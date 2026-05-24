"""Phase 6: Tests for the FastAPI backend endpoints (Phase 5)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_ok(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestLocationsEndpoint:
    def test_locations_returns_list(self, client):
        response = client.get("/api/v1/locations")
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data
        assert isinstance(data["locations"], list)
        assert len(data["locations"]) > 0


class TestCuisinesEndpoint:
    def test_cuisines_returns_list(self, client):
        response = client.get("/api/v1/cuisines")
        assert response.status_code == 200
        data = response.json()
        assert "cuisines" in data
        assert isinstance(data["cuisines"], list)
        assert len(data["cuisines"]) > 0


class TestRecommendationsEndpoint:
    def test_recommendations_success(self, client):
        payload = {
            "location": "Bellandur",
            "budget": "high",
            "cuisine": "",
            "min_rating": 4.0,
        }
        response = client.post("/api/v1/recommendations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) > 0
        for rec in data["recommendations"]:
            assert "rank" in rec
            assert "restaurant" in rec
            assert "explanation" in rec
            assert "name" in rec["restaurant"]
            assert "rating" in rec["restaurant"]

    def test_recommendations_empty_cuisine(self, client):
        """Empty cuisine should be allowed and return results."""
        payload = {
            "location": "Bellandur",
            "budget": "high",
            "cuisine": "",
            "min_rating": 4.0,
        }
        response = client.post("/api/v1/recommendations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) > 0

    def test_recommendations_invalid_budget(self, client):
        payload = {
            "location": "Bangalore",
            "budget": "premium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
        response = client.post("/api/v1/recommendations", json=payload)
        assert response.status_code == 422

    def test_recommendations_missing_location(self, client):
        payload = {
            "location": "",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
        response = client.post("/api/v1/recommendations", json=payload)
        assert response.status_code == 422

    def test_recommendations_no_match(self, client):
        payload = {
            "location": "NonExistentCity12345",
            "budget": "low",
            "cuisine": "Martian",
            "min_rating": 5.0,
        }
        response = client.post("/api/v1/recommendations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["recommendations"] == []
        assert "No restaurants match" in (data.get("overall_summary") or "")

    def test_root_redirects_to_docs(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/docs"
