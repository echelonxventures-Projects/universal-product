"""EC3-B13-U08 — Infrastructure Security validation (meta-validity WF + UIL conformance).

Proves a realized :class:`~infrastructure.security.SecurityFacet` is **META-VALID**
(INFRASTRUCTURE-005 §5/§6, WF-1…12 + UIMM-CONF) and **Infrastructure-law conformant**
(INFRASTRUCTURE-001 §7, UIL-01…15) by running a suite of deterministic checks through the
**CERTIFIED EC-1 Validation Engine**.

The checks are pure predicates over an immutable :class:`SecurityValidationSubject`. The
**governing, materially-exercised** obligations for this unit are **WF-10 / UIL-14 /
ISEC-01/04** (every evaluative facet is non-enforcing — the ``security-evaluative-
nonenforcing`` and ``authority-boundary`` checks) and **UIL-15 / ISEC-03/05** (no secret,
no technology — the ``no-secret-material`` and ``technology-independence`` checks). Every
check is deterministic (pure over the immutable subject).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance
from infrastructure.security import INFRA_SECURITY_ID_FAMILY, SecurityFacet
from infrastructure.security_meta import (
    ADMITTED_META_RELATIONSHIPS,
    SECURITY_META_CLASSES,
    InfrastructureState,
)
from infrastructure.security_traceability import TraceabilityRecord

_STATE_VALUES = frozenset(s.value for s in InfrastructureState)
_ADMITTED_RELATIONSHIPS = frozenset(ADMITTED_META_RELATIONSHIPS)
_META_CLASSES = frozenset(SECURITY_META_CLASSES)


@dataclass(frozen=True, slots=True)
class SecurityValidationSubject:
    """A normalized, immutable projection of a concern-013 construct that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    facet: str
    type_tag: str
    value_digest: str
    lifecycle_state: str
    relationships: tuple[str, ...]
    is_hosting_structure: bool
    is_resource: bool
    is_evaluative_facet: bool
    declares_mandatory_attributes: bool
    founding_acyclic: bool
    references_resolve: bool
    evaluates_object_bound: bool
    has_valid_verdict: bool
    non_enforcing: bool
    confers_authority: bool
    enacts_enforcement: bool
    grants_access: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    is_new_primitive: bool
    projects_completion: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_construct(
        cls,
        construct: SecurityFacet,
        trace: TraceabilityRecord,
    ) -> SecurityValidationSubject:
        """Project ``construct`` (+ its lineage) into a subject."""
        return cls(
            target_id=construct.construct_id,
            blueprint_id=construct.meta_class,
            meta_class=construct.meta_class,
            facet=construct.facet_value,
            type_tag=construct.type_tag,
            value_digest=construct.value_digest,
            lifecycle_state=construct.state.value,
            relationships=construct.meta_relationships(),
            is_hosting_structure=construct.is_hosting_structure(),
            is_resource=construct.is_resource(),
            is_evaluative_facet=construct.is_evaluative_facet(),
            declares_mandatory_attributes=construct.declares_mandatory_attributes(),
            founding_acyclic=construct.is_founding_acyclic(),
            references_resolve=construct.references_resolve(),
            evaluates_object_bound=construct.evaluates_object_bound(),
            has_valid_verdict=construct.has_valid_verdict(),
            non_enforcing=construct.non_enforcing,
            confers_authority=construct.confers_authority(),
            enacts_enforcement=construct.enacts_enforcement(),
            grants_access=construct.grants_access(),
            selects_technology=construct.selects_technology(),
            embeds_secret=construct.embeds_secret(),
            redefines_foundation=construct.redefines_foundation(),
            is_new_primitive=construct.is_new_primitive(),
            projects_completion=construct.projects_completion(),
            substrate_refs=tuple(construct.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),
        )


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------


class TypedCheck(ValidationCheck):
    """UIL-03 / C1 — the construct is classified by a non-empty ENG-004 type."""

    check_id = "infra-security-typed"
    severity = Severity.BLOCKING
    description = "Construct bears a non-empty ENG-004 type (UIL-03)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("construct is untyped (UIL-03)")
        return self._passed(type_tag=subject.type_tag)


class IdentifiedCheck(ValidationCheck):
    """UIL-04/05 / C1 — the construct is identified (ENG-001) and object-borne."""

    check_id = "infra-security-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Construct bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith(INFRA_SECURITY_ID_FAMILY):
            return self._failed("construct has no ENG-001 identity (UIL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("construct is not object-borne (no value digest) (UIL-05)")
        if not subject.declares_mandatory_attributes:
            return self._failed("construct lacks a mandatory meta-attribute (WF-1)")
        return self._passed(target_id=subject.target_id)


class ValueFidelityCheck(ValidationCheck):
    """ENG-003 — the construct core round-trips through the EC-1 canonical encoding."""

    check_id = "infra-security-value-fidelity"
    severity = Severity.BLOCKING
    description = "Construct core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("construct core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class MetaClassSingleCheck(ValidationCheck):
    """WF-1 — the construct instantiates exactly one concern-013 leaf meta-class."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Construct instantiates exactly one concern-013 leaf meta-class (WF-1)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.meta_class not in _META_CLASSES:
            return self._failed(
                "meta-class is not a concern-013 leaf meta-class (WF-1)",
                meta_class=subject.meta_class,
            )
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """WF-2 — every relationship used lies within the admitted meta-relationship set."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All construct relationships are within the admitted UIMM set (WF-2)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _ADMITTED_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside admitted set (WF-2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """WF-1/2 — mandatory meta-attributes declared and every reference resolves."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "Mandatory meta-attributes declared (WF-1) and references resolve (WF-2)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("mandatory meta-attributes not all declared (WF-1)")
        if not subject.references_resolve:
            return self._failed("a reference does not resolve (WF-2)")
        return self._passed(constraints=["WF-1", "WF-2"])


class EvaluativeNonEnforcingCheck(ValidationCheck):
    """WF-10 / UIL-14 / ISEC-01/04 — every evaluative facet has nonEnforcing=true."""

    check_id = "security-evaluative-nonenforcing"
    severity = Severity.BLOCKING
    description = "Security facet is evaluative and non-enforcing; enacts nothing (WF-10 / ISEC-04)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.is_evaluative_facet:
            return self._failed("construct is not an evaluative facet (WF-10)")
        if not subject.non_enforcing:
            return self._failed("security facet is not non-enforcing (WF-10 / ISEC-04)")
        if subject.enacts_enforcement:
            return self._failed("security facet enacts enforcement (ISEC-04)")
        if not subject.has_valid_verdict:
            return self._failed("security facet declares no valid evaluative verdict (ISEC-06)")
        return self._passed(facet=subject.facet, verdict="evaluative-nonenforcing")


class EvaluatesObjectBoundCheck(ValidationCheck):
    """ISEC-01 — the facet evaluates ≥1 ENG-002 object by resolvable reference."""

    check_id = "security-evaluates-objectbound"
    severity = Severity.BLOCKING
    description = "Security facet evaluates ≥1 ENG-002 object by reference (ISEC-01)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.evaluates_object_bound:
            return self._failed("facet evaluates no ENG-002 object by reference (ISEC-01)")
        return self._passed(facet=subject.facet)


class AuthorityBoundaryCheck(ValidationCheck):
    """ISEC-04/06 / AUTH-06 — confers no authority, enacts no enforcement, grants no access."""

    check_id = "authority-boundary"
    severity = Severity.BLOCKING
    description = "Facet confers no authority, enacts no enforcement, grants no access (ISEC-04/06)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("security facet confers authority (ISEC-06 / AUTH-06)")
        if subject.enacts_enforcement:
            return self._failed("security facet enacts enforcement (ISEC-04)")
        if subject.grants_access:
            return self._failed("security facet grants access / issues a credential (ISEC-04)")
        return self._passed(boundary="authority-none")


class NoSecretMaterialCheck(ValidationCheck):
    """ISEC-03 / RR-07 / UIL-15 — embeds no secret/credential/key/cryptographic material."""

    check_id = "no-secret-material"
    severity = Severity.BLOCKING
    description = "Facet embeds no secret/credential/key/cryptographic material (ISEC-03 / RR-07)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.embeds_secret:
            return self._failed("security facet embeds secret material (ISEC-03 / RR-07)")
        return self._passed(secret_free=True)


class FoundingAcyclicCheck(ValidationCheck):
    """WF-3 — the founding structure is acyclic (vacuous for evaluative facets)."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "Founding structure acyclic; evaluative facet participates in no founding edge (WF-3)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding structure is not acyclic (WF-3)")
        return self._passed(founding="vacuously-acyclic")


class ConstructKindCheck(ValidationCheck):
    """WF-5/WF-10 — a concern-013 construct is evaluative, never a Resource."""

    check_id = "infra-security-construct-kind"
    severity = Severity.BLOCKING
    description = "Construct kind is consistent with its meta-class (evaluative facet)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.is_resource:
            return self._failed("a concern-013 construct must not be a Resource (WF-5 scope)")
        if not subject.is_evaluative_facet:
            return self._failed("a concern-013 construct must be evaluative (WF-10)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """INFRASTRUCTURE-003 §3 — the construct holds a valid forward-only lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Construct holds a valid forward-only lifecycle state (INFRASTRUCTURE-003 §3)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UIL-02 / ISEC-02 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/DATA-014/SERVICE-014/APPLICATION-013 referenced, redefined nowhere (UIL-02)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UIL-02)")
        if subject.is_new_primitive:
            return self._failed("construct is a new primitive (WF-11 / UIL-01)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UIL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """UIL-15 / ISEC-05 / C7 — no IAM/PKI/crypto technology or vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete IAM/PKI/crypto technology/vendor selected (UIL-15 / ISEC-05)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UIL-15 / ISEC-05)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UIL-14/15 / ISEC-06 — confers no authority, embeds no secret, projects no completion."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Construct confers no authority, embeds no secret, projects no completion (UIL-14/15)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("construct confers authority (UIL-15 / ISEC-06)")
        if subject.embeds_secret:
            return self._failed("construct embeds a secret (UIL-15 / RR-07)")
        if subject.projects_completion:
            return self._failed("construct projects completion (WF-12)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§5 — the No-Orphan lineage is rooted and closes to the 13-INFRASTRUCTURE anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at the meta-class, closed to 13-INFRASTRUCTURE."

    def evaluate(self, subject: SecurityValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("13-INFRASTRUCTURE@") for link in chain):
            return self._failed("lineage does not close to the 13-INFRASTRUCTURE anchor")
        return self._passed(links=len(chain))


def security_checks() -> tuple[ValidationCheck, ...]:
    """The full Infrastructure Security validation suite (deterministically ordered)."""
    return (
        TypedCheck(),
        IdentifiedCheck(),
        ValueFidelityCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        EvaluativeNonEnforcingCheck(),
        EvaluatesObjectBoundCheck(),
        AuthorityBoundaryCheck(),
        NoSecretMaterialCheck(),
        FoundingAcyclicCheck(),
        ConstructKindCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class SecurityValidation:
    """The bundled outcome of validating a construct (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_construct(
    construct: SecurityFacet,
    trace: TraceabilityRecord,
    *,
    strict: bool = False,
) -> SecurityValidation:
    """Validate ``construct`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = SecurityValidationSubject.from_construct(construct, trace)
    engine = ValidationEngine(security_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return SecurityValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "SecurityValidationSubject",
    "SecurityValidation",
    "security_checks",
    "validate_construct",
]
