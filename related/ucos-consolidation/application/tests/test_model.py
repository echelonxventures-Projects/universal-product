"""EC3-B12-U11 — Universal Application Meta-Model construct tests (UAM + AMI-01…07 + APPLICATION-005)."""

from __future__ import annotations

import pytest

from application.model import (
    CERT_ID_PREFIX,
    MetaClassMember,
    MetaModel,
    MetaModelError,
    MetaRelationshipEdge,
    _has_founding_cycle,
    _member_from_spec,
    build_edges,
    make_metamodel,
)
from application.model_meta import (
    FOUNDATION_TARGETS,
    MEMBER_SPECS,
    META_CLASSES,
    META_RELATIONSHIPS,
    MODEL_CLASS,
    ONTOLOGY_ENTITIES,
    ONTOLOGY_RELATIONSHIPS,
    ModelState,
)

MODEL_NAME = "ucos.test.metamodel"
MODEL_TYPE = "ucos.core.metamodel"


def _cert(mc: str) -> str:
    return f"{CERT_ID_PREFIX}{mc}-{'a' * 16}"


def cert_ids() -> dict[str, str]:
    return {spec[0]: _cert(spec[0]) for spec in MEMBER_SPECS}


def valid_members() -> tuple[MetaClassMember, ...]:
    return tuple(_member_from_spec(spec, _cert(spec[0])) for spec in MEMBER_SPECS)


def a_model(**overrides) -> MetaModel:
    ids = overrides.pop("certification_ids", cert_ids())
    return make_metamodel(MODEL_NAME, MODEL_TYPE, ids, **overrides)


def a_raw_model(**overrides) -> MetaModel:
    kwargs = dict(
        name=MODEL_NAME,
        type_tag=MODEL_TYPE,
        members=valid_members(),
        edges=build_edges(),
    )
    kwargs.update(overrides)
    return MetaModel(**kwargs)


# ---------------------------------------------------------------------------
# Identity / typing / classification
# ---------------------------------------------------------------------------


def test_metamodel_is_typed_named_identified_and_classed():
    m = a_model()
    assert m.meta_class == MODEL_CLASS  # UAM (not a concern meta-class)
    assert m.name == MODEL_NAME
    assert m.type_tag == MODEL_TYPE  # UAL-03 typed
    assert m.model_id.startswith("UCOS-METAMODEL-")  # UAL-04 identified (ENG-001)
    assert len(m.structure_digest) == 64


def test_metamodel_id_is_deterministic():
    assert a_model().model_id == a_model().model_id


def test_metamodel_meta_class_is_uam_not_a_concern_class():
    assert a_model().meta_class not in META_CLASSES


# ---------------------------------------------------------------------------
# AMI-01 closure / AMI-02 relationship closure / AMI-03 totality
# ---------------------------------------------------------------------------


def test_metamodel_declares_meta_class_closure():
    m = a_model()
    assert m.meta_classes() == tuple(sorted(META_CLASSES))  # AMI-01
    assert m.declares_closure() is True


def test_metamodel_declares_relationship_closure():
    m = a_model()
    assert m.meta_relationships() == tuple(sorted(META_RELATIONSHIPS))  # AMI-02
    assert m.declares_relationship_closure() is True


def test_metamodel_is_total_over_ontology():
    m = a_model()
    assert m.modelled_entities() == tuple(sorted(ONTOLOGY_ENTITIES))  # AMI-03 entities
    assert m.modelled_relationships() == tuple(sorted(ONTOLOGY_RELATIONSHIPS))  # AMI-03 relations
    assert m.is_total() is True


# ---------------------------------------------------------------------------
# AMI-04 acyclicity / AMI-05 reuse / integration / map
# ---------------------------------------------------------------------------


def test_metamodel_founding_graph_is_acyclic():
    assert a_model().is_founding_acyclic() is True  # AMI-04 / AMK-03


def test_metamodel_members_certified_and_map_resolves():
    m = a_model()
    assert m.members_certified() is True  # integration
    assert m.map_resolves() is True  # §9
    assert m.reuses_by_reference() is True  # AMI-05


def test_metamodel_non_projection_and_non_constitutive():
    m = a_model()
    assert m.is_non_projection() is True  # AMI-07
    assert m.is_non_constitutive() is True  # AMI-06
    assert m.confers_authority() is False
    assert m.names_technology() is False
    assert m.selects_technology() is False
    assert m.embeds_secret() is False
    assert m.redefines_el1() is False


def test_metamodel_embeds_secret_detected():
    m = a_model(certification_ids=cert_ids())
    tainted = MetaModel(
        name="ucos.test.password.metamodel",  # secret marker in canonical core
        type_tag=MODEL_TYPE,
        members=valid_members(),
        edges=build_edges(),
    )
    assert tainted.embeds_secret() is True  # UAL-15 / RR-07 (caught at validation)
    assert m.embeds_secret() is False


# ---------------------------------------------------------------------------
# Members / edges structure
# ---------------------------------------------------------------------------


def test_member_resolves_and_to_dict():
    member = _member_from_spec(MEMBER_SPECS[1], _cert("AMC-02"))
    assert member.resolves() is True
    d = member.to_dict()
    assert d["meta_class"] == "AMC-02"
    assert d["owned"] is False
    assert d["resolves"] is True


@pytest.mark.parametrize(
    "member",
    [
        MetaClassMember("AMC-99", "X", "AOE-02", "AXH-02", "U", _cert("AMC-99")),  # not a class
        MetaClassMember("AMC-02", "X", "AOE-02", "AXH-02", "U", "NOPREFIX-abcdef0123456789"),
        MetaClassMember("AMC-02", "X", "AOE-02", "AXH-02", "U", "UCOS-CERT-AMC-02-short"),
        MetaClassMember("AMC-02", "X", "AOE-02", "AXH-02", "U", "UCOS-CERT-AMC-02-" + "z" * 16),
    ],
)
def test_member_does_not_resolve(member):
    assert member.resolves() is False


def test_edge_predicates_and_to_dict():
    founding = MetaRelationshipEdge("AMR-02", "composed-of", "AOR-02", "AMC-01", "AMC-03")
    reference = MetaRelationshipEdge("AMR-11", "behaves-as", "AOR-11", "AMC-01", "RL-F2")
    assert founding.is_founding() is True
    assert founding.target_is_foundation() is False
    assert reference.is_founding() is False
    assert reference.target_is_foundation() is True
    classes = frozenset(META_CLASSES)
    assert founding.resolves(classes) is True
    assert reference.resolves(classes) is True  # RL-F2 is a foundation target
    assert MetaRelationshipEdge("AMR-02", "x", "AOR-02", "AMC-99", "AMC-03").resolves(classes) is (
        False
    )
    d = founding.to_dict()
    assert d["founding"] is True and d["target_is_foundation"] is False


def test_build_edges_covers_all_fourteen_and_foundation_targets():
    edges = build_edges()
    assert len(edges) == 14
    assert {e.relationship for e in edges} == set(META_RELATIONSHIPS)
    assert {e.target for e in edges if e.target_is_foundation()} == set(FOUNDATION_TARGETS)


# ---------------------------------------------------------------------------
# Founding-cycle detector (AMI-04) — direct coverage of all branches
# ---------------------------------------------------------------------------


def test_founding_cycle_detector_linear_acyclic():
    edges = (
        MetaRelationshipEdge("AMR-02", "composed-of", "AOR-02", "A", "B"),
        MetaRelationshipEdge("AMR-03", "groups", "AOR-03", "A", "C"),
    )
    assert _has_founding_cycle(edges) is False


def test_founding_cycle_detector_detects_cycle():
    edges = (
        MetaRelationshipEdge("AMR-02", "composed-of", "AOR-02", "A", "B"),
        MetaRelationshipEdge("AMR-03", "groups", "AOR-03", "B", "A"),  # back-edge
    )
    assert _has_founding_cycle(edges) is True


def test_founding_cycle_detector_diamond_is_acyclic():
    # Diamond A→B, A→C, B→D, C→D exercises the already-visited (BLACK) skip branch.
    edges = (
        MetaRelationshipEdge("AMR-02", "composed-of", "AOR-02", "A", "B"),
        MetaRelationshipEdge("AMR-02", "composed-of", "AOR-02", "A", "C"),
        MetaRelationshipEdge("AMR-03", "groups", "AOR-03", "B", "D"),
        MetaRelationshipEdge("AMR-05", "engaged-through", "AOR-05", "C", "D"),
    )
    assert _has_founding_cycle(edges) is False


def test_founding_cycle_detector_ignores_non_founding_edges():
    edges = (
        MetaRelationshipEdge("AMR-01", "delivers", "AOR-01", "A", "B"),
        MetaRelationshipEdge("AMR-01", "delivers", "AOR-01", "B", "A"),  # peer cycle: not founding
    )
    assert _has_founding_cycle(edges) is False


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def test_metamodel_to_dict_is_complete():
    d = a_model().to_dict()
    assert d["model_class"] == MODEL_CLASS
    assert d["declares_closure"] is True
    assert d["declares_relationship_closure"] is True
    assert d["is_total"] is True
    assert d["founding_acyclic"] is True
    assert d["members_certified"] is True
    assert d["map_resolves"] is True
    assert d["non_constitutive"] is True
    assert len(d["members"]) == 10
    assert len(d["edges"]) == 14
    assert d["substrate_refs"][0] == "ENG-001"


# ---------------------------------------------------------------------------
# Lifecycle (UAL-12, forward-only)
# ---------------------------------------------------------------------------


def test_metamodel_lifecycle_is_forward_only():
    m = a_model()
    composed = m.transition(ModelState.COMPOSED)
    assert composed.state is ModelState.COMPOSED
    with pytest.raises(MetaModelError):  # UAL-12 — no backward transition
        composed.transition(ModelState.DEFINED)


def test_metamodel_transition_rejects_non_state():
    with pytest.raises(MetaModelError):
        a_model().transition("COMPOSED")


# ---------------------------------------------------------------------------
# Fail-closed construction (AMI-01…07)
# ---------------------------------------------------------------------------


def test_rejects_empty_name():
    with pytest.raises(MetaModelError):
        a_raw_model(name="  ")


def test_rejects_empty_type_tag():
    with pytest.raises(MetaModelError):
        a_raw_model(type_tag="")


def test_rejects_members_not_tuple():
    with pytest.raises(MetaModelError):
        a_raw_model(members=list(valid_members()))


def test_rejects_edges_not_tuple():
    with pytest.raises(MetaModelError):
        a_raw_model(edges=list(build_edges()))


def test_rejects_member_wrong_type():
    bad = (*valid_members()[:-1], object())
    with pytest.raises(MetaModelError):
        a_raw_model(members=bad)


def test_rejects_edge_wrong_type():
    bad = (*build_edges()[:-1], object())
    with pytest.raises(MetaModelError):
        a_raw_model(edges=bad)


def test_rejects_meta_class_not_closed_duplicate():
    members = valid_members()
    # replace AMC-10 with a duplicate AMC-01 → not exactly AMC-01…10 (AMI-01)
    dup = _member_from_spec(MEMBER_SPECS[0], _cert("AMC-01"))
    bad = (*members[:-1], dup)
    with pytest.raises(MetaModelError):
        a_raw_model(members=bad)


def test_rejects_member_not_resolving():
    members = list(valid_members())
    members[0] = MetaClassMember("AMC-01", "Application", "AOE-01", "AXH-01", "U01", "bad-cert-id")
    with pytest.raises(MetaModelError):  # AMI-05
        a_raw_model(members=tuple(members))


def test_rejects_relationship_not_closed():
    edges = build_edges()
    dup = edges[0]  # duplicate AMR-01, drop AMR-14 → not exactly AMR-01…14 (AMI-02)
    bad = (*edges[:-1], dup)
    with pytest.raises(MetaModelError):
        a_raw_model(edges=bad)


def test_rejects_entity_totality_violation():
    members = list(valid_members())
    spec = MEMBER_SPECS[0]  # AMC-01
    members[0] = MetaClassMember(spec[0], spec[1], "AOE-99", spec[3], spec[4], _cert(spec[0]))
    with pytest.raises(MetaModelError):  # AMI-03 entities
        a_raw_model(members=tuple(members))


def test_rejects_relationship_totality_violation():
    edges = list(build_edges())
    e = edges[0]
    edges[0] = MetaRelationshipEdge(e.relationship, e.name, "AOR-99", e.source, e.target)
    with pytest.raises(MetaModelError):  # AMI-03 relationships
        a_raw_model(edges=tuple(edges))


def test_rejects_edge_not_resolving():
    edges = list(build_edges())
    e = edges[0]
    edges[0] = MetaRelationshipEdge(e.relationship, e.name, e.models, "AMC-99", e.target)
    with pytest.raises(MetaModelError):  # AMI-05 edge resolution
        a_raw_model(edges=tuple(edges))


def test_rejects_founding_cycle():
    edges = list(build_edges())
    # rewire AMR-05 (engaged-through) to point AMC-04 → AMC-03, creating a founding cycle with
    # AMR-03 (groups) AMC-03 → AMC-04.
    for i, e in enumerate(edges):
        if e.relationship == "AMR-05":
            edges[i] = MetaRelationshipEdge("AMR-05", e.name, "AOR-05", "AMC-04", "AMC-03")
    with pytest.raises(MetaModelError):  # AMI-04 / AMK-03
        a_raw_model(edges=tuple(edges))


def test_rejects_bad_state():
    with pytest.raises(MetaModelError):  # UAL-12
        a_raw_model(state="DEFINED")


def test_rejects_empty_version():
    with pytest.raises(MetaModelError):
        a_raw_model(version=" ")


def test_rejects_bad_supersedes():
    with pytest.raises(MetaModelError):
        a_raw_model(supersedes=123)


def test_rejects_technology_marker():
    with pytest.raises(MetaModelError):  # AMI-06 / AMK-08 — names an application technology
        a_raw_model(type_tag="ucos.core.react.metamodel")


def test_make_metamodel_requires_all_ten_certification_ids():
    ids = cert_ids()
    del ids["AMC-10"]
    with pytest.raises(MetaModelError):  # AMI-01 — integrates all ten
        make_metamodel(MODEL_NAME, MODEL_TYPE, ids)


def test_supersedes_and_version_recorded():
    m = a_model(version="2.0.0", supersedes="UCOS-METAMODEL-old")
    assert m.version == "2.0.0"
    assert m.supersedes == "UCOS-METAMODEL-old"
