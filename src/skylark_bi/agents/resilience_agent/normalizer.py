"""
Safe normalization utilities for canonical business data.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from dateutil import parser

from .schemas import NormalizedValue


DEFAULT_MISSING_TOKENS = {
    "",
    "na",
    "n/a",
    "nan",
    "none",
    "null",
}


def is_missing(
    value: Any,
    missing_tokens: set[str] | None = None,
    dash_is_missing: bool = False,
) -> bool:
    """Return True when a value is safely considered missing."""

    if value is None:
        return True

    tokens = set(
        missing_tokens
        or DEFAULT_MISSING_TOKENS
    )

    if dash_is_missing:
        tokens.update(
            {
                "-",
                "--",
            }
        )

    text = str(value).strip()

    return text.casefold() in tokens


def missing_kind(
    value: Any,
    missing_tokens: set[str] | None = None,
    dash_is_missing: bool = False,
) -> str | None:
    """Classify the kind of missing value, when present."""

    if value is None:
        return "null"

    text = str(value)

    if text == "":
        return "empty_string"

    if text.strip() == "":
        return "whitespace"

    if is_missing(
        value,
        missing_tokens,
        dash_is_missing,
    ):
        return "missing_token"

    return None


def normalize_text(
    value: Any,
    missing_tokens: set[str] | None = None,
    dash_is_missing: bool = False,
) -> NormalizedValue:
    """Trim and collapse whitespace in free text."""

    kind = missing_kind(
        value,
        missing_tokens,
        dash_is_missing,
    )

    if kind:
        return NormalizedValue(
            original=value,
            normalized=None,
            valid=True,
            issues=[kind],
            reason="value is missing",
        )

    normalized = re.sub(
        r"\s+",
        " ",
        str(value).strip(),
    )

    issues = []

    if normalized != str(value):
        issues.append(
            "normalized_whitespace"
        )

    return NormalizedValue(
        original=value,
        normalized=normalized,
        valid=True,
        issues=issues,
        reason=(
            "trimmed/collapsed whitespace"
            if issues
            else None
        ),
    )


def normalize_number(
    value: Any,
    missing_tokens: set[str] | None = None,
) -> NormalizedValue:
    """Parse common numeric formats without converting invalids to zero."""

    if missing_kind(
        value,
        missing_tokens,
    ):
        return NormalizedValue(
            original=value,
            normalized=None,
            valid=True,
            issues=["missing_value"],
            reason="value is missing",
        )

    if isinstance(
        value,
        bool,
    ):
        return _invalid(
            value,
            "invalid_number",
        )

    if isinstance(
        value,
        (int, float),
    ):
        return NormalizedValue(
            original=value,
            normalized=float(value),
            valid=True,
        )

    cleaned = (
        str(value)
        .strip()
        .replace(",", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("€", "")
    )

    try:
        number = float(cleaned)

    except ValueError:
        return _invalid(
            value,
            "invalid_number",
        )

    return NormalizedValue(
        original=value,
        normalized=number,
        valid=True,
    )


def normalize_date(
    value: Any,
    missing_tokens: set[str] | None = None,
) -> NormalizedValue:
    """Parse dates defensively and flag ambiguous string dates."""

    if missing_kind(
        value,
        missing_tokens,
    ):
        return NormalizedValue(
            original=value,
            normalized=None,
            valid=True,
            issues=["missing_value"],
            reason="value is missing",
        )

    if isinstance(
        value,
        datetime,
    ):
        return NormalizedValue(
            original=value,
            normalized=value.date(),
            valid=True,
        )

    if isinstance(
        value,
        date,
    ):
        return NormalizedValue(
            original=value,
            normalized=value,
            valid=True,
        )

    text = str(value).strip()

    if _is_ambiguous_date(text):
        return NormalizedValue(
            original=value,
            normalized=None,
            valid=False,
            issues=["ambiguous_date"],
            reason="date could be interpreted multiple ways",
        )

    try:
        parsed = parser.parse(
            text,
            dayfirst=_looks_day_first(text),
            fuzzy=False,
        )

    except (
        ValueError,
        TypeError,
        OverflowError,
    ):
        return _invalid(
            value,
            "invalid_date",
        )

    return NormalizedValue(
        original=value,
        normalized=parsed.date(),
        valid=True,
    )


def normalize_category(
    value: Any,
    allowed_values: set[str] | None = None,
    aliases: dict[str, str] | None = None,
    missing_tokens: set[str] | None = None,
) -> NormalizedValue:
    """
    Normalize category for comparison while preserving configured aliases.
    """

    normalized_text = normalize_text(
        value,
        missing_tokens,
    )

    if normalized_text.normalized is None:
        return normalized_text

    comparable = (
        normalized_text.normalized
        .casefold()
    )

    alias_map = {
        key.casefold(): target
        for key, target in (aliases or {}).items()
    }

    normalized = alias_map.get(
        comparable,
        comparable,
    )

    issues = list(
        normalized_text.issues
    )

    if (
        allowed_values is not None
        and normalized.casefold()
        not in {
            value.casefold()
            for value in allowed_values
        }
    ):
        issues.append(
            "unknown_category"
        )

        return NormalizedValue(
            original=value,
            normalized=normalized,
            valid=False,
            issues=issues,
            reason="category is not in allowed values",
        )

    return NormalizedValue(
        original=value,
        normalized=normalized,
        valid=True,
        issues=issues,
        reason=normalized_text.reason,
    )


def _invalid(
    value: Any,
    issue: str,
) -> NormalizedValue:

    return NormalizedValue(
        original=value,
        normalized=None,
        valid=False,
        issues=[issue],
        reason=issue,
    )


def _is_ambiguous_date(
    value: str,
) -> bool:

    match = re.fullmatch(
        r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})",
        value,
    )

    if not match:
        return False

    first = int(
        match.group(1)
    )
    second = int(
        match.group(2)
    )

    return first <= 12 and second <= 12


def _looks_day_first(
    value: str,
) -> bool:

    match = re.fullmatch(
        r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})",
        value,
    )

    if not match:
        return False

    return int(match.group(1)) > 12
