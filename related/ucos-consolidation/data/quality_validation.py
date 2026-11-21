"""EC3-B10-U08 — Quality validation (meta-validity V1…V5 + UDL + DQA conformance).

This module proves a realized :class:`~data.quality.QualityObject` is **META-VALID**
(DATA-005 §8, V1…V5), **Data-law conformant** (DATA-001 §7, esp. **UDL-14 Quality as an
Evaluative Facet**, UDL-03, UDL-04/05, UDL-02, UDL-09, UDL-15), and satisfies the Quality
contracts (DATA-013 §10, DQA-K1…K5 + the measurement rules DQA-C1…C5) by running a suite
of deterministic, data-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`QualityValidationSubject`, so an
identical quality object yields a byte-identical report, evidence, and acceptance decision
(VC-4). Every check is **blocking**. A subset of check ids (``meta-class-single``,
``meta-relationships-closed``, ``foundation-reuse-integrity``, ``data-value-fidelity``,
``founding-acyclic``, ``provisional-state-disclosure``, ``traceability-rooted``) is
**shared with the CERTIFIED DMC-01 surface**, so the DMC-01 CCE ten-gate suite
(:func:`data.certification.cce_gates`) is reused verbatim by the Quality certification
(UDL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.quality import QualityObject
from data.quality_meta import (
    QUALITY_META_CLASS,
    QUALITY_RELATIONSHIPS,
    QualityState,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Quality object realizes (its meta-class) — used by the EC-1 report.
QUALITY_BLUEPRINT_ID = QUALITY_META_CLASS

_STATE_VALUES = frozenset(s.value for s in QualityState)
_META_RELATIONSHIPS = frozenset(QUALITY_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class QualityValidationSubject:
    """A normalized, immutable projection of a Quality object that checks evaluate.

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
    measured_construct_id: str
    absorbs_measured: bool
    kind: str
    classified: bool
    policy_ref: str
    binds_policy_by_reference: bool
    measured_dimensions: tuple[str, ...]
    records_measurement: bool
    dimensioned: bool
    gap_report: tuple[str, ...]
    verdict: str
    schema_ref: str
    schema_relative: bool
    evaluative: bool
    remediates: bool
    enforces: bool
    grants_access: bool
    recorded: bool
    names_technology: bool
    selects_technology: bool
    version: str
    relationships: tuple[str, ...]
    quality_state: str
    founding_acyclic: bool
    confers_authority: bool
    embeds_secret: bool
    redefines_el1: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    image_reference: str
    disclosure: dict[str, Any]

    @classmethod
    def from_quality(
        cls, quality: QualityObject, trace: TraceabilityRecord
    ) -> QualityValidationSubject:
        """Project ``quality`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=quality.quality_id,
            blueprint_id=QUALITY_BLUEPRINT_ID,
            meta_class=quality.meta_class,
            name=quality.name,
            type_tag=quality.type_tag,
            value_digest=quality.structure_digest,
            measured_construct_id=quality.measured_construct_id(),
            absorbs_measured=quality.absorbs_measured(),
            kind=quality.kind.value,
            classified=quality.is_classified(),
            policy_ref=quality.policy_ref,
            binds_policy_by_reference=quality.binds_policy_by_reference(),
            measured_dimensions=quality.measured_dimensions(),
            records_measurement=quality.records_measurement(),
            dimensioned=quality.is_dimensioned(),
            gap_report=quality.gap_report(),
            verdict=quality.verdict.value,
            schema_ref=quality.schema_ref,
            schema_relative=quality.is_schema_relative(),
            evaluative=quality.is_evaluative(),
            remediates=quality.remediates(),
            enforces=quality.enforces(),
            grants_access=quality.grants_access(),
            recorded=quality.is_recorded(),
            names_technology=quality.names_technology(),
            selects_technology=quality.selects_technology(),
            version=quality.version,
            relationships=quality.meta_relationships(),
            quality_state=quality.state.value,
            founding_acyclic=quality.is_founding_acyclic(),
            confers_authority=quality.confers_authority(),
            embeds_secret=quality.embeds_secret(),
            redefines_el1=quality.redefines_el1(),
            substrate_refs=tuple(quality.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            image_reference="",  # quality is a record, not a deployable image
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Data-layer validation checks (each maps to explicit V*/UDL*/DQA* obligations)
# ---------------------------------------------------------------------------


class QualityTypedCheck(ValidationCheck):
    """UDL-03 / DQA-K1 — quality object is classified by a non-empty ENG-004 type."""

    check_id = "quality-typed"
    severity = Severity.BLOCKING
    description = "Quality object bears a non-empty ENG-004 type_tag (DQA-K1 / UDL-03)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("quality object is untyped (DQA-K1 / UDL-03)")
        return self._passed(type_tag=subject.type_tag)


class QualityNamedCheck(ValidationCheck):
    """DQA-K1 — quality object has an explicit, decidable name."""

    check_id = "quality-named"
    severity = Severity.BLOCKING
    description = "Quality object has an explicit, non-empty name."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.name.strip():
            return self._failed("quality object is unnamed")
        return self._passed(name=subject.name)


class QualityIdentifiedCheck(ValidationCheck):
    """UDL-04/05 / DQA-K1 / DMK-01 / C1 — object is identified (ENG-001), object-borne."""

    check_id = "quality-identified"
    severity = Severity.BLOCKING
    description = "Quality object bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-QUALITY-"):
            return self._failed(
                "quality object has no ENG-001 identity (UDL-04)", id=subject.target_id
            )
        return self._passed(quality_id=subject.target_id)


class QualityValueFidelityCheck(ValidationCheck):
    """UDL-06 (transitive) / C3 — the object's representation is ENG-003 value-faithful."""

    check_id = "data-value-fidelity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Quality representation is content-addressed via ENG-003 encoding (UDL-06)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("quality representation is not value-faithful (UDL-06)", d=digest)
        return self._passed(value_digest=digest)


class QualityMeasuresSubjectCheck(ValidationCheck):
    """DMR-08 / DOR-08 / DQA-C3 — object measures a CERTIFIED construct by reference."""

    check_id = "quality-measures-subject"
    severity = Severity.BLOCKING
    description = "Quality measures a CERTIFIED construct by reference; owns none (DMR-08)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        cid = subject.measured_construct_id
        if not cid.startswith("UCOS-"):
            return self._failed("measured subject is not a CERTIFIED construct (DMR-08)", cid=cid)
        if subject.absorbs_measured:
            return self._failed("quality owns/absorbs its subject (DQA-C3 / DMX-02)")
        return self._passed(measures=cid)


class QualityEvaluativeCheck(ValidationCheck):
    """DQA-01 / DQA-K2 — quality is a decidable, evaluative measurement."""

    check_id = "quality-evaluative"
    severity = Severity.BLOCKING
    description = "Quality is a decidable, evaluative measurement (DQA-01 / DQA-K2)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.evaluative:
            return self._failed("quality is not evaluative (DQA-01 / DQA-K2)")
        return self._passed()


class QualityDimensionedCheck(ValidationCheck):
    """DQA-02 — quality is measured along a decidable dimension (single-facet, DXC-02)."""

    check_id = "quality-dimensioned"
    severity = Severity.BLOCKING
    description = "Quality is measured along a decidable dimension (DQA-02 / DXC-02)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.dimensioned or not subject.measured_dimensions:
            return self._failed(
                "quality is not dimensioned (DQA-02)", dims=list(subject.measured_dimensions)
            )
        return self._passed(dimensions=list(subject.measured_dimensions))


class QualityNonRemediatingCheck(ValidationCheck):
    """DQA-03 / DQA-K2 / UDL-14 — quality measures and records; it remediates/enforces nothing."""

    check_id = "quality-non-remediating"
    severity = Severity.BLOCKING
    description = "Quality measures/records and remediates/enforces nothing (DQA-03 / UDL-14)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if subject.remediates:
            return self._failed("quality remediates (DQA-03 / DQA-K2 — quality enacts nothing)")
        if subject.enforces:
            return self._failed("quality enforces (DQA-03 / UDL-14 — quality enacts nothing)")
        return self._passed()


class QualityRecordedCheck(ValidationCheck):
    """DQA-04 / DQA-K4 / DOV-08 — the measurement is recorded against an ENG-002 object."""

    check_id = "quality-recorded"
    severity = Severity.BLOCKING
    description = "The quality measurement is recorded on an ENG-002 object (DQA-04 / DOV-08)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.recorded:
            return self._failed("quality measurement is not recorded (DQA-04 / DQA-K4)")
        return self._passed()


class QualityBindsPolicyByReferenceCheck(ValidationCheck):
    """DMR-11 / DQA-06 / DQA-K3 — measurement binds a RUNTIME policy reference (not redefined)."""

    check_id = "quality-binds-policy-by-reference"
    severity = Severity.BLOCKING
    description = "Measurement binds a RUNTIME policy reference; no engine redefined (DMR-11)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.policy_ref.startswith("UCOS-POLICY-REF:"):
            return self._failed(
                "measurement does not bind a RUNTIME policy reference (DMR-11 / DQA-K3)"
            )
        if not subject.binds_policy_by_reference:
            return self._failed("quality measurement is not bound by reference (DMR-11 / DQA-06)")
        return self._passed(policy_ref=subject.policy_ref)


class QualityMeasurementRecordedCheck(ValidationCheck):
    """DQA-C1 — the object decidably records ≥1 per-dimension measurement verdict."""

    check_id = "quality-measurement-recorded"
    severity = Severity.BLOCKING
    description = "A quality object records ≥1 decidable per-dimension measurement (DQA-C1)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.records_measurement:
            return self._failed("a quality object records no measurement (DQA-C1)")
        return self._passed(dimensions=list(subject.measured_dimensions), verdict=subject.verdict)


class QualitySchemaRelativeCheck(ValidationCheck):
    """DQA-05 / DQA-C2 — completeness/consistency are measured relative to a declared schema."""

    check_id = "quality-schema-relative"
    severity = Severity.BLOCKING
    description = "Completeness/consistency measures bind a declared-schema reference (DQA-05)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.schema_relative:
            return self._failed(
                "a completeness/consistency measure is not schema-relative (DQA-05 / DQA-C2)",
                kind=subject.kind,
            )
        return self._passed(schema_ref=subject.schema_ref)


class QualityIndependenceCheck(ValidationCheck):
    """UDL-14 / DQA-07 / DQA-K5 / C6 — the object names no profiling/benchmark tech (material)."""

    check_id = "quality-independence"
    severity = Severity.BLOCKING
    description = "No profiling/DQ/benchmark technology or vendor named (UDL-14 / DQA-K5)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.selects_technology or subject.image_reference:
            return self._failed("a profiling/DQ/benchmark technology was named (UDL-14 / DQA-K5)")
        return self._passed()


class QualityVersionedCheck(ValidationCheck):
    """DQA-08 / UDL-12 — the object records an explicit version (additive/append-only)."""

    check_id = "quality-versioned"
    severity = Severity.BLOCKING
    description = "Quality object records an explicit version (DQA-08 / UDL-12)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("quality object records no version (DQA-08)")
        return self._passed(version=subject.version)


class QualityClassifiedCheck(ValidationCheck):
    """DXH-09 — the object is classified by exactly one quality kind."""

    check_id = "quality-classified"
    severity = Severity.BLOCKING
    description = "Quality object is classified by a single DXH-09 kind."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.classified or not subject.kind:
            return self._failed("quality object has no DXH-09 kind", kind=subject.kind)
        return self._passed(kind=subject.kind)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / DMI-01 — the object instantiates exactly one meta-class (DMC-09)."""

    check_id = "meta-class-single"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Quality object instantiates exactly the DMC-09 meta-class (V1)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if subject.meta_class != QUALITY_META_CLASS:
            return self._failed("meta-class is not DMC-09 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / DMI-02 — every relationship used lies within DMR-01…12 (uses 08/10/11)."""

    check_id = "meta-relationships-closed"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "All quality relationships are within DMR-01…12 (V2)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (DQA-K1 typed/identified, K2 evaluative/non-enforcing)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DQA-K1 (typed+identified), K2 (evaluative/non-remediating), K5 (no-auth) — V3."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # DQA-K1 typed
            and subject.name.strip()  # named
            and subject.target_id  # DMK-01 identified
            and subject.evaluative  # DQA-K2 evaluative
            and not subject.remediates  # DQA-K2 non-remediating
            and not subject.enforces  # DQA-K2 non-enforcing
            and subject.binds_policy_by_reference  # DQA-K3 measurement by reference
            and subject.recorded  # DQA-K4 recorded
            and not subject.confers_authority  # DQA-K5 no authority
            and subject.founding_acyclic  # DMK-03 acyclic
        )
        if not ok:
            return self._failed("DQA-K1/K2/K3/K4/K5 (DMK-01/03/07/08) not satisfied (V3)")
        return self._passed(constraints=["DQA-K1", "DQA-K2", "DQA-K3", "DQA-K4", "DQA-K5"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMK-03 — the founding/measurement graph is acyclic."""

    check_id = "founding-acyclic"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The quality object's founding graph is acyclic (V4 / DMK-03)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding/measurement graph is not acyclic (V4)")
        return self._passed()


class QualityValidStateCheck(ValidationCheck):
    """V5 / UDL-12 — the object holds a valid DOS-01…05 lifecycle state."""

    check_id = "quality-valid"
    severity = Severity.BLOCKING
    description = "Quality object holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if subject.quality_state not in _STATE_VALUES:
            return self._failed("invalid quality state (V5)", state=subject.quality_state)
        return self._passed(state=subject.quality_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UDL-02 / DMI-05 / VC-5 — EL-1 + DMC-02 + RL-F2 reused by reference only."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + DMC-02 + RL-F2 substrate referenced, redefined nowhere (UDL-02)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/DMC-02/RL-F2 primitive was redefined (UDL-02)")
        if not subject.substrate_refs:
            return self._failed("no EL-1 substrate reference recorded (UDL-02)")
        if subject.absorbs_measured:
            return self._failed("the certified data model was owned, not referenced (DMX-02)")
        if not subject.binds_policy_by_reference:
            return self._failed("RUNTIME policy was not bound by reference (UDL-02 / DQA-06)")
        return self._passed(substrate=list(subject.substrate_refs))


class NonConstitutiveCheck(ValidationCheck):
    """UDL-15 / DQA-09 / C7 — the object confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Quality confers no authority and embeds no secret (UDL-15 / DQA-09)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("quality confers authority (UDL-15 / DQA-09)")
        if subject.grants_access:
            return self._failed("quality grants access (UDL-15 / DQA-09)")
        if subject.embeds_secret:
            return self._failed("quality embeds a secret (UDL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§16 / AC — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at DMC-09 and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: QualityValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def quality_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
    return (
        QualityTypedCheck(),
        QualityNamedCheck(),
        QualityIdentifiedCheck(),
        QualityValueFidelityCheck(),
        QualityMeasuresSubjectCheck(),
        QualityEvaluativeCheck(),
        QualityDimensionedCheck(),
        QualityNonRemediatingCheck(),
        QualityRecordedCheck(),
        QualityBindsPolicyByReferenceCheck(),
        QualityMeasurementRecordedCheck(),
        QualitySchemaRelativeCheck(),
        QualityIndependenceCheck(),
        QualityVersionedCheck(),
        QualityClassifiedCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        QualityValidStateCheck(),
        FoundationReuseIntegrityCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class QualityValidation:
    """The bundled outcome of validating a Quality object (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_quality(
    quality: QualityObject, trace: TraceabilityRecord, *, strict: bool = False
) -> QualityValidation:
    """Validate ``quality`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected object raises via the
    EC-1 acceptance gate.
    """
    subject = QualityValidationSubject.from_quality(quality, trace)
    engine = ValidationEngine(quality_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return QualityValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "QUALITY_BLUEPRINT_ID",
    "QualityValidationSubject",
    "QualityValidation",
    "quality_checks",
    "validate_quality",
]
