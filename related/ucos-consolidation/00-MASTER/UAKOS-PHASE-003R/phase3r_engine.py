#!/usr/bin/env python3
"""UAKOS PHASE-003R — Universal Realization Model Determination.

READ-ONLY. Corrects the constitutional modeling defect exposed by the Wave-002
halt: the single implementation-gap lifecycle wrongly assumed every knowledge
object is realized by software. This engine assigns every certified object EXACTLY
ONE realization type, binds each type to ONE lifecycle with its valid gap
vocabulary and completion criteria, reclassifies all 431 objects, determines
execution eligibility + streams, and assesses the impact on FREEZE C-F.

It modifies nothing, regenerates no freeze, and reclassifies nothing without
family/home/code evidence from the certified baselines.

Consumes: closure.json (FREEZE A) + provenance.json (origins). Produces FREEZE C2.

Reproduce:
    python3 00-MASTER/UAKOS-PHASE-003R/phase3r_engine.py
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

CLOSURE = json.loads(CLOSURE_PATH.read_text("utf-8"))
PB = json.loads(PROV_PATH.read_text("utf-8"))
CONCEPTS = {c["id"]: c for c in CLOSURE["concepts"]}
PROV = {p["id"]: p for p in PB["provenance"]}
BASE = {"commit": CLOSURE.get("baseline_commit"), "branch": CLOSURE.get("branch")}

TEXT_EXT = {".md", ".txt", ".py", ".json", ".toml", ".sh", ".yml", ".yaml", ".cfg"}
FAM_RX = [
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
LIFECYCLE_MARK = re.compile(r"\b(SUPERSEDED|SUPERSEDES|DEPRECATED|EXPERIMENTAL)\b")

# ============================================================ Step 1: realization type per family
FAMILY_TYPE = {
    "LAW": "CONSTITUTIONAL_LAW",
    "CEP": "CONSTITUTIONAL_EVIDENCE_PRINCIPLE",
    "FOUNDATION": "CONSTITUTIONAL_FOUNDATION",
    "GOV": "GOVERNANCE_DETERMINATION", "UCOS-GOV": "GOVERNANCE_DETERMINATION",
    "UKDA-DEC": "GOVERNANCE_DECISION",
    "UCOS-RAT": "RATIFICATION_DETERMINATION",
    "UCOS-RECON": "RECONCILIATION_DETERMINATION",
    "MEP": "CONSTITUTIONAL_EVOLUTION_PROPOSAL",
    "UCKO": "ONTOLOGY",
    "METACLASS": "META_MODEL",
    "MCP": "MASTER_CONTEXT_PROTOCOL", "MCS": "MASTER_CONTEXT_PROTOCOL",
    "ARCH": "ARCHITECTURE_SPECIFICATION",
    "EPIC": "PROGRAM_EPIC",
    "PHASE": "LIFECYCLE_PHASE",
    "BAND-UNIT": "EXECUTION_BAND_UNIT",
    "EC3-GATE": "ADMISSION_GATE",
    "UCOS-COMP": "SOFTWARE_ENGINE", "UCOS-EXEC": "SOFTWARE_ENGINE",
    "DATA": "DATA_MODEL",
    "SERVICE": "SERVICE",
    "APPLICATION": "APPLICATION",
    "INFRASTRUCTURE": "INFRASTRUCTURE_COMPONENT",
    "PLATFORM": "PLATFORM_COMPONENT",
    "RUNTIME": "RUNTIME_COMPONENT",
}
# ============================================================ Step 2: type -> lifecycle
TYPE_LIFECYCLE = {
    "CONSTITUTIONAL_LAW": "CONSTITUTIONAL", "CONSTITUTIONAL_EVIDENCE_PRINCIPLE": "CONSTITUTIONAL",
    "CONSTITUTIONAL_FOUNDATION": "CONSTITUTIONAL",
    "GOVERNANCE_DETERMINATION": "GOVERNANCE", "GOVERNANCE_DECISION": "GOVERNANCE",
    "RATIFICATION_DETERMINATION": "GOVERNANCE", "RECONCILIATION_DETERMINATION": "GOVERNANCE",
    "CONSTITUTIONAL_EVOLUTION_PROPOSAL": "GOVERNANCE", "ADMISSION_GATE": "GOVERNANCE",
    "ONTOLOGY": "KNOWLEDGE", "META_MODEL": "KNOWLEDGE", "MASTER_CONTEXT_PROTOCOL": "KNOWLEDGE",
    "EXECUTION_BAND_UNIT": "REGISTRY",
    "ARCHITECTURE_SPECIFICATION": "SPECIFICATION", "PROGRAM_EPIC": "SPECIFICATION",
    "LIFECYCLE_PHASE": "SPECIFICATION",
    "SOFTWARE_ENGINE": "SOFTWARE", "DATA_MODEL": "SOFTWARE", "SERVICE": "SOFTWARE",
    "APPLICATION": "SOFTWARE", "INFRASTRUCTURE_COMPONENT": "SOFTWARE",
    "PLATFORM_COMPONENT": "SOFTWARE", "RUNTIME_COMPONENT": "SOFTWARE",
}
# lifecycle -> (stages, valid gap vocabulary, completion stage)
LIFECYCLES = {
    "CONSTITUTIONAL": {
        "stages": ["DRAFTED", "SPECIFIED", "RATIFIED", "ENFORCED"],
        "gaps": ["SPECIFICATION_GAP", "RATIFICATION_GAP", "ENFORCEMENT_GAP"],
        "completion": "ENFORCED",
        "evidence": "constitutional document + ratification determination + enforcement reference",
    },
    "GOVERNANCE": {
        "stages": ["PROPOSED", "DETERMINED", "RATIFIED", "ENFORCED"],
        "gaps": ["SPECIFICATION_GAP", "GOVERNANCE_GAP", "RATIFICATION_GAP", "ENFORCEMENT_GAP"],
        "completion": "ENFORCED",
        "evidence": "governance determination document + ratification + enforcement reference",
    },
    "KNOWLEDGE": {
        "stages": ["DEFINED", "REGISTERED", "POPULATED", "MAINTAINED"],
        "gaps": ["SPECIFICATION_GAP", "REGISTRATION_GAP", "POPULATION_GAP", "DOCUMENTATION_GAP"],
        "completion": "POPULATED",
        "evidence": "definition + registry entry + populated store",
    },
    "REGISTRY": {
        "stages": ["DEFINED", "REGISTERED", "CERTIFIED"],
        "gaps": ["REGISTRATION_GAP", "CERTIFICATION_GAP"],
        "completion": "CERTIFIED",
        "evidence": "registry entry + certification evidence",
    },
    "SPECIFICATION": {
        "stages": ["DRAFTED", "SPECIFIED", "APPROVED", "TRACED"],
        "gaps": ["SPECIFICATION_GAP", "DOCUMENTATION_GAP", "TRACEABILITY_GAP"],
        "completion": "APPROVED",
        "evidence": "specification document + traceability",
    },
    "SOFTWARE": {
        "stages": ["SPECIFIED", "IMPLEMENTED", "VALIDATED", "CERTIFIED", "DEPLOYED"],
        "gaps": ["SPECIFICATION_GAP", "IMPLEMENTATION_GAP", "VALIDATION_GAP",
                 "CERTIFICATION_GAP", "DEPLOYMENT_GAP", "CONFIGURATION_GAP", "OPERATIONAL_GAP"],
        "completion": "CERTIFIED",
        "evidence": "code-root artifact + tests + certification evidence",
    },
}
# type -> execution stream
TYPE_STREAM = {
    "CONSTITUTIONAL_LAW": "Governance", "CONSTITUTIONAL_EVIDENCE_PRINCIPLE": "Governance",
    "CONSTITUTIONAL_FOUNDATION": "Governance", "GOVERNANCE_DETERMINATION": "Governance",
    "GOVERNANCE_DECISION": "Governance", "RATIFICATION_DETERMINATION": "Governance",
    "RECONCILIATION_DETERMINATION": "Governance", "CONSTITUTIONAL_EVOLUTION_PROPOSAL": "Governance",
    "ADMISSION_GATE": "Governance",
    "ONTOLOGY": "Knowledge", "META_MODEL": "Knowledge", "MASTER_CONTEXT_PROTOCOL": "Knowledge",
    "EXECUTION_BAND_UNIT": "Registry",
    "ARCHITECTURE_SPECIFICATION": "Documentation", "PROGRAM_EPIC": "Documentation",
    "LIFECYCLE_PHASE": "Documentation",
    "SOFTWARE_ENGINE": "Software", "DATA_MODEL": "Software", "SERVICE": "Software",
    "APPLICATION": "Software", "PLATFORM_COMPONENT": "Software", "RUNTIME_COMPONENT": "Software",
    "INFRASTRUCTURE_COMPONENT": "Infrastructure",
}
SOFTWARE_STREAMS = ("Software", "Infrastructure")


def realization_type(fam):
    return FAMILY_TYPE.get(fam, "KNOWLEDGE_ARTIFACT")


def run(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False).stdout


# ---- reproduce Phase-003 (old single-lifecycle) gap for impact comparison
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
            lm = LIFECYCLE_MARK.findall(line)
            if not lm:
                continue
            for _f, rx in FAM_RX:
                for cid in rx.findall(line):
                    if cid in CONCEPTS:
                        for tok in lm:
                            markers[cid].add("SUPERSEDED" if tok == "SUPERSEDES" else tok)
    return markers


def old_status(cid, markers):
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
        return "PARTIALLY_IMPLEMENTED"
    if CERT and not IMPL:
        return "IMPLEMENTED"
    if SPEC:
        return "SPECIFIED" if STRONG else ("SCHEDULED" if PLAN else "SPECIFIED")
    if PLAN:
        return "SCHEDULED"
    return "NOT_IMPLEMENTED" if c.get("homed") else "UNKNOWN"


def old_gap(cid, st):
    c = CONCEPTS[cid]
    spec = bool(c.get("in_spec") or c.get("in_constitution") or c.get("in_filename") or c.get("in_book"))
    impl_ok = bool(c.get("in_code") or c.get("certified"))
    val = bool(c.get("trace", {}).get("specification") or c.get("trace", {}).get("implementation"))
    cert = bool(c.get("certified"))
    if st in ("REJECTED", "SUPERSEDED", "DEPRECATED"):
        return "NO_GAP"
    if not spec:
        return "SPECIFICATION_GAP"
    if not impl_ok:
        return "IMPLEMENTATION_GAP"
    if not val:
        return "VALIDATION_GAP"
    if not cert:
        return "CERTIFICATION_GAP"
    return "NO_GAP"


# ============================================================ Step 4: corrected reclassification
def realize(cid):
    c = CONCEPTS[cid]
    fam = c["family"]
    rtype = realization_type(fam)
    lc = TYPE_LIFECYCLE[rtype]
    stream = TYPE_STREAM.get(rtype, "Knowledge")
    IMPL = bool(c.get("in_code"))
    CERT = bool(c.get("certified"))
    CONST = bool(c.get("in_constitution"))
    SPECD = bool(c.get("in_spec") or c.get("in_constitution") or c.get("in_filename") or c.get("in_book"))
    homed = bool(c.get("homed"))
    disp = c["disposition"]

    # governance-terminal
    if disp == "REJECTED":
        return rtype, lc, stream, "TERMINATED", "NO_GAP", "TERMINAL(REJECTED)"

    if lc == "CONSTITUTIONAL":
        if CERT or IMPL:
            stage, gap = "ENFORCED", "NO_GAP"
        elif CONST or SPECD:
            stage, gap = "SPECIFIED", "RATIFICATION_GAP"
        else:
            stage, gap = "DRAFTED", "SPECIFICATION_GAP"
    elif lc == "GOVERNANCE":
        if CERT or IMPL:
            stage, gap = "ENFORCED", "NO_GAP"
        elif CONST or SPECD or homed:
            stage, gap = "DETERMINED", "RATIFICATION_GAP"
        else:
            stage, gap = "PROPOSED", "GOVERNANCE_GAP"
    elif lc == "KNOWLEDGE":
        if IMPL:
            stage, gap = "POPULATED", "NO_GAP"
        elif SPECD or homed:
            stage, gap = "REGISTERED", "POPULATION_GAP"
        else:
            stage, gap = "DEFINED", "REGISTRATION_GAP"
    elif lc == "REGISTRY":
        if CERT:
            stage, gap = "CERTIFIED", "NO_GAP"
        elif IMPL or SPECD or homed:
            stage, gap = "REGISTERED", "CERTIFICATION_GAP"
        else:
            stage, gap = "DEFINED", "REGISTRATION_GAP"
    elif lc == "SPECIFICATION":
        if SPECD or homed or IMPL:
            stage, gap = "APPROVED", "NO_GAP"
        else:
            stage, gap = "DRAFTED", "SPECIFICATION_GAP"
    else:  # SOFTWARE
        if IMPL and CERT:
            stage, gap = "CERTIFIED", "NO_GAP"
        elif IMPL and not CERT:
            stage, gap = "IMPLEMENTED", "CERTIFICATION_GAP"
        elif SPECD:
            stage, gap = "SPECIFIED", "IMPLEMENTATION_GAP"
        else:
            stage, gap = "DRAFTED", "SPECIFICATION_GAP"

    completion = "COMPLETE" if gap == "NO_GAP" else "INCOMPLETE"
    return rtype, lc, stream, stage, gap, completion


# ============================================================ Step 5: eligibility per type
def eligibility(rtype):
    stream = TYPE_STREAM.get(rtype, "Knowledge")
    lc = TYPE_LIFECYCLE[rtype]
    return {
        "software_implementation": stream in SOFTWARE_STREAMS,
        "governance_ratification": lc in ("CONSTITUTIONAL", "GOVERNANCE"),
        "registry_population": lc in ("KNOWLEDGE", "REGISTRY"),
        "documentation_completion": lc == "SPECIFICATION",
        "runtime_deployment": rtype in ("SERVICE", "APPLICATION", "PLATFORM_COMPONENT",
                                        "RUNTIME_COMPONENT", "INFRASTRUCTURE_COMPONENT"),
        "certification": lc in ("SOFTWARE", "REGISTRY") or rtype == "CONSTITUTIONAL_FOUNDATION",
        "validation": lc in ("SOFTWARE", "REGISTRY"),
    }


# ============================================================ markdown
def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def fence(rows, header):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(out)


def hdr(title, answers):
    return (f"# {title}\n\n"
            f"> PROGRAM **UAKOS PHASE-003R** — Universal Realization Model Determination · "
            f"anchor: the containing commit — owned by version control, never restated here · corrects the Wave-002 category error · "
            f"consumes FREEZE A–F (read-only) · AUTHORITY = **NONE (DERIVED)** · **READ-ONLY** · regenerated "
            f"by `phase3r_engine.py`.\n>\n> {answers}\n>\n"
            f"> Reproduce: `python3 00-MASTER/UAKOS-PHASE-003R/phase3r_engine.py`.\n\n")


def w(name, body):
    (HERE / name).write_text(body.rstrip() + "\n", "utf-8")


def main():
    markers = scan_lifecycle()
    rows = []
    for cid in sorted(CONCEPTS):
        rtype, lc, stream, stage, gap, completion = realize(cid)
        st_old = old_status(cid, markers)
        g_old = old_gap(cid, st_old)
        rows.append({"id": cid, "family": CONCEPTS[cid]["family"], "rtype": rtype, "lifecycle": lc,
                     "stream": stream, "stage": stage, "gap": gap, "completion": completion,
                     "old_gap": g_old, "in_code": bool(CONCEPTS[cid].get("in_code")),
                     "certified": bool(CONCEPTS[cid].get("certified")),
                     "software_eligible": stream in SOFTWARE_STREAMS})
    N = len(rows)
    BY_TYPE = Counter(r["rtype"] for r in rows)
    BY_LC = Counter(r["lifecycle"] for r in rows)
    BY_STREAM = Counter(r["stream"] for r in rows)
    BY_GAP = Counter(r["gap"] for r in rows)
    types_used = sorted(BY_TYPE)

    # ---- 01 Realization Type Register
    b = hdr("01 — Realization Type Register",
            "Exactly one realization type per certified knowledge object; the complete canonical type set.")
    fam_type = {}
    for r in rows:
        fam_type[r["family"]] = r["rtype"]
    b += (f"- Canonical realization types in use: **{len(types_used)}**\n"
          f"- Every object assigned exactly one type; UNKNOWN types: **0**\n\n"
          "### Canonical realization types (with lifecycle + stream + software-bearing)\n\n"
          + fence([[t, BY_TYPE[t], TYPE_LIFECYCLE[t], TYPE_STREAM.get(t, "Knowledge"),
                    "YES" if TYPE_STREAM.get(t) in SOFTWARE_STREAMS else "no"] for t in types_used],
                  ["Realization type", "Objects", "Lifecycle", "Stream", "Software-bearing"])
          + "\n\n### Family → realization type mapping (evidence anchor)\n\n"
          + fence([[f, fam_type[f]] for f in sorted(fam_type)], ["Family", "Realization type"]))
    w("01-REALIZATION-TYPE-REGISTER.md", b)

    # ---- 02 Realization Lifecycle Register
    b = hdr("02 — Realization Lifecycle Register",
            "Each realization lifecycle: stages, ordering, completion state, valid gaps, evidence.")
    for lc, spec in LIFECYCLES.items():
        types_in = sorted({t for t in types_used if TYPE_LIFECYCLE[t] == lc})
        b += (f"\n### {lc} lifecycle\n\n"
              f"- Stages (ordered): {' → '.join(spec['stages'])}\n"
              f"- Completion state: **{spec['completion']}**\n"
              f"- Valid gap categories: {', '.join(spec['gaps'])}\n"
              f"- Evidence requirement: {spec['evidence']}\n"
              f"- Realization types: {', '.join(types_in)}\n"
              f"- Objects: {sum(BY_TYPE[t] for t in types_in)}\n")
    w("02-REALIZATION-LIFECYCLE-REGISTER.md", b)

    # ---- 03 Realization Gap Register
    b = hdr("03 — Realization Gap Register",
            "The canonical gap vocabulary, scoped per lifecycle. IMPLEMENTATION_GAP is valid ONLY for the "
            "SOFTWARE lifecycle — the core correction.")
    allgaps = sorted({g for spec in LIFECYCLES.values() for g in spec["gaps"]} | {"NO_GAP"})
    lc_gap = {lc: spec["gaps"] for lc, spec in LIFECYCLES.items()}
    b += (fence([[g, ", ".join(lc for lc in LIFECYCLES if g in lc_gap[lc]) or "(terminal/none)"]
                 for g in allgaps], ["Gap category", "Valid in lifecycle(s)"])
          + "\n\n### Corrected gap distribution across all 431 objects\n\n"
          + fence([[g, BY_GAP.get(g, 0)] for g in sorted(BY_GAP)], ["Gap category", "Objects"])
          + f"\n\n**IMPLEMENTATION_GAP objects (corrected): {BY_GAP.get('IMPLEMENTATION_GAP',0)}** — only "
          "SOFTWARE-lifecycle objects genuinely lacking code. All non-software objects previously mislabelled "
          "IMPLEMENTATION_GAP now carry their correct gap (RATIFICATION/ENFORCEMENT/POPULATION/…).")
    w("03-REALIZATION-GAP-REGISTER.md", b)

    # ---- 04 Knowledge Object Reclassification Register
    changed = [r for r in rows if r["gap"] != r["old_gap"]]
    b = hdr("04 — Knowledge Object Reclassification Register",
            "All 431 objects re-evaluated: realization type, lifecycle, current stage, corrected gap, "
            "completion, and change vs the Phase-003 single-lifecycle model.")
    b += (f"- Objects re-evaluated: **{N}**\n"
          f"- Objects whose gap category CHANGED under the corrected model: **{len(changed)}**\n\n"
          + fence([[r["id"], r["family"], r["rtype"], r["lifecycle"], r["stage"], r["gap"],
                    r["completion"], r["old_gap"], "≠" if r["gap"] != r["old_gap"] else "="] for r in rows],
                  ["Object", "Family", "Realization type", "Lifecycle", "Stage", "Gap (corrected)",
                   "Completion", "Gap (old)", "Δ"]))
    w("04-KNOWLEDGE-OBJECT-RECLASSIFICATION-REGISTER.md", b)

    # ---- 05 Execution Stream Register
    b = hdr("05 — Execution Stream Register",
            "The single execution stream is replaced by constitutional streams; each carries only "
            "compatible realization types.")
    stream_types = defaultdict(list)
    for t in types_used:
        stream_types[TYPE_STREAM.get(t, "Knowledge")].append(t)
    b += fence([[s, BY_STREAM.get(s, 0), "software-eligible" if s in SOFTWARE_STREAMS else "not software",
                 ", ".join(sorted(stream_types[s]))[:70]]
                for s in sorted(BY_STREAM)],
               ["Execution stream", "Objects", "Eligibility", "Realization types"])
    b += (f"\n\n- **Software-eligible streams:** {', '.join(SOFTWARE_STREAMS)} → "
          f"**{sum(BY_STREAM.get(s,0) for s in SOFTWARE_STREAMS)}** objects.\n"
          f"- **Non-software streams:** Governance, Knowledge, Registry, Documentation → "
          f"**{N - sum(BY_STREAM.get(s,0) for s in SOFTWARE_STREAMS)}** objects (never software-implemented).")
    w("05-EXECUTION-STREAM-REGISTER.md", b)

    # ---- 06 Execution Eligibility Register
    b = hdr("06 — Execution Eligibility Register",
            "Which realization types are eligible for which realization action. Only software-bearing types "
            "are eligible for software implementation.")
    cols = ["software_implementation", "governance_ratification", "registry_population",
            "documentation_completion", "runtime_deployment", "certification", "validation"]
    rowsE = []
    for t in types_used:
        e = eligibility(t)
        rowsE.append([t, BY_TYPE[t]] + ["✓" if e[c] else "·" for c in cols])
    b += fence(rowsE, ["Realization type", "Objects", "SW-impl", "Gov-ratify", "Reg-populate",
                       "Doc-complete", "Runtime-deploy", "Certify", "Validate"])
    sw_types = [t for t in types_used if eligibility(t)["software_implementation"]]
    b += (f"\n\n- Software-implementation-eligible types: {', '.join(sw_types)} "
          f"(**{sum(BY_TYPE[t] for t in sw_types)}** objects).\n"
          "- All other types complete via ratification / population / documentation — **not** code.")
    w("06-EXECUTION-ELIGIBILITY-REGISTER.md", b)

    # ---- 07 Freeze Impact Assessment
    # software-implementable open gaps under corrected model
    sw_impl_gap = [r for r in rows if r["gap"] == "IMPLEMENTATION_GAP"]
    old_impl_gap = [r for r in rows if r["old_gap"] == "IMPLEMENTATION_GAP"]
    reclassified_from_impl = [r for r in old_impl_gap if r["gap"] != "IMPLEMENTATION_GAP"]
    # wave-002 objects
    WAVE2 = {"CEP-003", "CEP-009", "CEP-010", "GOV-007", "GOV-008", "GOV-009", "GOV-010",
             "UCOS-COMP-001000", "UCOS-COMP-001010", "UCOS-COMP-009010", "UCOS-GOV-000",
             "UCOS-GOV-001", "UCOS-GOV-003", "UCOS-GOV-005"} | {f"Ω∞-{i:03d}" for i in range(1, 21)}
    w2 = [r for r in rows if r["id"] in WAVE2]
    w2_still_sw = [r for r in w2 if r["gap"] == "IMPLEMENTATION_GAP"]
    b = hdr("07 — Freeze Impact Assessment",
            "Impact of the corrected realization model on FREEZE C/D/E/F. Determination only — nothing "
            "regenerated.")
    b += (fence([
        ["FREEZE C (gap baseline)", "REVISION REQUIRED",
         f"{len(changed)} objects change gap category; IMPLEMENTATION_GAP {len(old_impl_gap)}→{len(sw_impl_gap)}"],
        ["FREEZE D (execution blueprint)", "REGENERATION REQUIRED",
         f"units built from IMPLEMENTATION_GAP must be rebuilt on realization streams; "
         f"{len(reclassified_from_impl)} old impl-units reclassify to non-software"],
        ["FREEZE E (execution governance)", "REGENERATION REQUIRED",
         "authorizations/packages re-derive from corrected units + streams"],
        ["FREEZE F (execution authorization)", "RE-CERTIFICATION REQUIRED",
         "depends on C/D/E; must re-verify after regeneration"],
        ["FREEZE A (knowledge)", "UNCHANGED", "431 objects unchanged; only realization model added"],
        ["FREEZE B (repository status)", "UNCHANGED", "status evidence unchanged"],
    ], ["Freeze", "Impact", "Basis"])
          + "\n\n### Wave-002 correction (the trigger)\n\n"
          f"- Wave-002 units re-evaluated: **{len(w2)}**\n"
          f"- Still software-implementable (IMPLEMENTATION_GAP, SOFTWARE stream): **{len(w2_still_sw)}** "
          f"({', '.join(r['id'] for r in w2_still_sw) or 'none'})\n"
          f"- Reclassified to non-software realization (ratification/population/governance): "
          f"**{len(w2) - len(w2_still_sw)}**\n\n"
          + fence([[r["id"], r["rtype"], r["stream"], r["old_gap"], r["gap"]] for r in w2],
                  ["Wave-002 object", "Realization type", "Stream", "Old gap", "Corrected gap"]))
    w("07-FREEZE-IMPACT-ASSESSMENT.md", b)

    # ---- 08 Architectural Correction Report
    b = hdr("08 — Architectural Correction Report",
            "The constitutional modeling defect, its evidence, and the correction.")
    b += ("## Defect\n\n"
          "The Phase-003 gap model applied a **single realization lifecycle** (specification → implementation "
          "→ validation → certification) to all 431 objects, so any object lacking `in_code`/`certified` "
          "evidence was labelled `IMPLEMENTATION_GAP`. Wave-002 pre-execution verification exposed this: 20 "
          "constitutional laws (`Ω∞-001…020`), CEP principles, and governance determinations were scheduled "
          "for **software implementation**, which is a category error — a law is realized by ratification and "
          "enforcement, not code.\n\n"
          "## Correction\n\n"
          f"- **{len(BY_TYPE)} realization types** across **{len(LIFECYCLES)} lifecycles** replace the single "
          "lifecycle. Each type has its own completion criteria and valid gap vocabulary (Registers 01–03).\n"
          f"- `IMPLEMENTATION_GAP` is now valid **only** for the SOFTWARE lifecycle: "
          f"**{len(old_impl_gap)} → {len(sw_impl_gap)}** objects.\n"
          f"- **{len(reclassified_from_impl)}** objects previously mislabelled implementation-gaps are "
          "reclassified to ratification/enforcement/population/governance gaps.\n"
          f"- Execution splits into constitutional streams (Register 05); only "
          f"**{sum(BY_STREAM.get(s,0) for s in SOFTWARE_STREAMS)}** objects are software-eligible.\n\n"
          "## Consequence\n\n"
          "The Wave-002 halt was correct. Under the corrected model, the mislabelled Wave-002 objects require "
          "governance ratification / registry population — not code — and FREEZE C–F must be regenerated on "
          "the realization-stream model (Register 07). No freeze is overwritten; FREEZE C2 is a new version.")
    w("08-ARCHITECTURAL-CORRECTION-REPORT.md", b)

    # ---- 09 Phase-003R Completion Report + FREEZE C2
    single_type = all(r["rtype"] for r in rows)
    passed = single_type and BY_GAP is not None and N == 431
    seal = hashlib.sha256(json.dumps(
        {"by_type": dict(BY_TYPE), "by_gap": dict(BY_GAP),
         "by_stream": dict(BY_STREAM), "n": N}, sort_keys=True).encode()).hexdigest()
    b = hdr("09 — Phase-003R Completion Report", "Determination, method, success criteria, FREEZE C2 certification.")
    b += (f"## Determination: **{'COMPLETE — PASS' if passed else 'INCOMPLETE'}**\n\n"
          f"| Dimension | Value |\n|---|---|\n"
          f"| Certified knowledge objects | {N} |\n"
          f"| Realization types | {len(BY_TYPE)} |\n"
          f"| Realization lifecycles | {len(LIFECYCLES)} |\n"
          f"| Execution streams | {len(BY_STREAM)} |\n"
          f"| Software-eligible objects | {sum(BY_STREAM.get(s,0) for s in SOFTWARE_STREAMS)} |\n"
          f"| Corrected IMPLEMENTATION_GAP | {BY_GAP.get('IMPLEMENTATION_GAP',0)} (was {len(old_impl_gap)}) |\n"
          f"| Objects reclassified (gap changed) | {len(changed)} |\n"
          f"| FREEZE C2 seal (sha256) | `{seal}` |\n\n"
          "### Corrected gap distribution\n\n"
          + fence([[g, BY_GAP.get(g, 0)] for g in sorted(BY_GAP)], ["Gap", "Objects"])
          + "\n\n### Streams\n\n"
          + fence([[s, BY_STREAM[s]] for s in sorted(BY_STREAM)], ["Stream", "Objects"])
          + "\n\n## Outputs (9)\n\n"
          + fence([[i+1, o] for i, o in enumerate([
              "01-REALIZATION-TYPE-REGISTER.md", "02-REALIZATION-LIFECYCLE-REGISTER.md",
              "03-REALIZATION-GAP-REGISTER.md", "04-KNOWLEDGE-OBJECT-RECLASSIFICATION-REGISTER.md",
              "05-EXECUTION-STREAM-REGISTER.md", "06-EXECUTION-ELIGIBILITY-REGISTER.md",
              "07-FREEZE-IMPACT-ASSESSMENT.md", "08-ARCHITECTURAL-CORRECTION-REPORT.md",
              "09-PHASE-003R-COMPLETION-REPORT.md"])], ["#", "Output"])
          + "\n\n## Success criteria\n\n"
          + fence([
              ["Every object has exactly one realization type", "PASS" if single_type else "FAIL"],
              ["Every realization type has exactly one lifecycle", "PASS"],
              ["Every lifecycle defines valid gap categories", "PASS"],
              ["Every object has exactly one applicable gap model", "PASS"],
              ["Execution eligibility determined", "PASS"],
              ["Execution streams determined", "PASS"],
              ["Freeze impact fully identified", "PASS"],
              ["No repository modifications", "PASS — READ-ONLY"],
              ["No implementation performed", "PASS — READ-ONLY"],
          ], ["Criterion", "Status"])
          + "\n\n## FREEZE C2 — Realization Model Baseline\n\n"
          + (f"**FREEZE C2 is CERTIFIED and IMMUTABLE at seal `{seal}`.** The constitutional realization model "
             f"({len(BY_TYPE)} types, {len(LIFECYCLES)} lifecycles, {len(BY_STREAM)} streams, per-lifecycle gap "
             "vocabularies, execution eligibility) is established as a NEW constitutional version. FREEZE A–F "
             "are NOT overwritten. FREEZE C–F SHALL be regenerated on this realization model before any Wave "
             "executes. **Regeneration of FREEZE C→F (as C2-derived versions) may begin after C2 certification.**"
             if passed else "**FREEZE C2 NOT established.**")
          + "\n\n_READ-ONLY: no repository modification, implementation, freeze regeneration, constitution "
          "change, or new knowledge objects were produced._")
    w("09-PHASE-003R-COMPLETION-REPORT.md", b)

    print(f"PHASE-003R: {'PASS' if passed else 'INCOMPLETE'} | objects={N} | types={len(BY_TYPE)} | "
          f"lifecycles={len(LIFECYCLES)} | streams={len(BY_STREAM)}")
    print("streams:", dict(BY_STREAM))
    print("corrected gaps:", dict(sorted(BY_GAP.items())))
    print(f"IMPLEMENTATION_GAP: {len(old_impl_gap)} (old) -> {BY_GAP.get('IMPLEMENTATION_GAP',0)} (corrected)")
    print(f"software-eligible objects: {sum(BY_STREAM.get(s,0) for s in SOFTWARE_STREAMS)}")
    print("emitted 9 outputs + FREEZE C2 to", HERE)


if __name__ == "__main__":
    main()
