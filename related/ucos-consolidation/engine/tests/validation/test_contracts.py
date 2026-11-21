"""TASK-000049 — Validation contract tests (TASK-000046)."""

from __future__ import annotations

import pytest

from engine.runtime import assemble
from engine.validation.contracts import (
    VALIDATION_CONTRACT_VERSION,
    CheckStatus,
    Severity,
    ValidationFinding,
    ValidationRequest,
    ValidationSubject,
)
from engine.validation.errors import ValidationSubjectError


def test_request_immutable_and_serializable():
    request = ValidationRequest("UCOS-RUN-BP-DATA-0001-abc", strict=True)
    assert request.to_dict() == {"target_id": "UCOS-RUN-BP-DATA-0001-abc", "strict": True}
    assert VALIDATION_CONTRACT_VERSION == "1.0.0"
    with pytest.raises((AttributeError, TypeError)):
        request.strict = False  # type: ignore[misc]


def test_finding_properties_and_serialization():
    passed = ValidationFinding("c", Severity.BLOCKING, CheckStatus.PASS)
    failed = ValidationFinding("c", Severity.BLOCKING, CheckStatus.FAIL, "bad")
    advisory = ValidationFinding("a", Severity.ADVISORY, CheckStatus.FAIL, "meh")
    assert passed.passed is True
    assert passed.is_blocking_failure is False
    assert failed.is_blocking_failure is True
    assert advisory.is_blocking_failure is False
    assert failed.to_dict()["status"] == "fail"


def test_subject_from_runtime_unit(published_package, runtime_signer):
    unit = assemble(published_package, verify_with=runtime_signer)
    subject = ValidationSubject.from_runtime_unit(unit, blueprint_class="BP-DATA")
    assert subject.target_id == unit.runtime_id
    assert subject.blueprint_id == "BP-DATA-0001"
    assert subject.blueprint_class == "BP-DATA"
    assert subject.provenance_chain[0] == "BP-DATA-0001"
    assert f"@sha256:{subject.package_sha256}" in subject.image_reference
    d = subject.to_dict()
    assert d["disclosure"]["disclosure_id"] == "EC-1-PROVISIONAL-STATE"
    assert d["runtime_id"] == unit.runtime_id


def test_subject_requires_runtime_id(published_package, runtime_signer):
    import dataclasses

    unit = assemble(published_package, verify_with=runtime_signer)
    bare = dataclasses.replace(unit, runtime_id="")
    with pytest.raises(ValidationSubjectError):
        ValidationSubject.from_runtime_unit(bare)


def test_subject_without_disclosure_serializes(published_package, runtime_signer):
    import dataclasses

    unit = assemble(published_package, verify_with=runtime_signer)
    no_disc = dataclasses.replace(unit, disclosure=None)
    subject = ValidationSubject.from_runtime_unit(no_disc)
    assert subject.disclosure is None
    assert subject.to_dict()["disclosure"] is None
