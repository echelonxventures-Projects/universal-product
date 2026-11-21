#!/usr/bin/env python3
"""UCOS-MXR-001 — deterministic master execution roadmap engine (post UAKOS-CLOSURE-008).

Discovery, extraction, verification, reconciliation and closure are COMPLETE and are NOT
repeated here. This engine performs no discovery, mines no conversation corpus and creates
no replacement documentation. It reads the CURRENT REPOSITORY STATE ONLY and compiles it
into a deterministic execution program: a backlog, a dependency graph, waves, a critical
path, parallel groups, validation and certification gates, and a readiness determination
an autonomous implementation agent can execute without further architectural analysis.

Authoritative in-repo inputs (state of record, read-only)
    00-MASTER/MCP-003-MASTER-EXECUTION.md          MEP-01..MEP-10 master execution program
    00-MASTER/MCP-002-MASTER-STATE.md              §02 blockers · §05 next authorized capability
    00-MASTER/UCDA-000001/ucda-decisions.json      18 registered implementation work packages
    intelligence/UCOS-RIE-AEOS-READINESS.json      G-01..G-12 execution-spine gaps + severity
    intelligence/UCOS-RIE-EXECUTION-FRONTIER.json  declared frontier + critical path
    intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json    declared layered architecture (bottom-up)
    00-MASTER/UAKOS-CLOSURE-002/closure.json       440 concepts: disposition/in_code/certified
    00-MASTER/UAKOS-CLOSURE-008/assimilation.json  homed knowledge items + waves + destinations
    HEAD file evidence                             band realization probes (completion reports,
                                                   freeze modules) — the only measurement taken

Outputs (regenerated deterministically, no timestamps)
    roadmap.json                                   the machine-readable execution program
    01..10-*.md                                    the ten mandated roadmap artifacts

Usage
    python3 00-MASTER/UCOS-MXR-001/roadmap_engine.py
    python3 00-MASTER/UCOS-MXR-001/roadmap_engine.py --gate     # exit 1 unless executable
    python3 00-MASTER/UCOS-MXR-001/roadmap_engine.py --render   # re-render 01..10 from
                                                               # roadmap.json (replay)

`--render` replays the COMMITTED roadmap.json instead of recompiling it, so the HEAD recorded
in the artifacts is the HEAD they were compiled at. A committed artifact can never contain the
sha of the commit that carries it, so a drift gate MUST replay rather than recompile; the
recompile path (`--gate`) proves the program is still derivable from the registers.

AUTHORITY = NONE (DERIVED TRUTH). This engine authorizes nothing, ratifies nothing and
certifies nothing. It orders work that the repository's own registers already own.
Fail-closed (TRACK-001).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PROGRAM = "UCOS-MXR-001"
ROADMAP_JSON = HERE / "roadmap.json"

SRC = {
    "mep": "00-MASTER/MCP-003-MASTER-EXECUTION.md",
    "state": "00-MASTER/MCP-002-MASTER-STATE.md",
    "ucda": "00-MASTER/UCDA-000001/ucda-decisions.json",
    "aeos": "intelligence/UCOS-RIE-AEOS-READINESS.json",
    "frontier": "intelligence/UCOS-RIE-EXECUTION-FRONTIER.json",
    "depgraph": "intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json",
    "closure": "00-MASTER/UAKOS-CLOSURE-002/closure.json",
    "assimilation": "00-MASTER/UAKOS-CLOSURE-008/assimilation.json",
}

# --------------------------------------------------------------------------- readiness states
READY = "READY"
BLOCKED = "BLOCKED"
DEFERRED = "DEFERRED"
W_RAT = "WAITING_FOR_RATIFICATION"
W_IMP = "WAITING_FOR_IMPLEMENTATION"
W_VAL = "WAITING_FOR_VALIDATION"
W_CERT = "WAITING_FOR_CERTIFICATION"
STATES = [READY, BLOCKED, DEFERRED, W_RAT, W_IMP, W_VAL, W_CERT]
# A prerequisite in one of these states cannot be started, so a successor cannot be READY.
NON_EXECUTABLE = (BLOCKED, DEFERRED, W_RAT)
# Owner strings that name no accountable authority. The owner gate rejects them: an item whose
# owner is a placeholder is not assignable, so "every item has an owner" would be vacuous.
PLACEHOLDER_OWNERS = {"", "-", "—", "tbd", "unknown", "owner", "destination owner",
                      "destination owner (see uakos-closure-008)"}

# --------------------------------------------------------------------------- effort model
# Effort is expressed in POINTS on a fixed scale, never in calendar time: the repository
# carries no velocity evidence, so any hour/day figure would be fabricated.
COMPLEXITY_POINTS = {"S": 1, "M": 3, "L": 8, "XL": 20}

# Item classes that are IMPLEMENTATION work. The remaining classes are real obligations but not
# implementation: EVID is certification/validation of concepts already IMPLEMENTED by
# disposition, HYG is a commit and a CI re-run, REPORT is a document, RAT is an out-of-corpus
# constitutional act. Reported separately so the backlog total is never read as an
# implementation total.
IMPLEMENTATION_CLASSES = ("SPINE", "AEOS", "WP", "CONCEPT", "KNOW")

# --------------------------------------------------------------------------- wave policy
WAVES = [
    ("W0", "Repository fixed point & hygiene",
     "Bring the working tree, registration transaction and CI signals to a committed fixed "
     "point so that every later wave starts from reproducible Repository Truth."),
    ("W1", "EC-3 realization spine completion",
     "Close the remaining EC-3 band spine (Band-13 freeze) and the lane go-live + closure "
     "certification, plus the outstanding non-blocking EC-2 report."),
    ("W2", "AEOS execution spine — core runtimes",
     "Make the specified orchestration executable: the completeness and orchestration "
     "runtimes and the scheduler the repository declares HIGH-severity gaps."),
    ("W3", "AEOS execution spine — support, adapters, CLI",
     "The remaining declared spine gaps: concurrency, transactions, recovery, git "
     "orchestration, event-ledger reading, human adapter and the universal CLI."),
    ("W4", "Architectural decision work packages",
     "Discharge the registered implementation work packages that carry accepted "
     "architectural decisions into their located canonical owners."),
    ("W5", "Specified-concept realization",
     "Realize repository concepts whose disposition is SPECIFIED — specified, owned, and "
     "not yet carried by code or artifact."),
    ("W6", "Evidence & certification remediation",
     "Close the recorded evidence defects: concepts dispositioned IMPLEMENTED without code "
     "and implemented concepts that carry no certification."),
    ("W7", "Assimilated knowledge realization (active waves)",
     "Implement the knowledge items UAKOS-CLOSURE-008 homed into active waves 1-7, in the "
     "order their destinations and dependencies dictate."),
    ("WF", "Ratification-gated and authorization-gated futures",
     "Work that cannot start inside the repository: constitutional finality (an out-of-corpus "
     "act) and every DEFERRED/FUTURE entry that awaits explicit authorization."),
]
WAVE_IDS = [w[0] for w in WAVES]

# --------------------------------------------------------------------------- class policy
# Per item class: default complexity, validation command, certification gate, rollback.
CLASS_POLICY: dict[str, dict[str, str]] = {
    "SPINE": dict(
        complexity="L",
        validation="./verify.sh && bash 00-BOOK/tools/register.sh --guard",
        certification="CEP-005 unit certification (CCE CC-1..10) + band certification ledger",
        rollback="additive-only unit: `git revert <realize commit>` then `git revert <REG-AUTO-001 "
                 "sync commit>`; the frozen band baseline digest is unaffected"),
    "HYG": dict(
        complexity="M",
        validation="bash 00-BOOK/tools/register.sh --guard && ./verify.sh",
        certification="none — hygiene items carry no certification obligation",
        rollback="`git reset` the staged registration transaction before commit; after commit "
                 "`git revert` the sync commit (generated content is regenerable)"),
    "REPORT": dict(
        complexity="M",
        validation="./verify.sh && python3 00-BOOK/tools/ukb.py validate",
        certification="registration of the report as a repository artifact (REG-AUTO-001)",
        rollback="`git revert` the report commit; no code path is affected"),
    "AEOS": dict(
        complexity="L",
        validation="./verify.sh && python3 -m pytest engine/tests -o addopts=''",
        certification="CEP-004 validation then CEP-005 certification by the located owner",
        rollback="additive module: `git revert <realize commit>`; no existing certified module "
                 "is modified, so the prior gate state returns unchanged"),
    "WP": dict(
        complexity="M",
        validation="make ucda-gate && ./verify.sh",
        certification="CEP-005 certification recorded against the discharging decision",
        rollback="`git revert` the work-package commit; UCDA disposition returns to "
                 "REGISTERED-AS-IMPLEMENTATION-WORK-PACKAGE"),
    "CONCEPT": dict(
        complexity="M",
        validation="make closure-phase2-gate && ./verify.sh",
        certification="CEP-005 certification once the concept is carried by code or artifact",
        rollback="`git revert` the realization commit; closure.json disposition returns to "
                 "SPECIFIED/DEFERRED on regeneration"),
    "EVID": dict(
        complexity="S",
        validation="make uccep-gate && ./verify.sh",
        certification="CEP-005 certification of the located implementation evidence",
        rollback="`git revert` the evidence commit; no functional change to revert"),
    "KNOW": dict(
        complexity="S",
        validation="make assimilate-gate && ./verify.sh",
        certification="certification by the destination owner under its own constitution",
        rollback="`git revert` the commit; the UAKOS-CLOSURE-008 register re-renders to the "
                 "prior state from assimilation.json"),
    "RAT": dict(
        complexity="XL",
        validation="make cmg-gate  # VAC-01 must report located=true",
        certification="CEP-006 ratification — the only instrument that lifts READY-PROVISIONAL",
        rollback="none available in-repo: the act is out-of-corpus and cannot be reverted by "
                 "this repository"),
}

# Deterministic band-realization evidence probes. These are the ONLY measurements this engine
# takes, and each is a single file-existence test whose meaning is declared here, so the
# register-vs-evidence comparison is machine-checkable rather than interpretive.
BAND_PROBES = [
    dict(band="Band 10 (Data)", mep="MEP-01",
         probe="data/EC3-B10-U12-COMPLETION-REPORT.md",
         means="Band-10 realization certification & completion (U12) is recorded in code evidence"),
    dict(band="Band 11 (Service)", mep="MEP-02",
         probe="service/EC3-B11-U13-COMPLETION-REPORT.md",
         means="Band-11 freeze (U13) is recorded in code evidence"),
    dict(band="Band 12 (Application)", mep="MEP-03",
         probe="00-MASTER/CHECKPOINTS/*EC3-B12-U13*.md",
         means="Band-12 freeze (U13) is recorded — a governance freeze that by design left no "
               "code artifact, so its evidence is the operational-memory checkpoint"),
    dict(band="Band 13 (Infrastructure) realization", mep="MEP-04",
         probe="infrastructure/EC3-B13-U11-COMPLETION-REPORT.md",
         means="Band-13 realization certification & completion (U11) is recorded in code evidence"),
    dict(band="Band 13 freeze (Infrastructure)", mep="MEP-04",
         probe="00-MASTER/CHECKPOINTS/*EC3-B13-U12*.md",
         means="Band-13 freeze (U12) evidence — ABSENT at HEAD, which is why U12 is the open "
               "spine item and matches MCP-002 §05's next authorized capability"),
]


# --------------------------------------------------------------------------- helpers
def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(*args: str) -> str:
    # fixed argv, no shell, no user input.
    out = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=REPO, capture_output=True, text=True, check=False)
    return out.stdout if out.returncode == 0 else ""


def head_commit() -> str:
    return (git("rev-parse", "--short", "HEAD") or "unknown").strip()


def load(kind: str):
    path = REPO / SRC[kind]
    if not path.exists():
        raise SystemExit(f"{PROGRAM}: FAIL-CLOSED — required repository input missing: {SRC[kind]}")
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8")


def cell(text: str) -> str:
    """Normalize a markdown table cell to a single readable line."""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[*`]", "", text)
    return text


def clip(text: str, n: int = 220) -> str:
    text = cell(text)
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


# --------------------------------------------------------------------------- source parsers
def parse_mep(md: str) -> list[dict]:
    """Parse the MEP-01..MEP-nn rows of MCP-003 §02 (the master execution program)."""
    rows = []
    for line in md.splitlines():
        if not line.startswith("| MEP-"):
            continue
        parts = [c for c in line.split("|")][1:-1]
        if len(parts) < 10:
            continue
        rows.append(dict(
            mep=cell(parts[0]), capability=cell(parts[1]), owner=cell(parts[2]),
            depends_on=cell(parts[3]), priority=cell(parts[4]), readiness=cell(parts[5]),
            state=cell(parts[6]), acceptance=cell(parts[7]), exit=cell(parts[8]),
            percent=cell(parts[9])))
    if not rows:
        raise SystemExit(f"{PROGRAM}: FAIL-CLOSED — no MEP rows parsed from {SRC['mep']}")
    return rows


def parse_next_authorized(md: str) -> dict:
    """Extract MCP-002 §05's single answer to 'what do we do next'."""
    seg = md.split("## SECTION 05")[-1].split("## SECTION 06")[0]
    live = seg.split("Superseded snapshot")[0]
    unit = re.search(r"(EC3-B\d\d-U\d\d)", live)
    deferred = "DEFERRED" in live
    return dict(unit=unit.group(1) if unit else "", awaiting_authorization=deferred,
                statement=clip(live.split("**Next Authorized Capability:**")[-1], 320))



def hygiene_status(state: str) -> str:
    """Map a register state onto an implementation status, terminal states included.

    DATA, not a literal ladder: the words come from MCP-003 §02's own state column, so a
    register that starts saying PERFORMED needs no edit here.
    """
    text = str(state or "").upper()
    if any(token in text for token in ("PERFORMED", "SATISFIED", "COMPLETE", "DONE")):
        return "IMPLEMENTED"
    if "PENDING" in text:
        return "AUTHORIZED_PENDING"
    return "PLANNED"

def parse_blockers(md: str) -> list[dict]:
    seg = md.split("## SECTION 02 — BLOCKERS")[-1].split("## SECTION 03")[0]
    out = []
    for line in seg.splitlines():
        if not line.startswith("|") or line.startswith("|--") or "Blocker" in line:
            continue
        parts = [c for c in line.split("|")][1:-1]
        if len(parts) < 4 or cell(parts[0]) in ("", "—"):
            continue
        out.append(dict(id=cell(parts[0]), blocker=clip(parts[1], 200),
                        scope=cell(parts[2]), blocking=cell(parts[3])))
    return out


# --------------------------------------------------------------------------- backlog assembly
def band_evidence() -> list[dict]:
    out = []
    for probe in BAND_PROBES:
        row = dict(probe)
        pattern = probe["probe"]
        if "*" in pattern:
            row["present"] = any(REPO.glob(pattern))
        else:
            row["present"] = (REPO / pattern).exists()
        out.append(row)
    return out


# Zones that are PROJECTIONS or programme records rather than canonical homes: a concept
# whose only hit is a generated registry page or another programme's inventory is owned by
# its family zone, not by that projection.
PROJECTION_PREFIXES = ("00-BOOK/DATA/", "00-BOOK/PORTAL/", "00-BOOK/REGISTRIES/",
                       "00-BOOK/CONTROL-TOWER/", "00-MASTER/UAKOS-", "00-MASTER/CHECKPOINTS/",
                       ".runtime/", "dist/")
# 00-SOURCE/ and 99-FREEZE/ are INVIOLABLE READ-ONLY (PB-04): a concept defined only in a
# frozen source cannot be implemented there, so the implementation target is the family's
# existing canonical zone and the frozen source is recorded as the defining input.
FROZEN_PREFIXES = ("00-SOURCE/", "99-FREEZE/")
FAMILY_ZONE = {
    "LAW": "01-WORKING/LAW-REGISTER.md", "GOV": "01-WORKING/AUTHORITY-REGISTER.md",
    "UCOS-GOV": "01-WORKING/AUTHORITY-REGISTER.md", "UCOS-RAT": "01-WORKING/LAW-REGISTER.md",
    "FOUNDATION": "07-ENGINEERING", "ARCH": "07-ENGINEERING", "METACLASS": "07-ENGINEERING",
    "APPLICATION": "12-APPLICATION", "DATA": "10-DATA", "SERVICE": "11-SERVICE",
    "INFRASTRUCTURE": "13-INFRASTRUCTURE", "PLATFORM": "09-PLATFORM", "RUNTIME": "08-RUNTIME",
    "CEP": "00-CEP", "MEP": "00-MASTER", "EPIC": "00-MASTER", "PHASE": "00-MASTER",
    "UCOS-EXEC": "00-MASTER", "UCOS-COMP": "02-MASTER", "UCOS-RECON": "00-MASTER",
    "UCKO": "00-BOOK/MASTER-BOOK", "UKDA-DEC": "00-MASTER/UCDA-000001",
    "MCP": "00-MASTER", "MCS": "00-MASTER", "EC3-GATE": "02-MASTER", "BAND-UNIT": "02-MASTER",
}


def concept_home(concept: dict) -> str:
    """The concept's canonical home: a defining home if the register recorded one, else the
    first recorded file that is not a generated projection, else the closure register itself."""
    for candidate in (concept.get("def_homes") or []) + (concept.get("exact_homes") or []):
        if candidate and (REPO / candidate).exists():
            return candidate
    for candidate in concept.get("files") or []:
        if candidate.startswith(PROJECTION_PREFIXES):
            continue
        if (REPO / candidate).exists():
            return candidate
    return SRC["closure"]


def resolve_location(*texts: str) -> str:
    """First token in the register text that names a path EXISTING at HEAD, else the work-package
    register itself. Never invents a path: an item whose owner names no existing location is
    owned by the register that carries it."""
    for text in texts:
        for token in re.split(r"[\s·,;()]+", text or ""):
            token = token.strip("`\"'").rstrip(".,;:")
            if not token or "/" not in token:
                continue
            if (REPO / token).exists():
                return token
    return "00-MASTER/UCDA-000001"


def new_item(**kw) -> dict:
    pol = CLASS_POLICY[kw["item_class"]]
    complexity = kw.pop("complexity", None) or pol["complexity"]
    item = dict(
        id=kw["id"], title=kw["title"], item_class=kw["item_class"],
        source=kw["source"], location=kw["location"], owner=kw["owner"],
        depends_on=list(kw.get("depends_on") or []),
        priority=kw.get("priority", "P3"),
        complexity=complexity, effort_points=COMPLEXITY_POINTS[complexity],
        risk=kw.get("risk", "LOW"),
        implementation_status=kw.get("implementation_status", "NOT_STARTED"),
        validation_status=kw.get("validation_status", "NOT_VALIDATED"),
        certification_status=kw.get("certification_status", "NOT_CERTIFIED"),
        readiness=kw.get("readiness", READY),
        wave=kw["wave"],
        validation_command=kw.get("validation_command") or pol["validation"],
        certification_gate=kw.get("certification_gate") or pol["certification"],
        rollback=kw.get("rollback") or pol["rollback"],
        success_criteria=kw.get("success_criteria", ""),
        authorization_required=bool(kw.get("authorization_required", False)),
        note=kw.get("note", ""),
    )
    return item


def build_backlog(data: dict) -> list[dict]:
    items: list[dict] = []
    mep_rows = data["mep_rows"]
    mep_by_id = {r["mep"]: r for r in mep_rows}
    probes = {p["probe"]: p["present"] for p in data["band_evidence"]}
    nxt = data["next_authorized"]

    # ---- W0 hygiene / repository fixed point (MEP-07, MEP-08) ---------------------
    hyg = []
    for mep_id, wave in (("MEP-07", "W0"), ("MEP-08", "W0")):
        r = mep_by_id.get(mep_id)
        if not r:
            continue
        iid = f"MXR-HYG-{len(hyg) + 1:03d}"
        hyg.append(iid)
        items.append(new_item(
            id=iid, title=r["capability"], item_class="HYG",
            source=f"{SRC['mep']} §02 {mep_id}", location="00-BOOK/DATA",
            owner=r["owner"], priority="P2", risk="MEDIUM",
            # A HYGIENE ITEM MUST BE ABLE TO READ AS DONE. This mapping had exactly two
            # outcomes -- AUTHORIZED_PENDING when the register said PENDING, PLANNED
            # otherwise -- and neither is terminal. So W0 could never close no matter what
            # MCP-003 recorded, and the roadmap's own fourth condition ("the repository
            # fixed point (W0) must be committed first") was unsatisfiable by construction
            # rather than by fact. Measured: MEP-07 was performed on 2026-09-15 and still
            # reported PLANNED. The register's word is honoured here instead of collapsed.
            implementation_status=hygiene_status(r["state"]),
            readiness=READY, wave=wave,
            success_criteria=clip(r["exit"], 200) or clip(r["acceptance"], 200),
            note=f"register readiness={r['readiness']} · state={r['state']}"))

    # ---- W1 EC-3 spine ------------------------------------------------------------
    spine_ids = []
    b13_freeze_done = probes.get("00-MASTER/CHECKPOINTS/*EC3-B13-U12*.md", False)
    if not b13_freeze_done:
        iid = "MXR-SPINE-001"
        spine_ids.append(iid)
        items.append(new_item(
            id=iid,
            title=f"{nxt['unit'] or 'EC3-B13-U12'} — Band-13 Freeze (baseline establishment & "
                  "transition authorization)",
            item_class="SPINE", source=f"{SRC['state']} §05 (next authorized capability)",
            location="infrastructure", owner="EC-3 Executor (MEP-04)",
            priority="P1", risk="MEDIUM", depends_on=list(hyg),
            implementation_status="NOT_STARTED", readiness=DEFERRED if
            nxt["awaiting_authorization"] else READY,
            authorization_required=bool(nxt["awaiting_authorization"]), wave="W1",
            success_criteria="Band-13 immutable content-addressed baseline sealed (FP-1..6 "
                             "preconditions, FE-1..5 effects) mirroring the CERTIFIED Band-11/12 "
                             "U13 freeze; determinism byte-identical; zero registration drift",
            note="charter EC-3-B13-P01 §9 Stage 8; U01…U11 are CERTIFIED & COMPLETE per "
                 "MCP-002 §05 and infrastructure/EC3-B13-U11-COMPLETION-REPORT.md, while no "
                 "EC3-B13-U12 evidence exists at HEAD"))
    r5 = mep_by_id.get("MEP-05")
    if r5 and "CERTIFIED" not in r5["state"]:
        items.append(new_item(
            id="MXR-SPINE-002", title=r5["capability"], item_class="SPINE",
            source=f"{SRC['mep']} §02 MEP-05", location="02-MASTER",
            owner=r5["owner"], priority="P4", risk="MEDIUM",
            depends_on=list(spine_ids) or list(hyg),
            implementation_status="PLANNED", readiness=W_IMP, wave="W1",
            success_criteria=clip(r5["exit"], 200) or clip(r5["acceptance"], 200),
            note=f"register state={r5['state']} · depends_on={r5['depends_on']}"))
        spine_ids.append("MXR-SPINE-002")
    r6 = mep_by_id.get("MEP-06")
    if r6 and "CERTIFIED" not in r6["state"]:
        items.append(new_item(
            id="MXR-REPORT-001", title=r6["capability"], item_class="REPORT",
            source=f"{SRC['mep']} §02 MEP-06", location="14-SECURITY",
            owner=r6["owner"], priority="P3", risk="LOW",
            implementation_status="PLANNED", readiness=READY, wave="W1",
            success_criteria=clip(r6["exit"], 200) or clip(r6["acceptance"], 200),
            note="declared non-blocking in the register"))

    # ---- W2/W3 AEOS execution spine (declared gaps G-01..G-12) --------------------
    aeos = data["aeos"]
    sev_wave = {"HIGH": "W2", "MEDIUM": "W3", "LOW": "W3"}
    sev_complexity = {"HIGH": "L", "MEDIUM": "M", "LOW": "S"}
    aeos_ids = []
    layers = data["layered_architecture"]
    adapters_layer = next((i for i, layer in enumerate(layers) if "adapter" in layer.lower()), None)
    spine_layer = next((i for i, layer in enumerate(layers) if "AEOS" in layer), None)
    core_ids = []
    for gap in aeos["known_spine_gaps"]:
        gid = gap["id"]
        sev = gap["severity"]
        is_adapter = ("adapter" in gap["missing"].lower() or "CLI" in gap["missing"])
        iid = f"MXR-AEOS-{gid.split('-')[1]}"
        wave = "W3" if is_adapter else sev_wave[sev]
        deps = list(core_ids) if is_adapter else list(hyg)
        items.append(new_item(
            id=iid, title=f"{gid} — {gap['missing']}", item_class="AEOS",
            source=f"{SRC['aeos']} known_spine_gaps", location="engine",
            owner="engine/ (EC-1 substrate) · platform/ (EC-2 surface) — WP-UCDA-002 owner",
            priority="P1" if sev == "HIGH" else "P2" if sev == "MEDIUM" else "P3",
            complexity=sev_complexity[sev],
            risk="HIGH" if sev == "HIGH" else "MEDIUM" if sev == "MEDIUM" else "LOW",
            depends_on=deps, implementation_status="NOT_STARTED",
            readiness=DEFERRED, authorization_required=True, wave=wave,
            success_criteria=f"{gap['missing']} exists as executable code under engine/ or "
                             "platform/, validated (CEP-004) and certified (CEP-005) by its "
                             "located owner; the AEOS readiness artifact no longer lists "
                             f"{gid} under not_ready_because",
            note=f"declared severity {sev}; layer order from {SRC['depgraph']}: spine index "
                 f"{spine_layer} precedes adapters/CLI index {adapters_layer}"))
        aeos_ids.append(iid)
        if not is_adapter and sev == "HIGH":
            core_ids.append(iid)

    # ---- W4 UCDA registered implementation work packages -------------------------
    wp_ids = []
    rat_ids = []
    for wp in data["ucda"]["work_packages"]:
        wid = wp["id"]
        is_rat = "ratification" in wp["title"].lower() or "DR-RAT-11" in " ".join(wp["discharges"])
        is_aeos = "AEOS" in wp["title"]
        # THE STREAM SEGMENT IS PART OF THE IDENTITY, NOT DECORATION. Taking only the last
        # segment collapsed WP-UCDA-001, WP-W3-001, WP-W5-001 and WP-W6-001 onto one id and
        # WP-UCDA-002, WP-W1-002 onto another. graph_analysis keys by id, so the duplicates
        # vanished into the dict and `len(items) - len(topological_order)` reported them as
        # three unordered items — a UCKP-ART-03 duplication surfacing as an ordering fault,
        # which is why the gate named the wrong defect. The source id is unique; carry it.
        iid = f"MXR-{wid}"
        if is_rat:
            iid = f"MXR-RAT-{wid.removeprefix('WP-')}"
            items.append(new_item(
                id=iid, title=wp["title"], item_class="RAT",
                source=f"{SRC['ucda']} work_packages {wid}",
                location="00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md",
                owner=clip(wp["owner"], 180), priority="P0", risk="HIGH",
                implementation_status="BLOCKED_EXTERNAL", readiness=W_RAT,
                authorization_required=True, wave="WF",
                success_criteria=clip(wp["acceptance"], 260),
                note="out-of-corpus stakeholder act: not executable inside this repository"))
            rat_ids.append(iid)
            continue
        deps = list(aeos_ids) if is_aeos else list(hyg)
        items.append(new_item(
            id=iid, title=wp["title"], item_class="WP",
            source=f"{SRC['ucda']} work_packages {wid}",
            location=resolve_location(wp["owner"], wp.get("route", "")),
            owner=clip(wp["owner"], 180),
            priority="P1" if is_aeos else "P2",
            complexity="XL" if is_aeos else "M",
            risk="HIGH" if is_aeos else "MEDIUM",
            depends_on=deps, implementation_status="NOT_STARTED",
            readiness=DEFERRED if wp.get("authorization_required") else READY,
            authorization_required=bool(wp.get("authorization_required")),
            wave="W3" if is_aeos else "W4",
            success_criteria=clip(wp["acceptance"], 260),
            note=f"route: {clip(wp['route'], 200)}"))
        wp_ids.append(iid)

    # ---- W5/WF specified & deferred concepts (closure.json) ----------------------
    closure = data["closure"]
    n_spec = n_def = 0
    for concept in closure["concepts"]:
        disp = concept.get("disposition")
        if disp not in ("SPECIFIED", "DEFERRED"):
            continue
        family = concept.get("family") or "UNKNOWN"
        home = concept_home(concept)
        frozen_source = home if home.startswith(FROZEN_PREFIXES) else ""
        if frozen_source:
            home = FAMILY_ZONE.get(family, "02-MASTER")
        law_gated = family in ("LAW", "GOV", "UCOS-GOV", "PHASE")
        if disp == "SPECIFIED":
            n_spec += 1
            iid = f"MXR-CONCEPT-S{n_spec:03d}"
            readiness = W_RAT if law_gated else READY
            wave = "WF" if law_gated else "W5"
        else:
            n_def += 1
            iid = f"MXR-CONCEPT-D{n_def:03d}"
            readiness = DEFERRED
            wave = "WF"
        items.append(new_item(
            id=iid, title=f"{concept['id']} — realize {disp.lower()} concept ({family})",
            item_class="CONCEPT", source=f"{SRC['closure']} concepts[{concept['id']}]",
            location=home,
            owner=f"{family} family owner (canonical home: {home})",
            priority="P2" if disp == "SPECIFIED" else "P3",
            complexity="M" if disp == "SPECIFIED" else "S",
            risk="MEDIUM" if law_gated else "LOW",
            depends_on=list(rat_ids) if law_gated else [],
            implementation_status="SPECIFIED" if disp == "SPECIFIED" else "DEFERRED",
            validation_status="NOT_VALIDATED",
            certification_status="CERTIFIED" if concept.get("certified") else "NOT_CERTIFIED",
            readiness=readiness, wave=wave,
            authorization_required=(disp == "DEFERRED"),
            success_criteria=f"{concept['id']} is carried by code or a canonical artifact, "
                             "closure regeneration reports disposition IMPLEMENTED, and the "
                             "concept's certification flag is set by its owner",
            note=f"in_code={concept.get('in_code')} · certified={concept.get('certified')} · "
                 f"homes={len(concept.get('files') or [])}"
                 + (f" · defining source (frozen, read-only per PB-04): {frozen_source}"
                    if frozen_source else "")))

    # ---- W6 evidence & certification remediation --------------------------------
    n_evid = 0
    for concept in closure["concepts"]:
        if concept.get("disposition") != "IMPLEMENTED":
            continue
        no_code = not concept.get("in_code")
        no_cert = not concept.get("certified")
        if not (no_code or no_cert):
            continue
        n_evid += 1
        iid = f"MXR-EVID-{n_evid:03d}"
        kind = ("implementation evidence" if no_code else "certification")
        items.append(new_item(
            id=iid,
            title=f"{concept['id']} — supply missing {kind} for an IMPLEMENTED concept",
            item_class="EVID", source=f"{SRC['closure']} concepts[{concept['id']}]",
            location=(FAMILY_ZONE.get(concept.get("family") or "", "02-MASTER")
                      if concept_home(concept).startswith(FROZEN_PREFIXES)
                      else concept_home(concept)),
            owner=f"{concept.get('family')} family owner",
            priority="P2" if no_code else "P3",
            risk="MEDIUM" if no_code else "LOW",
            implementation_status="IMPLEMENTED_BY_DISPOSITION",
            validation_status="NOT_VALIDATED" if no_code else "VALIDATED",
            certification_status="NOT_CERTIFIED" if no_cert else "CERTIFIED",
            readiness=W_VAL if no_code else W_CERT, wave="W6",
            success_criteria=("code evidence exists for the concept and closure regeneration "
                              "reports in_code=true" if no_code else
                              "a certification record exists and closure regeneration reports "
                              "certified=true"),
            note=f"in_code={concept.get('in_code')} · certified={concept.get('certified')} — "
                 "recorded defect class VERIFICATION E-02"))

    # ---- W7 assimilated knowledge items in active waves -------------------------
    assim = data["assimilation"]
    cols = assim.get("row_columns") or []
    # `assimilation.json` serializes `owner`/`authority` as DERIVED columns — UAKOS-CLOSURE-008
    # rehydrates them from its destination policy at render time, so the serialized row carries
    # neither. The canonical owner is therefore recovered here from that same register's own
    # `destination_policy` (keyed by disposition, DOCUMENTATION as the declared fallback), which
    # is the identical deterministic map. No placeholder owner is ever emitted.
    dest_policy = assim.get("destination_policy") or {}

    def know_owner(row: dict) -> str:
        pol = (dest_policy.get(str(row.get("disposition")))
               or dest_policy.get("DOCUMENTATION") or {})
        return str(pol.get("owner") or "")

    def know_authority(row: dict) -> str:
        pol = (dest_policy.get(str(row.get("disposition")))
               or dest_policy.get("DOCUMENTATION") or {})
        return str(pol.get("authority") or "")

    kid_to_item: dict[str, str] = {}
    know_rows = []
    for row in assim["rows"]:
        r = dict(zip(cols, row, strict=False))
        if r.get("state") != "ASSIMILATED" or str(r.get("wave")) in ("F", ""):
            continue
        know_rows.append(r)
    know_rows.sort(key=lambda r: (str(r["wave"]), str(r["priority"]), str(r["kid"])))
    for n, r in enumerate(know_rows, 1):
        iid = f"MXR-KNOW-{n:04d}"
        kid_to_item[r["kid"]] = iid
    for n, r in enumerate(know_rows, 1):
        iid = f"MXR-KNOW-{n:04d}"
        # The knowledge dependency evidence is SYMMETRIC (co-occurrence), so it carries no
        # direction. Direction is resolved deterministically by the register's own ordering
        # (wave → priority → KID): an edge is kept only when it points to an EARLIER item.
        # This is acyclic by construction and adds no invented precedence.
        deps = [kid_to_item[k] for k in (r.get("dependencies") or [])
                if k in kid_to_item and kid_to_item[k] < iid]
        pri = str(r.get("priority") or "P3")
        items.append(new_item(
            id=iid, title=f"{r['kid']} — {r['name']} ({r['category']})", item_class="KNOW",
            source=f"{SRC['assimilation']} rows[{r['kid']}]",
            location=str(r.get("destination") or "00-MASTER/UAKOS-CLOSURE-008"),
            owner=know_owner(r),
            priority=pri, complexity="M" if pri in ("P0", "P1") else "S",
            risk="MEDIUM" if pri == "P0" else "LOW",
            depends_on=deps, implementation_status="HOMED_NOT_IMPLEMENTED",
            readiness=READY if pri in ("P0", "P1") else DEFERRED,
            authorization_required=pri not in ("P0", "P1"),
            wave="W7",
            success_criteria=f"the concept is carried by its canonical destination "
                             f"({r.get('destination')}) and UAKOS-CLOSURE-008 regeneration moves "
                             "it out of the ASSIMILATED state into ALREADY-REPRESENTED",
            note=f"assimilation wave {r.get('wave')} · maturity {r.get('maturity')} · "
                 f"{r.get('origin_conversations')} evidence conversations · constitutional "
                 f"authority {know_authority(r)} · readiness, authorization flag and complexity "
                 f"derived from the evidence priority {pri} (see register 01 §derivation)"))

    # ---- WF constitutional finality (MEP-09) ------------------------------------
    r9 = mep_by_id.get("MEP-09")
    if r9:
        items.append(new_item(
            id="MXR-RAT-002", title=r9["capability"], item_class="RAT",
            source=f"{SRC['mep']} §02 MEP-09",
            location="00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md",
            owner=r9["owner"], priority="P0", risk="HIGH",
            depends_on=list(rat_ids), implementation_status="BLOCKED_EXTERNAL",
            readiness=W_RAT, authorization_required=True, wave="WF",
            success_criteria=clip(r9["exit"], 220) or clip(r9["acceptance"], 220),
            note=f"register readiness={r9['readiness']} · state={r9['state']} — external act"))
    items.sort(key=lambda i: (WAVE_IDS.index(i["wave"]), i["id"]))
    return apply_readiness_closure(items)


def apply_readiness_closure(items: list[dict]) -> list[dict]:
    """A READY item whose prerequisite cannot itself be started is not READY — it is BLOCKED.

    Per-source readiness is assigned from each register's own fields, which describe an item in
    isolation. This pass closes readiness over the dependency graph so that BLOCKED is a MEASURED
    state rather than an unreachable one, and so that `READY` means what it says: startable now.
    Propagated to a fixpoint (the graph is acyclic, so this terminates) and deterministic — the
    iteration follows the already-sorted item order.
    """
    by_id = {i["id"]: i for i in items}
    changed = True
    while changed:
        changed = False
        for i in items:
            if i["readiness"] != READY:
                continue
            for d in i["depends_on"]:
                dep = by_id.get(d)
                if dep is not None and dep["readiness"] in NON_EXECUTABLE:
                    i["readiness"] = BLOCKED
                    i["note"] = ((i["note"] + " · ") if i["note"] else "") + (
                        f"BLOCKED — prerequisite {d} is {dep['readiness']}; releasing that "
                        "prerequisite releases this item")
                    changed = True
                    break
    return items


# --------------------------------------------------------------------------- graph analytics
def graph_analysis(items: list[dict]) -> dict:
    by_id = {i["id"]: i for i in items}
    edges = {i["id"]: [d for d in i["depends_on"] if d in by_id] for i in items}
    successors: dict[str, list[str]] = defaultdict(list)
    for iid, deps in edges.items():
        for d in deps:
            successors[d].append(iid)

    wave_rank = {i["id"]: WAVE_IDS.index(i["wave"]) for i in items}
    indeg = {iid: len(deps) for iid, deps in edges.items()}
    queue = deque(sorted(iid for iid, d in indeg.items() if d == 0))
    order: list[str] = []
    level = {iid: 0 for iid in edges}
    while queue:
        iid = queue.popleft()
        order.append(iid)
        for succ in sorted(successors[iid]):
            level[succ] = max(level[succ], level[iid] + 1)
            indeg[succ] -= 1
            if indeg[succ] == 0:
                queue.append(succ)
    cyclic = [iid for iid, d in indeg.items() if d > 0]

    # Effort-weighted longest path (the critical path) over the acyclic order. It is computed
    # TWICE: once over the in-repository executable subgraph (the path an agent can actually
    # walk) and once over the out-of-corpus ratification chain, which is longer in effort but
    # cannot be executed here. Conflating the two would misreport the engineering floor.
    def longest_path(pred) -> tuple[list[str], int]:
        dist: dict[str, int] = {}
        prev: dict[str, str | None] = {}
        for iid in order:
            if not pred(by_id[iid]):
                continue
            best, bestp = 0, None
            for d in edges[iid]:
                if pred(by_id[d]) and dist.get(d, 0) > best:
                    best, bestp = dist[d], d
            dist[iid] = best + by_id[iid]["effort_points"]
            prev[iid] = bestp
        if not dist:
            return [], 0
        end = max(dist, key=lambda k: (dist[k], k))
        chain: list[str] = []
        node: str | None = end
        while node:
            chain.append(node)
            node = prev.get(node)
        chain.reverse()
        return chain, dist[end]

    crit, crit_points = longest_path(lambda i: i["item_class"] != "RAT")
    ext, ext_points = longest_path(lambda i: i["item_class"] == "RAT")

    # parallel groups = topological levels; independent workstreams = weakly connected comps
    groups: dict[int, list[str]] = defaultdict(list)
    for iid in order:
        groups[level[iid]].append(iid)
    parent = {iid: iid for iid in edges}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for iid, deps in edges.items():
        for d in deps:
            ra, rb = find(iid), find(d)
            if ra != rb:
                parent[ra] = rb
    comps: dict[str, list[str]] = defaultdict(list)
    for iid in edges:
        comps[find(iid)].append(iid)

    # The EXECUTION order is the topological order re-sorted by (wave → level → priority → id).
    # It remains a valid topological order because no item may depend on a later wave (gated)
    # and every dependency sits at a strictly lower level, so it always sorts earlier.
    execution_order = sorted(
        order, key=lambda iid: (wave_rank[iid], level[iid], by_id[iid]["priority"], iid))
    return dict(
        topological_order=execution_order,
        discovery_order=order,
        cyclic=cyclic,
        acyclic=not cyclic,
        edge_count=sum(len(v) for v in edges.values()),
        critical_path=crit,
        critical_path_points=crit_points,
        critical_path_length=len(crit),
        external_chain=ext,
        external_chain_points=ext_points,
        levels={str(k): sorted(v) for k, v in sorted(groups.items())},
        level_of={k: level[k] for k in sorted(level)},
        workstreams=[sorted(v) for _, v in sorted(comps.items(), key=lambda kv: sorted(kv[1])[0])],
        successors={k: sorted(v) for k, v in sorted(successors.items())},
    )


# --------------------------------------------------------------------------- gates
def run_gates(items: list[dict], graph: dict, data: dict) -> list[dict]:
    by_id = {i["id"]: i for i in items}
    missing_dep = sorted({d for i in items for d in i["depends_on"] if d not in by_id})
    bad_loc = [i["id"] for i in items if not (REPO / i["location"]).exists()]
    no_owner = [i["id"] for i in items
                if str(i["owner"]).strip().lower() in PLACEHOLDER_OWNERS]
    no_cmd = [i["id"] for i in items if not i["validation_command"]]
    no_dod = [i["id"] for i in items if not i["success_criteria"]]
    no_rb = [i["id"] for i in items if not i["rollback"]]
    bad_state = [i["id"] for i in items if i["readiness"] not in STATES]
    # A READY item may not depend on an item that cannot be started (see
    # apply_readiness_closure). This gate proves the closure held.
    unclosed = [f"{i['id']}→{d}" for i in items if i["readiness"] == READY
                for d in i["depends_on"]
                if d in by_id and by_id[d]["readiness"] in NON_EXECUTABLE]
    # wave order must not be violated: no item may depend on an item in a later wave
    wave_viol = [f"{i['id']}→{d}" for i in items for d in i["depends_on"]
                 if d in by_id and WAVE_IDS.index(by_id[d]["wave"]) > WAVE_IDS.index(i["wave"])]
    unordered = len(items) - len(graph["topological_order"])
    ready = [i for i in items if i["readiness"] == READY]
    # Register/evidence staleness is MEASURED, not enumerated: any band probe that is present at
    # HEAD while its MEP row in MCP-003 §02 does not record CERTIFIED-COMPLETE is a divergence
    # between the register and the measurement. Recorded for the register's owner, never resolved
    # here (correcting MCP-003 is the Master Execution Authority's act).
    stale = []
    for p in data["band_evidence"]:
        state = str(data["mep_by_id"].get(p["mep"], {}).get("state", ""))
        if p["present"] and "CERTIFIED-COMPLETE" not in state.upper():
            stale.append((p, state))

    gates = [
        dict(gate="Dependency graph is acyclic", blocking=True,
             count=len(graph["cyclic"]), detail=graph["cyclic"][:5]),
        dict(gate="Every dependency resolves to a backlog item", blocking=True,
             count=len(missing_dep), detail=missing_dep[:5]),
        dict(gate="Every item has an EXISTING repository location", blocking=True,
             count=len(bad_loc), detail=bad_loc[:5]),
        dict(gate="Every item has a named owner (no placeholder)", blocking=True,
             count=len(no_owner), detail=no_owner[:5]),
        dict(gate="Every item has a validation command", blocking=True,
             count=len(no_cmd), detail=no_cmd[:5]),
        dict(gate="Every item has a Definition of Done", blocking=True,
             count=len(no_dod), detail=no_dod[:5]),
        dict(gate="Every item has a rollback strategy", blocking=True,
             count=len(no_rb), detail=no_rb[:5]),
        dict(gate="Every item holds exactly one readiness state", blocking=True,
             count=len(bad_state), detail=bad_state[:5]),
        dict(gate="No READY item depends on a non-executable prerequisite", blocking=True,
             count=len(unclosed), detail=unclosed[:5]),
        dict(gate="No wave depends on a later wave", blocking=True,
             count=len(wave_viol), detail=wave_viol[:5]),
        dict(gate="Deterministic execution order covers every item", blocking=True,
             count=unordered, detail=[]),
        dict(gate="At least one item is READY (the program can start)", blocking=True,
             count=0 if ready else 1, detail=[] if ready else ["no READY item"]),
        dict(gate="Register/evidence staleness recorded, not silently resolved", blocking=False,
             count=len(stale), detail=[f"{p['mep']}: {p['probe']} present at HEAD but register "
                                      f"state is {state or 'unparsed'}" for p, state in stale]),
    ]
    for g in gates:
        g["result"] = "PASS" if g["count"] == 0 else ("FAIL" if g["blocking"] else "REPORTED")
    return gates


# --------------------------------------------------------------------------- build
def build() -> dict:
    mep_md = load("mep")
    state_md = load("state")
    ucda = load("ucda")
    aeos = load("aeos")
    frontier = load("frontier")
    depgraph = load("depgraph")
    closure = load("closure")
    assimilation = load("assimilation")

    mep_rows = parse_mep(mep_md)
    data = dict(
        mep_rows=mep_rows,
        mep_by_id={r["mep"]: r for r in mep_rows},
        next_authorized=parse_next_authorized(state_md),
        blockers=parse_blockers(state_md),
        ucda=ucda,
        aeos=aeos,
        frontier=dict(ready=frontier.get("ready"), blocked=frontier.get("blocked"),
                      critical_path=frontier.get("critical_path"),
                      next_executable_capability=frontier.get("next_executable_capability"),
                      single_active_frontier=frontier.get("single_active_frontier")),
        layered_architecture=depgraph.get("layered_architecture_bottom_up") or [],
        closure=closure,
        assimilation=assimilation,
        band_evidence=band_evidence(),
    )

    items = build_backlog(data)
    graph = graph_analysis(items)
    gates = run_gates(items, graph, data)

    ready = [i for i in items if i["readiness"] == READY]
    blocked = [i for i in items if i["readiness"] == BLOCKED]
    deferred = [i for i in items if i["readiness"] == DEFERRED]
    rat = [i for i in items if i["readiness"] == W_RAT]
    blocking_fail = [g for g in gates if g["blocking"] and g["result"] == "FAIL"]

    conditions = []
    if rat:
        conditions.append(
            # NOT "an out-of-corpus act". UCCEP-F-004 amended exactly that wording: the
            # constituent act was performed IN corpus (UCOS-RAT-002, CMG T1 LOCATED), and
            # what remains is CEP-006 I.4's cap on in-corpus determinations -- a ceiling,
            # not an errand. Describing a designed cap as an outstanding act reports the
            # programme as waiting on something nobody is going to do.
            f"{len(rat)} item(s) WAITING_FOR_RATIFICATION — the ratification AUTHORITY is "
            "constituted (UCOS-RAT-002 enacted; CMG T1 LOCATED). These items await their own "
            "ratification record; the certification ceiling stays CERTIFIED-PROVISIONAL by "
            "CEP-006 I.4 regardless, which is a designed cap and not an open condition")
    auth = [i for i in items if i["authorization_required"] and i["wave"] != "WF"]
    if auth:
        conditions.append(
            f"{len(auth)} active-wave item(s) require explicit authorization before start "
            "(the repository's standing STOP rule: no capability begins unauthorized)")
    if blocked:
        conditions.append(
            f"{len(blocked)} item(s) BLOCKED — a prerequisite is authorization-gated or awaiting "
            "ratification, so the successor cannot start until that prerequisite is released; "
            "releasing the prerequisite releases the successor with no further act")
    # FIRES ON WHAT IS OUTSTANDING, NOT ON WHAT EXISTS. This tested only whether a
    # hygiene item was PRESENT, so W0 was reported as an open condition even with every
    # item discharged -- and the text asserted both were "recorded as pending" whatever
    # the register said. MEP-07 was performed on 2026-09-15 and this line still claimed it.
    open_hyg = [i for i in items
                if i["item_class"] == "HYG" and i["implementation_status"] != "IMPLEMENTED"]
    if open_hyg:
        conditions.append(
            f"the repository fixed point (W0) is not closed: {len(open_hyg)} hygiene item(s) "
            f"outstanding in MCP-003 §02 ({', '.join(i['title'] for i in open_hyg)})")

    if blocking_fail:
        verdict = "NO-GO"
    elif conditions:
        verdict = "CONDITIONAL GO"
    else:
        verdict = "GO"

    # completion percentage: measured over the repository's own concept model, not over the
    # backlog (a backlog is not a denominator).
    disp = closure["dispositions"]
    total_concepts = closure["concept_total"]
    implemented = disp.get("IMPLEMENTED", 0)
    certified = sum(1 for c in closure["concepts"] if c.get("certified"))
    in_code = sum(1 for c in closure["concepts"] if c.get("in_code"))

    payload = dict(
        program=PROGRAM,
        mission="Master execution roadmap — deterministic implementation execution program",
        authority="NONE — DERIVED TRUTH (fail-closed, TRACK-001)",
        head_commit=head_commit(),
        inputs={k: dict(path=v, sha256=sha256_text((REPO / v).read_text(
            encoding="utf-8", errors="replace"))) for k, v in SRC.items()},
        band_evidence=data["band_evidence"],
        next_authorized=data["next_authorized"],
        blockers=data["blockers"],
        declared_frontier=data["frontier"],
        layered_architecture=data["layered_architecture"],
        waves=[dict(id=w[0], objective=w[1], description=w[2]) for w in WAVES],
        wave_totals={
            w[0]: dict(
                items=sum(1 for i in items if i["wave"] == w[0]),
                effort_points=sum(i["effort_points"] for i in items if i["wave"] == w[0]))
            for w in WAVES},
        class_totals=dict(Counter(i["item_class"] for i in items)),
        readiness_totals={s: sum(1 for i in items if i["readiness"] == s) for s in STATES},
        priority_totals=dict(Counter(i["priority"] for i in items)),
        risk_totals=dict(Counter(i["risk"] for i in items)),
        total_items=len(items),
        implementation_items=sum(1 for i in items
                                 if i["item_class"] in IMPLEMENTATION_CLASSES),
        implementation_classes=list(IMPLEMENTATION_CLASSES),
        total_effort_points=sum(i["effort_points"] for i in items),
        ready_count=len(ready),
        blocked_count=len(blocked),
        deferred_count=len(deferred),
        waiting_for_ratification_count=len(rat),
        parallelizable_count=sum(len(v) for k, v in graph["levels"].items() if len(v) > 1),
        workstream_count=len(graph["workstreams"]),
        registered_future_pool=dict(
            source=SRC["assimilation"],
            wave_F_items=assimilation["assimilation_waves"].get("F", 0),
            note="registered DEFERRED/FUTURE knowledge entries — homed and owned, excluded "
                 "from the active backlog because their evidence carries no human commitment; "
                 "promoting them into work would fabricate a decision"),
        concept_model=dict(
            total=total_concepts, implemented=implemented,
            specified=disp.get("SPECIFIED", 0), deferred=disp.get("DEFERRED", 0),
            rejected=disp.get("REJECTED", 0), certified=certified, in_code=in_code),
        completion=dict(
            disposition_implemented_pct=round(100.0 * implemented / total_concepts, 1),
            certified_pct=round(100.0 * certified / total_concepts, 1),
            in_code_pct=round(100.0 * in_code / total_concepts, 1),
            ec3_bands_complete=sum(1 for p in data["band_evidence"] if p["present"]),
            ec3_band_probes=len(data["band_evidence"])),
        graph=graph,
        gates=gates,
        conditions=conditions,
        verdict=verdict,
        items=items,
    )
    seal = json.dumps({k: v for k, v in payload.items() if k != "seal_sha256"},
                      sort_keys=True, separators=(",", ":"))
    payload["seal_sha256"] = hashlib.sha256(seal.encode("utf-8")).hexdigest()
    return payload


# --------------------------------------------------------------------------- rendering
HDR = (
    "> PROGRAM {program} · MASTER EXECUTION ROADMAP (post UAKOS-CLOSURE-008) · HEAD `{head}` · "
    "AUTHORITY = NONE (DERIVED TRUTH) · generated by `roadmap_engine.py`\n>\n"
    "> Compiled from the CURRENT REPOSITORY STATE ONLY — MCP-002/MCP-003 (state of record), "
    "UCDA-000001 work packages, the RIE intelligence artifacts, `closure.json`, "
    "`assimilation.json` and HEAD file evidence. No discovery, no re-extraction, no "
    "reconciliation, no replacement documentation. Fail-closed.\n"
)


def header(p: dict, num: str, title: str, subtitle: str) -> list[str]:
    return [f"# {num} — {title}", "",
            HDR.format(program=p["program"], head=p["head_commit"]), f"> {subtitle}", ""]


def pct(n: int, d: int) -> str:
    return f"{(100.0 * n / d):.1f}%" if d else "—"


def table(head: list[str], rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    out.append("")
    return out


def write(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def render(p: dict) -> list[str]:
    items = p["items"]
    by_id = {i["id"]: i for i in items}
    g = p["graph"]
    written = []

    def wave_items(wid: str) -> list[dict]:
        return [i for i in items if i["wave"] == wid]

    # ---------------------------------------------------------------- 01 roadmap
    L = header(p, "01", "Master Execution Roadmap",
               "What remains to be implemented, in the order it must be implemented, derived "
               "from the repository's own registers and HEAD evidence.")
    L += table(["Field", "Value"], [
        ["Total remaining backlog items", p["total_items"]],
        ["— of which implementation work",
         f"{p['implementation_items']} (classes "
         f"{', '.join(p['implementation_classes'])}; the remaining "
         f"{p['total_items'] - p['implementation_items']} are certification/validation, hygiene, "
         "report and out-of-corpus ratification obligations)"],
        ["Total effort", f"{p['total_effort_points']} points (fixed scale S=1/M=3/L=8/XL=20)"],
    ] + [[s, p["readiness_totals"][s]] for s in STATES] + [
        ["Independent workstreams", p["workstream_count"]],
        ["Critical path length", f"{g['critical_path_length']} items · "
                                f"{g['critical_path_points']} points"],
        ["Implementation waves", len([w for w in p["waves"]
                                     if p["wave_totals"][w["id"]]["items"] > 0])],
        ["Verdict", f"**{p['verdict']}**"],
        ["Seal (sha256)", f"`{p['seal_sha256']}`"],
    ])
    L += ["Every one of the seven readiness states is listed above, so the rows sum to the "
          f"backlog total ({p['total_items']}).", ""]
    L += ["## The single next action", ""]
    nxt = p["next_authorized"]
    L += table(["Source", "Next authorized capability", "Awaiting authorization"],
               [[f"`{SRC['state']}` §05", nxt["unit"] or "—",
                 "yes" if nxt["awaiting_authorization"] else "no"]])
    L += [f"> {nxt['statement']}", ""]
    L += ["## Wave sequence", ""]
    L += table(["Wave", "Objective", "Items", "Effort (points)"],
               [[w["id"], w["objective"], p["wave_totals"][w["id"]]["items"],
                 p["wave_totals"][w["id"]]["effort_points"]] for w in p["waves"]])
    L += ["## Backlog composition by class", ""]
    L += table(["Class", "Meaning", "Items"], [
        ["HYG", "repository fixed point / hygiene (MCP-003 MEP-07, MEP-08)",
         p["class_totals"].get("HYG", 0)],
        ["SPINE", "EC-3 band realization spine + lane go-live",
         p["class_totals"].get("SPINE", 0)],
        ["REPORT", "outstanding registered report obligation", p["class_totals"].get("REPORT", 0)],
        ["AEOS", "declared execution-spine gaps G-01..G-12", p["class_totals"].get("AEOS", 0)],
        ["WP", "UCDA registered implementation work packages", p["class_totals"].get("WP", 0)],
        ["CONCEPT", "concepts dispositioned SPECIFIED or DEFERRED",
         p["class_totals"].get("CONCEPT", 0)],
        ["EVID", "IMPLEMENTED concepts missing code evidence or certification",
         p["class_totals"].get("EVID", 0)],
        ["KNOW", "UAKOS-CLOSURE-008 items homed into active waves",
         p["class_totals"].get("KNOW", 0)],
        ["RAT", "out-of-corpus ratification acts", p["class_totals"].get("RAT", 0)],
    ])
    L += ["## How KNOW readiness, authorization and effort are derived (disclosure)", ""]
    know = [i for i in items if i["item_class"] == "KNOW"]
    know_hi = [i for i in know if i["priority"] in ("P0", "P1")]
    know_ready = [i for i in know if i["readiness"] == READY]
    know_blocked = [i for i in know if i["readiness"] == BLOCKED]
    know_pts = sum(i["effort_points"] for i in know)
    L += table(["Attribute", "Derivation", "Consequence"], [
        ["readiness", "READY iff the evidence priority is P0/P1, then closed over the dependency "
                      "graph",
         f"{len(know_hi)} of {len(know)} KNOW items are so assigned; {len(know_blocked)} are then "
         f"BLOCKED behind a non-executable prerequisite, leaving {len(know_ready)} READY"],
        ["authorization_required", "true iff the evidence priority is NOT P0/P1",
         f"{len(know) - len(know_hi)} KNOW items are authorization-gated"],
        ["complexity / effort",
         "M (3 points) iff the evidence priority is P0/P1, else S (1 point)",
         f"{know_pts} of {p['total_effort_points']} points "
         f"({pct(know_pts, p['total_effort_points'])} of total effort)"],
    ])
    L += [
        "This is a DERIVATION, not an estimate. The priority label comes from the "
        "UAKOS-CLOSURE-008 "
        "evidence row, not from a repository authorization act and not from any sizing exercise: "
        "the repository carries no estimate for these items, so none is asserted. The consequence "
        "is stated plainly so the figures are never read as assessed effort or as an authorization "
        "decision — the split of otherwise-identical KNOW work into READY and authorization-gated "
        "is the evidence's own priority ordering carried forward, and only the destination owner "
        "can turn it into a commitment.",
        "",
    ]
    L += ["## Register vs HEAD evidence (recorded, not reconciled)", ""]
    L += table(["Band / unit", "MEP", "Evidence probe", "Present", "Meaning"],
               [[b["band"], b["mep"], f"`{b['probe']}`", "yes" if b["present"] else "**no**",
                 b["means"]] for b in p["band_evidence"]])
    L += [
        "The repository's own intelligence artifact still declares the frontier as "
        f"`{p['declared_frontier']['single_active_frontier']}` with "
        f"`{p['declared_frontier']['next_executable_capability']}` next, while MCP-002 §05 and "
        "HEAD file evidence place the frontier at the Band-13 freeze. This roadmap follows "
        "MCP-002 §05 plus HEAD evidence (the state of record and the measurement), and records "
        "the divergence here rather than editing either source — correcting them is their "
        "owners' act, not this engine's.",
        "",
        "## Excluded from the active backlog (declared)",
        "",
    ]
    pool = p["registered_future_pool"]
    L += table(["Pool", "Items", "Why excluded"],
               [["Registered FUTURE knowledge entries (UAKOS-CLOSURE-008 Wave F)",
                 pool["wave_F_items"], pool["note"]]])
    path = HERE / "01-MASTER-EXECUTION-ROADMAP.md"
    write(path, L)
    written.append(path.name)

    # ---------------------------------------------------------------- 02 backlog
    L = header(p, "02", "Implementation Backlog",
               "Every remaining implementation item with id, location, owner, dependency chain, "
               "priority, effort, and implementation / validation / certification status.")
    L += [f"Backlog items: **{p['total_items']}** · effort **{p['total_effort_points']}** points. "
          "The complete machine-readable backlog is `roadmap.json` (`items`).", ""]
    for wid, objective, _desc in WAVES:
        rows = wave_items(wid)
        if not rows:
            continue
        L += [f"## {wid} — {objective} ({len(rows)} items)", ""]
        big = len(rows) > 120
        shown = rows[:120] if big else rows
        L += table(["ID", "Item", "Location", "Owner", "Deps", "Pri", "Effort",
                    "Impl", "Val", "Cert", "Readiness"],
                   [[i["id"], clip(i["title"], 90), f"`{i['location']}`", clip(i["owner"], 60),
                     ", ".join(i["depends_on"]) or "—", i["priority"], i["effort_points"],
                     i["implementation_status"], i["validation_status"],
                     i["certification_status"], i["readiness"]] for i in shown])
        if big:
            L += [f"_{len(rows) - 120} further {wid} items are carried in `roadmap.json`; they "
                  "are homogeneous in owner, gate and rollback with the rows above._", ""]
    path = HERE / "02-IMPLEMENTATION-BACKLOG.md"
    write(path, L)
    written.append(path.name)

    # ---------------------------------------------------------------- 03 dependency graph
    L = header(p, "03", "Dependency Graph",
               "The complete execution dependency graph: prerequisites, successors, topological "
               "levels and independent workstreams.")
    L += table(["Property", "Value"], [
        ["Nodes", p["total_items"]],
        ["Edges", g["edge_count"]],
        ["Acyclic", "yes" if g["acyclic"] else "**no**"],
        ["Topological levels", len(g["levels"])],
        ["Independent workstreams", len(g["workstreams"])],
    ])
    L += ["## Layered architecture declared by the repository (bottom-up)", ""]
    L += table(["#", "Layer"], [[n, layer] for n, layer
                                in enumerate(p["layered_architecture"], 1)])
    L += ["## Prerequisites and successors (items with edges)", ""]
    rows = []
    for i in items:
        succ = g["successors"].get(i["id"], [])
        if not i["depends_on"] and not succ:
            continue
        rows.append([i["id"], clip(i["title"], 70), ", ".join(i["depends_on"]) or "—",
                     ", ".join(succ[:6]) + ("…" if len(succ) > 6 else "") or "—",
                     g["level_of"][i["id"]]])
    L += table(["ID", "Item", "Prerequisites", "Successors", "Level"], rows[:200])
    if len(rows) > 200:
        L += [f"_{len(rows) - 200} further edge-bearing items in `roadmap.json` "
              "(`graph.successors`)._", ""]
    L += ["## Roots (no prerequisite — startable the moment their wave opens)", ""]
    roots = [i for i in items if not i["depends_on"]]
    free = [i for i in roots if not i["authorization_required"]]
    free_by_wave = Counter(i["wave"] for i in free)
    free_by_class = Counter(i["item_class"] for i in free)
    L += [f"Root items: **{len(roots)}**. Of those, **{len(free)}** carry no prerequisite AND no "
          "authorization condition — measured, not assumed:", ""]
    L += table(["Wave", "Items", "Classes"],
               [[w, free_by_wave[w],
                 ", ".join(f"{c}×{sum(1 for i in free if i['wave'] == w and i['item_class'] == c)}"
                           for c in sorted({i["item_class"] for i in free if i["wave"] == w}))]
                for w in WAVE_IDS if free_by_wave[w]])
    L += [f"By class: {', '.join(f'{c} {n}' for c, n in sorted(free_by_class.items()))}. "
          "The two W0 roots are the only ones that are additionally unconditioned by wave "
          "sequencing; the rest are unauthorized-startable but sit in later waves, and their "
          f"readiness state (see register 01) is the binding statement — {len(free)} roots are "
          "authorization-free but not all of them are READY.", ""]
    path = HERE / "03-DEPENDENCY-GRAPH.md"
    write(path, L)
    written.append(path.name)

    # ---------------------------------------------------------------- 04 waves
    L = header(p, "04", "Implementation Waves",
               "Deterministic partition of all remaining work. No wave depends on a later wave "
               "(gated).")
    for wid, objective, desc in WAVES:
        rows = wave_items(wid)
        tot = p["wave_totals"][wid]
        L += [f"## {wid} — {objective}", ""]
        deps_waves = sorted({by_id[d]["wave"] for i in rows for d in i["depends_on"]
                             if d in by_id} - {wid})
        classes = sorted({i["item_class"] for i in rows})
        scope = sorted({i["location"].split("/")[0] for i in rows})[:8]
        L += table(["Field", "Value"], [
            ["Wave ID", wid],
            ["Objective", desc],
            ["Items", tot["items"]],
            ["Effort", f"{tot['effort_points']} points"],
            ["Repository scope", ", ".join(f"`{s}`" for s in scope) or "—"],
            ["Item classes", ", ".join(classes) or "—"],
            ["Input artifacts", ", ".join(f"`{SRC[k]}`" for k in
                                          ("mep", "state", "ucda", "aeos", "closure",
                                           "assimilation"))],
            ["Output artifacts", "code + tests + evidence + completion report under the item's "
                                 "location, plus the owner's certification record"],
            ["Depends on waves", ", ".join(deps_waves) or "none"],
            ["Validation gates", "`./verify.sh` (5 stages) + the item's class gate (register 07)"],
            ["Certification gates", "CEP-004 validation → CEP-005 certification (register 08)"],
            ["Definition of Done", "every item in the wave reports its success criteria met, "
                                   "`./verify.sh` exits 0, the class gate exits 0, and the "
                                   "regenerated registers show the item's status advanced"],
        ])
        if rows:
            top = sorted(rows, key=lambda i: (i["priority"], -i["effort_points"], i["id"]))[:12]
            L += table(["ID", "Item", "Pri", "Effort", "Readiness"],
                       [[i["id"], clip(i["title"], 80), i["priority"], i["effort_points"],
                         i["readiness"]] for i in top])
    path = HERE / "04-IMPLEMENTATION-WAVES.md"
    write(path, L)
    written.append(path.name)

    # ---------------------------------------------------------------- 05 critical path
    L = header(p, "05", "Critical Path",
               "The effort-weighted longest dependency chain: the sequence that sets the floor "
               "on total execution.")
    L += [f"In-repository critical path: **{g['critical_path_length']} items**, "
          f"**{g['critical_path_points']} points**. This is the engineering floor: the longest "
          "chain an autonomous agent can actually walk inside this repository. The out-of-corpus "
          f"ratification chain ({len(g['external_chain'])} items · {g['external_chain_points']} "
          "points) is longer in effort but is not executable here; it is reported separately "
          "below so the engineering floor is not confused with an external dependency.", ""]
    L += table(["#", "ID", "Item", "Wave", "Effort", "Readiness", "Validation command"],
               [[n, iid, clip(by_id[iid]["title"], 70), by_id[iid]["wave"],
                 by_id[iid]["effort_points"], by_id[iid]["readiness"],
                 f"`{by_id[iid]['validation_command']}`"]
                for n, iid in enumerate(g["critical_path"], 1)])
    L += ["## Out-of-corpus ratification chain (not executable in this repository)", ""]
    L += table(["#", "ID", "Item", "Wave", "Effort", "Readiness"],
               [[n, iid, clip(by_id[iid]["title"], 70), by_id[iid]["wave"],
                 by_id[iid]["effort_points"], by_id[iid]["readiness"]]
                for n, iid in enumerate(g["external_chain"], 1)])
    L += ["## Declared critical path (repository intelligence, for comparison)", ""]
    L += table(["#", "Declared step"],
               [[n, s] for n, s in enumerate(p["declared_frontier"]["critical_path"] or [], 1)])
    L += ["The declared path is the EC-3 band sequence; HEAD evidence shows Bands 10-12 "
          "complete and Band 13 certified through U11, so the remaining portion of that "
          "declared path is the Band-13 freeze plus lane go-live — which is what the computed "
          "path above starts with.", ""]
    path = HERE / "05-CRITICAL-PATH.md"
    write(path, L)
    written.append(path.name)

    # ---------------------------------------------------------------- 06 parallel groups
    L = header(p, "06", "Parallel Execution Groups",
               "Topological levels (safe concurrency) and independent workstreams (safe "
               "assignment to separate executors).")
    L += [f"Items in a level with siblings (parallelizable): **{p['parallelizable_count']}** · "
          f"independent workstreams: **{p['workstream_count']}**.", ""]
    L += ["## Levels — every item in a level may execute concurrently", ""]
    L += table(["Level", "Items", "Count", "Waves"],
               [[lvl, ", ".join(ids[:14]) + ("…" if len(ids) > 14 else ""), len(ids),
                 ", ".join(sorted({by_id[i]["wave"] for i in ids}))]
                for lvl, ids in g["levels"].items()])
    L += ["## Independent workstreams — no edge crosses between them", ""]
    rows = []
    for n, comp in enumerate(g["workstreams"], 1):
        classes = sorted({by_id[i]["item_class"] for i in comp})
        rows.append([n, len(comp), ", ".join(classes),
                     ", ".join(sorted({by_id[i]["wave"] for i in comp})),
                     sum(by_id[i]["effort_points"] for i in comp)])
    L += table(["#", "Items", "Classes", "Waves", "Effort"], rows[:60])
    if len(rows) > 60:
        L += [f"_{len(rows) - 60} further single-item workstreams in `roadmap.json` "
              "(`graph.workstreams`)._", ""]
    path = HERE / "06-PARALLEL-EXECUTION-GROUPS.md"
    write(path, L)
    written.append(path.name)

    # ---------------------------------------------------------------- 07 validation gates
    L = header(p, "07", "Validation Gates",
               "The executable validation obligation per item class. Every command is a real "
               "repository entry point.")
    L += table(["Class", "Validation command", "Applies to"],
               [[cls, f"`{pol['validation']}`", p["class_totals"].get(cls, 0)]
                for cls, pol in sorted(CLASS_POLICY.items())])
    L += ["## Repository-wide gates (must pass after every item)", ""]
    L += table(["Gate", "Command", "What it proves"], [
        ["Canonical verification", "`./verify.sh`",
         "ruff lint+format, pytest with --cov-fail-under=90, coverage report, "
         "governance enforce --pre, registry validate"],
        ["Registration drift", "`bash 00-BOOK/tools/register.sh --guard`",
         "artifact registration is committed and the generated registers carry no drift"],
        ["Aggregate constitutional gate", "`make uccep-gate`",
         "every located gate in the repository is green (fail-closed, boot tier)"],
        ["Decision evidence gate", "`make ucda-gate`",
         "every ratified decision carries exactly one disposition with resolvable evidence"],
        ["Meta-constitutional gate", "`make cmg-gate`",
         "meta-constitutional invariants hold; VAC-01 vacancy is reported"],
        ["Concept closure gate", "`make closure-gate` · `make closure-phase2-gate`",
         "no concept is unhomed, duplicated or orphaned"],
        ["Knowledge assimilation gate", "`make assimilate-gate`",
         "every verified knowledge object still holds exactly one terminal state"],
        ["Integration blueprint gate", "`make rib-gate`",
         "the repository integration blueprint's twelve quality gates hold"],
    ])
    L += ["## Program gates executed by this engine", ""]
    L += table(["Gate", "Blocking", "Count", "Result", "Detail"],
               [[x["gate"], "yes" if x["blocking"] else "no", x["count"], x["result"],
                 clip("; ".join(str(d) for d in x["detail"]), 160) or "—"] for x in p["gates"]])
    path = HERE / "07-VALIDATION-GATES.md"
    write(path, L)
    written.append(path.name)

    # ---------------------------------------------------------------- 08 certification gates
    L = header(p, "08", "Certification Gates",
               "The certification obligation per item class, and the ceiling that no engineering "
               "act can lift.")
    L += table(["Class", "Certification gate", "Items"],
               [[cls, pol["certification"], p["class_totals"].get(cls, 0)]
                for cls, pol in sorted(CLASS_POLICY.items())])
    L += ["## Certification ceiling", ""]
    L += table(["Constraint", "Source", "Effect"], [
        ["Certification is `CERTIFIED-PROVISIONAL`", f"`{SRC['state']}` §01 standing disclosure",
         "no engineering act can raise it; only CEP-006 ratification can"],
        ["Constitutional Tier T1 is VACANT (VAC-01)", "`00-CMG/CMG-REGISTRY.json`",
         "every certification below inherits PROVISIONAL status"],
        ["DR-RAT-11 requires an out-of-corpus act", f"`{SRC['ucda']}` WP-UCDA-001",
         "WAITING_FOR_RATIFICATION items cannot be executed inside this repository"],
    ])
    L += ["## Blockers of record", ""]
    L += table(["ID", "Blocker", "Scope", "Blocking?"],
               [[b["id"], b["blocker"], b["scope"], b["blocking"]] for b in p["blockers"]])
    path = HERE / "08-CERTIFICATION-GATES.md"
    write(path, L)
    written.append(path.name)

    # ---------------------------------------------------------------- 09 dashboard
    L = header(p, "09", "Implementation Dashboard",
               "One pane: what is done, what remains, what is ready, what is blocked.")
    cm = p["concept_model"]
    comp = p["completion"]
    L += ["## Repository implementation completion (measured over the concept model)", ""]
    L += table(["Metric", "Value", "Basis"], [
        ["Concepts", cm["total"], f"`{SRC['closure']}` concept_total"],
        ["IMPLEMENTED by disposition", f"{cm['implemented']} "
                                       f"({comp['disposition_implemented_pct']}%)", "closure.json"],
        ["Carried by code (`in_code`)", f"{cm['in_code']} ({comp['in_code_pct']}%)",
         "closure.json"],
        ["Certified", f"{cm['certified']} ({comp['certified_pct']}%)", "closure.json"],
        ["SPECIFIED (unrealized)", cm["specified"], "closure.json"],
        ["DEFERRED", cm["deferred"], "closure.json"],
        ["REJECTED", cm["rejected"], "closure.json"],
        ["EC-3 band evidence probes present",
         f"{comp['ec3_bands_complete']}/{comp['ec3_band_probes']}", "HEAD file evidence"],
    ])
    L += ["## Backlog dashboard", ""]
    L += table(["Readiness", "Items"], [[s, p["readiness_totals"][s]] for s in STATES])
    L += table(["Priority", "Items"],
               [[k, v] for k, v in sorted(p["priority_totals"].items())])
    L += table(["Risk", "Items"], [[k, v] for k, v in sorted(p["risk_totals"].items())])
    L += ["## Effort distribution", ""]
    total_pts = max(1, p["total_effort_points"])
    L += table(["Wave", "Items", "Effort (points)", "Share of effort"],
               [[w["id"], p["wave_totals"][w["id"]]["items"],
                 p["wave_totals"][w["id"]]["effort_points"],
                 f"{100.0 * p['wave_totals'][w['id']]['effort_points'] / total_pts:.1f}%"]
                for w in p["waves"]])
    L += [
        "Effort is in points on a fixed scale (S=1 · M=3 · L=8 · XL=20). The repository carries "
        "no velocity evidence, so no calendar estimate is derivable and none is given.",
        "",
        f"**Derivation disclosure.** The W7 share above is not an assessed size. All "
        f"{p['class_totals'].get('KNOW', 0)} KNOW items take complexity M (3 points) when their "
        "UAKOS-CLOSURE-008 evidence priority is P0/P1 and S (1 point) otherwise, so W7's share of "
        "total effort is a restatement of that priority split, not an estimate — see register 01 "
        "§'How KNOW readiness, authorization and effort are derived'. The EVID class is likewise "
        "uniformly S: a missing certification record is not sized by this engine. Only the SPINE, "
        "AEOS, WP and CONCEPT classes carry a complexity taken from their own register's "
        "declared severity or scope.",
        "",
    ]
    path = HERE / "09-IMPLEMENTATION-DASHBOARD.md"
    write(path, L)
    written.append(path.name)

    # ---------------------------------------------------------------- 10 readiness determination
    L = header(p, "10", "Execution Readiness Determination",
               "The autonomous execution plan and the final GO / CONDITIONAL GO / NO-GO "
               "determination.")
    L += table(["Field", "Value"], [
        ["Total remaining backlog items", p["total_items"]],
        ["— of which implementation work", p["implementation_items"]],
        ["— of which certification / validation / hygiene / report / ratification obligations",
         p["total_items"] - p["implementation_items"]],
        ["Ready to implement", p["ready_count"]],
        ["Blocked (prerequisite not startable)", p["blocked_count"]],
        ["Deferred (authorization-gated)", p["deferred_count"]],
        ["Waiting for ratification", p["waiting_for_ratification_count"]],
        ["Waiting for implementation", p["readiness_totals"][W_IMP]],
        ["Waiting for validation", p["readiness_totals"][W_VAL]],
        ["Waiting for certification", p["readiness_totals"][W_CERT]],
        ["Parallelizable items (share a level with a sibling)", p["parallelizable_count"]],
        ["Critical path", f"{g['critical_path_length']} items · "
                          f"{g['critical_path_points']} points"],
        ["Estimated implementation waves",
         len([w for w in p["waves"] if p["wave_totals"][w["id"]]["items"] > 0])],
        ["Repository implementation completion",
         f"{comp['disposition_implemented_pct']}% by disposition · {comp['in_code_pct']}% "
         f"carried by code · {comp['certified_pct']}% certified"],
        ["**Determination**", f"**{p['verdict']}**"],
    ])
    L += ["## Conditions attached to the determination", ""]
    L += table(["#", "Condition"], [[n, c] for n, c in enumerate(p["conditions"], 1)])
    L += ["## Autonomous execution plan — the first executable steps in order", ""]
    plan = [iid for iid in g["topological_order"]
            if by_id[iid]["readiness"] in (READY, W_VAL, W_CERT)][:30]
    for n, iid in enumerate(plan, 1):
        i = by_id[iid]
        L += [f"### Step {n} — `{i['id']}` · {clip(i['title'], 110)}", ""]
        L += table(["Field", "Value"], [
            ["Task ID", i["id"]],
            ["Wave", i["wave"]],
            ["Repository path", f"`{i['location']}`"],
            ["Owner", i["owner"]],
            ["Inputs", f"`{i['source']}`" + (f" · prerequisites: {', '.join(i['depends_on'])}"
                                             if i["depends_on"] else "")],
            ["Outputs", "the artifact or code the item's success criteria name, plus its "
                        "evidence and (where the class requires it) a completion report"],
            ["Validation command", f"`{i['validation_command']}`"],
            ["Success criteria", i["success_criteria"]],
            ["Rollback strategy", i["rollback"]],
            ["Authorization required", "yes" if i["authorization_required"] else "no"],
        ])
    L += [
        "Steps beyond the thirtieth continue in `roadmap.json` order "
        "(`graph.topological_order`, filtered to executable readiness states). The order is "
        "total and dependency-safe: an agent may execute it top to bottom, or execute any one "
        "topological level concurrently (register 06).",
        "",
        "## What this determination does NOT authorize",
        "",
        "- It authorizes nothing. Every DEFERRED item carries the repository's standing STOP "
        "rule: a capability begins only on explicit authorization.",
        "- It lifts no certification ceiling: `CERTIFIED-PROVISIONAL` holds while Tier T1 is "
        "vacant, and no item in this roadmap can change that.",
        "- It resolves no register staleness. Where a register and HEAD evidence disagree "
        "(register 01), the divergence is recorded for its owner, not corrected here.",
        "",
        f"**Determination: {p['verdict']}** · seal `{p['seal_sha256'][:32]}…`",
        "",
    ]
    path = HERE / "10-EXECUTION-READINESS-DETERMINATION.md"
    write(path, L)
    written.append(path.name)
    return written


def serialize(p: dict) -> str:
    head = {k: v for k, v in p.items() if k != "items"}
    body = json.dumps(head, indent=2, sort_keys=True)
    lines = [json.dumps(i, sort_keys=True, separators=(",", ":")) for i in p["items"]]
    return (body[:-2].rstrip() + ",\n  \"items\": [\n"
            + ",\n".join("    " + ln for ln in lines) + "\n  ]\n}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=f"{PROGRAM} master execution roadmap engine")
    ap.add_argument("--gate", action="store_true",
                    help="exit 1 unless the roadmap is executable (all blocking gates pass)")
    ap.add_argument("--render", action="store_true",
                    help="re-render 01..10 from the committed roadmap.json (replay; the recorded "
                         "HEAD is preserved, so a drift gate can compare committed vs rendered)")
    args = ap.parse_args()

    if args.render:
        if not ROADMAP_JSON.exists():
            print(f"{PROGRAM}: FAIL-CLOSED — {ROADMAP_JSON.name} absent; cannot render.",
                  file=sys.stderr)
            return 1
        payload = json.loads(ROADMAP_JSON.read_text(encoding="utf-8"))
    else:
        payload = build()
        ROADMAP_JSON.write_text(serialize(payload), encoding="utf-8")
    written = render(payload)
    print(f"{PROGRAM}: {payload['verdict']} | items={payload['total_items']} "
          f"(implementation={payload['implementation_items']}) "
          f"| ready={payload['ready_count']} blocked={payload['blocked_count']} "
          f"deferred={payload['deferred_count']} "
          f"awaiting_ratification={payload['waiting_for_ratification_count']} "
          f"| critical_path={payload['graph']['critical_path_length']} items/"
          f"{payload['graph']['critical_path_points']}pts "
          f"| effort={payload['total_effort_points']}pts"
          f"{' | RENDER (replay)' if args.render else ''}")
    print(f"wrote {len(written)} artifacts to 00-MASTER/{PROGRAM}")
    failed = [x for x in payload["gates"] if x["blocking"] and x["result"] == "FAIL"]
    if args.gate and failed:
        for x in failed:
            print(f"  BLOCKING FAIL: {x['gate']} = {x['count']} {x['detail']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
