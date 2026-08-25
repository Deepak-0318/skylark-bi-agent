import pandas as pd

from skylark_bi.phase1.quality import analyze_quality


def test_empty_column_detection():
    df = pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": [None, None, None],
        }
    )

    result = analyze_quality(
        df,
        "Test",
    )

    assert "B" in result["empty_columns"]


def test_duplicate_detection():
    df = pd.DataFrame(
        {
            "A": [1, 1, 2],
        }
    )

    result = analyze_quality(
        df,
        "Test",
    )

    assert result["duplicates"]["duplicate_rows"] == 2