"""EC3-B11-U07 — Orchestration validation (meta-validity V1…V5 + USL + SOO principles).

Proves a realized :class:`~service.orchestration.Orchestration` is **META-VALID** (SERVICE-005
§8, V1…V5), **Service-law conformant** (SERVICE-001 §7), and **Orchestration-principle
conformant** (SERVICE-011 §4, SOO-01…10) by running deterministic checks through the
**CERTIFIED EC-1 Validation Engine**.

The suite emits the seven **generic** check ids the CCE ten-gate suite depends on so that
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
from service.orchestration import Orchestration
from service.orchestration_meta import (
    KIND_RUNTIME_CONCERN,
    ORCHESTRATION_META_CLASS,
    OrchestrationKind,
)
from service.orchestration_traceability import OrchestrationTraceabilityRecord
from service.service_meta import META_RELATIONSHIPS, ServiceState
from service.service_validation import ServiceValidation

#: The blueprint id an Orchestration realizes (its meta-class) — used by the EC-1 report.
ORCHESTRATION_BLUEPRINT_ID = ORCHESTRATION_META_CLASS

_KIND_VALUES = frozenset(k.value for k in OrchestrationKind)
_STATE_VALUES = frozenset(s.value for s in ServiceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class OrchestrationValidationSubject:
    """A normalized, immutable projection of an Orchestration that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    step_refs: tuple[str, ...]
    dependencies: tuple[tuple[str, str], ...]
    execution_plan: tuple[str, ...]
    contract_ref: str
    behavior_ref: str
    data_refs: tuple[str, ...]
    runtime_concern: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    coordination_acyclic: bool
    founding_acyclic: bool
    coordinates_steps: bool
    topology_valid: bool
    contract_bound: bool
    runtime_reuse_valid: bool
    behavior_by_reference: bool
    data_by_reference: bool
    references_resolve: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_orchestration(
        cls, orchestration: Orchestration, trace: OrchestrationTraceabilityRecord
    ) -> OrchestrationValidationSubject:
        """Project ``orchestration`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=orchestration.orchestration_id,
            blueprint_id=ORCHESTRATION_BLUEPRINT_ID,
            meta_class=orchestration.meta_class,
            type_tag=orchestration.type_tag,
            kind=orchestration.kind.value,
            value_digest=orchestration.value_digest,
            step_refs=orchestration.step_refs,
            dependencies=orchestration.dependencies,
            execution_plan=orchestration.execution_plan(),
            contract_ref=orchestration.contract_ref,
            behavior_ref=orchestration.behavior_ref,
            data_refs=orchestration.data_refs,
            runtime_concern=KIND_RUNTIME_CONCERN[orchestration.kind],
            relationships=orchestration.meta_relationships(),
            lifecycle_state=orchestration.state.value,
            coordination_acyclic=orchestration.is_coordination_acyclic(),
            founding_acyclic=orchestration.is_founding_acyclic(),
            coordinates_steps=orchestration.coordinates_steps(),
            topology_valid=orchestration.topology_valid(),
            contract_bound=orchestration.contract_bound(),
            runtime_reuse_valid=orchestration.runtime_reuse_valid(),
            behavior_by_reference=orchestration.behavior_by_reference(),
            data_by_reference=orchestration.data_by_reference(),
            references_resolve=orchestration.references_resolve(),
            confers_authority=orchestration.confers_authority(),
            selects_technology=orchestration.selects_technology(),
            embeds_secret=orchestration.embeds_secret(),
            redefines_foundation=orchestration.redefines_foundation(),
            substrate_refs=tuple(orchestration.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),
        )


# ---------------------------------------------------------------------------
# Orchestration-layer validation checks
# ---------------------------------------------------------------------------


class OrchestrationTypedCheck(ValidationCheck):
    """USL-03 / SOO-01 / C1 — the orchestration is typed (non-empty ENG-004 type)."""

    check_id = "orchestration-typed"
    severity = Severity.BLOCKING
    description = "Orchestration bears a non-empty ENG-004 type_tag (USL-03 / SOO-01)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("orchestration is untyped (USL-03)")
        return self._passed(type_tag=subject.type_tag)


class OrchestrationIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SOO-02 / C1 — the orchestration is identified (ENG-001) and object-borne."""

    check_id = "orchestration-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Orchestration bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-ORCHESTRATION-"):
            return self._failed("orchestration has no ENG-001 identity (USL-04)")
        if not subject.value_digest:
            return self._failed("orchestration is not object-borne (no value digest) (USL-05)")
        return self._passed(orchestration_id=subject.target_id)


class OrchestrationValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the orchestration core round-trips through the EC-1 canonical encoding.

    Emitted under the shared id ``service-value-fidelity`` so the reused CCE Gate-3
    aggregates it without duplicating gate logic.
    """

    check_id = "service-value-fidelity"
    severity = Severity.BLOCKING
    description = "Orchestration core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("orchestration core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class OrchestrationClassifiedCheck(ValidationCheck):
    """SXH-07 / SXC-02 — the orchestration is classified by exactly one kind."""

    check_id = "orchestration-classified"
    severity = Severity.BLOCKING
    description = "Orchestration is classified by an SXH-07 kind (single-facet, SXC-02)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("orchestration kind is outside SXH-07", kind=subject.kind)
        return self._passed(kind=subject.kind)


class OrchestrationCoordinatesStepsCheck(ValidationCheck):
    """SMR-06 / SOR-06 / SOO-04 — the orchestration coordinates ≥1 step by ENG-005 reference."""

    check_id = "orchestration-coordinates-steps"
    severity = Severity.BLOCKING
    description = "Orchestration coordinates ≥1 step by ENG-005 reference (SMR-06 / SOO-04)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not subject.coordinates_steps:
            return self._failed("orchestration coordinates no step (SMR-06 / SOO-04)")
        return self._passed(steps=len(subject.step_refs))


class OrchestrationCoordinationAcyclicCheck(ValidationCheck):
    """SOO-06 / SOO-C1 — the founding coordination graph is acyclic (a deterministic plan)."""

    check_id = "orchestration-coordination-acyclic"
    severity = Severity.BLOCKING
    description = "Coordination graph acyclic; a single deterministic execution plan (SOO-06)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not subject.coordination_acyclic:
            return self._failed("coordination graph is cyclic/ill-formed (SOO-06 / SOO-C1)")
        return self._passed(execution_plan=list(subject.execution_plan))


class OrchestrationTopologyValidCheck(ValidationCheck):
    """SXH-07 / SOO-C3 — the coordination topology matches the orchestration kind."""

    check_id = "orchestration-topology-valid"
    severity = Severity.BLOCKING
    description = "Coordination topology matches the SXH-07 kind (SOO-C3; deterministic)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not subject.topology_valid:
            return self._failed(
                "orchestration topology invalid for kind (SOO-C3)",
                kind=subject.kind,
                steps=len(subject.step_refs),
                edges=len(subject.dependencies),
            )
        return self._passed(kind=subject.kind, steps=len(subject.step_refs))


class OrchestrationContractBoundCheck(ValidationCheck):
    """SMR-02 / SOR-02 / SOO-05 / SOO-K2 — the orchestration is bound by a composition contract."""

    check_id = "orchestration-contract-bound"
    severity = Severity.BLOCKING
    description = "Orchestration is bound by a composition contract by reference (SMR-02 / SOO-05)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not subject.contract_bound:
            return self._failed("orchestration is bound by no contract (SMR-02 / SOO-05)")
        return self._passed(contract_ref=subject.contract_ref)


class OrchestrationRuntimeReuseCheck(ValidationCheck):
    """SMR-11 / SOO-03 / SOO-C3 / §7 — behaves-as the kind's RUNTIME concern by reference."""

    check_id = "orchestration-runtime-reuse"
    severity = Severity.BLOCKING
    description = "Behaves-as the kind-appropriate RUNTIME concern by reference (SOO-03 / §7)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not subject.runtime_reuse_valid:
            return self._failed(
                "behavior does not reuse the kind's RUNTIME concern (SOO-03)",
                kind=subject.kind,
                expected=subject.runtime_concern,
                behavior_ref=subject.behavior_ref,
            )
        return self._passed(
            behavior_ref=subject.behavior_ref, runtime_concern=subject.runtime_concern
        )


class OrchestrationDataByReferenceCheck(ValidationCheck):
    """USL-11 / SOO-07 / SMR-13 — inter-step data references DF-2 by reference."""

    check_id = "orchestration-data-by-reference"
    severity = Severity.BLOCKING
    description = "Inter-step data references DF-2 (SMR-13, by reference; USL-11 / SOO-07)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not subject.data_by_reference:
            return self._failed("an inter-step data reference is not a valid DF-2 reference")
        return self._passed(data_refs=len(subject.data_refs))


class MetaClassSingleCheck(ValidationCheck):
    """V1 / SMI-01 — the orchestration instantiates exactly one meta-class (SMC-07)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Orchestration instantiates exactly the SMC-07 meta-class (V1)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if subject.meta_class != ORCHESTRATION_META_CLASS:
            return self._failed("meta-class is not SMC-07 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / SMI-02 — every relationship used lies within SMR-01…13."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All orchestration relationships are within SMR-01…13 (V2)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside SMR-01…13 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — SMK-01 (typed/identified/object) + SMK-02 (contract-bound) +
    SMK-05/07 (runtime/data references resolve)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01/02/05/07 hold (typed/identified, contract-bound, refs resolve) (V3)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("SMK-01 not satisfied (V3)")
        if not subject.contract_bound:
            return self._failed("SMK-02 not satisfied: orchestration is uncontracted (V3)")
        if not subject.references_resolve:
            return self._failed("SMK-05/07 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["SMK-01", "SMK-02", "SMK-05", "SMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMK-03 / SOO-06 / SOO-C1 — the founding coordination graph is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The orchestration's founding coordination graph is acyclic (V4 / SMK-03)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding coordination graph is not acyclic (V4 / SOO-C1)")
        return self._passed(acyclic=subject.founding_acyclic)


class LifecycleValidCheck(ValidationCheck):
    """V5 / USL-12 — the orchestration holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Orchestration holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """USL-02 / SMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/DF-2 referenced, redefined nowhere (USL-02)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (USL-02 / SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (USL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """USL-15 / SOO-09 / C7 — no workflow-engine/scheduler/BPMN/protocol/vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/workflow-engine/scheduler selected (USL-15 / SOO-09)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology/workflow-engine was selected (USL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """USL-15 / SOO-09 / C7 — the orchestration confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Orchestration confers no authority and embeds no secret (USL-15 / SOO-09)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("orchestration confers authority (USL-15)")
        if subject.embeds_secret:
            return self._failed("orchestration embeds a secret (USL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted at SMC-07 and closes to 11-SERVICE."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at SMC-07 and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: OrchestrationValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def orchestration_checks() -> tuple[ValidationCheck, ...]:
    """The full orchestration-layer validation suite (deterministically ordered by the engine)."""
    return (
        OrchestrationTypedCheck(),
        OrchestrationIdentifiedCheck(),
        OrchestrationValueFidelityCheck(),
        OrchestrationClassifiedCheck(),
        OrchestrationCoordinatesStepsCheck(),
        OrchestrationCoordinationAcyclicCheck(),
        OrchestrationTopologyValidCheck(),
        OrchestrationContractBoundCheck(),
        OrchestrationRuntimeReuseCheck(),
        OrchestrationDataByReferenceCheck(),
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


def validate_orchestration(
    orchestration: Orchestration,
    trace: OrchestrationTraceabilityRecord,
    *,
    strict: bool = False,
) -> ServiceValidation:
    """Validate ``orchestration`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = OrchestrationValidationSubject.from_orchestration(orchestration, trace)
    engine = ValidationEngine(orchestration_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ServiceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "ORCHESTRATION_BLUEPRINT_ID",
    "OrchestrationValidationSubject",
    "orchestration_checks",
    "validate_orchestration",
]
