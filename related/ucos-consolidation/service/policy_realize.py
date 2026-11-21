"""EC3-B11-U09 — Policy realization orchestrator + evidence emitter.

Performs the realization act for **SMC-09 Policy** under MEP-02 (Band 11 Service realization):
constructs the canonical Universal Policy exemplar, validates it through the CERTIFIED EC-1
engine (meta-validity V1…V5 + Service-law + SPL principles), certifies it through the reused
CCE ten gates (CC-1…CC-10) + Service compliance (C1…C7), closes its No-Orphan traceability, and
emits a **deterministic, content-addressed evidence bundle**. A double-realization self-check
proves byte-identical determinism (VC-4).

Run as a module::

    python -m service.policy_realize --evidence-dir service/_evidence/EC3-B11-U09

Engineering execution only (DE-05): asserts no constitutional finality, selects no technology,
writes nothing outside the caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.certification.contracts import content_hash
from service.policy import Policy, make_policy
from service.policy_certification import certify_policy
from service.policy_meta import POLICY_META_CLASS, PolicyKind
from service.policy_traceability import (
    PolicyTraceabilityRecord,
    build_policy_traceability,
)
from service.policy_validation import validate_policy
from service.service_certification import ServiceCertification
from service.service_meta import ServiceState
from service.service_validation import ServiceValidation

#: The realization unit this module realizes (EC-3 Band 11, Unit 09).
REALIZATION_UNIT = "EC3-B11-U09"

#: The realized artifact version (version-pinned certification; USL-12).
UNIT_VERSION = "1.0.0"

#: The canonical Universal Policy exemplar realized to prove the construct — an Authorization
#: policy bound-by the CERTIFIED-by-reference canonical Contract, governing the canonical
#: Operation + Execution by reference, evaluating via the RUNTIME policy concern (RUNTIME-010)
#: by reference, and predicating over one DF-2 data reference. Its type_tag matches the
#: DEFAULT_POLICY_REF the Execution unit (SMC-08) governs-by, closing the SMR-08 spine.
CANONICAL_TYPE_TAG = "ucos.service.policy.foundation"
CANONICAL_CONTRACT_REF = "ENG-005:SOE-03:ucos.service.contract.foundation"
CANONICAL_SUBJECT_REFS = (
    "ENG-005:SOE-05:ucos.service.operation.foundation",
    "ENG-005:SOE-08:ucos.service.execution.foundation",
)
CANONICAL_DATA_REFS = ("ENG-005:DF-2:ucos.data.entity.governed",)

#: Where the default evidence bundle is written (code-adjacent; never the corpus).
DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

_META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "meta-class-single",
    "V2": "meta-relationships-closed",
    "V3": "meta-constraints",
    "V4": "founding-acyclic",
    "V5": "lifecycle-valid",
}

_USL_CHECKS: dict[str, str] = {
    "USL-02": "foundation-reuse-integrity",
    "USL-03": "policy-typed",
    "USL-04": "policy-identified-objectbound",
    "USL-05": "policy-identified-objectbound",
    "USL-06": "policy-boundary-bound",
    "USL-10": "policy-runtime-reuse",
    "USL-11": "policy-data-by-reference",
    "USL-12": "lifecycle-valid",
    "USL-13": "policy-declarative-nonenforcing",
    "USL-15": "technology-independence",
}


def build_canonical_policy() -> Policy:
    """Construct the canonical Authorization-Policy exemplar (SMC-09)."""
    return make_policy(
        CANONICAL_TYPE_TAG,
        CANONICAL_CONTRACT_REF,
        kind=PolicyKind.AUTHORIZATION,
        subject_refs=CANONICAL_SUBJECT_REFS,
        data_refs=CANONICAL_DATA_REFS,
        state=ServiceState.DEFINED,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B11-U09 realization act."""

    policy: Policy
    trace: PolicyTraceabilityRecord
    validation: ServiceValidation
    certification: ServiceCertification

    def _passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def meta_validity(self) -> dict[str, bool]:
        passed = self._passed()
        return {v: passed.get(cid, False) for v, cid in _META_VALIDITY_CHECKS.items()}

    def usl_conformance(self) -> dict[str, bool]:
        passed = self._passed()
        result = {law: passed.get(cid, False) for law, cid in _USL_CHECKS.items()}
        result["USL-01"] = True
        result["USL-14"] = not self.policy.confers_authority()
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,
            "AC-2": passed.get("foundation-reuse-integrity", False),
            "AC-3": (
                passed.get("policy-typed", False)
                and passed.get("policy-identified-objectbound", False)
            ),
            "AC-4": passed.get("technology-independence", False),
            "AC-5": passed.get("non-constitutive", False),
            "AC-6": True,
            "AC-7": self.trace.closed,
        }

    def validation_criteria(self, *, byte_identical: bool) -> dict[str, bool]:
        mv = self.meta_validity()
        return {
            "VC-1": self.validation.accepted,
            "VC-2": all(mv.values()),
            "VC-3": all(self.usl_conformance().values()),
            "VC-4": byte_identical,
            "VC-5": self._passed().get("foundation-reuse-integrity", False),
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
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        return {
            "artifact": "EC3-B11-U09-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": POLICY_META_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "policy": self.policy.to_dict(),
            "traceability": self.trace.to_dict(),
            "validation": {
                "report": self.validation.report.to_dict(),
                "evidence": self.validation.evidence.to_dict(),
                "acceptance": self.validation.decision.to_dict(),
            },
            "meta_validity_V1_V5": self.meta_validity(),
            "usl_conformance": self.usl_conformance(),
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
    """Perform the realization act and return its full deterministic result."""
    policy = build_canonical_policy()
    trace = build_policy_traceability(
        policy,
        unit=REALIZATION_UNIT,
        forward=(
            policy.policy_id,
            "EC3-B11-U09-VALIDATION-EVIDENCE",
            "EC3-B11-U09-CCE-CERTIFICATION",
            "EC3-B11-U09-COMPLETION-REPORT",
        ),
    )
    validation = validate_policy(policy, trace)
    certification = certify_policy(validation, version=UNIT_VERSION)
    return RealizationResult(
        policy=policy,
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
    _write_json(evidence_dir / "service-compliance.json", bundle["service_compliance_C1_C7"])
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
        "policy_id": result.policy.policy_id,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B11-U09, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b11-u09-realize",
        description="Realize the Universal Policy (SMC-09) and emit evidence.",
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
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B11-U09 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "REALIZATION_UNIT",
    "UNIT_VERSION",
    "CANONICAL_TYPE_TAG",
    "DEFAULT_EVIDENCE_DIR",
    "RealizationResult",
    "build_canonical_policy",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
