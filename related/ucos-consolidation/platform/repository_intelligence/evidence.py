"""UCOS-EPIC-014 — Repository Intelligence evidence generation (Terminal T5).

Every determination yields evidence (IMP-007 §11). This module renders one intelligence
cycle into the set of sealed, machine-readable artefacts the repository persists, and into a
single content-addressed :class:`RepositoryIntelligenceEvidence` record that a downstream
gate or dashboard can consume on its own.

Two serializations coexist deliberately, and they are not interchangeable:

    * **hashing** uses :func:`platform.foundation.contracts.canonical_json` — the compact
      canonical form the whole platform already hashes with. Every seal in this subsystem is
      computed over that form, so seals are comparable across subsystems.
    * **file rendering** uses the indented, sorted, newline-terminated form the repository's
      existing JSON artefacts use, so an emitted artefact is readable and diffable.

The artefact set is fixed and named in :data:`ARTIFACT_NAMES`, so the writer, the determinism
proof and the artefact index all agree on exactly what a cycle produces. No wall-clock enters
any artefact: identical repository content reproduces identical bytes.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.repository_intelligence.certification import RepositoryCertificate
from platform.repository_intelligence.contracts import (
    DERIVED_TRUTH,
    EVIDENCE_FORMAT,
    REPOSITORY_INTELLIGENCE_AUTHORITY,
    REPOSITORY_INTELLIGENCE_PROGRAMME,
    DiscoveryDimension,
    RepositoryIntelligenceReport,
)
from platform.repository_intelligence.substrate import RepositorySubstrate
from platform.repository_intelligence.validation import RepositoryValidationReport
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from platform.repository_intelligence.runtime import IntelligenceCycle

#: The complete, fixed artefact set one intelligence cycle produces.
ARTIFACT_NAMES: dict[str, str] = {
    "report": "UCOS-RPI-REPORT.json",
    "graph": "UCOS-RPI-DEPENDENCY-GRAPH.json",
    "graph_dot": "UCOS-RPI-DEPENDENCY-GRAPH.dot",
    "graph_mermaid": "UCOS-RPI-DEPENDENCY-GRAPH.mmd",
    "capability_reuse": "UCOS-RPI-CAPABILITY-REUSE.json",
    "gaps": "UCOS-RPI-GAPS.json",
    "conflicts": "UCOS-RPI-CONFLICTS.json",
    "duplicates": "UCOS-RPI-DUPLICATES.json",
    "ownership": "UCOS-RPI-OWNERSHIP.json",
    "recommendations": "UCOS-RPI-RECOMMENDATIONS.json",
    "validation": "UCOS-RPI-VALIDATION.json",
    "certificate": "UCOS-RPI-CERTIFICATE.json",
    "evidence": "UCOS-RPI-EVIDENCE.json",
    "index": "UCOS-RPI-ARTIFACT-INDEX.json",
}

#: Schema identifier of the artefact index (a manifest, not a sealed determination).
ARTIFACT_INDEX_FORMAT = "ucos-repository-intelligence-artifact-index/1.0.0"


def artifact_text(payload: Mapping[str, Any]) -> str:
    """Render a payload in the repository's readable, deterministic artefact form."""
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _envelope(substrate: RepositorySubstrate, artifact_id: str, title: str) -> dict[str, Any]:
    """The common artefact header: identity, provenance and the authority disclaimer.

    Deliberately carries no timestamp. An artefact's identity is its substrate digest, which
    is what makes re-emission on an unchanged repository a no-op.
    """
    return {
        "artifact_id": artifact_id,
        "title": title,
        "programme": REPOSITORY_INTELLIGENCE_PROGRAMME,
        "producer": "UCOS-EPIC-014 Repository Intelligence (Terminal T5)",
        "authority": REPOSITORY_INTELLIGENCE_AUTHORITY,
        "derived_from": DERIVED_TRUTH,
        "classification": "ADDITIVE INTELLIGENCE (machine-readable) — derived, non-authoritative",
        "repository_id": substrate.config.repository_id,
        "substrate_digest": substrate.digest(),
        "substrate": substrate.to_dict(),
    }


@dataclass(frozen=True, slots=True)
class RepositoryIntelligenceEvidence:
    """A deterministic, serializable, content-addressed intelligence evidence record."""

    repository_id: str
    determination: str
    gate: str
    substrate_digest: str
    report_sha256: str
    validation_sha256: str
    certificate_seal: str
    graph_digest: str
    catalog_source: str
    dimension_verdicts: Mapping[str, str]
    counts: Mapping[str, int]
    validation_counts: Mapping[str, int]
    blocking_findings: tuple[Mapping[str, Any], ...]
    blocking_rules: tuple[str, ...]
    advisory_codes: tuple[str, ...]
    recommendations: tuple[Mapping[str, Any], ...]
    disclosure: Mapping[str, Any]

    def _core(self) -> dict[str, Any]:
        return {
            "evidence_format": EVIDENCE_FORMAT,
            "programme": REPOSITORY_INTELLIGENCE_PROGRAMME,
            "repository_id": self.repository_id,
            "determination": self.determination,
            "gate": self.gate,
            "substrate_digest": self.substrate_digest,
            "report_sha256": self.report_sha256,
            "validation_sha256": self.validation_sha256,
            "certificate_seal": self.certificate_seal,
            "graph_digest": self.graph_digest,
            "catalog_source": self.catalog_source,
            "dimension_verdicts": dict(sorted(self.dimension_verdicts.items())),
            "counts": dict(sorted(self.counts.items())),
            "validation_counts": dict(sorted(self.validation_counts.items())),
            "blocking_findings": [dict(f) for f in self.blocking_findings],
            "blocking_rules": list(self.blocking_rules),
            "advisory_codes": list(self.advisory_codes),
            "recommendations": [dict(r) for r in self.recommendations],
            "authority": REPOSITORY_INTELLIGENCE_AUTHORITY,
            "derived_from": DERIVED_TRUTH,
            "disclosure": dict(self.disclosure),
        }

    @property
    def evidence_sha256(self) -> str:
        """The deterministic content hash of the evidence record."""
        return content_hash(self._core())

    def to_dict(self) -> dict[str, Any]:
        return {**self._core(), "evidence_sha256": self.evidence_sha256}


def build_evidence(
    substrate: RepositorySubstrate,
    report: RepositoryIntelligenceReport,
    validation: RepositoryValidationReport,
    certificate: RepositoryCertificate,
) -> RepositoryIntelligenceEvidence:
    """Assemble the evidence record for one intelligence cycle."""
    return RepositoryIntelligenceEvidence(
        repository_id=report.repository_id,
        determination=certificate.determination.value,
        gate=certificate.gate,
        substrate_digest=report.substrate_digest,
        report_sha256=report.report_sha256,
        validation_sha256=validation.validation_sha256,
        certificate_seal=certificate.seal_sha256,
        graph_digest=report.graph.digest(),
        catalog_source=substrate.catalog_source,
        dimension_verdicts=dict(report.dimension_verdicts()),
        counts=report.counts(),
        validation_counts=validation.counts(),
        blocking_findings=tuple(f.core() for f in report.all_findings if f.is_blocking_failure),
        blocking_rules=validation.blocking_failures(),
        advisory_codes=tuple(
            sorted({f.code for f in report.all_findings if f.is_advisory_failure})
        ),
        recommendations=tuple(r.to_dict() for r in report.recommendations),
        disclosure=dict(report.disclosure),
    )


def build_artifacts(cycle: IntelligenceCycle) -> dict[str, str]:
    """Render one intelligence cycle into the complete, named artefact set.

    Returns ``{filename: file text}``. The artefact index is computed last, over the
    rendered bytes of every other artefact, so it is a true manifest of what was emitted.
    """
    substrate = cycle.substrate
    report = cycle.report
    payloads: dict[str, dict[str, Any]] = {}

    payloads[ARTIFACT_NAMES["report"]] = {
        **_envelope(substrate, "UCOS-RPI-REPORT", "Repository Intelligence Report"),
        **report.to_dict(),
    }
    payloads[ARTIFACT_NAMES["graph"]] = {
        **_envelope(substrate, "UCOS-RPI-DEPENDENCY-GRAPH", "Repository Dependency Graph"),
        **report.graph.to_dict(),
        "impact_profiles": {
            row["node"]: cycle.graph.impact_of(str(row["node"]))
            for row in cycle.graph.most_depended_upon()
        },
    }
    payloads[ARTIFACT_NAMES["capability_reuse"]] = {
        **_envelope(substrate, "UCOS-RPI-CAPABILITY-REUSE", "Capability and Reuse Intelligence"),
        "catalog_source": substrate.catalog_source,
        "capability_count": len(report.capabilities),
        "capabilities": [c.to_dict() for c in report.capabilities],
        "reuse": [r.to_dict() for r in report.reuse],
        "unproven_reuse": list(report.unproven_capabilities()),
    }
    payloads[ARTIFACT_NAMES["gaps"]] = _dimension_artifact(
        substrate, report, DiscoveryDimension.GAP, "UCOS-RPI-GAPS", "Repository Gap Register"
    )
    payloads[ARTIFACT_NAMES["conflicts"]] = _dimension_artifact(
        substrate,
        report,
        DiscoveryDimension.CONFLICT,
        "UCOS-RPI-CONFLICTS",
        "Repository Conflict Register",
    )
    payloads[ARTIFACT_NAMES["duplicates"]] = _dimension_artifact(
        substrate,
        report,
        DiscoveryDimension.DUPLICATE,
        "UCOS-RPI-DUPLICATES",
        "Repository Duplication Register",
    )
    payloads[ARTIFACT_NAMES["ownership"]] = {
        **_envelope(substrate, "UCOS-RPI-OWNERSHIP", "Repository Ownership Register"),
        **report.result_for(DiscoveryDimension.OWNERSHIP).to_dict(),
        "ownership": [o.to_dict() for o in report.ownership],
        "unowned": list(report.unowned_units()),
    }
    payloads[ARTIFACT_NAMES["recommendations"]] = {
        **_envelope(substrate, "UCOS-RPI-RECOMMENDATIONS", "Repository Recommendation Register"),
        "count": len(report.recommendations),
        "recommendations": [r.to_dict() for r in report.recommendations],
    }
    payloads[ARTIFACT_NAMES["validation"]] = {
        **_envelope(substrate, "UCOS-RPI-VALIDATION", "Repository Validation Report"),
        **cycle.validation.to_dict(),
    }
    payloads[ARTIFACT_NAMES["certificate"]] = {
        **_envelope(substrate, "UCOS-RPI-CERTIFICATE", "Repository Intelligence Certificate"),
        **cycle.certificate.to_dict(),
    }
    payloads[ARTIFACT_NAMES["evidence"]] = {
        **_envelope(substrate, "UCOS-RPI-EVIDENCE", "Repository Intelligence Evidence"),
        **cycle.evidence.to_dict(),
    }

    artifacts = {name: artifact_text(payload) for name, payload in payloads.items()}
    artifacts[ARTIFACT_NAMES["graph_dot"]] = report.graph.to_dot()
    artifacts[ARTIFACT_NAMES["graph_mermaid"]] = report.graph.to_mermaid()
    artifacts[ARTIFACT_NAMES["index"]] = artifact_text(
        {
            **_envelope(substrate, "UCOS-RPI-ARTIFACT-INDEX", "Repository Intelligence Artefacts"),
            "index_format": ARTIFACT_INDEX_FORMAT,
            "determination": cycle.certificate.determination.value,
            "gate": cycle.certificate.gate,
            "certificate_seal": cycle.certificate.seal_sha256,
            "artifact_count": len(artifacts),
            "artifacts": [
                {
                    "name": name,
                    "bytes": len(text.encode("utf-8")),
                    "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                }
                for name, text in sorted(artifacts.items())
            ],
        }
    )
    return dict(sorted(artifacts.items()))


def _dimension_artifact(
    substrate: RepositorySubstrate,
    report: RepositoryIntelligenceReport,
    dimension: DiscoveryDimension,
    artifact_id: str,
    title: str,
) -> dict[str, Any]:
    """Render one discovery dimension as a standalone register artefact."""
    result = report.result_for(dimension)
    by_code: dict[str, int] = {}
    for finding in result.findings:
        by_code[finding.code] = by_code.get(finding.code, 0) + 1
    return {
        **_envelope(substrate, artifact_id, title),
        **result.to_dict(),
        "by_code": dict(sorted(by_code.items())),
    }


__all__ = [
    "ARTIFACT_NAMES",
    "ARTIFACT_INDEX_FORMAT",
    "artifact_text",
    "RepositoryIntelligenceEvidence",
    "build_evidence",
    "build_artifacts",
]
