"""Query helpers on the in-memory restaurant catalog (no LLM)."""

from __future__ import annotations

from models import Restaurant

from data.phase1.normalize import normalize_city


def matches_location(restaurant: Restaurant, location: str) -> bool:
    return restaurant.location.lower() == normalize_city(location).lower()


def matches_min_rating(restaurant: Restaurant, min_rating: float) -> bool:
    return restaurant.rating >= min_rating


def query_restaurants(
    restaurants: list[Restaurant],
    *,
    location: str,
    min_rating: float = 0.0,
) -> list[Restaurant]:
    """
    Sample query from Phase 1 exit criteria.

    Example: restaurants in Bangalore with rating >= 4.0
    """
    city = normalize_city(location)
    if not city:
        return []

    results = [
        r
        for r in restaurants
        if matches_location(r, city) and matches_min_rating(r, min_rating)
    ]
    return sorted(results, key=lambda r: (-r.rating, r.name.lower()))


def count_by_city(restaurants: list[Restaurant]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in restaurants:
        counts[r.location] = counts.get(r.location, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: (-x[1], x[0])))
