"""EPIC-007 (Terminal T7) — Runtime Infrastructure (Universal Runtime Platform).

The **technology-neutral** runtime substrate model — realizing ``PRS-002`` Workload
Placement and ``PRS-004`` Capacity Governance. It selects **no** cloud, node, host,
cluster, container, orchestrator, or product (PEP-010): it models capacity as an
abstract set of named **partitions**, each offering a fixed number of execution
**slots**, and places a workload onto a partition by a **deterministic** content hash of
its identity — so identical inputs always place identically and the placement is
replayable (no wall-clock, no ambient state).

    * :class:`CapacityPosture` — the immutable, governed capacity posture (partitions ×
      slots), with a deterministic total-capacity view.
    * :class:`PlacementDecision` — the immutable, content-addressed placement of one
      workload onto a partition.
    * :class:`RuntimeInfrastructure` — the placement engine over a posture: deterministic
      partition assignment and a capacity summary.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.runtime_platform.errors import RuntimeInfrastructureError
from typing import Any

#: The recorded infrastructure posture format.
INFRASTRUCTURE_FORMAT = "ucos-runtime-infrastructure/1.0.0"

#: The default technology-neutral capacity posture (three partitions, four slots each).
DEFAULT_PARTITIONS: tuple[str, ...] = ("partition-a", "partition-b", "partition-c")
DEFAULT_SLOTS_PER_PARTITION = 4


@dataclass(frozen=True, slots=True)
class CapacityPosture:
    """An immutable, governed, technology-neutral capacity posture (PRS-004).

    ``partitions`` are opaque, ordered capacity domains; ``slots_per_partition`` is the
    governed concurrency each partition offers. No product/topology is named.
    """

    partitions: tuple[str, ...] = DEFAULT_PARTITIONS
    slots_per_partition: int = DEFAULT_SLOTS_PER_PARTITION

    def __post_init__(self) -> None:
        if not self.partitions:
            raise RuntimeInfrastructureError("capacity posture requires at least one partition")
        if len(set(self.partitions)) != len(self.partitions):
            raise RuntimeInfrastructureError("capacity partitions must be unique")
        for name in self.partitions:
            if not isinstance(name, str) or not name:
                raise RuntimeInfrastructureError("capacity partition names must be non-empty")
        if not isinstance(self.slots_per_partition, int) or self.slots_per_partition < 1:
            raise RuntimeInfrastructureError(
                "slots_per_partition must be a positive integer",
                slots_per_partition=self.slots_per_partition,
            )

    @property
    def partition_count(self) -> int:
        return len(self.partitions)

    @property
    def total_capacity(self) -> int:
        """The governed total execution capacity (partitions × slots)."""
        return self.partition_count * self.slots_per_partition

    def to_dict(self) -> dict[str, Any]:
        return {
            "infrastructure_format": INFRASTRUCTURE_FORMAT,
            "partitions": list(self.partitions),
            "partition_count": self.partition_count,
            "slots_per_partition": self.slots_per_partition,
            "total_capacity": self.total_capacity,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class PlacementDecision:
    """An immutable, content-addressed placement of a workload onto a partition (PRS-002)."""

    workload_id: str
    partition: str
    slot: int
    posture_fingerprint: str
    placement_id: str = ""

    @classmethod
    def create(
        cls, *, workload_id: str, partition: str, slot: int, posture_fingerprint: str
    ) -> PlacementDecision:
        core = {
            "workload_id": workload_id,
            "partition": partition,
            "slot": slot,
            "posture_fingerprint": posture_fingerprint,
        }
        return cls(
            workload_id=workload_id,
            partition=partition,
            slot=slot,
            posture_fingerprint=posture_fingerprint,
            placement_id=f"UCOS-URPP-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "placement_id": self.placement_id,
            "workload_id": self.workload_id,
            "partition": self.partition,
            "slot": self.slot,
            "posture_fingerprint": self.posture_fingerprint,
        }


class RuntimeInfrastructure:
    """The deterministic workload-placement engine over a :class:`CapacityPosture`."""

    __slots__ = ("_posture",)

    def __init__(self, posture: CapacityPosture | None = None) -> None:
        if posture is not None and not isinstance(posture, CapacityPosture):
            raise RuntimeInfrastructureError("RuntimeInfrastructure requires a CapacityPosture")
        self._posture = posture if posture is not None else CapacityPosture()

    @property
    def posture(self) -> CapacityPosture:
        return self._posture

    def place(self, workload_id: str) -> PlacementDecision:
        """Deterministically place ``workload_id`` onto a partition + slot (replayable)."""
        if not isinstance(workload_id, str) or not workload_id:
            raise RuntimeInfrastructureError("place requires a non-empty workload_id")
        # Deterministic assignment from the content hash of the workload identity.
        digest = int(content_hash({"workload_id": workload_id}), 16)
        partition_index = digest % self._posture.partition_count
        slot = (digest // self._posture.partition_count) % self._posture.slots_per_partition
        return PlacementDecision.create(
            workload_id=workload_id,
            partition=self._posture.partitions[partition_index],
            slot=slot,
            posture_fingerprint=self._posture.fingerprint(),
        )

    def summary(self) -> dict[str, Any]:
        return {
            "posture": self._posture.to_dict(),
            "total_capacity": self._posture.total_capacity,
        }

    def fingerprint(self) -> str:
        return self._posture.fingerprint()


__all__ = [
    "INFRASTRUCTURE_FORMAT",
    "DEFAULT_PARTITIONS",
    "DEFAULT_SLOTS_PER_PARTITION",
    "CapacityPosture",
    "PlacementDecision",
    "RuntimeInfrastructure",
]
