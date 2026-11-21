"""EC3-B13-U11 — Band-13 completion validation (readiness BRC + completion BCC evidence).

Proves a realized :class:`~infrastructure.band13.Band13Completion` record satisfies the
Band-13 readiness criteria (BRC-1…BRC-8) and completion criteria (BCC-1…BCC-8) **applied to
the EC-3 Infrastructure (Band-13) code realization**, by running deterministic checks through
the **CERTIFIED EC-1 Validation Engine** (:class:`engine.validation.executor.ValidationEngine`)
and enforcing the EC-1 acceptance gate.

The suite deliberately emits the **shared check ids** the CERTIFIED U01 CCE ten-gate suite
(:func:`infrastructure.capability_certification.cce_gates`) requires — ``traceability-rooted``,
``meta-class-single``, ``foundation-reuse-integrity``, ``infra-capability-value-fidelity``,
``founding-acyclic``, ``meta-relationships-closed``, ``provisional-state-disclosure`` — with
**band-level semantics**, so the CCE gates are reused verbatim (UIL-02 reuse-by-reference),
plus band-specific checks (``band13-*``) for the inventory/certification/integration facts.

Every check is **blocking** and is a pure predicate over an immutable
:class:`Band13ValidationSubject`, so an identical completion record yields a byte-identical
report, evidence, and acceptance decision (determinism).
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
from infrastructure.band13 import Band13Completion
from infrastructure.band13_meta import BAND_BLUEPRINT_ID, BAND_CLASS, EXPECTED_UNIT_COUNT, BandState

# --- U01 reuse by reference (UIL-02) — the certified infrastructure lineage type --
from infrastructure.capability_traceability import TraceabilityRecord

_STATE_VALUES = frozenset(s.value for s in BandState)
_ANCHOR_PREFIX = "13-INFRASTRUCTURE@"


@dataclass(frozen=True, slots=True)
class Band13ValidationSubject:
    """A normalized, immutable projection of a Band13Completion that checks evaluate."""

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
    meta_class_ownership_disjoint: bool
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
        cls, completion: Band13Completion, trace: TraceabilityRecord
    ) -> Band13ValidationSubject:
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
            meta_class_ownership_disjoint=completion.meta_class_ownership_disjoint(),
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
    """C1 — the completion record bears a non-empty ENG-004 type."""

    check_id = "band13-typed"
    severity = Severity.BLOCKING
    description = "Band-13 completion record bears a non-empty ENG-004 type_tag (UIL-03)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("band-13 completion record is untyped (UIL-03)")
        return self._passed(type_tag=subject.type_tag)


class BandIdentifiedCheck(ValidationCheck):
    """C1 — the record is identified (ENG-001) and object-borne."""

    check_id = "band13-identified"
    severity = Severity.BLOCKING
    description = "Band-13 completion record bears a deterministic ENG-001 identity."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-BAND13-"):
            return self._failed("band-13 record has no ENG-001 identity", id=subject.target_id)
        return self._passed(band_id=subject.target_id)


class BandValueFidelityCheck(ValidationCheck):
    """BRC-8 / C3 — the record's representation is ENG-003 value-faithful (content-addressed).

    Emits the shared id ``infra-capability-value-fidelity`` the U01 CCE gate suite requires
    (CC-3), reused verbatim with band-level semantics (UIL-02).
    """

    check_id = "infra-capability-value-fidelity"
    severity = Severity.BLOCKING
    description = "Band-13 completion record is content-addressed via ENG-003 encoding."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("band-13 record representation is not value-faithful")
        return self._passed(value_digest=digest)


class BandInventoryCompleteCheck(ValidationCheck):
    """BRC-1 / BCC-1 — the record inventories exactly the ten units U01…U10."""

    check_id = "band13-inventory-complete"
    severity = Severity.BLOCKING
    description = "Band-13 completion inventories exactly the ten units U01…U10 (BRC-1)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.inventory_complete or subject.unit_count != EXPECTED_UNIT_COUNT:
            return self._failed(
                "band-13 inventory is not exactly the ten units (BRC-1)",
                unit_count=subject.unit_count,
            )
        return self._passed(unit_count=subject.unit_count)


class BandAllUnitsCertifiedCheck(ValidationCheck):
    """BRC-1 / BRC-7 / BCC-1 — every inventoried unit U01…U10 is CCE-CERTIFIED (by reference)."""

    check_id = "band13-all-units-certified"
    severity = Severity.BLOCKING
    description = "Every Band-13 unit U01…U10 is CCE-CERTIFIED (reused by reference) (BRC-1/7)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.all_units_certified:
            return self._failed("a Band-13 unit is not CERTIFIED (BRC-1/BRC-7)")
        return self._passed(units_certified=subject.unit_count)


class BandMetaClassCoverageCheck(ValidationCheck):
    """BRC-3 — the units cover exactly the seventeen leaf meta-classes; non-overlapping.

    Emits the shared id ``meta-class-single`` the U01 CCE gate suite requires (CC-1).
    """

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "Band-13 units cover exactly the 17 leaf meta-classes; non-overlapping (BRC-3)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.meta_class_coverage_complete:
            return self._failed("units do not cover exactly the 17 leaf meta-classes (BRC-3)")
        if not subject.meta_class_ownership_disjoint:
            return self._failed("a leaf meta-class is owned by more than one unit (BRC-3)")
        return self._passed(coverage="INFRASTRUCTURE-005 §2 — 17/17")


class BandRelationshipClosureCheck(ValidationCheck):
    """BRC-4 / BCC-5 — the UIMM integration closes over the ten realized units.

    Emits the shared id ``meta-relationships-closed`` the U01 CCE gate suite requires (CC-3).
    """

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "Band spine closes over the UIMM dependsOn integration (via U10) (BRC-4)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.integration_closed:
            return self._failed("band spine does not close over the UIMM integration (BRC-4)")
        return self._passed()


class BandMetaModelIntegrationCheck(ValidationCheck):
    """BRC-8 / BCC-5 — the U10 UIMM integration closure holds (UIMM-CONF total)."""

    check_id = "band13-metamodel-integration-closed"
    severity = Severity.BLOCKING
    description = "The U10 UIMM integration closure holds (UIMM-CONF total) (BRC-8)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.integration_closed:
            return self._failed("UIMM meta-model integration closure incomplete (BRC-8)")
        return self._passed()


class BandIntegrationClosedCheck(ValidationCheck):
    """BRC-4 — consistency: the integration closure keys all hold (UIL/WF alignments)."""

    check_id = "band13-integration-closed"
    severity = Severity.BLOCKING
    description = "The Band-13 UIMM integration closure keys all hold (consistency) (BRC-4)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.integration_closed:
            return self._failed("band integration closure incomplete (BRC-4)")
        return self._passed()


class BandFoundingAcyclicCheck(ValidationCheck):
    """BRC-2 / BCC-4 — the band unit founding graph is acyclic, downward-only.

    Emits the shared id ``founding-acyclic`` the U01 CCE gate suite requires (CC-3).
    """

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The Band-13 unit founding graph is acyclic and downward-only (BRC-2)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.dependency_acyclic:
            return self._failed("band unit founding graph is not acyclic (BRC-2)")
        return self._passed()


class BandReuseIntegrityCheck(ValidationCheck):
    """BRC-5 / BCC-6 / UIL-02 — every unit reused by reference; nothing redefined.

    Emits the shared id ``foundation-reuse-integrity`` the U01 CCE gate suite requires (CC-2).
    """

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "Every unit reused by reference (certification id); no redefinition (BRC-5)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.substrate_refs:
            return self._failed("no substrate reference recorded (BRC-5)")
        if not subject.all_units_certified:
            return self._failed("a unit was owned, not referenced (BRC-5)")
        if not subject.reuses_by_reference:
            return self._failed("reuse-by-reference not satisfied (BRC-5)")
        return self._passed(substrate=list(subject.substrate_refs))


class BandVersionedCheck(ValidationCheck):
    """INFRASTRUCTURE-003 §3 — the completion record records an explicit version."""

    check_id = "band13-versioned"
    severity = Severity.BLOCKING
    description = "Band-13 completion record records an explicit version."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("band-13 completion record records no version")
        return self._passed(version=subject.version)


class BandValidStateCheck(ValidationCheck):
    """INFRASTRUCTURE-003 §3 — the record holds a valid forward-only lifecycle state."""

    check_id = "band13-valid-state"
    severity = Severity.BLOCKING
    description = "Band-13 completion record holds a valid forward-only lifecycle state."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if subject.band_state not in _STATE_VALUES:
            return self._failed("invalid band-13 completion state", state=subject.band_state)
        return self._passed(state=subject.band_state)


class BandIndependenceCheck(ValidationCheck):
    """BRC-6 / C7 / UIL-15 — the record names/selects no technology (material)."""

    check_id = "band13-independence"
    severity = Severity.BLOCKING
    description = "No infrastructure/transport technology named or selected (BRC-6 / UIL-15)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.selects_technology:
            return self._failed("a technology was named/selected (BRC-6 / UIL-15)")
        return self._passed()


class BandNonProjectionCheck(ValidationCheck):
    """BCC-8 — realization completion is never operational/deployment/production readiness."""

    check_id = "band13-non-projection"
    severity = Severity.BLOCKING
    description = "Realization completion is not operational/production readiness (WF-12)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not subject.non_projection:
            return self._failed("band completion projected as operational completion (WF-12)")
        return self._passed()


class BandNonConstitutiveCheck(ValidationCheck):
    """BRC-6 / C7 / UIL-15 — confers no authority, holds no secret, selects no technology."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Band-13 completion confers no authority, embeds no secret, no tech (UIL-15)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("band-13 completion confers authority (UIL-15)")
        if subject.embeds_secret:
            return self._failed("band-13 completion embeds a secret (UIL-15)")
        if subject.selects_technology:
            return self._failed("band-13 completion selects technology (UIL-15)")
        if not subject.non_constitutive:
            return self._failed("band-13 completion is constitutive (UIL-15)")
        return self._passed()


class BandProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted).

    Emits the shared id ``provisional-state-disclosure`` the U01 CCE gate suite requires (CC-7).
    """

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class BandTraceabilityRootedCheck(ValidationCheck):
    """BCC-8 / No-Orphan — the band lineage is rooted and closes to the 13-INFRASTRUCTURE anchor.

    Emits the shared id ``traceability-rooted`` the U01 CCE gate suite requires (CC-1 / CC-5).
    """

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Band lineage rooted at BAND-13 and closed to 13-INFRASTRUCTURE (No-Orphan)."

    def evaluate(self, subject: Band13ValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("band traceability chain is empty (No-Orphan)")
        if chain[0] != BAND_CLASS:
            return self._failed("band lineage not rooted at BAND-13", head=chain[0])
        if not any(link.startswith(_ANCHOR_PREFIX) for link in chain):
            return self._failed("band lineage does not close to the 13-INFRASTRUCTURE anchor")
        return self._passed(links=len(chain))


def band13_checks() -> tuple[ValidationCheck, ...]:
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
        BandIntegrationClosedCheck(),
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
class Band13Validation:
    """The bundled outcome of validating a Band13Completion (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_band13(
    completion: Band13Completion, trace: TraceabilityRecord, *, strict: bool = False
) -> Band13Validation:
    """Validate ``completion`` through the CERTIFIED EC-1 engine and enforce acceptance."""
    subject = Band13ValidationSubject.from_completion(completion, trace)
    engine = ValidationEngine(band13_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return Band13Validation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "Band13ValidationSubject",
    "Band13Validation",
    "band13_checks",
    "validate_band13",
]
