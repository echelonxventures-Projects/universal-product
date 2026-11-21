"""EC3-B11-U11 — Meta-model validation (meta-invariants SMI-01…07 + USL conformance).

This module proves a realized :class:`~service.model.MetaModel` satisfies the seven
meta-invariants (SERVICE-005 §8, SMI-01…07), is **Service-law conformant** (SERVICE-001 §7,
esp. **USL-02 reuse-by-reference** and **USL-15 non-constitutive**, plus USL-03/04/05), and
is a well-formed model-of-the-model, by running a suite of deterministic, service-layer
checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`ModelValidationSubject`, so an
identical meta-model yields a byte-identical report, evidence, and acceptance decision
(VC-4). Every check is **blocking**. A subset of check ids (``meta-class-single``,
``meta-relationships-closed``, ``foundation-reuse-integrity``, ``service-value-fidelity``,
``founding-acyclic``, ``provisional-state-disclosure``, ``traceability-rooted``) is
**shared with the CERTIFIED SMC-01 surface**, so the SMC-01 CCE ten-gate suite
(:func:`service.service_certification.cce_gates`) is reused verbatim by the meta-model
certification (USL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance
from service.model import MetaModel
from service.model_meta import (
    META_CLASSES,
    META_RELATIONSHIPS,
    MODEL_CLASS,
    ONTOLOGY_ENTITIES,
    ONTOLOGY_RELATIONSHIPS,
    ModelState,
)
from service.service_traceability import TraceabilityRecord

#: The blueprint id a meta-model realizes (its model-class) — used by the report.
MODEL_BLUEPRINT_ID = MODEL_CLASS

_STATE_VALUES = frozenset(s.value for s in ModelState)
_META_CLASSES = frozenset(META_CLASSES)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)
_ONTOLOGY_ENTITIES = frozenset(ONTOLOGY_ENTITIES)
_ONTOLOGY_RELATIONSHIPS = frozenset(ONTOLOGY_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class ModelValidationSubject:
    """A normalized, immutable projection of a MetaModel that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1 ``ValidationEngine``
    consumes) plus the model's meta-facts. Holds no runtime state and no wall-clock, so it
    is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    value_digest: str
    meta_classes: tuple[str, ...]
    meta_relationships: tuple[str, ...]
    modelled_entities: tuple[str, ...]
    modelled_relationships: tuple[str, ...]
    declares_closure: bool
    declares_relationship_closure: bool
    is_total: bool
    founding_acyclic: bool
    members_certified: bool
    map_resolves: bool
    reuses_by_reference: bool
    non_projection: bool
    confers_authority: bool
    embeds_secret: bool
    names_technology: bool
    selects_technology: bool
    redefines_el1: bool
    non_constitutive: bool
    version: str
    model_state: str
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_model(cls, model: MetaModel, trace: TraceabilityRecord) -> ModelValidationSubject:
        """Project ``model`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=model.model_id,
            blueprint_id=MODEL_BLUEPRINT_ID,
            meta_class=model.meta_class,
            name=model.name,
            type_tag=model.type_tag,
            value_digest=model.structure_digest,
            meta_classes=model.meta_classes(),
            meta_relationships=model.meta_relationships(),
            modelled_entities=model.modelled_entities(),
            modelled_relationships=model.modelled_relationships(),
            declares_closure=model.declares_closure(),
            declares_relationship_closure=model.declares_relationship_closure(),
            is_total=model.is_total(),
            founding_acyclic=model.is_founding_acyclic(),
            members_certified=model.members_certified(),
            map_resolves=model.map_resolves(),
            reuses_by_reference=model.reuses_by_reference(),
            non_projection=model.is_non_projection(),
            confers_authority=model.confers_authority(),
            embeds_secret=model.embeds_secret(),
            names_technology=model.names_technology(),
            selects_technology=model.selects_technology(),
            redefines_el1=model.redefines_el1(),
            non_constitutive=model.is_non_constitutive(),
            version=model.version,
            model_state=model.state.value,
            substrate_refs=tuple(model.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Service-layer validation checks (each maps to explicit SMI*/USL* obligations)
# ---------------------------------------------------------------------------


class ModelTypedCheck(ValidationCheck):
    """USL-03 / SMK-01 — the meta-model bears a non-empty ENG-004 type."""

    check_id = "metamodel-typed"
    severity = Severity.BLOCKING
    description = "Meta-model bears a non-empty ENG-004 type_tag (USL-03 / SMK-01)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("meta-model is untyped (USL-03 / SMK-01)")
        return self._passed(type_tag=subject.type_tag)


class ModelNamedCheck(ValidationCheck):
    """The meta-model has an explicit, decidable name."""

    check_id = "metamodel-named"
    severity = Severity.BLOCKING
    description = "Meta-model has an explicit, non-empty name."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.name.strip():
            return self._failed("meta-model is unnamed")
        return self._passed(name=subject.name)


class ModelIdentifiedCheck(ValidationCheck):
    """USL-04/05 / SMK-01 / C1 — the object is identified (ENG-001) and object-borne."""

    check_id = "metamodel-identified"
    severity = Severity.BLOCKING
    description = "Meta-model bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-METAMODEL-"):
            return self._failed("meta-model has no ENG-001 identity (USL-04)", id=subject.target_id)
        return self._passed(model_id=subject.target_id)


class ModelValueFidelityCheck(ValidationCheck):
    """USL-03 (transitive) / C3 — the object's representation is ENG-003 value-faithful."""

    check_id = "service-value-fidelity"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Meta-model representation is content-addressed via ENG-003 encoding (USL-03)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("meta-model representation is not value-faithful (USL-03)")
        return self._passed(value_digest=digest)


class MetaClassClosureCheck(ValidationCheck):
    """V1 / SMI-01 — the members are exactly the ten meta-classes SMC-01…10 (closure)."""

    check_id = "meta-class-single"  # shared id — reused by the SMC-01 CCE gate suite (CC-1)
    severity = Severity.BLOCKING
    description = "Meta-model closes over exactly the ten meta-classes SMC-01…10 (SMI-01)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        present = set(subject.meta_classes)
        if present != _META_CLASSES or len(subject.meta_classes) != len(_META_CLASSES):
            return self._failed(
                "meta-class set is not exactly SMC-01…10 (SMI-01)",
                present=sorted(present),
            )
        if not subject.declares_closure:
            return self._failed("meta-model does not declare closure (SMI-01)")
        return self._passed(meta_classes=list(subject.meta_classes))


class MetaRelationshipClosureCheck(ValidationCheck):
    """V2 / SMI-02 — the edges are exactly the thirteen meta-relationships SMR-01…13."""

    check_id = "meta-relationships-closed"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Meta-model closes over exactly the thirteen meta-relationships SMR-01…13."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        present = set(subject.meta_relationships)
        outside = present - _META_RELATIONSHIPS
        if outside:
            return self._failed("relationships outside SMR-01…13 (SMI-02)", outside=sorted(outside))
        if present != _META_RELATIONSHIPS or len(subject.meta_relationships) != len(
            _META_RELATIONSHIPS
        ):
            return self._failed("relationship set is not exactly SMR-01…13 (SMI-02)")
        if not subject.declares_relationship_closure:
            return self._failed("meta-model does not declare relationship closure (SMI-02)")
        return self._passed(meta_relationships=list(subject.meta_relationships))


class MetaModelTotalityCheck(ValidationCheck):
    """SMI-03 — members model exactly SOE-01…10 and edges model exactly SOR-01…13."""

    check_id = "metamodel-totality"
    severity = Severity.BLOCKING
    description = "Members model exactly SOE-01…10; edges model exactly SOR-01…13 (SMI-03)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if set(subject.modelled_entities) != _ONTOLOGY_ENTITIES or len(
            subject.modelled_entities
        ) != len(_ONTOLOGY_ENTITIES):
            return self._failed("ontology entity coverage is not total (SMI-03)")
        if set(subject.modelled_relationships) != _ONTOLOGY_RELATIONSHIPS or len(
            subject.modelled_relationships
        ) != len(_ONTOLOGY_RELATIONSHIPS):
            return self._failed("ontology relationship coverage is not total (SMI-03)")
        if not subject.is_total:
            return self._failed("meta-model is not total (SMI-03)")
        return self._passed(entities=len(subject.modelled_entities))


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / SMI-04 / SMK-03 — the founding meta-graph (SMR-02/03/04/05) is acyclic (a DAG)."""

    check_id = "founding-acyclic"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The meta-model founding graph (SMR-02/03/04/05) is acyclic (SMI-04 / SMK-03)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding meta-graph is not acyclic (SMI-04)")
        return self._passed()


class ModelMembersCertifiedCheck(ValidationCheck):
    """Integration — every member resolves to a CERTIFIED concern meta-class realization."""

    check_id = "metamodel-members-certified"
    severity = Severity.BLOCKING
    description = "Every meta-class member resolves to a CERTIFIED realization (integration)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.members_certified:
            return self._failed("a meta-class member is not CERTIFIED (integration)")
        return self._passed(members=len(subject.meta_classes))


class ModelMapResolvesCheck(ValidationCheck):
    """§9 — every meta-model map edge resolves within the closure or the frozen foundations."""

    check_id = "metamodel-map-resolves"
    severity = Severity.BLOCKING
    description = "Every meta-model map edge resolves within the closure/foundations (§9)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.map_resolves:
            return self._failed("a meta-model map edge does not resolve (§9)")
        return self._passed()


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (SMK-01 typed/identified, SMK-03 acyclic, SMK-08)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "SMK-01 (typed+identified), SMK-03 (founding acyclic), SMK-08 (no-tech) (V3)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # SMK-01 typed
            and subject.name.strip()  # named
            and subject.target_id  # SMK-01 identified
            and subject.declares_closure  # SMI-01
            and subject.declares_relationship_closure  # SMI-02
            and subject.is_total  # SMI-03
            and subject.founding_acyclic  # SMK-03 acyclic
            and subject.map_resolves  # §9 edges resolve
            and not subject.confers_authority  # SMK-08 no authority
            and not subject.names_technology  # SMK-08 no technology
        )
        if not ok:
            return self._failed("SMK-01/03/08 (SMI-01/02/03/04) not satisfied (V3)")
        return self._passed(constraints=["SMK-01", "SMK-03", "SMK-08"])


class ModelValidStateCheck(ValidationCheck):
    """V5 / USL-12 — the object holds a valid SOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"  # shared id — the SMC-01 V5 check id
    severity = Severity.BLOCKING
    description = "Meta-model holds a valid SOS-01…06 lifecycle state (V5 / USL-12)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if subject.model_state not in _STATE_VALUES:
            return self._failed("invalid meta-model state (V5)", state=subject.model_state)
        return self._passed(state=subject.model_state)


class ModelVersionedCheck(ValidationCheck):
    """USL-12 — the object records an explicit version (additive/append-only)."""

    check_id = "metamodel-versioned"
    severity = Severity.BLOCKING
    description = "Meta-model object records an explicit version (USL-12)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("meta-model object records no version (USL-12)")
        return self._passed(version=subject.version)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """SMI-05 / USL-02 — EL-1 + ten CERTIFIED units + RL-F2/PL-F2/DF-2 reused by reference."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + ten CERTIFIED units + RL-F2/PL-F2/DF-2 referenced, redefined 0 (SMI-05)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/RL-F2/PL-F2/DF-2/SMC primitive was redefined (SMI-05)")
        if not subject.substrate_refs:
            return self._failed("no substrate reference recorded (SMI-05)")
        if not subject.members_certified:
            return self._failed("a member realization was owned, not referenced (SMI-05)")
        if not subject.reuses_by_reference:
            return self._failed("reuse-by-reference not satisfied (SMI-05)")
        return self._passed(substrate=list(subject.substrate_refs))


class ModelIndependenceCheck(ValidationCheck):
    """SMI-06 / USL-15 / SMK-08 / C7 — the object names no technology (material)."""

    check_id = "technology-independence"  # shared id — the SMC-01 no-tech check id
    severity = Severity.BLOCKING
    description = "No service/API/transport technology named (SMI-06 / USL-15 / SMK-08)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.selects_technology:
            return self._failed("a service/API/transport technology was named (SMI-06)")
        return self._passed()


class NonProjectionCheck(ValidationCheck):
    """SMI-07 — model coverage is never roadmap/implementation/operational completion."""

    check_id = "metamodel-non-projection"
    severity = Severity.BLOCKING
    description = "Model coverage is never roadmap/operational completion (SMI-07 / STATUS-001 §2)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.non_projection:
            return self._failed("meta-model projects model coverage as completion (SMI-07)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """SMI-06 / USL-15 / C7 — the object confers no authority, holds no secret, selects no tech."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Meta-model confers no authority, embeds no secret, selects no tech (USL-15)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("meta-model confers authority (USL-15 / SMI-06)")
        if subject.embeds_secret:
            return self._failed("meta-model embeds a secret (USL-15 / RR-07)")
        if subject.selects_technology:
            return self._failed("meta-model selects technology (USL-15 / SMK-08)")
        if not subject.non_constitutive:
            return self._failed("meta-model is constitutive (SMI-06)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§10 / AC — the No-Orphan lineage is rooted and closes to the 11-SERVICE anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the SMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at the USM and closed to 11-SERVICE (No-Orphan)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the model-class", head=chain[0])
        if not any(link.startswith("11-SERVICE@") for link in chain):
            return self._failed("lineage does not close to the 11-SERVICE anchor")
        return self._passed(links=len(chain))


def model_checks() -> tuple[ValidationCheck, ...]:
    """The full service-layer validation suite (deterministically ordered by the engine)."""
    return (
        ModelTypedCheck(),
        ModelNamedCheck(),
        ModelIdentifiedCheck(),
        ModelValueFidelityCheck(),
        MetaClassClosureCheck(),
        MetaRelationshipClosureCheck(),
        MetaModelTotalityCheck(),
        FoundingAcyclicCheck(),
        ModelMembersCertifiedCheck(),
        ModelMapResolvesCheck(),
        MetaConstraintsCheck(),
        ModelValidStateCheck(),
        ModelVersionedCheck(),
        FoundationReuseIntegrityCheck(),
        ModelIndependenceCheck(),
        NonProjectionCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class ModelValidation:
    """The bundled outcome of validating a MetaModel (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_model(
    model: MetaModel, trace: TraceabilityRecord, *, strict: bool = False
) -> ModelValidation:
    """Validate ``model`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected object raises via the EC-1
    acceptance gate.
    """
    subject = ModelValidationSubject.from_model(model, trace)
    engine = ValidationEngine(model_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return ModelValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "MODEL_BLUEPRINT_ID",
    "ModelValidationSubject",
    "ModelValidation",
    "model_checks",
    "validate_model",
]
