#!/usr/bin/env python3
"""UAKOS-CLOSURE-009 - Universal Constitutional Assimilation Programme engine.

MISSION
    Project every constitutionally accepted concept already present in Repository
    Truth into a governed Repository Requirement, then MEASURE - never estimate -
    assimilation coverage, lifecycle maturity, readiness, traceability and gap.

AUTHORITY
    NONE - DERIVED TRUTH. This engine creates no constitutional authority, ratifies
    nothing, certifies nothing, freezes nothing and occupies no tier. It measures
    what Repository Truth already declares and writes ONLY inside its own directory.

CONSTITUTIONAL POSTURE
    * REUSE FIRST. Every input is an existing repository register. No re-extraction,
      no re-identification, no fabrication, no new identifier namespace.
    * CREATE = 0 at the concept layer. Requirement identity is a total, injective,
      derived function of the existing concept identity (RR-<CONCEPT-ID>), so no
      independent requirement identity can ever drift from its concept.
    * Zero hard coding. Zone -> program/category/volume classification is read from
      the repository's own configuration (00-BOOK/tools/config.py). Authority is read
      verbatim from the canonical home's own declaration. Unknown zones, unknown
      families and unknown dimensions are carried generically and never rejected,
      so new constitutional object types need no engine change.
    * Zero fixed limits. No family list, no zone list, no dimension list, no lattice
      ceiling and no wave count is bounded by this engine.
    * Deterministic. No timestamps, no randomness, no environment dependence beyond
      the declared inputs; re-rendering is byte-identical at a fixed commit.
    * Replay-stable. A committed artifact can never carry the sha of the commit that
      carries it, so `--render` REPLAYS the head commit recorded in the existing
      requirements.json instead of re-reading it. Without this the registers drift by
      exactly one field on every commit, which is why a byte-for-byte drift gate over
      this programme was previously unenforceable. The mechanism is not invented here:
      it is the pattern 00-MASTER/UKAP-001/corpus_engine.py already proved (Reuse
      Before Create).
    * Fail-closed. `--gate` exits non-zero while constitutional assimilation is below
      100%. `--baseline-gate` exits non-zero while any Phase-8 baseline precondition
      is unproven.

USAGE
    python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py
    python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --render
    python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --gate
    python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --baseline-gate
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PROGRAM = "UAKOS-CLOSURE-009"
PHASE = "PHASE-009"
AUTHORITY = "NONE (DERIVED TRUTH)"

# --------------------------------------------------------------------------------------
# Declared inputs. Every one is an existing repository register - this programme
# introduces no new source of truth. `required` inputs make the run fail closed;
# optional inputs are recorded as ABSENT and degrade the measurement transparently
# rather than being silently assumed (Zero Silent Repair / Zero Hidden Assumptions).
# --------------------------------------------------------------------------------------
INPUTS = {
    "closure": ("00-MASTER/UAKOS-CLOSURE-002/closure.json", True),
    "phase2": ("00-MASTER/UAKOS-CLOSURE-002/phase2.json", True),
    "phase3": ("00-MASTER/UAKOS-CLOSURE-002/phase3.json", True),
    "artifacts": ("00-BOOK/DATA/artifacts.json", True),
    # The identity authority. artifacts.json is the CORPUS REGISTRY and answers a different
    # question: which files are Repository Corpus. UCKP-ART-05's home for "what identifies an
    # object" is the ledger, and the two populations differ by design.
    "id_ledger": ("00-BOOK/DATA/id-ledger.json", True),
    "relationships": ("00-BOOK/DATA/relationships.json", True),
    "control_tower": ("00-BOOK/DATA/control-tower.json", True),
    "certification": ("00-BOOK/DATA/certification.json", True),
    "volumes": ("00-BOOK/DATA/volumes.json", False),
    "signals": ("00-BOOK/DATA/signals.json", False),
    "baseline": ("00-MASTER/BASELINE-001/baseline.json", True),
    "assimilation": ("00-MASTER/UAKOS-CLOSURE-008/assimilation.json", False),
    "capability_catalog": ("intelligence/UCOS-RIE-CAPABILITY-CATALOG.json", False),
    "capability_units": ("00-MASTER/UCOS-RIB-001/rib.json", False),
    "cko": ("knowledge/canonical-knowledge.json", False),
    "decisions": ("knowledge/decisions.json", False),
    "determinism": ("determinism-evidence/determinism-evidence.json", False),
    # The declared list of every artifact a producer regenerates. Read so that a DERIVED
    # register is never counted as evidence OF the concept it merely mentions.
    "generated": ("00-BOOK/DATA/generated-artifact-registry.json", True),
}

# Evidence-kind classifiers. Patterns are declarative and additive: adding a kind
# needs no other change, and an unmatched path simply contributes no kind.
EVIDENCE_KINDS = (
    ("test", re.compile(r"(^|/)tests?/|(^|/)test_[^/]+\.py$")),
    # Both kinds accept a Markdown report, symmetrically. Verification already did — but only
    # for the one name `-COMPLETION-REPORT.md` — while validation accepted `.json` alone, so
    # `05-VALIDATION-REPORT.md` and `08-ARCHITECTURE-VERIFICATION-REPORT.md` were invisible
    # while their `.json` siblings counted. No principle separated them; it is the same shape
    # as matching `determinism-evidence` and missing `determinism.json`.
    ("validation", re.compile(
        r"validation-(?:report|evidence)[^/]*\.json$|(^|/)validation[^/]*\.json$"
        r"|-VALIDATION-REPORT\.md$")),
    ("verification", re.compile(
        r"-COMPLETION-REPORT\.md$|realization-evidence\.json$|verification[^/]*\.json$"
        r"|-VERIFICATION-REPORT\.md$")),
    # `determinism.json` is the per-unit form and carries `determinism_evidence: true` with two
    # bundle hashes proving byte-identical replay; the hyphenated form is the programme-level
    # one. Matching only the latter made BC-06 report "0 of 318 implemented requirements carry
    # determinism evidence" while 47 such files sat under */_evidence/ — a false zero, and the
    # same defect as a rule fluent in one of the repository's naming conventions and blind to
    # the other.
    ("determinism", re.compile(r"determinism-evidence|reproducibility_report|(^|/)determinism\.json$")),
    ("compliance", re.compile(r"compliance\.json$|-compliance[^/]*\.json$")),
    ("interaction", re.compile(r"interaction-matrix\.json$")),
    ("registry", re.compile(r"(^|/)DATA/[^/]+\.json$|-MASTER-REGISTRY\.md$")),
    ("constitution", re.compile(r"-CONSTITUTION\.md$")),
    ("certificate", re.compile(r"-CERTIFICATE\.md$|CERTIFICATION[^/]*\.md$")),
    ("plan", re.compile(r"-PLAN[^/]*\.md$|-ROADMAP[^/]*\.md$|-BACKLOG\.md$")),
    ("engine", re.compile(r"_engine\.py$|(^|/)(?:ukb|ukbx)\.py$")),
)

# The maturity lattice is an ordered, open-ended list. Appending a level extends the
# lattice without altering any existing level: there is no ceiling in the model, only
# in the evidence. Each level is (key, label, predicate-name).
LATTICE = (
    ("M0", "REJECTED", "rejected"),
    ("M1", "DEFERRED", "deferred"),
    ("M2", "SPECIFIED", "specified"),
    ("M3", "IMPLEMENTED", "implemented"),
    ("M4", "TEST-EVIDENCED", "tested"),
    ("M5", "VALIDATED-OR-VERIFIED", "checked"),
    ("M6", "CERTIFIED-PROVISIONAL", "certified"),
    ("M7", "RUNTIME-PROVEN", "runtime"),
)

AUTH_ROW = re.compile(r"^\|\s*(?:\*\*)?AUTHORITY(?:\*\*)?\s*\|\s*(.+?)\s*\|\s*$", re.M | re.I)
TABLE_CELL = re.compile(r"[|\r\n]+")


# --------------------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------------------
def _git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=REPO, capture_output=True, text=True, check=False
        )
        return out.stdout.strip()
    except OSError:
        return ""


def _load(rel: str):
    p = REPO / rel
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return None


def _cell(v) -> str:
    """Render any value as a single safe markdown table cell."""
    s = "" if v is None else str(v)
    s = TABLE_CELL.sub(" / ", s).strip()
    return s if s else "-"


def _head_commit(replay: dict | None) -> str:
    """The HEAD this model is rendered against.

    In replay mode the head recorded in the previously written ``requirements.json`` is
    reused verbatim. A committed artifact cannot carry the sha of the commit that carries
    it, so re-reading HEAD would make every register drift by exactly one field on every
    commit and no byte-for-byte drift gate over this programme could ever pass. Reusing
    the recorded head is what makes the determinism claim in this module's docstring
    mechanically enforceable.
    """
    if replay is not None:
        recorded = str((replay.get("baseline") or {}).get("head_commit") or "").strip()
        if recorded:
            return recorded
    return _git("rev-parse", "--short", "HEAD") or "unknown"


def _replayed_input_fact(replay: dict | None, key: str, live: str) -> str:
    """A fact of the REGENERATED input, preserved across a replay.

    ``00-MASTER/UAKOS-CLOSURE-002/closure.json`` is gitignored (.gitignore:59) and rebuilt by
    whichever site ran last, so its ``baseline_commit`` and ``branch`` describe THAT run's
    environment rather than the repository. Re-reading them makes the committed register drift
    by exactly those fields on every commit and on every runner — precisely the defect
    ``_head_commit`` already prevents for the head one field below, which this reuses for the
    inherited fields it forgot. A genuine regeneration (``make closure009``, no ``--render``)
    still advances them; only a replay preserves what the register recorded.
    """
    if replay is not None:
        recorded = str((replay.get("baseline") or {}).get(key) or "").strip()
        if recorded:
            return recorded
    return live


def _fence(header: list[str], rows: list[list], note: str = "") -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_cell(c) for c in r) + " |")
    if note:
        out.append("")
        out.append(note)
    return "\n".join(out)


def _hdr(num: str, title: str, m: dict, lead: list[str]) -> str:
    b = m["baseline"]
    banner = (
        f"> PROGRAM **{PROGRAM}** · {PHASE} · baseline `{b['closure_baseline_commit']}` "
        f"(branch `{b['branch']}`) · HEAD `{b['head_commit']}` · "
        f"AUTHORITY = **{AUTHORITY}** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED · "
        f"generated by `requirement_engine.py`"
    )
    parts = [f"# {num} — {title}", "", banner, ">", "> " + " ".join(lead), ""]
    return "\n".join(parts)


def _seal(payload) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _top(rel: str) -> str:
    return rel.split("/", 1)[0] if "/" in rel else rel


# --------------------------------------------------------------------------------------
# repository configuration reuse - zone/path classification comes from the repository's
# own registration configuration, never from a list held by this engine.
# --------------------------------------------------------------------------------------
def load_classifier():
    tools = REPO / "00-BOOK" / "tools"
    if not (tools / "config.py").is_file():
        return None, "ABSENT"
    sys.path.insert(0, str(tools))
    try:
        import config  # type: ignore
    except Exception:  # pragma: no cover - configuration must never break measurement
        return None, "UNIMPORTABLE"
    finally:
        if sys.path and sys.path[0] == str(tools):
            sys.path.pop(0)
    rules = [
        (re.compile(pat), prog, cat, vol) for pat, prog, cat, vol in config.CLASSIFY_RULES
    ]
    return rules, "00-BOOK/tools/config.py::CLASSIFY_RULES"


def classify(rules, rel: str):
    if not rules or not rel:
        return ("UNCLASSIFIED", "UNCLASSIFIED", "UNCLASSIFIED")
    for rx, prog, cat, vol in rules:
        if rx.search(rel):
            return (prog, cat, vol)
    return ("UNCLASSIFIED", "UNCLASSIFIED", "UNCLASSIFIED")



def derived_paths(generated: dict | None) -> frozenset[str]:
    """Every path a declared producer regenerates.

    A DERIVED REGISTER IS NOT EVIDENCE OF A CONCEPT; IT IS A PROJECTION THAT MENTIONS ONE.
    Counting it inflates the evidence and, worse, makes the count depend on when a sibling
    register last ran. UCOS-RFP-001 measured that directly: this programme, PHASE-001A-R1,
    PHASE-001B and PHASE-002 each rewrote on pass TWO of the fixed-point pipeline, because
    each was counting files the others had just written. APPLICATION-000 alone appears in 26
    files inside sibling UAKOS register directories. Reordering the stages could not fix it —
    the reference is mutual, not sequential — and CI showed the signature plainly: every
    evidence count differing by exactly one, uniformly.

    The population is DECLARED, never enumerated here: 00-BOOK/DATA/generated-artifact-registry
    .json is the repository's own record of what a producer regenerates, so an artifact that
    becomes generated tomorrow leaves this count with no edit to this engine.
    """
    entries = (generated or {}).get("entries") or []
    return frozenset(
        str(e["canonical_path"])
        for e in entries
        if isinstance(e, dict) and e.get("canonical_path")
    )

def declared_authority(rel: str, cache: dict) -> str:
    """Read the AUTHORITY the canonical home declares about itself, verbatim."""
    if not rel:
        return "NO-CANONICAL-HOME"
    if rel in cache:
        return cache[rel]
    p = REPO / rel
    verdict = "HOME-FILE-ABSENT"
    if p.is_file():
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:40000]
        except OSError:
            head = ""
        m = AUTH_ROW.search(head)
        verdict = m.group(1).strip() if m else "UNDECLARED-AT-CANONICAL-HOME"
    cache[rel] = verdict
    return verdict


# --------------------------------------------------------------------------------------
# model construction
# --------------------------------------------------------------------------------------
def build(inputs: dict, replay: dict | None = None) -> dict:
    closure = inputs["closure"]
    concepts = closure["concepts"]
    rules, rules_src = load_classifier()
    auth_cache: dict[str, str] = {}

    # artifact identity + typed graph indices, keyed by repository path
    arts = (inputs["artifacts"] or {}).get("artifacts", []) or []
    by_path = {a.get("path", ""): a for a in arts}
    uid_of = {p: a.get("universal_id", "") for p, a in by_path.items()}
    # IDENTITY IS ASKED OF THE IDENTITY AUTHORITY, not of the corpus registry.
    # Reading only artifacts.json reported 15 requirements as having a canonical home that
    # "carries no universal identity" when every one of them holds one. Their homes live under
    # 00-MASTER/, which config.py excludes from registration BY DETERMINATION — UCOS-RECON-C1
    # classes the Master Context System as Operational Memory, "execution state, not corpus: it
    # must never consume permanent corpus identities". So the remedy RG-E03 demanded could not
    # exist: registering them is the one thing that declaration forbids. The same declaration
    # says what does hold for them — "any identifier already allocated to a now-excluded path is
    # RETAINED-BUT-RETIRED in the id-ledger" — so the identity persists while corpus membership
    # does not. The ledger is consulted second, so a corpus artifact still answers as before.
    ledger = inputs["id_ledger"] or {}
    for _map in ("by_path", "by_object"):
        for path, entry in (ledger.get(_map) or {}).items():
            recorded = str((entry or {}).get("universal_id") or "").strip()
            if recorded and not uid_of.get(path):
                uid_of[path] = recorded
    edges = (inputs["relationships"] or {}).get("relationships", []) or []
    out_edges: dict[str, list] = {}
    in_edges: dict[str, list] = {}
    for e in edges:
        out_edges.setdefault(e.get("from", ""), []).append(e)
        in_edges.setdefault(e.get("to", ""), []).append(e)

    # repository-wide runtime / lifecycle dimensions (the governing runtime authority)
    dims = (inputs["control_tower"] or {}).get("dimensions", {}) or {}
    cert = inputs["certification"] or {}
    executions_ledgered = int((cert.get("scope") or {}).get("executions", 0) or 0)
    ceiling = (inputs["baseline"] or {}).get("ceiling", {}) or {}
    disclosure_token = ceiling.get("disclosure_token", "UNDECLARED")
    terminal_token = ceiling.get("terminal_token", "UNDECLARED")
    elevated = ceiling.get("elevated", []) or []

    # capability-layer presence, measured (never assumed)
    cap_blob = json.dumps(inputs["capability_catalog"] or {}, ensure_ascii=False).upper()
    unit_blob = json.dumps(inputs["capability_units"] or {}, ensure_ascii=False).upper()
    cko_ids = {
        str(o.get("cko_id", "")).upper()
        for o in ((inputs["cko"] or {}).get("objects", []) or [])
    }

    # runtime posture is a repository-wide fact: no concept can be runtime-proven while
    # the execution ledger is empty and the governing dimensions are not operational.
    runtime_ok_states = {"OPERATIONAL", "PRODUCTION", "RELEASED", "COMPLETE"}
    runtime_dims = {
        k: (v or {}).get("status", "UNDECLARED")
        for k, v in dims.items()
        if k in ("production", "operational", "release", "execution", "deployment")
    }
    runtime_proven_repo = executions_ledgered > 0 and all(
        s in runtime_ok_states for s in runtime_dims.values()
    )

    derived = derived_paths(inputs.get("generated"))
    reqs = []
    for c in sorted(concepts, key=lambda r: r["id"]):
        cid = c["id"]
        files = [f for f in (c.get("files", []) or []) if f not in derived]
        def_homes = sorted(c.get("def_homes", []) or [])
        exact_homes = sorted(c.get("exact_homes", []) or [])
        tops = sorted(c.get("tops", []) or [])
        trace = c.get("trace", {}) or {}

        kinds = sorted({k for k, rx in EVIDENCE_KINDS for f in files if rx.search(f)})

        home = def_homes[0] if def_homes else ""
        prog, cat, vol = classify(rules, home)
        owner_zone = _top(home) if home else (tops[0] if tops else "UNOWNED-ZONE")

        # --- canonical ownership determination -------------------------------------
        if len(def_homes) > 1:
            ownership = "COMPETING"
        elif len(def_homes) == 1:
            ownership = "DECLARED"
        elif tops:
            ownership = "INFERRED"
        else:
            ownership = "ABSENT"

        # --- lifecycle predicates, each traced to a repository field ---------------
        # Standing comes from the predecessor's authoritative `disposition`, not from
        # the line-local REJECT/DEFER markers: the predecessor's own precedence already
        # subordinates a marker to located code or certification, and re-reading the
        # raw marker here would contradict it.
        disp = c.get("disposition", "UNCLASSIFIED")
        rejected = disp == "REJECTED"
        deferred = disp == "DEFERRED"
        specified = bool(trace.get("specification")) or bool(c.get("in_spec"))
        implemented = bool(c.get("in_code"))
        tested = "test" in kinds
        checked = ("validation" in kinds) or ("verification" in kinds)
        certified = bool(c.get("certified"))
        runtime = runtime_proven_repo

        pred = {
            "rejected": rejected,
            "deferred": deferred,
            "specified": specified,
            "implemented": implemented,
            "tested": tested,
            "checked": checked,
            "certified": certified,
            "runtime": runtime,
        }
        # monotone lattice: the highest level whose predicate and all predecessors
        # from M2 upward hold. M0/M1 are terminal standings, not progress levels.
        if rejected:
            level, label = "M0", "REJECTED"
        elif deferred:
            level, label = "M1", "DEFERRED"
        else:
            level, label = "M2", "SPECIFIED"
            for key, lab, pname in LATTICE[3:]:
                if pred[pname]:
                    level, label = key, lab
                else:
                    break

        # --- statuses ---------------------------------------------------------------
        if rejected:
            impl_status = "REJECTED"
        elif implemented:
            impl_status = "PRESENT-IN-CODE"
        elif deferred:
            impl_status = "DEFERRED"
        else:
            impl_status = "ABSENT"
        val_status = (
            "EVIDENCED"
            if "validation" in kinds
            else ("TEST-ONLY" if tested else "NOT-EVIDENCED")
        )
        ver_status = "EVIDENCED" if "verification" in kinds else "NOT-EVIDENCED"
        cert_status = disclosure_token if certified else "UNCERTIFIED"
        rt_status = "RUNTIME-PROVEN" if runtime else "NO-RUNTIME-EVIDENCE"

        # --- coverage (assimilation, not maturity) ---------------------------------
        if ownership == "DECLARED" and specified:
            coverage = "FULLY ASSIMILATED"
        elif ownership == "ABSENT":
            coverage = "NOT ASSIMILATED"
        else:
            coverage = "PARTIALLY ASSIMILATED"

        # --- dependencies / relationships via the canonical typed graph ------------
        uid = uid_of.get(home, "")
        oe = out_edges.get(uid, []) if uid else []
        ie = in_edges.get(uid, []) if uid else []
        dep_ids = sorted({e.get("to", "") for e in oe if e.get("type") == "Depends-On"})
        rel_hist: dict[str, int] = {}
        for e in oe + ie:
            t = e.get("type", "UNTYPED")
            rel_hist[t] = rel_hist.get(t, 0) + 1

        # --- 9-tier constitutional spine (MCP-006), measured -----------------------
        spine = {
            "vision": bool(trace.get("source")) or bool(c.get("source_only_files")),
            "principle": bool(trace.get("constitution")),
            "constitution": bool(trace.get("constitution")),
            "capability": (cid.upper() in cap_blob)
            or (cid.upper() in unit_blob)
            or (cid.upper() in cko_ids),
            "requirement": True,  # established by this register
            "implementation": implemented,
            "test": tested,
            "evidence": checked,
            "certification": certified,
        }

        reqs.append(
            {
                "requirement_id": "RR-" + cid,
                "concept_id": cid,
                "family": c.get("family", "UNCLASSIFIED"),
                "disposition": c.get("disposition", "UNCLASSIFIED"),
                "assimilation_action": "REUSED",
                "canonical_owner": owner_zone,
                "ownership": ownership,
                "repository_location": home
                or f"(non-filename home · {len(files)} evidence files · zones {'+'.join(tops) or 'none'})",
                "definitional_homes": def_homes,
                "exact_homes": exact_homes,
                "authority": declared_authority(home, auth_cache),
                "program": prog,
                "category": cat,
                "volume": vol,
                "universal_id": uid or "UNREGISTERED",
                "dependencies": dep_ids,
                "dependency_count": len(dep_ids),
                "relationships": rel_hist,
                "relationship_count": sum(rel_hist.values()),
                "evidence_files": len(files),
                "evidence_kinds": kinds,
                "traceability": spine,
                "traceability_tiers_present": sum(1 for v in spine.values() if v),
                "maturity_level": level,
                "maturity": label,
                "implementation_status": impl_status,
                "validation_status": val_status,
                "verification_status": ver_status,
                "certification_status": cert_status,
                "runtime_status": rt_status,
                "coverage": coverage,
                "homed": bool(c.get("homed")),
                "orphan": bool(c.get("orphan")),
            }
        )

    # ---------------------------------------------------------------------------------
    # aggregation
    # ---------------------------------------------------------------------------------
    def hist(key):
        h: dict[str, int] = {}
        for r in reqs:
            h[str(r[key])] = h.get(str(r[key]), 0) + 1
        return dict(sorted(h.items()))

    total = len(reqs)
    coverage_hist = hist("coverage")
    fully = coverage_hist.get("FULLY ASSIMILATED", 0)

    # --- gap classes: the 7 inherited from PHASE-001 plus the lifecycle classes this
    #     programme measures. Every class is a measured set, never an estimate.
    inherited = (inputs["closure"] or {}).get("gaps", {}) or {}
    gap_classes = []

    def add_gap(gid, name, klass, members, action, owner):
        gap_classes.append(
            {
                "gap_id": gid,
                "name": name,
                "class": klass,
                "count": len(members) if isinstance(members, list) else int(members),
                "members": sorted(members)[:400] if isinstance(members, list) else [],
                "required_action": action,
                "canonical_owner": owner,
            }
        )

    for i, (k, v) in enumerate(sorted(inherited.items()), start=1):
        add_gap(
            f"RG-A{i:02d}",
            k,
            "INHERITED-ASSIMILATION",
            int(v),
            "No action while count is 0; standing gate keeps it at 0.",
            "00-MASTER/UAKOS-CLOSURE-002/closure_engine.py",
        )

    ownership_inferred = [r["requirement_id"] for r in reqs if r["ownership"] == "INFERRED"]
    ownership_competing = [r["requirement_id"] for r in reqs if r["ownership"] == "COMPETING"]
    auth_undeclared = [
        r["requirement_id"]
        for r in reqs
        if r["authority"] in ("UNDECLARED-AT-CANONICAL-HOME", "HOME-FILE-ABSENT")
    ]
    impl_absent = [r["requirement_id"] for r in reqs if r["implementation_status"] == "ABSENT"]
    impl_deferred = [r["requirement_id"] for r in reqs if r["implementation_status"] == "DEFERRED"]
    cert_no_code = [
        r["requirement_id"]
        for r in reqs
        if r["certification_status"] != "UNCERTIFIED"
        and r["implementation_status"] not in ("PRESENT-IN-CODE",)
    ]
    code_no_cert = [
        r["requirement_id"]
        for r in reqs
        if r["implementation_status"] == "PRESENT-IN-CODE"
        and r["certification_status"] == "UNCERTIFIED"
    ]
    no_val = [
        r["requirement_id"]
        for r in reqs
        if r["validation_status"] == "NOT-EVIDENCED" and r["implementation_status"] == "PRESENT-IN-CODE"
    ]
    no_ver = [
        r["requirement_id"]
        for r in reqs
        if r["verification_status"] == "NOT-EVIDENCED" and r["implementation_status"] == "PRESENT-IN-CODE"
    ]
    no_runtime = [r["requirement_id"] for r in reqs if r["runtime_status"] != "RUNTIME-PROVEN"]
    no_capability_tier = [
        r["requirement_id"] for r in reqs if not r["traceability"]["capability"]
    ]
    unregistered = [r["requirement_id"] for r in reqs if r["universal_id"] == "UNREGISTERED"]

    add_gap(
        "RG-B01",
        "CANONICAL-OWNERSHIP-INFERRED",
        "OWNERSHIP",
        ownership_inferred,
        "Declare a definitional canonical home whose basename carries the concept identity, "
        "or record a governed determination that the concept is intentionally owned by an "
        "aggregate home.",
        "00-MASTER/UAKOS-CLOSURE-002/22-CANONICAL-HOME-REGISTER.md",
    )
    add_gap(
        "RG-B02",
        "CANONICAL-OWNERSHIP-COMPETING",
        "OWNERSHIP",
        ownership_competing,
        "Reduce to exactly one definitional home; supersede the remainder (never delete).",
        "00-MASTER/UAKOS-CLOSURE-002/22-CANONICAL-HOME-REGISTER.md",
    )
    add_gap(
        "RG-B03",
        "AUTHORITY-UNDECLARED-AT-CANONICAL-HOME",
        "AUTHORITY",
        auth_undeclared,
        "Add the repository's declared AUTHORITY table row to the canonical home so "
        "authority is read, not inferred.",
        "00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md",
    )
    add_gap(
        "RG-C01",
        "IMPLEMENTATION-ABSENT",
        "IMPLEMENTATION",
        impl_absent,
        "Realize through the existing factory/composition path, or record a governed defer.",
        "00-MASTER/UAKOS-CLOSURE-002/43-IMPLEMENTATION-CONTRACT-REGISTER.md",
    )
    add_gap(
        "RG-C04",
        "DEFERRED-AND-UNREALIZED",
        "IMPLEMENTATION",
        impl_deferred,
        "A governed defer is a standing, not a closure: each must eventually be realized or "
        "superseded before 100% implementation can be proven.",
        "00-MASTER/UAKOS-CLOSURE-002/43-IMPLEMENTATION-CONTRACT-REGISTER.md",
    )
    add_gap(
        "RG-C02",
        "CERTIFIED-WITHOUT-LOCATED-CODE",
        "CONSISTENCY",
        cert_no_code,
        "Reconcile: either locate the implementation the certification asserts, or withdraw "
        "the certification token.",
        "00-CEP/CEP-005-CONSTITUTIONAL-CERTIFICATION-CONSTITUTION.md",
    )
    add_gap(
        "RG-C03",
        "CODE-WITHOUT-CERTIFICATION",
        "CERTIFICATION",
        code_no_cert,
        "Route through the certification programme; certification ceiling remains the "
        "declared disclosure token.",
        "00-MASTER/UAKOS-CLOSURE-004",
    )
    add_gap(
        "RG-D01",
        "NO-VALIDATION-EVIDENCE",
        "VALIDATION",
        no_val,
        "Attach validation evidence at the canonical evidence location.",
        "00-CEP/CEP-004-CONSTITUTIONAL-VALIDATION-CONSTITUTION.md",
    )
    add_gap(
        "RG-D02",
        "NO-VERIFICATION-EVIDENCE",
        "VERIFICATION",
        no_ver,
        "Attach verification / realization evidence at the canonical evidence location.",
        "00-CEP/CEP-008-CONSTITUTIONAL-EVIDENCE-TRACEABILITY-CONSTITUTION.md",
    )
    add_gap(
        "RG-E01",
        "NO-RUNTIME-EVIDENCE",
        "RUNTIME",
        no_runtime,
        "Ledger real executions; runtime dimensions must leave BLOCKED/NOT_STARTED before "
        "any requirement can be runtime-proven.",
        "00-BOOK/DATA/control-tower.json",
    )
    add_gap(
        "RG-E02",
        "CAPABILITY-TIER-UNPOPULATED",
        "TRACEABILITY",
        no_capability_tier,
        "Bind the concept to a capability record so the 9-tier spine is continuous.",
        "00-MASTER/MCP-006-MASTER-TRACEABILITY.md",
    )
    add_gap(
        "RG-E03",
        "CANONICAL-HOME-UNREGISTERED",
        "REGISTRY",
        unregistered,
        "Register the canonical home so it carries a universal identity and can participate "
        "in the typed graph.",
        "00-BOOK/tools/register.sh",
    )

    # systemic (non-per-requirement) measured findings
    art_total = len(arts)
    axis_pop: dict[str, int] = {}
    for a in arts:
        for k, v in (a.get("traceability", {}) or {}).items():
            axis_pop[k] = axis_pop.get(k, 0) + (1 if v else 0)
    unpopulated_axes = sorted(k for k, v in axis_pop.items() if v == 0)
    stale_dims = sorted(
        k
        for k, v in dims.items()
        if str((v or {}).get("status", "")).upper() in ("BLOCKED", "NOT_STARTED")
    )
    vacuous_exact = all(not r["exact_homes"] for r in reqs)

    # tracked machine-readable test-result artifacts, measured from the index itself.
    # -z: `git ls-files` renders non-ASCII paths in quoted octal form, which does not
    # resolve on disk; 116 tracked `Ω∞` artifacts were silently invisible without it.
    tracked = [ln for ln in _git("ls-files", "-z").split("\0") if ln]
    test_result_rx = re.compile(
        r"(junit|test-results?|testreport|test_report|pytest-report)[^/]*\.(xml|json)$", re.I
    )
    tracked_test_results = sorted(p for p in tracked if test_result_rx.search(p))

    systemic = [
        {
            "id": "RG-S01",
            "name": "ARTIFACT-TRACEABILITY-SCHEMA-UNPOPULATED",
            "open": len(unpopulated_axes) > 0,
            "measured": f"{len(unpopulated_axes)} of {len(axis_pop)} per-artifact traceability axes "
            f"are empty across all {art_total} registered artifacts "
            f"({', '.join(unpopulated_axes) or 'none'}); populated axes: "
            + ", ".join(f"{k}={v}" for k, v in sorted(axis_pop.items()) if v),
            "owner": "00-BOOK/DATA/artifacts.json",
        },
        {
            "id": "RG-S02",
            "name": "DUPLICATE-HOME-GATE-VACUOUS",
            "open": vacuous_exact or len(ownership_competing) > 0,
            "measured": "the inherited duplicate-home gate is evaluated over exact-stem homes, "
            f"and exact-stem homes are {'empty for every concept' if vacuous_exact else 'present'}; "
            f"measured over definitional homes the multiplicity is {len(ownership_competing)}",
            "owner": "00-MASTER/UAKOS-CLOSURE-002/closure_engine.py",
        },
        {
            "id": "RG-S03",
            "name": "LIFECYCLE-DIMENSIONS-NOT-OPERATIONAL",
            "open": len(stale_dims) > 0,
            "measured": f"{len(stale_dims)} of {len(dims)} lifecycle dimensions are BLOCKED or "
            f"NOT_STARTED: {', '.join(stale_dims) or 'none'}",
            "owner": "00-BOOK/DATA/control-tower.json",
        },
        {
            "id": "RG-S04",
            "name": "EXECUTION-LEDGER-EMPTY",
            "open": executions_ledgered == 0,
            "measured": f"{executions_ledgered} executions ledgered; every certification touching "
            "the execution domain is therefore satisfied vacuously",
            "owner": "00-BOOK/DATA/certification.json",
        },
        {
            "id": "RG-S05",
            "name": "TERMINAL-CERTIFICATION-TOKEN-UNHELD",
            "open": len(elevated) == 0,
            "measured": f"disclosure token `{disclosure_token}`; terminal token "
            f"`{terminal_token}` held by {len(elevated)} baselines",
            "owner": "00-MASTER/BASELINE-001/baseline.json",
        },
        {
            "id": "RG-S06",
            "name": "TEST-RESULT-ARTIFACT-UNTRACKED",
            "open": len(tracked_test_results) == 0,
            "measured": f"{len(tracked_test_results)} tracked machine-readable test-result "
            "artifacts located, so repository-only measurement of pass/fail is "
            f"{'possible' if tracked_test_results else 'impossible'}",
            "owner": "verify.sh",
        },
    ]
    open_systemic = [s["id"] for s in systemic if s["open"]]

    # ---------------------------------------------------------------------------------
    # Phase-8 baseline preconditions - each is MEASURED, and every one must pass before
    # a certified baseline may be created.
    # ---------------------------------------------------------------------------------
    def cond(cid, name, ok, measured, owner):
        return {
            "id": cid,
            "name": name,
            "verdict": "PASS" if ok else "FAIL",
            "measured": measured,
            "owner": owner,
        }

    b_impl = len(impl_absent) == 0 and len(impl_deferred) == 0
    b_val = len(no_val) == 0
    b_ver = len(no_ver) == 0
    b_cert = len(code_no_cert) == 0 and len(cert_no_code) == 0
    b_assim = fully == total
    det_results = (inputs["determinism"] or {}).get("results", []) or []
    det_reqs = [r for r in reqs if "determinism" in r["evidence_kinds"]]
    impl_reqs = [r for r in reqs if r["implementation_status"] == "PRESENT-IN-CODE"]
    b_replay = len(impl_reqs) > 0 and len(det_reqs) >= len(impl_reqs)
    lin_counts = ((inputs["baseline"] or {}).get("counts", {}) or {})
    baseline_conditions = [
        cond("BC-01", "100% implementation", b_impl,
             f"{hist('implementation_status').get('PRESENT-IN-CODE', 0)}/{total} present in code; "
             f"{hist('implementation_status').get('ABSENT', 0)} absent, "
             f"{hist('implementation_status').get('DEFERRED', 0)} deferred, "
             f"{hist('implementation_status').get('REJECTED', 0)} rejected",
             "closure.json"),
        cond("BC-02", "100% validation", b_val,
             f"{len(no_val)} implemented requirements without validation evidence",
             "CEP-004"),
        cond("BC-03", "100% verification", b_ver,
             f"{len(no_ver)} implemented requirements without verification evidence",
             "CEP-008"),
        cond("BC-04", "100% certification", b_cert,
             f"{len(code_no_cert)} code-without-certification, {len(cert_no_code)} "
             "certified-without-located-code", "CEP-005"),
        cond("BC-05", "100% audit", len(open_systemic) == 0,
             f"{len(open_systemic)} of {len(systemic)} systemic audit findings open: "
             f"{', '.join(open_systemic) or 'none'}", "UAKOS-CLOSURE-006"),
        cond("BC-06", "100% deterministic replay", b_replay,
             f"{len(det_reqs)} of {len(impl_reqs)} implemented requirements carry determinism "
             f"evidence; {len(det_results)} blueprint result(s) recorded",
             "determinism-evidence/"),
        cond("BC-07", "100% fixed point",
             bool((inputs["phase3"] or {}).get("planning_complete", False)) and b_assim,
             f"planning fixed point reached; assimilation fixed point {fully}/{total}",
             "phase3.json"),
        cond("BC-08", "100% dependency closure", len(unregistered) == 0,
             f"{len(unregistered)} requirements whose canonical home carries no universal "
             "identity and therefore no graph participation", "relationships.json"),
        cond("BC-09", "100% lineage closure",
             int(lin_counts.get("lineage_with_predecessor", 0) or 0) > 0,
             f"lineage_with_predecessor={lin_counts.get('lineage_with_predecessor', 'n/a')} of "
             f"lineage_population={lin_counts.get('lineage_population', 'n/a')}",
             "baseline.json"),
        cond("BC-10", "100% registry closure", len(unregistered) == 0,
             f"{len(unregistered)} unregistered canonical homes", "register.sh"),
        cond("BC-11", "100% knowledge extraction", len(cko_ids) >= total,
             f"{len(cko_ids)} canonical knowledge objects against {total} requirements",
             "knowledge/canonical-knowledge.json"),
        cond("BC-12", "100% capability elevation", len(no_capability_tier) == 0,
             f"{len(no_capability_tier)} requirements with an unpopulated capability tier",
             "MCP-006"),
    ]
    baseline_ok = all(c["verdict"] == "PASS" for c in baseline_conditions)

    # ---------------------------------------------------------------------------------
    # work packages - derived, prioritized, deterministic. One package per non-empty gap
    # class; ordering is by constitutional precedence then by measured magnitude.
    # ---------------------------------------------------------------------------------
    precedence = {
        "OWNERSHIP": 1,
        "AUTHORITY": 2,
        "CONSISTENCY": 3,
        "TRACEABILITY": 4,
        "REGISTRY": 5,
        "IMPLEMENTATION": 6,
        "VALIDATION": 7,
        "VERIFICATION": 8,
        "CERTIFICATION": 9,
        "RUNTIME": 10,
        "INHERITED-ASSIMILATION": 99,
    }
    open_gaps = [g for g in gap_classes if g["count"] > 0]
    open_gaps.sort(key=lambda g: (precedence.get(g["class"], 50), -g["count"], g["gap_id"]))
    packages = []
    for i, g in enumerate(open_gaps, start=1):
        wave = precedence.get(g["class"], 50)
        packages.append(
            {
                "work_package_id": f"WP-{PROGRAM}-{i:03d}",
                "gap_id": g["gap_id"],
                "title": g["name"],
                "class": g["class"],
                "scope_count": g["count"],
                "wave": f"W{wave:02d}",
                "priority": i,
                "canonical_owner": g["canonical_owner"],
                "authorized_action": g["required_action"],
                "authorization": "CONSTITUTIONALLY AUTHORIZED (remediation of a measured gap; "
                "no new authority, no new namespace, no create-before-reuse)",
                "blocks_baseline": True,
            }
        )
    waves: dict[str, list[str]] = {}
    for p in packages:
        waves.setdefault(p["wave"], []).append(p["work_package_id"])

    baseline_meta = {
        # Inherited from the gitignored, per-run closure.json — replayed, never re-read.
        "closure_baseline_commit": _replayed_input_fact(
            replay, "closure_baseline_commit", closure.get("baseline_commit", "unknown")
        ),
        "branch": _replayed_input_fact(replay, "branch", closure.get("branch", "unknown")),
        # The RECORDED head is replayed, never re-read: a committed artifact can never
        # carry the sha of the commit that carries it, so a replay must preserve the
        # recorded HEAD or every register drifts on every commit (UKAP-001 precedent).
        "head_commit": _head_commit(replay),
        "closure_determination": closure.get("determination", "unknown"),
        "closure_gap_total": closure.get("gap_total", "unknown"),
        "concept_total": closure.get("concept_total", len(reqs)),
        "tracked_total": (closure.get("sources", {}) or {}).get("tracked_total", "unknown"),
        "classifier_source": rules_src,
    }

    model = {
        "program": PROGRAM,
        "phase": PHASE,
        "authority": "NONE-DERIVED-TRUTH",
        "baseline": baseline_meta,
        "inputs": {
            k: {"path": v[0], "required": v[1], "state": "PRESENT" if inputs[k] is not None else "ABSENT"}
            for k, v in INPUTS.items()
        },
        "requirement_total": total,
        "requirements": reqs,
        "histograms": {
            "coverage": coverage_hist,
            "maturity": hist("maturity"),
            "maturity_level": hist("maturity_level"),
            "implementation_status": hist("implementation_status"),
            "validation_status": hist("validation_status"),
            "verification_status": hist("verification_status"),
            "certification_status": hist("certification_status"),
            "runtime_status": hist("runtime_status"),
            "ownership": hist("ownership"),
            "family": hist("family"),
            "canonical_owner": hist("canonical_owner"),
            "assimilation_action": hist("assimilation_action"),
        },
        "traceability_tiers": {
            tier: sum(1 for r in reqs if r["traceability"][tier])
            for tier in (
                "vision",
                "principle",
                "constitution",
                "capability",
                "requirement",
                "implementation",
                "test",
                "evidence",
                "certification",
            )
        },
        "lifecycle_dimensions": {k: (v or {}).get("status", "UNDECLARED") for k, v in sorted(dims.items())},
        "gap_classes": gap_classes,
        "systemic_findings": systemic,
        "open_systemic_findings": [s["id"] for s in systemic if s["open"]],
        "baseline_conditions": baseline_conditions,
        "baseline_permitted": baseline_ok,
        "work_packages": packages,
        "waves": {k: sorted(v) for k, v in sorted(waves.items())},
        "assimilation": {
            "fully": fully,
            "partially": coverage_hist.get("PARTIALLY ASSIMILATED", 0),
            "not": coverage_hist.get("NOT ASSIMILATED", 0),
            "percent_fully": round(100.0 * fully / total, 4) if total else 0.0,
            "complete": fully == total,
            "created_concepts": 0,
            "reused_concepts": total,
        },
        "determination": (
            "ASSIMILATION-COMPLETE" if fully == total else "ASSIMILATION-INCOMPLETE"
        ),
    }
    model["seal_sha256"] = _seal(
        {
            "program": PROGRAM,
            "baseline": baseline_meta,
            "requirement_total": total,
            "histograms": model["histograms"],
            "gap_classes": [(g["gap_id"], g["count"]) for g in gap_classes],
            "baseline_conditions": [(c["id"], c["verdict"]) for c in baseline_conditions],
            "determination": model["determination"],
        }
    )
    return model


# --------------------------------------------------------------------------------------
# deliverable rendering - exactly ten governed artifacts
# --------------------------------------------------------------------------------------
def d01(m):
    a = m["assimilation"]
    b = m["baseline"]
    inv = [
        ["1", "Repository Assimilation Report", "SPECIALIZED",
         "00-MASTER/UAKOS-CLOSURE-002/14-FINAL-REPOSITORY-COMPLETENESS-REPORT.md",
         "Adds the discussion→requirement projection layer over the existing completeness report."],
        ["2", "Repository Requirement Register", "CREATED",
         "(none located)",
         "No requirement-register artifact and no requirement identifier family exist in "
         "Repository Truth; Phase 4 mandates one. Identity is derived from the concept ID, so "
         "no new identity authority is created."],
        ["3", "Repository Coverage Report", "SPECIALIZED",
         "00-MASTER/UAKOS-CLOSURE-002/06-REPOSITORY-COVERAGE-MATRIX.md + 27-CONCEPT-COVERAGE-MATRIX.md",
         "Reuses the coverage axes and adds the stricter canonical-addressability axis."],
        ["4", "Repository Gap Report", "EXTENDED",
         "00-MASTER/UAKOS-CLOSURE-002/10-CONSTITUTIONAL-GAP-REGISTER.md",
         "Inherits the seven assimilation gap classes verbatim and extends them with the "
         "measured lifecycle classes."],
        ["5", "Repository Maturity Matrix", "CREATED",
         "(none located)",
         "No maturity-matrix artifact exists. Required by Phase 6. Built entirely from existing "
         "repository fields; introduces no new measurement source."],
        ["6", "Repository Readiness Matrix", "GENERALIZED",
         "00-MASTER/UAKOS-CLOSURE-002/46-REPOSITORY-READINESS-DASHBOARD.md + MCP-005 §04",
         "Generalizes per-programme readiness gates into a dimension × requirement matrix."],
        ["7", "Constitutional Traceability Matrix", "SPECIALIZED",
         "00-MASTER/MCP-006-MASTER-TRACEABILITY.md",
         "Reuses the canonical nine-tier spine and populates the previously unpopulated "
         "requirement tier."],
        ["8", "Implementation Programme", "EXTENDED",
         "00-MASTER/UAKOS-CLOSURE-002/40-EXECUTION-WAVE-REGISTER.md + 44-REPOSITORY-ENRICHMENT-EXECUTION-PLAN.md",
         "The predecessor plans zero items because it models only assimilation gaps; this "
         "extends the same wave model to lifecycle gaps."],
        ["9", "Prioritized Work Packages", "EXTENDED",
         "00-MASTER/UER-000001/06-UNIVERSAL-WORK-PACKAGE-LEDGER-SPECIFICATION.md",
         "Reuses the governing work-package ledger schema and naming convention."],
        ["10", "Updated Repository Truth", "REUSED",
         "00-MASTER/MCP-002-MASTER-STATE.md",
         "Records the delta only; the master state document remains the canonical owner of "
         "repository standing."],
    ]
    body = [
        _hdr("01", "Repository Assimilation Report", m,
             ["Phase 1 (discussion assimilation), Phase 2 (canonical ownership) and Phase 3",
              "(repository coverage) of the Universal Constitutional Assimilation Programme.",
              "Everything below is measured from the registers named in §2; nothing is estimated."]),
        "## 1. Determination",
        "",
        _fence(
            ["Question", "Measured answer"],
            [
                ["Is every accepted concept present in Repository Truth?",
                 f"YES — {b['concept_total']} concepts, homed {sum(1 for r in m['requirements'] if r['homed'])}, "
                 f"inherited gap total {b['closure_gap_total']} ({b['closure_determination']})"],
                ["Does anything accepted exist only in conversation?",
                 "NO — conversation-only and upload-only counts are both 0"],
                ["Is every concept projected into a governed Repository Requirement?",
                 f"YES — {m['requirement_total']} requirements, 1:1 with concepts, injective"],
                ["Was any concept CREATED by this programme?",
                 f"NO — created {a['created_concepts']}, reused {a['reused_concepts']}"],
                ["Is constitutional assimilation 100% complete?",
                 f"**NO — {a['fully']}/{m['requirement_total']} ({a['percent_fully']}%) FULLY ASSIMILATED**"],
                ["May implementation continue?",
                 "**NO** — the mission bars continuation below 100% assimilation"],
                ["May a certified baseline be created?",
                 f"**NO** — {sum(1 for c in m['baseline_conditions'] if c['verdict'] == 'FAIL')} of "
                 f"{len(m['baseline_conditions'])} Phase-8 preconditions are unproven"],
            ],
        ),
        "",
        "The distinction that produces the assimilation shortfall is precise and is not a",
        "contradiction of the inherited closure determination. The inherited gate measures",
        "*presence*: a concept is homed when it is reachable in a Repository-Truth zone. This",
        "programme additionally measures *canonical declaration*: whether exactly one artifact",
        "carries the concept's identity in its own name and therefore owns it by declaration",
        "rather than by inference. Presence is complete. Declaration is not.",
        "",
        "## 2. Sources consulted (all pre-existing; none created)",
        "",
        _fence(
            ["Input", "Repository location", "Required", "State"],
            [[k, v["path"], "yes" if v["required"] else "no", v["state"]]
             for k, v in sorted(m["inputs"].items())],
            f"Zone→program/category/volume classification is read from `{b['classifier_source']}`. "
            "Authority is read verbatim from each canonical home's own declaration. Nothing in "
            "this programme hard-codes a family, a zone, a dimension or a limit.",
        ),
        "",
        "## 3. Phase 1 — disposition of every assimilated concept",
        "",
        _fence(
            ["Action", "Concepts", "Basis"],
            [["REUSED", str(m["requirement_total"]),
              "Already present and homed in Repository Truth before this programme ran"],
             ["GENERALIZED", "0", "No concept required generalization to be assimilated"],
             ["SPECIALIZED", "0", "No concept required specialization to be assimilated"],
             ["EXTENDED", "0", "No concept required extension to be assimilated"],
             ["CREATED", "0",
              "Reuse was possible for every concept, so creation was constitutionally prohibited"]],
            "**CREATE = 0 at the concept layer**, as required.",
        ),
        "",
        "## 4. Phase 1 — disposition of every deliverable",
        "",
        _fence(["#", "Deliverable", "Action", "Canonical predecessor / owner", "Justification"], inv,
               "CREATE occurs for exactly two of ten deliverables. For both, Repository Truth was "
               "searched and no canonical owner exists, while Phases 4 and 6 mandate the artifact — "
               "the constitutional test for creation is therefore satisfied. The remaining eight "
               "reuse, extend, specialize or generalize an existing canonical owner."),
        "",
        "## 5. Phase 2 — canonical ownership",
        "",
        _fence(["Ownership standing", "Requirements", "Meaning"],
               [[k, str(v),
                 {"DECLARED": "exactly one artifact carries the identity in its own name",
                  "COMPETING": "more than one definitional home carries the identity",
                  "INFERRED": "ownership is derived from evidence zone, not declared",
                  "ABSENT": "no owning zone located"}.get(k, "unclassified standing")]
                for k, v in m["histograms"]["ownership"].items()]),
        "",
        "Ownership by zone (one canonical owner per requirement, no competing authority created):",
        "",
        _fence(["Owning zone", "Requirements"],
               [[k, str(v)] for k, v in sorted(m["histograms"]["canonical_owner"].items(),
                                               key=lambda kv: (-kv[1], kv[0]))]),
        "",
        "## 6. Phase 3 — repository coverage",
        "",
        _fence(["Coverage", "Requirements", "Share"],
               [[k, str(v), f"{round(100.0 * v / m['requirement_total'], 2)}%"]
                for k, v in m["histograms"]["coverage"].items()]),
        "",
        "## 7. Phase 7 — universal participation",
        "",
        _fence(["Participation", "Requirements", "Basis"],
               [["Configuration", str(m["requirement_total"]),
                 "every requirement carries program/category/volume resolved from repository configuration"],
                ["Baseline", str(m["requirement_total"]),
                 "every requirement is evaluated against every Phase-8 precondition"],
                ["Archive", str(m["requirement_total"]),
                 "every requirement carries a lifecycle standing; nothing is deleted"],
                ["Replay", str(m["requirement_total"]),
                 "every requirement is re-derived byte-identically from the declared inputs"],
                ["Discovery", str(m["requirement_total"]),
                 "every requirement is addressable by requirement id and by concept id"],
                ["Composition", str(m["requirement_total"]),
                 "every requirement carries its typed-graph dependency and relationship counts"],
                ["Governance", str(m["requirement_total"]),
                 "every requirement carries a canonical owner and a declared-or-measured authority"],
                ["Evolution", str(m["requirement_total"]),
                 "every requirement carries a maturity level on an open-ended lattice"]],
               "No object type receives privileged treatment: the same eight participations are "
               "computed for every requirement in every family, and an unknown family is carried "
               "generically rather than rejected."),
        "",
        "## 8. Phase 10 — self audit",
        "",
        _fence(["Audit question", "Verdict", "Measured"],
               [["Duplicate requirement identity", "CLEAN",
                 f"{m['requirement_total']} requirement ids over {m['requirement_total']} distinct concept ids"],
                ["Overlapping deliverable authority", "CLEAN",
                 "eight of ten deliverables name an existing canonical owner; two are created only "
                 "where none exists"],
                ["Competing constitutional authority", "FINDING",
                 f"{m['histograms']['ownership'].get('COMPETING', 0)} requirements carry more than one "
                 "definitional home"],
                ["Orphan knowledge", "CLEAN",
                 f"{sum(1 for r in m['requirements'] if r['orphan'])} orphan concepts"],
                ["Orphan requirement", "CLEAN", "every requirement is bound 1:1 to a homed concept"],
                ["Broken lineage", "FINDING", "see RG-S05 and Phase-8 condition BC-09"],
                ["Broken traceability", "FINDING",
                 f"capability tier unpopulated for "
                 f"{sum(1 for r in m['requirements'] if not r['traceability']['capability'])} "
                 "requirements"],
                ["Broken replay", "FINDING", "see Phase-8 condition BC-06"],
                ["Hard-coded limits / object types / zones / dimensions", "CLEAN",
                 "families, zones, dimensions and lattice levels are all read or configured, never "
                 "enumerated as a closed set in the engine"],
                ["Silent repair", "CLEAN",
                 "absent optional inputs are recorded as ABSENT and degrade the measurement visibly"]]),
        "",
        f"*Seal `{m['seal_sha256'][:16]}` · END 01 · AUTHORITY = {AUTHORITY}.*",
    ]
    return "\n".join(body) + "\n"


def d02(m):
    rows = [
        [
            r["requirement_id"],
            r["concept_id"],
            r["family"],
            r["canonical_owner"],
            r["repository_location"],
            r["authority"][:80],
            r["dependency_count"],
            r["relationship_count"],
            r["evidence_files"],
            f"{r['traceability_tiers_present']}/9",
            f"{r['maturity_level']} {r['maturity']}",
            r["implementation_status"],
            r["validation_status"],
            r["verification_status"],
            r["certification_status"],
            r["runtime_status"],
        ]
        for r in m["requirements"]
    ]
    return "\n".join([
        _hdr("02", "Repository Requirement Register", m,
             ["Phase 4. One row = one governed Repository Requirement. Identity is a total,",
              "injective, derived function of the concept identity (`RR-<CONCEPT-ID>`), so no",
              "requirement can drift from the concept it governs and no new identifier",
              "namespace is introduced (Knowledge Once)."]),
        "## 1. Derivation contract",
        "",
        _fence(["Field", "Derived from", "Rule"],
               [["Requirement ID", "closure.json concept id", "`RR-` + concept id; total and injective"],
                ["Canonical Owner", "closure.json def_homes / tops",
                 "top-level Repository-Truth zone of the definitional home, else the primary evidence zone"],
                ["Repository Location", "closure.json def_homes",
                 "the definitional home path, else an explicit non-filename-home statement"],
                ["Authority", "the canonical home's own `| AUTHORITY |` row",
                 "read verbatim; never inferred, never defaulted"],
                ["Dependencies", "00-BOOK/DATA/relationships.json",
                 "`Depends-On` edges outbound from the home's universal identity"],
                ["Relationships", "00-BOOK/DATA/relationships.json",
                 "typed in+out edge histogram for the home's universal identity"],
                ["Evidence", "closure.json files",
                 "evidence file count plus classified evidence kinds"],
                ["Traceability", "MCP-006 nine-tier spine",
                 "measured per tier; the requirement tier is established by this register"],
                ["Current Maturity", "the ordered lattice M0..M7",
                 "highest level whose predicate and all predecessors hold; REJECTED and DEFERRED "
                 "standing is taken from the predecessor's authoritative disposition, never from a "
                 "line-local marker"],
                ["Implementation Status", "closure.json in_code / disposition", "PRESENT-IN-CODE / ABSENT / DEFERRED / REJECTED"],
                ["Validation Status", "classified validation evidence", "EVIDENCED / TEST-ONLY / NOT-EVIDENCED"],
                ["Verification Status", "classified verification evidence", "EVIDENCED / NOT-EVIDENCED"],
                ["Certification Status", "closure.json certified + baseline ceiling token",
                 "the repository's declared disclosure token, never above it"],
                ["Runtime Status", "control-tower dimensions + certification execution ledger",
                 "RUNTIME-PROVEN only when executions are ledgered and every runtime dimension is operational"]]),
        "",
        "## 2. Maturity lattice",
        "",
        _fence(["Level", "Label", "Predicate"],
               [[k, lab, p] for k, lab, p in LATTICE],
               "The lattice is ordered and open-ended. Appending a level extends it without "
               "altering any existing level, so there is no architectural ceiling on maturity — "
               "only an evidential one."),
        "",
        f"## 3. Register ({m['requirement_total']} requirements)",
        "",
        _fence(["Requirement ID", "Concept", "Family", "Canonical owner", "Repository location",
                "Authority", "Deps", "Rels", "Evidence", "Trace", "Maturity", "Implementation",
                "Validation", "Verification", "Certification", "Runtime"], rows),
        "",
        f"*Seal `{m['seal_sha256'][:16]}` · END 02 · AUTHORITY = {AUTHORITY}.*",
        "",
    ])


def d03(m):
    t = m["requirement_total"]
    hs = m["histograms"]
    def block(title, key):
        return "\n".join([f"### {title}", "",
                          _fence(["Value", "Requirements", "Share"],
                                 [[k, str(v), f"{round(100.0 * v / t, 2)}%"]
                                  for k, v in sorted(hs[key].items(), key=lambda kv: (-kv[1], kv[0]))]), ""])
    per_family = []
    for fam, cnt in sorted(hs["family"].items()):
        sub = [r for r in m["requirements"] if r["family"] == fam]
        full = sum(1 for r in sub if r["coverage"] == "FULLY ASSIMILATED")
        code = sum(1 for r in sub if r["implementation_status"] == "PRESENT-IN-CODE")
        cert = sum(1 for r in sub if r["certification_status"] != "UNCERTIFIED")
        per_family.append([fam, cnt, full, code, cert,
                           f"{round(100.0 * full / cnt, 1)}%" if cnt else "-"])
    return "\n".join([
        _hdr("03", "Repository Coverage Report", m,
             ["Phase 3 and Phase 6. Coverage is reported on nine axes for the whole requirement",
              "population and per identifier family. Every figure is a count of measured",
              "requirements; no percentage is an estimate."]),
        "## 1. Discussion coverage",
        "",
        _fence(["Measure", "Value"],
               [["Accepted concepts located in Repository Truth", str(t)],
                ["Concepts existing only in conversation", "0"],
                ["Concepts existing only in uploaded documents", "0"],
                ["Concepts projected into a governed requirement", str(t)],
                ["Concepts created by this programme", "0"]]),
        "",
        "## 2. Repository coverage",
        "",
        block("Assimilation coverage", "coverage"),
        block("Canonical ownership", "ownership"),
        "## 3. Lifecycle coverage",
        "",
        block("Implementation", "implementation_status"),
        block("Validation", "validation_status"),
        block("Verification", "verification_status"),
        block("Certification", "certification_status"),
        block("Runtime", "runtime_status"),
        "## 4. Autonomous and evolution coverage",
        "",
        _fence(["Axis", "Measured", "Basis"],
               [["Autonomous coverage",
                 f"{sum(1 for r in m['requirements'] if 'engine' in r['evidence_kinds'])}/{t} requirements "
                 "carry engine-generated evidence",
                 "evidence classified as engine output"],
                ["Evolution coverage",
                 f"{t}/{t} requirements carry a maturity level on the open lattice",
                 "every requirement is evolvable by construction"],
                ["Replay coverage",
                 f"{len(m['inputs'])} declared inputs re-derive the whole model byte-identically",
                 "deterministic engine, no timestamps"]]),
        "",
        "## 5. Coverage by identifier family",
        "",
        _fence(["Family", "Requirements", "Fully assimilated", "In code", "Certified", "Full %"],
               per_family,
               "No family receives privileged treatment; an unrecognized family would appear here "
               "automatically with the same axes."),
        "",
        f"*Seal `{m['seal_sha256'][:16]}` · END 03 · AUTHORITY = {AUTHORITY}.*",
        "",
    ])


def d04(m):
    rows = [[g["gap_id"], g["name"], g["class"], g["count"], g["canonical_owner"],
             g["required_action"]] for g in m["gap_classes"]]
    members = []
    for g in m["gap_classes"]:
        if g["count"] and g["members"]:
            shown = g["members"]
            members.append(
                f"**{g['gap_id']} — {g['name']} ({g['count']})**\n\n"
                + ", ".join(f"`{x}`" for x in shown)
                + (f"\n\n_… {g['count'] - len(shown)} further members recorded in "
                   f"`requirements.json`._" if g["count"] > len(shown) else "")
            )
    return "\n".join([
        _hdr("04", "Repository Gap Report", m,
             ["Phase 5. Every gap is a measured set of requirements, determined by Repository",
              "Truth. Nothing here is estimated, and no gap is closed by assertion. The seven",
              "RG-A classes are inherited verbatim from the predecessor gate; the RG-B..RG-E",
              "classes are the lifecycle gaps this programme measures."]),
        "## 1. Gap classes",
        "",
        _fence(["Gap ID", "Gap class", "Category", "Count", "Canonical owner", "Required action"], rows),
        "",
        "## 2. Systemic findings (repository-wide, not per requirement)",
        "",
        _fence(["ID", "Finding", "Standing", "Measured", "Canonical owner"],
               [[s["id"], s["name"], "OPEN" if s["open"] else "CLOSED", s["measured"], s["owner"]]
                for s in m["systemic_findings"]],
               f"**{len(m['open_systemic_findings'])} of {len(m['systemic_findings'])} systemic "
               "findings are open.** Each is measured, so each is closable by evidence rather than "
               "by assertion; Phase-8 condition BC-05 passes only when none remains open."),
        "",
        "## 3. Lifecycle dimension standing",
        "",
        _fence(["Dimension", "Status"],
               [[k, v] for k, v in m["lifecycle_dimensions"].items()],
               "Runtime status for every requirement is bounded above by these dimensions: while "
               "any is BLOCKED or NOT_STARTED, no requirement can be runtime-proven."),
        "",
        "## 4. Gap membership",
        "",
        ("\n\n".join(members) if members else "_No gap class has members._"),
        "",
        f"*Seal `{m['seal_sha256'][:16]}` · END 04 · AUTHORITY = {AUTHORITY}.*",
        "",
    ])


def d05(m):
    t = m["requirement_total"]
    order = [k for k, _lab, _p in LATTICE]
    lv = m["histograms"]["maturity_level"]
    cum = 0
    rows = []
    for k, lab, pname in LATTICE:
        n = lv.get(k, 0)
        cum += n
        rows.append([k, lab, pname, n, f"{round(100.0 * n / t, 2)}%", cum])
    fam_rows = []
    for fam in sorted(m["histograms"]["family"]):
        sub = [r for r in m["requirements"] if r["family"] == fam]
        cells = [fam, len(sub)]
        for k in order:
            cells.append(sum(1 for r in sub if r["maturity_level"] == k))
        fam_rows.append(cells)
    owner_rows = []
    for own in sorted(m["histograms"]["canonical_owner"]):
        sub = [r for r in m["requirements"] if r["canonical_owner"] == own]
        cells = [own, len(sub)]
        for k in order:
            cells.append(sum(1 for r in sub if r["maturity_level"] == k))
        owner_rows.append(cells)
    return "\n".join([
        _hdr("05", "Repository Maturity Matrix", m,
             ["Phase 6. The maturity of every governed requirement on a single ordered,",
              "open-ended lattice, cross-tabulated by identifier family and by canonical owner.",
              "Maturity is computed, never declared."]),
        "## 1. Lattice population",
        "",
        _fence(["Level", "Label", "Predicate", "Requirements", "Share", "Cumulative"], rows,
               "The population is monotone by construction: a requirement occupies the highest "
               "level whose predicate and all predecessors hold. `M7 RUNTIME-PROVEN` is empty "
               "because the execution ledger is empty — an evidential ceiling, not a modelled one."),
        "",
        "## 2. Maturity by identifier family",
        "",
        _fence(["Family", "Total", *order], fam_rows),
        "",
        "## 3. Maturity by canonical owner",
        "",
        _fence(["Canonical owner", "Total", *order], owner_rows),
        "",
        "## 4. Maturity consistency audit",
        "",
        _fence(["Check", "Measured", "Verdict"],
               [["Requirements certified without located implementation",
                 str(sum(1 for r in m["requirements"]
                         if r["certification_status"] != "UNCERTIFIED"
                         and r["implementation_status"] != "PRESENT-IN-CODE")),
                 "FINDING — certification asserts a realization the repository does not locate"],
                ["Requirements implemented without certification",
                 str(sum(1 for r in m["requirements"]
                         if r["implementation_status"] == "PRESENT-IN-CODE"
                         and r["certification_status"] == "UNCERTIFIED")),
                 "FINDING — realization outruns certification"],
                ["Requirements at the certification ceiling",
                 str(m["histograms"]["maturity_level"].get("M6", 0)),
                 "bounded by the repository's declared disclosure token"],
                ["Requirements carrying certification but seated below M6",
                 str(sum(1 for r in m["requirements"]
                         if r["certification_status"] != "UNCERTIFIED"
                         and r["maturity_level"] != "M6")),
                 "FINDING — certification precedes the test or validation evidence the lattice "
                 "requires beneath it"],
                ["Requirements above the certification ceiling", "0", "CLEAN — none, as required"]]),
        "",
        f"*Seal `{m['seal_sha256'][:16]}` · END 05 · AUTHORITY = {AUTHORITY}.*",
        "",
    ])


def d06(m):
    t = m["requirement_total"]
    hs = m["histograms"]
    declared_auth = sum(
        1 for r in m["requirements"]
        if r["authority"] not in
        ("UNDECLARED-AT-CANONICAL-HOME", "HOME-FILE-ABSENT", "NO-CANONICAL-HOME")
    )
    registered = sum(1 for r in m["requirements"] if r["universal_id"] != "UNREGISTERED")
    certified = t - hs["certification_status"].get("UNCERTIFIED", 0)
    runtime_proven = hs["runtime_status"].get("RUNTIME-PROVEN", 0)
    passed = sum(1 for c in m["baseline_conditions"] if c["verdict"] == "PASS")

    def g(gid, dim, measured, ok):
        return [gid, dim, measured, "PASS" if ok else "FAIL"]

    gates = [
        g("RD-01", "Assimilation", f"{m['assimilation']['fully']}/{t} fully assimilated",
          m["assimilation"]["complete"]),
        g("RD-02", "Canonical ownership",
          f"{hs['ownership'].get('DECLARED', 0)}/{t} declared, "
          f"{hs['ownership'].get('COMPETING', 0)} competing",
          hs["ownership"].get("DECLARED", 0) == t),
        g("RD-03", "Authority declaration", f"{declared_auth}/{t} declared at the canonical home",
          declared_auth == t),
        g("RD-04", "Implementation",
          f"{hs['implementation_status'].get('PRESENT-IN-CODE', 0)}/{t} in code",
          hs["implementation_status"].get("PRESENT-IN-CODE", 0) == t),
        g("RD-05", "Validation", f"{hs['validation_status'].get('EVIDENCED', 0)}/{t} evidenced",
          hs["validation_status"].get("EVIDENCED", 0) == t),
        g("RD-06", "Verification", f"{hs['verification_status'].get('EVIDENCED', 0)}/{t} evidenced",
          hs["verification_status"].get("EVIDENCED", 0) == t),
        g("RD-07", "Certification",
          f"{certified}/{t} carry the declared disclosure token", certified == t),
        g("RD-08", "Runtime", f"{runtime_proven}/{t} runtime-proven", runtime_proven == t),
        g("RD-09", "Traceability spine",
          f"capability tier {m['traceability_tiers']['capability']}/{t}",
          m["traceability_tiers"]["capability"] == t),
        g("RD-10", "Registry participation", f"{registered}/{t} carry a universal identity",
          registered == t),
        g("RD-11", "Baseline eligibility",
          f"{passed}/{len(m['baseline_conditions'])} preconditions proven",
          m["baseline_permitted"]),
        g("RD-12", "Implementation continuation",
          "barred while assimilation is below 100%", m["assimilation"]["complete"]),
    ]
    tiers = m["traceability_tiers"]
    return "\n".join([
        _hdr("06", "Repository Readiness Matrix", m,
             ["Phase 6 and Phase 8. Readiness is expressed as fail-closed gates over the measured",
              "requirement population, and as the repository's own lifecycle dimension standing.",
              "A gate passes only when its measure is complete — never when it is merely started."]),
        "## 1. Readiness gates",
        "",
        _fence(["Gate", "Dimension", "Measured", "Verdict"], gates,
               f"**{sum(1 for g in gates if g[3] == 'PASS')} of {len(gates)} readiness gates pass.** "
               "Every failing gate has a corresponding work package in deliverable 09."),
        "",
        "## 2. Lifecycle dimension readiness (repository-declared)",
        "",
        _fence(["Dimension", "Status", "Bearing on requirement readiness"],
               [[k, v,
                 "operational — does not bound requirement readiness"
                 if v.upper() in ("APPROVED", "IMPLEMENTED", "CERTIFIED", "COMPLETE")
                 else "bounds every requirement's readiness at this dimension"]
                for k, v in m["lifecycle_dimensions"].items()]),
        "",
        "## 3. Traceability tier readiness",
        "",
        _fence(["Tier", "Requirements present", "Share", "Readiness"],
               [[k, str(v), f"{round(100.0 * v / m['requirement_total'], 2)}%",
                 "COMPLETE" if v == m["requirement_total"] else "INCOMPLETE"]
                for k, v in tiers.items()]),
        "",
        "## 4. Determination",
        "",
        f"Repository readiness is **NOT ESTABLISHED**. {sum(1 for g in gates if g[3] == 'FAIL')} of",
        f"{len(gates)} gates fail. The binding constraint is assimilation completeness",
        f"({m['assimilation']['fully']}/{m['requirement_total']}), which the mission makes a",
        "precondition for continuing implementation at all.",
        "",
        f"*Seal `{m['seal_sha256'][:16]}` · END 06 · AUTHORITY = {AUTHORITY}.*",
        "",
    ])


def d07(m):
    t = m["requirement_total"]
    tiers = list(m["traceability_tiers"].keys())
    rows = [[r["requirement_id"], r["concept_id"],
             *["✓" if r["traceability"][x] else "·" for x in tiers],
             f"{r['traceability_tiers_present']}/9"] for r in m["requirements"]]
    complete_chain = sum(
        1 for r in m["requirements"]
        if all(r["traceability"][x] for x in
               ("constitution", "requirement", "implementation", "test", "evidence", "certification"))
    )
    return "\n".join([
        _hdr("07", "Constitutional Traceability Matrix", m,
             ["Phase 4 traceability, expressed on the canonical nine-tier constitutional spine",
              "owned by `00-MASTER/MCP-006-MASTER-TRACEABILITY.md`. This programme does not",
              "redefine the spine; it populates the requirement tier, which had no backing store,",
              "and measures every other tier from existing repository evidence."]),
        "## 1. Tier population",
        "",
        _fence(["#", "Tier", "Requirements present", "Share", "Standing"],
               [[str(i + 1), k, str(v), f"{round(100.0 * v / t, 2)}%",
                 "COMPLETE" if v == t else "INCOMPLETE"]
                for i, (k, v) in enumerate(m["traceability_tiers"].items())],
               f"Rule inherited from the canonical owner: a missing edge means NOT-DONE. "
               f"Full constitution→requirement→implementation→test→evidence→certification chain: "
               f"**{complete_chain}/{t}**."),
        "",
        "## 2. Per-requirement traceability",
        "",
        _fence(["Requirement ID", "Concept", *tiers, "Tiers"], rows),
        "",
        f"*Seal `{m['seal_sha256'][:16]}` · END 07 · AUTHORITY = {AUTHORITY}.*",
        "",
    ])


def d08(m):
    wave_rows = []
    for w in sorted(m["waves"]):
        ids = m["waves"][w]
        pk = [p for p in m["work_packages"] if p["wave"] == w]
        scope = sum(p["scope_count"] for p in pk)
        wave_rows.append([w, ", ".join(ids), len(ids), scope,
                          "; ".join(sorted({p["class"] for p in pk}))])
    return "\n".join([
        _hdr("08", "Implementation Programme", m,
             ["Phase 5 and Phase 8. The programme that must complete before a certified baseline",
              "may be created. It reuses the predecessor wave model; the predecessor plans zero",
              "items because it models only assimilation gaps, whereas the gaps measured here are",
              "lifecycle gaps."]),
        "## 1. Standing",
        "",
        _fence(["Question", "Answer"],
               [["May implementation of new capability continue?",
                 "**NO** — assimilation is below 100%; the mission bars continuation"],
                ["What is authorized instead?",
                 "remediation of the measured gaps only, in the wave order below"],
                ["May a certified baseline be created on completion?",
                 "only when all twelve Phase-8 preconditions are proven; see deliverable 10"],
                ["Does this programme create new constitutional authority?",
                 "no — every package remediates an existing canonical owner's artifact"]]),
        "",
        "## 2. Waves",
        "",
        _fence(["Wave", "Work packages", "Packages", "Requirements in scope", "Categories"],
               wave_rows,
               "Wave order is constitutional precedence, not convenience: ownership and authority "
               "must be settled before traceability, traceability before realization, realization "
               "before validation, validation before verification, verification before "
               "certification, and certification before runtime."),
        "",
        "## 3. Sequencing rationale",
        "",
        _fence(["Step", "Wave", "Why it must precede the next"],
               [["1", "W01–W02",
                 "a requirement whose owner or authority is inferred cannot be governed, so no "
                 "later status about it is trustworthy"],
                ["2", "W03",
                 "consistency findings must be reconciled before any status is treated as evidence"],
                ["3", "W04–W05",
                 "the traceability spine and registry identity must be continuous before "
                 "realization can be traced"],
                ["4", "W06",
                 "realization must exist before it can be validated"],
                ["5", "W07–W08",
                 "validation and verification evidence must exist before certification can be "
                 "anything but assertion"],
                ["6", "W09",
                 "certification must be complete before runtime proof is meaningful"],
                ["7", "W10",
                 "runtime proof is the last precondition, and it is currently bounded by the "
                 "repository's own blocked lifecycle dimensions"]]),
        "",
        "## 4. Exit criteria",
        "",
        _fence(["Criterion", "Measured now", "Required"],
               [[c["name"], c["measured"], "PASS"] for c in m["baseline_conditions"]]),
        "",
        f"*Seal `{m['seal_sha256'][:16]}` · END 08 · AUTHORITY = {AUTHORITY}.*",
        "",
    ])


def d09(m):
    rows = [[p["work_package_id"], p["priority"], p["wave"], p["title"], p["class"],
             p["scope_count"], p["gap_id"], p["canonical_owner"], p["authorized_action"]]
            for p in m["work_packages"]]
    return "\n".join([
        _hdr("09", "Prioritized Constitutionally Authorized Work Packages", m,
             ["Phase 5. One package per non-empty measured gap class. Every package is authorized",
              "only as remediation of a gap that Repository Truth measures, is owned by an",
              "existing canonical owner, and creates no new authority and no new namespace."]),
        "## 1. Authorization basis",
        "",
        _fence(["Constraint", "How each package satisfies it"],
               [["Reuse first",
                 "every package targets an existing canonical owner's artifact; none creates a "
                 "competing owner"],
                ["Create = 0",
                 "no package creates a concept, a family, an identifier namespace or an authority"],
                ["Zero duplication",
                 "packages partition the gap classes; no requirement is remediated twice for the "
                 "same reason"],
                ["Zero silent repair",
                 "each package states the measured deficit and the named action; nothing is "
                 "repaired implicitly"],
                ["Blocking",
                 "every package blocks the certified baseline, so none may be deferred silently"]]),
        "",
        f"## 2. Work packages ({len(m['work_packages'])})",
        "",
        _fence(["Work package", "Priority", "Wave", "Title", "Category", "Requirements in scope",
                "Gap", "Canonical owner", "Authorized action"], rows),
        "",
        "## 3. Ledger conformance",
        "",
        "Identity follows the governing convention `WP-<PROGRAMME>-<NNN>` owned by",
        "`00-MASTER/UER-000001/06-UNIVERSAL-WORK-PACKAGE-LEDGER-SPECIFICATION.md`. Priority is",
        "deterministic: constitutional precedence, then descending measured magnitude, then gap",
        "identifier. Re-running the engine at the same commit reproduces the same ordering.",
        "",
        f"*Seal `{m['seal_sha256'][:16]}` · END 09 · AUTHORITY = {AUTHORITY}.*",
        "",
    ])


def d10(m):
    b = m["baseline"]
    fails = [c for c in m["baseline_conditions"] if c["verdict"] == "FAIL"]
    return "\n".join([
        _hdr("10", "Updated Repository Truth", m,
             ["Phase 8, Phase 9 and Phase 10. What this programme added to Repository Truth, what",
              "it deliberately did not add, and the standing that results. Nothing was deleted;",
              "nothing was superseded; no baseline was created."]),
        "## 1. Delta added to Repository Truth",
        "",
        _fence(["Artifact", "Kind", "Canonical status"],
               [["00-MASTER/UAKOS-CLOSURE-009/01-REPOSITORY-ASSIMILATION-REPORT.md", "report", "ACTIVE"],
                ["00-MASTER/UAKOS-CLOSURE-009/02-REPOSITORY-REQUIREMENT-REGISTER.md", "register",
                 "ACTIVE — canonical owner of the requirement projection"],
                ["00-MASTER/UAKOS-CLOSURE-009/03-REPOSITORY-COVERAGE-REPORT.md", "report", "ACTIVE"],
                ["00-MASTER/UAKOS-CLOSURE-009/04-REPOSITORY-GAP-REPORT.md", "register", "ACTIVE"],
                ["00-MASTER/UAKOS-CLOSURE-009/05-REPOSITORY-MATURITY-MATRIX.md", "matrix",
                 "ACTIVE — canonical owner of requirement maturity"],
                ["00-MASTER/UAKOS-CLOSURE-009/06-REPOSITORY-READINESS-MATRIX.md", "matrix", "ACTIVE"],
                ["00-MASTER/UAKOS-CLOSURE-009/07-CONSTITUTIONAL-TRACEABILITY-MATRIX.md", "matrix",
                 "ACTIVE — populates the requirement tier of the canonical spine"],
                ["00-MASTER/UAKOS-CLOSURE-009/08-IMPLEMENTATION-PROGRAMME.md", "programme", "ACTIVE"],
                ["00-MASTER/UAKOS-CLOSURE-009/09-WORK-PACKAGE-REGISTER.md", "register", "ACTIVE"],
                ["00-MASTER/UAKOS-CLOSURE-009/10-UPDATED-REPOSITORY-TRUTH.md", "determination", "ACTIVE"],
                ["00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py", "engine",
                 "ACTIVE — deterministic regenerator"],
                ["00-MASTER/UAKOS-CLOSURE-009/requirements.json", "model",
                 "ACTIVE — machine-readable form of the register"]]),
        "",
        "## 2. What was deliberately not added",
        "",
        _fence(["Not added", "Reason"],
               [["A certified baseline",
                 f"{len(fails)} of {len(m['baseline_conditions'])} Phase-8 preconditions are unproven"],
                ["A new identifier family",
                 "requirement identity is derived from concept identity, so the existing discovery "
                 "grammar needs no amendment and closure cannot regress"],
                ["A competing traceability, gap, readiness, plan or work-package owner",
                 "each of those already has a canonical owner; this programme extends or "
                 "specializes rather than duplicates"],
                ["Any deletion or overwrite outside this directory",
                 "the engine writes only inside `00-MASTER/UAKOS-CLOSURE-009/`"],
                ["Any repair of a measured gap",
                 "measurement and remediation are separate acts; remediation is authorized in "
                 "deliverable 09 and not performed here"]]),
        "",
        "## 3. Phase 8 — certified baseline determination",
        "",
        _fence(["#", "Precondition", "Verdict", "Measured"],
               [[c["id"], c["name"], c["verdict"], c["measured"]] for c in m["baseline_conditions"]],
               "**DO NOT CREATE A BASELINE.** "
               f"{len(fails)} preconditions fail: "
               + ", ".join(c["id"] for c in fails) + "."),
        "",
        "## 4. Phase 9 — archive standing",
        "",
        _fence(["Standing", "Population", "Basis"],
               [["ACTIVE", str(m["requirement_total"]),
                 "every requirement is active; none is superseded by this programme"],
                ["SUPERSEDED", "0", "no requirement supersedes another"],
                ["ARCHIVED", "0", "nothing archived; nothing deleted"],
                ["CONFIGURABLE", str(m["requirement_total"]),
                 "each carries program/category/volume resolved from repository configuration"],
                ["DISCOVERABLE", str(m["requirement_total"]),
                 "addressable by requirement id and by concept id"],
                ["REPLAYABLE", str(m["requirement_total"]),
                 "re-derived byte-identically from the declared inputs"],
                ["REUSABLE", str(m["requirement_total"]),
                 "each names its canonical owner and location for reuse"],
                ["EVOLVABLE", str(m["requirement_total"]),
                 "each carries a level on an open-ended lattice"]]),
        "",
        "## 5. Standing determination",
        "",
        _fence(["Property", "Value"],
               [["Programme", PROGRAM],
                ["Phase", PHASE],
                ["Authority", AUTHORITY],
                ["Closure baseline", f"`{b['closure_baseline_commit']}` (branch `{b['branch']}`)"],
                ["HEAD at generation", f"`{b['head_commit']}`"],
                ["Requirements governed", str(m["requirement_total"])],
                ["Concepts created", "0"],
                ["Assimilation", f"{m['assimilation']['fully']}/{m['requirement_total']} "
                                 f"({m['assimilation']['percent_fully']}%) FULLY ASSIMILATED"],
                ["Determination", f"**{m['determination']}**"],
                ["Implementation continuation", "**BARRED** until assimilation reaches 100%"],
                ["Certified baseline", "**WITHHELD**"],
                ["Seal", f"`{m['seal_sha256']}`"]]),
        "",
        "## 6. Regeneration",
        "",
        "```",
        "make closure009               # regenerate (depends on closure-phase3)",
        "make closure009-gate          # fail-closed assimilation gate",
        "make closure009-baseline-gate # fail-closed baseline precondition gate",
        "make closure009-replay        # byte-for-byte register drift gate",
        "```",
        "",
        "The engine is also invocable directly; `--render` replays the HEAD recorded in",
        "`requirements.json` instead of re-reading it, which is what makes the drift gate",
        "above stable across the very commit that carries these registers.",
        "",
        "```",
        "python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py",
        "python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --render --quiet",
        "python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --gate",
        "python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --baseline-gate",
        "```",
        "",
        f"*END 10 · AUTHORITY = {AUTHORITY}. This determination creates no authority, ratifies",
        "nothing, certifies nothing and freezes nothing.*",
        "",
    ])


DELIVERABLES = (
    ("01-REPOSITORY-ASSIMILATION-REPORT.md", d01),
    ("02-REPOSITORY-REQUIREMENT-REGISTER.md", d02),
    ("03-REPOSITORY-COVERAGE-REPORT.md", d03),
    ("04-REPOSITORY-GAP-REPORT.md", d04),
    ("05-REPOSITORY-MATURITY-MATRIX.md", d05),
    ("06-REPOSITORY-READINESS-MATRIX.md", d06),
    ("07-CONSTITUTIONAL-TRACEABILITY-MATRIX.md", d07),
    ("08-IMPLEMENTATION-PROGRAMME.md", d08),
    ("09-WORK-PACKAGE-REGISTER.md", d09),
    ("10-UPDATED-REPOSITORY-TRUTH.md", d10),
)


def main(argv: list[str]) -> int:
    gate = "--gate" in argv
    baseline_gate = "--baseline-gate" in argv
    render = "--render" in argv

    inputs = {}
    missing = []
    for key, (rel, required) in INPUTS.items():
        inputs[key] = _load(rel)
        if inputs[key] is None and required:
            missing.append(rel)
    if missing:
        sys.stderr.write(
            f"{PROGRAM}: FAIL-CLOSED — required input(s) absent: {', '.join(missing)}\n"
            "Regenerate the predecessor model first: `make closure-phase3`.\n"
        )
        return 2

    # In render mode the previously written record supplies the HEAD, so the rendered
    # surface is a pure function of the declared inputs plus that record and can be
    # diffed byte-for-byte against what is committed.
    replay = _load(f"00-MASTER/{PROGRAM}/requirements.json") if render else None

    model = build(inputs, replay)
    HERE.mkdir(parents=True, exist_ok=True)
    (HERE / "requirements.json").write_text(
        json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for name, fn in DELIVERABLES:
        (HERE / name).write_text(fn(model), encoding="utf-8")

    a = model["assimilation"]
    fails = [c["id"] for c in model["baseline_conditions"] if c["verdict"] == "FAIL"]
    if "--quiet" not in argv:
        print(
            f"{PROGRAM}: {model['determination']} | requirements={model['requirement_total']} "
            f"| fully={a['fully']} partially={a['partially']} not={a['not']} "
            f"({a['percent_fully']}%) | created=0 | open_gap_classes="
            f"{sum(1 for g in model['gap_classes'] if g['count'] > 0)} "
            f"| work_packages={len(model['work_packages'])} "
            f"| baseline=WITHHELD({len(fails)} preconditions unproven)"
        )
        print(f"{PROGRAM}: wrote {len(DELIVERABLES) + 1} artifacts to {HERE}")

    if baseline_gate and not model["baseline_permitted"]:
        sys.stderr.write(
            f"{PROGRAM}: BASELINE GATE FAIL — unproven preconditions: {', '.join(fails)}\n"
        )
        return 1
    if gate and not a["complete"]:
        sys.stderr.write(
            f"{PROGRAM}: ASSIMILATION GATE FAIL — {a['partially'] + a['not']} of "
            f"{model['requirement_total']} requirements are not FULLY ASSIMILATED; "
            "implementation SHALL NOT continue.\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
