"""UVI-000001 Part 01 — the shapes verification intelligence reasons over.

Nothing here decides anything. These are the value objects the constitution, the
selector, the evidence registry and the scheduler exchange, kept in one module so a
type can be read without reading the engine that produces it.

Every dataclass is frozen. A plan that can be mutated after it is computed is a plan
whose digest stops meaning anything, and ``UVI-L-10`` measures that planning twice over
one repository state produces byte-identical output.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


class VerificationIntelligenceError(Exception):
    """The verification intelligence substrate is unusable, so no plan can be produced.

    Raised rather than degraded, for the reason ``engine.verification_impact`` states
    for its own fault type: a selector that quietly returns "nothing to verify" is the
    single most dangerous thing a verification selector can do. Every caller treats
    this as FAULT and falls back to the whole suite.
    """


class Selection(str, enum.Enum):
    """How much of the suite a mode runs."""

    IMPACT = "IMPACT"
    WHOLE_SUITE = "WHOLE_SUITE"


class Coverage(str, enum.Enum):
    """Whether a mode evaluates the coverage floor."""

    NOT_EVALUATED = "NOT_EVALUATED"
    FLOOR_90 = "FLOOR_90"


class Action(str, enum.Enum):
    """What the plan says to do with one declared stage.

    ``RUN`` is the default for anything the plan cannot classify, which is why the
    shell helper that reads the plan also defaults to ``RUN``: an unrecognised stage
    must execute, never be skipped.
    """

    RUN = "RUN"
    SKIP = "SKIP"
    REUSE = "REUSE"


@dataclass(frozen=True, slots=True)
class Mode:
    """One declared verification mode — a claim plus the obligations it requires."""

    mode_id: str
    flag: str
    purpose: str
    claim: str
    claims_not: tuple[str, ...]
    selection: Selection
    coverage: Coverage
    certification_eligible: bool
    evidence_reuse: bool
    parallel: bool
    stages: str | tuple[str, ...]
    budget_seconds: int

    @property
    def is_contract(self) -> bool:
        """True when the mode runs the whole declared contract rather than a subset."""
        return isinstance(self.stages, str)


@dataclass(frozen=True, slots=True)
class StageSpec:
    """One declared stage of ``./verify.sh``, classified.

    ``label`` is authoritative and is the join key: it is the literal
    ``run_stage "…"`` argument in the script, the string
    ``00-MASTER/UAKOS-CLOSURE-008/validation-record.json`` digests, and the string the
    shell looks the plan up by. ``UVI-L-03`` measures that this set and the script's
    set are equal and identically ordered.
    """

    stage_id: str
    label: str
    phase: str
    plane: str
    depends_on: tuple[str, ...]
    modes: tuple[str, ...]
    reusable: bool
    #: COMPATIBILITY. The field that used to carry both meanings. Retained so a
    #: declaration written before the separation still resolves; ``read_set`` is what
    #: everything reads now, and falls back to this when a stage declares no read-set.
    reuse_inputs: tuple[str, ...]
    owner: str
    shardable: bool = False
    #: WHAT THIS STAGE READS — a dependency relation, declared independently of whether
    #: the stage may be answered from cache. ``reuse_inputs`` carried both meanings, so a
    #: stage that must always run declared no inputs and was invisible to impact analysis
    #: even though its read-set was perfectly well known. ``("**",)`` is the declared
    #: whole-boundary token, for a stage whose subject genuinely is the tree.
    read_set: tuple[str, ...] = ()

    @property
    def reads(self) -> tuple[str, ...]:
        """The effective read-set: the declared one, or ``reuse_inputs`` in compatibility."""
        return self.read_set or self.reuse_inputs


@dataclass(frozen=True, slots=True)
class TestObject:
    """One collectible test file, as the Test Object Registry projects it."""

    path: str
    universal_id: str
    owner: str
    capability: str
    content_hash: str | None
    cost_seconds: float
    registered: bool = True
    """Whether the executable object registry holds this object.

    False means pytest collects the file and the registry has never heard of it — a NEW
    test file that has not yet been through registration. It is admitted anyway, because
    the alternative is what this flag exists to end: an unregistered test object used to
    be invisible to the selector, so it ran in a serial suite and was silently absent from
    every shard of a sharded one. A test that disappears when the run is parallelised is
    the worst failure a verification selector can have, because its symptom is a faster
    green run.
    """

    @property
    def is_priced(self) -> bool:
        """True when a measured cost backs this object rather than the default price."""
        return self.cost_seconds > 0


@dataclass(frozen=True, slots=True)
class SelectionResult:
    """What the layered selector decided, and why."""

    selection: Selection
    test_paths: tuple[str, ...]
    changed: tuple[str, ...]
    affected_objects: tuple[str, ...]
    affected_owners: tuple[str, ...]
    affected_capabilities: tuple[str, ...]
    affected_evidence: tuple[str, ...]
    affected_certification: tuple[str, ...]
    escalations: tuple[str, ...]
    layers: tuple[tuple[str, int], ...]
    superseded: tuple[str, ...] = ()
    """Widenings a narrower engine would have made, that this one answered precisely.

    Carried rather than discarded. :mod:`engine.verification_impact` widens on two
    computed heuristics that a five-substrate selector supersedes, and dropping them
    silently would hide the fact that a decision was overridden at all.
    """

    @property
    def escalated(self) -> bool:
        return self.selection is Selection.WHOLE_SUITE

    def to_dict(self) -> dict[str, Any]:
        return {
            "selection": self.selection.value,
            "test_paths": list(self.test_paths),
            "changed": list(self.changed),
            "affected_objects": list(self.affected_objects),
            "affected_owners": list(self.affected_owners),
            "affected_capabilities": list(self.affected_capabilities),
            "affected_evidence": list(self.affected_evidence),
            "affected_certification": list(self.affected_certification),
            "escalations": list(self.escalations),
            "superseded": list(self.superseded),
            "layers": [{"layer": name, "reached": count} for name, count in self.layers],
            "counts": {
                "changed": len(self.changed),
                "affected_objects": len(self.affected_objects),
                "affected_owners": len(self.affected_owners),
                "affected_capabilities": len(self.affected_capabilities),
                "selected_tests": len(self.test_paths),
            },
        }


@dataclass(frozen=True, slots=True)
class Shard:
    """One deterministic partition of the selected test objects."""

    index: int
    test_paths: tuple[str, ...]
    cost_seconds: float
    deselect: tuple[str, ...] = ()
    """Nodes of a split file that this shard must NOT run because another shard has them.

    Exactly one shard holding part of a split file receives the FILE itself rather than a
    node list, and this is what keeps it from running the parts its neighbours took. That
    shard is the remainder: it runs its own nodes and anything the cost model does not
    know about, so a node the measurement never saw is executed rather than dropped. The
    first implementation gave every shard an explicit node list, and 54 tests too fast to
    appear in a --durations report were therefore in no shard at all — a suite that
    reported 11 706 of 11 760 tests and called it a pass.
    """
    wave: int = 0
    """Which execution wave this shard belongs to.

    Wave 0 is the ordinary concurrent body. A later wave runs only after every earlier
    wave has finished and, for isolated objects, contains exactly one shard — so an
    object measured to be unsafe beside anything else runs with nothing else running.
    The wave changes WHEN a unit runs and never WHETHER it runs.
    """

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "wave": self.wave,
            "deselect": list(self.deselect),
            "tests": len(self.test_paths),
            "cost_seconds": round(self.cost_seconds, 3),
            "test_paths": list(self.test_paths),
        }


@dataclass(frozen=True, slots=True)
class StagePlan:
    """The decision the plan reached about one declared stage."""

    stage: StageSpec
    action: Action
    reason: str
    input_digest: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage.stage_id,
            "label": self.stage.label,
            "phase": self.stage.phase,
            "plane": self.stage.plane,
            "action": self.action.value,
            "reason": self.reason,
            "input_digest": self.input_digest,
        }


@dataclass(frozen=True, slots=True)
class Plan:
    """A complete, deterministic verification plan.

    No wall clock reaches this object. Two plans computed over one repository state are
    byte-identical, which is what makes :attr:`digest` a usable identity and what
    ``UVI-L-10`` measures.
    """

    mode: Mode
    stages: tuple[StagePlan, ...]
    selection: SelectionResult
    shards: tuple[Shard, ...]
    coverage: Coverage
    workers: int
    escalated_coverage: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def selection_is_impact(self) -> bool:
        """Whether this plan's selection is derived from the diff rather than the suite.

        Cross-job sharding needs a selection every job computes identically. A whole-suite
        selection is such a thing. An impact selection is not: it is derived from the
        diff, and two runners need not see the same diff — a shallow fetch alone is enough
        to make them disagree. Each job would then prove its OWN plan whole while
        partitioning a different suite from its neighbours.
        """
        return self.mode.selection is not Selection.WHOLE_SUITE

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": "UVI-000001",
            "authority": "NONE — DERIVED TRUTH",
            "mode": {
                "id": self.mode.mode_id,
                "flag": self.mode.flag,
                "claim": self.mode.claim,
                "claims_not": list(self.mode.claims_not),
                "certification_eligible": self.mode.certification_eligible,
                "budget_seconds": self.mode.budget_seconds,
            },
            "coverage": self.coverage.value,
            "coverage_escalated": self.escalated_coverage,
            "workers": self.workers,
            "stages": [entry.to_dict() for entry in self.stages],
            "selection": self.selection.to_dict(),
            "shards": [shard.to_dict() for shard in self.shards],
            "notes": list(self.notes),
        }
