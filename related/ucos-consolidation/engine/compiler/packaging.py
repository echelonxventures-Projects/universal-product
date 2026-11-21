"""TASK-000025 — Packaging Stage (EPIC-003, IMP-007 §7).

Assembles the compiled (and optimized) artifacts of a blueprint into a single,
deterministic, versioned **package** with a manifest. Packaging is a compilation
invariant of reproducibility (IMP-007 §5): the manifest embeds a **fixed artifact
ordering** (sorted by path), pinned toolchain identity, per-artifact SHA-256
hashes, and the full provenance chain — but **no timestamps or ambient state** —
so identical inputs yield a byte-identical package and a stable ``package_hash``.

The package embeds the provenance chain (Mandatory Rule 6) and contains no
secrets (SEC-04). Stdlib-only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from engine.compiler.data_compiler import CompiledArtifact, CompiledBlueprint
from engine.compiler.errors import PackagingError
from engine.compiler.optimization import OptimizedBlueprint
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("compiler.package")

#: Package manifest format version and pinned compiler toolchain identity.
PACKAGE_FORMAT = "1.0.0"
COMPILER_TOOLCHAIN = "ucos-imp-007-universal-compiler"
TOOLCHAIN_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class Package:
    """A deterministic, versioned package of compiled artifacts (IMP-007 §7)."""

    blueprint_id: str
    name: str
    version: str
    artifacts: tuple[CompiledArtifact, ...]
    manifest: dict[str, Any]
    package_hash: str

    def artifact_paths(self) -> tuple[str, ...]:
        """Every artifact path, in deterministic (sorted) order."""
        return tuple(a.path for a in self.artifacts)


def _as_compiled(blueprint: CompiledBlueprint | OptimizedBlueprint) -> CompiledBlueprint:
    if isinstance(blueprint, OptimizedBlueprint):
        return blueprint.blueprint
    return blueprint


class Packager:
    """Assembles a compiled blueprint into a deterministic package."""

    __slots__ = ()

    def package(
        self,
        blueprint: CompiledBlueprint | OptimizedBlueprint,
        *,
        name: str,
        version: str,
    ) -> Package:
        """Assemble ``blueprint`` into a signed-ready :class:`Package`."""
        compiled = _as_compiled(blueprint)
        if not compiled.artifacts:
            raise PackagingError(
                "cannot package a blueprint with no artifacts",
                blueprint_id=compiled.blueprint_id,
            )
        with trace("compiler.package", blueprint=compiled.blueprint_id):
            ordered = tuple(sorted(compiled.artifacts, key=lambda a: a.path))
            paths = [a.path for a in ordered]
            if len(set(paths)) != len(paths):
                raise PackagingError(
                    "duplicate artifact paths in package",
                    blueprint_id=compiled.blueprint_id,
                )
            manifest = self._build_manifest(compiled, ordered, name=name, version=version)
            package_hash = _hash_manifest(manifest)
        _logger.info(
            "compiler.blueprint.packaged",
            blueprint=compiled.blueprint_id,
            artifacts=len(ordered),
            package_hash=package_hash,
        )
        return Package(
            blueprint_id=compiled.blueprint_id,
            name=name,
            version=version,
            artifacts=ordered,
            manifest=manifest,
            package_hash=package_hash,
        )

    @staticmethod
    def _build_manifest(
        compiled: CompiledBlueprint,
        ordered: tuple[CompiledArtifact, ...],
        *,
        name: str,
        version: str,
    ) -> dict[str, Any]:
        return {
            "package_format": PACKAGE_FORMAT,
            "blueprint_id": compiled.blueprint_id,
            "name": name,
            "version": version,
            "toolchain": {
                "compiler": COMPILER_TOOLCHAIN,
                "compiler_version": TOOLCHAIN_VERSION,
            },
            "provenance": {
                "chain": list(compiled.provenance_chain),
                "generation_framework": compiled.generation_framework,
            },
            "artifacts": [
                {
                    "path": a.path,
                    "kind": a.kind.value,
                    "sha256": a.content_hash,
                    "bytes": a.byte_length,
                }
                for a in ordered
            ],
        }


def _hash_manifest(manifest: dict[str, Any]) -> str:
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = [
    "PACKAGE_FORMAT",
    "COMPILER_TOOLCHAIN",
    "TOOLCHAIN_VERSION",
    "Package",
    "Packager",
]
