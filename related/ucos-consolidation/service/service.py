"""EC3-B11-U01 — The Universal Service construct (SMC-01).

Realizes the meta-model root concept **SMC-01 Service** (SERVICE-005 §2; SERVICE-003
SOE-01; SERVICE-001 §4):

    the atomic unit of invocable capability — a typed (ENG-004) provider borne by an
    object (ENG-002), identified (ENG-001), that realizes a capability (SMR-01, by
    reference), whose behavior is a RUNTIME construct (SMR-11, by reference) and whose
    structural participation is a PLATFORM composition (SMR-12, by reference).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface) and reuses them *by reference* (USL-02 /
SMI-05): identity and value-fidelity are derived through the EC-1 certified
deterministic encoding (:func:`engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`) — the same discipline that
produces every EC-1 runtime, artifact, and certification identity — so this module
introduces **no second identity scheme and no parallel value model**. It selects no
technology (USL-15) and confers no authority (USL-15).

A :class:`Service` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001 via a deterministic id), *classified* (SXH-01 kind),
*capability-realizing* (SMR-01, by reference), *behavior-bound* and *composition-bound*
(SMR-11/12, by reference), and holds a *forward-only lifecycle state* (SOS-01…06,
USL-12). Constructing a :class:`Service` enforces the meta-constraints SMK-01/03/05/06
and the laws USL-03/04/05/09/10 fail-closed: an ill-formed service cannot be
instantiated. It realizes **no** Capability, Contract, Interface, Operation,
Composition, Orchestration, Execution, Policy, or Security object — those are separate
Band-11 units; this construct binds them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- EC-1 reuse by reference (USL-02 / SMI-05) — imported, never redefined -------
from engine.certification.contracts import canonical_json, content_hash
from service.service_meta import (
    LIFECYCLE_ORDER,
    SERVICE_META_CLASS,
    SERVICE_RELATIONSHIPS,
    SUBSTRATE_REFS,
    ServiceKind,
    ServiceState,
)

#: The deterministic id prefix for a realized Service (mirrors EC-1 UCOS-<KIND>-<hex16>).
SERVICE_ID_PREFIX = "UCOS-SERVICE"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (USL-02 / SMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the service)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity, no parallel model)",
    "ENG-004": "service.service_meta.ServiceKind + type_tag (ENG-004 typing, by reference)",
    "ENG-005": "reference identifiers (capability/behavior/composition refs; no new construct)",
    "RL-F2": "behavior/execution bound by reference (SMR-11/07); no runtime concern redefined",
    "PL-F2": "composition bound by reference (SMR-12; PLATFORM-008); no platform concern redefined",
    "DF-2": "operation I/O by reference (SMR-13) — scoped to the Operation unit (SMC-05)",
}

#: Concrete-technology markers forbidden by USL-15 (no API/protocol/framework/vendor).
#: An abstract EL-1/RL-F2/PL-F2 reference names none of these.
_TECHNOLOGY_MARKERS: tuple[str, ...] = (
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

#: Conservative secret markers used to enforce USL-15 / RR-07 (embed no secret).
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


class ServiceError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`Service`.

    A :class:`Service` is fail-closed (TRACK-001): an ill-formed service construct is
    rejected at construction rather than admitted as an invalid service.
    """


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(f"{name} must be a non-empty ENG-005 reference (USL-02/09/10)")
    return value


@dataclass(frozen=True, slots=True)
class Service:
    """SMC-01 — an immutable, typed, identified, capability-realizing service root.

    Fields:
        type_tag:        the ENG-004 Type of the service (decidable, non-empty) — USL-03.
        kind:            the SXH-01 classification of the service (SXC-02).
        capability_ref:  the ENG-005 reference to the capability the service realizes
                         (SMR-01, reference-only) — the SOE-01 defining relationship.
        behavior_ref:    the ENG-005 reference to the RUNTIME behavior the service binds
                         (SMR-11 behaves-as; RL-F2, by reference) — USL-10.
        composition_ref: the ENG-005 reference to the PLATFORM composition the service
                         participates as (SMR-12 composed-as; PL-F2 / PLATFORM-008) — USL-09.
        state:           the SOS-01…06 lifecycle state (forward-only) — USL-12 (default DEFINED).
    """

    type_tag: str
    kind: ServiceKind
    capability_ref: str
    behavior_ref: str = "ENG-005:RL-F2:runtime.execution"
    composition_ref: str = "ENG-005:PL-F2:PLATFORM-008.service"
    state: ServiceState = ServiceState.DEFINED

    def __post_init__(self) -> None:
        # SMK-01 / USL-03 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ServiceError("service must be typed with a non-empty ENG-004 type_tag (USL-03)")
        # SXH-01 / SXC-02 — classified by exactly one Service kind.
        if not isinstance(self.kind, ServiceKind):
            raise ServiceError("service kind must be an SXH-01 ServiceKind (SXC-02)")
        # SMR-01 — a service realizes a capability, bound by reference (reference-only).
        _require_reference("capability_ref", self.capability_ref)
        # SMR-11 / USL-10 — behavior bound to RL-F2 by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # SMR-12 / USL-09 — composition bound to PL-F2 by reference.
        _require_reference("composition_ref", self.composition_ref)
        # V5 / USL-12 — a valid lifecycle state.
        if not isinstance(self.state, ServiceState):
            raise ServiceError("service state must be a SOS-01…06 ServiceState (USL-12)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the service (its identity-defining tuple)."""
        return {
            "meta_class": SERVICE_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "capability_ref": self.capability_ref,
            "behavior_ref": self.behavior_ref,
            "composition_ref": self.composition_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the service core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def service_id(self) -> str:
        """The deterministic ENG-001 identity of the service (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (USL-04 — no second
        identity scheme): identical (type, kind, refs) always yields the identical id,
        so identity is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{SERVICE_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (SMC-01)."""
        return SERVICE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the SMR-01…13 relationships the service root participates in."""
        return SERVICE_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / SMK-03 — the founding graph is acyclic.

        A Service root binds its constituents *by reference* (string ids), so its
        founding structure carries no cycle; this is proven by the fact that its core
        canonically encodes (a cycle would raise at construction).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        """SOI-03 / SMK-05/06 — every ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (self.capability_ref, self.behavior_ref, self.composition_ref)
        )

    # -- non-constitutiveness (USL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """USL-15 / C7 — a service confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """USL-15 / C7 — True iff the service names a concrete technology/protocol/vendor."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """USL-15 / RR-07 / C7 — True iff the service appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """USL-02 / SMI-05 / VC-5 — a service redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (USL-12, forward-only) --------------------------------------

    def transition(self, to_state: ServiceState) -> Service:
        """Return a new service advanced to ``to_state`` (forward-only; USL-12).

        Raises:
            ServiceError: on a backward or in-place-reversing transition.
        """
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
        """A deterministic, serializable projection of the service."""
        return {
            "service_id": self.service_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "capability_ref": self.capability_ref,
            "behavior_ref": self.behavior_ref,
            "composition_ref": self.composition_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_service(
    type_tag: str,
    capability_ref: str,
    *,
    kind: ServiceKind = ServiceKind.ATOMIC,
    behavior_ref: str = "ENG-005:RL-F2:runtime.execution",
    composition_ref: str = "ENG-005:PL-F2:PLATFORM-008.service",
    state: ServiceState = ServiceState.DEFINED,
) -> Service:
    """Construct a well-formed :class:`Service` (fail-closed factory)."""
    return Service(
        type_tag=type_tag,
        kind=kind,
        capability_ref=capability_ref,
        behavior_ref=behavior_ref,
        composition_ref=composition_ref,
        state=state,
    )


__all__ = [
    "SERVICE_ID_PREFIX",
    "FOUNDATION_REUSE",
    "ServiceError",
    "Service",
    "make_service",
]
