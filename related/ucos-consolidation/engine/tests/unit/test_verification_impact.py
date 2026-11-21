"""Verification Impact Engine tests.

The suite is weighted toward proving the engine **fails wide**, because that is the
property that makes it safe to select verification with. A selector that errs narrow
produces a green run which skipped the affected test, so every test named
``*_escalates_*`` is guarding against the dangerous direction, not the annoying one.
"""

from __future__ import annotations

import json
import runpy

import pytest

from engine.verification_impact import (
    IMPACT_CONTRACT,
    ImpactError,
    ImpactGraph,
    ObjectRecord,
    Scope,
    analyse,
    load_graph,
    plan,
)
from engine.verification_impact.changes import changed_paths, working_tree_changes
from engine.verification_impact.cli import EXIT_BOUNDED, EXIT_ESCALATED, main
from engine.verification_impact.graph import CODE_CLASSES, repo_root


def _record(path: str, cls: str = "EXECUTABLE_OBJECT", deps=(), owner="own") -> ObjectRecord:
    return ObjectRecord(
        path=path,
        universal_id=f"UCOS-X-{abs(hash(path)) % 1000000:06d}",
        object_class=cls,
        owner=owner,
        dependencies=tuple(deps),
        produces=(),
        evidence_class="VALIDATION",
        certification_status="GOVERNED",
        content_hash="deadbeef",
    )


def _graph(*records: ObjectRecord) -> ImpactGraph:
    graph = ImpactGraph()
    for record in records:
        graph.objects[record.path] = record
        graph.owners[record.owner].add(record.path)
        for dep in record.dependencies:
            graph.dependents[dep].add(record.path)
    return graph


# --------------------------------------------------------------------- substrate


def test_the_engine_builds_no_new_graph() -> None:
    assert IMPACT_CONTRACT["builds_new_graph"] is False
    assert IMPACT_CONTRACT["fails_wide"] is True


def test_the_committed_registry_loads_with_real_edges() -> None:
    graph = load_graph()
    assert len(graph.objects) > 4000
    assert len(graph.tests) > 700
    assert len(graph.dependents) > 500


def test_load_fails_closed_on_a_missing_registry(tmp_path) -> None:
    with pytest.raises(ImpactError, match="unreadable"):
        load_graph(str(tmp_path))


def test_load_fails_closed_on_an_empty_registry(tmp_path) -> None:
    target = tmp_path / "00-MASTER" / "UCOS-UGA-001"
    target.mkdir(parents=True)
    (target / "01-EXECUTABLE-OBJECT-REGISTRY.json").write_text(json.dumps({"entries": []}))
    with pytest.raises(ImpactError, match="holds no entries"):
        load_graph(str(tmp_path))


def test_load_fails_closed_when_no_edges_exist(tmp_path) -> None:
    """A registry with objects but no edges cannot answer an impact question."""
    target = tmp_path / "00-MASTER" / "UCOS-UGA-001"
    target.mkdir(parents=True)
    (target / "01-EXECUTABLE-OBJECT-REGISTRY.json").write_text(
        json.dumps({"entries": [{"path": "a.py", "object_class": "EXECUTABLE_OBJECT"}]})
    )
    with pytest.raises(ImpactError, match="no dependency edges"):
        load_graph(str(tmp_path))


def test_malformed_entries_are_skipped_not_fatal(tmp_path) -> None:
    target = tmp_path / "00-MASTER" / "UCOS-UGA-001"
    target.mkdir(parents=True)
    (target / "01-EXECUTABLE-OBJECT-REGISTRY.json").write_text(
        json.dumps(
            {
                "entries": [
                    "not-a-mapping",
                    {"no_path": True},
                    {"path": "b.py", "object_class": "TEST_OBJECT", "dependencies": ["a.py"]},
                ]
            }
        )
    )
    graph = load_graph(str(tmp_path))
    assert graph.tests == ("b.py",)


def test_repo_root_resolves_to_a_real_checkout() -> None:
    import os

    assert os.path.isdir(os.path.join(repo_root(), "00-MASTER"))


def test_code_classes_cover_the_executable_kinds() -> None:
    assert "TEST_OBJECT" in CODE_CLASSES and "EXECUTABLE_OBJECT" in CODE_CLASSES


# --------------------------------------------------------------------- traversal


def test_dependents_are_found_transitively() -> None:
    graph = _graph(
        _record("core.py"),
        _record("mid.py", deps=["core.py"]),
        _record("test_top.py", cls="TEST_OBJECT", deps=["mid.py"]),
    )
    assert graph.dependents_of({"core.py"}) == {"mid.py", "test_top.py"}


def test_direct_only_traversal_stops_at_one_hop() -> None:
    graph = _graph(
        _record("core.py"),
        _record("mid.py", deps=["core.py"]),
        _record("test_top.py", cls="TEST_OBJECT", deps=["mid.py"]),
    )
    assert graph.dependents_of({"core.py"}, transitive=False) == {"mid.py"}


def test_a_dependency_cycle_terminates() -> None:
    """Import cycles exist in real trees; traversal must not spin."""
    graph = _graph(_record("a.py", deps=["b.py"]), _record("b.py", deps=["a.py"]))
    assert graph.dependents_of({"a.py"}) == {"a.py", "b.py"}


def test_ownership_lookup() -> None:
    graph = _graph(_record("x.py", owner="alpha"), _record("y.py", owner="alpha"))
    assert graph.owned_by("alpha") == ("x.py", "y.py")
    assert graph.owned_by("absent") == ()


def test_record_lookup_returns_none_for_an_unknown_path() -> None:
    assert _graph().record("nope.py") is None


# ------------------------------------------------------------------- bounded case


def test_a_bounded_change_selects_only_reachable_tests() -> None:
    graph = _graph(
        _record("core.py"),
        _record("test_core.py", cls="TEST_OBJECT", deps=["core.py"]),
        _record("test_unrelated.py", cls="TEST_OBJECT", deps=["other.py"]),
        _record("other.py"),
    )
    report = analyse(graph, ["core.py"])
    assert report.scope is Scope.CHANGED
    assert report.affected_tests == ("test_core.py",)
    assert "test_unrelated.py" not in report.affected_objects


def test_report_surfaces_evidence_certification_and_owners() -> None:
    graph = _graph(
        _record("core.py", owner="alpha"),
        _record("test_core.py", cls="TEST_OBJECT", deps=["core.py"], owner="alpha"),
    )
    report = analyse(graph, ["core.py"])
    assert report.affected_evidence == ("VALIDATION",)
    assert report.affected_certification == ("GOVERNED",)
    assert report.affected_owners == ("alpha",)


def test_plan_for_a_bounded_change_selects_paths() -> None:
    graph = _graph(
        _record("core.py"),
        _record("test_core.py", cls="TEST_OBJECT", deps=["core.py"]),
    )
    verification = plan(analyse(graph, ["core.py"]))
    assert verification.run_everything is False
    assert verification.test_paths == ("test_core.py",)


# ----------------------------------------------------------------- escalation


def test_no_changes_is_scope_none() -> None:
    report = analyse(_graph(), [])
    assert report.scope is Scope.NONE
    assert plan(report).run_everything is False
    assert plan(report).reason == "no changes to verify"


@pytest.mark.parametrize(
    "path",
    [
        "00-BOOK/DATA/id-ledger.json",
        "00-BOOK/SCHEMAS/artifact.schema.json",
        "00-BOOK/tools/ukb.py",
        "00-CMG/CMG-000001-x.md",
        "00-CEP/CEP-007-x.md",
        "pyproject.toml",
        "verify.sh",
        "Makefile",
        "scripts/ucos-env.sh",
    ],
)
def test_unbounded_paths_escalate_to_full(path: str) -> None:
    """A declaration drives engines no import graph connects to it."""
    report = analyse(_graph(_record("core.py")), [path])
    assert report.scope is Scope.FULL
    assert plan(report).run_everything is True


def test_bounded_suffixes_are_measured_not_declared() -> None:
    """The literal that was a language assumption, now a measurement.

    `BOUNDED_SUFFIXES = (".py",)` said only Python files carry edges an impact analysis can
    follow. That is true today and is NOT a property of impact analysis — it is a property of the
    registry's edge derivation, which resolves Python imports and nothing else. Measured at the
    commit that changed it: `.py` was the only suffix carrying a dependency edge, across 2,924
    `.md`, 2,290 `.py`, 173 `.json`, 38 `.yml` and 11 `.sh` objects.
    """
    from engine.verification_impact.impact import FALLBACK_BOUNDED_SUFFIXES, bounded_suffixes

    graph = _graph(_record("core.py", deps=("dep.py",)), _record("dep.py"))
    assert bounded_suffixes(graph) == FALLBACK_BOUNDED_SUFFIXES


def test_a_second_language_with_edges_becomes_bounded_without_an_edit() -> None:
    """THE POINT OF DERIVING IT, and the case a literal could never satisfy.

    A registry carrying edges for another suffix must make that suffix bounded, so the day an
    edge deriver lands for a second language its files stop escalating every change to FULL —
    with no edit to the selector. UCKP-ART-15: no conclusion rests on a hardcoded assumption.
    """
    from engine.verification_impact.impact import bounded_suffixes

    graph = _graph(
        _record("core.py", deps=("dep.py",)),
        _record("lib.rs", deps=("other.rs",)),
        _record("other.rs"),
    )
    assert bounded_suffixes(graph) == (".py", ".rs")


def test_a_suffix_whose_edges_nobody_derives_stays_unbounded() -> None:
    """The conclusion is unchanged; only its basis is measured.

    A file type present in the registry but carrying no edges is still unbounded, because nothing
    can follow its dependencies. Escalation for it remains correct — and is now correct for a
    stated reason rather than because a tuple happened not to list it.
    """
    from engine.verification_impact.impact import bounded_suffixes

    graph = _graph(_record("core.py", deps=("dep.py",)), _record("notes.md"), _record("dep.py"))
    assert ".md" not in bounded_suffixes(graph)


def test_non_python_changes_escalate_to_full() -> None:
    report = analyse(_graph(_record("core.py")), ["00-MASTER/X/register.md"])
    assert report.scope is Scope.FULL
    assert any("not present in the executable object registry" in e for e in report.escalations)


def test_a_registered_non_python_object_escalates_for_its_recorded_reason() -> None:
    """The escalation names the object class it measured, not the file extension.

    `engine/lineage/families.json` is the live case: registered as UCOS-ENG-000023 with an
    explicitly empty dependency list. Reporting "no dependency edges exist for this file
    type" about it asserted a property of `.json` that 172 registered `.json` objects
    contradict, and asserted it before consulting the registry at all.
    """
    data = _record("engine/lineage/families.json", "DOCUMENT_ARTIFACT")
    report = analyse(_graph(_record("core.py"), data), ["engine/lineage/families.json"])
    assert report.scope is Scope.FULL
    assert report.unregistered == (), "a registered object must not be reported unregistered"
    reasons = [e for e in report.escalations if "families.json" in e]
    assert reasons and "DOCUMENT_ARTIFACT" in reasons[0]
    assert not any("file type" in e for e in report.escalations)


def test_an_unregistered_python_file_escalates_and_is_named() -> None:
    """A new file absent from the registry has unknown dependents."""
    report = analyse(_graph(_record("core.py")), ["engine/brand_new.py"])
    assert report.scope is Scope.FULL
    assert report.unregistered == ("engine/brand_new.py",)


def test_a_bounded_change_reaching_no_test_widens_rather_than_skipping() -> None:
    """Code nothing exercises is a coverage question, not a licence to skip."""
    report = analyse(_graph(_record("orphan.py")), ["orphan.py"])
    assert report.scope is Scope.INTEGRATION
    assert any("reaches no test object" in e for e in report.escalations)
    assert plan(report).run_everything is True


def test_a_broad_blast_radius_widens_to_integration() -> None:
    graph = _graph(
        _record("core.py"),
        *[
            _record(f"test_{n}.py", cls="TEST_OBJECT", deps=["core.py"], owner=f"own{n}")
            for n in range(5)
        ],
    )
    report = analyse(graph, ["core.py"])
    assert report.scope is Scope.INTEGRATION
    assert any("subsystem-level blast radius" in e for e in report.escalations)


def test_mixed_changes_take_the_broader_scope() -> None:
    graph = _graph(
        _record("core.py"),
        _record("test_core.py", cls="TEST_OBJECT", deps=["core.py"]),
    )
    report = analyse(graph, ["core.py", "pyproject.toml"])
    assert report.scope is Scope.FULL


def test_scope_widen_is_monotonic() -> None:
    assert Scope.CHANGED.widen(Scope.FULL) is Scope.FULL
    assert Scope.FULL.widen(Scope.CHANGED) is Scope.FULL
    assert Scope.NONE.widen(Scope.NONE) is Scope.NONE
    assert Scope.INTEGRATION.widen(Scope.CHANGED) is Scope.INTEGRATION


def test_report_serialises_with_counts() -> None:
    graph = _graph(
        _record("core.py"),
        _record("test_core.py", cls="TEST_OBJECT", deps=["core.py"]),
    )
    body = analyse(graph, ["core.py"]).to_dict()
    assert body["counts"]["affected_tests"] == 1
    assert body["scope"] == "changed"


def test_is_full_predicate() -> None:
    assert analyse(_graph(), ["verify.sh"]).is_full is True


# ------------------------------------------------------------------------- CLI


@pytest.fixture(scope="module")
def a_currently_bounded_path() -> str:
    """A path the LIVE graph bounds today, DERIVED rather than named.

    This fixture exists because naming one has now gone stale twice. The test first named
    `engine/temporal/coordinate.py`; ADR-0015 gave it real external dependents and it correctly
    began to escalate, so the name was changed to `engine/knowledge/ukip/errors.py` — which by
    the time of this reading reaches 11 owners and escalates for exactly the same reason. Both
    times the ENGINE was right and the TEST was stale, and both times the failure looked like a
    regression in the thing under test.

    A hardcoded example of "a narrow change" is a claim about a dependency graph that is
    supposed to keep changing. So the example is now taken FROM the graph: the CLI's healthy
    path is proven on whatever the engine currently bounds. If the engine bounds nothing at all
    the fixture fails loudly, which is the right answer — a selector that can no longer bound
    anything has stopped selecting, and that is a finding rather than a green run.
    """
    from engine.verification_impact.cli import main as _main

    candidates = [
        "engine/verification_impact/render.py",
        "engine/tests/unit/test_verification_impact.py",
        "engine/knowledge/ukip/errors.py",
        "engine/temporal/coordinate.py",
    ]
    for path in candidates:
        if _main(["--path", path, "--quiet"]) == EXIT_BOUNDED:
            return path
    pytest.fail(
        "the live impact engine bounds none of the sampled paths, so the bounded CLI path "
        "cannot be exercised at all. Either the graph now makes every change subsystem-wide "
        "or the selector has stopped bounding; both are findings, neither is a pass."
    )


def test_cli_bounded_change_exits_zero(capsys, a_currently_bounded_path: str) -> None:
    """The CLI's healthy path, on a change the live graph genuinely bounds today."""
    assert main(["--path", a_currently_bounded_path, "--quiet"]) == EXIT_BOUNDED


def test_cli_selects_the_temporal_tests(capsys) -> None:
    """Live registry: a temporal change must reach its own suite.

    engine/temporal/coordinate.py now has real dependents outside its own package
    (engine/knowledge/ukip/relationships.py and confidence.py, ADR-0015/0016), which
    correctly escalates it past the bounded-CLI path (--print-tests prints nothing
    once escalated, per test_cli_print_tests_is_empty_when_escalated) — so this reads
    the full affected-test set via --json instead of the bounded --print-tests output.
    """
    main(["--path", "engine/temporal/coordinate.py", "--json"])
    body = json.loads(capsys.readouterr().out)
    assert body["plan"]["run_everything"] is True
    assert "engine/tests/unit/test_temporal_contract.py" in body["impact"]["affected_tests"]


def test_cli_escalation_exits_two(capsys) -> None:
    assert main(["--path", "00-BOOK/DATA/id-ledger.json", "--quiet"]) == EXIT_ESCALATED


def test_cli_print_tests_is_empty_when_escalated(capsys) -> None:
    """Silence plus exit 2 — never silence plus exit 0."""
    code = main(["--path", "verify.sh", "--print-tests"])
    assert code == EXIT_ESCALATED
    assert capsys.readouterr().out.strip() == ""


def test_cli_emits_json(capsys, a_currently_bounded_path: str) -> None:
    """The bounded report's shape, on a path the live graph bounds. See the fixture for why
    the example is derived rather than named."""
    main(["--path", a_currently_bounded_path, "--json"])
    body = json.loads(capsys.readouterr().out)
    assert body["plan"]["scope"] == "changed"
    assert body["impact"]["counts"]["changed"] == 1


def test_cli_renders_a_report(capsys) -> None:
    main(["--path", "engine/temporal/coordinate.py"])
    assert "VERIFICATION IMPACT" in capsys.readouterr().out


def test_cli_renders_escalations(capsys) -> None:
    main(["--path", "verify.sh"])
    assert "escalations:" in capsys.readouterr().out


def test_cli_faults_on_an_unresolvable_base(capsys) -> None:
    assert main(["--base", "not-a-real-ref-xyz", "--quiet"]) == EXIT_ESCALATED
    assert "IMPACT FAULT" in capsys.readouterr().err


# ------------------------------------------------------------------- changes


def test_working_tree_changes_returns_paths() -> None:
    from engine.verification_impact import working_tree_changes

    assert isinstance(working_tree_changes(), tuple)


def test_changed_paths_refuses_an_unresolvable_base() -> None:
    from engine.verification_impact import changed_paths

    with pytest.raises(ImpactError, match="does not resolve"):
        changed_paths("definitely-not-a-ref-abc123")


# ------------------------------------------------- diff-base resolution coverage
# The resolution chain is the part that must never return an empty set on failure,
# so each branch is exercised against a real throwaway repository rather than mocks.


@pytest.fixture(name="scratch_repo")
def _scratch_repo(tmp_path):
    """A real git repository with one commit, for base-resolution tests."""
    import subprocess

    root = tmp_path / "repo"
    root.mkdir()

    def git(*args: str):
        return subprocess.run(  # noqa: S603
            ["git", *args],  # noqa: S607 - resolved from PATH by design
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )

    git("init", "-q")
    git("config", "user.email", "t@t.invalid")
    git("config", "user.name", "t")
    (root / "a.py").write_text("x = 1\n")
    git("add", "a.py")
    git("commit", "-q", "-m", "first")
    return root, git


def test_explicit_base_diffs_against_it(scratch_repo) -> None:
    root, git = scratch_repo
    (root / "b.py").write_text("y = 2\n")
    git("add", "b.py")
    git("commit", "-q", "-m", "second")
    assert changed_paths("HEAD^", root=str(root)) == ("b.py",)


def test_working_tree_changes_include_staged_unstaged_and_untracked(scratch_repo) -> None:
    root, git = scratch_repo
    (root / "a.py").write_text("x = 2\n")  # unstaged modification
    (root / "staged.py").write_text("z = 3\n")
    git("add", "staged.py")
    (root / "untracked.py").write_text("w = 4\n")
    found = working_tree_changes(root=str(root))
    assert set(found) == {"a.py", "staged.py", "untracked.py"}


def test_working_tree_changes_take_priority_over_history(scratch_repo) -> None:
    root, _ = scratch_repo
    (root / "dirty.py").write_text("d = 1\n")
    assert changed_paths(root=str(root)) == ("dirty.py",)


def test_head_parent_is_used_when_the_tree_is_clean(scratch_repo) -> None:
    root, git = scratch_repo
    (root / "c.py").write_text("c = 1\n")
    git("add", "c.py")
    git("commit", "-q", "-m", "third")
    assert changed_paths(root=str(root)) == ("c.py",)


def test_a_clean_single_commit_repo_refuses_rather_than_reporting_nothing(
    scratch_repo,
) -> None:
    """The dangerous case: no base, clean tree. Must raise, never return ()."""

    root, _ = scratch_repo  # one commit, no HEAD^, no upstream, clean
    with pytest.raises(ImpactError, match="no diff base could be resolved"):
        changed_paths(root=str(root))


def test_working_tree_changes_outside_a_repository_returns_empty(tmp_path) -> None:
    assert working_tree_changes(root=str(tmp_path)) == ()


def test_changed_paths_outside_a_repository_refuses(tmp_path) -> None:
    with pytest.raises(ImpactError):
        changed_paths(root=str(tmp_path))


# ------------------------------------------------- version-control path fidelity
# Regression cover for the change-set parsing defect. `git diff --name-only` and
# `git ls-files --others` C-quote and octal-escape any path holding a non-ASCII byte,
# so a changed `UCOS-Ω∞-T.md` arrived as the literal `"UCOS-\316\251\342\210\236-T.md"`
# — quote characters included. That string is not a repository path: it matches no
# UNBOUNDED_PREFIXES entry (it starts with `"`), no BOUNDED_SUFFIXES entry (it ends
# with `.py"`), and no registry record.
#
# Measured consequence: the scope did NOT narrow — an unmatchable path falls through
# to the unbounded branch and widens to FULL. What broke is the *reason*: the engine
# reported "no dependency edges exist for this file type" about a registered .py
# module that has edges, and named a file that does not exist. Escalation that is
# right by accident and wrong by mechanism is not tracking real coupling, which is
# what REQ-37 requires of it.
#
# Every pre-existing test in this file uses ASCII-only fixture names, which is exactly
# why none of them could see it.

OMEGA_MODULE = "UCOS-Ω∞-MOD.py"
OMEGA_DOC = "UCOS-Ω∞-DOC.md"
OMEGA_NEW = "UCOS-Ω∞-NEW.md"


def _assert_unescaped(paths) -> None:
    """No quoted or octal-escaped path may survive into a change set."""
    assert not any(p.startswith('"') for p in paths), f"a quoted path survived: {paths}"
    assert not any(
        "\\316" in p or "\\342" in p for p in paths
    ), f"an octal-escaped path survived: {paths}"


def test_a_non_ascii_changed_file_is_detected_under_its_real_path(scratch_repo) -> None:
    """A — unstaged non-ASCII change reaches the selector as `UCOS-Ω∞-DOC.md`."""

    root, git = scratch_repo
    (root / OMEGA_DOC).write_text("# first\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "add omega doc")
    (root / OMEGA_DOC).write_text("# changed\n", encoding="utf-8")

    found = working_tree_changes(root=str(root))
    assert OMEGA_DOC in found
    _assert_unescaped(found)


def test_a_staged_non_ascii_file_is_detected_under_its_real_path(scratch_repo) -> None:
    """B — the `--cached` branch, which is the pre-commit reality."""

    root, git = scratch_repo
    (root / OMEGA_MODULE).write_text("y = 1\n", encoding="utf-8")
    git("add", OMEGA_MODULE)

    found = working_tree_changes(root=str(root))
    assert OMEGA_MODULE in found
    _assert_unescaped(found)


def test_an_untracked_non_ascii_file_is_detected_under_its_real_path(scratch_repo) -> None:
    """C — the `ls-files --others` branch."""

    root, _ = scratch_repo
    (root / OMEGA_NEW).write_text("# new\n", encoding="utf-8")

    found = working_tree_changes(root=str(root))
    assert OMEGA_NEW in found
    _assert_unescaped(found)


def test_a_non_ascii_path_survives_every_diff_base_branch(scratch_repo) -> None:
    """The base and HEAD^ branches carry the same defect as the working-tree ones.

    Not in the reported three, found by reading the module: `changed_paths` resolves
    through an explicit base, a merge-base, or `HEAD^`, and each parsed paths the same
    unsafe way. A fix covering only the working tree would leave CI — which supplies a
    base — still reading escaped names.
    """

    root, git = scratch_repo
    (root / OMEGA_MODULE).write_text("y = 1\n", encoding="utf-8")
    (root / "plain.py").write_text("w = 1\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "second")

    explicit = changed_paths("HEAD^", root=str(root))
    assert set(explicit) == {OMEGA_MODULE, "plain.py"}
    _assert_unescaped(explicit)

    fallback = changed_paths(root=str(root))  # clean tree, no upstream -> HEAD^ branch
    assert set(fallback) == {OMEGA_MODULE, "plain.py"}
    _assert_unescaped(fallback)


def test_ascii_change_detection_is_unchanged(scratch_repo) -> None:
    """D — the correction is path spelling only; ASCII behaviour must be identical."""

    root, git = scratch_repo
    (root / "a.py").write_text("x = 2\n", encoding="utf-8")
    (root / "staged.py").write_text("s = 1\n", encoding="utf-8")
    git("add", "staged.py")
    (root / "untracked.py").write_text("u = 1\n", encoding="utf-8")

    assert set(working_tree_changes(root=str(root))) == {"a.py", "staged.py", "untracked.py"}
    # Working-tree changes still take priority over history resolution.
    assert set(changed_paths(root=str(root))) == {"a.py", "staged.py", "untracked.py"}


def test_path_normalisation_does_not_weaken_escalation(scratch_repo) -> None:
    """E — escalation rules still fire, and now fire for the *right* reason.

    Two halves, because "not weakened" means both directions:

    * a registered non-ASCII module resolves to its real dependent test instead of
      escalating with the false claim that it has no dependency edges;
    * a non-ASCII path under an UNBOUNDED prefix still escalates — the escaped form
      lost `_is_unbounded` (it starts with `"`) and reached the unbounded branch only
      by the accident of also failing `_is_bounded`.
    """
    from collections import defaultdict

    from engine.verification_impact.impact import _is_bounded, _is_unbounded

    graph = ImpactGraph()
    test_path = "engine/tests/test_omega.py"
    graph.objects = {
        OMEGA_MODULE: _record(OMEGA_MODULE),
        test_path: _record(test_path, "TEST_OBJECT", deps=(OMEGA_MODULE,)),
    }
    graph.dependents = defaultdict(set, {OMEGA_MODULE: {test_path}})
    graph.owners = defaultdict(set, {"own": {OMEGA_MODULE, test_path}})

    report = analyse(graph, [OMEGA_MODULE])
    assert report.changed == (OMEGA_MODULE,)
    assert report.affected_tests == (test_path,), "real coupling must be resolved, not escalated"
    assert report.unregistered == (), "a registered module must not be reported unregistered"
    assert not any("no dependency edges" in e for e in report.escalations)

    escaped = '"UCOS-\\316\\251\\342\\210\\236-MOD.py"'
    stale = analyse(graph, [escaped])
    assert stale.affected_tests == (), "guard: the escaped form resolves no coupling at all"
    assert stale.scope is Scope.FULL

    # Unbounded classification survives normalisation; the escaped form loses it.
    assert _is_unbounded("00-CEP/UCOS-Ω∞-X.md") is True
    assert _is_bounded("00-CEP/UCOS-Ω∞-X.md") is False
    assert _is_unbounded('"00-CEP/UCOS-\\316\\251\\342\\210\\236-X.md"') is False
    unbounded_report = analyse(graph, ["00-CEP/UCOS-Ω∞-X.md"])
    assert unbounded_report.scope is Scope.FULL
    assert any("not bounded by import edges" in e for e in unbounded_report.escalations)


# --- git that answers, and git that does not ------------------------------------------
#
# Every change-set read here runs against this checkout, where git answers every question.
# Each read below is best-effort by construction — the sequence tries several bases and keeps
# what it can — so the arm that answers for a read that FAILS exists at every step and none
# had run. They matter because the failure mode they prevent is silent: a change set that
# comes back empty because git could not answer looks exactly like a verified run.


def _paths_returning(monkeypatch, *results):
    """Script the path-emitting git reads in order, so each failure position is reachable.

    git does not produce these combinations on demand — ``diff HEAD`` succeeding while
    ``diff --cached HEAD`` fails is not a state a repository can be put into — so the runner
    is scripted rather than a repository forged. What is under test is the SEQUENCE's response
    to a failed read, which is the same whatever made it fail.
    """
    answers = iter(results)
    monkeypatch.setattr(
        "engine.verification_impact.changes._git_paths", lambda *_a, **_k: next(answers)
    )


def test_a_read_that_fails_contributes_nothing_and_does_not_lose_the_others(monkeypatch) -> None:
    """THE WORKING-TREE CHANGE SET IS THREE READS UNIONED, and each may fail alone.

    Tracked modifications, staged modifications and untracked files are three separate git
    questions. A failure in the second or third must not discard the first: the union is what
    "the local change set" means, and answering with nothing because one read failed would
    narrow the verification silently. Only a failure of the FIRST read is fatal to the
    answer, and that arm was already exercised.
    """
    _paths_returning(monkeypatch, (0, ("tracked.py",)), (1, ()), (1, ()))

    assert working_tree_changes() == ("tracked.py",)


def test_a_supplied_base_that_resolves_but_cannot_be_diffed_is_a_fault(monkeypatch) -> None:
    """A BASE THAT RESOLVES IS NOT A BASE THAT DIFFS.

    The unresolvable base was tested. This is the other half: the ref exists and the diff
    against it still fails — a shallow clone whose history does not reach the base is the
    ordinary way. Returning an empty change set there would report that an explicitly based
    run found nothing to verify, which is the one answer this module refuses to give.
    """
    monkeypatch.setattr("engine.verification_impact.changes._exists", lambda *_a, **_k: True)
    _paths_returning(monkeypatch, (128, ()))

    with pytest.raises(ImpactError, match="could not diff against base"):
        changed_paths("origin/main")


def test_every_fallback_base_that_fails_falls_through_to_the_refusal(monkeypatch) -> None:
    """THE FALLBACK CHAIN ENDS IN A REFUSAL, NEVER IN AN EMPTY ANSWER.

    With no working-tree change the resolution tries the upstream merge-base and then
    ``HEAD^``, and each step has a failure arm none of which had run. All three lead to the
    same place on purpose: an empty change set is indistinguishable from a verified run, so
    when no base can be established the engine refuses rather than reporting that nothing
    changed.
    """
    monkeypatch.setattr(
        "engine.verification_impact.changes.working_tree_changes", lambda *_a, **_k: ()
    )
    monkeypatch.setattr("engine.verification_impact.changes._exists", lambda *_a, **_k: True)

    # the upstream resolves, and the merge-base against it does not
    refs = iter([(0, "origin/main"), (1, "")])
    monkeypatch.setattr("engine.verification_impact.changes._git", lambda *_a, **_k: next(refs))
    _paths_returning(monkeypatch, (1, ()))
    with pytest.raises(ImpactError, match="no diff base could be resolved"):
        changed_paths()

    # the merge-base resolves, and the diff from it does not
    refs = iter([(0, "origin/main"), (0, "abc123")])
    monkeypatch.setattr("engine.verification_impact.changes._git", lambda *_a, **_k: next(refs))
    _paths_returning(monkeypatch, (1, ()), (1, ()))
    with pytest.raises(ImpactError, match="no diff base could be resolved"):
        changed_paths()

    # and when the whole chain answers, the upstream merge-base IS the change set — the arm
    # every branch with an upstream and no local edits takes, which nothing had exercised.
    refs = iter([(0, "origin/main"), (0, "abc123")])
    monkeypatch.setattr("engine.verification_impact.changes._git", lambda *_a, **_k: next(refs))
    _paths_returning(monkeypatch, (0, ("b.py", "a.py")))
    assert changed_paths() == ("a.py", "b.py")


def test_a_report_with_no_escalation_renders_without_an_escalation_block(
    capsys, a_currently_bounded_path: str
) -> None:
    """THE RENDERED REPORT WAS ONLY EVER SEEN ESCALATING.

    The one render test names a path the live graph escalates, so the block-free form — what
    an operator sees on every bounded change, which is the common case — had never been
    produced. Emitting an empty "escalations:" heading would make a clean report look like a
    truncated one.
    """
    assert main([f"--path={a_currently_bounded_path}"]) == EXIT_BOUNDED

    rendered = capsys.readouterr().out
    assert "scope" in rendered
    assert "escalations:" not in rendered


def test_more_than_twelve_escalations_are_elided_with_a_count(capsys) -> None:
    """A REPORT NOBODY READS IS A REPORT THAT REPORTS NOTHING.

    The reasons are truncated at twelve and the remainder is counted, and the count arm had no
    case because no tested change escalates more than twelve times. It is the same discipline
    the environment gate keeps: forty lines of reasons above a verdict is how a report becomes
    something people scroll past, and the count is what stops the truncation from hiding that
    there was more.
    """
    unregistered = [f"--path=engine/never_written/module_{index}.py" for index in range(15)]

    assert main([*unregistered]) == EXIT_ESCALATED

    rendered = capsys.readouterr().out
    assert rendered.count("    - ") == 12
    assert "... +3 more" in rendered


def test_print_tests_emits_one_path_per_line_for_a_bounded_change(
    capsys, a_currently_bounded_path: str
) -> None:
    """SILENCE PLUS EXIT 2 WAS TESTED; SPEECH PLUS EXIT 0 WAS NOT.

    ``--print-tests`` is the mode ``verify.sh`` consumes, and the only case exercised was the
    escalated one where it prints nothing. The bounded case is the mode's whole purpose: one
    affected test path per line, with no report interleaved, so the output can be handed
    straight to the runner.
    """
    code = main([f"--path={a_currently_bounded_path}", "--print-tests"])

    printed = capsys.readouterr().out.splitlines()
    assert code == EXIT_BOUNDED
    assert printed
    assert all(line.endswith(".py") for line in printed), printed


def test_the_module_entry_point_dispatches_to_the_cli(monkeypatch) -> None:
    """``python -m engine.verification_impact`` IS THE INVOCATION verify.sh MAKES.

    The dispatcher is deliberately thin — two copies of an entry point are two things to keep
    in step — and nothing had ever run it, so the one line binding the module form to the CLI
    was unmeasured. It is executed rather than imported because the module body carries no
    ``__main__`` guard, which is also the only way the declared invocation is exercised.
    """
    monkeypatch.setattr("sys.argv", ["engine.verification_impact", "--path=verify.sh", "--quiet"])

    with pytest.raises(SystemExit) as raised:
        runpy.run_module("engine.verification_impact", run_name="__main__")

    assert raised.value.code == EXIT_ESCALATED
