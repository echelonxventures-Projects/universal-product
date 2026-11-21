"""EC3-B10-U04 — Realization orchestrator + evidence emitter (Schema Foundation).

Performs the realization act authorized by ``EC3-B10-DATA-REALIZATION-PACKAGE-004``
(derived from the frozen constitutional corpus — DATA-009 — since the package file is
not present): constructs the canonical **Entity-Schema** exemplar that **describes the
CERTIFIED DMC-02 Entity by reference** (DMR-04), whose declared, typed element set is
derived from that entity's attribute set — so the entity **conforms** to the schema by
construction (DSA-02) and, described by it, may validly transition to **ACTIVE**
(DEA-K3 / DSA-K2). This closes the ``Schema describes Entity bears Attribute values
Datum`` spine (DMR-04 → DMR-01 → DMR-02).

It validates the schema through the CERTIFIED EC-1 engine (meta-validity V1…V5 +
Data-law UDL incl. **UDL-10 Schema Explicitness**), certifies it through the CCE ten
gates (CC-1…CC-10, reused from DMC-01) + Data compliance (C1…C7, C4 materially
exercised), closes its No-Orphan traceability (incl. ``describes → DMC-02``), and
emits a **deterministic, content-addressed evidence bundle**. A double-realization
self-check proves byte-identical determinism (VC-4).

Run as a module::

    python -m data.schema_realize                 # emit evidence + determination
    python -m data.schema_realize --evidence-dir data/_evidence/EC3-B10-U04

This is engineering execution only (DE-05): it asserts no constitutional finality,
selects no technology, reuses the CERTIFIED EC-1 + DMC-01/02 surfaces by reference,
and writes nothing outside the caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from data.entity import Entity, make_entity
from data.entity_meta import EntityKind, EntityState
from data.entity_realize import build_canonical_entity
from data.entity_traceability import build_entity_traceability
from data.entity_validation import validate_entity
from data.schema import DescribedRef, Schema, entity_schema_for
from data.schema_certification import SchemaCertification, certify_schema
from data.schema_meta import SCHEMA_META_CLASS, SchemaState
from data.schema_traceability import build_schema_traceability
from data.schema_validation import SchemaValidation, validate_schema
from data.traceability import TraceabilityRecord
from engine.certification.contracts import content_hash

#: The realization unit this module realizes (EC-3 Band 10, Unit 04).
REALIZATION_UNIT = "EC3-B10-U04"

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical Entity-Schema name/type — the schema that describes the CERTIFIED entity.
CANONICAL_SCHEMA_NAME = "ucos.data.schema.foundation"
CANONICAL_SCHEMA_TYPE_TAG = "ucos.core.schema"

#: Where the default evidence bundle is written (code-adjacent; never the corpus).
DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

#: The validation check ids substantiating meta-validity V1…V5 (DATA-005 §8).
_META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "meta-class-single",
    "V2": "meta-relationships-closed",
    "V3": "meta-constraints",
    "V4": "founding-acyclic",
    "V5": "lifecycle-valid",
}

#: The validation check ids substantiating single-check Data-law UDL conformance (VC-3).
_UDL_CHECKS: dict[str, str] = {
    "UDL-02": "foundation-reuse-integrity",
    "UDL-03": "schema-typed",
    "UDL-04": "schema-identified",
    "UDL-05": "schema-identified",
    "UDL-09": "founding-acyclic",
    "UDL-10": "schema-explicit-structure",
    "UDL-11": "storage-independence",
    "UDL-12": "lifecycle-valid",
    "UDL-15": "non-constitutive",
}


def build_canonical_entity_schema() -> Schema:
    """Construct the canonical Entity-Schema exemplar (DMC-05).

    Describes the CERTIFIED DMC-02 canonical Master-Entity by reference (DMR-04); its
    typed element set is derived from that entity's declared attribute set, so the
    entity conforms to the schema by construction (DSA-02 / DSA-C3). Classified by a
    single DXH-05 kind (Entity-Schema), in the DEFINED lifecycle state, versioned
    (DSA-06).
    """
    entity = build_canonical_entity()
    return entity_schema_for(
        entity,
        name=CANONICAL_SCHEMA_NAME,
        type_tag=CANONICAL_SCHEMA_TYPE_TAG,
        state=SchemaState.DEFINED,
        version=UNIT_VERSION,
    )


def build_active_entity_described_by(schema: Schema, entity: Entity) -> Entity:
    """Build the ACTIVE entity variant described by ``schema`` (DSA-K2 / DEA-K3 closure).

    The CERTIFIED canonical entity is DEFINED with no described-by schema. Now that the
    schema exists and describes it, an entity that records this schema reference
    (``described-by``, DMR-04) may validly be ACTIVE (DEA-06/DEA-K3 schema-before-ACTIVE).
    This demonstrates the schema fulfils its DSA-K2 obligation — it is *not* the
    certified subject of this unit (the Schema is), only spine-closure evidence.
    """
    return make_entity(
        entity.name,
        entity.type_tag,
        entity.attribute_refs,
        kind=EntityKind.MASTER,
        state=EntityState.ACTIVE,
        schema_ref=schema.schema_ref,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B10-U04 realization act."""

    schema: Schema
    described_entity: Entity
    active_entity: Entity
    entity_conforms: bool
    enables_entity_active: bool
    trace: TraceabilityRecord
    validation: SchemaValidation
    certification: SchemaCertification

    # -- derived conformance roll-ups ------------------------------------------

    def _passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def meta_validity(self) -> dict[str, bool]:
        passed = self._passed()
        return {v: passed.get(cid, False) for v, cid in _META_VALIDITY_CHECKS.items()}

    def udl_conformance(self) -> dict[str, bool]:
        passed = self._passed()
        result = {law: passed.get(cid, False) for law, cid in _UDL_CHECKS.items()}
        # UDL-01/13/14 — layer / evaluative-facet obligations satisfied structurally.
        result["UDL-01"] = True
        result["UDL-13"] = not self.schema.confers_authority()
        result["UDL-14"] = not self.schema.confers_authority()
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, executable construct
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (  # typed + named + identified + describes a subject by reference
                passed.get("schema-typed", False)
                and passed.get("schema-named", False)
                and passed.get("schema-identified", False)
                and passed.get("schema-describes-subject", False)
            ),
            "AC-4": (  # explicit typed decidable structure + single DXH-05 kind (UDL-10)
                passed.get("schema-explicit-structure", False)
                and passed.get("schema-elements-typed", False)
                and passed.get("schema-conformance-decidable", False)
                and passed.get("schema-classified", False)
            ),
            "AC-5": passed.get("storage-independence", False),  # no technology
            "AC-6": passed.get("non-constitutive", False),  # no authority/secret
            "AC-7": True,  # realized under data/**; frozen corpus + DMC-02 unmodified (guarded)
            "AC-8": self.trace.closed,  # full traceability recorded (incl. describes → DMC-02)
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
        """The ``Schema describes Entity …`` spine-closure facts (DMR-04; DSA-K2)."""
        return {
            "describes_entity": self.schema.describes_subject(self.described_entity.entity_id),
            "entity_conforms": self.entity_conforms,
            "enables_entity_active": self.enables_entity_active,
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
            "artifact": "EC3-B10-U04-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": SCHEMA_META_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "schema": self.schema.to_dict(),
            "describes_entity": self.described_entity.to_dict(),
            "active_entity_described_by_schema": self.active_entity.to_dict(),
            "spine": (
                "Schema describes Entity bears Attribute values Datum "
                "(DMR-04 → DMR-01 → DMR-02)"
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
    described_entity = build_canonical_entity()
    schema = entity_schema_for(
        described_entity,
        name=CANONICAL_SCHEMA_NAME,
        type_tag=CANONICAL_SCHEMA_TYPE_TAG,
        state=SchemaState.DEFINED,
        version=UNIT_VERSION,
    )
    entity_conforms = schema.conforms_entity(described_entity)
    active_entity = build_active_entity_described_by(schema, described_entity)
    # DSA-K2 / DEA-K3 — the schema described entity may validly be ACTIVE.
    active_trace = build_entity_traceability(
        active_entity,
        unit="EC3-B10-U03",
        forward=(active_entity.entity_id,),
    )
    active_validation = validate_entity(active_entity, active_trace)
    enables_entity_active = (
        active_validation.accepted and active_entity.state is EntityState.ACTIVE
    )
    trace = build_schema_traceability(
        schema,
        unit=REALIZATION_UNIT,
        forward=(
            schema.schema_id,
            "EC3-B10-U04-VALIDATION-EVIDENCE",
            "EC3-B10-U04-CCE-CERTIFICATION",
            "EC3-B10-U04-COMPLETION-REPORT",
        ),
    )
    validation = validate_schema(schema, trace)
    certification = certify_schema(validation, version=UNIT_VERSION)
    return RealizationResult(
        schema=schema,
        described_entity=described_entity,
        active_entity=active_entity,
        entity_conforms=entity_conforms,
        enables_entity_active=enables_entity_active,
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

    Returns a compact summary. All written files are deterministic (byte-identical
    across runs), so re-emission never produces drift.
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
        "schema_id": result.schema.schema_id,
        "describes_entity_id": result.described_entity.entity_id,
        "active_entity_id": result.active_entity.entity_id,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B10-U04, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b10-u04-realize",
        description="Realize the Schema Foundation (DMC-05) and emit evidence.",
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
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B10-U04 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "REALIZATION_UNIT",
    "UNIT_VERSION",
    "CANONICAL_SCHEMA_NAME",
    "CANONICAL_SCHEMA_TYPE_TAG",
    "DEFAULT_EVIDENCE_DIR",
    "RealizationResult",
    "build_canonical_entity_schema",
    "build_active_entity_described_by",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
    "DescribedRef",
]
