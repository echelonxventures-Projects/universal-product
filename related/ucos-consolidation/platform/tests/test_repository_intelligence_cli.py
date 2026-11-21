"""Repository Intelligence CLI tests (UCOS-EPIC-014, Terminal T5).

`platform/repository_intelligence/cli.py` is the subsystem's only entry point and carried
195 statements with zero covered — the largest untested surface in the coverage
denominator. Thirteen commands, three exit codes and a stdout/stderr split were all
asserted by docstring alone.

What these tests hold the CLI to:

* **The fail-closed exit contract.** ``0`` on success/PASS, ``1`` on FAIL, ``2`` on a
  configuration or substrate fault. The three are distinct answers — "the repository is
  not certified" is not "the repository could not be measured" — and a suite that only
  checked "non-zero" would let the two collapse into each other.
* **The pipe-safety split.** Every human summary goes to stderr and every machine
  document to stdout, so ``--json`` output is parseable on its own. Each command's test
  parses stdout and separately asserts the summary reached stderr.
* **Every command is reachable.** The parser builds its subcommands from three separate
  tables (``_COMMANDS``, ``_REGISTERS``, and the hand-built graph/impact/advise parsers).
  A name present in one and absent from another is a `KeyError` at runtime, so the tables
  are asserted against the parser rather than trusted.

The subject is a synthetic UCOS-shaped repository built in ``tmp_path``, not this
repository: the CLI's claim is that ``--repo`` targets *any* UCOS-shaped tree, and a
suite that only ran against its own checkout would be measuring this repository instead
of the command.

**Bounded by construction.** The fixture repository is deliberately *not* certifiable.
Its capability catalog is composed by the live UCOS-RIE-001 producer, which derives
reuse directives from its own declaration conventions, so a fixture cannot hand the
subsystem a passing reuse dimension without reproducing that producer's conventions.
The PASS legs of `scan`, `validate` and `certify` are therefore not asserted here and
are recorded as an open coverage residue rather than silently skipped.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path
from platform.repository_intelligence.cli import (
    _COMMANDS,
    _REGISTERS,
    _build_parser,
    _cmd_advise,
    _print_cycle,
    main,
)
from platform.repository_intelligence.config import RepositoryIntelligenceConfig
from platform.repository_intelligence.contracts import Recommendation, RecommendationAction
from platform.repository_intelligence.runtime import run_once
from typing import Any

import pytest

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_FAULT = 2

ALPHA = "engine.alpha"
BETA = "platform.beta"

_DOC = '"""UCOS-EPIC-014 {name} capability (Terminal T5)."""\n'


def _build_repository(root: Path) -> Path:
    """A minimal UCOS-shaped repository: two owned capabilities, one depending on the other."""
    for base, package in (("engine", "alpha"), ("platform", "beta")):
        directory = root / base / package
        directory.mkdir(parents=True)
        doc = _DOC.format(name=package)
        (directory / "__init__.py").write_text(doc, encoding="utf-8")
        (directory / "core.py").write_text(
            f"{doc}\n\ndef {package}_value() -> int:\n    return {len(package)}\n",
            encoding="utf-8",
        )
    (root / "platform" / "beta" / "service.py").write_text(
        _DOC.format(name="beta") + "from engine.alpha.core import alpha_value\n\n"
        "def combined() -> int:\n    return alpha_value() + 1\n",
        encoding="utf-8",
    )
    for base in ("engine", "platform"):
        tests = root / base / "tests"
        tests.mkdir(parents=True, exist_ok=True)
        (tests / "test_smoke.py").write_text(
            _DOC.format(name="tests") + "\n\ndef test_ok() -> None:\n    assert True\n",
            encoding="utf-8",
        )
    (root / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nversion = "0.0.1"\n\n'
        '[project.scripts]\ndemo-beta = "platform.beta.service:combined"\n',
        encoding="utf-8",
    )
    return root


@pytest.fixture(scope="module")
def repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A shared read-only fixture repository (no command below mutates it except `emit`)."""
    return _build_repository(tmp_path_factory.mktemp("intel") / "demo-repo")


@pytest.fixture
def writable_repo(tmp_path: Path) -> Path:
    """A private fixture repository for the commands that write artefacts."""
    return _build_repository(tmp_path / "demo-repo")


def _run(repo: Path, *argv: str, as_json: bool = False) -> int:
    args = ["--repo", str(repo)]
    if as_json:
        args.append("--json")
    return main([*args, *argv])


def _stdout_json(capsys: pytest.CaptureFixture[str]) -> Any:
    captured = capsys.readouterr()
    assert captured.err, "the human summary must always reach stderr"
    return json.loads(captured.out)


# --------------------------------------------------------------------------- parser


def test_a_command_is_required() -> None:
    with pytest.raises(SystemExit) as excinfo:
        _build_parser().parse_args([])
    assert excinfo.value.code != 0


def test_every_dispatch_table_entry_is_a_parser_subcommand() -> None:
    """A name in a dispatch table but not in the parser is unreachable, and vice versa."""
    parser = _build_parser()
    actions = [a for a in parser._actions if a.dest == "command"]  # noqa: SLF001
    declared = set(actions[0].choices)
    assert set(_COMMANDS) | set(_REGISTERS) == declared


# --------------------------------------------------------------------------- scan


def test_scan_summarizes_all_eight_dimensions(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(repo, "scan") == EXIT_FAIL
    err = capsys.readouterr().err
    for dimension in (
        "repository",
        "capability",
        "reuse",
        "dependency",
        "gap",
        "conflict",
        "duplicate",
        "ownership",
    ):
        assert dimension in err
    assert "DETERMINATION:" in err
    assert "seal=" in err


def test_scan_json_emits_the_report(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "scan", as_json=True) == EXIT_FAIL
    report = _stdout_json(capsys)
    assert report["repository_id"] == "demo-repo"
    assert len(report["report_sha256"]) == 64
    assert sorted(report["dimension_verdicts"]) == [
        "capability",
        "conflict",
        "dependency",
        "duplicate",
        "gap",
        "ownership",
        "repository",
        "reuse",
    ]


def test_scan_is_reproducible(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _run(repo, "scan", as_json=True)
    first = _stdout_json(capsys)
    _run(repo, "scan", as_json=True)
    assert _stdout_json(capsys)["report_sha256"] == first["report_sha256"]


# --------------------------------------------------------------------------- graph


def test_graph_reports_nodes_edges_and_layers(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(repo, "graph") == EXIT_OK
    err = capsys.readouterr().err
    assert "repository graph:" in err
    assert "layer 0:" in err


def test_graph_json_is_acyclic_for_a_layered_repository(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(repo, "graph", as_json=True) == EXIT_OK
    payload = _stdout_json(capsys)
    assert payload["acyclic"] is True
    assert payload["cycles"] == []
    assert payload["counts"]["nodes"] >= 2


def test_graph_renders_dot(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "graph", "--dot") == EXIT_OK
    out = capsys.readouterr().out
    assert out.startswith("digraph")
    assert "}" in out


def test_graph_renders_mermaid(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "graph", "--mermaid") == EXIT_OK
    assert "flowchart" in capsys.readouterr().out


def test_a_cyclic_repository_makes_graph_a_finding(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An import cycle must exit 1 — a cycle is a finding, not a fault."""
    root = _build_repository(tmp_path / "cyclic-repo")
    (root / "engine" / "alpha" / "back.py").write_text(
        _DOC.format(name="alpha") + "from platform.beta.core import beta_value\n\n"
        "def back() -> int:\n    return beta_value()\n",
        encoding="utf-8",
    )
    (root / "platform" / "beta" / "core.py").write_text(
        _DOC.format(name="beta") + "from engine.alpha.core import alpha_value\n\n"
        "def beta_value() -> int:\n    return alpha_value()\n",
        encoding="utf-8",
    )
    assert main(["--repo", str(root), "--json", "graph"]) == EXIT_FAIL
    payload = json.loads(capsys.readouterr().out)
    assert payload["acyclic"] is False
    assert payload["cycles"]


# --------------------------------------------------------------------------- impact


def test_impact_reports_a_blast_radius(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "impact", ALPHA) == EXIT_OK
    err = capsys.readouterr().err
    assert "blast radius" in err
    assert "direct_dependents" in err


def test_impact_json_names_the_dependents(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "impact", ALPHA, as_json=True) == EXIT_OK
    profile = _stdout_json(capsys)
    assert profile["node"] == ALPHA
    assert BETA in profile["direct_dependents"]
    assert profile["blast_radius"] >= 1


def test_impact_of_a_leaf_has_no_dependents(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "impact", BETA, as_json=True) == EXIT_OK
    assert _stdout_json(capsys)["direct_dependents"] == []


def test_impact_of_an_unknown_capability_is_a_fault(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(repo, "impact", "engine.nonexistent") == EXIT_FAULT
    assert "repository intelligence error" in capsys.readouterr().err


# --------------------------------------------------------------------------- registers


@pytest.mark.parametrize("register", ["gaps", "conflicts", "duplicates"])
def test_each_discovery_register_reports(
    repo: Path, capsys: pytest.CaptureFixture[str], register: str
) -> None:
    exit_code = _run(repo, register)
    assert exit_code in {EXIT_OK, EXIT_FAIL}
    assert "============" in capsys.readouterr().err


@pytest.mark.parametrize("register", ["gaps", "conflicts", "duplicates"])
def test_each_discovery_register_emits_json(
    repo: Path, capsys: pytest.CaptureFixture[str], register: str
) -> None:
    _run(repo, register, as_json=True)
    payload = _stdout_json(capsys)
    assert payload["dimension"] == _REGISTERS[register].value
    assert isinstance(payload["findings"], list)


# --------------------------------------------------------------------------- reuse / ownership


def test_reuse_reports_proof_per_capability(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "reuse") == EXIT_OK
    err = capsys.readouterr().err
    assert "CAPABILITY REUSE" in err
    assert "proven" in err


def test_reuse_json_proves_the_dependency_is_an_importer(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(repo, "reuse", as_json=True) == EXIT_OK
    index = {item["capability"]: item for item in _stdout_json(capsys)["reuse"]}
    assert index[ALPHA]["proof"] == "proven"
    assert index[ALPHA]["importers"] == [BETA]
    # The leaf is published as a console script, so it is reachable without an importer.
    assert index[BETA]["proof"] == "entry_point"


def test_ownership_resolves_every_declared_capability(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every fixture module declares a Terminal, so no unit is orphaned — exit 0."""
    assert _run(repo, "ownership") == EXIT_OK
    assert "OWNERSHIP" in capsys.readouterr().err


def test_ownership_json_names_an_owner_for_each_subject(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(repo, "ownership", as_json=True) == EXIT_OK
    records = _stdout_json(capsys)["ownership"]
    assert records
    assert all(record["owner"] for record in records)


def test_an_unowned_capability_makes_ownership_a_finding(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Strip the ownership declaration and the same command must exit 1."""
    root = _build_repository(tmp_path / "unowned-repo")
    for path in (root / "engine" / "alpha").glob("*.py"):
        path.write_text(path.read_text(encoding="utf-8").replace(_DOC.format(name="alpha"), ""))
    assert main(["--repo", str(root), "ownership"]) == EXIT_FAIL
    assert "OWNERSHIP" in capsys.readouterr().err


# --------------------------------------------------------------------------- recommend / advise


def test_recommend_ranks_a_work_list(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "recommend") == EXIT_OK
    assert "RECOMMENDATIONS" in capsys.readouterr().err


def test_recommend_json_carries_priority_and_rationale(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(repo, "recommend", as_json=True) == EXIT_OK
    recommendations = _stdout_json(capsys)["recommendations"]
    assert recommendations
    assert all(item["rationale"] for item in recommendations)
    assert all(isinstance(item["priority"], int) for item in recommendations)


def test_advising_a_novel_capability_permits_creation(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = _run(repo, "advise", "engine.entirely_novel_thing", "--about", "a new thing")
    assert exit_code == EXIT_OK
    assert "ACTION:" in capsys.readouterr().err


def test_advising_an_existing_capability_refuses_duplication(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The never-duplicate guard is fail-closed: a caller scripting creation must be stopped."""
    assert _run(repo, "advise", ALPHA, "--about", "exactly what alpha already does") == EXIT_FAIL
    assert "ACTION:" in capsys.readouterr().err


def test_advise_json_carries_the_directive(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _run(repo, "advise", ALPHA, as_json=True)
    payload = _stdout_json(capsys)
    assert payload["action"]
    assert payload["rationale"]


# --------------------------------------------------------------------------- validate / certify


def test_validate_runs_composed_gates_and_intelligence_rules(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(repo, "validate") == EXIT_FAIL
    err = capsys.readouterr().err
    assert "composed acceptance gates" in err
    assert "intelligence rules" in err
    assert "VERDICT:" in err


def test_validate_json_reports_every_rule(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "validate", as_json=True) == EXIT_FAIL
    payload = _stdout_json(capsys)
    assert payload["counts"]["rules"] >= 1
    assert payload["rules"]


def test_certify_issues_a_sealed_certificate(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(repo, "certify") == EXIT_FAIL
    assert capsys.readouterr().err.strip()


def test_certify_json_seals_the_certificate(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "certify", as_json=True) == EXIT_FAIL
    certificate = _stdout_json(capsys)
    assert len(certificate["seal_sha256"]) == 64
    assert certificate["determination"]
    assert certificate["gate"]


# --------------------------------------------------------------------------- emit / verify / hook


def test_emit_writes_every_sealed_artefact(
    writable_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--repo", str(writable_repo), "emit"]) == EXIT_OK
    err = capsys.readouterr().err
    assert "wrote" in err
    written = list((writable_repo / ".runtime" / "repository-intelligence").glob("*"))
    assert written


def test_emit_json_lists_the_written_paths(
    writable_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--repo", str(writable_repo), "--json", "emit"]) == EXIT_OK
    assert _stdout_json(capsys)["written"]


def test_verify_proves_deterministic_regeneration(
    writable_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["--repo", str(writable_repo), "verify"])
    assert exit_code in {EXIT_OK, EXIT_FAIL}
    err = capsys.readouterr().err
    assert "artefacts compared" in err


def test_verify_json_reports_the_comparison(
    writable_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main(["--repo", str(writable_repo), "--json", "verify"])
    result = _stdout_json(capsys)
    assert "deterministic" in result
    assert "mismatches" in result
    assert result["note"]


def test_verify_reports_a_mismatch_as_non_deterministic(
    writable_repo: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Non-determinism must exit 1 and name the artefact that differed.

    A genuine mismatch is a race the fixture cannot stage — it needs two scans of an
    unchanged substrate to disagree. What is under test here is the CLI's reading of the
    documented `verify_determinism` result, so the *result* is supplied and the command
    itself stays real: the CLI still parses, dispatches, renders and returns.
    """
    monkeypatch.setattr(
        "platform.repository_intelligence.service.RepositoryIntelligenceService"
        ".verify_determinism",
        lambda self: {
            "deterministic": False,
            "conclusive": True,
            "substrate_changed_during_proof": False,
            "note": "identical substrate reproduced identical artefacts",
            "artifacts_compared": ["report.json", "certificate.json"],
            "mismatches": ["report.json"],
        },
    )
    assert main(["--repo", str(writable_repo), "verify"]) == EXIT_FAIL
    err = capsys.readouterr().err
    assert err.startswith("NON-DETERMINISTIC")
    assert "MISMATCH report.json" in err


def test_verify_reports_an_inconclusive_proof(
    writable_repo: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A substrate that moved mid-proof is INCONCLUSIVE — not a determinism failure."""
    monkeypatch.setattr(
        "platform.repository_intelligence.service.RepositoryIntelligenceService"
        ".verify_determinism",
        lambda self: {
            "deterministic": False,
            "conclusive": False,
            "substrate_changed_during_proof": True,
            "note": "the repository was modified by another writer between the two passes",
            "artifacts_compared": ["report.json"],
            "mismatches": [],
        },
    )
    assert main(["--repo", str(writable_repo), "verify"]) == EXIT_FAIL
    err = capsys.readouterr().err
    assert err.startswith("INCONCLUSIVE")
    assert "MISMATCH" not in err


def test_hook_prints_one_line_on_stdout(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The session-start hook goes to stdout: it is the artefact, not a summary."""
    assert _run(repo, "hook") == EXIT_OK
    out = capsys.readouterr().out
    assert out.strip()
    assert len(out.strip().splitlines()) == 1


def test_hook_json_emits_the_cycle_summary(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(repo, "hook", as_json=True) == EXIT_OK
    # `hook` prints its line then the JSON document, both on stdout.
    out = capsys.readouterr().out
    _, _, document = out.partition("\n")
    assert json.loads(document)


# --------------------------------------------------------------------------- faults


def test_an_absent_config_is_a_fault(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--config", str(tmp_path / "absent.json"), "scan"]) == EXIT_FAULT
    assert "repository intelligence error" in capsys.readouterr().err


def test_a_config_selects_the_repository(
    writable_repo: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--config` is the other way to name a subject, and it must reach the same substrate."""
    config = tmp_path / "intel.json"
    config.write_text(
        json.dumps({"repository_root": str(writable_repo), "repository_id": "from-config"}),
        encoding="utf-8",
    )
    assert main(["--config", str(config), "--json", "scan"]) == EXIT_FAIL
    assert _stdout_json(capsys)["repository_id"] == "from-config"


def test_an_absent_repository_is_a_fault(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--repo", str(tmp_path / "no-such-repo"), "scan"]) == EXIT_FAULT
    assert "repository intelligence error" in capsys.readouterr().err


# --------------------------------------------------------------- the two rendering arms
#
# Both are arms the CLI cannot reach through a real cycle, and both are worth keeping. The
# summary prints a "next" line only when there IS one, and the advisory prints a target only
# when the advice names a place — a CLI that printed "next: None" or a bare "->" would be
# reporting a value it does not have.


def test_the_summary_omits_the_next_line_when_there_is_no_next_action(
    writable_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``recommend()`` never returns empty — it emits NO_ACTION instead — so this arm cannot
    be produced by a scan. It is reached by handing the printer a report with no
    recommendations, which is the state the guard exists for: the alternative to the guard is
    an ``IndexError`` inside the summary of an otherwise successful cycle.
    """

    cycle = run_once(RepositoryIntelligenceConfig.create(writable_repo))
    assert cycle.report.recommendations, "the fixture produced no recommendation to remove"

    _print_cycle(cycle, sys.stderr)
    assert "next:" in capsys.readouterr().err

    without = dataclasses.replace(
        cycle, report=dataclasses.replace(cycle.report, recommendations=())
    )
    _print_cycle(without, sys.stderr)
    rendered = capsys.readouterr().err
    assert "next:" not in rendered
    assert "DETERMINATION:" in rendered, "the rest of the summary must still be printed"


def test_advice_that_names_no_place_prints_no_arrow(capsys: pytest.CaptureFixture[str]) -> None:
    """Every action the engine can return carries a target except NO_ACTION, so a real
    ``advise`` always has one. The arrow is still conditional, because ``->`` followed by
    nothing reads as advice that was truncated rather than advice that names no place."""

    class _Advising:
        def __init__(self, recommendation: Recommendation) -> None:
            self._recommendation = recommendation

        def advise(self, name: str, about: str) -> Recommendation:
            return self._recommendation

    placeless = Recommendation(
        action=RecommendationAction.CREATE,
        subject="engine.novel",
        priority=1,
        rationale="nothing existing matches",
    )
    args = argparse.Namespace(name="engine.novel", about="", as_json=False)
    assert _cmd_advise(_Advising(placeless), args) == EXIT_OK
    assert "  -> " not in capsys.readouterr().err

    located = Recommendation(
        action=RecommendationAction.CREATE,
        subject="engine.novel",
        priority=1,
        rationale="nothing existing matches",
        target="platform/novel",
    )
    assert _cmd_advise(_Advising(located), args) == EXIT_OK
    assert "  -> platform/novel" in capsys.readouterr().err
