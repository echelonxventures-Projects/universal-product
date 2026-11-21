"""UCOS-EPIC-006 — Certification audit ledger tests."""

from __future__ import annotations

import pytest

from engine.universal_certification import (
    AuditEventType,
    CertificationAuditLedger,
)
from engine.universal_certification.audit import GENESIS_HASH
from engine.universal_certification.errors import AuditIntegrityError

from .conftest import mutate


def _record(ledger, event, cid="UCOS-UCERT-X", sha="s", **detail):
    return ledger.record(event, certification_id=cid, certificate_sha256=sha, **detail)


def test_empty_ledger_head_is_genesis():
    ledger = CertificationAuditLedger()
    assert ledger.head_hash == GENESIS_HASH
    assert len(ledger) == 0


def test_append_and_chain():
    ledger = CertificationAuditLedger()
    e0 = _record(ledger, AuditEventType.CERTIFIED)
    e1 = _record(ledger, AuditEventType.CERTIFICATE_ISSUED)
    assert e0.prev_hash == GENESIS_HASH
    assert e1.prev_hash == e0.entry_hash
    assert ledger.head_hash == e1.entry_hash
    assert len(ledger) == 2
    assert ledger.entries == (e0, e1)
    assert ledger.verify() is True
    ledger.require_intact()


def test_record_rejects_bad_event_type():
    ledger = CertificationAuditLedger()
    with pytest.raises(AuditIntegrityError):
        ledger.record("certified", certification_id="c", certificate_sha256="s")  # type: ignore[arg-type]


def test_events_for_filters_by_certification():
    ledger = CertificationAuditLedger()
    _record(ledger, AuditEventType.CERTIFIED, cid="A")
    _record(ledger, AuditEventType.CERTIFIED, cid="B")
    _record(ledger, AuditEventType.APPROVED, cid="A")
    assert len(ledger.events_for("A")) == 2
    assert len(ledger.events_for("B")) == 1


def test_tamper_breaks_chain():
    ledger = CertificationAuditLedger()
    _record(ledger, AuditEventType.CERTIFIED)
    _record(ledger, AuditEventType.APPROVED)
    ledger._entries[0] = mutate(ledger._entries[0], event_type=AuditEventType.REJECTED)  # noqa: SLF001
    assert ledger.verify() is False
    with pytest.raises(AuditIntegrityError):
        ledger.require_intact()


def test_broken_prev_link_breaks_chain():
    ledger = CertificationAuditLedger()
    _record(ledger, AuditEventType.CERTIFIED)
    _record(ledger, AuditEventType.APPROVED)
    ledger._entries[1] = mutate(ledger._entries[1], prev_hash="f" * 64)  # noqa: SLF001
    assert ledger.verify() is False


def test_to_dict_snapshot():
    ledger = CertificationAuditLedger()
    _record(ledger, AuditEventType.CERTIFIED, detail_key="v")
    payload = ledger.to_dict()
    assert payload["count"] == 1
    assert payload["entries"][0]["event_type"] == "certified"
    assert payload["entries"][0]["detail"]["detail_key"] == "v"
