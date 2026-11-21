"""Tests for engine.knowledge.cli — the Part 13 operational surface."""

from __future__ import annotations

import json

import pytest

from engine.knowledge import UKDA_CONTRACT
from engine.knowledge.cli import build_parser, main
from engine.knowledge.store import CANON_FILE


def _run(argv, capsys):
    code = main(argv)
    out = capsys.readouterr().out
    return code, out


def test_contract_identity():
    assert UKDA_CONTRACT.name == "knowledge.ukda"
    assert str(UKDA_CONTRACT.version) == "1.0.0"
    assert build_parser().prog == "ucos-knowledge"


def test_init_then_validate_certify(tmp_path, capsys):
    store = str(tmp_path / "k")
    code, out = _run(["--store", store, "init"], capsys)
    assert code == 0
    assert (tmp_path / "k" / CANON_FILE).is_file()
    # re-init without --force fails
    code2, _ = _run(["--store", store, "init"], capsys)
    assert code2 == 1
    # re-init with --force succeeds
    code3, _ = _run(["--store", store, "init", "--force"], capsys)
    assert code3 == 0
    code4, out4 = _run(["--store", store, "validate"], capsys)
    assert code4 == 0 and json.loads(out4)["accepted"] is True
    code5, out5 = _run(["--store", store, "certify"], capsys)
    assert code5 == 0 and json.loads(out5)["certified"] is True


def test_search_impact_stats_bootstrap_docs(tmp_path, capsys):
    store = str(tmp_path / "k")
    _run(["--store", store, "init"], capsys)
    code, out = _run(["--store", store, "search", "knowledge", "once"], capsys)
    assert code == 0 and any(h["cko_id"] == "UCKO-PRIN-0001" for h in json.loads(out))
    code, out = _run(["--store", store, "impact", "UCKO-PRIN-0001"], capsys)
    assert code == 0 and "transitive_impact" in json.loads(out)
    code, out = _run(["--store", store, "stats"], capsys)
    assert code == 0 and json.loads(out)["total_objects"] >= 10
    code, out = _run(["--store", store, "bootstrap", "--format", "json"], capsys)
    assert code == 0 and json.loads(out)["current_state"]
    code, out = _run(["--store", store, "bootstrap", "--format", "md"], capsys)
    assert code == 0 and "Bootstrap Brief" in out
    code, out = _run(["--store", store, "docs", "--out", str(tmp_path / "hb")], capsys)
    assert code == 0 and (tmp_path / "hb" / "DECISION-HANDBOOK.md").is_file()


def test_docs_default_out_dir(tmp_path, capsys):
    store = str(tmp_path / "k")
    _run(["--store", store, "init"], capsys)
    code, _ = _run(["--store", store, "docs"], capsys)
    assert code == 0
    assert (tmp_path / "k" / "handbooks" / "KNOWLEDGE-INDEX.md").is_file()


def test_portal_command(tmp_path, capsys):
    store = str(tmp_path / "k")
    _run(["--store", store, "init"], capsys)
    # explicit output directory
    code, out = _run(["--store", store, "portal", "--out", str(tmp_path / "p")], capsys)
    assert code == 0
    assert (tmp_path / "p" / "INDEX.md").is_file()
    assert (tmp_path / "p" / "CAPABILITY-PORTAL.md").is_file()
    assert "wrote" in out
    # default output directory (<store>/portal)
    code2, _ = _run(["--store", store, "portal"], capsys)
    assert code2 == 0
    assert (tmp_path / "k" / "portal" / "INDEX.md").is_file()


def test_commands_fall_back_to_seed_without_store(tmp_path, capsys):
    # A store dir that does not exist -> seed base is used.
    store = str(tmp_path / "absent")
    code, out = _run(["--store", store, "validate"], capsys)
    assert code == 0 and json.loads(out)["accepted"] is True


def test_error_path_returns_exit_2(tmp_path, capsys):
    store_dir = tmp_path / "corrupt"
    store_dir.mkdir()
    (store_dir / CANON_FILE).write_text("{bad json", encoding="utf-8")
    code = main(["--store", str(store_dir), "validate"])
    out = capsys.readouterr().out
    assert code == 2
    assert json.loads(out)["code"].startswith("UKDA")


def test_missing_command_exits_nonzero():
    with pytest.raises(SystemExit):
        main([])


def _catalog(tmp_path, *, name="engine.knowledge.ukip", location="engine/knowledge/ukip"):
    """A one-entry capability catalogue, written where the command can be pointed at it."""
    path = tmp_path / "catalog.json"
    path.write_text(
        json.dumps(
            {
                "capabilities": [
                    {
                        "unique_id": "RC-01",
                        "canonical_name": name,
                        "canonical_location": location,
                        "category": "engine",
                        "authority": "EC-1 CERTIFIED",
                        "reuse": "REUSE_AS_IS/COMPOSE",
                        "replacement_prohibited": True,
                        "implementation_status": "CERTIFIED",
                        "description": "Universal Knowledge Intelligence Platform.",
                        "evidence_present": True,
                        "summary": "Admits knowledge from an unbounded number of providers.",
                        "symbols": ["KnowledgeRegistry"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return str(path)


def test_capabilities_projects_read_only_and_reports_what_would_change(tmp_path, capsys):
    """REPOSITORY SELF-AWARENESS, and the reason the default is read-only.

    The projection exists so a gate can notice that the canonical layer has fallen behind
    the repository — a capability added without its canonical knowledge. That only works if
    running it changes nothing: a command that wrote by default would repair the drift it
    was asked to detect, and the gate could never fail.

    The whole command was unexecuted, which is the shape that matters here: it is the one
    surface through which the canonical layer learns what the repository contains.
    """
    store = str(tmp_path / "k")
    _run(["--store", store, "init"], capsys)
    before = (tmp_path / "k" / CANON_FILE).read_text(encoding="utf-8")

    code, out = _run(["--store", store, "capabilities", "--catalog", _catalog(tmp_path)], capsys)
    payload = json.loads(out)
    assert code == 0
    assert payload["discovered"] == 1
    created = payload["assimilation"]["created"]
    # The identity is CONTENT-ADDRESSED, so it is asserted as a shape rather than as a
    # literal: pinning the digest would make this test fail on any edit to the record.
    assert len(created) == 1 and created[0].startswith("UCKO-CAP-")
    assert payload["coverage_before"] != payload["coverage_after"]
    assert "wrote" not in payload
    assert (tmp_path / "k" / CANON_FILE).read_text(encoding="utf-8") == before


def test_capabilities_gates_on_a_canonical_layer_that_has_fallen_behind(tmp_path, capsys):
    """Exit 1 when the layer is stale, so a capability added without its canonical knowledge
    fails closed rather than being noticed by whoever happens to read the report."""
    store = str(tmp_path / "k")
    _run(["--store", store, "init"], capsys)
    catalog = _catalog(tmp_path)

    code, _ = _run(["--store", store, "capabilities", "--catalog", catalog, "--gate"], capsys)
    assert code == 1


def test_capabilities_write_persists_and_makes_the_gate_pass(tmp_path, capsys):
    """The write is what closes the gate, and re-running it is a no-op — which is the
    property that makes the projection safe to run on every commit rather than once."""
    store = str(tmp_path / "k")
    _run(["--store", store, "init"], capsys)
    catalog = _catalog(tmp_path)

    code, out = _run(["--store", store, "capabilities", "--catalog", catalog, "--write"], capsys)
    payload = json.loads(out)
    assert code == 0
    assert len(payload["wrote"]) == 2
    assert all(str(tmp_path) in written for written in payload["wrote"])

    code, out = _run(["--store", store, "capabilities", "--catalog", catalog, "--gate"], capsys)
    assert code == 0, "the projection did not settle, so re-running it is not a no-op"
    settled = json.loads(out)["assimilation"]
    assert settled["created"] == [] and settled["updated"] == []
    assert settled["retired"] == []
    assert settled["unchanged"]
