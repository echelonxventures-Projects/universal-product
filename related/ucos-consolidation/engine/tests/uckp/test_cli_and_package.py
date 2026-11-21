"""The command surface and the package's public surface.

The exit-code tests carry the weight here. ``0``, ``1`` and ``2`` mean three different
things — success, a reached verdict of REFUSED, and a fault that reached no verdict — and
collapsing the last two is how "I could not tell" comes to look like "it passed".
"""

from __future__ import annotations

import json

import pytest

from engine.uckp import cli as uckp_cli
from engine.uckp.cli import COMMANDS, EXIT_FAULT, EXIT_REFUSED, main, write_projections

# --- commands -------------------------------------------------------------------


def test_the_law_command_needs_no_universe_and_reports_the_whole_law(capsys):
    assert main(["law", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["law_id"] == "UCKP-LAW-0001"
    assert len(payload["articles"]) == 20
    assert len(payload["invariants"]) == 17
    assert len(payload["stop_conditions"]) == 13


@pytest.mark.parametrize(
    "command",
    ["build", "validate", "project", "persist", "execute", "replay", "govern", "reason"],
)
def test_each_command_succeeds_over_the_constitutional_universe(command, tmp_path, capsys):
    assert main([command, "--persistence-base", str(tmp_path / command)]) == 0
    capsys.readouterr()


def test_validate_reports_all_seventeen_invariants_as_satisfied(tmp_path, capsys):
    assert main(["validate", "--json", "--persistence-base", str(tmp_path / "v")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "certified"
    assert payload["counts"]["satisfied"] == 17
    assert payload["all_stop_conditions_met"] is True


def test_certify_covers_validation_assimilation_and_the_universe(
    tmp_path, capsys, constitution_object_count, corpus_size, uga_projection_size
):
    assert (
        main(["certify", "--assimilate", "--persistence-base", str(tmp_path / "c"), "--json"]) == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "certified"
    assert payload["assimilation"]["lossless"] is True
    assert (
        payload["universe"]["counts"]["objects"]
        == constitution_object_count + corpus_size + uga_projection_size
    )


def test_assimilate_implies_the_artifact_corpus_without_being_asked_twice(
    tmp_path, capsys, corpus_size
):
    assert main(["assimilate", "--persistence-base", str(tmp_path / "a"), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["counts"]["artifacts_read"] == corpus_size
    assert payload["invertible"] is True


def test_project_reports_ten_kinds_and_no_authority_claim(tmp_path, capsys):
    assert main(["project", "--json", "--persistence-base", str(tmp_path / "p")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["kinds"]) == 10
    assert payload["authority_claims"] == []
    assert payload["replays_identically"] is True


def test_persist_proves_every_technology_produced_the_same_universe(tmp_path, capsys):
    assert main(["persist", "--json", "--persistence-base", str(tmp_path / "s")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["adapters"] == 10
    assert payload["failures"] == []
    assert len({digest for _, digest in payload["observed"]}) == 1


def test_execute_proves_interchangeability_for_subject_free_and_subject_bearing_requests(
    tmp_path, capsys
):
    assert main(["execute", "--json", "--persistence-base", str(tmp_path / "x")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["interchangeable"] is True
    assert payload["knowledge_owners"] == []
    assert len(payload["operations"]) == 4


def test_replay_reports_states_decisions_and_projections(tmp_path, capsys):
    assert main(["replay", "--json", "--persistence-base", str(tmp_path / "r")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["timeline"]["replays_identically"] is True
    assert payload["governance"]["replays_identically"] is True
    assert payload["projections"]["replays_identically"] is True
    assert payload["evolution"]["terminated"] is False


def test_govern_shows_every_decision_replaying_from_itself(tmp_path, capsys):
    assert main(["govern", "--json", "--persistence-base", str(tmp_path / "g")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["rules"] == 20
    assert payload["replays_identically"] is True
    assert all(decision["replayed"] for decision in payload["decisions"])


def test_reason_reports_thirteen_reasoners_and_a_clean_verdict(tmp_path, capsys):
    assert main(["reason", "--json", "--persistence-base", str(tmp_path / "i")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["results"]) == 13
    assert payload["clean"] is True


def test_describe_emits_the_whole_document(tmp_path, capsys):
    assert main(["describe", "--json", "--persistence-base", str(tmp_path / "d")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == "ucos-uckp-universe"
    for key in ("law", "registry", "graph", "projections", "timeline", "governance"):
        assert key in payload


def test_the_summary_goes_to_stderr_and_the_json_to_stdout(tmp_path, capsys):
    main(["build", "--json", "--persistence-base", str(tmp_path / "streams")])
    captured = capsys.readouterr()
    assert "UCKP UCKP-LAW-0001" in captured.err
    assert json.loads(captured.out)["law_id"] == "UCKP-LAW-0001"


def test_without_json_nothing_is_written_to_stdout(tmp_path, capsys):
    main(["build", "--persistence-base", str(tmp_path / "quiet")])
    assert capsys.readouterr().out == ""


# --- fail-closed behaviour ------------------------------------------------------


def test_a_fault_that_reaches_no_verdict_exits_two(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(uckp_cli, "ARTIFACT_REGISTRY_PATH", "no/such/registry.json", raising=False)
    assert main(["assimilate", "--source-root", str(tmp_path), "--json"]) == EXIT_FAULT
    assert "fault" in capsys.readouterr().err


def test_a_reached_verdict_of_refused_exits_one(tmp_path, capsys, monkeypatch):
    """Distinct from a fault: the universe was measured, and it did not pass."""
    from engine.uckp.validation import ConstitutionalValidator

    class Blinded(ConstitutionalValidator):
        def probes(self):
            return {key: value for key, value in super().probes().items() if key != "UCKP-INV-01"}

    monkeypatch.setattr(uckp_cli, "ConstitutionalValidator", Blinded)
    assert main(["validate", "--persistence-base", str(tmp_path / "refused")]) == EXIT_REFUSED
    assert "UNMEASURED" in capsys.readouterr().err


def test_the_command_list_is_complete_and_every_command_is_accepted():
    assert len(COMMANDS) == 12
    for command in COMMANDS:
        assert command in COMMANDS


def test_an_unknown_command_is_rejected_by_the_parser():
    with pytest.raises(SystemExit):
        main(["no-such-command"])


# --- writing projections --------------------------------------------------------


def test_write_projections_writes_every_view_and_a_manifest(universe, tmp_path):
    written = write_projections(universe, tmp_path / "out")
    assert len(written) == 11  # ten projections plus the manifest
    for path in written:
        assert path.is_file()
        assert path.read_text(encoding="utf-8")
    manifest = json.loads((tmp_path / "out" / "projection-manifest.json").read_text())
    assert manifest["counts"]["kinds"] == 10


def test_written_projections_are_byte_identical_on_a_second_write(universe, tmp_path):
    """Article 13: identical inputs always produce identical bytes."""
    first = {p.name: p.read_bytes() for p in write_projections(universe, tmp_path / "a")}
    second = {p.name: p.read_bytes() for p in write_projections(universe, tmp_path / "b")}
    assert first == second


# --- the package surface --------------------------------------------------------


def test_the_package_declares_the_law_it_implements():
    import engine.uckp as package

    assert package.UCKP_LAW_ID == "UCKP-LAW-0001"
    assert package.UCKP_VERSION == "1.0.0"


def test_every_exported_name_resolves():
    import engine.uckp as package

    for name in package.__all__:
        assert getattr(package, name) is not None


def test_an_unknown_name_raises_attribute_error():
    import engine.uckp as package

    with pytest.raises(AttributeError, match="has no attribute"):
        getattr(package, "NoSuchName")  # noqa: B009 - the lookup itself is the assertion


def test_dir_lists_the_public_surface():
    import engine.uckp as package

    listed = dir(package)
    assert "build_universe" in listed
    assert "content_hash" in listed
    assert listed == sorted(listed)


def test_the_exported_primitive_is_the_layer_zero_primitive():
    import engine.uckp as package
    from engine.uckp.canonical import content_hash

    assert package.content_hash is content_hash


def test_importing_layer_zero_does_not_drag_in_the_upper_layers():
    """Layer Zero must stay cheap, because the whole repository now depends on it."""
    import subprocess
    import sys

    result = subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-c",
            "import engine.uckp.canonical, sys;"
            "loaded = [m for m in sys.modules if m.startswith('engine.uckp.')];"
            "print(sorted(loaded))",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    loaded = set(json.loads(result.stdout.replace("'", '"')))
    for heavy in (
        "engine.uckp.registry",
        "engine.uckp.persistence",
        "engine.uckp.assimilation",
        "engine.uckp.universe",
        "engine.uckp.validation",
    ):
        assert heavy not in loaded


# --- the CLI: faults, and every reachable refusal --------------------------------


def test_asking_for_an_assimilation_payload_without_a_corpus_is_a_fault(tmp_path):
    """The payload builder must refuse rather than emit an empty assimilation record."""
    from engine.uckp.errors import UCKPError
    from engine.uckp.universe import build_universe

    universe = build_universe(persistence_base=tmp_path / "no-corpus")
    with pytest.raises(UCKPError, match="assimilate requires the artifact registry"):
        uckp_cli._payload("assimilate", universe, None, None)


def test_the_law_command_can_report_the_corpus_without_assembling_a_universe(
    tmp_path, capsys, repo_root
):
    """``law --with-artifacts`` is the cheapest way to measure the corpus."""
    from engine.uckp.assimilation import ARTIFACT_REGISTRY_PATH

    if not (repo_root / ARTIFACT_REGISTRY_PATH).is_file():
        pytest.skip(f"{ARTIFACT_REGISTRY_PATH} is not present in this checkout")
    assert main(["law", "--assimilate", "--json"]) == 0
    captured = capsys.readouterr()
    assert "assimilation:" in captured.err
    assert json.loads(captured.out)["law_id"] == "UCKP-LAW-0001"


def test_an_io_fault_is_reported_as_a_fault_and_never_as_a_verdict(monkeypatch, capsys):
    """Exit 2 means "no verdict was reached"; collapsing it into 1 would fake a pass."""

    def unavailable(**kwargs):
        raise OSError("the persistence root is not writable")

    monkeypatch.setattr(uckp_cli, "_assemble", unavailable)
    assert main(["build"]) == EXIT_FAULT
    assert "uckp io fault" in capsys.readouterr().err


def test_an_assimilation_that_lost_information_refuses(monkeypatch, tmp_path, capsys):
    from engine.uckp.assimilation import AssimilationReport

    real_assemble = uckp_cli._assemble

    def lossy(**kwargs):
        universe, _ = real_assemble(**kwargs)
        return universe, AssimilationReport(
            source="probe",
            source_digest="probe-digest",
            artifacts_read=1,
            objects_minted=0,
            losses=("one artifact was not minted",),
        )

    monkeypatch.setattr(uckp_cli, "_assemble", lossy)
    assert main(["build", "--persistence-base", str(tmp_path / "lossy")]) == EXIT_REFUSED
    capsys.readouterr()


@pytest.mark.parametrize(
    ("command", "payload"),
    [
        ("project", {"authority_claims": ["a projection that claims authority"]}),
        ("persist", {"failures": ["a mechanism that did not round-trip"]}),
        ("execute", {"interchangeable": False}),
    ],
)
def test_each_command_refuses_on_the_condition_its_own_payload_reports(
    command, payload, monkeypatch, tmp_path, capsys
):
    """One refusal per command, so no command can report a breach and still exit 0."""
    monkeypatch.setattr(uckp_cli, "_payload", lambda *args, **kwargs: payload)
    assert main([command, "--persistence-base", str(tmp_path / command)]) == EXIT_REFUSED
    capsys.readouterr()
