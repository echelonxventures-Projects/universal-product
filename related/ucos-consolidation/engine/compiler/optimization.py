"""TASK-000024 — Optimization Stage (EPIC-003, IMP-007 §9).

Optimization applies **semantics-preserving and traceability-preserving**
transforms to compiled artifacts (IMP-007 §9). It never removes derivable
behaviour, never invents behaviour, and never drops the embedded provenance chain
(Mandatory Rules 6 & 7). The transforms here are deliberately conservative
normalisations that also serve reproducibility (byte-stable output, IMP-007 §5):

    * strip trailing whitespace from every line (no semantic effect on SQL,
      Python, or the generated JSON, whose strings never carry trailing spaces);
    * collapse runs of blank lines to a single blank line;
    * guarantee exactly one terminating newline.

After every transform the optimizer **re-asserts** that the artifact still embeds
its blueprint id and canonical-source provenance; if any transform would break
traceability, it raises :class:`OptimizationError` and the build halts (fail-safe).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from engine.compiler.data_compiler import CompiledArtifact, CompiledBlueprint
from engine.compiler.errors import OptimizationError
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("compiler.optimize")

_TRAILING_WS = re.compile(r"[ \t]+$", re.MULTILINE)
_MANY_BLANKS = re.compile(r"\n{3,}")


@dataclass(frozen=True, slots=True)
class OptimizedBlueprint:
    """A compiled blueprint after semantics-preserving optimization."""

    blueprint: CompiledBlueprint
    applied: tuple[str, ...]


def _normalize(content: str) -> str:
    without_trailing = _TRAILING_WS.sub("", content)
    collapsed = _MANY_BLANKS.sub("\n\n", without_trailing)
    return collapsed.rstrip("\n") + "\n"


class Optimizer:
    """Applies semantics-preserving, traceability-preserving normalisations."""

    __slots__ = ()

    def optimize(self, compiled: CompiledBlueprint) -> OptimizedBlueprint:
        """Return an optimized copy of ``compiled`` (semantics preserved)."""
        canonical_source = (
            compiled.provenance_chain[1] if len(compiled.provenance_chain) > 1 else ""
        )
        with trace("compiler.optimize", blueprint=compiled.blueprint_id):
            new_artifacts: list[CompiledArtifact] = []
            applied: list[str] = []
            for artifact in compiled.artifacts:
                normalized = _normalize(artifact.content)
                if normalized != artifact.content:
                    applied.append(f"normalize:{artifact.path}")
                optimized = CompiledArtifact(
                    path=artifact.path, kind=artifact.kind, content=normalized
                )
                self._assert_traceability(optimized, compiled.blueprint_id, canonical_source)
                new_artifacts.append(optimized)
        result = CompiledBlueprint(
            blueprint_id=compiled.blueprint_id,
            provenance_chain=compiled.provenance_chain,
            generation_framework=compiled.generation_framework,
            artifacts=tuple(new_artifacts),
        )
        _logger.info(
            "compiler.blueprint.optimized",
            blueprint=compiled.blueprint_id,
            transforms=len(applied),
        )
        return OptimizedBlueprint(blueprint=result, applied=tuple(applied))

    @staticmethod
    def _assert_traceability(
        artifact: CompiledArtifact, blueprint_id: str, canonical_source: str
    ) -> None:
        # Config artifacts carry provenance as structured JSON fields; source and
        # schema carry it in a header line. In all cases the blueprint id and the
        # canonical source id must survive the transform (Mandatory Rule 6).
        if blueprint_id not in artifact.content or (
            canonical_source and canonical_source not in artifact.content
        ):
            raise OptimizationError(
                "optimization would drop provenance; refused",
                blueprint_id=blueprint_id,
                path=artifact.path,
            )


__all__ = ["OptimizedBlueprint", "Optimizer"]
