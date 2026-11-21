"""Commercial Intelligence CLI tests (UCOS-EPIC-014, Terminal T5).

`platform/commercial_intelligence/cli.py` carried 60 statements and zero coverage. The
module states the command's fail-closed contract — ``0`` iff the verdict is PASS, ``1``
on FAIL, ``2`` on a malformed configuration — and it is the only place that contract is
expressed. Untested, "fail-closed" was a docstring: a CLI that returned ``0`` over a
NOT-CERTIFIED commercial surface would make every pipeline consuming it green over a
refusal, and nothing would have noticed.

Two further behaviours are asserted here because they are contracts rather than
conveniences:

* **The summary goes to stderr and the artefacts to stdout.** The module promises the
  command "composes in a pipeline without the summary contaminating the JSON". That is
  only true if stdout is parseable JSON when a ``--json``-family flag is given, so every
  emission test parses stdout and separately asserts the summary landed on stderr.
* **An advisory failure is not a blocking one.** `_print_summary` marks findings ``BLOCK``
  or ``ADVIS`` and the two lead to different determinations (NOT-CERTIFIED against
  CERTIFIED-PROVISIONAL) and different exit codes. A suite that only ever produced blocking
  failures would leave the distinction the certification tiers rest on unmeasured.

Configurations are built from :mod:`platform.tests.commercial_helpers` and mutated
minimally, so each test names the one fact it changed and why that changes the verdict.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from platform.commercial_intelligence.cli import main
from platform.tests.commercial_helpers import valid_config
from typing import Any

import pytest

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_FAULT = 2


def _write(tmp_path: Path, payload: Any, name: str = "commercial.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _passing(tmp_path: Path) -> Path:
    return _write(tmp_path, valid_config())


def _blocking_failure(tmp_path: Path) -> Path:
    """An empty fact set for a declared domain — CMI-VAL-002, a blocking failure."""
    config = copy.deepcopy(valid_config())
    config["facts"]["marketplace_intelligence"] = {}
    return _write(tmp_path, config)


def _advisory_failure(tmp_path: Path) -> Path:
    """Concentration above the declared bound — CMI-PTF-003, advisory only."""
    config = copy.deepcopy(valid_config())
    config["facts"]["portfolio_intelligence"]["max_concentration_basis_points"] = 1
    return _write(tmp_path, config)


# --------------------------------------------------------------------------- verdicts


def test_a_certified_surface_exits_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--config", str(_passing(tmp_path))]) == EXIT_PASS
    captured = capsys.readouterr()
    assert "DETERMINATION: CERTIFIED" in captured.err
    assert "VERDICT: PASS" in captured.err
    # No artefact flag was given, so stdout must be empty.
    assert captured.out == ""


def test_a_blocking_failure_exits_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--config", str(_blocking_failure(tmp_path))]) == EXIT_FAIL
    err = capsys.readouterr().err
    assert "VERDICT: FAIL" in err
    assert "DETERMINATION: NOT-CERTIFIED" in err
    assert "BLOCK CMI-VAL-002" in err


def test_an_advisory_failure_is_provisional_not_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Advisory != blocking: the run still passes, but only provisionally."""
    assert main(["--config", str(_advisory_failure(tmp_path))]) == EXIT_PASS
    err = capsys.readouterr().err
    assert "ADVIS CMI-PTF-003" in err
    assert "DETERMINATION: CERTIFIED-PROVISIONAL" in err
    assert "VERDICT: PASS" in err


def test_the_summary_names_every_domain_and_family(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--config", str(_passing(tmp_path))]) == EXIT_PASS
    err = capsys.readouterr().err
    for domain in (
        "marketplace_intelligence",
        "licensing_intelligence",
        "product_intelligence",
        "portfolio_intelligence",
        "business_documentation",
        "commercial_packages",
        "pricing_intelligence",
        "investment_intelligence",
        "customer_intelligence",
        "policy_governance",
        "approval_intelligence",
        "business_evidence",
        "commercial_validation",
        "commercial_certification",
    ):
        assert domain in err
    for family in ("assurance", "commerce", "governance", "offer"):
        assert f"family {family}" in err
    assert "42 checks" in err
    assert "certificate:" in err
    assert "evidence:" in err


# --------------------------------------------------------------------------- artefacts


def test_json_emits_the_report_on_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--config", str(_passing(tmp_path)), "--json"]) == EXIT_PASS
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["target_id"] == "TEST-TARGET"
    assert report["verdict"] == "pass"
    assert report["passed"] is True
    assert len(report["domains"]) == 14
    assert len(report["domain_verdicts"]) == 14
    assert report["blocking_failures"] == []
    assert len(report["report_sha256"]) == 64
    # The summary must not have contaminated the machine artefact.
    assert "COMMERCIAL INTELLIGENCE SUMMARY" in captured.err


def test_dashboard_emits_the_dashboard_on_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--config", str(_passing(tmp_path)), "--dashboard"]) == EXIT_PASS
    assert json.loads(capsys.readouterr().out)


def test_certificate_emits_a_hashed_certificate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--config", str(_passing(tmp_path)), "--certificate"]) == EXIT_PASS
    certificate = json.loads(capsys.readouterr().out)
    assert certificate["determination"] == "CERTIFIED"
    assert len(certificate["certificate_sha256"]) == 64


def test_evidence_emits_a_hashed_evidence_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--config", str(_passing(tmp_path)), "--evidence"]) == EXIT_PASS
    evidence = json.loads(capsys.readouterr().out)
    assert len(evidence["evidence_sha256"]) == 64


def test_every_artefact_flag_may_be_combined(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """All four documents, in declared order, each a complete JSON value."""
    exit_code = main(
        [
            "--config",
            str(_passing(tmp_path)),
            "--json",
            "--dashboard",
            "--certificate",
            "--evidence",
        ]
    )
    assert exit_code == EXIT_PASS
    decoder = json.JSONDecoder()
    out = capsys.readouterr().out
    index = 0
    documents = []
    while index < len(out):
        value, offset = decoder.raw_decode(out, index)
        documents.append(value)
        index = offset
        while index < len(out) and out[index] in " \n\r\t":
            index += 1
    assert len(documents) == 4
    assert documents[0]["target_id"] == "TEST-TARGET"
    assert documents[2]["determination"] == "CERTIFIED"
    assert documents[3]["evidence_sha256"]


def test_the_artefacts_are_reproducible(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    config = _passing(tmp_path)
    assert main(["--config", str(config), "--certificate"]) == EXIT_PASS
    first = capsys.readouterr().out
    assert main(["--config", str(config), "--certificate"]) == EXIT_PASS
    assert capsys.readouterr().out == first


# --------------------------------------------------------------------------- faults


def test_an_absent_config_is_a_fault_not_a_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Exit 2, not 1: an unreadable config is not a commercial verdict."""
    assert main(["--config", str(tmp_path / "absent.json")]) == EXIT_FAULT
    assert "commercial intelligence error" in capsys.readouterr().err


def test_an_unsupported_config_suffix_is_a_fault(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "commercial.yaml"
    path.write_text("target_id: TEST", encoding="utf-8")
    assert main(["--config", str(path)]) == EXIT_FAULT
    assert "commercial intelligence error" in capsys.readouterr().err


def test_a_malformed_config_is_a_fault(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "commercial.json"
    path.write_text("{not json", encoding="utf-8")
    assert main(["--config", str(path)]) == EXIT_FAULT
    assert "commercial intelligence error" in capsys.readouterr().err


def test_an_unknown_domain_is_a_fault(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    config = copy.deepcopy(valid_config())
    config["facts"]["marketplace"] = {}
    assert main(["--config", str(_write(tmp_path, config))]) == EXIT_FAULT
    assert "unknown commercial-intelligence domain" in capsys.readouterr().err


def test_a_faulting_run_emits_no_artefact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A fault must short-circuit before any document reaches stdout."""
    exit_code = main(["--config", str(tmp_path / "absent.json"), "--json", "--certificate"])
    assert exit_code == EXIT_FAULT
    assert capsys.readouterr().out == ""


# --------------------------------------------------------------------------- parser


def test_config_is_required() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code != 0
