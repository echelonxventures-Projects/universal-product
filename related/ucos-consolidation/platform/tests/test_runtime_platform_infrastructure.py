"""EPIC-007 (T7) — Runtime infrastructure / placement tests."""

from __future__ import annotations

from platform.runtime_platform.errors import RuntimeInfrastructureError
from platform.runtime_platform.infrastructure import (
    CapacityPosture,
    PlacementDecision,
    RuntimeInfrastructure,
)

import pytest


def test_default_posture_capacity():
    posture = CapacityPosture()
    assert posture.partition_count == 3
    assert posture.total_capacity == 12
    assert posture.fingerprint() == CapacityPosture().fingerprint()


def test_posture_validation_fail_closed():
    with pytest.raises(RuntimeInfrastructureError):
        CapacityPosture(partitions=())
    with pytest.raises(RuntimeInfrastructureError):
        CapacityPosture(partitions=("a", "a"))
    with pytest.raises(RuntimeInfrastructureError):
        CapacityPosture(partitions=("",))
    with pytest.raises(RuntimeInfrastructureError):
        CapacityPosture(slots_per_partition=0)


def test_placement_is_deterministic_and_within_posture():
    infra = RuntimeInfrastructure()
    d1 = infra.place("workload-x")
    d2 = infra.place("workload-x")
    assert d1.placement_id == d2.placement_id
    assert d1.partition in infra.posture.partitions
    assert 0 <= d1.slot < infra.posture.slots_per_partition
    assert d1.placement_id.startswith("UCOS-URPP-")


def test_placement_distributes_across_partitions():
    infra = RuntimeInfrastructure()
    partitions = {infra.place(f"w{i}").partition for i in range(50)}
    assert len(partitions) > 1


def test_place_requires_workload_id():
    infra = RuntimeInfrastructure()
    with pytest.raises(RuntimeInfrastructureError):
        infra.place("")


def test_infrastructure_rejects_bad_posture():
    with pytest.raises(RuntimeInfrastructureError):
        RuntimeInfrastructure("not-a-posture")  # type: ignore[arg-type]


def test_summary_and_placement_to_dict():
    infra = RuntimeInfrastructure(CapacityPosture(partitions=("p",), slots_per_partition=2))
    assert infra.summary()["total_capacity"] == 2
    decision = infra.place("w")
    assert isinstance(decision, PlacementDecision)
    assert decision.to_dict()["workload_id"] == "w"
    assert infra.fingerprint() == infra.posture.fingerprint()
