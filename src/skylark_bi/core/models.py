"""
Canonical business models used across the Skylark BI Agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class Deal:
    """Canonical representation of a sales deal."""

    id: str | None = None
    deal_name: str | None = None
    owner_code: str | None = None
    client_code: str | None = None
    deal_status: str | None = None
    close_date: date | None = None
    closure_probability: float | None = None
    deal_value: float | None = None
    tentative_close_date: date | None = None
    deal_stage: str | None = None
    product_deal: str | None = None
    sector: str | None = None
    created_date: date | None = None
    raw_values: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def product(self) -> str | None:
        """Backward-compatible alias for older Phase 2 code."""

        return self.product_deal


@dataclass
class WorkOrder:
    """Canonical representation of an operational work order."""

    id: str | None = None
    deal_name: str | None = None
    customer_name_code: str | None = None
    serial_number: str | None = None
    nature_of_work: str | None = None
    last_executed_month: date | None = None
    execution_status: str | None = None
    data_delivery_date: date | None = None
    po_loi_date: date | None = None
    document_type: str | None = None
    probable_start_date: date | None = None
    probable_end_date: date | None = None
    bd_kam_personnel_code: str | None = None
    sector: str | None = None
    type_of_work: str | None = None
    software_platform_in_deliverables: str | None = None
    last_invoice_date: date | None = None
    latest_invoice_number: str | None = None
    amount_excl_gst: float | None = None
    amount_incl_gst: float | None = None
    billed_value_excl_gst: float | None = None
    billed_value_incl_gst: float | None = None
    collected_amount_incl_gst: float | None = None
    amount_to_be_billed_excl_gst: float | None = None
    amount_to_be_billed_incl_gst: float | None = None
    amount_receivable: float | None = None
    ar_priority_account: str | None = None
    quantity_by_ops: float | None = None
    quantities_as_per_po: float | None = None
    quantity_billed: float | None = None
    balance_quantity: float | None = None
    invoice_status: str | None = None
    expected_billing_month: date | None = None
    actual_billing_month: date | None = None
    actual_collection_month: date | None = None
    wo_status_billed: str | None = None
    collection_status: str | None = None
    collection_date: date | None = None
    billing_status: str | None = None
    raw_values: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def customer_code(self) -> str | None:
        """Backward-compatible alias for older Phase 2 code."""

        return self.customer_name_code

    @property
    def owner_code(self) -> str | None:
        """Backward-compatible alias for older Phase 2 code."""

        return self.bd_kam_personnel_code

    @property
    def order_value(self) -> float | None:
        """Backward-compatible alias for older Phase 2 code."""

        return self.amount_excl_gst

    @property
    def billed_value(self) -> float | None:
        """Backward-compatible alias for older Phase 2 code."""

        return self.billed_value_excl_gst

    @property
    def collected_amount(self) -> float | None:
        """Backward-compatible alias for older Phase 2 code."""

        return self.collected_amount_incl_gst

    @property
    def amount_to_be_billed(self) -> float | None:
        """Backward-compatible alias for older Phase 2 code."""

        return self.amount_to_be_billed_excl_gst

    @property
    def quantity_as_per_po(self) -> float | None:
        """Backward-compatible alias for older Phase 2 code."""

        return self.quantities_as_per_po
