"""EPIC-VAL-002 — Repository Acceptance error taxonomy (Terminal T3).

The Repository Acceptance Engine reuses the EC-1 Foundation error discipline
(TASK-000006): every error is rooted in :class:`FoundationError`, carries a stable,
category-prefixed ``code`` and structured, non-secret ``context`` so failures are
auditable (PL-02, IP-12) and machine-consumable.

The Repository Acceptance Engine is the *final acceptance gate*: an additive,
record-only aggregator that assimilates the acceptance-relevant facts of a
repository / EPIC / feature (discovery, ownership, dependencies, reuse,
implementation, validation, certification, registration, traceability, coverage,
reconciliation, cross-EPIC integration, architecture consistency, health and freeze
readiness) and **aggregates** them into an immutable acceptance certificate — it
invents no verdict (TP-01), mutates no subject, and never writes to the certified
corpus (DP-03). A malformed subject, a tampered (integrity-broken) acceptance
record, or a strict gate that rejects a repository fails loudly with a specific
error. The base class is named :class:`AcceptanceLayerError` so it never shadows the
validation/certification/foundation error hierarchies.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class AcceptanceLayerError(FoundationError):
    """Base class for all Repository Acceptance Engine errors (EPIC-VAL-002)."""

    code = "ACCEPT-000"


class RepositorySubjectError(AcceptanceLayerError):
    """A repository subject could not be assimilated from the supplied facts."""

    code = "ACCEPT-SUBJECT-001"


class AcceptanceRejectedError(AcceptanceLayerError):
    """A strict acceptance gate rejected the repository (fail-closed)."""

    code = "ACCEPT-REJECTED-001"


class AcceptanceIntegrityError(AcceptanceLayerError):
    """An immutable acceptance record failed its content-hash integrity check."""

    code = "ACCEPT-INTEGRITY-001"


__all__ = [
    "AcceptanceLayerError",
    "RepositorySubjectError",
    "AcceptanceRejectedError",
    "AcceptanceIntegrityError",
]
