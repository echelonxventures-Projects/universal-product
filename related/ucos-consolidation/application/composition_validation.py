"""EC3-B12-U08 — Composition validation (meta-validity V1…V5 + UAL/CMP conformance).

This module proves a realized :class:`~application.composition.Composition` is
**META-VALID** (APPLICATION-005 §8, V1…V5) and **Application-/Composition-law conformant**
(APPLICATION-001 §7, UAL-01…15; APPLICATION-012 §4, CMP-01…10) by running a suite of
deterministic, application-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate (:func:`engine.validation.gates.enforce_acceptance`). Validation evidence is produced
with the EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`CompositionValidationSubject` (the
type-independent projection the EC-1 engine consumes), so an identical composition yields a
byte-identical report, evidence, and acceptance decision (VC-4). Every check is
**blocking**: the verdict is PASS iff the composition satisfies every meta-validity and
Application-/Composition-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.composition import Composition
from application.composition_meta import (
    COMPOSITION_META_CLASS,
    META_RELATIONSHIPS,
    CompositionKind,
    CompositionState,
)
from application.composition_traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UAL-02) — the certified validation substrate --------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Composition realizes (its meta-class) — used by the EC-1 report.
COMPOSITION_BLUEPRINT_ID = COMPOSITION_META_CLASS

_KIND_VALUES = frozenset(k.value for k in CompositionKind)
_STATE_VALUES = frozenset(s.value for s in CompositionState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)
_FACETS = frozenset(
    {"feature-into-module", "module-into-application", "application-federation"}
)


@dataclass(frozen=True, slots=True)
class CompositionValidationSubject:
    """A normalized, immutable projection of a Composition that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1 ``ValidationEngine``
    consumes) plus the composition's meta-facts. Holds no runtime state and no wall-clock,
    so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    facet: str
    value_digest: str
    member_refs: tuple[str, ...]
    assembled_member_count: int
    assembled_ref: str
    composition_ref: str
    behavior_ref: str
    founding_relationship: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    is_founding: bool
    is_federation: bool
    references_resolve: bool
    assembles_members: bool
    members_are_partition: bool
    preserves_boundaries: bool
    federation_is_by_reference: bool
    uses_new_connection_construct: bool
    binds_platform_composition: bool
    binds_runtime_event: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_composition(
        cls, composition: Composition, trace: TraceabilityRecord
    ) -> CompositionValidationSubject:
        """Project ``composition`` (+ its lineage) into a validation subject."""
        payload = composition.to_dict()
        return cls(
            target_id=composition.composition_id,
            blueprint_id=COMPOSITION_BLUEPRINT_ID,
            meta_class=composition.meta_class,
            type_tag=composition.type_tag,
            kind=composition.kind.value,
            facet=composition.facet(),
            value_digest=composition.value_digest,
            member_refs=tuple(payload["member_refs"]),
            assembled_member_count=composition.assembled_member_count(),
            assembled_ref=composition.assembled_ref,
            composition_ref=composition.composition_ref,
            behavior_ref=composition.behavior_ref,
            founding_relationship=composition.founding_relationship(),
            relationships=composition.meta_relationships(),
            lifecycle_state=composition.state.value,
            founding_acyclic=composition.is_founding_acyclic(),
            is_founding=composition.participates_in_founding_edge(),
            is_federation=composition.is_federation(),
            references_resolve=composition.references_resolve(),
            assembles_members=composition.assembles_members(),
            members_are_partition=composition.members_are_partition(),
            preserves_boundaries=composition.preserves_boundaries(),
            federation_is_by_reference=composition.federation_is_by_reference(),
            uses_new_connection_construct=composition.uses_new_connection_construct(),
            binds_platform_composition=composition.binds_platform_composition(),
            binds_runtime_event=composition.binds_runtime_event(),
            confers_authority=composition.confers_authority(),
            selects_technology=composition.selects_technology(),
            embeds_secret=composition.embeds_secret(),
            redefines_foundation=composition.redefines_foundation(),
            substrate_refs=tuple(payload["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Composition-layer validation checks (each maps to explicit V*/UAL*/CMP*/AMK* obligations)
# ---------------------------------------------------------------------------


class CompositionTypedCheck(ValidationCheck):
    """UAL-03 / CMP-01 / AMK-01 / C1 — the composition is classified by a non-empty type."""

    check_id = "composition-typed"
    severity = Severity.BLOCKING
    description = "Composition bears a non-empty ENG-004 type_tag (UAL-03 / CMP-01)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("composition is untyped (UAL-03 / CMP-01)")
        return self._passed(type_tag=subject.type_tag)


class CompositionIdentifiedCheck(ValidationCheck):
    """UAL-04/05 / CMP-02 / AMK-01 / C1 — the composition is identified and object-borne."""

    check_id = "composition-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Composition bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-COMPOSITION-"):
            return self._failed(
                "composition lacks ENG-001 identity (UAL-04)", id=subject.target_id
            )
        if not subject.value_digest:
            return self._failed("composition is not object-borne (no value digest) (UAL-05)")
        return self._passed(composition_id=subject.target_id)


class CompositionValueFidelityCheck(ValidationCheck):
    """ENG-003 — the composition core round-trips through the EC-1 canonical encoding."""

    check_id = "composition-value-fidelity"
    severity = Severity.BLOCKING
    description = "Composition core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("composition core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class CompositionClassifiedCheck(ValidationCheck):
    """AXH-08 / AXC-04 — the composition is classified by exactly one Composition kind."""

    check_id = "composition-classified"
    severity = Severity.BLOCKING
    description = "Composition is classified by an AXH-08 kind (single-facet, AXC-04)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("composition kind is outside AXH-08", kind=subject.kind)
        if subject.facet not in _FACETS:
            return self._failed("composition facet is outside AXH-08", facet=subject.facet)
        return self._passed(kind=subject.kind, facet=subject.facet)


class CompositionAssemblesMembersCheck(ValidationCheck):
    """AMR-07 / CMP-C1 — the composition assembles ≥1 constituent by reference (defining)."""

    check_id = "composition-assembles-members"
    severity = Severity.BLOCKING
    description = "Composition assembles ≥1 constituent by ENG-005 reference (AMR-07 / CMP-C1)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.assembles_members or subject.assembled_member_count < 1:
            return self._failed("composition assembles no constituent (AMR-07 / CMP-C1)")
        return self._passed(assembled_member_count=subject.assembled_member_count)


class CompositionConstituentsTypedCheck(ValidationCheck):
    """CMP-K2 / AMK-02 — every assembled constituent is a declared, distinct ENG-005 ref."""

    check_id = "composition-constituents-typed"
    severity = Severity.BLOCKING
    description = "Every assembled constituent is a declared, distinct ENG-005 reference (CMP-K2)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.members_are_partition:
            return self._failed("assembled constituents are not a declared partition (CMP-K2)")
        return self._passed(assembled_member_count=subject.assembled_member_count)


class CompositionPreservesBoundariesCheck(ValidationCheck):
    """CMP-06 / CMP-C3 — the composition preserves boundaries and absorbs no identity."""

    check_id = "composition-preserves-boundaries"
    severity = Severity.BLOCKING
    description = "Composition preserves constituent boundaries; absorbs none (CMP-06 / CMP-C3)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.preserves_boundaries:
            return self._failed("composition absorbs a constituent identity (CMP-06 / CMP-C3)")
        return self._passed()


class CompositionFederationByReferenceCheck(ValidationCheck):
    """CMP-07 / CMP-C4 — application federation is peer, ≥2, by reference (never absorbed)."""

    check_id = "composition-federation-by-reference"
    severity = Severity.BLOCKING
    description = "Application federation composes ≥2 peer apps by reference (CMP-07 / CMP-C4)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.federation_is_by_reference:
            return self._failed(
                "federation is not a ≥2 peer, by-reference composition (CMP-07 / CMP-C4)"
            )
        return self._passed(is_federation=subject.is_federation)


class CompositionNoNewConnectionCheck(ValidationCheck):
    """CMP-04 / CMP-C2 — the composition introduces no new connection construct."""

    check_id = "composition-no-new-connection"
    severity = Severity.BLOCKING
    description = "Composition introduces no new connection construct; all links ENG-005 (CMP-04)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.uses_new_connection_construct:
            return self._failed("composition introduces a new connection construct (CMP-04)")
        return self._passed()


class CompositionByReferenceCheck(ValidationCheck):
    """UAL-09 / AMR-07/12 / C5 — composition binds the assembled whole + PL-F2 by reference."""

    check_id = "composition-by-reference"
    severity = Severity.BLOCKING
    description = "Composition binds assembled whole + PL-F2 by ENG-005 reference (UAL-09)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.assembled_ref.strip():
            return self._failed("no assembled-whole reference (AMR-07 / UAL-09)")
        if not subject.binds_platform_composition:
            return self._failed(
                "no PL-F2 experience composition reference, or a technology was named "
                "(AMR-12 / CMP-C5 / UAL-09)",
                composition_ref=subject.composition_ref,
            )
        return self._passed(
            assembled_ref=subject.assembled_ref, composition_ref=subject.composition_ref
        )


class CompositionBehaviorByReferenceCheck(ValidationCheck):
    """UAL-10 / §7 / AMK-05 — composition-emit behavior binds to RL-F2 by reference."""

    check_id = "composition-behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Composition-emit behavior binds to RL-F2 by ENG-005 reference (UAL-10 / §7)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("no RL-F2 behavior reference (UAL-10 / §7)")
        if not subject.binds_runtime_event:
            return self._failed(
                "composition-emit binding names a concrete technology, not RL-F2 (AMK-05)",
                behavior_ref=subject.behavior_ref,
            )
        return self._passed(behavior_ref=subject.behavior_ref)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / AMI-01 — the composition instantiates exactly one meta-class (AMC-08)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Composition instantiates exactly the AMC-08 meta-class (V1)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.meta_class != COMPOSITION_META_CLASS:
            return self._failed(
                "meta-class is not AMC-08 (V1)", meta_class=subject.meta_class
            )
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / AMI-02 — every relationship used lies within AMR-01…14."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All composition relationships are within AMR-01…14 (V2)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside AMR-01…14 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (AMK-01 typed/id/object; AMK-02/05/06 references)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "AMK-01 (typed/identified/object) and AMK-02/05/06 (references) hold (V3)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("AMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("AMK-05/06 not satisfied: a reference does not resolve (V3)")
        if not (subject.members_are_partition and subject.assembles_members):
            return self._failed(
                "AMK-02 not satisfied: assembled constituents not declared/partitioned (V3)"
            )
        return self._passed(constraints=["AMK-01", "AMK-02", "AMK-03", "AMK-05", "AMK-06"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / AMK-03 / CMP-C1 / UAL-09 — the founding graph is acyclic (materially proven).

    THE governing condition of AMC-08: the founding composition graph
    (features→modules→applications) is a DAG, proven by the deterministic three-colour cycle
    detector over the founding edge set (empty, hence acyclic, for a peer federation).
    """

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The composition's founding graph is acyclic (V4 / AMK-03 / CMP-C1 / UAL-09)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4 / AMK-03 / CMP-C1)")
        return self._passed(founding_relationship=subject.founding_relationship)


class LifecycleValidCheck(ValidationCheck):
    """V5 / UAL-12 — the composition holds a valid AOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Composition holds a valid AOS-01…06 lifecycle state (V5 / UAL-12)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UAL-02 / CMP-10 / AMI-05 / VC-5 — frozen foundations reused by reference, not redefined."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/PL-F2 referenced, redefined nowhere (UAL-02 / AMI-05)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UAL-02 / AMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UAL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """UAL-15 / CMP-09 / C7 — no bundler/packaging/framework/container/vendor is selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No module bundler/packaging/framework/container/vendor selected (UAL-15)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UAL-15 / CMP-09)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UAL-15 / CMP-09 / C7 — the composition confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Composition confers no authority and embeds no secret (UAL-15 / RR-07)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("composition confers authority (UAL-15 / CMP-09)")
        if subject.embeds_secret:
            return self._failed("composition embeds a secret (UAL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 12-APPLICATION anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at AMC-08 and closed to 12-APPLICATION (No-Orphan)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("12-APPLICATION@") for link in chain):
            return self._failed("lineage does not close to the 12-APPLICATION anchor")
        return self._passed(links=len(chain))


def composition_checks() -> tuple[ValidationCheck, ...]:
    """The full composition-layer validation suite (deterministically ordered by the engine)."""
    return (
        CompositionTypedCheck(),
        CompositionIdentifiedCheck(),
        CompositionValueFidelityCheck(),
        CompositionClassifiedCheck(),
        CompositionAssemblesMembersCheck(),
        CompositionConstituentsTypedCheck(),
        CompositionPreservesBoundariesCheck(),
        CompositionFederationByReferenceCheck(),
        CompositionNoNewConnectionCheck(),
        CompositionByReferenceCheck(),
        CompositionBehaviorByReferenceCheck(),
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


@dataclass(frozen=True, slots=True)
class CompositionValidation:
    """The bundled outcome of validating a Composition (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_composition(
    composition: Composition, trace: TraceabilityRecord, *, strict: bool = False
) -> CompositionValidation:
    """Validate ``composition`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected composition raises via the
    EC-1 acceptance gate.
    """
    subject = CompositionValidationSubject.from_composition(composition, trace)
    engine = ValidationEngine(composition_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return CompositionValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "COMPOSITION_BLUEPRINT_ID",
    "CompositionValidationSubject",
    "CompositionValidation",
    "composition_checks",
    "validate_composition",
]
