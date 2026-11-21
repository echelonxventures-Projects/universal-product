"""EC2-TASK-000156 — Certification console ledger & lineage tests (EC2-EPIC-011).

Covers the read-only, append-only, hash-chained console ledger: idempotent append by
certification id, tamper-evident chain verification, entry views, target/blueprint
navigation, and the deterministic parent/child/ancestry lineage (including the
re-certification history of a target). All navigation is a pure function of the chain.
"""

from __future__ import annotations

from platform.certification.errors import CertificationLedgerError, CertificationLineageError
from platform.certification.ledger import (
    CertificationConsoleLedger,
    CertificationLedgerView,
    CertificationLineageView,
)
from platform.tests.certification_console_helpers import (
    certified_output,
    not_certified_output,
)

import pytest

from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.certification.ledger import CertificationLedger


def _cert_record(validation_output, *, version="1.0.0"):
    report, evidence = validation_output
    subject = CertificationSubject.from_validation(report, evidence, version=version)
    return CertificationEngine().certify(subject).record


def test_append_is_idempotent_and_chain_verifies():
    ledger = CertificationConsoleLedger()
    record = _cert_record(certified_output())
    entry = ledger.append(record)
    assert entry.sequence == 0
    # re-append the same certification → returns the stored entry (idempotent)
    again = ledger.append(record)
    assert again.entry_hash == entry.entry_hash
    assert len(ledger) == 1
    assert record.certification_id in ledger
    assert ledger.head_hash == entry.entry_hash
    assert ledger.verify() is True
    ledger.require_intact()


def test_append_rejects_bad_type_and_construction():
    ledger = CertificationConsoleLedger()
    with pytest.raises(CertificationLedgerError):
        ledger.append("nope")  # type: ignore[arg-type]
    with pytest.raises(CertificationLedgerError):
        CertificationConsoleLedger(ledger="nope")  # type: ignore[arg-type]


def test_construct_from_seeded_engine_ledger():
    engine_ledger = CertificationLedger()
    record = _cert_record(certified_output())
    engine_ledger.append(record)
    ledger = CertificationConsoleLedger(engine_ledger)
    assert record.certification_id in ledger
    assert len(ledger) == 1


def test_get_and_view_and_views():
    ledger = CertificationConsoleLedger()
    record = _cert_record(certified_output())
    ledger.append(record)
    entry = ledger.get(record.certification_id)
    assert entry.certification_id == record.certification_id
    assert ledger.entries == (entry,)
    view = ledger.view(record.certification_id)
    assert isinstance(view, CertificationLedgerView)
    assert view.to_dict()["certification_id"] == record.certification_id
    assert ledger.views() == (view,)


def test_get_unknown_fail_closed():
    ledger = CertificationConsoleLedger()
    with pytest.raises(CertificationLedgerError):
        ledger.get("UCOS-CERT-missing")


def test_view_from_entry_rejects_bad_type():
    with pytest.raises(CertificationLedgerError):
        CertificationLedgerView.from_entry("nope")  # type: ignore[arg-type]


def test_by_target_and_by_blueprint():
    ledger = CertificationConsoleLedger()
    v1 = _cert_record(certified_output(), version="1.0.0")
    v2 = _cert_record(certified_output(), version="2.0.0")
    other = _cert_record(not_certified_output())
    ledger.append(v1)
    ledger.append(v2)
    ledger.append(other)
    by_target = ledger.by_target(v1.target_id)
    assert {v.certification_id for v in by_target} == {v1.certification_id, v2.certification_id}
    by_blueprint = ledger.by_blueprint(v1.blueprint_id)
    assert {v.certification_id for v in by_blueprint} == {v1.certification_id, v2.certification_id}


def test_ancestry_and_lineage():
    ledger = CertificationConsoleLedger()
    v1 = _cert_record(certified_output(), version="1.0.0")
    v2 = _cert_record(certified_output(), version="2.0.0")
    ledger.append(v1)
    ledger.append(v2)

    root = ledger.lineage(v1.certification_id)
    assert isinstance(root, CertificationLineageView)
    assert root.is_root is True
    assert root.parent is None
    assert root.child == v2.certification_id
    assert root.depth == 0

    child = ledger.lineage(v2.certification_id)
    assert child.parent == v1.certification_id
    assert child.child is None
    assert child.ancestors == (v1.certification_id,)
    assert child.target_ancestors == (v1.certification_id,)
    assert child.depth == 1
    assert child.lineage_id.startswith("UCOS-CLIN-")
    assert child.to_dict()["parent"] == v1.certification_id
    assert child.fingerprint() == child.fingerprint()

    assert tuple(e.certification_id for e in ledger.ancestry(v2.certification_id)) == (
        v1.certification_id,
    )


def test_lineage_unknown_fail_closed():
    ledger = CertificationConsoleLedger()
    with pytest.raises(CertificationLineageError):
        ledger.lineage("UCOS-CERT-missing")
    with pytest.raises(CertificationLineageError):
        ledger.ancestry("UCOS-CERT-missing")


def test_to_dict_and_fingerprint():
    ledger = CertificationConsoleLedger()
    ledger.append(_cert_record(certified_output()))
    d = ledger.to_dict()
    assert d["count"] == 1
    assert d["intact"] is True
    assert d["ledger_format"] == "ucos-certification-console-ledger/1.0.0"
    assert ledger.fingerprint() == ledger.fingerprint()
