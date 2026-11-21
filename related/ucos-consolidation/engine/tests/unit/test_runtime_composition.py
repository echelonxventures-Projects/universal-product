"""TASK-000041 — Universal Runtime Composition Engine unit tests (EPIC-006).

Exercises the Universe binding, the composition gates, deterministic identity, and
dynamic composition (RuntimeComposer) — all over synthetic assembled units.
"""

from __future__ import annotations

import json

import pytest

from engine.runtime.composition import (
    RUNTIME_COMPOSITION_FORMAT,
    RuntimeComposer,
    Universe,
    compose,
)
from engine.runtime.context import DEFAULT_CONTEXT, Federation
from engine.runtime.errors import (
    ReferenceFrameError,
    RuntimeCompositionError,
    RuntimeGraphError,
)


@pytest.fixture
def universes(make_runtime_unit):
    """Three same-context universes: A → B → (A) and C → {A, B}."""
    a = Universe.of(make_runtime_unit("A"), context_id="ctx1")
    b = Universe.of(make_runtime_unit("B"), context_id="ctx1", depends_on=["A"])
    c = Universe.of(make_runtime_unit("C"), context_id="ctx1", depends_on=["A", "B"])
    return a, b, c


# -- Universe -----------------------------------------------------------------


def test_universe_of_defaults_id_to_blueprint(make_runtime_unit):
    universe = Universe.of(make_runtime_unit("BP-DATA-0001"))
    assert universe.universe_id == "BP-DATA-0001"
    assert universe.context_id == DEFAULT_CONTEXT
    assert universe.depends_on == ()


def test_universe_depends_on_sorted_deduped(make_runtime_unit):
    universe = Universe.of(make_runtime_unit("X"), universe_id="X", depends_on=["b", "a", "b"])
    assert universe.depends_on == ("a", "b")


def test_universe_fingerprint_and_dict(make_runtime_unit):
    universe = Universe.of(make_runtime_unit("A"), context_id="ctx1", depends_on=["z"])
    assert universe.package_sha256 == universe.unit.package_sha256
    assert universe.fingerprint().startswith("A@ctx1:")
    blob = universe.to_dict()
    assert blob["universe_id"] == "A"
    assert blob["depends_on"] == ["z"]
    assert blob["unit"]["blueprint_id"] == "A"


# -- compose ------------------------------------------------------------------


def test_compose_builds_full_structure(universes):
    a, b, c = universes
    composition = compose([c, a, b], coordination="concurrent")
    assert composition.composition_id.startswith("UCOS-COMPOSITION-")
    assert composition.universe_ids() == ("A", "B", "C")
    assert composition.graph.order() == ("A", "B", "C")
    assert [ctx.context_id for ctx in composition.contexts] == ["ctx1"]
    assert composition.coordination == "concurrent"
    assert composition.descriptor["composition_descriptor_format"] == (RUNTIME_COMPOSITION_FORMAT)


def test_compose_carries_disclosure(universes):
    a, b, c = universes
    composition = compose([a, b, c])
    assert composition.disclosure["gate"] == "EC-1"
    assert composition.descriptor["provisional_state_disclosure"]["gate"] == "EC-1"


def test_compose_is_deterministic(universes):
    a, b, c = universes
    first = compose([a, b, c], coordination="conditional")
    second = compose([c, b, a], coordination="conditional")
    assert first.composition_id == second.composition_id
    assert json.dumps(first.descriptor, sort_keys=True) == json.dumps(
        second.descriptor, sort_keys=True
    )


def test_coordination_changes_identity(universes):
    a, b, c = universes
    seq = compose([a, b, c], coordination="sequential")
    con = compose([a, b, c], coordination="concurrent")
    assert seq.composition_id != con.composition_id


def test_universe_lookup(universes):
    a, b, c = universes
    composition = compose([a, b, c])
    assert composition.universe("B").universe_id == "B"
    with pytest.raises(RuntimeCompositionError):
        composition.universe("Z")


def test_composition_to_dict_serialisable(universes):
    a, b, c = universes
    blob = json.dumps(compose([a, b, c]).to_dict(), sort_keys=True)
    assert "UCOS-COMPOSITION-" in blob


# -- gates --------------------------------------------------------------------


def test_empty_composition_refused():
    with pytest.raises(RuntimeCompositionError) as exc:
        compose([])
    assert "at least one" in exc.value.message


def test_duplicate_universe_refused(universes):
    a, _b, _c = universes
    with pytest.raises(RuntimeCompositionError) as exc:
        compose([a, a])
    assert "duplicate" in exc.value.message


def test_non_universe_member_refused():
    with pytest.raises(RuntimeCompositionError) as exc:
        compose(["not-a-universe"])
    assert "Universe instances" in exc.value.message


def test_unit_without_disclosure_refused(make_runtime_unit):
    undisclosed = Universe.of(make_runtime_unit("A", disclosure=False))
    with pytest.raises(RuntimeCompositionError) as exc:
        compose([undisclosed])
    assert "disclosure" in exc.value.message


def test_cyclic_composition_refused(make_runtime_unit):
    a = Universe.of(make_runtime_unit("A"), depends_on=["B"])
    b = Universe.of(make_runtime_unit("B"), depends_on=["A"])
    with pytest.raises(RuntimeGraphError):
        compose([a, b])


def test_cross_context_without_federation_refused(make_runtime_unit):
    a = Universe.of(make_runtime_unit("A"), context_id="c1")
    b = Universe.of(make_runtime_unit("B"), context_id="c2", depends_on=["A"])
    with pytest.raises(ReferenceFrameError):
        compose([a, b])


def test_cross_context_with_federation(make_runtime_unit):
    a = Universe.of(make_runtime_unit("A"), context_id="c1")
    b = Universe.of(make_runtime_unit("B"), context_id="c2", depends_on=["A"])
    composition = compose([a, b], federations=[Federation("B", "A")])
    assert composition.federations == (Federation("B", "A"),)
    assert composition.descriptor["federations"] == [{"source": "B", "target": "A"}]


# -- dynamic composition (RuntimeComposer) ------------------------------------


def test_composer_builds_incrementally(make_runtime_unit):
    composer = RuntimeComposer()
    composer.add_unit(make_runtime_unit("A"), context_id="ctx1")
    composer.add(Universe.of(make_runtime_unit("B"), context_id="ctx1", depends_on=["A"]))
    composition = composer.compose(coordination="sequential")
    assert composition.universe_ids() == ("A", "B")


def test_composer_chaining_and_universes(make_runtime_unit):
    composer = (
        RuntimeComposer()
        .add_unit(make_runtime_unit("A"), context_id="c1")
        .add_unit(make_runtime_unit("B"), context_id="c2", depends_on=["A"])
        .federate("B", "A")
    )
    assert [u.universe_id for u in composer.universes()] == ["A", "B"]
    composition = composer.compose()
    assert composition.federations == (Federation("B", "A"),)


def test_composer_refuses_duplicate(make_runtime_unit):
    composer = RuntimeComposer().add_unit(make_runtime_unit("A"))
    with pytest.raises(RuntimeCompositionError) as exc:
        composer.add_unit(make_runtime_unit("A"))
    assert "already present" in exc.value.message


def test_composer_from_composition_extends_additively(universes):
    a, b, c = universes
    base = compose([a, b], coordination="sequential")
    extended = RuntimeComposer.from_composition(base).add(c).compose(coordination="sequential")
    assert extended.universe_ids() == ("A", "B", "C")
    # the base is unchanged (forward-only, no mutation)
    assert base.universe_ids() == ("A", "B")


def test_composer_from_composition_preserves_federation(make_runtime_unit):
    a = Universe.of(make_runtime_unit("A"), context_id="c1")
    b = Universe.of(make_runtime_unit("B"), context_id="c2", depends_on=["A"])
    base = compose([a, b], federations=[Federation("B", "A")])
    rebuilt = RuntimeComposer.from_composition(base).compose()
    assert rebuilt.composition_id == base.composition_id
