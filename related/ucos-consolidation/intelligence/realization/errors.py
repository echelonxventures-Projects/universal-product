"""URI-000001 — Realization Intelligence error taxonomy.

Rooted in the EC-1 Foundation error discipline (TASK-000006): every error carries a
stable, category-prefixed ``code`` and structured, non-secret ``context`` so failures
are auditable (PL-02, IP-12) and machine-consumable by the governance layer.

The taxonomy mirrors the realization pipeline, so a failure names the stage that
refused to proceed: intake → planning → composition → generation → implementation →
governance → traceability → evidence.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class RealizationError(FoundationError):
    """Base class for every Realization Intelligence error (URI-000001)."""

    code = "URI-000"


class KnowledgeIntakeError(RealizationError):
    """Canonical knowledge could not be located, read, or integrity-verified."""

    code = "URI-INTAKE-001"


class PlanningError(RealizationError):
    """A realization plan could not be derived (unresolvable or cyclic dependency)."""

    code = "URI-PLAN-001"


class CompositionError(RealizationError):
    """Plan steps could not be composed (conflicting or duplicated knowledge)."""

    code = "URI-COMPOSE-001"


class GenerationError(RealizationError):
    """A generator failed, or two generators claimed the same output path."""

    code = "URI-GENERATE-001"


class ImplementationError(RealizationError):
    """Materialization failed, or written bytes did not match the artifact seal."""

    code = "URI-IMPLEMENT-001"


class FrozenSurfaceError(ImplementationError):
    """A generated artifact targeted the frozen corpus (DP-03 / UCKO-PRIN-0002)."""

    code = "URI-FROZEN-001"


class GovernanceRejectedError(RealizationError):
    """A fail-closed realization gate refused the run; nothing was materialized."""

    code = "URI-REJECTED-001"


class TraceabilityError(RealizationError):
    """Traceability closure failed: an orphan artifact or an unrealized obligation."""

    code = "URI-TRACE-001"


class DeterminismError(RealizationError):
    """Regeneration was not byte-identical (UCKO-PRIN-0005 violated)."""

    code = "URI-DETERMINISM-001"


class EvidenceError(RealizationError):
    """The consolidated evidence bundle could not be produced (TRACK-001)."""

    code = "URI-EVIDENCE-001"


__all__ = [
    "RealizationError",
    "KnowledgeIntakeError",
    "PlanningError",
    "CompositionError",
    "GenerationError",
    "ImplementationError",
    "FrozenSurfaceError",
    "GovernanceRejectedError",
    "TraceabilityError",
    "DeterminismError",
    "EvidenceError",
]
