"""EC3-B10-U07 — Governance validation tests (EC-1 PASS + V1…V5 + UDL-13 + VC)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.governance import make_conformance, make_governance, policy_ref_for
from data.governance_meta import GovernanceKind
from data.governance_traceability import build_governance_traceability
from data.governance_validation import (
    GovernanceValidationSubject,
    governance_checks,
    validate_governance,
)
from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine

ENTITY_NAME = "ucos.demo.entity"
GOVERNANCE_NAME = "ucos.demo.governance"
POLICY_REF = policy_ref_for("conformance.udl")


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _governance(**overrides):
    entity = overrides.pop("entity", None) or _entity()
    kwargs = dict(
        kind=overrides.pop("kind", GovernanceKind.CONFORMANCE_RECORD),
        conformance=overrides.pop("conformance", make_conformance((("UDL-02", True),))),
    )
    kwargs.update(overrides)
    policy_ref = kwargs.pop("policy_ref", POLICY_REF)
    name = kwargs.pop("name", GOVERNANCE_NAME)
    type_tag = kwargs.pop("type_tag", "ucos.core.governance")
    return make_governance(name, type_tag, entity, policy_ref, **kwargs)


def _trace(governance):
    return build_governance_traceability(
        governance, unit="EC3-B10-U07", forward=(governance.governance_id,)
    )


def test_validation_passes_and_is_accepted():
    g = _governance()
    result = validate_governance(g, _trace(g))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    g = _governance()
    result = validate_governance(g, _trace(g))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(governance_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_v1_v5_all_hold():
    g = _governance()
    result = validate_governance(g, _trace(g))
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["meta-class-single"]  # V1 (DMC-08)
    assert passed["meta-relationships-closed"]  # V2
    assert passed["meta-constraints"]  # V3 (DGA-K1/K2/K3/K4/K5)
    assert passed["founding-acyclic"]  # V4
    assert passed["governance-valid"]  # V5


def test_governance_udl13_checks_present_and_pass():
    g = _governance()
    result = validate_governance(g, _trace(g))
    passed = {f.check_id: f.passed for f in result.report.findings}
    for cid in (
        "governance-typed",  # UDL-03 / DGA-K1
        "governance-named",
        "governance-identified",  # UDL-04/05
        "governance-governs-subject",  # DMR-07
        "governance-declarative",  # DGA-01 / DGA-K2
        "governance-non-enforcing",  # DGA-02 / UDL-13
        "governance-no-access",  # DGA-03 / DGA-K5
        "governance-recorded",  # DGA-06 / DGA-K4
        "governance-binds-policy-by-reference",  # DMR-11 / DGA-07
        "governance-conformance-recorded",  # DGA-C1
        "governance-stewardship-descriptor",  # DGA-05 / DGA-C4
        "governance-independence",  # UDL-13 / DGA-K5
        "governance-versioned",  # DGA-08 / UDL-12
        "governance-classified",  # DXH-08
        "data-value-fidelity",  # UDL-06 (transitive)
        "foundation-reuse-integrity",  # UDL-02 / VC-5
        "non-constitutive",  # UDL-15 / DGA-09
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_shared_check_ids_present_for_cce_gate_reuse():
    # These ids are consumed by the reused DMC-01 CCE ten-gate suite.
    g = _governance()
    result = validate_governance(g, _trace(g))
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
    g = _governance()
    s1 = GovernanceValidationSubject.from_governance(g, _trace(g))
    s2 = GovernanceValidationSubject.from_governance(g, _trace(g))
    assert s1 == s2  # determinism at the subject boundary


def test_strict_acceptance_returns_decision_for_valid_governance():
    g = _governance()
    result = validate_governance(g, _trace(g), strict=True)
    assert result.accepted is True
    assert result.decision.accepted is True


def test_untraced_governance_fails_traceability_gate():
    g = _governance()
    subject = GovernanceValidationSubject.from_governance(g, _trace(g))
    subject = replace(subject, provenance_chain=())  # orphaned lineage
    report = ValidationEngine(governance_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


def test_secret_bearing_governance_fails_non_constitutive_gate():
    g = _governance(name="api_key")
    result = validate_governance(g, _trace(g))
    assert result.accepted is False
    assert "non-constitutive" in {f.check_id for f in result.report.blocking_failures}


def _subject():
    g = _governance()
    return GovernanceValidationSubject.from_governance(g, _trace(g))


def _run(subject):
    return ValidationEngine(governance_checks()).validate(subject)


def test_enforcing_subject_fails_non_enforcing_gate():
    report = _run(replace(_subject(), enforces=True))
    assert report.verdict is Verdict.FAIL
    assert "governance-non-enforcing" in {f.check_id for f in report.blocking_failures}


def test_access_granting_subject_fails_no_access_gate():
    report = _run(replace(_subject(), grants_access=True))
    assert report.verdict is Verdict.FAIL
    assert "governance-no-access" in {f.check_id for f in report.blocking_failures}


def test_authority_conferring_subject_fails_no_access_gate():
    report = _run(replace(_subject(), confers_authority=True))
    assert report.verdict is Verdict.FAIL
    failed = {f.check_id for f in report.blocking_failures}
    assert "governance-no-access" in failed
    assert "non-constitutive" in failed


def test_technology_naming_subject_fails_independence_gate():
    report = _run(replace(_subject(), names_technology=True))
    assert report.verdict is Verdict.FAIL
    assert "governance-independence" in {f.check_id for f in report.blocking_failures}


def test_selects_technology_subject_fails_independence_gate():
    report = _run(replace(_subject(), selects_technology=True))
    assert report.verdict is Verdict.FAIL
    assert "governance-independence" in {f.check_id for f in report.blocking_failures}


def test_non_recorded_subject_fails_recorded_gate():
    report = _run(replace(_subject(), recorded=False))
    assert report.verdict is Verdict.FAIL
    assert "governance-recorded" in {f.check_id for f in report.blocking_failures}


def test_non_declarative_subject_fails_declarative_gate():
    report = _run(replace(_subject(), declarative=False))
    assert report.verdict is Verdict.FAIL
    assert "governance-declarative" in {f.check_id for f in report.blocking_failures}


def test_non_certified_subject_fails_governs_subject_gate():
    report = _run(replace(_subject(), governed_construct_id="NOT-A-CONSTRUCT"))
    assert report.verdict is Verdict.FAIL
    assert "governance-governs-subject" in {f.check_id for f in report.blocking_failures}


def test_absorbing_subject_fails_governs_subject_gate():
    report = _run(replace(_subject(), absorbs_governed=True))
    assert report.verdict is Verdict.FAIL
    assert "governance-governs-subject" in {f.check_id for f in report.blocking_failures}


def test_non_conformance_recording_subject_fails_conformance_gate():
    report = _run(replace(_subject(), records_conformance=False))
    assert report.verdict is Verdict.FAIL
    assert "governance-conformance-recorded" in {f.check_id for f in report.blocking_failures}


def test_stewardship_power_subject_fails_stewardship_gate():
    report = _run(replace(_subject(), stewardship_is_descriptor=False))
    assert report.verdict is Verdict.FAIL
    assert "governance-stewardship-descriptor" in {f.check_id for f in report.blocking_failures}


def test_non_policy_binding_subject_fails_policy_gate():
    report = _run(replace(_subject(), binds_policy_by_reference=False))
    assert report.verdict is Verdict.FAIL
    assert "governance-binds-policy-by-reference" in {f.check_id for f in report.blocking_failures}


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
    subject = replace(_subject(), provenance_chain=("DMC-08", "DATA-012", "DATA-001"))
    report = _run(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


@pytest.mark.parametrize(
    ("overrides", "expected_check"),
    [
        ({"type_tag": "  "}, "governance-typed"),
        ({"name": "  "}, "governance-named"),
        ({"target_id": "NOT-A-GOVERNANCE"}, "governance-identified"),
        ({"value_digest": "zz"}, "data-value-fidelity"),
        ({"classified": False, "kind": ""}, "governance-classified"),
        ({"version": "  "}, "governance-versioned"),
        ({"meta_class": "DMC-99"}, "meta-class-single"),
        ({"relationships": ("DMR-07", "DMR-99")}, "meta-relationships-closed"),
        ({"governance_state": "BOGUS"}, "governance-valid"),
        ({"redefines_el1": True}, "foundation-reuse-integrity"),
        ({"substrate_refs": ()}, "foundation-reuse-integrity"),
        ({"embeds_secret": True}, "non-constitutive"),
        ({"policy_ref": "not-a-policy-ref"}, "governance-binds-policy-by-reference"),
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
    assert_every_check_can_refuse(_subject(), governance_checks())
