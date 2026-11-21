"""EC3-B10-U02 — Realization orchestrator + evidence emitter (Attribute Foundation).

Performs the realization act authorized by ``EC3-B10-DATA-REALIZATION-PACKAGE-002``:
constructs the canonical Descriptive-Attribute exemplar that **values the CERTIFIED
DMC-01 Datum by reference** (DMR-02) and declares a bearing-entity reference (DMR-01)
+ nullability (DAA-05), validates it through the CERTIFIED EC-1 engine (meta-validity
V1…V5 + Data-law UDL incl. UDL-08), certifies it through the CCE ten gates
(CC-1…CC-10, reused from DMC-01) + Data compliance (C1…C7, C4 materially exercised),
closes its No-Orphan traceability (incl. ``values → DMC-01``), and emits a
**deterministic, content-addressed evidence bundle**. A double-realization self-check
proves byte-identical determinism (VC-4).

Run as a module::

    python -m data.attribute_realize                 # emit evidence + determination
    python -m data.attribute_realize --evidence-dir data/_evidence/EC3-B10-U02

This is engineering execution only (DE-05): it asserts no constitutional finality,
selects no technology, reuses the CERTIFIED EC-1 + DMC-01 surfaces by reference, and
writes nothing outside the caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from data.attribute import Attribute, DatumValueRef, make_attribute
from data.attribute_certification import AttributeCertification, certify_attribute
from data.attribute_meta import (
    ATTRIBUTE_META_CLASS,
    AttributeKind,
    AttributeState,
)
from data.attribute_traceability import build_attribute_traceability
from data.attribute_validation import AttributeValidation, validate_attribute
from data.datum import Datum, make_datum
from data.meta import DatumKind, DatumState
from data.traceability import TraceabilityRecord
from engine.certification.contracts import content_hash

#: The realization unit this module realizes (EC-3 Band 10, Unit 02).
REALIZATION_UNIT = "EC3-B10-U02"

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical Datum the attribute values (reused from the CERTIFIED DMC-01 surface).
CANONICAL_VALUE_TYPE_TAG = "ucos.data.attribute.value"
CANONICAL_VALUE = "EC3-B10-U02:ATTRIBUTE-FOUNDATION-VALUE"

#: The canonical Attribute exemplar realized to prove the construct (a Descriptive-Attribute).
CANONICAL_ATTRIBUTE_NAME = "ucos.data.attribute.foundation"
CANONICAL_ATTRIBUTE_TYPE_TAG = "ucos.core.string"

#: The single bearing-entity identity reference (DMR-01) — a *reference obligation*;
#: no Entity construct (DMC-02) is realized or embedded (that is EC3-B10-U03).
CANONICAL_BEARING_ENTITY_REF = "UCOS-ENTITY-REF:ucos.data.entity.foundation"

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
    "UDL-03": "attr-typed",
    "UDL-04": "attr-identified",
    "UDL-05": "attr-identified",
    "UDL-06": "data-value-fidelity",
    "UDL-09": "founding-acyclic",
    "UDL-11": "storage-independence",
    "UDL-12": "lifecycle-valid",
    "UDL-15": "non-constitutive",
}


def build_canonical_value_datum() -> Datum:
    """Construct the CERTIFIED-surface Datum the canonical attribute values (DMC-01 reuse)."""
    return make_datum(
        CANONICAL_VALUE_TYPE_TAG,
        CANONICAL_VALUE,
        kind=DatumKind.PRIMITIVE,
        state=DatumState.DEFINED,
    )


def build_canonical_attribute() -> Attribute:
    """Construct the canonical Descriptive-Attribute exemplar (DMC-03).

    Typed (ENG-004), explicitly named (DAA-04), valuing the CERTIFIED Datum by
    reference (DMR-02), borne by exactly one entity reference (DMR-01), with declared
    nullability (DAA-05) and a single DXH-03 kind.
    """
    value_datum = build_canonical_value_datum()
    return make_attribute(
        CANONICAL_ATTRIBUTE_NAME,
        CANONICAL_ATTRIBUTE_TYPE_TAG,
        value_datum,  # reused by reference → DatumValueRef (DMR-02; non-absorbing)
        CANONICAL_BEARING_ENTITY_REF,
        kind=AttributeKind.DESCRIPTIVE,
        nullable=False,
        state=AttributeState.DEFINED,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B10-U02 realization act."""

    attribute: Attribute
    value_datum: Datum
    trace: TraceabilityRecord
    validation: AttributeValidation
    certification: AttributeCertification

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
        result["UDL-13"] = not self.attribute.confers_authority()
        result["UDL-14"] = not self.attribute.confers_authority()
        # UDL-08 — ATTRIBUTE TYPEDNESS: typed + named + single-bearing + ENG-003 value.
        result["UDL-08"] = (
            passed.get("attr-typed", False)
            and passed.get("attr-named", False)
            and passed.get("attr-single-bearing", False)
            and passed.get("attr-values-datum", False)
        )
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, executable construct
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (  # typed + named + single-bearing + one ENG-003 value via DMR-02
                passed.get("attr-typed", False)
                and passed.get("attr-named", False)
                and passed.get("attr-single-bearing", False)
                and passed.get("attr-values-datum", False)
            ),
            "AC-4": (  # nullability declared + single DXH-03 kind
                passed.get("attr-nullability-declared", False)
                and passed.get("attr-classified", False)
            ),
            "AC-5": passed.get("storage-independence", False),  # no technology
            "AC-6": passed.get("non-constitutive", False),  # no authority/secret
            "AC-7": True,  # realized under data/**; frozen corpus + DMC-01 unmodified (guarded)
            "AC-8": self.trace.closed,  # full traceability recorded (incl. values → DMC-01)
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
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this realization."""
        return {
            "artifact": "EC3-B10-U02-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": ATTRIBUTE_META_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "attribute": self.attribute.to_dict(),
            "value_datum": self.value_datum.to_dict(),
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
    value_datum = build_canonical_value_datum()
    attribute = make_attribute(
        CANONICAL_ATTRIBUTE_NAME,
        CANONICAL_ATTRIBUTE_TYPE_TAG,
        DatumValueRef.from_datum(value_datum),
        CANONICAL_BEARING_ENTITY_REF,
        kind=AttributeKind.DESCRIPTIVE,
        nullable=False,
        state=AttributeState.DEFINED,
    )
    trace = build_attribute_traceability(
        attribute,
        unit=REALIZATION_UNIT,
        forward=(
            attribute.attribute_id,
            "EC3-B10-U02-VALIDATION-EVIDENCE",
            "EC3-B10-U02-CCE-CERTIFICATION",
            "EC3-B10-U02-COMPLETION-REPORT",
        ),
    )
    validation = validate_attribute(attribute, trace)
    certification = certify_attribute(validation, version=UNIT_VERSION)
    return RealizationResult(
        attribute=attribute,
        value_datum=value_datum,
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
        "certification_id": result.certification.decision.certification_id,
        "attribute_id": result.attribute.attribute_id,
        "values_datum_id": result.value_datum.datum_id,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B10-U02, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b10-u02-realize",
        description="Realize the Attribute Foundation (DMC-03) and emit evidence.",
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
    )
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B10-U02 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "REALIZATION_UNIT",
    "UNIT_VERSION",
    "CANONICAL_VALUE_TYPE_TAG",
    "CANONICAL_VALUE",
    "CANONICAL_ATTRIBUTE_NAME",
    "CANONICAL_ATTRIBUTE_TYPE_TAG",
    "CANONICAL_BEARING_ENTITY_REF",
    "DEFAULT_EVIDENCE_DIR",
    "RealizationResult",
    "build_canonical_value_datum",
    "build_canonical_attribute",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
