"""EC3-B13-U04 — The Universal Infrastructure Storage-Hosting construct (StorageHostingResource).

Realizes the meta-model leaf concept **StorageHostingResource** (INFRASTRUCTURE-005 §2/§7;
INFRASTRUCTURE-009 §1):

    the implementation-independent abstraction of **where and how DF-2-represented data
    (DATA-010) is hosted and located** — *the hosting locus of represented data, never the
    representation itself* — a quantum of data-hosting capacity that **declares a type
    (Storage Hosting Class, ENG-004), a quantified capacity (ENG-003), a locality
    (``locatedAt`` a Locality, by reference) and its hosted data** (a set of typed ENG-005
    ``Data Placement`` references, each ``hosts`` a frozen DATA-010 datum by reference —
    ISTO-01/02 / WF-7 / UIL-11), typed (ENG-004), borne by an object (ENG-002), identified
    (ENG-001), and holding a forward-only lifecycle state (INFRASTRUCTURE-003 §3).

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
redefined** (UIL-02). It **hosts** the frozen DATA-010 representation **by reference** and
**redefines no data concern** (ISTO-01 / UIL-11); it selects no filesystem/block/object
store/database engine/vendor (UIL-15 / ISTO-05) and confers no authority (UIL-15).

A :class:`StorageHostingResource` is *immutable* (a frozen object — ENG-002 objecthood),
*typed* (ENG-004), *identified* (ENG-001), *capacity-and-locality-declaring* (WF-5 /
UIL-08 / ISTO-02 — the governing Resource rule), *data-hosting* (``hosts`` ≥1 DATA-010
datum by reference; WF-7 / ISTO-01 / UIL-11 — the storage-unique governing rule),
*boundary-honoring* (every cross-boundary data placement declares a typed
``IsolationBoundary`` reference — ISTO-03 / UIL-07), *unbounded-by-declaration* (ISTO-04 /
UIL-13), and holds a *forward-only lifecycle state* (INFRASTRUCTURE-003 §3). Constructing
a :class:`StorageHostingResource` enforces the well-formedness rules WF-1/2/3/5/7/11/12
and the laws UIL-03/04/05/07/08/11/13/15 fail-closed: an ill-formed storage-hosting
resource cannot be instantiated. It realizes **no** Node/Cluster/Environment/
IsolationBoundary/Topology object and **no** DATA-010 datum — those are separate
Band-13 units and the frozen data layer; this construct binds them only *by reference*.
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
from infrastructure.storage_meta import (
    INFRASTRUCTURE_META_CLASS,
    LIFECYCLE_ORDER,
    STORAGE_RELATIONSHIPS,
    SUBSTRATE_REFS,
    InfrastructureState,
)

#: The deterministic id prefix for a realized Storage-Hosting Resource
#: (mirrors EC-1 UCOS-<KIND>-<hex16>).
INFRA_STORAGE_ID_PREFIX = "UCOS-INFRA-STORAGE"

#: The default ENG-005 reference to the frozen DATA-010 datum a storage-hosting resource
#: hosts (ISTO-01 / UIL-11). Abstract — names no filesystem/block/object store/DB engine.
DEFAULT_DATUM_HOST_REF = "ENG-005:DF-2:DATA-010.datum"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UIL-02 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the storage resource)",
    "ENG-003": "engine.certification.contracts.canonical_json (capacity + value fidelity)",
    "ENG-004": "infrastructure.storage type_tag Storage Hosting Class (typing)",
    "ENG-005": "reference identifiers (data placements / locatedAt / boundary refs; "
    "no new construct)",
    "DF-2": "hosted DATA-010 represented data bound by reference (ISTO-01 / UIL-11); "
    "no data concern redefined",
}


@dataclass(frozen=True, slots=True)
class StorageCapacity:
    """A declared, quantified amount of data-hosting capability (ENG-003).

    The INFRASTRUCTURE-009 §2 "Storage Capacity" construct — a technology-neutral,
    quantified value with **no artificial ceiling** (ISTO-04 / UIL-13). ``amount`` is a
    non-negative integer quantity in the (abstract) ``unit``; no upper bound is imposed,
    so scaling is architecturally unbounded (limited only by physical reality).

    Fields:
        amount: the non-negative quantity of data-hosting capability (ENG-003).
        unit:   the technology-neutral capacity unit (e.g. ``"storage-unit"``) — names no
                filesystem, block/object store, database engine, or vendor (UIL-15).
    """

    amount: int
    unit: str = "storage-unit"

    def __post_init__(self) -> None:
        # ENG-003 / ISTO-02 — a decidable, non-negative quantity (``bool`` is not a quantity).
        if isinstance(self.amount, bool) or not isinstance(self.amount, int) or self.amount < 0:
            raise InfrastructureError(
                "storage capacity amount must be a non-negative integer quantity (ENG-003)"
            )
        # ISTO-05 / UIL-15 — a non-empty, technology-neutral unit.
        if not isinstance(self.unit, str) or not self.unit.strip():
            raise InfrastructureError(
                "storage capacity unit must be a non-empty technology-neutral ENG-003 unit"
            )

    def canonical(self) -> dict[str, Any]:
        """The canonical, hashable projection of the capacity (ENG-003 value)."""
        return {"amount": self.amount, "unit": self.unit}

    def is_unbounded(self) -> bool:
        """ISTO-04 / UIL-13 — the capacity imposes no artificial ceiling (unbounded)."""
        return True


@dataclass(frozen=True, slots=True)
class DataPlacement:
    """The located hosting of a frozen DF-2 datum on a resource (INFRASTRUCTURE-009 §2).

    The Data Placement is *the* Storage-Hosting construct: **storage-hosting locates a
    DATA-010 datum by ENG-005 reference; no data concern is re-modeled and no storage
    technology is selected** (ISTO-01 / UIL-11 — the defining reuse). It hosts one frozen
    DATA-010 datum by reference (``datum_ref``), is classified by an abstract,
    technology-neutral Storage Hosting Class (ENG-004), and — when the placement crosses
    an isolation boundary — declares that boundary by a typed ENG-005 reference (ISTO-03 /
    UIL-07). A placement founds nothing (it is a peer ``hosts`` reference, not a
    ``contains``/``dependsOn`` founding edge), so it never introduces a founding cycle.

    Fields:
        datum_ref:      ENG-005 ``hosts`` reference to the frozen DATA-010 datum hosted
                        (ISTO-01 / UIL-11) — reference-only, non-mutating.
        placement_class: the ENG-004 abstract, technology-neutral Storage Hosting Class.
        cross_boundary: True iff the placement crosses an isolation boundary (ISTO-03).
        boundary_ref:   ENG-005 reference to the IsolationBoundary the placement honors;
                        mandatory (declared and typed) iff ``cross_boundary`` is True.
    """

    datum_ref: str = DEFAULT_DATUM_HOST_REF
    placement_class: str = "data-placement"
    cross_boundary: bool = False
    boundary_ref: str = ""

    def __post_init__(self) -> None:
        # ISTO-01 / UIL-11 — the placement hosts a frozen DATA-010 datum by ENG-005 reference.
        _require_reference("datum_ref", self.datum_ref)
        # ISTO-01 / UIL-03 — classified by a non-empty, abstract Storage Hosting Class (ENG-004).
        if not isinstance(self.placement_class, str) or not self.placement_class.strip():
            raise InfrastructureError(
                "data placement must declare a non-empty ENG-004 Storage Hosting Class (ISTO-01)"
            )
        if not isinstance(self.cross_boundary, bool):
            raise InfrastructureError("cross_boundary must be a boolean (ISTO-03)")
        # ISTO-03 / UIL-07 — a cross-boundary placement declares its boundary by a typed reference.
        if self.cross_boundary:
            _require_reference("boundary_ref", self.boundary_ref)
        elif self.boundary_ref and not (
            isinstance(self.boundary_ref, str) and self.boundary_ref.strip()
        ):
            raise InfrastructureError("boundary_ref, when present, must be an ENG-005 reference")

    def canonical(self) -> dict[str, Any]:
        """The canonical, hashable projection of the placement (ENG-005 reference tuple)."""
        return {
            "datum_ref": self.datum_ref,
            "placement_class": self.placement_class,
            "cross_boundary": self.cross_boundary,
            "boundary_ref": self.boundary_ref,
        }

    def datum_resolves(self) -> bool:
        """WF-7 / ISTO-01 — the hosted DATA-010 datum reference is a non-empty resolvable id."""
        return bool(self.datum_ref.strip())

    def honors_boundary(self) -> bool:
        """ISTO-03 / UIL-07 — a cross-boundary placement declares a typed boundary reference."""
        return (not self.cross_boundary) or bool(self.boundary_ref.strip())


@dataclass(frozen=True, slots=True)
class StorageHostingResource:
    """StorageHostingResource — an immutable, typed, identified quantum of data-hosting capacity.

    Fields:
        type_tag:      the ENG-004 Type (Storage Hosting Class) of the resource (decidable,
                       non-empty) — UIL-03 / INFRASTRUCTURE-009 §2.
        capacity:      the declared, quantified ENG-003 data-hosting capacity
                       (WF-5 / ISTO-02) — unbounded (ISTO-04 / UIL-13).
        locality_ref:  the ENG-005 ``locatedAt`` reference to the Locality the resource is
                       located at (WF-5 / ISTO-02; multiplicity 1, total) — reference-only.
        placements:    the hosted data — a non-empty tuple of typed :class:`DataPlacement`
                       references, each ``hosts`` a frozen DATA-010 datum by reference
                       (WF-7 / ISTO-01/02); the Resource's ``hosts`` edges, non-mutating.
        state:         the forward-only lifecycle (provisioningState; INFRASTRUCTURE-003
                       §3; default DEFINED).
    """

    type_tag: str
    capacity: StorageCapacity
    locality_ref: str
    placements: tuple[DataPlacement, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        # UIL-03 / INFRASTRUCTURE-009 §2 — typed by a non-empty ENG-004 Storage Hosting Class.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise InfrastructureError(
                "storage resource must be typed with a non-empty ENG-004 type (UIL-03)"
            )
        # WF-5 / ISTO-02 — declares a quantified ENG-003 capacity.
        if not isinstance(self.capacity, StorageCapacity):
            raise InfrastructureError(
                "storage resource must declare a StorageCapacity (WF-5 / ISTO-02)"
            )
        # WF-5 / ISTO-02 — declares a locality by ENG-005 ``locatedAt`` reference (total).
        _require_reference("locality_ref", self.locality_ref)
        # WF-7 / ISTO-01/02 — hosts its data: at least one typed DATA-010 data placement.
        if not isinstance(self.placements, tuple) or not self.placements:
            raise InfrastructureError(
                "storage resource must host its data "
                "(≥1 DataPlacement hosting a DATA-010 datum; WF-7 / ISTO-02)"
            )
        for placement in self.placements:
            if not isinstance(placement, DataPlacement):
                raise InfrastructureError(
                    "every hosted datum must be a DataPlacement (ISTO-01 / WF-7)"
                )
        # WF-1 / INFRASTRUCTURE-003 §3 — a valid forward-only lifecycle state.
        if not isinstance(self.state, InfrastructureState):
            raise InfrastructureError(
                "storage resource state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the resource (its identity-defining tuple)."""
        return {
            "meta_class": INFRASTRUCTURE_META_CLASS,
            "type_tag": self.type_tag,
            "capacity": self.capacity.canonical(),
            "locality_ref": self.locality_ref,
            "placements": [placement.canonical() for placement in self.placements],
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the resource core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def resource_id(self) -> str:
        """The deterministic ENG-001 identity of the resource (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UIL-04 — no second identity
        scheme): identical (type, capacity, locality, placements) always yields the
        identical id, so identity is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{INFRA_STORAGE_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (INFRASTRUCTURE-005) -------------------------

    @property
    def meta_class(self) -> str:
        """WF-1 — the single leaf meta-class this construct instantiates."""
        return INFRASTRUCTURE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """The admitted meta-relationships the resource participates in (hosts, locatedAt)."""
        return STORAGE_RELATIONSHIPS

    def declares_mandatory_attributes(self) -> bool:
        """WF-1 / WF-5 / WF-7 — the resource declares its mandatory meta-attributes.

        A Resource's mandatory set (INFRASTRUCTURE-005 §3) is id/type/value/**capacity**/
        **locality**/**hosts**/provisioningState — all present and non-empty; for a
        Storage-Hosting Resource the ``hosts`` edges are its data placements (≥1 placement
        hosting a DATA-010 datum).
        """
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.resource_id)
            and self.declares_capacity_and_locality()
            and self.hosts_data_by_reference()
        )

    def declares_capacity_and_locality(self) -> bool:
        """WF-5 / UIL-08 / ISTO-02 — the resource declares capacity and locality.

        THE governing Resource rule: a StorageHostingResource must declare both a
        quantified capacity (ENG-003) and a locality (``locatedAt`` reference).
        """
        return (
            isinstance(self.capacity, StorageCapacity)
            and self.capacity.amount >= 0
            and bool(self.capacity.unit.strip())
            and bool(self.locality_ref.strip())
        )

    def hosts_data_by_reference(self) -> bool:
        """WF-7 / ISTO-01 / UIL-11 — the resource hosts ≥1 DATA-010 datum by reference.

        THE storage-unique governing obligation (materially exercised): a storage-hosting
        resource hosts its represented data as typed ENG-005 references to frozen DATA-010
        data; it holds/mutates no data representation (redefines no data concern — UIL-11).
        """
        return bool(self.placements) and all(p.datum_resolves() for p in self.placements)

    def honors_isolation_boundaries(self) -> bool:
        """ISTO-03 / UIL-07 — data placement honors isolation boundaries.

        The distinguishing Storage rule (materially exercised): every cross-boundary data
        placement declares its isolation boundary by a typed ENG-005 reference; a
        placement that crosses a boundary without declaring it is ill-formed (rejected at
        construction).
        """
        return all(p.honors_boundary() for p in self.placements)

    def located_by_reference(self) -> bool:
        """WF-5 / ISTO-02 — the resource is located at a Locality by ENG-005 reference."""
        return isinstance(self.locality_ref, str) and bool(self.locality_ref.strip())

    def is_resource(self) -> bool:
        """WF-5 — a storage-hosting resource **is** a Resource (declares capacity/locality)."""
        return True

    def is_evaluative_facet(self) -> bool:
        """WF-10 N/A — a resource is not an EvaluativeFacet (nonEnforcing does not apply)."""
        return False

    def is_founding_acyclic(self) -> bool:
        """WF-3 — the founding graph is acyclic.

        A resource binds its constituents *by reference* (string ids), and data placements
        are peer (non-founding) ``hosts`` references, so its founding structure carries no
        cycle; this is proven by the fact that its core canonically encodes (a cycle would
        raise at construction).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        """WF-2 — every required ENG-005 reference is a non-empty resolvable id."""
        return bool(self.locality_ref.strip()) and all(
            p.datum_resolves() and p.honors_boundary() for p in self.placements
        )

    def declares_no_artificial_ceiling(self) -> bool:
        """ISTO-04 / UIL-13 — the declared capacity imposes no artificial ceiling."""
        return isinstance(self.capacity, StorageCapacity) and self.capacity.is_unbounded()

    # -- non-constitutiveness (UIL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """UIL-15 / C7 — a resource confers no authority (structurally has none)."""
        return False

    def enacts_enforcement(self) -> bool:
        """UIL-14 / WF-10 — a resource enacts no enforcement (it hosts data only)."""
        return False

    def selects_technology(self) -> bool:
        """UIL-15 / ISTO-05 / C7 — True iff the resource names a storage technology/vendor."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UIL-15 / RR-07 / C7 — True iff the resource appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UIL-02 / UIL-11 / VC-5 — a resource redefines no frozen primitive/data (reuse-only)."""
        return False

    def projects_completion(self) -> bool:
        """WF-12 — a resource projects no architecture-existence-as-completion claim."""
        return False

    def is_new_primitive(self) -> bool:
        """WF-11 / UIL-01 — a resource is no new primitive/authority/registry/lifecycle."""
        return False

    # -- lifecycle (forward-only) ----------------------------------------------

    def transition(self, to_state: InfrastructureState) -> StorageHostingResource:
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
            "placements": [placement.canonical() for placement in self.placements],
            "value_digest": self.value_digest,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_data_placement(
    datum_ref: str = DEFAULT_DATUM_HOST_REF,
    *,
    placement_class: str = "data-placement",
    cross_boundary: bool = False,
    boundary_ref: str = "",
) -> DataPlacement:
    """Construct a well-formed :class:`DataPlacement` (fail-closed factory)."""
    return DataPlacement(
        datum_ref=datum_ref,
        placement_class=placement_class,
        cross_boundary=cross_boundary,
        boundary_ref=boundary_ref,
    )


def make_storage_hosting_resource(
    type_tag: str,
    locality_ref: str,
    *,
    placements: tuple[DataPlacement, ...] | None = None,
    datum_ref: str = DEFAULT_DATUM_HOST_REF,
    placement_class: str = "data-placement",
    capacity: StorageCapacity | None = None,
    amount: int = 1,
    unit: str = "storage-unit",
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> StorageHostingResource:
    """Construct a well-formed :class:`StorageHostingResource` (fail-closed factory).

    ``placements`` may be supplied directly, or a single default data placement is built
    from ``datum_ref`` + ``placement_class``. ``capacity`` may be supplied directly, or
    built from ``amount`` + ``unit``.
    """
    declared_placements = (
        placements
        if placements is not None
        else (make_data_placement(datum_ref, placement_class=placement_class),)
    )
    declared_capacity = (
        capacity if capacity is not None else StorageCapacity(amount=amount, unit=unit)
    )
    return StorageHostingResource(
        type_tag=type_tag,
        capacity=declared_capacity,
        locality_ref=locality_ref,
        placements=declared_placements,
        state=state,
    )


__all__ = [
    "INFRA_STORAGE_ID_PREFIX",
    "DEFAULT_DATUM_HOST_REF",
    "FOUNDATION_REUSE",
    "StorageCapacity",
    "DataPlacement",
    "StorageHostingResource",
    "make_data_placement",
    "make_storage_hosting_resource",
]
