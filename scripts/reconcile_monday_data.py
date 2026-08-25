from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skylark_bi.agents.monday_agent import (  # noqa: E402
    MondayIntegrationService,
)


DEALS_CSV = (
    ROOT
    / "data/raw/Deal funnel Data.xlsx - Deal tracker.csv"
)

WORK_ORDERS_CSV = (
    ROOT
    / "data/raw/Work_Order_Tracker Data.xlsx - work order tracker.csv"
)


def main():

    service = MondayIntegrationService()

    # ---------------------------------------------------------
    # SOURCE DATA
    # ---------------------------------------------------------

    deals_source = pd.read_csv(DEALS_CSV)
    work_orders_source = pd.read_csv(
        WORK_ORDERS_CSV
    )

    # ---------------------------------------------------------
    # MONDAY DATA
    # ---------------------------------------------------------

    deals_reconciliation = service.reconcile_deals(
        deals_source.to_dict(
            orient="records"
        )
    )

    work_orders_reconciliation = (
        service.reconcile_work_orders(
            work_orders_source.to_dict(
                orient="records"
            )
        )
    )

    # ---------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------

    print("=" * 70)
    print("SKYLARK BI AGENT — MONDAY DATA RECONCILIATION")
    print("=" * 70)

    _print_result(
        "DEALS",
        deals_reconciliation,
    )

    _print_result(
        "WORK ORDERS",
        work_orders_reconciliation,
    )

    print("\n" + "=" * 70)
    print("RECONCILIATION COMPLETE")
    print("=" * 70)


def _print_result(
    title,
    result,
):

    print(f"\n{title}")
    print("-" * 70)

    print(
        f"Source records        : "
        f"{result.source_count}"
    )

    print(
        f"Monday records        : "
        f"{result.monday_count}"
    )

    print(
        f"Matched records       : "
        f"{result.matched_count}"
    )

    print(
        f"Missing from Monday   : "
        f"{len(result.missing_from_monday)}"
    )

    print(
        f"Monday only           : "
        f"{len(result.monday_only)}"
    )

    print(
        f"Duplicate source keys : "
        f"{len(result.duplicate_source_records)}"
    )

    print(
        f"Incomplete source rows: "
        f"{len(result.incomplete_source_records)}"
    )

    if result.incomplete_source_records:
        print("\nIncomplete source records:")

        for record in result.incomplete_source_records:
            print(
                f"  - {record.reason} | "
                f"{record.record}"
            )

    if result.missing_from_monday:
        print("\nMissing from Monday:")

        for record in result.missing_from_monday:
            print(
                f"  - count={record.count} | "
                f"{record.record}"
            )

    if result.monday_only:
        print("\nMonday-only records:")

        for record in result.monday_only:
            print(
                f"  - count={record.count} | "
                f"{record.record}"
            )

    if result.duplicate_source_records:
        print("\nDuplicate source fingerprints:")

        for record in result.duplicate_source_records:
            print(
                f"  - count={record.count} | "
                f"{record.record}"
            )


if __name__ == "__main__":
    main()
