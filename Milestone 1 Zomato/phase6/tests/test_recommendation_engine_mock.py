"""Phase 6: Mock LLM integration tests for the recommendation engine (Phase 4)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from models.schemas import BudgetBand, Restaurant, Summary, UserPreferences
from phase3.integration import IntegrationLayer
from phase4.recommendation_engine import RecommendationEngine


def _make_restaurant(name: str, rating: float = 4.0) -> Restaurant:
    return Restaurant(
        id=name.lower().replace(" ", "_"),
        name=name,
        location="Bangalore",
        cuisines=["Indian"],
        rating=rating,
        cost_band=BudgetBand.MEDIUM,
    )


class TestRecommendationEngineWithMockLLM:
    def test_successful_llm_response(self):
        shortlist = [
            _make_restaurant("Restaurant A", 4.5),
            _make_restaurant("Restaurant B", 4.2),
        ]
        mock_response = """```json
{
  "recommendations": [
    {"restaurant_name": "Restaurant A", "rank": 1, "explanation": "Top rated"},
    {"restaurant_name": "Restaurant B", "rank": 2, "explanation": "Good option"}
  ],
  "overall_summary": "Great choices"
}
```"""

        engine = RecommendationEngine(groq_api_key="fake_key")
        with patch.object(
            engine.groq_client, "generate_completion", return_value=mock_response
        ):
            summary = engine.generate_recommendations("prompt", shortlist, use_fallback=False)

        assert isinstance(summary, Summary)
        assert len(summary.recommendations) == 2
        assert summary.recommendations[0].rank == 1
        assert summary.recommendations[0].restaurant.name == "Restaurant A"
        assert summary.overall_summary == "Great choices"

    def test_hallucinated_name_filtered_out(self):
        shortlist = [_make_restaurant("Restaurant A", 4.5)]
        mock_response = """```json
{
  "recommendations": [
    {"restaurant_name": "Restaurant A", "rank": 1, "explanation": "Top rated"},
    {"restaurant_name": "Fake Restaurant", "rank": 2, "explanation": "Does not exist"}
  ]
}
```"""

        engine = RecommendationEngine(groq_api_key="fake_key")
        with patch.object(
            engine.groq_client, "generate_completion", return_value=mock_response
        ):
            summary = engine.generate_recommendations("prompt", shortlist, use_fallback=False)

        assert len(summary.recommendations) == 1
        assert summary.recommendations[0].restaurant.name == "Restaurant A"

    def test_invalid_json_uses_fallback(self):
        shortlist = [
            _make_restaurant("Restaurant A", 4.5),
            _make_restaurant("Restaurant B", 4.2),
        ]

        engine = RecommendationEngine(groq_api_key="fake_key")
        with patch.object(
            engine.groq_client, "generate_completion", return_value="not valid json at all"
        ):
            summary = engine.generate_recommendations("prompt", shortlist, use_fallback=True)

        assert len(summary.recommendations) == 2
        assert summary.recommendations[0].restaurant.name == "Restaurant A"
        assert "fallback" in summary.overall_summary.lower()

    def test_llm_exception_uses_fallback(self):
        shortlist = [_make_restaurant("Restaurant A", 4.5)]

        engine = RecommendationEngine(groq_api_key="fake_key")
        with patch.object(
            engine.groq_client, "generate_completion", side_effect=Exception("API down")
        ):
            summary = engine.generate_recommendations("prompt", shortlist, use_fallback=True)

        assert len(summary.recommendations) == 1
        assert summary.recommendations[0].restaurant.name == "Restaurant A"

    def test_empty_shortlist_returns_empty_summary(self):
        engine = RecommendationEngine(groq_api_key="fake_key")
        summary = engine.generate_recommendations("prompt", [], use_fallback=False)
        assert summary.recommendations == []
        assert "No restaurants available" in summary.overall_summary


class TestIntegrationLayer:
    def test_integration_produces_shortlist_and_prompt(self):
        catalog = [
            _make_restaurant("A", 4.5),
            _make_restaurant("B", 4.2),
            _make_restaurant("C", 3.5),
        ]
        prefs = UserPreferences(
            location="Bangalore",
            budget=BudgetBand.MEDIUM,
            cuisine="Indian",
            min_rating=4.0,
        )
        integration = IntegrationLayer(shortlist_cap=20)
        shortlist, prompt = integration.process(catalog, prefs)

        assert len(shortlist) == 2
        assert all(r.rating >= 4.0 for r in shortlist)
        assert "Bangalore" in prompt
        assert "Indian" in prompt
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_integration_has_matches(self):
        catalog = [_make_restaurant("A", 4.5)]
        prefs = UserPreferences(
            location="Bangalore",
            budget=BudgetBand.MEDIUM,
            cuisine="Indian",
            min_rating=4.0,
        )
        integration = IntegrationLayer()
        assert integration.has_matches(catalog, prefs) is True

    def test_integration_no_matches(self):
        catalog = [_make_restaurant("A", 4.5)]
        prefs = UserPreferences(
            location="Chennai",
            budget=BudgetBand.LOW,
            cuisine="Martian",
            min_rating=5.0,
        )
        integration = IntegrationLayer()
        assert integration.has_matches(catalog, prefs) is False
