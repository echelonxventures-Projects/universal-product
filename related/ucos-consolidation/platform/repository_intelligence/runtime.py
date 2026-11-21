"""UCOS-EPIC-014 — Repository Intelligence Runtime (Terminal T5).

The continuous loop that binds the subsystem together: read the substrate, run all eight
discovery dimensions, build the graph, rank recommendations, validate, certify, and — when
asked — persist the sealed artefacts. One method, :meth:`RepositoryIntelligenceRuntime.scan`,
performs a complete intelligence cycle.

"Search the repository continuously" is implemented as *cheap, idempotent re-scanning* rather
than a daemon: because the whole pipeline is a pure function of the substrate digest, a scan
can be re-run on every change (hook, CI job, pre-commit, or loop) and

    * an unchanged repository reproduces byte-identical artefacts — provable via
      :meth:`verify_determinism`, so re-running costs nothing and proves nothing changed;
    * a changed repository yields a new digest, and :meth:`cycle` reports the **drift**
      against the previously persisted report — what capabilities appeared or vanished, which
      dimension verdicts moved, and whether the certificate determination flipped.

Nothing here mutates the repository other than writing this subsystem's own artefacts under
its configured output directory; the certified corpus and every code root are read-only (DP-03).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from platform.repository_intelligence.certification import RepositoryCertificate
from platform.repository_intelligence.config import RepositoryIntelligenceConfig
from platform.repository_intelligence.contracts import (
    RepositoryIntelligenceReport,
    Verdict,
)
from platform.repository_intelligence.discovery import discover_all
from platform.repository_intelligence.evidence import (
    ARTIFACT_NAMES,
    RepositoryIntelligenceEvidence,
    build_artifacts,
    build_evidence,
)
from platform.repository_intelligence.graph import RepositoryGraph, build_graph
from platform.repository_intelligence.recommendation import RepositoryRecommendationEngine
from platform.repository_intelligence.substrate import RepositorySubstrate
from platform.repository_intelligence.validation import (
    RepositoryValidationReport,
    RepositoryValidator,
)
from typing import Any


@dataclass(frozen=True, slots=True)
class IntelligenceCycle:
    """The complete, immutable outcome of one intelligence cycle."""

    substrate: RepositorySubstrate
    report: RepositoryIntelligenceReport
    graph: RepositoryGraph
    validation: RepositoryValidationReport
    certificate: RepositoryCertificate
    evidence: RepositoryIntelligenceEvidence

    @property
    def passed(self) -> bool:
        return self.certificate.certified

    def summary(self) -> dict[str, Any]:
        """A compact, deterministic projection for dashboards, hooks and the CLI."""
        return {
            "repository_id": self.report.repository_id,
            "determination": self.certificate.determination.value,
            "gate": self.certificate.gate,
            "substrate_digest": self.report.substrate_digest,
            "report_sha256": self.report.report_sha256,
            "seal_sha256": self.certificate.seal_sha256,
            "counts": self.report.counts(),
            "dimension_verdicts": self.report.dimension_verdicts(),
            "validation": self.validation.counts(),
            "blocking_rules": list(self.validation.blocking_failures()),
            "graph": {
                "nodes": len(self.graph.nodes),
                "edges": len(self.graph.edges),
                "acyclic": not self.graph.cycles(),
                "layers": len(self.graph.topological_layers()),
                "foundations": list(self.graph.foundations()),
            },
            "next_action": (
                self.report.recommendations[0].to_dict() if self.report.recommendations else None
            ),
            "drift": dict(self.report.drift),
        }


class RepositoryIntelligenceRuntime:
    """Runs, persists and re-runs repository intelligence cycles."""

    __slots__ = ("config",)

    def __init__(self, config: RepositoryIntelligenceConfig | None = None) -> None:
        self.config = config or RepositoryIntelligenceConfig.create()

    # -- one cycle --------------------------------------------------------
    def scan(self, prior: Mapping[str, Any] | None = None) -> IntelligenceCycle:
        """Perform a full intelligence cycle over the current repository state."""
        substrate = RepositorySubstrate.scan(self.config)
        outcome = discover_all(substrate)
        graph = build_graph(outcome.units, outcome.edges)
        engine = RepositoryRecommendationEngine(substrate, outcome, graph)
        recommendations = engine.recommend()
        report = RepositoryIntelligenceReport.create(
            repository_id=self.config.repository_id,
            substrate_digest=substrate.digest(),
            units=outcome.units,
            capabilities=outcome.capabilities,
            reuse=outcome.reuse,
            ownership=outcome.ownership,
            graph=graph,
            dimension_results=outcome.results,
            recommendations=recommendations,
            drift=detect_drift(substrate.digest(), report_core(outcome, graph), prior),
        )
        validation = RepositoryValidator(report).validate()
        certificate = RepositoryCertificate.issue(report, validation)
        evidence = build_evidence(substrate, report, validation, certificate)
        return IntelligenceCycle(
            substrate=substrate,
            report=report,
            graph=graph,
            validation=validation,
            certificate=certificate,
            evidence=evidence,
        )

    def cycle(self) -> IntelligenceCycle:
        """Scan, comparing against the previously persisted report to report drift."""
        return self.scan(prior=self.prior_report())

    # -- persistence ------------------------------------------------------
    @property
    def output_dir(self) -> Path:
        return self.config.output_dir

    def prior_report(self) -> Mapping[str, Any] | None:
        """The previously persisted report, or None when this is the first cycle."""
        path = self.output_dir / ARTIFACT_NAMES["report"]
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            return None
        return payload if isinstance(payload, Mapping) else None

    def write(self, cycle: IntelligenceCycle | None = None) -> tuple[str, ...]:
        """Persist every sealed artefact, returning the repository-relative paths written."""
        run = cycle or self.cycle()
        target = self.output_dir
        target.mkdir(parents=True, exist_ok=True)
        written: list[str] = []
        for name, text in build_artifacts(run).items():
            path = target / name
            path.write_text(text, encoding="utf-8")
            written.append(self.config.rel(path))
        return tuple(sorted(written))

    # -- determinism proof ------------------------------------------------
    def verify_determinism(self) -> dict[str, Any]:
        """Prove that unchanged repository content yields byte-identical artefacts.

        Drift is excluded from the comparison by scanning with no prior on both passes:
        drift is a function of the *previous* run as well as the current state, so it is
        deterministic given both, but it is not a property of the current state alone.

        The two passes read the live repository, so a concurrent writer can change the
        substrate between them. That is a *changed input*, not non-determinism, and
        conflating the two would make the proof both flaky and dishonest — so the substrate
        digests are compared first and a mid-proof change is reported as ``inconclusive``.
        """
        first_cycle = self.scan(prior=None)
        second_cycle = self.scan(prior=None)
        first = build_artifacts(first_cycle)
        second = build_artifacts(second_cycle)
        mismatches = sorted(name for name in first if first.get(name) != second.get(name))
        substrate_changed = (
            first_cycle.report.substrate_digest != second_cycle.report.substrate_digest
        )
        return {
            "deterministic": not mismatches and not substrate_changed,
            "conclusive": not substrate_changed,
            "substrate_changed_during_proof": substrate_changed,
            "substrate_digests": [
                first_cycle.report.substrate_digest,
                second_cycle.report.substrate_digest,
            ],
            "note": (
                "the repository was modified by another writer between the two passes; the "
                "proof is inconclusive — re-run against a quiescent repository"
                if substrate_changed
                else "identical substrate reproduced identical artefacts"
            ),
            "artifacts_compared": sorted(first),
            "mismatches": mismatches,
        }


# ---------------------------------------------------------------------------
# drift
# ---------------------------------------------------------------------------
def report_core(outcome: Any, graph: RepositoryGraph) -> dict[str, Any]:
    """The minimal current-state projection drift is computed against."""
    return {
        "capabilities": sorted(c.name for c in outcome.capabilities if c.present_on_disk),
        "dimension_verdicts": {
            result.dimension.value: result.verdict.value for result in outcome.results
        },
        "graph_digest": graph.digest(),
        "edges": len(graph.edges),
    }


def detect_drift(
    substrate_digest: str,
    current: Mapping[str, Any],
    prior: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Compare the current state against a previously persisted report.

    Reports ``baseline`` when there is no prior, rather than inventing change, and
    ``unchanged`` when the substrate digest is identical — the cheap, exact answer that
    makes continuous re-scanning viable.
    """
    if prior is None:
        return {
            "baseline": True,
            "note": "no prior persisted report; drift baseline established",
            "capabilities_added": [],
            "capabilities_removed": [],
            "dimension_changes": [],
        }
    prior_digest = str(prior.get("substrate_digest", ""))
    if prior_digest and prior_digest == substrate_digest:
        return {
            "baseline": False,
            "substrate_changed": False,
            "note": "substrate digest unchanged since the prior report",
            "capabilities_added": [],
            "capabilities_removed": [],
            "dimension_changes": [],
        }
    prior_capabilities = {
        str(entry.get("name"))
        for entry in prior.get("capabilities", [])
        if isinstance(entry, Mapping) and entry.get("present_on_disk", True)
    }
    now_capabilities = set(current["capabilities"])
    prior_verdicts = dict(prior.get("dimension_verdicts", {}) or {})
    changes = [
        {"dimension": name, "from": prior_verdicts.get(name), "to": verdict}
        for name, verdict in sorted(current["dimension_verdicts"].items())
        if prior_verdicts.get(name) != verdict
    ]
    return {
        "baseline": False,
        "substrate_changed": True,
        "prior_substrate_digest": prior_digest,
        "capabilities_added": sorted(now_capabilities - prior_capabilities),
        "capabilities_removed": sorted(prior_capabilities - now_capabilities),
        "dimension_changes": changes,
        "prior_verdict": prior.get("verdict"),
        "graph_changed": str(prior.get("graph", {}).get("graph_digest", ""))
        != current["graph_digest"],
    }


def run_once(
    config: RepositoryIntelligenceConfig | None = None,
) -> IntelligenceCycle:
    """Convenience: perform one intelligence cycle with drift against the prior report."""
    return RepositoryIntelligenceRuntime(config).cycle()


def gate(config: RepositoryIntelligenceConfig | None = None) -> int:
    """Fail-closed gate entry point: 0 when certified, 1 otherwise."""
    cycle = run_once(config)
    return 0 if cycle.certificate.certified and cycle.report.verdict is not Verdict.FAIL else 1


__all__ = [
    "IntelligenceCycle",
    "RepositoryIntelligenceRuntime",
    "report_core",
    "detect_drift",
    "run_once",
    "gate",
]
