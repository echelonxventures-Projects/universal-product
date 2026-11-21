"""UCOS EC-2 Platform Certification Console & Ledger Runtime (EC2-EPIC-011).

The Certification Console & Ledger Runtime (L3 Application of the Program architecture,
§4) realizes Program **Surface #10 Certification Ledger** (PC-10 certification inspection
& ledger + PC-13 search + PC-16 audit): it makes the certified EC-1 certification output
**inspectable, searchable, ledger-navigable, and traceable** to authorized principals,
**faithfully** — every surfaced decision, immutable record, evidence reference, and ledger
entry is byte-for-byte the certified engine output (P6). Authorized principals surface a
certification for validated output (the certified engine is reproduced read-only over the
upstream validation report + evidence), inspect the decision/criteria, view the evidence
reference, navigate the append-only hash-chained ledger and a certification's lineage,
track the derived posture, evaluate readiness, validate certification governance,
discover/search certifications under authorization + isolation, and navigate the
Validation → Target → Certification trace edge — with cross-runtime health (including a
machine-checkable fidelity check and a ledger-integrity check), append-only audit, and
reproducible evidence.

Authoritative basis: ``06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md``
(§2.1 surface #10 Certification Ledger, PC-10/PC-13/PC-16, §3.2 RBAC row
``certification-ledger``, §4 L3/L4, §4.3 EC-1 ``certification`` interaction, §5
EC2-EPIC-011 acceptance, §9 P6 Fidelity), as determined by
``platform/certification/EC2-EPIC-011-DETERMINATION.md`` (**IMPLEMENTATION AUTHORIZED**),
and the certified EC-1 Certification Layer (``engine/certification/``, consumed read-only
by reference).

It is a strictly **additive**, **read/inspection-only** layer over the certified EC-1
engine and the EC-2 Foundation (EC2-EPIC-001), Identity (EC2-EPIC-002), and Observability
(EC2-EPIC-013) layers: it authorizes only through the Identity Layer on the existing
``certification-ledger`` capability group (no new authority, no new capability group),
consumes ``engine.certification`` **only by reference** (the L4 façade invokes the
certified ``CertificationEngine`` read-only; no criterion/verdict/ledger-rule/evidence
format is redefined), observes only through the Observability Layer, and exposes **no
mutation path** to any surfaced record, evidence, or ledger entry (the ledger is
append-only by construction). It modifies neither EC-1 nor any prior layer, never writes
to the certified corpus (DP-03), remains deterministic, starts no server, and opens no
socket.

Deliverables (EC2-TASK-000153…000161):
    * **errors** — the ``EC2-CC-*`` error taxonomy over ``PlatformError``.
    * **contracts** — vocabulary (``CertificationAction``, re-exported engine
      ``CertificationStatus``/``CertificationClass``/``CriterionSeverity``/
      ``CriterionStatus``), the descriptive ``CertificationRecordMetadata`` value type,
      the read-only view projections (``CriterionFindingView``, ``CertificationSummary``,
      ``CertificationEvidenceReference``, ``CertificationTrace``), the
      ``CertificationConsoleRecord`` aggregate, the verb→permission map binding the
      ``certification-ledger`` group, and ``CERTIFICATION_CONSOLE_CONTRACTS``.
    * **facade** — the read-only EC-1 façade (``CertificationFacade`` +
      ``SurfacedCertification``) consuming ``engine.certification`` by reference.
    * **registry** — the ``CertificationRegistry`` (surface/register/resolve/discover;
      append-only inspection log for reconstruction).
    * **ledger** — the read-only, append-only hash-chained ``CertificationConsoleLedger``
      (``CertificationLedgerView`` + ``CertificationLineageView``).
    * **status** — the deterministic derived ``CertificationPosture`` + status, the
      ``CertificationReadiness`` completeness evaluation, and the ``GovernanceAssessment``.
    * **context** — the resolved ``CertificationContext`` runtime binding.
    * **search** — authorization- and isolation-scoped ``CertificationSearch``.
    * **health** — console health checks + ``CertificationHealth`` (reuses L8 model),
      incl. the fidelity + ledger-integrity checks.
    * **evidence** — the deterministic ``CertificationConsoleEvidence`` runtime evidence.
    * **service** — the ``CertificationConsoleService`` composition root +
      ``CertificationAccess``.
    * **bootstrap** — ``bootstrap_certification_console`` (composes identity +
      observability + the console runtime).
"""

from __future__ import annotations

from platform.certification.bootstrap import (
    CERTIFICATION_CONSOLE_BOOTSTRAP_EVENT,
    bootstrap_certification_console,
)
from platform.certification.context import CertificationContext
from platform.certification.contracts import (
    CERTIFICATION_CONSOLE_CONTRACT_VERSION,
    CERTIFICATION_CONSOLE_CONTRACTS,
    CERTIFICATION_CONSOLE_GROUP,
    EMPTY_CERTIFICATION_METADATA,
    ENGINE_CERTIFICATION_CONTRACT,
    CertificationAction,
    CertificationClass,
    CertificationConsoleRecord,
    CertificationEvidenceReference,
    CertificationRecordMetadata,
    CertificationStatus,
    CertificationSummary,
    CertificationTrace,
    CriterionFindingView,
    CriterionSeverity,
    CriterionStatus,
    all_certification_actions,
    certification_console_contract,
    default_certification_console_contracts,
    permission_for,
)
from platform.certification.errors import (
    CertificationAccessError,
    CertificationConsoleError,
    CertificationContractError,
    CertificationEvidenceError,
    CertificationFidelityError,
    CertificationLedgerError,
    CertificationLineageError,
    CertificationRecordError,
    CertificationSearchError,
    CertificationServiceError,
    CertificationStatusError,
)
from platform.certification.evidence import CertificationConsoleEvidence
from platform.certification.facade import (
    CERTIFICATION_ENGINE_CONTRACTS,
    CertificationFacade,
    SurfacedCertification,
)
from platform.certification.health import (
    EVIDENCE_CHECK,
    FIDELITY_CHECK,
    LEDGER_CHECK,
    REGISTRY_CHECK,
    CertificationHealth,
    certification_console_health_checks,
)
from platform.certification.ledger import (
    CertificationConsoleLedger,
    CertificationLedgerView,
    CertificationLineageView,
)
from platform.certification.registry import CertificationRegistry, InspectionEvent
from platform.certification.search import (
    CertificationSearch,
    CertificationSearchResponse,
    CertificationSearchResult,
)
from platform.certification.service import (
    CERTIFICATION_ACCESS_EVENT,
    CERTIFICATION_CERTIFIED_EVENT,
    CERTIFICATION_EVIDENCE_RENDERED_EVENT,
    CERTIFICATION_GOVERNANCE_VALIDATED_EVENT,
    CERTIFICATION_HEALTH_CHANGED_EVENT,
    CERTIFICATION_INSPECTED_EVENT,
    CERTIFICATION_LEDGER_APPENDED_EVENT,
    CERTIFICATION_LEDGER_VIEWED_EVENT,
    CERTIFICATION_LINEAGE_RENDERED_EVENT,
    CERTIFICATION_NOT_CERTIFIED_EVENT,
    CERTIFICATION_READINESS_EVALUATED_EVENT,
    CERTIFICATION_SEARCHED_EVENT,
    CERTIFICATION_SURFACED_EVENT,
    CERTIFICATION_TRACED_EVENT,
    METRIC_ADVISORY,
    METRIC_BLOCKING_FAILURES,
    METRIC_CERTIFIED,
    METRIC_INSPECTIONS,
    METRIC_LEDGER_APPENDS,
    METRIC_NOT_CERTIFIED,
    METRIC_SURFACED,
    CertificationAccess,
    CertificationConsoleService,
    build_certification_console_service,
)
from platform.certification.status import (
    GOVERNANCE_RULES,
    READINESS_INDICATORS,
    CertificationPosture,
    CertificationReadiness,
    DerivedCertificationStatus,
    GovernanceAssessment,
    GovernanceViolation,
    derive_status,
    evaluate_readiness,
    validate_governance,
)

__all__ = [
    # contracts
    "CERTIFICATION_CONSOLE_CONTRACT_VERSION",
    "CERTIFICATION_CONSOLE_CONTRACTS",
    "CERTIFICATION_CONSOLE_GROUP",
    "ENGINE_CERTIFICATION_CONTRACT",
    "CertificationStatus",
    "CertificationClass",
    "CriterionSeverity",
    "CriterionStatus",
    "CertificationAction",
    "permission_for",
    "all_certification_actions",
    "CertificationRecordMetadata",
    "EMPTY_CERTIFICATION_METADATA",
    "CriterionFindingView",
    "CertificationSummary",
    "CertificationEvidenceReference",
    "CertificationTrace",
    "CertificationConsoleRecord",
    "certification_console_contract",
    "default_certification_console_contracts",
    # facade
    "CERTIFICATION_ENGINE_CONTRACTS",
    "SurfacedCertification",
    "CertificationFacade",
    # registry
    "InspectionEvent",
    "CertificationRegistry",
    # ledger
    "CertificationLedgerView",
    "CertificationLineageView",
    "CertificationConsoleLedger",
    # status / readiness / governance
    "CertificationPosture",
    "DerivedCertificationStatus",
    "derive_status",
    "READINESS_INDICATORS",
    "CertificationReadiness",
    "evaluate_readiness",
    "GOVERNANCE_RULES",
    "GovernanceViolation",
    "GovernanceAssessment",
    "validate_governance",
    # context
    "CertificationContext",
    # search
    "CertificationSearchResult",
    "CertificationSearchResponse",
    "CertificationSearch",
    # health
    "REGISTRY_CHECK",
    "LEDGER_CHECK",
    "FIDELITY_CHECK",
    "EVIDENCE_CHECK",
    "certification_console_health_checks",
    "CertificationHealth",
    # evidence
    "CertificationConsoleEvidence",
    # service
    "CERTIFICATION_SURFACED_EVENT",
    "CERTIFICATION_INSPECTED_EVENT",
    "CERTIFICATION_EVIDENCE_RENDERED_EVENT",
    "CERTIFICATION_LEDGER_VIEWED_EVENT",
    "CERTIFICATION_LINEAGE_RENDERED_EVENT",
    "CERTIFICATION_SEARCHED_EVENT",
    "CERTIFICATION_TRACED_EVENT",
    "CERTIFICATION_CERTIFIED_EVENT",
    "CERTIFICATION_NOT_CERTIFIED_EVENT",
    "CERTIFICATION_READINESS_EVALUATED_EVENT",
    "CERTIFICATION_GOVERNANCE_VALIDATED_EVENT",
    "CERTIFICATION_LEDGER_APPENDED_EVENT",
    "CERTIFICATION_HEALTH_CHANGED_EVENT",
    "CERTIFICATION_ACCESS_EVENT",
    "METRIC_SURFACED",
    "METRIC_CERTIFIED",
    "METRIC_NOT_CERTIFIED",
    "METRIC_ADVISORY",
    "METRIC_INSPECTIONS",
    "METRIC_LEDGER_APPENDS",
    "METRIC_BLOCKING_FAILURES",
    "CertificationAccess",
    "CertificationConsoleService",
    "build_certification_console_service",
    # bootstrap
    "CERTIFICATION_CONSOLE_BOOTSTRAP_EVENT",
    "bootstrap_certification_console",
    # errors
    "CertificationConsoleError",
    "CertificationContractError",
    "CertificationRecordError",
    "CertificationFidelityError",
    "CertificationEvidenceError",
    "CertificationStatusError",
    "CertificationSearchError",
    "CertificationLedgerError",
    "CertificationLineageError",
    "CertificationAccessError",
    "CertificationServiceError",
]
