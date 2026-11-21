"""EC2-TASK-000148 — Validation derived-status tests (EC2-EPIC-010).

Covers the pure derived-posture computation over a certified report: ACCEPTED,
ACCEPTED_WITH_ADVISORIES, and REJECTED, plus content-addressed determinism and
fail-closed input validation.
"""

from __future__ import annotations

from platform.tests.validation_console_helpers import (
    accepted_subject,
    advisory_subject,
    rejected_subject,
)
from platform.validation.errors import ValidationStatusError
from platform.validation.status import (
    DerivedValidationStatus,
    ValidationPosture,
    derive_status,
)

import pytest

from engine.validation.executor import ValidationEngine


def _report(subject):
    return ValidationEngine().validate(subject)


def test_posture_accepted():
    status = derive_status(_report(accepted_subject()))
    assert status.posture is ValidationPosture.ACCEPTED
    assert status.accepted is True
    assert status.blocking_failed == 0
    assert status.advisory_failed == 0
    assert status.status_id.startswith("UCOS-VDST-")


def test_posture_accepted_with_advisories():
    status = derive_status(_report(advisory_subject()))
    assert status.posture is ValidationPosture.ACCEPTED_WITH_ADVISORIES
    assert status.accepted is True
    assert status.advisory_failed == 1


def test_posture_rejected():
    status = derive_status(_report(rejected_subject()))
    assert status.posture is ValidationPosture.REJECTED
    assert status.accepted is False
    assert status.blocking_failed >= 1
    assert status.verdict == "fail"


def test_status_is_deterministic():
    a = derive_status(_report(accepted_subject()))
    b = derive_status(_report(accepted_subject()))
    assert a.status_id == b.status_id
    assert a.fingerprint() == b.fingerprint()
    assert a.to_dict()["posture"] == "accepted"


def test_derive_status_rejects_non_report():
    with pytest.raises(ValidationStatusError):
        derive_status("nope")  # type: ignore[arg-type]


def test_status_create_direct():
    status = DerivedValidationStatus.create(
        target_id="t",
        blueprint_id="bp",
        verdict="pass",
        accepted=True,
        posture=ValidationPosture.ACCEPTED,
        blocking_failed=0,
        advisory_failed=0,
    )
    assert status.status_id.startswith("UCOS-VDST-")
