"""UCOS-CTRL-STATE-000001 — Universal Project State (Wave 11).

The constitutional source of truth for **project state**: the immutable, replayable,
governable record of what the project is — its plans, roadmaps, objectives, milestones, work
packages, assignments, dependencies, progress and execution — at one logical tick.

It is a **consumer of existing constitutional services**, not a new authority beside them:

    * the state vocabulary is the control-plane **ontology**, discovered by introspection;
    * the population is the composed **Universal Control Plane**, harvested from the public
      projection of every engine it declares — no plan content is re-derived here;
    * persistence and replay run through the control plane's **DurableJournal**;
    * adjudication runs through its **GovernanceEngine** over its declared rule set;
    * certification runs through its **CertificationEngine** over its declared criteria;
    * lifecycle advance runs through its **StateEngine**.

What is genuinely new is that project state becomes addressable and durable. Before this
wave the plane's plan, roadmap, backlog, assignment and progress objects existed only in the
memory of the process that composed them: nothing could hash them, journal them, replay them
at a past tick, or present them to governance as subjects. :class:`ProjectStateRegistry` is
the canonical registry for those entities — they are not forced into the capability,
ownership or dependency registries, which hold different populations.

Deterministic and clock-free: identity is a content digest, ordering is explicit and the
logical ``tick`` is supplied by the caller. Python standard library only.
"""

from __future__ import annotations

from platform.universal_project_state.state import (
    ID_SUFFIX,
    IDENTITY_KEY,
    KIND_KEY,
    LIFECYCLE_KEYS,
    OWNER_KEYS,
    ProjectStateError,
    ProjectStateSnapshot,
    StateDelta,
    StateEntity,
    discover_entity_kinds,
    entity_id_of,
)
from platform.universal_project_state.state_certification import (
    certification_subject,
    certification_subjects,
    snapshot_certification_subjects,
    version_index,
)
from platform.universal_project_state.state_governance import (
    EVIDENCE_KEYS,
    HOME_KEYS,
    VERSION_KEYS,
    attribute_text,
    governance_subject,
    governance_subjects,
    snapshot_subjects,
)
from platform.universal_project_state.state_registry import (
    DEPENDENCY_KEYS,
    ProjectStateRegistry,
)
from platform.universal_project_state.state_replay import (
    EVENT_STATE_PROJECTED,
    PAYLOAD_ENTITIES,
    PAYLOAD_TICK,
    PAYLOAD_TRUTH,
    PAYLOAD_UNIVERSE,
    reconstruct,
    reconstruct_all,
    reconstruct_at,
    record_snapshot,
    replays,
    snapshot_from_payload,
    snapshot_payload,
    state_entries,
)
from platform.universal_project_state.state_runtime import (
    MAX_PROJECTION_DEPTH,
    ProjectStateEngine,
    plane_projections,
)

__version__ = "1.0.0"

__all__ = [
    # -- declared keys and event tokens --
    "DEPENDENCY_KEYS",
    "EVENT_STATE_PROJECTED",
    "EVIDENCE_KEYS",
    "HOME_KEYS",
    "IDENTITY_KEY",
    "ID_SUFFIX",
    "KIND_KEY",
    "LIFECYCLE_KEYS",
    "MAX_PROJECTION_DEPTH",
    "OWNER_KEYS",
    "PAYLOAD_ENTITIES",
    "PAYLOAD_TICK",
    "PAYLOAD_TRUTH",
    "PAYLOAD_UNIVERSE",
    "VERSION_KEYS",
    # -- errors --
    "ProjectStateError",
    # -- the state model --
    "ProjectStateSnapshot",
    "StateDelta",
    "StateEntity",
    # -- the canonical registry and the runtime --
    "ProjectStateEngine",
    "ProjectStateRegistry",
    # -- adapters and helpers --
    "attribute_text",
    "certification_subject",
    "certification_subjects",
    "discover_entity_kinds",
    "entity_id_of",
    "governance_subject",
    "governance_subjects",
    "plane_projections",
    "reconstruct",
    "reconstruct_all",
    "reconstruct_at",
    "record_snapshot",
    "replays",
    "snapshot_certification_subjects",
    "snapshot_from_payload",
    "snapshot_payload",
    "snapshot_subjects",
    "state_entries",
    "version_index",
]
