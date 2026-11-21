"""Tests for engine.knowledge.integration.cli — the operational surface."""

from __future__ import annotations

import json

import pytest

from engine.knowledge.integration.cli import _load_base, build_parser, main


@pytest.fixture
def store(tmp_path):
    # a non-existent store dir forces the deterministic seed base
    return str(tmp_path / "kb")


def _write_intent(tmp_path, **fields) -> str:
    payload = {
        "intent_id": "UCKO-CLI-NEW",
        "kind": "pattern",
        "title": "cli widget",
        "statement": "xyzzy plugh frobnicate widget capability",
        "universe": "APPSVC",
        "authority": "engineering",
        "owner": "TEAM-A",
    }
    payload.update(fields)
    path = tmp_path / "intent.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _run(store, *args) -> int:
    return main(["--store", store, "--no-constitution", *args])


def test_parser_identity():
    assert build_parser().prog == "ucos-knowledge-integration"


def test_constitution_command(store, capsys):
    assert _run(store, "constitution") == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["laws"]) == 10


def test_pipeline_accepts_novel_intent(store, tmp_path, capsys):
    intent = _write_intent(tmp_path)
    assert _run(store, "pipeline", "--intent", intent) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["accepted"] is True
    assert out["outcome"] == "created"


def test_screen_clean_and_violation(store, tmp_path, capsys):
    assert _run(store, "screen", "--intent", _write_intent(tmp_path)) == 0
    capsys.readouterr()
    dup = _write_intent(tmp_path, intent_id="UCKO-PRIN-0001", universe="GOVERNANCE")
    assert _run(store, "screen", "--intent", dup) == 1


def test_discover_reuse_register_compose(store, tmp_path, capsys):
    intent = _write_intent(tmp_path)
    assert _run(store, "discover", "--intent", intent) == 0
    capsys.readouterr()
    assert _run(store, "reuse", "--intent", intent) == 0
    capsys.readouterr()
    assert _run(store, "register", "--intent", intent) == 0
    capsys.readouterr()
    # a novel intent has no components -> composition insufficient -> exit 1
    assert _run(store, "compose", "--intent", intent) == 1


def test_node_commands(store, capsys):
    assert _run(store, "trace", "UCKO-PRIN-0001") == 0
    capsys.readouterr()
    assert _run(store, "depends", "UCKO-PRIN-0001") == 0
    capsys.readouterr()
    assert _run(store, "govern", "UCKO-DEC-0001") == 0


def test_malformed_intent_exits_2(store, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"intent_id": "X"}), encoding="utf-8")  # missing fields
    assert _run(store, "discover", "--intent", str(bad)) == 2


def test_the_constitution_is_extended_into_the_base_unless_it_is_declined(store):
    """``--no-constitution`` is the OPT-OUT, so the default path was the untested one.

    Every test above passes the flag to keep its fixtures small, which left the ordinary
    invocation — the one an operator actually runs — taking a branch nothing exercised. The
    constitution is what the governance and grounding commands resolve references against,
    so a default that silently loaded nothing would make those commands answer over a base
    missing the very objects they are meant to check against.
    """

    declined = _load_base(store, with_constitution=False)
    extended = _load_base(store, with_constitution=True)

    assert len(extended.objects()) > len(declined.objects())
    assert set(declined.object_ids()) < set(extended.object_ids())
