"""UCOS-EPIC-002 (Terminal T2) — Universal Knowledge Graph error taxonomy.

The Knowledge Graph reuses the EC-1 Foundation error discipline (TASK-000006):
every error is rooted in :class:`FoundationError`, carries a stable, category-
prefixed ``code`` and structured, non-secret ``context`` so failures are auditable
(PL-02, IP-12) and machine-consumable.

These types are additive engineering code built strictly over the read-only
Registry Adapter (EPIC-002). They never modify the certified corpus (DP-03) and
never mutate the frozen Foundation taxonomy — they specialise it for the
knowledge-graph surface.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class GraphError(FoundationError):
    """Base class for all Universal Knowledge Graph errors (UCOS-EPIC-002)."""

    code = "KG-000"


class DuplicateNodeError(GraphError):
    """Two distinct records claimed the same immutable node identifier.

    The graph forbids duplicate nodes (mission requirement: *No duplicate nodes*).
    Re-declaring an identical node is idempotent; re-declaring a *conflicting*
    node under an already-used identifier fails loudly.
    """

    code = "KG-DUP-NODE-001"


class DuplicateEdgeError(GraphError):
    """Two distinct edges claimed the same immutable edge identifier."""

    code = "KG-DUP-EDGE-001"


class ImmutableIdentifierError(GraphError):
    """An identifier violated the immutable-identifier contract.

    Node and edge identifiers are immutable once minted (mission requirement:
    *Immutable identifiers*). This is raised when a node/edge is presented with an
    empty, non-string, or otherwise structurally invalid identifier.
    """

    code = "KG-IMMUTABLE-001"


class NodeNotFoundError(GraphError):
    """A requested node is absent from the graph."""

    code = "KG-NODE-404"


class ProjectionError(GraphError):
    """A named graph projection is unknown or could not be constructed."""

    code = "KG-PROJECTION-001"


class GraphValidationError(GraphError):
    """The graph failed a structural validation invariant."""

    code = "KG-VALID-001"


__all__ = [
    "GraphError",
    "DuplicateNodeError",
    "DuplicateEdgeError",
    "ImmutableIdentifierError",
    "NodeNotFoundError",
    "ProjectionError",
    "GraphValidationError",
]
