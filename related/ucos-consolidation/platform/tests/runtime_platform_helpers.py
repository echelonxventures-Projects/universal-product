"""Shared fixtures/builders for the Universal Runtime Platform tests (EPIC-007, T7)."""

from __future__ import annotations

from platform.runtime_platform.contracts import WorkloadAttestation
from platform.runtime_platform.execution import ExecutionRequest
from platform.runtime_platform.workflow import WorkflowDefinition, WorkflowStep


def attestation(
    workload_id: str,
    *,
    validated: bool = True,
    certified: bool = True,
    knowledge: bool = True,
    measurement: bool = True,
) -> WorkloadAttestation:
    """Build a workload attestation (admissible by default)."""
    return WorkloadAttestation(
        workload_id=workload_id,
        registry_id=f"UCOS-REG-{workload_id}",
        validated=validated,
        certified=certified,
        knowledge_id=f"UCOS-KG-{workload_id}" if knowledge else None,
        measurement_id=f"UCOS-MEAS-{workload_id}" if measurement else None,
    )


def request(
    workload_id: str,
    *,
    dependencies: tuple[str, ...] = (),
    priority: int = 0,
    inject_failure: bool = False,
    validated: bool = True,
    certified: bool = True,
) -> ExecutionRequest:
    """Build an execution request for ``workload_id`` (admissible by default)."""
    return ExecutionRequest(
        workload_id=workload_id,
        attestation=attestation(workload_id, validated=validated, certified=certified),
        dependencies=dependencies,
        priority=priority,
        inject_failure=inject_failure,
    )


def workflow(
    workflow_id: str = "wf-1",
    *,
    failing_step: str | None = None,
) -> WorkflowDefinition:
    """Build a small 3-step workflow (a → {b, c}); optionally make one step fail."""
    return WorkflowDefinition(
        workflow_id=workflow_id,
        name="test workflow",
        steps=(
            WorkflowStep(step_id="a", attestation=attestation("a")),
            WorkflowStep(
                step_id="b",
                attestation=attestation("b"),
                depends_on=("a",),
                inject_failure=(failing_step == "b"),
            ),
            WorkflowStep(
                step_id="c",
                attestation=attestation("c"),
                depends_on=("a",),
                inject_failure=(failing_step == "c"),
            ),
        ),
    )


__all__ = ["attestation", "request", "workflow"]
