"""UCI-000001 Part 8 — the equivalence primitives, exercised without paying for a suite run.

WHAT THIS MODULE COVERS AND WHAT IT DELIBERATELY DOES NOT. ``reproducibility``,
``order_independence`` and ``shard_equivalence`` each run the whole suite inside a frozen
extraction of a commit — minutes of work per call, several times over. Unit-testing them would
mean running the suite from inside the suite. What IS unit-testable is every primitive those three
are assembled from, and that is where their correctness actually lives:

  * ``partition`` — the deliberately independent sharding. Its two refusals are the proof's
    soundness conditions, not conveniences.
  * ``discover_test_modules`` — the filesystem population, kept independent of pytest's plugin set
    so a collection hook cannot shrink the shards and the whole run together.
  * ``_compare_all`` — the N-1 comparison that stands in for N-way equality.
  * ``_collect_failures`` and ``EquivalenceFinding.holds`` — the two ways a proof can fail, kept
    separate because "the runs disagreed" and "a run did not pass" are different findings.

THE EMPTY-POPULATION REFUSALS ARE THE POINT. A shard proof over an empty suite compares nothing to
nothing and reports success; an empty shard contributes no coverage data and makes the combined
total silently smaller than the whole run. Both are asserted below, because both are ways this
module could certify a vacuum.
"""

from __future__ import annotations

import pytest

from engine.certification_integrity import suite
from engine.certification_integrity.equivalence import (
    EquivalenceFinding,
    _collect_failures,
    _compare_all,
    discover_test_modules,
    partition,
)
from engine.certification_integrity.model import IntegrityError

# ------------------------------------------------------------------------------- partition


def test_partition_is_round_robin_over_the_sorted_list() -> None:
    """Deterministic by construction: the same items always land in the same shard, whatever
    order the caller supplied them in."""
    items = ["e.py", "a.py", "d.py", "b.py", "c.py"]
    groups = partition(items, 2)
    assert groups == [["a.py", "c.py", "e.py"], ["b.py", "d.py"]]
    assert partition(list(reversed(items)), 2) == groups


def test_partition_covers_every_item_exactly_once() -> None:
    """A partition that dropped or duplicated an item would make the combined coverage differ from
    the whole run for a reason that has nothing to do with sharding."""
    items = [f"t{n}.py" for n in range(37)]
    groups = partition(items, 5)
    flat = [item for group in groups for item in group]
    assert sorted(flat) == sorted(items)
    assert len(flat) == len(set(flat)) == 37


def test_partition_refuses_fewer_than_two_shards() -> None:
    """One shard IS the whole run, so the proof would compare a run against itself and hold
    vacuously."""
    for shards in (1, 0, -1):
        with pytest.raises(IntegrityError):
            partition(["a.py", "b.py"], shards)


def test_partition_refuses_to_leave_a_shard_empty() -> None:
    """An empty shard contributes no coverage data, so the combined total would be silently
    smaller than the whole run and the inequality would be read as a sharding defect."""
    with pytest.raises(IntegrityError) as refusal:
        partition(["a.py", "b.py"], 4)
    assert "no tests" in str(refusal.value)


def test_partition_accepts_exactly_as_many_shards_as_items() -> None:
    groups = partition(["a.py", "b.py", "c.py"], 3)
    assert groups == [["a.py"], ["b.py"], ["c.py"]]


# -------------------------------------------------------------------- discover_test_modules


def test_discovery_reads_the_filesystem_and_returns_repo_relative_posix_paths(tmp_path) -> None:
    (tmp_path / "suite" / "nested").mkdir(parents=True)
    (tmp_path / "suite" / "test_a.py").write_text("", encoding="utf-8")
    (tmp_path / "suite" / "nested" / "test_b.py").write_text("", encoding="utf-8")
    (tmp_path / "suite" / "helper.py").write_text("", encoding="utf-8")
    (tmp_path / "suite" / "conftest.py").write_text("", encoding="utf-8")

    found = discover_test_modules(str(tmp_path), ["suite"])
    assert found == ["suite/nested/test_b.py", "suite/test_a.py"]


def test_discovery_takes_the_prefix_rule_not_the_suffix_rule(tmp_path) -> None:
    (tmp_path / "suite").mkdir()
    (tmp_path / "suite" / "test_yes.py").write_text("", encoding="utf-8")
    (tmp_path / "suite" / "no_test.py").write_text("", encoding="utf-8")
    assert discover_test_modules(str(tmp_path), ["suite"]) == ["suite/test_yes.py"]


def test_discovery_spans_every_declared_testpath(tmp_path) -> None:
    for tree in ("one", "two"):
        (tmp_path / tree).mkdir()
        (tmp_path / tree / f"test_{tree}.py").write_text("", encoding="utf-8")
    assert discover_test_modules(str(tmp_path), ["one", "two"]) == [
        "one/test_one.py",
        "two/test_two.py",
    ]


def test_discovery_refuses_an_empty_population(tmp_path) -> None:
    """A shard proof over an empty suite compares nothing to nothing and reports success."""
    (tmp_path / "suite").mkdir()
    with pytest.raises(IntegrityError) as refusal:
        discover_test_modules(str(tmp_path), ["suite"])
    assert "empty suite" in str(refusal.value)


def test_discovery_refuses_a_testpath_that_does_not_exist(tmp_path) -> None:
    with pytest.raises(IntegrityError):
        discover_test_modules(str(tmp_path), ["nowhere"])


# ---------------------------------------------------------------------------- the finding


def _result(label: str, *, exit_code: int = 0, report: object = None) -> suite.SuiteResult:
    return suite.SuiteResult(
        label=label,
        exit_code=exit_code,
        duration_seconds=0.0,
        counts={"passed": 1} if exit_code == 0 else {},
        coverage_xml="",
        report=report,  # type: ignore[arg-type]
        stdout_tail="",
        stderr_tail="",
    )


def test_a_finding_holds_only_when_the_runs_agree_and_all_of_them_passed() -> None:
    """Two independent failure modes, kept apart: runs that DISAGREE and runs that did not PASS.
    Collapsing them would report a red suite as a determinism defect."""
    assert EquivalenceFinding(rule="R", question="q", identical=True).holds
    assert not EquivalenceFinding(rule="R", question="q", identical=False).holds
    assert not EquivalenceFinding(
        rule="R", question="q", identical=True, failures=["a run failed"]
    ).holds


def test_a_finding_renders_both_failure_modes_into_its_record() -> None:
    record = EquivalenceFinding(
        rule="Rule 10",
        question="does combine(shards) equal the whole run?",
        identical=False,
        failures=["shard-2: pytest exited 1"],
    ).as_record()
    assert record["rule"] == "Rule 10"
    assert record["holds"] is False
    assert record["identical"] is False
    assert record["failures"] == ["shard-2: pytest exited 1"]
    assert record["runs"] == [] and record["comparisons"] == []


def test_the_record_copies_its_lists_so_a_reader_cannot_mutate_the_finding() -> None:
    finding = EquivalenceFinding(rule="R", question="q", failures=["one"])
    record = finding.as_record()
    record["failures"].append("two")  # type: ignore[union-attr]
    assert finding.failures == ["one"]


# -------------------------------------------------------------------------- the comparison


def test_a_run_that_produced_no_coverage_is_not_identical_to_anything() -> None:
    """ "The runs agreed" and "a run measured nothing" must never be the same answer: the second is
    an absent measurement, and treating absence as agreement is how a broken run certifies."""
    identical, comparisons = _compare_all([_result("a"), _result("b")])
    assert identical is False
    assert comparisons[0]["identical"] is False
    assert "no coverage measurement" in str(comparisons[0]["reason"])


def test_the_comparison_is_linear_in_the_number_of_runs() -> None:
    """N-1 comparisons against the first, not N(N-1)/2 pairwise: set equality is transitive, and
    the evidence has to stay readable when N is 100."""
    _identical, comparisons = _compare_all([_result(f"r{n}") for n in range(5)])
    assert len(comparisons) == 4
    assert [c["first"] for c in comparisons] == ["r0"] * 4


def test_collect_failures_names_the_run_and_its_exit_code() -> None:
    failures = _collect_failures([_result("ok"), _result("bad", exit_code=1)])
    assert len(failures) == 1
    assert "bad" in failures[0] and "1" in failures[0]


def test_collect_failures_is_empty_when_every_run_passed() -> None:
    assert _collect_failures([_result("a"), _result("b")]) == []
