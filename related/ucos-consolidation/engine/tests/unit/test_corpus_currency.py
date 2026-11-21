"""UKAP-001 / WP-001 / D-1 — corpus currency validation suite.

Proves the repository capability, not a description of it:

  * newest export selected            — from export CONTENT, never from a filename
  * stale export rejected             — fail-closed when a newer export exists but is ignored
  * deterministic behaviour           — identical inputs produce byte-identical measurements
  * reproducible execution            — the recorded determination is re-derivable
  * traceability preserved            — every export carries its own content identity
  * dependency closure preserved      — assimilation targets depend on the currency gate
  * Repository Truth preserved        — consumption is measured from committed artifacts only
  * Knowledge Once preserved          — one corpus discovered twice is ONE export

Every scenario is hermetic: synthetic exports are built under ``tmp_path`` so the suite never
depends on an external corpus tree being present.
"""

from __future__ import annotations

import importlib.util
import json
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
ENGINE_PATH = REPO / "00-MASTER" / "UKAP-001" / "corpus_engine.py"


def _load_engine():
    spec = importlib.util.spec_from_file_location("ukap_corpus_engine", ENGINE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ce = _load_engine()


# --------------------------------------------------------------------------- fixtures
def conversation(cid: str, update_time: float) -> dict:
    """A minimally-shaped ChatGPT conversation record."""
    return {
        "conversation_id": cid,
        "title": f"conversation {cid}",
        "create_time": update_time - 100.0,
        "update_time": update_time,
        "mapping": {"root": {"id": "root", "message": None, "parent": None, "children": []}},
    }


def write_export(
    root: Path, name: str, ids: list[str], newest: float, member: str = "payload.json"
) -> Path:
    """A synthetic export DIRECTORY. The member name is arbitrary on purpose."""
    export = root / name
    export.mkdir(parents=True)
    (export / member).write_text(
        json.dumps([conversation(cid, newest - idx) for idx, cid in enumerate(ids)]),
        encoding="utf-8",
    )
    return export


def write_zip_export(root: Path, name: str, ids: list[str], newest: float) -> Path:
    archive = root / name
    archive.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps([conversation(cid, newest - idx) for idx, cid in enumerate(ids)])
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("payload.json", payload)
    return archive


def measured(root: Path) -> list[dict]:
    """Discover + measure + dedupe + order, exactly as a live build does."""
    located = ce.discover_archive_locations([root])
    exports = ce.dedupe_by_identity([ce.measure_archive(loc) for loc in located])
    return ce.order_exports(exports, ce.archive_recency_key)


def model_for(
    archives: list[dict],
    cited: list[str],
    documents: list[dict] | None = None,
    consumed_documents: list[dict] | None = None,
) -> dict:
    model = {
        "archives": archives,
        "documents": documents or [],
        "consumed_conversations": {
            "available": True,
            "ids": sorted(cited),
            "objects": len(cited),
            "source": "00-MASTER/UAKOS-CLOSURE-008/assimilation.json",
            "error": None,
        },
        "consumed_documents": {
            "available": True,
            "documents": consumed_documents if consumed_documents is not None else [],
            "source": "00-MASTER/UAKOS-PHASE-001B/provenance.json",
            "error": None,
        },
        "corpus_roots": [],
    }
    model["gates"] = ce.run_gates(model, replayed=False)
    return model


def gate_of(model: dict, gid: str) -> dict:
    return next(g for g in model["gates"] if g["id"] == gid)


def determination(model: dict) -> str:
    blocking = [g for g in model["gates"] if g["blocking"] and g["result"] == "FAIL"]
    return "CORPUS STALE" if blocking else "CORPUS CURRENT"


def document(path: str, sha: str, commit_time: int, position: int) -> dict:
    return {
        "corpus_class": ce.CLASS_DOCUMENT,
        "export_id": path,
        "path": path,
        "content_sha256": sha,
        "bytes": 1024,
        "tracked": True,
        "commit": sha[:7],
        "commit_time": commit_time,
        "history_position": position,
        "recency_basis": "git commit order",
        "identifiable": True,
    }


# ------------------------------------------------------------------ structural discovery
def test_export_is_recognised_by_payload_structure_not_by_filename(tmp_path: Path):
    write_export(tmp_path, "an-arbitrarily-named-folder", ["c1"], 100.0, member="zzz.json")
    exports = measured(tmp_path)
    assert len(exports) == 1
    assert exports[0]["conversations"] == 1
    assert exports[0]["members"][0]["member"] == "zzz.json"


def test_non_conversation_json_is_not_an_export(tmp_path: Path):
    decoy = tmp_path / "decoy"
    decoy.mkdir()
    (decoy / "conversations-000.json").write_text(
        json.dumps({"objects": 3, "knowledge": []}), encoding="utf-8"
    )
    (decoy / "also.json").write_text(json.dumps([{"id": "x", "title": "y"}]), encoding="utf-8")
    assert measured(tmp_path) == []


def test_payload_signature_requires_an_array_of_conversation_objects():
    assert ce.looks_like_conversation_payload(b'[{"conversation_id":"a","mapping":{}}]')
    assert not ce.looks_like_conversation_payload(b'{"conversation_id":"a","mapping":{}}')
    assert not ce.looks_like_conversation_payload(b'[{"id":"a","title":"no mapping"}]')


def test_zip_form_export_cannot_hide_from_discovery(tmp_path: Path):
    write_zip_export(tmp_path, "sealed.zip", ["c1", "c2"], 500.0)
    exports = measured(tmp_path)
    assert len(exports) == 1
    assert exports[0]["locations"][0]["form"] == "ZIP"
    assert exports[0]["conversations"] == 2


def test_engine_never_descends_into_a_recognised_export(tmp_path: Path):
    outer = write_export(tmp_path, "outer", ["c1"], 100.0)
    write_export(outer, "nested", ["c2"], 900.0)
    exports = measured(tmp_path)
    assert len(exports) == 1
    assert exports[0]["conversation_ids"] == ["c1"]


# --------------------------------------------------------------- newest-export detection
def test_newest_export_selected_from_content_not_from_the_name(tmp_path: Path):
    # The alphabetically LAST name carries the OLDEST content: a name-based selection would
    # pick the wrong export, so this asserts the selection is content-derived.
    write_export(tmp_path, "zzz-looks-newest", ["old-1", "old-2"], 1000.0)
    write_export(tmp_path, "aaa-looks-oldest", ["old-1", "old-2", "new-1"], 9000.0)
    exports = measured(tmp_path)
    canonical = [e for e in exports if e["canonical"]]
    assert len(canonical) == 1
    assert canonical[0]["newest_recorded_time"] == 9000.0
    assert "new-1" in canonical[0]["conversation_ids"]
    assert [e["recency_rank"] for e in exports] == [0, 1]


def test_filesystem_mtime_is_never_consulted(tmp_path: Path):
    older_content = write_export(tmp_path, "older-content", ["c1"], 10.0)
    write_export(tmp_path, "newer-content", ["c1", "c2"], 99999.0)
    # Make the OLD-content export the most recently touched file on disk.
    for path in sorted(older_content.iterdir()):
        path.touch()
    older_content.touch()
    canonical = next(e for e in measured(tmp_path) if e["canonical"])
    assert canonical["conversations"] == 2


def test_recency_order_is_a_strict_total_order(tmp_path: Path):
    write_export(tmp_path, "a", ["c1"], 5.0)
    write_export(tmp_path, "b", ["c1", "c2"], 5.0)
    exports = measured(tmp_path)
    keys = [ce.archive_recency_key(e) for e in exports]
    assert len(set(keys)) == len(keys)
    assert gate_of(model_for(exports, ["c1"]), "CC-03")["result"] == "PASS"


def test_document_recency_uses_commit_order_and_breaks_ties_deterministically():
    older = document("04-REFERENCE/a.docx", "a" * 64, 100, 9)
    newer = document("04-REFERENCE/b.docx", "b" * 64, 200, 20)
    ordered = ce.order_exports([newer, older], ce.document_recency_key)
    assert [d["path"] for d in ordered] == ["04-REFERENCE/a.docx", "04-REFERENCE/b.docx"]
    assert ordered[-1]["canonical"] is True
    same_time_later_in_history = document("04-REFERENCE/c.docx", "c" * 64, 200, 21)
    ordered = ce.order_exports([newer, same_time_later_in_history], ce.document_recency_key)
    assert ordered[-1]["path"] == "04-REFERENCE/c.docx"


def test_document_recency_is_stable_when_a_commit_is_appended():
    """History position is counted from the ROOT, so appending a commit must not reorder or
    change any recorded recency evidence — otherwise every register drifts on every commit."""
    source = ENGINE_PATH.read_text(encoding="utf-8")
    assert '"rev-list", "--reverse", "HEAD"' in source
    assert "head_distance" not in source
    record = json.loads((ENGINE_PATH.parent / "corpus.json").read_text(encoding="utf-8"))
    for doc in record["documents"]:
        assert isinstance(doc["history_position"], int)


# --------------------------------------------------------------------- Knowledge Once
def test_one_corpus_discovered_twice_is_one_export(tmp_path: Path):
    ids = ["c1", "c2", "c3"]
    payload = json.dumps([conversation(cid, 700.0 - idx) for idx, cid in enumerate(ids)])
    unpacked = tmp_path / "unpacked"
    unpacked.mkdir()
    (unpacked / "payload.json").write_text(payload, encoding="utf-8")
    with zipfile.ZipFile(tmp_path / "packed.zip", "w") as zf:
        # A different member NAME with identical CONTENT must still resolve to one export.
        zf.writestr("conversations-000.json", payload)
    exports = measured(tmp_path)
    assert len(exports) == 1
    assert len(exports[0]["locations"]) == 2
    assert {loc["form"] for loc in exports[0]["locations"]} == {"DIRECTORY", "ZIP"}


def test_export_identity_is_the_payload_content_digest(tmp_path: Path):
    write_export(tmp_path / "one", "e", ["c1"], 42.0)
    write_export(tmp_path / "two", "totally-different-name", ["c1"], 42.0)
    first = measured(tmp_path / "one")[0]
    second = measured(tmp_path / "two")[0]
    assert first["payload_digest"] == second["payload_digest"]


# ---------------------------------------------------------------- stale corpus rejection
def test_stale_corpus_is_rejected_when_a_newer_export_is_ignored(tmp_path: Path):
    write_export(tmp_path, "older", ["shared-1", "shared-2"], 100.0)
    write_export(tmp_path, "newer", ["shared-1", "shared-2", "exclusive-1"], 900.0)
    exports = measured(tmp_path)
    stale = model_for(exports, cited=["shared-1", "shared-2"])
    assert gate_of(stale, "CC-05")["result"] == "FAIL"
    assert gate_of(stale, "CC-05")["blocking"] is True
    assert determination(stale) == "CORPUS STALE"
    current = model_for(exports, cited=["shared-1", "exclusive-1"])
    assert gate_of(current, "CC-05")["result"] == "PASS"
    assert determination(current) == "CORPUS CURRENT"


def test_assimilated_conversation_absent_from_the_canonical_export_is_rejected(tmp_path: Path):
    write_export(tmp_path, "only", ["c1", "c2"], 100.0)
    exports = measured(tmp_path)
    rolled_back = model_for(exports, cited=["c1", "vanished"])
    assert gate_of(rolled_back, "CC-04")["result"] == "FAIL"
    assert determination(rolled_back) == "CORPUS STALE"


def test_unmeasurable_consumption_fails_closed(tmp_path: Path):
    write_export(tmp_path, "only", ["c1"], 100.0)
    model = {
        "archives": measured(tmp_path),
        "documents": [],
        "consumed_conversations": {
            "available": False,
            "ids": [],
            "objects": 0,
            "source": "x",
            "error": "assimilation.json absent",
        },
        "consumed_documents": {
            "available": False,
            "documents": [],
            "source": "y",
            "error": "provenance.json absent",
        },
        "corpus_roots": [],
    }
    model["gates"] = ce.run_gates(model, replayed=False)
    assert gate_of(model, "CC-04")["result"] == "FAIL"
    assert gate_of(model, "CC-06")["result"] == "FAIL"
    assert determination(model) == "CORPUS STALE"


def test_unidentifiable_export_is_rejected(tmp_path: Path):
    write_export(tmp_path, "broken", ["c1"], 10.0, member="payload.json")
    (tmp_path / "broken" / "payload.json").write_text(
        '[{"conversation_id":"c1","mapping":{} truncated', encoding="utf-8"
    )
    exports = measured(tmp_path)
    assert exports and exports[0]["identifiable"] is False
    model = model_for(exports, cited=[])
    assert gate_of(model, "CC-02")["result"] == "FAIL"


def test_ignored_in_repo_export_is_rejected():
    docs = ce.order_exports(
        [
            document("04-REFERENCE/chat.docx", "a" * 64, 100, 9),
            document("04-REFERENCE/chat-later.docx", "b" * 64, 200, 2),
        ],
        ce.document_recency_key,
    )
    consumed = [{"path": "04-REFERENCE/chat.docx", "content_sha256": "a" * 64}]
    model = model_for([], cited=[], documents=docs, consumed_documents=consumed)
    cc06 = gate_of(model, "CC-06")
    assert cc06["result"] == "FAIL"
    assert "chat-later.docx" in cc06["detail"][0]
    assert determination(model) == "CORPUS STALE"


def test_in_repo_export_content_drift_is_rejected():
    docs = ce.order_exports(
        [document("04-REFERENCE/chat.docx", "b" * 64, 100, 3)], ce.document_recency_key
    )
    consumed = [{"path": "04-REFERENCE/chat.docx", "content_sha256": "a" * 64}]
    model = model_for([], cited=[], documents=docs, consumed_documents=consumed)
    assert gate_of(model, "CC-07")["result"] == "FAIL"
    assert determination(model) == "CORPUS STALE"


def test_untracked_in_repo_export_is_not_repository_truth():
    doc = document("04-REFERENCE/chat.docx", "a" * 64, 100, 3)
    doc["tracked"] = False
    doc["identifiable"] = False
    docs = ce.order_exports([doc], ce.document_recency_key)
    consumed = [{"path": "04-REFERENCE/chat.docx", "content_sha256": "a" * 64}]
    model = model_for([], cited=[], documents=docs, consumed_documents=consumed)
    assert gate_of(model, "CC-02")["result"] == "FAIL"


def test_uncited_canonical_conversations_are_reported_not_blocking(tmp_path: Path):
    write_export(tmp_path, "only", ["c1", "c2", "c3"], 100.0)
    model = model_for(measured(tmp_path), cited=["c1"])
    cc08 = gate_of(model, "CC-08")
    assert cc08["blocking"] is False
    assert cc08["result"] == "REPORTED"
    assert determination(model) == "CORPUS CURRENT"


# --------------------------------------------------------- determinism & reproducibility
def test_measurement_is_deterministic(tmp_path: Path):
    write_export(tmp_path, "one", ["c2", "c1"], 500.0)
    write_zip_export(tmp_path, "two.zip", ["c9"], 900.0)
    first = measured(tmp_path)
    second = measured(tmp_path)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first[0]["conversation_ids"] == sorted(first[0]["conversation_ids"])


def test_serialization_is_deterministic_and_newline_terminated(tmp_path: Path):
    model = model_for(measured(write_export(tmp_path, "e", ["c1"], 1.0).parent), cited=["c1"])
    raw = ce.serialize(model)
    assert raw.endswith("\n")
    assert not raw.endswith("\n\n")
    assert raw == ce.serialize(model)
    assert json.loads(raw)["archives"][0]["conversations"] == 1


def test_no_wall_clock_is_emitted():
    source = ENGINE_PATH.read_text(encoding="utf-8")
    for forbidden in ("datetime", "time.time", "strftime"):
        assert forbidden not in source, f"{forbidden} would make regeneration irreproducible"


def test_build_fails_closed_when_no_corpus_root_resolves(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("UKAP_CORPUS_ROOTS", str(tmp_path / "absent"))
    with pytest.raises(SystemExit) as exc:
        ce.build(None)
    assert "FAIL-CLOSED" in str(exc.value)


def test_replay_preserves_the_recorded_head_commit(tmp_path: Path, monkeypatch):
    """A committed artifact cannot carry the sha of the commit that carries it, so a replay
    must reproduce the RECORDED head — otherwise the register drift gate breaks on every
    commit."""
    write_export(tmp_path, "only", ["a"], 5.0)
    monkeypatch.setenv("UKAP_CORPUS_ROOTS", str(tmp_path))
    live = ce.build(None)
    record = json.loads(ce.serialize(live))
    record["head_commit"] = "deadbee"
    assert ce.build(record)["head_commit"] == "deadbee"


def test_replay_is_re_derivable_without_a_corpus(tmp_path: Path, monkeypatch):
    write_export(tmp_path, "older", ["a", "b"], 10.0)
    write_export(tmp_path, "newer", ["a", "b", "c"], 20.0)
    monkeypatch.setenv("UKAP_CORPUS_ROOTS", str(tmp_path))
    live = ce.build(None)
    monkeypatch.setenv("UKAP_CORPUS_ROOTS", str(tmp_path / "absent"))
    replayed = ce.build(json.loads(ce.serialize(live)))
    assert replayed["canonical_archive"] == live["canonical_archive"]
    assert replayed["seal_sha256"] == live["seal_sha256"]
    assert replayed["determination"] == live["determination"]


# ----------------------------------------------------- the repository's own currency state
def test_committed_corpus_record_is_current_and_complete():
    record = json.loads((ENGINE_PATH.parent / "corpus.json").read_text(encoding="utf-8"))
    assert record["determination"] == "CORPUS CURRENT"
    assert record["canonical_archive"]
    assert record["canonical_document"]
    for gate in record["gates"]:
        if gate["blocking"]:
            assert gate["result"] == "PASS", f"{gate['id']} {gate['gate']} is {gate['result']}"


def test_every_in_repo_conversation_export_is_assimilated():
    """The concrete D-1 defect: an in-repository ChatGPT export that no baseline consumed."""
    record = json.loads((ENGINE_PATH.parent / "corpus.json").read_text(encoding="utf-8"))
    discovered = {d["path"] for d in record["documents"]}
    consumed = {d["path"] for d in record["consumed_documents"]["documents"]}
    assert discovered, "no in-repository conversation export discovered"
    assert discovered <= consumed, f"ignored export(s): {sorted(discovered - consumed)}"


def test_consumption_evidence_is_a_tracked_artifact():
    """A gate that reads gitignored operational memory is unenforceable in a fresh clone."""
    source = ENGINE_PATH.read_text(encoding="utf-8")
    assert "PROVENANCE_REGISTER" in source
    assert '"UAKOS-PHASE-001B" / "provenance.json"' not in source
    record = json.loads((ENGINE_PATH.parent / "corpus.json").read_text(encoding="utf-8"))
    ignored = (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()
    for evidence in (
        record["consumed_documents"]["source"],
        record["consumed_conversations"]["source"],
    ):
        assert (REPO / evidence).exists(), f"{evidence} does not exist"
        assert evidence not in ignored, f"{evidence} is gitignored — absent in a fresh clone"


def test_assimilation_targets_depend_on_the_currency_gate():
    """Dependency closure: no assimilation artifact may be produced from an unverified corpus."""
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    for target in ("assimilate", "assimilate-replay", "assimilate-gate"):
        assert f"\n{target}: corpus-gate\n" in makefile, f"{target} bypasses corpus-gate"
    assert "\ncorpus-gate:\n" in makefile


# ------------------------------------------------- RC-0014: no machine paths in governed output


def test_governed_artifacts_carry_no_machine_path():
    """A governed artifact must not name one machine's filesystem.

    Five capabilities already refuse a `/Users/` fragment in their reports (uci, ucon, uec, urke
    and mutation gates). UKAP-001 and UAKOS-CLOSURE-008 had no such assertion and were the two
    that leaked: 29 occurrences across four COMMITTED artifacts, every one pointing at
    `/Users/<somebody>/Desktop/KNOWLEDGE-ASSIMILATION`. `corpus.json` additionally stored an
    ABSOLUTE path under a key named `relative`.

    The archives are ~4 GB and cannot be vendored, so the remedy is not relocation: the export is
    identified by its payload digest, which is machine-independent and is what CC-04/CC-05 verify
    against. This test is the control that keeps it that way.
    """
    repo = Path(__file__).resolve().parents[3]
    governed = [
        repo / "00-MASTER" / "UKAP-001" / "corpus.json",
        repo / "00-MASTER" / "UKAP-001" / "EVIDENCE-MANIFEST.json",
        repo / "00-MASTER" / "UAKOS-CLOSURE-008" / "assimilation.json",
        repo / "00-MASTER" / "UAKOS-CLOSURE-008" / "EVIDENCE-MANIFEST.json",
    ]
    present = [p for p in governed if p.exists()]
    assert present, "no governed artifact found — a vacuous pass would prove nothing"
    for path in present:
        body = path.read_text(encoding="utf-8")
        for fragment in ("/Users/", "/home/", "/private/var/"):
            assert fragment not in body, (
                f"{path.relative_to(repo)} names a machine path ({fragment}); a governed "
                f"artifact must identify evidence by digest, not by where one machine kept it"
            )


def test_no_absolute_path_hides_under_a_relative_key():
    """`relative` must mean relative. It held an absolute export location for twelve records."""
    repo = Path(__file__).resolve().parents[3]
    manifest = repo / "00-MASTER" / "UKAP-001" / "EVIDENCE-MANIFEST.json"
    if not manifest.exists():
        pytest.skip("UKAP-001 evidence manifest not generated in this checkout")
    files = json.loads(manifest.read_text(encoding="utf-8")).get("files", {})
    assert files, "manifest carries no files — refusing a vacuous pass"
    for key, record in files.items():
        value = record.get("relative", "")
        assert not value.startswith("/"), f"{key}: `relative` holds the absolute path {value!r}"
