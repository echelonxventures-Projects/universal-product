"""UCOS-EPIC-003 — Universal Discovery Engine (registry-driven, deterministic).

The Universal Discovery Engine replaces regex/filesystem discovery with a purely
**registry-driven** projection over the read-only 00-BOOK substrate (EPIC-002). It
discovers, deterministically and exhaustively, across eight universal dimensions:

    namespace · document · registry · component · dependency · evidence ·
    ontology · capability

There are **no hard-coded discovery patterns**: no regex over paths or content, no
``glob``/``fnmatch``, and no filesystem walking. The registry is the single source
of truth (INV-13). Identical substrates yield byte-identical discovery reports,
coverage reports, and evidence (TP-01, IMP-007 §5).

Deliverables: the Discovery Engine (:class:`UniversalDiscoveryEngine`), the
per-dimension discovery APIs, the :class:`CoverageReport`, and the deterministic
evidence bundle (:func:`emit_evidence`).
"""

from __future__ import annotations

from engine.discovery.contracts import (
    DISCOVERY_CONTRACT,
    DISCOVERY_CONTRACT_VERSION,
    DISCOVERY_DIMENSIONS,
    CoverageReport,
    DimensionCoverage,
    DimensionResult,
    DiscoveredItem,
    DiscoveryKind,
    DiscoveryReport,
    build_coverage_report,
    canonical_json,
    content_hash,
)
from engine.discovery.dimensions import (
    REALIZED_STATUSES,
    discover_capabilities,
    discover_components,
    discover_dependencies,
    discover_documents,
    discover_evidence,
    discover_namespaces,
    discover_ontology,
    discover_registries,
)
from engine.discovery.engine import DISCOVERY_ENGINE_ID, UniversalDiscoveryEngine
from engine.discovery.errors import (
    DiscoveryDimensionError,
    DiscoveryError,
    DiscoveryEvidenceError,
)
from engine.discovery.evidence import (
    DISCOVERY_COVERAGE_FORMAT,
    DISCOVERY_DIMENSION_FORMAT,
    DISCOVERY_EVIDENCE_FORMAT,
    DiscoveryEvidence,
    build_coverage_document,
    build_discovery_evidence,
    emit_evidence,
)

__all__ = [
    # engine facade
    "UniversalDiscoveryEngine",
    "DISCOVERY_ENGINE_ID",
    "DISCOVERY_CONTRACT",
    "DISCOVERY_CONTRACT_VERSION",
    # contracts / value types
    "DiscoveryKind",
    "DISCOVERY_DIMENSIONS",
    "DiscoveredItem",
    "DimensionCoverage",
    "DimensionResult",
    "CoverageReport",
    "DiscoveryReport",
    "build_coverage_report",
    "canonical_json",
    "content_hash",
    # dimension discoverers
    "REALIZED_STATUSES",
    "discover_namespaces",
    "discover_documents",
    "discover_registries",
    "discover_components",
    "discover_dependencies",
    "discover_evidence",
    "discover_ontology",
    "discover_capabilities",
    # evidence
    "DiscoveryEvidence",
    "build_discovery_evidence",
    "build_coverage_document",
    "emit_evidence",
    "DISCOVERY_EVIDENCE_FORMAT",
    "DISCOVERY_COVERAGE_FORMAT",
    "DISCOVERY_DIMENSION_FORMAT",
    # errors
    "DiscoveryError",
    "DiscoveryDimensionError",
    "DiscoveryEvidenceError",
]
