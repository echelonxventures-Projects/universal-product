"""EC3-B11-U09 — Policy validation (meta-validity V1…V5 + USL + SPL principles).

Proves a realized :class:`~service.policy.Policy` is **META-VALID** (SERVICE-005 §8, V1…V5),
**Service-law conformant** (SERVICE-001 §7), and **Policy-principle conformant** (SERVICE-013
§4, SPL-01…10) by running deterministic checks through the **CERTIFIED EC-1 Validation Engine**.

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
from service.policy import Policy
from service.policy_meta import (
    KIND_RUNTIME_CONCERN,
    POLICY_META_CLASS,
    PolicyKind,
)
from service.policy_traceability import PolicyTraceabilityRecord
from service.service_meta import META_RELATIONSHIPS, ServiceState
from service.service_validation import ServiceValidation

#: The blueprint id a Policy realizes (its meta-class) — used by the EC-1 report.
POLICY_BLUEPRINT_ID = POLICY_META_CLASS

_KIND_VALUES = frozenset(k.value for k in PolicyKind)
_STATE_VALUES = frozenset(s.value for s in ServiceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class PolicyValidationSubject:
    """A normalized, immutable projection of a Policy that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    contract_ref: str
    subject_refs: tuple[str, ...]
    behavior_ref: str
    data_refs: tuple[str, ...]
    runtime_concern: str
    precedence: int
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    no_self_founding: bool
    boundary_bound: bool
    declarative_nonenforcing: bool
    runtime_reuse_valid: bool
    behavior_by_reference: bool
    data_by_reference: bool
    scope_by_reference: bool
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
    def from_policy(
        cls, policy: Policy, trace: PolicyTraceabilityRecord
    ) -> PolicyValidationSubject:
        """Project ``policy`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=policy.policy_id,
            blueprint_id=POLICY_BLUEPRINT_ID,
            meta_class=policy.meta_class,
            type_tag=policy.type_tag,
            kind=policy.kind.value,
            value_digest=policy.value_digest,
            contract_ref=policy.contract_ref,
            subject_refs=policy.subject_refs,
            behavior_ref=policy.behavior_ref,
            data_refs=policy.data_refs,
            runtime_concern=KIND_RUNTIME_CONCERN[policy.kind],
            precedence=policy.precedence,
            relationships=policy.meta_relationships(),
            lifecycle_state=policy.state.value,
            founding_acyclic=policy.is_founding_acyclic(),
            no_self_founding=policy.no_self_founding(),
            boundary_bound=policy.boundary_bound(),
            declarative_nonenforcing=policy.declarative_nonenforcing(),
            runtime_reuse_valid=policy.runtime_reuse_valid(),
            behavior_by_reference=policy.behavior_by_reference(),
            data_by_reference=policy.data_by_reference(),
            scope_by_reference=policy.scope_by_reference(),
            precedence_decidable=policy.precedence_decidable(),
            records_lifecycle=policy.records_lifecycle(),
            references_resolve=policy.references_resolve(),
            confers_authority=policy.confers_authority(),
            selects_technology=policy.selects_technology(),
            embeds_secret=policy.embeds_secret(),
            redefines_foundation=policy.redefines_foundation(),
            substrate_refs=tuple(policy.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),
        )


# ---------------------------------------------------------------------------
# Policy-layer validation checks
# ---------------------------------------------------------------------------


class PolicyTypedCheck(ValidationCheck):
    """USL-03 / SPL-01 / C1 — the policy is typed (non-empty ENG-004 type)."""

    check_id = "policy-typed"
    severity = Severity.BLOCKING
    description = "Policy bears a non-empty ENG-004 type_tag (USL-03 / SPL-01)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("policy is untyped (USL-03)")
        return self._passed(type_tag=subject.type_tag)


class PolicyIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SPL-02 / C1 — the policy is identified (ENG-001) and object-borne."""

    check_id = "policy-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Policy bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-POLICY-"):
            return self._failed("policy has no ENG-001 identity (USL-04)")
        if not subject.value_digest:
            return self._failed("policy is not object-borne (no value digest) (USL-05)")
        return self._passed(policy_id=subject.target_id)


class PolicyValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the policy core round-trips through the EC-1 canonical encoding.

    Emitted under the shared id ``service-value-fidelity`` so the reused CCE Gate-3
    aggregates it without duplicating gate logic.
    """

    check_id = "service-value-fidelity"
    severity = Severity.BLOCKING
    description = "Policy core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("policy core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class PolicyClassifiedCheck(ValidationCheck):
    """SXH-09 / SXC-02 — the policy is classified by exactly one kind."""

    check_id = "policy-classified"
    severity = Severity.BLOCKING
    description = "Policy is classified by an SXH-09 kind (single-facet, SXC-02)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("policy kind is outside SXH-09", kind=subject.kind)
        return self._passed(kind=subject.kind)


class PolicyBoundaryBoundCheck(ValidationCheck):
    """SMR-02 / SOR-02 / SPL-06 / SPL-K2 — bound-by exactly the declaring contract boundary."""

    check_id = "policy-boundary-bound"
    severity = Severity.BLOCKING
    description = "Policy binds a contract/operation boundary by ENG-005 reference (SMR-02)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not subject.boundary_bound:
            return self._failed("policy is bound to no boundary (SMR-02 / SPL-06)")
        return self._passed(contract_ref=subject.contract_ref)


class PolicyDeclarativeCheck(ValidationCheck):
    """SPL-03 / SPL-04 / USL-13 — the policy is declarative and non-enforcing (THE law)."""

    check_id = "policy-declarative-nonenforcing"
    severity = Severity.BLOCKING
    description = "Policy is declarative and enacts/grants/blocks nothing (USL-13 / SPL-04)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not subject.declarative_nonenforcing:
            return self._failed("policy is not declarative/non-enforcing (USL-13 / SPL-04)")
        return self._passed(governing_law="USL-13")


class PolicyRuntimeReuseCheck(ValidationCheck):
    """SMR-11 / SPL-05 / §7 — evaluation behaves-as the RUNTIME policy concern by reference."""

    check_id = "policy-runtime-reuse"
    severity = Severity.BLOCKING
    description = "Evaluation behaves-as the RUNTIME policy concern (RUNTIME-010) by reference."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not subject.runtime_reuse_valid:
            return self._failed(
                "evaluation does not reuse the RUNTIME policy concern (SPL-05)",
                kind=subject.kind,
                expected=subject.runtime_concern,
                behavior_ref=subject.behavior_ref,
            )
        return self._passed(
            behavior_ref=subject.behavior_ref, runtime_concern=subject.runtime_concern
        )


class PolicyDataByReferenceCheck(ValidationCheck):
    """USL-11 / SPL-C4 / SMR-13 — predicate data references DF-2 by reference."""

    check_id = "policy-data-by-reference"
    severity = Severity.BLOCKING
    description = "Predicate data references DF-2 (SMR-13, by reference; USL-11 / SPL-C4)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not subject.data_by_reference:
            return self._failed("a predicate data reference is not a valid DF-2 reference")
        return self._passed(data_refs=len(subject.data_refs))


class PolicyGovernedScopeCheck(ValidationCheck):
    """SMR-08 / SOR-08 — every governed-subject reference is a valid ENG-005 reference."""

    check_id = "policy-governed-scope"
    severity = Severity.BLOCKING
    description = "Governed constructs referenced by valid ENG-005 references (SMR-08 governed-by)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not subject.scope_by_reference:
            return self._failed("a governed-subject reference is not a valid ENG-005 reference")
        return self._passed(subject_refs=len(subject.subject_refs))


class PolicyPrecedenceCheck(ValidationCheck):
    """SPL-08 — the policy's evaluation precedence is decidable from its SXH-09 kind."""

    check_id = "policy-precedence-decidable"
    severity = Severity.BLOCKING
    description = "Policy evaluation precedence is decidable from its SXH-09 kind (SPL-08)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not subject.precedence_decidable:
            return self._failed("policy precedence is not decidable (SPL-08)")
        return self._passed(precedence=subject.precedence)


class PolicyLifecycleRecordingCheck(ValidationCheck):
    """SPL-08 / SOV-08 — the policy records a decidable lifecycle state (never silent)."""

    check_id = "policy-lifecycle-recording"
    severity = Severity.BLOCKING
    description = "Policy records a decidable lifecycle state (SOV-08); transitions recorded."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not subject.records_lifecycle:
            return self._failed("policy does not record a lifecycle state (SOV-08)")
        return self._passed(state=subject.lifecycle_state)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / SMI-01 — the policy instantiates exactly one meta-class (SMC-09)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Policy instantiates exactly the SMC-09 meta-class (V1)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if subject.meta_class != POLICY_META_CLASS:
            return self._failed("meta-class is not SMC-09 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / SMI-02 — every relationship used lies within SMR-01…13."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All policy relationships are within SMR-01…13 (V2)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside SMR-01…13 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — SMK-01 (typed/identified/object) + SMK-02 (boundary-bound) +
    SMK-05/07 (runtime/data references resolve)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01/02/05/07 hold (typed/identified, boundary-bound, refs resolve) (V3)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("SMK-01 not satisfied (V3)")
        if not subject.boundary_bound:
            return self._failed("SMK-02 not satisfied: policy is not boundary-bound (V3)")
        if not subject.references_resolve:
            return self._failed("SMK-05/07 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["SMK-01", "SMK-02", "SMK-05", "SMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMK-03 / SMI-04 — the founding graph (bound-by / behaves-as) is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The policy's founding graph is acyclic (V4 / SMK-03)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4 / SMK-03)")
        return self._passed(acyclic=subject.founding_acyclic)


class LifecycleValidCheck(ValidationCheck):
    """V5 / USL-12 — the policy holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Policy holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """USL-02 / SMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/DF-2 referenced, redefined nowhere (USL-02)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (USL-02 / SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (USL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """USL-15 / SPL-09 / C7 — no policy-engine/IAM/gateway/protocol/vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/policy-engine/IAM selected (USL-15 / SPL-09)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology/policy-engine was selected (USL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """USL-13 / USL-15 / SPL-07/09 / C7 — the policy confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Policy confers no authority and embeds no secret (USL-13/15 / SPL-07/09)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("policy confers authority (USL-13 / USL-15 / SPL-07)")
        if subject.embeds_secret:
            return self._failed("policy embeds a secret (USL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§17 / AC-7 — the No-Orphan lineage is rooted at SMC-09 and closes to 11-SERVICE."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at SMC-09 and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: PolicyValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def policy_checks() -> tuple[ValidationCheck, ...]:
    """The full policy-layer validation suite (deterministically ordered by the engine)."""
    return (
        PolicyTypedCheck(),
        PolicyIdentifiedCheck(),
        PolicyValueFidelityCheck(),
        PolicyClassifiedCheck(),
        PolicyBoundaryBoundCheck(),
        PolicyDeclarativeCheck(),
        PolicyRuntimeReuseCheck(),
        PolicyDataByReferenceCheck(),
        PolicyGovernedScopeCheck(),
        PolicyPrecedenceCheck(),
        PolicyLifecycleRecordingCheck(),
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


def validate_policy(
    policy: Policy,
    trace: PolicyTraceabilityRecord,
    *,
    strict: bool = False,
) -> ServiceValidation:
    """Validate ``policy`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = PolicyValidationSubject.from_policy(policy, trace)
    engine = ValidationEngine(policy_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ServiceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "POLICY_BLUEPRINT_ID",
    "PolicyValidationSubject",
    "policy_checks",
    "validate_policy",
]
