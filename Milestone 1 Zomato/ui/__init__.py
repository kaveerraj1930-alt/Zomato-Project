"""UI package — Phase 0 shell, Phase 2 user input in ui.phase2."""

from ui.phase0 import run_web_app
from ui.phase2 import (
    BUDGET_LABELS,
    PreferenceValidationError,
    PreferenceValidator,
    UIError,
    ValidationResult,
    build_preferences,
    clear_options_cache,
    cli_main,
    collect_preferences_interactive,
    get_cuisine_options,
    get_location_options,
    log_preferences,
    preferences_from_dict,
    preferences_to_json,
    streamlit_main,
    validate_preferences,
)

__all__ = [
    "BUDGET_LABELS",
    "PreferenceValidationError",
    "PreferenceValidator",
    "UIError",
    "ValidationResult",
    "build_preferences",
    "clear_options_cache",
    "cli_main",
    "collect_preferences_interactive",
    "get_cuisine_options",
    "get_location_options",
    "log_preferences",
    "preferences_from_dict",
    "preferences_to_json",
    "run_web_app",
    "streamlit_main",
    "validate_preferences",
]
