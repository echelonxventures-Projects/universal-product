"""WP-UCDA-018 — the generation runtime executes a derived order, not a written one.

``DEC-MCOS-14`` recorded that two ordering mechanisms coexisted: a plan derived by
``engine/civilization/composition.py`` and a hard-coded six-step sequence in
``engine/factory/orchestrator.py::execute``. ``WP-UCDA-018`` set two acceptance clauses:

    1. the derived order IS the order the located generation runtime executes, proven by a
       test that changes the plan through a registration and observes the executed order
       change;
    2. no second ordering mechanism remains reachable.

Both are asserted here.
"""

from __future__ import annotations

import pytest

from engine.civilization.composition import CompositionPlanner
from engine.factory import phases
from engine.factory.contracts import FactoryRequest
from engine.factory.errors import GenerationPhaseError, OrchestrationError
from engine.factory.phases import (
    generation_order,
    generation_phase,
    generation_phases,
    generation_span,
    generation_stages,
    phase_graph,
    register_generation_phase,
    seam_phase,
    unregister_generation_phase,
)
from engine.foundation import composition as located_ordering


@pytest.fixture
def declared_probe():
    """Register an observing phase after ``compile``, and withdraw it afterwards.

    ``dependency-order`` breaks ties by key, so a phase keyed ``aa-probe`` requiring
    ``compile`` is derived into the position immediately after ``compile`` and before
    ``assemble`` — a change to the executed order caused purely by a registration.
    """
    observed: list[str] = []

    def handler(_orchestrator, _state):
        observed.append("aa-probe")

    register_generation_phase("aa-probe", handler=handler, requires=("compile",))
    try:
        yield observed
    finally:
        unregister_generation_phase("aa-probe")


# -- clause 1: a registration changes the order the runtime executes ------------


def test_registration_changes_the_derived_order(declared_probe):
    order = generation_order()
    assert "aa-probe" in order
    assert order.index("compile") < order.index("aa-probe") < order.index("assemble")


def test_registration_changes_the_order_the_runtime_executes(orchestrator, declared_probe):
    """The observing phase runs during a real generation, in its derived position."""
    before = generation_order()
    result = orchestrator.generate(FactoryRequest("BP-DATA-0001"))
    # The generation still succeeds unchanged ...
    assert result.success is True
    # ... and the newly declared phase was executed by the runtime, not merely declared.
    assert declared_probe == ["aa-probe"]
    # The executed span is the derived span, and it now contains the new phase.
    assert "aa-probe" in generation_span(after_seam=True)
    assert generation_order() == before


def test_withdrawing_a_phase_restores_the_order(orchestrator):
    """Symmetry: the order follows the declarations in both directions."""
    baseline = generation_order()
    calls: list[str] = []
    register_generation_phase(
        "aa-probe", handler=lambda _o, _s: calls.append("x"), requires=("compile",)
    )
    assert generation_order() != baseline
    unregister_generation_phase("aa-probe")
    assert generation_order() == baseline
    orchestrator.generate(FactoryRequest("BP-DATA-0001"))
    assert calls == []


def test_advertised_stages_follow_the_registration(declared_probe):
    """A factory cannot advertise a stage vocabulary the runtime does not execute."""
    assert generation_stages() == generation_order()
    assert "aa-probe" in generation_stages()


# -- clause 2: no second ordering mechanism remains reachable -------------------


def test_the_runtime_and_the_planner_derive_through_one_authority():
    """The factory runtime and the civilization planner share one strategy registry."""
    name = "wp-ucda-018-probe-strategy"
    if name not in located_ordering.strategy_names():
        located_ordering.register_strategy(name, lambda graph: [(0, key) for key in sorted(graph)])
    # Registered once, in the located authority — visible to BOTH consumers.
    assert name in located_ordering.strategy_names()
    from engine.civilization import composition as civilization_composition

    assert name in civilization_composition.strategy_names()
    assert civilization_composition.get_strategy(name) is located_ordering.get_strategy(name)
    # And the runtime can be ordered by it.
    assert set(generation_order(strategy=name)) == set(phase_graph())


def test_the_planner_and_the_runtime_share_the_default_strategy():
    from engine.civilization import composition as civilization_composition

    assert civilization_composition.DEFAULT_STRATEGY == located_ordering.DEFAULT_STRATEGY
    assert civilization_composition.dependency_order is located_ordering.dependency_order
    assert civilization_composition.parallel_waves is located_ordering.parallel_waves


def test_no_frozen_stage_tuple_remains_in_the_factory_layer():
    """``DEFAULT_STAGES`` was a second, frozen declaration of the order. It is gone."""
    import engine.factory as factory_layer
    import engine.factory.factories as factories_package
    import engine.factory.factories.base as base

    for module in (factory_layer, factories_package, base):
        assert not hasattr(module, "DEFAULT_STAGES")


def test_the_planner_still_derives_capability_composition():
    """The other consumer is unaffected: a plan is still derived from declarations."""
    planner = CompositionPlanner()
    planner.register_capability("beta", requires=("alpha",))
    planner.register_capability("alpha")
    plan = planner.plan(["beta"])
    assert [step.capability for step in plan.steps] == ["alpha", "beta"]


# -- the declaration is refused when it cannot be ordered ----------------------


def test_duplicate_phase_is_refused():
    with pytest.raises(GenerationPhaseError):
        register_generation_phase("compile", handler=lambda _o, _s: None)


def test_second_seam_is_refused():
    with pytest.raises(GenerationPhaseError) as excinfo:
        register_generation_phase("aa-probe", handler=lambda _o, _s: None, seam=True)
    assert excinfo.value.context["seam"] == "resolve-factory"
    assert "aa-probe" not in phase_graph()


def test_requirement_naming_an_undeclared_phase_is_refused():
    register_generation_phase("aa-probe", handler=lambda _o, _s: None, requires=("nowhere",))
    try:
        with pytest.raises(GenerationPhaseError) as excinfo:
            generation_order()
        assert excinfo.value.context["missing"] == ["nowhere"]
    finally:
        unregister_generation_phase("aa-probe")


def test_declared_cycle_is_refused():
    register_generation_phase("aa-probe", handler=lambda _o, _s: None, requires=("ab-probe",))
    register_generation_phase("ab-probe", handler=lambda _o, _s: None, requires=("aa-probe",))
    try:
        with pytest.raises(GenerationPhaseError) as excinfo:
            generation_order()
        assert excinfo.value.context["unresolved"] == ["aa-probe", "ab-probe"]
    finally:
        unregister_generation_phase("aa-probe")
        unregister_generation_phase("ab-probe")


def test_withdrawing_an_undeclared_phase_is_refused():
    with pytest.raises(GenerationPhaseError):
        unregister_generation_phase("never-declared")


def test_unknown_phase_lookup_is_refused():
    with pytest.raises(GenerationPhaseError):
        generation_phase("never-declared")


def test_seam_absence_is_refused(monkeypatch):
    """A runtime with no declared delegation boundary has no lawful split."""
    without_seam = {key: phase for key, phase in phases._PHASES.items() if key != "resolve-factory"}
    monkeypatch.setattr(phases, "_PHASES", without_seam)
    with pytest.raises(GenerationPhaseError):
        seam_phase()


# -- the declaration surface --------------------------------------------------


def test_declared_graph_reproduces_the_located_sequence():
    """This is a change of authority over the order, not a change of behaviour."""
    assert generation_order() == (
        "resolve-blueprint",
        "classify",
        "resolve-factory",
        "compile",
        "assemble",
        "deploy",
        "rollback",
        "evidence",
    )
    assert generation_span(after_seam=False) == (
        "resolve-blueprint",
        "classify",
        "resolve-factory",
    )
    assert generation_span(after_seam=True) == (
        "compile",
        "assemble",
        "deploy",
        "rollback",
        "evidence",
    )


def test_describe_reports_an_open_surface():
    described = phases.describe()
    assert described["subject"] == "GenerationPhaseGraph"
    assert described["fixed_pipeline"] is False
    assert described["upper_limit"] is None
    assert described["seam"] == "resolve-factory"
    assert described["order"] == list(generation_order())
    assert described["count"] == len(generation_phases())


def test_phase_declaration_renders_deterministically():
    rendered = generation_phase("assemble").to_dict()
    assert rendered == {"key": "assemble", "requires": ["compile"], "seam": False}


# -- the runtime refuses to proceed on an unusable derived span -----------------
#
# Each guard below is reachable only by declaring a span that omits a phase another phase
# depends on. They are asserted rather than left uncovered because a runtime that silently
# continued past a missing phase would produce a result no phase computed — which is exactly
# the class of defect DEC-MCOS-14 recorded.


def test_context_unbound_is_refused():
    from engine.factory.orchestrator import GenerationState

    state = GenerationState(request=FactoryRequest("BP-DATA-0001"))
    with pytest.raises(OrchestrationError):
        state.bound()


def test_generate_without_a_resolved_factory_is_refused(orchestrator, monkeypatch):
    import engine.factory.orchestrator as orch

    monkeypatch.setattr(orch, "generation_span", lambda *, after_seam: ("resolve-blueprint",))
    with pytest.raises(OrchestrationError):
        orchestrator.generate(FactoryRequest("BP-DATA-0001"))


def test_execute_without_an_evidence_phase_is_refused(orchestrator, monkeypatch):
    import engine.factory.orchestrator as orch

    prefix = ("resolve-blueprint", "classify", "resolve-factory")
    monkeypatch.setattr(
        orch, "generation_span", lambda *, after_seam: ("compile",) if after_seam else prefix
    )
    with pytest.raises(OrchestrationError):
        orchestrator.generate(FactoryRequest("BP-DATA-0001"))


def test_evidence_without_an_assembled_unit_is_refused(orchestrator, monkeypatch):
    import engine.factory.orchestrator as orch

    prefix = ("resolve-blueprint", "classify", "resolve-factory")
    monkeypatch.setattr(
        orch,
        "generation_span",
        lambda *, after_seam: ("compile", "evidence") if after_seam else prefix,
    )
    with pytest.raises(OrchestrationError):
        orchestrator.generate(FactoryRequest("BP-DATA-0001"))


def test_factory_resolution_before_classification_is_refused(orchestrator, monkeypatch):
    import engine.factory.orchestrator as orch

    monkeypatch.setattr(
        orch, "generation_span", lambda *, after_seam: ("resolve-blueprint", "resolve-factory")
    )
    with pytest.raises(OrchestrationError):
        orchestrator.generate(FactoryRequest("BP-DATA-0001"))
