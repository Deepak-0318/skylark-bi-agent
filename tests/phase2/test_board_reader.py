from skylark_bi.agents.monday_agent.board_reader import (
    MondayBoardReader,
)


class FakeClient:

    def __init__(self):
        self.calls = []

    def execute(
        self,
        query,
        variables,
    ):

        self.calls.append(
            variables
        )

        if len(self.calls) == 1:

            return {
                "boards": [
                    {
                        "items_page": {
                            "cursor": "cursor-1",
                            "items": [
                                {
                                    "id": "1",
                                    "name": "Deal A",
                                    "column_values": [],
                                }
                            ],
                        }
                    }
                ]
            }

        return {
            "next_items_page": {
                "cursor": None,
                "items": [
                    {
                        "id": "2",
                        "name": "Deal B",
                        "column_values": [],
                    }
                ],
            }
        }


class FakeConfig:
    page_size = 500


def test_read_all_items():

    client = FakeClient()

    reader = MondayBoardReader(
        client,
        FakeConfig(),
    )

    items = reader.read_all_items(
        123
    )

    assert len(items) == 2
    assert items[0].name == "Deal A"
    assert items[1].name == "Deal B"
    assert len(client.calls) == 2