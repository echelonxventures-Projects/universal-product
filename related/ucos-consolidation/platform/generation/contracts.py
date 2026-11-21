"""EC2-TASK-000109 — Generation Request Contracts (EC2-EPIC-007).

The versioned contract surface for the UCOS Platform **Generation Request Runtime**
(L3 Application of the Program architecture, §4) plus the immutable **core vocabulary**
every generation-request service speaks. It reuses the certified EC-1 contract
machinery through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and binds request authorization to
the single §3.2 :class:`~platform.identity.contracts.CapabilityGroup`
``generation-requests`` (PC-06/PC-07, matrix index 6) that **already physically exists**
in the certified Identity Layer. EC2-EPIC-007 introduces **no new capability group, no
new authority, and no new authorization logic**.

It also reuses — rather than reinventing — the frozen generation classification model:
the recorded generation ``family`` is one of the six frozen
:class:`~platform.blueprints.contracts.BlueprintFamily` members (the ``05-GENERATION``
Data → Event → API → Workflow → Service → Application chain). The runtime **records**
this classification read-only; it computes none (no alternative classification system,
P10).

Vocabulary:
    * :class:`RequestStatus` — the nine lifecycle states a request occupies
      (``submitted`` → ``validating`` → ``approved`` → ``queued`` → ``dispatched`` →
      ``running`` → ``completed`` / ``failed`` / ``cancelled``); the last three are
      terminal.
    * :class:`ExecutionState` — the derived execution posture of a request (a pure
      function of its lifecycle state): ``pending`` / ``dispatched`` / ``executing`` /
      ``succeeded`` / ``failed`` / ``aborted``.
    * :class:`RequestAction` — the governed request verbs, each mapped to the coarse
      RBAC :class:`~platform.foundation.identity.Permission` it requires.
    * :class:`GenerationRequest` — an immutable, content-addressed request aggregate
      scoped to a parent workspace/project, referencing a catalog blueprint **by
      reference**, carrying identity, ownership, provenance (blueprint ref + submitted
      tick), recorded classification, lifecycle state, and metadata.
    * :data:`GENERATION_REQUEST_CONTRACTS` — the published request service contracts
      consumers (EPIC-008/009/010 dashboards & consoles) bind to by reference
      (PL-05, versioned).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.generation.errors import RequestContractError
from platform.generation.metadata import EMPTY_METADATA, RequestMetadata
from platform.identity.contracts import CapabilityGroup
from typing import Any

#: The semantic version of the Generation Request Runtime contract surface (AR-03/PL-05).
GENERATION_REQUEST_CONTRACT_VERSION = "1.0.0"

#: The §3.2 capability group authorizing every generation-request action (reused; no new group).
GENERATION_REQUEST_GROUP = CapabilityGroup.GENERATION_REQUESTS

#: Re-export of the frozen generation family vocabulary (recorded, never computed).
RequestFamily = BlueprintFamily


class RequestStatus(str, Enum):
    """The lifecycle states a generation request occupies.

    ``submitted`` (received) → ``validating`` (structural/governance pre-checks) →
    ``approved`` (admitted) → ``queued`` (awaiting dispatch) → ``dispatched`` (handed
    off to the Execution Runtime) → ``running`` (executing) → ``completed`` (success) /
    ``failed`` (error) / ``cancelled`` (withdrawn). ``completed`` / ``failed`` /
    ``cancelled`` are terminal.
    """

    SUBMITTED = "submitted"
    VALIDATING = "validating"
    APPROVED = "approved"
    QUEUED = "queued"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionState(str, Enum):
    """The derived execution posture of a request (a pure function of lifecycle state)."""

    PENDING = "pending"
    DISPATCHED = "dispatched"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ABORTED = "aborted"


class RequestAction(str, Enum):
    """The governed generation-request verbs (each mapped to a required RBAC permission)."""

    SUBMIT = "submit"
    INSPECT = "inspect"
    DISCOVER = "discover"
    SEARCH = "search"
    TRACK = "track"
    TRACE = "trace"
    VALIDATE = "validate"
    APPROVE = "approve"
    QUEUE = "queue"
    DISPATCH = "dispatch"
    RUN = "run"
    COMPLETE = "complete"
    FAIL = "fail"
    CANCEL = "cancel"


#: The lifecycle → execution-posture map (pure, total, deterministic).
_EXECUTION_STATE: dict[RequestStatus, ExecutionState] = {
    RequestStatus.SUBMITTED: ExecutionState.PENDING,
    RequestStatus.VALIDATING: ExecutionState.PENDING,
    RequestStatus.APPROVED: ExecutionState.PENDING,
    RequestStatus.QUEUED: ExecutionState.PENDING,
    RequestStatus.DISPATCHED: ExecutionState.DISPATCHED,
    RequestStatus.RUNNING: ExecutionState.EXECUTING,
    RequestStatus.COMPLETED: ExecutionState.SUCCEEDED,
    RequestStatus.FAILED: ExecutionState.FAILED,
    RequestStatus.CANCELLED: ExecutionState.ABORTED,
}

#: The terminal lifecycle states (no outgoing transition).
TERMINAL_STATUSES: frozenset[RequestStatus] = frozenset(
    {RequestStatus.COMPLETED, RequestStatus.FAILED, RequestStatus.CANCELLED}
)

#: The verb→permission map (Determination §9). Read verbs require READ; submission and
#: governance mutations (validate/approve/queue/cancel) require CREATE; execution
#: mutations (dispatch/run/complete/fail) require EXECUTE — the coarse pipeline verb the
#: §3.2 matrix grants Architect/Developer/Business/Partner/Integrator on this group.
_ACTION_PERMISSIONS: dict[RequestAction, Permission] = {
    RequestAction.SUBMIT: Permission.CREATE,
    RequestAction.INSPECT: Permission.READ,
    RequestAction.DISCOVER: Permission.READ,
    RequestAction.SEARCH: Permission.READ,
    RequestAction.TRACK: Permission.READ,
    RequestAction.TRACE: Permission.READ,
    RequestAction.VALIDATE: Permission.CREATE,
    RequestAction.APPROVE: Permission.CREATE,
    RequestAction.QUEUE: Permission.CREATE,
    RequestAction.CANCEL: Permission.CREATE,
    RequestAction.DISPATCH: Permission.EXECUTE,
    RequestAction.RUN: Permission.EXECUTE,
    RequestAction.COMPLETE: Permission.EXECUTE,
    RequestAction.FAIL: Permission.EXECUTE,
}

#: The request actions that mutate runtime state (require ownership or administrator).
MUTATING_ACTIONS: frozenset[RequestAction] = frozenset(
    {
        RequestAction.SUBMIT,
        RequestAction.VALIDATE,
        RequestAction.APPROVE,
        RequestAction.QUEUE,
        RequestAction.CANCEL,
        RequestAction.DISPATCH,
        RequestAction.RUN,
        RequestAction.COMPLETE,
        RequestAction.FAIL,
    }
)


def permission_for(action: RequestAction) -> Permission:
    """Return the RBAC permission required by a request action (fail-closed)."""
    if not isinstance(action, RequestAction):
        raise RequestContractError("action must be a RequestAction")
    return _ACTION_PERMISSIONS[action]


def execution_state_for(status: RequestStatus) -> ExecutionState:
    """Return the derived execution posture for a lifecycle status (pure; fail-closed)."""
    if not isinstance(status, RequestStatus):
        raise RequestContractError("status must be a RequestStatus")
    return _EXECUTION_STATE[status]


def all_request_statuses() -> tuple[RequestStatus, ...]:
    """Return every request status in stable declaration order."""
    return tuple(RequestStatus)


def all_execution_states() -> tuple[ExecutionState, ...]:
    """Return every execution state in stable declaration order."""
    return tuple(ExecutionState)


def all_request_actions() -> tuple[RequestAction, ...]:
    """Return every request action in stable declaration order."""
    return tuple(RequestAction)


def _require_slug(slug: str) -> str:
    if not isinstance(slug, str) or not slug:
        raise RequestContractError("request slug is required")
    normalized = slug.strip().lower()
    if not normalized or any(c.isspace() for c in normalized):
        raise RequestContractError("request slug must be non-empty and whitespace-free")
    return normalized


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """An immutable, content-addressed generation request scoped to a workspace/project.

    A request's identity is content-addressed from its ``slug``, parent
    ``workspace_id``, referenced ``blueprint_ref``, and ``submitted_tick`` — so
    registration is idempotent and reproducible for identical submissions; mutable
    facets (status, metadata) never change the id. The ``tenant`` is inherited from the
    parent workspace at creation and is the request's isolation boundary (reused
    workspace isolation rule, P3). The recorded ``family`` is the EC-1 classification
    (via the referenced blueprint) the platform records read-only.
    """

    request_id: str
    slug: str
    blueprint_ref: str
    workspace_id: str
    project_id: str | None
    tenant: str | None
    owner_subject: str
    family: BlueprintFamily
    status: RequestStatus
    submitted_tick: int
    metadata: RequestMetadata

    @classmethod
    def create(
        cls,
        slug: str,
        blueprint_ref: str,
        workspace_id: str,
        owner_subject: str,
        family: BlueprintFamily,
        *,
        submitted_tick: int,
        project_id: str | None = None,
        tenant: str | None = None,
        status: RequestStatus = RequestStatus.SUBMITTED,
        metadata: RequestMetadata | None = None,
    ) -> GenerationRequest:
        """Build a request with a deterministic, content-addressed ``request_id``."""
        normalized_slug = _require_slug(slug)
        if not isinstance(blueprint_ref, str) or not blueprint_ref:
            raise RequestContractError("request requires a blueprint_ref", slug=normalized_slug)
        if not isinstance(workspace_id, str) or not workspace_id:
            raise RequestContractError("request requires a workspace_id", slug=normalized_slug)
        if not isinstance(owner_subject, str) or not owner_subject:
            raise RequestContractError("request owner_subject is required", slug=normalized_slug)
        if not isinstance(family, BlueprintFamily):
            raise RequestContractError("request family must be a BlueprintFamily")
        if not isinstance(status, RequestStatus):
            raise RequestContractError("request status must be a RequestStatus")
        if not isinstance(submitted_tick, int) or isinstance(submitted_tick, bool):
            raise RequestContractError(
                "request submitted_tick must be an int", slug=normalized_slug
            )
        if project_id is not None and (not isinstance(project_id, str) or not project_id):
            raise RequestContractError(
                "request project_id must be a non-empty string when provided",
                slug=normalized_slug,
            )
        md = metadata if metadata is not None else EMPTY_METADATA
        if not isinstance(md, RequestMetadata):
            raise RequestContractError("request metadata must be a RequestMetadata")
        identity = {
            "slug": normalized_slug,
            "workspace_id": workspace_id,
            "blueprint_ref": blueprint_ref,
            "submitted_tick": submitted_tick,
        }
        return cls(
            request_id=f"UCOS-GREQ-{content_hash(identity)[:16]}",
            slug=normalized_slug,
            blueprint_ref=blueprint_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            owner_subject=owner_subject,
            family=family,
            status=status,
            submitted_tick=submitted_tick,
            metadata=md,
        )

    def with_status(self, status: RequestStatus) -> GenerationRequest:
        """Return an immutable copy in ``status`` (the id is preserved)."""
        if not isinstance(status, RequestStatus):
            raise RequestContractError("request status must be a RequestStatus")
        return GenerationRequest(
            request_id=self.request_id,
            slug=self.slug,
            blueprint_ref=self.blueprint_ref,
            workspace_id=self.workspace_id,
            project_id=self.project_id,
            tenant=self.tenant,
            owner_subject=self.owner_subject,
            family=self.family,
            status=status,
            submitted_tick=self.submitted_tick,
            metadata=self.metadata,
        )

    def with_metadata(self, metadata: RequestMetadata) -> GenerationRequest:
        """Return an immutable copy carrying ``metadata`` (the id is preserved)."""
        if not isinstance(metadata, RequestMetadata):
            raise RequestContractError("request metadata must be a RequestMetadata")
        return GenerationRequest(
            request_id=self.request_id,
            slug=self.slug,
            blueprint_ref=self.blueprint_ref,
            workspace_id=self.workspace_id,
            project_id=self.project_id,
            tenant=self.tenant,
            owner_subject=self.owner_subject,
            family=self.family,
            status=self.status,
            submitted_tick=self.submitted_tick,
            metadata=metadata,
        )

    @property
    def execution_state(self) -> ExecutionState:
        """The derived execution posture of the request (pure function of status)."""
        return _EXECUTION_STATE[self.status]

    @property
    def is_terminal(self) -> bool:
        """True iff the request is in a terminal state (completed/failed/cancelled)."""
        return self.status in TERMINAL_STATUSES

    @property
    def is_dispatched(self) -> bool:
        """True iff the request has been handed off to the Execution Runtime or beyond."""
        return self.status in (
            RequestStatus.DISPATCHED,
            RequestStatus.RUNNING,
            RequestStatus.COMPLETED,
            RequestStatus.FAILED,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "slug": self.slug,
            "blueprint_ref": self.blueprint_ref,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "tenant": self.tenant,
            "owner_subject": self.owner_subject,
            "family": self.family.value,
            "status": self.status.value,
            "execution_state": self.execution_state.value,
            "submitted_tick": self.submitted_tick,
            "metadata": self.metadata.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- #
# The published generation-request contract surface (L3).                     #
# --------------------------------------------------------------------------- #

#: The request service contract identities the Generation Request Runtime publishes.
#: Each maps to an EC2-EPIC-007 deliverable; consumers bind to these by reference
#: (PL-05). The ``dispatch``/``runtime`` contracts are the binding point EPIC-008/012 use.
_GENERATION_REQUEST_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("requests.registry.registry", "Request registry — submit/register/resolve/discover."),
    ("requests.lifecycle.transition", "Lifecycle — deterministic request state machine."),
    ("requests.dispatch.handoff", "Dispatch — governed UI→request→execution-runtime boundary."),
    ("requests.provenance.trace", "Provenance — Generation→Blueprint→Request trace edge."),
    ("requests.status.derive", "Status — deterministic derived request + execution status."),
    ("requests.search.query", "Request search — authorization + isolation scoped discovery."),
    ("requests.runtime.service", "Request runtime — the L3 access + context decision point."),
)

#: Immutable references to the published generation-request contracts (name + version).
GENERATION_REQUEST_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, GENERATION_REQUEST_CONTRACT_VERSION)
    for name, _ in _GENERATION_REQUEST_CONTRACT_NAMES
)


def generation_request_contract(name: str, description: str = "") -> Contract:
    """Build a versioned request :class:`Contract` at the request contract version."""
    if not isinstance(name, str) or not name:
        raise RequestContractError("generation request contract name is required")
    try:
        return platform_contract(name, GENERATION_REQUEST_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise RequestContractError(str(exc), name=name) from exc


def default_generation_request_contracts() -> tuple[Contract, ...]:
    """The published request contracts as concrete :class:`Contract` objects."""
    return tuple(
        generation_request_contract(name, description)
        for name, description in _GENERATION_REQUEST_CONTRACT_NAMES
    )


__all__ = [
    "GENERATION_REQUEST_CONTRACT_VERSION",
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
    "GENERATION_REQUEST_CONTRACTS",
    "generation_request_contract",
    "default_generation_request_contracts",
]
