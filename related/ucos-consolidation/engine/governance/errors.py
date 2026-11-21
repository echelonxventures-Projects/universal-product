"""EPIC-VAL-003 — Repository Governance Pipeline error taxonomy (Terminal T3).

The Repository Governance Pipeline reuses the EC-1 Foundation error discipline
(TASK-000006): every error is rooted in :class:`FoundationError`, carries a stable,
category-prefixed ``code`` and structured, non-secret ``context`` so failures are
auditable (PL-02, IP-12) and machine-consumable.

The pipeline is the *end-to-end constitutional governance flow*: an additive,
record-only orchestrator that composes the already-built Validation Layer
(EPIC-007), Certification Layer (EPIC-008), and Repository Acceptance Engine
(EPIC-VAL-002) into one deterministic, fail-closed determination. It invents no
verdict (TP-01) — it only sequences and aggregates the underlying engines — mutates
no subject, and never writes to the certified corpus (DP-03). A malformed input, a
tampered (integrity-broken) governance report, or a strict gate that refuses a
not-governed repository fails loudly with a specific error. The base class is named
:class:`GovernanceLayerError` so it never shadows the
validation/certification/acceptance/foundation error hierarchies.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class GovernanceLayerError(FoundationError):
    """Base class for all Repository Governance Pipeline errors (EPIC-VAL-003)."""

    code = "GOV-000"


class GovernanceInputError(GovernanceLayerError):
    """A governance input could not be assimilated from the supplied facts."""

    code = "GOV-INPUT-001"


class GovernanceRejectedError(GovernanceLayerError):
    """A strict governance gate refused a not-governed repository (fail-closed)."""

    code = "GOV-REJECTED-001"


class GovernanceIntegrityError(GovernanceLayerError):
    """An immutable governance report failed its content-hash integrity check."""

    code = "GOV-INTEGRITY-001"


__all__ = [
    "GovernanceLayerError",
    "GovernanceInputError",
    "GovernanceRejectedError",
    "GovernanceIntegrityError",
]
