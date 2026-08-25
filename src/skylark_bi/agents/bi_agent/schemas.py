from dataclasses import dataclass, field
from typing import Any


@dataclass
class BIResult:
    intent: str
    metrics: dict[str, Any] = field(default_factory=dict)
    grouped: list[dict[str, Any]] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    data_quality: dict[str, Any] = field(default_factory=dict)