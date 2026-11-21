"""UCOS-UFC-001 — the Foundation Constitution CLI (``ucos-constitution``).

The library beneath this surface is proven in ``test_universal_constitution.py``. What
is proven here is the surface itself: that each of the seven commands measures the
thing it names, that ``--gate`` fails closed on a withheld determination and only on
the commands declared gateable, that a fault is contained as exit 2 rather than a
traceback, and that the human summary reports what the payload actually says —
including the negative readings the repository's own declarations never produce.

``_print_summary`` is exercised directly with crafted payloads for those negative
readings. It is a pure payload-to-text renderer, so a payload is its whole input; the
alternative would be corrupting the repository's declarations to force a duplicate or
an unbound gate, which measures the fixture rather than the renderer.
"""

from __future__ import annotations

import io
import json
from platform.universal_foundation.constitution_cli import (
    GATED_COMMANDS,
    _build_parser,
    _print_summary,
    main,
)

import pytest

COMMANDS = (
    "articles",
    "capabilities",
    "conform",
    "convergence",
    "nucleus",
    "maturity",
    "freeze",
)


def run(argv: list[str], capsys) -> tuple[int, str, str]:
    """Invoke main(); return (exit_code, stdout, stderr)."""
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------


def test_the_parser_admits_exactly_the_seven_declared_commands():
    """The command choices are the law's operations — no more, no fewer."""
    parser = _build_parser()
    action = next(a for a in parser._actions if a.dest == "command")
    assert set(action.choices) == set(COMMANDS)


def test_an_unknown_command_is_refused_by_the_parser():
    with pytest.raises(SystemExit):
        _build_parser().parse_args(["ratify"])


def test_the_gateable_commands_are_the_ones_that_measure_a_determination():
    """``articles`` and ``capabilities`` report; they do not determine, so they cannot gate."""
    assert set(GATED_COMMANDS) == {"conform", "convergence", "nucleus", "freeze"}
    assert set(GATED_COMMANDS) <= set(COMMANDS)


# ---------------------------------------------------------------------------
# every command runs and reports
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("command", COMMANDS)
def test_every_command_reports_its_summary_on_stderr_and_nothing_on_stdout(command, capsys):
    """Without --json the summary is diagnostic output; stdout stays free for data."""
    code, out, err = run([command], capsys)
    assert code == 0
    assert out == ""
    assert "UNIVERSAL FOUNDATION CONSTITUTION" in err
    assert f"command: {command}" in err


@pytest.mark.parametrize("command", COMMANDS)
def test_json_emits_the_payload_on_stdout(command, capsys):
    """--json puts the machine-readable determination on stdout, sorted and indented."""
    code, out, err = run([command, "--json"], capsys)
    assert code == 0
    payload = json.loads(out)
    assert isinstance(payload, dict) and payload
    keys = list(payload)
    assert keys == sorted(keys)
    # The summary is still rendered; --json adds a channel, it does not replace one.
    assert "UNIVERSAL FOUNDATION CONSTITUTION" in err


@pytest.mark.parametrize("command", ("convergence", "nucleus", "conform", "freeze"))
def test_detail_emits_at_least_what_the_summary_emits(command, capsys):
    """--detail is the full determination; a summary may never carry a key it drops."""
    _, summary_out, _ = run([command, "--json"], capsys)
    _, detail_out, _ = run([command, "--detail", "--json"], capsys)
    summary = json.loads(summary_out)
    detail = json.loads(detail_out)
    assert set(summary) <= set(detail)


# ---------------------------------------------------------------------------
# what each command actually measures
# ---------------------------------------------------------------------------


def test_articles_reports_the_seventeen_articles_over_thirteen_domains(capsys):
    _, out, err = run(["articles", "--json"], capsys)
    payload = json.loads(out)
    assert len(payload["articles"]) == 17
    assert len(payload["domains"]) == 13
    for article in payload["articles"]:
        assert article["article_id"] in err


def test_capabilities_reports_the_register_its_order_and_its_unbound_gates(capsys):
    """A gate no probe binds is the one way this command can withhold."""
    code, out, err = run(["capabilities", "--json"], capsys)
    payload = json.loads(out)
    assert payload["dependency_order"]
    assert " -> ".join(payload["dependency_order"]) in err
    # The repository binds every gate, so the command passes and lists no unbound gate.
    assert payload["unbound_gates"] == []
    assert code == 0
    assert "UNBOUND GATE" not in err


def test_convergence_reports_one_answer_per_constitutional_model(capsys):
    _, out, err = run(["convergence", "--json"], capsys)
    payload = json.loads(out)
    assert payload["models"]
    for model in payload["models"]:
        assert model["model_id"] in err
    assert "CONVERGED" in err


def test_nucleus_reports_completeness_per_registered_nucleus(capsys):
    _, out, err = run(["nucleus", "--json"], capsys)
    payload = json.loads(out)
    assert payload["nuclei"]
    assert payload["contract_id"] in err
    for nucleus in payload["nuclei"]:
        assert nucleus["capability_id"] in err


def test_maturity_reports_a_percentage_for_every_axis_the_gates_prove(capsys):
    _, out, err = run(["maturity", "--json"], capsys)
    payload = json.loads(out)
    assert payload["maturity_by_axis"]
    # Every axis reported is an axis the constitution declares gates for.
    assert set(payload["maturity_by_axis"]) <= set(payload["maturity_gates"])
    for axis in payload["maturity_by_axis"]:
        assert axis in err
    assert payload["capabilities"]


def test_conform_measures_every_capability_against_every_article(capsys):
    _, out, err = run(["conform", "--json"], capsys)
    payload = json.loads(out)
    counts = payload["counts"]
    assert counts["capabilities"] == len(payload["capabilities"])
    assert counts["faulted"] == 0
    assert f"{counts['passed']} passed" in err


def test_conform_carries_the_platform_articles_it_measures_twice_for(capsys):
    """UFC-17 reads the per-capability results, so the second pass carries platform gates."""
    _, out, _ = run(["conform", "--detail", "--json"], capsys)
    payload = json.loads(out)
    assert payload["platform_results"], "the second pass must contribute platform gates"


def test_freeze_withholds_readiness_when_the_suites_were_not_executed(capsys):
    """Unmeasured is not ready: without --with-suites the criteria are withheld."""
    code, out, err = run(["freeze", "--json"], capsys)
    payload = json.loads(out)
    assert payload["counts"]["unmeasured"] > 0
    assert payload["blockers"]
    assert "BLOCKER" in err
    # Reporting a withheld determination is not itself a failure; only --gate fails.
    assert code == 0


# ---------------------------------------------------------------------------
# gating
# ---------------------------------------------------------------------------


def test_gate_fails_closed_on_a_withheld_determination(capsys):
    code, _, err = run(["freeze", "--gate"], capsys)
    assert code == 1
    assert "FOUNDATION FREEZE WITHHELD" in err


@pytest.mark.parametrize("command", ("conform", "convergence", "nucleus"))
def test_gate_passes_when_the_determination_is_satisfied(command, capsys):
    code, _, err = run([command, "--gate"], capsys)
    assert code == 0
    assert "WITHHELD" not in err


@pytest.mark.parametrize("command", ("articles", "capabilities", "maturity"))
def test_gate_is_inert_on_a_command_that_determines_nothing(command, capsys):
    """A reporting command cannot fail a gated run even when --gate is passed."""
    assert command not in GATED_COMMANDS
    code, _, err = run([command, "--gate"], capsys)
    assert code == 0
    assert "WITHHELD" not in err


# ---------------------------------------------------------------------------
# faults
# ---------------------------------------------------------------------------


def test_an_unreadable_register_is_a_fault_not_a_pass(capsys, tmp_path):
    code, out, err = run(["capabilities", "--register", str(tmp_path / "absent.json")], capsys)
    assert code == 2
    assert out == ""
    assert "constitution error:" in err


def test_a_fault_is_reported_before_any_determination_is_claimed(capsys, tmp_path):
    """A faulted run emits no summary — there is no determination to summarize."""
    code, _, err = run(
        ["conform", "--convergence-register", str(tmp_path / "absent.json"), "--gate"],
        capsys,
    )
    assert code == 2
    assert "UNIVERSAL FOUNDATION CONSTITUTION" not in err


def test_a_malformed_register_document_is_a_fault(capsys, tmp_path):
    bad = tmp_path / "register.json"
    bad.write_text("{ not json", encoding="utf-8")
    code, _, err = run(["capabilities", "--register", str(bad)], capsys)
    assert code == 2
    assert "constitution error:" in err


# ---------------------------------------------------------------------------
# the summary renderer, on readings the repository does not currently produce
# ---------------------------------------------------------------------------


def _render(command: str, payload: dict) -> str:
    stream = io.StringIO()
    _print_summary(command, payload, stream)
    return stream.getvalue()


def test_the_summary_names_every_unbound_gate():
    text = _render(
        "capabilities",
        {
            "capabilities": [{"capability_id": "UFC-CAP-1", "domain": "TRUTH", "name": "Truth"}],
            "dependency_order": ["UFC-CAP-1"],
            "unbound_gates": ["UFC-09-GATE"],
        },
    )
    assert "UNBOUND GATE  UFC-09-GATE" in text
    assert "UFC-CAP-1" in text


def test_the_summary_names_a_duplicate_implementation_and_its_remediation():
    """A second answer must be reported with the locators that make it second."""
    text = _render(
        "convergence",
        {
            "counts": {"models": 1, "converged": 0, "duplicate_implementations": 1},
            "duplicate_groups": [
                {
                    "model_id": "UFC-MODEL-TRUTH",
                    "governed_root": "platform/universal_truth",
                    "locators": ["a/truth.py", "b/truth.py"],
                    "remediation": "retire b/truth.py",
                }
            ],
            "models": [
                {
                    "model_id": "UFC-MODEL-TRUTH",
                    "canonical_package": "platform.universal_truth",
                    "converged": False,
                }
            ],
            "gate_results": [{"verdict": "FAIL", "gate": "UFC-15-GATE"}],
        },
    )
    assert "DUPLICATE" in text
    assert "a/truth.py" in text and "b/truth.py" in text
    assert "-> retire b/truth.py" in text
    assert "NOT-CONVERGED" in text
    assert "FAIL" in text


def test_the_summary_marks_an_incomplete_nucleus_and_lists_its_missing_facets():
    text = _render(
        "nucleus",
        {
            "contract_id": "UFC-NUCLEUS-CONTRACT",
            "counts": {"nuclei": 1, "complete": 0, "facets": 4, "missing": 2},
            "nuclei": [
                {
                    "capability_id": "UFC-CAP-9",
                    "complete": False,
                    "completeness_percentage": 50.0,
                    "counts": {"RESOLVED": 2, "DECLARED-ABSENT": 0},
                }
            ],
            "blockers": ["UFC-CAP-9 is missing facet CONSTITUTION"],
            "gate_results": [{"verdict": "FAIL", "gate": "UFC-16-GATE"}],
        },
    )
    assert "INCOMPLETE" in text
    assert "50.00%" in text
    assert "MISSING  UFC-CAP-9 is missing facet CONSTITUTION" in text


def test_the_summary_marks_a_non_conformant_capability_and_its_blockers():
    text = _render(
        "conform",
        {
            "counts": {"capabilities": 1, "passed": 3, "failed": 1, "faulted": 0},
            "maturity_percentage": 75.0,
            "capabilities": [
                {
                    "capability_id": "UFC-CAP-2",
                    "conformant": False,
                    "maturity_percentage": 75.0,
                }
            ],
            "blockers": ["UFC-04 failed for UFC-CAP-2"],
        },
    )
    assert "NON-CONFORMANT" in text
    assert "1 failed" in text
    assert "BLOCKER  UFC-04 failed for UFC-CAP-2" in text


def test_the_summary_reports_freeze_criteria_verdict_by_verdict():
    text = _render(
        "freeze",
        {
            "determination": "NOT-READY",
            "counts": {"ready": 1, "not_ready": 1, "unmeasured": 1},
            "maturity_percentage": 88.0,
            "results": [
                {"verdict": "READY", "criterion_id": "FRZ-01", "requirement": "tests pass"},
                {"verdict": "UNMEASURED", "criterion_id": "FRZ-02", "requirement": "suites run"},
            ],
            "blockers": ["FRZ-02 was not measured"],
        },
    )
    assert "determination: NOT-READY" in text
    assert "1 ready, 1 not ready, 1 unmeasured" in text
    assert "READY" in text and "UNMEASURED" in text
    assert "BLOCKER  FRZ-02 was not measured" in text


def test_the_summary_renders_an_empty_payload_without_inventing_a_reading():
    """A payload that asserts nothing must render as nothing asserted, not as zeroes passed."""
    for command in COMMANDS:
        text = _render(command, {})
        assert f"command: {command}" in text
        assert "BLOCKER" not in text
        assert "UNBOUND GATE" not in text
