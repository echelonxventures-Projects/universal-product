"""EC2-TASK-000169 — Runtime Operations ledger & lineage tests (EC2-EPIC-012).

Covers the append-only, hash-chained operation ledger: idempotent append, tamper-evident
verification, entry/lineage views, runtime-scoped history, and fail-closed lookups.
"""

from __future__ import annotations

import dataclasses
from platform.runtime_operations.errors import (
    RuntimeOperationLedgerError,
    RuntimeOperationLineageError,
)
from platform.runtime_operations.ledger import (
    GENESIS_HASH,
    RuntimeOperationLedger,
    RuntimeOperationLedgerView,
    RuntimeOperationLineageView,
)
from platform.runtime_operations.operations import RuntimeOperationPlanner
from platform.tests.runtime_operations_helpers import certification_record, runtime_unit


def _record(runtime_id="UCOS-RUN-data-0123456789abcdef", blueprint="UCOS-BLPR-1", env="runtime"):
    unit = runtime_unit(runtime_id=runtime_id, blueprint=blueprint, environment=env)
    return (
        RuntimeOperationPlanner()
        .plan_deploy(unit, certification_record(), owner_subject="op@x")
        .record
    )


def test_empty_ledger():
    ledger = RuntimeOperationLedger()
    assert len(ledger) == 0
    assert ledger.head_hash == GENESIS_HASH
    assert ledger.verify() is True


def test_append_idempotent_and_chain():
    ledger = RuntimeOperationLedger()
    rec = _record()
    entry = ledger.append(rec)
    assert entry.sequence == 0
    assert entry.prev_hash == GENESIS_HASH
    assert rec.operation_id in ledger
    # idempotent
    again = ledger.append(rec)
    assert again.entry_hash == entry.entry_hash
    assert len(ledger) == 1
    assert ledger.verify() is True
    ledger.require_intact()


def test_append_rejects_bad_record():
    ledger = RuntimeOperationLedger()
    try:
        ledger.append("nope")  # type: ignore[arg-type]
        raise AssertionError("expected error")
    except RuntimeOperationLedgerError:
        pass


def test_multi_entry_chain_and_views():
    ledger = RuntimeOperationLedger()
    rec1 = _record(env="runtime")
    rec2 = _record(env="production")
    ledger.append(rec1)
    ledger.append(rec2)
    assert len(ledger) == 2
    assert len(ledger.entries) == 2
    assert ledger.entries[0].to_dict()["operation_id"] == rec1.operation_id
    views = ledger.views()
    assert all(isinstance(v, RuntimeOperationLedgerView) for v in views)
    assert ledger.view(rec1.operation_id).sequence == 0
    assert ledger.get(rec2.operation_id).sequence == 1
    assert len(ledger.by_runtime(rec1.runtime_id)) == 2
    assert ledger.to_dict()["count"] == 2
    assert ledger.fingerprint() == ledger.fingerprint()
    assert views[0].to_dict()["operation_id"] == rec1.operation_id


def test_lookup_fail_closed():
    ledger = RuntimeOperationLedger()
    try:
        ledger.get("UCOS-ROPR-missing")
        raise AssertionError("expected error")
    except RuntimeOperationLedgerError:
        pass


def test_tamper_detection():
    ledger = RuntimeOperationLedger()
    ledger.append(_record())
    ledger._entries[0] = dataclasses.replace(ledger._entries[0], descriptor_sha256="tampered")
    assert ledger.verify() is False
    try:
        ledger.require_intact()
        raise AssertionError("expected error")
    except RuntimeOperationLedgerError:
        pass


def test_tamper_sequence_break():
    ledger = RuntimeOperationLedger()
    ledger.append(_record(env="runtime"))
    ledger.append(_record(env="production"))
    ledger._entries[1] = dataclasses.replace(ledger._entries[1], prev_hash="0" * 64)
    assert ledger.verify() is False


def test_lineage():
    ledger = RuntimeOperationLedger()
    rec1 = _record(env="runtime")
    rec2 = _record(env="production")
    ledger.append(rec1)
    ledger.append(rec2)
    root = ledger.lineage(rec1.operation_id)
    assert isinstance(root, RuntimeOperationLineageView)
    assert root.is_root is True
    assert root.parent is None
    assert root.child == rec2.operation_id
    child = ledger.lineage(rec2.operation_id)
    assert child.is_root is False
    assert child.parent == rec1.operation_id
    assert child.depth == 1
    assert rec1.operation_id in child.runtime_ancestors
    assert child.to_dict()["depth"] == 1
    assert child.fingerprint() == child.fingerprint()
    assert len(ledger.ancestry(rec2.operation_id)) == 1


def test_lineage_fail_closed():
    ledger = RuntimeOperationLedger()
    try:
        ledger.lineage("UCOS-ROPR-missing")
        raise AssertionError("expected error")
    except RuntimeOperationLineageError:
        pass


def test_view_from_bad_entry():
    try:
        RuntimeOperationLedgerView.from_entry("nope")  # type: ignore[arg-type]
        raise AssertionError("expected error")
    except RuntimeOperationLedgerError:
        pass
