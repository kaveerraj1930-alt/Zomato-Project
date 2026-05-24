"""Data layer errors (Phase 1)."""


class DataError(Exception):
    """Base error for data ingestion."""


class DataLoadError(DataError):
    """Failed to download or read the dataset."""


class EmptyDatasetError(DataError):
    """Dataset loaded but contains no usable rows."""


class CacheError(DataError):
    """Processed cache file is missing or corrupt."""
