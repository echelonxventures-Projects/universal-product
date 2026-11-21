"""EPIC-006 — Universal Runtime Composition validation (integration).

Proves the EPIC-006 success criterion end to end: two **real, compiled, published,
assembled** runtime units (produced by the EPIC-003 pipeline + EPIC-005 assembly
against the certified compiler substrate) are composed into a deterministic,
bounded, acyclic :class:`RuntimeComposition` and coordinated
:class:`RuntimeOrchestration`, with the dependency graph, bounding contexts,
reference frames, execution plan, and EC-1 provisional-state disclosure all
resolved and preserved.

The runtime composition engine **composes existing Universes** — it reuses the
assembled units verbatim and adds no assembly, dependency-resolution, or execution
logic. No fixture short-circuits the engine.
"""

from __future__ import annotations

import json

import pytest

from engine.runtime import (
    Federation,
    RuntimeComposer,
    RuntimeComposition,
    RuntimeOrchestration,
    Universe,
    assemble,
    compose,
    orchestrate,
)
from engine.runtime.errors import ReferenceFrameError


@pytest.fixture
def assembled_units(published_package, dependency_published_package, runtime_signer):
    """Two genuine assembled RuntimeUnits: root BP-DATA-0001 + dep BP-DATA-0002."""
    root = assemble(published_package, verify_with=runtime_signer)
    dependency = assemble(dependency_published_package, verify_with=runtime_signer)
    return root, dependency


# -- SUCCESS CRITERION --------------------------------------------------------


def test_existing_universes_compose_into_runtime_composition(assembled_units):
    """Two assembled units compose into a deterministic RuntimeComposition."""
    root, dependency = assembled_units
    universes = [
        Universe.of(dependency, context_id="runtime"),
        Universe.of(root, context_id="runtime", depends_on=[dependency.blueprint_id]),
    ]
    composition = compose(universes, coordination="concurrent")

    assert isinstance(composition, RuntimeComposition)
    assert set(composition.universe_ids()) == {"BP-DATA-0001", "BP-DATA-0002"}
    # the dependency is composed before the root (dependencies first)
    order = composition.graph.order()
    assert order.index("BP-DATA-0002") < order.index("BP-DATA-0001")
    # the composed units are reused verbatim
    assert composition.universe("BP-DATA-0001").unit is root


def test_composition_preserves_disclosure(assembled_units):
    """The EC-1 provisional-state disclosure survives composition (DE-05)."""
    root, dependency = assembled_units
    composition = compose([Universe.of(root), Universe.of(dependency, universe_id="dep")])
    assert composition.disclosure["disclosure_id"] == "EC-1-PROVISIONAL-STATE"
    assert composition.disclosure["asserts_constitutional_finality"] is False


def test_orchestrating_existing_universes(assembled_units):
    """Existing Universes orchestrate into a coordinated RuntimeOrchestration."""
    root, dependency = assembled_units
    universes = [
        Universe.of(dependency),
        Universe.of(root, depends_on=[dependency.blueprint_id]),
    ]
    orchestration = orchestrate(universes, coordination="sequential")

    assert isinstance(orchestration, RuntimeOrchestration)
    plan_order = [step.universe_ids[0] for step in orchestration.plan.steps]
    assert plan_order.index("BP-DATA-0002") < plan_order.index("BP-DATA-0001")
    assert orchestration.descriptor["composition"]["universes"]


def test_composition_is_deterministic(assembled_units):
    """Identical Universes ⇒ byte-identical composition + orchestration."""
    root, dependency = assembled_units

    def build():
        universes = [
            Universe.of(dependency),
            Universe.of(root, depends_on=[dependency.blueprint_id]),
        ]
        return orchestrate(universes, coordination="concurrent")

    first, second = build(), build()
    assert first.orchestration_id == second.orchestration_id
    assert json.dumps(first.to_dict(), sort_keys=True) == json.dumps(
        second.to_dict(), sort_keys=True
    )


# -- CROSS-CONTEXT FEDERATION -------------------------------------------------


def test_cross_context_composition_requires_federation(assembled_units):
    """A cross-context dependency without a federation reference is refused."""
    root, dependency = assembled_units
    universes = [
        Universe.of(dependency, context_id="data"),
        Universe.of(root, context_id="app", depends_on=[dependency.blueprint_id]),
    ]
    with pytest.raises(ReferenceFrameError):
        compose(universes)


def test_cross_context_composition_with_federation(assembled_units):
    """An explicit federation reference authorises the cross-context dependency."""
    root, dependency = assembled_units
    universes = [
        Universe.of(dependency, context_id="data"),
        Universe.of(root, context_id="app", depends_on=[dependency.blueprint_id]),
    ]
    composition = compose(
        universes, federations=[Federation(root.blueprint_id, dependency.blueprint_id)]
    )
    assert {c.context_id for c in composition.contexts} == {"data", "app"}
    frame = {f.universe_id: f for f in composition.reference_frames}[root.blueprint_id]
    assert frame.federated == (dependency.blueprint_id,)


# -- DYNAMIC COMPOSITION ------------------------------------------------------


def test_dynamic_composition_extends_existing(assembled_units):
    """A composition can be extended additively via the RuntimeComposer."""
    root, dependency = assembled_units
    base = compose([Universe.of(dependency)])
    extended = (
        RuntimeComposer.from_composition(base)
        .add(Universe.of(root, depends_on=[dependency.blueprint_id]))
        .compose(coordination="sequential")
    )
    assert set(extended.universe_ids()) == {"BP-DATA-0001", "BP-DATA-0002"}
    assert base.universe_ids() == ("BP-DATA-0002",)
