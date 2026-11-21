"""EPIC-007 (T7) — Runtime platform service (composition point) tests."""

from __future__ import annotations

from platform.runtime_platform.core import RuntimeKernel
from platform.runtime_platform.errors import (
    ExecutionRegistryError,
    RuntimeAdmissionError,
    RuntimePlatformServiceError,
)
from platform.runtime_platform.events import WORKFLOW_RESOLVED
from platform.runtime_platform.service import (
    RuntimePlatformService,
    build_runtime_platform_service,
)
from platform.runtime_platform.workflow import WORKFLOW_COMPLETED
from platform.tests.runtime_platform_helpers import request, workflow

import pytest


def test_submit_execution_and_get():
    svc = build_runtime_platform_service()
    record = svc.submit_execution(request("w"))
    assert svc.get_execution(record.execution_id) is record
    with pytest.raises(ExecutionRegistryError):
        svc.get_execution("missing")


def test_submit_batch_and_schedule_batch():
    svc = build_runtime_platform_service()
    schedule = svc.schedule_batch([request("a"), request("b", dependencies=("a",))])
    assert schedule.stage_count == 2
    records = svc.submit_batch([request("b", dependencies=("a",)), request("a")])
    assert [r.workload_id for r in records] == ["a", "b"]


def test_run_workflow_completed_registers_all_steps():
    svc = build_runtime_platform_service()
    run = svc.run_workflow(workflow())
    assert run.status == WORKFLOW_COMPLETED
    assert svc.workflow_run_count == 1
    # each forward step is registered in the append-only registry
    for record in run.step_records:
        assert svc.get_execution(record.execution_id).workflow_id == "wf-1"
    assert len(svc.events.events_of(WORKFLOW_RESOLVED)) == 1


def test_run_workflow_compensated_registers_compensations():
    svc = build_runtime_platform_service()
    run = svc.run_workflow(workflow(failing_step="b"))
    assert run.failed_step == "b"
    for record in run.records:
        assert svc.get_execution(record.execution_id) is not None


def test_run_workflow_admission_fail_closed():
    svc = build_runtime_platform_service()
    from platform.runtime_platform.workflow import WorkflowDefinition, WorkflowStep
    from platform.tests.runtime_platform_helpers import attestation

    definition = WorkflowDefinition(
        workflow_id="wf-x",
        name="n",
        steps=(WorkflowStep("a", attestation("a", certified=False)),),
    )
    with pytest.raises(RuntimeAdmissionError):
        svc.run_workflow(definition)


def test_compensate_execution():
    svc = build_runtime_platform_service()
    record = svc.submit_execution(request("w"))
    compensated = svc.compensate_execution(record.execution_id)
    assert compensated.final_state == "compensated"


def test_discover_filters():
    svc = build_runtime_platform_service()
    svc.submit_execution(request("solo"))
    svc.run_workflow(workflow())
    assert len(svc.discover()) >= 4
    assert {r.workload_id for r in svc.discover(workflow_id="wf-1")} == {"a", "b", "c"}
    assert all(r.succeeded for r in svc.discover(final_state="succeeded"))
    both = svc.discover(workflow_id="wf-1", final_state="succeeded")
    assert all(r.workflow_id == "wf-1" and r.succeeded for r in both)


def test_lineage_and_ledger_entry():
    svc = build_runtime_platform_service()
    record = svc.submit_execution(request("w"))
    lineage = svc.lineage_of(record.execution_id)
    assert lineage.execution_id == record.execution_id
    entry = svc.ledger_entry(record.execution_id)
    assert entry.execution_id == record.execution_id


def test_evidence_is_content_addressed_and_deterministic():
    svc = build_runtime_platform_service()
    svc.submit_execution(request("w"))
    ev = svc.evidence()
    assert ev.evidence_id.startswith("UCOS-URPE-")
    assert ev.execution_count == 1
    assert ev.registry_intact
    assert ev.fingerprint() == svc.evidence().fingerprint()
    assert svc.to_dict()["workflow_run_count"] == 0


def test_service_rejects_bad_inputs():
    with pytest.raises(RuntimePlatformServiceError):
        build_runtime_platform_service(kernel="bad")  # type: ignore[arg-type]
    with pytest.raises(RuntimePlatformServiceError):
        RuntimePlatformService(kernel="bad", runner="bad")  # type: ignore[arg-type]
    svc = build_runtime_platform_service()
    with pytest.raises(RuntimePlatformServiceError):
        svc.run_workflow("bad")  # type: ignore[arg-type]


def test_the_service_refuses_a_runner_that_is_not_a_workflow_runner() -> None:
    """The second composition guard: a kernel without a governed runner is not a service."""
    with pytest.raises(RuntimePlatformServiceError, match="WorkflowRunner"):
        RuntimePlatformService(kernel=RuntimeKernel(), runner="bad")  # type: ignore[arg-type]
