#!/usr/bin/env python3
"""UAKOS-CLOSURE-002 · PHASE-002 — deterministic concept-graph reconciliation engine.

PHASE-002 does NOT re-extract or re-match concepts. It REUSES the Phase-001 machine
model (`closure.json`, produced by `closure_engine.py`) as the single canonical concept
truth (Knowledge Once, UCKO-PRIN-0001) and the repository's existing canonical typed
knowledge graph (`00-BOOK/DATA/relationships.json`) as the authoritative relationship
store. It projects those artifacts into the PHASE-002 reconciliation views (outputs
20-35) and a deterministic enrichment PLAN. It never mutates the frozen corpus, never
invents semantic matches, never applies enrichment automatically, and never issues a
green determination the evidence does not support (fail-closed, TRACK-001).

Inputs (read-only, must already exist):
    00-MASTER/UAKOS-CLOSURE-002/closure.json        (Phase-001 concept model)
    00-BOOK/DATA/relationships.json                 (canonical typed knowledge graph)

Outputs (regenerated deterministically):
    20..35 NN-*.md   +  phase2.json  (machine model)

Usage:
    python3 00-MASTER/UAKOS-CLOSURE-002/phase2_engine.py            # generate outputs 20-35
    python3 00-MASTER/UAKOS-CLOSURE-002/phase2_engine.py --gate     # exit 1 if NOT-CLOSED
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CLOSURE_JSON = HERE / "closure.json"
RELATIONSHIPS_JSON = REPO / "00-BOOK" / "DATA" / "relationships.json"

TRUTH_HOME_ROOTS = ("02-MASTER", "00-CEP", "00-BOOK", "00-MASTER", "03-CATALOGS",
                    "04-REFERENCE", "adr", "knowledge")
NONHOME_ROOTS = ("00-SOURCE", "01-WORKING")  # mention/upload zones, never a canonical home


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False).stdout


def _fence(rows: list[list], header: list[str]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def _top(rel: str) -> str:
    return rel.split("/", 1)[0]


# --------------------------------------------------------------------------- load canonical inputs
def load_inputs() -> tuple[dict, list[dict], dict]:
    if not CLOSURE_JSON.is_file():
        sys.exit("FAIL-CLOSED: closure.json (Phase-001 model) absent — run `make closure` first.")
    model = json.loads(CLOSURE_JSON.read_text("utf-8"))
    concepts = sorted(model["concepts"], key=lambda r: r["id"])
    graph = {"present": False, "count": 0, "edge_types": {}}
    if RELATIONSHIPS_JSON.is_file():
        rel = json.loads(RELATIONSHIPS_JSON.read_text("utf-8"))
        edges = rel.get("relationships", [])
        et = Counter(e.get("type") for e in edges)
        graph = {"present": True, "count": rel.get("count", len(edges)),
                 "edge_types": dict(sorted(et.items(), key=lambda kv: (-kv[1], kv[0])))}
    return model, concepts, graph


# --------------------------------------------------------------------------- concept-level derivations
def owner_of(rec: dict) -> str:
    """Owning program/zone = top-level of the canonical home; fall back to primary evidence top."""
    homes = rec.get("exact_homes") or rec.get("def_homes") or []
    if homes:
        return _top(sorted(homes)[0])
    # homed via code/constitution/book/spec but no filename home: use first non-source top
    tops = [t for t in sorted(rec.get("tops", [])) if t not in NONHOME_ROOTS]
    if tops:
        return tops[0]
    return sorted(rec.get("tops", ["(none)"]))[0]


def gap_class(rec: dict) -> str:
    if rec["homed"]:
        return "ORPHAN" if rec["orphan"] else "HOMED"
    if rec["in_repo_unhomed"]:
        return "IN-REPO-UNHOMED"
    if rec["upload_only"]:
        return "UPLOAD-ONLY"
    if rec["conversation_only"]:
        return "CONVERSATION-ONLY"
    return "UNCLASSIFIED"


def home_kinds(rec: dict) -> str:
    kinds = []
    if rec["in_filename"]:
        kinds.append("filename")
    if rec["in_code"]:
        kinds.append("code")
    if rec["in_constitution"]:
        kinds.append("constitution")
    if rec["in_book"]:
        kinds.append("book/catalog")
    if rec["in_spec"]:
        kinds.append("spec")
    return "+".join(kinds) if kinds else "—"


def build_cooccurrence(concepts: list[dict]) -> tuple[dict, list[tuple]]:
    """Deterministic co-occurrence graph: two concepts share an edge when they appear in the
    same definitional evidence file. Evidence-backed (from closure.json `files`); not invented."""
    file_to_concepts: dict[str, list[str]] = defaultdict(list)
    for r in concepts:
        for f in r["files"]:
            file_to_concepts[f].append(r["id"])
    edge_weight: dict[tuple[str, str], int] = defaultdict(int)
    for f, ids in file_to_concepts.items():
        uniq = sorted(set(ids))
        for a, b in combinations(uniq, 2):
            edge_weight[(a, b)] += 1
    degree: dict[str, int] = defaultdict(int)
    for (a, b) in edge_weight:
        degree[a] += 1
        degree[b] += 1
    edges = sorted(((w, a, b) for (a, b), w in edge_weight.items()), key=lambda x: (-x[0], x[1], x[2]))
    return dict(degree), edges


# --------------------------------------------------------------------------- header
def hdr(title: str, baseline: str, head: str, answers: str) -> str:
    return (
        f"# {title}\n\n"
        f"> PROGRAM UAKOS-CLOSURE-002 · PHASE-002 · Phase-001 baseline `{baseline}` · "
        f"HEAD `{head}` · AUTHORITY = NONE (DERIVED TRUTH) · generated by `phase2_engine.py`\n>\n"
        f"> Reuses `closure.json` (concept truth) + `00-BOOK/DATA/relationships.json` "
        f"(canonical graph). No re-extraction, no fabrication, fail-closed.\n>\n"
        f"> {answers}\n\n"
    )


# --------------------------------------------------------------------------- emit
def emit(model: dict, concepts: list[dict], graph: dict) -> tuple[list[Path], dict]:
    baseline = model.get("baseline_commit", "?")
    head = _run(["git", "rev-parse", "--short", "HEAD"]).strip() or baseline
    written: list[Path] = []

    def w(name: str, body: str) -> None:
        p = HERE / name
        p.write_text(body.rstrip() + "\n", "utf-8")
        written.append(p)

    total = len(concepts)
    homed = [r for r in concepts if r["homed"]]
    unhomed = [r for r in concepts if not r["homed"]]
    fam_counts = Counter(r["family"] for r in concepts)
    disp_counts = Counter(r["disposition"] for r in concepts)
    degree, edges = build_cooccurrence(concepts)

    # ---- 20 Canonical Concept Register
    rows = [[r["id"], r["family"], r["disposition"], "yes" if r["homed"] else "**NO**",
             len(r["exact_homes"]) or len(r["def_homes"]), len(r["files"])] for r in concepts]
    w("20-CANONICAL-CONCEPT-REGISTER.md",
      hdr("20 — Canonical Concept Register", baseline, head,
          "Every canonical concept anchor, its family, disposition, and canonical-home count.") +
      f"Distinct canonical concepts: **{total}** · homed: **{len(homed)}** · "
      f"unhomed (gaps): **{len(unhomed)}**.\n\n"
      "One row = one canonical concept (Knowledge Once: each ID exists once). Source: `closure.json`.\n\n" +
      _fence(rows, ["Concept", "Family", "Disposition", "Homed", "#Homes", "#Evidence files"]))

    # ---- 21 Concept Normalization Register
    fam_rows = [[k, v] for k, v in sorted(fam_counts.items())]
    w("21-CONCEPT-NORMALIZATION-REGISTER.md",
      hdr("21 — Concept Normalization Register", baseline, head,
          "The deterministic normalization rules applied to raw anchors (Phase 2.2).") +
      "Normalization is performed by `closure_engine.py` and reused verbatim here (no re-normalization):\n\n"
      "- **Family assignment** — each anchor is bucketed by the curated ID-namespace regex family "
      "(UCKO, UKDA-DEC, ARCH, MEP, MCP, MCS, CEP, DATA/SERVICE/APPLICATION/INFRASTRUCTURE/PLATFORM/RUNTIME, "
      "UCOS-COMP/GOV/EXEC/RAT/RECON, EPIC, GOV, METACLASS, BAND-UNIT, EC3-GATE, FOUNDATION, LAW, PHASE).\n"
      "- **Sentinel exclusion** — wildcard/example IDs (`…-99`, `…-999`, `…-U99`) are not real concepts and are dropped.\n"
      "- **Canonical-home matching** — an ID is homed when its uppercased form is the basename (or basename "
      "prefix) of a truth-root file, or it appears in a definitional location / implementation / UKDA store.\n"
      "- **Boundary (fail-closed, Charter §5)** — free-text prose concepts carrying no canonical ID are NOT "
      "invented into records; they are left for human canonicalization. PHASE-002 inherits this boundary.\n\n"
      f"Normalized distinct concepts: **{total}**, across **{len(fam_counts)}** families.\n\n" +
      _fence(fam_rows, ["Family", "Normalized concepts"]))

    # ---- 22 Canonical Home Register
    home_rows = []
    for r in concepts:
        home = "; ".join(sorted(r["exact_homes"] or r["def_homes"]))[:150] or (
            "(non-filename home)" if r["homed"] else "**NO CANONICAL HOME**")
        home_rows.append([r["id"], "yes" if r["homed"] else "**NO**", home_kinds(r), home])
    w("22-CANONICAL-HOME-REGISTER.md",
      hdr("22 — Canonical Home Register", baseline, head,
          "The one canonical home (or absence of home) for every concept (Phase 2.3 matching).") +
      f"Homed: **{len(homed)}** / **{total}**. Unhomed (must reach 0): **{len(unhomed)}**.\n\n"
      "A concept is *homed* when it has a definitional presence in Repository Truth (filename / code / "
      "constitution / catalog / spec / UKDA store). Unhomed concepts are closure violations.\n\n" +
      _fence(home_rows, ["Concept", "Homed", "Home kind(s)", "Canonical home file(s)"]))

    # ---- 23 Semantic Equivalence Matrix
    id_home_collisions = [r for r in concepts if len(r["exact_homes"]) > 1]
    w("23-SEMANTIC-EQUIVALENCE-MATRIX.md",
      hdr("23 — Semantic Equivalence Matrix", baseline, head,
          "Deterministic concept-equivalence classes (Phase 2.3/2.4).") +
      "Equivalence is decided **only** by canonical ID identity — the repository's own exists-once "
      "mechanism. Each distinct ID is its own equivalence class with exactly one intended canonical home.\n\n"
      "- Equivalence classes (distinct IDs): **" + str(total) + "**\n"
      "- Classes with >1 canonical home (equivalence collisions — must be 0): **" +
      str(len(id_home_collisions)) + "**\n\n"
      "**Boundary (Charter §5, fail-closed):** no natural-language / embedding semantic matching is performed. "
      "ID-less prose concepts are not equated by inference; doing so would fabricate equivalence. Therefore "
      "the only equivalence asserted is deterministic ID identity.\n\n" +
      (_fence([[r["id"], "; ".join(sorted(r["exact_homes"]))] for r in id_home_collisions],
              ["Concept", "Colliding homes"]) if id_home_collisions
       else "_No equivalence collisions — every canonical ID maps to at most one exact canonical home._"))

    # ---- 24 Duplicate Concept Report
    g = model["gaps"]
    dup_homes = model["detail"]["duplicate_homes"]
    hash_dups = model["detail"]["ukda_hash_duplicates"]
    w("24-DUPLICATE-CONCEPT-REPORT.md",
      hdr("24 — Duplicate Concept Report", baseline, head,
          "Concepts violating Knowledge Once via >1 canonical home or duplicate content (Phase 2.4).") +
      f"- Concepts with >1 filename home: **{g['duplicate_canonical_homes']}**\n"
      f"- UKDA content-hash duplicates: **{g['ukda_content_hash_duplicates']}**\n\n"
      "Cross-reference: `07-DUPLICATE-KNOWLEDGE-REPORT.md` (Phase-001 canonical source of this metric; "
      "not duplicated here — this output reconciles it at the concept level).\n\n" +
      (_fence([[r["id"], "; ".join(sorted(r["exact_homes"]))] for r in dup_homes],
              ["Concept", "Duplicate homes"]) if dup_homes else
       "_Zero duplicate canonical homes — Knowledge Once holds at the concept level._") +
      "\n\n" +
      (_fence([[d["content_sha256"][:16], ", ".join(d["ids"])] for d in hash_dups],
              ["content_sha256", "cko_ids"]) if hash_dups else
       "_Zero UKDA content-hash duplicates (UCKO-RULE-0001 holds)._"))

    # ---- 25 Concept Reconciliation Matrix
    gaps_only = [r for r in concepts if gap_class(r) not in ("HOMED",)]
    recon_action = {
        "IN-REPO-UNHOMED": "promote the mention into a definitional canonical home",
        "UPLOAD-ONLY": "canonicalize the uploaded concept into Repository Truth",
        "CONVERSATION-ONLY": "extract from corpus into a decision/spec, then home",
        "ORPHAN": "attach traceability (constitution/spec/impl) or archive with rationale",
        "UNCLASSIFIED": "assign a canonical home + disposition (no sixth state)",
    }
    w("25-CONCEPT-RECONCILIATION-MATRIX.md",
      hdr("25 — Concept Reconciliation Matrix", baseline, head,
          "Per-concept reconciliation state and required action (Phase 2.4).") +
      f"Reconciled (homed, no action): **{len(homed)}** / **{total}**. "
      f"Open reconciliation items: **{len(gaps_only)}**.\n\n"
      "## Open reconciliation items\n\n" +
      (_fence([[r["id"], r["family"], ", ".join(sorted(r["zones"])), gap_class(r),
                recon_action.get(gap_class(r), "review")] for r in gaps_only],
              ["Concept", "Family", "Zones", "State", "Required reconciliation"]) if gaps_only
       else "_None — every concept is reconciled to a canonical home._") +
      "\n\n## Disposition rollup (reconciled concepts)\n\n" +
      _fence([[k, v] for k, v in sorted(disp_counts.items())], ["Disposition", "Concepts"]))

    # ---- 26 Concept Traceability Matrix
    tr = lambda r, k: "✓" if r["trace"][k] else "·"
    full_chain = [r for r in concepts if all(r["trace"][k] for k in
                  ("constitution", "specification", "implementation", "certification"))]
    w("26-CONCEPT-TRACEABILITY-MATRIX.md",
      hdr("26 — Concept Traceability Matrix", baseline, head,
          "Source→Constitution→Spec→Impl→Cert traceability per concept (Phase 2.5).") +
      "Reuses the Phase-001 trace tiers (see `05-VISION-TO-REPOSITORY-MATRIX.md`); reconciled at concept level.\n\n"
      + _fence([
          ["source", sum(1 for r in concepts if r["trace"]["source"])],
          ["constitution", sum(1 for r in concepts if r["trace"]["constitution"])],
          ["specification", sum(1 for r in concepts if r["trace"]["specification"])],
          ["implementation", sum(1 for r in concepts if r["trace"]["implementation"])],
          ["certification", sum(1 for r in concepts if r["trace"]["certification"])],
      ], ["Trace tier", "Concepts with tier"]) +
      f"\n\nConcepts with a full constitution→spec→impl→cert chain: **{len(full_chain)}** / **{total}**.\n\n"
      "## Full matrix\n\n" +
      _fence([[r["id"], tr(r, "source"), tr(r, "constitution"), tr(r, "specification"),
               tr(r, "implementation"), tr(r, "certification")] for r in concepts],
             ["Concept", "Source", "Constitution", "Spec", "Impl", "Cert"]))

    # ---- 27 Concept Coverage Matrix
    fam_disp: dict[str, Counter] = defaultdict(Counter)
    for r in concepts:
        fam_disp[r["family"]][r["disposition"]] += 1
    disp_order = ["IMPLEMENTED", "SPECIFIED", "PLANNED", "DEFERRED", "REJECTED", "UNCLASSIFIED"]
    cov_rows = []
    for fam in sorted(fam_disp):
        c = fam_disp[fam]
        homed_n = sum(1 for r in concepts if r["family"] == fam and r["homed"])
        tot = sum(c.values())
        cov_rows.append([fam, *[c.get(d, 0) for d in disp_order], f"{homed_n}/{tot}"])
    w("27-CONCEPT-COVERAGE-MATRIX.md",
      hdr("27 — Concept Coverage Matrix", baseline, head,
          "Family × disposition coverage and homed ratio (Phase 2.8).") +
      f"Overall homed coverage: **{len(homed)}/{total}** "
      f"({100 * len(homed) // total if total else 0}%).\n\n" +
      _fence(cov_rows, ["Family", *disp_order, "Homed/Total"]))

    # ---- 28 Knowledge Graph
    top_nodes = sorted(degree.items(), key=lambda kv: (-kv[1], kv[0]))[:40]
    w("28-KNOWLEDGE-GRAPH.md",
      hdr("28 — Knowledge Graph", baseline, head,
          "Concept-level co-occurrence graph + reference to the canonical typed graph (Phase 2.6).") +
      "### Canonical typed graph (authoritative, reused not rebuilt)\n\n"
      f"`00-BOOK/DATA/relationships.json` present: **{graph['present']}** — "
      f"**{graph['count']}** typed edges. Edge types:\n\n" +
      (_fence([[k, v] for k, v in graph["edge_types"].items()], ["Edge type", "Count"])
       if graph["present"] else "_Canonical graph not found._") +
      "\n\n### Concept co-occurrence graph (derived from `closure.json` evidence files)\n\n"
      "Edges are evidence-backed: two concepts share an edge when they are defined/mentioned in the same "
      "file. This is a deterministic projection, **not** a competing canonical store.\n\n"
      f"- Concept nodes: **{total}** · co-occurrence edges: **{len(edges)}** · "
      f"isolated concepts (degree 0): **{total - len(degree)}**\n\n"
      "#### Highest-degree concepts\n\n" +
      _fence([[cid, deg] for cid, deg in top_nodes], ["Concept", "Co-occurrence degree"]))

    # ---- 29 Concept Dependency Graph
    dep_types = {k: graph["edge_types"].get(k, 0) for k in
                 ("Depends-On", "Required-By", "Consumes", "Consumed-By", "Implements", "Implemented-By")}
    w("29-CONCEPT-DEPENDENCY-GRAPH.md",
      hdr("29 — Concept Dependency Graph", baseline, head,
          "Dependency edges reused from the canonical graph (Phase 2.6).") +
      "PHASE-002 does not invent dependency edges. Dependency relationships are **reused** from the "
      "repository's canonical relationship store `00-BOOK/DATA/relationships.json` (artifact-level, "
      "authoritative). The dependency-bearing edge classes are:\n\n" +
      _fence([[k, v] for k, v in dep_types.items()], ["Dependency edge type", "Count"]) +
      "\n\nConcept-anchor IDs and artifact Universal-IDs are distinct namespaces; PHASE-002 references the "
      "canonical dependency edges rather than fabricating an anchor↔artifact bridge (fail-closed). "
      "Concept adjacency is provided via co-occurrence in `28-KNOWLEDGE-GRAPH.md`.")

    # ---- 30 Concept Relationship Graph
    w("30-CONCEPT-RELATIONSHIP-GRAPH.md",
      hdr("30 — Concept Relationship Graph", baseline, head,
          "Full typed-relationship view reused from the canonical graph (Phase 2.6).") +
      f"Authoritative typed relationships (`relationships.json`): **{graph['count']}** edges across "
      f"**{len(graph['edge_types'])}** relationship types.\n\n" +
      (_fence([[k, v] for k, v in graph["edge_types"].items()], ["Relationship type", "Count"])
       if graph["present"] else "_Canonical graph not found._") +
      "\n\nThis output reconciles PHASE-002 concepts against the existing typed graph; it does not create a "
      "second relationship store (Knowledge Once). Concept-level clustering is captured as co-occurrence in "
      "output 28.")

    # ---- 31 Concept Ownership Register
    owners = Counter(owner_of(r) for r in concepts)
    own_rows = [[r["id"], r["family"], owner_of(r), r["disposition"]] for r in concepts]
    w("31-CONCEPT-OWNERSHIP-REGISTER.md",
      hdr("31 — Concept Ownership Register", baseline, head,
          "The owning program/zone for every concept, derived from its canonical home.") +
      "Ownership = the top-level Repository-Truth zone of the concept's canonical home (or primary "
      "non-source evidence zone when the home is non-filename).\n\n## Owners\n\n" +
      _fence([[k, v] for k, v in sorted(owners.items(), key=lambda kv: (-kv[1], kv[0]))],
             ["Owning zone/program", "Concepts"]) +
      "\n\n## Per-concept ownership\n\n" +
      _fence(own_rows, ["Concept", "Family", "Owner", "Disposition"]))

    # ---- 32 Conversation / Upload Reconciliation
    conv = model["detail"]["conversation_only"]
    upl = model["detail"]["upload_only"]
    iru = model["detail"]["in_repo_unhomed"]
    src = model["sources"]
    w("32-CONVERSATION-UPLOAD-RECONCILIATION.md",
      hdr("32 — Conversation & Upload Reconciliation", baseline, head,
          "Reconciliation of conversation-only and upload-only knowledge (Phase 2.7).") +
      f"- Conversation-only concepts (external corpus only): **{len(conv)}**\n"
      f"- Upload-only concepts (`00-SOURCE`/root uploads only): **{len(upl)}**\n"
      f"- In-repo-unhomed concepts (mentioned in repo, incl. uploads, but not homed): **{len(iru)}**\n"
      f"- External corpus scanned present: **{src['corpus_present']}** — anchor-bearing corpus files: "
      f"**{src['corpus_files']}**\n\n"
      "**Fail-closed disclosure:** the external corpus scan surfaced **" + str(src["corpus_files"]) +
      "** anchor-bearing files. Where the corpus was skipped or contained no canonical anchors, "
      "conversation-ingestion completeness is **UNPROVEN** (absence disclosed, not asserted complete), "
      "consistent with Phase-001 Gap G-05.\n\n"
      "## In-repo-unhomed (upload/mention originated) concepts requiring canonicalization\n\n" +
      (_fence([[r["id"], r["family"], "; ".join(sorted(r["files"]))[:160]] for r in iru],
              ["Concept", "Family", "Where it currently lives"]) if iru
       else "_None._"))

    # ---- 33 Concept Enrichment Register (PLAN ONLY)
    enrich_rows = []
    for r in iru:
        enrich_rows.append([r["id"], r["family"], "IN-REPO-UNHOMED",
                            "; ".join(sorted(r["files"]))[:120],
                            "02-MASTER/ or 00-BOOK/REGISTRIES/ definitional home", "P1"])
    for r in upl:
        enrich_rows.append([r["id"], r["family"], "UPLOAD-ONLY",
                            "; ".join(sorted(r["source_only_files"]))[:120],
                            "canonicalize into Repository Truth", "P2"])
    for r in conv:
        enrich_rows.append([r["id"], r["family"], "CONVERSATION-ONLY",
                            "; ".join(sorted(r["corpus_files"]))[:120],
                            "extract from corpus into decision/spec", "P3"])
    for r in model["detail"]["orphans"]:
        enrich_rows.append([r["id"], r["family"], "ORPHAN", "homed, no traceability",
                            "attach traceability or archive", "P4"])
    w("33-CONCEPT-ENRICHMENT-REGISTER.md",
      hdr("33 — Concept Enrichment Register", baseline, head,
          "Deterministic enrichment PLAN for every open gap (Phase 2.10). PLAN ONLY — never auto-applied.") +
      "**This is a plan, not an action.** PHASE-002 never mutates Repository Truth automatically "
      "(Charter §1; mission directive 'Never implement automatically'). Each row routes one open gap to "
      "exactly one canonical destination; execution is separately authorized.\n\n"
      f"Open enrichment items: **{len(enrich_rows)}**.\n\n" +
      (_fence([[i + 1, *row] for i, row in enumerate(enrich_rows)],
              ["#", "Concept", "Family", "Gap class", "Current location", "Canonical destination", "Priority"])
       if enrich_rows else "_Enrichment register empty — zero open gaps at this baseline._") +
      "\n\nCross-reference: `09-REPOSITORY-ENRICHMENT-PLAN.md` (Phase-001 plan) and "
      "`10-CONSTITUTIONAL-GAP-REGISTER.md` (backlog).")

    # ---- 34 Closure & Universal Dashboard
    homed_pct = 100 * len(homed) // total if total else 0
    trace_impl = sum(1 for r in concepts if r["trace"]["implementation"])
    trace_cert = sum(1 for r in concepts if r["trace"]["certification"])
    w("34-CLOSURE-AND-UNIVERSAL-DASHBOARD.md",
      hdr("34 — Closure & Universal Dashboard", baseline, head,
          "Single-pane rollup of concept-graph closure and universal coverage.") +
      "## Closure Dashboard\n\n" +
      _fence([
          ["Determination", model["determination"]],
          ["Total blocking gaps", model["gap_total"]],
          ["Concepts", total],
          ["Homed", f"{len(homed)} ({homed_pct}%)"],
          ["Unhomed (gaps)", len(unhomed)],
          ["Duplicate canonical homes", g["duplicate_canonical_homes"]],
          ["UKDA content-hash duplicates", g["ukda_content_hash_duplicates"]],
          ["Orphan concepts", g["orphan_concepts"]],
          ["Conversation-only", g["conversation_only"]],
          ["Upload-only", g["upload_only"]],
      ], ["Metric", "Value"]) +
      "\n\n## Universal Coverage Dashboard\n\n" +
      _fence([[k, v] for k, v in sorted(disp_counts.items())], ["Disposition", "Concepts"]) +
      "\n\n" +
      _fence([
          ["Families covered", len(fam_counts)],
          ["Implementation-traced concepts", trace_impl],
          ["Certification-traced concepts", trace_cert],
          ["Canonical typed graph edges", graph["count"]],
          ["Concept co-occurrence edges", len(edges)],
      ], ["Coverage metric", "Value"]))

    # ---- 35 Phase-002 Completeness Determination (fail-closed)
    closed = model["determination"] == "CLOSED" and len(unhomed) == 0
    verdict = "CLOSED — concept-graph reconciliation complete" if closed else \
              f"FAIL-CLOSED — NOT CLOSED ({model['gap_total']} blocking gap(s))"
    seal = hashlib.sha256(json.dumps(
        {"phase": "PHASE-002", "baseline": baseline, "gaps": model["gaps"],
         "concepts": total, "homed": len(homed)}, sort_keys=True).encode()).hexdigest()
    crit = [
        ["Every concept normalized & registered", "PASS" if total > 0 else "FAIL"],
        ["Every concept has exactly one canonical home", "PASS" if len(unhomed) == 0 else "FAIL"],
        ["Zero duplicate canonical concepts",
         "PASS" if g["duplicate_canonical_homes"] == 0 and g["ukda_content_hash_duplicates"] == 0 else "FAIL"],
        ["Zero orphan concepts", "PASS" if g["orphan_concepts"] == 0 else "FAIL"],
        ["Zero conversation-only knowledge", "PASS" if g["conversation_only"] == 0 else "FAIL"],
        ["Zero upload-only knowledge", "PASS" if g["upload_only"] == 0 else "FAIL"],
        ["Zero in-repo-unhomed knowledge", "PASS" if g["in_repo_unhomed"] == 0 else "FAIL"],
        ["Knowledge graph reconciled (canonical graph reused)",
         "PASS" if graph["present"] else "FAIL"],
    ]
    w("35-PHASE-002-COMPLETENESS-DETERMINATION.md",
      hdr("35 — PHASE-002 Completeness Determination", baseline, head,
          "The fail-closed verdict for concept extraction, matching, and graph reconciliation.") +
      f"| Field | Value |\n|---|---|\n"
      f"| Program | UAKOS-CLOSURE-002 · PHASE-002 |\n"
      f"| Phase-001 baseline | `{baseline}` |\n"
      f"| Determination | **{verdict}** |\n"
      f"| Concepts | {total} · homed {len(homed)} · unhomed {len(unhomed)} |\n"
      f"| Seal (sha256) | `{seal}` |\n"
      f"| Authority | NONE — DERIVED TRUTH (fail-closed, TRACK-001) |\n\n"
      "## Success criteria\n\n" + _fence(crit, ["Criterion", "Status"]) + "\n\n" +
      ("All concept-level closure invariants hold. Concept-graph reconciliation is **COMPLETE**."
       if closed else
       f"**Determination withheld (fail-closed).** {len(unhomed)} concept(s) have no canonical home "
       "and the Phase-001 machine determination is NOT-CLOSED. Per the mission's constitutional directives "
       "(evidence precedes certification; broken traceability fails closure), PHASE-002 cannot certify "
       "concept closure while gaps remain. See `33-CONCEPT-ENRICHMENT-REGISTER.md` for the remediation plan "
       "and `19-REPOSITORY-TRUTH-DETERMINATION.md` for the Phase-001 rollup. Re-run `make closure && "
       "make closure-phase2` after enrichment; this determination self-certifies when gaps reach zero.") +
      "\n\n### Open gaps\n\n```json\n" + json.dumps(model["gaps"], indent=2, sort_keys=True) + "\n```")

    # ---- machine model
    phase2 = {
        "program": "UAKOS-CLOSURE-002",
        "phase": "PHASE-002",
        "baseline_commit": baseline,
        "head_commit": head,
        "authority": "NONE-DERIVED-TRUTH",
        "determination": "CLOSED" if closed else "NOT-CLOSED",
        "gap_total": model["gap_total"],
        "gaps": model["gaps"],
        "concept_total": total,
        "homed": len(homed),
        "unhomed": len(unhomed),
        "dispositions": dict(sorted(disp_counts.items())),
        "families": dict(sorted(fam_counts.items())),
        "canonical_graph": {"source": "00-BOOK/DATA/relationships.json",
                            "present": graph["present"], "edges": graph["count"],
                            "edge_types": graph["edge_types"]},
        "cooccurrence": {"nodes": total, "edges": len(edges),
                         "isolated": total - len(degree)},
        "open_enrichment_items": len(enrich_rows),
        "seal_sha256": seal,
        "inputs": {"closure_json": "closure.json",
                   "relationships_json": "00-BOOK/DATA/relationships.json"},
        "reused_phase1_outputs": ["04", "05", "06", "07", "09", "10", "14", "19"],
    }
    (HERE / "phase2.json").write_text(
        json.dumps(phase2, indent=2, sort_keys=True, ensure_ascii=False) + "\n", "utf-8")
    return written, phase2


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    gate = "--gate" in argv
    model, concepts, graph = load_inputs()
    written, phase2 = emit(model, concepts, graph)
    print(f"UAKOS-CLOSURE-002 · PHASE-002: {phase2['determination']} | "
          f"concepts={phase2['concept_total']} homed={phase2['homed']} unhomed={phase2['unhomed']} "
          f"| gaps={phase2['gap_total']} {json.dumps(phase2['gaps'], sort_keys=True)}")
    print(f"wrote {len(written) + 1} artifacts to {HERE}")
    if gate and phase2["determination"] != "CLOSED":
        print("GATE FAILED: PHASE-002 concept closure NOT achieved (fail-closed).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
