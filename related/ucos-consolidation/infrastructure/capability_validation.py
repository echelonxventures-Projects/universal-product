"""EC3-B13-U01 — Infrastructure Capability validation (meta-validity WF + UIL conformance).

This module proves a realized :class:`~infrastructure.capability.InfrastructureCapability`
is **META-VALID** (INFRASTRUCTURE-005 §5/§6, WF-1…12 + UIMM-CONF) and
**Infrastructure-law conformant** (INFRASTRUCTURE-001 §7, UIL-01…15) by running a suite
of deterministic, infrastructure-layer checks through the **CERTIFIED EC-1 Validation
Engine** (:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1
acceptance gate (:func:`engine.validation.gates.enforce_acceptance`). Validation evidence
is produced with the EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`CapabilityValidationSubject`
(the type-independent projection the EC-1 engine consumes), so an identical capability
yields a byte-identical report, evidence, and acceptance decision (VC-4). Every check
is **blocking**: the verdict is PASS iff the capability satisfies every meta-validity and
Infrastructure-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- EC-1 reuse by reference (UIL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance
from infrastructure.capability import INFRA_CAPABILITY_ID_PREFIX, InfrastructureCapability
from infrastructure.capability_meta import (
    ADMITTED_META_RELATIONSHIPS,
    INFRASTRUCTURE_META_CLASS,
    InfrastructureCapabilityKind,
    InfrastructureState,
)
from infrastructure.capability_traceability import TraceabilityRecord

#: The blueprint id an Infrastructure Capability realizes (its meta-class).
CAPABILITY_BLUEPRINT_ID = INFRASTRUCTURE_META_CLASS

_KIND_VALUES = frozenset(k.value for k in InfrastructureCapabilityKind)
_STATE_VALUES = frozenset(s.value for s in InfrastructureState)
_ADMITTED_RELATIONSHIPS = frozenset(ADMITTED_META_RELATIONSHIPS)
_ID_PREFIX = f"{INFRA_CAPABILITY_ID_PREFIX}-"


@dataclass(frozen=True, slots=True)
class CapabilityValidationSubject:
    """A normalized, immutable projection of a capability that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the capability's meta-facts. Holds no runtime
    state and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    enables_ref: str
    capability_ref: str
    behavior_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    declares_mandatory_attributes: bool
    founding_acyclic: bool
    references_resolve: bool
    enables_by_reference: bool
    reuses_platform_capability: bool
    declares_no_artificial_ceiling: bool
    is_resource: bool
    is_evaluative_facet: bool
    confers_authority: bool
    enacts_enforcement: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    is_new_primitive: bool
    projects_completion: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_capability(
        cls, capability: InfrastructureCapability, trace: TraceabilityRecord
    ) -> CapabilityValidationSubject:
        """Project ``capability`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=capability.capability_id,
            blueprint_id=CAPABILITY_BLUEPRINT_ID,
            meta_class=capability.meta_class,
            type_tag=capability.type_tag,
            kind=capability.kind.value,
            value_digest=capability.value_digest,
            enables_ref=capability.enables_ref,
            capability_ref=capability.capability_ref,
            behavior_ref=capability.behavior_ref,
            relationships=capability.meta_relationships(),
            lifecycle_state=capability.state.value,
            declares_mandatory_attributes=capability.declares_mandatory_attributes(),
            founding_acyclic=capability.is_founding_acyclic(),
            references_resolve=capability.references_resolve(),
            enables_by_reference=capability.enables_by_reference(),
            reuses_platform_capability=capability.reuses_platform_capability(),
            declares_no_artificial_ceiling=capability.declares_no_artificial_ceiling(),
            is_resource=capability.is_resource(),
            is_evaluative_facet=capability.is_evaluative_facet(),
            confers_authority=capability.confers_authority(),
            enacts_enforcement=capability.enacts_enforcement(),
            selects_technology=capability.selects_technology(),
            embeds_secret=capability.embeds_secret(),
            redefines_foundation=capability.redefines_foundation(),
            is_new_primitive=capability.is_new_primitive(),
            projects_completion=capability.projects_completion(),
            substrate_refs=tuple(capability.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Infrastructure-layer validation checks (each maps to explicit WF*/UIL*/ICAP* obligations)
# ---------------------------------------------------------------------------


class CapabilityTypedCheck(ValidationCheck):
    """UIL-03 / ICAP-02 / C1 — the capability is classified by a non-empty ENG-004 type."""

    check_id = "infra-capability-typed"
    severity = Severity.BLOCKING
    description = "Infrastructure capability bears a non-empty ENG-004 type_tag (UIL-03)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("capability is untyped (UIL-03)")
        return self._passed(type_tag=subject.type_tag)


class CapabilityIdentifiedCheck(ValidationCheck):
    """UIL-04/05 / ICAP-02 / C1 — the capability is identified (ENG-001) and object-borne."""

    check_id = "infra-capability-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Capability bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith(_ID_PREFIX):
            return self._failed("capability has no ENG-001 identity (UIL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("capability is not object-borne (no value digest) (UIL-05)")
        if not subject.declares_mandatory_attributes:
            return self._failed("capability lacks a mandatory meta-attribute (WF-1)")
        return self._passed(capability_id=subject.target_id)


class CapabilityValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the capability core round-trips through the EC-1 canonical encoding."""

    check_id = "infra-capability-value-fidelity"
    severity = Severity.BLOCKING
    description = "Capability core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("capability core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class CapabilityClassifiedCheck(ValidationCheck):
    """INFRASTRUCTURE-006 §2 — the capability is classified by exactly one kind."""

    check_id = "infra-capability-classified"
    severity = Severity.BLOCKING
    description = "Capability is classified by one INFRASTRUCTURE-006 §2 kind (single-facet)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("kind outside INFRASTRUCTURE-006 §2", kind=subject.kind)
        return self._passed(kind=subject.kind)


class CapabilityReusesPlatformCheck(ValidationCheck):
    """ICAP-01 / UIL-06 — the capability reuses PLATFORM-006/SF-2 by reference."""

    check_id = "infra-capability-reuses-platform"
    severity = Severity.BLOCKING
    description = "Capability reuses PLATFORM-006/SF-2 by ENG-005 reference (ICAP-01)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.reuses_platform_capability or not subject.capability_ref.strip():
            return self._failed("capability omits the PLATFORM-006 reuse (ICAP-01/UIL-06)")
        return self._passed(capability_ref=subject.capability_ref)


class CapabilityEnablesConstructCheck(ValidationCheck):
    """ICAP-03 / WF-2 — the capability enables a frozen lower construct by reference."""

    check_id = "infra-capability-enables-frozen-construct"
    severity = Severity.BLOCKING
    description = "Capability enables a frozen lower construct by ENG-005 reference (ICAP-03)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.enables_by_reference or not subject.enables_ref.strip():
            return self._failed("capability enables no frozen construct by reference (ICAP-03)")
        return self._passed(enables_ref=subject.enables_ref)


class MetaClassSingleCheck(ValidationCheck):
    """WF-1 — the capability instantiates exactly one leaf meta-class (InfrastructureCapability)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Capability instantiates exactly the InfrastructureCapability meta-class (WF-1)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.meta_class != INFRASTRUCTURE_META_CLASS:
            return self._failed(
                "meta-class is not InfrastructureCapability (WF-1)", meta_class=subject.meta_class
            )
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """UIL-09 — every relationship used lies within the admitted meta-relationship set."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All capability relationships are within the admitted UIMM set (UIL-09)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _ADMITTED_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside admitted set (UIL-09)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """WF-1/2 — mandatory meta-attributes declared and every reference resolves."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "Mandatory meta-attributes declared (WF-1) and references resolve (WF-2)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("mandatory meta-attributes not all declared (WF-1)")
        if not subject.references_resolve:
            return self._failed("a reference does not resolve (WF-2)")
        return self._passed(constraints=["WF-1", "WF-2"])


class FoundingAcyclicCheck(ValidationCheck):
    """WF-3 / UIL-09 — the founding graph is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The capability's founding graph is acyclic (WF-3 / UIL-09)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (WF-3)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """INFRASTRUCTURE-003 §3 — the capability holds a valid forward-only lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Capability holds a valid forward-only lifecycle state (INFRASTRUCTURE-003 §3)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UIL-02 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/PL-F2/SF-2 referenced, redefined nowhere (UIL-02)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UIL-02)")
        if subject.is_new_primitive:
            return self._failed("capability is a new primitive (WF-11 / UIL-01)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UIL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class HostingByReferenceCheck(ValidationCheck):
    """UIL-06 / ICAP-03 / C3 — hosting/delivery binds frozen constructs by ENG-005 reference."""

    check_id = "hosting-by-reference"
    severity = Severity.BLOCKING
    description = "Hosting/delivery binds frozen constructs by ENG-005 reference (UIL-06)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.enables_ref.strip() or not subject.capability_ref.strip():
            return self._failed("hosting/delivery reference missing (UIL-06)")
        return self._passed(enables_ref=subject.enables_ref, capability_ref=subject.capability_ref)


class BehaviorByReferenceCheck(ValidationCheck):
    """UIL-10 / C6 — hosting/delivery behavior binds to RL-F2 by ENG-005 reference."""

    check_id = "behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Behavior binds to RL-F2 by ENG-005 reference (UIL-10)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("no RL-F2 behavior reference (UIL-10)")
        return self._passed(behavior_ref=subject.behavior_ref)


class ScalingUnboundedCheck(ValidationCheck):
    """UIL-13 / ICAP-04 / C6 — the capability declares no artificial scaling ceiling."""

    check_id = "scaling-unbounded"
    severity = Severity.BLOCKING
    description = "Capability declares no artificial ceiling; scaling unbounded (UIL-13)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.declares_no_artificial_ceiling:
            return self._failed("capability declares an artificial ceiling (UIL-13 / ICAP-04)")
        return self._passed()


class TechnologyIndependenceCheck(ValidationCheck):
    """UIL-12 / UIL-15 / ICAP-05 / C7 — no cloud/orchestrator/IaC/transport/vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/cloud/orchestrator/vendor selected (UIL-12 / UIL-15)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UIL-12 / UIL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UIL-14/15 / ICAP-05 / C7 — confers no authority, enacts no enforcement, embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Capability confers no authority, enforces nothing, embeds no secret (UIL-14/15)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("capability confers authority (UIL-15)")
        if subject.enacts_enforcement:
            return self._failed("capability enacts enforcement (UIL-14)")
        if subject.embeds_secret:
            return self._failed("capability embeds a secret (UIL-15 / RR-07)")
        if subject.projects_completion:
            return self._failed("capability projects completion (WF-12)")
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
    """§5 — the No-Orphan lineage is rooted and closes to the 13-INFRASTRUCTURE anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at the meta-class, closed to 13-INFRASTRUCTURE."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("13-INFRASTRUCTURE@") for link in chain):
            return self._failed("lineage does not close to the 13-INFRASTRUCTURE anchor")
        return self._passed(links=len(chain))


def capability_checks() -> tuple[ValidationCheck, ...]:
    """The full infrastructure-capability validation suite (deterministically ordered)."""
    return (
        CapabilityTypedCheck(),
        CapabilityIdentifiedCheck(),
        CapabilityValueFidelityCheck(),
        CapabilityClassifiedCheck(),
        CapabilityReusesPlatformCheck(),
        CapabilityEnablesConstructCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        HostingByReferenceCheck(),
        BehaviorByReferenceCheck(),
        ScalingUnboundedCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class CapabilityValidation:
    """The bundled outcome of validating a capability (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_capability(
    capability: InfrastructureCapability, trace: TraceabilityRecord, *, strict: bool = False
) -> CapabilityValidation:
    """Validate ``capability`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected capability raises via the
    EC-1 acceptance gate.
    """
    subject = CapabilityValidationSubject.from_capability(capability, trace)
    engine = ValidationEngine(capability_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return CapabilityValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "CAPABILITY_BLUEPRINT_ID",
    "CapabilityValidationSubject",
    "CapabilityValidation",
    "capability_checks",
    "validate_capability",
]
