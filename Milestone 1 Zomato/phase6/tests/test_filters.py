"""Phase 6: Unit tests for the filter pipeline (Phase 3)."""

from __future__ import annotations

import pytest

from models.schemas import BudgetBand, Restaurant, UserPreferences
from phase3.filters import FilterPipeline, apply_shortlist_cap


def _make_restaurant(
    name: str,
    location: str = "Bangalore",
    cuisines: list[str] | None = None,
    rating: float = 4.0,
    cost_band: BudgetBand | None = BudgetBand.MEDIUM,
) -> Restaurant:
    return Restaurant(
        id=name.lower().replace(" ", "_"),
        name=name,
        location=location,
        cuisines=cuisines or ["Indian"],
        rating=rating,
        cost_band=cost_band,
    )


@pytest.fixture
def sample_catalog() -> list[Restaurant]:
    return [
        _make_restaurant("Bangalore Biryani", location="Bangalore", cuisines=["Indian"], rating=4.5, cost_band=BudgetBand.MEDIUM),
        _make_restaurant("Italian Place", location="Bangalore", cuisines=["Italian", "Pizza"], rating=4.2, cost_band=BudgetBand.HIGH),
        _make_restaurant("Budget Dhaba", location="Delhi", cuisines=["North Indian"], rating=3.8, cost_band=BudgetBand.LOW),
        _make_restaurant("Fine Dining", location="Bangalore", cuisines=["Continental"], rating=4.9, cost_band=BudgetBand.HIGH),
        _make_restaurant("Street Wok", location="Mumbai", cuisines=["Chinese", "Asian"], rating=4.0, cost_band=BudgetBand.LOW),
        _make_restaurant("Bellandur Cafe", location="Bellandur", cuisines=["Cafe", "Italian"], rating=4.3, cost_band=BudgetBand.MEDIUM),
    ]


class TestFilterByLocation:
    def test_exact_match(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="Bangalore", budget=BudgetBand.LOW, cuisine="Indian")
        result = pipeline._filter_by_location(sample_catalog, prefs)
        assert len(result) == 3
        assert all("bangalore" in r.location.lower() for r in result)

    def test_partial_match(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="Bell", budget=BudgetBand.LOW, cuisine="Indian")
        result = pipeline._filter_by_location(sample_catalog, prefs)
        assert len(result) == 1
        assert result[0].name == "Bellandur Cafe"

    def test_empty_location_returns_all(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="", budget=BudgetBand.LOW, cuisine="Indian")
        result = pipeline._filter_by_location(sample_catalog, prefs)
        assert len(result) == len(sample_catalog)

    def test_case_insensitive(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="BANGALORE", budget=BudgetBand.LOW, cuisine="Indian")
        result = pipeline._filter_by_location(sample_catalog, prefs)
        assert len(result) == 3


class TestFilterByCuisine:
    def test_single_cuisine_match(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="", budget=BudgetBand.LOW, cuisine="Italian")
        result = pipeline._filter_by_cuisine(sample_catalog, prefs)
        assert len(result) == 2
        assert {r.name for r in result} == {"Italian Place", "Bellandur Cafe"}

    def test_multiple_cuisines_string(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="", budget=BudgetBand.LOW, cuisine="Italian, Chinese")
        result = pipeline._filter_by_cuisine(sample_catalog, prefs)
        assert len(result) == 3

    def test_empty_cuisine_returns_all(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="", budget=BudgetBand.LOW, cuisine="")
        result = pipeline._filter_by_cuisine(sample_catalog, prefs)
        assert len(result) == len(sample_catalog)

    def test_no_match(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="", budget=BudgetBand.LOW, cuisine="Mexican")
        result = pipeline._filter_by_cuisine(sample_catalog, prefs)
        assert len(result) == 0


class TestFilterByRating:
    def test_min_rating_4_5(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="", budget=BudgetBand.LOW, cuisine="", min_rating=4.5)
        result = pipeline._filter_by_rating(sample_catalog, prefs)
        assert len(result) == 2
        assert all(r.rating >= 4.5 for r in result)

    def test_min_rating_0_returns_all(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="", budget=BudgetBand.LOW, cuisine="", min_rating=0.0)
        result = pipeline._filter_by_rating(sample_catalog, prefs)
        assert len(result) == len(sample_catalog)


class TestFilterByBudget:
    def test_low_budget(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="", budget=BudgetBand.LOW, cuisine="")
        result = pipeline._filter_by_budget(sample_catalog, prefs)
        assert len(result) == 2
        assert all(r.cost_band in [BudgetBand.LOW, None] for r in result)

    def test_medium_budget_includes_low_and_medium(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="", budget=BudgetBand.MEDIUM, cuisine="")
        result = pipeline._filter_by_budget(sample_catalog, prefs)
        low_medium = {BudgetBand.LOW, BudgetBand.MEDIUM, None}
        assert all(r.cost_band in low_medium for r in result)

    def test_high_budget_returns_all(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(location="", budget=BudgetBand.HIGH, cuisine="")
        result = pipeline._filter_by_budget(sample_catalog, prefs)
        assert len(result) == len(sample_catalog)


class TestFullPipeline:
    def test_bangalore_italian_high_rating(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(
            location="Bangalore",
            budget=BudgetBand.HIGH,
            cuisine="Italian",
            min_rating=4.2,
        )
        result = pipeline.apply(sample_catalog, prefs)
        assert len(result) == 1
        assert result[0].name == "Italian Place"

    def test_no_match_returns_empty(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(
            location="Chennai",
            budget=BudgetBand.LOW,
            cuisine="Mexican",
            min_rating=4.5,
        )
        result = pipeline.apply(sample_catalog, prefs)
        assert len(result) == 0

    def test_delhi_low_budget(self, sample_catalog):
        pipeline = FilterPipeline()
        prefs = UserPreferences(
            location="Delhi",
            budget=BudgetBand.LOW,
            cuisine="North Indian",
            min_rating=3.5,
        )
        result = pipeline.apply(sample_catalog, prefs)
        assert len(result) == 1
        assert result[0].name == "Budget Dhaba"


class TestShortlistCap:
    def test_cap_limits_results(self, sample_catalog):
        capped = apply_shortlist_cap(sample_catalog, top_n=3)
        assert len(capped) == 3
        assert capped[0].rating >= capped[1].rating >= capped[2].rating

    def test_cap_does_not_expand(self, sample_catalog):
        small = sample_catalog[:2]
        capped = apply_shortlist_cap(small, top_n=10)
        assert len(capped) == 2

    def test_cap_sorts_by_rating_descending(self, sample_catalog):
        capped = apply_shortlist_cap(sample_catalog, top_n=3)
        assert capped[0].rating == 4.9  # Fine Dining
        assert capped[1].rating == 4.5  # Bangalore Biryani
        assert capped[2].rating == 4.3  # Bellandur Cafe
