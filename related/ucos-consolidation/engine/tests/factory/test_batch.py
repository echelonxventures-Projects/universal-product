"""TASK-000045 — Multi-blueprint batch execution tests (TASK-000044)."""

from __future__ import annotations

import json

from engine.factory import generate_many
from engine.factory.contracts import FactoryRequest, GenerationStatus


def _requests(*ids):
    return [FactoryRequest(bp) for bp in ids]


def test_batch_generates_all_in_deterministic_order(orchestrator):
    results = generate_many(
        orchestrator,
        _requests("BP-SERVICE-0001", "BP-DATA-0001", "BP-API-0001", "BP-APPLICATION-0001"),
    )
    # returned sorted by blueprint id regardless of input order
    assert [r.blueprint_id for r in results] == [
        "BP-API-0001",
        "BP-APPLICATION-0001",
        "BP-DATA-0001",
        "BP-SERVICE-0001",
    ]
    by_id = {r.blueprint_id: r for r in results}
    assert by_id["BP-DATA-0001"].status is GenerationStatus.GENERATED
    assert by_id["BP-API-0001"].status is GenerationStatus.GAP


def test_batch_dedupes_repeated_ids(orchestrator):
    results = generate_many(orchestrator, _requests("BP-DATA-0001", "BP-DATA-0001"))
    assert len(results) == 1
    assert results[0].blueprint_id == "BP-DATA-0001"


def test_batch_is_deterministic(orchestrator):
    ids = ("BP-DATA-0001", "BP-API-0001", "BP-SERVICE-0001")
    a = generate_many(orchestrator, _requests(*ids))
    b = generate_many(orchestrator, _requests(*reversed(ids)))
    dump_a = json.dumps([r.to_dict() for r in a], sort_keys=True)
    dump_b = json.dumps([r.to_dict() for r in b], sort_keys=True)
    assert dump_a == dump_b


def test_batch_empty_input(orchestrator):
    assert generate_many(orchestrator, []) == ()
