"""EC3-B13-U05 — The Universal Infrastructure Environment & Provisioning constructs.

Realizes the **six** meta-model leaf concepts that concern 011 instantiates
(INFRASTRUCTURE-005 §2/§7; INFRASTRUCTURE-011 §1/§2):

* **Locality** — the abstract Region/Zone/Location where hosting occurs (foundational).
* **IsolationBoundary** — the line delimiting what an environment owns/hosts/exposes.
* **Node** — a unit of hosting capacity that ``contains`` Resources and is ``locatedAt`` a
  Locality (HostingStructure).
* **Cluster** — a cohesive grouping that ``contains`` Nodes and is ``locatedAt`` a Locality
  (HostingStructure).
* **Environment** — a bounded, named, isolated hosting context that declares **exactly one**
  IsolationBoundary (WF-4 / IENV-01), ``contains`` Clusters/Nodes/Resources, and is
  ``locatedAt`` a Locality (HostingStructure).
* **ProvisioningProcess** — the ``defined → provisioned → active → decommissioned`` lifecycle
  that ``provisions`` Resources and **binds an RL-F2 workflow by reference** (WF-6 / IENV-04 /
  UIL-10); it re-founds no PLATFORM-012/013 Runtime/Deployment and defines no new lifecycle.

Every construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
FROZEN/CERTIFIED lower layers, and the CERTIFIED Band-13 U01 shared primitives) and reuses
them *by reference* (UIL-02): identity and value-fidelity are derived through the EC-1
certified deterministic encoding (:func:`~engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`) — the same discipline that produces
every EC-1 identity — so this module introduces **no second identity scheme and no parallel
value model**. The shared infrastructure-layer primitives
(:class:`~infrastructure.capability.InfrastructureError`, the reference helper, and the
technology/secret markers) are **imported from the first Band-13 unit and never redefined**
(UIL-02). All containment is expressed as typed ENG-005 references (no new connection
construct — UIL-09); the founding ``contains`` graph is **acyclic** (WF-3 / IENV-03); no
IaC/cloud/orchestrator/vendor is selected (UIL-15 / IENV-06) and no authority is conferred
(UIL-15). The *act* of provisioning is out of scope — only its implementation-independent
lifecycle *as an architectural concept* is realized (IENV-05).

Constructing any of these six enforces its well-formedness rules and laws fail-closed: an
ill-formed construct cannot be instantiated. None of the six realizes a Resource
(Compute/Network/StorageHosting are U02/U03/U04), a DATA-010 datum, a Topology/Distribution
(U06), or a Security/Governance facet (U08/U09); those are bound only *by reference*.
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
from infrastructure.environment_meta import (
    CONSTRUCT_RELATIONSHIPS,
    LIFECYCLE_ORDER,
    SUBSTRATE_REFS,
    InfrastructureState,
)

#: The deterministic id prefixes for the six realized constructs (mirror EC-1
#: UCOS-<KIND>-<hex16>). Each construct instantiates exactly one leaf meta-class (WF-1) and
#: bears an id under its own prefix within the shared ``UCOS-INFRA-`` family.
INFRA_LOCALITY_ID_PREFIX = "UCOS-INFRA-LOCALITY"
INFRA_BOUNDARY_ID_PREFIX = "UCOS-INFRA-BOUNDARY"
INFRA_NODE_ID_PREFIX = "UCOS-INFRA-NODE"
INFRA_CLUSTER_ID_PREFIX = "UCOS-INFRA-CLUSTER"
INFRA_ENVIRONMENT_ID_PREFIX = "UCOS-INFRA-ENVIRONMENT"
INFRA_PROVISIONING_ID_PREFIX = "UCOS-INFRA-PROVISIONING"

#: The shared id-family prefix every Environment & Provisioning construct id begins with.
INFRA_ENV_ID_FAMILY = "UCOS-INFRA-"

#: The default ENG-005 reference to the RL-F2 workflow a ProvisioningProcess binds
#: (IENV-04 / UIL-10). Abstract — names no IaC/orchestrator/scheduler engine.
DEFAULT_PROVISIONING_WORKFLOW_REF = "ENG-005:RL-F2:runtime.workflow.provisioning"

#: The map of frozen-foundation primitives these constructs reuse *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UIL-02 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the construct)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity, no parallel model)",
    "ENG-004": "infrastructure.environment type_tag (typed construct)",
    "ENG-005": "reference identifiers (contains / locatedAt / boundary / provisions refs; "
    "no new construct)",
    "RL-F2": "provisioning workflow/state bound by reference (IENV-04 / UIL-10); no runtime "
    "concern redefined, no PLATFORM-012/013 re-founded",
}


def _selects_technology(core: dict[str, Any]) -> bool:
    """UIL-15 / IENV-06 — True iff the construct core names a concrete technology/vendor."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)


def _embeds_secret(core: dict[str, Any]) -> bool:
    """UIL-15 / RR-07 — True iff the construct core appears to embed a secret."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _SECRET_MARKERS)


class _InfraConstruct:
    """Shared behavior for every Environment & Provisioning construct (UIL-02 reuse).

    A non-dataclass base (``__slots__ = ()``) that the six frozen dataclasses inherit. It
    factors the identity/value/meta-model/non-constitutiveness/lifecycle behavior common to
    all six so it is defined — and covered — **once**, never redefined per construct (the
    same reuse-by-reference discipline this layer applies to the frozen foundations).

    Subclasses declare two class attributes (``META_CLASS`` and ``ID_PREFIX``) and implement
    :meth:`canonical_core`, :meth:`declares_mandatory_attributes`, and :meth:`_required_refs`.
    """

    __slots__ = ()

    #: The single leaf meta-class this construct instantiates (WF-1) — set per subclass.
    META_CLASS: str = ""
    #: The deterministic id prefix for this construct — set per subclass.
    ID_PREFIX: str = ""

    # -- abstract-ish surface (each subclass provides these) -------------------

    def canonical_core(self) -> dict[str, Any]:  # pragma: no cover - overridden
        raise NotImplementedError

    def _required_refs(self) -> tuple[str, ...]:  # pragma: no cover - overridden
        raise NotImplementedError

    def declares_mandatory_attributes(self) -> bool:  # pragma: no cover - overridden
        raise NotImplementedError

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the construct core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def construct_id(self) -> str:
        """The deterministic ENG-001 identity of the construct (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UIL-04 — no second identity
        scheme): an identical core always yields the identical id, so identity is
        reproducible and byte-stable (determinism, VC-4).
        """
        return f"{self.ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"  # type: ignore[attr-defined]

    # -- meta-model participation (INFRASTRUCTURE-005) -------------------------

    @property
    def meta_class(self) -> str:
        """WF-1 — the single leaf meta-class this construct instantiates."""
        return self.META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """The admitted meta-relationships this construct participates in (UIMM §4)."""
        return CONSTRUCT_RELATIONSHIPS[self.META_CLASS]

    def is_hosting_structure(self) -> bool:
        """UIMM §2 — True iff the construct is a HostingStructure (Node/Cluster/Env)."""
        return self.META_CLASS in ("Node", "Cluster", "Environment")

    def is_resource(self) -> bool:
        """WF-5 N/A — none of the six constructs is a Resource (no capacity meta-attribute)."""
        return False

    def is_evaluative_facet(self) -> bool:
        """WF-10 N/A — none of the six constructs is an EvaluativeFacet (nonEnforcing N/A)."""
        return False

    def is_founding_acyclic(self) -> bool:
        """WF-3 / UIL-09 — the founding graph is acyclic.

        Each construct binds its constituents *by reference* (string ids), so its own
        founding structure carries no cycle; this is proven by the fact that its core
        canonically encodes (a cycle would raise at construction). The **composition-level**
        acyclicity of the ``contains`` graph across constructs is proven separately by
        :func:`containment_graph_acyclic`.
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        """WF-2 — every required ENG-005 reference is a non-empty resolvable id."""
        return all(isinstance(ref, str) and bool(ref.strip()) for ref in self._required_refs())

    # -- non-constitutiveness (UIL-14 / UIL-15) --------------------------------

    def confers_authority(self) -> bool:
        """UIL-15 / C7 — a construct confers no authority (structurally has none)."""
        return False

    def enacts_enforcement(self) -> bool:
        """UIL-14 / WF-10 — a construct enacts no enforcement (it hosts/locates/provisions only)."""
        return False

    def selects_technology(self) -> bool:
        """UIL-15 / IENV-06 / C7 — True iff the construct names a concrete technology/vendor."""
        return _selects_technology(self.canonical_core())

    def embeds_secret(self) -> bool:
        """UIL-15 / RR-07 / C7 — True iff the construct appears to embed a secret."""
        return _embeds_secret(self.canonical_core())

    def redefines_foundation(self) -> bool:
        """UIL-02 / VC-5 — a construct redefines no frozen primitive (reuse-only)."""
        return False

    def projects_completion(self) -> bool:
        """WF-12 — a construct projects no architecture-existence-as-completion claim."""
        return False

    def is_new_primitive(self) -> bool:
        """WF-11 / UIL-01 — a construct is no new primitive/authority/registry/lifecycle."""
        return False

    # -- lifecycle (forward-only) ----------------------------------------------

    def transition(self, to_state: InfrastructureState):
        """Return a new construct advanced to ``to_state`` (forward-only).

        Raises:
            InfrastructureError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, InfrastructureState):
            raise InfrastructureError(
                "target state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )
        here = LIFECYCLE_ORDER.index(self.state)  # type: ignore[attr-defined]
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise InfrastructureError(
                f"lifecycle is forward-only: {self.state.value} → {to_state.value} is backward"  # type: ignore[attr-defined]
            )
        return replace(self, state=to_state)  # type: ignore[type-var]

    # -- serialization ----------------------------------------------------------

    def _base_dict(self) -> dict[str, Any]:
        """The common serializable projection shared by every construct."""
        return {
            "construct_id": self.construct_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,  # type: ignore[attr-defined]
            "value_digest": self.value_digest,
            "state": self.state.value,  # type: ignore[attr-defined]
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


@dataclass(frozen=True, slots=True)
class Locality(_InfraConstruct):
    """Locality — the abstract Region/Zone/Location where hosting occurs (foundational).

    A foundational construct: typed (ENG-004), identified (ENG-001), object-borne (ENG-002),
    with no founding relationship (it is the *target* of ``locatedAt``). It names no concrete
    region/zone/datacenter/provider (UIL-15 / IENV-06).
    """

    META_CLASS = "Locality"
    ID_PREFIX = INFRA_LOCALITY_ID_PREFIX

    type_tag: str
    scope: str = "region"
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise InfrastructureError(
                "locality must be typed with a non-empty ENG-004 type_tag (UIL-03)"
            )
        if not isinstance(self.scope, str) or not self.scope.strip():
            raise InfrastructureError(
                "locality must declare a non-empty abstract scope (Region/Zone/Location)"
            )
        if not isinstance(self.state, InfrastructureState):
            raise InfrastructureError(
                "locality state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )

    def canonical_core(self) -> dict[str, Any]:
        return {"meta_class": self.META_CLASS, "type_tag": self.type_tag, "scope": self.scope}

    def _required_refs(self) -> tuple[str, ...]:
        return ()

    def declares_mandatory_attributes(self) -> bool:
        """WF-1 — a Locality's mandatory set is id/type/value (no boundary/locality/contains)."""
        return bool(self.type_tag.strip()) and bool(self.value_digest) and bool(self.construct_id)

    def to_dict(self) -> dict[str, Any]:
        return {**self._base_dict(), "scope": self.scope}


@dataclass(frozen=True, slots=True)
class IsolationBoundary(_InfraConstruct):
    """IsolationBoundary — the line delimiting what an environment owns/hosts/exposes.

    A foundational construct: typed, identified, object-borne, participating in no founding
    relationship (it is the *target* of an Environment's ``boundary`` meta-attribute). It is
    the construct that makes an Environment *isolated* (UIL-07 / IENV-01).
    """

    META_CLASS = "IsolationBoundary"
    ID_PREFIX = INFRA_BOUNDARY_ID_PREFIX

    type_tag: str
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise InfrastructureError(
                "isolation boundary must be typed with a non-empty ENG-004 type_tag (UIL-03)"
            )
        if not isinstance(self.state, InfrastructureState):
            raise InfrastructureError(
                "isolation boundary state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )

    def canonical_core(self) -> dict[str, Any]:
        return {"meta_class": self.META_CLASS, "type_tag": self.type_tag}

    def _required_refs(self) -> tuple[str, ...]:
        return ()

    def declares_mandatory_attributes(self) -> bool:
        """WF-1 — an IsolationBoundary's mandatory set is id/type/value."""
        return bool(self.type_tag.strip()) and bool(self.value_digest) and bool(self.construct_id)

    def to_dict(self) -> dict[str, Any]:
        return self._base_dict()


@dataclass(frozen=True, slots=True)
class Node(_InfraConstruct):
    """Node — a unit of hosting capacity that ``contains`` Resources, ``locatedAt`` a Locality.

    A HostingStructure: typed, identified, object-borne; declares a ``locality`` (ENG-005
    ``locatedAt`` reference, multiplicity 1, total) and ``contains`` one or more constructs
    (Resources) by typed ENG-005 reference (multiplicity 1..*, founding-acyclic). It hosts
    no execution/data itself — that is the referenced Resource's concern.
    """

    META_CLASS = "Node"
    ID_PREFIX = INFRA_NODE_ID_PREFIX

    type_tag: str
    locality_ref: str
    contains: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "node")
        _require_reference("locality_ref", self.locality_ref)
        _require_contains(self.contains, "node", minimum=1)
        _require_state(self.state, "node")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "locality_ref": self.locality_ref,
            "contains": list(self.contains),
        }

    def _required_refs(self) -> tuple[str, ...]:
        return (self.locality_ref, *self.contains)

    def declares_mandatory_attributes(self) -> bool:
        """WF-1 — a Node declares id/type/value/**locality**/**contains** (HostingStructure set)."""
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and self.located_by_reference()
            and self.contains_by_reference()
        )

    def located_by_reference(self) -> bool:
        """The Node declares its Locality by an ENG-005 ``locatedAt`` reference (total)."""
        return isinstance(self.locality_ref, str) and bool(self.locality_ref.strip())

    def contains_by_reference(self) -> bool:
        """The Node ``contains`` ≥1 construct by typed ENG-005 reference (multiplicity 1..*)."""
        return bool(self.contains) and all(bool(r.strip()) for r in self.contains)

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "locality_ref": self.locality_ref,
            "contains": list(self.contains),
        }


@dataclass(frozen=True, slots=True)
class Cluster(_InfraConstruct):
    """Cluster — a cohesive grouping that ``contains`` Nodes, ``locatedAt`` a Locality.

    A HostingStructure with the same meta-shape as :class:`Node` (locality + contains), whose
    contained members are Nodes (by ENG-005 reference). Founding-acyclic (WF-3 / IENV-03).
    """

    META_CLASS = "Cluster"
    ID_PREFIX = INFRA_CLUSTER_ID_PREFIX

    type_tag: str
    locality_ref: str
    contains: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "cluster")
        _require_reference("locality_ref", self.locality_ref)
        _require_contains(self.contains, "cluster", minimum=1)
        _require_state(self.state, "cluster")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "locality_ref": self.locality_ref,
            "contains": list(self.contains),
        }

    def _required_refs(self) -> tuple[str, ...]:
        return (self.locality_ref, *self.contains)

    def declares_mandatory_attributes(self) -> bool:
        """WF-1 — a Cluster declares id/type/value/locality/contains (HostingStructure set)."""
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and self.located_by_reference()
            and self.contains_by_reference()
        )

    def located_by_reference(self) -> bool:
        """The Cluster declares its Locality by an ENG-005 ``locatedAt`` reference (total)."""
        return isinstance(self.locality_ref, str) and bool(self.locality_ref.strip())

    def contains_by_reference(self) -> bool:
        """The Cluster ``contains`` ≥1 Node by typed ENG-005 reference (multiplicity 1..*)."""
        return bool(self.contains) and all(bool(r.strip()) for r in self.contains)

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "locality_ref": self.locality_ref,
            "contains": list(self.contains),
        }


@dataclass(frozen=True, slots=True)
class Environment(_InfraConstruct):
    """Environment — a bounded, named, isolated hosting context (declares one boundary).

    A HostingStructure that declares **exactly one** IsolationBoundary (WF-4 / IENV-01 — the
    governing Environment rule, materially exercised), ``contains`` one or more constructs
    (Clusters/Nodes/Resources) by ENG-005 reference, and is ``locatedAt`` a Locality. Its
    founding ``contains`` graph is acyclic (WF-3 / IENV-03).
    """

    META_CLASS = "Environment"
    ID_PREFIX = INFRA_ENVIRONMENT_ID_PREFIX

    type_tag: str
    boundary_ref: str
    locality_ref: str
    contains: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "environment")
        # WF-4 / IENV-01 — declares exactly one isolation boundary (a single ENG-005 reference).
        _require_reference("boundary_ref", self.boundary_ref)
        _require_reference("locality_ref", self.locality_ref)
        _require_contains(self.contains, "environment", minimum=1)
        _require_state(self.state, "environment")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "boundary_ref": self.boundary_ref,
            "locality_ref": self.locality_ref,
            "contains": list(self.contains),
        }

    def _required_refs(self) -> tuple[str, ...]:
        return (self.boundary_ref, self.locality_ref, *self.contains)

    def declares_mandatory_attributes(self) -> bool:
        """WF-1 / WF-4 — an Environment declares id/type/value/boundary/locality/contains."""
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and self.declares_single_boundary()
            and self.located_by_reference()
            and self.contains_by_reference()
        )

    def declares_single_boundary(self) -> bool:
        """WF-4 / UIL-07 / IENV-01 — the Environment declares exactly one isolation boundary.

        THE governing, materially-exercised Environment rule: a single, non-empty ENG-005
        ``boundary`` reference. The single-cardinality is structural (one ``boundary_ref``
        field), so an Environment can never declare zero or many boundaries.
        """
        return isinstance(self.boundary_ref, str) and bool(self.boundary_ref.strip())

    def located_by_reference(self) -> bool:
        """The Environment declares its Locality by an ENG-005 ``locatedAt`` reference (total)."""
        return isinstance(self.locality_ref, str) and bool(self.locality_ref.strip())

    def contains_by_reference(self) -> bool:
        """The Environment ``contains`` ≥1 construct by typed ENG-005 reference (1..*)."""
        return bool(self.contains) and all(bool(r.strip()) for r in self.contains)

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "boundary_ref": self.boundary_ref,
            "locality_ref": self.locality_ref,
            "contains": list(self.contains),
        }


@dataclass(frozen=True, slots=True)
class ProvisioningProcess(_InfraConstruct):
    """ProvisioningProcess — the provisioning lifecycle bound to an RL-F2 workflow by reference.

    The ``defined → provisioned → active → decommissioned`` lifecycle (INFRASTRUCTURE-003 §3)
    that ``provisions`` one or more Resources by ENG-005 reference (multiplicity 1..*) and
    **binds an RL-F2 workflow by reference** (WF-6 / IENV-04 / UIL-10 — the governing rule,
    materially exercised): it re-founds no PLATFORM-012/013 Runtime/Deployment and defines no
    new lifecycle model. The *act* of provisioning is out of scope (IENV-05) — only the
    lifecycle *as an architectural concept* is realized. ``state`` is the mandatory
    ``provisioningState`` meta-attribute (INFRASTRUCTURE-005 §3).
    """

    META_CLASS = "ProvisioningProcess"
    ID_PREFIX = INFRA_PROVISIONING_ID_PREFIX

    type_tag: str
    provisions: tuple[str, ...] = field(default_factory=tuple)
    workflow_ref: str = DEFAULT_PROVISIONING_WORKFLOW_REF
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "provisioning process")
        _require_contains(self.provisions, "provisioning process", minimum=1, edge="provisions")
        # WF-6 / IENV-04 / UIL-10 — binds an RL-F2 workflow by reference.
        _require_reference("workflow_ref", self.workflow_ref)
        _require_state(self.state, "provisioning process")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "provisions": list(self.provisions),
            "workflow_ref": self.workflow_ref,
        }

    def _required_refs(self) -> tuple[str, ...]:
        return (self.workflow_ref, *self.provisions)

    def declares_mandatory_attributes(self) -> bool:
        """WF-1 — a ProvisioningProcess declares id/type/value/provisioningState/provisions."""
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and isinstance(self.state, InfrastructureState)
            and self.provisions_by_reference()
            and self.binds_runtime_workflow()
        )

    def binds_runtime_workflow(self) -> bool:
        """WF-6 / IENV-04 / UIL-10 — the process binds an RL-F2 workflow by ENG-005 reference.

        THE governing, materially-exercised ProvisioningProcess rule: a non-empty ENG-005
        ``workflow`` reference to the frozen RL-F2 workflow/state concern; the process
        re-founds no PLATFORM-012/013 and defines no new lifecycle model.
        """
        return isinstance(self.workflow_ref, str) and bool(self.workflow_ref.strip())

    def provisions_by_reference(self) -> bool:
        """The process ``provisions`` ≥1 Resource by typed ENG-005 reference (multiplicity 1..*)."""
        return bool(self.provisions) and all(bool(r.strip()) for r in self.provisions)

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "provisions": list(self.provisions),
            "workflow_ref": self.workflow_ref,
        }


# ---------------------------------------------------------------------------
# Shared fail-closed field guards (used by the HostingStructure / Process constructs)
# ---------------------------------------------------------------------------


def _require_typed(type_tag: Any, what: str) -> None:
    """UIL-03 — require a non-empty ENG-004 type tag."""
    if not isinstance(type_tag, str) or not type_tag.strip():
        raise InfrastructureError(
            f"{what} must be typed with a non-empty ENG-004 type_tag (UIL-03)"
        )


def _require_state(state: Any, what: str) -> None:
    """INFRASTRUCTURE-003 §3 — require a valid forward-only lifecycle state."""
    if not isinstance(state, InfrastructureState):
        raise InfrastructureError(
            f"{what} state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
        )


def _require_contains(members: Any, what: str, *, minimum: int, edge: str = "contains") -> None:
    """WF-2/WF-3 / IENV-03 — require a tuple of ≥``minimum`` non-empty ENG-005 references."""
    if not isinstance(members, tuple) or len(members) < minimum:
        raise InfrastructureError(
            f"{what} must declare ≥{minimum} {edge} reference(s) (multiplicity 1..*; WF-2)"
        )
    for member in members:
        _require_reference(f"{what} {edge} member", member)


def containment_graph_acyclic(constructs: tuple[_InfraConstruct, ...]) -> bool:
    """WF-3 / UIL-09 / IENV-03 — prove the composition ``contains`` graph is acyclic.

    Builds the directed edge set from every HostingStructure's ``contains`` references
    (container id → contained ref) and runs a deterministic three-colour DFS cycle detector
    over it (the same discipline as the Application Composition unit). A cycle — direct or
    transitive — yields ``False``; a well-formed downward-only containment yields ``True``.
    Constructs whose contained ids are external (e.g. a Node containing a Resource realized
    by U02/U03/U04) simply terminate the traversal (no outgoing edge from that ref).
    """
    edges: dict[str, tuple[str, ...]] = {}
    for c in constructs:
        if c.is_hosting_structure():
            edges[c.construct_id] = tuple(c.contains)  # type: ignore[attr-defined]

    WHITE, GREY, BLACK = 0, 1, 2
    colour: dict[str, int] = {node: WHITE for node in edges}

    def visit(node: str) -> bool:
        colour[node] = GREY
        for nxt in edges.get(node, ()):  # external refs have no outgoing edge
            state = colour.get(nxt, BLACK)  # unknown (external) ref → terminal (BLACK)
            if state == GREY:
                return False  # back-edge → cycle
            if state == WHITE and not visit(nxt):
                return False
        colour[node] = BLACK
        return True

    return all(visit(node) for node in edges if colour[node] == WHITE)


# ---------------------------------------------------------------------------
# Fail-closed factories
# ---------------------------------------------------------------------------


def make_locality(
    type_tag: str,
    *,
    scope: str = "region",
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> Locality:
    """Construct a well-formed :class:`Locality` (fail-closed factory)."""
    return Locality(type_tag=type_tag, scope=scope, state=state)


def make_isolation_boundary(
    type_tag: str, *, state: InfrastructureState = InfrastructureState.DEFINED
) -> IsolationBoundary:
    """Construct a well-formed :class:`IsolationBoundary` (fail-closed factory)."""
    return IsolationBoundary(type_tag=type_tag, state=state)


def make_node(
    type_tag: str,
    locality_ref: str,
    *,
    contains: tuple[str, ...],
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> Node:
    """Construct a well-formed :class:`Node` (fail-closed factory)."""
    return Node(type_tag=type_tag, locality_ref=locality_ref, contains=contains, state=state)


def make_cluster(
    type_tag: str,
    locality_ref: str,
    *,
    contains: tuple[str, ...],
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> Cluster:
    """Construct a well-formed :class:`Cluster` (fail-closed factory)."""
    return Cluster(type_tag=type_tag, locality_ref=locality_ref, contains=contains, state=state)


def make_environment(
    type_tag: str,
    boundary_ref: str,
    locality_ref: str,
    *,
    contains: tuple[str, ...],
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> Environment:
    """Construct a well-formed :class:`Environment` (fail-closed factory)."""
    return Environment(
        type_tag=type_tag,
        boundary_ref=boundary_ref,
        locality_ref=locality_ref,
        contains=contains,
        state=state,
    )


def make_provisioning_process(
    type_tag: str,
    *,
    provisions: tuple[str, ...],
    workflow_ref: str = DEFAULT_PROVISIONING_WORKFLOW_REF,
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> ProvisioningProcess:
    """Construct a well-formed :class:`ProvisioningProcess` (fail-closed factory)."""
    return ProvisioningProcess(
        type_tag=type_tag, provisions=provisions, workflow_ref=workflow_ref, state=state
    )


__all__ = [
    "INFRA_LOCALITY_ID_PREFIX",
    "INFRA_BOUNDARY_ID_PREFIX",
    "INFRA_NODE_ID_PREFIX",
    "INFRA_CLUSTER_ID_PREFIX",
    "INFRA_ENVIRONMENT_ID_PREFIX",
    "INFRA_PROVISIONING_ID_PREFIX",
    "INFRA_ENV_ID_FAMILY",
    "DEFAULT_PROVISIONING_WORKFLOW_REF",
    "FOUNDATION_REUSE",
    "Locality",
    "IsolationBoundary",
    "Node",
    "Cluster",
    "Environment",
    "ProvisioningProcess",
    "containment_graph_acyclic",
    "make_locality",
    "make_isolation_boundary",
    "make_node",
    "make_cluster",
    "make_environment",
    "make_provisioning_process",
]
