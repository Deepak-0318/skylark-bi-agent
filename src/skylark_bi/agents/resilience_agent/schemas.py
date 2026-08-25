"""
Structured models for the Data Resilience Agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


Severity = str
ExpectedType = str


@dataclass(frozen=True)
class FieldSpec:
    """Expected quality rules for a canonical field."""

    name: str
    expected_type: ExpectedType = "text"
    required: bool = False
    allowed_values: set[str] | None = None
    missing_tokens: set[str] | None = None
    dash_is_missing: bool = False


@dataclass(frozen=True)
class NormalizedValue:
    """Auditable normalization result for one value."""

    original: Any
    normalized: Any
    valid: bool
    issues: list[str] = field(
        default_factory=list
    )
    reason: str | None = None


@dataclass(frozen=True)
class BusinessImpact:
    """Business meaning of a field-level quality issue."""

    field: str
    issue_type: str
    impact: str
    recommended_action: str


@dataclass(frozen=True)
class DataQualityIssue:
    """A single data-quality issue."""

    dataset: str
    record_id: str | None
    field: str
    issue_type: str
    severity: Severity
    original_value: Any
    recommended_action: str
    impact: str | None = None
    normalized_value: Any = None
    message: str = ""
    business_impact: str | None = None


@dataclass(frozen=True)
class FieldQualityReport:
    """Quality profile for a dataset field."""

    dataset: str
    field: str
    total_records: int
    non_null_records: int
    null_count: int
    null_percentage: float
    empty_string_count: int
    unique_count: int
    duplicate_value_count: int
    expected_type: ExpectedType
    inferred_type: ExpectedType
    invalid_type_count: int
    example_values: list[Any]
    suspicious_values: list[Any]
    severity: Severity
    invalid_count: int = 0
    issue_count: int = 0
    sample_values: list[Any] = field(default_factory=list)

    @property
    def non_null_count(self) -> int:
        return self.non_null_records


@dataclass(frozen=True)
class RecordQualityReport:
    """Quality report for one canonical record."""

    dataset: str
    record_id: str | None
    issues: list[DataQualityIssue]
    normalized_values: dict[str, NormalizedValue]
    quality_score: float
    quality_label: str


@dataclass(frozen=True)
class DatasetQualityReport:
    """Dataset-level quality report."""

    dataset: str
    record_count: int
    field_count: int
    records_with_issues: int
    records_without_issues: int
    critical_issues: int
    warning_issues: int
    info_issues: int
    quality_score: float
    quality_label: str
    top_problematic_fields: list[tuple[str, int]]
    top_issue_types: list[tuple[str, int]]
    field_reports: list[FieldQualityReport]
    record_reports: list[RecordQualityReport]
    issues: list[DataQualityIssue]


@dataclass(frozen=True)
class DatasetProfile:
    """Dataset-level profile summary."""

    dataset: str
    records: int
    fields: int
    fields_with_issues: int
    records_with_issues: int
    critical_issues: int
    warning_issues: int


@dataclass(frozen=True)
class AnalysisReadiness:
    """Quality-aware readiness for a requested analysis."""

    dataset: str
    status: str
    ready: bool
    partially_ready: bool
    missing_required_fields: list[str]
    affected_records: list[str] = field(default_factory=list)
    quality_warnings: list[DataQualityIssue] = field(default_factory=list)
    critical_issues: list[DataQualityIssue] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FilteredRecords:
    """Non-mutating quality-aware record view."""

    records: list[Any]
    excluded_records: list[Any]
    record_reports: list[RecordQualityReport]
