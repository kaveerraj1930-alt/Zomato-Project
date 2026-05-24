"""Restaurant catalog: load, preprocess, cache, and serve."""

from __future__ import annotations

from dataclasses import dataclass

from config import Settings, get_settings
from data.phase1.cache import cache_exists, load_cache, save_cache
from data.phase1.exceptions import CacheError, DataLoadError
from data.phase1.loader import assert_required_columns, load_raw_dataframe
from data.phase1.preprocess import preprocess_dataframe
from data.phase1.validate import ValidationReport
from models import Restaurant


@dataclass
class CatalogLoadResult:
    restaurants: list[Restaurant]
    report: ValidationReport
    source: str  # "cache" | "huggingface"


_catalog: list[Restaurant] | None = None
_catalog_report: ValidationReport | None = None
_catalog_source: str | None = None


def load_restaurants(
    *,
    settings: Settings | None = None,
    force_refresh: bool = False,
    use_cache: bool = True,
) -> CatalogLoadResult:
    """
    Load and preprocess the full restaurant catalog.

    Order: memory (if already loaded) → parquet cache → Hugging Face download.
    """
    global _catalog, _catalog_report, _catalog_source

    cfg = settings or get_settings()

    if _catalog is not None and not force_refresh:
        return CatalogLoadResult(
            restaurants=_catalog,
            report=_catalog_report,  # type: ignore[arg-type]
            source=_catalog_source or "memory",
        )

    if use_cache and cache_exists(cfg) and not force_refresh:
        try:
            restaurants = load_cache(cfg)
            report = ValidationReport(
                input_rows=len(restaurants),
                valid_rows=len(restaurants),
                dropped_missing_fields=0,
                dropped_invalid_rating=0,
                duplicates_removed=0,
            )
            _catalog, _catalog_report, _catalog_source = restaurants, report, "cache"
            return CatalogLoadResult(restaurants=restaurants, report=report, source="cache")
        except CacheError:
            pass

    try:
        raw_df = load_raw_dataframe(cfg)
    except DataLoadError:
        if use_cache and cache_exists(cfg):
            restaurants = load_cache(cfg)
            report = ValidationReport(
                input_rows=len(restaurants),
                valid_rows=len(restaurants),
                dropped_missing_fields=0,
                dropped_invalid_rating=0,
                duplicates_removed=0,
            )
            _catalog, _catalog_report, _catalog_source = restaurants, report, "cache"
            return CatalogLoadResult(restaurants=restaurants, report=report, source="cache")
        raise

    assert_required_columns(raw_df)
    restaurants, report = preprocess_dataframe(raw_df)

    if use_cache:
        save_cache(restaurants, cfg)

    _catalog, _catalog_report, _catalog_source = restaurants, report, "huggingface"
    return CatalogLoadResult(restaurants=restaurants, report=report, source="huggingface")


def get_restaurants(*, force_refresh: bool = False) -> list[Restaurant]:
    """Return the catalog, loading on first access."""
    return load_restaurants(force_refresh=force_refresh).restaurants


def clear_catalog_cache() -> None:
    """Clear in-memory catalog (for tests)."""
    global _catalog, _catalog_report, _catalog_source
    _catalog = None
    _catalog_report = None
    _catalog_source = None
