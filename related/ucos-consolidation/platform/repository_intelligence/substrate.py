"""UCOS-EPIC-014 — Repository substrate reader (Terminal T5).

The **continuous repository search** primitive: one read-only pass over the repository
that produces every fact the eight discovery dimensions reason over. Discovery itself is
then a set of *pure functions* of this substrate, which is what makes the whole subsystem
deterministic and re-runnable on every change.

What is read (and nothing else is trusted):

    * ``git ls-files`` — the version-control eligibility boundary that the repository's
      own doctrine uses to define its corpus, with a deterministic filesystem walk as a
      fallback so the reader stays usable in a non-git export.
    * the Python AST of every tracked module under the declared code roots — imports,
      top-level symbols, the docstring's first line, LOC and a content digest.
    * ``pyproject.toml`` — the *declaration* substrate: published console scripts,
      packaged roots, and the pytest/coverage registration lists. Conflict discovery
      exists precisely because code and declarations can disagree.
    * the UCOS-RIE-001 capability catalog — **composed, never recomputed**.

Reuse boundary (this subsystem's own prime directive applied to itself): capability
identity/category/authority/reuse policy is already owned by UCOS-RIE-001
(``intelligence/rie/discovery.py``). This reader therefore *consumes* that catalog — by
lazy import of the live producer when importable, else by reading its emitted, sealed
artifact — and adds only the facts RIE does not carry. It never re-derives the catalog.
The ``intelligence`` root is not a packaged distribution root, hence the lazy import with
an artifact fallback rather than a hard dependency.

The reader **never writes**. It holds no wall-clock: ``digest()`` is a pure function of
repository content, so an unchanged repository yields an unchanged digest even across
commits, while any content change moves it.
"""

from __future__ import annotations

import ast
import hashlib
import json
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.repository_intelligence.config import RepositoryIntelligenceConfig
from platform.repository_intelligence.errors import SubstrateError
from typing import Any

#: How the capability catalog was obtained (recorded so evidence states its provenance).
CATALOG_SOURCE_PACKAGE = "intelligence.rie.discovery (live producer)"
CATALOG_SOURCE_ARTIFACT = "intelligence/UCOS-RIE-CAPABILITY-CATALOG.json (sealed artifact)"
CATALOG_SOURCE_ABSENT = "absent"

#: The keys a composed capability record must carry to be usable.
_CATALOG_KEYS = (
    "canonical_name",
    "canonical_location",
    "category",
    "authority",
    "reuse",
    "replacement_prohibited",
    "implementation_status",
)


# ---------------------------------------------------------------------------
# module facts
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class ModuleFact:
    """Everything the discovery dimensions need to know about one tracked module."""

    module: str
    capability: str
    root: str
    path: str
    loc: int
    content_sha256: str
    imports: tuple[str, ...] = ()
    import_time_imports: tuple[str, ...] = ()
    symbols: tuple[str, ...] = ()
    docline: str = ""
    is_test: bool = False
    parsed: bool = True

    @property
    def basename(self) -> str:
        """The module's terminal name (``contracts`` for ``platform.x.contracts``)."""
        return self.module.rsplit(".", 1)[-1]

    @property
    def deferred_imports(self) -> tuple[str, ...]:
        """Targets this module names but never resolves while it is being imported.

        Two constructs land here, and Python treats both as the *cure* for a circular
        import rather than a symptom of one:

          * ``if TYPE_CHECKING:`` — erased before the interpreter resolves anything;
          * an import inside a function or class body — resolved on first call, by which
            time every module in the loop is fully initialised.

        Neither can deadlock module initialisation, so neither can close an import cycle.
        """
        at_import = set(self.import_time_imports)
        return tuple(i for i in self.imports if i not in at_import)

    def core(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "capability": self.capability,
            "root": self.root,
            "path": self.path,
            "loc": self.loc,
            "content_sha256": self.content_sha256,
            "imports": list(self.imports),
            "import_time_imports": list(self.import_time_imports),
            "symbols": list(self.symbols),
            "is_test": self.is_test,
            "parsed": self.parsed,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "docline": self.docline}


@dataclass(frozen=True, slots=True)
class Declarations:
    """The repository's *declared* state, read from ``pyproject.toml``.

    Kept separate from the code facts because the whole point of conflict discovery is to
    compare the two. ``available`` is False when there is no readable pyproject, in which
    case declaration-dependent checks fail closed rather than pass vacuously.
    """

    available: bool = False
    console_scripts: Mapping[str, str] = field(default_factory=dict)
    packaged_includes: tuple[str, ...] = ()
    coverage_sources: tuple[str, ...] = ()
    pytest_cov_packages: tuple[str, ...] = ()
    runtime_dependencies: tuple[str, ...] = ()
    dev_dependencies: tuple[str, ...] = ()
    coverage_fail_under: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "console_scripts": dict(sorted(self.console_scripts.items())),
            "packaged_includes": list(self.packaged_includes),
            "coverage_sources": list(self.coverage_sources),
            "pytest_cov_packages": list(self.pytest_cov_packages),
            "runtime_dependencies": list(self.runtime_dependencies),
            "dev_dependencies": list(self.dev_dependencies),
            "coverage_fail_under": self.coverage_fail_under,
        }


# ---------------------------------------------------------------------------
# the substrate
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class RepositorySubstrate:
    """The immutable, single-pass, read-only projection of the repository."""

    config: RepositoryIntelligenceConfig
    modules: tuple[ModuleFact, ...]
    zones: Mapping[str, int]
    declarations: Declarations
    catalog: tuple[Mapping[str, Any], ...]
    catalog_source: str
    provenance: Mapping[str, str] = field(default_factory=dict)

    # -- construction ----------------------------------------------------
    @classmethod
    def scan(cls, config: RepositoryIntelligenceConfig | None = None) -> RepositorySubstrate:
        """Perform the one read-only pass and return the immutable substrate.

        Raises:
            SubstrateError: if no declared code root exists (fail-closed — vacuous
                intelligence over an empty substrate is worse than an explicit failure).
        """
        cfg = config or RepositoryIntelligenceConfig.create()
        cfg.require_substrate()
        tracked = _tracked_files(cfg)
        modules = tuple(
            sorted(
                (m for m in (_module_fact(cfg, rel) for rel in tracked if _is_code(cfg, rel)) if m),
                key=lambda m: m.module,
            )
        )
        catalog, catalog_source = _capability_catalog(cfg)
        return cls(
            config=cfg,
            modules=modules,
            zones=_zone_census(tracked),
            declarations=_declarations(cfg),
            catalog=catalog,
            catalog_source=catalog_source,
            provenance=_provenance(cfg, len(tracked)),
        )

    # -- projections -----------------------------------------------------
    def source_modules(self) -> tuple[ModuleFact, ...]:
        """Non-test modules (the implementation surface)."""
        return tuple(m for m in self.modules if not m.is_test)

    def test_modules(self) -> tuple[ModuleFact, ...]:
        return tuple(m for m in self.modules if m.is_test)

    def module_index(self) -> dict[str, ModuleFact]:
        return {m.module: m for m in self.modules}

    def capabilities_on_disk(self) -> tuple[str, ...]:
        """Distinct capability names present in the code substrate, canonically ordered."""
        return tuple(sorted({m.capability for m in self.source_modules()}))

    def location_is_populated(self, location: str) -> bool:
        """Whether any tracked module lives at or beneath a repository-relative location.

        This answers "is the thing the catalog claims actually here", which is a different
        question from "does the substrate model it as a capability". A catalog entry may
        name a real package at a granularity the capability model does not carry — a
        nested sub-package, a test package, a bare code root — and that is a divergence in
        naming, not a claim about something absent.

        Measured over the tracked module facts rather than the filesystem, so the answer
        stays a function of the substrate and cannot be changed by an untracked file.
        """
        cleaned = location.strip().strip("/")
        if not cleaned:
            return False
        prefix = f"{cleaned}/"
        return any(m.path == cleaned or m.path.startswith(prefix) for m in self.modules)

    def modules_of(self, capability: str) -> tuple[ModuleFact, ...]:
        return tuple(m for m in self.source_modules() if m.capability == capability)

    def symbols_of(self, capability: str) -> tuple[str, ...]:
        return tuple(sorted({s for m in self.modules_of(capability) for s in m.symbols}))

    def loc_of(self, capability: str) -> int:
        return sum(m.loc for m in self.modules_of(capability))

    def capability_of_module(self, module: str) -> str | None:
        """The capability that owns ``module``, matching the longest known prefix.

        Resolves an imported *module* path (``platform.foundation.contracts``) to the
        capability that provides it (``platform.foundation``) without assuming a fixed
        depth, so nested sub-packages attribute to their owning capability.
        """
        known = set(self.capabilities_on_disk())
        parts = module.split(".")
        for cut in range(len(parts), 0, -1):
            candidate = ".".join(parts[:cut])
            if candidate in known:
                return candidate
        return None

    def catalog_index(self) -> dict[str, Mapping[str, Any]]:
        """The composed RIE catalog keyed by canonical capability name."""
        return {str(entry["canonical_name"]): entry for entry in self.catalog}

    def catalog_available(self) -> bool:
        return self.catalog_source != CATALOG_SOURCE_ABSENT

    # -- identity --------------------------------------------------------
    def core(self) -> dict[str, Any]:
        """The hashable core: repository content only, no wall-clock, no absolute path."""
        return {
            "config": self.config.to_dict(),
            "modules": [m.core() for m in self.modules],
            "zones": dict(sorted(self.zones.items())),
            "declarations": self.declarations.to_dict(),
            "catalog": [{key: entry.get(key) for key in _CATALOG_KEYS} for entry in self.catalog],
        }

    def digest(self) -> str:
        """The deterministic content digest of the substrate.

        Git HEAD is deliberately *excluded*: the digest identifies repository **content**,
        so an unrelated commit does not perturb intelligence identity while any change to
        code or declarations does. HEAD is retained in :attr:`provenance` for audit.
        """
        return content_hash(self.core())

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository_id": self.config.repository_id,
            "substrate_digest": self.digest(),
            "catalog_source": self.catalog_source,
            "counts": {
                "tracked_zones": len(self.zones),
                "modules": len(self.modules),
                "source_modules": len(self.source_modules()),
                "test_modules": len(self.test_modules()),
                "capabilities_on_disk": len(self.capabilities_on_disk()),
                "catalog_entries": len(self.catalog),
                "console_scripts": len(self.declarations.console_scripts),
            },
            "zones": dict(sorted(self.zones.items())),
            "declarations": self.declarations.to_dict(),
            "provenance": dict(sorted(self.provenance.items())),
        }


# ---------------------------------------------------------------------------
# readers
# ---------------------------------------------------------------------------
def _provider(cfg: RepositoryIntelligenceConfig):
    """The declared discovery provider for this repository root.

    THE TWO WRAPPERS THIS REPLACED RAN ARBITRARY ARGV. `_git` and `_git_raw` took `*args` and
    returned "" on any failure, so every question this module asked went to the tool directly and
    every failure looked identical to an empty answer. The three questions it actually asks —
    the tracked-and-untracked population, the abbreviated revision, the branch — are each a
    declared capability now, and a failure raises where the caller decides what to do with it.
    """
    from engine.omega_infinite.git_provider import GitDiscoveryProvider

    return GitDiscoveryProvider(root=str(cfg.repository_root))


def _tracked_files(cfg: RepositoryIntelligenceConfig) -> tuple[str, ...]:
    """Repository-relative paths inside the version-control eligibility boundary.

    Uses ``git ls-files -z --cached --others --exclude-standard`` so the substrate covers
    everything git *would* track — committed files plus new, non-ignored ones — which is
    what makes intelligence useful on work in progress rather than only on history. The
    ``-z`` form is required because git otherwise C-quotes paths containing non-ASCII
    bytes, which would corrupt zone identities. A deterministic filesystem walk is the
    fallback for a non-git export.
    """
    # TRACKED plus UNTRACKED, which is two capabilities and not a wider filter on one: this
    # module reports on the working copy as an operator sees it, so debris counts here where it
    # must not count in a governance verdict.
    # THE EMPTY ANSWER TRIGGERS THE WALK BELOW; IT IS NOT THE ANSWER. The docstring says a
    # filesystem walk is the fallback for a non-git export, and the wrappers this replaced returned
    # "" on failure precisely so that branch would run. A first version returned an empty tuple
    # here and skipped the fallback, which turned "not a working copy" into "an empty repository"
    # for 58 tests — the vacuity this substrate is supposed to avoid, introduced while removing a
    # direct call.
    #
    # A REPORTING MODULE AND A GOVERNING MODULE WANT DIFFERENT ANSWERS TO THE SAME FAILURE. This
    # one reports on a working copy, so it degrades to walking it. mutation_classification governs
    # authority, so an empty tracked set there silently assigned every subject the wrong one and
    # raising was the fix. Neither should inherit the other's failure mode.
    from engine.omega_infinite.capability import WORKING_TREE_STATE
    from engine.omega_infinite.provider import ProviderError

    provider = _provider(cfg)
    try:
        tracked = [a.location.locator for a in provider.enumerate()]
        untracked = list(provider.supply(WORKING_TREE_STATE)["untracked"])
    except ProviderError:
        tracked, untracked = [], []
    listing = "\0".join([*tracked, *untracked])
    if listing:
        paths = [line for line in listing.split("\0") if line]
    else:
        paths = [
            cfg.rel(p)
            for p in sorted(cfg.repository_root.rglob("*"))
            if p.is_file() and not cfg.is_ignored(p.relative_to(cfg.repository_root))
        ]
    return tuple(sorted(p for p in paths if not cfg.is_ignored(Path(p))))


def _is_code(cfg: RepositoryIntelligenceConfig, rel: str) -> bool:
    parts = Path(rel).parts
    return bool(parts) and parts[0] in cfg.code_roots and rel.endswith(".py")


def _module_fact(cfg: RepositoryIntelligenceConfig, rel: str) -> ModuleFact | None:
    """Build a :class:`ModuleFact` for a tracked module, or None if unreadable."""
    path = cfg.repository_root / rel
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    parts = Path(rel).with_suffix("").parts
    module_parts = list(parts[:-1]) if parts[-1] == "__init__" else list(parts)
    module = ".".join(module_parts)
    root = parts[0]
    package = ".".join(parts[:-1]) if parts[-1] != "__init__" else ".".join(parts[:-1])
    loc = len(source.splitlines())
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    try:
        tree: ast.Module | None = ast.parse(source)
    except (SyntaxError, ValueError):
        tree = None
    imports, import_time_imports = _imports(tree, package) if tree else ((), ())
    symbols = _symbols(tree) if tree else ()
    docline = _docline(tree) if tree else ""
    return ModuleFact(
        module=module or root,
        capability=_capability_name(cfg, parts),
        root=root,
        path=rel,
        loc=loc,
        content_sha256=digest,
        imports=imports,
        import_time_imports=import_time_imports,
        symbols=symbols,
        docline=docline,
        is_test=cfg.test_dir_name in parts,
        parsed=tree is not None,
    )


def _capability_name(cfg: RepositoryIntelligenceConfig, parts: tuple[str, ...]) -> str:
    """The capability a module belongs to: ``<root>.<subpackage>``, else the root itself.

    A module sitting directly in a code root (``platform/__init__.py``) attributes to the
    root; anything deeper attributes to its first sub-package, which is the unit the RIE
    catalog also treats as a capability. Test modules attribute to the test package so
    they never inflate the implementation surface.
    """
    root = parts[0]
    if len(parts) < 2 or parts[1] == "__init__":
        return root
    if parts[1] == cfg.test_dir_name:
        return f"{root}.{cfg.test_dir_name}"
    return f"{root}.{parts[1]}"


def _imports(tree: ast.Module, package: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Absolute dotted import targets, relative resolved: ``(every target, at import)``.

    The second element is the subset the interpreter actually resolves while this module
    is being imported — module-level statements that are not ``TYPE_CHECKING``-guarded.
    That is the only set an import cycle can be built from; see
    :attr:`ModuleFact.deferred_imports` for what is excluded and why.

    A target reached both ways is at-import: one unguarded module-level statement is
    enough to make the dependency load-bearing, and deferring it elsewhere does not undo
    that.
    """
    at_import: set[str] = set()
    every: set[str] = set()

    def visit(node: ast.AST, *, deferred: bool) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Import | ast.ImportFrom):
                targets = (
                    {alias.name for alias in child.names}
                    if isinstance(child, ast.Import)
                    else ({t} if (t := _resolve_import_from(child, package)) else set())
                )
                every.update(targets)
                if not deferred:
                    at_import.update(targets)
                continue
            if isinstance(child, ast.If) and _is_type_checking_test(child.test):
                # Body only. The `else:` arm of a TYPE_CHECKING block is precisely the
                # branch that DOES run at import, so deferring it would erase a real
                # dependency — the same error in the opposite direction.
                for statement in child.body:
                    visit_statement(statement, deferred=True)
                for statement in child.orelse:
                    visit_statement(statement, deferred=deferred)
                continue
            visit(
                child,
                deferred=deferred
                or isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda),
            )

    def visit_statement(node: ast.AST, *, deferred: bool) -> None:
        """Apply the import test to a statement itself, then descend into it."""
        if isinstance(node, ast.Import | ast.ImportFrom):
            targets = (
                {alias.name for alias in node.names}
                if isinstance(node, ast.Import)
                else ({t} if (t := _resolve_import_from(node, package)) else set())
            )
            every.update(targets)
            if not deferred:
                at_import.update(targets)
            return
        visit(node, deferred=deferred)

    visit(tree, deferred=False)
    # Set membership, not visit order: a target may be imported at module level in one
    # place and deferred in another, and the verdict must not depend on which the walk
    # reached first.
    return tuple(sorted(every)), tuple(sorted(at_import))


def _is_type_checking_test(test: ast.expr) -> bool:
    """Whether an ``if`` test is the ``TYPE_CHECKING`` sentinel.

    Matches both spellings the repository uses — the bare ``TYPE_CHECKING`` name and the
    qualified ``typing.TYPE_CHECKING`` attribute.
    """
    if isinstance(test, ast.Name):
        return test.id == "TYPE_CHECKING"
    if isinstance(test, ast.Attribute):
        return test.attr == "TYPE_CHECKING"
    return False


def _resolve_import_from(node: ast.ImportFrom, package: str) -> str:
    """Resolve ``from . import x`` / ``from .y import z`` against the owning package."""
    if not node.level:
        return node.module or ""
    base_parts = package.split(".") if package else []
    trim = node.level - 1
    if trim:
        base_parts = base_parts[:-trim] if trim <= len(base_parts) else []
    if node.module:
        base_parts = [*base_parts, *node.module.split(".")]
    return ".".join(part for part in base_parts if part)


def _symbols(tree: ast.Module) -> tuple[str, ...]:
    """Top-level public function/class names (the module's declared surface)."""
    names = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
        and not node.name.startswith("_")
    }
    return tuple(sorted(names))


def _docline(tree: ast.Module) -> str:
    doc = ast.get_docstring(tree) or ""
    stripped = doc.strip()
    return stripped.splitlines()[0][:200] if stripped else ""


def _zone_census(tracked: tuple[str, ...]) -> dict[str, int]:
    """Tracked-file counts per top-level repository zone (deterministic)."""
    census: dict[str, int] = {}
    for rel in tracked:
        parts = Path(rel).parts
        zone = parts[0] if len(parts) > 1 else "."
        census[zone] = census.get(zone, 0) + 1
    return dict(sorted(census.items()))


def _declarations(cfg: RepositoryIntelligenceConfig) -> Declarations:
    """Read the declared state from ``pyproject.toml`` (fail-closed when unreadable)."""
    path = cfg.pyproject_path
    if not path.is_file():
        return Declarations()
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError, UnicodeDecodeError):
        return Declarations()
    project = raw.get("project", {}) if isinstance(raw.get("project"), Mapping) else {}
    tool = raw.get("tool", {}) if isinstance(raw.get("tool"), Mapping) else {}
    setuptools_cfg = (
        tool.get("setuptools", {}) if isinstance(tool.get("setuptools"), Mapping) else {}
    )
    find_cfg = (
        setuptools_cfg.get("packages", {}).get("find", {})
        if isinstance(setuptools_cfg.get("packages"), Mapping)
        else {}
    )
    coverage_cfg = tool.get("coverage", {}) if isinstance(tool.get("coverage"), Mapping) else {}
    pytest_cfg = tool.get("pytest", {}) if isinstance(tool.get("pytest"), Mapping) else {}
    ini = (
        pytest_cfg.get("ini_options", {})
        if isinstance(pytest_cfg.get("ini_options"), Mapping)
        else {}
    )
    addopts = ini.get("addopts", []) if isinstance(ini.get("addopts"), list) else []
    optional = project.get("optional-dependencies", {})
    dev = optional.get("dev", []) if isinstance(optional, Mapping) else []
    report_cfg = (
        coverage_cfg.get("report", {}) if isinstance(coverage_cfg.get("report"), Mapping) else {}
    )
    run_cfg = coverage_cfg.get("run", {}) if isinstance(coverage_cfg.get("run"), Mapping) else {}
    fail_under = report_cfg.get("fail_under")
    return Declarations(
        available=True,
        console_scripts={
            str(name): str(target)
            for name, target in dict(project.get("scripts", {}) or {}).items()
        },
        packaged_includes=tuple(str(i) for i in (find_cfg.get("include") or [])),
        coverage_sources=tuple(str(s) for s in (run_cfg.get("source") or [])),
        pytest_cov_packages=tuple(
            sorted(
                str(opt).split("=", 1)[1]
                for opt in addopts
                if isinstance(opt, str) and opt.startswith("--cov=")
            )
        ),
        runtime_dependencies=tuple(str(d) for d in (project.get("dependencies") or [])),
        dev_dependencies=tuple(str(d) for d in dev),
        coverage_fail_under=float(fail_under) if isinstance(fail_under, int | float) else None,
    )


def _capability_catalog(
    cfg: RepositoryIntelligenceConfig,
) -> tuple[tuple[Mapping[str, Any], ...], str]:
    """Compose the UCOS-RIE-001 capability catalog: live producer first, artifact second.

    Never re-derives the catalog. Returns an empty catalog with
    :data:`CATALOG_SOURCE_ABSENT` when neither is available, which the capability and
    conflict dimensions then report as a fail-closed finding.
    """
    live = _catalog_from_producer(cfg)
    if live:
        return live, CATALOG_SOURCE_PACKAGE
    artifact = _catalog_from_artifact(cfg)
    if artifact:
        return artifact, CATALOG_SOURCE_ARTIFACT
    return (), CATALOG_SOURCE_ABSENT


def _catalog_from_producer(
    cfg: RepositoryIntelligenceConfig,
) -> tuple[Mapping[str, Any], ...]:
    """Invoke the live UCOS-RIE-001 producer if the ``intelligence`` root is importable."""
    try:  # pragma: no cover - exercised only where the intelligence root is importable
        from intelligence.rie.config import RepoConfig
        from intelligence.rie.discovery import discover
        from intelligence.rie.evidence import EvidenceReader
    except ImportError:
        return ()
    try:  # pragma: no cover - defensive: a producer fault must not abort intelligence
        reader = EvidenceReader(RepoConfig.create(cfg.repository_root))
        return tuple(_normalize_catalog_entry(c.as_dict()) for c in discover(reader))
    except Exception:  # noqa: BLE001 - fall back to the sealed artifact
        return ()


def _catalog_from_artifact(
    cfg: RepositoryIntelligenceConfig,
) -> tuple[Mapping[str, Any], ...]:
    """Read the sealed, emitted capability catalog artifact."""
    path = cfg.capability_catalog_path
    if not path.is_file():
        return ()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return ()
    entries = payload.get("capabilities") if isinstance(payload, Mapping) else None
    if not isinstance(entries, list):
        return ()
    return tuple(
        _normalize_catalog_entry(e)
        for e in entries
        if isinstance(e, Mapping) and e.get("canonical_name")
    )


def _normalize_catalog_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Project a catalog entry onto the keys this subsystem consumes.

    Raises:
        SubstrateError: if the composed catalog entry lacks its canonical identity — a
            malformed upstream producer must fail loudly, not be silently patched.
    """
    if not entry.get("canonical_name"):
        raise SubstrateError("composed capability catalog entry has no canonical_name")
    return {
        "unique_id": str(entry.get("unique_id", "")),
        "canonical_name": str(entry["canonical_name"]),
        "canonical_location": str(entry.get("canonical_location", "")),
        "category": str(entry.get("category", "")),
        "authority": str(entry.get("authority", "")),
        "reuse": str(entry.get("reuse", "")),
        "replacement_prohibited": bool(entry.get("replacement_prohibited", False)),
        "implementation_status": str(entry.get("implementation_status", "")),
        "description": str(entry.get("description", "")),
        "evidence_present": bool(entry.get("evidence_present", False)),
    }


def _provenance(cfg: RepositoryIntelligenceConfig, tracked_count: int) -> dict[str, str]:
    """Audit-only provenance (never part of the substrate digest)."""
    from engine.omega_infinite.capability import REVISION_IDENTITY
    from engine.omega_infinite.provider import ProviderError

    try:
        position = _provider(cfg).supply(REVISION_IDENTITY)
    except ProviderError:
        position = {}
    head = str(position.get("short") or "")
    return {
        "head": head or "UNKNOWN",
        "branch": str(position.get("branch") or "") or "UNKNOWN",
        "tracked_files": str(tracked_count),
        "file_listing_source": "git ls-files" if head else "filesystem",
    }


__all__ = [
    "CATALOG_SOURCE_PACKAGE",
    "CATALOG_SOURCE_ARTIFACT",
    "CATALOG_SOURCE_ABSENT",
    "ModuleFact",
    "Declarations",
    "RepositorySubstrate",
]
