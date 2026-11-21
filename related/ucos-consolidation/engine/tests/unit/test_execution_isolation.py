"""EPIC-RTE-002 — Execution Isolation unit tests."""

from __future__ import annotations

import dataclasses

import pytest

from engine.runtime.execution.errors import ExecutionIsolationError
from engine.runtime.execution.isolation import (
    ISOLATION_FORMAT,
    IsolationPartition,
    IsolationView,
    isolate,
)


def test_isolate_single_context(composition):
    view = isolate(composition)
    assert isinstance(view, IsolationView)
    assert len(view.partitions) == 1
    partition = view.partitions[0]
    assert partition.context_id == "ctx1"
    assert set(partition.members) == {"A", "B", "C", "D"}


def test_partition_of_and_context_of(composition):
    view = isolate(composition)
    assert view.context_of("A") == "ctx1"
    assert view.partition_of("D").contains("D")


def test_partition_of_unbounded_raises(composition):
    view = isolate(composition)
    with pytest.raises(ExecutionIsolationError) as exc:
        view.partition_of("ZZZ")
    assert exc.value.code == "RT-EXEC-ISO-001"


def test_isolate_two_contexts_with_federation(federated_composition):
    view = isolate(federated_composition)
    assert {p.context_id for p in view.partitions} == {"ctx1", "ctx2"}


def test_isolate_detects_unauthorised_cross_context(federated_composition):
    # Strip the reference frames so the cross-context dependency is no longer
    # authorised — isolation must fail closed.
    broken = dataclasses.replace(federated_composition, reference_frames=())
    with pytest.raises(ExecutionIsolationError):
        isolate(broken)


def test_isolation_view_to_dict(composition):
    blob = isolate(composition).to_dict()
    assert blob["isolation_format"] == ISOLATION_FORMAT
    assert blob["partition_count"] == 1


def test_partition_to_dict():
    partition = IsolationPartition(context_id="ctx1", members=("A", "B"))
    assert partition.to_dict() == {"context_id": "ctx1", "members": ["A", "B"]}
