"""
Validation rules for canonical business records.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any

from .impact import (
    get_business_impact,
    recommended_action_for,
)
from .normalizer import (
    missing_kind,
    normalize_category,
    normalize_date,
    normalize_number,
    normalize_text,
)
from .quality import make_issue, quality_label, score_record
from .schemas import (
    DataQualityIssue,
    FieldSpec,
    NormalizedValue,
    RecordQualityReport,
    FilteredRecords,
)


DEAL_SCHEMA = {
    "id": FieldSpec("id", "text"),
    "deal_name": FieldSpec(
        "deal_name",
        "text",
        required=True,
    ),
    "owner_code": FieldSpec("owner_code", "text"),
    "client_code": FieldSpec("client_code", "text"),
    "deal_status": FieldSpec("deal_status", "categorical"),
    "close_date": FieldSpec("close_date", "date"),
    "closure_probability": FieldSpec(
        "closure_probability",
        "categorical",
        allowed_values={
            "high",
            "medium",
            "low",
        },
    ),
    "deal_value": FieldSpec("deal_value", "numeric"),
    "tentative_close_date": FieldSpec(
        "tentative_close_date",
        "date",
    ),
    "deal_stage": FieldSpec("deal_stage", "categorical"),
    "product_deal": FieldSpec("product_deal", "categorical"),
    "sector": FieldSpec("sector", "categorical"),
    "created_date": FieldSpec("created_date", "date"),
}


WORK_ORDER_SCHEMA = {
    "id": FieldSpec("id", "text"),
    "deal_name": FieldSpec(
        "deal_name",
        "text",
        required=True,
    ),
    "customer_name_code": FieldSpec("customer_name_code", "text"),
    "serial_number": FieldSpec("serial_number", "text"),
    "nature_of_work": FieldSpec("nature_of_work", "categorical"),
    "last_executed_month": FieldSpec(
        "last_executed_month",
        "date",
    ),
    "execution_status": FieldSpec(
        "execution_status",
        "categorical",
    ),
    "data_delivery_date": FieldSpec("data_delivery_date", "date"),
    "po_loi_date": FieldSpec("po_loi_date", "date"),
    "document_type": FieldSpec("document_type", "categorical"),
    "probable_start_date": FieldSpec("probable_start_date", "date"),
    "probable_end_date": FieldSpec("probable_end_date", "date"),
    "bd_kam_personnel_code": FieldSpec(
        "bd_kam_personnel_code",
        "text",
    ),
    "sector": FieldSpec("sector", "categorical"),
    "type_of_work": FieldSpec("type_of_work", "categorical"),
    "software_platform_in_deliverables": FieldSpec(
        "software_platform_in_deliverables",
        "categorical",
    ),
    "last_invoice_date": FieldSpec("last_invoice_date", "date"),
    "latest_invoice_number": FieldSpec(
        "latest_invoice_number",
        "text",
    ),
    "amount_excl_gst": FieldSpec("amount_excl_gst", "numeric"),
    "amount_incl_gst": FieldSpec("amount_incl_gst", "numeric"),
    "billed_value_excl_gst": FieldSpec(
        "billed_value_excl_gst",
        "numeric",
    ),
    "billed_value_incl_gst": FieldSpec(
        "billed_value_incl_gst",
        "numeric",
    ),
    "collected_amount_incl_gst": FieldSpec(
        "collected_amount_incl_gst",
        "numeric",
    ),
    "amount_to_be_billed_excl_gst": FieldSpec(
        "amount_to_be_billed_excl_gst",
        "numeric",
    ),
    "amount_to_be_billed_incl_gst": FieldSpec(
        "amount_to_be_billed_incl_gst",
        "numeric",
    ),
    "amount_receivable": FieldSpec(
        "amount_receivable",
        "numeric",
    ),
    "ar_priority_account": FieldSpec(
        "ar_priority_account",
        "categorical",
    ),
    "quantity_by_ops": FieldSpec("quantity_by_ops", "numeric"),
    "quantities_as_per_po": FieldSpec(
        "quantities_as_per_po",
        "numeric",
    ),
    "quantity_billed": FieldSpec("quantity_billed", "numeric"),
    "balance_quantity": FieldSpec("balance_quantity", "numeric"),
    "invoice_status": FieldSpec("invoice_status", "categorical"),
    "expected_billing_month": FieldSpec(
        "expected_billing_month",
        "date",
    ),
    "actual_billing_month": FieldSpec(
        "actual_billing_month",
        "date",
    ),
    "actual_collection_month": FieldSpec(
        "actual_collection_month",
        "date",
    ),
    "wo_status_billed": FieldSpec(
        "wo_status_billed",
        "categorical",
    ),
    "collection_status": FieldSpec(
        "collection_status",
        "categorical",
    ),
    "collection_date": FieldSpec("collection_date", "date"),
    "billing_status": FieldSpec("billing_status", "categorical"),
}


DATASET_SCHEMAS = {
    "deals": DEAL_SCHEMA,
    "work_orders": WORK_ORDER_SCHEMA,
}


def get_schema(
    dataset: str,
) -> dict[str, FieldSpec]:
    """Return the configured schema for a dataset."""

    try:
        return DATASET_SCHEMAS[
            dataset
        ]

    except KeyError as exc:
        raise ValueError(
            f"Unsupported dataset: {dataset}"
        ) from exc


def validate_record(
    dataset: str,
    record: Any,
    schema: dict[str, FieldSpec] | None = None,
) -> RecordQualityReport:
    """Validate one canonical record."""

    active_schema = schema or get_schema(
        dataset
    )

    record_id = _record_id(
        record
    )

    issues: list[DataQualityIssue] = []
    normalized_values: dict[
        str,
        NormalizedValue,
    ] = {}

    for field_name, spec in active_schema.items():

        value = _get_raw_or_field_value(
            record,
            field_name,
            dataset,
        )

        normalized = normalize_value(
            value,
            spec,
        )

        normalized_values[
            field_name
        ] = normalized

        kind = missing_kind(
            value,
            spec.missing_tokens,
            spec.dash_is_missing,
        )

        if kind:
            severity = (
                "critical"
                if spec.required
                else "warning"
            )

            issues.append(
                _issue(
                    dataset,
                    record_id,
                    field_name,
                    "missing_value",
                    severity,
                    value,
                    normalized.normalized,
                )
            )

            continue

        if not normalized.valid:
            issue_type = (
                normalized.issues[0]
                if normalized.issues
                else "invalid_value"
            )

            severity = (
                "warning"
                if issue_type == "unknown_category"
                else "critical"
            )

            issues.append(
                _issue(
                    dataset,
                    record_id,
                    field_name,
                    issue_type,
                    severity,
                    value,
                    normalized.normalized,
                )
            )

        elif "normalized_whitespace" in normalized.issues:
            issues.append(
                _issue(
                    dataset,
                    record_id,
                    field_name,
                    "normalized_whitespace",
                    "info",
                    value,
                    normalized.normalized,
                )
            )

    score = score_record(
        issues
    )

    return RecordQualityReport(
        dataset=dataset,
        record_id=record_id,
        issues=issues,
        normalized_values=normalized_values,
        quality_score=score,
        quality_label=quality_label(
            score
        ),
    )


def normalize_value(
    value: Any,
    spec: FieldSpec,
) -> NormalizedValue:
    """Normalize a value according to the field spec."""

    if spec.expected_type == "numeric":
        return normalize_number(
            value,
            spec.missing_tokens,
        )

    if spec.expected_type == "date":
        return normalize_date(
            value,
            spec.missing_tokens,
        )

    if spec.expected_type == "categorical":
        return normalize_category(
            value,
            allowed_values=spec.allowed_values,
            missing_tokens=spec.missing_tokens,
        )

    return normalize_text(
        value,
        spec.missing_tokens,
        spec.dash_is_missing,
    )


def validate_dataset_name(
    dataset: str,
) -> None:
    """Raise a controlled error for unsupported datasets."""

    get_schema(
        dataset
    )


def _issue(
    dataset: str,
    record_id: str | None,
    field_name: str,
    issue_type: str,
    severity: str,
    original_value: Any,
    normalized_value: Any = None,
) -> DataQualityIssue:

    impact = get_business_impact(
        field_name,
        "missing_value"
        if issue_type == "missing_value"
        else issue_type,
    )

    msg = f"Field '{field_name}' in dataset '{dataset}' has issue '{issue_type}' (original value: {repr(original_value)})"

    return make_issue(
        dataset=dataset,
        record_id=record_id,
        field=field_name,
        issue_type=issue_type,
        severity=severity,
        original_value=original_value,
        normalized_value=normalized_value,
        message=msg,
        recommended_action=recommended_action_for(
            field_name,
            issue_type,
        ),
        business_impact=(
            impact.impact
            if impact
            else None
        ),
        impact=(
            impact.impact
            if impact
            else None
        ),
    )


def _get_field(
    record: Any,
    field_name: str,
) -> Any:

    if isinstance(
        record,
        dict,
    ):
        return record.get(
            field_name
        )

    if hasattr(
        record,
        field_name,
    ):
        return getattr(
            record,
            field_name,
        )

    return None


def _record_id(
    record: Any,
) -> str | None:

    value = _get_field(
        record,
        "id",
    )

    if value is None:
        return None

    return str(value)


def record_to_dict(
    record: Any,
) -> dict[str, Any]:
    """Return public fields from a canonical record or dict."""

    if isinstance(
        record,
        dict,
    ):
        return dict(record)

    if is_dataclass(record):
        return {
            field.name: getattr(
                record,
                field.name,
            )
            for field in fields(record)
        }

    raise ValueError(
        "Malformed record: expected dataclass or dict."
    )


DEAL_COLUMN_MAPPING = {
    "deal_name": ("Name", "Deal Name"),
    "owner_code": ("Owner code",),
    "client_code": ("Client Code",),
    "deal_status": ("Deal Status",),
    "close_date": ("Close Date",),
    "closure_probability": ("Closure Probability",),
    "deal_value": ("Deal Value",),
    "tentative_close_date": ("Tentative Close Date",),
    "deal_stage": ("Deal Stage",),
    "product_deal": ("Product deal",),
    "sector": ("Sector/service", "Sector"),
    "created_date": ("Created Date",),
}


WORK_ORDER_COLUMN_MAPPING = {
    "deal_name": ("Name", "Deal name masked", "Deal Name"),
    "customer_name_code": ("Customer Name Code",),
    "serial_number": ("Serial #", "Serial Number"),
    "nature_of_work": ("Nature of Work",),
    "last_executed_month": ("Last executed month",),
    "execution_status": ("Execution Status",),
    "data_delivery_date": ("Data Delivery Date",),
    "po_loi_date": ("PO/LOI Date", "PO LOI Date"),
    "document_type": ("Document Type",),
    "probable_start_date": ("Probable Start Date",),
    "probable_end_date": ("Probable End Date",),
    "bd_kam_personnel_code": ("BD/KAM Personnel code",),
    "sector": ("Sector", "Sector/service"),
    "type_of_work": ("Type of Work",),
    "software_platform_in_deliverables": (
        "Software Platform in deliverables",
    ),
    "last_invoice_date": ("Last Invoice Date",),
    "latest_invoice_number": ("Latest Invoice Number",),
    "amount_excl_gst": ("Amount excl GST",),
    "amount_incl_gst": ("Amount incl GST",),
    "billed_value_excl_gst": ("Billed Value excl GST",),
    "billed_value_incl_gst": ("Billed Value incl GST",),
    "collected_amount_incl_gst": ("Collected Amount incl GST",),
    "amount_to_be_billed_excl_gst": (
        "Amount to be Billed excl GST",
    ),
    "amount_to_be_billed_incl_gst": (
        "Amount to be Billed incl GST",
    ),
    "amount_receivable": ("Amount Receivable",),
    "ar_priority_account": ("AR Priority Account",),
    "quantity_by_ops": ("Quantity by Ops",),
    "quantities_as_per_po": ("Quantities as per PO",),
    "quantity_billed": ("Quantity Billed",),
    "balance_quantity": ("Balance Quantity",),
    "invoice_status": ("Invoice Status",),
    "expected_billing_month": ("Expected Billing Month",),
    "actual_billing_month": ("Actual Billing Month",),
    "actual_collection_month": ("Actual Collection Month",),
    "wo_status_billed": ("WO Status - Billed",),
    "collection_status": ("Collection Status",),
    "collection_date": ("Collection Date",),
    "billing_status": ("Billing Status",),
}


def _get_raw_or_field_value(record: Any, field_name: str, dataset: str) -> Any:
    """Extract raw value from raw_values if available, otherwise get attribute."""
    raw_vals = None
    if isinstance(record, dict) and "raw_values" in record:
        raw_vals = record["raw_values"]
    elif hasattr(record, "raw_values"):
        raw_vals = getattr(record, "raw_values")

    if isinstance(raw_vals, dict):
        mapping = DEAL_COLUMN_MAPPING if dataset == "deals" else WORK_ORDER_COLUMN_MAPPING
        if field_name in mapping:
            possible_keys = mapping[field_name]
            for pk in possible_keys:
                if pk in raw_vals:
                    return raw_vals[pk]
    return _get_field(record, field_name)


def retain_valid_records(
    records: list[Any],
    dataset: str,
) -> FilteredRecords:
    """Return a view of records with no critical quality issues."""
    return exclude_critical_records(records, dataset)


def exclude_critical_records(
    records: list[Any],
    dataset: str,
) -> FilteredRecords:
    """Return a view of records excluding those with critical issues."""
    kept = []
    excluded = []
    reports = []
    for r in records:
        report = validate_record(dataset, r)
        reports.append(report)
        has_critical = any(issue.severity == "critical" for issue in report.issues)
        if not has_critical:
            kept.append(r)
        else:
            excluded.append(r)
    return FilteredRecords(records=kept, excluded_records=excluded, record_reports=reports)


def filter_by_quality_score(
    records: list[Any],
    dataset: str,
    min_score: float,
) -> FilteredRecords:
    """Filter records by a minimum quality score."""
    kept = []
    excluded = []
    reports = []
    for r in records:
        report = validate_record(dataset, r)
        reports.append(report)
        if report.quality_score >= min_score:
            kept.append(r)
        else:
            excluded.append(r)
    return FilteredRecords(records=kept, excluded_records=excluded, record_reports=reports)
