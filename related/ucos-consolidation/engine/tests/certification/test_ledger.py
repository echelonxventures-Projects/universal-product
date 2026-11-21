"""TASK-000053 — Certification ledger tests."""

from __future__ import annotations

import pytest

from engine.certification.errors import (
    CertificationIntegrityError,
    LedgerIntegrityError,
)
from engine.certification.ledger import (
    GENESIS_HASH,
    CertificationLedger,
    CertificationLedgerEntry,
)


def test_empty_ledger_head_is_genesis():
    ledger = CertificationLedger()
    assert len(ledger) == 0
    assert ledger.head_hash == GENESIS_HASH
    assert ledger.verify() is True


def test_append_chains_entries(certified_decision):
    ledger = CertificationLedger()
    entry = ledger.append(certified_decision.record)
    assert entry.sequence == 0
    assert entry.prev_hash == GENESIS_HASH
    assert entry.certification_id == certified_decision.certification_id
    assert entry.status == "certified"
    assert ledger.head_hash == entry.entry_hash
    assert ledger.verify() is True
    assert set(entry.to_dict()) >= {"sequence", "entry_hash", "prev_hash"}


def test_second_append_links_to_previous(certified_decision):
    ledger = CertificationLedger()
    first = ledger.append(certified_decision.record)
    second = ledger.append(certified_decision.record)
    assert second.sequence == 1
    assert second.prev_hash == first.entry_hash
    assert second.entry_hash != first.entry_hash  # sequence differs
    assert ledger.verify() is True
    assert len(ledger) == 2


def test_ledger_is_deterministic(certified_decision):
    a = CertificationLedger()
    b = CertificationLedger()
    a.append(certified_decision.record)
    b.append(certified_decision.record)
    assert a.to_dict() == b.to_dict()
    assert a.head_hash == b.head_hash


def test_append_rejects_tampered_record(certified_decision):
    record = certified_decision.record
    object.__setattr__(record, "version", "9.9.9")
    ledger = CertificationLedger()
    with pytest.raises(CertificationIntegrityError):
        ledger.append(record)


def test_verify_detects_broken_chain(certified_decision):
    ledger = CertificationLedger()
    ledger.append(certified_decision.record)
    ledger.append(certified_decision.record)
    # tamper with a stored entry's record hash
    tampered = CertificationLedgerEntry(
        **{**ledger.entries[0].to_dict(), "record_sha256": "0" * 64}
    )
    ledger._entries[0] = tampered  # noqa: SLF001 — test reaches into internals
    assert ledger.verify() is False
    with pytest.raises(LedgerIntegrityError):
        ledger.require_intact()


def test_require_intact_passes_for_valid_chain(certified_decision):
    ledger = CertificationLedger()
    ledger.append(certified_decision.record)
    ledger.require_intact()  # does not raise


def test_verify_detects_broken_prev_link(certified_decision):
    ledger = CertificationLedger()
    ledger.append(certified_decision.record)
    ledger.append(certified_decision.record)
    # break the second entry's back-link to its predecessor
    tampered = CertificationLedgerEntry(**{**ledger.entries[1].to_dict(), "prev_hash": "f" * 64})
    ledger._entries[1] = tampered  # noqa: SLF001 — test reaches into internals
    assert ledger.verify() is False
