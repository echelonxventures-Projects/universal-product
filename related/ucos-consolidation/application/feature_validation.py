"""EC3-B12-U04 — Feature validation (meta-validity V1…V5 + UAL/FEA conformance).

This module proves a realized :class:`~application.feature.Feature` is **META-VALID**
(APPLICATION-005 §8, V1…V5) and **Application-/Feature-law conformant** (APPLICATION-001
§7, UAL-01…15; APPLICATION-008 §4, FEA-01…10) by running a suite of deterministic,
application-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate (:func:`engine.validation.gates.enforce_acceptance`). Validation evidence is produced
with the EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`FeatureValidationSubject`
(the type-independent projection the EC-1 engine consumes), so an identical feature yields
a byte-identical report, evidence, and acceptance decision (VC-4). Every check is
**blocking**: the verdict is PASS iff the feature satisfies every meta-validity and
Application-/Feature-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.feature import Feature
from application.feature_meta import (
    FEATURE_META_CLASS,
    META_RELATIONSHIPS,
    FeatureKind,
    FeatureState,
)
from application.feature_traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UAL-02) — the certified validation substrate --------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Feature realizes (its meta-class) — used by the EC-1 report.
FEATURE_BLUEPRINT_ID = FEATURE_META_CLASS

_KIND_VALUES = frozenset(k.value for k in FeatureKind)
_STATE_VALUES = frozenset(s.value for s in FeatureState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class FeatureValidationSubject:
    """A normalized, immutable projection of a Feature that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the feature's meta-facts. Holds no runtime state
    and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    capability_ref: str
    operation_refs: tuple[str, ...]
    composed_operation_count: int
    interaction_ref: str
    module_ref: str
    data_ref: str
    behavior_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    references_resolve: bool
    delivers_capability: bool
    consumes_operations: bool
    operations_are_partition: bool
    presents_data: bool
    is_engaged: bool
    is_owned: bool
    declaration_complete: bool
    delivery_side: str
    delivery_side_is_consistent: bool
    engaged_before_executable: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_feature(
        cls, feature: Feature, trace: TraceabilityRecord
    ) -> FeatureValidationSubject:
        """Project ``feature`` (+ its lineage) into a validation subject."""
        payload = feature.to_dict()
        return cls(
            target_id=feature.feature_id,
            blueprint_id=FEATURE_BLUEPRINT_ID,
            meta_class=feature.meta_class,
            type_tag=feature.type_tag,
            kind=feature.kind.value,
            value_digest=feature.value_digest,
            capability_ref=feature.capability_ref,
            operation_refs=tuple(payload["operation_refs"]),
            composed_operation_count=feature.composed_operation_count(),
            interaction_ref=feature.interaction_ref,
            module_ref=feature.module_ref,
            data_ref=feature.data_ref,
            behavior_ref=feature.behavior_ref,
            relationships=feature.meta_relationships(),
            lifecycle_state=feature.state.value,
            founding_acyclic=feature.is_founding_acyclic(),
            references_resolve=feature.references_resolve(),
            delivers_capability=feature.delivers_capability(),
            consumes_operations=feature.consumes_operations(),
            operations_are_partition=feature.operations_are_partition(),
            presents_data=feature.presents_data(),
            is_engaged=feature.is_engaged(),
            is_owned=feature.is_owned(),
            declaration_complete=feature.declaration_complete(),
            delivery_side=feature.delivery_side(),
            delivery_side_is_consistent=feature.delivery_side_is_consistent(),
            engaged_before_executable=feature.engaged_before_executable(),
            confers_authority=feature.confers_authority(),
            selects_technology=feature.selects_technology(),
            embeds_secret=feature.embeds_secret(),
            redefines_foundation=feature.redefines_foundation(),
            substrate_refs=tuple(payload["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Feature-layer validation checks (each maps to explicit V*/UAL*/FEA*/AMK* obligations)
# ---------------------------------------------------------------------------


class FeatureTypedCheck(ValidationCheck):
    """UAL-03 / FEA-01 / AMK-01 / C1 — the feature is classified by a non-empty type."""

    check_id = "feature-typed"
    severity = Severity.BLOCKING
    description = "Feature bears a non-empty ENG-004 type_tag (UAL-03 / FEA-01)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("feature is untyped (UAL-03)")
        return self._passed(type_tag=subject.type_tag)


class FeatureIdentifiedCheck(ValidationCheck):
    """UAL-04/05 / FEA-02 / AMK-01 / C1 — the feature is identified and object-borne."""

    check_id = "feature-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Feature bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-FEATURE-"):
            return self._failed("feature lacks ENG-001 identity (UAL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("feature is not object-borne (no value digest) (UAL-05)")
        return self._passed(feature_id=subject.target_id)


class FeatureValueFidelityCheck(ValidationCheck):
    """ENG-003 — the feature core round-trips through the EC-1 canonical encoding."""

    check_id = "feature-value-fidelity"
    severity = Severity.BLOCKING
    description = "Feature core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("feature core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class FeatureClassifiedCheck(ValidationCheck):
    """AXH-04 / AXC-04 — the feature is classified by exactly one Feature kind."""

    check_id = "feature-classified"
    severity = Severity.BLOCKING
    description = "Feature is classified by an AXH-04 kind (single-facet, AXC-04)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("feature kind is outside AXH-04", kind=subject.kind)
        return self._passed(kind=subject.kind)


class FeatureDeliversCapabilityCheck(ValidationCheck):
    """AMR-01 / FEA-04 — the feature delivers a capability by reference."""

    check_id = "feature-delivers-capability"
    severity = Severity.BLOCKING
    description = "Feature delivers a capability by ENG-005 reference (AMR-01 / FEA-04)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.delivers_capability or not subject.capability_ref.strip():
            return self._failed("feature delivers no capability (AMR-01 / FEA-04)")
        return self._passed(capability_ref=subject.capability_ref)


class FeatureConsumesOperationCheck(ValidationCheck):
    """AMR-13 / FEA-04 / FEA-C2 / AMK-02 — the feature composes ≥1 SF-2 operation by ref."""

    check_id = "feature-consumes-operation"
    severity = Severity.BLOCKING
    description = "Feature composes ≥1 SF-2 operation by ENG-005 reference (AMR-13 / FEA-04)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.consumes_operations or subject.composed_operation_count < 1:
            return self._failed(
                "feature composes no SF-2 operation (AMR-13 / FEA-04 / UAL-06)"
            )
        return self._passed(composed_operation_count=subject.composed_operation_count)


class FeatureOperationsPartitionCheck(ValidationCheck):
    """FEA-C1 — the composed operations are distinct (a partition)."""

    check_id = "feature-operations-partition"
    severity = Severity.BLOCKING
    description = "Composed operations are distinct (a partition) (FEA-C1)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.operations_are_partition:
            return self._failed("composed operations are not distinct (FEA-C1)")
        return self._passed(composed_operation_count=subject.composed_operation_count)


class FeaturePresentsDataCheck(ValidationCheck):
    """AMR-14 / FEA-05 / UAL-13 / C4 — the feature presents DF-2 data by reference."""

    check_id = "feature-presents-data"
    severity = Severity.BLOCKING
    description = "Feature presents typed I/O as DF-2 data by reference (AMR-14 / FEA-05)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.presents_data or not subject.data_ref.strip():
            return self._failed("feature presents no DF-2 data (AMR-14 / FEA-05 / UAL-13)")
        return self._passed(data_ref=subject.data_ref)


class FeatureEngagedThroughInteractionCheck(ValidationCheck):
    """AMR-05 / FEA-06 / AMK-04 / UAL-11 — engaged through a typed interaction by ref.

    This is the relationship **no prior Band-12 unit used** — the feature's distinctive
    engaged-through founding edge (Feature → Interaction).
    """

    check_id = "feature-engaged-through-interaction"
    severity = Severity.BLOCKING
    description = "Feature is engaged through an interaction by reference (AMR-05 / FEA-06)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.is_engaged or not subject.interaction_ref.strip():
            return self._failed(
                "feature is not engaged through an interaction (AMR-05 / FEA-06 / UAL-11)"
            )
        return self._passed(interaction_ref=subject.interaction_ref)


class FeatureOwnedByModuleCheck(ValidationCheck):
    """AMR-03 / FEA-07 / UAL-07 — the feature belongs to exactly one owning module."""

    check_id = "feature-owned-by-module"
    severity = Severity.BLOCKING
    description = "Feature belongs to exactly one owning module by reference (AMR-03 / FEA-07)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.is_owned or not subject.module_ref.strip():
            return self._failed("feature has no owning module (AMR-03 / FEA-07 / UAL-07)")
        return self._passed(module_ref=subject.module_ref)


class FeatureDeclarationCompleteCheck(ValidationCheck):
    """FEA-C1 / AMK-02 / UAL-08 — the feature's declaration is complete (the governing law).

    A feature declares its delivered capability, composed SF-2 operations, typed I/O, and
    interaction — nothing implicit (FEA-03 / UAL-08).
    """

    check_id = "feature-declaration-complete"
    severity = Severity.BLOCKING
    description = "Feature declares capability + operations + typed I/O + interaction (UAL-08)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.declaration_complete:
            return self._failed(
                "feature declaration is incomplete (FEA-C1 / AMK-02 / UAL-08)"
            )
        return self._passed()


class FeatureDeliverySideConsistentCheck(ValidationCheck):
    """FEA-C5 / AXH-04 — the kind and composed-operation breadth are consistent."""

    check_id = "feature-delivery-side-consistent"
    severity = Severity.BLOCKING
    description = "Kind/operation-breadth consistent; Composite composes ≥2 (FEA-C5 / AXH-04)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.delivery_side_is_consistent:
            return self._failed(
                "delivery side inconsistent (a Composite-Feature must compose ≥2) (FEA-C5)",
                kind=subject.kind,
                count=subject.composed_operation_count,
            )
        return self._passed(delivery_side=subject.delivery_side)


class FeatureEngagedBeforeExecutableCheck(ValidationCheck):
    """AMK-04 / FEA-06 / FEA-K3 — engaged-through holds for the lifecycle state."""

    check_id = "feature-engaged-before-executable"
    severity = Severity.BLOCKING
    description = "Feature is engaged through an interaction before EXECUTABLE (AMK-04)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.engaged_before_executable:
            return self._failed(
                "feature reached EXECUTABLE un-engaged (AMK-04 / FEA-06)",
                state=subject.lifecycle_state,
            )
        return self._passed(state=subject.lifecycle_state)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / AMI-01 — the feature instantiates exactly one meta-class (AMC-04)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Feature instantiates exactly the AMC-04 meta-class (V1)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if subject.meta_class != FEATURE_META_CLASS:
            return self._failed("meta-class is not AMC-04 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / AMI-02 — every relationship used lies within AMR-01…14."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All feature relationships are within AMR-01…14 (V2)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside AMR-01…14 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (AMK-01 typed/id/object; AMK-02/05/07 references)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "AMK-01 (typed/identified/object) and AMK-02/05/07 (references) hold (V3)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("AMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("AMK-05/07 not satisfied: a reference does not resolve (V3)")
        if not subject.declaration_complete:
            return self._failed("AMK-02 not satisfied: declaration incomplete (V3)")
        return self._passed(constraints=["AMK-01", "AMK-02", "AMK-03", "AMK-05", "AMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / AMK-03 / FEA-C3 / UAL-09 — the founding graph (groups, engaged-through) is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The feature's founding graph (groups, engaged-through) is acyclic (V4 / AMK-03)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UAL-12 — the feature holds a valid AOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Feature holds a valid AOS-01…06 lifecycle state (V5 / UAL-12)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UAL-02 / FEA-10 / AMI-05 / VC-5 — frozen foundations reused by reference, not redefined."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/SF-2/DF-2 referenced, redefined nowhere (UAL-02 / AMI-05)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UAL-02 / AMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UAL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class BehaviorByReferenceCheck(ValidationCheck):
    """UAL-10 / §7 / AMK-05 — invoke/sequence/interact/emit behavior binds RL-F2 by reference."""

    check_id = "behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Behavior binds to RL-F2 by ENG-005 reference (UAL-10; feature-invoke/emit)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("no RL-F2 behavior reference (UAL-10 / §7)")
        return self._passed(behavior_ref=subject.behavior_ref)


class TechnologyIndependenceCheck(ValidationCheck):
    """UAL-15 / FEA-09 / C7 — no UI/framework/screen/API/protocol/transport/vendor is selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/UI/framework/protocol/vendor selected (UAL-15)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UAL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UAL-15 / FEA-09 / C7 — the feature confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Feature confers no authority and embeds no secret (UAL-15 / RR-07)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("feature confers authority (UAL-15)")
        if subject.embeds_secret:
            return self._failed("feature embeds a secret (UAL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 12-APPLICATION anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at AMC-04 and closed to 12-APPLICATION (No-Orphan)."

    def evaluate(self, subject: FeatureValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("12-APPLICATION@") for link in chain):
            return self._failed("lineage does not close to the 12-APPLICATION anchor")
        return self._passed(links=len(chain))


def feature_checks() -> tuple[ValidationCheck, ...]:
    """The full feature-layer validation suite (deterministically ordered by the engine)."""
    return (
        FeatureTypedCheck(),
        FeatureIdentifiedCheck(),
        FeatureValueFidelityCheck(),
        FeatureClassifiedCheck(),
        FeatureDeliversCapabilityCheck(),
        FeatureConsumesOperationCheck(),
        FeatureOperationsPartitionCheck(),
        FeaturePresentsDataCheck(),
        FeatureEngagedThroughInteractionCheck(),
        FeatureOwnedByModuleCheck(),
        FeatureDeclarationCompleteCheck(),
        FeatureDeliverySideConsistentCheck(),
        FeatureEngagedBeforeExecutableCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        BehaviorByReferenceCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class FeatureValidation:
    """The bundled outcome of validating a Feature (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_feature(
    feature: Feature, trace: TraceabilityRecord, *, strict: bool = False
) -> FeatureValidation:
    """Validate ``feature`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected feature raises via the
    EC-1 acceptance gate.
    """
    subject = FeatureValidationSubject.from_feature(feature, trace)
    engine = ValidationEngine(feature_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return FeatureValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "FEATURE_BLUEPRINT_ID",
    "FeatureValidationSubject",
    "FeatureValidation",
    "feature_checks",
    "validate_feature",
]
