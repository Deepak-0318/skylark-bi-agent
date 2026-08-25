"""
Read-only board discovery and item retrieval.
"""

from __future__ import annotations

from typing import Any

from .client import MondayClient
from .config import MondayConfig
from .errors import MondayBoardNotFoundError
from .schemas import (
    BoardData,
    BoardPage,
    MondayBoard,
    MondayColumn,
    MondayItem,
)


BOARD_QUERY = """
query GetBoard($board_id: ID!) {
  boards(ids: [$board_id]) {
    id
    name
    state
    permissions
    columns {
      id
      title
      type
      settings_str
    }
  }
}
"""


ITEMS_QUERY = """
query GetBoardItems(
  $board_id: ID!
  $limit: Int!
) {
  boards(ids: [$board_id]) {
    items_page(limit: $limit) {
      cursor
      items {
        id
        name
        url
        created_at
        updated_at
        column_values {
          id
          text
          value
          type
        }
      }
    }
  }
}
"""


NEXT_ITEMS_QUERY = """
query GetNextItems(
  $cursor: String!
  $limit: Int!
) {
  next_items_page(
    cursor: $cursor
    limit: $limit
  ) {
    cursor
    items {
      id
      name
      url
      created_at
      updated_at
      column_values {
        id
        text
        value
        type
      }
    }
  }
}
"""


class MondayBoardReader:
    """Read-only board operations."""

    def __init__(
        self,
        client: MondayClient,
        config: MondayConfig,
    ) -> None:

        self.client = client
        self.config = config

    def get_board_schema(
        self,
        board_id: int,
    ) -> MondayBoard:

        data = self.client.execute(
            BOARD_QUERY,
            {
                "board_id": board_id,
            },
        )

        boards = data.get(
            "boards",
            [],
        )

        if not boards:
            raise MondayBoardNotFoundError(
                f"Board {board_id} was not found."
            )

        raw = boards[0]

        columns = [
            MondayColumn(
                id=column["id"],
                title=column["title"],
                column_type=column.get(
                    "type"
                ),
                settings=self._parse_settings(
                    column.get(
                        "settings_str"
                    )
                ),
            )
            for column in raw.get(
                "columns",
                [],
            )
        ]

        return MondayBoard(
            id=int(raw["id"]),
            name=raw["name"],
            state=raw.get("state"),
            permissions=raw.get(
                "permissions"
            ),
            columns=columns,
        )

    def read_page(
        self,
        board_id: int,
        cursor: str | None = None,
    ) -> BoardPage:

        if cursor is None:

            data = self.client.execute(
                ITEMS_QUERY,
                {
                    "board_id": board_id,
                    "limit": self.config.page_size,
                },
            )

            board_data = (
                data.get("boards") or []
            )

            if not board_data:
                raise MondayBoardNotFoundError(
                    f"Board {board_id} was not found."
                )

            page = board_data[0].get(
                "items_page",
                {},
            )

        else:

            data = self.client.execute(
                NEXT_ITEMS_QUERY,
                {
                    "cursor": cursor,
                    "limit": self.config.page_size,
                },
            )

            page = data.get(
                "next_items_page",
                {},
            )

        items = [
            self._parse_item(item)
            for item in page.get(
                "items",
                [],
            )
        ]

        return BoardPage(
            items=items,
            cursor=page.get(
                "cursor"
            ),
        )

    def read_all_items(
        self,
        board_id: int,
    ) -> list[MondayItem]:

        items: list[MondayItem] = []

        cursor: str | None = None

        while True:

            page = self.read_page(
                board_id=board_id,
                cursor=cursor,
            )

            items.extend(
                page.items
            )

            if not page.cursor:
                break

            cursor = page.cursor

        return items

    def read_board(
        self,
        board_id: int,
    ) -> BoardData:

        board = self.get_board_schema(
            board_id
        )

        items = self.read_all_items(
            board_id
        )

        return BoardData(
            board=board,
            items=items,
        )

    @staticmethod
    def _parse_item(
        item: dict[str, Any],
    ) -> MondayItem:

        column_values = {}

        for column in item.get(
            "column_values",
            [],
        ):

            column_values[
                column["id"]
            ] = {
                "text": column.get(
                    "text"
                ),
                "value": column.get(
                    "value"
                ),
                "type": column.get(
                    "type"
                ),
            }

        return MondayItem(
            id=str(item["id"]),
            name=item.get(
                "name",
                "",
            ),
            column_values=column_values,
            created_at=item.get(
                "created_at"
            ),
            updated_at=item.get(
                "updated_at"
            ),
            url=item.get(
                "url"
            ),
        )

    @staticmethod
    def _parse_settings(
        value: str | None,
    ) -> dict[str, Any] | None:

        if not value:
            return None

        import json

        try:
            parsed = json.loads(value)

            if isinstance(
                parsed,
                dict,
            ):
                return parsed

        except json.JSONDecodeError:
            pass

        return None