"""Phase 2: user input validation, forms, CLI, and Streamlit app."""

from ui.phase2.cli import collect_preferences_interactive, main as cli_main
from ui.phase2.constants import BUDGET_LABELS
from ui.phase2.exceptions import PreferenceValidationError, UIError
from ui.phase2.options import clear_options_cache, get_cuisine_options, get_location_options
from ui.phase2.preferences_form import build_preferences
from ui.phase2.serializer import log_preferences, preferences_from_dict, preferences_to_json
from ui.phase2.streamlit_app import main as streamlit_main
from ui.phase2.validator import PreferenceValidator, ValidationResult, validate_preferences

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
    "streamlit_main",
    "validate_preferences",
]
