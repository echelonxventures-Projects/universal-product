"""EC3-B10-U10 — Relationship validation (meta-validity V1…V5 + UDL + DRA conformance).

This module proves a realized :class:`~data.relationship.RelationshipObject` is
**META-VALID** (DATA-005 §8, V1…V5), **Data-law conformant** (DATA-001 §7, esp. **UDL-09
Relationship by Reference**, UDL-03, UDL-04/05, UDL-02, UDL-10, UDL-15), and satisfies the
Relationship contracts (DATA-008 §10, DRA-K1…K5 + the integrity rules DRA-C1…C5) by
running a suite of deterministic, data-layer checks through the **CERTIFIED EC-1
Validation Engine** (:class:`engine.validation.executor.ValidationEngine`) and enforcing
the EC-1 acceptance gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable
:class:`RelationshipValidationSubject`, so an identical relationship object yields a
byte-identical report, evidence, and acceptance decision (VC-4). Every check is
**blocking**. A subset of check ids (``meta-class-single``, ``meta-relationships-closed``,
``foundation-reuse-integrity``, ``data-value-fidelity``, ``founding-acyclic``,
``provisional-state-disclosure``, ``traceability-rooted``) is **shared with the CERTIFIED
DMC-01 surface**, so the DMC-01 CCE ten-gate suite (:func:`data.certification.cce_gates`)
is reused verbatim by the Relationship certification (UDL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.relationship import RelationshipObject
from data.relationship_meta import (
    RELATIONSHIP_META_CLASS,
    RELATIONSHIP_RELATIONSHIPS,
    RelationshipState,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Relationship object realizes (its meta-class) — used by the report.
RELATIONSHIP_BLUEPRINT_ID = RELATIONSHIP_META_CLASS

_STATE_VALUES = frozenset(s.value for s in RelationshipState)
_META_RELATIONSHIPS = frozenset(RELATIONSHIP_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class RelationshipValidationSubject:
    """A normalized, immutable projection of a Relationship object that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1 ``ValidationEngine``
    consumes) plus the object's meta-facts. Holds no runtime state and no wall-clock, so
    it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    value_digest: str
    source_id: str
    target_entity_id: str
    endpoint_ids: tuple[str, ...]
    absorbs_endpoints: bool
    kind: str
    typed: bool
    by_reference: bool
    cardinality: str
    cardinality_explicit: bool
    direction: str
    directionality_declared: bool
    founding: bool
    endpoints_resolve: bool
    endpoints_distinct: bool
    founding_acyclic_rule: bool
    policy_ref: str
    binds_policy_by_reference: bool
    navigates_by_reference: bool
    enforces: bool
    recorded: bool
    verdict: str
    schema_ref: str
    schema_describable: bool
    names_technology: bool
    selects_technology: bool
    version: str
    relationships: tuple[str, ...]
    relationship_state: str
    founding_acyclic: bool
    confers_authority: bool
    embeds_secret: bool
    redefines_el1: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    image_reference: str
    disclosure: dict[str, Any]

    @classmethod
    def from_relationship(
        cls, relationship: RelationshipObject, trace: TraceabilityRecord
    ) -> RelationshipValidationSubject:
        """Project ``relationship`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=relationship.relationship_id,
            blueprint_id=RELATIONSHIP_BLUEPRINT_ID,
            meta_class=relationship.meta_class,
            name=relationship.name,
            type_tag=relationship.type_tag,
            value_digest=relationship.structure_digest,
            source_id=relationship.source_id(),
            target_entity_id=relationship.target_id(),
            endpoint_ids=relationship.endpoint_ids(),
            absorbs_endpoints=relationship.absorbs_endpoints(),
            kind=relationship.kind.value,
            typed=relationship.is_typed(),
            by_reference=relationship.is_by_reference(),
            cardinality=relationship.cardinality.value,
            cardinality_explicit=relationship.cardinality_explicit(),
            direction=relationship.direction.value,
            directionality_declared=relationship.directionality_declared(),
            founding=relationship.is_founding(),
            endpoints_resolve=relationship.endpoints_resolve(),
            endpoints_distinct=relationship.endpoints_distinct(),
            founding_acyclic_rule=relationship.founding_acyclic_rule(),
            policy_ref=relationship.policy_ref,
            binds_policy_by_reference=relationship.binds_policy_by_reference(),
            navigates_by_reference=relationship.navigates_by_reference(),
            enforces=relationship.enforces(),
            recorded=relationship.is_recorded(),
            verdict=relationship.verdict.value,
            schema_ref=relationship.schema_ref,
            schema_describable=relationship.is_schema_describable(),
            names_technology=relationship.names_technology(),
            selects_technology=relationship.selects_technology(),
            version=relationship.version,
            relationships=relationship.meta_relationships(),
            relationship_state=relationship.state.value,
            founding_acyclic=relationship.is_founding_acyclic(),
            confers_authority=relationship.confers_authority(),
            embeds_secret=relationship.embeds_secret(),
            redefines_el1=relationship.redefines_el1(),
            substrate_refs=tuple(relationship.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            image_reference="",  # a relationship is a record, not a deployable image
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Data-layer validation checks (each maps to explicit V*/UDL*/DRA* obligations)
# ---------------------------------------------------------------------------


class RelationshipTypedCheck(ValidationCheck):
    """UDL-03 / DRA-02 / DRA-K1 — relationship bears a non-empty ENG-004 type + DXH-04 kind."""

    check_id = "relationship-typed"
    severity = Severity.BLOCKING
    description = "Relationship bears a non-empty ENG-004 type_tag and DXH-04 kind (DRA-02)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("relationship is untyped (DRA-02 / DRA-K1 / UDL-03)")
        if not subject.typed or not subject.kind:
            return self._failed("relationship has no DXH-04 kind (DRA-02)", kind=subject.kind)
        return self._passed(type_tag=subject.type_tag, kind=subject.kind)


class RelationshipNamedCheck(ValidationCheck):
    """DRA-K1 — relationship has an explicit, decidable name."""

    check_id = "relationship-named"
    severity = Severity.BLOCKING
    description = "Relationship has an explicit, non-empty name."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.name.strip():
            return self._failed("relationship is unnamed")
        return self._passed(name=subject.name)


class RelationshipIdentifiedCheck(ValidationCheck):
    """UDL-04/05 / DRA-K1 / DMK-01 / C1 — object is identified (ENG-001), object-borne."""

    check_id = "relationship-identified"
    severity = Severity.BLOCKING
    description = "Relationship bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-RELATIONSHIP-"):
            return self._failed(
                "relationship has no ENG-001 identity (UDL-04)", id=subject.target_id
            )
        return self._passed(relationship_id=subject.target_id)


class RelationshipValueFidelityCheck(ValidationCheck):
    """UDL-06 (transitive) / C3 — the object's representation is ENG-003 value-faithful."""

    check_id = "data-value-fidelity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Relationship representation is content-addressed via ENG-003 encoding (UDL-06)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("relationship representation is not value-faithful (UDL-06)")
        return self._passed(value_digest=digest)


class RelationshipRelatesEndpointsCheck(ValidationCheck):
    """DMR-03 / DOR-03 / DRA-C5 — object relates two CERTIFIED entities by reference."""

    check_id = "relationship-relates-endpoints"
    severity = Severity.BLOCKING
    description = "Relationship relates two CERTIFIED entities by reference; owns none (DMR-03)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        for role, eid in (("source", subject.source_id), ("target", subject.target_entity_id)):
            if not eid.startswith("UCOS-"):
                return self._failed(
                    f"the {role} endpoint is not a CERTIFIED entity (DMR-03)", endpoint=eid
                )
        if subject.absorbs_endpoints:
            return self._failed("relationship owns/absorbs its endpoints (DRA-C5 / DMX-02)")
        return self._passed(endpoints=list(subject.endpoint_ids))


class RelationshipByReferenceCheck(ValidationCheck):
    """DRA-01 / UDL-09 — the relationship IS an ENG-005 reference (no new construct)."""

    check_id = "relationship-by-reference"
    severity = Severity.BLOCKING
    description = "Relationship is an ENG-005 reference; adds no connection construct (DRA-01)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.by_reference:
            return self._failed("relationship is not an ENG-005 reference (DRA-01 / UDL-09)")
        if subject.redefines_el1:
            return self._failed("relationship redefines a connection construct (UDL-09)")
        return self._passed()


class RelationshipCardinalityCheck(ValidationCheck):
    """DRA-04 / DRA-C3 — the relationship declares explicit, decidable cardinality."""

    check_id = "relationship-cardinality-explicit"
    severity = Severity.BLOCKING
    description = "Relationship declares explicit, decidable cardinality (DRA-04 / DRA-C3)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.cardinality_explicit or not subject.cardinality:
            return self._failed("relationship cardinality is not explicit (DRA-04 / DRA-C3)")
        return self._passed(cardinality=subject.cardinality)


class RelationshipDirectionalityCheck(ValidationCheck):
    """DRA-06 — the relationship declares a directionality consistent with its kind."""

    check_id = "relationship-directionality-declared"
    severity = Severity.BLOCKING
    description = "Relationship declares directed/peer consistently with its kind (DRA-06)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.directionality_declared:
            return self._failed(
                "relationship directionality is undeclared/inconsistent (DRA-06)",
                direction=subject.direction,
                kind=subject.kind,
            )
        return self._passed(direction=subject.direction)


class RelationshipReferentialIntegrityCheck(ValidationCheck):
    """DRA-05 / DRA-C2 / DRA-K4 — every endpoint resolves to an existing entity identity."""

    check_id = "relationship-referential-integrity"
    severity = Severity.BLOCKING
    description = "Every relationship endpoint resolves to an existing entity (DRA-05 / DRA-C2)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.endpoints_resolve:
            return self._failed("a relationship endpoint does not resolve (DRA-05 / DRA-K4)")
        return self._passed(endpoints=list(subject.endpoint_ids))


class RelationshipFoundingAcyclicRuleCheck(ValidationCheck):
    """DRA-03 / DRA-C1 / DRA-C4 — a founding relationship relates distinct entities."""

    check_id = "relationship-founding-acyclic-rule"
    severity = Severity.BLOCKING
    description = "A founding relationship relates distinct entities; no self-founding (DRA-03)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic_rule:
            return self._failed("a founding relationship self-founds (DRA-03 / DRA-C1)")
        return self._passed(founding=subject.founding, distinct=subject.endpoints_distinct)


class RelationshipNonAbsorbingCheck(ValidationCheck):
    """DRA-C5 / DMX-02 — the relationship references identities; it absorbs no entity content."""

    check_id = "relationship-non-absorbing"
    severity = Severity.BLOCKING
    description = "Relationship references entity identities; it absorbs no content (DRA-C5)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if subject.absorbs_endpoints:
            return self._failed("relationship absorbs entity content (DRA-C5 / DMX-02)")
        return self._passed()


class RelationshipBindsPolicyByReferenceCheck(ValidationCheck):
    """DMR-11 / §7 / DRA-K3 — navigation/integrity-check binds a RUNTIME policy reference."""

    check_id = "relationship-binds-policy-by-reference"
    severity = Severity.BLOCKING
    description = "Navigation/integrity binds a RUNTIME policy reference; no engine redefined."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.policy_ref.startswith("UCOS-POLICY-REF:"):
            return self._failed(
                "navigation does not bind a RUNTIME policy reference (DMR-11 / DRA-K3)"
            )
        if not subject.binds_policy_by_reference or not subject.navigates_by_reference:
            return self._failed("relationship navigation is not bound by reference (DMR-11 / §7)")
        return self._passed(policy_ref=subject.policy_ref)


class RelationshipVersionedCheck(ValidationCheck):
    """DRA-08 / UDL-12 — the object records an explicit version (additive/append-only)."""

    check_id = "relationship-versioned"
    severity = Severity.BLOCKING
    description = "Relationship object records an explicit version (DRA-08 / UDL-12)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("relationship object records no version (DRA-08)")
        return self._passed(version=subject.version)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / DMI-01 — the object instantiates exactly one meta-class (DMC-04)."""

    check_id = "meta-class-single"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Relationship object instantiates exactly the DMC-04 meta-class (V1)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if subject.meta_class != RELATIONSHIP_META_CLASS:
            return self._failed("meta-class is not DMC-04 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / DMI-02 — every relationship used lies within DMR-01…12 (uses 03/04/10/11)."""

    check_id = "meta-relationships-closed"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "All relationship meta-relationships are within DMR-01…12 (V2)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (DRA-K1 typed+ref, K2 acyclic, K4 integrity, K5 no-tech)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DRA-K1 (typed+ref), K2 (acyclic), K3/K4 (cardinality/integrity), K5 (no-tech)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # DRA-K1 typed
            and subject.name.strip()  # named
            and subject.target_id  # DMK-01 identified
            and subject.by_reference  # DRA-K1 ENG-005 reference
            and subject.founding_acyclic_rule  # DRA-K2 founding acyclic
            and subject.founding_acyclic  # DMK-03 acyclic
            and subject.cardinality_explicit  # DRA-K3 cardinality declared
            and subject.directionality_declared  # DRA-06 direction declared
            and subject.endpoints_resolve  # DRA-K4 referential integrity
            and subject.binds_policy_by_reference  # navigation by reference
            and not subject.confers_authority  # DRA-K5 no authority
            and not subject.names_technology  # DRA-K5 no technology
        )
        if not ok:
            return self._failed("DRA-K1/K2/K3/K4/K5 (DMK-01/03/05/08) not satisfied (V3)")
        return self._passed(constraints=["DRA-K1", "DRA-K2", "DRA-K3", "DRA-K4", "DRA-K5"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMK-03 — the founding/relationship graph is acyclic."""

    check_id = "founding-acyclic"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The relationship object's founding graph is acyclic (V4 / DMK-03)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding/relationship graph is not acyclic (V4)")
        return self._passed()


class RelationshipValidStateCheck(ValidationCheck):
    """V5 / UDL-12 — the object holds a valid DOS-01…05 lifecycle state."""

    check_id = "relationship-valid"
    severity = Severity.BLOCKING
    description = "Relationship object holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if subject.relationship_state not in _STATE_VALUES:
            return self._failed("invalid relationship state (V5)", state=subject.relationship_state)
        return self._passed(state=subject.relationship_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UDL-02 / DMI-05 / VC-5 — EL-1 + DMC-02 + RL-F2 reused by reference only."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + DMC-02 + RL-F2 substrate referenced, redefined nowhere (UDL-02)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/DMC-02/RL-F2 primitive was redefined (UDL-02)")
        if not subject.substrate_refs:
            return self._failed("no EL-1 substrate reference recorded (UDL-02)")
        if subject.absorbs_endpoints:
            return self._failed("the certified entity model was owned, not referenced (DMX-02)")
        if not subject.binds_policy_by_reference:
            return self._failed("RUNTIME policy was not bound by reference (UDL-02 / §7)")
        return self._passed(substrate=list(subject.substrate_refs))


class RelationshipIndependenceCheck(ValidationCheck):
    """UDL-09/11 / DRA-09 / DRA-K5 / C6 — object names no connection technology (material)."""

    check_id = "relationship-independence"
    severity = Severity.BLOCKING
    description = "No join/foreign-key/graph/database technology named (UDL-09 / DRA-K5)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.selects_technology or subject.image_reference:
            return self._failed(
                "a join/foreign-key/graph/database technology was named (UDL-09 / DRA-K5)"
            )
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UDL-15 / DRA-09 / C7 — the object confers no authority, holds no secret, selects no tech."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Relationship confers no authority, embeds no secret, selects no tech (UDL-15)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("relationship confers authority (UDL-15 / DRA-09)")
        if subject.embeds_secret:
            return self._failed("relationship embeds a secret (UDL-15 / RR-07)")
        if subject.selects_technology:
            return self._failed("relationship selects technology (UDL-15 / DRA-K5)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§16 / AC — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at DMC-04 and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: RelationshipValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def relationship_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
    return (
        RelationshipTypedCheck(),
        RelationshipNamedCheck(),
        RelationshipIdentifiedCheck(),
        RelationshipValueFidelityCheck(),
        RelationshipRelatesEndpointsCheck(),
        RelationshipByReferenceCheck(),
        RelationshipCardinalityCheck(),
        RelationshipDirectionalityCheck(),
        RelationshipReferentialIntegrityCheck(),
        RelationshipFoundingAcyclicRuleCheck(),
        RelationshipNonAbsorbingCheck(),
        RelationshipBindsPolicyByReferenceCheck(),
        RelationshipVersionedCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        RelationshipValidStateCheck(),
        FoundationReuseIntegrityCheck(),
        RelationshipIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class RelationshipValidation:
    """The bundled outcome of validating a Relationship object (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_relationship(
    relationship: RelationshipObject, trace: TraceabilityRecord, *, strict: bool = False
) -> RelationshipValidation:
    """Validate ``relationship`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected object raises via the
    EC-1 acceptance gate.
    """
    subject = RelationshipValidationSubject.from_relationship(relationship, trace)
    engine = ValidationEngine(relationship_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return RelationshipValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "RELATIONSHIP_BLUEPRINT_ID",
    "RelationshipValidationSubject",
    "RelationshipValidation",
    "relationship_checks",
    "validate_relationship",
]
