"""UAPF-000001 — tests for the declaration surface and the derived plan.

The claim under test is the one the whole framework rests on: a pipeline is *declared as data*
and its order is *derived*. So these tests check two things above all — that a malformed
declaration cannot exist as an object (validation is total and at construction, which is why no
consumer downstream re-checks it), and that the derived plan is a function of the declared
``requires`` edges and of nothing else, including declaration order.
"""

from __future__ import annotations

from platform.foundation.contracts import ContractRef
from platform.universal_pipeline.contracts import (
    CAPABILITY_DIRECTIONS,
    DEFAULT_PIPELINE_STRATEGY,
    SEED_PIPELINE_TYPES,
    PipelineCapability,
    PipelineDefinition,
    PipelineGateSpec,
    PipelineGovernanceSpec,
    PipelinePlan,
    PipelinePlugin,
    PipelinePolicy,
    PipelineSecuritySpec,
    StageDefinition,
    pipeline_type_description,
    pipeline_types,
    register_pipeline_type,
    require_pipeline_type,
)
from platform.universal_pipeline.errors import (
    PipelineDefinitionError,
    PipelinePlanError,
    PipelineTypeError,
)

import pytest


def _stage(stage_id: str, *requires: str, **kwargs: object) -> StageDefinition:
    return StageDefinition(
        stage_id=stage_id, handler="uapf.record", requires=tuple(requires), **kwargs
    )


def _definition(**overrides: object) -> PipelineDefinition:
    base: dict[str, object] = {
        "pipeline_id": "test.pipeline",
        "pipeline_type": "evolution",
        "version": "1.0.0",
        "stages": (_stage("first"), _stage("second", "first")),
    }
    base.update(overrides)
    return PipelineDefinition(**base)  # type: ignore[arg-type]


# ----------------------------------------------------------------- the type vocabulary


def test_every_mission_pipeline_type_is_seeded() -> None:
    registered = set(pipeline_types())
    for pipeline_type, description in SEED_PIPELINE_TYPES:
        assert pipeline_type in registered
        assert pipeline_type_description(pipeline_type) == description
    assert len(SEED_PIPELINE_TYPES) == 21


def test_pipeline_types_are_open_by_registration_and_append_only() -> None:
    register_pipeline_type("test-open-world-type", "admitted by a test, no code change")
    require_pipeline_type("test-open-world-type")
    assert "test-open-world-type" in pipeline_types()
    with pytest.raises(PipelineTypeError, match="already registered"):
        register_pipeline_type("test-open-world-type")


def test_an_unregistered_pipeline_type_fails_closed() -> None:
    with pytest.raises(PipelineTypeError, match="unregistered term"):
        require_pipeline_type("no-such-pipeline-type")
    with pytest.raises(PipelineTypeError):
        _definition(pipeline_type="no-such-pipeline-type")


# ------------------------------------------------------------------ component declarations


def test_gate_spec_declares_an_obligation_and_a_blocking_posture() -> None:
    blocking = PipelineGateSpec("G1", "evidence.present", description="d")
    advisory = PipelineGateSpec("G2", "metric.measured", blocking=False)
    assert blocking.blocking and not advisory.blocking
    assert blocking.identity.kind == "gate"
    assert blocking.to_dict()["obligation"] == "evidence.present"
    assert PipelineGateSpec.from_dict(blocking.to_dict()) == blocking
    with pytest.raises(PipelineDefinitionError, match="gate id is required"):
        PipelineGateSpec("", "x")
    with pytest.raises(PipelineDefinitionError, match="gate obligation is required"):
        PipelineGateSpec("G", "")
    with pytest.raises(PipelineDefinitionError, match="blocking must be a bool"):
        PipelineGateSpec("G", "o", blocking="yes")  # type: ignore[arg-type]
    with pytest.raises(PipelineDefinitionError, match="must be a mapping"):
        PipelineGateSpec.from_dict("nope")  # type: ignore[arg-type]


def test_policy_scope_binds_everything_when_it_names_nothing() -> None:
    everywhere = PipelinePolicy("P.all", "obligation.all")
    somewhere = PipelinePolicy("P.some", "obligation.some", applies_to=("first",))
    assert everywhere.binds("anything") and everywhere.binds("first")
    assert somewhere.binds("first") and not somewhere.binds("second")
    assert PipelinePolicy.from_dict(somewhere.to_dict()) == somewhere
    assert somewhere.identity.kind == "policy"
    with pytest.raises(PipelineDefinitionError, match="policy id is required"):
        PipelinePolicy("", "o")
    with pytest.raises(PipelineDefinitionError, match="applies_to must be a tuple"):
        PipelinePolicy("P", "o", applies_to=["first"])  # type: ignore[arg-type]
    with pytest.raises(PipelineDefinitionError, match="policy target is required"):
        PipelinePolicy("P", "o", applies_to=("",))
    with pytest.raises(PipelineDefinitionError, match="must be a mapping"):
        PipelinePolicy.from_dict(7)  # type: ignore[arg-type]


def test_capability_declares_a_direction_and_a_contract_reference() -> None:
    provided = PipelineCapability("cap.x", ContractRef("contract.x"), "provides")
    assert CAPABILITY_DIRECTIONS == ("provides", "requires")
    assert provided.identity.kind == "capability"
    assert PipelineCapability.from_dict(provided.to_dict()) == provided
    with pytest.raises(PipelineDefinitionError, match="capability id is required"):
        PipelineCapability("", ContractRef("c"))
    with pytest.raises(PipelineDefinitionError, match="must be a ContractRef"):
        PipelineCapability("cap", "contract.x")  # type: ignore[arg-type]
    with pytest.raises(PipelineDefinitionError, match="direction must be"):
        PipelineCapability("cap", ContractRef("c"), "consumes")
    with pytest.raises(PipelineDefinitionError, match="must be a mapping"):
        PipelineCapability.from_dict([])  # type: ignore[arg-type]
    with pytest.raises(PipelineDefinitionError, match="contract must be a mapping"):
        PipelineCapability.from_dict({"capability_id": "c", "contract": "x"})


def test_plugin_binds_a_handler_to_an_extension_point() -> None:
    plugin = PipelinePlugin("PL.1", "after-stage", "uapf.record")
    assert plugin.identity.kind == "plugin"
    assert PipelinePlugin.from_dict(plugin.to_dict()) == plugin
    with pytest.raises(PipelineDefinitionError, match="plugin id is required"):
        PipelinePlugin("", "point", "handler")
    with pytest.raises(PipelineDefinitionError, match="extension point is required"):
        PipelinePlugin("PL", "", "handler")
    with pytest.raises(PipelineDefinitionError, match="plugin handler is required"):
        PipelinePlugin("PL", "point", "")
    with pytest.raises(PipelineDefinitionError, match="must be a mapping"):
        PipelinePlugin.from_dict(None)  # type: ignore[arg-type]


def test_security_and_governance_specs_round_trip_and_validate() -> None:
    security = PipelineSecuritySpec(required_permissions=("execute",), classification="internal")
    governance = PipelineGovernanceSpec(obligations=("truth.synchronized",))
    assert PipelineSecuritySpec.from_dict(security.to_dict()) == security
    assert PipelineGovernanceSpec.from_dict(governance.to_dict()) == governance
    assert PipelineGovernanceSpec().authority == "NONE (DERIVED TRUTH)"
    with pytest.raises(PipelineDefinitionError, match="required_permissions must be a tuple"):
        PipelineSecuritySpec(required_permissions=["execute"])  # type: ignore[arg-type]
    with pytest.raises(PipelineDefinitionError, match="required permission is required"):
        PipelineSecuritySpec(required_permissions=("",))
    with pytest.raises(PipelineDefinitionError, match="classification is required"):
        PipelineSecuritySpec(classification="")
    with pytest.raises(PipelineDefinitionError, match="authority is required"):
        PipelineGovernanceSpec(authority="")
    with pytest.raises(PipelineDefinitionError, match="obligations must be a tuple"):
        PipelineGovernanceSpec(obligations=["x"])  # type: ignore[arg-type]
    with pytest.raises(PipelineDefinitionError, match="governance obligation is required"):
        PipelineGovernanceSpec(obligations=("",))
    with pytest.raises(PipelineDefinitionError, match="must be a mapping"):
        PipelineSecuritySpec.from_dict("x")  # type: ignore[arg-type]
    with pytest.raises(PipelineDefinitionError, match="must be a mapping"):
        PipelineGovernanceSpec.from_dict("x")  # type: ignore[arg-type]


def test_stage_declares_requirements_but_never_its_own_position() -> None:
    stage = StageDefinition(
        stage_id="s",
        handler="uapf.gate",
        requires=("a", "b"),
        gates=(PipelineGateSpec("G1", "o1"), PipelineGateSpec("G2", "o2", blocking=False)),
        optional=True,
    )
    assert stage.identity.kind == "stage"
    assert [gate.gate_id for gate in stage.blocking_gates] == ["G1"]
    assert StageDefinition.from_dict(stage.to_dict()) == stage
    with pytest.raises(PipelineDefinitionError, match="stage id is required"):
        StageDefinition(stage_id="", handler="h")
    with pytest.raises(PipelineDefinitionError, match="stage handler is required"):
        StageDefinition(stage_id="s", handler="")
    with pytest.raises(PipelineDefinitionError, match="cannot require itself"):
        _stage("s", "s")
    with pytest.raises(PipelineDefinitionError, match="duplicate stage requirement"):
        _stage("s", "a", "a")
    with pytest.raises(PipelineDefinitionError, match="requires must be a tuple"):
        StageDefinition(stage_id="s", handler="h", requires=["a"])  # type: ignore[arg-type]
    with pytest.raises(PipelineDefinitionError, match="gates must be a tuple"):
        StageDefinition(stage_id="s", handler="h", gates=[])  # type: ignore[arg-type]
    with pytest.raises(PipelineDefinitionError, match="duplicate gate id"):
        StageDefinition(
            stage_id="s",
            handler="h",
            gates=(PipelineGateSpec("G", "a"), PipelineGateSpec("G", "b")),
        )
    with pytest.raises(PipelineDefinitionError, match="policies must be a tuple"):
        StageDefinition(stage_id="s", handler="h", policies=["p"])  # type: ignore[arg-type]
    with pytest.raises(PipelineDefinitionError, match="must be a mapping"):
        StageDefinition.from_dict(1)  # type: ignore[arg-type]


# ------------------------------------------------------------------- pipeline declaration


def test_definition_exposes_derived_views_over_its_declarations() -> None:
    definition = _definition(
        capabilities=(
            PipelineCapability("cap.p", ContractRef("c.p"), "provides"),
            PipelineCapability("cap.r", ContractRef("c.r"), "requires"),
        ),
        policies=(PipelinePolicy("P.1", "o.1", applies_to=("first",)),),
        stages=(_stage("first", policies=("P.1",)), _stage("second", "first")),
    )
    assert definition.stage_ids == ("first", "second")
    assert definition.stage("second").requires == ("first",)
    assert definition.graph() == {"first": (), "second": ("first",)}
    assert [p.policy_id for p in definition.policies_for("first")] == ["P.1"]
    assert definition.policies_for("second") == ()
    assert [c.capability_id for c in definition.capabilities_by("provides")] == ["cap.p"]
    assert [c.capability_id for c in definition.capabilities_by("requires")] == ["cap.r"]
    assert definition.identity.kind == "pipeline"
    assert definition.strategy == DEFAULT_PIPELINE_STRATEGY
    assert (
        definition.fingerprint()
        == _definition(
            capabilities=definition.capabilities,
            policies=definition.policies,
            stages=definition.stages,
        ).fingerprint()
    )
    with pytest.raises(PipelineDefinitionError, match="no such stage"):
        definition.stage("absent")
    with pytest.raises(PipelineDefinitionError, match="unknown capability direction"):
        definition.capabilities_by("sideways")


@pytest.mark.parametrize(
    ("overrides", "match"),
    [
        ({"pipeline_id": ""}, "pipeline id is required"),
        ({"version": "one"}, "semantic version"),
        ({"stages": ()}, "at least one stage"),
        ({"stages": [_stage("a")]}, "at least one stage"),
        ({"stages": (_stage("a"), _stage("a"))}, "duplicate stage id"),
        ({"stages": (_stage("a", "ghost"),)}, "undeclared stage"),
        ({"strategy": ""}, "pipeline strategy is required"),
    ],
)
def test_a_malformed_declaration_cannot_exist(overrides: dict[str, object], match: str) -> None:
    with pytest.raises(PipelineDefinitionError, match=match):
        _definition(**overrides)


def test_duplicate_and_dangling_declarations_are_refused() -> None:
    with pytest.raises(PipelineDefinitionError, match="duplicate policy id"):
        _definition(policies=(PipelinePolicy("P", "a"), PipelinePolicy("P", "b")))
    with pytest.raises(PipelineDefinitionError, match="duplicate plugin id"):
        _definition(
            plugins=(PipelinePlugin("PL", "p1", "h"), PipelinePlugin("PL", "p2", "h")),
        )
    with pytest.raises(PipelineDefinitionError, match="duplicate capability declaration"):
        _definition(
            capabilities=(
                PipelineCapability("cap", ContractRef("c"), "provides"),
                PipelineCapability("cap", ContractRef("c"), "provides"),
            )
        )
    with pytest.raises(PipelineDefinitionError, match="undeclared policy"):
        _definition(stages=(_stage("first", policies=("P.absent",)),))


def test_the_same_capability_may_be_provided_and_required() -> None:
    """Direction is part of the uniqueness key, so a self-satisfying pipeline is declarable."""
    definition = _definition(
        capabilities=(
            PipelineCapability("cap", ContractRef("c"), "provides"),
            PipelineCapability("cap", ContractRef("c"), "requires"),
        )
    )
    assert len(definition.capabilities) == 2


def test_definition_round_trips_through_its_serialized_form() -> None:
    definition = _definition(
        capabilities=(PipelineCapability("cap.p", ContractRef("c.p"), "provides"),),
        policies=(PipelinePolicy("P.1", "o.1"),),
        plugins=(PipelinePlugin("PL.1", "point", "uapf.record"),),
        governance=PipelineGovernanceSpec(obligations=("o",)),
        security=PipelineSecuritySpec(required_permissions=("execute",)),
        description="d",
    )
    assert PipelineDefinition.from_dict(definition.to_dict()) == definition
    # Governance and security are optional in a declaration and default when omitted.
    minimal = PipelineDefinition.from_dict(
        {
            "pipeline_id": "p",
            "pipeline_type": "evolution",
            "version": "1.0.0",
            "stages": [{"stage_id": "s", "handler": "uapf.record"}],
        }
    )
    assert minimal.governance == PipelineGovernanceSpec()
    assert minimal.security == PipelineSecuritySpec()
    with pytest.raises(PipelineDefinitionError, match="must be a mapping"):
        PipelineDefinition.from_dict([])  # type: ignore[arg-type]


# ------------------------------------------------------------------------- derived plan


def test_plan_is_derived_from_declared_edges_not_declaration_order() -> None:
    forward = _definition(stages=(_stage("a"), _stage("b", "a"), _stage("c", "b")))
    shuffled = _definition(stages=(_stage("c", "b"), _stage("a"), _stage("b", "a")))
    assert PipelinePlan.derive(forward).waves == PipelinePlan.derive(shuffled).waves
    assert PipelinePlan.derive(forward).stage_ids == ("a", "b", "c")


def test_plan_expresses_the_concurrency_the_declarations_permit() -> None:
    plan = PipelinePlan.derive(
        _definition(stages=(_stage("root"), _stage("l", "root"), _stage("r", "root")))
    )
    assert plan.wave_count == 2
    assert plan.max_parallelism == 2
    assert plan.stages_in_wave(0) == ("root",)
    assert plan.stages_in_wave(1) == ("l", "r")
    assert plan.wave_indices == (0, 1)
    assert plan.identity.kind == "plan"
    assert plan.to_dict()["max_parallelism"] == 2


def test_a_strict_sequence_is_available_through_the_shared_strategy_registry() -> None:
    definition = _definition(stages=(_stage("root"), _stage("l", "root"), _stage("r", "root")))
    sequential = PipelinePlan.derive(definition, strategy="dependency-order")
    assert sequential.strategy == "dependency-order"
    assert sequential.wave_count == 3
    assert sequential.max_parallelism == 1
    # The strategy is recorded, so two plans over one declaration are distinguishable.
    assert sequential.fingerprint() != PipelinePlan.derive(definition).fingerprint()


def test_plan_derivation_fails_closed_on_a_cycle_and_an_unknown_strategy() -> None:
    # A cycle cannot be built through PipelineDefinition (closure honesty rejects it first),
    # so the cycle path is reached with mutually-requiring declared stages.
    cyclic = _definition(stages=(_stage("a", "b"), _stage("b", "a")))
    with pytest.raises(PipelinePlanError, match="contains a cycle") as raised:
        PipelinePlan.derive(cyclic)
    assert raised.value.context["unresolved"] == ["a", "b"]
    with pytest.raises(PipelinePlanError, match="unregistered ordering strategy"):
        PipelinePlan.derive(_definition(), strategy="no-such-strategy")
    with pytest.raises(PipelinePlanError, match="derived from a PipelineDefinition"):
        PipelinePlan.derive("not a definition")  # type: ignore[arg-type]


def test_plan_validates_its_own_shape() -> None:
    """FOUR FIELDS, FOUR REFUSALS — and the version's was the one never taken.

    A plan carries the version it was derived FOR, and ``derive`` always supplies the
    definition's own, so the check only ever answers about a plan built by hand or
    rehydrated. An unversioned plan is the dangerous one: it names a pipeline, orders its
    stages and says nothing about which version of that pipeline it orders, so it would be
    executed against whatever version happened to be resolved.
    """
    with pytest.raises(PipelinePlanError, match="plan pipeline id is required"):
        PipelinePlan(pipeline_id="", version="1.0.0", strategy="s", waves=((0, "a"),))
    with pytest.raises(PipelinePlanError, match="plan version is required") as raised:
        PipelinePlan(pipeline_id="p", version="", strategy="s", waves=((0, "a"),))
    assert raised.value.context["pipeline_id"] == "p"
    with pytest.raises(PipelinePlanError, match="plan strategy is required"):
        PipelinePlan(pipeline_id="p", version="1.0.0", strategy="", waves=((0, "a"),))
    with pytest.raises(PipelinePlanError, match="at least one stage"):
        PipelinePlan(pipeline_id="p", version="1.0.0", strategy="s", waves=())
    with pytest.raises(PipelinePlanError, match="at least one stage"):
        PipelinePlan(pipeline_id="p", version="1.0.0", strategy="s", waves=[(0, "a")])  # type: ignore[arg-type]


def test_an_unpopulated_wave_is_empty_rather_than_an_error() -> None:
    """Asking for a wave that holds nothing is a legitimate query, not a fault."""
    plan = PipelinePlan.derive(_definition())
    assert plan.stages_in_wave(99) == ()
