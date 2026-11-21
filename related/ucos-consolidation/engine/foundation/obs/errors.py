"""TASK-000006 — Foundation error taxonomy.

A single, stable exception hierarchy for the EC-1 engine. Every error carries a
stable ``code`` and structured ``context`` so failures are auditable (PL-02, IP-12)
and machine-consumable by later stages (Gap Reports in the compiler build on this).
Error context must never contain secret values (SEC-04) — callers pass references.
"""

from __future__ import annotations

from typing import Any


class FoundationError(Exception):
    """Base class for all EC-1 foundation errors.

    Attributes:
        code: stable, category-prefixed identifier (e.g. ``FND-CONFIG-001``).
        message: human-readable description.
        context: structured, non-secret key/value detail.
    """

    code: str = "FND-000"

    def __init__(self, message: str, **context: Any) -> None:
        super().__init__(message)
        self.message = message
        self.context: dict[str, Any] = dict(context)

    def to_dict(self) -> dict[str, Any]:
        """Return an auditable, serialisable representation of the error."""
        return {
            "error": type(self).__name__,
            "code": self.code,
            "message": self.message,
            "context": self.context,
        }

    def __str__(self) -> str:
        if self.context:
            rendered = ", ".join(f"{key}={value!r}" for key, value in self.context.items())
            return f"[{self.code}] {self.message} ({rendered})"
        return f"[{self.code}] {self.message}"


class ConfigurationError(FoundationError):
    """Invalid, missing, or malformed configuration (TASK-000005)."""

    code = "FND-CONFIG-001"


class SecurityViolation(FoundationError):
    """A secure-by-default rule was breached (SEC-01/04, DP-03)."""

    code = "FND-SEC-001"


class ContractViolation(FoundationError):
    """A versioned interface contract was breached (AR-03, PL-05)."""

    code = "FND-CONTRACT-001"


class ObservabilityError(FoundationError):
    """Telemetry / logging could not be produced (PL-02)."""

    code = "FND-OBS-001"


class ValidationError(FoundationError):
    """Structured input failed validation."""

    code = "FND-VALID-001"


__all__ = [
    "FoundationError",
    "ConfigurationError",
    "SecurityViolation",
    "ContractViolation",
    "ObservabilityError",
    "ValidationError",
]
