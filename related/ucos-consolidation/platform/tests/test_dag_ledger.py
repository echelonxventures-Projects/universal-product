"""WP-03 — DAG Event Ledger tests (PRJ-C2 · ACT-C2).

Covers the append-only, Merkle-linked event DAG that supersedes the linear event
model while preserving backward compatibility: content-addressed Merkle events with
parent references, head/root computation, DAG integrity (tamper-evident) and
acyclicity verification, first-class branch and merge, deterministic export/import
(replay), and the linear-model migration + projection layer (AIF-L08 / AIF-L17 / A/G1).
"""

from __future__ import annotations

import dataclasses
from platform.foundation.dag_ledger import (
    DAG_LEDGER_FORMAT,
    EVENT_ID_PREFIX,
    DagEvent,
    EventDag,
)
from platform.foundation.errors import DagLedgerError, DagLedgerIntegrityError
from platform.foundation.events import EventBus, PlatformEvent

import pytest

from engine.foundation.obs.context import reset_correlation_id, set_correlation_id

# --------------------------------------------------------------------------------
# DagEvent — content-addressed Merkle identity
# --------------------------------------------------------------------------------


def test_event_is_content_addressed_and_deterministic():
    a = DagEvent.create("t", "src", "subj", payload={"k": 1})
    b = DagEvent.create("t", "src", "subj", payload={"k": 1})
    assert a.event_hash == b.event_hash
    assert a.event_id == b.event_id
    assert a.event_id.startswith(EVENT_ID_PREFIX)
    assert a.is_root is True
    assert a.is_merge is False
    assert a.verify_integrity() is True


def test_event_hash_binds_parents_and_ignores_parent_order():
    root = DagEvent.create("t", "src", "s")
    other = DagEvent.create("t2", "src", "s")
    # Same content, different parents ⇒ different Merkle identity.
    child_a = DagEvent.create("c", "src", "s", parents=(root.event_hash,))
    child_b = DagEvent.create("c", "src", "s", parents=(other.event_hash,))
    assert child_a.event_hash != child_b.event_hash
    # Parent *order* is not identity-significant (sorted in the hash).
    m1 = DagEvent.create("m", "src", "s", parents=(root.event_hash, other.event_hash))
    m2 = DagEvent.create("m", "src", "s", parents=(other.event_hash, root.event_hash))
    assert m1.event_hash == m2.event_hash
    assert m1.is_merge is True


def test_event_validation():
    with pytest.raises(DagLedgerError):
        DagEvent.create("", "src", "s")
    with pytest.raises(DagLedgerError):
        DagEvent.create("t", "", "s")
    with pytest.raises(DagLedgerError):
        DagEvent.create("t", "src", 123)  # type: ignore[arg-type]
    with pytest.raises(DagLedgerError):
        DagEvent.create("t", "src", "s", index=-1)
    with pytest.raises(DagLedgerError):
        DagEvent.create("t", "src", "s", parents=("",))


def test_event_preserves_supplied_event_id():
    e = DagEvent.create("t", "src", "s", event_id="UCOS-EVT-legacy0001")
    assert e.event_id == "UCOS-EVT-legacy0001"
    # The Merkle hash is still content-addressed regardless of the id.
    assert e.verify_integrity() is True


def test_event_to_dict_from_dict_roundtrip():
    e = DagEvent.create("t", "src", "s", payload={"a": 1}, index=3)
    restored = DagEvent.from_dict(e.to_dict())
    assert restored.event_hash == e.event_hash
    assert restored.index == 3


def test_event_from_dict_errors():
    with pytest.raises(DagLedgerError):
        DagEvent.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(DagLedgerError):
        DagEvent.from_dict({"source": "s", "subject": "x"})  # missing event_type


# --------------------------------------------------------------------------------
# EventDag — append (linear-compatible), heads, roots
# --------------------------------------------------------------------------------


def test_append_is_linear_by_default_and_ordered():
    dag = EventDag()
    e0 = dag.append("a", "src", "s0")
    e1 = dag.append("b", "src", "s1")
    e2 = dag.append("c", "src", "s2")
    assert e0.is_root and e0.parents == ()
    assert e1.parents == (e0.event_hash,)
    assert e2.parents == (e1.event_hash,)
    assert [e.index for e in dag.events] == [0, 1, 2]
    assert dag.heads == (e2.event_hash,)
    assert dag.roots == (e0.event_hash,)
    assert len(dag) == 3
    assert dag.verify() is True
    dag.require_intact()


def test_empty_dag_has_no_heads_or_roots():
    dag = EventDag()
    assert dag.heads == ()
    assert dag.roots == ()
    assert dag.events == ()
    assert dag.verify() is True


def test_append_is_idempotent_by_event_hash():
    dag = EventDag()
    first = dag.append("a", "src", "s", payload={"x": 1})
    # Re-appending identical content with identical (empty) parents is a no-op.
    again = DagEvent.create("a", "src", "s", payload={"x": 1})
    assert again.event_hash == first.event_hash
    dup = dag._append("a", "src", "s", parents=(), payload={"x": 1})
    assert dup.event_hash == first.event_hash
    assert len(dag) == 1


def test_append_unknown_parent_fails_closed():
    dag = EventDag()
    with pytest.raises(DagLedgerError):
        dag.append("a", "src", "s", parents=("0" * 64,))


def test_get_contains_children_ancestors():
    dag = EventDag()
    e0 = dag.append("a", "src", "s0")
    e1 = dag.append("b", "src", "s1")
    # get by hash and by legacy event_id
    assert dag.get(e0.event_hash) is e0
    assert dag.get(e0.event_id) is e0
    assert e0.event_hash in dag
    assert e0.event_id in dag
    assert "missing" not in dag
    assert dag.children(e0.event_hash) == (e1,)
    assert dag.ancestors(e1.event_hash) == (e0,)
    assert dag.ancestors(e0.event_hash) == ()
    with pytest.raises(DagLedgerError):
        dag.get("no-such-event")


def test_correlation_id_is_bound_on_append():
    dag = EventDag()
    token = set_correlation_id("corr-xyz")
    try:
        e = dag.append("t", "src", "s")
    finally:
        reset_correlation_id(token)
    assert e.correlation_id == "corr-xyz"


# --------------------------------------------------------------------------------
# Branch & merge — first-class DAG topology (AIF-L08 / A/G1)
# --------------------------------------------------------------------------------


def test_branch_creates_a_second_head():
    dag = EventDag()
    root = dag.append("root", "src", "s")
    left = dag.branch(root.event_hash, "left", "src", "s")
    right = dag.branch(root.event_hash, "right", "src", "s")
    assert left.parents == (root.event_hash,)
    assert right.parents == (root.event_hash,)
    assert set(dag.heads) == {left.event_hash, right.event_hash}
    assert dag.roots == (root.event_hash,)
    assert dag.verify() is True


def test_append_with_multiple_heads_fails_closed():
    dag = EventDag()
    root = dag.append("root", "src", "s")
    dag.branch(root.event_hash, "left", "src", "s")
    dag.branch(root.event_hash, "right", "src", "s")
    with pytest.raises(DagLedgerError):
        dag.append("ambiguous", "src", "s")


def test_merge_converges_branches():
    dag = EventDag()
    root = dag.append("root", "src", "s")
    left = dag.branch(root.event_hash, "left", "src", "s")
    right = dag.branch(root.event_hash, "right", "src", "s")
    merged = dag.merge((left.event_hash, right.event_id), "merge", "src", "s", payload={"n": 1})
    assert merged.is_merge is True
    assert set(merged.parents) == {left.event_hash, right.event_hash}
    assert dag.heads == (merged.event_hash,)
    assert {a.event_hash for a in dag.ancestors(merged.event_hash)} == {
        root.event_hash,
        left.event_hash,
        right.event_hash,
    }
    assert dag.verify() is True
    # After a merge there is a single head again ⇒ plain append works.
    tail = dag.append("tail", "src", "s")
    assert tail.parents == (merged.event_hash,)


def test_merge_requires_two_parents():
    dag = EventDag()
    root = dag.append("root", "src", "s")
    with pytest.raises(DagLedgerError):
        dag.merge((root.event_hash,), "m", "src", "s")
    with pytest.raises(DagLedgerError):
        dag.merge((), "m", "src", "s")


def test_branch_and_merge_unknown_reference_fails_closed():
    dag = EventDag()
    dag.append("root", "src", "s")
    with pytest.raises(DagLedgerError):
        dag.branch("no-such", "x", "src", "s")
    with pytest.raises(DagLedgerError):
        dag.merge(("no-such-1", "no-such-2"), "m", "src", "s")


# --------------------------------------------------------------------------------
# Integrity — tamper-evidence & acyclicity
# --------------------------------------------------------------------------------


def test_tampering_a_recorded_event_breaks_verification():
    dag = EventDag()
    dag.append("a", "src", "s0")
    e1 = dag.append("b", "src", "s1")
    # Forge a mutated event that keeps the old event_hash (Recorded Truth edit).
    forged = dataclasses.replace(e1, payload={"x": "tampered"})
    assert forged.verify_integrity() is False
    dag._nodes[e1.event_hash] = forged
    assert dag.verify() is False
    with pytest.raises(DagLedgerIntegrityError):
        dag.require_intact()


def test_verify_detects_broken_topology():
    dag = EventDag()
    e0 = dag.append("a", "src", "s0")
    e1 = dag.append("b", "src", "s1")
    # Reverse the recorded order so a parent appears *after* its child.
    dag._order = [e1.event_hash, e0.event_hash]
    assert dag.verify() is False


# --------------------------------------------------------------------------------
# Export / import — deterministic replay
# --------------------------------------------------------------------------------


def _sample_dag() -> EventDag:
    dag = EventDag()
    root = dag.append("root", "src", "s")
    left = dag.branch(root.event_hash, "left", "src", "s", payload={"side": "L"})
    right = dag.branch(root.event_hash, "right", "src", "s", payload={"side": "R"})
    dag.merge((left.event_hash, right.event_hash), "merge", "src", "s")
    return dag


def test_export_shape_and_fingerprint_determinism():
    dag = _sample_dag()
    exported = dag.export()
    assert exported["ledger_format"] == DAG_LEDGER_FORMAT
    assert exported["count"] == 4
    assert len(exported["events"]) == 4
    # to_dict is the same canonical surface.
    assert dag.to_dict() == exported
    # Two independently-built identical DAGs fingerprint identically (replay).
    assert dag.fingerprint() == _sample_dag().fingerprint()


def test_import_roundtrip_preserves_dag_and_verifies():
    dag = _sample_dag()
    restored = EventDag.from_dict(dag.export())
    assert restored.verify() is True
    assert len(restored) == len(dag)
    assert restored.fingerprint() == dag.fingerprint()
    assert set(restored.heads) == set(dag.heads)


def test_import_rejects_malformed_export():
    with pytest.raises(DagLedgerError):
        EventDag.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(DagLedgerError):
        EventDag.from_dict({"ledger_format": DAG_LEDGER_FORMAT})  # no 'events'


def test_import_detects_tampered_event_hash():
    dag = EventDag()
    dag.append("a", "src", "s")
    exported = dag.export()
    exported["events"][0]["payload"] = {"x": "tampered"}  # hash no longer matches
    with pytest.raises(DagLedgerIntegrityError):
        EventDag.from_dict(exported)


def test_import_detects_out_of_order_parents():
    dag = EventDag()
    e0 = dag.append("a", "src", "s0")
    dag.append("b", "src", "s1")
    exported = dag.export()
    exported["events"].reverse()  # child now precedes its parent
    with pytest.raises(DagLedgerError):
        EventDag.from_dict(exported)
    # sanity: e0 really was the first-appended root
    assert e0.is_root


# --------------------------------------------------------------------------------
# Backward-compatible migration layer
# --------------------------------------------------------------------------------


def test_migrate_from_platform_events_preserves_order_and_ids():
    events = [
        PlatformEvent.create("a", "src", "s0", 0),
        PlatformEvent.create("b", "src", "s1", 1),
        PlatformEvent.create("c", "src", "s2", 2),
    ]
    dag = EventDag.from_platform_events(events)
    assert len(dag) == 3
    # Linear chain: exactly one head, one root.
    assert len(dag.heads) == 1 and len(dag.roots) == 1
    # Original UCOS-EVT- ids preserved verbatim (history not rewritten).
    assert [e.event_id for e in dag.events] == [ev.event_id for ev in events]
    assert dag.verify() is True


def test_migrate_from_event_bus_and_project_back():
    bus = EventBus()
    bus.publish("a", "src", "s0", payload={"k": 1})
    bus.publish("b", "src", "s1")
    dag = EventDag.from_event_bus(bus)
    projected = dag.to_platform_events()
    # Projection preserves order, sequence, ids, and payload (backward compat).
    assert [p.event_id for p in projected] == [e.event_id for e in bus.events]
    assert [p.sequence for p in projected] == [0, 1]
    assert projected[0].payload == {"k": 1}
    assert all(isinstance(p, PlatformEvent) for p in projected)


def test_from_event_bus_rejects_non_bus():
    with pytest.raises(DagLedgerError):
        EventDag.from_event_bus(["not", "a", "bus"])  # type: ignore[arg-type]


def test_from_platform_event_rejects_non_event():
    with pytest.raises(DagLedgerError):
        DagEvent.from_platform_event({"not": "an event"})  # type: ignore[arg-type]


def test_from_platform_event_wraps_and_preserves_identity():
    pe = PlatformEvent.create("t", "src", "s", 5, payload={"z": 9})
    node = DagEvent.from_platform_event(pe, parents=())
    assert node.event_id == pe.event_id  # legacy id preserved
    assert node.index == 5  # sequence carried as admission ordinal
    assert node.payload == {"z": 9}
    back = node.to_platform_event()
    assert back.event_id == pe.event_id
    assert back.sequence == 5
