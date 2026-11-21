"""ZG-P-02 — Coverage Instrument error taxonomy (Universe→Code Coverage).

The Universe→Code Coverage Instrument is a strictly **additive** platform package
(``platform/coverage/``) authorized by ZG-D-02 / MIP-ZG-001 to close **G4** — the
absence of a machine-verifiable Universe→Code coverage recompute. Like every prior
EC-2 layer it **reuses** the certified EC-1 / EC-2 Foundation error discipline: every
coverage error is rooted in :class:`~platform.foundation.errors.PlatformError`, carries
a stable ``EC2-COV-*`` code and structured, non-secret context so failures are
auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The instrument invents no authority, no registry scheme, and no governance structure;
it reads authoritative repository evidence and fails **closed** — absent or malformed
evidence raises a specific error rather than fabricating a coverage edge.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class CoverageError(PlatformError):
    """Base class for all Universe→Code Coverage Instrument errors."""

    code = "EC2-COV-000"


class CoverageContractError(CoverageError):
    """A coverage node, edge, or status vocabulary value is malformed (AR-03/PL-05)."""

    code = "EC2-COV-CONTRACT-001"


class CoverageEvidenceError(CoverageError):
    """Repository evidence is missing, malformed, or non-authoritative (fail-closed)."""

    code = "EC2-COV-EVIDENCE-001"


class CoverageGraphError(CoverageError):
    """The coverage graph is malformed (dangling edge, illegal adjacency, or cycle)."""

    code = "EC2-COV-GRAPH-001"


class CoverageRegistryError(CoverageError):
    """A coverage registry operation is malformed or violates append-only discipline."""

    code = "EC2-COV-REGISTRY-001"


class CoverageEngineError(CoverageError):
    """A coverage compute/verify/reconcile operation failed fail-closed."""

    code = "EC2-COV-ENGINE-001"


class CoverageCertificationError(CoverageError):
    """A coverage certification assertion could not be produced or failed closed."""

    code = "EC2-COV-CERT-001"


__all__ = [
    "CoverageError",
    "CoverageContractError",
    "CoverageEvidenceError",
    "CoverageGraphError",
    "CoverageRegistryError",
    "CoverageEngineError",
    "CoverageCertificationError",
]
