"""EC3-B11-U07 — The Universal Orchestration construct (SMC-07).

Realizes the meta-model concept **SMC-07 Orchestration** (SERVICE-005 §2; SERVICE-003 SOE-07;
SERVICE-011 §3):

    the **coordinated arrangement of operations and services toward an outcome** — the
    time-ordered / conditional coordination distinct from the structural assembly of
    Composition — an ENG-002 Object bearing an ENG-001 Identity, classified by an ENG-004 Type
    (SXH-07 = Sequential / Parallel / Choreographed), that **orchestrates** operations/services
    by reference (SMR-06, reference-only), **composes** the coordinated set (SMR-05,
    reference-only, acyclic), is **bound-by** a composition contract (SMR-02, founding, acyclic),
    **behaves-as** the RUNTIME workflow/orchestration/event concern (SMR-11, RUNTIME-009/013/008,
    by reference), and carries inter-step data via **operates-on** (SMR-13, DF-2, by reference).

The construct is the **deterministic coordination layer**: it declares an explicit, acyclic
**coordination-dependency graph** over its steps (SOO-06 / SOO-C1) from which a single,
byte-stable **execution plan** (topological levels) is derived — so ordering, sequencing,
scheduling, and completion are decidable with **no hidden execution path and no runtime
ambiguity**. Timeout / retry / rollback / compensation / fault-isolation / cancellation are
expressed as *references* to the frozen RUNTIME concern (SMR-11, RL-F2) the orchestration
reuses — never re-implemented here (SOO-03 / SOO-C5); a step is isolated because it is a member
*by reference*.

The construct is **additive over the CERTIFIED EC-1 foundation** and reuses it — and the
CERTIFIED SMC-01…06 Service / Capability / Contract / Interface / Operation / Composition — *by
reference* (USL-02 / SMI-05): identity and value-fidelity are derived through the EC-1 certified
deterministic encoding, so this module introduces **no second identity scheme and no parallel
value model**. It selects no technology / workflow-engine / scheduler / BPMN / state-machine
(USL-15 / SOO-09) and confers no authority.

An :class:`Orchestration` is *immutable* (ENG-002 objecthood), *typed* (ENG-004), *identified*
(ENG-001), *classified* (SXH-07 kind), *coordinates ≥1 step by reference* (SMR-06 / SOO-04),
*bound-by a composition contract* (SMR-02 / SOO-05), *runtime-reusing* (SMR-11 / SOO-03),
*data-by-reference* (SMR-13 / SOO-07), holds a *forward-only lifecycle state* (SOS-01…06,
USL-12), and is *founding-acyclic* over its coordination graph (SMK-03 / SOO-06 / SOO-C1: no
self-dependency, every edge resolves, no cycle). Constructing an :class:`Orchestration` enforces
these obligations fail-closed: an ill-formed orchestration cannot be instantiated. It
realizes/binds no Service, Capability, Contract, Interface, Operation, Composition, Execution,
Policy, or Security object — those are separate units; this construct binds them only *by
reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from engine.certification.contracts import canonical_json, content_hash
from service.orchestration_meta import (
    KIND_BEHAVIOR_SUFFIX,
    KIND_RUNTIME_CONCERN,
    LIFECYCLE_ORDER,
    ORCHESTRATION_META_CLASS,
    ORCHESTRATION_RELATIONSHIPS,
    ORCHESTRATION_SUBSTRATE_REFS,
    OrchestrationKind,
    ServiceState,
)
from service.service import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    ServiceError,
)

#: The deterministic id prefix for a realized Orchestration (mirrors EC-1 UCOS-<KIND>-<hex16>).
ORCHESTRATION_ID_PREFIX = "UCOS-ORCHESTRATION"

#: The default abstract composition contract an orchestration is bound-by (SMR-02; SMC-03).
DEFAULT_CONTRACT_REF = "ENG-005:SOE-03:ucos.service.contract.foundation"

#: The map of frozen-foundation primitives this construct reuses *by reference*.
ORCHESTRATION_FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the orchestration)",
    "ENG-003": "engine.certification.contracts.canonical_json (structural value fidelity)",
    "ENG-004": "service.orchestration_meta.OrchestrationKind + type_tag (ENG-004 typing, by ref)",
    "ENG-005": "reference identifiers (step/composed/contract/data refs; no new construct)",
    "RL-F2": "workflow/orchestration/event bound by reference (SMR-11; RUNTIME-009/013/008)",
    "DF-2": "inter-step data bound by reference (SMR-13); represented data not redefined",
}


def _default_behavior_ref(kind: OrchestrationKind) -> str:
    """The abstract RL-F2 behavior reference for ``kind`` (SERVICE-011 §7; SOO-03)."""
    concern = KIND_RUNTIME_CONCERN[kind]
    suffix = KIND_BEHAVIOR_SUFFIX[kind]
    return f"ENG-005:RL-F2:{concern}.{suffix}"


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(f"{name} must be a non-empty ENG-005 reference (SMR-02/06/11/13)")
    return value


def _require_ref_tuple(name: str, values: Any, *, allow_empty: bool = False) -> tuple[str, ...]:
    """Require ``values`` to be a tuple of non-empty ENG-005 reference strings."""
    if not isinstance(values, tuple):
        raise ServiceError(f"{name} must be a tuple of ENG-005 references (SMR-06/13)")
    if not allow_empty and not values:
        raise ServiceError(f"{name} must be non-empty (orchestration coordinates ≥1 step; SOO-04)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise ServiceError(f"{name} entries must be non-empty ENG-005 references (SMR-06/13)")
    return values


def _require_edges(name: str, values: Any) -> tuple[tuple[str, str], ...]:
    """Require ``values`` to be a tuple of (dependent, prerequisite) reference pairs."""
    if not isinstance(values, tuple):
        raise ServiceError(f"{name} must be a tuple of (dependent, prerequisite) pairs (SOO-06)")
    edges: list[tuple[str, str]] = []
    for pair in values:
        if not (isinstance(pair, tuple) and len(pair) == 2):
            raise ServiceError(f"{name} entries must be 2-tuples (dependent, prerequisite)")
        dep, pre = pair
        if not (isinstance(dep, str) and dep.strip() and isinstance(pre, str) and pre.strip()):
            raise ServiceError(f"{name} endpoints must be non-empty step references (SOO-06)")
        edges.append((dep, pre))
    return tuple(edges)


@dataclass(frozen=True, slots=True)
class Orchestration:
    """SMC-07 — an immutable, typed, identified, deterministic coordination of operations.

    Fields:
        type_tag:      the ENG-004 Type of the orchestration (decidable, non-empty) — SOO-01.
        kind:          the SXH-07 classification (Sequential / Parallel / Choreographed; SXC-02).
        step_refs:     tuple of ENG-005 references to the coordinated operations/services
                       (SMR-06 orchestrates; SOR-06; reference-only; SOO-04). Non-empty; these
                       are the nodes of the coordination graph.
        dependencies:  tuple of ``(dependent_step, prerequisite_step)`` coordination edges over
                       ``step_refs`` (SMR-05 composes; SOO-06). The founding coordination graph
                       must be acyclic (SOO-C1); it fixes the deterministic execution plan.
        contract_ref:  the ENG-005 reference to the composition contract that bounds the
                       coordination (SMR-02 bound-by; SOR-02; founding; SOO-05 / SOO-K2).
        behavior_ref:  the ENG-005 reference to the RUNTIME workflow/orchestration/event concern
                       the orchestration behaves-as (SMR-11; RL-F2; RUNTIME-009/013/008; §7). If
                       omitted it defaults to the kind-appropriate RUNTIME concern (SOO-03).
        data_refs:     tuple of DF-2-represented inter-step data references (SMR-13 operates-on;
                       SOR-13 / SOO-07; by reference). May be empty.
        state:         the SOS-01…06 lifecycle state (forward-only) — USL-12.
    """

    type_tag: str
    kind: OrchestrationKind
    step_refs: tuple[str, ...]
    dependencies: tuple[tuple[str, str], ...] = ()
    contract_ref: str = DEFAULT_CONTRACT_REF
    behavior_ref: str = ""
    data_refs: tuple[str, ...] = field(default=())
    state: ServiceState = ServiceState.DEFINED

    def __post_init__(self) -> None:
        # SOO-K1 / USL-03 / SOO-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ServiceError("orchestration must be typed: a non-empty ENG-004 type_tag (SOO-01)")
        # SXH-07 / SXC-02 — classified by exactly one orchestration kind.
        if not isinstance(self.kind, OrchestrationKind):
            raise ServiceError("orchestration kind must be an SXH-07 OrchestrationKind (SXC-02)")
        # SMR-06 / SOR-06 / SOO-04 — coordinates ≥1 step, by reference.
        _require_ref_tuple("step_refs", self.step_refs)
        # SMR-05 / SOO-06 — coordination edges are well-formed (dependent, prerequisite) pairs.
        _require_edges("dependencies", self.dependencies)
        # §7 / SOO-03 — derive the kind-appropriate RUNTIME behavior reference if omitted.
        if not (isinstance(self.behavior_ref, str) and self.behavior_ref.strip()):
            object.__setattr__(self, "behavior_ref", _default_behavior_ref(self.kind))
        # SMR-02 / SOR-02 / SOO-05 — bound by a composition contract, by reference.
        _require_reference("contract_ref", self.contract_ref)
        # SMR-11 / SOR-11 / SOO-03 — behaves-as RUNTIME workflow/orchestration/event, by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # SMR-13 / SOR-13 / SOO-07 — inter-step data by reference (may be empty).
        _require_ref_tuple("data_refs", self.data_refs, allow_empty=True)
        # V5 / USL-12 — a valid lifecycle state.
        if not isinstance(self.state, ServiceState):
            raise ServiceError("orchestration state must be a SOS-01…06 ServiceState (USL-12)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the orchestration (its identity-defining tuple)."""
        return {
            "meta_class": ORCHESTRATION_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "step_refs": list(self.step_refs),
            "dependencies": [list(edge) for edge in self.dependencies],
            "contract_ref": self.contract_ref,
            "behavior_ref": self.behavior_ref,
            "data_refs": list(self.data_refs),
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the orchestration core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def orchestration_id(self) -> str:
        """The deterministic ENG-001 identity of the orchestration (borne by this object)."""
        return f"{ORCHESTRATION_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    @property
    def self_ref(self) -> str:
        """The ENG-005 self-reference form of this orchestration (for self-founding detection)."""
        return f"ENG-005:SOE-07:{self.type_tag}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (SMC-07)."""
        return ORCHESTRATION_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the SMR-01…13 relationships the orchestration participates in."""
        return ORCHESTRATION_RELATIONSHIPS

    # -- deterministic coordination graph (SOO-06 / SOO-C1) --------------------

    def coordination_levels(self) -> tuple[tuple[str, ...], ...]:
        """The deterministic topological levels of the coordination graph (execution plan).

        Each level is the lexicographically-sorted set of steps whose prerequisites are all
        satisfied by earlier levels — a single, byte-stable schedule (no runtime ambiguity).
        Returns an empty tuple iff the graph is ill-formed or cyclic (fail-closed).
        """
        nodes = set(self.step_refs)
        prereqs: dict[str, set[str]] = {n: set() for n in self.step_refs}
        for dep, pre in self.dependencies:
            if dep not in nodes or pre not in nodes or dep == pre:
                return ()  # unresolved endpoint or self-dependency — ill-formed (SOO-C1)
            prereqs[dep].add(pre)
        resolved: set[str] = set()
        remaining = set(self.step_refs)
        levels: list[tuple[str, ...]] = []
        while remaining:
            ready = sorted(n for n in remaining if prereqs[n] <= resolved)
            if not ready:
                return ()  # a cycle remains — fail-closed (SOO-06 / SOO-C1)
            levels.append(tuple(ready))
            resolved.update(ready)
            remaining.difference_update(ready)
        return tuple(levels)

    def execution_plan(self) -> tuple[str, ...]:
        """The flattened deterministic execution order (sequencing) — empty iff cyclic."""
        return tuple(step for level in self.coordination_levels() for step in level)

    def is_coordination_acyclic(self) -> bool:
        """SOO-06 / SOO-C1 — the founding coordination-dependency graph is acyclic."""
        return len(self.execution_plan()) == len(self.step_refs)

    def is_founding_acyclic(self) -> bool:
        """V4 / SMK-03 / SOO-06 / SOO-C1 — the founding graph is acyclic (a DAG).

        The orchestration composes/orchestrates its steps *by reference*; the founding
        coordination graph must carry no cycle and no self-dependency. Canonical encodability
        proves the core is well-formed; the coordination plan proves acyclicity.
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return self.is_coordination_acyclic()

    def dependencies_resolve(self) -> bool:
        """SOO-C1 / SMK-03 — every coordination edge resolves to a step; no self-dependency."""
        nodes = set(self.step_refs)
        return all(
            dep in nodes and pre in nodes and dep != pre for dep, pre in self.dependencies
        )

    # -- orchestration-specific obligations ------------------------------------

    def coordinates_steps(self) -> bool:
        """SMR-06 / SOR-06 / SOO-04 — the orchestration coordinates ≥1 step, by reference."""
        return bool(self.step_refs) and all(
            isinstance(s, str) and bool(s.strip()) for s in self.step_refs
        )

    def topology_valid(self) -> bool:
        """SXH-07 / SOO-C3 — the coordination topology matches the orchestration kind.

        * Sequential    — the coordination graph induces one total order (every level has
                          exactly one ready step; a strict chain covering all steps). n ≥ 1.
        * Parallel      — the steps are concurrent: no founding coordination dependency. n ≥ 2.
        * Choreographed — event-driven partial order over ≥ 2 steps; acyclic. n ≥ 2.
        """
        n = len(self.step_refs)
        levels = self.coordination_levels()
        if not levels:  # cyclic / ill-formed
            return False
        if self.kind is OrchestrationKind.SEQUENTIAL:
            return n >= 1 and all(len(level) == 1 for level in levels)
        if self.kind is OrchestrationKind.PARALLEL:
            return n >= 2 and len(self.dependencies) == 0
        return n >= 2  # CHOREOGRAPHED — acyclic partial order (levels non-empty proves acyclic)

    def steps_contracted(self) -> bool:
        """SOO-05 — each coordinated step is a contracted operation; the orchestration is bound."""
        return self.contract_bound() and self.coordinates_steps()

    def contract_bound(self) -> bool:
        """SMR-02 / SOR-02 / SOO-05 / SOO-K2 — the orchestration is bound by a contract."""
        return bool(self.contract_ref.strip())

    def runtime_reuse_valid(self) -> bool:
        """SOO-03 / SOO-C3 / §7 — behaves-as the kind-appropriate RUNTIME concern by reference."""
        expected = KIND_RUNTIME_CONCERN[self.kind]
        return bool(self.behavior_ref.strip()) and expected in self.behavior_ref

    def behavior_by_reference(self) -> bool:
        """SMR-11 / USL-10 — behavior/execution binds RL-F2 by ENG-005 reference."""
        return bool(self.behavior_ref.strip())

    def data_by_reference(self) -> bool:
        """SMR-13 / SOO-07 / USL-11 — every inter-step data ref is a DF-2 reference."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.data_refs)

    def references_resolve(self) -> bool:
        """SMK-05/07 / SOO-K4 — every ENG-005 reference is a non-empty resolvable id."""
        singles = (self.contract_ref, self.behavior_ref)
        tuples = (*self.step_refs, *self.data_refs)
        return all(
            isinstance(ref, str) and bool(ref.strip()) for ref in (*singles, *tuples)
        ) and self.dependencies_resolve()

    # -- non-constitutiveness (USL-15 / SOO-09) --------------------------------

    def confers_authority(self) -> bool:
        """USL-15 / SOO-09 / C7 — an orchestration confers no authority (structurally none)."""
        return False

    def selects_technology(self) -> bool:
        """USL-15 / SOO-09 / C7 — True iff the orchestration names a workflow engine/technology."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """USL-15 / RR-07 / C7 — True iff the orchestration appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """USL-02 / SMI-05 / VC-5 — an orchestration redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (USL-12, forward-only) --------------------------------------

    def transition(self, to_state: ServiceState) -> Orchestration:
        """Return a new orchestration advanced to ``to_state`` (forward-only; USL-12)."""
        if not isinstance(to_state, ServiceState):
            raise ServiceError("target state must be a SOS-01…06 ServiceState (USL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise ServiceError(
                f"lifecycle is forward-only (USL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the orchestration."""
        return {
            "orchestration_id": self.orchestration_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "step_refs": list(self.step_refs),
            "dependencies": [list(edge) for edge in self.dependencies],
            "execution_plan": list(self.execution_plan()),
            "coordination_levels": [list(level) for level in self.coordination_levels()],
            "contract_ref": self.contract_ref,
            "behavior_ref": self.behavior_ref,
            "data_refs": list(self.data_refs),
            "value_digest": self.value_digest,
            "state": self.state.value,
            "runtime_concern": KIND_RUNTIME_CONCERN[self.kind],
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(ORCHESTRATION_SUBSTRATE_REFS),
        }


def make_orchestration(
    type_tag: str,
    step_refs: tuple[str, ...],
    *,
    kind: OrchestrationKind = OrchestrationKind.SEQUENTIAL,
    dependencies: tuple[tuple[str, str], ...] = (),
    contract_ref: str = DEFAULT_CONTRACT_REF,
    behavior_ref: str = "",
    data_refs: tuple[str, ...] = (),
    state: ServiceState = ServiceState.DEFINED,
) -> Orchestration:
    """Construct a well-formed :class:`Orchestration` (fail-closed factory)."""
    return Orchestration(
        type_tag=type_tag,
        kind=kind,
        step_refs=step_refs,
        dependencies=dependencies,
        contract_ref=contract_ref,
        behavior_ref=behavior_ref,
        data_refs=data_refs,
        state=state,
    )


__all__ = [
    "ORCHESTRATION_ID_PREFIX",
    "DEFAULT_CONTRACT_REF",
    "ORCHESTRATION_FOUNDATION_REUSE",
    "Orchestration",
    "make_orchestration",
]
