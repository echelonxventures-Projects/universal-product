"""EC2-TASK-000127 — Execution dashboard contracts tests (EC2-EPIC-008).

Covers the dashboard vocabulary and published contract surface: the reused
``execution-dashboard`` capability group binding, the READ-only action→permission map,
the surfaced EPIC-007 vocabulary re-exports, the observed observability surface, and the
versioned ``EXECUTION_DASHBOARD_CONTRACTS`` builders (fail-closed).
"""

from __future__ import annotations

from platform.execution_dashboard.contracts import (
    EXECUTION_DASHBOARD_CONTRACT_VERSION,
    EXECUTION_DASHBOARD_CONTRACTS,
    EXECUTION_DASHBOARD_GROUP,
    OBSERVED_GENERATION_EVENTS,
    OBSERVED_GENERATION_METRICS,
    DashboardAction,
    DashboardDerivedStatus,
    DashboardExecutionState,
    DashboardRequestPosture,
    DashboardRequestStatus,
    all_dashboard_actions,
    default_execution_dashboard_contracts,
    execution_dashboard_contract,
    permission_for,
)
from platform.execution_dashboard.errors import DashboardContractError
from platform.foundation.identity import Permission
from platform.generation.contracts import TERMINAL_STATUSES, ExecutionState, RequestStatus
from platform.generation.status import DerivedRequestStatus, RequestPosture
from platform.identity.contracts import CapabilityGroup

import pytest


def test_binds_the_existing_execution_dashboard_group_no_new_group():
    assert EXECUTION_DASHBOARD_GROUP is CapabilityGroup.EXECUTION_DASHBOARD


def test_surfaced_vocabulary_reexports_epic_007_verbatim():
    assert DashboardRequestStatus is RequestStatus
    assert DashboardExecutionState is ExecutionState
    assert DashboardRequestPosture is RequestPosture
    assert DashboardDerivedStatus is DerivedRequestStatus


def test_every_action_requires_read_only():
    for action in all_dashboard_actions():
        assert permission_for(action) is Permission.READ
    assert set(all_dashboard_actions()) == set(DashboardAction)


def test_permission_for_rejects_bad_action():
    with pytest.raises(DashboardContractError):
        permission_for("view")  # type: ignore[arg-type]


def test_observed_generation_surface_is_referenced():
    assert "generation.request.submitted" in OBSERVED_GENERATION_EVENTS
    assert "generation.request.dispatched" in OBSERVED_GENERATION_EVENTS
    assert "generation.request.completed" in OBSERVED_GENERATION_EVENTS
    assert "generation.request.failed" in OBSERVED_GENERATION_EVENTS
    assert "generation.request.cancelled" in OBSERVED_GENERATION_EVENTS
    assert "generation.requests.queue_depth" in OBSERVED_GENERATION_METRICS
    assert "generation.requests.lifecycle_latency" in OBSERVED_GENERATION_METRICS


def test_contract_surface_is_versioned_and_complete():
    assert EXECUTION_DASHBOARD_CONTRACT_VERSION == "1.0.0"
    names = {ref.name for ref in EXECUTION_DASHBOARD_CONTRACTS}
    assert "dashboard.runtime.service" in names
    assert "dashboard.search.query" in names
    assert "dashboard.summary.compose" in names
    for ref in EXECUTION_DASHBOARD_CONTRACTS:
        assert ref.version == EXECUTION_DASHBOARD_CONTRACT_VERSION


def test_default_contracts_build_and_match_refs():
    contracts = default_execution_dashboard_contracts()
    assert {c.name for c in contracts} == {ref.name for ref in EXECUTION_DASHBOARD_CONTRACTS}


def test_execution_dashboard_contract_rejects_empty_name():
    with pytest.raises(DashboardContractError):
        execution_dashboard_contract("")


def test_terminal_statuses_are_reused():
    assert RequestStatus.COMPLETED in TERMINAL_STATUSES
