"""
Cross-board relationship analysis.

This module identifies candidate relationships between the Deals
and Work Orders datasets.

Relationships are evidence-based. A detected overlap does not
automatically imply a production foreign-key relationship.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def normalize_for_matching(value: object) -> str | None:
    """Normalize a value for conservative relationship matching."""

    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    if not value:
        return None

    # Remove whitespace differences.
    value = "".join(value.split())

    return value


def analyze_column_pair(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_column: str,
    right_column: str,
) -> dict[str, Any]:
    """Analyze overlap between two candidate relationship columns."""

    left_values = {
        value
        for value in left[left_column]
        .map(normalize_for_matching)
        .dropna()
    }

    right_values = {
        value
        for value in right[right_column]
        .map(normalize_for_matching)
        .dropna()
    }

    overlap = left_values & right_values

    right_coverage = (
        len(overlap) / max(len(right_values), 1)
    ) * 100

    left_coverage = (
        len(overlap) / max(len(left_values), 1)
    ) * 100

    union = left_values | right_values

    jaccard = (
        len(overlap) / max(len(union), 1)
    )

    if right_coverage >= 80:
        confidence = "high"
        recommendation = "Suitable candidate for cross-board matching."

    elif right_coverage >= 30:
        confidence = "medium"
        recommendation = "Use with additional validation."

    elif overlap:
        confidence = "low"
        recommendation = "Limited overlap; avoid relying on this relationship alone."

    else:
        confidence = "none"
        recommendation = "Do not use as a cross-board join key."

    return {
        "left_column": left_column,
        "right_column": right_column,
        "left_unique_values": len(left_values),
        "right_unique_values": len(right_values),
        "overlap_count": len(overlap),
        "left_coverage_percentage": round(left_coverage, 2),
        "right_coverage_percentage": round(right_coverage, 2),
        "jaccard_similarity": round(jaccard, 4),
        "confidence": confidence,
        "recommendation": recommendation,
        "sample_matches": sorted(overlap)[:10],
    }


def analyze_relationships(
    deals: pd.DataFrame,
    work_orders: pd.DataFrame,
) -> dict[str, Any]:
    """Analyze known candidate relationships between the two boards."""

    candidates = [
        (
            "Deal Name",
            "Deal name masked",
            "candidate_key",
        ),
        (
            "Client Code",
            "Customer Name Code",
            "candidate_key",
        ),
        (
            "Owner code",
            "BD/KAM Personnel code",
            "candidate_dimension",
        ),
        (
            "Sector/service",
            "Sector",
            "analytical_dimension",
        ),
    ]

    relationships = []

    for left_column, right_column, relationship_type in candidates:

        if (
            left_column not in deals.columns
            or right_column not in work_orders.columns
        ):
            continue

        result = analyze_column_pair(
            deals,
            work_orders,
            left_column,
            right_column,
        )

        result["relationship_type"] = relationship_type

        relationships.append(result)

    return {
        "source_datasets": [
            "Deals",
            "Work Orders",
        ],
        "relationships": relationships,
    }