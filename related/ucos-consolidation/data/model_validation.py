"""EC3-B10-U11 — Meta-model validation (meta-invariants DMI-01…07 + UDL conformance).

This module proves a realized :class:`~data.model.MetaModel` satisfies the seven
meta-invariants (DATA-005 §8, DMI-01…07), is **Data-law conformant** (DATA-001 §7, esp.
**UDL-02 reuse-by-reference** and **UDL-15 non-constitutive**, plus UDL-03/04/05), and is
a well-formed model-of-the-model, by running a suite of deterministic, data-layer checks
through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`ModelValidationSubject`, so an
identical meta-model yields a byte-identical report, evidence, and acceptance decision
(VC-4). Every check is **blocking**. A subset of check ids (``meta-class-single``,
``meta-relationships-closed``, ``foundation-reuse-integrity``, ``data-value-fidelity``,
``founding-acyclic``, ``provisional-state-disclosure``, ``traceability-rooted``) is
**shared with the CERTIFIED DMC-01 surface**, so the DMC-01 CCE ten-gate suite
(:func:`data.certification.cce_gates`) is reused verbatim by the meta-model certification
(UDL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.model import MetaModel
from data.model_meta import (
    META_CLASSES,
    META_RELATIONSHIPS,
    MODEL_CLASS,
    ONTOLOGY_ENTITIES,
    ONTOLOGY_RELATIONSHIPS,
    ModelState,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

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
# Data-layer validation checks (each maps to explicit DMI*/UDL* obligations)
# ---------------------------------------------------------------------------


class ModelTypedCheck(ValidationCheck):
    """UDL-03 / DMK-01 — the meta-model bears a non-empty ENG-004 type."""

    check_id = "metamodel-typed"
    severity = Severity.BLOCKING
    description = "Meta-model bears a non-empty ENG-004 type_tag (UDL-03 / DMK-01)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("meta-model is untyped (UDL-03 / DMK-01)")
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
    """UDL-04/05 / DMK-01 / C1 — the object is identified (ENG-001) and object-borne."""

    check_id = "metamodel-identified"
    severity = Severity.BLOCKING
    description = "Meta-model bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-METAMODEL-"):
            return self._failed("meta-model has no ENG-001 identity (UDL-04)", id=subject.target_id)
        return self._passed(model_id=subject.target_id)


class ModelValueFidelityCheck(ValidationCheck):
    """UDL-06 (transitive) / C3 — the object's representation is ENG-003 value-faithful."""

    check_id = "data-value-fidelity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Meta-model representation is content-addressed via ENG-003 encoding (UDL-06)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("meta-model representation is not value-faithful (UDL-06)")
        return self._passed(value_digest=digest)


class MetaClassClosureCheck(ValidationCheck):
    """V1 / DMI-01 — the members are exactly the ten meta-classes DMC-01…10 (closure)."""

    check_id = "meta-class-single"  # shared id — reused by the DMC-01 CCE gate suite (CC-1)
    severity = Severity.BLOCKING
    description = "Meta-model closes over exactly the ten meta-classes DMC-01…10 (DMI-01)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        present = set(subject.meta_classes)
        if present != _META_CLASSES or len(subject.meta_classes) != len(_META_CLASSES):
            return self._failed(
                "meta-class set is not exactly DMC-01…10 (DMI-01)",
                present=sorted(present),
            )
        if not subject.declares_closure:
            return self._failed("meta-model does not declare closure (DMI-01)")
        return self._passed(meta_classes=list(subject.meta_classes))


class MetaRelationshipClosureCheck(ValidationCheck):
    """V2 / DMI-02 — the edges are exactly the twelve meta-relationships DMR-01…12."""

    check_id = "meta-relationships-closed"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Meta-model closes over exactly the twelve meta-relationships DMR-01…12 (DMI-02)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        present = set(subject.meta_relationships)
        outside = present - _META_RELATIONSHIPS
        if outside:
            return self._failed("relationships outside DMR-01…12 (DMI-02)", outside=sorted(outside))
        if present != _META_RELATIONSHIPS or len(subject.meta_relationships) != len(
            _META_RELATIONSHIPS
        ):
            return self._failed("relationship set is not exactly DMR-01…12 (DMI-02)")
        if not subject.declares_relationship_closure:
            return self._failed("meta-model does not declare relationship closure (DMI-02)")
        return self._passed(meta_relationships=list(subject.meta_relationships))


class MetaModelTotalityCheck(ValidationCheck):
    """DMI-03 — members model exactly DOE-01…10 and edges model exactly DOR-01…12."""

    check_id = "metamodel-totality"
    severity = Severity.BLOCKING
    description = "Members model exactly DOE-01…10; edges model exactly DOR-01…12 (DMI-03)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if set(subject.modelled_entities) != _ONTOLOGY_ENTITIES or len(
            subject.modelled_entities
        ) != len(_ONTOLOGY_ENTITIES):
            return self._failed("ontology entity coverage is not total (DMI-03)")
        if set(subject.modelled_relationships) != _ONTOLOGY_RELATIONSHIPS or len(
            subject.modelled_relationships
        ) != len(_ONTOLOGY_RELATIONSHIPS):
            return self._failed("ontology relationship coverage is not total (DMI-03)")
        if not subject.is_total:
            return self._failed("meta-model is not total (DMI-03)")
        return self._passed(entities=len(subject.modelled_entities))


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMI-04 / DMK-03 — the founding meta-graph (DMR-01/04) is acyclic (a DAG)."""

    check_id = "founding-acyclic"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The meta-model founding graph (DMR-01/04) is acyclic (DMI-04 / DMK-03)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding meta-graph is not acyclic (DMI-04)")
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
    """V3 — applicable meta-constraints (DMK-01 typed/identified, DMK-03 acyclic, DMK-08)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DMK-01 (typed+identified), DMK-03 (founding acyclic), DMK-08 (no-tech) (V3)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # DMK-01 typed
            and subject.name.strip()  # named
            and subject.target_id  # DMK-01 identified
            and subject.declares_closure  # DMI-01
            and subject.declares_relationship_closure  # DMI-02
            and subject.is_total  # DMI-03
            and subject.founding_acyclic  # DMK-03 acyclic
            and subject.map_resolves  # §9 edges resolve
            and not subject.confers_authority  # DMK-08 no authority
            and not subject.names_technology  # DMK-08 no technology
        )
        if not ok:
            return self._failed("DMK-01/03/08 (DMI-01/02/03/04) not satisfied (V3)")
        return self._passed(constraints=["DMK-01", "DMK-03", "DMK-08"])


class ModelValidStateCheck(ValidationCheck):
    """V5 / UDL-12 — the object holds a valid DOS-01…05 lifecycle state."""

    check_id = "metamodel-valid"
    severity = Severity.BLOCKING
    description = "Meta-model holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if subject.model_state not in _STATE_VALUES:
            return self._failed("invalid meta-model state (V5)", state=subject.model_state)
        return self._passed(state=subject.model_state)


class ModelVersionedCheck(ValidationCheck):
    """UDL-12 — the object records an explicit version (additive/append-only)."""

    check_id = "metamodel-versioned"
    severity = Severity.BLOCKING
    description = "Meta-model object records an explicit version (UDL-12)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("meta-model object records no version (UDL-12)")
        return self._passed(version=subject.version)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """DMI-05 / UDL-02 — EL-1 + the ten CERTIFIED units + RL-F2/PL-F2 reused by reference."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + ten CERTIFIED units + RL-F2/PL-F2 referenced, redefined nowhere (DMI-05)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/RL-F2/PL-F2/DMC primitive was redefined (DMI-05)")
        if not subject.substrate_refs:
            return self._failed("no substrate reference recorded (DMI-05)")
        if not subject.members_certified:
            return self._failed("a member realization was owned, not referenced (DMI-05)")
        if not subject.reuses_by_reference:
            return self._failed("reuse-by-reference not satisfied (DMI-05)")
        return self._passed(substrate=list(subject.substrate_refs))


class ModelIndependenceCheck(ValidationCheck):
    """DMI-06 / UDL-15 / DMK-08 / C6 — the object names no technology (material)."""

    check_id = "metamodel-independence"
    severity = Severity.BLOCKING
    description = "No data/storage/relationship technology named (DMI-06 / UDL-15 / DMK-08)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.selects_technology:
            return self._failed("a data/storage/relationship technology was named (DMI-06)")
        return self._passed()


class NonProjectionCheck(ValidationCheck):
    """DMI-07 — model coverage is never roadmap/implementation/operational completion."""

    check_id = "metamodel-non-projection"
    severity = Severity.BLOCKING
    description = "Model coverage is never roadmap/operational completion (DMI-07 / STATUS-001 §2)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not subject.non_projection:
            return self._failed("meta-model projects model coverage as completion (DMI-07)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """DMI-06 / UDL-15 / C7 — the object confers no authority, holds no secret, selects no tech."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Meta-model confers no authority, embeds no secret, selects no tech (UDL-15)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("meta-model confers authority (UDL-15 / DMI-06)")
        if subject.embeds_secret:
            return self._failed("meta-model embeds a secret (UDL-15 / RR-07)")
        if subject.selects_technology:
            return self._failed("meta-model selects technology (UDL-15 / DMK-08)")
        if not subject.non_constitutive:
            return self._failed("meta-model is constitutive (DMI-06)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§10 / AC — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at the UDM and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: ModelValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the model-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def model_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
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
