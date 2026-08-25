"""
Analysis readiness checking for Data Resilience Agent.
"""

from __future__ import annotations

from typing import Any

from .schemas import AnalysisReadiness, DataQualityIssue
from .validators import get_schema, validate_record, _record_id


def check_analysis_readiness(
    records: list[Any],
    required_fields: list[str],
    optional_fields: list[str] | None = None,
    dataset: str | None = None,
) -> AnalysisReadiness:
    """
    Assess whether a dataset of records is ready for a specific analysis,
    given required and optional fields.
    """
    if not dataset and records:
        first_rec = records[0]
        if isinstance(first_rec, dict):
            # Try to infer from dict keys
            if "deal_value" in first_rec:
                dataset = "deals"
            elif "amount_receivable" in first_rec:
                dataset = "work_orders"
        else:
            cls_name = first_rec.__class__.__name__
            if cls_name == "Deal":
                dataset = "deals"
            elif cls_name == "WorkOrder":
                dataset = "work_orders"

    if not dataset:
        dataset = "deals"  # fallback default

    try:
        schema = get_schema(dataset)
    except ValueError:
        schema = {}

    missing_required_fields: list[str] = []
    for field in required_fields:
        if field not in schema:
            missing_required_fields.append(field)

    # 1. NOT_READY if required fields do not exist in the schema at all
    if missing_required_fields:
        caveats = [
            f"Required field '{f}' is completely missing from the schema."
            for f in missing_required_fields
        ]
        return AnalysisReadiness(
            dataset=dataset,
            status="NOT_READY",
            ready=False,
            partially_ready=False,
            missing_required_fields=missing_required_fields,
            affected_records=[],
            quality_warnings=[],
            critical_issues=[],
            caveats=caveats,
        )

    # 2. Scan records for quality issues
    affected_records_set = set()
    critical_issues: list[DataQualityIssue] = []
    quality_warnings: list[DataQualityIssue] = []
    
    # Track count of missing/invalid values for required fields
    required_issues_count: dict[str, int] = {f: 0 for f in required_fields}

    for record in records:
        record_id = _record_id(record) or "unknown"
        report = validate_record(dataset, record)
        
        # Check for issues in required fields
        has_required_issue = False
        for issue in report.issues:
            if issue.field in required_fields:
                has_required_issue = True
                required_issues_count[issue.field] += 1
                if issue.severity == "critical":
                    critical_issues.append(issue)
                else:
                    quality_warnings.append(issue)
            elif optional_fields and issue.field in optional_fields:
                quality_warnings.append(issue)
        
        if has_required_issue:
            affected_records_set.add(record_id)

    affected_records = sorted(list(affected_records_set))

    # 3. Determine status and caveats
    if critical_issues or affected_records:
        status = "PARTIALLY_READY"
        ready = False
        partially_ready = True
        
        # Generate specific caveats based on which required fields are affected
        caveats = []
        for field, count in required_issues_count.items():
            if count > 0:
                if field == "deal_value":
                    caveats.append("Pipeline value analysis can proceed using records with usable deal values.")
                elif field == "sector":
                    caveats.append("Sector analysis can proceed using records with usable sector values.")
                else:
                    caveats.append(f"Analysis can proceed using records with usable '{field}' values ({count} records affected).")
        if not caveats:
            caveats.append("Some records contain issues in required fields.")
    else:
        status = "READY"
        ready = True
        partially_ready = False
        caveats = []

    return AnalysisReadiness(
        dataset=dataset,
        status=status,
        ready=ready,
        partially_ready=partially_ready,
        missing_required_fields=missing_required_fields,
        affected_records=affected_records,
        quality_warnings=quality_warnings,
        critical_issues=critical_issues,
        caveats=caveats,
    )
