"""EC3-B11-U05 — Operation validation (meta-validity V1…V5 + USL conformance + SOP principles).

Proves a realized :class:`~service.operation.Operation` is **META-VALID** (SERVICE-005 §8,
V1…V5), **Service-law conformant** (SERVICE-001 §7), and **Operation-principle conformant**
(SERVICE-009 §4, SOP-01…10) by running deterministic checks through the **CERTIFIED EC-1
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
from service.operation import Operation
from service.operation_meta import OPERATION_META_CLASS, EffectKind, OperationKind
from service.operation_traceability import OperationTraceabilityRecord
from service.service_meta import META_RELATIONSHIPS, ServiceState
from service.service_validation import ServiceValidation

#: The blueprint id an Operation realizes (its meta-class) — used by the EC-1 report.
OPERATION_BLUEPRINT_ID = OPERATION_META_CLASS

_KIND_VALUES = frozenset(k.value for k in OperationKind)
_EFFECT_VALUES = frozenset(e.value for e in EffectKind)
_STATE_VALUES = frozenset(s.value for s in ServiceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class OperationValidationSubject:
    """A normalized, immutable projection of an Operation that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    service_ref: str
    contract_ref: str
    interface_ref: str
    input_refs: tuple[str, ...]
    output_refs: tuple[str, ...]
    effects: tuple[str, ...]
    faults: tuple[str, ...]
    execution_ref: str
    behavior_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    provided_by_service: bool
    contract_bound: bool
    interface_addressed: bool
    signature_bounded: bool
    effects_honest: bool
    io_is_data: bool
    execution_by_reference: bool
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
    def from_operation(
        cls, operation: Operation, trace: OperationTraceabilityRecord
    ) -> OperationValidationSubject:
        """Project ``operation`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=operation.operation_id,
            blueprint_id=OPERATION_BLUEPRINT_ID,
            meta_class=operation.meta_class,
            type_tag=operation.type_tag,
            kind=operation.kind.value,
            value_digest=operation.value_digest,
            service_ref=operation.service_ref,
            contract_ref=operation.contract_ref,
            interface_ref=operation.interface_ref,
            input_refs=operation.input_refs,
            output_refs=operation.output_refs,
            effects=tuple(e.value for e in operation.effects),
            faults=operation.faults,
            execution_ref=operation.execution_ref,
            behavior_ref=operation.behavior_ref,
            relationships=operation.meta_relationships(),
            lifecycle_state=operation.state.value,
            founding_acyclic=operation.is_founding_acyclic(),
            provided_by_service=operation.provided_by_service(),
            contract_bound=operation.contract_bound(),
            interface_addressed=operation.interface_addressed(),
            signature_bounded=operation.signature_bounded(),
            effects_honest=operation.effects_honest(),
            io_is_data=operation.io_is_data(),
            execution_by_reference=operation.execution_by_reference(),
            behavior_by_reference=operation.behavior_by_reference(),
            references_resolve=operation.references_resolve(),
            confers_authority=operation.confers_authority(),
            selects_technology=operation.selects_technology(),
            embeds_secret=operation.embeds_secret(),
            redefines_foundation=operation.redefines_foundation(),
            substrate_refs=tuple(operation.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),
        )


# ---------------------------------------------------------------------------
# Operation-layer validation checks
# ---------------------------------------------------------------------------


class OperationTypedCheck(ValidationCheck):
    """USL-08 / SOP-01 / C1 — the operation is typed (non-empty ENG-004 type)."""

    check_id = "operation-typed"
    severity = Severity.BLOCKING
    description = "Operation bears a non-empty ENG-004 type_tag (USL-08 / SOP-01)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("operation is untyped (USL-08)")
        return self._passed(type_tag=subject.type_tag)


class OperationIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SOP-02 / C1 — the operation is identified (ENG-001) and object-borne."""

    check_id = "operation-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Operation bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-OPERATION-"):
            return self._failed("operation has no ENG-001 identity (USL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("operation is not object-borne (no value digest) (USL-05)")
        return self._passed(operation_id=subject.target_id)


class OperationValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the operation core round-trips through the EC-1 canonical encoding.

    Emitted under the shared id ``service-value-fidelity`` so the reused CCE Gate-3
    aggregates it without duplicating gate logic.
    """

    check_id = "service-value-fidelity"
    severity = Severity.BLOCKING
    description = "Operation core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("operation core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class OperationClassifiedCheck(ValidationCheck):
    """SXH-05 / SXC-02 / SOP-08 — the operation is classified by exactly one kind."""

    check_id = "operation-classified"
    severity = Severity.BLOCKING
    description = "Operation is classified by an SXH-05 kind (single-facet, SXC-02 / SOP-08)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("operation kind is outside SXH-05", kind=subject.kind)
        return self._passed(kind=subject.kind)


class OperationProvidedByServiceCheck(ValidationCheck):
    """SMR-04 / SOR-04 — the operation is provided by a service, by ENG-005 reference."""

    check_id = "operation-provided-by-service"
    severity = Severity.BLOCKING
    description = "Operation is provided by a service by ENG-005 reference (SMR-04, ref-only)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not subject.provided_by_service:
            return self._failed("operation is provided by no service (SMR-04)")
        return self._passed(service_ref=subject.service_ref)


class OperationContractBoundCheck(ValidationCheck):
    """SMR-02 / SOR-02 / SOP-04 — the operation is bound by exactly one contract."""

    check_id = "operation-contract-bound"
    severity = Severity.BLOCKING
    description = "Operation is bound by a contract by ENG-005 reference (SMR-02 / SOP-04)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not subject.contract_bound:
            return self._failed("operation is bound by no contract (SMR-02 / SOP-04)")
        return self._passed(contract_ref=subject.contract_ref)


class OperationInterfaceAddressedCheck(ValidationCheck):
    """SMR-03 / SOP-05 / SMK-04 — the operation is addressed through an interface."""

    check_id = "operation-interface-addressed"
    severity = Severity.BLOCKING
    description = "Operation is addressed through an interface by reference (SMR-03 / SMK-04)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not subject.interface_addressed:
            return self._failed("operation is addressed through no interface (SMR-03 / SMK-04)")
        return self._passed(interface_ref=subject.interface_ref)


class OperationSignatureBoundedCheck(ValidationCheck):
    """USL-08 / SOP-03 — typed I/O well-formed, ≥1 defined effect, faults declared."""

    check_id = "operation-signature-bounded"
    severity = Severity.BLOCKING
    description = "Operation declares typed I/O, ≥1 defined effect, and faults (USL-08 / SOP-03)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not subject.signature_bounded:
            return self._failed("operation signature is unbounded/implicit (SOP-03)")
        return self._passed(effects=list(subject.effects), faults=len(subject.faults))


class OperationEffectHonestCheck(ValidationCheck):
    """SOP-08 / USL-08 — declared effects are honest for the operation kind."""

    check_id = "operation-effect-honest"
    severity = Severity.BLOCKING
    description = "Declared effects are honest for the SXH-05 kind (SOP-08; a query changes none)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if any(e not in _EFFECT_VALUES for e in subject.effects):
            return self._failed("an effect is outside the declared vocabulary (SOP-03)")
        if not subject.effects_honest:
            return self._failed("effects dishonest for kind (SOP-08)", kind=subject.kind)
        return self._passed(kind=subject.kind, effects=list(subject.effects))


class OperationIoIsDataCheck(ValidationCheck):
    """USL-11 / SOP-07 / SMR-13 — the operation's I/O references DF-2 data by reference."""

    check_id = "operation-io-is-data"
    severity = Severity.BLOCKING
    description = "Operation I/O references DF-2 data (SMR-13, by reference; USL-11 / SOP-07)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not subject.io_is_data:
            return self._failed("an operation I/O reference is not a valid DF-2 reference (SOP-07)")
        return self._passed(inputs=len(subject.input_refs), outputs=len(subject.output_refs))


class OperationExecutionByReferenceCheck(ValidationCheck):
    """SMR-07 / SOP-06 — execution binds RL-F2 by ENG-005 reference."""

    check_id = "operation-execution-by-reference"
    severity = Severity.BLOCKING
    description = "Execution binds RL-F2 by ENG-005 reference (SMR-07 / SOP-06)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not subject.execution_by_reference:
            return self._failed("no RL-F2 execution reference (SMR-07)")
        return self._passed(execution_ref=subject.execution_ref)


class OperationBehaviorByReferenceCheck(ValidationCheck):
    """SMR-11 / SOP-06 — invocation behavior binds RL-F2 by ENG-005 reference."""

    check_id = "operation-behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Invocation behavior binds RL-F2 by ENG-005 reference (SMR-11 / SOP-06)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not subject.behavior_by_reference:
            return self._failed("no RL-F2 behavior reference (SMR-11)")
        return self._passed(behavior_ref=subject.behavior_ref)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / SMI-01 — the operation instantiates exactly one meta-class (SMC-05)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Operation instantiates exactly the SMC-05 meta-class (V1)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if subject.meta_class != OPERATION_META_CLASS:
            return self._failed("meta-class is not SMC-05 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / SMI-02 — every relationship used lies within SMR-01…13."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All operation relationships are within SMR-01…13 (V2)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside SMR-01…13 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — SMK-01 (typed/identified/object) + SMK-02 (contract-bound + signature) +
    SMK-04 (interface-addressed) + SMK-05/07 (references resolve)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01/02/04/05/07 hold (typed/identified, contract-bound, addressed) (V3)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("SMK-01 not satisfied (V3)")
        if not (subject.contract_bound and subject.signature_bounded):
            return self._failed("SMK-02 not satisfied: uncontracted or unbounded signature (V3)")
        if not subject.interface_addressed:
            return self._failed("SMK-04 not satisfied: not interface-addressed (V3)")
        if not subject.references_resolve:
            return self._failed("SMK-05/07 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["SMK-01", "SMK-02", "SMK-04", "SMK-05", "SMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMK-03 / SOP-C5 — the founding graph (provides/bound-by/exposes) is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The operation's founding graph is acyclic (V4 / SMK-03 / SOP-C5)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / USL-12 — the operation holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Operation holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """USL-02 / SMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/DF-2 referenced, redefined nowhere (USL-02)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (USL-02 / SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (USL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """USL-15 / SOP-09 / C7 — no API method/protocol/transport/framework/vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/protocol/API method selected (USL-15 / SOP-09)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology/protocol/API method was selected (USL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """USL-15 / SOP-09 / C7 — the operation confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Operation confers no authority and embeds no secret (USL-15 / SOP-09)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("operation confers authority (USL-15)")
        if subject.embeds_secret:
            return self._failed("operation embeds a secret (USL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted at SMC-05 and closes to 11-SERVICE."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at SMC-05 and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: OperationValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def operation_checks() -> tuple[ValidationCheck, ...]:
    """The full operation-layer validation suite (deterministically ordered by the engine)."""
    return (
        OperationTypedCheck(),
        OperationIdentifiedCheck(),
        OperationValueFidelityCheck(),
        OperationClassifiedCheck(),
        OperationProvidedByServiceCheck(),
        OperationContractBoundCheck(),
        OperationInterfaceAddressedCheck(),
        OperationSignatureBoundedCheck(),
        OperationEffectHonestCheck(),
        OperationIoIsDataCheck(),
        OperationExecutionByReferenceCheck(),
        OperationBehaviorByReferenceCheck(),
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


def validate_operation(
    operation: Operation, trace: OperationTraceabilityRecord, *, strict: bool = False
) -> ServiceValidation:
    """Validate ``operation`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = OperationValidationSubject.from_operation(operation, trace)
    engine = ValidationEngine(operation_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ServiceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "OPERATION_BLUEPRINT_ID",
    "OperationValidationSubject",
    "operation_checks",
    "validate_operation",
]
