"""UCI-000001 — the executing half: the gate CLI, the classifier, the runner, the three proofs.

WHY THIS IS A SECOND MODULE AND NOT MORE OF THE FIRST ONE.

``test_certification_integrity.py`` proves the LAWS, and it pays for real measurements to do it:
one ``inventory.build``, one ``contract.measure``. The four modules covered here cannot be proven
that way. ``classify.build`` costs a full measurement — 59.9s against this tree, measured — and
``suite``/``equivalence`` each run the whole test suite inside a frozen git extraction, several
times over, after pip-installing that extraction. A unit suite that paid those prices would BE the
expensive measurement it exists to check, and ``./verify.sh`` runs it on every commit.

So the expensive measurement is FORGED and everything around it executes for real. That is the
right split rather than a compromise, because none of these four modules decides anything about
coverage. They dispatch argv, match a line against a regex, assemble a pytest command line, and
compare two coverage reports that something else produced. Each one is a pure function of inputs a
test can state — and each one sat at 0.0% while the laws beneath them carried 790 lines of tests.

WHAT THE FORGERY COSTS, AND HOW THAT COST IS CONTAINED. A fake is the one thing here that can
drift from the real thing, so every fake returns the REAL dataclass — ``immutable.Extraction``,
``immutable.FrozenRun``, ``coverage_data.CoverageReport``, ``inventory.Inventory`` — never a
stand-in with matching attribute names. A renamed or retyped field then breaks these tests at the
same moment it breaks production. The two places that discipline would not reach are exercised
against real subprocesses instead: ``_combine`` really runs ``coverage combine``, and the frozen
extraction is really produced by ``git archive`` and really sealed.

Exit codes are asserted as LITERAL integers throughout. ``gate.EXIT_FAULT`` is an attribute
reference and proves nothing about its value, and a gate's exit code is its whole interface to the
shell.
"""

from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.certification_integrity import (
    classify,
    coverage_data,
    equivalence,
    gate,
    immutable,
    inventory,
    suite,
    surface,
)
from engine.certification_integrity.model import (
    CLASS_DEFENSIVE,
    CLASS_EXECUTABLE,
    CLASS_GENERATED,
    CLASS_IMPOSSIBLE,
    CLASS_UNREACHABLE,
    FILE_EXECUTABLE,
    REMEDY,
    ExecutableObject,
    FileRecord,
    IntegrityError,
    UncoveredLine,
)

REPO = Path(__file__).resolve().parents[3]
REPO_STR = str(REPO)

# --------------------------------------------------------------------------- shared fixtures
#
# Everything below builds the REAL dataclasses. A fake report is a plain dict only because
# ``contract.measure`` returns a plain dict.


def _coverage(files: dict[str, tuple[set[int], set[int]]]) -> coverage_data.CoverageReport:
    return coverage_data.CoverageReport(
        files={
            path: coverage_data.FileCoverage(path, frozenset(hit), frozenset(missed))
            for path, (hit, missed) in files.items()
        },
        branches_valid=4,
        branches_covered=2,
    )


def _law(
    law: str = "UCI-L-01",
    *,
    name: str = "every executable artifact is inside the denominator",
    status: str = "HOLDS",
    measured: object = 64,
    ceiling: object = 64,
    detail: str = "",
    offenders: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "law": law,
        "name": name,
        "status": status,
        "measured": measured,
        "ceiling": ceiling,
        "detail": detail,
        "offenders": list(offenders),
    }


def _report_document(
    *,
    status: str = "OPEN",
    laws: list[dict[str, Any]] | None = None,
    coverage_document: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """A report carrying exactly the keys ``gate._render`` reads, and no others.

    Hand-built rather than measured, so a status this working tree does not currently exhibit can
    still be rendered. Restricting it to the keys ``_render`` touches is deliberate: a fixture
    carrying the whole real document would keep passing after ``_render`` began reading a key that
    ``contract.measure`` had stopped emitting.
    """
    document: dict[str, Any] = {
        "declaration": "UCI-000001",
        "declaration_version": "1.0.0",
        "status": status,
        "inventory_digest": "9" * 64,
        "counts": {"laws": 6, "holds": 6, "refused": 0, "files": 1301, "objects": 14022},
        "totals": {
            "executable_statements": 150000,
            "measured_statements": 130000,
            "denominator_share_percent": 86.6667,
            "unmeasured_statements": 20000,
            "measured_coverage_percent": 96.89,
            "executable_coverage_percent": 84.0,
        },
        "scope_drift": {
            "coverage_scope": 40,
            "executable_surface": 1301,
            "governed_surface": 1269,
            "executable_not_in_coverage_scope": 70,
        },
        "laws": laws if laws is not None else [_law()],
    }
    if coverage_document is not None:
        document["coverage_document"] = coverage_document
    return document


def _inventory() -> inventory.Inventory:
    """A one-file inventory. The gate reports only its size and its digest."""
    record = FileRecord(
        path="engine/x.py",
        classification=FILE_EXECUTABLE,
        statements=3,
        covered=2,
        missing=1,
        measured=True,
        execution_paths=("test",),
        invocation_sources=("engine/tests/unit/test_x.py",),
        governing_authority="UCOS-COV-SCOPE-001 (declared denominator)",
        exclusion_reason=None,
        ast_statements=3,
    )
    return inventory.Inventory(
        files=(record,),
        objects=({"name": "engine/x.py", "kind": "module"},),
        totals={"files": 1},
        executable_outside_denominator=(),
        ungoverned_files=(),
        scope_drift={},
    )


class _Wiring:
    """What the gate asked its collaborators for, so the plumbing is asserted and not assumed."""

    def __init__(self) -> None:
        self.report: dict[str, Any] = _report_document()
        self.inventory = _inventory()
        self.sealed = "00-MASTER/UCI-000001/uci-ratchet.json"
        self.fault: Exception | None = None
        self.measure_calls: list[tuple[str, str | None]] = []
        self.build_calls: list[tuple[str, str | None]] = []
        self.write_calls: list[tuple[str, str, str | None]] = []
        self.seal_calls: list[tuple[str, str | None]] = []


@pytest.fixture
def wired(monkeypatch: pytest.MonkeyPatch) -> _Wiring:
    """``gate.main`` with its three expensive entry points replaced by recorders."""
    rec = _Wiring()

    def measure(root: str, *, coverage_xml: str | None = None) -> dict[str, Any]:
        rec.measure_calls.append((root, coverage_xml))
        if rec.fault is not None:
            raise rec.fault
        return rec.report

    def build(root: str, *, coverage_xml: str | None = None) -> inventory.Inventory:
        rec.build_calls.append((root, coverage_xml))
        return rec.inventory

    def write(root: str, path: str, *, coverage_xml: str | None = None) -> inventory.Inventory:
        rec.write_calls.append((root, path, coverage_xml))
        return rec.inventory

    def seal(root: str, *, coverage_xml: str | None = None) -> str:
        rec.seal_calls.append((root, coverage_xml))
        if rec.fault is not None:
            raise rec.fault
        return rec.sealed

    monkeypatch.setattr(gate, "measure", measure)
    monkeypatch.setattr(gate, "build_inventory", build)
    monkeypatch.setattr(gate, "write_inventory", write)
    monkeypatch.setattr(gate, "seal_ratchet", seal)
    return rec


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = gate.main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


# ------------------------------------------------------------------------------- the gate CLI
#
# ``engine/certification_integrity/gate.py`` was 95 units at 0.0%: three exit codes, seven flags
# and the render an operator actually reads, none of it executed by anything. The Makefile targets
# invoke it, so the only proof that ``--gate`` returns 1 rather than 0 on a refusal was that the
# source says so.


def test_the_gate_measures_the_current_directory_and_invents_no_coverage_path(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """``root`` is ``"."`` and ``coverage_xml`` is ``None`` unless an operator named one.

    Both matter. A gate that resolved its own root could measure a tree the operator is not
    standing in, and one that defaulted a coverage path could report a figure from a stale
    document while appearing to have been given none.
    """
    code, _out, _err = _run(capsys, "--gate", "--quiet")
    assert code == 0
    assert wired.measure_calls == [(".", None)]


def test_a_refused_law_closes_the_gate(wired: _Wiring, capsys: pytest.CaptureFixture[str]) -> None:
    wired.report = _report_document(
        status="CLOSED",
        laws=[_law(status="REFUSED", measured=70, ceiling=64, detail="6 more than the bound")],
    )
    code, _out, err = _run(capsys, "--gate")
    assert code == 1, "a measured refusal is exit 1 — CLOSED, not FAULT"
    assert "a blocking law was measured and REFUSED" in err


def test_the_fail_closed_verdict_is_opt_in(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """Without ``--gate`` this is a reporter, and a reporter that exited non-zero on a finding
    could not be used to look at a tree that has one."""
    wired.report = _report_document(status="CLOSED", laws=[_law(status="REFUSED")])
    code, _out, err = _run(capsys, "--quiet")
    assert code == 0
    assert err == "", "--quiet must silence the render on the CLOSED path too"


def test_a_measurement_that_could_not_be_taken_is_exit_two_and_names_its_cause(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """FAULT is not CLOSED. "the surface is fully governed" and "the surface could not be
    enumerated" are different facts, and collapsing them lets a broken enumerator certify an
    empty repository."""
    wired.fault = IntegrityError("the tracked-path boundary could not be established")
    code, out, err = _run(capsys, "--gate", "--json")
    assert code == 2
    assert "UCI-000001 FAULT: the tracked-path boundary could not be established" in err
    assert out == "", "a faulted run must not emit a report that could be read as a verdict"


def test_the_document_goes_to_stdout_and_the_render_goes_to_stderr(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """The separation is what makes ``--json`` pipeable: a render mixed into stdout would make
    every consumer of the report parse around prose."""
    code, out, err = _run(capsys, "--json")
    assert code == 0
    assert json.loads(out) == wired.report
    assert "UNIVERSAL CERTIFICATION INTEGRITY — UCI-000001" in err
    assert "UNIVERSAL CERTIFICATION INTEGRITY" not in out


def test_quiet_suppresses_the_render_and_nothing_else(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, err = _run(capsys, "--json", "--quiet")
    assert code == 0
    assert json.loads(out) == wired.report
    assert err == ""


def test_printing_the_inventory_takes_no_measurement(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--inventory`` short-circuits. Measuring anyway would make the cheap request cost the
    expensive one, and the gate documents itself as read-only here."""
    code, out, _err = _run(capsys, "--inventory")
    assert code == 0
    assert json.loads(out) == wired.inventory.as_document()
    assert wired.build_calls == [(".", None)]
    assert wired.measure_calls == [], "printing the inventory must not trigger a measurement"


def test_writing_the_inventory_names_the_file_and_reports_its_digest(
    wired: _Wiring, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = str(tmp_path / "coverage_gap_inventory.json")
    code, out, err = _run(capsys, "--write-inventory", target)
    assert code == 0
    assert wired.write_calls == [(".", target, None)]
    assert wired.measure_calls == []
    assert f"wrote {target}" in err
    assert wired.inventory.digest()[:16] in err
    assert out == "", "--write-inventory writes a file; it does not also print the document"


def test_the_inventory_write_is_silent_under_quiet(
    wired: _Wiring, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, _out, err = _run(capsys, "--write-inventory", str(tmp_path / "i.json"), "--quiet")
    assert code == 0
    assert err == ""


def test_the_inventory_flags_do_not_bypass_the_gate_when_the_gate_was_asked_for(
    wired: _Wiring, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The short circuit is conditional on ``--gate`` being absent. If it were not, writing an
    artifact would be a way to skip the verdict — which is the one thing the module's own header
    says regenerating an artifact must never be."""
    wired.report = _report_document(status="CLOSED", laws=[_law(status="REFUSED")])
    code, _out, _err = _run(
        capsys, "--write-inventory", str(tmp_path / "i.json"), "--gate", "--quiet"
    )
    assert code == 1
    assert wired.write_calls and wired.measure_calls == [(".", None)]


def test_sealing_the_ratchet_names_the_file_it_advanced(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    code, _out, err = _run(capsys, "--seal-ratchet", "--gate")
    assert code == 0
    assert wired.seal_calls == [(".", None)]
    assert f"sealed {wired.sealed}" in err


def test_a_seal_still_has_to_face_the_measurement_it_came_from(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """Sealing moves each bound only downward, so it cannot turn a refusal into a pass. The gate
    proves that by measuring AFTER sealing rather than reporting the seal as the outcome."""
    wired.report = _report_document(status="CLOSED", laws=[_law(status="REFUSED")])
    code, _out, _err = _run(capsys, "--seal-ratchet", "--gate", "--quiet")
    assert code == 1
    assert wired.seal_calls and wired.measure_calls


def test_a_coverage_document_named_on_the_command_line_reaches_every_reader(
    wired: _Wiring, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One flag, four readers. A path that reached the measurement but not the inventory would
    produce a report and an artifact describing two different runs."""
    named = str(tmp_path / "elsewhere.xml")
    code, _out, _err = _run(
        capsys,
        "--coverage-xml",
        named,
        "--write-inventory",
        str(tmp_path / "i.json"),
        "--seal-ratchet",
        "--gate",
        "--quiet",
    )
    assert code == 0
    assert wired.write_calls == [(".", str(tmp_path / "i.json"), named)]
    assert wired.seal_calls == [(".", named)]
    assert wired.measure_calls == [(".", named)]


def test_an_unknown_flag_is_refused_before_anything_is_measured(wired: _Wiring) -> None:
    with pytest.raises(SystemExit) as raised:
        gate.main(["--no-such-flag"])
    assert raised.value.code == 2, "argparse exits 2; a caller must not read it as a pass"
    assert wired.measure_calls == []


def test_the_package_entry_point_dispatches_to_the_gate() -> None:
    """``python -m engine.certification_integrity`` and the gate must be one command.

    Two entry points would be two places for the exit-code contract to be decided.
    """
    module = importlib.import_module("engine.certification_integrity.__main__")
    assert module.main is gate.main


# ------------------------------------------------------------------------------- the render
#
# The render is what an operator reads, and it is the only place a refusal explains itself. Both
# of its conditional regions are forged here, because this working tree exhibits neither.


def test_a_holding_law_carries_no_alarm_and_no_detail() -> None:
    rendered = gate._render(_report_document(laws=[_law(detail="unused when holding")]))
    assert "!!" not in rendered
    assert "unused when holding" not in rendered
    assert "a blocking law was measured and REFUSED" not in rendered


def test_a_refused_law_is_marked_and_the_first_six_offenders_are_named() -> None:
    """Six, not all of them. UCI-L-01 has 70 offenders on a bad day and a render that listed
    every one would bury the verdict it exists to deliver — but a render that listed none would
    make the refusal unactionable, so the cut is at six and the cut is asserted."""
    offenders = tuple(f"00-BOOK/tools/offender_{i}.py" for i in range(9))
    rendered = gate._render(
        _report_document(
            status="CLOSED",
            laws=[
                _law(status="HOLDS"),
                _law(
                    "UCI-L-02",
                    name="no executable artifact is ungoverned",
                    status="REFUSED",
                    measured=32,
                    ceiling=26,
                    detail="6 artifacts no authority claims",
                    offenders=offenders,
                ),
            ],
        )
    )
    assert "!! UCI-L-02" in rendered
    assert "   UCI-L-01" in rendered and "!! UCI-L-01" not in rendered
    assert "6 artifacts no authority claims" in rendered
    for named in offenders[:6]:
        assert f"- {named}" in rendered
    for withheld in offenders[6:]:
        assert withheld not in rendered
    assert rendered.endswith("a blocking law was measured and REFUSED — see the detail above")


def test_an_inconsistent_coverage_document_is_reported_above_the_status_line() -> None:
    """Placement is the point of ``lines[-2:-2]``.

    The banner says the per-file body of coverage.xml contradicts its own root element. Printed
    after ``STATUS``, it would read as a footnote to a verdict that was computed from the very
    document being impeached; printed above it, it qualifies the verdict.
    """
    rendered = gate._render(
        _report_document(
            coverage_document={
                "body_is_incomplete": True,
                "declared_statements": 130066,
                "statements": 55231,
                "files": 644,
                "missing_from_body": 74835,
                "missing_percent": 57.5,
            }
        )
    )
    lines = rendered.splitlines()
    banner = next(i for i, line in enumerate(lines) if "INTERNALLY INCONSISTENT" in line)
    status = next(i for i, line in enumerate(lines) if line.strip().startswith("STATUS"))
    assert banner < status, "the impeachment of the evidence must precede the verdict it qualifies"
    assert "130,066 statements" in rendered
    assert "55,231 in 644 files" in rendered
    assert "74,835 (57.5%)" in rendered


def test_a_consistent_coverage_document_adds_no_banner() -> None:
    rendered = gate._render(
        _report_document(coverage_document={"body_is_incomplete": False, "statements": 130066})
    )
    assert "INTERNALLY INCONSISTENT" not in rendered


def test_a_report_that_names_no_coverage_document_still_renders() -> None:
    """The key is optional: ``measure`` omits it when no coverage document was read at all."""
    rendered = gate._render(_report_document())
    assert "STATUS" in rendered
    assert rendered.splitlines()[-1].split(":")[-1].strip() == "OPEN"
    assert "9" * 16 in rendered, "the inventory digest is the provenance and must be shown"


# ------------------------------------------------------------------------------ the classifier
#
# ``classify.py`` was 105 units at 0.0%, which is the worst place in this package for a blind
# spot: classification decides what a repository OWES for an uncovered line, so a classifier
# nobody executes is a mechanism for retiring coverage debt without any test being written. Each
# rule is therefore fired on a line it must claim, and the default is proven to be the expensive
# one.


@pytest.mark.parametrize(
    ("source", "expected_class", "expected_rule"),
    [
        ("if TYPE_CHECKING:", CLASS_IMPOSSIBLE, "UCI-K-01"),
        ("from typing import Any", CLASS_IMPOSSIBLE, "UCI-K-01"),
        ("import typing", CLASS_IMPOSSIBLE, "UCI-K-01"),
        ('if __name__ == "__main__":', CLASS_IMPOSSIBLE, "UCI-K-02"),
        ("raise SystemExit(main())", CLASS_UNREACHABLE, "UCI-K-03"),
        ("sys.exit(1)", CLASS_UNREACHABLE, "UCI-K-03"),
        ("raise NotImplementedError", CLASS_DEFENSIVE, "UCI-K-04"),
        ("raise AssertionError('unreachable')", CLASS_DEFENSIVE, "UCI-K-04"),
        ("except OSError as exc:", CLASS_DEFENSIVE, "UCI-K-05"),
        ("except KeyboardInterrupt:", CLASS_DEFENSIVE, "UCI-K-05"),
        ("python = fallback  # pragma: no cover", CLASS_DEFENSIVE, "UCI-K-06"),
    ],
)
def test_every_rule_fires_on_a_line_it_claims(
    source: str, expected_class: str, expected_rule: str
) -> None:
    classification, rule, justification = classify.classify_line(source, "engine/x.py", "")
    assert (classification, rule) == (expected_class, expected_rule)
    assert justification, "a classification cheaper than executable must state why"


def test_every_declared_rule_is_reachable() -> None:
    """A rule no line can reach is an exemption class with no members and no cost.

    Asserted over ``RULES`` itself rather than over the table above, so adding a rule without
    adding a witness for it fails here instead of being silently untested.
    """
    fired = {rule for _cls, rule, _desc, _pattern in classify.RULES}
    witnessed = {
        classify.classify_line(source, "engine/x.py", "")[1]
        for source in (
            "if TYPE_CHECKING:",
            'if __name__ == "__main__":',
            "sys.exit(1)",
            "raise NotImplementedError",
            "except OSError:",
            "x = 1  # pragma: no cover",
        )
    }
    assert fired == witnessed, f"rules never witnessed: {sorted(fired - witnessed)}"


def test_the_default_classification_owes_a_test() -> None:
    """The cheap answer must be the expensive one, or silence retires debt."""
    classification, rule, justification = classify.classify_line(
        "value = compute(other)", "engine/x.py", ""
    )
    assert (classification, rule) == (CLASS_EXECUTABLE, "UCI-K-00")
    assert "owes a test" in justification
    assert REMEDY[classification] == "write tests"


def test_first_match_wins_so_rule_order_is_meaning() -> None:
    """A line matching two rules gets the earlier one. Stated in ``RULES``' own comment, and
    asserted here because the ordering is otherwise invisible."""
    classification, rule, _ = classify.classify_line(
        "if TYPE_CHECKING:  # pragma: no cover", "engine/x.py", ""
    )
    assert (classification, rule) == (CLASS_IMPOSSIBLE, "UCI-K-01")


def test_a_generated_marker_outranks_every_line_rule() -> None:
    """The remedy for generated output is to govern the generator, so the file-level fact wins
    over whatever the individual line happens to look like."""
    classification, rule, justification = classify.classify_line(
        "raise NotImplementedError", "engine/x.py", "# DO NOT EDIT — auto-generated by ukb.py"
    )
    assert (classification, rule) == (CLASS_GENERATED, "UCI-K-07")
    assert "govern the generator" in justification
    assert REMEDY[classification] == "govern"


def _uncovered(
    path: str, line: int, classification: str = CLASS_EXECUTABLE, **kw: Any
) -> UncoveredLine:
    return UncoveredLine(
        path=path,
        line=line,
        owner=kw.get("owner", f"{path}::thing"),
        source=kw.get("source", "value = compute()"),
        classification=classification,
        justification="UCI-K-00: test fixture",
    )


def test_the_plan_partitions_its_lines_by_class_and_by_owner() -> None:
    plan = classify.Plan(
        lines=(
            _uncovered("engine/a.py", 1),
            _uncovered("engine/a.py", 2),
            _uncovered("engine/b.py", 9, CLASS_DEFENSIVE),
        ),
        unmeasured_in_scope=(),
    )
    assert plan.by_class() == {CLASS_EXECUTABLE: 2, CLASS_DEFENSIVE: 1}
    assert plan.by_owner() == [("engine/a.py", 2), ("engine/b.py", 1)]
    assert plan.by_owner(limit=1) == [("engine/a.py", 2)]
    assert [line.line for line in plan.executable()] == [1, 2]


def test_the_plan_document_states_every_class_with_the_remedy_it_obliges() -> None:
    plan = classify.Plan(
        lines=(_uncovered("engine/a.py", 1), _uncovered("engine/b.py", 2, CLASS_IMPOSSIBLE)),
        unmeasured_in_scope=(),
    )
    document = classify.render(plan)
    assert "**Total uncovered lines measured:** 2" in document
    assert f"| `{CLASS_EXECUTABLE}` | 1 | 50.0% | {REMEDY[CLASS_EXECUTABLE]} |" in document
    assert f"| `{CLASS_IMPOSSIBLE}` | 1 | 50.0% | {REMEDY[CLASS_IMPOSSIBLE]} |" in document
    assert "`dead_code` is never assigned automatically" in document


def test_the_plan_document_survives_a_plan_with_no_uncovered_lines() -> None:
    """100% is the goal, so the document has to render AT the goal and not only short of it.

    Every table here is built by iterating the lines, so an empty plan exercises each loop's zero
    case at once. It also settles what ``render``'s ``if total else "—"`` share guard is worth:
    ``by_class()`` is derived from ``lines``, so the loop that would divide by zero cannot run when
    the total is zero. The guard is unreachable by construction rather than load-bearing — which is
    fine, and is recorded here so a later reader does not go looking for the input that reaches it.
    """
    document = classify.render(classify.Plan(lines=(), unmeasured_in_scope=()))
    assert "**Total uncovered lines measured:** 0" in document
    assert "0 lines carry no exemption" in document
    assert "| class | lines | share | remedy |" in document, "the header must survive an empty body"
    assert document.endswith("|---|---|---|\n"), "the sample table ends with its header and no rows"


def test_undescribed_files_are_reported_apart_from_uncovered_lines() -> None:
    """The 21x overstatement this section exists to prevent, asserted as a separation.

    Files the coverage document never mentions are named in their own section with their AST
    statement count, and are NOT added to the uncovered-line total. Folding them in produced a
    first draft claiming 79,008 lines owing tests against a coverage report showing 3,654.
    """
    absent = tuple(f"engine/absent/mod_{i:03d}.py" for i in range(45))
    plan = classify.Plan(
        lines=(_uncovered("engine/a.py", 1),),
        unmeasured_in_scope=absent,
        undescribed_statements=138582,
    )
    document = classify.render(plan)
    assert "**Total uncovered lines measured:** 1" in document
    assert "**45 files, 138,582 statements" in document
    assert "not assumed to be" in document
    assert all(f"- `{path}`" in document for path in absent[:40])
    assert "- … and 5 more" in document
    assert absent[44] not in document


def test_the_document_omits_the_undescribed_section_when_there_is_nothing_to_report() -> None:
    document = classify.render(
        classify.Plan(lines=(_uncovered("engine/a.py", 1),), unmeasured_in_scope=())
    )
    assert "does not describe" not in document


def test_a_pipe_in_a_source_line_is_escaped_so_the_table_survives() -> None:
    """``int | None`` is ordinary modern Python and an unescaped pipe silently ends the cell,
    which would corrupt every row after it in the rendered table."""
    plan = classify.Plan(
        lines=(_uncovered("engine/a.py", 7, source="def f(x: int | None) -> str | None:"),),
        unmeasured_in_scope=(),
    )
    document = classify.render(plan)
    assert r"int \| None" in document
    assert "int | None" not in document


# --------------------------------------------------------------------------- classify.build
#
# ``classify.build(".")`` costs a full inventory plus a full surface enumeration — 59.9s against
# this tree, measured — and ./verify.sh runs this file on every commit. So the two expensive
# enumerations are replaced by recorders and everything else in ``build`` runs for real, INCLUDING
# ``surface.read_text``: the sources it reads are written into ``tmp_path``, so the line-fetching
# closure, the head cache and the classifier all execute against real bytes on disk.


def _scope() -> surface.Scope:
    return surface.Scope(
        flag_packages=frozenset({"engine"}),
        source_paths=frozenset({"engine"}),
        excluded_packages={},
        testpaths=("engine/tests",),
        fail_under=90.0,
    )


def _object(module: str, *, missing: tuple[int, ...], measured: bool = True) -> ExecutableObject:
    return ExecutableObject(
        name=f"{module}::thing",
        kind="function",
        module=module,
        statements=10,
        covered=10 - len(missing),
        missing=len(missing),
        coverage_percent=0.0,
        tested=False,
        invoked=False,
        invocation_planes=(),
        measured=measured,
        missing_lines=missing,
    )


def _surface(root: str, objects: tuple[ExecutableObject, ...], coverage: Any) -> surface.Surface:
    return surface.Surface(
        root=root,
        scope=_scope(),
        objects=objects,
        measured_files=tuple(sorted({o.module for o in objects})),
        unmeasured_files=(),
        test_files=(),
        undeclared_files=(),
        engines=(),
        stages=(),
        coverage=coverage,
    )


def _file(path: str, *, measured: bool = True, ast_statements: int = 3) -> FileRecord:
    return FileRecord(
        path=path,
        classification=FILE_EXECUTABLE,
        statements=ast_statements,
        covered=0,
        missing=ast_statements,
        measured=measured,
        execution_paths=(),
        invocation_sources=(),
        governing_authority="UCOS-COV-SCOPE-001 (declared denominator)",
        exclusion_reason=None,
        ast_statements=ast_statements,
    )


@pytest.fixture
def enumerated(monkeypatch: pytest.MonkeyPatch):  # noqa: ANN201 - returns a local closure
    """Install the two enumerations ``classify.build`` would otherwise pay for."""

    def install(
        files: tuple[FileRecord, ...], objects: tuple[ExecutableObject, ...], coverage: Any
    ):
        monkeypatch.setattr(
            inventory,
            "build",
            lambda root, *, coverage_xml=None: inventory.Inventory(
                files=files,
                objects=(),
                totals={"files": len(files)},
                executable_outside_denominator=(),
                ungoverned_files=(),
                scope_drift={},
            ),
        )
        monkeypatch.setattr(
            surface,
            "build",
            lambda root, *, coverage_xml=None, paths=None: _surface(root, objects, coverage),
        )

    return install


def test_build_classifies_each_missing_line_against_the_file_it_came_from(
    tmp_path: Path, enumerated
) -> None:  # noqa: ANN001
    """One object, four missing lines, four different classes — read off real source."""
    module = "engine/sample.py"
    (tmp_path / "engine").mkdir()
    (tmp_path / module).write_text(
        "\n".join(
            [
                "import os",  # 1  executable
                "if TYPE_CHECKING:",  # 2  UCI-K-01 impossible
                "    raise NotImplementedError",  # 3  UCI-K-04 defensive
                "sys.exit(2)",  # 4  UCI-K-03 unreachable
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    enumerated(
        (_file(module),),
        (_object(module, missing=(1, 2, 3, 4)),),
        _coverage({module: ({5}, {1, 2, 3, 4})}),
    )

    plan = classify.build(str(tmp_path))

    assert [(line.line, line.classification) for line in plan.lines] == [
        (1, CLASS_EXECUTABLE),
        (2, CLASS_IMPOSSIBLE),
        (3, CLASS_DEFENSIVE),
        (4, CLASS_UNREACHABLE),
    ]
    assert plan.lines[0].source == "import os", "the source is quoted from disk, not reconstructed"
    assert plan.lines[0].owner == f"{module}::thing"
    assert plan.lines[1].justification.startswith("UCI-K-01: ")
    assert plan.unmeasured_in_scope == ()
    assert plan.undescribed_statements == 0


def test_a_file_the_coverage_document_never_describes_yields_no_uncovered_line(
    tmp_path: Path, enumerated
) -> None:  # noqa: ANN001
    """The 21x overstatement, prevented at its source rather than in the renderer.

    ``coverage.xml``'s body drops in-scope files, and absence there is indistinguishable from "no
    test imported it". So an undescribed file contributes to ``unmeasured_in_scope`` and to
    ``undescribed_statements`` — and contributes NOT ONE ``UncoveredLine``, because attributing its
    statements to ``executable`` would bill a rendering defect as coverage debt.
    """
    described, absent = "engine/described.py", "engine/absent.py"
    (tmp_path / "engine").mkdir()
    for name in (described, absent):
        (tmp_path / name).write_text("value = compute()\n", encoding="utf-8")
    enumerated(
        (_file(described), _file(absent, ast_statements=41)),
        (_object(described, missing=(1,)), _object(absent, missing=(1,))),
        _coverage({described: (set(), {1})}),
    )

    plan = classify.build(str(tmp_path))

    assert [line.path for line in plan.lines] == [described]
    assert plan.unmeasured_in_scope == (absent,)
    assert plan.undescribed_statements == 41


def test_an_unmeasured_object_and_an_out_of_range_line_are_both_handled(
    tmp_path: Path, enumerated
) -> None:
    """Two guards, one test, because both are answers to an inconsistent measurement.

    An object outside the denominator is skipped entirely — classifying it would report debt
    against a file no coverage figure covers. A missing line number past the end of the file is
    kept but quoted as the empty string, which the default rule classifies executable: the line
    was measured missing, so it is owed, and the report says so without inventing a source line
    it could not read.
    """
    inside, outside = "engine/inside.py", "engine/outside.py"
    (tmp_path / "engine").mkdir()
    for name in (inside, outside):
        (tmp_path / name).write_text("value = compute()\n", encoding="utf-8")
    enumerated(
        (_file(inside), _file(outside)),
        (
            _object(inside, missing=(1, 4096)),
            _object(outside, missing=(1,), measured=False),
        ),
        _coverage({inside: (set(), {1, 4096}), outside: (set(), {1})}),
    )

    plan = classify.build(str(tmp_path))

    assert [line.path for line in plan.lines] == [inside, inside]
    assert plan.lines[1].line == 4096
    assert plan.lines[1].source == ""
    assert plan.lines[1].classification == CLASS_EXECUTABLE


def test_an_object_with_nothing_missing_is_not_reported(tmp_path: Path, enumerated) -> None:  # noqa: ANN001
    module = "engine/covered.py"
    (tmp_path / "engine").mkdir()
    (tmp_path / module).write_text("value = compute()\n", encoding="utf-8")
    enumerated((_file(module),), (_object(module, missing=()),), _coverage({module: ({1}, set())}))
    assert classify.build(str(tmp_path)).lines == ()


def test_build_reports_nothing_undescribed_when_there_is_no_coverage_document(
    tmp_path: Path, enumerated
) -> None:  # noqa: ANN001
    """No measurement is not a measurement of zero.

    With ``surf.coverage is None`` nothing is described, so no line can be classified — and
    ``unmeasured_in_scope`` stays empty too, because naming every file as undescribed when there
    is no document at all would report the absence of a run as a property of the repository.
    """
    module = "engine/sample.py"
    (tmp_path / "engine").mkdir()
    (tmp_path / module).write_text("value = compute()\n", encoding="utf-8")
    enumerated((_file(module),), (_object(module, missing=(1,)),), None)

    plan = classify.build(str(tmp_path))
    assert plan.lines == ()
    assert plan.unmeasured_in_scope == ()
    assert plan.undescribed_statements == 0


def test_a_file_is_read_once_however_many_objects_it_owns(
    tmp_path: Path, enumerated, monkeypatch: pytest.MonkeyPatch
) -> None:  # noqa: ANN001
    """The cache is not an optimisation detail: ``build`` classifies every uncovered line in the
    repository, and re-reading a file per object would read the same 130,000-statement corpus once
    per function in it. The real reader is kept and only counted, so the bytes stay real."""
    module = "engine/shared.py"
    (tmp_path / "engine").mkdir()
    (tmp_path / module).write_text("def a():\n    return 1\n", encoding="utf-8")
    reads: list[str] = []
    real = surface.read_text

    def counting(root: str, relative: str) -> str:
        reads.append(relative)
        return real(root, relative)

    monkeypatch.setattr(surface, "read_text", counting)
    enumerated(
        (_file(module),),
        (_object(module, missing=(1,)), _object(module, missing=(2,))),
        _coverage({module: (set(), {1, 2})}),
    )

    plan = classify.build(str(tmp_path))

    assert [line.line for line in plan.lines] == [1, 2]
    assert reads == [module], f"the file was read {len(reads)} times for two objects"


def test_a_short_undescribed_list_is_reported_whole() -> None:
    """Below the sample size there is no remainder, so the document must not claim "and 0 more"."""
    document = classify.render(
        classify.Plan(
            lines=(), unmeasured_in_scope=("engine/a.py", "engine/b.py"), undescribed_statements=7
        ),
        sample=40,
    )
    assert "**2 files, 7 statements" in document
    assert "- `engine/a.py`" in document
    assert "- `engine/b.py`" in document
    assert "… and" not in document


# --------------------------------------------------------------------------- suite.py
#
# ``suite`` assembles a command line and reads pytest's own summary back. Both are pure functions
# of stated inputs, and both were at 0% for the parts that matter: the runner had 40 of its 68
# statements unexecuted, which included every line that pins the environment two runs are supposed
# to share. Rules 8-11 all compare two runs, so a harness that silently differed between them
# would make every one of those four proofs a measurement of the harness.


def test_pytest_argv_pins_the_four_things_two_runs_must_share() -> None:
    argv = suite.pytest_argv()
    assert (
        argv[0] == immutable.PYTHON_PLACEHOLDER
    ), "the interpreter is substituted by the extraction, so the argv must not name this one"
    assert argv[1:3] == ["-m", "pytest"]
    assert "-p" in argv and "no:cacheprovider" in argv, "run B must not be a function of run A"
    assert (
        argv[argv.index("-o") + 1] == "addopts="
    ), "the project's own --cov flags are cleared and re-added from the declared scope"
    assert "--cov-report=xml:coverage.xml" in argv
    assert "--cov-fail-under=0" in argv, (
        "the floor is applied once over combined data; a shard failing it alone would abort before "
        "writing its data and the combine would then measure less"
    )
    assert "engine.certification_integrity.pytest_shuffle" not in argv


def test_pytest_argv_orders_extras_before_targets_and_keeps_targets_last() -> None:
    """pytest reads positional targets after options, so the order is not cosmetic."""
    argv = suite.pytest_argv(
        targets=["engine/tests", "platform/tests"],
        xml_path=".uci-coverage-whole.xml",
        shuffle_seed=7,
        extra=["--cov=engine", "-x"],
    )
    assert argv[-2:] == ["engine/tests", "platform/tests"]
    assert argv.index("--cov=engine") < argv.index("engine/tests")
    assert "--cov-report=xml:.uci-coverage-whole.xml" in argv
    plugin = argv.index("engine.certification_integrity.pytest_shuffle")
    assert argv[plugin - 1] == "-p"


def test_a_run_that_measures_nothing_asks_for_no_coverage_report() -> None:
    argv = suite.pytest_argv(coverage=False, extra=["--co"])
    assert not [flag for flag in argv if flag.startswith("--cov")]
    assert argv[-1] == "--co"


def test_cov_flags_are_sorted_so_the_denominator_is_stated_once_per_run() -> None:
    """The flags become part of the recorded command, and an unordered set would make two runs
    over one identical denominator record two different commands."""
    assert suite.cov_flags(["platform", "engine", "engine"]) == [
        "--cov=engine",
        "--cov=engine",
        "--cov=platform",
    ]
    assert suite.cov_flags([]) == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1234 passed, 5 skipped in 61.42s", {"passed": 1234, "skipped": 5}),
        ("3 failed, 1200 passed in 90s", {"failed": 3, "passed": 1200}),
        ("2 error, 1 errors", {"error": 3}),
        ("7 xfailed, 2 xpassed, 4 deselected", {"xfailed": 7, "xpassed": 2, "deselected": 4}),
        ("", {}),
        ("collected 0 items", {}),
    ],
)
def test_parse_counts_reads_pytests_own_summary(text: str, expected: dict[str, int]) -> None:
    """``error`` and ``errors`` are pytest's singular and plural of one outcome, so they collapse.
    Kept apart, a run reporting ``1 error`` and a run reporting ``1 errors`` would compare unequal
    while describing the same failure."""
    assert suite.parse_counts(text) == expected


def test_the_result_counts_only_the_tests_that_executed() -> None:
    result = suite.SuiteResult(
        label="whole",
        exit_code=0,
        duration_seconds=61.4249,
        counts={"passed": 1200, "failed": 3, "skipped": 40, "deselected": 900},
        coverage_xml="build/x.xml",
        report=_coverage({"engine/x.py": ({1, 2}, {3})}),
        stdout_tail="out",
        stderr_tail="err",
    )
    assert result.test_count == 1203, "skipped and deselected tests did not execute"
    assert result.passed is True
    record = result.as_record()
    assert record["duration_seconds"] == 61.425
    assert record["test_count"] == 1203
    assert record["coverage"] == {
        "statements": 3,
        "covered": 2,
        "percent": 66.6667,
        "branches_valid": 4,
        "branches_covered": 2,
        "digest": result.report.digest(),
        "files": 1,
    }


def test_a_failing_run_with_no_measurement_records_the_absence_as_null() -> None:
    """``None`` and a report of zero are different facts and must not serialise alike."""
    result = suite.SuiteResult(
        label="shard-2",
        exit_code=1,
        duration_seconds=0.5,
        counts={},
        coverage_xml="",
        report=None,
        stdout_tail="",
        stderr_tail="",
    )
    assert result.passed is False
    assert result.test_count == 0
    assert result.as_record()["coverage"] is None


# --------------------------------------------------------------------------- run_in_extraction
#
# The frozen extraction is faked; the coverage document it produces is REAL and is parsed by the
# real ``coverage_data.parse``. That split is the whole point: what ``run_in_extraction`` decides
# is the argv, the environment and which tree the denominator is read from, and none of those
# decisions need a venv built or a suite run to be checked. What it must not be allowed to do is
# read a coverage figure it did not measure, so the refusal path is exercised by simply not
# writing the document the run was supposed to write.

_XML = (
    '<?xml version="1.0" ?>\n'
    '<coverage lines-valid="{valid}" lines-covered="{covered}" '
    'branches-valid="{bvalid}" branches-covered="{bcovered}">'
    "<sources><source>{root}</source></sources>"
    '<packages><package name="engine"><classes>'
    '<class filename="{name}"><lines>{lines}</lines></class>'
    "</classes></package></packages></coverage>\n"
)


def _write_coverage_xml(
    path: Path,
    root: Path,
    name: str = "engine/x.py",
    *,
    hit: tuple[int, ...] = (1,),
    missed: tuple[int, ...] = (2,),
    branches: tuple[int, int] = (2, 1),
) -> None:
    """A real coverage document, written where the run would have written it.

    Real rather than a stubbed ``CoverageReport`` because the reader is the part of this path that
    can be wrong: ``coverage_data.parse`` resolves ``filename`` against ``<sources>``, and a fake
    report would skip the resolution these runs depend on for their paths to compare at all.
    """
    lines = "".join(f'<line number="{n}" hits="1"/>' for n in hit)
    lines += "".join(f'<line number="{n}" hits="0"/>' for n in missed)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _XML.format(
            valid=len(hit) + len(missed),
            covered=len(hit),
            bvalid=branches[0],
            bcovered=branches[1],
            root=root,
            name=name,
            lines=lines,
        ),
        encoding="utf-8",
    )


class _Runner:
    """Records what ``run_in_extraction`` asked the extraction layer to do."""

    def __init__(self, extraction: immutable.Extraction) -> None:
        self.extraction = extraction
        self.prepare_calls: list[tuple[str, str, str | None]] = []
        self.run_calls: list[dict[str, Any]] = []
        self.scope_calls: list[str] = []
        self.writes_xml = True
        self.exit_code = 0
        self.stdout = "1200 passed, 40 skipped in 61.42s"
        self.stderr = ""

    @property
    def last(self) -> dict[str, Any]:
        return self.run_calls[-1]

    @property
    def command(self) -> tuple[str, ...]:
        return self.last["command"]


@pytest.fixture
def runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> _Runner:
    frozen_root = tmp_path / "extraction"
    (frozen_root / "engine").mkdir(parents=True)
    (frozen_root / "engine" / "x.py").write_text("value = compute()\n", encoding="utf-8")
    extraction = immutable.Extraction(
        sha="d" * 40,
        root=str(frozen_root),
        python=str(frozen_root / ".venv" / "bin" / "python"),
        reused=False,
        prepare_seconds=0.5,
        sealed_sha="e" * 40,
    )
    rec = _Runner(extraction)
    fingerprint = immutable.Fingerprint(
        head="a" * 40, porcelain_digest="b" * 64, tracked_digest="c" * 64, dirty_entries=0
    )

    def prepare(
        root: str,
        sha: str,
        *,
        workspace: str | None = None,
        build_venv: bool = True,
        reuse: bool = True,
    ) -> immutable.Extraction:
        rec.prepare_calls.append((root, sha, workspace))
        return extraction

    def run(
        root: str,
        command: list[str],
        *,
        sha: str | None = None,
        workspace: str | None = None,
        env: dict[str, str] | None = None,
        collect: dict[str, str] | None = None,
        build_venv: bool = True,
        reuse: bool = True,
        timeout: float | None = None,
    ) -> immutable.FrozenRun:
        rec.run_calls.append(
            {
                "root": root,
                "command": tuple(command),
                "sha": sha,
                "workspace": workspace,
                "env": dict(env or {}),
                "collect": dict(collect or {}),
                "timeout": timeout,
            }
        )
        if rec.writes_xml:
            # A run asked for no XML report writes none. The fake mirrors that rather than
            # inventing a document, so the coverage=False path is exercised as it really runs.
            asked = [arg for arg in command if arg.startswith("--cov-report=xml:")]
            for flag in asked:
                relative = flag.split(":", 1)[1]
                _write_coverage_xml(frozen_root / relative, frozen_root)
                for source, destination in (collect or {}).items():
                    shutil.copy2(frozen_root / source, destination)
        return immutable.FrozenRun(
            sha=extraction.sha,
            command=tuple(command),
            exit_code=rec.exit_code,
            duration_seconds=1.0,
            stdout_tail=rec.stdout,
            stderr_tail=rec.stderr,
            before=fingerprint,
            after=fingerprint,
            extraction=extraction,
        )

    def read_scope(root: str) -> surface.Scope:
        rec.scope_calls.append(root)
        return surface.Scope(
            flag_packages=frozenset({"platform", "engine"}),
            source_paths=frozenset({"engine", "platform"}),
            excluded_packages={},
            testpaths=("engine/tests",),
            fail_under=90.0,
        )

    monkeypatch.setattr(immutable, "prepare", prepare)
    monkeypatch.setattr(immutable, "run", run)
    monkeypatch.setattr(surface, "read_scope", read_scope)
    return rec


def test_the_denominator_is_read_from_the_frozen_tree_and_not_from_this_one(
    runner: _Runner,
) -> None:
    """A figure measured over a scope the commit never declared is attributable to no commit.

    So ``prepare`` runs FIRST and the scope is read from the extraction's root. Reading it from the
    caller's working tree would let an uncommitted ``pyproject.toml`` decide the denominator of a
    measurement labelled with a committed sha.
    """
    result, frozen = suite.run_in_extraction(root=".", sha="d" * 40, label="whole")

    assert runner.scope_calls == [runner.extraction.root]
    assert runner.prepare_calls == [(".", "d" * 40, None)]
    assert "--cov=engine" in runner.command and "--cov=platform" in runner.command
    assert result.label == "whole"
    assert result.exit_code == 0
    assert result.counts == {"passed": 1200, "skipped": 40}
    assert result.report is not None
    assert set(result.report.files) == {"engine/x.py"}
    assert frozen.extraction is runner.extraction


def test_the_environment_two_runs_must_share_is_stated_and_never_inherited(runner: _Runner) -> None:
    """Exactly two variables, both set explicitly. ``COVERAGE_FILE`` is per run because an
    ambient value once corrupted a parent's data file, and ``PYTHONHASHSEED`` is pinned because
    unpinned set iteration would let the harness manufacture the drift Rule 11 reports."""
    suite.run_in_extraction(root=".", sha="d" * 40, label="whole", timeout=900.0)

    assert runner.last["env"] == {
        "PYTHONHASHSEED": "0",
        "COVERAGE_FILE": ".uci-coverage-whole.data",
    }
    assert runner.last["timeout"] == 900.0
    assert runner.last["sha"] == "d" * 40


def test_a_seeded_run_carries_its_seed_into_the_environment_and_loads_the_shuffler(
    runner: _Runner,
) -> None:
    suite.run_in_extraction(root=".", sha="d" * 40, label="order-seed-7", shuffle_seed=7)

    assert runner.last["env"]["UCI_SHUFFLE_SEED"] == "7"
    assert "engine.certification_integrity.pytest_shuffle" in runner.command
    assert runner.last["env"]["COVERAGE_FILE"] == ".uci-coverage-order-seed-7.data"


def test_a_caller_supplied_coverage_file_keeps_two_runs_off_one_data_file(runner: _Runner) -> None:
    suite.run_in_extraction(
        root=".", sha="d" * 40, label="shard-1", coverage_file=".uci-shard-1.data"
    )
    assert runner.last["env"]["COVERAGE_FILE"] == ".uci-shard-1.data"


def test_a_caller_supplied_scope_is_used_verbatim_and_the_frozen_declaration_is_not_read(
    runner: _Runner,
) -> None:
    """Shard runs pass the scope down so all shards and the whole run share one denominator."""
    suite.run_in_extraction(
        root=".", sha="d" * 40, label="shard-1", scope_packages=["engine"], targets=["engine/tests"]
    )
    assert runner.scope_calls == [], "the scope was supplied, so nothing needed reading"
    assert "--cov=engine" in runner.command
    assert "--cov=platform" not in runner.command
    assert runner.command[-1] == "engine/tests"


def test_a_run_that_measures_nothing_asks_for_no_scope_and_reads_no_report(runner: _Runner) -> None:
    result, _ = suite.run_in_extraction(
        root=".", sha="d" * 40, label="collect-only", coverage=False, extra=["--co"]
    )
    assert runner.scope_calls == []
    assert not [flag for flag in runner.command if flag.startswith("--cov")]
    assert result.report is None
    assert result.coverage_xml.endswith(".uci-coverage-collect-only.xml")


def test_an_absent_measurement_is_refused_rather_than_read_as_zero(runner: _Runner) -> None:
    """The defect this refusal exists for: a run that crashed before writing coverage would
    otherwise be compared as a run that covered nothing, and two such runs agree perfectly."""
    runner.writes_xml = False
    runner.exit_code = 1
    with pytest.raises(IntegrityError) as raised:
        suite.run_in_extraction(root=".", sha="d" * 40, label="whole")
    message = str(raised.value)
    assert "run whole produced no coverage measurement at .uci-coverage-whole.xml" in message
    assert "refusing to treat an absent measurement as a zero one" in message


def test_a_collected_document_is_the_path_the_result_reports(
    runner: _Runner, tmp_path: Path
) -> None:
    """The extraction is deleted, so a result naming a path inside it would name nothing."""
    destination = tmp_path / "evidence" / "whole.xml"
    destination.parent.mkdir()
    result, _ = suite.run_in_extraction(
        root=".", sha="d" * 40, label="whole", collect_xml_to=str(destination)
    )
    assert runner.last["collect"] == {".uci-coverage-whole.xml": str(destination)}
    assert result.coverage_xml == str(destination)
    assert destination.exists(), "the collected artifact must outlive the extraction"


def test_the_counts_are_read_from_both_streams_of_the_run(runner: _Runner) -> None:
    """pytest's summary lands on stdout, but a crash reports on stderr, and a run that failed
    with its counts on the wrong stream must not be recorded as a run of zero tests."""
    runner.stdout = ""
    runner.stderr = "3 failed, 1197 passed in 61.42s"
    runner.exit_code = 1
    result, _ = suite.run_in_extraction(root=".", sha="d" * 40, label="whole")
    assert result.counts == {"failed": 3, "passed": 1197}
    assert result.test_count == 1200
    assert result.passed is False


# --------------------------------------------------------------------------- equivalence.py
#
# Rules 8, 9, 10 and 11 each run the whole suite between two and a hundred times inside a frozen
# extraction. What they DECIDE is which runs happen, what each one is labelled, which report is the
# baseline, and what a disagreement is called. None of that requires the suite to run, so
# ``suite.run_in_extraction`` is scripted per label — and every divergence these rules exist to
# catch is then INDUCED rather than waited for, which is the only way to witness a refusal that a
# healthy repository never produces.


class _Runs:
    """A scripted ``suite.run_in_extraction``: reports, exit codes and counts keyed by label."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.default = _coverage({"engine/x.py": ({1, 2}, {3})})
        self.reports: dict[str, Any] = {}
        self.exit_codes: dict[str, int] = {}
        self.counts: dict[str, dict[str, int]] = {}

    @property
    def labels(self) -> list[str]:
        return [call["label"] for call in self.calls]

    def call(self, label: str) -> dict[str, Any]:
        return next(c for c in self.calls if c["label"] == label)


@pytest.fixture
def runs(monkeypatch: pytest.MonkeyPatch) -> _Runs:
    rec = _Runs()

    def run_in_extraction(**kwargs: Any) -> tuple[suite.SuiteResult, None]:
        rec.calls.append(kwargs)
        label = kwargs["label"]
        return (
            suite.SuiteResult(
                label=label,
                exit_code=rec.exit_codes.get(label, 0),
                duration_seconds=1.0,
                counts=rec.counts.get(label, {"passed": 10}),
                coverage_xml=kwargs.get("collect_xml_to") or f".uci-coverage-{label}.xml",
                report=rec.reports.get(label, rec.default),
                stdout_tail="10 passed",
                stderr_tail="",
            ),
            None,
        )

    monkeypatch.setattr(suite, "run_in_extraction", run_in_extraction)
    return rec


SHA = "f" * 40
DIVERGENT = _coverage({"engine/x.py": ({1}, {2, 3})})


@pytest.mark.parametrize("count", [1, 0, -1])
def test_reproducibility_over_fewer_than_two_runs_is_refused(count: int, runs: _Runs) -> None:
    """One run is not a measurement of reproducibility, and it would report success forever."""
    with pytest.raises(IntegrityError) as raised:
        equivalence.reproducibility(".", SHA, runs=count)
    assert "at least two runs are required for the comparison to exist" in str(raised.value)
    assert runs.calls == [], "the refusal must come before the expense, not after it"


def test_three_identical_runs_hold_on_two_comparisons(runs: _Runs) -> None:
    """N-1 comparisons, because set equality is transitive and the evidence stays linear in N."""
    finding = equivalence.reproducibility(".", SHA, runs=3)

    assert runs.labels == ["repro-1", "repro-2", "repro-3"]
    assert finding.rule == "Rule 8/11"
    assert finding.question == f"are 3 independent runs over the frozen tree {'f' * 12} identical?"
    assert len(finding.runs) == 3
    assert [c["second_label"] for c in finding.comparisons] == ["repro-2", "repro-3"]
    assert {c["first_label"] for c in finding.comparisons} == {"repro-1"}
    assert finding.identical is True
    assert finding.failures == []
    assert finding.holds is True
    assert finding.as_record()["holds"] is True


def test_one_divergent_run_is_reported_against_the_baseline_and_the_others_still_agree(
    runs: _Runs,
) -> None:
    runs.reports["repro-2"] = DIVERGENT
    finding = equivalence.reproducibility(".", SHA, runs=3)

    by_second = {c["second_label"]: c for c in finding.comparisons}
    assert by_second["repro-2"]["identical"] is False
    assert by_second["repro-2"]["files_with_differing_lines"] == {
        "engine/x.py": {"covered_only_in_first": [2], "covered_only_in_second": []}
    }
    assert by_second["repro-3"]["identical"] is True
    assert finding.identical is False
    assert finding.holds is False
    assert finding.failures == [], "the runs all exited 0; only their coverage disagreed"


def test_a_run_that_measured_nothing_is_named_rather_than_compared(runs: _Runs) -> None:
    """A missing measurement is not a measurement of zero, so no diff is manufactured for it."""
    runs.reports["repro-3"] = None
    finding = equivalence.reproducibility(".", SHA, runs=3)

    absent = finding.comparisons[-1]
    assert absent == {
        "first": "repro-1",
        "second": "repro-3",
        "identical": False,
        "reason": "a run produced no coverage measurement",
    }
    assert "first_label" not in absent, "there is no diff here, so it must not look like one"
    assert finding.identical is False


def test_a_failing_run_is_a_failure_even_when_every_run_agreed(runs: _Runs) -> None:
    """Identical coverage across three failing runs is perfect reproducibility of a broken suite,
    so ``identical`` and ``holds`` have to be able to disagree."""
    runs.exit_codes["repro-2"] = 1
    runs.counts["repro-3"] = {}
    runs.exit_codes["repro-3"] = 2
    finding = equivalence.reproducibility(".", SHA, runs=3)

    assert finding.identical is True
    assert finding.holds is False
    assert finding.failures == [
        "repro-2: pytest exited 1 (counts={'passed': 10})",
        "repro-3: pytest exited 2 (counts=unparsed)",
    ]


def test_each_run_collects_its_own_document_under_the_directory_it_was_given(
    runs: _Runs, tmp_path: Path
) -> None:
    """Every run writes to the same relative path inside the extraction, so without a per-run
    destination the evidence of run 1 would be run 3's document under run 1's name."""
    finding = equivalence.reproducibility(
        ".", SHA, runs=2, evidence_dir=str(tmp_path), targets=["engine/tests"], timeout=900.0
    )
    assert [c["collect_xml_to"] for c in runs.calls] == [
        os.path.join(str(tmp_path), "coverage-repro-1.xml"),
        os.path.join(str(tmp_path), "coverage-repro-2.xml"),
    ]
    assert {c["targets"][0] for c in runs.calls} == {"engine/tests"}
    assert {c["timeout"] for c in runs.calls} == {900.0}
    assert finding.holds is True


def test_a_run_with_no_evidence_directory_collects_nothing(runs: _Runs) -> None:
    equivalence.reproducibility(".", SHA, runs=2)
    assert [c["collect_xml_to"] for c in runs.calls] == [None, None]


def test_the_declared_order_is_the_baseline_that_permutations_are_compared_against(
    runs: _Runs,
) -> None:
    """Comparing permutations only with each other answers the wrong question.

    Three shuffled runs can agree perfectly with one another and still differ from the order the
    repository actually runs, which is the order every other verdict in the repository was measured
    under. So the unseeded run is element 0 and every permutation is compared against it.
    """
    finding = equivalence.order_independence(".", SHA, seeds=[1, 7])

    assert runs.labels == ["order-declared", "order-seed-1", "order-seed-7"]
    assert runs.call("order-declared").get("shuffle_seed") is None
    assert [runs.call(f"order-seed-{s}")["shuffle_seed"] for s in (1, 7)] == [1, 7]
    assert finding.rule == "Rule 9"
    assert "2 randomized permutations agree with the declared order" in finding.question
    assert [c["first_label"] for c in finding.comparisons] == ["order-declared"] * 2
    assert finding.holds is True


def test_each_permutation_record_names_the_seed_that_produced_it(runs: _Runs) -> None:
    """A record that cannot name its seed cannot be replayed, and Rule 9's whole claim is that
    the permutation is reproducible from the seed."""
    finding = equivalence.order_independence(".", SHA, seeds=[3])
    assert "seed" not in finding.runs[0], "the declared order was not seeded"
    assert finding.runs[0]["label"] == "order-declared"
    assert finding.runs[1]["seed"] == 3


def test_a_permutation_that_changes_the_coverage_refuses(runs: _Runs) -> None:
    runs.reports["order-seed-7"] = DIVERGENT
    finding = equivalence.order_independence(".", SHA, seeds=[1, 7])
    assert finding.identical is False
    assert finding.holds is False
    assert {c["second_label"]: c["identical"] for c in finding.comparisons} == {
        "order-seed-1": True,
        "order-seed-7": False,
    }


def test_permutations_collect_their_evidence_under_their_own_labels(
    runs: _Runs, tmp_path: Path
) -> None:
    equivalence.order_independence(".", SHA, seeds=[5], evidence_dir=str(tmp_path))
    assert [c["collect_xml_to"] for c in runs.calls] == [
        os.path.join(str(tmp_path), "coverage-order-declared.xml"),
        os.path.join(str(tmp_path), "coverage-order-seed-5.xml"),
    ]


def test_no_permutation_is_still_a_measurement_of_the_declared_order(runs: _Runs) -> None:
    """``seeds=[]`` runs once and compares nothing. It holds vacuously, and it must not raise:
    ``_compare_all`` reads ``results[0]``, so the single-run case is a real input to it."""
    finding = equivalence.order_independence(".", SHA, seeds=[])
    assert runs.labels == ["order-declared"]
    assert finding.comparisons == []
    assert finding.identical is True
    assert finding.holds is True


# --------------------------------------------------------------------------- Rule 10
#
# ``partition`` and ``discover_test_modules`` run for real over real files in ``tmp_path`` — they
# are the part of the shard proof that decides what each shard measures, and faking them would
# leave the proof's population unexamined. ``_combine`` is replaced by a recorder that writes a
# real coverage document, and the real ``coverage_data.parse`` reads it back; ``_combine`` itself
# is then exercised against real ``coverage`` subprocesses in the section after this one.


class _Sharded:
    def __init__(self, extraction: immutable.Extraction, root: Path) -> None:
        self.extraction = extraction
        self.root = root
        self.combine_calls: list[tuple[str, str, list[str]]] = []
        #: what the combined document says, as (hit, missed, branch totals)
        self.combined: tuple[tuple[int, ...], tuple[int, ...], tuple[int, int]] = (
            (1, 2),
            (3,),
            (4, 2),
        )


@pytest.fixture
def sharded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runs: _Runs) -> _Sharded:
    frozen_root = tmp_path / "extraction"
    (frozen_root / "engine").mkdir(parents=True)
    (frozen_root / "engine" / "x.py").write_text("value = compute()\n", encoding="utf-8")
    tests = frozen_root / "engine" / "tests" / "unit"
    tests.mkdir(parents=True)
    for name in ("test_a.py", "test_b.py", "test_c.py", "test_d.py", "conftest.py"):
        (tests / name).write_text("", encoding="utf-8")
    extraction = immutable.Extraction(
        sha=SHA,
        root=str(frozen_root),
        python=str(frozen_root / ".venv" / "bin" / "python"),
        reused=True,
        prepare_seconds=0.1,
    )
    rec = _Sharded(extraction, frozen_root)

    def combine(root: str, python: str, data_files: list[str]) -> str:
        rec.combine_calls.append((root, python, list(data_files)))
        hit, missed, branches = rec.combined
        target = frozen_root / ".uci-combined.xml"
        _write_coverage_xml(target, frozen_root, hit=hit, missed=missed, branches=branches)
        return str(target)

    monkeypatch.setattr(immutable, "prepare", lambda root, sha, *, workspace=None, **kw: extraction)
    monkeypatch.setattr(
        surface,
        "read_scope",
        lambda root: surface.Scope(
            flag_packages=frozenset({"engine"}),
            source_paths=frozenset({"engine"}),
            excluded_packages={},
            testpaths=("engine/tests",),
            fail_under=90.0,
        ),
    )
    monkeypatch.setattr(equivalence, "_combine", combine)
    return rec


def test_combining_the_shards_equals_the_whole_run(runs: _Runs, sharded: _Sharded) -> None:
    finding = equivalence.shard_equivalence(".", SHA, shards=2)

    assert runs.labels == ["whole", "shard-1", "shard-2"]
    assert finding.rule == "Rule 10"
    assert finding.question == f"does combining 2 shards equal one full execution over {'f' * 12}?"
    assert finding.identical is True
    assert finding.failures == []
    assert finding.holds is True
    assert len(finding.comparisons) == 1
    assert finding.comparisons[0]["first_label"] == "whole"
    assert finding.comparisons[0]["second_label"] == "combined-shards"


def test_the_shards_partition_the_discovered_modules_and_nothing_else(
    runs: _Runs, sharded: _Sharded
) -> None:
    """``conftest.py`` is not a test module, and a shard population that included it would send
    pytest a target that collects nothing while the whole run still collected four files."""
    equivalence.shard_equivalence(".", SHA, shards=2)

    targets = [runs.call(f"shard-{i}")["targets"] for i in (1, 2)]
    assert sorted(t for group in targets for t in group) == [
        "engine/tests/unit/test_a.py",
        "engine/tests/unit/test_b.py",
        "engine/tests/unit/test_c.py",
        "engine/tests/unit/test_d.py",
    ]
    assert "targets" not in runs.call("whole"), "the whole run runs the suite, not a list of files"


def test_every_shard_writes_to_its_own_data_file(runs: _Runs, sharded: _Sharded) -> None:
    """One data file for three shards is a combine over one shard's data wearing three names."""
    equivalence.shard_equivalence(".", SHA, shards=3)
    files = [runs.call(f"shard-{i}")["coverage_file"] for i in (1, 2, 3)]
    assert files == [".uci-shard-1.data", ".uci-shard-2.data", ".uci-shard-3.data"]
    assert sharded.combine_calls == [(sharded.extraction.root, sharded.extraction.python, files)]
    assert runs.call("whole").get("coverage_file") is None


def test_each_shard_record_states_how_many_modules_it_ran(runs: _Runs, sharded: _Sharded) -> None:
    finding = equivalence.shard_equivalence(".", SHA, shards=2)
    assert [record.get("modules") for record in finding.runs] == [None, 2, 2]
    assert finding.runs[0]["label"] == "whole"


def test_a_combination_that_differs_names_each_total_that_differs(
    runs: _Runs, sharded: _Sharded
) -> None:
    """Rule 10 names statements, covered, files and both branch totals, so each is compared on its
    own rather than being taken as implied by the line-set equality."""
    sharded.combined = ((1,), (3,), (7, 5))
    finding = equivalence.shard_equivalence(".", SHA, shards=2)

    assert finding.identical is False
    assert finding.holds is False
    assert finding.failures == [
        "statements differ: whole=3 combined=2",
        "covered differ: whole=2 combined=1",
        "branches_valid differ: whole=4 combined=7",
        "branches_covered differ: whole=2 combined=5",
    ]


def test_a_whole_run_without_a_measurement_stops_before_any_comparison(
    runs: _Runs, sharded: _Sharded
) -> None:
    """With nothing to compare against, a diff would be a comparison with an absent operand."""
    runs.reports["whole"] = None
    finding = equivalence.shard_equivalence(".", SHA, shards=2)

    assert finding.failures == ["the whole run produced no coverage measurement"]
    assert finding.comparisons == []
    assert finding.identical is False
    assert sharded.combine_calls, "the shards were still combined, so the evidence survives"


def test_a_failing_shard_is_reported_with_the_whole_run(runs: _Runs, sharded: _Sharded) -> None:
    runs.exit_codes["shard-2"] = 1
    finding = equivalence.shard_equivalence(".", SHA, shards=2)
    assert finding.failures == ["shard-2: pytest exited 1 (counts={'passed': 10})"]
    assert finding.identical is True, "the shards still combined to the whole run's line set"
    assert finding.holds is False


def test_the_combined_document_is_copied_out_of_the_extraction(
    runs: _Runs, sharded: _Sharded, tmp_path: Path
) -> None:
    """The extraction is disposable, so evidence naming a path inside it names nothing later."""
    evidence = tmp_path / "evidence" / "rule-10"
    equivalence.shard_equivalence(".", SHA, shards=2, evidence_dir=str(evidence))

    assert (evidence / "coverage-combined.xml").exists()
    assert runs.call("whole")["collect_xml_to"] == str(evidence / "coverage-whole.xml")


# --------------------------------------------------------------------------- _combine, for real
#
# This is the one part of the shard proof that cannot be faked without emptying it. ``_combine``
# claims that ``coverage combine`` UNIONS two measurements, and that claim is a property of
# coverage.py, not of this repository — a fake that returned a union would be asserting the answer.
# So these three tests run real ``coverage`` subprocesses over real modules. They cost about a
# second in total, which is what a checkable claim about the tool costs.


def _shard_data(root: Path, python: str, script: str, data_file: str) -> None:
    """Measure one real execution into ``data_file``, the way a shard run does."""
    # Through `clean_environment`, so this helper measures the way production does: pytest-cov's
    # subprocess bootstrap would otherwise auto-start an unconfigured coverage inside this child
    # and write statement-only data beside the OUTER session's branch data, which coverage then
    # refuses to combine (immutable.AMBIENT_MEASUREMENT_VARS).
    env = immutable.clean_environment(COVERAGE_FILE=str(root / data_file))
    env.pop("PYTHONHASHSEED", None)
    done = subprocess.run(  # noqa: S603
        [python, "-m", "coverage", "run", script],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert done.returncode == 0, done.stderr
    assert (root / data_file).exists(), f"coverage wrote no data for {script}"


@pytest.fixture
def measurable(tmp_path: Path) -> Path:
    """Two scripts that each execute one half of one module."""
    root = tmp_path / "frozen"
    (root / "engine").mkdir(parents=True)
    (root / "engine" / "x.py").write_text(
        "def a():\n    return 1\n\n\ndef b():\n    return 2\n", encoding="utf-8"
    )
    for name, call in (("run_a.py", "a"), ("run_b.py", "b")):
        (root / name).write_text(f"import engine.x\n\nengine.x.{call}()\n", encoding="utf-8")
    return root


def test_combine_unions_the_shard_measurements_rather_than_replacing_them(measurable: Path) -> None:
    """The property Rule 10 rests on, measured rather than assumed.

    Shard 1 executes ``a`` and never ``b``; shard 2 the reverse. Neither data file alone covers the
    module. If ``coverage combine`` overwrote instead of merging — or if ``_combine`` passed the
    files in a way that made it overwrite — the combined report would still show a missing line, and
    Rule 10 would then be comparing the whole run against the last shard.
    """
    _shard_data(measurable, sys.executable, "run_a.py", ".uci-shard-1.data")
    _shard_data(measurable, sys.executable, "run_b.py", ".uci-shard-2.data")

    combined_xml = equivalence._combine(
        str(measurable), sys.executable, [".uci-shard-1.data", ".uci-shard-2.data"]
    )

    assert combined_xml == str(measurable / ".uci-combined.xml")
    report = coverage_data.parse(combined_xml, repository=str(measurable))
    module = report.files["engine/x.py"]
    assert (
        module.missed == frozenset()
    ), f"the combination lost a shard's measurement: {sorted(module.missed)} still missing"
    assert module.hit == frozenset({1, 2, 5, 6})
    assert (measurable / ".uci-combined.data").exists(), "the combined data is kept as evidence"
    assert (measurable / ".uci-shard-1.data").exists(), "--keep must leave the inputs in place"


def test_combining_shards_that_produced_nothing_is_refused(measurable: Path) -> None:
    """An absent data file means a shard never measured, and a combine over nothing renders an
    empty report — which reads as a successful measurement of a suite that covers nothing."""
    with pytest.raises(IntegrityError) as raised:
        equivalence._combine(str(measurable), sys.executable, [".uci-shard-1.data"])
    assert "no shard produced coverage data" in str(raised.value)
    assert "refusing to claim a combined measurement over nothing" in str(raised.value)


def test_a_failing_combine_is_an_error_and_not_an_empty_measurement(measurable: Path) -> None:
    """Forged by writing a file that exists and is not coverage data, which is what a truncated
    write from a killed shard leaves behind."""
    (measurable / ".uci-shard-1.data").write_text("not a coverage database", encoding="utf-8")
    with pytest.raises(IntegrityError) as raised:
        equivalence._combine(str(measurable), sys.executable, [".uci-shard-1.data"])
    assert str(raised.value).startswith("coverage combine failed: ")


def test_a_combine_that_cannot_be_rendered_is_an_error_too(measurable: Path) -> None:
    """The second subprocess has its own refusal, and an unrenderable measurement is not a zero
    one either. Forged by occupying the output path with a directory."""
    _shard_data(measurable, sys.executable, "run_a.py", ".uci-shard-1.data")
    (measurable / ".uci-combined.xml").mkdir()
    with pytest.raises(IntegrityError) as raised:
        equivalence._combine(str(measurable), sys.executable, [".uci-shard-1.data"])
    assert str(raised.value).startswith("rendering combined coverage failed: ")


# --------------------------------------------------------------------------- ambient environment
#
# WHY THIS SECTION EXISTS, STATED AS THE FAILURE IT COST. Every subprocess in this package measures
# something, and pytest-cov installs a `.pth` that AUTO-STARTS a second, unconfigured coverage in
# any Python subprocess the `COV_CORE_*` variables reach. Under `./verify.sh` that second coverage
# wrote STATEMENT-ONLY data, in the parallel filename form, beside the outer session's BRANCH data
# — and `coverage combine` refuses to merge the two. The result was not a wrong number: four of
# thirteen shards died with `INTERNALERROR: DataError: Can't combine statement coverage data with
# branch data` AFTER every test in them had passed, the combine over the survivors failed, and the
# coverage gate reported 71% — a figure that measured nothing.
#
# The stripping is what these tests hold. They are cheap because the property is a property of the
# environment dictionary, and the dictionary is where the defect lived.


def test_no_ambient_measurement_variable_survives_into_a_measuring_subprocess(monkeypatch) -> None:
    for name in immutable.AMBIENT_MEASUREMENT_VARS:
        monkeypatch.setenv(name, f"ambient-{name}")
    monkeypatch.setenv("PATH", os.environ["PATH"])

    environment = immutable.clean_environment()

    assert not (set(immutable.AMBIENT_MEASUREMENT_VARS) & set(environment)), (
        "a measuring subprocess would inherit the outer session's coverage bootstrap and "
        "contribute unconfigured data to a data file it does not own"
    )
    assert environment["PATH"] == os.environ["PATH"], "the rest of the environment is carried"


def test_the_stripped_set_names_both_families_and_not_just_the_one_that_was_found_first() -> None:
    """COVERAGE_FILE alone was the fix for the first occurrence and was NOT enough for the second.
    Naming the set is what makes the second family checkable instead of remembered."""
    assert "COVERAGE_FILE" in immutable.AMBIENT_MEASUREMENT_VARS
    assert {n for n in immutable.AMBIENT_MEASUREMENT_VARS if n.startswith("COV_CORE_")} >= {
        "COV_CORE_SOURCE",
        "COV_CORE_CONFIG",
        "COV_CORE_DATAFILE",
    }


def test_an_override_is_applied_after_the_strip_and_not_before(monkeypatch) -> None:
    """`clean_environment(COVERAGE_FILE=...)` must SET the variable it also strips, or the shard
    combiner would spawn a subprocess with no data file at all."""
    monkeypatch.setenv("COVERAGE_FILE", "/somewhere/ambient.data")
    environment = immutable.clean_environment(COVERAGE_FILE="/chosen/explicit.data")
    assert environment["COVERAGE_FILE"] == "/chosen/explicit.data"


def test_a_real_measuring_subprocess_writes_no_data_file_beside_the_outer_session(
    measurable: Path, monkeypatch
) -> None:
    """The end-to-end statement of the same property, over a real `coverage` subprocess.

    Forged by setting the bootstrap variables this process may not actually be running under, so
    the test holds whether or not the suite that runs it was itself invoked with `--cov`.
    """
    monkeypatch.setenv("COV_CORE_SOURCE", str(measurable))
    monkeypatch.setenv("COV_CORE_DATAFILE", str(measurable / ".outer-session.data"))
    monkeypatch.setenv("COV_CORE_CONFIG", "")

    _shard_data(measurable, sys.executable, "run_a.py", ".uci-shard-1.data")

    leaked = sorted(p.name for p in measurable.glob(".outer-session.data*"))
    assert leaked == [], f"the child contributed to a data file it does not own: {leaked}"
    assert (measurable / ".uci-shard-1.data").exists(), "and it still measured its own run"


# ------------------------------------------------------------------ the spawn-scrub ratchet
#
# WHY A RATCHET AND NOT A BAN. A Python subprocess that inherits `COV_CORE_*` restarts coverage
# at interpreter startup, and this repository has a second, worse consequence than stray data:
# `platform/` here SHADOWS the standard library's `platform`, coverage imports the stdlib module
# while bootstrapping, and `sys.modules['platform']` is then bound to it before the local package
# can win. Every later `from platform.<anything> import ...` in that child dies with "'platform'
# is not a package" — and 340 test modules import the local package. It has already been observed
# aborting a child's collection entirely, which made THE test that proves no test is silently
# skipped report 8,360 tests lost while the shards themselves ran and passed in full.
#
# The population cannot go to zero today: several of these sites live in 00-BOOK tools and
# 00-MASTER engines that this suite does not own, and some tests deliberately measure the ambient
# environment. So it is bounded instead, on the terms this repository uses everywhere else — the
# count may FALL and may never RISE, and a fall must tighten the ceiling rather than leave slack a
# regression can occupy in silence.


def _unscrubbed_spawn_sites() -> list[str]:
    """Every `sys.executable` subprocess in the tree that passes no `env=`.

    Measured over `git ls-files` rather than a directory walk, so an untracked scratch file
    cannot change the number and a tracked one always does.
    """
    import ast
    import subprocess as sp

    # `git` is resolved from PATH exactly as every other tool in this repository resolves it;
    # pinning an absolute path would make the measurement machine-specific.
    listed = sp.run(  # noqa: S603
        ["git", "ls-files", "*.py"],  # noqa: S607
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
        env=immutable.clean_environment(),
    )
    sites: list[str] = []
    for rel in listed.stdout.split():
        source = (Path(REPO) / rel).read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if name not in {"run", "Popen", "check_output", "call", "check_call"}:
                continue
            segment = ast.get_source_segment(source, node) or ""
            if "sys.executable" not in segment:
                continue
            if any(kw.arg == "env" for kw in node.keywords):
                continue
            sites.append(f"{rel}:{node.lineno}")
    return sorted(sites)


#: Measured at the commit that introduced this check. IT MAY FALL AND MAY NEVER RISE.
#:
#: LOWERED 16 -> 14 BECAUSE THE DEBT WAS REPAID. Both coverage spawns in
#: 00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py now pass
#: `env=immutable.clean_environment()`. That engine runs `coverage run -m pytest`, so it
#: was the most exposed inheritor of COV_CORE_* in the tree: the very child it spawns to
#: measure coverage was the one most likely to bind sys.modules["platform"] to the stdlib.
#:
#: A BLIND SPOT WAS INTRODUCED IN THE SAME EDIT, AND IS RECORDED RATHER THAN LEFT TO BE
#: REDISCOVERED. Those two sites also stopped passing `sys.executable` literally — they
#: now pass an interpreter resolved by `instrument_interpreter()`, because `$PY` in the
#: RFP pipeline is the hosted interpreter and not the pinned venv. `_unscrubbed_spawn_sites`
#: keys on the literal `sys.executable`, so it can no longer see them AT ALL, scrubbed or
#: not. The ceiling fell for a real repair, but the detector would not notice if the scrub
#: were removed tomorrow. Widening it to follow a resolved interpreter is the next
#: tightening, and it is a change to the DETECTOR rather than to this number.
UNSCRUBBED_SPAWN_CEILING = 14


def test_no_new_subprocess_inherits_the_measurement_environment() -> None:
    sites = _unscrubbed_spawn_sites()
    assert len(sites) <= UNSCRUBBED_SPAWN_CEILING, (
        f"{len(sites)} unscrubbed `sys.executable` spawn(s) exceed the ceiling "
        f"{UNSCRUBBED_SPAWN_CEILING}. A new one inherits COV_CORE_* and will bind "
        f"sys.modules['platform'] to the STDLIB module, breaking every later import of this "
        f"repository's own platform package inside that child. Pass "
        f"`env=immutable.clean_environment()`. New site(s): "
        f"{sorted(set(sites) - set(_KNOWN_UNSCRUBBED))}"
    )


def test_a_repaid_spawn_site_tightens_the_ceiling() -> None:
    """The lower half of the ratchet: debt repaid without tightening is refused exactly as new
    debt is, because a ceiling above the measurement licenses that many silent regressions."""
    sites = _unscrubbed_spawn_sites()
    assert len(sites) >= UNSCRUBBED_SPAWN_CEILING, (
        f"{len(sites)} unscrubbed spawn(s) is BELOW the ceiling {UNSCRUBBED_SPAWN_CEILING} — "
        f"lower UNSCRUBBED_SPAWN_CEILING to {len(sites)} and record why it fell."
    )


#: The sites the ceiling stands on, so a failure names what is NEW rather than what is known.
_KNOWN_UNSCRUBBED = (
    "00-BOOK/tools/ukctx_assimilate.py:170",
    "00-BOOK/tools/ukctx_certify.py:116",
    "00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py:281",
    "engine/tests/uckp/test_cli_and_package.py:238",
    "engine/tests/unit/test_enforcement_closure.py:615",
    "engine/tests/unit/test_verification_intelligence.py:826",
    "engine/tests/unit/test_verification_intelligence.py:1071",
    "platform/tests/test_canonical_validation_evidence.py:219",
    "platform/tests/test_constitutional_authority_alignment.py:296",
    "platform/tests/test_ledger_authority.py:760",
    "platform/tests/test_observation_universe.py:241",
    "platform/tests/test_verification_purity.py:180",
    "platform/tests/test_verification_purity.py:280",
    "platform/tests/test_verification_purity.py:416",
)


# --------------------------------------------------------------- the real extraction paths
#
# WHY THESE WERE UNTESTED, AND WHY THAT WAS THE WRONG TRADE. `prepare`, `extract`, `seal` and
# `run` are the machinery that makes a certification claim mean anything: they take a commit,
# rebuild it from `git archive` into a workspace nobody has written to, seal it to a digest that
# is a function of the archived bytes alone, and execute a command inside it. The module sat at
# 53% because exercising them costs a real extraction — and the paths that were skipped are
# precisely the ones a wrong answer would travel through.
#
# The venv construction and its `pip install` remain unexercised ON PURPOSE: they cost tens of
# seconds and can reach the network, and this suite already made the whole run 32% cheaper by
# refusing to carry avoidable cost. Everything reachable with `build_venv=False` is covered here,
# which is every path except the two that build an interpreter.


def test_a_fingerprint_records_the_four_things_that_make_a_tree_citable() -> None:
    fp = immutable.fingerprint(REPO_STR)
    record = fp.as_record()
    assert set(record) == {"head", "porcelain_digest", "tracked_digest", "dirty_entries"}
    assert len(str(record["head"])) == 40, "a head that is not a full sha cannot address a tree"
    assert isinstance(record["dirty_entries"], int)
    assert immutable.fingerprint(REPO_STR) == fp, "two samples of one tree must be equal"


def test_a_git_failure_is_reported_as_an_integrity_error_not_a_traceback() -> None:
    """`_git` wraps OSError and CalledProcessError, because a caller that cannot tell 'the tree
    moved' from 'git is missing' cannot decide what to do about either."""
    with pytest.raises(immutable.IntegrityError):
        immutable.resolve_sha(REPO_STR, "refs/heads/a-branch-that-does-not-exist")


def test_the_dependency_digest_reads_pyproject_at_the_SHA_not_on_disk() -> None:
    """The declared dependency set belongs to the commit under certification. Reading the working
    tree instead would let an uncommitted edit change what a past commit is said to have needed."""
    head = immutable.resolve_sha(REPO_STR)
    digest = immutable._dependency_digest(REPO_STR, head)
    assert len(digest) == 64, "a dependency digest is a sha256 over the pinned set"
    assert immutable._dependency_digest(REPO_STR, head) == digest


def test_extract_rebuilds_the_commit_and_seal_digests_the_archived_bytes(tmp_path: Path) -> None:
    head = immutable.resolve_sha(REPO_STR)
    destination = str(tmp_path / "extraction")
    immutable.extract(REPO_STR, head, destination)

    assert (Path(destination) / "pyproject.toml").exists(), "the archive did not land"
    assert (Path(destination) / "engine").is_dir()

    # `seal` makes a SEALING COMMIT over the extracted tree, so this is a 40-char git object
    # id, not a content hash — the identity is git's, which is what makes it addressable.
    sealed = immutable.seal(destination)
    assert len(sealed) == 40

    # Sealed identity is a function of CONTENT. A second extraction of the same commit into a
    # different directory must agree, or two certifications of one commit could disagree.
    other = str(tmp_path / "extraction-2")
    immutable.extract(REPO_STR, head, other)
    assert immutable.seal(other) == sealed, "the seal is not a function of the archived bytes"

    # And a changed byte must move it, or the seal would certify nothing.
    (Path(other) / "pyproject.toml").write_text("# perturbed\n", encoding="utf-8")
    assert immutable.seal(other) != sealed


def test_extract_refuses_a_sha_that_does_not_exist(tmp_path: Path) -> None:
    with pytest.raises(immutable.IntegrityError):
        immutable.extract(REPO_STR, "0" * 40, str(tmp_path / "nowhere"))


def test_prepare_reuses_an_extraction_and_says_so(tmp_path: Path) -> None:
    """Reuse is an optimisation that must never be silent: `reused` is on the record, so a run
    that was measured against a cached tree can be told apart from one that rebuilt it."""
    head = immutable.resolve_sha(REPO_STR)
    workspace = str(tmp_path / "ws")

    first = immutable.prepare(REPO_STR, head, workspace=workspace, build_venv=False)
    assert first.reused is False
    assert first.sealed_sha and len(first.sealed_sha) == 40
    assert first.python == sys.executable, "build_venv=False measures with the caller's python"

    second = immutable.prepare(REPO_STR, head, workspace=workspace, build_venv=False)
    assert second.reused is True, "a prepared extraction was rebuilt instead of reused"
    assert second.sealed_sha == first.sealed_sha, "reuse changed the sealed identity"
    assert second.prepare_seconds <= first.prepare_seconds + 5


def test_prepare_rebuilds_when_reuse_is_refused(tmp_path: Path) -> None:
    head = immutable.resolve_sha(REPO_STR)
    workspace = str(tmp_path / "ws")
    immutable.prepare(REPO_STR, head, workspace=workspace, build_venv=False)
    again = immutable.prepare(REPO_STR, head, workspace=workspace, build_venv=False, reuse=False)
    assert again.reused is False, "reuse=False still served a cached extraction"


def test_an_extraction_record_carries_both_shas(tmp_path: Path) -> None:
    head = immutable.resolve_sha(REPO_STR)
    record = immutable.prepare(
        REPO_STR, head, workspace=str(tmp_path / "ws"), build_venv=False
    ).as_record()
    assert record["source_sha"] == head
    assert record["sealed_sha"] != record["source_sha"], (
        "source and sealed identity must be distinguishable — one names where the bytes came "
        "from, the other names what they are"
    )


def test_run_executes_inside_the_extraction_and_collects_what_it_names(tmp_path: Path) -> None:
    """The end-to-end claim: a command runs against the FROZEN tree, not the working tree, and
    an artifact it produced can be cited afterwards because it was copied out."""
    head = immutable.resolve_sha(REPO_STR)
    outcome = immutable.run(
        REPO_STR,
        [
            immutable.PYTHON_PLACEHOLDER,
            "-c",
            "import pathlib,os;"
            "pathlib.Path('evidence.txt').write_text(os.path.basename(os.getcwd()));"
            "print('ran')",
        ],
        sha=head,
        workspace=str(tmp_path / "ws"),
        build_venv=False,
        collect={"evidence.txt": str(tmp_path / "collected.txt")},
    )
    assert outcome.exit_code == 0, outcome.stderr_tail
    assert "ran" in outcome.stdout_tail
    assert (tmp_path / "collected.txt").exists(), "a named artifact was not collected out"


def test_run_reports_a_failing_command_without_raising(tmp_path: Path) -> None:
    """A non-zero exit is a MEASUREMENT, not an error: the certification engine needs the record
    of what failed, and an exception here would discard it."""
    outcome = immutable.run(
        REPO_STR,
        [immutable.PYTHON_PLACEHOLDER, "-c", "raise SystemExit(3)"],
        sha=immutable.resolve_sha(REPO_STR),
        workspace=str(tmp_path / "ws"),
        build_venv=False,
    )
    assert outcome.exit_code == 3
    assert outcome.duration_seconds >= 0
