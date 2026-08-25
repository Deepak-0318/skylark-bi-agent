"""
Quality issue creation, scoring, and labels.
"""

from __future__ import annotations

from collections import Counter

from .schemas import (
    DataQualityIssue,
    DatasetQualityReport,
    RecordQualityReport,
)


DEFAULT_SEVERITY_WEIGHTS = {
    "critical": 0.40,
    "warning": 0.15,
    "info": 0.02,
}


def make_issue(
    dataset: str,
    record_id: str | None,
    field: str,
    issue_type: str,
    severity: str,
    original_value,
    recommended_action: str,
    impact: str | None = None,
) -> DataQualityIssue:
    """Create a structured issue."""

    return DataQualityIssue(
        dataset=dataset,
        record_id=record_id,
        field=field,
        issue_type=issue_type,
        severity=severity,
        original_value=original_value,
        recommended_action=recommended_action,
        impact=impact,
    )


def score_record(
    issues: list[DataQualityIssue],
    severity_weights: dict[str, float] | None = None,
) -> float:
    """Return a deterministic record quality score from 0 to 1."""

    weights = {
        **DEFAULT_SEVERITY_WEIGHTS,
        **(severity_weights or {}),
    }

    penalty = sum(
        weights.get(
            issue.severity,
            0.0,
        )
        for issue in issues
    )

    return round(
        max(
            0.0,
            1.0 - penalty,
        ),
        4,
    )


def quality_label(
    score: float,
) -> str:
    """Return a readable quality label."""

    if score >= 0.95:
        return "excellent"

    if score >= 0.80:
        return "good"

    if score >= 0.60:
        return "fair"

    if score >= 0.30:
        return "poor"

    return "critical"


def score_dataset(
    record_reports: list[RecordQualityReport],
) -> float:
    """Average record scores into a dataset score."""

    if not record_reports:
        return 1.0

    return round(
        sum(
            report.quality_score
            for report in record_reports
        )
        / len(record_reports),
        4,
    )


def summarize_dataset(
    dataset: str,
    field_count: int,
    field_reports,
    record_reports: list[RecordQualityReport],
) -> DatasetQualityReport:
    """Build a dataset-level report from field and record reports."""

    issues = [
        issue
        for report in record_reports
        for issue in report.issues
    ]

    issue_counts = Counter(
        issue.issue_type
        for issue in issues
    )

    field_counts = Counter(
        issue.field
        for issue in issues
    )

    dataset_score = score_dataset(
        record_reports
    )

    return DatasetQualityReport(
        dataset=dataset,
        record_count=len(record_reports),
        field_count=field_count,
        records_with_issues=sum(
            1
            for report in record_reports
            if report.issues
        ),
        records_without_issues=sum(
            1
            for report in record_reports
            if not report.issues
        ),
        critical_issues=sum(
            1
            for issue in issues
            if issue.severity == "critical"
        ),
        warning_issues=sum(
            1
            for issue in issues
            if issue.severity == "warning"
        ),
        info_issues=sum(
            1
            for issue in issues
            if issue.severity == "info"
        ),
        quality_score=dataset_score,
        quality_label=quality_label(
            dataset_score
        ),
        top_problematic_fields=field_counts.most_common(
            10
        ),
        top_issue_types=issue_counts.most_common(
            10
        ),
        field_reports=field_reports,
        record_reports=record_reports,
        issues=issues,
    )
