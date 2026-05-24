"""Recommendation API router: POST /api/v1/recommendations."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.schemas.api import SummaryResponse, UserPreferencesRequest
from backend.app.services.recommender import RecommenderService
from models.schemas import BudgetBand, UserPreferences

router = APIRouter(prefix="/api/v1", tags=["recommendations"])

# Shared service instance (singleton per process)
_recommender = RecommenderService()


def _map_request_to_preferences(req: UserPreferencesRequest) -> UserPreferences:
    """Convert API request model to internal UserPreferences."""
    band = BudgetBand(req.budget.lower())
    return UserPreferences(
        location=req.location,
        budget=band,
        cuisine=req.cuisine,
        min_rating=req.min_rating,
        extras=req.extras,
    )


def _map_summary_to_response(summary) -> SummaryResponse:
    """Convert internal Summary to API response model."""
    recommendations = []
    for rec in summary.recommendations:
        restaurant = rec.restaurant
        recommendations.append({
            "rank": rec.rank,
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "location": restaurant.location,
                "cuisines": restaurant.cuisines,
                "cost_for_two": restaurant.cost_for_two,
                "cost_band": restaurant.cost_band.value if restaurant.cost_band else None,
                "rating": restaurant.rating,
            },
            "explanation": rec.explanation,
        })
    return SummaryResponse(
        recommendations=recommendations,
        overall_summary=summary.overall_summary,
    )


@router.post("/recommendations", response_model=SummaryResponse)
async def create_recommendations(request: UserPreferencesRequest) -> SummaryResponse:
    """
    Generate restaurant recommendations based on user preferences.

    - **location**: City or area name (e.g., "Bangalore", "Bellandur")
    - **budget**: One of "low", "medium", "high"
    - **cuisine**: Preferred cuisine(s) — comma-separated string or list
    - **min_rating**: Minimum rating from 0.0 to 5.0
    - **extras**: Optional additional filters
    """
    try:
        preferences = _map_request_to_preferences(request)
        preferences.validate()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        summary = _recommender.recommend(preferences)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation engine error: {exc}") from exc

    return _map_summary_to_response(summary)
