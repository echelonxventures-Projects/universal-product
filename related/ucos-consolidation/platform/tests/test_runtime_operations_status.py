"""EC2-TASK-000167 — Runtime Operations derived status & governance tests (EC2-EPIC-012).

Covers the deterministic derived posture (deploy-governed / rollback-reversible /
rollback-irreversible) and the fail-closed governance assessment, including every
violation branch (uncertified, descriptor/unit mismatch, missing authority, missing
disclosure, missing provenance, irreversible rollback).
"""

from __future__ import annotations

import dataclasses
from platform.runtime_operations.contracts import RuntimeOperationKind, RuntimeOperationRecord
from platform.runtime_operations.errors import RuntimeOperationStatusError
from platform.runtime_operations.facade import RuntimeFacade
from platform.runtime_operations.status import (
    GOVERNANCE_RULES,
    DerivedRuntimeOperationStatus,
    GovernanceViolation,
    RuntimeOperationPosture,
    derive_status,
    validate_governance,
)
from platform.tests.runtime_operations_helpers import certification_record, runtime_unit

import pytest

_FACADE = RuntimeFacade()


def _deploy_record(unit=None, cert=None):
    unit = unit or runtime_unit()
    return RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.DEPLOY,
        unit=unit,
        certification=cert or certification_record(),
        deployment=_FACADE.deployment_descriptor(unit),
        owner_subject="op@x",
        environment="runtime",
    )


def _rollback_record(unit=None):
    unit = unit or runtime_unit()
    return RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.ROLLBACK,
        unit=unit,
        certification=certification_record(),
        rollback=_FACADE.rollback_descriptor(unit),
        owner_subject="op@x",
        environment="runtime",
    )


def test_derive_status_deploy():
    status = derive_status(_deploy_record())
    assert isinstance(status, DerivedRuntimeOperationStatus)
    assert status.posture is RuntimeOperationPosture.DEPLOY_GOVERNED
    assert status.reversible is False
    assert status.status_id.startswith("UCOS-RODS-")
    assert status.to_dict()["posture"] == "deploy-governed"
    assert status.fingerprint() == derive_status(_deploy_record()).fingerprint()


def test_derive_status_rollback_reversible():
    status = derive_status(_rollback_record())
    assert status.posture is RuntimeOperationPosture.ROLLBACK_REVERSIBLE
    assert status.reversible is True


def test_derive_status_rollback_irreversible():
    unit = runtime_unit()
    rb = dataclasses.replace(_FACADE.rollback_descriptor(unit), reversible=False)
    rec = RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.ROLLBACK,
        unit=unit,
        certification=certification_record(),
        rollback=rb,
        owner_subject="op@x",
        environment="runtime",
    )
    status = derive_status(rec)
    assert status.posture is RuntimeOperationPosture.ROLLBACK_IRREVERSIBLE


def test_derive_status_rejects_non_record():
    with pytest.raises(RuntimeOperationStatusError):
        derive_status("nope")  # type: ignore[arg-type]


def test_governance_compliant():
    assessment = validate_governance(_deploy_record())
    assert assessment.compliant is True
    assert assessment.violations == ()
    assert assessment.rules_evaluated == GOVERNANCE_RULES
    assert assessment.assessment_id.startswith("UCOS-ROGV-")
    assert assessment.to_dict()["compliant"] is True
    assert assessment.fingerprint() == validate_governance(_deploy_record()).fingerprint()


def test_governance_rollback_compliant():
    assert validate_governance(_rollback_record()).compliant is True


def test_governance_violation_uncertified():
    # A deploy record whose certification is not certified violates the 'certified' rule.
    from platform.tests.runtime_operations_helpers import not_certified_unit_and_record

    unit, cert = not_certified_unit_and_record()
    rec = _deploy_record(unit=unit, cert=cert)
    assessment = validate_governance(rec)
    assert assessment.compliant is False
    assert any(v.rule == "certified" for v in assessment.violations)


def test_governance_violation_authority_and_disclosure():
    unit = runtime_unit()
    rec = _deploy_record(unit=unit)
    broken = dataclasses.replace(rec.deployment, disclosure={"authority": "OTHER"})
    tampered = dataclasses.replace(rec, deployment=broken)
    assessment = validate_governance(tampered)
    rules = {v.rule for v in assessment.violations}
    assert "authority-execution-only" in rules
    assert "disclosure-present" in rules


def test_governance_violation_descriptor_mismatch_and_provenance():
    unit = runtime_unit()
    rec = _deploy_record(unit=unit)
    mismatched = dataclasses.replace(rec.deployment, runtime_id="UCOS-RUN-x-0000000000000000")
    tampered = dataclasses.replace(rec, deployment=mismatched)
    assert any(
        v.rule == "descriptor-matches-unit" for v in validate_governance(tampered).violations
    )
    no_prov_unit = runtime_unit(with_provenance=False)
    rec2 = _deploy_record(unit=no_prov_unit)
    assert any(v.rule == "provenance-present" for v in validate_governance(rec2).violations)


def test_governance_violation_irreversible_rollback():
    unit = runtime_unit()
    rb = dataclasses.replace(_FACADE.rollback_descriptor(unit), reversible=False)
    rec = RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.ROLLBACK,
        unit=unit,
        certification=certification_record(),
        rollback=rb,
        owner_subject="op@x",
        environment="runtime",
    )
    assert any(v.rule == "reversible-when-rollback" for v in validate_governance(rec).violations)


def test_governance_rejects_non_record():
    with pytest.raises(RuntimeOperationStatusError):
        validate_governance("nope")  # type: ignore[arg-type]


def test_governance_violation_to_dict():
    assert GovernanceViolation("r", "m").to_dict() == {"rule": "r", "message": "m"}
