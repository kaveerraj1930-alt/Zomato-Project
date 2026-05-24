"""Service layer: orchestrates Phase 1-4 pipeline for the FastAPI backend."""

from __future__ import annotations

import os
from typing import Any

from models.schemas import BudgetBand, Recommendation, Restaurant, Summary, UserPreferences
from data import get_restaurants
from phase3.integration import IntegrationLayer
from phase4.recommendation_engine import RecommendationEngine


class RecommenderService:
    """Orchestrates the full recommendation pipeline (Phases 1-4)."""

    def __init__(self) -> None:
        self._catalog: list[Restaurant] | None = None
        self._integration = IntegrationLayer(shortlist_cap=20)

    def load_catalog(self) -> list[Restaurant]:
        """Lazy-load the restaurant catalog (Phase 1)."""
        if self._catalog is None:
            self._catalog = get_restaurants()
        return self._catalog

    def get_locations(self) -> list[str]:
        """Return sorted list of unique locations from the catalog."""
        catalog = self.load_catalog()
        locations = sorted({r.location for r in catalog if r.location})
        return locations

    def get_cuisines(self) -> list[str]:
        """Return sorted list of unique cuisines from the catalog."""
        catalog = self.load_catalog()
        cuisine_set: set[str] = set()
        for r in catalog:
            for c in r.cuisines:
                if c:
                    cuisine_set.add(c.strip())
        return sorted(cuisine_set)

    def recommend(self, preferences: UserPreferences) -> Summary:
        """
        Run the full recommendation pipeline.

        Steps:
            1. Load catalog (Phase 1)
            2. Filter + build prompt (Phase 3)
            3. LLM ranking + hallucination check (Phase 4)
            4. Return structured Summary
        """
        catalog = self.load_catalog()

        # Phase 3: Integration Layer
        shortlist, prompt = self._integration.process(catalog, preferences)

        if not shortlist:
            return Summary(
                recommendations=[],
                overall_summary="No restaurants match the given criteria.",
            )

        # Phase 4: Recommendation Engine
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            engine = RecommendationEngine(
                groq_api_key=api_key,
                model="llama-3.3-70b-versatile",
                timeout=30,
                max_retries=3,
            )
            try:
                summary = engine.generate_recommendations(prompt, shortlist, use_fallback=True)
                return summary
            except Exception:
                # Fallback on any engine failure
                pass

        # Fallback: rule-based top 5 by rating
        return self._fallback_recommendations(shortlist)

    def _fallback_recommendations(self, shortlist: list[Restaurant]) -> Summary:
        """Generate rule-based fallback recommendations when LLM is unavailable."""
        sorted_restaurants = sorted(shortlist, key=lambda r: r.rating, reverse=True)[:5]
        recommendations: list[Recommendation] = []
        for rank, restaurant in enumerate(sorted_restaurants, start=1):
            explanation = (
                f"Recommended based on rating of {restaurant.rating} and "
                f"cuisines: {', '.join(restaurant.cuisines)}."
            )
            recommendations.append(
                Recommendation(
                    restaurant=restaurant,
                    rank=rank,
                    explanation=explanation,
                )
            )
        return Summary(
            recommendations=recommendations,
            overall_summary=(
                "Recommendations generated using rule-based fallback. "
                "These are top-rated restaurants from your filtered list."
            ),
        )
