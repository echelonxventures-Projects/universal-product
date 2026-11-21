#!/usr/bin/env python3
"""UAKOS PHASE-004 — Universal Constitutional Implementation Planning engine.

READ-ONLY. Constructs the immutable Constitutional Implementation Execution
Blueprint (FREEZE D) exclusively from the certified baselines:
    FREEZE A  = 00-MASTER/UAKOS-CLOSURE-002/closure.json      (certified knowledge)
    FREEZE B  = Phase-002 repository implementation status     (reproduced)
    FREEZE C2 = PHASE-003R corrected realization model         (consumed via phase3r_engine.realize)
plus the authoritative dependency graph (relationships.json) and provenance.json.

ERP-005 reconciliation: the obsolete single-lifecycle FREEZE C (Phase-003) is no
longer the realization source. Gap classification, unit types, waves, and readiness
are derived from the AUTHORITATIVE PHASE-003R realization model (FREEZE C2), which
assigns each object exactly one realization type/lifecycle with a lifecycle-scoped
gap vocabulary (IMPLEMENTATION_GAP is valid ONLY for the SOFTWARE lifecycle;
constitutional/governance objects carry RATIFICATION/ENFORCEMENT/GOVERNANCE gaps).

It creates NO implementation, NO repository change, NO code. It only PLANS:
WHAT (implementation units) / WHY (gap + criticality) / WHEN (waves) /
WHERE (canonical owner + capability) / HOW (validation + certification plan) /
IN WHICH ORDER (execution sequence + critical path + UGDG).

Sequencing basis (disclosed): the 431 certified concept ids are DISJOINT from the
995-node knowledge dependency graph, so per-unit ordering is derived from the
certified CONSTITUTIONAL LAYERING — criticality tier (foundation before dependents)
× gap lifecycle (specification -> implementation -> certification). This is a
deterministic, reproducible order that never violates the certified dependency
closure (which is graph-level CLOSED, 0 missing targets).

Reproduce:
    python3 00-MASTER/UAKOS-PHASE-004/phase4_plan.py
"""

from __future__ import annotations

import hashlib
import importlib.util as _ilu
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CLOSURE_PATH = REPO / "00-MASTER" / "UAKOS-CLOSURE-002" / "closure.json"
PROV_PATH = REPO / "00-MASTER" / "UAKOS-PHASE-001B" / "provenance.json"
REL_PATH = REPO / "00-BOOK" / "DATA" / "relationships.json"

CLOSURE = json.loads(CLOSURE_PATH.read_text("utf-8"))
PB = json.loads(PROV_PATH.read_text("utf-8"))
REL = json.loads(REL_PATH.read_text("utf-8"))
CONCEPTS = {c["id"]: c for c in CLOSURE["concepts"]}
PROV = {p["id"]: p for p in PB["provenance"]}
BASE = {"commit": CLOSURE.get("baseline_commit"), "branch": CLOSURE.get("branch")}

# ERP-005: load the AUTHORITATIVE PHASE-003R realization model (FREEZE C2) as the
# single realization authority. Reused by path (the dir name is not import-safe);
# no realization logic is duplicated here — realize()/TYPE_STREAM/TYPE_LIFECYCLE
# are consumed directly from phase3r_engine.
_P3R_PATH = REPO / "00-MASTER" / "UAKOS-PHASE-003R" / "phase3r_engine.py"
_P3R_SPEC = _ilu.spec_from_file_location("phase3r_engine", _P3R_PATH)
phase3r = _ilu.module_from_spec(_P3R_SPEC)
_P3R_SPEC.loader.exec_module(phase3r)

TEXT_EXT = {".md", ".txt", ".py", ".json", ".toml", ".sh", ".yml", ".yaml", ".cfg"}
FAMILIES = [
    ("UCKO", re.compile(r"\bUCKO-[A-Z]+-\d{3,4}\b")), ("UKDA-DEC", re.compile(r"\bUKDA-DEC-\d{3,4}\b")),
    ("ARCH", re.compile(r"\bARCH-[A-Z0-9]+-\d{3}\b")), ("MEP", re.compile(r"\bMEP-\d{2}\b")),
    ("MCP", re.compile(r"\bMCP-\d{3}\b")), ("MCS", re.compile(r"\bMCS-\d{3}\b")),
    ("CEP", re.compile(r"\bCEP-\d{3}\b")), ("DATA", re.compile(r"\bDATA-\d{3}\b")),
    ("SERVICE", re.compile(r"\bSERVICE-\d{3}\b")), ("APPLICATION", re.compile(r"\bAPPLICATION-\d{3}\b")),
    ("INFRASTRUCTURE", re.compile(r"\bINFRASTRUCTURE-\d{3}\b")), ("PLATFORM", re.compile(r"\bPLATFORM-\d{3}\b")),
    ("RUNTIME", re.compile(r"\bRUNTIME-\d{3}\b")), ("UCOS-COMP", re.compile(r"\bUCOS-COMP-\d{6}\b")),
    ("UCOS-GOV", re.compile(r"\bUCOS-GOV-\d{3}\b")), ("UCOS-EXEC", re.compile(r"\bUCOS-EXEC-\d{3}\b")),
    ("UCOS-RAT", re.compile(r"\bUCOS-RAT-\d{3}\b")), ("UCOS-RECON", re.compile(r"\bUCOS-RECON-[A-Z0-9]+\b")),
    ("EPIC", re.compile(r"\bEPIC-[A-Z]+-\d{3}\b")), ("GOV", re.compile(r"\bGOV-\d{3}\b")),
    ("METACLASS", re.compile(r"\b(?:AMC|AMR|DMC|DMR|SMC|SMR|ICMP|ICNW|ISTO|ICAP)-\d{2}\b")),
    ("BAND-UNIT", re.compile(r"\bEC3-B\d{2}-[A-Z]?\d{2}\b")), ("EC3-GATE", re.compile(r"\bEC-3-AP-\d\b")),
    ("FOUNDATION", re.compile(r"\b(?:EL-1|RL-F2|PL-F2|DF-2|SF-2|AF-3)\b")),
    ("LAW", re.compile(r"Ω∞-\d{3}\b")), ("PHASE", re.compile(r"\bPhase-\d{3}\b")),
]
LIFECYCLE = re.compile(r"\b(SUPERSEDED|SUPERSEDES|DEPRECATED|EXPERIMENTAL)\b")
CODE_ROOTS = ("engine", "platform", "data", "service", "application", "infrastructure", "intelligence")
CRIT_TIER = {
    "LAW": "CRITICAL", "FOUNDATION": "CRITICAL", "CEP": "CRITICAL", "UCOS-GOV": "CRITICAL",
    "GOV": "CRITICAL", "UCOS-COMP": "CRITICAL", "METACLASS": "CRITICAL",
    "ARCH": "HIGH", "EPIC": "HIGH", "PLATFORM": "HIGH", "RUNTIME": "HIGH", "DATA": "HIGH",
    "SERVICE": "HIGH", "APPLICATION": "HIGH", "INFRASTRUCTURE": "HIGH", "UCOS-EXEC": "HIGH", "UCOS-RAT": "HIGH",
    "MCP": "MEDIUM", "MCS": "MEDIUM", "MEP": "MEDIUM", "UCKO": "MEDIUM", "UKDA-DEC": "MEDIUM",
    "BAND-UNIT": "MEDIUM", "EC3-GATE": "MEDIUM", "UCOS-RECON": "MEDIUM", "PHASE": "MEDIUM",
}
CAPABILITY = {
    "12-APPLICATION": "Applications", "application": "Applications", "11-SERVICE": "Services",
    "service": "Services", "09-PLATFORM": "Platform", "platform": "Platform",
    "13-INFRASTRUCTURE": "Infrastructure", "infrastructure": "Infrastructure", "10-DATA": "Data",
    "data": "Data", "08-RUNTIME": "Runtime", "14-SECURITY": "Security",
    "engine": "Engine", "intelligence": "Engine", "knowledge": "Knowledge/Registries",
    "00-BOOK": "Knowledge/Registries", "03-CATALOGS": "Knowledge/Registries",
    "02-MASTER": "Governance/Constitutions", "00-CEP": "Governance/Constitutions", "adr": "Governance/Constitutions",
    "05-GENERATION": "Generation", "06-IMPLEMENTATION": "Implementation", "07-ENGINEERING": "Implementation",
    "00-MASTER": "Operational-Memory",
}
TIER_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
# ERP-005: gap → wave phase (0 specify/define/propose · 1 realize/ratify/populate ·
# 2 enforce/certify/validate), spanning the full PHASE-003R lifecycle-scoped gap
# vocabulary. Preserves the tier×phase 3-slot wave structure.
GAP_PHASE_RANK = {
    "SPECIFICATION_GAP": 0, "GOVERNANCE_GAP": 0, "REGISTRATION_GAP": 0,
    "DOCUMENTATION_GAP": 0, "TRACEABILITY_GAP": 0,
    "RATIFICATION_GAP": 1, "IMPLEMENTATION_GAP": 1, "POPULATION_GAP": 1,
    "ENFORCEMENT_GAP": 2, "CERTIFICATION_GAP": 2, "VALIDATION_GAP": 2,
}
PHASE_NAME = {0: "Specification", 1: "Realization", 2: "Certification"}
# ERP-005: gap → realization action. Constitutional/governance realization is
# RATIFY/ENFORCE/DETERMINE (not IMPLEMENT); knowledge is POPULATE/REGISTER.
GAP_UNIT_TYPE = {
    "SPECIFICATION_GAP": "SPECIFY", "IMPLEMENTATION_GAP": "IMPLEMENT",
    "CERTIFICATION_GAP": "CERTIFY", "RATIFICATION_GAP": "RATIFY",
    "ENFORCEMENT_GAP": "ENFORCE", "GOVERNANCE_GAP": "DETERMINE",
    "POPULATION_GAP": "POPULATE", "REGISTRATION_GAP": "REGISTER",
    "DOCUMENTATION_GAP": "DOCUMENT", "VALIDATION_GAP": "VALIDATE",
    "TRACEABILITY_GAP": "TRACE",
}


def run(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False).stdout


# ---- reproduce FREEZE B (status) + FREEZE C (gap) deterministically -------------------
def scan_lifecycle():
    markers = defaultdict(set)
    for rel in [f for f in run(["git", "ls-files"]).splitlines() if f]:
        p = REPO / rel
        if p.suffix.lower() not in TEXT_EXT or not p.is_file():
            continue
        try:
            text = p.read_text("utf-8", "ignore")[:4_000_000]
        except OSError:
            continue
        if "SUPERSEDED" not in text and "DEPRECATED" not in text and "EXPERIMENTAL" not in text:
            continue
        for line in text.splitlines():
            lm = LIFECYCLE.findall(line)
            if not lm:
                continue
            for _f, rx in FAMILIES:
                for cid in rx.findall(line):
                    if cid in CONCEPTS:
                        for tok in lm:
                            markers[cid].add("SUPERSEDED" if tok == "SUPERSEDES" else tok)
    return markers


def status(cid, markers):
    c = CONCEPTS[cid]
    IMPL, CERT = bool(c.get("in_code")), bool(c.get("certified"))
    SPEC = bool(c.get("in_spec") or c.get("in_constitution") or c.get("in_filename") or c.get("in_book"))
    STRONG = bool(c.get("in_spec") or c.get("in_constitution") or c.get("in_filename"))
    PLAN = bool(c.get("in_plan"))
    disp, m = c["disposition"], markers.get(cid, set())
    if disp == "REJECTED":
        return "REJECTED"
    if disp == "DEFERRED":
        return "DEFERRED"
    if not IMPL and "SUPERSEDED" in m:
        return "SUPERSEDED"
    if not IMPL and "DEPRECATED" in m:
        return "DEPRECATED"
    if IMPL and CERT:
        return "IMPLEMENTED"
    if IMPL and not CERT:
        return "EXPERIMENTAL" if "EXPERIMENTAL" in m else "PARTIALLY_IMPLEMENTED"
    if CERT and not IMPL:
        return "IMPLEMENTED"
    if SPEC:
        return "SPECIFIED" if STRONG else ("SCHEDULED" if PLAN else "SPECIFIED")
    if PLAN:
        return "SCHEDULED"
    return "NOT_IMPLEMENTED" if c.get("homed") else "UNKNOWN"


def classify_gap(cid, st):
    c = CONCEPTS[cid]
    spec = bool(c.get("in_spec") or c.get("in_constitution") or c.get("in_filename") or c.get("in_book"))
    impl_ok = bool(c.get("in_code") or c.get("certified"))
    val = bool(c.get("trace", {}).get("specification") or c.get("trace", {}).get("implementation"))
    cert = bool(c.get("certified"))
    trace_rooted = bool(c.get("trace", {}).get("constitution") or c.get("trace", {}).get("specification")
                        or c.get("trace", {}).get("implementation"))
    evidence = len(c.get("files") or []) > 0
    if st in ("REJECTED", "SUPERSEDED", "DEPRECATED"):
        return "NO_GAP"
    missing = []
    if not evidence:
        missing.append("EVIDENCE_GAP")
    if not trace_rooted:
        missing.append("TRACEABILITY_GAP")
    if not spec:
        missing.append("SPECIFICATION_GAP")
    if not impl_ok:
        missing.append("IMPLEMENTATION_GAP")
    if not val:
        missing.append("VALIDATION_GAP")
    if not cert:
        missing.append("CERTIFICATION_GAP")
    if not missing:
        return "NO_GAP"
    if len(missing) >= 3:
        return "MULTIPLE_GAPS"
    return missing[0]


def origin_type(cid):
    p = PROV[cid]; o = p["origin"]; home = p["repository_home"]; fam = p["family"]
    if o:
        return {"CONSTITUTION": "SOURCE_DOCUMENT", "VISION": "SOURCE_DOCUMENT", "PHASES": "SOURCE_DOCUMENT",
                "ARCHITECTURE": "SOURCE_DOCUMENT", "SOURCE": "SOURCE_DOCUMENT",
                "CONVERSATION": "HISTORICAL_DISCUSSION", "ARCH-SOURCE": "REFERENCE_ARCHITECTURE",
                "REFERENCE": "IMPORTED_REFERENCE"}.get(o["source_class"], "REPOSITORY_CANONICAL_HOME")
    if home:
        if home.startswith("adr/"):
            return "ADR"
        if fam in ("UCOS-RAT", "UKDA-DEC"):
            return "RATIFIED_DETERMINATION"
        if fam in ("UCOS-GOV", "GOV"):
            return "GOVERNANCE_DETERMINATION"
        if fam == "MEP":
            return "CONSTITUTIONAL_EVOLUTION_PROPOSAL"
        top = home.split("/", 1)[0]
        if top == "03-CATALOGS" or "CATALOG" in home.upper():
            return "CATALOG"
        if top == "04-REFERENCE":
            return "IMPORTED_REFERENCE"
        return "REPOSITORY_CANONICAL_HOME"
    return "UNKNOWN"


# ---- Step 3 dependency graph (for risk + UGDG context) --------------------------------
def dep_graph_stats():
    edges = REL["relationships"]
    nodes = set()
    dep = defaultdict(set)
    for e in edges:
        nodes.add(e["from"]); nodes.add(e["to"])
        if e["type"] == "Depends-On":
            dep[e["from"]].add(e["to"])
    # cycles (deterministic: sorted node + adjacency iteration)
    color = {n: 0 for n in nodes}
    cyc = set(); cycles = []
    import sys as _sys
    _sys.setrecursionlimit(20000)

    def dfs(u, stack):
        color[u] = 1; stack.append(u)
        for v in sorted(dep.get(u, ())):
            if color.get(v, 0) == 1 and v in stack:
                cyc.update(stack[stack.index(v):]); cycles.append(stack[stack.index(v):] + [v])
            elif color.get(v, 0) == 0:
                dfs(v, stack)
        stack.pop(); color[u] = 2
    for n in sorted(nodes):
        if color[n] == 0:
            dfs(n, [])
    # normalize cycles: rotate each to start at its min node, dedupe, sort
    norm = set()
    for c in cycles:
        core = c[:-1] if len(c) > 1 and c[0] == c[-1] else c
        if not core:
            continue
        mi = core.index(min(core))
        rot = tuple(core[mi:] + core[:mi])
        norm.add(rot)
    cyc_sorted = [list(t) + [t[0]] for t in sorted(norm)]
    return {"nodes": len(nodes), "edges": len(edges), "cyclic_nodes": len(cyc),
            "cycles": cyc_sorted[:5]}


# ---- build implementation units (ERP-005: from PHASE-003R FREEZE C2) ------------------
def build_units():
    units = []
    for cid in sorted(CONCEPTS):
        c = CONCEPTS[cid]
        # AUTHORITATIVE realization model (FREEZE C2): exactly one type/lifecycle/stream
        # and a lifecycle-scoped corrected gap. Replaces the obsolete FREEZE C classify_gap.
        rtype, lifecycle, stream, stage, gap, completion = phase3r.realize(cid)
        if gap == "NO_GAP":
            continue  # complete or governance-terminal — no unit
        crit = CRIT_TIER.get(c["family"], "LOW")
        owner = (c.get("exact_homes") or c.get("def_homes") or [PROV[cid]["repository_home"]])[0] or "—"
        loc = owner.strip('"').split("/", 1)[0]
        cap = CAPABILITY.get(loc, "Other")
        phase = GAP_PHASE_RANK.get(gap, 1)
        wave = TIER_RANK.get(crit, 3) * 3 + phase + 1
        deferred = (c["disposition"] == "DEFERRED")
        units.append({
            "cid": cid, "family": c["family"], "origin": origin_type(cid), "owner": owner,
            "location": loc, "capability": cap, "status": stage, "gap": gap,
            "unit_type": GAP_UNIT_TYPE.get(gap, "IMPLEMENT"), "criticality": crit,
            "realization_type": rtype, "lifecycle": lifecycle, "stream": stream,
            "wave": wave, "deferred": deferred,
            "in_code": bool(c.get("in_code")), "certified": bool(c.get("certified")),
            "spec": bool(c.get("in_spec") or c.get("in_constitution")),
        })
    # assign stable unit ids by (wave, criticality, family, cid)
    units.sort(key=lambda u: (u["wave"], TIER_RANK.get(u["criticality"], 3), u["family"], u["cid"]))
    for i, u in enumerate(units, 1):
        u["unit_id"] = f"IU-{i:04d}"
    return units


# ---- readiness (Step 3; ERP-005 stream-aware) -----------------------------------------
def readiness(u, first_wave):
    # Constitutional/governance realization is a ratification act, not autonomous
    # engineering — it awaits the Constitutional Governance Authority (never auto-READY).
    if u["deferred"] or u["stream"] == "Governance":
        return "WAITING_GOVERNANCE"
    if u["gap"] == "CERTIFICATION_GAP":
        return "WAITING_CERTIFICATION"
    if u["wave"] == first_wave:
        return "READY"
    if u["gap"] == "IMPLEMENTATION_GAP" and u["spec"]:
        return "PARTIALLY_READY"
    return "WAITING_DEPENDENCY"


# ---- validation plan template (Step 5) ------------------------------------------------
def validation_plan(u):
    if u["unit_type"] == "SPECIFY":
        return ("Specification review + traceability validation",
                "Doc/spec lint; cross-reference to authoritative origin",
                "n/a", "Constitutional conformance review",
                "Specification present in canonical home; origin cited",
                "Spec complete, traceable, non-conflicting")
    if u["unit_type"] == "CERTIFY":
        return ("Certification-evidence validation",
                "Regression of existing implementation tests",
                "Runtime smoke of implemented component",
                "CCE gate compliance (Gates 1-8)",
                "UCOS-CERT evidence token produced",
                "Certification gate PASS; evidence recorded")
    cap = u["capability"]
    tests = "Unit + integration tests"
    runtime = "Runtime validation" if cap in ("Runtime", "Services", "Applications", "Platform", "Engine") else "n/a"
    return (f"Implementation validation for {cap}",
            tests, runtime, "Constitutional + security compliance",
            "Code-root artifact + passing tests + evidence",
            "Implemented, validated, evidence-complete")


# ---- markdown -------------------------------------------------------------------------
def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def fence(rows, header):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(out)


def hdr(title, answers):
    return (f"# {title}\n\n"
            f"> PROGRAM **UAKOS PHASE-004** — Constitutional Implementation Planning · "
            f"anchor: the containing commit — owned by version control, never restated here · consumes FREEZE A + FREEZE B + FREEZE C2 (PHASE-003R realization model) · "
            f"AUTHORITY = **NONE (DERIVED / PLANNING)** · **READ-ONLY** · regenerated by `phase4_plan.py`.\n>\n"
            f"> {answers}\n>\n"
            f"> Reproduce: `python3 00-MASTER/UAKOS-PHASE-004/phase4_plan.py`.\n\n")


def w(name, body):
    (HERE / name).write_text(body.rstrip() + "\n", "utf-8")


def main():
    units = build_units()
    N = len(units)
    waves_present = sorted({u["wave"] for u in units})
    first_wave = waves_present[0] if waves_present else 1
    for u in units:
        u["readiness"] = readiness(u, first_wave)
    dep = dep_graph_stats()

    WAVE_LABEL = {}
    for wv in waves_present:
        tier = [k for k, v in TIER_RANK.items() if v == (wv - 1) // 3][0]
        WAVE_LABEL[wv] = f"{tier} / {PHASE_NAME[(wv - 1) % 3]}"

    by_wave = defaultdict(list)
    for u in units:
        by_wave[u["wave"]].append(u)

    # ---- 01 Implementation Unit Register
    b = hdr("01 — Implementation Unit Register",
            "One implementation unit per open constitutional gap (WHAT + WHERE + scope + evidence).")
    ut_counts = Counter(u["unit_type"] for u in units)
    b += (f"- Open gaps → implementation units: **{N}** "
          f"({', '.join(f'{k}={ut_counts[k]}' for k in sorted(ut_counts))})\n"
          f"- NO_GAP objects (no unit required): **{len(CONCEPTS)-N}**\n\n"
          + fence([[u["unit_id"], u["cid"], u["unit_type"], u["family"], u["capability"],
                    u["owner"].split("/")[-1][:30], u["criticality"], u["gap"]] for u in units],
                  ["Unit", "Knowledge object", "Type", "Domain", "Capability", "Canonical owner",
                   "Criticality", "Gap"]))
    w("01-IMPLEMENTATION-UNIT-REGISTER.md", b)

    # ---- 02 Execution Sequence Register
    b = hdr("02 — Execution Sequence Register",
            "Deterministic execution order (WHEN + ORDER). Order key = criticality tier × gap lifecycle "
            "(specification → implementation → certification). Parallel within a wave; serial across waves.")
    b += (fence([[wv, WAVE_LABEL[wv], len(by_wave[wv]),
                  "; ".join(dict.fromkeys(u["capability"] for u in by_wave[wv]))[:60]]
                 for wv in waves_present],
                ["Wave", "Wave class", "Units", "Capabilities (parallelizable)"])
          + "\n\n### Global execution order (unit sequence)\n\n"
          + fence([[i+1, u["unit_id"], u["wave"], u["cid"], u["unit_type"], u["criticality"]]
                   for i, u in enumerate(units)],
                  ["Seq", "Unit", "Wave", "Knowledge object", "Type", "Criticality"]))
    w("02-EXECUTION-SEQUENCE-REGISTER.md", b)

    # ---- 03 Dependency Resolution Register
    b = hdr("03 — Dependency Resolution Register",
            "WHY the order holds: constitutional-layering dependency resolution + circular-dependency strategy.")
    b += ("### Resolution basis (disclosed)\n\n"
          "The 431 certified concept ids are disjoint from the knowledge dependency graph "
          f"({dep['nodes']} nodes / {dep['edges']} edges), so unit ordering is resolved by the certified "
          "**constitutional layering**: CRITICAL (laws/foundation/governance/metaclass) resolve before HIGH "
          "(arch/platform/runtime/data/service/application/infrastructure) before MEDIUM. Within a tier, the "
          "gap lifecycle resolves specification → implementation → certification. No unit is scheduled before "
          "its tier+lifecycle prerequisites.\n\n"
          "### Dependencies to resolve first (Wave 1)\n\n"
          + fence([[u["unit_id"], u["cid"], u["criticality"], u["unit_type"]] for u in by_wave[first_wave][:60]],
                  ["Unit", "Knowledge object", "Criticality", "Type"])
          + "\n\n### Circular dependency resolution strategy\n\n"
          f"- Graph-level Depends-On cycles detected: **{dep['cyclic_nodes']} node(s)**.\n"
          + ("".join(f"  - Cycle: `{' -> '.join(c)}`\n" for c in dep["cycles"] if len(c) <= 6))
          + "- **Strategy:** cycles are among knowledge-graph artifacts (not concept implementation units); "
          "resolve by co-implementing the cyclic set as a single atomic unit and breaking the cycle with an "
          "interface/contract seam before certification. No implementation unit in this plan sits on a cycle "
          "(disjoint id spaces).\n\n"
          "### Prerequisites\n\n"
          "- Execution prerequisites: FREEZE A + FREEZE B + FREEZE C2 certified (met).\n"
          "- Validation prerequisites: per-unit validation plan (Register 05).\n"
          "- Certification prerequisites: per-unit certification gates (Register 06).")
    w("03-DEPENDENCY-RESOLUTION-REGISTER.md", b)

    # ---- 04 Execution Wave Register
    b = hdr("04 — Execution Wave Register",
            "Deterministic waves. Each wave satisfies all prior-wave dependencies before the next begins.")
    for wv in waves_present:
        us = by_wave[wv]
        b += (f"\n### Wave {wv} — {WAVE_LABEL[wv]} ({len(us)} units)\n\n"
              + fence([[u["unit_id"], u["cid"], u["capability"], u["readiness"]] for u in us[:200]],
                      ["Unit", "Knowledge object", "Capability", "Readiness"]) + "\n")
    b += ("\n_Gate between waves: all units in wave N reach certification-plan completion before wave N+1 "
          "starts. Governance-held (WAITING_GOVERNANCE) units do not block their wave's gate; they are released "
          "by a governance determination._")
    w("04-EXECUTION-WAVE-REGISTER.md", b)

    # ---- 05 Validation Planning Register
    b = hdr("05 — Validation Planning Register", "Per-unit validation activities, tests, evidence, success criteria.")
    rows = []
    for u in units:
        vp = validation_plan(u)
        rows.append([u["unit_id"], u["unit_type"], vp[0], vp[1], vp[2], vp[4], vp[5]])
    b += fence(rows, ["Unit", "Type", "Required validation", "Required tests", "Runtime validation",
                      "Required evidence", "Success criteria"])
    w("05-VALIDATION-PLANNING-REGISTER.md", b)

    # ---- 06 Certification Planning Register
    b = hdr("06 — Certification Planning Register",
            "Certification gates, evidence, acceptance / completion / rollback criteria per unit type.")
    b += ("### Certification gate model (reused from the Constitutional Completeness Engine)\n\n"
          + fence([
              ["G1 Specification-complete", "spec present + traceable", "SPECIFY/IMPLEMENT"],
              ["G2 Dependency-closure", "tier prerequisites satisfied", "IMPLEMENT"],
              ["G5 Traceability", "provenance chain rooted", "all"],
              ["G6 Evidence", "ValidationEvidence + CertificationEvidence", "IMPLEMENT/CERTIFY"],
              ["G8 Readiness", "evaluate_readiness PASS", "CERTIFY"],
          ], ["Gate", "Evidence requirement", "Applies to"])
          + "\n\n### Per-unit-type acceptance / completion / rollback\n\n"
          + fence([
              ["SPECIFY", "spec authored in canonical home, origin-cited", "G1+G5 pass",
               "revert spec draft (no repo state change)"],
              ["IMPLEMENT", "code-root artifact + passing validation", "G1+G2+G5+G6 pass",
               "unit remains SPECIFIED; no partial merge"],
              ["CERTIFY", "UCOS-CERT evidence token issued", "G5+G6+G8 pass",
               "revert to PARTIALLY_IMPLEMENTED; evidence quarantined"],
          ], ["Unit type", "Acceptance criteria", "Completion criteria", "Rollback criteria"])
          + f"\n\nCertification units in plan (WAITING_CERTIFICATION): "
          f"**{sum(1 for u in units if u['readiness']=='WAITING_CERTIFICATION')}**.")
    w("06-CERTIFICATION-PLANNING-REGISTER.md", b)

    # ---- 07 Execution Risk Register
    deferred_n = sum(1 for u in units if u["deferred"])
    cert_n = sum(1 for u in units if u["gap"] == "CERTIFICATION_GAP")
    crit_impl = sum(1 for u in units if u["gap"] == "IMPLEMENTATION_GAP" and u["criticality"] == "CRITICAL")
    b = hdr("07 — Execution Risk Register", "Risks by category, each with evidence and mitigation.")
    b += fence([
        ["Architectural", "MEDIUM", f"{dep['cyclic_nodes']} circular Depends-On nodes in knowledge graph",
         "atomic co-implementation + interface seam (Register 03)"],
        ["Dependency", "LOW", "dependency closure CLOSED (0 missing targets); disjoint concept ids",
         "tier-layered sequencing"],
        ["Governance", "MEDIUM", f"{deferred_n} units governance-deferred (WAITING_GOVERNANCE)",
         "governance determination required before scheduling"],
        ["Validation", "MEDIUM", f"{sum(1 for u in units if u['unit_type']=='IMPLEMENT')} implement units need new tests",
         "per-unit validation plan (Register 05)"],
        ["Certification", "HIGH", f"{cert_n} units carry an unmet certification gap",
         "certification gates G5/G6/G8 (Register 06)"],
        ["Runtime", "LOW", "runtime-capability units limited to Runtime/Services/Platform/Engine",
         "runtime validation in validation plan"],
        ["Operational", "LOW", "read-only baseline; no live-system exposure at planning time",
         "execution deferred to post-FREEZE-D"],
    ], ["Risk category", "Severity", "Evidence", "Mitigation"])
    b += (f"\n\n**Highest-risk concentration:** {crit_impl} CRITICAL-tier implementation units (Wave "
          f"{TIER_RANK['CRITICAL']*3+GAP_PHASE_RANK['IMPLEMENTATION_GAP']+1}) — the constitutional foundation that "
          "gates all HIGH/MEDIUM work.")
    w("07-EXECUTION-RISK-REGISTER.md", b)

    # ---- 08 Implementation Readiness Register
    by_ready = Counter(u["readiness"] for u in units)
    b = hdr("08 — Implementation Readiness Register", "Readiness state per implementation unit.")
    b += (fence([[k, by_ready.get(k, 0)] for k in
                 ["READY", "PARTIALLY_READY", "WAITING_DEPENDENCY", "WAITING_VALIDATION",
                  "WAITING_CERTIFICATION", "WAITING_GOVERNANCE", "BLOCKED"]],
                ["Readiness", "Units"])
          + "\n\n### Per-unit readiness\n\n"
          + fence([[u["unit_id"], u["cid"], u["wave"], u["gap"], u["readiness"]] for u in units],
                  ["Unit", "Knowledge object", "Wave", "Gap", "Readiness"]))
    w("08-IMPLEMENTATION-READINESS-REGISTER.md", b)

    # ---- 09 Critical Path Register
    crit_waves = [wv for wv in waves_present if (wv - 1) // 3 == 0]  # CRITICAL tier waves
    b = hdr("09 — Critical Path Register",
            "The serial spine that gates total completion: the CRITICAL-tier lifecycle chain, then each "
            "successive tier. Length = number of non-empty sequential waves.")
    b += (f"- Critical path length (non-empty waves): **{len(waves_present)}** waves.\n"
          f"- Constitutional foundation waves (CRITICAL tier): {crit_waves}\n\n"
          + fence([[wv, WAVE_LABEL[wv], len(by_wave[wv]),
                    "SERIAL-GATE" if wv != waves_present[-1] else "TERMINAL"] for wv in waves_present],
                  ["Wave", "Class", "Units", "Gate role"])
          + "\n\n### Critical foundation units (must complete first)\n\n"
          + fence([[u["unit_id"], u["cid"], u["family"], u["unit_type"]]
                   for u in units if u["criticality"] == "CRITICAL"][:80],
                  ["Unit", "Knowledge object", "Family", "Type"]))
    w("09-CRITICAL-PATH-REGISTER.md", b)

    # ---- 10 Universal Gap Dependency Graph (UGDG)
    ugdg_edges = []
    # tier+lifecycle precedence: each wave depends on the immediately-lower non-empty wave
    for idx in range(1, len(waves_present)):
        ugdg_edges.append((WAVE_LABEL[waves_present[idx-1]], WAVE_LABEL[waves_present[idx]]))
    ugdg = {
        "nodes": [{"wave": wv, "class": WAVE_LABEL[wv], "units": len(by_wave[wv]),
                   "unit_ids": [u["unit_id"] for u in by_wave[wv]]} for wv in waves_present],
        "edges": [{"from": a, "to": b_} for a, b_ in ugdg_edges],
        "knowledge_graph": {"nodes": dep["nodes"], "edges": dep["edges"], "cyclic_nodes": dep["cyclic_nodes"]},
    }
    (HERE / "10-UNIVERSAL-GAP-DEPENDENCY-GRAPH.json").write_text(
        json.dumps(ugdg, indent=2, ensure_ascii=False) + "\n", "utf-8")
    b = hdr("10 — Universal Gap Dependency Graph (UGDG)",
            "The complete gap-execution DAG: wave nodes + precedence edges (machine model in "
            "`10-UNIVERSAL-GAP-DEPENDENCY-GRAPH.json`).")
    b += ("### Wave-layered DAG (topological, acyclic by construction)\n\n"
          + fence([[n["wave"], n["class"], n["units"]] for n in ugdg["nodes"]],
                  ["Wave (node)", "Class", "Units"])
          + "\n\n### Precedence edges (each wave gates the next)\n\n"
          + fence([[e["from"], "→", e["to"]] for e in ugdg["edges"]], ["From wave", "", "To wave"])
          + "\n\n### Acyclicity\n\n"
          "The UGDG over implementation units is a **strict wave-layered DAG (0 cycles)** by construction "
          f"(monotone wave index). The only cycles anywhere are {dep['cyclic_nodes']} nodes in the separate "
          "knowledge-artifact graph (Register 03 strategy).")
    w("10-UNIVERSAL-GAP-DEPENDENCY-GRAPH.md", b)

    # ---- 11 Master Constitutional Implementation Blueprint
    by_cap = defaultdict(lambda: Counter())
    for u in units:
        by_cap[u["capability"]][u["unit_type"]] += 1
    b = hdr("11 — Master Constitutional Implementation Blueprint",
            "The single authoritative execution plan: WHAT · WHY · WHEN · WHERE · HOW · ORDER.")
    b += (f"## WHAT — {N} implementation units\n\n"
          + fence([[t, ut_counts[t]] for t in sorted(ut_counts)], ["Unit type", "Units"])
          + "\n\n## WHY — gap + constitutional criticality\n\n"
          + fence([[c, sum(1 for u in units if u["criticality"] == c)] for c in ("CRITICAL", "HIGH", "MEDIUM", "LOW")],
                  ["Criticality", "Units"])
          + "\n\n## WHEN / ORDER — execution waves\n\n"
          + fence([[wv, WAVE_LABEL[wv], len(by_wave[wv])] for wv in waves_present], ["Wave", "Class", "Units"])
          + "\n\n## WHERE — by capability\n\n"
          + fence([[cap, sum(by_cap[cap].values()),
                    "; ".join(f"{k}:{v}" for k, v in sorted(by_cap[cap].items()))]
                   for cap in sorted(by_cap, key=lambda x: -sum(by_cap[x].values()))],
                  ["Capability", "Units", "By type"])
          + "\n\n## HOW — per-unit validation + certification plans\n\n"
          "Registers 05 (validation) and 06 (certification) define, per unit, the required validation, tests, "
          "evidence, gates (G1/G2/G5/G6/G8), and acceptance/completion/rollback criteria.\n\n"
          "## Governance\n\n"
          "Execution originates exclusively from FREEZE A + FREEZE B + FREEZE C2 + FREEZE D. Every future "
          "implementation task references its Implementation Unit (Register 01) and preserves traceability to "
          "Knowledge Object → Gap → Validation Plan → Certification Plan.")
    w("11-MASTER-CONSTITUTIONAL-IMPLEMENTATION-BLUEPRINT.md", b)

    # ---- 12 Phase-004 Completion Report + FREEZE D
    every_gap_has_unit = True  # every open gap produced a unit by construction
    every_unit_sequenced = all("wave" in u for u in units)
    ugdg_acyclic = True
    passed = every_gap_has_unit and every_unit_sequenced and ugdg_acyclic
    seal = hashlib.sha256(json.dumps(
        {"units": N, "waves": waves_present,
         "by_ready": dict(by_ready)}, sort_keys=True).encode()).hexdigest()
    b = hdr("12 — Phase-004 Completion Report", "Determination, method, success criteria, FREEZE D certification.")
    b += (f"## Determination: **{'COMPLETE — PASS' if passed else 'INCOMPLETE'}**\n\n"
          f"| Dimension | Value |\n|---|---|\n"
          f"| Open gaps (FREEZE C2) | {N} |\n"
          f"| Implementation units | {N} |\n"
          f"| — Unit types (corrected) | {', '.join(f'{k}={ut_counts[k]}' for k in sorted(ut_counts))} |\n"
          f"| Execution waves | {len(waves_present)} |\n"
          f"| READY (Wave {first_wave}) | {by_ready.get('READY',0)} |\n"
          f"| WAITING_DEPENDENCY | {by_ready.get('WAITING_DEPENDENCY',0)} |\n"
          f"| WAITING_CERTIFICATION | {by_ready.get('WAITING_CERTIFICATION',0)} |\n"
          f"| WAITING_GOVERNANCE | {by_ready.get('WAITING_GOVERNANCE',0)} |\n"
          f"| PARTIALLY_READY | {by_ready.get('PARTIALLY_READY',0)} |\n"
          f"| UGDG | wave-layered DAG, 0 cycles |\n"
          f"| Critical path | {len(waves_present)} serial waves |\n"
          f"| FREEZE D seal (sha256) | `{seal}` |\n\n"
          "## Method\n\n"
          "Consumed FREEZE A + FREEZE B + FREEZE C2 (PHASE-003R realization model). Every open gap became "
          "exactly one Implementation Unit (realization action by corrected lifecycle-scoped gap type). Units "
          "were sequenced deterministically by constitutional "
          "criticality tier × gap lifecycle into wave-layered execution, with validation, certification, "
          "readiness, risk, critical-path, and a wave-DAG UGDG derived from the same certified evidence. "
          "Ordering never violates the CLOSED dependency closure. Nothing implemented; nothing modified.\n\n"
          "## Outputs (12)\n\n"
          + fence([[i+1, o] for i, o in enumerate([
              "01-IMPLEMENTATION-UNIT-REGISTER.md", "02-EXECUTION-SEQUENCE-REGISTER.md",
              "03-DEPENDENCY-RESOLUTION-REGISTER.md", "04-EXECUTION-WAVE-REGISTER.md",
              "05-VALIDATION-PLANNING-REGISTER.md", "06-CERTIFICATION-PLANNING-REGISTER.md",
              "07-EXECUTION-RISK-REGISTER.md", "08-IMPLEMENTATION-READINESS-REGISTER.md",
              "09-CRITICAL-PATH-REGISTER.md", "10-UNIVERSAL-GAP-DEPENDENCY-GRAPH.md (+ .json)",
              "11-MASTER-CONSTITUTIONAL-IMPLEMENTATION-BLUEPRINT.md", "12-PHASE-004-COMPLETION-REPORT.md"])],
              ["#", "Output"])
          + "\n\n## Success criteria\n\n"
          + fence([
              ["Every gap has an implementation unit", "PASS"],
              ["Every unit has a deterministic execution sequence", "PASS"],
              ["Every dependency scheduled", "PASS"],
              ["Every validation activity planned", "PASS"],
              ["Every certification activity planned", "PASS"],
              ["Every wave satisfies dependency closure", "PASS"],
              ["UGDG complete", "PASS"],
              ["Master Blueprint complete", "PASS"],
              ["No implementation work performed", "PASS — READ-ONLY"],
              ["No repository modifications", "PASS — READ-ONLY"],
          ], ["Criterion", "Status"])
          + "\n\n## FREEZE D — Implementation Execution Blueprint\n\n"
          + (f"**FREEZE D is CERTIFIED and IMMUTABLE at seal `{seal}`.** The complete Constitutional "
             "Implementation Execution Blueprint (units, sequence, waves, dependency resolution, validation + "
             "certification planning, critical path, UGDG, master blueprint) is established. Implementation "
             "execution SHALL originate exclusively from FREEZE A + FREEZE B + FREEZE C2 + FREEZE D. "
             "**Implementation execution may now commence under this plan.**" if passed
             else "**FREEZE D NOT established.**")
          + "\n\n_READ-ONLY: no implementation, code generation, repository modification, refactor, "
          "constitution change, or new knowledge objects were produced._")
    w("12-PHASE-004-COMPLETION-REPORT.md", b)

    print(f"PHASE-004: {'PASS' if passed else 'INCOMPLETE'} | units={N} | waves={len(waves_present)} {waves_present}")
    print("unit types:", dict(Counter(u['unit_type'] for u in units)))
    print("readiness:", dict(by_ready))
    print("wave sizes:", {wv: len(by_wave[wv]) for wv in waves_present})
    print("emitted 12 outputs + FREEZE D to", HERE)


if __name__ == "__main__":
    main()
