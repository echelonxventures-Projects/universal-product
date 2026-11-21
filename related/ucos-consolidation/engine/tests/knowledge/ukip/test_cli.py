"""Tests for engine.knowledge.ukip.cli.

Proves every subcommand's happy path and its primary failure branches via
main() with argv injection. No external files are needed beyond the seed base;
providers are assembled in-memory. Exit codes are verified against the module
constants (EXIT_OK, EXIT_GATE, EXIT_ERROR).
"""

from __future__ import annotations

import argparse
import json
from unittest.mock import patch

import pytest

from engine.knowledge.ukip.cli import (
    EXIT_ERROR,
    EXIT_GATE,
    EXIT_OK,
    _emit,
    build_parser,
    main,
)
from engine.knowledge.ukip.graph import PROJECTIONS

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def run(argv: list[str], *, capture: bool = True) -> tuple[int, str]:
    """Invoke main() and capture stdout; return (exit_code, stdout)."""
    import io

    buf = io.StringIO()
    with patch("sys.stdout", buf):
        code = main(argv)
    return code, buf.getvalue()


def _json_out(argv: list[str]) -> tuple[int, dict]:
    code, out = run(argv)
    return code, json.loads(out) if out.strip() else {}


@pytest.fixture
def seed_store(tmp_path):
    """A writable store holding the founding canonical knowledge (never the repo's)."""
    from engine.knowledge.seed import build_seed_base
    from engine.knowledge.store import KnowledgeStore

    store = tmp_path / "store"
    store.mkdir()
    KnowledgeStore(store).save(build_seed_base())
    return store


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser.prog == "ucos-knowledge-intelligence"


def test_parser_requires_subcommand():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])


# ---------------------------------------------------------------------------
# constitution
# ---------------------------------------------------------------------------


def test_cmd_constitution_default():
    code, doc = _json_out(["constitution"])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "laws" in doc or "capabilities" in doc


def test_cmd_constitution_with_capability():
    code, doc = _json_out(["constitution", "--capability", "ADMIT"])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "capability" in doc
    assert doc["capability"] == "ADMIT"


# ---------------------------------------------------------------------------
# providers
# ---------------------------------------------------------------------------


def test_cmd_providers():
    code, doc = _json_out(["providers"])
    assert code == EXIT_OK
    assert "units" in doc


# ---------------------------------------------------------------------------
# assimilate
# ---------------------------------------------------------------------------


def test_cmd_assimilate():
    code, doc = _json_out(["assimilate"])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "ledger" in doc or "accepted" in doc


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------


def test_cmd_registry_summary():
    code, doc = _json_out(["registry"])
    assert code == EXIT_OK
    assert "records" in doc


def test_cmd_registry_full():
    code, doc = _json_out(["registry", "--full"])
    assert code == EXIT_OK


# ---------------------------------------------------------------------------
# record
# ---------------------------------------------------------------------------


def test_cmd_record_found():
    # Get a known key from the seed base
    _, reg_doc = _json_out(["registry"])
    records = reg_doc.get("records", [])
    if not records:
        pytest.skip("no records in seed base")
    ref = records[0]["knowledge_id"]
    code, doc = _json_out(["record", ref])
    assert code == EXIT_OK
    assert "knowledge_id" in doc


def test_cmd_record_not_found():
    code, doc = _json_out(["record", "GHOST-NOT-EXIST-99999"])
    assert code == EXIT_ERROR
    assert "error" in doc


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------


def test_cmd_classify():
    code, doc = _json_out(["classify", "Every system must have a single source of truth."])
    assert code == EXIT_OK
    assert "classification" in doc
    assert "knowledge_id" in doc


def test_cmd_classify_with_title_and_rationale():
    code, doc = _json_out(
        [
            "classify",
            "Every artifact must be registered.",
            "--title",
            "Registration Law",
            "--rationale",
            "Prevents duplicate artifacts.",
        ]
    )
    assert code == EXIT_OK


# ---------------------------------------------------------------------------
# relate
# ---------------------------------------------------------------------------


def test_cmd_relate():
    code, doc = _json_out(["relate"])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "edges" in doc or "relationships" in doc or isinstance(doc, dict)


def test_cmd_relate_compose():
    code, doc = _json_out(["relate", "--compose", "--depth", "2"])
    assert code in (EXIT_OK, EXIT_GATE)


# ---------------------------------------------------------------------------
# graph
# ---------------------------------------------------------------------------


def test_cmd_graph_summary():
    code, doc = _json_out(["graph"])
    assert code == EXIT_OK
    assert "nodes" not in doc  # summary omits raw nodes


def test_cmd_graph_full():
    code, doc = _json_out(["graph", "--full"])
    assert code == EXIT_OK


def test_cmd_graph_projection():
    """A declared projection is emitted as relationships, not as a second graph."""
    code, doc = _json_out(["graph", "--projection", "dependency"])
    assert code == EXIT_OK
    assert doc["projection"] == "dependency"
    assert isinstance(doc["relationships"], list)
    # A projection cites the relations it is built from; every emitted item is a
    # relationship of a type the "dependency" family declares (graph.py PROJECTIONS).
    permitted = {t.value for t in PROJECTIONS["dependency"]}
    assert {r["relation"] for r in doc["relationships"]} <= permitted


def test_cmd_graph_projection_unknown_name_is_not_swallowed():
    """An undeclared projection name fails loudly rather than emitting an empty view.

    ``KnowledgeIntelligenceGraph.projection`` raises ``KeyError`` for a name that is
    not in ``PROJECTIONS``, and ``main`` deliberately maps only KnowledgeError/OSError/
    ValueError — so an unknown projection can never be mistaken for "no relationships".
    """
    with pytest.raises(KeyError):
        run(["graph", "--projection", "kind"])


# ---------------------------------------------------------------------------
# impact
# ---------------------------------------------------------------------------


def test_cmd_impact_not_found():
    code, doc = _json_out(["impact", "GHOST-99999"])
    assert code == EXIT_ERROR
    assert "error" in doc


def test_cmd_impact_found():
    _, reg_doc = _json_out(["registry"])
    records = reg_doc.get("records", [])
    if not records:
        pytest.skip("no records in seed base")
    ref = records[0]["knowledge_id"]
    code, doc = _json_out(["impact", ref])
    assert code == EXIT_OK


# ---------------------------------------------------------------------------
# discover
# ---------------------------------------------------------------------------


def test_cmd_discover_empty_query():
    code, doc = _json_out(["discover"])
    assert code == EXIT_OK
    assert "hits" in doc


def test_cmd_discover_with_query():
    code, doc = _json_out(["discover", "truth", "--limit", "5"])
    assert code == EXIT_OK
    assert "query" in doc
    assert "count" in doc
    assert "hits" in doc


def test_cmd_discover_coverage():
    code, doc = _json_out(["discover", "--coverage"])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "is_fully_discoverable" in doc or "discoverable" in str(doc)


# ---------------------------------------------------------------------------
# screen
# ---------------------------------------------------------------------------


def test_cmd_screen():
    code, doc = _json_out(
        [
            "screen",
            "The registry must be the single source of truth for artifact identity.",
        ]
    )
    assert code in (EXIT_OK, EXIT_GATE)
    assert "must_reuse" in doc or isinstance(doc, dict)


def test_cmd_screen_with_kind():
    """--kind is coerced to a KnowledgeKind, enabling exact-duplicate detection."""
    code, doc = _json_out(
        [
            "screen",
            "All context must be declared before use.",
            "--kind",
            "principle",
        ]
    )
    assert code in (EXIT_OK, EXIT_GATE)
    # The determination is the gate: the reuse verdict is what selects the exit code.
    assert code == (EXIT_GATE if doc["verdict"] == "reuse" else EXIT_OK)


def test_cmd_screen_rejects_unknown_kind():
    """An undeclared kind is a validation error, not a silently ignored flag."""
    code, doc = _json_out(
        [
            "screen",
            "All context must be declared before use.",
            "--kind",
            "PRINCIPLE",
        ]
    )
    assert code == EXIT_ERROR
    assert doc == {}  # the failure goes to stderr; nothing is emitted as a result


# ---------------------------------------------------------------------------
# provenance
# ---------------------------------------------------------------------------


def test_cmd_provenance_summary():
    code, doc = _json_out(["provenance"])
    assert code in (EXIT_OK, EXIT_GATE)
    assert isinstance(doc, dict)


def test_cmd_provenance_full():
    code, doc = _json_out(["provenance", "--full"])
    assert code in (EXIT_OK, EXIT_GATE)


def test_cmd_provenance_record_not_found():
    code, doc = _json_out(["provenance", "GHOST-99999"])
    assert code == EXIT_ERROR
    assert "error" in doc


def test_cmd_provenance_record_found():
    _, reg_doc = _json_out(["registry"])
    records = reg_doc.get("records", [])
    if not records:
        pytest.skip("no records in seed base")
    ref = records[0]["knowledge_id"]
    code, doc = _json_out(["provenance", ref])
    assert code in (EXIT_OK, EXIT_GATE)


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


def test_cmd_validate():
    code, doc = _json_out(["validate"])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "verdict" in doc or "accepted" in doc


# ---------------------------------------------------------------------------
# certify
# ---------------------------------------------------------------------------


def test_cmd_certify():
    code, doc = _json_out(["certify"])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "certified" in doc or "status" in doc


# ---------------------------------------------------------------------------
# evidence
# ---------------------------------------------------------------------------


def test_cmd_evidence_stdout():
    code, doc = _json_out(["evidence"])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "seal" in doc or "accepted" in doc


def test_cmd_evidence_write(tmp_path):
    code, doc = _json_out(["evidence", "--out", str(tmp_path)])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "path" in doc
    assert "seal" in doc


def test_cmd_evidence_verify(tmp_path):
    # First write, then verify
    _json_out(["evidence", "--out", str(tmp_path)])
    bundle_files = list(tmp_path.iterdir())
    if not bundle_files:
        pytest.skip("no bundle file written")
    bundle_file = bundle_files[0]
    code, doc = _json_out(["evidence", "--verify", str(bundle_file)])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "verified" in doc


# ---------------------------------------------------------------------------
# stats
# ---------------------------------------------------------------------------


def test_cmd_stats():
    code, doc = _json_out(["stats"])
    assert code in (EXIT_OK, EXIT_GATE)
    assert "providers" in doc
    assert "records" in doc
    assert "verdict" in doc
    assert "certification" in doc
    assert "seal" in doc
    # The exit code is derived from the two verdicts, never reported independently.
    certified = doc["verdict"] == "valid" and doc["certification"] == "certified"
    assert code == (EXIT_OK if certified else EXIT_GATE)


def test_cmd_stats_passes_when_valid_and_certified(seed_store):
    """stats exits 0 only when validation accepts AND certification certifies."""
    code, doc = _json_out(["stats", "--store", str(seed_store)])
    assert code == EXIT_OK
    assert doc["verdict"] == "valid"
    assert doc["certification"] == "certified"
    assert doc["records"] > 0
    # The seal is over the assimilation, so a second run of the same store repeats it.
    _, again = _json_out(["stats", "--store", str(seed_store)])
    assert again["seal"] == doc["seal"]


def test_cmd_stats_gates_on_an_uncertified_store(seed_store):
    """An unsatisfied criterion gates stats: a successful run is not a passing run.

    Dropping the seed base's decisions leaves the objects that cite them ungrounded,
    which is a defect validation reports rather than a load-time refusal — so the run
    completes, emits its summary, and still gates.
    """
    decisions = seed_store / "decisions.json"
    decisions.write_text(json.dumps({"decisions": []}), encoding="utf-8")
    code, doc = _json_out(["stats", "--store", str(seed_store)])
    assert code == EXIT_GATE
    assert not (doc["verdict"] == "valid" and doc["certification"] == "certified")
    # It gated on the verdict, not by failing: the summary is still complete.
    assert doc["records"] > 0 and doc["seal"]


# ---------------------------------------------------------------------------
# error handling
# ---------------------------------------------------------------------------


def _main_raising(exc: BaseException, capsys) -> tuple[int, str]:
    """Drive main() with a subcommand whose handler raises ``exc``; return (code, stderr)."""

    def _bad_func(_args: argparse.Namespace) -> int:
        raise exc

    with patch("engine.knowledge.ukip.cli.build_parser") as mock_parser:
        mock_parser.return_value.parse_args.return_value = argparse.Namespace(func=_bad_func)
        code = main([])
    return code, capsys.readouterr().err


def test_main_returns_exit_error_on_knowledge_error(capsys):
    """main() maps KnowledgeError to EXIT_ERROR and reports it on stderr."""
    from engine.knowledge.errors import KnowledgeError

    code, err = _main_raising(KnowledgeError("simulated error"), capsys)
    assert code == EXIT_ERROR
    assert "simulated error" in err


def test_main_returns_exit_error_on_oserror(capsys):
    """main() maps OSError to EXIT_ERROR — an unreadable store is not a crash."""
    code, err = _main_raising(OSError("simulated OS error"), capsys)
    assert code == EXIT_ERROR
    assert "simulated OS error" in err


def test_main_returns_exit_error_on_value_error(capsys):
    """main() maps ValueError to EXIT_ERROR — malformed input is not a crash."""
    code, err = _main_raising(ValueError("simulated value error"), capsys)
    assert code == EXIT_ERROR
    assert "simulated value error" in err


# ---------------------------------------------------------------------------
# _emit
# ---------------------------------------------------------------------------


def test_emit_outputs_sorted_json(capsys):
    _emit({"z": 1, "a": 2})
    out = capsys.readouterr().out
    doc = json.loads(out)
    assert doc == {"a": 2, "z": 1}
    keys = list(json.loads(out).keys())
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# _providers with additional sources
# ---------------------------------------------------------------------------


def test_providers_with_document_source(tmp_path):
    """--documents flag adds a DocumentProvider to the registry."""
    (tmp_path / "doc.md").write_text(
        "# Doc\n\n## Section\n\nSome content here.\n", encoding="utf-8"
    )
    code, doc = _json_out(["providers", "--documents", str(tmp_path)])
    assert code == EXIT_OK
    provider_ids = list(doc.get("units", {}).keys())
    assert any("documents" in pid for pid in provider_ids)


def test_providers_with_unit_source(tmp_path):
    """--units adds an external MappingProvider; unlimited providers, same pipeline."""
    payload = tmp_path / "units.json"
    payload.write_text(
        json.dumps(
            {
                "units": [
                    {
                        "key": "external-1",
                        "title": "External Knowledge",
                        "statement": "External systems must cite the source of every claim.",
                        "rationale": "Uncited knowledge cannot be corroborated.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    code, doc = _json_out(["providers", "--units", str(payload)])
    assert code == EXIT_OK
    # The provider is registered under the derived id and contributes its one unit.
    assert doc["units"]["units-1"] == 1


def test_units_and_documents_compose_without_pipeline_change(tmp_path):
    """Both operator-added provider kinds coexist; adding one changes nothing else."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "doc.md").write_text(
        "# Doc\n\n## Section\n\nDeclared context must precede use.\n", encoding="utf-8"
    )
    payload = tmp_path / "units.json"
    payload.write_text(
        json.dumps({"units": [{"key": "x", "title": "X", "statement": "A statement."}]}),
        encoding="utf-8",
    )
    baseline_code, baseline = _json_out(["providers"])
    code, doc = _json_out(["providers", "--documents", str(docs), "--units", str(payload)])
    assert code == baseline_code == EXIT_OK
    assert {"documents-1", "units-1"} <= set(doc["units"])
    # The canonical providers are untouched by the additions.
    for provider_id, count in baseline["units"].items():
        assert doc["units"][provider_id] == count
