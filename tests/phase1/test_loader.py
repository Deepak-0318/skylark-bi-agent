from pathlib import Path

from skylark_bi.phase1.loader import load_dataset


ROOT = Path(__file__).resolve().parents[2]

RAW = ROOT / "data" / "raw"


def test_deals_load():
    path = RAW / "Deal funnel Data.xlsx - Deal tracker.csv"

    df = load_dataset(
        path,
        dataset_name="Deals",
    )

    assert len(df) == 346
    assert "Deal Name" in df.columns
    assert "Sector/service" in df.columns


def test_work_orders_load():
    path = RAW / "Work_Order_Tracker Data.xlsx - work order tracker.csv"

    df = load_dataset(
        path,
        dataset_name="Work Orders",
    )

    assert len(df) == 176
    assert "Serial #" in df.columns
    assert "Sector" in df.columns