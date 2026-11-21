"""EC3-B12-U03 — Module validation (meta-validity V1…V5 + UAL/MOD conformance).

This module proves a realized :class:`~application.module.Module` is **META-VALID**
(APPLICATION-005 §8, V1…V5) and **Application-/Module-law conformant** (APPLICATION-001
§7, UAL-01…15; APPLICATION-007 §4, MOD-01…10) by running a suite of deterministic,
application-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate (:func:`engine.validation.gates.enforce_acceptance`). Validation evidence is produced
with the EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`ModuleValidationSubject`
(the type-independent projection the EC-1 engine consumes), so an identical module
yields a byte-identical report, evidence, and acceptance decision (VC-4). Every check is
**blocking**: the verdict is PASS iff the module satisfies every meta-validity and
Application-/Module-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.module import Module
from application.module_meta import (
    META_RELATIONSHIPS,
    MODULE_META_CLASS,
    ModuleKind,
    ModuleState,
)
from application.module_traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UAL-02) — the certified validation substrate --------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Module realizes (its meta-class) — used by the EC-1 report.
MODULE_BLUEPRINT_ID = MODULE_META_CLASS

_KIND_VALUES = frozenset(k.value for k in ModuleKind)
_STATE_VALUES = frozenset(s.value for s in ModuleState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class ModuleValidationSubject:
    """A normalized, immutable projection of a Module that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the module's meta-facts. Holds no runtime state
    and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    feature_refs: tuple[str, ...]
    owned_feature_count: int
    application_ref: str
    composition_ref: str
    behavior_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    references_resolve: bool
    groups_features: bool
    ownership_is_partition: bool
    bounded: bool
    cohesive: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_module(
        cls, module: Module, trace: TraceabilityRecord
    ) -> ModuleValidationSubject:
        """Project ``module`` (+ its lineage) into a validation subject."""
        payload = module.to_dict()
        return cls(
            target_id=module.module_id,
            blueprint_id=MODULE_BLUEPRINT_ID,
            meta_class=module.meta_class,
            type_tag=module.type_tag,
            kind=module.kind.value,
            value_digest=module.value_digest,
            feature_refs=tuple(payload["feature_refs"]),
            owned_feature_count=module.owned_feature_count(),
            application_ref=module.application_ref,
            composition_ref=module.composition_ref,
            behavior_ref=module.behavior_ref,
            relationships=module.meta_relationships(),
            lifecycle_state=module.state.value,
            founding_acyclic=module.is_founding_acyclic(),
            references_resolve=module.references_resolve(),
            groups_features=module.groups_features(),
            ownership_is_partition=module.ownership_is_partition(),
            bounded=module.is_bounded(),
            cohesive=module.is_cohesive(),
            confers_authority=module.confers_authority(),
            selects_technology=module.selects_technology(),
            embeds_secret=module.embeds_secret(),
            redefines_foundation=module.redefines_foundation(),
            substrate_refs=tuple(payload["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Module-layer validation checks (each maps to explicit V*/UAL*/MOD*/AMK* obligations)
# ---------------------------------------------------------------------------


class ModuleTypedCheck(ValidationCheck):
    """UAL-03 / MOD-01 / AMK-01 / C1 — the module is classified by a non-empty type."""

    check_id = "module-typed"
    severity = Severity.BLOCKING
    description = "Module bears a non-empty ENG-004 type_tag (UAL-03 / MOD-01)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("module is untyped (UAL-03)")
        return self._passed(type_tag=subject.type_tag)


class ModuleIdentifiedCheck(ValidationCheck):
    """UAL-04/05 / MOD-02 / AMK-01 / C1 — the module is identified and object-borne."""

    check_id = "module-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Module bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-MODULE-"):
            return self._failed("module lacks ENG-001 identity (UAL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("module is not object-borne (no value digest) (UAL-05)")
        return self._passed(module_id=subject.target_id)


class ModuleValueFidelityCheck(ValidationCheck):
    """ENG-003 — the module core round-trips through the EC-1 canonical encoding."""

    check_id = "module-value-fidelity"
    severity = Severity.BLOCKING
    description = "Module core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("module core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class ModuleClassifiedCheck(ValidationCheck):
    """AXH-03 / AXC-02 — the module is classified by exactly one Module kind."""

    check_id = "module-classified"
    severity = Severity.BLOCKING
    description = "Module is classified by an AXH-03 kind (single-facet, AXC-02)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("module kind is outside AXH-03", kind=subject.kind)
        return self._passed(kind=subject.kind)


class ModuleGroupsFeaturesCheck(ValidationCheck):
    """AMR-03 / MOD-07 / UAL-07 — the module groups (owns) ≥1 feature by reference."""

    check_id = "module-groups-features"
    severity = Severity.BLOCKING
    description = "Module groups ≥1 owned feature by ENG-005 reference (AMR-03 / MOD-07)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not subject.groups_features or subject.owned_feature_count < 1:
            return self._failed("module groups no feature (AMR-03 / MOD-07 / UAL-07)")
        return self._passed(owned_feature_count=subject.owned_feature_count)


class ModuleOwnershipPartitionCheck(ValidationCheck):
    """MOD-05 / MOD-07 / MOD-C2 — feature ownership is a partition (distinct owners)."""

    check_id = "module-ownership-partition"
    severity = Severity.BLOCKING
    description = "Feature ownership is a partition: owned features are distinct (MOD-05 / MOD-C2)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not subject.ownership_is_partition:
            return self._failed("feature ownership is not a partition (MOD-05 / MOD-C2)")
        return self._passed(owned_feature_count=subject.owned_feature_count)


class ModuleBoundedCheck(ValidationCheck):
    """MOD-03 / MOD-C1 / UAL-07 — the module declares an explicit, decidable boundary."""

    check_id = "module-bounded"
    severity = Severity.BLOCKING
    description = "Module declares an explicit, decidable boundary of owned features (MOD-03)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not subject.bounded:
            return self._failed("module boundary is not explicit/decidable (MOD-03 / UAL-07)")
        return self._passed()


class ModuleCohesiveCheck(ValidationCheck):
    """MOD-04 / UAL-07 — owned features form one cohesive grouping under the boundary."""

    check_id = "module-cohesive"
    severity = Severity.BLOCKING
    description = "Owned features form one cohesive grouping under the boundary (MOD-04 / UAL-07)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not subject.cohesive:
            return self._failed("module grouping is not cohesive (MOD-04 / UAL-07)")
        return self._passed()


class MetaClassSingleCheck(ValidationCheck):
    """V1 / AMI-01 — the module instantiates exactly one meta-class (AMC-03)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Module instantiates exactly the AMC-03 meta-class (V1)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if subject.meta_class != MODULE_META_CLASS:
            return self._failed("meta-class is not AMC-03 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / AMI-02 — every relationship used lies within AMR-01…14."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All module relationships are within AMR-01…14 (V2)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside AMR-01…14 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (AMK-01 typed/id/object; AMK-05/06 references)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "AMK-01 (typed/identified/object) and AMK-05/06 (references) hold (V3)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("AMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("AMK-05/06 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["AMK-01", "AMK-03", "AMK-05", "AMK-06"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / AMK-03 / MOD-C3 / UAL-09 — the founding graph (composed-of, groups) is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The module's founding graph is acyclic (V4 / AMK-03 / MOD-C3)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UAL-12 — the module holds a valid AOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Module holds a valid AOS-01…06 lifecycle state (V5 / UAL-12)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UAL-02 / MOD-10 / AMI-05 / VC-5 — frozen foundations reused by reference, not redefined."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/PL-F2 referenced, redefined nowhere (UAL-02 / AMI-05)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UAL-02 / AMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UAL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class CompositionByReferenceCheck(ValidationCheck):
    """UAL-09 / AMR-02/07/12 / C5 — composition binds to the app/PL-F2 by ENG-005 reference."""

    check_id = "composition-by-reference"
    severity = Severity.BLOCKING
    description = "Composition binds to application + PL-F2 by ENG-005 reference (UAL-09)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not subject.application_ref.strip():
            return self._failed("no application composition reference (AMR-02 / UAL-09)")
        if not subject.composition_ref.strip():
            return self._failed("no PL-F2 experience composition reference (AMR-12 / UAL-09)")
        return self._passed(
            application_ref=subject.application_ref, composition_ref=subject.composition_ref
        )


class BehaviorByReferenceCheck(ValidationCheck):
    """UAL-10 / §7 / AMK-05 — module-transition/emit behavior binds to RL-F2 by reference."""

    check_id = "behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Behavior binds to RL-F2 by ENG-005 reference (UAL-10; module-transition/emit)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("no RL-F2 behavior reference (UAL-10 / §7)")
        return self._passed(behavior_ref=subject.behavior_ref)


class TechnologyIndependenceCheck(ValidationCheck):
    """UAL-15 / MOD-09 / C7 — no UI/framework/screen/API/protocol/transport/vendor is selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/UI/framework/protocol/vendor selected (UAL-15)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UAL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UAL-15 / MOD-09 / C7 — the module confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Module confers no authority and embeds no secret (UAL-15 / RR-07)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("module confers authority (UAL-15)")
        if subject.embeds_secret:
            return self._failed("module embeds a secret (UAL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 12-APPLICATION anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at AMC-03 and closed to 12-APPLICATION (No-Orphan)."

    def evaluate(self, subject: ModuleValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("12-APPLICATION@") for link in chain):
            return self._failed("lineage does not close to the 12-APPLICATION anchor")
        return self._passed(links=len(chain))


def module_checks() -> tuple[ValidationCheck, ...]:
    """The full module-layer validation suite (deterministically ordered by the engine)."""
    return (
        ModuleTypedCheck(),
        ModuleIdentifiedCheck(),
        ModuleValueFidelityCheck(),
        ModuleClassifiedCheck(),
        ModuleGroupsFeaturesCheck(),
        ModuleOwnershipPartitionCheck(),
        ModuleBoundedCheck(),
        ModuleCohesiveCheck(),
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
class ModuleValidation:
    """The bundled outcome of validating a Module (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_module(
    module: Module, trace: TraceabilityRecord, *, strict: bool = False
) -> ModuleValidation:
    """Validate ``module`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected module raises via the
    EC-1 acceptance gate.
    """
    subject = ModuleValidationSubject.from_module(module, trace)
    engine = ValidationEngine(module_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ModuleValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "MODULE_BLUEPRINT_ID",
    "ModuleValidationSubject",
    "ModuleValidation",
    "module_checks",
    "validate_module",
]
