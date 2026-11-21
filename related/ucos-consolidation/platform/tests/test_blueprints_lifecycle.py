"""EC2-TASK-000100 — Blueprint lifecycle state-machine tests (EC2-EPIC-006)."""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintStatus
from platform.blueprints.errors import BlueprintLifecycleError
from platform.blueprints.lifecycle import (
    BlueprintEvent,
    allowed_transitions,
    can_transition,
    validate_transition,
)

import pytest


@pytest.mark.parametrize(
    ("current", "targets"),
    [
        (BlueprintStatus.DRAFT, {BlueprintStatus.VALIDATED, BlueprintStatus.RETIRED}),
        (BlueprintStatus.VALIDATED, {BlueprintStatus.CATALOGUED, BlueprintStatus.RETIRED}),
        (BlueprintStatus.CATALOGUED, {BlueprintStatus.SUPERSEDED, BlueprintStatus.RETIRED}),
        (BlueprintStatus.SUPERSEDED, {BlueprintStatus.RETIRED}),
        (BlueprintStatus.RETIRED, set()),
    ],
)
def test_allowed_transitions(current, targets):
    assert set(allowed_transitions(current)) == targets


def test_can_transition_and_validate():
    assert can_transition(BlueprintStatus.DRAFT, BlueprintStatus.VALIDATED) is True
    assert can_transition(BlueprintStatus.DRAFT, BlueprintStatus.CATALOGUED) is False
    validate_transition(BlueprintStatus.VALIDATED, BlueprintStatus.CATALOGUED)


def test_illegal_transitions_are_fail_closed():
    with pytest.raises(BlueprintLifecycleError):
        validate_transition(BlueprintStatus.RETIRED, BlueprintStatus.CATALOGUED)
    with pytest.raises(BlueprintLifecycleError):
        validate_transition(BlueprintStatus.DRAFT, BlueprintStatus.DRAFT)  # no-op


def test_transition_endpoints_must_be_status():
    with pytest.raises(BlueprintLifecycleError):
        allowed_transitions("draft")  # type: ignore[arg-type]
    with pytest.raises(BlueprintLifecycleError):
        can_transition("draft", BlueprintStatus.VALIDATED)  # type: ignore[arg-type]


def test_blueprint_event_serialisation():
    event = BlueprintEvent(
        sequence=0,
        blueprint_id="UCOS-BLPR-1",
        from_status=BlueprintStatus.DRAFT,
        to_status=BlueprintStatus.VALIDATED,
        tick=7,
    )
    d = event.to_dict()
    assert d["from_status"] == "draft"
    assert d["to_status"] == "validated"
    assert d["tick"] == 7
