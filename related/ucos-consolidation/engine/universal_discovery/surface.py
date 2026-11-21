"""UCOS-OMEGA-001 Part 7 — the five phases, joined over ONE population.

WHY THE JOIN IS THE PRODUCT. The repository already computed a coverage scope, an executable
surface, a governed surface and a discovery surface — four populations, independently derived, and
no code had ever asked whether they agreed. A file could sit in exactly one of them indefinitely,
and 619 did. Ω computes ONE population and derives every verdict from it, so disagreement between
verdicts is not a thing that can happen rather than a thing that is checked for.

Read in this order: ``discovery`` (Ω-1) answers what exists; ``graph`` (Ω-3) answers what reaches
it; ``authority`` (Ω-2) answers who owns it; ``classification`` (Ω-5) answers how it is governed;
``ratchet`` (Ω-4) answers whether that got worse. This module runs them once, in that order,
because each takes the previous one's output and none of them takes a list.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from dataclasses import dataclass

# ONE import node rather than three. `_structure` counts import STATEMENTS per artifact and
# `import_entropy` is a ratchet over that count, so three `from engine.universal_discovery import`
# lines cost three where one does the same work. Merged when the UEC-L-04 gate delegation added an
# import elsewhere in this package: the bound was not the thing that was wrong, so the bound is not
# what changed.
from engine.universal_discovery import (
    authority as authority_module,
)
from engine.universal_discovery import (
    classification as classification_module,
)
from engine.universal_discovery import (
    discovery,
    graph,
    ratchet,
)
from engine.universal_discovery.model import (
    CONVERGENT,
    DENSITY,
    DISPOSITIONS,
    ENTROPY,
    MEASURED,
    MONOTONIC,
    SURFACE_DISPOSITIONS,
    TRANSIENT,
    Artifact,
    Observation,
    OmegaError,
    Population,
)

SCHEMA = "ucos-omega-surface"
VERSION = "1.0.0"

#: Where the sealed ratchet state lives. One path, inside the programme home that owns it, so the
#: Ω-A-03 ancestry rule assigns its authority the same way it assigns every other programme's.
RATCHET_STATE = os.path.join("00-MASTER", "UCOS-OMEGA-001", "omega-ratchet.json")


@dataclass(frozen=True)
class OmegaSurface:
    population: Population
    artifacts: tuple[Artifact, ...]
    observations: tuple[Observation, ...]
    totals: dict[str, object]
    unresolved_dynamic: dict[str, int]
    unparsed: tuple[str, ...]
    #: Retained so the Ω-3 relocation proof costs no second read and no second parse. Excluded
    #: from ``digest`` and from ``as_document``: they are inputs to the measurement, not results
    #: of it, and putting inputs in the evidence would make the digest change when a comment did.
    source_heads: dict[str, str]
    imported_by: dict[str, frozenset[str]]
    frozen: tuple[str, ...]

    def digest(self) -> str:
        payload = {
            "artifacts": [a.as_record() for a in self.artifacts],
            "totals": self.totals,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def by_disposition(self, disposition: str) -> tuple[Artifact, ...]:
        return tuple(a for a in self.artifacts if a.disposition == disposition)

    def by_rule(self, rule: str) -> tuple[Artifact, ...]:
        return tuple(a for a in self.artifacts if a.disposition_rule == rule)

    def as_document(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "authority": "NONE — DERIVED TRUTH. Measurement of tracked repository state.",
            "producer": "engine/universal_discovery/surface.py",
            "determinism": (
                "No wall clock, no commit identity, no working-tree status. The bytes are a pure "
                "function of tracked content, so two runs over one tree are byte-identical."
            ),
            "discovered": {
                "tracked_python": len(self.population.paths),
                "roots": list(self.population.roots),
                "importable_roots": list(self.population.importable_roots),
                "test_roots": list(self.population.test_roots),
                "measurable_packages": list(self.population.measurable_packages),
            },
            "totals": self.totals,
            "ratchet": [o.as_record() for o in self.observations],
            "unresolved_dynamic_import_sites": dict(sorted(self.unresolved_dynamic.items())),
            "unparsed": list(self.unparsed),
            "artifacts": [a.as_record() for a in self.artifacts],
        }


# --------------------------------------------------------------------------- structural measures


def _structure(source: str) -> tuple[int, int, int]:
    """``(statements, callables, imports)`` from the AST alone.

    NEVER intersected with a coverage report. A structural measure that changes because
    ``coverage.xml`` happened to exist is not a measure of the repository, and UCI-L-06 already
    moved 10→9 on exactly that — the presence of an artifact it did not measure.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0, 0, 0
    statements = len({n.lineno for n in ast.walk(tree) if isinstance(n, ast.stmt)})
    callables = sum(
        1
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
    )
    imports = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Import | ast.ImportFrom))
    return statements, callables, imports


# ------------------------------------------------------------------------------- reachability


def _invoking_planes(
    paths: tuple[str, ...],
    import_graph: graph.ImportGraph,
    orchestrated: dict[str, set[str]],
    entry_points: frozenset[str],
    test_roots: tuple[str, ...],
) -> dict[str, frozenset[str]]:
    """Every plane that reaches each artifact, grouped by plane TYPE.

    THE GROUPING IS THE STRICTNESS. An artifact named in thirty-one workflow files is reached by
    ONE plane, ``ci``, so "invoked by many things" cannot be satisfied by a fan of copies of the
    same thing. Without the grouping, adding a workflow would improve every metric here.
    """
    planes: dict[str, set[str]] = {path: set() for path in paths}
    for path in paths:
        module = discovery.module_dotted(path)
        # A test module is reached by the suite that COLLECTS it, and pytest collects by walking
        # the test root rather than by importing from elsewhere. Without this, 703 of the 741
        # artifacts this measurement called unreachable were test modules — every one of which
        # runs on every ``./verify.sh``. "Nothing imports it" and "nothing runs it" are different
        # facts, and conflating them would have made the suite look like dead code.
        if discovery._under_any(path, test_roots):
            planes[path].add(graph.PLANE_TEST)
        importers = import_graph.importers_of_path(path)
        if importers:
            planes[path].add(graph.PLANE_IMPORT)
        for importer in importers:
            importer_path = import_graph.path_of.get(importer, importer)
            if discovery._under_any(importer_path, test_roots):
                planes[path].add(graph.PLANE_TEST)
        if module:
            for named, named_planes in orchestrated.items():
                if named == module or module.startswith(named + "."):
                    planes[path].update(named_planes)
            if any(ep == module or ep.startswith(module + ".") for ep in entry_points):
                planes[path].add(graph.PLANE_CLI)
        # A script invocation is matched as a FULL PATH, never by basename. Suffix matching let a
        # bare ``__init__.py`` in a Makefile comment claim every package initialiser in the tree.
        for named, named_planes in orchestrated.items():
            if named.endswith(".py") and named == path:
                planes[path].update(named_planes)
    return {path: frozenset(found) for path, found in planes.items()}


# ------------------------------------------------------------------------------------- the join


def build(root: str = ".") -> OmegaSurface:
    """Run all five phases over one discovered population."""
    paths = discovery.tracked_python(root)
    sources = {path: graph.read_text(root, path) for path in paths}

    # Ω-3 first: the import relation is what Ω-1's test-root derivation needs, because eighteen
    # suite helpers carry no test naming and only the graph can tell a helper from a product.
    import_graph = graph.ImportGraph(root, paths, sources)
    imported_by = graph.imported_by_path(import_graph, paths)

    # Ω-1
    roots = discovery.derive_roots(paths)
    test_roots = discovery.derive_test_roots(paths, imported_by)
    discovery.assert_suite_exists(test_roots)
    exemptions, transient = discovery.read_declared(root)
    measurable = discovery.derive_measurable_packages(paths, test_roots, exemptions=exemptions)
    population = Population(
        paths=paths,
        roots=roots,
        importable_roots=discovery.derive_importable_roots(roots),
        test_roots=test_roots,
        measurable_packages=measurable,
        declared_exemptions=exemptions,
        declared_transient=transient,
    )
    _assert_declarations_live(population)

    # Ω-3, continued: orchestration planes.
    orchestrated = graph.orchestrated_modules(graph.orchestration_texts(root))
    entry_points = graph.console_entry_points(root)
    planes = _invoking_planes(paths, import_graph, orchestrated, entry_points, test_roots)

    # Ω-5
    frozen = discovery.frozen_prefixes(root)
    heads = {
        path: "\n".join(sources[path].splitlines()[: classification_module.MARKER_WINDOW])
        for path in paths
    }
    dispositions: dict[str, tuple[str, str, str]] = {}
    for path in paths:
        dispositions[path] = classification_module.classify(
            path,
            source_head=heads[path],
            measurable_packages=measurable,
            test_roots=test_roots,
            frozen=frozen,
            declared_exemptions=exemptions,
            declared_transient=transient,
        )
    classification_module.assert_total(dispositions)

    # Ω-2. Two passes, because Ω-A-05 inherits from importers and an importer's own authority must
    # be known first. The second pass reads the first pass's answers and never its own, so the
    # result cannot depend on iteration order.
    contracts = authority_module.ContractIndex(root)
    first: dict[str, tuple[str, str]] = {}
    for path in paths:
        first[path] = authority_module.derive_authority(
            path,
            source=sources[path],
            contracts=contracts,
            invoking_planes=planes,
            importer_authorities={},
            transient=transient,
        )
    importer_authorities: dict[str, frozenset[str]] = {}
    for path in paths:
        owners = {
            first[import_graph.path_of[importer]][0]
            for importer in import_graph.importers_of_path(path)
            if importer in import_graph.path_of
        }
        importer_authorities[path] = frozenset(o for o in owners if o)
    authorities: dict[str, tuple[str, str]] = {}
    for path in paths:
        authorities[path] = authority_module.derive_authority(
            path,
            source=sources[path],
            contracts=contracts,
            invoking_planes=planes,
            importer_authorities=importer_authorities,
            transient=transient,
        )
    authority_module.assert_total(authorities, transient)

    artifacts = []
    for path in paths:
        statements, callables, imports = _structure(sources[path])
        disposition, rule, reason = dispositions[path]
        owner, owner_rule = authorities[path]
        artifacts.append(
            Artifact(
                path=path,
                root=path.split("/", 1)[0] if "/" in path else "",
                module=discovery.module_dotted(path),
                disposition=disposition,
                disposition_rule=rule,
                disposition_reason=reason,
                authority=owner,
                authority_rule=owner_rule,
                reachable=bool(planes[path]),
                reached_by=tuple(sorted(planes[path])),
                statements=statements,
                callables=callables,
                imports=imports,
            )
        )
    frozen_artifacts = tuple(artifacts)
    observations = measure(frozen_artifacts, import_graph, os.path.join(root, RATCHET_STATE))
    return OmegaSurface(
        population=population,
        artifacts=frozen_artifacts,
        observations=observations,
        totals=_totals(frozen_artifacts, population),
        unresolved_dynamic=dict(import_graph.unresolved_dynamic),
        unparsed=import_graph.unparsed,
        source_heads=heads,
        imported_by=dict(imported_by),
        frozen=frozen,
    )


def _assert_declarations_live(population: Population) -> None:
    """A declared exemption or transient whose subject is gone is a REFUSAL, not a leftover.

    Same construction the coverage-scope control already used, kept because it is what stops a
    reasoned register from decaying into a blanket one: an excuse that stops being true has to
    cost something.
    """
    packages = set(population.measurable_packages)
    present_packages = {
        package
        for path in population.paths
        for package in [discovery.module_dotted(path)]
        if package
    }
    stale = sorted(
        package
        for package in population.declared_exemptions
        if not any(m == package or m.startswith(package + ".") for m in present_packages)
    )
    if stale:
        raise OmegaError(
            "these packages are declared exempt from the coverage denominator but no tracked "
            f"module belongs to them, so the exemption is stale: {stale}"
        )
    measured_but_exempt = sorted(
        package for package in population.declared_exemptions if package in packages
    )
    if measured_but_exempt:
        raise OmegaError(
            "these packages are declared exempt AND appear in the derived denominator, so the "
            f"exemption is stale in the other direction: {measured_but_exempt}"
        )
    missing = sorted(p for p in population.declared_transient if p not in set(population.paths))
    if missing:
        raise OmegaError(
            f"these paths are declared transient but git does not track them: {missing}"
        )


def _totals(artifacts: tuple[Artifact, ...], population: Population) -> dict[str, object]:
    surface = [a for a in artifacts if a.disposition in SURFACE_DISPOSITIONS]
    measured = [a for a in surface if a.disposition == MEASURED]
    statements = sum(a.statements for a in surface)
    measured_statements = sum(a.statements for a in measured)
    return {
        "artifacts": len(artifacts),
        "by_disposition": {
            disposition: {
                "files": sum(1 for a in artifacts if a.disposition == disposition),
                "statements": sum(a.statements for a in artifacts if a.disposition == disposition),
            }
            for disposition in DISPOSITIONS
        },
        "by_disposition_rule": {
            rule: sum(1 for a in artifacts if a.disposition_rule == rule)
            for rule in sorted({a.disposition_rule for a in artifacts})
        },
        "by_authority_rule": {
            rule: sum(1 for a in artifacts if a.authority_rule == rule)
            for rule in sorted({a.authority_rule for a in artifacts})
        },
        "distinct_authorities": len({a.authority for a in artifacts if a.authority}),
        "authority_coverage_percent": round(
            100.0
            * sum(1 for a in artifacts if a.authority or a.disposition == TRANSIENT)
            / len(artifacts),
            4,
        ),
        "executable_surface_files": len(surface),
        "executable_surface_statements": statements,
        "measured_surface_statements": measured_statements,
        "measured_surface_percent": round(100.0 * measured_statements / statements, 4)
        if statements
        else 0.0,
        "unreachable_files": sum(1 for a in artifacts if not a.reachable),
        "discovered_roots": len(population.roots),
        "discovered_test_roots": len(population.test_roots),
        "discovered_measurable_packages": len(population.measurable_packages),
    }


# ------------------------------------------------------------------------------------- Ω-4


def metrics(
    artifacts: tuple[Artifact, ...], import_graph: graph.ImportGraph
) -> tuple[tuple[str, str, float, str, tuple[int, int] | None], ...]:
    """Every ratcheted metric, as ``(name, kind, value, subject, ratio)``.

    NOT A THRESHOLD IN SIGHT. Each entry is a measurement and a DIRECTION; the bound it is held to
    is whatever this repository has already achieved, read from the sealed state at comparison
    time. That is what makes the set scale-free: a repository ten times this size produces ten
    times these counts for the count metrics and the SAME values for the density ones, and the
    density ones are the ones that carry the architectural claim.
    """
    surface = [a for a in artifacts if a.disposition in SURFACE_DISPOSITIONS]
    unexplained = [
        a for a in artifacts if a.disposition_rule == classification_module.RULE_UNEXPLAINED
    ]
    unnameable = [
        a for a in artifacts if a.disposition_rule == classification_module.RULE_UNNAMEABLE
    ]
    declared_exempt = [
        a for a in artifacts if a.disposition_rule == classification_module.RULE_DECLARED_EXEMPT
    ]
    last_resort = [a for a in artifacts if a.authority_rule == authority_module.RULE_REPOSITORY]
    unreachable = [a for a in artifacts if not a.reachable]
    ungoverned_statements = sum(a.statements for a in surface if a.disposition != MEASURED)
    surface_statements = sum(a.statements for a in surface)
    callables = sum(a.callables for a in artifacts)
    imports = sum(a.imports for a in artifacts)

    return (
        (
            "unexplained_exemptions",
            CONVERGENT,
            float(len(unexplained)),
            "artifacts no Ω-5 rule could explain (Ω-C-07). The bucket that must empty.",
            None,
        ),
        (
            "unnameable_exemptions",
            CONVERGENT,
            float(len(unnameable)),
            "artifacts no coverage source could name because their root is not a Python "
            "identifier (Ω-C-06). Falls when a governance engine becomes importable.",
            None,
        ),
        (
            "declared_exemptions",
            MONOTONIC,
            float(len(declared_exempt)),
            "artifacts an owner declared outside the denominator with a reason (Ω-C-05).",
            None,
        ),
        (
            "authority_of_last_resort",
            CONVERGENT,
            float(len(last_resort)),
            "artifacts owned only by the unconditional rule (Ω-A-07). Every one is a file no "
            "declaration, home, plane or importer claimed.",
            None,
        ),
        (
            "unreachable_artifacts",
            CONVERGENT,
            float(len(unreachable)),
            "artifacts no import, plane or entry point reaches. Code that cannot run.",
            None,
        ),
        (
            "unresolved_dynamic_sites",
            MONOTONIC,
            float(sum(import_graph.unresolved_dynamic.values())),
            "dynamic imports whose argument is computed, so no edge could be measured.",
            None,
        ),
        (
            "unmeasured_surface_density",
            DENSITY,
            ratchet.ratio(ungoverned_statements, surface_statements),
            "statements on the executable surface that no measurement covers, over all surface "
            "statements. SCALE-FREE: growth cannot breach it and cannot flatter it.",
            (ungoverned_statements, surface_statements),
        ),
        (
            "import_entropy",
            ENTROPY,
            ratchet.ratio(imports, len(artifacts)),
            "import statements per tracked artifact. Bounds how tangled the AVERAGE artifact may "
            "get, independently of how many artifacts exist.",
            (imports, len(artifacts)),
        ),
        (
            "statement_entropy",
            ENTROPY,
            ratchet.ratio(surface_statements, max(callables, 1)),
            "surface statements per callable. Rises when code accretes outside named, testable "
            "units, which is the shape unmeasurable code takes.",
            (surface_statements, max(callables, 1)),
        ),
    )


def measure(
    artifacts: tuple[Artifact, ...], import_graph: graph.ImportGraph, state_path: str
) -> tuple[Observation, ...]:
    state = ratchet.load(state_path)
    observations = tuple(
        state.observe(name, kind, value, subject, ratio=ratio_pair)
        for name, kind, value, subject, ratio_pair in metrics(artifacts, import_graph)
    )
    # A floor is a claim about the work, so it is checked against the work on every run.
    ratchet.assert_floors_live(state, observations)
    return observations
