"""EC3-B10-U07 — Governance construct tests (DMC-08 + DGA-01…10 + UDL-13/03/04)."""

from __future__ import annotations

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.governance import (
    ConformanceEntry,
    GovernanceError,
    GovernanceObject,
    GovernedConstructRef,
    make_conformance,
    make_governance,
    policy_ref_for,
)
from data.governance_meta import (
    GOVERNANCE_META_CLASS,
    GOVERNANCE_RELATIONSHIPS,
    GovernanceKind,
    GovernanceState,
    GovernanceVerdict,
)

ENTITY_NAME = "ucos.demo.entity"
GOVERNANCE_NAME = "ucos.demo.governance"
POLICY_REF = policy_ref_for("conformance.udl")


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _conformance():
    return make_conformance((("UDL-02", True), ("UDL-13", True)))


def _governance(**overrides):
    entity = overrides.pop("entity", None) or _entity()
    kwargs = dict(
        kind=overrides.pop("kind", GovernanceKind.CONFORMANCE_RECORD),
        conformance=overrides.pop("conformance", _conformance()),
    )
    kwargs.update(overrides)
    policy_ref = kwargs.pop("policy_ref", POLICY_REF)
    name = kwargs.pop("name", GOVERNANCE_NAME)
    type_tag = kwargs.pop("type_tag", "ucos.core.governance")
    return make_governance(name, type_tag, entity, policy_ref, **kwargs)


def test_governance_is_typed_named_identified_and_classified():
    g = _governance()
    assert g.meta_class == GOVERNANCE_META_CLASS  # V1 (DMC-08)
    assert g.name == GOVERNANCE_NAME  # named
    assert g.type_tag == "ucos.core.governance"  # UDL-03 typed
    assert g.governance_id.startswith("UCOS-GOVERNANCE-")  # UDL-04 identified (ENG-001)
    assert g.kind is GovernanceKind.CONFORMANCE_RECORD  # DXH-08 classified
    assert g.is_classified() is True


def test_governance_governs_entity_by_reference_not_owning():
    entity = _entity()
    g = _governance(entity=entity)
    assert g.governed_construct_id() == entity.entity_id  # DMR-07 governs
    assert g.governs_construct(entity.entity_id) is True
    assert g.absorbs_governed() is False  # DGA-C4 / DMX-02 — referenced, not owned
    ref_dict = g.governed_ref.to_dict()
    assert ref_dict["owned"] is False
    assert ref_dict["binding"] == "DMR-07:governs"


def test_governed_construct_ref_requires_certified_entity():
    with pytest.raises(GovernanceError):  # DMR-07
        GovernedConstructRef.from_entity(object())


def test_governance_is_declarative_and_non_enforcing():
    g = _governance()
    assert g.is_declarative() is True  # DGA-01 / DGA-K2
    assert g.enforces() is False  # DGA-02 / DGA-K2 — enacts nothing
    assert g.grants_access() is False  # DGA-03 / DGA-K5
    assert g.confers_authority() is False  # DGA-03 / DGA-K5
    assert g.is_recorded() is True  # DGA-06 / DGA-K4


def test_governance_binds_policy_by_reference():
    g = _governance()
    assert g.binds_policy_by_reference() is True  # DMR-11 / DGA-07 / DGA-K3
    assert g.policy_ref.startswith("UCOS-POLICY-REF:")


def test_governance_records_conformance_verdicts():
    g = _governance()
    assert g.records_conformance() is True  # DGA-C1
    assert g.conformance_laws() == ("UDL-02", "UDL-13")
    assert g.is_conformant() is True
    assert g.gap_report() == ()  # no violation recorded


def test_governance_gap_report_records_violations_without_enforcing():
    g = _governance(conformance=make_conformance((("UDL-02", True), ("UDL-13", False))))
    assert g.gap_report() == ("UDL-13",)  # DGA-C5 — routed to a Gap Report, not enforced
    assert g.is_conformant() is False
    assert g.enforces() is False  # still enforces nothing


def test_governance_identity_is_deterministic_and_structure_derived():
    a = _governance()
    b = _governance()
    c = _governance(name="different.governance")
    assert a.governance_id == b.governance_id  # same structure → same ENG-001 identity
    assert a.governance_id != c.governance_id  # different name → different identity


def test_governance_is_immutable_objecthood():
    g = _governance()
    with pytest.raises((AttributeError, TypeError)):
        g.name = "other"  # frozen object (ENG-002 objecthood)


def test_unnamed_governance_is_rejected_fail_closed():
    with pytest.raises(GovernanceError):
        _governance(name="")


def test_untyped_governance_is_rejected_fail_closed():
    with pytest.raises(GovernanceError):
        _governance(type_tag="")  # DGA-K1 / UDL-03


def test_conformance_record_without_verdicts_is_rejected_fail_closed():
    with pytest.raises(GovernanceError):  # DGA-C1 — ≥1 law verdict required
        _governance(kind=GovernanceKind.CONFORMANCE_RECORD, conformance=())


def test_policy_object_kind_allows_empty_conformance():
    g = _governance(kind=GovernanceKind.POLICY_OBJECT, conformance=())
    assert g.records_conformance() is True  # not a Conformance-Record → trivially satisfied
    assert g.kind is GovernanceKind.POLICY_OBJECT


def test_conformance_entry_requires_named_law_and_bool_verdict():
    with pytest.raises(GovernanceError):
        ConformanceEntry(law_id="", satisfied=True)  # DGA-C1
    with pytest.raises(GovernanceError):
        ConformanceEntry(law_id="UDL-02", satisfied="yes")  # decidable verdict


def test_duplicate_conformance_law_is_rejected():
    with pytest.raises(GovernanceError):  # DGA-C1
        _governance(conformance=make_conformance((("UDL-02", True), ("UDL-02", False))))


def test_governance_naming_a_policy_technology_is_rejected_fail_closed():
    # UDL-13 / DGA-09 / DGA-K5 — evaluative record only; names no engine/IAM/vendor.
    with pytest.raises(GovernanceError):
        _governance(name="open policy agent")
    with pytest.raises(GovernanceError):
        _governance(type_tag="casbin.rbac")
    with pytest.raises(GovernanceError):
        _governance(steward="apache ranger")


def test_relationships_are_within_dmr_closure():
    g = _governance()
    assert set(g.meta_relationships()) <= set(GOVERNANCE_RELATIONSHIPS)  # V2
    assert g.meta_relationships() == ("DMR-07", "DMR-10", "DMR-11")


def test_stewardship_is_recorded_descriptor_not_a_power():
    g = _governance(steward="data.steward.record")
    assert g.steward == "data.steward.record"  # DGA-05 / DGA-C4
    assert g.stewardship_is_descriptor() is True
    assert g.confers_authority() is False


def test_verdict_is_a_decidable_governance_judgment():
    g = _governance(verdict=GovernanceVerdict.NON_CONFORMANT)
    assert g.verdict is GovernanceVerdict.NON_CONFORMANT  # DGA-06 / DOV-08
    payload = g.to_dict()
    assert payload["verdict"] == "non-conformant"


def test_supersession_lineage_is_recorded():
    g = _governance(version="2.0.0", supersedes="UCOS-GOVERNANCE-old-0000000000000000")
    assert g.version == "2.0.0"  # DGA-08
    assert g.supersedes == "UCOS-GOVERNANCE-old-0000000000000000"  # DGA-C3 append-only
    with pytest.raises(GovernanceError):
        _governance(version="")


def test_founding_graph_is_acyclic():
    g = _governance()
    assert g.is_founding_acyclic() is True  # V4 / DMK-03


def test_invalid_policy_ref_is_rejected():
    with pytest.raises(GovernanceError):  # DMR-11 / DGA-K3 — must bind a RUNTIME policy reference
        _governance(policy_ref="not-a-policy-ref")


def test_subject_without_certified_construct_id_is_rejected():
    bad_ref = GovernedConstructRef(
        construct_id="NOT-A-CONSTRUCT",
        structure_digest="a" * 64,
        name="x",
        type_tag="t",
        meta_class="DMC-02",
    )
    with pytest.raises(GovernanceError):  # DMR-07
        make_governance(
            "g", "ucos.core.governance", bad_ref, POLICY_REF, conformance=_conformance()
        )


def test_subject_without_structural_digest_is_rejected():
    bad_ref = GovernedConstructRef(
        construct_id="UCOS-ENTITY-x-0000000000000000",
        structure_digest="short",  # not a 64-hex digest
        name="x",
        type_tag="t",
        meta_class="DMC-02",
    )
    with pytest.raises(GovernanceError):  # UDL-06
        make_governance(
            "g", "ucos.core.governance", bad_ref, POLICY_REF, conformance=_conformance()
        )


def test_non_governed_ref_is_rejected():
    with pytest.raises(GovernanceError):  # DMR-07
        GovernanceObject(
            name="g",
            type_tag="ucos.core.governance",
            kind=GovernanceKind.CONFORMANCE_RECORD,
            governed_ref="not-a-ref",
            policy_ref=POLICY_REF,
            conformance=_conformance(),
        )


def test_non_governance_kind_is_rejected():
    with pytest.raises(GovernanceError):  # DXH-08 / DMR-09
        _governance(kind="Conformance-Record")  # str, not GovernanceKind


def test_non_conformance_tuple_is_rejected():
    # Constructed directly (bypassing make_governance's tuple() coercion) to exercise the guard.
    ref = GovernedConstructRef.from_entity(_entity())
    with pytest.raises(GovernanceError):  # DGA-C1
        GovernanceObject(
            name="g",
            type_tag="ucos.core.governance",
            kind=GovernanceKind.CONFORMANCE_RECORD,
            governed_ref=ref,
            policy_ref=POLICY_REF,
            conformance=[ConformanceEntry("UDL-02", True)],  # list, not tuple
        )


def test_non_conformance_entry_member_is_rejected():
    with pytest.raises(GovernanceError):  # DGA-C1
        _governance(conformance=("not-an-entry",))


def test_non_verdict_is_rejected():
    with pytest.raises(GovernanceError):  # DGA-06
        _governance(verdict="conformant")  # str, not GovernanceVerdict


def test_non_string_steward_is_rejected():
    with pytest.raises(GovernanceError):  # DGA-05
        _governance(steward=123)


def test_non_state_state_is_rejected():
    with pytest.raises(GovernanceError):  # UDL-12
        _governance(state="DEFINED")  # str, not GovernanceState


def test_non_string_supersedes_is_rejected():
    with pytest.raises(GovernanceError):  # DGA-C3
        _governance(supersedes=123)


def test_non_constitutive_and_no_secret():
    g = _governance()
    assert g.confers_authority() is False  # UDL-15 / DGA-09 / C7
    assert g.redefines_el1() is False  # UDL-02 / DMI-05
    assert g.selects_technology() is False  # UDL-13 / DGA-K5 (evaluative record)
    assert g.embeds_secret() is False


def test_secret_bearing_governance_is_detected():
    leaky = _governance(name="password")
    assert leaky.embeds_secret() is True  # UDL-15 / RR-07


def test_governance_to_dict_records_substrate_reuse():
    g = _governance()
    payload = g.to_dict()
    assert payload["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005"]
    assert payload["meta_class"] == "DMC-08"
    assert payload["absorbs_governed"] is False
    assert payload["declarative"] is True
    assert payload["enforces"] is False
    assert payload["grants_access"] is False
    assert payload["recorded"] is True
    assert payload["names_technology"] is False
    assert payload["binds_policy_by_reference"] is True


def test_governance_type_is_the_realized_construct():
    assert isinstance(_governance(), GovernanceObject)


def test_progression_is_forward_only():
    g = _governance(state=GovernanceState.DEFINED)
    active = g.transition(GovernanceState.ACTIVE)
    assert active.state is GovernanceState.ACTIVE  # UDL-12 forward-only
    with pytest.raises(GovernanceError):
        active.transition(GovernanceState.DEFINED)  # backward rejected


def test_transition_to_non_state_is_rejected():
    g = _governance()
    with pytest.raises(GovernanceError):  # UDL-12
        g.transition("ACTIVE")  # str, not GovernanceState


def test_make_conformance_builds_entries():
    entries = make_conformance((("UDL-02", True), ("UDL-13", False)))
    assert len(entries) == 2
    assert all(isinstance(e, ConformanceEntry) for e in entries)
    assert entries[1].law_id == "UDL-13"
    assert entries[1].satisfied is False


def test_policy_ref_for_builds_prefixed_reference():
    ref = policy_ref_for("conformance.udl")
    assert ref == "UCOS-POLICY-REF:conformance.udl"


def test_governance_selects_no_technology():
    g = _governance()
    assert g.names_technology() is False  # UDL-13 / DGA-09 / DGA-K5
    assert g.selects_technology() is False
