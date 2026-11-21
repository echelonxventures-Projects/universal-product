"""EPIC-007 (T7) — Workflow resolution & saga tests."""

from __future__ import annotations

from platform.runtime_platform.errors import WorkflowError
from platform.runtime_platform.execution import ExecutionEngine
from platform.runtime_platform.workflow import (
    WORKFLOW_COMPENSATED,
    WORKFLOW_COMPLETED,
    WorkflowDefinition,
    WorkflowRunner,
    WorkflowStep,
)
from platform.tests.runtime_platform_helpers import attestation, workflow

import pytest


def test_definition_validation_fail_closed():
    with pytest.raises(WorkflowError):
        WorkflowDefinition(workflow_id="", name="n", steps=(WorkflowStep("a", attestation("a")),))
    with pytest.raises(WorkflowError):
        WorkflowDefinition(workflow_id="w", name="n", steps=())
    with pytest.raises(WorkflowError):
        WorkflowDefinition(
            workflow_id="w",
            name="n",
            steps=(WorkflowStep("a", attestation("a")), WorkflowStep("a", attestation("a"))),
        )
    with pytest.raises(WorkflowError):
        WorkflowDefinition(
            workflow_id="w",
            name="n",
            steps=(WorkflowStep("a", attestation("a"), depends_on=("ghost",)),),
        )


def test_step_validation_fail_closed():
    with pytest.raises(WorkflowError):
        WorkflowStep("", attestation("a"))
    with pytest.raises(WorkflowError):
        WorkflowStep("a", "bad")  # type: ignore[arg-type]
    with pytest.raises(WorkflowError):
        WorkflowStep("a", attestation("a"), depends_on=("a",))
    with pytest.raises(WorkflowError):
        WorkflowStep("a", attestation("a"), depends_on=("",))


def test_resolve_orders_stages_and_is_deterministic():
    plan = workflow().resolve()
    assert plan.order[0] == "a"
    assert plan.stages[0] == ("a",)
    assert set(plan.stages[1]) == {"b", "c"}
    assert plan.stage_count == 2
    assert plan.plan_id.startswith("UCOS-URPW-")
    assert workflow().resolve().fingerprint() == plan.fingerprint()


def test_resolve_cycle_fails_closed():
    definition = WorkflowDefinition(
        workflow_id="w",
        name="n",
        steps=(
            WorkflowStep("a", attestation("a"), depends_on=("c",)),
            WorkflowStep("b", attestation("b"), depends_on=("a",)),
            WorkflowStep("c", attestation("c"), depends_on=("b",)),
        ),
    )
    with pytest.raises(WorkflowError):
        definition.resolve()


def test_definition_step_lookup_and_dict():
    definition = workflow()
    assert definition.step("a").step_id == "a"
    with pytest.raises(WorkflowError):
        definition.step("zzz")
    assert definition.to_dict()["workflow_id"] == "wf-1"
    assert definition.fingerprint() == workflow().fingerprint()


def test_run_completed_saga():
    runner = WorkflowRunner()
    record = runner.run(workflow())
    assert record.status == WORKFLOW_COMPLETED
    assert record.completed
    assert len(record.step_records) == 3
    assert record.compensations == ()
    assert record.failed_step is None
    assert record.run_id.startswith("UCOS-URPWR-")
    assert all(step.succeeded for step in record.step_records)


def test_run_compensated_saga_on_failure():
    runner = WorkflowRunner()
    record = runner.run(workflow(failing_step="b"))
    assert record.status == WORKFLOW_COMPENSATED
    assert not record.completed
    assert record.failed_step == "b"
    # step "a" succeeded before "b" failed -> exactly one compensation (of "a").
    assert len(record.compensations) == 1
    assert record.compensations[0].final_state == "compensated"
    # forward records: a (succeeded) + b (failed); c never ran (same stage, after b).
    assert {r.workload_id for r in record.step_records} == {"a", "b"}


def test_run_records_property_and_dict():
    runner = WorkflowRunner()
    record = runner.run(workflow(failing_step="b"))
    assert len(record.records) == len(record.step_records) + len(record.compensations)
    payload = record.to_dict()
    assert payload["status"] == WORKFLOW_COMPENSATED
    assert payload["failed_step"] == "b"


def test_runner_uses_supplied_engine_and_rejects_bad():
    engine = ExecutionEngine()
    runner = WorkflowRunner(engine=engine)
    assert runner.engine is engine
    with pytest.raises(WorkflowError):
        WorkflowRunner(engine="bad")  # type: ignore[arg-type]
    with pytest.raises(WorkflowError):
        runner.run("bad")  # type: ignore[arg-type]


def test_run_is_deterministic():
    assert (
        WorkflowRunner().run(workflow()).fingerprint()
        == WorkflowRunner().run(workflow()).fingerprint()
    )
