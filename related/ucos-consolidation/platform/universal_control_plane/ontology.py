"""UCOS-CTRL-000001 — Universal Control Plane domain model.

Every concept the Control Plane governs is an immutable value object here.
Identity is derived from content (content-addressed); no wall-clock appears in
any identifier — callers supply a logical ``tick`` (monotonic integer).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Identity helpers
# ---------------------------------------------------------------------------


def _digest(payload: Mapping[str, Any]) -> str:
    """SHA-256 of the canonical JSON of *payload*, truncated to 16 hex chars."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _id(namespace: str, natural_key: str, tick: int) -> str:
    return _digest({"ns": namespace, "key": natural_key, "tick": tick})


# ---------------------------------------------------------------------------
# Lifecycle state tokens — open; projects extend via StateEngine.
# ---------------------------------------------------------------------------

LIFECYCLE_DRAFT = "DRAFT"
LIFECYCLE_ACTIVE = "ACTIVE"
LIFECYCLE_PAUSED = "PAUSED"
LIFECYCLE_COMPLETE = "COMPLETE"
LIFECYCLE_CANCELLED = "CANCELLED"
LIFECYCLE_ARCHIVED = "ARCHIVED"

DEFAULT_LIFECYCLE: tuple[str, ...] = (
    LIFECYCLE_DRAFT,
    LIFECYCLE_ACTIVE,
    LIFECYCLE_PAUSED,
    LIFECYCLE_COMPLETE,
    LIFECYCLE_CANCELLED,
    LIFECYCLE_ARCHIVED,
)

# Priority tokens
PRIORITY_CRITICAL = "CRITICAL"
PRIORITY_HIGH = "HIGH"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_LOW = "LOW"


# ---------------------------------------------------------------------------
# Registry objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Universe:
    """A registered sovereign universe in the Control Plane."""

    universe_id: str
    name: str
    description: str = ""
    state: str = LIFECYCLE_ACTIVE
    version: str = "1.0.0"
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.universe", self.universe_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Universe",
            "identity": self.identity,
            "universe_id": self.universe_id,
            "name": self.name,
            "description": self.description,
            "state": self.state,
            "version": self.version,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class Capability:
    """A registered capability owned by a universe."""

    capability_id: str
    universe_id: str
    name: str
    description: str = ""
    state: str = LIFECYCLE_ACTIVE
    version: str = "1.0.0"
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.capability", self.capability_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Capability",
            "identity": self.identity,
            "capability_id": self.capability_id,
            "universe_id": self.universe_id,
            "name": self.name,
            "description": self.description,
            "state": self.state,
            "version": self.version,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class OwnershipRecord:
    """A declared ownership binding: one owner holds one capability."""

    ownership_id: str
    capability_id: str
    owner_id: str
    owner_kind: str  # "Universe" | "Agent" | open token
    rationale: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.ownership", self.ownership_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "OwnershipRecord",
            "identity": self.identity,
            "ownership_id": self.ownership_id,
            "capability_id": self.capability_id,
            "owner_id": self.owner_id,
            "owner_kind": self.owner_kind,
            "rationale": self.rationale,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class DependencyRecord:
    """A registered dependency edge: *from_id* depends on *to_id*."""

    dependency_id: str
    from_id: str
    to_id: str
    kind: str = "REQUIRES"  # REQUIRES | EXTENDS | CONSUMES | open token
    optional: bool = False
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.dependency", self.dependency_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "DependencyRecord",
            "identity": self.identity,
            "dependency_id": self.dependency_id,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "dependency_kind": self.kind,
            "optional": self.optional,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class AgentRecord:
    """A registered execution agent."""

    agent_id: str
    name: str
    kind: str = "AUTONOMOUS"  # AUTONOMOUS | HUMAN | HYBRID | open token
    capabilities: tuple[str, ...] = ()
    state: str = LIFECYCLE_ACTIVE
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.agent", self.agent_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "AgentRecord",
            "identity": self.identity,
            "agent_id": self.agent_id,
            "name": self.name,
            "agent_kind": self.kind,
            "capabilities": list(self.capabilities),
            "state": self.state,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


# ---------------------------------------------------------------------------
# Planning hierarchy
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Vision:
    """The long-term directional declaration for a universe."""

    vision_id: str
    universe_id: str
    statement: str
    state: str = LIFECYCLE_ACTIVE
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.vision", self.vision_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Vision",
            "identity": self.identity,
            "vision_id": self.vision_id,
            "universe_id": self.universe_id,
            "statement": self.statement,
            "state": self.state,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class Goal:
    """A strategic goal tied to a vision."""

    goal_id: str
    vision_id: str
    title: str
    description: str = ""
    priority: str = PRIORITY_MEDIUM
    state: str = LIFECYCLE_DRAFT
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.goal", self.goal_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Goal",
            "identity": self.identity,
            "goal_id": self.goal_id,
            "vision_id": self.vision_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "state": self.state,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class Objective:
    """A measurable, verifiable target tied to a goal."""

    objective_id: str
    goal_id: str
    title: str
    success_criteria: str
    description: str = ""
    priority: str = PRIORITY_MEDIUM
    state: str = LIFECYCLE_DRAFT
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.objective", self.objective_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Objective",
            "identity": self.identity,
            "objective_id": self.objective_id,
            "goal_id": self.goal_id,
            "title": self.title,
            "success_criteria": self.success_criteria,
            "description": self.description,
            "priority": self.priority,
            "state": self.state,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class Milestone:
    """A verifiable checkpoint with a logical sequence position."""

    milestone_id: str
    universe_id: str
    title: str
    description: str = ""
    sequence: int = 0
    objective_ids: tuple[str, ...] = ()
    state: str = LIFECYCLE_DRAFT
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.milestone", self.milestone_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Milestone",
            "identity": self.identity,
            "milestone_id": self.milestone_id,
            "universe_id": self.universe_id,
            "title": self.title,
            "description": self.description,
            "sequence": self.sequence,
            "objective_ids": list(self.objective_ids),
            "state": self.state,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


# ---------------------------------------------------------------------------
# Execution layer
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BacklogItem:
    """A unit of planned work in the universal backlog."""

    item_id: str
    universe_id: str
    title: str
    description: str = ""
    priority: str = PRIORITY_MEDIUM
    milestone_id: str = ""
    objective_id: str = ""
    state: str = LIFECYCLE_DRAFT
    estimate: int = 0  # logical effort units; meaning is open
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.backlog", self.item_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "BacklogItem",
            "identity": self.identity,
            "item_id": self.item_id,
            "universe_id": self.universe_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "milestone_id": self.milestone_id,
            "objective_id": self.objective_id,
            "state": self.state,
            "estimate": self.estimate,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class Assignment:
    """A binding of a backlog item to an agent."""

    assignment_id: str
    item_id: str
    agent_id: str
    rationale: str = ""
    state: str = LIFECYCLE_ACTIVE
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.assignment", self.assignment_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Assignment",
            "identity": self.identity,
            "assignment_id": self.assignment_id,
            "item_id": self.item_id,
            "agent_id": self.agent_id,
            "rationale": self.rationale,
            "state": self.state,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class ScheduleEntry:
    """A scheduler-produced directive: item at logical position in a wave."""

    entry_id: str
    item_id: str
    agent_id: str
    position: int
    wave: int = 0
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.schedule_entry", self.entry_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "ScheduleEntry",
            "identity": self.identity,
            "entry_id": self.entry_id,
            "item_id": self.item_id,
            "agent_id": self.agent_id,
            "position": self.position,
            "wave": self.wave,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


# ---------------------------------------------------------------------------
# Intelligence and traceability objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Prompt:
    """A generated agent prompt with full context."""

    prompt_id: str
    item_id: str
    agent_id: str
    universe_id: str
    text: str
    context_digest: str = ""
    template_id: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.prompt", self.prompt_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Prompt",
            "identity": self.identity,
            "prompt_id": self.prompt_id,
            "item_id": self.item_id,
            "agent_id": self.agent_id,
            "universe_id": self.universe_id,
            "text": self.text,
            "context_digest": self.context_digest,
            "template_id": self.template_id,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class Metric:
    """A single measured value at a logical point in time."""

    metric_id: str
    subject_id: str
    name: str
    value: float
    unit: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.metric", self.metric_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Metric",
            "identity": self.identity,
            "metric_id": self.metric_id,
            "subject_id": self.subject_id,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class ProgressRecord:
    """A measured progress snapshot for a subject."""

    record_id: str
    subject_id: str
    total: int
    completed: int
    state: str = LIFECYCLE_ACTIVE
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.progress", self.record_id, self.tick)

    @property
    def percentage(self) -> float:
        return (self.completed / self.total * 100.0) if self.total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "ProgressRecord",
            "identity": self.identity,
            "record_id": self.record_id,
            "subject_id": self.subject_id,
            "total": self.total,
            "completed": self.completed,
            "percentage": round(self.percentage, 2),
            "state": self.state,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class Determination:
    """A recorded determination: what was measured, what was decided."""

    determination_id: str
    subject_id: str
    verdict: str  # AUTHORIZED | BLOCKED | DEFERRED | open token
    rationale: str
    evidence_ids: tuple[str, ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.determination", self.determination_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Determination",
            "identity": self.identity,
            "determination_id": self.determination_id,
            "subject_id": self.subject_id,
            "verdict": self.verdict,
            "rationale": self.rationale,
            "evidence_ids": list(self.evidence_ids),
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class Decision:
    """A recorded decision with rationale and alternatives considered."""

    decision_id: str
    subject_id: str
    title: str
    choice: str
    rationale: str
    alternatives: tuple[str, ...] = ()
    determination_id: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.decision", self.decision_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Decision",
            "identity": self.identity,
            "decision_id": self.decision_id,
            "subject_id": self.subject_id,
            "title": self.title,
            "choice": self.choice,
            "rationale": self.rationale,
            "alternatives": list(self.alternatives),
            "determination_id": self.determination_id,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class Evidence:
    """A content-addressed evidence record."""

    evidence_id: str
    subject_id: str
    kind: str  # MEASUREMENT | TEST | AUDIT | REVIEW | open token
    claim: str
    payload_digest: str
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.evidence", self.evidence_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Evidence",
            "identity": self.identity,
            "evidence_id": self.evidence_id,
            "subject_id": self.subject_id,
            "evidence_kind": self.kind,
            "claim": self.claim,
            "payload_digest": self.payload_digest,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class HistoryEntry:
    """An append-only entry in the control-plane history log."""

    entry_id: str
    subject_id: str
    event: str  # STATE_CHANGED | ASSIGNED | DETERMINED | open token
    detail: str = ""
    actor_id: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.history", self.entry_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "HistoryEntry",
            "identity": self.identity,
            "entry_id": self.entry_id,
            "subject_id": self.subject_id,
            "event": self.event,
            "detail": self.detail,
            "actor_id": self.actor_id,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class ReplayRecord:
    """A replayable execution record binding inputs to outputs."""

    replay_id: str
    subject_id: str
    inputs_digest: str
    outputs_digest: str
    history_ids: tuple[str, ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.replay", self.replay_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "ReplayRecord",
            "identity": self.identity,
            "replay_id": self.replay_id,
            "subject_id": self.subject_id,
            "inputs_digest": self.inputs_digest,
            "outputs_digest": self.outputs_digest,
            "history_ids": list(self.history_ids),
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


# ---------------------------------------------------------------------------
# Repository Truth objects
#
# Everything below is *discovered*, never authored: each object is a projection
# of what the repository already records, carried into the control plane's own
# vocabulary so a single object type can be governed, certified, versioned and
# replayed regardless of which subsystem produced it.
# ---------------------------------------------------------------------------

#: Truth classes a discovered artifact may occupy (mirrors the URTF vocabulary,
#: which remains the authority — these tokens are open, not an enumeration).
TRUTH_CANONICAL = "canonical"
TRUTH_UNCLASSIFIED = "unclassified"


@dataclass(frozen=True)
class ArtifactRecord:
    """A registered repository artifact, as the control plane sees it."""

    artifact_id: str
    name: str
    category: str
    status: str
    version: str
    owner: str
    locator: str
    truth_class: str = TRUTH_UNCLASSIFIED
    canonical_home_eligible: bool = False
    content_digest: str = ""
    program: str = ""
    volume: str = ""
    dependencies: tuple[str, ...] = ()
    classes: tuple[str, ...] = ()
    traceability: tuple[str, ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.artifact", self.artifact_id, self.tick)

    def in_class(self, class_id: str) -> bool:
        return class_id in self.classes

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "ArtifactRecord",
            "identity": self.identity,
            "artifact_id": self.artifact_id,
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "version": self.version,
            "owner": self.owner,
            "locator": self.locator,
            "truth_class": self.truth_class,
            "canonical_home_eligible": self.canonical_home_eligible,
            "content_digest": self.content_digest,
            "program": self.program,
            "volume": self.volume,
            "dependencies": list(self.dependencies),
            "classes": list(self.classes),
            "traceability": list(self.traceability),
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


# ---------------------------------------------------------------------------
# Governance objects
# ---------------------------------------------------------------------------

GOVERNANCE_GOVERNED = "GOVERNED"
GOVERNANCE_NOT_GOVERNED = "NOT-GOVERNED"
GOVERNANCE_UNGOVERNED = "UNGOVERNED"

SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_HIGH = "HIGH"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_LOW = "LOW"

#: Severities that, when violated, deny governance. Anything below is recorded
#: and reported but does not by itself withhold the verdict.
BLOCKING_SEVERITIES: tuple[str, ...] = (SEVERITY_CRITICAL, SEVERITY_HIGH)


@dataclass(frozen=True)
class GovernanceViolation:
    """A declared governance rule a subject failed."""

    violation_id: str
    subject_id: str
    rule_id: str
    severity: str
    message: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.violation", self.violation_id, self.tick)

    @property
    def blocking(self) -> bool:
        return self.severity in BLOCKING_SEVERITIES

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "GovernanceViolation",
            "identity": self.identity,
            "violation_id": self.violation_id,
            "subject_id": self.subject_id,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "blocking": self.blocking,
            "message": self.message,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class GovernanceRecord:
    """The resolved governance state of exactly one control-plane object."""

    record_id: str
    subject_id: str
    status: str
    lifecycle_state: str = LIFECYCLE_DRAFT
    satisfied_rules: tuple[str, ...] = ()
    violation_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    determination_id: str = ""
    rationale: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.governance", self.record_id, self.tick)

    @property
    def governed(self) -> bool:
        return self.status == GOVERNANCE_GOVERNED

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "GovernanceRecord",
            "identity": self.identity,
            "record_id": self.record_id,
            "subject_id": self.subject_id,
            "status": self.status,
            "governed": self.governed,
            "lifecycle_state": self.lifecycle_state,
            "satisfied_rules": list(self.satisfied_rules),
            "violation_ids": list(self.violation_ids),
            "evidence_ids": list(self.evidence_ids),
            "determination_id": self.determination_id,
            "rationale": self.rationale,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


# ---------------------------------------------------------------------------
# Certification objects
# ---------------------------------------------------------------------------

CERTIFICATION_CERTIFIED = "CERTIFIED"
CERTIFICATION_NOT_CERTIFIED = "NOT-CERTIFIED"
CERTIFICATION_UNCERTIFIED = "UNCERTIFIED"

CRITERION_BLOCKING = "BLOCKING"
CRITERION_ADVISORY = "ADVISORY"


@dataclass(frozen=True)
class CriterionOutcome:
    """One certification criterion evaluated against one subject."""

    criterion_id: str
    severity: str
    passed: bool
    message: str = ""

    @property
    def blocking_failure(self) -> bool:
        return not self.passed and self.severity == CRITERION_BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "severity": self.severity,
            "passed": self.passed,
            "blocking_failure": self.blocking_failure,
            "message": self.message,
        }


@dataclass(frozen=True)
class CertificationState:
    """The resolved certification state of exactly one control-plane object."""

    state_id: str
    subject_id: str
    status: str
    eligible: bool = False
    version: str = ""
    criteria: tuple[CriterionOutcome, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()
    rationale: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        """Content-addressed over the assessment *and* the history behind it.

        Including the lineage is what makes reassessment a chain rather than a
        list of identical links: re-affirming a seal after a prior one is a
        distinguishable event, and a lineage of repeated identities could not
        record that. ``evidence_ids`` is excluded — it points at the record of
        this state, so admitting it would make the identity depend on itself.
        """
        return _digest(
            {
                "ns": "ctrl.certification",
                "state_id": self.state_id,
                "subject_id": self.subject_id,
                "status": self.status,
                "eligible": self.eligible,
                "version": self.version,
                "criteria": [c.to_dict() for c in self.criteria],
                "lineage": list(self.lineage),
                "tick": self.tick,
            }
        )

    @property
    def certified(self) -> bool:
        return self.status == CERTIFICATION_CERTIFIED

    @property
    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(c.criterion_id for c in self.criteria if c.blocking_failure)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "CertificationState",
            "identity": self.identity,
            "state_id": self.state_id,
            "subject_id": self.subject_id,
            "status": self.status,
            "certified": self.certified,
            "eligible": self.eligible,
            "version": self.version,
            "criteria": [c.to_dict() for c in self.criteria],
            "blocking_failures": list(self.blocking_failures),
            "evidence_ids": list(self.evidence_ids),
            "lineage": list(self.lineage),
            "rationale": self.rationale,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


# ---------------------------------------------------------------------------
# Version objects
# ---------------------------------------------------------------------------

VERSION_SEMANTIC = "semantic"
VERSION_CONSTITUTIONAL = "constitutional"
VERSION_ARTIFACT = "artifact"
VERSION_CAPABILITY = "capability"
VERSION_IMPLEMENTATION = "implementation"
VERSION_GOVERNANCE = "governance"
VERSION_CERTIFICATION = "certification"

VERSION_KINDS: tuple[str, ...] = (
    VERSION_SEMANTIC,
    VERSION_CONSTITUTIONAL,
    VERSION_ARTIFACT,
    VERSION_CAPABILITY,
    VERSION_IMPLEMENTATION,
    VERSION_GOVERNANCE,
    VERSION_CERTIFICATION,
)


@dataclass(frozen=True)
class VersionRecord:
    """One immutable, content-addressed version of one subject in one dimension.

    A version is not a string the object carries; it is a record with a parent, a
    content digest and a revision, which is what makes lineage, promotion and
    rollback executable rather than descriptive.
    """

    subject_id: str
    kind: str
    version: str
    revision: int = 1
    content_digest: str = ""
    parent_version_id: str = ""
    superseded_by: str = ""
    rationale: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def version_id(self) -> str:
        """Content-addressed identity: identical content in the same lineage slot
        yields an identical id, which is what makes replay verifiable."""
        return _digest(
            {
                "ns": "ctrl.version",
                "subject": self.subject_id,
                "kind": self.kind,
                "version": self.version,
                "revision": self.revision,
                "content_digest": self.content_digest,
                "parent": self.parent_version_id,
            }
        )

    @property
    def identity(self) -> str:
        return self.version_id

    @property
    def is_root(self) -> bool:
        return not self.parent_version_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "VersionRecord",
            "identity": self.identity,
            "version_id": self.version_id,
            "subject_id": self.subject_id,
            "version_kind": self.kind,
            "version": self.version,
            "revision": self.revision,
            "content_digest": self.content_digest,
            "parent_version_id": self.parent_version_id,
            "superseded_by": self.superseded_by,
            "is_root": self.is_root,
            "rationale": self.rationale,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


# ---------------------------------------------------------------------------
# Evolution objects
# ---------------------------------------------------------------------------

CHANGE_CREATED = "CREATED"
CHANGE_MODIFIED = "MODIFIED"
CHANGE_PROMOTED = "PROMOTED"
CHANGE_REGRESSED = "REGRESSED"
CHANGE_IMPROVED = "IMPROVED"
CHANGE_REMOVED = "REMOVED"
CHANGE_UNCHANGED = "UNCHANGED"

DIMENSION_CAPABILITY = "CAPABILITY"
DIMENSION_ARCHITECTURE = "ARCHITECTURE"
DIMENSION_GOVERNANCE = "GOVERNANCE"
DIMENSION_CERTIFICATION = "CERTIFICATION"
DIMENSION_VERSION = "VERSION"


@dataclass(frozen=True)
class ChangeRecord:
    """One measured delta between two observations of the same subject."""

    change_id: str
    subject_id: str
    kind: str
    dimension: str = DIMENSION_VERSION
    sequence: int = 0
    from_value: str = ""
    to_value: str = ""
    delta_digest: str = ""
    rationale: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.change", self.change_id, self.tick)

    @property
    def is_regression(self) -> bool:
        return self.kind == CHANGE_REGRESSED

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "ChangeRecord",
            "identity": self.identity,
            "change_id": self.change_id,
            "subject_id": self.subject_id,
            "change_kind": self.kind,
            "dimension": self.dimension,
            "sequence": self.sequence,
            "from_value": self.from_value,
            "to_value": self.to_value,
            "delta_digest": self.delta_digest,
            "is_regression": self.is_regression,
            "rationale": self.rationale,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


# ---------------------------------------------------------------------------
# Registration and constitutional linkage
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegistrationRecord:
    """The registration of one control-plane object into the control plane itself."""

    registration_id: str
    subject_id: str
    subject_kind: str
    name: str
    module: str
    layer: str
    universe_id: str
    owner_id: str
    capability_id: str = ""
    lineage: tuple[str, ...] = ()
    description: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.registration", self.registration_id, self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "RegistrationRecord",
            "identity": self.identity,
            "registration_id": self.registration_id,
            "subject_id": self.subject_id,
            "subject_kind": self.subject_kind,
            "name": self.name,
            "module": self.module,
            "layer": self.layer,
            "universe_id": self.universe_id,
            "owner_id": self.owner_id,
            "capability_id": self.capability_id,
            "lineage": list(self.lineage),
            "description": self.description,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class LinkageRecord:
    """Which constitutional linkages one subject closes, and which it leaves open."""

    linkage_id: str
    subject_id: str
    links: Mapping[str, str] = field(default_factory=dict)
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def identity(self) -> str:
        return _id("ctrl.linkage", self.linkage_id, self.tick)

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(sorted(name for name, target in self.links.items() if not target))

    @property
    def complete(self) -> bool:
        return bool(self.links) and not self.missing

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "LinkageRecord",
            "identity": self.identity,
            "linkage_id": self.linkage_id,
            "subject_id": self.subject_id,
            "links": dict(sorted(self.links.items())),
            "missing": list(self.missing),
            "complete": self.complete,
            "tick": self.tick,
            "attributes": dict(self.attributes),
        }


# ---------------------------------------------------------------------------
# Durable replay
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JournalEntry:
    """One hash-chained entry in the durable control-plane journal.

    The chain is what makes replay *durable* rather than process-local: each entry
    binds the digest of its own payload to the digest of the entry before it, so a
    journal read back after a restart either reconstructs the identical state or
    fails closed at the first tampered link.
    """

    sequence: int
    subject_id: str
    event: str
    payload_digest: str
    previous_hash: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def entry_hash(self) -> str:
        """This entry's link in the chain — a function of the entry and its parent."""
        return _digest(
            {
                "sequence": self.sequence,
                "subject_id": self.subject_id,
                "event": self.event,
                "payload_digest": self.payload_digest,
                "previous_hash": self.previous_hash,
                "tick": self.tick,
            }
        )

    @property
    def identity(self) -> str:
        return self.entry_hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "JournalEntry",
            "sequence": self.sequence,
            "subject_id": self.subject_id,
            "event": self.event,
            "payload_digest": self.payload_digest,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
            "tick": self.tick,
            "payload": dict(self.payload),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> JournalEntry:
        """Rebuild an entry from its serialised form (the read side of replay)."""
        return cls(
            sequence=int(raw["sequence"]),
            subject_id=str(raw["subject_id"]),
            event=str(raw["event"]),
            payload_digest=str(raw["payload_digest"]),
            previous_hash=str(raw["previous_hash"]),
            payload=dict(raw.get("payload", {})),
            tick=int(raw.get("tick", 0)),
        )


def payload_digest(payload: Any) -> str:
    """The canonical digest of a journal or evidence payload."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode()).hexdigest()
