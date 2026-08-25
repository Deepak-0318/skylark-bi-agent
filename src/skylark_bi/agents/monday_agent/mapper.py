"""
Mapping between Monday board records and canonical business models.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from dateutil import parser

from skylark_bi.core.models import Deal, WorkOrder

from .schemas import BoardData, MondayBoard, MondayItem


ColumnMapping = dict[str, str | tuple[str, ...] | list[str]]


DEAL_COLUMN_MAPPING: ColumnMapping = {
    "deal_name": ("Name", "Deal Name"),
    "owner_code": ("Owner code",),
    "client_code": ("Client Code",),
    "deal_status": ("Deal Status",),
    "close_date": ("Close Date (A)", "Close Date"),
    "closure_probability": ("Closure Probability",),
    "deal_value": ("Masked Deal value", "Deal Value"),
    "tentative_close_date": ("Tentative Close Date",),
    "deal_stage": ("Deal Stage",),
    "product_deal": ("Product deal",),
    "sector": ("Sector/service", "Sector"),
    "created_date": ("Created Date",),
}


WORK_ORDER_COLUMN_MAPPING: ColumnMapping = {
    "deal_name": ("Name", "Deal name masked", "Deal Name"),
    "customer_name_code": ("Customer Name Code",),
    "serial_number": ("Serial #", "Serial Number"),
    "nature_of_work": ("Nature of Work",),
    "last_executed_month": (
        "Last executed month of recurring project",
        "Last executed month",
    ),
    "execution_status": ("Execution Status",),
    "data_delivery_date": ("Data Delivery Date",),
    "po_loi_date": (
        "Date of PO/LOI",
        "PO/LOI Date",
        "PO LOI Date",
    ),
    "document_type": ("Document Type",),
    "probable_start_date": ("Probable Start Date",),
    "probable_end_date": ("Probable End Date",),
    "bd_kam_personnel_code": ("BD/KAM Personnel code",),
    "sector": ("Sector", "Sector/service"),
    "type_of_work": ("Type of Work",),
    "software_platform_in_deliverables": (
        "Is any Skylark software platform part of the client deliverables in this deal?",
        "Software Platform in deliverables",
    ),
    "last_invoice_date": (
        "Last invoice date",
        "Last Invoice Date",
    ),
    "latest_invoice_number": (
        "latest invoice no.",
        "Latest Invoice Number",
    ),
    "amount_excl_gst": (
        "Amountin Rupees (Excl of GST) (Masked)",
        "Amount in Rupees (Excl of GST) (Masked)",
        "Amount excl GST",
    ),
    "amount_incl_gst": (
        "Amount in Rupees (Incl of GST) (Masked)",
        "Amount incl GST",
    ),
    "billed_value_excl_gst": (
        "Billed Value in Rupees (Excl of GST.) (Masked)",
        "Billed Value excl GST",
    ),
    "billed_value_incl_gst": (
        "Billed Value in Rupees (Incl of GST.) (Masked)",
        "Billed Value incl GST",
    ),
    "collected_amount_incl_gst": (
        "Collected Amount in Rupees (Incl of GST.) (Masked)",
        "Collected Amount incl GST",
    ),
    "amount_to_be_billed_excl_gst": (
        "Amount to be billed in Rs. (Exl. of GST) (Masked)",
        "Amount to be Billed excl GST",
    ),
    "amount_to_be_billed_incl_gst": (
        "Amount to be billed in Rs. (Incl. of GST) (Masked)",
        "Amount to be Billed incl GST",
    ),
    "amount_receivable": (
        "Amount Receivable (Masked)",
        "Amount Receivable",
    ),
    "ar_priority_account": ("AR Priority account", "AR Priority Account"),
    "quantity_by_ops": ("Quantity by Ops",),
    "quantities_as_per_po": ("Quantities as per PO",),
    "quantity_billed": (
        "Quantity billed (till date)",
        "Quantity Billed",
    ),
    "balance_quantity": (
        "Balance in quantity",
        "Balance Quantity",
    ),
    "invoice_status": ("Invoice Status",),
    "expected_billing_month": ("Expected Billing Month",),
    "actual_billing_month": ("Actual Billing Month",),
    "actual_collection_month": ("Actual Collection Month",),
    "wo_status_billed": (
        "WO Status (billed)",
        "WO Status - Billed",
    ),
    "collection_status": ("Collection status", "Collection Status"),
    "collection_date": ("Collection Date",),
    "billing_status": ("Billing Status",),
}


DEAL_DATE_FIELDS = {
    "close_date",
    "tentative_close_date",
    "created_date",
}

WORK_ORDER_DATE_FIELDS = {
    "last_executed_month",
    "data_delivery_date",
    "po_loi_date",
    "probable_start_date",
    "probable_end_date",
    "last_invoice_date",
    "expected_billing_month",
    "actual_billing_month",
    "actual_collection_month",
    "collection_date",
}

DEAL_NUMERIC_FIELDS = {
    "deal_value",
}

WORK_ORDER_NUMERIC_FIELDS = {
    "amount_excl_gst",
    "amount_incl_gst",
    "billed_value_excl_gst",
    "billed_value_incl_gst",
    "collected_amount_incl_gst",
    "amount_to_be_billed_excl_gst",
    "amount_to_be_billed_incl_gst",
    "amount_receivable",
    "quantity_by_ops",
    "quantities_as_per_po",
    "quantity_billed",
    "balance_quantity",
}


def _board_schema(board: MondayBoard | BoardData) -> MondayBoard:
    """Accept either MondayBoard or BoardData."""
    if isinstance(board, BoardData):
        return board.board
    return board


def build_column_map(
    board: MondayBoard | BoardData,
) -> dict[str, str]:
    """Map normalized Monday column titles to column IDs."""

    schema = _board_schema(board)

    return {
        _normalize_column_name(column.title): column.id
        for column in schema.columns
    }


def optional_string(value: Any) -> str | None:
    """Return a trimmed string or None for missing/empty values."""

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    if text.casefold() in {"nan", "none", "null"}:
        return None

    return text


def optional_number(value: Any) -> float | None:
    """Defensively parse a numeric value from Monday text."""

    text = optional_string(value)

    if text is None:
        return None

    cleaned = (
        text.replace(",", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("%", "")
        .strip()
    )

    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def optional_date(value: Any) -> date | None:
    """Defensively parse a date-like value."""

    text = optional_string(value)

    if text is None:
        return None

    try:
        return parser.parse(
            text,
            fuzzy=False,
            dayfirst=False,
        ).date()
    except (ValueError, TypeError, OverflowError):
        return None


def column_lookup(
    item: MondayItem,
    board: MondayBoard | BoardData,
    column_names: str | tuple[str, ...] | list[str],
) -> Any:
    """Look up a Monday value by column title."""

    names = _as_names(column_names)

    for name in names:
        if _normalize_column_name(name) == "name":
            value = optional_string(item.name)
            if value is not None:
                return value

    columns = build_column_map(board)

    for name in names:
        column_id = columns.get(
            _normalize_column_name(name)
        )

        if not column_id:
            continue

        value = item.column_values.get(
            column_id
        )

        if not value:
            continue

        text = value.get("text")

        if text not in (None, ""):
            return text

        raw = value.get("value")

        if raw not in (None, ""):
            return raw

    return None


def map_deal(
    item: MondayItem,
    board: MondayBoard | BoardData,
    column_mapping: ColumnMapping | None = None,
) -> Deal:
    """Map a Monday item into a canonical Deal."""

    mapping = {
        **DEAL_COLUMN_MAPPING,
        **(column_mapping or {}),
    }

    values = _mapped_values(
        item,
        board,
        mapping,
        DEAL_DATE_FIELDS,
        DEAL_NUMERIC_FIELDS,
    )

    return Deal(
        id=item.id,
        raw_values=_raw_values(item, board),
        **values,
    )


def map_work_order(
    item: MondayItem,
    board: MondayBoard | BoardData,
    column_mapping: ColumnMapping | None = None,
) -> WorkOrder:
    """Map a Monday item into a canonical WorkOrder."""

    mapping = {
        **WORK_ORDER_COLUMN_MAPPING,
        **(column_mapping or {}),
    }

    values = _mapped_values(
        item,
        board,
        mapping,
        WORK_ORDER_DATE_FIELDS,
        WORK_ORDER_NUMERIC_FIELDS,
    )

    return WorkOrder(
        id=item.id,
        raw_values=_raw_values(item, board),
        **values,
    )


def _mapped_values(
    item: MondayItem,
    board: MondayBoard | BoardData,
    mapping: ColumnMapping,
    date_fields: set[str],
    numeric_fields: set[str],
) -> dict[str, Any]:

    values: dict[str, Any] = {}

    for field_name, column_names in mapping.items():
        value = column_lookup(
            item,
            board,
            column_names,
        )

        if field_name in date_fields:
            values[field_name] = optional_date(value)
        elif field_name in numeric_fields:
            values[field_name] = optional_number(value)
        else:
            values[field_name] = optional_string(value)

    return values


def _raw_values(
    item: MondayItem,
    board: MondayBoard | BoardData,
) -> dict[str, Any]:

    schema = _board_schema(board)

    raw = {
        "Name": item.name,
    }

    for column in schema.columns:
        value = item.column_values.get(
            column.id,
            {},
        )

        raw[column.title] = value.get("text")

    return raw


def _as_names(
    column_names: str | tuple[str, ...] | list[str],
) -> tuple[str, ...]:

    if isinstance(column_names, str):
        return (column_names,)

    return tuple(column_names)


def _normalize_column_name(value: str) -> str:
    return " ".join(
        value.strip().casefold().split()
    )