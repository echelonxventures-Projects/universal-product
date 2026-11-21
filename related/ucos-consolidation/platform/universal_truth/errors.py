"""UCOS-URTF-001 — Universal Repository Truth Framework error taxonomy.

The Universal Repository Truth Framework (``platform/universal_truth/``) is a strictly
**additive** platform package that generalises *what counts as Truth* out of any single
engine and into a declared, reusable policy. Like every prior EC-2 layer it **reuses**
the certified Foundation error discipline: every error is rooted in
:class:`~platform.foundation.errors.PlatformError`, carries a stable ``EC2-URTF-*`` code
and structured, non-secret context so failures are auditable (PL-02, IP-12) and
machine-consumable by TRACK-001.

The framework invents no authority. It **classifies** declared zones and fails
**closed**: a malformed selector, an inadmissible zone declaration, or a projection over
a malformed document raises a specific error rather than guessing a classification.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class RepositoryTruthError(PlatformError):
    """Base class for all Universal Repository Truth Framework (URTF-001) errors."""

    code = "EC2-URTF-000"


class TruthContractError(RepositoryTruthError):
    """A truth vocabulary value (class, selector, zone, classification) is malformed."""

    code = "EC2-URTF-CONTRACT-001"


class TruthPolicyError(RepositoryTruthError):
    """A truth policy is malformed, ambiguous, or declares an inadmissible zone."""

    code = "EC2-URTF-POLICY-001"


class TruthProjectionError(RepositoryTruthError):
    """A subject projection could not be derived from a declared document (fail-closed)."""

    code = "EC2-URTF-PROJECTION-001"


class TruthEligibilityError(RepositoryTruthError):
    """A declared locator-eligibility ledger is malformed, empty, or unreadable."""

    code = "EC2-URTF-ELIGIBILITY-001"


__all__ = [
    "RepositoryTruthError",
    "TruthContractError",
    "TruthPolicyError",
    "TruthProjectionError",
    "TruthEligibilityError",
]
