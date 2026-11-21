"""Repository/storage-agnostic configuration — re-exported plus a nested sink.

``intelligence.rie.config`` owns ``resolve_repo_root``, ``RepoConfig`` and the
``OutputSink``/``FileSink``/``MemorySink`` interface. The kernel re-exports them
(no second source of truth) and adds:

  * :class:`NestedFileSink` — a file sink that accepts *relative* output names
    containing directory segments (``publications/research-paper.md``), which the
    publication subsystem needs and which no existing sink provides.
  * :func:`subsystem_config` — resolve a :class:`RepoConfig` whose ``output_dir``
    is a subsystem-owned directory under ``intelligence/``, so every write is
    contained inside a single, guardable write scope.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from intelligence.rie.config import (
    FileSink,
    MemorySink,
    OutputSink,
    RepoConfig,
    resolve_repo_root,
)

#: The one directory tree any intelligence subsystem may write into.
WRITE_SCOPE_ROOT = "intelligence"


@dataclass
class NestedFileSink(FileSink):
    """A :class:`FileSink` that honours directory segments in the output name."""

    def emit(self, name: str, canonical_text: str) -> str:
        target = self.directory / name
        if not self._contained(target):
            raise ValueError(f"output name escapes the sink directory: {name!r}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(canonical_text, encoding="utf-8")
        return str(target)

    def _contained(self, target: Path) -> bool:
        root = self.directory.resolve()
        resolved = Path(target).resolve() if target.exists() else self._resolve_virtual(target)
        return resolved == root or root in resolved.parents

    @staticmethod
    def _resolve_virtual(target: Path) -> Path:
        """Resolve a not-yet-existing path without touching the filesystem."""
        parts: list[str] = []
        for part in target.parts:
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)
        return Path(*parts) if parts else Path("/")


def subsystem_config(subsystem_dir: str, repo_root: Path | None = None) -> RepoConfig:
    """Return a :class:`RepoConfig` writing into ``intelligence/<subsystem_dir>``."""
    return RepoConfig.create(repo_root, output_subdir=f"{WRITE_SCOPE_ROOT}/{subsystem_dir}")


__all__ = [
    "WRITE_SCOPE_ROOT",
    "FileSink",
    "MemorySink",
    "NestedFileSink",
    "OutputSink",
    "RepoConfig",
    "resolve_repo_root",
    "subsystem_config",
]
