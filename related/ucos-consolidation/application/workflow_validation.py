"""EC3-B12-U05 — Workflow validation (meta-validity V1…V5 + UAL/WKF conformance).

This module proves a realized :class:`~application.workflow.Workflow` is **META-VALID**
(APPLICATION-005 §8, V1…V5) and **Application-/Workflow-law conformant** (APPLICATION-001
§7, UAL-01…15; APPLICATION-009 §4, WKF-01…10) by running a suite of deterministic,
application-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate (:func:`engine.validation.gates.enforce_acceptance`). Validation evidence is produced
with the EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`WorkflowValidationSubject`
(the type-independent projection the EC-1 engine consumes), so an identical workflow yields
a byte-identical report, evidence, and acceptance decision (VC-4). Every check is
**blocking**: the verdict is PASS iff the workflow satisfies every meta-validity and
Application-/Workflow-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.workflow import Workflow
from application.workflow_meta import (
    META_RELATIONSHIPS,
    WORKFLOW_META_CLASS,
    WorkflowKind,
    WorkflowState,
)
from application.workflow_traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UAL-02) — the certified validation substrate --------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Workflow realizes (its meta-class) — used by the EC-1 report.
WORKFLOW_BLUEPRINT_ID = WORKFLOW_META_CLASS

_KIND_VALUES = frozenset(k.value for k in WorkflowKind)
_STATE_VALUES = frozenset(s.value for s in WorkflowState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class WorkflowValidationSubject:
    """A normalized, immutable projection of a Workflow that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the workflow's meta-facts. Holds no runtime state
    and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    sequence_refs: tuple[str, ...]
    sequenced_step_count: int
    operation_refs: tuple[str, ...]
    consumed_operation_count: int
    state_ref: str
    behavior_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    references_resolve: bool
    sequences_steps: bool
    steps_are_partition: bool
    consumes_operations: bool
    operations_are_partition: bool
    holds_state: bool
    sequence_is_explicit: bool
    branch_determinacy_holds: bool
    records_intermediate_state: bool
    arrangement_class: str
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_workflow(
        cls, workflow: Workflow, trace: TraceabilityRecord
    ) -> WorkflowValidationSubject:
        """Project ``workflow`` (+ its lineage) into a validation subject."""
        payload = workflow.to_dict()
        return cls(
            target_id=workflow.workflow_id,
            blueprint_id=WORKFLOW_BLUEPRINT_ID,
            meta_class=workflow.meta_class,
            type_tag=workflow.type_tag,
            kind=workflow.kind.value,
            value_digest=workflow.value_digest,
            sequence_refs=tuple(payload["sequence_refs"]),
            sequenced_step_count=workflow.sequenced_step_count(),
            operation_refs=tuple(payload["operation_refs"]),
            consumed_operation_count=workflow.consumed_operation_count(),
            state_ref=workflow.state_ref,
            behavior_ref=workflow.behavior_ref,
            relationships=workflow.meta_relationships(),
            lifecycle_state=workflow.state.value,
            founding_acyclic=workflow.is_founding_acyclic(),
            references_resolve=workflow.references_resolve(),
            sequences_steps=workflow.sequences_steps(),
            steps_are_partition=workflow.steps_are_partition(),
            consumes_operations=workflow.consumes_operations(),
            operations_are_partition=workflow.operations_are_partition(),
            holds_state=workflow.holds_state(),
            sequence_is_explicit=workflow.sequence_is_explicit(),
            branch_determinacy_holds=workflow.branch_determinacy_holds(),
            records_intermediate_state=workflow.records_intermediate_state(),
            arrangement_class=workflow.arrangement_class(),
            confers_authority=workflow.confers_authority(),
            selects_technology=workflow.selects_technology(),
            embeds_secret=workflow.embeds_secret(),
            redefines_foundation=workflow.redefines_foundation(),
            substrate_refs=tuple(payload["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Workflow-layer validation checks (each maps to explicit V*/UAL*/WKF*/AMK* obligations)
# ---------------------------------------------------------------------------


class WorkflowTypedCheck(ValidationCheck):
    """UAL-03 / WKF-01 / AMK-01 / C1 — the workflow is classified by a non-empty type."""

    check_id = "workflow-typed"
    severity = Severity.BLOCKING
    description = "Workflow bears a non-empty ENG-004 type_tag (UAL-03 / WKF-01)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("workflow is untyped (UAL-03)")
        return self._passed(type_tag=subject.type_tag)


class WorkflowIdentifiedCheck(ValidationCheck):
    """UAL-04/05 / WKF-02 / AMK-01 / C1 — the workflow is identified and object-borne."""

    check_id = "workflow-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Workflow bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-WORKFLOW-"):
            return self._failed("workflow lacks ENG-001 identity (UAL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("workflow is not object-borne (no value digest) (UAL-05)")
        return self._passed(workflow_id=subject.target_id)


class WorkflowValueFidelityCheck(ValidationCheck):
    """ENG-003 — the workflow core round-trips through the EC-1 canonical encoding."""

    check_id = "workflow-value-fidelity"
    severity = Severity.BLOCKING
    description = "Workflow core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("workflow core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class WorkflowClassifiedCheck(ValidationCheck):
    """AXH-05 / AXC-04 — the workflow is classified by exactly one Workflow kind."""

    check_id = "workflow-classified"
    severity = Severity.BLOCKING
    description = "Workflow is classified by an AXH-05 kind (single-facet, AXC-04)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("workflow kind is outside AXH-05", kind=subject.kind)
        return self._passed(kind=subject.kind, arrangement=subject.arrangement_class)


class WorkflowSequencesStepsCheck(ValidationCheck):
    """AMR-04 / WKF-04 — the workflow sequences ≥1 feature/operation by reference.

    This is the workflow's **defining relationship** (sequenced-by) and the relationship
    **no prior Band-12 unit used** — the arrangement of delivery over time.
    """

    check_id = "workflow-sequences-steps"
    severity = Severity.BLOCKING
    description = "Workflow sequences ≥1 feature/operation by ENG-005 reference (AMR-04 / WKF-04)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.sequences_steps or subject.sequenced_step_count < 1:
            return self._failed("workflow sequences nothing (AMR-04 / WKF-04)")
        return self._passed(sequenced_step_count=subject.sequenced_step_count)


class WorkflowStepsPartitionCheck(ValidationCheck):
    """WKF-C1 — the sequenced steps are distinct (a partition)."""

    check_id = "workflow-steps-partition"
    severity = Severity.BLOCKING
    description = "Sequenced steps are distinct (a partition) (WKF-C1)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.steps_are_partition:
            return self._failed("sequenced steps are not distinct (WKF-C1)")
        return self._passed(sequenced_step_count=subject.sequenced_step_count)


class WorkflowConsumesOperationCheck(ValidationCheck):
    """AMR-13 / WKF-K4 / AMK-07 — the workflow's steps consume ≥1 SF-2 operation by ref."""

    check_id = "workflow-consumes-operation"
    severity = Severity.BLOCKING
    description = "Workflow's steps consume ≥1 SF-2 operation by ENG-005 reference (AMR-13)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.consumes_operations or subject.consumed_operation_count < 1:
            return self._failed("workflow's steps consume no SF-2 operation (AMR-13 / WKF-K4)")
        return self._passed(consumed_operation_count=subject.consumed_operation_count)


class WorkflowOperationsPartitionCheck(ValidationCheck):
    """WKF-K4 — the consumed operations are distinct (a partition)."""

    check_id = "workflow-operations-partition"
    severity = Severity.BLOCKING
    description = "Consumed operations are distinct (a partition) (WKF-K4)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.operations_are_partition:
            return self._failed("consumed operations are not distinct (WKF-K4)")
        return self._passed(consumed_operation_count=subject.consumed_operation_count)


class WorkflowHoldsStateCheck(ValidationCheck):
    """AMR-06 / WKF-06 / AMK-05 — the workflow holds/advances state by reference (→ RL-F2).

    This is the workflow's second distinctive relationship (holds-state) — the relationship
    **no prior Band-12 unit used** — bound to RL-F2 by reference.
    """

    check_id = "workflow-holds-state"
    severity = Severity.BLOCKING
    description = "Workflow holds/advances state by reference → RL-F2 (AMR-06 / WKF-06)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.holds_state or not subject.state_ref.strip():
            return self._failed("workflow holds no state (AMR-06 / WKF-06 / UAL-12)")
        return self._passed(state_ref=subject.state_ref)


class WorkflowSequenceExplicitCheck(ValidationCheck):
    """WKF-C1 / UAL-10 — the workflow's arrangement is explicit, typed, and decidable.

    A workflow declares its sequence of features/operations — nothing implicit (WKF-04 /
    WKF-C1 / UAL-10, the governing law).
    """

    check_id = "workflow-sequence-explicit"
    severity = Severity.BLOCKING
    description = "Workflow sequence is explicit, typed, and decidable (WKF-C1 / UAL-10)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.sequence_is_explicit:
            return self._failed("workflow arrangement is not explicit (WKF-C1 / UAL-10)")
        return self._passed(arrangement=subject.arrangement_class)


class WorkflowBranchDeterminacyCheck(ValidationCheck):
    """WKF-05 / WKF-C2 / AXH-05 — branch conditions are decidable and terminating."""

    check_id = "workflow-branch-determinacy"
    severity = Severity.BLOCKING
    description = "Branch conditions decidable+terminating; Conditional sequences ≥2 (WKF-05)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.branch_determinacy_holds:
            return self._failed(
                "branch determinacy fails (a Conditional-Workflow must sequence ≥2) (WKF-05)",
                kind=subject.kind,
                count=subject.sequenced_step_count,
            )
        return self._passed(arrangement=subject.arrangement_class)


class WorkflowProcessRecordsStateCheck(ValidationCheck):
    """WKF-07 / WKF-C5 — a Process records its intermediate states (auditable progress)."""

    check_id = "workflow-process-records-state"
    severity = Severity.BLOCKING
    description = "A Process-Workflow records intermediate state (WKF-07 / WKF-C5)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.records_intermediate_state:
            return self._failed(
                "a Process-Workflow does not record intermediate state (WKF-07 / WKF-C5)",
                kind=subject.kind,
            )
        return self._passed(arrangement=subject.arrangement_class)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / AMI-01 — the workflow instantiates exactly one meta-class (AMC-05)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Workflow instantiates exactly the AMC-05 meta-class (V1)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if subject.meta_class != WORKFLOW_META_CLASS:
            return self._failed("meta-class is not AMC-05 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / AMI-02 — every relationship used lies within AMR-01…14."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All workflow relationships are within AMR-01…14 (V2)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside AMR-01…14 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (AMK-01 typed/id/object; AMK-02/05/07 references)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "AMK-01 (typed/identified/object) and AMK-02/05/07 (references) hold (V3)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("AMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("AMK-05/07 not satisfied: a reference does not resolve (V3)")
        if not (subject.sequence_is_explicit and subject.consumes_operations):
            return self._failed("AMK-02 not satisfied: sequence/consumption incomplete (V3)")
        return self._passed(constraints=["AMK-01", "AMK-02", "AMK-03", "AMK-05", "AMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / AMK-03 / WKF-C2 — the founding graph is acyclic (workflow uses no AMR-02/03/05)."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The workflow's founding graph is acyclic; sequencing is reference-only (V4)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UAL-12 — the workflow holds a valid AOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Workflow holds a valid AOS-01…06 lifecycle state (V5 / UAL-12)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UAL-02 / WKF-10 / AMI-05 / VC-5 — frozen foundations reused by reference, not redefined."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/SF-2 referenced, redefined nowhere (UAL-02 / AMI-05)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UAL-02 / AMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UAL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class BehaviorByReferenceCheck(ValidationCheck):
    """UAL-10 / §7 / AMK-05 / WKF-C4 — sequence/transition/emit binds RL-F2 + SF-2 by reference.

    THE governing law of the Workflow: the workflow binds the frozen RL-F2 workflow concern
    and SF-2 orchestration by reference and re-founds neither.
    """

    check_id = "behavior-by-reference"
    severity = Severity.BLOCKING
    description = "Behavior binds RL-F2 workflow + SF-2 orchestration by reference (UAL-10 / §7)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("no RL-F2 behavior reference (UAL-10 / §7 / WKF-C4)")
        return self._passed(behavior_ref=subject.behavior_ref)


class TechnologyIndependenceCheck(ValidationCheck):
    """UAL-15 / WKF-09 / C7 — no engine/scheduler/framework/API/protocol/vendor is selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/engine/scheduler/framework/vendor selected (UAL-15)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UAL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UAL-15 / WKF-09 / C7 — the workflow confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Workflow confers no authority and embeds no secret (UAL-15 / RR-07)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("workflow confers authority (UAL-15)")
        if subject.embeds_secret:
            return self._failed("workflow embeds a secret (UAL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 12-APPLICATION anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at AMC-05 and closed to 12-APPLICATION (No-Orphan)."

    def evaluate(self, subject: WorkflowValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("12-APPLICATION@") for link in chain):
            return self._failed("lineage does not close to the 12-APPLICATION anchor")
        return self._passed(links=len(chain))


def workflow_checks() -> tuple[ValidationCheck, ...]:
    """The full workflow-layer validation suite (deterministically ordered by the engine)."""
    return (
        WorkflowTypedCheck(),
        WorkflowIdentifiedCheck(),
        WorkflowValueFidelityCheck(),
        WorkflowClassifiedCheck(),
        WorkflowSequencesStepsCheck(),
        WorkflowStepsPartitionCheck(),
        WorkflowConsumesOperationCheck(),
        WorkflowOperationsPartitionCheck(),
        WorkflowHoldsStateCheck(),
        WorkflowSequenceExplicitCheck(),
        WorkflowBranchDeterminacyCheck(),
        WorkflowProcessRecordsStateCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        BehaviorByReferenceCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class WorkflowValidation:
    """The bundled outcome of validating a Workflow (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_workflow(
    workflow: Workflow, trace: TraceabilityRecord, *, strict: bool = False
) -> WorkflowValidation:
    """Validate ``workflow`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected workflow raises via the
    EC-1 acceptance gate.
    """
    subject = WorkflowValidationSubject.from_workflow(workflow, trace)
    engine = ValidationEngine(workflow_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return WorkflowValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "WORKFLOW_BLUEPRINT_ID",
    "WorkflowValidationSubject",
    "WorkflowValidation",
    "workflow_checks",
    "validate_workflow",
]
