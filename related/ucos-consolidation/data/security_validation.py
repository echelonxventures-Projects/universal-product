"""EC3-B10-U09 — Security validation (meta-validity V1…V5 + UDL + DZA conformance).

This module proves a realized :class:`~data.security.SecurityObject` is **META-VALID**
(DATA-005 §8, V1…V5), **Data-law conformant** (DATA-001 §7, esp. **UDL-14 Security as an
Evaluative Facet**, UDL-03, UDL-04/05, UDL-02, UDL-09, UDL-15), and satisfies the Security
contracts (DATA-014 §10, DZA-K1…K5 + the classification rules DZA-C1…C5) by running a suite
of deterministic, data-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`SecurityValidationSubject`, so an
identical security object yields a byte-identical report, evidence, and acceptance decision
(VC-4). Every check is **blocking**. A subset of check ids (``meta-class-single``,
``meta-relationships-closed``, ``foundation-reuse-integrity``, ``data-value-fidelity``,
``founding-acyclic``, ``provisional-state-disclosure``, ``traceability-rooted``) is
**shared with the CERTIFIED DMC-01 surface**, so the DMC-01 CCE ten-gate suite
(:func:`data.certification.cce_gates`) is reused verbatim by the Security certification
(UDL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.security import SecurityObject
from data.security_meta import (
    SECURITY_META_CLASS,
    SECURITY_RELATIONSHIPS,
    SecurityState,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Security object realizes (its meta-class) — used by the EC-1 report.
SECURITY_BLUEPRINT_ID = SECURITY_META_CLASS

_STATE_VALUES = frozenset(s.value for s in SecurityState)
_META_RELATIONSHIPS = frozenset(SECURITY_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class SecurityValidationSubject:
    """A normalized, immutable projection of a Security object that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1 ``ValidationEngine``
    consumes) plus the object's meta-facts. Holds no runtime state and no wall-clock, so
    it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    value_digest: str
    classified_construct_id: str
    absorbs_classified: bool
    kind: str
    classified: bool
    policy_ref: str
    binds_policy_by_reference: bool
    enforcement_by_reference: bool
    classified_dimensions: tuple[str, ...]
    records_classification: bool
    dimensioned: bool
    gap_report: tuple[str, ...]
    verdict: str
    evaluative: bool
    enforces: bool
    grants_access: bool
    recorded: bool
    names_technology: bool
    selects_technology: bool
    version: str
    relationships: tuple[str, ...]
    security_state: str
    founding_acyclic: bool
    confers_authority: bool
    embeds_secret: bool
    redefines_el1: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    image_reference: str
    disclosure: dict[str, Any]

    @classmethod
    def from_security(
        cls, security: SecurityObject, trace: TraceabilityRecord
    ) -> SecurityValidationSubject:
        """Project ``security`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=security.security_id,
            blueprint_id=SECURITY_BLUEPRINT_ID,
            meta_class=security.meta_class,
            name=security.name,
            type_tag=security.type_tag,
            value_digest=security.structure_digest,
            classified_construct_id=security.classified_construct_id(),
            absorbs_classified=security.absorbs_classified(),
            kind=security.kind.value,
            classified=security.is_classified(),
            policy_ref=security.policy_ref,
            binds_policy_by_reference=security.binds_policy_by_reference(),
            enforcement_by_reference=security.enforcement_by_reference(),
            classified_dimensions=security.classified_dimensions(),
            records_classification=security.records_classification(),
            dimensioned=security.is_dimensioned(),
            gap_report=security.gap_report(),
            verdict=security.verdict.value,
            evaluative=security.is_evaluative(),
            enforces=security.enforces(),
            grants_access=security.grants_access(),
            recorded=security.is_recorded(),
            names_technology=security.names_technology(),
            selects_technology=security.selects_technology(),
            version=security.version,
            relationships=security.meta_relationships(),
            security_state=security.state.value,
            founding_acyclic=security.is_founding_acyclic(),
            confers_authority=security.confers_authority(),
            embeds_secret=security.embeds_secret(),
            redefines_el1=security.redefines_el1(),
            substrate_refs=tuple(security.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            image_reference="",  # security is a record, not a deployable image
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Data-layer validation checks (each maps to explicit V*/UDL*/DZA* obligations)
# ---------------------------------------------------------------------------


class SecurityTypedCheck(ValidationCheck):
    """UDL-03 / DZA-K1 — security object is classified by a non-empty ENG-004 type."""

    check_id = "security-typed"
    severity = Severity.BLOCKING
    description = "Security object bears a non-empty ENG-004 type_tag (DZA-K1 / UDL-03)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("security object is untyped (DZA-K1 / UDL-03)")
        return self._passed(type_tag=subject.type_tag)


class SecurityNamedCheck(ValidationCheck):
    """DZA-K1 — security object has an explicit, decidable name."""

    check_id = "security-named"
    severity = Severity.BLOCKING
    description = "Security object has an explicit, non-empty name."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.name.strip():
            return self._failed("security object is unnamed")
        return self._passed(name=subject.name)


class SecurityIdentifiedCheck(ValidationCheck):
    """UDL-04/05 / DZA-K1 / DMK-01 / C1 — object is identified (ENG-001), object-borne."""

    check_id = "security-identified"
    severity = Severity.BLOCKING
    description = "Security object bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-SECURITY-"):
            return self._failed(
                "security object has no ENG-001 identity (UDL-04)", id=subject.target_id
            )
        return self._passed(security_id=subject.target_id)


class SecurityValueFidelityCheck(ValidationCheck):
    """UDL-06 (transitive) / C3 — the object's representation is ENG-003 value-faithful."""

    check_id = "data-value-fidelity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Security representation is content-addressed via ENG-003 encoding (UDL-06)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("security representation is not value-faithful (UDL-06)", d=digest)
        return self._passed(value_digest=digest)


class SecurityClassifiesSubjectCheck(ValidationCheck):
    """DMR-09 / DOR-09 / DZA-C3 — object classifies a CERTIFIED construct by reference."""

    check_id = "security-classifies-subject"
    severity = Severity.BLOCKING
    description = "Security classifies a CERTIFIED construct by reference; owns none (DMR-09)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        cid = subject.classified_construct_id
        if not cid.startswith("UCOS-"):
            return self._failed("classified subject is not a CERTIFIED construct (DMR-09)", cid=cid)
        if subject.absorbs_classified:
            return self._failed("security owns/absorbs its subject (DZA-C3 / DMX-02)")
        return self._passed(classifies=cid)


class SecurityEvaluativeCheck(ValidationCheck):
    """DZA-01 / DZA-K2 — security is a decidable, evaluative classification."""

    check_id = "security-evaluative"
    severity = Severity.BLOCKING
    description = "Security is a decidable, evaluative classification (DZA-01 / DZA-K2)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.evaluative:
            return self._failed("security is not evaluative (DZA-01 / DZA-K2)")
        return self._passed()


class SecurityDimensionedCheck(ValidationCheck):
    """DZA-02 — security is classified along a decidable dimension (single-facet, DXC-02)."""

    check_id = "security-dimensioned"
    severity = Severity.BLOCKING
    description = "Security is classified along a decidable dimension (DZA-02 / DXC-02)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.dimensioned or not subject.classified_dimensions:
            return self._failed(
                "security is not dimensioned (DZA-02)", dims=list(subject.classified_dimensions)
            )
        return self._passed(dimensions=list(subject.classified_dimensions))


class SecurityNonEnforcingCheck(ValidationCheck):
    """DZA-01 / DZA-C2 / DZA-K2 / UDL-14 — security classifies/records; enforces/grants nothing."""

    check_id = "security-non-enforcing"
    severity = Severity.BLOCKING
    description = "Security classifies/records and enforces/grants nothing (DZA-01 / UDL-14)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.enforces:
            return self._failed("security enforces (DZA-01 / DZA-K2 — security enacts nothing)")
        if subject.grants_access:
            return self._failed("security grants access (DZA-01 / DZA-C2 — enacts nothing)")
        return self._passed()


class SecurityRecordedCheck(ValidationCheck):
    """DZA-04 / DZA-K4 / DOV-08 — the classification is recorded against an ENG-002 object."""

    check_id = "security-recorded"
    severity = Severity.BLOCKING
    description = "The security classification is recorded on an ENG-002 object (DZA-04 / DOV-08)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.recorded:
            return self._failed("security classification is not recorded (DZA-04 / DZA-K4)")
        return self._passed()


class SecurityBindsPolicyByReferenceCheck(ValidationCheck):
    """DMR-11 / DZA-06 / DZA-K3 — integrity-check binds a RUNTIME policy reference by ref."""

    check_id = "security-binds-policy-by-reference"
    severity = Severity.BLOCKING
    description = "Integrity-check binds a RUNTIME policy reference; no engine redefined (DMR-11)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.policy_ref.startswith("UCOS-POLICY-REF:"):
            return self._failed(
                "integrity-check does not bind a RUNTIME policy reference (DMR-11 / DZA-K3)"
            )
        if not subject.binds_policy_by_reference:
            return self._failed("security evaluation is not bound by reference (DMR-11 / DZA-06)")
        return self._passed(policy_ref=subject.policy_ref)


class SecurityClassificationRecordedCheck(ValidationCheck):
    """DZA-C1 — the object decidably records ≥1 per-dimension classification verdict."""

    check_id = "security-classification-recorded"
    severity = Severity.BLOCKING
    description = "A security object records ≥1 decidable per-dimension classification (DZA-C1)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.records_classification:
            return self._failed("a security object records no classification (DZA-C1)")
        return self._passed(
            dimensions=list(subject.classified_dimensions), verdict=subject.verdict
        )


class SecurityEnforcementByReferenceCheck(ValidationCheck):
    """DZA-03 / DZA-C3 — any enforcement obligation is expressed as a downstream reference."""

    check_id = "security-enforcement-by-reference"
    severity = Severity.BLOCKING
    description = "Enforcement obligations are downstream references; none defined here (DZA-03)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.enforces:
            return self._failed("security defines enforcement (DZA-03 — enforcement is by ref)")
        if not subject.enforcement_by_reference:
            return self._failed(
                "security does not express enforcement by reference (DZA-03 / DZA-C3)"
            )
        return self._passed()


class SecurityIndependenceCheck(ValidationCheck):
    """UDL-14 / DZA-07 / DZA-C5 / DZA-K5 / C6 — object names no crypto/controls tech (material)."""

    check_id = "security-independence"
    severity = Severity.BLOCKING
    description = "No cryptography/IAM/DLP technology or vendor named (UDL-14 / DZA-07 / DZA-K5)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.selects_technology or subject.image_reference:
            return self._failed(
                "a cryptography/access-control/DLP technology was named (UDL-14 / DZA-K5)"
            )
        return self._passed()


class SecurityVersionedCheck(ValidationCheck):
    """DZA-08 / UDL-12 — the object records an explicit version (additive/append-only)."""

    check_id = "security-versioned"
    severity = Severity.BLOCKING
    description = "Security object records an explicit version (DZA-08 / UDL-12)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("security object records no version (DZA-08)")
        return self._passed(version=subject.version)


class SecurityClassifiedCheck(ValidationCheck):
    """DXH-10 — the object is classified by exactly one security kind."""

    check_id = "security-classified"
    severity = Severity.BLOCKING
    description = "Security object is classified by a single DXH-10 kind."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.classified or not subject.kind:
            return self._failed("security object has no DXH-10 kind", kind=subject.kind)
        return self._passed(kind=subject.kind)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / DMI-01 — the object instantiates exactly one meta-class (DMC-10)."""

    check_id = "meta-class-single"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Security object instantiates exactly the DMC-10 meta-class (V1)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.meta_class != SECURITY_META_CLASS:
            return self._failed("meta-class is not DMC-10 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / DMI-02 — every relationship used lies within DMR-01…12 (uses 09/10/11)."""

    check_id = "meta-relationships-closed"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "All security relationships are within DMR-01…12 (V2)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (DZA-K1 typed/identified, K2 evaluative/non-enforcing)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DZA-K1 (typed+identified), K2 (evaluative/non-enforcing), K5 (no-auth) — V3."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # DZA-K1 typed
            and subject.name.strip()  # named
            and subject.target_id  # DMK-01 identified
            and subject.evaluative  # DZA-K2 evaluative
            and not subject.enforces  # DZA-K2 non-enforcing
            and not subject.grants_access  # DZA-K2 grants nothing
            and subject.binds_policy_by_reference  # DZA-K3 evaluation by reference
            and subject.recorded  # DZA-K4 recorded
            and not subject.confers_authority  # DZA-K5 no authority
            and subject.founding_acyclic  # DMK-03 acyclic
        )
        if not ok:
            return self._failed("DZA-K1/K2/K3/K4/K5 (DMK-01/03/07/08) not satisfied (V3)")
        return self._passed(constraints=["DZA-K1", "DZA-K2", "DZA-K3", "DZA-K4", "DZA-K5"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMK-03 — the founding/classification graph is acyclic."""

    check_id = "founding-acyclic"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The security object's founding graph is acyclic (V4 / DMK-03)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding/classification graph is not acyclic (V4)")
        return self._passed()


class SecurityValidStateCheck(ValidationCheck):
    """V5 / UDL-12 — the object holds a valid DOS-01…05 lifecycle state."""

    check_id = "security-valid"
    severity = Severity.BLOCKING
    description = "Security object holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.security_state not in _STATE_VALUES:
            return self._failed("invalid security state (V5)", state=subject.security_state)
        return self._passed(state=subject.security_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UDL-02 / DMI-05 / VC-5 — EL-1 + DMC-02 + RL-F2 reused by reference only."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + DMC-02 + RL-F2 substrate referenced, redefined nowhere (UDL-02)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/DMC-02/RL-F2 primitive was redefined (UDL-02)")
        if not subject.substrate_refs:
            return self._failed("no EL-1 substrate reference recorded (UDL-02)")
        if subject.absorbs_classified:
            return self._failed("the certified data model was owned, not referenced (DMX-02)")
        if not subject.binds_policy_by_reference:
            return self._failed("RUNTIME policy was not bound by reference (UDL-02 / DZA-06)")
        return self._passed(substrate=list(subject.substrate_refs))


class NonConstitutiveCheck(ValidationCheck):
    """UDL-15 / DZA-09 / C7 — the object confers no authority, grants no access, holds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Security confers no authority, grants no access, embeds no secret (UDL-15)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("security confers authority (UDL-15 / DZA-09)")
        if subject.grants_access:
            return self._failed("security grants access (UDL-15 / DZA-09 / DZA-K5)")
        if subject.embeds_secret:
            return self._failed("security embeds a secret (UDL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§17 / AC — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at DMC-10 and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def security_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
    return (
        SecurityTypedCheck(),
        SecurityNamedCheck(),
        SecurityIdentifiedCheck(),
        SecurityValueFidelityCheck(),
        SecurityClassifiesSubjectCheck(),
        SecurityEvaluativeCheck(),
        SecurityDimensionedCheck(),
        SecurityNonEnforcingCheck(),
        SecurityRecordedCheck(),
        SecurityBindsPolicyByReferenceCheck(),
        SecurityClassificationRecordedCheck(),
        SecurityEnforcementByReferenceCheck(),
        SecurityIndependenceCheck(),
        SecurityVersionedCheck(),
        SecurityClassifiedCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        SecurityValidStateCheck(),
        FoundationReuseIntegrityCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class SecurityValidation:
    """The bundled outcome of validating a Security object (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_security(
    security: SecurityObject, trace: TraceabilityRecord, *, strict: bool = False
) -> SecurityValidation:
    """Validate ``security`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected object raises via the
    EC-1 acceptance gate.
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
