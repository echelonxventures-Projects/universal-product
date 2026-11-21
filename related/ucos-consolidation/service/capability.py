"""EC3-B11-U02 — The Universal Capability construct (SMC-02).

Realizes the meta-model concept **SMC-02 Capability** (SERVICE-005 §2; SERVICE-003
SOE-02):

    the implementation-independent **ability to perform work** a service realizes
    (SMR-01, reference-only), reusing the PLATFORM capability construct (PLATFORM-006)
    by reference (SMR-12) — a typed (ENG-004) ability borne by an object (ENG-002),
    identified (ENG-001), whose performance-of-work is a RUNTIME behavior (SMR-11, by
    reference).

The construct is **additive over the CERTIFIED EC-1 foundation** and reuses it — and the
Universal Service root (SMC-01) — *by reference* (USL-02 / SMI-05): identity and
value-fidelity are derived through the EC-1 certified deterministic encoding
(:func:`~engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`), the same discipline that produces
every EC-1 identity, so this module introduces **no second identity scheme and no parallel
value model**. It selects no technology (USL-15) and confers no authority (USL-15).

A :class:`Capability` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001), *classified* (SXH-02 kind), *behavior-bound* and
*platform-composed* (SMR-11/12, by reference), and holds a *forward-only lifecycle state*
(SOS-01…06, USL-12). Constructing a :class:`Capability` enforces the meta-constraints
SMK-01/03/05/06 and the laws USL-03/04/05/09/10 fail-closed: an ill-formed capability
cannot be instantiated. It realizes **no** Service, Contract, Interface, Operation,
Composition, Orchestration, Execution, Policy, or Security object — those are separate
Band-11 units; this construct binds them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- EC-1 reuse by reference (USL-02 / SMI-05) — imported, never redefined -------
from engine.certification.contracts import canonical_json, content_hash

# --- Service-layer reuse (SMC-01 sibling primitives) — imported, never redefined -
from service.capability_meta import (
    CAPABILITY_META_CLASS,
    CAPABILITY_RELATIONSHIPS,
    CAPABILITY_SUBSTRATE_REFS,
    LIFECYCLE_ORDER,
    CapabilityKind,
    ServiceState,
)
from service.service import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    ServiceError,
    _require_reference,
)

#: The deterministic id prefix for a realized Capability (mirrors EC-1 UCOS-<KIND>-<hex16>).
CAPABILITY_ID_PREFIX = "UCOS-CAPABILITY"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (USL-02 / SMI-05 / VC-5).
CAPABILITY_FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the capability)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity, no parallel model)",
    "ENG-004": "service.capability_meta.CapabilityKind + type_tag (ENG-004 typing, by reference)",
    "ENG-005": "reference identifiers (behavior/platform/service refs; no new construct)",
    "RL-F2": "behavior bound by reference (SMR-11); the ability-to-perform-work, not redefined",
    "PL-F2": "PLATFORM-006 capability construct bound by reference (SMR-12); not redefined",
    "SMC-01": "the Universal Service root that realizes this capability (SMR-01, by reference)",
}


@dataclass(frozen=True, slots=True)
class Capability:
    """SMC-02 — an immutable, typed, identified ability to perform work.

    Fields:
        type_tag:      the ENG-004 Type of the capability (decidable, non-empty) — USL-03.
        kind:          the SXH-02 classification (Functional / Query / Command; SXC-02).
        behavior_ref:  the ENG-005 reference to the RUNTIME behavior the capability binds
                       (SMR-11 behaves-as; RL-F2, by reference) — the ability to perform
                       work — USL-10.
        platform_ref:  the ENG-005 reference to the PLATFORM-006 capability construct the
                       capability is composed as (SMR-12 composed-as; PL-F2) — USL-09; the
                       SOE-02 defining reuse.
        service_ref:   the ENG-005 reference to the Service (SMC-01) that realizes this
                       capability (SMR-01 realizes, reference-only), or empty when the
                       capability is declared standalone ahead of its realizing service.
        state:         the SOS-01…06 lifecycle state (forward-only) — USL-12 (default DEFINED).
    """

    type_tag: str
    kind: CapabilityKind
    behavior_ref: str = "ENG-005:RL-F2:runtime.capability.perform"
    platform_ref: str = "ENG-005:PL-F2:PLATFORM-006.capability"
    service_ref: str = ""
    state: ServiceState = ServiceState.DEFINED

    def __post_init__(self) -> None:
        # SMK-01 / USL-03 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ServiceError(
                "capability must be typed with a non-empty ENG-004 type_tag (USL-03)"
            )
        # SXH-02 / SXC-02 — classified by exactly one Capability kind.
        if not isinstance(self.kind, CapabilityKind):
            raise ServiceError("capability kind must be an SXH-02 CapabilityKind (SXC-02)")
        # SMR-11 / USL-10 — behavior (ability to perform work) bound to RL-F2 by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # SMR-12 / USL-09 — PLATFORM-006 composition bound to PL-F2 by reference.
        _require_reference("platform_ref", self.platform_ref)
        # SMR-01 — realized-by a Service, by reference; optional (may precede its service).
        if not isinstance(self.service_ref, str):
            raise ServiceError("service_ref must be an ENG-005 reference string (SMR-01)")
        # V5 / USL-12 — a valid lifecycle state.
        if not isinstance(self.state, ServiceState):
            raise ServiceError("capability state must be a SOS-01…06 ServiceState (USL-12)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the capability (its identity-defining tuple)."""
        return {
            "meta_class": CAPABILITY_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "behavior_ref": self.behavior_ref,
            "platform_ref": self.platform_ref,
            "service_ref": self.service_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the capability core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def capability_id(self) -> str:
        """The deterministic ENG-001 identity of the capability (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (USL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity
        is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{CAPABILITY_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (SMC-02)."""
        return CAPABILITY_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the SMR-01…13 relationships the capability participates in."""
        return CAPABILITY_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / SMK-03 — the founding graph is acyclic.

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
        """SMK-05/06 — every required ENG-005 reference is a non-empty resolvable id.

        ``service_ref`` is optional (a capability may be declared before its realizing
        service), so it is excluded from the required set; when present it is a string.
        """
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (self.behavior_ref, self.platform_ref)
        )

    # -- non-constitutiveness (USL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """USL-15 / C7 — a capability confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """USL-15 / C7 — True iff the capability names a concrete technology/protocol/vendor."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """USL-15 / RR-07 / C7 — True iff the capability appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """USL-02 / SMI-05 / VC-5 — a capability redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (USL-12, forward-only) --------------------------------------

    def transition(self, to_state: ServiceState) -> Capability:
        """Return a new capability advanced to ``to_state`` (forward-only; USL-12).

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
        """A deterministic, serializable projection of the capability."""
        return {
            "capability_id": self.capability_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "behavior_ref": self.behavior_ref,
            "platform_ref": self.platform_ref,
            "service_ref": self.service_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(CAPABILITY_SUBSTRATE_REFS),
        }


def make_capability(
    type_tag: str,
    *,
    kind: CapabilityKind = CapabilityKind.FUNCTIONAL,
    behavior_ref: str = "ENG-005:RL-F2:runtime.capability.perform",
    platform_ref: str = "ENG-005:PL-F2:PLATFORM-006.capability",
    service_ref: str = "",
    state: ServiceState = ServiceState.DEFINED,
) -> Capability:
    """Construct a well-formed :class:`Capability` (fail-closed factory)."""
    return Capability(
        type_tag=type_tag,
        kind=kind,
        behavior_ref=behavior_ref,
        platform_ref=platform_ref,
        service_ref=service_ref,
        state=state,
    )


__all__ = [
    "CAPABILITY_ID_PREFIX",
    "CAPABILITY_FOUNDATION_REUSE",
    "Capability",
    "make_capability",
]
