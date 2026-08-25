from skylark_bi.agents.monday_agent.service import (
    MondayIntegrationService,
)
from skylark_bi.agents.monday_agent.schemas import (
    BoardData,
    MondayBoard,
    MondayColumn,
    MondayItem,
)


class FakeConfig:
    deals_board_id = 100
    work_orders_board_id = 200


class FakeReader:

    def __init__(self):
        self.calls = []

        self.deals_board = MondayBoard(
            id=100,
            name="Deals",
            state="active",
            permissions="everyone",
            columns=[
                MondayColumn("owner", "Owner code"),
            ],
        )

        self.work_orders_board = MondayBoard(
            id=200,
            name="Work Orders",
            state="active",
            permissions="everyone",
            columns=[
                MondayColumn("customer", "Customer Name Code"),
                MondayColumn("serial", "Serial #"),
                MondayColumn("nature", "Nature of Work"),
            ],
        )

    def get_board_schema(
        self,
        board_id,
    ):
        self.calls.append(
            ("schema", board_id)
        )

        if board_id == 100:
            return self.deals_board

        return self.work_orders_board

    def read_all_items(
        self,
        board_id,
    ):
        self.calls.append(
            ("items", board_id)
        )

        return self.read_board(
            board_id
        ).items

    def read_board(
        self,
        board_id,
    ):
        self.calls.append(
            ("board", board_id)
        )

        if board_id == 100:
            return BoardData(
                board=self.deals_board,
                items=[
                    MondayItem(
                        id="1",
                        name="Deal A",
                        column_values={
                            "owner": {
                                "text": "OWN"
                            }
                        },
                    )
                ],
            )

        return BoardData(
            board=self.work_orders_board,
            items=[
                MondayItem(
                    id="2",
                    name="Deal A",
                    column_values={
                        "customer": {
                            "text": "CUST"
                        },
                        "serial": {
                            "text": "SN-1"
                        },
                        "nature": {
                            "text": "Mapping"
                        },
                    },
                )
            ],
        )


def make_service():

    service = MondayIntegrationService.__new__(
        MondayIntegrationService
    )

    service.config = FakeConfig()
    service.reader = FakeReader()
    service.client = None

    return service


def test_service_exposes_read_only_behavior():

    service = make_service()

    assert not hasattr(
        service,
        "create_item",
    )
    assert not hasattr(
        service,
        "update_item",
    )
    assert not hasattr(
        service,
        "delete_item",
    )
    assert not hasattr(
        service,
        "create_board",
    )
    assert not hasattr(
        service,
        "update_board",
    )
    assert not hasattr(
        service,
        "delete_board",
    )


def test_service_reads_deals_and_work_orders():

    service = make_service()

    deals = service.read_deals()
    work_orders = service.read_work_orders()

    assert deals[0].deal_name == "Deal A"
    assert deals[0].owner_code == "OWN"
    assert work_orders[0].deal_name == "Deal A"
    assert work_orders[0].serial_number == "SN-1"


def test_service_mapping_helpers():

    service = make_service()
    board_data = service.read_board(
        100
    )

    deal = service.map_deal(
        board_data.items[0],
        board_data.board,
    )

    assert deal.deal_name == "Deal A"


def test_service_reconciliation_helpers():

    service = make_service()

    deals_result = service.reconcile_deals(
        [
            {
                "Deal Name": "Deal A",
                "Owner code": "OWN",
            }
        ]
    )

    work_orders_result = service.reconcile_work_orders(
        [
            {
                "Deal name masked": "Deal A",
                "Customer Name Code": "CUST",
                "Serial #": "SN-1",
                "Nature of Work": "Mapping",
            }
        ]
    )

    assert deals_result.matched_count == 1
    assert work_orders_result.matched_count == 1
