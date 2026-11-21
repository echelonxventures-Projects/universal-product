"""EC2-TASK-000127 — Execution Dashboard Contracts (EC2-EPIC-008).

The versioned contract surface for the UCOS Platform **Execution Dashboard Runtime**
(L3 Application of the Program architecture, §4) plus the immutable **core vocabulary**
every dashboard service speaks. It reuses the certified EC-1 contract machinery through
the Platform Foundation (:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and binds dashboard authorization to
the single §3.2 :class:`~platform.identity.contracts.CapabilityGroup`
``execution-dashboard`` (PC-08, matrix index 7) that **already physically exists** in the
certified Identity Layer. EC2-EPIC-008 introduces **no new capability group, no new
authority, and no new authorization logic**.

It also **reuses — rather than reinventing** — the frozen Generation Request vocabulary:
the surfaced :class:`~platform.generation.contracts.RequestStatus`,
:class:`~platform.generation.contracts.ExecutionState`,
:class:`~platform.generation.status.RequestPosture`,
:data:`~platform.generation.contracts.TERMINAL_STATUSES`,
:class:`~platform.generation.status.DerivedRequestStatus`, and the
:class:`~platform.generation.search.RequestSearchResponse` /
:class:`~platform.generation.search.RequestHit` search contracts are the certified
EC2-EPIC-007 members (re-exported, never redefined). The dashboard **records** these
read-only; it computes no lifecycle, execution, or generation state of its own (P10).

Vocabulary:
    * :class:`DashboardAction` — the governed (read-only) dashboard verbs, each mapped to
      the coarse RBAC :class:`~platform.foundation.identity.Permission` it requires (all
      :data:`Permission.READ`).
    * :data:`OBSERVED_GENERATION_EVENTS` — the EPIC-007 governed lifecycle events the
      dashboard surfaces by reference (submitted/dispatched/completed/failed/cancelled).
    * :data:`OBSERVED_GENERATION_METRICS` — the EPIC-007 observability metrics the
      dashboard surfaces by reference (``queue_depth``, ``lifecycle_latency``, …).
    * :data:`EXECUTION_DASHBOARD_CONTRACTS` — the published dashboard service contracts
      consumers (later presentation / navigation portal) bind to by reference
      (PL-05, versioned).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from enum import Enum
from platform.execution_dashboard.errors import DashboardContractError
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.generation.contracts import (
    TERMINAL_STATUSES,
    ExecutionState,
    RequestStatus,
)
from platform.generation.status import DerivedRequestStatus, RequestPosture
from platform.identity.contracts import CapabilityGroup

#: The semantic version of the Execution Dashboard Runtime contract surface (AR-03/PL-05).
EXECUTION_DASHBOARD_CONTRACT_VERSION = "1.0.0"

#: The §3.2 capability group authorizing every dashboard action (reused; no new group).
EXECUTION_DASHBOARD_GROUP = CapabilityGroup.EXECUTION_DASHBOARD

#: Re-exports of the frozen EPIC-007 generation vocabulary (surfaced, never redefined).
DashboardRequestStatus = RequestStatus
DashboardExecutionState = ExecutionState
DashboardRequestPosture = RequestPosture
DashboardDerivedStatus = DerivedRequestStatus
DASHBOARD_TERMINAL_STATUSES = TERMINAL_STATUSES

# --------------------------------------------------------------------------- #
# Observed EPIC-007 observability surface (consumed by reference, never emitted #
# by the dashboard itself — these are the generation runtime's governed events  #
# and metrics the dashboard provides operational visibility over).              #
# --------------------------------------------------------------------------- #

#: The EPIC-007 governed lifecycle events the dashboard surfaces (by reference, PC-08).
OBSERVED_GENERATION_EVENTS: tuple[str, ...] = (
    "generation.request.submitted",
    "generation.request.dispatched",
    "generation.request.completed",
    "generation.request.failed",
    "generation.request.cancelled",
)

#: The EPIC-007 observability metrics the dashboard surfaces (by reference, PC-12).
OBSERVED_GENERATION_METRICS: tuple[str, ...] = (
    "generation.requests.submitted",
    "generation.requests.dispatched",
    "generation.requests.completed",
    "generation.requests.failed",
    "generation.requests.cancelled",
    "generation.requests.queue_depth",
    "generation.requests.lifecycle_latency",
)


class DashboardAction(str, Enum):
    """The governed (read-only) execution-dashboard verbs.

    Every action requires only :data:`Permission.READ` on the ``execution-dashboard``
    group — the dashboard exposes no create/execute/administer authority and no mutation
    path to any request, dispatch, or lifecycle datum (observability & navigation only).
    """

    VIEW = "view"
    SUMMARIZE = "summarize"
    INSPECT_QUEUE = "inspect-queue"
    CENSUS = "census"
    TREND = "trend"
    INSPECT_HEALTH = "inspect-health"
    INSPECT = "inspect"
    DISCOVER = "discover"
    SEARCH = "search"


#: The verb→permission map (Determination §7/§13). Every dashboard verb is READ-only.
_ACTION_PERMISSIONS: dict[DashboardAction, Permission] = {
    action: Permission.READ for action in DashboardAction
}


def permission_for(action: DashboardAction) -> Permission:
    """Return the RBAC permission required by a dashboard action (fail-closed)."""
    if not isinstance(action, DashboardAction):
        raise DashboardContractError("action must be a DashboardAction")
    return _ACTION_PERMISSIONS[action]


def all_dashboard_actions() -> tuple[DashboardAction, ...]:
    """Return every execution-dashboard action in stable declaration order."""
    return tuple(DashboardAction)


# --------------------------------------------------------------------------- #
# The published execution-dashboard contract surface (L3).                    #
# --------------------------------------------------------------------------- #

#: The dashboard service contract identities the Execution Dashboard Runtime publishes.
#: Each maps to an EC2-EPIC-008 deliverable; consumers bind to these by reference (PL-05).
_EXECUTION_DASHBOARD_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("dashboard.summary.compose", "Dashboard summary — metrics + queue + health aggregate."),
    ("dashboard.queue.visibility", "Queue visibility — deterministic queue-depth census."),
    ("dashboard.census.aggregate", "Request census — status/execution/family aggregation."),
    ("dashboard.trend.generate", "Trend generation — deterministic lifecycle-event trend."),
    ("dashboard.health.visibility", "Health visibility — dashboard + surfaced source health."),
    ("dashboard.requests.visibility", "Request visibility — per-request execution snapshots."),
    ("dashboard.search.query", "Request search — authorization + isolation scoped discovery."),
    ("dashboard.runtime.service", "Dashboard runtime — the L3 read + access decision point."),
)

#: Immutable references to the published execution-dashboard contracts (name + version).
EXECUTION_DASHBOARD_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, EXECUTION_DASHBOARD_CONTRACT_VERSION)
    for name, _ in _EXECUTION_DASHBOARD_CONTRACT_NAMES
)


def execution_dashboard_contract(name: str, description: str = "") -> Contract:
    """Build a versioned dashboard :class:`Contract` at the dashboard contract version."""
    if not isinstance(name, str) or not name:
        raise DashboardContractError("execution dashboard contract name is required")
    try:
        return platform_contract(name, EXECUTION_DASHBOARD_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise DashboardContractError(str(exc), name=name) from exc


def default_execution_dashboard_contracts() -> tuple[Contract, ...]:
    """The published dashboard contracts as concrete :class:`Contract` objects."""
    return tuple(
        execution_dashboard_contract(name, description)
        for name, description in _EXECUTION_DASHBOARD_CONTRACT_NAMES
    )


__all__ = [
    "EXECUTION_DASHBOARD_CONTRACT_VERSION",
    "EXECUTION_DASHBOARD_GROUP",
    "DashboardRequestStatus",
    "DashboardExecutionState",
    "DashboardRequestPosture",
    "DashboardDerivedStatus",
    "DASHBOARD_TERMINAL_STATUSES",
    "OBSERVED_GENERATION_EVENTS",
    "OBSERVED_GENERATION_METRICS",
    "DashboardAction",
    "permission_for",
    "all_dashboard_actions",
    "EXECUTION_DASHBOARD_CONTRACTS",
    "execution_dashboard_contract",
    "default_execution_dashboard_contracts",
]
