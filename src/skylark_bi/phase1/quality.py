"""
Data-quality analysis for Phase 1.

This module identifies missingness, duplicates, empty columns,
identifier candidates, and basic quality severity.

It does not modify the underlying dataset.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


# ---------------------------------------------------------------------
# Severity thresholds
# ---------------------------------------------------------------------

CRITICAL_MISSING_THRESHOLD = 80.0
WARNING_MISSING_THRESHOLD = 30.0


# ---------------------------------------------------------------------
# Missing-value analysis
# ---------------------------------------------------------------------

def analyze_missing_values(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """
    Analyze missing values for every column.
    """

    results = []

    total_rows = len(df)

    for column in df.columns:

        null_count = int(
            df[column].isna().sum()
        )

        null_percentage = (
            null_count / max(total_rows, 1)
        ) * 100

        if null_percentage >= CRITICAL_MISSING_THRESHOLD:
            severity = "critical"

        elif null_percentage >= WARNING_MISSING_THRESHOLD:
            severity = "warning"

        elif null_percentage > 0:
            severity = "low"

        else:
            severity = "none"

        results.append(
            {
                "column": column,
                "null_count": null_count,
                "null_percentage": round(
                    null_percentage,
                    2,
                ),
                "severity": severity,
            }
        )

    return sorted(
        results,
        key=lambda x: x["null_percentage"],
        reverse=True,
    )


# ---------------------------------------------------------------------
# Empty columns
# ---------------------------------------------------------------------

def find_empty_columns(
    df: pd.DataFrame,
) -> list[str]:
    """
    Find columns containing no usable values.
    """

    return [
        column
        for column in df.columns
        if df[column].isna().all()
    ]


# ---------------------------------------------------------------------
# Duplicate rows
# ---------------------------------------------------------------------

def analyze_duplicates(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Analyze exact duplicate rows.
    """

    duplicate_mask = df.duplicated(
        keep=False
    )

    duplicate_rows = int(
        duplicate_mask.sum()
    )

    duplicate_groups = int(
        df.duplicated().sum()
    )

    return {
        "duplicate_rows": duplicate_rows,
        "duplicate_groups": duplicate_groups,
        "duplicate_percentage": round(
            duplicate_rows
            / max(len(df), 1)
            * 100,
            2,
        ),
    }


# ---------------------------------------------------------------------
# Constant columns
# ---------------------------------------------------------------------

def find_constant_columns(
    df: pd.DataFrame,
) -> list[str]:
    """
    Find columns containing only one distinct value.
    """

    return [
        column
        for column in df.columns
        if df[column].nunique(
            dropna=False
        ) <= 1
    ]


# ---------------------------------------------------------------------
# Near-constant columns
# ---------------------------------------------------------------------

def find_near_constant_columns(
    df: pd.DataFrame,
    threshold: float = 0.95,
) -> list[dict[str, Any]]:
    """
    Find columns where one value dominates most records.
    """

    results = []

    for column in df.columns:

        value_counts = (
            df[column]
            .value_counts(
                dropna=False
            )
        )

        if value_counts.empty:
            continue

        dominant_value = value_counts.iloc[0]

        dominant_percentage = (
            dominant_value
            / len(df)
        )

        if dominant_percentage >= threshold:

            results.append(
                {
                    "column": column,
                    "dominant_percentage": round(
                        dominant_percentage
                        * 100,
                        2,
                    ),
                    "dominant_value": str(
                        value_counts.index[0]
                    ),
                }
            )

    return results


# ---------------------------------------------------------------------
# Identifier candidates
# ---------------------------------------------------------------------

def find_identifier_candidates(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """
    Identify columns that may act as identifiers.

    Heuristic:
    - Mostly non-null
    - High uniqueness
    """

    candidates = []

    for column in df.columns:

        series = df[column]

        non_null = series.dropna()

        if len(non_null) == 0:
            continue

        unique_ratio = (
            non_null.nunique()
            / len(non_null)
        )

        if unique_ratio >= 0.90:

            candidates.append(
                {
                    "column": column,
                    "unique_ratio": round(
                        unique_ratio,
                        4,
                    ),
                    "unique_count": int(
                        non_null.nunique()
                    ),
                    "non_null_count": int(
                        len(non_null)
                    ),
                }
            )

    return sorted(
        candidates,
        key=lambda x: x["unique_ratio"],
        reverse=True,
    )


# ---------------------------------------------------------------------
# Overall quality report
# ---------------------------------------------------------------------

def analyze_quality(
    df: pd.DataFrame,
    dataset_name: str,
) -> dict[str, Any]:
    """
    Generate the complete Phase 1 quality report.
    """

    missing_values = analyze_missing_values(
        df
    )

    empty_columns = find_empty_columns(
        df
    )

    duplicates = analyze_duplicates(
        df
    )

    constant_columns = find_constant_columns(
        df
    )

    near_constant_columns = (
        find_near_constant_columns(df)
    )

    identifier_candidates = (
        find_identifier_candidates(df)
    )

    critical_fields = [
        item
        for item in missing_values
        if item["severity"] == "critical"
    ]

    warning_fields = [
        item
        for item in missing_values
        if item["severity"] == "warning"
    ]

    return {
        "dataset": dataset_name,
        "record_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_values": missing_values,
        "empty_columns": empty_columns,
        "duplicates": duplicates,
        "constant_columns": constant_columns,
        "near_constant_columns": near_constant_columns,
        "identifier_candidates": identifier_candidates,
        "summary": {
            "critical_missing_fields": len(
                critical_fields
            ),
            "warning_missing_fields": len(
                warning_fields
            ),
            "empty_columns": len(
                empty_columns
            ),
            "duplicate_rows": duplicates[
                "duplicate_rows"
            ],
        },
    }