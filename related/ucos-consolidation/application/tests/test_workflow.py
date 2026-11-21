"""EC3-B12-U05 — Workflow construct tests (AMC-05 + AMK-01/02/03/05/07 + UAL-03/10/12)."""

from __future__ import annotations

import pytest

from application.workflow import Workflow, WorkflowError, make_workflow
from application.workflow_meta import (
    WORKFLOW_META_CLASS,
    WORKFLOW_RELATIONSHIPS,
    WorkflowKind,
    WorkflowState,
)

SEQ = (
    "ENG-005:AMC-04:ucos.demo.feature.a",
    "ENG-005:AMC-04:ucos.demo.feature.b",
)
ONE_STEP = ("ENG-005:AMC-04:ucos.demo.feature.a",)
OPS = (
    "ENG-005:SF-2:ucos.demo.operation.a",
    "ENG-005:SF-2:ucos.demo.operation.b",
)
ONE_OP = ("ENG-005:SF-2:ucos.demo.operation.a",)


def test_workflow_is_typed_identified_and_sequences_and_consumes():
    w = make_workflow("ucos.demo.workflow", SEQ, ONE_OP)
    assert w.meta_class == WORKFLOW_META_CLASS  # V1 (AMC-05)
    assert w.type_tag == "ucos.demo.workflow"  # UAL-03 typed
    assert w.workflow_id.startswith("UCOS-WORKFLOW-")  # UAL-04 identified (ENG-001)
    assert len(w.value_digest) == 64  # ENG-003 value fidelity
    assert w.kind is WorkflowKind.SEQUENTIAL  # AXH-05 classified
    assert w.sequences_steps() is True  # AMR-04 / WKF-04 (the defining relationship)
    assert w.consumes_operations() is True  # AMR-13
    assert w.holds_state() is True  # AMR-06 / WKF-06 (the NEW relationship)
    assert w.sequenced_step_count() == 2
    assert w.consumed_operation_count() == 1


def test_workflow_identity_is_deterministic_and_core_derived():
    a = make_workflow("t", SEQ, OPS)
    b = make_workflow("t", SEQ, OPS)
    c = make_workflow("t", ONE_STEP, OPS)
    assert a.workflow_id == b.workflow_id  # same core → same ENG-001 identity
    assert a.workflow_id != c.workflow_id  # different sequence → different identity


def test_sequence_order_is_identity_defining():
    # A workflow is an ORDERED arrangement — sequence order IS identity-defining
    # (unlike a Feature's unordered operation set).
    a = make_workflow("t", ("ENG-005:x", "ENG-005:y"), ONE_OP)
    b = make_workflow("t", ("ENG-005:y", "ENG-005:x"), ONE_OP)
    assert a.workflow_id != b.workflow_id  # order matters for the arrangement


def test_consumed_operations_are_order_independent_for_identity():
    a = make_workflow("t", SEQ, ("ENG-005:SF-2:x", "ENG-005:SF-2:y"))
    b = make_workflow("t", SEQ, ("ENG-005:SF-2:y", "ENG-005:SF-2:x"))
    assert a.workflow_id == b.workflow_id  # operations are a set (partition); order-independent


def test_workflow_is_immutable_objecthood():
    w = make_workflow("t", SEQ, ONE_OP)
    with pytest.raises((AttributeError, TypeError)):
        w.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_workflow_is_rejected_fail_closed():
    with pytest.raises(WorkflowError):
        make_workflow("", SEQ, ONE_OP)  # UAL-03 — no untyped workflow may exist
    with pytest.raises(WorkflowError):
        make_workflow("   ", SEQ, ONE_OP)


def test_non_string_type_tag_is_rejected():
    with pytest.raises(WorkflowError):
        Workflow(  # type: ignore[arg-type]
            type_tag=object(),
            kind=WorkflowKind.SEQUENTIAL,
            sequence_refs=SEQ,
            operation_refs=ONE_OP,
        )


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(WorkflowError):
        Workflow(  # type: ignore[arg-type]
            type_tag="t", kind="not-a-kind", sequence_refs=SEQ, operation_refs=ONE_OP
        )


def test_workflow_without_sequence_is_rejected():
    with pytest.raises(WorkflowError):
        make_workflow("t", (), ONE_OP)  # AMR-04 / WKF-04 — must sequence ≥1 step


def test_non_tuple_sequence_refs_is_rejected():
    with pytest.raises(WorkflowError):
        Workflow(  # type: ignore[arg-type]
            type_tag="t", kind=WorkflowKind.SEQUENTIAL, sequence_refs=["a"], operation_refs=ONE_OP
        )


def test_empty_sequence_reference_is_rejected():
    with pytest.raises(WorkflowError):
        make_workflow("t", ("ENG-005:a", ""), ONE_OP)  # AMR-04 — each step non-empty
    with pytest.raises(WorkflowError):
        make_workflow("t", ("   ",), ONE_OP)


def test_duplicate_sequenced_step_is_rejected_partition():
    with pytest.raises(WorkflowError):
        make_workflow("t", ("ENG-005:a", "ENG-005:a"), ONE_OP)  # WKF-C1 partition


def test_conditional_workflow_requires_two_or_more_steps():
    with pytest.raises(WorkflowError):
        make_workflow("t", ONE_STEP, ONE_OP, kind=WorkflowKind.CONDITIONAL)  # AXH-05 / WKF-05
    w = make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.CONDITIONAL)  # ≥2 → ok
    assert w.sequenced_step_count() == 2


def test_workflow_without_operation_is_rejected():
    with pytest.raises(WorkflowError):
        make_workflow("t", SEQ, ())  # AMR-13 / WKF-K4 — steps must consume ≥1 operation


def test_non_tuple_operation_refs_is_rejected():
    with pytest.raises(WorkflowError):
        Workflow(  # type: ignore[arg-type]
            type_tag="t",
            kind=WorkflowKind.SEQUENTIAL,
            sequence_refs=SEQ,
            operation_refs=["a"],
        )


def test_empty_operation_reference_is_rejected():
    with pytest.raises(WorkflowError):
        make_workflow("t", SEQ, ("ENG-005:SF-2:a", ""))  # AMR-13 — each op ref non-empty
    with pytest.raises(WorkflowError):
        make_workflow("t", SEQ, ("   ",))


def test_duplicate_operation_is_rejected_partition():
    with pytest.raises(WorkflowError):
        make_workflow("t", SEQ, ("ENG-005:SF-2:a", "ENG-005:SF-2:a"))  # WKF-K4 partition


def test_missing_state_or_behavior_reference_is_rejected():
    with pytest.raises(WorkflowError):
        make_workflow("t", SEQ, ONE_OP, state_ref="")  # AMR-06 / WKF-06
    with pytest.raises(WorkflowError):
        make_workflow("t", SEQ, ONE_OP, behavior_ref="")  # AMR-11 / UAL-10


def test_workflow_cannot_sequence_its_state_or_behavior():
    st = "ENG-005:AMC-07:ucos.state"
    with pytest.raises(WorkflowError):
        make_workflow("t", (st,), ONE_OP, state_ref=st)  # WKF-C2 acyclic guard
    beh = "ENG-005:RL-F2:runtime.wf"
    with pytest.raises(WorkflowError):
        make_workflow("t", (beh,), ONE_OP, behavior_ref=beh)  # WKF-C2 acyclic guard


def test_workflow_cannot_consume_its_state_or_behavior_as_operation():
    st = "ENG-005:AMC-07:ucos.state"
    with pytest.raises(WorkflowError):
        make_workflow("t", SEQ, (st,), state_ref=st)  # WKF-C2 / AMK-03 acyclic guard
    beh = "ENG-005:RL-F2:runtime.wf"
    with pytest.raises(WorkflowError):
        make_workflow("t", SEQ, (beh,), behavior_ref=beh)  # WKF-C2 / AMK-03 acyclic guard


def test_bad_state_is_rejected_fail_closed():
    with pytest.raises(WorkflowError):
        Workflow(
            type_tag="t",
            kind=WorkflowKind.SEQUENTIAL,
            sequence_refs=SEQ,
            operation_refs=ONE_OP,
            state="BAD",  # type: ignore[arg-type]
        )


def test_relationships_are_within_amr_closure():
    w = make_workflow("t", SEQ, ONE_OP)
    assert set(w.meta_relationships()) <= set(f"AMR-{n:02d}" for n in range(1, 15))  # V2
    assert w.meta_relationships() == (
        "AMR-04",
        "AMR-06",
        "AMR-10",
        "AMR-11",
        "AMR-13",
    )
    assert w.meta_relationships() == WORKFLOW_RELATIONSHIPS


def test_workflow_uses_sequenced_by_and_holds_state_but_not_delivers_or_groups():
    # The distinctive AMC-05 relationship set: uses AMR-04 (sequenced-by, NEW) + AMR-06
    # (holds-state, NEW) and does NOT use AMR-01 (delivers), AMR-03 (groups),
    # AMR-05 (engaged-through), AMR-07 (assembled-by), or AMR-14 (presents-data).
    rels = set(make_workflow("t", SEQ, ONE_OP).meta_relationships())
    assert {"AMR-04", "AMR-06"} <= rels
    for absent in ("AMR-01", "AMR-02", "AMR-03", "AMR-05", "AMR-07", "AMR-12", "AMR-14"):
        assert absent not in rels


def test_lifecycle_is_forward_only():
    w = make_workflow("t", SEQ, ONE_OP, state=WorkflowState.DEFINED)
    composed = w.transition(WorkflowState.COMPOSED)
    assert composed.state is WorkflowState.COMPOSED
    ctx = composed.transition(WorkflowState.CONTEXTUALIZED)
    assert ctx.state is WorkflowState.CONTEXTUALIZED
    executable = ctx.transition(WorkflowState.EXECUTABLE)
    assert executable.state is WorkflowState.EXECUTABLE
    with pytest.raises(WorkflowError):
        executable.transition(WorkflowState.DEFINED)  # UAL-12 / WKF-C3 — no backward


def test_transition_to_same_state_is_allowed():
    w = make_workflow("t", SEQ, ONE_OP, state=WorkflowState.COMPOSED)
    same = w.transition(WorkflowState.COMPOSED)  # not backward (forward-or-equal)
    assert same.state is WorkflowState.COMPOSED


def test_transition_rejects_non_state_target():
    w = make_workflow("t", SEQ, ONE_OP)
    with pytest.raises(WorkflowError):
        w.transition("EXECUTABLE")  # type: ignore[arg-type]


def test_all_workflow_kinds_construct():
    assert make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.SEQUENTIAL).kind is (
        WorkflowKind.SEQUENTIAL
    )
    assert make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.CONDITIONAL).kind is (
        WorkflowKind.CONDITIONAL
    )
    assert make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.PROCESS).kind is WorkflowKind.PROCESS


def test_arrangement_class_reflects_kind():
    assert make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.SEQUENTIAL).arrangement_class() == (
        "sequential"
    )
    assert make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.CONDITIONAL).arrangement_class() == (
        "conditional"
    )
    assert make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.PROCESS).arrangement_class() == (
        "process"
    )


def test_references_resolve_and_founding_acyclic():
    w = make_workflow("t", SEQ, ONE_OP)
    assert w.references_resolve() is True  # AOI-03 / AMK-05/07
    assert w.is_founding_acyclic() is True  # V4 / AMK-03 / WKF-C2


def test_sequence_explicit_and_branch_determinacy_and_process_records_state():
    seq_wf = make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.SEQUENTIAL)
    assert seq_wf.sequence_is_explicit() is True  # WKF-C1 / UAL-10
    assert seq_wf.branch_determinacy_holds() is True  # WKF-05 (≥1 step)
    assert seq_wf.records_intermediate_state() is True  # non-process → trivially True
    assert seq_wf.steps_are_partition() is True  # WKF-C1
    assert seq_wf.operations_are_partition() is True  # WKF-K4
    assert seq_wf.sequences_step(SEQ[0]) is True  # AMR-04
    assert seq_wf.sequences_step("ENG-005:not-sequenced") is False
    assert seq_wf.consumes_operation(ONE_OP[0]) is True  # AMR-13
    assert seq_wf.consumes_operation("ENG-005:SF-2:not-consumed") is False

    cond_wf = make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.CONDITIONAL)
    assert cond_wf.branch_determinacy_holds() is True  # ≥2 branches

    proc_wf = make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.PROCESS)
    assert proc_wf.records_intermediate_state() is True  # WKF-07 / WKF-C5 (holds state)


def test_non_constitutive_and_no_secret_no_technology():
    w = make_workflow("t", SEQ, ONE_OP)
    assert w.confers_authority() is False  # UAL-15 / WKF-09 / C7
    assert w.redefines_foundation() is False  # UAL-02 / AMI-05
    assert w.selects_technology() is False  # UAL-15 (abstract references only)
    assert w.embeds_secret() is False


def test_technology_bearing_workflow_is_detected():
    techy = make_workflow("t", ("ENG-005:AMC-04:airflow.dag",), ONE_OP)
    assert techy.selects_technology() is True  # UAL-15 — concrete engine named


def test_secret_bearing_workflow_is_detected():
    leaky = make_workflow("t", ("ENG-005:AMC-04:password-reset",), ONE_OP)
    assert leaky.embeds_secret() is True  # UAL-15 / RR-07


def test_workflow_to_dict_records_substrate_reuse():
    w = make_workflow("t", SEQ, OPS, kind=WorkflowKind.PROCESS)
    payload = w.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
        "SF-2",
    ]
    assert payload["meta_class"] == "AMC-05"
    assert payload["kind"] == "Process-Workflow"
    assert payload["sequenced_step_count"] == 2
    assert payload["consumed_operation_count"] == 2
    assert payload["sequence_explicit"] is True
    assert payload["holds_state"] is True
    assert payload["arrangement_class"] == "process"
    assert payload["state"] == "DEFINED"
    # sequence_refs preserve order (ordered arrangement); operations are canonically sorted
    assert payload["sequence_refs"] == list(SEQ)
    assert payload["operation_refs"] == sorted(OPS)


def test_canonical_core_excludes_state_and_id():
    w = make_workflow("t", SEQ, ONE_OP)
    core = w.canonical_core()
    assert "state" not in core  # lifecycle is not identity-defining
    assert "workflow_id" not in core
    assert core["meta_class"] == "AMC-05"
    assert core["sequence_refs"] == list(SEQ)  # order preserved
    assert core["operation_refs"] == sorted(ONE_OP)


def test_state_does_not_change_identity():
    a = make_workflow("t", SEQ, ONE_OP, state=WorkflowState.DEFINED)
    b = make_workflow("t", SEQ, ONE_OP, state=WorkflowState.COMPOSED)
    assert a.workflow_id == b.workflow_id  # identity is core-derived, not state


def test_workflow_type_is_the_realized_construct():
    assert isinstance(make_workflow("t", SEQ, ONE_OP), Workflow)
