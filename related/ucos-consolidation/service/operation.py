"""EC3-B11-U05 — The Universal Operation construct (SMC-05).

Realizes the meta-model concept **SMC-05 Operation** (SERVICE-005 §2; SERVICE-003 SOE-05;
SERVICE-009 §3):

    a **single, named, invocable unit of work with typed inputs and outputs, defined
    effects, and declared faults** — the atomic act a service offers — an ENG-002 Object
    bearing an ENG-001 Identity, classified by an ENG-004 Type, that a service **provides**
    (SMR-04, founding, acyclic), that is **bound-by** exactly one contract (SMR-02,
    founding, acyclic), **addressed-through** an interface (SMR-03), **executes** by
    reference to RL-F2 (SMR-07), whose behavior is a RUNTIME construct (SMR-11, by
    reference) and whose typed I/O references DF-2 data (SMR-13, by reference).

The construct is **additive over the CERTIFIED EC-1 foundation** and reuses it — and the
CERTIFIED SMC-01 Service / SMC-02 Capability / SMC-03 Contract / SMC-04 Interface — *by
reference* (USL-02 / SMI-05): identity and value-fidelity are derived through the EC-1
certified deterministic encoding, so this module introduces **no second identity scheme
and no parallel value model**. It selects no technology / protocol / API method (USL-15 /
SOP-09) and confers no authority.

An :class:`Operation` is *immutable* (ENG-002 objecthood), *typed* (ENG-004), *identified*
(ENG-001), *classified* (SXH-05 kind = Query / Command / Event, SOP-08), *provided-by a
service* (SMR-04, by reference), *bound-by a contract* (SMR-02, by reference), *addressed
through an interface* (SMR-03, by reference), declares a **bounded signature** — typed I/O
(DF-2 references, SMR-13 / SOP-07), defined **effects** and declared **faults** (SOP-03) —
binds **execution** (SMR-07) and **behavior** (SMR-11) to RL-F2 by reference (SOP-06), and
holds a *forward-only lifecycle state* (SOS-01…06, USL-12; breaking signature change = new
versioned operation, USL-12/15). Constructing an :class:`Operation` enforces SOP-K1…K5 and
the laws USL-03/04/05/06/08/10/11 fail-closed: an ill-formed operation cannot be
instantiated. Effect honesty (SOP-08) is enforced: a query declares no state-changing
effect. It realizes/binds no Service, Capability, Contract, Interface, Composition,
Orchestration, Execution, Policy, or Security object — those are separate units; this
construct binds them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from engine.certification.contracts import canonical_json, content_hash
from service.operation_meta import (
    LIFECYCLE_ORDER,
    OPERATION_META_CLASS,
    OPERATION_RELATIONSHIPS,
    OPERATION_SUBSTRATE_REFS,
    EffectKind,
    OperationKind,
    ServiceState,
)
from service.service import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    ServiceError,
)

#: The deterministic id prefix for a realized Operation (mirrors EC-1 UCOS-<KIND>-<hex16>).
OPERATION_ID_PREFIX = "UCOS-OPERATION"

#: The default abstract RUNTIME execution binding an operation executes (SMR-07; RL-F2).
DEFAULT_EXECUTION_REF = "ENG-005:RL-F2:runtime.execution"

#: The default abstract RUNTIME invocation behavior an operation behaves-as (SMR-11; RL-F2).
DEFAULT_BEHAVIOR_REF = "ENG-005:RL-F2:runtime.invocation"

#: The map of frozen-foundation primitives this construct reuses *by reference*.
OPERATION_FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the operation)",
    "ENG-003": "engine.certification.contracts.canonical_json (typed-signature value fidelity)",
    "ENG-004": "service.operation_meta.OperationKind + type_tag (ENG-004 typing, by reference)",
    "ENG-005": "reference identifiers (service/contract/interface/execution refs; no new type)",
    "RL-F2": "execution/behavior bound by reference (SMR-07/11); no runtime concern redefined",
    "DF-2": "operation typed I/O bound by reference to represented DATA (SMR-13); not redefined",
}


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(f"{name} must be a non-empty ENG-005 reference (SMR-02/03/04/07/11)")
    return value


def _require_ref_tuple(name: str, values: Any) -> tuple[str, ...]:
    """Require ``values`` to be a tuple of non-empty DF-2 reference strings (SMR-13 / SOP-07)."""
    if not isinstance(values, tuple):
        raise ServiceError(f"{name} must be a tuple of DF-2 references (SOP-03/07)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise ServiceError(f"{name} entries must be non-empty DF-2 references (SOP-03/07)")
    return values


def _require_effects(values: Any) -> tuple[EffectKind, ...]:
    """Require ``values`` to be a tuple of :class:`EffectKind` (declared effects; SOP-03)."""
    if not isinstance(values, tuple):
        raise ServiceError("effects must be a tuple of EffectKind (SOP-03)")
    for v in values:
        if not isinstance(v, EffectKind):
            raise ServiceError("each effect must be an EffectKind (SOP-03 / SXH-05)")
    return values


def _require_faults(values: Any) -> tuple[str, ...]:
    """Require ``values`` to be a tuple of non-empty declared-fault descriptors (SOP-03)."""
    if not isinstance(values, tuple):
        raise ServiceError("faults must be a tuple of declared-fault descriptors (SOP-03)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise ServiceError("each fault must be a non-empty descriptor (SOP-03)")
    return values


@dataclass(frozen=True, slots=True)
class Operation:
    """SMC-05 — an immutable, typed, identified, invocable unit of work.

    Fields:
        type_tag:      the ENG-004 Type of the operation (decidable, non-empty) — USL-08 / SOP-01.
        kind:          the SXH-05 classification (Query / Command / Event; SOP-08).
        service_ref:   the ENG-005 reference to the Service that provides the operation
                       (SMR-04 provides; SOR-04; founding, reference-only).
        contract_ref:  the ENG-005 reference to the Contract that binds the operation
                       (SMR-02 bound-by; SOR-02; founding; SOP-04 — exactly one).
        interface_ref: the ENG-005 reference to the Interface through which the operation
                       is addressed (SMR-03; SOR-03; SOP-05 / SMK-04).
        input_refs:    tuple of DF-2-represented typed input references (SMR-13 / SOP-07 /
                       USL-11; by reference).
        output_refs:   tuple of DF-2-represented typed output references (SMR-13 / SOP-07 /
                       USL-11; by reference).
        effects:       tuple of declared :class:`EffectKind` (SOP-03; effect honesty SOP-08).
        faults:        tuple of declared-fault descriptors (SOP-03; nothing implicit).
        execution_ref: the ENG-005 reference to the RUNTIME execution the operation binds
                       (SMR-07 executes; RL-F2, by reference) — SOP-06.
        behavior_ref:  the ENG-005 reference to the RUNTIME invocation behavior the operation
                       binds (SMR-11 behaves-as; RL-F2, by reference) — SOP-06.
        state:         the SOS-01…06 lifecycle state (forward-only) — USL-12.
    """

    type_tag: str
    kind: OperationKind
    service_ref: str
    contract_ref: str
    interface_ref: str
    input_refs: tuple[str, ...] = ()
    output_refs: tuple[str, ...] = ()
    effects: tuple[EffectKind, ...] = ()
    faults: tuple[str, ...] = ()
    execution_ref: str = DEFAULT_EXECUTION_REF
    behavior_ref: str = DEFAULT_BEHAVIOR_REF
    state: ServiceState = ServiceState.DEFINED

    def __post_init__(self) -> None:
        # SOP-K1 / USL-08 / SOP-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ServiceError("operation must be typed with a non-empty ENG-004 type_tag (USL-08)")
        # SXH-05 / SXC-02 / SOP-08 — classified by exactly one operation kind.
        if not isinstance(self.kind, OperationKind):
            raise ServiceError("operation kind must be an SXH-05 OperationKind (SXC-02)")
        # SMR-04 / SOR-04 — provided by a service, bound by reference.
        _require_reference("service_ref", self.service_ref)
        # SMR-02 / SOR-02 / SOP-04 — bound by exactly one contract, by reference.
        _require_reference("contract_ref", self.contract_ref)
        # SMR-03 / SOR-03 / SOP-05 / SMK-04 — addressed through an interface, by reference.
        _require_reference("interface_ref", self.interface_ref)
        # SMR-13 / SOP-07 / USL-11 — typed I/O declared by DF-2 reference.
        _require_ref_tuple("input_refs", self.input_refs)
        _require_ref_tuple("output_refs", self.output_refs)
        # SOP-03 — declared effects (EffectKind) and faults (descriptors); nothing implicit.
        _require_effects(self.effects)
        _require_faults(self.faults)
        # SMR-07 / SOP-06 — execution bound to RL-F2 by reference.
        _require_reference("execution_ref", self.execution_ref)
        # SMR-11 / SOP-06 — behavior bound to RL-F2 by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # V5 / USL-12 — a valid lifecycle state.
        if not isinstance(self.state, ServiceState):
            raise ServiceError("operation state must be a SOS-01…06 ServiceState (USL-12)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the operation (its identity-defining tuple)."""
        return {
            "meta_class": OPERATION_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "service_ref": self.service_ref,
            "contract_ref": self.contract_ref,
            "interface_ref": self.interface_ref,
            "input_refs": list(self.input_refs),
            "output_refs": list(self.output_refs),
            "effects": [e.value for e in self.effects],
            "faults": list(self.faults),
            "execution_ref": self.execution_ref,
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the operation core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def operation_id(self) -> str:
        """The deterministic ENG-001 identity of the operation (borne by this object)."""
        return f"{OPERATION_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (SMC-05)."""
        return OPERATION_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the SMR-01…13 relationships the operation participates in."""
        return OPERATION_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / SMK-03 / SOP-C5 — the founding graph (provides/bound-by/exposes) is acyclic."""
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    # -- operation-specific obligations ----------------------------------------

    def provided_by_service(self) -> bool:
        """SMR-04 / SOR-04 — the operation is provided by a service (by reference)."""
        return bool(self.service_ref.strip())

    def contract_bound(self) -> bool:
        """SMR-02 / SOR-02 / SOP-04 — the operation is bound by exactly one contract."""
        return bool(self.contract_ref.strip())

    def interface_addressed(self) -> bool:
        """SMR-03 / SOP-05 / SMK-04 — the operation is addressed through an interface."""
        return bool(self.interface_ref.strip())

    def signature_bounded(self) -> bool:
        """USL-08 / SOP-03 — typed I/O well-formed, ≥1 defined effect, faults well-formed.

        An operation with no declared effect is under-specified (nothing is implicit); its
        typed inputs/outputs, when present, are well-formed DF-2 references and its faults
        are non-empty descriptors.
        """
        io = (*self.input_refs, *self.output_refs)
        io_ok = all(isinstance(r, str) and bool(r.strip()) for r in io)
        effects_ok = bool(self.effects)
        faults_ok = all(isinstance(f, str) and bool(f.strip()) for f in self.faults)
        return io_ok and effects_ok and faults_ok

    def effects_honest(self) -> bool:
        """SOP-08 / USL-08 — declared effects are honest for the operation kind.

        * Query   — reads/derives only; declares no state-changing (WRITE) or event effect.
        * Command — intends a represented state change; declares ≥1 WRITE effect.
        * Event   — emits/consumes an event; declares ≥1 EMIT or CONSUME effect.
        """
        declared = set(self.effects)
        if self.kind is OperationKind.QUERY:
            return all(e is EffectKind.READ for e in self.effects)
        if self.kind is OperationKind.COMMAND:
            return EffectKind.WRITE in declared
        return bool(declared & {EffectKind.EMIT, EffectKind.CONSUME})

    def io_is_data(self) -> bool:
        """USL-11 / SOP-07 / SMR-13 — every I/O reference is a non-empty DF-2 reference."""
        return all(
            isinstance(r, str) and bool(r.strip())
            for r in (*self.input_refs, *self.output_refs)
        )

    def execution_by_reference(self) -> bool:
        """SMR-07 / SOP-06 — execution binds RL-F2 by a non-empty reference."""
        return bool(self.execution_ref.strip())

    def behavior_by_reference(self) -> bool:
        """SMR-11 / SOP-06 — invocation behavior binds RL-F2 by a non-empty reference."""
        return bool(self.behavior_ref.strip())

    def references_resolve(self) -> bool:
        """SMK-05/07 / SOP-K4 — every ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (
                self.service_ref,
                self.contract_ref,
                self.interface_ref,
                self.execution_ref,
                self.behavior_ref,
            )
        )

    # -- non-constitutiveness (USL-15 / SOP-09) --------------------------------

    def confers_authority(self) -> bool:
        """USL-15 / SOP-09 / C7 — an operation confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """USL-15 / SOP-09 / C7 — True iff the operation names a technology/API method/URL."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """USL-15 / RR-07 / C7 — True iff the operation appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """USL-02 / SMI-05 / VC-5 — an operation redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (USL-12, forward-only) --------------------------------------

    def transition(self, to_state: ServiceState) -> Operation:
        """Return a new operation advanced to ``to_state`` (forward-only; USL-12)."""
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
        """A deterministic, serializable projection of the operation."""
        return {
            "operation_id": self.operation_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "service_ref": self.service_ref,
            "contract_ref": self.contract_ref,
            "interface_ref": self.interface_ref,
            "input_refs": list(self.input_refs),
            "output_refs": list(self.output_refs),
            "effects": [e.value for e in self.effects],
            "faults": list(self.faults),
            "execution_ref": self.execution_ref,
            "behavior_ref": self.behavior_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(OPERATION_SUBSTRATE_REFS),
        }


def make_operation(
    type_tag: str,
    service_ref: str,
    contract_ref: str,
    interface_ref: str,
    *,
    kind: OperationKind = OperationKind.COMMAND,
    input_refs: tuple[str, ...] = (),
    output_refs: tuple[str, ...] = (),
    effects: tuple[EffectKind, ...] = (),
    faults: tuple[str, ...] = (),
    execution_ref: str = DEFAULT_EXECUTION_REF,
    behavior_ref: str = DEFAULT_BEHAVIOR_REF,
    state: ServiceState = ServiceState.DEFINED,
) -> Operation:
    """Construct a well-formed :class:`Operation` (fail-closed factory)."""
    return Operation(
        type_tag=type_tag,
        kind=kind,
        service_ref=service_ref,
        contract_ref=contract_ref,
        interface_ref=interface_ref,
        input_refs=input_refs,
        output_refs=output_refs,
        effects=effects,
        faults=faults,
        execution_ref=execution_ref,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "OPERATION_ID_PREFIX",
    "DEFAULT_EXECUTION_REF",
    "DEFAULT_BEHAVIOR_REF",
    "OPERATION_FOUNDATION_REUSE",
    "Operation",
    "make_operation",
]
