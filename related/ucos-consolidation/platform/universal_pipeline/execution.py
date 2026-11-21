"""UAPF-000001 — the Universal Execution Engine (running a derived plan, once, provably).

Execution is the narrowest module in the framework, deliberately. It decides nothing: the
plan was derived by the contracts layer, the order by the ordering authority, the admission
by the gateway, the legality of every state change by the state engine, and the behaviour of
every stage by a registered handler. What is left — and all this module does — is walk the
plan, thread outputs forward, record what happened, and route failure.

Nothing bypasses the gateway
----------------------------
:meth:`PipelineRuntime.execute` requires a
:class:`~platform.universal_pipeline.gateway.GatewayTransaction`
and *recomputes* its authorization before doing anything. Because the authorization binds the
pipeline, the version, the unit and the inputs hash, a caller cannot present a transaction
admitted for other work, nor alter the inputs after admission: both invalidate the
authorization. The rule "nothing executes without admission" is therefore enforced by
arithmetic rather than by convention.

Outputs thread forward; nothing is shared
-----------------------------------------
Each stage receives the unit's inputs merged with the outputs of every stage already
completed, and returns new outputs. There is no mutable context object, so a stage cannot
reach backwards and change what an earlier stage recorded, and a re-run from the same
declaration reproduces the same values. Later stages override earlier keys, which is what
makes a refinement stage possible without a special mechanism.

Failure is routed, never swallowed
----------------------------------
A non-optional stage that does not pass stops the walk and the unit becomes ``FAILED`` with
the stage's findings. An *optional* stage that does not pass records its findings and the
walk continues — that is the entire meaning of ``optional``. A handler that *raises* is
converted into a recorded failure with the exception's own message, because an unhandled
exception in third-party behaviour must not be able to abort the orchestrator; but the
framework's own fail-closed errors (an unregistered handler, a malformed outcome) propagate,
because those are declaration defects and must not be recorded as if the subject had failed.

Determinism: no wall-clock, no RNG, no I/O. The record's fingerprint is a function of the
plan, the inputs and the handlers, so an identical run yields an identical fingerprint.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.contracts import PipelineDefinition, PipelinePlan
from platform.universal_pipeline.errors import (
    PipelineExecutionError,
    UniversalPipelineError,
)
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.gateway import GatewayTransaction, inputs_hash_for
from platform.universal_pipeline.handlers import StageContext, StageOutcome, run_stage
from platform.universal_pipeline.identity import Identity, mint
from platform.universal_pipeline.observability import PipelineObservability
from platform.universal_pipeline.queue import PipelineQueueManager
from platform.universal_pipeline.registry import PipelineRegistry, PipelineRegistryEntry
from typing import Any


@dataclass(frozen=True, slots=True)
class ExecutionUnit:
    """One unit of work: a registered pipeline version, an identity, and its inputs.

    A unit carries the *declaration and the plan it will run*, not a reference to look them
    up later, so the thing executed is exactly the thing that was admitted. Re-resolving the
    pipeline at execution time would let a registration between admission and execution
    change what runs.
    """

    unit_id: str
    definition: PipelineDefinition
    plan: PipelinePlan
    inputs: Mapping[str, Any] = field(default_factory=dict)
    attempt: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.unit_id, str) or not self.unit_id:
            raise PipelineExecutionError("execution unit id is required")
        if not isinstance(self.definition, PipelineDefinition):
            raise PipelineExecutionError(
                "execution unit requires a PipelineDefinition", unit_id=self.unit_id
            )
        if not isinstance(self.plan, PipelinePlan):
            raise PipelineExecutionError(
                "execution unit requires a PipelinePlan", unit_id=self.unit_id
            )
        if self.plan.pipeline_id != self.definition.pipeline_id:
            raise PipelineExecutionError(
                "execution unit plan belongs to a different pipeline",
                unit_id=self.unit_id,
                pipeline_id=self.definition.pipeline_id,
            )
        if not isinstance(self.inputs, Mapping):
            raise PipelineExecutionError(
                "execution unit inputs must be a mapping", unit_id=self.unit_id
            )
        if self.attempt < 0:
            raise PipelineExecutionError(
                "execution unit attempt must be non-negative", unit_id=self.unit_id
            )

    @classmethod
    def for_entry(
        cls,
        entry: PipelineRegistryEntry,
        unit_id: str,
        *,
        inputs: Mapping[str, Any] | None = None,
        attempt: int = 0,
    ) -> ExecutionUnit:
        """Build a unit from a registry entry — the only sanctioned construction path.

        Raises:
            PipelineExecutionError: if ``entry`` is not a registry entry.
        """
        if not isinstance(entry, PipelineRegistryEntry):
            raise PipelineExecutionError("an execution unit is built from a registry entry")
        return cls(
            unit_id=unit_id,
            definition=entry.definition,
            plan=entry.plan,
            inputs=dict(inputs or {}),
            attempt=attempt,
        )

    @property
    def pipeline_id(self) -> str:
        return self.definition.pipeline_id

    @property
    def version(self) -> str:
        return self.definition.version

    @property
    def identity(self) -> Identity:
        return mint("execution-unit", self.unit_id, self.pipeline_id, self.version)

    def inputs_hash(self) -> str:
        """The hash the gateway authorization binds these inputs by."""
        return inputs_hash_for(self.inputs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "identity": self.identity.value,
            "pipeline_id": self.pipeline_id,
            "version": self.version,
            "attempt": self.attempt,
            "input_keys": sorted(self.inputs),
            "inputs_hash": self.inputs_hash(),
            "plan_fingerprint": self.plan.fingerprint(),
        }


@dataclass(frozen=True, slots=True)
class ExecutionUnitRecord:
    """The immutable, complete account of one execution: every outcome, in order.

    ``passed`` is derived from the outcomes rather than stored independently, so a record
    cannot claim success while carrying a blocking failure. ``outputs`` is the threaded
    result — what the unit produced — and is the evidence a validation stage consumes.
    """

    unit_id: str
    pipeline_id: str
    version: str
    transaction_id: str
    outcomes: tuple[StageOutcome, ...]
    outputs: Mapping[str, Any] = field(default_factory=dict)
    findings: tuple[str, ...] = ()
    attempt: int = 0

    def __post_init__(self) -> None:
        for label, value in (
            ("unit id", self.unit_id),
            ("pipeline id", self.pipeline_id),
            ("version", self.version),
            ("transaction id", self.transaction_id),
        ):
            if not isinstance(value, str) or not value:
                raise PipelineExecutionError(f"execution record {label} is required")
        if not isinstance(self.outcomes, tuple):
            raise PipelineExecutionError(
                "execution record outcomes must be a tuple", unit_id=self.unit_id
            )
        for outcome in self.outcomes:
            if not isinstance(outcome, StageOutcome):
                raise PipelineExecutionError(
                    "execution record outcomes must be StageOutcome values",
                    unit_id=self.unit_id,
                )
        if not isinstance(self.outputs, Mapping):
            raise PipelineExecutionError(
                "execution record outputs must be a mapping", unit_id=self.unit_id
            )

    @property
    def passed(self) -> bool:
        """True iff no recorded outcome carries an unwaived failure."""
        return not self.findings

    @property
    def identity(self) -> Identity:
        return mint("execution-unit", self.unit_id, self.transaction_id, self.fingerprint())

    @property
    def stages_run(self) -> tuple[str, ...]:
        """The stage ids actually executed, in execution order."""
        return tuple(outcome.stage_id for outcome in self.outcomes)

    def outcome_of(self, stage_id: str) -> StageOutcome:
        """The recorded outcome of ``stage_id``.

        Raises:
            PipelineExecutionError: if the stage did not run (fail-closed — an absent
                outcome is not a passing one).
        """
        for outcome in self.outcomes:
            if outcome.stage_id == stage_id:
                return outcome
        raise PipelineExecutionError(
            "stage did not run in this execution", unit_id=self.unit_id, stage_id=stage_id
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "pipeline_id": self.pipeline_id,
            "version": self.version,
            "transaction_id": self.transaction_id,
            "attempt": self.attempt,
            "passed": self.passed,
            "stages_run": list(self.stages_run),
            "outcomes": [outcome.to_dict() for outcome in self.outcomes],
            "outputs": dict(self.outputs),
            "findings": list(self.findings),
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of the whole execution."""
        return content_hash(
            {
                "unit_id": self.unit_id,
                "pipeline_id": self.pipeline_id,
                "version": self.version,
                "outcomes": [outcome.to_dict() for outcome in self.outcomes],
                "outputs": dict(self.outputs),
                "findings": list(self.findings),
            }
        )


class PipelineRuntime:
    """Walks a derived plan for one admitted unit, recording every outcome.

    Optionally bound to a queue (so lifecycle transitions are driven as work progresses), a
    bus (so the walk is recorded) and observability (so outcomes are measured). All three are
    optional because the runtime must be usable in isolation to be testable in isolation —
    and a runtime that could only run inside a full platform could not be proven pure.
    """

    __slots__ = ("_registry", "_queue", "_bus", "_observability")

    def __init__(
        self,
        registry: PipelineRegistry,
        *,
        queue: PipelineQueueManager | None = None,
        bus: PipelineEventBus | None = None,
        observability: PipelineObservability | None = None,
    ) -> None:
        if not isinstance(registry, PipelineRegistry):
            raise PipelineExecutionError("runtime requires a PipelineRegistry")
        if queue is not None and not isinstance(queue, PipelineQueueManager):
            raise PipelineExecutionError("queue must be a PipelineQueueManager")
        if bus is not None and not isinstance(bus, PipelineEventBus):
            raise PipelineExecutionError("bus must be a PipelineEventBus")
        if observability is not None and not isinstance(observability, PipelineObservability):
            raise PipelineExecutionError("observability must be a PipelineObservability")
        self._registry = registry
        self._queue = queue
        self._bus = bus
        self._observability = observability

    def execute(self, unit: ExecutionUnit, transaction: GatewayTransaction) -> ExecutionUnitRecord:
        """Execute ``unit`` under ``transaction`` and return the complete record.

        Raises:
            PipelineExecutionError: if the transaction does not authorize *this* unit with
                *these* inputs (the bypass check), or if a declared stage handler is
                unregistered.
            PipelineStateError: if a lifecycle transition the queue is asked to make is
                illegal.
        """
        self._require_authorized(unit, transaction)
        threaded: dict[str, Any] = dict(unit.inputs)
        outcomes: list[StageOutcome] = []
        findings: list[str] = []
        for wave in unit.plan.wave_indices:
            for stage_id in unit.plan.stages_in_wave(wave):
                stage = unit.definition.stage(stage_id)
                outcome = self._run(unit, stage_id, threaded)
                outcomes.append(outcome)
                threaded.update(outcome.outputs)
                self._record_stage(unit, wave, outcome)
                if outcome.passed:
                    continue
                if stage.optional:
                    findings.extend(
                        f"optional stage {stage_id} did not pass: {finding}"
                        for finding in outcome.findings
                    )
                    continue
                findings.extend(
                    f"stage {stage_id} did not pass: {finding}" for finding in outcome.findings
                )
                return self._finish(unit, transaction, outcomes, threaded, tuple(findings))
        # An optional-stage finding is recorded but does not fail the unit, so a record with
        # only optional findings must still be reported as passed.
        blocking = tuple(f for f in findings if not f.startswith("optional stage "))
        record = self._finish(unit, transaction, outcomes, threaded, blocking)
        if findings and not blocking:
            self._emit("uapf.stage.completed", unit.unit_id, {"advisory_findings": findings})
        return record

    # -- internals --------------------------------------------------------------------

    def _require_authorized(self, unit: ExecutionUnit, transaction: GatewayTransaction) -> None:
        """The bypass check: the transaction must authorize this unit with these inputs."""
        if not isinstance(unit, ExecutionUnit):
            raise PipelineExecutionError("only an ExecutionUnit can be executed")
        if not isinstance(transaction, GatewayTransaction):
            raise PipelineExecutionError(
                "execution requires a gateway transaction (nothing bypasses the gateway)",
                unit_id=unit.unit_id,
            )
        transaction.require_authorized()
        mismatch = {
            "unit_id": (transaction.unit_id, unit.unit_id),
            "pipeline_id": (transaction.pipeline_id, unit.pipeline_id),
            "version": (transaction.version, unit.version),
            "inputs_hash": (transaction.inputs_hash, unit.inputs_hash()),
        }
        for field_name, (authorized, actual) in mismatch.items():
            if authorized != actual:
                raise PipelineExecutionError(
                    "gateway transaction does not authorize this execution",
                    unit_id=unit.unit_id,
                    mismatched=field_name,
                    authorized=authorized,
                    actual=actual,
                )
        # The pipeline must still be registered: a transaction is not a licence to run
        # something the registry no longer holds.
        self._registry.get(unit.pipeline_id, unit.version)

    def _run(self, unit: ExecutionUnit, stage_id: str, threaded: Mapping[str, Any]) -> StageOutcome:
        """Run one stage, converting a handler exception into a recorded failure.

        A framework error (unregistered handler, malformed outcome) is a declaration defect
        and propagates. A handler's *own* exception is a failure of the subject, so it is
        recorded as one — which is what keeps a third-party handler from halting autonomy.
        """
        stage = unit.definition.stage(stage_id)
        context = StageContext(
            pipeline_id=unit.pipeline_id,
            version=unit.version,
            unit_id=unit.unit_id,
            stage=stage,
            inputs=dict(threaded),
            attempt=unit.attempt,
        )
        try:
            return run_stage(context)
        except UniversalPipelineError:
            raise
        except Exception as exc:  # noqa: BLE001 — a handler fault is the subject's failure
            return StageOutcome(
                stage_id=stage_id,
                status="FAIL",
                findings=(f"stage handler raised {type(exc).__name__}: {exc}",),
                outputs={},
            )

    def _record_stage(self, unit: ExecutionUnit, wave: int, outcome: StageOutcome) -> None:
        if self._observability is not None:
            self._observability.observe_outcome(
                outcome.stage_id, outcome.passed, pipeline_id=unit.pipeline_id
            )
        self._emit(
            "uapf.stage.completed",
            unit.unit_id,
            {
                "wave": wave,
                "stage_id": outcome.stage_id,
                "status": outcome.status,
                "evidence_hash": outcome.evidence_hash(),
            },
        )

    def _finish(
        self,
        unit: ExecutionUnit,
        transaction: GatewayTransaction,
        outcomes: list[StageOutcome],
        threaded: Mapping[str, Any],
        findings: tuple[str, ...],
    ) -> ExecutionUnitRecord:
        """Build the record and drive the unit's lifecycle to its post-execution state."""
        record = ExecutionUnitRecord(
            unit_id=unit.unit_id,
            pipeline_id=unit.pipeline_id,
            version=unit.version,
            transaction_id=transaction.transaction_id,
            outcomes=tuple(outcomes),
            outputs=dict(threaded),
            findings=findings,
            attempt=unit.attempt,
        )
        if self._queue is not None and unit.unit_id in self._queue:
            if record.passed:
                self._queue.advance(unit.unit_id, "IMPLEMENTED")
            else:
                self._queue.fail(unit.unit_id, findings[0])
        if self._observability is not None:
            self._observability.record_span(
                "uapf.execution.stages", len(outcomes), unit_id=unit.unit_id
            )
        return record

    def _emit(self, category: str, subject: str, payload: dict[str, Any]) -> None:
        if self._bus is not None:
            self._bus.emit(category, subject, payload=payload)


__all__ = ["ExecutionUnit", "ExecutionUnitRecord", "PipelineRuntime"]
