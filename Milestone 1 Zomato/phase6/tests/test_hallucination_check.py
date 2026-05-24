"""Phase 6: Tests for the hallucination checker (Phase 4)."""

from __future__ import annotations

from models.schemas import BudgetBand, Recommendation, Restaurant
from phase4.hallucination_check import HallucinationChecker


def _make_restaurant(name: str) -> Restaurant:
    return Restaurant(
        id=name.lower().replace(" ", "_"),
        name=name,
        location="Bangalore",
        cuisines=["Indian"],
        rating=4.0,
        cost_band=BudgetBand.MEDIUM,
    )


def _make_recommendation(name: str, rank: int = 1) -> Recommendation:
    return Recommendation(
        restaurant=_make_restaurant(name),
        rank=rank,
        explanation=f"Great choice: {name}",
    )


class TestHallucinationCheckerVerify:
    def test_all_valid(self):
        shortlist = [
            _make_restaurant("Restaurant A"),
            _make_restaurant("Restaurant B"),
        ]
        recommendations = [
            _make_recommendation("Restaurant A", 1),
            _make_recommendation("Restaurant B", 2),
        ]
        checker = HallucinationChecker()
        is_valid, invalid = checker.verify(recommendations, shortlist)
        assert is_valid is True
        assert invalid == []

    def test_one_invalid(self):
        shortlist = [_make_restaurant("Restaurant A")]
        recommendations = [
            _make_recommendation("Restaurant A", 1),
            _make_recommendation("Fake Restaurant", 2),
        ]
        checker = HallucinationChecker()
        is_valid, invalid = checker.verify(recommendations, shortlist)
        assert is_valid is False
        assert invalid == ["Fake Restaurant"]

    def test_case_insensitive(self):
        shortlist = [_make_restaurant("Restaurant A")]
        recommendations = [_make_recommendation("RESTAURANT A", 1)]
        checker = HallucinationChecker()
        is_valid, invalid = checker.verify(recommendations, shortlist)
        assert is_valid is True
        assert invalid == []

    def test_empty_recommendations(self):
        shortlist = [_make_restaurant("Restaurant A")]
        checker = HallucinationChecker()
        is_valid, invalid = checker.verify([], shortlist)
        assert is_valid is True
        assert invalid == []


class TestHallucinationCheckerFilter:
    def test_filters_out_invalid(self):
        shortlist = [_make_restaurant("Restaurant A")]
        recommendations = [
            _make_recommendation("Restaurant A", 1),
            _make_recommendation("Fake Restaurant", 2),
        ]
        checker = HallucinationChecker()
        valid = checker.filter_valid_recommendations(recommendations, shortlist)
        assert len(valid) == 1
        assert valid[0].restaurant.name == "Restaurant A"

    def test_all_invalid_returns_empty(self):
        shortlist = [_make_restaurant("Restaurant A")]
        recommendations = [_make_recommendation("Fake Restaurant", 1)]
        checker = HallucinationChecker()
        valid = checker.filter_valid_recommendations(recommendations, shortlist)
        assert valid == []

    def test_all_valid_unchanged(self):
        shortlist = [
            _make_restaurant("Restaurant A"),
            _make_restaurant("Restaurant B"),
        ]
        recommendations = [
            _make_recommendation("Restaurant A", 1),
            _make_recommendation("Restaurant B", 2),
        ]
        checker = HallucinationChecker()
        valid = checker.filter_valid_recommendations(recommendations, shortlist)
        assert len(valid) == 2
