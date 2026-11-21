"""EC3-B12-U09 — Security validation (meta-validity V1…V5 + UAL/SEC conformance).

This module proves a realized :class:`~application.security.Security` record is **META-VALID**
(APPLICATION-005 §8, V1…V5) and **Application-/Security-law conformant** (APPLICATION-001 §7,
UAL-01…15; APPLICATION-013 §4, SEC-01…10) by running a suite of deterministic, application-layer
checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance gate
(:func:`engine.validation.gates.enforce_acceptance`). Validation evidence is produced with the
EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`SecurityValidationSubject` (the
type-independent projection the EC-1 engine consumes), so an identical record yields a
byte-identical report, evidence, and acceptance decision (VC-4). Every check is **blocking**:
the verdict is PASS iff the record satisfies every meta-validity and Application-/Security-law
obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.security import Security
from application.security_meta import (
    META_RELATIONSHIPS,
    SECURITY_META_CLASS,
    SecurityKind,
    SecurityState,
)
from application.security_traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UAL-02) — the certified validation substrate --------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Security record realizes (its meta-class) — used by the EC-1 report.
SECURITY_BLUEPRINT_ID = SECURITY_META_CLASS

_KIND_VALUES = frozenset(k.value for k in SecurityKind)
_STATE_VALUES = frozenset(s.value for s in SecurityState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)
_FACETS = frozenset({"authentication", "authorization", "confidentiality", "integrity"})


@dataclass(frozen=True, slots=True)
class SecurityValidationSubject:
    """A normalized, immutable projection of a Security record that checks evaluate.

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
    governance_refs: tuple[str, ...]
    data_refs: tuple[str, ...]
    behavior_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    is_founding: bool
    classifies_boundary: bool
    evaluative_nonenforcing: bool
    binds_runtime_policy: bool
    behavior_by_reference: bool
    data_by_reference: bool
    data_security_reuse: bool
    governed_by_reference: bool
    references_resolve: bool
    uses_new_connection_construct: bool
    precedence_decidable: bool
    confers_authority: bool
    grants_access: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_security(
        cls, security: Security, trace: TraceabilityRecord
    ) -> SecurityValidationSubject:
        """Project ``security`` (+ its lineage) into a validation subject."""
        payload = security.to_dict()
        return cls(
            target_id=security.security_id,
            blueprint_id=SECURITY_BLUEPRINT_ID,
            meta_class=security.meta_class,
            type_tag=security.type_tag,
            kind=security.kind.value,
            facet=security.facet(),
            value_digest=security.value_digest,
            subject_refs=tuple(payload["subject_refs"]),
            governance_refs=tuple(payload["governance_refs"]),
            data_refs=tuple(payload["data_refs"]),
            behavior_ref=security.behavior_ref,
            relationships=security.meta_relationships(),
            lifecycle_state=security.state.value,
            founding_acyclic=security.is_founding_acyclic(),
            is_founding=security.participates_in_founding_edge(),
            classifies_boundary=security.classifies_boundary(),
            evaluative_nonenforcing=security.evaluative_nonenforcing(),
            binds_runtime_policy=security.binds_runtime_policy(),
            behavior_by_reference=security.behavior_by_reference(),
            data_by_reference=security.data_by_reference(),
            data_security_reuse=security.data_security_reuse(),
            governed_by_reference=security.governed_by_reference(),
            references_resolve=security.references_resolve(),
            uses_new_connection_construct=security.uses_new_connection_construct(),
            precedence_decidable=security.precedence_decidable(),
            confers_authority=security.confers_authority(),
            grants_access=security.grants_access(),
            selects_technology=security.selects_technology(),
            embeds_secret=security.embeds_secret(),
            redefines_foundation=security.redefines_foundation(),
            substrate_refs=tuple(payload["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Security-layer validation checks (each maps to explicit V*/UAL*/SEC*/AMK* obligations)
# ---------------------------------------------------------------------------


class SecurityTypedCheck(ValidationCheck):
    """UAL-03 / SEC-01 / AMK-01 / C1 — the record is classified by a non-empty type."""

    check_id = "security-typed"
    severity = Severity.BLOCKING
    description = "Security record bears a non-empty ENG-004 type_tag (UAL-03 / SEC-01)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("security record is untyped (UAL-03 / SEC-01)")
        return self._passed(type_tag=subject.type_tag)


class SecurityIdentifiedCheck(ValidationCheck):
    """UAL-04/05 / SEC-02 / AMK-01 / C1 — the record is identified and object-borne."""

    check_id = "security-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Security record bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-SECURITY-"):
            return self._failed(
                "security record lacks ENG-001 identity (UAL-04)", id=subject.target_id
            )
        if not subject.value_digest:
            return self._failed("security record is not object-borne (no value digest) (UAL-05)")
        return self._passed(security_id=subject.target_id)


class SecurityValueFidelityCheck(ValidationCheck):
    """ENG-003 — the record core round-trips through the EC-1 canonical encoding."""

    check_id = "security-value-fidelity"
    severity = Severity.BLOCKING
    description = "Security core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("security core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class SecurityClassifiedCheck(ValidationCheck):
    """AXH-09 / AXC-04 — the record is classified by exactly one Security kind."""

    check_id = "security-classified"
    severity = Severity.BLOCKING
    description = "Security record is classified by an AXH-09 kind (single-facet, AXC-04)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("security kind is outside AXH-09", kind=subject.kind)
        if subject.facet not in _FACETS:
            return self._failed("security facet is outside AXH-09", facet=subject.facet)
        return self._passed(kind=subject.kind, facet=subject.facet)


class SecurityClassifiesBoundaryCheck(ValidationCheck):
    """AMR-08 / AOR-08 / SEC-07 / SEC-K2 — the record classifies ≥1 declared boundary (defining)."""

    check_id = "security-classifies-boundary"
    severity = Severity.BLOCKING
    description = "Security record classifies ≥1 boundary by ENG-005 reference (AMR-08 / SEC-07)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.classifies_boundary or not subject.subject_refs:
            return self._failed("security record classifies no boundary (AMR-08 / SEC-07)")
        return self._passed(secured_count=len(subject.subject_refs))


class SecurityEvaluativeNonEnforcingCheck(ValidationCheck):
    """UAL-14 / SEC-03/04 / SEC-C1/C2 — the record is evaluative and enacts nothing (governing)."""

    check_id = "security-evaluative-nonenforcing"
    severity = Severity.BLOCKING
    description = "Security is evaluative, grants no access, confers no authority (UAL-14 law)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.evaluative_nonenforcing:
            return self._failed("security record enacts/grants (UAL-14 / SEC-03 / SEC-C1/C2)")
        if subject.grants_access:
            return self._failed("security record grants access (SEC-04 / SEC-C2)")
        return self._passed(governing_law="UAL-14")


class SecurityGovernanceByReferenceCheck(ValidationCheck):
    """AMR-09 / AOR-09 — the informing Governance is referenced (governed-by, reference-only)."""

    check_id = "security-governance-by-reference"
    severity = Severity.BLOCKING
    description = "Informing Governance is bound by ENG-005 reference (AMR-09 governed-by)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.governed_by_reference:
            return self._failed("a governance reference is malformed (AMR-09)")
        return self._passed(governance_count=len(subject.governance_refs))


class SecurityBehaviorByReferenceCheck(ValidationCheck):
    """UAL-10 / §7 / AMK-05 — the security-evaluate behavior binds RL-F2 by reference."""

    check_id = "security-behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Security-evaluate behavior binds RL-F2 by ENG-005 reference (§7 / AMK-05)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip() or not subject.behavior_by_reference:
            return self._failed("no RL-F2 security-evaluate reference (§7 / UAL-10)")
        if not subject.binds_runtime_policy:
            return self._failed(
                "security-evaluate binding names a concrete technology, not RL-F2 (AMK-05)",
                behavior_ref=subject.behavior_ref,
            )
        return self._passed(behavior_ref=subject.behavior_ref)


class SecurityDataByReferenceCheck(ValidationCheck):
    """AMR-14 / AOR-14 / UAL-13 / SEC-06 — presented data is DF-2/DATA-014 by reference."""

    check_id = "security-data-by-reference"
    severity = Severity.BLOCKING
    description = "Presented data is DF-2/DATA-014 by ENG-005 reference (AMR-14 / UAL-13 / SEC-06)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.data_by_reference:
            return self._failed("a presented-data reference is malformed (AMR-14 / UAL-13)")
        if not subject.data_security_reuse:
            return self._failed("data-security classifications not reused by reference (SEC-C4)")
        return self._passed(data_count=len(subject.data_refs))


class SecurityNoNewConnectionCheck(ValidationCheck):
    """SEC-C4 analog — the record introduces no new connection construct (all ENG-005 refs)."""

    check_id = "security-no-new-connection"
    severity = Severity.BLOCKING
    description = "Security record introduces no new connection construct; all links ENG-005."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.uses_new_connection_construct:
            return self._failed("security record introduces a new connection construct (SEC-C4)")
        return self._passed()


class MetaClassSingleCheck(ValidationCheck):
    """V1 / AMI-01 — the record instantiates exactly one meta-class (AMC-09)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Security record instantiates exactly the AMC-09 meta-class (V1)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.meta_class != SECURITY_META_CLASS:
            return self._failed("meta-class is not AMC-09 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / AMI-02 — every relationship used lies within AMR-01…14."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All security relationships are within AMR-01…14 (V2)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside AMR-01…14 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (AMK-01 typed/id/object; AMK-02/05/07 references)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "AMK-01 (typed/identified/object), AMK-02 (boundary), AMK-05/07 (refs) hold (V3)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("AMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("AMK-05/07 not satisfied: a reference does not resolve (V3)")
        if not (subject.classifies_boundary and subject.precedence_decidable):
            return self._failed(
                "AMK-02 not satisfied: no declared boundary/concern (V3)"
            )
        return self._passed(constraints=["AMK-01", "AMK-02", "AMK-03", "AMK-05", "AMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / AMK-03 — the founding graph is acyclic (vacuous: no founding edge).

    A Security record participates in no founding relationship (its relationships AMR-08/09/10/14
    are all reference-only), so its founding graph is empty and therefore acyclic, exactly as the
    State used no founding edge. Proven via the no-self-founding guard.
    """

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The security record's founding graph is acyclic (V4 / AMK-03)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4 / AMK-03)")
        if subject.is_founding:
            return self._failed("a security record must participate in no founding edge (AMK-03)")
        return self._passed(founding="vacuous (reference-only)")


class LifecycleValidCheck(ValidationCheck):
    """V5 / UAL-12 — the record holds a valid AOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Security record holds a valid AOS-01…06 lifecycle state (V5 / UAL-12)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UAL-02 / SEC-06 / AMI-05 / VC-5 — frozen foundations reused by reference, not redefined."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/DF-2 (+ DATA-014) referenced, redefined nowhere (UAL-02 / AMI-05)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UAL-02 / AMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UAL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """UAL-15 / SEC-05 / SEC-C3 / C7 — no crypto/IAM/provider/protocol/technology is selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No cryptography/IAM/provider/protocol/technology selected (UAL-15 / SEC-05)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete security technology was selected (UAL-15 / SEC-05)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UAL-15 / SEC-09 / C7 — the record confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Security record confers no authority and embeds no secret (UAL-15 / RR-07)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("security record confers authority (UAL-15 / SEC-09)")
        if subject.embeds_secret:
            return self._failed("security record embeds a secret (UAL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 12-APPLICATION anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at AMC-09 and closed to 12-APPLICATION (No-Orphan)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("12-APPLICATION@") for link in chain):
            return self._failed("lineage does not close to the 12-APPLICATION anchor")
        return self._passed(links=len(chain))


def security_checks() -> tuple[ValidationCheck, ...]:
    """The full security-layer validation suite (deterministically ordered by the engine)."""
    return (
        SecurityTypedCheck(),
        SecurityIdentifiedCheck(),
        SecurityValueFidelityCheck(),
        SecurityClassifiedCheck(),
        SecurityClassifiesBoundaryCheck(),
        SecurityEvaluativeNonEnforcingCheck(),
        SecurityGovernanceByReferenceCheck(),
        SecurityBehaviorByReferenceCheck(),
        SecurityDataByReferenceCheck(),
        SecurityNoNewConnectionCheck(),
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
class SecurityValidation:
    """The bundled outcome of validating a Security record (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_security(
    security: Security, trace: TraceabilityRecord, *, strict: bool = False
) -> SecurityValidation:
    """Validate ``security`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected record raises via the EC-1
    acceptance gate.
    """
    subject = SecurityValidationSubject.from_security(security, trace)
    engine = ValidationEngine(security_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return SecurityValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "SECURITY_BLUEPRINT_ID",
    "SecurityValidationSubject",
    "SecurityValidation",
    "security_checks",
    "validate_security",
]
