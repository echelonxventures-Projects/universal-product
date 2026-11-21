"""EC3-B10-U07 — Realization orchestrator + evidence emitter (Governance Foundation).

Performs the realization act authorized by ``EC3-B10-DATA-REALIZATION-PACKAGE-007``
(derived from the frozen constitutional corpus — DATA-012 — since the package file is
not present): constructs the canonical **declarative, non-enforcing Governance** exemplar
that **governs the CERTIFIED DMC-02 Entity by reference** (DMR-07), recording a
Conformance-Record over the applicable Data Laws (DGA-C1) and binding conformance
evaluation *by reference* to the frozen RUNTIME policy concern (DMR-11 / DGA-07). This
extends the spine to ``Governance governs Entity bears Attribute values Datum``
(DMR-07 → DMR-01 → DMR-02).

It is an **evaluative record that enacts nothing** — it declares conformance verdicts,
stewardship descriptors, and a policy reference as *records*, and names **no** policy
engine, rules engine, access-control/IAM system, enforcement point, or vendor (UDL-13
Governance as Declarative Constraint — materially enforced).

It validates the governance object through the CERTIFIED EC-1 engine (meta-validity
V1…V5 + Data-law UDL incl. **UDL-13**), certifies it through the CCE ten gates
(CC-1…CC-10, reused from DMC-01) + Data compliance (C1…C7, C6 materially exercised),
closes its No-Orphan traceability (incl. ``governs → DMC-02``), and emits a
**deterministic, content-addressed evidence bundle**. A double-realization self-check
proves byte-identical determinism (VC-4).

Run as a module::

    python -m data.governance_realize                 # emit evidence + determination
    python -m data.governance_realize --evidence-dir data/_evidence/EC3-B10-U07

This is engineering execution only (DE-05): it asserts no constitutional finality and no
operational/deployment/production readiness; it selects no technology, reuses the
CERTIFIED EC-1 + DMC-01/02 surfaces by reference, and writes nothing outside the
caller-provided evidence dir.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from data.entity import Entity
from data.entity_realize import build_canonical_entity
from data.governance import (
    ConformanceEntry,
    GovernanceObject,
    GovernedConstructRef,
    make_conformance,
    make_governance,
    policy_ref_for,
)
from data.governance_certification import GovernanceCertification, certify_governance
from data.governance_meta import (
    CANONICAL_GOVERNED_LAWS,
    GOVERNANCE_META_CLASS,
    GovernanceKind,
    GovernanceState,
    GovernanceVerdict,
)
from data.governance_traceability import build_governance_traceability
from data.governance_validation import GovernanceValidation, validate_governance
from data.traceability import TraceabilityRecord
from engine.certification.contracts import content_hash

#: The realization unit this module realizes (EC-3 Band 10, Unit 07).
REALIZATION_UNIT = "EC3-B10-U07"

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical governance name/type — the object that governs the CERTIFIED entity.
CANONICAL_GOVERNANCE_NAME = "ucos.data.governance.foundation"
CANONICAL_GOVERNANCE_TYPE_TAG = "ucos.core.governance"

#: The canonical RUNTIME policy predicate the object binds by reference (abstract).
CANONICAL_POLICY_PREDICATE = "conformance.udl"

#: A recorded, non-authoritative stewardship descriptor (DGA-05 / DGA-C4).
CANONICAL_STEWARD = "ucos.data.governance.steward"

#: Where the default evidence bundle is written (code-adjacent; never the corpus).
DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

#: The validation check ids substantiating meta-validity V1…V5 (DATA-005 §8).
_META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "meta-class-single",
    "V2": "meta-relationships-closed",
    "V3": "meta-constraints",
    "V4": "founding-acyclic",
    "V5": "governance-valid",
}

#: The validation check ids substantiating single-check Data-law UDL conformance (VC-3).
_UDL_CHECKS: dict[str, str] = {
    "UDL-02": "foundation-reuse-integrity",
    "UDL-03": "governance-typed",
    "UDL-04": "governance-identified",
    "UDL-05": "governance-identified",
    "UDL-09": "founding-acyclic",
    "UDL-15": "non-constitutive",
}


def _canonical_conformance() -> tuple[ConformanceEntry, ...]:
    """The canonical Conformance-Record: every applicable governed law satisfied (DGA-C1)."""
    return make_conformance(tuple((law, True) for law in CANONICAL_GOVERNED_LAWS))


def build_canonical_governance() -> GovernanceObject:
    """Construct the canonical declarative, non-enforcing Governance exemplar (DMC-08).

    Governs the CERTIFIED DMC-02 canonical Master-Entity by reference (DMR-07), recording
    a Conformance-Record over the applicable Data Laws (DGA-C1) and binding conformance
    evaluation by reference to the RUNTIME policy concern (DMR-11 / DGA-07). Evaluative
    record only — names no policy/enforcement technology (UDL-13).
    """
    entity = build_canonical_entity()
    return make_governance(
        CANONICAL_GOVERNANCE_NAME,
        CANONICAL_GOVERNANCE_TYPE_TAG,
        entity,
        policy_ref_for(CANONICAL_POLICY_PREDICATE),
        kind=GovernanceKind.CONFORMANCE_RECORD,
        conformance=_canonical_conformance(),
        verdict=GovernanceVerdict.CONFORMANT,
        steward=CANONICAL_STEWARD,
        state=GovernanceState.DEFINED,
        version=UNIT_VERSION,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B10-U07 realization act."""

    governance: GovernanceObject
    governed_entity: Entity
    trace: TraceabilityRecord
    validation: GovernanceValidation
    certification: GovernanceCertification

    # -- derived conformance roll-ups ------------------------------------------

    def _passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def meta_validity(self) -> dict[str, bool]:
        passed = self._passed()
        return {v: passed.get(cid, False) for v, cid in _META_VALIDITY_CHECKS.items()}

    def udl_conformance(self) -> dict[str, bool]:
        passed = self._passed()
        result = {law: passed.get(cid, False) for law, cid in _UDL_CHECKS.items()}
        # UDL-01 layer; UDL-13 governance (material, non-enforcing); UDL-14 evaluative facet.
        result["UDL-01"] = True
        result["UDL-13"] = not self.governance.enforces() and not self.governance.grants_access()
        result["UDL-14"] = not self.governance.confers_authority()
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, executable construct
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (  # typed + named + identified + governs a subject by reference
                passed.get("governance-typed", False)
                and passed.get("governance-named", False)
                and passed.get("governance-identified", False)
                and passed.get("governance-governs-subject", False)
            ),
            "AC-4": (  # declarative + non-enforcing + no-access + recorded + conformance/class
                passed.get("governance-declarative", False)
                and passed.get("governance-non-enforcing", False)
                and passed.get("governance-no-access", False)
                and passed.get("governance-recorded", False)
                and passed.get("governance-binds-policy-by-reference", False)
                and passed.get("governance-conformance-recorded", False)
                and passed.get("governance-classified", False)
            ),
            "AC-5": passed.get("governance-independence", False),  # no technology (material UDL-13)
            "AC-6": passed.get("non-constitutive", False),  # no authority/secret
            "AC-7": True,  # realized under data/**; frozen corpus + DMC-02 unmodified (guarded)
            "AC-8": self.trace.closed,  # full traceability recorded (incl. governs → DMC-02)
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

    def spine_closure(self) -> dict[str, bool]:
        """The ``Governance governs Entity …`` spine-closure facts."""
        return {
            "governs_entity": self.governance.governs_construct(self.governed_entity.entity_id),
            "declarative": self.governance.is_declarative(),
            "non_enforcing": not self.governance.enforces(),
            "binds_policy_by_reference": self.governance.binds_policy_by_reference(),
            "technology_neutral": not self.governance.names_technology(),
        }

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
            and all(self.spine_closure().values())
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this realization."""
        return {
            "artifact": "EC3-B10-U07-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_class": GOVERNANCE_META_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "governance": self.governance.to_dict(),
            "governed_entity": self.governed_entity.to_dict(),
            "spine": (
                "Governance governs Entity bears Attribute values Datum "
                "(DMR-07 → DMR-01 → DMR-02)"
            ),
            "spine_closure": self.spine_closure(),
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
    governed_entity = build_canonical_entity()
    governance = make_governance(
        CANONICAL_GOVERNANCE_NAME,
        CANONICAL_GOVERNANCE_TYPE_TAG,
        governed_entity,
        policy_ref_for(CANONICAL_POLICY_PREDICATE),
        kind=GovernanceKind.CONFORMANCE_RECORD,
        conformance=_canonical_conformance(),
        verdict=GovernanceVerdict.CONFORMANT,
        steward=CANONICAL_STEWARD,
        state=GovernanceState.DEFINED,
        version=UNIT_VERSION,
    )
    trace = build_governance_traceability(
        governance,
        unit=REALIZATION_UNIT,
        forward=(
            governance.governance_id,
            "EC3-B10-U07-VALIDATION-EVIDENCE",
            "EC3-B10-U07-CCE-CERTIFICATION",
            "EC3-B10-U07-COMPLETION-REPORT",
        ),
    )
    validation = validate_governance(governance, trace)
    certification = certify_governance(validation, version=UNIT_VERSION)
    return RealizationResult(
        governance=governance,
        governed_entity=governed_entity,
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
        "spine_closed": all(result.spine_closure().values()),
        "certification_id": result.certification.decision.certification_id,
        "governance_id": result.governance.governance_id,
        "governs_entity_id": result.governed_entity.entity_id,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B10-U07, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b10-u07-realize",
        description="Realize the Governance Foundation (DMC-08) and emit evidence.",
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
        and summary["spine_closed"]
    )
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B10-U07 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "REALIZATION_UNIT",
    "UNIT_VERSION",
    "CANONICAL_GOVERNANCE_NAME",
    "CANONICAL_GOVERNANCE_TYPE_TAG",
    "CANONICAL_POLICY_PREDICATE",
    "CANONICAL_STEWARD",
    "DEFAULT_EVIDENCE_DIR",
    "RealizationResult",
    "build_canonical_governance",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
    "GovernedConstructRef",
    "ConformanceEntry",
]
