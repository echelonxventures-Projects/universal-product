"""EC3-B11-U10 — Universal Security construct tests (SMC-10).

Covers construction fail-closed guards, boundary classification (SMR-09), informing-policy
scope (SMR-08 governed-by), RUNTIME reuse by reference (RUNTIME-010), DF-2/DATA-014 data by
reference (SSE-06), evaluative non-enforcement (USL-14), founding acyclicity (no self-founding),
precedence, recorded classification judgments (SSE-C1), coverage reports (§12), identity/value
determinism, non-constitutiveness, lifecycle, serialization.
"""

from __future__ import annotations

import pytest

from service.security import (
    Security,
    SecurityAssessment,
    SecurityCoverage,
    SecurityVerdict,
    _default_behavior_ref,
    assess_security_coverage,
    make_security,
)
from service.security_meta import (
    KIND_PRECEDENCE,
    KIND_RUNTIME_CONCERN,
    SECURITY_RELATIONSHIPS,
    SecurityKind,
)
from service.service import ServiceError
from service.service_meta import ServiceState

_OP = "ENG-005:SOE-05:ucos.service.operation.foundation"
_EXEC = "ENG-005:SOE-08:ucos.service.execution.foundation"
_POLICY = "ENG-005:SOE-09:ucos.service.policy.foundation"
_DATA = ("ENG-005:DF-2:ucos.data.entity.governed",)


def _conf() -> Security:
    return make_security(
        "ucos.service.security.foundation",
        (_OP, _EXEC),
        kind=SecurityKind.CONFIDENTIALITY,
        policy_refs=(_POLICY,),
        data_refs=_DATA,
    )


# -- construction guards ----------------------------------------------------


def test_untyped_security_rejected():
    with pytest.raises(ServiceError, match="typed"):
        make_security("  ", (_OP,))


def test_bad_kind_rejected():
    with pytest.raises(ServiceError, match="SecurityKind"):
        Security(type_tag="t", kind="Confidentiality", subject_refs=(_OP,))  # type: ignore[arg-type]


def test_non_tuple_subject_refs_rejected():
    with pytest.raises(ServiceError, match="tuple of ENG-005 references"):
        make_security("t", ["x"])  # type: ignore[arg-type]


def test_empty_subject_refs_rejected():
    with pytest.raises(ServiceError, match="at least 1"):
        make_security("t", ())


def test_blank_subject_ref_entry_rejected():
    with pytest.raises(ServiceError, match="entries must be non-empty"):
        make_security("t", (_OP, "  "))


def test_non_tuple_policy_refs_rejected():
    with pytest.raises(ServiceError, match="tuple of ENG-005 references"):
        make_security("t", (_OP,), policy_refs=["x"])  # type: ignore[arg-type]


def test_blank_policy_ref_entry_rejected():
    with pytest.raises(ServiceError, match="entries must be non-empty"):
        make_security("t", (_OP,), policy_refs=(_POLICY, "  "))


def test_non_tuple_data_refs_rejected():
    with pytest.raises(ServiceError, match="tuple of ENG-005 references"):
        make_security("t", (_OP,), data_refs=["x"])  # type: ignore[arg-type]


def test_blank_data_ref_entry_rejected():
    with pytest.raises(ServiceError, match="entries must be non-empty"):
        make_security("t", (_OP,), data_refs=("ok", "  "))


def test_bad_state_rejected():
    with pytest.raises(ServiceError, match="ServiceState"):
        Security(type_tag="t", kind=SecurityKind.CONFIDENTIALITY, subject_refs=(_OP,), state="X")  # type: ignore[arg-type]


# -- identity + defaults ----------------------------------------------------


def test_identity_is_deterministic_and_prefixed():
    a, b = _conf(), _conf()
    assert a.security_id == b.security_id
    assert a.security_id.startswith("UCOS-SECURITY-")
    assert len(a.value_digest) == 64


def test_self_ref_form():
    assert _conf().self_ref == "ENG-005:SOE-10:ucos.service.security.foundation"


def test_meta_class_and_relationships():
    s = _conf()
    assert s.meta_class == "SMC-10"
    assert s.meta_relationships() == SECURITY_RELATIONSHIPS


@pytest.mark.parametrize("kind", list(SecurityKind))
def test_default_behavior_ref_is_runtime_010(kind):
    ref = _default_behavior_ref(kind)
    assert KIND_RUNTIME_CONCERN[kind] in ref
    assert "RUNTIME-010" in ref
    s = make_security("t", (_OP,), kind=kind)
    assert s.runtime_reuse_valid() is True


def test_explicit_behavior_ref_preserved():
    s = make_security("t", (_OP,), behavior_ref="ENG-005:RL-F2:RUNTIME-010.evaluate")
    assert s.behavior_ref == "ENG-005:RL-F2:RUNTIME-010.evaluate"


def test_empty_policy_and_data_refs_allowed():
    s = make_security("t", (_OP,))
    assert s.policy_refs == ()
    assert s.data_refs == ()
    assert s.policy_informed() is True
    assert s.data_by_reference() is True
    assert s.data_security_reuse() is True


# -- founding acyclicity + self-founding ------------------------------------


def test_canonical_security_is_founding_acyclic():
    s = _conf()
    assert s.no_self_founding() is True
    assert s.is_founding_acyclic() is True
    assert s.references_resolve() is True


def test_self_founding_via_subject_ref_rejected_by_acyclicity():
    s = make_security("t", ("ENG-005:SOE-10:t",))
    assert s.no_self_founding() is False
    assert s.is_founding_acyclic() is False
    assert s.references_resolve() is False


def test_self_founding_via_policy_ref_detected():
    s = make_security("t", (_OP,), policy_refs=("ENG-005:SOE-10:t",))
    assert s.no_self_founding() is False


def test_self_founding_via_data_ref_detected():
    s = make_security("t", (_OP,), data_refs=("ENG-005:SOE-10:t",))
    assert s.no_self_founding() is False


def test_self_founding_via_behavior_ref_detected():
    s = make_security("t", (_OP,), behavior_ref="ENG-005:SOE-10:t")
    assert s.no_self_founding() is False


# -- obligations ------------------------------------------------------------


def test_obligation_predicates_hold_for_canonical():
    s = _conf()
    assert s.boundary_classified() is True
    assert s.evaluative_nonenforcing() is True
    assert s.runtime_reuse_valid() is True
    assert s.behavior_by_reference() is True
    assert s.data_by_reference() is True
    assert s.data_security_reuse() is True
    assert s.policy_informed() is True
    assert s.precedence_decidable() is True
    assert s.records_lifecycle() is True
    assert s.references_resolve() is True
    assert s.redefines_foundation() is False
    assert s.confers_authority() is False


@pytest.mark.parametrize(
    "kind,rank,bears",
    [
        (SecurityKind.AUTHENTICATION, 0, False),
        (SecurityKind.AUTHORIZATION, 1, False),
        (SecurityKind.CONFIDENTIALITY, 2, True),
        (SecurityKind.INTEGRITY, 3, True),
    ],
)
def test_precedence_and_bears_data_match_taxonomy(kind, rank, bears):
    s = make_security("t", (_OP,), kind=kind)
    assert s.precedence == rank
    assert KIND_PRECEDENCE[kind] == rank
    assert s.bears_data is bears


def test_runtime_reuse_invalid_when_wrong_concern():
    s = make_security("t", (_OP,), behavior_ref="ENG-005:RL-F2:RUNTIME-999.other")
    assert s.runtime_reuse_valid() is False


def test_selects_technology_detected():
    s = make_security("t", ("ENG-005:SOE-05:kafka.op",))
    assert s.selects_technology() is True


def test_embeds_secret_detected():
    s = make_security("t", ("ENG-005:SOE-05:password.op",))
    assert s.embeds_secret() is True


def test_clean_security_has_no_tech_or_secret():
    s = _conf()
    assert s.selects_technology() is False
    assert s.embeds_secret() is False


# -- evaluative classification → recorded judgment (SSE-C1 / SOV-09) --------


def test_record_assessment_satisfied_for_classified_subject():
    s = _conf()
    a = s.record_assessment(_OP, satisfied=True)
    assert isinstance(a, SecurityAssessment)
    assert a.verdict is SecurityVerdict.SATISFIED
    assert a.security_id == s.security_id
    assert a.subject_ref == _OP
    assert a.kind == SecurityKind.CONFIDENTIALITY.value
    assert a.enacts_nothing() is True


def test_record_assessment_violated_for_classified_subject():
    a = _conf().record_assessment(_EXEC, satisfied=False)
    assert a.verdict is SecurityVerdict.VIOLATED


def test_record_assessment_inapplicable_when_out_of_scope():
    a = _conf().record_assessment("ENG-005:SOE-05:some.other.op", satisfied=True)
    assert a.verdict is SecurityVerdict.INAPPLICABLE


def test_record_assessment_rejects_empty_subject():
    with pytest.raises(ServiceError, match="subject_ref"):
        _conf().record_assessment("   ", satisfied=True)


def test_classifies():
    s = _conf()
    assert s.classifies(_OP) is True
    assert s.classifies("ENG-005:SOE-05:nope") is False
    assert s.classifies(123) is False  # type: ignore[arg-type]


def test_assessment_to_dict_shape():
    a = _conf().record_assessment(_OP, satisfied=True)
    payload = a.to_dict()
    assert payload["verdict"] == "SATISFIED"
    assert payload["enacts"] == "none"
    assert payload["security_id"].startswith("UCOS-SECURITY-")


# -- coverage report (§12, evaluative/non-enforcing) ------------------------


def test_assess_coverage_records_present_and_absent_facets():
    authn = make_security("a", (_OP,), kind=SecurityKind.AUTHENTICATION)
    conf = make_security("c", (_OP,), kind=SecurityKind.CONFIDENTIALITY)
    coverage = assess_security_coverage((authn, conf))
    assert len(coverage) == 1
    cov = coverage[0]
    assert isinstance(cov, SecurityCoverage)
    assert cov.subject_ref == _OP
    assert SecurityKind.AUTHENTICATION.value in cov.facets_present
    assert SecurityKind.CONFIDENTIALITY.value in cov.facets_present
    assert SecurityKind.AUTHORIZATION.value in cov.facets_absent
    assert cov.fully_covered is False


def test_assess_coverage_fully_covered_when_all_facets_present():
    objs = tuple(make_security("x", (_OP,), kind=k) for k in SecurityKind)
    cov = assess_security_coverage(objs)[0]
    assert cov.fully_covered is True
    assert cov.facets_absent == ()


def test_coverage_to_dict_shape():
    cov = assess_security_coverage((_conf(),))[0]
    payload = cov.to_dict()
    assert payload["subject_ref"] in (_OP, _EXEC)
    assert "records only" in payload["assessment"]
    assert payload["fully_covered"] is False


def test_assess_coverage_empty_input():
    assert assess_security_coverage(()) == ()


# -- lifecycle --------------------------------------------------------------


def test_forward_transition_ok():
    s = _conf().transition(ServiceState.CONTRACTED)
    assert s.state is ServiceState.CONTRACTED


def test_backward_transition_rejected():
    s = _conf().transition(ServiceState.EXECUTABLE)
    with pytest.raises(ServiceError, match="forward-only"):
        s.transition(ServiceState.DEFINED)


def test_bad_transition_target_rejected():
    with pytest.raises(ServiceError, match="ServiceState"):
        _conf().transition("EXECUTABLE")  # type: ignore[arg-type]


# -- serialization ----------------------------------------------------------


def test_to_dict_is_complete_and_deterministic():
    d = _conf().to_dict()
    assert d["meta_class"] == "SMC-10"
    assert d["kind"] == SecurityKind.CONFIDENTIALITY.value
    assert d["subject_refs"] == [_OP, _EXEC]
    assert d["policy_refs"] == [_POLICY]
    assert d["runtime_concern"] == "RUNTIME-010"
    assert d["data_refs"] == list(_DATA)
    assert d["precedence"] == 2
    assert d["bears_data"] is True
    assert d["relationships"] == list(SECURITY_RELATIONSHIPS)
    assert "RL-F2" in d["substrate_refs"] and "DF-2" in d["substrate_refs"]
