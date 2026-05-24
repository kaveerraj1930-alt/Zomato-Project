"""Build validated UserPreferences from web or CLI input."""

from __future__ import annotations

from models import UserPreferences

from ui.phase2.constants import BUDGET_LABELS
from ui.phase2.exceptions import PreferenceValidationError
from ui.phase2.validator import PreferenceValidator, validate_raw_preferences


def build_preferences(
    *,
    location: str,
    budget_label: str,
    cuisine: str | list[str],
    min_rating: float,
    family_friendly: bool = False,
    quick_service: bool = False,
    validator: PreferenceValidator | None = None,
) -> UserPreferences:
    """
    Build and validate preferences from form or CLI field values.

    Raises PreferenceValidationError when validation fails.
    """
    extras: dict[str, bool] = {}
    if family_friendly:
        extras["family_friendly"] = True
    if quick_service:
        extras["quick_service"] = True

    result = validate_raw_preferences(
        location=location,
        budget_label=budget_label,
        cuisine=cuisine,
        min_rating=min_rating,
        extras=extras,
        validator=validator,
    )
    if not result.valid or result.preferences is None:
        raise PreferenceValidationError(result.errors)

    return result.preferences
