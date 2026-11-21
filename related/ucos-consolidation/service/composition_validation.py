"""EC3-B11-U06 — Composition validation (meta-validity V1…V5 + USL conformance + SCO principles).

Proves a realized :class:`~service.composition.Composition` is **META-VALID** (SERVICE-005 §8,
V1…V5), **Service-law conformant** (SERVICE-001 §7), and **Composition-principle conformant**
(SERVICE-010 §4, SCO-01…10) by running deterministic checks through the **CERTIFIED EC-1
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
from service.composition import Composition
from service.composition_meta import COMPOSITION_META_CLASS, CompositionKind
from service.composition_traceability import CompositionTraceabilityRecord
from service.service_meta import META_RELATIONSHIPS, ServiceState
from service.service_validation import ServiceValidation

#: The blueprint id a Composition realizes (its meta-class) — used by the EC-1 report.
COMPOSITION_BLUEPRINT_ID = COMPOSITION_META_CLASS

_KIND_VALUES = frozenset(k.value for k in CompositionKind)
_STATE_VALUES = frozenset(s.value for s in ServiceState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class CompositionValidationSubject:
    """A normalized, immutable projection of a Composition that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    member_refs: tuple[str, ...]
    contract_ref: str
    composition_ref: str
    integration_ref: str
    invocation_ref: str
    data_refs: tuple[str, ...]
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding: bool
    founding_acyclic: bool
    composes_members: bool
    topology_valid: bool
    contract_bound: bool
    platform_reuse: bool
    data_by_reference: bool
    invocation_by_reference: bool
    references_resolve: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_composition(
        cls, composition: Composition, trace: CompositionTraceabilityRecord
    ) -> CompositionValidationSubject:
        """Project ``composition`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=composition.composition_id,
            blueprint_id=COMPOSITION_BLUEPRINT_ID,
            meta_class=composition.meta_class,
            type_tag=composition.type_tag,
            kind=composition.kind.value,
            value_digest=composition.value_digest,
            member_refs=composition.member_refs,
            contract_ref=composition.contract_ref,
            composition_ref=composition.composition_ref,
            integration_ref=composition.integration_ref,
            invocation_ref=composition.invocation_ref,
            data_refs=composition.data_refs,
            relationships=composition.meta_relationships(),
            lifecycle_state=composition.state.value,
            founding=composition.is_founding(),
            founding_acyclic=composition.is_founding_acyclic(),
            composes_members=composition.composes_members(),
            topology_valid=composition.topology_valid(),
            contract_bound=composition.contract_bound(),
            platform_reuse=composition.platform_reuse(),
            data_by_reference=composition.data_by_reference(),
            invocation_by_reference=composition.invocation_by_reference(),
            references_resolve=composition.references_resolve(),
            confers_authority=composition.confers_authority(),
            selects_technology=composition.selects_technology(),
            embeds_secret=composition.embeds_secret(),
            redefines_foundation=composition.redefines_foundation(),
            substrate_refs=tuple(composition.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),
        )


# ---------------------------------------------------------------------------
# Composition-layer validation checks
# ---------------------------------------------------------------------------


class CompositionTypedCheck(ValidationCheck):
    """USL-03 / SCO-01 / C1 — the composition is typed (non-empty ENG-004 type)."""

    check_id = "composition-typed"
    severity = Severity.BLOCKING
    description = "Composition bears a non-empty ENG-004 type_tag (USL-03 / SCO-01)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("composition is untyped (USL-03)")
        return self._passed(type_tag=subject.type_tag)


class CompositionIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SCO-02 / C1 — the composition is identified (ENG-001) and object-borne."""

    check_id = "composition-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Composition bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-COMPOSITION-"):
            return self._failed("composition has no ENG-001 identity (USL-04)")
        if not subject.value_digest:
            return self._failed("composition is not object-borne (no value digest) (USL-05)")
        return self._passed(composition_id=subject.target_id)


class CompositionValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the composition core round-trips through the EC-1 canonical encoding.

    Emitted under the shared id ``service-value-fidelity`` so the reused CCE Gate-3
    aggregates it without duplicating gate logic.
    """

    check_id = "service-value-fidelity"
    severity = Severity.BLOCKING
    description = "Composition core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("composition core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class CompositionClassifiedCheck(ValidationCheck):
    """SXH-06 / SXC-02 — the composition is classified by exactly one kind."""

    check_id = "composition-classified"
    severity = Severity.BLOCKING
    description = "Composition is classified by an SXH-06 kind (single-facet, SXC-02)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("composition kind is outside SXH-06", kind=subject.kind)
        return self._passed(kind=subject.kind)


class CompositionComposesMembersCheck(ValidationCheck):
    """SMR-05 / SOR-05 / SCO-03 — the composition composes ≥1 member by ENG-005 reference."""

    check_id = "composition-composes-members"
    severity = Severity.BLOCKING
    description = "Composition composes ≥1 member by ENG-005 reference (SMR-05 / SCO-03)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.composes_members:
            return self._failed("composition composes no member (SMR-05 / SCO-03)")
        return self._passed(members=len(subject.member_refs))


class CompositionTopologyValidCheck(ValidationCheck):
    """SCO-C2/C3 — the member arity matches the composition kind (topology decidable)."""

    check_id = "composition-topology-valid"
    severity = Severity.BLOCKING
    description = "Member arity matches the SXH-06 kind (SCO-C2 peer / SCO-C3 delegation)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.topology_valid:
            return self._failed(
                "composition topology invalid for kind (SCO-C2/C3)",
                kind=subject.kind,
                members=len(subject.member_refs),
            )
        return self._passed(kind=subject.kind, members=len(subject.member_refs))


class CompositionContractBoundCheck(ValidationCheck):
    """SMR-02 / SOR-02 / SCO-05 / SCO-K2 — the composition is bound by a composition contract."""

    check_id = "composition-contract-bound"
    severity = Severity.BLOCKING
    description = "Composition is bound by a composition contract by reference (SMR-02 / SCO-05)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.contract_bound:
            return self._failed("composition is bound by no contract (SMR-02 / SCO-05)")
        return self._passed(contract_ref=subject.contract_ref)


class CompositionPlatformReuseCheck(ValidationCheck):
    """SMR-12 / SCO-06 — composes-as/integrates-as PLATFORM-010/011 by reference."""

    check_id = "composition-platform-reuse"
    severity = Severity.BLOCKING
    description = "Composition reuses PLATFORM-010/011 by ENG-005 reference (SMR-12 / SCO-06)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.platform_reuse:
            return self._failed("composition does not reuse PLATFORM composition (SMR-12 / SCO-06)")
        return self._passed(
            composition_ref=subject.composition_ref, integration_ref=subject.integration_ref
        )


class CompositionDataByReferenceCheck(ValidationCheck):
    """USL-11 / SCO-07 / SMR-13 — cross-composition data references DF-2 by reference."""

    check_id = "composition-data-by-reference"
    severity = Severity.BLOCKING
    description = "Cross-composition data references DF-2 (SMR-13, by reference; USL-11 / SCO-07)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.data_by_reference:
            return self._failed("a cross-composition data reference is not a valid DF-2 reference")
        return self._passed(data_refs=len(subject.data_refs))


class CompositionInvocationByReferenceCheck(ValidationCheck):
    """§7 composition-invoke / USL-10 — delegated invocation binds RL-F2 by ENG-005 reference."""

    check_id = "composition-invocation-by-reference"
    severity = Severity.BLOCKING
    description = "Delegated invocation binds RL-F2 by ENG-005 reference (§7 / USL-10)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.invocation_by_reference:
            return self._failed("no RL-F2 delegated-invocation reference (§7 / USL-10)")
        return self._passed(invocation_ref=subject.invocation_ref)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / SMI-01 — the composition instantiates exactly one meta-class (SMC-06)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Composition instantiates exactly the SMC-06 meta-class (V1)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.meta_class != COMPOSITION_META_CLASS:
            return self._failed("meta-class is not SMC-06 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / SMI-02 — every relationship used lies within SMR-01…13."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All composition relationships are within SMR-01…13 (V2)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside SMR-01…13 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — SMK-01 (typed/identified/object) + SMK-02 (contract-bound) +
    SMK-06/07 (platform/data references resolve) + SMK-05 (invocation resolves)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01/02/05/06/07 hold (typed/identified, contract-bound, refs resolve) (V3)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("SMK-01 not satisfied (V3)")
        if not subject.contract_bound:
            return self._failed("SMK-02 not satisfied: composition is uncontracted (V3)")
        if not subject.references_resolve:
            return self._failed("SMK-05/06/07 not satisfied: a reference does not resolve (V3)")
        return self._passed(constraints=["SMK-01", "SMK-02", "SMK-05", "SMK-06", "SMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMK-03 / SCO-04 / SCO-C1 — the founding graph (composes/provides) is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The composition's founding graph is acyclic (V4 / SMK-03 / SCO-C1)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4 / SCO-04)")
        return self._passed(founding=subject.founding)


class LifecycleValidCheck(ValidationCheck):
    """V5 / USL-12 — the composition holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Composition holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """USL-02 / SMI-05 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/PL-F2/RL-F2/DF-2 referenced, redefined nowhere (USL-02)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (USL-02 / SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (USL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """USL-15 / SCO-09 / C7 — no service-mesh/gateway/protocol/framework/vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete technology/mesh/gateway selected (USL-15 / SCO-09)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology/mesh/gateway was selected (USL-15)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """USL-15 / SCO-09 / C7 — the composition confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Composition confers no authority and embeds no secret (USL-15 / SCO-09)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("composition confers authority (USL-15)")
        if subject.embeds_secret:
            return self._failed("composition embeds a secret (USL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted at SMC-06 and closes to 11-SERVICE."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at SMC-06 and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: CompositionValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def composition_checks() -> tuple[ValidationCheck, ...]:
    """The full composition-layer validation suite (deterministically ordered by the engine)."""
    return (
        CompositionTypedCheck(),
        CompositionIdentifiedCheck(),
        CompositionValueFidelityCheck(),
        CompositionClassifiedCheck(),
        CompositionComposesMembersCheck(),
        CompositionTopologyValidCheck(),
        CompositionContractBoundCheck(),
        CompositionPlatformReuseCheck(),
        CompositionDataByReferenceCheck(),
        CompositionInvocationByReferenceCheck(),
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


def validate_composition(
    composition: Composition, trace: CompositionTraceabilityRecord, *, strict: bool = False
) -> ServiceValidation:
    """Validate ``composition`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = CompositionValidationSubject.from_composition(composition, trace)
    engine = ValidationEngine(composition_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ServiceValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "COMPOSITION_BLUEPRINT_ID",
    "CompositionValidationSubject",
    "composition_checks",
    "validate_composition",
]
