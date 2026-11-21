"""EC3-B11-U12 — Band-11 completion validation (readiness BRC + completion BCC evidence).

Proves a realized :class:`~service.band11.Band11Completion` record satisfies the Band-11
readiness criteria (BRC-1…BRC-8) and completion criteria (BCC-1…BCC-8) **applied to the
EC-3 Service (Band-11) code realization**, by running deterministic, service-layer checks
through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate.

The suite deliberately emits the **shared check ids** the CERTIFIED SMC-01 CCE ten-gate
suite (:func:`service.service_certification.cce_gates`) requires — ``traceability-rooted``,
``meta-class-single``, ``foundation-reuse-integrity``, ``service-value-fidelity``,
``founding-acyclic``, ``meta-relationships-closed``, ``provisional-state-disclosure`` — with
**band-level semantics**, so the CCE gates are reused verbatim (USL-02 reuse-by-reference),
plus band-specific checks (``band11-*``) for the inventory/certification/integration facts.

Every check is **blocking** and is a pure predicate over an immutable
:class:`Band11ValidationSubject`, so an identical completion record yields a byte-identical
report, evidence, and acceptance decision (BRC-8 determinism).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- EC-1 reuse by reference (USL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance
from service.band11 import Band11Completion
from service.band11_meta import BAND_BLUEPRINT_ID, BAND_CLASS, EXPECTED_UNIT_COUNT, BandState
from service.service_traceability import TraceabilityRecord

_STATE_VALUES = frozenset(s.value for s in BandState)


@dataclass(frozen=True, slots=True)
class Band11ValidationSubject:
    """A normalized, immutable projection of a Band11Completion that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    value_digest: str
    unit_count: int
    inventory_complete: bool
    all_units_certified: bool
    meta_class_coverage_complete: bool
    dependency_acyclic: bool
    integration_closed: bool
    reuses_by_reference: bool
    non_projection: bool
    confers_authority: bool
    embeds_secret: bool
    names_technology: bool
    selects_technology: bool
    non_constitutive: bool
    version: str
    band_state: str
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_completion(
        cls, completion: Band11Completion, trace: TraceabilityRecord
    ) -> Band11ValidationSubject:
        """Project ``completion`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=completion.band_id,
            blueprint_id=BAND_BLUEPRINT_ID,
            meta_class=completion.meta_class,
            name=completion.name,
            type_tag=completion.type_tag,
            value_digest=completion.structure_digest,
            unit_count=len(completion.units),
            inventory_complete=completion.inventory_complete(),
            all_units_certified=completion.all_units_certified(),
            meta_class_coverage_complete=completion.meta_class_coverage_complete(),
            dependency_acyclic=completion.dependency_acyclic(),
            integration_closed=completion.integration_closed(),
            reuses_by_reference=completion.reuses_by_reference(),
            non_projection=completion.is_non_projection(),
            confers_authority=completion.confers_authority(),
            embeds_secret=completion.embeds_secret(),
            names_technology=completion.names_technology(),
            selects_technology=completion.selects_technology(),
            non_constitutive=completion.is_non_constitutive(),
            version=completion.version,
            band_state=completion.state.value,
            substrate_refs=tuple(completion.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Band-completion validation checks (each maps to explicit BRC*/BCC* obligations)
# ---------------------------------------------------------------------------


class BandTypedCheck(ValidationCheck):
    """C1 / SMK-01 — the completion record bears a non-empty ENG-004 type."""

    check_id = "band11-typed"
    severity = Severity.BLOCKING
    description = "Band-11 completion record bears a non-empty ENG-004 type_tag (SMK-01)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("band-11 completion record is untyped (SMK-01)")
        return self._passed(type_tag=subject.type_tag)


class BandIdentifiedCheck(ValidationCheck):
    """C1 / SMK-01 — the record is identified (ENG-001) and object-borne."""

    check_id = "band11-identified"
    severity = Severity.BLOCKING
    description = "Band-11 completion record bears a deterministic ENG-001 identity."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-BAND11-"):
            return self._failed("band-11 record has no ENG-001 identity", id=subject.target_id)
        return self._passed(band_id=subject.target_id)


class BandValueFidelityCheck(ValidationCheck):
    """BRC-8 / C3 — the record's representation is ENG-003 value-faithful (content-addressed)."""

    check_id = "service-value-fidelity"  # shared id — reused by the SMC-01 CCE gate suite (CC-3)
    severity = Severity.BLOCKING
    description = "Band-11 completion record is content-addressed via ENG-003 encoding."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("band-11 record representation is not value-faithful")
        return self._passed(value_digest=digest)


class BandInventoryCompleteCheck(ValidationCheck):
    """BRC-1 / BCC-1 — the record inventories exactly the eleven units U01…U11."""

    check_id = "band11-inventory-complete"
    severity = Severity.BLOCKING
    description = "Band-11 completion inventories exactly the eleven units U01…U11 (BRC-1)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.inventory_complete or subject.unit_count != EXPECTED_UNIT_COUNT:
            return self._failed(
                "band-11 inventory is not exactly the eleven units (BRC-1)",
                unit_count=subject.unit_count,
            )
        return self._passed(unit_count=subject.unit_count)


class BandAllUnitsCertifiedCheck(ValidationCheck):
    """BRC-2 / BCC-1 — every inventoried unit U01…U11 is CCE-CERTIFIED (by reference)."""

    check_id = "band11-all-units-certified"
    severity = Severity.BLOCKING
    description = "Every Band-11 unit U01…U11 is CCE-CERTIFIED (reused by reference) (BRC-2)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.all_units_certified:
            return self._failed("a Band-11 unit is not CERTIFIED (BRC-2)")
        return self._passed(units_certified=subject.unit_count)


class BandMetaClassCoverageCheck(ValidationCheck):
    """BRC-3 / BCC-2 / SMI-01 — the concern units cover exactly SMC-01…10 (closure)."""

    check_id = "meta-class-single"  # shared id — reused by the SMC-01 CCE gate suite (CC-1)
    severity = Severity.BLOCKING
    description = "Band-11 concern units cover exactly the ten meta-classes SMC-01…10 (SMI-01)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.meta_class_coverage_complete:
            return self._failed("concern units do not cover exactly SMC-01…10 (BRC-3 / SMI-01)")
        return self._passed(coverage="SMC-01…10")


class BandRelationshipClosureCheck(ValidationCheck):
    """BCC-5 / SMI-02 — the band spine closes over SMR-01…13 (via the CERTIFIED U11)."""

    check_id = "meta-relationships-closed"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Band spine closes over the thirteen meta-relationships SMR-01…13 (via U11)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.integration_closed:
            return self._failed("band spine does not close over SMR-01…13 (BCC-5 / SMI-02)")
        return self._passed()


class BandMetaModelIntegrationCheck(ValidationCheck):
    """BRC-6 / BCC-3 — the U11 meta-model integration closure holds (SMI-01…07)."""

    check_id = "band11-metamodel-integration-closed"
    severity = Severity.BLOCKING
    description = "The U11 meta-model integration closure holds over SMI-01…07 (BRC-6)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.integration_closed:
            return self._failed("meta-model integration closure incomplete (BRC-6)")
        return self._passed()


class BandFoundingAcyclicCheck(ValidationCheck):
    """BRC-4 / BCC-4 / SMK-03 — the band unit founding graph is acyclic, downward-only."""

    check_id = "founding-acyclic"  # shared id — reused by the SMC-01 CCE gate suite (CC-3)
    severity = Severity.BLOCKING
    description = "The Band-11 unit founding graph is acyclic and downward-only (BRC-4)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.dependency_acyclic:
            return self._failed("band unit founding graph is not acyclic (BRC-4)")
        return self._passed()


class BandReuseIntegrityCheck(ValidationCheck):
    """BRC-5 / BCC-6 / USL-02 — every unit reused by reference; nothing redefined."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Every unit reused by reference (certification id); no redefinition (BRC-5)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.substrate_refs:
            return self._failed("no substrate reference recorded (BRC-5)")
        if not subject.all_units_certified:
            return self._failed("a unit was owned, not referenced (BRC-5)")
        if not subject.reuses_by_reference:
            return self._failed("reuse-by-reference not satisfied (BRC-5)")
        return self._passed(substrate=list(subject.substrate_refs))


class BandVersionedCheck(ValidationCheck):
    """USL-12 — the completion record records an explicit version."""

    check_id = "band11-versioned"
    severity = Severity.BLOCKING
    description = "Band-11 completion record records an explicit version (USL-12)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("band-11 completion record records no version (USL-12)")
        return self._passed(version=subject.version)


class BandValidStateCheck(ValidationCheck):
    """USL-12 — the record holds a valid SOS-01…06 lifecycle state."""

    check_id = "band11-valid-state"
    severity = Severity.BLOCKING
    description = "Band-11 completion record holds a valid SOS-01…06 lifecycle state (USL-12)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if subject.band_state not in _STATE_VALUES:
            return self._failed("invalid band-11 completion state", state=subject.band_state)
        return self._passed(state=subject.band_state)


class BandIndependenceCheck(ValidationCheck):
    """BCC-7 / C6 / USL-15 — the record names/selects no technology (material)."""

    check_id = "band11-independence"
    severity = Severity.BLOCKING
    description = "No service/transport/integration technology named or selected (BCC-7 / USL-15)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.selects_technology:
            return self._failed("a technology was named/selected (BCC-7 / USL-15)")
        return self._passed()


class BandNonProjectionCheck(ValidationCheck):
    """BCC-8 — realization completion is never operational/deployment/production readiness."""

    check_id = "band11-non-projection"
    severity = Severity.BLOCKING
    description = "Realization completion is not operational/production readiness (BCC-8)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not subject.non_projection:
            return self._failed("band completion projected as operational completion (BCC-8)")
        return self._passed()


class BandNonConstitutiveCheck(ValidationCheck):
    """BCC-7 / C7 / USL-15 — confers no authority, holds no secret, selects no technology."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Band-11 completion confers no authority, embeds no secret, no tech (USL-15)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("band-11 completion confers authority (USL-15)")
        if subject.embeds_secret:
            return self._failed("band-11 completion embeds a secret (USL-15 / RR-07)")
        if subject.selects_technology:
            return self._failed("band-11 completion selects technology (USL-15)")
        if not subject.non_constitutive:
            return self._failed("band-11 completion is constitutive (USL-15)")
        return self._passed()


class BandProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class BandTraceabilityRootedCheck(ValidationCheck):
    """BRC-7 / No-Orphan — the band lineage is rooted and closes to the 11-SERVICE anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Band lineage rooted at BAND-11 and closed to 11-SERVICE (No-Orphan) (BRC-7)."

    def evaluate(self, subject: Band11ValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("band traceability chain is empty (No-Orphan)")
        if chain[0] != BAND_CLASS:
            return self._failed("band lineage not rooted at BAND-11", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("band lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def band11_checks() -> tuple[ValidationCheck, ...]:
    """The full band-completion validation suite (deterministically ordered by the engine)."""
    return (
        BandTypedCheck(),
        BandIdentifiedCheck(),
        BandValueFidelityCheck(),
        BandInventoryCompleteCheck(),
        BandAllUnitsCertifiedCheck(),
        BandMetaClassCoverageCheck(),
        BandRelationshipClosureCheck(),
        BandMetaModelIntegrationCheck(),
        BandFoundingAcyclicCheck(),
        BandReuseIntegrityCheck(),
        BandVersionedCheck(),
        BandValidStateCheck(),
        BandIndependenceCheck(),
        BandNonProjectionCheck(),
        BandNonConstitutiveCheck(),
        BandProvisionalDisclosureCheck(),
        BandTraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class Band11Validation:
    """The bundled outcome of validating a Band11Completion (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_band11(
    completion: Band11Completion, trace: TraceabilityRecord, *, strict: bool = False
) -> Band11Validation:
    """Validate ``completion`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = Band11ValidationSubject.from_completion(completion, trace)
    engine = ValidationEngine(band11_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return Band11Validation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "Band11ValidationSubject",
    "Band11Validation",
    "band11_checks",
    "validate_band11",
]
