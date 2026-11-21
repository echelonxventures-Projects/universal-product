"""TASK-000025/000029 — Packaging Stage tests (deterministic package + manifest)."""

from __future__ import annotations

import pytest

from engine.compiler.data_compiler import (
    ArtifactKind,
    CompiledArtifact,
    CompiledBlueprint,
    DataBlueprintCompiler,
)
from engine.compiler.errors import PackagingError
from engine.compiler.optimization import Optimizer
from engine.compiler.packaging import (
    COMPILER_TOOLCHAIN,
    PACKAGE_FORMAT,
    Packager,
)
from engine.compiler.parser import parse_document


def _package(data_blueprint):
    ir = parse_document(data_blueprint)
    compiled = DataBlueprintCompiler().compile(ir)
    optimized = Optimizer().optimize(compiled)
    return Packager().package(optimized, name=ir.name, version=ir.version)


def test_package_manifest_shape(data_blueprint):
    package = _package(data_blueprint)
    manifest = package.manifest
    assert manifest["package_format"] == PACKAGE_FORMAT
    assert manifest["toolchain"]["compiler"] == COMPILER_TOOLCHAIN
    assert manifest["blueprint_id"] == "BP-DATA-0001"
    assert manifest["provenance"]["chain"][0] == "BP-DATA-0001"
    assert len(manifest["artifacts"]) == 3
    # deterministic ordering by path
    paths = [a["path"] for a in manifest["artifacts"]]
    assert paths == sorted(paths)
    assert package.artifact_paths() == tuple(sorted(package.artifact_paths()))


def test_package_hash_is_deterministic(data_blueprint):
    assert _package(data_blueprint).package_hash == _package(data_blueprint).package_hash


def test_package_accepts_compiled_blueprint_directly(data_blueprint):
    ir = parse_document(data_blueprint)
    compiled = DataBlueprintCompiler().compile(ir)
    package = Packager().package(compiled, name=ir.name, version=ir.version)
    assert package.blueprint_id == "BP-DATA-0001"


def test_package_rejects_empty_artifacts():
    empty = CompiledBlueprint(
        blueprint_id="BP-DATA-0001",
        provenance_chain=("BP-DATA-0001",),
        generation_framework="UCOS-GEN-000003",
        artifacts=(),
    )
    with pytest.raises(PackagingError):
        Packager().package(empty, name="X", version="1.0.0")


def test_package_rejects_duplicate_paths():
    dup = CompiledArtifact(path="a.sql", kind=ArtifactKind.SQL_SCHEMA, content="x\n")
    blueprint = CompiledBlueprint(
        blueprint_id="BP-DATA-0001",
        provenance_chain=("BP-DATA-0001",),
        generation_framework="UCOS-GEN-000003",
        artifacts=(dup, dup),
    )
    with pytest.raises(PackagingError):
        Packager().package(blueprint, name="X", version="1.0.0")
