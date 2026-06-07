class AppException(Exception):
    """Base exception for the unified backend app."""


class ConfigurationException(AppException):
    """Raised when required application configuration is invalid."""
