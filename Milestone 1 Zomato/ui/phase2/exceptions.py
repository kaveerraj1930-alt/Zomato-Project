"""User input layer errors (Phase 2)."""


class UIError(Exception):
    """Base error for the UI package."""


class PreferenceValidationError(UIError):
    """One or more preference fields failed validation."""

    def __init__(self, messages: list[str]) -> None:
        self.messages = messages
        text = "; ".join(messages) if len(messages) > 1 else messages[0]
        super().__init__(text)
