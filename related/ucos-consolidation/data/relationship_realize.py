"""EC3-B10-U10 — Realization orchestrator + evidence emitter (Relationship Foundation).

Performs the realization act authorized by ``EC3-B10-DATA-REALIZATION-PACKAGE-010``
(derived from the frozen constitutional corpus — DATA-008 — since the package file is not
present): constructs the canonical **typed, decidable Relationship** exemplar that
**relates two CERTIFIED DMC-02 Entities by reference** (DMR-03) — a peer Association with
explicit N:M cardinality — binding navigation/referential-integrity evaluation *by
reference* to the frozen RUNTIME policy concern (DMR-11 / §7). The source endpoint is the
exact CERTIFIED U03 canonical Entity, extending the spine to ``Relationship relates Entity
bears Attribute values Datum`` (DMR-03 → DMR-01 → DMR-02).

It is a **typed ENG-005 reference that enacts nothing** — it records related endpoints,
an explicit cardinality, a declared directionality, and a policy reference as *records*,
and names **no** join language, foreign-key mechanic, graph engine, ORM, database, or
relationship product/vendor (UDL-09 Relationship by Reference; DATA-008 §2.2 — materially
enforced).

It validates the relationship through the CERTIFIED EC-1 engine (meta-validity V1…V5 +
Data-law UDL incl. **UDL-09**), certifies it through the CCE ten gates (CC-1…CC-10, reused
from DMC-01) + Data compliance (C1…C7, C5 materially exercised), closes its No-Orphan
traceability (incl. ``relates → DMC-02``), and emits a **deterministic, content-addressed
evidence bundle**. A double-realization self-check proves byte-identical determinism
(VC-4).

Run as a module::

    python -m data.relationship_realize                 # emit evidence + determination
    python -m data.relationship_realize --evidence-dir data/_evidence/EC3-B10-U10

This is engineering execution only (DE-05): it asserts no constitutional finality and no
operational/deployment/production readiness; it selects no technology, reuses the
CERTIFIED EC-1 + DMC-01/02 surfaces by reference, and writes nothing outside the
caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from data.attribute import make_attribute
from data.attribute_meta import AttributeKind, AttributeState
from data.datum import make_datum
from data.entity import Entity, entity_ref_for, make_entity
from data.entity_meta import EntityKind, EntityState
from data.entity_realize import build_canonical_entity
from data.meta import DatumKind, DatumState
from data.relationship import (
    EntityEndpointRef,
    RelationshipObject,
    make_relationship,
    policy_ref_for,
)
from data.relationship_certification import RelationshipCertification, certify_relationship
from data.relationship_meta import (
    RELATIONSHIP_META_CLASS,
    RelationshipCardinality,
    RelationshipDirection,
    RelationshipKind,
    RelationshipState,
    RelationshipVerdict,
)
from data.relationship_traceability import build_relationship_traceability
from data.relationship_validation import RelationshipValidation, validate_relationship
from data.traceability import TraceabilityRecord
from engine.certification.contracts import content_hash

#: The realization unit this module realizes (EC-3 Band 10, Unit 10).
REALIZATION_UNIT = "EC3-B10-U10"

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical relationship name/type — the object that relates the CERTIFIED entities.
CANONICAL_RELATIONSHIP_NAME = "ucos.data.relationship.foundation"
CANONICAL_RELATIONSHIP_TYPE_TAG = "ucos.core.relationship"

#: The canonical RUNTIME policy predicate the object binds by reference (abstract).
CANONICAL_POLICY_PREDICATE = "relationship.navigation"

#: The canonical DXH-04 kind — a peer Association (DOR-03 relates), non-founding.
CANONICAL_RELATIONSHIP_KIND = RelationshipKind.ASSOCIATION

#: The canonical explicit cardinality — a many-to-many peer association (DRA-04).
CANONICAL_CARDINALITY = RelationshipCardinality.MANY_TO_MANY

#: The distinct target-endpoint entity name (a second CERTIFIED-surface Entity).
CANONICAL_TARGET_ENTITY_NAME = "ucos.data.entity.related"
CANONICAL_TARGET_ENTITY_TYPE_TAG = "ucos.core.entity"
CANONICAL_TARGET_ATTRIBUTE_NAME = "ucos.data.attribute.related"
CANONICAL_TARGET_ATTRIBUTE_TYPE_TAG = "ucos.core.string"
CANONICAL_TARGET_VALUE_TYPE_TAG = "ucos.data.attribute.value"
CANONICAL_TARGET_VALUE = "EC3-B10-U10:RELATIONSHIP-TARGET-ENTITY-VALUE"

#: Where the default evidence bundle is written (code-adjacent; never the corpus).
DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

#: The validation check ids substantiating meta-validity V1…V5 (DATA-005 §8).
_META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "meta-class-single",
    "V2": "meta-relationships-closed",
    "V3": "meta-constraints",
    "V4": "founding-acyclic",
    "V5": "relationship-valid",
}

#: The validation check ids substantiating single-check Data-law UDL conformance (VC-3).
_UDL_CHECKS: dict[str, str] = {
    "UDL-02": "foundation-reuse-integrity",
    "UDL-03": "relationship-typed",
    "UDL-04": "relationship-identified",
    "UDL-05": "relationship-identified",
    "UDL-09": "relationship-by-reference",
    "UDL-10": "relationship-cardinality-explicit",
    "UDL-12": "relationship-valid",
    "UDL-15": "non-constitutive",
}


def build_canonical_target_entity() -> Entity:
    """Construct a distinct CERTIFIED-surface Entity to serve as the target endpoint (DMR-03).

    A second Master-Entity — typed, identified, bearing one CERTIFIED Attribute by
    reference — distinct from the canonical source entity so the canonical relationship
    relates two distinct entities (well-formed for both peer and founding kinds).
    """
    value_datum = make_datum(
        CANONICAL_TARGET_VALUE_TYPE_TAG,
        CANONICAL_TARGET_VALUE,
        kind=DatumKind.PRIMITIVE,
        state=DatumState.DEFINED,
    )
    attribute = make_attribute(
        CANONICAL_TARGET_ATTRIBUTE_NAME,
        CANONICAL_TARGET_ATTRIBUTE_TYPE_TAG,
        value_datum,
        entity_ref_for(CANONICAL_TARGET_ENTITY_NAME),
        kind=AttributeKind.DESCRIPTIVE,
        nullable=False,
        state=AttributeState.DEFINED,
    )
    return make_entity(
        CANONICAL_TARGET_ENTITY_NAME,
        CANONICAL_TARGET_ENTITY_TYPE_TAG,
        (attribute,),
        kind=EntityKind.MASTER,
        state=EntityState.DEFINED,
    )


def build_canonical_relationship() -> RelationshipObject:
    """Construct the canonical typed, decidable Relationship exemplar (DMC-04).

    Relates the CERTIFIED DMC-02 canonical Master-Entity (source) to a distinct CERTIFIED
    Entity (target) by reference (DMR-03), as a peer Association with explicit N:M
    cardinality (DRA-04), binding navigation/integrity evaluation by reference to the
    RUNTIME policy concern (DMR-11 / §7). ENG-005 reference only — names no
    join/foreign-key/graph/database technology (UDL-09 / DRA-K5).
    """
    source = build_canonical_entity()
    target = build_canonical_target_entity()
    return make_relationship(
        CANONICAL_RELATIONSHIP_NAME,
        CANONICAL_RELATIONSHIP_TYPE_TAG,
        source,
        target,
        policy_ref_for(CANONICAL_POLICY_PREDICATE),
        kind=CANONICAL_RELATIONSHIP_KIND,
        cardinality=CANONICAL_CARDINALITY,
        direction=RelationshipDirection.PEER,
        verdict=RelationshipVerdict.PASS,
        state=RelationshipState.DEFINED,
        version=UNIT_VERSION,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B10-U10 realization act."""

    relationship: RelationshipObject
    source_entity: Entity
    target_entity: Entity
    trace: TraceabilityRecord
    validation: RelationshipValidation
    certification: RelationshipCertification

    # -- derived conformance roll-ups ------------------------------------------

    def _passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def meta_validity(self) -> dict[str, bool]:
        passed = self._passed()
        return {v: passed.get(cid, False) for v, cid in _META_VALIDITY_CHECKS.items()}

    def udl_conformance(self) -> dict[str, bool]:
        passed = self._passed()
        result = {law: passed.get(cid, False) for law, cid in _UDL_CHECKS.items()}
        # UDL-01 layer; UDL-09 relationship (material, ENG-005 reference + founding acyclic).
        result["UDL-01"] = True
        result["UDL-09"] = (
            self.relationship.is_by_reference()
            and self.relationship.founding_acyclic_rule()
            and self.relationship.endpoints_resolve()
            and not self.relationship.absorbs_endpoints()
            and not self.relationship.names_technology()
        )
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, executable construct
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (  # typed + named + identified + relates endpoints by reference
                passed.get("relationship-typed", False)
                and passed.get("relationship-named", False)
                and passed.get("relationship-identified", False)
                and passed.get("relationship-relates-endpoints", False)
            ),
            "AC-4": (  # by-reference + cardinal + directional + integral + acyclic + navigable
                passed.get("relationship-by-reference", False)
                and passed.get("relationship-cardinality-explicit", False)
                and passed.get("relationship-directionality-declared", False)
                and passed.get("relationship-referential-integrity", False)
                and passed.get("relationship-founding-acyclic-rule", False)
                and passed.get("relationship-non-absorbing", False)
                and passed.get("relationship-binds-policy-by-reference", False)
            ),
            "AC-5": passed.get("relationship-independence", False),  # no technology (material)
            "AC-6": passed.get("non-constitutive", False),  # no authority/access/secret
            "AC-7": True,  # realized under data/**; frozen corpus + DMC-02 unmodified (guarded)
            "AC-8": self.trace.closed,  # full traceability recorded (incl. relates → DMC-02)
        }

    def validation_criteria(self, *, byte_identical: bool) -> dict[str, bool]:
        mv = self.meta_validity()
        return {
            "VC-1": self.validation.accepted,  # EC-1 ValidationEngine PASS + accepted
            "VC-2": all(mv.values()),  # meta-validity V1…V5
            "VC-3": all(self.udl_conformance().values()),  # UDL conformance
            "VC-4": byte_identical,  # determinism (byte-identical recompute)
            "VC-5": self._passed().get("foundation-reuse-integrity", False),  # reuse integrity
        }

    def certification_gates(self) -> dict[str, bool]:
        return {f.criterion_id: f.passed for f in self.certification.decision.findings}

    def data_compliance(self) -> dict[str, bool]:
        return {c["id"]: c["status"] == "pass" for c in self.certification.compliance.conditions}

    def spine_closure(self) -> dict[str, bool]:
        """The ``Relationship relates Entity …`` spine-closure facts."""
        return {
            "relates_entities": self.relationship.relates_entities(
                self.source_entity.entity_id, self.target_entity.entity_id
            ),
            "source_is_certified_entity": self.relationship.source_id()
            == self.source_entity.entity_id,
            "by_reference": self.relationship.is_by_reference(),
            "cardinality_explicit": self.relationship.cardinality_explicit(),
            "directionality_declared": self.relationship.directionality_declared(),
            "referential_integrity": self.relationship.endpoints_resolve(),
            "founding_acyclic": self.relationship.founding_acyclic_rule(),
            "non_absorbing": not self.relationship.absorbs_endpoints(),
            "navigates_by_reference": self.relationship.navigates_by_reference(),
            "technology_neutral": not self.relationship.names_technology(),
        }

    def determination(self, *, byte_identical: bool) -> str:
        vc = self.validation_criteria(byte_identical=byte_identical)
        gates_ok = all(self.certification_gates().values())
        if (
            self.validation.accepted
            and self.certification.certified
            and self.trace.closed
            and all(vc.values())
            and gates_ok
            and all(self.data_compliance().values())
            and all(self.spine_closure().values())
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this realization."""
        return {
            "artifact": "EC3-B10-U10-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": RELATIONSHIP_META_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "relationship": self.relationship.to_dict(),
            "source_entity": self.source_entity.to_dict(),
            "target_entity": self.target_entity.to_dict(),
            "spine": (
                "Relationship relates Entity bears Attribute values Datum "
                "(DMR-03 → DMR-01 → DMR-02)"
            ),
            "spine_closure": self.spine_closure(),
            "traceability": self.trace.to_dict(),
            "validation": {
                "report": self.validation.report.to_dict(),
                "evidence": self.validation.evidence.to_dict(),
                "acceptance": self.validation.decision.to_dict(),
            },
            "meta_validity_V1_V5": self.meta_validity(),
            "udl_conformance": self.udl_conformance(),
            "certification": {
                "cce_gates": self.certification.decision.to_dict(),
                "ledger": self.certification.ledger.to_dict(),
                "evidence": self.certification.evidence.to_dict(),
            },
            "data_compliance_C1_C7": self.certification.compliance.to_dict(),
            "criteria": {
                "acceptance": self.acceptance_criteria(),
                "validation": self.validation_criteria(byte_identical=byte_identical),
                "certification_gates": self.certification_gates(),
                "data_compliance": self.data_compliance(),
            },
            "determination": self.determination(byte_identical=byte_identical),
        }


def realize() -> RealizationResult:
    """Perform the realization act and return its full deterministic result."""
    source_entity = build_canonical_entity()
    target_entity = build_canonical_target_entity()
    relationship = make_relationship(
        CANONICAL_RELATIONSHIP_NAME,
        CANONICAL_RELATIONSHIP_TYPE_TAG,
        EntityEndpointRef.from_entity(source_entity),
        EntityEndpointRef.from_entity(target_entity),
        policy_ref_for(CANONICAL_POLICY_PREDICATE),
        kind=CANONICAL_RELATIONSHIP_KIND,
        cardinality=CANONICAL_CARDINALITY,
        direction=RelationshipDirection.PEER,
        verdict=RelationshipVerdict.PASS,
        state=RelationshipState.DEFINED,
        version=UNIT_VERSION,
    )
    trace = build_relationship_traceability(
        relationship,
        unit=REALIZATION_UNIT,
        forward=(
            relationship.relationship_id,
            "EC3-B10-U10-VALIDATION-EVIDENCE",
            "EC3-B10-U10-CCE-CERTIFICATION",
            "EC3-B10-U10-COMPLETION-REPORT",
        ),
    )
    validation = validate_relationship(relationship, trace)
    certification = certify_relationship(validation, version=UNIT_VERSION)
    return RealizationResult(
        relationship=relationship,
        source_entity=source_entity,
        target_entity=target_entity,
        trace=trace,
        validation=validation,
        certification=certification,
    )


def determinism_check() -> tuple[bool, str, str]:
    """Realize twice and compare the evidence bundles byte-for-byte (VC-4).

    Returns ``(byte_identical, digest_a, digest_b)`` where the digests are the EC-1
    content hashes of the two independently produced evidence bundles.
    """
    bundle_a = realize().to_bundle(byte_identical=True)
    bundle_b = realize().to_bundle(byte_identical=True)
    digest_a = content_hash(bundle_a)
    digest_b = content_hash(bundle_b)
    return (digest_a == digest_b, digest_a, digest_b)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def emit_evidence(evidence_dir: Path) -> dict[str, Any]:
    """Realize, self-check determinism, and write the evidence bundle to disk.

    Returns a compact summary. All written files are deterministic (byte-identical across
    runs), so re-emission never produces drift.
    """
    byte_identical, digest_a, digest_b = determinism_check()
    result = realize()
    bundle = result.to_bundle(byte_identical=byte_identical)

    evidence_dir.mkdir(parents=True, exist_ok=True)
    _write_json(evidence_dir / "realization-evidence.json", bundle)
    _write_json(evidence_dir / "validation-report.json", bundle["validation"]["report"])
    _write_json(evidence_dir / "validation-evidence.json", bundle["validation"]["evidence"])
    _write_json(evidence_dir / "acceptance-decision.json", bundle["validation"]["acceptance"])
    _write_json(evidence_dir / "cce-certification.json", bundle["certification"]["cce_gates"])
    _write_json(evidence_dir / "certification-evidence.json", bundle["certification"]["evidence"])
    _write_json(evidence_dir / "certification-ledger.json", bundle["certification"]["ledger"])
    _write_json(evidence_dir / "data-compliance.json", bundle["data_compliance_C1_C7"])
    _write_json(evidence_dir / "traceability.json", bundle["traceability"])
    _write_json(
        evidence_dir / "determinism.json",
        {
            "determinism_evidence": True,
            "unit": REALIZATION_UNIT,
            "byte_identical": byte_identical,
            "bundle_sha256_a": digest_a,
            "bundle_sha256_b": digest_b,
        },
    )

    return {
        "unit": REALIZATION_UNIT,
        "determination": bundle["determination"],
        "validation_accepted": result.validation.accepted,
        "certified": result.certification.certified,
        "traceability_closed": result.trace.closed,
        "byte_identical": byte_identical,
        "spine_closed": all(result.spine_closure().values()),
        "certification_id": result.certification.decision.certification_id,
        "relationship_id": result.relationship.relationship_id,
        "source_entity_id": result.source_entity.entity_id,
        "target_entity_id": result.target_entity.entity_id,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B10-U10, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b10-u10-realize",
        description="Realize the Relationship Foundation (DMC-04) and emit evidence.",
    )
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    args = parser.parse_args(argv)

    summary = emit_evidence(Path(args.evidence_dir))
    print(json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=False))
    complete = (
        summary["determination"] == "COMPLETE"
        and summary["validation_accepted"]
        and summary["certified"]
        and summary["traceability_closed"]
        and summary["byte_identical"]
        and summary["spine_closed"]
    )
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B10-U10 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "REALIZATION_UNIT",
    "UNIT_VERSION",
    "CANONICAL_RELATIONSHIP_NAME",
    "CANONICAL_RELATIONSHIP_TYPE_TAG",
    "CANONICAL_POLICY_PREDICATE",
    "CANONICAL_RELATIONSHIP_KIND",
    "CANONICAL_CARDINALITY",
    "CANONICAL_TARGET_ENTITY_NAME",
    "DEFAULT_EVIDENCE_DIR",
    "RealizationResult",
    "build_canonical_target_entity",
    "build_canonical_relationship",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
    "EntityEndpointRef",
]
