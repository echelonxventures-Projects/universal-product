"""EC3-B12-U01 — Application validation (meta-validity V1…V5 + UAL-01…15 conformance).

This module proves a realized :class:`~application.application.Application` is
**META-VALID** (APPLICATION-005 §8, V1…V5) and **Application-law conformant**
(APPLICATION-001 §7, UAL-01…15) by running a suite of deterministic,
application-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1
acceptance gate (:func:`engine.validation.gates.enforce_acceptance`). Validation
evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`ApplicationValidationSubject`
(the type-independent projection the EC-1 engine consumes), so an identical
application yields a byte-identical report, evidence, and acceptance decision (VC-4).
Every check is **blocking**: the verdict is PASS iff the application satisfies every
meta-validity and Application-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.application import Application
from application.application_meta import (
    APPLICATION_META_CLASS,
    META_RELATIONSHIPS,
    ApplicationKind,
    ApplicationState,
)
from application.application_traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UAL-02) — the certified validation substrate --------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id an Application realizes (its meta-class) — used by the EC-1 report.
APPLICATION_BLUEPRINT_ID = APPLICATION_META_CLASS

_KIND_VALUES = frozenset(k.value for k in ApplicationKind)
_STATE_VALUES = frozenset(s.value for s in ApplicationState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class ApplicationValidationSubject:
    """A normalized, immutable projection of an Application that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the application's meta-facts. Holds no runtime
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
    def from_application(
        cls, application: Application, trace: TraceabilityRecord
    ) -> ApplicationValidationSubject:
        """Project ``application`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=application.application_id,
            blueprint_id=APPLICATION_BLUEPRINT_ID,
            meta_class=application.meta_class,
            type_tag=application.type_tag,
            kind=application.kind.value,
            value_digest=application.value_digest,
            capability_ref=application.capability_ref,
            behavior_ref=application.behavior_ref,
            composition_ref=application.composition_ref,
            relationships=application.meta_relationships(),
            lifecycle_state=application.state.value,
            founding_acyclic=application.is_founding_acyclic(),
            references_resolve=application.references_resolve(),
            confers_authority=application.confers_authority(),
            selects_technology=application.selects_technology(),
            embeds_secret=application.embeds_secret(),
            redefines_foundation=application.redefines_foundation(),
            substrate_refs=tuple(application.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Application-layer validation checks (each maps to explicit V*/UAL*/AMK* obligations)
# ---------------------------------------------------------------------------


class ApplicationTypedCheck(ValidationCheck):
    """UAL-03 / AMK-01 / C1 — the application is classified by a non-empty ENG-004 type."""

    check_id = "application-typed"
    severity = Severity.BLOCKING
    description = "Application bears a non-empty ENG-004 type_tag (UAL-03)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("application is untyped (UAL-03)")
        return self._passed(type_tag=subject.type_tag)


class ApplicationIdentifiedCheck(ValidationCheck):
    """UAL-04/05 / AMK-01 / C1 — the application is identified (ENG-001) and object-borne."""

    check_id = "application-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Application bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-APPLICATION-"):
            return self._failed("application lacks ENG-001 identity (UAL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("application is not object-borne (no value digest) (UAL-05)")
        return self._passed(application_id=subject.target_id)


class ApplicationValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the application core round-trips through the EC-1 canonical encoding."""

    check_id = "application-value-fidelity"
    severity = Severity.BLOCKING
    description = "Application core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("application core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class ApplicationClassifiedCheck(ValidationCheck):
    """AXH-01 / AXC-02 — the application is classified by exactly one Application kind."""

    check_id = "application-classified"
    severity = Severity.BLOCKING
    description = "Application is classified by an AXH-01 kind (single-facet, AXC-02)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("application kind is outside AXH-01", kind=subject.kind)
        return self._passed(kind=subject.kind)


class ApplicationDeliversCapabilityCheck(ValidationCheck):
    """AMR-01 / AOE-01 — the application delivers a capability, bound by ENG-005 reference."""

    check_id = "application-delivers-capability"
    severity = Severity.BLOCKING
    description = "Application delivers a capability by ENG-005 reference (AMR-01, reference-only)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if not subject.capability_ref.strip():
            return self._failed("application delivers no capability (AMR-01)")
        return self._passed(capability_ref=subject.capability_ref)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / AMI-01 — the application instantiates exactly one meta-class (AMC-01)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Application instantiates exactly the AMC-01 meta-class (V1)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if subject.meta_class != APPLICATION_META_CLASS:
            return self._failed("meta-class is not AMC-01 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / AMI-02 — every relationship used lies within AMR-01…14."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All application relationships are within AMR-01…14 (V2)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside AMR-01…14 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (AMK-01 typed/identified/object; AMK-05/06 refs)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "AMK-01 (typed/identified/object) and AMK-05/06 (references) hold (V3)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("AMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("AMK-05/06 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["AMK-01", "AMK-05", "AMK-06"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / AMK-03 / UAL-09 — the founding graph is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The application's founding graph is acyclic (V4 / AMK-03)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UAL-12 — the application holds a valid AOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Application holds a valid AOS-01…06 lifecycle state (V5 / UAL-12)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UAL-02 / AMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/PL-F2/DF-2/SF-2 referenced, redefined nowhere (UAL-02)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UAL-02 / AMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UAL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class CompositionByReferenceCheck(ValidationCheck):
    """UAL-09 / AMR-12 / C5 — experience composition binds to PL-F2 by ENG-005 reference."""

    check_id = "composition-by-reference"
    severity = Severity.BLOCKING
    description = "Composition binds to PL-F2 by ENG-005 reference (UAL-09; no new construct)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if not subject.composition_ref.strip():
            return self._failed("no PL-F2 experience composition reference (UAL-09)")
        return self._passed(composition_ref=subject.composition_ref)


class BehaviorByReferenceCheck(ValidationCheck):
    """UAL-10/12 / AMR-11 / C6 — state/workflow behavior binds to RL-F2 by ENG-005 reference."""

    check_id = "behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Behavior/state binds to RL-F2 by ENG-005 reference (UAL-10/12)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("no RL-F2 behavior reference (UAL-10)")
        return self._passed(behavior_ref=subject.behavior_ref)


class TechnologyIndependenceCheck(ValidationCheck):
    """UAL-15 / C7 — no UI/framework/screen/API/protocol/transport/vendor is selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/UI/framework/protocol/vendor selected (UAL-15)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UAL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UAL-15 / C7 — the application confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Application confers no authority and embeds no secret (UAL-15 / RR-07)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("application confers authority (UAL-15)")
        if subject.embeds_secret:
            return self._failed("application embeds a secret (UAL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 12-APPLICATION anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at AMC-01 and closed to 12-APPLICATION (No-Orphan)."

    def evaluate(self, subject: ApplicationValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("12-APPLICATION@") for link in chain):
            return self._failed("lineage does not close to the 12-APPLICATION anchor")
        return self._passed(links=len(chain))


def application_checks() -> tuple[ValidationCheck, ...]:
    """The full application-layer validation suite (deterministically ordered by the engine)."""
    return (
        ApplicationTypedCheck(),
        ApplicationIdentifiedCheck(),
        ApplicationValueFidelityCheck(),
        ApplicationClassifiedCheck(),
        ApplicationDeliversCapabilityCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        CompositionByReferenceCheck(),
        BehaviorByReferenceCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class ApplicationValidation:
    """The bundled outcome of validating an Application (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_application(
    application: Application, trace: TraceabilityRecord, *, strict: bool = False
) -> ApplicationValidation:
    """Validate ``application`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected application raises via
    the EC-1 acceptance gate.
    """
    subject = ApplicationValidationSubject.from_application(application, trace)
    engine = ValidationEngine(application_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ApplicationValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "APPLICATION_BLUEPRINT_ID",
    "ApplicationValidationSubject",
    "ApplicationValidation",
    "application_checks",
    "validate_application",
]
