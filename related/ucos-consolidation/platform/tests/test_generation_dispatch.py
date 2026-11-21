"""EC2-TASK-000112 — Generation request dispatch tests (EC2-EPIC-007).

Covers the execution-dispatch boundary: DispatchRecord bound to the certified EC-1
execution contracts by reference, fail-closed validation (target must be a certified
engine contract; no live engine import), the append-only DispatchLedger (idempotent by
id, fail-closed on a conflicting handoff), and the handoff edge audit evidence.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import ENGINE_CONTRACTS
from platform.generation.dispatch import (
    DEFAULT_EXECUTION_TARGET,
    DISPATCH_CONTRACTS,
    FACTORY_CONTRACT,
    RUNTIME_CONTRACT,
    DispatchLedger,
    DispatchRecord,
    all_dispatch_contracts,
)
from platform.generation.errors import RequestDispatchError

import pytest


def _record(**kw):
    base = dict(
        request_ref="UCOS-GREQ-1",
        blueprint_ref="UCOS-BLPR-abc",
        family=BlueprintFamily.DATA,
        content_hash="c0ffee",
        tick=5,
    )
    base.update(kw)
    return DispatchRecord.create(**base)


def test_dispatch_contracts_are_certified_engine_refs_by_reference():
    engine_names = {ref.name for ref in ENGINE_CONTRACTS}
    for ref in DISPATCH_CONTRACTS:
        assert ref.name in engine_names
    assert FACTORY_CONTRACT in all_dispatch_contracts()
    assert RUNTIME_CONTRACT in all_dispatch_contracts()
    assert DEFAULT_EXECUTION_TARGET == RUNTIME_CONTRACT


def test_record_is_content_addressed_and_deterministic():
    a = _record()
    b = _record()
    assert a.dispatch_id == b.dispatch_id
    assert a.dispatch_id.startswith("UCOS-GDSP-")
    assert a.engine_contracts == all_dispatch_contracts()


def test_record_default_and_explicit_target():
    assert _record().execution_target == RUNTIME_CONTRACT
    assert _record(execution_target=FACTORY_CONTRACT).execution_target == FACTORY_CONTRACT


def test_record_parameters_sorted_and_serialized():
    rec = _record(parameters={"b": "2", "a": "1"})
    assert list(rec.to_dict()["parameters"]) == ["a", "b"]


@pytest.mark.parametrize(
    "kw",
    [
        {"request_ref": ""},
        {"blueprint_ref": ""},
        {"family": "data"},
        {"content_hash": ""},
        {"tick": "5"},
        {"tick": True},
        {"execution_target": "engine.unknown.call"},
        {"parameters": {"": "v"}},
        {"parameters": {"k": 1}},
    ],
)
def test_record_rejects_malformed(kw):
    with pytest.raises(RequestDispatchError):
        _record(**kw)


def test_handoff_edge_is_audit_evidence():
    edge = _record().handoff_edge()
    assert edge["boundary"] == "generation-request-dispatch"
    assert edge["request"]["request_ref"] == "UCOS-GREQ-1"
    assert edge["execution"]["target"] == RUNTIME_CONTRACT
    assert RUNTIME_CONTRACT in edge["execution"]["engine_contracts"]


def test_record_fingerprint_and_to_dict_deterministic():
    a = _record(parameters={"k": "v"})
    b = _record(parameters={"k": "v"})
    assert a.fingerprint() == b.fingerprint()
    assert a.to_dict()["dispatch_id"] == a.dispatch_id


def test_ledger_record_and_get():
    ledger = DispatchLedger()
    rec = _record()
    stored = ledger.record(rec)
    assert stored is rec
    assert ledger.has("UCOS-GREQ-1")
    assert "UCOS-GREQ-1" in ledger
    assert ledger.get("UCOS-GREQ-1") is rec
    assert ledger.by_dispatch_id(rec.dispatch_id) is rec
    assert len(ledger) == 1


def test_ledger_idempotent_on_identical_record():
    ledger = DispatchLedger()
    rec = _record()
    ledger.record(rec)
    assert ledger.record(_record()) is rec  # identical id ⇒ returns stored


def test_ledger_rejects_conflicting_dispatch():
    ledger = DispatchLedger()
    ledger.record(_record())
    with pytest.raises(RequestDispatchError):
        ledger.record(_record(content_hash="different"))


def test_ledger_rejects_non_record_and_absent_lookups():
    ledger = DispatchLedger()
    with pytest.raises(RequestDispatchError):
        ledger.record("nope")  # type: ignore[arg-type]
    with pytest.raises(RequestDispatchError):
        ledger.get("UCOS-GREQ-missing")
    with pytest.raises(RequestDispatchError):
        ledger.by_dispatch_id("UCOS-GDSP-missing")


def test_ledger_fingerprint_and_all_deterministic():
    def build():
        ledger = DispatchLedger()
        ledger.record(_record(request_ref="UCOS-GREQ-1", tick=1))
        ledger.record(_record(request_ref="UCOS-GREQ-2", tick=2))
        return ledger

    assert build().fingerprint() == build().fingerprint()
    assert build().request_refs == ("UCOS-GREQ-1", "UCOS-GREQ-2")
    assert len(build().all()) == 2
