from skylark_bi.agents.monday_agent.mapper import (
    map_deal,
    map_work_order,
)
from skylark_bi.agents.monday_agent.schemas import (
    MondayBoard,
    MondayColumn,
    MondayItem,
)


def test_map_deal():

    board = MondayBoard(
        id=123,
        name="Deals",
        state="active",
        permissions="everyone",
        columns=[
            MondayColumn(
                id="owner",
                title="Owner code",
                column_type="text",
            ),
            MondayColumn(
                id="sector",
                title="Sector/service",
                column_type="text",
            ),
            MondayColumn(
                id="stage",
                title="Deal Stage",
                column_type="text",
            ),
        ],
    )

    item = MondayItem(
        id="1",
        name="Test Deal",
        column_values={
            "owner": {
                "text": "OWNER_001"
            },
            "sector": {
                "text": "Mining"
            },
            "stage": {
                "text": "A. Lead Generated"
            },
        },
    )

    deal = map_deal(
        item,
        board,
    )

    assert deal.deal_name == "Test Deal"
    assert deal.owner_code == "OWNER_001"
    assert deal.sector == "Mining"
    assert deal.deal_stage == "A. Lead Generated"


def test_map_deal_full_canonical_fields():

    board = MondayBoard(
        id=123,
        name="Deals",
        state="active",
        permissions="everyone",
        columns=[
            MondayColumn("owner", "Owner code"),
            MondayColumn("client", "Client Code"),
            MondayColumn("status", "Deal Status"),
            MondayColumn("close", "Close Date"),
            MondayColumn("probability", "Closure Probability"),
            MondayColumn("value", "Deal Value"),
            MondayColumn("tentative", "Tentative Close Date"),
            MondayColumn("stage", "Deal Stage"),
            MondayColumn("product", "Product deal"),
            MondayColumn("sector", "Sector/service"),
            MondayColumn("created", "Created Date"),
        ],
    )

    item = MondayItem(
        id="1",
        name="Deal A",
        column_values={
            "owner": {"text": "OWNER_001"},
            "client": {"text": "CLIENT_001"},
            "status": {"text": "Won"},
            "close": {"text": "2026-01-15"},
            "probability": {"text": "High"},
            "value": {"text": "1,250.50"},
            "tentative": {"text": "bad-date"},
            "stage": {"text": "Proposal"},
            "product": {"text": "Survey"},
            "sector": {"text": "Mining"},
            "created": {"text": "2025-12-01"},
        },
    )

    deal = map_deal(
        item,
        board,
    )

    assert deal.id == "1"
    assert deal.deal_name == "Deal A"
    assert deal.client_code == "CLIENT_001"
    assert deal.close_date.isoformat() == "2026-01-15"
    assert deal.closure_probability == "High"
    assert deal.deal_value == 1250.50
    assert deal.tentative_close_date is None
    assert deal.product_deal == "Survey"
    assert deal.raw_values["Name"] == "Deal A"


def test_map_deal_handles_missing_values_and_columns():

    board = MondayBoard(
        id=123,
        name="Deals",
        state="active",
        permissions="everyone",
        columns=[
            MondayColumn("value", "Deal Value"),
            MondayColumn("created", "Created Date"),
        ],
    )

    item = MondayItem(
        id="1",
        name="  ",
        column_values={
            "value": {"text": "not-a-number"},
            "created": {"text": "not-a-date"},
        },
    )

    deal = map_deal(
        item,
        board,
    )

    assert deal.deal_name is None
    assert deal.owner_code is None
    assert deal.deal_value is None
    assert deal.created_date is None


def test_map_deal_closure_probability_is_categorical():

    board = MondayBoard(
        id=123,
        name="Deals",
        state="active",
        permissions="everyone",
        columns=[
            MondayColumn("probability", "Closure Probability"),
            MondayColumn("value", "Deal Value"),
        ],
    )

    for probability in (
        "High",
        "Medium",
        "Low",
    ):
        item = MondayItem(
            id="1",
            name="Deal A",
            column_values={
                "probability": {
                    "text": probability
                },
                "value": {
                    "text": "1,250.50"
                },
            },
        )

        deal = map_deal(
            item,
            board,
        )

        assert deal.closure_probability == probability
        assert deal.deal_value == 1250.50


def test_map_deal_missing_closure_probability_is_none():

    board = MondayBoard(
        id=123,
        name="Deals",
        state="active",
        permissions="everyone",
        columns=[
            MondayColumn("probability", "Closure Probability"),
            MondayColumn("value", "Deal Value"),
        ],
    )

    item = MondayItem(
        id="1",
        name="Deal A",
        column_values={
            "probability": {
                "text": ""
            },
            "value": {
                "text": "100"
            },
        },
    )

    deal = map_deal(
        item,
        board,
    )

    assert deal.closure_probability is None
    assert deal.deal_value == 100.0


def test_map_deal_name_falls_back_to_configured_column():

    board = MondayBoard(
        id=123,
        name="Deals",
        state="active",
        permissions="everyone",
        columns=[
            MondayColumn("deal_name", "Deal Name"),
        ],
    )

    item = MondayItem(
        id="1",
        name=" ",
        column_values={
            "deal_name": {
                "text": "Fallback Deal"
            },
        },
    )

    deal = map_deal(
        item,
        board,
    )

    assert deal.deal_name == "Fallback Deal"


def test_map_work_order_full_canonical_fields():

    board = MondayBoard(
        id=456,
        name="Work Orders",
        state="active",
        permissions="everyone",
        columns=[
            MondayColumn("customer", "Customer Name Code"),
            MondayColumn("serial", "Serial #"),
            MondayColumn("nature", "Nature of Work"),
            MondayColumn("executed", "Last executed month"),
            MondayColumn("status", "Execution Status"),
            MondayColumn("delivery", "Data Delivery Date"),
            MondayColumn("po", "PO/LOI Date"),
            MondayColumn("document", "Document Type"),
            MondayColumn("start", "Probable Start Date"),
            MondayColumn("end", "Probable End Date"),
            MondayColumn("bd", "BD/KAM Personnel code"),
            MondayColumn("sector", "Sector"),
            MondayColumn("type", "Type of Work"),
            MondayColumn("platform", "Software Platform in deliverables"),
            MondayColumn("invoice_date", "Last Invoice Date"),
            MondayColumn("invoice", "Latest Invoice Number"),
            MondayColumn("amount_excl", "Amount excl GST"),
            MondayColumn("amount_incl", "Amount incl GST"),
            MondayColumn("billed_excl", "Billed Value excl GST"),
            MondayColumn("billed_incl", "Billed Value incl GST"),
            MondayColumn("collected", "Collected Amount incl GST"),
            MondayColumn("to_bill_excl", "Amount to be Billed excl GST"),
            MondayColumn("to_bill_incl", "Amount to be Billed incl GST"),
            MondayColumn("receivable", "Amount Receivable"),
            MondayColumn("priority", "AR Priority Account"),
            MondayColumn("ops", "Quantity by Ops"),
            MondayColumn("po_qty", "Quantities as per PO"),
            MondayColumn("billed_qty", "Quantity Billed"),
            MondayColumn("balance", "Balance Quantity"),
            MondayColumn("invoice_status", "Invoice Status"),
            MondayColumn("expected", "Expected Billing Month"),
            MondayColumn("actual_bill", "Actual Billing Month"),
            MondayColumn("actual_collection", "Actual Collection Month"),
            MondayColumn("wo_billed", "WO Status - Billed"),
            MondayColumn("collection_status", "Collection Status"),
            MondayColumn("collection_date", "Collection Date"),
            MondayColumn("billing_status", "Billing Status"),
        ],
    )

    item = MondayItem(
        id="2",
        name="Deal A",
        column_values={
            "customer": {"text": "CUST_001"},
            "serial": {"text": "SN-001"},
            "nature": {"text": "Mapping"},
            "executed": {"text": "2026-02-01"},
            "status": {"text": "Completed"},
            "delivery": {"text": "2026-02-15"},
            "po": {"text": "2026-01-20"},
            "document": {"text": "PO"},
            "start": {"text": "2026-02-01"},
            "end": {"text": "2026-02-28"},
            "bd": {"text": "BD_001"},
            "sector": {"text": "Mining"},
            "type": {"text": "Survey"},
            "platform": {"text": "GIS"},
            "invoice_date": {"text": "2026-03-01"},
            "invoice": {"text": "INV-001"},
            "amount_excl": {"text": "100"},
            "amount_incl": {"text": "118"},
            "billed_excl": {"text": "90"},
            "billed_incl": {"text": "106.2"},
            "collected": {"text": "50"},
            "to_bill_excl": {"text": "10"},
            "to_bill_incl": {"text": "11.8"},
            "receivable": {"text": "56.2"},
            "priority": {"text": "High"},
            "ops": {"text": "5"},
            "po_qty": {"text": "6"},
            "billed_qty": {"text": "4"},
            "balance": {"text": "2"},
            "invoice_status": {"text": "Partial"},
            "expected": {"text": "2026-03-01"},
            "actual_bill": {"text": "2026-03-01"},
            "actual_collection": {"text": "2026-04-01"},
            "wo_billed": {"text": "Billed"},
            "collection_status": {"text": "Partial"},
            "collection_date": {"text": "2026-04-10"},
            "billing_status": {"text": "Open"},
        },
    )

    work_order = map_work_order(
        item,
        board,
    )

    assert work_order.id == "2"
    assert work_order.deal_name == "Deal A"
    assert work_order.customer_name_code == "CUST_001"
    assert work_order.serial_number == "SN-001"
    assert work_order.last_executed_month.isoformat() == "2026-02-01"
    assert work_order.amount_excl_gst == 100.0
    assert work_order.amount_incl_gst == 118.0
    assert work_order.quantities_as_per_po == 6.0
    assert work_order.billing_status == "Open"


def test_map_work_order_handles_malformed_values():

    board = MondayBoard(
        id=456,
        name="Work Orders",
        state="active",
        permissions="everyone",
        columns=[
            MondayColumn("amount", "Amount excl GST"),
            MondayColumn("delivery", "Data Delivery Date"),
        ],
    )

    item = MondayItem(
        id="2",
        name="Work Order",
        column_values={
            "amount": {"text": "bad-number"},
            "delivery": {"text": "bad-date"},
        },
    )

    work_order = map_work_order(
        item,
        board,
    )

    assert work_order.deal_name == "Work Order"
    assert work_order.amount_excl_gst is None
    assert work_order.data_delivery_date is None
