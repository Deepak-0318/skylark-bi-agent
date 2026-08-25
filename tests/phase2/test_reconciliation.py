from skylark_bi.agents.monday_agent.reconciliation import (
    reconcile_deals,
    reconcile_work_orders,
)
from skylark_bi.core.models import Deal, WorkOrder


def test_reconcile_deals_exact_match():

    source = [
        {
            "Deal Name": "Deal A",
            "Owner code": "OWN",
            "Client Code": "CLIENT",
            "Deal Status": "Won",
            "Created Date": "2026-01-01",
        }
    ]

    monday = [
        Deal(
            deal_name="Deal A",
            owner_code="OWN",
            client_code="CLIENT",
            deal_status="Won",
            created_date="2026-01-01",
        )
    ]

    result = reconcile_deals(
        source,
        monday,
    )

    assert result.source_count == 1
    assert result.monday_count == 1
    assert result.matched_count == 1
    assert result.missing_from_monday == []
    assert result.monday_only == []


def test_reconcile_deals_normalizes_case_and_whitespace():

    source = [
        {
            "Deal Name": "  Deal   A ",
            "Owner code": "OWN",
            "Client Code": "CLIENT",
            "Deal Status": "Won",
            "Created Date": "2026-01-01",
        }
    ]

    monday = [
        Deal(
            deal_name="deal a",
            owner_code="own",
            client_code="client",
            deal_status="won",
            created_date="2026-01-01",
        )
    ]

    result = reconcile_deals(
        source,
        monday,
    )

    assert result.matched_count == 1


def test_reconcile_deals_duplicate_names_use_full_fingerprint():

    source = [
        {
            "Deal Name": "Deal A",
            "Owner code": "OWN-1",
            "Client Code": "CLIENT",
            "Deal Status": "Won",
            "Created Date": "2026-01-01",
        },
        {
            "Deal Name": "Deal A",
            "Owner code": "OWN-2",
            "Client Code": "CLIENT",
            "Deal Status": "Won",
            "Created Date": "2026-01-01",
        },
    ]

    monday = [
        Deal(
            deal_name="Deal A",
            owner_code="OWN-1",
            client_code="CLIENT",
            deal_status="Won",
            created_date="2026-01-01",
        )
    ]

    result = reconcile_deals(
        source,
        monday,
    )

    assert result.matched_count == 1
    assert len(result.missing_from_monday) == 1
    assert (
        result.missing_from_monday[0].record["Owner code"]
        == "OWN-2"
    )


def test_reconcile_deals_detects_duplicate_source_records():

    source = [
        {
            "Deal Name": "Deal A",
            "Owner code": "OWN",
            "Client Code": "CLIENT",
            "Deal Status": "Won",
            "Created Date": "2026-01-01",
        },
        {
            "Deal Name": "deal a",
            "Owner code": "own",
            "Client Code": "client",
            "Deal Status": "won",
            "Created Date": "2026-01-01",
        },
    ]

    result = reconcile_deals(
        source,
        [],
    )

    assert len(result.duplicate_source_records) == 1
    assert result.duplicate_source_records[0].count == 2


def test_reconcile_deals_classifies_source_and_monday_only():

    source = [
        {
            "Deal Name": "Source Only",
            "Owner code": "OWN",
            "Client Code": "CLIENT",
            "Deal Status": "Open",
            "Created Date": "2026-01-01",
        }
    ]

    monday = [
        Deal(
            deal_name="Monday Only",
            owner_code="OWN",
            client_code="CLIENT",
            deal_status="Open",
            created_date="2026-01-01",
        )
    ]

    result = reconcile_deals(
        source,
        monday,
    )

    assert result.matched_count == 0
    assert len(result.missing_from_monday) == 1
    assert len(result.monday_only) == 1


def test_reconcile_deals_blank_name_is_incomplete():

    source = [
        {
            "Deal Name": " ",
            "Owner code": "OWN",
        }
    ]

    result = reconcile_deals(
        source,
        [],
    )

    assert result.matched_count == 0
    assert result.missing_from_monday == []
    assert len(result.incomplete_source_records) == 1
    assert (
        result.incomplete_source_records[0].reason
        == "missing_required_fields:deal_name"
    )


def test_reconcile_work_orders_uses_work_order_fingerprint():

    source = [
        {
            "Deal name masked": "Deal A",
            "Customer Name Code": "CUST",
            "Serial #": "001",
            "Nature of Work": "Mapping",
        }
    ]

    monday = [
        WorkOrder(
            deal_name=" deal a ",
            customer_name_code="cust",
            serial_number="001",
            nature_of_work="mapping",
        )
    ]

    result = reconcile_work_orders(
        source,
        monday,
    )

    assert result.matched_count == 1


def test_reconcile_zero_records():

    result = reconcile_deals(
        [],
        [],
    )

    assert result.source_count == 0
    assert result.monday_count == 0
    assert result.matched_count == 0
    assert result.missing_from_monday == []
    assert result.monday_only == []
