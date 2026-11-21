"""URI-000001 — the Implementation Engine.

The only component in the subsystem permitted to write to disk, and the only one that
therefore needs a guard. Everything upstream is pure; materialization is where a mistake
could damage a repository, so the rules are narrow and enforced before the first byte is
written:

* **Frozen-corpus refusal (DP-03 / UCKO-PRIN-0002)** — every target path is checked
  against the Foundation frozen-path guard *and* against escaping the configured artifact
  root. A single offending artifact aborts the whole pass; nothing partial is written.
* **Additive surface only** — writes land under the configured ``artifact_root``. Path
  traversal (``..``), absolute paths, and symlinked parents are rejected.
* **Idempotence** — an artifact whose on-disk bytes already match is reported
  ``unchanged`` and left untouched, so re-running realization is a no-op and the
  repository stays byte-stable.
* **Write-then-verify** — after writing, the bytes are read back and hashed. A mismatch
  raises rather than being recorded as success.
* **Dry run** — ``dry_run=True`` computes the identical record while writing nothing, so
  the effect of a realization can be reviewed before it happens.

Pruning of stale artifacts is *opt-in* and confined to the artifact root: it only removes
files that a previous URI pass generated (identified by the manifest of record), never
arbitrary files it happens to find.
"""

from __future__ import annotations

import json
from pathlib import Path

from engine.foundation.guards.frozen_paths import find_frozen_writes
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from intelligence.realization.canonical import document_json, sealed, sha256_text
from intelligence.realization.config import RealizationConfig
from intelligence.realization.contracts import (
    GeneratedArtifact,
    GenerationManifest,
    ImplementationRecord,
    MaterializedFile,
)
from intelligence.realization.errors import FrozenSurfaceError, ImplementationError

_logger = get_logger("intelligence.realization.implementation")

#: The manifest of record, written alongside the artifacts it describes.
MANIFEST_FILENAME = "UCOS-URI-MANIFEST.json"

ACTION_CREATED = "created"
ACTION_UPDATED = "updated"
ACTION_UNCHANGED = "unchanged"
ACTION_PLANNED = "planned"


class ImplementationEngine:
    """Materializes generated artifacts onto the declared additive surface."""

    def __init__(self, config: RealizationConfig | None = None) -> None:
        self.config = config or RealizationConfig.create()

    # -- guards ---------------------------------------------------------------

    def _resolve(self, relative_path: str) -> Path:
        """Resolve and validate one artifact path against the additive surface."""
        if not relative_path or relative_path.startswith("/"):
            raise ImplementationError(
                "artifact path must be repository-relative", path=relative_path
            )
        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ImplementationError("artifact path escapes the artifact root", path=relative_path)
        root = self.config.artifact_root
        resolved = (root / candidate).resolve()
        if root.resolve() not in resolved.parents:
            raise ImplementationError(
                "resolved artifact path is outside the artifact root",
                path=relative_path,
                artifact_root=str(root),
            )
        self._assert_not_frozen(resolved, relative_path)
        return resolved

    def _assert_not_frozen(self, resolved: Path, relative_path: str) -> None:
        """Refuse any write that would land inside the frozen corpus (DP-03)."""
        try:
            repo_relative = resolved.relative_to(self.config.repo_root)
        except ValueError:
            return  # outside the repository (a test tmp dir) — the root check already ran
        offending = find_frozen_writes([repo_relative.as_posix()])
        if offending:
            raise FrozenSurfaceError(
                "refusing to write a generated artifact into the frozen corpus",
                path=relative_path,
                repository_path=repo_relative.as_posix(),
                frozen=list(offending),
            )

    def preflight(self, manifest: GenerationManifest) -> tuple[Path, ...]:
        """Validate every target path before writing anything. Fail-closed."""
        if not manifest.artifacts:
            raise ImplementationError(
                "generation manifest is empty; nothing to materialize",
                generation_id=manifest.generation_id,
            )
        return tuple(self._resolve(artifact.relative_path) for artifact in manifest.artifacts)

    # -- materialization ------------------------------------------------------

    def materialize(
        self, manifest: GenerationManifest, *, dry_run: bool = False
    ) -> ImplementationRecord:
        """Write (or plan) every artifact, then verify what was written."""
        with trace(
            "realization.materialize",
            generation_id=manifest.generation_id,
            artifacts=len(manifest.artifacts),
            dry_run=dry_run,
        ):
            targets = self.preflight(manifest)
            files: list[MaterializedFile] = []
            for artifact, path in zip(manifest.artifacts, targets, strict=True):
                files.append(self._write(artifact, path, dry_run=dry_run))
            record = ImplementationRecord(
                generation_id=manifest.generation_id,
                generation_seal=manifest.seal,
                knowledge_seal=manifest.knowledge_seal,
                artifact_root=self.config.rel(self.config.artifact_root),
                files=tuple(sorted(files, key=lambda f: f.relative_path)),
                dry_run=dry_run,
                verified=not dry_run,
            )
            if not dry_run:
                self._verify(manifest)
                self._write_manifest(manifest, record)
            _logger.info(
                "realization.materialized",
                implementation_id=record.implementation_id,
                files=len(record.files),
                actions=record.actions(),
                dry_run=dry_run,
            )
            return record

    def _write(self, artifact: GeneratedArtifact, path: Path, *, dry_run: bool) -> MaterializedFile:
        digest = artifact.content_sha256
        existing = self._existing_hash(path)
        if dry_run:
            action = (
                ACTION_UNCHANGED
                if existing == digest
                else f"{ACTION_PLANNED}:{ACTION_CREATED if existing is None else ACTION_UPDATED}"
            )
        elif existing == digest:
            action = ACTION_UNCHANGED
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(artifact.content, encoding="utf-8")
            action = ACTION_CREATED if existing is None else ACTION_UPDATED
        return MaterializedFile(
            relative_path=artifact.relative_path,
            artifact_id=artifact.artifact_id,
            content_sha256=digest,
            size=artifact.size,
            action=action,
        )

    @staticmethod
    def _existing_hash(path: Path) -> str | None:
        if not path.is_file():
            return None
        return sha256_text(path.read_text(encoding="utf-8"))

    # -- verification ---------------------------------------------------------

    def _verify(self, manifest: GenerationManifest) -> None:
        """Read every artifact back and require the bytes to match the seal."""
        mismatches: list[dict[str, str]] = []
        for artifact in manifest.artifacts:
            path = self._resolve(artifact.relative_path)
            actual = self._existing_hash(path)
            if actual != artifact.content_sha256:
                mismatches.append(
                    {
                        "path": artifact.relative_path,
                        "expected": artifact.content_sha256,
                        "actual": actual or "absent",
                    }
                )
        if mismatches:
            raise ImplementationError(
                "materialized bytes do not match the generated artifact seal",
                mismatches=mismatches,
            )

    def verify(self, manifest: GenerationManifest) -> dict[str, object]:
        """Non-raising verification of what is currently on disk."""
        results = []
        for artifact in manifest.artifacts:
            path = self._resolve(artifact.relative_path)
            actual = self._existing_hash(path)
            results.append(
                {
                    "path": artifact.relative_path,
                    "expected": artifact.content_sha256,
                    "actual": actual,
                    "present": actual is not None,
                    "matched": actual == artifact.content_sha256,
                }
            )
        failed = [entry for entry in results if not entry["matched"]]
        return {
            "verified": not failed,
            "checked": len(results),
            "failed": failed,
            "artifact_root": self.config.rel(self.config.artifact_root),
        }

    # -- manifest of record ---------------------------------------------------

    def manifest_path(self) -> Path:
        return self.config.artifact_root / MANIFEST_FILENAME

    def _write_manifest(self, manifest: GenerationManifest, record: ImplementationRecord) -> Path:
        path = self.manifest_path()
        self._assert_not_frozen(path.resolve(), MANIFEST_FILENAME)
        payload = sealed(
            {
                "artifact_id": "UCOS-URI-MANIFEST",
                "title": "Realized Artifact Manifest",
                "document_format": "ucos-uri-manifest/1.0.0",
                "capability": "URI-000001",
                "authority": "NONE (derived from canonical knowledge)",
                "generation": manifest.to_dict(),
                # Canonical: the manifest is a generated artifact that a pristine
                # clone must reproduce byte-for-byte, so it may carry no observation
                # of the run that wrote it. The actions remain on the returned record
                # and in the structured log, where they are evidence.
                "implementation": record.to_canonical_dict(),
            }
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(document_json(payload), encoding="utf-8")
        return path

    # -- pruning (opt-in, bounded) --------------------------------------------

    def stale_artifacts(self, manifest: GenerationManifest) -> tuple[str, ...]:
        """Files a previous URI pass generated that the current manifest no longer claims."""
        previous = self._previous_paths()
        current = set(manifest.paths())
        return tuple(sorted(path for path in previous if path not in current))

    def _previous_paths(self) -> set[str]:
        path = self.manifest_path()
        if not path.is_file():
            return set()
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return set()
        artifacts = document.get("generation", {}).get("artifacts", [])
        return {
            entry["relative_path"]
            for entry in artifacts
            if isinstance(entry, dict) and entry.get("relative_path")
        }

    def prune(self, manifest: GenerationManifest, *, dry_run: bool = True) -> dict[str, object]:
        """Remove artifacts a previous pass generated that are no longer claimed."""
        stale = self.stale_artifacts(manifest)
        removed: list[str] = []
        for relative_path in stale:
            target = self._resolve(relative_path)
            if not target.is_file():
                continue
            if not dry_run:
                target.unlink()
            removed.append(relative_path)
        return {
            "dry_run": dry_run,
            "stale": list(stale),
            "removed": removed,
            "scope": self.config.rel(self.config.artifact_root),
        }


def materialize_artifacts(
    manifest: GenerationManifest,
    config: RealizationConfig | None = None,
    *,
    dry_run: bool = False,
) -> ImplementationRecord:
    """Convenience entry point: materialize a generation manifest."""
    return ImplementationEngine(config).materialize(manifest, dry_run=dry_run)


__all__ = [
    "ACTION_CREATED",
    "ACTION_PLANNED",
    "ACTION_UNCHANGED",
    "ACTION_UPDATED",
    "MANIFEST_FILENAME",
    "ImplementationEngine",
    "materialize_artifacts",
]
