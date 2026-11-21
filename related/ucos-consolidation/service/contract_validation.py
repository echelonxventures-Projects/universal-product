"""EC3-B11-U03 — Contract validation (meta-validity V1…V5 + USL conformance + SCN principles).

Proves a realized :class:`~service.contract.Contract` is **META-VALID** (SERVICE-005 §8,
V1…V5), **Service-law conformant** (SERVICE-001 §7), and **Contract-principle conformant**
(SERVICE-007 §4, SCN-01…10) by running deterministic checks through the **CERTIFIED EC-1
Validation Engine**.

The suite emits the seven **generic** check ids the CCE ten-gate suite depends on so that
:func:`service.service_certification.cce_gates` is reused **verbatim**. The result is
bundled as the shared :class:`service.service_validation.ServiceValidation`.
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
from service.contract import Contract
from service.contract_meta import CONTRACT_META_CLASS, ContractKind
from service.contract_traceability import ContractTraceabilityRecord
from service.service_meta import META_RELATIONSHIPS, ServiceState
from service.service_validation import ServiceValidation

#: The blueprint id a Contract realizes (its meta-class) — used by the EC-1 report.
CONTRACT_BLUEPRINT_ID = CONTRACT_META_CLASS

_KIND_VALUES = frozenset(k.value for k in ContractKind)
_STATE_VALUES = frozenset(s.value for s in ServiceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class ContractValidationSubject:
    """A normalized, immutable projection of a Contract that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    effects: tuple[str, ...]
    faults: tuple[str, ...]
    policy_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    specifies_io: bool
    io_is_data: bool
    declares_effects_and_faults: bool
    policy_by_reference: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_contract(
        cls, contract: Contract, trace: ContractTraceabilityRecord
    ) -> ContractValidationSubject:
        """Project ``contract`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=contract.contract_id,
            blueprint_id=CONTRACT_BLUEPRINT_ID,
            meta_class=contract.meta_class,
            type_tag=contract.type_tag,
            kind=contract.kind.value,
            value_digest=contract.value_digest,
            inputs=contract.inputs,
            outputs=contract.outputs,
            effects=contract.effects,
            faults=contract.faults,
            policy_ref=contract.policy_ref,
            relationships=contract.meta_relationships(),
            lifecycle_state=contract.state.value,
            founding_acyclic=contract.is_founding_acyclic(),
            specifies_io=contract.specifies_io(),
            io_is_data=contract.io_is_data(),
            declares_effects_and_faults=contract.declares_effects_and_faults(),
            policy_by_reference=contract.policy_by_reference(),
            confers_authority=contract.confers_authority(),
            selects_technology=contract.selects_technology(),
            embeds_secret=contract.embeds_secret(),
            redefines_foundation=contract.redefines_foundation(),
            substrate_refs=tuple(contract.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),
        )


# ---------------------------------------------------------------------------
# Contract-layer validation checks
# ---------------------------------------------------------------------------


class ContractTypedCheck(ValidationCheck):
    """USL-03 / SCN-01 / C1 — the contract is classified by a non-empty ENG-004 type."""

    check_id = "contract-typed"
    severity = Severity.BLOCKING
    description = "Contract bears a non-empty ENG-004 type_tag (USL-03 / SCN-01)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("contract is untyped (USL-03)")
        return self._passed(type_tag=subject.type_tag)


class ContractIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SCN-02 / C1 — the contract is identified (ENG-001) and object-borne."""

    check_id = "contract-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Contract bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-CONTRACT-"):
            return self._failed("contract has no ENG-001 identity (USL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("contract is not object-borne (no value digest) (USL-05)")
        return self._passed(contract_id=subject.target_id)


class ContractValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the contract core round-trips through the EC-1 canonical encoding.

    Emitted under the shared id ``service-value-fidelity`` so the reused CCE Gate-3
    aggregates it without duplicating gate logic.
    """

    check_id = "service-value-fidelity"
    severity = Severity.BLOCKING
    description = "Contract core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("contract core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class ContractClassifiedCheck(ValidationCheck):
    """SXH-03 / SXC-02 — the contract is classified by exactly one Contract kind."""

    check_id = "contract-classified"
    severity = Severity.BLOCKING
    description = "Contract is classified by an SXH-03 kind (single-facet, SXC-02)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("contract kind is outside SXH-03", kind=subject.kind)
        return self._passed(kind=subject.kind)


class ContractExplicitSpecCheck(ValidationCheck):
    """USL-06 / SCN-03 — the contract is an explicit typed spec that declares its I/O."""

    check_id = "contract-explicit-spec"
    severity = Severity.BLOCKING
    description = "Contract explicitly declares its typed I/O structure (USL-06 / SCN-03)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if not subject.specifies_io:
            return self._failed("contract specifies neither inputs nor outputs (USL-06)")
        return self._passed(inputs=len(subject.inputs), outputs=len(subject.outputs))


class ContractIoIsDataCheck(ValidationCheck):
    """USL-11 / SCN-04 — the contract's I/O references DF-2-represented data by reference."""

    check_id = "contract-io-is-data"
    severity = Severity.BLOCKING
    description = "Contract I/O references DF-2 data (SMR-13, by reference; USL-11 / SCN-04)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if not subject.io_is_data:
            return self._failed("a contract I/O reference is not a valid DF-2 reference (SCN-04)")
        return self._passed()


class ContractDeclaresEffectsFaultsCheck(ValidationCheck):
    """SCN-05 / SMK-02 — the contract declares its effects and faults."""

    check_id = "contract-declares-effects-faults"
    severity = Severity.BLOCKING
    description = "Contract declares effects and faults (SCN-05 / SMK-02)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if not subject.declares_effects_and_faults:
            return self._failed("contract does not declare effects/faults (SCN-05)")
        return self._passed(effects=len(subject.effects), faults=len(subject.faults))


class ContractPolicyByReferenceCheck(ValidationCheck):
    """SCN-06 / USL-13 — applicable policy, when bound, is a non-enforcing reference."""

    check_id = "contract-policy-by-reference"
    severity = Severity.BLOCKING
    description = "Applicable policy (SOE-09) bound by reference; evaluative (SCN-06 / USL-13)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if not subject.policy_by_reference:
            return self._failed("policy_ref present but blank (SCN-06)")
        return self._passed(policy_ref=subject.policy_ref or "(none)")


class MetaClassSingleCheck(ValidationCheck):
    """V1 / SMI-01 — the contract instantiates exactly one meta-class (SMC-03)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Contract instantiates exactly the SMC-03 meta-class (V1)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if subject.meta_class != CONTRACT_META_CLASS:
            return self._failed("meta-class is not SMC-03 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / SMI-02 — every relationship used lies within SMR-01…13."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All contract relationships are within SMR-01…13 (V2)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside SMR-01…13 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints SMK-01 (typed/identified/object) + SMK-02 (typed I/O)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01 (typed/identified/object) and SMK-02 (typed I/O + effects/faults) (V3)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("SMK-01 not satisfied (V3)")
        if not (subject.io_is_data and subject.declares_effects_and_faults):
            return self._failed("SMK-02 not satisfied: typed I/O + effects/faults (V3)")
        return self._passed(constraints=["SMK-01", "SMK-02"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMK-03 — the founding graph (bound-by) is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The contract's founding graph is acyclic (V4 / SMK-03)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / USL-12 / SCN-08 — the contract holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Contract holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """USL-02 / SMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/DF-2 referenced, redefined nowhere (USL-02)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (USL-02 / SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (USL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """USL-15 / SCN-09 / C7 — no API/protocol/IDL/schema/framework/vendor technology selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/IDL/vendor selected (USL-15 / SCN-09)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology/IDL was selected (USL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """USL-15 / SCN-09 / C7 — the contract confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Contract confers no authority and embeds no secret (USL-15 / SCN-09)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("contract confers authority (USL-15)")
        if subject.embeds_secret:
            return self._failed("contract embeds a secret (USL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted at SMC-03 and closes to 11-SERVICE."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at SMC-03 and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: ContractValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def contract_checks() -> tuple[ValidationCheck, ...]:
    """The full contract-layer validation suite (deterministically ordered by the engine)."""
    return (
        ContractTypedCheck(),
        ContractIdentifiedCheck(),
        ContractValueFidelityCheck(),
        ContractClassifiedCheck(),
        ContractExplicitSpecCheck(),
        ContractIoIsDataCheck(),
        ContractDeclaresEffectsFaultsCheck(),
        ContractPolicyByReferenceCheck(),
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


def validate_contract(
    contract: Contract, trace: ContractTraceabilityRecord, *, strict: bool = False
) -> ServiceValidation:
    """Validate ``contract`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = ContractValidationSubject.from_contract(contract, trace)
    engine = ValidationEngine(contract_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ServiceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "CONTRACT_BLUEPRINT_ID",
    "ContractValidationSubject",
    "contract_checks",
    "validate_contract",
]
