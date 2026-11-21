"""EC2-TASK-000157 — Certification derived-status / readiness / governance tests (EC2-EPIC-011).

Covers the three pure derived evaluations over a certified decision: the derived posture
(CERTIFIED / CERTIFIED_WITH_ADVISORIES / NOT_CERTIFIED), the deterministic readiness
completeness evaluation, and the certification governance compliance assessment (every
rule, compliant and violating), plus content-addressed determinism and fail-closed input
validation.
"""

from __future__ import annotations

from dataclasses import replace
from platform.certification.errors import CertificationStatusError
from platform.certification.status import (
    GOVERNANCE_RULES,
    READINESS_INDICATORS,
    CertificationPosture,
    DerivedCertificationStatus,
    derive_status,
    evaluate_readiness,
    validate_governance,
)
from platform.tests.certification_console_helpers import (
    VERSION,
    advisory_output,
    certified_output,
    not_certified_output,
)

import pytest

from engine.certification.contracts import CertificationStatus, CertificationSubject
from engine.certification.engine import CertificationEngine


def _decision(validation_output, *, version=VERSION):
    report, evidence = validation_output
    subject = CertificationSubject.from_validation(report, evidence, version=version)
    return CertificationEngine().certify(subject)


# --------------------------------------------------------------------------- #
# Derived status                                                               #
# --------------------------------------------------------------------------- #


def test_posture_certified():
    status = derive_status(_decision(certified_output()))
    assert status.posture is CertificationPosture.CERTIFIED
    assert status.certified is True
    assert status.blocking_failed == 0
    assert status.advisory_failed == 0
    assert status.status_id.startswith("UCOS-CDST-")


def test_posture_certified_with_advisories():
    status = derive_status(_decision(advisory_output()))
    assert status.posture is CertificationPosture.CERTIFIED_WITH_ADVISORIES
    assert status.certified is True
    assert status.advisory_failed == 1


def test_posture_not_certified():
    status = derive_status(_decision(not_certified_output()))
    assert status.posture is CertificationPosture.NOT_CERTIFIED
    assert status.certified is False
    assert status.blocking_failed >= 1
    assert status.status == "not-certified"


def test_status_is_deterministic():
    a = derive_status(_decision(certified_output()))
    b = derive_status(_decision(certified_output()))
    assert a.status_id == b.status_id
    assert a.fingerprint() == b.fingerprint()
    assert a.to_dict()["posture"] == "certified"


def test_derive_status_rejects_non_decision():
    with pytest.raises(CertificationStatusError):
        derive_status("nope")  # type: ignore[arg-type]


def test_status_create_direct():
    status = DerivedCertificationStatus.create(
        certification_id="c",
        target_id="t",
        blueprint_id="bp",
        version="1.0.0",
        status="certified",
        certified=True,
        posture=CertificationPosture.CERTIFIED,
        blocking_failed=0,
        advisory_failed=0,
    )
    assert status.status_id.startswith("UCOS-CDST-")


# --------------------------------------------------------------------------- #
# Readiness                                                                    #
# --------------------------------------------------------------------------- #


def test_readiness_ready_when_certified():
    readiness = evaluate_readiness(_decision(certified_output()))
    assert readiness.ready is True
    assert set(readiness.satisfied) == set(READINESS_INDICATORS)
    assert readiness.blockers == ()
    assert readiness.readiness_id.startswith("UCOS-CRDY-")
    assert readiness.to_dict()["ready"] is True
    assert readiness.fingerprint() == readiness.fingerprint()


def test_readiness_blocked_when_not_certified():
    readiness = evaluate_readiness(_decision(not_certified_output()))
    assert readiness.ready is False
    assert "certified" in readiness.blockers
    assert "no-blocking-failures" in readiness.blockers


def test_readiness_rejects_non_decision():
    with pytest.raises(CertificationStatusError):
        evaluate_readiness("nope")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Governance                                                                   #
# --------------------------------------------------------------------------- #


def test_governance_compliant_for_certified():
    assessment = validate_governance(_decision(certified_output()))
    assert assessment.compliant is True
    assert assessment.violations == ()
    assert set(assessment.rules_evaluated) == set(GOVERNANCE_RULES)
    assert assessment.assessment_id.startswith("UCOS-CGOV-")
    assert assessment.to_dict()["compliant"] is True
    assert assessment.fingerprint() == assessment.fingerprint()


def test_governance_compliant_for_not_certified_but_consistent():
    # A NOT-CERTIFIED decision is still governance-compliant: its record is intact,
    # authority/standard/disclosure/version pinned, and status is consistent with the
    # blocking-failure set.
    assessment = validate_governance(_decision(not_certified_output()))
    assert assessment.compliant is True


def test_governance_reports_record_and_field_violations():
    decision = _decision(not_certified_output())
    bad_record = replace(
        decision.record,
        authority="WRONG-AUTHORITY",
        standard="",
        standard_version="",
        disclosure={},
        version="   ",
    )
    bad_decision = replace(decision, record=bad_record)
    assessment = validate_governance(bad_decision)
    assert assessment.compliant is False
    rules = {v.rule for v in assessment.violations}
    assert {
        "record-integrity",
        "authority-execution-only",
        "standard-pinned",
        "disclosure-present",
        "version-pinned",
    } <= rules
    assert assessment.violations[0].to_dict()["rule"] in rules


def test_governance_reports_status_inconsistency():
    decision = _decision(certified_output())
    assert decision.record.status is CertificationStatus.CERTIFIED
    # Force an inconsistency: CERTIFIED record but a non-empty blocking-failure set.
    inconsistent = replace(decision, blocking_failures=("phantom-criterion",))
    assessment = validate_governance(inconsistent)
    assert assessment.compliant is False
    assert any(v.rule == "status-consistent" for v in assessment.violations)


def test_governance_rejects_non_decision():
    with pytest.raises(CertificationStatusError):
        validate_governance("nope")  # type: ignore[arg-type]
