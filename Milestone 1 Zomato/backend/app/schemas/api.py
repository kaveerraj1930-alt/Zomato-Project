"""Pydantic v2 request/response models for the FastAPI backend."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"status": "ok"}})
    status: str


class LocationsResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"locations": ["Bangalore", "Delhi", "Mumbai"]}})
    locations: list[str]


class CuisinesResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"cuisines": ["Italian", "Chinese", "Indian"]}})
    cuisines: list[str]


class UserPreferencesRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
            "extras": {},
        }
    })

    location: str = Field(..., min_length=1, description="City or area name")
    budget: str = Field(..., pattern="^(low|medium|high)$", description="Budget band: low, medium, or high")
    cuisine: str | list[str] = Field(default="", description="Preferred cuisine(s)")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Minimum rating (0-5)")
    extras: dict[str, Any] = Field(default_factory=dict, description="Extra filters")


class RestaurantResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "1",
            "name": "Italian Place",
            "location": "Bangalore",
            "cuisines": ["Italian", "Pizza"],
            "cost_for_two": 500,
            "cost_band": "medium",
            "rating": 4.5,
        }
    })

    id: str
    name: str
    location: str
    cuisines: list[str]
    cost_for_two: float | None = None
    cost_band: str | None = None
    rating: float


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "rank": 1,
            "restaurant": {
                "id": "1",
                "name": "Italian Place",
                "location": "Bangalore",
                "cuisines": ["Italian", "Pizza"],
                "cost_for_two": 500,
                "cost_band": "medium",
                "rating": 4.5,
            },
            "explanation": "Top-rated Italian restaurant matching your preferences.",
        }
    })

    rank: int
    restaurant: RestaurantResponse
    explanation: str


class SummaryResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "recommendations": [],
            "overall_summary": "Top recommendations based on your preferences.",
        }
    })

    recommendations: list[RecommendationResponse]
    overall_summary: str | None = None
