"""EC3-B10-U06 — Lifecycle validation tests (EC-1 PASS + V1…V5 + UDL-12 + VC)."""

from __future__ import annotations

from dataclasses import replace

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.lifecycle import forward_transitions, make_lifecycle, runtime_ref_for
from data.lifecycle_meta import LifecycleState
from data.lifecycle_traceability import build_lifecycle_traceability
from data.lifecycle_validation import (
    LifecycleValidationSubject,
    lifecycle_checks,
    validate_lifecycle,
)
from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict

ENTITY_NAME = "ucos.demo.entity"
LIFECYCLE_NAME = "ucos.demo.lifecycle"
STATE_REF = runtime_ref_for("state.defined")


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _lifecycle(**overrides):
    entity = overrides.pop("entity", None) or _entity()
    kwargs = dict(current_state=overrides.pop("current_state", LifecycleState.DEFINED))
    kwargs.update(overrides)
    transitions = kwargs.pop("transitions", forward_transitions())
    state_ref = kwargs.pop("state_ref", STATE_REF)
    name = kwargs.pop("name", LIFECYCLE_NAME)
    type_tag = kwargs.pop("type_tag", "ucos.core.lifecycle")
    return make_lifecycle(name, type_tag, entity, transitions, state_ref, **kwargs)


def _trace(lifecycle):
    return build_lifecycle_traceability(
        lifecycle, unit="EC3-B10-U06", forward=(lifecycle.lifecycle_id,)
    )


def test_validation_passes_and_is_accepted():
    lc = _lifecycle()
    result = validate_lifecycle(lc, _trace(lc))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    lc = _lifecycle()
    result = validate_lifecycle(lc, _trace(lc))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(lifecycle_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_v1_v5_all_hold():
    lc = _lifecycle()
    result = validate_lifecycle(lc, _trace(lc))
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["meta-class-single"]  # V1 (DMC-07)
    assert passed["meta-relationships-closed"]  # V2
    assert passed["meta-constraints"]  # V3 (DLA-K1/K3/K4)
    assert passed["founding-acyclic"]  # V4
    assert passed["lifecycle-valid"]  # V5


def test_lifecycle_governance_udl12_checks_present_and_pass():
    lc = _lifecycle()
    result = validate_lifecycle(lc, _trace(lc))
    passed = {f.check_id: f.passed for f in result.report.findings}
    for cid in (
        "lifecycle-typed",  # UDL-03 / DLA-K1
        "lifecycle-named",
        "lifecycle-identified",  # UDL-04/05
        "lifecycle-transitions-subject",  # DMR-06
        "lifecycle-states-closed",  # DLA-02
        "lifecycle-forward-only",  # DLA-01 / DLA-C1
        "lifecycle-transitions-guarded",  # DLA-04 / DLA-K4
        "lifecycle-transitions-recorded",  # DLA-03 / DMR-11
        "lifecycle-single-state",  # DLA-C5
        "lifecycle-behaves-by-reference",  # DMR-11 / DLA-07
        "lifecycle-independence",  # UDL-12 / DLA-K5
        "lifecycle-versioned",  # DLA-08 / UDL-12
        "lifecycle-classified",  # DXH-07
        "data-value-fidelity",  # UDL-06 (transitive)
        "foundation-reuse-integrity",  # UDL-02 / VC-5
        "non-constitutive",  # UDL-15 / DLA-09
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_shared_check_ids_present_for_cce_gate_reuse():
    # These ids are consumed by the reused DMC-01 CCE ten-gate suite.
    lc = _lifecycle()
    result = validate_lifecycle(lc, _trace(lc))
    ids = {f.check_id for f in result.report.findings}
    for cid in (
        "meta-class-single",
        "meta-relationships-closed",
        "foundation-reuse-integrity",
        "data-value-fidelity",
        "founding-acyclic",
        "provisional-state-disclosure",
        "traceability-rooted",
    ):
        assert cid in ids, cid


def test_subject_projection_is_deterministic():
    lc = _lifecycle()
    s1 = LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))
    s2 = LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))
    assert s1 == s2  # determinism at the subject boundary


def test_strict_acceptance_returns_decision_for_valid_lifecycle():
    lc = _lifecycle()
    result = validate_lifecycle(lc, _trace(lc), strict=True)
    assert result.accepted is True
    assert result.decision.accepted is True


def test_untraced_lifecycle_fails_traceability_gate():
    lc = _lifecycle()
    subject = LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))
    subject = replace(subject, provenance_chain=())  # orphaned lineage
    report = ValidationEngine(lifecycle_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


def test_secret_bearing_lifecycle_fails_non_constitutive_gate():
    lc = _lifecycle(name="api_key")
    result = validate_lifecycle(lc, _trace(lc))
    assert result.accepted is False
    assert "non-constitutive" in {f.check_id for f in result.report.blocking_failures}


def test_technology_naming_subject_fails_independence_gate():
    lc = _lifecycle()
    subject = LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))
    subject = replace(subject, names_technology=True)
    report = ValidationEngine(lifecycle_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "lifecycle-independence" in {f.check_id for f in report.blocking_failures}


def test_non_forward_only_subject_fails_gate():
    lc = _lifecycle()
    subject = LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))
    subject = replace(subject, forward_only=False, transition_pairs=(("ACTIVE", "DEFINED"),))
    report = ValidationEngine(lifecycle_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "lifecycle-forward-only" in {f.check_id for f in report.blocking_failures}


def test_unguarded_subject_fails_gate():
    lc = _lifecycle()
    subject = LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))
    subject = replace(subject, transitions_guarded=False, guard_refs=("not-a-guard",))
    report = ValidationEngine(lifecycle_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "lifecycle-transitions-guarded" in {f.check_id for f in report.blocking_failures}


def test_unrecorded_subject_fails_gate():
    lc = _lifecycle()
    subject = LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))
    subject = replace(subject, transitions_recorded=False, event_refs=("not-an-event",))
    report = ValidationEngine(lifecycle_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "lifecycle-transitions-recorded" in {f.check_id for f in report.blocking_failures}


def test_self_referencing_founding_subject_fails_acyclic_gate():
    lc = _lifecycle()
    subject = LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))
    subject = replace(subject, founding_acyclic=False)
    report = ValidationEngine(lifecycle_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "founding-acyclic" in {f.check_id for f in report.blocking_failures}


def test_non_runtime_binding_subject_fails_behavior_gate():
    lc = _lifecycle()
    subject = LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))
    subject = replace(subject, binds_runtime_by_reference=False)
    report = ValidationEngine(lifecycle_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "lifecycle-behaves-by-reference" in {f.check_id for f in report.blocking_failures}


def test_non_certified_subject_fails_transitions_subject_gate():
    lc = _lifecycle()
    subject = LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))
    subject = replace(subject, transitioned_entity_id="NOT-AN-ENTITY")
    report = ValidationEngine(lifecycle_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "lifecycle-transitions-subject" in {f.check_id for f in report.blocking_failures}


import pytest

from engine.validation.executor import ValidationEngine


def _subject():
    lc = _lifecycle()
    return LifecycleValidationSubject.from_lifecycle(lc, _trace(lc))


def _run(subject):
    return ValidationEngine(lifecycle_checks()).validate(subject)


@pytest.mark.parametrize(
    ("overrides", "expected_check"),
    [
        ({"type_tag": "  "}, "lifecycle-typed"),
        ({"name": "  "}, "lifecycle-named"),
        ({"target_id": "NOT-A-LIFECYCLE"}, "lifecycle-identified"),
        ({"value_digest": "zz"}, "data-value-fidelity"),
        ({"states_closed": False}, "lifecycle-states-closed"),
        ({"states": ("DEFINED", "BOGUS")}, "lifecycle-states-closed"),
        ({"single_state": False}, "lifecycle-single-state"),
        ({"current_state": "BOGUS"}, "lifecycle-single-state"),
        ({"classified": False, "facet": "Bogus-Facet"}, "lifecycle-classified"),
        ({"version": "  "}, "lifecycle-versioned"),
        ({"meta_class": "DMC-99"}, "meta-class-single"),
        ({"relationships": ("DMR-06", "DMR-99")}, "meta-relationships-closed"),
        ({"lifecycle_state": "BOGUS"}, "lifecycle-valid"),
        ({"redefines_el1": True}, "foundation-reuse-integrity"),
        ({"substrate_refs": ()}, "foundation-reuse-integrity"),
        ({"confers_authority": True}, "non-constitutive"),
        ({"state_ref": "not-a-runtime-ref"}, "lifecycle-behaves-by-reference"),
    ],
)
def test_each_guard_fails_closed(overrides, expected_check):
    subject = replace(_subject(), **overrides)
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert expected_check in {f.check_id for f in report.blocking_failures}


def test_meta_constraints_fail_when_not_forward_only():
    subject = replace(_subject(), forward_only=False, transition_pairs=(("ACTIVE", "DEFINED"),))
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    failed = {f.check_id for f in report.blocking_failures}
    assert "meta-constraints" in failed


def test_disclosure_absent_fails_provisional_gate():
    subject = replace(_subject(), disclosure={})
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert "provisional-state-disclosure" in {f.check_id for f in report.blocking_failures}


def test_guard_ref_malformed_fails_guarded_gate():
    subject = replace(_subject(), guard_refs=("bad-guard",))
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert "lifecycle-transitions-guarded" in {f.check_id for f in report.blocking_failures}


def test_event_ref_malformed_fails_recorded_gate():
    subject = replace(_subject(), event_refs=("bad-event",))
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert "lifecycle-transitions-recorded" in {f.check_id for f in report.blocking_failures}


def test_absorbing_subject_fails_transitions_subject_gate():
    subject = replace(_subject(), absorbs_subject=True)
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert "lifecycle-transitions-subject" in {f.check_id for f in report.blocking_failures}


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    assert_every_check_can_refuse(_subject(), lifecycle_checks())
