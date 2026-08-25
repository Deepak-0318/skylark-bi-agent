import pandas as pd

from skylark_bi.phase1.profiler import profile_dataframe


def test_profile_dataframe():
    df = pd.DataFrame(
        {
            "Name": ["A", "B", None],
            "Amount": [100, 200, 300],
        }
    )

    profile = profile_dataframe(
        df,
        "Test",
    )

    assert profile["record_count"] == 3
    assert profile["column_count"] == 2
    assert len(profile["columns"]) == 2