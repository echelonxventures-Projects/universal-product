"""EC2-TASK-000090 — Project lifecycle tests.

Covers the deterministic project state machine: legal transitions, refusal of illegal
edges, terminal ARCHIVED (no exit), no-op self-transition refusal, fail-closed type
validation, and the append-only ProjectEvent record.
"""

from __future__ import annotations

from platform.projects.contracts import ProjectStatus
from platform.projects.errors import ProjectLifecycleError
from platform.projects.lifecycle import (
    ProjectEvent,
    allowed_transitions,
    can_transition,
    validate_transition,
)

import pytest


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ProjectStatus.ACTIVE, ProjectStatus.SUSPENDED),
        (ProjectStatus.ACTIVE, ProjectStatus.COMPLETED),
        (ProjectStatus.ACTIVE, ProjectStatus.ARCHIVED),
        (ProjectStatus.SUSPENDED, ProjectStatus.ACTIVE),
        (ProjectStatus.SUSPENDED, ProjectStatus.ARCHIVED),
        (ProjectStatus.COMPLETED, ProjectStatus.ACTIVE),
        (ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED),
    ],
)
def test_legal_transitions(current, target):
    assert can_transition(current, target) is True
    validate_transition(current, target)  # does not raise


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ProjectStatus.ACTIVE, ProjectStatus.ACTIVE),  # no-op self
        (ProjectStatus.SUSPENDED, ProjectStatus.COMPLETED),  # unknown edge
        (ProjectStatus.COMPLETED, ProjectStatus.SUSPENDED),  # unknown edge
        (ProjectStatus.ARCHIVED, ProjectStatus.ACTIVE),  # terminal exit
        (ProjectStatus.ARCHIVED, ProjectStatus.ARCHIVED),  # terminal self
    ],
)
def test_illegal_transitions_refused(current, target):
    assert can_transition(current, target) is False
    with pytest.raises(ProjectLifecycleError):
        validate_transition(current, target)


def test_archived_is_terminal():
    assert allowed_transitions(ProjectStatus.ARCHIVED) == ()


def test_allowed_transitions_stable_order():
    assert allowed_transitions(ProjectStatus.ACTIVE) == (
        ProjectStatus.SUSPENDED,
        ProjectStatus.COMPLETED,
        ProjectStatus.ARCHIVED,
    )


def test_transition_type_validation():
    with pytest.raises(ProjectLifecycleError):
        allowed_transitions("active")  # type: ignore[arg-type]
    with pytest.raises(ProjectLifecycleError):
        can_transition("active", ProjectStatus.ACTIVE)  # type: ignore[arg-type]


def test_project_event_is_serializable():
    event = ProjectEvent(
        sequence=0,
        project_id="UCOS-PROJ-1",
        from_status=ProjectStatus.ACTIVE,
        to_status=ProjectStatus.COMPLETED,
        tick=7,
    )
    assert event.to_dict() == {
        "sequence": 0,
        "project_id": "UCOS-PROJ-1",
        "from_status": "active",
        "to_status": "completed",
        "tick": 7,
    }
