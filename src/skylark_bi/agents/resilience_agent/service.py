"""
High-level service orchestrating the Data Resilience Agent capabilities.
"""

from __future__ import annotations

from typing import Any

from skylark_bi.core.models import Deal, WorkOrder

from .schemas import (
    FieldQualityReport,
    RecordQualityReport,
    DatasetQualityReport,
    AnalysisReadiness,
    DatasetProfile,
    FilteredRecords,
)
from .validators import (
    validate_record,
    retain_valid_records,
    exclude_critical_records,
    filter_by_quality_score,
)
from .profiler import profile_dataset, get_dataset_profile
from .quality import summarize_dataset
from .readiness import check_analysis_readiness


class ResilienceAgentService:
    """
    Public facade for the Data Resilience Agent.

    Provides high-level data quality, profiling, normalization, and filtering
    for Deals and WorkOrders without calling Monday.com APIs directly.
    """

    def validate_deal(self, record: Deal | dict[str, Any]) -> RecordQualityReport:
        """Validate one Deal record."""
        return validate_record("deals", record)

    def validate_work_order(self, record: WorkOrder | dict[str, Any]) -> RecordQualityReport:
        """Validate one WorkOrder record."""
        return validate_record("work_orders", record)

    def validate_deals(self, records: list[Deal | dict[str, Any]]) -> list[RecordQualityReport]:
        """Validate a collection of Deal records."""
        return [self.validate_deal(r) for r in records]

    def validate_work_orders(self, records: list[WorkOrder | dict[str, Any]]) -> list[RecordQualityReport]:
        """Validate a collection of WorkOrder records."""
        return [self.validate_work_order(r) for r in records]

    def assess_deal_quality(self, record: Deal | dict[str, Any]) -> RecordQualityReport:
        """Assess the quality of a single Deal record."""
        return self.validate_deal(record)

    def assess_work_order_quality(self, record: WorkOrder | dict[str, Any]) -> RecordQualityReport:
        """Assess the quality of a single WorkOrder record."""
        return self.validate_work_order(record)

    def profile_deals(self, records: list[Deal | dict[str, Any]]) -> DatasetQualityReport:
        """Profile and summarize the quality of a Deal dataset."""
        field_reports = profile_dataset("deals", records)
        record_reports = self.validate_deals(records)
        return summarize_dataset("deals", len(field_reports), field_reports, record_reports)

    def profile_work_orders(self, records: list[WorkOrder | dict[str, Any]]) -> DatasetQualityReport:
        """Profile and summarize the quality of a WorkOrder dataset."""
        field_reports = profile_dataset("work_orders", records)
        record_reports = self.validate_work_orders(records)
        return summarize_dataset("work_orders", len(field_reports), field_reports, record_reports)

    def get_deals_profile_summary(self, records: list[Deal | dict[str, Any]]) -> DatasetProfile:
        """Get high-level summary profile for Deals."""
        return get_dataset_profile("deals", records)

    def get_work_orders_profile_summary(self, records: list[WorkOrder | dict[str, Any]]) -> DatasetProfile:
        """Get high-level summary profile for WorkOrders."""
        return get_dataset_profile("work_orders", records)

    def normalize_deal(self, record: Deal) -> Deal:
        """Normalize a Deal, returning a new normalized Deal instance."""
        report = self.validate_deal(record)
        normalized_fields = {}
        for field_name, norm_val in report.normalized_values.items():
            normalized_fields[field_name] = norm_val.normalized

        deal_id = getattr(record, "id", None)
        raw_vals = getattr(record, "raw_values", {})

        return Deal(
            id=deal_id,
            raw_values=raw_vals,
            **normalized_fields
        )

    def normalize_work_order(self, record: WorkOrder) -> WorkOrder:
        """Normalize a WorkOrder, returning a new normalized WorkOrder instance."""
        report = self.validate_work_order(record)
        normalized_fields = {}
        for field_name, norm_val in report.normalized_values.items():
            normalized_fields[field_name] = norm_val.normalized

        wo_id = getattr(record, "id", None)
        raw_vals = getattr(record, "raw_values", {})

        return WorkOrder(
            id=wo_id,
            raw_values=raw_vals,
            **normalized_fields
        )

    def normalize_deals(self, records: list[Deal]) -> list[Deal]:
        """Normalize a collection of Deals."""
        return [self.normalize_deal(r) for r in records]

    def normalize_work_orders(self, records: list[WorkOrder]) -> list[WorkOrder]:
        """Normalize a collection of WorkOrders."""
        return [self.normalize_work_order(r) for r in records]

    def check_analysis_readiness(
        self,
        records: list[Any],
        required_fields: list[str],
        optional_fields: list[str] | None = None,
        dataset: str | None = None,
    ) -> AnalysisReadiness:
        """Verify if a set of records has sufficient quality to support analysis."""
        return check_analysis_readiness(
            records=records,
            required_fields=required_fields,
            optional_fields=optional_fields,
            dataset=dataset,
        )

    def filter_by_quality(
        self,
        records: list[Any],
        dataset: str,
        min_score: float | None = None,
        exclude_critical: bool = True,
    ) -> FilteredRecords:
        """Quality-aware non-mutating filtering view of records."""
        if min_score is not None:
            return filter_by_quality_score(records, dataset, min_score)
        if exclude_critical:
            return exclude_critical_records(records, dataset)
        return retain_valid_records(records, dataset)
