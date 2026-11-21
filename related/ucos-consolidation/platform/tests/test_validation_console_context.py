"""EC2-TASK-000148 — Validation console context tests (EC2-EPIC-010).

Covers the immutable, content-addressed runtime context binding produced on a resolved
selection: derivation from a record + principal, ownership standing, posture, and
fail-closed input validation.
"""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.tests.validation_console_helpers import accepted_subject, advisory_subject
from platform.validation.context import ValidationContext
from platform.validation.contracts import ValidationRecord
from platform.validation.errors import ValidationServiceError
from platform.validation.status import ValidationPosture

import pytest

from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance


def _record(subject, **kw):
    report = ValidationEngine().validate(subject)
    return ValidationRecord.create(
        report=report,
        evidence=build_validation_evidence(report),
        decision=enforce_acceptance(report),
        subject=subject,
        owner_subject=kw.pop("owner_subject", "arch@x"),
        **kw,
    )


def test_context_binds_who_what_where():
    record = _record(accepted_subject(), tenant="acme", request_ref="UCOS-GREQ-1")
    principal = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
    ctx = ValidationContext.create(record, principal, is_owner=True)
    assert ctx.context_id.startswith("UCOS-VCTX-")
    assert ctx.record_id == record.record_id
    assert ctx.target_id == record.target_id
    assert ctx.accepted is True
    assert ctx.posture is ValidationPosture.ACCEPTED
    assert ctx.request_ref == "UCOS-GREQ-1"
    assert ctx.subject == "arch@x"
    assert ctx.is_owner is True
    assert ctx.to_dict()["posture"] == "accepted"
    assert ctx.fingerprint()


def test_context_reflects_advisory_posture():
    record = _record(advisory_subject())
    principal = Principal.create("arch@x", [Role.ARCHITECT])
    ctx = ValidationContext.create(record, principal)
    assert ctx.posture is ValidationPosture.ACCEPTED_WITH_ADVISORIES
    assert ctx.is_owner is False


def test_context_is_deterministic():
    record = _record(accepted_subject(), tenant="acme")
    principal = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
    a = ValidationContext.create(record, principal, is_owner=True)
    b = ValidationContext.create(record, principal, is_owner=True)
    assert a.context_id == b.context_id


def test_context_fail_closed_inputs():
    record = _record(accepted_subject())
    principal = Principal.create("arch@x", [Role.ARCHITECT])
    with pytest.raises(ValidationServiceError):
        ValidationContext.create("nope", principal)  # type: ignore[arg-type]
    with pytest.raises(ValidationServiceError):
        ValidationContext.create(record, "nope")  # type: ignore[arg-type]
    with pytest.raises(ValidationServiceError):
        ValidationContext.create(record, principal, is_owner="yes")  # type: ignore[arg-type]
