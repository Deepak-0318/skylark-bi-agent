from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "Deal funnel Data.xlsx - Deal tracker.csv"
)


def main() -> None:
    df = pd.read_csv(FILE_PATH)

    duplicate_mask = df.duplicated(
        keep=False
    )

    duplicates = df.loc[
        duplicate_mask
    ].copy()

    print("=" * 100)
    print("DEALS — DUPLICATE INVESTIGATION")
    print("=" * 100)

    print(
        f"\nTotal records: {len(df)}"
    )

    print(
        f"Rows involved in duplicate groups: "
        f"{len(duplicates)}"
    )

    print(
        f"Duplicate copies beyond first occurrence: "
        f"{df.duplicated().sum()}"
    )

    print("\nDUPLICATE RECORDS")
    print("-" * 100)

    with pd.option_context(
        "display.max_columns",
        None,
        "display.width",
        250,
        "display.max_colwidth",
        40,
    ):
        print(
            duplicates.to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()