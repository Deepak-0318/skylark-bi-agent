from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueryPlan:
    original_query: str
    intent: str
    datasets: list[str] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)
    date_range: dict[str, Any] = field(default_factory=dict)
    metrics: list[str] = field(default_factory=list)
    group_by: list[str] = field(default_factory=list)
    sort_by: str | None = None
    descending: bool = True
    limit: int | None = None
    confidence: float = 0.0
    clarification_required: bool = False
    clarification_question: str | None = None