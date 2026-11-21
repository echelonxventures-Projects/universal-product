"""UCOS-CTRL-PLAN-000001 — Master Plan Engine (Wave 12).

The canonical executable master plan of the control plane: one immutable, content-addressed,
replayable projection of everything the project is planning, derived entirely from Repository
Truth by way of the authoritative Project State snapshot.

It is a **deterministic projection and a consumer**, not a new authority:

    * Repository Truth is discovered by the control plane's ``RepositoryTruthEngine``;
    * the entity population is Wave 11's ``ProjectStateEngine`` snapshot, taken as
      authoritative — no entity is re-derived here;
    * membership is the ontology's own planning vocabulary (``PLAN_KINDS``): vision, goal,
      objective, milestone, backlog item, assignment and progress record. The registration,
      governance, certification, version, ownership, dependency and capability records in the
      same snapshot belong to other authorities and are not projected;
    * persistence and replay run through the control plane's ``DurableJournal``;
    * ownership, lifecycle, governance and certification arrive already determined on the
      entity, and this wave determines none of them.

What is genuinely new is that planning state becomes an *executable plan*: nodes normalized
into one shape, edges resolved from the identifiers those entities already publish, a
deterministic execution ordering, a containment lineage, and a content identity for the whole.
A relationship the state does not support is left absent and counted — never inferred, never
fabricated.

Deterministic and clock-free: identity is a content digest, ordering is explicit and the
logical ``tick`` comes from the snapshot. Python standard library only.
"""

from __future__ import annotations

from platform.universal_master_plan.master_plan import (
    EDGE_CONTAINS,
    EDGE_REQUIRES,
    ESTIMATE_KEY,
    IDS_SUFFIX,
    MAX_LINEAGE_DEPTH,
    PLAN_KINDS,
    PRIORITY_KEY,
    SEQUENCE_KEY,
    TITLE_KEYS,
    MasterPlan,
    MasterPlanError,
    PlanDelta,
    PlanEdge,
    PlanNode,
    compose_edges,
    compose_plan,
    is_plan_entity,
    plan_dependencies,
    plan_kinds,
    plan_references,
)
from platform.universal_master_plan.master_plan_registry import MasterPlanRegistry
from platform.universal_master_plan.master_plan_replay import (
    EVENT_PLAN_COMPOSED,
    PAYLOAD_NODES,
    PAYLOAD_SNAPSHOT,
    PAYLOAD_TICK,
    PAYLOAD_TRUTH,
    PAYLOAD_UNIVERSE,
    plan_entries,
    plan_from_payload,
    plan_payload,
    reconstruct,
    reconstruct_all,
    reconstruct_at,
    record_plan,
    replays,
)
from platform.universal_master_plan.master_plan_runtime import MasterPlanEngine

__version__ = "1.0.0"

__all__ = [
    # -- declared keys, edge kinds and event tokens --
    "EDGE_CONTAINS",
    "EDGE_REQUIRES",
    "ESTIMATE_KEY",
    "EVENT_PLAN_COMPOSED",
    "IDS_SUFFIX",
    "MAX_LINEAGE_DEPTH",
    "PAYLOAD_NODES",
    "PAYLOAD_SNAPSHOT",
    "PAYLOAD_TICK",
    "PAYLOAD_TRUTH",
    "PAYLOAD_UNIVERSE",
    "PLAN_KINDS",
    "PRIORITY_KEY",
    "SEQUENCE_KEY",
    "TITLE_KEYS",
    # -- errors --
    "MasterPlanError",
    # -- the plan model --
    "MasterPlan",
    "PlanDelta",
    "PlanEdge",
    "PlanNode",
    # -- the canonical registry and the runtime --
    "MasterPlanEngine",
    "MasterPlanRegistry",
    # -- composition, replay and helpers --
    "compose_edges",
    "compose_plan",
    "is_plan_entity",
    "plan_dependencies",
    "plan_entries",
    "plan_from_payload",
    "plan_kinds",
    "plan_payload",
    "plan_references",
    "reconstruct",
    "reconstruct_all",
    "reconstruct_at",
    "record_plan",
    "replays",
]
