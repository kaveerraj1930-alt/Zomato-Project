"""Metadata API router: health, locations, cuisines."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.schemas.api import CuisinesResponse, HealthResponse, LocationsResponse
from backend.app.services.recommender import RecommenderService

router = APIRouter(prefix="/api/v1", tags=["metadata"])

# Shared service instance
_recommender = RecommenderService()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint for load balancers and monitoring."""
    return HealthResponse(status="ok")


@router.get("/locations", response_model=LocationsResponse)
async def list_locations() -> LocationsResponse:
    """Return all unique locations available in the restaurant catalog."""
    try:
        locations = _recommender.get_locations()
        return LocationsResponse(locations=locations)
    except Exception as exc:
        return LocationsResponse(locations=[])


@router.get("/cuisines", response_model=CuisinesResponse)
async def list_cuisines() -> CuisinesResponse:
    """Return all unique cuisines available in the restaurant catalog."""
    try:
        cuisines = _recommender.get_cuisines()
        return CuisinesResponse(cuisines=cuisines)
    except Exception as exc:
        return CuisinesResponse(cuisines=[])
