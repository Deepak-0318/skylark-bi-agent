"""
Dataset profiling utilities.

The profiler describes the structure and statistical characteristics
of the raw datasets without modifying the business data.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


DATE_KEYWORDS = (
    "date",
    "month",
    "year",
)

NUMERIC_KEYWORDS = (
    "amount",
    "value",
    "revenue",
    "probability",
    "quantity",
    "rate",
    "percentage",
)


def infer_column_type(series: pd.Series) -> str:
    """
    Infer the analytical type of a column.

    The goal is not to force a pandas dtype, but to identify how the
    column should be treated by later data-resilience and BI layers.
    """

    non_null = series.dropna()

    if len(non_null) == 0:
        return "empty"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    column_name = str(series.name).lower()

    # Date candidate detection
    if any(keyword in column_name for keyword in DATE_KEYWORDS):
        parsed = pd.to_datetime(
            non_null.astype(str),
            errors="coerce",
            format="mixed",
        )

        if parsed.notna().mean() >= 0.5:
            return "datetime_candidate"

    # Numeric candidate detection
    if any(keyword in column_name for keyword in NUMERIC_KEYWORDS):
        cleaned = (
            non_null.astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.strip()
        )

        numeric = pd.to_numeric(
            cleaned,
            errors="coerce",
        )

        if numeric.notna().mean() >= 0.5:
            return "numeric_candidate"

    unique_count = series.nunique(dropna=True)

    unique_ratio = unique_count / max(len(series), 1)

    if unique_count <= 30 or unique_ratio <= 0.10:
        return "categorical"

    return "text"


def get_sample_values(
    series: pd.Series,
    limit: int = 5,
) -> list[str | None]:
    """Return representative non-null sample values."""

    values = series.dropna().head(limit).tolist()

    result: list[str | None] = []

    for value in values:
        if pd.isna(value):
            result.append(None)
        else:
            result.append(str(value))

    return result


def get_numeric_statistics(
    series: pd.Series,
) -> dict[str, float]:
    """Return numeric statistics when the column is numeric."""

    numeric = pd.to_numeric(
        series,
        errors="coerce",
    ).dropna()

    if numeric.empty:
        return {}

    return {
        "min": float(numeric.min()),
        "max": float(numeric.max()),
        "mean": float(numeric.mean()),
        "median": float(numeric.median()),
    }


def profile_column(series: pd.Series) -> dict[str, Any]:
    """Create a profile for a single column."""

    null_count = int(series.isna().sum())
    total_count = int(len(series))

    profile: dict[str, Any] = {
        "name": str(series.name),
        "pandas_dtype": str(series.dtype),
        "inferred_type": infer_column_type(series),
        "record_count": total_count,
        "non_null_count": int(series.notna().sum()),
        "null_count": null_count,
        "null_percentage": round(
            (null_count / max(total_count, 1)) * 100,
            2,
        ),
        "unique_count": int(
            series.nunique(dropna=True)
        ),
        "sample_values": get_sample_values(series),
    }

    numeric_stats = get_numeric_statistics(series)

    if numeric_stats:
        profile["numeric_statistics"] = numeric_stats

    return profile


def profile_dataframe(
    df: pd.DataFrame,
    dataset_name: str,
) -> dict[str, Any]:
    """
    Generate a complete dataset profile.

    The returned dictionary is JSON serializable.
    """

    columns = [
        profile_column(df[column])
        for column in df.columns
    ]

    return {
        "dataset": dataset_name,
        "record_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": columns,
    }