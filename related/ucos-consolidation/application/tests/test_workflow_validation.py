"""EC3-B12-U05 — Workflow validation tests (V1…V5 + UAL/WKF conformance, fail-closed)."""

from __future__ import annotations

from application.workflow import make_workflow
from application.workflow_meta import REALIZATION_UNIT, WorkflowKind, WorkflowState
from application.workflow_traceability import build_traceability
from application.workflow_validation import (
    WorkflowValidationSubject,
    validate_workflow,
    workflow_checks,
)

SEQ = (
    "ENG-005:AMC-04:ucos.demo.feature.a",
    "ENG-005:AMC-04:ucos.demo.feature.b",
)
ONE_OP = ("ENG-005:SF-2:ucos.demo.operation.a",)


def _trace(workflow, *, forward=("fwd",)):
    return build_traceability(workflow, unit=REALIZATION_UNIT, forward=forward)


def _validate(workflow, **trace_kw):
    return validate_workflow(workflow, _trace(workflow, **trace_kw))


def test_canonical_workflow_passes_all_checks():
    w = make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.PROCESS)
    result = _validate(w)
    assert result.accepted is True
    assert result.report.verdict == "pass"
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert all(passed.values())
    # every check ran
    assert len(result.report.findings) == len(workflow_checks())


def test_all_expected_checks_present():
    ids = {c.check_id for c in workflow_checks()}
    expected = {
        "workflow-typed",
        "workflow-identified-objectbound",
        "workflow-value-fidelity",
        "workflow-classified",
        "workflow-sequences-steps",
        "workflow-steps-partition",
        "workflow-consumes-operation",
        "workflow-operations-partition",
        "workflow-holds-state",
        "workflow-sequence-explicit",
        "workflow-branch-determinacy",
        "workflow-process-records-state",
        "meta-class-single",
        "meta-relationships-closed",
        "meta-constraints",
        "founding-acyclic",
        "lifecycle-valid",
        "foundation-reuse-integrity",
        "behavior-by-reference",
        "technology-independence",
        "non-constitutive",
        "provisional-state-disclosure",
        "traceability-rooted",
    }
    assert ids == expected


def test_subject_projection_roundtrips_facts():
    w = make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.CONDITIONAL)
    subject = WorkflowValidationSubject.from_workflow(w, _trace(w))
    assert subject.meta_class == "AMC-05"
    assert subject.kind == "Conditional-Workflow"
    assert subject.sequenced_step_count == 2
    assert subject.consumed_operation_count == 1
    assert subject.arrangement_class == "conditional"
    assert subject.holds_state is True
    assert subject.branch_determinacy_holds is True
    assert subject.target_id.startswith("UCOS-WORKFLOW-")


def test_technology_bearing_workflow_fails_validation():
    techy = make_workflow("t", ("ENG-005:AMC-04:kafka.stream",), ONE_OP)
    result = _validate(techy)
    assert result.accepted is False
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["technology-independence"] is False


def test_secret_bearing_workflow_fails_non_constitutive():
    leaky = make_workflow("t", ("ENG-005:AMC-04:step",), ("ENG-005:SF-2:api_key.rotate",))
    result = _validate(leaky)
    assert result.accepted is False
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["non-constitutive"] is False


def test_empty_forward_trace_fails_traceability_only_at_trace_level():
    # A closed backward chain still roots traceability; forward emptiness affects
    # trace.closed (checked in realize), not the traceability-rooted check.
    w = make_workflow("t", SEQ, ONE_OP)
    result = validate_workflow(w, build_traceability(w, unit=REALIZATION_UNIT, forward=()))
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["traceability-rooted"] is True  # backward lineage is rooted + closed


def test_validation_is_deterministic():
    w = make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.PROCESS)
    a = _validate(w)
    b = _validate(w)
    assert a.report.to_dict() == b.report.to_dict()
    assert a.evidence.to_dict() == b.evidence.to_dict()


def test_lifecycle_state_variants_validate():
    for st in (WorkflowState.DEFINED, WorkflowState.EXECUTABLE, WorkflowState.RETIRED):
        w = make_workflow("t", SEQ, ONE_OP, state=st)
        assert _validate(w).accepted is True


def test_strict_mode_accepts_valid_workflow():
    w = make_workflow("t", SEQ, ONE_OP)
    result = validate_workflow(w, _trace(w), strict=True)
    assert result.accepted is True



# --- per-check negative coverage (crafted WorkflowValidationSubject via replace) ---

from dataclasses import replace  # noqa: E402

import pytest  # noqa: E402

from application.workflow_meta import WorkflowState as _WState  # noqa: E402
from engine.validation.errors import AcceptanceGateError  # noqa: E402


def _subject(workflow=None):
    workflow = workflow or make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.PROCESS)
    return WorkflowValidationSubject.from_workflow(workflow, _trace(workflow))


def _find(cid):
    return next(c for c in workflow_checks() if c.check_id == cid)


def test_typed_check_fails_on_empty_type():
    assert _find("workflow-typed").evaluate(replace(_subject(), type_tag="")).passed is False


def test_identified_check_fails_on_bad_prefix():
    subj = replace(_subject(), target_id="UCOS-FEATURE-xyz")
    assert _find("workflow-identified-objectbound").evaluate(subj).passed is False


def test_identified_check_fails_on_missing_digest():
    subj = replace(_subject(), value_digest="")
    assert _find("workflow-identified-objectbound").evaluate(subj).passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    subj = replace(_subject(), value_digest="not-a-hash")
    assert _find("workflow-value-fidelity").evaluate(subj).passed is False


def test_classified_check_fails_on_unknown_kind():
    subj = replace(_subject(), kind="Bogus-Workflow")
    assert _find("workflow-classified").evaluate(subj).passed is False


def test_sequences_steps_fails_when_none():
    subj = replace(_subject(), sequences_steps=False, sequenced_step_count=0)
    assert _find("workflow-sequences-steps").evaluate(subj).passed is False


def test_steps_partition_fails_when_not_partition():
    subj = replace(_subject(), steps_are_partition=False)
    assert _find("workflow-steps-partition").evaluate(subj).passed is False


def test_consumes_operation_fails_when_none():
    subj = replace(_subject(), consumes_operations=False, consumed_operation_count=0)
    assert _find("workflow-consumes-operation").evaluate(subj).passed is False


def test_consumes_operation_fails_when_count_zero_even_if_flag_true():
    subj = replace(_subject(), consumes_operations=True, consumed_operation_count=0)
    assert _find("workflow-consumes-operation").evaluate(subj).passed is False


def test_operations_partition_fails_when_not_partition():
    subj = replace(_subject(), operations_are_partition=False)
    assert _find("workflow-operations-partition").evaluate(subj).passed is False


def test_holds_state_fails_when_absent():
    subj = replace(_subject(), holds_state=False, state_ref="")
    assert _find("workflow-holds-state").evaluate(subj).passed is False


def test_sequence_explicit_fails_when_not_explicit():
    subj = replace(_subject(), sequence_is_explicit=False)
    assert _find("workflow-sequence-explicit").evaluate(subj).passed is False


def test_branch_determinacy_fails_when_broken():
    subj = replace(_subject(), branch_determinacy_holds=False)
    assert _find("workflow-branch-determinacy").evaluate(subj).passed is False


def test_process_records_state_fails_when_not_recorded():
    subj = replace(_subject(), records_intermediate_state=False)
    assert _find("workflow-process-records-state").evaluate(subj).passed is False


def test_meta_class_check_fails_on_wrong_class():
    subj = replace(_subject(), meta_class="AMC-04")
    assert _find("meta-class-single").evaluate(subj).passed is False


def test_meta_relationships_check_fails_outside_closure():
    subj = replace(_subject(), relationships=("AMR-04", "AMR-99"))
    assert _find("meta-relationships-closed").evaluate(subj).passed is False


def test_meta_constraints_fails_when_amk01_broken():
    subj = replace(_subject(), value_digest="")
    assert _find("meta-constraints").evaluate(subj).passed is False


def test_meta_constraints_fails_when_reference_unresolved():
    subj = replace(_subject(), references_resolve=False)
    assert _find("meta-constraints").evaluate(subj).passed is False


def test_meta_constraints_fails_when_sequence_or_consumption_incomplete():
    subj = replace(_subject(), sequence_is_explicit=False)
    assert _find("meta-constraints").evaluate(subj).passed is False
    subj2 = replace(_subject(), consumes_operations=False)
    assert _find("meta-constraints").evaluate(subj2).passed is False


def test_founding_acyclic_check_fails_when_flag_false():
    subj = replace(_subject(), founding_acyclic=False)
    assert _find("founding-acyclic").evaluate(subj).passed is False


def test_lifecycle_check_fails_on_bad_state():
    subj = replace(_subject(), lifecycle_state="BOGUS")
    assert _find("lifecycle-valid").evaluate(subj).passed is False


def test_lifecycle_check_passes_for_every_valid_state():
    check = _find("lifecycle-valid")
    for st in _WState:
        subj = replace(_subject(), lifecycle_state=st.value)
        assert check.evaluate(subj).passed is True


def test_reuse_integrity_fails_on_redefinition():
    subj = replace(_subject(), redefines_foundation=True)
    assert _find("foundation-reuse-integrity").evaluate(subj).passed is False


def test_reuse_integrity_fails_on_missing_substrate():
    subj = replace(_subject(), substrate_refs=())
    assert _find("foundation-reuse-integrity").evaluate(subj).passed is False


def test_behavior_by_reference_fails_on_empty():
    subj = replace(_subject(), behavior_ref="")
    assert _find("behavior-by-reference").evaluate(subj).passed is False


def test_technology_independence_fails_when_technology_selected():
    subj = replace(_subject(), selects_technology=True)
    assert _find("technology-independence").evaluate(subj).passed is False


def test_non_constitutive_fails_on_authority():
    subj = replace(_subject(), confers_authority=True)
    assert _find("non-constitutive").evaluate(subj).passed is False


def test_non_constitutive_fails_on_secret():
    subj = replace(_subject(), embeds_secret=True)
    assert _find("non-constitutive").evaluate(subj).passed is False


def test_provisional_disclosure_fails_when_absent():
    subj = replace(_subject(), disclosure={})
    assert _find("provisional-state-disclosure").evaluate(subj).passed is False


def test_traceability_rooted_fails_on_empty_chain():
    subj = replace(_subject(), provenance_chain=())
    assert _find("traceability-rooted").evaluate(subj).passed is False


def test_traceability_rooted_fails_on_wrong_head():
    subj = replace(_subject(), provenance_chain=("WRONG", "12-APPLICATION@b7e7657"))
    assert _find("traceability-rooted").evaluate(subj).passed is False


def test_traceability_rooted_fails_without_anchor():
    subj = replace(_subject(), provenance_chain=("AMC-05", "APPLICATION-009"))
    assert _find("traceability-rooted").evaluate(subj).passed is False


def test_strict_validation_raises_on_bad_workflow():
    techy = make_workflow("t", ("ENG-005:AMC-04:kafka.stream",), ONE_OP)
    trace = build_traceability(techy, unit=REALIZATION_UNIT, forward=("f1", "f2"))
    with pytest.raises(AcceptanceGateError):
        validate_workflow(techy, trace, strict=True)
