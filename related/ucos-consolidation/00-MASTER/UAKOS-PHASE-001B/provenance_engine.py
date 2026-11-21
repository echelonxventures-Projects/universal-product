#!/usr/bin/env python3
"""UAKOS PHASE-001B — Universal Constitutional Provenance Reconstruction engine.

READ-ONLY evidence-reconstruction instrument (operational memory, NOT repository
implementation). It never mutates 00-SOURCE/** 99-FREEZE/** engine/** platform/**
or any constitution. It only *reconstructs* the provenance layer that the
Phase-001 closure engine discarded when it flattened each DOCX into a single
whitespace-collapsed string.

Mission: reconstruct the chain
    Document -> Page -> Section -> Paragraph -> Original Text -> Knowledge Object
             -> Repository Evidence -> Validation Evidence -> Certification Evidence
for every knowledge object in closure.json (the concept universe is read from the
closure baseline — never hardcoded).

Determinism (UCKO-PRIN-0005): stdlib only; logical pages are derived from
explicit <w:br w:type="page"/> and Word <w:lastRenderedPageBreak/> markers in
word/document.xml (reproducible from the file, never guessed); sections are
reconstructed from structural heading patterns (disclosed heuristic, since the
source DOCX carry no paragraph styles). Every field cites evidence; nothing is
synthesised.

Usage:
    python3 00-MASTER/UAKOS-PHASE-001B/provenance_engine.py
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import zipfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CLOSURE = REPO / "00-MASTER" / "UAKOS-CLOSURE-002" / "closure.json"
#: The declared record of every artifact a producer regenerates — see :func:`derived_paths`.
GENERATED = REPO / "00-BOOK" / "DATA" / "generated-artifact-registry.json"

# --- concept anchor families: verbatim copy of closure_engine.py FAMILIES so the
# --- concept namespace this phase reconstructs is IDENTICAL to the one Phase-001 closed.
FAMILIES: list[tuple[str, re.Pattern[str]]] = [
    ("UCKO", re.compile(r"\bUCKO-[A-Z]+-\d{3,4}\b")),
    ("UKDA-DEC", re.compile(r"\bUKDA-DEC-\d{3,4}\b")),
    ("ARCH", re.compile(r"\bARCH-[A-Z0-9]+-\d{3}\b")),
    ("MEP", re.compile(r"\bMEP-\d{2}\b")),
    ("MCP", re.compile(r"\bMCP-\d{3}\b")),
    ("MCS", re.compile(r"\bMCS-\d{3}\b")),
    ("CEP", re.compile(r"\bCEP-\d{3}\b")),
    ("DATA", re.compile(r"\bDATA-\d{3}\b")),
    ("SERVICE", re.compile(r"\bSERVICE-\d{3}\b")),
    ("APPLICATION", re.compile(r"\bAPPLICATION-\d{3}\b")),
    ("INFRASTRUCTURE", re.compile(r"\bINFRASTRUCTURE-\d{3}\b")),
    ("PLATFORM", re.compile(r"\bPLATFORM-\d{3}\b")),
    ("RUNTIME", re.compile(r"\bRUNTIME-\d{3}\b")),
    ("UCOS-COMP", re.compile(r"\bUCOS-COMP-\d{6}\b")),
    ("UCOS-GOV", re.compile(r"\bUCOS-GOV-\d{3}\b")),
    ("UCOS-EXEC", re.compile(r"\bUCOS-EXEC-\d{3}\b")),
    ("UCOS-RAT", re.compile(r"\bUCOS-RAT-\d{3}\b")),
    ("UCOS-RECON", re.compile(r"\bUCOS-RECON-[A-Z0-9]+\b")),
    ("EPIC", re.compile(r"\bEPIC-[A-Z]+-\d{3}\b")),
    ("GOV", re.compile(r"\bGOV-\d{3}\b")),
    ("METACLASS", re.compile(r"\b(?:AMC|AMR|DMC|DMR|SMC|SMR|ICMP|ICNW|ISTO|ICAP)-\d{2}\b")),
    ("BAND-UNIT", re.compile(r"\bEC3-B\d{2}-[A-Z]?\d{2}\b")),
    ("EC3-GATE", re.compile(r"\bEC-3-AP-\d\b")),
    ("FOUNDATION", re.compile(r"\b(?:EL-1|RL-F2|PL-F2|DF-2|SF-2|AF-3)\b")),
    ("LAW", re.compile(r"Ω∞-\d{3}\b")),
    ("PHASE", re.compile(r"\bPhase-\d{3}\b")),
]
_SENTINEL = re.compile(r"-U?9{2,3}$")

# heading detection (source DOCX carry NO paragraph styles -> structural heuristic)
H_KEYWORD = re.compile(
    r"^(ARTICLE|SECTION|CHAPTER|PART|APPENDIX|SCHEDULE|ANNEX|TITLE|PREAMBLE|"
    r"PHASE|STAGE|EPIC|BAND|LAW|PRINCIPLE|CLAUSE|DIVISION)\b", re.I)
H_NUMBERED = re.compile(r"^(\d+(?:\.\d+){0,4})[\.\)]?\s+\S")
CONV_MARK = re.compile(r"\b(recommend|recommendation|propose|proposal|suggest|"
                       r"decision|decide|we will|we should|let'?s|option|reject|"
                       r"defer|deferred|future|instead|better to|going to|plan to)\b", re.I)
REC_MARK = re.compile(r"\b(recommend(?:s|ed|ation)?|propose[sd]?|suggest(?:s|ed|ion)?)\b", re.I)

PARA_RE = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.S)
TEXT_RE = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.S)
PAGES_RE = re.compile(r"<Pages>(\d+)</Pages>")


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False).stdout


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------- source classification
def classify_doc(rel: str) -> str:
    low = rel.lower()
    base = low.rsplit("/", 1)[-1]
    if "chatgpt" in base or "chat.docx" in base or base.startswith("chat"):
        return "CONVERSATION"
    if rel.startswith("00-SOURCE/CONSTITUTIONS"):
        return "CONSTITUTION"
    if rel.startswith("00-SOURCE/VISION"):
        return "VISION"
    if rel.startswith("00-SOURCE/PHASES"):
        return "PHASES"
    if rel.startswith("00-SOURCE/ARCHITECTURE"):
        return "ARCHITECTURE"
    if rel.startswith("00-SOURCE"):
        return "SOURCE"
    if "architectural-sources" in low:
        return "ARCH-SOURCE"
    if rel.startswith("04-REFERENCE"):
        return "REFERENCE"
    return "OTHER"


# priority for choosing the *originating* source (lower = more authoritative origin)
CLASS_PRIORITY = {
    "CONSTITUTION": 0, "VISION": 1, "PHASES": 2, "ARCHITECTURE": 3, "SOURCE": 4,
    "ARCH-SOURCE": 5, "REFERENCE": 6, "OTHER": 7, "CONVERSATION": 9,
}


# --------------------------------------------------------------- DOCX structural parse
def parse_docx(rel: str, p: Path) -> dict:
    """Deterministically reconstruct pages/sections/paragraphs from word/document.xml."""
    rec = {
        "path": rel, "sha256": sha256_file(p), "bytes": p.stat().st_size,
        "class": classify_doc(rel), "extractable": True, "integrity": "OK",
        "declared_pages": None, "logical_pages": 0, "paragraphs": 0,
        "nonempty_paragraphs": 0, "explicit_page_breaks": 0, "render_page_breaks": 0,
        "sections": 0, "tables": 0, "images": 0, "error": None,
    }
    try:
        z = zipfile.ZipFile(p)
        names = z.namelist()
        if "word/document.xml" not in names:
            rec["extractable"] = False
            rec["integrity"] = "NO_DOCUMENT_XML"
            return rec | {"_paras": []}
        raw = z.read("word/document.xml").decode("utf-8", "ignore")
        if "docProps/app.xml" in names:
            m = PAGES_RE.search(z.read("docProps/app.xml").decode("utf-8", "ignore"))
            if m:
                rec["declared_pages"] = int(m.group(1))
        rec["tables"] = raw.count("<w:tbl>")
        rec["images"] = raw.count("<pic:pic") + raw.count("<w:drawing>")
    except (OSError, zipfile.BadZipFile) as e:
        rec["extractable"] = False
        rec["integrity"] = f"BADZIP:{e}"
        return rec | {"_paras": []}

    paras: list[dict] = []
    section_map: list[dict] = []
    page = 1
    sec_stack = {1: "", 2: "", 3: ""}   # heading levels
    sections_seen: set[str] = set()
    explicit_pb = render_pb = 0
    for i, block in enumerate(PARA_RE.findall(raw)):
        # page breaks recorded on this paragraph -> advance the logical page BEFORE placing it
        ep = block.count('w:type="page"')
        rp = block.count("lastRenderedPageBreak")
        if ep or rp:
            page += (ep + rp)
            explicit_pb += ep
            render_pb += rp
        text = html.unescape("".join(TEXT_RE.findall(block))).strip()
        if not text:
            paras.append({"i": i, "page": page, "sec": _sec_path(sec_stack), "text": ""})
            continue
        lvl = _heading_level(text)
        if lvl:
            sec_stack[lvl] = text[:120]
            for deeper in range(lvl + 1, 4):
                sec_stack[deeper] = ""
            key = f"p{page}|{text[:120]}"
            if key not in sections_seen:
                sections_seen.add(key)
                section_map.append({"level": lvl, "heading": text[:120],
                                    "page": page, "paragraph": i})
        paras.append({"i": i, "page": page, "sec": _sec_path(sec_stack), "text": text})

    rec["logical_pages"] = page
    rec["paragraphs"] = len(paras)
    rec["nonempty_paragraphs"] = sum(1 for x in paras if x["text"])
    rec["explicit_page_breaks"] = explicit_pb
    rec["render_page_breaks"] = render_pb
    rec["sections"] = len(sections_seen)
    rec["section_map"] = section_map
    return rec | {"_paras": paras}


def _heading_level(text: str) -> int | None:
    if len(text) > 140:
        return None
    if H_KEYWORD.match(text):
        return 1
    if H_NUMBERED.match(text) and len(text) <= 120:
        return 2
    letters = [c for c in text if c.isalpha()]
    if 2 <= len(text) <= 80 and letters and text == text.upper() and not text.endswith((".", ",", ";")):
        return 3
    return None


def _sec_path(stack: dict) -> str:
    return " / ".join(stack[l] for l in (1, 2, 3) if stack[l]) or "(preamble/unsectioned)"


# derived/evidence artifacts are never a credible canonical *home*
_NON_HOME = ("CHECKPOINTS/", "_evidence/", "/outputs/", "outputs/", "determinism-evidence/",
             "artifacts.json", "id-ledger.json", "change-ledger.json", "relationships.json",
             ".egg-info/", "/__pycache__/")
# preference order for a credible originating home (lower rank = stronger)
_HOME_ROOTS = ("02-MASTER", "00-CEP", "03-CATALOGS", "knowledge", "06-IMPLEMENTATION",
               "07-ENGINEERING", "08-RUNTIME", "09-PLATFORM", "10-DATA", "11-SERVICE",
               "12-APPLICATION", "13-INFRASTRUCTURE", "14-SECURITY", "04-REFERENCE",
               "00-BOOK", "00-MASTER")


def _best_home(exact: list, defh: list, files: list) -> str | None:
    if exact:
        return sorted(exact)[0]
    if defh:
        return sorted(defh)[0]
    real = [f for f in files if not any(s in f for s in _NON_HOME)]
    if not real:
        real = files
    if not real:
        return None

    def rank(f: str) -> tuple:
        top = f.split("/", 1)[0]
        r = _HOME_ROOTS.index(top) if top in _HOME_ROOTS else len(_HOME_ROOTS)
        return (r, len(f), f)

    return sorted(real, key=rank)[0]


# --------------------------------------------------------------- concept occurrence scan
def scan_concepts(docs: list[dict]) -> dict:
    """id -> {doc_rel -> first occurrence {page,sec,para,text}}, deterministic first-hit per doc."""
    occ: dict[str, dict[str, dict]] = defaultdict(dict)
    for d in docs:
        rel = d["path"]
        for para in d["_paras"]:
            t = para["text"]
            if not t:
                continue
            for fam, rx in FAMILIES:
                for cid in rx.findall(t):
                    if _SENTINEL.search(cid):
                        continue
                    if rel not in occ[cid]:
                        occ[cid][rel] = {
                            "page": para["page"], "section": para["sec"],
                            "paragraph": para["i"], "family": fam,
                            "text": t[:400],
                        }
    return occ


# --------------------------------------------------------------- main reconstruction
def derived_paths() -> frozenset[str]:
    """Every path a declared producer regenerates.

    A DERIVED REGISTER IS NOT EVIDENCE OF A CONCEPT; IT IS A PROJECTION THAT MENTIONS ONE.
    Counting one makes this measurement depend on when a SIBLING register last ran, which
    UCOS-RFP-001 measured as non-convergence: this programme, PHASE-001A-R1, CLOSURE-009 and
    PHASE-002 each rewrote on pass TWO of the fixed-point pipeline because each counted files
    the others had just written. The reference is mutual rather than sequential, so no stage
    ordering resolves it.

    The population is DECLARED, never enumerated here, so an artifact that becomes generated
    tomorrow leaves this count with no edit to this engine.
    """
    if not GENERATED.is_file():
        return frozenset()
    entries = (json.loads(GENERATED.read_text("utf-8")) or {}).get("entries") or []
    return frozenset(
        str(e["canonical_path"])
        for e in entries
        if isinstance(e, dict) and e.get("canonical_path")
    )

def reconstruct() -> dict:
    closure = json.loads(CLOSURE.read_text("utf-8"))
    concepts = {c["id"]: c for c in closure["concepts"]}
    derived = derived_paths()

    # Enumerate ALL frozen source DOCX from the filesystem (mission consumes every
    # source under 00-SOURCE/** and 04-REFERENCE/** incl ARCHITECTURAL-SOURCES/**,
    # regardless of git-tracking status). Word lock/temp files (~$) are excluded.
    docx_rels: list[str] = []
    for root in ("00-SOURCE", "04-REFERENCE"):
        base = REPO / root
        if base.is_dir():
            for p in base.rglob("*.docx"):
                if p.name.startswith("~$"):
                    continue
                docx_rels.append(str(p.relative_to(REPO)))
    docs = []
    for rel in sorted(set(docx_rels)):
        p = REPO / rel
        if p.is_file():
            docs.append(parse_docx(rel, p))
    docs.sort(key=lambda d: (CLASS_PRIORITY.get(d["class"], 8), d["path"]))

    occ = scan_concepts(docs)
    doc_class = {d["path"]: d["class"] for d in docs}

    # per-concept provenance reconstruction
    prov = []
    for cid in sorted(concepts):
        c = concepts[cid]
        hits = occ.get(cid, {})
        # choose originating source by class priority then path
        origin = None
        if hits:
            rel = sorted(hits, key=lambda r: (CLASS_PRIORITY.get(doc_class[r], 8), r))[0]
            h = hits[rel]
            origin = {
                "source_document": rel, "source_class": doc_class[rel],
                "page": h["page"], "section": h["section"],
                "paragraph": h["paragraph"], "original_text": h["text"],
                "other_source_documents": sorted(r for r in hits if r != rel),
            }
        exact = c.get("exact_homes") or []
        defh = c.get("def_homes") or []
        repo_home = _best_home(exact, defh, c.get("files") or [])
        in_conv = bool(hits) and all(doc_class[r] == "CONVERSATION" for r in hits)
        in_frozen = any(doc_class[r] in ("CONSTITUTION", "VISION", "PHASES", "ARCHITECTURE", "SOURCE")
                        for r in hits)

        # reconstruction quality (Step 8) + confidence (Step 4)
        if origin and in_frozen:
            quality = "RECOVERED" if origin["section"] != "(preamble/unsectioned)" else "PARTIALLY_RECOVERED"
            confidence = "HIGH"
        elif origin and doc_class[origin["source_document"]] in ("ARCH-SOURCE", "REFERENCE"):
            quality = "PARTIALLY_RECOVERED"
            confidence = "MEDIUM"
        elif in_conv:
            quality = "CONVERSATION_ONLY"
            confidence = "LOW"
        elif c.get("conversation_only"):
            quality = "CONVERSATION_ONLY"
            confidence = "LOW"
        elif repo_home:
            quality = "REPOSITORY_ONLY"
            confidence = "REPOSITORY"
        else:
            quality = "NOT_RECOVERABLE"
            confidence = "NONE"

        trace = c.get("trace", {})
        # evidence completeness: 8 provenance-chain links
        links = {
            "source_document": bool(origin) or bool(repo_home),
            "page": bool(origin),
            "section": bool(origin) and origin["section"] != "(preamble/unsectioned)",
            "paragraph": bool(origin),
            "original_text": bool(origin),
            "knowledge_object": True,
            "repository_evidence": bool(c.get("files")),
            "validation_evidence": bool(trace.get("specification") or trace.get("implementation")),
            "certification_evidence": bool(c.get("certified")),
        }
        prov.append({
            "id": cid, "family": c["family"], "disposition": c["disposition"],
            "origin": origin,
            "repository_home": repo_home,
            "repository_evidence_files": len(
                [f for f in (c.get("files") or []) if f not in derived]
            ),
            "def_homes": defh, "exact_homes": exact,
            "trace": trace, "certified": bool(c.get("certified")),
            "conversation_only": bool(c.get("conversation_only")),
            "upload_only": bool(c.get("upload_only")),
            "orphan": bool(c.get("orphan")),
            "quality": quality, "confidence": confidence,
            "links": links,
            "completeness": round(sum(links.values()) / len(links), 3),
        })

    # ChatGPT assimilation
    chat_docs = [d for d in docs if d["class"] == "CONVERSATION"]
    chat_items = []
    all_ids = set(concepts)
    for d in chat_docs:
        for para in d["_paras"]:
            t = para["text"]
            if not t or not CONV_MARK.search(t):
                continue
            cited = sorted({cid for _, rx in FAMILIES for cid in rx.findall(t)
                            if cid in all_ids})
            chat_items.append({
                "document": d["path"], "page": para["page"], "section": para["sec"],
                "paragraph": para["i"], "text": t[:300],
                "cited_concepts": cited,
                "status": "CAPTURED" if cited else "CANDIDATE",
            })

    # recommendations across all sources
    recs = []
    for d in docs:
        for para in d["_paras"]:
            t = para["text"]
            if t and REC_MARK.search(t):
                cited = sorted({cid for _, rx in FAMILIES for cid in rx.findall(t) if cid in all_ids})
                recs.append({"document": d["path"], "class": d["class"], "page": para["page"],
                             "paragraph": para["i"], "text": t[:280], "cited_concepts": cited})

    return {
        "closure_baseline": {"commit": closure.get("baseline_commit"),
                             "branch": closure.get("branch"),
                             "concept_total": closure.get("concept_total"),
                             "determination": closure.get("determination")},
        "docs": docs, "occ": occ, "prov": prov,
        "chat_items": chat_items, "recs": recs,
        "families": closure.get("families", {}),
        "concepts_raw": concepts,
    }


if __name__ == "__main__":
    model = reconstruct()
    # strip heavy paragraph payloads before dumping the machine model; cap section maps
    slim_docs = []
    for d in model["docs"]:
        sd = {k: v for k, v in d.items() if k != "_paras"}
        sm = sd.get("section_map", [])
        sd["section_map_shown"] = len(sm[:800])
        sd["section_map"] = sm[:800]
        slim_docs.append(sd)
    out = {
        "closure_baseline": model["closure_baseline"],
        "documents": slim_docs,
        "provenance": model["prov"],
        "chatgpt_items": model["chat_items"],
        "recommendations_sample": model["recs"][:2000],
        "recommendations_total": len(model["recs"]),
        "families": model["families"],
    }
    (HERE / "provenance.json").write_text(
        json.dumps(out, indent=2, sort_keys=False, ensure_ascii=False) + "\n", "utf-8")
    q = defaultdict(int)
    for r in model["prov"]:
        q[r["quality"]] += 1
    print("PHASE-001B reconstruction complete")
    print("documents:", len(slim_docs), "| concepts:", len(model["prov"]))
    print("quality:", dict(sorted(q.items())))
    print("chatgpt items:", len(model["chat_items"]), "| recommendations:", len(model["recs"]))
