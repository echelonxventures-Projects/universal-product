"""EPIC-007 (Terminal T7) — Execution Engine (Universal Runtime Platform).

The **Execution Engine** — realizing the runtime plane's core compute-governance
concern. Like the certified EC-1 runtime execution platform, it **executes nothing
live**: it models a governed execution as a *deterministic trajectory* over the
:mod:`~platform.runtime_platform.lifecycle` state machine and produces a recorded,
content-addressed :class:`ExecutionRecord` only. Given the same
:class:`ExecutionRequest` and capacity posture, the engine yields a byte-identical
record (no wall-clock, no ambient state) — the basis of replayability.

    * :class:`ExecutionRequest` — the immutable, content-addressed unit of governed
      execution: a workload identity, its upstream :class:`WorkloadAttestation`, its
      declared in-batch dependencies, a governed priority, and an explicit,
      deterministic failure indicator (so failure paths are modelled, not random).
    * :class:`ExecutionRecord` — the immutable outcome: the request, the lifecycle
      trajectory it traversed, its placement, and its final state.
    * :class:`ExecutionEngine` — the modelling engine: :meth:`ExecutionEngine.run`
      drives a request ``pending → scheduled → placed → running → succeeded|failed``;
      :meth:`ExecutionEngine.compensate` records a governed reversal of a settled record.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.runtime_platform.contracts import WorkloadAttestation
from platform.runtime_platform.errors import ExecutionEngineError, ExecutionRequestError
from platform.runtime_platform.infrastructure import PlacementDecision, RuntimeInfrastructure
from platform.runtime_platform.lifecycle import (
    COMPENSATED,
    FAILED,
    PENDING,
    PLACED,
    RUNNING,
    SCHEDULED,
    SUCCEEDED,
    is_settled,
    require_transition,
    validate_trajectory,
)
from typing import Any

#: The recorded execution-record format.
EXECUTION_RECORD_FORMAT = "ucos-runtime-execution-record/1.0.0"


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    """An immutable, content-addressed request to execute a governed workload."""

    workload_id: str
    attestation: WorkloadAttestation
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    priority: int = 0
    inject_failure: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)
    request_id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.workload_id, str) or not self.workload_id:
            raise ExecutionRequestError("execution request workload_id is required")
        if not isinstance(self.attestation, WorkloadAttestation):
            raise ExecutionRequestError(
                "execution request requires a WorkloadAttestation", workload_id=self.workload_id
            )
        if self.attestation.workload_id != self.workload_id:
            raise ExecutionRequestError(
                "attestation workload_id must match the request workload_id",
                workload_id=self.workload_id,
                attested=self.attestation.workload_id,
            )
        if not isinstance(self.priority, int) or isinstance(self.priority, bool):
            raise ExecutionRequestError(
                "execution priority must be an integer", workload_id=self.workload_id
            )
        for dependency in self.dependencies:
            if not isinstance(dependency, str) or not dependency:
                raise ExecutionRequestError(
                    "execution dependencies must be non-empty ids", workload_id=self.workload_id
                )
        if self.workload_id in self.dependencies:
            raise ExecutionRequestError(
                "an execution request may not depend on itself", workload_id=self.workload_id
            )
        object.__setattr__(self, "dependencies", tuple(self.dependencies))
        object.__setattr__(self, "metadata", dict(self.metadata))
        if not self.request_id:
            object.__setattr__(self, "request_id", f"UCOS-URPX-{content_hash(self._core())[:16]}")

    def _core(self) -> dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "attestation": self.attestation.fingerprint(),
            "dependencies": list(self.dependencies),
            "priority": self.priority,
            "inject_failure": self.inject_failure,
            "metadata": dict(self.metadata),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["request_id"] = self.request_id
        payload["attestation_ref"] = self.attestation.attestation_id
        return payload

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ExecutionRecord:
    """An immutable, content-addressed record of a modelled execution outcome."""

    request: ExecutionRequest
    trajectory: tuple[str, ...]
    final_state: str
    placement: PlacementDecision
    workflow_id: str | None = None
    execution_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        request: ExecutionRequest,
        trajectory: tuple[str, ...],
        placement: PlacementDecision,
        workflow_id: str | None = None,
    ) -> ExecutionRecord:
        validate_trajectory(trajectory)
        core = {
            "request_id": request.request_id,
            "trajectory": list(trajectory),
            "placement_id": placement.placement_id,
            "workflow_id": workflow_id,
        }
        return cls(
            request=request,
            trajectory=trajectory,
            final_state=trajectory[-1],
            placement=placement,
            workflow_id=workflow_id,
            execution_id=f"UCOS-URPR-{content_hash(core)[:16]}",
        )

    @property
    def workload_id(self) -> str:
        return self.request.workload_id

    @property
    def succeeded(self) -> bool:
        return self.final_state == SUCCEEDED

    @property
    def settled(self) -> bool:
        return is_settled(self.final_state)

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_record_format": EXECUTION_RECORD_FORMAT,
            "execution_id": self.execution_id,
            "workload_id": self.workload_id,
            "request": self.request.to_dict(),
            "trajectory": list(self.trajectory),
            "final_state": self.final_state,
            "placement": self.placement.to_dict(),
            "workflow_id": self.workflow_id,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class ExecutionEngine:
    """The deterministic, model-only execution engine (records structures; runs nothing live)."""

    __slots__ = ("_infrastructure",)

    def __init__(self, infrastructure: RuntimeInfrastructure | None = None) -> None:
        if infrastructure is not None and not isinstance(infrastructure, RuntimeInfrastructure):
            raise ExecutionEngineError("ExecutionEngine requires a RuntimeInfrastructure")
        self._infrastructure = (
            infrastructure if infrastructure is not None else RuntimeInfrastructure()
        )

    @property
    def infrastructure(self) -> RuntimeInfrastructure:
        return self._infrastructure

    def run(self, request: ExecutionRequest, *, workflow_id: str | None = None) -> ExecutionRecord:
        """Model a governed execution deterministically, returning a recorded outcome.

        Drives the lifecycle ``pending → scheduled → placed → running → succeeded`` for a
        healthy request, or ``… → running → failed`` when the request explicitly injects a
        deterministic failure. Placement is decided by the technology-neutral
        infrastructure. Executes nothing live.
        """
        if not isinstance(request, ExecutionRequest):
            raise ExecutionEngineError("run requires an ExecutionRequest")
        placement = self._infrastructure.place(request.workload_id)
        trajectory = (PENDING, SCHEDULED, PLACED, RUNNING)
        terminal = FAILED if request.inject_failure else SUCCEEDED
        trajectory = (*trajectory, require_transition(RUNNING, terminal))
        return ExecutionRecord.create(
            request=request,
            trajectory=trajectory,
            placement=placement,
            workflow_id=workflow_id,
        )

    def compensate(self, record: ExecutionRecord) -> ExecutionRecord:
        """Record a governed reversal of a settled execution (``… → compensated``).

        Only a settled, non-terminal-compensated record may be compensated (fail-closed).
        The compensated record extends the original trajectory by one legal transition.
        """
        if not isinstance(record, ExecutionRecord):
            raise ExecutionEngineError("compensate requires an ExecutionRecord")
        if not record.settled:
            raise ExecutionEngineError(
                "only a settled execution may be compensated",
                execution_id=record.execution_id,
                final_state=record.final_state,
            )
        if record.final_state == COMPENSATED:
            raise ExecutionEngineError(
                "execution already compensated", execution_id=record.execution_id
            )
        trajectory = (*record.trajectory, require_transition(record.final_state, COMPENSATED))
        return ExecutionRecord.create(
            request=record.request,
            trajectory=trajectory,
            placement=record.placement,
            workflow_id=record.workflow_id,
        )


__all__ = [
    "EXECUTION_RECORD_FORMAT",
    "ExecutionRequest",
    "ExecutionRecord",
    "ExecutionEngine",
]
