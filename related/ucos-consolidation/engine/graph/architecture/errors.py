"""UCOS-EPIC-010 (Terminal T2) — Architecture Intelligence error taxonomy.

The Architecture Intelligence Engine is additive engineering code built strictly
**read-only** over the certified Universal Knowledge Graph (UCOS-EPIC-002), which
is itself a read projection of Registry Truth (the ``00-BOOK`` substrate). Nothing
in this package mutates the certified corpus (DP-03).

Every error is rooted in the Knowledge-Graph :class:`~engine.graph.errors.GraphError`
(and thus in the EC-1 Foundation :class:`~engine.foundation.obs.errors.FoundationError`),
carrying a stable, category-prefixed ``code`` and structured, non-secret ``context``
so failures are auditable (PL-02, IP-12) and machine-consumable.
"""

from __future__ import annotations

from engine.graph.errors import GraphError


class ArchitectureIntelligenceError(GraphError):
    """Base class for all Architecture Intelligence errors (UCOS-EPIC-010)."""

    code = "AIG-000"


class UnknownEngineError(ArchitectureIntelligenceError):
    """A named architecture-intelligence engine/report was requested but unknown."""

    code = "AIG-ENGINE-001"


class InsightsWriteError(ArchitectureIntelligenceError):
    """Refused to write an insights/evidence artifact (e.g. under the frozen corpus)."""

    code = "AIG-WRITE-001"


class ReachabilityError(ArchitectureIntelligenceError):
    """A semantic-reachability query referenced an unknown relation family or node."""

    code = "AIG-REACH-001"


__all__ = [
    "ArchitectureIntelligenceError",
    "UnknownEngineError",
    "InsightsWriteError",
    "ReachabilityError",
]
