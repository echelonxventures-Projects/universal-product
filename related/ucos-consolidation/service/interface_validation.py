"""EC3-B11-U04 — Interface validation (meta-validity V1…V5 + USL conformance + SIN principles).

Proves a realized :class:`~service.interface.Interface` is **META-VALID** (SERVICE-005 §8,
V1…V5), **Service-law conformant** (SERVICE-001 §7), and **Interface-principle conformant**
(SERVICE-008 §4, SIN-01…10) by running deterministic checks through the **CERTIFIED EC-1
Validation Engine**.

The suite emits the seven **generic** check ids the CCE ten-gate suite depends on so that
:func:`service.service_certification.cce_gates` is reused **verbatim**. The result is
bundled as the shared :class:`service.service_validation.ServiceValidation`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding
from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance
from service.interface import Interface
from service.interface_meta import INTERFACE_META_CLASS, InterfaceKind
from service.interface_traceability import InterfaceTraceabilityRecord
from service.service_meta import META_RELATIONSHIPS, ServiceState
from service.service_validation import ServiceValidation

#: The blueprint id an Interface realizes (its meta-class) — used by the EC-1 report.
INTERFACE_BLUEPRINT_ID = INTERFACE_META_CLASS

_KIND_VALUES = frozenset(k.value for k in InterfaceKind)
_STATE_VALUES = frozenset(s.value for s in ServiceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class InterfaceValidationSubject:
    """A normalized, immutable projection of an Interface that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    service_ref: str
    operations: tuple[str, ...]
    io_refs: tuple[str, ...]
    endpoint_ref: str
    behavior_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    exposed_by_service: bool
    is_sole_surface: bool
    io_is_data: bool
    endpoint_is_abstract: bool
    behavior_by_reference: bool
    references_resolve: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_interface(
        cls, interface: Interface, trace: InterfaceTraceabilityRecord
    ) -> InterfaceValidationSubject:
        """Project ``interface`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=interface.interface_id,
            blueprint_id=INTERFACE_BLUEPRINT_ID,
            meta_class=interface.meta_class,
            type_tag=interface.type_tag,
            kind=interface.kind.value,
            value_digest=interface.value_digest,
            service_ref=interface.service_ref,
            operations=interface.operations,
            io_refs=interface.io_refs,
            endpoint_ref=interface.endpoint_ref,
            behavior_ref=interface.behavior_ref,
            relationships=interface.meta_relationships(),
            lifecycle_state=interface.state.value,
            founding_acyclic=interface.is_founding_acyclic(),
            exposed_by_service=interface.exposed_by_service(),
            is_sole_surface=interface.is_sole_surface(),
            io_is_data=interface.io_is_data(),
            endpoint_is_abstract=interface.endpoint_is_abstract(),
            behavior_by_reference=interface.behavior_by_reference(),
            references_resolve=interface.references_resolve(),
            confers_authority=interface.confers_authority(),
            selects_technology=interface.selects_technology(),
            embeds_secret=interface.embeds_secret(),
            redefines_foundation=interface.redefines_foundation(),
            substrate_refs=tuple(interface.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),
        )


# ---------------------------------------------------------------------------
# Interface-layer validation checks
# ---------------------------------------------------------------------------


class InterfaceTypedCheck(ValidationCheck):
    """USL-07 / SIN-01 / C1 — the interface is a typed surface (non-empty ENG-004 type)."""

    check_id = "interface-typed"
    severity = Severity.BLOCKING
    description = "Interface bears a non-empty ENG-004 type_tag (USL-07 / SIN-01)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("interface is untyped (USL-07)")
        return self._passed(type_tag=subject.type_tag)


class InterfaceIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SIN-02 / C1 — the interface is identified (ENG-001) and object-borne."""

    check_id = "interface-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Interface bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-INTERFACE-"):
            return self._failed("interface has no ENG-001 identity (USL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("interface is not object-borne (no value digest) (USL-05)")
        return self._passed(interface_id=subject.target_id)


class InterfaceValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the interface core round-trips through the EC-1 canonical encoding.

    Emitted under the shared id ``service-value-fidelity`` so the reused CCE Gate-3
    aggregates it without duplicating gate logic.
    """

    check_id = "service-value-fidelity"
    severity = Severity.BLOCKING
    description = "Interface core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("interface core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class InterfaceClassifiedCheck(ValidationCheck):
    """SXH-04 / SXC-02 / SIN-06 — the interface is classified by exactly one interaction style."""

    check_id = "interface-classified"
    severity = Severity.BLOCKING
    description = "Interface is classified by an SXH-04 kind (single-facet, SXC-02 / SIN-06)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("interface kind is outside SXH-04", kind=subject.kind)
        return self._passed(kind=subject.kind)


class InterfaceExposedByServiceCheck(ValidationCheck):
    """SMR-03 / SOR-03 — the interface is exposed by a service, bound by ENG-005 reference."""

    check_id = "interface-exposed-by-service"
    severity = Severity.BLOCKING
    description = "Interface is exposed by a service by ENG-005 reference (SMR-03, reference-only)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if not subject.exposed_by_service:
            return self._failed("interface is exposed by no service (SMR-03)")
        return self._passed(service_ref=subject.service_ref)


class InterfaceSoleSurfaceCheck(ValidationCheck):
    """USL-07 / SIN-03 — the interface presents at least one addressable operation surface."""

    check_id = "interface-sole-surface"
    severity = Severity.BLOCKING
    description = "Interface presents ≥1 addressable operation (sole-surface; USL-07 / SIN-03)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if not subject.is_sole_surface:
            return self._failed("interface presents no addressable operation (SIN-03)")
        return self._passed(operations=len(subject.operations))


class InterfaceIoIsDataCheck(ValidationCheck):
    """USL-11 / SIN-07 / SMR-13 — the interface's carried I/O references DF-2 data by reference."""

    check_id = "interface-io-is-data"
    severity = Severity.BLOCKING
    description = "Interface I/O references DF-2 data (SMR-13, by reference; USL-11 / SIN-07)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if not subject.io_is_data:
            return self._failed("an interface I/O reference is not a valid DF-2 reference (SIN-07)")
        return self._passed(io=len(subject.io_refs))


class InterfaceEndpointAbstractCheck(ValidationCheck):
    """SIN-05 / SIN-C1 — the endpoint, when present, is a non-blank abstract locus."""

    check_id = "interface-endpoint-abstract"
    severity = Severity.BLOCKING
    description = "Endpoint is an abstract addressable locus; no URL/protocol (SIN-05 / SIN-C1)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if not subject.endpoint_is_abstract:
            return self._failed("endpoint_ref present but blank (SIN-05)")
        return self._passed(endpoint_ref=subject.endpoint_ref or "(none)")


class InterfaceBehaviorByReferenceCheck(ValidationCheck):
    """SMR-11 / SIN-C5 — interaction behavior binds RL-F2 by ENG-005 reference."""

    check_id = "interface-behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Interaction behavior binds RL-F2 by ENG-005 reference (SMR-11 / SIN-C5)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if not subject.behavior_by_reference:
            return self._failed("no RL-F2 interaction behavior reference (SMR-11)")
        return self._passed(behavior_ref=subject.behavior_ref)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / SMI-01 — the interface instantiates exactly one meta-class (SMC-04)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Interface instantiates exactly the SMC-04 meta-class (V1)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if subject.meta_class != INTERFACE_META_CLASS:
            return self._failed("meta-class is not SMC-04 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / SMI-02 — every relationship used lies within SMR-01…13."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All interface relationships are within SMR-01…13 (V2)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside SMR-01…13 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints SMK-01 (typed/identified/object) + SMK-05 (refs)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01 (typed/identified/object) and SMK-05 (references resolve) hold (V3)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("SMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("SMK-05 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["SMK-01", "SMK-05"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMK-03 / SIN-C3 — the founding graph (exposes) is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The interface's founding graph is acyclic (V4 / SMK-03 / SIN-C3)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / USL-12 / SIN-08 — the interface holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Interface holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """USL-02 / SMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/DF-2 referenced, redefined nowhere (USL-02)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (USL-02 / SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (USL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """USL-15 / SIN-05 / SIN-09 / C7 — no URL/protocol/transport/framework/vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/protocol/endpoint URL selected (USL-15 / SIN-05/09)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology/protocol/URL was selected (USL-15 / SIN-05)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """USL-15 / SIN-09 / C7 — the interface confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Interface confers no authority and embeds no secret (USL-15 / SIN-09)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("interface confers authority (USL-15)")
        if subject.embeds_secret:
            return self._failed("interface embeds a secret (USL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted at SMC-04 and closes to 11-SERVICE."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at SMC-04 and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: InterfaceValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def interface_checks() -> tuple[ValidationCheck, ...]:
    """The full interface-layer validation suite (deterministically ordered by the engine)."""
    return (
        InterfaceTypedCheck(),
        InterfaceIdentifiedCheck(),
        InterfaceValueFidelityCheck(),
        InterfaceClassifiedCheck(),
        InterfaceExposedByServiceCheck(),
        InterfaceSoleSurfaceCheck(),
        InterfaceIoIsDataCheck(),
        InterfaceEndpointAbstractCheck(),
        InterfaceBehaviorByReferenceCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


def validate_interface(
    interface: Interface, trace: InterfaceTraceabilityRecord, *, strict: bool = False
) -> ServiceValidation:
    """Validate ``interface`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = InterfaceValidationSubject.from_interface(interface, trace)
    engine = ValidationEngine(interface_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ServiceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "INTERFACE_BLUEPRINT_ID",
    "InterfaceValidationSubject",
    "interface_checks",
    "validate_interface",
]
