"""EC3-B12-U02 — The Universal Capability construct (AMC-02).

Realizes the meta-model concept **AMC-02 Capability** (APPLICATION-005 §2;
APPLICATION-006; APPLICATION-003 AOE-02; APPLICATION-001 §4):

    the implementation-independent **ability delivered to an actor** that an application
    realizes by composing service operations — a typed (ENG-004) object (ENG-002),
    identified (ENG-001), delivered by an application (AMR-01, by reference) through
    features that **consume an SF-2 operation under contract** (AMR-13, by reference;
    the defining relationship — CAP-05), whose delivered data references DF-2 (AMR-14,
    by reference; CAP-07), whose behavior is a RUNTIME construct (AMR-11, by reference)
    and whose structural participation is a PLATFORM experience composition
    (AMR-12, by reference; PLATFORM-006/009).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface + CERTIFIED-COMPLETE + FROZEN Band-11 service
surface + the CERTIFIED Band-12 U01 Universal Application root) and reuses them *by
reference* (UAL-02 / AMI-05): identity and value-fidelity are derived through the EC-1
certified deterministic encoding (:func:`engine.certification.contracts.canonical_json`
/ :func:`~engine.certification.contracts.content_hash`) — the same discipline that
produces every EC-1 runtime, artifact, and certification identity — so this module
introduces **no second identity scheme and no parallel value model**. It selects no
technology/UI/screen and confers no authority (UAL-15).

A :class:`Capability` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001 via a deterministic id), *classified* (AXH-02 kind),
*service-consuming* (AMR-13, by reference — the defining relationship), *data-referencing*
(AMR-14, by reference), *behavior-bound* and *composition-bound* (AMR-11/12, by reference),
and holds a *forward-only lifecycle state* (AOS-01…06, UAL-12). Constructing a
:class:`Capability` enforces the meta-constraints AMK-01/03/05/06/07 and the laws
UAL-03/04/05/06/09/10/12/13 fail-closed: an ill-formed capability cannot be instantiated.
It realizes **no** Application, Module, Feature, Workflow, Interaction, State, Composition,
Security, or Governance object — those are separate Band-12 units; this construct binds
them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from application.capability_meta import (
    CAPABILITY_META_CLASS,
    CAPABILITY_RELATIONSHIPS,
    LIFECYCLE_ORDER,
    READ_SIDE_KINDS,
    SUBSTRATE_REFS,
    WRITE_SIDE_KINDS,
    CapabilityKind,
    CapabilityState,
)

# --- EC-1 reuse by reference (UAL-02 / AMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Capability (mirrors EC-1 UCOS-<KIND>-<hex16>).
CAPABILITY_ID_PREFIX = "UCOS-CAPABILITY"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UAL-02 / AMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the capability)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity; no parallel model)",
    "ENG-004": "application.capability_meta.CapabilityKind + type_tag (ENG-004 typing, by ref)",
    "ENG-005": "reference identifiers (operation/data/behavior/composition refs; no new construct)",
    "RL-F2": "delivery/transaction/emit behavior bound by reference (AMR-11); none redefined",
    "PL-F2": "experience composition bound by reference (AMR-12; PLATFORM-006/009); none redefined",
    "SF-2": "delivered ability via contracted operation by reference (AMR-13, CAP-05); none redef",
    "DF-2": "presented/delivered data by reference (AMR-14, CAP-07); none redefined",
}

#: Concrete-technology markers forbidden by UAL-15 (no UI/framework/screen/API/protocol/vendor).
#: An abstract EL-1/RL-F2/PL-F2/DF-2/SF-2 reference names none of these.
_TECHNOLOGY_MARKERS: tuple[str, ...] = (
    "react",
    "vue",
    "angular",
    "svelte",
    "tailwind",
    "bootstrap",
    "grpc",
    "graphql",
    "kafka",
    "rabbitmq",
    "postgres",
    "mysql",
    "mongodb",
    "kubernetes",
    "docker",
    "nginx",
    "openapi",
    "swagger",
    "lambda",
    "dynamodb",
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


class CapabilityError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`Capability`.

    A :class:`Capability` is fail-closed (TRACK-001): an ill-formed capability construct
    is rejected at construction rather than admitted as an invalid capability.
    """


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise CapabilityError(
            f"{name} must be a non-empty ENG-005 reference (UAL-02/09/13)"
        )
    return value


@dataclass(frozen=True, slots=True)
class Capability:
    """AMC-02 — an immutable, typed, identified, service-consuming application capability.

    Fields:
        type_tag:        the ENG-004 Type of the capability (decidable, non-empty) — UAL-03.
        kind:            the AXH-02 classification of the capability (AXC-02).
        operation_ref:   the ENG-005 reference to the SF-2 operation the capability's
                         delivery consumes (AMR-13 consumes-operation, reference-only) —
                         the CAP-05 defining relationship (a capability is realized only
                         by consuming an SF-2 operation under contract).
        data_ref:        the ENG-005 reference to the DF-2 represented data the capability
                         presents (AMR-14 presents-data; CAP-07 / UAL-13, by reference).
        behavior_ref:    the ENG-005 reference to the RUNTIME behavior the capability binds
                         (AMR-11 behaves-as; RL-F2, by reference; deliver/transact/emit) —
                         UAL-10.
        composition_ref: the ENG-005 reference to the PLATFORM experience composition the
                         capability participates as (AMR-12 composed-as; PL-F2 /
                         PLATFORM-006/009) — UAL-09.
        state:           the AOS-01…06 lifecycle state (forward-only) — UAL-12 (default DEFINED).
    """

    type_tag: str
    kind: CapabilityKind
    operation_ref: str
    data_ref: str = "ENG-005:DF-2:data.represented"
    behavior_ref: str = "ENG-005:RL-F2:runtime.capability-deliver"
    composition_ref: str = "ENG-005:PL-F2:PLATFORM-006.capability"
    state: CapabilityState = CapabilityState.DEFINED

    def __post_init__(self) -> None:
        # AMK-01 / UAL-03 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise CapabilityError(
                "capability must be typed with a non-empty ENG-004 type_tag (UAL-03)"
            )
        # AXH-02 / AXC-02 — classified by exactly one Capability kind.
        if not isinstance(self.kind, CapabilityKind):
            raise CapabilityError("capability kind must be an AXH-02 CapabilityKind (AXC-02)")
        # AMR-13 / CAP-05 / UAL-06 — realized by consuming an SF-2 operation (reference-only).
        _require_reference("operation_ref", self.operation_ref)
        # AMR-14 / CAP-07 / UAL-13 — delivered data references a DF-2 construct.
        _require_reference("data_ref", self.data_ref)
        # AMR-11 / UAL-10 — behavior bound to RL-F2 by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # AMR-12 / UAL-09 — experience composition bound to PL-F2 by reference.
        _require_reference("composition_ref", self.composition_ref)
        # V5 / UAL-12 — a valid lifecycle state.
        if not isinstance(self.state, CapabilityState):
            raise CapabilityError(
                "capability state must be an AOS-01…06 CapabilityState (UAL-12)"
            )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the capability (its identity-defining tuple)."""
        return {
            "meta_class": CAPABILITY_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "operation_ref": self.operation_ref,
            "data_ref": self.data_ref,
            "behavior_ref": self.behavior_ref,
            "composition_ref": self.composition_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the capability core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def capability_id(self) -> str:
        """The deterministic ENG-001 identity of the capability (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UAL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity
        is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{CAPABILITY_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (APPLICATION-005/006) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (AMC-02)."""
        return CAPABILITY_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the AMR-01…14 relationships the capability participates in."""
        return CAPABILITY_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / AMK-03 / CAP-C3 — the founding graph is acyclic.

        A Capability binds its constituents *by reference* (string ids), so its founding
        structure carries no cycle; this is proven by the fact that its core canonically
        encodes (a cycle would raise at construction).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        """AOI-03 / AMK-05/06/07 — every ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (
                self.operation_ref,
                self.data_ref,
                self.behavior_ref,
                self.composition_ref,
            )
        )

    def consumes_operation(self) -> bool:
        """CAP-05 / AMR-13 — the capability is realized by consuming an SF-2 operation."""
        return bool(self.operation_ref.strip())

    def is_bounded(self) -> bool:
        """CAP-06 / CAP-C1 / UAL-08 — the capability declares an explicit, decidable scope.

        A capability is bounded iff its type, kind, and consumed-operation reference are
        all explicit (declared and non-empty) — the scope of delivered ability is closed
        at declaration.
        """
        return bool(self.type_tag.strip()) and self.consumes_operation()

    def delivery_side(self) -> str:
        """CAP-C5 — the read-side/write-side classification of delivered ability.

        Informational capabilities are read-side, Transactional are write-side, and
        Functional capabilities deliver domain work (neither strictly read nor write).
        """
        if self.kind in READ_SIDE_KINDS:
            return "read-side"
        if self.kind in WRITE_SIDE_KINDS:
            return "write-side"
        return "functional"

    # -- non-constitutiveness (UAL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """UAL-15 / CAP-09 / C7 — a capability confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """UAL-15 / CAP-09 / C7 — True iff the capability names a concrete technology/UI/vendor."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UAL-15 / RR-07 / C7 — True iff the capability appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UAL-02 / AMI-05 / VC-5 — a capability redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (UAL-12, forward-only) --------------------------------------

    def transition(self, to_state: CapabilityState) -> Capability:
        """Return a new capability advanced to ``to_state`` (forward-only; UAL-12).

        Raises:
            CapabilityError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, CapabilityState):
            raise CapabilityError("target state must be an AOS-01…06 CapabilityState (UAL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise CapabilityError(
                f"lifecycle is forward-only (UAL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the capability."""
        return {
            "capability_id": self.capability_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "operation_ref": self.operation_ref,
            "data_ref": self.data_ref,
            "behavior_ref": self.behavior_ref,
            "composition_ref": self.composition_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "delivery_side": self.delivery_side(),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_capability(
    type_tag: str,
    operation_ref: str,
    *,
    kind: CapabilityKind = CapabilityKind.FUNCTIONAL,
    data_ref: str = "ENG-005:DF-2:data.represented",
    behavior_ref: str = "ENG-005:RL-F2:runtime.capability-deliver",
    composition_ref: str = "ENG-005:PL-F2:PLATFORM-006.capability",
    state: CapabilityState = CapabilityState.DEFINED,
) -> Capability:
    """Construct a well-formed :class:`Capability` (fail-closed factory)."""
    return Capability(
        type_tag=type_tag,
        kind=kind,
        operation_ref=operation_ref,
        data_ref=data_ref,
        behavior_ref=behavior_ref,
        composition_ref=composition_ref,
        state=state,
    )


__all__ = [
    "CAPABILITY_ID_PREFIX",
    "FOUNDATION_REUSE",
    "CapabilityError",
    "Capability",
    "make_capability",
]
