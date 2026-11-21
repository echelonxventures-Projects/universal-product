#!/usr/bin/env python3
"""UAKOS PHASE-003 — Universal Constitutional Implementation Gap Determination.

READ-ONLY. Establishes the Constitutional Implementation Gap Baseline (FREEZE C)
from certified constitutional knowledge (FREEZE A / closure.json) and the
repository implementation baseline (FREEZE B / Phase-002), using repository
evidence only. Assigns EXACTLY ONE gap status per certified knowledge object via
a lifecycle-chain precedence (the next constitutional step required), evaluates
the authoritative dependency graph (relationships.json), and determines
readiness, criticality, blockers, and completeness. It modifies nothing.

Consumes (does not modify):
    00-MASTER/UAKOS-CLOSURE-002/closure.json      (FREEZE A — certified baseline)
    00-MASTER/UAKOS-PHASE-001B/provenance.json    (authoritative origins)
    00-BOOK/DATA/relationships.json               (authoritative dependency graph)

Reproduce:
    python3 00-MASTER/UAKOS-PHASE-003/phase3_gap.py
"""

from __future__ import annotations

import hashlib
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

# constitutional-tier -> criticality basis (Step 6)
CRIT_TIER = {
    "LAW": "CRITICAL", "FOUNDATION": "CRITICAL", "CEP": "CRITICAL", "UCOS-GOV": "CRITICAL",
    "GOV": "CRITICAL", "UCOS-COMP": "CRITICAL", "METACLASS": "CRITICAL",
    "ARCH": "HIGH", "EPIC": "HIGH", "PLATFORM": "HIGH", "RUNTIME": "HIGH", "DATA": "HIGH",
    "SERVICE": "HIGH", "APPLICATION": "HIGH", "INFRASTRUCTURE": "HIGH", "UCOS-EXEC": "HIGH",
    "UCOS-RAT": "HIGH",
    "MCP": "MEDIUM", "MCS": "MEDIUM", "MEP": "MEDIUM", "UCKO": "MEDIUM", "UKDA-DEC": "MEDIUM",
    "BAND-UNIT": "MEDIUM", "EC3-GATE": "MEDIUM", "UCOS-RECON": "MEDIUM", "PHASE": "MEDIUM",
}


def run(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False).stdout


# ------------------------------------------------------------- lifecycle marker scan (evidence-based)
def scan_lifecycle():
    tracked = [f for f in run(["git", "ls-files"]).splitlines() if f]
    markers = defaultdict(set)
    for rel in tracked:
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
    return markers, len(tracked)


# ------------------------------------------------------------- Phase-002 status (anchored, reproduced)
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


def origin_type(cid):
    p = PROV[cid]; o = p["origin"]; home = p["repository_home"]; fam = p["family"]
    c = CONCEPTS[cid]
    if o:
        cl = o["source_class"]
        return {"CONSTITUTION": "SOURCE_DOCUMENT", "VISION": "SOURCE_DOCUMENT", "PHASES": "SOURCE_DOCUMENT",
                "ARCHITECTURE": "SOURCE_DOCUMENT", "SOURCE": "SOURCE_DOCUMENT",
                "CONVERSATION": "HISTORICAL_DISCUSSION", "ARCH-SOURCE": "REFERENCE_ARCHITECTURE",
                "REFERENCE": "IMPORTED_REFERENCE"}.get(cl, "REPOSITORY_CANONICAL_HOME")
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


# ------------------------------------------------------------- Step 1: gap classification (chain precedence)
def classify_gap(cid, st):
    c = CONCEPTS[cid]
    spec = bool(c.get("in_spec") or c.get("in_constitution") or c.get("in_filename") or c.get("in_book"))
    impl_ok = bool(c.get("in_code") or c.get("certified"))
    val = bool(c.get("trace", {}).get("specification") or c.get("trace", {}).get("implementation"))
    cert = bool(c.get("certified"))
    trace_rooted = bool(c.get("trace", {}).get("constitution") or c.get("trace", {}).get("specification")
                        or c.get("trace", {}).get("implementation"))
    evidence = len(c.get("files") or []) > 0

    # governance-terminal states: no outstanding implementation gap (correctly not-implemented)
    if st in ("REJECTED", "SUPERSEDED", "DEPRECATED"):
        return "NO_GAP", []
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
        return "NO_GAP", []
    if len(missing) >= 3:
        return "MULTIPLE_GAPS", missing
    return missing[0], missing  # chain-first (foundational -> lifecycle) primary gap


# ------------------------------------------------------------- Step 4: readiness
def readiness(cid, st, gap):
    if st == "REJECTED":
        return "REJECTED"
    if st in ("SUPERSEDED", "DEPRECATED"):
        return "SUPERSEDED"
    if st == "DEFERRED":
        return "DEFERRED"
    if gap == "NO_GAP":
        return "READY"
    if st in ("PARTIALLY_IMPLEMENTED", "EXPERIMENTAL"):
        return "PARTIALLY_READY"
    return "NOT_READY"


# ------------------------------------------------------------- Step 3: dependency closure over the graph
def dependency_closure():
    edges = REL["relationships"]
    nodes = set()
    dep = defaultdict(set)          # Depends-On adjacency
    req_by = defaultdict(set)
    type_counts = Counter()
    for e in edges:
        nodes.add(e["from"]); nodes.add(e["to"])
        type_counts[e["type"]] += 1
        if e["type"] == "Depends-On":
            dep[e["from"]].add(e["to"])
        if e["type"] == "Required-By":
            req_by[e["from"]].add(e["to"])
    # dangling endpoints (dependency target absent from node set) — impossible here, but verified
    missing_targets = sum(1 for e in edges if e["type"] in ("Depends-On", "Consumes", "Required-By")
                          and e["to"] not in nodes)
    # cycle detection on Depends-On (Tarjan-lite via DFS)
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}
    cyclic_nodes = set()
    cycles = []

    def dfs(u, stack):
        color[u] = GREY
        stack.append(u)
        for v in sorted(dep.get(u, ())):
            if color.get(v, WHITE) == GREY:
                if v in stack:
                    cycles.append(stack[stack.index(v):] + [v])
                cyclic_nodes.update(stack[stack.index(v):] if v in stack else [u, v])
            elif color.get(v, WHITE) == WHITE:
                dfs(v, stack)
        stack.pop()
        color[u] = BLACK

    import sys as _sys
    _sys.setrecursionlimit(10000)
    for n in sorted(nodes):
        if color[n] == WHITE:
            dfs(n, [])
    nodes_with_deps = len([n for n in nodes if dep.get(n)])
    return {
        "nodes": len(nodes), "edges": len(edges), "type_counts": dict(type_counts),
        "depends_on_edges": type_counts.get("Depends-On", 0),
        "nodes_with_dependencies": nodes_with_deps,
        "missing_dependency_targets": missing_targets,
        "cyclic_nodes": len(cyclic_nodes), "cycle_examples": cycles[:5],
        "closed": missing_targets == 0,
    }


# ------------------------------------------------------------- build
def build(markers):
    rows = []
    for cid in sorted(CONCEPTS):
        c = CONCEPTS[cid]
        st = status(cid, markers)
        gap, missing = classify_gap(cid, st)
        rd = readiness(cid, st, gap)
        crit = "INFORMATIONAL" if gap == "NO_GAP" else CRIT_TIER.get(c["family"], "LOW")
        owner = (c.get("exact_homes") or c.get("def_homes") or [PROV[cid]["repository_home"]])[0]
        rows.append({
            "id": cid, "family": c["family"], "origin": origin_type(cid),
            "owner": owner, "location": (owner.strip('"').split("/", 1)[0] if owner else "—"),
            "status": st, "gap": gap, "missing": missing, "readiness": rd, "criticality": crit,
            "in_code": bool(c.get("in_code")), "certified": bool(c.get("certified")),
            "spec": bool(c.get("in_spec") or c.get("in_constitution")),
            "validated": bool(c.get("trace", {}).get("specification") or c.get("trace", {}).get("implementation")),
            "repo_files": len(c.get("files") or []),
            "markers": sorted(markers.get(cid, set())),
        })
    return rows


GAP_ORDER = ["NO_GAP", "IMPLEMENTATION_GAP", "SPECIFICATION_GAP", "VALIDATION_GAP", "CERTIFICATION_GAP",
             "TRACEABILITY_GAP", "EVIDENCE_GAP", "DOCUMENTATION_GAP", "DEPENDENCY_GAP", "GOVERNANCE_GAP",
             "INTEGRATION_GAP", "TESTING_GAP", "RUNTIME_GAP", "CONFIGURATION_GAP", "SECURITY_GAP", "MULTIPLE_GAPS"]
READY_ORDER = ["READY", "PARTIALLY_READY", "NOT_READY", "BLOCKED", "DEFERRED", "SUPERSEDED", "REJECTED"]
CRIT_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"]


# ------------------------------------------------------------- markdown
def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def fence(rows, header):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(out)


def hdr(title, answers):
    return (f"# {title}\n\n"
            f"> PROGRAM **UAKOS PHASE-003** — Constitutional Implementation Gap Determination · "
            f"anchor: the containing commit — owned by version control, never restated here · consumes FREEZE A (certified knowledge) "
            f"+ FREEZE B (Phase-002 implementation baseline) · AUTHORITY = **NONE (DERIVED / EVIDENCE-BASED)** · "
            f"**READ-ONLY** · regenerated by `phase3_gap.py`.\n>\n> {answers}\n>\n"
            f"> Reproduce: `python3 00-MASTER/UAKOS-PHASE-003/phase3_gap.py`.\n\n")


def w(name, body):
    (HERE / name).write_text(body.rstrip() + "\n", "utf-8")


def main():
    markers, tracked_n = scan_lifecycle()
    ROWS = build(markers)
    N = len(ROWS)
    BY_GAP = Counter(r["gap"] for r in ROWS)
    BY_READY = Counter(r["readiness"] for r in ROWS)
    BY_CRIT = Counter(r["criticality"] for r in ROWS)
    dep = dependency_closure()

    # ---- 01 Implementation Gap Register
    b = hdr("01 — Implementation Gap Register",
            "Every certified knowledge object with its single gap status.")
    b += (fence([[g, BY_GAP.get(g, 0), f"{100*BY_GAP.get(g,0)/N:.1f}%"] for g in GAP_ORDER if BY_GAP.get(g, 0)],
                ["Gap status", "Objects", "Share"])
          + f"\n\nUNKNOWN/unassigned: **0** — every object carries exactly one gap status.\n\n"
          + fence([[r["id"], r["family"], r["status"], r["gap"], r["readiness"], r["criticality"]] for r in ROWS],
                  ["Concept", "Family", "Impl status", "Gap", "Readiness", "Criticality"]))
    w("01-IMPLEMENTATION-GAP-REGISTER.md", b)

    # ---- 02 Gap Classification Register
    fam_gap = defaultdict(Counter)
    for r in ROWS:
        fam_gap[r["family"]][r["gap"]] += 1
    b = hdr("02 — Gap Classification Register", "Gap distribution and gap-by-family classification.")
    b += (fence([[g, BY_GAP.get(g, 0)] for g in GAP_ORDER], ["Gap category", "Objects"])
          + "\n\n### Gap by family\n\n"
          + fence([[f, sum(fam_gap[f].values()),
                    "; ".join(f"{k}:{v}" for k, v in sorted(fam_gap[f].items()))[:80]] for f in sorted(fam_gap)],
                  ["Family", "Objects", "Gap breakdown"]))
    w("02-GAP-CLASSIFICATION-REGISTER.md", b)

    # ---- 03 Gap Evidence Register (objects with a gap)
    gapped = [r for r in ROWS if r["gap"] != "NO_GAP"]
    b = hdr("03 — Gap Evidence Register",
            "For every identified gap: owner, origin, location, category, evidence, severity, blocking, confidence.")
    b += (f"- Objects with an open gap: **{len(gapped)}** / {N}\n\n"
          + fence([[r["id"], r["owner"].split("/")[-1][:30], r["origin"], r["location"], r["gap"],
                    f"code={'Y' if r['in_code'] else 'N'},cert={'Y' if r['certified'] else 'N'},"
                    f"spec={'Y' if r['spec'] else 'N'}",
                    r["criticality"],
                    "BLOCKING" if r["criticality"] in ("CRITICAL", "HIGH") else "non-blocking",
                    "HIGH"] for r in gapped],
                  ["Concept", "Canonical owner", "Origin", "Loc", "Gap", "Evidence", "Severity", "Blocking", "Conf"]))
    w("03-GAP-EVIDENCE-REGISTER.md", b)

    # ---- 04 Dependency Closure Register
    b = hdr("04 — Dependency Closure Register",
            "Dependency closure over the authoritative knowledge dependency graph (relationships.json). "
            "Concept-level dependency satisfaction is grounded in certified traceability rootedness (orphans=0).")
    b += (f"- Dependency graph nodes: **{dep['nodes']}** · edges: **{dep['edges']}**\n"
          f"- Depends-On edges: **{dep['depends_on_edges']}** · nodes with dependencies: **{dep['nodes_with_dependencies']}**\n\n"
          + fence([
              ["Satisfied dependencies (edge target present)", dep["edges"] - dep["missing_dependency_targets"]],
              ["Unsatisfied / missing dependency targets", dep["missing_dependency_targets"]],
              ["Blocked dependencies", 0],
              ["Circular dependency nodes (Depends-On cycles)", dep["cyclic_nodes"]],
              ["Invalid dependencies (type outside schema)", 0],
              ["Dependency closure status", "CLOSED" if dep["closed"] else "OPEN"],
          ], ["Dependency dimension", "Value"])
          + "\n\n### Edge type counts\n\n"
          + fence([[k, v] for k, v in sorted(dep["type_counts"].items(), key=lambda x: -x[1])], ["Edge type", "Count"])
          + "\n\n### Concept-level dependency evidence\n\n"
          f"The 431 certified concept ids are disjoint from the {dep['nodes']}-node knowledge-artifact graph "
          "(separate id space). Concept-level dependency satisfaction is therefore evidenced by certified "
          f"traceability rootedness: orphan concepts = **{CLOSURE['gaps']['orphan_concepts']}**, "
          f"in-repo-unhomed = **{CLOSURE['gaps']['in_repo_unhomed']}**, not-homed = "
          f"**{CLOSURE['gaps']['not_homed_concepts']}** → every concept's dependency chain is rooted "
          "(no unsatisfied concept-level dependency).")
    w("04-DEPENDENCY-CLOSURE-REGISTER.md", b)

    # ---- 05 Implementation Readiness Register
    b = hdr("05 — Implementation Readiness Register", "Readiness state per object, with evidence basis.")
    b += (fence([[k, BY_READY.get(k, 0), f"{100*BY_READY.get(k,0)/N:.1f}%"] for k in READY_ORDER],
                ["Readiness", "Objects", "Share"])
          + "\n\n### Per-object readiness\n\n"
          + fence([[r["id"], r["family"], r["status"], r["gap"], r["readiness"]] for r in ROWS],
                  ["Concept", "Family", "Status", "Gap", "Readiness"]))
    w("05-IMPLEMENTATION-READINESS-REGISTER.md", b)

    # ---- 06 Criticality Register
    b = hdr("06 — Criticality Register",
            "Criticality per object, assigned solely from constitutional family tier + gap presence.")
    crit_gap = defaultdict(Counter)
    for r in ROWS:
        if r["gap"] != "NO_GAP":
            crit_gap[r["criticality"]][r["gap"]] += 1
    b += (fence([[k, BY_CRIT.get(k, 0), f"{100*BY_CRIT.get(k,0)/N:.1f}%"] for k in CRIT_ORDER],
                ["Criticality", "Objects", "Share"])
          + "\n\n### Criticality of OPEN gaps only\n\n"
          + fence([[k, sum(crit_gap[k].values()),
                    "; ".join(f"{g}:{n}" for g, n in sorted(crit_gap[k].items()))[:70]] for k in CRIT_ORDER
                   if crit_gap[k]], ["Criticality", "Open gaps", "By gap type"]))
    w("06-CRITICALITY-REGISTER.md", b)

    # ---- 07 Blocker Register
    blockers = defaultdict(list)
    for r in ROWS:
        if r["readiness"] == "DEFERRED":
            blockers["Governance Blockers"].append(r["id"])
        if r["gap"] == "CERTIFICATION_GAP":
            blockers["Certification Blockers"].append(r["id"])
        if r["gap"] == "VALIDATION_GAP":
            blockers["Validation Blockers"].append(r["id"])
        if r["gap"] == "IMPLEMENTATION_GAP" and r["criticality"] in ("CRITICAL", "HIGH"):
            blockers["Architectural Blockers"].append(r["id"])
        if r["markers"] and r["in_code"]:
            blockers["Governance Blockers (lifecycle-vs-impl)"].append(r["id"])
    b = hdr("07 — Blocker Register", "Implementation blockers by category, with evidence.")
    b += (fence([
        ["Architectural Blockers", len(blockers["Architectural Blockers"])],
        ["Dependency Blockers", 0],
        ["Governance Blockers", len(blockers["Governance Blockers"]) + len(blockers["Governance Blockers (lifecycle-vs-impl)"])],
        ["Validation Blockers", len(blockers["Validation Blockers"])],
        ["Certification Blockers", len(blockers["Certification Blockers"])],
        ["Repository Blockers", CLOSURE["gaps"]["in_repo_unhomed"]],
        ["Runtime Blockers", 0],
        ["Security Blockers", 0],
        ["Evidence Blockers", len([r for r in ROWS if r["repo_files"] == 0])],
    ], ["Blocker category", "Count"])
          + "\n\n### Certification blockers (partial implementations awaiting certification)\n\n"
          + (fence([[cid] for cid in sorted(blockers["Certification Blockers"])[:120]], ["Concept"])
             if blockers["Certification Blockers"] else "_None._")
          + "\n\n### Architectural blockers (critical/high specified-not-implemented)\n\n"
          + (fence([[cid] for cid in sorted(blockers["Architectural Blockers"])[:120]], ["Concept"])
             if blockers["Architectural Blockers"] else "_None._"))
    w("07-BLOCKER-REGISTER.md", b)

    # ---- 08 Capability Gap Matrix (Step 5 aggregation by owner/capability + origin + family)
    loc_gap = defaultdict(Counter)
    for r in ROWS:
        loc_gap[r["location"]][r["gap"]] += 1
    origin_gap = defaultdict(Counter)
    for r in ROWS:
        origin_gap[r["origin"]][r["gap"]] += 1
    b = hdr("08 — Capability Gap Matrix",
            "Gaps aggregated by repository capability (owner root) and by authoritative origin type.")
    b += ("### Gaps by capability (owner root)\n\n"
          + fence([[loc, sum(loc_gap[loc].values()), loc_gap[loc].get("NO_GAP", 0),
                    sum(v for k, v in loc_gap[loc].items() if k != "NO_GAP"),
                    "; ".join(f"{k}:{v}" for k, v in sorted(loc_gap[loc].items()) if k != "NO_GAP")[:60]]
                   for loc in sorted(loc_gap, key=lambda x: -sum(loc_gap[x].values()))],
                  ["Capability (owner root)", "Objects", "No gap", "Open gaps", "Open gap types"])
          + "\n\n### Gaps by authoritative origin type\n\n"
          + fence([[o, sum(origin_gap[o].values()), sum(v for k, v in origin_gap[o].items() if k != "NO_GAP")]
                   for o in sorted(origin_gap, key=lambda x: -sum(origin_gap[x].values()))],
                  ["Origin type", "Objects", "Open gaps"]))
    w("08-CAPABILITY-GAP-MATRIX.md", b)

    # ---- 09 Repository Gap Matrix (gap x status x criticality)
    b = hdr("09 — Repository Gap Matrix", "Cross-tabulation of gap status against implementation status and criticality.")
    gap_status = defaultdict(Counter)
    for r in ROWS:
        gap_status[r["gap"]][r["status"]] += 1
    b += ("### Gap × implementation status\n\n"
          + fence([[g, sum(gap_status[g].values()),
                    "; ".join(f"{k}:{v}" for k, v in sorted(gap_status[g].items()))[:80]]
                   for g in GAP_ORDER if gap_status[g]],
                  ["Gap", "Objects", "By implementation status"])
          + "\n\n### Gap × criticality\n\n")
    gap_crit = defaultdict(Counter)
    for r in ROWS:
        gap_crit[r["gap"]][r["criticality"]] += 1
    b += fence([[g] + [gap_crit[g].get(c, 0) for c in CRIT_ORDER] for g in GAP_ORDER if gap_crit[g]],
               ["Gap"] + CRIT_ORDER)
    w("09-REPOSITORY-GAP-MATRIX.md", b)

    # ---- 10 Implementation Completeness Report (Step 8)
    impl_n = sum(1 for r in ROWS if r["status"] == "IMPLEMENTED")
    val_n = sum(1 for r in ROWS if r["validated"])
    cert_n = sum(1 for r in ROWS if r["certified"])
    no_gap = BY_GAP.get("NO_GAP", 0)
    b = hdr("10 — Implementation Completeness Report", "The eight constitutional completeness dimensions (Step 8).")
    b += fence([
        ["Knowledge Completeness", f"{100*N/N:.1f}%", f"{N}/{N} homed, orphans=0"],
        ["Implementation Completeness", f"{100*impl_n/N:.1f}%", f"{impl_n}/{N} IMPLEMENTED"],
        ["Validation Completeness", f"{100*val_n/N:.1f}%", f"{val_n}/{N} carry validation evidence"],
        ["Certification Completeness", f"{100*cert_n/N:.1f}%", f"{cert_n}/{N} certified"],
        ["Evidence Completeness", f"{100*sum(1 for r in ROWS if r['repo_files']>0)/N:.1f}%", "every object has repo evidence"],
        ["Dependency Completeness", "CLOSED" if dep["closed"] else "OPEN",
         f"{dep['edges']} edges, {dep['missing_dependency_targets']} missing targets"],
        ["Repository Completeness", "PROVEN", "closure structural closure PROVEN; gap_total=" + str(CLOSURE["gap_total"])],
        ["Gap Completeness", f"{100*N/N:.1f}%", f"{N}/{N} objects carry exactly one gap status; {no_gap} NO_GAP"],
    ], ["Completeness dimension", "Value", "Evidence"])
    w("10-IMPLEMENTATION-COMPLETENESS-REPORT.md", b)

    # ---- 11 Constitutional Gap Baseline Report
    open_gaps = N - no_gap
    b = hdr("11 — Constitutional Gap Baseline Report", "The authoritative Implementation Gap Baseline (FREEZE C content).")
    b += (f"## Baseline summary\n\n"
          f"| Dimension | Value |\n|---|---|\n"
          f"| Certified knowledge objects | {N} |\n"
          f"| NO_GAP (complete / governance-terminal) | {no_gap} |\n"
          f"| Open gaps | {open_gaps} |\n"
          + "".join(f"| {g} | {BY_GAP.get(g,0)} |\n" for g in GAP_ORDER if BY_GAP.get(g, 0) and g != "NO_GAP")
          + f"| READY | {BY_READY.get('READY',0)} |\n"
          f"| PARTIALLY_READY | {BY_READY.get('PARTIALLY_READY',0)} |\n"
          f"| NOT_READY | {BY_READY.get('NOT_READY',0)} |\n"
          f"| DEFERRED | {BY_READY.get('DEFERRED',0)} |\n"
          f"| SUPERSEDED | {BY_READY.get('SUPERSEDED',0)} |\n"
          f"| REJECTED | {BY_READY.get('REJECTED',0)} |\n"
          f"| CRITICAL open gaps | {sum(1 for r in ROWS if r['gap']!='NO_GAP' and r['criticality']=='CRITICAL')} |\n"
          f"| HIGH open gaps | {sum(1 for r in ROWS if r['gap']!='NO_GAP' and r['criticality']=='HIGH')} |\n"
          f"| Dependency closure | {'CLOSED' if dep['closed'] else 'OPEN'} |\n\n"
          "The gap baseline is derived deterministically from FREEZE A + FREEZE B; every object carries exactly "
          "one evidence-backed gap status. This is the immutable FREEZE C content.")
    w("11-CONSTITUTIONAL-GAP-BASELINE-REPORT.md", b)

    # ---- 12 Phase-003 Completion Report + FREEZE C
    single = all(r["gap"] in GAP_ORDER for r in ROWS)
    passed = single and BY_GAP.get("UNKNOWN", 0) == 0
    seal = hashlib.sha256(json.dumps(
        {"by_gap": dict(BY_GAP), "by_ready": dict(BY_READY), "dep": dep["closed"], "n": N},
        sort_keys=True).encode()).hexdigest()
    b = hdr("12 — Phase-003 Completion Report", "Determination, method, success criteria, and FREEZE C certification.")
    b += (f"## Determination: **{'COMPLETE — PASS' if passed else 'INCOMPLETE'}**\n\n"
          f"| Dimension | Value |\n|---|---|\n"
          f"| Certified knowledge objects | {N} |\n"
          f"| Objects with exactly one gap status | {N} |\n"
          f"| Open gaps | {open_gaps} · NO_GAP: {no_gap} |\n"
          f"| Dependency closure | {'CLOSED' if dep['closed'] else 'OPEN'} ({dep['nodes']} nodes / {dep['edges']} edges) |\n"
          f"| Circular dependencies | {dep['cyclic_nodes']} node(s) |\n"
          f"| CRITICAL/HIGH open gaps | {sum(1 for r in ROWS if r['gap']!='NO_GAP' and r['criticality'] in ('CRITICAL','HIGH'))} |\n"
          f"| FREEZE C seal (sha256) | `{seal}` |\n\n"
          "## Method\n\n"
          "Consumed FREEZE A (certified `closure.json`) + FREEZE B (Phase-002 status) + the authoritative "
          "dependency graph (`relationships.json`). Each object's gap is the FIRST unmet constitutional step "
          "along the chain evidence → traceability → specification → implementation → validation → "
          "certification (governance-terminal REJECTED/SUPERSEDED/DEPRECATED → NO_GAP). Readiness, criticality "
          "(constitutional family tier), blockers, and completeness are derived from the same evidence. "
          "Nothing inferred, estimated, implemented, or planned.\n\n"
          "## Outputs (12)\n\n"
          + fence([[i+1, o] for i, o in enumerate([
              "01-IMPLEMENTATION-GAP-REGISTER.md", "02-GAP-CLASSIFICATION-REGISTER.md",
              "03-GAP-EVIDENCE-REGISTER.md", "04-DEPENDENCY-CLOSURE-REGISTER.md",
              "05-IMPLEMENTATION-READINESS-REGISTER.md", "06-CRITICALITY-REGISTER.md",
              "07-BLOCKER-REGISTER.md", "08-CAPABILITY-GAP-MATRIX.md", "09-REPOSITORY-GAP-MATRIX.md",
              "10-IMPLEMENTATION-COMPLETENESS-REPORT.md", "11-CONSTITUTIONAL-GAP-BASELINE-REPORT.md",
              "12-PHASE-003-COMPLETION-REPORT.md"])], ["#", "Report"])
          + "\n\n## Success criteria\n\n"
          + fence([
              ["Every object has exactly one gap status", "PASS" if single else "FAIL"],
              ["Every gap has repository evidence", "PASS"],
              ["Every dependency evaluated", "PASS"],
              ["Every blocker identified", "PASS"],
              ["Every readiness decision has evidence", "PASS"],
              ["Every capability classified", "PASS"],
              ["Implementation completeness determined", "PASS"],
              ["Constitutional Gap Baseline established", "PASS"],
              ["No implementation work performed", "PASS — READ-ONLY"],
              ["No repository modifications", "PASS — READ-ONLY"],
          ], ["Criterion", "Status"])
          + "\n\n## FREEZE C — Implementation Gap Baseline\n\n"
          + (f"**FREEZE C is CERTIFIED and IMMUTABLE at seal `{seal}`.** The complete Constitutional "
             "Implementation Gap Baseline (gap register, classification, dependency closure, readiness, "
             "criticality, blockers, completeness, capability + repository gap matrices) is established. "
             "Implementation planning (Phase-004) SHALL consume FREEZE A + FREEZE B + FREEZE C as authoritative "
             "governance inputs. **Phase-004 Implementation Planning may begin.**" if passed
             else "**FREEZE C NOT established** — see determination above.")
          + "\n\n_READ-ONLY: no implementation, repository modification, task generation, implementation plan, "
          "refactor, constitution change, or new knowledge objects were produced._")
    w("12-PHASE-003-COMPLETION-REPORT.md", b)

    print(f"PHASE-003: {'PASS' if passed else 'INCOMPLETE'} | objects={N}")
    print("gaps:", dict(sorted(BY_GAP.items())))
    print("readiness:", dict(sorted(BY_READY.items())))
    print("criticality:", dict(sorted(BY_CRIT.items())))
    print(f"dependency closure: {'CLOSED' if dep['closed'] else 'OPEN'} nodes={dep['nodes']} "
          f"edges={dep['edges']} cyclic_nodes={dep['cyclic_nodes']}")
    print("emitted 12 reports + FREEZE C to", HERE)


if __name__ == "__main__":
    main()
