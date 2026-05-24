"""Tests for web form → UserPreferences mapping."""

import pytest

from models import BudgetBand
from ui.phase2.exceptions import PreferenceValidationError
from ui.phase2.preferences_form import build_preferences


def test_build_preferences_from_form():
    prefs = build_preferences(
        location="Bangalore",
        budget_label="Medium",
        cuisine="Italian",
        min_rating=4.0,
        family_friendly=True,
    )
    assert prefs.location == "Bangalore"
    assert prefs.budget == BudgetBand.MEDIUM
    assert prefs.cuisine_list() == ["Italian"]
    assert prefs.extras == {"family_friendly": True}


def test_build_preferences_invalid_budget():
    with pytest.raises(PreferenceValidationError, match="Budget"):
        build_preferences(
            location="Delhi",
            budget_label="Premium",
            cuisine="Chinese",
            min_rating=3.0,
        )


def test_build_preferences_empty_location():
    with pytest.raises(PreferenceValidationError, match="Location"):
        build_preferences(
            location="   ",
            budget_label="Low",
            cuisine="Chinese",
            min_rating=3.0,
        )
