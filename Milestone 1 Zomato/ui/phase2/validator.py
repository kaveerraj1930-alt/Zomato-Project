"""Validate user preferences before they enter the pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from models import BudgetBand, UserPreferences

from ui.phase2.constants import BUDGET_LABELS

MAX_LOCATION_LENGTH = 100
MAX_CUISINE_ITEM_LENGTH = 50
MAX_CUISINES = 5
MAX_EXTRAS_KEYS = 10
ALLOWED_EXTRA_KEYS = frozenset({"family_friendly", "quick_service"})


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    preferences: UserPreferences | None = None

    @property
    def error_message(self) -> str:
        return "; ".join(self.errors)


class PreferenceValidator:
    """Required fields, enums, rating range, and safe string limits."""

    def validate_raw(
        self,
        *,
        location: str,
        budget_label: str,
        cuisine: str | list[str],
        min_rating: float,
        extras: dict[str, Any] | None = None,
    ) -> ValidationResult:
        errors = self._collect_errors(
            location=location,
            budget_label=budget_label,
            cuisine=cuisine,
            min_rating=min_rating,
            extras=extras or {},
        )
        if errors:
            return ValidationResult(valid=False, errors=errors)

        budget = BUDGET_LABELS[budget_label]
        cuisine_value: str | list[str]
        if isinstance(cuisine, list):
            cuisine_value = cuisine
        else:
            cuisine_value = cuisine.strip()

        preferences = UserPreferences(
            location=location.strip(),
            budget=budget,
            cuisine=cuisine_value,
            min_rating=float(min_rating),
            extras={k: v for k, v in (extras or {}).items() if v},
        )
        return ValidationResult(valid=True, errors=[], preferences=preferences)

    def validate(self, preferences: UserPreferences) -> ValidationResult:
        budget_label = preferences.budget.value.title()
        if preferences.budget == BudgetBand.LOW:
            budget_label = "Low"
        elif preferences.budget == BudgetBand.MEDIUM:
            budget_label = "Medium"
        elif preferences.budget == BudgetBand.HIGH:
            budget_label = "High"

        return self.validate_raw(
            location=preferences.location,
            budget_label=budget_label,
            cuisine=preferences.cuisine,
            min_rating=preferences.min_rating,
            extras=preferences.extras,
        )

    def _collect_errors(
        self,
        *,
        location: str,
        budget_label: str,
        cuisine: str | list[str],
        min_rating: float,
        extras: dict[str, Any],
    ) -> list[str]:
        errors: list[str] = []

        loc = (location or "").strip()
        if not loc:
            errors.append("Location is required.")
        elif len(loc) > MAX_LOCATION_LENGTH:
            errors.append(f"Location must be at most {MAX_LOCATION_LENGTH} characters.")

        if budget_label not in BUDGET_LABELS:
            errors.append("Budget must be Low, Medium, or High.")

        cuisines = self._normalize_cuisines(cuisine)
        if not cuisines:
            errors.append("At least one cuisine is required.")
        elif len(cuisines) > MAX_CUISINES:
            errors.append(f"Select at most {MAX_CUISINES} cuisines.")
        else:
            for item in cuisines:
                if len(item) > MAX_CUISINE_ITEM_LENGTH:
                    errors.append(
                        f"Each cuisine must be at most {MAX_CUISINE_ITEM_LENGTH} characters."
                    )
                    break

        try:
            rating = float(min_rating)
        except (TypeError, ValueError):
            errors.append("Minimum rating must be a number.")
            rating = -1.0

        if not errors and not 0.0 <= rating <= 5.0:
            errors.append("Minimum rating must be between 0 and 5.")

        if len(extras) > MAX_EXTRAS_KEYS:
            errors.append(f"At most {MAX_EXTRAS_KEYS} extra preferences are allowed.")

        unknown_extras = set(extras) - ALLOWED_EXTRA_KEYS
        if unknown_extras:
            errors.append(f"Unsupported extra preferences: {', '.join(sorted(unknown_extras))}.")

        return errors

    @staticmethod
    def _normalize_cuisines(cuisine: str | list[str]) -> list[str]:
        if isinstance(cuisine, list):
            return [c.strip() for c in cuisine if c and str(c).strip()]
        return [c.strip() for c in str(cuisine).split(",") if c.strip()]


_default_validator = PreferenceValidator()


def validate_preferences(
    preferences: UserPreferences,
    *,
    validator: PreferenceValidator | None = None,
) -> ValidationResult:
    return (validator or _default_validator).validate(preferences)


def validate_raw_preferences(
    *,
    location: str,
    budget_label: str,
    cuisine: str | list[str],
    min_rating: float,
    extras: dict[str, Any] | None = None,
    validator: PreferenceValidator | None = None,
) -> ValidationResult:
    return (validator or _default_validator).validate_raw(
        location=location,
        budget_label=budget_label,
        cuisine=cuisine,
        min_rating=min_rating,
        extras=extras,
    )
