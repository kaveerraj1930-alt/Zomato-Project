"""CLI preference collection (Phase 2 input surface)."""

from __future__ import annotations

import argparse
import json
import sys

from ui.phase2.exceptions import PreferenceValidationError
from ui.phase2.options import get_cuisine_options, get_location_options
from ui.phase2.preferences_form import BUDGET_LABELS, build_preferences
from ui.phase2.serializer import log_preferences, preferences_to_json


def _prompt_choice(label: str, options: list[str], *, default_index: int = 0) -> str:
    print(f"\n{label}")
    for i, opt in enumerate(options, start=1):
        marker = " (default)" if i - 1 == default_index else ""
        print(f"  {i}. {opt}{marker}")
    while True:
        raw = input(f"Enter 1–{len(options)} or press Enter for default: ").strip()
        if not raw:
            return options[default_index]
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
        if raw in options:
            return raw
        print("Invalid choice. Try again.")


def _prompt_float(label: str, *, default: float) -> float:
    raw = input(f"{label} [{default}]: ").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        print("Please enter a number.")
        return _prompt_float(label, default=default)


def collect_preferences_interactive() -> dict:
    """Walk the user through preference prompts."""
    locations = get_location_options()
    cuisines = get_cuisine_options()
    budgets = list(BUDGET_LABELS.keys())

    location = _prompt_choice("Select location (locality / city in dataset)", locations)
    budget_label = _prompt_choice("Select budget", budgets, default_index=1)
    cuisine = _prompt_choice("Select cuisine", cuisines)
    min_rating = _prompt_float("Minimum rating (0–5)", default=4.0)

    family = input("Family-friendly? [y/N]: ").strip().lower() in {"y", "yes"}
    quick = input("Quick service? [y/N]: ").strip().lower() in {"y", "yes"}

    return {
        "location": location,
        "budget_label": budget_label,
        "cuisine": cuisine,
        "min_rating": min_rating,
        "family_friendly": family,
        "quick_service": quick,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect user preferences via CLI.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print validated preferences as JSON only",
    )
    parser.add_argument("--location", help="Skip prompts: location")
    parser.add_argument("--budget", choices=list(BUDGET_LABELS.keys()), help="Skip prompts: budget")
    parser.add_argument("--cuisine", help="Skip prompts: cuisine")
    parser.add_argument("--min-rating", type=float, default=4.0, help="Minimum rating")
    args = parser.parse_args(argv)

    try:
        if args.location and args.budget and args.cuisine:
            preferences = build_preferences(
                location=args.location,
                budget_label=args.budget,
                cuisine=args.cuisine,
                min_rating=args.min_rating,
            )
        else:
            raw = collect_preferences_interactive()
            preferences = build_preferences(**raw)
    except PreferenceValidationError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        for msg in exc.messages:
            print(f"  - {msg}", file=sys.stderr)
        return 1

    log_preferences(preferences)

    if args.json:
        print(preferences_to_json(preferences, indent=2))
    else:
        print("\nValidated preferences:")
        print(preferences_to_json(preferences, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
