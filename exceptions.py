class RIAException(Exception):
    """Base exception for RIA application."""

class SourceError(RIAException):
    """Raised when fetching or parsing external scientific literature fails."""

class AIProviderError(RIAException):
    """Raised when local or cloud AI inference encounters an error."""

class ValidationError(RIAException):
    """Raised when input or structured schema validation fails."""

class DatabaseError(RIAException):
    """Raised on SQLite persistence errors."""
