"""UCKP Layer Zero — error taxonomy.

Layer Zero reuses the EC-1 Foundation error discipline (TASK-000006): every error
is rooted in :class:`FoundationError`, carries a stable category-prefixed ``code``
and structured, non-secret ``context`` so every constitutional refusal is auditable
(PL-02, IP-12) and machine-consumable.

Layer Zero is fail-closed by construction. Where the law cannot be satisfied the
layer raises rather than degrading: a knowledge universe that silently accepts a
second authority has already lost the property the law exists to guarantee.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class UCKPError(FoundationError):
    """Base class for every Universal Constitutional Knowledge Layer error."""

    code = "UCKP-000"


class LawViolation(UCKPError):
    """An operation would violate an article of the root constitutional law."""

    code = "UCKP-LAW-001"


class IdentityError(UCKPError):
    """A universal identity is malformed, or a minted identity was mutated."""

    code = "UCKP-IDENTITY-001"


class FacetError(UCKPError):
    """A UCKO facet is unknown, absent, or of the wrong shape."""

    code = "UCKP-FACET-001"


class IntegrityError(UCKPError):
    """A content-addressed constitutional object was mutated after sealing."""

    code = "UCKP-INTEGRITY-001"


class DuplicateAuthorityError(UCKPError):
    """The same knowledge would exist twice, or under two authorities."""

    code = "UCKP-DUPLICATE-001"


class UnknownObjectError(UCKPError):
    """A referenced universal constitutional knowledge object does not exist."""

    code = "UCKP-404"


class RelationshipError(UCKPError):
    """A knowledge-graph relationship is malformed or unresolvable."""

    code = "UCKP-RELATION-001"


class CircularAuthorityError(UCKPError):
    """Authority derivation contains a cycle: nothing would ground the chain."""

    code = "UCKP-CIRCULAR-001"


class ProjectionAuthorityError(UCKPError):
    """A projection claimed authority. Only a UCKO may hold authority."""

    code = "UCKP-PROJECTION-001"


class PersistenceContractError(UCKPError):
    """A persistence adapter failed the identical constitutional persistence contract."""

    code = "UCKP-PERSISTENCE-001"


class ExecutionContractError(UCKPError):
    """An execution adapter failed the identical constitutional execution contract."""

    code = "UCKP-EXECUTION-001"


class StateImmutabilityError(UCKPError):
    """A prior constitutional state would change, or a transition is not well-founded."""

    code = "UCKP-STATE-001"


class EvolutionError(UCKPError):
    """The append-only evolution model was violated (out-of-order or rewritten stage)."""

    code = "UCKP-EVOLUTION-001"


class GovernanceError(UCKPError):
    """A governance decision is not discoverable, replayable or deterministic."""

    code = "UCKP-GOVERNANCE-001"


class AssimilationError(UCKPError):
    """Constitutional assimilation would lose information, authority or provenance."""

    code = "UCKP-ASSIMILATION-001"


class UCKPValidationError(UCKPError):
    """A constitutional invariant could not be measured, so no verdict may be asserted."""

    code = "UCKP-VALID-001"


__all__ = [
    "AssimilationError",
    "CircularAuthorityError",
    "DuplicateAuthorityError",
    "EvolutionError",
    "ExecutionContractError",
    "FacetError",
    "GovernanceError",
    "IdentityError",
    "IntegrityError",
    "LawViolation",
    "PersistenceContractError",
    "ProjectionAuthorityError",
    "RelationshipError",
    "StateImmutabilityError",
    "UCKPError",
    "UCKPValidationError",
    "UnknownObjectError",
]
