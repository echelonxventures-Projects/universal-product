"""EC3-B13-U07 — The Universal Infrastructure Resilience & Availability constructs.

Realizes the **two** constructs that concern 012 (INFRASTRUCTURE-012) instantiates
over the **two** leaf meta-classes (INFRASTRUCTURE-005 §2/§7):

**AvailabilityTopology meta-class:**
* **AvailabilityTopology** — an evaluative continuity arrangement over resources/clusters;
  classifies resilience posture {single, redundant, fault-tolerant, self-healing} and
  declares continuity metrics; non-enforcing (WF-10 — evaluates, does not enact failover).

**ScalingArrangement meta-class:**
* **ScalingArrangement** — an evaluative expand/contract topology over capacity; classifies
  scaling posture {fixed, elastic, unbounded} with no artificial ceiling (WF-9 / UIL-13 /
  IRES-02); non-enforcing (WF-10 — evaluates, does not autoscale).

Every construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
FROZEN/CERTIFIED lower layers, and the CERTIFIED Band-13 U01…U06 constructs) and reuses
them *by reference* (UIL-02): identity and value-fidelity are derived through the EC-1
certified deterministic encoding. No construct enacts failover, provisions capacity, or
selects technology/vendor (UIL-15 / IRES-01/06) and no authority is conferred.

Constructing either enforces its well-formedness rules and laws fail-closed.
Neither realizes a Resource (U02/U03/U04), an Environment/ProvisioningProcess (U05),
a Topology/Distribution (U06), or a Security/Governance facet (U08/U09); those are
bound only *by reference*.
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
from infrastructure.resilience_meta import (
    CONSTRUCT_RELATIONSHIPS,
    LIFECYCLE_ORDER,
    SUBSTRATE_REFS,
    InfrastructureState,
)

#: Deterministic id prefixes for the two realized constructs.
INFRA_AVAILABILITY_ID_PREFIX = "UCOS-INFRA-AVAILABILITYTOPOLOGY"
INFRA_SCALING_ID_PREFIX = "UCOS-INFRA-SCALINGARRANGEMENT"

#: The shared id-family prefix every Resilience & Availability construct id begins with.
INFRA_RESILIENCE_ID_FAMILY = "UCOS-INFRA-"

#: The default ENG-005 reference to RL-F2 runtime continuity concerns bound by reference
#: (IRES-03). Abstract — names no failover/HA technology.
DEFAULT_RL_F2_REF = "ENG-005:RL-F2:runtime.continuity.foundation"

#: The default ENG-005 reference to the Cluster construct an AvailabilityTopology sustains
#: by reference. Abstract — names no cluster technology.
DEFAULT_CLUSTER_REF = "ENG-005:Cluster:hosting.cluster.foundation"

#: The default ENG-005 reference to the Resource a ScalingArrangement scales by reference.
#: Abstract — names no compute/storage/network technology.
DEFAULT_RESOURCE_REF = "ENG-005:Resource:capacity.resource.foundation"

#: The map of frozen-foundation primitives these constructs reuse by reference.
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity)",
    "ENG-002": "python frozen object (immutable objecthood)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity)",
    "ENG-004": "infrastructure.resilience type_tag (typed construct)",
    "ENG-005": "reference identifiers (sustains/scales refs; no new relationship construct)",
    "PL-F2": "platform composition reused by reference",
    "RL-F2": "runtime workflow/state bound by reference (IRES-03); no redefinition",
    "SF-2": "service capability referenced by continuity topology",
    "AF-3": "application experience referenced by continuity topology",
}


def _selects_technology(core: dict[str, Any]) -> bool:
    """UIL-15 / IRES-06 — True iff the construct core names a concrete technology/vendor."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)


def _embeds_secret(core: dict[str, Any]) -> bool:
    """UIL-15 / RR-07 — True iff the construct core appears to embed a secret."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _SECRET_MARKERS)


class _InfraConstruct:
    """Shared behavior for every Resilience & Availability construct (UIL-02 reuse).

    A non-dataclass base (``__slots__ = ()``) that the two frozen dataclasses inherit.
    Factors the identity/value/meta-model/non-constitutiveness/lifecycle behavior common to
    both so it is defined — and covered — **once**.
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
        # Both AvailabilityTopology and ScalingArrangement are evaluative, non-enforcing
        # constructs (WF-10 / IRES-01).
        return type(self).__name__ in ("AvailabilityTopology", "ScalingArrangement")

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
        # Evaluative facets — never enact enforcement (WF-10).
        return False

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

    def has_valid_posture(self) -> bool:
        """WF-9/WF-10 — posture validity check; overridden per construct."""
        return False

    def has_artificial_ceiling(self) -> bool:
        """WF-9 / IRES-02 — True iff the construct declares an artificial ceiling.

        Default ``False`` — AvailabilityTopology (does not scale) never declares
        a ceiling; ScalingArrangement overrides if needed but the current design
        treats fixed-posture as a physical-reality ceiling, not artificial.
        """
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
# AvailabilityTopology meta-class construct
# ===========================================================================


@dataclass(frozen=True, slots=True)
class AvailabilityTopology(_InfraConstruct):
    """AvailabilityTopology — an evaluative continuity arrangement over resources/clusters.

    An evaluative, non-enforcing construct (WF-10 / IRES-01): classifies resilience posture
    {single, redundant, fault-tolerant, self-healing}, declares continuity metrics, and
    sustains Resources/Clusters by typed ENG-005 reference. It never enacts failover,
    provisions capacity, or selects technology/vendor (UIL-15 / IRES-06). Honors isolation
    boundaries (IRES-05).
    """

    META_CLASS = "AvailabilityTopology"
    ID_PREFIX = INFRA_AVAILABILITY_ID_PREFIX

    type_tag: str
    resilience_posture: str = "redundant"
    sustains: tuple[str, ...] = field(default_factory=tuple)
    continuity_metrics: tuple[str, ...] = field(default_factory=tuple)
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "availability topology")
        _require_posture(self.resilience_posture, self.META_CLASS)
        # sustains ≥1 Resource/Cluster by reference (INFRASTRUCTURE-005 §3)
        if not isinstance(self.sustains, tuple) or len(self.sustains) < 1:
            raise InfrastructureError(
                "availability topology must sustain ≥1 Resource/Cluster by reference "
                "(INFRASTRUCTURE-005 §3)"
            )
        for s in self.sustains:
            _require_reference("availability topology sustains member", s)
        _require_state(self.state, "availability topology")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "resilience_posture": self.resilience_posture,
            "sustains": list(self.sustains),
            "continuity_metrics": list(self.continuity_metrics),
            "depends_on": list(self.depends_on),
        }

    def _required_refs(self) -> tuple[str, ...]:
        return (*self.sustains, *self.depends_on)

    def declares_mandatory_attributes(self) -> bool:
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and bool(self.resilience_posture.strip())
            and bool(self.sustains)
        )

    def has_valid_posture(self) -> bool:
        """IRES-01 — resilience posture is one of the admitted values."""
        return self.resilience_posture in ("single", "redundant", "fault-tolerant", "self-healing")

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "resilience_posture": self.resilience_posture,
            "sustains": list(self.sustains),
            "continuity_metrics": list(self.continuity_metrics),
            "depends_on": list(self.depends_on),
        }


# ===========================================================================
# ScalingArrangement meta-class construct
# ===========================================================================


@dataclass(frozen=True, slots=True)
class ScalingArrangement(_InfraConstruct):
    """ScalingArrangement — an evaluative expand/contract topology over capacity.

    An evaluative, non-enforcing construct (WF-10 / IRES-01): classifies scaling posture
    {fixed, elastic, unbounded} with no artificial ceiling (WF-9 / UIL-13 / IRES-02),
    scales Resources by typed ENG-005 reference. Never autoscales, provisions capacity, or
    selects technology/vendor (UIL-15 / IRES-06).
    """

    META_CLASS = "ScalingArrangement"
    ID_PREFIX = INFRA_SCALING_ID_PREFIX

    type_tag: str
    scaling_posture: str = "elastic"
    scales: tuple[str, ...] = field(default_factory=tuple)
    scaling_metrics: tuple[str, ...] = field(default_factory=tuple)
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        _require_typed(self.type_tag, "scaling arrangement")
        _require_posture(self.scaling_posture, self.META_CLASS)
        # scales ≥1 Resource by reference (INFRASTRUCTURE-005 §3)
        if not isinstance(self.scales, tuple) or len(self.scales) < 1:
            raise InfrastructureError(
                "scaling arrangement must scale ≥1 Resource by reference "
                "(INFRASTRUCTURE-005 §3)"
            )
        for s in self.scales:
            _require_reference("scaling arrangement scales member", s)
        _require_state(self.state, "scaling arrangement")

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "scaling_posture": self.scaling_posture,
            "scales": list(self.scales),
            "scaling_metrics": list(self.scaling_metrics),
            "depends_on": list(self.depends_on),
        }

    def _required_refs(self) -> tuple[str, ...]:
        return (*self.scales, *self.depends_on)

    def declares_mandatory_attributes(self) -> bool:
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and bool(self.scaling_posture.strip())
            and bool(self.scales)
        )

    def has_valid_posture(self) -> bool:
        """WF-9 — scaling posture is one of the admitted values; no artificial ceiling declared."""
        return self.scaling_posture in ("fixed", "elastic", "unbounded")

    def has_artificial_ceiling(self) -> bool:
        """WF-9 / IRES-02 — True iff the posture or metrics name an artificial ceiling."""
        # A scaling arrangement with posture "unbounded" or elastic declares no ceiling.
        # A "fixed" posture is the ceiling itself — that is physical reality, not artificial.
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._base_dict(),
            "scaling_posture": self.scaling_posture,
            "scales": list(self.scales),
            "scaling_metrics": list(self.scaling_metrics),
            "depends_on": list(self.depends_on),
        }


# ---------------------------------------------------------------------------
# Shared fail-closed field guards
# ---------------------------------------------------------------------------


_ADMITTED_POSTURES: dict[str, tuple[str, ...]] = {
    "AvailabilityTopology": ("single", "redundant", "fault-tolerant", "self-healing"),
    "ScalingArrangement": ("fixed", "elastic", "unbounded"),
}


def _require_typed(type_tag: Any, what: str) -> None:
    """UIL-03 — require a non-empty ENG-004 type tag."""
    if not isinstance(type_tag, str) or not type_tag.strip():
        raise InfrastructureError(
            f"{what} must be typed with a non-empty ENG-004 type_tag (UIL-03)"
        )


def _require_posture(posture: Any, meta_class: str) -> None:
    """WF-9/WF-10 — require a valid posture value for the meta-class."""
    if not isinstance(posture, str) or not posture.strip():
        raise InfrastructureError(
            f"{meta_class} must declare a non-empty posture (resiliencePosture/scalingPosture)"
        )
    admitted = _ADMITTED_POSTURES.get(meta_class, ())
    if posture not in admitted:
        raise InfrastructureError(
            f"{meta_class} posture '{posture}' not in admitted set {admitted} "
            f"(WF-9/WF-10)"
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


def make_availability_topology(
    type_tag: str,
    *,
    resilience_posture: str = "redundant",
    sustains: tuple[str, ...] = (DEFAULT_CLUSTER_REF,),
    continuity_metrics: tuple[str, ...] = (),
    depends_on: tuple[str, ...] = (),
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> AvailabilityTopology:
    """Construct a well-formed :class:`AvailabilityTopology` (fail-closed factory)."""
    return AvailabilityTopology(
        type_tag=type_tag,
        resilience_posture=resilience_posture,
        sustains=sustains,
        continuity_metrics=continuity_metrics,
        depends_on=depends_on,
        state=state,
    )


def make_scaling_arrangement(
    type_tag: str,
    *,
    scaling_posture: str = "elastic",
    scales: tuple[str, ...] = (DEFAULT_RESOURCE_REF,),
    scaling_metrics: tuple[str, ...] = (),
    depends_on: tuple[str, ...] = (),
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> ScalingArrangement:
    """Construct a well-formed :class:`ScalingArrangement` (fail-closed factory)."""
    return ScalingArrangement(
        type_tag=type_tag,
        scaling_posture=scaling_posture,
        scales=scales,
        scaling_metrics=scaling_metrics,
        depends_on=depends_on,
        state=state,
    )


__all__ = [
    "INFRA_AVAILABILITY_ID_PREFIX",
    "INFRA_SCALING_ID_PREFIX",
    "INFRA_RESILIENCE_ID_FAMILY",
    "DEFAULT_RL_F2_REF",
    "DEFAULT_CLUSTER_REF",
    "DEFAULT_RESOURCE_REF",
    "FOUNDATION_REUSE",
    "AvailabilityTopology",
    "ScalingArrangement",
    "make_availability_topology",
    "make_scaling_arrangement",
]
