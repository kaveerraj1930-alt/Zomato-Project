"""Phase 1 data layer tests (no Hugging Face network required)."""

from __future__ import annotations

import pandas as pd
import pytest

from data.phase1.columns import HF_AREA, HF_CITY, HF_COST, HF_CUISINES, HF_NAME, HF_RATE
from data.phase1.exceptions import EmptyDatasetError
from data.phase1.normalize import (
    normalize_city,
    parse_cost_for_two,
    parse_cuisines,
    parse_rating,
    row_to_restaurant,
)
from data.phase1.preprocess import preprocess_dataframe, records_to_dataframe, dataframe_to_restaurants
from data.phase1.query import query_restaurants
from data.phase1.repository import clear_catalog_cache
from data.phase1.validate import dedupe_restaurants
from models import BudgetBand, Restaurant


def _sample_row(**overrides):
    base = {
        HF_NAME: "The Italian Place",
        HF_AREA: "Indiranagar",
        HF_CITY: "Bangalore",
        HF_CUISINES: "Italian, Pizza",
        HF_RATE: "4.5/5",
        HF_COST: "800",
    }
    base.update(overrides)
    return base


def test_parse_rating_formats():
    assert parse_rating("4.1/5") == 4.1
    assert parse_rating("NEW") is None
    assert parse_rating("-") is None


def test_parse_cost_formats():
    assert parse_cost_for_two("1,200") == 1200.0
    assert parse_cost_for_two("-") is None


def test_normalize_city_aliases():
    assert normalize_city("bengaluru") == "Bangalore"
    assert normalize_city("New Delhi") == "Delhi"


def test_row_to_restaurant():
    r = row_to_restaurant(_sample_row(), row_index=0)
    assert r is not None
    assert r.name == "The Italian Place"
    assert r.location == "Bangalore"
    assert r.cuisines == ["Italian", "Pizza"]
    assert r.rating == 4.5
    assert r.cost_for_two == 800.0
    assert r.cost_band == BudgetBand.MEDIUM


def test_preprocess_dataframe_and_query():
    df = pd.DataFrame(
        [
            _sample_row(),
            _sample_row(**{HF_NAME: "Spice Hub", HF_CUISINES: "North Indian", HF_RATE: "3.8/5"}),
            _sample_row(**{HF_NAME: "Bad Row", HF_RATE: "NEW"}),
            _sample_row(**{HF_NAME: "Delhi Diner", HF_CITY: "Delhi", HF_RATE: "4.2/5"}),
        ]
    )
    restaurants, report = preprocess_dataframe(df)
    assert report.valid_rows == 3
    assert report.dropped_invalid_rating == 1

    matches = query_restaurants(restaurants, location="Bangalore", min_rating=4.0)
    assert len(matches) == 1
    assert matches[0].name == "The Italian Place"


def test_dedupe_keeps_higher_rating():
    low = Restaurant(
        id="1",
        name="Cafe X",
        location="Pune",
        cuisines=["Cafe"],
        rating=3.5,
    )
    high = Restaurant(
        id="2",
        name="Cafe X",
        location="Pune",
        cuisines=["Cafe"],
        rating=4.5,
    )
    deduped, removed = dedupe_restaurants([low, high])
    assert removed == 1
    assert deduped[0].rating == 4.5


def test_cache_roundtrip(tmp_path, monkeypatch):
    from config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("DATA_CACHE_DIR", str(tmp_path))

    from data.phase1.cache import load_cache, save_cache

    original = [
        Restaurant(
            id="abc",
            name="Test Kitchen",
            location="Mumbai",
            cuisines=["Chinese"],
            rating=4.0,
            cost_for_two=600.0,
            cost_band=BudgetBand.MEDIUM,
        )
    ]
    save_cache(original)
    loaded = load_cache()
    assert len(loaded) == 1
    assert loaded[0].name == "Test Kitchen"

    get_settings.cache_clear()
    clear_catalog_cache()


def test_empty_dataset_raises():
    df = pd.DataFrame([_sample_row(**{HF_RATE: "NEW"})])
    with pytest.raises(EmptyDatasetError):
        preprocess_dataframe(df)


def test_records_dataframe_roundtrip():
    restaurants, _ = preprocess_dataframe(pd.DataFrame([_sample_row()]))
    df = records_to_dataframe(restaurants)
    restored = dataframe_to_restaurants(df)
    assert restored[0].name == restaurants[0].name
    assert restored[0].cuisines == restaurants[0].cuisines
