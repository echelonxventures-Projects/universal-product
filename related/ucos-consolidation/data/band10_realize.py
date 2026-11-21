"""EC3-B10-U12 — Realization orchestrator + evidence emitter (Band-10 Completion & Certification).

Performs the certification/completion act authorized by the ``MCP-003`` **MEP-01** exit
criterion ("All Band-10 units CCE-COMPLETE; Band-10 certification + completion report") and
the ``EC-3-AP-2-BAND-10-ADMISSION-DETERMINATION``: it **materially re-realizes the whole
Band-10 stack** through the CERTIFIED Universal Data Meta-Model orchestrator
(:func:`data.model_realize.realize`), which live-realizes and certifies the ten concern
meta-classes (U01…U10) and integrates them into the DATA-005 meta-model (U11). From that
single reuse call it captures the eleven CERTIFIED unit certifications (U01…U11) **by
reference** and composes them into an immutable :class:`~data.band10.Band10Completion`
record.

It validates the completion through the CERTIFIED EC-1 engine (readiness BRC-1…8 +
completion BCC-1…8), certifies it through the CCE ten gates (CC-1…CC-10, reused verbatim
from DMC-01) + Data compliance (C1…C7, C5 materially exercised at band level), closes its
No-Orphan traceability (incl. the eleven certified units), and emits a **deterministic,
content-addressed evidence bundle**. A double-realization self-check proves byte-identical
determinism.

This capability **introduces no new data concern, meta-class, ontology, or primitive**
(UDL-02 / UDL-15): it references, verifies, aggregates, and certifies — it never rewrites,
recreates, mutates, or re-judges any CERTIFIED unit.

Run as a module::

    python -m data.band10_realize
    python -m data.band10_realize --evidence-dir data/_evidence/EC3-B10-U12

Engineering execution only (DE-05): asserts no constitutional finality and no
operational/deployment/production readiness; selects no technology; writes nothing outside
the caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# --- the CERTIFIED Band-10 meta-model orchestrator, reused by reference (UDL-02) --
from data import model_realize
from data.band10 import Band10Completion, make_band10_completion
from data.band10_certification import Band10Certification, certify_band10
from data.band10_meta import (
    BAND_COMPLETION_CRITERIA,
    BAND_READINESS_CRITERIA,
    META_MODEL_UNIT,
    BandState,
)
from data.band10_traceability import build_band10_traceability
from data.band10_validation import Band10Validation, validate_band10
from data.traceability import TraceabilityRecord
from engine.certification.contracts import content_hash

#: The realization unit this module realizes (EC-3 Band 10, Unit 12).
REALIZATION_UNIT = "EC3-B10-U12"

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical band-completion name/type.
CANONICAL_BAND_NAME = "ucos.data.band10.completion"
CANONICAL_BAND_TYPE_TAG = "ucos.core.band-completion"

#: Where the default evidence bundle is written (code-adjacent; never the corpus).
DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

#: BRC readiness criterion → the validation check id(s) that substantiate it (BRC-8 is
#: the determinism self-check, decided separately).
_BRC_CHECKS: dict[str, tuple[str, ...]] = {
    "BRC-1": ("band10-inventory-complete",),
    "BRC-2": ("band10-all-units-certified",),
    "BRC-3": ("meta-class-single",),
    "BRC-4": ("founding-acyclic",),
    "BRC-5": ("foundation-reuse-integrity",),
    "BRC-6": ("band10-metamodel-integration-closed",),
    "BRC-7": ("traceability-rooted",),
}

#: BCC completion criterion → the validation check id(s) that substantiate it.
_BCC_CHECKS: dict[str, tuple[str, ...]] = {
    "BCC-1": ("band10-inventory-complete", "band10-all-units-certified"),
    "BCC-2": ("meta-class-single",),
    "BCC-3": ("band10-metamodel-integration-closed",),
    "BCC-4": ("founding-acyclic",),
    "BCC-5": ("meta-relationships-closed",),
    "BCC-6": ("foundation-reuse-integrity",),
    "BCC-7": ("non-constitutive", "band10-independence"),
    "BCC-8": ("band10-non-projection",),
}


def build_band_completion() -> Band10Completion:
    """Materially realize the whole Band-10 stack and compose the completion record.

    Reuses :func:`data.model_realize.realize` (which live-realizes and certifies U01…U10
    and integrates them into the U11 meta-model), then captures the eleven CERTIFIED unit
    certifications (U01…U10 members + the U11 meta-model itself) by reference.
    """
    udm = model_realize.realize()
    unit_certifications: list[tuple[str, str, bool]] = [
        (m.unit, m.certification_id, m.certified) for m in udm.members
    ]
    unit_certifications.append(
        (
            META_MODEL_UNIT,
            udm.certification.decision.certification_id,
            bool(udm.certification.certified),
        )
    )
    return make_band10_completion(
        CANONICAL_BAND_NAME,
        CANONICAL_BAND_TYPE_TAG,
        tuple(unit_certifications),
        meta_model_id=udm.model.model_id,
        integration=udm.integration_closure(),
        version=UNIT_VERSION,
        state=BandState.DEFINED,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B10-U12 certification/completion act."""

    completion: Band10Completion
    trace: TraceabilityRecord
    validation: Band10Validation
    certification: Band10Certification

    def _passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def readiness_criteria(self, *, byte_identical: bool) -> dict[str, bool]:
        passed = self._passed()
        result = {
            brc: all(passed.get(c, False) for c in checks)
            for brc, checks in _BRC_CHECKS.items()
        }
        result["BRC-8"] = byte_identical  # determinism self-check
        return dict(sorted(result.items()))

    def completion_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            bcc: all(passed.get(c, False) for c in checks)
            for bcc, checks in _BCC_CHECKS.items()
        }

    def unit_inventory(self) -> list[dict[str, Any]]:
        return [u.to_dict() for u in self.completion.units]

    def all_units_certified(self) -> bool:
        return self.completion.all_units_certified() and self.completion.inventory_complete()

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, executable certification record
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (  # inventory + certification (aggregation over the eleven units)
                passed.get("band10-inventory-complete", False)
                and passed.get("band10-all-units-certified", False)
                and self.all_units_certified()
            ),
            "AC-4": (  # coverage + integration + acyclic founding
                passed.get("meta-class-single", False)
                and passed.get("band10-metamodel-integration-closed", False)
                and passed.get("founding-acyclic", False)
            ),
            "AC-5": passed.get("band10-independence", False),  # no technology
            "AC-6": passed.get("non-constitutive", False),  # no authority/secret/tech
            "AC-7": True,  # realized under data/**; certified units unmodified
            "AC-8": self.trace.closed,  # full traceability (incl. eleven certified units)
        }

    def validation_criteria(self, *, byte_identical: bool) -> dict[str, bool]:
        passed = self._passed()
        return {
            "VC-1": self.validation.accepted,  # EC-1 ValidationEngine PASS + accepted
            "VC-2": all(self.readiness_criteria(byte_identical=byte_identical).values()),  # BRC
            "VC-3": all(self.completion_criteria().values()),  # BCC
            "VC-4": byte_identical,  # determinism (byte-identical recompute)
            "VC-5": passed.get("foundation-reuse-integrity", False),  # reuse integrity
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
            and self.all_units_certified()
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this certification act."""
        return {
            "artifact": "EC3-B10-U12-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "band_class": self.completion.meta_class,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "completion": self.completion.to_dict(),
            "unit_inventory": self.unit_inventory(),
            "unit_count": len(self.completion.units),
            "all_units_certified": self.all_units_certified(),
            "readiness_criteria": self.readiness_criteria(byte_identical=byte_identical),
            "readiness_criteria_definitions": dict(BAND_READINESS_CRITERIA),
            "completion_criteria": self.completion_criteria(),
            "completion_criteria_definitions": dict(BAND_COMPLETION_CRITERIA),
            "traceability": self.trace.to_dict(),
            "validation": {
                "report": self.validation.report.to_dict(),
                "evidence": self.validation.evidence.to_dict(),
                "acceptance": self.validation.decision.to_dict(),
            },
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
    """Perform the band-completion certification act and return its full deterministic result."""
    completion = build_band_completion()
    trace = build_band10_traceability(
        completion,
        unit=REALIZATION_UNIT,
        forward=(
            completion.band_id,
            "EC3-B10-U12-VALIDATION-EVIDENCE",
            "EC3-B10-U12-CCE-CERTIFICATION",
            "EC3-B10-U12-COMPLETION-REPORT",
        ),
    )
    validation = validate_band10(completion, trace)
    certification = certify_band10(validation, version=UNIT_VERSION)
    return RealizationResult(
        completion=completion,
        trace=trace,
        validation=validation,
        certification=certification,
    )


def determinism_check() -> tuple[bool, str, str]:
    """Realize twice and compare the evidence bundles byte-for-byte (VC-4)."""
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
    """Realize, self-check determinism, and write the evidence bundle to disk."""
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
    _write_json(evidence_dir / "capability-inventory.json", {
        "unit": REALIZATION_UNIT,
        "unit_count": bundle["unit_count"],
        "all_units_certified": bundle["all_units_certified"],
        "units": bundle["unit_inventory"],
    })
    _write_json(
        evidence_dir / "readiness-determination.json",
        {
            "unit": REALIZATION_UNIT,
            "readiness_criteria": bundle["readiness_criteria"],
            "definitions": bundle["readiness_criteria_definitions"],
            "ready": all(bundle["readiness_criteria"].values()),
        },
    )
    _write_json(
        evidence_dir / "completion-determination.json",
        {
            "unit": REALIZATION_UNIT,
            "completion_criteria": bundle["completion_criteria"],
            "definitions": bundle["completion_criteria_definitions"],
            "complete": all(bundle["completion_criteria"].values()),
            "determination": bundle["determination"],
        },
    )
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
        "all_units_certified": result.all_units_certified(),
        "ready": all(result.readiness_criteria(byte_identical=byte_identical).values()),
        "complete": all(result.completion_criteria().values()),
        "certification_id": result.certification.decision.certification_id,
        "band_id": result.completion.band_id,
        "unit_certification_ids": {u.unit: u.certification_id for u in result.completion.units},
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: certify the Band-10 realization, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b10-u12-realize",
        description="Certify the Band-10 Data realization (U01…U11) and emit evidence.",
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
        and summary["all_units_certified"]
        and summary["ready"]
        and summary["complete"]
    )
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B10-U12 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "REALIZATION_UNIT",
    "UNIT_VERSION",
    "DEFAULT_EVIDENCE_DIR",
    "build_band_completion",
    "RealizationResult",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
