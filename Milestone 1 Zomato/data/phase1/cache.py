"""Persist and load processed restaurant catalog."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import Settings, get_settings
from data.phase1.exceptions import CacheError
from data.phase1.preprocess import dataframe_to_restaurants, records_to_dataframe
from models import Restaurant

CACHE_FILENAME = "restaurants.parquet"


def cache_path(settings: Settings | None = None) -> Path:
    cfg = settings or get_settings()
    return cfg.data_cache_dir / CACHE_FILENAME


def cache_exists(settings: Settings | None = None) -> bool:
    return cache_path(settings).is_file()


def save_cache(restaurants: list[Restaurant], settings: Settings | None = None) -> Path:
    cfg = settings or get_settings()
    cfg.data_cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_path(cfg)
    df = records_to_dataframe(restaurants)
    df.to_parquet(path, index=False)
    return path


def load_cache(settings: Settings | None = None) -> list[Restaurant]:
    path = cache_path(settings)
    if not path.is_file():
        raise CacheError(f"Cache file not found: {path}")

    try:
        df = pd.read_parquet(path)
    except Exception as exc:
        raise CacheError(
            f"Could not read cache at {path}. Delete the file and reload from Hugging Face."
        ) from exc

    if df.empty:
        raise CacheError(f"Cache file is empty: {path}")

    return dataframe_to_restaurants(df)
