"""EC3-B10-U02 — Attribute validation (meta-validity V1…V5 + UDL + DAA conformance).

This module proves a realized :class:`~data.attribute.Attribute` is **META-VALID**
(DATA-005 §8, V1…V5), **Data-law conformant** (DATA-001 §7, esp. **UDL-08 Attribute
Typedness**, UDL-06, UDL-03, UDL-02, UDL-09, UDL-11, UDL-15), and satisfies the
Attribute contracts (DATA-007 §10, DAA-K1/K2 + DAA-05/07 rules) by running a suite
of deterministic, data-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1
acceptance gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`AttributeValidationSubject`,
so an identical attribute yields a byte-identical report, evidence, and acceptance
decision (VC-4). Every check is **blocking**. A subset of check ids
(``meta-class-single``, ``meta-relationships-closed``, ``foundation-reuse-integrity``,
``data-value-fidelity``, ``founding-acyclic``, ``provisional-state-disclosure``,
``traceability-rooted``) is **shared with the CERTIFIED DMC-01 surface**, so the
DMC-01 CCE ten-gate suite (:func:`data.certification.cce_gates`) is reused verbatim
by the Attribute certification (UDL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.attribute import Attribute
from data.attribute_meta import (
    ATTRIBUTE_META_CLASS,
    ATTRIBUTE_RELATIONSHIPS,
    AttributeKind,
    AttributeState,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id an Attribute realizes (its meta-class) — used by the EC-1 report.
ATTRIBUTE_BLUEPRINT_ID = ATTRIBUTE_META_CLASS

_KIND_VALUES = frozenset(k.value for k in AttributeKind)
_STATE_VALUES = frozenset(s.value for s in AttributeState)
_META_RELATIONSHIPS = frozenset(ATTRIBUTE_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class AttributeValidationSubject:
    """A normalized, immutable projection of an Attribute that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the attribute's meta-facts. Holds no runtime
    state and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    kind: str
    value_digest: str
    value_datum_id: str
    absorbs_value: bool
    bearing_entity_ref: str
    nullable: bool
    nullability_declared: bool
    references_entity: str
    derived_from: tuple[str, ...]
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    confers_authority: bool
    embeds_secret: bool
    redefines_el1: bool
    selects_technology: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    storage_selected: bool
    image_reference: str
    disclosure: dict[str, Any]

    @classmethod
    def from_attribute(
        cls, attribute: Attribute, trace: TraceabilityRecord
    ) -> AttributeValidationSubject:
        """Project ``attribute`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=attribute.attribute_id,
            blueprint_id=ATTRIBUTE_BLUEPRINT_ID,
            meta_class=attribute.meta_class,
            name=attribute.name,
            type_tag=attribute.type_tag,
            kind=attribute.kind.value,
            value_digest=attribute.value_digest,
            value_datum_id=attribute.value_ref.datum_id,
            absorbs_value=attribute.absorbs_value(),
            bearing_entity_ref=attribute.bearing_entity_ref,
            nullable=attribute.nullable,
            nullability_declared=isinstance(attribute.nullable, bool),
            references_entity=attribute.references_entity,
            derived_from=tuple(attribute.derived_from),
            relationships=attribute.meta_relationships(),
            lifecycle_state=attribute.state.value,
            founding_acyclic=attribute.is_founding_acyclic(),
            confers_authority=attribute.confers_authority(),
            embeds_secret=attribute.embeds_secret(),
            redefines_el1=attribute.redefines_el1(),
            selects_technology=attribute.selects_technology(),
            substrate_refs=tuple(attribute.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            storage_selected=False,  # UDL-11 — no storage technology is ever selected
            image_reference="",  # an attribute is representation, not a deployable image
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Data-layer validation checks (each maps to explicit V*/UDL*/DAA* obligations)
# ---------------------------------------------------------------------------


class AttributeTypedCheck(ValidationCheck):
    """UDL-03/08 / DAA-01 / DAA-K1 — attribute is classified by a non-empty ENG-004 type."""

    check_id = "attr-typed"
    severity = Severity.BLOCKING
    description = "Attribute bears a non-empty ENG-004 type_tag (DAA-01 / UDL-08)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("attribute is untyped (DAA-01 / UDL-08)")
        return self._passed(type_tag=subject.type_tag)


class AttributeNamedCheck(ValidationCheck):
    """UDL-08 / DAA-04 / DAA-K1 — attribute has an explicit, decidable name."""

    check_id = "attr-named"
    severity = Severity.BLOCKING
    description = "Attribute has an explicit, non-empty name (DAA-04 / UDL-08)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if not subject.name.strip():
            return self._failed("attribute is unnamed (DAA-04 / UDL-08)")
        return self._passed(name=subject.name)


class AttributeIdentifiedCheck(ValidationCheck):
    """UDL-04/05 / DMK-01 / C1 — attribute is identified (ENG-001) and object-borne."""

    check_id = "attr-identified"
    severity = Severity.BLOCKING
    description = "Attribute bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-ATTR-"):
            return self._failed("attribute has no ENG-001 identity (UDL-04)", id=subject.target_id)
        return self._passed(attribute_id=subject.target_id)


class AttributeValueFidelityCheck(ValidationCheck):
    """UDL-06 / DAA-03 / C3 — the single value is an ENG-003 value (via the Datum ref)."""

    check_id = "data-value-fidelity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Attribute carries exactly one ENG-003 value digest (DAA-03 / UDL-06)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("value is not ENG-003 value-faithful (UDL-06)", digest=digest)
        return self._passed(value_digest=digest)


class AttributeValuesDatumCheck(ValidationCheck):
    """DMR-02 / DAA-03 / DMX-02 — attribute values a CERTIFIED Datum by reference (non-absorb)."""

    check_id = "attr-values-datum"
    severity = Severity.BLOCKING
    description = "Attribute values one CERTIFIED Datum by reference; absorbs it not (DMR-02)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if not subject.value_datum_id.startswith("UCOS-DATUM-"):
            return self._failed(
                "values target is not a CERTIFIED Datum identity (DMR-02)",
                datum=subject.value_datum_id,
            )
        if subject.absorbs_value:
            return self._failed("attribute absorbs its value's Datum model (DMX-02)")
        return self._passed(values=subject.value_datum_id)


class AttributeSingleBearingCheck(ValidationCheck):
    """DMR-01 / DAA-02 / DAA-K2 — attribute is borne by exactly one entity (by reference)."""

    check_id = "attr-single-bearing"
    severity = Severity.BLOCKING
    description = "Attribute is borne by exactly one entity reference (DMR-01 / DAA-02)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if not subject.bearing_entity_ref.strip():
            return self._failed("attribute floats free — no bearing entity (DAA-02)")
        return self._passed(borne_by=subject.bearing_entity_ref)


class AttributeNullabilityDeclaredCheck(ValidationCheck):
    """DAA-05 / DAA-C2 — nullability is declared explicitly, never implicit."""

    check_id = "attr-nullability-declared"
    severity = Severity.BLOCKING
    description = "Attribute nullability is an explicitly declared boolean (DAA-05)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if not subject.nullability_declared:
            return self._failed("attribute nullability is not declared explicitly (DAA-05)")
        return self._passed(nullable=subject.nullable)


class AttributeClassifiedCheck(ValidationCheck):
    """DMR-09 / DXH-03 — the attribute is classified by exactly one Attribute kind."""

    check_id = "attr-classified"
    severity = Severity.BLOCKING
    description = "Attribute is classified by a single DXH-03 kind (DMR-09 classified-by)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("attribute kind is outside DXH-03", kind=subject.kind)
        return self._passed(kind=subject.kind)


class AttributeRelationalByReferenceCheck(ValidationCheck):
    """DAA-07 / DAA-C4 — a relational attribute references a target entity, never embeds it."""

    check_id = "attr-relational-by-reference"
    severity = Severity.BLOCKING
    description = "A Relational-Attribute references a target entity via ENG-005 (DAA-07)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if subject.kind == AttributeKind.RELATIONAL.value:
            if not subject.references_entity.strip():
                return self._failed("relational attribute has no ENG-005 reference (DAA-07)")
            return self._passed(references_entity=subject.references_entity)
        # Non-relational attributes carry no cross-entity reference (vacuously satisfied).
        if subject.references_entity:
            return self._failed("non-relational attribute set a cross-entity reference (DAA-07)")
        return self._passed(relational=False)


class AttributeDerivationProvenanceCheck(ValidationCheck):
    """DAA-06 / DAA-C3 — a derived attribute records provenance (DME engine deferred)."""

    check_id = "attr-derivation-provenance"
    severity = Severity.BLOCKING
    description = "A Derived-Attribute records provenance; others carry none (DAA-06)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if subject.kind == AttributeKind.DERIVED.value:
            if not subject.derived_from:
                return self._failed("derived attribute records no provenance (DAA-06)")
            return self._passed(derived_from=list(subject.derived_from))
        if subject.derived_from:
            return self._failed("non-derived attribute declared provenance (DAA-06)")
        return self._passed(derived=False)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / DMI-01 — the attribute instantiates exactly one meta-class (DMC-03)."""

    check_id = "meta-class-single"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Attribute instantiates exactly the DMC-03 meta-class (V1)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if subject.meta_class != ATTRIBUTE_META_CLASS:
            return self._failed("meta-class is not DMC-03 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / DMI-02 — every relationship used lies within DMR-01…12 (uses 01/02/04/08/09)."""

    check_id = "meta-relationships-closed"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "All attribute relationships are within DMR-01…12 (V2)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (DMK-01 typed/named/identified, DMK-02 single value)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DAA-K1 (typed+named) and DAA-K2 (single value + single bearing) hold (V3)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # DAA-K1 typed
            and subject.name.strip()  # DAA-K1 named
            and subject.target_id  # DMK-01 identified
            and subject.value_digest  # DAA-K2 one value
            and subject.bearing_entity_ref.strip()  # DAA-K2 one bearing
        )
        if not ok:
            return self._failed("DAA-K1/K2 (DMK-01/02) not satisfied (V3)")
        return self._passed(constraints=["DAA-K1", "DAA-K2", "DMK-01", "DMK-02"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMK-03 / UDL-09 — the founding graph is acyclic."""

    check_id = "founding-acyclic"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The attribute's founding graph is acyclic (V4 / DMK-03 / UDL-09)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UDL-12 — the attribute holds a valid DOS-01…05 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Attribute holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UDL-02 / DMI-05 / VC-5 — EL-1 and the CERTIFIED Datum are reused by reference only."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + DMC-01 substrate referenced, redefined nowhere (UDL-02 / DMI-05)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/DMC-01 primitive was redefined (UDL-02 / DMI-05)")
        if not subject.substrate_refs:
            return self._failed("no EL-1 substrate reference recorded (UDL-02)")
        if subject.absorbs_value:
            return self._failed("the certified Datum model was absorbed, not referenced (DMX-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class StorageIndependenceCheck(ValidationCheck):
    """UDL-11 / DAA-K5 / C6 — no storage technology is selected; representation only."""

    check_id = "storage-independence"
    severity = Severity.BLOCKING
    description = "No storage engine/DB/format/vendor; no image reference (UDL-11)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if subject.storage_selected or subject.selects_technology or subject.image_reference:
            return self._failed("a storage technology was selected (UDL-11 / DAA-K5)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UDL-15 / DAA-09 / C7 — the attribute confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Attribute confers no authority and embeds no secret (UDL-15 / DAA-09)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("attribute confers authority (UDL-15 / DAA-09)")
        if subject.embeds_secret:
            return self._failed("attribute embeds a secret (UDL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§6 / AC-8 — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at DMC-03 and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: AttributeValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def attribute_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
    return (
        AttributeTypedCheck(),
        AttributeNamedCheck(),
        AttributeIdentifiedCheck(),
        AttributeValueFidelityCheck(),
        AttributeValuesDatumCheck(),
        AttributeSingleBearingCheck(),
        AttributeNullabilityDeclaredCheck(),
        AttributeClassifiedCheck(),
        AttributeRelationalByReferenceCheck(),
        AttributeDerivationProvenanceCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        StorageIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class AttributeValidation:
    """The bundled outcome of validating an Attribute (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_attribute(
    attribute: Attribute, trace: TraceabilityRecord, *, strict: bool = False
) -> AttributeValidation:
    """Validate ``attribute`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and
    the :class:`AcceptanceDecision`. With ``strict=True`` a rejected attribute raises
    via the EC-1 acceptance gate.
    """
    subject = AttributeValidationSubject.from_attribute(attribute, trace)
    engine = ValidationEngine(attribute_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return AttributeValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "ATTRIBUTE_BLUEPRINT_ID",
    "AttributeValidationSubject",
    "AttributeValidation",
    "attribute_checks",
    "validate_attribute",
]
