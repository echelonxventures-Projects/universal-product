"""UCOS EC-2 Platform Validation Console Runtime (EC2-EPIC-010).

The Validation Console Runtime (L3 Application of the Program architecture, §4) realizes
Program **Surface #9 Validation Explorer** (PC-09 validation inspection + PC-13 search +
PC-16 audit): it makes the certified EC-1 validation output **inspectable, searchable,
and traceable** to authorized principals, **faithfully** — every surfaced report,
evidence record, and acceptance decision is byte-for-byte the certified engine output
(P6). Authorized principals surface a validation for a target (the certified engine is
reproduced read-only over its subject), inspect the report/findings, view the evidence
reference and acceptance decision, track the derived posture, discover/search validations
under authorization + isolation, and navigate the Request → Target → Validation trace
edge — with cross-runtime health (including a machine-checkable fidelity check),
append-only audit, and reproducible evidence.

Authoritative basis: ``06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md``
(§2.1 surface #9 Validation Explorer, PC-09/PC-13/PC-16, §3.2 RBAC row
``validation-explorer``, §4 L3/L4, §4.3 EC-1 ``validation`` interaction, §5 EC2-EPIC-010
acceptance, §9 P6 Validation Fidelity), as determined by
``platform/validation/EC2-EPIC-010-DETERMINATION.md`` (**IMPLEMENTATION AUTHORIZED**), and
the certified EC-1 Validation Layer (``engine/validation/``, consumed read-only by
reference).

It is a strictly **additive**, **read/inspection-only** layer over the certified EC-1
engine and the EC-2 Foundation (EC2-EPIC-001), Identity (EC2-EPIC-002), and Observability
(EC2-EPIC-013) layers: it authorizes only through the Identity Layer on the existing
``validation-explorer`` capability group (no new authority, no new capability group),
consumes ``engine.validation`` **only by reference** (the L4 façade invokes the certified
``ValidationEngine`` read-only; no check/verdict/gate/evidence-format is redefined),
observes only through the Observability Layer, and exposes **no mutation path** to any
surfaced report, evidence, or acceptance decision. It modifies neither EC-1 nor any prior
layer, never writes to the certified corpus (DP-03), remains deterministic, starts no
server, and opens no socket.

Deliverables (EC2-TASK-000145…000152):
    * **errors** — the ``EC2-VC-*`` error taxonomy over ``PlatformError``.
    * **metadata** — the immutable ``ValidationRecordMetadata`` value type.
    * **contracts** — vocabulary (``ValidationAction``, re-exported engine
      ``Verdict``/``Severity``/``CheckStatus``), the read-only view projections
      (``FindingView``, ``ValidationSummary``, ``ValidationDecisionView``,
      ``ValidationEvidenceReference``, ``ValidationTrace``), the ``ValidationRecord``
      aggregate, the verb→permission map binding the ``validation-explorer`` group, and
      ``VALIDATION_CONSOLE_CONTRACTS``.
    * **facade** — the read-only EC-1 façade (``ValidationFacade`` + ``SurfacedValidation``)
      consuming ``engine.validation`` by reference.
    * **registry** — the ``ValidationRecordRegistry`` (surface/register/resolve/discover;
      append-only inspection log for reconstruction).
    * **status** — the deterministic derived ``ValidationPosture`` + status.
    * **context** — the resolved ``ValidationContext`` runtime binding.
    * **search** — authorization- and isolation-scoped ``ValidationSearch``.
    * **health** — console health checks + ``ValidationHealth`` (reuses L8 model), incl.
      the fidelity check.
    * **evidence** — the deterministic ``ValidationConsoleEvidence`` runtime evidence.
    * **service** — the ``ValidationConsoleService`` composition root + ``ValidationAccess``.
    * **bootstrap** — ``bootstrap_validation_console`` (composes identity + observability
      + the console runtime).
"""

from __future__ import annotations

from platform.validation.bootstrap import (
    VALIDATION_CONSOLE_BOOTSTRAP_EVENT,
    bootstrap_validation_console,
)
from platform.validation.context import ValidationContext
from platform.validation.contracts import (
    ENGINE_VALIDATION_CONTRACT,
    VALIDATION_CONSOLE_CONTRACT_VERSION,
    VALIDATION_CONSOLE_CONTRACTS,
    VALIDATION_CONSOLE_GROUP,
    CheckStatus,
    FindingView,
    Severity,
    ValidationAction,
    ValidationDecisionView,
    ValidationEvidenceReference,
    ValidationRecord,
    ValidationSummary,
    ValidationTrace,
    Verdict,
    all_validation_actions,
    default_validation_console_contracts,
    permission_for,
    validation_console_contract,
)
from platform.validation.errors import (
    ValidationAccessError,
    ValidationConsoleError,
    ValidationContractError,
    ValidationEvidenceError,
    ValidationFidelityError,
    ValidationRecordError,
    ValidationSearchError,
    ValidationServiceError,
    ValidationStatusError,
    ValidationTraceError,
)
from platform.validation.evidence import ValidationConsoleEvidence
from platform.validation.facade import (
    VALIDATION_ENGINE_CONTRACTS,
    SurfacedValidation,
    ValidationFacade,
)
from platform.validation.health import (
    EVIDENCE_CHECK,
    FIDELITY_CHECK,
    REGISTRY_CHECK,
    ValidationHealth,
    validation_console_health_checks,
)
from platform.validation.metadata import (
    EMPTY_VALIDATION_METADATA,
    ValidationRecordMetadata,
)
from platform.validation.registry import InspectionEvent, ValidationRecordRegistry
from platform.validation.search import (
    ValidationSearch,
    ValidationSearchResponse,
    ValidationSearchResult,
)
from platform.validation.service import (
    METRIC_ACCEPTED,
    METRIC_ADVISORY,
    METRIC_BLOCKING_FAILURES,
    METRIC_INSPECTIONS,
    METRIC_REJECTED,
    METRIC_SURFACED,
    VALIDATION_ACCEPTED_EVENT,
    VALIDATION_ACCESS_EVENT,
    VALIDATION_DECISION_RENDERED_EVENT,
    VALIDATION_EVIDENCE_RENDERED_EVENT,
    VALIDATION_HEALTH_CHANGED_EVENT,
    VALIDATION_INSPECTED_EVENT,
    VALIDATION_REJECTED_EVENT,
    VALIDATION_SEARCHED_EVENT,
    VALIDATION_SURFACED_EVENT,
    VALIDATION_TRACED_EVENT,
    ValidationAccess,
    ValidationConsoleService,
    build_validation_console_service,
)
from platform.validation.status import (
    DerivedValidationStatus,
    ValidationPosture,
    derive_status,
)

__all__ = [
    # contracts
    "VALIDATION_CONSOLE_CONTRACT_VERSION",
    "VALIDATION_CONSOLE_CONTRACTS",
    "VALIDATION_CONSOLE_GROUP",
    "ENGINE_VALIDATION_CONTRACT",
    "Verdict",
    "Severity",
    "CheckStatus",
    "ValidationAction",
    "permission_for",
    "all_validation_actions",
    "FindingView",
    "ValidationSummary",
    "ValidationDecisionView",
    "ValidationEvidenceReference",
    "ValidationTrace",
    "ValidationRecord",
    "validation_console_contract",
    "default_validation_console_contracts",
    # metadata
    "ValidationRecordMetadata",
    "EMPTY_VALIDATION_METADATA",
    # facade
    "VALIDATION_ENGINE_CONTRACTS",
    "SurfacedValidation",
    "ValidationFacade",
    # registry
    "InspectionEvent",
    "ValidationRecordRegistry",
    # status
    "ValidationPosture",
    "DerivedValidationStatus",
    "derive_status",
    # context
    "ValidationContext",
    # search
    "ValidationSearchResult",
    "ValidationSearchResponse",
    "ValidationSearch",
    # health
    "REGISTRY_CHECK",
    "FIDELITY_CHECK",
    "EVIDENCE_CHECK",
    "validation_console_health_checks",
    "ValidationHealth",
    # evidence
    "ValidationConsoleEvidence",
    # service
    "VALIDATION_SURFACED_EVENT",
    "VALIDATION_INSPECTED_EVENT",
    "VALIDATION_EVIDENCE_RENDERED_EVENT",
    "VALIDATION_DECISION_RENDERED_EVENT",
    "VALIDATION_SEARCHED_EVENT",
    "VALIDATION_TRACED_EVENT",
    "VALIDATION_ACCEPTED_EVENT",
    "VALIDATION_REJECTED_EVENT",
    "VALIDATION_HEALTH_CHANGED_EVENT",
    "VALIDATION_ACCESS_EVENT",
    "METRIC_SURFACED",
    "METRIC_ACCEPTED",
    "METRIC_REJECTED",
    "METRIC_ADVISORY",
    "METRIC_INSPECTIONS",
    "METRIC_BLOCKING_FAILURES",
    "ValidationAccess",
    "ValidationConsoleService",
    "build_validation_console_service",
    # bootstrap
    "VALIDATION_CONSOLE_BOOTSTRAP_EVENT",
    "bootstrap_validation_console",
    # errors
    "ValidationConsoleError",
    "ValidationContractError",
    "ValidationRecordError",
    "ValidationFidelityError",
    "ValidationEvidenceError",
    "ValidationStatusError",
    "ValidationSearchError",
    "ValidationTraceError",
    "ValidationAccessError",
    "ValidationServiceError",
]
