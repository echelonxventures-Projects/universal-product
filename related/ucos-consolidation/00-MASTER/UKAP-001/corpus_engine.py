#!/usr/bin/env python3
"""UKAP-001 / WP-001 / D-1 — deterministic CORPUS CURRENCY engine.

MISSION (D-1, CORPUS CURRENCY RESTORATION)
    Guarantee that every downstream assimilation artifact is derived from the NEWEST
    available ChatGPT export, and fail closed the moment a newer export exists but is
    ignored. This engine discovers exports, identifies the newest, resolves the canonical
    assimilation input, measures what the repository's committed baselines actually
    consumed, and refuses to certify a stale corpus.

    It adds NO new authority, NO new discovery pipeline and NO new knowledge. It measures
    corpus currency and reports. AUTHORITY = NONE (DERIVED TRUTH). Fail-closed (TRACK-001).

TWO CORPUS CLASSES (both are "ChatGPT exports"; both are governed here)
    EXPORT-ARCHIVE   a ChatGPT data-export tree (directory or .zip) discovered under the
                     corpus roots. Consumed by KNOWLEDGE-ASSIMILATION PHASE-001/002, whose
                     output is the frozen evidence that UAKOS-CLOSURE-008 assimilates.
    EXPORT-DOCUMENT  an in-repository ChatGPT conversation export (.docx) under the frozen
                     source roots. Consumed by UAKOS-PHASE-001B provenance reconstruction.

NO ASSUMPTIONS (constitutional constraints of this work package)
    * no hardcoded export versions        — nothing in this file names an export
    * no filename assumptions             — an EXPORT-ARCHIVE is recognised by the STRUCTURE
                                            of its payload (a JSON array of conversation
                                            objects carrying `mapping` + a conversation id),
                                            never by its name; an EXPORT-DOCUMENT is
                                            classified by the EXISTING PHASE-001B
                                            classifier, imported, not copied
    * no filesystem-timestamp assumptions — EXPORT-ARCHIVE recency is derived from the
                                            export's OWN recorded conversation times
                                            (content), EXPORT-DOCUMENT recency from git
                                            commit order (Repository Truth). Filesystem
                                            mtime is never read: it does not survive a clone

CANONICAL INPUT RESOLUTION
    Per class, exports are placed in a strict total order by a content/Repository-Truth
    recency key; the maximum is the CANONICAL export. Identity is content-derived, so the
    same export discovered twice (e.g. a .zip and its extracted tree, or via a symlink) is
    ONE export with several locations — never two rival corpora.

Authoritative inputs
    EXTERNAL (read-only; never written)
        $UKAP_CORPUS_ROOTS (os.pathsep-separated) else $UAKOS_EVIDENCE_ROOT else
        ~/Desktop/KNOWLEDGE-ASSIMILATION — the corpus roots scanned for EXPORT-ARCHIVEs.
    IN-REPO (Repository Truth — the sole consumption authority)
        00-MASTER/UAKOS-CLOSURE-008/assimilation.json  conversation evidence actually
            assimilated (column `evidence_conversation`) → what the archive corpus delivered
        00-MASTER/UAKOS-PHASE-001B/01-SOURCE-PROVENANCE-REGISTER.md  CONVERSATION documents
            actually reconstructed → what the document corpus delivered (a TRACKED register:
            the `provenance.json` machine model is gitignored and absent in a fresh clone)
        the repository itself, via `git ls-files` + `git log`

Outputs (regenerated deterministically, no timestamps)
    corpus.json              full export inventory, recency order, canonical resolution,
                             consumption measurement, gates, determination + seal
    EVIDENCE-MANIFEST.json   sha256 of every input consumed
    01..08-*.md              the eight registers

Usage
    python3 00-MASTER/UKAP-001/corpus_engine.py            # discover + resolve + render
    python3 00-MASTER/UKAP-001/corpus_engine.py --gate     # exit 1 unless CORPUS CURRENT
    python3 00-MASTER/UKAP-001/corpus_engine.py --render    # replay from corpus.json

`--render` replays the EXPORT-ARCHIVE inventory from corpus.json (self-containment: no
corpus root required, byte-identical replay) while the EXPORT-DOCUMENT class and BOTH
consumption measurements are always re-measured live, because they are pure functions of
the repository. A gate run therefore can never be vacuous: adding an in-repo export, or
rolling a baseline back onto an older corpus, fails the gate with no external tree present.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PROGRAM = "UKAP-001"
DETERMINATION_ID = "D-1"
CORPUS_JSON = HERE / "corpus.json"
EVIDENCE_MANIFEST = HERE / "EVIDENCE-MANIFEST.json"

# Repository-Truth consumption evidence. BOTH sources must be TRACKED artifacts: the
# machine models `provenance.json` / `closure.json` are gitignored operational memory and are
# absent in a fresh clone, so relying on them would make the gate environment-dependent and
# would render it unenforceable in CI. The committed registers are the Repository Truth.
ASSIM_JSON = REPO / "00-MASTER" / "UAKOS-CLOSURE-008" / "assimilation.json"
PROVENANCE_REGISTER = (REPO / "00-MASTER" / "UAKOS-PHASE-001B"
                       / "01-SOURCE-PROVENANCE-REGISTER.md")
PROVENANCE_ENGINE = REPO / "00-MASTER" / "UAKOS-PHASE-001B" / "provenance_engine.py"

# The frozen source roots PHASE-001B reconstructs from; the in-repo conversation exports
# live here. Kept identical to provenance_engine.reconstruct() so the two can never diverge.
DOC_ROOTS = ("00-SOURCE", "04-REFERENCE")

DEFAULT_CORPUS_ROOT = Path.home() / "Desktop" / "KNOWLEDGE-ASSIMILATION"

# Bounded structural scan: an export tree is recognised the moment a directory carries a
# conversation payload; the engine never descends into a recognised export.
MAX_SCAN_DEPTH = 3
SNIFF_BYTES = 1 << 16

CLASS_ARCHIVE = "EXPORT-ARCHIVE"
CLASS_DOCUMENT = "EXPORT-DOCUMENT"


# --------------------------------------------------------------------------- helpers
def sha256_stream(fh) -> str:
    h = hashlib.sha256()
    for chunk in iter(lambda: fh.read(1 << 20), b""):
        h.update(chunk)
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    with path.open("rb") as fh:
        return sha256_stream(fh)


def git(*args: str) -> str:
    # fixed argv, no shell, no user input — the two bandit findings are accepted here.
    out = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=REPO, capture_output=True, text=True, check=False)
    return out.stdout if out.returncode == 0 else ""


def head_commit() -> str:
    return (git("rev-parse", "--short", "HEAD") or "unknown").strip()


def corpus_roots() -> list[Path]:
    """Corpus roots, in declared order. Reuses the EXISTING evidence-root contract
    ($UAKOS_EVIDENCE_ROOT) so no new configuration surface is invented; $UKAP_CORPUS_ROOTS
    overrides it when the corpus lives apart from the evidence tree."""
    raw = os.environ.get("UKAP_CORPUS_ROOTS")
    if raw:
        parts = [p for p in raw.split(os.pathsep) if p.strip()]
    else:
        parts = [os.environ.get("UAKOS_EVIDENCE_ROOT", str(DEFAULT_CORPUS_ROOT))]
    seen: set[str] = set()
    roots: list[Path] = []
    for p in parts:
        rp = Path(p).expanduser()
        key = str(rp)
        if key not in seen:
            seen.add(key)
            roots.append(rp)
    return roots


def load_classify_doc():
    """Import the EXISTING PHASE-001B source classifier instead of re-implementing it, so
    'which in-repo document is a ChatGPT conversation export' has exactly ONE definition in
    the repository (no duplicated capability, no drift)."""
    spec = importlib.util.spec_from_file_location("_ukap_provenance_engine", PROVENANCE_ENGINE)
    if spec is None or spec.loader is None:
        raise SystemExit(
            f"{PROGRAM}: FAIL-CLOSED — cannot load the PHASE-001B classifier from "
            f"{PROVENANCE_ENGINE}; the in-repo conversation-export universe is undefined.")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.classify_doc


# ------------------------------------------------------------- EXPORT-ARCHIVE discovery
def looks_like_conversation_payload(prefix: bytes) -> bool:
    """STRUCTURAL recognition of a ChatGPT conversation payload — no filename is consulted.

    A payload is a JSON ARRAY whose leading object carries the conversation node graph
    (`mapping`) and a conversation identifier. This is the shape ChatGPT exports emit and
    the shape the assimilation pipeline consumes.
    """
    text = prefix.decode("utf-8", errors="replace").lstrip()
    if not text.startswith("["):
        return False
    return '"mapping"' in text and ('"conversation_id"' in text or '"id"' in text)


def _dir_payload_members(d: Path) -> list[str]:
    """Names of the conversation payloads directly inside a directory (sorted)."""
    names: list[str] = []
    try:
        entries = sorted(d.iterdir(), key=lambda p: p.name)
    except (OSError, PermissionError):
        return names
    for p in entries:
        if not p.is_file() or p.suffix.lower() != ".json":
            continue
        try:
            with p.open("rb") as fh:
                prefix = fh.read(SNIFF_BYTES)
        except (OSError, PermissionError):
            continue
        if looks_like_conversation_payload(prefix):
            names.append(p.name)
    return names


def _zip_payload_members(z: Path) -> list[str]:
    names: list[str] = []
    try:
        with zipfile.ZipFile(z) as zf:
            for name in sorted(zf.namelist()):
                if name.endswith("/") or not name.lower().endswith(".json"):
                    continue
                try:
                    with zf.open(name) as fh:
                        prefix = fh.read(SNIFF_BYTES)
                except (OSError, KeyError, zipfile.BadZipFile):
                    continue
                if looks_like_conversation_payload(prefix):
                    names.append(name)
    except (OSError, zipfile.BadZipFile):
        return []
    return names


def discover_archive_locations(roots: list[Path]) -> list[dict]:
    """Bounded, deterministic structural scan for export locations under the corpus roots.

    A directory that carries a conversation payload IS an export location and is never
    descended into. A .zip that carries one is an export location too, so an export that
    has not been unpacked can never hide from the currency gate.
    """
    found: list[dict] = []
    visited: set[str] = set()
    for root in roots:
        if not root.is_dir():
            continue
        # BREADTH-FIRST with sorted siblings: an export reached by several paths is reported
        # at its shallowest location, and the traversal order is identical on every machine.
        queue: list[tuple[Path, int]] = [(root, 0)]
        while queue:
            d, depth = queue.pop(0)
            try:
                real = str(d.resolve())
            except OSError:
                continue
            if real in visited:
                continue
            visited.add(real)
            members = _dir_payload_members(d)
            if members:
                found.append({"root": str(root), "location": str(d), "form": "DIRECTORY",
                              "members": members})
                continue  # a recognised export is never descended into
            if depth >= MAX_SCAN_DEPTH:
                continue
            try:
                entries = sorted(d.iterdir(), key=lambda p: p.name)
            except (OSError, PermissionError):
                continue
            for p in entries:
                if p.is_file() and p.suffix.lower() == ".zip":
                    zmembers = _zip_payload_members(p)
                    if zmembers:
                        found.append({"root": str(root), "location": str(p), "form": "ZIP",
                                      "members": zmembers})
                elif p.is_dir():
                    queue.append((p, depth + 1))
    found.sort(key=lambda e: (e["root"], e["location"]))
    return found


def _conversation_facts(payload: object) -> tuple[list[str], float | None]:
    """Conversation ids and the newest time the export ITSELF records, from content."""
    ids: list[str] = []
    newest: float | None = None
    if not isinstance(payload, list):
        return ids, newest
    for conv in payload:
        if not isinstance(conv, dict):
            continue
        cid = conv.get("conversation_id") or conv.get("id")
        if isinstance(cid, str) and cid:
            ids.append(cid)
        for key in ("update_time", "create_time"):
            val = conv.get(key)
            if isinstance(val, (int, float)) and (newest is None or val > newest):
                newest = float(val)
    return ids, newest


def measure_archive(loc: dict) -> dict:
    """Content-derived identity + recency for one export location. Never reads mtime."""
    path = Path(loc["location"])
    digests: list[str] = []
    ids: list[str] = []
    newest: float | None = None
    records = 0
    member_rows: list[dict] = []
    error: str | None = None

    def account(name: str, digest: str, payload: object) -> None:
        nonlocal newest, records
        cids, mx = _conversation_facts(payload)
        ids.extend(cids)
        records += len(cids)
        if mx is not None and (newest is None or mx > newest):
            newest = mx
        digests.append(digest)
        member_rows.append({"member": name, "sha256": digest, "records": len(cids)})

    try:
        if loc["form"] == "DIRECTORY":
            for name in loc["members"]:
                member = path / name
                digest = sha256_file(member)
                with member.open("rb") as fh:
                    payload = json.load(fh)
                account(name, digest, payload)
        else:
            with zipfile.ZipFile(path) as zf:
                for name in loc["members"]:
                    # read each payload ONCE: decompressing a multi-hundred-MB member twice
                    # would double the cost of every build for no gain.
                    with zf.open(name) as fh:
                        blob = fh.read()
                    digest = hashlib.sha256(blob).hexdigest()
                    account(name, digest, json.loads(blob.decode("utf-8", errors="replace")))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        error = f"{type(exc).__name__}: {exc}"

    unique_ids = sorted(set(ids))
    # Identity is the multiset of PAYLOAD CONTENT digests — member names are excluded on
    # purpose, so a .zip and its extracted tree resolve to the SAME export.
    payload_digest = hashlib.sha256(
        "\n".join(sorted(digests)).encode("utf-8")).hexdigest() if digests else ""
    return {
        "corpus_class": CLASS_ARCHIVE,
        "export_id": payload_digest[:16],
        "payload_digest": payload_digest,
        "locations": [{"location": loc["location"], "form": loc["form"], "root": loc["root"]}],
        "members": member_rows,
        "payload_members": len(member_rows),
        "records": records,
        "conversations": len(unique_ids),
        "conversation_ids": unique_ids,
        "newest_recorded_time": newest,
        "recency_basis": "export content — newest conversation time recorded by the export",
        "identifiable": bool(payload_digest) and bool(unique_ids) and error is None,
        "error": error,
    }


def dedupe_by_identity(exports: list[dict]) -> list[dict]:
    """Collapse identical corpora discovered at several locations into ONE export."""
    merged: dict[str, dict] = {}
    for exp in exports:
        key = exp["payload_digest"] or f"UNIDENTIFIABLE::{exp['locations'][0]['location']}"
        if key in merged:
            known = merged[key]
            for loc in exp["locations"]:
                if loc not in known["locations"]:
                    known["locations"].append(loc)
            known["locations"].sort(key=lambda loc: (loc["root"], loc["location"]))
        else:
            merged[key] = exp
    return list(merged.values())


# ------------------------------------------------------------ EXPORT-DOCUMENT discovery
def commit_order() -> dict[str, int]:
    """History position of every commit (0 = root commit), from `git rev-list --reverse`.

    Position is counted FROM THE ROOT, not from HEAD: distance-from-HEAD shifts by one on
    every new commit, which would make the recency evidence — and therefore every rendered
    register — drift on each commit. Counting from the root is stable under append and is
    identical in every clone.
    """
    return {sha: idx for idx, sha in enumerate(git("rev-list", "--reverse", "HEAD").split())
            if sha}


def discover_documents(order: dict[str, int], tracked: set[str]) -> list[dict]:
    classify_doc = load_classify_doc()
    rows: list[dict] = []
    for root in DOC_ROOTS:
        base = REPO / root
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.docx"), key=lambda q: str(q)):
            if p.name.startswith("~$") or not p.is_file():
                continue
            rel = str(p.relative_to(REPO))
            if classify_doc(rel) != "CONVERSATION":
                continue
            sha = git("log", "-1", "--format=%H", "--", rel).strip()
            ctime = git("log", "-1", "--format=%ct", "--", rel).strip()
            rows.append({
                "corpus_class": CLASS_DOCUMENT,
                "export_id": rel,
                "path": rel,
                "content_sha256": sha256_file(p),
                "bytes": p.stat().st_size,
                "tracked": rel in tracked,
                "commit": sha[:7] if sha else "",
                "commit_time": int(ctime) if ctime.isdigit() else None,
                "history_position": order.get(sha) if sha else None,
                "recency_basis": "git commit order — Repository Truth (filesystem mtime is "
                                 "never read: it does not survive a clone)",
                "identifiable": bool(sha) and rel in tracked,
            })
    rows.sort(key=lambda r: r["path"])
    return rows


# --------------------------------------------------------------------------- recency order
def archive_recency_key(exp: dict) -> tuple[float, int, str]:
    return (
        exp["newest_recorded_time"] if exp["newest_recorded_time"] is not None else -1.0,
        exp["conversations"],
        exp["payload_digest"],
    )


def document_recency_key(doc: dict) -> tuple[int, int, str]:
    return (
        doc["commit_time"] if doc["commit_time"] is not None else -1,
        doc["history_position"] if doc["history_position"] is not None else -1,
        doc["content_sha256"],
    )


def order_exports(exports: list[dict], keyfn) -> list[dict]:
    """Strict total order, oldest → newest, with the rank recorded on every export."""
    ranked = sorted(exports, key=keyfn)
    for idx, exp in enumerate(ranked):
        exp["recency_rank"] = idx
        exp["recency_key"] = [str(part) for part in keyfn(exp)]
        exp["canonical"] = idx == len(ranked) - 1
    return ranked


# ------------------------------------------------------------------ consumption evidence
def consumed_conversations() -> dict:
    """Conversation ids the COMMITTED assimilation baseline actually carries evidence from.

    Read from UAKOS-CLOSURE-008/assimilation.json — the repository's own frozen artifact —
    so 'what was consumed' is Repository Truth, never an external claim.
    """
    if not ASSIM_JSON.exists():
        return {"available": False, "ids": [], "objects": 0,
                "source": str(ASSIM_JSON.relative_to(REPO)),
                "error": "assimilation.json absent — the assimilation baseline is unmeasurable"}
    payload = json.loads(ASSIM_JSON.read_text(encoding="utf-8"))
    cols = payload.get("row_columns") or []
    rows = payload.get("rows") or []
    if "evidence_conversation" not in cols:
        return {"available": False, "ids": [], "objects": len(rows),
                "source": str(ASSIM_JSON.relative_to(REPO)),
                "error": "assimilation.json carries no `evidence_conversation` column"}
    idx = cols.index("evidence_conversation")
    ids = {row[idx] for row in rows if len(row) > idx and isinstance(row[idx], str) and row[idx]}
    return {"available": True, "ids": sorted(ids), "objects": len(rows),
            "source": str(ASSIM_JSON.relative_to(REPO)), "error": None}


def consumed_documents() -> dict:
    """CONVERSATION documents the COMMITTED provenance baseline actually reconstructed.

    Read from the TRACKED register `01-SOURCE-PROVENANCE-REGISTER.md` (columns
    `Document | Class | SHA-256 (16) | …`), which is the committed Repository Truth for
    PHASE-001B and is therefore present in every clone. The machine model `provenance.json`
    is deliberately NOT consulted: it is gitignored operational memory, so a gate that
    depended on it would silently weaken to nothing in CI.
    """
    if not PROVENANCE_REGISTER.exists():
        return {"available": False, "documents": [],
                "source": str(PROVENANCE_REGISTER.relative_to(REPO)),
                "error": "01-SOURCE-PROVENANCE-REGISTER.md absent — the provenance baseline "
                         "is unmeasurable"}
    docs: list[dict] = []
    for line in PROVENANCE_REGISTER.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[1] != "CONVERSATION":
            continue
        docs.append({"path": cells[0],
                     "content_sha256": cells[2].rstrip("…").rstrip(".").strip()})
    docs.sort(key=lambda d: d["path"])
    return {"available": True, "documents": docs,
            "source": str(PROVENANCE_REGISTER.relative_to(REPO)), "error": None}


# --------------------------------------------------------------------------- gates
def gate(gid: str, name: str, blocking: bool, detail: list[str], subject: str) -> dict:
    return {"id": gid, "gate": name, "blocking": blocking, "count": len(detail),
            "detail": detail[:12], "detail_total": len(detail), "subject": subject,
            "result": "PASS" if not detail else ("FAIL" if blocking else "REPORTED")}


def run_gates(model: dict, replayed: bool) -> list[dict]:
    archives: list[dict] = model["archives"]
    documents: list[dict] = model["documents"]
    conv = model["consumed_conversations"]
    cdocs = model["consumed_documents"]

    gates: list[dict] = []

    # --- CC-01 corpus root resolution -------------------------------------------------
    if replayed:
        root_detail: list[str] = []
    elif not archives:
        root_detail = [f"no ChatGPT export discovered under: "
                       f"{', '.join(model['corpus_roots']) or '(no root configured)'}"]
    else:
        root_detail = []
    gates.append(gate("CC-01", "Corpus root resolves to at least one discoverable export",
                      True, root_detail, CLASS_ARCHIVE))

    # --- CC-02 every discovered export is identifiable --------------------------------
    unident = [f"{e['locations'][0]['location']} ({e['error'] or 'no conversation payload'})"
               for e in archives if not e["identifiable"]]
    unident += [f"{d['path']} (untracked or no commit — not Repository Truth)"
                for d in documents if not d["identifiable"]]
    gates.append(gate("CC-02", "Every discovered export is identifiable and parseable",
                      True, unident, "BOTH"))

    # --- CC-03 canonical selection is a strict total order ----------------------------
    ties: list[str] = []
    for label, group, keyfn in ((CLASS_ARCHIVE, archives, archive_recency_key),
                                (CLASS_DOCUMENT, documents, document_recency_key)):
        seen: dict[tuple, str] = {}
        for exp in group:
            key = keyfn(exp)
            if key in seen:
                ties.append(f"{label}: {exp['export_id']} ties with {seen[key]}")
            else:
                seen[key] = exp["export_id"]
    gates.append(gate("CC-03", "Newest-export selection is a strict total order (no tie)",
                      True, ties, "BOTH"))

    # --- CC-04 nothing consumed is foreign to the canonical corpus --------------------
    canon = next((e for e in archives if e.get("canonical")), None)
    detail: list[str] = []
    if not conv["available"]:
        detail = [conv["error"] or "consumption unmeasurable"]
    elif canon is None:
        detail = [] if replayed and not archives else ["no canonical EXPORT-ARCHIVE resolved"]
    else:
        canon_ids = set(canon["conversation_ids"])
        foreign = sorted(set(conv["ids"]) - canon_ids)
        detail = [f"{cid} (assimilated evidence absent from the canonical export)"
                  for cid in foreign]
    gates.append(gate("CC-04", "Every assimilated conversation exists in the canonical export",
                      True, detail, CLASS_ARCHIVE))

    # --- CC-05 the newest export is actually assimilated ------------------------------
    detail = []
    if canon is not None and conv["available"]:
        older: set[str] = set()
        for exp in archives:
            if exp["payload_digest"] != canon["payload_digest"]:
                older.update(exp["conversation_ids"])
        exclusive = set(canon["conversation_ids"]) - older
        if exclusive and not (exclusive & set(conv["ids"])):
            detail = [
                f"the canonical export {canon['export_id']} contributes "
                f"{len(exclusive)} conversation(s) that no older export carries, and the "
                f"assimilation baseline cites NONE of them — a newer export exists but is "
                f"ignored (STALE CORPUS)"]
    gates.append(gate("CC-05", "The canonical (newest) export is assimilated, not ignored",
                      True, detail, CLASS_ARCHIVE))

    # --- CC-06 no in-repo export is ignored -------------------------------------------
    detail = []
    if not cdocs["available"]:
        detail = [cdocs["error"] or "consumption unmeasurable"]
    else:
        consumed_paths = {d["path"] for d in cdocs["documents"]}
        for doc in documents:
            if doc["path"] not in consumed_paths:
                detail.append(f"{doc['path']} — discovered in-repo conversation export never "
                              f"reconstructed by the provenance baseline (STALE CORPUS)")
        for path in sorted(consumed_paths - {d["path"] for d in documents}):
            detail.append(f"{path} — recorded as consumed but no longer discoverable")
    gates.append(gate("CC-06", "Every in-repo conversation export is assimilated",
                      True, detail, CLASS_DOCUMENT))

    # --- CC-07 consumed content still matches current content -------------------------
    detail = []
    if cdocs["available"]:
        current = {d["path"]: d["content_sha256"] for d in documents}
        for rec in cdocs["documents"]:
            live = current.get(rec["path"])
            recorded = rec["content_sha256"]
            # The committed register records a 16-hex prefix; compare on the recorded width
            # so a truncated record is still a real integrity check, never a free pass.
            if live is not None and recorded and not live.startswith(recorded):
                detail.append(f"{rec['path']} — content changed since reconstruction "
                              f"({recorded[:12]} → {live[:12]})")
    gates.append(gate("CC-07", "Assimilated in-repo export content has not drifted",
                      True, detail, CLASS_DOCUMENT))

    # --- CC-08 reported: conversations carried by the canonical export but not cited ---
    detail = []
    if canon is not None and conv["available"]:
        uncited = sorted(set(canon["conversation_ids"]) - set(conv["ids"]))
        detail = [f"{len(uncited)} conversation(s) in the canonical export yielded no "
                  f"knowledge object"] if uncited else []
    gates.append(gate("CC-08", "Canonical-export conversations not cited by any object",
                      False, detail, CLASS_ARCHIVE))
    return gates


# --------------------------------------------------------------------------- model build
def build(replay: dict | None) -> dict:
    """Build the currency model.

    `replay` is the previously recorded `corpus.json` payload, or None for a live build.
    In replay mode the EXPORT-ARCHIVE inventory AND the corpus roots it was measured under
    are both taken from the record, so rendering is a pure function of `corpus.json` + the
    repository and is byte-identical on any machine, with or without a corpus present.
    """
    replayed = replay is not None
    if replayed:
        archives = [dict(exp) for exp in replay.get("archives", [])]
        root_names = [str(r) for r in replay.get("corpus_roots", [])]
        resolved = [str(r) for r in replay.get("corpus_roots_resolved", [])]
        # The RECORDED head is replayed, never re-read: a committed artifact can never carry
        # the sha of the commit that carries it, so a replay must preserve the recorded HEAD
        # for the register drift gate to be a fixed point across commits.
        head = str(replay.get("head_commit") or head_commit())
    else:
        head = head_commit()
        roots = corpus_roots()
        root_names = [str(r) for r in roots]
        resolved = [str(r) for r in roots if r.is_dir()]
        located = discover_archive_locations(roots)
        archives = dedupe_by_identity([measure_archive(loc) for loc in located])
        if not archives and not resolved:
            raise SystemExit(
                f"{PROGRAM}: FAIL-CLOSED — no corpus root resolves: "
                f"{', '.join(root_names)}\n"
                f"  set UKAP_CORPUS_ROOTS (or UAKOS_EVIDENCE_ROOT), or run with --render to "
                f"replay the recorded inventory from corpus.json")
    archives = order_exports(archives, archive_recency_key)

    tracked = {line for line in git("ls-files").splitlines() if line}
    documents = order_exports(discover_documents(commit_order(), tracked),
                              document_recency_key)

    model = {
        "program": PROGRAM,
        "determination_id": DETERMINATION_ID,
        "authority": "NONE — DERIVED TRUTH (fail-closed, TRACK-001)",
        "head_commit": head,
        "corpus_roots": root_names,
        "corpus_roots_resolved": resolved,
        "archives": archives,
        "documents": documents,
        "consumed_conversations": consumed_conversations(),
        "consumed_documents": consumed_documents(),
    }
    # The execution MODE is deliberately not part of the model: the determination, the seal
    # and every rendered register must be a pure function of the corpus record plus the
    # repository, so a replay can be diffed byte-for-byte against a live build.
    model["gates"] = run_gates(model, replayed)
    blocking_fail = [g for g in model["gates"] if g["blocking"] and g["result"] == "FAIL"]
    model["determination"] = "CORPUS STALE" if blocking_fail else "CORPUS CURRENT"
    model["canonical_archive"] = next(
        (e["export_id"] for e in archives if e.get("canonical")), "")
    model["canonical_document"] = next(
        (d["export_id"] for d in documents if d.get("canonical")), "")
    model["evidence_manifest"] = evidence_manifest(archives)

    # LOCATIONS BECOME PORTABLE BEFORE THE SEAL IS TAKEN, and the order is the whole point.
    # Discovery needs real paths — `payload_for` opens `loc["location"]` — so the model carries
    # absolute paths right up to here. Sealing them would make the seal a function of WHERE the
    # corpus sat, so `build(serialize(model))` would not reproduce `build(...)`: measured, the
    # replay test saw 9ac4a8ab… against 4c105593…. Sealing the portable form makes the seal a
    # function of the evidence's IDENTITY instead, which is what replay can reproduce and what a
    # second machine holding the same corpus will compute. `_portable` is idempotent, so a replay
    # that is already portable is unchanged by it.
    model = _portable(model)

    seal_src = json.dumps({k: v for k, v in model.items() if k != "seal_sha256"},
                          sort_keys=True, separators=(",", ":"))
    model["seal_sha256"] = hashlib.sha256(seal_src.encode("utf-8")).hexdigest()
    return model


def evidence_manifest(archives: list[dict]) -> dict:
    """sha256 of every input this determination rests on: the in-repo consumption evidence
    plus the content digest of every discovered export payload."""
    manifest: dict[str, dict] = {}
    for key, path in (("assimilation_baseline", ASSIM_JSON),
                      ("provenance_baseline", PROVENANCE_REGISTER)):
        if path.exists():
            manifest[key] = {"relative": str(path.relative_to(REPO)),
                             "bytes": path.stat().st_size, "sha256": sha256_file(path)}
    for exp in archives:
        # EXTERNAL EVIDENCE IS NAMED AS EXTERNAL (RC-0014). This wrote the archive's ABSOLUTE
        # filesystem location under a key called `relative`, so a committed governed artifact
        # asserted `/Users/<somebody>/Desktop/…` as a relative path — false in form and
        # unresolvable on any other machine. The archives are ~4 GB of chat exports and cannot
        # be vendored, so the honest record is: identify them by CONTENT, state plainly that
        # the bytes are external, and keep the digest that lets any holder of the corpus verify
        # they have the same evidence this determination rests on.
        #
        # `relative` is retained and set to the logical, machine-independent identity so every
        # existing reader keeps working; the absolute location moves to `external_location`,
        # which says what it is.
        # The absolute location is deliberately NOT recorded. `export_id` is the payload's own
        # content digest and `sha256` is what CC-04/CC-05 verify against, so the artifact already
        # identifies the evidence completely. A path would only say which machine held it.
        manifest[f"export::{exp['export_id']}"] = {
            "relative": f"external:export/{exp['export_id']}",
            "external": True,
            "bytes": sum(m.get("records", 0) for m in exp["members"]),
            "sha256": exp["payload_digest"]}
    return manifest


# --------------------------------------------------------------------------- serialization
def portable_location(value: str) -> str:
    """A filesystem location as a governed artifact may record it.

    Inside the repository -> repository-relative. Outside -> a CONTENT-SCOPED token naming the
    external root rather than one machine's path to it.

    WHY (RC-0014). The model carries real absolute paths because the engine RE-READS the archives
    while measuring — `payload_for` opens `loc["location"]`. That is correct at runtime and wrong
    on disk: serializing it wrote `/Users/<somebody>/Desktop/KNOWLEDGE-ASSIMILATION/…` into
    `corpus.json`, a committed governed artifact, twelve times. The bytes are ~4 GB of chat
    exports and cannot be vendored, so the remedy is not to relocate them but to stop asserting
    a machine's path as if it were repository truth: the archive is identified by its payload
    digest, which is what CC-04/CC-05 actually verify against, and the digest is machine-
    independent. Sanitizing HERE rather than in the model keeps runtime resolution intact and
    makes the on-disk form portable by construction.
    """
    if not value.startswith("/"):
        return value
    path = Path(value)
    try:
        return str(path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        return f"external:{path.name}" if path.name else "external:"


#: Keys whose STRING value is a filesystem location.
LOCATION_KEYS = ("location", "root", "external_location")
#: Keys whose LIST value is a list of filesystem locations. Named separately because they carry
#: bare strings rather than records, so the recursive walk would otherwise never see them — which
#: is exactly how `corpus_roots` kept leaking after the record-level locations were fixed.
LOCATION_LIST_KEYS = ("corpus_roots", "corpus_roots_resolved")


def _portable(node):
    """Recursively rewrite the location-bearing keys of a model for serialization."""
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if key in LOCATION_KEYS and isinstance(value, str):
                out[key] = portable_location(value)
            elif key in LOCATION_LIST_KEYS and isinstance(value, list):
                out[key] = [
                    portable_location(x) if isinstance(x, str) else _portable(x) for x in value
                ]
            else:
                out[key] = _portable(value)
        return out
    if isinstance(node, list):
        return [_portable(x) for x in node]
    return node


def serialize(model: dict) -> str:
    """Deterministic, diffable JSON: sorted keys, two-space indent, single trailing newline.
    Conversation-id lists are the evidence CC-04/CC-05 replay from, so they are recorded in
    full — the artifact must be sufficient to re-derive the determination with no corpus.

    Locations are made PORTABLE on the way out (see `portable_location`): the artifact records
    what was consumed and its digest, never one machine's path to it.
    """
    return json.dumps(_portable(model), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def deserialize(raw: str) -> dict:
    return json.loads(raw)


# --------------------------------------------------------------------------- rendering
HDR_NOTE = (
    "> PROGRAM {program} · {det} CORPUS CURRENCY RESTORATION · HEAD `{head}` · "
    "AUTHORITY = NONE (DERIVED TRUTH) · generated by `corpus_engine.py`\n>\n"
    "> Export recency is derived from export CONTENT (EXPORT-ARCHIVE) and git commit order "
    "(EXPORT-DOCUMENT). No export version, filename or filesystem timestamp is assumed. "
    "Consumption is measured from the repository's own committed baselines. No timestamps "
    "are emitted; regeneration is byte-identical. Fail-closed.\n"
)


def md_header(model: dict, num: str, title: str, subtitle: str) -> list[str]:
    return [
        f"# {num} — {title}",
        "",
        HDR_NOTE.format(program=model["program"], det=model["determination_id"],
                        head=model["head_commit"]),
        f"> {subtitle}",
        "",
    ]


def table(head: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    out.append("")
    return out


def write(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def rel_location(model: dict, loc: str) -> str:
    """Locations are external absolute paths; render them relative to their corpus root so
    the registers do not embed a machine-specific home directory."""
    for root in sorted(model["corpus_roots"], key=len, reverse=True):
        if loc == root:
            return "."
        if loc.startswith(root.rstrip("/") + "/"):
            return loc[len(root.rstrip("/")) + 1:]
    return Path(loc).name


def render(model: dict) -> list[str]:
    written: list[str] = []
    archives = model["archives"]
    documents = model["documents"]
    conv = model["consumed_conversations"]
    cdocs = model["consumed_documents"]
    canon_a = next((e for e in archives if e.get("canonical")), None)
    canon_d = next((d for d in documents if d.get("canonical")), None)

    # ------------------------------------------------------------------ 01 discovery
    L = md_header(model, "01", "Corpus Discovery Register",
                  "Every ChatGPT export the repository can see, in both corpus classes, "
                  "recognised by payload STRUCTURE and content identity — never by name.")
    L += ["## Corpus roots (EXPORT-ARCHIVE scan)", ""]
    L += table(["#", "Root", "Resolved"],
               [[i + 1, "`" + r + "`", "yes" if r in model["corpus_roots_resolved"] else "no"]
                for i, r in enumerate(model["corpus_roots"])])
    if model["archives"]:
        L += ["`corpus.json` records this inventory in full, so `--render` re-derives the same "
              "determination with NO corpus root present; the EXPORT-DOCUMENT class and both "
              "consumption measurements are always re-measured live from the repository, so a "
              "replayed gate is never vacuous.", ""]
    L += [f"## EXPORT-ARCHIVE — {len(archives)} export(s)", ""]
    L += table(["Export", "Conversations", "Payload members", "Records", "Locations",
                "Identifiable"],
               [[f"`{e['export_id']}`", e["conversations"], e["payload_members"], e["records"],
                 " · ".join(f"`{rel_location(model, loc['location'])}` ({loc['form']})"
                            for loc in e["locations"]),
                 "yes" if e["identifiable"] else "NO"] for e in archives])
    L += ["An export discovered at several locations (an archive and its unpacked tree, or a "
          "symlink) is ONE export: identity is the digest of the payload CONTENT, so rival "
          "copies of the same corpus can never be counted twice.", ""]
    L += [f"## EXPORT-DOCUMENT — {len(documents)} export(s)", ""]
    L += table(["Export", "Bytes", "Tracked", "Commit", "Content sha256 (first 16)"],
               [[f"`{d['path']}`", d["bytes"], "yes" if d["tracked"] else "NO",
                 f"`{d['commit']}`" if d["commit"] else "—", d["content_sha256"][:16]]
                for d in documents])
    L += ["Class membership is decided by the EXISTING PHASE-001B source classifier, imported "
          "by this engine — the repository has exactly one definition of what a ChatGPT "
          "conversation export is.", ""]
    p = HERE / "01-CORPUS-DISCOVERY-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ------------------------------------------------------------------ 02 recency
    L = md_header(model, "02", "Export Recency Register",
                  "The strict total order over discovered exports, oldest → newest, and the "
                  "evidence each rank rests on.")
    L += ["## EXPORT-ARCHIVE recency (content-derived)", ""]
    L += table(["Rank", "Export", "Newest recorded conversation time", "Conversations",
                "Payload digest (first 16)", "Canonical"],
               [[e["recency_rank"], f"`{e['export_id']}`",
                 e["newest_recorded_time"] if e["newest_recorded_time"] is not None else "—",
                 e["conversations"], e["payload_digest"][:16],
                 "CANONICAL" if e.get("canonical") else ""] for e in archives])
    L += ["Recency key: `(newest conversation time recorded inside the export, conversation "
          "count, payload digest)`. The time is read from the export's OWN conversation "
          "records; no filename and no filesystem mtime is consulted, so the order is "
          "identical on every machine and survives a clone.", ""]
    L += ["## EXPORT-DOCUMENT recency (Repository Truth)", ""]
    L += table(["Rank", "Export", "Commit", "Commit time", "History position", "Canonical"],
               [[d["recency_rank"], f"`{d['path']}`", f"`{d['commit']}`" if d["commit"] else "—",
                 d["commit_time"] if d["commit_time"] is not None else "—",
                 d["history_position"] if d["history_position"] is not None else "—",
                 "CANONICAL" if d.get("canonical") else ""] for d in documents])
    L += ["Recency key: `(commit time of the last commit touching the path, history position "
          "counted from the root commit, content sha256)`. Git history is Repository Truth; "
          "position is counted from the ROOT so it cannot shift when a new commit is appended. "
          "An untracked export has no commit and therefore no recency — it fails CC-02 rather "
          "than being ranked on an unverifiable signal.", ""]
    p = HERE / "02-EXPORT-RECENCY-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ------------------------------------------------------------------ 03 canonical
    L = md_header(model, "03", "Canonical Corpus Register",
                  "The resolved canonical assimilation input per corpus class: the single "
                  "newest export every downstream artifact must be derived from.")
    rows = []
    if canon_a:
        rows.append([CLASS_ARCHIVE, f"`{canon_a['export_id']}`",
                     " · ".join(f"`{rel_location(model, loc['location'])}`"
                                for loc in canon_a["locations"]),
                     f"{canon_a['conversations']} conversations",
                     canon_a["payload_digest"][:16]])
    if canon_d:
        rows.append([CLASS_DOCUMENT, f"`{canon_d['path']}`", f"`{canon_d['path']}`",
                     f"{canon_d['bytes']} bytes", canon_d["content_sha256"][:16]])
    L += table(["Corpus class", "Canonical export", "Location(s)", "Extent",
                "Identity (first 16)"], rows)
    if canon_a:
        older: set[str] = set()
        for exp in archives:
            if exp["payload_digest"] != canon_a["payload_digest"]:
                older.update(exp["conversation_ids"])
        exclusive = sorted(set(canon_a["conversation_ids"]) - older)
        L += ["## Canonical-exclusive knowledge (EXPORT-ARCHIVE)", "",
              f"The canonical export carries **{len(exclusive)}** conversation(s) that no "
              f"older discovered export carries. This is the knowledge that is LOST whenever "
              f"a stale corpus is assimilated, and it is the evidence CC-05 requires the "
              f"baseline to demonstrate.", ""]
    L += ["## Resolution rule", "",
          "Canonical = the maximum of the recency order (Register 02) within a corpus class. "
          "Every downstream artifact must be derivable from the canonical export; a baseline "
          "that demonstrably never saw it is STALE and the gate fails closed.", ""]
    p = HERE / "03-CANONICAL-CORPUS-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ------------------------------------------------------------------ 04 consumption
    L = md_header(model, "04", "Corpus Consumption Register",
                  "What the repository's committed baselines ACTUALLY consumed, measured from "
                  "the repository itself — never from an external claim.")
    L += ["## EXPORT-ARCHIVE consumption", ""]
    L += table(["Measure", "Value", "Evidence"], [
        ["Assimilated knowledge objects", conv.get("objects", 0), f"`{conv.get('source', '')}`"],
        ["Distinct conversations cited", len(conv.get("ids", [])),
         "column `evidence_conversation`"],
        ["Canonical export conversations", canon_a["conversations"] if canon_a else 0,
         "Register 03"],
        ["Cited conversations absent from the canonical export",
         len(set(conv.get("ids", [])) - set(canon_a["conversation_ids"])) if canon_a else "—",
         "CC-04"],
    ])
    L += ["## EXPORT-DOCUMENT consumption", ""]
    L += table(["Consumed export", "Recorded content sha256 (first 16)", "Current", "State"],
               [[f"`{rec['path']}`", rec["content_sha256"][:16],
                 next((d["content_sha256"][:16] for d in documents
                       if d["path"] == rec["path"]), "—"),
                 "CURRENT" if any(d["path"] == rec["path"]
                                  and d["content_sha256"] == rec["content_sha256"]
                                  for d in documents) else "DRIFTED/ABSENT"]
                for rec in cdocs.get("documents", [])])
    ignored = [d["path"] for d in documents
               if d["path"] not in {r["path"] for r in cdocs.get("documents", [])}]
    L += [f"Discovered in-repo conversation exports never consumed: **{len(ignored)}**"
          + ((" — " + ", ".join(f"`{p}`" for p in ignored)) if ignored else ""), ""]
    L += [f"Consumption evidence: `{cdocs.get('source', '')}` (`documents[]` where "
          f"`class == CONVERSATION`).", ""]
    p = HERE / "04-CORPUS-CONSUMPTION-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ------------------------------------------------------------------ 05 staleness
    L = md_header(model, "05", "Corpus Staleness Register",
                  "The fail-closed currency determination: is every downstream artifact "
                  "derived from the newest available export?")
    L += table(["Gate", "Subject", "Blocking", "Count", "Result", "Detail"],
               [[f"{g['id']} — {g['gate']}", g["subject"], "yes" if g["blocking"] else "no",
                 g["count"], g["result"], "; ".join(str(d) for d in g["detail"]) or "—"]
                for g in model["gates"]])
    L += [f"## Determination — **{model['determination']}**", ""]
    stale = [g for g in model["gates"] if g["blocking"] and g["result"] == "FAIL"]
    if stale:
        L += ["The corpus is STALE. Restore currency by regenerating the affected baseline "
              "from the canonical export (Register 03), then re-run this gate:", "",
              "```", "make corpus", "make assimilate-gate", "```", ""]
        L += table(["Failing gate", "Why it blocks"],
                   [[g["id"], "; ".join(str(d) for d in g["detail"])] for g in stale])
    else:
        L += ["No blocking staleness condition holds: every corpus class resolves to a "
              "canonical export, and every committed baseline demonstrably consumed it.", ""]
    p = HERE / "05-CORPUS-STALENESS-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ------------------------------------------------------------------ 06 validation
    L = md_header(model, "06", "Validation Report",
                  "Automated validation of the corpus-currency capability itself.")
    L += ["## Program gates (fail-closed)", ""]
    L += table(["Gate", "Blocking", "Result", "Count"],
               [[f"{g['id']} — {g['gate']}", "yes" if g["blocking"] else "no", g["result"],
                 g["count"]] for g in model["gates"]])
    L += ["## Validated properties", ""]
    L += table(["Property", "How it is proven", "Where"], [
        ["Newest export selected",
         "the recency order is recomputed from export content / git history and the maximum "
         "is recorded as canonical", "Register 02/03 · `test_corpus_currency.py`"],
        ["Stale export rejected",
         "CC-05 fails closed when the canonical export contributes conversations no older "
         "export carries and the baseline cites none of them",
         "Register 05 · `test_corpus_currency.py`"],
        ["Deterministic behaviour",
         "no timestamp is emitted; JSON is sorted and indented; markdown ends in exactly one "
         "newline; identity and order are content-derived",
         "`corpus.json` seal · `test_corpus_currency.py`"],
        ["Reproducible execution",
         "`--render` re-derives the determination from `corpus.json` with no corpus root, and "
         "the CI drift gate diffs the re-rendered registers against the committed ones",
         "`make corpus-replay` · `.github/workflows/corpus-gate.yml`"],
        ["Traceability preserved",
         "every export carries its content identity, every consumed conversation is traced to "
         "the committed baseline column it was read from", "Register 04 · `EVIDENCE-MANIFEST.json`"],
        ["Dependency closure preserved",
         "the gate runs BEFORE assimilation in the Makefile, so no downstream artifact can be "
         "generated from an unverified corpus", "`Makefile` (`assimilate: corpus-gate`)"],
        ["Repository Truth preserved",
         "consumption is measured only from committed in-repo artifacts; the external corpus "
         "is read-only and is never a home for anything", "Register 04"],
    ])
    L += ["## Disclosed limits", "",
          "- An EXPORT-ARCHIVE is recognised through `*.json` payloads whose content matches "
          "the conversation structure; a corpus published in some other container is not "
          "discovered (it would also not be consumable by the assimilation pipeline).",
          "- CC-05 proves the newest export was assimilated by requiring evidence from its "
          "exclusive conversations. A newer export whose exclusive conversations yield no "
          "knowledge object at all would fail this gate; that is deliberate — under "
          "fail-closed, unproven currency is treated as staleness, not as a pass.",
          "- The scan is bounded to depth "
          f"{MAX_SCAN_DEPTH} below each corpus root and never descends into a recognised "
          "export.", ""]
    p = HERE / "06-VALIDATION-REPORT.md"
    write(p, L)
    written.append(p.name)

    # ------------------------------------------------------------------ 07 certification
    blocking_fail = [g for g in model["gates"] if g["blocking"] and g["result"] == "FAIL"]
    L = md_header(model, "07", "Certification Report",
                  "Certification of D-1 — corpus currency as an enforced repository "
                  "capability.")
    L += [f"**DETERMINATION: {model['determination']}** — "
          f"{len(blocking_fail)} blocking gate failure(s).", ""]
    L += table(["Certified", "Evidence"], [
        ["Export discovery is implemented, not documented",
         "`corpus_engine.py` structural discovery over the configured corpus roots"],
        ["Newest-export detection is content-derived",
         f"Register 02 — canonical EXPORT-ARCHIVE `{model['canonical_archive']}`, canonical "
         f"EXPORT-DOCUMENT `{model['canonical_document']}`"],
        ["Canonical input resolution is recorded",
         "Register 03 + `corpus.json` (`canonical_archive`, `canonical_document`)"],
        ["Stale corpus is rejected automatically",
         "CC-04/CC-05/CC-06/CC-07 are blocking; `make corpus-gate` exits non-zero"],
        ["Assimilation cannot run against an unverified corpus",
         "`assimilate`, `assimilate-replay` and `assimilate-gate` depend on `corpus-gate`"],
        ["Determinism", "no timestamps are emitted; regeneration is byte-identical; "
         f"seal `{model['seal_sha256'][:16]}`"],
        ["Knowledge Once", "an export discovered at several locations is one export "
         "(content identity); no corpus is counted or assimilated twice"],
        ["Repository Truth", "consumption is measured from committed in-repo baselines only; "
         "the external corpus is read-only"],
    ])
    if blocking_fail:
        L += ["## NOT CERTIFIED", ""]
        L += table(["Gate", "Failure"],
                   [[g["id"], "; ".join(str(d) for d in g["detail"])] for g in blocking_fail])
    L += ["## Evidence manifest (hashed inputs)", ""]
    L += table(["Key", "Input", "sha256 (first 16)"],
               [[k, "`" + (v["relative"] if not v["relative"].startswith("/")
                           else rel_location(model, v["relative"])) + "`", v["sha256"][:16]]
                for k, v in sorted(model["evidence_manifest"].items())])
    p = HERE / "07-CERTIFICATION-REPORT.md"
    write(p, L)
    written.append(p.name)

    # ------------------------------------------------------------------ 08 completion
    L = md_header(model, "08", "Corpus Currency Completion Report",
                  "D-1 completion state: what the repository can now guarantee about corpus "
                  "currency.")
    L += table(["Objective (D-1)", "State", "Evidence"], [
        ["Detect the newest available ChatGPT export", "IMPLEMENTED", "Register 01/02"],
        ["Make the newest export the canonical assimilation input", "IMPLEMENTED",
         "Register 03"],
        ["Prevent future execution against stale exports", "IMPLEMENTED",
         "Register 05 · `corpus-gate` precedes `assimilate`"],
        ["Regenerate the complete assimilation baseline", "IMPLEMENTED",
         "`make corpus assimilate roadmap`"],
        ["Regenerate all downstream derived artifacts", "IMPLEMENTED",
         "PHASE-001B → CLOSURE-008 → UCOS-MXR-001"],
        ["Preserve determinism", "PRESERVED", "byte-identical regeneration; no timestamps"],
        ["Preserve Repository Truth", "PRESERVED", "Register 04"],
        ["Preserve Knowledge Once", "PRESERVED", "content identity dedupe"],
    ])
    L += ["## Corpus state", ""]
    L += table(["Corpus class", "Exports", "Canonical", "Currency"], [
        [CLASS_ARCHIVE, len(archives), f"`{model['canonical_archive']}`",
         "CURRENT" if not [g for g in model["gates"]
                           if g["subject"] in (CLASS_ARCHIVE, "BOTH")
                           and g["blocking"] and g["result"] == "FAIL"] else "STALE"],
        [CLASS_DOCUMENT, len(documents), f"`{model['canonical_document']}`",
         "CURRENT" if not [g for g in model["gates"]
                           if g["subject"] in (CLASS_DOCUMENT, "BOTH")
                           and g["blocking"] and g["result"] == "FAIL"] else "STALE"],
    ])
    L += [f"**{model['determination']}** — `{PROGRAM}` {DETERMINATION_ID}: "
          + ("COMPLETE." if model["determination"] == "CORPUS CURRENT"
             else "NOT COMPLETE while a blocking gate fails."), ""]
    p = HERE / "08-CORPUS-CURRENCY-COMPLETION-REPORT.md"
    write(p, L)
    written.append(p.name)
    return written


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=f"{PROGRAM} {DETERMINATION_ID} corpus currency "
                                             f"engine")
    ap.add_argument("--gate", action="store_true",
                    help="exit 1 unless the determination is CORPUS CURRENT")
    ap.add_argument("--render", action="store_true",
                    help="replay the export inventory from corpus.json (no corpus root needed)")
    args = ap.parse_args()

    if args.render:
        if not CORPUS_JSON.exists():
            print(f"{PROGRAM}: FAIL-CLOSED — {CORPUS_JSON.name} absent; cannot render.",
                  file=sys.stderr)
            return 1
        recorded = deserialize(CORPUS_JSON.read_text(encoding="utf-8"))
        model = build(recorded)
    else:
        model = build(None)
        CORPUS_JSON.write_text(serialize(model), encoding="utf-8")
        EVIDENCE_MANIFEST.write_text(
            json.dumps(dict(program=PROGRAM, determination_id=DETERMINATION_ID,
                            head_commit=model["head_commit"],
                            corpus_roots=[portable_location(r) for r in model["corpus_roots"]],
                            canonical_archive=model["canonical_archive"],
                            canonical_document=model["canonical_document"],
                            files=model["evidence_manifest"]),
                       indent=2, sort_keys=True) + "\n", encoding="utf-8")

    written = render(model)
    print(f"{PROGRAM} {DETERMINATION_ID}: {model['determination']} "
          f"| archives={len(model['archives'])} canonical={model['canonical_archive'] or '—'} "
          f"| documents={len(model['documents'])} "
          f"canonical={model['canonical_document'] or '—'} "
          f"| conversations_cited={len(model['consumed_conversations'].get('ids', []))}")
    print(f"wrote {len(written)} registers to 00-MASTER/{PROGRAM}")
    if args.gate and model["determination"] != "CORPUS CURRENT":
        for g in model["gates"]:
            if g["blocking"] and g["result"] == "FAIL":
                print(f"  BLOCKING FAIL: {g['id']} {g['gate']} = {g['count']} {g['detail']}",
                      file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
