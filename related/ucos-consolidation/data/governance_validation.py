"""EC3-B10-U07 — Governance validation (meta-validity V1…V5 + UDL + DGA conformance).

This module proves a realized :class:`~data.governance.GovernanceObject` is **META-VALID**
(DATA-005 §8, V1…V5), **Data-law conformant** (DATA-001 §7, esp. **UDL-13 Governance as
Declarative Constraint**, UDL-03, UDL-04/05, UDL-02, UDL-09, UDL-15), and satisfies the
Governance contracts (DATA-012 §10, DGA-K1…K5 + the evaluation rules DGA-C1…C5) by
running a suite of deterministic, data-layer checks through the **CERTIFIED EC-1
Validation Engine** (:class:`engine.validation.executor.ValidationEngine`) and enforcing
the EC-1 acceptance gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`GovernanceValidationSubject`, so
an identical governance object yields a byte-identical report, evidence, and acceptance
decision (VC-4). Every check is **blocking**. A subset of check ids (``meta-class-single``,
``meta-relationships-closed``, ``foundation-reuse-integrity``, ``data-value-fidelity``,
``founding-acyclic``, ``provisional-state-disclosure``, ``traceability-rooted``) is
**shared with the CERTIFIED DMC-01 surface**, so the DMC-01 CCE ten-gate suite
(:func:`data.certification.cce_gates`) is reused verbatim by the Governance certification
(UDL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.governance import GovernanceObject
from data.governance_meta import (
    GOVERNANCE_META_CLASS,
    GOVERNANCE_RELATIONSHIPS,
    GovernanceState,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Governance object realizes (its meta-class) — used by the EC-1 report.
GOVERNANCE_BLUEPRINT_ID = GOVERNANCE_META_CLASS

_STATE_VALUES = frozenset(s.value for s in GovernanceState)
_META_RELATIONSHIPS = frozenset(GOVERNANCE_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class GovernanceValidationSubject:
    """A normalized, immutable projection of a Governance object that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the object's meta-facts. Holds no runtime
    state and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    value_digest: str
    governed_construct_id: str
    absorbs_governed: bool
    kind: str
    classified: bool
    policy_ref: str
    binds_policy_by_reference: bool
    conformance_laws: tuple[str, ...]
    records_conformance: bool
    gap_report: tuple[str, ...]
    verdict: str
    declarative: bool
    enforces: bool
    grants_access: bool
    recorded: bool
    steward: str
    stewardship_is_descriptor: bool
    names_technology: bool
    selects_technology: bool
    version: str
    relationships: tuple[str, ...]
    governance_state: str
    founding_acyclic: bool
    confers_authority: bool
    embeds_secret: bool
    redefines_el1: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    image_reference: str
    disclosure: dict[str, Any]

    @classmethod
    def from_governance(
        cls, governance: GovernanceObject, trace: TraceabilityRecord
    ) -> GovernanceValidationSubject:
        """Project ``governance`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=governance.governance_id,
            blueprint_id=GOVERNANCE_BLUEPRINT_ID,
            meta_class=governance.meta_class,
            name=governance.name,
            type_tag=governance.type_tag,
            value_digest=governance.structure_digest,
            governed_construct_id=governance.governed_construct_id(),
            absorbs_governed=governance.absorbs_governed(),
            kind=governance.kind.value,
            classified=governance.is_classified(),
            policy_ref=governance.policy_ref,
            binds_policy_by_reference=governance.binds_policy_by_reference(),
            conformance_laws=governance.conformance_laws(),
            records_conformance=governance.records_conformance(),
            gap_report=governance.gap_report(),
            verdict=governance.verdict.value,
            declarative=governance.is_declarative(),
            enforces=governance.enforces(),
            grants_access=governance.grants_access(),
            recorded=governance.is_recorded(),
            steward=governance.steward,
            stewardship_is_descriptor=governance.stewardship_is_descriptor(),
            names_technology=governance.names_technology(),
            selects_technology=governance.selects_technology(),
            version=governance.version,
            relationships=governance.meta_relationships(),
            governance_state=governance.state.value,
            founding_acyclic=governance.is_founding_acyclic(),
            confers_authority=governance.confers_authority(),
            embeds_secret=governance.embeds_secret(),
            redefines_el1=governance.redefines_el1(),
            substrate_refs=tuple(governance.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            image_reference="",  # governance is a record, not a deployable image
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Data-layer validation checks (each maps to explicit V*/UDL*/DGA* obligations)
# ---------------------------------------------------------------------------


class GovernanceTypedCheck(ValidationCheck):
    """UDL-03 / DGA-K1 — governance object is classified by a non-empty ENG-004 type."""

    check_id = "governance-typed"
    severity = Severity.BLOCKING
    description = "Governance object bears a non-empty ENG-004 type_tag (DGA-K1 / UDL-03)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("governance object is untyped (DGA-K1 / UDL-03)")
        return self._passed(type_tag=subject.type_tag)


class GovernanceNamedCheck(ValidationCheck):
    """DGA-K1 — governance object has an explicit, decidable name."""

    check_id = "governance-named"
    severity = Severity.BLOCKING
    description = "Governance object has an explicit, non-empty name."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.name.strip():
            return self._failed("governance object is unnamed")
        return self._passed(name=subject.name)


class GovernanceIdentifiedCheck(ValidationCheck):
    """UDL-04/05 / DGA-K1 / DMK-01 / C1 — object is identified (ENG-001), object-borne."""

    check_id = "governance-identified"
    severity = Severity.BLOCKING
    description = "Governance object bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-GOVERNANCE-"):
            return self._failed(
                "governance object has no ENG-001 identity (UDL-04)", id=subject.target_id
            )
        return self._passed(governance_id=subject.target_id)


class GovernanceValueFidelityCheck(ValidationCheck):
    """UDL-06 (transitive) / C3 — the object's representation is ENG-003 value-faithful."""

    check_id = "data-value-fidelity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Governance representation is content-addressed via ENG-003 encoding (UDL-06)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed(
                "governance representation is not value-faithful (UDL-06)", d=digest
            )
        return self._passed(value_digest=digest)


class GovernanceGovernsSubjectCheck(ValidationCheck):
    """DMR-07 / DOR-07 / DGA-C4 — object governs a CERTIFIED construct by reference."""

    check_id = "governance-governs-subject"
    severity = Severity.BLOCKING
    description = "Governance governs a CERTIFIED construct by reference; owns none (DMR-07)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        cid = subject.governed_construct_id
        if not cid.startswith("UCOS-"):
            return self._failed("governed subject is not a CERTIFIED construct (DMR-07)", cid=cid)
        if subject.absorbs_governed:
            return self._failed("governance owns/absorbs its subject (DGA-C4 / DMX-02)")
        return self._passed(governs=cid)


class GovernanceDeclarativeCheck(ValidationCheck):
    """DGA-01 / DGA-K2 — governance is a declarative, decidable predicate."""

    check_id = "governance-declarative"
    severity = Severity.BLOCKING
    description = "Governance is a declarative, decidable predicate (DGA-01 / DGA-K2)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.declarative:
            return self._failed("governance is not declarative (DGA-01 / DGA-K2)")
        return self._passed()


class GovernanceNonEnforcingCheck(ValidationCheck):
    """DGA-02 / DGA-K2 / UDL-13 — governance evaluates and records; it enforces nothing."""

    check_id = "governance-non-enforcing"
    severity = Severity.BLOCKING
    description = "Governance evaluates/records and enforces nothing (DGA-02 / UDL-13)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.enforces:
            return self._failed("governance enforces (DGA-02 / DGA-K2 — governance enacts nothing)")
        return self._passed()


class GovernanceNoAccessCheck(ValidationCheck):
    """DGA-03 / DGA-K5 — a governance object grants no access and confers no authority."""

    check_id = "governance-no-access"
    severity = Severity.BLOCKING
    description = "Governance grants no access and confers no authority (DGA-03 / DGA-K5)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.grants_access:
            return self._failed("governance grants access (DGA-03 / DGA-K5)")
        if subject.confers_authority:
            return self._failed("governance confers authority (DGA-03 / DGA-K5)")
        return self._passed()


class GovernanceRecordedCheck(ValidationCheck):
    """DGA-06 / DGA-K4 / DOV-08 — the judgment is recorded against an ENG-002 object."""

    check_id = "governance-recorded"
    severity = Severity.BLOCKING
    description = "The governance judgment is recorded on an ENG-002 object (DGA-06 / DOV-08)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.recorded:
            return self._failed("governance judgment is not recorded (DGA-06 / DGA-K4)")
        return self._passed()


class GovernanceBindsPolicyByReferenceCheck(ValidationCheck):
    """DMR-11 / DGA-07 / DGA-K3 — evaluation binds a RUNTIME policy reference (not redefined)."""

    check_id = "governance-binds-policy-by-reference"
    severity = Severity.BLOCKING
    description = "Evaluation binds a RUNTIME policy reference; no engine redefined (DMR-11)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.policy_ref.startswith("UCOS-POLICY-REF:"):
            return self._failed(
                "evaluation does not bind a RUNTIME policy reference (DMR-11 / DGA-K3)"
            )
        if not subject.binds_policy_by_reference:
            return self._failed("governance evaluation is not bound by reference (DMR-11 / DGA-07)")
        return self._passed(policy_ref=subject.policy_ref)


class GovernanceConformanceRecordedCheck(ValidationCheck):
    """DGA-C1 — a Conformance-Record decidably records each applicable-law verdict."""

    check_id = "governance-conformance-recorded"
    severity = Severity.BLOCKING
    description = "A Conformance-Record records ≥1 decidable per-law verdict (DGA-C1)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.records_conformance:
            return self._failed("a Conformance-Record records no law verdict (DGA-C1)")
        return self._passed(laws=list(subject.conformance_laws), verdict=subject.verdict)


class GovernanceStewardshipDescriptorCheck(ValidationCheck):
    """DGA-05 / DGA-C4 — stewardship/ownership are recorded descriptors, not powers."""

    check_id = "governance-stewardship-descriptor"
    severity = Severity.BLOCKING
    description = "Stewardship/ownership are recorded descriptors, not powers (DGA-05 / DGA-C4)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.stewardship_is_descriptor:
            return self._failed("stewardship confers power (DGA-05 / DGA-C4)")
        return self._passed(steward=subject.steward)


class GovernanceIndependenceCheck(ValidationCheck):
    """UDL-13 / DGA-09 / DGA-K5 / C6 — the object names no policy/enforcement tech (material)."""

    check_id = "governance-independence"
    severity = Severity.BLOCKING
    description = "No policy/rules engine, IAM, or enforcement point named (UDL-13 / DGA-K5)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.selects_technology or subject.image_reference:
            return self._failed("a policy/IAM/enforcement technology was named (UDL-13 / DGA-K5)")
        return self._passed()


class GovernanceVersionedCheck(ValidationCheck):
    """DGA-08 / UDL-12 — the object records an explicit version (additive/supersession)."""

    check_id = "governance-versioned"
    severity = Severity.BLOCKING
    description = "Governance object records an explicit version (DGA-08 / UDL-12)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("governance object records no version (DGA-08)")
        return self._passed(version=subject.version)


class GovernanceClassifiedCheck(ValidationCheck):
    """DXH-08 — the object is classified by exactly one governance kind."""

    check_id = "governance-classified"
    severity = Severity.BLOCKING
    description = "Governance object is classified by a single DXH-08 kind."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.classified or not subject.kind:
            return self._failed("governance object has no DXH-08 kind", kind=subject.kind)
        return self._passed(kind=subject.kind)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / DMI-01 — the object instantiates exactly one meta-class (DMC-08)."""

    check_id = "meta-class-single"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Governance object instantiates exactly the DMC-08 meta-class (V1)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.meta_class != GOVERNANCE_META_CLASS:
            return self._failed("meta-class is not DMC-08 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / DMI-02 — every relationship used lies within DMR-01…12 (uses 07/10/11)."""

    check_id = "meta-relationships-closed"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "All governance relationships are within DMR-01…12 (V2)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (DGA-K1 typed/identified, K2 declarative/non-enforcing)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DGA-K1 (typed+identified), K2 (declarative/non-enforcing), K5 (no-auth) — V3."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # DGA-K1 typed
            and subject.name.strip()  # named
            and subject.target_id  # DMK-01 identified
            and subject.declarative  # DGA-K2 declarative
            and not subject.enforces  # DGA-K2 non-enforcing
            and subject.binds_policy_by_reference  # DGA-K3 evaluation by reference
            and subject.recorded  # DGA-K4 recorded
            and not subject.grants_access  # DGA-K5 no access
            and not subject.confers_authority  # DGA-K5 no authority
            and subject.founding_acyclic  # DMK-03 acyclic
        )
        if not ok:
            return self._failed("DGA-K1/K2/K3/K4/K5 (DMK-01/03/07/08) not satisfied (V3)")
        return self._passed(constraints=["DGA-K1", "DGA-K2", "DGA-K3", "DGA-K4", "DGA-K5"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMK-03 — the founding/governance graph is acyclic."""

    check_id = "founding-acyclic"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The governance object's founding graph is acyclic (V4 / DMK-03)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding/governance graph is not acyclic (V4)")
        return self._passed()


class GovernanceValidStateCheck(ValidationCheck):
    """V5 / UDL-12 — the object holds a valid DOS-01…05 lifecycle state."""

    check_id = "governance-valid"
    severity = Severity.BLOCKING
    description = "Governance object holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.governance_state not in _STATE_VALUES:
            return self._failed("invalid governance state (V5)", state=subject.governance_state)
        return self._passed(state=subject.governance_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UDL-02 / DMI-05 / VC-5 — EL-1 + DMC-02 + RL-F2 reused by reference only."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + DMC-02 + RL-F2 substrate referenced, redefined nowhere (UDL-02)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/DMC-02/RL-F2 primitive was redefined (UDL-02)")
        if not subject.substrate_refs:
            return self._failed("no EL-1 substrate reference recorded (UDL-02)")
        if subject.absorbs_governed:
            return self._failed("the certified data model was owned, not referenced (DMX-02)")
        if not subject.binds_policy_by_reference:
            return self._failed("RUNTIME policy was not bound by reference (UDL-02 / DGA-07)")
        return self._passed(substrate=list(subject.substrate_refs))


class NonConstitutiveCheck(ValidationCheck):
    """UDL-15 / DGA-09 / C7 — the object confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Governance confers no authority and embeds no secret (UDL-15 / DGA-09)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("governance confers authority (UDL-15 / DGA-09)")
        if subject.embeds_secret:
            return self._failed("governance embeds a secret (UDL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§16 / AC — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at DMC-08 and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def governance_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
    return (
        GovernanceTypedCheck(),
        GovernanceNamedCheck(),
        GovernanceIdentifiedCheck(),
        GovernanceValueFidelityCheck(),
        GovernanceGovernsSubjectCheck(),
        GovernanceDeclarativeCheck(),
        GovernanceNonEnforcingCheck(),
        GovernanceNoAccessCheck(),
        GovernanceRecordedCheck(),
        GovernanceBindsPolicyByReferenceCheck(),
        GovernanceConformanceRecordedCheck(),
        GovernanceStewardshipDescriptorCheck(),
        GovernanceIndependenceCheck(),
        GovernanceVersionedCheck(),
        GovernanceClassifiedCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        GovernanceValidStateCheck(),
        FoundationReuseIntegrityCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class GovernanceValidation:
    """The bundled outcome of validating a Governance object (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_governance(
    governance: GovernanceObject, trace: TraceabilityRecord, *, strict: bool = False
) -> GovernanceValidation:
    """Validate ``governance`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected object raises via the
    EC-1 acceptance gate.
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
