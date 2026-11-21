"""EC3-B10-U09 — Security validation tests (EC-1 PASS + V1…V5 + UDL-14 + VC)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.security import make_classifications, make_security, policy_ref_for
from data.security_meta import SecurityKind
from data.security_traceability import build_security_traceability
from data.security_validation import (
    SecurityValidationSubject,
    security_checks,
    validate_security,
)
from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine

ENTITY_NAME = "ucos.demo.entity"
SECURITY_NAME = "ucos.demo.security"
POLICY_REF = policy_ref_for("security.udl")


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _security(**overrides):
    entity = overrides.pop("entity", None) or _entity()
    kwargs = dict(
        kind=overrides.pop("kind", SecurityKind.CLASSIFICATION_LABEL),
        classifications=overrides.pop(
            "classifications", make_classifications((("sensitivity", True, 1),))
        ),
    )
    kwargs.update(overrides)
    policy_ref = kwargs.pop("policy_ref", POLICY_REF)
    name = kwargs.pop("name", SECURITY_NAME)
    type_tag = kwargs.pop("type_tag", "ucos.core.security")
    return make_security(name, type_tag, entity, policy_ref, **kwargs)


def _trace(security):
    return build_security_traceability(
        security, unit="EC3-B10-U09", forward=(security.security_id,)
    )


def test_validation_passes_and_is_accepted():
    s = _security()
    result = validate_security(s, _trace(s))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    s = _security()
    result = validate_security(s, _trace(s))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(security_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_v1_v5_all_hold():
    s = _security()
    result = validate_security(s, _trace(s))
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["meta-class-single"]  # V1 (DMC-10)
    assert passed["meta-relationships-closed"]  # V2
    assert passed["meta-constraints"]  # V3 (DZA-K1/K2/K3/K4/K5)
    assert passed["founding-acyclic"]  # V4
    assert passed["security-valid"]  # V5


def test_security_udl14_checks_present_and_pass():
    s = _security()
    result = validate_security(s, _trace(s))
    passed = {f.check_id: f.passed for f in result.report.findings}
    for cid in (
        "security-typed",  # UDL-03 / DZA-K1
        "security-named",
        "security-identified",  # UDL-04/05
        "security-classifies-subject",  # DMR-09
        "security-evaluative",  # DZA-01 / DZA-K2
        "security-dimensioned",  # DZA-02 / DXC-02
        "security-non-enforcing",  # DZA-01 / UDL-14
        "security-recorded",  # DZA-04 / DZA-K4
        "security-binds-policy-by-reference",  # DMR-11 / DZA-06
        "security-classification-recorded",  # DZA-C1
        "security-enforcement-by-reference",  # DZA-03 / DZA-C3
        "security-independence",  # UDL-14 / DZA-K5
        "security-versioned",  # DZA-08 / UDL-12
        "security-classified",  # DXH-10
        "data-value-fidelity",  # UDL-06 (transitive)
        "foundation-reuse-integrity",  # UDL-02 / VC-5
        "non-constitutive",  # UDL-15 / DZA-09
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_shared_check_ids_present_for_cce_gate_reuse():
    # These ids are consumed by the reused DMC-01 CCE ten-gate suite.
    s = _security()
    result = validate_security(s, _trace(s))
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
    s = _security()
    s1 = SecurityValidationSubject.from_security(s, _trace(s))
    s2 = SecurityValidationSubject.from_security(s, _trace(s))
    assert s1 == s2  # determinism at the subject boundary


def test_strict_acceptance_returns_decision_for_valid_security():
    s = _security()
    result = validate_security(s, _trace(s), strict=True)
    assert result.accepted is True
    assert result.decision.accepted is True


def test_untraced_security_fails_traceability_gate():
    s = _security()
    subject = SecurityValidationSubject.from_security(s, _trace(s))
    subject = replace(subject, provenance_chain=())  # orphaned lineage
    report = ValidationEngine(security_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


def test_secret_bearing_security_fails_non_constitutive_gate():
    s = _security(name="api_key")
    result = validate_security(s, _trace(s))
    assert result.accepted is False
    assert "non-constitutive" in {f.check_id for f in result.report.blocking_failures}


def _subject():
    s = _security()
    return SecurityValidationSubject.from_security(s, _trace(s))


def _run(subject):
    return ValidationEngine(security_checks()).validate(subject)


def test_enforcing_subject_fails_non_enforcing_gate():
    report = _run(replace(_subject(), enforces=True))
    assert report.verdict is Verdict.FAIL
    assert "security-non-enforcing" in {f.check_id for f in report.blocking_failures}


def test_access_granting_subject_fails_non_enforcing_gate():
    report = _run(replace(_subject(), grants_access=True))
    assert report.verdict is Verdict.FAIL
    assert "security-non-enforcing" in {f.check_id for f in report.blocking_failures}


def test_access_granting_subject_fails_non_constitutive_gate():
    report = _run(replace(_subject(), grants_access=True))
    assert report.verdict is Verdict.FAIL
    assert "non-constitutive" in {f.check_id for f in report.blocking_failures}


def test_authority_conferring_subject_fails_non_constitutive_gate():
    report = _run(replace(_subject(), confers_authority=True))
    assert report.verdict is Verdict.FAIL
    assert "non-constitutive" in {f.check_id for f in report.blocking_failures}


def test_enforcing_subject_fails_enforcement_by_reference_gate():
    report = _run(replace(_subject(), enforces=True))
    assert report.verdict is Verdict.FAIL
    assert "security-enforcement-by-reference" in {f.check_id for f in report.blocking_failures}


def test_non_reference_enforcement_subject_fails_enforcement_gate():
    report = _run(replace(_subject(), enforcement_by_reference=False))
    assert report.verdict is Verdict.FAIL
    assert "security-enforcement-by-reference" in {f.check_id for f in report.blocking_failures}


def test_technology_naming_subject_fails_independence_gate():
    report = _run(replace(_subject(), names_technology=True))
    assert report.verdict is Verdict.FAIL
    assert "security-independence" in {f.check_id for f in report.blocking_failures}


def test_selects_technology_subject_fails_independence_gate():
    report = _run(replace(_subject(), selects_technology=True))
    assert report.verdict is Verdict.FAIL
    assert "security-independence" in {f.check_id for f in report.blocking_failures}


def test_image_reference_subject_fails_independence_gate():
    report = _run(replace(_subject(), image_reference="quay.io/x:1"))
    assert report.verdict is Verdict.FAIL
    assert "security-independence" in {f.check_id for f in report.blocking_failures}


def test_non_recorded_subject_fails_recorded_gate():
    report = _run(replace(_subject(), recorded=False))
    assert report.verdict is Verdict.FAIL
    assert "security-recorded" in {f.check_id for f in report.blocking_failures}


def test_non_evaluative_subject_fails_evaluative_gate():
    report = _run(replace(_subject(), evaluative=False))
    assert report.verdict is Verdict.FAIL
    assert "security-evaluative" in {f.check_id for f in report.blocking_failures}


def test_non_certified_subject_fails_classifies_subject_gate():
    report = _run(replace(_subject(), classified_construct_id="NOT-A-CONSTRUCT"))
    assert report.verdict is Verdict.FAIL
    assert "security-classifies-subject" in {f.check_id for f in report.blocking_failures}


def test_absorbing_subject_fails_classifies_subject_gate():
    report = _run(replace(_subject(), absorbs_classified=True))
    assert report.verdict is Verdict.FAIL
    assert "security-classifies-subject" in {f.check_id for f in report.blocking_failures}


def test_non_dimensioned_subject_fails_dimensioned_gate():
    report = _run(replace(_subject(), dimensioned=False, classified_dimensions=()))
    assert report.verdict is Verdict.FAIL
    assert "security-dimensioned" in {f.check_id for f in report.blocking_failures}


def test_non_classification_recording_subject_fails_classification_gate():
    report = _run(replace(_subject(), records_classification=False))
    assert report.verdict is Verdict.FAIL
    assert "security-classification-recorded" in {f.check_id for f in report.blocking_failures}


def test_non_policy_binding_subject_fails_policy_gate():
    report = _run(replace(_subject(), binds_policy_by_reference=False))
    assert report.verdict is Verdict.FAIL
    assert "security-binds-policy-by-reference" in {f.check_id for f in report.blocking_failures}


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
    subject = replace(_subject(), provenance_chain=("DMC-10", "DATA-014", "DATA-001"))
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


@pytest.mark.parametrize(
    ("overrides", "expected_check"),
    [
        ({"type_tag": "  "}, "security-typed"),
        ({"name": "  "}, "security-named"),
        ({"target_id": "NOT-A-SECURITY"}, "security-identified"),
        ({"value_digest": "zz"}, "data-value-fidelity"),
        ({"classified": False, "kind": ""}, "security-classified"),
        ({"version": "  "}, "security-versioned"),
        ({"meta_class": "DMC-99"}, "meta-class-single"),
        ({"relationships": ("DMR-09", "DMR-99")}, "meta-relationships-closed"),
        ({"security_state": "BOGUS"}, "security-valid"),
        ({"redefines_el1": True}, "foundation-reuse-integrity"),
        ({"substrate_refs": ()}, "foundation-reuse-integrity"),
        ({"embeds_secret": True}, "non-constitutive"),
        ({"policy_ref": "not-a-policy-ref"}, "security-binds-policy-by-reference"),
    ],
)
def test_each_guard_fails_closed(overrides, expected_check):
    subject = replace(_subject(), **overrides)
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert expected_check in {f.check_id for f in report.blocking_failures}


def test_meta_constraints_fail_when_enforcing():
    report = _run(replace(_subject(), enforces=True))
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
    assert_every_check_can_refuse(_subject(), security_checks())
