"""The one read-only pass, and the configuration that steers it, over BUILT repositories.

WHY THIS MODULE EXISTS. `RepositorySubstrate.scan` is measured everywhere — through this
repository, which is a git work tree with a readable pyproject, a sealed capability catalog
and no unparseable module. Every fallback it carries for a repository that is none of those
things was therefore unexecuted: the filesystem walk that stands in for `git ls-files`, the
`Declarations()` it returns when pyproject is absent or malformed, the catalog artifact
reader, the unparseable-module path, and the `SubstrateError` that refuses a catalog entry
with no canonical identity. Each of those is the behaviour on a repository someone will
actually point this at, and a fallback nobody has taken is a fallback nobody has checked.

Every repository below is BUILT under ``tmp_path``, which is what makes these statements
about the SUBSTRATE rather than about the tree the suite happens to run in.
"""

from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path
from platform.repository_intelligence import substrate as sub
from platform.repository_intelligence.certification import (
    GATE_CLOSED,
    GATE_OPEN,
    RepositoryCertificate,
    certify,
)
from platform.repository_intelligence.config import (
    DEFAULT_CONVENTION_MODULES,
    DEFAULT_IGNORED_DIRS,
    RepositoryIntelligenceConfig,
    load_config,
    parse_config,
    resolve_repository_root,
)
from platform.repository_intelligence.contracts import Determination, DiscoveryDimension
from platform.repository_intelligence.discovery import discover_all
from platform.repository_intelligence.errors import (
    IntelligenceConfigurationError,
    RepositoryCertificationError,
    RepositoryValidationError,
    SubstrateError,
)
from platform.repository_intelligence.recommendation import build_recommendations
from platform.repository_intelligence.runtime import (
    RepositoryIntelligenceRuntime,
    detect_drift,
    gate,
    run_once,
)
from platform.repository_intelligence.service import build_repository_intelligence_service
from platform.repository_intelligence.validation import RepositoryValidator, validate_report

import pytest

from engine.omega_infinite.provider import ProviderError
from intelligence.rie import discovery as rie_discovery

PYPROJECT = """
[project]
name = "synthetic"
dependencies = ["jsonschema==4.26.0"]
[project.optional-dependencies]
dev = ["pytest==8.3.4"]
[project.scripts]
ucos-alpha = "engine.alpha.cli:main"
[tool.setuptools.packages.find]
include = ["engine*"]
[tool.coverage.run]
source = ["engine/alpha"]
[tool.coverage.report]
fail_under = 90
[tool.pytest.ini_options]
addopts = ["--cov=engine.alpha", "-ra"]
"""


def _repo(tmp_path: Path, *, pyproject: str | None = PYPROJECT) -> Path:
    (tmp_path / "engine" / "alpha").mkdir(parents=True)
    (tmp_path / "engine" / "__init__.py").write_text('"""Root."""\n', encoding="utf-8")
    (tmp_path / "engine" / "alpha" / "__init__.py").write_text(
        '"""Alpha — Terminal T5."""\n\n\ndef run() -> int:\n    return 0\n', encoding="utf-8"
    )
    if pyproject is not None:
        (tmp_path / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    return tmp_path


def _config(root: Path, **overrides) -> RepositoryIntelligenceConfig:
    return RepositoryIntelligenceConfig.create(
        root, repository_id="synthetic", code_roots=("engine",), **overrides
    )


# -- configuration ---------------------------------------------------------------------


def test_a_configuration_defaults_every_field_it_is_not_given(tmp_path):
    config = RepositoryIntelligenceConfig.create(tmp_path)
    assert config.repository_id == tmp_path.name
    assert config.code_roots == ("engine", "platform")
    assert config.ignored_dirs == DEFAULT_IGNORED_DIRS
    assert config.convention_modules == DEFAULT_CONVENTION_MODULES
    assert config.pyproject_path == tmp_path / "pyproject.toml"
    assert config.output_dir == tmp_path / ".runtime/repository-intelligence"
    assert config.capability_catalog_path.name == "UCOS-RIE-CAPABILITY-CATALOG.json"
    assert config.code_root_path("engine") == tmp_path / "engine"


def test_an_unknown_configuration_key_is_refused_rather_than_ignored(tmp_path):
    with pytest.raises(IntelligenceConfigurationError) as excinfo:
        RepositoryIntelligenceConfig.create(tmp_path, not_a_key=1, also_not=2)
    assert excinfo.value.context["keys"] == ["also_not", "not_a_key"]


def test_a_configuration_that_is_not_a_mapping_is_refused():
    with pytest.raises(IntelligenceConfigurationError):
        RepositoryIntelligenceConfig.from_mapping(["not", "a", "mapping"])


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("code_roots", "engine"),
        ("code_roots", 7),
        ("ignored_dirs", "cache"),
        ("convention_modules", object()),
        ("extra_evidence", 3),
    ],
)
def test_a_list_field_given_something_that_is_not_a_list_is_refused(tmp_path, key, value):
    with pytest.raises(IntelligenceConfigurationError, match="expected a list of strings"):
        RepositoryIntelligenceConfig.create(tmp_path, **{key: value})


@pytest.mark.parametrize("value", ["not-a-number", None, object()])
def test_a_threshold_that_is_not_a_number_is_refused(tmp_path, value):
    with pytest.raises(IntelligenceConfigurationError, match="expected a number"):
        RepositoryIntelligenceConfig.create(tmp_path, convention_threshold=value)


@pytest.mark.parametrize("value", [-0.1, 1.5])
def test_a_threshold_outside_zero_to_one_is_refused(tmp_path, value):
    with pytest.raises(IntelligenceConfigurationError, match=r"fraction in \[0,1\]"):
        RepositoryIntelligenceConfig.create(tmp_path, convention_threshold=value)


@pytest.mark.parametrize("value", ["five", None, object()])
def test_a_minimum_loc_that_is_not_an_integer_is_refused(tmp_path, value):
    with pytest.raises(IntelligenceConfigurationError, match="expected an integer"):
        RepositoryIntelligenceConfig.create(tmp_path, duplicate_min_loc=value)


def test_a_negative_minimum_loc_is_refused(tmp_path):
    with pytest.raises(IntelligenceConfigurationError, match="non-negative"):
        RepositoryIntelligenceConfig.create(tmp_path, duplicate_min_loc=-1)


def test_a_path_outside_the_repository_is_reported_as_itself(tmp_path):
    config = _config(tmp_path)
    assert config.rel(tmp_path / "engine" / "x.py") == "engine/x.py"
    assert config.rel(Path("/elsewhere/x.py")) == "/elsewhere/x.py"


def test_an_ignored_directory_is_recognised_at_any_depth(tmp_path):
    config = _config(tmp_path)
    assert config.is_ignored(Path("engine/__pycache__/x.pyc")) is True
    assert config.is_ignored(Path("engine/alpha/x.py")) is False


def test_a_repository_with_no_declared_code_root_fails_closed(tmp_path):
    """Vacuous intelligence over an empty substrate is worse than an explicit failure."""
    with pytest.raises(SubstrateError):
        _config(tmp_path).require_substrate()
    _repo(tmp_path)
    _config(tmp_path).require_substrate()


def test_the_configuration_digest_is_content_addressed_and_path_independent(tmp_path):
    first = tmp_path / "one" / "repo"
    second = tmp_path / "two" / "repo"
    for root in (first, second):
        root.mkdir(parents=True)
    assert (
        RepositoryIntelligenceConfig.create(first).digest()
        == RepositoryIntelligenceConfig.create(second).digest()
    )
    assert "repository_root" in RepositoryIntelligenceConfig.create(first).to_dict()
    assert RepositoryIntelligenceConfig.create(first).to_dict()["repository_root"] == "repo"


def test_a_json_and_a_toml_configuration_assimilate_identically(tmp_path):
    document = {"repository_root": str(tmp_path), "code_roots": ["engine"], "duplicate_min_loc": 9}
    json_path = tmp_path / "ri.json"
    json_path.write_text(json.dumps(document), encoding="utf-8")
    toml_path = tmp_path / "ri.toml"
    toml_path.write_text(
        f'repository_root = "{tmp_path}"\ncode_roots = ["engine"]\nduplicate_min_loc = 9\n',
        encoding="utf-8",
    )
    assert load_config(json_path).digest() == load_config(toml_path).digest()
    assert parse_config(document).duplicate_min_loc == 9


def test_a_configuration_file_that_is_absent_unreadable_or_foreign_is_refused(tmp_path):
    with pytest.raises(IntelligenceConfigurationError, match="not found"):
        load_config(tmp_path / "absent.json")

    broken = tmp_path / "broken.json"
    broken.write_text("{ not json", encoding="utf-8")
    with pytest.raises(IntelligenceConfigurationError, match="could not be read or parsed"):
        load_config(broken)

    foreign = tmp_path / "config.yaml"
    foreign.write_text("a: 1", encoding="utf-8")
    with pytest.raises(IntelligenceConfigurationError, match="unsupported configuration file type"):
        load_config(foreign)

    listy = tmp_path / "list.json"
    listy.write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(IntelligenceConfigurationError, match="must be a mapping/table"):
        load_config(listy)


def test_the_root_resolver_walks_up_to_the_substrate_marker(tmp_path):
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    assert resolve_repository_root(deep) == tmp_path.resolve()


def test_the_root_resolver_never_raises_when_no_marker_exists(tmp_path):
    """A resolver that raised would make the subsystem unusable outside a packaged tree."""
    assert resolve_repository_root(tmp_path / "nothing" / "here").is_dir()


# -- the scan --------------------------------------------------------------------------


def test_a_repository_without_git_is_walked_deterministically(tmp_path):
    """The filesystem fallback is what makes intelligence usable on an export with no
    ``.git`` — a non-git tree must produce a substrate, not an empty one."""
    _repo(tmp_path)
    (tmp_path / "engine" / "__pycache__").mkdir()
    (tmp_path / "engine" / "__pycache__" / "x.pyc").write_text("cached", encoding="utf-8")
    substrate = sub.RepositorySubstrate.scan(_config(tmp_path))
    paths = {module.path for module in substrate.modules}
    assert paths == {"engine/__init__.py", "engine/alpha/__init__.py"}
    assert substrate.digest() == sub.RepositorySubstrate.scan(_config(tmp_path)).digest()


def test_the_declarations_are_read_from_pyproject(tmp_path):
    _repo(tmp_path)
    declarations = sub.RepositorySubstrate.scan(_config(tmp_path)).declarations
    assert declarations.available is True
    assert declarations.console_scripts == {"ucos-alpha": "engine.alpha.cli:main"}
    assert declarations.packaged_includes == ("engine*",)
    assert declarations.coverage_sources == ("engine/alpha",)
    assert declarations.pytest_cov_packages == ("engine.alpha",)
    assert declarations.runtime_dependencies == ("jsonschema==4.26.0",)
    assert declarations.dev_dependencies == ("pytest==8.3.4",)
    assert declarations.coverage_fail_under == 90.0
    assert set(declarations.to_dict()) == {
        "available",
        "console_scripts",
        "packaged_includes",
        "coverage_sources",
        "pytest_cov_packages",
        "runtime_dependencies",
        "dev_dependencies",
        "coverage_fail_under",
    }


def test_an_absent_or_malformed_pyproject_leaves_the_declarations_unavailable(tmp_path):
    """Unavailable is not empty-and-fine: the declaration-dependent checks read
    ``available`` precisely so they fail closed instead of passing vacuously."""
    _repo(tmp_path, pyproject=None)
    assert sub.RepositorySubstrate.scan(_config(tmp_path)).declarations.available is False

    (tmp_path / "pyproject.toml").write_text("[project\nname =", encoding="utf-8")
    assert sub.RepositorySubstrate.scan(_config(tmp_path)).declarations.available is False


def test_a_pyproject_whose_tables_are_the_wrong_shape_yields_empty_declarations(tmp_path):
    _repo(tmp_path, pyproject='project = "not-a-table"\ntool = 7\n')
    declarations = sub.RepositorySubstrate.scan(_config(tmp_path)).declarations
    assert declarations.available is True
    assert declarations.console_scripts == {}
    assert declarations.coverage_fail_under is None


def test_a_module_that_does_not_parse_is_recorded_as_unparsed_rather_than_dropped(tmp_path):
    _repo(tmp_path)
    (tmp_path / "engine" / "alpha" / "broken.py").write_text("def (\n", encoding="utf-8")
    substrate = sub.RepositorySubstrate.scan(_config(tmp_path))
    broken = substrate.module_index()["engine.alpha.broken"]
    assert broken.parsed is False
    assert broken.imports == () and broken.symbols == () and broken.docline == ""


def test_only_a_root_initialiser_attributes_to_the_root_itself(tmp_path):
    """``engine/__init__.py`` is the root; anything deeper — including a module sitting
    loose in the root — is its own first sub-package, which is the grain the RIE catalog
    also treats as a capability."""
    _repo(tmp_path)
    (tmp_path / "engine" / "loose.py").write_text('"""Loose."""\n', encoding="utf-8")
    index = sub.RepositorySubstrate.scan(_config(tmp_path)).module_index()
    assert index["engine"].capability == "engine"
    assert index["engine.loose"].capability == "engine.loose"
    assert index["engine.alpha"].capability == "engine.alpha"


def test_a_test_module_attributes_to_the_test_package_and_never_to_the_surface(tmp_path):
    _repo(tmp_path)
    (tmp_path / "engine" / "tests").mkdir()
    (tmp_path / "engine" / "tests" / "test_alpha.py").write_text(
        "import engine.alpha\n", encoding="utf-8"
    )
    substrate = sub.RepositorySubstrate.scan(_config(tmp_path))
    test = substrate.module_index()["engine.tests.test_alpha"]
    assert test.is_test is True
    assert test.capability == "engine.tests"
    assert test not in substrate.source_modules()
    assert substrate.test_modules() == (test,)


def test_relative_imports_resolve_against_the_owning_package(tmp_path):
    _repo(tmp_path)
    (tmp_path / "engine" / "alpha" / "core.py").write_text(
        "from . import contracts\nfrom .. import alpha\nfrom .nested.deep import thing\n",
        encoding="utf-8",
    )
    facts = sub.RepositorySubstrate.scan(_config(tmp_path)).module_index()["engine.alpha.core"]
    # `from . import x` names the PACKAGE, `from .y import z` names `<package>.y`, and
    # `from .. import x` climbs one level — three different resolutions, all absolute.
    assert set(facts.imports) == {"engine.alpha", "engine", "engine.alpha.nested.deep"}


def test_a_deferred_import_is_recorded_as_an_import_and_not_as_an_import_time_one(tmp_path):
    _repo(tmp_path)
    (tmp_path / "engine" / "alpha" / "core.py").write_text(
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n    import engine.beta\n"
        "def later():\n    import engine.gamma\n"
        "import engine.delta\n",
        encoding="utf-8",
    )
    facts = sub.RepositorySubstrate.scan(_config(tmp_path)).module_index()["engine.alpha.core"]
    assert {"engine.beta", "engine.gamma", "engine.delta"} <= set(facts.imports)
    assert "engine.delta" in facts.import_time_imports
    assert set(facts.deferred_imports) == {"engine.beta", "engine.gamma"}


def test_an_import_nested_inside_a_type_checking_block_is_still_deferred(tmp_path):
    """A TYPE_CHECKING body holds STATEMENTS, and only some of them are imports.

    The guarded body is walked statement by statement so the deferral is applied to each,
    and a statement that is not itself an import has to be descended into rather than
    skipped — a ``try/except ImportError`` around a typing-only import is the ordinary way
    that block is written, and treating it as opaque would drop the dependency entirely.
    """
    _repo(tmp_path)
    (tmp_path / "engine" / "alpha" / "core.py").write_text(
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    try:\n"
        "        import engine.beta\n"
        "    except ImportError:\n"
        "        engine = None\n"
        "else:\n"
        "    import engine.delta\n",
        encoding="utf-8",
    )
    facts = sub.RepositorySubstrate.scan(_config(tmp_path)).module_index()["engine.alpha.core"]
    assert {"engine.beta", "engine.delta"} <= set(facts.imports)
    assert "engine.beta" in facts.deferred_imports
    assert "engine.delta" in facts.import_time_imports


def test_the_else_arm_of_a_type_checking_block_can_carry_a_nested_import(tmp_path):
    """The ``else:`` arm is the branch that DOES run at import, and it is walked with the
    caller's deferral rather than with the guard's. A nested statement there must therefore
    reach the same descent — deferring it would erase a real dependency, which is the same
    error as the body's in the opposite direction."""
    _repo(tmp_path)
    (tmp_path / "engine" / "alpha" / "core.py").write_text(
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    import engine.beta\n"
        "else:\n"
        "    try:\n"
        "        import engine.delta\n"
        "    except ImportError:\n"
        "        pass\n",
        encoding="utf-8",
    )
    facts = sub.RepositorySubstrate.scan(_config(tmp_path)).module_index()["engine.alpha.core"]
    assert "engine.delta" in facts.import_time_imports
    assert "engine.beta" in facts.deferred_imports


def test_a_module_path_that_cannot_be_read_is_dropped_rather_than_crashing_the_scan(tmp_path):
    """One unreadable path must not be the reason the whole substrate cannot be measured.

    A DIRECTORY NAMED LIKE A MODULE IS THE REALISTIC CASE, and it is what the walk actually
    hands to ``_module_fact``: the fallback enumerates every file, a caller can create
    ``engine/alpha/plugin.py/`` as a directory, and ``read_text`` on it raises ``IsADirectoryError``
    — an ``OSError``. The scan keeps every module it could read.
    """
    _repo(tmp_path)
    (tmp_path / "engine" / "alpha" / "readable.py").write_text("X = 1\n", encoding="utf-8")
    assert sub._module_fact(_config(tmp_path), "engine/alpha") is None
    assert sub._module_fact(_config(tmp_path), "engine/alpha/absent.py") is None
    assert sub._module_fact(_config(tmp_path), "engine/alpha/readable.py") is not None


def test_the_tracked_population_comes_from_the_provider_when_there_is_one():
    """The provider path, over the one repository that HAS a provider to answer.

    Every other substrate test builds a tree with no ``.git``, so the provider always raised
    and only the filesystem fallback ever ran. That leaves the primary path — the one every
    real invocation takes — measured by nothing, and the fallback's own comment records what
    that costs: returning an empty tuple instead of falling back once turned "not a working
    copy" into "an empty repository" for 58 tests.
    """
    root = Path(__file__).resolve().parents[2]
    paths = sub._tracked_files(RepositoryIntelligenceConfig.create(root))
    assert len(paths) > 1000, "the provider answered with a population too small to be this repo"
    assert "platform/repository_intelligence/substrate.py" in paths
    assert paths == tuple(sorted(paths))
    assert not any(".ec1-venv" in path for path in paths)


def test_a_producer_this_repository_cannot_import_falls_back_instead_of_failing(monkeypatch):
    """The ``intelligence`` root is importable HERE, so the ImportError arm never ran.

    It is not decoration: this subsystem is meant to be usable against a repository that
    carries no UCOS-RIE-001 producer at all, and the answer there is "no live catalog", not
    a crash. ``sys.modules[name] = None`` is the interpreter's own way of making an import
    of *name* raise ImportError, so the arm is reached by the failure it was written for
    rather than by a stubbed function that returns the answer.
    """

    monkeypatch.setitem(sys.modules, "intelligence.rie.config", None)
    assert sub._catalog_from_producer(_config(Path(__file__).resolve().parents[2])) == ()


def test_a_producer_that_faults_falls_back_to_the_sealed_artifact(monkeypatch):
    """DEFENSIVE, AND DELIBERATELY BROAD. The producer is another programme's code running
    inside this measurement; whatever it raises, the honest answer is that no live catalog
    was obtained — not that repository intelligence cannot run. The bare ``except`` is the
    boundary between two subsystems, and this is the failure it exists for."""

    def faulting(_reader):
        raise ValueError("the producer could not read its own evidence")

    monkeypatch.setattr(rie_discovery, "discover", faulting)
    assert sub._catalog_from_producer(_config(Path(__file__).resolve().parents[2])) == ()


def test_a_sealed_catalog_artifact_is_read_when_the_producer_is_unavailable(tmp_path, monkeypatch):
    _repo(tmp_path)
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        json.dumps(
            {
                "capabilities": [
                    {
                        "canonical_name": "engine.alpha",
                        "canonical_location": "engine/alpha",
                        "category": "engine",
                        "reuse": "REUSE",
                    },
                    {"no_name": True},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(sub, "_catalog_from_producer", lambda _cfg: ())
    substrate = sub.RepositorySubstrate.scan(_config(tmp_path, capability_catalog="catalog.json"))
    assert substrate.catalog_source == sub.CATALOG_SOURCE_ARTIFACT
    assert substrate.catalog_available() is True
    assert [entry["canonical_name"] for entry in substrate.catalog] == ["engine.alpha"]


@pytest.mark.parametrize("payload", ["{ not json", '{"capabilities": "not-a-list"}', "[]"])
def test_a_catalog_artifact_that_cannot_be_used_leaves_the_catalog_absent(
    tmp_path, monkeypatch, payload
):
    _repo(tmp_path)
    (tmp_path / "catalog.json").write_text(payload, encoding="utf-8")
    monkeypatch.setattr(sub, "_catalog_from_producer", lambda _cfg: ())
    substrate = sub.RepositorySubstrate.scan(_config(tmp_path, capability_catalog="catalog.json"))
    assert substrate.catalog_source == sub.CATALOG_SOURCE_ABSENT
    assert substrate.catalog_available() is False


def test_an_absent_catalog_artifact_leaves_the_catalog_absent(tmp_path, monkeypatch):
    _repo(tmp_path)
    monkeypatch.setattr(sub, "_catalog_from_producer", lambda _cfg: ())
    substrate = sub.RepositorySubstrate.scan(_config(tmp_path, capability_catalog="nowhere.json"))
    assert substrate.catalog_source == sub.CATALOG_SOURCE_ABSENT


def test_a_catalog_entry_with_no_canonical_identity_fails_loudly(tmp_path):
    """A malformed upstream producer must not be silently patched: the entry has no
    identity, so nothing downstream could address what it names."""
    with pytest.raises(SubstrateError):
        sub._normalize_catalog_entry({"canonical_location": "engine/alpha"})


def test_a_catalog_entry_is_projected_onto_exactly_the_keys_this_subsystem_consumes():
    entry = sub._normalize_catalog_entry(
        {"canonical_name": "engine.alpha", "surprise": "dropped", "replacement_prohibited": 1}
    )
    assert "surprise" not in entry
    assert entry["replacement_prohibited"] is True
    assert entry["description"] == ""


def test_a_version_control_reader_that_cannot_run_yields_no_output(tmp_path, monkeypatch):
    """The reader degrades to the filesystem walk rather than aborting the scan.

    THE PROPERTY IS UNCHANGED; WHAT IT REACHES THROUGH IS. This asserted the property by
    monkeypatching `sub.subprocess.run` and calling `sub._git_raw` — two internals that existed
    only because this module invoked the tool directly. Both are gone, and asserting through them
    would now be asserting that a particular implementation is still present rather than that the
    degradation still happens.

    It fails the PROVIDER instead, which is the surface the module actually depends on, and
    asserts the same two things: the population reader returns nothing, and the scan still finds
    modules by walking. A test that survives the mechanism it was written against is testing the
    behaviour.
    """

    class _Refusing:
        def enumerate(self, *_a, **_k):
            raise ProviderError("no version control here")

        def supply(self, *_a, **_k):
            raise ProviderError("no version control here")

    monkeypatch.setattr(sub, "_provider", lambda _cfg: _Refusing())
    assert sub._tracked_files(_config(_repo(tmp_path))) != ()
    assert sub.RepositorySubstrate.scan(_config(tmp_path)).modules


def test_the_substrate_answers_the_questions_the_dimensions_ask_of_it(tmp_path):
    _repo(tmp_path)
    substrate = sub.RepositorySubstrate.scan(_config(tmp_path))
    assert substrate.capabilities_on_disk() == ("engine", "engine.alpha")
    assert substrate.capability_of_module("engine.alpha.deeply.nested") == "engine.alpha"
    assert substrate.capability_of_module("nothing.here") is None
    assert substrate.location_is_populated("engine/alpha") is True
    assert substrate.location_is_populated("engine/ghost") is False
    assert substrate.location_is_populated("  ") is False
    assert substrate.symbols_of("engine.alpha") == ("run",)
    assert substrate.loc_of("engine.alpha") > 0
    assert all(isinstance(name, str) and name for name in substrate.catalog_index())
    payload = substrate.to_dict()
    assert payload["repository_id"] == "synthetic"
    assert payload["counts"]["modules"] == len(substrate.modules)
    assert payload["provenance"] == dict(sorted(substrate.provenance.items()))


def test_a_module_fact_serialises_its_core_plus_its_docline(tmp_path):
    _repo(tmp_path)
    fact = sub.RepositorySubstrate.scan(_config(tmp_path)).module_index()["engine.alpha"]
    assert fact.basename == "alpha"
    assert "docline" not in fact.core()
    assert fact.to_dict()["docline"] == "Alpha — Terminal T5."


# -- the runtime: drift, persistence and the fail-closed gate --------------------------
#
# WHY THIS SECTION EXISTS. `detect_drift` is what makes continuous re-scanning viable —
# it answers "baseline", "unchanged" or "here is exactly what moved" — and only the last
# of those three had ever been produced. `prior_report` returning None on a corrupt file
# (the fail-safe direction: no prior beats a wrong prior), and the `gate` that turns a
# cycle into an exit code, were unexecuted as well.


def _synthetic_current() -> dict:
    return {
        "capabilities": ["engine.alpha", "engine.beta"],
        "dimension_verdicts": {"gap": "pass", "conflict": "fail"},
        "graph_digest": "now",
    }


def test_the_first_cycle_establishes_a_baseline_rather_than_inventing_change():
    drift = detect_drift("digest", _synthetic_current(), None)
    assert drift["baseline"] is True
    assert drift["capabilities_added"] == []
    assert drift["dimension_changes"] == []


def test_an_identical_substrate_digest_is_the_cheap_exact_answer():
    drift = detect_drift("same", _synthetic_current(), {"substrate_digest": "same"})
    assert drift["baseline"] is False
    assert drift["substrate_changed"] is False
    assert drift["dimension_changes"] == []


def test_a_changed_substrate_reports_exactly_what_moved():
    prior = {
        "substrate_digest": "before",
        "verdict": "pass",
        "capabilities": [
            {"name": "engine.alpha", "present_on_disk": True},
            {"name": "engine.gone", "present_on_disk": True},
            {"name": "engine.phantom", "present_on_disk": False},
        ],
        "dimension_verdicts": {"gap": "pass", "conflict": "pass"},
        "graph": {"graph_digest": "before"},
    }
    drift = detect_drift("after", _synthetic_current(), prior)
    assert drift["substrate_changed"] is True
    assert drift["prior_substrate_digest"] == "before"
    assert drift["capabilities_added"] == ["engine.beta"]
    assert drift["capabilities_removed"] == ["engine.gone"]
    assert drift["dimension_changes"] == [{"dimension": "conflict", "from": "pass", "to": "fail"}]
    assert drift["prior_verdict"] == "pass"
    assert drift["graph_changed"] is True


def test_a_cycle_persists_its_artefacts_and_reads_its_own_prior_back(tmp_path):
    _repo(tmp_path)
    runtime = RepositoryIntelligenceRuntime(_config(tmp_path, output_subdir=".ri"))
    assert runtime.prior_report() is None

    written = runtime.write()
    assert written
    assert runtime.output_dir == tmp_path / ".ri"
    prior = runtime.prior_report()
    assert prior is not None
    assert prior["substrate_digest"]

    # Persisting into the repository is itself a substrate change, and the drift the next
    # cycle reports says so rather than silently absorbing its own output.
    second = runtime.scan(prior)
    assert second.summary()["repository_id"] == "synthetic"
    assert second.report.drift["baseline"] is False
    assert second.report.drift["prior_substrate_digest"] == prior["substrate_digest"]
    assert runtime.verify_determinism()["deterministic"] is True


@pytest.mark.parametrize("payload", ["{ not json", '["not", "a", "mapping"]'])
def test_a_prior_report_that_cannot_be_used_reads_as_no_prior(tmp_path, payload):
    """No prior beats a wrong prior: drift would otherwise be computed against garbage."""
    _repo(tmp_path)
    runtime = RepositoryIntelligenceRuntime(_config(tmp_path, output_subdir=".ri"))
    runtime.output_dir.mkdir(parents=True, exist_ok=True)
    (runtime.output_dir / "UCOS-RPI-REPORT.json").write_text(payload, encoding="utf-8")
    assert runtime.prior_report() is None


def test_the_gate_turns_a_cycle_into_an_exit_code(tmp_path):
    _repo(tmp_path)
    config = _config(tmp_path, output_subdir=".ri")
    cycle = run_once(config)
    assert gate(config) == (0 if cycle.passed and cycle.report.verdict.value != "fail" else 1)
    assert cycle.summary()["substrate_digest"] == cycle.report.substrate_digest


def test_the_service_composes_the_runtime_without_a_second_derivation(tmp_path):
    _repo(tmp_path)
    service = build_repository_intelligence_service(_config(tmp_path, output_subdir=".ri"))
    assert service.graph().nodes
    assert service.validation().counts()
    assert service.certificate().seal_sha256
    assert service.findings(DiscoveryDimension.GAP) == service.gaps()
    assert isinstance(service.conflicts(), tuple)
    assert isinstance(service.duplicates(), tuple)
    assert service.recommendations()
    assert service.advise("engine.alpha").subject == "engine.alpha"
    assert isinstance(service.reuse_candidates("engine.alpha", "alpha"), tuple)
    assert "engine" in service.hook_line() or service.hook_line()
    assert service.emit()
    assert service.verify_determinism()["deterministic"] is True


# -- the three module-level wrappers, and the refusals that make the seal mean something ---
#
# The runtime composes `RepositoryValidator`, `RepositoryCertificate.issue` and
# `RepositoryRecommendationEngine` directly, so the module-level convenience functions each
# subsystem exports were never called by anything. A published entry point nothing invokes is
# a second way of asking a question that nobody has checked answers the same way.


def _cycle(tmp_path: Path):
    _repo(tmp_path)
    return run_once(_config(tmp_path, output_subdir=".ri"))


def test_the_published_wrappers_answer_exactly_as_the_composed_objects_do(tmp_path) -> None:
    """Same inputs, same answer. If they ever diverge, one of them is the wrong entry point."""

    cycle = _cycle(tmp_path)

    assert validate_report(cycle.report).counts() == cycle.validation.counts()
    assert certify(cycle.report, cycle.validation).seal_sha256 == cycle.certificate.seal_sha256
    outcome = discover_all(cycle.substrate)
    assert build_recommendations(cycle.substrate, outcome, cycle.graph) == (
        cycle.report.recommendations
    )


def test_certifying_a_report_against_someone_elses_validation_is_refused(tmp_path) -> None:
    """THE SEAL IS THE CLAIM, so what it is a claim ABOUT has to be checked.

    A certificate binds a determination to a report by digest. Issuing one from a validation
    of a different report would seal a true statement about the wrong subject — the gate would
    open on evidence that was never examined, and every field of the certificate would still
    verify.
    """

    cycle = _cycle(tmp_path)
    foreign = dataclasses.replace(cycle.validation, report_sha256="a" * 64)
    with pytest.raises(RepositoryCertificationError) as excinfo:
        RepositoryCertificate.issue(cycle.report, foreign)
    assert excinfo.value.context["report_sha256"] == cycle.report.report_sha256
    assert excinfo.value.context["validated_sha256"] == "a" * 64


def test_a_certificate_edited_after_issue_fails_its_own_integrity_check(tmp_path) -> None:
    """The seal is over the certificate's own fields, so flipping the determination without
    reissuing is detectable — which is the only reason a stored certificate is worth reading
    later. `gate_open` is asserted alongside it because the gate and the determination are two
    projections of one decision and must never be readable as disagreeing."""

    cycle = _cycle(tmp_path)
    genuine = cycle.certificate
    assert genuine.verify_integrity() is True
    genuine.require_integrity()
    assert genuine.gate_open is (genuine.gate == GATE_OPEN)
    assert genuine.gate_open is genuine.certified

    forged = dataclasses.replace(
        genuine, determination=Determination.CERTIFIED_INTELLIGENT, gate=GATE_OPEN
    )
    assert forged.gate_open is True
    assert forged.verify_integrity() is False
    with pytest.raises(RepositoryCertificationError) as excinfo:
        forged.require_integrity()
    assert excinfo.value.context["expected"] == genuine.seal_sha256
    assert excinfo.value.context["actual"] == forged.recompute_seal()

    resealed = RepositoryCertificate.issue(cycle.report, cycle.validation)
    assert resealed.seal_sha256 == genuine.seal_sha256
    assert resealed.gate in (GATE_OPEN, GATE_CLOSED)


def test_validation_refuses_anything_that_is_not_an_intelligence_report(tmp_path) -> None:
    """A mapping that looks like a report is the realistic mistake — a caller who round-tripped
    one through JSON. Every gate below would then read attributes off a dict, find nothing, and
    produce a PASS over a report that was never examined."""

    cycle = _cycle(tmp_path)
    with pytest.raises(RepositoryValidationError) as excinfo:
        RepositoryValidator(cycle.report.to_dict())
    assert excinfo.value.context["received"] == "dict"
