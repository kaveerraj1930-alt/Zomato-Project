"""Schema validation and deduplication for restaurant records."""

from __future__ import annotations

from dataclasses import dataclass

from models import Restaurant

from data.phase1.exceptions import EmptyDatasetError


@dataclass
class ValidationReport:
    input_rows: int
    valid_rows: int
    dropped_missing_fields: int
    dropped_invalid_rating: int
    duplicates_removed: int

    @property
    def dropped_total(self) -> int:
        return self.input_rows - self.valid_rows


def dedupe_restaurants(restaurants: list[Restaurant]) -> tuple[list[Restaurant], int]:
    """Keep the highest-rated row per (name, location city)."""
    best: dict[tuple[str, str], Restaurant] = {}
    for r in restaurants:
        key = (r.name.lower(), r.location.lower())
        existing = best.get(key)
        if existing is None or r.rating > existing.rating:
            best[key] = r
    removed = len(restaurants) - len(best)
    return list(best.values()), removed


def validate_catalog(
    restaurants: list[Restaurant],
    *,
    input_rows: int,
    dropped_missing_fields: int,
    dropped_invalid_rating: int,
) -> tuple[list[Restaurant], ValidationReport]:
    deduped, dupes_removed = dedupe_restaurants(restaurants)

    report = ValidationReport(
        input_rows=input_rows,
        valid_rows=len(deduped),
        dropped_missing_fields=dropped_missing_fields,
        dropped_invalid_rating=dropped_invalid_rating,
        duplicates_removed=dupes_removed,
    )

    if not deduped:
        raise EmptyDatasetError(
            "No valid restaurants after preprocessing. "
            f"Input rows: {input_rows}, dropped: {report.dropped_total}."
        )

    return deduped, report
