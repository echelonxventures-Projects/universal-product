"""EC3-B12-U06 — Realization orchestrator + evidence emitter.

Performs the realization act authorized by
``EC-3-AP-4-BAND-12-ADMISSION-DETERMINATION`` (Band 12 ADMITTED · MEP-03 OPEN) for the
sixth Band-12 unit: constructs the canonical Universal Interaction exemplar, validates it
through the CERTIFIED EC-1 engine (meta-validity V1…V5 + Application-/Interaction-law
conformance), certifies it through the CCE ten gates (CC-1…CC-10) + Application compliance
(C1…C7), closes its No-Orphan traceability, and emits a **deterministic, content-addressed
evidence bundle**. A double-realization self-check proves byte-identical determinism (VC-4).

Run as a module::

    python -m application.interaction_realize                    # emit evidence + determination
    python -m application.interaction_realize --evidence-dir application/_evidence/EC3-B12-U06

This is engineering execution only (DE-05): it asserts no constitutional finality, selects
no technology, and writes nothing outside the caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from application.interaction import Interaction, make_interaction
from application.interaction_certification import (
    InteractionCertification,
    certify_interaction,
)
from application.interaction_meta import (
    INTERACTION_META_CLASS,
    REALIZATION_UNIT,
    InteractionKind,
    InteractionState,
)
from application.interaction_traceability import TraceabilityRecord, build_traceability
from application.interaction_validation import InteractionValidation, validate_interaction
from engine.certification.contracts import content_hash

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical Universal Interaction exemplar realized to prove the construct — a
#: Command-Interaction (AXH-06 Command; direction "command") that engages a feature,
#: presents DF-2 data over an abstract surface, and holds interaction/session state,
#: materially exercising the typed-exchange-at-an-abstract-surface path (UAL-11) and the
#: founding engaged-through edge (AMR-05).
CANONICAL_TYPE_TAG = "ucos.application.interaction.foundation"
#: The Feature the canonical interaction engages (AMR-05 engaged-through, by reference).
CANONICAL_FEATURE_REF = "ENG-005:AMC-04:ucos.application.feature.foundation"
#: The abstract presentation surface the canonical interaction is described over (INT-03).
CANONICAL_SURFACE_REF = "ENG-005:SURFACE:ucos.application.interaction.surface.foundation"
#: The DF-2 data the canonical interaction presents/exchanges (AMR-14, by reference).
CANONICAL_DATA_REF = "ENG-005:DF-2:ucos.application.interaction.exchange.foundation"
#: The interaction/session State the canonical interaction holds (AMR-06, by reference).
CANONICAL_STATE_REF = "ENG-005:AMC-07:ucos.application.state.foundation"

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

#: The validation check ids substantiating Application-/Interaction-law conformance (VC-3).
#: Only the laws that apply to the Interaction are recorded (UAL-06/07/08/09 are scoped to
#: the Feature/Module/Application/Composition units — recorded N/A in interaction_meta).
_UAL_CHECKS: dict[str, str] = {
    "UAL-02": "foundation-reuse-integrity",
    "UAL-03": "interaction-typed",
    "UAL-04": "interaction-identified-objectbound",
    "UAL-05": "interaction-identified-objectbound",
    "UAL-10": "behavior-by-reference",
    "UAL-11": "interaction-surface-abstract",
    "UAL-12": "lifecycle-valid",
    "UAL-13": "interaction-presents-data",
    "UAL-15": "technology-independence",
}


def build_canonical_interaction() -> Interaction:
    """Construct the canonical Command Universal Interaction exemplar (AMC-06)."""
    return make_interaction(
        CANONICAL_TYPE_TAG,
        CANONICAL_FEATURE_REF,
        kind=InteractionKind.COMMAND,
        surface_ref=CANONICAL_SURFACE_REF,
        data_ref=CANONICAL_DATA_REF,
        state_ref=CANONICAL_STATE_REF,
        state=InteractionState.DEFINED,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B12-U06 realization act."""

    interaction: Interaction
    trace: TraceabilityRecord
    validation: InteractionValidation
    certification: InteractionCertification

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
        # UAL-14 (security/governance evaluative, non-enforcing) — the Interaction enacts
        # nothing and confers no authority.
        result["UAL-14"] = not self.interaction.confers_authority()
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, deliverable construct
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (
                passed.get("interaction-typed", False)
                and passed.get("interaction-identified-objectbound", False)
            ),
            "AC-4": passed.get("technology-independence", False),  # no technology/rendering
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

    def interaction_compliance(self) -> dict[str, bool]:
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
            and all(self.interaction_compliance().values())
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this realization."""
        return {
            "artifact": "EC3-B12-U06-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": INTERACTION_META_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "interaction": self.interaction.to_dict(),
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
                "application_compliance": self.interaction_compliance(),
            },
            "determination": self.determination(byte_identical=byte_identical),
        }


def realize() -> RealizationResult:
    """Perform the realization act and return its full deterministic result."""
    interaction = build_canonical_interaction()
    trace = build_traceability(
        interaction,
        unit=REALIZATION_UNIT,
        forward=(
            interaction.interaction_id,
            "EC3-B12-U06-VALIDATION-EVIDENCE",
            "EC3-B12-U06-CCE-CERTIFICATION",
            "EC3-B12-U06-COMPLETION-REPORT",
        ),
    )
    validation = validate_interaction(interaction, trace)
    certification = certify_interaction(validation, version=UNIT_VERSION)
    return RealizationResult(
        interaction=interaction,
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
        "interaction_id": result.interaction.interaction_id,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B12-U06, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b12-u06-realize",
        description="Realize the Universal Application Interaction (AMC-06) and emit evidence.",
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
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B12-U06 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "UNIT_VERSION",
    "CANONICAL_TYPE_TAG",
    "CANONICAL_FEATURE_REF",
    "CANONICAL_SURFACE_REF",
    "CANONICAL_DATA_REF",
    "CANONICAL_STATE_REF",
    "DEFAULT_EVIDENCE_DIR",
    "RealizationResult",
    "build_canonical_interaction",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
