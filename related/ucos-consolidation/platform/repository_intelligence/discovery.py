"""UCOS-EPIC-014 — The eight repository-discovery dimensions (Terminal T5).

Each dimension is a **pure, deterministic function of the substrate** — no I/O, no
wall-clock, no ambient state — so the same repository content always yields the same
findings, and the whole set can be re-run continuously on every change.

    1. :func:`discover_repository` — what exists (units, zones, readability).
    2. :func:`discover_capabilities` — what it can do. **Composed** from the UCOS-RIE-001
       catalog; this module never re-derives capability identity or reuse policy.
    3. :func:`discover_reuse` — what is *provably* reused, which is what turns "never
       duplicate capabilities" from a slogan into a checkable property.
    4. :func:`discover_dependencies` — what depends on what (the real import graph).
    5. :func:`discover_gaps` — what is missing or unregistered.
    6. :func:`discover_conflicts` — where the repository contradicts itself.
    7. :func:`detect_duplicates` — what is duplicated, classified rather than merely flagged.
    8. :func:`discover_ownership` — who owns each unit, and on what basis.

Severity doctrine (uniform across dimensions, so the aggregate verdict means something):

    * **BLOCKING** — a *contradiction* or defect: the repository asserts two incompatible
      things, or an invariant is provably broken (unparseable module, import cycle, layer
      violation, phantom catalog entry, unresolvable declaration, byte-identical duplicate).
    * **ADVISORY** — *incompleteness*: something is absent, unproven or unregistered.
      Real, reported, and recommendation-generating, but not a self-contradiction.

Boundary with existing owners (no duplication of capability):
    * capability identity/category/authority/reuse policy → ``intelligence/rie``.
    * Registry-Truth gaps (dangling edges, volume mismatches, traceability) →
      :mod:`platform.measurement.gaps`. The gaps found *here* are **code- and
      declaration-substrate** gaps, a disjoint universe with its own code namespace.
    * acceptance adjudication over a supplied inventory → :mod:`engine.acceptance.gates`,
      which :mod:`platform.repository_intelligence.validation` composes rather than copies.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from platform.repository_intelligence.contracts import (
    CapabilityRecord,
    DependencyEdge,
    DimensionResult,
    DiscoveryDimension,
    EdgeKind,
    Finding,
    FindingStatus,
    OwnershipRecord,
    RepositoryUnit,
    ReuseAssessment,
    ReuseProof,
    Severity,
    UnitKind,
)
from platform.repository_intelligence.graph import strongly_connected_components
from platform.repository_intelligence.substrate import (
    CATALOG_SOURCE_ABSENT,
    ModuleFact,
    RepositorySubstrate,
)
from typing import Any

# -- finding codes ----------------------------------------------------------
SUBSTRATE_PRESENT = "repository-substrate-present"
CATALOG_COMPOSED = "capability-catalog-composed"
MODULE_UNPARSED = "repository-module-unparsed"

CATALOG_OMISSION = "capability-catalog-omission"
CATALOG_PHANTOM = "conflict-catalog-phantom"
CATALOG_GRANULARITY = "capability-catalog-granularity"
CAPABILITY_UNDOCUMENTED = "capability-undocumented"

REUSE_DIRECTIVE_MISSING = "reuse-directive-missing"
REUSE_UNPROVEN = "reuse-unproven"

DEPENDENCY_ACYCLIC = "dependency-graph-acyclic"
DEPENDENCY_UNRESOLVABLE = "dependency-unresolvable-internal"
DEPENDENCY_UNDECLARED = "conflict-undeclared-dependency"
DEPENDENCY_COMPANION_ROOT = "dependency-companion-root"

GAP_UNTESTED = "capability-untested"
GAP_UNREGISTERED_COVERAGE = "capability-unregistered-coverage"
GAP_UNREGISTERED_COV_OPTION = "capability-unregistered-cov-option"
GAP_MISSING_CONVENTION_MODULE = "capability-missing-convention-module"
GAP_UNPUBLISHED_CLI = "capability-unpublished-cli"

CONFLICT_IMPORT_CYCLE = "conflict-import-cycle"
CONFLICT_LAYER_VIOLATION = "conflict-layer-violation"
CONFLICT_REGISTRATION_INCONSISTENT = "conflict-declaration-registration"
CONFLICT_ENTRY_POINT_UNRESOLVABLE = "conflict-entry-point-unresolvable"
CONFLICT_ENTRY_POINT_ALIASED = "conflict-entry-point-aliased"
CONFLICT_NOT_PACKAGED = "conflict-capability-not-packaged"

DUPLICATE_MODULE_CONTENT = "duplicate-module-content"
DUPLICATE_TRIVIAL_CONTENT = "duplicate-trivial-content"
DUPLICATE_CAPABILITY_NAME = "duplicate-capability-name"
DUPLICATE_SYMBOL_SURFACE = "duplicate-symbol-surface"

OWNERSHIP_UNOWNED = "ownership-unowned"
OWNERSHIP_CONTESTED = "ownership-contested"

#: A capability pair must share at least this many public symbols *and* this Jaccard
#: overlap of their public surfaces before it is reported as a duplication signal.
_SURFACE_MIN_SHARED = 3
_SURFACE_MIN_JACCARD = 0.5

#: Ownership tokens recognised in a package docstring's first line, most specific first.
_TERMINAL_PATTERN = re.compile(r"\bTerminal[\s-]+T?(\d{1,2})\b", re.IGNORECASE)
_PROGRAMME_PATTERN = re.compile(r"\b((?:UCOS|EC\d|EC-\d)[A-Z0-9-]*-(?:EPIC|TASK)-?\d+)\b")
_EPIC_PATTERN = re.compile(r"\b((?:EPIC|TASK)-[A-Z]*-?\d+)\b")

#: Zones whose name follows the numbered constitutional convention.
_ZONE_PATTERN = re.compile(r"^\d{2}-")


@dataclass(frozen=True, slots=True)
class DiscoveryOutcome:
    """Everything the eight dimensions produced, ready for graphing and adjudication."""

    units: tuple[RepositoryUnit, ...]
    capabilities: tuple[CapabilityRecord, ...]
    reuse: tuple[ReuseAssessment, ...]
    edges: tuple[DependencyEdge, ...]
    ownership: tuple[OwnershipRecord, ...]
    results: tuple[DimensionResult, ...]

    def result_for(self, dimension: DiscoveryDimension) -> DimensionResult:
        for result in self.results:
            if result.dimension is dimension:
                return result
        return DimensionResult.create(dimension, ())


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _pass(
    code: str, dimension: DiscoveryDimension, subject: str, message: str, **details: Any
) -> Finding:
    return Finding(
        code=code,
        dimension=dimension,
        severity=Severity.BLOCKING,
        status=FindingStatus.PASS,
        subject=subject,
        message=message,
        details=details,
    )


def _fail(
    code: str,
    dimension: DiscoveryDimension,
    subject: str,
    message: str,
    severity: Severity = Severity.BLOCKING,
    **details: Any,
) -> Finding:
    return Finding(
        code=code,
        dimension=dimension,
        severity=severity,
        status=FindingStatus.FAIL,
        subject=subject,
        message=message,
        details=details,
    )


def _advisory(
    code: str, dimension: DiscoveryDimension, subject: str, message: str, **details: Any
) -> Finding:
    return _fail(code, dimension, subject, message, severity=Severity.ADVISORY, **details)


def implementation_capabilities(substrate: RepositorySubstrate) -> tuple[str, ...]:
    """Capabilities that are genuine sub-packages of a code root.

    Excludes the bare code roots themselves (``engine``, ``platform``) and the test
    packages: neither is a capability the repository offers, and treating them as such
    would manufacture false catalog omissions.
    """
    roots = set(substrate.config.code_roots)
    test_suffix = f".{substrate.config.test_dir_name}"
    return tuple(
        name
        for name in substrate.capabilities_on_disk()
        if name not in roots and not name.endswith(test_suffix)
    )


# ---------------------------------------------------------------------------
# 1. Repository Discovery
# ---------------------------------------------------------------------------
def discover_repository(
    substrate: RepositorySubstrate,
) -> tuple[tuple[RepositoryUnit, ...], DimensionResult]:
    """Enumerate every unit of the repository and prove the substrate is readable."""
    cfg = substrate.config
    dimension = DiscoveryDimension.REPOSITORY
    units: list[RepositoryUnit] = []
    findings: list[Finding] = []

    for root in cfg.code_roots:
        if not cfg.code_root_path(root).is_dir():
            continue
        modules = [m for m in substrate.source_modules() if m.root == root]
        units.append(
            RepositoryUnit(
                name=root,
                kind=UnitKind.CODE_ROOT,
                location=root,
                tracked_files=len([m for m in substrate.modules if m.root == root]),
                loc=sum(m.loc for m in modules),
                detail="declared code root",
            )
        )

    for capability in implementation_capabilities(substrate):
        modules = substrate.modules_of(capability)
        location = capability.replace(".", "/")
        units.append(
            RepositoryUnit(
                name=capability,
                kind=UnitKind.CODE_CAPABILITY,
                location=location,
                tracked_files=len(modules),
                loc=substrate.loc_of(capability),
                detail=_capability_docline(substrate, capability),
            )
        )

    for zone, count in substrate.zones.items():
        if zone in cfg.code_roots or zone == ".":
            continue
        kind = (
            UnitKind.CONSTITUTIONAL_ZONE if _ZONE_PATTERN.match(zone) else UnitKind.EVIDENCE_STORE
        )
        units.append(RepositoryUnit(name=zone, kind=kind, location=zone, tracked_files=count))

    for script, target in sorted(substrate.declarations.console_scripts.items()):
        units.append(
            RepositoryUnit(
                name=script,
                kind=UnitKind.ENTRY_POINT,
                location=target,
                detail="published console script",
            )
        )

    source_count = len(substrate.source_modules())
    if source_count:
        findings.append(
            _pass(
                SUBSTRATE_PRESENT,
                dimension,
                cfg.repository_id,
                f"{source_count} source modules readable across {len(cfg.code_roots)} code roots",
                source_modules=source_count,
                units=len(units),
            )
        )
    else:
        findings.append(
            _fail(
                SUBSTRATE_PRESENT,
                dimension,
                cfg.repository_id,
                "no readable source module found under the declared code roots",
                code_roots=list(cfg.code_roots),
            )
        )

    for module in substrate.modules:
        if not module.parsed:
            findings.append(
                _fail(
                    MODULE_UNPARSED,
                    dimension,
                    module.module,
                    "module could not be parsed; its facts cannot be trusted",
                    path=module.path,
                )
            )

    return tuple(units), DimensionResult.create(dimension, tuple(findings))


def _capability_docline(substrate: RepositorySubstrate, capability: str) -> str:
    """The capability's own package docstring first line (its self-description)."""
    for module in substrate.modules_of(capability):
        if module.module == capability:
            return module.docline
    return ""


# ---------------------------------------------------------------------------
# 2. Capability Discovery (composed from UCOS-RIE-001)
# ---------------------------------------------------------------------------
def discover_capabilities(
    substrate: RepositorySubstrate,
) -> tuple[tuple[CapabilityRecord, ...], DimensionResult]:
    """Compose the capability inventory; never re-derive capability identity or policy."""
    dimension = DiscoveryDimension.CAPABILITY
    findings: list[Finding] = []
    catalog = substrate.catalog_index()
    on_disk = implementation_capabilities(substrate)

    if substrate.catalog_source == CATALOG_SOURCE_ABSENT:
        findings.append(
            _fail(
                CATALOG_COMPOSED,
                dimension,
                substrate.config.repository_id,
                "the UCOS-RIE-001 capability catalog could neither be imported nor read; "
                "capability policy cannot be composed and is not re-derived here",
                catalog_path=substrate.config.capability_catalog,
            )
        )
    else:
        findings.append(
            _pass(
                CATALOG_COMPOSED,
                dimension,
                substrate.config.repository_id,
                f"composed {len(catalog)} capabilities from {substrate.catalog_source}",
                entries=len(catalog),
                source=substrate.catalog_source,
            )
        )

    records: list[CapabilityRecord] = []
    for name in on_disk:
        entry = catalog.get(name)
        modules = substrate.modules_of(name)
        tests = _test_modules_for(substrate, name)
        if entry is None:
            policy = _derived_policy(substrate, name)
            findings.append(
                _advisory(
                    CATALOG_OMISSION,
                    dimension,
                    name,
                    "capability exists in the code substrate but is absent from the "
                    "composed capability catalog (catalog is stale)",
                    location=name.replace(".", "/"),
                    policy_basis=policy["basis"],
                )
            )
            records.append(
                CapabilityRecord(
                    name=name,
                    location=name.replace(".", "/"),
                    category=str(policy["category"]),
                    authority=str(policy["authority"]),
                    reuse_directive=str(policy["reuse"]),
                    replacement_prohibited=bool(policy["replacement_prohibited"]),
                    implementation_status="IMPLEMENTED",
                    description=_capability_docline(substrate, name),
                    source="substrate-scan (catalog omission)",
                    modules=len(modules),
                    symbols=len(substrate.symbols_of(name)),
                    test_modules=len(tests),
                )
            )
        else:
            records.append(
                CapabilityRecord(
                    name=name,
                    location=str(entry.get("canonical_location") or name.replace(".", "/")),
                    category=str(entry.get("category", "")),
                    authority=str(entry.get("authority", "")),
                    reuse_directive=str(entry.get("reuse", "")),
                    replacement_prohibited=bool(entry.get("replacement_prohibited", False)),
                    implementation_status=str(entry.get("implementation_status", "")),
                    description=str(
                        entry.get("description") or _capability_docline(substrate, name)
                    ),
                    source=substrate.catalog_source,
                    modules=len(modules),
                    symbols=len(substrate.symbols_of(name)),
                    test_modules=len(tests),
                )
            )
        if not _capability_docline(substrate, name):
            findings.append(
                _advisory(
                    CAPABILITY_UNDOCUMENTED,
                    dimension,
                    name,
                    "capability package has no docstring, so it cannot describe itself "
                    "to discovery or declare its owner",
                )
            )

    # Catalog entries that name a code capability which is not on disk are phantoms.
    #
    # "Not on disk" is tested against the location the catalog itself declares, NOT against
    # membership of ``on_disk``. Those are different questions, and conflating them was
    # C-02. ``implementation_capabilities`` deliberately narrows the capability set — it
    # drops the bare code roots and the test packages, and says in its own docstring that
    # including them "would manufacture false catalog omissions". Comparing the catalog
    # against that narrowed set applied the exclusion in one direction only: it suppressed
    # false omissions and manufactured false PHANTOMS out of the very same entries.
    #
    # The catalog is authoritative for capability identity — this module states twice that
    # it never re-derives it — and it names capabilities at their real package depth, while
    # ``_capability_name`` attributes every module to a depth-1 owner. Both are correct for
    # their own dimension. Neither is evidence that a location is absent, which is the only
    # thing "phantom" may mean.
    disk_set = set(on_disk)
    for name, entry in sorted(catalog.items()):
        if str(entry.get("category", "")) not in substrate.config.code_roots:
            continue
        if name in disk_set:
            continue
        location = str(entry.get("canonical_location", ""))
        if substrate.location_is_populated(location):
            findings.append(
                _advisory(
                    CATALOG_GRANULARITY,
                    dimension,
                    name,
                    "catalog names a real code location the capability model does not "
                    "carry as a capability of its own; the location exists and its "
                    "modules attribute to their owning capability",
                    claimed_location=location,
                    catalog_source=substrate.catalog_source,
                )
            )
            continue
        records.append(
            CapabilityRecord(
                name=name,
                location=location,
                category=str(entry.get("category", "")),
                authority=str(entry.get("authority", "")),
                reuse_directive=str(entry.get("reuse", "")),
                replacement_prohibited=bool(entry.get("replacement_prohibited", False)),
                implementation_status=str(entry.get("implementation_status", "")),
                description=str(entry.get("description", "")),
                source=substrate.catalog_source,
                present_on_disk=False,
            )
        )

    ordered = tuple(sorted(records, key=lambda r: r.name))
    return ordered, DimensionResult.create(dimension, tuple(findings))


def _test_modules_for(substrate: RepositorySubstrate, capability: str) -> tuple[ModuleFact, ...]:
    """Test modules that import the capability (evidence the capability is exercised)."""
    return tuple(
        m
        for m in substrate.test_modules()
        if any(
            imported == capability or imported.startswith(f"{capability}.")
            for imported in m.imports
        )
    )


def _derived_policy(substrate: RepositorySubstrate, capability: str) -> dict[str, Any]:
    """Derive reuse policy for an uncatalogued capability from its own layer's catalog.

    The policy is *not invented*: it is the modal (most common, ties broken
    deterministically) policy the composed catalog already assigns to capabilities in the
    same category, so a new sub-package inherits the layer's established disposition.
    """
    root = capability.split(".", 1)[0]
    peers = [e for e in substrate.catalog if str(e.get("category")) == root]
    if not peers:
        return {
            "category": root,
            "authority": "UNDETERMINED",
            "reuse": "",
            "replacement_prohibited": False,
            "basis": "no catalogued peer in this layer",
        }
    modal = Counter(
        (
            str(e.get("authority", "")),
            str(e.get("reuse", "")),
            bool(e.get("replacement_prohibited")),
        )
        for e in peers
    )
    authority, reuse, prohibited = sorted(modal.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return {
        "category": root,
        "authority": authority,
        "reuse": reuse,
        "replacement_prohibited": prohibited,
        "basis": f"modal policy of {len(peers)} catalogued peers in category '{root}'",
    }


# ---------------------------------------------------------------------------
# 4. Dependency Discovery (runs before reuse, which consumes its edges)
# ---------------------------------------------------------------------------
def discover_dependencies(
    substrate: RepositorySubstrate,
) -> tuple[tuple[DependencyEdge, ...], DimensionResult]:
    """Derive the real capability-level import graph from the module ASTs."""
    dimension = DiscoveryDimension.DEPENDENCY
    findings: list[Finding] = []
    roots = set(substrate.config.code_roots)
    known = set(implementation_capabilities(substrate)) | roots
    module_index = substrate.module_index()

    aggregated: dict[tuple[str, str], list[str]] = {}
    for module in substrate.source_modules():
        source_capability = module.capability
        # import_time_imports, not imports: this graph decides the acyclicity rule, and a
        # cycle is a property of module *initialisation*. A TYPE_CHECKING import is erased
        # before anything resolves; a function-body import resolves on first call, once
        # every module in the loop is already initialised. Neither can deadlock an import.
        #
        # Reading `imports` here reported both recorded cycles against code that was
        # already decoupled on purpose: C-01 (certification -> validation -> runtime) had
        # two of three edges under TYPE_CHECKING, in blocks whose own comments read
        # "typing only, avoids import cycles"; and the universal_foundation ->
        # universal_measurement -> universal_ownership loop was closed by a single
        # function-local import in universal_ownership/cli.py. Deferring is the cure for a
        # circular import, so counting it as one reported the fix as the defect.
        for imported in module.import_time_imports:
            top = imported.split(".", 1)[0]
            if top not in roots:
                continue
            target = substrate.capability_of_module(imported)
            if target is None:
                if imported not in module_index and not _is_package_prefix(imported, known):
                    findings.append(
                        _fail(
                            DEPENDENCY_UNRESOLVABLE,
                            dimension,
                            f"{module.module} -> {imported}",
                            "module imports an internal target that does not exist "
                            "in the substrate",
                            importer=module.module,
                            imported=imported,
                        )
                    )
                continue
            if target == source_capability:
                continue
            aggregated.setdefault((source_capability, target), []).append(module.module)

    edges = tuple(
        DependencyEdge(
            source=source,
            target=target,
            kind=EdgeKind.IMPORTS,
            weight=len(modules),
            modules=tuple(sorted(modules)),
        )
        for (source, target), modules in sorted(aggregated.items())
    )

    # Undeclared third-party runtime dependency vs the declared dependency set.
    # A top-level import target is *first party* iff a package of that name exists at the
    # repository root; such a target is derived from the substrate, never a fixed list, so
    # an unpackaged companion root (one outside the declared, distributable code roots) is
    # reported as an architectural fact rather than mistaken for a third-party dependency.
    declared = _declared_distributions(substrate)
    stdlib = set(sys.stdlib_module_names)
    external: dict[str, list[str]] = {}
    companion: dict[str, list[str]] = {}
    for module in substrate.source_modules():
        for imported in module.imports:
            top = imported.split(".", 1)[0]
            if top in roots or top in stdlib or not top or top.startswith("_"):
                continue
            if _is_first_party(substrate, top):
                companion.setdefault(top, []).append(module.module)
            elif top not in declared:
                external.setdefault(top, []).append(module.module)
    for distribution, importers in sorted(external.items()):
        findings.append(
            _fail(
                DEPENDENCY_UNDECLARED,
                dimension,
                distribution,
                "source module imports a non-stdlib distribution that the project does "
                "not declare as a runtime dependency",
                importers=sorted(importers)[:20],
                importer_count=len(importers),
            )
        )
    for root, importers in sorted(companion.items()):
        findings.append(
            _advisory(
                DEPENDENCY_COMPANION_ROOT,
                dimension,
                root,
                "source module depends on a first-party root that is outside the declared "
                "distributable code roots, so the dependency is not carried by the package",
                importers=sorted(importers)[:20],
                importer_count=len(importers),
                declared_code_roots=sorted(roots),
            )
        )

    cycles = _cycles(edges)
    if cycles:
        # One determination here (the graph property); the conflict dimension owns the
        # per-cycle detail, so a cycle is counted once in each dimension's own terms.
        findings.append(
            _fail(
                DEPENDENCY_ACYCLIC,
                dimension,
                substrate.config.repository_id,
                f"capability dependency graph is not acyclic: {len(cycles)} cyclic "
                f"component(s) across {len(edges)} edges",
                cycle_count=len(cycles),
                components=[list(cycle) for cycle in cycles],
                edges=len(edges),
            )
        )
    else:
        findings.append(
            _pass(
                DEPENDENCY_ACYCLIC,
                dimension,
                substrate.config.repository_id,
                f"capability dependency graph is acyclic across {len(edges)} edges",
                edges=len(edges),
            )
        )

    return edges, DimensionResult.create(dimension, tuple(findings))


def _is_package_prefix(imported: str, known: set[str]) -> bool:
    """True iff ``imported`` names a package that contains known capabilities."""
    return any(name.startswith(f"{imported}.") for name in known)


def _is_first_party(substrate: RepositorySubstrate, top: str) -> bool:
    """True iff ``top`` names a Python package that lives at the repository root."""
    return (substrate.config.repository_root / top / "__init__.py").is_file()


def _declared_distributions(substrate: RepositorySubstrate) -> set[str]:
    """Top-level import names implied by the declared runtime + dev dependencies."""
    names: set[str] = set()
    for spec in (
        *substrate.declarations.runtime_dependencies,
        *substrate.declarations.dev_dependencies,
    ):
        name = re.split(r"[<>=!~\[; ]", spec, maxsplit=1)[0].strip()
        if name:
            names.add(name.replace("-", "_").lower())
    return names


def _cycles(edges: tuple[DependencyEdge, ...]) -> tuple[tuple[str, ...], ...]:
    """Cyclic components of the dependency relation.

    Delegates to :func:`platform.repository_intelligence.graph.strongly_connected_components`
    — the subsystem's single cycle detector — rather than carrying a second copy.
    """
    return strongly_connected_components(edges)


# ---------------------------------------------------------------------------
# 3. Reuse Discovery
# ---------------------------------------------------------------------------
def discover_reuse(
    substrate: RepositorySubstrate,
    capabilities: tuple[CapabilityRecord, ...],
    edges: tuple[DependencyEdge, ...],
) -> tuple[tuple[ReuseAssessment, ...], DimensionResult]:
    """Assess, from evidence, whether each existing capability is actually reused."""
    dimension = DiscoveryDimension.REUSE
    findings: list[Finding] = []
    importers: dict[str, set[str]] = {}
    for edge in edges:
        if edge.kind is EdgeKind.IMPORTS:
            importers.setdefault(edge.target, set()).add(edge.source)

    entry_points: dict[str, set[str]] = {}
    for script, target in substrate.declarations.console_scripts.items():
        module = target.split(":", 1)[0]
        capability = substrate.capability_of_module(module)
        if capability:
            entry_points.setdefault(capability, set()).add(script)

    assessments: list[ReuseAssessment] = []
    for record in capabilities:
        if not record.present_on_disk:
            continue
        consumers = tuple(sorted(importers.get(record.name, set())))
        published = tuple(sorted(entry_points.get(record.name, set())))
        if consumers:
            proof = ReuseProof.PROVEN
        elif published:
            proof = ReuseProof.ENTRY_POINT
        else:
            proof = ReuseProof.UNPROVEN
        assessments.append(
            ReuseAssessment(
                capability=record.name,
                reuse_directive=record.reuse_directive,
                replacement_prohibited=record.replacement_prohibited,
                proof=proof,
                importers=consumers,
                published_entry_points=published,
            )
        )
        if not record.reuse_directive:
            findings.append(
                _fail(
                    REUSE_DIRECTIVE_MISSING,
                    dimension,
                    record.name,
                    "capability carries no reuse directive, so reuse-over-reinvention "
                    "cannot be adjudicated for it",
                    category=record.category,
                )
            )
        if proof is ReuseProof.UNPROVEN:
            findings.append(
                _advisory(
                    REUSE_UNPROVEN,
                    dimension,
                    record.name,
                    "capability is imported by no other capability and publishes no "
                    "console script; its reuse is unproven",
                    reuse_directive=record.reuse_directive,
                    replacement_prohibited=record.replacement_prohibited,
                )
            )
    return tuple(assessments), DimensionResult.create(dimension, tuple(findings))


# ---------------------------------------------------------------------------
# 5. Gap Discovery
# ---------------------------------------------------------------------------
def discover_gaps(
    substrate: RepositorySubstrate,
    capabilities: tuple[CapabilityRecord, ...],
) -> DimensionResult:
    """Find what the code and declaration substrate is *missing* (incompleteness)."""
    dimension = DiscoveryDimension.GAP
    findings: list[Finding] = []
    declarations = substrate.declarations
    coverage_sources = set(declarations.coverage_sources)
    cov_packages = set(declarations.pytest_cov_packages)
    scripts_by_module = {
        target.split(":", 1)[0] for target in declarations.console_scripts.values()
    }
    present = [r for r in capabilities if r.present_on_disk]

    for record in present:
        path_form = record.name.replace(".", "/")
        if declarations.available and path_form not in coverage_sources:
            findings.append(
                _advisory(
                    GAP_UNREGISTERED_COVERAGE,
                    dimension,
                    record.name,
                    "capability is not registered in the coverage source list, so the "
                    "repository coverage gate does not measure it",
                    expected_entry=path_form,
                )
            )
        if declarations.available and record.name not in cov_packages:
            findings.append(
                _advisory(
                    GAP_UNREGISTERED_COV_OPTION,
                    dimension,
                    record.name,
                    "capability is not registered as a pytest --cov target",
                    expected_option=f"--cov={record.name}",
                )
            )
        if not record.test_modules:
            findings.append(
                _advisory(
                    GAP_UNTESTED,
                    dimension,
                    record.name,
                    "no test module imports this capability",
                    modules=record.modules,
                )
            )
        if (
            f"{record.name}.cli" in substrate.module_index()
            and f"{record.name}.cli" not in scripts_by_module
        ):
            findings.append(
                _advisory(
                    GAP_UNPUBLISHED_CLI,
                    dimension,
                    record.name,
                    "capability provides a cli module that no console script publishes",
                    module=f"{record.name}.cli",
                )
            )

    findings.extend(_convention_gaps(substrate, present, dimension))
    return DimensionResult.create(dimension, tuple(findings))


def _convention_gaps(
    substrate: RepositorySubstrate,
    capabilities: list[CapabilityRecord],
    dimension: DiscoveryDimension,
) -> list[Finding]:
    """Report a convention module absent from a capability whose peers overwhelmingly have it.

    The expectation is *derived from the repository itself* — a module basename becomes
    expected only once more than :attr:`convention_threshold` of the peer capabilities in
    the same code root declare it — so the check adapts to the repository's own evolving
    conventions instead of encoding a fixed list.
    """
    findings: list[Finding] = []
    threshold = substrate.config.convention_threshold
    by_root: dict[str, list[CapabilityRecord]] = {}
    for record in capabilities:
        by_root.setdefault(record.name.split(".", 1)[0], []).append(record)

    for root, peers in sorted(by_root.items()):
        if len(peers) < 2:
            continue
        basenames: dict[str, set[str]] = {}
        for peer in peers:
            for module in substrate.modules_of(peer.name):
                basenames.setdefault(module.basename, set()).add(peer.name)
        expected = {
            basename
            for basename, owners in basenames.items()
            if basename in substrate.config.convention_modules
            and len(owners) / len(peers) > threshold
        }
        for peer in peers:
            have = {m.basename for m in substrate.modules_of(peer.name)}
            for basename in sorted(expected - have):
                findings.append(
                    _advisory(
                        GAP_MISSING_CONVENTION_MODULE,
                        dimension,
                        f"{peer.name}.{basename}",
                        f"'{basename}' is an established convention in '{root}' "
                        f"(present in >{int(threshold * 100)}% of peers) but is absent here",
                        capability=peer.name,
                        module=basename,
                        peers=len(peers),
                    )
                )
    return findings


# ---------------------------------------------------------------------------
# 6. Conflict Discovery
# ---------------------------------------------------------------------------
def discover_conflicts(
    substrate: RepositorySubstrate,
    capabilities: tuple[CapabilityRecord, ...],
    edges: tuple[DependencyEdge, ...],
) -> DimensionResult:
    """Find where the repository contradicts itself (declarations vs code vs layering)."""
    dimension = DiscoveryDimension.CONFLICT
    findings: list[Finding] = []
    declarations = substrate.declarations
    module_index = substrate.module_index()
    roots = list(substrate.config.code_roots)

    # Layer violations: an earlier-declared root must not depend on a later one.
    order = {root: position for position, root in enumerate(roots)}
    for edge in edges:
        source_root = edge.source.split(".", 1)[0]
        target_root = edge.target.split(".", 1)[0]
        if (
            source_root in order
            and target_root in order
            and order[source_root] < order[target_root]
        ):
            findings.append(
                _fail(
                    CONFLICT_LAYER_VIOLATION,
                    dimension,
                    f"{edge.source} -> {edge.target}",
                    f"'{source_root}' is declared below '{target_root}' yet depends upon it",
                    modules=list(edge.modules)[:20],
                    weight=edge.weight,
                )
            )

    for cycle in _cycles(edges):
        findings.append(
            _fail(
                CONFLICT_IMPORT_CYCLE,
                dimension,
                " -> ".join(cycle),
                "capabilities are mutually dependent, so neither can be reused "
                "independently of the others",
                cycle=list(cycle),
                interface="see the dependency dimension for the acyclicity determination",
            )
        )

    # Declaration/registration inconsistency: registered in one gate but not the other.
    coverage_sources = set(declarations.coverage_sources)
    cov_packages = set(declarations.pytest_cov_packages)
    if declarations.available:
        for record in capabilities:
            if not record.present_on_disk:
                continue
            path_form = record.name.replace(".", "/")
            in_source = path_form in coverage_sources
            in_option = record.name in cov_packages
            if in_source != in_option:
                findings.append(
                    _fail(
                        CONFLICT_REGISTRATION_INCONSISTENT,
                        dimension,
                        record.name,
                        "capability is registered in one coverage gate but not the other, "
                        "so the two declarations contradict each other",
                        in_coverage_source=in_source,
                        in_pytest_cov=in_option,
                    )
                )

    # Console scripts must resolve to a module that exists.
    targets: dict[str, list[str]] = {}
    for script, target in sorted(declarations.console_scripts.items()):
        module = target.split(":", 1)[0]
        targets.setdefault(target, []).append(script)
        if module.split(".", 1)[0] in roots and module not in module_index:
            findings.append(
                _fail(
                    CONFLICT_ENTRY_POINT_UNRESOLVABLE,
                    dimension,
                    script,
                    "published console script names a module that does not exist",
                    target=target,
                )
            )
    for target, scripts in sorted(targets.items()):
        if len(scripts) > 1:
            findings.append(
                _advisory(
                    CONFLICT_ENTRY_POINT_ALIASED,
                    dimension,
                    target,
                    "more than one console script resolves to the same entry point",
                    scripts=sorted(scripts),
                )
            )

    # Catalog phantoms: the composed catalog claims a location that is not on disk.
    for record in capabilities:
        if record.present_on_disk:
            continue
        findings.append(
            _fail(
                CATALOG_PHANTOM,
                dimension,
                record.name,
                "the composed capability catalog records a code capability that does not "
                "exist in the substrate",
                claimed_location=record.location,
                catalog_source=record.source,
            )
        )

    # Packaging: a capability's root must be matched by the declared package includes.
    if declarations.available and declarations.packaged_includes:
        for root in roots:
            if not any(
                _include_matches(pattern, root) for pattern in declarations.packaged_includes
            ):
                findings.append(
                    _advisory(
                        CONFLICT_NOT_PACKAGED,
                        dimension,
                        root,
                        "declared code root is not matched by any package include pattern, "
                        "so its capabilities are not distributed",
                        includes=list(declarations.packaged_includes),
                    )
                )
    return DimensionResult.create(dimension, tuple(findings))


def _include_matches(pattern: str, root: str) -> bool:
    """Match a setuptools ``packages.find`` include pattern against a root name."""
    if pattern.endswith("*"):
        return root.startswith(pattern[:-1])
    return pattern == root


# ---------------------------------------------------------------------------
# 7. Duplicate Detection
# ---------------------------------------------------------------------------
def detect_duplicates(substrate: RepositorySubstrate) -> DimensionResult:
    """Detect duplication in the substrate and *classify* it rather than merely flag it.

    Three independent detectors, because duplication hides in three different places:
    byte-identical files, repeated capability names across layers, and — the one that
    actually matters for "never duplicate capabilities" — capability pairs whose public
    symbol surfaces substantially overlap.
    """
    dimension = DiscoveryDimension.DUPLICATE
    findings: list[Finding] = []
    minimum_loc = substrate.config.duplicate_min_loc

    by_hash: dict[str, list[ModuleFact]] = {}
    for module in substrate.source_modules():
        by_hash.setdefault(module.content_sha256, []).append(module)
    for digest, group in sorted(by_hash.items()):
        if len(group) < 2:
            continue
        paths = sorted(m.path for m in group)
        loc = max(m.loc for m in group)
        if loc >= minimum_loc:
            findings.append(
                _fail(
                    DUPLICATE_MODULE_CONTENT,
                    dimension,
                    paths[0],
                    f"{len(group)} modules are byte-identical; at most one can be canonical",
                    content_sha256=digest,
                    paths=paths,
                    loc=loc,
                )
            )
        else:
            findings.append(
                _advisory(
                    DUPLICATE_TRIVIAL_CONTENT,
                    dimension,
                    paths[0],
                    f"{len(group)} modules are byte-identical but trivial "
                    f"(<{minimum_loc} lines); treated as convention, not duplication",
                    content_sha256=digest,
                    paths=paths,
                    loc=loc,
                )
            )

    by_short_name: dict[str, list[str]] = {}
    for capability in implementation_capabilities(substrate):
        by_short_name.setdefault(capability.rsplit(".", 1)[-1], []).append(capability)
    for short, names in sorted(by_short_name.items()):
        if len(names) < 2:
            continue
        overlap = _surface_overlap(substrate, names)
        findings.append(
            _advisory(
                DUPLICATE_CAPABILITY_NAME,
                dimension,
                short,
                "the same capability name exists in more than one code root",
                locations=sorted(names),
                assessment=(
                    "SUSPECT — layered pair also shares a public surface"
                    if overlap["jaccard"] >= _SURFACE_MIN_JACCARD
                    else "INTENTIONAL — layered pair with distinct public surfaces"
                ),
                shared_symbols=overlap["shared"],
                surface_jaccard=overlap["jaccard"],
            )
        )

    findings.extend(_surface_duplicates(substrate, dimension))
    return DimensionResult.create(dimension, tuple(findings))


def _surface_overlap(substrate: RepositorySubstrate, names: list[str]) -> dict[str, Any]:
    """Public-symbol overlap across a set of capabilities (Jaccard + shared names)."""
    surfaces = [set(substrate.symbols_of(name)) for name in sorted(names)]
    shared = set.intersection(*surfaces) if surfaces else set()
    union = set.union(*surfaces) if surfaces else set()
    return {
        "shared": sorted(shared)[:20],
        "shared_count": len(shared),
        "jaccard": round(len(shared) / len(union), 4) if union else 0.0,
    }


def _surface_duplicates(
    substrate: RepositorySubstrate, dimension: DiscoveryDimension
) -> list[Finding]:
    """Capability pairs whose public surfaces overlap enough to signal duplicated capability."""
    findings: list[Finding] = []
    surfaces = {
        name: set(substrate.symbols_of(name)) for name in implementation_capabilities(substrate)
    }
    names = sorted(n for n, surface in surfaces.items() if surface)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            shared = surfaces[left] & surfaces[right]
            union = surfaces[left] | surfaces[right]
            jaccard = len(shared) / len(union) if union else 0.0
            if len(shared) >= _SURFACE_MIN_SHARED and jaccard >= _SURFACE_MIN_JACCARD:
                findings.append(
                    _advisory(
                        DUPLICATE_SYMBOL_SURFACE,
                        dimension,
                        f"{left} ~ {right}",
                        "two capabilities expose substantially the same public surface; "
                        "one of them is a candidate duplicate to be composed away",
                        left=left,
                        right=right,
                        shared_symbols=sorted(shared)[:20],
                        shared_count=len(shared),
                        surface_jaccard=round(jaccard, 4),
                    )
                )
    return findings


# ---------------------------------------------------------------------------
# 8. Ownership Discovery
# ---------------------------------------------------------------------------
def discover_ownership(
    substrate: RepositorySubstrate,
    units: tuple[RepositoryUnit, ...],
    capabilities: tuple[CapabilityRecord, ...],
) -> tuple[tuple[OwnershipRecord, ...], DimensionResult]:
    """Derive each capability's owner from the substrate, with an explicit basis.

    Precedence, strongest evidence first: a declared *terminal* in the capability's own
    docstrings, then a declared *programme* identifier, then the layer authority the
    composed catalog assigns. A capability whose modules declare two different terminals
    is reported as contested rather than silently resolved to one of them.
    """
    dimension = DiscoveryDimension.OWNERSHIP
    findings: list[Finding] = []
    records: list[OwnershipRecord] = []
    by_name = {record.name: record for record in capabilities}

    for unit in units:
        if unit.kind is not UnitKind.CODE_CAPABILITY:
            continue
        terminals, programmes = _declared_owners(substrate, unit.name)
        record = by_name.get(unit.name)
        if terminals:
            owner = terminals[0]
            basis = "declared terminal in package docstrings"
            confidence = "high" if len(terminals) == 1 else "contested"
            candidates = terminals
        elif programmes:
            owner = programmes[0]
            basis = "declared programme identifier in package docstrings"
            confidence = "medium"
            candidates = programmes
        elif record and record.authority and record.authority != "UNDETERMINED":
            owner = record.authority
            basis = "layer authority from the composed capability catalog"
            confidence = "low"
            candidates = (record.authority,)
        else:
            owner = OwnershipRecord.UNOWNED
            basis = "no owner declared and no layer authority available"
            confidence = "none"
            candidates = ()
        ownership = OwnershipRecord(
            subject=unit.name,
            owner=owner,
            basis=basis,
            confidence=confidence,
            candidates=candidates,
        )
        records.append(ownership)
        if not ownership.owned:
            findings.append(
                _advisory(
                    OWNERSHIP_UNOWNED,
                    dimension,
                    unit.name,
                    "capability has no derivable owner",
                    location=unit.location,
                )
            )
        elif ownership.contested and confidence == "contested":
            findings.append(
                _fail(
                    OWNERSHIP_CONTESTED,
                    dimension,
                    unit.name,
                    "capability declares more than one owning terminal, so ownership is ambiguous",
                    candidates=list(candidates),
                )
            )
    return tuple(records), DimensionResult.create(dimension, tuple(findings))


def _declared_owners(
    substrate: RepositorySubstrate, capability: str
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Terminal and programme owner tokens declared in a capability's module doclines."""
    terminals: set[str] = set()
    programmes: set[str] = set()
    for module in substrate.modules_of(capability):
        text = module.docline
        if not text:
            continue
        for match in _TERMINAL_PATTERN.finditer(text):
            terminals.add(f"Terminal T{int(match.group(1))}")
        for pattern in (_PROGRAMME_PATTERN, _EPIC_PATTERN):
            for match in pattern.finditer(text):
                programmes.add(match.group(1))
    return tuple(sorted(terminals)), tuple(sorted(programmes))


# ---------------------------------------------------------------------------
# orchestration
# ---------------------------------------------------------------------------
def discover_all(substrate: RepositorySubstrate) -> DiscoveryOutcome:
    """Run all eight dimensions in dependency order and return the complete outcome."""
    units, repository_result = discover_repository(substrate)
    capabilities, capability_result = discover_capabilities(substrate)
    edges, dependency_result = discover_dependencies(substrate)
    reuse, reuse_result = discover_reuse(substrate, capabilities, edges)
    gap_result = discover_gaps(substrate, capabilities)
    conflict_result = discover_conflicts(substrate, capabilities, edges)
    duplicate_result = detect_duplicates(substrate)
    ownership, ownership_result = discover_ownership(substrate, units, capabilities)
    return DiscoveryOutcome(
        units=units,
        capabilities=capabilities,
        reuse=reuse,
        edges=edges,
        ownership=ownership,
        results=(
            repository_result,
            capability_result,
            reuse_result,
            dependency_result,
            gap_result,
            conflict_result,
            duplicate_result,
            ownership_result,
        ),
    )


def dimension_summary(outcome: DiscoveryOutcome) -> dict[str, Mapping[str, Any]]:
    """A compact, deterministic per-dimension summary (for dashboards and the CLI)."""
    return {
        result.dimension.value: {
            "verdict": result.verdict.value,
            **result.counts(),
        }
        for result in outcome.results
    }


__all__ = [
    "DiscoveryOutcome",
    "implementation_capabilities",
    "discover_repository",
    "discover_capabilities",
    "discover_reuse",
    "discover_dependencies",
    "discover_gaps",
    "discover_conflicts",
    "detect_duplicates",
    "discover_ownership",
    "discover_all",
    "dimension_summary",
]
