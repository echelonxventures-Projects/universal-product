"""EC3-B13-U06 — The Universal Infrastructure Topology & Distribution constructs.

Realizes the **five** constructs that concern 010 (INFRASTRUCTURE-010) instantiates
over the **two** leaf meta-classes (INFRASTRUCTURE-005 §2/§7):

**Topology meta-class:**
* **Topology** — the structural arrangement of resources→nodes→clusters→environments and
  their connectivity; declares a founding-acyclic ``contains`` graph over ENG-005 references.
* **LocalityMap** — the assignment of constructs to abstract Region/Zone/Location; all
  locality remains abstract (ITOP-04); no provider-specific region/zone named.
* **PlacementRule** — an evaluative rule for assigning constructs to localities/nodes;
  non-enforcing (evaluates, does not enforce).

**Distribution meta-class:**
* **DistributionArrangement** — the deployment configuration of hosted capabilities; hosts
  AF-3/SF-2 by reference (WF-8 / ITOP-03); no transport/CDN/technology selected.
* **DeliveryArrangement** — how hosted experiences/operations are delivered to actors; hosts
  AF-3/SF-2 by reference; no rendering/transport technology selected.

Every construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
FROZEN/CERTIFIED lower layers, and the CERTIFIED Band-13 U01…U05 constructs) and reuses
them *by reference* (UIL-02): identity and value-fidelity are derived through the EC-1
certified deterministic encoding. No new connection construct is introduced (UIL-09 —
ITOP-01); the founding ``dependsOn`` graph is acyclic (WF-3 / ITOP-02); no technology/CDN/
vendor is selected (UIL-15 / ITOP-06) and no authority is conferred.

Constructing any of the five enforces its well-formedness rules and laws fail-closed.
None realizes a Resource (U02/U03/U04), an Environment/ProvisioningProcess (U05),
a Security/Governance facet (U08/U09), or a Resilience/Scaling arrangement (U07); those
are bound only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

# --- EC-1 reuse by reference (UIL-02) ---
from engine.certification.contracts import canonical_json, content_hash

# --- Band-13 shared primitives reused by reference (UIL-02) ---
from infrastructure.capability import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    InfrastructureError,
    _require_reference,
)
from infrastructure.topology_meta import (
    CONSTRUCT_RELATIONSHIPS,
    LIFECYCLE_ORDER,
    SUBSTRATE_REFS,
    InfrastructureState,
)

#: Deterministic id prefixes for the five realized constructs.
INFRA_TOPOLOGY_ID_PREFIX = "UCOS-INFRA-TOPOLOGY"
INFRA_LOCALITYMAP_ID_PREFIX = "UCOS-INFRA-LOCALITYMAP"
INFRA_PLACEMENTRULE_ID_PREFIX = "UCOS-INFRA-PLACEMENTRULE"
INFRA_DISTRIBUTION_ID_PREFIX = "UCOS-INFRA-DISTRIBUTION"
INFRA_DELIVERY_ID_PREFIX = "UCOS-INFRA-DELIVERY"

#: The shared id-family prefix every Topology & Distribution construct id begins with.
INFRA_TOPOLOGY_ID_FAMILY = "UCOS-INFRA-"

#: The default ENG-005 reference to the PL-F2 composition a Topology reuses by reference
#: (ITOP-01). Abstract — names no technology/connector.
DEFAULT_COMPOSITION_REF = "ENG-005:PL-F2:platform.composition.foundation"

#: The default ENG-005 reference to the AF-3/SF-2 capability a Distribution hosts by
#: reference (WF-8 / ITOP-03). Abstract — names no transport/CDN/technology.
DEFAULT_CAPABILITY_REF = "ENG-005:AF-3:application.experience.foundation"

#: The map of frozen-foundation primitives these constructs reuse by reference.
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity)",
    "ENG-002": "python frozen object (immutable objecthood)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity)",
    "ENG-004": "infrastructure.topology type_tag (typed construct)",
    "ENG-005": "reference identifiers (contains/hosts/dependsOn refs; no new connection construct)",
    "PL-F2": "platform composition reused by reference (ITOP-01); topology re-founds none",
    "RL-F2": "runtime workflow/state referenced by Distribution lifecycle",
    "SF-2": "service capability hosted by reference (ITOP-03)",
    "AF-3": "application experience delivered by reference (ITOP-03)",
}


def _selects_technology(core: dict[str, Any]) -> bool:
    """UIL-15 / ITOP-06 — True iff the construct core names a concrete technology/vendor."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)


def _embeds_secret(core: dict[str, Any]) -> bool:
    """UIL-15 / RR-07 — True iff the construct core appears to embed a secret."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _SECRET_MARKERS)


class _InfraConstruct:
    """Shared behavior for every Topology & Distribution construct (UIL-02 reuse).

    A non-dataclass base (``__slots__ = ()``) that the five frozen dataclasses inherit.
    Factors the identity/value/meta-model/non-constitutiveness/lifecycle behavior common to
    all five so it is defined — and covered — **once**.
    """

    __slots__ = ()

    META_CLASS: str = ""
    ID_PREFIX: str = ""

    def canonical_core(self) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    def _required_refs(self) -> tuple[str, ...]:  # pragma: no cover
        raise NotImplementedError

    def declares_mandatory_attributes(self) -> bool:  # pragma: no cover
        raise NotImplementedError

    # -- identity (ENG-001) borne by object (ENG-002) ---

    @property
    def value_digest(self) -> str:
        return content_hash(self.canonical_core())

    @property
    def construct_id(self) -> str:
        return f"{self.ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"  # type: ignore[attr-defined]

    # -- meta-model participation ---

    @property
    def meta_class(self) -> str:
        return self.META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        return CONSTRUCT_RELATIONSHIPS.get(self.META_CLASS, ())

    def is_hosting_structure(self) -> bool:
        return False

    def is_resource(self) -> bool:
        return False

    def is_evaluative_facet(self) -> bool:
        # LocalityMap and PlacementRule are evaluative facets within the Topology meta-class.
        # Check by actual class rather than META_CLASS since both share "Topology" as meta-class.
        return type(self).__name__ in ("LocalityMap", "PlacementRule")

    def is_founding_acyclic(self) -> bool:
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):
            return False
        return True

    def references_resolve(self) -> bool:
        return all(isinstance(ref, str) and bool(ref.strip()) for ref in self._required_refs())

    # -- non-constitutiveness ---

    def confers_authority(self) -> bool:
        return False

    def enacts_enforcement(self) -> bool:
        return self.is_evaluative_facet()

    def selects_technology(self) -> bool:
        return _selects_technology(self.canonical_core())

    def embeds_secret(self) -> bool:
        return _embeds_secret(self.canonical_core())

    def redefines_foundation(self) -> bool:
        return False

    def projects_completion(self) -> bool:
        return False

    def is_new_primitive(self) -> bool:
        return False

    # -- lifecycle ---

    def transition(self, to_state: InfrastructureState):
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

    # -- serialization ---

    def _base_dict(self) -> dict[str, Any]:
        return {
            "construct_id": self.construct_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,  # type: ignore[attr-defined]
            "value_digest": self.value_digest,
            "state": self.state.value,  # type: ignore[attr-defined]
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


# ===========================================================================
# Topology meta-class constructs
# ===========================================================================


@dataclass(frozen=True, slots=True)
class Topology(_InfraConstruct):
    """Topology — the structural arrangement of resources→nodes→clusters→environments.

    The structural arrangement construct (ITOP-01/02): declares a founding-acyclic
    ``contains`` graph over typed ENG-005 references (no new connection construct —
    UIL-09), reuses PL-F2 composition by reference, and maps abstract locality. It names
    no concrete region/zone/technology (UIL-15 / ITOP-04/06).
    """

    META_CLASS = "Topology"
    ID_PREFIX = INFRA_TOPOLOGY_ID_PREFIX

    type_tag: str
    composition_ref: str = DEFAULT_COMPOSITION_REF
    contains: tuple[str, ...] = field(default_factory=tuple)
    locality_map_refs: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "topology")
        _require_reference("composition_ref", self.composition_ref)
        _require_state(self.state, "topology")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "composition_ref": self.composition_ref,
            "contains": list(self.contains),
            "locality_map_refs": list(self.locality_map_refs),
        }

    def _required_refs(self) -> tuple[str, ...]:
        return (self.composition_ref, *self.contains, *self.locality_map_refs)

    def declares_mandatory_attributes(self) -> bool:
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and bool(self.composition_ref.strip())
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "composition_ref": self.composition_ref,
            "contains": list(self.contains),
            "locality_map_refs": list(self.locality_map_refs),
        }


@dataclass(frozen=True, slots=True)
class LocalityMap(_InfraConstruct):
    """LocalityMap — the assignment of constructs to abstract Region/Zone/Location.

    An evaluative, non-enforcing construct (ITOP-04): maps constructs to abstract locality
    designations (Region/Zone/Location) by ENG-005 reference. All locality remains abstract
    — no provider-specific region, zone, datacenter, or edge location is named.
    """

    META_CLASS = "Topology"
    ID_PREFIX = INFRA_LOCALITYMAP_ID_PREFIX

    type_tag: str
    locality_type: str = "region"
    mapping_refs: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "locality map")
        if not isinstance(self.locality_type, str) or not self.locality_type.strip():
            raise InfrastructureError(
                "locality map must declare an abstract locality type (Region/Zone/Location; ITOP-04)"
            )
        _require_state(self.state, "locality map")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "locality_type": self.locality_type,
            "mapping_refs": list(self.mapping_refs),
        }

    def _required_refs(self) -> tuple[str, ...]:
        return tuple(self.mapping_refs)

    def declares_mandatory_attributes(self) -> bool:
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and bool(self.locality_type.strip())
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "locality_type": self.locality_type,
            "mapping_refs": list(self.mapping_refs),
        }


@dataclass(frozen=True, slots=True)
class PlacementRule(_InfraConstruct):
    """PlacementRule — an evaluative rule for assigning constructs to localities/nodes.

    An evaluative, non-enforcing construct (ITOP-02/05): declares placement constraints
    by typed ENG-005 reference. Non-enforcing — it evaluates, it does not enforce (WF-10
    N/A — it declares intent, never enactment).
    """

    META_CLASS = "Topology"
    ID_PREFIX = INFRA_PLACEMENTRULE_ID_PREFIX

    type_tag: str
    rule_kind: str = "affinity"
    target_refs: tuple[str, ...] = field(default_factory=tuple)
    constraint_refs: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "placement rule")
        if not isinstance(self.rule_kind, str) or not self.rule_kind.strip():
            raise InfrastructureError(
                "placement rule must declare a non-empty rule_kind (affinity/anti-affinity/isolation)"
            )
        _require_state(self.state, "placement rule")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "rule_kind": self.rule_kind,
            "target_refs": list(self.target_refs),
            "constraint_refs": list(self.constraint_refs),
        }

    def _required_refs(self) -> tuple[str, ...]:
        return (*self.target_refs, *self.constraint_refs)

    def declares_mandatory_attributes(self) -> bool:
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and bool(self.rule_kind.strip())
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "rule_kind": self.rule_kind,
            "target_refs": list(self.target_refs),
            "constraint_refs": list(self.constraint_refs),
        }


# ===========================================================================
# Distribution meta-class constructs
# ===========================================================================


@dataclass(frozen=True, slots=True)
class DistributionArrangement(_InfraConstruct):
    """DistributionArrangement — the deployment configuration of hosted capabilities.

    The Distribution arrangement (WF-8 / ITOP-03): hosts AF-3/SF-2 capabilities by typed
    ENG-005 reference (multiplicity 1..*), declares distribution strategy, and selects no
    transport/CDN/technology (UIL-15). Forward-only lifecycle.
    """

    META_CLASS = "Distribution"
    ID_PREFIX = INFRA_DISTRIBUTION_ID_PREFIX

    type_tag: str
    hosts: tuple[str, ...] = field(default_factory=tuple)
    strategy: str = "standard"
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "distribution arrangement")
        # WF-8 / ITOP-03 — hosts ≥1 AF-3/SF-2 capability by reference (multiplicity 1..*)
        if not isinstance(self.hosts, tuple) or len(self.hosts) < 1:
            raise InfrastructureError(
                "distribution arrangement must host ≥1 AF-3/SF-2 capability by reference "
                "(WF-8 / ITOP-03)"
            )
        for h in self.hosts:
            _require_reference("distribution hosts member", h)
        if not isinstance(self.strategy, str) or not self.strategy.strip():
            raise InfrastructureError(
                "distribution arrangement must declare a non-empty strategy"
            )
        _require_state(self.state, "distribution arrangement")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "hosts": list(self.hosts),
            "strategy": self.strategy,
            "depends_on": list(self.depends_on),
        }

    def _required_refs(self) -> tuple[str, ...]:
        return (*self.hosts, *self.depends_on)

    def declares_mandatory_attributes(self) -> bool:
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and self.hosts_by_reference()
            and bool(self.strategy.strip())
        )

    def hosts_by_reference(self) -> bool:
        """WF-8 / ITOP-03 — Distribution hosts ≥1 AF-3/SF-2 capability by ENG-005 reference."""
        return bool(self.hosts) and all(bool(r.strip()) for r in self.hosts)

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "hosts": list(self.hosts),
            "strategy": self.strategy,
            "depends_on": list(self.depends_on),
        }


@dataclass(frozen=True, slots=True)
class DeliveryArrangement(_InfraConstruct):
    """DeliveryArrangement — how hosted experiences/operations are delivered to actors.

    The Delivery arrangement (WF-8 / ITOP-03): hosts AF-3/SF-2 capabilities by typed
    ENG-005 reference for delivery to actors; declares delivery mode/channel; selects no
    rendering/transport/CDN/technology (UIL-15). Forward-only lifecycle.
    """

    META_CLASS = "Distribution"
    ID_PREFIX = INFRA_DELIVERY_ID_PREFIX

    type_tag: str
    hosts: tuple[str, ...] = field(default_factory=tuple)
    delivery_mode: str = "direct"
    channel_refs: tuple[str, ...] = field(default_factory=tuple)
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "delivery arrangement")
        # WF-8 / ITOP-03 — hosts ≥1 AF-3/SF-2 capability by reference.
        if not isinstance(self.hosts, tuple) or len(self.hosts) < 1:
            raise InfrastructureError(
                "delivery arrangement must host ≥1 AF-3/SF-2 capability by reference "
                "(WF-8 / ITOP-03)"
            )
        for h in self.hosts:
            _require_reference("delivery hosts member", h)
        if not isinstance(self.delivery_mode, str) or not self.delivery_mode.strip():
            raise InfrastructureError(
                "delivery arrangement must declare a non-empty delivery_mode"
            )
        _require_state(self.state, "delivery arrangement")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "hosts": list(self.hosts),
            "delivery_mode": self.delivery_mode,
            "channel_refs": list(self.channel_refs),
            "depends_on": list(self.depends_on),
        }

    def _required_refs(self) -> tuple[str, ...]:
        return (*self.hosts, *self.channel_refs, *self.depends_on)

    def declares_mandatory_attributes(self) -> bool:
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and self.hosts_by_reference()
            and bool(self.delivery_mode.strip())
        )

    def hosts_by_reference(self) -> bool:
        """WF-8 / ITOP-03 — Delivery hosts ≥1 AF-3/SF-2 capability by ENG-005 reference."""
        return bool(self.hosts) and all(bool(r.strip()) for r in self.hosts)

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "hosts": list(self.hosts),
            "delivery_mode": self.delivery_mode,
            "channel_refs": list(self.channel_refs),
            "depends_on": list(self.depends_on),
        }


# ---------------------------------------------------------------------------
# Shared fail-closed field guards
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


# ---------------------------------------------------------------------------
# Fail-closed factories
# ---------------------------------------------------------------------------


def make_topology(
    type_tag: str,
    *,
    composition_ref: str = DEFAULT_COMPOSITION_REF,
    contains: tuple[str, ...] = (),
    locality_map_refs: tuple[str, ...] = (),
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> Topology:
    """Construct a well-formed :class:`Topology` (fail-closed factory)."""
    return Topology(
        type_tag=type_tag,
        composition_ref=composition_ref,
        contains=contains,
        locality_map_refs=locality_map_refs,
        state=state,
    )


def make_locality_map(
    type_tag: str,
    *,
    locality_type: str = "region",
    mapping_refs: tuple[str, ...] = (),
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> LocalityMap:
    """Construct a well-formed :class:`LocalityMap` (fail-closed factory)."""
    return LocalityMap(
        type_tag=type_tag,
        locality_type=locality_type,
        mapping_refs=mapping_refs,
        state=state,
    )


def make_placement_rule(
    type_tag: str,
    *,
    rule_kind: str = "affinity",
    target_refs: tuple[str, ...] = (),
    constraint_refs: tuple[str, ...] = (),
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> PlacementRule:
    """Construct a well-formed :class:`PlacementRule` (fail-closed factory)."""
    return PlacementRule(
        type_tag=type_tag,
        rule_kind=rule_kind,
        target_refs=target_refs,
        constraint_refs=constraint_refs,
        state=state,
    )


def make_distribution_arrangement(
    type_tag: str,
    *,
    hosts: tuple[str, ...],
    strategy: str = "standard",
    depends_on: tuple[str, ...] = (),
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> DistributionArrangement:
    """Construct a well-formed :class:`DistributionArrangement` (fail-closed factory)."""
    return DistributionArrangement(
        type_tag=type_tag,
        hosts=hosts,
        strategy=strategy,
        depends_on=depends_on,
        state=state,
    )


def make_delivery_arrangement(
    type_tag: str,
    *,
    hosts: tuple[str, ...],
    delivery_mode: str = "direct",
    channel_refs: tuple[str, ...] = (),
    depends_on: tuple[str, ...] = (),
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> DeliveryArrangement:
    """Construct a well-formed :class:`DeliveryArrangement` (fail-closed factory)."""
    return DeliveryArrangement(
        type_tag=type_tag,
        hosts=hosts,
        delivery_mode=delivery_mode,
        channel_refs=channel_refs,
        depends_on=depends_on,
        state=state,
    )


__all__ = [
    "INFRA_TOPOLOGY_ID_PREFIX",
    "INFRA_LOCALITYMAP_ID_PREFIX",
    "INFRA_PLACEMENTRULE_ID_PREFIX",
    "INFRA_DISTRIBUTION_ID_PREFIX",
    "INFRA_DELIVERY_ID_PREFIX",
    "INFRA_TOPOLOGY_ID_FAMILY",
    "DEFAULT_COMPOSITION_REF",
    "DEFAULT_CAPABILITY_REF",
    "FOUNDATION_REUSE",
    "Topology",
    "LocalityMap",
    "PlacementRule",
    "DistributionArrangement",
    "DeliveryArrangement",
    "make_topology",
    "make_locality_map",
    "make_placement_rule",
    "make_distribution_arrangement",
    "make_delivery_arrangement",
]
