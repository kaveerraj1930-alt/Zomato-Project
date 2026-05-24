"""Shared application errors."""


class AppError(Exception):
    """Base error for the recommendation service."""


class ConfigurationError(AppError):
    """Invalid or missing configuration."""


class ValidationError(AppError):
    """Invalid user input or schema data."""
