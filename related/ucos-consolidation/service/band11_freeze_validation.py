"""EC3-B11-U13 — Band-11 freeze validation (freeze precondition + effect evidence).

Proves a realized :class:`~service.band11_freeze.Band11Freeze` record satisfies the freeze
preconditions (FP-1…FP-6, mirroring SERVICE-015 P-1…P-6) and freeze effects (FE-1…FE-5,
mirroring SERVICE-015 OUTPUT 3), by running deterministic, service-layer checks through the
**CERTIFIED EC-1 Validation Engine** (:class:`engine.validation.executor.ValidationEngine`)
and enforcing the EC-1 acceptance gate.

The suite deliberately emits the **shared check ids** the CERTIFIED SMC-01 CCE ten-gate
suite (:func:`service.service_certification.cce_gates`) requires — ``traceability-rooted``,
``meta-class-single``, ``foundation-reuse-integrity``, ``service-value-fidelity``,
``founding-acyclic``, ``meta-relationships-closed``, ``provisional-state-disclosure`` — with
**freeze-level semantics**, so the CCE gates are reused verbatim (USL-02 reuse-by-reference),
plus freeze-specific checks (``freeze-*``) for the inventory/certification/baseline facts.

Every check is **blocking** and is a pure predicate over an immutable
:class:`FreezeValidationSubject`, so an identical freeze record yields a byte-identical
report, evidence, and acceptance decision (FP-6 determinism).
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
from service.band11_freeze import Band11Freeze
from service.band11_freeze_meta import (
    EXPECTED_FROZEN_UNIT_COUNT,
    FREEZE_BLUEPRINT_ID,
    FREEZE_CLASS,
    FreezeState,
)
from service.service_traceability import TraceabilityRecord

_STATE_VALUES = frozenset(s.value for s in FreezeState)


@dataclass(frozen=True, slots=True)
class FreezeValidationSubject:
    """A normalized, immutable projection of a Band11Freeze that checks evaluate."""

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    value_digest: str
    unit_count: int
    inventory_complete: bool
    all_units_certified: bool
    all_units_frozen: bool
    meta_class_coverage_complete: bool
    band_completion_referenced: bool
    dependency_acyclic: bool
    integration_closed: bool
    reuses_by_reference: bool
    effects_declared: bool
    immutable_baseline: bool
    non_projection: bool
    confers_authority: bool
    embeds_secret: bool
    names_technology: bool
    selects_technology: bool
    non_constitutive: bool
    version: str
    freeze_state: str
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_freeze(
        cls, freeze: Band11Freeze, trace: TraceabilityRecord
    ) -> FreezeValidationSubject:
        """Project ``freeze`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=freeze.freeze_id,
            blueprint_id=FREEZE_BLUEPRINT_ID,
            meta_class=freeze.meta_class,
            name=freeze.name,
            type_tag=freeze.type_tag,
            value_digest=freeze.baseline_digest,
            unit_count=len(freeze.units),
            inventory_complete=freeze.inventory_complete(),
            all_units_certified=freeze.all_units_certified(),
            all_units_frozen=freeze.all_units_frozen(),
            meta_class_coverage_complete=freeze.meta_class_coverage_complete(),
            band_completion_referenced=freeze.band_completion_referenced(),
            dependency_acyclic=freeze.dependency_acyclic(),
            integration_closed=freeze.integration_closed(),
            reuses_by_reference=freeze.reuses_by_reference(),
            effects_declared=freeze.effects_declared(),
            immutable_baseline=freeze.is_immutable_baseline(),
            non_projection=freeze.is_non_projection(),
            confers_authority=freeze.confers_authority(),
            embeds_secret=freeze.embeds_secret(),
            names_technology=freeze.names_technology(),
            selects_technology=freeze.selects_technology(),
            non_constitutive=freeze.is_non_constitutive(),
            version=freeze.version,
            freeze_state=freeze.state.value,
            substrate_refs=tuple(freeze.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Freeze validation checks (each maps to explicit FP*/FE* obligations)
# ---------------------------------------------------------------------------


class FreezeTypedCheck(ValidationCheck):
    """C1 / SMK-01 — the freeze record bears a non-empty ENG-004 type."""

    check_id = "freeze-typed"
    severity = Severity.BLOCKING
    description = "Band-11 freeze record bears a non-empty ENG-004 type_tag (SMK-01)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("band-11 freeze record is untyped (SMK-01)")
        return self._passed(type_tag=subject.type_tag)


class FreezeIdentifiedCheck(ValidationCheck):
    """C1 / SMK-01 — the record is identified (ENG-001) and object-borne."""

    check_id = "freeze-identified"
    severity = Severity.BLOCKING
    description = "Band-11 freeze record bears a deterministic ENG-001 identity."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-FREEZE-BAND11-"):
            return self._failed("band-11 freeze has no ENG-001 identity", id=subject.target_id)
        return self._passed(freeze_id=subject.target_id)


class FreezeBaselineFidelityCheck(ValidationCheck):
    """FP-6 / C3 — the baseline seal is ENG-003 value-faithful (content-addressed)."""

    check_id = "service-value-fidelity"  # shared id — reused by the SMC-01 CCE gate suite (CC-3)
    severity = Severity.BLOCKING
    description = "Band-11 freeze baseline is content-addressed via ENG-003 encoding."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("band-11 freeze baseline is not value-faithful")
        return self._passed(baseline_digest=digest)


class FreezeInventoryCompleteCheck(ValidationCheck):
    """FP-1 — the record inventories exactly the twelve units U01…U12."""

    check_id = "freeze-inventory-complete"
    severity = Severity.BLOCKING
    description = "Band-11 freeze inventories exactly the twelve units U01…U12 (FP-1)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.inventory_complete or subject.unit_count != EXPECTED_FROZEN_UNIT_COUNT:
            return self._failed(
                "band-11 freeze inventory is not exactly the twelve units (FP-1)",
                unit_count=subject.unit_count,
            )
        return self._passed(unit_count=subject.unit_count)


class FreezeAllUnitsCertifiedCheck(ValidationCheck):
    """FP-1 — every inventoried unit U01…U12 is CCE-CERTIFIED (by reference)."""

    check_id = "freeze-all-units-certified"
    severity = Severity.BLOCKING
    description = "Every Band-11 unit U01…U12 is CCE-CERTIFIED (reused by reference) (FP-1)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.all_units_certified:
            return self._failed("a Band-11 unit is not CERTIFIED (FP-1)")
        return self._passed(units_certified=subject.unit_count)


class FreezeAllUnitsFrozenCheck(ValidationCheck):
    """FE-1 — every inventoried unit is marked FROZEN (immutability)."""

    check_id = "freeze-all-units-frozen"
    severity = Severity.BLOCKING
    description = "Every Band-11 unit U01…U12 is marked FROZEN (immutability, FE-1)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.all_units_frozen:
            return self._failed("a Band-11 unit is not FROZEN (FE-1)")
        return self._passed(units_frozen=subject.unit_count)


class FreezeMetaClassCoverageCheck(ValidationCheck):
    """FP-3 / SMI-01 — the concern units cover exactly SMC-01…10 (closure)."""

    check_id = "meta-class-single"  # shared id — reused by the SMC-01 CCE gate suite (CC-1)
    severity = Severity.BLOCKING
    description = "Band-11 concern units cover exactly the ten meta-classes SMC-01…10 (SMI-01)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.meta_class_coverage_complete:
            return self._failed("concern units do not cover exactly SMC-01…10 (FP-3 / SMI-01)")
        return self._passed(coverage="SMC-01…10")


class FreezeRelationshipClosureCheck(ValidationCheck):
    """FP-4 / SMI-02 — the band spine closes over SMR-01…13 (via the CERTIFIED U11)."""

    check_id = "meta-relationships-closed"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Band spine closes over the thirteen meta-relationships SMR-01…13 (via U11)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.integration_closed:
            return self._failed("band spine does not close over SMR-01…13 (FP-4 / SMI-02)")
        return self._passed()


class FreezeBandCompletionReferencedCheck(ValidationCheck):
    """FP-4 — the U12 band completion (certification-of-certifications) is referenced."""

    check_id = "freeze-band-completion-referenced"
    severity = Severity.BLOCKING
    description = "The U12 Band-11 completion is referenced by id + certification id (FP-4)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.band_completion_referenced:
            return self._failed("U12 band completion is not referenced (FP-4)")
        return self._passed()


class FreezeFoundingAcyclicCheck(ValidationCheck):
    """FP-2 / SMK-03 — the frozen unit founding graph is acyclic, downward-only."""

    check_id = "founding-acyclic"  # shared id — reused by the SMC-01 CCE gate suite (CC-3)
    severity = Severity.BLOCKING
    description = "The Band-11 frozen unit founding graph is acyclic and downward-only (FP-2)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.dependency_acyclic:
            return self._failed("frozen unit founding graph is not acyclic (FP-2)")
        return self._passed()


class FreezeReuseIntegrityCheck(ValidationCheck):
    """FP-5 / FE-2 / USL-02 — every unit reused by reference; nothing redefined."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Every unit reused by reference (certification id); no redefinition (FP-5)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.substrate_refs:
            return self._failed("no substrate reference recorded (FP-5)")
        if not subject.all_units_certified:
            return self._failed("a unit was owned, not referenced (FP-5)")
        if not subject.reuses_by_reference:
            return self._failed("reuse-by-reference not satisfied (FP-5)")
        return self._passed(substrate=list(subject.substrate_refs))


class FreezeEffectsDeclaredCheck(ValidationCheck):
    """FE-3/FE-4/FE-5 — the five SERVICE-015-style freeze effects are declared."""

    check_id = "freeze-effects-declared"
    severity = Severity.BLOCKING
    description = "The baseline declares exactly the five freeze effects FE-1…FE-5."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.effects_declared:
            return self._failed("freeze effects FE-1…FE-5 not fully declared")
        return self._passed()


class FreezeImmutableBaselineCheck(ValidationCheck):
    """FE-1 — the record carries a valid content-addressed immutable baseline seal."""

    check_id = "freeze-immutable-baseline"
    severity = Severity.BLOCKING
    description = "Band-11 freeze carries a valid content-addressed immutable baseline (FE-1)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.immutable_baseline:
            return self._failed("band-11 freeze baseline seal is absent/malformed (FE-1)")
        return self._passed()


class FreezeVersionedCheck(ValidationCheck):
    """USL-12 — the freeze record records an explicit version."""

    check_id = "freeze-versioned"
    severity = Severity.BLOCKING
    description = "Band-11 freeze record records an explicit version (USL-12)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("band-11 freeze record records no version (USL-12)")
        return self._passed(version=subject.version)


class FreezeValidStateCheck(ValidationCheck):
    """USL-12 — the record holds a valid SOS-01…06 lifecycle state."""

    check_id = "freeze-valid-state"
    severity = Severity.BLOCKING
    description = "Band-11 freeze record holds a valid SOS-01…06 lifecycle state (USL-12)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if subject.freeze_state not in _STATE_VALUES:
            return self._failed("invalid band-11 freeze state", state=subject.freeze_state)
        return self._passed(state=subject.freeze_state)


class FreezeIndependenceCheck(ValidationCheck):
    """C6 / USL-15 — the record names/selects no technology (material)."""

    check_id = "freeze-independence"
    severity = Severity.BLOCKING
    description = "No service/transport/integration technology named or selected (USL-15)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.selects_technology:
            return self._failed("a technology was named/selected (USL-15)")
        return self._passed()


class FreezeNonProjectionCheck(ValidationCheck):
    """FE-4 — a freeze baseline is never operational/deployment/production readiness."""

    check_id = "freeze-non-projection"
    severity = Severity.BLOCKING
    description = "Freeze baseline is not operational/production readiness (FE-4 / STATUS-001)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not subject.non_projection:
            return self._failed("freeze baseline projected as operational readiness (FE-4)")
        return self._passed()


class FreezeNonConstitutiveCheck(ValidationCheck):
    """FE-3 / C7 / USL-15 — confers no authority, holds no secret, selects no technology."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Band-11 freeze confers no authority, embeds no secret, no tech (USL-15)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("band-11 freeze confers authority (USL-15)")
        if subject.embeds_secret:
            return self._failed("band-11 freeze embeds a secret (USL-15 / RR-07)")
        if subject.selects_technology:
            return self._failed("band-11 freeze selects technology (USL-15)")
        if not subject.non_constitutive:
            return self._failed("band-11 freeze is constitutive (USL-15)")
        return self._passed()


class FreezeProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class FreezeTraceabilityRootedCheck(ValidationCheck):
    """No-Orphan — the freeze lineage is rooted and closes to the 11-SERVICE anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Freeze lineage rooted at BAND-11-FREEZE and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: FreezeValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("freeze traceability chain is empty (No-Orphan)")
        if chain[0] != FREEZE_CLASS:
            return self._failed("freeze lineage not rooted at BAND-11-FREEZE", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("freeze lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def band11_freeze_checks() -> tuple[ValidationCheck, ...]:
    """The full freeze validation suite (deterministically ordered by the engine)."""
    return (
        FreezeTypedCheck(),
        FreezeIdentifiedCheck(),
        FreezeBaselineFidelityCheck(),
        FreezeInventoryCompleteCheck(),
        FreezeAllUnitsCertifiedCheck(),
        FreezeAllUnitsFrozenCheck(),
        FreezeMetaClassCoverageCheck(),
        FreezeRelationshipClosureCheck(),
        FreezeBandCompletionReferencedCheck(),
        FreezeFoundingAcyclicCheck(),
        FreezeReuseIntegrityCheck(),
        FreezeEffectsDeclaredCheck(),
        FreezeImmutableBaselineCheck(),
        FreezeVersionedCheck(),
        FreezeValidStateCheck(),
        FreezeIndependenceCheck(),
        FreezeNonProjectionCheck(),
        FreezeNonConstitutiveCheck(),
        FreezeProvisionalDisclosureCheck(),
        FreezeTraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class Band11FreezeValidation:
    """The bundled outcome of validating a Band11Freeze (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_band11_freeze(
    freeze: Band11Freeze, trace: TraceabilityRecord, *, strict: bool = False
) -> Band11FreezeValidation:
    """Validate ``freeze`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = FreezeValidationSubject.from_freeze(freeze, trace)
    engine = ValidationEngine(band11_freeze_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return Band11FreezeValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "FreezeValidationSubject",
    "Band11FreezeValidation",
    "band11_freeze_checks",
    "validate_band11_freeze",
]
