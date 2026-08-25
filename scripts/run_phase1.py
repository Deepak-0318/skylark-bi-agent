"""
Complete Phase 1 pipeline.

Pipeline:

Raw Data
    ↓
Loader
    ↓
Profiler
    ↓
Quality Analysis
    ↓
Relationship Analysis
    ↓
Metric Catalog
    ↓
Generated Reports
"""

from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))


from skylark_bi.phase1.loader import load_dataset
from skylark_bi.phase1.profiler import profile_dataframe
from skylark_bi.phase1.quality import analyze_quality
from skylark_bi.phase1.relationships import analyze_relationships
from skylark_bi.phase1.metrics import get_metric_catalog


RAW_DATA = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA = PROJECT_ROOT / "data" / "processed"
DOCS = PROJECT_ROOT / "docs"


DEALS_FILE = (
    RAW_DATA
    / "Deal funnel Data.xlsx - Deal tracker.csv"
)

WORK_ORDERS_FILE = (
    RAW_DATA
    / "Work_Order_Tracker Data.xlsx - work order tracker.csv"
)


def save_json(
    data: dict,
    path: Path,
) -> None:
    """Save JSON output."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )


def generate_phase1_report(
    deals_profile,
    work_orders_profile,
    deals_quality,
    work_orders_quality,
    relationships,
    metrics,
) -> None:
    """Generate the final Phase 1 Markdown report."""

    lines = [
        "# Phase 1 — Dataset Understanding",
        "",
        "## Dataset Summary",
        "",
        "| Dataset | Records | Columns |",
        "|---|---:|---:|",
        (
            f"| Deals | "
            f"{deals_profile['record_count']} | "
            f"{deals_profile['column_count']} |"
        ),
        (
            f"| Work Orders | "
            f"{work_orders_profile['record_count']} | "
            f"{work_orders_profile['column_count']} |"
        ),
        "",
        "## Data Quality Summary",
        "",
        "### Deals",
        "",
        f"- Critical missing fields: "
        f"{deals_quality['summary']['critical_missing_fields']}",
        f"- Warning fields: "
        f"{deals_quality['summary']['warning_missing_fields']}",
        f"- Completely empty columns: "
        f"{deals_quality['summary']['empty_columns']}",
        f"- Rows involved in duplicate groups: "
        f"{deals_quality['summary']['duplicate_rows']}",
        "",
        "### Work Orders",
        "",
        f"- Critical missing fields: "
        f"{work_orders_quality['summary']['critical_missing_fields']}",
        f"- Warning fields: "
        f"{work_orders_quality['summary']['warning_missing_fields']}",
        f"- Completely empty columns: "
        f"{work_orders_quality['summary']['empty_columns']}",
        f"- Rows involved in duplicate groups: "
        f"{work_orders_quality['summary']['duplicate_rows']}",
        "",
        "## Cross-Board Relationships",
        "",
        "| Deals field | Work Orders field | Overlap | Confidence | Recommendation |",
        "|---|---|---:|---|---|",
    ]

    for relationship in relationships["relationships"]:

        lines.append(
            f"| {relationship['left_column']} | "
            f"{relationship['right_column']} | "
            f"{relationship['overlap_count']} | "
            f"{relationship['confidence']} | "
            f"{relationship['recommendation']} |"
        )

    lines.extend(
        [
            "",
            "## Supported BI Metrics",
            "",
            "| Metric | Dataset | Reliability |",
            "|---|---|---|",
        ]
    )

    for metric in metrics.values():

        lines.append(
            f"| {metric['name']} | "
            f"{metric['dataset']} | "
            f"{metric['reliability']} |"
        )

    lines.extend(
        [
            "",
            "## Key Phase 1 Findings",
            "",
            "1. Deals contain significant missingness in close dates, "
            "closure probability and deal value.",
            "",
            "2. Work Orders contain several completely empty billing "
            "and collection fields.",
            "",
            "3. Deal Name and Deal name masked show strong normalized "
            "overlap and are a candidate record-level relationship.",
            "",
            "4. Owner code and BD/KAM Personnel code show strong overlap.",
            "",
            "5. Sector/service and Sector provide a reliable shared "
            "analytical dimension.",
            "",
            "6. Client Code and Customer Name Code have no observed "
            "overlap and should not be used as a direct join.",
            "",
            "7. Missing values must be communicated as data-quality "
            "caveats rather than inferred without evidence.",
            "",
        ]
    )

    DOCS.mkdir(
        parents=True,
        exist_ok=True,
    )

    (DOCS / "DATASET_ANALYSIS.md").write_text(
        "\n".join(lines)
    )


def main() -> None:
    """Run the complete Phase 1 pipeline."""

    print("=" * 70)
    print("SKYLARK BI AGENT — PHASE 1")
    print("COMPLETE DATASET UNDERSTANDING PIPELINE")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. LOAD
    # ---------------------------------------------------------

    print("\n[1/5] Loading datasets...")

    deals = load_dataset(
        DEALS_FILE,
        dataset_name="Deals",
    )

    work_orders = load_dataset(
        WORK_ORDERS_FILE,
        dataset_name="Work Orders",
    )

    print(
        f"  Deals       : {len(deals)} records"
    )

    print(
        f"  Work Orders : {len(work_orders)} records"
    )

    # ---------------------------------------------------------
    # 2. PROFILE
    # ---------------------------------------------------------

    print("\n[2/5] Profiling datasets...")

    deals_profile = profile_dataframe(
        deals,
        "Deals",
    )

    work_orders_profile = profile_dataframe(
        work_orders,
        "Work Orders",
    )

    # ---------------------------------------------------------
    # 3. QUALITY
    # ---------------------------------------------------------

    print("\n[3/5] Analyzing data quality...")

    deals_quality = analyze_quality(
        deals,
        "Deals",
    )

    work_orders_quality = analyze_quality(
        work_orders,
        "Work Orders",
    )

    # ---------------------------------------------------------
    # 4. RELATIONSHIPS
    # ---------------------------------------------------------

    print("\n[4/5] Analyzing cross-board relationships...")

    relationships = analyze_relationships(
        deals,
        work_orders,
    )

    # ---------------------------------------------------------
    # 5. METRICS
    # ---------------------------------------------------------

    print("\n[5/5] Building business metric catalog...")

    metrics = get_metric_catalog()

    # ---------------------------------------------------------
    # SAVE OUTPUTS
    # ---------------------------------------------------------

    save_json(
        deals_profile,
        PROCESSED_DATA / "deals_profile.json",
    )

    save_json(
        work_orders_profile,
        PROCESSED_DATA / "work_orders_profile.json",
    )

    save_json(
        {
            "deals": deals_quality,
            "work_orders": work_orders_quality,
        },
        PROCESSED_DATA / "data_quality_report.json",
    )

    save_json(
        relationships,
        PROCESSED_DATA / "relationship_report.json",
    )

    save_json(
        metrics,
        PROCESSED_DATA / "metric_catalog.json",
    )

    generate_phase1_report(
        deals_profile,
        work_orders_profile,
        deals_quality,
        work_orders_quality,
        relationships,
        metrics,
    )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("PHASE 1 COMPLETED")
    print("=" * 70)

    print("\nGenerated:")
    print("  data/processed/deals_profile.json")
    print("  data/processed/work_orders_profile.json")
    print("  data/processed/data_quality_report.json")
    print("  data/processed/relationship_report.json")
    print("  data/processed/metric_catalog.json")
    print("  docs/DATASET_ANALYSIS.md")

    print("\nPhase 1 status: READY FOR AGENT DEVELOPMENT")


if __name__ == "__main__":
    main()