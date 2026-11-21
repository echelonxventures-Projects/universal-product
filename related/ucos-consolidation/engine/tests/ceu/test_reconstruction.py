"""UCOS-CEU-001 — Steering 022: Repository Truth must be sufficient to reconstruct state.

The property: everything the registry knows is *in its document*. If any constitutional
fact lives only in memory, the rebuilt registry diverges and these tests fail.

The sharp version of the claim is the certification one — a determination computed over a
registry rebuilt from a document must equal the determination computed over the original.
If it does not, certification depended on hidden runtime state, which Steering 016 and 022
both forbid.
"""

from __future__ import annotations

import pytest

from engine.ceu.catalog import bootstrap, relationship_view
from engine.ceu.errors import ExistenceError
from engine.ceu.existence import ExistenceRegistry, ExistenceUnit, reconstruct
from engine.ceu.possessions import assess, certify_levels, completeness
from engine.ceu.sufficiency import assess_registry

FRAME = {"frame": "planetary-a1", "resolution_digest": "abc"}


@pytest.fixture
def seeded() -> ExistenceRegistry:
    registry = bootstrap()
    registry.bind_context(FRAME)
    return registry


def _evolved(registry: ExistenceRegistry) -> ExistenceRegistry:
    """A registry carrying every kind of history: relationships, supersession, revival."""
    view = relationship_view(registry)
    a = registry.register(ExistenceUnit(form="entity", key="a", title="A"))
    b = registry.register(ExistenceUnit(form="entity", key="b", title="B"))
    view.relate("composes", a.universal_id, b.universal_id, authority="T")
    view.relate("contradicts", a.universal_id, b.universal_id, authority="T")
    layer = registry.unit("classification", "layer")
    registry.supersede(layer.universal_id, authority="GOV", note="split")
    registry.resurrect(layer.universal_id, authority="GOV")
    obsolete = registry.register(ExistenceUnit(form="entity", key="gone", title="Gone"))
    registry.supersede(obsolete.universal_id, authority="GOV")
    return registry


def test_a_seeded_registry_reconstructs_exactly(seeded: ExistenceRegistry):
    report = reconstruct(seeded)
    assert report["reconstructed"] is True
    assert report["source_digest"] == report["rebuilt_digest"]
    assert report["divergent_sections"] == []
    assert report["source_units"] == report["rebuilt_units"]


def test_a_registry_carrying_history_reconstructs_exactly(seeded: ExistenceRegistry):
    report = reconstruct(_evolved(seeded))
    assert report["reconstructed"] is True
    assert report["journal_verifies"] is True
    assert report["audit_head_matches"] is True


def test_the_journal_survives_reconstruction(seeded: ExistenceRegistry):
    evolved = _evolved(seeded)
    rebuilt = ExistenceRegistry.from_document(evolved.to_document())
    assert [e.to_dict() for e in rebuilt.audit()] == [e.to_dict() for e in evolved.audit()]
    assert rebuilt.verify_audit() == []


def test_supersession_and_resurrection_survive_reconstruction(seeded: ExistenceRegistry):
    evolved = _evolved(seeded)
    rebuilt = ExistenceRegistry.from_document(evolved.to_document())
    layer = evolved.unit("classification", "layer").universal_id
    gone = evolved.unit("entity", "gone").universal_id
    assert rebuilt.is_superseded(gone) is True
    assert rebuilt.is_superseded(layer) is False  # resurrected, and the record persists
    assert rebuilt.supersessions() == evolved.supersessions()


def test_the_context_binding_survives_reconstruction(seeded: ExistenceRegistry):
    rebuilt = ExistenceRegistry.from_document(seeded.to_document())
    assert rebuilt.context == seeded.context
    assert rebuilt.is_context_bound


def test_relationships_survive_reconstruction(seeded: ExistenceRegistry):
    evolved = _evolved(seeded)
    rebuilt = ExistenceRegistry.from_document(evolved.to_document())
    view = relationship_view(rebuilt)
    a = rebuilt.unit("entity", "a").universal_id
    assert view.neighbours(a, relationship_type="composes")
    assert view.topologies_of(a) == relationship_view(evolved).topologies_of(a)


def test_the_root_form_is_not_manufactured_twice(seeded: ExistenceRegistry):
    """Reconstruction replays the recorded root; it does not bootstrap a second one."""
    rebuilt = ExistenceRegistry.from_document(seeded.to_document())
    genesis = [e for e in rebuilt.audit() if e.action == "register"]
    roots = [u for u in rebuilt.units(form=rebuilt.root_form) if u.key == rebuilt.root_form]
    assert len(roots) == 1
    assert len(genesis) == len(seeded.units())


# --------------------------------------------------------------------------- #
# No determination may depend on hidden runtime state                          #
# --------------------------------------------------------------------------- #


def test_certification_is_identical_on_the_reconstructed_registry(seeded: ExistenceRegistry):
    """Steering 016/022 — the decisive test."""
    evolved = _evolved(seeded)
    rebuilt = ExistenceRegistry.from_document(evolved.to_document())
    assert certify_levels(rebuilt) == certify_levels(evolved)


def test_every_determination_is_identical_on_the_reconstructed_registry(seeded):
    evolved = _evolved(seeded)
    rebuilt = ExistenceRegistry.from_document(evolved.to_document())
    assert assess(rebuilt) == assess(evolved)
    assert completeness(rebuilt) == completeness(evolved)
    assert assess_registry(rebuilt) == assess_registry(evolved)


def test_reconstruction_is_itself_reproducible(seeded: ExistenceRegistry):
    document = seeded.to_document()
    first = ExistenceRegistry.from_document(document)
    second = ExistenceRegistry.from_document(document)
    assert first.digest() == second.digest() == seeded.digest()


# --------------------------------------------------------------------------- #
# A document that is not sufficient is refused, never partially loaded         #
# --------------------------------------------------------------------------- #


def test_a_malformed_document_is_refused():
    for payload in ({}, {"root_form": "form"}, {"units": []}):
        with pytest.raises(ExistenceError):
            ExistenceRegistry.from_document(payload)


def test_a_tampered_unit_is_refused(seeded: ExistenceRegistry):
    document = seeded.to_document()
    document["units"][3]["title"] = "Tampered"
    with pytest.raises(ExistenceError) as caught:
        ExistenceRegistry.from_document(document)
    assert "does not reproduce" in caught.value.message


def test_a_tampered_journal_is_refused(seeded: ExistenceRegistry):
    document = seeded.to_document()
    document["audit"][5]["subject"] = "UCOS-ENTY-ffffffffffff"
    with pytest.raises(ExistenceError) as caught:
        ExistenceRegistry.from_document(document)
    assert caught.value.detail["findings"]


def test_a_truncated_journal_is_refused(seeded: ExistenceRegistry):
    document = seeded.to_document()
    del document["audit"][0]
    with pytest.raises(ExistenceError):
        ExistenceRegistry.from_document(document)
