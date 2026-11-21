"""EC3-B11-U08 — Execution validation (meta-validity V1…V5 + USL + SEX principles).

Proves a realized :class:`~service.execution.Execution` is **META-VALID** (SERVICE-005 §8,
V1…V5), **Service-law conformant** (SERVICE-001 §7), and **Execution-principle conformant**
(SERVICE-012 §4, SEX-01…10) by running deterministic checks through the **CERTIFIED EC-1
Validation Engine**.

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
from service.execution import Execution
from service.execution_meta import (
    EXECUTION_META_CLASS,
    KIND_RUNTIME_CONCERN,
    ExecutionKind,
)
from service.execution_traceability import ExecutionTraceabilityRecord
from service.service_meta import META_RELATIONSHIPS, ServiceState
from service.service_validation import ServiceValidation

#: The blueprint id an Execution realizes (its meta-class) — used by the EC-1 report.
EXECUTION_BLUEPRINT_ID = EXECUTION_META_CLASS

_KIND_VALUES = frozenset(k.value for k in ExecutionKind)
_STATE_VALUES = frozenset(s.value for s in ServiceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class ExecutionValidationSubject:
    """A normalized, immutable projection of an Execution that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    operation_ref: str
    behavior_ref: str
    data_refs: tuple[str, ...]
    policy_ref: str
    runtime_concern: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    no_self_founding: bool
    operation_bound: bool
    fulfils_contract: bool
    runtime_reuse_valid: bool
    behavior_by_reference: bool
    transactionality_by_reference: bool
    data_by_reference: bool
    policy_governed: bool
    records_completion: bool
    references_resolve: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_execution(
        cls, execution: Execution, trace: ExecutionTraceabilityRecord
    ) -> ExecutionValidationSubject:
        """Project ``execution`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=execution.execution_id,
            blueprint_id=EXECUTION_BLUEPRINT_ID,
            meta_class=execution.meta_class,
            type_tag=execution.type_tag,
            kind=execution.kind.value,
            value_digest=execution.value_digest,
            operation_ref=execution.operation_ref,
            behavior_ref=execution.behavior_ref,
            data_refs=execution.data_refs,
            policy_ref=execution.policy_ref,
            runtime_concern=KIND_RUNTIME_CONCERN[execution.kind],
            relationships=execution.meta_relationships(),
            lifecycle_state=execution.state.value,
            founding_acyclic=execution.is_founding_acyclic(),
            no_self_founding=execution.no_self_founding(),
            operation_bound=execution.operation_bound(),
            fulfils_contract=execution.fulfils_contract(),
            runtime_reuse_valid=execution.runtime_reuse_valid(),
            behavior_by_reference=execution.behavior_by_reference(),
            transactionality_by_reference=execution.transactionality_by_reference(),
            data_by_reference=execution.data_by_reference(),
            policy_governed=execution.policy_governed(),
            records_completion=execution.records_completion(),
            references_resolve=execution.references_resolve(),
            confers_authority=execution.confers_authority(),
            selects_technology=execution.selects_technology(),
            embeds_secret=execution.embeds_secret(),
            redefines_foundation=execution.redefines_foundation(),
            substrate_refs=tuple(execution.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),
        )


# ---------------------------------------------------------------------------
# Execution-layer validation checks
# ---------------------------------------------------------------------------


class ExecutionTypedCheck(ValidationCheck):
    """USL-03 / SEX-01 / C1 — the execution is typed (non-empty ENG-004 type)."""

    check_id = "execution-typed"
    severity = Severity.BLOCKING
    description = "Execution bears a non-empty ENG-004 type_tag (USL-03 / SEX-01)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("execution is untyped (USL-03)")
        return self._passed(type_tag=subject.type_tag)


class ExecutionIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SEX-02 / C1 — the execution is identified (ENG-001) and object-borne."""

    check_id = "execution-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Execution bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-EXECUTION-"):
            return self._failed("execution has no ENG-001 identity (USL-04)")
        if not subject.value_digest:
            return self._failed("execution is not object-borne (no value digest) (USL-05)")
        return self._passed(execution_id=subject.target_id)


class ExecutionValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the execution core round-trips through the EC-1 canonical encoding.

    Emitted under the shared id ``service-value-fidelity`` so the reused CCE Gate-3
    aggregates it without duplicating gate logic.
    """

    check_id = "service-value-fidelity"
    severity = Severity.BLOCKING
    description = "Execution core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("execution core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class ExecutionClassifiedCheck(ValidationCheck):
    """SXH-08 / SXC-02 — the execution is classified by exactly one kind."""

    check_id = "execution-classified"
    severity = Severity.BLOCKING
    description = "Execution is classified by an SXH-08 kind (single-facet, SXC-02)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("execution kind is outside SXH-08", kind=subject.kind)
        return self._passed(kind=subject.kind)


class ExecutionOperationBoundCheck(ValidationCheck):
    """SMR-07 / SOR-07 / SEX-04 / SEX-K2 — carries out exactly the operation referencing it."""

    check_id = "execution-operation-bound"
    severity = Severity.BLOCKING
    description = "Execution carries out exactly one operation by ENG-005 reference (SMR-07)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not subject.operation_bound:
            return self._failed("execution is bound to no operation (SMR-07 / SEX-04)")
        return self._passed(operation_ref=subject.operation_ref)


class ExecutionContractFulfilmentCheck(ValidationCheck):
    """SEX-05 / USL-06 — the execution fulfils its (contracted) operation; invents no work."""

    check_id = "execution-contract-fulfilment"
    severity = Severity.BLOCKING
    description = "Execution fulfils its operation's contract; effects only as contracted (SEX-05)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not subject.fulfils_contract:
            return self._failed("execution fulfils no contracted operation (SEX-05 / USL-06)")
        return self._passed(operation_ref=subject.operation_ref)


class ExecutionRuntimeReuseCheck(ValidationCheck):
    """SMR-11 / SEX-03 / §7 — behaves-as the kind's RUNTIME concern by reference."""

    check_id = "execution-runtime-reuse"
    severity = Severity.BLOCKING
    description = "Behaves-as the kind-appropriate RUNTIME concern by reference (SEX-03 / §7)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not subject.runtime_reuse_valid:
            return self._failed(
                "behavior does not reuse the kind's RUNTIME concern (SEX-03)",
                kind=subject.kind,
                expected=subject.runtime_concern,
                behavior_ref=subject.behavior_ref,
            )
        return self._passed(
            behavior_ref=subject.behavior_ref, runtime_concern=subject.runtime_concern
        )


class ExecutionTransactionalityCheck(ValidationCheck):
    """SEX-06 / SEX-C1 / §7 — transactional atomicity is a RUNTIME workflow property by ref."""

    check_id = "execution-transactionality-by-reference"
    severity = Severity.BLOCKING
    description = "Transactional atomicity binds RUNTIME workflow by reference (SEX-06)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not subject.transactionality_by_reference:
            return self._failed(
                "transactional execution does not bind RUNTIME workflow by reference (SEX-C1)",
                kind=subject.kind,
                behavior_ref=subject.behavior_ref,
            )
        return self._passed(kind=subject.kind)


class ExecutionDataByReferenceCheck(ValidationCheck):
    """USL-11 / SEX-07 / SMR-13 — read/written data references DF-2 by reference."""

    check_id = "execution-data-by-reference"
    severity = Severity.BLOCKING
    description = "Read/written data references DF-2 (SMR-13, by reference; USL-11 / SEX-07)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not subject.data_by_reference:
            return self._failed("a read/written data reference is not a valid DF-2 reference")
        return self._passed(data_refs=len(subject.data_refs))


class ExecutionPolicyGovernedCheck(ValidationCheck):
    """SMR-08 / SOR-08 / §11 — the execution is governed-by a declarative policy by reference."""

    check_id = "execution-policy-governed"
    severity = Severity.BLOCKING
    description = "Execution is governed-by a declarative policy by reference (SMR-08 / §11)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not subject.policy_governed:
            return self._failed("execution is governed by no policy (SMR-08 / §11)")
        return self._passed(policy_ref=subject.policy_ref)


class ExecutionLifecycleRecordingCheck(ValidationCheck):
    """SEX-08 / SOV-07 — the execution records completion; transitions are never silent."""

    check_id = "execution-lifecycle-recording"
    severity = Severity.BLOCKING
    description = "Execution records completion (emits an `executed` event; SEX-08 / SOV-07)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not subject.records_completion:
            return self._failed("execution does not record completion (SEX-08)")
        return self._passed(state=subject.lifecycle_state)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / SMI-01 — the execution instantiates exactly one meta-class (SMC-08)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Execution instantiates exactly the SMC-08 meta-class (V1)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if subject.meta_class != EXECUTION_META_CLASS:
            return self._failed("meta-class is not SMC-08 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / SMI-02 — every relationship used lies within SMR-01…13."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All execution relationships are within SMR-01…13 (V2)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside SMR-01…13 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — SMK-01 (typed/identified/object) + SMK-02 (operation-bound) +
    SMK-05/07 (runtime/data references resolve)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01/02/05/07 hold (typed/identified, operation-bound, refs resolve) (V3)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("SMK-01 not satisfied (V3)")
        if not subject.operation_bound:
            return self._failed("SMK-02 not satisfied: execution is not operation-bound (V3)")
        if not subject.references_resolve:
            return self._failed("SMK-05/07 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["SMK-01", "SMK-02", "SMK-05", "SMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMK-03 / SMI-04 — the founding graph (executed / behaves-as) is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The execution's founding graph is acyclic (V4 / SMK-03)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4 / SMK-03)")
        return self._passed(acyclic=subject.founding_acyclic)


class LifecycleValidCheck(ValidationCheck):
    """V5 / USL-12 — the execution holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Execution holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """USL-02 / SMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/DF-2 referenced, redefined nowhere (USL-02)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (USL-02 / SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (USL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """USL-15 / SEX-09 / C7 — no runtime-engine/container/scheduler/protocol/vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/runtime-engine/container selected (USL-15 / SEX-09)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology/runtime-engine was selected (USL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """USL-15 / SEX-09 / C7 — the execution confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Execution confers no authority and embeds no secret (USL-15 / SEX-09)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("execution confers authority (USL-15)")
        if subject.embeds_secret:
            return self._failed("execution embeds a secret (USL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§17 / AC-7 — the No-Orphan lineage is rooted at SMC-08 and closes to 11-SERVICE."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at SMC-08 and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: ExecutionValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def execution_checks() -> tuple[ValidationCheck, ...]:
    """The full execution-layer validation suite (deterministically ordered by the engine)."""
    return (
        ExecutionTypedCheck(),
        ExecutionIdentifiedCheck(),
        ExecutionValueFidelityCheck(),
        ExecutionClassifiedCheck(),
        ExecutionOperationBoundCheck(),
        ExecutionContractFulfilmentCheck(),
        ExecutionRuntimeReuseCheck(),
        ExecutionTransactionalityCheck(),
        ExecutionDataByReferenceCheck(),
        ExecutionPolicyGovernedCheck(),
        ExecutionLifecycleRecordingCheck(),
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


def validate_execution(
    execution: Execution,
    trace: ExecutionTraceabilityRecord,
    *,
    strict: bool = False,
) -> ServiceValidation:
    """Validate ``execution`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = ExecutionValidationSubject.from_execution(execution, trace)
    engine = ValidationEngine(execution_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ServiceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "EXECUTION_BLUEPRINT_ID",
    "ExecutionValidationSubject",
    "execution_checks",
    "validate_execution",
]
