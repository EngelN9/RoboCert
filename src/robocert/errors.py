"""Shared fail-closed validation errors for RoboCert artifacts."""


class ValidationError(ValueError):
    """Raised when an artifact violates the declared RoboCert data contract."""
