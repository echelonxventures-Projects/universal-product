"""UAPF-000001 — tests for the integration gateway and the execution engine.

The central claim: **nothing bypasses the gateway**, and that is enforced by arithmetic rather
than by convention. A transaction's authorization is a content hash over the pipeline, version,
unit and inputs it was admitted for, so altering any of them invalidates it — and the runtime
recomputes it before doing anything. These tests attack that property directly: forge a
transaction, swap its inputs, reuse another unit's admission, and execute with none at all.

The execution claim: the runtime decides nothing. It walks a derived plan, threads outputs
forward without a shared mutable context, records every outcome, and routes failure — converting
a *handler's* exception into a recorded failure while letting the framework's own fail-closed
errors propagate, because those are declaration defects rather than facts about the subject.
"""

from __future__ import annotations

import dataclasses
from platform.universal_pipeline.contracts import (
    PipelineDefinition,
    PipelineGateSpec,
    PipelineGovernanceSpec,
    PipelineSecuritySpec,
    StageDefinition,
)
from platform.universal_pipeline.errors import (
    PipelineExecutionError,
    PipelineGatewayError,
    PipelineGovernanceError,
    PipelineHandlerError,
)
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.execution import (
    ExecutionUnit,
    ExecutionUnitRecord,
    PipelineRuntime,
)
from platform.universal_pipeline.gateway import (
    GatewayTransaction,
    UniversalPipelineGateway,
    authorization_for,
    inputs_hash_for,
)
from platform.universal_pipeline.governance import PipelineGovernance, obligations_from
from platform.universal_pipeline.handlers import (
    CONTINUE_STATUS,
    StageContext,
    StageOutcome,
    register_stage_handler,
)
from platform.universal_pipeline.observability import PipelineObservability
from platform.universal_pipeline.queue import PipelineQueueManager, QueueEntry
from platform.universal_pipeline.registry import PipelineRegistry

import pytest

PIPELINE = "test.execution"


def _definition(
    *,
    stages: tuple[StageDefinition, ...] | None = None,
    version: str = "1.0.0",
    security: PipelineSecuritySpec | None = None,
    governance: PipelineGovernanceSpec | None = None,
) -> PipelineDefinition:
    return PipelineDefinition(
        pipeline_id=PIPELINE,
        pipeline_type="implementation",
        version=version,
        stages=stages
        or (
            StageDefinition(stage_id="first", handler="uapf.record"),
            StageDefinition(stage_id="second", handler="uapf.record", requires=("first",)),
        ),
        security=security or PipelineSecuritySpec(),
        governance=governance or PipelineGovernanceSpec(),
    )


def _registry(definition: PipelineDefinition | None = None) -> PipelineRegistry:
    registry = PipelineRegistry()
    registry.register(definition or _definition())
    return registry


# ------------------------------------------------------------------------------- gateway


def test_a_submission_is_admitted_and_authorized_for_exactly_its_own_work() -> None:
    registry = _registry()
    gateway = UniversalPipelineGateway(registry)
    transaction = gateway.submit(PIPELINE, "u1", inputs={"alpha": 1})
    assert transaction.verify()
    transaction.require_authorized()
    assert transaction.unit_id == "u1"
    assert transaction.pipeline_id == PIPELINE
    assert transaction.version == "1.0.0"
    assert transaction.inputs_hash == inputs_hash_for({"alpha": 1})
    assert transaction.authorization == authorization_for(transaction.core())
    assert transaction.identity.kind == "transaction"
    assert transaction.transaction_id == transaction.identity.value
    assert gateway.is_admitted("u1")
    assert gateway.transaction("u1") == transaction
    assert gateway.admitted == (transaction,)
    assert len(gateway) == 1
    assert transaction.to_dict()["unit_id"] == "u1"


def test_resubmitting_identical_work_is_idempotent() -> None:
    gateway = UniversalPipelineGateway(_registry())
    first = gateway.submit(PIPELINE, "u1", inputs={"alpha": 1})
    second = gateway.submit(PIPELINE, "u1", inputs={"alpha": 1})
    assert first == second
    assert len(gateway) == 1


def test_altering_an_admitted_transaction_invalidates_its_authorization() -> None:
    gateway = UniversalPipelineGateway(_registry())
    transaction = gateway.submit(PIPELINE, "u1", inputs={"alpha": 1})
    for field, value in [
        ("inputs_hash", inputs_hash_for({"alpha": 2})),
        ("unit_id", "u2"),
        ("pipeline_id", "other"),
        ("version", "9.9.9"),
        ("permissions", ("admin",)),
    ]:
        forged = dataclasses.replace(transaction, **{field: value})
        assert not forged.verify()
        with pytest.raises(PipelineGatewayError, match="bypass attempt"):
            forged.require_authorized()


def test_an_unregistered_pipeline_is_refused_and_the_refusal_is_recorded() -> None:
    bus = PipelineEventBus()
    gateway = UniversalPipelineGateway(_registry(), bus=bus)
    with pytest.raises(PipelineGatewayError, match="unregistered pipeline"):
        gateway.submit("no.such.pipeline", "u1")
    # Recorded first, then raised — so the attempt is auditable.
    refusals = bus.events_of("uapf.gateway.refused")
    assert len(refusals) == 1
    assert refusals[0].payload["pipeline_id"] == "no.such.pipeline"
    with pytest.raises(PipelineGatewayError, match="unregistered pipeline"):
        gateway.submit(PIPELINE, "u1", version="9.9.9")


def test_a_principal_lacking_a_required_permission_is_refused() -> None:
    registry = _registry(
        _definition(security=PipelineSecuritySpec(required_permissions=("execute", "admin")))
    )
    gateway = UniversalPipelineGateway(registry)
    with pytest.raises(PipelineGatewayError, match="lacks a permission") as raised:
        gateway.submit(PIPELINE, "u1", permissions=["execute"])
    assert raised.value.context["missing"] == ["admin"]
    transaction = gateway.submit(PIPELINE, "u1", permissions=["execute", "admin"])
    assert transaction.permissions == ("admin", "execute")


def test_governance_can_refuse_a_submission() -> None:
    bus = PipelineEventBus()
    registry = _registry(
        _definition(governance=PipelineGovernanceSpec(obligations=("truth.synchronized",)))
    )
    governance = PipelineGovernance(bus=bus)
    gateway = UniversalPipelineGateway(registry, governance=governance, bus=bus)
    with pytest.raises(PipelineGovernanceError, match="governance refused"):
        gateway.submit(PIPELINE, "u1")
    assert any(
        event.payload.get("reason") == "governance refused the submission"
        for event in bus.events_of("uapf.gateway.refused")
    )
    admitted = gateway.submit(PIPELINE, "u1", evidence=obligations_from(["truth.synchronized"]))
    assert admitted.verify()


def test_an_unadmitted_unit_has_no_transaction() -> None:
    gateway = UniversalPipelineGateway(_registry())
    assert not gateway.is_admitted("u1")
    with pytest.raises(PipelineGatewayError, match="never admitted"):
        gateway.transaction("u1")


def test_gateway_construction_and_submission_are_validated() -> None:
    with pytest.raises(PipelineGatewayError, match="requires a PipelineRegistry"):
        UniversalPipelineGateway("registry")  # type: ignore[arg-type]
    with pytest.raises(PipelineGatewayError, match="must be a PipelineGovernance"):
        UniversalPipelineGateway(_registry(), governance="g")  # type: ignore[arg-type]
    with pytest.raises(PipelineGatewayError, match="must be a PipelineEventBus"):
        UniversalPipelineGateway(_registry(), bus="b")  # type: ignore[arg-type]
    gateway = UniversalPipelineGateway(_registry())
    with pytest.raises(PipelineGatewayError, match="unit id is required"):
        gateway.submit(PIPELINE, "")
    with pytest.raises(PipelineGatewayError, match="inputs must be a mapping"):
        gateway.submit(PIPELINE, "u1", inputs=["alpha"])  # type: ignore[arg-type]
    assert gateway.fingerprint() == gateway.fingerprint()
    assert gateway.to_dict()["admitted_count"] == 0


@pytest.mark.parametrize(
    "field", ["pipeline_id", "version", "unit_id", "inputs_hash", "authorization"]
)
def test_transaction_requires_every_core_field(field: str) -> None:
    fields = {
        "pipeline_id": "p",
        "version": "1.0.0",
        "unit_id": "u",
        "inputs_hash": "h",
        "authorization": "a",
    }
    fields[field] = ""
    with pytest.raises(PipelineGatewayError, match="is required"):
        GatewayTransaction(**fields)  # type: ignore[arg-type]


def test_transaction_validates_its_optional_fields() -> None:
    with pytest.raises(PipelineGatewayError, match="permissions must be a tuple"):
        GatewayTransaction(
            pipeline_id="p",
            version="1.0.0",
            unit_id="u",
            inputs_hash="h",
            authorization="a",
            permissions=["x"],  # type: ignore[arg-type]
        )
    with pytest.raises(PipelineGatewayError, match="detail must be a mapping"):
        GatewayTransaction(
            pipeline_id="p",
            version="1.0.0",
            unit_id="u",
            inputs_hash="h",
            authorization="a",
            detail=[],  # type: ignore[arg-type]
        )


# ----------------------------------------------------------------------------- execution


def _execute(
    definition: PipelineDefinition | None = None,
    *,
    inputs: dict[str, object] | None = None,
    with_queue: bool = True,
) -> tuple[ExecutionUnitRecord, PipelineQueueManager]:
    resolved = definition or _definition()
    registry = _registry(resolved)
    entry = registry.get(resolved.pipeline_id, resolved.version)
    queue = PipelineQueueManager()
    queue.enqueue(
        QueueEntry(unit_id="u1", pipeline_id=resolved.pipeline_id, version=resolved.version)
    )
    queue.promote("u1")
    queue.cut()
    gateway = UniversalPipelineGateway(registry)
    transaction = gateway.submit(resolved.pipeline_id, "u1", inputs=inputs)
    runtime = PipelineRuntime(registry, queue=queue if with_queue else None)
    unit = ExecutionUnit.for_entry(entry, "u1", inputs=inputs)
    return runtime.execute(unit, transaction), queue


def test_a_plan_is_walked_in_wave_order_and_outputs_thread_forward() -> None:
    record, queue = _execute()
    assert record.passed
    assert record.stages_run == ("first", "second")
    assert record.outcome_of("first").passed
    # The second stage saw the first stage's outputs.
    assert record.outputs["recorded_stage"] == "second"
    assert queue.entry("u1").state == "IMPLEMENTED"
    assert record.identity.kind == "execution-unit"
    assert record.to_dict()["passed"] is True
    with pytest.raises(PipelineExecutionError, match="did not run"):
        record.outcome_of("never")


def test_identical_declarations_and_inputs_reproduce_the_record() -> None:
    left, _ = _execute(inputs={"alpha": 1})
    right, _ = _execute(inputs={"alpha": 1})
    assert left.fingerprint() == right.fingerprint()
    other, _ = _execute(inputs={"alpha": 2})
    assert other.fingerprint() != left.fingerprint()


def test_a_gate_stage_is_discharged_by_a_preceding_stages_output() -> None:
    """Outputs threading forward is what lets a pipeline discharge its own declared gate."""
    definition = _definition(
        stages=(
            StageDefinition(stage_id="record", handler="uapf.record"),
            StageDefinition(
                stage_id="gate",
                handler="uapf.gate",
                requires=("record",),
                gates=(PipelineGateSpec("G", "recorded_stage"),),
            ),
        )
    )
    record, queue = _execute(definition)
    assert record.passed
    assert queue.entry("u1").state == "IMPLEMENTED"


def test_a_blocking_stage_failure_stops_the_walk_and_fails_the_unit() -> None:
    definition = _definition(
        stages=(
            StageDefinition(
                stage_id="gate",
                handler="uapf.gate",
                gates=(PipelineGateSpec("G", "never.supplied"),),
            ),
            StageDefinition(stage_id="after", handler="uapf.record", requires=("gate",)),
        )
    )
    record, queue = _execute(definition)
    assert not record.passed
    assert record.stages_run == ("gate",)
    assert "after" not in record.stages_run
    assert record.findings[0].startswith("stage gate did not pass")
    assert queue.entry("u1").state == "FAILED"
    assert queue.entry("u1").reason == record.findings[0]


def test_an_optional_stage_failure_records_a_finding_and_the_walk_continues() -> None:
    definition = _definition(
        stages=(
            StageDefinition(
                stage_id="advisory",
                handler="uapf.gate",
                gates=(PipelineGateSpec("G", "never.supplied"),),
                optional=True,
            ),
            StageDefinition(stage_id="after", handler="uapf.record", requires=("advisory",)),
        )
    )
    record, queue = _execute(definition)
    assert record.passed
    assert record.stages_run == ("advisory", "after")
    assert queue.entry("u1").state == "IMPLEMENTED"


def test_a_handler_exception_becomes_a_recorded_failure_not_a_crash() -> None:
    def explodes(context: StageContext) -> StageOutcome:
        raise RuntimeError("handler blew up")

    register_stage_handler("test.handler.explodes", explodes)
    definition = _definition(
        stages=(StageDefinition(stage_id="boom", handler="test.handler.explodes"),)
    )
    record, queue = _execute(definition)
    assert not record.passed
    assert "handler blew up" in record.findings[0]
    assert "RuntimeError" in record.findings[0]
    assert queue.entry("u1").state == "FAILED"


def test_a_framework_error_inside_a_handler_still_propagates() -> None:
    """A declaration defect must not be recorded as if the subject had failed."""

    def raises_framework_error(context: StageContext) -> StageOutcome:
        raise PipelineHandlerError("a declaration defect, not a subject failure")

    register_stage_handler("test.handler.framework-error", raises_framework_error)
    definition = _definition(
        stages=(StageDefinition(stage_id="s", handler="test.handler.framework-error"),)
    )
    with pytest.raises(PipelineHandlerError, match="declaration defect"):
        _execute(definition)


def test_execution_without_a_gateway_transaction_is_impossible() -> None:
    registry = _registry()
    entry = registry.get(PIPELINE)
    runtime = PipelineRuntime(registry)
    unit = ExecutionUnit.for_entry(entry, "u1")
    with pytest.raises(PipelineExecutionError, match="nothing bypasses the gateway"):
        runtime.execute(unit, None)  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="only an ExecutionUnit"):
        runtime.execute("unit", None)  # type: ignore[arg-type]


def test_a_transaction_admitted_for_other_work_is_refused() -> None:
    registry = _registry()
    entry = registry.get(PIPELINE)
    gateway = UniversalPipelineGateway(registry)
    runtime = PipelineRuntime(registry)
    other_unit = gateway.submit(PIPELINE, "u2")
    with pytest.raises(PipelineExecutionError, match="does not authorize") as raised:
        runtime.execute(ExecutionUnit.for_entry(entry, "u1"), other_unit)
    assert raised.value.context["mismatched"] == "unit_id"
    # Inputs are bound into the authorization, so swapping them is caught too.
    admitted = gateway.submit(PIPELINE, "u1", inputs={"alpha": 1})
    with pytest.raises(PipelineExecutionError, match="does not authorize") as raised:
        runtime.execute(ExecutionUnit.for_entry(entry, "u1", inputs={"alpha": 2}), admitted)
    assert raised.value.context["mismatched"] == "inputs_hash"


def test_a_forged_transaction_is_refused_before_anything_runs() -> None:
    registry = _registry()
    entry = registry.get(PIPELINE)
    gateway = UniversalPipelineGateway(registry)
    transaction = gateway.submit(PIPELINE, "u1")
    forged = dataclasses.replace(transaction, authorization="deadbeef")
    with pytest.raises(PipelineGatewayError, match="bypass attempt"):
        PipelineRuntime(registry).execute(ExecutionUnit.for_entry(entry, "u1"), forged)


def test_execution_records_stages_and_measures_outcomes() -> None:
    bus = PipelineEventBus()
    observability = PipelineObservability()
    registry = _registry()
    entry = registry.get(PIPELINE)
    gateway = UniversalPipelineGateway(registry)
    runtime = PipelineRuntime(registry, bus=bus, observability=observability)
    runtime.execute(ExecutionUnit.for_entry(entry, "u1"), gateway.submit(PIPELINE, "u1"))
    assert len(bus.events_of("uapf.stage.completed")) == 2
    assert observability.total("uapf.stage.passed") == 2.0
    assert observability.total("uapf.execution.stages") == 2.0
    assert observability.health()["status"] == "HEALTHY"


def test_a_runtime_without_a_queue_still_executes() -> None:
    record, _ = _execute(with_queue=False)
    assert record.passed


def test_runtime_construction_is_validated() -> None:
    registry = _registry()
    with pytest.raises(PipelineExecutionError, match="requires a PipelineRegistry"):
        PipelineRuntime("registry")  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="queue must be"):
        PipelineRuntime(registry, queue="q")  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="bus must be"):
        PipelineRuntime(registry, bus="b")  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="observability must be"):
        PipelineRuntime(registry, observability="o")  # type: ignore[arg-type]


def test_execution_unit_validates_its_own_shape() -> None:
    definition = _definition()
    registry = _registry(definition)
    entry = registry.get(PIPELINE)
    assert ExecutionUnit.for_entry(entry, "u1").identity.kind == "execution-unit"
    assert ExecutionUnit.for_entry(entry, "u1").to_dict()["pipeline_id"] == PIPELINE
    with pytest.raises(PipelineExecutionError, match="built from a registry entry"):
        ExecutionUnit.for_entry("entry", "u1")  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="unit id is required"):
        ExecutionUnit(unit_id="", definition=definition, plan=entry.plan)
    with pytest.raises(PipelineExecutionError, match="requires a PipelineDefinition"):
        ExecutionUnit(unit_id="u", definition="d", plan=entry.plan)  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="requires a PipelinePlan"):
        ExecutionUnit(unit_id="u", definition=definition, plan="p")  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="inputs must be a mapping"):
        ExecutionUnit(unit_id="u", definition=definition, plan=entry.plan, inputs=[])  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="attempt must be non-negative"):
        ExecutionUnit(unit_id="u", definition=definition, plan=entry.plan, attempt=-1)
    other = _registry(_definition(version="2.0.0"))
    with pytest.raises(PipelineExecutionError, match="different pipeline"):
        ExecutionUnit(
            unit_id="u",
            definition=PipelineDefinition(
                pipeline_id="other",
                pipeline_type="implementation",
                version="1.0.0",
                stages=(StageDefinition(stage_id="s", handler="uapf.record"),),
            ),
            plan=other.get(PIPELINE, "2.0.0").plan,
        )


def test_execution_record_validates_its_own_shape() -> None:
    outcome = StageOutcome(stage_id="s", status=CONTINUE_STATUS)
    fields: dict[str, object] = {
        "unit_id": "u",
        "pipeline_id": "p",
        "version": "1.0.0",
        "transaction_id": "t",
        "outcomes": (outcome,),
    }
    assert ExecutionUnitRecord(**fields).passed  # type: ignore[arg-type]
    for field in ("unit_id", "pipeline_id", "version", "transaction_id"):
        broken = dict(fields)
        broken[field] = ""
        with pytest.raises(PipelineExecutionError, match="is required"):
            ExecutionUnitRecord(**broken)  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="outcomes must be a tuple"):
        ExecutionUnitRecord(**{**fields, "outcomes": [outcome]})  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="must be StageOutcome values"):
        ExecutionUnitRecord(**{**fields, "outcomes": ("s",)})  # type: ignore[arg-type]
    with pytest.raises(PipelineExecutionError, match="outputs must be a mapping"):
        ExecutionUnitRecord(**{**fields, "outputs": []})  # type: ignore[arg-type]
