"""Dynamic Capability Composition: derived from declarations, never a fixed pipeline."""

from __future__ import annotations

import pytest

from engine.civilization.composition import (
    DEFAULT_STRATEGY,
    CompositionPlanner,
    dependency_order,
    get_strategy,
    parallel_waves,
    register_strategy,
    strategy_names,
)
from engine.civilization.errors import (
    CapabilityUnknownError,
    CompositionCycleError,
    CompositionStrategyError,
    CompositionUnsatisfiedError,
)
from engine.civilization.metatypes import REQUIRES
from engine.kernel.kernel import MetaKernel


def _chain() -> CompositionPlanner:
    planner = CompositionPlanner()
    planner.register_capability("store")
    planner.register_capability("index", requires=("store",))
    planner.register_capability("search", requires=("index",))
    return planner


def test_a_plan_is_derived_from_declared_requirements():
    plan = _chain().plan(("search",))
    assert [step.capability for step in plan.steps] == ["store", "index", "search"]
    assert plan.strategy == DEFAULT_STRATEGY
    assert plan.waves == 3


def test_registering_a_capability_changes_the_plan_with_no_code_change():
    planner = _chain()
    before = planner.plan(("search",))
    planner.register_capability("rank", requires=("search",))
    after = planner.plan(("rank",))
    assert len(after.steps) == len(before.steps) + 1
    assert after.plan_hash() != before.plan_hash()


def test_the_composition_rule_is_itself_replaceable():
    planner = _chain()
    total = planner.plan(("search",), strategy="dependency-order")
    waved = planner.plan(("search",), strategy="parallel-waves")
    assert {s.capability for s in total.steps} == {s.capability for s in waved.steps}
    assert total.plan_hash() != waved.plan_hash()
    assert "parallel-waves" in strategy_names()


def test_independent_capabilities_share_a_wave():
    planner = CompositionPlanner()
    planner.register_capability("left")
    planner.register_capability("right")
    planner.register_capability("join", requires=("left", "right"))
    plan = planner.plan(("join",), strategy="parallel-waves")
    waves = {step.capability: step.wave for step in plan.steps}
    assert waves["left"] == waves["right"] == 0
    assert waves["join"] == 1
    assert plan.waves == 2


def test_a_declared_cycle_is_detected_rather_than_ordered():
    planner = CompositionPlanner()
    # "alpha" forward-references "beta", so no kernel edge is created and the declared
    # graph is free to contain the cycle the kernel graph could never hold.
    planner.register_capability("alpha", requires=("beta",))
    planner.register_capability("beta", requires=("alpha",))
    with pytest.raises(CompositionCycleError):
        planner.plan(("alpha",))


def test_a_requirement_edge_that_would_cycle_is_carried_by_the_declaration_alone():
    planner = CompositionPlanner()
    planner.register_capability("one")
    two = planner.register_capability("two", requires=("one",))
    assert planner.capability("one").identity in two.related(REQUIRES)
    # Re-declaring "one" as requiring "two" would close a cycle in the kernel graph, so the
    # edge is skipped while the declaration still records the requirement.
    again = planner.register_capability("one", requires=("two",), version="2.0.0")
    assert again.attributes["requires"] == ["two"]
    assert again.related(REQUIRES) == ()


def test_composition_is_context_aware():
    planner = CompositionPlanner()
    planner.register_capability("localized", dimensions=("Language-Axis",))
    with pytest.raises(CompositionUnsatisfiedError, match="dimension"):
        planner.plan(("localized",))
    plan = planner.plan(("localized",), context=("Language-Axis",))
    assert plan.context == ("Language-Axis",)
    assert plan.steps[0].dimensions == ("Language-Axis",)


def test_composition_is_policy_aware():
    planner = CompositionPlanner()
    planner.register_capability("governed", policies=("retention",))
    with pytest.raises(CompositionUnsatisfiedError, match="policy"):
        planner.plan(("governed",))
    plan = planner.plan(("governed",), policies=("retention",))
    assert plan.policies == ("retention",)


def test_composition_is_evidence_aware():
    planner = CompositionPlanner()
    planner.register_capability("attested", evidence=("proof-1",))
    planner.register_capability("unattested")
    # Evidence declared but not supplied.
    with pytest.raises(CompositionUnsatisfiedError, match="evidence"):
        planner.plan(("attested",), require_evidence=True)
    # No evidence declared at all.
    with pytest.raises(CompositionUnsatisfiedError, match="evidence"):
        planner.plan(("unattested",), require_evidence=True)
    plan = planner.plan(("attested",), evidence=("proof-1",), require_evidence=True)
    assert plan.steps[0].capability == "attested"


def test_a_plan_with_no_target_is_refused():
    with pytest.raises(CompositionUnsatisfiedError, match="no composition target"):
        _chain().plan(())


def test_an_unregistered_strategy_is_refused():
    with pytest.raises(CompositionStrategyError):
        _chain().plan(("search",), strategy="does-not-exist")


def test_a_strategy_name_is_never_silently_replaced():
    with pytest.raises(ValueError, match="already registered"):
        register_strategy(DEFAULT_STRATEGY, dependency_order)


def test_a_new_strategy_is_admitted_by_registration():
    name = "test-reverse-key-order"
    if name not in strategy_names():
        register_strategy(name, lambda graph: [(0, key) for key in sorted(graph, reverse=True)])
    planner = _chain()
    plan = planner.plan(("search",), strategy=name)
    assert [s.capability for s in plan.steps] == ["store", "search", "index"]
    assert get_strategy(name) is not None


def test_an_unregistered_capability_is_refused():
    with pytest.raises(CapabilityUnknownError):
        _chain().plan(("absent",))


def test_the_requirement_closure_is_unbounded_and_deduplicated():
    planner = CompositionPlanner()
    planner.register_capability("base")
    planner.register_capability("left", requires=("base",))
    planner.register_capability("right", requires=("base",))
    planner.register_capability("top", requires=("left", "right"))
    closure = planner.closure(("top", "top"))
    assert set(closure) == {"top", "left", "right", "base"}
    plan = planner.plan(("top",))
    assert [s.capability for s in plan.steps][0] == "base"
    assert plan.targets == ("top",)


def test_discovery_by_dimension_policy_and_requirement():
    planner = CompositionPlanner()
    planner.register_capability("a", dimensions=("D",), policies=("P",))
    planner.register_capability("b", requires=("a",))
    assert [c.natural_key for c in planner.discover(dimension="D")] == ["a"]
    assert [c.natural_key for c in planner.discover(policy="P")] == ["a"]
    assert [c.natural_key for c in planner.discover(requires="a")] == ["b"]
    assert len(planner.discover()) == 2


def test_lookup_of_an_unregistered_capability_is_refused():
    with pytest.raises(CapabilityUnknownError):
        CompositionPlanner().capability("ghost")


def test_validate_rejects_an_unresolvable_requirement():
    planner = CompositionPlanner()
    planner.register_capability("dangling", requires=("never-registered",))
    assert planner.validate() is False


def test_validate_defers_to_the_kernel_audit_chain(monkeypatch):
    planner = _chain()
    assert planner.validate() is True
    monkeypatch.setattr(MetaKernel, "validate", lambda self: False)
    assert planner.validate() is False


def test_describe_declares_no_pipeline_and_no_limit():
    described = _chain().describe()
    assert described["fixed_pipeline"] is False
    assert described["upper_limit"] is None
    assert described["count"] == 3


def test_plan_and_step_serialisation_is_deterministic():
    plan = _chain().plan(("search",))
    payload = plan.to_dict()
    assert payload["plan_hash"] == plan.plan_hash()
    assert payload["waves"] == 3
    assert payload["steps"][0]["sequence"] == 0
    assert payload["steps"][0]["requires"] == []
    assert plan.to_dict() == plan.to_dict()


def test_the_planner_shares_one_kernel():
    kernel = MetaKernel()
    planner = CompositionPlanner(kernel=kernel)
    assert planner.kernel is kernel


def test_strategies_agree_on_the_acyclic_part_of_a_cyclic_graph():
    graph = {"a": ("b",), "b": ("a",), "c": ()}
    assert dependency_order(graph) == [(0, "c")]
    assert parallel_waves(graph) == [(0, "c")]
