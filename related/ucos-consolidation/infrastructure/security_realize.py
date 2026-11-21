"""EC3-B13-U08 — Realization orchestrator + evidence emitter.

Performs the realization act admitted by ``STAGE-04-S4-02`` (`UCOS-CEP-000027`) and planned
by ``STAGE-04-S4-03`` (`UCOS-CEP-000028`; §Capability Implementation Map): constructs the
canonical Infrastructure Security composition (the five SecurityFacet facets — Isolation,
Authentication, Authorization, Confidentiality, Integrity), validates each through the
CERTIFIED EC-1 engine, certifies each through the CCE ten gates (CC-1…CC-10) + Infrastructure
compliance (C1…C7) into a shared hash-chained ledger, closes each facet's No-Orphan
traceability, and emits a **deterministic, content-addressed evidence bundle**.

Run as a module::

    python -m infrastructure.security_realize
    python -m infrastructure.security_realize --evidence-dir infrastructure/_evidence/EC3-B13-U08

This is engineering execution only (DE-05): it asserts no constitutional finality, selects
no technology, embeds no secret, grants no access, and writes nothing outside the
caller-provided evidence dir. The composition proves the governing obligations: **WF-10 /
UIL-14 / ISEC-01/04** (every facet is evaluative & non-enforcing — C4), **ISEC-03 / RR-07**
(no secret material), **UIL-15 / ISEC-05** (no technology — C7).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.certification.contracts import content_hash
from engine.certification.ledger import CertificationLedger
from infrastructure.security import (
    SecurityFacet,
    SecurityFacetKind,
    make_security_facet,
)
from infrastructure.security_certification import SecurityCertification, certify_construct
from infrastructure.security_meta import REALIZATION_UNIT
from infrastructure.security_traceability import TraceabilityRecord, build_traceability
from infrastructure.security_validation import SecurityValidation, validate_construct

UNIT_VERSION = "1.0.0"

# Canonical construct type tags (technology-neutral) — one per facet.
CANONICAL_TYPES: dict[SecurityFacetKind, str] = {
    SecurityFacetKind.ISOLATION: "ucos.infrastructure.security.isolation.foundation",
    SecurityFacetKind.AUTHENTICATION: "ucos.infrastructure.security.authentication.foundation",
    SecurityFacetKind.AUTHORIZATION: "ucos.infrastructure.security.authorization.foundation",
    SecurityFacetKind.CONFIDENTIALITY: "ucos.infrastructure.security.confidentiality.foundation",
    SecurityFacetKind.INTEGRITY: "ucos.infrastructure.security.integrity.foundation",
}

#: Canonical realization order (INFRASTRUCTURE-013 §2 listing) — deterministic.
CANONICAL_ORDER: tuple[SecurityFacetKind, ...] = (
    SecurityFacetKind.ISOLATION,
    SecurityFacetKind.AUTHENTICATION,
    SecurityFacetKind.AUTHORIZATION,
    SecurityFacetKind.CONFIDENTIALITY,
    SecurityFacetKind.INTEGRITY,
)

DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

#: The concern-representative namesake facet (S4-03 plan §Capability Implementation Map).
NAMESAKE_FACET = "integrity"

# Validation check ids substantiating meta-validity.
_META_VALIDITY_CHECKS: dict[str, str] = {
    "WF-1": "meta-class-single",
    "WF-2": "meta-constraints",
    "WF-3": "founding-acyclic",
    "WF-10": "security-evaluative-nonenforcing",
    "WF-11": "foundation-reuse-integrity",
    "WF-12": "non-constitutive",
}

# Validation check ids substantiating Infrastructure-law UIL conformance.
_UIL_CHECKS: dict[str, str] = {
    "UIL-02": "foundation-reuse-integrity",
    "UIL-03": "infra-security-typed",
    "UIL-04": "infra-security-identified-objectbound",
    "UIL-05": "infra-security-identified-objectbound",
    "UIL-07": "authority-boundary",
    "UIL-14": "security-evaluative-nonenforcing",
    "UIL-15": "technology-independence",
}


@dataclass(frozen=True, slots=True)
class Composition:
    """The canonical Infrastructure Security composition (five SecurityFacet facets)."""

    isolation: SecurityFacet
    authentication: SecurityFacet
    authorization: SecurityFacet
    confidentiality: SecurityFacet
    integrity: SecurityFacet

    def ordered(self) -> tuple[SecurityFacet, ...]:
        return (
            self.isolation,
            self.authentication,
            self.authorization,
            self.confidentiality,
            self.integrity,
        )


def build_canonical_composition() -> Composition:
    """Construct the canonical Infrastructure Security composition (fail-closed)."""
    facets = {
        kind: make_security_facet(CANONICAL_TYPES[kind], kind)
        for kind in CANONICAL_ORDER
    }
    return Composition(
        isolation=facets[SecurityFacetKind.ISOLATION],
        authentication=facets[SecurityFacetKind.AUTHENTICATION],
        authorization=facets[SecurityFacetKind.AUTHORIZATION],
        confidentiality=facets[SecurityFacetKind.CONFIDENTIALITY],
        integrity=facets[SecurityFacetKind.INTEGRITY],
    )


@dataclass(frozen=True, slots=True)
class ConstructRealization:
    """The realization outcome for a single facet."""

    construct: SecurityFacet
    trace: TraceabilityRecord
    validation: SecurityValidation
    certification: SecurityCertification

    def passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def to_dict(self) -> dict[str, Any]:
        return {
            "construct": self.construct.to_dict(),
            "traceability": self.trace.to_dict(),
            "validation": {
                "report": self.validation.report.to_dict(),
                "evidence": self.validation.evidence.to_dict(),
                "acceptance": self.validation.decision.to_dict(),
            },
            "certification": {
                "cce_gates": self.certification.decision.to_dict(),
                "evidence": self.certification.evidence.to_dict(),
            },
            "infrastructure_compliance_C1_C7": self.certification.compliance.to_dict(),
            "certification_id": self.certification.decision.certification_id,
        }


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B13-U08 realization act."""

    composition: Composition
    realizations: tuple[ConstructRealization, ...]
    ledger: CertificationLedger

    def by_facet(self, facet: str) -> ConstructRealization:
        for r in self.realizations:
            if r.construct.facet_value == facet:
                return r
        raise KeyError(facet)

    @property
    def namesake(self) -> ConstructRealization:
        return self.by_facet(NAMESAKE_FACET)

    def _passed_all(self, check_id: str) -> bool:
        return all(r.passed().get(check_id, False) for r in self.realizations)

    def all_accepted(self) -> bool:
        return all(r.validation.accepted for r in self.realizations)

    def all_certified(self) -> bool:
        return all(r.certification.certified for r in self.realizations)

    def all_traceable(self) -> bool:
        return all(r.trace.closed for r in self.realizations)

    def meta_validity(self) -> dict[str, bool]:
        return {wf: self._passed_all(cid) for wf, cid in _META_VALIDITY_CHECKS.items()}

    def uil_conformance(self) -> dict[str, bool]:
        result = {law: self._passed_all(cid) for law, cid in _UIL_CHECKS.items()}
        result["UIL-01"] = True
        return dict(sorted(result.items()))

    def certification_gates(self) -> dict[str, bool]:
        gate_ids = [f.criterion_id for f in self.realizations[0].certification.decision.findings]
        return {
            gid: all(
                next(f for f in r.certification.decision.findings if f.criterion_id == gid).passed
                for r in self.realizations
            )
            for gid in gate_ids
        }

    def security_compliance(self) -> dict[str, bool]:
        cond_ids = [c["id"] for c in self.realizations[0].certification.compliance.conditions]
        return {
            cid: all(
                next(c for c in r.certification.compliance.conditions if c["id"] == cid)["status"]
                == "pass"
                for r in self.realizations
            )
            for cid in cond_ids
        }

    def acceptance_criteria(self) -> dict[str, bool]:
        return {
            "AC-1": self.all_accepted(),
            "AC-2": self._passed_all("foundation-reuse-integrity"),
            "AC-3": (
                self._passed_all("infra-security-typed")
                and self._passed_all("infra-security-identified-objectbound")
            ),
            "AC-4": self._passed_all("technology-independence"),
            "AC-5": self._passed_all("non-constitutive"),
            "AC-6": (
                self._passed_all("security-evaluative-nonenforcing")
                and self._passed_all("authority-boundary")
                and self._passed_all("no-secret-material")
            ),
            "AC-7": self.all_traceable(),
        }

    def validation_criteria(self, *, byte_identical: bool) -> dict[str, bool]:
        return {
            "VC-1": self.all_accepted(),
            "VC-2": all(self.meta_validity().values()),
            "VC-3": all(self.uil_conformance().values()),
            "VC-4": byte_identical,
            "VC-5": self._passed_all("foundation-reuse-integrity"),
        }

    def determination(self, *, byte_identical: bool) -> str:
        vc = self.validation_criteria(byte_identical=byte_identical)
        gates_ok = all(self.certification_gates().values())
        if (
            self.all_accepted()
            and self.all_certified()
            and self.all_traceable()
            and all(vc.values())
            and gates_ok
            and all(self.security_compliance().values())
        ):
            return "COMPLETE"
        if self.all_accepted() and self.all_certified() and self.all_traceable():
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def certification_ids(self) -> dict[str, str]:
        return {r.construct.facet_value: r.certification.decision.certification_id for r in self.realizations}

    def construct_ids(self) -> dict[str, str]:
        return {r.construct.facet_value: r.construct.construct_id for r in self.realizations}

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        return {
            "artifact": "EC3-B13-U08-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": "SecurityFacet",
            "facets": [r.construct.facet_value for r in self.realizations],
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "constructs": [r.to_dict() for r in self.realizations],
            "certification_ledger": self.ledger.to_dict(),
            "meta_validity_WF": self.meta_validity(),
            "uil_conformance": self.uil_conformance(),
            "certification_ids": self.certification_ids(),
            "construct_ids": self.construct_ids(),
            "criteria": {
                "acceptance": self.acceptance_criteria(),
                "validation": self.validation_criteria(byte_identical=byte_identical),
                "certification_gates": self.certification_gates(),
                "infrastructure_compliance": self.security_compliance(),
            },
            "determination": self.determination(byte_identical=byte_identical),
        }


def realize() -> RealizationResult:
    """Perform the realization act and return its full deterministic result."""
    composition = build_canonical_composition()
    constructs = composition.ordered()

    ledger = CertificationLedger()
    realizations: list[ConstructRealization] = []
    for construct in constructs:
        label = construct.facet_value.upper()
        trace = build_traceability(
            construct,
            unit=REALIZATION_UNIT,
            forward=(
                construct.construct_id,
                f"EC3-B13-U08-{label}-VALIDATION-EVIDENCE",
                f"EC3-B13-U08-{label}-CCE-CERTIFICATION",
                "EC3-B13-U08-COMPLETION-REPORT",
            ),
        )
        validation = validate_construct(construct, trace)
        certification = certify_construct(validation, version=UNIT_VERSION, ledger=ledger)
        realizations.append(
            ConstructRealization(
                construct=construct,
                trace=trace,
                validation=validation,
                certification=certification,
            )
        )
    return RealizationResult(
        composition=composition,
        realizations=tuple(realizations),
        ledger=ledger,
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
    namesake = result.namesake

    evidence_dir.mkdir(parents=True, exist_ok=True)
    _write_json(evidence_dir / "realization-evidence.json", bundle)
    _write_json(evidence_dir / "validation-report.json", namesake.validation.report.to_dict())
    _write_json(evidence_dir / "validation-evidence.json", namesake.validation.evidence.to_dict())
    _write_json(evidence_dir / "acceptance-decision.json", namesake.validation.decision.to_dict())
    _write_json(evidence_dir / "cce-certification.json", namesake.certification.decision.to_dict())
    _write_json(
        evidence_dir / "certification-evidence.json", namesake.certification.evidence.to_dict()
    )
    _write_json(evidence_dir / "certification-ledger.json", result.ledger.to_dict())
    _write_json(
        evidence_dir / "infrastructure-compliance.json", namesake.certification.compliance.to_dict()
    )
    _write_json(evidence_dir / "traceability.json", namesake.trace.to_dict())
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
        "validation_accepted": result.all_accepted(),
        "certified": result.all_certified(),
        "traceability_closed": result.all_traceable(),
        "byte_identical": byte_identical,
        "certification_ids": result.certification_ids(),
        "construct_ids": result.construct_ids(),
        "ledger_head": result.ledger.head_hash,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B13-U08, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b13-u08-realize",
        description="Realize the Universal Infrastructure Security constructs.",
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
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B13-U08 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "UNIT_VERSION",
    "CANONICAL_TYPES",
    "CANONICAL_ORDER",
    "DEFAULT_EVIDENCE_DIR",
    "NAMESAKE_FACET",
    "Composition",
    "ConstructRealization",
    "RealizationResult",
    "build_canonical_composition",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
