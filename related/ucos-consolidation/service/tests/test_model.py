"""EC3-B11-U11 — Universal Service Meta-Model construct tests (USM + SMI-01…07 + SERVICE-005)."""

from __future__ import annotations

import pytest

from service.model import (
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
from service.model_meta import (
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
    assert m.meta_class == MODEL_CLASS  # USM (not a concern meta-class)
    assert m.name == MODEL_NAME
    assert m.type_tag == MODEL_TYPE  # USL-03 typed
    assert m.model_id.startswith("UCOS-METAMODEL-")  # USL-04 identified (ENG-001)
    assert len(m.structure_digest) == 64


def test_metamodel_id_is_deterministic():
    assert a_model().model_id == a_model().model_id


def test_metamodel_meta_class_is_usm_not_a_concern_class():
    assert a_model().meta_class not in META_CLASSES


# ---------------------------------------------------------------------------
# SMI-01 closure / SMI-02 relationship closure / SMI-03 totality
# ---------------------------------------------------------------------------


def test_metamodel_declares_meta_class_closure():
    m = a_model()
    assert m.meta_classes() == tuple(sorted(META_CLASSES))  # SMI-01
    assert m.declares_closure() is True


def test_metamodel_declares_relationship_closure():
    m = a_model()
    assert m.meta_relationships() == tuple(sorted(META_RELATIONSHIPS))  # SMI-02
    assert m.declares_relationship_closure() is True


def test_metamodel_is_total_over_ontology():
    m = a_model()
    assert m.modelled_entities() == tuple(sorted(ONTOLOGY_ENTITIES))  # SMI-03 entities
    assert m.modelled_relationships() == tuple(sorted(ONTOLOGY_RELATIONSHIPS))  # SMI-03 relations
    assert m.is_total() is True


# ---------------------------------------------------------------------------
# SMI-04 acyclicity / SMI-05 reuse / integration / map
# ---------------------------------------------------------------------------


def test_metamodel_founding_graph_is_acyclic():
    assert a_model().is_founding_acyclic() is True  # SMI-04 / SMK-03


def test_metamodel_members_certified_and_map_resolves():
    m = a_model()
    assert m.members_certified() is True  # integration
    assert m.map_resolves() is True  # §9
    assert m.reuses_by_reference() is True  # SMI-05


def test_metamodel_non_projection_and_non_constitutive():
    m = a_model()
    assert m.is_non_projection() is True  # SMI-07
    assert m.is_non_constitutive() is True  # SMI-06
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
    assert tainted.embeds_secret() is True  # USL-15 / RR-07 (caught at validation)
    assert m.embeds_secret() is False


# ---------------------------------------------------------------------------
# Members / edges structure
# ---------------------------------------------------------------------------


def test_member_resolves_and_to_dict():
    member = _member_from_spec(MEMBER_SPECS[1], _cert("SMC-02"))
    assert member.resolves() is True
    d = member.to_dict()
    assert d["meta_class"] == "SMC-02"
    assert d["owned"] is False
    assert d["resolves"] is True


@pytest.mark.parametrize(
    "member",
    [
        MetaClassMember("SMC-99", "X", "SOE-02", "SXH-02", "U", _cert("SMC-99")),  # not a class
        MetaClassMember("SMC-02", "X", "SOE-02", "SXH-02", "U", "NOPREFIX-abcdef0123456789"),
        MetaClassMember("SMC-02", "X", "SOE-02", "SXH-02", "U", "UCOS-CERT-SMC-02-short"),
        MetaClassMember("SMC-02", "X", "SOE-02", "SXH-02", "U", "UCOS-CERT-SMC-02-" + "z" * 16),
    ],
)
def test_member_does_not_resolve(member):
    assert member.resolves() is False


def test_edge_predicates_and_to_dict():
    founding = MetaRelationshipEdge("SMR-02", "bound-by", "SOR-02", "SMC-05", "SMC-03")
    reference = MetaRelationshipEdge("SMR-11", "behaves-as", "SOR-11", "SMC-01", "RL-F2")
    assert founding.is_founding() is True
    assert founding.target_is_foundation() is False
    assert reference.is_founding() is False
    assert reference.target_is_foundation() is True
    classes = frozenset(META_CLASSES)
    assert founding.resolves(classes) is True
    assert reference.resolves(classes) is True  # RL-F2 is a foundation target
    assert MetaRelationshipEdge("SMR-02", "x", "SOR-02", "SMC-99", "SMC-03").resolves(classes) is (
        False
    )
    d = founding.to_dict()
    assert d["founding"] is True and d["target_is_foundation"] is False


def test_build_edges_covers_all_thirteen_and_foundation_targets():
    edges = build_edges()
    assert len(edges) == 13
    assert {e.relationship for e in edges} == set(META_RELATIONSHIPS)
    assert {e.target for e in edges if e.target_is_foundation()} == set(FOUNDATION_TARGETS)


# ---------------------------------------------------------------------------
# Founding-cycle detector (SMI-04) — direct coverage of all branches
# ---------------------------------------------------------------------------


def test_founding_cycle_detector_linear_acyclic():
    edges = (
        MetaRelationshipEdge("SMR-04", "provides", "SOR-04", "A", "B"),
        MetaRelationshipEdge("SMR-05", "composes", "SOR-05", "A", "C"),
    )
    assert _has_founding_cycle(edges) is False


def test_founding_cycle_detector_detects_cycle():
    edges = (
        MetaRelationshipEdge("SMR-04", "provides", "SOR-04", "A", "B"),
        MetaRelationshipEdge("SMR-02", "bound-by", "SOR-02", "B", "A"),  # back-edge
    )
    assert _has_founding_cycle(edges) is True


def test_founding_cycle_detector_diamond_is_acyclic():
    # Diamond A→B, A→C, B→D, C→D exercises the already-visited (BLACK) skip branch.
    edges = (
        MetaRelationshipEdge("SMR-04", "provides", "SOR-04", "A", "B"),
        MetaRelationshipEdge("SMR-04", "provides", "SOR-04", "A", "C"),
        MetaRelationshipEdge("SMR-04", "provides", "SOR-04", "B", "D"),
        MetaRelationshipEdge("SMR-05", "composes", "SOR-05", "C", "D"),
    )
    assert _has_founding_cycle(edges) is False


def test_founding_cycle_detector_ignores_non_founding_edges():
    edges = (
        MetaRelationshipEdge("SMR-01", "realizes", "SOR-01", "A", "B"),
        MetaRelationshipEdge("SMR-01", "realizes", "SOR-01", "B", "A"),  # peer cycle: not founding
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
    assert len(d["edges"]) == 13
    assert d["substrate_refs"][0] == "ENG-001"


# ---------------------------------------------------------------------------
# Lifecycle (USL-12, forward-only)
# ---------------------------------------------------------------------------


def test_metamodel_lifecycle_is_forward_only():
    m = a_model()
    contracted = m.transition(ModelState.CONTRACTED)
    assert contracted.state is ModelState.CONTRACTED
    with pytest.raises(MetaModelError):  # USL-12 — no backward transition
        contracted.transition(ModelState.DEFINED)


def test_metamodel_transition_rejects_non_state():
    with pytest.raises(MetaModelError):
        a_model().transition("CONTRACTED")


# ---------------------------------------------------------------------------
# Fail-closed construction (SMI-01…07)
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
    # replace SMC-10 with a duplicate SMC-01 → not exactly SMC-01…10 (SMI-01)
    dup = _member_from_spec(MEMBER_SPECS[0], _cert("SMC-01"))
    bad = (*members[:-1], dup)
    with pytest.raises(MetaModelError):
        a_raw_model(members=bad)


def test_rejects_member_not_resolving():
    members = list(valid_members())
    members[0] = MetaClassMember("SMC-01", "Service", "SOE-01", "SXH-01", "U01", "bad-cert-id")
    with pytest.raises(MetaModelError):  # SMI-05
        a_raw_model(members=tuple(members))


def test_rejects_relationship_not_closed():
    edges = build_edges()
    dup = edges[0]  # duplicate SMR-01, drop SMR-13 → not exactly SMR-01…13 (SMI-02)
    bad = (*edges[:-1], dup)
    with pytest.raises(MetaModelError):
        a_raw_model(edges=bad)


def test_rejects_entity_totality_violation():
    members = list(valid_members())
    spec = MEMBER_SPECS[0]  # SMC-01
    members[0] = MetaClassMember(spec[0], spec[1], "SOE-99", spec[3], spec[4], _cert(spec[0]))
    with pytest.raises(MetaModelError):  # SMI-03 entities
        a_raw_model(members=tuple(members))


def test_rejects_relationship_totality_violation():
    edges = list(build_edges())
    e = edges[0]
    edges[0] = MetaRelationshipEdge(e.relationship, e.name, "SOR-99", e.source, e.target)
    with pytest.raises(MetaModelError):  # SMI-03 relationships
        a_raw_model(edges=tuple(edges))


def test_rejects_edge_not_resolving():
    edges = list(build_edges())
    e = edges[0]
    edges[0] = MetaRelationshipEdge(e.relationship, e.name, e.models, "SMC-99", e.target)
    with pytest.raises(MetaModelError):  # SMI-05 edge resolution
        a_raw_model(edges=tuple(edges))


def test_rejects_founding_cycle():
    edges = list(build_edges())
    # rewire SMR-02 (bound-by) to point SMC-05 → SMC-01, creating a founding cycle with
    # SMR-04 (provides) SMC-01 → SMC-05.
    for i, e in enumerate(edges):
        if e.relationship == "SMR-02":
            edges[i] = MetaRelationshipEdge("SMR-02", e.name, "SOR-02", "SMC-05", "SMC-01")
    with pytest.raises(MetaModelError):  # SMI-04 / SMK-03
        a_raw_model(edges=tuple(edges))


def test_rejects_bad_state():
    with pytest.raises(MetaModelError):  # USL-12
        a_raw_model(state="DEFINED")


def test_rejects_empty_version():
    with pytest.raises(MetaModelError):
        a_raw_model(version=" ")


def test_rejects_bad_supersedes():
    with pytest.raises(MetaModelError):
        a_raw_model(supersedes=123)


def test_rejects_technology_marker():
    with pytest.raises(MetaModelError):  # SMI-06 / SMK-08 — names a service technology
        a_raw_model(type_tag="ucos.core.grpc.metamodel")


def test_make_metamodel_requires_all_ten_certification_ids():
    ids = cert_ids()
    del ids["SMC-10"]
    with pytest.raises(MetaModelError):  # SMI-01 — integrates all ten
        make_metamodel(MODEL_NAME, MODEL_TYPE, ids)


def test_supersedes_and_version_recorded():
    m = a_model(version="2.0.0", supersedes="UCOS-METAMODEL-old")
    assert m.version == "2.0.0"
    assert m.supersedes == "UCOS-METAMODEL-old"
