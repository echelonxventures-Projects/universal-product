"""EC3-B13-U03 — Network Resource validation (meta-validity WF + UIL conformance).

This module proves a realized :class:`~infrastructure.network.NetworkResource` is
**META-VALID** (INFRASTRUCTURE-005 §5/§6, WF-1…12 + UIMM-CONF) and **Infrastructure-law
conformant** (INFRASTRUCTURE-001 §7, UIL-01…15) by running a suite of deterministic,
infrastructure-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate (:func:`engine.validation.gates.enforce_acceptance`). Validation evidence is
produced with the EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`NetworkValidationSubject` (the
type-independent projection the EC-1 engine consumes), so an identical resource yields a
byte-identical report, evidence, and acceptance decision (VC-4). Every check is
**blocking**: the verdict is PASS iff the resource satisfies every meta-validity and
Infrastructure-law obligation it is subject to — with WF-5 / UIL-08 (a Resource declares
capacity and locality) and **ICNW-03 / UIL-07 (connectivity honors isolation boundaries)**
the **governing, materially-exercised** obligations for this unit.
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
from infrastructure.network import INFRA_NETWORK_ID_PREFIX, NetworkResource
from infrastructure.network_meta import (
    ADMITTED_META_RELATIONSHIPS,
    INFRASTRUCTURE_META_CLASS,
    InfrastructureState,
)
from infrastructure.network_traceability import TraceabilityRecord

#: The blueprint id a Network Resource realizes (its meta-class).
NETWORK_BLUEPRINT_ID = INFRASTRUCTURE_META_CLASS

_STATE_VALUES = frozenset(s.value for s in InfrastructureState)
_ADMITTED_RELATIONSHIPS = frozenset(ADMITTED_META_RELATIONSHIPS)
_ID_PREFIX = f"{INFRA_NETWORK_ID_PREFIX}-"


@dataclass(frozen=True, slots=True)
class NetworkValidationSubject:
    """A normalized, immutable projection of a network resource that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the resource's meta-facts. Holds no runtime state
    and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    capacity_amount: int
    capacity_unit: str
    value_digest: str
    locality_ref: str
    link_count: int
    relationships: tuple[str, ...]
    lifecycle_state: str
    declares_mandatory_attributes: bool
    declares_capacity_and_locality: bool
    declares_connected_endpoints: bool
    honors_isolation_boundaries: bool
    connectivity_by_reference: bool
    founding_acyclic: bool
    references_resolve: bool
    declares_no_artificial_ceiling: bool
    is_resource: bool
    is_evaluative_facet: bool
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
    def from_resource(
        cls, resource: NetworkResource, trace: TraceabilityRecord
    ) -> NetworkValidationSubject:
        """Project ``resource`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=resource.resource_id,
            blueprint_id=NETWORK_BLUEPRINT_ID,
            meta_class=resource.meta_class,
            type_tag=resource.type_tag,
            capacity_amount=resource.capacity.amount,
            capacity_unit=resource.capacity.unit,
            value_digest=resource.value_digest,
            locality_ref=resource.locality_ref,
            link_count=len(resource.links),
            relationships=resource.meta_relationships(),
            lifecycle_state=resource.state.value,
            declares_mandatory_attributes=resource.declares_mandatory_attributes(),
            declares_capacity_and_locality=resource.declares_capacity_and_locality(),
            declares_connected_endpoints=resource.declares_connected_endpoints(),
            honors_isolation_boundaries=resource.honors_isolation_boundaries(),
            connectivity_by_reference=resource.connectivity_by_reference(),
            founding_acyclic=resource.is_founding_acyclic(),
            references_resolve=resource.references_resolve(),
            declares_no_artificial_ceiling=resource.declares_no_artificial_ceiling(),
            is_resource=resource.is_resource(),
            is_evaluative_facet=resource.is_evaluative_facet(),
            confers_authority=resource.confers_authority(),
            enacts_enforcement=resource.enacts_enforcement(),
            selects_technology=resource.selects_technology(),
            embeds_secret=resource.embeds_secret(),
            redefines_foundation=resource.redefines_foundation(),
            is_new_primitive=resource.is_new_primitive(),
            projects_completion=resource.projects_completion(),
            substrate_refs=tuple(resource.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Infrastructure-layer validation checks (each maps to explicit WF*/UIL*/ICNW* obligations)
# ---------------------------------------------------------------------------


class NetworkTypedCheck(ValidationCheck):
    """UIL-03 / ICNW-01 / C1 — the resource bears a non-empty ENG-004 Connectivity Class."""

    check_id = "infra-network-typed"
    severity = Severity.BLOCKING
    description = "Network resource bears a non-empty ENG-004 Connectivity Class type_tag (UIL-03)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("network resource is untyped (UIL-03)")
        return self._passed(type_tag=subject.type_tag)


class NetworkIdentifiedCheck(ValidationCheck):
    """UIL-04/05 / ICNW-02 / C1 — the resource is identified (ENG-001) and object-borne."""

    check_id = "infra-network-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Resource bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith(_ID_PREFIX):
            return self._failed("resource has no ENG-001 identity (UIL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("resource is not object-borne (no value digest) (UIL-05)")
        if not subject.declares_mandatory_attributes:
            return self._failed("resource lacks a mandatory meta-attribute (WF-1 / WF-5)")
        return self._passed(resource_id=subject.target_id)


class NetworkValueFidelityCheck(ValidationCheck):
    """ENG-003 / C3 — the resource core round-trips through the EC-1 canonical encoding."""

    check_id = "infra-network-value-fidelity"
    severity = Severity.BLOCKING
    description = "Resource core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("resource core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class NetworkDeclaresCapacityLocalityCheck(ValidationCheck):
    """WF-5 / UIL-08 / ICNW-02 / C4 — every Resource declares capacity and locality.

    A governing, materially-exercised obligation for the Network Resource: a Resource that
    omits either a quantified capacity or a locality reference is ill-formed.
    """

    check_id = "infra-network-declares-capacity-locality"
    severity = Severity.BLOCKING
    description = "Network resource declares a quantified capacity and a locality (WF-5 / UIL-08)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if subject.capacity_amount < 0 or not subject.capacity_unit.strip():
            return self._failed("resource omits a quantified capacity (WF-5 / ICNW-02)")
        if not subject.locality_ref.strip():
            return self._failed("resource omits its locality (WF-5 / ICNW-02)")
        if not subject.declares_capacity_and_locality:
            return self._failed("resource does not declare capacity and locality (WF-5)")
        return self._passed(
            capacity_amount=subject.capacity_amount,
            capacity_unit=subject.capacity_unit,
            locality_ref=subject.locality_ref,
        )


class NetworkDeclaresConnectedEndpointsCheck(ValidationCheck):
    """ICNW-02 / WF-2 / UIL-08 / C4 — the resource declares its connected endpoints."""

    check_id = "infra-network-declares-connected-endpoints"
    severity = Severity.BLOCKING
    description = "Network resource declares ≥1 typed connectivity link with resolving endpoints."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if subject.link_count < 1:
            return self._failed("resource declares no connected endpoints (ICNW-02)")
        if not subject.declares_connected_endpoints:
            return self._failed("a connectivity endpoint does not resolve (ICNW-02 / WF-2)")
        return self._passed(link_count=subject.link_count)


class NetworkConnectivityByReferenceCheck(ValidationCheck):
    """ICNW-01 / WF-2 / UIL-09 — connectivity is a typed ENG-005 reference (no new construct)."""

    check_id = "infra-network-connectivity-by-reference"
    severity = Severity.BLOCKING
    description = "Connectivity is a typed ENG-005 reference; no new connection construct."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if not subject.connectivity_by_reference:
            return self._failed(
                "connectivity is not expressed as a typed ENG-005 reference (ICNW-01 / UIL-09)"
            )
        return self._passed(link_count=subject.link_count)


class NetworkHonorsBoundariesCheck(ValidationCheck):
    """ICNW-03 / UIL-07 / C4 — connectivity honors isolation boundaries.

    THE distinguishing, materially-exercised Network obligation: every cross-boundary link
    declares its isolation boundary by a typed ENG-005 reference.
    """

    check_id = "infra-network-honors-boundaries"
    severity = Severity.BLOCKING
    description = "Cross-boundary connectivity declares a typed isolation boundary (ICNW-03)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if not subject.honors_isolation_boundaries:
            return self._failed(
                "a cross-boundary link omits its typed isolation boundary (ICNW-03 / UIL-07)"
            )
        return self._passed()


class MetaClassSingleCheck(ValidationCheck):
    """WF-1 — the resource instantiates exactly one leaf meta-class (NetworkResource)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Resource instantiates exactly the NetworkResource meta-class (WF-1)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if subject.meta_class != INFRASTRUCTURE_META_CLASS:
            return self._failed(
                "meta-class is not NetworkResource (WF-1)", meta_class=subject.meta_class
            )
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """UIL-09 — every relationship used lies within the admitted meta-relationship set."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All resource relationships are within the admitted UIMM set (UIL-09)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _ADMITTED_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside admitted set (UIL-09)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """WF-1/2 — mandatory meta-attributes declared and every reference resolves."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "Mandatory meta-attributes declared (WF-1) and references resolve (WF-2)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("mandatory meta-attributes not all declared (WF-1)")
        if not subject.references_resolve:
            return self._failed("a reference does not resolve (WF-2)")
        return self._passed(constraints=["WF-1", "WF-2"])


class FoundingAcyclicCheck(ValidationCheck):
    """WF-3 / UIL-09 — the founding graph is acyclic (connectivity is peer, non-founding)."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The resource's founding graph is acyclic (WF-3 / UIL-09)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (WF-3)")
        return self._passed()


class ResourceKindCheck(ValidationCheck):
    """WF-5 — the construct is a Resource (capacity/locality) and not an EvaluativeFacet."""

    check_id = "infra-network-is-resource"
    severity = Severity.BLOCKING
    description = "Construct is a Resource (WF-5) and not an EvaluativeFacet (WF-10 N/A)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if not subject.is_resource:
            return self._failed("construct is not a Resource (WF-5)")
        if subject.is_evaluative_facet:
            return self._failed("a Resource must not be an EvaluativeFacet (WF-10)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """INFRASTRUCTURE-003 §3 — the resource holds a valid forward-only lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Resource holds a valid forward-only lifecycle state (INFRASTRUCTURE-003 §3)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UIL-02 / VC-5 — frozen foundations reused by reference, redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1 referenced, redefined nowhere (UIL-02)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UIL-02)")
        if subject.is_new_primitive:
            return self._failed("resource is a new primitive (WF-11 / UIL-01)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UIL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class ConnectivityReferenceCheck(ValidationCheck):
    """UIL-09 / ICNW-01 / C5 — connectivity + locality bound by ENG-005 reference."""

    check_id = "connectivity-by-reference"
    severity = Severity.BLOCKING
    description = "Connectivity endpoints + locality bound by ENG-005 reference (UIL-09 / WF-2)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if not subject.connectivity_by_reference or not subject.locality_ref.strip():
            return self._failed("connectivity/locality reference missing (UIL-09 / WF-2)")
        return self._passed(link_count=subject.link_count, locality_ref=subject.locality_ref)


class ScalingUnboundedCheck(ValidationCheck):
    """UIL-13 / ICNW-04 / C6 — the resource declares no artificial capacity ceiling."""

    check_id = "scaling-unbounded"
    severity = Severity.BLOCKING
    description = "Resource declares no artificial ceiling; network scaling unbounded (UIL-13)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if not subject.declares_no_artificial_ceiling:
            return self._failed("resource declares an artificial ceiling (UIL-13 / ICNW-04)")
        return self._passed()


class TechnologyIndependenceCheck(ValidationCheck):
    """UIL-12 / UIL-15 / ICNW-05 / C7 — no transport/protocol/mesh/vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No concrete transport/protocol/mesh/vendor selected (UIL-12 / UIL-15)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete transport/technology was selected (UIL-12 / ICNW-05)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UIL-14/15 / ICNW-05 / C7 — confers no authority, enacts no enforcement, embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Resource confers no authority, enforces nothing, embeds no secret (UIL-14/15)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("resource confers authority (UIL-15)")
        if subject.enacts_enforcement:
            return self._failed("resource enacts enforcement (UIL-14)")
        if subject.embeds_secret:
            return self._failed("resource embeds a secret (UIL-15 / RR-07)")
        if subject.projects_completion:
            return self._failed("resource projects completion (WF-12)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§5 — the No-Orphan lineage is rooted and closes to the 13-INFRASTRUCTURE anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at the meta-class, closed to 13-INFRASTRUCTURE."

    def evaluate(self, subject: NetworkValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("13-INFRASTRUCTURE@") for link in chain):
            return self._failed("lineage does not close to the 13-INFRASTRUCTURE anchor")
        return self._passed(links=len(chain))


def network_checks() -> tuple[ValidationCheck, ...]:
    """The full network-resource validation suite (deterministically ordered)."""
    return (
        NetworkTypedCheck(),
        NetworkIdentifiedCheck(),
        NetworkValueFidelityCheck(),
        NetworkDeclaresCapacityLocalityCheck(),
        NetworkDeclaresConnectedEndpointsCheck(),
        NetworkConnectivityByReferenceCheck(),
        NetworkHonorsBoundariesCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        ResourceKindCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        ConnectivityReferenceCheck(),
        ScalingUnboundedCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class NetworkValidation:
    """The bundled outcome of validating a resource (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_network(
    resource: NetworkResource, trace: TraceabilityRecord, *, strict: bool = False
) -> NetworkValidation:
    """Validate ``resource`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected resource raises via the
    EC-1 acceptance gate.
    """
    subject = NetworkValidationSubject.from_resource(resource, trace)
    engine = ValidationEngine(network_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return NetworkValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "NETWORK_BLUEPRINT_ID",
    "NetworkValidationSubject",
    "NetworkValidation",
    "network_checks",
    "validate_network",
]
