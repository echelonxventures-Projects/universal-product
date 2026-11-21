"""EC3-B10-U06 — The Universal Lifecycle construct (DMC-07).

Realizes the meta-model construct **DMC-07 Lifecycle** (DATA-005 §2; DATA-011 §3):

    the **decidable, forward-only ordered progression** of a data construct through
    states, each transition recorded as a RUNTIME event *by reference* — the ontology
    root DOE-07, classified by DXH-07 (Definitional / Operative / Terminal). A lifecycle
    is an ENG-002 Object classified by an ENG-004 Type, ``transitions`` a datum/entity
    (DMR-06) and binds state/event/guard behavior *by reference* to the frozen RUNTIME
    concern (DMR-11). A lifecycle is neither the entity it governs (DOE-02) nor a
    workflow engine — it is the **represented state progression**.

The construct is **additive over the CERTIFIED EC-1 foundation *and* the CERTIFIED
DMC-02 Entity**, reusing both *by reference* (UDL-02 / DMI-05):

* Identity is derived through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.canonical_json` /
  :func:`~engine.certification.contracts.content_hash`) — no second identity scheme.
* The transitioned subject (DMR-06 ``transitions``) is a **reference to a CERTIFIED
  :class:`~data.entity.Entity`** (id + structural digest + name/type + meta-class),
  **never owned, embedded, or copied** (DMX-02 non-absorbing; DLA-07 by reference).
* Each transition is **forward-only** (DLA-01/DLA-C1/DLA-K3), **guarded** by a
  declarative, non-enforcing predicate reference (DLA-04/DLA-K4), and **records** a
  RUNTIME event reference (DLA-03/DMR-11 — no silent transition).
* State/event/guard behavior is a **RUNTIME reference** only (DMR-11 / DLA-07) — no
  workflow engine, scheduler, ETL/migration tool, or orchestration is defined.

**No workflow engine, scheduler, ETL/migration tool, orchestration engine, or vendor is
selected** (UDL-12 / DLA-09 / DLA-K5) — enforced fail-closed by a technology-marker scan
over the whole construct. This is the material exercise of UDL-12 Lifecycle Governance:
a lifecycle *is* abstract forward-only state progression.

A :class:`Lifecycle` is *immutable* (frozen — ENG-002 objecthood), *typed* (ENG-004,
DLA-K1/UDL-03), *identified* (ENG-001, DLA-K1/UDL-04), *subject-bound* (``transitions`` a
CERTIFIED entity by reference — DMR-06), *forward-only* (DLA-01/DLA-C1), *single-state*
(DLA-C5), *versioned*, and holds a *forward-only lifecycle state* (DOS-01…05, UDL-12).
Constructing a :class:`Lifecycle` enforces DLA-K1/K3/K4/K5, the transition rules
DLA-C1/C2/C4/C5, and UDL-12/03/04/05 **fail-closed**: an ill-formed lifecycle cannot
exist.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- DMC-02 reuse by reference (UDL-02) — never redefined -------------------------
from data.entity import Entity
from data.lifecycle_meta import (
    LIFECYCLE_META_CLASS,
    LIFECYCLE_ORDER,
    LIFECYCLE_RELATIONSHIPS,
    LIFECYCLE_SUBSTRATE_REFS,
    STATE_FACETS,
    LifecycleState,
    StateFacet,
)

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Lifecycle (mirrors EC-1 UCOS-<KIND>-<hex16>).
LIFECYCLE_ID_PREFIX = "UCOS-LIFECYCLE"

#: The reference prefix a lifecycle presents to bind RUNTIME state/event (DMR-11 / DLA-03).
RUNTIME_REF_PREFIX = "UCOS-RUNTIME-REF"

#: The reference prefix a transition guard presents (RUNTIME policy evaluation — DOB-06).
GUARD_REF_PREFIX = "UCOS-GUARD-REF"

#: The identity-reference prefix a transitioned Entity carries (DMR-06 ``transitions`` target).
ENTITY_ID_PREFIX = "UCOS-ENTITY"

#: The map of EC-1 / DMC-02 primitives this construct reuses *by reference* (never
#: redefined). Recorded for the reuse-integrity check (UDL-02 / DMI-05 / VC-5).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the lifecycle)",
    "ENG-004": "data.lifecycle_meta.LifecycleState + type_tag (ENG-004 typing discipline)",
    "ENG-005": "transitioned-entity + RUNTIME state/event/guard identity references (DMR-06/11)",
    "DMC-02": "data.entity.Entity — the CERTIFIED transitions target (DMR-06); referenced only",
    "RL-F2": "RUNTIME state/event/policy — behavior bound by reference (DMR-11 / DLA-07)",
}

#: Conservative secret markers used to enforce UDL-15 / DLA-09 / RR-07 (embed no secret).
_SECRET_MARKERS: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "privatekey",
    "api_key",
    "apikey",
    "access_token",
    "credential",
    "-----begin",
)

#: Conservative lifecycle-technology markers used to enforce **UDL-12 / DLA-09 / DLA-K5**
#: (select no workflow engine, scheduler, ETL/migration tool, or orchestration engine). A
#: lifecycle naming any of these is rejected fail-closed — a lifecycle is abstract,
#: forward-only state progression only. This is the material exercise of UDL-12.
_TECH_MARKERS: tuple[str, ...] = (
    "airflow",
    "temporal.io",
    "temporal-workflow",
    "camunda",
    "activiti",
    "bpmn",
    "celery",
    "luigi",
    "prefect",
    "dagster",
    "argo",
    "cron",
    "crontab",
    "quartz",
    "step functions",
    "stepfunctions",
    "nifi",
    "kettle",
    "talend",
    "informatica",
    "oozie",
    "azkaban",
    "flink",
    "apache beam",
    "aws glue",
    "databricks",
    "zeebe",
    "conductor",
    "cadence",
    "workflow engine",
    "etl pipeline",
    "scheduler daemon",
)


def runtime_ref_for(concept: str) -> str:
    """The reference a lifecycle presents to bind RUNTIME state/event (DMR-11 / DLA-03).

    A lifecycle's state/event behavior is a *reference* to the frozen RL-F2 concern
    (DLA-07), never a redefined engine.
    """
    return f"{RUNTIME_REF_PREFIX}:{concept}"


def guard_ref_for(predicate: str) -> str:
    """The declarative, non-enforcing guard reference a transition presents (DLA-04).

    A guard is a *RUNTIME policy evaluation by reference* (DOB-06); it evaluates, it does
    not enact (DLA-K4).
    """
    return f"{GUARD_REF_PREFIX}:{predicate}"


class LifecycleError(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`Lifecycle`.

    A :class:`Lifecycle` is fail-closed (TRACK-001): an ill-formed, backward, unguarded,
    unrecorded, or technology-bound state progression is rejected at construction rather
    than admitted as an invalid or non-abstract lifecycle.
    """


@dataclass(frozen=True, slots=True)
class GovernedSubjectRef:
    """A reference to a CERTIFIED Entity a lifecycle ``transitions`` (DMR-06 / DOR-06).

    Records **only** the transitioned entity's identity, structural fingerprint, name,
    type, and meta-class — never its implementation — so the lifecycle references, and
    never owns or absorbs, the subject it governs (DMX-02 non-absorbing; DLA-07 by
    reference; UDL-02 reuse-by-reference).
    """

    entity_id: str
    structure_digest: str
    name: str
    type_tag: str
    meta_class: str

    @classmethod
    def from_entity(cls, entity: Entity) -> GovernedSubjectRef:
        """Project a CERTIFIED :class:`~data.entity.Entity` into a governed-subject ref."""
        if not isinstance(entity, Entity):
            raise LifecycleError("a lifecycle transitions a data.entity.Entity (DMR-06)")
        return cls(
            entity_id=entity.entity_id,
            structure_digest=entity.structure_digest,
            name=entity.name,
            type_tag=entity.type_tag,
            meta_class=entity.meta_class,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "structure_digest": self.structure_digest,
            "name": self.name,
            "type_tag": self.type_tag,
            "meta_class": self.meta_class,
            "binding": "DMR-06:transitions",
            "owned": False,  # DLA-07 — transitioned by reference, never owned
            "absorbing": False,  # DMX-02 — referenced, not absorbed
        }


@dataclass(frozen=True, slots=True)
class Transition:
    """A single forward-only, guarded, recorded lifecycle transition (DLA-01/03/04).

    Fields:
        from_state: the source DOS-01…05 state.
        to_state:   the target DOS-01…05 state (strictly after ``from_state``; DLA-C1).
        guard_ref:  a declarative, non-enforcing guard reference (DLA-04 / DLA-K4;
                    a RUNTIME policy evaluation by reference — DOB-06).
        event_ref:  the recorded RUNTIME event reference the transition emits
                    (DLA-03 / DMR-11 / DOB-04 — no silent transition).
    """

    from_state: LifecycleState
    to_state: LifecycleState
    guard_ref: str
    event_ref: str

    def __post_init__(self) -> None:
        if not isinstance(self.from_state, LifecycleState) or not isinstance(
            self.to_state, LifecycleState
        ):
            raise LifecycleError("a transition connects two DOS-01…05 states (DLA-02)")
        here = LIFECYCLE_ORDER.index(self.from_state)
        there = LIFECYCLE_ORDER.index(self.to_state)
        # DLA-01 / DLA-C1 / DLA-K3 — forward-only; reversals are not admitted.
        if there <= here:
            raise LifecycleError(
                f"transition is not forward-only (DLA-01 / DLA-C1): "
                f"{self.from_state.value} → {self.to_state.value}"
            )
        # DLA-04 / DLA-K4 — a declarative, non-enforcing guard reference.
        if not isinstance(self.guard_ref, str) or not self.guard_ref.startswith(
            f"{GUARD_REF_PREFIX}:"
        ):
            raise LifecycleError("a transition must declare a guard reference (DLA-04 / DLA-K4)")
        # DLA-03 / DMR-11 — a recorded RUNTIME event reference (no silent transition).
        if not isinstance(self.event_ref, str) or not self.event_ref.startswith(
            f"{RUNTIME_REF_PREFIX}:"
        ):
            raise LifecycleError("a transition must record a RUNTIME event reference (DLA-03)")

    @property
    def is_forward_only(self) -> bool:
        """DLA-01 / DLA-C1 — the target state is strictly after the source state."""
        return LIFECYCLE_ORDER.index(self.to_state) > LIFECYCLE_ORDER.index(self.from_state)

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "guard_ref": self.guard_ref,
            "event_ref": self.event_ref,
            "forward_only": self.is_forward_only,
            "guard_enforcing": False,  # DLA-K4 — guards evaluate, do not enact
            "recorded": True,  # DLA-03 — every transition records a RUNTIME event
        }


@dataclass(frozen=True, slots=True)
class Lifecycle:
    """DMC-07 — an immutable, typed, identified, technology-neutral state progression.

    Fields:
        name:          the explicit lifecycle name (part of identity).
        type_tag:      the ENG-004 Type of the lifecycle (DLA-K1; UDL-03).
        subject_ref:   the CERTIFIED entity the lifecycle ``transitions`` (DMR-06;
                       DLA-07 non-owning).
        transitions:   the declared forward-only, guarded, recorded transitions
                       (DLA-01/03/04). Non-empty; no duplicate (from,to) pair.
        current_state: the single current DOS-01…05 state (single-state invariant;
                       DLA-C5).
        state_ref:     the RUNTIME state reference the current state binds to (DMR-11 /
                       DLA-07 / DOB-02). A reference obligation only — no engine defined.
        version:       the lifecycle version (supersession on breaking change; DLA-05).
        supersedes:    the id of a superseded lifecycle, recorded on breaking change
                       (DLA-05 / DLA-C4).
    """

    name: str
    type_tag: str
    subject_ref: GovernedSubjectRef
    transitions: tuple[Transition, ...]
    state_ref: str
    current_state: LifecycleState = LifecycleState.DEFINED
    version: str = "1.0.0"
    supersedes: str = ""

    def __post_init__(self) -> None:
        # explicit, decidable name.
        if not isinstance(self.name, str) or not self.name.strip():
            raise LifecycleError("lifecycle must have an explicit name")
        # DLA-K1 / DMK-01 / UDL-03 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise LifecycleError("lifecycle must be typed with an ENG-004 type_tag (DLA-K1)")
        # DMR-06 — the transitioned subject is a reference to a CERTIFIED entity.
        if not isinstance(self.subject_ref, GovernedSubjectRef):
            raise LifecycleError("lifecycle transitions a CERTIFIED entity by reference (DMR-06)")
        if not self.subject_ref.entity_id.startswith(f"{ENTITY_ID_PREFIX}-"):
            raise LifecycleError("the transitioned subject is not a CERTIFIED Entity id (DMR-06)")
        if len(self.subject_ref.structure_digest) != 64 or any(
            c not in "0123456789abcdef" for c in self.subject_ref.structure_digest
        ):
            raise LifecycleError("the transitioned subject carries no structural digest (UDL-06)")
        # DLA-02 / DLA-C1 — a non-empty set of forward-only transitions.
        if not isinstance(self.transitions, tuple) or not self.transitions:
            raise LifecycleError("lifecycle must declare ≥1 forward-only transition (DLA-C1)")
        seen_pairs: set[tuple[str, str]] = set()
        for tr in self.transitions:
            if not isinstance(tr, Transition):
                raise LifecycleError("transitions are Transition records (DLA-01)")
            pair = (tr.from_state.value, tr.to_state.value)
            if pair in seen_pairs:
                raise LifecycleError("lifecycle declares a duplicate transition (DLA-C1)")
            seen_pairs.add(pair)
        # V5 / UDL-12 / DLA-C5 — a single, valid, forward-only current state.
        if not isinstance(self.current_state, LifecycleState):
            raise LifecycleError("current state must be a DOS-01…05 state (UDL-12)")
        # DMR-11 / DLA-07 / DOB-02 — the current state binds a RUNTIME state reference.
        if not isinstance(self.state_ref, str) or not self.state_ref.startswith(
            f"{RUNTIME_REF_PREFIX}:"
        ):
            raise LifecycleError("state must bind a RUNTIME state reference (DMR-11 / DLA-07)")
        # DLA-08 — a lifecycle records an explicit, non-empty version.
        if not isinstance(self.version, str) or not self.version.strip():
            raise LifecycleError("lifecycle must record an explicit version (DLA-08 / UDL-12)")
        if not isinstance(self.supersedes, str):
            raise LifecycleError("lifecycle supersedes reference must be a string (DLA-05)")
        # UDL-12 / DLA-09 / DLA-K5 — names no workflow/scheduler technology (material).
        if self._scan_technology():
            raise LifecycleError(
                "lifecycle names a workflow/scheduler/ETL engine or vendor "
                "(UDL-12 / DLA-09 / DLA-K5)"
            )

    # -- technology-neutrality (UDL-12, material) ------------------------------

    def _scan_technology(self) -> bool:
        """True iff any technology marker appears in the lifecycle's declared surface."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECH_MARKERS)

    def names_technology(self) -> bool:
        """UDL-12 / DLA-09 / DLA-K5 / C6 — True iff the lifecycle names a workflow tech."""
        return self._scan_technology()

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the lifecycle (structure + subject reference)."""
        return {
            "meta_class": LIFECYCLE_META_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "subject_ref": {
                "entity_id": self.subject_ref.entity_id,
                "structure_digest": self.subject_ref.structure_digest,
                "name": self.subject_ref.name,
                "type_tag": self.subject_ref.type_tag,
                "meta_class": self.subject_ref.meta_class,
            },
            "transitions": [
                {
                    "from_state": t.from_state.value,
                    "to_state": t.to_state.value,
                    "guard_ref": t.guard_ref,
                    "event_ref": t.event_ref,
                }
                for t in self.transitions
            ],
            "current_state": self.current_state.value,
            "state_ref": self.state_ref,
            "version": self.version,
            "supersedes": self.supersedes,
        }

    @property
    def structure_digest(self) -> str:
        """The EC-1 content hash of the lifecycle core — its structural fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def lifecycle_id(self) -> str:
        """The deterministic ENG-001 identity of the lifecycle (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second identity
        scheme): identical lifecycle always yields the identical id, so identity is
        reproducible and byte-stable (determinism, VC-4).
        """
        return f"{LIFECYCLE_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (DATA-005 / DATA-011) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (DMC-07)."""
        return LIFECYCLE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the DMR-01…12 relationships the lifecycle participates in."""
        return LIFECYCLE_RELATIONSHIPS

    def transitioned_entity_id(self) -> str:
        """The identity of the entity this lifecycle transitions (DMR-06; by reference)."""
        return self.subject_ref.entity_id

    def states(self) -> tuple[LifecycleState, ...]:
        """DLA-02 — the closed forward-only state set (DOS-01…05)."""
        return LIFECYCLE_ORDER

    @property
    def facet(self) -> StateFacet:
        """DXH-07 — the facet of the current state (Definitional/Operative/Terminal)."""
        return STATE_FACETS[self.current_state]

    def transition_pairs(self) -> tuple[tuple[str, str], ...]:
        """The declared (from, to) state pairs of the lifecycle's transitions."""
        return tuple((t.from_state.value, t.to_state.value) for t in self.transitions)

    def guard_refs(self) -> tuple[str, ...]:
        """The declarative guard references of the lifecycle's transitions (DLA-04)."""
        return tuple(t.guard_ref for t in self.transitions)

    def event_refs(self) -> tuple[str, ...]:
        """The recorded RUNTIME event references of the lifecycle's transitions (DLA-03)."""
        return tuple(t.event_ref for t in self.transitions)

    # -- lifecycle property predicates -----------------------------------------

    def is_forward_only(self) -> bool:
        """DLA-01 / DLA-C1 / DLA-K3 — every declared transition is forward-only."""
        return all(t.is_forward_only for t in self.transitions)

    def transitions_are_guarded(self) -> bool:
        """DLA-04 / DLA-C2 / DLA-K4 — every transition declares a guard reference."""
        return bool(self.transitions) and all(
            t.guard_ref.startswith(f"{GUARD_REF_PREFIX}:") for t in self.transitions
        )

    def transitions_are_recorded(self) -> bool:
        """DLA-03 / DLA-C2 / DMR-11 — every transition records a RUNTIME event reference."""
        return bool(self.transitions) and all(
            t.event_ref.startswith(f"{RUNTIME_REF_PREFIX}:") for t in self.transitions
        )

    def guards_are_non_enforcing(self) -> bool:
        """DLA-K4 / UDL-13 — guards are declarative predicates; they enact nothing."""
        return True

    def is_single_state(self) -> bool:
        """DLA-C5 — the lifecycle is in exactly one current state at any point."""
        return isinstance(self.current_state, LifecycleState)

    def states_are_closed(self) -> bool:
        """DLA-02 / DOS-01…05 — the state set is the closed forward-only DOS-01…05 set."""
        return self.states() == LIFECYCLE_ORDER

    def is_classified(self) -> bool:
        """DXH-07 — the current state maps to exactly one DXH-07 facet."""
        return self.current_state in STATE_FACETS

    def binds_runtime_by_reference(self) -> bool:
        """DMR-11 / DLA-07 / DOB-02 — state/event behavior binds a RUNTIME reference only."""
        return (
            self.state_ref.startswith(f"{RUNTIME_REF_PREFIX}:") and self.transitions_are_recorded()
        )

    def represents_retention(self) -> bool:
        """DLA-06 / DLA-C3 — retention/archival are represented Terminal-State records.

        A lifecycle that declares a transition into a Terminal-State facet
        (DEPRECATED/SUPERSEDED/RETIRED) represents retention as a state, not scheduler
        technology.
        """
        return any(STATE_FACETS[t.to_state] is StateFacet.TERMINAL for t in self.transitions)

    def is_founding_acyclic(self) -> bool:
        """V4 / DMK-03 — the founding/transition graph is acyclic.

        The lifecycle's founding references (``transitions`` → entity, ``behaves-as`` →
        RUNTIME state/event/guard) are recorded by *identity reference*; none may
        reference the lifecycle itself, so the founding graph is a DAG. The state
        transitions are strictly forward-only, so the transition graph is also acyclic.
        """
        own = self.lifecycle_id
        refs = {self.transitioned_entity_id(), self.state_ref}
        refs.update(self.guard_refs())
        refs.update(self.event_refs())
        return own not in refs and self.is_forward_only()

    def transitions_subject(self, entity_id: str) -> bool:
        """DMR-06 — whether this lifecycle transitions the entity ``entity_id``."""
        return entity_id == self.transitioned_entity_id()

    def absorbs_subject(self) -> bool:
        """DLA-07 / DMX-02 — the lifecycle references the subject it governs, never owns it."""
        return False

    # -- non-constitutiveness (UDL-15 / DLA-09) --------------------------------

    def confers_authority(self) -> bool:
        """UDL-15 / DLA-09 / C7 — a lifecycle confers no authority (structurally none)."""
        return False

    def embeds_secret(self) -> bool:
        """UDL-15 / DLA-09 / RR-07 / C7 — True iff the lifecycle appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """UDL-02 / DMI-05 / VC-5 — a lifecycle redefines no EL-1/DMC-02/RL-F2 model."""
        return False

    def selects_technology(self) -> bool:
        """UDL-12 / DLA-09 / DLA-K5 — a lifecycle selects no workflow technology (material)."""
        return self._scan_technology()

    # -- lifecycle progression (UDL-12, forward-only) --------------------------

    def transition(self, to_state: LifecycleState) -> Lifecycle:
        """Return a new lifecycle advanced to ``to_state`` (forward-only; UDL-12 / DLA-01).

        The advance must correspond to a *declared* transition (DLA-C2) and be
        forward-only (DLA-01/DLA-C1). Breaking change to the state model is supersession,
        never in-place mutation (DLA-05 / UDL-15).

        Raises:
            LifecycleError: on a backward transition or one not declared by the lifecycle.
        """
        if not isinstance(to_state, LifecycleState):
            raise LifecycleError("target state must be a DOS-01…05 state (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.current_state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there <= here:
            raise LifecycleError(
                f"lifecycle is forward-only (UDL-12 / DLA-01): "
                f"{self.current_state.value} → {to_state.value} is not forward"
            )
        declared = {(t.from_state, t.to_state) for t in self.transitions}
        if (self.current_state, to_state) not in declared:
            raise LifecycleError(
                f"transition {self.current_state.value} → {to_state.value} is not declared "
                f"(DLA-C2 — transitions are guarded and recorded)"
            )
        return replace(self, current_state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the lifecycle."""
        return {
            "lifecycle_id": self.lifecycle_id,
            "meta_class": self.meta_class,
            "name": self.name,
            "type_tag": self.type_tag,
            "subject_ref": self.subject_ref.to_dict(),
            "transitioned_entity_id": self.transitioned_entity_id(),
            "transitions": [t.to_dict() for t in self.transitions],
            "transition_pairs": [list(p) for p in self.transition_pairs()],
            "guard_refs": list(self.guard_refs()),
            "event_refs": list(self.event_refs()),
            "states": [s.value for s in self.states()],
            "states_closed": self.states_are_closed(),
            "current_state": self.current_state.value,
            "facet": self.facet.value,
            "single_state": self.is_single_state(),
            "forward_only": self.is_forward_only(),
            "transitions_guarded": self.transitions_are_guarded(),
            "transitions_recorded": self.transitions_are_recorded(),
            "guards_non_enforcing": self.guards_are_non_enforcing(),
            "represents_retention": self.represents_retention(),
            "state_ref": self.state_ref,
            "binds_runtime_by_reference": self.binds_runtime_by_reference(),
            "names_technology": self.names_technology(),
            "classified": self.is_classified(),
            "version": self.version,
            "supersedes": self.supersedes,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(LIFECYCLE_SUBSTRATE_REFS),
            "absorbs_subject": self.absorbs_subject(),
        }


def forward_transitions(
    *,
    guard_prefix: str = "guard",
    event_prefix: str = "event",
) -> tuple[Transition, ...]:
    """The canonical closed forward-only DOS-01…05 transition chain (DLA-C1).

    Builds the four adjacent forward transitions
    DEFINED→ACTIVE→DEPRECATED→SUPERSEDED→RETIRED, each guarded by a declarative guard
    reference (DLA-04) and recording a RUNTIME event reference (DLA-03).
    """
    chain: list[Transition] = []
    for src, dst in zip(LIFECYCLE_ORDER, LIFECYCLE_ORDER[1:], strict=False):
        label = f"{src.value.lower()}-to-{dst.value.lower()}"
        chain.append(
            Transition(
                from_state=src,
                to_state=dst,
                guard_ref=guard_ref_for(f"{guard_prefix}.{label}"),
                event_ref=runtime_ref_for(f"{event_prefix}.{label}"),
            )
        )
    return tuple(chain)


def make_lifecycle(
    name: str,
    type_tag: str,
    subject: Entity | GovernedSubjectRef,
    transitions: tuple[Transition, ...],
    state_ref: str,
    *,
    current_state: LifecycleState = LifecycleState.DEFINED,
    version: str = "1.0.0",
    supersedes: str = "",
) -> Lifecycle:
    """Construct a well-formed :class:`Lifecycle` (fail-closed factory).

    ``subject`` is the construct the lifecycle transitions — either a CERTIFIED
    :class:`~data.entity.Entity` (reused by reference — the DMR-06 ``transitions``
    target) or an already-projected :class:`GovernedSubjectRef`.
    """
    subject_ref = (
        subject
        if isinstance(subject, GovernedSubjectRef)
        else GovernedSubjectRef.from_entity(subject)
    )
    return Lifecycle(
        name=name,
        type_tag=type_tag,
        subject_ref=subject_ref,
        transitions=tuple(transitions),
        state_ref=state_ref,
        current_state=current_state,
        version=version,
        supersedes=supersedes,
    )


__all__ = [
    "LIFECYCLE_ID_PREFIX",
    "RUNTIME_REF_PREFIX",
    "GUARD_REF_PREFIX",
    "ENTITY_ID_PREFIX",
    "REUSE_REFS",
    "runtime_ref_for",
    "guard_ref_for",
    "LifecycleError",
    "GovernedSubjectRef",
    "Transition",
    "Lifecycle",
    "forward_transitions",
    "make_lifecycle",
]
