"""UCOS-OMEGA-001 Part 2 (Ω-1) — the population, discovered rather than declared.

THE ONE INPUT IS ``git ls-files '*.py'``.

Not the filesystem, for the reason ``platform/tests/test_coverage_scope.py`` already records: a
control that enumerates the working copy decides differently on a developer's machine than on a
clean checkout, and a control whose verdict depends on local debris gets suppressed. Version
control is the eligibility boundary everywhere else in this repository and it is the boundary
here.

Not a list, for the reason this whole package exists: ``SOURCE_TREES = ("engine", "platform")``
was true when it was written and wrong for five roots afterwards, and nothing could say so,
because a list has no term for what it omits.

EVERY DERIVATION BELOW IS A PROPERTY, NOT A NAME.

  root                — the first path segment of a tracked ``.py`` file. Whatever it is.
  importable root     — that segment is a Python identifier, so a coverage source can name it.
                        ``00-MASTER`` is not one; ``quantum`` would be. The rule is the
                        language's, so no future root can be admitted or refused by taste.
  test root           — the shallowest directory under a root that holds tracked ``test_*.py``.
                        Discovered from the naming pytest itself collects on, applied to
                        whatever tree carries it.
  measurable package  — an importable root's coverage unit. If the root holds modules DIRECTLY
                        it is itself the unit; otherwise each sub-directory carrying tracked
                        Python is. That distinction is measured from the tree, and it is exactly
                        the distinction the hand-written 78-entry list encoded by hand: ``engine``
                        and ``platform`` hold only ``__init__.py`` at their top level and were
                        listed per sub-package; ``service``/``data``/``application``/
                        ``infrastructure``/``intelligence`` hold modules and were listed whole.

A SUB-PACKAGE PREDICATE THAT CANNOT MISS PEP 420. "Contains any tracked ``.py`` at any depth",
never "contains ``__init__.py``". The second predicate is what put ``engine/recursive_knowledge``
— sixteen modules, 2,849 statements, a live gate, a ``verify.sh`` stage, a workflow and 135
tests — outside the denominator while every scope test passed.
"""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping

from engine.omega_infinite.git_provider import GitDiscoveryProvider
from engine.omega_infinite.provider import ProviderError, Selector
from engine.universal_discovery.model import OmegaError

#: ``root -> (test_roots, measurable_packages, exemptions, transient)``.
#:
#: A HAND-ROLLED DICT RATHER THAN ``functools.lru_cache``, and the reason is the Ω-4 ratchet doing
#: its job on this very edit. Adding the cache with ``functools`` and ``typing.NamedTuple`` added
#: two import statements to this module, and ``import_entropy`` — imports per tracked artifact —
#: rose from 8.007283 to 8.008193 and the gate refused it. The bound was not the thing that was
#: wrong, so the bound was not what changed: a module-level dict needs no import, states its key
#: explicitly, and leaves the measurement where it was.
_DERIVED_SCOPE: dict[
    str, tuple[tuple[str, ...], tuple[str, ...], dict[str, str], dict[str, str]]
] = {}

#: pytest's own collection convention, applied to whatever tree carries it. This is a property of
#: the test runner rather than of this repository's layout, which is what makes it survive a tree
#: nobody has created yet.
TEST_MODULE_PREFIX = "test_"
TEST_MODULE_SUFFIX = "_test.py"


def tracked_python(root: str) -> tuple[str, ...]:
    """Every tracked ``.py`` path, POSIX, repo-relative, sorted.

    A missing work tree or an empty answer RAISES. An empty population satisfies every Ω
    invariant, so returning one would convert "this repository is ungoverned" into "this
    repository is fully governed" — the single most dangerous defect this package could have.
    """
    # THE PROVIDER, NOT THE TOOL. The selector carries the same `*.py` narrowing, and the
    # provider raises rather than returning an empty tuple — which is what the paragraph above
    # requires, since an empty population satisfies every Ω invariant and would turn "ungoverned"
    # into "fully governed".
    #
    # Proven identical before the swap: 2,292 paths both ways, sets equal. The pathspec/fnmatch
    # divergence that widened rie/config.py's answer does not arise here, because `*.py` means the
    # same thing to both and the endswith filter below makes the population exact either way.
    try:
        artifacts = GitDiscoveryProvider(root=root).enumerate(Selector(patterns=("*.py",)))
    except ProviderError as exc:
        raise OmegaError(
            "the tracked Python population could not be read from the tracked-content "
            f"provider at {root!r}: {exc}"
        ) from exc
    paths = tuple(
        sorted(a.location.locator for a in artifacts if a.location.locator.endswith(".py"))
    )
    if not paths:
        raise OmegaError(
            f"git tracks no Python under {root!r}; refusing to govern an empty population"
        )
    return paths


def derive_roots(paths: tuple[str, ...]) -> tuple[str, ...]:
    """Every top-level segment that carries tracked Python. The Ω-1 replacement for SOURCE_TREES.

    A file at the repository root has no directory segment and is attributed to ``""``, which is
    a real root with a real authority rather than a case to skip — root-level modules are exactly
    the kind of artifact a tree-keyed list cannot see.
    """
    return tuple(sorted({p.split("/", 1)[0] if "/" in p else "" for p in paths}))


#: Module basenames that ARE importable despite the dunder shape. ``__init__`` makes a directory a
#: package and ``__main__`` is what ``python -m`` executes, so both are real module identities.
#: Excluding them cost 8 CLI entry points their reachability verdict — every ``__main__.py`` in the
#: repository read as unreachable while ``verify.sh``, the Makefile and CI all invoke it as
#: ``python -m <package>``.
IMPORTABLE_DUNDERS: frozenset[str] = frozenset({"__init__", "__main__"})


def is_importable_name(name: str) -> bool:
    """Whether Python could name this segment in an import. The rule is the language's."""
    return name.isidentifier() and (not name.startswith("__") or name in IMPORTABLE_DUNDERS)


def derive_importable_roots(roots: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(r for r in roots if is_importable_name(r))


def is_test_module(path: str) -> bool:
    """The naming pytest collects on, asked of a path rather than of a directory listing."""
    name = os.path.basename(path)
    return name.startswith(TEST_MODULE_PREFIX) or name.endswith(TEST_MODULE_SUFFIX)


#: Modules that support a suite without being one. A directory holding only these plus test
#: modules is still a test directory: ``conftest.py`` is pytest's own fixture mechanism and
#: ``__init__.py`` is how a test tree becomes importable, so neither is source under measurement.
TEST_SUPPORT_MODULES: frozenset[str] = frozenset({"__init__.py", "conftest.py"})


def _tree(paths: tuple[str, ...]) -> dict[str, tuple[list[str], list[str]]]:
    """(files, sub-directories) per directory, built from the tracked population alone."""
    tree: dict[str, tuple[list[str], list[str]]] = {}

    def slot(directory: str) -> tuple[list[str], list[str]]:
        return tree.setdefault(directory, ([], []))

    for path in paths:
        parts = path.split("/")
        directory = "/".join(parts[:-1])
        slot(directory)[0].append(path)
        for depth in range(len(parts) - 1, 0, -1):
            parent = "/".join(parts[: depth - 1])
            child = "/".join(parts[:depth])
            entries = slot(parent)[1]
            if child not in entries:
                entries.append(child)
    return tree


def _suite_member(
    path: str,
    tree: Mapping[str, tuple[list[str], list[str]]],
    imported_by: Mapping[str, frozenset[str]],
) -> bool:
    """Whether this module belongs to a suite rather than being source under measurement.

    THREE PROPERTIES, ALL MEASURED, NONE OF THEM A DIRECTORY NAME.

      1. it is a test module by the convention pytest itself collects on; or
      2. it is suite support — ``conftest.py`` is pytest's fixture mechanism and ``__init__.py``
         is how a tree becomes importable — sitting above a subtree that holds test modules; or
      3. its OWN directory directly holds test modules, and no module outside that directory's
         subtree imports it.

    Property 3 is the load-bearing one, and the locality is exactly what makes it correct. The
    repository holds eighteen suite helpers carrying no ``test_`` prefix —
    ``platform/tests/_coverage_helpers.py``, ``engine/tests/uckp/doubles.py`` and sixteen more —
    and a name-keyed predicate declared their trees "not test directories", which would put
    ``engine.tests`` and ``platform.tests`` into the coverage denominator: 234 test modules
    measured as though they were the product.

    A LOOSER VERSION OF PROPERTY 3 WAS MEASURED AND REJECTED. "No module outside this DIRECTORY
    imports it" swallowed ``service``, ``data``, ``application`` and ``infrastructure`` whole —
    those four layers have zero inbound imports from anywhere else in the repository, so at root
    level every one of their modules trivially satisfied it and all four were classified as test
    trees. Requiring the module's own directory to hold test modules DIRECTLY separates the two
    cases on a property the import graph cannot supply: ``platform/tests`` sits beside its tests,
    ``service/policy.py`` does not.
    """
    directory = os.path.dirname(path)
    name = os.path.basename(path)
    if is_test_module(name):
        return True
    if name in TEST_SUPPORT_MODULES:
        return _holds_test_module(directory, tree)
    files, _directories = tree.get(directory, ([], []))
    if not any(is_test_module(os.path.basename(sibling)) for sibling in files):
        return False
    prefix = directory.rstrip("/") + "/" if directory else ""
    return not any(
        importer != path and not importer.startswith(prefix)
        for importer in imported_by.get(path, frozenset())
    )


def _is_test_directory(
    directory: str,
    tree: Mapping[str, tuple[list[str], list[str]]],
    imported_by: Mapping[str, frozenset[str]],
) -> bool:
    """Whether every tracked module in this subtree belongs to a suite. Recursive and measured."""
    files, directories = tree.get(directory, ([], []))
    if any(not _suite_member(path, tree, imported_by) for path in files):
        return False
    return all(_is_test_directory(child, tree, imported_by) for child in directories)


def _holds_test_module(directory: str, tree: Mapping[str, tuple[list[str], list[str]]]) -> bool:
    files, directories = tree.get(directory, ([], []))
    if any(is_test_module(os.path.basename(path)) for path in files):
        return True
    return any(_holds_test_module(child, tree) for child in directories)


def derive_test_roots(
    paths: tuple[str, ...], imported_by: Mapping[str, frozenset[str]]
) -> tuple[str, ...]:
    """Every MAXIMAL test directory: the shallowest one whose whole subtree is a suite.

    Maximal, so ``engine/tests/unit`` and ``engine/tests/graph`` collapse into ``engine/tests``
    and a deep suite is collected once rather than as twenty-three roots. Derived from the tracked
    tree and the import relation, so the answer for a root nobody has created yet is already
    correct — and a directory called ``tests`` that holds production code is NOT silently dropped
    from the denominator, because the predicate never reads the name.

    RETURNS AN EMPTY TUPLE HONESTLY, and the fault for "this repository has no suite" lives in
    ``assert_suite_exists`` instead. The distinction was measured rather than reasoned: raising
    here made the primitive unable to answer the correct question about a tree that legitimately
    has no tests, and a predicate that cannot be asked about the negative case cannot be tested
    against it.
    """
    tree = _tree(paths)
    roots: list[str] = []
    for directory in sorted(tree):
        if not directory:
            continue
        if any(directory == existing or directory.startswith(existing + "/") for existing in roots):
            continue
        if _holds_test_module(directory, tree) and _is_test_directory(directory, tree, imported_by):
            roots.append(directory)
    return tuple(sorted(roots))


def assert_suite_exists(test_roots: tuple[str, ...]) -> None:
    """A repository whose suite is invisible to discovery would be certified by running nothing.

    Asserted where a REPOSITORY is being governed — the gate and the pytest plugin — and not inside
    the derivation, so that composing the derivation over an arbitrary tree stays possible.
    """
    if not test_roots:
        raise OmegaError(
            "no test root was discovered in the tracked population; a repository whose suite is "
            "invisible to discovery would be certified by running nothing"
        )


def derived_scope(
    root: str,
) -> tuple[tuple[str, ...], tuple[str, ...], dict[str, str], dict[str, str]]:
    """``(test_roots, measurable_packages, exemptions, transient)`` for one repository, memoised.

    WHY A CACHE EXISTS AT ALL, stated as the regression that produced it: deriving the scope walks
    ``git ls-files`` and parses every tracked module, which costs ~4.4 seconds.
    ``engine/certification_integrity`` calls ``read_scope`` on every ``surface.build``, and before Ω
    that call was a millisecond TOML parse — so making it a derivation turned a cheap function into
    a repeated full-tree analysis and the serial suite slowed to a crawl. The cache restores the old
    cost profile without restoring the old lists.

    KEYED ON THE ROOT, and correct for exactly one reason: the tracked population cannot change
    inside a single process run of a gate or a suite. A caller that MUTATES a tree and re-derives
    must use a fresh root — every fixture in the Ω suite does — or call
    ``clear_derived_scope_cache``.
    """
    from engine.universal_discovery import graph

    cached = _DERIVED_SCOPE.get(root)
    if cached is not None:
        return cached

    paths = tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    test_roots = derive_test_roots(paths, graph.imported_by_path(import_graph, paths))
    assert_suite_exists(test_roots)
    exemptions, transient = read_declared(root)
    packages = derive_measurable_packages(paths, test_roots, exemptions=exemptions)
    derived = (test_roots, packages, exemptions, transient)
    _DERIVED_SCOPE[root] = derived
    return derived


def clear_derived_scope_cache() -> None:
    """Drop the memoised derivation. For a caller that has changed the tree in-process."""
    _DERIVED_SCOPE.clear()


def _under_any(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path == p or path.startswith(p.rstrip("/") + "/") for p in prefixes)


def derive_measurable_packages(
    paths: tuple[str, ...],
    test_roots: tuple[str, ...],
    *,
    exemptions: dict[str, str] | None = None,
) -> tuple[str, ...]:
    """The coverage denominator, derived. The Ω-1 replacement for 78 hand-written ``--cov=`` flags.

    Two shapes, chosen by measurement rather than by listing:

      * a root that holds modules DIRECTLY (beyond ``__init__.py``) is itself the unit, because
        naming its sub-packages would leave those modules unmeasured;
      * a root that holds only sub-directories is measured per sub-directory, because naming the
        root would pull its test tree into the denominator through the package graph.

    Declared exemptions are subtracted here and nowhere else, so there is exactly one place a
    package can leave the denominator and it is a place that demands a written reason.
    """
    exempt = dict(exemptions or {})
    by_root: dict[str, set[str]] = {}
    direct: set[str] = set()
    for path in paths:
        if _under_any(path, test_roots):
            continue
        parts = path.split("/")
        if len(parts) < 2 or not is_importable_name(parts[0]):
            continue
        root = parts[0]
        by_root.setdefault(root, set())
        if len(parts) == 2:
            if parts[1] != "__init__.py":
                direct.add(root)
            continue
        if is_importable_name(parts[1]):
            by_root[root].add(parts[1])

    packages: set[str] = set()
    for root, children in by_root.items():
        if root in direct:
            packages.add(root)
            continue
        packages.update(f"{root}.{child}" for child in children)

    def exempted(package: str) -> bool:
        return any(package == e or package.startswith(e + ".") for e in exempt)

    kept = tuple(sorted(p for p in packages if not exempted(p)))
    if not kept:
        raise OmegaError(
            "the derived coverage denominator is empty, so a percentage computed over it "
            "would be a number about nothing"
        )
    return kept


def module_dotted(path: str) -> str:
    """The dotted module name for a path, or "" when no import could name it.

    PATH-INDEPENDENT BY CONSTRUCTION for the Ω-3 relocation property: this returns "" rather
    than guessing whenever any segment is not an identifier, so a governance verdict never
    depends on a directory name Python could not have imported anyway.
    """
    if not path.endswith(".py"):
        return ""
    parts = path[: -len(".py")].split("/")
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts or not all(is_importable_name(p) for p in parts):
        return ""
    return ".".join(parts)


# --------------------------------------------------------------------- the declared inputs
# Two, both of them judgements that Ω requires to be WRITTEN DOWN rather than encoded in a
# predicate. Neither is an enumeration of what exists: each is a claim about something that
# exists, and the claim is refused the moment its subject stops existing.


def read_declared(root: str) -> tuple[dict[str, str], dict[str, str]]:
    """``(exemptions, transient)`` from ``pyproject.toml``. A malformed table is a FAULT.

    ``[tool.ucos.coverage_scope] excluded_packages`` — a package outside the denominator, with a
    reason, which is the only honest form an exclusion can take.

    ``[tool.ucos.omega] transient`` — Ω-2's single admissible route to ``authority = NONE``. An
    entry here is a declaration that the artifact does not persist, which is why it is the one
    disposition a human may assert and the one place an absent owner is not a finding.
    """
    path = os.path.join(root, "pyproject.toml")
    try:
        with open(path, "rb") as handle:
            config = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise OmegaError(f"the Ω declarations are unreadable at {path!r}: {exc}") from exc
    ucos = config.get("tool", {}).get("ucos", {})
    exemptions = {
        entry["package"]: entry["reason"]
        for entry in ucos.get("coverage_scope", {}).get("excluded_packages", [])
    }
    transient = {
        entry["path"]: entry["reason"] for entry in ucos.get("omega", {}).get("transient", [])
    }
    for table, name in ((exemptions, "excluded_packages"), (transient, "transient")):
        for subject, reason in table.items():
            if not str(reason).strip():
                raise OmegaError(
                    f"{name} entry {subject!r} carries no reason; an exemption without a stated "
                    "reason is a silent one, which is the defect the register exists to end"
                )
    return exemptions, transient


def frozen_prefixes(root: str) -> tuple[str, ...]:
    """Trees a declaration freezes, read from the guard that owns the question.

    Ω-5 forbids classifying by location, and this does not classify by location: it asks
    ``engine/foundation/guards/frozen_paths.py`` — the DP-03 guard that already refuses writes to
    these trees — which prefixes it protects. The ARCHIVED disposition therefore tracks the
    guard. A tree that stops being frozen stops being archived with no edit here, and a tree that
    becomes frozen is archived on the same commit, because there is one declaration and Ω reads
    it rather than restating it.
    """
    del root  # the guard is a module-level declaration, not a per-checkout scan
    try:
        from engine.foundation.guards.frozen_paths import FROZEN_PREFIXES
    except ImportError as exc:  # pragma: no cover - the guard is tracked source
        raise OmegaError(
            f"the DP-03 frozen-path guard could not be read, so the ARCHIVED disposition has "
            f"no declared basis: {exc}"
        ) from exc
    if not FROZEN_PREFIXES:
        raise OmegaError("the DP-03 guard declares no frozen prefix; ARCHIVED would be vacuous")
    return tuple(sorted(p.rstrip("/") + "/" for p in FROZEN_PREFIXES))
