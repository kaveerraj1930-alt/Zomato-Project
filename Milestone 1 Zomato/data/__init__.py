"""Data package — Phase 1 implementation lives in data.phase1."""

from data.phase1 import (
    CacheError,
    CatalogLoadResult,
    DataError,
    DataLoadError,
    EmptyDatasetError,
    ValidationReport,
    clear_catalog_cache,
    count_by_city,
    get_restaurants,
    load_restaurants,
    query_restaurants,
)

__all__ = [
    "CacheError",
    "CatalogLoadResult",
    "DataError",
    "DataLoadError",
    "EmptyDatasetError",
    "ValidationReport",
    "clear_catalog_cache",
    "count_by_city",
    "get_restaurants",
    "load_restaurants",
    "query_restaurants",
]
