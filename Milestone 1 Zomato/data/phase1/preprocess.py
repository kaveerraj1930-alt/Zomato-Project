"""Clean and normalize a raw Hugging Face dataset into Restaurant records."""

from __future__ import annotations

from typing import Any

import pandas as pd

from models import Restaurant

from data.phase1.columns import HF_AREA, HF_CITY, HF_NAME, HF_RATE, REQUIRED_SOURCE_COLUMNS
from data.phase1.normalize import normalize_city, parse_rating, row_to_restaurant
from data.phase1.validate import ValidationReport, validate_catalog


def _missing_columns(df: pd.DataFrame) -> list[str]:
    lower_cols = {c.lower(): c for c in df.columns}
    missing: list[str] = []
    for col in REQUIRED_SOURCE_COLUMNS:
        if col.lower() not in lower_cols and col not in df.columns:
            missing.append(col)
    return missing


def preprocess_dataframe(df: pd.DataFrame) -> tuple[list[Restaurant], ValidationReport]:
    missing = _missing_columns(df)
    if missing:
        raise ValueError(f"Dataset missing required columns: {', '.join(missing)}")

    input_rows = len(df)
    restaurants: list[Restaurant] = []
    dropped_missing = 0
    dropped_rating = 0

    for idx, row in df.iterrows():
        record = row.to_dict()
        name = str(record.get(HF_NAME, "")).strip()
        city = normalize_city(record.get(HF_CITY) or record.get(HF_AREA))

        if not name or not city:
            dropped_missing += 1
            continue
        if parse_rating(record.get(HF_RATE)) is None:
            dropped_rating += 1
            continue

        restaurant = row_to_restaurant(record, row_index=int(idx))
        if restaurant is None:
            dropped_missing += 1
            continue
        restaurants.append(restaurant)

    return validate_catalog(
        restaurants,
        input_rows=input_rows,
        dropped_missing_fields=dropped_missing,
        dropped_invalid_rating=dropped_rating,
    )


def records_to_dataframe(restaurants: list[Restaurant]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for r in restaurants:
        rows.append(
            {
                "id": r.id,
                "name": r.name,
                "location": r.location,
                "cuisines": "|".join(r.cuisines),
                "cost_for_two": r.cost_for_two,
                "cost_band": r.cost_band.value if r.cost_band else None,
                "rating": r.rating,
                "area": r.metadata.get("area"),
                "url": r.metadata.get("url"),
            }
        )
    return pd.DataFrame(rows)


def dataframe_to_restaurants(df: pd.DataFrame) -> list[Restaurant]:
    restaurants: list[Restaurant] = []
    for _, row in df.iterrows():
        cuisines = [c.strip() for c in str(row["cuisines"]).split("|") if c.strip()]
        cost_band = None
        if pd.notna(row.get("cost_band")) and str(row["cost_band"]).strip():
            from models import BudgetBand

            cost_band = BudgetBand(str(row["cost_band"]))
        metadata: dict[str, Any] = {}
        if pd.notna(row.get("area")):
            metadata["area"] = row["area"]
        if pd.notna(row.get("url")):
            metadata["url"] = row["url"]

        cost = row["cost_for_two"]
        restaurants.append(
            Restaurant(
                id=str(row["id"]),
                name=str(row["name"]),
                location=str(row["location"]),
                cuisines=cuisines,
                cost_for_two=float(cost) if pd.notna(cost) else None,
                cost_band=cost_band,
                rating=float(row["rating"]),
                metadata=metadata,
            )
        )
    return restaurants
