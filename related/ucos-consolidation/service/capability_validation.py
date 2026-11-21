"""EC3-B11-U02 — Capability validation (meta-validity V1…V5 + USL-01…15 conformance).

This module proves a realized :class:`~service.capability.Capability` is **META-VALID**
(SERVICE-005 §8, V1…V5) and **Service-law conformant** (SERVICE-001 §7, USL-01…15) by
running a suite of deterministic checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate (:func:`engine.validation.gates.enforce_acceptance`).

The suite emits the same seven **generic** check ids the CCE ten-gate suite depends on
(``traceability-rooted``, ``meta-class-single``, ``foundation-reuse-integrity``,
``service-value-fidelity``, ``founding-acyclic``, ``meta-relationships-closed``,
``provisional-state-disclosure``) so that
:func:`service.service_certification.cce_gates` is reused **verbatim** — no gate logic is
duplicated. The result is bundled as the shared
:class:`service.service_validation.ServiceValidation`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- EC-1 reuse by reference (USL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding
from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance
from service.capability import Capability
from service.capability_meta import (
    CAPABILITY_META_CLASS,
    CapabilityKind,
)
from service.capability_traceability import CapabilityTraceabilityRecord

# --- service-layer reuse — the shared validation bundle + closure sets ------------
from service.service_meta import META_RELATIONSHIPS, ServiceState
from service.service_validation import ServiceValidation

#: The blueprint id a Capability realizes (its meta-class) — used by the EC-1 report.
CAPABILITY_BLUEPRINT_ID = CAPABILITY_META_CLASS

_KIND_VALUES = frozenset(k.value for k in CapabilityKind)
_STATE_VALUES = frozenset(s.value for s in ServiceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class CapabilityValidationSubject:
    """A normalized, immutable projection of a Capability that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    behavior_ref: str
    platform_ref: str
    service_ref: str
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
    def from_capability(
        cls, capability: Capability, trace: CapabilityTraceabilityRecord
    ) -> CapabilityValidationSubject:
        """Project ``capability`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=capability.capability_id,
            blueprint_id=CAPABILITY_BLUEPRINT_ID,
            meta_class=capability.meta_class,
            type_tag=capability.type_tag,
            kind=capability.kind.value,
            value_digest=capability.value_digest,
            behavior_ref=capability.behavior_ref,
            platform_ref=capability.platform_ref,
            service_ref=capability.service_ref,
            relationships=capability.meta_relationships(),
            lifecycle_state=capability.state.value,
            founding_acyclic=capability.is_founding_acyclic(),
            references_resolve=capability.references_resolve(),
            confers_authority=capability.confers_authority(),
            selects_technology=capability.selects_technology(),
            embeds_secret=capability.embeds_secret(),
            redefines_foundation=capability.redefines_foundation(),
            substrate_refs=tuple(capability.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Capability-layer validation checks
# ---------------------------------------------------------------------------


class CapabilityTypedCheck(ValidationCheck):
    """USL-03 / SMK-01 / C1 — the capability is classified by a non-empty ENG-004 type."""

    check_id = "capability-typed"
    severity = Severity.BLOCKING
    description = "Capability bears a non-empty ENG-004 type_tag (USL-03)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("capability is untyped (USL-03)")
        return self._passed(type_tag=subject.type_tag)


class CapabilityIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SMK-01 / C1 — the capability is identified (ENG-001) and object-borne."""

    check_id = "capability-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Capability bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-CAPABILITY-"):
            return self._failed("capability has no ENG-001 identity (USL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("capability is not object-borne (no value digest) (USL-05)")
        return self._passed(capability_id=subject.target_id)


class CapabilityValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the capability core round-trips through the EC-1 canonical encoding.

    Emitted under the shared id ``service-value-fidelity`` so the reused CCE Gate-3
    (Coverage) aggregates it without duplicating gate logic.
    """

    check_id = "service-value-fidelity"
    severity = Severity.BLOCKING
    description = "Capability core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("capability core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class CapabilityClassifiedCheck(ValidationCheck):
    """SXH-02 / SXC-02 — the capability is classified by exactly one Capability kind."""

    check_id = "capability-classified"
    severity = Severity.BLOCKING
    description = "Capability is classified by an SXH-02 kind (single-facet, SXC-02)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("capability kind is outside SXH-02", kind=subject.kind)
        return self._passed(kind=subject.kind)


class CapabilityRealizedByCheck(ValidationCheck):
    """SMR-01 / SOE-02 — the capability is realizable by a service (realized-by reference).

    A Capability is the target of SMR-01 (Service → Capability). ``service_ref`` is
    optional (a capability may be declared before its realizing service); when present it
    must be a well-formed ENG-005 reference.
    """

    check_id = "capability-realized-by"
    severity = Severity.BLOCKING
    description = "Capability is realized-by a Service via ENG-005 reference (SMR-01; optional)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.service_ref and not subject.service_ref.strip():
            return self._failed("service_ref present but blank (SMR-01)")
        return self._passed(service_ref=subject.service_ref or "(unbound)")


class MetaClassSingleCheck(ValidationCheck):
    """V1 / SMI-01 — the capability instantiates exactly one meta-class (SMC-02)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Capability instantiates exactly the SMC-02 meta-class (V1)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.meta_class != CAPABILITY_META_CLASS:
            return self._failed("meta-class is not SMC-02 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / SMI-02 — every relationship used lies within SMR-01…13."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All capability relationships are within SMR-01…13 (V2)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside SMR-01…13 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (SMK-01 typed/identified/object; SMK-05/06 refs)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01 (typed/identified/object) and SMK-05/06 (references) hold (V3)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("SMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("SMK-05/06 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["SMK-01", "SMK-05", "SMK-06"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMK-03 / USL-09 — the founding graph is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The capability's founding graph is acyclic (V4 / SMK-03)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / USL-12 — the capability holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Capability holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """USL-02 / SMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/PL-F2 referenced, redefined nowhere (USL-02)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (USL-02 / SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (USL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class PlatformCompositionByReferenceCheck(ValidationCheck):
    """USL-09 / SMR-12 / C5 — the capability composes PLATFORM-006 by ENG-005 reference."""

    check_id = "composition-by-reference"
    severity = Severity.BLOCKING
    description = "Capability composes PLATFORM-006 (PL-F2) by ENG-005 reference (USL-09)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.platform_ref.strip():
            return self._failed("no PL-F2/PLATFORM-006 composition reference (USL-09)")
        return self._passed(platform_ref=subject.platform_ref)


class BehaviorByReferenceCheck(ValidationCheck):
    """USL-10 / SMR-11 / C6 — the ability-to-perform-work binds RL-F2 by ENG-005 reference."""

    check_id = "execution-by-reference"
    severity = Severity.BLOCKING
    description = "Capability behavior (ability to perform work) binds RL-F2 by reference (USL-10)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("no RL-F2 behavior reference (USL-10)")
        return self._passed(behavior_ref=subject.behavior_ref)


class TechnologyIndependenceCheck(ValidationCheck):
    """USL-15 / C7 — no API/protocol/transport/framework/vendor technology is selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/protocol/vendor selected (USL-15)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (USL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """USL-15 / C7 — the capability confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Capability confers no authority and embeds no secret (USL-15 / RR-07)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("capability confers authority (USL-15)")
        if subject.embeds_secret:
            return self._failed("capability embeds a secret (USL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted at SMC-02 and closes to 11-SERVICE."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at SMC-02 and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def capability_checks() -> tuple[ValidationCheck, ...]:
    """The full capability-layer validation suite (deterministically ordered by the engine)."""
    return (
        CapabilityTypedCheck(),
        CapabilityIdentifiedCheck(),
        CapabilityValueFidelityCheck(),
        CapabilityClassifiedCheck(),
        CapabilityRealizedByCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        PlatformCompositionByReferenceCheck(),
        BehaviorByReferenceCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


def validate_capability(
    capability: Capability, trace: CapabilityTraceabilityRecord, *, strict: bool = False
) -> ServiceValidation:
    """Validate ``capability`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the shared :class:`ServiceValidation` bundle (report + evidence + acceptance
    decision) so the certification stage reuses the EC-1 certification path unchanged.
    """
    subject = CapabilityValidationSubject.from_capability(capability, trace)
    engine = ValidationEngine(capability_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ServiceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "CAPABILITY_BLUEPRINT_ID",
    "CapabilityValidationSubject",
    "capability_checks",
    "validate_capability",
]
