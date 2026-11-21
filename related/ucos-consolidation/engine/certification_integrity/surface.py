"""UCI-000001 Part 3 — the executable surface, enumerated by rule.

WHAT AN "EXECUTABLE OBJECT" IS HERE.

Every tracked ``.py`` file, and inside it every class, function and method, plus the four
non-Python executable kinds the repository actually runs: console entry points, module CLIs,
``verify.sh`` stages and the ``00-MASTER`` governance engines. The population comes from
``git ls-files``, never from a list, for the reason ``engine/enforcement_closure/discovery.py``
states: a hand-written list of what exists agrees with itself forever.

THE DENOMINATOR IS A PROPERTY OF THE OBJECT, NOT OF THE MEASUREMENT.

The central move of this module is that ``measured`` is computed from the declared coverage
scope in ``pyproject.toml`` and attached to every object, so "0% covered" and "not in the
denominator" can never again be read as the same fact. They were previously indistinguishable,
because an unmeasured file simply does not appear in ``coverage.xml`` and absence renders as
nothing rather than as zero.

ATTRIBUTION PARTITIONS. A method's statements belong to the method, not also to its class and
its module. Nesting the counts would let one statement be covered three times and make the
totals exceed the file, so every line is attributed to its innermost enclosing object and the
module keeps only what no class or function encloses. The consequence worth stating: summing
``statements`` over all objects of a file equals the file's statement count exactly, which is
the invariant ``contract`` asserts rather than assumes.
"""

from __future__ import annotations

import ast
import os
import re
import tomllib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from engine.certification_integrity import coverage_data
from engine.certification_integrity.model import (
    KIND_CLASS,
    KIND_CLI,
    KIND_ENTRY_POINT,
    KIND_FUNCTION,
    KIND_GOVERNANCE_ENGINE,
    KIND_METHOD,
    KIND_MODULE,
    KIND_WORKFLOW_STAGE,
    PLANE_CI,
    PLANE_ENV,
    PLANE_MAKE,
    PLANE_PYTHON,
    PLANE_TEST,
    PLANE_VERIFY,
    ExecutableObject,
    IntegrityError,
)
from engine.omega_infinite.git_provider import GitDiscoveryProvider
from engine.omega_infinite.provider import ProviderError

#: The invoking texts, grouped into the plane TYPE each belongs to. Grouping is what makes this
#: measurement stricter than a count of texts: every workflow file collapses into one ``ci``
#: plane, so an artifact reachable only from CI cannot report itself multiply invoked.
PLANE_SOURCES = {
    "Makefile": PLANE_MAKE,
    "verify.sh": PLANE_VERIFY,
    "scripts/ucos-env.sh": PLANE_ENV,
}

STAGE_LABEL = re.compile(r'^\s*run_stage "([^"]+)"', re.M)
MAKE_TARGET = re.compile(r"(?m)^([A-Za-z0-9_.-]+)\s*:(?!=)")

#: A file is a governance engine if UEC-000001's naming conventions make it one. The patterns
#: are duplicated from the UEC declaration rather than imported because this module must be able
#: to enumerate the surface even when the declaration is unparseable — and ``contract`` measures
#: that the two populations agree, so duplication that drifts is a refusal rather than a secret.
ENGINE_PATTERNS = (
    re.compile(r"^00-MASTER/[^/]+/[^/]+_engine\.py$"),
    re.compile(r"^engine/[^/]+/gate\.py$"),
)


@dataclass(frozen=True)
class Scope:
    """The declared coverage denominator, read from ``pyproject.toml``.

    Both declarations are read and their DISAGREEMENT is preserved rather than reconciled.
    ``platform/tests/test_coverage_scope.py`` refuses a disagreement, so this class expects
    none; keeping both lets ``contract`` state which one it used instead of silently picking.
    """

    flag_packages: frozenset[str]
    source_paths: frozenset[str]
    excluded_packages: dict[str, str]
    testpaths: tuple[str, ...]
    fail_under: float

    def measures(self, path: str) -> bool:
        return any(path == s or path.startswith(s.rstrip("/") + "/") for s in self.source_paths)

    def is_test(self, path: str) -> bool:
        return any(path.startswith(t.rstrip("/") + "/") for t in self.testpaths)


def read_scope(root: str) -> Scope:
    """The denominator, DERIVED by Ω-1 and no longer parsed from three lists.

    WHAT CHANGED, AND WHY THIS FUNCTION'S NAME NOW OVERSTATES ITS WORK. It used to read three
    enumerations out of ``pyproject.toml`` — ``addopts`` ``--cov=`` flags, ``[tool.coverage.run]
    source`` and ``testpaths`` — and its own docstring described the first two as one denominator
    "declared TWICE and reconciled by nobody". They are gone. ``engine/universal_discovery``
    derives all three from ``git ls-files '*.py'``, so ``flag_packages`` and ``source_paths`` are
    now two VIEWS of one derivation rather than two opinions, and ``Scope``'s comment about
    preserving their disagreement describes a disagreement that can no longer occur.

    WHAT IS STILL READ FROM THE FILE, because both are judgements rather than populations: the
    declared exemption register, and the coverage floor.

    A DERIVATION FAULT IS AN INTEGRITY FAULT. ``OmegaError`` is re-raised as ``IntegrityError`` so
    UCI's callers keep one error type, and so that "discovery could not run" can never be read as
    "discovery found nothing" — the empty-world state in which every no-violations claim is true.
    """
    path = os.path.join(root, "pyproject.toml")
    try:
        with open(path, "rb") as handle:
            config = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise IntegrityError(
            f"the coverage denominator is undeclared or unparseable: {exc}"
        ) from exc
    try:
        report = config["tool"]["coverage"]["report"]
    except KeyError as exc:
        raise IntegrityError(f"pyproject.toml declares no coverage report policy at {exc}") from exc

    from engine.universal_discovery import discovery as omega_discovery
    from engine.universal_discovery.model import OmegaError

    try:
        # Memoised per root: this function is called on every ``surface.build`` and the derivation
        # walks the whole tracked tree. See ``discovery.derived_scope``.
        test_roots, packages, excluded, _transient = omega_discovery.derived_scope(root)
    except OmegaError as exc:
        raise IntegrityError(f"the Ω-1 denominator derivation failed: {exc}") from exc

    return Scope(
        flag_packages=frozenset(packages),
        # ``measures()`` compares PATH prefixes, so the dotted derivation is projected onto paths
        # here. One derivation, two spellings — never two sources of truth.
        source_paths=frozenset(package.replace(".", "/") for package in packages),
        excluded_packages=excluded,
        testpaths=test_roots,
        fail_under=float(report.get("fail_under", 0)),
    )


def tracked_paths(root: str) -> tuple[str, ...]:
    """Version control is the eligibility boundary, as it is for UEC-000001.

    A missing work tree raises rather than returning an empty tuple, because an empty world is
    the state in which every "no violations" claim is true.
    """
    # THE PROVIDER, NOT THE TOOL. This asks TRACKED_CONTENT, which is the one question
    # DiscoveryProvider has always answered, and the provider issues the same
    # `--cached --exclude-standard -z`. `enumerate` sorts and deduplicates, which this call site
    # did by hand, so the population is identical and no verdict can move. The failure semantics
    # match too: the provider raises rather than returning an empty world, which is what the
    # docstring above requires.
    try:
        artifacts = GitDiscoveryProvider(root=root).enumerate()
    except ProviderError as exc:
        raise IntegrityError(f"the tracked-path boundary could not be established: {exc}") from exc
    paths = tuple(sorted(artifact.location.locator for artifact in artifacts))
    if not paths:
        raise IntegrityError("git reports no tracked paths — refusing to measure an empty world")
    return paths


def read_text(root: str, relative: str) -> str:
    try:
        with open(os.path.join(root, relative), encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError):
        return ""


# --------------------------------------------------------------------------- AST attribution


@dataclass
class _Node:
    """One AST-derived object before coverage is joined."""

    name: str
    kind: str
    lineno: int
    end_lineno: int
    own: set[int] = field(default_factory=set)


def _statement_lines(tree: ast.AST) -> set[int]:
    """Every line coverage.py could report a statement on.

    Deliberately excludes docstrings and the bodies of ``if TYPE_CHECKING`` blocks? No — it
    excludes NOTHING. The set is intentionally a superset of what coverage.py counts, and the
    join in ``objects_for`` intersects it with the measured line set, so a disagreement between
    this walker and coverage.py's parser can only ever DROP a line from an object's own count,
    never invent one. Reimplementing coverage.py's arbitration here would be a second parser
    whose bugs would read as coverage findings.
    """
    return {node.lineno for node in ast.walk(tree) if isinstance(node, ast.stmt)}


def _nodes(tree: ast.Module, module: str) -> list[_Node]:
    """Classes, functions and methods with their line ranges, innermost-attributed."""
    found: list[_Node] = []

    def walk(body: Iterable[ast.stmt], prefix: str, in_class: bool) -> None:
        for node in body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                name = f"{prefix}{node.name}"
                found.append(
                    _Node(
                        name=f"{module}::{name}",
                        kind=KIND_METHOD if in_class else KIND_FUNCTION,
                        lineno=node.lineno,
                        end_lineno=node.end_lineno or node.lineno,
                    )
                )
                walk(node.body, f"{name}.", False)
            elif isinstance(node, ast.ClassDef):
                name = f"{prefix}{node.name}"
                found.append(
                    _Node(
                        name=f"{module}::{name}",
                        kind=KIND_CLASS,
                        lineno=node.lineno,
                        end_lineno=node.end_lineno or node.lineno,
                    )
                )
                walk(node.body, f"{name}.", True)
            else:
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.stmt):
                        walk([child], prefix, in_class)
                    else:
                        for grand in ast.walk(child):
                            if isinstance(grand, ast.stmt):
                                walk([grand], prefix, in_class)

    walk(tree.body, "", False)
    return found


def _attribute(nodes: Sequence[_Node], lines: set[int]) -> set[int]:
    """Assign each line to its innermost enclosing node; return what nothing enclosed.

    Innermost wins, so counts partition. Ties (a one-line lambda inside a one-line function)
    resolve to the node with the narrowest span, and equal spans resolve to the later-declared
    node, which is the inner one by construction of ``_nodes``.
    """
    ordered = sorted(nodes, key=lambda n: (n.end_lineno - n.lineno, n.lineno))
    unclaimed = set(lines)
    for line in sorted(lines):
        for node in ordered:
            if node.lineno <= line <= node.end_lineno:
                node.own.add(line)
                unclaimed.discard(line)
                break
    return unclaimed


# ------------------------------------------------------------------------------- the surface


@dataclass
class Surface:
    """The whole enumerated surface, plus the populations the laws quantify over."""

    root: str
    scope: Scope
    objects: tuple[ExecutableObject, ...]
    #: Repository-relative paths of tracked non-test ``.py`` files, partitioned three ways.
    measured_files: tuple[str, ...]
    unmeasured_files: tuple[str, ...]
    test_files: tuple[str, ...]
    #: Unmeasured files that no coverage scope claims AND no UEC discovery rule governs. This
    #: is the mission's "undeclared executable surface".
    undeclared_files: tuple[str, ...]
    engines: tuple[str, ...]
    stages: tuple[str, ...]
    coverage: coverage_data.CoverageReport | None

    def by_kind(self, kind: str) -> tuple[ExecutableObject, ...]:
        return tuple(o for o in self.objects if o.kind == kind)

    def totals(self) -> dict[str, object]:
        measured = [o for o in self.objects if o.measured]
        unmeasured = [o for o in self.objects if not o.measured]
        statements = sum(o.statements for o in self.objects)
        covered = sum(o.covered for o in self.objects)
        measured_statements = sum(o.statements for o in measured)
        measured_covered = sum(o.covered for o in measured)
        return {
            "objects": len(self.objects),
            "objects_measured": len(measured),
            "objects_unmeasured": len(unmeasured),
            "executable_statements": statements,
            "executable_covered": covered,
            "executable_coverage_percent": (
                round(covered * 100.0 / statements, 4) if statements else 100.0
            ),
            "measured_statements": measured_statements,
            "measured_covered": measured_covered,
            "measured_coverage_percent": (
                round(measured_covered * 100.0 / measured_statements, 4)
                if measured_statements
                else 100.0
            ),
            "unmeasured_statements": statements - measured_statements,
            "denominator_share_percent": (
                round(measured_statements * 100.0 / statements, 4) if statements else 100.0
            ),
            "files_measured": len(self.measured_files),
            "files_unmeasured": len(self.unmeasured_files),
            "files_undeclared": len(self.undeclared_files),
            "files_test": len(self.test_files),
        }


def is_engine(path: str) -> bool:
    return any(pattern.match(path) for pattern in ENGINE_PATTERNS)


def _entry_points(root: str) -> dict[str, str]:
    """Declared console scripts, which are executable surfaces nothing else enumerates."""
    try:
        with open(os.path.join(root, "pyproject.toml"), "rb") as handle:
            config = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return dict(config.get("project", {}).get("scripts", {}))


def build(
    root: str,
    *,
    coverage_xml: str | None = None,
    paths: Sequence[str] | None = None,
) -> Surface:
    """Enumerate the surface and join the coverage measurement onto it."""
    scope = read_scope(root)
    tracked = tuple(paths) if paths is not None else tracked_paths(root)

    report: coverage_data.CoverageReport | None = None
    candidate = coverage_xml or os.path.join(root, "coverage.xml")
    if os.path.exists(candidate):
        report = coverage_data.parse(candidate, repository=root)

    python_files = [p for p in tracked if p.endswith(".py")]
    test_files = tuple(p for p in python_files if scope.is_test(p))
    non_test = [p for p in python_files if not scope.is_test(p)]
    measured_files = tuple(p for p in non_test if scope.measures(p))
    unmeasured_files = tuple(p for p in non_test if not scope.measures(p))
    engines = tuple(p for p in non_test if is_engine(p))

    workflows = tuple(
        p for p in tracked if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml"))
    )
    corpus = _corpus(root, workflows)
    test_corpus = _test_corpus(root, test_files)
    source_corpus = _source_corpus(root, non_test)

    stages = tuple(dict.fromkeys(STAGE_LABEL.findall(read_text(root, "verify.sh"))))

    objects: list[ExecutableObject] = []
    for path in non_test:
        objects.extend(
            _objects_for(
                path,
                root=root,
                scope=scope,
                report=report,
                corpus=corpus,
                test_corpus=test_corpus,
                source_corpus=source_corpus,
            )
        )

    # The non-Python kinds. They carry no statements: a verify.sh stage is not a Python object
    # and reporting 0/0 for it would put an unmeasurable 100% into the executable total. Their
    # value is the invocation and tested columns, which is what the mission asks of them.
    for label in stages:
        objects.append(
            ExecutableObject(
                name=f"verify.sh::{label}",
                kind=KIND_WORKFLOW_STAGE,
                module="verify.sh",
                statements=0,
                covered=0,
                missing=0,
                coverage_percent=None,
                tested=label in test_corpus_text(test_corpus),
                invoked=True,
                invocation_planes=(PLANE_VERIFY,),
                measured=False,
            )
        )
    for name, target in sorted(_entry_points(root).items()).__iter__():
        module = target.split(":", 1)[0].replace(".", "/") + ".py"
        planes = _planes_for_needles(
            (name, target, target.split(":", 1)[0]), corpus, source_corpus, test_corpus, module
        )
        objects.append(
            ExecutableObject(
                name=f"console_scripts::{name}",
                kind=KIND_ENTRY_POINT,
                module=module,
                statements=0,
                covered=0,
                missing=0,
                coverage_percent=None,
                tested=PLANE_TEST in planes,
                invoked=bool(planes - {PLANE_TEST}),
                invocation_planes=tuple(sorted(planes)),
                measured=False,
            )
        )

    undeclared = tuple(
        p
        for p in unmeasured_files
        if not is_engine(p) and not p.startswith("00-MASTER/") and _has_executable_code(root, p)
    )

    return Surface(
        root=root,
        scope=scope,
        objects=tuple(objects),
        measured_files=measured_files,
        unmeasured_files=unmeasured_files,
        test_files=test_files,
        undeclared_files=undeclared,
        engines=engines,
        stages=stages,
        coverage=report,
    )


def test_corpus_text(test_corpus: dict[str, str]) -> str:
    return "\n".join(test_corpus.values())


def _has_executable_code(root: str, path: str) -> bool:
    """True when the file has a statement that is not an import or a docstring.

    Without this, every ``__init__.py`` re-export would report as undeclared executable
    surface, which would swamp the finding that matters with 400 files of nothing.
    """
    try:
        tree = ast.parse(read_text(root, path))
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, ast.Import | ast.ImportFrom):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        if isinstance(node, ast.Assign | ast.AnnAssign) and not isinstance(
            getattr(node, "value", None), ast.Lambda | ast.Call
        ):
            continue
        return True
    return False


def _corpus(root: str, workflows: Sequence[str]) -> dict[str, tuple[str, str]]:
    """text-key -> (plane type, text). Workflows all share the ``ci`` plane type."""
    corpus: dict[str, tuple[str, str]] = {}
    for relative, plane in PLANE_SOURCES.items():
        corpus[relative] = (plane, read_text(root, relative))
    for workflow in workflows:
        corpus[workflow] = (PLANE_CI, read_text(root, workflow))
    return corpus


def _evidence(text: str) -> str:
    """Imports, evaluated string constants and identifiers — docstrings excluded.

    Identical in intent to ``engine/enforcement_closure/discovery.source_evidence``, and
    excluding prose is load-bearing for the same measured reason recorded there: counting
    docstrings as evidence moved that package's untested-engine deficit from 18 to 16 on prose
    alone. A module that DESCRIBES an engine has not invoked it.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ""
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            first = node.body[0] if node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                docstrings.add(id(first.value))
    parts: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in docstrings:
                parts.append(node.value)
        elif isinstance(node, ast.Import):
            parts.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            parts.append(module)
            parts.extend(f"{module}.{alias.name}" for alias in node.names)
        elif isinstance(node, ast.Attribute):
            parts.append(node.attr)
        elif isinstance(node, ast.Name):
            parts.append(node.id)
    return "\n".join(parts)


def _test_corpus(root: str, test_files: Sequence[str]) -> dict[str, str]:
    return {path: _evidence(read_text(root, path)) for path in test_files}


def _source_corpus(root: str, non_test: Sequence[str]) -> dict[str, str]:
    return {path: _evidence(read_text(root, path)) for path in non_test}


def module_dotted(path: str) -> str:
    return path[: -len(".py")].replace("/", ".").removesuffix(".__init__")


def _needles_for(path: str) -> tuple[str, ...]:
    """The strings that constitute naming this file, strictly.

    A bare package name is NOT a needle. UEC-000001 records the hostile audit that forced this:
    repointing every caller of ``engine/recursive_knowledge/gate.py`` at a non-existent
    attribute of the same package left its invocation law green, because the package name still
    matched. Only the module path and the file path count.
    """
    dotted = module_dotted(path)
    needles = {path, dotted}
    if path.endswith("/gate.py") or path.endswith("_engine.py"):
        needles.add(os.path.basename(path))
    return tuple(sorted(needles))


def _planes_for_needles(
    needles: Sequence[str],
    corpus: dict[str, tuple[str, str]],
    source_corpus: dict[str, str],
    test_corpus: dict[str, str],
    own_path: str,
) -> set[str]:
    planes: set[str] = set()
    for key, (plane, text) in corpus.items():
        if key == own_path:
            continue
        if any(needle and needle in text for needle in needles):
            planes.add(plane)
    for key, evidence in source_corpus.items():
        if key == own_path:
            continue
        if any(needle and needle in evidence for needle in needles):
            planes.add(PLANE_PYTHON)
            break
    for evidence in test_corpus.values():
        if any(needle and needle in evidence for needle in needles):
            planes.add(PLANE_TEST)
            break
    return planes


def _objects_for(
    path: str,
    *,
    root: str,
    scope: Scope,
    report: coverage_data.CoverageReport | None,
    corpus: dict[str, tuple[str, str]],
    test_corpus: dict[str, str],
    source_corpus: dict[str, str],
) -> list[ExecutableObject]:
    text = read_text(root, path)
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    measured = scope.measures(path)
    file_coverage = report.files.get(path) if report else None
    # A file inside the declared scope that coverage never reported is a file no test imported.
    # Its statements are real and its covered count is zero, and that distinction is exactly
    # what ``measured`` preserves: measured-and-zero is a coverage gap, unmeasured-and-zero is
    # a governance gap, and they have different remedies.
    hit = set(file_coverage.hit) if file_coverage else set()
    countable = _statement_lines(tree)
    if file_coverage is not None:
        countable &= file_coverage.hit | file_coverage.missed

    nodes = _nodes(tree, path)
    module_own = _attribute(nodes, countable)

    needles = _needles_for(path)
    planes = _planes_for_needles(needles, corpus, source_corpus, test_corpus, path)
    module_tested = PLANE_TEST in planes
    invoked = bool(planes - {PLANE_TEST})
    plane_tuple = tuple(sorted(planes))

    def build_object(name: str, kind: str, own: set[int], tested: bool) -> ExecutableObject:
        covered = len(own & hit)
        return ExecutableObject(
            name=name,
            kind=kind,
            module=path,
            statements=len(own),
            covered=covered,
            missing=len(own) - covered,
            coverage_percent=(
                (round(covered * 100.0 / len(own), 4) if own else 100.0) if measured else None
            ),
            tested=tested,
            invoked=invoked,
            invocation_planes=plane_tuple,
            measured=measured,
            missing_lines=tuple(sorted(own - hit)),
        )

    kind = KIND_GOVERNANCE_ENGINE if is_engine(path) else KIND_MODULE
    if kind is KIND_MODULE and _is_cli(tree):
        kind = KIND_CLI
    objects = [build_object(path, kind, module_own, module_tested)]
    evidence_of_tests = test_corpus_text(test_corpus)
    for node in nodes:
        short = node.name.split("::", 1)[1].split(".")[-1]
        tested = module_tested and (short in evidence_of_tests or bool(node.own & hit))
        objects.append(build_object(node.name, node.kind, node.own, tested))
    return objects


def _is_cli(tree: ast.Module) -> bool:
    """A module with a ``__main__`` guard or an argparse parser is an invocable CLI."""
    for node in tree.body:
        if isinstance(node, ast.If):
            test = node.test
            if (
                isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
            ):
                return True
    return any(
        isinstance(node, ast.Attribute) and node.attr == "ArgumentParser" for node in ast.walk(tree)
    )
