"""UCOS-UOF-001 — Universal Ownership Framework error taxonomy.

The Universal Ownership Framework (``platform/universal_ownership/``) is a strictly
**additive** platform package that generalises canonical ownership out of per-repository
heuristics into a constitutional contract plus a pluggable evidence framework. It reuses
the certified Foundation error discipline: every error is rooted in
:class:`~platform.foundation.errors.PlatformError`, carries a stable ``EC2-UOF-*`` code and
structured, non-secret context (PL-02, IP-12).

The framework **never fabricates ownership**. Absent constitutive evidence it raises or
records an honest UNRESOLVED standing — it does not guess an owner, and a caller that asks
it to assert one without evidence fails closed.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class OwnershipError(PlatformError):
    """Base class for all Universal Ownership Framework (UOF-001) errors."""

    code = "EC2-UOF-000"


class OwnershipContractError(OwnershipError):
    """An ownership vocabulary value or declaration contract is malformed."""

    code = "EC2-UOF-CONTRACT-001"


class OwnershipEvidenceError(OwnershipError):
    """An evidence provider is malformed or produced inadmissible evidence (fail-closed)."""

    code = "EC2-UOF-EVIDENCE-001"


class OwnershipProviderConflictError(OwnershipError):
    """Two different evidence providers claim the same provider identity."""

    code = "EC2-UOF-EVIDENCE-002"


class OwnershipDeterminationError(OwnershipError):
    """An ownership determination could not be produced honestly (fail-closed)."""

    code = "EC2-UOF-DETERMINATION-001"


class OwnershipFabricationError(OwnershipError):
    """An attempt was made to assert ownership without constitutive evidence.

    Ownership SHALL be declared and evidenced; it SHALL NEVER be implied, inferred, or
    filled in to close a metric.
    """

    code = "EC2-UOF-DETERMINATION-002"


class OwnershipRecommendationError(OwnershipError):
    """A recommendation provider is malformed or proposed for a subject it may not.

    A recommendation is a proposal for a governing authority to ratify, never an
    assignment. This error is raised rather than allowing a proposal to be mistaken for
    evidence, or to be offered for a subject whose ownership is already declared.
    """

    code = "EC2-UOF-RECOMMENDATION-001"


class OwnershipEligibilityError(OwnershipError):
    """A declared locator-eligibility ledger is malformed or unreadable (fail-closed)."""

    code = "EC2-UOF-ELIGIBILITY-001"


__all__ = [
    "OwnershipError",
    "OwnershipContractError",
    "OwnershipEvidenceError",
    "OwnershipProviderConflictError",
    "OwnershipDeterminationError",
    "OwnershipFabricationError",
    "OwnershipRecommendationError",
    "OwnershipEligibilityError",
]
