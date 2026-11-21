"""EC2-TASK-000150 — Validation console health tests (EC2-EPIC-010).

Covers the deterministic health probe over the record registry + EC-1 façade: the
registry/fidelity/evidence-integrity checks, the machine-checkable fidelity invariant
(P6), and the induced-fault paths (infidelic record, inconsistent evidence).
"""

from __future__ import annotations

from platform.observability.contracts import HealthStatus
from platform.tests.validation_console_helpers import (
    accepted_subject,
    advisory_subject,
)
from platform.validation.contracts import ValidationRecord
from platform.validation.facade import ValidationFacade
from platform.validation.health import (
    EVIDENCE_CHECK,
    FIDELITY_CHECK,
    REGISTRY_CHECK,
    ValidationHealth,
    validation_console_health_checks,
)
from platform.validation.registry import ValidationRecordRegistry

import pytest

from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance


def _surfaced(subject):
    report = ValidationEngine().validate(subject)
    return report, build_validation_evidence(report), enforce_acceptance(report)


def _record(*, report, subject, evidence=None, decision=None):
    ev = evidence if evidence is not None else build_validation_evidence(report)
    dec = decision if decision is not None else enforce_acceptance(report)
    return ValidationRecord.create(
        report=report,
        evidence=ev,
        decision=dec,
        subject=subject,
        owner_subject="arch@x",
    )


def test_health_checks_are_all_critical():
    checks = validation_console_health_checks()
    assert {c.name for c in checks} == {REGISTRY_CHECK, FIDELITY_CHECK, EVIDENCE_CHECK}
    assert all(c.critical for c in checks)


def test_healthy_when_records_are_faithful():
    reg = ValidationRecordRegistry()
    report, ev, dec = _surfaced(accepted_subject())
    reg.record(_record(report=report, subject=accepted_subject(), evidence=ev, decision=dec))
    health = ValidationHealth(reg, ValidationFacade())
    probe = health.probe()
    assert probe[REGISTRY_CHECK] is HealthStatus.HEALTHY
    assert probe[FIDELITY_CHECK] is HealthStatus.HEALTHY
    assert probe[EVIDENCE_CHECK] is HealthStatus.HEALTHY
    assert health.healthy is True
    assert health.infidelic_records() == ()
    assert health.inconsistent_evidence() == ()


def test_infidelic_record_drives_fidelity_unhealthy():
    reg = ValidationRecordRegistry()
    accepted_report, _, _ = _surfaced(accepted_subject())
    # Store the accepted report but a *different* subject with the same target id;
    # a fresh certified reproduction over the stored subject diverges → infidelic.
    reg.record(_record(report=accepted_report, subject=advisory_subject()))
    health = ValidationHealth(reg, ValidationFacade())
    assert health.infidelic_records()
    assert health.probe()[FIDELITY_CHECK] is HealthStatus.UNHEALTHY
    assert health.healthy is False


def test_inconsistent_evidence_drives_evidence_unhealthy():
    reg = ValidationRecordRegistry()
    accepted_report, _, _ = _surfaced(accepted_subject())
    advisory_report, advisory_ev, _ = _surfaced(advisory_subject())
    # Fidelity holds (report matches subject) but the stored evidence is from a different
    # report → evidence-integrity check fails while fidelity passes.
    reg.record(_record(report=accepted_report, subject=accepted_subject(), evidence=advisory_ev))
    health = ValidationHealth(reg, ValidationFacade())
    assert health.infidelic_records() == ()
    assert health.inconsistent_evidence()
    assert health.probe()[EVIDENCE_CHECK] is HealthStatus.UNHEALTHY


def test_health_rejects_bad_construction():
    with pytest.raises(TypeError):
        ValidationHealth("nope", ValidationFacade())  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ValidationHealth(ValidationRecordRegistry(), "nope")  # type: ignore[arg-type]
