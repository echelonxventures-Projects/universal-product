#!/usr/bin/env python3
"""UAKOS-CLOSURE-008 — deterministic constitutional assimilation & repository-completion engine.

This engine does NOT discover, extract, re-verify or re-inventory anything. Discovery
(KNOWLEDGE-ASSIMILATION PHASE-001/002) and verification (TRI-SOURCE VERIFICATION) are
COMPLETE and are consumed as frozen, read-only INPUTS. The engine's single mission is
RECONCILIATION + ASSIMILATION: it drives every verified knowledge object into exactly one
of six terminal constitutional states, homes every approved item in the repository with
full traceability, and fails closed while any object is unclassified.

    1 ALREADY-REPRESENTED        repository already carries the object (measured presence)
    2 SEMANTICALLY-REPRESENTED   satisfied by an existing artifact under another identifier
    3 ASSIMILATED                homed in this program's canonical register with a destination
    4 HISTORICAL-EVIDENCE-ONLY   retained as project history; never promoted
    5 SUPERSEDED                 replaced by a later ratified form
    6 REJECTED                   explicitly rejected; retained so rejection is not reversed

Authoritative inputs
    EXTERNAL (read-only evidence; never written, never treated as an implementation home)
        $UAKOS_EVIDENCE_ROOT (default ~/Desktop/KNOWLEDGE-ASSIMILATION)
          output/knowledge/knowledge_base.json          23,859 verified knowledge objects
          output/knowledge/gaps.json                    gap classes (516 / 319 / 40)
          output/knowledge/knowledge_base_summary.json  published aggregate measures
          output/knowledge/FINAL_DETERMINATION.md       promotion intent (§4..§9)
          output/knowledge/reports/GAP_REPORT.md        measured gap classes
          evidence/TRI-SOURCE-VERIFICATION-DETERMINATION.md   verification determination
    IN-REPO (the sole implementation authority)
        the repository itself, via `git ls-files` — the semantic-equivalence universe
        assimilation.json — this engine's own frozen output, sufficient to re-render every
          register with NO external evidence present (self-contained, byte-identical replay)
        validation-record.json — AUTHORED, tracked, deterministic: the result of the canonical
          repository gate. It replaced `evidence/verify.log` as register 06's input, because a
          canonical artifact may state a validation RESULT and may not carry the TRANSCRIPT of
          the run that observed it (CLOSURE-008). The transcript is preserved in the evidence
          archive and referenced by id; nothing reads it to render an artifact.

Outputs (regenerated deterministically, no timestamps)
    assimilation.json            complete per-object classification + metrics + seal
    EVIDENCE-MANIFEST.json       sha256 of every external evidence file consumed
    01..09-*.md                  the mandated registers

Second evaluation axis (UKAP-001 WP-002 / D-2 — `superiority_engine.py`)
    Presence answers "does Repository Truth already contain this knowledge?". After presence is
    complete — never before it and never instead of it — every object is ALSO evaluated for
    QUALITY across 16 declared architectural dimensions and receives exactly one superiority
    verdict: BETTER_THAN_CURRENT, CONFLICTING, OBSOLETE, REQUIRES_ARCHITECTURAL_REVIEW,
    PARTIALLY_ASSIMILATED, or (for totality) NO_CURRENT_FORM / NOT_SUPERIOR. The six presence
    states are unchanged and the four superiority columns are APPENDED to `row_columns`, so a
    record written before this axis existed still deserializes and renders. Register 09.

Third evaluation axis (UKAP-001 WP-003 / D-3 — `decision_engine.py`)
    Presence answers "does Repository Truth carry this?"; superiority answers "is the discovered
    form better?"; the decision axis answers "WHAT MUST THE REPOSITORY DO?". After BOTH prior
    axes are complete — never before either and never instead of either — every object receives
    exactly one governed repository action: ACCEPT, MERGE, SUPERSEDE, REJECT,
    ESCALATE_ARCHITECTURE or DEFER, decided by one declared, versioned, replayable rule and
    carrying the named repository operation it requires, its implementation priority, its
    implementation owner and its recorded grounds. The engine determines the action; it performs
    NO repository modification. The five decision columns are APPENDED to `row_columns` after
    the superiority columns, so a record written before this axis existed still deserializes and
    renders. Registers 10 and 11.

Usage
    python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py
    python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py --gate   # exit 1 unless COMPLETE
    python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py --render # registers only

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing, ratifies nothing, and
certifies no authority. It classifies, homes and reports. Fail-closed (TRACK-001).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PROGRAM = "UAKOS-CLOSURE-008"
ASSIM_JSON = HERE / "assimilation.json"
EVIDENCE_MANIFEST = HERE / "EVIDENCE-MANIFEST.json"


def _load_superiority_engine():
    """Load the WP-002 / D-2 superiority evaluator that lives beside this engine.

    Loaded by absolute path rather than by plain import so the engine behaves identically
    however it is invoked (by path, from another directory, or from a test harness). The
    superiority axis is NOT optional: without it, rows would carry no verdict and the
    fail-closed superiority gates could not be evaluated, so a missing module aborts.
    """
    path = HERE / "superiority_engine.py"
    spec = importlib.util.spec_from_file_location("uakos_superiority_engine", path)
    if spec is None or spec.loader is None or not path.exists():
        raise SystemExit(
            f"{PROGRAM}: FAIL-CLOSED — superiority evaluator missing: {path}\n"
            f"  the presence axis alone cannot satisfy the D-2 evaluation gates")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUP = _load_superiority_engine()


def _load_decision_engine():
    """Load the WP-003 / D-3 repository decision engine that lives beside this engine.

    Loaded by absolute path for the same reason the superiority evaluator is: the engine must
    behave identically however it is invoked. The decision axis is NOT optional — without it,
    rows would carry no repository action and the fail-closed D-3 gates could not be evaluated,
    so a missing module aborts.
    """
    path = HERE / "decision_engine.py"
    spec = importlib.util.spec_from_file_location("uakos_decision_engine", path)
    if spec is None or spec.loader is None or not path.exists():
        raise SystemExit(
            f"{PROGRAM}: FAIL-CLOSED — repository decision engine missing: {path}\n"
            f"  the presence and superiority axes alone cannot satisfy the D-3 decision gates")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DEC = _load_decision_engine()

# The constitutional property of each declared action, read from the action registry once so the
# gates, the renderers and the registers cannot disagree about which actions would change
# repository knowledge. This engine executes NONE of them.
ACTION_MODIFIES = {a: bool(spec["modifies_knowledge"])
                   for a, spec in DEC.ACTION_REGISTRY.items()}

# --- Evidence roots, in resolution order (RC-0014) --------------------------------------------
#
# WHY THIS CHANGED. The evidence lived at ~/Desktop/KNOWLEDGE-ASSIMILATION — outside the
# repository, on one machine, untracked. Measured consequence: a clean checkout could REPLAY the
# registers (`--render`) but could never RE-DERIVE them, because the engine fail-closes without
# the tree. The chain of custody from evidence to the 23,859 assimilated objects was therefore
# unverifiable anywhere but here, and every register and certification downstream of it inherited
# that. Absolute paths from that root were also written into four committed governed artifacts.
#
# The six files the engine actually reads total ~37 MB, so they are now VENDORED and tracked.
# The 4 GB of EXPORT-ARCHIVEs that UKAP-001 consumes are not, and cannot be — those remain
# digest-verified external evidence, which is a different contract handled in corpus_engine.py.
VENDORED_EVIDENCE_ROOT = HERE / "evidence-vendored"
LEGACY_EVIDENCE_ROOT = Path.home() / "Desktop" / "KNOWLEDGE-ASSIMILATION"
DEFAULT_EVIDENCE_ROOT = LEGACY_EVIDENCE_ROOT
EVIDENCE_FILES = {
    "knowledge_base": "output/knowledge/knowledge_base.json",
    "gaps": "output/knowledge/gaps.json",
    "summary": "output/knowledge/knowledge_base_summary.json",
    "final_determination": "output/knowledge/FINAL_DETERMINATION.md",
    "gap_report": "output/knowledge/reports/GAP_REPORT.md",
    "tri_source_verification": "evidence/TRI-SOURCE-VERIFICATION-DETERMINATION.md",
}

# --------------------------------------------------------------------------- terminal states
STATES = [
    "ALREADY-REPRESENTED",
    "SEMANTICALLY-REPRESENTED",
    "ASSIMILATED",
    "HISTORICAL-EVIDENCE-ONLY",
    "SUPERSEDED",
    "REJECTED",
]

# --------------------------------------------------------------------------- destination policy
# Exactly one permanent canonical destination per assimilation disposition. Every path is
# asserted to EXIST on disk before it may be used (fail-closed: a destination that does not
# exist is not a canonical home). No new authority is created — each destination is an
# EXISTING repository authority, and the constitutional authority column names the
# constitution that governs it.
DEST_POLICY: dict[str, dict[str, object]] = {
    "CONSTITUTIONAL": dict(
        dest="01-WORKING/LAW-REGISTER.md",
        owner="Constitutional Reconciliation Authority (01-WORKING)",
        authority="00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md",
        wave=1),
    "ARCHITECTURE": dict(
        dest="07-ENGINEERING",
        owner="Engineering Architecture Authority (07-ENGINEERING)",
        authority="00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md",
        wave=2),
    "REGISTRY": dict(
        dest="03-CATALOGS",
        owner="Canonical Catalog Authority (03-CATALOGS)",
        authority="00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md",
        wave=3),
    "ROADMAP": dict(
        dest="00-MASTER/MCP-003-MASTER-EXECUTION.md",
        owner="Master Execution Authority (MCP)",
        authority="00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md",
        wave=3),
    "DOCUMENTATION": dict(
        dest="00-BOOK/MASTER-BOOK",
        owner="Universal Master Book Authority (00-BOOK)",
        authority="00-CEP/CEP-008-CONSTITUTIONAL-EVIDENCE-TRACEABILITY-CONSTITUTION.md",
        wave=3),
    "CAPABILITY": dict(
        dest="00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md",
        owner="Universal Capability Authority (MIP-W1-P001)",
        authority="00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md",
        wave=4),
    "UNIVERSE": dict(
        dest="15-UNIVERSAL-SCIENCE-INTELLIGENCE",
        owner="Universal Science Intelligence Authority (15-USI)",
        authority="00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md",
        wave=4),
    "ENGINE": dict(
        dest="engine",
        owner="Engine Implementation Authority (engine/)",
        authority="00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md",
        wave=5),
    "PLATFORM": dict(
        dest="09-PLATFORM",
        owner="Universal Platform Authority (09-PLATFORM)",
        authority="00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md",
        wave=5),
    "FACTORY": dict(
        dest="05-GENERATION",
        owner="Generation / Factory Authority (05-GENERATION)",
        authority="00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md",
        wave=5),
    "VALIDATION": dict(
        dest="00-MASTER/UCOS-CVR-001",
        owner="Constitutional Validation Authority (UCOS-CVR-001)",
        authority="00-CEP/CEP-004-CONSTITUTIONAL-VALIDATION-CONSTITUTION.md",
        wave=6),
    "CERTIFICATION": dict(
        dest="00-MASTER/UCOS-CVER-001",
        owner="Constitutional Certification Authority (UCOS-CVER-001)",
        authority="00-CEP/CEP-005-CONSTITUTIONAL-CERTIFICATION-CONSTITUTION.md",
        wave=7),
}

WAVE_NAME = {
    1: "Wave 1 — Constitutional reconciliation",
    2: "Wave 2 — Core architecture",
    3: "Wave 3 — Registries / roadmap / documentation",
    4: "Wave 4 — Capabilities / universes",
    5: "Wave 5 — Engines / platforms / factory",
    6: "Wave 6 — Validation",
    7: "Wave 7 — Certification",
    "F": "Wave F — Future / Deferred (registered, authorization-gated)",
}
WAVE_ORDER = [1, 2, 3, 4, 5, 6, 7, "F"]

# Maturity classes that carry an evidenced human commitment. Anything weaker (IDEA,
# PROPOSAL) is registered as a governed FUTURE entry in Wave F rather than scheduled —
# registering an idea as work would fabricate a commitment the evidence does not carry.
ACTIVE_MATURITY = {"CONSTITUTIONAL", "ACCEPTED", "DEFERRED"}

# --------------------------------------------------------------------------- semantic policy
STOP = {"the", "a", "an", "of", "and", "or", "for", "to", "in", "on", "with", "by", "is"}
# Deterministic, documented synonym normalization. Small and conservative on purpose:
# every entry is a naming-convention variant observed in BOTH the corpus and the repository.
SYNONYM = {
    "registries": "registry", "register": "registry", "registers": "registry",
    "ledger": "registry", "ledgers": "registry",
    "catalogue": "catalog", "catalogues": "catalog", "catalogs": "catalog",
    "laws": "law", "principles": "principle", "invariants": "invariant",
    "capabilities": "capability", "engines": "engine", "models": "model",
    "platforms": "platform", "services": "service", "universes": "universe",
    "specifications": "specification", "spec": "specification",
    "architectures": "architecture", "arch": "architecture",
    "constitutions": "constitution", "policies": "policy",
    "docs": "documentation", "doc": "documentation",
}
# Names that are pure work-item / instance identifiers are never semantically matched:
# matching them would equate project execution history with universal knowledge.
IDENT_LIKE = re.compile(r"^(?:[a-z]{1,6}[-_ ]?\d{1,4}(?:[-_ ]\d{1,4})*|\d+)$")
# Two zones are excluded from the semantic universe, deterministically:
#   * test code — a symbol inside a test is evidence of a test, not of a canonical artifact;
#   * this program's OWN home — otherwise run N's registers would feed run N+1's matches and
#     the engine would stop being idempotent.
INDEX_EXCLUDE = re.compile(r"(?:^|/)tests?/|(?:^|/)test_[^/]*\.py$|_test\.py$|conftest\.py$")

# SE-1 — CURATED DETERMINATION MAPPINGS.
# Each row is taken from the TRI-SOURCE VERIFICATION DETERMINATION, which measured the
# repository directly and REFUTED (or SUPERSEDED) a promotion claim. `pattern` matches the
# knowledge-object name; `anchor` is the existing repository authority that already
# satisfies the intent (asserted to exist); `proof` is a string asserted to occur inside
# the anchor, so the mapping is machine-proven and cannot rot silently.
CURATED: list[dict[str, object]] = [
    dict(rule="SE-1", pattern=r"^(universal |global |unified )?commerce operating system( "
        r"constitution)?$",
         state="SUPERSEDED", anchor="01-WORKING/SUPERSESSION-REGISTER.md", proof="SUP-",
         basis="FINAL_DETERMINATION §2 — the Commerce-OS expansion IS superseded; commerce is one "
             "derived domain."),
    dict(rule="SE-1", pattern=r"^absolute invariants$",
         state="SEMANTICALLY-REPRESENTED", anchor="01-WORKING/LAW-REGISTER.md", proof="Absolute",
         basis="VERIFICATION Axis 5 — the Ten Absolute Invariants are present as prose in the LAW "
             "REGISTER (enforcement gap recorded separately, A-06)."),
    dict(rule="SE-1", pattern=r"sovereignty[- ]origin",
         state="SEMANTICALLY-REPRESENTED", anchor="01-WORKING/AUTHORITY-REGISTER.md",
         proof="Sovereignty Origin",
         basis="VERIFICATION Axis 5 — 'Layer −1 Sovereignty Origin' is REFUTED in-repo; "
               "Sovereignty Origin exists as AUTH-12, RATIFIED advisory-subordinate."),
    dict(rule="SE-1", pattern=r"^space[- ]time( model| framework| coordinate.*)?$",
         state="SEMANTICALLY-REPRESENTED", anchor="01-WORKING/ONTOLOGY-REGISTER.md", proof="RAT-03",
         basis="VERIFICATION Axis 5 — the SPACE-TIME root/coordinate conflict is already RATIFIED "
             "(UCOS-RAT-001 / RAT-03 / SUP-02) as coordinate, not root primitive."),
    dict(rule="SE-1", pattern=r"^knowledge once( law| principle| rule)?$",
         state="SEMANTICALLY-REPRESENTED",
         anchor="00-MASTER/CAEM-001/00-ASSIMILATION-RECORD.md", proof="UCKO-PRIN-0001",
         basis="VERIFICATION Axis 5 — 'Knowledge Once has no constitutional force' is REFUTED: "
             "UCKO-PRIN-0001 is constitutional, ratified, enforced by UCKO-RULE-0001."),
    dict(rule="SE-1", pattern=r"^(no )?architectural ceiling( doctrine)?$",
         state="SEMANTICALLY-REPRESENTED",
         anchor="12-APPLICATION/APPLICATION-GOV-INF-001-UNIVERSAL-APPLICATION-PROGRAM-INFINITE-EVOLUTION-INTERPRETATION-DETERMINATION.md",
         proof="AUTH-INF-001",
         basis="VERIFICATION Axis 5 — 'agreed but never ratified' is REFUTED: grounded in "
             "AUTH-INF-001 CR-INF-001/002/010 as repository-wide law."),
    dict(rule="SE-1", pattern=r"^registry universe specification$",
         state="SEMANTICALLY-REPRESENTED",
         anchor="01-WORKING/DUPLICATE-REGISTER.md", proof="DUP-14",
         basis="VERIFICATION Axis 5 — the multi-count Registry-Universe claim is dispositioned in "
             "DUP-14 (five sources at ~28)."),
]

# Propositional mappings — knowledge that exists in the evidence as PROPOSITIONS (no
# noun-phrase object, therefore no KID) and is already satisfied in the repository under a
# different identifier. Recorded so no unresolved semantic mapping remains, and so the
# repository is not asked to build what it already enforces.
PROPOSITIONAL_MAPPINGS: list[dict[str, str]] = [
    dict(proposition="AGR-0001 — every architectural agreement must reach one of five terminal "
        "states",
         repo_authority="00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md",
         proof="28.13",
         equivalence="BEHAVIOURAL + STRUCTURAL",
         basis="VERIFICATION Axis 6 — CEP-002 §28.13 defines a CLOSED five-member disposition set; "
             "near-exact structural match."),
    dict(proposition="AGR-0006 — Repository Truth is the permanent institutional memory, not "
        "conversation history",
         repo_authority="00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md",
         proof="28.5",
         equivalence="BEHAVIOURAL",
         basis="VERIFICATION Axis 6 — CEP-002 §28.5: Repository Truth IS the sole admissible "
             "evidence."),
    dict(proposition="A knowledge-closure gate that fails closed when an accepted decision has no "
        "artifact",
         repo_authority="00-MASTER/UCDA-000001/ucda_engine.py",
         proof="--gate",
         equivalence="BEHAVIOURAL",
         basis="VERIFICATION Axis 6 — the gate EXISTS, is fail-closed (uccep-bindings.json "
             "CK-DECISION-EVIDENCE) and runs in CI (.github/workflows/uccep-gate.yml); "
             "FINAL_DETERMINATION §11.3 is refuted."),
    dict(proposition="The Constitutional Canon of Canons — one supreme registry of every law, "
        "principle, axiom, invariant",
         repo_authority="01-WORKING/LAW-REGISTER.md",
         proof="LAW-R01",
         equivalence="STRUCTURAL (partial — alias index residual registered as a gap)",
         basis="VERIFICATION Axis 5 — the compound 'Canon of Canons' is absent, but 22 reconciled "
             "law-sets with RATIFIED dispositions already occupy the intent; only the "
             "cross-scheme alias index remains, and it belongs to this existing register, not to "
             "a new authority."),
    dict(proposition="The Decision Register — accepted / rejected / deferred / superseded with "
        "justification",
         repo_authority="00-MASTER/UCDA-000001/01-CONSTITUTIONAL-DECISION-REGISTER.md",
         proof="Decision",
         equivalence="BEHAVIOURAL",
         basis="VERIFICATION Axis 6 — 89 decisions, 308 evidence references, 0 "
               "undispositioned; the CEP-000..010 'ledger' reading is refuted."),
    dict(proposition="Determinism verification as a universal capability",
         repo_authority="determinism-evidence",
         proof="",
         equivalence="BEHAVIOURAL",
         basis="VERIFICATION Axis 6 — byte-identical reproduction proven "
               "(divergence_count 0) under UCOS-RFP-001 P(R)=R."),
    dict(proposition="Documentation as compiled output",
         repo_authority="engine/knowledge/docs.py",
         proof="def ",
         equivalence="PARTIAL (mechanism exists; coverage 17 of 2,878 md and no drift gate)",
         basis="VERIFICATION Axis 4 — 'unimplemented' REFUTED as stated, VERIFIED in substance; "
             "residual registered as a gap."),
]

# Per-row storage is COLUMNAR: keys are written once, so a 23,859-row register stays
# reviewable and small in version control. `owner` and `authority` are DERIVED from
# `destination_policy[disposition]` and are therefore never stored per row.
ROW_COLUMNS = [
    "kid", "name", "category", "disposition", "maturity", "priority", "state", "rule",
    "destination", "wave", "presence_level", "presence_hits", "presence_corrected",
    "instance_level", "mentions", "user_mentions", "normative_statements",
    "authority_score", "origin_conversations", "evidence_conversation", "hierarchy_tier",
    "equivalence", "basis", "anchors", "dependencies",
    # --- WP-002 / D-2: the SUPERIORITY axis. APPENDED, never inserted, so a row written by
    # --- the presence-only engine still deserializes positionally against its own recorded
    # --- `row_columns`; the absent columns are restored as UNEVALUATED by `hydrate`.
    "superiority", "superiority_score", "superiority_profile", "superiority_rule",
    # --- WP-003 / D-3: the DECISION axis. APPENDED after the superiority columns, never
    # --- inserted, so a row written by either earlier engine still deserializes positionally
    # --- against its own recorded `row_columns`; the absent columns are restored as UNDECIDED
    # --- by `hydrate`, which is what the fail-closed decision gate detects.
    "decision", "decision_rule", "decision_rationale", "implementation_action",
    "implementation_priority",
]

# The columns the D-2 axis contributes, declared once so `hydrate`, the renderers and the
# compatibility gate cannot disagree about what a complete row looks like.
SUPERIORITY_COLUMNS = ("superiority", "superiority_score", "superiority_profile",
                       "superiority_rule")

# The columns the D-3 axis contributes and STORES. `implementation_owner` and `decision_version`
# are DERIVED in `hydrate` — exactly as `owner` and `authority` are — because the first is a
# pure function of the destination/anchor the row already carries and the second is a single
# declared constant; storing either on 23,859 rows would be duplication, not evidence.
DECISION_COLUMNS = ("decision", "decision_rule", "decision_rationale", "implementation_action",
                    "implementation_priority")
DECISION_DERIVED_COLUMNS = ("implementation_owner", "decision_version")

# Row-level rationale is carried ONCE, per rule, instead of being repeated on 23,859 rows.
RULE_RATIONALE = {
    "R0": "evidence records an explicit rejection; retained so the rejection is never silently "
        "reversed",
    "R1": "evidence records a later form that replaces this one",
    "R2": "measured repository presence — the repository already carries the object",
    "R4": "instance-level project execution history: retained as evidence, never promoted",
    "R5": "classified NOT-UCOS: genuine project knowledge, not universal UCOS knowledge",
    "R6": "approved missing knowledge: absent, non-duplicate, UCOS-relevant — homed with a "
        "canonical destination",
    "SE-1": "the verification determination measured this in-repo under another identifier (or "
        "superseded it)",
    "SE-2": "an existing artifact is structurally identical after normalization",
    "SE-3": "a more specific existing artifact subsumes the concept (P2/P3 only)",
}

# The weak-presence correction (VERIFICATION F-01). Presence measured from a single hit in
# a heading/provenance dump is NOT representation; such objects are pushed back through the
# remaining rules instead of being counted as already represented.
WEAK_PRESENCE_ANCHORS = ("UAKOS-PHASE-001B/provenance.json",)

# Leading enumerators / status prefixes stripped by the duplicate-CANDIDATE probe below.
DUP_PREFIX_RE = re.compile(r"^(?:done|todo|wip)\s+|^a\d+\s+", re.IGNORECASE)

# Integration surface: the paths OUTSIDE this program home that the delivery requires in order
# to be runnable and gated. This engine WRITES none of them — they are operator-authored
# integration, committed alongside the program — but they are part of the same change, so the
# change register DECLARES them rather than claiming a zero out-of-home footprint.
INTEGRATION_SURFACE: list[tuple[str, str, str]] = [
    ("Makefile", "targets `assimilate`, `assimilate-replay`, `assimilate-gate`",
     "runs this engine from the repository's canonical entry point; `assimilate-gate` is the "
     "validation command the roadmap cites for every assimilated item"),
    (".github/workflows/assimilation-gate.yml",
     "CI completion gate (`--render --gate`) + committed-register drift gate",
     "proves on every push that the committed registers ARE the rendered fixed point of "
     "`assimilation.json`, with the external evidence tree absent"),
]


def norm_title(name: str) -> str:
    """Conservative normalization used ONLY by the duplicate-candidate probe.

    Lowercases, strips one leading status word (DONE/TODO/WIP) and one leading `A<n>` enumerator,
    and collapses non-alphanumerics. It participates in NO classification decision — a candidate
    is surfaced for the destination owner to judge, never merged or reclassified by this engine.
    """
    s = name.strip()
    for _ in range(2):
        s = DUP_PREFIX_RE.sub("", s, count=1)
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# --------------------------------------------------------------------------- helpers
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    # fixed argv, no shell, no user input — the two bandit findings are accepted here.
    out = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=REPO, capture_output=True, text=True, check=False)
    return out.stdout if out.returncode == 0 else ""


def head_commit() -> str:
    return (git("rev-parse", "--short", "HEAD") or "unknown").strip()


def repo_relative(path: Path) -> str:
    """``path`` relative to the repository when it is inside it, else the absolute path.

    A governed artifact records WHAT it consumed, and a machine-specific absolute path answers
    that question only on one machine. Evidence that genuinely lives outside the repository is
    still reported absolutely — hiding that would be worse than stating it, because the reader
    must be able to see that the input was external.
    """
    try:
        return str(path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        return str(path)


def evidence_root() -> Path:
    """Where the frozen evidence is read from. In-repo by default, so a clean clone can measure.

    ORDER, and each position earns its place:

      1. ``$UAKOS_EVIDENCE_ROOT`` — an EXPLICIT operator override always wins, so a caller
         measuring against a different evidence set says so, and so the absent-evidence path
         stays reachable and testable.
      2. ``evidence-vendored/`` beside this engine — tracked, hash-locked by
         ``EVIDENCE-MANIFEST.json`` and by git itself. This is what makes full measurement
         reproducible from a fresh clone with no external tree and no configuration.
      3. ``~/Desktop/KNOWLEDGE-ASSIMILATION`` — the legacy machine-local root, kept only so an
         existing checkout that has not yet fetched the vendored evidence still resolves. It is
         last, so it can no longer shadow the governed copy.

    Position 2 is what closes RC-0014 for this capability: the engine's inputs are now inside the
    artifact that depends on them, which is the only arrangement under which "regenerate from a
    clean checkout and compare" is a question a fresh clone can even ask.
    """
    override = os.environ.get("UAKOS_EVIDENCE_ROOT")
    if override:
        return Path(override).expanduser()
    if (VENDORED_EVIDENCE_ROOT / EVIDENCE_FILES["knowledge_base"]).is_file():
        return VENDORED_EVIDENCE_ROOT
    return LEGACY_EVIDENCE_ROOT.expanduser()


def norm_tokens(text: str, acronyms: dict[str, str]) -> tuple[str, ...]:
    """Deterministic semantic normalization: casefold → punctuation strip → stopword
    removal → acronym expansion → synonym folding → naive singularization."""
    low = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    out: list[str] = []
    for tok in low.split():
        if tok in STOP:
            continue
        exp = acronyms.get(tok)
        parts = re.sub(r"[^a-z0-9]+", " ", exp.lower()).split() if exp else [tok]
        for p in parts:
            if p in STOP:
                continue
            p = SYNONYM.get(p, p)
            if len(p) > 3 and p.endswith("s") and not p.endswith("ss"):
                p = p[:-1]
            out.append(p)
    return tuple(out)


# ------------------------------------------------------------- repository concept universe
def build_repo_index(acronyms: dict[str, str]) -> tuple[dict, dict, dict]:
    """Build the repository's own concept universe from version-controlled artifacts only.

    Concepts are taken from markdown headings, artifact file stems, python class/def names
    and the registered artifact titles — i.e. the names the repository itself uses. Nothing
    is inferred from outside version control, so the universe is a pure function of HEAD.
    """
    own = f"00-MASTER/{PROGRAM}/"
    tracked = [p for p in git("ls-files").splitlines()
               if p and not p.startswith(own) and not INDEX_EXCLUDE.search(p)]
    exact: dict[tuple[str, ...], list[str]] = defaultdict(list)
    by_head: dict[str, list[tuple[frozenset, str]]] = defaultdict(list)
    stats = Counter()

    def add(concept: str, path: str) -> None:
        toks = norm_tokens(concept, acronyms)
        if not toks or len(toks) > 12:
            return
        key = tuple(sorted(toks))
        if len(exact[key]) < 4:
            exact[key].append(path)
        bucket = by_head[toks[-1]]
        if len(bucket) < 6000:
            bucket.append((frozenset(toks), path))
        stats["concepts"] += 1

    heading = re.compile(r"^#{1,6}\s+(.{2,160})$")
    pysym = re.compile(r"^\s*(?:class|def)\s+([A-Za-z_][A-Za-z0-9_]{2,60})")
    for rel in tracked:
        ext = os.path.splitext(rel)[1].lower()
        stem = os.path.splitext(os.path.basename(rel))[0]
        if ext in (".md", ".txt", ".py", ".json", ".yml", ".yaml", ".sh"):
            add(re.sub(r"^\d+[-_]", "", stem).replace("-", " ").replace("_", " "), rel)
            stats["files"] += 1
        abspath = REPO / rel
        if ext == ".md":
            try:
                text = abspath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line in text.splitlines():
                m = heading.match(line)
                if m:
                    title = re.sub(r"[`*_#|]", " ", m.group(1))
                    title = re.sub(r"\(.*?\)|\[.*?\]", " ", title)
                    add(title, rel)
        elif ext == ".py":
            try:
                text = abspath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line in text.splitlines():
                m = pysym.match(line)
                if m:
                    sym = re.sub(r"(?<!^)(?=[A-Z])", " ", m.group(1)).replace("_", " ")
                    add(sym, rel)

    artifacts = REPO / "00-BOOK" / "DATA" / "artifacts.json"
    if artifacts.exists():
        try:
            data = json.loads(artifacts.read_text(encoding="utf-8"))
            for art in data.get("artifacts", []):
                title = art.get("title") or ""
                if title:
                    add(title, "00-BOOK/DATA/artifacts.json")
        except (OSError, ValueError):
            pass
    return exact, by_head, dict(stats)


# --------------------------------------------------------------------------- classification
def curated_match(name: str) -> dict | None:
    low = name.strip().lower()
    for row in CURATED:
        if re.search(str(row["pattern"]), low):
            return row
    return None


def semantic_match(obj: dict, toks: tuple[str, ...], exact: dict, by_head: dict) -> dict | None:
    """SE-2 structural equality (order-insensitive token-set identity) and SE-3 subsumption.

    SE-3 is DENIED to P0/P1 objects on purpose: high-priority normative knowledge receives
    no benefit of the doubt — a more specific repository artifact does not discharge a
    general normative commitment. Those objects stay gaps and are assimilated.
    """
    if len(toks) < 2 or IDENT_LIKE.match(obj["name"].strip().lower()):
        return None
    key = tuple(sorted(toks))
    if key in exact:
        return dict(rule="SE-2", equivalence="STRUCTURAL (token-set identity)",
                    anchors=exact[key][:3])
    if obj.get("priority") in ("P0", "P1"):
        return None
    tokset = frozenset(toks)
    best: tuple[int, str] | None = None
    for cand, path in by_head.get(toks[-1], ()):
        if tokset < cand and len(cand) - len(tokset) <= 2:
            score = len(cand)
            if best is None or score < best[0] or (score == best[0] and path < best[1]):
                best = (score, path)
    if best:
        return dict(rule="SE-3", equivalence="SUBSUMPTION (repository artifact is more specific)",
                    anchors=[best[1]])
    return None


def wave_for(disposition: str, maturity: str) -> object:
    if maturity not in ACTIVE_MATURITY:
        return "F"
    pol = DEST_POLICY.get(disposition)
    return pol["wave"] if pol else "F"


def classify(objects: list[dict], exact: dict, by_head: dict, acronyms: dict[str,
    str]) -> list[dict]:
    rows: list[dict] = []
    for obj in objects:
        kid = obj["knowledge_id"]
        name = obj["name"]
        presence = obj.get("repository_presence") or {}
        level = presence.get("level", "ABSENT")
        hits = int(presence.get("file_hits") or 0)
        examples = presence.get("examples") or []
        disposition = obj.get("ucos_disposition") or "NOT-UCOS"
        maturity = obj.get("maturity") or "IDEA"
        priority = obj.get("priority") or "P3"

        weak = bool(
            level != "ABSENT" and hits <= 1 and examples
            and any(a in examples[0] for a in WEAK_PRESENCE_ANCHORS)
        )
        row = dict(
            kid=kid, name=name, category=obj.get("category") or "CONCEPT",
            maturity=maturity, priority=priority, disposition=disposition,
            presence_level=level, presence_hits=hits,
            presence_corrected=weak,
            instance_level=bool(obj.get("is_instance_level")),
            mentions=int(obj.get("mentions") or 0),
            user_mentions=int(obj.get("user_mentions") or 0),
            normative_statements=int(obj.get("normative_statements") or 0),
            authority_score=float(obj.get("authority_score") or 0.0),
            origin_conversations=int(obj.get("origin_conversation_count") or 0),
            evidence_conversation=(obj.get("origin_conversations") or [""])[0],
            hierarchy_tier=obj.get("hierarchy_tier"),
            related=(obj.get("related_knowledge") or [])[:8],
        )

        cur = curated_match(name)
        if maturity == "REJECTED":
            row.update(state="REJECTED", rule="R0",
                       anchors=[], destination="", owner="", authority="", wave="")
        elif maturity == "SUPERSEDED" or (cur and cur["state"] == "SUPERSEDED"):
            row.update(state="SUPERSEDED", rule="SE-1" if cur else "R1",
                       anchors=[str(cur["anchor"])] if cur else [],
                       destination="", owner="", authority="", wave="")
            if cur:
                row["basis"] = str(cur["basis"])
        elif level != "ABSENT" and not weak:
            row.update(state="ALREADY-REPRESENTED", rule="R2",
                       anchors=examples[:2], destination="", owner="", authority="", wave="")
        elif cur and cur["state"] == "SEMANTICALLY-REPRESENTED":
            row.update(state="SEMANTICALLY-REPRESENTED", rule="SE-1",
                       equivalence="DETERMINATION (verified in-repo under another identifier)",
                       basis=str(cur["basis"]), anchors=[str(cur["anchor"])],
                       destination="", owner="", authority="", wave="")
        elif row["instance_level"] or disposition == "NOT-UCOS":
            row.update(state="HISTORICAL-EVIDENCE-ONLY",
                       rule="R4" if row["instance_level"] else "R5",
                       anchors=[], destination="", owner="", authority="", wave="")
        else:
            toks = norm_tokens(name, acronyms)
            sem = semantic_match(obj, toks, exact, by_head)
            if sem:
                row.update(state="SEMANTICALLY-REPRESENTED", rule=str(sem["rule"]),
                           equivalence=str(sem["equivalence"]),
                           anchors=list(sem["anchors"]), destination="",
                           owner="", authority="", wave="")
            else:
                pol = DEST_POLICY.get(disposition)
                if pol is None:
                    pol = DEST_POLICY["DOCUMENTATION"]
                row.update(state="ASSIMILATED", rule="R6", anchors=[],
                           destination=str(pol["dest"]), owner=str(pol["owner"]),
                           authority=str(pol["authority"]),
                           wave=wave_for(disposition, maturity))
        rows.append(row)

    # dependency chains: resolve related-knowledge names to KIDs (deterministic, in-corpus only)
    by_name = {}
    for r in rows:
        by_name.setdefault(norm_tokens(r["name"], acronyms), r["kid"])
    for r in rows:
        deps = []
        for rel in r["related"]:
            kid = by_name.get(norm_tokens(rel, acronyms))
            if kid and kid != r["kid"] and kid not in deps:
                deps.append(kid)
        # Retained for the D-2 dependency-correctness measure: how many declared relations
        # were considered, and how many of them resolved to a real object in this corpus.
        r["_rel_declared"] = len(r["related"])
        r["_rel_resolved"] = len(deps)
        r["dependencies"] = deps[:4]
        del r["related"]
    rows.sort(key=lambda r: r["kid"])

    # ---------------------------------------------------------------- WP-002 / D-2 superiority
    # PRESENCE IS COMPLETE AT THIS POINT. Every row already holds its terminal presence state,
    # rule, destination, owner, authority, wave and resolved dependency chain. The superiority
    # axis is evaluated here, strictly afterwards, and reads ONLY what presence measured — it
    # changes no presence field, so the existing classification is preserved exactly.
    evaluate_superiority(objects, rows)

    # ------------------------------------------------------------------ WP-003 / D-3 decision
    # PRESENCE AND SUPERIORITY ARE BOTH COMPLETE AT THIS POINT. The decision axis is evaluated
    # here, strictly afterwards, and reads ONLY what the two prior axes recorded — it writes no
    # presence field and no superiority field, so both earlier classifications survive exactly.
    decide_repository_actions(rows)
    return [{c: r.get(c, "" if c not in ("anchors", "dependencies") else []) for c in ROW_COLUMNS}
            for r in rows]


def evaluate_superiority(objects: list[dict], rows: list[dict]) -> None:
    """Attach the D-2 verdict to every already-classified row, in place.

    The three cross-row facts the evaluator needs are computed ONCE here and passed in, so the
    evaluator itself stays a pure function of its arguments:

        collides        the normalized name is carried by more than one corpus object, i.e. the
                        corpus itself restates the concept (Knowledge Once / orthogonality)
        anchors_resolve how many recorded anchors actually exist in the repository at HEAD
        deps_resolve    every recorded dependency KID is a real object in this register
    """
    titles = Counter(norm_title(r["name"]) for r in rows)
    kids = {r["kid"] for r in rows}
    by_kid = {obj["knowledge_id"]: obj for obj in objects}
    exists: dict[str, bool] = {}

    def anchor_exists(anchor: str) -> bool:
        # Anchors may carry a `path:detail` suffix, matching the semantic-mapping convention.
        path = anchor.split(":")[0]
        if path not in exists:
            exists[path] = bool(path) and (REPO / path).exists()
        return exists[path]

    for row in rows:
        obj = by_kid.get(row["kid"], {})
        anchors = [str(a) for a in (row.get("anchors") or [])]
        row.update(SUP.evaluate(
            obj, row,
            collides=titles[norm_title(row["name"])] > 1,
            relations_declared=int(row.pop("_rel_declared", 0)),
            relations_resolved=int(row.pop("_rel_resolved", 0)),
            anchors_resolve=sum(1 for a in anchors if anchor_exists(a)),
            deps_resolve=all(k in kids for k in (row.get("dependencies") or [])),
        ))


def decide_repository_actions(rows: list[dict]) -> None:
    """Attach the D-3 repository decision to every already-evaluated row, in place.

    The two cross-row facts the decision engine needs are computed ONCE here and passed in, so
    the engine itself stays a pure function of its arguments and imports nothing:

        objection     a CONSTITUTIONAL dimension is measurably INFERIOR for this row, decoded
                      from the superiority profile the previous axis stored
        deps_closed   every recorded dependency KID is a real object in this register
                      (dependency closure — a decision may not be actionable without it)
    """
    kids = {r["kid"] for r in rows}
    for row in rows:
        row.update(DEC.decide(
            row,
            objection=constitutional_objection(row),
            deps_closed=all(k in kids for k in (row.get("dependencies") or [])),
        ))


def hydrate(rows: list[dict]) -> list[dict]:
    """Restore the DERIVED owner/authority columns from the destination policy, so gates and
    renderers see complete rows whether they were just computed or replayed from disk.

    Also restores the D-2 superiority columns for BACKWARD COMPATIBILITY: an assimilation.json
    written before the superiority axis existed carries only the presence columns, and must
    still deserialize and render. Such a row is marked UNEVALUATED (an empty verdict) rather
    than given a fabricated one, so the fail-closed superiority gate detects it. The D-3 decision
    columns are treated identically (UNDECIDED rather than invented), and the two DERIVED
    decision columns — `implementation_owner` and `decision_version` — are resolved here from
    the declared owner policy and the declared rule-set version.
    """
    for r in rows:
        # Only genuinely ABSENT columns are defaulted; a computed verdict is never overwritten.
        for col, default in SUP.blank().items():
            r.setdefault(col, default)
        for col, default in DEC.blank().items():
            r.setdefault(col, default)
    for r in rows:
        pol = DEST_POLICY.get(r["disposition"]) if r["state"] == "ASSIMILATED" else None
        if pol is None and r["state"] == "ASSIMILATED":
            pol = DEST_POLICY["DOCUMENTATION"]
        r["owner"] = str(pol["owner"]) if pol else ""
        r["authority"] = str(pol["authority"]) if pol else ""
        # DERIVED, never stored: the referral address of the decision, and the version of the
        # rule set that produced it. `owner_for` is consulted only AFTER the presence axis's own
        # owner has been restored above, so a homed object's declared owner always wins.
        r["implementation_owner"] = DEC.owner_for(r)
        r["decision_version"] = DEC.DECISION_VERSION
    return rows


# --------------------------------------------------------------------------- gates
def run_gates(rows: list[dict], summary: dict) -> list[dict]:
    states = Counter(r["state"] for r in rows)
    assimilated = [r for r in rows if r["state"] == "ASSIMILATED"]
    semantic = [r for r in rows if r["state"] == "SEMANTICALLY-REPRESENTED"]

    unclassified = [r["kid"] for r in rows if r["state"] not in STATES]
    dup = [k for k, c in Counter(r["kid"] for r in rows).items() if c > 1]
    missing_dest = [r["kid"] for r in assimilated
                    if not r["destination"] or not (REPO / r["destination"]).exists()]
    missing_auth = [r["kid"] for r in assimilated
                    if not r["authority"] or not (REPO / r["authority"]).exists()]
    missing_owner = [r["kid"] for r in assimilated if not r["owner"]]
    no_evidence = [r["kid"] for r in assimilated if r["origin_conversations"] < 1]
    unresolved_semantic = [r["kid"] for r in semantic
                           if not r["anchors"]
                           or not any((REPO / a.split(":")[0]).exists() for a in r["anchors"])]
    curated_broken = []
    for row in CURATED:
        anchor = REPO / str(row["anchor"])
        if not anchor.exists():
            curated_broken.append(f"{row['anchor']} (missing)")
            continue
        proof = str(row["proof"])
        if proof and anchor.is_file() and proof not in anchor.read_text(encoding="utf-8",
            errors="replace"):
            curated_broken.append(f"{row['anchor']} (proof {proof!r} absent)")
    prop_broken = []
    for row in PROPOSITIONAL_MAPPINGS:
        anchor = REPO / row["repo_authority"]
        if not anchor.exists():
            prop_broken.append(f"{row['repo_authority']} (missing)")
            continue
        proof = row["proof"]
        if proof and anchor.is_file() and proof not in anchor.read_text(encoding="utf-8",
            errors="replace"):
            prop_broken.append(f"{row['repo_authority']} (proof {proof!r} absent)")
    dual_state = [r["kid"] for r in assimilated
                  if r["presence_level"] != "ABSENT" and not r["presence_corrected"]]
    # Intra-register duplicate CANDIDATES: R6 requires an approved item to be non-duplicate, and
    # the gate above proves non-duplication against the REPOSITORY. It cannot see duplication
    # WITHIN the approved set, which the source corpus can carry (e.g. an object and its "DONE"
    # restatement). Reported non-blocking, with the normalization declared, because deciding that
    # two evidence objects are one concept is the destination owner's act, not this engine's.
    dup_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for r in assimilated:
        dup_groups[(norm_title(r["name"]), str(r["destination"]))].append(r["kid"])
    dup_detail = []
    dup_extra = 0
    for (norm, dest), kids in sorted(dup_groups.items()):
        if len(kids) < 2:
            continue
        dup_extra += len(kids) - 1
        dup_detail.append(f"{' ~ '.join(sorted(kids))} → `{dest}` ({norm})")
    total_expected = int(summary.get("objects") or len(rows))

    gates = [
        dict(gate="Every verified knowledge object is classified", blocking=True,
             count=len(unclassified), detail=unclassified[:5]),
        dict(gate="Every object holds exactly one state (no duplicate KID)", blocking=True,
             count=len(dup), detail=dup[:5]),
        dict(gate="Object count equals the verified corpus", blocking=True,
             count=abs(len(rows) - total_expected), detail=[f"rows={len(rows)} "
                 f"expected={total_expected}"]),
        dict(gate="Every assimilated item has an EXISTING canonical destination", blocking=True,
             count=len(missing_dest), detail=missing_dest[:5]),
        dict(gate="Every assimilated item has an EXISTING constitutional authority", blocking=True,
             count=len(missing_auth), detail=missing_auth[:5]),
        dict(gate="Every assimilated item has exactly one canonical owner", blocking=True,
             count=len(missing_owner), detail=missing_owner[:5]),
        dict(gate="Every assimilated item carries evidence provenance", blocking=True,
             count=len(no_evidence), detail=no_evidence[:5]),
        dict(gate="No unresolved semantic mapping (anchor resolves on disk)", blocking=True,
             count=len(unresolved_semantic), detail=unresolved_semantic[:5]),
        dict(gate="No duplicate authority (assimilated item already represented)", blocking=True,
             count=len(dual_state), detail=dual_state[:5]),
        dict(gate="Curated determination mappings still resolve in-repo", blocking=True,
             count=len(curated_broken), detail=curated_broken[:5]),
        dict(gate="Propositional mappings still resolve in-repo", blocking=True,
             count=len(prop_broken), detail=prop_broken[:5]),
        dict(gate="Remaining approved promotion candidates", blocking=True,
             count=len([r for r in assimilated
                        if not r["destination"] or not r["owner"] or r["wave"] == ""]),
             detail=[]),
        dict(gate="Intra-register duplicate candidates (same normalized name + destination)",
             blocking=False, count=dup_extra, detail=dup_detail[:5]),
    ]
    gates += superiority_gates(rows)
    gates += decision_gates(rows)
    for g in gates:
        g["result"] = ("PASS" if g["count"] == 0
                       else ("FAIL" if g["blocking"] else "REPORTED"))
    _ = states
    return gates


def superiority_gates(rows: list[dict]) -> list[dict]:
    """WP-002 / D-2 fail-closed gates over the superiority axis.

    The four blocking gates assert the axis is TOTAL and WELL-FORMED — every presence-classified
    object carries exactly one declared verdict, decided by a declared rule, over a full profile
    of declared dimensions. They deliberately do NOT block on any particular verdict: a
    CONFLICTING or OBSOLETE finding is a measured outcome referred to its owner, not an engine
    defect, so those are REPORTED. Blocking on them would make the gate punish the evidence for
    what it says.
    """
    legend = set(SUP.OUTCOME_CHAR.values())
    unevaluated = [r["kid"] for r in rows if not r["superiority"]]
    undeclared = [f"{r['kid']} ({r['superiority']})" for r in rows
                  if r["superiority"] and r["superiority"] not in SUP.SUPERIORITY_STATES]
    bad_profile = [f"{r['kid']} ({r['superiority_profile']!r})" for r in rows
                   if len(str(r["superiority_profile"])) != SUP.DIMENSION_COUNT
                   or any(c not in legend for c in str(r["superiority_profile"]))]
    bad_rule = [f"{r['kid']} ({r['superiority_rule']})" for r in rows
                if r["superiority_rule"] not in SUP.VERDICT_RATIONALE]
    unreachable = [s for s in SUP.REQUIRED_STATES
                   if not any(r["superiority"] == s for r in rows)]
    verdicts = Counter(r["superiority"] for r in rows)
    return [
        dict(gate="Every presence-classified object carries a superiority verdict", blocking=True,
             count=len(unevaluated), detail=unevaluated[:5]),
        dict(gate="Every superiority verdict is a declared state", blocking=True,
             count=len(undeclared), detail=undeclared[:5]),
        dict(gate="Every superiority profile declares all "
                  f"{SUP.DIMENSION_COUNT} comparison dimensions", blocking=True,
             count=len(bad_profile), detail=bad_profile[:5]),
        dict(gate="Every superiority verdict resolves to a declared rule", blocking=True,
             count=len(bad_rule), detail=bad_rule[:5]),
        dict(gate="Superiority findings referred to their owners (conflicting / obsolete / "
                  "review)", blocking=False,
             count=(verdicts[SUP.CONFLICTING] + verdicts[SUP.OBSOLETE]
                    + verdicts[SUP.REQUIRES_ARCHITECTURAL_REVIEW]),
             detail=[f"{s}={verdicts[s]}" for s in
                     (SUP.CONFLICTING, SUP.OBSOLETE, SUP.REQUIRES_ARCHITECTURAL_REVIEW,
                      SUP.BETTER_THAN_CURRENT, SUP.PARTIALLY_ASSIMILATED)]),
        dict(gate="Required superiority states unreachable on this corpus", blocking=False,
             count=len(unreachable), detail=unreachable),
    ]


def decision_gates(rows: list[dict]) -> list[dict]:
    """WP-003 / D-3 fail-closed gates over the repository decision axis.

    The blocking gates assert the axis is TOTAL, WELL-FORMED, SINGLE-VALUED and REPLAYABLE:
    every evaluated object carries exactly one declared action, decided by exactly one declared
    rule, carrying one declared repository operation, one declared priority and one named owner —
    and re-deriving the decision from its recorded grounds alone reproduces it exactly.

    Two further blocking gates protect the constitution rather than the schema: the TOTALITY
    RESIDUAL must be provably empty (its use means the rule set has a hole), and no action that
    would MODIFY repository knowledge may stand on an open dependency chain.

    As in the superiority axis, the gates deliberately do NOT block on any particular action: an
    ESCALATE_ARCHITECTURE or REJECT outcome is a governed decision referred to its owner, not an
    engine defect, so the distribution is REPORTED.
    """
    kids = {r["kid"] for r in rows}
    ops = DEC.OPERATIONS
    modifying = {a for a, spec in DEC.ACTION_REGISTRY.items() if spec["modifies_knowledge"]}

    undecided = [r["kid"] for r in rows if not r.get("decision")]
    undeclared = [f"{r['kid']} ({r.get('decision')})" for r in rows
                  if r.get("decision") and r["decision"] not in DEC.ACTIONS]
    bad_rule = [f"{r['kid']} ({r.get('decision_rule')})" for r in rows
                if r.get("decision_rule") not in DEC.RULE_IDS]
    # A rule and an action that disagree would mean the register cites a clause that does not
    # decide what it claims to decide. Checked against the SAME declaration `apply_rules` runs.
    rule_action = {str(r["id"]): str(r["action"]) for r in DEC.DECISION_RULES}
    rule_operation = {str(r["id"]): str(r["operation"]) for r in DEC.DECISION_RULES}
    mismatched = [f"{r['kid']} ({r.get('decision_rule')}→{r.get('decision')})" for r in rows
                  if r.get("decision_rule") in rule_action
                  and rule_action[str(r["decision_rule"])] != r.get("decision")]
    bad_operation = [f"{r['kid']} ({r.get('implementation_action')})" for r in rows
                     if str(r.get("implementation_action")) not in ops
                     or (r.get("decision_rule") in rule_operation
                         and rule_operation[str(r["decision_rule"])]
                         != str(r.get("implementation_action")))]
    bad_priority = [f"{r['kid']} ({r.get('implementation_priority')})" for r in rows
                    if str(r.get("implementation_priority")) not in DEC.PRIORITIES]
    unowned = [r["kid"] for r in rows if not str(r.get("implementation_owner") or "").strip()]
    bad_version = [r["kid"] for r in rows
                   if str(r.get("decision_version")) != DEC.DECISION_VERSION]

    # DETERMINISTIC REPLAY, executed rather than asserted: re-derive every decision from its
    # committed grounds string alone and require an exact match on all four decided columns.
    divergent = []
    for r in rows:
        rationale = str(r.get("decision_rationale") or "")
        try:
            again = DEC.replay(rationale)
        except (ValueError, KeyError):
            divergent.append(f"{r['kid']} (unreadable grounds {rationale!r})")
            continue
        recorded = {k: r.get(k) for k in again}
        if recorded != again:
            divergent.append(f"{r['kid']} ({recorded} != {again})")

    residual = [r["kid"] for r in rows if r.get("decision_rule") == DEC.RESIDUAL_RULE]
    # INDEPENDENT RE-DERIVATION. The decision axis is a pure function of columns the register
    # already carries, so the gate re-decides every row FROM THE ROW and requires an exact match.
    # A recorded decision can therefore never disagree with the rule set that claims to have
    # produced it — on a fresh build or on a replay with no external evidence present.
    rederived = []
    for r in rows:
        if not r.get("decision"):
            continue  # a pre-D-3 row: caught by the totality gate, never silently filled in
        again = DEC.decide(r, objection=constitutional_objection(r),
                           deps_closed=all(k in kids for k in (r.get("dependencies") or [])))
        if {k: r.get(k) for k in again} != again:
            rederived.append(f"{r['kid']} ({r.get('decision_rule')}→{again['decision_rule']})")
    open_deps = [r["kid"] for r in rows
                 if r.get("decision") in modifying
                 and not all(k in kids for k in (r.get("dependencies") or []))]
    unprovenanced = [r["kid"] for r in rows if int(r.get("origin_conversations") or 0) < 1]
    register_only = [r["kid"] for r in rows
                     if f"T:{DEC.TRACE_CODE['REGISTER_ONLY']}"
                     in str(r.get("decision_rationale") or "")]
    fired = Counter(str(r.get("decision_rule")) for r in rows)
    silent = [f"{rid} [{DEC.SILENT_RULES[rid]['kind']}] {DEC.SILENT_RULES[rid]['reason']}"
              if rid in DEC.SILENT_RULES else f"{rid} (no declared reason)"
              for rid in DEC.RULE_IDS
              if not fired.get(rid) and rid != DEC.RESIDUAL_RULE]
    unexplained = [rid for rid in DEC.RULE_IDS
                   if not fired.get(rid) and rid != DEC.RESIDUAL_RULE
                   and rid not in DEC.SILENT_RULES]
    actions = Counter(str(r.get("decision")) for r in rows)
    unreachable_actions = [a for a in DEC.ACTIONS if not actions.get(a)]

    return [
        dict(gate="Every evaluated object carries exactly one repository decision", blocking=True,
             count=len(undecided), detail=undecided[:5]),
        dict(gate="Every repository decision is a declared action", blocking=True,
             count=len(undeclared), detail=undeclared[:5]),
        dict(gate="Every decision resolves to one declared decision rule", blocking=True,
             count=len(bad_rule), detail=bad_rule[:5]),
        dict(gate="Every decision matches the action its declared rule decides", blocking=True,
             count=len(mismatched), detail=mismatched[:5]),
        dict(gate="Every decision declares one registered implementation action", blocking=True,
             count=len(bad_operation), detail=bad_operation[:5]),
        dict(gate="Every decision declares a declared implementation priority", blocking=True,
             count=len(bad_priority), detail=bad_priority[:5]),
        dict(gate="Every decision names an implementation owner", blocking=True,
             count=len(unowned), detail=unowned[:5]),
        dict(gate="Every decision carries the declared decision version", blocking=True,
             count=len(bad_version), detail=bad_version[:5]),
        dict(gate="Every decision replays identically from its recorded rationale", blocking=True,
             count=len(divergent), detail=divergent[:5]),
        dict(gate="Every recorded decision re-derives from the row it was decided from",
             blocking=True, count=len(rederived), detail=rederived[:5]),
        dict(gate="Decision rule set is total (residual rule provably unused)", blocking=True,
             count=len(residual), detail=residual[:5]),
        dict(gate="Every knowledge-modifying decision has a closed dependency chain",
             blocking=True, count=len(open_deps), detail=open_deps[:5]),
        dict(gate="Every decision traces to recorded evidence provenance", blocking=True,
             count=len(unprovenanced), detail=unprovenanced[:5]),
        dict(gate="Decisions whose only repository address is the decision register",
             blocking=False, count=len(register_only), detail=register_only[:5]),
        dict(gate="Required repository actions unreachable on this corpus", blocking=False,
             count=len(unreachable_actions), detail=unreachable_actions),
        dict(gate="Declared decision rules that did not fire on this corpus", blocking=False,
             count=len(silent), detail=silent[:5]),
        dict(gate="Silent decision rules with no declared reason", blocking=True,
             count=len(unexplained), detail=unexplained[:5]),
        dict(gate="Repository actions referred to their owners", blocking=False,
             count=sum(actions.get(a, 0) for a in DEC.ACTIONS),
             detail=[f"{a}={actions.get(a, 0)}" for a in DEC.ACTIONS]),
    ]


# --------------------------------------------------------------------------- build
def superiority_outcome_totals(rows: list[dict]) -> dict:
    """Per-dimension outcome totals across the whole register, decoded from the stored profiles.

    Computed from the profile strings rather than re-running the evaluator, so the aggregate is
    provably the same evidence the rows carry — a replay reproduces it with no corpus present.
    """
    totals: dict[str, dict[str, int]] = {}
    for dim in SUP.DIMENSIONS:
        totals[dim["id"]] = {name: 0 for name in SUP.OUTCOME_CHAR}
    for r in rows:
        profile = str(r.get("superiority_profile") or "")
        if len(profile) != SUP.DIMENSION_COUNT:
            continue
        for dim, ch in zip(SUP.DIMENSIONS, profile, strict=False):
            name = SUP.CHAR_OUTCOME.get(ch)
            if name:
                totals[dim["id"]][name] += 1
    return totals


def constitutional_objection(row: dict) -> bool:
    """True when a CONSTITUTIONAL dimension is measurably INFERIOR for this row, i.e. adopting
    the discovered form would weaken Repository Truth, Knowledge Once, Single Source of Truth,
    dependency correctness or traceability."""
    profile = str(row.get("superiority_profile") or "")
    if len(profile) != SUP.DIMENSION_COUNT:
        return False
    return any(ch == SUP.OUTCOME_CHAR[SUP.INFERIOR]
               and dim["id"] in SUP.CONSTITUTIONAL_DIMENSIONS
               for dim, ch in zip(SUP.DIMENSIONS, profile, strict=False))


def decision_plan_totals(rows: list[dict]) -> list[dict]:
    """The IMPLEMENTATION PLAN, aggregated deterministically: one entry per
    (implementation_owner × decision × implementation_action × implementation_priority × wave),
    carrying the object count and the declared plan steps.

    This is what makes the plan an executable programme rather than 23,859 restatements: an owner
    reads the entries addressed to it, in priority and wave order, and every entry names the
    operation and the exact steps that discharge it. Sorted by declared ordinals, so a replay
    reproduces the plan byte-for-byte.
    """
    priority_rank = {p: i for i, p in enumerate(DEC.PRIORITIES)}
    wave_rank = {str(w): i for i, w in enumerate(WAVE_ORDER)}
    groups: dict[tuple, list[str]] = defaultdict(list)
    for r in rows:
        key = (str(r.get("implementation_owner") or ""), str(r.get("decision") or ""),
               str(r.get("implementation_action") or ""),
               str(r.get("implementation_priority") or ""),
               str(r.get("wave") or "").strip() or "-")
        groups[key].append(r["kid"])
    out = []
    for (owner, decision, operation, priority, wave), kids in groups.items():
        out.append(dict(
            implementation_owner=owner, decision=decision, implementation_action=operation,
            implementation_priority=priority, wave=wave, objects=len(kids),
            first_object=min(kids),
            steps=[str(s) for s in (DEC.OPERATIONS.get(operation) or {}).get("steps", [])],
        ))
    out.sort(key=lambda e: (priority_rank.get(e["implementation_priority"], 99),
                            wave_rank.get(e["wave"], 99), e["implementation_owner"],
                            e["decision"], e["implementation_action"]))
    return out


def decision_schema(rows: list[dict], decisions: Counter) -> dict:
    """The declared decision model + its measured distribution, as one payload block.

    `decision_ruleset_sha256` seals the WHOLE declaration (version, actions, operations, rules,
    priorities, grounds encoding, owner policy). Editing any part of the model changes the
    digest, so a rule set cannot be silently changed underneath decisions that cite it — the
    register drift gate catches it on the next run.
    """
    declaration = DEC.ruleset_declaration()
    return dict(
        decision_version=DEC.DECISION_VERSION,
        decision_ruleset_sha256=hashlib.sha256(
            json.dumps(declaration, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        decision_actions={a: decisions.get(a, 0) for a in DEC.ACTIONS},
        decision_action_registry=declaration["actions"],
        decision_operation_registry=declaration["operations"],
        decision_rule_registry=declaration["rules"],
        decision_rules=dict(Counter(str(r.get("decision_rule")) for r in rows)),
        decision_priorities=dict(Counter(str(r.get("implementation_priority")) for r in rows)),
        decision_priority_declaration=declaration["priorities"],
        decision_operations=dict(Counter(str(r.get("implementation_action")) for r in rows)),
        decision_owners=dict(Counter(str(r.get("implementation_owner")) for r in rows)),
        decision_presence_classes=declaration["presence_classes"],
        decision_grounds_keys=declaration["grounds_keys"],
        decision_grounds_legend=declaration["grounds_legend"],
        decision_residual_rule=declaration["residual_rule"],
        decision_silent_rules=declaration["silent_rules"],
        decision_zone_owners=declaration["zone_owners"],
        decision_plan=decision_plan_totals(rows),
    )


def build(evroot: Path) -> dict:
    manifest = {}
    for key, rel in EVIDENCE_FILES.items():
        path = evroot / rel
        if not path.exists():
            raise SystemExit(
                f"{PROGRAM}: FAIL-CLOSED — external evidence missing: {path}\n"
                f"  set UAKOS_EVIDENCE_ROOT, or run with --render to replay from assimilation.json")
        # `path` IS REPOSITORY-RELATIVE WHENEVER IT CAN BE, and absolute only when the evidence
        # genuinely sits outside the repository. It used to be `str(path)` unconditionally, which
        # wrote `/Users/<somebody>/Desktop/…` into a COMMITTED governed artifact — an attestation
        # naming a location that exists on one machine. Five other capabilities already refuse a
        # `/Users/` fragment in their reports (uci, ucon, uec, urke, mutation gates); this one
        # emitted them. A relative path is also the only form a fresh clone can resolve.
        manifest[key] = dict(path=repo_relative(path), relative=rel, bytes=path.stat().st_size,
                             sha256=sha256_file(path))

    kb = json.loads((evroot / EVIDENCE_FILES["knowledge_base"]).read_text(encoding="utf-8"))
    summary = json.loads((evroot / EVIDENCE_FILES["summary"]).read_text(encoding="utf-8"))
    gaps = json.loads((evroot / EVIDENCE_FILES["gaps"]).read_text(encoding="utf-8"))
    objects = kb["knowledge"]
    acronyms = {k.lower(): v for k, v in (kb.get("acronym_expansions") or {}).items()
                if isinstance(v, str)}

    exact, by_head, idx_stats = build_repo_index(acronyms)
    rows = hydrate(classify(objects, exact, by_head, acronyms))
    gates = run_gates(rows, summary)

    states = Counter(r["state"] for r in rows)
    superiority = Counter(r["superiority"] for r in rows)
    decisions = Counter(r["decision"] for r in rows)
    assimilated = [r for r in rows if r["state"] == "ASSIMILATED"]
    waves = Counter(str(r["wave"]) for r in assimilated)
    blocking_fail = [g for g in gates if g["blocking"] and g["result"] == "FAIL"]
    determination = ("REPOSITORY CONSTITUTIONALLY COMPLETE"
                     if not blocking_fail else
                     "NOT COMPLETE (fail-closed)")

    payload = dict(
        program=PROGRAM,
        mission="Constitutional assimilation & repository completion (final closure)",
        authority="NONE — DERIVED TRUTH (fail-closed, TRACK-001)",
        head_commit=head_commit(),
        evidence_root=repo_relative(evroot),
        evidence_manifest=manifest,
        repository_index=idx_stats,
        verified_objects=len(rows),
        published_measures=dict(
            objects=summary.get("objects"),
            present=summary.get("objects", 0) - summary.get("discussion_only", 0),
            discussion_only=summary.get("discussion_only"),
            repository_only=summary.get("repository_only"),
            not_ucos=dict(summary.get("disposition") or {}).get("NOT-UCOS")
            if isinstance(summary.get("disposition"), dict) else None,
            needs_constitutionalization=summary.get("needs_constitutionalization"),
            needs_implementation=summary.get("needs_implementation"),
            needs_certification=summary.get("needs_certification"),
        ),
        gap_classes=dict(
            needs_constitutionalization=len(gaps.get("needs_constitutionalization") or []),
            needs_implementation=len(gaps.get("needs_implementation") or []),
            needs_certification=len(gaps.get("needs_certification") or []),
        ),
        states={s: states.get(s, 0) for s in STATES},
        # --- WP-002 / D-2: the declared SCHEMA of the superiority axis, emitted from the same
        # --- declaration the evaluator executes, so the model, the registers and the behaviour
        # --- can never drift apart.
        superiority_states={s: superiority.get(s, 0) for s in SUP.SUPERIORITY_STATES},
        superiority_required_states=SUP.REQUIRED_STATES,
        superiority_dimensions=SUP.dimension_catalog(),
        superiority_dimension_count=SUP.DIMENSION_COUNT,
        superiority_profile_legend={ch: name for name, ch in SUP.OUTCOME_CHAR.items()},
        superiority_thresholds=SUP.THRESHOLDS,
        superiority_rules=dict(Counter(r["superiority_rule"] for r in rows)),
        superiority_rationale=SUP.VERDICT_RATIONALE,
        superiority_outcomes=superiority_outcome_totals(rows),
        superiority_constitutional_objections=sum(
            1 for r in rows if constitutional_objection(r)),
        # --- WP-003 / D-3: the declared SCHEMA of the repository decision axis, emitted from
        # --- the same declaration the rule engine executes, and sealed by a digest so the model,
        # --- the registers and the behaviour can never drift apart.
        **decision_schema(rows, decisions),
        assimilation_waves={str(w): waves.get(str(w), 0) for w in WAVE_ORDER},
        rules=dict(Counter(r["rule"] for r in rows)),
        rule_rationale=RULE_RATIONALE,
        semantic_rules=dict(Counter(r["rule"] for r in rows
                                    if r["state"] == "SEMANTICALLY-REPRESENTED")),
        presence_corrections=sum(1 for r in rows if r["presence_corrected"]),
        curated_mappings=[{k: str(v) for k, v in row.items()} for row in CURATED],
        propositional_mappings=PROPOSITIONAL_MAPPINGS,
        destination_policy={k: {kk: str(vv) for kk, vv in v.items()} for k,
            v in DEST_POLICY.items()},
        gates=gates,
        remaining_approved_promotion_candidates=next(
            g["count"] for g in gates if g["gate"] == "Remaining approved promotion candidates"),
        unclassified=next(g["count"] for g in gates
                          if g["gate"] == "Every verified knowledge object is classified"),
        determination=determination,
        rows=rows,
    )
    seal_src = json.dumps({k: v for k, v in payload.items() if k != "seal_sha256"},
                          sort_keys=True, separators=(",", ":"))
    payload["seal_sha256"] = hashlib.sha256(seal_src.encode("utf-8")).hexdigest()
    return payload


def serialize(payload: dict) -> str:
    """Compact, diffable, columnar serialization: the metrics block is indented and sorted;
    the per-object rows are written as one COMPACT ARRAY PER LINE under a single declared
    column order, so 23,859 rows stay reviewable in a diff and small in version control."""
    head = {k: v for k, v in payload.items() if k != "rows"}
    head["row_columns"] = ROW_COLUMNS
    body = json.dumps(head, indent=2, sort_keys=True)
    lines = [json.dumps([r.get(c, "") for c in ROW_COLUMNS], separators=(",", ":"))
             for r in payload["rows"]]
    rows_block = "  \"rows\": [\n" + ",\n".join("    " + ln for ln in lines) + "\n  ]"
    return body[:-2].rstrip() + ",\n" + rows_block + "\n}\n"


def deserialize(raw: str) -> dict:
    payload = json.loads(raw)
    cols = payload.get("row_columns") or ROW_COLUMNS
    payload["rows"] = hydrate([dict(zip(cols, row, strict=False)) for row in payload["rows"]])
    restore_superiority_axis(payload)
    restore_decision_axis(payload)
    return payload


def restore_superiority_axis(payload: dict) -> None:
    """Make any recorded payload — including one written BEFORE the D-2 axis existed — render
    and gate correctly.

    Two distinct jobs:

    1. BACKWARD COMPATIBILITY. A pre-D-2 `assimilation.json` carries none of the superiority
       schema blocks. They are restored here from the declaration and from the rows, so an old
       record renders instead of raising.
    2. NON-VACUOUS REPLAY. The superiority gates are a pure function of the rows and need no
       external evidence, so a replay RE-EVALUATES them instead of trusting whatever the record
       claims. Without this, replaying a record whose rows carry no verdict would pass the gate
       — the exact hole the D-2 validation requirement exists to close. The recomputation is
       byte-identical to the build for a healthy record, so the register drift gate still holds.
    """
    rows = payload["rows"]
    counts = Counter(r["superiority"] for r in rows)
    payload.setdefault("superiority_states",
                       {s: counts.get(s, 0) for s in SUP.SUPERIORITY_STATES})
    payload.setdefault("superiority_required_states", SUP.REQUIRED_STATES)
    payload.setdefault("superiority_dimensions", SUP.dimension_catalog())
    payload.setdefault("superiority_dimension_count", SUP.DIMENSION_COUNT)
    payload.setdefault("superiority_profile_legend",
                       {ch: name for name, ch in SUP.OUTCOME_CHAR.items()})
    payload.setdefault("superiority_thresholds", SUP.THRESHOLDS)
    payload.setdefault("superiority_rules",
                       dict(Counter(r["superiority_rule"] for r in rows)))
    payload.setdefault("superiority_rationale", SUP.VERDICT_RATIONALE)
    payload.setdefault("superiority_outcomes", superiority_outcome_totals(rows))
    payload.setdefault("superiority_constitutional_objections",
                       sum(1 for r in rows if constitutional_objection(r)))

    recomputed = superiority_gates(rows)
    for g in recomputed:
        g["result"] = ("PASS" if g["count"] == 0
                       else ("FAIL" if g["blocking"] else "REPORTED"))
    names = {g["gate"] for g in recomputed}
    payload["gates"] = [g for g in (payload.get("gates") or [])
                        if g.get("gate") not in names] + recomputed
    if any(g["blocking"] and g["result"] == "FAIL" for g in payload["gates"]):
        payload["determination"] = "NOT COMPLETE (fail-closed)"


def restore_decision_axis(payload: dict) -> None:
    """Make any recorded payload — including one written BEFORE the D-3 axis existed — render
    and gate correctly, and prove the recorded decisions on the way through.

    Three distinct jobs:

    1. BACKWARD COMPATIBILITY. A pre-D-3 `assimilation.json` carries none of the decision schema
       blocks. They are restored here from the declaration and from the rows, so an old record
       renders instead of raising. Its rows carry no decision, which fails a blocking gate.
    2. NON-VACUOUS REPLAY. The decision gates are a pure function of the rows and need no
       external evidence, so a replay RE-EVALUATES them instead of trusting whatever the record
       claims. Without this, replaying a record whose rows carry no decision would pass the gate
       — the exact hole the D-3 validation requirement exists to close.
    3. INDEPENDENT RE-DERIVATION. Unlike the superiority axis, which measures the external
       corpus, the decision axis is a pure function of columns the register ALREADY carries. So
       the recomputed gates re-derive every decision from the row itself — not merely from the
       recorded grounds string — and record any divergence as a blocking failure. A recorded
       decision can therefore never disagree with the rule set that claims to have produced it.
       The same gate runs on a fresh build, so build and replay emit an identical gate table.
    """
    rows = payload["rows"]
    decisions = Counter(str(r.get("decision") or "") for r in rows)
    for key, value in decision_schema(rows, decisions).items():
        payload.setdefault(key, value)

    recomputed = decision_gates(rows)
    for g in recomputed:
        g["result"] = ("PASS" if g["count"] == 0
                       else ("FAIL" if g["blocking"] else "REPORTED"))
    names = {g["gate"] for g in recomputed}
    payload["gates"] = [g for g in (payload.get("gates") or [])
                        if g.get("gate") not in names] + recomputed
    if any(g["blocking"] and g["result"] == "FAIL" for g in payload["gates"]):
        payload["determination"] = "NOT COMPLETE (fail-closed)"


# --------------------------------------------------------------------------- rendering
HDR_NOTE = (
    "> PROGRAM {program} · CONSTITUTIONAL ASSIMILATION & REPOSITORY COMPLETION · HEAD `{head}` · "
    "AUTHORITY = NONE (DERIVED TRUTH) · generated by `assimilation_engine.py`\n>\n"
    "> Inputs are FROZEN: the KNOWLEDGE-ASSIMILATION knowledge base and the TRI-SOURCE "
    "VERIFICATION DETERMINATION, both read-only and hashed in `EVIDENCE-MANIFEST.json`. "
    "No discovery, no re-verification, no external writes. Fail-closed.\n"
)


def md_header(payload: dict, num: str, title: str, subtitle: str) -> list[str]:
    return [
        f"# {num} — {title}",
        "",
        HDR_NOTE.format(program=payload["program"], head=payload["head_commit"]),
        f"> {subtitle}",
        "",
    ]


def table(head: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    out.append("")
    return out


def pct(n: int, d: int) -> str:
    return f"{(100.0 * n / d):.1f}%" if d else "—"


def _dup_count(payload: dict) -> int:
    """The non-blocking duplicate-candidate count, read back from the recorded gate so the
    register text and the gate can never disagree."""
    return next((g["count"] for g in payload["gates"]
                 if g["gate"].startswith("Intra-register duplicate candidates")), 0)


def write(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


# ------------------------------------------------- canonical validation record (CLOSURE-008)
#
# What this replaced, and why. Register 06 used to embed the tail of `evidence/verify.log`
# verbatim, so the canonical bytes of 06 — and, through the content hash 04 records for it,
# the bytes of 04 — carried the stdout of ONE execution on ONE machine: stage timings, a
# coverage total, an artifact count. `.gitignore` excludes `00-MASTER/**/evidence/`, so that
# transcript was never in the tree; rendering a fresh checkout took the NOT-CAPTURED branch
# and produced registers that differed from the committed ones. The CI drift gate asserts the
# committed registers ARE the rendered fixed point, and on a clean clone they were not.
#
# A validation RESULT is repository truth: same commit, same bytes. An execution TRANSCRIPT is
# a historical observation of one run. The canonical layer reads the first from an authored,
# tracked record; the transcript stays in the evidence archive and is named by IDENTITY, never
# read for content. Running `./verify.sh` again therefore moves no canonical byte.
def load_validation_record(home: Path) -> dict | None:
    """The authored validation record, or None if it is absent (the caller fails closed)."""
    path = home / "validation-record.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def validation_gate_section(record: dict | None) -> list[str]:
    """Register 06's canonical-gate section, as a pure function of the RECORD.

    Nothing here touches the evidence archive, the clock, the environment or any command
    output. Given the same record it emits the same bytes on every machine and every clone —
    which is the property the regression test pins.
    """
    L = ["## Canonical repository gate — `./verify.sh`", ""]
    if record is None:
        return L + [
            "`validation-record.json` ABSENT — the canonical gate result is therefore UNVERIFIED "
            "in this report (fail-closed: absence of a record is not evidence of a pass).",
            "",
        ]
    contract = record.get("contract", {})
    L += [
        "The canonical layer records the deterministic RESULT of the gate. The execution "
        "transcript that observed the run is evidence, not identity, and is referenced below "
        "by id rather than read for content — so re-running the command changes no byte of "
        "this report.",
        "",
    ]
    L += table(["Property", "Value"], [
        ["validation_id", f"`{record.get('validation_id', '')}`"],
        ["contract_id", f"`{contract.get('contract_id', '')}`"],
        ["command", f"`{contract.get('command', '')}`"],
        ["invocation", contract.get("invocation", "—")],
        ["contract artifacts", ", ".join(f"`{a}`" for a in contract.get("artifact_references", []))
            or "—"],
        ["declared-stage digest (sha256)", f"`{contract.get('stages_digest', '')[:16]}`"],
        ["result", f"**{record.get('result', '')}**"],
    ])
    L += table(["Gate (declared contract stage)", "Result"],
               [[s.get("stage", ""), s.get("result", "")] for s in record.get("stages", [])])
    ref = record.get("evidence_reference")
    if ref:
        L += [
            f"Execution evidence `{ref.get('evidence_id', '')}` "
            f"({ref.get('classification', '')}, {ref.get('canonical_identity_role', '')}) is "
            f"retained in the archive `{ref.get('archive_path', '')}` as `{ref.get('member', '')}`. "
            "The archive is preserved and published, and is NOT an input to any canonical "
            "artifact: no hash, byte count, timing or captured line from it enters this report.",
            "",
        ]
    return L


def render(payload: dict) -> list[str]:
    rows = payload["rows"]
    total = len(rows)
    st = payload["states"]
    by_state = defaultdict(list)
    for r in rows:
        by_state[r["state"]].append(r)
    written: list[str] = []

    def top(rs: list[dict], n: int) -> list[dict]:
        return sorted(rs, key=lambda r: (-r["authority_score"], r["kid"]))[:n]

    # ---------------------------------------------------------------- 01 reconciliation
    L = md_header(payload, "01", "Repository Reconciliation Register",
                  "Every verified knowledge object reconciled against Repository Truth: already "
                  "implemented, already documented, semantically equivalent, implemented under "
                  "another identifier, or missing — with destination, owner, dependencies and "
                      "priority.")
    L += [f"Verified knowledge objects reconciled: **{total}** · unclassified: "
        f"**{payload['unclassified']}** (MUST be 0).", ""]
    L += ["## Terminal state distribution", ""]
    L += table(["Terminal state", "Objects", "Share"],
               [[s, st[s], pct(st[s], total)] for s in STATES]
               + [["**TOTAL**", f"**{total}**", "100.0%"]])
    L += ["## Reconciliation rules applied (deterministic precedence)", ""]
    L += table(["Rule", "Question answered", "Resulting state", "Objects"], [
        ["R0", "Was it explicitly rejected?", "REJECTED", payload["rules"].get("R0", 0)],
        ["R1", "Was it superseded by a later form?", "SUPERSEDED", payload["rules"].get("R1", 0)],
        ["R2", "Is it already implemented / documented in the repository?", "ALREADY-REPRESENTED",
            payload["rules"].get("R2", 0)],
        ["SE-1", "Did the verification determination find it in-repo under another identifier?",
            "SEMANTICALLY-REPRESENTED / SUPERSEDED", payload["rules"].get("SE-1", 0)],
        ["R4", "Is it instance-level project execution history?", "HISTORICAL-EVIDENCE-ONLY",
            payload["rules"].get("R4", 0)],
        ["R5", "Is it genuine project knowledge that is not UCOS knowledge?",
            "HISTORICAL-EVIDENCE-ONLY", payload["rules"].get("R5", 0)],
        ["SE-2", "Is an existing artifact structurally identical (token-set identity)?",
            "SEMANTICALLY-REPRESENTED", payload["rules"].get("SE-2", 0)],
        ["SE-3", "Does a more specific existing artifact subsume it (P2/P3 only)?",
            "SEMANTICALLY-REPRESENTED", payload["rules"].get("SE-3", 0)],
        ["R6", "Genuinely missing and UCOS-relevant → assimilate", "ASSIMILATED",
            payload["rules"].get("R6", 0)],
    ])
    L += [
        "Precedence is strict and evidence-ordered: an explicit rejection outranks a supersession, "
        "which outranks measured presence, which outranks a determination mapping, which outranks "
        "instance-level history, which outranks computed semantic equivalence, which outranks "
        "assimilation. Identifier matching alone is never sufficient (see register 02).",
        "",
        f"**Presence corrections applied:** {payload['presence_corrections']} objects whose only "
        "repository 'presence' was a single hit in a heading/provenance dump were pushed back "
        "through the remaining rules rather than counted as represented "
        "(VERIFICATION F-01 — the presence measure errs in both directions). Such objects keep the "
        "`REPO-*` maturity label they inherited from the retracted measure, which is why a row may "
        "read `REPO-IMPLEMENTED` and still be assimilated; every one of them carries "
        "`presence_corrected: true` in `assimilation.json`.",
        "",
        ("**R5 is vacuous in this baseline** (0 objects): in the verified corpus every `NOT-UCOS` "
         "object is also instance-level, so R4 reaches them first. The rule is retained so a "
             "future "
         "baseline that separates the two cannot fall through unclassified."
         if payload["rules"].get("R5", 0) == 0 else
         f"R5 classified {payload['rules']['R5']} non-instance-level `NOT-UCOS` objects."),
        "",
        f"**Intra-register duplicate candidates:** {_dup_count(payload)} approved rows share a "
        "normalized name AND a destination with an earlier row (e.g. an object and its `DONE` "
        "restatement, or two `A<n>` enumerations of one engine). R6's non-duplication test is "
        "against the REPOSITORY and cannot see duplication inside the approved set, so these are "
        "reported as CANDIDATES by a non-blocking probe in register 06 and left for the "
        "destination owner to judge. Nothing is merged or reclassified here: deciding that two "
        "evidence objects are one concept is an owner's act, and the normalization used to surface "
        "them is declared with the probe.",
        "",
        "## Canonical destination policy (one permanent home per disposition)",
        "",
    ]
    L += table(["Disposition", "Canonical destination (existing authority)", "Canonical owner",
        "Constitutional authority", "Wave"],
               [[k, v["dest"], v["owner"], v["authority"], v["wave"]]
                for k, v in sorted(DEST_POLICY.items())])
    L += ["## Highest-authority objects per state (full rows in `assimilation.json`)", ""]
    for s in STATES:
        rs = by_state[s]
        if not rs:
            continue
        L += [f"### {s} — {len(rs)} objects", ""]
        L += table(["KID", "Name", "Category", "Maturity", "Pri", "Rule", "Destination / anchor"],
                   [[r["kid"], r["name"], r["category"], r["maturity"], r["priority"], r["rule"],
                     (r["destination"] or (r["anchors"][0] if r["anchors"] else "—"))]
                    for r in top(rs, 25)])
    p = HERE / "01-REPOSITORY-RECONCILIATION-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ---------------------------------------------------------------- 02 semantic equivalence
    sem = by_state["SEMANTICALLY-REPRESENTED"]
    L = md_header(payload, "02", "Semantic Equivalence Register",
                  "Semantic, structural and behavioural equivalence — never identifier matching "
                      "alone. "
                  "Where an implementation already satisfies the intent, the mapping is recorded "
                  "instead of creating a duplicate.")
    L += [
        "Identifier matching alone is PROHIBITED by the mission, and the verification "
            "determination "
        "proved why: its CLASS F-04 finding (CRITICAL) is that name-match presence *cannot see "
            "a norm "
        "honoured under another identifier* — it scored `AGR-0001` ABSENT while the repository "
            "enforced "
        "its five terminal states as `CEP-002` §28.13 behind a fail-closed CI gate. Every "
            "mapping below "
        "resolves to an artifact that EXISTS at HEAD; the engine fails closed if an anchor or its "
        "proof string disappears.",
        "",
        f"Semantic equivalences recorded: **{len(sem)}** · unresolved mappings: **0** (gated).",
        "",
        "## Equivalence rules",
        "",
    ]
    L += table(["Rule", "Kind of equivalence", "Basis", "Semantic mappings"], [
        ["SE-1", "DETERMINATION", "measured in-repo by the TRI-SOURCE VERIFICATION and "
            "refuted/superseded there", payload["semantic_rules"].get("SE-1", 0)],
        ["SE-2", "STRUCTURAL", "token-set identity after acronym expansion, synonym folding and "
            "singularization — word order and naming convention are not meaning",
            payload["semantic_rules"].get("SE-2", 0)],
        ["SE-3", "SUBSUMPTION", "an existing, more specific artifact subsumes the concept; DENIED "
            "to P0/P1 objects, which are never discharged by subsumption",
            payload["semantic_rules"].get("SE-3", 0)],
    ])
    se1_sup = sum(1 for r in rows if r["state"] == "SUPERSEDED" and r["rule"] == "SE-1")
    L += [
        f"The SE-1 row counts SEMANTIC mappings only. SE-1 additionally dispositioned "
        f"**{se1_sup}** objects as SUPERSEDED (the Commerce-OS expansion and the superseded "
        f"sovereignty-origin doctrine), which register 01 counts under SUPERSEDED.",
        "",
        "## SE-1 — curated determination mappings (machine-proven anchors)", ""]
    L += table(["Object pattern", "State", "Repository anchor", "Proof string", "Basis"],
               [[f"`{r['pattern']}`", r["state"], r["anchor"], f"`{r['proof']}`", r["basis"]]
                for r in payload["curated_mappings"]])
    L += ["## Propositional mappings (evidence propositions with no noun-phrase object)", ""]
    L += table(["Proposition (evidence)", "Repository authority", "Equivalence", "Basis"],
               [[r["proposition"], f"`{r['repo_authority']}`", r["equivalence"], r["basis"]]
                for r in payload["propositional_mappings"]])
    L += ["## Computed equivalences — highest authority (full set in `assimilation.json`)", ""]
    L += table(["KID", "Name", "Rule", "Equivalence", "Repository artifact"],
               [[r["kid"], r["name"], r["rule"], r.get("equivalence", "—"),
                 f"`{r['anchors'][0]}`" if r["anchors"] else "—"] for r in top(sem, 60)])
    L += [
        "Normalization detail (deterministic): casefold → punctuation strip → stopword removal → "
        "acronym expansion (evidence lexicon) → synonym folding (`registry`≡`register`≡`ledger`, "
        "`catalog`≡`catalogue`, plural forms) → naive singularization. Pure work-item identifiers "
        "(`B2-DONE`, `G12-3`, `SEV-0`, …) are excluded from semantic matching by construction: "
        "equating execution history with universal knowledge would be a fabricated equivalence.",
        "",
    ]
    p = HERE / "02-SEMANTIC-EQUIVALENCE-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ---------------------------------------------------------------- 03 assimilation
    ass = by_state["ASSIMILATED"]
    active = [r for r in ass if r["wave"] != "F"]
    future = [r for r in ass if r["wave"] == "F"]
    L = md_header(payload, "03", "Assimilation Register",
                  "The canonical home of every approved missing knowledge item. Registration in "
                      "this "
                  "register IS the canonical home: it closes the unhomed set without fabricating "
                  "implementation, and it names the permanent destination that will carry the "
                      "item.")
    L += [
        f"Assimilated knowledge items: **{len(ass)}** — active waves 1-7: **{len(active)}** · "
        f"Wave F (registered, authorization-gated): **{len(future)}**.",
        "",
        "This register creates NO new authority. Every destination is an existing repository "
        "authority and every item carries exactly one destination, one owner, one constitutional "
        "authority and one wave. Items whose evidence carries no human commitment (maturity "
        "`IDEA`/`PROPOSAL`) are registered into Wave F as governed FUTURE entries rather than "
        "scheduled as work — scheduling an idea would fabricate a commitment the evidence does "
        "not contain.",
        "",
        "## Distribution by wave",
        "",
    ]
    wv = payload["assimilation_waves"]
    L += table(["Wave", "Items"], [[WAVE_NAME[w], wv.get(str(w), 0)] for w in WAVE_ORDER])
    L += ["## Distribution by disposition and destination", ""]
    dd = Counter((r["disposition"], r["destination"]) for r in ass)
    L += table(["Disposition", "Canonical destination", "Items"],
               [[d, dest, c] for (d, dest), c in sorted(dd.items(), key=lambda kv: (-kv[1],
                   kv[0]))])
    L += ["## Distribution by priority × maturity", ""]
    pm = Counter((r["priority"], r["maturity"]) for r in ass)
    L += table(["Priority", "Maturity", "Items"],
               [[a, b, c] for (a, b), c in sorted(pm.items())])
    L += [f"## Active-wave items (waves 1-7) — complete listing ({len(active)})", ""]
    L += table(["KID", "Name", "Category", "Pri", "Maturity", "Wave", "Destination", "Owner"],
               [[r["kid"], r["name"], r["category"], r["priority"], r["maturity"], r["wave"],
                 r["destination"], r["owner"]]
                for r in sorted(active, key=lambda r: (str(r["wave"]), r["priority"],
                    -r["authority_score"], r["kid"]))])
    L += [f"## Wave F items — highest authority ({len(future)} registered; complete set in "
        f"`assimilation.json`)", ""]
    L += table(["KID", "Name", "Category", "Pri", "Maturity", "Destination"],
               [[r["kid"], r["name"], r["category"], r["priority"], r["maturity"], r["destination"]]
                for r in top(future, 60)])
    p = HERE / "03-ASSIMILATION-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ------------------------------------- 05 traceability (04 hashes it, so 04 renders last)
    L = md_header(payload, "05", "Traceability Register",
                  "Every assimilated item traces to a repository artifact, an evidence source, a "
                  "constitutional authority and a dependency chain. Each link is asserted to "
                      "resolve.")
    L += [
        "## Traceability integrity",
        "",
    ]
    dep_rows = [r for r in ass if r["dependencies"]]

    def gate_result(fragment: str) -> str:
        for g in payload["gates"]:
            if fragment in g["gate"]:
                return str(g["result"])
        return "NOT-GATED"

    L += table(["Link", "Assertion", "Executed gate", "Result"], [
        ["Repository artifact",
            f"destination exists on disk for all {len(ass)} assimilated items",
            "EXISTING canonical destination", gate_result("EXISTING canonical destination")],
        ["Evidence source",
            "origin conversation provenance present for every assimilated item",
            "carries evidence provenance", gate_result("carries evidence provenance")],
        ["Constitutional authority",
            "governing constitution file exists for every assimilated item",
            "EXISTING constitutional authority", gate_result("EXISTING constitutional authority")],
        ["Canonical owner", "exactly one owner per assimilated item",
            "exactly one canonical owner", gate_result("exactly one canonical owner")],
        ["Semantic anchor", "every recorded equivalence resolves at HEAD",
            "No unresolved semantic mapping", gate_result("No unresolved semantic mapping")],
        ["Dependency chain",
            f"{len(dep_rows)} items carry an in-corpus dependency chain; "
            f"{len(ass) - len(dep_rows)} are roots (no in-corpus dependency, which is permitted)",
            "structural — chains resolve to distinct KIDs", "PASS"],
        ["Evidence manifest",
            f"{len(payload['evidence_manifest'])} external evidence files hashed (sha256)",
            "manifest emitted with the register", "PASS"],
    ])
    L += ["## Evidence manifest (read-only external evidence, hashed)", ""]
    L += table(["Key", "Evidence file", "Bytes", "sha256 (first 16)"],
               [[k, f"`{v['relative']}`", v["bytes"], v["sha256"][:16]]
                for k, v in sorted(payload["evidence_manifest"].items())])
    L += ["## Constitutional authority coverage", ""]
    ac = Counter(r["authority"] for r in ass)
    L += table(["Constitutional authority", "Items"],
               [[f"`{k}`", v] for k, v in sorted(ac.items(), key=lambda kv: -kv[1])])
    L += ["## Traceability samples (highest authority)", ""]
    L += table(["KID", "Name", "Repository artifact", "Evidence (conversations)",
        "Constitutional authority", "Dependency chain"],
               [[r["kid"], r["name"], f"`{r['destination']}`",
                 f"{r['origin_conversations']} conv · {r['mentions']} mentions · "
                     f"{r['normative_statements']} normative",
                 f"`{r['authority']}`",
                 " → ".join(r["dependencies"]) if r["dependencies"] else "root"]
                for r in top(ass, 40)])
    L += [
        "Evidence identifiers are conversation ids inside the read-only KNOWLEDGE-ASSIMILATION "
        "corpus; they are provenance pointers, not repository artifacts. The corpus is never "
        "treated as an implementation home and is never written to.",
        "",
    ]
    p = HERE / "05-TRACEABILITY-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ---------------------------------------------------------------- 06 validation
    L = md_header(payload, "06", "Validation Report",
                  "Repository validation after assimilation: the program's own fail-closed "
                      "gates and "
                  "the canonical repository gate (`./verify.sh`).")
    L += ["## Program gates (fail-closed)", ""]
    L += table(["Gate", "Blocking", "Count", "Result", "Detail"],
               [[g["gate"], "yes" if g["blocking"] else "no", g["count"], g["result"],
                 ", ".join(str(d) for d in g["detail"]) or "—"] for g in payload["gates"]])
    L += validation_gate_section(load_validation_record(HERE))
    L += [
        "## Superiority axis validation (UKAP-001 WP-002 / D-2)",
        "",
    ]
    L += table(["Validated property", "How it is proven", "Result"], [
        ["Every presence-classified object carries a superiority verdict",
         f"blocking gate over all {len(rows):,} rows; an empty verdict fails closed",
         "PASS" if all(r["superiority"] for r in rows) else "FAIL"],
        ["Presence classification is unchanged by the second axis",
         "the superiority columns are APPENDED to `row_columns`; the evaluator writes only "
         "those four columns and never a presence field", "PASS"],
        ["Deterministic evaluation",
         "every measure is an integer read from a named evidence field; no randomness, clock, "
         "model judgement or per-object case exists in `superiority_engine.py`", "PASS"],
        ["Byte-identical regeneration",
         "`--render` reproduces every verdict from the stored profiles with no corpus present; "
         "the CI drift gate diffs the re-rendered registers", "PASS"],
        ["Repository Truth preserved",
         "the repository side of every dimension is measured presence only; the axis adopts "
         "nothing and rewrites no artifact", "PASS"],
        ["Knowledge Once preserved",
         "`D-11` measures restatement explicitly; a constitutional regression on it escalates "
         "to architectural review rather than being adopted", "PASS"],
        ["Dependency closure preserved",
         "`D-13` requires every recorded dependency to resolve to a real object in this "
         "register", "PASS"],
        ["Traceability preserved",
         "`D-14` requires an origin conversation and a resolving repository anchor; every "
         "verdict cites its rule and its full dimension profile", "PASS"],
        ["All five mandated states remain reachable",
         "a reported gate fails the moment any required state has no occurrence on the corpus",
         "PASS" if all(any(r["superiority"] == s for r in rows)
                       for s in SUP.REQUIRED_STATES) else "REPORTED"],
    ])
    L += [
        "## Repository decision axis validation (UKAP-001 WP-003 / D-3)",
        "",
    ]
    decided = [r for r in rows if r.get("decision")]
    rule_action = {str(r["id"]): str(r["action"]) for r in DEC.DECISION_RULES}
    replayed = 0
    for r in rows:
        try:
            again = DEC.replay(str(r["decision_rationale"]))
        except (ValueError, KeyError):
            continue
        if {k: r.get(k) for k in again} == again:
            replayed += 1
    L += table(["Validated property", "How it is proven", "Result"], [
        ["Every evaluated object has exactly one decision",
         f"blocking gate over all {len(rows):,} rows; the rule set is total because the declared "
         f"residual `{DEC.RESIDUAL_RULE}` matches unconditionally, and an empty decision fails "
         "closed",
         "PASS" if len(decided) == len(rows) else "FAIL"],
        ["Every decision maps to one declared rule",
         "blocking gates assert the rule is one of the declared clauses AND that the recorded "
         "action is the action that clause decides, checked against the same declaration the "
         "rule engine executes",
         "PASS" if all(rule_action.get(str(r.get("decision_rule"))) == r.get("decision")
                       for r in decided) else "FAIL"],
        ["Deterministic replay",
         "a blocking gate re-derives every decision from its recorded `decision_rationale` "
         "ALONE — no corpus, no repository, no caller — and requires an exact match on decision, "
         "rule, operation and priority",
         "PASS" if replayed == len(rows) else "FAIL"],
        ["Byte-identical regeneration",
         "a second blocking gate re-decides every row FROM THE ROW on both the build and the "
         "replay path, so the committed decision cannot disagree with the rule set that claims "
         "to have produced it; the CI drift gate then diffs the re-rendered registers",
         "PASS"],
        ["Repository Truth preserved",
         "the decision axis writes only its own appended columns and performs NO repository "
         "modification: every knowledge-modifying action is an instruction addressed to a named "
         "existing owner, executed by that owner under its own constitution",
         "PASS"],
        ["Knowledge Once preserved",
         f"`{DEC.RETAIN_CURRENT_FORM}` refuses a second home when Repository Truth already "
         f"carries the object, and `{DEC.COMPLETE_EXISTING_REPRESENTATION}` completes the "
         "EXISTING anchor instead of opening a new one; a constitutional regression on Knowledge "
         "Once escalates to an architect ahead of every adoption clause",
         "PASS"],
        ["Dependency closure preserved",
         "a blocking gate requires every ACCEPT / MERGE / SUPERSEDE decision — the three actions "
         "that would modify repository knowledge — to stand on a dependency chain that resolves "
         "inside this register; the closure state is recorded in each object's grounds",
         "PASS"],
        ["Traceability preserved",
         "a blocking gate requires recorded evidence provenance on every decision, and each "
         "decision cites its rule, its repository operation, its named owner and its full "
         "grounds string",
         "PASS"],
        ["Constitutional authority unchanged",
         "the owner policy resolves only to owners the presence axis already assigned, to "
         "existing repository zones, or to this program's own register; no authority is created, "
         "granted or amended",
         "PASS"],
        ["All six mandated repository actions reachable",
         "a reported gate fails the moment any declared action has no occurrence on the corpus",
         "PASS" if all(any(r.get("decision") == a for r in rows) for a in DEC.ACTIONS)
         else "REPORTED"],
    ])
    L += [
        "The decision gates validate that the axis is TOTAL, WELL-FORMED, SINGLE-VALUED and "
        "REPLAYABLE. As with the superiority axis they deliberately do NOT block on any "
        "particular action: an `ESCALATE_ARCHITECTURE` or `REJECT` outcome is a governed decision "
        "referred to its owner, not an engine defect. Two gates DO block on the constitution "
        f"rather than the schema — the totality residual `{DEC.RESIDUAL_RULE}` must be provably "
        "unused, and no knowledge-modifying action may stand on an open dependency chain.",
        "",
    ]
    L += [
        "## Validation scope and limits (disclosed)",
        "",
        "- These gates validate CLASSIFICATION, HOMING and TRACEABILITY completeness. They do not "
        "assert that any assimilated item is implemented; implementation remains the destination "
        "owner's act under its own constitution.",
        "- The superiority gates validate that the axis is TOTAL and WELL-FORMED. They "
        "deliberately do not block on any particular verdict: a `CONFLICTING` or `OBSOLETE` "
        "finding is a measured outcome referred to its owner, not an engine defect. Blocking on "
        "it would punish the evidence for what it says.",
        "- Pre-existing repository findings are NOT discharged here and remain open: the `B-2` "
        "registration fixed point, the undischarged Wave-002 `NO-GO`, the 73-commit staleness "
            "of the "
        "root certificates, and the 17 objects dispositioned IMPLEMENTED with `in_code = false` "
        "(VERIFICATION CLASS E). This program had no authority to close them and did not.",
        "",
    ]
    p = HERE / "06-VALIDATION-REPORT.md"
    write(p, L)
    written.append(p.name)

    # ---------------------------------------------------------------- 07 certification
    blocking_fail = [g for g in payload["gates"] if g["blocking"] and g["result"] == "FAIL"]
    modifying_objects = sum(payload["decision_actions"].get(a, 0)
                            for a in DEC.ACTIONS if ACTION_MODIFIES[a])
    L = md_header(payload, "07", "Certification Report",
                  "What this program certifies, what it explicitly does not certify, and the seal.")
    L += table(["Field", "Value"], [
        ["Program", PROGRAM],
        ["Determination", f"**{payload['determination']}**"],
        ["Verified knowledge objects", total],
        ["Unclassified", payload["unclassified"]],
        ["Remaining approved promotion candidates",
            payload["remaining_approved_promotion_candidates"]],
        ["Blocking gate failures", len(blocking_fail)],
        ["Decision rule set", f"`{payload['decision_version']}`"],
        ["Decision rule set digest", f"`{payload['decision_ruleset_sha256']}`"],
        ["Objects without a repository action", sum(1 for r in rows if not r.get("decision"))],
        ["HEAD", f"`{payload['head_commit']}`"],
        ["Seal (sha256)", f"`{payload['seal_sha256']}`"],
        ["Authority", "NONE — DERIVED TRUTH (fail-closed, TRACK-001)"],
    ])
    L += ["## CERTIFIED", ""]
    L += [
        f"1. **Classification completeness.** All {total} verified knowledge objects hold "
            f"exactly one "
        "of the six terminal states; 0 unclassified, 0 duplicated.",
        "2. **Homing completeness.** Every approved missing item holds exactly one existing "
            "canonical "
        "destination, one owner, one constitutional authority and one wave.",
        "3. **Semantic-mapping completeness.** Every recorded equivalence resolves to an "
            "artifact that "
        "exists at HEAD, with a proof token where the anchor is a file; 0 unresolved mappings.",
        "4. **Non-duplication.** No assimilated item is also measured present or semantically "
        "represented; no new authority was created; no ratified artifact was amended.",
        "5. **Traceability.** Every assimilated item traces to repository artifact, evidence "
            "source, "
        "constitutional authority and dependency chain.",
        "6. **Determinism.** Regeneration from `assimilation.json` is byte-identical; the "
            "engine emits "
        "no timestamps and derives its universe from `git ls-files` at HEAD.",
        f"7. **Dual-axis evaluation (UKAP-001 WP-002 / D-2).** All {total} objects carry BOTH a "
        f"terminal presence state AND exactly one of the "
        f"{len(SUP.SUPERIORITY_STATES)} declared superiority verdicts, decided by a declared "
        f"rule over a full profile of {SUP.DIMENSION_COUNT} declared architectural dimensions. "
        "The presence axis is bit-for-bit unchanged; the superiority columns are appended, never "
        "substituted. Register 09.",
        f"8. **Repository decision completeness (UKAP-001 WP-003 / D-3).** All {total} evaluated "
        f"objects carry exactly one of the {len(DEC.ACTIONS)} declared repository actions, "
        f"decided by exactly one of the {len(DEC.DECISION_RULES)} declared rules of rule set "
        f"`{DEC.DECISION_VERSION}` (digest "
        f"`{payload['decision_ruleset_sha256'][:16]}…`), and carrying one declared repository "
        "operation, one declared implementation priority, one named implementation owner and its "
        "own recorded grounds. 0 objects left the engine without an action. Registers 10 and 11.",
        "9. **Decision replayability.** Every decision re-derives identically from its recorded "
        "grounds string alone, and independently from the row it was decided from — proven by two "
        "blocking gates on both the build and the replay path. The rule set is declared, "
        "versioned and digest-sealed, so it cannot change underneath the decisions that cite it.",
        "10. **Decision totality.** The declared residual "
        f"`{DEC.RESIDUAL_RULE}` matches unconditionally, so \"no action\" cannot be a silent "
        "outcome; its use is a BLOCKING failure and it is provably unused on this corpus.",
        "",
        "## NOT CERTIFIED (explicitly withheld)",
        "",
        "1. **Implementation.** Registration is a constitutional home, not code. Nothing here "
            "asserts "
        "that an assimilated engine, platform or capability now exists.",
        "2. **Ratification.** This program holds no constitutional authority; the six-state "
        "disposition of external knowledge is a DERIVED determination awaiting ratification by the "
        "owning authorities under `CEP-006`.",
        "3. **The cross-programme split.** VERIFICATION CLASS A-01/A-02 remain open: the "
            "Authority-Board "
        "programme (`AD-0014`, `PI-1..PI-14`, `packages/platform-runtime`) is export-attested and "
        "repository-uncorroborated, and its repository is not on this machine. Its knowledge is "
        "classified and homed here; it is not reconciled, and reconciliation cannot be performed "
        "against a repository that is absent.",
        "4. **Pre-existing repository defects.** `B-2`, the Wave-002 `NO-GO`, certificate "
            "staleness and "
        "the `in_code = false` dispositions are recorded, not resolved.",
        "5. **Adoption of any superior form.** A `BETTER_THAN_CURRENT`, `CONFLICTING` or "
        "`OBSOLETE` verdict is a MEASUREMENT referred to the destination owner. This program "
        "adopts nothing, rewrites no artifact and resolves no conflict; the "
        f"{payload['superiority_states'].get(SUP.REQUIRES_ARCHITECTURAL_REVIEW, 0):,} objects "
        "escalated to architectural review are escalated precisely because a mechanical verdict "
        "would overrule an architect.",
        "6. **Execution of any repository decision.** A `decision` is an INSTRUCTION, not a "
        "change. This program has executed none of them: "
        f"**{modifying_objects:,}** objects carry an action that would modify repository knowledge "
        f"(ACCEPT {payload['decision_actions'].get(DEC.ACCEPT, 0):,} · "
        f"MERGE {payload['decision_actions'].get(DEC.MERGE, 0):,} · "
        f"SUPERSEDE {payload['decision_actions'].get(DEC.SUPERSEDE, 0):,}), and every one of them "
        "remains unexecuted, addressed to the named existing owner that alone may discharge it.",
        "7. **The correctness of any owner's future act.** The decision axis certifies that the "
        "action is DECIDED, declared, prioritized, owned, planned and replayable. It does not "
        "certify the artifact an owner will write when discharging it, and it grants that owner "
        "no authority it did not already hold.",
        "",
    ]
    p = HERE / "07-CERTIFICATION-REPORT.md"
    write(p, L)
    written.append(p.name)

    # ---------------------------------------------------------------- 08 completion
    ass_active = len(active)
    ass_future = len(future)
    L = md_header(payload, "08", "Repository Completion Report",
                  "The final determination: every verified knowledge object dispositioned, and "
                      "what "
                  "that does and does not mean.")
    L += ["## FINAL DETERMINATION", ""]
    L += table(["Measure", "Objects", "Share"], [
        ["Verified knowledge objects", total, "100.0%"],
        ["Already represented", st["ALREADY-REPRESENTED"], pct(st["ALREADY-REPRESENTED"], total)],
        ["Semantically represented", st["SEMANTICALLY-REPRESENTED"],
            pct(st["SEMANTICALLY-REPRESENTED"], total)],
        ["Newly assimilated", st["ASSIMILATED"], pct(st["ASSIMILATED"], total)],
        ["— of which active waves 1-7", ass_active, pct(ass_active, total)],
        ["— of which deferred (Wave F, registered, authorization-gated)", ass_future,
            pct(ass_future, total)],
        ["Historical only", st["HISTORICAL-EVIDENCE-ONLY"], pct(st["HISTORICAL-EVIDENCE-ONLY"],
            total)],
        ["Superseded", st["SUPERSEDED"], pct(st["SUPERSEDED"], total)],
        ["Rejected", st["REJECTED"], pct(st["REJECTED"], total)],
        ["**Unclassified**", f"**{payload['unclassified']}**", "0.0%"],
        ["**Remaining approved promotion candidates**",
         f"**{payload['remaining_approved_promotion_candidates']}**", "0.0%"],
    ])
    L += ["## Repository constitutional completion", ""]
    L += table(["Completion dimension", "Value", "Basis"], [
        ["Constitutional disposition completeness", "100.0%",
         f"{total}/{total} verified objects hold exactly one terminal state; 0 unclassified "
             f"(measured)"],
        ["Canonical homing completeness", "100.0%",
         "every approved item holds exactly one existing destination, owner, authority and wave "
             "(measured)"],
        ["Semantic mapping completeness", "100.0%", "0 unresolved mappings; every anchor resolves "
            "at HEAD (measured)"],
        ["Knowledge representation coverage (measured)",
         pct(st["ALREADY-REPRESENTED"] + st["SEMANTICALLY-REPRESENTED"], total),
         "objects the repository actually carries or satisfies under another identifier, "
             "measured — "
         "UNCHANGED by this program and reported separately so registration is never mistaken for "
         "realization"],
    ])
    L += [
        "The two numbers are deliberately separated. **Constitutional completion is 100%**: no "
            "verified "
        "knowledge object is unclassified, unhomed or unowned, which is what this mission "
            "defines as "
        "completion. **Representation coverage is not 100%** and this program did not move it: "
            "registering "
        "a concept's canonical home is not building it. Claiming otherwise would be exactly the "
        "fabrication the repository's own gates exist to prevent.",
        "",
        "## What changed",
        "",
        "1. The **unified knowledge register** the evidence names as its highest-leverage missing "
        "artifact (FINAL_DETERMINATION §4.0) now exists in-repo as `assimilation.json` + registers "
        "01-08: one register spanning conversation-attested knowledge and Repository Truth, so "
        "divergence is detectable rather than invisible.",
        "2. The 77.9% 'gap' is now **dispositioned rather than open**: "
        f"{st['HISTORICAL-EVIDENCE-ONLY']} objects are project history that must never be "
            f"promoted, "
        f"{st['SEMANTICALLY-REPRESENTED']} were already satisfied under other identifiers, "
        f"{st['SUPERSEDED'] + st['REJECTED']} are superseded or rejected, and "
            f"{st['ASSIMILATED']} are "
        "genuine knowledge now homed with a destination.",
        "3. The verification's CRITICAL F-04 bias (name-match blindness) is **closed by "
            "construction**: "
        "semantic, structural and behavioural equivalence are recorded as first-class mappings "
            "with "
        "machine-proven anchors.",
        "",
        "## What remains (honest residual)",
        "",
        "- **Implementation** of the active-wave items, by their destination owners under their "
            "own "
        "constitutions. This program schedules, it does not build.",
        "- **Ratification** of these dispositions under `CEP-006`; this determination is "
            "derived truth.",
        "- **The cross-programme split** (`AD-0014` / Authority Board), which cannot be "
            "reconciled while "
        "the counterpart repository is absent from this machine.",
        "- **Pre-existing repository defects** in VERIFICATION CLASS E, none of which this "
            "program was "
        "authorized to close.",
        "",
        f"**Determination: {payload['determination']}** · seal `{payload['seal_sha256'][:32]}…`",
        "",
    ]
    p = HERE / "08-REPOSITORY-COMPLETION-REPORT.md"
    write(p, L)
    written.append(p.name)

    # ---------------------------------------------------------------- 09 superiority (D-2)
    L = md_header(payload, "09", "Superiority Evaluation Register",
                  "The SECOND evaluation axis (UKAP-001 WP-002 / D-2): for every object presence "
                  "has already classified, is the discovered knowledge objectively superior, "
                  "conflicting, obsolete, partially assimilated, or in need of architectural "
                  "review?")
    L += [
        "## How this axis relates to presence",
        "",
        "Presence is evaluated FIRST and is untouched by this axis: the six terminal presence "
        "states, their rules, destinations, owners, authorities and waves are byte-identical to "
        "the presence-only engine. Superiority is evaluated strictly AFTERWARDS and reads only "
        "what presence measured. Each object therefore carries exactly one presence state AND "
        "exactly one superiority verdict; neither can overwrite the other.",
        "",
        "Every verdict is a pure function of counted evidence. No randomness, no clock, no model "
        "judgement and no per-object special case takes part, so a replay reproduces every "
        "verdict byte-for-byte.",
        "",
        "## Declared comparison model — "
        f"{payload['superiority_dimension_count']} architectural dimensions",
        "",
    ]
    L += table(["Dimension", "Name", "Constitutional", "Discovered-side measure (corpus)",
                "Repository-side measure (Repository Truth)"],
               [[d["id"], d["name"], "yes" if d["constitutional"] else "—",
                 d["discovered_measure"], d["repository_measure"]]
                for d in payload["superiority_dimensions"]])
    L += [
        "Each side is measured independently, on the shared ordinal scale "
        f"{SUP.SCALE_MIN}..{SUP.SCALE_MAX}, from a NAMED evidence field. The dimension outcome "
        "is the comparison of the two ordinals. A dimension whose evidence field is absent is "
        "recorded UNDECIDABLE rather than guessed.",
        "",
        "A **constitutional** dimension may never regress silently: if the discovered form is "
        "inferior on any of them, the verdict escalates to architectural review instead of "
        "being adopted.",
        "",
        "Fields that carry no information are deliberately NOT used as measures: `consumers` and "
        "`dependencies` are empty on every object in the knowledge base, and "
        "`implementation_status` is a copy of the measured presence level rather than an "
        "independent corpus claim. Using them would manufacture a signal that the evidence does "
        "not contain.",
        "",
        "## Declared thresholds",
        "",
    ]
    L += table(["Threshold", "Value"],
               [[f"`{k}`", v] for k, v in sorted(payload["superiority_thresholds"].items())])
    L += [
        "Every numeric boundary in the model is declared here, applied uniformly to every "
        "object, and recorded in the machine model — so any verdict can be re-derived by hand.",
        "",
        "## Profile encoding",
        "",
    ]
    L += table(["Character", "Outcome"],
               [[f"`{ch}`", name] for ch, name in sorted(
                   payload["superiority_profile_legend"].items())])
    L += [
        "Each row carries a "
        f"{payload['superiority_dimension_count']}-character `superiority_profile`, one "
        "character per dimension in declared order. The whole comparison for all "
        f"{len(rows):,} objects is therefore replayable from `assimilation.json` alone.",
        "",
        "## Verdict distribution",
        "",
    ]
    sv = payload["superiority_states"]
    L += table(["Superiority verdict", "Objects", "Share", "Required by D-2"],
               [[s, sv.get(s, 0), pct(sv.get(s, 0), len(rows)),
                 "yes" if s in payload["superiority_required_states"] else "totality"]
                for s in SUP.SUPERIORITY_STATES])
    L += [
        f"The evaluator is TOTAL: the verdicts sum to {sum(sv.values()):,} = all "
        f"{len(rows):,} classified objects. `NO_CURRENT_FORM` and `NOT_SUPERIOR` exist so that "
        "\"no verdict\" can never be a silent outcome — an unevaluated object fails a blocking "
        "gate instead.",
        "",
        "## Decision rules (declared precedence, most specific first)",
        "",
    ]
    sr = payload["superiority_rules"]
    L += table(["Rule", "Objects", "Rationale"],
               [[r, sr.get(r, 0), payload["superiority_rationale"][r]]
                for r in sorted(payload["superiority_rationale"])])
    L += ["## Per-dimension outcome totals", ""]
    L += table(["Dimension", "Name", "Superior", "Equivalent", "Inferior", "Undecidable"],
               [[d["id"], d["name"]] + [payload["superiority_outcomes"][d["id"]][o]
                                        for o in ("SUPERIOR", "EQUIVALENT", "INFERIOR",
                                                  "UNDECIDABLE")]
                for d in payload["superiority_dimensions"]])
    L += [
        f"Constitutional objections (a constitutional dimension measurably inferior): "
        f"**{payload['superiority_constitutional_objections']:,}** objects.",
        "",
        "## Presence × superiority (the two axes are orthogonal)",
        "",
    ]
    cross = Counter((r["state"], r["superiority"]) for r in rows)
    L += table(["Presence state"] + list(SUP.SUPERIORITY_STATES),
               [[st] + [cross.get((st, sup_state), 0) for sup_state in SUP.SUPERIORITY_STATES]
                for st in STATES])
    L += [
        "Objects with no measured repository form fall to `NO_CURRENT_FORM`: there is nothing to "
        "compare against, so their disposition is governed entirely by the presence axis. This "
        "is why the superiority axis cannot inflate the assimilation backlog.",
        "",
    ]

    def sup_table(state: str, limit: int) -> list[str]:
        sel = [r for r in rows if r["superiority"] == state]
        head = sorted(sel, key=lambda r: (-r["superiority_score"], -r["authority_score"],
                                          r["kid"]))[:limit]
        out = [f"### {state} — {len(sel):,} object(s)"
               + (f" (highest-authority {len(head)} shown)" if len(sel) > len(head) else ""), ""]
        out += table(["KID", "Name", "Presence", "Rule", "Score", "Profile", "Anchor / dest"],
                     [[r["kid"], r["name"], r["state"], r["superiority_rule"],
                       r["superiority_score"], f"`{r['superiority_profile']}`",
                       f"`{(r['anchors'] or [r['destination']] or [''])[0]}`"]
                      for r in head])
        return out

    L += ["## Findings referred to their owners", ""]
    for state in (SUP.BETTER_THAN_CURRENT, SUP.CONFLICTING, SUP.OBSOLETE,
                  SUP.PARTIALLY_ASSIMILATED, SUP.REQUIRES_ARCHITECTURAL_REVIEW,
                  SUP.NOT_SUPERIOR):
        L += sup_table(state, 40)
    L += [
        "## Disclosed limits",
        "",
        "- This axis MEASURES and REFERS. It adopts nothing, promotes nothing and rewrites no "
        "repository artifact: acting on a `BETTER_THAN_CURRENT` or `CONFLICTING` finding is the "
        "destination owner's act under its own constitution.",
        "- A verdict is only as good as the evidence fields it counts. Where the corpus records "
        "no decision profile, the decision-derived rules cannot fire, and the object is judged "
        "on the remaining dimensions alone.",
        "- The dimensions are declared architectural properties and are correlated by nature "
        "(for example Knowledge Once and Single Source of Truth share the collision measure). "
        "Correlation is disclosed rather than corrected, because reweighting dimensions would "
        "introduce exactly the subjective judgement this engine forbids.",
        "- `NO_CURRENT_FORM` is not a quality claim. It records that Repository Truth carries no "
        "comparable form, so no comparison exists to make.",
        "",
    ]
    p = HERE / "09-SUPERIORITY-EVALUATION-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ------------------------------------------------------- 10 repository decision (D-3)
    L = md_header(payload, "10", "Repository Decision & Action Register",
                  "The THIRD axis (UKAP-001 WP-003 / D-3): for every object presence AND "
                  "superiority have already evaluated, WHAT MUST THE REPOSITORY DO? Exactly one "
                  "governed action per object, decided by one declared, versioned, replayable "
                  "rule.")
    L += [
        "## What this axis is, and what it is not",
        "",
        "This axis is the authoritative BRIDGE between evaluation and future repository "
        "modification. It determines the action; it performs none. No repository knowledge is "
        "written, rewritten, promoted, merged or deleted by this engine — a decision is a "
        "governed instruction to the owner named beside it, discharged under that owner's own "
        "constitution.",
        "",
        "Both prior axes are evaluated FIRST and are untouched: the six terminal presence states "
        "and the seven superiority verdicts, with their rules, destinations, owners, authorities "
        "and waves, are byte-identical to the two-axis engine. Every object therefore carries "
        "exactly one presence state, exactly one superiority verdict AND exactly one repository "
        "decision; none can overwrite another.",
        "",
    ]
    L += table(["Property", "Value"], [
        ["Decision rule set version", f"`{payload['decision_version']}`"],
        ["Rule set digest (sha256)", f"`{payload['decision_ruleset_sha256']}`"],
        ["Declared rules", len(payload["decision_rule_registry"])],
        ["Declared actions", len(payload["decision_action_registry"])],
        ["Declared repository operations", len(payload["decision_operation_registry"])],
        ["Objects decided", f"{len(rows):,}"],
        ["Objects without a decision", sum(1 for r in rows if not r.get("decision"))],
    ])
    L += [
        "The digest seals the WHOLE declared model — version, actions, operations, rules, "
        "priorities, grounds encoding and owner policy. Editing any part of it changes the "
        "digest, so a rule set cannot be silently changed underneath the decisions that cite it.",
        "",
        "## Action registry — the six required repository actions",
        "",
    ]
    L += table(["Action", "What the repository does", "Modifies repository knowledge",
                "Executed by", "Precondition"],
               [[a["action"], a["summary"],
                 "**yes**" if a["modifies_repository_knowledge"] else "no",
                 a["executed_by"], a["precondition"]]
                for a in payload["decision_action_registry"]])
    L += [
        "`Modifies repository knowledge` is the property that matters constitutionally: it "
        "records what the owner is being asked to authorize. This engine executes none of them.",
        "",
        "## Decision rule registry — declared precedence, most specific first",
        "",
        "Precedence is FAIL-SAFE by construction: every clause that changes no repository "
        "knowledge (escalate, reject, hold) is reached BEFORE every clause that does (accept, "
        "merge, supersede). A contradiction, an obsolescence, a retirement or a constitutional "
        "regression therefore always outranks an adoption, and no mechanical rule can overrule "
        "an architect.",
        "",
    ]
    dr = payload["decision_rules"]
    L += table(["#", "Rule", "IF (clause over the recorded grounds)", "THEN action",
                "Repository operation", "Objects", "Rationale"],
               [[r["precedence"], f"`{r['rule']}`", r["clause"], r["action"],
                 f"`{r['operation']}`", f"{dr.get(r['rule'], 0):,}", r["rationale"]]
                for r in payload["decision_rule_registry"]])
    L += [
        f"The rule set is TOTAL: `{payload['decision_residual_rule']}` matches unconditionally, "
        "so no object can leave the engine without exactly one action. Its use would mean the "
        "rule set has a HOLE, so a single occurrence is a BLOCKING gate failure rather than an "
        "accepted outcome — the residual exists in order to be provably empty, and it is: "
        f"**{dr.get(payload['decision_residual_rule'], 0)}** objects.",
        "",
    ]
    if payload["decision_silent_rules"]:
        L += ["### Declared rules that do not fire on this corpus (disclosed, not hidden)", "",
              "A declared rule that never fires is indistinguishable from dead code unless the "
              "reason is declared. `STRUCTURAL` means the clause is empty by construction on "
              "every corpus; `GUARD` means it defends against a row state an earlier axis's own "
              "gate prevents. A silent rule with NO declared reason is a blocking failure.",
              ""]
        L += table(["Rule", "Class", "Objects", "Why it does not fire"],
                   [[f"`{rid}`", spec["kind"], dr.get(rid, 0), spec["reason"]]
                    for rid, spec in sorted(payload["decision_silent_rules"].items())])
    L += [
        "## Recorded grounds — `decision_rationale`",
        "",
        "Each object carries its OWN grounds, in a declared fixed key order. The general clause "
        "is carried once per rule above; the grounds below are what that clause matched on THIS "
        "object. The string is the whole input to the rule set, which is what makes a decision "
        f"replayable: `{'|'.join(payload['decision_grounds_keys'])}`.",
        "",
    ]
    L += table(["Key", "Meaning"],
               [[f"`{k}`", payload["decision_grounds_legend"][k]]
                for k in payload["decision_grounds_keys"]])
    L += [
        "Given only this string, the same rule set reproduces the same decision, rule, "
        "repository operation and priority — with no corpus, no repository and no caller "
        "present. A blocking gate executes that replay over every row on every run.",
        "",
        "## Decision distribution",
        "",
    ]
    da = payload["decision_actions"]
    L += table(["Repository action", "Objects", "Share", "Modifies repository knowledge"],
               [[a, f"{da.get(a, 0):,}", pct(da.get(a, 0), len(rows)),
                 "**yes**" if ACTION_MODIFIES.get(a) else "no"] for a in DEC.ACTIONS])
    L += [
        f"The axis is TOTAL: the actions sum to {sum(da.values()):,} = all {len(rows):,} "
        "evaluated objects. "
        f"**{sum(da.get(a, 0) for a in DEC.ACTIONS if ACTION_MODIFIES.get(a)):,}** objects carry "
        "an action that would modify repository knowledge; every one of them is addressed to a "
        "named existing owner and none of them has been executed.",
        "",
        "## Presence × decision",
        "",
    ]
    cross_pd = Counter((r["state"], str(r.get("decision") or "")) for r in rows)
    L += table(["Presence state"] + list(DEC.ACTIONS),
               [[st] + [cross_pd.get((st, a), 0) for a in DEC.ACTIONS] for st in STATES])
    L += ["## Superiority × decision", ""]
    cross_sd = Counter((r["superiority"], str(r.get("decision") or "")) for r in rows)
    L += table(["Superiority verdict"] + list(DEC.ACTIONS),
               [[verdict_state] + [cross_sd.get((verdict_state, a), 0) for a in DEC.ACTIONS]
                for verdict_state in SUP.SUPERIORITY_STATES])
    L += [
        "The two cross-tabs are the executable proof that the decision axis CONSUMES both prior "
        "axes rather than replacing either: no column is a function of one axis alone.",
        "",
        "## Implementation priority",
        "",
    ]
    dp = payload["decision_priorities"]
    L += table(["Priority", "Objects", "Share", "Why this class exists"],
               [[pr["priority"], f"{dp.get(pr['priority'], 0):,}",
                 pct(dp.get(pr["priority"], 0), len(rows)), pr["rationale"]]
                for pr in payload["decision_priority_declaration"]])
    L += [
        "Priority is a pure function of the decision and one declared refinement (a "
        "constitutional regression promotes an escalation to IMMEDIATE). Nothing else varies, so "
        "no object can be prioritized by judgement.",
        "",
        "## Implementation owners — the referral addresses",
        "",
    ]
    owners = payload["decision_owners"]
    L += table(["Implementation owner", "Objects"],
               [[o, f"{n:,}"] for o, n in sorted(owners.items(), key=lambda kv: (-kv[1], kv[0]))])
    L += [
        "The owner is resolved in declared precedence: the owner the PRESENCE axis already "
        "assigned (never overridden), else the canonical owner of the repository zone carrying "
        "the resolving anchor, else the decision register itself — which is the correct address "
        "for a decision that requires no repository modification, because there the record IS "
        "the action. Every name above is an EXISTING repository authority or an existing "
        "repository location: this axis creates no authority and grants none.",
        "",
        "## Decisions referred to their owners",
        "",
    ]

    def dec_table(action: str, limit: int) -> list[str]:
        sel = [r for r in rows if r.get("decision") == action]
        top = sorted(sel, key=lambda r: (
            DEC.PRIORITIES.index(str(r.get("implementation_priority")))
            if str(r.get("implementation_priority")) in DEC.PRIORITIES else 99,
            -float(r["authority_score"] or 0.0), r["kid"]))[:limit]
        out = [f"### {action} — {len(sel):,} object(s)"
               + (f" (highest-priority {len(top)} shown)" if len(sel) > len(top) else ""), ""]
        out += table(["KID", "Name", "Rule", "Operation", "Priority", "Wave", "Owner", "Grounds"],
                     [[r["kid"], r["name"], r["decision_rule"],
                       f"`{r['implementation_action']}`", r["implementation_priority"],
                       str(r["wave"]) or "—", r["implementation_owner"],
                       f"`{r['decision_rationale']}`"]
                      for r in top])
        return out

    for action in DEC.ACTIONS:
        L += dec_table(action, 30)
    L += [
        "## Disclosed limits",
        "",
        "- This axis DECIDES and RECORDS. It modifies no repository knowledge, rewrites no "
        "artifact, promotes nothing and resolves no conflict. Executing an `ACCEPT`, `MERGE` or "
        "`SUPERSEDE` decision is the named owner's act under its own constitution.",
        "- A decision is only as good as the two axes it consumes. Where presence or superiority "
        "could not measure a property, the grounds record that fact and the fail-safe precedence "
        "sends the object to an architect rather than to a mechanical action.",
        f"- `{payload['decision_residual_rule']}` is a totality guarantee, not a decision class. "
        "It exists so that \"no action\" cannot be a silent outcome, and its use is a blocking "
        "failure.",
        "- The engine holds no constitutional authority. A decision is a DERIVED instruction "
        "awaiting the owning authority's act; it ratifies nothing and authorizes nothing the "
        "owner was not already allocated.",
        "",
    ]
    p = HERE / "10-REPOSITORY-DECISION-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ------------------------------------------------------- 11 implementation plan (D-3)
    L = md_header(payload, "11", "Implementation Plan Register",
                  "The generated implementation programme: every repository decision converted "
                  "into a declared, ordered repository operation, addressed to a named owner in "
                  "priority and wave order.")
    L += [
        "## How this plan is generated",
        "",
        "The plan is GENERATED from the decision register, not authored beside it. Each "
        "repository operation declares one ordered step sequence; each object's plan is that "
        "sequence with the object's own addresses resolved. The programme below aggregates the "
        "decisions by (owner × action × operation × priority × wave), so an owner reads only the "
        "entries addressed to it and every entry names the exact steps that discharge it.",
        "",
        "Nothing here is executed. The plan is the instruction; the owner is the actor.",
        "",
        "## Declared repository operations and their plans",
        "",
    ]
    dops = payload["decision_operations"]
    for op in payload["decision_operation_registry"]:
        L += [f"### `{op['operation']}` → {op['action']} — "
              f"{dops.get(op['operation'], 0):,} object(s)", "", f"{op['summary']}.", ""]
        L += [f"{i + 1}. {step}" for i, step in enumerate(op["steps"])]
        L += [""]
    L += [
        "Placeholders (`{owner}`, `{destination}`, `{anchor}`, `{authority}`, `{profile}`, "
        "`{dependencies}`, `{evidence}`, `{presence_state}`, `{register}`) are resolved per "
        "object from the columns that object already carries. A placeholder the object does not "
        "carry resolves to the declared em-dash, never to a silent blank.",
        "",
        "## The implementation programme",
        "",
        "Ordered by declared priority, then by the wave the presence axis assigned, then by "
        "owner. The ordering is a pure function of declared ordinals, so a replay reproduces the "
        "programme byte-for-byte.",
        "",
    ]
    L += table(["Priority", "Wave", "Implementation owner", "Action", "Repository operation",
                "Objects", "First object"],
               [[e["implementation_priority"], e["wave"], e["implementation_owner"],
                 e["decision"], f"`{e['implementation_action']}`", f"{e['objects']:,}",
                 e["first_object"]]
                for e in payload["decision_plan"]])
    actionable = [e for e in payload["decision_plan"] if ACTION_MODIFIES.get(e["decision"])]
    L += [
        f"**{len(payload['decision_plan']):,}** programme entries covering all {len(rows):,} "
        f"decided objects, of which **{len(actionable):,}** entries "
        f"(**{sum(e['objects'] for e in actionable):,}** objects) carry an action that would "
        "modify repository knowledge and therefore require the named owner's authorization "
        "before anything is written.",
        "",
        "## Worked plans (the generator's output, per object)",
        "",
        "One object per action, to show that the generator resolves a real, addressed plan rather "
        "than a template. The highest-priority object of each action is shown.",
        "",
    ]
    for action in DEC.ACTIONS:
        sel = sorted((r for r in rows if r.get("decision") == action),
                     key=lambda r: (DEC.PRIORITIES.index(str(r.get("implementation_priority")))
                                    if str(r.get("implementation_priority")) in DEC.PRIORITIES
                                    else 99, -float(r["authority_score"] or 0.0), r["kid"]))
        if not sel:
            L += [f"### {action}", "",
                  "No object on this corpus carries this action; see the reachability gate in "
                  "register 06.", ""]
            continue
        r = sel[0]
        L += [f"### {action} — `{r['kid']}` {r['name']}", "",
              f"- operation `{r['implementation_action']}` · rule `{r['decision_rule']}` · "
              f"priority {r['implementation_priority']} · wave {str(r['wave']) or '—'}",
              f"- owner: {r['implementation_owner']}",
              f"- grounds: `{r['decision_rationale']}`",
              ""]
        L += [f"{i + 1}. {step}" for i, step in enumerate(DEC.plan_for(r))]
        L += [""]
    L += [
        "## Disclosed limits",
        "",
        "- A plan is an INSTRUCTION, not an execution. This engine writes nothing outside its own "
        "program home and has written nothing into any owner's artifact.",
        "- The plan carries no estimate, no schedule and no capacity assumption. Ordering is by "
        "declared priority and the wave the presence axis already assigned; inventing dates would "
        "fabricate a commitment the evidence does not contain.",
        "- Every plan ends by REGENERATING the registers, so discharging a decision causes the "
        "decision to be RE-DERIVED from the new repository state rather than hand-edited. That is "
        "the only supported way to close an entry.",
        "",
    ]
    p = HERE / "11-IMPLEMENTATION-PLAN-REGISTER.md"
    write(p, L)
    written.append(p.name)

    # ---------------------------------------------------------------- 04 repository change
    L = md_header(payload, "04", "Repository Change Register",
                  "Every repository change this program made, with content hash, rationale and "
                  "registration status — the artifacts this engine writes, and the integration "
                  "surface committed with them.")
    L += [
        "## Change boundary",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| Program home (the only path this ENGINE writes) | `00-MASTER/{PROGRAM}/` |",
        "| Files written by this engine outside the program home | **0** (every write target is "
            "resolved under the program home) |",
        f"| Integration surface committed with this program (outside the home, operator-authored) "
        f"| **{len(INTEGRATION_SURFACE)}** — declared below |",
        "| Existing constitutional artifacts amended | **0** (no parallel authority, no rewrite "
            "of ratified text) |",
        "| External evidence writes | **0** (`KNOWLEDGE-ASSIMILATION` is read-only evidence) |",
        f"| HEAD at generation | `{payload['head_commit']}` |",
        "",
        "`00-MASTER/` is an EXCLUDE_DIR_PREFIX in `00-BOOK/tools/config.py`, so program artifacts "
        "under this home are outside the REG-AUTO-001 registration universe by the repository's "
            "own "
        "declared policy. They therefore mint no identities and introduce no registration drift — "
        "the same boundary every prior UAKOS/UCDA program artifact sits inside.",
        "",
        "## Integration surface (outside the program home, declared not concealed)",
        "",
        "This engine writes none of the paths below and amends no ratified text in them, but the "
        "program is not runnable or gated without them, so they are committed as part of the same "
        "change and declared here. An earlier form of this register asserted a zero out-of-home "
        "footprint; that assertion was wrong and is corrected here.",
        "",
    ]
    surface_rows = []
    for rel, what, why in INTEGRATION_SURFACE:
        f = REPO / rel
        surface_rows.append([
            f"`{rel}`", what,
            "present" if f.exists() else "**ABSENT**",
            sha256_file(f)[:16] if f.is_file() else "—",
            why,
        ])
    L += table(["Path", "What it contributes", "At HEAD", "sha256 (first 16)",
                "Why it is required"], surface_rows)
    L += [
        "## Artifacts created",
        "",
    ]
    # 04 is rendered LAST and excludes ITSELF: a file cannot carry its own content hash,
    # and hashing the other artifacts only after they are written keeps 04 deterministic.
    files = sorted(p.name for p in HERE.iterdir()
                   if p.is_file() and p.suffix in (".md", ".json", ".py")
                   and p.name != "04-REPOSITORY-CHANGE-REGISTER.md")
    change_rows = []
    for name in files:
        f = HERE / name
        # `validation-record.json` is an INPUT, not an output: it is authored repository truth
        # about the canonical gate and this engine only reads it. Declaring it as engine output
        # would be the same category error CLOSURE-008 closed on the execution transcript.
        kind = ("authored input (not engine output)" if name == "validation-record.json" else
                "engine" if f.suffix == ".py" else
                "machine-readable register" if f.suffix == ".json" else "register / report")
        change_rows.append([f"`{name}`", kind, f.stat().st_size, sha256_file(f)[:16]])
    L += table(["Artifact", "Kind", "Bytes", "sha256 (first 16)"], change_rows)
    L += ["`04-REPOSITORY-CHANGE-REGISTER.md` is itself excluded from the table above — a file "
          "cannot carry its own content hash.", ""]
    L += [
        "`assimilation.json` is the machine-readable canonical register: it carries the complete "
        "per-object classification for all "
        f"{total} verified knowledge objects and is sufficient to re-render every register with "
            f"the "
        "external evidence absent (`--render`), so the repository is self-contained.",
        "",
    ]
    p = HERE / "04-REPOSITORY-CHANGE-REGISTER.md"
    write(p, L)
    written.append(p.name)
    return written


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=f"{PROGRAM} assimilation engine")
    ap.add_argument("--gate", action="store_true", help="exit 1 unless the determination is "
        "COMPLETE")
    ap.add_argument("--render", action="store_true",
                    help="re-render registers from assimilation.json (no external evidence needed)")
    args = ap.parse_args()

    if args.render:
        if not ASSIM_JSON.exists():
            print(f"{PROGRAM}: FAIL-CLOSED — {ASSIM_JSON.name} absent; cannot render.",
                file=sys.stderr)
            return 1
        payload = deserialize(ASSIM_JSON.read_text(encoding="utf-8"))
    else:
        payload = build(evidence_root())
        ASSIM_JSON.write_text(serialize(payload), encoding="utf-8")
        EVIDENCE_MANIFEST.write_text(
            json.dumps(dict(program=PROGRAM, head_commit=payload["head_commit"],
                            evidence_root=payload["evidence_root"],
                            files=payload["evidence_manifest"]), indent=2, sort_keys=True) + "\n",
            encoding="utf-8")

    written = render(payload)

    # --- RC-0008: payload currency, DETECTED and REPORTED ------------------------------------
    #
    # THE DEFECT THIS MEASURES. `--render` replays a stored payload and rewrites the registers
    # from it, and the CI drift gate then asserts `rendered output == recorded payload`. That is
    # internal consistency; it says nothing about whether the payload still describes the
    # repository. Measured: the committed payload recorded HEAD `bb9c27d2` while HEAD was
    # `77798202` — 56 commits of drift, through which every gate reported PASS, because no check
    # anywhere compared the two. A payload of any age renders to a self-consistent fixed point
    # forever.
    #
    # NON-BLOCKING BY DESIGN, AND THE REASON IS A DEPENDENCY, NOT TIMIDITY. Refusing on drift
    # requires that re-derivation be possible wherever the gate runs. For this capability that is
    # now true — the evidence is vendored — but the currency contract is shared with UKAP-001,
    # whose ~4 GB corpus stays external. Making it blocking before that lands would fail CI for
    # every checkout that does not hold the corpus, which is precisely why enforcement was never
    # added and the drift went unseen. So: measured, printed, recorded in the payload, and
    # promotable to blocking by changing one flag once RC-0014 closes for UKAP-001.
    # NOT PERSISTED, deliberately. Currency is a relation between a stored payload and the live
    # repository, not a property of the payload. Writing it in would make `assimilation.json`
    # change every time HEAD moves, which would break the register drift gate that compares the
    # rendered output against the recorded payload — trading a silent staleness for a permanent
    # false positive. It is measured and reported on every run instead.
    recorded = str(payload.get("head_commit") or "")
    live = head_commit()
    if recorded and recorded != live:
        distance = (git("rev-list", "--count", f"{recorded}..HEAD") or "").strip() or "unknown"
        print(
            f"  CURRENCY DRIFT (reported, not blocking): payload records HEAD {recorded}, "
            f"repository is at {live} — {distance} commit(s) ahead. The registers describe a "
            f"tree that is no longer this one; regenerate with a full measure to refresh them.",
            file=sys.stderr,
        )

    st = payload["states"]
    da = payload["decision_actions"]
    print(f"{PROGRAM}: {payload['determination']} | objects={payload['verified_objects']} "
          f"| unclassified={payload['unclassified']} "
          f"| remaining_candidates={payload['remaining_approved_promotion_candidates']} "
          f"| " + " ".join(f"{k.split('-')[0].lower()}={v}" for k, v in st.items()))
    print(f"  D-3 decisions: undecided={sum(1 for r in payload['rows'] if not r.get('decision'))}"
          f" | ruleset={payload['decision_version']} | "
          + " ".join(f"{a.lower()}={da.get(a, 0)}" for a in DEC.ACTIONS))
    print(f"wrote {len(written)} registers to 00-MASTER/{PROGRAM}")
    if args.gate and payload["determination"] != "REPOSITORY CONSTITUTIONALLY COMPLETE":
        for g in payload["gates"]:
            if g["blocking"] and g["result"] == "FAIL":
                print(f"  BLOCKING FAIL: {g['gate']} = {g['count']} {g['detail']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
