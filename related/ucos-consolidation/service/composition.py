"""EC3-B11-U06 — The Universal Composition construct (SMC-06).

Realizes the meta-model concept **SMC-06 Composition** (SERVICE-005 §2; SERVICE-003 SOE-06;
SERVICE-010 §3):

    the **structural assembly of services and operations into larger services** — how
    invocable units combine into cohesive providers, distinct from the time-ordered
    coordination of Orchestration — an ENG-002 Object bearing an ENG-001 Identity, classified
    by an ENG-004 Type (SXH-06 = Aggregation / Federation / Delegation), that **composes**
    services/operations by reference (SMR-05, reference-only, acyclic), is **bound-by** a
    composition contract (SMR-02, founding, acyclic), reuses PLATFORM composition/integration
    via **composed-as** (SMR-12, PLATFORM-010/011, by reference), carries cross-composition
    data via **operates-on** (SMR-13, DF-2, by reference), and binds delegated invocation to
    RUNTIME RL-F2 by reference (§7 composition-invoke).

The construct is **additive over the CERTIFIED EC-1 foundation** and reuses it — and the
CERTIFIED SMC-01…05 Service / Capability / Contract / Interface / Operation — *by reference*
(USL-02 / SMI-05): identity and value-fidelity are derived through the EC-1 certified
deterministic encoding, so this module introduces **no second identity scheme and no parallel
value model**. It selects no technology / service-mesh / gateway (USL-15 / SCO-09) and confers
no authority.

A :class:`Composition` is *immutable* (ENG-002 objecthood), *typed* (ENG-004), *identified*
(ENG-001), *classified* (SXH-06 kind), *composes ≥1 member by reference* (SMR-05 / SCO-03),
*bound-by a composition contract* (SMR-02 / SCO-05), *platform-reusing* (SMR-12 / SCO-06),
*data-by-reference* (SMR-13 / SCO-07), holds a *forward-only lifecycle state* (SOS-01…06,
USL-12), and — for the founding kinds Aggregation/Delegation — is *founding-acyclic* (SCO-04 /
SCO-C1: no self-composition, distinct founding members). Nested and recursive composition are
expressed by members that are themselves compositions *by reference*, with founding acyclicity
preventing an unbounded self-founding cycle. Constructing a :class:`Composition` enforces the
structural obligations fail-closed: an ill-formed composition cannot be instantiated. It
realizes/binds no Service, Capability, Contract, Interface, Operation, Orchestration,
Execution, Policy, or Security object — those are separate units; this construct binds them
only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from engine.certification.contracts import canonical_json, content_hash
from service.composition_meta import (
    COMPOSITION_META_CLASS,
    COMPOSITION_RELATIONSHIPS,
    COMPOSITION_SUBSTRATE_REFS,
    FOUNDING_KINDS,
    LIFECYCLE_ORDER,
    CompositionKind,
    ServiceState,
)
from service.service import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    ServiceError,
)

#: The deterministic id prefix for a realized Composition (mirrors EC-1 UCOS-<KIND>-<hex16>).
COMPOSITION_ID_PREFIX = "UCOS-COMPOSITION"

#: The default abstract PLATFORM composition a composition assembles-as (SMR-12; PLATFORM-010).
DEFAULT_COMPOSITION_REF = "ENG-005:PL-F2:PLATFORM-010.composition"

#: The default abstract PLATFORM integration a composition integrates-as (§7; PLATFORM-011).
DEFAULT_INTEGRATION_REF = "ENG-005:PL-F2:PLATFORM-011.integration"

#: The default abstract RUNTIME invocation a composition delegates to (§7 composition-invoke).
DEFAULT_INVOCATION_REF = "ENG-005:RL-F2:runtime.execution"

#: The map of frozen-foundation primitives this construct reuses *by reference*.
COMPOSITION_FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the composition)",
    "ENG-003": "engine.certification.contracts.canonical_json (structural value fidelity)",
    "ENG-004": "service.composition_meta.CompositionKind + type_tag (ENG-004 typing, by ref)",
    "ENG-005": "reference identifiers (member/contract/platform/data refs; no new construct)",
    "PL-F2": "composition/integration bound by reference (SMR-12; PLATFORM-010/011); redefines 0",
    "RL-F2": "delegated invocation bound by reference (§7); no runtime concern redefined",
    "DF-2": "cross-composition data bound by reference (SMR-13); represented data not redefined",
}


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(f"{name} must be a non-empty ENG-005 reference (SMR-02/12/13; §7)")
    return value


def _require_ref_tuple(name: str, values: Any, *, allow_empty: bool = False) -> tuple[str, ...]:
    """Require ``values`` to be a tuple of non-empty ENG-005 reference strings."""
    if not isinstance(values, tuple):
        raise ServiceError(f"{name} must be a tuple of ENG-005 references (SMR-05/13)")
    if not allow_empty and not values:
        raise ServiceError(f"{name} must be non-empty (a composition composes ≥1 member; SCO-03)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise ServiceError(f"{name} entries must be non-empty ENG-005 references (SMR-05/13)")
    return values


@dataclass(frozen=True, slots=True)
class Composition:
    """SMC-06 — an immutable, typed, identified, structural assembly of services/operations.

    Fields:
        type_tag:       the ENG-004 Type of the composition (decidable, non-empty) — SCO-01.
        kind:           the SXH-06 classification (Aggregation / Federation / Delegation; SXC-02).
        member_refs:    tuple of ENG-005 references to the composed services/operations
                        (SMR-05 composes; SOR-05; reference-only; SCO-03). Non-empty.
        contract_ref:   the ENG-005 reference to the composition contract that bounds the
                        assembly (SMR-02 bound-by; SOR-02; founding; SCO-05 / SCO-K2).
        composition_ref: the ENG-005 reference to the PLATFORM composition the assembly
                        composes-as (SMR-12 composed-as; PL-F2 / PLATFORM-010; SCO-06).
        integration_ref: the ENG-005 reference to the PLATFORM integration the assembly
                        integrates-as (§7 composition-integrate; PL-F2 / PLATFORM-011).
        invocation_ref: the ENG-005 reference to the RUNTIME invocation the composition
                        delegates to (§7 composition-invoke; RL-F2, by reference).
        data_refs:      tuple of DF-2-represented cross-composition data references
                        (SMR-13 operates-on; SCO-07 / SCO-C5; by reference). May be empty.
        state:          the SOS-01…06 lifecycle state (forward-only) — USL-12.
    """

    type_tag: str
    kind: CompositionKind
    member_refs: tuple[str, ...]
    contract_ref: str
    composition_ref: str = DEFAULT_COMPOSITION_REF
    integration_ref: str = DEFAULT_INTEGRATION_REF
    invocation_ref: str = DEFAULT_INVOCATION_REF
    data_refs: tuple[str, ...] = ()
    state: ServiceState = ServiceState.DEFINED

    def __post_init__(self) -> None:
        # SCO-K1 / USL-03 / SCO-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ServiceError("composition must be typed: a non-empty ENG-004 type_tag (SCO-01)")
        # SXH-06 / SXC-02 — classified by exactly one composition kind.
        if not isinstance(self.kind, CompositionKind):
            raise ServiceError("composition kind must be an SXH-06 CompositionKind (SXC-02)")
        # SMR-05 / SOR-05 / SCO-03 — composes ≥1 member, by reference.
        _require_ref_tuple("member_refs", self.member_refs)
        # SMR-02 / SOR-02 / SCO-05 — bound by a composition contract, by reference.
        _require_reference("contract_ref", self.contract_ref)
        # SMR-12 / SOR-12 / SCO-06 — composes-as / integrates-as PLATFORM, by reference.
        _require_reference("composition_ref", self.composition_ref)
        _require_reference("integration_ref", self.integration_ref)
        # §7 composition-invoke — delegated invocation bound to RL-F2 by reference.
        _require_reference("invocation_ref", self.invocation_ref)
        # SMR-13 / SOR-13 / SCO-07 — cross-composition data by reference (may be empty).
        _require_ref_tuple("data_refs", self.data_refs, allow_empty=True)
        # V5 / USL-12 — a valid lifecycle state.
        if not isinstance(self.state, ServiceState):
            raise ServiceError("composition state must be a SOS-01…06 ServiceState (USL-12)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the composition (its identity-defining tuple)."""
        return {
            "meta_class": COMPOSITION_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "member_refs": list(self.member_refs),
            "contract_ref": self.contract_ref,
            "composition_ref": self.composition_ref,
            "integration_ref": self.integration_ref,
            "invocation_ref": self.invocation_ref,
            "data_refs": list(self.data_refs),
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the composition core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def composition_id(self) -> str:
        """The deterministic ENG-001 identity of the composition (borne by this object)."""
        return f"{COMPOSITION_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    @property
    def self_ref(self) -> str:
        """The ENG-005 self-reference form of this composition (for self-founding detection)."""
        return f"ENG-005:SOE-06:{self.type_tag}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (SMC-06)."""
        return COMPOSITION_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the SMR-01…13 relationships the composition participates in."""
        return COMPOSITION_RELATIONSHIPS

    def is_founding(self) -> bool:
        """SCO-C1 — True iff this composition's kind founds a structural (DAG) assembly."""
        return self.kind in FOUNDING_KINDS

    def is_founding_acyclic(self) -> bool:
        """V4 / SMK-03 / SCO-04 / SCO-C1 — the founding graph is acyclic (a DAG).

        For a founding kind (Aggregation/Delegation) the composition must not compose
        itself (no self-founding) and its founding members must be distinct; Federation is
        peer (SCO-C2), structurally non-founding. Canonical encodability proves no cycle.
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        if self.is_founding():
            if self.self_ref in self.member_refs:
                return False
            if len(set(self.member_refs)) != len(self.member_refs):
                return False
        return True

    # -- composition-specific obligations --------------------------------------

    def composes_members(self) -> bool:
        """SMR-05 / SOR-05 / SCO-03 — the composition composes ≥1 member, by reference."""
        return bool(self.member_refs) and all(
            isinstance(m, str) and bool(m.strip()) for m in self.member_refs
        )

    def topology_valid(self) -> bool:
        """SCO-C2/C3 — the member arity matches the composition kind.

        * Aggregation — assembles ≥1 operation into a service.
        * Federation  — peer composition of ≥2 services (peer, SOR-05).
        * Delegation  — references exactly one target operation (SCO-C3).
        """
        n = len(self.member_refs)
        if self.kind is CompositionKind.AGGREGATION:
            return n >= 1
        if self.kind is CompositionKind.FEDERATION:
            return n >= 2
        return n == 1  # DELEGATION

    def contract_bound(self) -> bool:
        """SMR-02 / SOR-02 / SCO-05 / SCO-K2 — the composition is bound by a contract."""
        return bool(self.contract_ref.strip())

    def platform_reuse(self) -> bool:
        """SMR-12 / SCO-06 — composes-as/integrates-as PLATFORM by non-empty references."""
        return bool(self.composition_ref.strip()) and bool(self.integration_ref.strip())

    def data_by_reference(self) -> bool:
        """SMR-13 / SCO-07 / SCO-C5 — every cross-composition data ref is a DF-2 reference."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.data_refs)

    def invocation_by_reference(self) -> bool:
        """§7 composition-invoke / USL-10 — delegated invocation binds RL-F2 by reference."""
        return bool(self.invocation_ref.strip())

    def references_resolve(self) -> bool:
        """SMK-05/06/07 / SCO-K4 — every ENG-005 reference is a non-empty resolvable id."""
        singles = (
            self.contract_ref,
            self.composition_ref,
            self.integration_ref,
            self.invocation_ref,
        )
        tuples = (*self.member_refs, *self.data_refs)
        return all(
            isinstance(ref, str) and bool(ref.strip()) for ref in (*singles, *tuples)
        )

    # -- non-constitutiveness (USL-15 / SCO-09) --------------------------------

    def confers_authority(self) -> bool:
        """USL-15 / SCO-09 / C7 — a composition confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """USL-15 / SCO-09 / C7 — True iff the composition names a mesh/gateway/technology."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """USL-15 / RR-07 / C7 — True iff the composition appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """USL-02 / SMI-05 / VC-5 — a composition redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (USL-12, forward-only) --------------------------------------

    def transition(self, to_state: ServiceState) -> Composition:
        """Return a new composition advanced to ``to_state`` (forward-only; USL-12)."""
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
        """A deterministic, serializable projection of the composition."""
        return {
            "composition_id": self.composition_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "member_refs": list(self.member_refs),
            "contract_ref": self.contract_ref,
            "composition_ref": self.composition_ref,
            "integration_ref": self.integration_ref,
            "invocation_ref": self.invocation_ref,
            "data_refs": list(self.data_refs),
            "value_digest": self.value_digest,
            "state": self.state.value,
            "founding": self.is_founding(),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(COMPOSITION_SUBSTRATE_REFS),
        }


def make_composition(
    type_tag: str,
    member_refs: tuple[str, ...],
    contract_ref: str,
    *,
    kind: CompositionKind = CompositionKind.AGGREGATION,
    composition_ref: str = DEFAULT_COMPOSITION_REF,
    integration_ref: str = DEFAULT_INTEGRATION_REF,
    invocation_ref: str = DEFAULT_INVOCATION_REF,
    data_refs: tuple[str, ...] = (),
    state: ServiceState = ServiceState.DEFINED,
) -> Composition:
    """Construct a well-formed :class:`Composition` (fail-closed factory)."""
    return Composition(
        type_tag=type_tag,
        kind=kind,
        member_refs=member_refs,
        contract_ref=contract_ref,
        composition_ref=composition_ref,
        integration_ref=integration_ref,
        invocation_ref=invocation_ref,
        data_refs=data_refs,
        state=state,
    )


__all__ = [
    "COMPOSITION_ID_PREFIX",
    "DEFAULT_COMPOSITION_REF",
    "DEFAULT_INTEGRATION_REF",
    "DEFAULT_INVOCATION_REF",
    "COMPOSITION_FOUNDATION_REUSE",
    "Composition",
    "make_composition",
]
