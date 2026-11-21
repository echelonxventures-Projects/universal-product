"""UCOS-EPIC-003 — Universal Discovery evidence & coverage report emission.

A **Discovery Evidence Record** captures, deterministically, the outcome of a
universal discovery pass so it is auditable (IMP-007 §11; Mandatory Rule 6 — every
determination yields evidence). The record embeds no wall-clock or ambient state,
so an identical substrate produces a byte-identical record and bundle.

    * :class:`DiscoveryEvidence` — the immutable, content-addressed evidence record
      (engine identity, substrate sizes, per-dimension coverage + counts, discovered
      gaps, and the discovery report's content hash).
    * :func:`build_discovery_evidence` — assemble the record from a report.
    * :func:`emit_evidence` — write the deterministic on-disk bundle: a coverage
      report, the evidence record, and one file per discovery dimension.

The module is standard-library only (TP-04/TP-05) and never mutates the certified
corpus (DP-03): it writes evidence to a caller-provided output directory only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.discovery.contracts import DiscoveryReport, content_hash
from engine.discovery.errors import DiscoveryEvidenceError

#: The discovery evidence record format identifier.
DISCOVERY_EVIDENCE_FORMAT = "ucos-discovery-evidence/1.0.0"

#: The coverage report format identifier.
DISCOVERY_COVERAGE_FORMAT = "ucos-discovery-coverage/1.0.0"

#: The per-dimension report format identifier.
DISCOVERY_DIMENSION_FORMAT = "ucos-discovery-dimension/1.0.0"


@dataclass(frozen=True, slots=True)
class DiscoveryEvidence:
    """A deterministic, content-addressed Universal Discovery Evidence Record."""

    engine_id: str
    substrate: dict[str, int]
    complete: bool
    coverage_percent: float
    counts: dict[str, int]
    coverage: dict[str, Any]
    gaps: dict[str, list[str]]
    report_sha256: str
    record_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_format": DISCOVERY_EVIDENCE_FORMAT,
            "engine_id": self.engine_id,
            "substrate": dict(self.substrate),
            "complete": self.complete,
            "coverage_percent": self.coverage_percent,
            "counts": dict(self.counts),
            "coverage": self.coverage,
            "gaps": {k: list(v) for k, v in self.gaps.items()},
            "report_sha256": self.report_sha256,
            "record_sha256": self.record_sha256,
        }


def build_discovery_evidence(report: DiscoveryReport) -> DiscoveryEvidence:
    """Assemble a deterministic :class:`DiscoveryEvidence` from a discovery report."""
    coverage = report.coverage()
    gaps = {r.kind.value: list(r.gaps) for r in report.results if r.gaps}
    core = {
        "engine_id": report.engine_id,
        "substrate": dict(report.substrate),
        "complete": report.complete,
        "coverage_percent": coverage.percent,
        "counts": report.counts(),
        "coverage": coverage.to_dict(),
        "gaps": gaps,
        "report_sha256": report.content_sha256(),
    }
    return DiscoveryEvidence(
        engine_id=report.engine_id,
        substrate=dict(report.substrate),
        complete=report.complete,
        coverage_percent=coverage.percent,
        counts=report.counts(),
        coverage=coverage.to_dict(),
        gaps=gaps,
        report_sha256=report.content_sha256(),
        record_sha256=content_hash(core),
    )


def _write_json(path: Path, document: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def build_coverage_document(report: DiscoveryReport) -> dict[str, Any]:
    """Return the standalone, serializable coverage report document."""
    return {
        "schema": DISCOVERY_COVERAGE_FORMAT,
        "engine_id": report.engine_id,
        "substrate": dict(report.substrate),
        "report_sha256": report.content_sha256(),
        "coverage": report.coverage().to_dict(),
        "counts": report.counts(),
    }


def emit_evidence(report: DiscoveryReport, directory: str | Path) -> dict[str, str]:
    """Write the deterministic discovery evidence bundle and return ``{filename: path}``.

    The bundle contains, all with sorted keys for byte-reproducibility:
        * ``discovery-coverage-report.json`` — the aggregate coverage surface.
        * ``discovery-evidence-record.json`` — the content-addressed evidence record.
        * ``discovery-<dimension>.json`` — one full result file per dimension.
    """
    target = Path(directory)
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:  # pragma: no cover - platform/IO dependent
        raise DiscoveryEvidenceError(
            "discovery evidence directory could not be created", directory=str(target)
        ) from exc

    written: dict[str, str] = {}

    coverage_doc = build_coverage_document(report)
    written["discovery-coverage-report.json"] = str(
        _write_json(target / "discovery-coverage-report.json", coverage_doc)
    )

    evidence_doc = build_discovery_evidence(report).to_dict()
    written["discovery-evidence-record.json"] = str(
        _write_json(target / "discovery-evidence-record.json", evidence_doc)
    )

    for result in report.results:
        filename = f"discovery-{result.kind.value}.json"
        document = {
            "schema": DISCOVERY_DIMENSION_FORMAT,
            "engine_id": report.engine_id,
            "report": result.to_dict(),
        }
        written[filename] = str(_write_json(target / filename, document))

    return written


__all__ = [
    "DISCOVERY_EVIDENCE_FORMAT",
    "DISCOVERY_COVERAGE_FORMAT",
    "DISCOVERY_DIMENSION_FORMAT",
    "DiscoveryEvidence",
    "build_discovery_evidence",
    "build_coverage_document",
    "emit_evidence",
]
