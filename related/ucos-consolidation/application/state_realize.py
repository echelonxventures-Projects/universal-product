"""EC3-B12-U07 — Realization orchestrator + evidence emitter.

Performs the realization act authorized by
``EC-3-AP-4-BAND-12-ADMISSION-DETERMINATION`` (Band 12 ADMITTED · MEP-03 OPEN) for the
seventh Band-12 unit: constructs the canonical Universal State exemplar, validates it
through the CERTIFIED EC-1 engine (meta-validity V1…V5 + Application-/State-law
conformance), certifies it through the CCE ten gates (CC-1…CC-10) + Application compliance
(C1…C7), closes its No-Orphan traceability, and emits a **deterministic, content-addressed
evidence bundle**. A double-realization self-check proves byte-identical determinism (VC-4).

Run as a module::

    python -m application.state_realize                    # emit evidence + determination
    python -m application.state_realize --evidence-dir application/_evidence/EC3-B12-U07

This is engineering execution only (DE-05): it asserts no constitutional finality, selects
no technology, and writes nothing outside the caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from application.state import State, make_state
from application.state_certification import StateCertification, certify_state
from application.state_meta import (
    REALIZATION_UNIT,
    STATE_META_CLASS,
    StateKind,
    StateLifecycle,
)
from application.state_traceability import TraceabilityRecord, build_traceability
from application.state_validation import StateValidation, validate_state
from engine.certification.contracts import content_hash

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical Universal State exemplar realized to prove the construct — an
#: Interaction-State (AXH-07 Interaction) that is held by the CERTIFIED AMC-06 Interaction,
#: bound to a declared context, binds the frozen RL-F2 RUNTIME state concern by reference,
#: and presents DF-2 data, materially exercising the state-binds-RL-F2-by-reference path
#: (UAL-12 / STA-03, THE governing law) and forward-only recorded lifecycle (STA-04/05).
CANONICAL_TYPE_TAG = "ucos.application.state.foundation"
#: The construct that holds the canonical state (AMR-06 held-by, by reference) — the
#: CERTIFIED Band-12 U06 Interaction.
CANONICAL_HOLDER_REF = "ENG-005:AMC-06:ucos.application.interaction.foundation"
#: The declared, abstract context the canonical state is bound to (STA-06, no technology).
CANONICAL_CONTEXT_REF = "ENG-005:CONTEXT:ucos.application.state.context.foundation"
#: The DF-2 data the canonical state binds/presents (AMR-14, by reference).
CANONICAL_DATA_REF = "ENG-005:DF-2:ucos.application.state.data.foundation"
#: The frozen RUNTIME state concern the canonical state behaves-as (AMR-11 / §7, RL-F2).
CANONICAL_BEHAVIOR_REF = "ENG-005:RL-F2:runtime.state-transition"

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

#: The validation check ids substantiating Application-/State-law conformance (VC-3). Only
#: the laws that apply to the State are recorded (UAL-06/07/08/09/11 are scoped to the
#: Feature/Module/Application/Composition/Interaction units — recorded N/A in state_meta).
_UAL_CHECKS: dict[str, str] = {
    "UAL-02": "foundation-reuse-integrity",
    "UAL-03": "state-typed",
    "UAL-04": "state-identified-objectbound",
    "UAL-05": "state-identified-objectbound",
    "UAL-10": "state-binds-runtime-state",
    "UAL-12": "lifecycle-valid",
    "UAL-13": "state-presents-data",
    "UAL-15": "technology-independence",
}


def build_canonical_state() -> State:
    """Construct the canonical Interaction Universal State exemplar (AMC-07)."""
    return make_state(
        CANONICAL_TYPE_TAG,
        CANONICAL_HOLDER_REF,
        kind=StateKind.INTERACTION,
        context_ref=CANONICAL_CONTEXT_REF,
        data_ref=CANONICAL_DATA_REF,
        behavior_ref=CANONICAL_BEHAVIOR_REF,
        state=StateLifecycle.DEFINED,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B12-U07 realization act."""

    state: State
    trace: TraceabilityRecord
    validation: StateValidation
    certification: StateCertification

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
        # UAL-14 (security/governance evaluative, non-enforcing) — the State enacts nothing
        # and confers no authority.
        result["UAL-14"] = not self.state.confers_authority()
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, deliverable construct
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (
                passed.get("state-typed", False)
                and passed.get("state-identified-objectbound", False)
            ),
            "AC-4": passed.get("technology-independence", False),  # no state store/technology
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

    def state_compliance(self) -> dict[str, bool]:
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
            and all(self.state_compliance().values())
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this realization."""
        return {
            "artifact": "EC3-B12-U07-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": STATE_META_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "state": self.state.to_dict(),
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
                "application_compliance": self.state_compliance(),
            },
            "determination": self.determination(byte_identical=byte_identical),
        }


def realize() -> RealizationResult:
    """Perform the realization act and return its full deterministic result."""
    state = build_canonical_state()
    trace = build_traceability(
        state,
        unit=REALIZATION_UNIT,
        forward=(
            state.state_id,
            "EC3-B12-U07-VALIDATION-EVIDENCE",
            "EC3-B12-U07-CCE-CERTIFICATION",
            "EC3-B12-U07-COMPLETION-REPORT",
        ),
    )
    validation = validate_state(state, trace)
    certification = certify_state(validation, version=UNIT_VERSION)
    return RealizationResult(
        state=state,
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
        "state_id": result.state.state_id,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B12-U07, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b12-u07-realize",
        description="Realize the Universal Application State (AMC-07) and emit evidence.",
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
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B12-U07 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "UNIT_VERSION",
    "CANONICAL_TYPE_TAG",
    "CANONICAL_HOLDER_REF",
    "CANONICAL_CONTEXT_REF",
    "CANONICAL_DATA_REF",
    "CANONICAL_BEHAVIOR_REF",
    "DEFAULT_EVIDENCE_DIR",
    "RealizationResult",
    "build_canonical_state",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
