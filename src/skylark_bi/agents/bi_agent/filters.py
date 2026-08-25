from datetime import date, datetime
from typing import Any


FIELD_ALIASES = {
    "status": (
        "status",
        "deal_status",
        "execution_status",
    ),
    "customer": (
        "customer_name_code",
        "customer_code",
    ),
    "client": (
        "client_code",
        "customer_name_code",
        "customer_code",
    ),
    "owner": (
        "owner_code",
        "bd_kam_personnel_code",
    ),
}


def _get_value(
    record: Any,
    field: str,
):
    """
    Read a field from either a canonical model or dict.
    """

    if isinstance(record, dict):
        return record.get(field)

    return getattr(
        record,
        field,
        None,
    )


def _normalized_text(value: Any) -> str:
    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .casefold()
        .split()
    )


def _matches(
    actual: Any,
    expected: Any,
) -> bool:

    if actual is None:
        return False

    # Exact numeric comparison
    if isinstance(actual, (int, float)) and isinstance(
        expected,
        (int, float),
    ):
        return actual == expected

    # Date comparison
    if isinstance(actual, (date, datetime)):
        return _normalized_text(
            actual.isoformat()
        ) == _normalized_text(
            expected
        )

    actual_text = _normalized_text(
        actual
    )

    expected_text = _normalized_text(
        expected
    )

    return actual_text == expected_text


def _candidate_fields(
    field: str,
    record: Any,
) -> tuple[str, ...]:

    if field in FIELD_ALIASES:
        aliases = FIELD_ALIASES[field]

        existing = tuple(
            alias
            for alias in aliases
            if (
                isinstance(record, dict)
                and alias in record
            )
            or (
                not isinstance(record, dict)
                and hasattr(record, alias)
            )
        )

        if existing:
            return existing

        return aliases

    return (field,)


def _record_matches_filter(
    record: Any,
    field: str,
    expected: Any,
) -> bool:

    # ---------------------------------------------------------
    # Special semantic aliases
    # ---------------------------------------------------------

    for candidate in _candidate_fields(
        field,
        record,
    ):
        actual = _get_value(
            record,
            candidate,
        )

        if _matches(
            actual,
            expected,
        ):
            return True

    # ---------------------------------------------------------
    # Deal/customer name fallback
    #
    # This allows an LLM-generated entity such as:
    # {"deal_name": "Sakura"}
    # to work against Deal.deal_name.
    # ---------------------------------------------------------

    if field in {
        "deal_name",
        "customer_name_code",
        "customer_code",
        "client_code",
    }:
        for candidate in (
            "deal_name",
            "customer_name_code",
            "customer_code",
            "client_code",
        ):
            actual = _get_value(
                record,
                candidate,
            )

            if _matches(
                actual,
                expected,
            ):
                return True

    return False


def apply_filters(
    records,
    filters: dict,
):
    """
    Apply semantic filters to canonical records.

    Unknown temporal filters are intentionally skipped here because
    date/period logic is handled by the BI aggregation layer.
    """

    result = list(records)

    for field, expected in filters.items():

        if field in {
            "relative_period",
            "quarter",
        }:
            continue

        filtered = [
            record
            for record in result
            if _record_matches_filter(
                record,
                field,
                expected,
            )
        ]

        result = filtered

    return result