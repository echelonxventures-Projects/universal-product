"""EC2-TASK-000157 — Certification console context tests (EC2-EPIC-011).

Covers the immutable, content-addressed runtime context binding produced on a resolved
selection: derivation from a record + principal, ownership standing, posture, and
fail-closed input validation.
"""

from __future__ import annotations

from platform.certification.context import CertificationContext
from platform.certification.contracts import CertificationConsoleRecord
from platform.certification.errors import CertificationServiceError
from platform.certification.status import CertificationPosture
from platform.foundation.identity import Principal, Role
from platform.tests.certification_console_helpers import (
    VERSION,
    advisory_output,
    certified_output,
)

import pytest

from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.certification.evidence import build_certification_evidence


def _record(validation_output, **kw):
    report, evidence = validation_output
    subject = CertificationSubject.from_validation(report, evidence, version=VERSION)
    decision = CertificationEngine().certify(subject)
    return CertificationConsoleRecord.create(
        report=report,
        validation_evidence=evidence,
        decision=decision,
        certification_evidence=build_certification_evidence(decision),
        owner_subject=kw.pop("owner_subject", "arch@x"),
        **kw,
    )


def test_context_binds_who_what_where():
    record = _record(certified_output(), tenant="acme", request_ref="UCOS-GREQ-1")
    principal = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
    ctx = CertificationContext.create(record, principal, is_owner=True)
    assert ctx.context_id.startswith("UCOS-CCTX-")
    assert ctx.record_id == record.record_id
    assert ctx.certification_id == record.certification_id
    assert ctx.target_id == record.target_id
    assert ctx.certified is True
    assert ctx.posture is CertificationPosture.CERTIFIED
    assert ctx.request_ref == "UCOS-GREQ-1"
    assert ctx.subject == "arch@x"
    assert ctx.is_owner is True
    assert ctx.to_dict()["posture"] == "certified"
    assert ctx.fingerprint()


def test_context_reflects_advisory_posture():
    record = _record(advisory_output())
    principal = Principal.create("arch@x", [Role.ARCHITECT])
    ctx = CertificationContext.create(record, principal)
    assert ctx.posture is CertificationPosture.CERTIFIED_WITH_ADVISORIES
    assert ctx.is_owner is False


def test_context_is_deterministic():
    record = _record(certified_output(), tenant="acme")
    principal = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
    a = CertificationContext.create(record, principal, is_owner=True)
    b = CertificationContext.create(record, principal, is_owner=True)
    assert a.context_id == b.context_id


def test_context_fail_closed_inputs():
    record = _record(certified_output())
    principal = Principal.create("arch@x", [Role.ARCHITECT])
    with pytest.raises(CertificationServiceError):
        CertificationContext.create("nope", principal)  # type: ignore[arg-type]
    with pytest.raises(CertificationServiceError):
        CertificationContext.create(record, "nope")  # type: ignore[arg-type]
    with pytest.raises(CertificationServiceError):
        CertificationContext.create(record, principal, is_owner="yes")  # type: ignore[arg-type]
