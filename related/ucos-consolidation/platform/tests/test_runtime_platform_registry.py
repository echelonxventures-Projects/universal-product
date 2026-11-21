"""EPIC-007 (T7) — Execution registry (append-only, hash-chained) tests."""

from __future__ import annotations

import dataclasses
from platform.runtime_platform.errors import ExecutionRegistryError
from platform.runtime_platform.execution import ExecutionEngine
from platform.runtime_platform.registry import GENESIS_HASH, ExecutionRegistry
from platform.tests.runtime_platform_helpers import request

import pytest


def _record(engine, workload_id, *, workflow_id=None, fail=False):
    return engine.run(request(workload_id, inject_failure=fail), workflow_id=workflow_id)


def test_register_appends_and_chains():
    engine = ExecutionEngine()
    reg = ExecutionRegistry()
    assert reg.head_hash == GENESIS_HASH
    e0 = reg.register(_record(engine, "a"))
    e1 = reg.register(_record(engine, "b"))
    assert e0.sequence == 0 and e1.sequence == 1
    assert e1.prev_hash == e0.entry_hash
    assert len(reg) == 2
    assert reg.verify()


def test_register_is_idempotent():
    engine = ExecutionEngine()
    reg = ExecutionRegistry()
    record = _record(engine, "a")
    first = reg.register(record)
    second = reg.register(record)
    assert first.entry_hash == second.entry_hash
    assert len(reg) == 1
    assert record.execution_id in reg


def test_get_and_entry_and_records():
    engine = ExecutionEngine()
    reg = ExecutionRegistry()
    record = _record(engine, "a")
    reg.register(record)
    assert reg.get(record.execution_id) is record
    assert reg.entry(record.execution_id).execution_id == record.execution_id
    assert reg.records() == (record,)


def test_get_and_entry_absent_fail_closed():
    reg = ExecutionRegistry()
    with pytest.raises(ExecutionRegistryError):
        reg.get("missing")
    with pytest.raises(ExecutionRegistryError):
        reg.entry("missing")
    with pytest.raises(ExecutionRegistryError):
        reg.lineage("missing")


def test_register_requires_record():
    with pytest.raises(ExecutionRegistryError):
        ExecutionRegistry().register("bad")  # type: ignore[arg-type]


def test_by_workflow_and_by_state_and_census():
    engine = ExecutionEngine()
    reg = ExecutionRegistry()
    reg.register(_record(engine, "a", workflow_id="wf"))
    reg.register(_record(engine, "b", workflow_id="wf"))
    reg.register(_record(engine, "c", fail=True))
    assert {r.workload_id for r in reg.by_workflow("wf")} == {"a", "b"}
    assert len(reg.by_state("succeeded")) == 2
    assert len(reg.by_state("failed")) == 1
    census = reg.census()
    assert census["total"] == 3
    assert census["succeeded"] == 2
    assert census["failed"] == 1


def test_lineage_chain_and_workflow_siblings():
    engine = ExecutionEngine()
    reg = ExecutionRegistry()
    r0 = _record(engine, "a", workflow_id="wf")
    r1 = _record(engine, "b", workflow_id="wf")
    reg.register(r0)
    reg.register(r1)
    lineage = reg.lineage(r1.execution_id)
    assert lineage.parent == r0.execution_id
    assert lineage.child is None
    assert lineage.depth == 1
    assert r0.execution_id in lineage.workflow_siblings
    assert lineage.lineage_id.startswith("UCOS-URPL-")
    root = reg.lineage(r0.execution_id)
    assert root.is_root
    assert root.parent is None
    assert root.child == r1.execution_id


def test_tamper_detection():
    engine = ExecutionEngine()
    reg = ExecutionRegistry()
    reg.register(_record(engine, "a"))
    reg.register(_record(engine, "b"))
    assert reg.verify()
    # Corrupt a recorded entry: the chain must detect it.
    reg._entries[0] = dataclasses.replace(reg._entries[0], record_sha256="deadbeef")
    assert not reg.verify()
    with pytest.raises(ExecutionRegistryError):
        reg.require_intact()


def test_to_dict_and_fingerprint():
    engine = ExecutionEngine()
    reg = ExecutionRegistry()
    reg.register(_record(engine, "a"))
    payload = reg.to_dict()
    assert payload["count"] == 1
    assert payload["intact"] is True
    assert reg.fingerprint() == reg.fingerprint()
    assert reg.entries[0].to_dict()["execution_id"]
