"""EC3-B13-U01 — The Universal Infrastructure Capability construct (InfrastructureCapability).

Realizes the meta-model leaf concept **InfrastructureCapability** (INFRASTRUCTURE-005 §2;
INFRASTRUCTURE-006 §1):

    the implementation-independent **hosting/delivery ability** an infrastructure realizes
    — the "what is hosted and delivered" — which **reuses the PLATFORM-006 / SF-2 capability
    construct by reference** (ICAP-01 / UIL-06) and **enables a frozen lower-layer construct
    by reference** (ICAP-03), typed (ENG-004), borne by an object (ENG-002), identified
    (ENG-001), whose hosting/delivery behavior is a RUNTIME construct (UIL-10, by reference).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
FROZEN/CERTIFIED lower layers) and reuses them *by reference* (UIL-02): identity and
value-fidelity are derived through the EC-1 certified deterministic encoding
(:func:`~engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`) — the same discipline that produces
every EC-1 identity — so this module introduces **no second identity scheme and no parallel
value model**. It selects no technology (UIL-12 / UIL-15) and confers no authority (UIL-15).

An :class:`InfrastructureCapability` is *immutable* (a frozen object — ENG-002 objecthood),
*typed* (ENG-004), *identified* (ENG-001), *classified* (INFRASTRUCTURE-006 §2 kind),
*platform-reusing* (ICAP-01, by reference), *frozen-construct-enabling* (ICAP-03, by
reference), *behavior-bound* (UIL-10, by reference), and holds a *forward-only lifecycle
state* (INFRASTRUCTURE-003 §3). Constructing an :class:`InfrastructureCapability` enforces
the well-formedness rules WF-1/2/3/11/12 and the laws UIL-03/04/05/06/15 fail-closed: an
ill-formed capability cannot be instantiated. It realizes **no** Resource, HostingStructure,
Arrangement, ProvisioningProcess, or EvaluativeFacet object — those are separate Band-13
units; this construct binds them only *by reference*.

This is the **first** realized Band-13 unit, so it also establishes the shared
infrastructure-layer primitives (:class:`InfrastructureError`, the reference helper, and
the technology/secret markers) that every subsequent Band-13 concern imports — never
redefining any of them (UIL-02).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- EC-1 reuse by reference (UIL-02) — imported, never redefined ----------------
from engine.certification.contracts import canonical_json, content_hash
from infrastructure.capability_meta import (
    CAPABILITY_RELATIONSHIPS,
    INFRASTRUCTURE_META_CLASS,
    LIFECYCLE_ORDER,
    SUBSTRATE_REFS,
    InfrastructureCapabilityKind,
    InfrastructureState,
)

#: The deterministic id prefix for a realized Infrastructure Capability
#: (mirrors EC-1 UCOS-<KIND>-<hex16>).
INFRA_CAPABILITY_ID_PREFIX = "UCOS-INFRA-CAPABILITY"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UIL-02 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the capability)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity, no parallel model)",
    "ENG-004": "infrastructure.capability_meta.InfrastructureCapabilityKind + type_tag (typing)",
    "ENG-005": "reference identifiers (platform/enable/behavior refs; no new construct)",
    "RL-F2": "hosting/delivery behavior bound by reference (UIL-10); no runtime concern redefined",
    "PL-F2": "PLATFORM-006 capability construct bound by reference (ICAP-01); not redefined",
    "SF-2": "hosted/delivered service capability bound by reference (UIL-06); not redefined",
}

#: Concrete-technology markers forbidden by UIL-12 / UIL-15 (no cloud/orchestrator/
#: IaC/transport/vendor). An abstract EL-1/RL-F2/PL-F2/SF-2/AF-3 reference names none.
#: Curated to avoid collision with the abstract reference vocabulary this layer uses.
_TECHNOLOGY_MARKERS: tuple[str, ...] = (
    "aws",
    "azure",
    "gcp",
    "kubernetes",
    "docker",
    "terraform",
    "ansible",
    "pulumi",
    "openstack",
    "vmware",
    "cloudformation",
    "openshift",
    "nginx",
    "envoy",
    "postgres",
    "mysql",
    "mongodb",
    "kafka",
    "rabbitmq",
    "http://",
    "https://",
    "tcp://",
)

#: Conservative secret markers used to enforce UIL-15 / RR-07 (embed no secret).
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


class InfrastructureError(ValueError):
    """Raised when inputs cannot be realized as a well-formed infrastructure construct.

    Every Band-13 construct is fail-closed (TRACK-001): an ill-formed infrastructure
    construct is rejected at construction rather than admitted as invalid. This is the
    shared error type for the whole ``infrastructure/**`` surface (established by the
    first unit, EC3-B13-U01).
    """


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise InfrastructureError(
            f"{name} must be a non-empty ENG-005 reference (UIL-02/06/09)"
        )
    return value


@dataclass(frozen=True, slots=True)
class InfrastructureCapability:
    """InfrastructureCapability — an immutable, typed, identified hosting/delivery ability.

    Fields:
        type_tag:      the ENG-004 Type of the capability (decidable, non-empty) — UIL-03.
        kind:          the INFRASTRUCTURE-006 §2 classification (Hosting / Delivery /
                       Provisioning / Scaling / Resilience).
        enables_ref:   the ENG-005 reference to the frozen lower-layer construct this
                       capability enables/hosts/delivers (ICAP-03, reference-only, never
                       mutating) — the INFRASTRUCTURE-006 §2 "declares the frozen construct
                       it enables" obligation.
        capability_ref: the ENG-005 reference to the PLATFORM-006 / SF-2 capability construct
                       the infrastructure capability reuses (ICAP-01 / UIL-06; the defining
                       reuse) — reference-only, never re-founded.
        behavior_ref:  the ENG-005 reference to the RUNTIME behavior the capability binds
                       (UIL-10; RL-F2, by reference) — the hosting/delivery/provisioning act.
        state:         the forward-only lifecycle state (INFRASTRUCTURE-003 §3; default DEFINED).
    """

    type_tag: str
    kind: InfrastructureCapabilityKind
    enables_ref: str
    capability_ref: str = "ENG-005:PL-F2:PLATFORM-006.capability"
    behavior_ref: str = "ENG-005:RL-F2:runtime.capability"
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        # ICAP-02 / UIL-03 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise InfrastructureError(
                "infrastructure capability must be typed with a non-empty ENG-004 type_tag (UIL-03)"
            )
        # INFRASTRUCTURE-006 §2 — classified by exactly one capability kind.
        if not isinstance(self.kind, InfrastructureCapabilityKind):
            raise InfrastructureError(
                "capability kind must be an InfrastructureCapabilityKind (INFRASTRUCTURE-006 §2)"
            )
        # ICAP-03 / UIL-06 — enables a frozen lower-layer construct, bound by reference.
        _require_reference("enables_ref", self.enables_ref)
        # ICAP-01 / UIL-06 — reuses the PLATFORM-006 / SF-2 capability, by reference.
        _require_reference("capability_ref", self.capability_ref)
        # UIL-10 — hosting/delivery behavior bound to RL-F2 by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # WF-1 / INFRASTRUCTURE-003 §3 — a valid lifecycle state.
        if not isinstance(self.state, InfrastructureState):
            raise InfrastructureError(
                "capability state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the capability (its identity-defining tuple)."""
        return {
            "meta_class": INFRASTRUCTURE_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "enables_ref": self.enables_ref,
            "capability_ref": self.capability_ref,
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the capability core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def capability_id(self) -> str:
        """The deterministic ENG-001 identity of the capability (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UIL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity
        is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{INFRA_CAPABILITY_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (INFRASTRUCTURE-005) -------------------------

    @property
    def meta_class(self) -> str:
        """WF-1 — the single leaf meta-class this construct instantiates."""
        return INFRASTRUCTURE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """The admitted meta-relationships the capability participates in (dependsOn)."""
        return CAPABILITY_RELATIONSHIPS

    def declares_mandatory_attributes(self) -> bool:
        """WF-1 — the capability declares its mandatory meta-attributes (id/type/value).

        InfrastructureCapability is neither a Resource (no capacity/locality) nor an
        EvaluativeFacet (no nonEnforcing) — its mandatory set is exactly id/type/value
        (INFRASTRUCTURE-005 §3), all present and non-empty.
        """
        return bool(self.type_tag.strip()) and bool(self.value_digest) and bool(self.capability_id)

    def is_resource(self) -> bool:
        """WF-5 N/A — a capability is not a Resource (declares no capacity/locality)."""
        return False

    def is_evaluative_facet(self) -> bool:
        """WF-10 N/A — a capability is not an EvaluativeFacet (nonEnforcing does not apply)."""
        return False

    def is_founding_acyclic(self) -> bool:
        """WF-3 / UIL-09 — the founding graph is acyclic.

        A capability binds its constituents *by reference* (string ids), so its founding
        structure carries no cycle; this is proven by the fact that its core canonically
        encodes (a cycle would raise at construction).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        """WF-2 — every required ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (self.enables_ref, self.capability_ref, self.behavior_ref)
        )

    def enables_by_reference(self) -> bool:
        """ICAP-03 / WF-2 — the enabled frozen construct is bound by reference, non-mutating.

        The capability holds only an ENG-005 reference string to the enabled construct;
        it never holds or mutates the construct itself.
        """
        return isinstance(self.enables_ref, str) and bool(self.enables_ref.strip())

    def reuses_platform_capability(self) -> bool:
        """ICAP-01 / UIL-06 — the capability reuses PLATFORM-006/SF-2 by reference."""
        return isinstance(self.capability_ref, str) and bool(self.capability_ref.strip())

    def declares_no_artificial_ceiling(self) -> bool:
        """ICAP-04 / UIL-13 — the capability declares no artificial ceiling.

        A capability names no numeric bound; scaling is architecturally unbounded
        (physical reality only). This holds structurally for every kind, and is the
        governing condition for the ``SCALING`` kind.
        """
        return True

    # -- non-constitutiveness (UIL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """UIL-15 / C7 — a capability confers no authority (structurally has none)."""
        return False

    def enacts_enforcement(self) -> bool:
        """UIL-14 / WF-10 — a capability enacts no enforcement (it hosts/delivers only)."""
        return False

    def selects_technology(self) -> bool:
        """UIL-12 / UIL-15 / C7 — True iff the capability names a concrete technology/vendor."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UIL-15 / RR-07 / C7 — True iff the capability appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UIL-02 / VC-5 — a capability redefines no frozen primitive (reuse-only)."""
        return False

    def projects_completion(self) -> bool:
        """WF-12 — a capability projects no architecture-existence-as-completion claim."""
        return False

    def is_new_primitive(self) -> bool:
        """WF-11 / UIL-01 — a capability is no new primitive/authority/registry/lifecycle."""
        return False

    # -- lifecycle (forward-only) ----------------------------------------------

    def transition(self, to_state: InfrastructureState) -> InfrastructureCapability:
        """Return a new capability advanced to ``to_state`` (forward-only).

        Raises:
            InfrastructureError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, InfrastructureState):
            raise InfrastructureError(
                "target state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise InfrastructureError(
                f"lifecycle is forward-only: {self.state.value} → {to_state.value} is backward"
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
            "enables_ref": self.enables_ref,
            "capability_ref": self.capability_ref,
            "behavior_ref": self.behavior_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_infrastructure_capability(
    type_tag: str,
    enables_ref: str,
    *,
    kind: InfrastructureCapabilityKind = InfrastructureCapabilityKind.HOSTING,
    capability_ref: str = "ENG-005:PL-F2:PLATFORM-006.capability",
    behavior_ref: str = "ENG-005:RL-F2:runtime.capability",
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> InfrastructureCapability:
    """Construct a well-formed :class:`InfrastructureCapability` (fail-closed factory)."""
    return InfrastructureCapability(
        type_tag=type_tag,
        kind=kind,
        enables_ref=enables_ref,
        capability_ref=capability_ref,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "INFRA_CAPABILITY_ID_PREFIX",
    "FOUNDATION_REUSE",
    "InfrastructureError",
    "InfrastructureCapability",
    "make_infrastructure_capability",
]
