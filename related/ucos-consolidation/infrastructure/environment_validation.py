"""EC3-B13-U05 — Environment & Provisioning validation (meta-validity WF + UIL conformance).

This module proves a realized Environment & Provisioning construct (any of the six leaf
meta-classes :class:`~infrastructure.environment.Locality`,
:class:`~infrastructure.environment.IsolationBoundary`,
:class:`~infrastructure.environment.Node`, :class:`~infrastructure.environment.Cluster`,
:class:`~infrastructure.environment.Environment`,
:class:`~infrastructure.environment.ProvisioningProcess`) is **META-VALID**
(INFRASTRUCTURE-005 §5/§6, WF-1…12 + UIMM-CONF) and **Infrastructure-law conformant**
(INFRASTRUCTURE-001 §7, UIL-01…15) by running a suite of deterministic checks through the
**CERTIFIED EC-1 Validation Engine** (:class:`engine.validation.executor.ValidationEngine`)
and enforcing the EC-1 acceptance gate (:func:`engine.validation.gates.enforce_acceptance`).

The checks are pure predicates over an immutable :class:`EnvValidationSubject` — a
type-independent projection that carries per-construct ``applies_*`` flags so a single
suite validates all six meta-classes: an obligation scoped to a construct it does not
apply to (e.g. the single-boundary rule on a Locality) is satisfied vacuously. The
**governing, materially-exercised** obligations for this unit are **WF-4 / UIL-07** (an
Environment declares exactly one isolation boundary — C4), **WF-3 / UIL-09** (the
containment founding graph is acyclic — C5), and **WF-6 / UIL-10** (a ProvisioningProcess
binds an RL-F2 workflow by reference — C6). Every check is **blocking**.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- EC-1 reuse by reference (UIL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance
from infrastructure.environment import INFRA_ENV_ID_FAMILY, _InfraConstruct
from infrastructure.environment_meta import (
    ADMITTED_META_RELATIONSHIPS,
    ENVIRONMENT_META_CLASSES,
    InfrastructureState,
)
from infrastructure.environment_traceability import TraceabilityRecord

_STATE_VALUES = frozenset(s.value for s in InfrastructureState)
_ADMITTED_RELATIONSHIPS = frozenset(ADMITTED_META_RELATIONSHIPS)
_META_CLASSES = frozenset(ENVIRONMENT_META_CLASSES)


@dataclass(frozen=True, slots=True)
class EnvValidationSubject:
    """A normalized, immutable projection of any concern-011 construct that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1 ``ValidationEngine``
    consumes) plus the construct's meta-facts and per-construct ``applies_*`` flags. Holds
    no runtime state and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
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
    containment_acyclic: bool
    applies_locality: bool
    located_by_reference: bool
    applies_boundary: bool
    declares_single_boundary: bool
    applies_workflow: bool
    binds_runtime_workflow: bool
    applies_contains: bool
    contains_count: int
    applies_provisions: bool
    provisions_count: int
    confers_authority: bool
    enacts_enforcement: bool
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
        construct: _InfraConstruct,
        trace: TraceabilityRecord,
        *,
        containment_acyclic: bool = True,
    ) -> EnvValidationSubject:
        """Project ``construct`` (+ its lineage + composition acyclicity) into a subject."""
        meta_class = construct.meta_class
        is_hosting = construct.is_hosting_structure()
        applies_boundary = meta_class == "Environment"
        applies_workflow = meta_class == "ProvisioningProcess"
        applies_provisions = meta_class == "ProvisioningProcess"
        return cls(
            target_id=construct.construct_id,
            blueprint_id=meta_class,
            meta_class=meta_class,
            type_tag=construct.type_tag,  # type: ignore[attr-defined]
            value_digest=construct.value_digest,
            lifecycle_state=construct.state.value,  # type: ignore[attr-defined]
            relationships=construct.meta_relationships(),
            is_hosting_structure=is_hosting,
            is_resource=construct.is_resource(),
            is_evaluative_facet=construct.is_evaluative_facet(),
            declares_mandatory_attributes=construct.declares_mandatory_attributes(),
            founding_acyclic=construct.is_founding_acyclic(),
            references_resolve=construct.references_resolve(),
            containment_acyclic=containment_acyclic,
            applies_locality=is_hosting,
            located_by_reference=(construct.located_by_reference() if is_hosting else True),  # type: ignore[attr-defined]
            applies_boundary=applies_boundary,
            declares_single_boundary=(
                construct.declares_single_boundary() if applies_boundary else True  # type: ignore[attr-defined]
            ),
            applies_workflow=applies_workflow,
            binds_runtime_workflow=(
                construct.binds_runtime_workflow() if applies_workflow else True  # type: ignore[attr-defined]
            ),
            applies_contains=is_hosting,
            contains_count=(len(construct.contains) if is_hosting else 0),  # type: ignore[attr-defined]
            applies_provisions=applies_provisions,
            provisions_count=(len(construct.provisions) if applies_provisions else 0),  # type: ignore[attr-defined]
            confers_authority=construct.confers_authority(),
            enacts_enforcement=construct.enacts_enforcement(),
            selects_technology=construct.selects_technology(),
            embeds_secret=construct.embeds_secret(),
            redefines_foundation=construct.redefines_foundation(),
            is_new_primitive=construct.is_new_primitive(),
            projects_completion=construct.projects_completion(),
            substrate_refs=tuple(construct.to_dict()["substrate_refs"]),  # type: ignore[attr-defined]
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Infrastructure-layer validation checks (each maps to explicit WF*/UIL*/IENV* obligations)
# ---------------------------------------------------------------------------


class EnvTypedCheck(ValidationCheck):
    """UIL-03 / C1 — the construct is classified by a non-empty ENG-004 type."""

    check_id = "infra-env-typed"
    severity = Severity.BLOCKING
    description = "Construct bears a non-empty ENG-004 type (UIL-03)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("construct is untyped (UIL-03)")
        return self._passed(type_tag=subject.type_tag)


class EnvIdentifiedCheck(ValidationCheck):
    """UIL-04/05 / C1 — the construct is identified (ENG-001) and object-borne."""

    check_id = "infra-env-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Construct bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith(INFRA_ENV_ID_FAMILY):
            return self._failed("construct has no ENG-001 identity (UIL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("construct is not object-borne (no value digest) (UIL-05)")
        if not subject.declares_mandatory_attributes:
            return self._failed("construct lacks a mandatory meta-attribute (WF-1)")
        return self._passed(target_id=subject.target_id)


class EnvValueFidelityCheck(ValidationCheck):
    """ENG-003 — the construct core round-trips through the EC-1 canonical encoding."""

    check_id = "infra-env-value-fidelity"
    severity = Severity.BLOCKING
    description = "Construct core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("construct core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class MetaClassSingleCheck(ValidationCheck):
    """WF-1 — the construct instantiates exactly one concern-011 leaf meta-class."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Construct instantiates exactly one concern-011 leaf meta-class (WF-1)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if subject.meta_class not in _META_CLASSES:
            return self._failed(
                "meta-class is not a concern-011 leaf meta-class (WF-1)",
                meta_class=subject.meta_class,
            )
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """WF-2 — every relationship used lies within the admitted meta-relationship set."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All construct relationships are within the admitted UIMM set (WF-2)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _ADMITTED_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside admitted set (WF-2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """WF-1/2 — mandatory meta-attributes declared and every reference resolves."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "Mandatory meta-attributes declared (WF-1) and references resolve (WF-2)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("mandatory meta-attributes not all declared (WF-1)")
        if not subject.references_resolve:
            return self._failed("a reference does not resolve (WF-2)")
        return self._passed(constraints=["WF-1", "WF-2"])


class FoundingAcyclicCheck(ValidationCheck):
    """WF-3 — the construct's own founding graph is acyclic (references are ids)."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The construct's founding graph is acyclic (WF-3)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (WF-3)")
        return self._passed()


class ContainmentAcyclicCheck(ValidationCheck):
    """WF-3 / UIL-09 / IENV-03 / C5 — the composition containment graph is acyclic.

    A governing, materially-exercised obligation: node/cluster/environment containment is
    founding-acyclic and expressed as ENG-005 references (no new connection construct).
    """

    check_id = "infra-env-containment-acyclic"
    severity = Severity.BLOCKING
    description = "Node/cluster/environment containment is acyclic ENG-005 refs (WF-3 / IENV-03)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if not subject.containment_acyclic:
            return self._failed("containment founding graph is not acyclic (WF-3 / IENV-03)")
        return self._passed()


class EnvBoundedIsolatedCheck(ValidationCheck):
    """WF-4 / UIL-07 / IENV-01 / C4 — an Environment declares exactly one isolation boundary.

    THE governing, materially-exercised Environment rule (vacuous for the other five
    constructs, which declare no boundary).
    """

    check_id = "infra-env-bounded-isolated"
    severity = Severity.BLOCKING
    description = "Every Environment declares exactly one isolation boundary (WF-4 / UIL-07)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if subject.applies_boundary and not subject.declares_single_boundary:
            return self._failed("environment does not declare its isolation boundary (WF-4)")
        return self._passed(applies=subject.applies_boundary)


class LocatedCheck(ValidationCheck):
    """INFRASTRUCTURE-005 §3 — every HostingStructure declares its locality by reference."""

    check_id = "infra-env-located"
    severity = Severity.BLOCKING
    description = "Every HostingStructure declares its locality by an ENG-005 reference."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if subject.applies_locality and not subject.located_by_reference:
            return self._failed("hosting structure omits its locality reference (WF-1)")
        return self._passed(applies=subject.applies_locality)


class ContainmentByReferenceCheck(ValidationCheck):
    """UIL-09 / WF-2 / IENV-03 — containment/provisioning uses ≥1 typed ENG-005 reference."""

    check_id = "infra-env-containment-by-reference"
    severity = Severity.BLOCKING
    description = "Containment/provisioning uses ≥1 typed ENG-005 reference (UIL-09 / WF-2)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if subject.applies_contains and subject.contains_count < 1:
            return self._failed("hosting structure contains nothing (multiplicity 1..*; WF-2)")
        if subject.applies_provisions and subject.provisions_count < 1:
            return self._failed("provisioning process provisions nothing (multiplicity 1..*; WF-2)")
        applies_ref = subject.applies_contains or subject.applies_provisions
        if applies_ref and not subject.references_resolve:
            return self._failed("a containment/provisioning reference does not resolve (WF-2)")
        return self._passed(
            contains_count=subject.contains_count, provisions_count=subject.provisions_count
        )


class ProvisioningBindsRuntimeCheck(ValidationCheck):
    """WF-6 / UIL-10 / IENV-04 / C6 — a ProvisioningProcess binds an RL-F2 workflow by reference.

    THE governing, materially-exercised ProvisioningProcess rule (vacuous for the other five
    constructs): it re-founds no PLATFORM-012/013 and defines no new lifecycle model.
    """

    check_id = "infra-env-provisioning-binds-runtime"
    severity = Severity.BLOCKING
    description = "Every ProvisioningProcess binds an RL-F2 workflow by reference (WF-6 / UIL-10)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if subject.applies_workflow and not subject.binds_runtime_workflow:
            return self._failed("provisioning process does not bind an RL-F2 workflow (WF-6)")
        return self._passed(applies=subject.applies_workflow)


class ConstructKindCheck(ValidationCheck):
    """WF-5/WF-10 N/A — no concern-011 construct is a Resource or an EvaluativeFacet."""

    check_id = "infra-env-construct-kind"
    severity = Severity.BLOCKING
    description = "Construct is neither a Resource (WF-5) nor an EvaluativeFacet (WF-10)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if subject.is_resource:
            return self._failed("a concern-011 construct must not be a Resource (WF-5 scope)")
        if subject.is_evaluative_facet:
            return self._failed("a concern-011 construct must not be an EvaluativeFacet (WF-10)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """INFRASTRUCTURE-003 §3 — the construct holds a valid forward-only lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Construct holds a valid forward-only lifecycle state (INFRASTRUCTURE-003 §3)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UIL-02 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2 referenced, redefined nowhere (UIL-02)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UIL-02)")
        if subject.is_new_primitive:
            return self._failed("construct is a new primitive (WF-11 / UIL-01)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UIL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """UIL-15 / IENV-06 / C7 — no IaC/cloud/orchestrator/vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete IaC/cloud/orchestrator/vendor technology selected (UIL-15)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UIL-15 / IENV-06)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UIL-14/15 / IENV-06 / C7 — confers no authority, enacts no enforcement, embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Construct confers no authority, enforces nothing, embeds no secret (UIL-14/15)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("construct confers authority (UIL-15)")
        if subject.enacts_enforcement:
            return self._failed("construct enacts enforcement (UIL-14)")
        if subject.embeds_secret:
            return self._failed("construct embeds a secret (UIL-15 / RR-07)")
        if subject.projects_completion:
            return self._failed("construct projects completion (WF-12)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§5 — the No-Orphan lineage is rooted and closes to the 13-INFRASTRUCTURE anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at the meta-class, closed to 13-INFRASTRUCTURE."

    def evaluate(self, subject: EnvValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("13-INFRASTRUCTURE@") for link in chain):
            return self._failed("lineage does not close to the 13-INFRASTRUCTURE anchor")
        return self._passed(links=len(chain))


def environment_checks() -> tuple[ValidationCheck, ...]:
    """The full Environment & Provisioning validation suite (deterministically ordered)."""
    return (
        EnvTypedCheck(),
        EnvIdentifiedCheck(),
        EnvValueFidelityCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        ContainmentAcyclicCheck(),
        EnvBoundedIsolatedCheck(),
        LocatedCheck(),
        ContainmentByReferenceCheck(),
        ProvisioningBindsRuntimeCheck(),
        ConstructKindCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class EnvValidation:
    """The bundled outcome of validating a construct (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_construct(
    construct: _InfraConstruct,
    trace: TraceabilityRecord,
    *,
    containment_acyclic: bool = True,
    strict: bool = False,
) -> EnvValidation:
    """Validate ``construct`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected construct raises via the
    EC-1 acceptance gate.
    """
    subject = EnvValidationSubject.from_construct(
        construct, trace, containment_acyclic=containment_acyclic
    )
    engine = ValidationEngine(environment_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return EnvValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "EnvValidationSubject",
    "EnvValidation",
    "environment_checks",
    "validate_construct",
]
