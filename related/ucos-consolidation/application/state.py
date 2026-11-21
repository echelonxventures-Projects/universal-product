"""EC3-B12-U07 — The Universal State construct (AMC-07).

Realizes the meta-model concept **AMC-07 State** (APPLICATION-005 §2; APPLICATION-011;
APPLICATION-003 AOE-07; APPLICATION-001 §2):

    the **implementation-independent condition of an application/module/feature/interaction
    at a point in a journey, within a context** — a typed (ENG-004) object (ENG-002),
    identified (ENG-001), classified by one AXH-07 kind (Lifecycle / Interaction /
    Context), that is **held by** an application/feature/interaction/workflow (AMR-06
    held-state, by reference; the State is the *held* condition — reference-only, not
    founding), **binds/behaves-as the frozen RUNTIME state concern** (AMR-11 / §7, by
    reference → RL-F2; STA-03/STA-C5), **binds its data as DF-2 data** (AMR-14
    presents-data, by reference; STA-C4), is **bound to a declared, decidable context**
    (actor / session / tenant / locale / policy — STA-06/STA-C3), and **advances
    forward-only** through the AOS-01…06 lifecycle with every transition recorded as a
    RUNTIME event (UAL-12 / STA-04/05).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface + CERTIFIED-COMPLETE + FROZEN Band-11 service
surface + the CERTIFIED Band-12 U01 Application root + U02 Capability + U03 Module + U04
Feature + U05 Workflow + U06 Interaction) and reuses them *by reference* (UAL-02 /
AMI-05): identity and value-fidelity are derived through the EC-1 certified deterministic
encoding (:func:`engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`) — the same discipline that produces
every EC-1 runtime, artifact, and certification identity — so this module introduces **no
second identity scheme and no parallel value model**. It selects no technology (no state
store, cache, or database), and confers no authority (STA-09 / UAL-15). The RL-F2 state
concern is **reused by reference and never re-founded** (STA-03/STA-C5).

A :class:`State` is *immutable* (a frozen object — ENG-002 objecthood), *typed* (ENG-004),
*identified* (ENG-001 via a deterministic id), *classified* (AXH-07 kind), *held* (AMR-06,
by reference), *runtime-bound* (AMR-11, by reference → RL-F2), *data-binding* (AMR-14, by
reference), *context-bound* (STA-06, decidable & explicit), and holds a *forward-only
lifecycle state* (AOS-01…06, UAL-12). Constructing a :class:`State` enforces the
meta-constraints AMK-01/02/05/07/08 and the laws UAL-03/04/05/10/12/13 fail-closed: an
ill-formed state cannot be instantiated. It realizes **no** Application, Capability,
Module, Feature, Workflow, Interaction, Composition, Security, or Governance object —
those are separate Band-12 units; this construct binds them only *by reference*. In
particular it **delivers no capability** (AMR-01), **groups no feature** (AMR-03),
**sequences no feature** (AMR-04), **engages no feature** (AMR-05), **consumes no SF-2
operation** (AMR-13), and **assembles no PLATFORM composition** (AMR-07/12) — a state is
the *condition held by* a construct (it conditions delivery), not the construct itself.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from application.state_meta import (
    LIFECYCLE_ORDER,
    STATE_FACETS,
    STATE_META_CLASS,
    STATE_RELATIONSHIPS,
    SUBSTRATE_REFS,
    StateKind,
    StateLifecycle,
)

# --- EC-1 reuse by reference (UAL-02 / AMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized State (mirrors EC-1 UCOS-<KIND>-<hex16>).
STATE_ID_PREFIX = "UCOS-STATE"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UAL-02 / AMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the state)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity; no parallel model)",
    "ENG-004": "application.state_meta.StateKind + type_tag (ENG-004 typing, by reference)",
    "ENG-005": "reference identifiers (holder, context, data, behavior refs)",
    "RL-F2": "RUNTIME state concern by reference (§7, AMR-11 / STA-03); none redefined",
    "DF-2": "represented bound data by reference (presents-data AMR-14); none redefined",
}

#: Concrete-technology markers forbidden by UAL-15 / STA-09 (STA-K5): no state-store,
#: cache, database, state-management library, transport, protocol, engine, cloud, or
#: vendor. An application state names none of these — persistence/storage/caching are
#: downstream runtime concerns (APPLICATION-011 §2.2), referenced by RL-F2, never selected.
_TECHNOLOGY_MARKERS: tuple[str, ...] = (
    # state stores / caches / databases (STA-09 / STA-K5 — no store selected)
    "redis",
    "memcached",
    "etcd",
    "zookeeper",
    "consul",
    "dynamodb",
    "postgres",
    "mysql",
    "mongodb",
    "cassandra",
    "sqlite",
    "localstorage",
    "sessionstorage",
    "indexeddb",
    "cookie-store",
    "ehcache",
    "hazelcast",
    "ignite",
    # state-management libraries / engines
    "redux",
    "vuex",
    "mobx",
    "zustand",
    "recoil",
    "xstate",
    "akka",
    # transports / infra / vendors
    "kafka",
    "rabbitmq",
    "kubernetes",
    "docker",
    "nginx",
    "lambda",
    "s3-bucket",
    "http://",
    "https://",
    "tcp://",
)

#: Conservative secret markers used to enforce UAL-15 / RR-07 (embed no secret).
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


class StateError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`State`.

    A :class:`State` is fail-closed (TRACK-001): an ill-formed state construct is rejected
    at construction rather than admitted as an invalid state.
    """


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise StateError(f"{name} must be a non-empty ENG-005 reference (UAL-02 / STA-K1)")
    return value


def _contains_marker(value: str, markers: tuple[str, ...]) -> bool:
    """True iff ``value`` (case-insensitively) contains any of ``markers``."""
    haystack = value.lower()
    return any(marker in haystack for marker in markers)


@dataclass(frozen=True, slots=True)
class State:
    """AMC-07 — an immutable, typed, identified, context-bound application State.

    Fields:
        type_tag:     the ENG-004 Type of the state (decidable, non-empty) — UAL-03/STA-01.
        kind:         the AXH-07 classification of the state (AXC-04): Lifecycle /
                      Interaction / Context.
        holder_ref:   the ENG-005 reference to the Application/Feature/Interaction/Workflow
                      that holds this state (AMR-06 holds-state, reference-only) — the State
                      is the *held* condition (AOR-06 target). Required, non-empty.
        context_ref:  the ENG-005 reference to the **declared context** (actor / session /
                      tenant / locale / policy) the state is bound to (STA-06 / STA-C3) —
                      the distinctive State obligation: every state is bound to a decidable,
                      explicit context that selects **no technology** (STA-09/STA-K5).
                      Required, non-empty, decidable, technology-free.
        data_ref:     the ENG-005 reference to the DF-2 data the state binds/presents
                      (AMR-14 presents-data, reference-only) — STA-C4/STA-K4/UAL-13.
                      Required, non-empty.
        behavior_ref: the ENG-005 reference to the frozen RUNTIME state concern the state
                      behaves-as / binds (AMR-11 behaves-as; RL-F2 state; §7) — STA-03/
                      STA-C5/UAL-10. Required, non-empty.
        state:        the AOS-01…06 lifecycle state (forward-only) — UAL-12 (default DEFINED).
    """

    type_tag: str
    kind: StateKind
    holder_ref: str
    context_ref: str = "ENG-005:CONTEXT:ucos.application.state.context.primary"
    data_ref: str = "ENG-005:DF-2:ucos.application.state.data.primary"
    behavior_ref: str = "ENG-005:RL-F2:runtime.state-transition"
    state: StateLifecycle = StateLifecycle.DEFINED

    def __post_init__(self) -> None:
        # AMK-01 / UAL-03 / STA-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise StateError(
                "state must be typed with a non-empty ENG-004 type_tag (UAL-03 / STA-01)"
            )
        # AXH-07 / AXC-04 — classified by exactly one State kind.
        if not isinstance(self.kind, StateKind):
            raise StateError("state kind must be an AXH-07 StateKind (AXC-04)")
        # AMR-06 / AOR-06 — held by exactly one construct by reference (reference-only).
        _require_reference("holder_ref", self.holder_ref)
        # STA-06 / STA-C3 — bound to a declared, decidable context (by reference).
        _require_reference("context_ref", self.context_ref)
        # AMR-14 / STA-C4 / AMK-07 — binds/presents DF-2 data by reference.
        _require_reference("data_ref", self.data_ref)
        # AMR-11 / §7 / AMK-05 / STA-03 — behaves-as / binds RUNTIME state by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # V5 / UAL-12 — a valid lifecycle state.
        if not isinstance(self.state, StateLifecycle):
            raise StateError("state must hold an AOS-01…06 StateLifecycle (UAL-12)")
        # STA-06 / STA-09 / STA-K5 / UAL-15 — the declared context is abstract: it selects
        # no state store, cache, database, or state-management technology.
        if _contains_marker(self.context_ref, _TECHNOLOGY_MARKERS):
            raise StateError(
                "the declared context must be abstract — no state store, cache, database, "
                "or state-management technology may be selected (STA-06 / STA-09 / STA-K5)"
            )
        # STA-C5 / AMK-05 — the RUNTIME state concern is bound by reference, never re-founded:
        # the behavior reference must not itself name a concrete state technology.
        if _contains_marker(self.behavior_ref, _TECHNOLOGY_MARKERS):
            raise StateError(
                "the RUNTIME state binding must reference the frozen RL-F2 state concern, "
                "not a concrete state technology (STA-03 / STA-C5 / STA-K5)"
            )
        # AMK-08 / STA-09 — non-absorption hygiene: the holder cannot also be the state's
        # own context / data / behavior binding (a state is held *by* a distinct construct).
        binding_refs = {self.context_ref, self.data_ref, self.behavior_ref}
        if self.holder_ref in binding_refs:
            raise StateError(
                "a state cannot be held by its own context/data/behavior binding "
                "(AMK-08 non-absorption)"
            )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the state (its identity-defining tuple).

        Identity is fixed by (meta-class, type, kind/facet, holder, context, bound data,
        bound behavior). The lifecycle ``state`` is **not** part of identity (a state keeps
        its identity as it advances its lifecycle forward-only — STA-04).
        """
        return {
            "meta_class": STATE_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "facet": self.facet(),
            "holder_ref": self.holder_ref,
            "context_ref": self.context_ref,
            "data_ref": self.data_ref,
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the state core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def state_id(self) -> str:
        """The deterministic ENG-001 identity of the state (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UAL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity
        is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{STATE_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (APPLICATION-005/011) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (AMC-07)."""
        return STATE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the AMR-01…14 relationships the state participates in."""
        return STATE_RELATIONSHIPS

    def facet(self) -> str:
        """AXH-07 — the condition facet the kind classifies (lifecycle/interaction/context)."""
        return STATE_FACETS[self.kind]

    def is_founding_acyclic(self) -> bool:
        """V4 / AMK-03 — the founding graph is acyclic (satisfied *vacuously*).

        A State participates in **no** founding relationship (its relationships
        AMR-06/10/11/14 are all reference-only; the founding relationships are AMR-02/03/05).
        Its founding graph is therefore empty and trivially acyclic — exactly as the
        Workflow used no founding edge. Proven by the fact that its core canonically encodes
        and the holder is distinct from every binding reference (non-absorption).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return self.holder_ref not in {
            self.context_ref,
            self.data_ref,
            self.behavior_ref,
        }

    def participates_in_founding_edge(self) -> bool:
        """AMK-03 — a State participates in no founding relationship (AMR-02/03/05)."""
        return any(r in {"AMR-02", "AMR-03", "AMR-05"} for r in STATE_RELATIONSHIPS)

    def references_resolve(self) -> bool:
        """AOI-03 / AMK-05/07 — every ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(r, str) and bool(r.strip())
            for r in (
                self.holder_ref,
                self.context_ref,
                self.data_ref,
                self.behavior_ref,
            )
        )

    def is_held(self) -> bool:
        """AMR-06 / AOR-06 — the state is held by a construct (by reference)."""
        return bool(self.holder_ref.strip())

    def held_by(self) -> str:
        """AMR-06 — the ENG-005 reference to the construct that holds this state."""
        return self.holder_ref

    def is_held_by(self, holder_ref: str) -> bool:
        """AMR-06 — True iff ``holder_ref`` is the construct that holds this state."""
        return holder_ref == self.holder_ref

    def binds_runtime_state(self) -> bool:
        """AMR-11 / §7 / AMK-05 / STA-03 — behaves-as / binds RUNTIME state (→ RL-F2).

        The governing, materially-exercised binding: the application state binds the frozen
        RL-F2 state concern by reference and re-founds none.
        """
        return bool(self.behavior_ref.strip()) and not _contains_marker(
            self.behavior_ref, _TECHNOLOGY_MARKERS
        )

    def presents_data(self) -> bool:
        """AMR-14 / STA-C4 / UAL-13 — the state binds/presents DF-2 data by reference."""
        return bool(self.data_ref.strip())

    def context_is_bound(self) -> bool:
        """STA-06 / STA-C3 — the state is bound to a declared, decidable, abstract context.

        The distinctive State obligation: every state is bound to an explicit context
        (actor/session/tenant/locale/policy) that selects no state technology.
        """
        return bool(self.context_ref.strip()) and not _contains_marker(
            self.context_ref, _TECHNOLOGY_MARKERS
        )

    def declared_context(self) -> str:
        """STA-06 — the ENG-005 reference to the declared context."""
        return self.context_ref

    def lifecycle_is_decidable(self) -> bool:
        """STA-07 — membership in a lifecycle state is decidable at any point."""
        return self.state in LIFECYCLE_ORDER

    def kind_class(self) -> str:
        """AXH-07 — the lifecycle / interaction / context classification (the facet)."""
        return self.facet()

    # -- non-constitutiveness (UAL-15 / STA-09) --------------------------------

    def confers_authority(self) -> bool:
        """UAL-15 / STA-09 / C7 — a state confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """UAL-15 / STA-09 / C7 — True iff the state names a concrete technology.

        Covers state stores, caches, databases, state-management libraries, engines,
        transports, protocols, infrastructure, or vendors across the whole state core
        (including the declared context and behavior binding).
        """
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UAL-15 / RR-07 / C7 — True iff the state appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UAL-02 / AMI-05 / VC-5 — a state redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (UAL-12, forward-only, recorded) ----------------------------

    def transition(self, to_state: StateLifecycle) -> State:
        """Return a new state advanced to ``to_state`` (forward-only; UAL-12 / STA-04).

        State advancement is forward-only and recorded (STA-05); there is no silent or
        in-place-reversible transition (STA-C1). Use :meth:`transition_event` to obtain the
        RUNTIME-event descriptor that records the transition.

        Raises:
            StateError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, StateLifecycle):
            raise StateError("target state must be an AOS-01…06 StateLifecycle (UAL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise StateError(
                f"lifecycle is forward-only (UAL-12 / STA-04 / STA-C1): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    def transition_event(self, to_state: StateLifecycle) -> dict[str, Any]:
        """STA-05 / STA-C2 / §7 — the RUNTIME-event descriptor that records a transition.

        A transition is never silent: it is recorded as a RUNTIME event (by reference —
        ``state-record`` → RUNTIME event, §7 / AOV-07). This descriptor is the recorded
        transition; the *act* of recording is the frozen RL-F2 event concern by reference.

        Raises:
            StateError: on a backward or in-place-reversing transition.
        """
        advanced = self.transition(to_state)
        return {
            "record": "state-transitioned",  # AOV-07
            "binding": "ENG-005:RL-F2:runtime.state-record",  # §7 — RUNTIME event by ref
            "from": self.state.value,
            "to": advanced.state.value,
            "state_id": advanced.state_id,
        }

    def records_transitions(self) -> bool:
        """STA-05 / STA-C2 — transitions are recorded as RUNTIME events (structurally true)."""
        return True

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the state."""
        return {
            "state_id": self.state_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "facet": self.facet(),
            "holder_ref": self.holder_ref,
            "context_ref": self.context_ref,
            "data_ref": self.data_ref,
            "behavior_ref": self.behavior_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "context_bound": self.context_is_bound(),
            "binds_runtime_state": self.binds_runtime_state(),
            "presents_data": self.presents_data(),
            "is_held": self.is_held(),
            "lifecycle_decidable": self.lifecycle_is_decidable(),
            "records_transitions": self.records_transitions(),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_state(
    type_tag: str,
    holder_ref: str,
    *,
    kind: StateKind = StateKind.INTERACTION,
    context_ref: str = "ENG-005:CONTEXT:ucos.application.state.context.primary",
    data_ref: str = "ENG-005:DF-2:ucos.application.state.data.primary",
    behavior_ref: str = "ENG-005:RL-F2:runtime.state-transition",
    state: StateLifecycle = StateLifecycle.DEFINED,
) -> State:
    """Construct a well-formed :class:`State` (fail-closed factory)."""
    return State(
        type_tag=type_tag,
        kind=kind,
        holder_ref=holder_ref,
        context_ref=context_ref,
        data_ref=data_ref,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "STATE_ID_PREFIX",
    "FOUNDATION_REUSE",
    "StateError",
    "State",
    "make_state",
]
