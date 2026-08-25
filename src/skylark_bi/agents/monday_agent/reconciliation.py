"""
Record-level reconciliation between source records and Monday records.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Iterable


DEAL_FINGERPRINT_FIELDS = (
    "deal_name",
    "owner_code",
    "client_code",
    "deal_status",
    "created_date",
)


WORK_ORDER_FINGERPRINT_FIELDS = (
    "deal_name",
    "customer_name_code",
    "serial_number",
    "nature_of_work",
)


FIELD_ALIASES = {
    "deal_name": (
        "deal_name",
        "Deal Name",
        "Deal name masked",
        "Name",
        "name",
    ),
    "owner_code": (
        "owner_code",
        "Owner code",
    ),
    "client_code": (
        "client_code",
        "Client Code",
    ),
    "deal_status": (
        "deal_status",
        "Deal Status",
    ),
    "created_date": (
        "created_date",
        "Created Date",
    ),
    "customer_name_code": (
        "customer_name_code",
        "customer_code",
        "Customer Name Code",
    ),
    "serial_number": (
        "serial_number",
        "Serial #",
        "Serial Number",
    ),
    "nature_of_work": (
        "nature_of_work",
        "Nature of Work",
    ),
}


@dataclass(frozen=True)
class ReconciliationRecord:
    """Structured representation of a reconciled record."""

    fingerprint: tuple[str, ...]
    record: dict[str, Any]
    count: int = 1
    reason: str | None = None


@dataclass(frozen=True)
class ReconciliationResult:
    """Summary and record-level details for reconciliation."""

    source_count: int
    monday_count: int
    matched_count: int
    missing_from_monday: list[ReconciliationRecord]
    monday_only: list[ReconciliationRecord]
    duplicate_source_records: list[ReconciliationRecord]
    incomplete_source_records: list[ReconciliationRecord]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation."""

        return {
            "source_count": self.source_count,
            "monday_count": self.monday_count,
            "matched_count": self.matched_count,
            "missing_from_monday": [
                _record_to_dict(record)
                for record in self.missing_from_monday
            ],
            "monday_only": [
                _record_to_dict(record)
                for record in self.monday_only
            ],
            "duplicate_source_records": [
                _record_to_dict(record)
                for record in self.duplicate_source_records
            ],
            "incomplete_source_records": [
                _record_to_dict(record)
                for record in self.incomplete_source_records
            ],
        }


def reconcile_deals(
    source_records: Iterable[Any],
    monday_records: Iterable[Any],
) -> ReconciliationResult:
    """Reconcile Deals using a deterministic multi-field fingerprint."""

    return reconcile_records(
        source_records,
        monday_records,
        DEAL_FINGERPRINT_FIELDS,
        required_fields=("deal_name",),
    )


def reconcile_work_orders(
    source_records: Iterable[Any],
    monday_records: Iterable[Any],
) -> ReconciliationResult:
    """Reconcile Work Orders using a deterministic multi-field fingerprint."""

    return reconcile_records(
        source_records,
        monday_records,
        WORK_ORDER_FINGERPRINT_FIELDS,
        required_fields=("deal_name",),
    )


def reconcile_records(
    source_records: Iterable[Any],
    monday_records: Iterable[Any],
    fingerprint_fields: tuple[str, ...],
    required_fields: tuple[str, ...],
) -> ReconciliationResult:
    """Reconcile two record collections without mutating either side."""

    source = list(source_records)
    monday = list(monday_records)

    source_index = _build_index(
        source,
        fingerprint_fields,
        required_fields,
        include_incomplete=True,
    )

    monday_index = _build_index(
        monday,
        fingerprint_fields,
        required_fields,
        include_incomplete=False,
    )

    source_counts = {
        fingerprint: len(records)
        for fingerprint, records in source_index[
            "complete"
        ].items()
    }

    monday_counts = {
        fingerprint: len(records)
        for fingerprint, records in monday_index[
            "complete"
        ].items()
    }

    matched_count = sum(
        min(
            source_counts[fingerprint],
            monday_counts.get(
                fingerprint,
                0,
            ),
        )
        for fingerprint in source_counts
    )

    missing_from_monday = [
        ReconciliationRecord(
            fingerprint=fingerprint,
            record=source_index["complete"][fingerprint][0],
            count=source_counts[fingerprint],
            reason="not_found_in_monday",
        )
        for fingerprint in sorted(source_counts)
        if monday_counts.get(
            fingerprint,
            0,
        ) == 0
    ]

    monday_only = [
        ReconciliationRecord(
            fingerprint=fingerprint,
            record=monday_index["complete"][fingerprint][0],
            count=monday_counts[fingerprint],
            reason="not_found_in_source",
        )
        for fingerprint in sorted(monday_counts)
        if source_counts.get(
            fingerprint,
            0,
        ) == 0
    ]

    duplicate_source_records = [
        ReconciliationRecord(
            fingerprint=fingerprint,
            record=records[0],
            count=len(records),
            reason="duplicate_source_fingerprint",
        )
        for fingerprint, records in sorted(
            source_index["complete"].items()
        )
        if len(records) > 1
    ]

    return ReconciliationResult(
        source_count=len(source),
        monday_count=len(monday),
        matched_count=matched_count,
        missing_from_monday=missing_from_monday,
        monday_only=monday_only,
        duplicate_source_records=duplicate_source_records,
        incomplete_source_records=source_index[
            "incomplete"
        ],
    )


def build_fingerprint(
    record: Any,
    fields: tuple[str, ...],
) -> tuple[str, ...]:
    """Build a normalized comparison fingerprint."""

    return tuple(
        _normalize_value(
            _get_value(
                record,
                field,
            )
        )
        for field in fields
    )


def _build_index(
    records: list[Any],
    fingerprint_fields: tuple[str, ...],
    required_fields: tuple[str, ...],
    include_incomplete: bool,
) -> dict[str, Any]:

    complete: dict[
        tuple[str, ...],
        list[dict[str, Any]],
    ] = defaultdict(list)

    incomplete: list[ReconciliationRecord] = []

    for record in records:

        missing_required = [
            field
            for field in required_fields
            if not _normalize_value(
                _get_value(
                    record,
                    field,
                )
            )
        ]

        fingerprint = build_fingerprint(
            record,
            fingerprint_fields,
        )

        plain_record = _to_record_dict(
            record
        )

        if missing_required:

            if include_incomplete:
                incomplete.append(
                    ReconciliationRecord(
                        fingerprint=fingerprint,
                        record=plain_record,
                        reason=(
                            "missing_required_fields:"
                            + ",".join(missing_required)
                        ),
                    )
                )

            continue

        complete[fingerprint].append(
            plain_record
        )

    return {
        "complete": complete,
        "incomplete": incomplete,
    }


def _get_value(
    record: Any,
    field: str,
) -> Any:

    for alias in FIELD_ALIASES.get(
        field,
        (field,),
    ):

        if isinstance(
            record,
            dict,
        ):
            if alias in record:
                return record[alias]

            continue

        if hasattr(
            record,
            alias,
        ):
            return getattr(
                record,
                alias,
            )

    return None


def _normalize_value(
    value: Any,
) -> str:

    if value is None:
        return ""

    if isinstance(
        value,
        datetime,
    ):
        value = value.date()

    if isinstance(
        value,
        date,
    ):
        return value.isoformat()

    text = str(value).strip()

    if text.casefold() in {
        "nan",
        "none",
        "null",
    }:
        return ""

    return " ".join(
        text.casefold().split()
    )


def _to_record_dict(
    record: Any,
) -> dict[str, Any]:

    if isinstance(
        record,
        dict,
    ):
        return dict(record)

    if hasattr(
        record,
        "__dataclass_fields__",
    ):
        return asdict(record)

    return {
        "value": record,
    }


def _record_to_dict(
    record: ReconciliationRecord,
) -> dict[str, Any]:

    return {
        "fingerprint": list(record.fingerprint),
        "record": record.record,
        "count": record.count,
        "reason": record.reason,
    }
