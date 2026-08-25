from dataclasses import dataclass, field
from typing import Any


@dataclass
class FinalAnswer:
    answer: str
    headline_metrics: dict[str, Any] = field(default_factory=dict)
    insights: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    data_quality: dict[str, Any] = field(default_factory=dict)
    clarification_required: bool = False
    clarification_question: str | None = None