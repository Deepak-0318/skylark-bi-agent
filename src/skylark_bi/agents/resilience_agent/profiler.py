"""
Dataset profiling for data quality analysis.

Builds field-level reports from validated records without modifying data.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

from .schemas import FieldQualityReport, DatasetProfile
from .validators import validate_record, get_schema, _get_raw_or_field_value
from .normalizer import (
    normalize_number,
    normalize_date,
    normalize_category,
    missing_kind,
)

DEFAULT_MISSING_TOKENS = {
    "",
    "na",
    "n/a",
    "nan",
    "none",
    "null",
}


def profile_field(
    dataset: str,
    field_name: str,
    values: list[Any],
    issue_count: int = 0,
) -> FieldQualityReport:
    """
    Build a quality profile for one field across all records.

    Preserves original values, detects missing/invalid patterns.
    """

    total = len(values)
    null_count = sum(
        1
        for v in values
        if v is None
    )

    non_null_values = [
        v
        for v in values
        if v is not None
    ]

    empty_string_count = sum(
        1
        for v in non_null_values
        if isinstance(v, str) and v == ""
    )

    missing_token_count = sum(
        1
        for v in non_null_values
        if missing_kind(v, DEFAULT_MISSING_TOKENS)
    )

    total_missing = (
        null_count
        + empty_string_count
        + missing_token_count
    )

    non_null_count = total - total_missing

    # Extract valid values for analysis
    valid_values = [
        v
        for v in non_null_values
        if not missing_kind(v, DEFAULT_MISSING_TOKENS)
    ]

    # Type inference
    numeric_count = 0
    date_count = 0
    
    for v in valid_values:
        if normalize_number(v).normalized is not None:
            numeric_count += 1
        if normalize_date(v).normalized is not None:
            date_count += 1

    total_valid = len(valid_values)
    if total_valid > 0:
        if numeric_count / total_valid > 0.5:
            inferred_type = "numeric"
        elif date_count / total_valid > 0.5:
            inferred_type = "date"
        else:
            # Check unique count relative to total for categorical
            unique_vals = set(str(val).casefold() for val in valid_values)
            if len(unique_vals) / total_valid < 0.2 and len(unique_vals) < 15:
                inferred_type = "categorical"
            else:
                inferred_type = "text"
    else:
        inferred_type = "text"

    # Expected Type and Invalid Counts
    schema = get_schema(dataset)
    field_spec = schema.get(field_name)
    expected_type = field_spec.expected_type if field_spec else "text"
    
    invalid_count = 0
    if expected_type == "numeric":
        invalid_count = sum(
            1
            for v in valid_values
            if normalize_number(v).normalized is None
        )
    elif expected_type == "date":
        invalid_count = sum(
            1
            for v in valid_values
            if normalize_date(v).normalized is None
        )
    elif expected_type == "categorical":
        allowed = field_spec.allowed_values if field_spec else None
        invalid_count = sum(
            1
            for v in valid_values
            if not normalize_category(v, allowed_values=allowed).valid
        )

    # Uniqueness and duplicates
    unique_values = set(
        str(v).strip()
        for v in valid_values
    )

    unique_count = len(unique_values)

    duplicate_value_count = len(valid_values) - unique_count

    # Examples
    example_values = valid_values[:5]

    # Suspicious values (outliers)
    suspicious_values = []
    if inferred_type == "numeric":
        try:
            nums = [
                float(normalize_number(v).normalized)
                for v in valid_values
                if normalize_number(v).valid
            ]
            if nums:
                mean = sum(nums) / len(nums)
                variance = sum((x - mean) ** 2 for x in nums) / len(nums)
                std = math.sqrt(variance)
                
                if std > 0:
                    suspicious_values = [
                        v
                        for v in valid_values
                        if normalize_number(v).valid
                        and abs(float(normalize_number(v).normalized) - mean) > 3 * std
                    ][:5]
        except (ValueError, TypeError):
            pass

    # Determine severity
    null_percentage = (
        (total_missing / total * 100)
        if total > 0
        else 0
    )

    if field_spec and field_spec.required and (total_missing > 0 or invalid_count > 0):
        severity = "critical"
    elif null_percentage >= 80 or (invalid_count / total * 100 >= 30 if total > 0 else False):
        severity = "critical"
    elif null_percentage >= 30 or invalid_count > 0:
        severity = "warning"
    else:
        severity = "info"

    return FieldQualityReport(
        dataset=dataset,
        field=field_name,
        total_records=total,
        non_null_records=non_null_count,
        null_count=total_missing,
        null_percentage=round(
            null_percentage,
            2,
        ),
        empty_string_count=empty_string_count,
        unique_count=unique_count,
        duplicate_value_count=duplicate_value_count,
        expected_type=expected_type,
        inferred_type=inferred_type,
        invalid_type_count=invalid_count,
        example_values=example_values,
        suspicious_values=suspicious_values,
        severity=severity,
        invalid_count=invalid_count,
        issue_count=issue_count,
        sample_values=example_values,
    )


def profile_dataset(
    dataset: str,
    records: list[Any],
) -> list[FieldQualityReport]:
    """
    Build field-level profiles for all records in a dataset.

    Returns one FieldQualityReport per field.
    """

    if not records:
        return []

    # Run validation to collect issues and reports
    record_reports = [validate_record(dataset, r) for r in records]

    # Count issues per field
    issues_by_field: dict[str, int] = {}
    for rep in record_reports:
        for issue in rep.issues:
            issues_by_field[issue.field] = issues_by_field.get(issue.field, 0) + 1

    # Extract all field values
    schema = get_schema(dataset)
    field_values: dict[str, list[Any]] = {
        field_name: []
        for field_name in schema.keys()
    }

    for record in records:
        for field_name in schema.keys():
            value = _get_raw_or_field_value(record, field_name, dataset)
            field_values[field_name].append(value)

    # Profile each field
    return [
        profile_field(
            dataset,
            field_name,
            values,
            issue_count=issues_by_field.get(field_name, 0),
        )
        for field_name, values in field_values.items()
    ]


def get_dataset_profile(
    dataset: str,
    records: list[Any],
) -> DatasetProfile:
    """Create a high-level summary profile of a dataset."""
    schema = get_schema(dataset)
    if not records:
        return DatasetProfile(
            dataset=dataset,
            records=0,
            fields=len(schema),
            fields_with_issues=0,
            records_with_issues=0,
            critical_issues=0,
            warning_issues=0,
        )

    field_reports = profile_dataset(dataset, records)
    record_reports = [validate_record(dataset, r) for r in records]

    all_issues = [issue for rep in record_reports for issue in rep.issues]

    fields_with_issues = sum(1 for fr in field_reports if fr.issue_count > 0)
    records_with_issues = sum(1 for rr in record_reports if rr.issues)
    critical_issues = sum(1 for issue in all_issues if issue.severity == "critical")
    warning_issues = sum(1 for issue in all_issues if issue.severity == "warning")

    return DatasetProfile(
        dataset=dataset,
        records=len(records),
        fields=len(schema),
        fields_with_issues=fields_with_issues,
        records_with_issues=records_with_issues,
        critical_issues=critical_issues,
        warning_issues=warning_issues,
    )
