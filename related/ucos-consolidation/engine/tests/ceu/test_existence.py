"""UCOS-CEU-001 — the existence substrate: existence precedes entity.

What these tests exist to falsify, stated as the failures they would catch:

* a form, classification, relationship or topology that is *not* a registered unit —
  i.e. a construct privileged by being a shape in the source code (UCEP-001, UCEP-002);
* ownership decided by a predicate rather than discovered from the registry (CEU-006);
* a relationship that is an edge rather than an entity with identity and lineage (CEU-003);
* an entity confined to one topology at a time (CEU-004, S-007);
* a classification that cannot split, merge, deprecate or come back (CEU-002);
* a registered unit with no identifier, no journal entry, or a non-reproducing digest
  (UCEP-007);
* a ceiling anywhere.
"""

from __future__ import annotations

import pytest

from engine.ceu.errors import (
    ExistenceError,
    ExistenceRegistrationError,
    RelationshipAdmissibilityError,
    RelationshipError,
    TopologyCycleError,
)
from engine.ceu.existence import (
    ATTR_FACULTIES,
    ATTR_SPECIALIZES,
    ExistenceRegistry,
    ExistenceUnit,
    RelationshipView,
)
from engine.registry.universal.identity import is_well_formed, parse_kind_name

FORMS = (
    ("classification", "CLSS"),
    ("relationship-type", "RLTY"),
    ("relationship", "RSHP"),
    ("topology", "TOPO"),
    ("entity", "ENTY"),
)


@pytest.fixture
def registry() -> ExistenceRegistry:
    reg = ExistenceRegistry()
    for key, code in FORMS:
        reg.declare_form(key, title=key.title(), code=code)
    return reg


@pytest.fixture
def view(registry: ExistenceRegistry) -> RelationshipView:
    return RelationshipView(
        registry,
        type_form="relationship-type",
        relationship_form="relationship",
        topology_form="topology",
    )


def _classification(registry: ExistenceRegistry, key: str, **attributes) -> ExistenceUnit:
    return registry.register(
        ExistenceUnit(form="classification", key=key, title=key.title(), attributes=attributes)
    )


def _entity(registry: ExistenceRegistry, key: str, classification: str = "") -> ExistenceUnit:
    return registry.register(
        ExistenceUnit(form="entity", key=key, title=key.upper(), classification=classification)
    )


# --------------------------------------------------------------------------- #
# Existence precedes entity                                                    #
# --------------------------------------------------------------------------- #


def test_the_root_form_is_a_unit_of_itself():
    reg = ExistenceRegistry()
    root = reg.form_of(reg.root_form)
    assert root.form == root.key == reg.root_form
    assert is_well_formed(root.universal_id)


def test_the_root_is_not_a_reserved_word():
    """Even the name of the root is configuration, not vocabulary baked into the code."""
    reg = ExistenceRegistry(root_form="species-of-being", root_code="SPOB")
    assert reg.root_form == "species-of-being"
    assert reg.form_of("species-of-being").form == "species-of-being"
    assert not reg.has_form("form")


def test_entity_is_one_form_among_many_and_not_the_root(registry: ExistenceRegistry):
    assert "entity" in registry.form_keys()
    assert registry.form_of("entity").form == registry.root_form
    # the root form is the only self-referential one; entity has no special status
    assert registry.form_of("entity").key != registry.root_form


def test_a_future_form_needs_no_code_change(registry: ExistenceRegistry):
    registry.declare_form("dream", title="Dream", code="DRMX")
    unit = registry.register(ExistenceUnit(form="dream", key="d1", title="A Dream"))
    assert parse_kind_name(unit.universal_id) == "DREAM"
    assert registry.counts()["dream"] == 1


@pytest.mark.parametrize("form", [f for f, _ in FORMS])
def test_every_construct_is_a_registered_unit(registry: ExistenceRegistry, form: str):
    """UCEP-001: classification, relationship and topology are units, not shapes."""
    declared = registry.form_of(form)
    assert declared.form == registry.root_form
    assert is_well_formed(declared.universal_id)
    assert registry.audit(subject=declared.universal_id)


# --------------------------------------------------------------------------- #
# Identity, lineage, registration (UCEP-007)                                   #
# --------------------------------------------------------------------------- #


def test_an_unregistered_unit_has_no_identity():
    detached = ExistenceUnit(form="entity", key="ghost", title="Ghost")
    with pytest.raises(ExistenceError):
        _ = detached.universal_id


def test_every_registered_unit_is_identified_journaled_and_intact(registry: ExistenceRegistry):
    _classification(registry, "nucleus")
    assert registry.unlineaged() == ()
    assert registry.verify_audit() == []
    for unit in registry.units():
        assert is_well_formed(unit.universal_id)
        assert unit.is_intact()


def test_registration_is_idempotent_and_refuses_a_conflicting_rewrite(registry):
    first = _classification(registry, "nucleus")
    assert _classification(registry, "nucleus") == first
    with pytest.raises(ExistenceRegistrationError):
        registry.register(
            ExistenceUnit(form="classification", key="nucleus", title="Something Else")
        )


def test_a_unit_of_an_unregistered_form_is_refused(registry: ExistenceRegistry):
    with pytest.raises(ExistenceError):
        registry.register(ExistenceUnit(form="rumour", key="r", title="R"))


def test_a_unit_naming_an_unregistered_classification_is_refused(registry):
    with pytest.raises(ExistenceRegistrationError):
        _entity(registry, "a", classification="UCOS-CLSS-ffffffffffff")


@pytest.mark.parametrize("field", ["form", "key", "title"])
def test_a_unit_must_declare_its_own_fields(field: str):
    kwargs = {"form": "entity", "key": "k", "title": "T"}
    kwargs[field] = "  "
    with pytest.raises(ExistenceError):
        ExistenceUnit(**kwargs)


# --------------------------------------------------------------------------- #
# Ownership is discovered, not hardcoded (CEU-006)                             #
# --------------------------------------------------------------------------- #


def test_ownership_is_a_registered_faculty_not_a_predicate(registry: ExistenceRegistry):
    nucleus = _classification(registry, "nucleus", **{ATTR_FACULTIES: ("own-capability",)})
    layer = _classification(registry, "layer")
    assert registry.holds(nucleus.universal_id, "own-capability")
    assert not registry.holds(layer.universal_id, "own-capability")


def test_owners_are_discovered_by_query(registry: ExistenceRegistry):
    nucleus = _classification(registry, "nucleus", **{ATTR_FACULTIES: ("own-capability",)})
    _classification(registry, "layer")
    assert registry.holding("own-capability") == (nucleus.universal_id,)


def test_a_specialization_inherits_the_faculty_without_restating_it(registry):
    nucleus = _classification(registry, "nucleus", **{ATTR_FACULTIES: ("own-capability",)})
    micro = _classification(registry, "micro-nucleus", **{ATTR_SPECIALIZES: nucleus.universal_id})
    nano = _classification(registry, "nano-nucleus", **{ATTR_SPECIALIZES: micro.universal_id})
    assert registry.holds(nano.universal_id, "own-capability")
    assert registry.ancestry(nano.universal_id) == (
        nano.universal_id,
        micro.universal_id,
        nucleus.universal_id,
    )
    assert nano.universal_id in registry.specializations_of(nucleus.universal_id)


def test_a_new_faculty_needs_no_code_change(registry: ExistenceRegistry):
    holder = _classification(registry, "steward", **{ATTR_FACULTIES: ("hold-mandate",)})
    assert registry.holding("hold-mandate") == (holder.universal_id,)


# --------------------------------------------------------------------------- #
# Classifications evolve (CEU-002)                                             #
# --------------------------------------------------------------------------- #


def test_a_classification_splits(registry: ExistenceRegistry):
    old = _classification(registry, "unit")
    a = _classification(registry, "nucleus")
    b = _classification(registry, "layer")
    record = registry.supersede(
        old.universal_id, successors=[a.universal_id, b.universal_id], authority="GOV"
    )
    assert record["successors"] == [a.universal_id, b.universal_id]
    assert registry.is_superseded(old.universal_id)
    assert old.universal_id not in {u.universal_id for u in registry.admissible()}


def test_classifications_merge(registry: ExistenceRegistry):
    a = _classification(registry, "nucleus")
    b = _classification(registry, "micro-nucleus")
    merged = _classification(registry, "capability-authority")
    for old in (a, b):
        registry.supersede(old.universal_id, successors=[merged.universal_id], authority="GOV")
    assert registry.successors_of(a.universal_id) == registry.successors_of(b.universal_id)


def test_a_deprecated_classification_has_no_successor(registry: ExistenceRegistry):
    old = _classification(registry, "obsolete")
    registry.supersede(old.universal_id, authority="GOV")
    assert registry.successors_of(old.universal_id) == ()
    assert registry.supersessions()[0]["deprecated_outright"] is True


def test_a_superseded_classification_admits_no_new_units(registry: ExistenceRegistry):
    old = _classification(registry, "obsolete")
    registry.supersede(old.universal_id, authority="GOV")
    with pytest.raises(ExistenceRegistrationError):
        _entity(registry, "a", classification=old.universal_id)


def test_supersession_is_not_deletion(registry: ExistenceRegistry):
    old = _classification(registry, "obsolete")
    registry.supersede(old.universal_id, authority="GOV")
    assert registry.resolve(old.universal_id) == old


def test_a_classification_can_be_resurrected(registry: ExistenceRegistry):
    old = _classification(registry, "obsolete")
    registry.supersede(old.universal_id, authority="GOV")
    registry.resurrect(old.universal_id, authority="GOV", note="needed again")
    assert not registry.is_superseded(old.universal_id)
    assert _entity(registry, "a", classification=old.universal_id)


def test_resurrection_keeps_the_supersession_in_the_journal(registry: ExistenceRegistry):
    old = _classification(registry, "obsolete")
    registry.supersede(old.universal_id, authority="GOV")
    registry.resurrect(old.universal_id, authority="GOV")
    actions = [e.action for e in registry.audit(subject=old.universal_id)]
    assert actions == ["register", "supersede", "resurrect"]


def test_resurrection_preserves_the_pre_resurrection_field_values(registry: ExistenceRegistry):
    """P4-F-001: the record right after supersede() must survive resurrect() intact,
    not just be provable by hash — the actual field values must be readable."""
    old = _classification(registry, "obsolete")
    registry.supersede(old.universal_id, authority="GOV", note="first pass")
    registry.resurrect(old.universal_id, authority="GOV", note="needed again")
    history = registry.supersession_history(old.universal_id)
    assert len(history) == 2
    assert history[0]["active"] is True
    assert history[0]["note"] == "first pass"
    assert "resurrected_by" not in history[0]
    assert history[1]["active"] is False
    assert history[1]["resurrected_by"] == "GOV"
    assert history[1]["resurrection_note"] == "needed again"
    # the resurrection snapshot still carries the original supersession's own note —
    # it is a new record built from the old one, not an unrelated fresh record
    assert history[1]["note"] == "first pass"


def test_a_split_supersede_and_resurrect_cycle_is_fully_reconstructible(
    registry: ExistenceRegistry,
):
    """A subject superseded, resurrected, then superseded again keeps every snapshot."""
    old = _classification(registry, "cyclical")
    registry.supersede(old.universal_id, authority="GOV", note="round one")
    registry.resurrect(old.universal_id, authority="GOV")
    registry.supersede(old.universal_id, authority="GOV", note="round two")
    history = registry.supersession_history(old.universal_id)
    assert len(history) == 3
    assert [h["active"] for h in history] == [True, False, True]
    assert history[0]["note"] == "round one"
    assert history[2]["note"] == "round two"
    # supersessions() still reports only the CURRENT state — one row, not three
    assert len(registry.supersessions()) == 1
    assert registry.supersessions()[0]["note"] == "round two"


def test_supersession_history_survives_reconstruction(registry: ExistenceRegistry):
    old = _classification(registry, "obsolete")
    registry.supersede(old.universal_id, authority="GOV", note="first")
    registry.resurrect(old.universal_id, authority="GOV")
    rebuilt = ExistenceRegistry.from_document(registry.to_document())
    assert rebuilt.supersession_history(old.universal_id) == registry.supersession_history(
        old.universal_id
    )
    assert rebuilt.digest() == registry.digest()


def test_supersession_refuses_the_unlawful_cases(registry: ExistenceRegistry):
    a = _classification(registry, "a")
    b = _classification(registry, "b")
    with pytest.raises(ExistenceError):
        registry.supersede(a.universal_id, successors=[a.universal_id], authority="GOV")
    with pytest.raises(ExistenceError):
        registry.supersede(a.universal_id, successors=[b.universal_id], authority="  ")
    registry.supersede(b.universal_id, authority="GOV")
    with pytest.raises(ExistenceError):
        registry.supersede(a.universal_id, successors=[b.universal_id], authority="GOV")
    with pytest.raises(ExistenceError):
        registry.resurrect(a.universal_id, authority="GOV")


def test_every_construct_supersedes_through_the_one_mechanism(registry, view):
    """CEU-002/003/004: forms, topologies and relationship types evolve identically."""
    registry.register(ExistenceUnit(form="topology", key="mesh", title="Mesh"))
    registry.register(ExistenceUnit(form="relationship-type", key="peers", title="Peers"))
    for form, key in (("form", "entity"), ("topology", "mesh"), ("relationship-type", "peers")):
        unit = registry.unit(form, key)
        registry.supersede(unit.universal_id, authority="GOV")
        assert registry.is_superseded(unit.universal_id)


# --------------------------------------------------------------------------- #
# Relationships are entities (CEU-003)                                         #
# --------------------------------------------------------------------------- #


def _wire(registry: ExistenceRegistry, view: RelationshipView) -> tuple[str, str]:
    registry.register(ExistenceUnit(form="topology", key="hierarchy", title="Hierarchy"))
    registry.register(ExistenceUnit(form="topology", key="mesh", title="Mesh"))
    registry.register(
        ExistenceUnit(
            form="relationship-type",
            key="composes",
            title="Composes",
            attributes={"acyclic": True, "topologies": ("hierarchy",)},
        )
    )
    registry.register(
        ExistenceUnit(
            form="relationship-type",
            key="peers-with",
            title="Peers With",
            attributes={"topologies": ("mesh",)},
        )
    )
    return _entity(registry, "a").universal_id, _entity(registry, "b").universal_id


def test_a_relationship_is_a_registered_identified_lineaged_unit(registry, view):
    a, b = _wire(registry, view)
    edge = view.relate("composes", a, b, authority="T")
    assert edge.form == "relationship"
    assert is_well_formed(edge.universal_id)
    assert registry.audit(subject=edge.universal_id)
    assert edge.is_intact()
    assert registry.resolve(edge.universal_id) == edge


def test_a_relationship_supersedes_like_any_other_unit(registry, view):
    a, b = _wire(registry, view)
    edge = view.relate("composes", a, b, authority="T")
    registry.supersede(edge.universal_id, authority="GOV")
    assert registry.is_superseded(edge.universal_id)


def test_any_form_may_relate_to_any_form_by_default(registry, view):
    """CEU-007: validity is registry-driven, and the default declares no restriction."""
    a, _ = _wire(registry, view)
    topology = registry.unit("topology", "mesh").universal_id
    edge = view.relate("peers-with", a, topology, authority="T")
    assert edge.attribute("target") == topology


def test_a_relationship_may_relate_two_relationships(registry, view):
    a, b = _wire(registry, view)
    first = view.relate("composes", a, b, authority="T")
    second = view.relate("peers-with", a, b, authority="T")
    linked = view.relate("peers-with", first.universal_id, second.universal_id, authority="T")
    assert linked.attribute("source") == first.universal_id


def test_a_declared_constraint_is_enforced(registry, view):
    a, b = _wire(registry, view)
    registry.register(
        ExistenceUnit(
            form="relationship-type",
            key="entities-only",
            title="Entities Only",
            attributes={"source_forms": ("entity",), "target_forms": ("entity",)},
        )
    )
    assert view.relate("entities-only", a, b, authority="T")
    topology = registry.unit("topology", "mesh").universal_id
    with pytest.raises(RelationshipAdmissibilityError):
        view.relate("entities-only", a, topology, authority="T")


def test_an_unregistered_endpoint_is_refused(registry, view):
    a, _ = _wire(registry, view)
    with pytest.raises(RelationshipAdmissibilityError):
        view.relate("composes", a, "UCOS-ENTY-ffffffffffff", authority="T")


def test_an_unregistered_or_superseded_type_is_refused(registry, view):
    a, b = _wire(registry, view)
    with pytest.raises(RelationshipError):
        view.relate("imagines", a, b, authority="T")
    declared = registry.unit("relationship-type", "composes")
    registry.supersede(declared.universal_id, authority="GOV")
    with pytest.raises(RelationshipError):
        view.relate("composes", a, b, authority="T")


def test_an_acyclic_type_refuses_a_cycle(registry, view):
    a, b = _wire(registry, view)
    view.relate("composes", a, b, authority="T")
    with pytest.raises(TopologyCycleError):
        view.relate("composes", b, a, authority="T")


def test_a_type_that_is_not_acyclic_permits_a_cycle(registry, view):
    a, b = _wire(registry, view)
    view.relate("peers-with", a, b, authority="T")
    assert view.relate("peers-with", b, a, authority="T")
    assert view.cycle_in("peers-with")


def test_relationship_depth_is_unlimited(registry, view):
    _wire(registry, view)
    chain = [_entity(registry, f"n{i}").universal_id for i in range(12)]
    for source, target in zip(chain, chain[1:], strict=False):
        view.relate("composes", source, target, authority="T")
    assert len(view.reachable(chain[0], "composes")) == len(chain) - 1


# --------------------------------------------------------------------------- #
# Simultaneous, unlimited topologies (CEU-004, S-007)                          #
# --------------------------------------------------------------------------- #


def test_one_entity_participates_in_many_topologies_at_once(registry, view):
    a, b = _wire(registry, view)
    for extra in ("fractal", "semantic", "temporal"):
        registry.register(ExistenceUnit(form="topology", key=extra, title=extra.title()))
    view.relate("composes", a, b, authority="T")
    view.relate("peers-with", a, b, authority="T", topologies=("fractal", "semantic", "temporal"))
    assert view.topologies_of(a) == ("fractal", "hierarchy", "mesh", "semantic", "temporal")


def test_topology_membership_is_discoverable(registry, view):
    a, b = _wire(registry, view)
    view.relate("composes", a, b, authority="T")
    assert view.participants("hierarchy") == tuple(sorted((a, b)))
    assert view.participants("mesh") == ()


def test_a_relationship_naming_an_unregistered_topology_is_refused(registry, view):
    a, b = _wire(registry, view)
    with pytest.raises(ExistenceError):
        view.relate("composes", a, b, authority="T", topologies=("nowhere",))


def test_the_graph_reports_no_dangling_endpoints(registry, view):
    a, b = _wire(registry, view)
    view.relate("composes", a, b, authority="T")
    assert view.dangling() == ()


# --------------------------------------------------------------------------- #
# Context, determinism, no ceiling                                             #
# --------------------------------------------------------------------------- #


def test_the_substrate_binds_to_one_reality(registry: ExistenceRegistry):
    fingerprint = {"frame": "planetary-a1", "resolution_digest": "abc"}
    assert registry.bind_context(fingerprint) == fingerprint
    assert registry.bind_context(fingerprint) == fingerprint
    assert registry.is_context_bound
    with pytest.raises(ExistenceError):
        registry.bind_context({"frame": "planetary-b4", "resolution_digest": "def"})


def test_an_unbound_substrate_fails_closed(registry: ExistenceRegistry):
    with pytest.raises(ExistenceError):
        registry.require_context()
    with pytest.raises(ExistenceError):
        registry.bind_context({"frame": "f"})


def test_the_substrate_is_deterministic(registry: ExistenceRegistry):
    assert registry.digest() == registry.digest()
    assert ExistenceRegistry().digest() == ExistenceRegistry().digest()


def test_two_identically_built_substrates_agree():
    def build() -> ExistenceRegistry:
        reg = ExistenceRegistry()
        for key, code in FORMS:
            reg.declare_form(key, title=key.title(), code=code)
        _classification(reg, "nucleus", **{ATTR_FACULTIES: ("own-capability",)})
        return reg

    assert build().digest() == build().digest()


def test_the_document_declares_no_ceiling(registry: ExistenceRegistry):
    document = registry.to_document()
    assert document["closed_set"] is False
    assert document["upper_limit"] is None
    assert document["root_form"] == registry.root_form
    assert document["counts"]["by_form"]


def test_the_journal_detects_tampering(registry: ExistenceRegistry):
    _classification(registry, "nucleus")
    assert registry.verify_audit() == []
    registry._audit[0] = registry._audit[0].__class__(  # noqa: SLF001 - forced state
        sequence=99,
        action="register",
        subject="tampered",
        content_hash="x",
        prev_hash="y",
    )
    assert registry.verify_audit()


# --------------------------------------------------------------------------- #
# The registry's own surface, and every refusal it is built to make            #
#                                                                             #
# WHY THIS SECTION EXISTS. The suite above proves the SUBSTRATE's properties   #
# — existence precedes entity, a relationship is a unit, a classification can  #
# come back. It reaches those properties through a small, happy subset of the  #
# registry's API, so the accessors the rest of the repository actually calls   #
# (`resolve` on an unknown id, `register_all`, `identifiers`, `form_id_of`,    #
# `successors_of_key`, `require_context`) and the refusals that make the       #
# append-only claim mean anything (rewriting an active supersession, a         #
# resurrection with no authority, a cycle in the specialization graph) were    #
# never executed. An append-only registry that has never refused a rewrite is  #
# a registry that has only ever been asked nicely.                             #
# --------------------------------------------------------------------------- #


def test_a_registry_must_name_its_root_form():
    with pytest.raises(ExistenceError, match="root form must be named"):
        ExistenceRegistry(root_form="   ")


def test_resolving_an_identifier_nothing_registered_fails_closed(registry):
    with pytest.raises(ExistenceError, match="not registered"):
        registry.resolve("UCOS-ENTY-ffffffffffff")
    assert registry.find("UCOS-ENTY-ffffffffffff") is None
    assert registry.form_id_of("UCOS-ENTY-ffffffffffff") is None


def test_a_batch_registration_registers_every_unit_it_is_given(registry):
    units = (
        ExistenceUnit(form="entity", key="batch-a", title="A"),
        ExistenceUnit(form="entity", key="batch-b", title="B"),
    )
    registered = registry.register_all(units)
    assert [u.key for u in registered] == ["batch-a", "batch-b"]
    assert registry.counts()["entity"] == 2
    assert set(registry.identifiers()) >= {u.universal_id for u in registered}
    assert registry.identifiers() == tuple(sorted(registry.identifiers()))


def test_the_form_of_a_registered_identifier_is_answerable(registry):
    unit = _entity(registry, "addressed")
    assert registry.form_id_of(unit.universal_id) == "entity"
    assert registry.id_of("entity", "addressed") == unit.universal_id


def test_a_superseded_form_admits_no_new_units(registry):
    form = registry.form_of("entity")
    successor = registry.declare_form("successor-entity", title="Successor", code="SENT")
    registry.supersede(form.universal_id, successors=(successor.universal_id,), authority="GOV")
    assert registry.is_superseded_key(registry.root_form, "entity") is True
    assert registry.successors_of_key(registry.root_form, "entity") == (successor.universal_id,)
    with pytest.raises(ExistenceRegistrationError, match="superseded form"):
        _entity(registry, "too-late")


def test_a_key_nothing_registered_is_neither_superseded_nor_has_successors(registry):
    assert registry.is_superseded_key("entity", "never-existed") is False
    assert registry.successors_of_key("entity", "never-existed") == ()


def test_repeating_an_identical_supersession_is_the_same_act_and_not_a_second_one(registry):
    unit = _entity(registry, "twice")
    first = registry.supersede(unit.universal_id, authority="GOV", note="n")
    again = registry.supersede(unit.universal_id, authority="GOV", note="n")
    assert again == first
    assert len(registry.supersessions()) == 1


def test_an_active_supersession_may_not_be_rewritten(registry):
    """The whole of what append-only means here: the record stands until a resurrection
    appends the next one."""
    unit = _entity(registry, "rewritten")
    other = _entity(registry, "other")
    registry.supersede(unit.universal_id, authority="GOV")
    with pytest.raises(ExistenceError, match="may not be rewritten"):
        registry.supersede(unit.universal_id, successors=(other.universal_id,), authority="GOV")


def test_a_resurrection_must_name_its_authority(registry):
    unit = _entity(registry, "returning")
    registry.supersede(unit.universal_id, authority="GOV")
    for absent in ("", "   "):
        with pytest.raises(ExistenceError, match="must name its authority"):
            registry.resurrect(unit.universal_id, authority=absent)


def test_a_unit_that_is_not_superseded_cannot_be_resurrected(registry):
    unit = _entity(registry, "never-gone")
    with pytest.raises(ExistenceError, match="not superseded"):
        registry.resurrect(unit.universal_id, authority="GOV")


def test_a_cycle_in_the_specialization_graph_is_refused(registry):
    """Forged: the chain walker is the one traversal every hierarchy uses, so a cycle in
    it would loop forever rather than report."""
    from dataclasses import replace

    first = _classification(registry, "first")
    second = _classification(registry, "second", specializes=first.universal_id)
    looped = replace(first, attributes={ATTR_SPECIALIZES: second.universal_id})
    registry._units[("classification", "first")] = looped
    registry._by_id[first.universal_id] = ("classification", "first")
    with pytest.raises(ExistenceError, match="cycle in the specialization graph"):
        registry.ancestry(first.universal_id)


def test_an_unbound_substrate_names_no_reference_frame(registry):
    assert registry.is_context_bound is False
    assert registry.context == {}
    with pytest.raises(ExistenceError, match="not bound to any reference frame"):
        registry.require_context()


def test_the_seal_is_the_digest_and_both_move_only_with_the_registry(registry):
    before = registry.seal()
    assert before == registry.digest()
    _entity(registry, "moves-the-seal")
    assert registry.seal() != before


def test_the_relationship_view_reads_the_registry_it_was_given(registry, view):
    assert view.registry is registry


def test_a_relationship_type_may_narrow_by_classification(registry, view):
    a, b = _wire(registry, view)
    permitted = _classification(registry, "permitted")
    tagged = _entity(registry, "tagged", classification=permitted.universal_id)
    registry.register(
        ExistenceUnit(
            form="relationship-type",
            key="classified-only",
            title="Classified Only",
            attributes={"source_classifications": (permitted.universal_id,)},
        )
    )
    assert view.relate("classified-only", tagged.universal_id, b, authority="T")
    with pytest.raises(RelationshipAdmissibilityError, match="classification"):
        view.relate("classified-only", a, b, authority="T")


def test_the_view_answers_inbound_and_outbound_neighbourhoods(registry, view):
    a, b = _wire(registry, view)
    c = _entity(registry, "c").universal_id
    view.relate("composes", a, b, authority="T")
    view.relate("composes", b, c, authority="T")
    assert view.neighbours(a) == (b,)
    assert view.inbound(c) == (b,)
    assert view.inbound(a) == ()
    assert view.relationships(source=a, target=b)
    assert view.relationships(source=a, target=c) == ()
    assert view.reachable(a, "composes") == tuple(sorted((b, c)))
    assert view.dangling() == ()


def test_the_view_serialises_an_open_set_with_no_upper_limit(registry, view):
    a, b = _wire(registry, view)
    view.relate("composes", a, b, authority="T")
    document = view.to_document()
    assert document["count"] == 1
    assert document["closed_set"] is False
    assert document["upper_limit"] is None
    assert document["dangling"] == []
    assert len(view.digest()) == 64


# --------------------------------------------------------------------------- #
# the arms a substrate built by this code never reaches                        #
# --------------------------------------------------------------------------- #


def test_a_single_valued_attribute_reads_as_a_one_element_tuple(registry: ExistenceRegistry):
    """A DECLARATION MAY NAME ONE THING WITHOUT WRAPPING IT IN A LIST.

    Every seeded and constructed unit here declares its list-valued attributes as lists, so
    the string arm had no case. Without it a single declared value would be read
    CHARACTER BY CHARACTER — ``"tree"`` becoming four topologies named ``t``, ``r``, ``e``
    and ``e`` — which is the classic shape of this bug and is silent, because the result is
    still a tuple of strings.
    """
    unit = registry.register(
        ExistenceUnit(
            form="entity",
            key="single-valued",
            title="Single valued",
            attributes={"topologies": "tree", "faculties": ["a", "b"], "absent": None},
        )
    )

    assert unit.tuple_attribute("topologies") == ("tree",)
    assert unit.tuple_attribute("faculties") == ("a", "b")
    assert unit.tuple_attribute("absent") == ()


def test_an_unregistered_unit_serialises_without_an_identity(registry: ExistenceRegistry):
    """REGISTRATION IS THE ACT THAT CREATES EXISTENCE, so an unregistered unit has no
    identifier to serialise — and every serialisation test here runs over registered units.

    Emitting ``universal_id`` anyway would have to invent one, and the property raises rather
    than invent. Omitting the key says the unit is not yet in existence, which is the truth
    and is what ``from_document`` reads back.
    """
    unregistered = ExistenceUnit(form="entity", key="not-yet", title="Not yet")

    payload = unregistered.to_dict()

    assert "universal_id" not in payload
    assert payload["identity_kind"] == ""
    with pytest.raises(ExistenceError, match="registration creates existence"):
        _ = unregistered.universal_id

    registered = registry.register(unregistered)
    assert registered.to_dict()["universal_id"] == registered.universal_id


def test_a_bound_substrate_answers_the_context_it_requires(registry: ExistenceRegistry):
    """``require_context`` HAS TWO ANSWERS AND ONLY THE REFUSAL HAD A TEST.

    The fail-closed arm is exercised wherever a measurement needs a reference frame; the
    arm that actually hands the frame back is what every such measurement then reads. It
    returns a COPY, so a caller that mutates what it was given cannot rewrite the substrate's
    binding through the accessor that was supposed to only report it.
    """
    with pytest.raises(ExistenceError, match="not bound to any reference frame"):
        registry.require_context()

    frame = {"frame": "planetary-a1", "resolution_digest": "abc"}
    registry.bind_context(frame)

    answered = registry.require_context()
    assert answered == frame
    answered["frame"] = "mutated"
    assert registry.require_context()["frame"] == "planetary-a1"


def test_a_document_written_before_supersession_history_is_read_losslessly(
    registry: ExistenceRegistry,
):
    """AN OLDER DOCUMENT IS STILL A FAITHFUL RECORD, and the reader that says so had no case.

    Every document this substrate writes today carries ``supersession_history``, so the
    legacy path — current-state summaries only, one entry per subject — was dead even though
    it is the exact shape every registry's own output took before that field existed.
    Refusing such a document would make the substrate unable to read its own history; reading
    it as no history at all would silently drop every supersession it records.

    The same document exercises what the reader must survive: a supersession row that is not
    a mapping or names no subject, and an audit row that is not a mapping. Each is skipped
    rather than raised on, because a reader that aborts on one malformed row loses every
    sound row after it.
    """
    old = _classification(registry, "old")
    new = _classification(registry, "new")
    registry.supersede(
        old.universal_id, successors=[new.universal_id], authority="TEST", note="first"
    )

    document = registry.to_document()
    legacy = {
        **document,
        "supersession_history": "written by a version that had no history field",
        "supersessions": [
            *document["supersessions"],
            {"no_subject": True},
            "not a mapping at all",
        ],
        "audit": [*document["audit"], "not a mapping at all"],
    }

    rebuilt = ExistenceRegistry.from_document(legacy)

    assert [row["subject"] for row in rebuilt.supersessions()] == [old.universal_id]
    assert rebuilt.supersession_history(old.universal_id) == registry.supersessions()
    assert len(rebuilt.audit()) == len(registry.audit())


def test_a_history_whose_records_are_not_a_list_contribute_nothing(registry: ExistenceRegistry):
    """The history field is read as ``subject -> list of records``, and a subject whose
    value is not a list is skipped rather than wrapped.

    Wrapping it would put a string or a mapping into a list the rest of the substrate
    iterates as records, and every reader of that history would then see a malformed row it
    has no way to interpret — reported as history, which is worse than no history.
    """
    old = _classification(registry, "old")
    new = _classification(registry, "new")
    registry.supersede(
        old.universal_id, successors=[new.universal_id], authority="TEST", note="first"
    )

    document = registry.to_document()
    damaged = {
        **document,
        "supersession_history": {
            **document["supersession_history"],
            "UCOS-CLSS-ffffffffffff": "not a list",
        },
    }

    rebuilt = ExistenceRegistry.from_document(damaged)

    assert rebuilt.supersession_history(old.universal_id)
    assert rebuilt.supersession_history("UCOS-CLSS-ffffffffffff") == ()


def test_a_unit_outside_a_relationship_gains_none_of_its_arrangements(
    registry: ExistenceRegistry, view: RelationshipView
):
    """SIMULTANEOUS TOPOLOGIES ARE READ OFF THE RELATIONSHIPS A UNIT IS IN, and the skip for
    the relationships it is NOT in had never run — every case here relates every unit.

    Without it a unit would inherit the arrangements of every relationship in the substrate,
    which turns "which arrangements does this participate in" into "which arrangements
    exist" and makes the answer identical for every unit.
    """
    registry.register(ExistenceUnit(form="topology", key="mesh", title="Mesh"))
    registry.register(
        ExistenceUnit(form="relationship-type", key="links", title="Links", attributes={})
    )
    a = _entity(registry, "a")
    b = _entity(registry, "b")
    bystander = _entity(registry, "bystander")
    view.relate("links", a.universal_id, b.universal_id, authority="T", topologies=("mesh",))

    assert view.topologies_of(a.universal_id) == ("mesh",)
    assert view.topologies_of(bystander.universal_id) == ()


def test_reachability_terminates_when_two_routes_meet(
    registry: ExistenceRegistry, view: RelationshipView
):
    """THE VISITED SET IS INVISIBLE UNTIL A GRAPH OFFERS A SECOND ROUTE INTO A NODE.

    Every relationship graph tested here is a chain or a fan, so no node is ever reached
    twice and the guard never fired. On a diamond it is what stops the shared node — and
    everything below it — from being walked once per route; on a cycle it is what stops the
    walk from not terminating at all. The ANSWER is unchanged either way, which is exactly
    why the guard is invisible without a graph shaped to need it.
    """
    registry.register(
        ExistenceUnit(form="relationship-type", key="flows-to", title="Flows to", attributes={})
    )
    top, left, right, bottom = (_entity(registry, key) for key in ("top", "left", "right", "join"))
    for source, target in (
        (top, left),
        (top, right),
        (left, bottom),
        (right, bottom),
    ):
        view.relate("flows-to", source.universal_id, target.universal_id, authority="T")

    assert set(view.reachable(top.universal_id, "flows-to")) == {
        left.universal_id,
        right.universal_id,
        bottom.universal_id,
    }
