"""EC3-B12-U02 — Capability validation (meta-validity V1…V5 + UAL/CAP conformance).

This module proves a realized :class:`~application.capability.Capability` is
**META-VALID** (APPLICATION-005 §8, V1…V5) and **Application-/Capability-law conformant**
(APPLICATION-001 §7, UAL-01…15; APPLICATION-006 §4, CAP-01…10) by running a suite of
deterministic, application-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate (:func:`engine.validation.gates.enforce_acceptance`). Validation evidence is produced
with the EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`CapabilityValidationSubject`
(the type-independent projection the EC-1 engine consumes), so an identical capability
yields a byte-identical report, evidence, and acceptance decision (VC-4). Every check is
**blocking**: the verdict is PASS iff the capability satisfies every meta-validity and
Application-/Capability-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.capability import Capability
from application.capability_meta import (
    CAPABILITY_META_CLASS,
    META_RELATIONSHIPS,
    CapabilityKind,
    CapabilityState,
)
from application.capability_traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UAL-02) — the certified validation substrate --------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Capability realizes (its meta-class) — used by the EC-1 report.
CAPABILITY_BLUEPRINT_ID = CAPABILITY_META_CLASS

_KIND_VALUES = frozenset(k.value for k in CapabilityKind)
_STATE_VALUES = frozenset(s.value for s in CapabilityState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class CapabilityValidationSubject:
    """A normalized, immutable projection of a Capability that checks evaluate.

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
    operation_ref: str
    data_ref: str
    behavior_ref: str
    composition_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    delivery_side: str
    founding_acyclic: bool
    references_resolve: bool
    consumes_operation: bool
    bounded: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_capability(
        cls, capability: Capability, trace: TraceabilityRecord
    ) -> CapabilityValidationSubject:
        """Project ``capability`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=capability.capability_id,
            blueprint_id=CAPABILITY_BLUEPRINT_ID,
            meta_class=capability.meta_class,
            type_tag=capability.type_tag,
            kind=capability.kind.value,
            value_digest=capability.value_digest,
            operation_ref=capability.operation_ref,
            data_ref=capability.data_ref,
            behavior_ref=capability.behavior_ref,
            composition_ref=capability.composition_ref,
            relationships=capability.meta_relationships(),
            lifecycle_state=capability.state.value,
            delivery_side=capability.delivery_side(),
            founding_acyclic=capability.is_founding_acyclic(),
            references_resolve=capability.references_resolve(),
            consumes_operation=capability.consumes_operation(),
            bounded=capability.is_bounded(),
            confers_authority=capability.confers_authority(),
            selects_technology=capability.selects_technology(),
            embeds_secret=capability.embeds_secret(),
            redefines_foundation=capability.redefines_foundation(),
            substrate_refs=tuple(capability.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Capability-layer validation checks (each maps to explicit V*/UAL*/CAP*/AMK* obligations)
# ---------------------------------------------------------------------------


class CapabilityTypedCheck(ValidationCheck):
    """UAL-03 / CAP-01 / AMK-01 / C1 — the capability is classified by a non-empty type."""

    check_id = "capability-typed"
    severity = Severity.BLOCKING
    description = "Capability bears a non-empty ENG-004 type_tag (UAL-03 / CAP-01)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("capability is untyped (UAL-03)")
        return self._passed(type_tag=subject.type_tag)


class CapabilityIdentifiedCheck(ValidationCheck):
    """UAL-04/05 / CAP-02 / AMK-01 / C1 — the capability is identified and object-borne."""

    check_id = "capability-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Capability bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-CAPABILITY-"):
            return self._failed("capability lacks ENG-001 identity (UAL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("capability is not object-borne (no value digest) (UAL-05)")
        return self._passed(capability_id=subject.target_id)


class CapabilityValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the capability core round-trips through the EC-1 canonical encoding."""

    check_id = "capability-value-fidelity"
    severity = Severity.BLOCKING
    description = "Capability core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("capability core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class CapabilityClassifiedCheck(ValidationCheck):
    """AXH-02 / AXC-02 — the capability is classified by exactly one Capability kind."""

    check_id = "capability-classified"
    severity = Severity.BLOCKING
    description = "Capability is classified by an AXH-02 kind (single-facet, AXC-02)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("capability kind is outside AXH-02", kind=subject.kind)
        return self._passed(kind=subject.kind, delivery_side=subject.delivery_side)


class CapabilityConsumesOperationCheck(ValidationCheck):
    """AMR-13 / CAP-05 / UAL-06 — the capability consumes an SF-2 operation by reference."""

    check_id = "capability-consumes-operation"
    severity = Severity.BLOCKING
    description = "Capability consumes an SF-2 operation by ENG-005 reference (AMR-13 / CAP-05)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.consumes_operation or not subject.operation_ref.strip():
            return self._failed("capability consumes no SF-2 operation (AMR-13 / CAP-05)")
        return self._passed(operation_ref=subject.operation_ref)


class CapabilityPresentsDataCheck(ValidationCheck):
    """AMR-14 / CAP-07 / UAL-13 — the capability's delivered data references DF-2."""

    check_id = "capability-presents-data"
    severity = Severity.BLOCKING
    description = "Capability's delivered data references DF-2 by ENG-005 reference (AMR-14)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.data_ref.strip():
            return self._failed("capability presents no DF-2 data reference (AMR-14 / CAP-07)")
        return self._passed(data_ref=subject.data_ref)


class CapabilityBoundedCheck(ValidationCheck):
    """CAP-06 / CAP-C1 / UAL-08 — the capability declares an explicit, decidable scope."""

    check_id = "capability-bounded"
    severity = Severity.BLOCKING
    description = "Capability declares an explicit, decidable scope of delivered ability (CAP-06)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.bounded:
            return self._failed("capability scope is not explicitly bounded (CAP-06 / UAL-08)")
        return self._passed()


class MetaClassSingleCheck(ValidationCheck):
    """V1 / AMI-01 — the capability instantiates exactly one meta-class (AMC-02)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Capability instantiates exactly the AMC-02 meta-class (V1)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.meta_class != CAPABILITY_META_CLASS:
            return self._failed("meta-class is not AMC-02 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / AMI-02 — every relationship used lies within AMR-01…14."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All capability relationships are within AMR-01…14 (V2)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside AMR-01…14 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (AMK-01 typed/id/object; AMK-05/06/07 references)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "AMK-01 (typed/identified/object) and AMK-05/06/07 (references) hold (V3)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("AMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("AMK-05/06/07 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["AMK-01", "AMK-05", "AMK-06", "AMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / AMK-03 / CAP-C3 / UAL-09 — the founding graph is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The capability's founding graph is acyclic (V4 / AMK-03 / CAP-C3)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UAL-12 — the capability holds a valid AOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Capability holds a valid AOS-01…06 lifecycle state (V5 / UAL-12)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UAL-02 / CAP-03 / AMI-05 / VC-5 — frozen foundations reused by reference, not redefined."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/PL-F2/SF-2/DF-2 referenced, redefined nowhere (UAL-02 / CAP-03)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UAL-02 / AMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UAL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class CompositionByReferenceCheck(ValidationCheck):
    """UAL-09 / AMR-12 / C5 — experience composition binds to PL-F2 by ENG-005 reference."""

    check_id = "composition-by-reference"
    severity = Severity.BLOCKING
    description = "Composition binds to PL-F2 by ENG-005 reference (UAL-09; PLATFORM-006/009)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.composition_ref.strip():
            return self._failed("no PL-F2 experience composition reference (UAL-09)")
        return self._passed(composition_ref=subject.composition_ref)


class BehaviorByReferenceCheck(ValidationCheck):
    """UAL-10/12 / AMR-11 / C6 — deliver/transact/emit behavior binds to RL-F2 by reference."""

    check_id = "behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Behavior binds to RL-F2 by ENG-005 reference (UAL-10; deliver/transact/emit)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("no RL-F2 behavior reference (UAL-10)")
        return self._passed(behavior_ref=subject.behavior_ref)


class TechnologyIndependenceCheck(ValidationCheck):
    """UAL-15 / CAP-09 / C7 — no UI/framework/screen/API/protocol/transport/vendor is selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/UI/framework/protocol/vendor selected (UAL-15)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UAL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UAL-15 / CAP-09 / C7 — the capability confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Capability confers no authority and embeds no secret (UAL-15 / RR-07)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("capability confers authority (UAL-15)")
        if subject.embeds_secret:
            return self._failed("capability embeds a secret (UAL-15 / RR-07)")
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
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 12-APPLICATION anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at AMC-02 and closed to 12-APPLICATION (No-Orphan)."

    def evaluate(self, subject: CapabilityValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("12-APPLICATION@") for link in chain):
            return self._failed("lineage does not close to the 12-APPLICATION anchor")
        return self._passed(links=len(chain))


def capability_checks() -> tuple[ValidationCheck, ...]:
    """The full capability-layer validation suite (deterministically ordered by the engine)."""
    return (
        CapabilityTypedCheck(),
        CapabilityIdentifiedCheck(),
        CapabilityValueFidelityCheck(),
        CapabilityClassifiedCheck(),
        CapabilityConsumesOperationCheck(),
        CapabilityPresentsDataCheck(),
        CapabilityBoundedCheck(),
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
class CapabilityValidation:
    """The bundled outcome of validating a Capability (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_capability(
    capability: Capability, trace: TraceabilityRecord, *, strict: bool = False
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
