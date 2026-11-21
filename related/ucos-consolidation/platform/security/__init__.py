"""UCOS EC-2 Platform Security Runtime (EC2-CAP-SEC-001) — SEC-CLASS (Phase 1).

The Security Runtime is the runtime realization of the existing constitutional
security architecture (``ARCH-SECURITY-001``), determined in
``platform/security/EC2-CAP-SEC-001-DETERMINATION.md``. It is a **governed, additive,
record-only** platform runtime composed over the certified EC-1 engine and the EC-2
Foundation / Identity / Observability layers: it consumes them only through published
contracts, modifies none, never writes to the certified corpus (DP-03), remains
deterministic, and preserves every EC-1 certification.

**This package ships Phase 1 — SEC-CLASS (Security Classification Runtime)** — the
constitutional "enforcement-by-reference seam", and **Phase 2 — SEC-INTEL (Security
Intelligence Runtime)** — the record-only findings/threats/controls/exceptions/
pentest/compliance/audit intelligence surface with automatic evidence-derived roll-up
(UKB-ADV-005; ``finding.schema.json``). SEC-CLASS **classifies, records, traces,
validates, and reports** the subject-layer security classification records (DATA-014 /
SERVICE-014 / APPLICATION-013 / INFRASTRUCTURE-013) and resolves their declared
enforcement obligation to the certified L7
:class:`~platform.identity.service.AuthorizationService` seam **by reference only**.
SEC-INTEL **records, correlates, rolls up, traces, validates, and reports** security
findings and stores **no** secret value (SEC-04 / RR-07; UKB-ADV-005 §6). Neither
**ever** authorizes, ratifies, enacts, governs, overrides, or escalates authority
(RG-02 / AR-04).

Phase 3 — **SEC-REG (Security Registry Runtime)** — realizes the seven constitutional
§17 registries (Security · Identity · Threat · Risk · Evidence · Certification ·
Trust) as append-only, record-only, attributed, queryable stores that never ratify or
enact (RG-02 / RG-05); see :mod:`platform.security.registries`.

Phase 4 — **SEC-OBS (Security Observability Runtime)** — emits the existing
``security`` signal dimension and shapes security telemetry (metric/log/audit)
**through** the certified L8 Observability Layer, preserving reverse-traceability to
the finding/scan that raised each signal (§15; UMB-015 §5); it creates no new signal
dimension and no second telemetry stack; see :mod:`platform.security.observability`.

Phase 5 — **SEC-CERT (Security Certification Runtime)** — records the seven §18
security certification objects, applies the §19 control-facet failure guard (producing
a Gap Report on any missing facet), and rolls recorded certifications into a
deterministic program certification; record-only, evidence-backed, non-constitutive
(STATUS-001 §2); see :mod:`platform.security.certification`.

Phase 6 — **SEC-ZONE (Zone & Control Posture Runtime)** — records the posture of the
UMB-015 five protection zones and seven controls (policy-configured, not compiled
ceilings) and evaluates the zone mutation-direction invariant (UMB-INV-01); record-only;
see :mod:`platform.security.zones`.

All six record-only Security Runtime sub-capabilities are now present.

Deliverables (SEC-CLASS + SEC-INTEL):
    * **errors** — the ``EC2-SEC-*`` error taxonomy over ``PlatformError``.
    * **contracts** — the classification vocabulary (``ClassificationKind``,
      ``SubjectLayer``, ``EnforcementReference``), the intelligence vocabulary
      (``FindingKind``, ``Severity``, ``FindingState``, ``RollupState``), and the
      published SEC-CLASS / SEC-INTEL contract surfaces.
    * **classification** — the immutable ``SecurityClassification`` record and the
      append-only ``ClassificationLedger``.
    * **intelligence** — the immutable ``SecurityFinding`` record, the append-only
      ``FindingLedger``, the evidence-derived ``compute_rollup``, and the
      ``SecurityIntelligenceService`` + ``SecurityIntelligenceEvidence``.
    * **service** — the ``SecurityClassificationService`` composition root and
      ``SecurityClassificationEvidence``.
    * **bootstrap** — ``bootstrap_security_classification`` and
      ``bootstrap_security_intelligence`` (compose the runtimes onto a
      ``PlatformContext``).

This package carries no constitutional authority; the external gates (EC-1…EC-6)
remain open.
"""

from __future__ import annotations

from platform.security.bootstrap import (
    SECURITY_CERTIFICATION_BOOTSTRAP_EVENT,
    SECURITY_CLASSIFICATION_BOOTSTRAP_EVENT,
    SECURITY_INTELLIGENCE_BOOTSTRAP_EVENT,
    SECURITY_OBSERVABILITY_BOOTSTRAP_EVENT,
    SECURITY_REGISTRY_BOOTSTRAP_EVENT,
    SECURITY_ZONE_BOOTSTRAP_EVENT,
    bootstrap_security_certification,
    bootstrap_security_classification,
    bootstrap_security_intelligence,
    bootstrap_security_observability,
    bootstrap_security_registry,
    bootstrap_security_zone,
)
from platform.security.certification import (
    CERTIFICATION_RECORDED_EVENT,
    CertificationLedger,
    GapReport,
    ProgramCertification,
    SecurityCertification,
    SecurityCertificationEvidence,
    SecurityCertificationService,
    build_security_certification_service,
    evaluate_control_facets,
    roll_up_program,
)
from platform.security.classification import (
    ClassificationLedger,
    SecurityClassification,
)
from platform.security.contracts import (
    BLOCKING_SEVERITIES,
    CANON_ZONES,
    CONTROL_MECHANISM,
    L7_BOUND_KINDS,
    OPEN_FINDING_STATES,
    REGISTRY_SOURCE,
    REQUIRED_CONTROL_FACETS,
    SECURITY_CERTIFICATION_CONTRACT_VERSION,
    SECURITY_CERTIFICATION_CONTRACTS,
    SECURITY_CLASSIFICATION_CONTRACT_VERSION,
    SECURITY_CLASSIFICATION_CONTRACTS,
    SECURITY_INTELLIGENCE_CONTRACT_VERSION,
    SECURITY_INTELLIGENCE_CONTRACTS,
    SECURITY_OBSERVABILITY_CONTRACT_VERSION,
    SECURITY_OBSERVABILITY_CONTRACTS,
    SECURITY_REGISTRY_CONTRACT_VERSION,
    SECURITY_REGISTRY_CONTRACTS,
    SECURITY_SIGNAL_DIMENSION,
    SECURITY_ZONE_CONTRACT_VERSION,
    SECURITY_ZONE_CONTRACTS,
    SUBJECT_LAYER_KINDS,
    SUBJECT_LAYER_SOURCE,
    ZONE_DEFAULT_POSTURE,
    ZONE_LEVEL,
    ZONE_NAME,
    CertificationClass,
    CertificationDecision,
    ClassificationKind,
    ControlFacet,
    EnforcementReference,
    FindingKind,
    FindingState,
    RegistryKind,
    RollupState,
    SecurityControl,
    SecurityZone,
    Severity,
    SubjectLayer,
    all_certification_classes,
    all_classification_kinds,
    all_control_facets,
    all_finding_kinds,
    all_finding_states,
    all_registry_kinds,
    all_security_controls,
    all_security_zones,
    all_severities,
    all_subject_layers,
    default_security_certification_contracts,
    default_security_classification_contracts,
    default_security_intelligence_contracts,
    default_security_observability_contracts,
    default_security_registry_contracts,
    default_security_zone_contracts,
    security_certification_contract,
    security_classification_contract,
    security_intelligence_contract,
    security_observability_contract,
    security_registry_contract,
    security_zone_contract,
)
from platform.security.errors import (
    CertificationGapError,
    CertificationValidationError,
    ClassificationBindingError,
    ClassificationValidationError,
    EnforcementReferenceError,
    FindingValidationError,
    RegistryEntryError,
    RegistryValidationError,
    SecretLeakError,
    SecurityBootstrapError,
    SecurityCertificationError,
    SecurityClassificationError,
    SecurityContractError,
    SecurityError,
    SecurityFindingError,
    SecurityObservabilityError,
    SecurityRegistryError,
    SecurityRollupError,
    SecuritySignalError,
    SecurityZoneError,
    SignalTraceabilityError,
    ZoneMutationError,
    ZonePostureError,
)
from platform.security.intelligence import (
    FINDING_RECORDED_EVENT,
    ROLLUP_EVALUATED_EVENT,
    SECRET_LEAK_IDENTIFIER,
    FindingLedger,
    SecurityFinding,
    SecurityIntelligenceEvidence,
    SecurityIntelligenceService,
    SecurityRollup,
    build_security_intelligence_service,
    compute_rollup,
    scan_for_secret,
)
from platform.security.observability import (
    SECURITY_SIGNAL_AUDIT_ACTION,
    SECURITY_SIGNAL_EMITTED_EVENT,
    SECURITY_SIGNAL_METRIC,
    SecurityObservabilityEvidence,
    SecurityObservabilityService,
    SecuritySignal,
    SignalLedger,
    build_security_observability_service,
)
from platform.security.registries import (
    REGISTRY_RECORDED_EVENT,
    AppendOnlyRegistry,
    RegistryEntry,
    SecurityRegistryEvidence,
    SecurityRegistryService,
    SecurityRegistrySet,
    build_security_registry_service,
)
from platform.security.service import (
    CLASSIFICATION_RECORDED_EVENT,
    SecurityClassificationEvidence,
    SecurityClassificationService,
    build_security_classification_service,
)
from platform.security.zones import (
    POSTURE_RECORDED_EVENT,
    POSTURE_TARGET_CONTROL,
    POSTURE_TARGET_ZONE,
    PostureLedger,
    PostureRecord,
    SecurityZoneEvidence,
    SecurityZoneService,
    build_security_zone_service,
    zone_may_mutate,
)

__all__ = [
    # contracts
    "SECURITY_CLASSIFICATION_CONTRACT_VERSION",
    "SECURITY_CLASSIFICATION_CONTRACTS",
    "ClassificationKind",
    "L7_BOUND_KINDS",
    "SubjectLayer",
    "SUBJECT_LAYER_SOURCE",
    "SUBJECT_LAYER_KINDS",
    "EnforcementReference",
    "all_classification_kinds",
    "all_subject_layers",
    "security_classification_contract",
    "default_security_classification_contracts",
    "SECURITY_INTELLIGENCE_CONTRACT_VERSION",
    "SECURITY_INTELLIGENCE_CONTRACTS",
    "FindingKind",
    "Severity",
    "FindingState",
    "RollupState",
    "BLOCKING_SEVERITIES",
    "OPEN_FINDING_STATES",
    "all_finding_kinds",
    "all_severities",
    "all_finding_states",
    "security_intelligence_contract",
    "default_security_intelligence_contracts",
    # SEC-REG
    "SECURITY_REGISTRY_CONTRACT_VERSION",
    "SECURITY_REGISTRY_CONTRACTS",
    "RegistryKind",
    "REGISTRY_SOURCE",
    "all_registry_kinds",
    "security_registry_contract",
    "default_security_registry_contracts",
    # SEC-OBS
    "SECURITY_OBSERVABILITY_CONTRACT_VERSION",
    "SECURITY_OBSERVABILITY_CONTRACTS",
    "SECURITY_SIGNAL_DIMENSION",
    "security_observability_contract",
    "default_security_observability_contracts",
    # SEC-CERT
    "SECURITY_CERTIFICATION_CONTRACT_VERSION",
    "SECURITY_CERTIFICATION_CONTRACTS",
    "CertificationClass",
    "CertificationDecision",
    "ControlFacet",
    "REQUIRED_CONTROL_FACETS",
    "all_certification_classes",
    "all_control_facets",
    "security_certification_contract",
    "default_security_certification_contracts",
    # SEC-ZONE
    "SECURITY_ZONE_CONTRACT_VERSION",
    "SECURITY_ZONE_CONTRACTS",
    "SecurityZone",
    "SecurityControl",
    "ZONE_LEVEL",
    "ZONE_NAME",
    "ZONE_DEFAULT_POSTURE",
    "CANON_ZONES",
    "CONTROL_MECHANISM",
    "all_security_zones",
    "all_security_controls",
    "security_zone_contract",
    "default_security_zone_contracts",
    # classification
    "SecurityClassification",
    "ClassificationLedger",
    # intelligence
    "FINDING_RECORDED_EVENT",
    "ROLLUP_EVALUATED_EVENT",
    "SECRET_LEAK_IDENTIFIER",
    "SecurityFinding",
    "FindingLedger",
    "SecurityRollup",
    "compute_rollup",
    "scan_for_secret",
    "SecurityIntelligenceEvidence",
    "SecurityIntelligenceService",
    "build_security_intelligence_service",
    # registries
    "REGISTRY_RECORDED_EVENT",
    "RegistryEntry",
    "AppendOnlyRegistry",
    "SecurityRegistrySet",
    "SecurityRegistryEvidence",
    "SecurityRegistryService",
    "build_security_registry_service",
    # observability
    "SECURITY_SIGNAL_EMITTED_EVENT",
    "SECURITY_SIGNAL_METRIC",
    "SECURITY_SIGNAL_AUDIT_ACTION",
    "SecuritySignal",
    "SignalLedger",
    "SecurityObservabilityEvidence",
    "SecurityObservabilityService",
    "build_security_observability_service",
    # certification
    "CERTIFICATION_RECORDED_EVENT",
    "GapReport",
    "evaluate_control_facets",
    "SecurityCertification",
    "CertificationLedger",
    "ProgramCertification",
    "roll_up_program",
    "SecurityCertificationEvidence",
    "SecurityCertificationService",
    "build_security_certification_service",
    # zones
    "POSTURE_RECORDED_EVENT",
    "POSTURE_TARGET_ZONE",
    "POSTURE_TARGET_CONTROL",
    "zone_may_mutate",
    "PostureRecord",
    "PostureLedger",
    "SecurityZoneEvidence",
    "SecurityZoneService",
    "build_security_zone_service",
    # service
    "CLASSIFICATION_RECORDED_EVENT",
    "SecurityClassificationEvidence",
    "SecurityClassificationService",
    "build_security_classification_service",
    # bootstrap
    "SECURITY_CLASSIFICATION_BOOTSTRAP_EVENT",
    "bootstrap_security_classification",
    "SECURITY_INTELLIGENCE_BOOTSTRAP_EVENT",
    "bootstrap_security_intelligence",
    "SECURITY_REGISTRY_BOOTSTRAP_EVENT",
    "bootstrap_security_registry",
    "SECURITY_OBSERVABILITY_BOOTSTRAP_EVENT",
    "bootstrap_security_observability",
    "SECURITY_CERTIFICATION_BOOTSTRAP_EVENT",
    "bootstrap_security_certification",
    "SECURITY_ZONE_BOOTSTRAP_EVENT",
    "bootstrap_security_zone",
    # errors
    "SecurityError",
    "SecurityClassificationError",
    "ClassificationBindingError",
    "EnforcementReferenceError",
    "ClassificationValidationError",
    "SecurityContractError",
    "SecurityBootstrapError",
    "SecurityFindingError",
    "FindingValidationError",
    "SecretLeakError",
    "SecurityRollupError",
    "SecurityRegistryError",
    "RegistryEntryError",
    "RegistryValidationError",
    "SecurityObservabilityError",
    "SecuritySignalError",
    "SignalTraceabilityError",
    "SecurityCertificationError",
    "CertificationValidationError",
    "CertificationGapError",
    "SecurityZoneError",
    "ZonePostureError",
    "ZoneMutationError",
]
