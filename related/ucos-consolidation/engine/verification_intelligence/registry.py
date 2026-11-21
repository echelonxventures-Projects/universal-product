"""UVI-000001 Part 03 — the Test Object Registry, and the substrates it is projected from.

A DERIVED PROJECTION, not a new registry. Every field below is read from a surface that
already exists and is already gate-measured:

============================  ==========================================================
Substrate                     Owner
============================  ==========================================================
identity, ownership, edges    ``00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json``
relationship edges            ``00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json``
capability of an owner        ``intelligence/UCOS-RIE-CAPABILITY-CATALOG.json``
what pytest collects          ``pyproject.toml`` ``[tool.pytest.ini_options] testpaths``
measured cost                 ``00-MASTER/UVI-000001/test-cost-model.json``
============================  ==========================================================

The registry adds exactly two things to what those surfaces already say, and both are
projections rather than facts: **collectibility** (a ``TEST_OBJECT`` that pytest would
never collect is not a selectable unit of verification) and **price** (a measured
duration, used only to balance shards). Deleting this projection changes no verdict; it
changes how long reaching the verdict takes.

Authority: NONE — DERIVED TRUTH.
"""

from __future__ import annotations

import fnmatch
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field

from engine.verification_intelligence.constitution import COST_MODEL, repo_root
from engine.verification_intelligence.model import TestObject, VerificationIntelligenceError

EXECUTABLE_REGISTRY = "00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json"

#: The registry that is TOTAL over the version-controlled boundary. 01 is the
#: EXECUTABLE projection of it — a strict subset that omits the 1 233 DOCUMENT_ARTIFACT
#: objects, which is right for import-edge traversal and wrong for a read-set. A stage
#: declaring ``00-BOOK/SCHEMAS/`` or ``00-SOURCE/`` reads documents, and resolving those
#: prefixes against 01 matched NOTHING while 32 tracked, hashed objects sat in 02.
UNIVERSAL_REGISTRY = "00-MASTER/UCOS-UGA-001/02-UNIVERSAL-OBJECT-REGISTRY.json"
RELATIONSHIP_GRAPH = "00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json"
CAPABILITY_CATALOG = "intelligence/UCOS-RIE-CAPABILITY-CATALOG.json"
PYPROJECT = "pyproject.toml"

#: The price of a test object no measurement covers. Deliberately generous: an
#: unmeasured file that is actually slow would otherwise be packed into an already
#: full shard, and the cost of over-pricing is a slightly uneven plan while the cost of
#: under-pricing is one shard the whole run waits on.
DEFAULT_COST_SECONDS = 4.0


def _read_json(path: str, what: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationIntelligenceError(f"{what} is unreadable: {path}") from exc
    if not isinstance(document, dict):
        raise VerificationIntelligenceError(f"{what} is not an object: {path}")
    return document


@dataclass(slots=True)
class Substrates:
    """Every graph selection derives from, loaded once and indexed for reverse walks."""

    objects: dict[str, dict] = field(default_factory=dict)
    #: Every version-controlled object, not only the executable projection. Selection
    #: walks ``objects`` because import edges live there; the evidence read-set resolves
    #: against this, because a stage reads documents as readily as it reads code.
    universal: dict[str, dict] = field(default_factory=dict)
    dependents: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    owner_members: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    by_universal_id: dict[str, str] = field(default_factory=dict)
    relationships: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    capability_of_owner: dict[str, str] = field(default_factory=dict)

    def record(self, path: str) -> dict | None:
        return self.objects.get(path)

    def dependents_of(self, seeds: set[str]) -> set[str]:
        """Transitive reverse closure over import edges.

        Breadth-first over the inverted edge set. Seeds are excluded from the result
        unless something reaches them, so a caller can still distinguish "what changed"
        from "what the change reaches".
        """
        seen: set[str] = set()
        frontier = set(seeds)
        while frontier:
            nxt: set[str] = set()
            for path in frontier:
                for dependent in self.dependents.get(path, ()):
                    if dependent not in seen:
                        seen.add(dependent)
                        nxt.add(dependent)
            frontier = nxt
        return seen

    def related_identities(self, universal_ids: set[str]) -> set[str]:
        """One hop over the relationship graph, in both directions."""
        neighbours: set[str] = set()
        for identity in universal_ids:
            neighbours |= self.relationships.get(identity, set())
        return neighbours - universal_ids


def load_substrates(root: str | None = None) -> Substrates:
    """Load identity, ownership, dependency, capability and relationship in one pass.

    Raises:
        VerificationIntelligenceError: any declared substrate is absent or unusable.
            Fail closed: a selector missing one of its graphs would narrow silently,
            which is the one outcome this design refuses.
    """
    base = root or repo_root()
    substrates = Substrates()

    registry = _read_json(os.path.join(base, EXECUTABLE_REGISTRY), "the executable object registry")
    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        raise VerificationIntelligenceError("the executable object registry holds no entries")
    for entry in entries:
        if not isinstance(entry, dict) or "path" not in entry:
            continue
        path = str(entry["path"])
        substrates.objects[path] = entry
        owner = str(entry.get("owner") or "")
        if owner:
            substrates.owner_members[owner].add(path)
        identity = str(entry.get("universal_id") or "")
        if identity:
            substrates.by_universal_id[identity] = path
        for dependency in entry.get("dependencies") or ():
            substrates.dependents[str(dependency)].add(path)
    if not substrates.dependents:
        raise VerificationIntelligenceError(
            "the registry carries no dependency edges, so impact cannot be computed; "
            "the registry is regenerated by UCOS-UGA-001 under AUTHORIZED identity "
            "allocation (REG-AUTO-001), which is irreversible — obtain that "
            "authorization rather than invoking allocation to clear this error"
        )

    universal = _read_json(os.path.join(base, UNIVERSAL_REGISTRY), "the universal object registry")
    universal_entries = universal.get("entries")
    if not isinstance(universal_entries, list) or not universal_entries:
        raise VerificationIntelligenceError("the universal object registry holds no entries")
    for entry in universal_entries:
        if isinstance(entry, dict) and "path" in entry:
            substrates.universal[str(entry["path"])] = entry

    graph = _read_json(os.path.join(base, RELATIONSHIP_GRAPH), "the relationship graph")
    edges = graph.get("relationships")
    if not isinstance(edges, list) or not edges:
        raise VerificationIntelligenceError("the relationship graph holds no relationships")
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source, target = str(edge.get("from") or ""), str(edge.get("to") or "")
        if not source or not target:
            continue
        substrates.relationships[source].add(target)
        substrates.relationships[target].add(source)

    catalog = _read_json(os.path.join(base, CAPABILITY_CATALOG), "the capability catalogue")
    capabilities = catalog.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise VerificationIntelligenceError("the capability catalogue holds no capabilities")
    for capability in capabilities:
        if not isinstance(capability, dict):
            continue
        location = str(capability.get("canonical_location") or "")
        name = str(capability.get("canonical_name") or location)
        if location:
            substrates.capability_of_owner[location] = name

    return substrates


def collection_roots(root: str | None = None) -> tuple[str, ...]:
    """The paths pytest collects from, DERIVED by Ω-1 rather than read from a declaration.

    This function's original docstring stated the right principle and then implemented the wrong
    version of it: it read ``testpaths`` out of ``pyproject.toml`` because restating the roots here
    "would create a second answer to 'what is the test suite', and the two would drift the first
    time a path was added to one of them". That reasoning was correct and the list it trusted was
    the problem — ``testpaths`` was itself a hand-written enumeration, and four layers holding 188
    test modules and 3,995 passing tests were absent from it for months.

    Under UCOS-OMEGA-001 there is no ``testpaths``. The collectible set is derived from which
    directories hold suites, by the same call ``engine/universal_discovery/pytest_scope.py`` makes
    to configure the run — so this function and the runner cannot disagree, and a tree added
    tomorrow is collected here without an edit.
    """
    base = root or repo_root()
    try:
        from engine.universal_discovery.discovery import derived_scope
        from engine.universal_discovery.model import OmegaError
    except ImportError as exc:  # pragma: no cover - the package is tracked source
        raise VerificationIntelligenceError(
            "the Ω-1 discovery package is unavailable, so the collectible set is unknown"
        ) from exc
    try:
        test_roots, _packages, _exemptions, _transient = derived_scope(base)
    except OmegaError as exc:
        raise VerificationIntelligenceError(
            f"the collectible set could not be derived: {exc}"
        ) from exc
    if not test_roots:
        raise VerificationIntelligenceError(
            "discovery found no test root, so the collectible set is unknown"
        )
    return tuple(test_roots)


def is_collectible(path: str, roots: tuple[str, ...]) -> bool:
    """True when pytest would collect ``path`` under the declared roots.

    ``python_files`` is left at the pytest default because the configuration does not
    override it; the moment it does, this reads it instead of assuming.
    """
    if not path.endswith(".py"):
        return False
    if not any(path == root or path.startswith(root.rstrip("/") + "/") for root in roots):
        return False
    return fnmatch.fnmatch(os.path.basename(path), "test_*.py")


def load_cost_model(root: str | None = None) -> tuple[dict[str, float], dict[str, dict], float]:
    """Measured durations, split tables and the split threshold.

    A missing or unparseable model is not an error. Every test object is then priced at
    the default and nothing is split, which produces a slower plan and never a wrong one.
    """
    target = os.path.join(root or repo_root(), COST_MODEL)
    if not os.path.isfile(target):
        return {}, {}, 0.0
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}, {}, 0.0
    raw_costs = document.get("costs")
    costs = (
        {str(path): float(value) for path, value in raw_costs.items() if _is_number(value)}
        if isinstance(raw_costs, dict)
        else {}
    )
    raw_split = document.get("split")
    split = (
        {str(path): entry for path, entry in raw_split.items() if isinstance(entry, dict)}
        if isinstance(raw_split, dict)
        else {}
    )
    threshold = document.get("split_threshold_seconds")
    return costs, split, float(threshold) if _is_number(threshold) else 0.0


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


@dataclass(slots=True)
class TestObjectRegistry:
    """Every collectible test object, priced and attributed.

    ``by_owner`` is what makes ownership-driven selection possible: a test that
    exercises a module through a subprocess has no import edge to it, but it is owned
    by the same owner, and the owner is recorded truth.
    """

    objects: dict[str, TestObject] = field(default_factory=dict)
    by_owner: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    by_capability: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    roots: tuple[str, ...] = ()
    priced: int = 0
    node_costs: dict[str, float] = field(default_factory=dict)
    splittable: dict[str, tuple[str, ...]] = field(default_factory=dict)
    stale_splits: tuple[str, ...] = ()
    """Objects the cost model declares splittable whose recorded hash no longer matches.

    A STALE ENTRY IS NOT A FAULT, AND THAT IS EXACTLY WHY IT NEEDS REPORTING. Splitting is
    hash-gated: an object whose content moved falls back to whole-file placement, which is
    slower and never wrong — the cost model's own authority text says so and this does not
    contest it. What was missing is that the fallback was SILENT. The comparison happened,
    the plan quietly got worse, and the run looked identical.

    Measured when this was added: one object — the second-most-expensive in the suite, 168.4s
    over 24 nodes — had been placed whole since a commit four earlier moved its hash. The floor
    that put under every wave went unnoticed until someone asked why a wave felt slow.

    THE OBJECT IS DESCRIBED AND NOT NAMED, AND UVI-L-06 IS WHY. "Selection Is Derived, Never
    Authored" refuses any specific test file named anywhere in this module, and it refused the
    first draft of this docstring, which cited the path as evidence. The law is right and the
    prose was wrong: a scanner cannot distinguish a filename in a comment from one in a
    constant, and a selection engine that names a test file has stopped deriving its selection.
    The path belongs in the commit message and in the run's own report, both of which compute
    it. Whatever object is stale appears in `stale_splits` at runtime, measured, never typed.

    Reported, never gated. Making it fail would contradict "slower, never wrong"; making it
    visible is a different claim, and the only one the measurement supports.
    """

    unregistered: tuple[str, ...] = ()
    """Collectible test objects the executable object registry does not hold.

    Reported rather than hidden, and never empty-by-construction: this is the population
    whose absence UVI-L-08 measured as 130 tests in no shard.
    """

    @property
    def paths(self) -> tuple[str, ...]:
        """Every collectible test path, sorted — the whole suite, as a selection."""
        return tuple(sorted(self.objects))

    def cost_of(self, unit: str) -> float:
        """The measured price of one schedulable unit — a test file or a test node."""
        if unit in self.node_costs:
            return self.node_costs[unit]
        entry = self.objects.get(unit)
        return entry.cost_seconds if entry else DEFAULT_COST_SECONDS

    def units_for(self, test_paths: tuple[str, ...]) -> tuple[str, ...]:
        """The schedulable units covering ``test_paths``.

        A test object whose measured cost exceeds the declared threshold is placed as its
        individual nodes; every other object is placed whole. Splitting happens only when
        the recorded content hash still matches the registry's, so the node ids are known
        to be current — a changed file falls back to whole-file placement, which is always
        correct and merely slower. Every node of a split file is present exactly once, so
        the union of the units is exactly ``test_paths``.
        """
        units: list[str] = []
        for path in sorted(set(test_paths)):
            nodes = self.splittable.get(path)
            units.extend(nodes if nodes else (path,))
        return tuple(units)

    def total_cost(self, paths: tuple[str, ...] | None = None) -> float:
        return sum(self.cost_of(path) for path in (paths if paths is not None else self.paths))


def _collectible_on_disk(base: str, roots: tuple[str, ...]) -> tuple[str, ...]:
    """Every file under ``roots`` that pytest would collect, read from the tree.

    The tree is the authority on what pytest will collect, and it is the only authority
    that cannot be stale. ``is_collectible`` decides membership so this function and the
    registry projection above apply the identical rule rather than two that can drift.

    Sorted, and ``__pycache__`` is pruned so the walk cost stays in the roots that matter.
    Deterministic by construction: UVI-L-10 requires two plans over one state to produce
    identical bytes, and an os.walk in filesystem order would not.
    """
    found: list[str] = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(os.path.join(base, root)):
            dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
            for name in sorted(filenames):
                relative = os.path.relpath(os.path.join(dirpath, name), base)
                if is_collectible(relative, roots):
                    found.append(relative)
    return tuple(sorted(found))


def build_test_registry(
    substrates: Substrates | None = None, root: str | None = None
) -> TestObjectRegistry:
    """Project the Test Object Registry from the substrates and the pytest configuration."""
    base = root or repo_root()
    substrates = substrates or load_substrates(base)
    roots = collection_roots(base)
    costs, split, threshold = load_cost_model(base)

    registry = TestObjectRegistry(roots=roots)
    stale: list[str] = []
    for path, entry in substrates.objects.items():
        if entry.get("object_class") != "TEST_OBJECT" or not is_collectible(path, roots):
            continue
        owner = str(entry.get("owner") or "")
        measured = costs.get(path)
        test_object = TestObject(
            path=path,
            universal_id=str(entry.get("universal_id") or ""),
            owner=owner,
            capability=substrates.capability_of_owner.get(owner, ""),
            content_hash=entry.get("content_hash"),
            cost_seconds=float(measured) if measured is not None else DEFAULT_COST_SECONDS,
        )
        registry.objects[path] = test_object
        registry.by_owner[owner].add(path)
        if test_object.capability:
            registry.by_capability[test_object.capability].add(path)
        if measured is not None:
            registry.priced += 1
        entry_split = split.get(path)
        if entry_split is not None and threshold > 0 and (measured or 0.0) > threshold:
            if entry_split.get("content_hash") != test_object.content_hash:
                # The fallback that used to be silent. See `stale_splits` for why this is
                # observed rather than refused.
                stale.append(path)
            else:
                nodes = entry_split.get("nodes")
                if isinstance(nodes, dict) and nodes:
                    registry.splittable[path] = tuple(sorted(str(node) for node in nodes))
                    for node, seconds in nodes.items():
                        if _is_number(seconds):
                            registry.node_costs[str(node)] = float(seconds)

    # --- FAIL WIDE OVER THE UNREGISTERED --------------------------------------------
    # Everything above is projected from the executable object registry. That registry is
    # a REGISTRATION artifact: a test file enters it only when the registration
    # transaction runs, so a newly written test file is absent from it until then. The
    # loop above therefore could not see such a file at all, and the consequence was not
    # that it ran unpriced — it was that it did not run.
    #
    # Measured (UVI-L-08, this repository, 2026-08-22): 130 collectible tests across two
    # files were in NO shard. `pytest` collected them, every shard's argv excluded them,
    # and the sharded suite reported green over a suite that was 130 tests smaller than
    # the one the collector found. A serial run passed. That asymmetry is the single most
    # dangerous defect a verification selector can carry, because parallelising the run
    # is what makes the tests disappear, and going faster is not a symptom anyone reads
    # as a failure.
    #
    # The correction is this engine's own declared principle applied to itself: FAIL WIDE.
    # An object the selector cannot bound is INCLUDED, never dropped. So the collectible
    # set is derived from the declared collection roots and the filesystem, and anything
    # the registry does not hold is admitted as an unregistered object.
    #
    # This is DERIVATION, not authoring, and UVI-L-06 is why the distinction matters: the
    # roots come from `testpaths` in pyproject and the members come from the tree, so no
    # code path here names a test file. Traversal is sorted, so planning twice over one
    # state still produces identical bytes (UVI-L-10).
    #
    # It mints nothing. An unregistered object carries no universal id, no owner and no
    # capability — which is exactly right, because it HAS none until REG-AUTO-001 runs.
    # Registration remains that authority's act; this only refuses to let the absence of
    # registration silently shrink a verification run.
    for path in _collectible_on_disk(base, roots):
        if path in registry.objects:
            continue
        registry.objects[path] = TestObject(
            path=path,
            universal_id="",
            owner="",
            capability="",
            content_hash=None,
            cost_seconds=DEFAULT_COST_SECONDS,
            registered=False,
        )
    registry.unregistered = tuple(
        sorted(path for path, obj in registry.objects.items() if not obj.registered)
    )
    registry.stale_splits = tuple(sorted(stale))

    if not registry.objects:
        raise VerificationIntelligenceError(
            "the Test Object Registry projected no collectible test object; the executable "
            "registry and the pytest configuration disagree about what the suite is"
        )
    return registry
