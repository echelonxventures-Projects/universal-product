"""EC3-B10-U08 — Quality validation tests (EC-1 PASS + V1…V5 + UDL-14 + VC)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.quality import make_measurements, make_quality, policy_ref_for
from data.quality_meta import QualityKind
from data.quality_traceability import build_quality_traceability
from data.quality_validation import (
    QualityValidationSubject,
    quality_checks,
    validate_quality,
)
from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine

ENTITY_NAME = "ucos.demo.entity"
QUALITY_NAME = "ucos.demo.quality"
POLICY_REF = policy_ref_for("quality.udl")
SCHEMA_REF = "UCOS-SCHEMA-REF:ucos.demo.schema"


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _quality(**overrides):
    entity = overrides.pop("entity", None) or _entity()
    kwargs = dict(
        kind=overrides.pop("kind", QualityKind.COMPLETENESS_MEASURE),
        measurements=overrides.pop(
            "measurements", make_measurements((("completeness", True, 100),))
        ),
        schema_ref=overrides.pop("schema_ref", SCHEMA_REF),
    )
    kwargs.update(overrides)
    policy_ref = kwargs.pop("policy_ref", POLICY_REF)
    name = kwargs.pop("name", QUALITY_NAME)
    type_tag = kwargs.pop("type_tag", "ucos.core.quality")
    return make_quality(name, type_tag, entity, policy_ref, **kwargs)


def _trace(quality):
    return build_quality_traceability(quality, unit="EC3-B10-U08", forward=(quality.quality_id,))


def test_validation_passes_and_is_accepted():
    q = _quality()
    result = validate_quality(q, _trace(q))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    q = _quality()
    result = validate_quality(q, _trace(q))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(quality_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_v1_v5_all_hold():
    q = _quality()
    result = validate_quality(q, _trace(q))
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["meta-class-single"]  # V1 (DMC-09)
    assert passed["meta-relationships-closed"]  # V2
    assert passed["meta-constraints"]  # V3 (DQA-K1/K2/K3/K4/K5)
    assert passed["founding-acyclic"]  # V4
    assert passed["quality-valid"]  # V5


def test_quality_udl14_checks_present_and_pass():
    q = _quality()
    result = validate_quality(q, _trace(q))
    passed = {f.check_id: f.passed for f in result.report.findings}
    for cid in (
        "quality-typed",  # UDL-03 / DQA-K1
        "quality-named",
        "quality-identified",  # UDL-04/05
        "quality-measures-subject",  # DMR-08
        "quality-evaluative",  # DQA-01 / DQA-K2
        "quality-dimensioned",  # DQA-02 / DXC-02
        "quality-non-remediating",  # DQA-03 / UDL-14
        "quality-recorded",  # DQA-04 / DQA-K4
        "quality-binds-policy-by-reference",  # DMR-11 / DQA-06
        "quality-measurement-recorded",  # DQA-C1
        "quality-schema-relative",  # DQA-05 / DQA-C2
        "quality-independence",  # UDL-14 / DQA-K5
        "quality-versioned",  # DQA-08 / UDL-12
        "quality-classified",  # DXH-09
        "data-value-fidelity",  # UDL-06 (transitive)
        "foundation-reuse-integrity",  # UDL-02 / VC-5
        "non-constitutive",  # UDL-15 / DQA-09
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_shared_check_ids_present_for_cce_gate_reuse():
    # These ids are consumed by the reused DMC-01 CCE ten-gate suite.
    q = _quality()
    result = validate_quality(q, _trace(q))
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
    q = _quality()
    s1 = QualityValidationSubject.from_quality(q, _trace(q))
    s2 = QualityValidationSubject.from_quality(q, _trace(q))
    assert s1 == s2  # determinism at the subject boundary


def test_strict_acceptance_returns_decision_for_valid_quality():
    q = _quality()
    result = validate_quality(q, _trace(q), strict=True)
    assert result.accepted is True
    assert result.decision.accepted is True


def test_untraced_quality_fails_traceability_gate():
    q = _quality()
    subject = QualityValidationSubject.from_quality(q, _trace(q))
    subject = replace(subject, provenance_chain=())  # orphaned lineage
    report = ValidationEngine(quality_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


def test_secret_bearing_quality_fails_non_constitutive_gate():
    q = _quality(name="api_key")
    result = validate_quality(q, _trace(q))
    assert result.accepted is False
    assert "non-constitutive" in {f.check_id for f in result.report.blocking_failures}


def _subject():
    q = _quality()
    return QualityValidationSubject.from_quality(q, _trace(q))


def _run(subject):
    return ValidationEngine(quality_checks()).validate(subject)


def test_remediating_subject_fails_non_remediating_gate():
    report = _run(replace(_subject(), remediates=True))
    assert report.verdict is Verdict.FAIL
    assert "quality-non-remediating" in {f.check_id for f in report.blocking_failures}


def test_enforcing_subject_fails_non_remediating_gate():
    report = _run(replace(_subject(), enforces=True))
    assert report.verdict is Verdict.FAIL
    assert "quality-non-remediating" in {f.check_id for f in report.blocking_failures}


def test_access_granting_subject_fails_non_constitutive_gate():
    report = _run(replace(_subject(), grants_access=True))
    assert report.verdict is Verdict.FAIL
    assert "non-constitutive" in {f.check_id for f in report.blocking_failures}


def test_authority_conferring_subject_fails_non_constitutive_gate():
    report = _run(replace(_subject(), confers_authority=True))
    assert report.verdict is Verdict.FAIL
    assert "non-constitutive" in {f.check_id for f in report.blocking_failures}


def test_technology_naming_subject_fails_independence_gate():
    report = _run(replace(_subject(), names_technology=True))
    assert report.verdict is Verdict.FAIL
    assert "quality-independence" in {f.check_id for f in report.blocking_failures}


def test_selects_technology_subject_fails_independence_gate():
    report = _run(replace(_subject(), selects_technology=True))
    assert report.verdict is Verdict.FAIL
    assert "quality-independence" in {f.check_id for f in report.blocking_failures}


def test_image_reference_subject_fails_independence_gate():
    report = _run(replace(_subject(), image_reference="quay.io/x:1"))
    assert report.verdict is Verdict.FAIL
    assert "quality-independence" in {f.check_id for f in report.blocking_failures}


def test_non_recorded_subject_fails_recorded_gate():
    report = _run(replace(_subject(), recorded=False))
    assert report.verdict is Verdict.FAIL
    assert "quality-recorded" in {f.check_id for f in report.blocking_failures}


def test_non_evaluative_subject_fails_evaluative_gate():
    report = _run(replace(_subject(), evaluative=False))
    assert report.verdict is Verdict.FAIL
    assert "quality-evaluative" in {f.check_id for f in report.blocking_failures}


def test_non_certified_subject_fails_measures_subject_gate():
    report = _run(replace(_subject(), measured_construct_id="NOT-A-CONSTRUCT"))
    assert report.verdict is Verdict.FAIL
    assert "quality-measures-subject" in {f.check_id for f in report.blocking_failures}


def test_absorbing_subject_fails_measures_subject_gate():
    report = _run(replace(_subject(), absorbs_measured=True))
    assert report.verdict is Verdict.FAIL
    assert "quality-measures-subject" in {f.check_id for f in report.blocking_failures}


def test_non_dimensioned_subject_fails_dimensioned_gate():
    report = _run(replace(_subject(), dimensioned=False, measured_dimensions=()))
    assert report.verdict is Verdict.FAIL
    assert "quality-dimensioned" in {f.check_id for f in report.blocking_failures}


def test_non_measurement_recording_subject_fails_measurement_gate():
    report = _run(replace(_subject(), records_measurement=False))
    assert report.verdict is Verdict.FAIL
    assert "quality-measurement-recorded" in {f.check_id for f in report.blocking_failures}


def test_non_schema_relative_subject_fails_schema_gate():
    report = _run(replace(_subject(), schema_relative=False))
    assert report.verdict is Verdict.FAIL
    assert "quality-schema-relative" in {f.check_id for f in report.blocking_failures}


def test_non_policy_binding_subject_fails_policy_gate():
    report = _run(replace(_subject(), binds_policy_by_reference=False))
    assert report.verdict is Verdict.FAIL
    assert "quality-binds-policy-by-reference" in {f.check_id for f in report.blocking_failures}


def test_non_acyclic_founding_subject_fails_acyclic_gate():
    report = _run(replace(_subject(), founding_acyclic=False))
    assert report.verdict is Verdict.FAIL
    assert "founding-acyclic" in {f.check_id for f in report.blocking_failures}


def test_misrooted_lineage_fails_traceability_gate():
    # chain contains the 10-DATA anchor but is not rooted at the meta-class.
    subject = replace(_subject(), provenance_chain=("WRONG-ROOT", "10-DATA@b7e7657"))
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


def test_lineage_without_anchor_fails_traceability_gate():
    # chain is rooted at the meta-class but never closes to the 10-DATA anchor.
    subject = replace(_subject(), provenance_chain=("DMC-09", "DATA-013", "DATA-001"))
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


@pytest.mark.parametrize(
    ("overrides", "expected_check"),
    [
        ({"type_tag": "  "}, "quality-typed"),
        ({"name": "  "}, "quality-named"),
        ({"target_id": "NOT-A-QUALITY"}, "quality-identified"),
        ({"value_digest": "zz"}, "data-value-fidelity"),
        ({"classified": False, "kind": ""}, "quality-classified"),
        ({"version": "  "}, "quality-versioned"),
        ({"meta_class": "DMC-99"}, "meta-class-single"),
        ({"relationships": ("DMR-08", "DMR-99")}, "meta-relationships-closed"),
        ({"quality_state": "BOGUS"}, "quality-valid"),
        ({"redefines_el1": True}, "foundation-reuse-integrity"),
        ({"substrate_refs": ()}, "foundation-reuse-integrity"),
        ({"embeds_secret": True}, "non-constitutive"),
        ({"policy_ref": "not-a-policy-ref"}, "quality-binds-policy-by-reference"),
    ],
)
def test_each_guard_fails_closed(overrides, expected_check):
    subject = replace(_subject(), **overrides)
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert expected_check in {f.check_id for f in report.blocking_failures}


def test_meta_constraints_fail_when_remediating():
    report = _run(replace(_subject(), remediates=True))
    assert report.verdict is Verdict.FAIL
    assert "meta-constraints" in {f.check_id for f in report.blocking_failures}


def test_disclosure_absent_fails_provisional_gate():
    report = _run(replace(_subject(), disclosure={}))
    assert report.verdict is Verdict.FAIL
    assert "provisional-state-disclosure" in {f.check_id for f in report.blocking_failures}


def test_non_runtime_policy_ref_fails_reuse_integrity_gate():
    subject = replace(_subject(), binds_policy_by_reference=False)
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert "foundation-reuse-integrity" in {f.check_id for f in report.blocking_failures}


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    assert_every_check_can_refuse(_subject(), quality_checks())
