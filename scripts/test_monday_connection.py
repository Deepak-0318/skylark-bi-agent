from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT / "src"),
)


from skylark_bi.agents.monday_agent import (
    MondayIntegrationService,
)


def main():

    service = MondayIntegrationService()

    print("=" * 70)
    print("SKYLARK BI AGENT — MONDAY.COM CONNECTION TEST")
    print("=" * 70)

    print("\nDEALS BOARD")
    print("-" * 70)

    deals = service.discover_board(
        service.config.deals_board_id
    )

    print(
        f"Board ID   : {deals['board_id']}"
    )

    print(
        f"Board Name : {deals['board_name']}"
    )

    print(
        f"Columns    : {deals['column_count']}"
    )

    for column in deals["columns"]:
        print(
            f"  - {column['title']} "
            f"[{column['type']}]"
        )

    print("\nWORK ORDERS BOARD")
    print("-" * 70)

    work_orders = service.discover_board(
        service.config.work_orders_board_id
    )

    print(
        f"Board ID   : {work_orders['board_id']}"
    )

    print(
        f"Board Name : {work_orders['board_name']}"
    )

    print(
        f"Columns    : {work_orders['column_count']}"
    )

    for column in work_orders["columns"]:
        print(
            f"  - {column['title']} "
            f"[{column['type']}]"
        )

    print("\n" + "=" * 70)
    print("MONDAY.COM CONNECTION SUCCESSFUL")
    print("=" * 70)


if __name__ == "__main__":
    main()