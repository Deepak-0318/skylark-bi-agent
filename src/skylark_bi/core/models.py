"""
Canonical business models used across the Skylark BI Agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Deal:
    """Canonical representation of a sales deal."""

    deal_name: Optional[str] = None
    owner_code: Optional[str] = None
    client_code: Optional[str] = None
    deal_status: Optional[str] = None
    close_date: Optional[datetime] = None
    closure_probability: Optional[str] = None
    deal_value: Optional[float] = None
    tentative_close_date: Optional[datetime] = None
    deal_stage: Optional[str] = None
    product: Optional[str] = None
    sector: Optional[str] = None
    created_date: Optional[datetime] = None


@dataclass
class WorkOrder:
    """Canonical representation of an operational work order."""

    deal_name: Optional[str] = None
    customer_code: Optional[str] = None
    serial_number: Optional[str] = None
    nature_of_work: Optional[str] = None
    execution_status: Optional[str] = None
    data_delivery_date: Optional[datetime] = None
    po_loi_date: Optional[datetime] = None
    document_type: Optional[str] = None
    probable_start_date: Optional[datetime] = None
    probable_end_date: Optional[datetime] = None
    owner_code: Optional[str] = None
    sector: Optional[str] = None
    type_of_work: Optional[str] = None
    order_value: Optional[float] = None
    billed_value: Optional[float] = None
    collected_amount: Optional[float] = None
    amount_to_be_billed: Optional[float] = None
    amount_receivable: Optional[float] = None
    quantity_by_ops: Optional[float] = None
    quantity_as_per_po: Optional[float] = None
    quantity_billed: Optional[float] = None
    balance_quantity: Optional[float] = None