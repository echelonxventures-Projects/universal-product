"""EC3-B13-U02 — The Universal Infrastructure Compute construct (ComputeResource).

Realizes the meta-model leaf concept **ComputeResource** (INFRASTRUCTURE-005 §2/§7;
INFRASTRUCTURE-007 §1):

    the implementation-independent abstraction of **execution-hosting capacity** — *where
    and with what capacity* RL-F2 execution is hosted — a quantum of execution-hosting
    capability that **declares a type (Compute Class, ENG-004), a quantified capacity
    (ENG-003), a locality (``locatedAt`` a Locality, by reference) and a hosted execution
    reference** (``hosts`` RL-F2 execution, by reference — ICMP-01 / UIL-10), typed
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
redefined** (UIL-02). It selects no processor/VM/container/orchestrator/hardware
(UIL-12 / UIL-15 / ICMP-05) and confers no authority (UIL-15).

A :class:`ComputeResource` is *immutable* (a frozen object — ENG-002 objecthood),
*typed* (ENG-004), *identified* (ENG-001), *capacity-and-locality-declaring* (WF-5 /
UIL-08 / ICMP-02 — the governing Resource rule), *execution-hosting* (``hosts`` RL-F2 by
reference; ICMP-01 / UIL-10), *unbounded-by-declaration* (ICMP-04 / UIL-13), and holds a
*forward-only lifecycle state* (INFRASTRUCTURE-003 §3). Constructing a
:class:`ComputeResource` enforces the well-formedness rules WF-1/2/3/5/11/12 and the laws
UIL-03/04/05/08/09/10/13/15 fail-closed: an ill-formed compute resource cannot be
instantiated. It realizes **no** Node/Cluster/Environment/ProvisioningProcess/Topology
object — those are separate Band-13 units; this construct binds them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
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
from infrastructure.compute_meta import (
    COMPUTE_RELATIONSHIPS,
    INFRASTRUCTURE_META_CLASS,
    LIFECYCLE_ORDER,
    SUBSTRATE_REFS,
    InfrastructureState,
)

#: The deterministic id prefix for a realized Compute Resource
#: (mirrors EC-1 UCOS-<KIND>-<hex16>).
INFRA_COMPUTE_ID_PREFIX = "UCOS-INFRA-COMPUTE"

#: The default ENG-005 reference to the frozen RL-F2 execution concern a compute resource
#: hosts (ICMP-01 / UIL-10). Abstract — names no processor/VM/container/orchestrator.
DEFAULT_EXECUTION_HOST_REF = "ENG-005:RL-F2:runtime.execution"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UIL-02 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the compute resource)",
    "ENG-003": "engine.certification.contracts.canonical_json (capacity + value fidelity)",
    "ENG-004": "infrastructure.compute type_tag Compute Class (typing)",
    "ENG-005": "reference identifiers (hosts/locatedAt refs; no new construct)",
    "RL-F2": "hosted execution bound by reference (ICMP-01 / UIL-10); no runtime concern redefined",
}


@dataclass(frozen=True, slots=True)
class ComputeCapacity:
    """A declared, quantified amount of execution-hosting capability (ENG-003).

    The INFRASTRUCTURE-007 §2 "Compute Capacity" construct — a technology-neutral,
    quantified value with **no artificial ceiling** (ICMP-04 / UIL-13). ``amount`` is a
    non-negative integer quantity in the (abstract) ``unit``; no upper bound is imposed,
    so scaling is architecturally unbounded (limited only by physical reality).

    Fields:
        amount: the non-negative quantity of execution-hosting capability (ENG-003).
        unit:   the technology-neutral capacity unit (e.g. ``"compute-unit"``) — names no
                vendor instance type, processor, or hardware (UIL-12 / UIL-15).
    """

    amount: int
    unit: str = "compute-unit"

    def __post_init__(self) -> None:
        # ENG-003 / ICMP-02 — a decidable, non-negative quantity (``bool`` is not a quantity).
        if isinstance(self.amount, bool) or not isinstance(self.amount, int) or self.amount < 0:
            raise InfrastructureError(
                "compute capacity amount must be a non-negative integer quantity (ENG-003)"
            )
        # ICMP-02 / UIL-15 — a non-empty, technology-neutral unit.
        if not isinstance(self.unit, str) or not self.unit.strip():
            raise InfrastructureError(
                "compute capacity unit must be a non-empty technology-neutral ENG-003 unit"
            )

    def canonical(self) -> dict[str, Any]:
        """The canonical, hashable projection of the capacity (ENG-003 value)."""
        return {"amount": self.amount, "unit": self.unit}

    def is_unbounded(self) -> bool:
        """ICMP-04 / UIL-13 — the capacity imposes no artificial ceiling (unbounded)."""
        return True


@dataclass(frozen=True, slots=True)
class ComputeResource:
    """ComputeResource — an immutable, typed, identified quantum of execution-hosting capacity.

    Fields:
        type_tag:      the ENG-004 Type (Compute Class) of the resource (decidable,
                       non-empty) — UIL-03 / INFRASTRUCTURE-007 §2.
        capacity:      the declared, quantified ENG-003 execution-hosting capacity
                       (WF-5 / ICMP-02) — unbounded (ICMP-04 / UIL-13).
        locality_ref:  the ENG-005 ``locatedAt`` reference to the Locality the resource is
                       located at (WF-5 / ICMP-02; multiplicity 1, total) — reference-only.
        execution_host_ref: the ENG-005 ``hosts`` reference to the frozen RL-F2 execution
                       concern the resource hosts (ICMP-01 / UIL-10 — the defining reuse),
                       reference-only, non-mutating.
        state:         the forward-only lifecycle (provisioningState; INFRASTRUCTURE-003
                       §3; default DEFINED).
    """

    type_tag: str
    capacity: ComputeCapacity
    locality_ref: str
    execution_host_ref: str = DEFAULT_EXECUTION_HOST_REF
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        # UIL-03 / INFRASTRUCTURE-007 §2 — typed by a non-empty ENG-004 Compute Class.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise InfrastructureError(
                "compute resource must be typed with a non-empty ENG-004 Compute Class (UIL-03)"
            )
        # WF-5 / ICMP-02 — declares a quantified ENG-003 capacity.
        if not isinstance(self.capacity, ComputeCapacity):
            raise InfrastructureError(
                "compute resource must declare a ComputeCapacity (WF-5 / ICMP-02)"
            )
        # WF-5 / ICMP-02 — declares a locality by ENG-005 ``locatedAt`` reference (total).
        _require_reference("locality_ref", self.locality_ref)
        # ICMP-01 / UIL-10 — hosts RL-F2 execution by ENG-005 reference.
        _require_reference("execution_host_ref", self.execution_host_ref)
        # WF-1 / INFRASTRUCTURE-003 §3 — a valid forward-only lifecycle state.
        if not isinstance(self.state, InfrastructureState):
            raise InfrastructureError(
                "compute resource state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the resource (its identity-defining tuple)."""
        return {
            "meta_class": INFRASTRUCTURE_META_CLASS,
            "type_tag": self.type_tag,
            "capacity": self.capacity.canonical(),
            "locality_ref": self.locality_ref,
            "execution_host_ref": self.execution_host_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the resource core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def resource_id(self) -> str:
        """The deterministic ENG-001 identity of the resource (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UIL-04 — no second identity
        scheme): identical (type, capacity, refs) always yields the identical id, so
        identity is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{INFRA_COMPUTE_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (INFRASTRUCTURE-005) -------------------------

    @property
    def meta_class(self) -> str:
        """WF-1 — the single leaf meta-class this construct instantiates."""
        return INFRASTRUCTURE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """The admitted meta-relationships the resource participates in (hosts, locatedAt)."""
        return COMPUTE_RELATIONSHIPS

    def declares_mandatory_attributes(self) -> bool:
        """WF-1 / WF-5 — the resource declares its mandatory meta-attributes.

        A Resource's mandatory set (INFRASTRUCTURE-005 §3) is id/type/value/**capacity**/
        **locality**/**hosts**/provisioningState — all present and non-empty.
        """
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.resource_id)
            and self.declares_capacity_and_locality()
            and bool(self.execution_host_ref.strip())
        )

    def declares_capacity_and_locality(self) -> bool:
        """WF-5 / UIL-08 / ICMP-02 — the resource declares capacity and locality.

        THE governing Resource rule: a ComputeResource must declare both a quantified
        capacity (ENG-003) and a locality (``locatedAt`` reference).
        """
        return (
            isinstance(self.capacity, ComputeCapacity)
            and self.capacity.amount >= 0
            and bool(self.capacity.unit.strip())
            and bool(self.locality_ref.strip())
        )

    def is_resource(self) -> bool:
        """WF-5 — a compute resource **is** a Resource (declares capacity/locality)."""
        return True

    def is_evaluative_facet(self) -> bool:
        """WF-10 N/A — a resource is not an EvaluativeFacet (nonEnforcing does not apply)."""
        return False

    def is_founding_acyclic(self) -> bool:
        """WF-3 / UIL-09 — the founding graph is acyclic.

        A resource binds its constituents *by reference* (string ids), so its founding
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
            for ref in (self.locality_ref, self.execution_host_ref)
        )

    def hosts_execution_by_reference(self) -> bool:
        """ICMP-01 / WF-2 / UIL-10 — hosts the frozen RL-F2 execution concern by reference.

        The resource holds only an ENG-005 reference string to the hosted execution
        concern; it never holds or mutates any runtime construct, and re-founds no
        PLATFORM-012 Runtime.
        """
        return isinstance(self.execution_host_ref, str) and bool(self.execution_host_ref.strip())

    def located_by_reference(self) -> bool:
        """WF-5 / ICMP-02 — the resource is located at a Locality by ENG-005 reference."""
        return isinstance(self.locality_ref, str) and bool(self.locality_ref.strip())

    def declares_no_artificial_ceiling(self) -> bool:
        """ICMP-04 / UIL-13 — the declared capacity imposes no artificial ceiling."""
        return isinstance(self.capacity, ComputeCapacity) and self.capacity.is_unbounded()

    # -- non-constitutiveness (UIL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """UIL-15 / C7 — a resource confers no authority (structurally has none)."""
        return False

    def enacts_enforcement(self) -> bool:
        """UIL-14 / WF-10 — a resource enacts no enforcement (it hosts execution only)."""
        return False

    def selects_technology(self) -> bool:
        """UIL-12 / UIL-15 / ICMP-05 / C7 — True iff the resource names a concrete technology."""
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

    def transition(self, to_state: InfrastructureState) -> ComputeResource:
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
            "execution_host_ref": self.execution_host_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_compute_resource(
    type_tag: str,
    locality_ref: str,
    *,
    capacity: ComputeCapacity | None = None,
    amount: int = 1,
    unit: str = "compute-unit",
    execution_host_ref: str = DEFAULT_EXECUTION_HOST_REF,
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> ComputeResource:
    """Construct a well-formed :class:`ComputeResource` (fail-closed factory).

    ``capacity`` may be supplied directly, or built from ``amount`` + ``unit``.
    """
    declared = capacity if capacity is not None else ComputeCapacity(amount=amount, unit=unit)
    return ComputeResource(
        type_tag=type_tag,
        capacity=declared,
        locality_ref=locality_ref,
        execution_host_ref=execution_host_ref,
        state=state,
    )


__all__ = [
    "INFRA_COMPUTE_ID_PREFIX",
    "DEFAULT_EXECUTION_HOST_REF",
    "FOUNDATION_REUSE",
    "ComputeCapacity",
    "ComputeResource",
    "make_compute_resource",
]
