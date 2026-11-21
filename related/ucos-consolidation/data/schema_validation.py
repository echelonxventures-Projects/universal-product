"""EC3-B10-U04 — Schema validation (meta-validity V1…V5 + UDL + DSA conformance).

This module proves a realized :class:`~data.schema.Schema` is **META-VALID**
(DATA-005 §8, V1…V5), **Data-law conformant** (DATA-001 §7, esp. **UDL-10 Schema
Explicitness**, UDL-03, UDL-04/05, UDL-02, UDL-09, UDL-11, UDL-15), and satisfies the
Schema contracts (DATA-009 §10, DSA-K1/K3 + the conformance rules DSA-C1/C2/C3) by
running a suite of deterministic, data-layer checks through the **CERTIFIED EC-1
Validation Engine** (:class:`engine.validation.executor.ValidationEngine`) and
enforcing the EC-1 acceptance gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`SchemaValidationSubject`, so
an identical schema yields a byte-identical report, evidence, and acceptance decision
(VC-4). Every check is **blocking**. A subset of check ids (``meta-class-single``,
``meta-relationships-closed``, ``foundation-reuse-integrity``, ``data-value-fidelity``,
``founding-acyclic``, ``provisional-state-disclosure``, ``traceability-rooted``) is
**shared with the CERTIFIED DMC-01 surface**, so the DMC-01 CCE ten-gate suite
(:func:`data.certification.cce_gates`) is reused verbatim by the Schema certification
(UDL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.schema import Schema
from data.schema_meta import (
    SCHEMA_META_CLASS,
    SCHEMA_RELATIONSHIPS,
    SchemaKind,
    SchemaState,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Schema realizes (its meta-class) — used by the EC-1 report.
SCHEMA_BLUEPRINT_ID = SCHEMA_META_CLASS

_KIND_VALUES = frozenset(k.value for k in SchemaKind)
_STATE_VALUES = frozenset(s.value for s in SchemaState)
_META_RELATIONSHIPS = frozenset(SCHEMA_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class SchemaValidationSubject:
    """A normalized, immutable projection of a Schema that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the schema's meta-facts. Holds no runtime
    state and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    kind: str
    value_digest: str
    element_names: tuple[str, ...]
    element_type_tags: tuple[str, ...]
    element_count: int
    explicit: bool
    conformance_decidable: bool
    elements_typed: bool
    described_subject_ids: tuple[str, ...]
    member_schema_refs: tuple[str, ...]
    absorbs_described: bool
    version: str
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
    def from_schema(cls, schema: Schema, trace: TraceabilityRecord) -> SchemaValidationSubject:
        """Project ``schema`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=schema.schema_id,
            blueprint_id=SCHEMA_BLUEPRINT_ID,
            meta_class=schema.meta_class,
            name=schema.name,
            type_tag=schema.type_tag,
            kind=schema.kind.value,
            value_digest=schema.structure_digest,
            element_names=schema.element_names(),
            element_type_tags=schema.element_type_tags(),
            element_count=schema.element_count,
            explicit=schema.is_explicit(),
            conformance_decidable=schema.is_conformance_decidable(),
            elements_typed=schema.elements_typed(),
            described_subject_ids=schema.described_subject_ids(),
            member_schema_refs=schema.member_schema_refs,
            absorbs_described=schema.absorbs_described(),
            version=schema.version,
            relationships=schema.meta_relationships(),
            lifecycle_state=schema.state.value,
            founding_acyclic=schema.is_founding_acyclic(),
            confers_authority=schema.confers_authority(),
            embeds_secret=schema.embeds_secret(),
            redefines_el1=schema.redefines_el1(),
            selects_technology=schema.selects_technology(),
            substrate_refs=tuple(schema.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            storage_selected=False,  # UDL-11 — no storage technology is ever selected
            image_reference="",  # a schema is a description, not a deployable image
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Data-layer validation checks (each maps to explicit V*/UDL*/DSA* obligations)
# ---------------------------------------------------------------------------


class SchemaTypedCheck(ValidationCheck):
    """UDL-03 / DSA-03 / DSA-K1 — schema is classified by a non-empty ENG-004 type."""

    check_id = "schema-typed"
    severity = Severity.BLOCKING
    description = "Schema bears a non-empty ENG-004 type_tag (DSA-03 / DSA-K1 / UDL-03)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("schema is untyped (DSA-K1 / UDL-03)")
        return self._passed(type_tag=subject.type_tag)


class SchemaNamedCheck(ValidationCheck):
    """DSA-01 — schema has an explicit, decidable name."""

    check_id = "schema-named"
    severity = Severity.BLOCKING
    description = "Schema has an explicit, non-empty name (DSA-01)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if not subject.name.strip():
            return self._failed("schema is unnamed (DSA-01)")
        return self._passed(name=subject.name)


class SchemaIdentifiedCheck(ValidationCheck):
    """UDL-04/05 / DSA-K1 / DMK-01 / C1 — schema is identified (ENG-001) and object-borne."""

    check_id = "schema-identified"
    severity = Severity.BLOCKING
    description = "Schema bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-SCHEMA-"):
            return self._failed("schema has no ENG-001 identity (UDL-04)", id=subject.target_id)
        return self._passed(schema_id=subject.target_id)


class SchemaValueFidelityCheck(ValidationCheck):
    """UDL-06 (transitive) / C3 — the schema's representation is ENG-003 value-faithful."""

    check_id = "data-value-fidelity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Schema representation is content-addressed via ENG-003 encoding (UDL-06)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("schema representation is not value-faithful (UDL-06)", d=digest)
        return self._passed(value_digest=digest)


class SchemaExplicitStructureCheck(ValidationCheck):
    """UDL-10 / DSA-01 — the schema declares an explicit, decidable, non-empty element set."""

    check_id = "schema-explicit-structure"
    severity = Severity.BLOCKING
    description = "Schema declares an explicit, decidable, non-empty element set (UDL-10 / DSA-01)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if subject.element_count < 1:
            return self._failed("schema declares no explicit structure (UDL-10 / DSA-01)")
        if not subject.explicit:
            return self._failed("schema structure is not decidable (UDL-10 / DSA-02)")
        if len(set(subject.element_names)) != subject.element_count:
            return self._failed("schema element set has a duplicate member (DSA-02 / DSA-C2)")
        return self._passed(element_count=subject.element_count)


class SchemaElementsTypedCheck(ValidationCheck):
    """DSA-03 / DSA-C3 — every schema element references a non-empty ENG-004 type."""

    check_id = "schema-elements-typed"
    severity = Severity.BLOCKING
    description = "Every schema element references a non-empty ENG-004 type (DSA-03 / DSA-C3)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if not subject.elements_typed or any(not t.strip() for t in subject.element_type_tags):
            return self._failed("a schema element is untyped (DSA-03 / DSA-C3)")
        return self._passed(typed=subject.element_count)


class SchemaConformanceDecidableCheck(ValidationCheck):
    """DSA-02 / DSA-C2 — conformance of a data set to the schema is decidable."""

    check_id = "schema-conformance-decidable"
    severity = Severity.BLOCKING
    description = "Conformance to the schema is decidable (explicit structure + subject) (DSA-02)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if not subject.conformance_decidable:
            return self._failed("schema conformance is not decidable (DSA-02 / DSA-C2)")
        return self._passed()


class SchemaDescribesSubjectCheck(ValidationCheck):
    """DMR-04 / DOR-04 / DSA-09 — schema describes ≥1 CERTIFIED subject by reference (non-own)."""

    check_id = "schema-describes-subject"
    severity = Severity.BLOCKING
    description = "Schema describes ≥1 CERTIFIED subject by reference or composes members (DMR-04)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if not subject.described_subject_ids and not subject.member_schema_refs:
            return self._failed("schema describes no subject and composes no member (DMR-04)")
        bad = [s for s in subject.described_subject_ids if not s.startswith("UCOS-")]
        if bad:
            return self._failed("a described subject is not CERTIFIED (DMR-04)", bad=bad)
        if subject.absorbs_described:
            return self._failed("schema owns/absorbs a described model (DSA-09 / DMX-02)")
        return self._passed(describes=list(subject.described_subject_ids))


class SchemaCompositionAcyclicCheck(ValidationCheck):
    """DSA-05 / DSA-C1 / DSA-K3 — aggregate composition (and describes) is acyclic."""

    check_id = "schema-composition-acyclic"
    severity = Severity.BLOCKING
    description = "Aggregate/describes composition is acyclic; no self-composition (DSA-C1)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("schema composition is not acyclic (DSA-C1 / DMK-03)")
        if subject.target_id in subject.member_schema_refs:
            return self._failed("schema composes itself (DSA-C1)")
        return self._passed()


class SchemaVersionedCheck(ValidationCheck):
    """DSA-06 — the schema records an explicit version (versioned evolution)."""

    check_id = "schema-versioned"
    severity = Severity.BLOCKING
    description = "Schema records an explicit version (DSA-06 versioned evolution)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("schema records no version (DSA-06)")
        return self._passed(version=subject.version)


class SchemaClassifiedCheck(ValidationCheck):
    """DMR-09 / DXH-05 — the schema is classified by exactly one Schema kind."""

    check_id = "schema-classified"
    severity = Severity.BLOCKING
    description = "Schema is classified by a single DXH-05 kind (DMR-09 classified-by)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("schema kind is outside DXH-05", kind=subject.kind)
        return self._passed(kind=subject.kind)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / DMI-01 — the schema instantiates exactly one meta-class (DMC-05)."""

    check_id = "meta-class-single"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Schema instantiates exactly the DMC-05 meta-class (V1)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if subject.meta_class != SCHEMA_META_CLASS:
            return self._failed("meta-class is not DMC-05 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / DMI-02 — every relationship used lies within DMR-01…12 (uses 04/10)."""

    check_id = "meta-relationships-closed"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "All schema relationships are within DMR-01…12 (V2)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (DSA-K1 typed/identified, DSA-K3 acyclic)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DSA-K1 (typed+identified) and DSA-K3 (acyclic composition) hold (V3)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # DSA-K1 typed
            and subject.name.strip()  # DSA-01 named
            and subject.target_id  # DMK-01 identified
            and subject.element_count >= 1  # explicit structure
            and subject.founding_acyclic  # DSA-K3 acyclic
        )
        if not ok:
            return self._failed("DSA-K1/K3 (DMK-01/03) not satisfied (V3)")
        return self._passed(constraints=["DSA-K1", "DSA-K3", "DMK-01", "DMK-03"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMK-03 / DSA-C1 — the founding/composition graph is acyclic."""

    check_id = "founding-acyclic"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The schema's founding/composition graph is acyclic (V4 / DMK-03 / DSA-C1)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UDL-12 — the schema holds a valid DOS-01…05 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Schema holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UDL-02 / DMI-05 / VC-5 — EL-1 and the CERTIFIED Entity are reused by reference only."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + DMC-02 substrate referenced, redefined nowhere (UDL-02 / DMI-05)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/DMC-02 primitive was redefined (UDL-02 / DMI-05)")
        if not subject.substrate_refs:
            return self._failed("no EL-1 substrate reference recorded (UDL-02)")
        if subject.absorbs_described:
            return self._failed("the certified Entity model was owned, not referenced (DMX-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class StorageIndependenceCheck(ValidationCheck):
    """UDL-11 / DSA-07 / DSA-K5 / C6 — no storage technology is selected; description only."""

    check_id = "storage-independence"
    severity = Severity.BLOCKING
    description = "No storage engine/DB/format/query lang; no image reference (UDL-11 / DSA-07)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if subject.storage_selected or subject.selects_technology or subject.image_reference:
            return self._failed("a storage technology was selected (UDL-11 / DSA-07 / DSA-K5)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UDL-15 / DSA-09 / C7 — the schema confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Schema confers no authority and embeds no secret (UDL-15 / DSA-09)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("schema confers authority (UDL-15 / DSA-09)")
        if subject.embeds_secret:
            return self._failed("schema embeds a secret (UDL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§16 / AC — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at DMC-05 and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: SchemaValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def schema_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
    return (
        SchemaTypedCheck(),
        SchemaNamedCheck(),
        SchemaIdentifiedCheck(),
        SchemaValueFidelityCheck(),
        SchemaExplicitStructureCheck(),
        SchemaElementsTypedCheck(),
        SchemaConformanceDecidableCheck(),
        SchemaDescribesSubjectCheck(),
        SchemaCompositionAcyclicCheck(),
        SchemaVersionedCheck(),
        SchemaClassifiedCheck(),
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
class SchemaValidation:
    """The bundled outcome of validating a Schema (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_schema(
    schema: Schema, trace: TraceabilityRecord, *, strict: bool = False
) -> SchemaValidation:
    """Validate ``schema`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and
    the :class:`AcceptanceDecision`. With ``strict=True`` a rejected schema raises via
    the EC-1 acceptance gate.
    """
    subject = SchemaValidationSubject.from_schema(schema, trace)
    engine = ValidationEngine(schema_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return SchemaValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "SCHEMA_BLUEPRINT_ID",
    "SchemaValidationSubject",
    "SchemaValidation",
    "schema_checks",
    "validate_schema",
]
