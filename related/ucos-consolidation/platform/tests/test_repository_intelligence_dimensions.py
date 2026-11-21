"""UCOS-EPIC-014 — the eight discovery dimensions driven over a SYNTHETIC substrate.

WHY THIS MODULE EXISTS, STATED AS THE MEASUREMENT THAT PRODUCED IT. Every existing suite
runs the dimensions over THIS repository, which is a repository that mostly satisfies
them: the catalog composes, the graph is acyclic, no module fails to parse, no two modules
are byte-identical, no console script dangles and no capability declares two owners. So
the PASS arm of each dimension was measured and the FAIL and ADVISORY arms — which are the
entire product of a discovery engine — were not. A detector observed only over a substrate
that gives it nothing to detect is indistinguishable from one that detects nothing.

Every substrate below is BUILT rather than scanned. That is the point twice over: it is
the only way to present the engine with a repository that contradicts itself, and it is
what makes these tests a statement about the DIMENSIONS rather than about the state this
repository happens to be in on the day they run.
"""

from __future__ import annotations

from pathlib import Path
from platform.repository_intelligence import discovery, recommendation
from platform.repository_intelligence.config import RepositoryIntelligenceConfig
from platform.repository_intelligence.contracts import (
    DependencyEdge,
    DimensionResult,
    DiscoveryDimension,
    EdgeKind,
    Finding,
    FindingStatus,
    RecommendationAction,
    RepositoryIntelligenceReport,
    Severity,
    UnitKind,
    Verdict,
)
from platform.repository_intelligence.errors import DiscoveryError, GraphError, RecommendationError
from platform.repository_intelligence.graph import GraphNode, RepositoryGraph, build_graph
from platform.repository_intelligence.recommendation import (
    PRIORITY_NONE,
    RepositoryRecommendationEngine,
)
from platform.repository_intelligence.substrate import (
    CATALOG_SOURCE_ABSENT,
    Declarations,
    ModuleFact,
    RepositorySubstrate,
)
from platform.repository_intelligence.validation import RepositoryValidator

import pytest

CATALOG_SOURCE = "test-catalog"


def _config(tmp_path: Path, **overrides) -> RepositoryIntelligenceConfig:
    fields = {
        "repository_root": tmp_path,
        "repository_id": "synthetic",
        "code_roots": ("engine", "platform"),
    }
    fields.update(overrides)
    return RepositoryIntelligenceConfig(**fields)


def _module(
    module: str,
    *,
    capability: str | None = None,
    loc: int = 40,
    content: str | None = None,
    imports: tuple[str, ...] = (),
    import_time: tuple[str, ...] | None = None,
    symbols: tuple[str, ...] = (),
    docline: str = "A capability that describes itself.",
    is_test: bool = False,
    parsed: bool = True,
) -> ModuleFact:
    parts = module.split(".")
    return ModuleFact(
        module=module,
        capability=capability if capability is not None else ".".join(parts[:2]),
        root=parts[0],
        path=module.replace(".", "/") + ".py",
        loc=loc,
        content_sha256=content if content is not None else f"sha-{module}",
        imports=imports,
        import_time_imports=imports if import_time is None else import_time,
        symbols=symbols,
        docline=docline,
        is_test=is_test,
        parsed=parsed,
    )


def _substrate(
    tmp_path: Path,
    modules: tuple[ModuleFact, ...],
    *,
    zones: dict[str, int] | None = None,
    declarations: Declarations | None = None,
    catalog: tuple[dict, ...] = (),
    catalog_source: str = CATALOG_SOURCE,
    config: RepositoryIntelligenceConfig | None = None,
) -> RepositorySubstrate:
    return RepositorySubstrate(
        config=config or _config(tmp_path),
        modules=tuple(sorted(modules, key=lambda m: m.module)),
        zones=zones or {},
        declarations=declarations or Declarations(available=False),
        catalog=catalog,
        catalog_source=catalog_source,
    )


def _codes(result) -> list[str]:
    return sorted(f.code for f in result.findings)


def _finding(result, code: str):
    for item in result.findings:
        if item.code == code:
            return item
    raise AssertionError(f"{code!r} not among {_codes(result)}")


# -- 1. repository ---------------------------------------------------------------------


def test_a_readable_substrate_reports_its_units_and_passes(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.alpha"),
            _module("engine.alpha.contracts"),
            _module("platform.tests.test_alpha", capability="platform.tests", is_test=True),
        ),
        zones={"00-BOOK": 12, "evidence": 3, ".": 1, "engine": 2},
        declarations=Declarations(
            available=True, console_scripts={"ucos-alpha": "engine.alpha:main"}
        ),
    )
    units, result = discovery.discover_repository(substrate)
    kinds = {unit.kind for unit in units}
    assert UnitKind.CODE_CAPABILITY in kinds
    assert UnitKind.ENTRY_POINT in kinds
    assert UnitKind.CONSTITUTIONAL_ZONE in kinds  # 00-BOOK matches the numbered convention
    assert UnitKind.EVIDENCE_STORE in kinds  # 'evidence' does not
    assert {u.name for u in units if u.kind is UnitKind.CONSTITUTIONAL_ZONE} == {"00-BOOK"}
    assert _finding(result, discovery.SUBSTRATE_PRESENT).status is FindingStatus.PASS
    # the declared code roots do not exist under tmp_path, so no CODE_ROOT unit is emitted
    assert UnitKind.CODE_ROOT not in kinds


def test_a_declared_code_root_that_exists_becomes_a_unit(tmp_path):
    (tmp_path / "engine").mkdir()
    substrate = _substrate(tmp_path, (_module("engine.alpha"),))
    units, _result = discovery.discover_repository(substrate)
    roots = [u for u in units if u.kind is UnitKind.CODE_ROOT]
    assert [u.name for u in roots] == ["engine"]
    assert roots[0].tracked_files == 1


def test_a_substrate_with_no_readable_source_module_fails_closed(tmp_path):
    substrate = _substrate(
        tmp_path, (_module("platform.tests.test_alpha", capability="platform.tests", is_test=True),)
    )
    _units, result = discovery.discover_repository(substrate)
    assert _finding(result, discovery.SUBSTRATE_PRESENT).status is FindingStatus.FAIL


def test_a_module_that_could_not_be_parsed_is_reported(tmp_path):
    substrate = _substrate(
        tmp_path, (_module("engine.alpha"), _module("engine.alpha.broken", parsed=False))
    )
    _units, result = discovery.discover_repository(substrate)
    finding = _finding(result, discovery.MODULE_UNPARSED)
    assert finding.subject == "engine.alpha.broken"
    assert finding.severity is Severity.BLOCKING


def test_the_code_roots_themselves_are_not_capabilities(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine", capability="engine"),
            _module("engine.alpha"),
            _module("platform.tests.test_alpha", capability="platform.tests", is_test=True),
        ),
    )
    assert discovery.implementation_capabilities(substrate) == ("engine.alpha",)


# -- 2. capabilities -------------------------------------------------------------------


def test_an_absent_catalog_fails_rather_than_re_deriving_capability_policy(tmp_path):
    substrate = _substrate(
        tmp_path, (_module("engine.alpha"),), catalog_source=CATALOG_SOURCE_ABSENT
    )
    _records, result = discovery.discover_capabilities(substrate)
    assert _finding(result, discovery.CATALOG_COMPOSED).status is FindingStatus.FAIL


def test_a_capability_absent_from_the_catalog_inherits_its_layer_s_modal_policy(tmp_path):
    catalog = (
        {
            "canonical_name": "engine.beta",
            "category": "engine",
            "authority": "OWNER-A",
            "reuse": "REUSE",
            "replacement_prohibited": True,
            "canonical_location": "engine/beta",
            "implementation_status": "IMPLEMENTED",
        },
        {
            "canonical_name": "engine.gamma",
            "category": "engine",
            "authority": "OWNER-A",
            "reuse": "REUSE",
            "replacement_prohibited": True,
            "canonical_location": "engine/gamma",
            "implementation_status": "IMPLEMENTED",
        },
    )
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"), _module("engine.beta"), _module("engine.gamma")),
        catalog=catalog,
    )
    records, result = discovery.discover_capabilities(substrate)
    omission = _finding(result, discovery.CATALOG_OMISSION)
    assert omission.subject == "engine.alpha"
    assert omission.severity is Severity.ADVISORY
    assert "modal policy of 2 catalogued peers" in omission.details["policy_basis"]
    alpha = next(r for r in records if r.name == "engine.alpha")
    assert alpha.authority == "OWNER-A"
    assert alpha.replacement_prohibited is True
    assert alpha.source == "substrate-scan (catalog omission)"


def test_the_first_capability_in_a_layer_inherits_nothing_and_says_so(tmp_path):
    substrate = _substrate(tmp_path, (_module("engine.alpha"),), catalog=())
    records, _result = discovery.discover_capabilities(substrate)
    alpha = next(r for r in records if r.name == "engine.alpha")
    assert alpha.authority == "UNDETERMINED"
    assert alpha.reuse_directive == ""


def test_a_capability_package_with_no_docstring_is_reported(tmp_path):
    substrate = _substrate(tmp_path, (_module("engine.alpha", docline=""),))
    _records, result = discovery.discover_capabilities(substrate)
    assert _finding(result, discovery.CAPABILITY_UNDOCUMENTED).subject == "engine.alpha"


def test_a_catalog_entry_naming_a_populated_location_is_granularity_not_a_phantom(tmp_path):
    catalog = (
        {
            "canonical_name": "engine.alpha.nested",
            "category": "engine",
            "canonical_location": "engine/alpha/nested",
            "authority": "A",
            "reuse": "R",
        },
    )
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"), _module("engine.alpha.nested.core", capability="engine.alpha")),
        catalog=catalog,
    )
    records, result = discovery.discover_capabilities(substrate)
    finding = _finding(result, discovery.CATALOG_GRANULARITY)
    assert finding.details["claimed_location"] == "engine/alpha/nested"
    assert all(record.present_on_disk for record in records)


def test_a_catalog_entry_naming_a_location_that_is_absent_becomes_a_phantom_record(tmp_path):
    catalog = (
        {
            "canonical_name": "engine.ghost",
            "category": "engine",
            "canonical_location": "engine/ghost",
            "authority": "A",
            "reuse": "R",
        },
    )
    substrate = _substrate(tmp_path, (_module("engine.alpha"),), catalog=catalog)
    records, result = discovery.discover_capabilities(substrate)
    ghost = next(r for r in records if r.name == "engine.ghost")
    assert ghost.present_on_disk is False
    assert discovery.CATALOG_GRANULARITY not in _codes(result)


def test_a_catalog_entry_outside_the_declared_code_roots_is_ignored(tmp_path):
    catalog = ({"canonical_name": "corpus.thing", "category": "corpus"},)
    substrate = _substrate(tmp_path, (_module("engine.alpha"),), catalog=catalog)
    records, _result = discovery.discover_capabilities(substrate)
    assert [r.name for r in records] == ["engine.alpha"]


# -- 4. dependencies -------------------------------------------------------------------


def test_an_internal_import_that_resolves_to_nothing_is_a_blocking_finding(tmp_path):
    substrate = _substrate(tmp_path, (_module("engine.alpha", imports=("engine.nowhere.at_all",)),))
    _edges, result = discovery.discover_dependencies(substrate)
    finding = _finding(result, discovery.DEPENDENCY_UNRESOLVABLE)
    assert finding.details["imported"] == "engine.nowhere.at_all"
    assert finding.severity is Severity.BLOCKING


def test_an_import_of_a_package_prefix_that_contains_capabilities_resolves(tmp_path):
    substrate = _substrate(tmp_path, (_module("engine.alpha", imports=("engine",)),))
    _edges, result = discovery.discover_dependencies(substrate)
    assert discovery.DEPENDENCY_UNRESOLVABLE not in _codes(result)


def test_a_deferred_import_does_not_create_an_edge_and_cannot_close_a_cycle(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.alpha", imports=("platform.beta",), import_time=()),
            _module("platform.beta", imports=("engine.alpha",)),
        ),
    )
    edges, result = discovery.discover_dependencies(substrate)
    assert [(e.source, e.target) for e in edges] == [("platform.beta", "engine.alpha")]
    assert _finding(result, discovery.DEPENDENCY_ACYCLIC).status is FindingStatus.PASS


def test_a_real_import_cycle_is_refused_by_the_acyclicity_determination(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.alpha", imports=("engine.beta",)),
            _module("engine.beta", imports=("engine.alpha",)),
        ),
    )
    _edges, result = discovery.discover_dependencies(substrate)
    finding = _finding(result, discovery.DEPENDENCY_ACYCLIC)
    assert finding.status is FindingStatus.FAIL
    assert finding.details["cycle_count"] == 1


def test_an_undeclared_third_party_distribution_is_reported(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha", imports=("some_vendor_lib",)),),
        declarations=Declarations(available=True, runtime_dependencies=("other-lib==1.0",)),
    )
    _edges, result = discovery.discover_dependencies(substrate)
    finding = _finding(result, discovery.DEPENDENCY_UNDECLARED)
    assert finding.subject == "some_vendor_lib"
    assert finding.details["importer_count"] == 1


def test_a_declared_distribution_is_not_reported_however_its_name_is_spelled(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha", imports=("some_vendor_lib",)),),
        declarations=Declarations(available=True, dev_dependencies=("Some-Vendor-Lib>=1.0",)),
    )
    _edges, result = discovery.discover_dependencies(substrate)
    assert discovery.DEPENDENCY_UNDECLARED not in _codes(result)


def test_a_first_party_root_outside_the_distributable_roots_is_an_architectural_fact(tmp_path):
    companion = tmp_path / "companion"
    companion.mkdir()
    (companion / "__init__.py").write_text("", encoding="utf-8")
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha", imports=("companion.thing",)),),
        declarations=Declarations(available=True),
    )
    _edges, result = discovery.discover_dependencies(substrate)
    finding = _finding(result, discovery.DEPENDENCY_COMPANION_ROOT)
    assert finding.subject == "companion"
    assert finding.severity is Severity.ADVISORY


def test_a_stdlib_import_is_neither_undeclared_nor_a_companion_root(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha", imports=("json", "os.path", "_private")),),
        declarations=Declarations(available=True),
    )
    _edges, result = discovery.discover_dependencies(substrate)
    assert discovery.DEPENDENCY_UNDECLARED not in _codes(result)
    assert discovery.DEPENDENCY_COMPANION_ROOT not in _codes(result)


def test_an_intra_capability_import_creates_no_edge(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.alpha", imports=("engine.alpha.contracts",)),
            _module("engine.alpha.contracts"),
        ),
    )
    edges, _result = discovery.discover_dependencies(substrate)
    assert edges == ()


# -- 3. reuse --------------------------------------------------------------------------


def test_a_capability_nothing_imports_and_nothing_publishes_is_unproven(tmp_path):
    substrate = _substrate(tmp_path, (_module("engine.alpha"),))
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    assessments, result = discovery.discover_reuse(substrate, records, edges)
    assert [a.proof.value for a in assessments] == ["unproven"]
    assert discovery.REUSE_UNPROVEN in _codes(result)
    assert discovery.REUSE_DIRECTIVE_MISSING in _codes(result)


def test_a_console_script_is_reuse_evidence_when_nothing_imports_the_capability(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"),),
        declarations=Declarations(
            available=True, console_scripts={"ucos-alpha": "engine.alpha.cli:main"}
        ),
        catalog=(
            {
                "canonical_name": "engine.alpha",
                "category": "engine",
                "reuse": "REUSE",
                "authority": "A",
                "canonical_location": "engine/alpha",
            },
        ),
    )
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    assessments, result = discovery.discover_reuse(substrate, records, edges)
    assert [a.proof.value for a in assessments] == ["entry_point"]
    assert assessments[0].published_entry_points == ("ucos-alpha",)
    assert discovery.REUSE_UNPROVEN not in _codes(result)
    assert discovery.REUSE_DIRECTIVE_MISSING not in _codes(result)


def test_an_importer_proves_reuse(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"), _module("platform.beta", imports=("engine.alpha",))),
        catalog=(
            {
                "canonical_name": "engine.alpha",
                "category": "engine",
                "reuse": "REUSE",
                "authority": "A",
                "canonical_location": "engine/alpha",
            },
            {
                "canonical_name": "platform.beta",
                "category": "platform",
                "reuse": "REUSE",
                "authority": "A",
                "canonical_location": "platform/beta",
            },
        ),
    )
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    assessments, _result = discovery.discover_reuse(substrate, records, edges)
    proven = {a.capability: a.proof.value for a in assessments}
    assert proven["engine.alpha"] == "proven"


def test_a_phantom_capability_is_not_assessed_for_reuse(tmp_path):
    catalog = (
        {
            "canonical_name": "engine.ghost",
            "category": "engine",
            "canonical_location": "engine/ghost",
            "reuse": "R",
            "authority": "A",
        },
    )
    substrate = _substrate(tmp_path, (_module("engine.alpha"),), catalog=catalog)
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    assessments, _result = discovery.discover_reuse(substrate, records, edges)
    assert "engine.ghost" not in {a.capability for a in assessments}


# -- 5. gaps ---------------------------------------------------------------------------


def test_an_unregistered_untested_capability_reports_every_gap_it_has(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"), _module("engine.alpha.cli", capability="engine.alpha")),
        declarations=Declarations(available=True),
    )
    records, _ = discovery.discover_capabilities(substrate)
    result = discovery.discover_gaps(substrate, records)
    assert discovery.GAP_UNREGISTERED_COVERAGE in _codes(result)
    assert discovery.GAP_UNREGISTERED_COV_OPTION in _codes(result)
    assert discovery.GAP_UNTESTED in _codes(result)
    assert discovery.GAP_UNPUBLISHED_CLI in _codes(result)
    assert all(f.severity is Severity.ADVISORY for f in result.findings)


def test_a_fully_registered_tested_and_published_capability_reports_no_gap(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.alpha"),
            _module("engine.alpha.cli", capability="engine.alpha"),
            _module(
                "platform.tests.test_alpha",
                capability="platform.tests",
                is_test=True,
                imports=("engine.alpha",),
            ),
        ),
        declarations=Declarations(
            available=True,
            coverage_sources=("engine/alpha",),
            pytest_cov_packages=("engine.alpha",),
            console_scripts={"ucos-alpha": "engine.alpha.cli:main"},
        ),
    )
    records, _ = discovery.discover_capabilities(substrate)
    result = discovery.discover_gaps(substrate, records)
    assert discovery.GAP_UNREGISTERED_COVERAGE not in _codes(result)
    assert discovery.GAP_UNTESTED not in _codes(result)
    assert discovery.GAP_UNPUBLISHED_CLI not in _codes(result)


def test_a_convention_a_layer_has_established_is_expected_of_its_peers(tmp_path):
    modules = (
        _module("engine.alpha"),
        _module("engine.alpha.errors", capability="engine.alpha"),
        _module("engine.beta"),
        _module("engine.beta.errors", capability="engine.beta"),
        _module("engine.gamma"),
    )
    substrate = _substrate(tmp_path, modules)
    records, _ = discovery.discover_capabilities(substrate)
    result = discovery.discover_gaps(substrate, records)
    missing = [f for f in result.findings if f.code == discovery.GAP_MISSING_CONVENTION_MODULE]
    assert [f.subject for f in missing] == ["engine.gamma.errors"]
    assert missing[0].details["peers"] == 3


def test_a_layer_with_one_capability_establishes_no_convention(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"), _module("engine.alpha.errors", capability="engine.alpha")),
    )
    records, _ = discovery.discover_capabilities(substrate)
    result = discovery.discover_gaps(substrate, records)
    assert discovery.GAP_MISSING_CONVENTION_MODULE not in _codes(result)


# -- 6. conflicts ----------------------------------------------------------------------


def test_a_lower_layer_depending_on_a_higher_one_is_a_layer_violation(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha", imports=("platform.beta",)), _module("platform.beta")),
    )
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    result = discovery.discover_conflicts(substrate, records, edges)
    finding = _finding(result, discovery.CONFLICT_LAYER_VIOLATION)
    assert finding.subject == "engine.alpha -> platform.beta"
    assert finding.severity is Severity.BLOCKING


def test_a_cycle_is_reported_once_more_in_the_conflict_dimension_s_own_terms(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.alpha", imports=("engine.beta",)),
            _module("engine.beta", imports=("engine.alpha",)),
        ),
    )
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    result = discovery.discover_conflicts(substrate, records, edges)
    assert _finding(result, discovery.CONFLICT_IMPORT_CYCLE).details["cycle"]


def test_registration_in_one_coverage_gate_and_not_the_other_is_a_contradiction(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"),),
        declarations=Declarations(available=True, coverage_sources=("engine/alpha",)),
    )
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    result = discovery.discover_conflicts(substrate, records, edges)
    finding = _finding(result, discovery.CONFLICT_REGISTRATION_INCONSISTENT)
    assert finding.details == {"in_coverage_source": True, "in_pytest_cov": False}


def test_a_console_script_naming_a_module_that_does_not_exist_is_refused(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"),),
        declarations=Declarations(
            available=True, console_scripts={"ucos-ghost": "engine.ghost.cli:main"}
        ),
    )
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    result = discovery.discover_conflicts(substrate, records, edges)
    assert _finding(result, discovery.CONFLICT_ENTRY_POINT_UNRESOLVABLE).subject == "ucos-ghost"


def test_two_console_scripts_resolving_to_one_entry_point_are_reported(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"),),
        declarations=Declarations(
            available=True,
            console_scripts={"ucos-alpha": "engine.alpha:main", "alpha": "engine.alpha:main"},
        ),
    )
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    result = discovery.discover_conflicts(substrate, records, edges)
    finding = _finding(result, discovery.CONFLICT_ENTRY_POINT_ALIASED)
    assert finding.details["scripts"] == ["alpha", "ucos-alpha"]


def test_a_catalogued_capability_that_is_not_on_disk_is_a_phantom(tmp_path):
    catalog = (
        {
            "canonical_name": "engine.ghost",
            "category": "engine",
            "canonical_location": "engine/ghost",
            "authority": "A",
            "reuse": "R",
        },
    )
    substrate = _substrate(tmp_path, (_module("engine.alpha"),), catalog=catalog)
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    result = discovery.discover_conflicts(substrate, records, edges)
    assert _finding(result, discovery.CATALOG_PHANTOM).subject == "engine.ghost"


@pytest.mark.parametrize(
    ("includes", "reported"),
    [(("engine*",), False), (("engine",), False), (("platform*",), True)],
)
def test_a_code_root_no_package_include_matches_is_not_distributed(tmp_path, includes, reported):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"),),
        config=_config(tmp_path, code_roots=("engine",)),
        declarations=Declarations(available=True, packaged_includes=includes),
    )
    records, _ = discovery.discover_capabilities(substrate)
    edges, _ = discovery.discover_dependencies(substrate)
    result = discovery.discover_conflicts(substrate, records, edges)
    assert (discovery.CONFLICT_NOT_PACKAGED in _codes(result)) is reported


# -- 7. duplicates ---------------------------------------------------------------------


def test_two_byte_identical_modules_are_a_blocking_duplicate(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.alpha", content="same", loc=40),
            _module("platform.beta", content="same", loc=40),
        ),
    )
    result = discovery.detect_duplicates(substrate)
    finding = _finding(result, discovery.DUPLICATE_MODULE_CONTENT)
    assert finding.severity is Severity.BLOCKING
    assert finding.details["paths"] == ["engine/alpha.py", "platform/beta.py"]


def test_two_byte_identical_but_trivial_modules_are_convention_not_duplication(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.alpha", content="same", loc=1),
            _module("platform.beta", content="same", loc=1),
        ),
    )
    result = discovery.detect_duplicates(substrate)
    assert _finding(result, discovery.DUPLICATE_TRIVIAL_CONTENT).severity is Severity.ADVISORY
    assert discovery.DUPLICATE_MODULE_CONTENT not in _codes(result)


def test_one_capability_name_in_two_roots_is_reported_and_assessed(tmp_path):
    shared = ("Alpha", "Beta", "Gamma", "Delta")
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.thing", symbols=shared),
            _module("platform.thing", symbols=shared),
        ),
    )
    result = discovery.detect_duplicates(substrate)
    finding = _finding(result, discovery.DUPLICATE_CAPABILITY_NAME)
    assert finding.subject == "thing"
    assert finding.details["assessment"].startswith("SUSPECT")
    assert finding.details["surface_jaccard"] == 1.0


def test_a_layered_pair_with_distinct_surfaces_is_assessed_as_intentional(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.thing", symbols=("Alpha", "Beta")),
            _module("platform.thing", symbols=("Gamma", "Delta")),
        ),
    )
    finding = _finding(discovery.detect_duplicates(substrate), discovery.DUPLICATE_CAPABILITY_NAME)
    assert finding.details["assessment"].startswith("INTENTIONAL")
    assert finding.details["surface_jaccard"] == 0.0


def test_two_differently_named_capabilities_sharing_a_surface_are_duplication_candidates(tmp_path):
    shared = ("Alpha", "Beta", "Gamma", "Delta")
    substrate = _substrate(
        tmp_path,
        (_module("engine.left", symbols=shared), _module("engine.right", symbols=shared)),
    )
    result = discovery.detect_duplicates(substrate)
    finding = _finding(result, discovery.DUPLICATE_SYMBOL_SURFACE)
    assert finding.details["shared_count"] == 4
    assert finding.details["surface_jaccard"] == 1.0


def test_a_shared_surface_below_the_declared_thresholds_is_not_reported(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.left", symbols=("Alpha", "Beta", "Only")),
            _module("engine.right", symbols=("Alpha", "Beta", "Other")),
        ),
    )
    assert discovery.DUPLICATE_SYMBOL_SURFACE not in _codes(discovery.detect_duplicates(substrate))


def test_a_capability_with_no_public_surface_is_not_compared(tmp_path):
    substrate = _substrate(
        tmp_path, (_module("engine.left", symbols=()), _module("engine.right", symbols=()))
    )
    assert discovery.detect_duplicates(substrate).findings == ()


# -- 8. ownership ----------------------------------------------------------------------


def test_a_declared_terminal_is_the_strongest_ownership_evidence(tmp_path):
    substrate = _substrate(
        tmp_path, (_module("engine.alpha", docline="EPIC-DOC-003 (Terminal T4) — the portal."),)
    )
    units, _ = discovery.discover_repository(substrate)
    records, _ = discovery.discover_capabilities(substrate)
    ownership, result = discovery.discover_ownership(substrate, units, records)
    assert ownership[0].owner == "Terminal T4"
    assert ownership[0].confidence == "high"
    assert result.findings == ()


def test_two_declared_terminals_make_ownership_contested_rather_than_resolved(tmp_path):
    substrate = _substrate(
        tmp_path,
        (
            _module("engine.alpha", docline="Terminal T4 — the portal."),
            _module("engine.alpha.core", capability="engine.alpha", docline="Terminal T5 — core."),
        ),
    )
    units, _ = discovery.discover_repository(substrate)
    records, _ = discovery.discover_capabilities(substrate)
    ownership, result = discovery.discover_ownership(substrate, units, records)
    assert ownership[0].confidence == "contested"
    assert _finding(result, discovery.OWNERSHIP_CONTESTED).details["candidates"] == [
        "Terminal T4",
        "Terminal T5",
    ]


def test_a_programme_identifier_owns_a_capability_that_declares_no_terminal(tmp_path):
    substrate = _substrate(
        tmp_path, (_module("engine.alpha", docline="UCOS-EPIC-014 — commercial intelligence."),)
    )
    units, _ = discovery.discover_repository(substrate)
    records, _ = discovery.discover_capabilities(substrate)
    ownership, _result = discovery.discover_ownership(substrate, units, records)
    assert ownership[0].owner == "EPIC-014"
    assert ownership[0].confidence == "medium"


def test_the_layer_authority_owns_a_capability_that_declares_nothing(tmp_path):
    catalog = (
        {
            "canonical_name": "engine.alpha",
            "category": "engine",
            "authority": "OWNER-A",
            "reuse": "R",
            "canonical_location": "engine/alpha",
        },
    )
    substrate = _substrate(
        tmp_path, (_module("engine.alpha", docline="A module."),), catalog=catalog
    )
    units, _ = discovery.discover_repository(substrate)
    records, _ = discovery.discover_capabilities(substrate)
    ownership, result = discovery.discover_ownership(substrate, units, records)
    assert ownership[0].owner == "OWNER-A"
    assert ownership[0].confidence == "low"
    assert result.findings == ()


def test_a_capability_nothing_owns_is_reported_as_unowned(tmp_path):
    substrate = _substrate(tmp_path, (_module("engine.alpha", docline="A module."),))
    units, _ = discovery.discover_repository(substrate)
    records, _ = discovery.discover_capabilities(substrate)
    ownership, result = discovery.discover_ownership(substrate, units, records)
    assert ownership[0].confidence == "none"
    assert _finding(result, discovery.OWNERSHIP_UNOWNED).subject == "engine.alpha"


def test_a_module_with_no_docline_contributes_no_owner_token(tmp_path):
    assert discovery._declared_owners(
        _substrate(tmp_path, (_module("engine.alpha", docline=""),)), "engine.alpha"
    ) == ((), ())


# -- orchestration ---------------------------------------------------------------------


def test_discover_all_runs_every_dimension_and_the_outcome_is_addressable(tmp_path):
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"), _module("platform.beta", imports=("engine.alpha",))),
    )
    outcome = discovery.discover_all(substrate)
    assert len(outcome.results) == 8
    assert {r.dimension for r in outcome.results} == set(DiscoveryDimension)
    for dimension in DiscoveryDimension:
        assert outcome.result_for(dimension).dimension is dimension
    summary = discovery.dimension_summary(outcome)
    assert set(summary) == {d.value for d in DiscoveryDimension}
    assert all("verdict" in row for row in summary.values())


def test_asking_the_outcome_for_a_dimension_it_does_not_carry_yields_an_empty_result():
    outcome = discovery.DiscoveryOutcome(
        units=(), capabilities=(), reuse=(), edges=(), ownership=(), results=()
    )
    empty = outcome.result_for(DiscoveryDimension.GAP)
    assert empty.dimension is DiscoveryDimension.GAP
    assert empty.findings == ()


# --------------------------------------------------------------------------------------
# recommendation — the advice the engine gives about a substrate that contradicts itself
#
# WHY THIS SECTION EXISTS. The recommendation engine is the product of every dimension
# above: it turns findings into a ranked, evidence-cited work list, and it is the guard
# that answers "should I build this?" before a capability is duplicated. Over THIS
# repository it produces one shape of advice, so the branches that only fire on a
# contradictory substrate — the cycle-breaking repair target, the aggregate remedy, the
# NO_ACTION verdict over a clean repository — were unexecuted, and so was every arm of
# `advise` below REUSE.
# --------------------------------------------------------------------------------------


def _advisor(tmp_path: Path, modules: tuple[ModuleFact, ...], **kwargs):
    substrate = _substrate(tmp_path, modules, **kwargs)
    outcome = discovery.discover_all(substrate)
    return (
        substrate,
        outcome,
        RepositoryRecommendationEngine(
            substrate, outcome, build_graph(outcome.units, outcome.edges)
        ),
    )


def test_a_repository_with_nothing_to_report_is_advised_to_do_nothing(tmp_path):
    """The NO_ACTION arm. An engine that could only ever produce work would have no way to
    say that the repository is consistent, and 'no findings' would read as 'not run'."""

    substrate = _substrate(tmp_path, (_module("engine.alpha"),))
    empty = discovery.DiscoveryOutcome(
        units=(), capabilities=(), reuse=(), edges=(), ownership=(), results=()
    )
    engine = RepositoryRecommendationEngine(substrate, empty, build_graph(empty.units, empty.edges))
    (only,) = engine.recommend()
    assert only.action is RecommendationAction.NO_ACTION
    assert only.priority == PRIORITY_NONE
    assert engine.summary((only,))["total"] == 1
    assert engine.summary(())["next_action"] is None


def test_the_engine_refuses_anything_that_is_not_a_discovery_outcome(tmp_path):
    substrate = _substrate(tmp_path, (_module("engine.alpha"),))
    outcome = discovery.discover_all(substrate)
    graph = build_graph(outcome.units, outcome.edges)
    with pytest.raises(RecommendationError):
        RepositoryRecommendationEngine(substrate, {"not": "an outcome"}, graph)


def test_a_cycle_is_repaired_by_naming_the_heaviest_edge_to_invert(tmp_path):
    """The cheapest single inversion, derived from edge weight, rather than 'break the
    cycle' — advice that names no edge is advice nobody can act on."""
    modules = (
        _module("engine.alpha", imports=("engine.beta",)),
        _module("engine.alpha.two", capability="engine.alpha", imports=("engine.beta",)),
        _module("engine.beta", imports=("engine.alpha",)),
    )
    _substrate_, _outcome, engine = _advisor(tmp_path, modules)
    targets = [r.target for r in engine.recommend() if r.target]
    assert any("engine.alpha -> engine.beta (2 module(s))" in t for t in targets)
    assert any("cyclic component(s)" in t for t in targets)


def test_a_repair_target_falls_back_to_the_detail_the_finding_carries(tmp_path):
    modules = (
        _module("engine.alpha"),
        _module("engine.alpha.cli", capability="engine.alpha"),
    )
    _substrate_, _outcome, engine = _advisor(
        tmp_path,
        modules,
        declarations=Declarations(
            available=True, console_scripts={"ucos-ghost": "engine.ghost.cli:main"}
        ),
    )
    targets = {r.target for r in engine.recommend()}
    assert "engine.ghost.cli:main" in targets


def test_advisory_findings_that_share_a_code_share_one_recommendation(tmp_path):
    modules = (_module("engine.alpha"), _module("engine.beta"), _module("engine.gamma"))
    _substrate_, outcome, engine = _advisor(
        tmp_path, modules, declarations=Declarations(available=True)
    )
    untested = [
        f for result in outcome.results for f in result.findings if f.code == discovery.GAP_UNTESTED
    ]
    assert len(untested) == 3
    aggregated = [r for r in engine.recommend() if r.subject == discovery.GAP_UNTESTED]
    assert len(aggregated) == 1
    assert aggregated[0].rationale.startswith("3 subject(s):")
    assert aggregated[0].target == "3 subjects"
    assert len(aggregated[0].evidence) == 3


def test_proposing_a_capability_that_already_exists_is_answered_with_reuse(tmp_path):
    catalog = (
        {
            "canonical_name": "engine.alpha",
            "category": "engine",
            "reuse": "REUSE",
            "authority": "A",
            "canonical_location": "engine/alpha",
            "replacement_prohibited": True,
        },
    )
    _substrate_, _outcome, engine = _advisor(tmp_path, (_module("engine.alpha"),), catalog=catalog)
    advice = engine.advise("engine.alpha")
    assert advice.action is RecommendationAction.REUSE
    assert "replacement is prohibited" in advice.rationale
    assert advice.target == "engine/alpha"


def test_proposing_a_name_that_exists_in_another_layer_is_answered_with_extend(tmp_path):
    _substrate_, _outcome, engine = _advisor(tmp_path, (_module("engine.alpha"),))
    advice = engine.advise("platform.alpha")
    assert advice.action is RecommendationAction.EXTEND
    assert "engine.alpha" in advice.rationale


def test_a_proposal_whose_vocabulary_an_existing_capability_covers_is_answered_with_compose(
    tmp_path,
):
    module = _module(
        "engine.gapfinder",
        docline="Discover gaps, conflicts and duplicates across the repository.",
        symbols=("discover_gaps", "discover_conflicts", "detect_duplicates"),
    )
    _substrate_, _outcome, engine = _advisor(tmp_path, (module,))
    candidates = engine.reuse_candidates(
        "engine.finder", "discover gaps conflicts and duplicates across the repository"
    )
    assert candidates
    assert candidates[0].capability == "engine.gapfinder"
    assert 0.0 < candidates[0].score <= 1.0
    assert set(candidates[0].to_dict()) == {
        "capability",
        "score",
        "matched_tokens",
        "reuse_directive",
        "replacement_prohibited",
        "location",
    }
    advice = engine.advise(
        "engine.finder", "discover gaps conflicts and duplicates across the repository"
    )
    assert advice.action is RecommendationAction.COMPOSE
    assert advice.target == "engine.gapfinder"


def test_a_proposal_nothing_covers_is_answered_with_create(tmp_path):
    _substrate_, _outcome, engine = _advisor(tmp_path, (_module("engine.alpha", docline="A."),))
    advice = engine.advise("engine.quantum", "orbital mechanics telemetry")
    assert advice.action is RecommendationAction.CREATE


def test_a_proposal_with_no_usable_tokens_yields_no_reuse_candidate(tmp_path):
    _substrate_, _outcome, engine = _advisor(tmp_path, (_module("engine.alpha"),))
    assert engine.reuse_candidates("...", "") == ()


def test_advising_on_an_empty_proposal_is_refused_rather_than_permitted(tmp_path):
    """A permissive CREATE over an empty proposal is exactly the answer that lets a
    duplicate capability through."""
    _substrate_, _outcome, engine = _advisor(tmp_path, (_module("engine.alpha"),))
    for empty in ("", "   "):
        with pytest.raises(RecommendationError):
            engine.advise(empty)


def test_a_capability_with_no_derivable_vocabulary_is_not_a_candidate(tmp_path):
    _substrate_, _outcome, engine = _advisor(
        tmp_path, (_module("engine.a", capability="engine.a", docline="", symbols=()),)
    )
    assert engine.reuse_candidates("engine.other", "a description with words") == ()


# --------------------------------------------------------------------------------------
# The graph's own refusals, its degree projections, and the vocabulary's parse
#
# `build_graph` is only ever called on a graph the discovery pass just derived, so it is
# always well formed and the two GraphError arms never ran. They are not decoration: the
# graph is what every reachability, cycle and weight answer is computed over, so a graph
# that silently dropped a fact would make every one of those answers quietly wrong instead
# of loudly absent.
# --------------------------------------------------------------------------------------


def test_a_duplicate_node_identity_is_refused_rather_than_deduplicated(tmp_path):
    """Two nodes under one id are two different capabilities claiming one name. Keeping
    either one is a choice about which set of edges survives, and nothing here is entitled
    to make it."""

    node = GraphNode(node_id="engine.alpha", kind=UnitKind.CODE_CAPABILITY, label="alpha")
    twin = GraphNode(node_id="engine.alpha", kind=UnitKind.CODE_CAPABILITY, label="also alpha")
    with pytest.raises(GraphError) as excinfo:
        RepositoryGraph.create((node, twin), ())
    assert excinfo.value.context["node"] == "engine.alpha"


def test_an_edge_whose_endpoint_is_not_a_node_is_refused(tmp_path):
    """A dangling endpoint is a dropped fact, and dropping it silently is what makes a
    dependency answer wrong rather than missing: the edge exists in the repository and would
    exist in no projection of the graph. Both endpoints are checked, not just the target."""

    alpha = GraphNode(node_id="engine.alpha", kind=UnitKind.CODE_CAPABILITY, label="alpha")
    with pytest.raises(GraphError) as excinfo:
        RepositoryGraph.create(
            (alpha,),
            (DependencyEdge(source="engine.alpha", target="engine.ghost", weight=1),),
        )
    assert excinfo.value.context["unknown"] == "engine.ghost"

    with pytest.raises(GraphError) as excinfo:
        RepositoryGraph.create(
            (alpha,),
            (DependencyEdge(source="engine.ghost", target="engine.alpha", weight=1),),
        )
    assert excinfo.value.context["unknown"] == "engine.ghost"


def test_the_degree_projections_count_both_directions_over_every_node(tmp_path):
    """Out-degree and in-degree are the two halves of the same relation, and an ISOLATED node
    must appear in both at zero. A projection that only listed nodes with edges would make a
    capability nothing imports and that imports nothing invisible — which is exactly the
    shape of finished-but-unwired code the reuse dimension is trying to surface."""
    modules = (
        _module("engine.alpha", imports=("engine.beta",)),
        _module("engine.beta"),
        _module("engine.lonely"),
    )
    substrate = _substrate(tmp_path, modules)
    outcome = discovery.discover_all(substrate)
    graph = build_graph(outcome.units, outcome.edges)

    out, into = graph.out_degree(), graph.in_degree()
    assert set(out) == set(into) == set(graph.node_ids())
    assert out["engine.alpha"] == 1
    assert into["engine.beta"] == 1
    assert out["engine.lonely"] == into["engine.lonely"] == 0
    assert sum(out.values()) == sum(into.values())


def test_a_dimension_name_the_vocabulary_does_not_declare_is_refused() -> None:
    """The parse names what IS supported in the refusal, so a caller with a typo is told the
    eight values rather than left to find them."""

    assert DiscoveryDimension.parse("gap") is DiscoveryDimension.GAP
    assert DiscoveryDimension.parse(DiscoveryDimension.REUSE) is DiscoveryDimension.REUSE
    with pytest.raises(DiscoveryError) as excinfo:
        DiscoveryDimension.parse("reusability")
    assert excinfo.value.context["dimension"] == "reusability"
    assert set(excinfo.value.context["supported"]) == {d.value for d in DiscoveryDimension}


def test_a_dimension_the_report_never_ran_reads_as_an_empty_pass(tmp_path):
    """ "Ran and found nothing" and "did not run" both mean there is nothing to act on, so
    ``result_for`` answers for a dimension the report does not carry rather than raising —
    every consumer would otherwise need the same guard, and one of them would forget it.

    The two accessors built on it are asserted too, because they are what callers actually
    use: ``findings_of`` and ``failures_of`` inherit the totality or lose it together.
    """

    report = RepositoryIntelligenceReport(
        repository_id="synthetic",
        substrate_digest="substrate",
        units=(),
        capabilities=(),
        reuse=(),
        ownership=(),
        graph=build_graph((), ()),
        dimension_results=(DimensionResult.create(DiscoveryDimension.CAPABILITY, ()),),
        recommendations=(),
        verdict=Verdict.PASS,
        authority="ENGINEERING-EXECUTION-ONLY",
        derived_from="test",
        disclosure={},
        report_sha256="report",
    )

    carried = report.result_for(DiscoveryDimension.CAPABILITY)
    assert carried.dimension is DiscoveryDimension.CAPABILITY

    absent = report.result_for(DiscoveryDimension.GAP)
    assert absent.dimension is DiscoveryDimension.GAP
    assert absent.findings == ()
    assert report.findings_of(DiscoveryDimension.GAP) == ()
    assert report.failures_of(DiscoveryDimension.GAP) == ()
    assert report.all_findings == ()


def test_a_capability_with_no_package_module_describes_itself_with_nothing(tmp_path):
    """The docline is read from the capability's OWN package module. A capability made of
    sub-modules with no ``engine/alpha/__init__.py`` has no self-description, and "" is the
    honest answer — borrowing a sub-module's docline would attribute one module's sentence
    to the whole capability."""
    described = _substrate(tmp_path, (_module("engine.alpha", docline="Alpha describes itself."),))
    assert discovery._capability_docline(described, "engine.alpha") == "Alpha describes itself."

    undescribed = _substrate(tmp_path, (_module("engine.alpha.core"),))
    assert discovery._capability_docline(undescribed, "engine.alpha") == ""
    assert discovery._capability_docline(undescribed, "engine.absent") == ""


# --------------------------------------------------------------------------------------
# The arms a well-formed repository never reaches
# --------------------------------------------------------------------------------------


def test_a_dependency_spec_that_names_nothing_declares_no_distribution(tmp_path):
    """``>=1.0`` and ``""`` are entries a hand-edited pyproject really carries, and each parses
    to an empty name. Adding "" to the declared set would make EVERY unresolved import look
    declared, because an import whose top-level name is compared against a set containing the
    empty string still fails — but a later membership test on a normalised empty name would
    not, and the gap dimension would stop reporting undeclared third-party imports."""
    declarations = Declarations(
        available=True,
        runtime_dependencies=("jsonschema==4.26.0", ">=1.0", "   "),
        dev_dependencies=("", "pytest-cov>=5"),
    )
    substrate = _substrate(tmp_path, (_module("engine.alpha"),), declarations=declarations)
    assert discovery._declared_distributions(substrate) == {"jsonschema", "pytest_cov"}


def test_reuse_counts_only_import_edges_as_evidence_of_use(tmp_path):
    """A CONTAINS edge says a capability holds a module; it says nothing about anyone using it.

    Counting it as an importer would make every capability its own evidence of reuse, and the
    reuse dimension — whose entire job is to separate "exists" from "is used" — would report
    that everything is reused.
    """

    modules = (_module("engine.alpha"), _module("engine.beta"))
    substrate = _substrate(tmp_path, modules)
    outcome = discovery.discover_all(substrate)

    edges = (
        DependencyEdge(source="engine.beta", target="engine.alpha", kind=EdgeKind.CONTAINS),
        DependencyEdge(source="engine.beta", target="engine.alpha", kind=EdgeKind.PUBLISHES),
    )
    assessments, _result = discovery.discover_reuse(substrate, outcome.capabilities, edges)
    by_name = {a.capability: a for a in assessments}
    assert by_name["engine.alpha"].importers == ()

    importing = (DependencyEdge(source="engine.beta", target="engine.alpha"),)
    assessments, _result = discovery.discover_reuse(substrate, outcome.capabilities, importing)
    by_name = {a.capability: a for a in assessments}
    assert by_name["engine.alpha"].importers == ("engine.beta",)


def test_a_capability_that_is_not_on_disk_is_not_asked_about_its_registration(tmp_path):
    """A phantom catalog entry has no path, so "registered in one gate but not the other" is
    a question about nothing. Asking it anyway would manufacture a registration conflict for
    every catalog entry the substrate does not carry — which is the false-phantom shape the
    catalog suite already had to unpick once."""
    declarations = Declarations(
        available=True,
        coverage_sources=("engine/alpha",),
        pytest_cov_packages=("engine.alpha",),
    )
    substrate = _substrate(
        tmp_path,
        (_module("engine.alpha"),),
        declarations=declarations,
        catalog=(
            {
                "canonical_name": "engine.alpha",
                "canonical_location": "engine/alpha",
                "category": "engine",
            },
            {
                "canonical_name": "engine.phantom",
                "canonical_location": "engine/phantom",
                "category": "engine",
            },
        ),
    )
    outcome = discovery.discover_all(substrate)
    absent = [r for r in outcome.capabilities if not r.present_on_disk]
    assert [r.name for r in absent] == ["engine.phantom"]

    # The phantom IS reported — as a phantom. What must not happen is a REGISTRATION
    # verdict about it, because it has no path for either gate to have registered.
    conflicts = outcome.result_for(DiscoveryDimension.CONFLICT)
    registration = [
        f for f in conflicts.findings if f.code == discovery.CONFLICT_REGISTRATION_INCONSISTENT
    ]
    assert not any("engine.phantom" in f.subject for f in registration)


def test_a_cycle_whose_edges_the_graph_does_not_carry_names_no_edge_to_invert(tmp_path):
    """Advice that names no edge is advice nobody can act on — but INVENTING one would be
    worse. When the cycle's members share no edge in the graph the engine is holding, the
    repair target falls through to the component summary rather than pointing at an edge that
    is not there."""

    substrate, _outcome, engine = _advisor(tmp_path, (_module("engine.alpha"),))
    assert engine._heaviest_back_edge(("engine.ghost", "engine.phantom")) == ""

    finding = Finding(
        code="conflict.import_cycle",
        dimension=DiscoveryDimension.CONFLICT,
        severity=Severity.BLOCKING,
        status=FindingStatus.FAIL,
        subject="engine.ghost -> engine.phantom",
        message="mutually dependent",
        details={
            "cycle": ["engine.ghost", "engine.phantom"],
            "components": [["engine.ghost", "engine.phantom"]],
        },
    )
    assert (
        engine._repair_target(finding) == "1 cyclic component(s); see the conflict dimension detail"
    )


def test_a_word_that_becomes_a_stopword_when_depluralised_is_still_a_stopword(tmp_path):
    """``engines`` is not in the stopword set and ``engine`` is. Stripping the plural without
    re-testing would let every proposal about "engines" match on the repository's own layer
    name, which is exactly the collision the stopword list exists to prevent."""

    assert "engine" in recommendation._STOPWORDS
    assert "engines" not in recommendation._STOPWORDS
    assert "engines" not in recommendation._tokens("engines and platforms")
    assert "engine" not in recommendation._tokens("engines and platforms")
    assert "ledger" in recommendation._tokens("ledgers for the engines")


def test_a_report_carrying_no_findings_proves_no_rule_and_fails_closed(tmp_path):
    """ "Could not be determined" is not "holds".

    Every intelligence rule is evidenced by a specific discovery finding, so a report that
    produced none cannot prove any of them. Passing here would be the worst possible failure
    mode of the whole subsystem: a repository nothing was measured over would certify.
    """

    empty = RepositoryIntelligenceReport(
        repository_id="synthetic",
        substrate_digest="substrate",
        units=(),
        capabilities=(),
        reuse=(),
        ownership=(),
        graph=build_graph((), ()),
        dimension_results=(DimensionResult.create(DiscoveryDimension.REPOSITORY, ()),),
        recommendations=(),
        verdict=Verdict.PASS,
        authority="ENGINEERING-EXECUTION-ONLY",
        derived_from="test",
        disclosure={},
        report_sha256="a" * 64,
    )
    validation = RepositoryValidator(empty).validate()
    undetermined = [rule for rule in validation.rules if "could not be determined" in rule.message]
    assert undetermined, "a report with no findings proved a rule anyway"
    assert all(rule.status is not FindingStatus.PASS for rule in undetermined)
    assert validation.verdict is not Verdict.PASS


def test_the_transitive_closure_visits_a_diamond_once_and_never_returns_to_its_origin(tmp_path):
    """TWO GUARDS, TWO DIFFERENT INFINITE LOOPS, and a well-formed acyclic repository trips
    neither — which is why they were unexecuted.

    ``neighbour not in seen`` is what stops a DIAMOND from being walked twice: alpha reaches
    delta through both beta and gamma, and without it delta re-enters the frontier and the
    work doubles at every subsequent level. ``neighbour != node_id`` is what stops a CYCLE
    from putting the origin into its own closure — "alpha depends on alpha" is not a fact
    about the repository, it is an artifact of the walk, and it would appear in the blast
    radius of every capability in a cycle.
    """
    diamond = (
        _module("engine.alpha", imports=("engine.beta", "engine.gamma")),
        _module("engine.beta", imports=("engine.delta",)),
        _module("engine.gamma", imports=("engine.delta",)),
        _module("engine.delta"),
    )
    substrate = _substrate(tmp_path, diamond)
    outcome = discovery.discover_all(substrate)
    graph = build_graph(outcome.units, outcome.edges)

    reached = graph.dependencies_of("engine.alpha")
    assert reached == ("engine.beta", "engine.delta", "engine.gamma")
    assert len(reached) == len(set(reached))
    assert graph.dependencies_of("engine.alpha", depth=1) == ("engine.beta", "engine.gamma")
    assert graph.dependents_of("engine.delta") == ("engine.alpha", "engine.beta", "engine.gamma")

    cyclic = (
        _module("engine.alpha", imports=("engine.beta",)),
        _module("engine.beta", imports=("engine.alpha",)),
    )
    substrate = _substrate(tmp_path / "cyclic", cyclic)
    outcome = discovery.discover_all(substrate)
    graph = build_graph(outcome.units, outcome.edges)
    assert graph.dependencies_of("engine.alpha") == ("engine.beta",)
    assert graph.dependents_of("engine.alpha") == ("engine.beta",)
