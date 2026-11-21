"""UAPF-000001 — tests for the scheduler, the handler registry, governance and assurance.

Four engines, one shared theme: each decides exactly one thing and refuses to decide anything
else. The scheduler derives an order and starts nothing. A handler receives a declaration and
can cause no effect. Governance evaluates declared obligations and holds no rule text. The
assurance engine judges no subject — it only enforces that validation, verification and
certification happened in the order Repository Truth requires.
"""

from __future__ import annotations

from platform.universal_pipeline.assurance import (
    ASSURANCE_ACTS,
    CertificationRecord,
    PipelineAssurance,
    ValidationRecord,
    VerificationRecord,
)
from platform.universal_pipeline.contracts import (
    PipelineDefinition,
    PipelineGateSpec,
    PipelineGovernanceSpec,
    PipelinePolicy,
    StageDefinition,
)
from platform.universal_pipeline.dependencies import DependencyManager
from platform.universal_pipeline.errors import (
    PipelineCertificationError,
    PipelineGovernanceError,
    PipelineHandlerError,
    PipelineObservabilityError,
    PipelineScheduleError,
    PipelineStateError,
    PipelineValidationError,
)
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.governance import (
    GOVERNANCE_AUTHORITY,
    GovernanceVerdict,
    PipelineGovernance,
    RecoveryPoint,
    obligations_from,
)
from platform.universal_pipeline.handlers import (
    CONTINUE_STATUS,
    GATE_HANDLER,
    RECORD_HANDLER,
    STAGE_OUTCOME_STATUSES,
    StageContext,
    StageOutcome,
    get_stage_handler,
    register_stage_handler,
    require_stage_handler,
    run_stage,
    stage_handler_names,
)
from platform.universal_pipeline.observability import (
    DEGRADED,
    FAILURE_METRIC,
    HEALTHY,
    SUCCESS_METRIC,
    TELEMETRY_KINDS,
    PipelineObservability,
    PipelineTelemetry,
)
from platform.universal_pipeline.scheduler import (
    DEFAULT_SCHEDULE_STRATEGY,
    PipelineSchedule,
    PipelineScheduler,
)

import pytest


def _manager() -> DependencyManager:
    manager = DependencyManager()
    manager.declare("root")
    manager.declare("left", ["root"])
    manager.declare("right", ["root"])
    manager.declare("join", ["left", "right"])
    return manager


def _context(stage: StageDefinition, **inputs: object) -> StageContext:
    return StageContext(
        pipeline_id="test.pipeline", version="1.0.0", unit_id="u1", stage=stage, inputs=inputs
    )


# ----------------------------------------------------------------------------- scheduler


def test_schedule_expresses_declared_concurrency_and_starts_nothing() -> None:
    schedule = PipelineScheduler().schedule(_manager())
    assert schedule.strategy == DEFAULT_SCHEDULE_STRATEGY
    assert schedule.wave_count == 3
    assert schedule.max_parallelism == 2
    assert schedule.units_in_wave(0) == ("root",)
    assert schedule.units_in_wave(1) == ("left", "right")
    assert schedule.units_in_wave(2) == ("join",)
    assert schedule.wave_of("join") == 2
    assert schedule.wave_indices == (0, 1, 2)
    assert set(schedule.unit_ids) == {"root", "left", "right", "join"}
    assert schedule.identity.kind == "schedule"
    assert schedule.to_dict()["unit_count"] == 4
    # A schedule is a comparable value: re-deriving it reproduces the fingerprint.
    assert schedule.fingerprint() == PipelineScheduler().schedule(_manager()).fingerprint()


def test_schedule_is_available_as_a_strict_sequence_too() -> None:
    schedule = PipelineScheduler().schedule(_manager(), strategy="dependency-order")
    assert schedule.wave_count == 4
    assert schedule.max_parallelism == 1


def test_an_empty_schedule_is_legitimate() -> None:
    schedule = PipelineScheduler().schedule(DependencyManager())
    assert schedule.waves == ()
    assert schedule.wave_count == 0
    assert schedule.max_parallelism == 0
    with pytest.raises(PipelineScheduleError, match="not in this schedule"):
        schedule.wave_of("anything")


def test_scheduling_fails_closed_on_bad_inputs() -> None:
    scheduler = PipelineScheduler()
    with pytest.raises(PipelineScheduleError, match="derived from a DependencyManager"):
        scheduler.schedule("not a manager")  # type: ignore[arg-type]
    with pytest.raises(PipelineScheduleError, match="must be a mapping"):
        scheduler.schedule_graph([("a", ())])  # type: ignore[arg-type]
    with pytest.raises(PipelineScheduleError, match="unregistered ordering strategy"):
        scheduler.schedule_graph({"a": ()}, strategy="no-such-strategy")
    with pytest.raises(PipelineScheduleError, match="closure honesty"):
        scheduler.schedule_graph({"a": ("ghost",)})
    with pytest.raises(PipelineScheduleError, match="contains a cycle"):
        scheduler.schedule_graph({"a": ("b",), "b": ("a",)})


def test_critical_path_ranks_by_transitive_dependent_count() -> None:
    scheduler = PipelineScheduler()
    ranked = scheduler.critical_path(_manager())
    assert ranked[0] == ("root", 3)
    assert dict(ranked)["join"] == 0
    assert scheduler.critical_path(_manager(), limit=2) == ranked[:2]
    with pytest.raises(PipelineScheduleError, match="limit must be a positive integer"):
        scheduler.critical_path(_manager(), limit=0)
    with pytest.raises(PipelineScheduleError, match="derived from a DependencyManager"):
        scheduler.critical_path("x")  # type: ignore[arg-type]


def test_schedule_validates_its_own_shape() -> None:
    with pytest.raises(PipelineScheduleError, match="strategy is required"):
        PipelineSchedule(strategy="", waves=())
    with pytest.raises(PipelineScheduleError, match="waves must be a tuple"):
        PipelineSchedule(strategy="s", waves=[])  # type: ignore[arg-type]


# ------------------------------------------------------------------------------ handlers


def test_the_built_in_record_handler_accounts_for_a_stage_and_passes() -> None:
    stage = StageDefinition(stage_id="s", handler=RECORD_HANDLER)
    outcome = run_stage(_context(stage, alpha=1, beta=2))
    assert outcome.status == CONTINUE_STATUS
    assert outcome.passed
    assert outcome.outputs["recorded_stage"] == "s"
    assert outcome.outputs["recorded_handler"] == RECORD_HANDLER
    # Input *keys*, never values: a recording stage proves it saw them (SEC-04).
    assert outcome.outputs["recorded_input_keys"] == ["alpha", "beta"]
    assert "declaration_fingerprint" in outcome.outputs
    assert outcome.identity.kind == "handler"
    assert outcome.evidence_hash() == run_stage(_context(stage, alpha=1, beta=2)).evidence_hash()


def test_the_built_in_gate_handler_discharges_gates_it_has_never_heard_of() -> None:
    stage = StageDefinition(
        stage_id="g",
        handler=GATE_HANDLER,
        gates=(
            PipelineGateSpec("G.block", "obligation.required"),
            PipelineGateSpec("G.advise", "obligation.advisory", blocking=False),
        ),
    )
    refused = run_stage(_context(stage))
    assert refused.status == "FAIL"
    assert "undischarged blocking obligation: obligation.required" in refused.findings
    assert any("advisory gate not discharged" in f for f in refused.findings)
    assert refused.outputs["undischarged"] == ["obligation.required"]

    admitted = run_stage(_context(stage, **{"obligation.required": True}))
    assert admitted.passed
    assert admitted.outputs["discharged"] == ["obligation.required"]
    assert admitted.outputs["gate_count"] == 2
    # The advisory gate is still reported, but does not fail the stage.
    assert any("advisory" in f for f in admitted.findings)


def test_a_stage_with_no_gates_passes_the_gate_handler() -> None:
    outcome = run_stage(_context(StageDefinition(stage_id="g", handler=GATE_HANDLER)))
    assert outcome.passed
    assert outcome.findings == ()


def test_handlers_are_open_by_registration_and_append_only() -> None:
    def handler(context: StageContext) -> StageOutcome:
        return StageOutcome(stage_id=context.stage_id, status=CONTINUE_STATUS)

    register_stage_handler("test.handler.open-world", handler, "registered by a test")
    assert "test.handler.open-world" in stage_handler_names()
    require_stage_handler("test.handler.open-world")
    assert get_stage_handler("test.handler.open-world") is handler
    with pytest.raises(PipelineHandlerError, match="already registered"):
        register_stage_handler("test.handler.open-world", handler)
    with pytest.raises(PipelineHandlerError, match="must be callable"):
        register_stage_handler("test.handler.not-callable", "nope")  # type: ignore[arg-type]
    with pytest.raises(PipelineHandlerError, match="unregistered term"):
        require_stage_handler("test.handler.absent")


def test_a_stage_naming_an_unregistered_handler_fails_closed() -> None:
    stage = StageDefinition(stage_id="s", handler="test.handler.never-registered")
    with pytest.raises(PipelineHandlerError, match="unregistered term"):
        run_stage(_context(stage))


def test_a_handler_returning_the_wrong_thing_is_refused() -> None:
    register_stage_handler("test.handler.returns-junk", lambda context: "not an outcome")
    register_stage_handler(
        "test.handler.wrong-stage",
        lambda context: StageOutcome(stage_id="someone-else", status=CONTINUE_STATUS),
    )
    with pytest.raises(PipelineHandlerError, match="did not return a StageOutcome"):
        run_stage(_context(StageDefinition(stage_id="s", handler="test.handler.returns-junk")))
    with pytest.raises(PipelineHandlerError, match="outcome for a different stage"):
        run_stage(_context(StageDefinition(stage_id="s", handler="test.handler.wrong-stage")))
    with pytest.raises(PipelineHandlerError, match="run from a StageContext"):
        run_stage("not a context")  # type: ignore[arg-type]


def test_stage_context_is_closed_and_validated() -> None:
    stage = StageDefinition(stage_id="s", handler=RECORD_HANDLER)
    context = _context(stage, alpha=1)
    assert context.stage_id == "s"
    assert context.handler == RECORD_HANDLER
    assert context.input("alpha") == 1
    assert context.input("absent", "fallback") == "fallback"
    assert context.to_dict()["input_keys"] == ["alpha"]
    with pytest.raises(PipelineHandlerError, match="pipeline id is required"):
        StageContext(pipeline_id="", version="1.0.0", unit_id="u", stage=stage)
    with pytest.raises(PipelineHandlerError, match="unit id is required"):
        StageContext(pipeline_id="p", version="1.0.0", unit_id="", stage=stage)
    with pytest.raises(PipelineHandlerError, match="requires a StageDefinition"):
        StageContext(pipeline_id="p", version="1.0.0", unit_id="u", stage="s")  # type: ignore[arg-type]
    with pytest.raises(PipelineHandlerError, match="inputs must be a mapping"):
        StageContext(pipeline_id="p", version="1.0.0", unit_id="u", stage=stage, inputs=[])  # type: ignore[arg-type]
    with pytest.raises(PipelineHandlerError, match="attempt must be non-negative"):
        StageContext(pipeline_id="p", version="1.0.0", unit_id="u", stage=stage, attempt=-1)


def test_stage_outcome_validates_its_own_shape() -> None:
    assert STAGE_OUTCOME_STATUSES == ("FAIL", "PASS", "SKIP")
    assert not StageOutcome(stage_id="s", status="SKIP").passed
    with pytest.raises(PipelineHandlerError, match="stage id is required"):
        StageOutcome(stage_id="", status=CONTINUE_STATUS)
    with pytest.raises(PipelineHandlerError, match="unknown stage outcome status"):
        StageOutcome(stage_id="s", status="MAYBE")
    with pytest.raises(PipelineHandlerError, match="findings must be a tuple"):
        StageOutcome(stage_id="s", status=CONTINUE_STATUS, findings=["x"])  # type: ignore[arg-type]
    with pytest.raises(PipelineHandlerError, match="non-empty strings"):
        StageOutcome(stage_id="s", status=CONTINUE_STATUS, findings=("",))
    with pytest.raises(PipelineHandlerError, match="outputs must be a mapping"):
        StageOutcome(stage_id="s", status=CONTINUE_STATUS, outputs=[])  # type: ignore[arg-type]
    with pytest.raises(PipelineHandlerError, match="must state at least one finding"):
        StageOutcome(stage_id="s", status="FAIL")


# ---------------------------------------------------------------------------- governance


def _definition(**overrides: object) -> PipelineDefinition:
    base: dict[str, object] = {
        "pipeline_id": "test.pipeline",
        "pipeline_type": "governance",
        "version": "1.0.0",
        "stages": (StageDefinition(stage_id="only", handler=RECORD_HANDLER),),
    }
    base.update(overrides)
    return PipelineDefinition(**base)  # type: ignore[arg-type]


def test_governance_holds_no_authority_of_its_own() -> None:
    assert GOVERNANCE_AUTHORITY == "NONE (DERIVED TRUTH)"
    assert PipelineGovernance().to_dict()["authority"] == GOVERNANCE_AUTHORITY


def test_repository_wide_and_declared_policies_compose_as_a_union() -> None:
    governance = PipelineGovernance()
    governance.register_policy(PipelinePolicy("P.global", "obligation.global"))
    definition = _definition(policies=(PipelinePolicy("P.local", "obligation.local"),))
    binding = governance.binding_policies(definition=definition)
    assert [p.policy_id for p in binding] == ["P.global", "P.local"]
    refused = governance.evaluate("subject", definition=definition)
    assert not refused.approved
    assert refused.undischarged == ("obligation.global", "obligation.local")
    approved = governance.evaluate(
        "subject",
        definition=definition,
        evidence=obligations_from(["obligation.global", "obligation.local"]),
    )
    assert approved.approved
    governance.require_approved(approved)


def test_a_declared_policy_cannot_shed_a_repository_wide_obligation() -> None:
    governance = PipelineGovernance()
    governance.register_policy(PipelinePolicy("P.same", "obligation.strict"))
    # A pipeline declaring the same policy id with a laxer obligation must not win.
    definition = _definition(policies=(PipelinePolicy("P.same", "obligation.lax", blocking=False),))
    binding = governance.binding_policies(definition=definition)
    assert [p.obligation for p in binding] == ["obligation.strict"]


def test_an_advisory_policy_records_a_finding_without_refusing() -> None:
    governance = PipelineGovernance()
    governance.register_policy(PipelinePolicy("P.advice", "obligation.advice", blocking=False))
    verdict = governance.evaluate("subject")
    assert verdict.approved
    assert any("advisory" in finding for finding in verdict.findings)


def test_stage_scoped_policies_bind_only_their_stage() -> None:
    governance = PipelineGovernance()
    governance.register_policy(
        PipelinePolicy("P.scoped", "obligation.scoped", applies_to=("only",))
    )
    assert governance.binding_policies(stage_id="only")
    assert governance.binding_policies(stage_id="other") == ()


def test_declared_governance_obligations_are_evaluated_not_decorative() -> None:
    governance = PipelineGovernance()
    definition = _definition(
        governance=PipelineGovernanceSpec(obligations=("repository.truth.synchronized",))
    )
    verdict = governance.evaluate("subject", definition=definition)
    assert verdict.undischarged == ("repository.truth.synchronized",)
    with pytest.raises(PipelineGovernanceError, match="governance refused"):
        governance.require_approved(verdict)


def test_governance_records_verdicts_and_recovery_points_as_an_audit_trail() -> None:
    bus = PipelineEventBus()
    governance = PipelineGovernance(bus=bus)
    governance.evaluate("subject")
    point = governance.record_recovery_point("subject", "CERTIFIED", detail={"k": "v"})
    assert point.ordinal == 0
    assert point.identity.kind == "recovery-point"
    assert governance.latest_recovery_point("subject") == point
    assert len(governance.verdicts) == 1
    assert len(governance.verdicts_for("subject")) == 1
    trail = governance.audit_trail("subject")
    assert {entry["kind"] for entry in trail} == {"verdict", "recovery-point"}
    assert governance.audit_trail() == trail
    assert len(bus.events_of("uapf.policy.evaluated")) == 1
    assert len(bus.events_of("uapf.recovery.recorded")) == 1
    assert governance.fingerprint() == governance.fingerprint()


def test_governance_fails_closed_on_bad_inputs() -> None:
    governance = PipelineGovernance()
    with pytest.raises(PipelineGovernanceError, match="only a PipelinePolicy"):
        governance.register_policy("P")  # type: ignore[arg-type]
    governance.register_policy(PipelinePolicy("P.dup", "o"))
    with pytest.raises(PipelineGovernanceError, match="policy already registered"):
        governance.register_policy(PipelinePolicy("P.dup", "o2"))
    with pytest.raises(PipelineGovernanceError, match="subject is required"):
        governance.evaluate("")
    with pytest.raises(PipelineGovernanceError, match="evidence must be a mapping"):
        governance.evaluate("s", evidence=["o"])  # type: ignore[arg-type]
    with pytest.raises(PipelineGovernanceError, match="must be a PipelineDefinition"):
        governance.binding_policies(definition="d")  # type: ignore[arg-type]
    with pytest.raises(PipelineGovernanceError, match="a GovernanceVerdict is required"):
        governance.require_approved("verdict")  # type: ignore[arg-type]
    with pytest.raises(PipelineGovernanceError, match="no recovery point recorded"):
        governance.latest_recovery_point("never")
    with pytest.raises(PipelineGovernanceError, match="subject is required"):
        governance.record_recovery_point("", "READY")
    with pytest.raises(PipelineStateError, match="unknown execution-unit state"):
        governance.record_recovery_point("s", "INVENTED")
    with pytest.raises(PipelineGovernanceError, match="must be a PipelineEventBus"):
        PipelineGovernance(bus="x")  # type: ignore[arg-type]


def test_a_verdict_cannot_lie_about_itself() -> None:
    with pytest.raises(PipelineGovernanceError, match="subject is required"):
        GovernanceVerdict(subject="", approved=True)
    with pytest.raises(PipelineGovernanceError, match="approval must be a bool"):
        GovernanceVerdict(subject="s", approved="yes")  # type: ignore[arg-type]
    with pytest.raises(PipelineGovernanceError, match="must be a tuple"):
        GovernanceVerdict(subject="s", approved=True, considered=["o"])  # type: ignore[arg-type]
    with pytest.raises(PipelineGovernanceError, match="cannot carry an undischarged"):
        GovernanceVerdict(subject="s", approved=True, undischarged=("o",))
    with pytest.raises(PipelineGovernanceError, match="must state why it refused"):
        GovernanceVerdict(subject="s", approved=False)


def test_recovery_point_validates_its_own_shape() -> None:
    with pytest.raises(PipelineGovernanceError, match="checkpoint is required"):
        RecoveryPoint(subject="s", state="READY", checkpoint="", ordinal=0)
    with pytest.raises(PipelineGovernanceError, match="ordinal must be non-negative"):
        RecoveryPoint(subject="s", state="READY", checkpoint="c", ordinal=-1)
    with pytest.raises(PipelineGovernanceError, match="detail must be a mapping"):
        RecoveryPoint(subject="s", state="READY", checkpoint="c", ordinal=0, detail=[])  # type: ignore[arg-type]


# ----------------------------------------------------------------------------- assurance


def test_the_three_acts_must_happen_in_the_constitutional_order() -> None:
    assert ASSURANCE_ACTS == ("validation", "verification", "certification")
    assurance = PipelineAssurance()
    # Certification before anything: refused, naming the missing verification.
    with pytest.raises(PipelineCertificationError, match="no verification record"):
        assurance.certify("u1")
    with pytest.raises(PipelineValidationError, match="no validation record"):
        assurance.verify("u1")
    validated = assurance.validate("u1", evidence={"rules": 12})
    verified = assurance.verify("u1", evidence={"independent": True})
    certified = assurance.certify("u1", evidence={"criteria": "declared"})
    # Each act is bound to the one it rests on, so a record cannot float free.
    assert verified.validated_hash == validated.evidence_hash()
    assert certified.verified_hash == verified.evidence_hash()
    assert assurance.is_validated("u1")
    assert assurance.is_verified("u1")
    assert assurance.is_certified("u1")
    assert [r["act"] for r in assurance.records_for("u1")] == list(ASSURANCE_ACTS)
    assert assurance.subjects() == ("u1",)


def test_a_failing_verdict_is_a_result_but_blocks_the_next_act() -> None:
    assurance = PipelineAssurance()
    failed = assurance.validate("u1", passed=False, findings=("rule R1 failed",))
    assert not failed.passed
    assert assurance.latest_validation("u1") == failed
    assert not assurance.is_validated("u1")
    with pytest.raises(PipelineValidationError, match="requires a passed validation"):
        assurance.verify("u1")
    # A later passing validation unblocks it — forward-only correction.
    assurance.validate("u1", evidence={"fixed": True})
    verified_failure = assurance.verify("u1", passed=False, findings=("not sound",))
    assert not verified_failure.passed
    with pytest.raises(PipelineCertificationError, match="requires a passed verification"):
        assurance.certify("u1")


def test_records_are_content_addressed_and_deterministic() -> None:
    def build() -> PipelineAssurance:
        assurance = PipelineAssurance()
        assurance.validate("u1", evidence={"rules": 3})
        assurance.verify("u1", evidence={"independent": True})
        assurance.certify("u1", evidence={"criteria": "all"})
        return assurance

    left, right = build(), build()
    assert left.fingerprint() == right.fingerprint()
    rendered = left.to_dict()
    assert rendered["validation_count"] == 1
    assert rendered["certified_subjects"] == ["u1"]
    assert left.validations[0].identity.kind == "validation-record"
    assert left.verifications[0].identity.kind == "verification-record"
    assert left.certifications[0].identity.kind == "certification-record"


def test_assurance_records_every_act_on_the_bus() -> None:
    bus = PipelineEventBus()
    assurance = PipelineAssurance(bus=bus)
    assurance.validate("u1")
    assurance.verify("u1")
    assurance.certify("u1")
    for category in ("uapf.unit.validated", "uapf.unit.verified", "uapf.unit.certified"):
        assert len(bus.events_of(category)) == 1
    with pytest.raises(PipelineValidationError, match="must be a PipelineEventBus"):
        PipelineAssurance(bus="x")  # type: ignore[arg-type]


def test_assurance_records_validate_their_own_shape() -> None:
    with pytest.raises(PipelineValidationError, match="subject is required"):
        ValidationRecord(subject="", passed=True)
    with pytest.raises(PipelineValidationError, match="verdict must be a bool"):
        ValidationRecord(subject="s", passed="yes")  # type: ignore[arg-type]
    with pytest.raises(PipelineValidationError, match="findings must be a tuple"):
        ValidationRecord(subject="s", passed=True, findings=["f"])  # type: ignore[arg-type]
    with pytest.raises(PipelineValidationError, match="non-empty strings"):
        ValidationRecord(subject="s", passed=True, findings=("",))
    with pytest.raises(PipelineValidationError, match="evidence must be a mapping"):
        ValidationRecord(subject="s", passed=True, evidence=[])  # type: ignore[arg-type]
    with pytest.raises(PipelineValidationError, match="ordinal must be non-negative"):
        ValidationRecord(subject="s", passed=True, ordinal=-1)
    with pytest.raises(PipelineValidationError, match="must state at least one finding"):
        ValidationRecord(subject="s", passed=False)
    with pytest.raises(PipelineValidationError, match="must name the validation"):
        VerificationRecord(subject="s", passed=True)
    with pytest.raises(PipelineCertificationError, match="must name the verification"):
        CertificationRecord(subject="s", passed=True)
    assert VerificationRecord(subject="s", passed=True, validated_hash="h").act == "verification"
    assert CertificationRecord(subject="s", passed=True, verified_hash="h").act == "certification"


def test_lookup_of_an_absent_certification_fails_closed() -> None:
    assurance = PipelineAssurance()
    with pytest.raises(PipelineCertificationError, match="no certification record"):
        assurance.latest_certification("never")


# ------------------------------------------------------------------------- observability


def test_health_is_derived_from_recorded_outcomes() -> None:
    observability = PipelineObservability()
    assert observability.health()["status"] == HEALTHY
    observability.observe_outcome("s1", True)
    assert observability.health()["status"] == HEALTHY
    observability.observe_outcome("s2", False)
    health = observability.health()
    assert health["status"] == DEGRADED
    assert health["failures"] == 1.0
    assert health["successes"] == 1.0
    assert health["observed"] == 2.0
    assert observability.total(SUCCESS_METRIC) == 1.0
    assert observability.total(FAILURE_METRIC) == 1.0
    assert observability.total("never.recorded") == 0.0


def test_spans_are_measured_in_steps_not_seconds() -> None:
    observability = PipelineObservability()
    span = observability.record_span("uapf.execution.stages", 4, unit_id="u1")
    assert span.kind == "span"
    assert span.value == 4.0
    assert span.labels["unit_id"] == "u1"
    with pytest.raises(PipelineObservabilityError, match="non-negative integer"):
        observability.record_span("x", -1)
    with pytest.raises(PipelineObservabilityError, match="non-negative integer"):
        observability.record_span("x", True)  # type: ignore[arg-type]


def test_bottlenecks_rank_by_recorded_magnitude() -> None:
    observability = PipelineObservability()
    observability.record("small", 1.0)
    observability.record("large", 10.0)
    observability.record("medium", 5.0)
    assert observability.bottlenecks() == (("large", 10.0), ("medium", 5.0), ("small", 1.0))
    assert observability.bottlenecks(limit=1) == (("large", 10.0),)
    assert observability.names() == ("large", "medium", "small")
    assert observability.totals()["large"] == 10.0
    assert len(observability.metrics_named("large")) == 1
    assert len(observability) == 3
    with pytest.raises(PipelineObservabilityError, match="limit must be a positive integer"):
        observability.bottlenecks(limit=0)


def test_telemetry_is_deterministic_and_validated() -> None:
    def build() -> PipelineObservability:
        observability = PipelineObservability()
        observability.record("counted", 2.0, labels={"stage_id": "s"})
        return observability

    assert build().fingerprint() == build().fingerprint()
    assert TELEMETRY_KINDS == ("counter", "gauge", "span")
    assert build().to_dict()["metric_count"] == 1
    assert PipelineTelemetry(name="n", value=1).identity.kind == "telemetry"
    with pytest.raises(PipelineObservabilityError, match="name is required"):
        PipelineTelemetry(name="", value=1)
    with pytest.raises(PipelineObservabilityError, match="must be numeric"):
        PipelineTelemetry(name="n", value="1")  # type: ignore[arg-type]
    with pytest.raises(PipelineObservabilityError, match="must be numeric"):
        PipelineTelemetry(name="n", value=True)  # type: ignore[arg-type]
    with pytest.raises(PipelineObservabilityError, match="unknown telemetry kind"):
        PipelineTelemetry(name="n", value=1, kind="histogram")
    with pytest.raises(PipelineObservabilityError, match="labels must be a mapping"):
        PipelineTelemetry(name="n", value=1, labels=[])  # type: ignore[arg-type]
    with pytest.raises(PipelineObservabilityError, match="string to string"):
        PipelineTelemetry(name="n", value=1, labels={"k": 1})  # type: ignore[dict-item]
    with pytest.raises(PipelineObservabilityError, match="ordinal must be non-negative"):
        PipelineTelemetry(name="n", value=1, ordinal=-1)
    with pytest.raises(PipelineObservabilityError, match="must be a PipelineObservability|bus"):
        PipelineObservability(bus="x")  # type: ignore[arg-type]


def test_observability_records_telemetry_on_the_bus() -> None:
    bus = PipelineEventBus()
    PipelineObservability(bus=bus).record("counted", 1.0)
    assert len(bus.events_of("uapf.telemetry.recorded")) == 1


def test_every_assurance_lookup_returns_the_most_recent_record_for_its_subject() -> None:
    """THREE LOOKUPS, THREE ACTS, and only the certification refusal had a test.

    Each walks its own ledger in reverse so the most recent record wins — an act performed
    twice must resolve to the second one, or a re-validated unit would keep answering with
    the evidence of the run that failed. Only the refusals were exercised, which leaves three
    lookups that could return the WRONG record while still terminating, and every consumer
    reading evidence from them would read it from another subject or another attempt.
    """
    assurance = PipelineAssurance()

    assurance.validate("unit", evidence={"attempt": 1})
    assurance.validate("unit", evidence={"attempt": 2})
    assurance.validate("other", evidence={"attempt": 1})
    assert assurance.latest_validation("unit").evidence["attempt"] == 2
    assert assurance.latest_validation("other").evidence["attempt"] == 1

    assurance.verify("unit", evidence={"attempt": 1})
    assurance.verify("unit", evidence={"attempt": 2})
    assert assurance.latest_verification("unit").evidence["attempt"] == 2

    assurance.certify("unit", evidence={"attempt": 1})
    assurance.certify("unit", evidence={"attempt": 2})
    assert assurance.latest_certification("unit").evidence["attempt"] == 2

    with pytest.raises(PipelineValidationError):
        assurance.latest_validation("never")
    with pytest.raises(PipelineCertificationError):
        assurance.latest_verification("never")


def test_a_certification_lookup_walks_past_records_belonging_to_another_subject() -> None:
    """ONE LEDGER, MANY SUBJECTS — and the reverse walk has to step over the others.

    Every existing case certifies one subject, or certifies the subject under test LAST, so
    the reverse walk matched on its first step and the loop's continue arm never ran. That
    arm is the difference between "the most recent certification of this subject" and "the
    most recent certification", and collapsing the two would hand a caller another unit's
    evidence — under a lookup whose whole contract is that it is subject-scoped.
    """
    assurance = PipelineAssurance()

    for subject, attempt in (("wanted", 1), ("noise-a", 2), ("noise-b", 3)):
        assurance.validate(subject, evidence={"attempt": attempt})
        assurance.verify(subject, evidence={"attempt": attempt})
        assurance.certify(subject, evidence={"attempt": attempt})

    found = assurance.latest_certification("wanted")

    assert found.subject == "wanted"
    assert found.evidence["attempt"] == 1


def test_recorded_measurements_are_readable_in_record_order() -> None:
    """A METER THAT CANNOT BE READ IS NOT A METER.

    ``health``, ``total`` and ``names`` are DERIVATIONS over the recorded measurements, and
    each was tested; the raw sequence they derive from had no reader. It is the evidence
    view — the one an operator or an evidence bundle uses to see what was actually recorded
    rather than what was concluded from it — and record order is part of what it reports,
    because two measurements of the same metric are only interpretable in the order taken.
    """
    observability = PipelineObservability()
    observability.observe_outcome("s1", True)
    span = observability.record_span("uapf.execution.stages", 3)

    metrics = observability.metrics

    assert isinstance(metrics, tuple)
    assert len(metrics) == len(observability) == 2
    assert metrics[0].name == SUCCESS_METRIC
    assert metrics[1] is span
