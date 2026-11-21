"""EC3-B13-U03 — The Universal Infrastructure Network construct (NetworkResource).

Realizes the meta-model leaf concept **NetworkResource** (INFRASTRUCTURE-005 §2/§7;
INFRASTRUCTURE-008 §1):

    the implementation-independent abstraction of **connectivity between hosted
    constructs** — *the typed arrangement by which resources, nodes, clusters, and
    environments are reachable from one another* — a quantum of connectivity capacity that
    **declares a type (Connectivity Class, ENG-004), a quantified capacity (ENG-003), a
    locality (``locatedAt`` a Locality, by reference) and its connected endpoints** (a set
    of typed ENG-005 ``Connectivity Link`` reachability references — ICNW-01/02), typed
    (ENG-004), borne by an object (ENG-002), identified (ENG-001), and holding a
    forward-only lifecycle state (INFRASTRUCTURE-003 §3).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
FROZEN/CERTIFIED lower layers, and the CERTIFIED Band-13 EC3-B13-U01
:class:`~infrastructure.capability.InfrastructureCapability` primitives) and reuses them
*by reference* (UIL-02): identity and value-fidelity are derived through the EC-1
certified deterministic encoding (:func:`~engine.certification.contracts.canonical_json`
/ :func:`~engine.certification.contracts.content_hash`) — the same discipline that
produces every EC-1 identity — so this module introduces **no second identity scheme and
no parallel value model**. The shared infrastructure-layer primitives
(:class:`~infrastructure.capability.InfrastructureError`, the reference helper, and the
technology/secret markers) are **imported from the first Band-13 unit and never
redefined** (UIL-02). It selects no transport/protocol/mesh/vendor (UIL-12 / UIL-15 /
ICNW-05) and confers no authority (UIL-15).

A :class:`NetworkResource` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001), *capacity-and-locality-declaring* (WF-5 / UIL-08 /
ICNW-02 — the governing Resource rule), *endpoint-declaring* (≥1 ``ConnectivityLink``;
ICNW-02), *boundary-honoring* (every cross-boundary link declares a typed
``IsolationBoundary`` reference — ICNW-03 / UIL-07, the distinguishing Network law),
*connectivity-by-reference* (typed ENG-005 references, no new connection construct —
ICNW-01 / UIL-09), *unbounded-by-declaration* (ICNW-04 / UIL-13), and holds a
*forward-only lifecycle state* (INFRASTRUCTURE-003 §3). Constructing a
:class:`NetworkResource` enforces the well-formedness rules WF-1/2/3/5/11/12 and the laws
UIL-03/04/05/07/08/09/12/13/15 fail-closed: an ill-formed network resource cannot be
instantiated. It realizes **no** Node/Cluster/Environment/IsolationBoundary/Topology
object — those are separate Band-13 units; this construct binds them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

# --- EC-1 reuse by reference (UIL-02) — imported, never redefined ----------------
from engine.certification.contracts import canonical_json, content_hash

# --- Band-13 shared primitives reused by reference (UIL-02) — established by U01 --
from infrastructure.capability import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    InfrastructureError,
    _require_reference,
)
from infrastructure.network_meta import (
    INFRASTRUCTURE_META_CLASS,
    LIFECYCLE_ORDER,
    NETWORK_RELATIONSHIPS,
    SUBSTRATE_REFS,
    InfrastructureState,
)

#: The deterministic id prefix for a realized Network Resource
#: (mirrors EC-1 UCOS-<KIND>-<hex16>).
INFRA_NETWORK_ID_PREFIX = "UCOS-INFRA-NETWORK"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UIL-02 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the network resource)",
    "ENG-003": "engine.certification.contracts.canonical_json (capacity + value fidelity)",
    "ENG-004": "infrastructure.network type_tag Connectivity Class (typing)",
    "ENG-005": "reference identifiers (connectivity links / locatedAt / boundary refs; "
    "no new connection construct)",
}


@dataclass(frozen=True, slots=True)
class NetworkCapacity:
    """A declared, quantified amount of connectivity capacity (ENG-003).

    The INFRASTRUCTURE-008-analog of "Compute Capacity" — a technology-neutral, quantified
    value with **no artificial ceiling** (ICNW-04 / UIL-13). ``amount`` is a non-negative
    integer quantity in the (abstract) ``unit``; no upper bound is imposed, so scaling is
    architecturally unbounded (limited only by physical reality).

    Fields:
        amount: the non-negative quantity of connectivity capacity (ENG-003).
        unit:   the technology-neutral capacity unit (e.g. ``"connectivity-unit"``) — names
                no bandwidth product, transport, or vendor (UIL-12 / UIL-15).
    """

    amount: int
    unit: str = "connectivity-unit"

    def __post_init__(self) -> None:
        # ENG-003 / ICNW-02 — a decidable, non-negative quantity (``bool`` is not a quantity).
        if isinstance(self.amount, bool) or not isinstance(self.amount, int) or self.amount < 0:
            raise InfrastructureError(
                "network capacity amount must be a non-negative integer quantity (ENG-003)"
            )
        # ICNW-05 / UIL-15 — a non-empty, technology-neutral unit.
        if not isinstance(self.unit, str) or not self.unit.strip():
            raise InfrastructureError(
                "network capacity unit must be a non-empty technology-neutral ENG-003 unit"
            )

    def canonical(self) -> dict[str, Any]:
        """The canonical, hashable projection of the capacity (ENG-003 value)."""
        return {"amount": self.amount, "unit": self.unit}

    def is_unbounded(self) -> bool:
        """ICNW-04 / UIL-13 — the capacity imposes no artificial ceiling (unbounded)."""
        return True


@dataclass(frozen=True, slots=True)
class ConnectivityLink:
    """A typed reachability reference between two hosted constructs (INFRASTRUCTURE-008 §2).

    The Connectivity Link is *the* Network construct: **connectivity is a typed ENG-005
    reference; no new connection construct is introduced and no protocol/transport is
    selected** (ICNW-01 / UIL-09). It connects two hosted constructs by reference
    (``source_ref`` → ``target_ref``), is classified by an abstract, technology-neutral
    Connectivity Class (ENG-004), and — when it crosses an isolation boundary — declares
    that boundary by a typed ENG-005 reference (ICNW-03 / UIL-07). A link founds nothing
    (it is a peer reachability reference, not a ``contains``/``dependsOn`` founding edge),
    so a link never introduces a founding cycle.

    Fields:
        source_ref:         ENG-005 reference to the source hosted construct.
        target_ref:         ENG-005 reference to the target hosted construct.
        connectivity_class: the ENG-004 abstract, technology-neutral category of connectivity.
        cross_boundary:     True iff the link crosses an isolation boundary (ICNW-03).
        boundary_ref:       ENG-005 reference to the IsolationBoundary the link crosses;
                            mandatory (declared and typed) iff ``cross_boundary`` is True.
    """

    source_ref: str
    target_ref: str
    connectivity_class: str = "reachability"
    cross_boundary: bool = False
    boundary_ref: str = ""

    def __post_init__(self) -> None:
        # ICNW-01 / UIL-09 — connectivity is a typed ENG-005 reference between two endpoints.
        _require_reference("source_ref", self.source_ref)
        _require_reference("target_ref", self.target_ref)
        # ICNW-01 / UIL-03 — classified by a non-empty, abstract Connectivity Class (ENG-004).
        if not isinstance(self.connectivity_class, str) or not self.connectivity_class.strip():
            raise InfrastructureError(
                "connectivity link must declare a non-empty ENG-004 Connectivity Class (ICNW-01)"
            )
        if not isinstance(self.cross_boundary, bool):
            raise InfrastructureError("cross_boundary must be a boolean (ICNW-03)")
        # ICNW-03 / UIL-07 — a cross-boundary link declares its boundary by a typed reference.
        if self.cross_boundary:
            _require_reference("boundary_ref", self.boundary_ref)
        elif self.boundary_ref and not (
            isinstance(self.boundary_ref, str) and self.boundary_ref.strip()
        ):
            raise InfrastructureError("boundary_ref, when present, must be an ENG-005 reference")

    def canonical(self) -> dict[str, Any]:
        """The canonical, hashable projection of the link (ENG-005 reference tuple)."""
        return {
            "source_ref": self.source_ref,
            "target_ref": self.target_ref,
            "connectivity_class": self.connectivity_class,
            "cross_boundary": self.cross_boundary,
            "boundary_ref": self.boundary_ref,
        }

    def endpoints_resolve(self) -> bool:
        """WF-2 / ICNW-01 — both endpoint references are non-empty resolvable ids."""
        return bool(self.source_ref.strip()) and bool(self.target_ref.strip())

    def honors_boundary(self) -> bool:
        """ICNW-03 / UIL-07 — a cross-boundary link declares a typed boundary reference."""
        return (not self.cross_boundary) or bool(self.boundary_ref.strip())


@dataclass(frozen=True, slots=True)
class NetworkResource:
    """NetworkResource — an immutable, typed, identified quantum of connectivity capacity.

    Fields:
        type_tag:      the ENG-004 Type (Connectivity Class) of the resource (decidable,
                       non-empty) — UIL-03 / INFRASTRUCTURE-008 §2.
        capacity:      the declared, quantified ENG-003 connectivity capacity
                       (WF-5 / ICNW-02) — unbounded (ICNW-04 / UIL-13).
        locality_ref:  the ENG-005 ``locatedAt`` reference to the Locality the resource is
                       located at (WF-5 / ICNW-02; multiplicity 1, total) — reference-only.
        links:         the connected endpoints — a non-empty tuple of typed
                       :class:`ConnectivityLink` reachability references (ICNW-01/02); the
                       Resource's ``hosts`` edges, realized by reference, non-mutating.
        state:         the forward-only lifecycle (provisioningState; INFRASTRUCTURE-003
                       §3; default DEFINED).
    """

    type_tag: str
    capacity: NetworkCapacity
    locality_ref: str
    links: tuple[ConnectivityLink, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        # UIL-03 / INFRASTRUCTURE-008 §2 — typed by a non-empty ENG-004 Connectivity Class.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise InfrastructureError(
                "network resource must be typed with a non-empty ENG-004 type (UIL-03)"
            )
        # WF-5 / ICNW-02 — declares a quantified ENG-003 capacity.
        if not isinstance(self.capacity, NetworkCapacity):
            raise InfrastructureError(
                "network resource must declare a NetworkCapacity (WF-5 / ICNW-02)"
            )
        # WF-5 / ICNW-02 — declares a locality by ENG-005 ``locatedAt`` reference (total).
        _require_reference("locality_ref", self.locality_ref)
        # ICNW-02 — declares its connected endpoints: at least one typed connectivity link.
        if not isinstance(self.links, tuple) or not self.links:
            raise InfrastructureError(
                "network resource must declare its connected endpoints "
                "(≥1 ConnectivityLink; ICNW-02)"
            )
        for link in self.links:
            if not isinstance(link, ConnectivityLink):
                raise InfrastructureError(
                    "every connected endpoint must be a ConnectivityLink (ICNW-01)"
                )
        # WF-1 / INFRASTRUCTURE-003 §3 — a valid forward-only lifecycle state.
        if not isinstance(self.state, InfrastructureState):
            raise InfrastructureError(
                "network resource state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the resource (its identity-defining tuple)."""
        return {
            "meta_class": INFRASTRUCTURE_META_CLASS,
            "type_tag": self.type_tag,
            "capacity": self.capacity.canonical(),
            "locality_ref": self.locality_ref,
            "links": [link.canonical() for link in self.links],
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the resource core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def resource_id(self) -> str:
        """The deterministic ENG-001 identity of the resource (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UIL-04 — no second identity
        scheme): identical (type, capacity, locality, links) always yields the identical
        id, so identity is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{INFRA_NETWORK_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (INFRASTRUCTURE-005) -------------------------

    @property
    def meta_class(self) -> str:
        """WF-1 — the single leaf meta-class this construct instantiates."""
        return INFRASTRUCTURE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """The admitted meta-relationships the resource participates in (hosts, locatedAt)."""
        return NETWORK_RELATIONSHIPS

    def declares_mandatory_attributes(self) -> bool:
        """WF-1 / WF-5 — the resource declares its mandatory meta-attributes.

        A Resource's mandatory set (INFRASTRUCTURE-005 §3) is id/type/value/**capacity**/
        **locality**/**hosts**/provisioningState — all present and non-empty; for a Network
        Resource the ``hosts`` edges are its connected endpoints (≥1 connectivity link).
        """
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.resource_id)
            and self.declares_capacity_and_locality()
            and self.declares_connected_endpoints()
        )

    def declares_capacity_and_locality(self) -> bool:
        """WF-5 / UIL-08 / ICNW-02 — the resource declares capacity and locality.

        THE governing Resource rule: a NetworkResource must declare both a quantified
        capacity (ENG-003) and a locality (``locatedAt`` reference).
        """
        return (
            isinstance(self.capacity, NetworkCapacity)
            and self.capacity.amount >= 0
            and bool(self.capacity.unit.strip())
            and bool(self.locality_ref.strip())
        )

    def declares_connected_endpoints(self) -> bool:
        """ICNW-02 / WF-2 — the resource declares ≥1 connectivity link with resolving endpoints.

        The Network-specific governing obligation: a network resource declares its
        connected endpoints as typed ENG-005 reachability references (ICNW-01/02).
        """
        return bool(self.links) and all(link.endpoints_resolve() for link in self.links)

    def honors_isolation_boundaries(self) -> bool:
        """ICNW-03 / UIL-07 — connectivity honors isolation boundaries.

        THE distinguishing Network law (materially exercised): every cross-boundary link
        declares its isolation boundary by a typed ENG-005 reference; a link that crosses a
        boundary without declaring it is ill-formed (rejected at construction).
        """
        return all(link.honors_boundary() for link in self.links)

    def connectivity_by_reference(self) -> bool:
        """ICNW-01 / WF-2 / UIL-09 — connectivity is a typed ENG-005 reference, no new construct.

        Every connectivity link holds only ENG-005 reference strings (endpoints + optional
        boundary) and a typed Connectivity Class; it introduces no new connection construct
        and holds/mutates no hosted construct.
        """
        return all(
            link.endpoints_resolve() and bool(link.connectivity_class.strip())
            for link in self.links
        )

    def is_resource(self) -> bool:
        """WF-5 — a network resource **is** a Resource (declares capacity/locality)."""
        return True

    def is_evaluative_facet(self) -> bool:
        """WF-10 N/A — a resource is not an EvaluativeFacet (nonEnforcing does not apply)."""
        return False

    def is_founding_acyclic(self) -> bool:
        """WF-3 / UIL-09 — the founding graph is acyclic.

        A resource binds its constituents *by reference* (string ids), and connectivity
        links are peer (non-founding) reachability references, so its founding structure
        carries no cycle; this is proven by the fact that its core canonically encodes (a
        cycle would raise at construction).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        """WF-2 — every required ENG-005 reference is a non-empty resolvable id."""
        return bool(self.locality_ref.strip()) and all(
            link.endpoints_resolve() and link.honors_boundary() for link in self.links
        )

    def declares_no_artificial_ceiling(self) -> bool:
        """ICNW-04 / UIL-13 — the declared capacity imposes no artificial ceiling."""
        return isinstance(self.capacity, NetworkCapacity) and self.capacity.is_unbounded()

    # -- non-constitutiveness (UIL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """UIL-15 / C7 — a resource confers no authority (structurally has none)."""
        return False

    def enacts_enforcement(self) -> bool:
        """UIL-14 / WF-10 — a resource enacts no enforcement (it declares connectivity only)."""
        return False

    def selects_technology(self) -> bool:
        """UIL-12 / UIL-15 / ICNW-05 / C7 — True iff the resource names a transport/technology."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UIL-15 / RR-07 / C7 — True iff the resource appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UIL-02 / VC-5 — a resource redefines no frozen primitive (reuse-only)."""
        return False

    def projects_completion(self) -> bool:
        """WF-12 — a resource projects no architecture-existence-as-completion claim."""
        return False

    def is_new_primitive(self) -> bool:
        """WF-11 / UIL-01 — a resource is no new primitive/authority/registry/lifecycle."""
        return False

    # -- lifecycle (forward-only) ----------------------------------------------

    def transition(self, to_state: InfrastructureState) -> NetworkResource:
        """Return a new resource advanced to ``to_state`` (forward-only).

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
        """A deterministic, serializable projection of the resource."""
        return {
            "resource_id": self.resource_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "capacity": self.capacity.canonical(),
            "locality_ref": self.locality_ref,
            "links": [link.canonical() for link in self.links],
            "value_digest": self.value_digest,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_connectivity_link(
    source_ref: str,
    target_ref: str,
    *,
    connectivity_class: str = "reachability",
    cross_boundary: bool = False,
    boundary_ref: str = "",
) -> ConnectivityLink:
    """Construct a well-formed :class:`ConnectivityLink` (fail-closed factory)."""
    return ConnectivityLink(
        source_ref=source_ref,
        target_ref=target_ref,
        connectivity_class=connectivity_class,
        cross_boundary=cross_boundary,
        boundary_ref=boundary_ref,
    )


def make_network_resource(
    type_tag: str,
    locality_ref: str,
    *,
    links: tuple[ConnectivityLink, ...] | None = None,
    source_ref: str = "ENG-005:INFRASTRUCTURE-007:compute.endpoint.a",
    target_ref: str = "ENG-005:INFRASTRUCTURE-007:compute.endpoint.b",
    connectivity_class: str = "reachability",
    capacity: NetworkCapacity | None = None,
    amount: int = 1,
    unit: str = "connectivity-unit",
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> NetworkResource:
    """Construct a well-formed :class:`NetworkResource` (fail-closed factory).

    ``links`` may be supplied directly, or a single default reachability link is built
    from ``source_ref`` + ``target_ref`` + ``connectivity_class``. ``capacity`` may be
    supplied directly, or built from ``amount`` + ``unit``.
    """
    declared_links = (
        links
        if links is not None
        else (
            make_connectivity_link(
                source_ref, target_ref, connectivity_class=connectivity_class
            ),
        )
    )
    declared_capacity = (
        capacity if capacity is not None else NetworkCapacity(amount=amount, unit=unit)
    )
    return NetworkResource(
        type_tag=type_tag,
        capacity=declared_capacity,
        locality_ref=locality_ref,
        links=declared_links,
        state=state,
    )


__all__ = [
    "INFRA_NETWORK_ID_PREFIX",
    "FOUNDATION_REUSE",
    "NetworkCapacity",
    "ConnectivityLink",
    "NetworkResource",
    "make_connectivity_link",
    "make_network_resource",
]
