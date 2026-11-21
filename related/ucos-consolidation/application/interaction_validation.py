"""EC3-B12-U06 — Interaction validation (meta-validity V1…V5 + UAL/INT conformance).

This module proves a realized :class:`~application.interaction.Interaction` is
**META-VALID** (APPLICATION-005 §8, V1…V5) and **Application-/Interaction-law conformant**
(APPLICATION-001 §7, UAL-01…15; APPLICATION-010 §4, INT-01…10) by running a suite of
deterministic, application-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate (:func:`engine.validation.gates.enforce_acceptance`). Validation evidence is produced
with the EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`InteractionValidationSubject`
(the type-independent projection the EC-1 engine consumes), so an identical interaction
yields a byte-identical report, evidence, and acceptance decision (VC-4). Every check is
**blocking**: the verdict is PASS iff the interaction satisfies every meta-validity and
Application-/Interaction-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.interaction import Interaction
from application.interaction_meta import (
    INTERACTION_META_CLASS,
    META_RELATIONSHIPS,
    InteractionKind,
    InteractionState,
)
from application.interaction_traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UAL-02) — the certified validation substrate --------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id an Interaction realizes (its meta-class) — used by the EC-1 report.
INTERACTION_BLUEPRINT_ID = INTERACTION_META_CLASS

_KIND_VALUES = frozenset(k.value for k in InteractionKind)
_STATE_VALUES = frozenset(s.value for s in InteractionState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)
_DIRECTIONS = frozenset({"input", "command", "query", "response"})


@dataclass(frozen=True, slots=True)
class InteractionValidationSubject:
    """A normalized, immutable projection of an Interaction that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1 ``ValidationEngine``
    consumes) plus the interaction's meta-facts. Holds no runtime state and no wall-clock,
    so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    direction: str
    value_digest: str
    feature_ref: str
    surface_ref: str
    data_ref: str
    state_ref: str
    behavior_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    references_resolve: bool
    direction_is_decidable: bool
    engages_feature: bool
    presents_data: bool
    holds_state: bool
    surface_is_abstract: bool
    sole_engagement_point: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_interaction(
        cls, interaction: Interaction, trace: TraceabilityRecord
    ) -> InteractionValidationSubject:
        """Project ``interaction`` (+ its lineage) into a validation subject."""
        payload = interaction.to_dict()
        return cls(
            target_id=interaction.interaction_id,
            blueprint_id=INTERACTION_BLUEPRINT_ID,
            meta_class=interaction.meta_class,
            type_tag=interaction.type_tag,
            kind=interaction.kind.value,
            direction=interaction.direction(),
            value_digest=interaction.value_digest,
            feature_ref=interaction.feature_ref,
            surface_ref=interaction.surface_ref,
            data_ref=interaction.data_ref,
            state_ref=interaction.state_ref,
            behavior_ref=interaction.behavior_ref,
            relationships=interaction.meta_relationships(),
            lifecycle_state=interaction.state.value,
            founding_acyclic=interaction.is_founding_acyclic(),
            references_resolve=interaction.references_resolve(),
            direction_is_decidable=interaction.direction_is_decidable(),
            engages_feature=interaction.engages_feature(),
            presents_data=interaction.presents_data(),
            holds_state=interaction.holds_state(),
            surface_is_abstract=interaction.surface_is_abstract(),
            sole_engagement_point=interaction.is_sole_engagement_point(),
            confers_authority=interaction.confers_authority(),
            selects_technology=interaction.selects_technology(),
            embeds_secret=interaction.embeds_secret(),
            redefines_foundation=interaction.redefines_foundation(),
            substrate_refs=tuple(payload["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Interaction-layer validation checks (each maps to explicit V*/UAL*/INT*/AMK* obligations)
# ---------------------------------------------------------------------------


class InteractionTypedCheck(ValidationCheck):
    """UAL-03/11 / INT-01 / AMK-01 / C1 — the interaction is classified by a non-empty type."""

    check_id = "interaction-typed"
    severity = Severity.BLOCKING
    description = "Interaction bears a non-empty ENG-004 type_tag (UAL-03/11 / INT-01)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("interaction is untyped (UAL-03/11)")
        return self._passed(type_tag=subject.type_tag)


class InteractionIdentifiedCheck(ValidationCheck):
    """UAL-04/05 / INT-02 / AMK-01 / C1 — the interaction is identified and object-borne."""

    check_id = "interaction-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Interaction bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-INTERACTION-"):
            return self._failed(
                "interaction lacks ENG-001 identity (UAL-04)", id=subject.target_id
            )
        if not subject.value_digest:
            return self._failed("interaction is not object-borne (no value digest) (UAL-05)")
        return self._passed(interaction_id=subject.target_id)


class InteractionValueFidelityCheck(ValidationCheck):
    """ENG-003 — the interaction core round-trips through the EC-1 canonical encoding."""

    check_id = "interaction-value-fidelity"
    severity = Severity.BLOCKING
    description = "Interaction core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("interaction core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class InteractionClassifiedCheck(ValidationCheck):
    """AXH-06 / AXC-04 — the interaction is classified by exactly one Interaction kind."""

    check_id = "interaction-classified"
    severity = Severity.BLOCKING
    description = "Interaction is classified by an AXH-06 kind (single-facet, AXC-04)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("interaction kind is outside AXH-06", kind=subject.kind)
        return self._passed(kind=subject.kind, direction=subject.direction)


class InteractionDirectionDecidableCheck(ValidationCheck):
    """INT-07 / INT-C5 — the interaction declares a single decidable direction."""

    check_id = "interaction-direction-decidable"
    severity = Severity.BLOCKING
    description = "Interaction declares a decidable direction (input/command/query/response)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not subject.direction_is_decidable or subject.direction not in _DIRECTIONS:
            return self._failed(
                "interaction direction is not decidable (INT-07 / INT-C5)",
                direction=subject.direction,
            )
        return self._passed(direction=subject.direction)


class InteractionEngagesFeatureCheck(ValidationCheck):
    """AMR-05 / INT-04 / INT-C2 — the interaction engages a feature by reference (founding).

    This is the interaction's **founding relationship** (engaged-through, Feature →
    Interaction): a feature is reachable by an actor only through a declared, typed
    interaction — the interaction is that sole engagement point.
    """

    check_id = "interaction-engages-feature"
    severity = Severity.BLOCKING
    description = "Interaction engages a feature by ENG-005 reference (AMR-05 / INT-04)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not subject.engages_feature or not subject.feature_ref.strip():
            return self._failed("interaction engages no feature (AMR-05 / INT-04 / INT-C2)")
        return self._passed(feature_ref=subject.feature_ref)


class InteractionSurfaceAbstractCheck(ValidationCheck):
    """INT-03 / INT-C1 / UAL-11 — the presentation surface is abstract (no technology).

    THE distinctive interaction obligation: presentation (screen) is an abstract surface;
    it names surface/region without selecting a rendering technology, UI framework, or
    design system.
    """

    check_id = "interaction-surface-abstract"
    severity = Severity.BLOCKING
    description = "Presentation surface is abstract; no rendering technology (INT-03 / UAL-11)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not subject.surface_ref.strip():
            return self._failed("interaction has no presentation surface (INT-03 / INT-C1)")
        if not subject.surface_is_abstract:
            return self._failed(
                "presentation surface selects a rendering technology (INT-03 / INT-C1 / UAL-11)",
                surface_ref=subject.surface_ref,
            )
        return self._passed(surface_ref=subject.surface_ref)


class InteractionPresentsDataCheck(ValidationCheck):
    """AMR-14 / INT-06 / INT-C4 / UAL-13 / AMK-07 — presents DF-2 data by reference."""

    check_id = "interaction-presents-data"
    severity = Severity.BLOCKING
    description = "Interaction presents DF-2 exchanged data by ENG-005 reference (AMR-14)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not subject.presents_data or not subject.data_ref.strip():
            return self._failed("interaction presents no DF-2 data (AMR-14 / INT-06 / UAL-13)")
        return self._passed(data_ref=subject.data_ref)


class InteractionHoldsStateCheck(ValidationCheck):
    """AMR-06 / AMK-05 — the interaction holds/advances interaction/session state (→ RL-F2)."""

    check_id = "interaction-holds-state"
    severity = Severity.BLOCKING
    description = "Interaction holds/advances state by reference → RL-F2 (AMR-06)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not subject.holds_state or not subject.state_ref.strip():
            return self._failed("interaction holds no state (AMR-06 / AMK-05)")
        return self._passed(state_ref=subject.state_ref)


class InteractionSoleEngagementCheck(ValidationCheck):
    """INT-04 / INT-C2 — the interaction is a declared, typed, sole engagement point."""

    check_id = "interaction-sole-engagement"
    severity = Severity.BLOCKING
    description = "Interaction is a declared, typed, sole feature-engagement point (INT-04)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not subject.sole_engagement_point:
            return self._failed(
                "interaction is not a well-formed sole engagement point (INT-04 / INT-C2)"
            )
        return self._passed(feature_ref=subject.feature_ref, direction=subject.direction)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / AMI-01 — the interaction instantiates exactly one meta-class (AMC-06)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Interaction instantiates exactly the AMC-06 meta-class (V1)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if subject.meta_class != INTERACTION_META_CLASS:
            return self._failed("meta-class is not AMC-06 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / AMI-02 — every relationship used lies within AMR-01…14."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All interaction relationships are within AMR-01…14 (V2)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside AMR-01…14 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (AMK-01 typed/id/object; AMK-02/05/07 references)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "AMK-01 (typed/identified/object) and AMK-02/05/07 (references) hold (V3)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("AMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("AMK-05/07 not satisfied: a reference does not resolve (V3)")
        if not (
            subject.direction_is_decidable
            and subject.engages_feature
            and subject.presents_data
        ):
            return self._failed(
                "AMK-02 not satisfied: direction/feature/data declaration incomplete (V3)"
            )
        return self._passed(constraints=["AMK-01", "AMK-02", "AMK-03", "AMK-05", "AMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / AMK-03 / INT-C3 — the founding graph is acyclic (engaged-through DAG).

    The interaction is the *target* of the founding engaged-through edge (AMR-05); the
    engaged feature is distinct from every binding reference (no self-founding), so the
    founding structure carries no cycle. Materially exercised (unlike the Workflow, which
    used no founding edge).
    """

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The interaction's founding (engaged-through) graph is acyclic (V4 / AMK-03)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4 / INT-C3)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UAL-12 — the interaction holds a valid AOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Interaction holds a valid AOS-01…06 lifecycle state (V5 / UAL-12)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UAL-02 / INT-10 / AMI-05 / VC-5 — frozen foundations reused by reference, not redefined."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/DF-2 referenced, redefined nowhere (UAL-02 / AMI-05)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UAL-02 / AMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UAL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class BehaviorByReferenceCheck(ValidationCheck):
    """UAL-10 / §7 / AMK-05 / INT-05 — exchange/transition/emit binds RL-F2 by reference."""

    check_id = "behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Behavior binds RL-F2 event/state by reference (UAL-10 / §7 / INT-05)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("no RL-F2 behavior reference (UAL-10 / §7 / INT-05)")
        return self._passed(behavior_ref=subject.behavior_ref)


class TechnologyIndependenceCheck(ValidationCheck):
    """UAL-11/15 / INT-09 / C7 — no rendering tech / UI framework / engine / vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No rendering technology/UI framework/engine/vendor selected (UAL-11/15)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UAL-11/15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UAL-15 / INT-09 / C7 — the interaction confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Interaction confers no authority and embeds no secret (UAL-15 / RR-07)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("interaction confers authority (UAL-15)")
        if subject.embeds_secret:
            return self._failed("interaction embeds a secret (UAL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 12-APPLICATION anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at AMC-06 and closed to 12-APPLICATION (No-Orphan)."

    def evaluate(self, subject: InteractionValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("12-APPLICATION@") for link in chain):
            return self._failed("lineage does not close to the 12-APPLICATION anchor")
        return self._passed(links=len(chain))


def interaction_checks() -> tuple[ValidationCheck, ...]:
    """The full interaction-layer validation suite (deterministically ordered by the engine)."""
    return (
        InteractionTypedCheck(),
        InteractionIdentifiedCheck(),
        InteractionValueFidelityCheck(),
        InteractionClassifiedCheck(),
        InteractionDirectionDecidableCheck(),
        InteractionEngagesFeatureCheck(),
        InteractionSurfaceAbstractCheck(),
        InteractionPresentsDataCheck(),
        InteractionHoldsStateCheck(),
        InteractionSoleEngagementCheck(),
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
class InteractionValidation:
    """The bundled outcome of validating an Interaction (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_interaction(
    interaction: Interaction, trace: TraceabilityRecord, *, strict: bool = False
) -> InteractionValidation:
    """Validate ``interaction`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected interaction raises via the
    EC-1 acceptance gate.
    """
    subject = InteractionValidationSubject.from_interaction(interaction, trace)
    engine = ValidationEngine(interaction_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return InteractionValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "INTERACTION_BLUEPRINT_ID",
    "InteractionValidationSubject",
    "InteractionValidation",
    "interaction_checks",
    "validate_interaction",
]
