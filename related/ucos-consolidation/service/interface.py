"""EC3-B11-U04 — The Universal Interface construct (SMC-04).

Realizes the meta-model concept **SMC-04 Interface** (SERVICE-005 §2; SERVICE-003 SOE-04;
SERVICE-008 §3):

    the **typed surface through which a service's operations are addressed** — the shape by
    which capability is requested, distinct from the endpoint (an abstract addressable
    locus) that locates it and from the contract that specifies it — an ENG-002 Object
    bearing an ENG-001 Identity, classified by an ENG-004 Type, that a service **exposes**
    (SMR-03, founding, acyclic), whose interaction behavior is a RUNTIME construct (SMR-11,
    by reference) and whose carried I/O references DF-2 data (SMR-13, by reference).

The construct is **additive over the CERTIFIED EC-1 foundation** and reuses it — and the
CERTIFIED SMC-01 Service / SMC-02 Capability / SMC-03 Contract — *by reference* (USL-02 /
SMI-05): identity and value-fidelity are derived through the EC-1 certified deterministic
encoding, so this module introduces **no second identity scheme and no parallel value
model**. It selects no technology / protocol / endpoint URL (USL-15 / SIN-05 / SIN-09) and
confers no authority.

An :class:`Interface` is *immutable* (ENG-002 objecthood), *typed* (ENG-004), *identified*
(ENG-001), *classified* (SXH-04 kind = interaction style, SIN-06), *exposed by a service*
(SMR-03, by reference), presents an addressable **operation surface** (SIN-03 sole-surface),
carries I/O by DF-2 reference (SMR-13 / SIN-07), is made available at an abstract **endpoint**
(SIN-05), binds interaction behavior by reference (SMR-11 / SIN-C5), and holds a *forward-only
lifecycle state* (SOS-01…06, USL-12; breaking change = new versioned interface, SIN-08).
Constructing an :class:`Interface` enforces SIN-K1/K4 and the laws USL-03/04/05/07/11
fail-closed: an ill-formed interface cannot be instantiated. It realizes/binds no Service,
Capability, Contract, Operation, Composition, Orchestration, Execution, Policy, or Security
object — those are separate units; this construct binds them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from engine.certification.contracts import canonical_json, content_hash
from service.interface_meta import (
    INTERFACE_META_CLASS,
    INTERFACE_RELATIONSHIPS,
    INTERFACE_SUBSTRATE_REFS,
    LIFECYCLE_ORDER,
    InterfaceKind,
    ServiceState,
)
from service.service import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    ServiceError,
)

#: The deterministic id prefix for a realized Interface (mirrors EC-1 UCOS-<KIND>-<hex16>).
INTERFACE_ID_PREFIX = "UCOS-INTERFACE"

#: The default abstract RUNTIME interaction binding an interface behaves-as (SMR-11; RL-F2).
DEFAULT_INTERACTION_REF = "ENG-005:RL-F2:runtime.interaction"

#: The map of frozen-foundation primitives this construct reuses *by reference*.
INTERFACE_FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the interface)",
    "ENG-003": "engine.certification.contracts.canonical_json (typed-surface value fidelity)",
    "ENG-004": "service.interface_meta.InterfaceKind + type_tag (ENG-004 typing, by reference)",
    "ENG-005": "reference identifiers (service/operation/io/endpoint/behavior refs; no new type)",
    "RL-F2": "interaction behavior bound by reference (SMR-11); no runtime concern redefined",
    "DF-2": "interface-carried I/O bound by reference to represented DATA (SMR-13); not redefined",
}


def _require_ref_tuple(name: str, values: Any) -> tuple[str, ...]:
    """Require ``values`` to be a tuple of non-empty ENG-005/DF-2 reference strings."""
    if not isinstance(values, tuple):
        raise ServiceError(f"{name} must be a tuple of ENG-005 references (SIN-03/07)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise ServiceError(f"{name} entries must be non-empty ENG-005 references (SIN-03/07)")
    return values


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(f"{name} must be a non-empty ENG-005 reference (SMR-03/11)")
    return value


@dataclass(frozen=True, slots=True)
class Interface:
    """SMC-04 — an immutable, typed, identified, addressable surface of a service.

    Fields:
        type_tag:     the ENG-004 Type of the interface (decidable, non-empty) — USL-07 / SIN-01.
        kind:         the SXH-04 interaction style (Request-Response / Event / Stream; SIN-06).
        service_ref:  the ENG-005 reference to the Service that exposes the interface
                      (SMR-03 exposes; SOR-03; founding, reference-only).
        operations:   tuple of ENG-005 references to the operations addressable through the
                      interface (SIN-03 sole-surface; presented under their contracts, SIN-04).
        io_refs:      tuple of DF-2-represented interface-carried I/O references (SMR-13 /
                      SIN-07 / USL-11; by reference).
        endpoint_ref: the abstract addressable-locus reference at which the interface is made
                      available (SIN-05 / SIN-C1); abstract only — no URL/protocol/port.
                      Empty ⇒ not yet made addressable.
        behavior_ref: the ENG-005 reference to the RUNTIME interaction behavior the interface
                      binds (SMR-11 behaves-as; RL-F2, by reference) — SIN-C5.
        state:        the SOS-01…06 lifecycle state (forward-only) — USL-12 / SIN-08.
    """

    type_tag: str
    kind: InterfaceKind
    service_ref: str
    operations: tuple[str, ...] = ()
    io_refs: tuple[str, ...] = ()
    endpoint_ref: str = ""
    behavior_ref: str = DEFAULT_INTERACTION_REF
    state: ServiceState = ServiceState.DEFINED

    def __post_init__(self) -> None:
        # SIN-K1 / USL-07 / SIN-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ServiceError("interface must be typed with a non-empty ENG-004 type_tag (USL-07)")
        # SXH-04 / SXC-02 / SIN-06 — classified by exactly one interaction-style kind.
        if not isinstance(self.kind, InterfaceKind):
            raise ServiceError("interface kind must be an SXH-04 InterfaceKind (SXC-02)")
        # SMR-03 / SOR-03 — an interface is exposed by a service, bound by reference.
        _require_reference("service_ref", self.service_ref)
        # SIN-03 — the addressable operation surface (may be empty at DEFINED; refs well-formed).
        _require_ref_tuple("operations", self.operations)
        # SMR-13 / SIN-07 / USL-11 — carried I/O declared by DF-2 reference.
        _require_ref_tuple("io_refs", self.io_refs)
        # SIN-05 / SIN-C1 — endpoint is an abstract locus reference (optional string).
        if not isinstance(self.endpoint_ref, str):
            raise ServiceError("endpoint_ref must be an abstract-locus reference string (SIN-05)")
        # SMR-11 / SIN-C5 — interaction behavior bound to RL-F2 by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # V5 / USL-12 — a valid lifecycle state.
        if not isinstance(self.state, ServiceState):
            raise ServiceError("interface state must be a SOS-01…06 ServiceState (USL-12)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the interface (its identity-defining tuple)."""
        return {
            "meta_class": INTERFACE_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "service_ref": self.service_ref,
            "operations": list(self.operations),
            "io_refs": list(self.io_refs),
            "endpoint_ref": self.endpoint_ref,
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the interface core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def interface_id(self) -> str:
        """The deterministic ENG-001 identity of the interface (borne by this object)."""
        return f"{INTERFACE_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (SMC-04)."""
        return INTERFACE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the SMR-01…13 relationships the interface participates in."""
        return INTERFACE_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / SMK-03 / SIN-C3 — the founding graph (exposes) is acyclic."""
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    # -- interface-specific obligations ----------------------------------------

    def exposed_by_service(self) -> bool:
        """SMR-03 / SOR-03 / SIN — the interface is exposed by a service (by reference)."""
        return bool(self.service_ref.strip())

    def is_sole_surface(self) -> bool:
        """USL-07 / SIN-03 — the interface presents at least one addressable operation.

        An interface exposing no operation exposes no surface; a well-formed interface
        declares the operations addressable only through it (sole-surface discipline).
        """
        return bool(self.operations) and all(
            isinstance(o, str) and bool(o.strip()) for o in self.operations
        )

    def io_is_data(self) -> bool:
        """USL-11 / SIN-07 / SMR-13 — every carried I/O reference is a non-empty DF-2 reference."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.io_refs)

    def endpoint_is_abstract(self) -> bool:
        """SIN-05 / SIN-C1 — the endpoint, when present, is a non-blank abstract locus.

        Concrete-locator detection (URL/protocol/port) is enforced by
        :meth:`selects_technology`; here we require a present endpoint to be non-blank.
        """
        return self.endpoint_ref == "" or bool(self.endpoint_ref.strip())

    def behavior_by_reference(self) -> bool:
        """SMR-11 / SIN-C5 — interaction behavior binds RL-F2 by a non-empty reference."""
        return bool(self.behavior_ref.strip())

    def references_resolve(self) -> bool:
        """SMK-05 / SIN-K4 — every ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (self.service_ref, self.behavior_ref)
        )

    # -- non-constitutiveness (USL-15 / SIN-09) --------------------------------

    def confers_authority(self) -> bool:
        """USL-15 / SIN-09 / C7 — an interface confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """USL-15 / SIN-05 / SIN-09 / C7 — True iff the interface names a technology/URL."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """USL-15 / RR-07 / C7 — True iff the interface appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """USL-02 / SMI-05 / VC-5 — an interface redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (USL-12 / SIN-08, forward-only) -----------------------------

    def transition(self, to_state: ServiceState) -> Interface:
        """Return a new interface advanced to ``to_state`` (forward-only; USL-12 / SIN-08)."""
        if not isinstance(to_state, ServiceState):
            raise ServiceError("target state must be a SOS-01…06 ServiceState (USL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise ServiceError(
                f"lifecycle is forward-only (USL-12 / SIN-08): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the interface."""
        return {
            "interface_id": self.interface_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "service_ref": self.service_ref,
            "operations": list(self.operations),
            "io_refs": list(self.io_refs),
            "endpoint_ref": self.endpoint_ref,
            "behavior_ref": self.behavior_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(INTERFACE_SUBSTRATE_REFS),
        }


def make_interface(
    type_tag: str,
    service_ref: str,
    *,
    kind: InterfaceKind = InterfaceKind.REQUEST_RESPONSE,
    operations: tuple[str, ...] = (),
    io_refs: tuple[str, ...] = (),
    endpoint_ref: str = "",
    behavior_ref: str = DEFAULT_INTERACTION_REF,
    state: ServiceState = ServiceState.DEFINED,
) -> Interface:
    """Construct a well-formed :class:`Interface` (fail-closed factory)."""
    return Interface(
        type_tag=type_tag,
        kind=kind,
        service_ref=service_ref,
        operations=operations,
        io_refs=io_refs,
        endpoint_ref=endpoint_ref,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "INTERFACE_ID_PREFIX",
    "DEFAULT_INTERACTION_REF",
    "INTERFACE_FOUNDATION_REUSE",
    "Interface",
    "make_interface",
]
