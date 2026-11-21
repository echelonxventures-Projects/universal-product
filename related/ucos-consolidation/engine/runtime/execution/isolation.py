"""EPIC-RTE-002 — Execution Isolation (Runtime Execution Platform).

Realises **Execution Isolation**: the execution-time view of the bounding-context
partitions that already govern a :class:`~engine.runtime.composition.RuntimeComposition`.
Every composed Universe is bounded by exactly one runtime context
(RUNTIME-013 ORL-05/ORL-14) and no execution may cross a context boundary without
an explicit federation (ORL-13).

This module **reuses the composition's already-resolved contexts and reference
frames verbatim** (:class:`~engine.runtime.context.RuntimeContext` /
:class:`~engine.runtime.context.ReferenceFrame`, EPIC-006) — it re-resolves
nothing and adds no isolation logic. It projects them into an execution-time
partition map and re-affirms, deterministically, that every recorded dependency
edge stays within its partition or is federated. It is a *structure only*.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.execution.errors import ExecutionIsolationError

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.composition import RuntimeComposition

_logger = get_logger("runtime.execution.isolation")

#: The recorded isolation format.
ISOLATION_FORMAT = "ucos-execution-isolation/1.0.0"


@dataclass(frozen=True, slots=True)
class IsolationPartition:
    """One execution-time isolation partition (a bounding context's members)."""

    context_id: str
    members: tuple[str, ...]

    def contains(self, universe_id: str) -> bool:
        return universe_id in self.members

    def to_dict(self) -> dict[str, Any]:
        return {"context_id": self.context_id, "members": list(self.members)}


@dataclass(frozen=True, slots=True)
class IsolationView:
    """The full, deterministic isolation view of a composition's execution."""

    composition_id: str
    partitions: tuple[IsolationPartition, ...]

    def partition_of(self, universe_id: str) -> IsolationPartition:
        """Return the partition bounding ``universe_id`` (raises if unbounded)."""
        for partition in self.partitions:
            if partition.contains(universe_id):
                return partition
        raise ExecutionIsolationError(
            "universe is not bounded by any isolation partition",
            universe_id=universe_id,
        )

    def context_of(self, universe_id: str) -> str:
        """The bounding context id of ``universe_id``."""
        return self.partition_of(universe_id).context_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "isolation_format": ISOLATION_FORMAT,
            "composition_id": self.composition_id,
            "partition_count": len(self.partitions),
            "partitions": [p.to_dict() for p in self.partitions],
        }


def isolate(composition: RuntimeComposition) -> IsolationView:
    """Project the composition's resolved contexts into an execution isolation view.

    Reuses :attr:`RuntimeComposition.contexts` verbatim and re-affirms that every
    recorded dependency edge is either intra-partition or authorised by a federated
    reference frame (ORL-13). Fails closed on any residual isolation leak.

    Raises:
        ExecutionIsolationError: if a dependency crosses a partition boundary and no
            reference frame authorises it (a defensive re-check of ORL-13).
    """
    with trace("runtime.execution.isolate", composition=composition.composition_id):
        partitions = tuple(
            IsolationPartition(context_id=ctx.context_id, members=ctx.members)
            for ctx in composition.contexts
        )
        view = IsolationView(composition_id=composition.composition_id, partitions=partitions)
        frames = {frame.universe_id: frame for frame in composition.reference_frames}
        for universe in composition.universes:
            context_id = view.context_of(universe.universe_id)
            for dependency in universe.depends_on:
                if view.context_of(dependency) == context_id:
                    continue
                frame = frames.get(universe.universe_id)
                if frame is None or not frame.can_reference(dependency):
                    raise ExecutionIsolationError(
                        "execution dependency crosses an isolation boundary without "
                        "an authorising reference frame",
                        universe_id=universe.universe_id,
                        dependency=dependency,
                        context=context_id,
                    )
    _logger.info(
        "runtime.execution.isolated",
        composition_id=composition.composition_id,
        partitions=len(partitions),
    )
    return view


__all__ = [
    "ISOLATION_FORMAT",
    "IsolationPartition",
    "IsolationView",
    "isolate",
]
