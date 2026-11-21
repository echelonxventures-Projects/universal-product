"""EC3-B10-U05 — Storage validation (meta-validity V1…V5 + UDL + DTA conformance).

This module proves a realized :class:`~data.storage.Storage` is **META-VALID**
(DATA-005 §8, V1…V5), **Data-law conformant** (DATA-001 §7, esp. **UDL-11 Storage
Independence**, UDL-03, UDL-04/05, UDL-02, UDL-09, UDL-12, UDL-15), and satisfies the
Storage contracts (DATA-010 §10, DTA-K1/K3/K5 + the topology rules DTA-C1/C2/C3/C4) by
running a suite of deterministic, data-layer checks through the **CERTIFIED EC-1
Validation Engine** (:class:`engine.validation.executor.ValidationEngine`) and enforcing
the EC-1 acceptance gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`StorageValidationSubject`, so
an identical topology yields a byte-identical report, evidence, and acceptance decision
(VC-4). Every check is **blocking**. A subset of check ids (``meta-class-single``,
``meta-relationships-closed``, ``foundation-reuse-integrity``, ``data-value-fidelity``,
``founding-acyclic``, ``provisional-state-disclosure``, ``traceability-rooted``) is
**shared with the CERTIFIED DMC-01 surface**, so the DMC-01 CCE ten-gate suite
(:func:`data.certification.cce_gates`) is reused verbatim by the Storage certification
(UDL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.storage import Storage
from data.storage_meta import (
    STORAGE_META_CLASS,
    STORAGE_RELATIONSHIPS,
    DurabilityLevel,
    StorageKind,
    StorageState,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Storage realizes (its meta-class) — used by the EC-1 report.
STORAGE_BLUEPRINT_ID = STORAGE_META_CLASS

_KIND_VALUES = frozenset(k.value for k in StorageKind)
_DURABILITY_VALUES = frozenset(d.value for d in DurabilityLevel)
_STATE_VALUES = frozenset(s.value for s in StorageState)
_META_RELATIONSHIPS = frozenset(STORAGE_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class StorageValidationSubject:
    """A normalized, immutable projection of a Storage that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the topology's meta-facts. Holds no runtime
    state and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    kind: str
    value_digest: str
    loci: tuple[str, ...]
    locus_count: int
    placement_explicit: bool
    durability: str
    durability_declared: bool
    persisted_entity_ids: tuple[str, ...]
    schema_refs: tuple[str, ...]
    schema_aligned: bool
    topology_consistent: bool
    runtime_ref: str
    binds_runtime_by_reference: bool
    names_technology: bool
    absorbs_persisted: bool
    version: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    confers_authority: bool
    embeds_secret: bool
    redefines_el1: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    image_reference: str
    disclosure: dict[str, Any]

    @classmethod
    def from_storage(cls, storage: Storage, trace: TraceabilityRecord) -> StorageValidationSubject:
        """Project ``storage`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=storage.storage_id,
            blueprint_id=STORAGE_BLUEPRINT_ID,
            meta_class=storage.meta_class,
            name=storage.name,
            type_tag=storage.type_tag,
            kind=storage.kind.value,
            value_digest=storage.structure_digest,
            loci=storage.placement_loci(),
            locus_count=storage.locus_count,
            placement_explicit=storage.is_placement_explicit(),
            durability=storage.durability.value,
            durability_declared=storage.is_durability_declared(),
            persisted_entity_ids=storage.persisted_entity_ids(),
            schema_refs=storage.schema_refs(),
            schema_aligned=storage.is_schema_aligned(),
            topology_consistent=storage.is_topology_consistent(),
            runtime_ref=storage.runtime_ref,
            binds_runtime_by_reference=storage.binds_runtime_by_reference(),
            names_technology=storage.names_technology(),
            absorbs_persisted=storage.absorbs_persisted(),
            version=storage.version,
            relationships=storage.meta_relationships(),
            lifecycle_state=storage.state.value,
            founding_acyclic=storage.is_founding_acyclic(),
            confers_authority=storage.confers_authority(),
            embeds_secret=storage.embeds_secret(),
            redefines_el1=storage.redefines_el1(),
            substrate_refs=tuple(storage.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            image_reference="",  # a topology is a description, not a deployable image
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Data-layer validation checks (each maps to explicit V*/UDL*/DTA* obligations)
# ---------------------------------------------------------------------------


class StorageTypedCheck(ValidationCheck):
    """UDL-03 / DTA-01 / DTA-K1 — topology is classified by a non-empty ENG-004 type."""

    check_id = "storage-typed"
    severity = Severity.BLOCKING
    description = "Storage bears a non-empty ENG-004 type_tag (DTA-01 / DTA-K1 / UDL-03)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("storage is untyped (DTA-K1 / UDL-03)")
        return self._passed(type_tag=subject.type_tag)


class StorageNamedCheck(ValidationCheck):
    """DTA-03 — topology has an explicit, decidable name."""

    check_id = "storage-named"
    severity = Severity.BLOCKING
    description = "Storage has an explicit, non-empty name (DTA-03)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not subject.name.strip():
            return self._failed("storage is unnamed (DTA-03)")
        return self._passed(name=subject.name)


class StorageIdentifiedCheck(ValidationCheck):
    """UDL-04/05 / DTA-K1 / DMK-01 / C1 — topology is identified (ENG-001) and object-borne."""

    check_id = "storage-identified"
    severity = Severity.BLOCKING
    description = "Storage bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-STORAGE-"):
            return self._failed("storage has no ENG-001 identity (UDL-04)", id=subject.target_id)
        return self._passed(storage_id=subject.target_id)


class StorageValueFidelityCheck(ValidationCheck):
    """UDL-06 (transitive) / C3 — the topology's representation is ENG-003 value-faithful."""

    check_id = "data-value-fidelity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Storage representation is content-addressed via ENG-003 encoding (UDL-06)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("storage representation is not value-faithful (UDL-06)", d=digest)
        return self._passed(value_digest=digest)


class StoragePlacementExplicitCheck(ValidationCheck):
    """DTA-03 / DTA-C1 — the topology declares an explicit, decidable locus set."""

    check_id = "storage-placement-explicit"
    severity = Severity.BLOCKING
    description = "Storage declares an explicit, decidable, non-empty locus set (DTA-03 / DTA-C1)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if subject.locus_count < 1:
            return self._failed("storage declares no explicit placement (DTA-03 / DTA-C1)")
        if not subject.placement_explicit:
            return self._failed("storage placement is not decidable (DTA-C1)")
        if len(set(subject.loci)) != subject.locus_count:
            return self._failed("storage locus set has a duplicate member (DTA-C1)")
        return self._passed(locus_count=subject.locus_count)


class StorageDurabilityDeclaredCheck(ValidationCheck):
    """DTA-04 / DTA-C2 — durability is a declared, decidable property."""

    check_id = "storage-durability-declared"
    severity = Severity.BLOCKING
    description = "Storage declares a decidable durability level (DTA-04 / DTA-C2)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not subject.durability_declared or subject.durability not in _DURABILITY_VALUES:
            return self._failed("storage durability is not declared/decidable (DTA-04)")
        return self._passed(durability=subject.durability)


class StoragePersistsEntitiesCheck(ValidationCheck):
    """DMR-05 / DTA-09 / DMX-02 — topology persists CERTIFIED entities by reference (non-own)."""

    check_id = "storage-persists-entities"
    severity = Severity.BLOCKING
    description = "Storage persists ≥1 CERTIFIED entity by reference; owns/absorbs none (DMR-05)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not subject.persisted_entity_ids:
            return self._failed("storage persists no entity (DMR-05)")
        bad = [e for e in subject.persisted_entity_ids if not e.startswith("UCOS-ENTITY-")]
        if bad:
            return self._failed("a persisted subject is not a CERTIFIED Entity (DMR-05)", bad=bad)
        if subject.absorbs_persisted:
            return self._failed("storage owns/absorbs persisted data (DTA-09 / DMX-02)")
        return self._passed(persists=list(subject.persisted_entity_ids))


class StorageSchemaAlignedCheck(ValidationCheck):
    """DTA-07 / DTA-C4 / DTA-K3 — persisted data is schema-conformant (schema referenced)."""

    check_id = "storage-schema-aligned"
    severity = Severity.BLOCKING
    description = "Every persisted entity references a conformance schema (DTA-07 / DTA-K3)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not subject.schema_aligned:
            return self._failed("persisted data is not schema-aligned (DTA-07 / DTA-K3)")
        bad = [s for s in subject.schema_refs if not s.startswith("UCOS-SCHEMA-")]
        if bad:
            return self._failed("a schema reference is not a CERTIFIED Schema (DTA-07)", bad=bad)
        return self._passed(schemas=list(subject.schema_refs))


class StoragePersistenceByReferenceCheck(ValidationCheck):
    """DMR-11 / DTA-02 / DTA-K2 — persistence binds a RUNTIME state reference (not redefined)."""

    check_id = "storage-persistence-by-reference"
    severity = Severity.BLOCKING
    description = "Persistence binds a RUNTIME state reference; no engine redefined (DMR-11)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not subject.binds_runtime_by_reference:
            return self._failed("persistence does not bind a RUNTIME reference (DMR-11 / DTA-K2)")
        return self._passed(runtime_ref=subject.runtime_ref)


class StorageTopologyConsistentCheck(ValidationCheck):
    """DXH-06 / DTA-C3 — locus cardinality / durability consistent with the topology kind."""

    check_id = "storage-topology-consistent"
    severity = Severity.BLOCKING
    description = "Topology cardinality/durability is consistent with its DXH-06 kind (DTA-C3)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not subject.topology_consistent:
            return self._failed("topology cardinality/durability inconsistent with kind (DTA-C3)")
        return self._passed(kind=subject.kind, loci=subject.locus_count)


class StorageIndependenceCheck(ValidationCheck):
    """UDL-11 / DTA-01 / DTA-K5 / C6 — the topology names no storage technology (material)."""

    check_id = "storage-independence"
    severity = Severity.BLOCKING
    description = "No engine/DB/format/query language/broker/vendor named (UDL-11 / DTA-01)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.image_reference:
            return self._failed("a storage technology was named/selected (UDL-11 / DTA-K5)")
        return self._passed()


class StorageVersionedCheck(ValidationCheck):
    """DTA-08 / UDL-12 — the topology records an explicit version (additive/supersession)."""

    check_id = "storage-versioned"
    severity = Severity.BLOCKING
    description = "Storage records an explicit version (DTA-08 / UDL-12)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("storage records no version (DTA-08)")
        return self._passed(version=subject.version)


class StorageClassifiedCheck(ValidationCheck):
    """DMR-09 / DXH-06 — the topology is classified by exactly one Storage kind."""

    check_id = "storage-classified"
    severity = Severity.BLOCKING
    description = "Storage is classified by a single DXH-06 kind (DMR-09 classified-by)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("storage kind is outside DXH-06", kind=subject.kind)
        return self._passed(kind=subject.kind)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / DMI-01 — the topology instantiates exactly one meta-class (DMC-06)."""

    check_id = "meta-class-single"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Storage instantiates exactly the DMC-06 meta-class (V1)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if subject.meta_class != STORAGE_META_CLASS:
            return self._failed("meta-class is not DMC-06 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / DMI-02 — every relationship used lies within DMR-01…12 (uses 05/10/11)."""

    check_id = "meta-relationships-closed"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "All storage relationships are within DMR-01…12 (V2)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (DTA-K1 typed/identified, DTA-K3 schema-conformant)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DTA-K1 (typed+identified) and DTA-K3 (schema-conformant) hold (V3)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # DTA-K1 typed
            and subject.name.strip()  # DTA-03 named
            and subject.target_id  # DMK-01 identified
            and subject.locus_count >= 1  # explicit placement
            and subject.schema_aligned  # DTA-K3 schema-conformant
            and subject.founding_acyclic  # DMK-03 acyclic
        )
        if not ok:
            return self._failed("DTA-K1/K3 (DMK-01/03/04) not satisfied (V3)")
        return self._passed(constraints=["DTA-K1", "DTA-K3", "DMK-01", "DMK-03"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMK-03 / DTA-C3 — the founding/persistence graph is acyclic."""

    check_id = "founding-acyclic"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The topology's founding/persistence graph is acyclic (V4 / DMK-03)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UDL-12 — the topology holds a valid DOS-01…05 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Storage holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UDL-02 / DMI-05 / VC-5 — EL-1 + DMC-02/05 + RL-F2 reused by reference only."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + DMC-02/05 + RL-F2 substrate referenced, redefined nowhere (UDL-02)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/DMC-02/05/RL-F2 primitive was redefined (UDL-02)")
        if not subject.substrate_refs:
            return self._failed("no EL-1 substrate reference recorded (UDL-02)")
        if subject.absorbs_persisted:
            return self._failed("the certified data model was owned, not referenced (DMX-02)")
        if not subject.binds_runtime_by_reference:
            return self._failed("RUNTIME persistence was not bound by reference (UDL-02 / DTA-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class NonConstitutiveCheck(ValidationCheck):
    """UDL-15 / DTA-09 / C7 — the topology confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Storage confers no authority and embeds no secret (UDL-15 / DTA-09)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("storage confers authority (UDL-15 / DTA-09)")
        if subject.embeds_secret:
            return self._failed("storage embeds a secret (UDL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§16 / AC — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at DMC-06 and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: StorageValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def storage_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
    return (
        StorageTypedCheck(),
        StorageNamedCheck(),
        StorageIdentifiedCheck(),
        StorageValueFidelityCheck(),
        StoragePlacementExplicitCheck(),
        StorageDurabilityDeclaredCheck(),
        StoragePersistsEntitiesCheck(),
        StorageSchemaAlignedCheck(),
        StoragePersistenceByReferenceCheck(),
        StorageTopologyConsistentCheck(),
        StorageIndependenceCheck(),
        StorageVersionedCheck(),
        StorageClassifiedCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class StorageValidation:
    """The bundled outcome of validating a Storage (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_storage(
    storage: Storage, trace: TraceabilityRecord, *, strict: bool = False
) -> StorageValidation:
    """Validate ``storage`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected topology raises via the
    EC-1 acceptance gate.
    """
    subject = StorageValidationSubject.from_storage(storage, trace)
    engine = ValidationEngine(storage_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return StorageValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "STORAGE_BLUEPRINT_ID",
    "StorageValidationSubject",
    "StorageValidation",
    "storage_checks",
    "validate_storage",
]
