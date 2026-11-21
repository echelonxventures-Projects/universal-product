"""EC2-TASK-000082 — Workspace lifecycle tests.

Covers the deterministic state machine (legal edges, terminal ARCHIVED, fail-closed
illegal/self transitions) and the append-only WorkspaceEvent.
"""

from __future__ import annotations

from platform.workspace.contracts import WorkspaceStatus
from platform.workspace.errors import WorkspaceLifecycleError
from platform.workspace.lifecycle import (
    WorkspaceEvent,
    allowed_transitions,
    can_transition,
    validate_transition,
)

import pytest


def test_legal_transitions():
    assert can_transition(WorkspaceStatus.ACTIVE, WorkspaceStatus.SUSPENDED)
    assert can_transition(WorkspaceStatus.ACTIVE, WorkspaceStatus.ARCHIVED)
    assert can_transition(WorkspaceStatus.SUSPENDED, WorkspaceStatus.ACTIVE)
    assert can_transition(WorkspaceStatus.SUSPENDED, WorkspaceStatus.ARCHIVED)


def test_archived_is_terminal():
    assert allowed_transitions(WorkspaceStatus.ARCHIVED) == ()
    assert not can_transition(WorkspaceStatus.ARCHIVED, WorkspaceStatus.ACTIVE)


def test_self_transition_is_illegal():
    assert not can_transition(WorkspaceStatus.ACTIVE, WorkspaceStatus.ACTIVE)


def test_allowed_transitions_are_ordered():
    targets = allowed_transitions(WorkspaceStatus.ACTIVE)
    assert targets == (WorkspaceStatus.SUSPENDED, WorkspaceStatus.ARCHIVED)


def test_validate_transition_raises_on_illegal():
    with pytest.raises(WorkspaceLifecycleError):
        validate_transition(WorkspaceStatus.ARCHIVED, WorkspaceStatus.ACTIVE)
    validate_transition(WorkspaceStatus.ACTIVE, WorkspaceStatus.SUSPENDED)  # no raise


def test_transition_functions_reject_non_status():
    with pytest.raises(WorkspaceLifecycleError):
        allowed_transitions("active")  # type: ignore[arg-type]
    with pytest.raises(WorkspaceLifecycleError):
        can_transition("active", WorkspaceStatus.ARCHIVED)  # type: ignore[arg-type]


def test_workspace_event_serializes():
    event = WorkspaceEvent(
        sequence=0,
        workspace_id="UCOS-WSPC-x",
        from_status=WorkspaceStatus.ACTIVE,
        to_status=WorkspaceStatus.ARCHIVED,
        tick=5,
    )
    payload = event.to_dict()
    assert payload["from_status"] == "active" and payload["to_status"] == "archived"
    assert payload["sequence"] == 0 and payload["tick"] == 5
