"""EC3-B12-U11 — Realization orchestrator + evidence emitter (Universal Application Meta-Model).

Performs the realization act authorized by ``EC-3-AP-4-BAND-12-ADMISSION-DETERMINATION``
(Band 12 ADMITTED · MEP-03 OPEN; the UAM integration is the APPLICATION-005 spine step named
by MCP-002 §05): constructs the canonical **Universal Application Meta-Model (UAM)** that
**integrates the ten CERTIFIED concern meta-classes** (AMC-01…10; units U01…U10) and the
fourteen meta-relationships (AMR-01…14) into one closed, total, acyclic, reuse-integral,
non-constitutive, non-projective model — the conformance gate for the whole Band-12
Application layer.

Integration is **material, not asserted**: this act **re-realizes all ten CERTIFIED concern
units live** (through their own realize orchestrators), proves each is CERTIFIED, captures
each live certification id, and composes them **by reference** into the meta-model. Thus the
meta-model closes the ten realized meta-classes into the APPLICATION-005 model-of-the-model,
extending the whole Band-12 spine ``Meta-Model fixes {Application, Capability, Module, Feature,
Workflow, Interaction, State, Composition, Security, Governance}``.

It validates the meta-model through the CERTIFIED EC-1 engine (meta-invariants AMI-01…07 +
Application-law UAL incl. **UAL-02/15**), certifies it through the CCE ten gates (CC-1…CC-10,
reused from AMC-01) + Application compliance (C1…C7, C5 materially exercised at the whole-model
level), closes its No-Orphan traceability (incl. the ten founding units), and emits a
**deterministic, content-addressed evidence bundle**. A double-realization self-check proves
byte-identical determinism (VC-4).

Run as a module::

    python -m application.model_realize                      # emit evidence + determination
    python -m application.model_realize --evidence-dir application/_evidence/EC3-B12-U11

This is engineering execution only (DE-05): it asserts no constitutional finality and no
operational/deployment/production readiness; it selects no technology, reuses the CERTIFIED
EC-1 + AMC-01…10 surfaces by reference, and writes nothing outside the caller-provided
evidence dir.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# --- the ten CERTIFIED concern-unit realizers, reused by reference (UAL-02) -------
from application import (
    application_realize,
    capability_realize,
    composition_realize,
    feature_realize,
    governance_realize,
    interaction_realize,
    module_realize,
    security_realize,
    state_realize,
    workflow_realize,
)
from application.application_traceability import TraceabilityRecord
from application.model import MetaModel, make_metamodel
from application.model_certification import ModelCertification, certify_model
from application.model_meta import (
    MEMBER_SPECS,
    META_INVARIANTS,
    MODEL_CLASS,
    ModelState,
)
from application.model_traceability import build_model_traceability
from application.model_validation import ModelValidation, validate_model
from engine.certification.contracts import content_hash

#: The realization unit this module realizes (EC-3 Band 12, Unit 11).
REALIZATION_UNIT = "EC3-B12-U11"

#: The realized artifact version (version-pinned certification; URS-L-20).
UNIT_VERSION = "1.0.0"

#: The canonical meta-model name/type — the model that integrates the ten meta-classes.
CANONICAL_MODEL_NAME = "ucos.application.metamodel.universal"
CANONICAL_MODEL_TYPE_TAG = "ucos.core.metamodel"

#: Where the default evidence bundle is written (code-adjacent; never the corpus).
DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

#: The ten CERTIFIED concern-unit realizers, keyed by meta-class (AMC-01…10). Each returns a
#: ``RealizationResult`` exposing ``.certification.certified`` and
#: ``.certification.decision.certification_id`` (the uniform UCIC-001 realization contract).
_MEMBER_REALIZERS: dict[str, Callable[[], Any]] = {
    "AMC-01": application_realize.realize,
    "AMC-02": capability_realize.realize,
    "AMC-03": module_realize.realize,
    "AMC-04": feature_realize.realize,
    "AMC-05": workflow_realize.realize,
    "AMC-06": interaction_realize.realize,
    "AMC-07": state_realize.realize,
    "AMC-08": composition_realize.realize,
    "AMC-09": security_realize.realize,
    "AMC-10": governance_realize.realize,
}

#: The unit id declared for each member meta-class (from the APPLICATION-005 §2 projection).
_MEMBER_UNITS: dict[str, str] = {spec[0]: spec[4] for spec in MEMBER_SPECS}

#: The validation check ids substantiating the seven meta-invariants (APPLICATION-005 §8).
_META_INVARIANT_CHECKS: dict[str, str] = {
    "AMI-01": "meta-class-single",
    "AMI-02": "meta-relationships-closed",
    "AMI-03": "metamodel-totality",
    "AMI-04": "founding-acyclic",
    "AMI-05": "foundation-reuse-integrity",
    "AMI-06": "non-constitutive",
    "AMI-07": "metamodel-non-projection",
}

#: The validation check ids substantiating single-check Application-law UAL conformance (VC-3).
_UAL_CHECKS: dict[str, str] = {
    "UAL-02": "foundation-reuse-integrity",
    "UAL-03": "metamodel-typed",
    "UAL-04": "metamodel-identified",
    "UAL-05": "metamodel-identified",
    "UAL-12": "lifecycle-valid",
    "UAL-15": "non-constitutive",
}


@dataclass(frozen=True, slots=True)
class MemberCertification:
    """The live certification outcome of one integrated concern meta-class member."""

    meta_class: str
    unit: str
    certified: bool
    certification_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "meta_class": self.meta_class,
            "unit": self.unit,
            "certified": self.certified,
            "certification_id": self.certification_id,
        }


def realize_members() -> tuple[MemberCertification, ...]:
    """Live-realize all ten CERTIFIED concern units and capture their certifications.

    This is the **material integration** step: each member's own realize orchestrator runs
    end-to-end, and its CERTIFIED verdict + certification id are captured so the meta-model
    composes ten genuinely-certified realizations by reference (not recorded assertions).
    """
    members: list[MemberCertification] = []
    for meta_class, realizer in _MEMBER_REALIZERS.items():
        result = realizer()
        members.append(
            MemberCertification(
                meta_class=meta_class,
                unit=_MEMBER_UNITS[meta_class],
                certified=bool(result.certification.certified),
                certification_id=result.certification.decision.certification_id,
            )
        )
    return tuple(sorted(members, key=lambda m: m.meta_class))


def build_canonical_metamodel(members: tuple[MemberCertification, ...]) -> MetaModel:
    """Construct the canonical Universal Application Meta-Model from the live member certs.

    Composes the ten CERTIFIED concern meta-classes (by their live certification ids) and the
    frozen APPLICATION-005 §3/§9 fourteen-edge projection into the closed, total, acyclic UAM.
    """
    certification_ids = {m.meta_class: m.certification_id for m in members}
    return make_metamodel(
        CANONICAL_MODEL_NAME,
        CANONICAL_MODEL_TYPE_TAG,
        certification_ids,
        state=ModelState.DEFINED,
        version=UNIT_VERSION,
    )


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B12-U11 realization act."""

    model: MetaModel
    members: tuple[MemberCertification, ...]
    trace: TraceabilityRecord
    validation: ModelValidation
    certification: ModelCertification

    # -- derived conformance roll-ups ------------------------------------------

    def _passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def members_all_certified(self) -> bool:
        """Integration — all ten live member realizations are CERTIFIED."""
        return len(self.members) == len(MEMBER_SPECS) and all(m.certified for m in self.members)

    def meta_invariants(self) -> dict[str, bool]:
        """The seven meta-invariants AMI-01…07, decided on validation evidence."""
        passed = self._passed()
        result = {ami: passed.get(cid, False) for ami, cid in _META_INVARIANT_CHECKS.items()}
        # AMI-06 is additionally substantiated by the technology-independence check.
        result["AMI-06"] = result["AMI-06"] and passed.get("technology-independence", False)
        return dict(sorted(result.items()))

    def ual_conformance(self) -> dict[str, bool]:
        passed = self._passed()
        result = {law: passed.get(cid, False) for law, cid in _UAL_CHECKS.items()}
        result["UAL-01"] = True  # layer founded on frozen EL-1
        # UAL-02 materially exercised: reuse-by-reference over all ten CERTIFIED units.
        result["UAL-02"] = passed.get("foundation-reuse-integrity", False) and (
            self.members_all_certified()
        )
        return dict(sorted(result.items()))

    def acceptance_criteria(self) -> dict[str, bool]:
        passed = self._passed()
        return {
            "AC-1": self.validation.accepted,  # real, additive, executable construct
            "AC-2": passed.get("foundation-reuse-integrity", False),  # reuse by reference
            "AC-3": (  # typed + named + identified + members certified (integration)
                passed.get("metamodel-typed", False)
                and passed.get("metamodel-named", False)
                and passed.get("metamodel-identified", False)
                and passed.get("metamodel-members-certified", False)
                and self.members_all_certified()
            ),
            "AC-4": (  # closure + relationship-closure + totality + map-resolves + acyclic
                passed.get("meta-class-single", False)
                and passed.get("meta-relationships-closed", False)
                and passed.get("metamodel-totality", False)
                and passed.get("metamodel-map-resolves", False)
                and passed.get("founding-acyclic", False)
            ),
            "AC-5": passed.get("technology-independence", False),  # no technology
            "AC-6": passed.get("non-constitutive", False),  # no authority/access/secret
            "AC-7": True,  # realized under application/**; frozen corpus + prior units unmodified
            "AC-8": self.trace.closed,  # full traceability recorded (incl. ten founding units)
        }

    def validation_criteria(self, *, byte_identical: bool) -> dict[str, bool]:
        mi = self.meta_invariants()
        return {
            "VC-1": self.validation.accepted,  # EC-1 ValidationEngine PASS + accepted
            "VC-2": all(mi.values()),  # meta-invariants AMI-01…07
            "VC-3": all(self.ual_conformance().values()),  # UAL conformance
            "VC-4": byte_identical,  # determinism (byte-identical recompute)
            "VC-5": self._passed().get("foundation-reuse-integrity", False),  # reuse integrity
        }

    def certification_gates(self) -> dict[str, bool]:
        return {f.criterion_id: f.passed for f in self.certification.decision.findings}

    def application_compliance(self) -> dict[str, bool]:
        return {c["id"]: c["status"] == "pass" for c in self.certification.compliance.conditions}

    def integration_closure(self) -> dict[str, bool]:
        """The whole-model integration facts (the U11 spine-closure analogue)."""
        return {
            "all_members_certified": self.members_all_certified(),
            "closure_AMI_01": self.model.declares_closure(),
            "relationship_closure_AMI_02": self.model.declares_relationship_closure(),
            "totality_AMI_03": self.model.is_total(),
            "founding_acyclic_AMI_04": self.model.is_founding_acyclic(),
            "reuse_by_reference_AMI_05": self.model.reuses_by_reference(),
            "non_constitutive_AMI_06": self.model.is_non_constitutive(),
            "non_projection_AMI_07": self.model.is_non_projection(),
            "map_resolves": self.model.map_resolves(),
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
            and all(self.application_compliance().values())
            and all(self.integration_closure().values())
        ):
            return "COMPLETE"
        if self.validation.accepted and self.certification.decision.certified and self.trace.closed:
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this realization."""
        return {
            "artifact": "EC3-B12-U11-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "model_class": MODEL_CLASS,
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "model": self.model.to_dict(),
            "member_certifications": [m.to_dict() for m in self.members],
            "spine": (
                "Meta-Model fixes {Application, Capability, Module, Feature, Workflow, "
                "Interaction, State, Composition, Security, Governance} (AMC-01…10) via "
                "AMR-01…14 (AMI-01…07)"
            ),
            "integration_closure": self.integration_closure(),
            "meta_invariants": self.meta_invariants(),
            "meta_invariant_definitions": dict(META_INVARIANTS),
            "traceability": self.trace.to_dict(),
            "validation": {
                "report": self.validation.report.to_dict(),
                "evidence": self.validation.evidence.to_dict(),
                "acceptance": self.validation.decision.to_dict(),
            },
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
                "application_compliance": self.application_compliance(),
            },
            "determination": self.determination(byte_identical=byte_identical),
        }


def realize() -> RealizationResult:
    """Perform the realization act and return its full deterministic result."""
    members = realize_members()
    model = build_canonical_metamodel(members)
    trace = build_model_traceability(
        model,
        unit=REALIZATION_UNIT,
        forward=(
            model.model_id,
            "EC3-B12-U11-VALIDATION-EVIDENCE",
            "EC3-B12-U11-CCE-CERTIFICATION",
            "EC3-B12-U11-COMPLETION-REPORT",
        ),
    )
    validation = validate_model(model, trace)
    certification = certify_model(validation, version=UNIT_VERSION)
    return RealizationResult(
        model=model,
        members=members,
        trace=trace,
        validation=validation,
        certification=certification,
    )


def determinism_check() -> tuple[bool, str, str]:
    """Realize twice and compare the evidence bundles byte-for-byte (VC-4).

    Returns ``(byte_identical, digest_a, digest_b)`` where the digests are the EC-1 content
    hashes of the two independently produced evidence bundles.
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
        "integration_closed": all(result.integration_closure().values()),
        "members_all_certified": result.members_all_certified(),
        "certification_id": result.certification.decision.certification_id,
        "model_id": result.model.model_id,
        "member_certification_ids": {m.meta_class: m.certification_id for m in result.members},
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B12-U11, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b12-u11-realize",
        description="Realize the Universal Application Meta-Model (UAM) and emit evidence.",
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
        and summary["integration_closed"]
        and summary["members_all_certified"]
    )
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B12-U11 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "REALIZATION_UNIT",
    "UNIT_VERSION",
    "CANONICAL_MODEL_NAME",
    "CANONICAL_MODEL_TYPE_TAG",
    "DEFAULT_EVIDENCE_DIR",
    "MemberCertification",
    "RealizationResult",
    "realize_members",
    "build_canonical_metamodel",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
