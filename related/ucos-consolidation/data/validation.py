"""EC3-B10-U01 — Datum validation (meta-validity V1…V5 + UDL-01…15 conformance).

This module proves a realized :class:`~data.datum.Datum` is **META-VALID** (DATA-005
§8, V1…V5) and **Data-law conformant** (DATA-001 §7, UDL-01…15) by running a suite
of deterministic, data-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1
acceptance gate (:func:`engine.validation.gates.enforce_acceptance`). Validation
evidence is produced with the EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`DatumValidationSubject`
(the type-independent projection the EC-1 engine consumes), so an identical datum
yields a byte-identical report, evidence, and acceptance decision (VC-4). Every
check is **blocking**: the verdict is PASS iff the datum satisfies every meta-validity
and Data-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.datum import Datum
from data.meta import (
    DATUM_META_CLASS,
    META_RELATIONSHIPS,
    DatumKind,
    DatumState,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Datum realizes (its meta-class) — used by the EC-1 report.
DATUM_BLUEPRINT_ID = DATUM_META_CLASS

_KIND_VALUES = frozenset(k.value for k in DatumKind)
_STATE_VALUES = frozenset(s.value for s in DatumState)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class DatumValidationSubject:
    """A normalized, immutable projection of a Datum that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the datum's meta-facts. Holds no runtime
    state and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    value_digest: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    confers_authority: bool
    embeds_secret: bool
    redefines_el1: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    storage_selected: bool
    image_reference: str
    disclosure: dict[str, Any]

    @classmethod
    def from_datum(cls, datum: Datum, trace: TraceabilityRecord) -> DatumValidationSubject:
        """Project ``datum`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=datum.datum_id,
            blueprint_id=DATUM_BLUEPRINT_ID,
            meta_class=datum.meta_class,
            type_tag=datum.type_tag,
            kind=datum.kind.value,
            value_digest=datum.value_digest,
            relationships=datum.meta_relationships(),
            lifecycle_state=datum.state.value,
            founding_acyclic=datum.is_founding_acyclic(),
            confers_authority=datum.confers_authority(),
            embeds_secret=datum.embeds_secret(),
            redefines_el1=datum.redefines_el1(),
            substrate_refs=tuple(datum.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            storage_selected=False,  # UDL-11 — no storage technology is ever selected
            image_reference="",  # a datum is representation, not a deployable image
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Data-layer validation checks (each maps to explicit V*/UDL*/DMK* obligations)
# ---------------------------------------------------------------------------


class DatumTypedCheck(ValidationCheck):
    """UDL-03 / DMK-01 / C1 — the datum is classified by a non-empty ENG-004 type."""

    check_id = "data-typed"
    severity = Severity.BLOCKING
    description = "Datum bears a non-empty ENG-004 type_tag (UDL-03)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("datum is untyped (UDL-03)")
        return self._passed(type_tag=subject.type_tag)


class DatumIdentifiedCheck(ValidationCheck):
    """UDL-04/05 / DMK-01 / C1 — the datum is identified (ENG-001) and object-borne."""

    check_id = "data-identified-objectbound"
    severity = Severity.BLOCKING
    description = "Datum bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-DATUM-"):
            return self._failed("datum has no ENG-001 identity (UDL-04)", id=subject.target_id)
        if not subject.value_digest:
            return self._failed("datum is not object-borne (no value digest) (UDL-05)")
        return self._passed(datum_id=subject.target_id)


class DatumValueFidelityCheck(ValidationCheck):
    """UDL-06 / DMK-02 / C3 — value is ENG-003 value (no parallel value model)."""

    check_id = "data-value-fidelity"
    severity = Severity.BLOCKING
    description = "Value round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("value is not ENG-003 value-faithful (UDL-06)", digest=digest)
        return self._passed(value_digest=digest)


class DatumClassifiedCheck(ValidationCheck):
    """DMR-09 / DXH-01 — the datum is classified by exactly one Datum kind."""

    check_id = "data-classified"
    severity = Severity.BLOCKING
    description = "Datum is classified by a DXH-01 kind (DMR-09 classified-by)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("datum kind is outside DXH-01", kind=subject.kind)
        return self._passed(kind=subject.kind)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / DMI-01 — the datum instantiates exactly one meta-class (DMC-01)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Datum instantiates exactly the DMC-01 meta-class (V1)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if subject.meta_class != DATUM_META_CLASS:
            return self._failed("meta-class is not DMC-01 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / DMI-02 — every relationship used lies within DMR-01…12."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All datum relationships are within DMR-01…12 (V2)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (DMK-01 typed/identified/object, DMK-02 value)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DMK-01 (typed/identified/object) and DMK-02 (ENG-003 value) hold (V3)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("DMK-01/02 not satisfied (V3)")
        return self._passed(constraints=["DMK-01", "DMK-02"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMK-03 / UDL-09 — the founding graph is acyclic."""

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The datum's founding graph is acyclic (V4 / DMK-03)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UDL-12 — the datum holds a valid DOS-01…05 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Datum holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UDL-02 / DMI-05 / VC-5 — EL-1 is reused by reference and redefined nowhere."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1 substrate referenced (ENG-001…004), redefined nowhere (UDL-02)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1 primitive was redefined (UDL-02 / DMI-05)")
        if not subject.substrate_refs:
            return self._failed("no EL-1 substrate reference recorded (UDL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class StorageIndependenceCheck(ValidationCheck):
    """UDL-11 / C6 — no storage technology is selected; representation only."""

    check_id = "storage-independence"
    severity = Severity.BLOCKING
    description = "No storage engine/DB/format/vendor; no image reference (UDL-11)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if subject.storage_selected or subject.image_reference:
            return self._failed("a storage technology was selected (UDL-11)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UDL-15 / C7 — the datum confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Datum confers no authority and embeds no secret (UDL-15 / RR-07)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("datum confers authority (UDL-15)")
        if subject.embeds_secret:
            return self._failed("datum embeds a secret (UDL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§6 / AC-7 — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at DMC-01 and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: DatumValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def datum_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
    return (
        DatumTypedCheck(),
        DatumIdentifiedCheck(),
        DatumValueFidelityCheck(),
        DatumClassifiedCheck(),
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
class DatumValidation:
    """The bundled outcome of validating a Datum (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_datum(
    datum: Datum, trace: TraceabilityRecord, *, strict: bool = False
) -> DatumValidation:
    """Validate ``datum`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and
    the :class:`AcceptanceDecision`. With ``strict=True`` a rejected datum raises via
    the EC-1 acceptance gate.
    """
    subject = DatumValidationSubject.from_datum(datum, trace)
    engine = ValidationEngine(datum_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return DatumValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "DATUM_BLUEPRINT_ID",
    "DatumValidationSubject",
    "DatumValidation",
    "datum_checks",
    "validate_datum",
]
