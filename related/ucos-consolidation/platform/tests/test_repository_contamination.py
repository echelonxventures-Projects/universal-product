"""UCOS-CL-001 — an ignore rule must not be able to buy repository cleanliness.

The regression these tests exist for is specific and was real. At ``be46a300`` two lines
were added to ``.gitignore``:

    * [2-9]
    * [2-9].*

45 duplicate files were physically present. 41 of them left ``git status --porcelain``,
which is the command UCOS-RIB-001 counts for ``dirty_entries_outside_generated``. Nothing
was deleted. But the metric fell to zero, and that flipped RIB ``GATE-12`` and ``GATE-04``,
opened ``rib.json:gate``, satisfied AEE ``OBS-BLUEPRINT-GATE`` and cleared ``CONV-02``.

No test in the repository failed, because no test asserted the property that matters:
*exclusion must not be able to reduce the measured contamination on its own.*

``test_adding_an_ignore_rule_does_not_reduce_contamination`` is that assertion. It builds a
throwaway repository, plants a contaminating file, measures, then adds an ignore rule for
it and measures again — and requires the count to hold. It fails against the pre-fix
design by construction, because under that design the count is the porcelain line count.
"""

from __future__ import annotations

import json
import subprocess
import subprocess as sp
from pathlib import Path
from platform.repository_intelligence import contamination
from platform.repository_intelligence.contamination import (
    DECLARED_CLASSES,
    ContaminationReport,
    ExcludedPath,
    load_register,
    measure,
)

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607 - fixed argv, no shell
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


@pytest.fixture
def sandbox(tmp_path: Path) -> Path:
    """A minimal repository carrying a valid exclusion register."""
    repo = tmp_path / "repo"
    (repo / "00-BOOK" / "DATA").mkdir(parents=True)
    _git(repo.parent, "init", "--quiet", str(repo))
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "test")

    (repo / "00-BOOK" / "DATA" / "exclusion-register.json").write_text(
        json.dumps(
            {
                "schema": "ucos-exclusion-register",
                "entries": [
                    {"rule": "__pycache__/", "class": "CACHE", "rationale": "bytecode"},
                ],
            }
        ),
        encoding="utf-8",
    )
    (repo / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    (repo / "source.py").write_text("x = 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "--quiet", "-m", "baseline")
    return repo


def test_baseline_sandbox_is_clean(sandbox: Path) -> None:
    report = measure(sandbox)
    assert report.clean, report.as_dict()
    assert report.contamination_entries == 0


def test_adding_an_ignore_rule_does_not_reduce_contamination(sandbox: Path) -> None:
    """THE regression. Exclusion without declaration must not lower the count.

    This is the property whose absence let a two-line .gitignore edit clear a blocking
    convergence criterion on a repository that still held every contaminating file.
    """
    (sandbox / "debris 2.py").write_text("y = 2\n", encoding="utf-8")

    before = measure(sandbox)
    assert before.contamination_entries == 1, before.as_dict()
    assert "debris 2.py" in before.untracked_entries

    # Exclude it — the exact move that manufactured cleanliness at be46a300. The rule is
    # COMMITTED, as it was there, so the only thing left to measure is the debris itself.
    (sandbox / ".gitignore").write_text("__pycache__/\n* [2-9].*\n", encoding="utf-8")
    _git(sandbox, "add", ".gitignore")
    _git(sandbox, "commit", "--quiet", "-m", "exclude the debris")

    after = measure(sandbox)
    assert after.contamination_entries == 1, (
        "adding an ignore rule reduced the contamination count without any declaration — "
        "the exclusion authority is again an input to the gate that polices exclusion.\n"
        f"before={before.as_dict()}\nafter={after.as_dict()}"
    )
    # It moved from 'untracked' to 'ignored but undeclared'. Still counted, now named.
    assert after.ignored_unclassified == 1
    assert "debris 2.py" in after.unclassified_paths


def test_declaring_the_class_is_what_clears_it(sandbox: Path) -> None:
    """The count falls only when a tracked, reviewable declaration accounts for the path.

    This is the other half of the invariant: exclusion is not forbidden, it is made to cost
    a declaration. A reviewer sees the class and can disagree with it.
    """
    (sandbox / "scratch.tmp").write_text("t\n", encoding="utf-8")
    (sandbox / ".gitignore").write_text("__pycache__/\n*.tmp\n", encoding="utf-8")
    _git(sandbox, "add", ".gitignore")
    _git(sandbox, "commit", "--quiet", "-m", "exclude scratch files")

    assert measure(sandbox).ignored_unclassified == 1

    register = sandbox / "00-BOOK" / "DATA" / "exclusion-register.json"
    doc = json.loads(register.read_text(encoding="utf-8"))
    doc["entries"].append({"rule": "*.tmp", "class": "TEMPORARY", "rationale": "scratch"})
    register.write_text(json.dumps(doc), encoding="utf-8")
    _git(sandbox, "add", "-A")
    _git(sandbox, "commit", "--quiet", "-m", "declare the class")

    after = measure(sandbox)
    assert after.ignored_unclassified == 0, after.as_dict()
    assert after.clean, after.as_dict()


def test_a_tracked_path_shadowed_by_an_ignore_rule_is_counted(sandbox: Path) -> None:
    """A tracked file matched by an ignore rule is contamination-in-waiting.

    It survives only because git does not apply ignore rules to indexed files. The moment
    it leaves the index it disappears from governance silently. `00-SOURCE/VISION/Missing
    2.docx` and `Missing 3.docx` were in exactly this state under the withdrawn rule, while
    the rule's own comment claimed numbered originals were not suppressed.
    """
    (sandbox / "Chapter 2.md").write_text("# two\n", encoding="utf-8")
    _git(sandbox, "add", "-A")
    _git(sandbox, "commit", "--quiet", "-m", "authored numbered document")
    assert measure(sandbox).clean

    (sandbox / ".gitignore").write_text("__pycache__/\n* [2-9].*\n", encoding="utf-8")

    after = measure(sandbox)
    assert "Chapter 2.md" in after.shadowed_tracked, after.as_dict()
    assert not after.clean


def test_undeclared_class_in_register_is_a_register_error(sandbox: Path) -> None:
    """A register entry carrying an unrecognised class declares nothing, and fails closed."""
    register = sandbox / "00-BOOK" / "DATA" / "exclusion-register.json"
    doc = json.loads(register.read_text(encoding="utf-8"))
    doc["entries"].append({"rule": "*.tmp", "class": "PROBABLY_FINE", "rationale": "no"})
    register.write_text(json.dumps(doc), encoding="utf-8")

    mapping, errors = load_register(sandbox)
    assert "*.tmp" not in mapping
    assert any("PROBABLY_FINE" in e for e in errors)
    assert not measure(sandbox).clean


def test_missing_register_fails_closed(tmp_path: Path) -> None:
    """No register is not 'nothing to check'. It is an unmeasurable repository."""
    repo = tmp_path / "bare"
    repo.mkdir()
    _git(tmp_path, "init", "--quiet", str(repo))
    mapping, errors = load_register(repo)
    assert mapping == {}
    assert errors and "missing" in errors[0]


# --- the live repository ----------------------------------------------------------------


def test_live_repository_has_no_unclassified_exclusion() -> None:
    """Every ignored path in THIS repository resolves to a declared class."""
    report = measure(REPO_ROOT)
    assert report.register_errors == [] or not report.register_errors, report.register_errors
    assert report.ignored_unclassified == 0, (
        "ignored paths with no declared class in the exclusion register:\n  "
        + "\n  ".join(report.unclassified_paths)
    )


def test_live_repository_shadows_no_tracked_path() -> None:
    """No tracked path in THIS repository is matched by an ignore rule."""
    report = measure(REPO_ROOT)
    assert report.shadowed_tracked == (), (
        "tracked paths matched by an ignore rule — they survive only by being indexed:\n  "
        + "\n  ".join(report.shadowed_tracked)
    )


def test_every_declared_class_is_recognised() -> None:
    """The live register uses only classes the classifier recognises."""
    mapping, errors = load_register(REPO_ROOT)
    assert errors == (), errors
    assert mapping, "live exclusion register declares no rules"
    assert set(mapping.values()) <= DECLARED_CLASSES


def test_report_counts_are_consistent() -> None:
    """contamination_entries is the sum of its parts — no double counting, no omission."""
    r = ContaminationReport(
        dirty_entries=("a",),
        untracked_entries=("b", "c"),
        excluded=(),
        shadowed_tracked=("d",),
    )
    assert r.contamination_entries == 4
    assert not r.clean


# ---------------------------------------------------------------------------
# UCOS-RC-001 — canonical identity must not carry environmental filesystem state.
#
# Phase 9 forensic, HEAD 382b65e8: rib.json differed from a pristine clone in
# EXACTLY ONE field, `.repository.contamination.excluded_entries` — 232 in the
# source repository, 69 in the clone. It is a count of ignored files physically
# present on disk (__pycache__, .ec1-venv, tool caches), so it measures the
# machine, not the repository. All 15 RIB markdown outputs were byte-identical;
# this single integer was the whole of registry_variance.
#
# Phase 8 could not see it: it iterates an already-settled tree where the count
# is constant, so it reported drift 0 across 5 rounds while the leak was live.
# Only a clone moves that number, which is why the boundary asserted here is the
# SERIALIZED REPORT rather than any fixed-point round.
# ---------------------------------------------------------------------------


def test_serialized_report_carries_no_environmental_count() -> None:
    """Two repositories with identical governance state must serialize identically.

    The reports below differ only in how many ignored files happen to sit on disk —
    232 versus 69, the exact source/clone figures from the forensic. Every governance
    fact is the same: nothing unclassified, nothing shadowed, nothing dirty. If the
    serialized bytes differ, canonical identity is a function of the machine.
    """
    governed = ExcludedPath(path="x/__pycache__/m.pyc", rule="__pycache__/", classification="CACHE")

    source_env = ContaminationReport(
        excluded=tuple(
            ExcludedPath(
                path=f"p{i}/__pycache__/m.pyc", rule="__pycache__/", classification="CACHE"
            )
            for i in range(232)
        )
    )
    clone_env = ContaminationReport(excluded=(governed,) * 69)

    assert source_env.ignored_unclassified == clone_env.ignored_unclassified == 0
    assert source_env.contamination_entries == clone_env.contamination_entries == 0

    assert source_env.as_dict() == clone_env.as_dict(), (
        "the serialized contamination report changes with the number of ignored files "
        "present on disk. That number is environment, not repository content, and it is "
        "embedded in rib.json — so a pristine clone of the same commit derives a "
        "different canonical artifact. This is Phase-9 registry_variance."
    )


def test_no_canonical_field_counts_excluded_entries() -> None:
    """`excluded_entries` must not appear in the serialized report at any depth.

    The byte test above catches a divergence only when the two environments actually
    differ. This forbids the field outright, so the leak cannot return by being equal
    on the machine that happens to run the test.
    """
    report = ContaminationReport(
        excluded=(ExcludedPath(path="a", rule="__pycache__/", classification="CACHE"),)
    )
    assert (
        "excluded_entries" not in report.as_dict()
    ), "as_dict() serializes a count of ignored filesystem entries into canonical output"


def test_live_rib_json_carries_no_environmental_count() -> None:
    """The artifact boundary: the committed canonical artifact itself.

    Asserted over rib.json rather than over the producer, because the producer is not
    what Phase 9 compares.
    """
    rib = REPO_ROOT / "00-MASTER" / "UCOS-RIB-001" / "rib.json"
    if not rib.is_file():
        pytest.skip("rib.json not present")
    contamination = json.loads(rib.read_text(encoding="utf-8"))["repository"]["contamination"]
    assert "excluded_entries" not in contamination, (
        "rib.json embeds excluded_entries — a count of ignored files on this machine. "
        f"Present value: {contamination.get('excluded_entries')!r}. A pristine clone "
        "computes a different one, which is exactly Phase-9 registry_variance."
    )


# --- the register's own structural refusals ----------------------------------------------
#
# WHY EACH OF THESE IS A SEPARATE ENTRY IN `register_errors` RATHER THAN AN EXCEPTION. The
# register is read before anything is measured, so a reader has to learn everything wrong
# with it in one pass. Raising on the first defect would report one line of a file that has
# three, and the operator would fix them one commit at a time.


def test_a_register_that_is_not_json_is_a_named_error_and_not_a_crash(sandbox: Path) -> None:
    """An unparseable register declares NOTHING, which is the state that must fail closed.

    Returning an empty mapping and no error would be the dangerous shape: every ignored path
    would resolve to no class, `ignored_unclassified` would rise, and the repository would
    look contaminated for a reason nobody could locate. The error names the parse failure so
    the reader is sent to the register rather than to the ignore rules.
    """
    register = sandbox / "00-BOOK" / "DATA" / "exclusion-register.json"
    register.write_text('{"entries": [ truncated', encoding="utf-8")

    mapping, errors = load_register(sandbox)
    assert mapping == {}
    assert len(errors) == 1
    assert "not valid JSON" in errors[0]
    assert not measure(sandbox).clean


def test_a_register_entry_with_no_rule_declares_nothing(sandbox: Path) -> None:
    """A class with no pattern excuses no path. It is an entry that looks like governance."""
    register = sandbox / "00-BOOK" / "DATA" / "exclusion-register.json"
    doc = json.loads(register.read_text(encoding="utf-8"))
    doc["entries"].append({"class": "CACHE", "rationale": "which paths?"})
    register.write_text(json.dumps(doc), encoding="utf-8")

    mapping, errors = load_register(sandbox)
    assert mapping == {"__pycache__/": "CACHE"}
    assert errors == ("register entry with no rule",)


def test_a_rule_declared_twice_is_refused_rather_than_resolved(sandbox: Path) -> None:
    """TWO CLASSES FOR ONE PATTERN IS NOT A CHOICE THE READER GETS TO MAKE.

    Last-wins or first-wins would both be a silent answer to a question the register asks
    twice, and the two classes carry different obligations — a path that is CACHE is
    reconstructible and one that is TOOL_OPERATIONAL is not. The first declaration stands
    and the collision is reported, so the duplicate has to be resolved in the register.
    """
    register = sandbox / "00-BOOK" / "DATA" / "exclusion-register.json"
    doc = json.loads(register.read_text(encoding="utf-8"))
    doc["entries"].append({"rule": "__pycache__/", "class": "TOOL_OPERATIONAL", "rationale": "no"})
    register.write_text(json.dumps(doc), encoding="utf-8")

    mapping, errors = load_register(sandbox)
    assert mapping == {"__pycache__/": "CACHE"}, "the first declaration must stand"
    assert errors == ("rule '__pycache__/' declared twice",)


def test_every_defect_in_one_register_is_reported_in_one_pass(sandbox: Path) -> None:
    """Three defects, three errors. The operator fixes the register once, not three times."""
    register = sandbox / "00-BOOK" / "DATA" / "exclusion-register.json"
    doc = json.loads(register.read_text(encoding="utf-8"))
    doc["entries"] += [
        {"class": "CACHE"},
        {"rule": "*.tmp", "class": "PROBABLY_FINE"},
        {"rule": "__pycache__/", "class": "CACHE"},
    ]
    register.write_text(json.dumps(doc), encoding="utf-8")

    mapping, errors = load_register(sandbox)
    assert mapping == {"__pycache__/": "CACHE"}
    assert len(errors) == 3


# --- git is the boundary, and a git that fails is not a git that answered nothing ---------


def test_a_failing_git_command_raises_rather_than_reading_as_an_empty_repository(
    tmp_path: Path,
) -> None:
    """UCOS-CL-004 IN ONE SENTENCE: a corrupt ref made ``git log --all`` look like an empty
    history. "The command failed" and "the command found nothing" are different states, and
    conflating them turns every contamination measure into a pass — an empty answer satisfies
    every check here. Measuring a directory that is not a work tree is the cheapest way to
    reach the failure, and it is also the realistic one: a caller pointed at the wrong path.
    """
    outside = tmp_path / "not-a-repo"
    (outside / "00-BOOK" / "DATA").mkdir(parents=True)
    (outside / "00-BOOK" / "DATA" / "exclusion-register.json").write_text(
        json.dumps({"entries": []}), encoding="utf-8"
    )
    with pytest.raises(RuntimeError, match=r"git status .* failed"):
        measure(outside)


def test_check_ignore_finding_nothing_is_a_result_and_not_a_failure(sandbox: Path) -> None:
    """``git check-ignore`` exits 1 when no path matched, which is the ordinary case for a
    clean repository. Treating a non-zero exit as an error would make every clean measurement
    raise, so the accepted set is ``(0, 1)`` and everything else is a fault."""
    assert measure(sandbox).clean


def test_a_path_a_producer_rewrites_is_not_contamination(sandbox: Path) -> None:
    """``generated`` subtracts a producer's own output from the dirty set.

    UCOS-RIB-001 already does this and for the same reason: an artifact that dirties itself
    by being produced would make its own gate un-satisfiable, so the programme could never
    pass a run in which it did its job.
    """
    (sandbox / "source.py").write_text("x = 2\n", encoding="utf-8")
    assert not measure(sandbox).clean
    exempted = measure(sandbox, generated=["source.py"])
    assert exempted.clean
    assert exempted.dirty_entries == ()


def test_the_environmental_count_is_available_to_a_reader_and_to_no_artifact(
    sandbox: Path,
) -> None:
    """``excluded_entries`` counts what THIS filesystem happens to hold.

    It was serialized once, and the Phase-9 forensic at HEAD 382b65e8 found it to be the
    single differing field in rib.json between the source repository (232) and a pristine
    clone (69) — the entire cause of registry_variance. So it stays a property a report can
    read and stays out of ``as_dict``, and both halves of that are asserted here: a caller
    that wants the number gets it, and nothing canonical can pick it up by accident.
    """
    cache = sandbox / "__pycache__"
    cache.mkdir()
    (cache / "source.cpython-312.pyc").write_bytes(b"\x00")

    report = measure(sandbox)
    assert report.excluded_entries == len(report.excluded)
    assert report.excluded_entries > 0
    assert report.clean, "a declared exclusion class is what makes this clean"
    assert "excluded_entries" not in report.as_dict()


def test_a_check_ignore_that_fails_outright_raises_rather_than_matching_nothing(
    sandbox: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exit 1 means "no path matched". Anything else means the question was not answered.

    Collapsing the two would be the same defect as the one above in a subtler place: every
    ignored path would resolve to ``<unmatched>``, ``ignored_unclassified`` would equal the
    whole ignored set, and a repository that is fully declared would report as contaminated.
    The failure is reached by making the subprocess itself report a real git failure, so the
    arm runs on the shape it was written for.
    """

    real = sp.run

    def failing(argv, **kwargs):
        if "check-ignore" in argv:
            return sp.CompletedProcess(argv, 128, stdout="", stderr="fatal: not a git repository")
        return real(argv, **kwargs)

    monkeypatch.setattr(contamination.subprocess, "run", failing)
    (sandbox / "__pycache__").mkdir()
    (sandbox / "__pycache__" / "x.pyc").write_bytes(b"\x00")
    with pytest.raises(RuntimeError, match=r"git check-ignore failed \(128\)"):
        measure(sandbox)


def test_a_check_ignore_line_that_carries_no_path_is_skipped(
    sandbox: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``check-ignore -v`` emits ``<source>\\t<path>``, and a line without the tab is not a
    verdict about any path. Indexing it positionally would attribute one path's rule to
    another, so it is dropped — a lost rule makes a path UNCLASSIFIED, which fails closed,
    whereas a misattributed rule silently declares the wrong class."""

    real = sp.run

    def truncated(argv, **kwargs):
        if "check-ignore" in argv:
            completed = real(argv, **kwargs)
            noise = "warning: a line with no tab at all\n"
            return sp.CompletedProcess(argv, completed.returncode, noise + completed.stdout, "")
        return real(argv, **kwargs)

    monkeypatch.setattr(contamination.subprocess, "run", truncated)
    cache = sandbox / "__pycache__"
    cache.mkdir()
    (cache / "x.pyc").write_bytes(b"\x00")

    report = measure(sandbox)
    assert report.clean, "the real verdicts must survive the unusable line"
    assert report.excluded_entries > 0
    assert all(e.classification == "CACHE" for e in report.excluded)
