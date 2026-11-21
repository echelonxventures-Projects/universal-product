"""UCOS EC-2 Platform Runtime Operations Runtime (EC2-EPIC-012).

The Runtime Operations Runtime (L8 Operations of the Program architecture, §4) realizes
Program **Surface #11 Runtime Operations** (PC-11 runtime deploy/rollback operations +
PC-13 search + PC-16 audit): it **governs and records** the deployment and rollback of
CERTIFIED runtime units **strictly through EC-1 runtime descriptors**, faithfully — every
surfaced descriptor is byte-for-byte the certified engine output (P6). Authorized
principals govern a deploy or a reversible rollback of a certified unit (the certified
EC-1 runtime descriptor/rollback factories are reproduced read-only over an
already-assembled unit), discover and inspect deployment/rollback descriptors, navigate
the append-only hash-chained operation ledger and an operation's lineage, track the
derived posture, verify reversibility (IP-08), validate operation governance,
discover/search operations under authorization + isolation — with cross-runtime health
(including a machine-checkable fidelity check and a reversibility check), append-only
audit, and reproducible evidence.

Authoritative basis: ``06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md``
(§2.1 surface #11 Runtime Operations, PC-11/PC-13/PC-16, §3.2 RBAC row
``runtime-operations``, §4 L4/L8, §4.3 EC-1 ``runtime`` interaction, §5 EC2-EPIC-012
acceptance, §9 P6 Fidelity), the certified EC-1 Runtime Assembly Layer
(``engine/runtime/``, consumed read-only by reference), and the certified Certification
Console (``platform/certification/``, consumed by reference for certification status).

It is a strictly **additive**, **govern/record-only** layer over the certified EC-1 engine
and the EC-2 Foundation (EC2-EPIC-001), Identity (EC2-EPIC-002), Certification
(EC2-EPIC-011), and Observability (EC2-EPIC-013) layers: it authorizes only through the
Identity Layer on the existing ``runtime-operations`` capability group (no new authority,
no new capability group), consumes ``engine.runtime`` **only by reference** (the L4 façade
invokes the certified descriptor/rollback factories read-only; no descriptor format,
rollback strategy, disclosure, or reversibility rule is redefined), admits **only CERTIFIED
units**, observes only through the Observability Layer, and exposes **no mutation path** to
any surfaced descriptor, certification record, or ledger entry (the operation ledger is
append-only by construction). The actual runtime execution remains inside EC-1. It modifies
neither EC-1 nor any prior layer, never writes to the certified corpus (DP-03), remains
deterministic, starts no server, and opens no socket.

Deliverables (EC2-TASK-000163…000172):
    * **errors** — the ``EC2-RO-*`` error taxonomy over ``PlatformError``.
    * **contracts** — vocabulary (``RuntimeOperationKind``, ``RuntimeOperationAction``),
      the descriptive ``RuntimeOperationMetadata``, the read-only view projections
      (``RuntimeUnitReference``, ``CertificationReference``, ``DeploymentDescriptorView``,
      ``RollbackDescriptorView``), the ``RuntimeOperationRecord`` aggregate, the
      verb→permission map binding the ``runtime-operations`` group, and
      ``RUNTIME_OPERATIONS_CONTRACTS``.
    * **facade** — the read-only EC-1 façade (``RuntimeFacade``) consuming ``engine.runtime``
      by reference (deploy/rollback descriptor generation + fidelity).
    * **descriptors** — the ``DescriptorCatalog`` (deploy/rollback discovery + inspection).
    * **guard** — the CERTIFIED-only ``RuntimeAdmissionGuard`` + ``AdmissionDecision``.
    * **operations** — the ``RuntimeOperationPlanner`` orchestration + ``RuntimeOperationPlan``
      and the append-only ``RuntimeOperationRegistry``.
    * **ledger** — the read-only, append-only hash-chained ``RuntimeOperationLedger``
      (``RuntimeOperationLedgerView`` + ``RuntimeOperationLineageView``).
    * **reversibility** — the IP-08 ``ReversibilityProof`` + ``prove_reversibility``.
    * **status** — the deterministic derived ``RuntimeOperationPosture`` + status and the
      ``GovernanceAssessment``.
    * **context** — the resolved ``RuntimeOperationContext`` runtime binding.
    * **search** — authorization- and isolation-scoped ``RuntimeOperationSearch``.
    * **health** — runtime health checks + ``RuntimeOperationsHealth`` (reuses L8 model),
      incl. the fidelity + reversibility checks.
    * **service** — the ``RuntimeOperationsService`` composition root + ``RuntimeOperationAccess``
      + ``RuntimeOperationEvidence``.
    * **bootstrap** — ``bootstrap_runtime_operations`` (composes identity + observability +
      the runtime).
"""

from __future__ import annotations

from platform.runtime_operations.bootstrap import (
    RUNTIME_OPERATIONS_BOOTSTRAP_EVENT,
    bootstrap_runtime_operations,
)
from platform.runtime_operations.context import RuntimeOperationContext
from platform.runtime_operations.contracts import (
    EMPTY_RUNTIME_OPERATION_METADATA,
    ENGINE_RUNTIME_ASSEMBLE_CONTRACT,
    ENGINE_RUNTIME_DEPLOY_CONTRACT,
    RUNTIME_OPERATIONS_CONTRACT_VERSION,
    RUNTIME_OPERATIONS_CONTRACTS,
    RUNTIME_OPERATIONS_GROUP,
    CertificationReference,
    DeploymentDescriptorView,
    RollbackDescriptorView,
    RuntimeOperationAction,
    RuntimeOperationKind,
    RuntimeOperationMetadata,
    RuntimeOperationRecord,
    RuntimeUnitReference,
    action_for_kind,
    all_runtime_operation_actions,
    default_runtime_operations_contracts,
    permission_for,
    runtime_operations_contract,
)
from platform.runtime_operations.descriptors import DescriptorCatalog
from platform.runtime_operations.errors import (
    RuntimeAdmissionError,
    RuntimeDescriptorError,
    RuntimeFidelityError,
    RuntimeOperationAccessError,
    RuntimeOperationLedgerError,
    RuntimeOperationLineageError,
    RuntimeOperationRecordError,
    RuntimeOperationsContractError,
    RuntimeOperationSearchError,
    RuntimeOperationsError,
    RuntimeOperationServiceError,
    RuntimeOperationStatusError,
    RuntimeReversibilityError,
)
from platform.runtime_operations.facade import RUNTIME_ENGINE_CONTRACTS, RuntimeFacade
from platform.runtime_operations.guard import (
    ADMISSION_CRITERIA,
    AdmissionDecision,
    RuntimeAdmissionGuard,
)
from platform.runtime_operations.health import (
    FIDELITY_CHECK,
    LEDGER_CHECK,
    REGISTRY_CHECK,
    REVERSIBILITY_CHECK,
    RuntimeOperationsHealth,
    runtime_operations_health_checks,
)
from platform.runtime_operations.ledger import (
    GENESIS_HASH,
    RuntimeOperationLedger,
    RuntimeOperationLedgerEntry,
    RuntimeOperationLedgerView,
    RuntimeOperationLineageView,
)
from platform.runtime_operations.operations import (
    InspectionEvent,
    RuntimeOperationPlan,
    RuntimeOperationPlanner,
    RuntimeOperationRegistry,
)
from platform.runtime_operations.reversibility import (
    REVERSIBILITY_INDICATORS,
    ReversibilityProof,
    prove_reversibility,
)
from platform.runtime_operations.search import (
    RuntimeOperationSearch,
    RuntimeOperationSearchResponse,
    RuntimeOperationSearchResult,
)
from platform.runtime_operations.service import (
    METRIC_CLOSURE_SIZE,
    METRIC_DEPLOYS,
    METRIC_INSPECTIONS,
    METRIC_LEDGER_APPENDS,
    METRIC_OPERATIONS,
    METRIC_ROLLBACKS,
    RUNTIME_DEPLOY_APPLIED_EVENT,
    RUNTIME_DESCRIPTOR_INSPECTED_EVENT,
    RUNTIME_GOVERNANCE_VALIDATED_EVENT,
    RUNTIME_HEALTH_CHANGED_EVENT,
    RUNTIME_LEDGER_APPENDED_EVENT,
    RUNTIME_LEDGER_VIEWED_EVENT,
    RUNTIME_LINEAGE_RENDERED_EVENT,
    RUNTIME_OPERATION_ACCESS_EVENT,
    RUNTIME_OPERATION_INSPECTED_EVENT,
    RUNTIME_OPERATION_RECORDED_EVENT,
    RUNTIME_OPERATION_SEARCHED_EVENT,
    RUNTIME_OPERATION_TRACKED_EVENT,
    RUNTIME_REVERSIBILITY_VERIFIED_EVENT,
    RUNTIME_ROLLBACK_APPLIED_EVENT,
    RuntimeOperationAccess,
    RuntimeOperationEvidence,
    RuntimeOperationsService,
    build_runtime_operations_service,
)
from platform.runtime_operations.status import (
    GOVERNANCE_RULES,
    DerivedRuntimeOperationStatus,
    GovernanceAssessment,
    GovernanceViolation,
    RuntimeOperationPosture,
    derive_status,
    validate_governance,
)

__all__ = [
    # contracts
    "RUNTIME_OPERATIONS_CONTRACT_VERSION",
    "RUNTIME_OPERATIONS_CONTRACTS",
    "RUNTIME_OPERATIONS_GROUP",
    "ENGINE_RUNTIME_ASSEMBLE_CONTRACT",
    "ENGINE_RUNTIME_DEPLOY_CONTRACT",
    "RuntimeOperationKind",
    "RuntimeOperationAction",
    "permission_for",
    "all_runtime_operation_actions",
    "action_for_kind",
    "RuntimeOperationMetadata",
    "EMPTY_RUNTIME_OPERATION_METADATA",
    "RuntimeUnitReference",
    "CertificationReference",
    "DeploymentDescriptorView",
    "RollbackDescriptorView",
    "RuntimeOperationRecord",
    "runtime_operations_contract",
    "default_runtime_operations_contracts",
    # facade
    "RUNTIME_ENGINE_CONTRACTS",
    "RuntimeFacade",
    # descriptors
    "DescriptorCatalog",
    # guard
    "ADMISSION_CRITERIA",
    "AdmissionDecision",
    "RuntimeAdmissionGuard",
    # operations
    "RuntimeOperationPlan",
    "RuntimeOperationPlanner",
    "InspectionEvent",
    "RuntimeOperationRegistry",
    # ledger
    "GENESIS_HASH",
    "RuntimeOperationLedgerEntry",
    "RuntimeOperationLedgerView",
    "RuntimeOperationLineageView",
    "RuntimeOperationLedger",
    # reversibility
    "REVERSIBILITY_INDICATORS",
    "ReversibilityProof",
    "prove_reversibility",
    # status / governance
    "RuntimeOperationPosture",
    "DerivedRuntimeOperationStatus",
    "derive_status",
    "GOVERNANCE_RULES",
    "GovernanceViolation",
    "GovernanceAssessment",
    "validate_governance",
    # context
    "RuntimeOperationContext",
    # search
    "RuntimeOperationSearchResult",
    "RuntimeOperationSearchResponse",
    "RuntimeOperationSearch",
    # health
    "REGISTRY_CHECK",
    "LEDGER_CHECK",
    "FIDELITY_CHECK",
    "REVERSIBILITY_CHECK",
    "runtime_operations_health_checks",
    "RuntimeOperationsHealth",
    # service
    "RUNTIME_DEPLOY_APPLIED_EVENT",
    "RUNTIME_ROLLBACK_APPLIED_EVENT",
    "RUNTIME_OPERATION_RECORDED_EVENT",
    "RUNTIME_LEDGER_APPENDED_EVENT",
    "RUNTIME_OPERATION_INSPECTED_EVENT",
    "RUNTIME_DESCRIPTOR_INSPECTED_EVENT",
    "RUNTIME_LEDGER_VIEWED_EVENT",
    "RUNTIME_LINEAGE_RENDERED_EVENT",
    "RUNTIME_OPERATION_SEARCHED_EVENT",
    "RUNTIME_OPERATION_TRACKED_EVENT",
    "RUNTIME_REVERSIBILITY_VERIFIED_EVENT",
    "RUNTIME_GOVERNANCE_VALIDATED_EVENT",
    "RUNTIME_HEALTH_CHANGED_EVENT",
    "RUNTIME_OPERATION_ACCESS_EVENT",
    "METRIC_OPERATIONS",
    "METRIC_DEPLOYS",
    "METRIC_ROLLBACKS",
    "METRIC_LEDGER_APPENDS",
    "METRIC_INSPECTIONS",
    "METRIC_CLOSURE_SIZE",
    "RuntimeOperationAccess",
    "RuntimeOperationEvidence",
    "RuntimeOperationsService",
    "build_runtime_operations_service",
    # bootstrap
    "RUNTIME_OPERATIONS_BOOTSTRAP_EVENT",
    "bootstrap_runtime_operations",
    # errors
    "RuntimeOperationsError",
    "RuntimeOperationsContractError",
    "RuntimeOperationRecordError",
    "RuntimeDescriptorError",
    "RuntimeAdmissionError",
    "RuntimeFidelityError",
    "RuntimeReversibilityError",
    "RuntimeOperationStatusError",
    "RuntimeOperationSearchError",
    "RuntimeOperationLedgerError",
    "RuntimeOperationLineageError",
    "RuntimeOperationAccessError",
    "RuntimeOperationServiceError",
]
