"""URI-000001 — the Generation Engine.

The single execution path for all seven generators. It walks the composition in
topological order, builds each unit's :class:`GenerationContext` (including the artifacts
every upstream family already produced for the same target), invokes the one generator
bound to that unit's family, and collects the result into a sealed manifest.

The engine — not the generators — owns:

* **ordering** — units are executed in the composition's topological order, so a
  downstream family can cite an upstream artifact by path and never race it;
* **visibility** — a unit sees only the upstream artifacts of its own target, so
  cross-target leakage is structurally impossible;
* **path uniqueness** — two generators claiming the same output path is a hard failure,
  not a last-writer-wins accident;
* **sealing** — content hashes and the manifest seal.

Generation is a **pure function** of the composition and the canonical knowledge behind
it: nothing here touches the filesystem, the clock, the environment, or the network. That
is what makes the determinism gate meaningful rather than decorative.
"""

from __future__ import annotations

from collections.abc import Mapping

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from intelligence.realization.contracts import (
    ArtifactFamily,
    GeneratedArtifact,
    GenerationManifest,
    RealizationComposition,
    RealizationPlan,
)
from intelligence.realization.errors import GenerationError
from intelligence.realization.generators import generator_for, registry_manifest
from intelligence.realization.generators.base import GenerationContext
from intelligence.realization.knowledge import KnowledgeIntake

_logger = get_logger("intelligence.realization.generation")


class GenerationEngine:
    """Executes the composition into sealed, in-memory artifacts. Writes nothing."""

    def generate(
        self,
        intake: KnowledgeIntake,
        plan: RealizationPlan,
        composition: RealizationComposition,
    ) -> GenerationManifest:
        """Return the sealed generation manifest for ``composition``."""
        with trace(
            "realization.generate",
            composition_id=composition.composition_id,
            units=len(composition.units),
        ):
            self._assert_coherent(intake, plan, composition)
            # target_id -> family value -> artifacts produced so far.
            produced: dict[str, dict[str, tuple[GeneratedArtifact, ...]]] = {}
            claimed: dict[str, str] = {}
            artifacts: list[GeneratedArtifact] = []

            for unit in composition.ordered_units():
                target = plan.target(unit.target_id)
                upstream = produced.setdefault(unit.target_id, {})
                context = GenerationContext(
                    intake=intake,
                    plan=plan,
                    composition=composition,
                    unit=unit,
                    target=target,
                    upstream=dict(upstream),
                )
                emitted = self._invoke(unit.family, context)
                self._claim_paths(emitted, claimed, unit.unit_id)
                upstream[unit.family.value] = emitted
                artifacts.extend(emitted)

            manifest = GenerationManifest(
                composition_id=composition.composition_id,
                composition_seal=composition.seal,
                plan_id=composition.plan_id,
                knowledge_seal=composition.knowledge_seal,
                artifacts=tuple(sorted(artifacts, key=lambda art: art.relative_path)),
            )
            _logger.info(
                "realization.generated",
                generation_id=manifest.generation_id,
                artifacts=len(manifest.artifacts),
                families=len(manifest.by_family()),
            )
            return manifest

    # -- internals ------------------------------------------------------------

    @staticmethod
    def _assert_coherent(
        intake: KnowledgeIntake,
        plan: RealizationPlan,
        composition: RealizationComposition,
    ) -> None:
        """Refuse to generate from stages that were derived from different states."""
        if plan.plan_id != composition.plan_id:
            raise GenerationError(
                "composition does not belong to the supplied plan",
                plan_id=plan.plan_id,
                composition_plan_id=composition.plan_id,
            )
        if intake.knowledge_seal != composition.knowledge_seal:
            raise GenerationError(
                "composition was derived from a different canonical knowledge state",
                intake_seal=intake.knowledge_seal,
                composition_seal=composition.knowledge_seal,
            )
        if not composition.units:
            raise GenerationError(
                "composition contains no units; nothing to generate",
                composition_id=composition.composition_id,
            )

    @staticmethod
    def _invoke(
        family: ArtifactFamily, context: GenerationContext
    ) -> tuple[GeneratedArtifact, ...]:
        generator = generator_for(family)
        emitted = generator.generate(context)
        if not emitted:
            raise GenerationError(
                "generator produced no artifact for a planned step",
                family=family.value,
                generator=generator.name,
                step_id=context.unit.step_id,
            )
        for artifact in emitted:
            if artifact.family is not family:
                raise GenerationError(
                    "generator emitted an artifact outside its own family",
                    generator=generator.name,
                    expected=family.value,
                    actual=artifact.family.value,
                    path=artifact.relative_path,
                )
            if not artifact.provenance.source_ckos:
                raise GenerationError(
                    "generated artifact is not anchored to any canonical object",
                    generator=generator.name,
                    path=artifact.relative_path,
                )
        return emitted

    @staticmethod
    def _claim_paths(
        emitted: tuple[GeneratedArtifact, ...],
        claimed: dict[str, str],
        unit_id: str,
    ) -> None:
        for artifact in emitted:
            owner = claimed.get(artifact.relative_path)
            if owner is not None:
                raise GenerationError(
                    "two composition units claim the same output path",
                    path=artifact.relative_path,
                    first_unit=owner,
                    second_unit=unit_id,
                )
            claimed[artifact.relative_path] = unit_id

    # -- determinism ----------------------------------------------------------

    def verify_determinism(
        self,
        intake: KnowledgeIntake,
        plan: RealizationPlan,
        composition: RealizationComposition,
    ) -> dict[str, object]:
        """Generate twice and prove the two passes are byte-identical."""
        first = self.generate(intake, plan, composition)
        second = self.generate(intake, plan, composition)
        left = {a.relative_path: a.content_sha256 for a in first.artifacts}
        right = {a.relative_path: a.content_sha256 for a in second.artifacts}
        mismatches = sorted(
            path for path in set(left) | set(right) if left.get(path) != right.get(path)
        )
        return {
            "deterministic": not mismatches and first.seal == second.seal,
            "artifact_count": len(first.artifacts),
            "mismatches": mismatches,
            "first_seal": first.seal,
            "second_seal": second.seal,
            "generators": registry_manifest(),
        }


def generate_artifacts(
    intake: KnowledgeIntake,
    plan: RealizationPlan,
    composition: RealizationComposition,
) -> GenerationManifest:
    """Convenience entry point: run the generation engine once."""
    return GenerationEngine().generate(intake, plan, composition)


def artifact_index(manifest: GenerationManifest) -> Mapping[str, GeneratedArtifact]:
    """Index a manifest's artifacts by relative path (for verification and tracing)."""
    return {artifact.relative_path: artifact for artifact in manifest.artifacts}


__all__ = ["GenerationEngine", "artifact_index", "generate_artifacts"]
