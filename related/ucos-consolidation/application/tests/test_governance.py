"""EC3-B12-U10 — Governance construct tests (AMC-10 + AMK-01/02/03/05/07/08 + UAL-14)."""

from __future__ import annotations

import pytest

from application.governance import (
    Governance,
    GovernanceAssessment,
    GovernanceCoverage,
    GovernanceError,
    GovernanceVerdict,
    assess_governance_coverage,
    make_governance,
)
from application.governance_meta import (
    GOVERNANCE_META_CLASS,
    GOVERNANCE_RELATIONSHIPS,
    GovernanceKind,
    GovernanceState,
)

SUBJECTS = (
    "ENG-005:AMC-01:ucos.demo.application",
    "ENG-005:AMC-04:ucos.demo.feature",
)
SECURITY = ("ENG-005:AMC-09:ucos.demo.security.record",)
STATES = ("ENG-005:AMC-07:ucos.demo.state.lifecycle",)
BEHAVIOR = "ENG-005:RL-F2:runtime.governance-evaluate.RUNTIME-010"


def _gov(**overrides):
    base = dict(
        type_tag="ucos.demo.governance",
        subject_refs=SUBJECTS,
        kind=GovernanceKind.CONFORMANCE,
        security_refs=SECURITY,
    )
    base.update(overrides)
    return make_governance(**base)


def test_governance_is_typed_identified_governing_and_evaluative():
    g = _gov()
    assert g.meta_class == GOVERNANCE_META_CLASS  # V1 (AMC-10)
    assert g.type_tag == "ucos.demo.governance"  # UAL-03 / GOV-01 typed
    assert g.governance_id.startswith("UCOS-GOVERNANCE-")  # UAL-04 identified (ENG-001)
    assert len(g.value_digest) == 64  # ENG-003 value fidelity
    assert g.kind is GovernanceKind.CONFORMANCE  # AXH-10 classified
    assert g.facet() == "conformance"  # AXH-10 facet
    assert g.governs_boundary() is True  # AMR-09 defining
    assert g.governed_constructs() == SUBJECTS
    assert g.evaluative_nonenforcing() is True  # UAL-14 (governing, material)
    assert g.binds_runtime_policy() is True  # §7 / AMK-05
    assert g.secures_by_reference() is True  # AMR-08
    assert g.state_by_reference() is True  # AMR-06 (no state refs → vacuously true)
    assert g.participates_in_founding_edge() is False  # reference-only, no founding edge
    assert g.is_founding_acyclic() is True  # V4 / AMK-03 (vacuous)


def test_governance_identity_is_deterministic_and_core_derived():
    a = _gov()
    b = _gov(subject_refs=tuple(reversed(SUBJECTS)))
    c = _gov(subject_refs=("ENG-005:AMC-01:ucos.other.app",))
    assert a.governance_id == b.governance_id  # subject order is not identity-defining
    assert a.governance_id != c.governance_id  # different governed boundary → different id


def test_kind_is_identity_defining_across_kinds():
    a = _gov(kind=GovernanceKind.CONFORMANCE)
    b = _gov(kind=GovernanceKind.POLICY)
    assert a.governance_id != b.governance_id  # kind/facet is part of identity


def test_governance_is_immutable_objecthood():
    g = _gov()
    with pytest.raises((AttributeError, TypeError)):
        g.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_default_behavior_ref_is_derived_when_omitted():
    g = make_governance("t", SUBJECTS, kind=GovernanceKind.CONFORMANCE)
    assert g.behavior_ref == "ENG-005:RL-F2:runtime.governance-evaluate.RUNTIME-010"
    assert g.binds_runtime_policy() is True


def test_untyped_governance_is_rejected_fail_closed():
    with pytest.raises(GovernanceError):
        make_governance("", SUBJECTS)  # UAL-03 / GOV-01
    with pytest.raises(GovernanceError):
        make_governance("   ", SUBJECTS)


def test_non_string_type_tag_is_rejected():
    with pytest.raises(GovernanceError):
        Governance(  # type: ignore[arg-type]
            type_tag=object(),
            kind=GovernanceKind.CONFORMANCE,
            subject_refs=SUBJECTS,
        )


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(GovernanceError):
        Governance(  # type: ignore[arg-type]
            type_tag="t", kind="not-a-kind", subject_refs=SUBJECTS
        )


def test_subject_refs_must_be_a_tuple():
    with pytest.raises(GovernanceError):
        Governance(  # type: ignore[arg-type]
            type_tag="t",
            kind=GovernanceKind.CONFORMANCE,
            subject_refs=["not", "a", "tuple"],
        )


def test_empty_subject_is_rejected():
    with pytest.raises(GovernanceError):
        make_governance("t", ("",))  # GOV-K2
    with pytest.raises(GovernanceError):
        make_governance("t", ("   ",))


def test_at_least_one_boundary_required():
    with pytest.raises(GovernanceError):
        make_governance("t", ())  # AMR-09 / GOV-07 (≥1 boundary)


def test_security_refs_must_be_tuple_of_refs():
    with pytest.raises(GovernanceError):
        Governance(  # type: ignore[arg-type]
            type_tag="t",
            kind=GovernanceKind.CONFORMANCE,
            subject_refs=SUBJECTS,
            security_refs=["not-a-tuple"],
        )
    with pytest.raises(GovernanceError):
        make_governance("t", SUBJECTS, security_refs=("",))


def test_state_refs_must_be_tuple_of_refs():
    with pytest.raises(GovernanceError):
        make_governance("t", SUBJECTS, state_refs=("   ",))
    with pytest.raises(GovernanceError):
        Governance(  # type: ignore[arg-type]
            type_tag="t",
            kind=GovernanceKind.LIFECYCLE,
            subject_refs=SUBJECTS,
            state_refs="not-a-tuple",
        )


def test_bad_lifecycle_state_is_rejected_fail_closed():
    with pytest.raises(GovernanceError):
        Governance(
            type_tag="t",
            kind=GovernanceKind.CONFORMANCE,
            subject_refs=SUBJECTS,
            state="BAD",  # type: ignore[arg-type]
        )


def test_relationships_are_within_amr_closure():
    g = _gov()
    assert set(g.meta_relationships()) <= {f"AMR-{n:02d}" for n in range(1, 15)}  # V2
    assert g.meta_relationships() == ("AMR-06", "AMR-08", "AMR-09", "AMR-10")
    assert g.meta_relationships() == GOVERNANCE_RELATIONSHIPS


def test_governance_uses_evaluative_relationships_but_not_deliver_hold_consume_assemble():
    # AMC-10 relationship set: uses AMR-06 (holds-state) + AMR-08 (secured-by) + AMR-09
    # (governed-by) + AMR-10 (id) and does NOT use AMR-01/02/03/04/05/07/11/12/13/14.
    rels = set(_gov().meta_relationships())
    assert {"AMR-06", "AMR-08", "AMR-09", "AMR-10"} <= rels
    for absent in ("AMR-01", "AMR-02", "AMR-03", "AMR-04", "AMR-05", "AMR-07",
                   "AMR-11", "AMR-12", "AMR-13", "AMR-14"):
        assert absent not in rels


# -- founding acyclicity (V4 / AMK-03 — vacuous / no-self-founding) ----------------


def test_no_self_founding_true_for_well_formed_record():
    assert _gov().no_self_founding() is True
    assert _gov().references_resolve() is True


def test_self_founding_reference_is_detected():
    # A subject that names the record itself (ENG-005:AOE-10:<type_tag>) is a self-founding ref.
    g = make_governance("t", ("ENG-005:AOE-10:t", SUBJECTS[0]))
    assert g.no_self_founding() is False  # AMK-03
    assert g.is_founding_acyclic() is False  # V4 fails on self-founding
    assert g.references_resolve() is False


# -- accessors / evaluative obligations -------------------------------------------


def test_governs_and_precedence_and_holds_state():
    g = _gov()
    assert g.governs(SUBJECTS[0]) is True
    assert g.governs("ENG-005:AMC-01:not-a-subject") is False
    assert g.precedence == 0  # Conformance precedence (AXH-10 order)
    assert g.precedence_decidable() is True
    assert g.holds_state is False  # Conformance holds no state
    assert make_governance("t", SUBJECTS, kind=GovernanceKind.LIFECYCLE).holds_state is True
    assert g.uses_new_connection_construct() is False
    assert g.behavior_by_reference() is True


def test_enforces_ratifies_and_confers_authority_are_false():
    g = _gov()
    assert g.enforces() is False  # GOV-04 / GOV-C2
    assert g.ratifies() is False  # GOV-04 / GOV-C2/C5
    assert g.confers_authority() is False  # UAL-14/15 / GOV-09
    assert g.redefines_foundation() is False  # UAL-02 / AMI-05


# -- evaluative judgment → recorded judgment (GOV-C1 / AOV-09) --------------------


def test_record_assessment_satisfied_violated_inapplicable():
    g = _gov()
    good = g.record_assessment(SUBJECTS[0], True)
    assert isinstance(good, GovernanceAssessment)
    assert good.verdict is GovernanceVerdict.SATISFIED
    assert good.enacts_nothing() is True
    bad = g.record_assessment(SUBJECTS[0], False)
    assert bad.verdict is GovernanceVerdict.VIOLATED
    off = g.record_assessment("ENG-005:AMC-01:unscoped", True)
    assert off.verdict is GovernanceVerdict.INAPPLICABLE  # outside governed boundary


def test_record_assessment_rejects_empty_subject():
    with pytest.raises(GovernanceError):
        _gov().record_assessment("", True)


def test_assessment_to_dict_shape():
    d = _gov().record_assessment(SUBJECTS[0], True).to_dict()
    assert d["assessment_format"] == "ucos-application-governance-assessment/1.0.0"
    assert d["verdict"] == "SATISFIED"
    assert d["enacts"] == "none"
    assert d["kind"] == "Conformance-Record"


# -- coverage map (APPLICATION-014 §11; evaluative, non-enforcing) ----------------


def test_assess_governance_coverage_records_present_and_absent_facets():
    conf = make_governance("t", (SUBJECTS[0],), kind=GovernanceKind.CONFORMANCE)
    life = make_governance("t", (SUBJECTS[0],), kind=GovernanceKind.LIFECYCLE)
    pol = make_governance("t", (SUBJECTS[1],), kind=GovernanceKind.POLICY)
    coverage = assess_governance_coverage((conf, life, pol))
    by_subject = {c.subject_ref: c for c in coverage}
    assert set(by_subject) == set(SUBJECTS)
    cov0 = by_subject[SUBJECTS[0]]
    assert cov0.facets_present == ("Conformance-Record", "Lifecycle-Record")
    assert "Policy-Record" in cov0.facets_absent
    assert cov0.fully_covered is False


def test_coverage_fully_covered_when_all_facets_present():
    subj = ("ENG-005:AMC-01:ucos.full",)
    records = tuple(
        make_governance("t", subj, kind=k)
        for k in GovernanceKind
    )
    coverage = assess_governance_coverage(records)
    assert len(coverage) == 1
    assert coverage[0].fully_covered is True
    assert coverage[0].facets_absent == ()


def test_coverage_to_dict_shape():
    d = GovernanceCoverage(
        subject_ref="ENG-005:AMC-01:x",
        facets_present=("Conformance-Record",),
        facets_absent=("Policy-Record",),
    ).to_dict()
    assert d["coverage_format"] == "ucos-application-governance-coverage/1.0.0"
    assert d["fully_covered"] is False
    assert "records only, enacts nothing" in d["assessment"]


# -- lifecycle (UAL-12, forward-only) ---------------------------------------------


def test_lifecycle_is_forward_only():
    g = _gov(state=GovernanceState.DEFINED)
    composed = g.transition(GovernanceState.COMPOSED)
    assert composed.state is GovernanceState.COMPOSED
    executable = composed.transition(GovernanceState.CONTEXTUALIZED).transition(
        GovernanceState.EXECUTABLE
    )
    assert executable.state is GovernanceState.EXECUTABLE
    with pytest.raises(GovernanceError):
        executable.transition(GovernanceState.DEFINED)  # UAL-12 — no backward


def test_transition_to_same_state_is_allowed():
    g = _gov(state=GovernanceState.COMPOSED)
    assert g.transition(GovernanceState.COMPOSED).state is GovernanceState.COMPOSED


def test_transition_rejects_non_state_target():
    with pytest.raises(GovernanceError):
        _gov().transition("EXECUTABLE")  # type: ignore[arg-type]


def test_governance_does_not_change_identity_across_lifecycle():
    a = _gov(state=GovernanceState.DEFINED)
    b = _gov(state=GovernanceState.COMPOSED)
    assert a.governance_id == b.governance_id  # identity is core-derived, not lifecycle


# -- non-constitutiveness (UAL-15 / GOV-K5/09) ------------------------------------


def test_non_constitutive_and_no_secret_no_technology():
    g = _gov()
    assert g.confers_authority() is False  # UAL-15 / GOV-09 / C7
    assert g.selects_technology() is False  # UAL-15 / GOV-K5 (abstract references only)
    assert g.embeds_secret() is False


def test_technology_bearing_governance_is_detected():
    techy = make_governance("t", ("ENG-005:AMC-01:camunda.workflow", SUBJECTS[1]))
    assert techy.selects_technology() is True  # UAL-15 / GOV-K5 — approval engine named


def test_secret_bearing_governance_is_detected():
    leaky = make_governance("t", ("ENG-005:AMC-01:api_key-store", SUBJECTS[1]))
    assert leaky.embeds_secret() is True  # UAL-15 / RR-07


# -- serialization / canonical core -----------------------------------------------


def test_governance_to_dict_records_substrate_reuse():
    payload = _gov().to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
    ]
    assert payload["meta_class"] == "AMC-10"
    assert payload["kind"] == "Conformance-Record"
    assert payload["facet"] == "conformance"
    assert payload["is_founding"] is False
    assert payload["founding_acyclic"] is True
    assert payload["evaluative_nonenforcing"] is True
    assert payload["binds_runtime_policy"] is True
    assert payload["holds_state"] is False
    assert payload["precedence"] == 0
    assert payload["runtime_concern"] == "RUNTIME-010"


def test_canonical_core_excludes_lifecycle_and_id():
    core = _gov().canonical_core()
    assert "state" not in core  # lifecycle is not identity-defining
    assert "governance_id" not in core
    assert core["meta_class"] == "AMC-10"
    assert core["facet"] == "conformance"
    assert core["subject_refs"] == sorted(SUBJECTS)


def test_make_governance_default_kind_is_conformance():
    g = make_governance("t", SUBJECTS)
    assert g.kind is GovernanceKind.CONFORMANCE
    assert isinstance(g, Governance)


def test_lifecycle_record_holds_state_by_reference():
    g = make_governance("t", SUBJECTS, kind=GovernanceKind.LIFECYCLE, state_refs=STATES)
    assert g.holds_state is True
    assert g.state_by_reference() is True
    assert g.to_dict()["state_refs"] == list(STATES)
