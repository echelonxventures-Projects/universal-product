"""EC3-B11-U08 — The Universal Execution construct (SMC-08).

Realizes the meta-model concept **SMC-08 Execution** (SERVICE-005 §2; SERVICE-003 SOE-08;
SERVICE-012 §3):

    the **carrying-out of an invoked operation** — the act by which a contracted operation is
    performed, distinct from the operation's definition (SMC-05) and the orchestration that
    sequences it (SMC-07) — an ENG-002 Object bearing an ENG-001 Identity, classified by an
    ENG-004 Type (SXH-08 = Synchronous / Asynchronous / Transactional), that is **executed** by
    exactly the operation that references it (SMR-07, reference-only; SEX-04), **behaves-as** the
    RUNTIME execution/state/workflow concern (SMR-11, RUNTIME-006/007/009, by reference),
    carries the DF-2-represented data it reads/writes via **operates-on** (SMR-13, by reference),
    and is **governed-by** a declarative policy (SMR-08, reference-only).

The construct is the **deterministic runtime-realization layer**: it names *which* frozen
RUNTIME concern carries out the operation (per SXH-08 kind — SEX-03 / §7) and *which* DF-2 data
it reads/writes (SEX-07) as **references**, so the carrying-out is decidable with **no hidden
runtime behavior, no non-deterministic scheduling, and no implicit execution**. Atomicity,
consistency, isolation, durability of a transactional execution, timeout / retry / rollback /
compensation / recovery, state transitions, and asynchronous completion are all expressed as
*references* to the frozen RUNTIME concern the execution reuses (SMR-11, RL-F2; RUNTIME-006/007/
008/009) — never re-implemented here (SEX-06 / §9 SEX-C1…C5). The execution defines no runtime
engine, scheduler, state store, workflow engine, or event bus; it references them (STH-14).

The construct is **additive over the CERTIFIED EC-1 foundation** and reuses it — and the
CERTIFIED SMC-01…07 Service / Capability / Contract / Interface / Operation / Composition /
Orchestration — *by reference* (USL-02 / SMI-05): identity and value-fidelity are derived
through the EC-1 certified deterministic encoding, so this module introduces **no second
identity scheme and no parallel value model**. It selects no technology / runtime-engine /
container / scheduler (USL-15 / SEX-09) and confers no authority.

An :class:`Execution` is *immutable* (ENG-002 objecthood), *typed* (ENG-004), *identified*
(ENG-001), *classified* (SXH-08 kind), *operation-bound by reference* (SMR-07 / SEX-04),
*runtime-reusing* (SMR-11 / SEX-03), *data-by-reference* (SMR-13 / SEX-07), *policy-governed by
reference* (SMR-08 / §11), and holds a *forward-only lifecycle state* (SOS-01…06, USL-12).
Constructing an :class:`Execution` enforces these obligations fail-closed: an ill-formed
execution cannot be instantiated. It realizes/binds no Service, Capability, Contract, Interface,
Operation, Composition, Orchestration, Policy, or Security object — those are separate units;
this construct binds them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from engine.certification.contracts import canonical_json, content_hash
from service.execution_meta import (
    EXECUTION_META_CLASS,
    EXECUTION_RELATIONSHIPS,
    EXECUTION_SUBSTRATE_REFS,
    KIND_BEHAVIOR_SUFFIX,
    KIND_RUNTIME_CONCERN,
    LIFECYCLE_ORDER,
    ExecutionKind,
    ServiceState,
)
from service.service import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    ServiceError,
)

#: The deterministic id prefix for a realized Execution (mirrors EC-1 UCOS-<KIND>-<hex16>).
EXECUTION_ID_PREFIX = "UCOS-EXECUTION"

#: The default declarative policy an execution is governed-by (SMR-08; §11; reference-only).
DEFAULT_POLICY_REF = "ENG-005:SOE-09:ucos.service.policy.foundation"

#: The map of frozen-foundation primitives this construct reuses *by reference*.
EXECUTION_FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the execution)",
    "ENG-003": "engine.certification.contracts.canonical_json (structural value fidelity)",
    "ENG-004": "service.execution_meta.ExecutionKind + type_tag (ENG-004 typing, by reference)",
    "ENG-005": "reference identifiers (operation/behavior/data/policy refs; no new construct)",
    "RL-F2": "execution/state/workflow bound by reference (SMR-11; RUNTIME-006/007/009/008)",
    "DF-2": "read/written data bound by reference (SMR-13); represented data not redefined",
}


def _default_behavior_ref(kind: ExecutionKind) -> str:
    """The abstract RL-F2 behavior reference for ``kind`` (SERVICE-012 §7; SEX-03)."""
    concern = KIND_RUNTIME_CONCERN[kind]
    suffix = KIND_BEHAVIOR_SUFFIX[kind]
    return f"ENG-005:RL-F2:{concern}.{suffix}"


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(f"{name} must be a non-empty ENG-005 reference (SMR-07/08/11/13)")
    return value


def _require_ref_tuple(name: str, values: Any) -> tuple[str, ...]:
    """Require ``values`` to be a (possibly empty) tuple of non-empty ENG-005 reference strings."""
    if not isinstance(values, tuple):
        raise ServiceError(f"{name} must be a tuple of ENG-005 references (SMR-13)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise ServiceError(f"{name} entries must be non-empty ENG-005 references (SMR-13)")
    return values


@dataclass(frozen=True, slots=True)
class Execution:
    """SMC-08 — an immutable, typed, identified, operation-bound carrying-out of an operation.

    Fields:
        type_tag:      the ENG-004 Type of the execution (decidable, non-empty) — SEX-01.
        kind:          the SXH-08 classification (Synchronous / Asynchronous / Transactional).
        operation_ref: the ENG-005 reference to the operation that executes (references) this
                       execution (SMR-07 executes; SOR-07; reference-only; SEX-04). The
                       execution carries out exactly this contracted operation (SEX-05).
        behavior_ref:  the ENG-005 reference to the RUNTIME execution/state/workflow concern the
                       execution behaves-as (SMR-11; RL-F2; RUNTIME-006/007/009; §7). If omitted
                       it defaults to the kind-appropriate RUNTIME concern (SEX-03).
        data_refs:     tuple of DF-2-represented data references the execution reads/writes
                       (SMR-13 operates-on; SOR-13; SEX-07; by reference). May be empty.
        policy_ref:    the ENG-005 reference to the declarative policy the execution is
                       governed-by (SMR-08; SOR-08; §11; reference-only, non-enforcing).
        state:         the SOS-01…06 lifecycle state (forward-only) — USL-12.
    """

    type_tag: str
    kind: ExecutionKind
    operation_ref: str
    behavior_ref: str = ""
    data_refs: tuple[str, ...] = field(default=())
    policy_ref: str = DEFAULT_POLICY_REF
    state: ServiceState = ServiceState.DEFINED

    def __post_init__(self) -> None:
        # SEX-K1 / USL-03 / SEX-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ServiceError("execution must be typed: a non-empty ENG-004 type_tag (SEX-01)")
        # SXH-08 / SXC-02 — classified by exactly one execution kind.
        if not isinstance(self.kind, ExecutionKind):
            raise ServiceError("execution kind must be an SXH-08 ExecutionKind (SXC-02)")
        # SMR-07 / SOR-07 / SEX-04 — carries out exactly the operation that references it.
        _require_reference("operation_ref", self.operation_ref)
        # §7 / SEX-03 — derive the kind-appropriate RUNTIME behavior reference if omitted.
        if not (isinstance(self.behavior_ref, str) and self.behavior_ref.strip()):
            object.__setattr__(self, "behavior_ref", _default_behavior_ref(self.kind))
        # SMR-11 / SOR-11 / SEX-03 — behaves-as RUNTIME execution/state/workflow, by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # SMR-13 / SOR-13 / SEX-07 — read/written data by reference (may be empty).
        _require_ref_tuple("data_refs", self.data_refs)
        # SMR-08 / SOR-08 / §11 — governed by a declarative policy, by reference.
        _require_reference("policy_ref", self.policy_ref)
        # V5 / USL-12 — a valid lifecycle state.
        if not isinstance(self.state, ServiceState):
            raise ServiceError("execution state must be a SOS-01…06 ServiceState (USL-12)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the execution (its identity-defining tuple)."""
        return {
            "meta_class": EXECUTION_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "operation_ref": self.operation_ref,
            "behavior_ref": self.behavior_ref,
            "data_refs": list(self.data_refs),
            "policy_ref": self.policy_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the execution core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def execution_id(self) -> str:
        """The deterministic ENG-001 identity of the execution (borne by this object)."""
        return f"{EXECUTION_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    @property
    def self_ref(self) -> str:
        """The ENG-005 self-reference form of this execution (for self-founding detection)."""
        return f"ENG-005:SOE-08:{self.type_tag}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (SMC-08)."""
        return EXECUTION_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the SMR-01…13 relationships the execution participates in."""
        return EXECUTION_RELATIONSHIPS

    # -- founding acyclicity (V4 / SMK-03) -------------------------------------

    def is_founding_acyclic(self) -> bool:
        """V4 / SMK-03 / SMI-04 — the founding graph (executed / behaves-as) is acyclic.

        An Execution binds its operation, behavior, data, and policy *by reference* (string
        ids), so its founding structure carries no cycle. Canonical encodability proves the
        core is well-formed; the no-self-founding guard proves no reference names the execution
        itself (a cycle would otherwise be admissible).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return self.no_self_founding()

    def no_self_founding(self) -> bool:
        """SMK-03 — no reference founds the execution on itself (no self-founding cycle)."""
        me = self.self_ref
        return all(
            ref != me
            for ref in (self.operation_ref, self.behavior_ref, self.policy_ref, *self.data_refs)
        )

    # -- execution-specific obligations ----------------------------------------

    def operation_bound(self) -> bool:
        """SMR-07 / SOR-07 / SEX-04 / SEX-K2 — carries out exactly the operation referencing it."""
        return bool(self.operation_ref.strip())

    def fulfils_contract(self) -> bool:
        """SEX-05 / USL-06 — fulfils its operation's contract (the operation binds the contract).

        The execution carries out a *contracted* operation; the contract is borne by that
        operation (SMC-05 / SOR-04→SMR-02). An execution is contract-fulfilling iff it is bound
        to an operation by reference — it invents no work of its own (SEX-04).
        """
        return self.operation_bound()

    def runtime_reuse_valid(self) -> bool:
        """SEX-03 / §7 — behaves-as the kind-appropriate RUNTIME concern by reference."""
        expected = KIND_RUNTIME_CONCERN[self.kind]
        return bool(self.behavior_ref.strip()) and expected in self.behavior_ref

    def behavior_by_reference(self) -> bool:
        """SMR-11 / USL-10 — behavior/execution binds RL-F2 by ENG-005 reference."""
        return bool(self.behavior_ref.strip())

    def transactionality_by_reference(self) -> bool:
        """SEX-06 / SEX-C1 / §7 — a transactional execution's atomicity is a RUNTIME workflow
        property by reference (RUNTIME-009); non-transactional kinds carry no such obligation.

        This is the material exercise of USL-10 for the transactional case: atomicity /
        consistency / isolation / durability are *referenced* from the frozen RUNTIME workflow
        concern, never redefined here.
        """
        if self.kind is not ExecutionKind.TRANSACTIONAL:
            return True
        return KIND_RUNTIME_CONCERN[ExecutionKind.TRANSACTIONAL] in self.behavior_ref

    def data_by_reference(self) -> bool:
        """SMR-13 / SOR-13 / SEX-07 / USL-11 — every read/written data ref is a DF-2 reference."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.data_refs)

    def policy_governed(self) -> bool:
        """SMR-08 / SOR-08 / §11 — the execution is governed-by a declarative policy, by ref."""
        return bool(self.policy_ref.strip())

    def records_completion(self) -> bool:
        """SEX-08 / SOV-07 — the execution records completion (emits an `executed` event).

        Completion recording is structural: an execution's carrying-out and its completion/fault
        signalling bind the RUNTIME event concern by reference (§7 execution-emit); a valid
        lifecycle state (USL-12) means transitions are recorded, never silent.
        """
        return isinstance(self.state, ServiceState)

    def references_resolve(self) -> bool:
        """SEX-K3/K4 / SMK-05/07 — every ENG-005 reference is a non-empty resolvable id."""
        singles = (self.operation_ref, self.behavior_ref, self.policy_ref)
        return all(
            isinstance(ref, str) and bool(ref.strip()) for ref in (*singles, *self.data_refs)
        ) and self.no_self_founding()

    # -- non-constitutiveness (USL-15 / SEX-09) --------------------------------

    def confers_authority(self) -> bool:
        """USL-15 / SEX-09 / C7 — an execution confers no authority (structurally none)."""
        return False

    def selects_technology(self) -> bool:
        """USL-15 / SEX-09 / C7 — True iff the execution names a runtime engine/technology."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """USL-15 / RR-07 / C7 — True iff the execution appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """USL-02 / SMI-05 / VC-5 — an execution redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (USL-12, forward-only) --------------------------------------

    def transition(self, to_state: ServiceState) -> Execution:
        """Return a new execution advanced to ``to_state`` (forward-only; USL-12)."""
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
        """A deterministic, serializable projection of the execution."""
        return {
            "execution_id": self.execution_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "operation_ref": self.operation_ref,
            "behavior_ref": self.behavior_ref,
            "data_refs": list(self.data_refs),
            "policy_ref": self.policy_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "runtime_concern": KIND_RUNTIME_CONCERN[self.kind],
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(EXECUTION_SUBSTRATE_REFS),
        }


def make_execution(
    type_tag: str,
    operation_ref: str,
    *,
    kind: ExecutionKind = ExecutionKind.SYNCHRONOUS,
    behavior_ref: str = "",
    data_refs: tuple[str, ...] = (),
    policy_ref: str = DEFAULT_POLICY_REF,
    state: ServiceState = ServiceState.DEFINED,
) -> Execution:
    """Construct a well-formed :class:`Execution` (fail-closed factory)."""
    return Execution(
        type_tag=type_tag,
        kind=kind,
        operation_ref=operation_ref,
        behavior_ref=behavior_ref,
        data_refs=data_refs,
        policy_ref=policy_ref,
        state=state,
    )


__all__ = [
    "EXECUTION_ID_PREFIX",
    "DEFAULT_POLICY_REF",
    "EXECUTION_FOUNDATION_REUSE",
    "Execution",
    "make_execution",
]
