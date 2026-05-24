"""Canonical types used across data, filters, LLM, and UI phases."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class BudgetBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Restaurant:
    id: str
    name: str
    location: str
    cuisines: list[str]
    cost_for_two: float | None = None
    cost_band: BudgetBand | None = None
    rating: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.cost_band is not None:
            data["cost_band"] = self.cost_band.value
        return data


@dataclass
class UserPreferences:
    location: str
    budget: BudgetBand
    cuisine: str | list[str]
    min_rating: float = 0.0
    extras: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Raise ValueError when preferences are invalid."""
        if not self.location or not self.location.strip():
            raise ValueError("Location is required.")
        if not isinstance(self.budget, BudgetBand):
            raise ValueError("Budget must be low, medium, or high.")
        if not 0.0 <= self.min_rating <= 5.0:
            raise ValueError("Minimum rating must be between 0 and 5.")

    def cuisine_list(self) -> list[str]:
        if isinstance(self.cuisine, str):
            parts = [c.strip() for c in self.cuisine.split(",") if c.strip()]
            return parts if parts else ([self.cuisine.strip()] if self.cuisine.strip() else [])
        return [c.strip() for c in self.cuisine if c and str(c).strip()]

    def to_dict(self) -> dict[str, Any]:
        return {
            "location": self.location.strip(),
            "budget": self.budget.value,
            "cuisine": self.cuisine_list(),
            "min_rating": self.min_rating,
            "extras": self.extras,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class Recommendation:
    restaurant: Restaurant
    rank: int
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "restaurant": self.restaurant.to_dict(),
            "explanation": self.explanation,
        }


@dataclass
class Summary:
    recommendations: list[Recommendation] = field(default_factory=list)
    overall_summary: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommendations": [r.to_dict() for r in self.recommendations],
            "overall_summary": self.overall_summary,
        }


@dataclass
class RecommendationResult:
    """Full pipeline output (preferences in, summary + status out)."""

    preferences: UserPreferences
    summary: Summary
    message: str
    shortlist_size: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "preferences": self.preferences.to_dict(),
            "summary": self.summary.to_dict(),
            "message": self.message,
            "shortlist_size": self.shortlist_size,
        }
