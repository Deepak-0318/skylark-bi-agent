"""
Typed response models for Monday.com.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MondayColumn:
    id: str
    title: str
    column_type: str | None = None
    settings: dict[str, Any] | None = None


@dataclass(frozen=True)
class MondayBoard:
    id: int
    name: str
    state: str | None
    permissions: str | None
    columns: list[MondayColumn] = field(
        default_factory=list
    )


@dataclass(frozen=True)
class MondayItem:
    id: str
    name: str
    column_values: dict[str, dict[str, Any]]
    created_at: str | None = None
    updated_at: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class BoardPage:
    items: list[MondayItem]
    cursor: str | None


@dataclass(frozen=True)
class BoardData:
    board: MondayBoard
    items: list[MondayItem]