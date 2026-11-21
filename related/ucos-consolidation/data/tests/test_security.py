"""EC3-B10-U09 — Security construct tests (DMC-10 + DZA-01…10 + UDL-14/03/04)."""

from __future__ import annotations

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.security import (
    ClassificationEntry,
    ClassifiedConstructRef,
    SecurityError,
    SecurityObject,
    make_classifications,
    make_security,
    policy_ref_for,
)
from data.security_meta import (
    SECURITY_META_CLASS,
    SECURITY_RELATIONSHIPS,
    SecurityKind,
    SecurityState,
    SecurityVerdict,
)

ENTITY_NAME = "ucos.demo.entity"
SECURITY_NAME = "ucos.demo.security"
POLICY_REF = policy_ref_for("security.udl")


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _classifications(dim="sensitivity"):
    return make_classifications(((dim, True, 1),))


def _security(**overrides):
    entity = overrides.pop("entity", None) or _entity()
    kind = overrides.pop("kind", SecurityKind.CLASSIFICATION_LABEL)
    kwargs = dict(kind=kind, classifications=overrides.pop("classifications", _classifications()))
    kwargs.update(overrides)
    policy_ref = kwargs.pop("policy_ref", POLICY_REF)
    name = kwargs.pop("name", SECURITY_NAME)
    type_tag = kwargs.pop("type_tag", "ucos.core.security")
    return make_security(name, type_tag, entity, policy_ref, **kwargs)


def test_security_is_typed_named_identified_and_classified():
    s = _security()
    assert s.meta_class == SECURITY_META_CLASS  # V1 (DMC-10)
    assert s.name == SECURITY_NAME  # named
    assert s.type_tag == "ucos.core.security"  # UDL-03 typed
    assert s.security_id.startswith("UCOS-SECURITY-")  # UDL-04 identified (ENG-001)
    assert s.kind is SecurityKind.CLASSIFICATION_LABEL  # DXH-10 classified
    assert s.is_classified() is True


def test_security_classifies_entity_by_reference_not_owning():
    entity = _entity()
    s = _security(entity=entity)
    assert s.classified_construct_id() == entity.entity_id  # DMR-09 classifies
    assert s.classifies_construct(entity.entity_id) is True
    assert s.absorbs_classified() is False  # DZA-C3 / DMX-02 — referenced, not owned
    ref_dict = s.classified_ref.to_dict()
    assert ref_dict["owned"] is False
    assert ref_dict["binding"] == "DMR-09:classifies"


def test_classified_construct_ref_requires_certified_entity():
    with pytest.raises(SecurityError):  # DMR-09
        ClassifiedConstructRef.from_entity(object())


def test_security_is_evaluative_and_non_enforcing():
    s = _security()
    assert s.is_evaluative() is True  # DZA-01 / DZA-K2
    assert s.enforces() is False  # DZA-01 / DZA-C2 — enacts nothing
    assert s.grants_access() is False  # DZA-01 / DZA-K5
    assert s.confers_authority() is False  # DZA-09 / DZA-K5
    assert s.is_recorded() is True  # DZA-04 / DZA-K4


def test_security_is_dimensioned_single_facet():
    s = _security()
    assert s.is_dimensioned() is True  # DZA-02
    assert s.classified_dimension() == "sensitivity"  # DXC-02 single facet
    assert s.classified_dimensions() == ("sensitivity",)


def test_security_binds_policy_by_reference():
    s = _security()
    assert s.binds_policy_by_reference() is True  # DMR-11 / DZA-06 / DZA-K3
    assert s.policy_ref.startswith("UCOS-POLICY-REF:")


def test_security_enforcement_is_by_reference():
    s = _security()
    assert s.enforcement_by_reference() is True  # DZA-03 / DZA-C3
    assert s.to_dict()["enforcement_by_reference"] is True


def test_security_records_classification_verdicts():
    s = _security()
    assert s.records_classification() is True  # DZA-C1
    assert s.classified_dimensions() == ("sensitivity",)
    assert s.passes() is True
    assert s.gap_report() == ()  # no deficiency recorded


def test_security_gap_report_records_deficiencies_without_enforcing():
    s = _security(classifications=make_classifications((("sensitivity", False, 0),)))
    assert s.gap_report() == ("sensitivity",)  # DZA-C1 — recorded, not enforced
    assert s.passes() is False
    assert s.enforces() is False  # still enforces nothing


def test_confidentiality_record_classifies_confidentiality():
    s = _security(
        kind=SecurityKind.CONFIDENTIALITY_RECORD,
        classifications=_classifications("confidentiality"),
    )
    assert s.classified_dimension() == "confidentiality"


def test_integrity_record_classifies_integrity():
    s = _security(
        kind=SecurityKind.INTEGRITY_RECORD,
        classifications=_classifications("integrity"),
    )
    assert s.classified_dimension() == "integrity"


def test_security_identity_is_deterministic_and_structure_derived():
    a = _security()
    b = _security()
    c = _security(name="different.security")
    assert a.security_id == b.security_id  # same structure → same ENG-001 identity
    assert a.security_id != c.security_id  # different name → different identity


def test_security_is_immutable_objecthood():
    s = _security()
    with pytest.raises((AttributeError, TypeError)):
        s.name = "other"  # frozen object (ENG-002 objecthood)


def test_unnamed_security_is_rejected_fail_closed():
    with pytest.raises(SecurityError):
        _security(name="")


def test_untyped_security_is_rejected_fail_closed():
    with pytest.raises(SecurityError):
        _security(type_tag="")  # DZA-K1 / UDL-03


def test_security_without_classifications_is_rejected_fail_closed():
    with pytest.raises(SecurityError):  # DZA-C1 — ≥1 classification required
        _security(classifications=())


def test_classification_dimension_must_match_kind_facet():
    with pytest.raises(SecurityError):  # DXC-02 / DZA-02 — single facet
        _security(
            kind=SecurityKind.CLASSIFICATION_LABEL,
            classifications=make_classifications((("confidentiality", True, 1),)),
        )


def test_classification_entry_requires_valid_dimension_verdict_and_level():
    with pytest.raises(SecurityError):  # DZA-02 — unknown dimension
        ClassificationEntry(dimension="availability", satisfied=True)
    with pytest.raises(SecurityError):  # DZA-C1 — decidable verdict
        ClassificationEntry(dimension="sensitivity", satisfied="yes")
    with pytest.raises(SecurityError):  # DZA-C1 — integer level
        ClassificationEntry(dimension="sensitivity", satisfied=True, level="high")
    with pytest.raises(SecurityError):  # DZA-C1 — bounded [0,3]
        ClassificationEntry(dimension="sensitivity", satisfied=True, level=4)
    with pytest.raises(SecurityError):  # DZA-C1 — bool is not a level
        ClassificationEntry(dimension="sensitivity", satisfied=True, level=True)


def test_security_naming_a_cryptography_technology_is_rejected_fail_closed():
    # UDL-14 / DZA-07 / DZA-C5 / DZA-K5 — evaluative record only; names no crypto/IAM/DLP tech.
    with pytest.raises(SecurityError):
        _security(name="openssl")
    with pytest.raises(SecurityError):
        _security(type_tag="vault.kms")
    with pytest.raises(SecurityError):
        _security(name="rbac.policy")


def test_relationships_are_within_dmr_closure():
    s = _security()
    assert set(s.meta_relationships()) <= set(SECURITY_RELATIONSHIPS)  # V2
    assert s.meta_relationships() == ("DMR-09", "DMR-10", "DMR-11")


def test_verdict_is_a_decidable_security_judgment():
    s = _security(verdict=SecurityVerdict.FAIL)
    assert s.verdict is SecurityVerdict.FAIL  # DZA-C1 / DOV-08
    payload = s.to_dict()
    assert payload["verdict"] == "fail"


def test_supersession_lineage_is_recorded():
    s = _security(version="2.0.0", supersedes="UCOS-SECURITY-old-0000000000000000")
    assert s.version == "2.0.0"  # DZA-08
    assert s.supersedes == "UCOS-SECURITY-old-0000000000000000"  # DZA-C4 append-only
    with pytest.raises(SecurityError):
        _security(version="")


def test_founding_graph_is_acyclic():
    s = _security()
    assert s.is_founding_acyclic() is True  # V4 / DMK-03


def test_invalid_policy_ref_is_rejected():
    with pytest.raises(SecurityError):  # DMR-11 / DZA-K3 — must bind a RUNTIME policy reference
        _security(policy_ref="not-a-policy-ref")


def test_subject_without_certified_construct_id_is_rejected():
    bad_ref = ClassifiedConstructRef(
        construct_id="NOT-A-CONSTRUCT",
        structure_digest="a" * 64,
        name="x",
        type_tag="t",
        meta_class="DMC-02",
    )
    with pytest.raises(SecurityError):  # DMR-09
        make_security(
            "s",
            "ucos.core.security",
            bad_ref,
            POLICY_REF,
            classifications=_classifications(),
        )


def test_subject_without_structural_digest_is_rejected():
    bad_ref = ClassifiedConstructRef(
        construct_id="UCOS-ENTITY-x-0000000000000000",
        structure_digest="short",  # not a 64-hex digest
        name="x",
        type_tag="t",
        meta_class="DMC-02",
    )
    with pytest.raises(SecurityError):  # UDL-06
        make_security(
            "s",
            "ucos.core.security",
            bad_ref,
            POLICY_REF,
            classifications=_classifications(),
        )


def test_non_classified_ref_is_rejected():
    with pytest.raises(SecurityError):  # DMR-09
        SecurityObject(
            name="s",
            type_tag="ucos.core.security",
            kind=SecurityKind.CLASSIFICATION_LABEL,
            classified_ref="not-a-ref",
            policy_ref=POLICY_REF,
            classifications=_classifications(),
        )


def test_non_security_kind_is_rejected():
    with pytest.raises(SecurityError):  # DXH-10 / DMR-09
        _security(kind="Classification-Label")  # str, not SecurityKind


def test_non_classification_tuple_is_rejected():
    # Constructed directly (bypassing make_security's tuple() coercion) to exercise the guard.
    ref = ClassifiedConstructRef.from_entity(_entity())
    with pytest.raises(SecurityError):  # DZA-C1
        SecurityObject(
            name="s",
            type_tag="ucos.core.security",
            kind=SecurityKind.CLASSIFICATION_LABEL,
            classified_ref=ref,
            policy_ref=POLICY_REF,
            classifications=[ClassificationEntry("sensitivity", True)],  # list, not tuple
        )


def test_non_classification_entry_member_is_rejected():
    with pytest.raises(SecurityError):  # DZA-C1
        _security(classifications=("not-an-entry",))


def test_non_verdict_is_rejected():
    with pytest.raises(SecurityError):  # DZA-C1
        _security(verdict="pass")  # str, not SecurityVerdict


def test_non_state_state_is_rejected():
    with pytest.raises(SecurityError):  # UDL-12
        _security(state="DEFINED")  # str, not SecurityState


def test_non_string_supersedes_is_rejected():
    with pytest.raises(SecurityError):  # DZA-C4
        _security(supersedes=123)


def test_non_constitutive_and_no_secret():
    s = _security()
    assert s.confers_authority() is False  # UDL-15 / DZA-09 / C7
    assert s.redefines_el1() is False  # UDL-02 / DMI-05
    assert s.selects_technology() is False  # UDL-14 / DZA-K5 (evaluative record)
    assert s.embeds_secret() is False


def test_secret_bearing_security_is_detected():
    leaky = _security(name="password")
    assert leaky.embeds_secret() is True  # UDL-15 / RR-07


def test_security_to_dict_records_substrate_reuse():
    s = _security()
    payload = s.to_dict()
    assert payload["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005"]
    assert payload["meta_class"] == "DMC-10"
    assert payload["absorbs_classified"] is False
    assert payload["evaluative"] is True
    assert payload["enforces"] is False
    assert payload["grants_access"] is False
    assert payload["recorded"] is True
    assert payload["names_technology"] is False
    assert payload["binds_policy_by_reference"] is True
    assert payload["enforcement_by_reference"] is True


def test_security_type_is_the_realized_construct():
    assert isinstance(_security(), SecurityObject)


def test_progression_is_forward_only():
    s = _security(state=SecurityState.DEFINED)
    active = s.transition(SecurityState.ACTIVE)
    assert active.state is SecurityState.ACTIVE  # UDL-12 forward-only
    with pytest.raises(SecurityError):
        active.transition(SecurityState.DEFINED)  # backward rejected


def test_transition_to_non_state_is_rejected():
    s = _security()
    with pytest.raises(SecurityError):  # UDL-12
        s.transition("ACTIVE")  # str, not SecurityState


def test_make_classifications_builds_entries():
    entries = make_classifications((("sensitivity", True, 2), ("sensitivity", False, 0)))
    assert len(entries) == 2
    assert all(isinstance(e, ClassificationEntry) for e in entries)
    assert entries[1].dimension == "sensitivity"
    assert entries[1].satisfied is False
    assert entries[1].level == 0


def test_policy_ref_for_builds_prefixed_reference():
    ref = policy_ref_for("security.udl")
    assert ref == "UCOS-POLICY-REF:security.udl"


def test_security_selects_no_technology():
    s = _security()
    assert s.names_technology() is False  # UDL-14 / DZA-07 / DZA-K5
    assert s.selects_technology() is False
