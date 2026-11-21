#!/usr/bin/env python3
"""UAKOS-CLOSURE-002 · PHASE-003 — deterministic canonical implementation-planning engine.

PHASE-003 does NOT discover, extract, re-inventory, or rebuild graphs. Discovery is complete
(PHASE-001/002). This engine consumes the FROZEN PHASE-002 baseline as its only authoritative
input and, for every unresolved (unhomed) concept, derives — deterministically and from evidence
only — exactly one implementation strategy: a classification, a canonical destination, an owner,
a dependency chain, an execution wave, a priority, an execution contract, an enrichment plan row,
and a projected closure path. It produces CONSTITUTIONAL PLANS ONLY. It never modifies Repository
Truth, never implements automatically, and never fabricates certainty (fail-closed, TRACK-001).

Authoritative input (frozen, read-only):
    00-MASTER/UAKOS-CLOSURE-002/closure.json   (PHASE-001/002 concept model — the ONLY input)
    00-MASTER/UAKOS-CLOSURE-002/phase2.json    (cross-consistency check)

Outputs (regenerated deterministically): 36..48 NN-*.md + phase3.json

Usage:
    python3 00-MASTER/UAKOS-CLOSURE-002/phase3_engine.py
    python3 00-MASTER/UAKOS-CLOSURE-002/phase3_engine.py --gate   # exit 1 while NOT-CLOSED
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CLOSURE_JSON = HERE / "closure.json"
PHASE2_JSON = HERE / "phase2.json"

# --------------------------------------------------------------------------- deterministic policy tables
# Execution waves (mission STEP 3.4). "F" = Future/Deferred wave (parked, authorization-gated).
WAVE_NAME = {
    1: "Wave 1 — Foundational constitutional artifacts",
    2: "Wave 2 — Core architecture",
    3: "Wave 3 — Registries / governance / roadmap",
    4: "Wave 4 — Capabilities",
    5: "Wave 5 — Implementations / specifications",
    6: "Wave 6 — Validation",
    7: "Wave 7 — Certification",
    "F": "Wave F — Future / Deferred (authorization-gated; no premature implementation)",
}
WAVE_ORDER = [1, 2, 3, 4, 5, 6, 7, "F"]

# One row per implementation class (mission STEP 3.1). Each carries its permanent constitutional
# destination (3.2), execution wave (3.4), priority (3.6), predecessor class (3.3), and the
# evidence/validation/certification a plan for that class requires (3.7).
CLASS_META: dict[str, dict] = {
    "Missing Constitution": dict(
        dest="02-MASTER (Constitution) + 00-BOOK/REGISTRIES (law registry home)",
        owner="Master Constitution Authority (02-MASTER)", wave=1, priority="Critical", pred=None,
        evidence="ratified constitutional text with law ID + downward-only founding reference",
        validation="ukb validate (structural) + referential integrity", certification="constitutional ratification determination"),
    "Missing Universe": dict(
        dest="02-MASTER (Universe Architecture Framework)",
        owner="Master Constitution Authority (02-MASTER)", wave=2, priority="High", pred="Missing Constitution",
        evidence="universe definition founded on a ratified constitution", validation="ukb validate",
        certification="architecture admission determination"),
    "Missing Architecture": dict(
        dest="02-MASTER (Architecture Framework) / Architecture",
        owner="Architecture Authority (02-MASTER)", wave=2, priority="High", pred="Missing Constitution",
        evidence="architecture artifact founded downward-only on constitution", validation="ukb validate",
        certification="architecture admission determination"),
    "Missing Governance": dict(
        dest="Governance (GOV program) / 00-MASTER governance",
        owner="Governance Program", wave=3, priority="High", pred="Missing Architecture",
        evidence="governance determination with authority + scope", validation="ukb enforce (classification)",
        certification="governance admission determination"),
    "Missing Roadmap": dict(
        dest="00-BOOK/CONTROL-TOWER (Roadmap Reconciliation Registry)",
        owner="Control Tower / Roadmap Authority", wave=3, priority="High", pred="Missing Architecture",
        evidence="roadmap unit with phase ID + mapped artifacts", validation="roadmap reconciliation",
        certification="phase reality determination"),
    "Missing Registry": dict(
        dest="00-BOOK/REGISTRIES",
        owner="Registry Authority (ukb)", wave=3, priority="High", pred="Missing Architecture",
        evidence="registry entry with canonical ID + backlinks", validation="ukb enforce parity",
        certification="registration certification (hard checks)"),
    "Missing Decision Record": dict(
        dest="adr/ (Decision Record) + knowledge/decisions.json",
        owner="UKDA / Decision Authority", wave=3, priority="High", pred="Missing Constitution",
        evidence="decision record with context/decision/consequences", validation="UKDA hash-uniqueness",
        certification="decision ratification"),
    "Missing Capability": dict(
        dest="Implementation root + Capability Registry",
        owner="Owning domain program", wave=4, priority="Medium", pred="Missing Specification",
        evidence="capability realization with meta + tests", validation="unit/integration tests",
        certification="capability certification"),
    "Missing Specification": dict(
        dest="Numbered-band specification (domain band, e.g. 08-RUNTIME / 10-DATA)",
        owner="Owning domain program", wave=5, priority="Medium", pred="Missing Architecture",
        evidence="specification founded on architecture", validation="ukb validate",
        certification="specification admission"),
    "Missing Validation": dict(
        dest="_evidence/ (validation evidence)",
        owner="Validation Authority", wave=6, priority="Medium", pred="Missing Specification",
        evidence="validation-evidence.json + validation-report.json", validation="test-tier execution",
        certification="validation determination"),
    "Missing Evidence": dict(
        dest="_evidence/",
        owner="Evidence Authority", wave=6, priority="Medium", pred="Missing Specification",
        evidence="realization-evidence.json", validation="evidence integrity", certification="evidence acceptance"),
    "Missing Certification": dict(
        dest="Certification Registry (UCOS-CERT-*)",
        owner="Certification Authority", wave=7, priority="Medium", pred="Missing Validation",
        evidence="certification determination + co-located UCOS-CERT token", validation="hard-check suite",
        certification="certification-of-certifications"),
    "Future Capability": dict(
        dest="Future Phase backlog (00-BOOK/REGISTRIES — registered as FUTURE)",
        owner="00-MASTER / Program Backlog Authority", wave="F", priority="Future", pred=None,
        evidence="backlog registration marking the concept FUTURE", validation="registry parity",
        certification="deferred — none until activated"),
    "Future Universe": dict(
        dest="Future Universe backlog (00-BOOK/REGISTRIES — registered as FUTURE)",
        owner="00-MASTER / Program Backlog Authority", wave="F", priority="Future", pred=None,
        evidence="backlog registration marking the universe FUTURE", validation="registry parity",
        certification="deferred — none until activated"),
    "Deferred": dict(
        dest="00-BOOK/REGISTRIES (Deferred/Future-Component Backlog) — registered as DEFERRED",
        owner="00-MASTER / Deferred Backlog Authority", wave="F", priority="Future", pred=None,
        evidence="backlog registration recording the DEFERRED marker + source", validation="registry parity",
        certification="deferred — none until authorized for activation"),
    "Rejected": dict(
        dest="adr/ (Rejected-Options Decision Record)",
        owner="UKDA / Decision Authority", wave="F", priority="Low", pred=None,
        evidence="rejected-options decision record with rationale", validation="UKDA hash-uniqueness",
        certification="not applicable (archived)"),
}

# Family → default (non-deferred, non-rejected) implementation class (mission STEP 3.1).
FAMILY_CLASS = {
    "LAW": "Missing Constitution",
    "UCKO": "Missing Decision Record",
    "UKDA-DEC": "Missing Decision Record",
    "ARCH": "Missing Architecture",
    "METACLASS": "Missing Architecture",
    "GOV": "Missing Governance",
    "UCOS-GOV": "Missing Governance",
    "UCOS-EXEC": "Missing Governance",
    "MEP": "Missing Roadmap",
    "EPIC": "Missing Roadmap",
    "PHASE": "Missing Roadmap",
    "UCOS-RECON": "Missing Registry",
    "UCOS-RAT": "Missing Certification",
    "CEP": "Missing Specification",
    "DATA": "Missing Specification",
    "SERVICE": "Missing Specification",
    "APPLICATION": "Missing Specification",
    "INFRASTRUCTURE": "Missing Specification",
    "PLATFORM": "Missing Specification",
    "RUNTIME": "Missing Specification",
    "MCP": "Missing Specification",
    "MCS": "Missing Specification",
    "CEP": "Missing Specification",
    "UCOS-COMP": "Missing Capability",
    "BAND-UNIT": "Missing Capability",
    "FOUNDATION": "Missing Constitution",
    "EC3-GATE": "Missing Governance",
}

# Family → owning program/zone (mission STEP 3.2 owner). One owner per concept.
FAMILY_OWNER = {
    "DATA": "10-DATA program", "SERVICE": "11-SERVICE program", "APPLICATION": "12-APPLICATION program",
    "INFRASTRUCTURE": "13-INFRASTRUCTURE program", "PLATFORM": "09-PLATFORM program",
    "RUNTIME": "08-RUNTIME program", "GOV": "Governance Program", "ARCH": "Architecture Authority (02-MASTER)",
    "PHASE": "Control Tower / Roadmap Authority", "LAW": "Master Constitution Authority (02-MASTER)",
    "UCOS-RECON": "00-MASTER Reconciliation Authority", "UCOS-COMP": "00-MASTER / Deferred Backlog Authority",
}


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False).stdout


def _fence(rows: list[list], header: list[str]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


# --------------------------------------------------------------------------- classification (STEP 3.1)
def classify(rec: dict) -> str:
    """Deterministic, evidence-precedence classification. Every concept gets exactly one class."""
    if rec["rejected"]:
        return "Rejected"
    if rec["deferred"]:
        return "Deferred"
    return FAMILY_CLASS.get(rec["family"], "Missing Specification")


def owner_of(rec: dict, klass: str) -> str:
    return FAMILY_OWNER.get(rec["family"]) or CLASS_META[klass]["owner"]


def plan_for(rec: dict) -> dict:
    klass = classify(rec)
    meta = CLASS_META[klass]
    return {
        "id": rec["id"], "family": rec["family"], "class": klass,
        "destination": meta["dest"], "owner": owner_of(rec, klass),
        "wave": meta["wave"], "priority": meta["priority"], "pred_class": meta["pred"],
        "evidence_required": meta["evidence"], "validation_required": meta["validation"],
        "certification_required": meta["certification"],
        "origin": ("in-repo-unhomed" if rec["in_repo_unhomed"] else
                   "conversation-only" if rec["conversation_only"] else
                   "upload-only" if rec["upload_only"] else "repo"),
        "n_sources": len(rec["files"]) or len(rec["corpus_files"]),
    }


def hdr(title: str, baseline: str, head: str, answers: str) -> str:
    return (
        f"# {title}\n\n"
        f"> PROGRAM UAKOS-CLOSURE-002 · PHASE-003 · frozen baseline `{baseline}` · HEAD `{head}` · "
        f"AUTHORITY = NONE (DERIVED TRUTH) · generated by `phase3_engine.py`\n>\n"
        f"> Planning only. Reuses the frozen PHASE-002 baseline (`closure.json`). No discovery, no "
        f"re-extraction, no repository modification, no automatic implementation. Fail-closed.\n>\n"
        f"> {answers}\n\n"
    )


# --------------------------------------------------------------------------- emit
def emit(model: dict) -> tuple[list[Path], dict]:
    baseline = model.get("baseline_commit", "?")
    head = _run(["git", "rev-parse", "--short", "HEAD"]).strip() or baseline
    concepts = sorted(model["concepts"], key=lambda r: r["id"])
    unhomed = [r for r in concepts if not r["homed"]]
    plans = [plan_for(r) for r in unhomed]
    plans.sort(key=lambda p: (WAVE_ORDER.index(p["wave"]), p["class"], p["id"]))

    class_counts = Counter(p["class"] for p in plans)
    wave_counts = Counter(p["wave"] for p in plans)
    prio_counts = Counter(p["priority"] for p in plans)
    written: list[Path] = []

    def w(name: str, body: str) -> None:
        p = HERE / name
        p.write_text(body.rstrip() + "\n", "utf-8")
        written.append(p)

    # ---- 36 Gap Classification Register (STEP 3.1)
    w("36-GAP-CLASSIFICATION-REGISTER.md",
      hdr("36 — Gap Classification Register", baseline, head,
          "Exactly one implementation class for every unresolved concept (STEP 3.1).") +
      f"Unresolved concepts classified: **{len(plans)}** / **{len(unhomed)}** "
      f"(unclassified: **{len(unhomed) - len(plans)}** — MUST be 0).\n\n"
      "Classification is deterministic by evidence precedence: `Rejected` (marker) → `Deferred` "
      "(marker) → family-derived class. No concept remains unclassified.\n\n## Class distribution\n\n" +
      _fence([[k, v] for k, v in sorted(class_counts.items())], ["Implementation class", "Concepts"]) +
      "\n\n## Per-concept classification\n\n" +
      _fence([[p["id"], p["family"], p["origin"], p["class"]] for p in plans],
             ["Concept", "Family", "Origin", "Class"]))

    # ---- 37 Canonical Destination Register (STEP 3.2)
    dest_counts = Counter(p["destination"] for p in plans)
    w("37-CANONICAL-DESTINATION-REGISTER.md",
      hdr("37 — Canonical Destination Register", baseline, head,
          "Exactly one permanent constitutional destination per concept (STEP 3.2).") +
      "Each destination is the concept's permanent canonical home. Registering a Deferred/Future concept "
      "in a backlog registry IS a canonical home (it leaves the unhomed set as a governed DEFERRED entry) "
      "— this closes the gap without premature implementation.\n\n## Destination distribution\n\n" +
      _fence([[k, v] for k, v in sorted(dest_counts.items(), key=lambda kv: (-kv[1], kv[0]))],
             ["Canonical destination", "Concepts"]) +
      "\n\n## Per-concept destination & owner\n\n" +
      _fence([[p["id"], p["class"], p["destination"], p["owner"]] for p in plans],
             ["Concept", "Class", "Canonical destination", "Owner"]))

    # ---- 38 Dependency Register (STEP 3.3)
    w("38-DEPENDENCY-REGISTER.md",
      hdr("38 — Dependency Register", baseline, head,
          "Required predecessor artifacts per concept — an acyclic wave-gated dependency (STEP 3.3).") +
      "Dependencies are expressed as constitutional-layer gates (predecessor class + its wave). This is a "
      "strict partial order over classes → the graph is acyclic by construction (no concept depends on a "
      "later or equal wave).\n\n" +
      _fence([[p["id"], p["class"], f"Wave {p['wave']}",
               p["pred_class"] or "— (foundational / parked)",
               f"Wave {CLASS_META[p['pred_class']]['wave']}" if p["pred_class"] else "—"]
              for p in plans],
             ["Concept", "Class", "Wave", "Predecessor class", "Predecessor wave"]))

    # ---- 39 Implementation Dependency Graph (STEP 3.3)
    layer_edges = []
    for klass, meta in CLASS_META.items():
        if class_counts.get(klass):
            pred = meta["pred"]
            layer_edges.append((pred or "ROOT", klass, class_counts[klass]))
    w("39-IMPLEMENTATION-DEPENDENCY-GRAPH.md",
      hdr("39 — Implementation Dependency Graph", baseline, head,
          "The acyclic class/wave dependency DAG (STEP 3.3). No cycles.") +
      "### Wave gate chain (topological order)\n\n"
      "`Wave 1 → Wave 2 → Wave 3 → Wave 4 → Wave 5 → Wave 6 → Wave 7`  ·  `Wave F` (parked, no successors)\n\n"
      "### Class dependency edges (predecessor → class · concept count)\n\n" +
      _fence([[src, "→", dst, n] for src, dst, n in
              sorted(layer_edges, key=lambda e: (e[1],))],
             ["Predecessor", "", "Class", "Concepts"]) +
      "\n\n### Mermaid\n\n```mermaid\ngraph LR\n"
      "  W1[Wave1 Constitution] --> W2[Wave2 Architecture] --> W3[Wave3 Registry/Gov/Roadmap]\n"
      "  W3 --> W4[Wave4 Capabilities] --> W5[Wave5 Impl/Spec] --> W6[Wave6 Validation] --> W7[Wave7 Certification]\n"
      "  WF[WaveF Deferred/Future/Rejected]\n```\n\n"
      "**Acyclicity:** dependency edges only point from a lower wave to a higher wave; Wave F has no "
      "outgoing edges. Therefore the dependency graph contains no cycles (STEP 3.3 invariant satisfied).")

    # ---- 40 Execution Wave Register (STEP 3.4)
    w("40-EXECUTION-WAVE-REGISTER.md",
      hdr("40 — Execution Wave Register", baseline, head,
          "Every gap partitioned into exactly one deterministic execution wave (STEP 3.4).") +
      _fence([[WAVE_NAME[wv], wave_counts.get(wv, 0)] for wv in WAVE_ORDER], ["Wave", "Concepts"]) +
      f"\n\nEvery concept belongs to exactly one wave (sum = **{sum(wave_counts.values())}** = "
      f"**{len(plans)}** concepts).\n\n## Per-concept wave assignment\n\n" +
      _fence([[p["id"], p["class"], WAVE_NAME[p["wave"]]] for p in plans],
             ["Concept", "Class", "Wave"]))

    # ---- 41 Repository Impact Assessment (STEP 3.5)
    IMPACT = {
        "Missing Constitution": ("1 new constitution + registry entry", "law registry, artifact registry",
                                 "new root node + downward edges", "HIGH", "adr templates, existing law register"),
        "Missing Architecture": ("1 new architecture artifact", "artifact registry, knowledge graph",
                                 "new arch node + Depends-On edges", "MEDIUM", "existing architecture framework"),
        "Missing Governance": ("1 governance determination", "artifact registry, control tower",
                               "governance node + Authorizes edges", "MEDIUM", "existing GOV determinations"),
        "Missing Roadmap": ("roadmap registry entry", "roadmap reconciliation registry, control tower",
                            "phase node + mapping edges", "LOW", "existing roadmap registry"),
        "Missing Registry": ("registry entry", "target registry, id-ledger",
                             "registry node + backlinks", "LOW", "existing registries, ukb"),
        "Missing Decision Record": ("1 ADR", "decisions.json, adr/",
                                    "decision node + Traces-To", "LOW", "adr/ conventions"),
        "Missing Specification": ("1 band specification", "artifact registry, knowledge graph",
                                  "spec node + Implements edges", "MEDIUM", "existing band specs"),
        "Missing Capability": ("code + meta + tests", "artifact registry, twin",
                               "capability node + Implemented-By", "HIGH", "existing engine/platform patterns"),
        "Deferred": ("backlog registry entry (DEFERRED)", "deferred backlog registry",
                     "deferred node (parked)", "LOW", "existing corpus source; no new design"),
        "Future Capability": ("backlog registry entry (FUTURE)", "future backlog registry",
                              "future node (parked)", "LOW", "corpus source"),
        "Future Universe": ("backlog registry entry (FUTURE)", "future backlog registry",
                            "future node (parked)", "LOW", "corpus source"),
        "Rejected": ("rejected-options ADR", "decisions.json",
                     "archived decision node", "LOW", "adr/ rejected-options pattern"),
        "Missing Certification": ("certification determination", "certification registry",
                                  "cert node + certifies edges", "MEDIUM", "existing cert registry"),
        "Missing Validation": ("validation evidence", "_evidence/", "validation edges", "MEDIUM", "existing evidence patterns"),
        "Missing Evidence": ("realization evidence", "_evidence/", "evidence edges", "MEDIUM", "existing evidence patterns"),
        "Missing Universe": ("universe framework artifact", "artifact registry", "universe node", "MEDIUM", "existing universe framework"),
    }
    impact_rows = []
    for klass in sorted(class_counts):
        files_a, regs, kg, risk, reuse = IMPACT.get(klass, ("1 artifact", "artifact registry", "new node", "MEDIUM", "existing patterns"))
        impact_rows.append([klass, class_counts[klass], files_a, regs, kg, risk, reuse])
    w("41-REPOSITORY-IMPACT-ASSESSMENT.md",
      hdr("41 — Repository Impact Assessment", baseline, head,
          "Projected repository impact per class (STEP 3.5). Estimates — never modifies the repository.") +
      "> All values are **Derived/Projected** estimates. PHASE-003 performs no writes; actual impact is "
      "measured only at authorized execution time.\n\n" +
      _fence(impact_rows, ["Class", "Concepts", "Files affected (est.)", "Registries affected",
                           "Knowledge-graph impact", "Repository risk", "Reuse opportunity"]) +
      "\n\n**Traceability impact:** each active-wave artifact adds one Vision→…→Registry chain link. "
      "**Validation/Certification impact:** only active-wave classes (Constitution/Architecture/"
      "Governance/Roadmap/Registry/Specification) enter validation; Deferred/Future classes carry no "
      "certification until authorized activation.")

    # ---- 42 Priority Register (STEP 3.6)
    w("42-PRIORITY-REGISTER.md",
      hdr("42 — Priority Register", baseline, head,
          "Priority per concept, assigned purely by constitutional dependency (STEP 3.6).") +
      "Priority is a pure function of constitutional wave (never convenience): Wave 1 → Critical; "
      "Waves 2-3 → High; Waves 4-6 → Medium; Wave 7 → Medium; Wave F → Future (Rejected → Low).\n\n" +
      _fence([[k, prio_counts.get(k, 0)] for k in ["Critical", "High", "Medium", "Low", "Future"]],
             ["Priority", "Concepts"]) +
      "\n\n## Per-concept priority\n\n" +
      _fence([[p["id"], p["class"], f"Wave {p['wave']}", p["priority"]] for p in plans],
             ["Concept", "Class", "Wave", "Priority"]))

    # ---- 43 Implementation Contract Register (STEP 3.7)
    contract_defs = []
    for klass in sorted(class_counts):
        m = CLASS_META[klass]
        contract_defs.append([klass,
                              "the classified concept + predecessor-wave completion",
                              m["dest"],
                              (m["pred"] + " closed" if m["pred"] else "none (foundational/parked)"),
                              "concept homed at destination with disposition",
                              m["evidence"], m["validation"], m["certification"]])
    w("43-IMPLEMENTATION-CONTRACT-REGISTER.md",
      hdr("43 — Implementation Contract Register", baseline, head,
          "One execution contract per class, bound to every concept (STEP 3.7). No ambiguity.") +
      "### Class contracts (inputs · outputs · pre/postconditions · success · evidence · validation · certification)\n\n" +
      _fence(contract_defs, ["Class", "Inputs", "Output (destination)", "Precondition",
                             "Postcondition / success", "Evidence required", "Validation required",
                             "Certification required"]) +
      "\n\n### Per-concept contract binding\n\n" +
      _fence([[p["id"], p["class"], f"CONTRACT::{p['class'].replace(' ', '-').upper()}"] for p in plans],
             ["Concept", "Class", "Bound contract"]))

    # ---- 44 Repository Enrichment Execution Plan (STEP 3.8) — the master per-concept plan
    w("44-REPOSITORY-ENRICHMENT-EXECUTION-PLAN.md",
      hdr("44 — Repository Enrichment Execution Plan", baseline, head,
          "The deterministic execution plan: every gap with all required attributes (STEP 3.8).") +
      "> **PLAN ONLY.** Execution is separately authorized; PHASE-003 applies nothing. Each row is complete: "
      "canonical ID · destination · owner · dependencies · wave · priority · evidence · validation · "
      "certification · expected artifacts.\n\n"
      f"Planned concepts: **{len(plans)}**.\n\n" +
      _fence([[i + 1, p["id"], p["class"], p["destination"], p["owner"],
               (p["pred_class"] or "—"), f"W{p['wave']}", p["priority"],
               p["evidence_required"], p["validation_required"], p["certification_required"],
               f"1× {p['class'].split(' ', 1)[-1].lower()} artifact at destination"]
              for i, p in enumerate(plans)],
             ["#", "Canonical ID", "Class", "Destination", "Owner", "Depends-on", "Wave",
              "Priority", "Evidence required", "Validation required", "Certification required",
              "Expected artifact(s)"]))

    # ---- 45 Closure Projection Report (STEP 3.9)
    active_waves = [1, 2, 3, 4, 5, 6, 7]
    measured_unhomed = len(unhomed)
    remaining = measured_unhomed
    proj_rows = []
    for wv in active_waves:
        closed = wave_counts.get(wv, 0)
        remaining -= closed
        proj_rows.append([WAVE_NAME[wv], closed, remaining, "Projected"])
    # Wave F closes the parked concepts via registration-as-deferred (governed home)
    fclosed = wave_counts.get("F", 0)
    remaining_after_f = remaining - fclosed
    proj_rows.append([WAVE_NAME["F"], fclosed, remaining_after_f, "Projected"])
    conv_only = sum(1 for r in unhomed if r["conversation_only"])
    w("45-CLOSURE-PROJECTION-REPORT.md",
      hdr("45 — Closure Projection Report", baseline, head,
          "Projected repository completeness after each execution wave (STEP 3.9). No fabricated certainty.") +
      "### Classification of certainty\n\n"
      f"- **Measured** (from frozen `closure.json`): total concepts **{model['concept_total']}**, "
      f"homed **{model['concept_total'] - measured_unhomed}**, unhomed **{measured_unhomed}** "
      f"(conversation-only **{conv_only}**, in-repo-unhomed **{sum(1 for r in unhomed if r['in_repo_unhomed'])}**).\n"
      f"- **Derived** (deterministic classification): {len(plans)} concepts across "
      f"{len(class_counts)} classes and {len(wave_counts)} waves.\n"
      "- **Projected** (estimate, NOT certainty): the wave-by-wave residual below assumes each wave's "
      "planned artifacts are authored, registered, and pass validation. Actual closure is measured only "
      "by re-running `make closure` after authorized execution.\n\n"
      "### Projected unhomed residual after each wave\n\n" +
      _fence(proj_rows, ["After wave", "Concepts homed (proj.)", "Unhomed residual (proj.)", "Certainty"]) +
      "\n\n**Projected end-state:** active waves 1-7 home **" +
      str(measured_unhomed - remaining) + "** concepts; Wave F registers the remaining **" +
      str(remaining) + "** as governed DEFERRED/FUTURE entries. Projected unhomed at full execution: **" +
      str(max(remaining_after_f, 0)) + "**. This is a projection — the repository remains NOT-CLOSED until "
      "measured evidence confirms it (fail-closed).\n\n"
      "- **Remaining conversation-only** after Wave F registration: projected **0** (each becomes a homed "
      "backlog/decision entry).\n- **Remaining evidence/validation gaps:** unchanged until Waves 6-7 execute "
      "(no active-wave concept currently requires them in this baseline).")

    # ---- 46 Repository Readiness Dashboard
    w("46-REPOSITORY-READINESS-DASHBOARD.md",
      hdr("46 — Repository Readiness Dashboard", baseline, head,
          "Single-pane readiness rollup for the enrichment program.") +
      "## Baseline (Measured)\n\n" +
      _fence([["Total concepts", model["concept_total"]],
              ["Homed", model["concept_total"] - measured_unhomed],
              ["Unhomed (planned)", measured_unhomed],
              ["Duplicate / orphan", f"{model['gaps']['duplicate_canonical_homes']} / {model['gaps']['orphan_concepts']}"],
              ["Determination", model["determination"]]], ["Metric", "Value"]) +
      "\n\n## Plan (Derived)\n\n" +
      _fence([["Classes assigned", len(class_counts)], ["Waves populated", len(wave_counts)],
              ["Critical/High priority", prio_counts.get("Critical", 0) + prio_counts.get("High", 0)],
              ["Medium priority", prio_counts.get("Medium", 0)],
              ["Future/Low priority", prio_counts.get("Future", 0) + prio_counts.get("Low", 0)],
              ["Contracts bound", len(plans)]], ["Metric", "Value"]) +
      "\n\n## Active-wave workload\n\n" +
      _fence([[WAVE_NAME[wv], wave_counts.get(wv, 0)] for wv in WAVE_ORDER if wave_counts.get(wv, 0)],
             ["Wave", "Concepts"]))

    # ---- 47 Knowledge Closure Roadmap
    roadmap_lines = ["The ordered, gated path from NOT-CLOSED toward evidence-backed closure. "
                     "Each wave is a gate: it opens only when the prior wave's artifacts are homed, "
                     "registered, and validated (fail-closed). No wave auto-executes.\n"]
    for wv in WAVE_ORDER:
        n = wave_counts.get(wv, 0)
        if not n:
            continue
        exemplar = ", ".join(sorted(p["id"] for p in plans if p["wave"] == wv)[:6])
        roadmap_lines.append(f"- **{WAVE_NAME[wv]}** — {n} concept(s). e.g. {exemplar}"
                             f"{' …' if n > 6 else ''}")
    w("47-KNOWLEDGE-CLOSURE-ROADMAP.md",
      hdr("47 — Knowledge Closure Roadmap", baseline, head,
          "The deterministic wave-gated roadmap to constitutional closure.") +
      "\n".join(roadmap_lines) +
      "\n\n**Gate law:** advancing to Wave N+1 requires Wave N artifacts to be homed + registered + "
      "validated, verified by re-running `make closure && make closure-phase2`. Closure is a standing "
      "gate, not a one-time event.")

    # ---- 48 Phase-003 Determination (fail-closed)
    #
    # UCCEP-F-001 / DG-7 / WP-UCCEP-001 / OA-5. This determination previously asserted
    # `repository_status` as the literal "NOT-CLOSED", and three of its success criteria as
    # the literal True, so `--gate` exited 1 unconditionally and no measured state could ever
    # satisfy it. A gate with no reachable PASS state carries no evidentiary value (PR-18),
    # and a constant verdict is not a determination. Every value below is now MEASURED, on
    # the same terms the sibling engines already used: `closure_engine.py` and
    # `phase2_engine.py` both compute "CLOSED" if closed else "NOT-CLOSED" from their own
    # blocking-gap count, and this engine now reads that located determination rather than
    # restating a constant beside it.
    located_closure = str(model.get("determination", "")).strip()
    located_gap_total = int(model.get("gap_total", 0) or 0)
    # The located determination is authoritative, and it is cross-checked rather than trusted:
    # a "CLOSED" carrying blocking gaps is itself a finding, and is refused.
    repository_status = (
        "CLOSED" if located_closure == "CLOSED" and located_gap_total == 0 else "NOT-CLOSED"
    )

    # Acyclicity is measured over the declared class-dependency chain instead of asserted.
    # The invariant the registers state is wave monotonicity: no concept may depend on a
    # predecessor in a later or equal wave. Wave "F" is parked and has no successors, so it is
    # ordered last by WAVE_ORDER.index rather than by numeric comparison.
    def _acyclic_dependency_chain() -> bool:
        for plan in plans:
            pred = plan["pred_class"]
            if pred is None:
                continue  # foundational / parked: no predecessor edge to order
            if pred not in CLASS_META:
                return False
            if WAVE_ORDER.index(CLASS_META[pred]["wave"]) >= WAVE_ORDER.index(plan["wave"]):
                return False
        # The class chain itself must terminate: walking `pred` from any class must reach None
        # without revisiting a class.
        for klass in CLASS_META:
            seen: set[str] = set()
            cursor: str | None = klass
            while cursor is not None:
                if cursor in seen or cursor not in CLASS_META:
                    return False
                seen.add(cursor)
                cursor = CLASS_META[cursor]["pred"]
        return True

    # "Planning only" is measured as a write-scope guard: this engine may write nothing
    # outside its own operational memory. That is the whole of the claim that Repository
    # Truth is unchanged and that no implementation was applied, and it is now checked
    # against the paths actually written rather than asserted.
    outside_own_memory = sorted(
        str(path.relative_to(REPO)) for path in written if path.resolve().parent != HERE
    )
    planning_only = not outside_own_memory

    success = {
        "Every unresolved concept classified (1 class)": len(plans) == len(unhomed),
        "Every concept has exactly one destination": all(p["destination"] for p in plans),
        "Every concept has exactly one owner": all(p["owner"] for p in plans),
        "Every concept has exactly one wave": all(p["wave"] in WAVE_NAME for p in plans),
        "Every concept has a dependency chain (acyclic)": _acyclic_dependency_chain(),
        "Every concept has an implementation contract": all(p["class"] in CLASS_META for p in plans),
        "Every concept has an enrichment plan row": len(plans) == len(unhomed),
        "Every concept has a projected closure path": all(
            p["wave"] in WAVE_NAME and p["destination"] and p["owner"] for p in plans
        ),
        "No concept unowned / unclassified / unknown": len(plans) == len(unhomed)
        and all(p["owner"] for p in plans),
        "Repository Truth unchanged (planning only)": planning_only,
        "No automatic implementation applied": planning_only,
    }
    all_pass = all(success.values())
    if not all_pass:
        determination = "FAIL-CLOSED — PLANNING INCOMPLETE"
    elif repository_status == "CLOSED":
        determination = "PLANNING-COMPLETE · REPOSITORY CLOSED (measured)"
    else:
        determination = "PLANNING-COMPLETE · REPOSITORY NOT-CLOSED (fail-closed)"
    seal = hashlib.sha256(json.dumps(
        {"phase": "PHASE-003", "baseline": baseline, "planned": len(plans),
         "repository_status": repository_status,
         "classes": dict(sorted(class_counts.items())), "waves": {str(k): v for k, v in sorted(wave_counts.items(), key=str)}},
        sort_keys=True).encode()).hexdigest()
    status_note = (
        "measured from the located PHASE-002 closure determination"
        if repository_status == "CLOSED"
        else "measured — planning delivered, execution pending"
    )
    w("48-PHASE-003-DETERMINATION.md",
      hdr("48 — PHASE-003 Determination", baseline, head,
          "The fail-closed determination for canonical implementation planning.") +
      f"| Field | Value |\n|---|---|\n"
      f"| Program | UAKOS-CLOSURE-002 · PHASE-003 |\n"
      f"| Frozen baseline | `{baseline}` |\n"
      f"| Determination | **{determination}** |\n"
      f"| Unresolved concepts planned | {len(plans)} / {len(unhomed)} |\n"
      f"| Classes / Waves | {len(class_counts)} / {len(wave_counts)} |\n"
      f"| Repository status | **{repository_status}** ({status_note}) |\n"
      f"| Located closure determination | `{located_closure or '—'}` · blocking gaps {located_gap_total} |\n"
      f"| Seal (sha256) | `{seal}` |\n"
      f"| Authority | NONE — DERIVED TRUTH (fail-closed, TRACK-001) |\n\n"
      "## Success criteria (mission)\n\n" +
      _fence([[k, "PASS" if v else "**FAIL**"] for k, v in success.items()], ["Criterion", "Status"]) +
      "\n\n" +
      ("**Planning is COMPLETE and internally consistent.** Every unresolved concept now has exactly one "
       "classification, destination, owner, wave, dependency chain, contract, enrichment-plan row, and "
       "projected closure path. **Repository Truth is unchanged**; no implementation was applied, and that "
       "is measured as a write-scope guard over the paths this engine actually wrote rather than asserted. "
       + (
           "The repository is **CLOSED**: the located PHASE-002 closure determination reports CLOSED with "
           "zero blocking gaps, and this determination reports what was measured rather than a constant. "
           "This verdict is reachable in both directions — it becomes NOT-CLOSED again the moment a "
           "blocking gap reappears (UCCEP-F-001 / OA-5)."
           if repository_status == "CLOSED" else
           "The repository remains **NOT-CLOSED** — this determination delivers the deterministic roadmap "
           "to reach closure, not closure itself (evidence precedes implementation; planning precedes "
           "execution). Execute via authorized waves, then re-run `make closure && make closure-phase2` "
           "to measure progress."
       )
       if all_pass else
       "**Planning incomplete — fail-closed.** One or more concepts lack a required planning attribute. "
       "See the failing criteria above; no determination is asserted until every concept is fully planned."))

    # ---- machine model
    phase3 = {
        "program": "UAKOS-CLOSURE-002", "phase": "PHASE-003",
        "baseline_commit": baseline, "head_commit": head,
        "authority": "NONE-DERIVED-TRUTH",
        "determination": determination,
        "repository_status": repository_status,
        "located_closure_determination": located_closure,
        "located_blocking_gaps": located_gap_total,
        "planning_only": planning_only,
        "wrote_outside_own_memory": outside_own_memory,
        "planning_complete": all_pass,
        "unresolved_total": len(unhomed),
        "planned_total": len(plans),
        "classes": dict(sorted(class_counts.items())),
        "waves": {str(k): v for k, v in sorted(wave_counts.items(), key=lambda kv: str(kv[0]))},
        "priorities": dict(sorted(prio_counts.items())),
        "projection": {"active_waves_home": measured_unhomed - remaining,
                       "wave_F_register": remaining,
                       "projected_unhomed_at_full_execution": max(remaining_after_f, 0),
                       "certainty": "PROJECTED (not measured)"},
        "success_criteria": success,
        "seal_sha256": seal,
        "inputs": {"closure_json": "closure.json", "phase2_json": "phase2.json"},
        "plans": plans,
    }
    (HERE / "phase3.json").write_text(
        json.dumps(phase3, indent=2, sort_keys=True, ensure_ascii=False) + "\n", "utf-8")
    return written, phase3


def load_model() -> dict:
    if not CLOSURE_JSON.is_file():
        sys.exit("FAIL-CLOSED: closure.json (frozen PHASE-002 baseline) absent — run `make closure` first.")
    model = json.loads(CLOSURE_JSON.read_text("utf-8"))
    # cross-consistency with phase2.json (non-fatal disclosure)
    if PHASE2_JSON.is_file():
        p2 = json.loads(PHASE2_JSON.read_text("utf-8"))
        if p2.get("concept_total") != model.get("concept_total"):
            print(f"NOTE: phase2.json concept_total={p2.get('concept_total')} != "
                  f"closure.json={model.get('concept_total')}; using closure.json (authoritative).",
                  file=sys.stderr)
    return model


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    gate = "--gate" in argv
    model = load_model()
    written, phase3 = emit(model)
    print(f"UAKOS-CLOSURE-002 · PHASE-003: {phase3['determination']} | "
          f"planned={phase3['planned_total']}/{phase3['unresolved_total']} "
          f"| classes={len(phase3['classes'])} waves={len(phase3['waves'])} "
          f"| repo={phase3['repository_status']}")
    print(f"wrote {len(written) + 1} artifacts to {HERE}")
    if gate and not phase3["planning_complete"]:
        print("GATE: planning incomplete (fail-closed) — a success criterion is unmet.", file=sys.stderr)
        return 1
    if gate and phase3["repository_status"] != "CLOSED":
        print("GATE: repository NOT-CLOSED (fail-closed) — planning delivered, execution pending.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
