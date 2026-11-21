"""EC3-B11-U09 — Policy validation tests (meta-validity V1…V5 + USL + SPL)."""

from __future__ import annotations

from typing import Any

from engine.runtime.disclosure import build_disclosure
from service.policy import make_policy
from service.policy_meta import POLICY_RELATIONSHIPS, PolicyKind
from service.policy_traceability import build_policy_traceability
from service.policy_validation import (
    FoundationReuseIntegrityCheck,
    FoundingAcyclicCheck,
    LifecycleValidCheck,
    MetaClassSingleCheck,
    MetaConstraintsCheck,
    MetaRelationshipsClosedCheck,
    NonConstitutiveCheck,
    PolicyBoundaryBoundCheck,
    PolicyClassifiedCheck,
    PolicyDataByReferenceCheck,
    PolicyDeclarativeCheck,
    PolicyGovernedScopeCheck,
    PolicyIdentifiedCheck,
    PolicyLifecycleRecordingCheck,
    PolicyPrecedenceCheck,
    PolicyRuntimeReuseCheck,
    PolicyTypedCheck,
    PolicyValidationSubject,
    PolicyValueFidelityCheck,
    ProvisionalDisclosureCheck,
    TechnologyIndependenceCheck,
    TraceabilityRootedCheck,
    policy_checks,
    validate_policy,
)

_CONTRACT = "ENG-005:SOE-03:ucos.service.contract.foundation"
_OP = "ENG-005:SOE-05:ucos.service.operation.foundation"


def _pol(**kw):
    return make_policy(
        kw.pop("type_tag", "ucos.service.policy.foundation"),
        kw.pop("contract_ref", _CONTRACT),
        kind=kw.pop("kind", PolicyKind.AUTHORIZATION),
        subject_refs=kw.pop("subject_refs", (_OP,)),
        data_refs=kw.pop("data_refs", ("ENG-005:DF-2:ucos.data.entity.governed",)),
        **kw,
    )


def _trace(p):
    return build_policy_traceability(p, unit="EC3-B11-U09", forward=(p.policy_id,))


def _subject(**overrides: Any) -> PolicyValidationSubject:
    p = _pol()
    base: dict[str, Any] = dict(
        target_id=p.policy_id,
        blueprint_id="SMC-09",
        meta_class="SMC-09",
        type_tag=p.type_tag,
        kind=p.kind.value,
        value_digest=p.value_digest,
        contract_ref=p.contract_ref,
        subject_refs=p.subject_refs,
        behavior_ref=p.behavior_ref,
        data_refs=p.data_refs,
        runtime_concern="RUNTIME-010",
        precedence=p.precedence,
        relationships=p.meta_relationships(),
        lifecycle_state=p.state.value,
        founding_acyclic=True,
        no_self_founding=True,
        boundary_bound=True,
        declarative_nonenforcing=True,
        runtime_reuse_valid=True,
        behavior_by_reference=True,
        data_by_reference=True,
        scope_by_reference=True,
        precedence_decidable=True,
        records_lifecycle=True,
        references_resolve=True,
        confers_authority=False,
        selects_technology=False,
        embeds_secret=False,
        redefines_foundation=False,
        substrate_refs=("ENG-001", "RL-F2", "DF-2"),
        provenance_chain=("SMC-09", "SOE-09", "11-SERVICE@b7e7657"),
        disclosure=build_disclosure(),
    )
    base.update(overrides)
    return PolicyValidationSubject(**base)


def _ev(check, **overrides: Any) -> bool:
    return check.evaluate(_subject(**overrides)).passed


# -- end-to-end -------------------------------------------------------------


def test_validate_canonical_policy_accepted():
    p = _pol()
    result = validate_policy(p, _trace(p))
    assert result.accepted is True
    assert not result.report.blocking_failures


def test_validate_self_founding_policy_rejected():
    p = make_policy("t", "ENG-005:SOE-09:t")
    result = validate_policy(p, _trace(p))
    assert result.accepted is False
    ids = {f.check_id for f in result.report.blocking_failures}
    assert "founding-acyclic" in ids


def test_validate_wrong_runtime_concern_rejected():
    p = make_policy("t", _CONTRACT, behavior_ref="ENG-005:RL-F2:RUNTIME-999.other")
    result = validate_policy(p, _trace(p))
    assert result.accepted is False
    ids = {f.check_id for f in result.report.blocking_failures}
    assert "policy-runtime-reuse" in ids


def test_suite_has_twentyone_checks():
    assert len(policy_checks()) == 21


# -- per-check pass/fail ----------------------------------------------------


def test_typed_check():
    assert PolicyTypedCheck().evaluate(_subject()).passed is True
    assert PolicyTypedCheck().evaluate(_subject(type_tag="  ")).passed is False


def test_identified_check():
    assert PolicyIdentifiedCheck().evaluate(_subject()).passed is True
    assert PolicyIdentifiedCheck().evaluate(_subject(target_id="X")).passed is False
    assert PolicyIdentifiedCheck().evaluate(_subject(value_digest="")).passed is False


def test_value_fidelity_check():
    assert PolicyValueFidelityCheck().evaluate(_subject()).passed is True
    assert PolicyValueFidelityCheck().evaluate(_subject(value_digest="zz")).passed is False


def test_classified_check():
    assert PolicyClassifiedCheck().evaluate(_subject()).passed is True
    assert PolicyClassifiedCheck().evaluate(_subject(kind="Nope")).passed is False


def test_boundary_bound_check():
    assert PolicyBoundaryBoundCheck().evaluate(_subject()).passed is True
    assert _ev(PolicyBoundaryBoundCheck(), boundary_bound=False) is False


def test_declarative_check():
    assert PolicyDeclarativeCheck().evaluate(_subject()).passed is True
    assert _ev(PolicyDeclarativeCheck(), declarative_nonenforcing=False) is False


def test_runtime_reuse_check():
    assert PolicyRuntimeReuseCheck().evaluate(_subject()).passed is True
    assert _ev(PolicyRuntimeReuseCheck(), runtime_reuse_valid=False) is False


def test_data_by_reference_check():
    assert PolicyDataByReferenceCheck().evaluate(_subject()).passed is True
    assert _ev(PolicyDataByReferenceCheck(), data_by_reference=False) is False


def test_governed_scope_check():
    assert PolicyGovernedScopeCheck().evaluate(_subject()).passed is True
    assert _ev(PolicyGovernedScopeCheck(), scope_by_reference=False) is False


def test_precedence_check():
    assert PolicyPrecedenceCheck().evaluate(_subject()).passed is True
    assert _ev(PolicyPrecedenceCheck(), precedence_decidable=False) is False


def test_lifecycle_recording_check():
    assert PolicyLifecycleRecordingCheck().evaluate(_subject()).passed is True
    assert _ev(PolicyLifecycleRecordingCheck(), records_lifecycle=False) is False


def test_meta_class_single_check():
    assert MetaClassSingleCheck().evaluate(_subject()).passed is True
    assert MetaClassSingleCheck().evaluate(_subject(meta_class="SMC-08")).passed is False


def test_meta_relationships_closed_check():
    assert MetaRelationshipsClosedCheck().evaluate(_subject()).passed is True
    bad = _subject(relationships=(*POLICY_RELATIONSHIPS, "SMR-99"))
    assert MetaRelationshipsClosedCheck().evaluate(bad).passed is False


def test_meta_constraints_check():
    assert MetaConstraintsCheck().evaluate(_subject()).passed is True
    assert MetaConstraintsCheck().evaluate(_subject(type_tag="")).passed is False
    assert MetaConstraintsCheck().evaluate(_subject(boundary_bound=False)).passed is False
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
    no_anchor = _subject(provenance_chain=("SMC-09", "SOE-09"))
    assert TraceabilityRootedCheck().evaluate(no_anchor).passed is False
