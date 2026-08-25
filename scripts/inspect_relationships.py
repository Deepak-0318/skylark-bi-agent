from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW = PROJECT_ROOT / "data" / "raw"

DEALS_FILE = (
    RAW
    / "Deal funnel Data.xlsx - Deal tracker.csv"
)

WORK_ORDERS_FILE = (
    RAW
    / "Work_Order_Tracker Data.xlsx - work order tracker.csv"
)


def normalize(value):
    if pd.isna(value):
        return None

    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "")
    )


def analyze_pair(
    deals,
    work_orders,
    deal_column,
    work_order_column,
):
    left = (
        deals[deal_column]
        .dropna()
        .map(normalize)
    )

    right = (
        work_orders[work_order_column]
        .dropna()
        .map(normalize)
    )

    left_values = set(left)
    right_values = set(right)

    overlap = left_values & right_values

    print(
        f"\n{deal_column}"
        f"  ↔  "
        f"{work_order_column}"
    )

    print("-" * 80)

    print(
        f"Deals unique values       : "
        f"{len(left_values)}"
    )

    print(
        f"Work Order unique values  : "
        f"{len(right_values)}"
    )

    print(
        f"Exact normalized overlap  : "
        f"{len(overlap)}"
    )

    if overlap:
        print("\nSample matches:")

        for value in sorted(
            overlap
        )[:20]:
            print(
                f"  {value}"
            )


def main():
    deals = pd.read_csv(
        DEALS_FILE
    )

    work_orders = pd.read_csv(
        WORK_ORDERS_FILE
    )

    print("=" * 100)
    print("SKYLARK — CROSS-BOARD RELATIONSHIP ANALYSIS")
    print("=" * 100)

    analyze_pair(
        deals,
        work_orders,
        "Deal Name",
        "Deal name masked",
    )

    analyze_pair(
        deals,
        work_orders,
        "Client Code",
        "Customer Name Code",
    )

    analyze_pair(
        deals,
        work_orders,
        "Owner code",
        "BD/KAM Personnel code",
    )

    analyze_pair(
        deals,
        work_orders,
        "Sector/service",
        "Sector",
    )


if __name__ == "__main__":
    main()