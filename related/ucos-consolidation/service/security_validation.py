"""EC3-B11-U10 — Security validation (meta-validity V1…V5 + USL + SSE principles).

Proves a realized :class:`~service.security.Security` is **META-VALID** (SERVICE-005 §8,
V1…V5), **Service-law conformant** (SERVICE-001 §7), and **Security-principle conformant**
(SERVICE-014 §4, SSE-01…10) by running deterministic checks through the **CERTIFIED EC-1
Validation Engine**.

The suite emits the seven **generic** check ids the CCE ten-gate suite depends on
(``traceability-rooted``, ``meta-class-single``, ``foundation-reuse-integrity``,
``service-value-fidelity``, ``founding-acyclic``, ``meta-relationships-closed``,
``provisional-state-disclosure``) so that
:func:`service.service_certification.cce_gates` is reused **verbatim**. The result is bundled
as the shared :class:`service.service_validation.ServiceValidation`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding
from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance
from service.security import Security
from service.security_meta import (
    KIND_RUNTIME_CONCERN,
    SECURITY_META_CLASS,
    SecurityKind,
)
from service.security_traceability import SecurityTraceabilityRecord
from service.service_meta import META_RELATIONSHIPS, ServiceState
from service.service_validation import ServiceValidation

#: The blueprint id a Security object realizes (its meta-class) — used by the EC-1 report.
SECURITY_BLUEPRINT_ID = SECURITY_META_CLASS

_KIND_VALUES = frozenset(k.value for k in SecurityKind)
_STATE_VALUES = frozenset(s.value for s in ServiceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class SecurityValidationSubject:
    """A normalized, immutable projection of a Security object that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    subject_refs: tuple[str, ...]
    policy_refs: tuple[str, ...]
    behavior_ref: str
    data_refs: tuple[str, ...]
    runtime_concern: str
    precedence: int
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    no_self_founding: bool
    boundary_classified: bool
    evaluative_nonenforcing: bool
    runtime_reuse_valid: bool
    behavior_by_reference: bool
    data_by_reference: bool
    data_security_reuse: bool
    policy_informed: bool
    precedence_decidable: bool
    records_lifecycle: bool
    references_resolve: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_security(
        cls, security: Security, trace: SecurityTraceabilityRecord
    ) -> SecurityValidationSubject:
        """Project ``security`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=security.security_id,
            blueprint_id=SECURITY_BLUEPRINT_ID,
            meta_class=security.meta_class,
            type_tag=security.type_tag,
            kind=security.kind.value,
            value_digest=security.value_digest,
            subject_refs=security.subject_refs,
            policy_refs=security.policy_refs,
            behavior_ref=security.behavior_ref,
            data_refs=security.data_refs,
            runtime_concern=KIND_RUNTIME_CONCERN[security.kind],
            precedence=security.precedence,
            relationships=security.meta_relationships(),
            lifecycle_state=security.state.value,
            founding_acyclic=security.is_founding_acyclic(),
            no_self_founding=security.no_self_founding(),
            boundary_classified=security.boundary_classified(),
            evaluative_nonenforcing=security.evaluative_nonenforcing(),
            runtime_reuse_valid=security.runtime_reuse_valid(),
            behavior_by_reference=security.behavior_by_reference(),
            data_by_reference=security.data_by_reference(),
            data_security_reuse=security.data_security_reuse(),
            policy_informed=security.policy_informed(),
            precedence_decidable=security.precedence_decidable(),
            records_lifecycle=security.records_lifecycle(),
            references_resolve=security.references_resolve(),
            confers_authority=security.confers_authority(),
            selects_technology=security.selects_technology(),
            embeds_secret=security.embeds_secret(),
            redefines_foundation=security.redefines_foundation(),
            substrate_refs=tuple(security.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),
        )


# ---------------------------------------------------------------------------
# Security-layer validation checks
# ---------------------------------------------------------------------------


class SecurityTypedCheck(ValidationCheck):
    """USL-03 / SSE-01 / C1 — the security object is typed (non-empty ENG-004 type)."""

    check_id = "security-typed"
    severity = Severity.BLOCKING
    description = "Security bears a non-empty ENG-004 type_tag (USL-03 / SSE-01)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("security is untyped (USL-03)")
        return self._passed(type_tag=subject.type_tag)


class SecurityIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SSE-02 / C1 — the security object is identified (ENG-001) and object-borne."""

    check_id = "security-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Security bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-SECURITY-"):
            return self._failed("security has no ENG-001 identity (USL-04)")
        if not subject.value_digest:
            return self._failed("security is not object-borne (no value digest) (USL-05)")
        return self._passed(security_id=subject.target_id)


class SecurityValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the security core round-trips through the EC-1 canonical encoding.

    Emitted under the shared id ``service-value-fidelity`` so the reused CCE Gate-3
    aggregates it without duplicating gate logic.
    """

    check_id = "service-value-fidelity"
    severity = Severity.BLOCKING
    description = "Security core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("security core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class SecurityClassifiedCheck(ValidationCheck):
    """SXH-10 / SXC-02 — the security object is classified by exactly one kind."""

    check_id = "security-classified"
    severity = Severity.BLOCKING
    description = "Security is classified by an SXH-10 kind (single-facet, SXC-02)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("security kind is outside SXH-10", kind=subject.kind)
        return self._passed(kind=subject.kind)


class SecurityBoundaryClassifiedCheck(ValidationCheck):
    """SMR-09 / SOR-09 / SSE-07 / SSE-K2 — classifies at least one declared boundary."""

    check_id = "security-boundary-classified"
    severity = Severity.BLOCKING
    description = "Security classifies a service/operation/execution boundary (SMR-09)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.boundary_classified:
            return self._failed("security classifies no boundary (SMR-09 / SSE-07)")
        return self._passed(subject_refs=len(subject.subject_refs))


class SecurityEvaluativeCheck(ValidationCheck):
    """SSE-03 / SSE-C1 / USL-14 — the security object is evaluative and non-enforcing (THE law)."""

    check_id = "security-evaluative-nonenforcing"
    severity = Severity.BLOCKING
    description = "Security is evaluative; grants no access, issues nothing, encrypts nothing."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.evaluative_nonenforcing:
            return self._failed("security is not evaluative/non-enforcing (USL-14 / SSE-03)")
        return self._passed(governing_law="USL-14")


class SecurityRuntimeReuseCheck(ValidationCheck):
    """SMR-11 / SSE-K4 / §7 — evaluation behaves-as the RUNTIME policy concern by reference."""

    check_id = "security-runtime-reuse"
    severity = Severity.BLOCKING
    description = "Evaluation behaves-as the RUNTIME policy concern (RUNTIME-010) by reference."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.runtime_reuse_valid:
            return self._failed(
                "evaluation does not reuse the RUNTIME policy concern (§7)",
                kind=subject.kind,
                expected=subject.runtime_concern,
                behavior_ref=subject.behavior_ref,
            )
        return self._passed(
            behavior_ref=subject.behavior_ref, runtime_concern=subject.runtime_concern
        )


class SecurityDataByReferenceCheck(ValidationCheck):
    """USL-11 / SSE-06 / SMR-13 — confidentiality/integrity data references DATA-014 by ref."""

    check_id = "security-data-by-reference"
    severity = Severity.BLOCKING
    description = "Data references DF-2/DATA-014 (SMR-13, by reference; USL-11 / SSE-06)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not (subject.data_by_reference and subject.data_security_reuse):
            return self._failed("a data reference is not a valid DF-2/DATA-014 reference")
        return self._passed(data_refs=len(subject.data_refs))


class SecurityPolicyInformedCheck(ValidationCheck):
    """SMR-08 / SOR-08 — every informing-policy reference is a valid ENG-005 reference."""

    check_id = "security-policy-informed"
    severity = Severity.BLOCKING
    description = "Informing policies referenced by valid ENG-005 references (SMR-08 governed-by)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.policy_informed:
            return self._failed("an informing-policy reference is not a valid ENG-005 reference")
        return self._passed(policy_refs=len(subject.policy_refs))


class SecurityPrecedenceCheck(ValidationCheck):
    """SSE-08 — the security object's evaluation precedence is decidable from its SXH-10 kind."""

    check_id = "security-precedence-decidable"
    severity = Severity.BLOCKING
    description = "Security evaluation precedence is decidable from its SXH-10 kind (SSE-08)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.precedence_decidable:
            return self._failed("security precedence is not decidable (SSE-08)")
        return self._passed(precedence=subject.precedence)


class SecurityLifecycleRecordingCheck(ValidationCheck):
    """SSE-08 / SOV-08 — the security object records a decidable lifecycle state (never silent)."""

    check_id = "security-lifecycle-recording"
    severity = Severity.BLOCKING
    description = "Security records a decidable lifecycle state (SOV-08); transitions recorded."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.records_lifecycle:
            return self._failed("security does not record a lifecycle state (SOV-08)")
        return self._passed(state=subject.lifecycle_state)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / SMI-01 — the security object instantiates exactly one meta-class (SMC-10)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Security instantiates exactly the SMC-10 meta-class (V1)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.meta_class != SECURITY_META_CLASS:
            return self._failed("meta-class is not SMC-10 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / SMI-02 — every relationship used lies within SMR-01…13."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All security relationships are within SMR-01…13 (V2)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside SMR-01…13 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — SMK-01 (typed/identified/object) + SMK-02 (boundary-classified) +
    SMK-05/07 (runtime/data references resolve)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01/02/05/07 hold (typed/identified, boundary-classified, refs resolve) (V3)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("SMK-01 not satisfied (V3)")
        if not subject.boundary_classified:
            return self._failed("SMK-02 not satisfied: security classifies no boundary (V3)")
        if not subject.references_resolve:
            return self._failed("SMK-05/07 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["SMK-01", "SMK-02", "SMK-05", "SMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMK-03 / SMI-04 — the founding graph (classified-by / behaves-as) is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The security object's founding graph is acyclic (V4 / SMK-03)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4 / SMK-03)")
        return self._passed(acyclic=subject.founding_acyclic)


class LifecycleValidCheck(ValidationCheck):
    """V5 / USL-12 — the security object holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Security holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """USL-02 / SMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/DF-2 (incl. DATA-014) referenced, redefined nowhere (USL-02)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (USL-02 / SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (USL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """USL-15 / SSE-04 / C7 — no cryptography/IAM/key-management/protocol/vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete cryptography/IAM/key-management selected (USL-15 / SSE-04)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete cryptography/IAM technology was selected (USL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """USL-13/14/15 / SSE-05/09 / C7 — the security object confers no authority, holds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Security confers no authority and embeds no secret (USL-13/15 / SSE-05/09)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("security confers authority (USL-13 / USL-15 / SSE-09)")
        if subject.embeds_secret:
            return self._failed("security embeds a secret (USL-15 / SSE-05 / RR-07)")
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
    """§17 / AC-7 — the No-Orphan lineage is rooted at SMC-10 and closes to 11-SERVICE."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at SMC-10 and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def security_checks() -> tuple[ValidationCheck, ...]:
    """The full security-layer validation suite (deterministically ordered by the engine)."""
    return (
        SecurityTypedCheck(),
        SecurityIdentifiedCheck(),
        SecurityValueFidelityCheck(),
        SecurityClassifiedCheck(),
        SecurityBoundaryClassifiedCheck(),
        SecurityEvaluativeCheck(),
        SecurityRuntimeReuseCheck(),
        SecurityDataByReferenceCheck(),
        SecurityPolicyInformedCheck(),
        SecurityPrecedenceCheck(),
        SecurityLifecycleRecordingCheck(),
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


def validate_security(
    security: Security,
    trace: SecurityTraceabilityRecord,
    *,
    strict: bool = False,
) -> ServiceValidation:
    """Validate ``security`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = SecurityValidationSubject.from_security(security, trace)
    engine = ValidationEngine(security_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ServiceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "SECURITY_BLUEPRINT_ID",
    "SecurityValidationSubject",
    "security_checks",
    "validate_security",
]
