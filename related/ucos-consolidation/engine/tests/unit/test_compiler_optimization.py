"""TASK-000024/000029 — Optimization Stage tests (semantics/traceability preserving)."""

from __future__ import annotations

import pytest

from engine.compiler.data_compiler import (
    ArtifactKind,
    CompiledArtifact,
    CompiledBlueprint,
    DataBlueprintCompiler,
)
from engine.compiler.errors import OptimizationError
from engine.compiler.optimization import Optimizer
from engine.compiler.parser import parse_document


def _compiled(data_blueprint) -> CompiledBlueprint:
    return DataBlueprintCompiler().compile(parse_document(data_blueprint))


def test_optimize_preserves_provenance_and_normalises(data_blueprint):
    compiled = _compiled(data_blueprint)
    result = Optimizer().optimize(compiled)
    for artifact in result.blueprint.artifacts:
        assert "BP-DATA-0001" in artifact.content
        assert artifact.content.endswith("\n")
        assert "  \n" not in artifact.content  # no trailing whitespace
        assert "\n\n\n" not in artifact.content  # no triple blank lines


def test_optimize_reports_applied_transforms():
    # An artifact with trailing whitespace + excess blanks should be normalised.
    dirty = CompiledArtifact(
        path="config/x.json",
        kind=ArtifactKind.CONFIG,
        content='{"blueprint_id":"BP-DATA-0001","src":"UCOS-DAT-000007"}   \n\n\n\n',
    )
    compiled = CompiledBlueprint(
        blueprint_id="BP-DATA-0001",
        provenance_chain=("BP-DATA-0001", "UCOS-DAT-000007"),
        generation_framework="UCOS-GEN-000003",
        artifacts=(dirty,),
    )
    result = Optimizer().optimize(compiled)
    assert result.applied == ("normalize:config/x.json",)


def test_optimize_is_idempotent(data_blueprint):
    compiled = _compiled(data_blueprint)
    once = Optimizer().optimize(compiled).blueprint
    twice = Optimizer().optimize(once)
    assert twice.applied == ()  # already normalised — nothing to do


def test_optimize_refuses_to_drop_provenance():
    artifact = CompiledArtifact(
        path="schema/x.sql", kind=ArtifactKind.SQL_SCHEMA, content="SELECT 1;\n"
    )
    compiled = CompiledBlueprint(
        blueprint_id="BP-DATA-0001",
        provenance_chain=("BP-DATA-0001", "UCOS-DAT-000007"),
        generation_framework="UCOS-GEN-000003",
        artifacts=(artifact,),
    )
    with pytest.raises(OptimizationError) as exc:
        Optimizer().optimize(compiled)
    assert exc.value.context["blueprint_id"] == "BP-DATA-0001"
