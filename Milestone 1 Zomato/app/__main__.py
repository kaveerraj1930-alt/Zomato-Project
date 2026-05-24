"""Entry point: python -m app"""

from __future__ import annotations

import json
import sys

from config import get_settings
from models import BudgetBand, UserPreferences
from services import run_recommendation


def main() -> int:
    settings = get_settings()
    print("Zomato Recommendation Service (Phase 0) — v0.1.0")
    print(f"Project root: {settings.project_root}")
    print(f"Dataset: {settings.hf_dataset_name}")
    print(f"Cache dir: {settings.data_cache_dir}")
    print()
    print("Primary interface: web UI")
    print("  python -m ui")
    print("  streamlit run ui/streamlit_app.py")
    print()

    demo_preferences = UserPreferences(
        location="Bangalore",
        budget=BudgetBand.MEDIUM,
        cuisine="Italian",
        min_rating=4.0,
        extras={"family_friendly": True},
    )

    try:
        result = run_recommendation(demo_preferences, settings=settings)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Demo preferences:")
    print(json.dumps(demo_preferences.to_dict(), indent=2))
    print()
    print("Pipeline result:")
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
