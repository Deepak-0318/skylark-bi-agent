import pandas as pd

from skylark_bi.phase1.relationships import (
    analyze_column_pair,
)


def test_relationship_overlap():
    left = pd.DataFrame(
        {
            "Deal": [
                "Alpha",
                "Beta",
                "Gamma",
            ]
        }
    )

    right = pd.DataFrame(
        {
            "DealMasked": [
                "alpha",
                "delta",
            ]
        }
    )

    result = analyze_column_pair(
        left,
        right,
        "Deal",
        "DealMasked",
    )

    assert result["overlap_count"] == 1
    assert result["confidence"] == "medium"