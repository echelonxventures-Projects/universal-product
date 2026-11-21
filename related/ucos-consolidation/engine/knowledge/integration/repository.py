"""UKI — Constitutional Repository Discovery & Assimilation (EPIC-UKDA-004).

Completes the Universal Knowledge Architecture by teaching the **existing**
:class:`~engine.knowledge.integration.pipeline.ConstitutionalPipeline` to accept a
*live repository* and produce a fully assimilated :class:`RepositorySubject` ready
for downstream Validation, Certification, and Acceptance.

It adds **only the missing capabilities** and reuses everything else verbatim:

    * :class:`RepositoryProbe` — the single impure boundary. It reads a live working
      tree (filesystem + optional ``git``) and returns an immutable, deterministic
      :class:`RepositorySnapshot`. Nothing downstream touches disk or a clock, so
      assimilation is byte-reproducible for an identical snapshot (IMP-007 §5).
    * pure analyzers — ``discover``/``frontier``/``drift``/``checkpoints``/
      ``workstreams`` project the snapshot into the report value types.
    * :class:`RepositoryAssimilator` — projects each discovered repository unit into
      an :class:`~engine.knowledge.integration.contracts.ArtifactIntent` and drives
      the *existing* ``ConstitutionalPipeline`` (no new execution controller). Ownership,
      dependency, reuse, and discovery are therefore performed by the existing engines
      — never re-implemented. It then binds the assimilated units into a canonical
      base and reuses ``validate_base`` and ``certify_base`` to attest the subject.
    * :class:`RepositorySubject` — the canonical, immutable assimilation result, and
      :func:`emit_evidence` — the deterministic on-disk report bundle (Repository
      Discovery / Frontier / Drift reports + Assimilation Evidence).

The module is standard-library only (TP-04/TP-05) and never mutates the certified
corpus (DP-03).
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import tomllib
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.knowledge.certification import certify_base
from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.integration.contracts import ArtifactIntent, Operation
from engine.knowledge.integration.errors import RepositoryDiscoveryError
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.validation import validate_base

#: Recognised source-code file extensions (generic ecosystem conventions, overridable).
SOURCE_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".py",
        ".pyi",
        ".ipynb",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".ts",
        ".tsx",
        ".go",
        ".rs",
        ".java",
        ".kt",
        ".kts",
        ".scala",
        ".c",
        ".h",
        ".cc",
        ".cpp",
        ".hpp",
        ".cxx",
        ".cs",
        ".rb",
        ".php",
        ".swift",
        ".m",
        ".mm",
        ".sh",
        ".bash",
        ".zsh",
        ".sql",
        ".proto",
        ".graphql",
    }
)

#: Directory names never treated as repository units (generic, non-source, overridable).
DEFAULT_IGNORES: frozenset[str] = frozenset(
    {"__pycache__", "node_modules", "venv", ".venv", "site-packages", "dist", "build"}
)

#: The default owner assigned to a discovered unit that no ownership signal claims.
DEFAULT_REPOSITORY_OWNER = "UCOS-REPOSITORY-STEWARD"

#: The candidate CODEOWNERS locations, in precedence order.
_CODEOWNERS_LOCATIONS: tuple[str, ...] = ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS")

_VERSION = "1.0.0"

#: Schema identifiers for the emitted, self-contained report artifacts.
SCHEMA_DISCOVERY = "ucos-ukda-repository-discovery-report"
SCHEMA_FRONTIER = "ucos-ukda-repository-frontier-report"
SCHEMA_DRIFT = "ucos-ukda-repository-drift-report"
SCHEMA_ASSIMILATION = "ucos-ukda-repository-assimilation-evidence"


def _slug(text: str) -> str:
    """Return a deterministic, upper-case, dash-delimited slug of ``text``."""
    out: list[str] = []
    prev_dash = False
    for ch in text.strip().upper():
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    return "".join(out).strip("-") or "REPO"


def _split_requirement(spec: str) -> tuple[str, str | None]:
    """Split a dependency spec into ``(name, version_or_none)`` (best-effort, generic)."""
    spec = spec.strip()
    match = re.match(r"^([A-Za-z0-9_.\-]+)(.*)$", spec)
    if not match:
        return spec, None
    rest = match.group(2).strip()
    return match.group(1), (rest or None)


# --------------------------------------------------------------------------- values


@dataclass(frozen=True, slots=True)
class CommitRef:
    """An immutable reference to a single commit (checkpoint candidate)."""

    sha: str
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {"sha": self.sha, "summary": self.summary}


@dataclass(frozen=True, slots=True)
class OwnershipSignal:
    """A single ownership claim discovered in the repository (e.g. CODEOWNERS)."""

    pattern: str
    owners: tuple[str, ...]
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {"pattern": self.pattern, "owners": list(self.owners), "source": self.source}


@dataclass(frozen=True, slots=True)
class DependencySignal:
    """A single dependency discovered in a declared repository manifest."""

    name: str
    version: str | None
    manifest: str
    kind: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "manifest": self.manifest,
            "kind": self.kind,
        }


@dataclass(frozen=True, slots=True)
class RepositoryUnit:
    """A discovered, top-level unit of a repository (a candidate capability subtree)."""

    unit_id: str
    path: str
    realized: bool
    source_files: int
    total_files: int
    owner: str
    languages: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "path": self.path,
            "realized": self.realized,
            "source_files": self.source_files,
            "total_files": self.total_files,
            "owner": self.owner,
            "languages": list(self.languages),
        }


@dataclass(frozen=True, slots=True)
class RepositoryCheckpoint:
    """A stable implementation checkpoint (the HEAD commit or a tag)."""

    checkpoint_id: str
    ref: str
    kind: str
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "ref": self.ref,
            "kind": self.kind,
            "summary": self.summary,
        }


@dataclass(frozen=True, slots=True)
class Workstream:
    """An active workstream: a branch, or the uncommitted working tree."""

    workstream_id: str
    name: str
    kind: str
    active: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "workstream_id": self.workstream_id,
            "name": self.name,
            "kind": self.kind,
            "active": self.active,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class FrontierItem:
    """An implementation frontier item: an authorized-but-unrealized repository unit."""

    unit_id: str
    path: str
    reason: str
    status: str = "authorized-frontier"

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "path": self.path,
            "reason": self.reason,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class DriftItem:
    """A single divergence between the committed baseline and the working tree."""

    path: str
    kind: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "kind": self.kind, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class RepositorySnapshot:
    """The immutable, deterministic capture of a live repository (probe output)."""

    name: str
    root: str
    universe: str
    head: str | None
    branch: str | None
    default_branch: str | None
    git_available: bool
    units: tuple[RepositoryUnit, ...]
    ownership: tuple[OwnershipSignal, ...]
    dependencies: tuple[DependencySignal, ...]
    tags: tuple[str, ...]
    branches: tuple[str, ...]
    commits: tuple[CommitRef, ...]
    staged: tuple[str, ...]
    modified: tuple[str, ...]
    untracked: tuple[str, ...]

    @property
    def repository_id(self) -> str:
        """The canonical, deterministic identity of the repository subject."""
        return f"REPO-{self.universe}"

    def realized_units(self) -> tuple[RepositoryUnit, ...]:
        return tuple(u for u in self.units if u.realized)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "root": self.root,
            "universe": self.universe,
            "repository_id": self.repository_id,
            "head": self.head,
            "branch": self.branch,
            "default_branch": self.default_branch,
            "git_available": self.git_available,
            "units": [u.to_dict() for u in self.units],
            "ownership": [o.to_dict() for o in self.ownership],
            "dependencies": [d.to_dict() for d in self.dependencies],
            "tags": list(self.tags),
            "branches": list(self.branches),
            "commits": [c.to_dict() for c in self.commits],
            "staged": list(self.staged),
            "modified": list(self.modified),
            "untracked": list(self.untracked),
        }


# --------------------------------------------------------------------------- reports


@dataclass(frozen=True, slots=True)
class RepositoryDiscoveryReport:
    """Repository Discovery Report — units, ownership, dependencies, and checkpoints."""

    units: tuple[RepositoryUnit, ...]
    ownership: tuple[OwnershipSignal, ...]
    dependencies: tuple[DependencySignal, ...]
    checkpoints: tuple[RepositoryCheckpoint, ...]

    def counts(self) -> dict[str, int]:
        return {
            "units": len(self.units),
            "realized_units": sum(1 for u in self.units if u.realized),
            "ownership_signals": len(self.ownership),
            "dependencies": len(self.dependencies),
            "checkpoints": len(self.checkpoints),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": self.counts(),
            "units": [u.to_dict() for u in self.units],
            "ownership": [o.to_dict() for o in self.ownership],
            "dependencies": [d.to_dict() for d in self.dependencies],
            "checkpoints": [c.to_dict() for c in self.checkpoints],
        }


@dataclass(frozen=True, slots=True)
class RepositoryFrontierReport:
    """Repository Frontier Report — realized units vs authorized-but-unrealized frontier."""

    realized: tuple[str, ...]
    frontier: tuple[FrontierItem, ...]

    def counts(self) -> dict[str, int]:
        return {"realized": len(self.realized), "frontier": len(self.frontier)}

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": self.counts(),
            "realized": list(self.realized),
            "frontier": [f.to_dict() for f in self.frontier],
        }


@dataclass(frozen=True, slots=True)
class RepositoryDriftReport:
    """Repository Drift Report — working-tree drift and active workstreams."""

    head: str | None
    branch: str | None
    drift: tuple[DriftItem, ...]
    workstreams: tuple[Workstream, ...]

    @property
    def clean(self) -> bool:
        return not self.drift

    def counts(self) -> dict[str, int]:
        return {
            "drift": len(self.drift),
            "workstreams": len(self.workstreams),
            "active_workstreams": sum(1 for w in self.workstreams if w.active),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "head": self.head,
            "branch": self.branch,
            "clean": self.clean,
            "counts": self.counts(),
            "drift": [d.to_dict() for d in self.drift],
            "workstreams": [w.to_dict() for w in self.workstreams],
        }


@dataclass(frozen=True, slots=True)
class UnitAssimilation:
    """The constitutional decision for one repository unit fed through the pipeline."""

    unit_id: str
    path: str
    intent_id: str
    outcome: str
    disposition: str
    accepted: bool
    reasons: tuple[str, ...]
    decision: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "path": self.path,
            "intent_id": self.intent_id,
            "outcome": self.outcome,
            "disposition": self.disposition,
            "accepted": self.accepted,
            "reasons": list(self.reasons),
            "decision": self.decision,
        }


@dataclass(frozen=True, slots=True)
class RepositoryAssimilationEvidence:
    """Repository Assimilation Evidence — per-unit pipeline decisions + subject attestation."""

    subject_id: str
    units: tuple[UnitAssimilation, ...]
    validation: dict[str, Any]
    certification: dict[str, Any]
    validated: bool
    certified: bool

    @property
    def units_accepted(self) -> bool:
        return all(u.accepted for u in self.units)

    @property
    def accepted(self) -> bool:
        """True iff every unit was accepted and the bound subject validated and certified."""
        return self.units_accepted and self.validated and self.certified

    def counts(self) -> dict[str, int]:
        return {
            "units": len(self.units),
            "accepted": sum(1 for u in self.units if u.accepted),
            "blocked": sum(1 for u in self.units if not u.accepted),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "accepted": self.accepted,
            "units_accepted": self.units_accepted,
            "validated": self.validated,
            "certified": self.certified,
            "counts": self.counts(),
            "units": [u.to_dict() for u in self.units],
            "validation": self.validation,
            "certification": self.certification,
        }


@dataclass(frozen=True, slots=True)
class RepositorySubject:
    """The canonical, immutable assimilation result for a live repository (EPIC-UKDA-004)."""

    repository_id: str
    name: str
    root: str
    universe: str
    head: str | None
    branch: str | None
    discovery: RepositoryDiscoveryReport
    frontier: RepositoryFrontierReport
    drift: RepositoryDriftReport
    assimilation: RepositoryAssimilationEvidence
    subject_object: dict[str, Any]

    @property
    def assimilated(self) -> bool:
        """True iff every unit was assimilated and the subject validated and certified."""
        return self.assimilation.accepted

    def header(self) -> dict[str, Any]:
        """The stable identity header echoed into every emitted report artifact."""
        return {
            "repository_id": self.repository_id,
            "name": self.name,
            "root": self.root,
            "universe": self.universe,
            "head": self.head,
            "branch": self.branch,
            "assimilated": self.assimilated,
        }

    def reports(self) -> dict[str, dict[str, Any]]:
        """The four self-contained report artifacts keyed by canonical filename."""
        header = self.header()
        return {
            "repository-discovery-report.json": {
                "schema": SCHEMA_DISCOVERY,
                "version": _VERSION,
                "repository": header,
                "report": self.discovery.to_dict(),
            },
            "repository-frontier-report.json": {
                "schema": SCHEMA_FRONTIER,
                "version": _VERSION,
                "repository": header,
                "report": self.frontier.to_dict(),
            },
            "repository-drift-report.json": {
                "schema": SCHEMA_DRIFT,
                "version": _VERSION,
                "repository": header,
                "report": self.drift.to_dict(),
            },
            "repository-assimilation-evidence.json": {
                "schema": SCHEMA_ASSIMILATION,
                "version": _VERSION,
                "repository": header,
                "report": self.assimilation.to_dict(),
            },
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.header(),
            "subject_object": self.subject_object,
            "discovery": self.discovery.to_dict(),
            "frontier": self.frontier.to_dict(),
            "drift": self.drift.to_dict(),
            "assimilation": self.assimilation.to_dict(),
        }


# --------------------------------------------------------------------------- probe


GitRunner = Callable[[Sequence[str]], str | None]


def _default_git_runner(root: Path) -> GitRunner:
    """Return a runner that executes read-only ``git`` commands under ``root``."""

    def run(args: Sequence[str]) -> str | None:
        try:
            proc = subprocess.run(  # noqa: S603 - fixed argv, no shell
                ["git", "-C", str(root), *args],  # noqa: S607 - git resolved on PATH by design
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError):  # pragma: no cover - git absent/aborted
            return None
        if proc.returncode != 0:
            return None
        return proc.stdout

    return run


def _first_line(text: str | None) -> str | None:
    if not text or not text.strip():
        return None
    return text.strip().splitlines()[0].strip()


def _lines(text: str | None) -> tuple[str, ...]:
    if not text:
        return ()
    return tuple(sorted(line.strip() for line in text.splitlines() if line.strip()))


def _parse_commits(text: str | None) -> tuple[CommitRef, ...]:
    if not text:
        return ()
    commits: list[CommitRef] = []
    for line in text.splitlines():
        if "\x1f" not in line:
            continue
        sha, summary = line.split("\x1f", 1)
        if sha.strip():
            commits.append(CommitRef(sha=sha.strip(), summary=summary.strip()))
    return tuple(commits)


def _parse_status(text: str | None) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    staged: list[str] = []
    modified: list[str] = []
    untracked: list[str] = []
    for line in (text or "").splitlines():
        if len(line) < 4:
            continue
        index, worktree, path = line[0], line[1], line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[-1].strip()
        if index == "?" and worktree == "?":
            untracked.append(path)
            continue
        if index not in (" ", "?"):
            staged.append(path)
        if worktree not in (" ", "?"):
            modified.append(path)
    return tuple(sorted(staged)), tuple(sorted(modified)), tuple(sorted(untracked))


def _pattern_matches(pattern: str, relpath: str) -> bool:
    normalized = pattern.strip().lstrip("/").rstrip("/")
    if normalized in ("", "*", "**"):
        return True
    return (
        relpath == normalized
        or relpath.startswith(normalized + "/")
        or fnmatch.fnmatch(relpath, normalized)
        or fnmatch.fnmatch(relpath, normalized + "/*")
    )


def _resolve_owner(relpath: str, ownership: Iterable[OwnershipSignal]) -> str:
    """Return the most specific (longest-pattern) owner claiming ``relpath``, else ""."""
    best_owner = ""
    best_len = -1
    for signal in ownership:
        if signal.owners and _pattern_matches(signal.pattern, relpath):
            score = len(signal.pattern.strip("/"))
            if score > best_len:
                best_len = score
                best_owner = signal.owners[0]
    return best_owner


class RepositoryProbe:
    """The single impure boundary: capture a live repository into a snapshot."""

    __slots__ = ("_source_extensions", "_ignore", "_max_commits")

    def __init__(
        self,
        *,
        source_extensions: Iterable[str] | None = None,
        ignore: Iterable[str] | None = None,
        max_commits: int = 20,
    ) -> None:
        self._source_extensions = (
            frozenset(source_extensions) if source_extensions is not None else SOURCE_EXTENSIONS
        )
        self._ignore = frozenset(ignore) if ignore is not None else DEFAULT_IGNORES
        self._max_commits = max_commits

    def capture(self, root: str | Path, *, git: GitRunner | None = None) -> RepositorySnapshot:
        """Capture ``root`` (filesystem + optional git) into an immutable snapshot."""
        root_path = Path(root).resolve()
        if not root_path.is_dir():
            raise RepositoryDiscoveryError(
                "repository root is not a directory", root=str(root_path)
            )
        runner = git if git is not None else _default_git_runner(root_path)

        head = _first_line(runner(["rev-parse", "HEAD"]))
        branch = _first_line(runner(["rev-parse", "--abbrev-ref", "HEAD"]))
        inside = _first_line(runner(["rev-parse", "--is-inside-work-tree"]))
        git_available = inside == "true" or head is not None
        tags = _lines(runner(["tag", "--list"]))
        branches = _lines(runner(["for-each-ref", "--format=%(refname:short)", "refs/heads"]))
        commits = _parse_commits(runner(["log", f"-{self._max_commits}", "--format=%H%x1f%s"]))
        staged, modified, untracked = _parse_status(runner(["status", "--porcelain"]))
        default_branch = self._default_branch(runner)

        ownership = self._discover_ownership(root_path)
        units = self._discover_units(root_path, ownership)
        dependencies = self._discover_dependencies(root_path)

        return RepositorySnapshot(
            name=root_path.name,
            root=root_path.as_posix(),
            universe=_slug(root_path.name),
            head=head,
            branch=branch,
            default_branch=default_branch,
            git_available=git_available,
            units=units,
            ownership=ownership,
            dependencies=dependencies,
            tags=tags,
            branches=branches,
            commits=commits,
            staged=staged,
            modified=modified,
            untracked=untracked,
        )

    @staticmethod
    def _default_branch(runner: GitRunner) -> str | None:
        ref = _first_line(runner(["symbolic-ref", "refs/remotes/origin/HEAD"]))
        if ref and "/" in ref:
            return ref.rsplit("/", 1)[-1]
        return None

    def _discover_ownership(self, root: Path) -> tuple[OwnershipSignal, ...]:
        signals: list[OwnershipSignal] = []
        for location in _CODEOWNERS_LOCATIONS:
            path = root / location
            if not path.is_file():
                continue
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                parts = stripped.split()
                if len(parts) < 2:
                    continue
                signals.append(
                    OwnershipSignal(pattern=parts[0], owners=tuple(parts[1:]), source=location)
                )
        return tuple(signals)

    def _discover_units(
        self, root: Path, ownership: Sequence[OwnershipSignal]
    ) -> tuple[RepositoryUnit, ...]:
        units: list[RepositoryUnit] = []
        slug = _slug(root.name)
        for entry in sorted(root.iterdir(), key=lambda p: p.name):
            if not entry.is_dir() or entry.name.startswith(".") or entry.name in self._ignore:
                continue
            source_files, total_files, languages = self._scan(entry)
            relpath = entry.relative_to(root).as_posix()
            units.append(
                RepositoryUnit(
                    unit_id=f"REPO-{slug}-UNIT-{_slug(relpath)}",
                    path=relpath,
                    realized=source_files > 0,
                    source_files=source_files,
                    total_files=total_files,
                    owner=_resolve_owner(relpath, ownership),
                    languages=languages,
                )
            )
        return tuple(units)

    def _scan(self, directory: Path) -> tuple[int, int, tuple[str, ...]]:
        source = 0
        total = 0
        languages: set[str] = set()
        for dirpath, dirnames, filenames in os.walk(directory):
            dirnames[:] = sorted(
                d for d in dirnames if not d.startswith(".") and d not in self._ignore
            )
            _ = dirpath
            for filename in filenames:
                if filename.startswith("."):
                    continue
                total += 1
                ext = Path(filename).suffix.lower()
                if ext in self._source_extensions:
                    source += 1
                    languages.add(ext.lstrip("."))
        return source, total, tuple(sorted(languages))

    def _discover_dependencies(self, root: Path) -> tuple[DependencySignal, ...]:
        signals: list[DependencySignal] = []
        signals.extend(self._pyproject_dependencies(root))
        signals.extend(self._package_json_dependencies(root))
        signals.extend(self._requirements_dependencies(root))
        return tuple(sorted(signals, key=lambda d: (d.manifest, d.kind, d.name)))

    @staticmethod
    def _pyproject_dependencies(root: Path) -> list[DependencySignal]:
        path = root / "pyproject.toml"
        if not path.is_file():
            return []
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            return []
        out: list[DependencySignal] = []
        project = data.get("project", {})
        for spec in project.get("dependencies", []) or []:
            name, version = _split_requirement(str(spec))
            out.append(DependencySignal(name, version, "pyproject.toml", "runtime"))
        for group, specs in (project.get("optional-dependencies", {}) or {}).items():
            for spec in specs or []:
                name, version = _split_requirement(str(spec))
                out.append(DependencySignal(name, version, "pyproject.toml", f"optional:{group}"))
        return out

    @staticmethod
    def _package_json_dependencies(root: Path) -> list[DependencySignal]:
        path = root / "package.json"
        if not path.is_file():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        out: list[DependencySignal] = []
        for key, kind in (("dependencies", "runtime"), ("devDependencies", "dev")):
            block = data.get(key) or {}
            if isinstance(block, dict):
                for name, version in sorted(block.items()):
                    out.append(
                        DependencySignal(str(name), str(version) or None, "package.json", kind)
                    )
        return out

    @staticmethod
    def _requirements_dependencies(root: Path) -> list[DependencySignal]:
        path = root / "requirements.txt"
        if not path.is_file():
            return []
        out: list[DependencySignal] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("-"):
                continue
            name, version = _split_requirement(stripped)
            out.append(DependencySignal(name, version, "requirements.txt", "runtime"))
        return out


# --------------------------------------------------------------------------- analyzers


def discover_checkpoints(snapshot: RepositorySnapshot) -> tuple[RepositoryCheckpoint, ...]:
    """Discover implementation checkpoints (the HEAD commit + every tag)."""
    checkpoints: list[RepositoryCheckpoint] = []
    if snapshot.head:
        summary = snapshot.commits[0].summary if snapshot.commits else ""
        checkpoints.append(
            RepositoryCheckpoint(
                checkpoint_id=f"CKPT-HEAD-{snapshot.head[:12]}",
                ref=snapshot.head,
                kind="head",
                summary=summary,
            )
        )
    for tag in snapshot.tags:
        checkpoints.append(
            RepositoryCheckpoint(
                checkpoint_id=f"CKPT-TAG-{_slug(tag)}", ref=tag, kind="tag", summary=""
            )
        )
    return tuple(checkpoints)


def discover_workstreams(snapshot: RepositorySnapshot) -> tuple[Workstream, ...]:
    """Discover active workstreams (branches + the uncommitted working tree)."""
    workstreams: list[Workstream] = []
    for name in snapshot.branches:
        active = name == snapshot.branch
        workstreams.append(
            Workstream(
                workstream_id=f"WS-BRANCH-{_slug(name)}",
                name=name,
                kind="branch",
                active=active,
                detail="checked-out branch" if active else "branch",
            )
        )
    if snapshot.staged or snapshot.modified or snapshot.untracked:
        detail = (
            f"{len(snapshot.staged)} staged, "
            f"{len(snapshot.modified)} modified, "
            f"{len(snapshot.untracked)} untracked"
        )
        workstreams.append(
            Workstream(
                workstream_id="WS-WORKING-TREE",
                name="working-tree",
                kind="working-tree",
                active=True,
                detail=detail,
            )
        )
    return tuple(workstreams)


def discover_frontier(snapshot: RepositorySnapshot) -> RepositoryFrontierReport:
    """Discover the implementation frontier: realized units vs authorized-unrealized units."""
    realized: list[str] = []
    frontier: list[FrontierItem] = []
    for unit in snapshot.units:
        if unit.realized:
            realized.append(unit.unit_id)
            continue
        reason = "empty-unit" if unit.total_files == 0 else "documentation-only"
        frontier.append(FrontierItem(unit_id=unit.unit_id, path=unit.path, reason=reason))
    return RepositoryFrontierReport(realized=tuple(sorted(realized)), frontier=tuple(frontier))


def discover_drift(snapshot: RepositorySnapshot) -> RepositoryDriftReport:
    """Detect repository drift (working-tree divergence) and active workstreams."""
    drift: list[DriftItem] = []
    for path in snapshot.staged:
        drift.append(DriftItem(path=path, kind="staged", detail="staged change vs HEAD"))
    for path in snapshot.modified:
        drift.append(DriftItem(path=path, kind="modified", detail="working-tree change vs index"))
    for path in snapshot.untracked:
        drift.append(
            DriftItem(path=path, kind="untracked", detail="file not under version control")
        )
    return RepositoryDriftReport(
        head=snapshot.head,
        branch=snapshot.branch,
        drift=tuple(drift),
        workstreams=discover_workstreams(snapshot),
    )


def discover_repository(snapshot: RepositorySnapshot) -> RepositoryDiscoveryReport:
    """Produce the Repository Discovery Report from a snapshot (units + signals + checkpoints)."""
    return RepositoryDiscoveryReport(
        units=snapshot.units,
        ownership=snapshot.ownership,
        dependencies=snapshot.dependencies,
        checkpoints=discover_checkpoints(snapshot),
    )


# --------------------------------------------------------------------------- assimilator


class RepositoryAssimilator:
    """Drives the existing ConstitutionalPipeline to assimilate a live repository.

    It creates **no** new execution controller: every unit is routed through the
    injected pipeline's ``execute`` method, so discovery, ownership, dependency, and
    reuse determination are performed by the existing engines. The assimilated units
    are then bound into a canonical base and attested with the existing knowledge
    validation and certification, yielding a :class:`RepositorySubject` ready for
    downstream Validation, Certification, and Acceptance.
    """

    __slots__ = ("_pipeline", "_default_owner")

    def __init__(self, pipeline: Any, *, default_owner: str = DEFAULT_REPOSITORY_OWNER) -> None:
        self._pipeline = pipeline
        self._default_owner = default_owner

    def assimilate(self, snapshot: RepositorySnapshot) -> RepositorySubject:
        """Assimilate ``snapshot`` into a canonical :class:`RepositorySubject`."""
        discovery = discover_repository(snapshot)
        frontier = discover_frontier(snapshot)
        drift = discover_drift(snapshot)

        realized = snapshot.realized_units()
        unit_records = tuple(self._assimilate_unit(snapshot, unit) for unit in realized)

        subject_base = self._subject_base(snapshot, realized)
        validation = validate_base(subject_base)
        certification = certify_base(subject_base)
        subject_object = subject_base.require_object(snapshot.repository_id).to_dict()

        assimilation = RepositoryAssimilationEvidence(
            subject_id=snapshot.repository_id,
            units=unit_records,
            validation=validation.to_dict(),
            certification=certification.to_dict(),
            validated=validation.accepted,
            certified=certification.certified,
        )

        return RepositorySubject(
            repository_id=snapshot.repository_id,
            name=snapshot.name,
            root=snapshot.root,
            universe=snapshot.universe,
            head=snapshot.head,
            branch=snapshot.branch,
            discovery=discovery,
            frontier=frontier,
            drift=drift,
            assimilation=assimilation,
            subject_object=subject_object,
        )

    def _unit_statement(self, snapshot: RepositorySnapshot, unit: RepositoryUnit) -> str:
        return (
            f"Assimilated repository unit at path '{unit.path}' in repository "
            f"'{snapshot.name}' with {unit.source_files} source file(s)."
        )

    def _assimilate_unit(
        self, snapshot: RepositorySnapshot, unit: RepositoryUnit
    ) -> UnitAssimilation:
        intent = ArtifactIntent(
            intent_id=unit.unit_id,
            kind=KnowledgeKind.REFERENCE,
            title=f"Repository unit {unit.path}",
            statement=self._unit_statement(snapshot, unit),
            universe=snapshot.universe,
            authority=KnowledgeAuthority.ENGINEERING,
            owner=unit.owner or self._default_owner,
            operation=Operation.CREATE,
            rationale="Discovered as a realized source unit during EPIC-UKDA-004 assimilation.",
            tags=("repository", "unit", *unit.languages),
        )
        decision = self._pipeline.execute(intent)
        return UnitAssimilation(
            unit_id=unit.unit_id,
            path=unit.path,
            intent_id=intent.intent_id,
            outcome=decision.outcome.value,
            disposition=decision.disposition.value,
            accepted=decision.accepted,
            reasons=tuple(decision.reasons),
            decision=decision.to_dict(),
        )

    def _subject_base(
        self, snapshot: RepositorySnapshot, realized: Sequence[RepositoryUnit]
    ) -> KnowledgeBase:
        unit_objects = [
            CanonicalKnowledgeObject.create(
                cko_id=unit.unit_id,
                kind=KnowledgeKind.REFERENCE,
                title=f"Repository unit {unit.path}",
                statement=self._unit_statement(snapshot, unit),
                rationale="Realized repository unit assimilated under EPIC-UKDA-004.",
                universe=snapshot.universe,
                authority=KnowledgeAuthority.ENGINEERING,
                owner=unit.owner or self._default_owner,
                lifecycle=Lifecycle.OPERATIONAL,
                version=_VERSION,
                tags=("repository", "unit"),
            )
            for unit in realized
        ]
        unit_ids = tuple(sorted(obj.cko_id for obj in unit_objects))
        head = snapshot.head or "unversioned"
        branch = snapshot.branch or "detached"
        repository = CanonicalKnowledgeObject.create(
            cko_id=snapshot.repository_id,
            kind=KnowledgeKind.REFERENCE,
            title=f"Repository {snapshot.name}",
            statement=(
                f"Canonical assimilated subject for live repository '{snapshot.name}' at HEAD "
                f"{head} on branch '{branch}' with {len(unit_ids)} realized unit(s)."
            ),
            rationale=(
                "Produced by the Constitutional Pipeline repository assimilation (EPIC-UKDA-004)."
            ),
            universe=snapshot.universe,
            authority=KnowledgeAuthority.ENGINEERING,
            owner=self._default_owner,
            lifecycle=Lifecycle.OPERATIONAL,
            version=_VERSION,
            dependencies=unit_ids,
            knowledge_links=unit_ids,
            tags=("repository", "subject"),
        )
        return KnowledgeBase([repository, *unit_objects])


# --------------------------------------------------------------------------- emission


def _write_json(path: Path, document: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def emit_evidence(subject: RepositorySubject, directory: str | Path) -> dict[str, str]:
    """Write the four deterministic report artifacts and return ``{filename: path}``."""
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for filename, document in sorted(subject.reports().items()):
        written[filename] = str(_write_json(target / filename, document))
    return written


__all__ = [
    "SOURCE_EXTENSIONS",
    "DEFAULT_IGNORES",
    "DEFAULT_REPOSITORY_OWNER",
    "SCHEMA_DISCOVERY",
    "SCHEMA_FRONTIER",
    "SCHEMA_DRIFT",
    "SCHEMA_ASSIMILATION",
    "CommitRef",
    "OwnershipSignal",
    "DependencySignal",
    "RepositoryUnit",
    "RepositoryCheckpoint",
    "Workstream",
    "FrontierItem",
    "DriftItem",
    "RepositorySnapshot",
    "RepositoryDiscoveryReport",
    "RepositoryFrontierReport",
    "RepositoryDriftReport",
    "UnitAssimilation",
    "RepositoryAssimilationEvidence",
    "RepositorySubject",
    "GitRunner",
    "RepositoryProbe",
    "RepositoryAssimilator",
    "discover_repository",
    "discover_frontier",
    "discover_drift",
    "discover_checkpoints",
    "discover_workstreams",
    "emit_evidence",
]
