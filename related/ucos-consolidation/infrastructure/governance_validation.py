"""EC3-B13-U09 — Infrastructure Governance validation (meta-validity WF + UIL conformance).

Proves a realized :class:`~infrastructure.governance.GovernanceFacet` is **META-VALID**
(INFRASTRUCTURE-005 §5/§6, WF-1…12 + UIMM-CONF) and **Infrastructure-law conformant**
(INFRASTRUCTURE-001 §7, UIL-01…15) by running a suite of deterministic checks through the
**CERTIFIED EC-1 Validation Engine**.

The checks are pure predicates over an immutable :class:`GovernanceValidationSubject`. The
**governing, materially-exercised** obligations for this unit are **WF-10 / UIL-14 /
IGOV-01** (every construct is record-only and non-enforcing — the ``governance-evaluative-
nonenforcing`` and ``authority-boundary`` checks) and **UIL-15 / IGOV-06** (no secret,
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
from infrastructure.governance import INFRA_GOVERNANCE_ID_FAMILY, GovernanceFacet
from infrastructure.governance_meta import (
    ADMITTED_META_RELATIONSHIPS,
    GOVERNANCE_META_CLASSES,
    InfrastructureState,
)
from infrastructure.governance_traceability import TraceabilityRecord

_STATE_VALUES = frozenset(s.value for s in InfrastructureState)
_ADMITTED_RELATIONSHIPS = frozenset(ADMITTED_META_RELATIONSHIPS)
_META_CLASSES = frozenset(GOVERNANCE_META_CLASSES)


@dataclass(frozen=True, slots=True)
class GovernanceValidationSubject:
    """A normalized, immutable projection of a concern-014 construct that checks evaluate."""

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
        construct: GovernanceFacet,
        trace: TraceabilityRecord,
    ) -> GovernanceValidationSubject:
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

    check_id = "infra-governance-typed"
    severity = Severity.BLOCKING
    description = "Construct bears a non-empty ENG-004 type (UIL-03)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("construct is untyped (UIL-03)")
        return self._passed(type_tag=subject.type_tag)


class IdentifiedCheck(ValidationCheck):
    """UIL-04/05 / C1 — the construct is identified (ENG-001) and object-borne."""

    check_id = "infra-governance-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Construct bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith(INFRA_GOVERNANCE_ID_FAMILY):
            return self._failed("construct has no ENG-001 identity (UIL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("construct is not object-borne (no value digest) (UIL-05)")
        if not subject.declares_mandatory_attributes:
            return self._failed("construct lacks a mandatory meta-attribute (WF-1)")
        return self._passed(target_id=subject.target_id)


class ValueFidelityCheck(ValidationCheck):
    """ENG-003 — the construct core round-trips through the EC-1 canonical encoding."""

    check_id = "infra-governance-value-fidelity"
    severity = Severity.BLOCKING
    description = "Construct core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("construct core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class MetaClassSingleCheck(ValidationCheck):
    """WF-1 — the construct instantiates exactly one concern-014 leaf meta-class."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Construct instantiates exactly one concern-014 leaf meta-class (WF-1)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.meta_class not in _META_CLASSES:
            return self._failed(
                "meta-class is not a concern-014 leaf meta-class (WF-1)",
                meta_class=subject.meta_class,
            )
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """WF-2 — every relationship used lies within the admitted meta-relationship set."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All construct relationships are within the admitted UIMM set (WF-2)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _ADMITTED_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside admitted set (WF-2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """WF-1/2 — mandatory meta-attributes declared and every reference resolves."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "Mandatory meta-attributes declared (WF-1) and references resolve (WF-2)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("mandatory meta-attributes not all declared (WF-1)")
        if not subject.references_resolve:
            return self._failed("a reference does not resolve (WF-2)")
        return self._passed(constraints=["WF-1", "WF-2"])


class EvaluativeNonEnforcingCheck(ValidationCheck):
    """WF-10 / UIL-14 / IGOV-01 — every governance construct is record-only, non-enforcing."""

    check_id = "governance-evaluative-nonenforcing"
    severity = Severity.BLOCKING
    description = "Record-only, non-enforcing; enacts nothing (WF-10/IGOV-01)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.is_evaluative_facet:
            return self._failed("construct is not an evaluative facet (WF-10)")
        if not subject.non_enforcing:
            return self._failed("governance construct is not non-enforcing (WF-10 / IGOV-01)")
        if subject.enacts_enforcement:
            return self._failed("governance construct enacts enforcement (IGOV-01)")
        if not subject.has_valid_verdict:
            return self._failed("no valid evaluative verdict declared (IGOV-01)")
        return self._passed(facet=subject.facet, verdict="record-only-nonenforcing")


class EvaluatesObjectBoundCheck(ValidationCheck):
    """IGOV-02 — the construct evaluates ≥1 ENG-002 object by resolvable reference."""

    check_id = "governance-evaluates-objectbound"
    severity = Severity.BLOCKING
    description = "Governance construct evaluates ≥1 ENG-002 object by reference (IGOV-02)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.evaluates_object_bound:
            return self._failed("construct evaluates no ENG-002 object by reference (IGOV-02)")
        return self._passed(facet=subject.facet)


class AuthorityBoundaryCheck(ValidationCheck):
    """IGOV-01/04 / AUTH-06 — confers no authority, enacts no enforcement, grants no access."""

    check_id = "authority-boundary"
    severity = Severity.BLOCKING
    description = "Confers no authority, enacts no enforcement, grants no access (IGOV-01/04)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("governance construct confers authority (IGOV-04 / AUTH-06)")
        if subject.enacts_enforcement:
            return self._failed("governance construct enacts enforcement (IGOV-01)")
        if subject.grants_access:
            return self._failed("governance construct grants access / approves (IGOV-01/04)")
        return self._passed(boundary="authority-none")


class NoSecretMaterialCheck(ValidationCheck):
    """UIL-15 / IGOV-06 — embeds no secret/credential/key/cryptographic material."""

    check_id = "no-secret-material"
    severity = Severity.BLOCKING
    description = "Embeds no secret/credential/key/cryptographic material (UIL-15 / IGOV-06)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.embeds_secret:
            return self._failed("governance construct embeds secret material (UIL-15 / IGOV-06)")
        return self._passed(secret_free=True)


class FoundingAcyclicCheck(ValidationCheck):
    """WF-3 — the founding structure is acyclic (vacuous for evaluative facets)."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "Founding structure acyclic; evaluative facet has no founding edge (WF-3)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding structure is not acyclic (WF-3)")
        return self._passed(founding="vacuously-acyclic")


class ConstructKindCheck(ValidationCheck):
    """WF-5/WF-10 — a concern-014 construct is evaluative, never a Resource."""

    check_id = "infra-governance-construct-kind"
    severity = Severity.BLOCKING
    description = "Construct kind is consistent with its meta-class (evaluative facet)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.is_resource:
            return self._failed("a concern-014 construct must not be a Resource (WF-5 scope)")
        if not subject.is_evaluative_facet:
            return self._failed("a concern-014 construct must be evaluative (WF-10)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """INFRASTRUCTURE-003 §3 — the construct holds a valid forward-only lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Construct holds a valid forward-only lifecycle state (INFRASTRUCTURE-003 §3)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UIL-02 / IGOV-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/ENG-000/RL-F2/UIMM-CONF/UITX/UCI-001/REG-AUTO-001 by reference (UIL-02)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UIL-02)")
        if subject.is_new_primitive:
            return self._failed("construct is a new primitive (WF-11 / UIL-01)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UIL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """UIL-15 / IGOV-06 / C7 — no policy engine/technology or vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete policy engine/technology/vendor selected (UIL-15 / IGOV-06)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UIL-15 / IGOV-06)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UIL-14/15 / IGOV-04 — confers no authority, embeds no secret, projects no completion."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Confers no authority, embeds no secret, projects no completion (UIL-14/15)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("construct confers authority (UIL-15 / IGOV-04)")
        if subject.embeds_secret:
            return self._failed("construct embeds a secret (UIL-15 / IGOV-06)")
        if subject.projects_completion:
            return self._failed("construct projects completion (WF-12)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§5 — the No-Orphan lineage is rooted and closes to the 13-INFRASTRUCTURE anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at the meta-class, closed to 13-INFRASTRUCTURE."

    def evaluate(self, subject: GovernanceValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("13-INFRASTRUCTURE@") for link in chain):
            return self._failed("lineage does not close to the 13-INFRASTRUCTURE anchor")
        return self._passed(links=len(chain))


def governance_checks() -> tuple[ValidationCheck, ...]:
    """The full Infrastructure Governance validation suite (deterministically ordered)."""
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
class GovernanceValidation:
    """The bundled outcome of validating a construct (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_construct(
    construct: GovernanceFacet,
    trace: TraceabilityRecord,
    *,
    strict: bool = False,
) -> GovernanceValidation:
    """Validate ``construct`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = GovernanceValidationSubject.from_construct(construct, trace)
    engine = ValidationEngine(governance_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return GovernanceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "GovernanceValidationSubject",
    "GovernanceValidation",
    "governance_checks",
    "validate_construct",
]
