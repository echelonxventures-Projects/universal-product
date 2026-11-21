"""URI-000001 — repository-agnostic, storage-agnostic configuration.

No absolute path is ever hardcoded. The repository root is resolved by walking upward
until the canonical markers are found, exactly as :mod:`intelligence.rie` does, and the
sink abstraction is **reused** from that subsystem rather than duplicated
(compose-never-duplicate).

Three output surfaces are configured, and only these three are ever written:

* ``artifact_root``  — ``<repo>/realization`` : the generated artifacts themselves.
* ``evidence_dir``   — ``<repo>/data/_evidence/URI-000001`` : the evidence bundle
  (UCIC-001 Output 5 binding).
* ``knowledge_dir``  — ``<repo>/knowledge`` : **read-only** here; URI never writes
  canonical knowledge (it has no authority to author it).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from intelligence.rie.config import FileSink, MemorySink, OutputSink

#: Markers that identify a UCOS-shaped repository root.
_MARKERS = ("engine", "knowledge")

#: The capability identifier this subsystem realizes under.
CAPABILITY_ID = "URI-000001"

#: Default, non-frozen home for generated realization artifacts.
ARTIFACT_DIRNAME = "realization"

#: Default evidence home (UCIC-001 Output 5: ``data/_evidence/<CAP-ID>/``).
EVIDENCE_PARENT = "data/_evidence"


def resolve_repo_root(start: Path | None = None) -> Path:
    """Find the repository root by locating the canonical markers upward from ``start``."""
    here = (start or Path(__file__)).resolve()
    for candidate in (here, *here.parents):
        if all((candidate / marker).exists() for marker in _MARKERS):
            return candidate
    # intelligence/realization/config.py -> parents[2] is the repository root.
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class RealizationConfig:
    """Resolved locations for the realization pipeline. All paths are absolute."""

    repo_root: Path
    knowledge_dir: Path
    artifact_root: Path
    evidence_dir: Path

    @classmethod
    def create(
        cls,
        repo_root: Path | str | None = None,
        *,
        artifact_root: Path | str | None = None,
        evidence_dir: Path | str | None = None,
        knowledge_dir: Path | str | None = None,
    ) -> RealizationConfig:
        """Build a configuration, defaulting every surface from the repository root."""
        root = Path(repo_root).resolve() if repo_root else resolve_repo_root()
        return cls(
            repo_root=root,
            knowledge_dir=Path(knowledge_dir).resolve() if knowledge_dir else root / "knowledge",
            artifact_root=Path(artifact_root).resolve()
            if artifact_root
            else root / ARTIFACT_DIRNAME,
            evidence_dir=Path(evidence_dir).resolve()
            if evidence_dir
            else root / EVIDENCE_PARENT / CAPABILITY_ID,
        )

    def rel(self, path: Path) -> str:
        """Return ``path`` relative to the repository root when possible (POSIX form)."""
        try:
            return path.resolve().relative_to(self.repo_root).as_posix()
        except ValueError:
            return path.as_posix()

    def artifact_path(self, relative: str) -> Path:
        """Resolve a generated artifact's repository-relative path under the artifact root."""
        return self.artifact_root / relative


__all__ = [
    "ARTIFACT_DIRNAME",
    "CAPABILITY_ID",
    "EVIDENCE_PARENT",
    "FileSink",
    "MemorySink",
    "OutputSink",
    "RealizationConfig",
    "resolve_repo_root",
]
