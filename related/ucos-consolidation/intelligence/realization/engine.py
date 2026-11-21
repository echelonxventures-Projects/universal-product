"""URI-000001 — the Realization Intelligence Engine.

The single entry point that runs the whole pipeline and the single place the stage order is
enforced::

    intake → plan → compose → generate → govern → trace → (materialize) → evidence

Two properties are worth stating explicitly because they are easy to get wrong and
expensive to discover later:

* **Governance precedes materialization.** Generation is pure, so the twelve gates can be
  adjudicated over a complete generation manifest *before* a single byte is written. A
  rejected run therefore writes nothing at all — there is no partial realization to clean
  up. The determinism proof and the pre-materialization trace ledger are both available at
  that point, so no gate has to be waived.
* **Re-running is a no-op.** Every artifact is content-addressed and the Implementation
  Engine skips byte-identical files, so a second pass over unchanged canonical knowledge
  reports ``unchanged`` for everything and leaves the repository untouched.

The engine holds no authority. Its outputs are derived truth over canonical knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from intelligence.realization.composition import CompositionEngine, CompositionFindings
from intelligence.realization.config import RealizationConfig
from intelligence.realization.contracts import (
    GenerationManifest,
    ImplementationRecord,
    RealizationComposition,
    RealizationPlan,
)
from intelligence.realization.evidence import (
    RealizationEvidence,
    build_evidence,
    emit_evidence,
    verify_bundle,
)
from intelligence.realization.generation import GenerationEngine
from intelligence.realization.governance import (
    RealizationDecision,
    RealizationGovernor,
    enforce_realization,
)
from intelligence.realization.implementation import ImplementationEngine
from intelligence.realization.knowledge import KnowledgeIntake
from intelligence.realization.planning import PlanningEngine
from intelligence.realization.traceability import (
    TraceabilityEngine,
    TraceLedger,
    coverage_summary,
)

_logger = get_logger("intelligence.realization.engine")


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """Everything one pipeline run produced, in stage order."""

    intake: KnowledgeIntake
    plan: RealizationPlan
    composition: RealizationComposition
    findings: CompositionFindings
    manifest: GenerationManifest
    determinism: dict[str, Any]
    decision: RealizationDecision
    ledger: TraceLedger
    record: ImplementationRecord | None
    evidence: RealizationEvidence
    emitted: dict[str, str]

    @property
    def governed(self) -> bool:
        return self.decision.governed

    def summary(self) -> dict[str, Any]:
        """A compact, deterministic run summary (the CLI's default output)."""
        return {
            "capability": self.decision.capability,
            "verdict": self.decision.verdict,
            "gates": f"{self.decision.passed_count}/{len(self.decision.gates)}",
            "blocking_reasons": list(self.decision.blocking_reasons),
            "knowledge_seal": self.intake.knowledge_seal,
            "knowledge_source": self.intake.source,
            "canonical_objects": len(self.intake.base.objects()),
            "canonical_decisions": len(self.intake.base.decisions()),
            "targets": len(self.plan.targets),
            "plan_id": self.plan.plan_id,
            "steps": len(self.plan.steps),
            "waves": len(self.plan.waves),
            "composition_id": self.composition.composition_id,
            "units": len(self.composition.units),
            "generation_id": self.manifest.generation_id,
            "artifacts": len(self.manifest.artifacts),
            "families": self.manifest.by_family(),
            "deterministic": bool(self.determinism.get("deterministic")),
            "implementation_id": self.record.implementation_id if self.record else None,
            "materialized": None if self.record is None else not self.record.dry_run,
            "actions": self.record.actions() if self.record else {},
            "trace_closed": self.ledger.closed,
            "coverage": dict(coverage_summary(self.ledger, self.intake)),
            "evidence_id": self.evidence.evidence_id,
            "evidence_files": sorted(self.emitted),
        }


class RealizationIntelligenceEngine:
    """Orchestrates the four engines, the seven generators, governance and evidence."""

    def __init__(self, config: RealizationConfig | None = None) -> None:
        self.config = config or RealizationConfig.create()
        self.planner = PlanningEngine()
        self.composer = CompositionEngine()
        self.generator = GenerationEngine()
        self.implementer = ImplementationEngine(self.config)
        self.governor = RealizationGovernor(self.config)
        self.tracer = TraceabilityEngine()

    # -- stages ---------------------------------------------------------------

    def intake(self) -> KnowledgeIntake:
        """Load and integrity-verify canonical knowledge — the only input."""
        return KnowledgeIntake.load(self.config.knowledge_dir)

    def plan(self, intake: KnowledgeIntake | None = None) -> RealizationPlan:
        return self.planner.plan(intake or self.intake())

    def compose(
        self, intake: KnowledgeIntake | None = None, plan: RealizationPlan | None = None
    ) -> tuple[RealizationComposition, CompositionFindings]:
        resolved_intake = intake or self.intake()
        resolved_plan = plan or self.planner.plan(resolved_intake)
        return self.composer.compose(resolved_intake, resolved_plan)

    def generate(
        self,
    ) -> tuple[
        KnowledgeIntake,
        RealizationPlan,
        RealizationComposition,
        CompositionFindings,
        GenerationManifest,
    ]:
        """Run the pure prefix of the pipeline: nothing is written."""
        intake = self.intake()
        plan = self.planner.plan(intake)
        composition, findings = self.composer.compose(intake, plan)
        manifest = self.generator.generate(intake, plan, composition)
        return intake, plan, composition, findings, manifest

    # -- full pipeline --------------------------------------------------------

    def realize(
        self,
        *,
        dry_run: bool = False,
        strict: bool = True,
        emit: bool = True,
        prune: bool = False,
    ) -> RealizationResult:
        """Run the complete pipeline.

        Governance is adjudicated before materialization, so ``strict=True`` (the default)
        guarantees a rejected run writes no artifact. Evidence is emitted either way when
        ``emit`` is set, because a rejection is itself a result that must be evidenced.
        """
        with trace("realization.realize", dry_run=dry_run, strict=strict):
            intake, plan, composition, findings, manifest = self.generate()
            determinism = self.generator.verify_determinism(intake, plan, composition)
            pre_ledger = self.tracer.build(intake, plan, composition, manifest)
            decision = self.governor.adjudicate(
                intake=intake,
                plan=plan,
                composition=composition,
                findings=findings,
                manifest=manifest,
                determinism=determinism,
                ledger=pre_ledger,
            )

            record: ImplementationRecord | None = None
            ledger = pre_ledger
            if decision.governed:
                record = self.implementer.materialize(manifest, dry_run=dry_run)
                ledger = self.tracer.build(intake, plan, composition, manifest, record)
                if prune and not dry_run:
                    self.implementer.prune(manifest, dry_run=False)
                # Re-adjudicate with the materialization evidence in hand so the recorded
                # decision covers what actually happened, not only what was intended.
                decision = self.governor.adjudicate(
                    intake=intake,
                    plan=plan,
                    composition=composition,
                    findings=findings,
                    manifest=manifest,
                    determinism=determinism,
                    ledger=ledger,
                    record=record,
                )

            evidence = build_evidence(
                intake=intake,
                plan=plan,
                composition=composition,
                findings=findings,
                manifest=manifest,
                decision=decision,
                ledger=ledger,
                determinism=determinism,
                record=record,
            )
            emitted = emit_evidence(evidence, self.config) if emit else {}
            result = RealizationResult(
                intake=intake,
                plan=plan,
                composition=composition,
                findings=findings,
                manifest=manifest,
                determinism=determinism,
                decision=decision,
                ledger=ledger,
                record=record,
                evidence=evidence,
                emitted=emitted,
            )
            _logger.info(
                "realization.complete",
                verdict=decision.verdict,
                artifacts=len(manifest.artifacts),
                materialized=bool(record and not record.dry_run),
                evidence=len(emitted),
            )
            enforce_realization(decision, strict=strict)
            return result

    # -- verification ---------------------------------------------------------

    def verify(self) -> dict[str, Any]:
        """Prove determinism, on-disk artifact integrity, and evidence completeness."""
        intake, plan, composition, _findings, manifest = self.generate()
        determinism = self.generator.verify_determinism(intake, plan, composition)
        artifacts = self.implementer.verify(manifest)
        bundle = verify_bundle(self.config)
        ledger = self.tracer.build(intake, plan, composition, manifest)
        return {
            "verified": bool(
                determinism["deterministic"]
                and artifacts["verified"]
                and bundle["complete"]
                and ledger.closed
            ),
            "knowledge_seal": intake.knowledge_seal,
            "determinism": determinism,
            "artifacts": artifacts,
            "evidence_bundle": bundle,
            "traceability": {
                "closed": ledger.closed,
                "forward_gaps": list(ledger.forward_gaps),
                "orphan_artifacts": list(ledger.orphan_artifacts),
            },
        }

    def govern(self) -> RealizationDecision:
        """Adjudicate the twelve gates without materializing anything."""
        intake, plan, composition, findings, manifest = self.generate()
        determinism = self.generator.verify_determinism(intake, plan, composition)
        ledger = self.tracer.build(intake, plan, composition, manifest)
        return self.governor.adjudicate(
            intake=intake,
            plan=plan,
            composition=composition,
            findings=findings,
            manifest=manifest,
            determinism=determinism,
            ledger=ledger,
        )

    def trace(self) -> TraceLedger:
        """Build the traceability ledger for the current canonical knowledge state."""
        intake, plan, composition, _findings, manifest = self.generate()
        return self.tracer.build(intake, plan, composition, manifest)


def realize(config: RealizationConfig | None = None, **kwargs: Any) -> RealizationResult:
    """Convenience entry point: run the full realization pipeline."""
    return RealizationIntelligenceEngine(config).realize(**kwargs)


__all__ = ["RealizationIntelligenceEngine", "RealizationResult", "realize"]
