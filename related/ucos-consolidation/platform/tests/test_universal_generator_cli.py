"""UCOS-UNG-001 — the Ω Nucleus generator CLI (``ucos-generate``).

The surface's own obligations: each command reports the thing it names, ``plan`` states what
*would* exist without creating any of it, ``readiness`` answers the Phase 6 question without
generating anything, and a fault is contained as exit 2 rather than a traceback.

``readiness`` is also the one command that can gate, and the packaged register currently
contains exactly one nucleus it must gate on — the one declaring no catalogue. That is a real
reading, so it is asserted as one rather than mocked.
"""

from __future__ import annotations

import io
import json
from platform.tests.universal_generator_helpers import (
    CATALOG_FREE_CAPABILITY,
    COMPLETE_CAPABILITY,
    target,
)
from platform.universal_generator.cli import (
    GATED_COMMANDS,
    _build_parser,
    _print_summary,
    main,
)
from platform.universal_generator.registry import TargetRegister

import pytest

COMMANDS = ("targets", "templates", "plan", "readiness")


def run(argv: list[str], capsys) -> tuple[int, str, str]:
    """Invoke main(); return (exit_code, stdout, stderr)."""
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


@pytest.fixture
def stub_targets(tmp_path):
    """A one-target register document naming a shipped template."""
    path = tmp_path / "targets.json"
    path.write_text(
        json.dumps(
            {
                "register_id": "test.targets",
                "version": "1.0.0",
                "targets": [
                    target(
                        "GT-01",
                        template="contract-surface",
                        destination="{package_path}/generated_contracts.py",
                    ).to_dict()
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------


def test_the_parser_admits_exactly_the_four_declared_commands():
    action = next(a for a in _build_parser()._actions if a.dest == "command")
    assert set(action.choices) == set(COMMANDS)


def test_an_unknown_command_is_refused_by_the_parser():
    with pytest.raises(SystemExit):
        _build_parser().parse_args(["materialise"])


def test_readiness_is_the_only_command_that_determines_anything():
    """targets, templates and plan report; only readiness withholds."""
    assert GATED_COMMANDS == ("readiness",)


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------


def test_targets_reports_every_declared_obligation(capsys):
    code, out, err = run(["targets", "--json"], capsys)
    assert code == 0
    payload = json.loads(out)
    assert payload["count"] == len(payload["targets"])
    for item in payload["targets"]:
        assert item["target_id"] in err
        assert item["destination"] in err


def test_templates_reports_every_registered_rendering_authority(capsys):
    code, out, err = run(["templates", "--json"], capsys)
    assert code == 0
    payload = json.loads(out)
    assert payload["count"] == len(payload["templates"])
    for item in payload["templates"]:
        assert item["name"] in err


def test_every_declared_target_is_rendered_by_a_registered_template(capsys):
    """Composition already refuses otherwise; this states the invariant the CLI reports."""
    _, targets_out, _ = run(["targets", "--json"], capsys)
    _, templates_out, _ = run(["templates", "--json"], capsys)
    declared = {item["template"] for item in json.loads(targets_out)["targets"]}
    registered = {item["name"] for item in json.loads(templates_out)["templates"]}
    assert declared <= registered


def test_a_summary_goes_to_stderr_and_stdout_stays_free_for_data(capsys):
    code, out, err = run(["targets"], capsys)
    assert code == 0
    assert out == ""
    assert "UNIVERSAL Ω NUCLEUS GENERATOR" in err


# ---------------------------------------------------------------------------
# plan
# ---------------------------------------------------------------------------


def test_plan_states_what_would_exist_and_where(capsys):
    code, out, err = run(["plan", "--nucleus", COMPLETE_CAPABILITY, "--json"], capsys)
    assert code == 0
    payload = json.loads(out)
    assert payload["nucleus_id"] == COMPLETE_CAPABILITY
    assert payload["total"] == len(payload["artifacts"])
    assert payload["plan_id"] in err
    for artifact in payload["artifacts"]:
        assert artifact["destination"] in err


def test_plan_omits_the_rendered_bytes_unless_they_are_asked_for(capsys):
    _, summary_out, _ = run(["plan", "--nucleus", COMPLETE_CAPABILITY, "--json"], capsys)
    _, content_out, _ = run(
        ["plan", "--nucleus", COMPLETE_CAPABILITY, "--content", "--json"], capsys
    )
    summary = json.loads(summary_out)
    full = json.loads(content_out)
    assert "content" not in summary["artifacts"][0]
    assert full["artifacts"][0]["content"]
    assert summary["plan_id"] == full["plan_id"]


def test_plan_without_a_nucleus_is_a_fault_rather_than_a_plan_for_everything(capsys):
    code, out, err = run(["plan"], capsys)
    assert code == 2
    assert out == ""
    assert "requires --nucleus" in err


def test_plan_for_an_unregistered_nucleus_is_a_fault(capsys):
    code, _, err = run(["plan", "--nucleus", "UCOS-NOBODY-001"], capsys)
    assert code == 2
    assert "generation error:" in err


def test_planning_writes_nothing(capsys, tmp_path, monkeypatch):
    """A plan is a determination; materialising it is a separate constituent act."""
    monkeypatch.chdir(tmp_path)
    code, _, _ = run(["plan", "--nucleus", COMPLETE_CAPABILITY, "--content", "--json"], capsys)
    assert code == 0
    assert list(tmp_path.iterdir()) == []


def test_plan_is_replay_identical_across_two_invocations(capsys):
    _, first, _ = run(["plan", "--nucleus", COMPLETE_CAPABILITY, "--content", "--json"], capsys)
    _, second, _ = run(["plan", "--nucleus", COMPLETE_CAPABILITY, "--content", "--json"], capsys)
    assert first == second


# ---------------------------------------------------------------------------
# readiness
# ---------------------------------------------------------------------------


def test_readiness_counts_the_population_and_names_what_blocks_it(capsys):
    code, out, err = run(["readiness", "--json"], capsys)
    assert code == 0
    payload = json.loads(out)
    assert payload["nuclei"] > 0
    assert payload["generatable"] == payload["nuclei"] - len(payload["blocked"])
    assert payload["targets"] > 0 and payload["templates"] > 0
    assert payload["generator_fingerprint"]
    # The one nucleus declaring no catalogue cannot answer the catalogue destination.
    assert CATALOG_FREE_CAPABILITY in payload["blocked"]
    assert f"BLOCKED  {CATALOG_FREE_CAPABILITY}" in err


def test_readiness_gates_while_any_nucleus_is_blocked(capsys):
    code, _, err = run(["readiness", "--gate"], capsys)
    assert code == 1
    assert "GENERATION READINESS WITHHELD" in err


def test_readiness_passes_when_every_nucleus_answers_every_destination(capsys, stub_targets):
    """Zero findings means the Foundation can generate its whole population."""
    code, out, err = run(["readiness", "--targets", str(stub_targets), "--gate", "--json"], capsys)
    assert code == 0
    payload = json.loads(out)
    assert payload["blocked"] == {}
    assert payload["generatable"] == payload["nuclei"]
    assert "WITHHELD" not in err
    assert "BLOCKED" not in err


@pytest.mark.parametrize("command", ("targets", "templates", "plan"))
def test_gate_is_inert_on_a_command_that_determines_nothing(command, capsys):
    argv = [command, "--gate"]
    if command == "plan":
        argv += ["--nucleus", COMPLETE_CAPABILITY]
    code, _, err = run(argv, capsys)
    assert code == 0
    assert "WITHHELD" not in err


# ---------------------------------------------------------------------------
# specialisation and faults
# ---------------------------------------------------------------------------


def test_an_explicit_target_document_specialises_what_a_generation_produces(capsys, stub_targets):
    code, out, _ = run(["targets", "--targets", str(stub_targets), "--json"], capsys)
    assert code == 0
    payload = json.loads(out)
    assert payload["register_id"] == "test.targets"
    assert [item["target_id"] for item in payload["targets"]] == ["GT-01"]


def test_an_explicit_register_specialises_the_population_planned_over(capsys, tmp_path):
    code, _, err = run(["readiness", "--register", str(tmp_path / "absent.json")], capsys)
    assert code == 2
    assert "generation error:" in err


def test_an_unreadable_target_document_is_a_fault_not_a_pass(capsys, tmp_path):
    code, out, err = run(["targets", "--targets", str(tmp_path / "absent.json")], capsys)
    assert code == 2
    assert out == ""
    assert "generation error:" in err


def test_a_target_naming_an_unregistered_template_is_a_fault(capsys, tmp_path):
    path = tmp_path / "targets.json"
    path.write_text(
        json.dumps(
            {
                "register_id": "test.targets",
                "targets": [target("GT-01", template="no-such-renderer").to_dict()],
            }
        ),
        encoding="utf-8",
    )
    code, _, err = run(["targets", "--targets", str(path)], capsys)
    assert code == 2
    assert "no-such-renderer" in err


def test_a_faulted_run_claims_no_determination(capsys, tmp_path):
    code, _, err = run(["readiness", "--targets", str(tmp_path / "absent.json"), "--gate"], capsys)
    assert code == 2
    assert "UNIVERSAL Ω NUCLEUS GENERATOR" not in err


# ---------------------------------------------------------------------------
# the summary renderer
# ---------------------------------------------------------------------------


def _render(command: str, payload: dict) -> str:
    stream = io.StringIO()
    _print_summary(command, payload, stream)
    return stream.getvalue()


def test_the_summary_renders_an_empty_payload_without_inventing_a_reading():
    for command in COMMANDS:
        text = _render(command, {})
        assert f"command: {command}" in text
        assert "BLOCKED" not in text


def test_the_readiness_summary_reports_every_finding_for_every_blocked_nucleus():
    text = _render(
        "readiness",
        {
            "nuclei": 2,
            "generatable": 0,
            "targets": 10,
            "templates": 10,
            "blocked": {
                "UCOS-B-001": ["GT-07: cannot answer {catalog_path}"],
                "UCOS-A-001": ["GT-06: cannot answer {cli_path}", "GT-04: no registry"],
            },
        },
    )
    assert "BLOCKED  UCOS-A-001  GT-06" in text
    assert "BLOCKED  UCOS-A-001  GT-04" in text
    assert "BLOCKED  UCOS-B-001  GT-07" in text
    # Blocked nuclei are reported in identity order, not dictionary order.
    assert text.index("UCOS-A-001") < text.index("UCOS-B-001")


def test_the_register_is_only_read_for_the_commands_that_need_it(capsys, tmp_path):
    """targets and templates describe the generator, so a bad register cannot affect them."""
    for command in ("targets", "templates"):
        code, _, _ = run([command, "--register", str(tmp_path / "absent.json")], capsys)
        assert code == 0


def test_an_in_memory_register_and_the_declared_document_agree(stub_targets):
    """The CLI's --targets path loads exactly the register a caller would build itself."""
    from platform.universal_generator.registry import load_target_register

    loaded = load_target_register(stub_targets)
    built = TargetRegister(
        "test.targets",
        version="1.0.0",
        targets=[
            target(
                "GT-01",
                template="contract-surface",
                destination="{package_path}/generated_contracts.py",
            )
        ],
    )
    assert loaded.to_dict() == built.to_dict()
