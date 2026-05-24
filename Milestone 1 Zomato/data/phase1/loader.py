"""Download the Zomato dataset from Hugging Face."""

from __future__ import annotations

import time
import pandas as pd

from config import Settings, get_settings
from data.phase1.exceptions import DataLoadError

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 2.0


def load_raw_dataframe(settings: Settings | None = None) -> pd.DataFrame:
    """
    Load the raw HF dataset as a pandas DataFrame.

    Raises DataLoadError on network or repository failures.
    """
    cfg = settings or get_settings()
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            from datasets import load_dataset

            # Load only a sample of the dataset for faster startup on Render
            dataset = load_dataset(cfg.hf_dataset_name, split="train")
            # Take first 1000 rows for faster loading
            df = dataset.to_pandas()
            if len(df) > 1000:
                df = df.head(1000)
            return df
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))

    raise DataLoadError(
        f"Could not load dataset '{cfg.hf_dataset_name}' from Hugging Face. "
        f"Check your connection or use a local cache. Details: {last_error}"
    ) from last_error


def assert_required_columns(df: pd.DataFrame) -> None:
    """Raise if the HF schema changed."""
    from data.phase1.columns import HF_CUISINES, HF_NAME, HF_RATE

    required = {HF_NAME, HF_CUISINES, HF_RATE}
    present = set(df.columns)
    missing = [c for c in required if c not in present]
    if missing:
        raise DataLoadError(
            f"Unexpected dataset schema. Missing columns: {missing}. "
            f"Found: {sorted(present)[:20]}..."
        )
