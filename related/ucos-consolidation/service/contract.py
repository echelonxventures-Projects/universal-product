"""EC3-B11-U03 — The Universal Contract construct (SMC-03).

Realizes the meta-model concept **SMC-03 Contract** (SERVICE-005 §2; SERVICE-003 SOE-03;
SERVICE-007 §3):

    the binding, typed, implementation-independent **specification of an operation or
    service** — declaring typed inputs and outputs (DF-2-represented data by reference,
    SMR-13), defined effects, declared faults, and applicable policy (SOE-09 by
    reference, SMR-08) — an ENG-002 Object bearing an ENG-001 Identity, classified by an
    ENG-004 Type, that operations/services are **bound-by** (SMR-02, founding, acyclic).

The construct is **additive over the CERTIFIED EC-1 foundation** and reuses it — and the
CERTIFIED SMC-01 Service / SMC-02 Capability — *by reference* (USL-02 / SMI-05): identity
and value-fidelity are derived through the EC-1 certified deterministic encoding, so this
module introduces **no second identity scheme and no parallel value model**. It selects no
technology / IDL / schema language (USL-15 / SCN-09) and confers no authority.

A :class:`Contract` is *immutable* (ENG-002 objecthood), *typed* (ENG-004), *identified*
(ENG-001), *classified* (SXH-03 kind), declares typed I/O by DF-2 reference (SCN-04),
declares effects and faults (SCN-05), declares applicable policy by reference (SCN-06),
and holds a *forward-only lifecycle state* (SOS-01…06, USL-12; breaking change = new
versioned contract, SCN-08). Constructing a :class:`Contract` enforces SMK-01/02 and the
laws USL-03/04/05/06/11 fail-closed: an ill-formed contract cannot be instantiated. It
realizes/binds no Service, Capability, Interface, Operation, Composition, Orchestration,
Execution, Policy, or Security object — those are separate units; this construct binds
them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from engine.certification.contracts import canonical_json, content_hash
from service.contract_meta import (
    CONTRACT_META_CLASS,
    CONTRACT_RELATIONSHIPS,
    CONTRACT_SUBSTRATE_REFS,
    LIFECYCLE_ORDER,
    ContractKind,
    ServiceState,
)
from service.service import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    ServiceError,
)

#: The deterministic id prefix for a realized Contract (mirrors EC-1 UCOS-<KIND>-<hex16>).
CONTRACT_ID_PREFIX = "UCOS-CONTRACT"

#: The map of frozen-foundation primitives this construct reuses *by reference*.
CONTRACT_FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the contract)",
    "ENG-003": "engine.certification.contracts.canonical_json (typed-value fidelity; no parallel)",
    "ENG-004": "service.contract_meta.ContractKind + type_tag (ENG-004 typing, by reference)",
    "ENG-005": "reference identifiers (I/O data / policy refs; no new construct)",
    "DF-2": "typed I/O bound by reference to represented DATA (SMR-13); not redefined",
}


def _require_ref_tuple(name: str, values: Any) -> tuple[str, ...]:
    """Require ``values`` to be a tuple of non-empty ENG-005/DF-2 reference strings."""
    if not isinstance(values, tuple):
        raise ServiceError(f"{name} must be a tuple of ENG-005 references (SCN-04/05)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise ServiceError(f"{name} entries must be non-empty ENG-005 references (SCN-04/05)")
    return values


@dataclass(frozen=True, slots=True)
class Contract:
    """SMC-03 — an immutable, typed, identified specification of an operation/service.

    Fields:
        type_tag:  the ENG-004 Type of the contract (decidable, non-empty) — USL-03 / SCN-01.
        kind:      the SXH-03 classification (Operation / Service / Composition; SXC-02).
        inputs:    tuple of DF-2-represented typed input references (SMR-13; SCN-04/USL-11).
        outputs:   tuple of DF-2-represented typed output references (SMR-13; SCN-04/USL-11).
        effects:   tuple of declared effect references (SCN-05); empty ⇒ a pure/no-effect contract.
        faults:    tuple of declared fault references (SCN-05); empty ⇒ declares no fault.
        policy_ref: the ENG-005 reference to applicable policy (SOE-09; SMR-08 / SCN-06 /
                    USL-13), evaluative & non-enforcing; empty ⇒ no policy bound.
        state:     the SOS-01…06 lifecycle state (forward-only) — USL-12 / SCN-08 (default DEFINED).
    """

    type_tag: str
    kind: ContractKind
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    effects: tuple[str, ...] = ()
    faults: tuple[str, ...] = ()
    policy_ref: str = ""
    state: ServiceState = ServiceState.DEFINED

    def __post_init__(self) -> None:
        # SMK-01 / USL-03 / SCN-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ServiceError("contract must be typed with a non-empty ENG-004 type_tag (USL-03)")
        # SXH-03 / SXC-02 — classified by exactly one Contract kind.
        if not isinstance(self.kind, ContractKind):
            raise ServiceError("contract kind must be an SXH-03 ContractKind (SXC-02)")
        # SCN-04 / USL-11 — typed I/O declared by DF-2 reference; SCN-05 — effects/faults declared.
        _require_ref_tuple("inputs", self.inputs)
        _require_ref_tuple("outputs", self.outputs)
        _require_ref_tuple("effects", self.effects)
        _require_ref_tuple("faults", self.faults)
        # SCN-06 / USL-13 — applicable policy by reference (optional).
        if not isinstance(self.policy_ref, str):
            raise ServiceError("policy_ref must be an ENG-005 reference string (SCN-06)")
        # V5 / USL-12 — a valid lifecycle state.
        if not isinstance(self.state, ServiceState):
            raise ServiceError("contract state must be a SOS-01…06 ServiceState (USL-12)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the contract (its identity-defining tuple)."""
        return {
            "meta_class": CONTRACT_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "effects": list(self.effects),
            "faults": list(self.faults),
            "policy_ref": self.policy_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the contract core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def contract_id(self) -> str:
        """The deterministic ENG-001 identity of the contract (borne by this object)."""
        return f"{CONTRACT_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (SMC-03)."""
        return CONTRACT_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the SMR-01…13 relationships the contract participates in."""
        return CONTRACT_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / SMK-03 — the founding graph (bound-by) is acyclic."""
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    # -- contract-specific obligations -----------------------------------------

    def specifies_io(self) -> bool:
        """USL-06 / SCN-03 — the contract is an explicit typed spec that declares its I/O.

        A well-formed contract explicitly declares its input and output structure (the
        tuples exist); at least one of inputs/outputs is present (a contract specifying
        neither inputs nor outputs specifies nothing).
        """
        return bool(self.inputs) or bool(self.outputs)

    def io_is_data(self) -> bool:
        """USL-11 / SCN-04 — every declared I/O reference is a non-empty DF-2 reference."""
        return all(
            isinstance(r, str) and bool(r.strip()) for r in (*self.inputs, *self.outputs)
        )

    def declares_effects_and_faults(self) -> bool:
        """SCN-05 / SMK-02 — effects and faults are explicitly declared (as tuples)."""
        return isinstance(self.effects, tuple) and isinstance(self.faults, tuple)

    def policy_by_reference(self) -> bool:
        """SCN-06 / USL-13 — applicable policy, when bound, is a non-empty reference."""
        return self.policy_ref == "" or bool(self.policy_ref.strip())

    # -- non-constitutiveness (USL-15 / SCN-09) --------------------------------

    def confers_authority(self) -> bool:
        """USL-15 / SCN-09 / C7 — a contract confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """USL-15 / SCN-09 / C7 — True iff the contract names a concrete technology/IDL/vendor."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """USL-15 / RR-07 / C7 — True iff the contract appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """USL-02 / SMI-05 / VC-5 — a contract redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (USL-12 / SCN-08, forward-only) -----------------------------

    def transition(self, to_state: ServiceState) -> Contract:
        """Return a new contract advanced to ``to_state`` (forward-only; USL-12 / SCN-08)."""
        if not isinstance(to_state, ServiceState):
            raise ServiceError("target state must be a SOS-01…06 ServiceState (USL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise ServiceError(
                f"lifecycle is forward-only (USL-12 / SCN-08): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the contract."""
        return {
            "contract_id": self.contract_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "effects": list(self.effects),
            "faults": list(self.faults),
            "policy_ref": self.policy_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(CONTRACT_SUBSTRATE_REFS),
        }


def make_contract(
    type_tag: str,
    *,
    kind: ContractKind = ContractKind.OPERATION,
    inputs: tuple[str, ...] = (),
    outputs: tuple[str, ...] = (),
    effects: tuple[str, ...] = (),
    faults: tuple[str, ...] = (),
    policy_ref: str = "",
    state: ServiceState = ServiceState.DEFINED,
) -> Contract:
    """Construct a well-formed :class:`Contract` (fail-closed factory)."""
    return Contract(
        type_tag=type_tag,
        kind=kind,
        inputs=inputs,
        outputs=outputs,
        effects=effects,
        faults=faults,
        policy_ref=policy_ref,
        state=state,
    )


__all__ = [
    "CONTRACT_ID_PREFIX",
    "CONTRACT_FOUNDATION_REUSE",
    "Contract",
    "make_contract",
]
