from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skylark_bi.agents.monday_agent import (
    MondayIntegrationService,
)


def main():
    service = MondayIntegrationService()

    print("=" * 70)
    print("SKYLARK BI AGENT — MONDAY.COM DATA RETRIEVAL TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # DEALS
    # ---------------------------------------------------------

    print("\nDEALS")
    print("-" * 70)

    deals_board = service.reader.read_board(
        service.config.deals_board_id
    )

    print(f"Board      : {deals_board.board.name}")
    print(f"Board ID   : {deals_board.board.id}")
    print(f"Items read : {len(deals_board.items)}")

    if deals_board.items:
        print("\nSample records:")

        for item in deals_board.items[:5]:
            print(
                f"  {item.id} | {item.name}"
            )

    # ---------------------------------------------------------
    # WORK ORDERS
    # ---------------------------------------------------------

    print("\nWORK ORDERS")
    print("-" * 70)

    work_orders_board = service.reader.read_board(
        service.config.work_orders_board_id
    )

    print(
        f"Board      : "
        f"{work_orders_board.board.name}"
    )

    print(
        f"Board ID   : "
        f"{work_orders_board.board.id}"
    )

    print(
        f"Items read : "
        f"{len(work_orders_board.items)}"
    )

    if work_orders_board.items:
        print("\nSample records:")

        for item in work_orders_board.items[:5]:
            print(
                f"  {item.id} | {item.name}"
            )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("DATA RETRIEVAL SUCCESSFUL")
    print("=" * 70)

    print(
        f"Deals items retrieved       : "
        f"{len(deals_board.items)}"
    )

    print(
        f"Work Orders items retrieved : "
        f"{len(work_orders_board.items)}"
    )


if __name__ == "__main__":
    main()