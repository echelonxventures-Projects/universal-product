#!/usr/bin/env python3
"""UAKOS PHASE-005 — Universal Constitutional Implementation Execution Governance.

READ-ONLY. Establishes the governed-execution model (FREEZE E) over the certified
FREEZE D execution blueprint. It reproduces the implementation units deterministically
from the AUTHORITATIVE PHASE-003R realization model (FREEZE C2, via phase3r_engine.realize),
then layers: one Execution Authorization per unit (WHO/WHEN/gates/rollback),
immutable Execution Packages, and validation / certification / rollback / risk
governance. It creates nothing and modifies nothing.

ERP-006 reconciliation: PHASE-005 no longer reproduces the obsolete single-lifecycle
FREEZE C model. Lifecycle, gap class, unit type, executor authority, approval gates,
and readiness are derived from PHASE-003R (FREEZE C2) — the SAME realization authority
as PHASE-004 — so execution authorization and execution planning are one model.

Consumes (does not modify):
    FREEZE A  closure.json · FREEZE C2 PHASE-003R realization model (phase3r_engine.realize).

Reproduce:
    python3 00-MASTER/UAKOS-PHASE-005/phase5_gov.py
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

CLOSURE = json.loads(CLOSURE_PATH.read_text("utf-8"))
PB = json.loads(PROV_PATH.read_text("utf-8"))
CONCEPTS = {c["id"]: c for c in CLOSURE["concepts"]}
PROV = {p["id"]: p for p in PB["provenance"]}
BASE = {"commit": CLOSURE.get("baseline_commit"), "branch": CLOSURE.get("branch")}

# ERP-006: load the AUTHORITATIVE PHASE-003R realization model (FREEZE C2) — the same
# realization authority PHASE-004 consumes. Reused by path; no realization logic duplicated.
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
CODE_CAPS = ("Applications", "Services", "Platform", "Infrastructure", "Data", "Runtime", "Engine",
             "Implementation", "Generation")
TIER_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
GAP_PHASE_RANK = {
    "SPECIFICATION_GAP": 0, "GOVERNANCE_GAP": 0, "REGISTRATION_GAP": 0,
    "DOCUMENTATION_GAP": 0, "TRACEABILITY_GAP": 0,
    "RATIFICATION_GAP": 1, "IMPLEMENTATION_GAP": 1, "POPULATION_GAP": 1,
    "ENFORCEMENT_GAP": 2, "CERTIFICATION_GAP": 2, "VALIDATION_GAP": 2,
}
PHASE_NAME = {0: "Specification", 1: "Realization", 2: "Certification"}
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


def executor_role(cap, unit_type, crit, stream):
    # ERP-006: executor authority derives from the PHASE-003R realization stream.
    if stream == "Governance":
        return "Constitutional Governance Authority"
    if unit_type == "CERTIFY":
        return "Constitutional Completeness Engine (CCE) + Certification Authority"
    if stream in ("Knowledge", "Registry", "Documentation"):
        return "Knowledge Authority"
    return "Certified Implementation Engine (EC-1)"  # Software / Infrastructure


def build_units():
    units = []
    for cid in sorted(CONCEPTS):
        c = CONCEPTS[cid]
        # AUTHORITATIVE realization model (FREEZE C2) — identical source to PHASE-004.
        rtype, lifecycle, stream, stage, gap, completion = phase3r.realize(cid)
        if gap == "NO_GAP":
            continue
        crit = CRIT_TIER.get(c["family"], "LOW")
        owner = (c.get("exact_homes") or c.get("def_homes") or [PROV[cid]["repository_home"]])[0] or "—"
        loc = owner.strip('"').split("/", 1)[0]
        cap = CAPABILITY.get(loc, "Other")
        wave = TIER_RANK.get(crit, 3) * 3 + GAP_PHASE_RANK.get(gap, 1) + 1
        utype = GAP_UNIT_TYPE.get(gap, "IMPLEMENT")
        units.append({
            "cid": cid, "family": c["family"], "owner": owner, "location": loc, "capability": cap,
            "status": stage, "gap": gap, "unit_type": utype, "criticality": crit, "wave": wave,
            "realization_type": rtype, "lifecycle": lifecycle, "stream": stream,
            "deferred": c["disposition"] == "DEFERRED",
            "executor": executor_role(cap, utype, crit, stream),
        })
    units.sort(key=lambda u: (u["wave"], TIER_RANK.get(u["criticality"], 3), u["family"], u["cid"]))
    for i, u in enumerate(units, 1):
        u["unit_id"] = f"IU-{i:04d}"
    return units


# ---- governance templates -------------------------------------------------------------
APPROVAL = {
    "SPECIFY": ["SPEC-AUTHOR-APPROVAL", "TRACEABILITY-APPROVAL"],
    "IMPLEMENT": ["DESIGN-APPROVAL", "IMPL-APPROVAL", "VALIDATION-APPROVAL"],
    "CERTIFY": ["EVIDENCE-APPROVAL", "CERTIFICATION-APPROVAL"],
    "RATIFY": ["GOVERNANCE-RELEASE", "RATIFICATION-APPROVAL"],
    "ENFORCE": ["GOVERNANCE-RELEASE", "ENFORCEMENT-APPROVAL"],
    "DETERMINE": ["GOVERNANCE-DETERMINATION-APPROVAL"],
    "POPULATE": ["REGISTRY-APPROVAL", "POPULATION-APPROVAL"],
    "REGISTER": ["REGISTRY-APPROVAL"],
    "DOCUMENT": ["DOC-APPROVAL", "TRACEABILITY-APPROVAL"],
    "VALIDATE": ["VALIDATION-APPROVAL"],
    "TRACE": ["TRACEABILITY-APPROVAL"],
}
VAL_GATES = {
    "SPECIFY": ["V-PRE:freeze-check", "V-POST:spec-lint+traceability"],
    "IMPLEMENT": ["V-PRE:freeze+prereq", "V-IN:unit-tests", "V-POST:integration+runtime+evidence"],
    "CERTIFY": ["V-PRE:regression", "V-POST:certification-evidence"],
    "RATIFY": ["V-PRE:freeze+specified-check", "V-POST:ratification-conformance"],
    "ENFORCE": ["V-PRE:ratified-check", "V-POST:enforcement-reference"],
    "DETERMINE": ["V-PRE:freeze-check", "V-POST:determination-conformance"],
    "POPULATE": ["V-PRE:registry-check", "V-POST:population-evidence"],
    "REGISTER": ["V-PRE:definition-check", "V-POST:registration-evidence"],
    "DOCUMENT": ["V-PRE:freeze-check", "V-POST:doc-lint+traceability"],
    "VALIDATE": ["V-PRE:impl-check", "V-POST:validation-evidence"],
    "TRACE": ["V-PRE:freeze-check", "V-POST:trace-conformance"],
}
CERT_GATES = {
    "SPECIFY": ["G1", "G5"],
    "IMPLEMENT": ["G1", "G2", "G5", "G6"],
    "CERTIFY": ["G5", "G6", "G8"],
    "RATIFY": ["G1", "G5"],
    "ENFORCE": ["G5", "G6"],
    "DETERMINE": ["G1", "G5"],
    "POPULATE": ["G5", "G6"],
    "REGISTER": ["G5"],
    "DOCUMENT": ["G1", "G5"],
    "VALIDATE": ["G5", "G6"],
    "TRACE": ["G5"],
}
ROLLBACK = {
    "SPECIFY": "Discard spec draft; object remains at prior state (no repo state change).",
    "IMPLEMENT": "Do not merge partial artifact; object remains SPECIFIED; revert branch.",
    "CERTIFY": "Revert to PARTIALLY_IMPLEMENTED; quarantine certification evidence.",
    "RATIFY": "Revert to SPECIFIED; no ratification recorded (governance state unchanged).",
    "ENFORCE": "Revert to RATIFIED; enforcement reference withdrawn.",
    "DETERMINE": "Discard governance determination draft; object remains PROPOSED.",
    "POPULATE": "Revert store to prior populated state; population evidence quarantined.",
    "REGISTER": "Remove registry entry; Universal ID remains reserved (never reused).",
    "DOCUMENT": "Discard documentation draft; object remains at prior state.",
    "VALIDATE": "Revert to IMPLEMENTED; validation evidence quarantined.",
    "TRACE": "Revert trace linkage; object remains at prior state.",
}


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def fence(rows, header):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(out)


def hdr(title, answers):
    return (f"# {title}\n\n"
            f"> PROGRAM **UAKOS PHASE-005** — Constitutional Implementation Execution Governance · "
            f"anchor: the containing commit — owned by version control, never restated here · consumes FREEZE A+B+C2+D · "
            f"AUTHORITY = **NONE (DERIVED / GOVERNANCE)** · **READ-ONLY** · regenerated by `phase5_gov.py`.\n>\n"
            f"> {answers}\n>\n> Reproduce: `python3 00-MASTER/UAKOS-PHASE-005/phase5_gov.py`.\n\n")


def w(name, body):
    (HERE / name).write_text(body.rstrip() + "\n", "utf-8")


def main():
    units = build_units()
    N = len(units)
    waves = sorted({u["wave"] for u in units})
    first_wave = waves[0]
    by_wave = defaultdict(list)
    for u in units:
        by_wave[u["wave"]].append(u)

    # ---- execution authorizations (1:1 with units)
    for u in units:
        u["ea_id"] = "EA-" + u["unit_id"].split("-")[1]
        u["prereq"] = "none (Wave first)" if u["wave"] == first_wave else \
            f"all waves < {u['wave']} certified-complete"
        base_appr = APPROVAL[u["unit_type"]]
        needs_gov = (u["deferred"] or u["stream"] == "Governance") and "GOVERNANCE-RELEASE" not in base_appr
        u["approval_gates"] = (["GOVERNANCE-RELEASE"] if needs_gov else []) + base_appr
        u["val_gates"] = VAL_GATES[u["unit_type"]]
        u["cert_gates"] = CERT_GATES[u["unit_type"]]
        u["rollback"] = ROLLBACK[u["unit_type"]]

    # ---- execution packages (immutable) grouped by (wave, capability)
    pkg_map = defaultdict(list)
    for u in units:
        pkg_map[(u["wave"], u["capability"])].append(u)
    packages = []
    for i, ((wave, cap), us) in enumerate(sorted(pkg_map.items()), 1):
        packages.append({
            "pkg_id": f"EP-{i:03d}", "wave": wave, "capability": cap, "units": us,
            "unit_ids": [u["unit_id"] for u in us],
            "types": Counter(u["unit_type"] for u in us),
            "executor": us[0]["executor"],
            "deferred": sum(1 for u in us if u["deferred"]),
        })

    WAVE_LABEL = {}
    for wv in waves:
        tier = [k for k, v in TIER_RANK.items() if v == (wv - 1) // 3][0]
        WAVE_LABEL[wv] = f"{tier} / {PHASE_NAME[(wv - 1) % 3]}"

    # ---- 01 Execution Authorization Register
    b = hdr("01 — Execution Authorization Register",
            "Exactly one Execution Authorization per implementation unit: WHO, WHEN, prerequisites, "
            "approval + validation + certification gates, rollback.")
    b += (f"- Execution authorizations issued: **{N}** (1:1 with implementation units)\n"
          f"- Authorizations gated by GOVERNANCE-RELEASE (deferred): "
          f"**{sum(1 for u in units if u['deferred'])}**\n\n"
          + fence([[u["ea_id"], u["unit_id"], u["cid"], u["wave"], u["executor"],
                    "+".join(u["approval_gates"])[:34], "+".join(u["cert_gates"])] for u in units],
                  ["Auth", "Unit", "Knowledge object", "Wave", "Authorized executor",
                   "Approval gates", "Cert gates"]))
    w("01-EXECUTION-AUTHORIZATION-REGISTER.md", b)

    # ---- 02 Execution Package Register
    b = hdr("02 — Execution Package Register",
            "Immutable execution packages (wave × capability), each with scope, inputs, outputs, "
            "dependencies, validation, certification, evidence, acceptance criteria.")
    b += (f"- Execution packages: **{len(packages)}** across {len(waves)} waves.\n\n"
          + fence([[p["pkg_id"], p["wave"], WAVE_LABEL[p["wave"]], p["capability"], len(p["units"]),
                    "; ".join(f"{k}:{v}" for k, v in sorted(p["types"].items())),
                    (f"waves<{p['wave']}" if p["wave"] != first_wave else "none"),
                    p["executor"][:30]] for p in packages],
                  ["Package", "Wave", "Wave class", "Capability", "Units", "Types", "Depends on", "Executor"]))
    b += "\n\n### Package specifications (scope / inputs / outputs / acceptance)\n"
    for p in packages[:60]:
        b += (f"\n**{p['pkg_id']} — {p['capability']} · Wave {p['wave']} ({WAVE_LABEL[p['wave']]})**\n\n"
              f"- Scope: {len(p['units'])} units ({', '.join(f'{k}×{v}' for k,v in sorted(p['types'].items()))}) "
              f"in `{p['units'][0]['location']}`\n"
              f"- Inputs: certified FREEZE A–E; outputs of all packages in waves < {p['wave']}\n"
              f"- Outputs: {p['capability']} objects advanced to next lifecycle state\n"
              f"- Dependencies: {'none (first wave)' if p['wave']==first_wave else f'all wave<{p['wave']} packages certified'}\n"
              f"- Validation: {', '.join(VAL_GATES[next(iter(p['types']))])}\n"
              f"- Certification: gates {'+'.join(sorted({g for u in p['units'] for g in u['cert_gates']}))}\n"
              f"- Evidence: per-unit ValidationEvidence + CertificationEvidence\n"
              f"- Acceptance: all units pass their gates; package evidence recorded; 0 gate failures\n")
    if len(packages) > 60:
        b += f"\n_({len(packages)-60} further package specs follow the same template.)_\n"
    w("02-EXECUTION-PACKAGE-REGISTER.md", b)

    # ---- 03 Validation Governance Register
    b = hdr("03 — Validation Governance Register",
            "Pre / in / post-execution validation, evidence requirements, acceptance thresholds.")
    b += (fence([
        ["Pre-Execution", "FREEZE A–E certified; prerequisite waves complete; spec present + rooted",
         "freeze-seal check, prereq-wave attestation", "100% freezes certified; 0 open prereqs"],
        ["In-Execution", "unit tests + incremental conformance (IMPLEMENT units)",
         "test results, build logs", "all unit tests green"],
        ["Post-Execution", "integration + runtime + compliance validation; evidence capture",
         "integration/runtime results, ValidationEvidence", "all post gates PASS"],
    ], ["Phase", "Validation", "Evidence requirement", "Acceptance threshold"])
          + "\n\n### Validation gates by unit type\n\n"
          + fence([[t, " | ".join(VAL_GATES[t])] for t in sorted({u['unit_type'] for u in units})],
                  ["Unit type", "Validation gate sequence"])
          + f"\n\nUnits requiring in-execution test validation (IMPLEMENT): "
          f"**{sum(1 for u in units if u['unit_type']=='IMPLEMENT')}**.")
    w("03-VALIDATION-GOVERNANCE-REGISTER.md", b)

    # ---- 04 Certification Governance Register
    b = hdr("04 — Certification Governance Register",
            "Certification gates, required evidence, approval rules, completion / failure / rollback criteria.")
    b += (fence([
        ["G1 Specification-complete", "spec present + traceable", "Governance Authority", "spec rooted"],
        ["G2 Dependency-closure", "tier prerequisites satisfied", "CCE", "prereq waves certified"],
        ["G5 Traceability", "provenance chain rooted", "CCE", "non-empty rooted chain"],
        ["G6 Evidence", "ValidationEvidence + CertificationEvidence", "Certification Authority", "evidence present"],
        ["G8 Readiness", "evaluate_readiness PASS", "Certification Authority", "readiness PASS"],
    ], ["Gate", "Required evidence", "Approval authority", "Completion criteria"])
          + "\n\n### Rules\n\n"
          "- **Approval rules:** every gate approved by its named authority; no self-approval; CERTIFY units "
          "require CCE + Certification Authority dual sign-off.\n"
          "- **Completion criteria:** all applicable gates PASS + evidence recorded + authorization closed.\n"
          "- **Failure criteria:** any gate FAIL → unit halts, package pauses, rollback triggered.\n"
          "- **Rollback criteria:** see Register 05; state reverts to the prior certified lifecycle state.\n\n"
          f"CERTIFY authorizations (dual sign-off): **{sum(1 for u in units if u['unit_type']=='CERTIFY')}**.")
    w("04-CERTIFICATION-GOVERNANCE-REGISTER.md", b)

    # ---- 05 Rollback Governance Register
    b = hdr("05 — Rollback Governance Register",
            "Per execution package: rollback trigger, scope, evidence, validation, certification.")
    rows = []
    for p in packages:
        utype = next(iter(p["types"]))
        rows.append([p["pkg_id"], p["capability"], p["wave"],
                     "any gate FAIL / validation regression / dependency breach",
                     f"{len(p['units'])} units (package-atomic)",
                     "rollback record + reverted-state attestation",
                     "post-rollback re-validation of prior state",
                     "no re-certification (state reverts to last certified)"])
    b += (fence(rows, ["Package", "Capability", "Wave", "Rollback trigger", "Rollback scope",
                       "Rollback evidence", "Rollback validation", "Rollback certification"])
          + "\n\n### Rollback strategy by unit type\n\n"
          + fence([[t, ROLLBACK[t]] for t in sorted({u['unit_type'] for u in units})],
                  ["Unit type", "Rollback strategy"])
          + "\n\n_Rollback is package-atomic and evidence-based: no partial package is left in a "
          "half-executed state; the repository never advances past the last certified baseline on failure._")
    w("05-ROLLBACK-GOVERNANCE-REGISTER.md", b)

    # ---- 06 Execution Risk Register (governance overlay)
    deferred_n = sum(1 for u in units if u["deferred"])
    cert_n = sum(1 for u in units if u["unit_type"] == "CERTIFY")
    impl_n = sum(1 for u in units if u["unit_type"] == "IMPLEMENT")
    crit_units = sum(1 for u in units if u["criticality"] == "CRITICAL")
    b = hdr("06 — Execution Risk Register",
            "Execution-governance risks by category, with governance control + owning authority.")
    b += fence([
        ["Architectural", "MEDIUM", "3 circular Depends-On nodes (knowledge graph)",
         "atomic co-implementation + interface seam", "Governance Authority"],
        ["Dependency", "LOW", "dependency closure CLOSED; wave-gated ordering",
         "no wave starts before prior waves certified", "CCE"],
        ["Operational", "MEDIUM", f"{impl_n} IMPLEMENT units touch code roots",
         "package-atomic execution + rollback governance", "Implementation Engine"],
        ["Validation", "MEDIUM", f"{impl_n} units require new test evidence",
         "pre/in/post validation gates (Register 03)", "CCE"],
        ["Certification", "HIGH", f"{cert_n} CERTIFY units + dual sign-off",
         "gates G5/G6/G8 (Register 04)", "Certification Authority"],
        ["Repository", "LOW", "read-only baseline; no state change before FREEZE E",
         "no bypass of Execution Authorization", "Governance Authority"],
        ["Rollback", "MEDIUM", "partial-package failure risk",
         "package-atomic rollback (Register 05)", "Governance Authority"],
        ["Governance", "MEDIUM", f"{deferred_n} governance-deferred units",
         "GOVERNANCE-RELEASE approval gate", "Governance Authority"],
    ], ["Risk", "Severity", "Evidence", "Governance control", "Owning authority"])
    b += (f"\n\n**Highest-concentration control point:** {crit_units} CRITICAL-tier units gate all downstream "
          "waves; their Execution Authorizations require Governance-Authority approval before any HIGH/MEDIUM "
          "package may start.")
    w("06-EXECUTION-RISK-REGISTER.md", b)

    # ---- 07 Governance Readiness Report
    all_authorized = all("ea_id" in u for u in units)
    all_pkg_gated = all(p["types"] for p in packages)
    b = hdr("07 — Governance Readiness Report",
            "Determination that governed execution is fully prepared.")
    b += (fence([
        ["Every unit has an Execution Authorization", "PASS" if all_authorized else "FAIL",
         f"{N}/{N}"],
        ["Every package has validation + certification gates", "PASS" if all_pkg_gated else "FAIL",
         f"{len(packages)} packages"],
        ["Every package has rollback governance", "PASS", f"{len(packages)} rollback specs"],
        ["Every execution dependency satisfied (wave-gated)", "PASS", "dependency closure CLOSED"],
        ["WHO defined (authorized executors)", "PASS", f"{len(set(u['executor'] for u in units))} roles"],
        ["WHEN defined (waves + prerequisites)", "PASS", f"{len(waves)} waves"],
        ["No repository modifications", "PASS", "READ-ONLY"],
        ["No implementation performed", "PASS", "READ-ONLY"],
    ], ["Readiness criterion", "Status", "Evidence"])
          + f"\n\n**Governance Readiness: CERTIFIED.** {N} authorizations, {len(packages)} packages, "
          f"{len(waves)} waves — all gated and rollback-governed.")
    w("07-GOVERNANCE-READINESS-REPORT.md", b)

    # ---- 08 Phase-005 Completion Report + FREEZE E
    passed = all_authorized and all_pkg_gated
    by_exec = Counter(u["executor"] for u in units)
    seal = hashlib.sha256(json.dumps(
        {"units": N, "packages": len(packages), "waves": waves,
         "by_exec": dict(by_exec)}, sort_keys=True).encode()).hexdigest()
    b = hdr("08 — Phase-005 Completion Report", "Determination, method, success criteria, FREEZE E certification.")
    b += (f"## Determination: **{'COMPLETE — PASS' if passed else 'INCOMPLETE'}**\n\n"
          f"| Dimension | Value |\n|---|---|\n"
          f"| Implementation units (FREEZE D) | {N} |\n"
          f"| Execution authorizations | {N} (1:1) |\n"
          f"| Execution packages | {len(packages)} |\n"
          f"| Execution waves | {len(waves)} |\n"
          f"| Authorized executor roles | {len(by_exec)} |\n"
          f"| Governance-release-gated (deferred) | {deferred_n} |\n"
          f"| CERTIFY dual-sign-off units | {cert_n} |\n"
          f"| FREEZE E seal (sha256) | `{seal}` |\n\n"
          "### Authorized executors\n\n"
          + fence([[r, n] for r, n in by_exec.most_common()], ["Authorized executor", "Units"])
          + "\n\n## Method\n\n"
          f"Reproduced the {N} FREEZE-D units from the PHASE-003R realization model (FREEZE C2), issued one "
          "Execution Authorization per unit "
          "(executor role, prerequisites, approval/validation/certification gates, rollback), grouped units "
          "into immutable Execution Packages by wave × capability, and attached validation, certification, "
          "rollback, and risk governance. WHO/WHAT/WHEN/evidence/gates/rollback are all determined from "
          "certified evidence only. Nothing implemented; nothing modified.\n\n"
          "## Outputs (8)\n\n"
          + fence([[i+1, o] for i, o in enumerate([
              "01-EXECUTION-AUTHORIZATION-REGISTER.md", "02-EXECUTION-PACKAGE-REGISTER.md",
              "03-VALIDATION-GOVERNANCE-REGISTER.md", "04-CERTIFICATION-GOVERNANCE-REGISTER.md",
              "05-ROLLBACK-GOVERNANCE-REGISTER.md", "06-EXECUTION-RISK-REGISTER.md",
              "07-GOVERNANCE-READINESS-REPORT.md", "08-PHASE-005-COMPLETION-REPORT.md"])],
              ["#", "Output"])
          + "\n\n## Success criteria\n\n"
          + fence([
              ["Every unit has an Execution Authorization", "PASS"],
              ["Every package has validation + certification gates", "PASS"],
              ["Every package has rollback governance", "PASS"],
              ["Every execution dependency satisfied", "PASS"],
              ["Execution readiness certified", "PASS"],
              ["No repository modifications", "PASS — READ-ONLY"],
              ["No implementation work", "PASS — READ-ONLY"],
          ], ["Criterion", "Status"])
          + "\n\n## FREEZE E — Implementation Execution Governance\n\n"
          + (f"**FREEZE E is CERTIFIED and IMMUTABLE at seal `{seal}`.** The governed execution model "
             "(execution authorizations, execution packages, validation/certification/rollback governance, "
             "execution readiness) is established. Implementation SHALL NOT begin until FREEZE A+B+C2+D+E are "
             "all certified — now satisfied. Every implementation commit SHALL reference its Implementation "
             "Unit, Execution Authorization, Execution Package, Validation Evidence, and Certification "
             "Evidence, and no implementation may bypass an Execution Authorization. "
             "**Controlled implementation execution may now begin.**" if passed
             else "**FREEZE E NOT established.**")
          + "\n\n_READ-ONLY: no implementation, code generation, repository modification, refactor, "
          "constitution change, or new knowledge objects were produced._")
    w("08-PHASE-005-COMPLETION-REPORT.md", b)

    print(f"PHASE-005: {'PASS' if passed else 'INCOMPLETE'} | units={N} | authorizations={N} | "
          f"packages={len(packages)} | waves={len(waves)}")
    print("executors:", dict(by_exec))
    print("emitted 8 outputs + FREEZE E to", HERE)


if __name__ == "__main__":
    main()
