"""UCOS-NUC-001 — typed, structured failures of the Nucleus Ownership Authority.

Every error carries machine-readable detail so a refusal is *evidence*, not a
message. The hierarchy is deliberately shallow: one root the callers catch and one
subclass per constitutional clause that can be violated, so a caller never has to
string-match a reason.
"""

from __future__ import annotations

from typing import Any


class NucleusError(Exception):
    """Root of every Nucleus Ownership Authority failure."""

    def __init__(self, message: str, **detail: Any) -> None:
        super().__init__(message)
        self.message = message
        self.detail: dict[str, Any] = {k: detail[k] for k in sorted(detail)}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": type(self).__name__,
            "message": self.message,
            "detail": self.detail,
        }

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        if not self.detail:
            return self.message
        rendered = ", ".join(f"{k}={self.detail[k]!r}" for k in self.detail)
        return f"{self.message} ({rendered})"


class StructuralValidationError(NucleusError):
    """A declaration is not well-formed (missing, empty or wrongly typed field)."""


class RegistrationError(NucleusError):
    """A registration was refused: duplicate identity, or unknown referent."""


class OwnershipViolation(NucleusError):
    """AC-004 / NL-01…NL-05 — ownership does not resolve to exactly one nucleus."""


class LayerOwnershipViolation(OwnershipViolation):
    """NL-02 — a layer attempted to own a capability. Layers organise; they own nothing."""


class CompositionOwnershipViolation(OwnershipViolation):
    """NL-05 — a composition attempted to own a capability instead of selecting nuclei."""


class MisclassificationError(NucleusError):
    """NL-06 — a subject that is a composition was declared as a nucleus (or vice versa)."""


class LifecycleError(NucleusError):
    """AC-008 — the constitutional lifecycle was executed out of order or incompletely."""


class EvolutionError(NucleusError):
    """AC-009 — an evolution did not preserve lineage, or did not register."""


class CertificationError(NucleusError):
    """AC-002 / D-21 — certification was requested over an uncertifiable subject."""


class ContextBindingViolation(NucleusError):
    """AC-006 / AC-007 — an entity acted without, or against, a resolved context.

    Raised where a context binding is *required* and is absent, incomplete, or would
    silently change: an unbound population asked to certify, a partially resolved frame
    offered as a reality, or a registry already bound to one frame being rebound to
    another. Each is the same failure — a claim about a reality nobody named.
    """


__all__ = [
    "ContextBindingViolation",
    "NucleusError",
    "StructuralValidationError",
    "RegistrationError",
    "OwnershipViolation",
    "LayerOwnershipViolation",
    "CompositionOwnershipViolation",
    "MisclassificationError",
    "LifecycleError",
    "EvolutionError",
    "CertificationError",
]
