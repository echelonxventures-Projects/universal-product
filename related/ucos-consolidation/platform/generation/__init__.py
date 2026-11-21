"""UCOS EC-2 Platform Generation Request Runtime (EC2-EPIC-007).

The Generation Request Runtime (L3 Application of the Program architecture, §4) realizes
Program **Surface #8 Generation Requests** (PC-06 generation submission + PC-07 execution
dispatch): it makes the Generation Request the **canonical governed entry point for all
generation activity inside EC-2**. Authorized principals submit generation requests
against a catalog blueprint (EPIC-006, by reference) scoped to a workspace/project, drive
them through a deterministic lifecycle (submitted → validating → approved → queued →
dispatched → running → completed / failed / cancelled), hand approved requests off to the
certified EC-1 Execution Runtime through the single governed dispatch boundary, track
their derived lifecycle + execution status, discover/search them under authorization +
isolation, and carry the ``Generation → Blueprint → Request → Implementation`` link-4
trace continuation — with cross-runtime health, append-only audit, and reproducible
evidence.

Authoritative basis: ``06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md``
(§2.1 surface #8 Generation Requests, PC-06 + PC-07, §3.2 RBAC row ``generation-requests``,
§4 L3/L4, §4.3 EC-1 ``factory``/``compiler``/``runtime``/``determinism`` interaction, §5
EC2-EPIC-007 acceptance, §7 dispatch), as determined by
``platform/generation/EC2-EPIC-007-DETERMINATION.md`` (**IMPLEMENTATION AUTHORIZED**), and
the frozen ``05-GENERATION/`` generation-framework corpus (the definition of the six
generation families and the non-reversible generation chain).

It is a strictly **additive** layer over the certified EC-1 engine and the EC-2
Foundation (EC2-EPIC-001), Identity (EC2-EPIC-002), Observability (EC2-EPIC-013),
Workspace (EC2-EPIC-004), Project Management (EC2-EPIC-005), and Blueprint Catalog
(EC2-EPIC-006) layers: it authorizes only through the Identity Layer on the existing
``generation-requests`` capability group (no new authority, no new capability group),
records the generation family read-only (reusing the frozen
:class:`~platform.blueprints.contracts.BlueprintFamily`; no new classification model),
observes only through the Observability Layer, binds to workspaces/projects/blueprints by
reference, and hands off to EC-1 execution **only by contract reference** (never a live
``engine.*`` import). It modifies neither EC-1 nor any prior layer, never writes to the
certified corpus (DP-03), remains deterministic, starts no server, and opens no socket.

Deliverables (EC2-TASK-000109…000118):
    * **errors** — the ``EC2-GR-*`` error taxonomy over ``PlatformError``.
    * **metadata** — the immutable ``RequestMetadata`` value type.
    * **contracts** — vocabulary (``RequestStatus``, ``ExecutionState``,
      ``RequestAction``, ``GenerationRequest``), the verb→permission map binding the
      ``generation-requests`` group, and ``GENERATION_REQUEST_CONTRACTS``.
    * **lifecycle** — the deterministic request state machine + ``RequestEvent``.
    * **registry** — the ``GenerationRequestRegistry`` (submit/register/resolve/discover/
      transition; append-only event log for reconstruction).
    * **dispatch** — the governed execution-dispatch boundary (``DispatchRecord`` +
      ``DispatchLedger``) bound to the certified EC-1 execution contracts by reference.
    * **provenance** — the link-4 trace continuation (``RequestProvenance`` +
      ``ProvenanceLedger``).
    * **status** — the deterministic derived lifecycle + execution status.
    * **context** — the resolved ``RequestContext`` runtime binding.
    * **search** — authorization- and isolation-scoped ``RequestSearch``.
    * **health** — request health checks + ``RequestHealth`` (reuses L8 model).
    * **service** — the ``GenerationRequestService`` composition root + ``RequestEvidence``.
    * **bootstrap** — ``bootstrap_generation_requests`` (composes identity + observability
      + workspace + the request runtime).
"""

from __future__ import annotations

from platform.generation.bootstrap import (
    GENERATION_REQUEST_BOOTSTRAP_EVENT,
    bootstrap_generation_requests,
)
from platform.generation.context import RequestContext
from platform.generation.contracts import (
    GENERATION_REQUEST_CONTRACT_VERSION,
    GENERATION_REQUEST_CONTRACTS,
    GENERATION_REQUEST_GROUP,
    MUTATING_ACTIONS,
    TERMINAL_STATUSES,
    ExecutionState,
    GenerationRequest,
    RequestAction,
    RequestFamily,
    RequestStatus,
    all_execution_states,
    all_request_actions,
    all_request_statuses,
    default_generation_request_contracts,
    execution_state_for,
    generation_request_contract,
    permission_for,
)
from platform.generation.dispatch import (
    COMPILER_CONTRACT,
    DEFAULT_EXECUTION_TARGET,
    DETERMINISM_CONTRACT,
    DISPATCH_CONTRACTS,
    FACTORY_CONTRACT,
    RUNTIME_CONTRACT,
    DispatchLedger,
    DispatchRecord,
    all_dispatch_contracts,
)
from platform.generation.errors import (
    GenerationRequestError,
    RequestAccessError,
    RequestContractError,
    RequestDispatchError,
    RequestLifecycleError,
    RequestMetadataError,
    RequestProvenanceError,
    RequestRegistryError,
    RequestSearchError,
    RequestServiceError,
    RequestStatusError,
)
from platform.generation.health import (
    DISPATCH_CHECK,
    INTEGRITY_CHECK,
    REGISTRY_CHECK,
    RequestHealth,
    generation_request_health_checks,
)
from platform.generation.lifecycle import (
    RequestEvent,
    allowed_transitions,
    can_transition,
    validate_transition,
)
from platform.generation.metadata import EMPTY_METADATA, RequestMetadata
from platform.generation.provenance import ProvenanceLedger, RequestProvenance
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.search import (
    RequestHit,
    RequestSearch,
    RequestSearchResponse,
)
from platform.generation.service import (
    METRIC_CANCELLED,
    METRIC_COMPLETED,
    METRIC_DISPATCHED,
    METRIC_FAILED,
    METRIC_LIFECYCLE_LATENCY,
    METRIC_QUEUE_DEPTH,
    METRIC_SUBMITTED,
    REQUEST_ACCESS_EVENT,
    REQUEST_APPROVED_EVENT,
    REQUEST_CANCELLED_EVENT,
    REQUEST_COMPLETED_EVENT,
    REQUEST_DISPATCHED_EVENT,
    REQUEST_FAILED_EVENT,
    REQUEST_HEALTH_CHANGED_EVENT,
    REQUEST_METADATA_UPDATED_EVENT,
    REQUEST_PROVENANCE_LINKED_EVENT,
    REQUEST_QUEUED_EVENT,
    REQUEST_RUNNING_EVENT,
    REQUEST_SUBMITTED_EVENT,
    REQUEST_VALIDATING_EVENT,
    GenerationRequestService,
    RequestAccess,
    RequestEvidence,
    build_generation_request_service,
)
from platform.generation.status import (
    DerivedRequestStatus,
    RequestPosture,
    derive_status,
)

__all__ = [
    # contracts
    "GENERATION_REQUEST_CONTRACT_VERSION",
    "GENERATION_REQUEST_CONTRACTS",
    "GENERATION_REQUEST_GROUP",
    "RequestFamily",
    "RequestStatus",
    "ExecutionState",
    "RequestAction",
    "TERMINAL_STATUSES",
    "MUTATING_ACTIONS",
    "permission_for",
    "execution_state_for",
    "all_request_statuses",
    "all_execution_states",
    "all_request_actions",
    "GenerationRequest",
    "generation_request_contract",
    "default_generation_request_contracts",
    # metadata
    "RequestMetadata",
    "EMPTY_METADATA",
    # lifecycle
    "RequestEvent",
    "allowed_transitions",
    "can_transition",
    "validate_transition",
    # registry
    "GenerationRequestRegistry",
    # dispatch
    "FACTORY_CONTRACT",
    "COMPILER_CONTRACT",
    "RUNTIME_CONTRACT",
    "DETERMINISM_CONTRACT",
    "DISPATCH_CONTRACTS",
    "DEFAULT_EXECUTION_TARGET",
    "DispatchRecord",
    "DispatchLedger",
    "all_dispatch_contracts",
    # provenance
    "RequestProvenance",
    "ProvenanceLedger",
    # status
    "RequestPosture",
    "DerivedRequestStatus",
    "derive_status",
    # context
    "RequestContext",
    # search
    "RequestHit",
    "RequestSearchResponse",
    "RequestSearch",
    # health
    "REGISTRY_CHECK",
    "DISPATCH_CHECK",
    "INTEGRITY_CHECK",
    "generation_request_health_checks",
    "RequestHealth",
    # service
    "REQUEST_SUBMITTED_EVENT",
    "REQUEST_VALIDATING_EVENT",
    "REQUEST_APPROVED_EVENT",
    "REQUEST_QUEUED_EVENT",
    "REQUEST_DISPATCHED_EVENT",
    "REQUEST_RUNNING_EVENT",
    "REQUEST_COMPLETED_EVENT",
    "REQUEST_FAILED_EVENT",
    "REQUEST_CANCELLED_EVENT",
    "REQUEST_METADATA_UPDATED_EVENT",
    "REQUEST_PROVENANCE_LINKED_EVENT",
    "REQUEST_HEALTH_CHANGED_EVENT",
    "REQUEST_ACCESS_EVENT",
    "METRIC_SUBMITTED",
    "METRIC_DISPATCHED",
    "METRIC_COMPLETED",
    "METRIC_FAILED",
    "METRIC_CANCELLED",
    "METRIC_QUEUE_DEPTH",
    "METRIC_LIFECYCLE_LATENCY",
    "RequestAccess",
    "RequestEvidence",
    "GenerationRequestService",
    "build_generation_request_service",
    # bootstrap
    "GENERATION_REQUEST_BOOTSTRAP_EVENT",
    "bootstrap_generation_requests",
    # errors
    "GenerationRequestError",
    "RequestContractError",
    "RequestMetadataError",
    "RequestLifecycleError",
    "RequestRegistryError",
    "RequestDispatchError",
    "RequestProvenanceError",
    "RequestStatusError",
    "RequestSearchError",
    "RequestAccessError",
    "RequestServiceError",
]
