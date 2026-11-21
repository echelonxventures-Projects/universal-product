"""URI-000001 — the consolidated evidence bundle.

Evidence is fail-closed under TRACK-001: absence of a required artifact means NOT-DONE, and
no self-attestation substitutes for a physical file. This module emits the eight documents
that constitute proof a realization actually happened, each independently sealed, plus an
evidence record whose hash covers all of them.

Bundle (UCIC-001 Output 5 binding — ``data/_evidence/<CAP-ID>/``):

===================================  ==========================================
``realization-intake.json``          the canonical knowledge state realized from
``realization-plan.json``            the derived, waved, acyclic plan
``realization-composition.json``     composed units, bindings, findings
``realization-generation.json``      the generation manifest (paths + hashes)
``realization-implementation.json``  what was written, and what verified
``realization-governance.json``      the twelve-gate decision
``realization-traceability.json``    the closure ledger both directions
``realization-determinism.json``     the byte-identity proof
``realization-evidence-record.json`` the record sealing all of the above
===================================  ==========================================

No document reads a clock. The bundle's identity is the knowledge seal it was derived
from, so two runs over identical canonical knowledge produce byte-identical evidence.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.foundation.guards.frozen_paths import find_frozen_writes
from engine.foundation.obs.logging import get_logger
from intelligence.realization.canonical import (
    content_hash,
    document_json,
    sealed,
    short_seal,
    verify_seal,
)
from intelligence.realization.composition import CompositionFindings
from intelligence.realization.config import CAPABILITY_ID, RealizationConfig
from intelligence.realization.contracts import (
    DERIVED_AUTHORITY,
    GenerationManifest,
    ImplementationRecord,
    RealizationComposition,
    RealizationPlan,
)
from intelligence.realization.errors import EvidenceError
from intelligence.realization.generators import registry_manifest
from intelligence.realization.governance import RealizationDecision
from intelligence.realization.knowledge import KnowledgeIntake
from intelligence.realization.traceability import TraceLedger, coverage_summary

_logger = get_logger("intelligence.realization.evidence")

EVIDENCE_FORMAT = "ucos-uri-evidence/1.0.0"

INTAKE_FILE = "realization-intake.json"
PLAN_FILE = "realization-plan.json"
COMPOSITION_FILE = "realization-composition.json"
GENERATION_FILE = "realization-generation.json"
IMPLEMENTATION_FILE = "realization-implementation.json"
GOVERNANCE_FILE = "realization-governance.json"
TRACEABILITY_FILE = "realization-traceability.json"
DETERMINISM_FILE = "realization-determinism.json"
RECORD_FILE = "realization-evidence-record.json"

#: Every document the bundle must contain. A missing entry is NOT-DONE (TRACK-001).
REQUIRED_FILES: tuple[str, ...] = (
    INTAKE_FILE,
    PLAN_FILE,
    COMPOSITION_FILE,
    GENERATION_FILE,
    IMPLEMENTATION_FILE,
    GOVERNANCE_FILE,
    TRACEABILITY_FILE,
    DETERMINISM_FILE,
    RECORD_FILE,
)


def _envelope(artifact_id: str, title: str, knowledge_seal: str) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "title": title,
        "document_format": EVIDENCE_FORMAT,
        "capability": CAPABILITY_ID,
        "authority": DERIVED_AUTHORITY,
        "knowledge_seal": knowledge_seal,
    }


@dataclass(frozen=True, slots=True)
class RealizationEvidence:
    """The complete, sealed evidence bundle as in-memory documents."""

    knowledge_seal: str
    documents: Mapping[str, dict[str, Any]]

    @property
    def evidence_id(self) -> str:
        return f"URI-EVD-{short_seal(self.record_hash)}"

    @property
    def record_hash(self) -> str:
        return content_hash({name: self.documents[name] for name in sorted(self.documents)})

    def missing(self) -> tuple[str, ...]:
        return tuple(name for name in REQUIRED_FILES if name not in self.documents)

    def complete(self) -> bool:
        return not self.missing()


def build_evidence(
    *,
    intake: KnowledgeIntake,
    plan: RealizationPlan,
    composition: RealizationComposition,
    findings: CompositionFindings,
    manifest: GenerationManifest,
    decision: RealizationDecision,
    ledger: TraceLedger,
    determinism: Mapping[str, Any],
    record: ImplementationRecord | None = None,
) -> RealizationEvidence:
    """Assemble the evidence bundle from the stage outputs. Reads no clock, writes nothing."""
    seal = intake.knowledge_seal
    documents: dict[str, dict[str, Any]] = {}

    documents[INTAKE_FILE] = sealed(
        {
            **_envelope("UCOS-URI-INTAKE", "Canonical Knowledge Intake", seal),
            "intake": intake.to_dict(),
        }
    )
    documents[PLAN_FILE] = sealed(
        {
            **_envelope("UCOS-URI-PLAN", "Realization Plan", seal),
            "plan": plan.to_dict(),
        }
    )
    documents[COMPOSITION_FILE] = sealed(
        {
            **_envelope("UCOS-URI-COMPOSITION", "Realization Composition", seal),
            "composition": composition.to_dict(),
            "findings": findings.to_dict(),
        }
    )
    documents[GENERATION_FILE] = sealed(
        {
            **_envelope("UCOS-URI-GENERATION", "Generation Manifest", seal),
            "generation": manifest.to_dict(),
            "generators": registry_manifest(),
        }
    )
    documents[IMPLEMENTATION_FILE] = sealed(
        {
            **_envelope("UCOS-URI-IMPLEMENTATION", "Implementation Record", seal),
            "implementation": record.to_dict()
            if record is not None
            else {"materialized": False, "reason": "no materialization pass was run"},
        }
    )
    documents[GOVERNANCE_FILE] = sealed(
        {
            **_envelope("UCOS-URI-GOVERNANCE", "Realization Governance Decision", seal),
            "decision": decision.to_dict(),
        }
    )
    documents[TRACEABILITY_FILE] = sealed(
        {
            **_envelope("UCOS-URI-TRACEABILITY", "Realization Traceability Closure", seal),
            "traceability": ledger.to_dict(),
            "coverage": dict(coverage_summary(ledger, intake)),
        }
    )
    documents[DETERMINISM_FILE] = sealed(
        {
            **_envelope("UCOS-URI-DETERMINISM", "Realization Determinism Proof", seal),
            "determinism": dict(determinism),
        }
    )

    body = {name: documents[name] for name in sorted(documents)}
    documents[RECORD_FILE] = sealed(
        {
            **_envelope("UCOS-URI-EVIDENCE-RECORD", "Realization Evidence Record", seal),
            "bundle": sorted(documents),
            "bundle_hashes": {name: body[name]["content_sha256"] for name in sorted(body)},
            "bundle_hash": content_hash(body),
            "verdict": decision.verdict,
            "gates_passed": f"{decision.passed_count}/{len(decision.gates)}",
            "blocking_reasons": list(decision.blocking_reasons),
            "trace_closed": ledger.closed,
            "deterministic": bool(determinism.get("deterministic")),
            "artifact_count": len(manifest.artifacts),
            "plan_id": plan.plan_id,
            "composition_id": composition.composition_id,
            "generation_id": manifest.generation_id,
            "implementation_id": record.implementation_id if record else None,
            "required_files": list(REQUIRED_FILES),
        }
    )
    return RealizationEvidence(knowledge_seal=seal, documents=documents)


def emit_evidence(
    evidence: RealizationEvidence, config: RealizationConfig | None = None
) -> dict[str, str]:
    """Write the bundle to the evidence directory. Returns ``{filename: abspath}``."""
    resolved = config or RealizationConfig.create()
    directory = resolved.evidence_dir
    missing = evidence.missing()
    if missing:
        raise EvidenceError(
            "evidence bundle is incomplete; refusing to emit a partial bundle",
            missing=list(missing),
        )
    _guard_writable(resolved, directory)
    directory.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for name in sorted(evidence.documents):
        path = directory / name
        path.write_text(document_json(evidence.documents[name]), encoding="utf-8")
        written[name] = str(path)
    _logger.info(
        "realization.evidence_emitted",
        evidence_id=evidence.evidence_id,
        files=len(written),
        directory=resolved.rel(directory),
    )
    return written


def _guard_writable(config: RealizationConfig, directory: Path) -> None:
    """Refuse to emit evidence into the frozen corpus (DP-03)."""
    try:
        relative = directory.resolve().relative_to(config.repo_root)
    except ValueError:
        return
    offending = find_frozen_writes([relative.as_posix()])
    if offending:
        raise EvidenceError(
            "refusing to write evidence into the frozen corpus",
            directory=relative.as_posix(),
            frozen=list(offending),
        )


def verify_bundle(config: RealizationConfig | None = None) -> dict[str, Any]:
    """Check the on-disk bundle: presence plus per-document seal verification."""
    resolved = config or RealizationConfig.create()
    directory = resolved.evidence_dir
    results = []
    for name in REQUIRED_FILES:
        path = directory / name
        if not path.is_file():
            results.append({"file": name, "present": False, "sealed": False})
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            results.append({"file": name, "present": True, "sealed": False})
            continue
        results.append({"file": name, "present": True, "sealed": verify_seal(document)})
    failed = [entry for entry in results if not (entry["present"] and entry["sealed"])]
    return {
        "complete": not failed,
        "directory": resolved.rel(directory),
        "checked": len(results),
        "failed": failed,
        "files": results,
    }


__all__ = [
    "COMPOSITION_FILE",
    "DETERMINISM_FILE",
    "EVIDENCE_FORMAT",
    "GENERATION_FILE",
    "GOVERNANCE_FILE",
    "IMPLEMENTATION_FILE",
    "INTAKE_FILE",
    "PLAN_FILE",
    "RECORD_FILE",
    "REQUIRED_FILES",
    "TRACEABILITY_FILE",
    "RealizationEvidence",
    "build_evidence",
    "emit_evidence",
    "verify_bundle",
]
