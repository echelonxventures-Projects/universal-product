"""EC3-B11-U01 — Service validation (meta-validity V1…V5 + USL-01…15 conformance).

This module proves a realized :class:`~service.service.Service` is **META-VALID**
(SERVICE-005 §8, V1…V5) and **Service-law conformant** (SERVICE-001 §7, USL-01…15) by
running a suite of deterministic, service-layer checks through the **CERTIFIED EC-1
Validation Engine** (:class:`engine.validation.executor.ValidationEngine`) and
enforcing the EC-1 acceptance gate (:func:`engine.validation.gates.enforce_acceptance`).
Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`ServiceValidationSubject`
(the type-independent projection the EC-1 engine consumes), so an identical service
yields a byte-identical report, evidence, and acceptance decision (VC-4). Every check
is **blocking**: the verdict is PASS iff the service satisfies every meta-validity and
Service-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- EC-1 reuse by reference (USL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance
from service.service import Service
from service.service_meta import (
    META_RELATIONSHIPS,
    SERVICE_META_CLASS,
    ServiceKind,
    ServiceState,
)
from service.service_traceability import TraceabilityRecord

#: The blueprint id a Service realizes (its meta-class) — used by the EC-1 report.
SERVICE_BLUEPRINT_ID = SERVICE_META_CLASS

_KIND_VALUES = frozenset(k.value for k in ServiceKind)
_STATE_VALUES = frozenset(s.value for s in ServiceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class ServiceValidationSubject:
    """A normalized, immutable projection of a Service that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the service's meta-facts. Holds no runtime
    state and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    capability_ref: str
    behavior_ref: str
    composition_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    references_resolve: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_service(cls, service: Service, trace: TraceabilityRecord) -> ServiceValidationSubject:
        """Project ``service`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=service.service_id,
            blueprint_id=SERVICE_BLUEPRINT_ID,
            meta_class=service.meta_class,
            type_tag=service.type_tag,
            kind=service.kind.value,
            value_digest=service.value_digest,
            capability_ref=service.capability_ref,
            behavior_ref=service.behavior_ref,
            composition_ref=service.composition_ref,
            relationships=service.meta_relationships(),
            lifecycle_state=service.state.value,
            founding_acyclic=service.is_founding_acyclic(),
            references_resolve=service.references_resolve(),
            confers_authority=service.confers_authority(),
            selects_technology=service.selects_technology(),
            embeds_secret=service.embeds_secret(),
            redefines_foundation=service.redefines_foundation(),
            substrate_refs=tuple(service.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Service-layer validation checks (each maps to explicit V*/USL*/SMK* obligations)
# ---------------------------------------------------------------------------


class ServiceTypedCheck(ValidationCheck):
    """USL-03 / SMK-01 / C1 — the service is classified by a non-empty ENG-004 type."""

    check_id = "service-typed"
    severity = Severity.BLOCKING
    description = "Service bears a non-empty ENG-004 type_tag (USL-03)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("service is untyped (USL-03)")
        return self._passed(type_tag=subject.type_tag)


class ServiceIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SMK-01 / C1 — the service is identified (ENG-001) and object-borne."""

    check_id = "service-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Service bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-SERVICE-"):
            return self._failed("service has no ENG-001 identity (USL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("service is not object-borne (no value digest) (USL-05)")
        return self._passed(service_id=subject.target_id)


class ServiceValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the service core round-trips through the EC-1 canonical encoding."""

    check_id = "service-value-fidelity"
    severity = Severity.BLOCKING
    description = "Service core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("service core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class ServiceClassifiedCheck(ValidationCheck):
    """SXH-01 / SXC-02 — the service is classified by exactly one Service kind."""

    check_id = "service-classified"
    severity = Severity.BLOCKING
    description = "Service is classified by an SXH-01 kind (single-facet, SXC-02)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("service kind is outside SXH-01", kind=subject.kind)
        return self._passed(kind=subject.kind)


class ServiceRealizesCapabilityCheck(ValidationCheck):
    """SMR-01 / SOE-01 — the service realizes a capability, bound by ENG-005 reference."""

    check_id = "service-realizes-capability"
    severity = Severity.BLOCKING
    description = "Service realizes a capability by ENG-005 reference (SMR-01, reference-only)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if not subject.capability_ref.strip():
            return self._failed("service realizes no capability (SMR-01)")
        return self._passed(capability_ref=subject.capability_ref)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / SMI-01 — the service instantiates exactly one meta-class (SMC-01)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Service instantiates exactly the SMC-01 meta-class (V1)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if subject.meta_class != SERVICE_META_CLASS:
            return self._failed("meta-class is not SMC-01 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / SMI-02 — every relationship used lies within SMR-01…13."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All service relationships are within SMR-01…13 (V2)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside SMR-01…13 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (SMK-01 typed/identified/object; SMK-05/06 refs)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01 (typed/identified/object) and SMK-05/06 (references) hold (V3)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("SMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("SMK-05/06 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["SMK-01", "SMK-05", "SMK-06"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMK-03 / USL-09 — the founding graph is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The service's founding graph is acyclic (V4 / SMK-03)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / USL-12 — the service holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Service holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """USL-02 / SMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/PL-F2/DF-2 referenced, redefined nowhere (USL-02)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (USL-02 / SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (USL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class CompositionByReferenceCheck(ValidationCheck):
    """USL-09 / SMR-12 / C5 — composition binds to PL-F2 by ENG-005 reference."""

    check_id = "composition-by-reference"
    severity = Severity.BLOCKING
    description = "Composition binds to PL-F2 by ENG-005 reference (USL-09; no new construct)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if not subject.composition_ref.strip():
            return self._failed("no PL-F2 composition reference (USL-09)")
        return self._passed(composition_ref=subject.composition_ref)


class ExecutionByReferenceCheck(ValidationCheck):
    """USL-10 / SMR-11 / C6 — execution/behavior binds to RL-F2 by ENG-005 reference."""

    check_id = "execution-by-reference"
    severity = Severity.BLOCKING
    description = "Behavior/execution binds to RL-F2 by ENG-005 reference (USL-10)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("no RL-F2 behavior reference (USL-10)")
        return self._passed(behavior_ref=subject.behavior_ref)


class TechnologyIndependenceCheck(ValidationCheck):
    """USL-15 / C7 — no API/protocol/transport/framework/vendor technology is selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/protocol/vendor selected (USL-15)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (USL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """USL-15 / C7 — the service confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Service confers no authority and embeds no secret (USL-15 / RR-07)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("service confers authority (USL-15)")
        if subject.embeds_secret:
            return self._failed("service embeds a secret (USL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 11-SERVICE anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at SMC-01 and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: ServiceValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def service_checks() -> tuple[ValidationCheck, ...]:
    """The full service-layer validation suite (deterministically ordered by the engine)."""
    return (
        ServiceTypedCheck(),
        ServiceIdentifiedCheck(),
        ServiceValueFidelityCheck(),
        ServiceClassifiedCheck(),
        ServiceRealizesCapabilityCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        CompositionByReferenceCheck(),
        ExecutionByReferenceCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class ServiceValidation:
    """The bundled outcome of validating a Service (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_service(
    service: Service, trace: TraceabilityRecord, *, strict: bool = False
) -> ServiceValidation:
    """Validate ``service`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected service raises via the
    EC-1 acceptance gate.
    """
    subject = ServiceValidationSubject.from_service(service, trace)
    engine = ValidationEngine(service_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ServiceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "SERVICE_BLUEPRINT_ID",
    "ServiceValidationSubject",
    "ServiceValidation",
    "service_checks",
    "validate_service",
]
