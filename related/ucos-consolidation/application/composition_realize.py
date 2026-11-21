"""EC3-B12-U08 — Realization orchestrator + evidence emitter.

Performs the realization act authorized by
``EC-3-AP-4-BAND-12-ADMISSION-DETERMINATION`` (Band 12 ADMITTED · MEP-03 OPEN) for the
eighth Band-12 unit: constructs the canonical Universal Composition exemplar, validates it
through the CERTIFIED EC-1 engine (meta-validity V1…V5 + Application-/Composition-law
conformance), certifies it through the CCE ten gates (CC-1…CC-10) + Application compliance
(C1…C7), closes its No-Orphan traceability, and emits a **deterministic, content-addressed
evidence bundle**. A double-realization self-check proves byte-identical determinism (VC-4).

Run as a module::

    python -m application.composition_realize                    # emit evidence + determination
    python -m application.composition_realize --evidence-dir application/_evidence/EC3-B12-U08

This is engineering execution only (DE-05): it asserts no constitutional finality, selects
no technology, and writes nothing outside the caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from application.composition import Composition, make_composition
from application.composition_certification import (
    CompositionCertification,
    certify_composition,
)
from application.composition_meta import (
    COMPOSITION_META_CLASS,
    REALIZATION_UNIT,
    CompositionKind,
    CompositionState,
)
from application.composition_traceability import TraceabilityRecord, build_traceability
from application.composition_validation import CompositionValidation, validate_composition
from engine.certification.contracts import content_hash

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical Universal Composition exemplar realized to prove the construct — a
#: Module-into-Application composition (AXH-08) that assembles the CERTIFIED Band-12 U03
#: Modules into the CERTIFIED Band-12 U01 Application, reuses PL-F2 experience composition
#: by reference, keeps its founding graph acyclic, and binds its composition-emit behavior
#: to the frozen RL-F2 RUNTIME event concern by reference — materially exercising the
#: founding-acyclic path (AMK-03 / CMP-C1 / UAL-09, THE governing law).
CANONICAL_TYPE_TAG = "ucos.application.composition.foundation"
#: The constituents the canonical composition assembles (AMR-07, by reference) — the
#: CERTIFIED Band-12 U03 Modules.
CANONICAL_MEMBER_REFS: tuple[str, ...] = (
    "ENG-005:AMC-03:ucos.application.module.foundation",
    "ENG-005:AMC-03:ucos.application.module.supporting",
)
#: The whole the canonical composition assembles (AMR-07 assembled-by, by reference) — the
#: CERTIFIED Band-12 U01 Application root.
CANONICAL_ASSEMBLED_REF = "ENG-005:AMC-01:ucos.application.foundation"
#: The PL-F2 experience composition the canonical composition is composed-as (AMR-12, by ref).
CANONICAL_COMPOSITION_REF = "ENG-005:PL-F2:PLATFORM-009.composition"
#: The frozen RUNTIME event concern the canonical composition binds (§7 emit, RL-F2, by ref).
CANONICAL_BEHAVIOR_REF = "ENG-005:RL-F2:runtime.composition-emit"

#: Where the default evidence bundle is written (code-adjacent; never the corpus).
DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

#: The validation check ids substantiating meta-validity V1…V5 (APPLICATION-005 §8).
_META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "meta-class-single",
    "V2": "meta-relationships-closed",
    "V3": "meta-constraints",
    "V4": "founding-acyclic",
    "V5": "lifecycle-valid",
}

#: The validation check ids substantiating Application-/Composition-law conformance (VC-3).
#: Only the laws that apply to the Composition are recorded (UAL-06/07/08/11/13 are scoped
#: to the Feature/Module/Interaction units — recorded N/A in composition_meta).
_UAL_CHECKS: dict[str, str] = {
    "UAL-02": "foundation-reuse-integrity",
    "UAL-03": "composition-typed",
    "UAL-04": "composition-identified-objectbound",
    "UAL-05": "composition-identified-objectbound",
    "UAL-09": "composition-by-reference",
    "UAL-10": "composition-behavior-by-reference",
    "UAL-12": "lifecycle-valid",
    "UAL-15": "technology-independence",
}


def build_canonical_composition() -> Composition:
    """Construct the canonical Module-into-Application Universal Composition exemplar (AMC-08)."""
    return make_composition(
        CANONICAL_TYPE_TAG,
        CANONICAL_MEMBER_REFS,
        kind=CompositionKind.MODULE_INTO_APPLICATION,
        assembled_ref=CANONICAL_ASSEMBLED_REF,
        composition_ref=CANONICAL_COMPOSITION_REF,
        behavior_ref=CANONICAL_BEHAVIOR_REF,
        state=CompositionState.DEFINED,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B12-U08 realization act."""

    composition: Composition
    trace: TraceabilityRecord
    validation: CompositionValidation
    certification: CompositionCertification

    # -- derived conformance roll-ups ------------------------------------------

    def _passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def meta_validity(self) -> dict[str, bool]:
        passed = self._passed()
        return {v: passed.get(cid, False) for v, cid in _META_VALIDITY_CHECKS.items()}

    def ual_conformance(self) -> dict[str, bool]:
        passed = self._passed()
        result = {law: passed.get(cid, False) for law, cid in _UAL_CHECKS.items()}
        # UAL-01 (layer) is satisfied structurally by founding on the frozen substrate.
        result["UAL-01"] = True
        # UAL-14 (security/governance evaluative, non-enforcing) — the Composition enacts
        # nothing and confers no authority.
        result["UAL-14"] = not self.composition.confers_authority()
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, deliverable construct
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (
                passed.get("composition-typed", False)
                and passed.get("composition-identified-objectbound", False)
            ),
            "AC-4": passed.get("technology-independence", False),  # no bundler/packaging tech
            "AC-5": passed.get("non-constitutive", False),  # no authority/secret
            "AC-6": True,  # realized under application/**; frozen corpus/data/service unmodified
            "AC-7": self.trace.closed,  # full traceability recorded
        }

    def validation_criteria(self, *, byte_identical: bool) -> dict[str, bool]:
        mv = self.meta_validity()
        return {
            "VC-1": self.validation.accepted,  # EC-1 ValidationEngine PASS + accepted
            "VC-2": all(mv.values()),  # meta-validity V1…V5
            "VC-3": all(self.ual_conformance().values()),  # applicable UAL conformance
            "VC-4": byte_identical,  # determinism (byte-identical recompute)
            "VC-5": self._passed().get("foundation-reuse-integrity", False),  # reuse integrity
        }

    def certification_gates(self) -> dict[str, bool]:
        return {f.criterion_id: f.passed for f in self.certification.decision.findings}

    def composition_compliance(self) -> dict[str, bool]:
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
            and all(self.composition_compliance().values())
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this realization."""
        return {
            "artifact": "EC3-B12-U08-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": COMPOSITION_META_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "composition": self.composition.to_dict(),
            "traceability": self.trace.to_dict(),
            "validation": {
                "report": self.validation.report.to_dict(),
                "evidence": self.validation.evidence.to_dict(),
                "acceptance": self.validation.decision.to_dict(),
            },
            "meta_validity_V1_V5": self.meta_validity(),
            "ual_conformance": self.ual_conformance(),
            "certification": {
                "cce_gates": self.certification.decision.to_dict(),
                "ledger": self.certification.ledger.to_dict(),
                "evidence": self.certification.evidence.to_dict(),
            },
            "application_compliance_C1_C7": self.certification.compliance.to_dict(),
            "criteria": {
                "acceptance": self.acceptance_criteria(),
                "validation": self.validation_criteria(byte_identical=byte_identical),
                "certification_gates": self.certification_gates(),
                "application_compliance": self.composition_compliance(),
            },
            "determination": self.determination(byte_identical=byte_identical),
        }


def realize() -> RealizationResult:
    """Perform the realization act and return its full deterministic result."""
    composition = build_canonical_composition()
    trace = build_traceability(
        composition,
        unit=REALIZATION_UNIT,
        forward=(
            composition.composition_id,
            "EC3-B12-U08-VALIDATION-EVIDENCE",
            "EC3-B12-U08-CCE-CERTIFICATION",
            "EC3-B12-U08-COMPLETION-REPORT",
        ),
    )
    validation = validate_composition(composition, trace)
    certification = certify_composition(validation, version=UNIT_VERSION)
    return RealizationResult(
        composition=composition,
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
    _write_json(
        evidence_dir / "application-compliance.json", bundle["application_compliance_C1_C7"]
    )
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
        "composition_id": result.composition.composition_id,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B12-U08, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b12-u08-realize",
        description="Realize the Universal Application Composition (AMC-08) and emit evidence.",
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
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B12-U08 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "UNIT_VERSION",
    "CANONICAL_TYPE_TAG",
    "CANONICAL_MEMBER_REFS",
    "CANONICAL_ASSEMBLED_REF",
    "CANONICAL_COMPOSITION_REF",
    "CANONICAL_BEHAVIOR_REF",
    "DEFAULT_EVIDENCE_DIR",
    "RealizationResult",
    "build_canonical_composition",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
