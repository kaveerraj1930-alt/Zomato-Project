"""Phase 0 foundation tests."""

import pytest

from config import get_settings
from models import BudgetBand, UserPreferences
from services import run_recommendation


def test_run_recommendation_without_catalog(monkeypatch):
    """Pipeline stub when catalog is not loaded."""
    monkeypatch.setattr(
        "services.recommendation.get_restaurants",
        lambda **kwargs: [],
    )
    prefs = UserPreferences(
        location="Delhi",
        budget=BudgetBand.LOW,
        cuisine="Chinese",
        min_rating=3.5,
    )
    result = run_recommendation(prefs)
    assert result.shortlist_size == 0
    assert result.summary.recommendations == []
    assert "Loaded 0 restaurants" in result.message


def test_run_recommendation_rejects_none():
    with pytest.raises(ValueError, match="not None"):
        run_recommendation(None)


def test_user_preferences_validation():
    prefs = UserPreferences(location="", budget=BudgetBand.HIGH, cuisine="Italian")
    with pytest.raises(ValueError, match="Location"):
        prefs.validate()


def test_settings_defaults():
    settings = get_settings()
    assert settings.top_k == 5
    assert settings.shortlist_max == 20
