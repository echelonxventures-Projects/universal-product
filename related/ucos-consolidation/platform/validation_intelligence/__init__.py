"""UCOS-EPIC-013 — Continuous Validation Intelligence (Terminal T5).

The platform-layer validation **intelligence**: a deterministic, fail-closed,
evidence-producing engine that *expands validation beyond static rule execution*
(EPIC-005) by reasoning across seven intelligence dimensions —
**cross-capability consistency, repository completeness, contract compatibility,
architecture compliance, runtime compatibility, version compatibility, and governance
compliance** — from a single, configuration-driven command.

The engine is:

    * **universal** — one normalized :class:`IntelligenceTarget` and one open analyzer
      suite reason over any system; the seven dimensions are covered by the built-in
      :func:`default_analyzers`, and callers may supply their own analyzers;
    * **fail-closed** — an analyzer that cannot prove its invariant (absent or malformed
      evidence) records a FAIL, never a pass; the verdict is FAIL iff any *blocking*
      check failed (Mission mandate);
    * **evidence-required** — every run yields a content-addressed
      :class:`ValidationIntelligenceReport`, an :class:`IntelligenceDashboard`, a
      :class:`CompatibilityReport`, a :class:`ComplianceReport`, and a
      :class:`ValidationIntelligenceEvidence` record (Mandatory Rule 6); and
    * **deterministic** — an identical target analyzed by an identical suite yields a
      byte-identical report and content hash (IMP-007 §5); no wall-clock or ambient state
      enters any identity.

It is strictly additive and record-only over the certified EC-1 engine and EPIC-005: it
consumes the EC-1 foundation (logging, telemetry, disclosure, frozen-path guard) and the
platform foundation (content hashing) through their published surfaces, invents no
verdict (TP-01), mutates no target, and never writes to the certified corpus (DP-03). It
asserts ``ENGINEERING-EXECUTION-ONLY`` authority and carries the EC-1 provisional-state
disclosure (DE-05 / IP-01).

Deliverables: Validation Intelligence
(:class:`ContinuousValidationIntelligenceEngine` / :class:`ValidationIntelligenceReport`),
Compatibility Engine (:class:`CompatibilityEngine` / :class:`CompatibilityReport`),
Compliance Reports (:class:`ComplianceReport`), Validation Evidence
(:class:`ValidationIntelligenceEvidence`), and the CLI (``ucos-validate-intel``).
"""

from __future__ import annotations

from platform.validation_intelligence.analyzers import (
    ArchitectureComplianceAnalyzer,
    ContractCompatibilityAnalyzer,
    CrossCapabilityConsistencyAnalyzer,
    DimensionAnalyzer,
    GovernanceComplianceAnalyzer,
    RepositoryCompletenessAnalyzer,
    RuntimeCompatibilityAnalyzer,
    VersionCompatibilityAnalyzer,
    default_analyzers,
)
from platform.validation_intelligence.compatibility import (
    CompatibilityEngine,
    SemVer,
    build_compatibility_report,
)
from platform.validation_intelligence.compliance import build_compliance_report
from platform.validation_intelligence.config import (
    ValidationIntelligenceConfig,
    load_config,
    parse_config,
)
from platform.validation_intelligence.contracts import (
    COMPATIBILITY_REPORT_FORMAT,
    COMPLIANCE_REPORT_FORMAT,
    INTELLIGENCE_AUTHORITY,
    INTELLIGENCE_DASHBOARD_FORMAT,
    INTELLIGENCE_REPORT_FORMAT,
    VALIDATION_INTELLIGENCE_CONTRACT_VERSION,
    CompatibilityReport,
    ComplianceReport,
    DimensionKind,
    DimensionReport,
    Finding,
    FindingStatus,
    IntelligenceDashboard,
    IntelligenceDimension,
    IntelligenceTarget,
    Severity,
    ValidationIntelligenceReport,
    Verdict,
    dimensions_of_kind,
)
from platform.validation_intelligence.engine import ContinuousValidationIntelligenceEngine
from platform.validation_intelligence.errors import (
    AnalyzerDefinitionError,
    CompatibilityError,
    IntelligenceConfigError,
    IntelligenceEngineError,
    IntelligenceTargetError,
    ValidationIntelligenceError,
)
from platform.validation_intelligence.evidence import (
    EVIDENCE_FORMAT,
    ValidationIntelligenceEvidence,
    build_validation_intelligence_evidence,
)
from platform.validation_intelligence.service import (
    ContinuousValidationIntelligenceService,
    build_validation_intelligence_service,
)

__all__ = [
    # contracts
    "VALIDATION_INTELLIGENCE_CONTRACT_VERSION",
    "INTELLIGENCE_REPORT_FORMAT",
    "INTELLIGENCE_DASHBOARD_FORMAT",
    "COMPATIBILITY_REPORT_FORMAT",
    "COMPLIANCE_REPORT_FORMAT",
    "INTELLIGENCE_AUTHORITY",
    "DimensionKind",
    "IntelligenceDimension",
    "dimensions_of_kind",
    "Severity",
    "FindingStatus",
    "Verdict",
    "IntelligenceTarget",
    "Finding",
    "DimensionReport",
    "ValidationIntelligenceReport",
    "IntelligenceDashboard",
    "CompatibilityReport",
    "ComplianceReport",
    # analyzers
    "DimensionAnalyzer",
    "CrossCapabilityConsistencyAnalyzer",
    "RepositoryCompletenessAnalyzer",
    "ContractCompatibilityAnalyzer",
    "ArchitectureComplianceAnalyzer",
    "RuntimeCompatibilityAnalyzer",
    "VersionCompatibilityAnalyzer",
    "GovernanceComplianceAnalyzer",
    "default_analyzers",
    # compatibility engine
    "CompatibilityEngine",
    "SemVer",
    "build_compatibility_report",
    # compliance
    "build_compliance_report",
    # engine
    "ContinuousValidationIntelligenceEngine",
    # evidence
    "EVIDENCE_FORMAT",
    "ValidationIntelligenceEvidence",
    "build_validation_intelligence_evidence",
    # config
    "ValidationIntelligenceConfig",
    "parse_config",
    "load_config",
    # service
    "ContinuousValidationIntelligenceService",
    "build_validation_intelligence_service",
    # errors
    "ValidationIntelligenceError",
    "IntelligenceConfigError",
    "IntelligenceTargetError",
    "AnalyzerDefinitionError",
    "IntelligenceEngineError",
    "CompatibilityError",
]
