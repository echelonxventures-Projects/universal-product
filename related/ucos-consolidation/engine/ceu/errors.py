"""UCOS-CEU-001 — typed, structured failures of the Constitutional Existence layer.

Every error carries machine-readable detail, so a refusal is *evidence* rather than a
message a caller has to string-match. The hierarchy is shallow and one subclass maps to
one constitutional condition that can be violated.
"""

from __future__ import annotations

from typing import Any


class CEUError(Exception):
    """Root of every Constitutional Existence Unit failure."""

    def __init__(self, message: str, **detail: Any) -> None:
        super().__init__(message)
        self.message = message
        self.detail: dict[str, Any] = {k: detail[k] for k in sorted(detail)}

    def to_dict(self) -> dict[str, Any]:
        return {"error": type(self).__name__, "message": self.message, "detail": self.detail}

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        if not self.detail:
            return self.message
        rendered = ", ".join(f"{k}={self.detail[k]!r}" for k in self.detail)
        return f"{self.message} ({rendered})"


class FacultyError(CEUError):
    """A faculty is unregistered, malformed, or would be redefined."""


class KindError(CEUError):
    """An existence kind is unregistered, malformed, superseded, or cyclic."""


class KindRegistrationError(KindError):
    """A kind registration was refused: duplicate key, claimed code, unknown parent."""


class TopologyError(CEUError):
    """A topology is unregistered, or a relationship names one that does not exist."""


class RelationshipError(CEUError):
    """A relationship type or instance is unregistered, malformed, or inadmissible."""


class RelationshipAdmissibilityError(RelationshipError):
    """S-008 — the relationship is refused by its own declared type constraints."""


class TopologyCycleError(RelationshipError):
    """A relationship type declared acyclic was given a cycle."""


class ExistenceError(CEUError):
    """A unit of existence is malformed, unregistered, or duplicated."""


class ExistenceRegistrationError(ExistenceError):
    """Registration was refused: duplicate identity, unknown kind, or superseded kind."""


class PossessionError(CEUError):
    """S-011 — a unit lacks one of the possessions every entity must have."""


class CEUCertificationError(CEUError):
    """Certification was requested over an uncertifiable population."""


__all__ = [
    "CEUError",
    "FacultyError",
    "KindError",
    "KindRegistrationError",
    "TopologyError",
    "RelationshipError",
    "RelationshipAdmissibilityError",
    "TopologyCycleError",
    "ExistenceError",
    "ExistenceRegistrationError",
    "PossessionError",
    "CEUCertificationError",
]
