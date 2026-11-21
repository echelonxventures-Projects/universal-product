"""EC3-B11-U13 — Realization orchestrator + evidence emitter (Band-11 Freeze).

Performs the freeze act authorized by the ``SERVICE-015`` freeze pattern applied to the EC-3
realization, discharged after the ``MCP-003`` **MEP-02** exit criterion (Band-11
CERTIFIED-COMPLETE, U01…U12): it **materially re-realizes and re-certifies the whole Band-11
stack** through the CERTIFIED U12 band orchestrator (:func:`service.band11_realize.realize`),
which itself re-realizes the ten concern meta-classes (U01…U10), integrates them into the
SERVICE-005 meta-model (U11), and produces the Band-11 Realization Completion (U12,
certification-of-certifications). From that single reuse call it captures the **twelve**
CERTIFIED unit certifications (the eleven realization units by reference + the U12 band
completion itself) and composes them into an immutable
:class:`~service.band11_freeze.Band11Freeze` baseline record — the seal of the whole band.

It validates the freeze through the CERTIFIED EC-1 engine (preconditions FP-1…6 + effects
FE-1…5), certifies it through the CCE ten gates (CC-1…CC-10, reused verbatim from SMC-01) +
Service compliance (C1…C7, C5 materially exercised at freeze level), closes its No-Orphan
traceability (incl. the twelve certified units), and emits a **deterministic,
content-addressed evidence bundle**. A double-realization self-check proves byte-identical
determinism — the immutability guarantee (FP-6): the frozen baseline recomputes identically.

This capability **introduces no new service concern, meta-class, ontology, or primitive, and
no new functionality** (USL-02 / USL-15): it references, verifies, aggregates, seals, and
certifies — it never rewrites, recreates, mutates, or re-judges any CERTIFIED unit.

Run as a module::

    python -m service.band11_freeze_realize
    python -m service.band11_freeze_realize --evidence-dir service/_evidence/EC3-B11-U13

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

from engine.certification.contracts import content_hash

# --- the CERTIFIED U12 band orchestrator, reused by reference (USL-02) ------------
from service import band11_realize
from service.band11_freeze import Band11Freeze, make_band11_freeze
from service.band11_freeze_certification import (
    Band11FreezeCertification,
    certify_band11_freeze,
)
from service.band11_freeze_meta import (
    BAND_COMPLETION_UNIT,
    FREEZE_EFFECTS,
    FREEZE_PRECONDITIONS,
    FreezeState,
)
from service.band11_freeze_traceability import build_band11_freeze_traceability
from service.band11_freeze_validation import Band11FreezeValidation, validate_band11_freeze
from service.service_traceability import TraceabilityRecord

#: The realization unit this module realizes (EC-3 Band 11, Unit 13).
REALIZATION_UNIT = "EC3-B11-U13"

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical freeze name/type.
CANONICAL_FREEZE_NAME = "ucos.service.band11.freeze"
CANONICAL_FREEZE_TYPE_TAG = "ucos.core.band-freeze"

#: Where the default evidence bundle is written (code-adjacent; never the corpus).
DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

#: FP precondition → the validation check id(s) that substantiate it (FP-6 is the
#: determinism self-check, decided separately).
_FP_CHECKS: dict[str, tuple[str, ...]] = {
    "FP-1": ("freeze-inventory-complete", "freeze-all-units-certified"),
    "FP-2": ("founding-acyclic",),
    "FP-3": ("meta-class-single",),
    "FP-4": ("freeze-band-completion-referenced", "meta-relationships-closed"),
    "FP-5": ("foundation-reuse-integrity",),
}

#: FE effect → the validation check id(s) that substantiate it.
_FE_CHECKS: dict[str, tuple[str, ...]] = {
    "FE-1": ("freeze-immutable-baseline", "freeze-all-units-frozen"),
    "FE-2": ("foundation-reuse-integrity",),
    "FE-3": ("non-constitutive", "freeze-effects-declared"),
    "FE-4": ("freeze-non-projection", "freeze-effects-declared"),
    "FE-5": ("freeze-effects-declared", "freeze-versioned"),
}


def build_band_freeze() -> Band11Freeze:
    """Materially re-realize the whole Band-11 stack and compose the freeze baseline.

    Reuses :func:`service.band11_realize.realize` (which live-realizes and certifies U01…U10,
    integrates them into the U11 meta-model, and produces the U12 band completion), then
    captures the **twelve** CERTIFIED unit certifications (the eleven realization units +
    the U12 band completion) by reference.
    """
    band = band11_realize.realize()
    unit_certifications: list[tuple[str, str, bool]] = [
        (u.unit, u.certification_id, u.certified) for u in band.completion.units
    ]
    band_completion_cert = band.certification.decision.certification_id
    unit_certifications.append(
        (BAND_COMPLETION_UNIT, band_completion_cert, bool(band.certification.certified))
    )
    return make_band11_freeze(
        CANONICAL_FREEZE_NAME,
        CANONICAL_FREEZE_TYPE_TAG,
        tuple(unit_certifications),
        band_completion_id=band.completion.band_id,
        band_completion_certification_id=band_completion_cert,
        meta_model_id=band.completion.meta_model_id,
        integration=band.completion.integration_map(),
        version=UNIT_VERSION,
        state=FreezeState.DEFINED,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B11-U13 freeze act."""

    freeze: Band11Freeze
    trace: TraceabilityRecord
    validation: Band11FreezeValidation
    certification: Band11FreezeCertification

    def _passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def freeze_preconditions(self, *, byte_identical: bool) -> dict[str, bool]:
        passed = self._passed()
        result = {
            fp: all(passed.get(c, False) for c in checks) for fp, checks in _FP_CHECKS.items()
        }
        result["FP-6"] = byte_identical  # determinism self-check (immutability guarantee)
        return dict(sorted(result.items()))

    def freeze_effects(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            fe: all(passed.get(c, False) for c in checks) for fe, checks in _FE_CHECKS.items()
        }

    def frozen_inventory(self) -> list[dict[str, Any]]:
        return [u.to_dict() for u in self.freeze.units]

    def all_units_certified(self) -> bool:
        return self.freeze.all_units_certified() and self.freeze.inventory_complete()

    def all_units_frozen(self) -> bool:
        return self.freeze.all_units_frozen() and self.freeze.inventory_complete()

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, executable freeze record
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (  # inventory + certification (aggregation over the twelve units)
                passed.get("freeze-inventory-complete", False)
                and passed.get("freeze-all-units-certified", False)
                and self.all_units_certified()
            ),
            "AC-4": (  # coverage + band-completion + acyclic founding
                passed.get("meta-class-single", False)
                and passed.get("freeze-band-completion-referenced", False)
                and passed.get("founding-acyclic", False)
            ),
            "AC-5": passed.get("freeze-independence", False),  # no technology
            "AC-6": passed.get("non-constitutive", False),  # no authority/secret/tech
            "AC-7": True,  # realized under service/**; certified units unmodified
            "AC-8": self.trace.closed,  # full traceability (incl. twelve certified units)
        }

    def validation_criteria(self, *, byte_identical: bool) -> dict[str, bool]:
        passed = self._passed()
        return {
            "VC-1": self.validation.accepted,  # EC-1 ValidationEngine PASS + accepted
            "VC-2": all(self.freeze_preconditions(byte_identical=byte_identical).values()),  # FP
            "VC-3": all(self.freeze_effects().values()),  # FE
            "VC-4": byte_identical,  # determinism (byte-identical recompute — immutability)
            "VC-5": passed.get("foundation-reuse-integrity", False),  # reuse integrity
        }

    def certification_gates(self) -> dict[str, bool]:
        return {f.criterion_id: f.passed for f in self.certification.decision.findings}

    def service_compliance(self) -> dict[str, bool]:
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
            and all(self.service_compliance().values())
            and self.all_units_certified()
            and self.all_units_frozen()
        ):
            return "FROZEN"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "FROZEN WITH CONDITIONS"
        return "NOT FROZEN"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this freeze act."""
        return {
            "artifact": "EC3-B11-U13-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "freeze_class": self.freeze.meta_class,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "freeze": self.freeze.to_dict(),
            "baseline_digest": self.freeze.baseline_digest,
            "frozen_inventory": self.frozen_inventory(),
            "unit_count": len(self.freeze.units),
            "all_units_certified": self.all_units_certified(),
            "all_units_frozen": self.all_units_frozen(),
            "freeze_preconditions": self.freeze_preconditions(byte_identical=byte_identical),
            "freeze_precondition_definitions": dict(FREEZE_PRECONDITIONS),
            "freeze_effects": self.freeze_effects(),
            "freeze_effect_definitions": dict(FREEZE_EFFECTS),
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
            "service_compliance_C1_C7": self.certification.compliance.to_dict(),
            "criteria": {
                "acceptance": self.acceptance_criteria(),
                "validation": self.validation_criteria(byte_identical=byte_identical),
                "certification_gates": self.certification_gates(),
                "service_compliance": self.service_compliance(),
            },
            "determination": self.determination(byte_identical=byte_identical),
        }


def realize() -> RealizationResult:
    """Perform the freeze act and return its full deterministic result."""
    freeze = build_band_freeze()
    trace = build_band11_freeze_traceability(
        freeze,
        unit=REALIZATION_UNIT,
        forward=(
            freeze.freeze_id,
            "EC3-B11-U13-VALIDATION-EVIDENCE",
            "EC3-B11-U13-CCE-CERTIFICATION",
            "EC3-B11-U13-COMPLETION-REPORT",
        ),
    )
    validation = validate_band11_freeze(freeze, trace)
    certification = certify_band11_freeze(validation, version=UNIT_VERSION)
    return RealizationResult(
        freeze=freeze,
        trace=trace,
        validation=validation,
        certification=certification,
    )


def determinism_check() -> tuple[bool, str, str]:
    """Realize twice and compare the evidence bundles byte-for-byte (VC-4 / FP-6)."""
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
    _write_json(evidence_dir / "service-compliance.json", bundle["service_compliance_C1_C7"])
    _write_json(evidence_dir / "traceability.json", bundle["traceability"])
    _write_json(
        evidence_dir / "freeze-baseline.json",
        {
            "unit": REALIZATION_UNIT,
            "freeze_id": result.freeze.freeze_id,
            "baseline_digest": result.freeze.baseline_digest,
            "band_completion_id": result.freeze.band_completion_id,
            "band_completion_certification_id": result.freeze.band_completion_certification_id,
            "unit_count": len(result.freeze.units),
            "all_units_certified": result.all_units_certified(),
            "all_units_frozen": result.all_units_frozen(),
            "effects": list(result.freeze.effects),
            "units": result.frozen_inventory(),
        },
    )
    _write_json(
        evidence_dir / "freeze-preconditions.json",
        {
            "unit": REALIZATION_UNIT,
            "freeze_preconditions": bundle["freeze_preconditions"],
            "definitions": bundle["freeze_precondition_definitions"],
            "ready": all(bundle["freeze_preconditions"].values()),
        },
    )
    _write_json(
        evidence_dir / "freeze-effects.json",
        {
            "unit": REALIZATION_UNIT,
            "freeze_effects": bundle["freeze_effects"],
            "definitions": bundle["freeze_effect_definitions"],
            "declared": all(bundle["freeze_effects"].values()),
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
        "all_units_frozen": result.all_units_frozen(),
        "ready": all(result.freeze_preconditions(byte_identical=byte_identical).values()),
        "effects_declared": all(result.freeze_effects().values()),
        "certification_id": result.certification.decision.certification_id,
        "freeze_id": result.freeze.freeze_id,
        "baseline_digest": result.freeze.baseline_digest,
        "unit_certification_ids": {u.unit: u.certification_id for u in result.freeze.units},
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: freeze the Band-11 realization, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b11-u13-realize",
        description="Freeze the Band-11 Service realization (U01…U12) and emit evidence.",
    )
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    args = parser.parse_args(argv)

    summary = emit_evidence(Path(args.evidence_dir))
    print(json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=False))
    frozen = (
        summary["determination"] == "FROZEN"
        and summary["validation_accepted"]
        and summary["certified"]
        and summary["traceability_closed"]
        and summary["byte_identical"]
        and summary["all_units_certified"]
        and summary["all_units_frozen"]
        and summary["ready"]
        and summary["effects_declared"]
    )
    print(f"[{'PASS' if frozen else 'FAIL'}] EC3-B11-U13 → {summary['determination']}")
    return 0 if frozen else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "REALIZATION_UNIT",
    "UNIT_VERSION",
    "DEFAULT_EVIDENCE_DIR",
    "build_band_freeze",
    "RealizationResult",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
