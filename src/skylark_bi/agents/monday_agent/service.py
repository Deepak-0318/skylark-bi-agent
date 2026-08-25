"""
High-level Monday.com integration service.

This is the boundary exposed to future agents/orchestration logic.
"""

from __future__ import annotations

from typing import Any

from .board_reader import MondayBoardReader
from .client import MondayClient
from .config import MondayConfig
from .mapper import map_deal, map_work_order
from .reconciliation import (
    ReconciliationResult,
    reconcile_deals,
    reconcile_work_orders,
)
from .schemas import BoardData, MondayItem


class MondayIntegrationService:
    """
    Read-only Monday.com integration.

    Agent-facing capabilities:

    - discover_board
    - get_board_schema
    - read_board
    - read_all_items
    - read_deals
    - read_work_orders
    - reconcile_deals
    - reconcile_work_orders
    """

    def __init__(
        self,
        config: MondayConfig | None = None,
    ) -> None:

        self.config = (
            config
            or MondayConfig.from_environment()
        )

        self.client = MondayClient(
            self.config
        )

        self.reader = MondayBoardReader(
            self.client,
            self.config,
        )

    # ---------------------------------------------------------
    # TOOL 1 — BOARD DISCOVERY
    # ---------------------------------------------------------

    def discover_board(
        self,
        board_id: int,
    ) -> dict[str, Any]:

        board = self.reader.get_board_schema(
            board_id
        )

        return {
            "board_id": board.id,
            "board_name": board.name,
            "state": board.state,
            "permissions": board.permissions,
            "column_count": len(
                board.columns
            ),
            "columns": [
                {
                    "id": column.id,
                    "title": column.title,
                    "type": column.column_type,
                }
                for column in board.columns
            ],
        }

    # ---------------------------------------------------------
    # TOOL 2 — BOARD SCHEMA
    # ---------------------------------------------------------

    def get_board_schema(
        self,
        board_id: int,
    ):
        return self.reader.get_board_schema(
            board_id
        )

    # ---------------------------------------------------------
    # TOOL 3 — READ BOARD DATA
    # ---------------------------------------------------------

    def read_board(
        self,
        board_id: int,
    ) -> BoardData:
        return self.reader.read_board(
            board_id
        )

    def read_all_items(
        self,
        board_id: int,
    ) -> list[MondayItem]:
        return self.reader.read_all_items(
            board_id
        )

    def read_board_data(
        self,
        board_id: int,
    ) -> BoardData:
        return self.read_board(
            board_id
        )

    # ---------------------------------------------------------
    # CANONICAL DATA ACCESS
    # ---------------------------------------------------------

    def read_deals(self):

        if not self.config.deals_board_id:
            raise ValueError(
                "MONDAY_DEALS_BOARD_ID is not configured."
            )

        board_data = self.reader.read_board(
            self.config.deals_board_id
        )

        return [
            map_deal(
                item,
                board_data.board,
            )
            for item in board_data.items
        ]

    def read_work_orders(self):

        if not self.config.work_orders_board_id:
            raise ValueError(
                "MONDAY_WORK_ORDERS_BOARD_ID "
                "is not configured."
            )

        board_data = self.reader.read_board(
            self.config.work_orders_board_id
        )

        return [
            map_work_order(
                item,
                board_data.board,
            )
            for item in board_data.items
        ]

    def get_deals(self):
        return self.read_deals()

    def get_work_orders(self):
        return self.read_work_orders()

    def map_deal(
        self,
        item,
        board,
    ):
        return map_deal(
            item,
            board,
        )

    def map_work_order(
        self,
        item,
        board,
    ):
        return map_work_order(
            item,
            board,
        )

    def reconcile_deals(
        self,
        source_records,
        monday_records=None,
    ) -> ReconciliationResult:

        monday = (
            monday_records
            if monday_records is not None
            else self.read_deals()
        )

        return reconcile_deals(
            source_records,
            monday,
        )

    def reconcile_work_orders(
        self,
        source_records,
        monday_records=None,
    ) -> ReconciliationResult:

        monday = (
            monday_records
            if monday_records is not None
            else self.read_work_orders()
        )

        return reconcile_work_orders(
            source_records,
            monday,
        )
