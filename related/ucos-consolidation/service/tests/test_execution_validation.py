"""EC3-B11-U08 — Execution validation tests (meta-validity V1…V5 + USL + SEX)."""

from __future__ import annotations

from typing import Any

from engine.runtime.disclosure import build_disclosure
from service.execution import make_execution
from service.execution_meta import EXECUTION_RELATIONSHIPS, ExecutionKind
from service.execution_traceability import build_execution_traceability
from service.execution_validation import (
    ExecutionClassifiedCheck,
    ExecutionContractFulfilmentCheck,
    ExecutionDataByReferenceCheck,
    ExecutionIdentifiedCheck,
    ExecutionLifecycleRecordingCheck,
    ExecutionOperationBoundCheck,
    ExecutionPolicyGovernedCheck,
    ExecutionRuntimeReuseCheck,
    ExecutionTransactionalityCheck,
    ExecutionTypedCheck,
    ExecutionValidationSubject,
    ExecutionValueFidelityCheck,
    FoundationReuseIntegrityCheck,
    FoundingAcyclicCheck,
    LifecycleValidCheck,
    MetaClassSingleCheck,
    MetaConstraintsCheck,
    MetaRelationshipsClosedCheck,
    NonConstitutiveCheck,
    ProvisionalDisclosureCheck,
    TechnologyIndependenceCheck,
    TraceabilityRootedCheck,
    execution_checks,
    validate_execution,
)

_OP = "ENG-005:SOE-05:ucos.service.operation.foundation"


def _exe(**kw):
    return make_execution(
        kw.pop("type_tag", "ucos.service.execution.foundation"),
        kw.pop("operation_ref", _OP),
        kind=kw.pop("kind", ExecutionKind.SYNCHRONOUS),
        data_refs=kw.pop("data_refs", ("ENG-005:DF-2:ucos.data.entity.executed",)),
        **kw,
    )


def _trace(e):
    return build_execution_traceability(e, unit="EC3-B11-U08", forward=(e.execution_id,))


def _subject(**overrides: Any) -> ExecutionValidationSubject:
    e = _exe()
    base: dict[str, Any] = dict(
        target_id=e.execution_id,
        blueprint_id="SMC-08",
        meta_class="SMC-08",
        type_tag=e.type_tag,
        kind=e.kind.value,
        value_digest=e.value_digest,
        operation_ref=e.operation_ref,
        behavior_ref=e.behavior_ref,
        data_refs=e.data_refs,
        policy_ref=e.policy_ref,
        runtime_concern="RUNTIME-006",
        relationships=e.meta_relationships(),
        lifecycle_state=e.state.value,
        founding_acyclic=True,
        no_self_founding=True,
        operation_bound=True,
        fulfils_contract=True,
        runtime_reuse_valid=True,
        behavior_by_reference=True,
        transactionality_by_reference=True,
        data_by_reference=True,
        policy_governed=True,
        records_completion=True,
        references_resolve=True,
        confers_authority=False,
        selects_technology=False,
        embeds_secret=False,
        redefines_foundation=False,
        substrate_refs=("ENG-001", "RL-F2", "DF-2"),
        provenance_chain=("SMC-08", "SOE-08", "11-SERVICE@b7e7657"),
        disclosure=build_disclosure(),
    )
    base.update(overrides)
    return ExecutionValidationSubject(**base)


def _ev(check, **overrides: Any) -> bool:
    """Evaluate ``check`` against a subject with ``overrides`` and return its passed flag."""
    return check.evaluate(_subject(**overrides)).passed


# -- end-to-end -------------------------------------------------------------


def test_validate_canonical_execution_accepted():
    e = _exe()
    result = validate_execution(e, _trace(e))
    assert result.accepted is True
    assert not result.report.blocking_failures


def test_validate_self_founding_execution_rejected():
    e = make_execution("t", "ENG-005:SOE-08:t", kind=ExecutionKind.SYNCHRONOUS)
    result = validate_execution(e, _trace(e))
    assert result.accepted is False
    ids = {f.check_id for f in result.report.blocking_failures}
    assert "founding-acyclic" in ids


def test_validate_bad_transactional_rejected():
    e = make_execution("t", _OP, behavior_ref="ENG-005:RL-F2:RUNTIME-006.run",
                       kind=ExecutionKind.TRANSACTIONAL)
    result = validate_execution(e, _trace(e))
    assert result.accepted is False
    ids = {f.check_id for f in result.report.blocking_failures}
    assert "execution-transactionality-by-reference" in ids
    assert "execution-runtime-reuse" in ids


def test_suite_has_twentyone_checks():
    assert len(execution_checks()) == 21


# -- per-check pass/fail ----------------------------------------------------


def test_typed_check():
    assert ExecutionTypedCheck().evaluate(_subject()).passed is True
    assert ExecutionTypedCheck().evaluate(_subject(type_tag="  ")).passed is False


def test_identified_check():
    assert ExecutionIdentifiedCheck().evaluate(_subject()).passed is True
    assert ExecutionIdentifiedCheck().evaluate(_subject(target_id="X")).passed is False
    assert ExecutionIdentifiedCheck().evaluate(_subject(value_digest="")).passed is False


def test_value_fidelity_check():
    assert ExecutionValueFidelityCheck().evaluate(_subject()).passed is True
    assert ExecutionValueFidelityCheck().evaluate(_subject(value_digest="zz")).passed is False


def test_classified_check():
    assert ExecutionClassifiedCheck().evaluate(_subject()).passed is True
    assert ExecutionClassifiedCheck().evaluate(_subject(kind="Nope")).passed is False


def test_operation_bound_check():
    assert ExecutionOperationBoundCheck().evaluate(_subject()).passed is True
    assert ExecutionOperationBoundCheck().evaluate(_subject(operation_bound=False)).passed is False


def test_contract_fulfilment_check():
    assert ExecutionContractFulfilmentCheck().evaluate(_subject()).passed is True
    assert _ev(ExecutionContractFulfilmentCheck(), fulfils_contract=False) is False


def test_runtime_reuse_check():
    assert ExecutionRuntimeReuseCheck().evaluate(_subject()).passed is True
    assert _ev(ExecutionRuntimeReuseCheck(), runtime_reuse_valid=False) is False


def test_transactionality_check():
    assert ExecutionTransactionalityCheck().evaluate(_subject()).passed is True
    assert _ev(ExecutionTransactionalityCheck(), transactionality_by_reference=False) is False


def test_data_by_reference_check():
    assert ExecutionDataByReferenceCheck().evaluate(_subject()).passed is True
    assert _ev(ExecutionDataByReferenceCheck(), data_by_reference=False) is False


def test_policy_governed_check():
    assert ExecutionPolicyGovernedCheck().evaluate(_subject()).passed is True
    assert ExecutionPolicyGovernedCheck().evaluate(_subject(policy_governed=False)).passed is False


def test_lifecycle_recording_check():
    assert ExecutionLifecycleRecordingCheck().evaluate(_subject()).passed is True
    assert _ev(ExecutionLifecycleRecordingCheck(), records_completion=False) is False


def test_meta_class_single_check():
    assert MetaClassSingleCheck().evaluate(_subject()).passed is True
    assert MetaClassSingleCheck().evaluate(_subject(meta_class="SMC-07")).passed is False


def test_meta_relationships_closed_check():
    assert MetaRelationshipsClosedCheck().evaluate(_subject()).passed is True
    bad = _subject(relationships=(*EXECUTION_RELATIONSHIPS, "SMR-99"))
    assert MetaRelationshipsClosedCheck().evaluate(bad).passed is False


def test_meta_constraints_check():
    assert MetaConstraintsCheck().evaluate(_subject()).passed is True
    assert MetaConstraintsCheck().evaluate(_subject(type_tag="")).passed is False
    assert MetaConstraintsCheck().evaluate(_subject(operation_bound=False)).passed is False
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
    no_anchor = _subject(provenance_chain=("SMC-08", "SOE-08"))
    assert TraceabilityRootedCheck().evaluate(no_anchor).passed is False
