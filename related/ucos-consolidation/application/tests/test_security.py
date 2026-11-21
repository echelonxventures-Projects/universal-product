"""EC3-B12-U09 — Security construct tests (AMC-09 + AMK-01/02/03/05/07/08 + UAL-14)."""

from __future__ import annotations

import pytest

from application.security import (
    Security,
    SecurityAssessment,
    SecurityCoverage,
    SecurityError,
    SecurityVerdict,
    assess_security_coverage,
    make_security,
)
from application.security_meta import (
    SECURITY_META_CLASS,
    SECURITY_RELATIONSHIPS,
    SecurityKind,
    SecurityState,
)

SUBJECTS = (
    "ENG-005:AMC-01:ucos.demo.application",
    "ENG-005:AMC-04:ucos.demo.feature",
)
GOVERNANCE = ("ENG-005:AMC-10:ucos.demo.governance.policy",)
DATA = ("ENG-005:DF-2:DATA-014.confidentiality.datum",)
BEHAVIOR = "ENG-005:RL-F2:runtime.security-evaluate.RUNTIME-010"


def _sec(**overrides):
    base = dict(
        type_tag="ucos.demo.security",
        subject_refs=SUBJECTS,
        kind=SecurityKind.CONFIDENTIALITY,
        governance_refs=GOVERNANCE,
        data_refs=DATA,
        behavior_ref=BEHAVIOR,
    )
    base.update(overrides)
    return make_security(**base)


def test_security_is_typed_identified_classifying_and_evaluative():
    s = _sec()
    assert s.meta_class == SECURITY_META_CLASS  # V1 (AMC-09)
    assert s.type_tag == "ucos.demo.security"  # UAL-03 / SEC-01 typed
    assert s.security_id.startswith("UCOS-SECURITY-")  # UAL-04 identified (ENG-001)
    assert len(s.value_digest) == 64  # ENG-003 value fidelity
    assert s.kind is SecurityKind.CONFIDENTIALITY  # AXH-09 classified
    assert s.facet() == "confidentiality"  # AXH-09 facet
    assert s.classifies_boundary() is True  # AMR-08 defining
    assert s.secured_boundaries() == SUBJECTS
    assert s.evaluative_nonenforcing() is True  # UAL-14 (governing, material)
    assert s.binds_runtime_policy() is True  # §7 / AMK-05
    assert s.data_by_reference() is True  # AMR-14 / UAL-13
    assert s.governed_by_reference() is True  # AMR-09
    assert s.participates_in_founding_edge() is False  # reference-only, no founding edge
    assert s.is_founding_acyclic() is True  # V4 / AMK-03 (vacuous)


def test_security_identity_is_deterministic_and_core_derived():
    a = _sec()
    b = _sec(subject_refs=tuple(reversed(SUBJECTS)))
    c = _sec(subject_refs=("ENG-005:AMC-01:ucos.other.app",))
    assert a.security_id == b.security_id  # subject order is not identity-defining
    assert a.security_id != c.security_id  # different classified boundary → different id


def test_kind_is_identity_defining_across_kinds():
    a = _sec(kind=SecurityKind.CONFIDENTIALITY, data_refs=DATA)
    b = _sec(kind=SecurityKind.INTEGRITY, data_refs=DATA)
    assert a.security_id != b.security_id  # kind/facet is part of identity


def test_security_is_immutable_objecthood():
    s = _sec()
    with pytest.raises((AttributeError, TypeError)):
        s.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_default_behavior_ref_is_derived_when_omitted():
    s = make_security("t", SUBJECTS, kind=SecurityKind.AUTHENTICATION)
    assert s.behavior_ref == "ENG-005:RL-F2:runtime.security-evaluate.RUNTIME-010"
    assert s.binds_runtime_policy() is True


def test_untyped_security_is_rejected_fail_closed():
    with pytest.raises(SecurityError):
        make_security("", SUBJECTS)  # UAL-03 / SEC-01
    with pytest.raises(SecurityError):
        make_security("   ", SUBJECTS)


def test_non_string_type_tag_is_rejected():
    with pytest.raises(SecurityError):
        Security(  # type: ignore[arg-type]
            type_tag=object(),
            kind=SecurityKind.AUTHORIZATION,
            subject_refs=SUBJECTS,
        )


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(SecurityError):
        Security(  # type: ignore[arg-type]
            type_tag="t", kind="not-a-kind", subject_refs=SUBJECTS
        )


def test_subject_refs_must_be_a_tuple():
    with pytest.raises(SecurityError):
        Security(  # type: ignore[arg-type]
            type_tag="t",
            kind=SecurityKind.AUTHORIZATION,
            subject_refs=["not", "a", "tuple"],
        )


def test_empty_subject_is_rejected():
    with pytest.raises(SecurityError):
        make_security("t", ("",))  # SEC-K2
    with pytest.raises(SecurityError):
        make_security("t", ("   ",))


def test_at_least_one_boundary_required():
    with pytest.raises(SecurityError):
        make_security("t", ())  # AMR-08 / SEC-07 (≥1 boundary)


def test_governance_refs_must_be_tuple_of_refs():
    with pytest.raises(SecurityError):
        Security(  # type: ignore[arg-type]
            type_tag="t",
            kind=SecurityKind.AUTHORIZATION,
            subject_refs=SUBJECTS,
            governance_refs=["not-a-tuple"],
        )
    with pytest.raises(SecurityError):
        make_security("t", SUBJECTS, governance_refs=("",))


def test_data_refs_must_be_tuple_of_refs():
    with pytest.raises(SecurityError):
        make_security("t", SUBJECTS, data_refs=("   ",))
    with pytest.raises(SecurityError):
        Security(  # type: ignore[arg-type]
            type_tag="t",
            kind=SecurityKind.CONFIDENTIALITY,
            subject_refs=SUBJECTS,
            data_refs="not-a-tuple",
        )


def test_bad_lifecycle_state_is_rejected_fail_closed():
    with pytest.raises(SecurityError):
        Security(
            type_tag="t",
            kind=SecurityKind.AUTHORIZATION,
            subject_refs=SUBJECTS,
            state="BAD",  # type: ignore[arg-type]
        )


def test_relationships_are_within_amr_closure():
    s = _sec()
    assert set(s.meta_relationships()) <= {f"AMR-{n:02d}" for n in range(1, 15)}  # V2
    assert s.meta_relationships() == ("AMR-08", "AMR-09", "AMR-10", "AMR-14")
    assert s.meta_relationships() == SECURITY_RELATIONSHIPS


def test_security_uses_evaluative_relationships_but_not_deliver_hold_consume_assemble():
    # AMC-09 relationship set: uses AMR-08 (secured-by) + AMR-09 (governed-by) + AMR-10 (id) +
    # AMR-14 (presents-data) and does NOT use AMR-01/02/03/04/05/06/07/11/12/13.
    rels = set(_sec().meta_relationships())
    assert {"AMR-08", "AMR-09", "AMR-10", "AMR-14"} <= rels
    for absent in ("AMR-01", "AMR-02", "AMR-03", "AMR-04", "AMR-05", "AMR-06", "AMR-07",
                   "AMR-11", "AMR-12", "AMR-13"):
        assert absent not in rels


# -- founding acyclicity (V4 / AMK-03 — vacuous / no-self-founding) ----------------


def test_no_self_founding_true_for_well_formed_record():
    assert _sec().no_self_founding() is True
    assert _sec().references_resolve() is True


def test_self_founding_reference_is_detected():
    # A subject that names the record itself (ENG-005:AOE-09:<type_tag>) is a self-founding ref.
    s = make_security("t", ("ENG-005:AOE-09:t", SUBJECTS[0]))
    assert s.no_self_founding() is False  # AMK-03
    assert s.is_founding_acyclic() is False  # V4 fails on self-founding
    assert s.references_resolve() is False


# -- accessors / evaluative obligations -------------------------------------------


def test_classifies_and_precedence_and_bears_data():
    s = _sec()
    assert s.classifies(SUBJECTS[0]) is True
    assert s.classifies("ENG-005:AMC-01:not-a-subject") is False
    assert s.precedence == 2  # Confidentiality precedence (AXH-09 order)
    assert s.precedence_decidable() is True
    assert s.bears_data is True  # Confidentiality bears data
    assert make_security("t", SUBJECTS, kind=SecurityKind.AUTHENTICATION).bears_data is False
    assert s.uses_new_connection_construct() is False
    assert s.data_security_reuse() is True
    assert s.behavior_by_reference() is True


def test_grants_access_and_confers_authority_are_false():
    s = _sec()
    assert s.grants_access() is False  # SEC-04 / SEC-C2
    assert s.confers_authority() is False  # UAL-14/15 / SEC-09
    assert s.redefines_foundation() is False  # UAL-02 / AMI-05


# -- evaluative classification → recorded judgment (SEC-C1 / AOV-09) --------------


def test_record_assessment_satisfied_violated_inapplicable():
    s = _sec()
    good = s.record_assessment(SUBJECTS[0], True)
    assert isinstance(good, SecurityAssessment)
    assert good.verdict is SecurityVerdict.SATISFIED
    assert good.enacts_nothing() is True
    bad = s.record_assessment(SUBJECTS[0], False)
    assert bad.verdict is SecurityVerdict.VIOLATED
    off = s.record_assessment("ENG-005:AMC-01:unscoped", True)
    assert off.verdict is SecurityVerdict.INAPPLICABLE  # outside classified boundary


def test_record_assessment_rejects_empty_subject():
    with pytest.raises(SecurityError):
        _sec().record_assessment("", True)


def test_assessment_to_dict_shape():
    d = _sec().record_assessment(SUBJECTS[0], True).to_dict()
    assert d["assessment_format"] == "ucos-application-security-assessment/1.0.0"
    assert d["verdict"] == "SATISFIED"
    assert d["enacts"] == "none"
    assert d["kind"] == "Confidentiality-Record"


# -- coverage map (APPLICATION-013 §12; evaluative, non-enforcing) ----------------


def test_assess_security_coverage_records_present_and_absent_facets():
    authn = make_security("t", (SUBJECTS[0],), kind=SecurityKind.AUTHENTICATION)
    authz = make_security("t", (SUBJECTS[0],), kind=SecurityKind.AUTHORIZATION)
    conf = make_security("t", (SUBJECTS[1],), kind=SecurityKind.CONFIDENTIALITY, data_refs=DATA)
    coverage = assess_security_coverage((authn, authz, conf))
    by_subject = {c.subject_ref: c for c in coverage}
    assert set(by_subject) == set(SUBJECTS)
    cov0 = by_subject[SUBJECTS[0]]
    assert cov0.facets_present == ("Authentication-Record", "Authorization-Record")
    assert "Confidentiality-Record" in cov0.facets_absent
    assert cov0.fully_covered is False


def test_coverage_fully_covered_when_all_facets_present():
    subj = ("ENG-005:AMC-01:ucos.full",)
    records = tuple(
        make_security("t", subj, kind=k, data_refs=DATA)
        for k in SecurityKind
    )
    coverage = assess_security_coverage(records)
    assert len(coverage) == 1
    assert coverage[0].fully_covered is True
    assert coverage[0].facets_absent == ()


def test_coverage_to_dict_shape():
    d = SecurityCoverage(
        subject_ref="ENG-005:AMC-01:x",
        facets_present=("Authentication-Record",),
        facets_absent=("Authorization-Record",),
    ).to_dict()
    assert d["coverage_format"] == "ucos-application-security-coverage/1.0.0"
    assert d["fully_covered"] is False
    assert "records only, enacts nothing" in d["assessment"]


# -- lifecycle (UAL-12, forward-only) ---------------------------------------------


def test_lifecycle_is_forward_only():
    s = _sec(state=SecurityState.DEFINED)
    composed = s.transition(SecurityState.COMPOSED)
    assert composed.state is SecurityState.COMPOSED
    executable = composed.transition(SecurityState.CONTEXTUALIZED).transition(
        SecurityState.EXECUTABLE
    )
    assert executable.state is SecurityState.EXECUTABLE
    with pytest.raises(SecurityError):
        executable.transition(SecurityState.DEFINED)  # UAL-12 — no backward


def test_transition_to_same_state_is_allowed():
    s = _sec(state=SecurityState.COMPOSED)
    assert s.transition(SecurityState.COMPOSED).state is SecurityState.COMPOSED


def test_transition_rejects_non_state_target():
    with pytest.raises(SecurityError):
        _sec().transition("EXECUTABLE")  # type: ignore[arg-type]


def test_security_does_not_change_identity_across_lifecycle():
    a = _sec(state=SecurityState.DEFINED)
    b = _sec(state=SecurityState.COMPOSED)
    assert a.security_id == b.security_id  # identity is core-derived, not lifecycle


# -- non-constitutiveness (UAL-15 / SEC-05/09) ------------------------------------


def test_non_constitutive_and_no_secret_no_technology():
    s = _sec()
    assert s.confers_authority() is False  # UAL-15 / SEC-09 / C7
    assert s.selects_technology() is False  # UAL-15 / SEC-05 (abstract references only)
    assert s.embeds_secret() is False


def test_technology_bearing_security_is_detected():
    techy = make_security("t", ("ENG-005:AMC-01:oauth.provider", SUBJECTS[1]))
    assert techy.selects_technology() is True  # UAL-15 / SEC-05 — IAM/protocol named


def test_secret_bearing_security_is_detected():
    leaky = make_security("t", ("ENG-005:AMC-01:api_key-store", SUBJECTS[1]))
    assert leaky.embeds_secret() is True  # UAL-15 / RR-07


# -- serialization / canonical core -----------------------------------------------


def test_security_to_dict_records_substrate_reuse():
    payload = _sec().to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
        "DF-2",
    ]
    assert payload["meta_class"] == "AMC-09"
    assert payload["kind"] == "Confidentiality-Record"
    assert payload["facet"] == "confidentiality"
    assert payload["is_founding"] is False
    assert payload["founding_acyclic"] is True
    assert payload["evaluative_nonenforcing"] is True
    assert payload["binds_runtime_policy"] is True
    assert payload["bears_data"] is True
    assert payload["precedence"] == 2
    assert payload["runtime_concern"] == "RUNTIME-010"


def test_canonical_core_excludes_lifecycle_and_id():
    core = _sec().canonical_core()
    assert "state" not in core  # lifecycle is not identity-defining
    assert "security_id" not in core
    assert core["meta_class"] == "AMC-09"
    assert core["facet"] == "confidentiality"
    assert core["subject_refs"] == sorted(SUBJECTS)


def test_make_security_default_kind_is_authorization():
    s = make_security("t", SUBJECTS)
    assert s.kind is SecurityKind.AUTHORIZATION
    assert isinstance(s, Security)
