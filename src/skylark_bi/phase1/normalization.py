"""
Data normalization utilities.

These functions provide deterministic normalization rules for
messy business data without inventing missing information.
"""

from __future__ import annotations

import re

import pandas as pd


NULL_LIKE_VALUES = {
    "",
    "null",
    "none",
    "nan",
    "n/a",
    "na",
    "not available",
    "-",
    "--",
}


def normalize_text(value: object) -> str | None:
    """Normalize free-text and categorical values."""

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.lower() in NULL_LIKE_VALUES:
        return None

    value = re.sub(r"\s+", " ", value)

    return value


def normalize_category(value: object) -> str | None:
    """Normalize categorical values while preserving readable casing."""

    value = normalize_text(value)

    if value is None:
        return None

    return value.title()


def normalize_identifier(value: object) -> str | None:
    """Normalize identifiers for matching."""

    value = normalize_text(value)

    if value is None:
        return None

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "",
        value,
    ).upper()


def normalize_numeric(value: object) -> float | None:
    """
    Convert common business numeric representations into floats.

    Handles commas, currency symbols, and percentage signs.
    Does not invent values.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.lower() in NULL_LIKE_VALUES:
        return None

    value = (
        value
        .replace(",", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("€", "")
        .strip()
    )

    percentage = value.endswith("%")

    if percentage:
        value = value[:-1].strip()

    try:
        number = float(value)
    except ValueError:
        return None

    if percentage:
        return number / 100

    return number


def normalize_date(value: object) -> pd.Timestamp | None:
    """Parse mixed date formats safely."""

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.lower() in NULL_LIKE_VALUES:
        return None

    parsed = pd.to_datetime(
        value,
        errors="coerce",
        format="mixed",
    )

    if pd.isna(parsed):
        return None

    return parsed


def normalize_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply conservative normalization to object columns.

    This function does not perform domain-specific mappings.
    """

    normalized = df.copy()

    for column in normalized.columns:

        if pd.api.types.is_object_dtype(
            normalized[column]
        ):
            normalized[column] = normalized[column].map(
                normalize_text
            )

    return normalized