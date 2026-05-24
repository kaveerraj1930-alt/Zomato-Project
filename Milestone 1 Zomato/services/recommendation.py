"""Recommendation pipeline orchestrator (Phases 1–4 wired in later)."""

from __future__ import annotations

from config import Settings, get_settings
from data import DataLoadError, EmptyDatasetError, get_restaurants, query_restaurants
from models import RecommendationResult, Summary, UserPreferences


def run_recommendation(
    preferences: UserPreferences | None,
    *,
    settings: Settings | None = None,
) -> RecommendationResult:
    """
    End-to-end recommendation entry point.

    Phase 1: loads catalog and counts location/rating matches.
    Later phases add full filters, LLM ranking, and explanations.
    """
    if preferences is None:
        raise ValueError("preferences must be a UserPreferences instance, not None.")

    preferences.validate()
    cfg = settings or get_settings()

    try:
        catalog = get_restaurants()
    except (DataLoadError, EmptyDatasetError) as exc:
        return RecommendationResult(
            preferences=preferences,
            summary=Summary(recommendations=[], overall_summary=None),
            message=str(exc),
            shortlist_size=0,
        )

    matches = query_restaurants(
        catalog,
        location=preferences.location,
        min_rating=preferences.min_rating,
    )

    return RecommendationResult(
        preferences=preferences,
        summary=Summary(
            recommendations=[],
            overall_summary=None,
        ),
        message=(
            f"Loaded {len(catalog):,} restaurants from catalog. "
            f"{len(matches):,} match {preferences.location} with rating ≥ {preferences.min_rating}. "
            f"LLM ranking (Phase 4) will use up to {cfg.shortlist_max} candidates."
        ),
        shortlist_size=len(matches),
    )
