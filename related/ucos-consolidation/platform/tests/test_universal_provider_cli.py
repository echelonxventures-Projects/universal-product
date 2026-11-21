"""Universal Provider Architecture CLI tests (UPA-000013, Terminal-04).

`platform/universal_provider/cli.py` was the framework's only surface with no test at
all: 96 statements, zero covered. That is not a cosmetic gap. The CLI is the one place
where the framework's exit-code contract is stated — ``0`` success, ``1`` a
constitutional finding, ``2`` the command could not be executed — and an exit-code
contract nothing exercises is a claim rather than a behaviour. A refusal that returned
``0`` would make every downstream gate green over a refused provider.

Every command is driven through :func:`main` with an explicit ``argv``, so the tests
measure the parser and the handler together rather than calling handlers directly with
hand-built namespaces. Each command is asserted on both legs of its contract: the
success exit code *and* the finding exit code that the same command must produce when
the catalog says something is wrong.

The catalog is always a ``tmp_path`` of fixture manifests, never the repository's own,
except in the one test that deliberately measures the default-catalog branch: the
claim under test is that the CLI names no provider, so a suite that only ever ran
against the shipped catalog would be measuring the catalog rather than the CLI.
"""

from __future__ import annotations

import json
from pathlib import Path
from platform.tests.universal_provider_helpers import (
    memo_manifest,
    write_manifest,
)
from platform.universal_provider.cli import (
    DEFAULT_CATALOG,
    EXIT_ERROR,
    EXIT_FINDING,
    EXIT_OK,
    build_parser,
    main,
)
from platform.universal_provider.evidence import MANIFEST_FILENAME
from typing import Any

import pytest

MEMO_QUALIFIED_ID = "fixture.memo@1.0.0"


def _catalog(tmp_path: Path) -> Path:
    """A single-provider catalog directory."""
    directory = tmp_path / "catalog"
    write_manifest(directory, "memo.json", memo_manifest())
    return directory


def _emitted(capsys: pytest.CaptureFixture[str]) -> Any:
    """The JSON document the CLI printed on stdout."""
    return json.loads(capsys.readouterr().out)


# --------------------------------------------------------------------------- constitution


def test_constitution_prints_the_executable_constitution(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["constitution"]) == EXIT_OK
    payload = _emitted(capsys)
    assert payload["articles"]
    assert payload["constitution_id"]
    assert payload["operations"]


def test_constitution_takes_no_catalog() -> None:
    """The constitution is the framework's own text, so it cannot depend on a catalog."""
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["constitution", "--catalog", "anywhere"])


# --------------------------------------------------------------------------- discover


def test_discover_reports_a_declared_provider(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["discover", "--catalog", str(_catalog(tmp_path))]) == EXIT_OK
    payload = _emitted(capsys)
    assert payload["count"] == 1
    assert payload["kinds"] == ["memo"]
    assert payload["realizable"] == [MEMO_QUALIFIED_ID]
    assert payload["declared_only"] == []
    assert payload["conflicts"] == []
    assert payload["discovery_hash"]


def test_discover_separates_declared_only_from_realizable(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    directory = tmp_path / "catalog"
    write_manifest(directory, "realizable.json", memo_manifest())
    write_manifest(
        directory,
        "declared.json",
        {
            **memo_manifest(entry_point=""),
            "identity": {**memo_manifest()["identity"], "provider_id": "fixture.declared"},
        },
    )
    assert main(["discover", "--catalog", str(directory)]) == EXIT_OK
    payload = _emitted(capsys)
    assert payload["realizable"] == [MEMO_QUALIFIED_ID]
    assert payload["declared_only"] == ["fixture.declared@1.0.0"]


def test_a_discovery_conflict_is_a_finding_not_a_success(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two manifests, one qualified id, different bytes — the CLI must exit 1."""
    directory = tmp_path / "catalog"
    write_manifest(directory, "a.json", memo_manifest())
    write_manifest(directory, "b.json", memo_manifest(description="a different description"))
    assert main(["discover", "--catalog", str(directory)]) == EXIT_FINDING
    payload = _emitted(capsys)
    assert len(payload["conflicts"]) == 1
    assert payload["conflicts"][0]["qualified_id"] == MEMO_QUALIFIED_ID


def test_discover_falls_back_to_the_repository_catalog(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No ``--catalog`` means the declared default, resolved from the module's location."""
    assert main(["discover"]) in {EXIT_OK, EXIT_FINDING}
    payload = _emitted(capsys)
    assert payload["count"] >= 1
    assert (Path(__file__).resolve().parents[2] / DEFAULT_CATALOG).is_dir()


# --------------------------------------------------------------------------- onboard


def test_onboard_runs_the_pipeline_and_activates(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["onboard", "--catalog", str(_catalog(tmp_path))]) == EXIT_OK
    payload = _emitted(capsys)
    assert payload["providers"] == 1
    assert payload["active"] == [MEMO_QUALIFIED_ID]
    assert payload["tiers"][MEMO_QUALIFIED_ID]
    assert payload["lifecycle_intact"] is True
    assert payload["certification_intact"] is True
    assert payload["phases"]
    assert payload["state_hash"]
    assert "evidence" not in payload


def test_onboard_writes_an_evidence_bundle_that_verifies(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    destination = tmp_path / "evidence"
    exit_code = main(
        [
            "onboard",
            "--catalog",
            str(_catalog(tmp_path)),
            "--evidence",
            str(destination),
        ]
    )
    assert exit_code == EXIT_OK
    evidence = _emitted(capsys)["evidence"]
    assert evidence["directory"] == str(destination)
    assert evidence["bundle_hash"]
    assert MANIFEST_FILENAME in evidence["artifacts"]
    # The bundle the CLI just wrote must satisfy the CLI's own verifier.
    assert main(["verify-evidence", str(destination)]) == EXIT_OK


def test_a_refused_provider_makes_onboarding_a_finding(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A blocking constitutional failure must not exit 0."""
    directory = tmp_path / "catalog"
    write_manifest(directory, "refused.json", memo_manifest(source_of_record="", entry_point=""))
    assert main(["onboard", "--catalog", str(directory)]) == EXIT_FINDING
    payload = _emitted(capsys)
    assert payload["tiers"][MEMO_QUALIFIED_ID] == "refused"
    assert payload["active"] == []


# --------------------------------------------------------------------------- validate


def test_validate_accepts_a_version_pinned_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["validate", MEMO_QUALIFIED_ID, "--catalog", str(_catalog(tmp_path))])
    assert exit_code == EXIT_OK
    payload = _emitted(capsys)
    assert payload["qualified_id"] == MEMO_QUALIFIED_ID
    assert payload["status"]
    assert payload["report_hash"]
    assert payload["gates"]
    assert all(gate["gate_id"] and gate["article_id"] for gate in payload["gates"])


def test_validate_resolves_an_unpinned_id_to_its_highest_version(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["validate", "fixture.memo", "--catalog", str(_catalog(tmp_path))])
    assert exit_code == EXIT_OK
    assert _emitted(capsys)["qualified_id"] == MEMO_QUALIFIED_ID


def test_validate_reports_a_finding_for_a_failing_provider(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    directory = tmp_path / "catalog"
    write_manifest(directory, "refused.json", memo_manifest(source_of_record="", entry_point=""))
    assert main(["validate", MEMO_QUALIFIED_ID, "--catalog", str(directory)]) == EXIT_FINDING
    payload = _emitted(capsys)
    assert payload["status"] == "failed"
    assert payload["counts"]["fail"] >= 1
    assert payload["counts"]["blocking_failures"] >= 1


def test_validating_an_unknown_provider_could_not_be_executed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Exit 2 is not exit 1: "no such provider" is not a constitutional finding."""
    exit_code = main(["validate", "fixture.absent", "--catalog", str(_catalog(tmp_path))])
    assert exit_code == EXIT_ERROR
    captured = capsys.readouterr()
    assert captured.out == ""
    assert json.loads(captured.err)["code"].startswith("UPA-")


def test_an_unreadable_catalog_could_not_be_executed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["discover", "--catalog", str(tmp_path / "does-not-exist")])
    assert exit_code == EXIT_ERROR
    assert json.loads(capsys.readouterr().err)["code"].startswith("UPA-")


# --------------------------------------------------------------------------- state


def test_state_is_content_addressed_and_reproducible(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    catalog = _catalog(tmp_path)
    assert main(["state", "--catalog", str(catalog)]) == EXIT_OK
    first = _emitted(capsys)
    assert main(["state", "--catalog", str(catalog)]) == EXIT_OK
    second = _emitted(capsys)
    assert first == second
    assert first["constitution_hash"]
    assert first["registry"]
    assert first["lifecycle"]
    assert first["certification"]


# --------------------------------------------------------------------------- verify-evidence


def test_a_tampered_evidence_bundle_is_a_finding(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    destination = tmp_path / "evidence"
    assert (
        main(["onboard", "--catalog", str(_catalog(tmp_path)), "--evidence", str(destination)])
        == EXIT_OK
    )
    capsys.readouterr()
    victim = next(
        path for path in sorted(destination.glob("*.json")) if path.name != MANIFEST_FILENAME
    )
    victim.write_text(json.dumps({"tampered": True}), encoding="utf-8")
    assert main(["verify-evidence", str(destination)]) == EXIT_FINDING
    assert _emitted(capsys)["intact"] is False


def test_verifying_a_bundle_with_no_manifest_could_not_be_executed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    assert main(["verify-evidence", str(empty)]) == EXIT_ERROR
    assert json.loads(capsys.readouterr().err)["code"].startswith("UPA-")


# --------------------------------------------------------------------------- parser


def test_the_parser_requires_a_command() -> None:
    with pytest.raises(SystemExit) as excinfo:
        build_parser().parse_args([])
    assert excinfo.value.code != 0


def test_every_declared_subcommand_is_reachable() -> None:
    """The help text and the handler table must not drift apart."""
    parser = build_parser()
    for command in ("constitution", "discover", "onboard", "state", "verify-evidence"):
        argv = [command] if command != "verify-evidence" else [command, "somewhere"]
        assert callable(parser.parse_args(argv).handler)
    assert callable(parser.parse_args(["validate", "fixture.memo"]).handler)


def test_main_reads_sys_argv_when_given_no_argv(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.argv", ["ucos-provider", "constitution"])
    assert main() == EXIT_OK
    assert _emitted(capsys)["articles"]
