"""UCOS Ω∞ — Universe→Code Coverage Instrument (``platform.coverage``, ZG-P-02).

The deterministic, machine-verifiable, fail-closed instrument that closes **G4** — the
missing machine-verifiable Universe→Code coverage recompute identified by ZG-D-02 /
MIP-ZG-001. It reconstructs the authoritative coverage spine

    Universe → Phase → Program → Implementation → Epic → Module → Code Asset → Runtime Asset

from repository evidence (no hardcoded mappings, no manual tables, no synthetic edges),
computes fail-closed coverage status, records it in an append-only content-addressed
registry, exposes ``compute``/``verify``/``reconcile``/``fingerprint``/``report``, drives
nine critical health checks, and emits certification-facing evidence for G4 closure.

Strictly **additive**: it reuses the certified Foundation contract machinery and the
Observability health model, integrates with GOV-002/005/006 · TRACK-001 · STATUS-001 ·
MIP-ZG-001 **by reference**, and modifies no EC-1 module, no prior EC-2 epic, and no
frozen corpus.
"""

from __future__ import annotations

from platform.coverage.certification import (
    CERTIFIED,
    NOT_CERTIFIED,
    CoverageCertification,
    assess,
)
from platform.coverage.contracts import (
    COVERAGE_CONTRACTS,
    GOVERNANCE_AUTHORITIES,
    CoverageEdge,
    CoverageNode,
    CoverageNodeKind,
    CoverageStatus,
)
from platform.coverage.engine import (
    CoverageEngine,
    CoverageReconciliation,
    CoverageVerification,
)
from platform.coverage.errors import (
    CoverageError,
    CoverageEvidenceError,
    CoverageGraphError,
    CoverageRegistryError,
)
from platform.coverage.evidence import (
    EvidenceBundle,
    EvidenceSource,
    InMemoryEvidenceSource,
)
from platform.coverage.graph import CoverageGraph
from platform.coverage.health import CoverageHealth, coverage_health_checks
from platform.coverage.registry import CoverageRegistry
from platform.coverage.repository import RepositoryEvidenceSource
from platform.coverage.service import (
    CoverageEvidence,
    CoverageService,
    build_coverage_service,
)

__all__ = [
    "CoverageNodeKind",
    "CoverageStatus",
    "CoverageNode",
    "CoverageEdge",
    "COVERAGE_CONTRACTS",
    "GOVERNANCE_AUTHORITIES",
    "EvidenceBundle",
    "EvidenceSource",
    "InMemoryEvidenceSource",
    "RepositoryEvidenceSource",
    "CoverageGraph",
    "CoverageRegistry",
    "CoverageEngine",
    "CoverageVerification",
    "CoverageReconciliation",
    "CoverageHealth",
    "coverage_health_checks",
    "CoverageCertification",
    "assess",
    "CERTIFIED",
    "NOT_CERTIFIED",
    "CoverageService",
    "CoverageEvidence",
    "build_coverage_service",
    "CoverageError",
    "CoverageEvidenceError",
    "CoverageGraphError",
    "CoverageRegistryError",
]
