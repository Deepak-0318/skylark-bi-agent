"""
Business-impact metadata for field-level quality issues.
"""

from __future__ import annotations

from .schemas import BusinessImpact


FIELD_IMPACT_CATALOG = {
    # Deals
    ("deal_value", "missing_value"): BusinessImpact(
        field="deal_value",
        issue_type="missing_value",
        impact="cannot reliably participate in pipeline value aggregation",
        recommended_action="exclude from value-based aggregation",
    ),
    ("deal_value", "invalid_number"): BusinessImpact(
        field="deal_value",
        issue_type="invalid_number",
        impact="cannot reliably participate in pipeline value aggregation due to malformed value",
        recommended_action="exclude from value-based aggregation",
    ),
    ("sector", "missing_value"): BusinessImpact(
        field="sector",
        issue_type="missing_value",
        impact="cannot reliably participate in sector analysis",
        recommended_action="exclude from sector breakdowns",
    ),
    ("close_date", "missing_value"): BusinessImpact(
        field="close_date",
        issue_type="missing_value",
        impact="cannot reliably be assigned to a quarter using close date",
        recommended_action="exclude from close-date period grouping",
    ),
    ("close_date", "invalid_date"): BusinessImpact(
        field="close_date",
        issue_type="invalid_date",
        impact="cannot reliably be assigned to a quarter using close date due to malformed date",
        recommended_action="exclude from close-date period grouping",
    ),
    ("closure_probability", "missing_value"): BusinessImpact(
        field="closure_probability",
        issue_type="missing_value",
        impact="weighted pipeline cannot be calculated for that record",
        recommended_action="exclude from weighted pipeline calculations",
    ),

    # Work Orders
    ("execution_status", "missing_value"): BusinessImpact(
        field="execution_status",
        issue_type="missing_value",
        impact="operational status analysis may exclude the record",
        recommended_action="exclude from execution-status analysis",
    ),
    ("amount_receivable", "invalid_number"): BusinessImpact(
        field="amount_receivable",
        issue_type="invalid_number",
        impact="receivables analysis cannot safely use that value",
        recommended_action="exclude from receivables aggregation",
    ),
    ("amount_receivable", "missing_value"): BusinessImpact(
        field="amount_receivable",
        issue_type="missing_value",
        impact="receivables analysis may understate records with missing receivable values",
        recommended_action="exclude from receivables aggregation",
    ),
    ("billing_status", "missing_value"): BusinessImpact(
        field="billing_status",
        issue_type="missing_value",
        impact="billing status analysis may exclude the record",
        recommended_action="exclude from billing-status analysis",
    ),
}


def get_business_impact(
    field: str,
    issue_type: str,
) -> BusinessImpact | None:
    """Return configured impact metadata for an issue."""

    # 1. Exact match on (field, issue_type)
    impact = FIELD_IMPACT_CATALOG.get((field, issue_type))
    if impact:
        return impact

    # 2. Check for generalized lookups/fallbacks
    for (f, it), imp in FIELD_IMPACT_CATALOG.items():
        if f == field:
            if it == "missing_value" and issue_type.startswith("invalid"):
                return imp
            if it.startswith("invalid") and issue_type == "missing_value":
                return imp

    return None


def recommended_action_for(
    field: str,
    issue_type: str,
) -> str:
    """Return recommended action text for a field issue."""

    impact = get_business_impact(
        field,
        issue_type,
    )

    if impact:
        return impact.recommended_action

    if issue_type == "missing_value":
        return "review missing value before analysis"

    if issue_type.startswith("invalid"):
        return "exclude invalid value from typed analysis"

    if issue_type == "unknown_category":
        return "review category mapping before grouped analysis"

    return "review data quality issue"
