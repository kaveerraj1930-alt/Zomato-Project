"""Form options derived from the restaurant catalog when available."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from config import get_settings

# Fallback when cache is not built yet
DEFAULT_LOCATIONS = [
    "Btm",
    "Koramangala 5Th Block",
    "Indiranagar",
    "Jayanagar",
    "Jp Nagar",
    "Delhi",
    "Mumbai",
    "Bangalore",
]

DEFAULT_CUISINES = [
    "North Indian",
    "Chinese",
    "South Indian",
    "Fast Food",
    "Italian",
    "Cafe",
    "Bakery",
    "Mughlai",
    "Continental",
    "Desserts",
    "Mexican",
    "Thai",
]


def _cache_path() -> Path:
    return get_settings().data_cache_dir / "restaurants.parquet"


@lru_cache(maxsize=1)
def get_location_options(*, limit: int = 80) -> list[str]:
    """Top localities from the processed catalog (by restaurant count)."""
    path = _cache_path()
    if not path.is_file():
        return DEFAULT_LOCATIONS.copy()

    try:
        import pandas as pd

        df = pd.read_parquet(path, columns=["location"])
        ranked = df["location"].value_counts().head(limit)
        return ranked.index.astype(str).tolist()
    except Exception:
        return DEFAULT_LOCATIONS.copy()


@lru_cache(maxsize=1)
def get_cuisine_options(*, limit: int = 40) -> list[str]:
    """Most common cuisines in the catalog."""
    path = _cache_path()
    if not path.is_file():
        return DEFAULT_CUISINES.copy()

    try:
        import pandas as pd

        df = pd.read_parquet(path, columns=["cuisines"])
        counts: dict[str, int] = {}
        for raw in df["cuisines"].dropna():
            for part in str(raw).split("|"):
                name = part.strip()
                if name:
                    counts[name] = counts.get(name, 0) + 1
        ranked = sorted(counts, key=lambda k: (-counts[k], k.lower()))
        return ranked[:limit] if ranked else DEFAULT_CUISINES.copy()
    except Exception:
        return DEFAULT_CUISINES.copy()


def clear_options_cache() -> None:
    get_location_options.cache_clear()
    get_cuisine_options.cache_clear()
