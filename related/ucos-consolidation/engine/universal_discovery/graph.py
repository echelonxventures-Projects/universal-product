"""UCOS-OMEGA-001 Part 3 (Ω-3) — the execution graph, which is what governance is actually over.

WHY DIRECTORIES WERE THE WRONG DENOMINATOR.

``engine/``, ``platform/``, ``service/`` is a finite list of places. Reachability is not a list of
places, it is a relation, and the relation is what determines whether a line of code can ever
run. Governing the places meant that the same module governed itself differently depending on
where it sat, and the repository already paid for that twice: ``engine/recursive_knowledge`` was
ungoverned for being a namespace directory, and five whole trees were ungoverned for not being
``engine`` or ``platform``.

THE Ω-3 PROPERTY, STATED SO IT CAN BE TESTED: relocating a module changes nothing about its
governance. ``engine/x.py`` and ``galaxy/x.py`` are the same artifact to every verdict this
package produces, because no verdict reads a directory name — reachability reads the import
relation, authority reads declarations and ancestry, and the disposition reads measured content.

THE SEVEN PLANES ARE GROUPED BY TYPE, NEVER COUNTED AS TEXTS.

An artifact reachable from thirty-one workflow files is reachable from ONE plane, ``ci``. That
grouping is what stops "invoked by many things" from being satisfied by a fan of copies of the
same thing, and it is the same construction ``engine/certification_integrity/surface.py`` uses
for its invocation planes.

  import    — another tracked module imports it
  test      — a discovered test root imports it
  python    — ``python -m`` or a direct script invocation, from any orchestration text
  cli       — a declared console entry point
  make      — a Makefile recipe reaches it
  verify    — a ``verify.sh`` stage reaches it
  ci        — any workflow reaches it

DYNAMIC LOADING IS MEASURED, NOT ASSUMED AWAY. ``importlib.import_module("a.b")`` and
``__import__("a.b")`` with a literal argument are edges, and are recorded as such. A dynamic
import whose argument is computed is NOT an edge and is reported as an unresolved dynamic site,
because pretending to resolve it would be the same lie as an enumeration: an answer with no
measurement behind it.
"""

from __future__ import annotations

import ast
import os
import re
from collections.abc import Iterable, Mapping

from engine.universal_discovery.discovery import module_dotted
from engine.universal_discovery.model import OmegaError

PLANE_IMPORT = "import"
PLANE_TEST = "test"
PLANE_PYTHON = "python"
PLANE_CLI = "cli"
PLANE_MAKE = "make"
PLANE_VERIFY = "verify"
PLANE_CI = "ci"

#: Orchestration texts, grouped into the plane TYPE each belongs to. Every workflow collapses
#: into ``ci``; the mapping is over KINDS of text and not over this repository's particular files,
#: so a new workflow or a new shell entry point joins its plane without an edit.
ORCHESTRATION_PLANES: tuple[tuple[str, str], ...] = (
    ("Makefile", PLANE_MAKE),
    ("verify.sh", PLANE_VERIFY),
    (".github/workflows", PLANE_CI),
    ("scripts", PLANE_PYTHON),
)

#: ``python -m package.module`` and ``python path/to/file.py`` in any orchestration text.
MODULE_INVOCATION = re.compile(r"-m\s+([A-Za-z_][A-Za-z0-9_.]*)")

#: A SCRIPT INVOCATION MUST BE A PATH, and the required ``/`` is the whole point of this pattern.
#:
#: THE FALSE POSITIVE THIS CLOSES, measured rather than imagined. The pattern was
#: ``([A-Za-z0-9_./-]+\.py)`` and the match was tested with ``path.endswith("/" + named)``, so a
#: bare filename mentioned in PROSE matched every file sharing that basename. The Makefile
#: carries the sentence "invisible to an ``__init__.py`` predicate" in a comment — and that one
#: comment made all 88 package initialisers in the repository report themselves invoked by the
#: ``make`` and ``ci`` planes. ``model.py``, ``config.py``, ``registry.py``, ``ledger.py`` and
#: ten more were inflating reachability the same way.
#:
#: A path is an invocation. A word in a sentence is not.
SCRIPT_INVOCATION = re.compile(r"([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+\.py)\b")

#: Dynamic import with a LITERAL argument. Resolvable, therefore a real edge.
#:
#: MATCHED ON THE AST, NOT ON THE TEXT, and the difference is a measured defect rather than a
#: preference. The first implementation was a regex over the source, so a STRING containing the
#: call pattern counted as a call — and ``engine/tests/universal_discovery/test_graph.py``, the
#: module whose whole job is to exercise this detector, carries the pattern twice as test data.
#: The detector reported two dynamic import sites that do not exist, the gate refused a
#: regression that had not happened, and the file that legitimately NAMES the pattern was
#: convicted of containing it. String literals are data. Only a call is a call.
_DYNAMIC_FUNCTIONS = ("importlib.import_module", "__import__")


def _callee_name(node: ast.expr) -> str:
    """Dotted name of a call target, or "" when the target is not a plain name or attribute."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _callee_name(node.value)
        return f"{base}.{node.attr}" if base else ""
    return ""


def _dynamic_imports(tree: ast.AST) -> tuple[frozenset[str], int]:
    """``(literal targets, count of unresolvable sites)`` for every dynamic import CALL.

    A literal argument resolves to a real edge; ignoring it would understate the graph. A computed
    argument resolves to nothing and is COUNTED rather than guessed, because pretending to resolve
    it would be the same lie as an enumeration — an answer with no measurement behind it.
    """
    literal: set[str] = set()
    unresolved = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _callee_name(node.func) not in _DYNAMIC_FUNCTIONS:
            continue
        first = node.args[0] if node.args else None
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            literal.add(first.value)
        else:
            unresolved += 1
    return frozenset(literal), unresolved


def _resolve_relative(module: str, node: ast.ImportFrom, *, is_package: bool) -> str:
    """Resolve ``from . import x`` against the importing module's own package.

    ``is_package`` IS LOAD-BEARING AND WAS MEASURED, NOT REASONED. Inside a module, ``from .``
    means "my parent package"; inside that package's ``__init__.py`` it means "me". Treating both
    the same way resolved every relative import in a package initialiser one level too high, which
    silently dropped real edges and made initialisers look like leaves — and a leaf looks governed.
    """
    if not node.level:
        return node.module or ""
    parts = module.split(".")
    depth = node.level - 1 if is_package else node.level
    base = parts[: max(0, len(parts) - depth)]
    if node.module:
        base = [*base, *node.module.split(".")]
    return ".".join(base)


def module_imports(
    source: str, module: str, *, is_package: bool = False
) -> tuple[frozenset[str], int]:
    """Every module name this source imports, plus the count of unresolvable dynamic sites.

    A SYNTAX ERROR IS A FAULT. Returning "no imports" for a file Python cannot parse would make
    an unparseable module look like a leaf, and a leaf looks governed.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise OmegaError(
            f"{module or '<unnamed>'} does not parse, so its edges are unknown: {exc}"
        ) from exc
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            resolved = _resolve_relative(module, node, is_package=is_package)
            if resolved:
                found.add(resolved)
                found.update(f"{resolved}.{alias.name}" for alias in node.names)
    literal, unresolved = _dynamic_imports(tree)
    found.update(literal)
    return frozenset(found), unresolved


def read_text(root: str, path: str) -> str:
    try:
        with open(os.path.join(root, path), encoding="utf-8", errors="surrogateescape") as handle:
            return handle.read()
    except OSError as exc:
        raise OmegaError(f"a tracked file could not be read: {path}: {exc}") from exc


class ImportGraph:
    """The tracked-module import relation, and the reverse relation reachability needs.

    KEYED ON MODULE IDENTITY, NEVER ON PATH. That is the Ω-3 property in one sentence: the graph
    would be identical if every file moved, because an import names a module and not a directory.
    """

    def __init__(
        self,
        root: str,
        paths: Iterable[str],
        sources: Mapping[str, str] | None = None,
    ) -> None:
        self.path_of: dict[str, str] = {}
        self.imports: dict[str, frozenset[str]] = {}
        self.unresolved_dynamic: dict[str, int] = {}
        self.unparsed: tuple[str, ...] = ()
        unparsed: list[str] = []
        paths = tuple(paths)
        for path in paths:
            module = module_dotted(path)
            if module:
                self.path_of[module] = path
        for path in paths:
            module = module_dotted(path)
            source = sources[path] if sources is not None else read_text(root, path)
            key = module or path
            try:
                edges, dynamic = module_imports(
                    source, module, is_package=path.endswith("/__init__.py")
                )
            except OmegaError:
                unparsed.append(path)
                edges, dynamic = frozenset(), 0
            self.imports[key] = edges
            if dynamic:
                self.unresolved_dynamic[key] = dynamic
        self.unparsed = tuple(sorted(unparsed))
        self.imported_by = self._reverse()

    def _reverse(self) -> dict[str, frozenset[str]]:
        """Who imports each tracked module. Foreign names are dropped, not guessed.

        An import of ``json`` names a module this repository does not track, so it contributes no
        edge. Only edges between tracked modules are recorded, which keeps the graph a statement
        about THIS population rather than about the standard library.
        """
        reverse: dict[str, set[str]] = {module: set() for module in self.path_of}
        tracked = set(self.path_of)
        for importer, edges in self.imports.items():
            for target in edges:
                if target in tracked:
                    reverse[target].add(importer)
                    continue
                # ``from a.b import thing`` records ``a.b.thing``; when the leaf is a symbol
                # rather than a module the edge belongs to its parent.
                parent = target.rsplit(".", 1)[0]
                if parent in tracked:
                    reverse[parent].add(importer)
        return {module: frozenset(importers) for module, importers in reverse.items()}

    def importers_of_path(self, path: str) -> frozenset[str]:
        module = module_dotted(path)
        if not module:
            return frozenset()
        return self.imported_by.get(module, frozenset())


def imported_by_path(graph: ImportGraph, paths: Iterable[str]) -> dict[str, frozenset[str]]:
    """The reverse relation expressed over PATHS, which is what test-root derivation needs."""
    out: dict[str, frozenset[str]] = {}
    for path in paths:
        importers = graph.importers_of_path(path)
        out[path] = frozenset(graph.path_of.get(importer, importer) for importer in importers)
    return out


# ------------------------------------------------------------------- orchestration reachability


def orchestration_texts(root: str) -> dict[str, str]:
    """Every orchestration text, discovered by walking the declared plane KINDS.

    Not a list of this repository's workflow files: a list of the KINDS of place orchestration
    lives, walked. A thirty-second workflow is read on the day it is added.
    """
    found: dict[str, str] = {}
    for location, _plane in ORCHESTRATION_PLANES:
        absolute = os.path.join(root, location)
        if os.path.isfile(absolute):
            found[location] = read_text(root, location)
        elif os.path.isdir(absolute):
            for current, _dirs, files in os.walk(absolute):
                for name in sorted(files):
                    if not name.endswith((".yml", ".yaml", ".sh", ".py", ".mk")):
                        continue
                    relative = os.path.relpath(os.path.join(current, name), root)
                    found[relative.replace(os.sep, "/")] = read_text(root, relative)
    if not found:
        raise OmegaError(
            "no orchestration text was found, so every artifact would read as unreachable "
            "and the reachability measurement would be about nothing"
        )
    return found


def plane_for(location: str) -> str:
    for prefix, plane in ORCHESTRATION_PLANES:
        if location == prefix or location.startswith(prefix.rstrip("/") + "/"):
            return plane
    return PLANE_PYTHON


def console_entry_points(root: str) -> frozenset[str]:
    """Declared console scripts, read from ``pyproject.toml``. A CLI is an execution surface."""
    import tomllib

    path = os.path.join(root, "pyproject.toml")
    try:
        with open(path, "rb") as handle:
            config = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise OmegaError(f"declared entry points are unreadable: {exc}") from exc
    scripts = config.get("project", {}).get("scripts", {}) or {}
    return frozenset(str(target).split(":", 1)[0] for target in scripts.values())


def orchestrated_modules(texts: Mapping[str, str]) -> dict[str, set[str]]:
    """``module or script path -> the set of PLANES that invoke it``.

    Grouped by plane type at insertion, so a module named in thirty-one workflows carries one
    plane rather than thirty-one invocations.
    """
    planes: dict[str, set[str]] = {}
    for location, text in texts.items():
        plane = plane_for(location)
        for match in MODULE_INVOCATION.findall(text):
            planes.setdefault(match, set()).add(plane)
        for match in SCRIPT_INVOCATION.findall(text):
            planes.setdefault(match.lstrip("./"), set()).add(plane)
    return planes
