"""UCOS-CTRL-PLAN-000001 — Master Plan replay adapter (Wave 12).

The master plan persists through the durable journal the control plane already owns:
:class:`~platform.universal_control_plane.durable.DurableJournal`, whose entries are
hash-chained, appended one fsync at a time and verifiable byte-for-byte.

No journal, no second chain and no parallel persistence format is introduced here. This
module contributes only the two functions the generic journal cannot supply — how a composed
plan becomes one entry and how an entry becomes that plan again — plus the event token such
entries are written under.

The round trip is exact *by construction*. A recorded entry carries each node's original
control-plane projection, exactly as project state journals its entities, and reconstruction
rebuilds every node through the same
:meth:`~platform.universal_project_state.state.StateEntity.from_projection` and
:meth:`~platform.universal_master_plan.master_plan.PlanNode.from_entity` that built it, then
re-resolves the edges through the same :func:`~platform.universal_master_plan.master_plan.
compose_edges`. Nothing normalized, linked or ordered is re-serialised alongside the payload,
so ``reconstruct(journal).plan_id == plan.plan_id`` is a proof that the projection replays and
not a comparison of two copies of one string.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from platform.universal_control_plane.durable import DurableJournal
from platform.universal_control_plane.errors import JournalError
from platform.universal_control_plane.ontology import JournalEntry
from platform.universal_master_plan.master_plan import (
    MasterPlan,
    MasterPlanError,
    PlanNode,
    compose_edges,
)
from platform.universal_project_state.state import StateEntity
from typing import Any

#: The event token under which a composed master plan is journalled.
EVENT_PLAN_COMPOSED = "PLAN_COMPOSED"

#: The payload keys one journalled plan carries.
PAYLOAD_UNIVERSE = "universe_id"
PAYLOAD_TRUTH = "truth_id"
PAYLOAD_SNAPSHOT = "snapshot_id"
PAYLOAD_TICK = "tick"
PAYLOAD_NODES = "nodes"


def plan_payload(plan: MasterPlan) -> dict[str, Any]:
    """The canonical journal payload for *plan* — the projections its nodes came from."""
    return {
        PAYLOAD_UNIVERSE: plan.universe_id,
        PAYLOAD_TRUTH: plan.truth_id,
        PAYLOAD_SNAPSHOT: plan.snapshot_id,
        PAYLOAD_TICK: plan.tick,
        PAYLOAD_NODES: [dict(node.attributes) for node in plan.nodes],
    }


def record_plan(journal: DurableJournal, plan: MasterPlan, *, tick: int = 0) -> JournalEntry:
    """Append *plan* to *journal* as one durable, chained entry."""
    return journal.append(plan.plan_id, EVENT_PLAN_COMPOSED, plan_payload(plan), tick=tick)


def plan_from_payload(payload: Mapping[str, Any]) -> MasterPlan:
    """Rebuild a master plan from one journalled payload (fail-closed)."""
    raw_nodes = payload.get(PAYLOAD_NODES)
    if not isinstance(raw_nodes, Sequence) or isinstance(raw_nodes, str | bytes):
        raise MasterPlanError("journalled plan payload carries no nodes array")
    tick = int(payload.get(PAYLOAD_TICK, 0) or 0)
    nodes: list[PlanNode] = []
    for raw in raw_nodes:
        if not isinstance(raw, Mapping):
            raise MasterPlanError("journalled plan node is not an object")
        nodes.append(PlanNode.from_entity(StateEntity.from_projection(raw, tick=tick)))
    ordered = tuple(nodes)
    return MasterPlan(
        universe_id=str(payload.get(PAYLOAD_UNIVERSE, "")),
        truth_id=str(payload.get(PAYLOAD_TRUTH, "")),
        snapshot_id=str(payload.get(PAYLOAD_SNAPSHOT, "")),
        nodes=ordered,
        edges=compose_edges(ordered),
        tick=tick,
    )


def plan_entries(journal: DurableJournal) -> tuple[JournalEntry, ...]:
    """Every master-plan entry in *journal*, in append order."""
    return tuple(entry for entry in journal.entries() if entry.event == EVENT_PLAN_COMPOSED)


def reconstruct(journal: DurableJournal) -> MasterPlan:
    """The latest master plan the journal holds (fail-closed when it holds none)."""
    entries = plan_entries(journal)
    if not entries:
        raise MasterPlanError(f"journal holds no {EVENT_PLAN_COMPOSED} entry to replay")
    return plan_from_payload(entries[-1].payload)


def reconstruct_all(journal: DurableJournal) -> tuple[MasterPlan, ...]:
    """Every plan the journal holds, oldest first — the plan's recorded lineage."""
    return tuple(plan_from_payload(entry.payload) for entry in plan_entries(journal))


def reconstruct_at(journal: DurableJournal, sequence: int) -> MasterPlan:
    """The plan recorded by the entry at *sequence* — historical reconstruction."""
    for entry in plan_entries(journal):
        if entry.sequence == sequence:
            return plan_from_payload(entry.payload)
    raise MasterPlanError(f"journal holds no {EVENT_PLAN_COMPOSED} entry at {sequence}")


def replays(journal: DurableJournal, plan: MasterPlan) -> bool:
    """Whether the journal replays *plan* exactly — chain intact and identity equal.

    :meth:`~platform.universal_control_plane.durable.DurableJournal.verify` returns ``True``
    or raises; it never returns ``False``. So it is called for its exception rather than
    guarded on its result, which is what keeps this predicate total without an unreachable
    branch pretending to handle a value that cannot occur.
    """
    try:
        journal.verify()
        return reconstruct(journal).plan_id == plan.plan_id
    except (JournalError, MasterPlanError):
        return False


__all__ = [
    "EVENT_PLAN_COMPOSED",
    "PAYLOAD_NODES",
    "PAYLOAD_SNAPSHOT",
    "PAYLOAD_TICK",
    "PAYLOAD_TRUTH",
    "PAYLOAD_UNIVERSE",
    "plan_entries",
    "plan_from_payload",
    "plan_payload",
    "reconstruct",
    "reconstruct_all",
    "reconstruct_at",
    "record_plan",
    "replays",
]
