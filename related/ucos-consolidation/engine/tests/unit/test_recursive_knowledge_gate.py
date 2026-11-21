"""URKE-000001 Part 15 — the gate as a program: its argv, its two streams, its three exit codes.

WHY THIS IS A SEPARATE FILE FROM ``test_recursive_knowledge.py``.

That suite proves the thirty-two LAWS, and it proves them by mutating the measured input. None of it
executes the gate. The result was a 53-unit CLI at 4%: two calls, one of them ``--metrics``, and
nothing at all through ``_render`` — which is the only part of this capability an operator ever
reads, and the part that formats a REFUSAL it can therefore never have formatted correctly.

WHAT IS REAL HERE AND WHAT IS FORGED.

The report is REAL. It is measured once by ``contract.measure()`` — 0.9s against this tree, measured
— and reused, because ``gate.main`` re-measuring per test would pay for the same answer six times.
Reuse is not forgery: every field these tests read was computed by the real thirty-two laws over the
real repository.

The REFUSALS are forged, and they have to be. This repository's URKE gate is OPEN, its parity is
10/10 and no law is refused, so the CLOSED verdict, the ``XX`` mark, the violation list, the
truncation at six and the "absent layers" clause are all unreachable from a healthy tree. Each is
induced by mutating a deep copy of the real report, which is the only way a gate's failure rendering
is ever seen before the day it is needed.

Exit codes are asserted as LITERAL integers. ``gate.EXIT_FAULT`` is an attribute reference: it
proves the test and the module agree, not that either is right, and a gate's exit code is its whole
interface to the shell.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from engine.recursive_knowledge import contract, evidence, gate
from engine.recursive_knowledge.model import RecursiveKnowledgeError

REFUSED = "REFUSED"


@pytest.fixture(scope="module")
def measured() -> dict[str, Any]:
    """One real measurement, shared. Deep-copied by every test that mutates it."""
    return contract.measure()


class _Wiring:
    """Records what the gate asked ``measure`` for, and answers with a report or a fault."""

    def __init__(self, report: dict[str, Any]) -> None:
        self.report = report
        self.calls: list[dict[str, Any]] = []
        self.fault: RecursiveKnowledgeError | None = None


@pytest.fixture
def wired(measured: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> _Wiring:
    rec = _Wiring(copy.deepcopy(measured))

    def measure(
        declaration: str | None = None,
        *,
        repository: str | None = None,
        laws: list[str] | None = None,
    ) -> dict[str, Any]:
        rec.calls.append({"declaration": declaration, "repository": repository, "laws": laws})
        if rec.fault is not None:
            raise rec.fault
        return rec.report

    monkeypatch.setattr(gate, "measure", measure)
    return rec


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = gate.main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


# --------------------------------------------------------------------------- the three verdicts


def test_an_open_gate_exits_zero_and_reports_on_stderr(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """The report goes to stderr so a caller can pipe the JSON on stdout without stripping prose."""
    code, out, err = _run(capsys, "--gate")

    assert code == 0
    assert out == "", "nothing was asked for on stdout, so nothing may be written there"
    assert err.splitlines()[-1] == "  verdict: OPEN"
    assert "UNIVERSAL RECURSIVE KNOWLEDGE FOUNDATION — URKE-000001" in err
    assert wired.calls == [{"declaration": None, "repository": gate.repo_root(), "laws": None}]


def test_a_refused_law_closes_the_gate(wired: _Wiring, capsys: pytest.CaptureFixture[str]) -> None:
    wired.report["status"] = "CLOSED"
    wired.report["laws"][0]["verdict"] = REFUSED
    wired.report["laws"][0]["violations"] = ["engine/x.py governs no unknown"]

    code, _out, err = _run(capsys, "--gate")

    assert code == 1
    assert "  XX  " in err
    assert "          - engine/x.py governs no unknown" in err
    assert err.splitlines()[-1] == "  verdict: CLOSED"


def test_the_closed_verdict_is_opt_in_and_the_measurement_is_not(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """Without ``--gate`` the same closed report is reported and exits 0.

    That is the difference between an observation and an enforcement, and it is why every caller
    that enforces has to pass the flag: a reader must be able to read a closed report without
    the reading itself failing their build.
    """
    wired.report["status"] = "CLOSED"
    code, _out, err = _run(capsys)
    assert code == 0
    assert "  verdict: CLOSED" in err


def test_a_closed_gate_reports_even_when_asked_to_be_quiet(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--quiet`` suppresses the summary when the gate is OPEN and NOT when it is closed. A
    refusal an operator cannot see is a refusal they cannot act on, and the flag exists to keep
    successful runs silent, not to hide failures."""
    wired.report["status"] = "CLOSED"
    code, _out, err = _run(capsys, "--gate", "--quiet")
    assert code == 1
    assert "  verdict: CLOSED" in err


def test_quiet_suppresses_the_summary_of_an_open_gate(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, err = _run(capsys, "--gate", "--quiet")
    assert code == 0
    assert err == ""
    assert out == ""


def test_a_measurement_that_could_not_be_taken_is_exit_two(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """FAULT is not CLOSED. "A law refused this repository" and "the law set could not be loaded"
    are different facts, and a gate that returned 1 for both would let an unreadable declaration
    pass as whichever answer the caller found convenient."""
    wired.fault = RecursiveKnowledgeError("urke-declaration.json is not readable")

    code, out, err = _run(capsys, "--gate")

    assert code == 2
    assert out == "", "a fault has no report, so stdout stays empty even under --json"
    assert "FAULT" in err
    assert "Detected: urke-declaration.json is not readable" in err
    assert "No verdict was reached. This is NOT a pass and NOT a refusal." in err
    assert f"Repair with: {gate.REPAIR_COMMAND}" in err


def test_the_fault_render_is_reached_under_json_too(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    wired.fault = RecursiveKnowledgeError("a law could not be computed")
    code, out, _err = _run(capsys, "--json", "--gate")
    assert code == 2
    assert out == ""


# --------------------------------------------------------------------------- what reaches stdout


def test_the_json_report_is_the_whole_report_and_the_prose_stays_on_stderr(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, err = _run(capsys, "--json")

    assert code == 0
    document = json.loads(out)
    assert document["status"] == wired.report["status"]
    assert document["counts"]["laws"] == wired.report["counts"]["laws"]
    assert len(document["laws"]) == len(wired.report["laws"])
    assert "verdict: OPEN" in err, "the summary is still rendered; --json adds, it does not replace"


def test_json_and_quiet_together_emit_exactly_the_document(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """The machine-readable invocation: one document on stdout, nothing else anywhere."""
    code, out, err = _run(capsys, "--json", "--quiet")
    assert code == 0
    assert err == ""
    assert json.loads(out)["declaration"] == wired.report["declaration"]


def test_the_metrics_flag_takes_no_measurement_at_all(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """Complexity metrics are a property of the DECLARATION, so the thirty-two laws are not run.

    Asserted by the absence of a ``measure`` call rather than by a stopwatch: the flag exists so an
    operator can ask what the declaration contains without paying for a verdict over the repository.
    """
    code, out, err = _run(capsys, "--metrics")

    assert code == 0
    assert wired.calls == [], "a metrics query measured the repository"
    metrics = json.loads(out)
    assert metrics["primitive_count"] > 0
    assert metrics == dict(sorted(metrics.items())), "the document is emitted sorted"
    assert err == ""


# --------------------------------------------------------------------------- argv passthrough


def test_a_named_law_is_the_only_one_measured(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--law`` is repeatable, so it accumulates rather than replacing."""
    code, _out, _err = _run(capsys, "--law", "URKE-L-01", "--law", "URKE-L-32", "--quiet")
    assert code == 0
    assert wired.calls[0]["laws"] == ["URKE-L-01", "URKE-L-32"]


def test_a_named_repository_is_measured_instead_of_the_resolved_one(
    wired: _Wiring, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    code, _out, _err = _run(
        capsys, "--repository", str(tmp_path), "--declaration", "/somewhere/urke.json", "--quiet"
    )
    assert code == 0
    assert wired.calls[0] == {
        "declaration": "/somewhere/urke.json",
        "repository": str(tmp_path),
        "laws": None,
    }


def test_an_unknown_flag_is_refused_before_anything_is_measured(wired: _Wiring) -> None:
    with pytest.raises(SystemExit) as raised:
        gate.main(["--fix"])
    assert raised.value.code == 2, "argparse exits 2; a caller must not read that as a pass"
    assert wired.calls == []


# --------------------------------------------------------------------------- evidence


def test_evidence_is_written_only_when_asked_and_every_path_is_named(
    wired: _Wiring,
    measured: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """The write is real in production and recorded here; what is asserted is that the gate names
    every path it wrote. An unreported write is a file an operator cannot find and cannot review."""
    written = [str(tmp_path / "urke-report.json"), str(tmp_path / "urke-seeded.json")]
    seen: list[dict[str, Any]] = []

    def write(
        declaration: Any, report: Any, seeded: Any, *, repository: str, command: str
    ) -> list[str]:
        seen.append({"repository": repository, "command": command, "report": report})
        return written

    monkeypatch.setattr(evidence, "write", write)

    code, out, err = _run(capsys, "--evidence")

    assert code == 0
    assert out == ""
    for path in written:
        assert f"URKE: wrote {path}" in err
    assert seen[0]["command"] == "python -m engine.recursive_knowledge.gate"
    assert seen[0]["report"] is wired.report, "the evidence must be of the run that just happened"


def test_evidence_is_written_silently_under_quiet(
    wired: _Wiring, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--quiet`` silences the announcement, not the write."""
    calls: list[str] = []

    def write(
        declaration: Any, report: Any, seeded: Any, *, repository: str, command: str
    ) -> list[str]:
        calls.append(repository)
        return ["build/urke-report.json"]

    monkeypatch.setattr(evidence, "write", write)

    code, out, err = _run(capsys, "--evidence", "--quiet")

    assert code == 0
    assert calls, "the evidence write was skipped, not silenced"
    assert (out, err) == ("", "")


# --------------------------------------------------------------------------- the render itself


def test_the_summary_states_every_figure_an_operator_acts_on(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """Each line is checked against the report it was rendered from, so a summary that quoted the
    wrong field — or quoted a constant — fails here rather than misinforming a reader."""
    report = wired.report
    _code, _out, err = _run(capsys)

    assert f"declaration          : {report['declaration']} v{report['declaration_version']}" in err
    assert f"declaration digest   : {report['declaration_digest'][:16]}" in err
    assert f"laws measured        : {report['counts']['laws']}" in err
    assert f"holds {report['counts']['holds']}   refused {report['counts']['refused']}" in err
    assert f"primitives           : {report['metrics']['primitive_count']}" in err
    assert f"data rows            : {report['metrics']['data_row_count']}" in err
    assert f"complexity ratio {report['metrics']['complexity_ratio']}" in err
    assert f"governed subjects    : {report['ledger']['subjects']}" in err
    assert f"chain {report['ledger']['chain_head'][:12]}" in err
    assert (
        f"discovery            : {report['discovery_report']['findings']} findings from "
        f"{report['discovery_report']['sources']} sources"
    ) in err
    assert f"ledger verification  : {report['ledger_verification']['status']}" in err
    assert f"standing: {report['standing']}" in err
    assert f"parity: {len(report['parity'])}/{len(report['parity'])} layers present" in err
    assert "absent:" not in err, "every layer is present on this tree"


def test_a_long_violation_list_is_truncated_and_says_how_much_it_hid(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """Six is enough to identify a pattern; a law with 400 violations would otherwise
    bury the other thirty-one laws under one of them, and the count is what tells a
    reader to look further."""
    violations = [f"engine/module_{i:02d}.py is ungoverned" for i in range(9)]
    wired.report["status"] = "CLOSED"
    wired.report["laws"][0].update({"verdict": REFUSED, "violations": violations})

    code, _out, err = _run(capsys, "--gate")

    assert code == 1
    for shown in violations[:6]:
        assert f"          - {shown}" in err
    for hidden in violations[6:]:
        assert hidden not in err
    assert "          ... +3 more" in err


def test_exactly_six_violations_are_shown_whole(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """The boundary: at six there is no remainder, so the gate must not report "+0 more"."""
    wired.report["laws"][0].update({"verdict": REFUSED, "violations": [f"v{i}" for i in range(6)]})
    _code, _out, err = _run(capsys)
    assert "more" not in err
    assert "          - v5" in err


def test_an_absent_layer_is_named_in_the_parity_line(
    wired: _Wiring, capsys: pytest.CaptureFixture[str]
) -> None:
    """Parity is the claim that every declared layer of the capability exists. When one does not,
    the summary has to say WHICH: "9/10 layers present" alone sends an operator to read ten."""
    names = sorted(wired.report["parity"])
    wired.report["parity"][names[0]] = False
    wired.report["parity"][names[-1]] = False

    _code, _out, err = _run(capsys)

    total = len(wired.report["parity"])
    assert f"parity: {total - 2}/{total} layers present" in err
    assert f"absent: {names[0]}, {names[-1]}" in err
