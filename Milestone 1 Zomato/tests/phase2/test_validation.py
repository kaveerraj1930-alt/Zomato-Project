"""Phase 2 user input layer tests."""

import json
import pytest

from models import BudgetBand, UserPreferences
from ui.phase2.exceptions import PreferenceValidationError
from ui.phase2.preferences_form import build_preferences
from ui.phase2.serializer import preferences_from_dict, preferences_to_json
from ui.phase2.validator import PreferenceValidator, validate_raw_preferences


def test_validate_raw_success():
    result = validate_raw_preferences(
        location="Btm",
        budget_label="Medium",
        cuisine=["Italian", "Pizza"],
        min_rating=4.0,
        extras={"family_friendly": True},
    )
    assert result.valid
    assert result.preferences is not None
    assert result.preferences.cuisine_list() == ["Italian", "Pizza"]


def test_validate_multiple_errors():
    result = validate_raw_preferences(
        location="",
        budget_label="Premium",
        cuisine=[],
        min_rating=6.0,
    )
    assert not result.valid
    assert len(result.errors) >= 3


def test_build_preferences_raises_validation_error():
    with pytest.raises(PreferenceValidationError) as exc:
        build_preferences(
            location="",
            budget_label="Low",
            cuisine="Chinese",
            min_rating=3.0,
        )
    assert len(exc.value.messages) >= 1


def test_preferences_json_roundtrip():
    prefs = build_preferences(
        location="Indiranagar",
        budget_label="High",
        cuisine="North Indian, Chinese",
        min_rating=4.5,
        quick_service=True,
    )
    payload = json.loads(preferences_to_json(prefs))
    restored = preferences_from_dict(payload)
    assert restored.location == "Indiranagar"
    assert restored.budget == BudgetBand.HIGH
    assert restored.cuisine_list() == ["North Indian", "Chinese"]
    assert restored.extras.get("quick_service") is True


def test_max_cuisines_limit():
    result = validate_raw_preferences(
        location="Btm",
        budget_label="Low",
        cuisine=["A", "B", "C", "D", "E", "F"],
        min_rating=3.0,
    )
    assert not result.valid
    assert any("at most" in e.lower() for e in result.errors)


def test_location_max_length():
    result = validate_raw_preferences(
        location="x" * 101,
        budget_label="Low",
        cuisine="Cafe",
        min_rating=3.0,
    )
    assert not result.valid


def test_validate_preferences_object():
    prefs = UserPreferences(
        location="Btm",
        budget=BudgetBand.MEDIUM,
        cuisine="Italian",
        min_rating=4.0,
    )
    from ui.phase2.validator import validate_preferences

    result = validate_preferences(prefs)
    assert result.valid
