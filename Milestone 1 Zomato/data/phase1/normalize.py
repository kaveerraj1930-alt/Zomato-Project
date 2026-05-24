"""Map raw dataset rows to canonical Restaurant objects."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from models import BudgetBand, Restaurant

from data.phase1.columns import (
    HF_ADDRESS,
    HF_AREA,
    HF_CITY,
    HF_COST,
    HF_CUISINES,
    HF_DISH_LIKED,
    HF_LISTED_TYPE,
    HF_NAME,
    HF_RATE,
    HF_REST_TYPE,
    HF_URL,
    HF_VOTES,
)

CITY_ALIASES: dict[str, str] = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "new delhi": "Delhi",
    "delhi": "Delhi",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "hyderabad": "Hyderabad",
    "chennai": "Chennai",
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    "pune": "Pune",
}

# INR approximate cost for two (typical Zomato bands)
COST_BAND_LOW_MAX = 500
COST_BAND_MEDIUM_MAX = 1000


def normalize_city(value: str | None) -> str:
    if not value or not str(value).strip():
        return ""
    cleaned = str(value).strip()
    key = cleaned.lower()
    return CITY_ALIASES.get(key, cleaned.title())


def parse_rating(raw: Any) -> float | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text in {"-", "NEW", "nan", "None"}:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    rating = float(match.group(1))
    if rating > 5.0:
        rating = rating / 10.0 if rating <= 10.0 else 5.0
    if not 0.0 <= rating <= 5.0:
        return None
    return round(rating, 2)


def parse_cost_for_two(raw: Any) -> float | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text in {"-", "nan", "None"}:
        return None
    digits = re.sub(r"[^\d.]", "", text.replace(",", ""))
    if not digits:
        return None
    try:
        cost = float(digits)
    except ValueError:
        return None
    return cost if cost > 0 else None


def cost_to_band(cost: float | None) -> BudgetBand | None:
    if cost is None:
        return None
    if cost <= COST_BAND_LOW_MAX:
        return BudgetBand.LOW
    if cost <= COST_BAND_MEDIUM_MAX:
        return BudgetBand.MEDIUM
    return BudgetBand.HIGH


def parse_cuisines(raw: Any) -> list[str]:
    if raw is None:
        return []
    parts = [c.strip() for c in str(raw).split(",") if c.strip()]
    return parts


def make_restaurant_id(name: str, city: str, area: str) -> str:
    key = f"{name}|{city}|{area}".lower()
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def row_to_restaurant(row: dict[str, Any], *, row_index: int) -> Restaurant | None:
    name = str(row.get(HF_NAME, "")).strip()
    city = normalize_city(row.get(HF_CITY) or row.get(HF_AREA))
    area = str(row.get(HF_AREA, "")).strip()

    if not name or not city:
        return None

    rating = parse_rating(row.get(HF_RATE))
    if rating is None:
        return None

    cost = parse_cost_for_two(row.get(HF_COST))
    cuisines = parse_cuisines(row.get(HF_CUISINES))
    if not cuisines:
        return None

    metadata: dict[str, Any] = {"area": area, "source_row": row_index}
    if row.get(HF_URL):
        metadata["url"] = row[HF_URL]
    if row.get(HF_ADDRESS):
        metadata["address"] = row[HF_ADDRESS]
    if row.get(HF_REST_TYPE):
        metadata["rest_type"] = row[HF_REST_TYPE]
    if row.get(HF_VOTES) is not None:
        metadata["votes"] = row[HF_VOTES]
    if row.get(HF_DISH_LIKED):
        metadata["dish_liked"] = row[HF_DISH_LIKED]
    if row.get(HF_LISTED_TYPE):
        metadata["listed_in_type"] = row[HF_LISTED_TYPE]

    return Restaurant(
        id=make_restaurant_id(name, city, area),
        name=name,
        location=city,
        cuisines=cuisines,
        cost_for_two=cost,
        cost_band=cost_to_band(cost),
        rating=rating,
        metadata=metadata,
    )
