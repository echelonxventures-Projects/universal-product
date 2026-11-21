"""EC2-TASK-000159 — Certification console health tests (EC2-EPIC-011).

Covers the deterministic health probe over the record registry, the append-only ledger,
and the EC-1 façade: the registry/ledger-integrity/fidelity/evidence-integrity checks,
the machine-checkable fidelity invariant (P6), and the induced-fault paths (broken
ledger chain, infidelic record, inconsistent evidence).
"""

from __future__ import annotations

from dataclasses import replace
from platform.certification.contracts import CertificationConsoleRecord
from platform.certification.facade import CertificationFacade
from platform.certification.health import (
    EVIDENCE_CHECK,
    FIDELITY_CHECK,
    LEDGER_CHECK,
    REGISTRY_CHECK,
    CertificationHealth,
    certification_console_health_checks,
)
from platform.certification.ledger import CertificationConsoleLedger
from platform.certification.registry import CertificationRegistry
from platform.observability.contracts import HealthStatus
from platform.tests.certification_console_helpers import (
    VERSION,
    advisory_output,
    certified_output,
)

import pytest

from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.certification.evidence import build_certification_evidence
from engine.certification.ledger import CertificationLedger


def _decision(validation_output, *, version=VERSION):
    report, evidence = validation_output
    subject = CertificationSubject.from_validation(report, evidence, version=version)
    return CertificationEngine().certify(subject)


def _console_record(*, report, validation_evidence, decision, certification_evidence=None):
    cert_ev = (
        certification_evidence
        if certification_evidence is not None
        else build_certification_evidence(decision)
    )
    return CertificationConsoleRecord.create(
        report=report,
        validation_evidence=validation_evidence,
        decision=decision,
        certification_evidence=cert_ev,
        owner_subject="arch@x",
    )


def test_health_checks_are_all_critical():
    checks = certification_console_health_checks()
    assert {c.name for c in checks} == {
        REGISTRY_CHECK,
        LEDGER_CHECK,
        FIDELITY_CHECK,
        EVIDENCE_CHECK,
    }
    assert all(c.critical for c in checks)


def test_healthy_when_records_are_faithful():
    reg = CertificationRegistry()
    ledger = CertificationConsoleLedger()
    report, ev = certified_output()
    decision = _decision((report, ev))
    record = _console_record(report=report, validation_evidence=ev, decision=decision)
    reg.record(record)
    ledger.append(record.record)
    health = CertificationHealth(reg, ledger, CertificationFacade())
    probe = health.probe()
    assert probe[REGISTRY_CHECK] is HealthStatus.HEALTHY
    assert probe[LEDGER_CHECK] is HealthStatus.HEALTHY
    assert probe[FIDELITY_CHECK] is HealthStatus.HEALTHY
    assert probe[EVIDENCE_CHECK] is HealthStatus.HEALTHY
    assert health.healthy is True
    assert health.infidelic_records() == ()
    assert health.inconsistent_evidence() == ()


def test_broken_ledger_drives_ledger_unhealthy():
    engine_ledger = CertificationLedger()
    decision = _decision(certified_output())
    engine_ledger.append(decision.record)
    # Tamper the stored entry so the hash chain no longer verifies.
    engine_ledger._entries[0] = replace(engine_ledger._entries[0], record_sha256="tampered")
    ledger = CertificationConsoleLedger(engine_ledger)
    reg = CertificationRegistry()
    health = CertificationHealth(reg, ledger, CertificationFacade())
    assert ledger.verify() is False
    assert health.probe()[LEDGER_CHECK] is HealthStatus.UNHEALTHY
    assert health.healthy is False


def test_infidelic_record_drives_fidelity_unhealthy():
    reg = CertificationRegistry()
    ledger = CertificationConsoleLedger()
    cert_report, cert_ev = certified_output()
    adv_report, adv_ev = advisory_output()
    decision = _decision((cert_report, cert_ev))  # CERTIFIED over the accepted output
    # Store the certified decision but pair it with the advisory validation output
    # (same target). A fresh reproduction over the stored output diverges → infidelic.
    record = _console_record(report=adv_report, validation_evidence=adv_ev, decision=decision)
    reg.record(record)
    health = CertificationHealth(reg, ledger, CertificationFacade())
    assert health.infidelic_records()
    assert health.probe()[FIDELITY_CHECK] is HealthStatus.UNHEALTHY
    assert health.healthy is False


def test_inconsistent_evidence_drives_evidence_unhealthy():
    reg = CertificationRegistry()
    ledger = CertificationConsoleLedger()
    report, ev = certified_output()
    decision = _decision((report, ev))
    wrong_evidence = build_certification_evidence(_decision(advisory_output()))
    record = _console_record(
        report=report,
        validation_evidence=ev,
        decision=decision,
        certification_evidence=wrong_evidence,
    )
    reg.record(record)
    health = CertificationHealth(reg, ledger, CertificationFacade())
    assert health.infidelic_records() == ()
    assert health.inconsistent_evidence()
    assert health.probe()[EVIDENCE_CHECK] is HealthStatus.UNHEALTHY


def test_health_rejects_bad_construction():
    reg = CertificationRegistry()
    ledger = CertificationConsoleLedger()
    facade = CertificationFacade()
    with pytest.raises(TypeError):
        CertificationHealth("nope", ledger, facade)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        CertificationHealth(reg, "nope", facade)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        CertificationHealth(reg, ledger, "nope")  # type: ignore[arg-type]
