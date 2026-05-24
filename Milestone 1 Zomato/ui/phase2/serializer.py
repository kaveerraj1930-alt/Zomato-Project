"""Serialize preferences for logging and prompt building."""

from __future__ import annotations

import json
import logging
from typing import Any

from models import UserPreferences

logger = logging.getLogger(__name__)


def preferences_to_dict(preferences: UserPreferences) -> dict[str, Any]:
    return preferences.to_dict()


def preferences_to_json(preferences: UserPreferences, *, indent: int | None = None) -> str:
    return json.dumps(preferences_to_dict(preferences), ensure_ascii=False, indent=indent)


def preferences_from_dict(data: dict[str, Any]) -> UserPreferences:
    from models import BudgetBand

    cuisine = data.get("cuisine", [])
    if isinstance(cuisine, str):
        cuisine_value: str | list[str] = cuisine
    else:
        cuisine_value = list(cuisine)

    return UserPreferences(
        location=str(data["location"]).strip(),
        budget=BudgetBand(str(data["budget"]).lower()),
        cuisine=cuisine_value,
        min_rating=float(data.get("min_rating", 0.0)),
        extras=dict(data.get("extras") or {}),
    )


def log_preferences(preferences: UserPreferences, *, level: int = logging.INFO) -> None:
    """Log validated preferences as JSON for debugging and audit."""
    logger.log(level, "User preferences: %s", preferences_to_json(preferences))
