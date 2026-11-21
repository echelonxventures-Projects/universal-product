"""EC3-B10-U03 — Entity validation (meta-validity V1…V5 + UDL + DEA conformance).

This module proves a realized :class:`~data.entity.Entity` is **META-VALID**
(DATA-005 §8, V1…V5), **Data-law conformant** (DATA-001 §7, esp. **UDL-07 Entity
Boundedness**, UDL-03, UDL-04/05, UDL-02, UDL-09, UDL-11, UDL-15), and satisfies the
Entity contracts (DATA-006 §10, DEA-K1/K2/K3 + the boundary rules DEA-C1/C2) by
running a suite of deterministic, data-layer checks through the **CERTIFIED EC-1
Validation Engine** (:class:`engine.validation.executor.ValidationEngine`) and
enforcing the EC-1 acceptance gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`EntityValidationSubject`,
so an identical entity yields a byte-identical report, evidence, and acceptance
decision (VC-4). Every check is **blocking**. A subset of check ids
(``meta-class-single``, ``meta-relationships-closed``, ``foundation-reuse-integrity``,
``data-value-fidelity``, ``founding-acyclic``, ``provisional-state-disclosure``,
``traceability-rooted``) is **shared with the CERTIFIED DMC-01 surface**, so the
DMC-01 CCE ten-gate suite (:func:`data.certification.cce_gates`) is reused verbatim
by the Entity certification (UDL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.entity import Entity
from data.entity_meta import (
    ENTITY_META_CLASS,
    ENTITY_RELATIONSHIPS,
    EntityKind,
    EntityState,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id an Entity realizes (its meta-class) — used by the EC-1 report.
ENTITY_BLUEPRINT_ID = ENTITY_META_CLASS

_KIND_VALUES = frozenset(k.value for k in EntityKind)
_STATE_VALUES = frozenset(s.value for s in EntityState)
_META_RELATIONSHIPS = frozenset(ENTITY_RELATIONSHIPS)

#: The DOS states that require an entity to be schema-described first (DEA-K3).
_ACTIVE_OR_BEYOND = frozenset(
    s.value
    for s in (
        EntityState.ACTIVE,
        EntityState.DEPRECATED,
        EntityState.SUPERSEDED,
        EntityState.RETIRED,
    )
)


@dataclass(frozen=True, slots=True)
class EntityValidationSubject:
    """A normalized, immutable projection of an Entity that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the entity's meta-facts. Holds no runtime
    state and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    kind: str
    value_digest: str
    attribute_ids: tuple[str, ...]
    attribute_names: tuple[str, ...]
    attribute_type_tags: tuple[str, ...]
    attribute_bearing_refs: tuple[str, ...]
    expected_bearing_ref: str
    attribute_count: int
    bounded: bool
    absorbs_attributes: bool
    schema_ref: str
    schema_described: bool
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
    def from_entity(cls, entity: Entity, trace: TraceabilityRecord) -> EntityValidationSubject:
        """Project ``entity`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=entity.entity_id,
            blueprint_id=ENTITY_BLUEPRINT_ID,
            meta_class=entity.meta_class,
            name=entity.name,
            type_tag=entity.type_tag,
            kind=entity.kind.value,
            value_digest=entity.structure_digest,
            attribute_ids=entity.borne_attribute_ids(),
            attribute_names=tuple(r.name for r in entity.attribute_refs),
            attribute_type_tags=tuple(r.type_tag for r in entity.attribute_refs),
            attribute_bearing_refs=tuple(r.bearing_entity_ref for r in entity.attribute_refs),
            expected_bearing_ref=entity.bearing_ref,
            attribute_count=entity.attribute_count,
            bounded=entity.is_bounded(),
            absorbs_attributes=entity.absorbs_attributes(),
            schema_ref=entity.schema_ref,
            schema_described=entity.is_schema_described(),
            relationships=entity.meta_relationships(),
            lifecycle_state=entity.state.value,
            founding_acyclic=entity.is_founding_acyclic(),
            confers_authority=entity.confers_authority(),
            embeds_secret=entity.embeds_secret(),
            redefines_el1=entity.redefines_el1(),
            selects_technology=entity.selects_technology(),
            substrate_refs=tuple(entity.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            storage_selected=False,  # UDL-11 — no storage technology is ever selected
            image_reference="",  # an entity is representation, not a deployable image
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Data-layer validation checks (each maps to explicit V*/UDL*/DEA* obligations)
# ---------------------------------------------------------------------------


class EntityTypedCheck(ValidationCheck):
    """UDL-03 / DEA-01 / DEA-K1 — entity is classified by a non-empty ENG-004 type."""

    check_id = "entity-typed"
    severity = Severity.BLOCKING
    description = "Entity bears a non-empty ENG-004 type_tag (DEA-01 / UDL-03)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("entity is untyped (DEA-01 / UDL-03)")
        return self._passed(type_tag=subject.type_tag)


class EntityNamedCheck(ValidationCheck):
    """DEA-02 — entity has an explicit, decidable name."""

    check_id = "entity-named"
    severity = Severity.BLOCKING
    description = "Entity has an explicit, non-empty name (DEA-02)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if not subject.name.strip():
            return self._failed("entity is unnamed (DEA-02)")
        return self._passed(name=subject.name)


class EntityIdentifiedCheck(ValidationCheck):
    """UDL-04/05 / DEA-02 / DMK-01 / C1 — entity is identified (ENG-001) and object-borne."""

    check_id = "entity-identified"
    severity = Severity.BLOCKING
    description = "Entity bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-ENTITY-"):
            return self._failed("entity has no ENG-001 identity (UDL-04)", id=subject.target_id)
        return self._passed(entity_id=subject.target_id)


class EntityValueFidelityCheck(ValidationCheck):
    """UDL-06 (transitive) / C3 — the entity's representation is ENG-003 value-faithful."""

    check_id = "data-value-fidelity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Entity representation is content-addressed via ENG-003 encoding (UDL-06)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("entity representation is not value-faithful (UDL-06)", d=digest)
        return self._passed(value_digest=digest)


class EntityBearsAttributesCheck(ValidationCheck):
    """DMR-01 / DEA-04 / DMX-02 — entity bears CERTIFIED Attributes by reference (non-own)."""

    check_id = "entity-bears-attributes"
    severity = Severity.BLOCKING
    description = "Entity bears ≥1 CERTIFIED Attribute by reference; owns/absorbs none (DMR-01)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if subject.attribute_count < 1:
            return self._failed("entity bears no attributes (DEA-04 / UDL-07)")
        bad = [a for a in subject.attribute_ids if not a.startswith("UCOS-ATTR-")]
        if bad:
            return self._failed("a borne attribute is not a CERTIFIED Attribute (DMR-01)", bad=bad)
        if subject.absorbs_attributes:
            return self._failed("entity owns/absorbs attribute implementation (DEA-04 / DMX-02)")
        return self._passed(bears=list(subject.attribute_ids))


class EntityBoundednessCheck(ValidationCheck):
    """UDL-07 / DEA-03 / DEA-C1 — the attribute set is explicit, decidable, and bounded."""

    check_id = "entity-boundedness"
    severity = Severity.BLOCKING
    description = "Entity declares an explicit, decidable, non-overlapping attribute set (UDL-07)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if not subject.bounded:
            return self._failed("entity boundary is not decidable (UDL-07 / DEA-C1)")
        if len(set(subject.attribute_names)) != subject.attribute_count:
            return self._failed("entity attribute set has a duplicate member (DEA-C1)")
        return self._passed(attribute_count=subject.attribute_count)


class EntityBoundaryOwnershipCheck(ValidationCheck):
    """DEA-C2 / DOC-02 — each borne attribute is borne by exactly this entity."""

    check_id = "entity-boundary-ownership"
    severity = Severity.BLOCKING
    description = "Every borne attribute is bound to exactly this entity's boundary (DEA-C2)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        expected = subject.expected_bearing_ref
        mismatched = [r for r in subject.attribute_bearing_refs if r != expected]
        if mismatched:
            return self._failed("a borne attribute is bound to another entity (DEA-C2)")
        return self._passed(boundary=subject.expected_bearing_ref)


class EntityAttributesTypedCheck(ValidationCheck):
    """DEA-04 / DEA-K2 / UDL-08 — every borne attribute is typed (ENG-004)."""

    check_id = "entity-attributes-typed"
    severity = Severity.BLOCKING
    description = "Every borne attribute carries a non-empty ENG-004 type (DEA-04 / DEA-K2)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if any(not t.strip() for t in subject.attribute_type_tags):
            return self._failed("a borne attribute is untyped (DEA-04 / DEA-K2 / UDL-08)")
        return self._passed(typed=subject.attribute_count)


class EntityClassifiedCheck(ValidationCheck):
    """DMR-09 / DXH-02 — the entity is classified by exactly one Entity kind."""

    check_id = "entity-classified"
    severity = Severity.BLOCKING
    description = "Entity is classified by a single DXH-02 kind (DMR-09 classified-by)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("entity kind is outside DXH-02", kind=subject.kind)
        return self._passed(kind=subject.kind)


class EntitySchemaBeforeActiveCheck(ValidationCheck):
    """DEA-06 / DEA-K3 — an entity is schema-described (DMR-04) before it may be ACTIVE."""

    check_id = "entity-schema-before-active"
    severity = Severity.BLOCKING
    description = "An ACTIVE-or-beyond entity records a described-by schema reference (DEA-K3)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state in _ACTIVE_OR_BEYOND and not subject.schema_described:
            return self._failed("entity is ACTIVE without a described-by schema (DEA-06 / DEA-K3)")
        return self._passed(schema_described=subject.schema_described)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / DMI-01 — the entity instantiates exactly one meta-class (DMC-02)."""

    check_id = "meta-class-single"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Entity instantiates exactly the DMC-02 meta-class (V1)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if subject.meta_class != ENTITY_META_CLASS:
            return self._failed("meta-class is not DMC-02 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / DMI-02 — every relationship used lies within DMR-01…12 (uses 01/04/10)."""

    check_id = "meta-relationships-closed"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "All entity relationships are within DMR-01…12 (V2)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (DEA-K1 typed/identified, DEA-K2 typed attrs)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DEA-K1 (typed+identified) and DEA-K2 (typed borne attrs) hold (V3)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # DEA-K1 typed
            and subject.name.strip()  # DEA-02 named
            and subject.target_id  # DMK-01 identified
            and subject.attribute_count >= 1  # bears a bounded set
            and all(t.strip() for t in subject.attribute_type_tags)  # DEA-K2 typed attrs
        )
        if not ok:
            return self._failed("DEA-K1/K2 (DMK-01) not satisfied (V3)")
        return self._passed(constraints=["DEA-K1", "DEA-K2", "DMK-01"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMK-03 / UDL-09 / DEA-C3 — the founding graph is acyclic."""

    check_id = "founding-acyclic"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The entity's founding graph is acyclic (V4 / DMK-03 / UDL-09 / DEA-C3)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UDL-12 — the entity holds a valid DOS-01…05 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Entity holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UDL-02 / DMI-05 / VC-5 — EL-1 and the CERTIFIED Attribute are reused by reference only."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + DMC-03 substrate referenced, redefined nowhere (UDL-02 / DMI-05)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/DMC-03 primitive was redefined (UDL-02 / DMI-05)")
        if not subject.substrate_refs:
            return self._failed("no EL-1 substrate reference recorded (UDL-02)")
        if subject.absorbs_attributes:
            return self._failed("the certified Attribute model was owned, not referenced (DMX-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class StorageIndependenceCheck(ValidationCheck):
    """UDL-11 / DEA-K5 / C6 — no storage technology is selected; representation only."""

    check_id = "storage-independence"
    severity = Severity.BLOCKING
    description = "No storage engine/DB/format/vendor; no image reference (UDL-11)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if subject.storage_selected or subject.selects_technology or subject.image_reference:
            return self._failed("a storage technology was selected (UDL-11 / DEA-K5)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UDL-15 / DEA-09 / C7 — the entity confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Entity confers no authority and embeds no secret (UDL-15 / DEA-09)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("entity confers authority (UDL-15 / DEA-09)")
        if subject.embeds_secret:
            return self._failed("entity embeds a secret (UDL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§16 / AC-8 — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at DMC-02 and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: EntityValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def entity_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
    return (
        EntityTypedCheck(),
        EntityNamedCheck(),
        EntityIdentifiedCheck(),
        EntityValueFidelityCheck(),
        EntityBearsAttributesCheck(),
        EntityBoundednessCheck(),
        EntityBoundaryOwnershipCheck(),
        EntityAttributesTypedCheck(),
        EntityClassifiedCheck(),
        EntitySchemaBeforeActiveCheck(),
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
class EntityValidation:
    """The bundled outcome of validating an Entity (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_entity(
    entity: Entity, trace: TraceabilityRecord, *, strict: bool = False
) -> EntityValidation:
    """Validate ``entity`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and
    the :class:`AcceptanceDecision`. With ``strict=True`` a rejected entity raises
    via the EC-1 acceptance gate.
    """
    subject = EntityValidationSubject.from_entity(entity, trace)
    engine = ValidationEngine(entity_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return EntityValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "ENTITY_BLUEPRINT_ID",
    "EntityValidationSubject",
    "EntityValidation",
    "entity_checks",
    "validate_entity",
]
