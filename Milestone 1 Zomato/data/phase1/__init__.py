"""Phase 1: data ingestion, preprocessing, and catalog queries."""

from data.phase1.exceptions import CacheError, DataLoadError, DataError, EmptyDatasetError
from data.phase1.query import count_by_city, query_restaurants
from data.phase1.repository import CatalogLoadResult, clear_catalog_cache, get_restaurants, load_restaurants
from data.phase1.validate import ValidationReport

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
