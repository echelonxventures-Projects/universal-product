"""TASK-000046 — Validation Layer error taxonomy (EPIC-007).

The Validation Layer reuses the EC-1 Foundation error discipline (TASK-000006):
every error is rooted in :class:`FoundationError`, carries a stable,
category-prefixed ``code`` and structured, non-secret ``context`` so failures are
auditable (PL-02, IP-12) and machine-consumable.

The Validation Layer is a *read-only, additive* verifier over already-generated
artifacts: it never mutates a subject, never writes to the certified corpus, and
invents no verdicts (TP-01). A malformed subject, or a strict acceptance gate that
rejects a report, fails loudly with a specific error. The base class is named
:class:`ValidationLayerError` so it never shadows the compiler/foundation
``ValidationError`` types.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class ValidationLayerError(FoundationError):
    """Base class for all Validation Layer errors (EPIC-007)."""

    code = "VAL-000"


class ValidationSubjectError(ValidationLayerError):
    """A validation subject could not be constructed from the supplied input."""

    code = "VAL-SUBJECT-001"


class AcceptanceGateError(ValidationLayerError):
    """A strict acceptance gate rejected a validation report (TASK-000049)."""

    code = "VAL-GATE-001"


__all__ = [
    "ValidationLayerError",
    "ValidationSubjectError",
    "AcceptanceGateError",
]
