"""UCOS-COV-SCOPE-001, under Ω-1 — the coverage denominator is DERIVED, and the derivation is total.

WHAT THIS FILE USED TO BE, AND WHY IT WAS NOT ENOUGH.

It governed two hand-written lists. ``addopts`` carried 78 ``--cov=`` flags, ``[tool.coverage.run]
source`` carried 78 paths, and this control refused a disagreement between them or an omission from
both. That was a real improvement over nothing, and it caught real defects. It also had the defect
of its own kind, twice over, and the second time is the one that mattered:

    SOURCE_TREES = ("engine", "platform")

Every question this file asked was scoped by that tuple, so a top-level tree that was neither was
not a possibility the control REFUSED — it was a question the control never ASKED. Five existed.
They carried 35,333 statements and 4,121 passing tests, four of the five had test roots that no
``testpaths`` entry collected, and every test in this file passed throughout. The fix at the time
was to add a second control and a second enumeration predicate, which bought correctness for the
sixth tree and nothing for the seventh.

Then ``_top_level_packages`` was keyed on ``__init__.py``, and ``engine/recursive_knowledge`` — a
PEP 420 namespace directory with sixteen modules, 2,849 statements, a live gate, a ``verify.sh``
stage, a workflow and a 135-test suite — was invisible to it. And ``scripts/``, 281 statements, was
in no list at all and was found by discovery on its first run.

WHAT THIS FILE IS NOW. The lists are gone. ``engine/universal_discovery`` derives the denominator
and the collection set from ``git ls-files '*.py'``, and this control governs the DERIVATION:

  * that it is total — no source package is measured by neither the derivation nor an exemption;
  * that it is honest — no exemption is stale, and every one carries a reason;
  * that it is not vacuous — the specific historical misses are pinned BY NAME, so restoring any
    of the old predicates fails a test that says which defect it reintroduced;
  * and that it is UNBOUNDED, which is the Ω-1 success criterion and is proved by experiment:
    ``test_a_tree_that_does_not_exist_yet_is_already_governed`` builds five top-level trees nobody
    has ever registered and measures that discovery governs all five with zero configuration.

WHAT IS STILL DECLARED, AND WHY THAT IS NOT A REGRESSION. ``[tool.ucos.coverage_scope]``
``excluded_packages`` remains, and must. Ω-5 permits an artifact to sit outside measurement only
under a disposition that STATES a reason; a silent exclusion is the defect and an arguable one is
the remedy. It is a register of judgements, not an enumeration of what exists — which is why a
stale entry is refused in both directions below.
"""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path
from typing import Any

import pytest

from engine.universal_discovery import discovery, graph
from engine.universal_discovery.model import OmegaError

REPO = Path(__file__).resolve().parents[2]
PYPROJECT = REPO / "pyproject.toml"


@pytest.fixture(scope="module")
def config() -> dict[str, Any]:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def derived() -> tuple[tuple[str, ...], tuple[str, ...], dict[str, str]]:
    """``(measurable packages, test roots, declared exemptions)`` — computed, never read.

    Module-scoped because the derivation walks 2,177 files and parses every one of them; asking it
    once per test would make this file the slowest in the suite for no additional truth.
    """
    paths = discovery.tracked_python(str(REPO))
    import_graph = graph.ImportGraph(str(REPO), paths)
    test_roots = discovery.derive_test_roots(paths, graph.imported_by_path(import_graph, paths))
    exemptions, _transient = discovery.read_declared(str(REPO))
    packages = discovery.derive_measurable_packages(paths, test_roots, exemptions=exemptions)
    return packages, test_roots, exemptions


def _packages_present(paths: tuple[str, ...], test_roots: tuple[str, ...]) -> set[str]:
    """Every source package the tree actually holds — an INDEPENDENT oracle, not the derivation.

    NO TREE LIST, and that absence is the whole point. The predicate is "a tracked ``.py`` file at
    any depth under an importable root, outside a discovered test root", which is strictly wider
    than ``__init__.py`` (so PEP 420 namespace directories are seen) and strictly narrower than the
    filesystem (so untracked debris is not).

    WHY IT DOES NOT CALL ``derive_measurable_packages``, WHICH WOULD BE SHORTER. It used to, with
    ``exemptions={}``, and that made ``test_every_source_package_is_measured_or_declared_exempt``
    TRUE BY CONSTRUCTION: the derivation with no exemptions minus the derivation with them is a
    subset of the exemptions, always, whatever either one computes. The control read as the
    strongest test in this file and asked nothing. A control over a derivation needs a second
    opinion the derivation cannot influence, which is the same reason ``ukctx_verify.py`` does not
    import ``ukctx.py`` — a verifier sharing its subject's implementation agrees with it uniformly,
    including where it is uniformly wrong (MB7). This re-derivation is that second opinion, and it
    is not the duplication UCKP-ART-03 voids: it authors no knowledge and holds no authority over
    the denominator, it only observes the tree the denominator claims to cover.

    IT IS DELIBERATELY WIDER IN ONE PLACE. ``derive_measurable_packages`` keeps a second-level
    directory only when ``is_importable_name`` admits it; this does not. Python code under a
    directory coverage cannot name is still code that nothing measures, so it must surface as
    unaccounted and be answered — by a declared exemption stating why, or by moving it — rather
    than disappear because the derivation could not have found it. Roots are still filtered, on
    the same predicate the derivation uses, because a non-importable ROOT gives its children no
    dotted name at all.
    """
    from engine.universal_discovery.discovery import is_importable_name

    direct: set[str] = set()  # roots holding modules directly — measured as the root itself
    children: dict[str, set[str]] = {}

    for path in paths:
        if any(path == root or path.startswith(root.rstrip("/") + "/") for root in test_roots):
            continue
        parts = path.split("/")
        if len(parts) < 2 or not is_importable_name(parts[0]):
            continue
        root = parts[0]
        children.setdefault(root, set())
        if len(parts) == 2:
            if parts[1] != "__init__.py":
                direct.add(root)
            continue
        children[root].add(parts[1])

    present: set[str] = set()
    for root, kids in children.items():
        if root in direct:
            present.add(root)
        else:
            present.update(f"{root}.{kid}" for kid in kids)
    return present


# --------------------------------------------------------------- Ω-1: the derivation is installed


def test_the_denominator_is_derived_rather_than_declared(config: dict[str, Any]) -> None:
    """No enumeration of the denominator may survive in configuration, in either of its two homes.

    Both copies are named because both existed and they were reconciled by nobody. If either comes
    back, the repository has two answers to one question again, and the one that is wrong will be
    the one nothing consults.
    """
    ini = config["tool"]["pytest"]["ini_options"]
    flags = [a for a in ini["addopts"] if a.startswith("--cov=")]
    assert not flags, (
        "the coverage denominator is enumerated in addopts again; it is derived by "
        f"engine/universal_discovery and must not be listed: {flags}"
    )
    assert "testpaths" not in ini, (
        "testpaths is declared again; the collection set is derived from which directories hold "
        "suites, and a static list is what left 3,995 passing tests collected by nothing"
    )
    assert "source" not in config["tool"]["coverage"]["run"], (
        "[tool.coverage.run] source is declared again; it was the second of two lists that had to "
        "agree and were reconciled by nobody"
    )


def test_the_derivation_is_actually_wired_into_the_test_run(config: dict[str, Any]) -> None:
    """A derivation nothing invokes is a library, not a control.

    This is the non-vacuity guard for the whole file: every test below could pass while the suite
    itself measured nothing, if the plugin were simply not loaded.
    """
    addopts = config["tool"]["pytest"]["ini_options"]["addopts"]
    assert "engine.universal_discovery.pytest_scope" in addopts, (
        "the scope-injection plugin is not in addopts, so pytest-cov receives no derived "
        "denominator and coverage would measure whatever it happened to import"
    )
    assert (
        addopts[addopts.index("engine.universal_discovery.pytest_scope") - 1] == "-p"
    ), "the plugin name appears in addopts but not as the value of -p, so it is not loaded"


# ------------------------------------------------------------------ Ω-1: the derivation is total


def test_every_source_package_is_measured_or_declared_exempt(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """The whole control. A third possibility is what let 4,580 statements go unmeasured."""
    packages, test_roots, exemptions = derived
    paths = discovery.tracked_python(str(REPO))
    unaccounted = sorted(_packages_present(paths, test_roots) - set(packages) - set(exemptions))
    assert not unaccounted, (
        "these packages are neither in the derived denominator nor declared exempt, so they are "
        f"outside the coverage measurement and nothing says why: {unaccounted}"
    )


def test_the_derived_scope_names_only_packages_that_exist(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """A denominator entry measuring nothing reads as measurement and contributes none."""
    packages, test_roots, _exemptions = derived
    paths = discovery.tracked_python(str(REPO))
    ghosts = sorted(set(packages) - _packages_present(paths, test_roots))
    assert not ghosts, f"the derived denominator names packages absent from the tree: {ghosts}"


def test_no_declared_exemption_is_stale(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """An excuse that stops being true is a refusal, so the register cannot rot into a blanket."""
    packages, test_roots, exemptions = derived
    paths = discovery.tracked_python(str(REPO))
    present = _packages_present(paths, test_roots)
    for package, reason in exemptions.items():
        assert package in present, (
            f"{package} is declared exempt from coverage but is not present in the tree; the "
            "exemption is stale and must be withdrawn"
        )
        assert package not in set(packages), (
            f"{package} is declared exempt AND appears in the derived denominator; the exemption "
            "is stale in the other direction and must be withdrawn"
        )
        assert reason.strip(), f"{package} is exempt with no stated reason"


def test_every_discovered_test_root_has_its_code_in_the_denominator(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """Collecting a layer's tests while excluding its code raises the ratio and measures nothing.

    This is the pairing Rule 1 of the closure mandate names as a defect, and it is the exact state
    ``intelligence/`` was left in for the interval between UCOS-CL-008 and UCI-000001. Under Ω-1 it
    cannot recur by omission, because both sides of the pairing come from one derivation — so this
    test now guards the DERIVATION rather than two lists.
    """
    packages, test_roots, exemptions = derived
    unpaired = []
    for test_root in test_roots:
        layer = test_root.split("/", 1)[0]
        if any(p == layer or p.startswith(layer + ".") for p in packages):
            continue
        if any(e == layer or e.startswith(layer + ".") for e in exemptions):
            continue
        unpaired.append(test_root)
    assert not unpaired, (
        "these test roots are collected but the code they exercise is in no measurement, so "
        f"running them raises no measured coverage: {unpaired}"
    )


def test_the_denominator_is_not_vacuous(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """A denominator over nothing reports 100% forever. The degenerate case, refused."""
    packages, _test_roots, _exemptions = derived
    assert len(packages) > 1, (
        f"the derived denominator holds {len(packages)} packages; a measurement over one package "
        "is not a measurement of this repository"
    )


# ------------------------------------------------- Ω-1 SUCCESS CRITERION, discharged by experiment


def _git(repository: Path, *arguments: str) -> None:
    subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", *arguments],  # noqa: S607 - git from PATH by design
        cwd=repository,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def unregistered_trees(tmp_path: Path) -> Path:
    """A repository holding five top-level trees that no configuration anywhere mentions.

    Built as a real git repository because the discovery boundary is ``git ls-files`` and a
    filesystem-only fixture would test a code path the gate does not use. Each tree carries the
    shapes that historically defeated enumeration: a namespace package with no ``__init__.py``, a
    layer holding modules directly, a suite whose helper carries no ``test_`` prefix.
    """
    repository = tmp_path / "unbounded"
    (repository / "quantum" / "entanglement").mkdir(parents=True)
    (repository / "quantum" / "entanglement" / "state.py").write_text("X = 1\n")
    (repository / "quantum" / "tests").mkdir(parents=True)
    (repository / "quantum" / "tests" / "test_state.py").write_text("def test_x():\n    pass\n")
    (repository / "quantum" / "tests" / "helpers.py").write_text("def build():\n    return 1\n")

    (repository / "mars").mkdir(parents=True)
    (repository / "mars" / "__init__.py").write_text("")
    (repository / "mars" / "habitat.py").write_text("Y = 2\n")

    for name in ("civilization", "planetary", "interstellar"):
        (repository / name / "core").mkdir(parents=True)
        (repository / name / "core" / "engine.py").write_text(f"NAME = {name!r}\n")

    (repository / "pyproject.toml").write_text("[tool.ucos]\n")
    _git(repository, "init", "-q")
    _git(repository, "add", "-A")
    return repository


def test_a_tree_that_does_not_exist_yet_is_already_governed(unregistered_trees: Path) -> None:
    """Ω-1's success criterion: 0 code changes, 0 configuration changes, 0 registration.

    Five top-level trees are created in a repository whose configuration is an empty table. No
    file in this repository mentions ``quantum``, ``mars``, ``civilization``, ``planetary`` or
    ``interstellar``. Discovery must nonetheless place every one of them inside the denominator and
    collect its suite — using exactly the code that ships, with no edit and no registration.

    THIS IS THE TEST THE OLD CONTROL COULD NOT HAVE PASSED. ``SOURCE_TREES = ("engine",
    "platform")`` would have returned an empty answer for all five, and the assertion that would
    have caught it did not exist because the possibility had no name.
    """
    root = str(unregistered_trees)
    paths = discovery.tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    test_roots = discovery.derive_test_roots(paths, graph.imported_by_path(import_graph, paths))
    packages = discovery.derive_measurable_packages(paths, test_roots)

    assert set(discovery.derive_roots(paths)) == {
        "civilization",
        "interstellar",
        "mars",
        "planetary",
        "quantum",
    }, "discovery did not find every tracked top-level tree"

    # A tree holding sub-packages is measured per sub-package; a tree holding modules directly is
    # measured whole. Both shapes appear here, and both are derived rather than configured.
    assert "quantum.entanglement" in packages, (
        "a namespace sub-package with no __init__.py is outside the derived denominator — the "
        "engine/recursive_knowledge defect, reintroduced"
    )
    assert "mars" in packages, "a layer holding modules directly is outside the denominator"
    for name in ("civilization", "planetary", "interstellar"):
        assert f"{name}.core" in packages, f"{name} is outside the derived denominator"

    assert test_roots == (
        "quantum/tests",
    ), f"the suite of an unregistered tree was not discovered: {test_roots}"
    assert (
        "quantum.tests" not in packages
    ), "a suite entered the coverage denominator, which would let tests raise their own coverage"


def test_the_experiment_is_not_passing_by_accident(unregistered_trees: Path) -> None:
    """NON-VACUITY for the criterion above: no configuration in the fixture names any tree.

    Without this, the previous test could be passing because the fixture quietly registered what it
    then claimed was discovered — which is exactly the shape of the defect being fixed.
    """
    declared = (unregistered_trees / "pyproject.toml").read_text(encoding="utf-8")
    for name in ("quantum", "mars", "civilization", "planetary", "interstellar"):
        assert name not in declared, f"the fixture registers {name}, so discovery proved nothing"
    assert "cov" not in declared and "testpaths" not in declared


def test_this_repository_names_none_of_the_five_trees_anywhere() -> None:
    """The criterion asserted against the REAL repository's own configuration and orchestration.

    The experiment above runs in a temporary tree, which proves the derivation is general. This
    proves the complementary half: nothing in THIS repository's configuration, build or CI mentions
    ``quantum``, ``mars``, ``planetary`` or ``interstellar``, so when those trees were created here
    and measured — 20 artifacts, every one classified, every one owned, all five suites collected
    and passing under the bare ``pytest`` invocation — no registration made it happen.

    ``civilization`` is deliberately absent from the list: ``engine/civilization`` is a real package
    in this repository, so the token legitimately appears and asserting otherwise would be a test
    that fails for the wrong reason.
    """
    governance_texts = [
        REPO / "pyproject.toml",
        REPO / "Makefile",
        REPO / "verify.sh",
        *sorted((REPO / ".github" / "workflows").glob("*.yml")),
    ]
    for name in ("quantum", "mars", "planetary", "interstellar"):
        for path in governance_texts:
            body = path.read_text(encoding="utf-8", errors="surrogateescape")
            # The proof narrative names the trees in prose; a REGISTRATION would name them in a
            # scope list, a testpath, a --cov flag or a make target. Only the latter would falsify
            # the criterion, so the assertion is over declarations rather than over the word.
            for line in body.splitlines():
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith("//"):
                    continue
                assert f'"{name}"' not in line and f"--cov={name}" not in line, (
                    f"{path.name} registers {name!r} outside a comment, so the Ω-1 criterion "
                    f"'0 configuration changes' is no longer what is being measured: {line.strip()}"
                )


# ------------------------------------------------------------------------------- NON-VACUITY
# Every guard above is forged into failure, and every historical miss is pinned BY NAME so that
# restoring an old predicate fails a test that says which defect it brought back.


def test_a_namespace_package_is_counted_as_present(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """The ``__init__.py``-keyed predicate, pinned. 2,849 statements were invisible to it."""
    packages, _test_roots, _exemptions = derived
    assert "engine.recursive_knowledge" in packages, (
        "engine/recursive_knowledge is a directory of tracked modules and must be in the derived "
        "denominator whether or not it carries an __init__.py; enumeration keyed on __init__.py "
        "is what put 2,849 statements outside the measurement"
    )
    assert not (REPO / "engine" / "recursive_knowledge" / "__init__.py").exists(), (
        "engine/recursive_knowledge has acquired an __init__.py, so it is no longer evidence that "
        "namespace packages are discovered; point this test at another namespace package or "
        "withdraw it, but do not let it pass vacuously"
    )


def test_the_enforcement_closure_programme_is_inside_the_denominator(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """The original self-exemption: the closure programme, outside the measurement it imposes."""
    packages, _test_roots, _exemptions = derived
    assert "engine.enforcement_closure" in packages


def test_the_five_late_layers_are_inside_the_denominator(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """The ``SOURCE_TREES`` defect, pinned by name rather than described.

    These five were outside a denominator scoped to ``engine`` and ``platform``. They are named
    here so that narrowing the derivation back to two trees fails a test that says so, instead of
    quietly reproducing the state in which 35,333 statements were unmeasured.
    """
    packages, _test_roots, _exemptions = derived
    for layer in ("application", "data", "infrastructure", "intelligence", "service"):
        assert layer in packages, f"{layer} has left the derived denominator"


def test_the_tooling_root_discovery_found_is_inside_the_denominator(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """``scripts/`` was in NO list — not addopts, not source, not testpaths, not an exemption.

    It was found by the first run of discovery, which is the clearest single piece of evidence that
    a derived denominator sees what an enumerated one cannot. 281 statements.
    """
    packages, _test_roots, _exemptions = derived
    assert "scripts" in packages, (
        "scripts/ has left the derived denominator; it is the root that no enumeration ever "
        "contained and its presence is what proves discovery is wider than the lists it replaced"
    )


def test_a_suite_helper_is_not_measured_as_source(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """The eighteen helpers with no ``test_`` prefix, pinned.

    A naming-keyed test-root predicate declared ``platform/tests`` and ``engine/tests`` to be
    source, which would put 234 test modules into the coverage denominator and let the suite raise
    its own coverage by growing. The import relation is what answers correctly, so this test also
    pins the reason ``derive_test_roots`` takes a graph at all.
    """
    packages, test_roots, _exemptions = derived
    assert (
        "platform.tests" not in packages and "engine.tests" not in packages
    ), "a test tree entered the coverage denominator"
    assert "platform/tests" in test_roots and "engine/tests" in test_roots
    assert (REPO / "platform" / "tests" / "_coverage_helpers.py").exists(), (
        "the helper this test is pinned to is gone; repoint it at another suite module carrying no "
        "test_ prefix, or withdraw it, but do not let it pass vacuously"
    )


def test_untracked_debris_does_not_enter_the_denominator(
    derived: tuple[tuple[str, ...], tuple[str, ...], dict[str, str]],
) -> None:
    """A guard whose verdict depends on local state gets suppressed, and measures nothing."""
    packages, _test_roots, _exemptions = derived
    tracked = discovery.tracked_python(str(REPO))
    roots_with_tracked_python = {p.split("/", 1)[0] for p in tracked if "/" in p}
    stray = sorted(p for p in packages if p.split(".", 1)[0] not in roots_with_tracked_python)
    assert not stray, (
        "the derived denominator names a package git does not track, so its verdict depends on "
        f"local state: {stray}"
    )


def test_an_empty_population_is_refused(tmp_path: Path) -> None:
    """The degenerate world. Every Ω invariant is true over it, so it must be a FAULT.

    This is the single most dangerous defect the discovery layer could have: an empty answer would
    convert "this repository is ungoverned" into "this repository is fully governed".
    """
    empty = tmp_path / "empty"
    empty.mkdir()
    _git(empty, "init", "-q")
    with pytest.raises(OmegaError, match="empty population"):
        discovery.tracked_python(str(empty))


def test_a_repository_git_does_not_track_is_refused(tmp_path: Path) -> None:
    """Not a git work tree at all — refused rather than answered from the filesystem."""
    with pytest.raises(
        OmegaError, match="could not be read from the tracked-content provider|empty population"
    ):
        discovery.tracked_python(str(tmp_path / "absent"))


def test_a_denominator_emptied_by_exemptions_is_refused() -> None:
    """Exempting everything would report a perfect percentage over nothing."""
    paths = ("alpha/beta/module.py", "alpha/tests/test_module.py")
    with pytest.raises(OmegaError, match="computed over nothing|empty"):
        discovery.derive_measurable_packages(
            paths, ("alpha/tests",), exemptions={"alpha.beta": "everything"}
        )


def test_an_exemption_without_a_reason_is_refused(tmp_path: Path) -> None:
    """A reason is what makes an exemption arguable rather than merely present."""
    (tmp_path / "pyproject.toml").write_text(
        '[tool.ucos.coverage_scope]\nexcluded_packages = [{ package = "a.b", reason = "   " }]\n',
        encoding="utf-8",
    )
    with pytest.raises(OmegaError, match="no reason"):
        discovery.read_declared(str(tmp_path))


def test_a_repository_with_no_suite_is_refused_at_the_gate(tmp_path: Path) -> None:
    """The suite fault lives where a REPOSITORY is governed, and it must still fire there.

    Moving it out of ``derive_test_roots`` made the primitive composable; this test is what stops
    that from having quietly removed the refusal altogether.
    """
    with pytest.raises(OmegaError, match="invisible to discovery"):
        discovery.assert_suite_exists(())


def test_a_directory_called_tests_that_holds_source_is_not_dropped(tmp_path: Path) -> None:
    """The mirror-image defect of the one above, and the reason the predicate reads no names.

    A name-keyed rule would omit any directory called ``tests`` from the denominator, which is a
    free way to retire coverage debt: move code into ``tests/`` and it stops being measured. The
    derived rule asks whether the directory's contents belong to a suite, so production code
    sitting under that name stays measured.
    """
    repository = tmp_path / "misnamed"
    (repository / "layer" / "tests").mkdir(parents=True)
    (repository / "layer" / "tests" / "production.py").write_text("VALUE = 1\n")
    (repository / "layer" / "consumer.py").write_text("from layer.tests.production import VALUE\n")
    (repository / "pyproject.toml").write_text("[tool.ucos]\n")
    _git(repository, "init", "-q")
    _git(repository, "add", "-A")

    root = str(repository)
    paths = discovery.tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    test_roots = discovery.derive_test_roots(paths, graph.imported_by_path(import_graph, paths))
    assert (
        test_roots == ()
    ), f"a directory named tests holding production code was treated as a suite: {test_roots}"
    assert "layer" in discovery.derive_measurable_packages(paths, test_roots), (
        "production code under a directory called tests left the denominator, which would make "
        "renaming a directory a way to retire coverage debt"
    )
