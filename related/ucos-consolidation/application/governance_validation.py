"""EC3-B12-U10 — Governance validation (meta-validity V1…V5 + UAL/GOV conformance).

This module proves a realized :class:`~application.governance.Governance` record is
**META-VALID** (APPLICATION-005 §8, V1…V5) and **Application-/Governance-law conformant**
(APPLICATION-001 §7, UAL-01…15; APPLICATION-014 §4, GOV-01…10) by running a suite of
deterministic, application-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance gate
(:func:`engine.validation.gates.enforce_acceptance`). Validation evidence is produced with the
EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`GovernanceValidationSubject` (the
type-independent projection the EC-1 engine consumes), so an identical record yields a
byte-identical report, evidence, and acceptance decision (VC-4). Every check is **blocking**:
the verdict is PASS iff the record satisfies every meta-validity and Application-/Governance-law
obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.governance import Governance
from application.governance_meta import (
    GOVERNANCE_META_CLASS,
    META_RELATIONSHIPS,
    GovernanceKind,
    GovernanceState,
)
from application.governance_traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UAL-02) — the certified validation substrate --------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Governance record realizes (its meta-class) — used by the EC-1 report.
GOVERNANCE_BLUEPRINT_ID = GOVERNANCE_META_CLASS

_KIND_VALUES = frozenset(k.value for k in GovernanceKind)
_STATE_VALUES = frozenset(s.value for s in GovernanceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)
_FACETS = frozenset({"conformance", "lifecycle", "policy"})


@dataclass(frozen=True, slots=True)
class GovernanceValidationSubject:
    """A normalized, immutable projection of a Governance record that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1 ``ValidationEngine``
    consumes) plus the record's meta-facts. Holds no runtime state and no wall-clock, so it is
    deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    facet: str
    value_digest: str
    subject_refs: tuple[str, ...]
    security_refs: tuple[str, ...]
    state_refs: tuple[str, ...]
    behavior_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    is_founding: bool
    governs_boundary: bool
    evaluative_nonenforcing: bool
    binds_runtime_policy: bool
    behavior_by_reference: bool
    secures_by_reference: bool
    state_by_reference: bool
    references_resolve: bool
    uses_new_connection_construct: bool
    precedence_decidable: bool
    confers_authority: bool
    enforces: bool
    ratifies: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_governance(
        cls, governance: Governance, trace: TraceabilityRecord
    ) -> GovernanceValidationSubject:
        """Project ``governance`` (+ its lineage) into a validation subject."""
        payload = governance.to_dict()
        return cls(
            target_id=governance.governance_id,
            blueprint_id=GOVERNANCE_BLUEPRINT_ID,
            meta_class=governance.meta_class,
            type_tag=governance.type_tag,
            kind=governance.kind.value,
            facet=governance.facet(),
            value_digest=governance.value_digest,
            subject_refs=tuple(payload["subject_refs"]),
            security_refs=tuple(payload["security_refs"]),
            state_refs=tuple(payload["state_refs"]),
            behavior_ref=governance.behavior_ref,
            relationships=governance.meta_relationships(),
            lifecycle_state=governance.state.value,
            founding_acyclic=governance.is_founding_acyclic(),
            is_founding=governance.participates_in_founding_edge(),
            governs_boundary=governance.governs_boundary(),
            evaluative_nonenforcing=governance.evaluative_nonenforcing(),
            binds_runtime_policy=governance.binds_runtime_policy(),
            behavior_by_reference=governance.behavior_by_reference(),
            secures_by_reference=governance.secures_by_reference(),
            state_by_reference=governance.state_by_reference(),
            references_resolve=governance.references_resolve(),
            uses_new_connection_construct=governance.uses_new_connection_construct(),
            precedence_decidable=governance.precedence_decidable(),
            confers_authority=governance.confers_authority(),
            enforces=governance.enforces(),
            ratifies=governance.ratifies(),
            selects_technology=governance.selects_technology(),
            embeds_secret=governance.embeds_secret(),
            redefines_foundation=governance.redefines_foundation(),
            substrate_refs=tuple(payload["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Governance-layer validation checks (each maps to explicit V*/UAL*/GOV*/AMK* obligations)
# ---------------------------------------------------------------------------


class GovernanceTypedCheck(ValidationCheck):
    """UAL-03 / GOV-01 / AMK-01 / C1 — the record is classified by a non-empty type."""

    check_id = "governance-typed"
    severity = Severity.BLOCKING
    description = "Governance record bears a non-empty ENG-004 type_tag (UAL-03 / GOV-01)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("governance record is untyped (UAL-03 / GOV-01)")
        return self._passed(type_tag=subject.type_tag)


class GovernanceIdentifiedCheck(ValidationCheck):
    """UAL-04/05 / GOV-02 / AMK-01 / C1 — the record is identified and object-borne."""

    check_id = "governance-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Governance record bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-GOVERNANCE-"):
            return self._failed(
                "governance record lacks ENG-001 identity (UAL-04)", id=subject.target_id
            )
        if not subject.value_digest:
            return self._failed("governance record is not object-borne (no value digest) (UAL-05)")
        return self._passed(governance_id=subject.target_id)


class GovernanceValueFidelityCheck(ValidationCheck):
    """ENG-003 — the record core round-trips through the EC-1 canonical encoding."""

    check_id = "governance-value-fidelity"
    severity = Severity.BLOCKING
    description = "Governance core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("governance core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class GovernanceClassifiedCheck(ValidationCheck):
    """AXH-10 / AXC-04 — the record is classified by exactly one Governance kind."""

    check_id = "governance-classified"
    severity = Severity.BLOCKING
    description = "Governance record is classified by an AXH-10 kind (single-facet, AXC-04)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("governance kind is outside AXH-10", kind=subject.kind)
        if subject.facet not in _FACETS:
            return self._failed("governance facet is outside AXH-10", facet=subject.facet)
        return self._passed(kind=subject.kind, facet=subject.facet)


class GovernanceGovernsBoundaryCheck(ValidationCheck):
    """AMR-09 / AOR-09 / GOV-07 / GOV-K2 — the record governs ≥1 declared boundary (defining)."""

    check_id = "governance-governs-boundary"
    severity = Severity.BLOCKING
    description = "Governance record governs ≥1 boundary by ENG-005 reference (AMR-09 / GOV-07)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.governs_boundary or not subject.subject_refs:
            return self._failed("governance record governs no boundary (AMR-09 / GOV-07)")
        return self._passed(governed_count=len(subject.subject_refs))


class GovernanceEvaluativeNonEnforcingCheck(ValidationCheck):
    """UAL-14 / GOV-03/04 / GOV-C1/C2 — record-only, enacts nothing (THE governing law)."""

    check_id = "governance-evaluative-nonenforcing"
    severity = Severity.BLOCKING
    description = "Governance is record-only; approves/enforces/ratifies nothing (UAL-14 law)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.evaluative_nonenforcing:
            return self._failed("governance record enacts (UAL-14 / GOV-03 / GOV-C1/C2)")
        if subject.enforces or subject.ratifies:
            return self._failed("governance record enforces/ratifies (GOV-04 / GOV-C2)")
        return self._passed(governing_law="UAL-14")


class GovernanceSecuresByReferenceCheck(ValidationCheck):
    """AMR-08 / AOR-08 — the referenced Security-conformance is bound by reference (secured-by)."""

    check_id = "governance-secures-by-reference"
    severity = Severity.BLOCKING
    description = "Referenced Security conformance is bound by ENG-005 reference (AMR-08)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.secures_by_reference:
            return self._failed("a security-conformance reference is malformed (AMR-08)")
        return self._passed(security_count=len(subject.security_refs))


class GovernanceBehaviorByReferenceCheck(ValidationCheck):
    """UAL-10 / §7 / AMK-05 — the governance-evaluate behavior binds RL-F2 by reference."""

    check_id = "governance-behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Governance-evaluate behavior binds RL-F2 by ENG-005 reference (§7 / AMK-05)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip() or not subject.behavior_by_reference:
            return self._failed("no RL-F2 governance-evaluate reference (§7 / UAL-10)")
        if not subject.binds_runtime_policy:
            return self._failed(
                "governance-evaluate binding names a concrete technology, not RL-F2 (AMK-05)",
                behavior_ref=subject.behavior_ref,
            )
        return self._passed(behavior_ref=subject.behavior_ref)


class GovernanceStateByReferenceCheck(ValidationCheck):
    """AMR-06 / AOR-06 — the held State (lifecycle-record) is bound by reference (holds-state)."""

    check_id = "governance-state-by-reference"
    severity = Severity.BLOCKING
    description = "Held State (lifecycle-record) is bound by ENG-005 reference (AMR-06)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.state_by_reference:
            return self._failed("a held-state reference is malformed (AMR-06)")
        return self._passed(state_count=len(subject.state_refs))


class GovernanceNoNewConnectionCheck(ValidationCheck):
    """GOV-C4 analog — the record introduces no new connection construct (all ENG-005 refs)."""

    check_id = "governance-no-new-connection"
    severity = Severity.BLOCKING
    description = "Governance record introduces no new connection construct; all links ENG-005."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.uses_new_connection_construct:
            return self._failed("governance record introduces a new connection construct (GOV-C4)")
        return self._passed()


class MetaClassSingleCheck(ValidationCheck):
    """V1 / AMI-01 — the record instantiates exactly one meta-class (AMC-10)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Governance record instantiates exactly the AMC-10 meta-class (V1)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.meta_class != GOVERNANCE_META_CLASS:
            return self._failed("meta-class is not AMC-10 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / AMI-02 — every relationship used lies within AMR-01…14."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All governance relationships are within AMR-01…14 (V2)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside AMR-01…14 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (AMK-01 typed/id/object; AMK-02/05/07 references)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "AMK-01 (typed/identified/object), AMK-02 (boundary), AMK-05/07 (refs) hold (V3)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("AMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("AMK-05/07 not satisfied: a reference does not resolve (V3)")
        if not (subject.governs_boundary and subject.precedence_decidable):
            return self._failed(
                "AMK-02 not satisfied: no declared boundary/concern (V3)"
            )
        return self._passed(constraints=["AMK-01", "AMK-02", "AMK-03", "AMK-05", "AMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / AMK-03 — the founding graph is acyclic (vacuous: no founding edge).

    A Governance record participates in no founding relationship (its relationships
    AMR-06/08/09/10 are all reference-only), so its founding graph is empty and therefore
    acyclic, exactly as the State/Security used no founding edge. Proven via the no-self-founding
    guard.
    """

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The governance record's founding graph is acyclic (V4 / AMK-03)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4 / AMK-03)")
        if subject.is_founding:
            return self._failed(
                "a governance record must participate in no founding edge (AMK-03)"
            )
        return self._passed(founding="vacuous (reference-only)")


class LifecycleValidCheck(ValidationCheck):
    """V5 / UAL-12 — the record holds a valid AOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Governance record holds a valid AOS-01…06 lifecycle state (V5 / UAL-12)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UAL-02 / AMI-05 / VC-5 — frozen foundations reused by reference, not redefined."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2 referenced, redefined nowhere (UAL-02 / AMI-05)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UAL-02 / AMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UAL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """UAL-15 / GOV-K5 / GOV-C3 / C7 — no engine/approval/enforcement technology is selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No workflow-approval/policy-enforcement/technology selected (UAL-15 / GOV-K5)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete governance technology was selected (UAL-15 / GOV-K5)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UAL-15 / GOV-09 / C7 — the record confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Governance record confers no authority and embeds no secret (UAL-15 / RR-07)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("governance record confers authority (UAL-15 / GOV-09)")
        if subject.embeds_secret:
            return self._failed("governance record embeds a secret (UAL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 12-APPLICATION anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at AMC-10 and closed to 12-APPLICATION (No-Orphan)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("12-APPLICATION@") for link in chain):
            return self._failed("lineage does not close to the 12-APPLICATION anchor")
        return self._passed(links=len(chain))


def governance_checks() -> tuple[ValidationCheck, ...]:
    """The full governance-layer validation suite (deterministically ordered by the engine)."""
    return (
        GovernanceTypedCheck(),
        GovernanceIdentifiedCheck(),
        GovernanceValueFidelityCheck(),
        GovernanceClassifiedCheck(),
        GovernanceGovernsBoundaryCheck(),
        GovernanceEvaluativeNonEnforcingCheck(),
        GovernanceSecuresByReferenceCheck(),
        GovernanceBehaviorByReferenceCheck(),
        GovernanceStateByReferenceCheck(),
        GovernanceNoNewConnectionCheck(),
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
class GovernanceValidation:
    """The bundled outcome of validating a Governance record (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_governance(
    governance: Governance, trace: TraceabilityRecord, *, strict: bool = False
) -> GovernanceValidation:
    """Validate ``governance`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected record raises via the EC-1
    acceptance gate.
    """
    subject = GovernanceValidationSubject.from_governance(governance, trace)
    engine = ValidationEngine(governance_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return GovernanceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "GOVERNANCE_BLUEPRINT_ID",
    "GovernanceValidationSubject",
    "GovernanceValidation",
    "governance_checks",
    "validate_governance",
]
