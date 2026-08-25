"""
Business metric catalog discovered during Phase 1.

This catalog defines supported founder-level analytics and the
source fields required to calculate them.
"""

from __future__ import annotations

from typing import Any


METRIC_CATALOG: dict[str, dict[str, Any]] = {

    "deal_count": {
        "name": "Deal Count",
        "dataset": "Deals",
        "description": "Number of deal records.",
        "fields": ["Deal Name"],
        "aggregation": "count",
        "reliability": "high",
    },

    "pipeline_value": {
        "name": "Pipeline Value",
        "dataset": "Deals",
        "description": "Sum of available masked deal values.",
        "fields": ["Masked Deal value"],
        "aggregation": "sum",
        "reliability": "medium",
        "caveat": "Deal value is substantially incomplete.",
    },

    "deals_by_sector": {
        "name": "Deals by Sector",
        "dataset": "Deals",
        "description": "Deal count and available value grouped by sector.",
        "fields": [
            "Sector/service",
            "Masked Deal value",
        ],
        "aggregation": "group_by",
        "reliability": "high",
    },

    "deals_by_stage": {
        "name": "Deals by Stage",
        "dataset": "Deals",
        "description": "Distribution of deals across pipeline stages.",
        "fields": [
            "Deal Stage",
            "Deal Name",
        ],
        "aggregation": "group_by",
        "reliability": "high",
    },

    "work_order_count": {
        "name": "Work Order Count",
        "dataset": "Work Orders",
        "description": "Number of work-order records.",
        "fields": ["Serial #"],
        "aggregation": "count",
        "reliability": "high",
    },

    "work_orders_by_sector": {
        "name": "Work Orders by Sector",
        "dataset": "Work Orders",
        "description": "Work-order distribution by sector.",
        "fields": [
            "Sector",
            "Serial #",
        ],
        "aggregation": "group_by",
        "reliability": "high",
    },

    "order_value": {
        "name": "Order Value",
        "dataset": "Work Orders",
        "description": "Total order value.",
        "fields": [
            "Amount in Rupees (Excl of GST) (Masked)"
        ],
        "aggregation": "sum",
        "reliability": "high",
    },

    "billed_value": {
        "name": "Billed Value",
        "dataset": "Work Orders",
        "description": "Total billed value.",
        "fields": [
            "Billed Value in Rupees (Excl of GST.) (Masked)"
        ],
        "aggregation": "sum",
        "reliability": "medium",
        "caveat": "Some records have missing billed values.",
    },

    "collected_amount": {
        "name": "Collected Amount",
        "dataset": "Work Orders",
        "description": "Total collected amount.",
        "fields": [
            "Collected Amount in Rupees (Incl of GST.) (Masked)"
        ],
        "aggregation": "sum",
        "reliability": "medium",
        "caveat": "Collection data is incomplete.",
    },

    "amount_receivable": {
        "name": "Amount Receivable",
        "dataset": "Work Orders",
        "description": "Total outstanding receivables.",
        "fields": [
            "Amount Receivable (Masked)"
        ],
        "aggregation": "sum",
        "reliability": "high",
    },

    "execution_status": {
        "name": "Execution Status",
        "dataset": "Work Orders",
        "description": "Distribution of work orders by execution status.",
        "fields": [
            "Execution Status",
            "Serial #",
        ],
        "aggregation": "group_by",
        "reliability": "high",
    },

    "sector_pipeline_vs_execution": {
        "name": "Sector Pipeline vs Execution",
        "dataset": "Cross-board",
        "description": (
            "Compare deal pipeline with operational work orders "
            "using sector as a shared analytical dimension."
        ),
        "fields": [
            "Deals.Sector/service",
            "Work Orders.Sector",
        ],
        "aggregation": "cross_board",
        "reliability": "high",
        "caveat": (
            "Sector is an analytical dimension, not a record-level join key."
        ),
    },
}


def get_metric_catalog() -> dict[str, dict[str, Any]]:
    """Return the metric catalog."""
    return METRIC_CATALOG