"""EC3-B11-U10 — Security validation tests (meta-validity V1…V5 + USL + SSE)."""

from __future__ import annotations

from typing import Any

from engine.runtime.disclosure import build_disclosure
from service.security import make_security
from service.security_meta import SECURITY_RELATIONSHIPS, SecurityKind
from service.security_traceability import build_security_traceability
from service.security_validation import (
    FoundationReuseIntegrityCheck,
    FoundingAcyclicCheck,
    LifecycleValidCheck,
    MetaClassSingleCheck,
    MetaConstraintsCheck,
    MetaRelationshipsClosedCheck,
    NonConstitutiveCheck,
    ProvisionalDisclosureCheck,
    SecurityBoundaryClassifiedCheck,
    SecurityClassifiedCheck,
    SecurityDataByReferenceCheck,
    SecurityEvaluativeCheck,
    SecurityIdentifiedCheck,
    SecurityLifecycleRecordingCheck,
    SecurityPolicyInformedCheck,
    SecurityPrecedenceCheck,
    SecurityRuntimeReuseCheck,
    SecurityTypedCheck,
    SecurityValidationSubject,
    SecurityValueFidelityCheck,
    TechnologyIndependenceCheck,
    TraceabilityRootedCheck,
    security_checks,
    validate_security,
)

_OP = "ENG-005:SOE-05:ucos.service.operation.foundation"
_POLICY = "ENG-005:SOE-09:ucos.service.policy.foundation"


def _sec(**kw):
    return make_security(
        kw.pop("type_tag", "ucos.service.security.foundation"),
        kw.pop("subject_refs", (_OP,)),
        kind=kw.pop("kind", SecurityKind.CONFIDENTIALITY),
        policy_refs=kw.pop("policy_refs", (_POLICY,)),
        data_refs=kw.pop("data_refs", ("ENG-005:DF-2:ucos.data.entity.governed",)),
        **kw,
    )


def _trace(s):
    return build_security_traceability(s, unit="EC3-B11-U10", forward=(s.security_id,))


def _subject(**overrides: Any) -> SecurityValidationSubject:
    s = _sec()
    base: dict[str, Any] = dict(
        target_id=s.security_id,
        blueprint_id="SMC-10",
        meta_class="SMC-10",
        type_tag=s.type_tag,
        kind=s.kind.value,
        value_digest=s.value_digest,
        subject_refs=s.subject_refs,
        policy_refs=s.policy_refs,
        behavior_ref=s.behavior_ref,
        data_refs=s.data_refs,
        runtime_concern="RUNTIME-010",
        precedence=s.precedence,
        relationships=s.meta_relationships(),
        lifecycle_state=s.state.value,
        founding_acyclic=True,
        no_self_founding=True,
        boundary_classified=True,
        evaluative_nonenforcing=True,
        runtime_reuse_valid=True,
        behavior_by_reference=True,
        data_by_reference=True,
        data_security_reuse=True,
        policy_informed=True,
        precedence_decidable=True,
        records_lifecycle=True,
        references_resolve=True,
        confers_authority=False,
        selects_technology=False,
        embeds_secret=False,
        redefines_foundation=False,
        substrate_refs=("ENG-001", "RL-F2", "DF-2"),
        provenance_chain=("SMC-10", "SOE-10", "11-SERVICE@b7e7657"),
        disclosure=build_disclosure(),
    )
    base.update(overrides)
    return SecurityValidationSubject(**base)


def _ev(check, **overrides: Any) -> bool:
    return check.evaluate(_subject(**overrides)).passed


# -- end-to-end -------------------------------------------------------------


def test_validate_canonical_security_accepted():
    s = _sec()
    result = validate_security(s, _trace(s))
    assert result.accepted is True
    assert not result.report.blocking_failures


def test_validate_self_founding_security_rejected():
    s = make_security("t", ("ENG-005:SOE-10:t",))
    result = validate_security(s, _trace(s))
    assert result.accepted is False
    ids = {f.check_id for f in result.report.blocking_failures}
    assert "founding-acyclic" in ids


def test_validate_wrong_runtime_concern_rejected():
    s = make_security("t", (_OP,), behavior_ref="ENG-005:RL-F2:RUNTIME-999.other")
    result = validate_security(s, _trace(s))
    assert result.accepted is False
    ids = {f.check_id for f in result.report.blocking_failures}
    assert "security-runtime-reuse" in ids


def test_suite_has_twentyone_checks():
    assert len(security_checks()) == 21


# -- per-check pass/fail ----------------------------------------------------


def test_typed_check():
    assert SecurityTypedCheck().evaluate(_subject()).passed is True
    assert SecurityTypedCheck().evaluate(_subject(type_tag="  ")).passed is False


def test_identified_check():
    assert SecurityIdentifiedCheck().evaluate(_subject()).passed is True
    assert SecurityIdentifiedCheck().evaluate(_subject(target_id="X")).passed is False
    assert SecurityIdentifiedCheck().evaluate(_subject(value_digest="")).passed is False


def test_value_fidelity_check():
    assert SecurityValueFidelityCheck().evaluate(_subject()).passed is True
    assert SecurityValueFidelityCheck().evaluate(_subject(value_digest="zz")).passed is False


def test_classified_check():
    assert SecurityClassifiedCheck().evaluate(_subject()).passed is True
    assert SecurityClassifiedCheck().evaluate(_subject(kind="Nope")).passed is False


def test_boundary_classified_check():
    assert SecurityBoundaryClassifiedCheck().evaluate(_subject()).passed is True
    assert _ev(SecurityBoundaryClassifiedCheck(), boundary_classified=False) is False


def test_evaluative_check():
    assert SecurityEvaluativeCheck().evaluate(_subject()).passed is True
    assert _ev(SecurityEvaluativeCheck(), evaluative_nonenforcing=False) is False


def test_runtime_reuse_check():
    assert SecurityRuntimeReuseCheck().evaluate(_subject()).passed is True
    assert _ev(SecurityRuntimeReuseCheck(), runtime_reuse_valid=False) is False


def test_data_by_reference_check():
    assert SecurityDataByReferenceCheck().evaluate(_subject()).passed is True
    assert _ev(SecurityDataByReferenceCheck(), data_by_reference=False) is False
    assert _ev(SecurityDataByReferenceCheck(), data_security_reuse=False) is False


def test_policy_informed_check():
    assert SecurityPolicyInformedCheck().evaluate(_subject()).passed is True
    assert _ev(SecurityPolicyInformedCheck(), policy_informed=False) is False


def test_precedence_check():
    assert SecurityPrecedenceCheck().evaluate(_subject()).passed is True
    assert _ev(SecurityPrecedenceCheck(), precedence_decidable=False) is False


def test_lifecycle_recording_check():
    assert SecurityLifecycleRecordingCheck().evaluate(_subject()).passed is True
    assert _ev(SecurityLifecycleRecordingCheck(), records_lifecycle=False) is False


def test_meta_class_single_check():
    assert MetaClassSingleCheck().evaluate(_subject()).passed is True
    assert MetaClassSingleCheck().evaluate(_subject(meta_class="SMC-09")).passed is False


def test_meta_relationships_closed_check():
    assert MetaRelationshipsClosedCheck().evaluate(_subject()).passed is True
    bad = _subject(relationships=(*SECURITY_RELATIONSHIPS, "SMR-99"))
    assert MetaRelationshipsClosedCheck().evaluate(bad).passed is False


def test_meta_constraints_check():
    assert MetaConstraintsCheck().evaluate(_subject()).passed is True
    assert MetaConstraintsCheck().evaluate(_subject(type_tag="")).passed is False
    assert MetaConstraintsCheck().evaluate(_subject(boundary_classified=False)).passed is False
    assert MetaConstraintsCheck().evaluate(_subject(references_resolve=False)).passed is False


def test_founding_acyclic_check():
    assert FoundingAcyclicCheck().evaluate(_subject()).passed is True
    assert FoundingAcyclicCheck().evaluate(_subject(founding_acyclic=False)).passed is False


def test_lifecycle_valid_check():
    assert LifecycleValidCheck().evaluate(_subject()).passed is True
    assert LifecycleValidCheck().evaluate(_subject(lifecycle_state="BOGUS")).passed is False


def test_foundation_reuse_integrity_check():
    assert FoundationReuseIntegrityCheck().evaluate(_subject()).passed is True
    assert _ev(FoundationReuseIntegrityCheck(), redefines_foundation=True) is False
    assert FoundationReuseIntegrityCheck().evaluate(_subject(substrate_refs=())).passed is False


def test_technology_independence_check():
    assert TechnologyIndependenceCheck().evaluate(_subject()).passed is True
    assert TechnologyIndependenceCheck().evaluate(_subject(selects_technology=True)).passed is False


def test_non_constitutive_check():
    assert NonConstitutiveCheck().evaluate(_subject()).passed is True
    assert NonConstitutiveCheck().evaluate(_subject(confers_authority=True)).passed is False
    assert NonConstitutiveCheck().evaluate(_subject(embeds_secret=True)).passed is False


def test_provisional_disclosure_check():
    assert ProvisionalDisclosureCheck().evaluate(_subject()).passed is True
    assert ProvisionalDisclosureCheck().evaluate(_subject(disclosure={})).passed is False


def test_traceability_rooted_check():
    assert TraceabilityRootedCheck().evaluate(_subject()).passed is True
    assert TraceabilityRootedCheck().evaluate(_subject(provenance_chain=())).passed is False
    assert TraceabilityRootedCheck().evaluate(_subject(provenance_chain=("X", "Y"))).passed is False
    no_anchor = _subject(provenance_chain=("SMC-10", "SOE-10"))
    assert TraceabilityRootedCheck().evaluate(no_anchor).passed is False
