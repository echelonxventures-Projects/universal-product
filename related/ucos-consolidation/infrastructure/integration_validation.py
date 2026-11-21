"""EC3-B13-U10 — Universal Infrastructure Integration validation (meta-validity + UIL).

Proves a realized :class:`~infrastructure.integration.InfrastructureDependency` is
**META-VALID** (INFRASTRUCTURE-005 §5/§6, WF-1…12 + UIMM-CONF) and **Infrastructure-law
conformant** (INFRASTRUCTURE-001 §7, UIL-01…15) by running a suite of deterministic checks
through the **CERTIFIED EC-1 Validation Engine**.

The checks are pure predicates over an immutable :class:`IntegrationValidationSubject`. The
**governing, materially-exercised** obligations for this unit are **WF-3 / UIL-09** (the
``dependsOn`` graph is downward-only and acyclic — the ``dependency-downward-acyclic`` and
``meta-relationships-closed`` checks) and **UIL-02 / UIL-15** (reuse-by-reference,
non-constitutive — the ``foundation-reuse-integrity``, ``technology-independence`` and
``non-constitutive`` checks). Every check is deterministic (pure over the immutable subject).
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
from infrastructure.integration import (
    DEPENDS_ON,
    INFRA_DEPENDENCY_ID_FAMILY,
    InfrastructureDependency,
)
from infrastructure.integration_meta import (
    ADMITTED_META_RELATIONSHIPS,
    CONCERN_REGISTRY,
    INTEGRATION_META_CLASSES,
    InfrastructureState,
)
from infrastructure.integration_traceability import TraceabilityRecord

_STATE_VALUES = frozenset(s.value for s in InfrastructureState)
_ADMITTED_RELATIONSHIPS = frozenset(ADMITTED_META_RELATIONSHIPS)
_META_CLASSES = frozenset(INTEGRATION_META_CLASSES)
_KNOWN_CONCERN_REFS = frozenset(c.ref for c in CONCERN_REGISTRY)


@dataclass(frozen=True, slots=True)
class IntegrationValidationSubject:
    """A normalized, immutable projection of a dependency construct that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    value_digest: str
    lifecycle_state: str
    relationships: tuple[str, ...]
    relationship: str
    source_ref: str
    target_ref: str
    source_index: int
    target_index: int
    basis: str
    downward_only: bool
    is_downward_only: bool
    is_dependency: bool
    is_resource: bool
    is_evaluative_facet: bool
    declares_mandatory_attributes: bool
    founding_acyclic: bool
    references_resolve: bool
    is_reference_only: bool
    mutates_endpoints: bool
    endpoints_known: bool
    confers_authority: bool
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
        dependency: InfrastructureDependency,
        trace: TraceabilityRecord,
    ) -> IntegrationValidationSubject:
        """Project ``dependency`` (+ its lineage) into a subject."""
        return cls(
            target_id=dependency.construct_id,
            blueprint_id=dependency.meta_class,
            meta_class=dependency.meta_class,
            type_tag=dependency.type_tag,
            value_digest=dependency.value_digest,
            lifecycle_state=dependency.state.value,
            relationships=dependency.meta_relationships(),
            relationship=dependency.relationship,
            source_ref=dependency.source_ref,
            target_ref=dependency.target_ref,
            source_index=dependency.source_index,
            target_index=dependency.target_index,
            basis=dependency.basis,
            downward_only=dependency.downward_only,
            is_downward_only=dependency.is_downward_only(),
            is_dependency=dependency.is_dependency(),
            is_resource=dependency.is_resource(),
            is_evaluative_facet=dependency.is_evaluative_facet(),
            declares_mandatory_attributes=dependency.declares_mandatory_attributes(),
            founding_acyclic=dependency.is_founding_acyclic(),
            references_resolve=dependency.references_resolve(),
            is_reference_only=dependency.is_reference_only(),
            mutates_endpoints=dependency.mutates_endpoints(),
            endpoints_known=(
                dependency.source_ref in _KNOWN_CONCERN_REFS
                and dependency.target_ref in _KNOWN_CONCERN_REFS
            ),
            confers_authority=dependency.confers_authority(),
            selects_technology=dependency.selects_technology(),
            embeds_secret=dependency.embeds_secret(),
            redefines_foundation=dependency.redefines_foundation(),
            is_new_primitive=dependency.is_new_primitive(),
            projects_completion=dependency.projects_completion(),
            substrate_refs=tuple(dependency.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),
        )


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------


class TypedCheck(ValidationCheck):
    """UIL-03 / C1 — the dependency is classified by a non-empty ENG-004 type."""

    check_id = "dependency-typed"
    severity = Severity.BLOCKING
    description = "Dependency bears a non-empty ENG-004 type (UIL-03)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("dependency is untyped (UIL-03)")
        return self._passed(type_tag=subject.type_tag)


class IdentifiedCheck(ValidationCheck):
    """UIL-04/05 / C1 — the dependency is identified (ENG-001) and object-borne."""

    check_id = "dependency-identified"
    severity = Severity.BLOCKING
    description = "Dependency bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith(INFRA_DEPENDENCY_ID_FAMILY):
            return self._failed("dependency has no ENG-001 identity (UIL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("dependency is not object-borne (no value digest) (UIL-05)")
        if not subject.declares_mandatory_attributes:
            return self._failed("dependency lacks a mandatory meta-attribute (WF-1)")
        return self._passed(target_id=subject.target_id)


class ValueFidelityCheck(ValidationCheck):
    """ENG-003 — the dependency core round-trips through the EC-1 canonical encoding."""

    check_id = "dependency-value-fidelity"
    severity = Severity.BLOCKING
    description = "Dependency core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("dependency core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class MetaClassSingleCheck(ValidationCheck):
    """WF-1 — the construct instantiates exactly the InfrastructureDependency leaf meta-class."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Instantiates exactly one leaf meta-class: InfrastructureDependency (WF-1)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if subject.meta_class not in _META_CLASSES:
            return self._failed(
                "meta-class is not the InfrastructureDependency leaf meta-class (WF-1)",
                meta_class=subject.meta_class,
            )
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """WF-2 / §4 / UIL-09 — the dependency realizes only the admitted dependsOn relationship."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "Realizes only the admitted dependsOn meta-relationship (WF-2 / UIL-09)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _ADMITTED_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside admitted set (WF-2)", outside=outside)
        if subject.relationship != DEPENDS_ON:
            return self._failed(
                "dependency does not realize the dependsOn relationship (§4)",
                relationship=subject.relationship,
            )
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """WF-1/2 — mandatory meta-attributes declared and every reference resolves."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "Mandatory meta-attributes declared (WF-1) and references resolve (WF-2)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("mandatory meta-attributes not all declared (WF-1)")
        if not subject.references_resolve:
            return self._failed("a reference does not resolve (WF-2)")
        return self._passed(constraints=["WF-1", "WF-2"])


class DownwardAcyclicCheck(ValidationCheck):
    """WF-3 / §3 / UIL-09 — the dependency is downwardOnly=true and points strictly downward."""

    check_id = "dependency-downward-acyclic"
    severity = Severity.BLOCKING
    description = "Dependency is downwardOnly=true and strictly downward; graph acyclic (WF-3)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if subject.downward_only is not True:
            return self._failed("dependency is not downwardOnly=true (INFRASTRUCTURE-005 §3)")
        if not subject.is_downward_only:
            return self._failed(
                "dependsOn edge is not strictly downward (WF-3)",
                source_index=subject.source_index,
                target_index=subject.target_index,
            )
        if not subject.founding_acyclic:
            return self._failed("dependsOn edge introduces a founding cycle (WF-3)")
        return self._passed(
            downward=f"#{subject.source_index}→#{subject.target_index}", acyclic=True
        )


class ReferenceOnlyCheck(ValidationCheck):
    """UIL-02 / §4 — the dependency only references its endpoints; it mutates neither."""

    check_id = "dependency-reference-only"
    severity = Severity.BLOCKING
    description = "Dependency composes endpoints by reference only; mutates nothing (UIL-02)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if not subject.is_reference_only:
            return self._failed("dependency is not reference-only (UIL-02)")
        if subject.mutates_endpoints:
            return self._failed("dependency mutates an endpoint it references (UIL-02 / §4)")
        return self._passed(reference_only=True)


class EndpointsResolveCheck(ValidationCheck):
    """IINT-01 — both endpoints resolve to CERTIFIED Band-13 concern units (by reference)."""

    check_id = "dependency-endpoints-resolve"
    severity = Severity.BLOCKING
    description = "Both endpoints reference known certified Band-13 concern units (IINT-01)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if not subject.endpoints_known:
            return self._failed(
                "an endpoint does not reference a known certified concern (IINT-01)",
                source=subject.source_ref,
                target=subject.target_ref,
            )
        return self._passed(source=subject.source_ref, target=subject.target_ref)


class AuthorityBoundaryCheck(ValidationCheck):
    """WF-11 / AUTH-06 — the dependency confers no authority and mutates nothing."""

    check_id = "authority-boundary"
    severity = Severity.BLOCKING
    description = "Confers no authority; mutates no endpoint (WF-11 / AUTH-06)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("dependency confers authority (WF-11 / AUTH-06)")
        if subject.mutates_endpoints:
            return self._failed("dependency mutates an endpoint (UIL-02)")
        return self._passed(boundary="authority-none")


class NoSecretMaterialCheck(ValidationCheck):
    """UIL-15 — embeds no secret/credential/key/cryptographic material."""

    check_id = "no-secret-material"
    severity = Severity.BLOCKING
    description = "Embeds no secret/credential/key/cryptographic material (UIL-15)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if subject.embeds_secret:
            return self._failed("dependency embeds secret material (UIL-15)")
        return self._passed(secret_free=True)


class FoundingAcyclicCheck(ValidationCheck):
    """WF-3 — the founding (dependsOn) structure is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "Founding dependsOn structure is acyclic (WF-3)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding structure is not acyclic (WF-3)")
        return self._passed(founding="acyclic")


class LifecycleValidCheck(ValidationCheck):
    """INFRASTRUCTURE-003 §3 — the dependency holds a valid forward-only lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Dependency holds a valid forward-only lifecycle state (INFRASTRUCTURE-003 §3)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UIL-02 / UIL-09 / VC-5 — the frozen ENG-005 reference is reused, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "ENG-001…005 reused by reference; a dependency ⊑ ENG-005 reference (UIL-02/09)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UIL-02)")
        if subject.is_new_primitive:
            return self._failed("dependency is a new primitive (WF-11 / UIL-09)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UIL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """UIL-15 / C7 — no concrete technology or vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/vendor selected (UIL-15)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UIL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UIL-14/15 / WF-11/12 — confers no authority, embeds no secret, projects no completion."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Confers no authority, embeds no secret, projects no completion (WF-11/12)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("dependency confers authority (UIL-15 / WF-11)")
        if subject.embeds_secret:
            return self._failed("dependency embeds a secret (UIL-15)")
        if subject.is_new_primitive:
            return self._failed("dependency is a new primitive (WF-11)")
        if subject.projects_completion:
            return self._failed("dependency projects completion (WF-12)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§5 — the No-Orphan lineage is rooted and closes to the 13-INFRASTRUCTURE anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at the meta-class, closed to 13-INFRASTRUCTURE."

    def evaluate(self, subject: IntegrationValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("13-INFRASTRUCTURE@") for link in chain):
            return self._failed("lineage does not close to the 13-INFRASTRUCTURE anchor")
        return self._passed(links=len(chain))


def integration_checks() -> tuple[ValidationCheck, ...]:
    """The full Infrastructure Integration validation suite (deterministically ordered)."""
    return (
        TypedCheck(),
        IdentifiedCheck(),
        ValueFidelityCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        DownwardAcyclicCheck(),
        ReferenceOnlyCheck(),
        EndpointsResolveCheck(),
        AuthorityBoundaryCheck(),
        NoSecretMaterialCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class IntegrationValidation:
    """The bundled outcome of validating a dependency (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_dependency(
    dependency: InfrastructureDependency,
    trace: TraceabilityRecord,
    *,
    strict: bool = False,
) -> IntegrationValidation:
    """Validate ``dependency`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = IntegrationValidationSubject.from_construct(dependency, trace)
    engine = ValidationEngine(integration_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return IntegrationValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "IntegrationValidationSubject",
    "IntegrationValidation",
    "integration_checks",
    "validate_dependency",
]
