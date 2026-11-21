"""ResearchIntelligenceEngine — the producer of every research intelligence output.

Reads declared Repository Truth → assimilates the research corpus → registers it →
analyses standards → validates → emits sealed, machine-readable outputs. Holds no
authority: every output declares ``AUTHORITY = NONE (derived truth)`` and cites the
content fingerprint of every substrate surface it read.
"""

from __future__ import annotations

from typing import Any

from intelligence.kernel.canonical import canonical_json, sealed
from intelligence.kernel.config import (
    NestedFileSink,
    OutputSink,
    RepoConfig,
    subsystem_config,
)
from intelligence.kernel.knowledge import CanonicalKnowledgeResolver
from intelligence.kernel.substrate import SubstrateReader
from intelligence.kernel.validation import EXIT_ABORT, ValidationReport
from intelligence.research import AUTHORITY, PROGRAMME, __version__
from intelligence.research.assimilation import ResearchAssimilationEngine
from intelligence.research.model import ResearchCorpus
from intelligence.research.registry import ResearchRegistry
from intelligence.research.standards import StandardsAnalysisEngine, curated_overlay
from intelligence.research.validation import ResearchValidationEngine

#: The subsystem-owned output directory (the only place this engine writes).
OUTPUT_DIR = PROGRAMME

_CLASSIFICATION = (
    "ADDITIVE INTELLIGENCE (machine-readable) — derived research truth, non-authoritative"
)


class ResearchIntelligenceEngine:
    """The Research Intelligence subsystem: assimilate → register → analyse → validate."""

    def __init__(self, config: RepoConfig | None = None) -> None:
        self.config = config or subsystem_config(OUTPUT_DIR)
        self.substrate = SubstrateReader(self.config)
        self.resolver = CanonicalKnowledgeResolver(self.substrate)
        self.assimilation = ResearchAssimilationEngine(self.substrate, self.resolver)
        self._corpus: ResearchCorpus | None = None
        self._registry: ResearchRegistry | None = None

    # -- core ------------------------------------------------------------------

    def corpus(self) -> ResearchCorpus:
        if self._corpus is None:
            self._corpus = self.assimilation.assimilate()
        return self._corpus

    def registry(self) -> ResearchRegistry:
        if self._registry is None:
            self._registry = ResearchRegistry(self.corpus())
        return self._registry

    def standards(self) -> StandardsAnalysisEngine:
        return StandardsAnalysisEngine(self.corpus(), self.resolver)

    def validation(self) -> ValidationReport:
        return ResearchValidationEngine(
            self.corpus(),
            self.resolver,
            self.registry(),
            reassimilate=self._fresh_corpus,
        ).validate()

    def _fresh_corpus(self) -> ResearchCorpus:
        """A second, independent assimilation — the determinism witness."""
        substrate = SubstrateReader(self.config)
        resolver = CanonicalKnowledgeResolver(substrate)
        return ResearchAssimilationEngine(substrate, resolver).assimilate()

    # -- envelope --------------------------------------------------------------

    def envelope(self, artifact_id: str, title: str) -> dict[str, Any]:
        """The common, deterministic header. No wall-clock — identity is the evidence."""
        return {
            "artifact_id": artifact_id,
            "title": title,
            "programme": PROGRAMME,
            "producer": f"{PROGRAMME} Universal Research Intelligence v{__version__}",
            "authority": AUTHORITY,
            "classification": _CLASSIFICATION,
            "evidence_state": {
                "substrate": self.substrate.fingerprint(),
                "knowledge": self.resolver.fingerprint(),
            },
        }

    # -- model -----------------------------------------------------------------

    def model(self) -> dict[str, Any]:
        corpus = self.corpus()
        registry = self.registry()
        validation = self.validation()
        model = self.envelope("UCOS-URI-MODEL", "Research Intelligence Model")
        model.update(
            {
                "counts": corpus.counts(),
                "registry": {
                    "registry_id": registry.ledger.registry_id,
                    "records": registry.count(),
                    "class_histogram": registry.ledger.class_histogram(),
                    "journal_head": registry.ledger.head(),
                    "integrity": registry.verify(),
                },
                "units": [u.to_dict() for u in corpus.units],
                "standards_summary": {
                    k: v for k, v in self.standards().model().items() if k != "standards"
                },
                "validation": {
                    "verdict": validation.verdict,
                    "gate": "OPEN" if validation.gate_open else "CLOSED",
                    "checks_passed": len(validation.passed()),
                    "checks_total": len(validation.checks),
                    "blocking_failures": [c.check_id for c in validation.blocking_failures()],
                },
                "substrate_inventory": [dict(s) for s in corpus.substrate_inventory],
                "assimilation_gaps": self.assimilation.gaps(),
            }
        )
        return model

    # -- outputs ---------------------------------------------------------------

    def outputs(self) -> dict[str, dict[str, Any]]:
        corpus = self.corpus()
        registry = self.registry()
        validation = self.validation()

        assimilation = self.envelope("UCOS-URI-ASSIMILATION", "Research Assimilation Corpus")
        assimilation.update(corpus.to_dict())
        assimilation["gaps"] = self.assimilation.gaps()

        registry_out = self.envelope("UCOS-URI-RESEARCH-REGISTRY", "Research Registry")
        registry_out.update(registry.document())

        standards_out = self.envelope("UCOS-URI-STANDARDS-ANALYSIS", "Standards Analysis")
        standards_out.update(self.standards().model())
        standards_out["curated_overlay"] = dict(curated_overlay())

        validation_out = self.envelope("UCOS-URI-RESEARCH-VALIDATION", "Research Validation Report")
        validation_out.update(validation.to_dict())

        snapshot = self.envelope("UCOS-URI-SNAPSHOT", "Research Intelligence Snapshot")
        snapshot.update(
            {
                "counts": corpus.counts(),
                "registry_records": registry.count(),
                "registry_head": registry.ledger.head(),
                "research_areas": [u.area_label for u in corpus.units],
                "standards_conformance": self.standards().conformance_histogram(),
                "verdict": validation.verdict,
                "gate": "OPEN" if validation.gate_open else "CLOSED",
                "citable_references": len(registry.citable_refs()),
            }
        )

        payloads = {
            "UCOS-URI-MODEL.json": self.model(),
            "UCOS-URI-ASSIMILATION.json": assimilation,
            "UCOS-URI-RESEARCH-REGISTRY.json": registry_out,
            "UCOS-URI-STANDARDS-ANALYSIS.json": standards_out,
            "UCOS-URI-RESEARCH-VALIDATION.json": validation_out,
            "UCOS-URI-SNAPSHOT.json": snapshot,
        }
        return {name: sealed(payload) for name, payload in payloads.items()}

    def write(self, sink: OutputSink | None = None) -> list[str]:
        target = sink or NestedFileSink(self.config.output_dir)
        written = [
            target.emit(name, canonical_json(payload)) for name, payload in self.outputs().items()
        ]
        return sorted(written)

    # -- determinism -----------------------------------------------------------

    def verify_determinism(self) -> dict[str, Any]:
        """Prove identical repository state ⇒ byte-identical outputs."""
        first = self.outputs()
        second = ResearchIntelligenceEngine(self.config).outputs()
        mismatches = sorted(
            name
            for name in first
            if canonical_json(first[name]) != canonical_json(second.get(name, {}))
        )
        return {
            "programme": PROGRAMME,
            "deterministic": not mismatches and sorted(first) == sorted(second),
            "outputs_checked": sorted(first),
            "mismatches": mismatches,
            "corpus_content_hash": sealed(self.corpus().to_dict())["content_hash"],
        }

    # -- gate ------------------------------------------------------------------

    def gate(self) -> tuple[int, str]:
        """Fail-closed research gate. 0 open · 1 closed · 2 fail-closed abort."""
        missing = self.substrate.missing_required()
        if missing:
            return (
                EXIT_ABORT,
                f"{PROGRAMME}: FAIL-CLOSED ABORT | required substrate unavailable: "
                f"{', '.join(missing)}",
            )
        validation = self.validation()
        determinism = self.verify_determinism()
        corpus = self.corpus()
        registry = self.registry()
        line = (
            f"{PROGRAMME}: {validation.verdict} | "
            f"claims={len(corpus.claims)} findings={len(corpus.findings)} "
            f"standards={len(corpus.standards)} units={len(corpus.units)} | "
            f"records={registry.count()} | "
            f"checks={len(validation.passed())}/{len(validation.checks)} PASS | "
            f"deterministic={str(determinism['deterministic']).lower()} | "
            f"gate={'OPEN' if validation.gate_open else 'CLOSED'} | "
            f"seal={registry.ledger.head()[:16]}"
        )
        if not determinism["deterministic"]:
            return 1, line
        return validation.exit_code, line


__all__ = ["OUTPUT_DIR", "ResearchIntelligenceEngine"]
