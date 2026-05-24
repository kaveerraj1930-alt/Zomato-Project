"""Phase 1 CLI: python -m data [--refresh]"""

from __future__ import annotations

import argparse
import sys

from config import get_settings
from data import count_by_city, load_restaurants, query_restaurants


def main() -> int:
    parser = argparse.ArgumentParser(description="Load and inspect the Zomato restaurant catalog.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-download from Hugging Face and rebuild cache",
    )
    parser.add_argument(
        "--city",
        default="Bangalore",
        help="City for sample query (default: Bangalore)",
    )
    parser.add_argument(
        "--min-rating",
        type=float,
        default=4.0,
        help="Minimum rating for sample query (default: 4.0)",
    )
    args = parser.parse_args()

    settings = get_settings()
    print("Phase 1 — Data ingestion")
    print(f"Dataset: {settings.hf_dataset_name}")
    print(f"Cache:   {settings.data_cache_dir}")
    print()

    try:
        result = load_restaurants(settings=settings, force_refresh=args.refresh)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    report = result.report
    restaurants = result.restaurants
    print(f"Source: {result.source}")
    print(f"Input rows:          {report.input_rows:,}")
    print(f"Valid restaurants:   {report.valid_rows:,}")
    print(f"Dropped (missing):   {report.dropped_missing_fields:,}")
    print(f"Dropped (no rating): {report.dropped_invalid_rating:,}")
    print(f"Duplicates removed:  {report.duplicates_removed:,}")
    print()

    top_cities = list(count_by_city(restaurants).items())[:8]
    print("Top cities:")
    for city, count in top_cities:
        print(f"  {city}: {count:,}")
    print()

    sample = query_restaurants(restaurants, location=args.city, min_rating=args.min_rating)
    print(f"Sample query: {args.city} with rating >= {args.min_rating}")
    print(f"Matches: {len(sample):,}")
    for r in sample[:5]:
        cuisines = ", ".join(r.cuisines[:3])
        cost = f"₹{r.cost_for_two:.0f}" if r.cost_for_two else "N/A"
        print(f"  ★ {r.rating}  {r.name}  ({cuisines})  {cost}")
    if len(sample) > 5:
        print(f"  … and {len(sample) - 5:,} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
