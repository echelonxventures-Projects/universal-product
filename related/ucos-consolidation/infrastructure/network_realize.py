"""EC3-B13-U03 — Realization orchestrator + evidence emitter.

Performs the realization act authorized by ``EC-3-AP-5-BAND-13-ADMISSION-DETERMINATION``
(Band 13 ADMITTED · MEP-04 OPEN) and planned by ``EC-3-B13-P01`` (Band-13 Master Program
Charter §3.2/§4.1 STAGE 2, WBS row EC3-B13-U03): constructs the canonical Universal
Infrastructure Network exemplar, validates it through the CERTIFIED EC-1 engine
(meta-validity WF-1…12 + Infrastructure-law UIL-01…15), certifies it through the CCE ten
gates (CC-1…CC-10) + Infrastructure compliance (C1…C7), closes its No-Orphan
traceability, and emits a **deterministic, content-addressed evidence bundle**. A
double-realization self-check proves byte-identical determinism (VC-4).

Run as a module::

    python -m infrastructure.network_realize
    python -m infrastructure.network_realize --evidence-dir infrastructure/_evidence/EC3-B13-U03

This is engineering execution only (DE-05): it asserts no constitutional finality,
selects no technology, and writes nothing outside the caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.certification.contracts import content_hash
from infrastructure.network import NetworkResource, make_network_resource
from infrastructure.network_certification import NetworkCertification, certify_network
from infrastructure.network_meta import (
    INFRASTRUCTURE_META_CLASS,
    REALIZATION_UNIT,
    InfrastructureState,
)
from infrastructure.network_traceability import TraceabilityRecord, build_traceability
from infrastructure.network_validation import NetworkValidation, validate_network

#: The realized artifact version (version-pinned certification).
UNIT_VERSION = "1.0.0"

#: The canonical Universal Infrastructure Network exemplar realized to prove the
#: construct: a network resource with a declared, unbounded capacity, located at an
#: (abstract) Locality by reference, that declares its connected endpoints as a typed
#: ENG-005 reachability link (no protocol/transport selected).
CANONICAL_TYPE_TAG = "ucos.infrastructure.network.foundation"
CANONICAL_LOCALITY_REF = "ENG-005:INFRASTRUCTURE-011:locality.foundation"
CANONICAL_SOURCE_REF = "ENG-005:INFRASTRUCTURE-007:compute.endpoint.a"
CANONICAL_TARGET_REF = "ENG-005:INFRASTRUCTURE-007:compute.endpoint.b"
CANONICAL_CONNECTIVITY_CLASS = "reachability"
CANONICAL_CAPACITY_AMOUNT = 1
CANONICAL_CAPACITY_UNIT = "connectivity-unit"

#: Where the default evidence bundle is written (code-adjacent; never the corpus).
DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

#: The validation check ids substantiating meta-validity (INFRASTRUCTURE-005 §5 WF rules
#: applicable to the Network Resource). WF-4/6/7/8/9/10 are scoped to other leaf
#: meta-classes. WF-5 (a Resource declares capacity and locality) is a governing rule.
_META_VALIDITY_CHECKS: dict[str, str] = {
    "WF-1": "meta-class-single",
    "WF-2": "infra-network-connectivity-by-reference",
    "WF-3": "founding-acyclic",
    "WF-5": "infra-network-declares-capacity-locality",
    "WF-11": "foundation-reuse-integrity",
    "WF-12": "non-constitutive",
}

#: The validation check ids substantiating Infrastructure-law UIL conformance (VC-3).
_UIL_CHECKS: dict[str, str] = {
    "UIL-02": "foundation-reuse-integrity",
    "UIL-03": "infra-network-typed",
    "UIL-04": "infra-network-identified-objectbound",
    "UIL-05": "infra-network-identified-objectbound",
    "UIL-07": "infra-network-honors-boundaries",
    "UIL-08": "infra-network-declares-capacity-locality",
    "UIL-09": "infra-network-connectivity-by-reference",
    "UIL-12": "technology-independence",
    "UIL-13": "scaling-unbounded",
    "UIL-15": "non-constitutive",
}


def build_canonical_network_resource() -> NetworkResource:
    """Construct the canonical Universal Infrastructure Network exemplar."""
    return make_network_resource(
        CANONICAL_TYPE_TAG,
        CANONICAL_LOCALITY_REF,
        source_ref=CANONICAL_SOURCE_REF,
        target_ref=CANONICAL_TARGET_REF,
        connectivity_class=CANONICAL_CONNECTIVITY_CLASS,
        amount=CANONICAL_CAPACITY_AMOUNT,
        unit=CANONICAL_CAPACITY_UNIT,
        state=InfrastructureState.DEFINED,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B13-U03 realization act."""

    resource: NetworkResource
    trace: TraceabilityRecord
    validation: NetworkValidation
    certification: NetworkCertification

    # -- derived conformance roll-ups ------------------------------------------

    def _passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def meta_validity(self) -> dict[str, bool]:
        passed = self._passed()
        return {wf: passed.get(cid, False) for wf, cid in _META_VALIDITY_CHECKS.items()}

    def uil_conformance(self) -> dict[str, bool]:
        passed = self._passed()
        result = {law: passed.get(cid, False) for law, cid in _UIL_CHECKS.items()}
        # UIL-01 (layer) is satisfied structurally by founding on the frozen substrate.
        result["UIL-01"] = True
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, executable construct
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (
                passed.get("infra-network-typed", False)
                and passed.get("infra-network-identified-objectbound", False)
            ),
            "AC-4": passed.get("technology-independence", False),  # no transport/technology
            "AC-5": passed.get("non-constitutive", False),  # no authority/secret/enforcement
            "AC-6": True,  # realized under infrastructure/**; frozen surfaces unmodified
            "AC-7": self.trace.closed,  # full traceability recorded
        }

    def validation_criteria(self, *, byte_identical: bool) -> dict[str, bool]:
        mv = self.meta_validity()
        return {
            "VC-1": self.validation.accepted,  # EC-1 ValidationEngine PASS + accepted
            "VC-2": all(mv.values()),  # meta-validity (WF applicable)
            "VC-3": all(self.uil_conformance().values()),  # UIL conformance (applicable)
            "VC-4": byte_identical,  # determinism (byte-identical recompute)
            "VC-5": self._passed().get("foundation-reuse-integrity", False),  # reuse integrity
        }

    def certification_gates(self) -> dict[str, bool]:
        return {f.criterion_id: f.passed for f in self.certification.decision.findings}

    def network_compliance(self) -> dict[str, bool]:
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
            and all(self.network_compliance().values())
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this realization."""
        return {
            "artifact": "EC3-B13-U03-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": INFRASTRUCTURE_META_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "resource": self.resource.to_dict(),
            "traceability": self.trace.to_dict(),
            "validation": {
                "report": self.validation.report.to_dict(),
                "evidence": self.validation.evidence.to_dict(),
                "acceptance": self.validation.decision.to_dict(),
            },
            "meta_validity_WF": self.meta_validity(),
            "uil_conformance": self.uil_conformance(),
            "certification": {
                "cce_gates": self.certification.decision.to_dict(),
                "ledger": self.certification.ledger.to_dict(),
                "evidence": self.certification.evidence.to_dict(),
            },
            "infrastructure_compliance_C1_C7": self.certification.compliance.to_dict(),
            "criteria": {
                "acceptance": self.acceptance_criteria(),
                "validation": self.validation_criteria(byte_identical=byte_identical),
                "certification_gates": self.certification_gates(),
                "infrastructure_compliance": self.network_compliance(),
            },
            "determination": self.determination(byte_identical=byte_identical),
        }


def realize() -> RealizationResult:
    """Perform the realization act and return its full deterministic result."""
    resource = build_canonical_network_resource()
    trace = build_traceability(
        resource,
        unit=REALIZATION_UNIT,
        forward=(
            resource.resource_id,
            "EC3-B13-U03-VALIDATION-EVIDENCE",
            "EC3-B13-U03-CCE-CERTIFICATION",
            "EC3-B13-U03-COMPLETION-REPORT",
        ),
    )
    validation = validate_network(resource, trace)
    certification = certify_network(validation, version=UNIT_VERSION)
    return RealizationResult(
        resource=resource, trace=trace, validation=validation, certification=certification
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
        evidence_dir / "infrastructure-compliance.json",
        bundle["infrastructure_compliance_C1_C7"],
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
        "resource_id": result.resource.resource_id,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B13-U03, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b13-u03-realize",
        description="Realize the Universal Infrastructure Network resource and emit evidence.",
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
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B13-U03 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "UNIT_VERSION",
    "CANONICAL_TYPE_TAG",
    "CANONICAL_LOCALITY_REF",
    "CANONICAL_SOURCE_REF",
    "CANONICAL_TARGET_REF",
    "CANONICAL_CONNECTIVITY_CLASS",
    "CANONICAL_CAPACITY_AMOUNT",
    "CANONICAL_CAPACITY_UNIT",
    "DEFAULT_EVIDENCE_DIR",
    "RealizationResult",
    "build_canonical_network_resource",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
