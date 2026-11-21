"""ZG-P-02 — Repository evidence source (Universe→Code Coverage Instrument).

Reconstructs the coverage evidence bundle **entirely from authoritative repository
artifacts** — no hardcoded universe map, no manual coverage table, no synthetic edge:

    * Universe → Phase   — parsed from the committed Universe Catalog registry rows
      (``02-MASTER/…UNIVERSAL-UNIVERSE-CATALOG.md``; the ``Phase`` column = IMP-00x).
    * Phase → Program    — the IMP artifact name (from the committed IMP Program Tracker
      ``### IMP-00N — <Name>`` headers) matched by name-token overlap to a
      ``06-IMPLEMENTATION/`` program document.
    * Program → Implementation — the program document matched by name-token overlap to a
      realizing code package under ``platform/*`` or ``engine/*``.
    * Implementation → Epic — the ``*-COMPLETION-REPORT.md`` in the package (its epic id).
    * Epic → Module      — each ``*.py`` module in the package.
    * Module → Code Asset — each top-level ``def``/``class`` symbol (via :mod:`ast`).
    * Code Asset → Runtime Asset — the package runtime-evidence node, present iff a
      completion report **and** ≥1 test module for the package both exist.

Every extraction is a pure, deterministic function of file contents (no wall-clock, no
mtime). Where a link cannot be evidenced, **no edge is emitted** — the upstream node is
reported as a coverage gap (fail-closed), never bridged by a fabricated edge.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from platform.coverage.contracts import CoverageEdge, CoverageNode, CoverageNodeKind
from platform.coverage.errors import CoverageEvidenceError
from platform.coverage.evidence import EvidenceBundle, EvidenceSource

#: Repository markers used to locate the repository root deterministically.
_ROOT_MARKERS = ("02-MASTER", "platform")

#: Filename of the committed Universe Catalog (ARCH-001 analog).
_UNIVERSE_CATALOG = "02-MASTER/UCOS-Ω∞-UNIVERSAL-UNIVERSE-CATALOG.md"

#: Filename of the committed IMP Program Tracker (IMP-00N → name).
_IMP_TRACKER = "02-MASTER/UCOS-Ω∞-IMPLEMENTATION-PROGRAM-TRACKER.md"

#: The implementation-program document band.
_IMPL_DIR = "06-IMPLEMENTATION"

#: Code-package roots (EC-2 platform, EC-1 engine).
_CODE_ROOTS = ("platform", "engine")

#: Tokens dropped from name matching (too generic to discriminate a program/package).
_STOPWORDS = frozenset(
    {
        "ucos",
        "universal",
        "the",
        "of",
        "and",
        "a",
        "an",
        "for",
        "platform",
        "architecture",
        "engine",
        "program",
        "realization",
        "management",
    }
)

_UNI_ROW = re.compile(r"^\|\s*(UNI-\d+)\s*\|")
_IMP_PHASE = re.compile(r"(IMP-\d+)")
_IMP_HEADER = re.compile(r"^#{1,6}\s*(IMP-\d+)\s*[—:-]\s*(.+?)\s*$")
_COMPLETION_RE = re.compile(r"([A-Z0-9]+(?:-[A-Z0-9]+)*)-COMPLETION-REPORT\.md$")


def _slug_tokens(text: str) -> frozenset[str]:
    """Lowercase alphanumeric tokens minus stopwords (deterministic name signature)."""
    raw = re.split(r"[^a-z0-9]+", text.lower())
    return frozenset(t for t in raw if t and t not in _STOPWORDS)


def parse_universe_rows(markdown: str) -> tuple[tuple[str, str], ...]:
    """Extract ``(UNI-###, IMP-###)`` pairs from Universe Catalog registry rows.

    Reads the pipe-delimited registry tables; the 8th column is the implementation
    ``Phase``. Rows without a resolvable ``IMP-###`` phase are skipped (fail-closed:
    no phase ⇒ no universe→phase edge).
    """
    pairs: list[tuple[str, str]] = []
    for line in markdown.splitlines():
        if not _UNI_ROW.match(line):
            continue
        cols = [c.strip() for c in line.split("|")]
        # cols[0]='' , cols[1]=ID, ... cols[8]=Phase, cols[9]=Description, cols[10]=''
        if len(cols) < 9:
            continue
        uni = cols[1]
        phase_match = _IMP_PHASE.search(cols[8])
        if phase_match is None:
            continue
        pairs.append((uni, phase_match.group(1)))
    return tuple(pairs)


def parse_imp_names(markdown: str) -> dict[str, str]:
    """Extract ``{IMP-###: name}`` from IMP Program Tracker artifact headers."""
    names: dict[str, str] = {}
    for line in markdown.splitlines():
        m = _IMP_HEADER.match(line.strip())
        if m is None:
            continue
        names.setdefault(m.group(1), m.group(2).strip())
    return names


def top_level_symbols(source: str) -> tuple[str, ...]:
    """Return the top-level ``def``/``class`` symbol names of a module (deterministic)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ()
    symbols = [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
        and not node.name.startswith("_")
    ]
    return tuple(sorted(set(symbols)))


def best_match(tokens: frozenset[str], candidates: dict[str, frozenset[str]]) -> str | None:
    """Return the candidate key with the greatest token overlap (>0), tie-broken by key."""
    best: str | None = None
    best_score = 0
    for key in sorted(candidates):
        score = len(tokens & candidates[key])
        if score > best_score:
            best_score = score
            best = key
    return best


def discover_repo_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` (or this file) until a directory has all root markers."""
    here = (start or Path(__file__)).resolve()
    for candidate in (here, *here.parents):
        if candidate.is_dir() and all((candidate / m).exists() for m in _ROOT_MARKERS):
            return candidate
    raise CoverageEvidenceError("could not locate the repository root from evidence markers")


class RepositoryEvidenceSource(EvidenceSource):
    """A deterministic, fail-closed evidence source over the real repository."""

    __slots__ = ("_root",)

    def __init__(self, repo_root: Path | str | None = None) -> None:
        self._root = discover_repo_root(Path(repo_root)) if repo_root else discover_repo_root()

    @property
    def root(self) -> Path:
        return self._root

    def _read(self, rel: str) -> str:
        path = self._root / rel
        if not path.is_file():
            raise CoverageEvidenceError("required evidence artifact is absent", artifact=rel)
        return path.read_text(encoding="utf-8")

    def collect(self) -> EvidenceBundle:  # noqa: C901 - a single cohesive extraction pass
        nodes: list[CoverageNode] = []
        edges: list[CoverageEdge] = []

        def add_node(kind: CoverageNodeKind, ref: str, *, authority: str) -> None:
            nodes.append(CoverageNode.create(kind, ref, authority=authority))

        def add_edge(sk, sr, tk, tr, *, authority, evidence) -> None:  # noqa: ANN001
            edges.append(
                CoverageEdge.create(
                    source_kind=sk,
                    source_ref=sr,
                    target_kind=tk,
                    target_ref=tr,
                    authority=authority,
                    evidence=evidence,
                )
            )

        # 1. Universe → Phase (from the committed catalog).
        catalog = self._read(_UNIVERSE_CATALOG)
        phases: set[str] = set()
        for uni, phase in parse_universe_rows(catalog):
            add_node(CoverageNodeKind.UNIVERSE, uni, authority=_UNIVERSE_CATALOG)
            if phase not in phases:
                add_node(CoverageNodeKind.PHASE, phase, authority=_IMP_TRACKER)
                phases.add(phase)
            add_edge(
                CoverageNodeKind.UNIVERSE,
                uni,
                CoverageNodeKind.PHASE,
                phase,
                authority=_UNIVERSE_CATALOG,
                evidence=f"{uni} Phase={phase}",
            )

        # 2. Phase → Program (IMP name ↔ 06-IMPLEMENTATION document, by token overlap).
        imp_names = parse_imp_names(self._read(_IMP_TRACKER))
        impl_dir = self._root / _IMPL_DIR
        program_tokens: dict[str, frozenset[str]] = {}
        if impl_dir.is_dir():
            for doc in sorted(impl_dir.glob("*.md")):
                program_tokens[f"{_IMPL_DIR}/{doc.name}"] = _slug_tokens(doc.stem)
        program_of_phase: dict[str, str] = {}
        for phase in sorted(phases):
            name = imp_names.get(phase)
            if not name:
                continue
            program = best_match(_slug_tokens(name), program_tokens)
            if program is None:
                continue
            program_of_phase[phase] = program
            add_node(CoverageNodeKind.PROGRAM, program, authority=_IMP_TRACKER)
            add_edge(
                CoverageNodeKind.PHASE,
                phase,
                CoverageNodeKind.PROGRAM,
                program,
                authority=_IMP_TRACKER,
                evidence=f"{phase} '{name}' -> {program}",
            )

        # 3. Program → Implementation (code package, by token overlap), then the code chain.
        package_tokens: dict[str, frozenset[str]] = {}
        for code_root in _CODE_ROOTS:
            root_dir = self._root / code_root
            if not root_dir.is_dir():
                continue
            for pkg in sorted(root_dir.iterdir()):
                if not pkg.is_dir() or pkg.name.startswith(("_", ".")) or pkg.name == "tests":
                    continue
                package_tokens[f"{code_root}/{pkg.name}"] = _slug_tokens(pkg.name)

        linked_packages: set[str] = set()
        for program in sorted(set(program_of_phase.values())):
            prog_tokens = program_tokens.get(program, frozenset())
            package = best_match(prog_tokens, package_tokens)
            if package is None:
                continue
            add_node(CoverageNodeKind.IMPLEMENTATION, package, authority=program)
            add_edge(
                CoverageNodeKind.PROGRAM,
                program,
                CoverageNodeKind.IMPLEMENTATION,
                package,
                authority=program,
                evidence=f"{program} -> {package}",
            )
            linked_packages.add(package)

        # 4..7. Implementation → Epic → Module → Code Asset → Runtime Asset.
        for package in sorted(linked_packages):
            self._emit_code_chain(package, nodes, edges)

        try:
            return EvidenceBundle.create(nodes, edges)
        except CoverageEvidenceError:  # pragma: no cover - defensive fail-closed
            raise

    def _emit_code_chain(
        self, package: str, nodes: list[CoverageNode], edges: list[CoverageEdge]
    ) -> None:
        pkg_dir = self._root / package
        if not pkg_dir.is_dir():  # pragma: no cover - defensive; linked packages are dirs
            return
        # Epic: from the package completion report filename.
        epic: str | None = None
        completion_rel: str | None = None
        for report in sorted(pkg_dir.glob("*-COMPLETION-REPORT.md")):
            m = _COMPLETION_RE.search(report.name)
            if m is not None:
                epic = m.group(1)
                completion_rel = f"{package}/{report.name}"
                break
        if epic is None or completion_rel is None:
            return  # no epic evidence ⇒ implementation is an (honest) gap

        nodes.append(CoverageNode.create(CoverageNodeKind.EPIC, epic, authority=completion_rel))
        edges.append(
            CoverageEdge.create(
                source_kind=CoverageNodeKind.IMPLEMENTATION,
                source_ref=package,
                target_kind=CoverageNodeKind.EPIC,
                target_ref=epic,
                authority=completion_rel,
                evidence=f"{package} completion report {epic}",
            )
        )

        # Runtime evidence: package has a completion report AND ≥1 test module.
        # Test suites live under platform/tests (EC-2) and engine/tests (EC-1); a test
        # module is evidence for a package when its filename references the package slug.
        pkg_slug = package.split("/")[-1]
        test_hits: list[Path] = []
        for tests_rel in ("platform/tests", "engine/tests"):
            tests_dir = self._root / tests_rel
            if tests_dir.is_dir():
                test_hits.extend(sorted(tests_dir.glob(f"*{pkg_slug}*.py")))
        runtime_ref = f"runtime:{package}"
        runtime_available = bool(test_hits)
        if runtime_available:
            nodes.append(
                CoverageNode.create(
                    CoverageNodeKind.RUNTIME_ASSET,
                    runtime_ref,
                    authority=f"{completion_rel}+tests",
                )
            )

        # Modules and code assets.
        for module in sorted(pkg_dir.glob("*.py")):
            module_rel = f"{package}/{module.name}"
            nodes.append(
                CoverageNode.create(CoverageNodeKind.MODULE, module_rel, authority=package)
            )
            edges.append(
                CoverageEdge.create(
                    source_kind=CoverageNodeKind.EPIC,
                    source_ref=epic,
                    target_kind=CoverageNodeKind.MODULE,
                    target_ref=module_rel,
                    authority=completion_rel,
                    evidence=f"{epic} module {module_rel}",
                )
            )
            symbols = top_level_symbols(module.read_text(encoding="utf-8"))
            # A module with no public top-level symbol is still a real code asset (its
            # re-export/module-level surface); represent it as one module-level asset so
            # runtime evidence attaches (evidence-grounded — the file exists and is tested).
            if not symbols:
                symbols = ("<module>",)
            for symbol in symbols:
                asset_ref = f"{module_rel}::{symbol}"
                nodes.append(
                    CoverageNode.create(
                        CoverageNodeKind.CODE_ASSET, asset_ref, authority=module_rel
                    )
                )
                edges.append(
                    CoverageEdge.create(
                        source_kind=CoverageNodeKind.MODULE,
                        source_ref=module_rel,
                        target_kind=CoverageNodeKind.CODE_ASSET,
                        target_ref=asset_ref,
                        authority=module_rel,
                        evidence=f"top-level symbol {symbol}",
                    )
                )
                if runtime_available:
                    edges.append(
                        CoverageEdge.create(
                            source_kind=CoverageNodeKind.CODE_ASSET,
                            source_ref=asset_ref,
                            target_kind=CoverageNodeKind.RUNTIME_ASSET,
                            target_ref=runtime_ref,
                            authority=f"{completion_rel}+tests",
                            evidence=f"runtime evidence for {pkg_slug}",
                        )
                    )


__all__ = [
    "RepositoryEvidenceSource",
    "discover_repo_root",
    "parse_universe_rows",
    "parse_imp_names",
    "top_level_symbols",
    "best_match",
]
