"""UCOS-EPIC-014 — Repository Intelligence error taxonomy (Terminal T5).

Repository Intelligence answers, continuously and from evidence alone, the eight
discovery questions the repository must never guess at: *what exists, what it can do,
what may be reused, what depends on what, what is missing, what conflicts, what is
duplicated, and who owns it* — and then graphs, recommends, validates and certifies
the answer.

The subsystem **reuses** the EC-1 / Platform Foundation error discipline additively; it
does not fork or modify it. Every error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-RPI-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable.

Fail-closed discipline: a detector that cannot *prove* an invariant holds — because the
substrate it needs is absent or malformed — records a **FAIL finding**, never a pass and
never a swallowed exception. An exception is raised **only** for a malformed
configuration or an unusable substrate (an authoring/environment fault), never for a
legitimate fail-closed verdict, which is always reported as data.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class RepositoryIntelligenceError(PlatformError):
    """Base class for all Repository Intelligence errors (UCOS-EPIC-014)."""

    code = "EC2-RPI-000"


class IntelligenceConfigurationError(RepositoryIntelligenceError):
    """The repository-intelligence configuration is missing, unreadable, or malformed."""

    code = "EC2-RPI-CONFIG-001"


class SubstrateError(RepositoryIntelligenceError):
    """The repository substrate could not be read (absent root, unusable code roots)."""

    code = "EC2-RPI-SUBSTRATE-001"


class DiscoveryError(RepositoryIntelligenceError):
    """A discovery dimension was supplied a malformed substrate or unknown dimension."""

    code = "EC2-RPI-DISCOVERY-001"


class GraphError(RepositoryIntelligenceError):
    """The repository graph is malformed (unknown endpoint, duplicate node identity)."""

    code = "EC2-RPI-GRAPH-001"


class RecommendationError(RepositoryIntelligenceError):
    """A recommendation could not be derived from the supplied intelligence."""

    code = "EC2-RPI-RECOMMEND-001"


class RepositoryValidationError(RepositoryIntelligenceError):
    """Repository validation could not be composed or executed."""

    code = "EC2-RPI-VALIDATE-001"


class RepositoryCertificationError(RepositoryIntelligenceError):
    """A repository-intelligence certificate could not be issued or failed integrity."""

    code = "EC2-RPI-CERTIFY-001"


__all__ = [
    "RepositoryIntelligenceError",
    "IntelligenceConfigurationError",
    "SubstrateError",
    "DiscoveryError",
    "GraphError",
    "RecommendationError",
    "RepositoryValidationError",
    "RepositoryCertificationError",
]
