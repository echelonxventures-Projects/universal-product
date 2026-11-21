"""Ω-1 — the population is discovered, and every derivation is a property rather than a name."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from engine.universal_discovery import discovery, graph
from engine.universal_discovery.model import OmegaError

from .conftest import git


def _roots_and_packages(repository: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    root = str(repository)
    paths = discovery.tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    test_roots = discovery.derive_test_roots(paths, graph.imported_by_path(import_graph, paths))
    return test_roots, discovery.derive_measurable_packages(paths, test_roots)


# ------------------------------------------------------------------------------ the population


def test_the_population_is_git_and_untracked_files_are_invisible(
    make_repo: Callable[..., Path],
) -> None:
    """The boundary that keeps a verdict from depending on a developer's working copy."""
    repository = make_repo({"alpha/module.py": "X = 1\n"})
    (repository / "alpha" / "debris.py").write_text("Y = 2\n", encoding="utf-8")

    paths = discovery.tracked_python(str(repository))
    assert paths == ("alpha/module.py",), (
        "an untracked file entered the population, so this control's verdict is a function of "
        f"local state: {paths}"
    )


def test_an_empty_population_is_a_fault_and_not_a_pass(tmp_path: Path) -> None:
    """The most dangerous defect available here: "ungoverned" rendering as "fully governed"."""
    empty = tmp_path / "empty"
    empty.mkdir()
    git(empty, "init", "-q")
    with pytest.raises(OmegaError, match="empty population"):
        discovery.tracked_python(str(empty))


def test_a_missing_work_tree_raises_rather_than_answering(tmp_path: Path) -> None:
    with pytest.raises(
        OmegaError, match="could not be read from the tracked-content provider|empty population"
    ):
        discovery.tracked_python(str(tmp_path / "nowhere"))


def test_non_python_tracked_files_are_not_in_the_population(
    make_repo: Callable[..., Path],
) -> None:
    repository = make_repo({"alpha/module.py": "X = 1\n", "alpha/data.json": "{}\n"})
    assert discovery.tracked_python(str(repository)) == ("alpha/module.py",)


# ----------------------------------------------------------------------------------- the roots


def test_roots_are_derived_from_whatever_exists(layered_repo: Path) -> None:
    paths = discovery.tracked_python(str(layered_repo))
    assert discovery.derive_roots(paths) == ("00-GOV", "alpha", "beta")


def test_a_repository_root_module_is_attributed_to_a_real_root(
    make_repo: Callable[..., Path],
) -> None:
    """A file with no directory segment is a root with an authority, not a case to skip."""
    repository = make_repo({"toplevel.py": "X = 1\n", "alpha/module.py": "Y = 2\n"})
    paths = discovery.tracked_python(str(repository))
    assert "" in discovery.derive_roots(paths)


def test_importability_is_the_language_rule_and_not_a_taste(layered_repo: Path) -> None:
    """``00-GOV`` is refused as a coverage source because Python could not name it, full stop."""
    paths = discovery.tracked_python(str(layered_repo))
    roots = discovery.derive_roots(paths)
    assert discovery.derive_importable_roots(roots) == ("alpha", "beta")
    assert discovery.is_importable_name("quantum")
    assert not discovery.is_importable_name("00-MASTER")
    assert not discovery.is_importable_name("__dunder__")
    assert not discovery.is_importable_name("has-a-dash")


# ------------------------------------------------------------------------------- the test roots


def test_a_test_root_collapses_to_its_shallowest_directory(layered_repo: Path) -> None:
    test_roots, _packages = _roots_and_packages(layered_repo)
    assert test_roots == ("alpha/tests", "beta/tests")


def test_a_suite_helper_with_no_test_prefix_is_still_a_suite_member(
    layered_repo: Path,
) -> None:
    """The eighteen-helper defect, in miniature. ``support.py`` must not make its tree source."""
    test_roots, packages = _roots_and_packages(layered_repo)
    assert "alpha/tests" in test_roots
    assert "alpha.tests" not in packages, (
        "a suite entered the coverage denominator because one of its helpers carried no test_ "
        "prefix — the defect that would have measured 234 test modules as product"
    )


def test_a_layer_whose_only_consumer_is_its_own_suite_is_not_a_suite(
    make_repo: Callable[..., Path],
) -> None:
    """The measured counter-example that rejected the looser predicate.

    ``service``, ``data``, ``application`` and ``infrastructure`` have zero inbound imports from
    anywhere else in the real repository. Under "nothing outside this DIRECTORY imports it", all
    four were classified as test trees and 29,970 statements left the denominator. The locality
    requirement — the module's own directory must hold test modules — is what separates them.
    """
    repository = make_repo(
        {
            "layer/__init__.py": "",
            "layer/product.py": "def run():\n    return 1\n",
            "layer/tests/test_product.py": (
                "from layer.product import run\n\n\ndef test_run():\n" "    assert run() == 1\n"
            ),
        }
    )
    test_roots, packages = _roots_and_packages(repository)
    assert test_roots == ("layer/tests",)
    assert "layer" in packages, (
        "a self-contained layer was swallowed as a test tree, which is how 29,970 statements "
        "would leave the denominator"
    )


def test_a_directory_called_tests_that_holds_source_is_not_a_suite(
    make_repo: Callable[..., Path],
) -> None:
    """The mirror defect: renaming a directory must not be a way to retire coverage debt."""
    repository = make_repo(
        {
            "layer/tests/production.py": "VALUE = 1\n",
            "layer/consumer.py": "from layer.tests.production import VALUE\n",
        }
    )
    test_roots, packages = _roots_and_packages(repository)
    assert test_roots == ()
    assert "layer" in packages


def test_a_suite_kept_somewhere_other_than_tests_is_still_discovered(
    make_repo: Callable[..., Path],
) -> None:
    """The predicate reads contents, so a tree that calls its suite ``checks`` is collected."""
    repository = make_repo(
        {
            "layer/product.py": "X = 1\n",
            "layer/checks/test_product.py": "def test_x():\n    pass\n",
        }
    )
    test_roots, _packages = _roots_and_packages(repository)
    assert test_roots == ("layer/checks",)


def test_a_trailing_test_suffix_is_collected_too(make_repo: Callable[..., Path]) -> None:
    repository = make_repo(
        {
            "layer/product.py": "X = 1\n",
            "layer/spec/module_test.py": "def test_x():\n    pass\n",
        }
    )
    test_roots, packages = _roots_and_packages(repository)
    assert test_roots == ("layer/spec",)
    assert packages == ("layer",)


def test_a_root_holding_nothing_but_a_suite_collapses_to_the_root(
    make_repo: Callable[..., Path],
) -> None:
    """Maximality taken to its conclusion, and it is the correct answer rather than an edge case.

    If a whole tree is nothing but tests, the tree IS the suite, and collecting it once beats
    collecting each of its sub-directories. The real repository never reaches this state because
    ``engine`` and ``platform`` hold source beside their suites, which is what stops the collapse
    one level too high.
    """
    repository = make_repo(
        {
            "product/module.py": "X = 1\n",
            "suite/unit/test_a.py": "def test_a():\n    pass\n",
            "suite/integration/test_b.py": "def test_b():\n    pass\n",
        }
    )
    test_roots, packages = _roots_and_packages(repository)
    assert test_roots == ("suite",)
    assert packages == ("product",)


def test_a_repository_with_no_suite_is_refused_where_a_repository_is_governed() -> None:
    with pytest.raises(OmegaError, match="invisible to discovery"):
        discovery.assert_suite_exists(())
    discovery.assert_suite_exists(("alpha/tests",))


# --------------------------------------------------------------------- the measurable packages


def test_the_two_measurement_shapes_are_chosen_by_measurement(layered_repo: Path) -> None:
    """A tree of sub-packages is measured per sub-package; a tree of modules is measured whole.

    This is precisely the distinction the 78-entry hand-written list encoded by hand, and getting
    it wrong in either direction is a real defect: naming the root of ``alpha`` would pull
    ``alpha/tests`` into the denominator through the package graph, and naming sub-packages of
    ``beta`` would leave ``beta/module.py`` unmeasured.
    """
    _test_roots, packages = _roots_and_packages(layered_repo)
    assert packages == ("alpha.core", "alpha.namespaced", "beta")


def test_a_namespace_package_with_no_init_is_measured(layered_repo: Path) -> None:
    """PEP 420. ``alpha/namespaced`` has no ``__init__.py`` and carries 2,849 statements' worth of
    precedent: ``engine/recursive_knowledge`` was invisible to the ``__init__.py`` predicate."""
    _test_roots, packages = _roots_and_packages(layered_repo)
    assert "alpha.namespaced" in packages
    assert not (layered_repo / "alpha" / "namespaced" / "__init__.py").exists()


def test_a_non_importable_root_never_enters_the_denominator(layered_repo: Path) -> None:
    _test_roots, packages = _roots_and_packages(layered_repo)
    assert not any(p.startswith("00-GOV") for p in packages)


def test_an_exemption_removes_exactly_its_subtree(layered_repo: Path) -> None:
    root = str(layered_repo)
    paths = discovery.tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    test_roots = discovery.derive_test_roots(paths, graph.imported_by_path(import_graph, paths))
    packages = discovery.derive_measurable_packages(
        paths, test_roots, exemptions={"alpha.core": "declared"}
    )
    assert "alpha.core" not in packages
    assert "alpha.namespaced" in packages and "beta" in packages


def test_exempting_everything_is_refused() -> None:
    with pytest.raises(OmegaError, match="a number about nothing"):
        discovery.derive_measurable_packages(
            ("alpha/beta/module.py",), (), exemptions={"alpha.beta": "all of it"}
        )


# ----------------------------------------------------------------------------- module identity


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("engine/foundation/identity.py", "engine.foundation.identity"),
        ("engine/foundation/__init__.py", "engine.foundation"),
        ("scripts/tool.py", "scripts.tool"),
        ("00-MASTER/UCI-000001/uci_engine.py", ""),
        ("engine/has-a-dash/mod.py", ""),
        ("notpython.txt", ""),
    ],
)
def test_module_identity_is_path_independent_or_absent(path: str, expected: str) -> None:
    """Returns "" rather than guessing, so no verdict can depend on a name Python cannot import."""
    assert discovery.module_dotted(path) == expected


# ------------------------------------------------------------------------- the declared inputs


def test_declared_inputs_are_read_with_their_reasons(make_repo: Callable[..., Path]) -> None:
    repository = make_repo(
        {"alpha/module.py": "X = 1\n"},
        pyproject=(
            "[tool.ucos.coverage_scope]\n"
            'excluded_packages = [{ package = "alpha.dead", reason = "retired" }]\n'
            "[tool.ucos.omega]\n"
            'transient = [{ path = "alpha/scratch.py", reason = "generated in-run" }]\n'
        ),
    )
    exemptions, transient = discovery.read_declared(str(repository))
    assert exemptions == {"alpha.dead": "retired"}
    assert transient == {"alpha/scratch.py": "generated in-run"}


@pytest.mark.parametrize(
    "table",
    [
        '[tool.ucos.coverage_scope]\nexcluded_packages = [{ package = "a.b", reason = "  " }]\n',
        '[tool.ucos.omega]\ntransient = [{ path = "a/b.py", reason = "" }]\n',
    ],
)
def test_a_declaration_with_no_reason_is_refused(
    make_repo: Callable[..., Path], table: str
) -> None:
    """A reason is what makes an exemption arguable rather than merely present."""
    repository = make_repo({"alpha/module.py": "X = 1\n"}, pyproject=table)
    with pytest.raises(OmegaError, match="no reason"):
        discovery.read_declared(str(repository))


def test_an_unreadable_declaration_is_a_fault(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("this is not = valid = toml\n", encoding="utf-8")
    with pytest.raises(OmegaError, match="unreadable"):
        discovery.read_declared(str(tmp_path))


def test_absent_declarations_are_empty_rather_than_a_fault(
    make_repo: Callable[..., Path],
) -> None:
    """No declaration is a legitimate state: it means nothing has been argued for."""
    repository = make_repo({"alpha/module.py": "X = 1\n"})
    assert discovery.read_declared(str(repository)) == ({}, {})


def test_frozen_prefixes_come_from_the_guard_that_owns_the_question() -> None:
    """ARCHIVED tracks the DP-03 guard, so the two cannot drift apart."""
    from engine.foundation.guards.frozen_paths import FROZEN_PREFIXES

    derived = discovery.frozen_prefixes(".")
    assert derived
    assert set(derived) == {p.rstrip("/") + "/" for p in FROZEN_PREFIXES}


def test_a_guard_that_freezes_nothing_is_a_fault_rather_than_an_empty_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ARCHIVED would be vacuous, and a vacuous disposition reports a pass it did not earn.

    The guard is read at call time — ``frozen_prefixes`` imports ``FROZEN_PREFIXES`` inside its
    own body precisely so the answer tracks the declaration rather than a value captured at
    import. Emptying the declaration is therefore the honest way to reach this refusal, and it
    is the state a future edit that removes the last frozen tree would actually produce.
    """
    from engine.foundation.guards import frozen_paths

    monkeypatch.setattr(frozen_paths, "FROZEN_PREFIXES", ())
    with pytest.raises(OmegaError, match="ARCHIVED would be vacuous"):
        discovery.frozen_prefixes(".")


def test_a_sub_directory_python_could_not_import_never_becomes_a_package(
    make_repo: Callable[..., Path],
) -> None:
    """``alpha/00-GOV/engine.py`` is tracked, importable-rooted, and nameable by no source.

    The root passes ``is_importable_name`` so the root-level filter admits it, and then the
    SECOND segment fails the same rule. Without this test the branch that drops it reads as
    dead: every sub-directory in the fixtures happens to be an identifier, so the denominator
    would have been identical whether the check existed or not — and a check that cannot change
    an answer is indistinguishable from one that has been deleted.
    """
    repository = make_repo(
        {
            "alpha/core/service.py": "X = 1\n",
            "alpha/00-GOV/engine.py": "Y = 2\n",
            "alpha/tests/test_service.py": "def test_x():\n    pass\n",
        }
    )
    paths = discovery.tracked_python(str(repository))
    packages = discovery.derive_measurable_packages(paths, ("alpha/tests",))
    assert "alpha.core" in packages
    assert not any("00-GOV" in package for package in packages)


def test_the_derivation_cache_can_be_dropped_by_a_caller_that_changed_the_tree() -> None:
    """The cache is keyed on the ROOT and the population cannot change inside one process run —
    unless a caller mutates the tree, which is what this escape hatch exists for. A cache with
    no way to be dropped would make the Ω suite's own fixtures unable to re-derive."""
    discovery.derived_scope(".")
    assert discovery._DERIVED_SCOPE
    discovery.clear_derived_scope_cache()
    assert not discovery._DERIVED_SCOPE
