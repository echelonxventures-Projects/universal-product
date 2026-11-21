"""UCOS-UFP-001 — Universal Foundation Platform error taxonomy.

The Universal Foundation Platform (``platform/universal_foundation/``) composes the reusable
Foundation capabilities — Repository Truth, Ownership, Source Assimilation and Measurement
Policy — into one service that a project specialises by **declaration**.

It reuses the certified Foundation error discipline: every error is rooted in
:class:`~platform.foundation.errors.PlatformError`, carries a stable ``EC2-UFP-*`` code and
structured, non-secret context (PL-02, IP-12), and fails **closed**.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class UniversalFoundationError(PlatformError):
    """Base class for all Universal Foundation Platform (UFP-001) errors."""

    code = "EC2-UFP-000"


class SpecializationError(UniversalFoundationError):
    """A project specialisation document is missing, malformed, or incomplete (fail-closed)."""

    code = "EC2-UFP-SPECIALIZATION-001"


class FoundationCompositionError(UniversalFoundationError):
    """The Foundation could not be composed from the declared specialisation."""

    code = "EC2-UFP-COMPOSITION-001"


class FoundationConstitutionError(UniversalFoundationError):
    """A constitutional article, domain, scope or gate reference is malformed or unknown."""

    code = "EC2-UFP-CONSTITUTION-001"


class FoundationConformanceError(UniversalFoundationError):
    """A capability register entry is malformed, or a conformance probe could not execute."""

    code = "EC2-UFP-CONFORMANCE-001"


class FoundationConvergenceError(UniversalFoundationError):
    """A constitutional-model convergence declaration is malformed or unresolvable."""

    code = "EC2-UFP-CONVERGENCE-001"


class FoundationFreezeError(UniversalFoundationError):
    """A freeze criterion declaration is malformed, or its evidence could not be measured."""

    code = "EC2-UFP-FREEZE-001"


class FoundationNucleusError(UniversalFoundationError):
    """An Ω Nucleus facet contract or profile declaration is malformed or unresolvable."""

    code = "EC2-UFP-NUCLEUS-001"


__all__ = [
    "FoundationNucleusError",
    "UniversalFoundationError",
    "SpecializationError",
    "FoundationCompositionError",
    "FoundationConstitutionError",
    "FoundationConformanceError",
    "FoundationConvergenceError",
    "FoundationFreezeError",
]
