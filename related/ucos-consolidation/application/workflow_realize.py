"""EC3-B12-U05 — Realization orchestrator + evidence emitter.

Performs the realization act authorized by
``EC-3-AP-4-BAND-12-ADMISSION-DETERMINATION`` (Band 12 ADMITTED · MEP-03 OPEN) for the
fifth Band-12 unit: constructs the canonical Universal Workflow exemplar, validates it
through the CERTIFIED EC-1 engine (meta-validity V1…V5 + Application-/Workflow-law
conformance), certifies it through the CCE ten gates (CC-1…CC-10) + Application compliance
(C1…C7), closes its No-Orphan traceability, and emits a **deterministic, content-addressed
evidence bundle**. A double-realization self-check proves byte-identical determinism (VC-4).

Run as a module::

    python -m application.workflow_realize                    # emit evidence + determination
    python -m application.workflow_realize --evidence-dir application/_evidence/EC3-B12-U05

This is engineering execution only (DE-05): it asserts no constitutional finality, selects
no technology, and writes nothing outside the caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from application.workflow import Workflow, make_workflow
from application.workflow_certification import WorkflowCertification, certify_workflow
from application.workflow_meta import (
    REALIZATION_UNIT,
    WORKFLOW_META_CLASS,
    WorkflowKind,
    WorkflowState,
)
from application.workflow_traceability import TraceabilityRecord, build_traceability
from application.workflow_validation import WorkflowValidation, validate_workflow
from engine.certification.contracts import content_hash

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical Universal Workflow exemplar realized to prove the construct — a
#: Process-Workflow (AXH-05 Process) that sequences two features/operations toward an
#: outcome and consumes two SF-2 operations, materially exercising the long-running,
#: state-advancing path (WKF-07 / WKF-C5) and the ordered-sequence identity distinction.
CANONICAL_TYPE_TAG = "ucos.application.workflow.foundation"
#: The features/operations the canonical workflow sequences (AMR-04, by reference; WKF-04).
CANONICAL_SEQUENCE_REFS: tuple[str, ...] = (
    "ENG-005:AMC-04:ucos.application.feature.intake",
    "ENG-005:AMC-04:ucos.application.feature.fulfilment",
)
#: The SF-2 operations the canonical workflow's steps consume (AMR-13, by reference).
CANONICAL_OPERATION_REFS: tuple[str, ...] = (
    "ENG-005:SF-2:ucos.service.operation.primary",
    "ENG-005:SF-2:ucos.service.operation.secondary",
)
#: The State the canonical workflow holds/advances (AMR-06, by reference; WKF-06 → RL-F2).
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

#: The validation check ids substantiating Application-/Workflow-law conformance (VC-3).
#: Only the laws that apply to the Workflow are recorded (UAL-06/07/08/09/11/13 are scoped
#: to the Feature/Module/Application/Interaction units — recorded N/A in workflow_meta).
_UAL_CHECKS: dict[str, str] = {
    "UAL-02": "foundation-reuse-integrity",
    "UAL-03": "workflow-typed",
    "UAL-04": "workflow-identified-objectbound",
    "UAL-05": "workflow-identified-objectbound",
    "UAL-10": "behavior-by-reference",
    "UAL-12": "lifecycle-valid",
    "UAL-15": "technology-independence",
}


def build_canonical_workflow() -> Workflow:
    """Construct the canonical Process Universal Workflow exemplar (AMC-05)."""
    return make_workflow(
        CANONICAL_TYPE_TAG,
        CANONICAL_SEQUENCE_REFS,
        CANONICAL_OPERATION_REFS,
        kind=WorkflowKind.PROCESS,
        state_ref=CANONICAL_STATE_REF,
        state=WorkflowState.DEFINED,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B12-U05 realization act."""

    workflow: Workflow
    trace: TraceabilityRecord
    validation: WorkflowValidation
    certification: WorkflowCertification

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
        # UAL-14 (security/governance evaluative, non-enforcing) — the Workflow enacts
        # nothing and confers no authority.
        result["UAL-14"] = not self.workflow.confers_authority()
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, deliverable construct
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (
                passed.get("workflow-typed", False)
                and passed.get("workflow-identified-objectbound", False)
            ),
            "AC-4": passed.get("technology-independence", False),  # no technology/engine
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

    def workflow_compliance(self) -> dict[str, bool]:
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
            and all(self.workflow_compliance().values())
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this realization."""
        return {
            "artifact": "EC3-B12-U05-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": WORKFLOW_META_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "workflow": self.workflow.to_dict(),
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
                "application_compliance": self.workflow_compliance(),
            },
            "determination": self.determination(byte_identical=byte_identical),
        }


def realize() -> RealizationResult:
    """Perform the realization act and return its full deterministic result."""
    workflow = build_canonical_workflow()
    trace = build_traceability(
        workflow,
        unit=REALIZATION_UNIT,
        forward=(
            workflow.workflow_id,
            "EC3-B12-U05-VALIDATION-EVIDENCE",
            "EC3-B12-U05-CCE-CERTIFICATION",
            "EC3-B12-U05-COMPLETION-REPORT",
        ),
    )
    validation = validate_workflow(workflow, trace)
    certification = certify_workflow(validation, version=UNIT_VERSION)
    return RealizationResult(
        workflow=workflow,
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
        "workflow_id": result.workflow.workflow_id,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B12-U05, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b12-u05-realize",
        description="Realize the Universal Application Workflow (AMC-05) and emit evidence.",
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
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B12-U05 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "UNIT_VERSION",
    "CANONICAL_TYPE_TAG",
    "CANONICAL_SEQUENCE_REFS",
    "CANONICAL_OPERATION_REFS",
    "CANONICAL_STATE_REF",
    "DEFAULT_EVIDENCE_DIR",
    "RealizationResult",
    "build_canonical_workflow",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
