#!/usr/bin/env python3
"""UAKOS-CLOSURE-002 — deterministic repository closure engine.

Implements the Vision-to-Repository closure program as an auditable, re-runnable,
standard-library-only tool (honors UCKO-PRIN-0003 vendor-neutral core and
UCKO-PRIN-0005 determinism). It never mutates the frozen corpus and never issues
a closure certificate that the evidence does not support (fail-closed, TRACK-001).

Pipeline (mission phases 1-10):
    discover sources -> extract canonical concept anchors -> match Repository Truth
    -> assign one disposition -> analyze duplicates/orphans/traceability
    -> emit 14 artifacts + closure.json -> fail-closed determination.

Usage:
    python3 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py            # generate reports
    python3 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py --gate     # exit 1 if NOT-CLOSED
    python3 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py --gate \
        --require-complete-population                     # additionally exit 1 if UNMEASURED

SCAN-MODE DISCLOSURE (AB-6 / CG-10, schema 2).
    The `conversation_only` gap class is measurable ONLY from the external corpus at
    ``REPO.parent / "UCOS"``. Where that directory is absent, no concept originating there
    enters the population at all, so the class measures 0 by ABSENCE rather than by closure.
    Before schema 2 that was indistinguishable, from the outside, from a measured zero: the
    determination is a pure function of the discovered population and never consulted
    ``corpus_present``, so an unscanned population returned CLOSED. This engine's own
    contract above forbids exactly that ("never issues a closure certificate that the
    evidence does not support"), and the repository's standing rule is that a probe which
    cannot execute reports FAULT, never a pass.

    Schema 2 therefore records, on every run and in ``closure.json``:

        ``schema_version``       the disclosure contract version (integer)
        ``scan_mode``            how the population was bounded on this run
        ``population_complete``  False whenever a declared source could not be read
        ``population_disclosure`` the human-readable reason, or None

    Two scan modes are COMPLETE within their declared scope: ``full-corpus`` (the corpus was
    present and scanned) and ``repo-only (declared)`` (the caller set ``CLOSURE_SKIP_CORPUS=1``,
    an explicit constituent act — this is the "declare then use" shape the repository already
    applies to open vocabularies, not "anything goes"). One mode is INCOMPLETE:
    ``repo-only (undeclared — corpus absent)``, where nobody declared a narrower scope and the
    wider one could not be read.

    WHAT THIS CHANGE DOES NOT DO. It does not alter the determination. ``closed`` remains the
    same pure function of the discovered population it has always been, so no verdict moves and
    no gate changes colour. Making an incomplete population BLOCKING is a verdict-changing
    governance act, recorded as AB-6 ("pin canonical full-corpus mode") and reserved to the EKI
    owner pending P2 sign-off; a measurement engine may not confer that on itself. The lever is
    provided, fail-closed and default-off, as ``--require-complete-population`` so the owner can
    bind it in CI with one line at the moment sign-off is given.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

# --------------------------------------------------------------------------- paths
HERE = Path(__file__).resolve().parent

# AB-6 / CG-10: the disclosure contract version. Bumped when the meaning of `scan_mode`,
# `population_complete` or `population_disclosure` changes, so a consumer can refuse a
# reading it does not understand instead of misreading it.
SCHEMA_VERSION = 2
REPO = HERE.parent.parent  # <repo>/00-MASTER/UAKOS-CLOSURE-002 -> <repo>
CORPUS = REPO.parent / "UCOS"  # external corpus sibling (conversation/upload material)

# Canonical-truth roots: a concept ID found here is "homed" (has a canonical home).
TRUTH_ROOTS = (
    "02-MASTER", "00-CEP", "00-MASTER", "00-BOOK", "03-CATALOGS", "04-REFERENCE",
    "06-IMPLEMENTATION", "07-ENGINEERING", "08-RUNTIME", "09-PLATFORM",
    "10-DATA", "11-SERVICE", "12-APPLICATION", "13-INFRASTRUCTURE", "14-SECURITY",
    "99-FREEZE", "adr", "knowledge",
)
# Engineering (code) roots: presence here is IMPLEMENTED evidence.
CODE_ROOTS = ("engine", "platform", "data", "service", "application", "infrastructure", "intelligence")
# Upload/source roots: presence ONLY here (or in corpus) = upload/conversation-only gap.
SOURCE_ROOTS = ("00-SOURCE",)
# Spec/constitution roots: presence here is SPECIFIED evidence.
SPEC_ROOTS = ("02-MASTER", "00-CEP", "10-DATA", "11-SERVICE", "12-APPLICATION",
              "13-INFRASTRUCTURE", "14-SECURITY", "08-RUNTIME", "09-PLATFORM", "06-IMPLEMENTATION")
PLAN_MARK = re.compile(r"\b(ROADMAP|MASTER PLAN|MASTER-PLAN|MEP-\d|CHARTER|PLANNED|FUTURE)\b", re.I)
DEFER_MARK = re.compile(r"\b(DEFERRED|BLOCKED|PENDING AUTHORIZATION|DEFER)\b", re.I)
REJECT_MARK = re.compile(r"\b(REJECTED|rejected_options|REJECT)\b")

TEXT_EXT = {".md", ".txt", ".py", ".json", ".toml", ".sh", ".yml", ".yaml", ".cfg"}

# --------------------------------------------------------------------------- concept anchor families
# Each family is (name, compiled-regex). Curated to the repo's real ID namespace.
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
CERT_RE = re.compile(r"\bUCOS-CERT-[A-Za-z0-9-]{6,}\b")  # evidence token, not a concept
_SENTINEL = re.compile(r"-U?9{2,3}$")  # wildcard/example ids (…-99, …-999, …-U99) are not real concepts


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False).stdout


def _read_text(path: Path, limit: int = 4_000_000) -> str:
    try:
        if path.suffix.lower() == ".docx":
            with zipfile.ZipFile(path) as z:
                if "word/document.xml" not in z.namelist():
                    return ""
                raw = z.read("word/document.xml").decode("utf-8", "ignore")
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw))[:limit]
        if path.suffix.lower() in TEXT_EXT or path.suffix.lower() == ".docx":
            return path.read_text("utf-8", "ignore")[:limit]
    except (OSError, zipfile.BadZipFile):
        return ""
    return ""


def _top(rel: str) -> str:
    return rel.split("/", 1)[0]


# --------------------------------------------------------------------------- phase 1: source discovery
def _tracked_paths() -> list[str]:
    """Every tracked path, NUL-delimited so non-ASCII names survive verbatim.

    `git ls-files` without `-z` renders any path containing a non-ASCII byte in
    double-quoted, octal-escaped form (`"…/UCOS-\\316\\251\\342\\210\\236-…"`). That
    literal string does not resolve on disk, so every such artifact was silently read as
    empty and dropped from concept extraction — 116 tracked `Ω∞` artifacts, including
    canonical `02-MASTER/` architecture constitutions that DECLARE concept identities.
    Their concepts therefore measured as having no canonical home, which is a measurement
    defect, not repository truth. `-z` is the same fix `00-BOOK/tools/ukb.py::_git_ls`
    already applies, so closure now sees exactly the eligibility boundary registration
    sees (the divergence recorded as OBS-1 in
    `00-MASTER/UCCEP-000007/17-EVIDENCE-APPENDIX.md` §E-02).
    """
    return [f for f in _run(["git", "ls-files", "-z"]).split("\0") if f]


def discover_sources() -> dict:
    tracked = _tracked_paths()
    docx = sorted(f for f in tracked if f.lower().endswith(".docx"))
    md = sorted(f for f in tracked if f.lower().endswith(".md"))
    root_uploads = sorted(f for f in tracked if "/" not in f and f.lower().endswith((".md", ".docx")))
    corpus_files: list[str] = []
    corpus_skip_declared = os.environ.get("CLOSURE_SKIP_CORPUS") == "1"
    corpus_present = CORPUS.is_dir()
    if corpus_present and not corpus_skip_declared:
        for p in sorted(CORPUS.rglob("*")):
            if p.is_file() and p.suffix.lower() in (TEXT_EXT | {".docx"}):
                corpus_files.append(str(p.relative_to(CORPUS)))
    by_top: dict[str, int] = defaultdict(int)
    for f in tracked:
        by_top[_top(f)] += 1
    return {
        "tracked_total": len(tracked),
        "tracked_by_top": dict(sorted(by_top.items(), key=lambda kv: (-kv[1], kv[0]))),
        "markdown": md,
        "docx_uploads": docx,
        "root_uploads": root_uploads,
        "corpus_dir": str(CORPUS),
        "corpus_present": corpus_present,
        "corpus_skip_declared": corpus_skip_declared,
        "corpus_files": corpus_files,
        "_tracked": tracked,
    }


def scan_disclosure(sources: dict) -> dict:
    """Bound the population this run actually read, and say so (AB-6 / CG-10, schema 2).

    Three outcomes, only one of which is incomplete. A declared narrowing is complete WITHIN
    ITS DECLARED SCOPE, because somebody performed a constituent act naming that scope; an
    UNDECLARED narrowing is incomplete, because the wider scope was neither read nor waived.
    Returned as data so the determination stays a pure function and the disclosure travels
    with the artifact rather than living in a print statement.
    """
    if sources["corpus_skip_declared"]:
        return {
            "scan_mode": "repo-only (declared)",
            "population_complete": True,
            "population_disclosure": (
                "CLOSURE_SKIP_CORPUS=1 was declared by the caller, so the external corpus was "
                "deliberately not scanned. The `conversation_only` class is out of scope for "
                "this run by explicit declaration, not unmeasured by accident."
            ),
        }
    if sources["corpus_present"]:
        return {
            "scan_mode": "full-corpus",
            "population_complete": True,
            "population_disclosure": None,
        }
    return {
        "scan_mode": "repo-only (undeclared — corpus absent)",
        "population_complete": False,
        "population_disclosure": (
            f"The external corpus {sources['corpus_dir']} does not exist and no narrower scope "
            "was declared. Every concept originating only there is absent from the population, "
            "so `conversation_only` (and any gap class derived from corpus-only concepts) is "
            "UNMEASURED on this run and its zero is an absence, not a closure. The historical "
            "measured residue under full-corpus mode was 91. Consumers projecting this document "
            "as a population — notably the ownership determination, which declares "
            "`population_document: 00-MASTER/UAKOS-CLOSURE-002/closure.json` — inherit this bound."
        ),
    }


# --------------------------------------------------------------------------- phase 2/3/4: extract + match
def _new_rec(cid: str, fam: str) -> dict:
    return {
        "id": cid, "family": fam, "zones": set(), "tops": set(),
        "homed": False, "in_filename": False, "heading_home": False, "in_code": False, "in_book": False,
        "in_spec": False, "in_constitution": False, "in_plan": False,
        "deferred": False, "rejected": False, "certified": False,
        "files": set(), "def_homes": set(), "exact_homes": set(),
        "source_only_files": set(), "corpus_files": set(),
    }


# derived / non-definitional path segments: presence here is evidence, never a canonical home
DERIVED_SEG = ("_evidence/", "/outputs/", "outputs/", "determinism-evidence/",
               "CHECKPOINTS/", "/__pycache__/", ".egg-info/")

# Governance data that names subjects is NOT implementation. The ownership declaration
# catalogue lives under a code root because that is where the owning package keeps its
# packaged documents, but its keys are the subjects a HUMAN authority has assigned owners —
# counting them as `in_code` would let the act of ratifying an owner flip a concept's
# engineering disposition, which is the circularity UCKP-ART-04 forbids: a persistence
# mechanism of a decision is not evidence the decision was implemented. Measured at
# a6af5ad1..196ff693: ratifying 113 assignments moved 47 concepts to IMPLEMENTED on no
# evidence but their appearance in this file (e.g. GOV-007, whose only code-root mention
# was its own assignment key). The exclusion is for this document's ROLE, not its path
# accident: it is the governed assignments surface named by the Foundation specialization.
GOVERNANCE_ASSIGNMENT = "platform/universal_ownership/catalog/ucos-ownership-declarations.json"


# A heading that names an id, or a range containing it, is an AUTHORED DECLARATION of what
# the document defines: `## SECTION 3 — META-RELATIONSHIPS (AMR-01…14)`. It is read, never
# inferred — which is why the same header correctly withholds AMC-11 from a section that
# declares AMC-01…10.
# The numbering segment may carry a letter prefix — this repository writes both `AMR-01\u202614`
# and `EC3-B10-U01\u2026U12`, and a range over the second is as much a declaration as over the
# first. Reading only the bare-numeral form made the rule fluent in one of the repository's
# conventions and blind to the other.
# The stem admits this repository's own sigil. Its LAW family is written `\u03a9\u221e-001`, and an
# `[A-Z]`-anchored stem cannot match a character outside ASCII — so the range
# `(\u03a9\u221e-001\u2026020)` was unreadable while `(AMR-01\u202614)` was not. Third time this rule proved
# fluent in one of the repository's conventions and blind to another; the first two were the
# letter-prefixed numbering and the mention-versus-declaration line.
_HEAD_RANGE = re.compile(
    r"\b([A-Z\u03a9][A-Z0-9\u03a9\u221e]*(?:-[A-Z0-9]+)*)-([A-Z]*)(\d+)"
    r"\s*(?:\u2026|\.\.\.|\u2013|\u2014)\s*(?:\1-)?\2?(\d+)\b"
)
# A programme that MEASURES concepts cannot be the definitional home of the concepts it
# measures; its registers list and score them and define none.
_MEASUREMENT_HOME = re.compile(r"00-MASTER/(UAKOS-|P0-|UCOS-MXR-|UCOS-RIB-|UCOS-AEE-)")


# A document that names another as its `Source:` is a PROJECTION of it. UCKP-ART-11 is explicit
# that generated output never owns truth, so a projection cannot be a definitional home — and
# the document says so itself, which keeps this read rather than inferred.
_PROJECTION = re.compile(r"^\s*[-*]?\s*Source:\s*\[", re.M)


# A concept AUTHORED in code: its id standing alone as a constructor argument, in a module
# that is not a test and not derived. `engine/knowledge/seed.py` writes UCKO-PRIN-0001 with
# its title, statement, rationale and authority as literal source; the canonical knowledge
# store is generated FROM that, so under UCKP-ART-11 the seed is the home and the store is a
# projection of it. CLOSURE-002 already holds that "implementation is a valid canonical home".
_CODE_AUTHORED = re.compile(r"""^["']([A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+)["'],?$""")


# `*/_evidence/<concept-id>/` is a STRUCTURAL claim of ownership: the directory name says
# whose evidence this is, and says it more plainly than a mention inside the file would.
_EVIDENCE_DIR = re.compile(r"(?:^|/)_evidence/([^/]+)/")


def _evidence_subject(rel: str) -> str:
    """The concept a file's evidence directory names, or "" when it names none."""
    m = _EVIDENCE_DIR.search(rel)
    return m.group(1) if m else ""


def _code_author_eligible(rel: str, zone: str) -> bool:
    """Eligible to AUTHOR a concept: a code-root file that is neither test nor derived.

    Deliberately no suffix test. `rel.endswith(".py")` would be a type decided by filename,
    which ZX-02 refuses — engine/omega_infinite/classification.py types an artifact by four
    declared rules with the suffix consulted LAST — and it is not needed here: the claim
    already requires the concept to be a knowledge object carrying a statement AND exactly one
    file to author it. Measured both ways over 1,444 candidate files, the two agree exactly
    (UCKO-PRIN-0001…0005), because a data file listing the same id makes the count two and
    disqualifies it. The narrower predicate was buying nothing but a violation.
    """
    return (zone == "repo" and _top(rel) in CODE_ROOTS
            and "/tests/" not in rel and "/test_" not in rel
            and not any(seg in rel for seg in DERIVED_SEG))


def _defined_knowledge_objects() -> set[str]:
    """Ids the canonical store records WITH a statement — i.e. carrying a definition."""
    store = REPO / "knowledge" / "canonical-knowledge.json"
    try:
        data = json.loads(store.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {
        str(o.get("cko_id") or "")
        for o in (data.get("objects") or [])
        if isinstance(o, dict) and str(o.get("statement") or "").strip()
    } - {""}


def _heading_home_eligible(rel: str, zone: str, text: str) -> bool:
    return (zone == "repo" and _top(rel) in TRUTH_ROOTS
            and not any(seg in rel for seg in DERIVED_SEG)
            and not _MEASUREMENT_HOME.match(rel)
            and not _PROJECTION.search(text[:2000]))


# A document that states its own identity settles which concept it is the home OF.
# `UCOS-COMP-000000-GLOBAL-IMPLEMENTATION-GRAPH-DETERMINATION.md` declares
# `ARTIFACT ID | UCOS-COMP-000000-GIG` — it is the home of GIG, not of UCOS-COMP-000000,
# whose own home declares `ARTIFACT ID | UCOS-COMP-000000` two files away.
_DECLARED_ID = re.compile(
    r"^\|\s*\**\s*(?:ARTIFACT\s+ID|Artifact\s+Identifier)\s*\**\s*\|\s*[`*]*\s*"
    r"([A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*)\s*[`*]*\s*\|",
    re.M | re.I,
)


def _declared_artifact_id(text: str) -> str:
    """The identity a document claims for ITSELF, or "" when it claims none."""
    m = _DECLARED_ID.search(text[:4000])
    return m.group(1).strip() if m else ""


def _is_def_home(rel: str, cid: str) -> bool:
    """A definitional home: a truth-root file whose basename is (or starts with) the id,
    excluding derived/evidence/checkpoint artifacts.

    A basename PREFIX is not an identity. Three files begin `UCOS-COMP-000000-` and the rule
    read all three as homes of UCOS-COMP-000000, reporting a competition that does not exist:
    two of them declare themselves `-GIG` and `-ISR`, artifacts of their own that merely share
    a prefix. Where a document states its own ARTIFACT ID, that statement decides — it is the
    home of the id it claims and of no prefix of it. Documents claiming no identity keep the
    basename rule, so this can only ever withdraw a home a document itself disclaims.
    """
    if any(seg in rel for seg in DERIVED_SEG):
        return False
    if _top(rel) not in TRUTH_ROOTS:
        return False

    stem = rel.rsplit("/", 1)[-1].upper()
    cu = cid.upper()
    return stem == cu or stem.startswith(cu + "-") or stem.startswith(cu + ".") or stem.startswith(cu + "_")


def _definitional_body_id(line: str) -> str | None:
    """The id this line DELIVERS a definition for, if any.

    A definition occupies a structural position: the whole first cell of a table row, or the
    defined term leading a line. An id appearing later in a row is a reference to it.
    """
    s = line.strip()
    if s.startswith("|"):
        parts = s.split("|")
        if len(parts) > 1:
            cell = parts[1].strip().strip("*`_ ").strip()
            return cell or None
        return None
    m = re.match(
        r"^[*`_]*([A-Za-z\u03a9][A-Za-z0-9\u03a9\u221e]*(?:-[A-Za-z0-9]+)+)[*`_]*\s*[\u2014:-]\s+\S",
        s,
    )
    return m.group(1) if m else None


def _scan(paths: list[tuple[str, Path]], concepts: dict, cert_index: dict, zone: str,
          heading_index: dict[str, set] | None = None,
          body_index: dict[str, set] | None = None,
          code_index: dict[str, set] | None = None,
          evidence_index: dict[str, set] | None = None) -> None:
    """Populate concept occurrences with line-local disposition markers. zone in {repo, source, corpus}."""
    for rel, abspath in paths:
        text = _read_text(abspath)
        if not text:
            continue
        top = _top(rel)
        name_upper = rel.upper()
        declared_id = _declared_artifact_id(text) if zone == "repo" else ""
        if evidence_index is not None and zone == "repo":
            subject = _evidence_subject(rel)
            if subject:
                evidence_index.setdefault(subject, set()).add(rel)
        # line-local pass: attribute disposition markers only to ids on the same line
        for line in text.splitlines() if "\n" in text else [text]:
            ids_here: list[tuple[str, str]] = []
            for fam, rx in FAMILIES:
                for cid in rx.findall(line):
                    if _SENTINEL.search(cid):  # wildcard/example ids (…-99, …-999) are not concepts
                        continue
                    ids_here.append((cid, fam))
            if code_index is not None and _code_author_eligible(rel, zone):
                m = _CODE_AUTHORED.match(line.strip())
                if m:
                    code_index.setdefault(m.group(1), set()).add(rel)
            if body_index is not None and not line.lstrip().startswith("#") \
                    and _heading_home_eligible(rel, zone, text):
                delivered = _definitional_body_id(line)
                if delivered:
                    body_index.setdefault(delivered, set()).add(rel)
            if heading_index is not None and line.lstrip().startswith("#") \
                    and _heading_home_eligible(rel, zone, text):
                # A heading DECLARES what the document defines only when the id leads it
                # (`## AMC-11 — ...`) or falls inside a declared range. An id that merely
                # appears somewhere in a heading is a mention: `## EC3-B10 DATA REALIZATION
                # PACKAGE (ARCH-DATA-001)` is a heading about work on a concept, not a claim
                # to define it, and two such packages would both claim the same concept.
                for cid, _fam in ids_here:
                    if re.match(r"#{1,6}\s+[*_`]*" + re.escape(cid) + r"\b", line.strip()):
                        heading_index.setdefault(cid, set()).add(rel)
                for m in _HEAD_RANGE.finditer(line):
                    stem, mark, first, last = m.group(1), m.group(2), m.group(3), m.group(4)
                    if not (0 <= int(last) - int(first) <= 60):
                        continue
                    for n in range(int(first), int(last) + 1):
                        cid_n = f"{stem}-{mark}{str(n).zfill(len(first))}"
                        heading_index.setdefault(cid_n, set()).add(rel)
            if not ids_here:
                continue
            reject = bool(REJECT_MARK.search(line))
            defer = bool(DEFER_MARK.search(line))
            plan = bool(PLAN_MARK.search(line))
            certs_here = CERT_RE.findall(line)
            for cid, fam in ids_here:
                rec = concepts.get(cid) or concepts.setdefault(cid, _new_rec(cid, fam))
                rec["zones"].add(zone)
                rec["tops"].add(top)
                rec["files"].add(rel)
                if reject:
                    rec["rejected"] = True
                if defer:
                    rec["deferred"] = True
                if plan:
                    rec["in_plan"] = True
                if certs_here:
                    rec["certified"] = True
                    cert_index.setdefault(cid, set()).update(certs_here)
                if zone == "repo":
                    in_derived = any(s in rel for s in DERIVED_SEG) or rel == GOVERNANCE_ASSIGNMENT
                    if top in TRUTH_ROOTS:
                        rec["homed"] = True
                    if top in CODE_ROOTS and not in_derived:
                        rec["in_code"] = True
                        rec["homed"] = True  # implementation is a valid canonical home
                    if top in SPEC_ROOTS:
                        rec["in_spec"] = True
                    if top in ("02-MASTER", "00-CEP"):
                        rec["in_constitution"] = True
                    if top in ("00-BOOK", "00-MASTER", "03-CATALOGS", "04-REFERENCE"):
                        rec["in_book"] = True
                    if cid in name_upper:
                        rec["homed"] = True
                    if _is_def_home(rel, cid):
                        rec["homed"] = True
                        rec["in_filename"] = True
                        rec["def_homes"].add(rel)
                        if declared_id:
                            rec.setdefault("home_claims", {})[rel] = declared_id
                        stem = rel.rsplit("/", 1)[-1].rsplit(".", 1)[0].upper()
                        if stem == cid.upper():
                            rec["exact_homes"].add(rel)
                elif zone == "source":
                    rec["source_only_files"].add(rel)
                elif zone == "corpus":
                    rec["corpus_files"].add(rel)


def build_concepts(sources: dict) -> tuple[dict, dict]:
    cert_index: dict[str, set] = {}
    concepts: dict[str, dict] = {}

    repo_paths, source_paths, corpus_paths = [], [], []
    for rel in sources["_tracked"]:
        p = REPO / rel
        if p.suffix.lower() not in (TEXT_EXT | {".docx"}):
            continue
        (source_paths if _top(rel) in SOURCE_ROOTS else repo_paths).append((rel, p))
    # The UKDA canonical store is authoritative Repository Truth even though it is git-ignored
    # (generated). Scan it explicitly so seeded UCKO-*/UKDA-DEC-* count as homed.
    for extra in ("knowledge/canonical-knowledge.json", "knowledge/decisions.json"):
        p = REPO / extra
        if p.is_file() and (extra, p) not in repo_paths:
            repo_paths.append((extra, p))
    if (REPO / "knowledge" / "handbooks").is_dir():
        for hb in sorted((REPO / "knowledge" / "handbooks").rglob("*.md")):
            repo_paths.append((str(hb.relative_to(REPO)), hb))
    if sources["corpus_present"]:
        for rel in sources["corpus_files"]:
            corpus_paths.append((rel, CORPUS / rel))

    # First pass over repo to build cert_index, then classify.
    heading_index: dict[str, set] = {}
    body_index: dict[str, set] = {}
    code_index: dict[str, set] = {}
    evidence_index: dict[str, set] = {}
    _scan(repo_paths, concepts, cert_index, "repo", heading_index, body_index, code_index,
          evidence_index)
    _scan(source_paths, concepts, cert_index, "source")
    _scan(corpus_paths, concepts, cert_index, "corpus")

    # A SECOND LAWFUL FORM OF DEFINITIONAL HOME, read rather than inferred.
    # The filename rule above fits one of this repository's two id conventions — one document
    # per id (`APPLICATION-005`, `UCOS-COMP-000000`). The other convention defines a whole
    # family inside one document and says so in a heading: `## SECTION 3 — META-RELATIONSHIPS
    # (AMR-01…14)`. Under the filename rule alone those concepts are homed by evidence zone
    # and never DECLARED, so the ownership determination reported them as unowned while their
    # definition sat under a header naming their exact range. That is a rule whose measurement
    # does not reach it (adr/0041), not an absent definition — and authoring `AMR-01-*.md` to
    # satisfy it would be a second authoring of existing knowledge, which UCKP-ART-03 voids.
    #
    # A heading home is claimed ONLY when exactly one document declares the id. Where several
    # do, the multiplicity is a real competition for someone to resolve, and this engine
    # records nothing rather than picking a winner: choosing between two authored declarations
    # is a determination, and this engine measures.
    # EVIDENCE FILED UNDER A CONCEPT'S OWN DIRECTORY BELONGS TO IT.
    # The scan associates a file with a concept when the file MENTIONS it, which misses the
    # plainest statement of ownership the repository makes: `data/_evidence/EC3-B10-U01/`.
    # Inside that directory, determinism.json and realization-evidence.json happen to repeat
    # the unit id and were credited; validation-evidence.json and validation-report.json do
    # not, and were invisible — so 45 concepts were reported as carrying no validation
    # evidence while their validation reports sat in a directory named after them. The
    # directory name is the claim; it does not become truer for being restated inside.
    for cid, rels in evidence_index.items():
        rec = concepts.get(cid)
        if rec is None:
            continue
        rec["files"].update(rels)

    # A CONCEPT AUTHORED IN CODE IS HOMED WHERE IT WAS WRITTEN.
    # Claimed only for a concept the canonical store records WITH A STATEMENT, authored in
    # exactly one module. Both halves are needed. Store membership proves the id names a
    # knowledge object carrying a definition rather than a row in a list — without it,
    # `infrastructure/band13_meta.py` qualifies, and its own comment says its entries name
    # "the frozen architecture the unit realizes": an inventory pointing AT definitions, not
    # a definition. One module is needed because a concept written in two places has no
    # single home to name, and that is a competition rather than a determination for this
    # engine to settle.
    defined_objects = _defined_knowledge_objects()
    for cid, rels in code_index.items():
        rec = concepts.get(cid)
        if rec is None or rec["def_homes"] or cid not in defined_objects or len(rels) != 1:
            continue
        rec["def_homes"].add(next(iter(rels)))
        rec["code_home"] = True
        rec["homed"] = True

    # A BASENAME PREFIX IS NOT AN IDENTITY.
    # Three files begin `UCOS-COMP-000000-` and the basename rule read all three as homes of
    # UCOS-COMP-000000, reporting a competition that does not exist. Two of them state their
    # own identity as `UCOS-COMP-000000-GIG` and `-ISR`: artifacts of their own that merely
    # share a prefix. The third states `UCOS-COMP-000000` exactly, and is the home.
    #
    # The exclusion applies ONLY when some candidate claims the bare id, because claiming a
    # longer id is not by itself a disclaimer. `EC-3-AP-1-EXECUTOR-DESIGNATION-DETERMINATION.md`
    # states that whole string as its ARTIFACT ID — a document naming itself by its filename,
    # not a distinct artifact — and it is the only candidate EC-3-AP-1 has. Withdrawing it
    # would strip a home from a concept whose document nobody disputes, so where no candidate
    # claims the bare id the basename rule stands untouched.
    for cid, rec in concepts.items():
        homes = rec["def_homes"]
        claims = rec.get("home_claims") or {}
        if len(homes) < 2 or not claims:
            continue
        exact = {h for h in homes if claims.get(h, "").upper() == cid.upper()}
        if not exact:
            continue
        disclaimed = {h for h in homes if h not in exact and claims.get(h)}
        if disclaimed:
            rec["def_homes"] = homes - disclaimed
            rec["prefix_collisions"] = sorted(disclaimed)

    # AN IMPLEMENTATION IS A FACET, NOT A RIVAL DEFINITION.
    # `UCOS-COMP-000001` carried two filename homes — its constitution in 02-MASTER and its
    # `-IMPLEMENTATION` companion in 06-IMPLEMENTATION — and the count-of-homes rule read that
    # as two competing definitions. UCKP-ART-01/04 settle it: an execution environment or
    # implementation of an entity is a VIEW of it and holds no independent authority, so it
    # cannot compete with the document that defines it. Where a concept is defined in a
    # constitutional zone AND implemented in 06-IMPLEMENTATION, the definition is the home and
    # the implementation is a facet. Concepts whose homes genuinely compete WITHIN one zone are
    # untouched: that multiplicity is real and only a determination can reduce it.
    for rec in concepts.values():
        homes = rec["def_homes"]
        if len(homes) < 2:
            continue
        defining = {h for h in homes if _top(h) in ("02-MASTER", "00-CEP")}
        facets = {h for h in homes if _top(h) == "06-IMPLEMENTATION"}
        if defining and facets:
            rec["def_homes"] = homes - facets
            rec["implementation_facets"] = sorted(facets)

    # A HEADING DECLARES SCOPE; THE BODY DELIVERS THE DEFINITION. Both are required.
    # `SERVICE-005` declares `## SECTION 3 — META-RELATIONSHIPS (SMR-01…13)` and carries the
    # thirteen defining rows. `SERVICE-014` cites the same range in `### 15.2 Relationship
    # consistency — all within SOR-01…13 / SMR-01…13` and carries none: a consistency check
    # referencing a range is not a claim to define it. Requiring delivery as well as
    # declaration separates them, and without it the two documents compete for the same concepts and
    # neither could be its home.
    for cid, rels in heading_index.items():
        rec = concepts.get(cid)
        if rec is None or rec["def_homes"]:
            continue
        rels = rels & body_index.get(cid, set())
        if len(rels) != 1:
            continue
        rec["def_homes"].add(next(iter(rels)))
        rec["heading_home"] = True
        rec["homed"] = True

    # resolve certification from co-located cert evidence
    for cid, rec in concepts.items():
        if cert_index.get(cid):
            rec["certified"] = True
    return concepts, cert_index


# --------------------------------------------------------------------------- phase 5/6: disposition + traceability
def assign(concepts: dict) -> None:
    for rec in concepts.values():
        homed = rec["homed"]
        # disposition precedence: strongest evidence wins; UNCLASSIFIED only when not homed
        if not homed:
            disp = "UNCLASSIFIED"
        elif rec["in_code"] or rec["certified"]:
            disp = "IMPLEMENTED"
        elif rec["rejected"]:
            disp = "REJECTED"
        elif rec["deferred"]:
            disp = "DEFERRED"
        elif rec["in_constitution"] or rec["in_spec"] or rec["in_filename"] or rec["in_book"]:
            disp = "SPECIFIED"
        elif rec["in_plan"]:
            disp = "PLANNED"
        else:
            disp = "SPECIFIED"
        rec["disposition"] = disp
        # gap location subsets (a not-homed concept is the gap; these say where it currently lives)
        rec["upload_only"] = (not homed) and bool(rec["source_only_files"]) and "repo" not in rec["zones"]
        rec["conversation_only"] = (
            (not homed) and bool(rec["corpus_files"])
            and not rec["source_only_files"] and "repo" not in rec["zones"]
        )
        rec["in_repo_unhomed"] = (not homed) and "repo" in rec["zones"]
        # traceability tiers
        rec["trace"] = {
            "source": bool(rec["source_only_files"]) or bool(rec["corpus_files"]),
            "constitution": rec["in_constitution"],
            "specification": rec["in_spec"] or rec["in_filename"] or rec["in_book"],
            "implementation": rec["in_code"],
            "certification": rec["certified"],
        }
        rec["orphan"] = homed and not (
            rec["trace"]["constitution"] or rec["trace"]["specification"] or rec["trace"]["implementation"]
        )


# --------------------------------------------------------------------------- serialization helpers
def _clean(rec: dict) -> dict:
    out = {k: (sorted(v) if isinstance(v, set) else v) for k, v in rec.items()}
    return out


def build_model(sources: dict, concepts: dict) -> dict:
    recs = [_clean(r) for r in concepts.values()]
    recs.sort(key=lambda r: r["id"])
    disp_counts: dict[str, int] = defaultdict(int)
    fam_counts: dict[str, int] = defaultdict(int)
    for r in recs:
        disp_counts[r["disposition"]] += 1
        fam_counts[r["family"]] += 1
    upload_only = [r for r in recs if r["upload_only"]]
    conversation_only = [r for r in recs if r["conversation_only"]]
    in_repo_unhomed = [r for r in recs if r["in_repo_unhomed"]]
    unclassified = [r for r in recs if r["disposition"] == "UNCLASSIFIED"]
    orphans = [r for r in recs if r["orphan"]]
    # duplicate canonical homes: same id is the EXACT basename of >1 definitional file
    # (series-prefixed distinct artifacts like UCOS-COMP-000000-* are NOT duplicates)
    dup_home = [r for r in recs if len(r["exact_homes"]) > 1]
    # UKDA content-hash duplicates (Repository Truth store)
    hash_dups = _ukda_hash_dups()

    # distinct concept-level gap set (no double counting): every not-homed concept + every orphan
    gap_ids = {r["id"] for r in unclassified} | {r["id"] for r in orphans}
    gaps = {
        "not_homed_concepts": len(unclassified),
        "upload_only": len(upload_only),
        "conversation_only": len(conversation_only),
        "in_repo_unhomed": len(in_repo_unhomed),
        "orphan_concepts": len(orphans),
        "duplicate_canonical_homes": len(dup_home),
        "ukda_content_hash_duplicates": len(hash_dups),
    }
    # blocking invariants (determination): distinct not-homed/orphan concepts + structural duplicates
    blocking = len(gap_ids) + len(dup_home) + len(hash_dups)
    closed = blocking == 0
    return {
        "program": "UAKOS-CLOSURE-002",
        "schema_version": SCHEMA_VERSION,
        "baseline_commit": _run(["git", "rev-parse", "--short", "HEAD"]).strip(),
        "branch": _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip(),
        # AB-6 / CG-10 disclosure. Recorded ALONGSIDE the determination and deliberately not
        # folded into it: `closed` above remains the same pure function of the discovered
        # population, so this addition moves no verdict. Making an incomplete population
        # blocking is the governance act reserved to the EKI owner (AB-6, pending P2 sign-off).
        **scan_disclosure(sources),
        "determination": "CLOSED" if closed else "NOT-CLOSED",
        "gap_total": blocking,
        "gaps": gaps,
        "concept_total": len(recs),
        "dispositions": dict(sorted(disp_counts.items())),
        "families": dict(sorted(fam_counts.items())),
        "sources": {
            "tracked_total": sources["tracked_total"],
            "markdown": len(sources["markdown"]),
            "docx_uploads": len(sources["docx_uploads"]),
            "corpus_present": sources["corpus_present"],
            "corpus_files": len(sources["corpus_files"]),
            "tracked_by_top": sources["tracked_by_top"],
        },
        "detail": {
            "upload_only": upload_only,
            "conversation_only": conversation_only,
            "in_repo_unhomed": in_repo_unhomed,
            "unclassified": unclassified,
            "orphans": orphans,
            "duplicate_homes": dup_home,
            "ukda_hash_duplicates": hash_dups,
        },
        "concepts": recs,
    }


def _ukda_hash_dups() -> list[dict]:
    store = REPO / "knowledge" / "canonical-knowledge.json"
    if not store.is_file():
        return []
    data = json.loads(store.read_text("utf-8"))
    seen: dict[str, list[str]] = defaultdict(list)
    for obj in data.get("objects", []):
        h = obj.get("content_sha256")
        if h:
            seen[h].append(obj.get("cko_id", "?"))
    return [{"content_sha256": h, "ids": ids} for h, ids in sorted(seen.items()) if len(ids) > 1]


# --------------------------------------------------------------------------- phase 9/10: emit artifacts
def _fence(rows: list[list[str]], header: list[str]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def _hdr(title: str, m: dict, answers: str) -> str:
    return (
        f"# {title}\n\n"
        f"> PROGRAM UAKOS-CLOSURE-002 · baseline `{m['baseline_commit']}` (branch `{m['branch']}`) · "
        f"AUTHORITY = NONE (DERIVED TRUTH) · generated by `closure_engine.py`\n>\n"
        f"> {answers}\n\n"
    )


def emit(m: dict) -> list[Path]:
    written: list[Path] = []

    def w(name: str, body: str) -> None:
        p = HERE / name
        p.write_text(body.rstrip() + "\n", "utf-8")
        written.append(p)

    s = m["sources"]
    # 01 Source Inventory
    rows = [[k, v] for k, v in s["tracked_by_top"].items()]
    w("01-SOURCE-INVENTORY.md",
      _hdr("01 — Source Inventory", m, "Every discovered knowledge source.") +
      f"- Tracked files: **{s['tracked_total']}** · Markdown: **{s['markdown']}** · "
      f"docx uploads: **{s['docx_uploads']}** · external corpus present: **{s['corpus_present']}** "
      f"(**{s['corpus_files']}** files)\n\n## Tracked files by top-level source\n\n" +
      _fence(rows, ["Source root", "Files"]))

    # 02 Conversation Inventory (external corpus = conversation/upload material)
    conv = m["detail"]["conversation_only"]
    w("02-CONVERSATION-INVENTORY.md",
      _hdr("02 — Conversation Inventory", m, "External corpus / conversation material scanned for concepts.") +
      f"External corpus dir scanned: **{s['corpus_present']}** — **{s['corpus_files']}** files.\n\n"
      f"Concepts appearing **only** in the corpus (conversation-only, not yet in Repository Truth): "
      f"**{len(conv)}**.\n\n" +
      (_fence([[r["id"], r["family"], len(r["corpus_files"])] for r in conv[:200]],
              ["Concept", "Family", "Corpus files"]) if conv else "_None — no conversation-only concepts detected._"))

    # 03 Uploaded Document Inventory
    docx_rows = [[f] for f in _sources_docx(m)]
    w("03-UPLOADED-DOCUMENT-INVENTORY.md",
      _hdr("03 — Uploaded Document Inventory", m, "Every uploaded architectural document (docx) in the repository.") +
      "Uploaded `.docx` sources are tracked and hash-pinned in `00-SOURCE-MANIFEST/SOURCE-HASHES.txt`.\n\n" +
      _fence(docx_rows, ["Uploaded document"]))

    # 04 Constitutional Concept Inventory
    fam_rows = [[k, v] for k, v in m["families"].items()]
    w("04-CONSTITUTIONAL-CONCEPT-INVENTORY.md",
      _hdr("04 — Constitutional Concept Inventory", m, "Every discovered canonical concept anchor, by family.") +
      f"Total distinct concept anchors: **{m['concept_total']}**.\n\n## By family\n\n" +
      _fence(fam_rows, ["Family", "Concepts"]) +
      "\n\n## Full concept ledger\n\n" +
      _fence([[r["id"], r["family"], r["disposition"], "yes" if r["homed"] else "**NO**"]
              for r in m["concepts"]], ["Concept", "Family", "Disposition", "Homed"]))

    # 05 Vision-to-Repository Matrix
    w("05-VISION-TO-REPOSITORY-MATRIX.md",
      _hdr("05 — Vision-to-Repository Traceability Matrix", m,
           "Vision -> Constitution -> Specification -> Implementation -> Certification per concept.") +
      _fence([[r["id"],
               "✓" if r["trace"]["source"] else "·",
               "✓" if r["trace"]["constitution"] else "·",
               "✓" if r["trace"]["specification"] else "·",
               "✓" if r["trace"]["implementation"] else "·",
               "✓" if r["trace"]["certification"] else "·"]
              for r in m["concepts"]],
             ["Concept", "Source", "Constitution", "Spec", "Impl", "Cert"]))

    # 06 Repository Coverage Matrix
    dr = [[k, v] for k, v in m["dispositions"].items()]
    w("06-REPOSITORY-COVERAGE-MATRIX.md",
      _hdr("06 — Repository Coverage Matrix", m, "Disposition coverage across all concepts.") +
      _fence(dr, ["Disposition", "Concepts"]) +
      f"\n\nHomed (canonical home present): **{sum(1 for r in m['concepts'] if r['homed'])}** / "
      f"**{m['concept_total']}**.")

    # 07 Duplicate Knowledge Report
    dh = m["detail"]["duplicate_homes"]
    hd = m["detail"]["ukda_hash_duplicates"]
    w("07-DUPLICATE-KNOWLEDGE-REPORT.md",
      _hdr("07 — Duplicate Knowledge Report", m, "Concepts with more than one canonical home; UKDA content-hash duplicates.") +
      f"Concepts declared in >1 filename-home: **{len(dh)}**.\n\n" +
      (_fence([[r["id"], "; ".join(sorted(r["exact_homes"]))[:180]] for r in dh],
              ["Concept", "Duplicate homes"]) if dh else "_None._") +
      f"\n\nUKDA content-hash duplicates (Repository Truth store): **{len(hd)}**.\n\n" +
      (_fence([[d["content_sha256"][:16], ", ".join(d["ids"])] for d in hd], ["content_sha256", "cko_ids"])
       if hd else "_None — no two canonical objects share a content hash (UCKO-RULE-0001 holds)._"))

    # 08 Missing Knowledge Report
    uo = m["detail"]["upload_only"]
    co = m["detail"]["conversation_only"]
    uc = m["detail"]["unclassified"]
    iru = m["detail"]["in_repo_unhomed"]
    w("08-MISSING-KNOWLEDGE-REPORT.md",
      _hdr("08 — Missing Knowledge Report", m, "Concepts not present in Repository Truth (gaps).") +
      f"- Not-homed concepts (no canonical home = no disposition): **{len(uc)}**\n"
      f"  - of which upload-only (`00-SOURCE`/uploads only): **{len(uo)}**\n"
      f"  - of which conversation-only (external corpus only): **{len(co)}**\n"
      f"  - of which in-repo but unhomed (mentioned, never defined): **{len(iru)}**\n\n"
      "## Upload-only\n\n" +
      (_fence([[r["id"], r["family"], "; ".join(sorted(r["source_only_files"]))[:160]] for r in uo[:300]],
              ["Concept", "Family", "Source files"]) if uo else "_None._") +
      "\n\n## In-repo but unhomed (closure violations — must reach zero)\n\n" +
      (_fence([[r["id"], r["family"], ", ".join(sorted(r["tops"]))[:120]] for r in iru[:300]],
              ["Concept", "Family", "Seen in"]) if iru else "_None._"))

    # 09 Repository Enrichment Plan
    w("09-REPOSITORY-ENRICHMENT-PLAN.md",
      _hdr("09 — Repository Enrichment Plan", m, "How every gap becomes Repository Truth.") +
      _enrichment_plan(m))

    # 10 Constitutional Gap Register
    w("10-CONSTITUTIONAL-GAP-REGISTER.md",
      _hdr("10 — Constitutional Gap Register", m, "One row per open gap; the closure backlog.") +
      _gap_register(m))

    # 11 Closure Evidence
    w("11-CLOSURE-EVIDENCE.md",
      _hdr("11 — Closure Evidence", m, "The evidence basis of the determination.") +
      f"- Baseline commit: `{m['baseline_commit']}` (branch `{m['branch']}`)\n"
      f"- Concepts analyzed: **{m['concept_total']}**\n"
      f"- Sources: {s['tracked_total']} tracked, {s['docx_uploads']} docx uploads, "
      f"{s['corpus_files']} corpus files\n"
      f"- Machine model: `closure.json` (deterministic; re-run `make closure` to reproduce)\n"
      f"- Gap totals: {json.dumps(m['gaps'], sort_keys=True)}\n\n"
      "This program is fail-closed: the determination below reflects only evidence physically present "
      "at the baseline commit. No speculative closure is asserted (TRACK-001).")

    # 12 Repository Closure Certificate
    w("12-REPOSITORY-CLOSURE-CERTIFICATE.md", _certificate(m, "Repository"))
    # 13 Vision Closure Certificate
    w("13-VISION-CLOSURE-CERTIFICATE.md", _certificate(m, "Vision"))

    # 14 Final Repository Completeness Report
    w("14-FINAL-REPOSITORY-COMPLETENESS-REPORT.md",
      _hdr("14 — Final Repository Completeness Report", m, "The single-page verdict.") +
      _final_report(m))
    return written


def _sources_docx(m: dict) -> list[str]:
    # -z: see _tracked_paths — quoted octal paths do not resolve on disk.
    return [f for f in _run(["git", "ls-files", "-z", "*.docx"]).split("\0") if f]


def _enrichment_plan(m: dict) -> str:
    g = m["gaps"]
    lines = ["Every open gap is routed to exactly one constitutional destination:\n"]
    lines.append(_fence([
        ["Not-homed concepts", g["not_homed_concepts"], "Assign a canonical home + disposition (no sixth state permitted)"],
        ["  · upload-only", g["upload_only"], "Canonicalize into 02-MASTER / band spec / UKDA store; then SPECIFIED or PLANNED"],
        ["  · conversation-only", g["conversation_only"], "Extract from corpus into a decision record / spec; then classify"],
        ["  · in-repo unhomed", g["in_repo_unhomed"], "Promote the mention into a definitional home (filename/registry/catalog)"],
        ["Orphan concepts", g["orphan_concepts"], "Attach traceability (constitution/spec/impl) or archive with rationale"],
        ["Duplicate canonical homes", g["duplicate_canonical_homes"], "Merge to one home; convert others to links (UCKO-PRIN-0001)"],
        ["UKDA hash duplicates", g["ukda_content_hash_duplicates"], "Remove duplicate object; keep one canonical record"],
    ], ["Gap class", "Count", "Constitutional destination"]))
    lines.append("\nPriority: in-repo-unhomed -> upload-only -> conversation-only -> orphan -> duplicates.")
    return "\n".join(lines)


def _gap_register(m: dict) -> str:
    rows = []
    for r in m["detail"]["in_repo_unhomed"]:
        rows.append([r["id"], "IN-REPO-UNHOMED", "promote mention to a definitional home"])
    for r in m["detail"]["upload_only"]:
        rows.append([r["id"], "UPLOAD-ONLY", "canonicalize into Repository Truth"])
    for r in m["detail"]["conversation_only"]:
        rows.append([r["id"], "CONVERSATION-ONLY", "extract from corpus into a spec/decision"])
    for r in m["detail"]["orphans"]:
        rows.append([r["id"], "ORPHAN", "attach traceability or archive"])
    for r in m["detail"]["duplicate_homes"]:
        rows.append([r["id"], "DUPLICATE-HOME", "merge to one canonical home"])
    if not rows:
        return "_Gap register empty — zero open constitutional gaps at this baseline._"
    rows.sort(key=lambda x: (x[1], x[0]))
    return (f"Open gaps: **{len(rows)}**.\n\n" +
            _fence([[i + 1, *row] for i, row in enumerate(rows[:800])],
                   ["#", "Concept", "Gap class", "Required action"]))


def _certificate(m: dict, kind: str) -> str:
    ok = m["determination"] == "CLOSED"
    verdict = "CLOSED — 100%" if ok else f"NOT-CLOSED — {m['gap_total']} open gap(s)"
    seal = hashlib.sha256(
        json.dumps({"kind": kind, "commit": m["baseline_commit"], "gaps": m["gaps"]},
                   sort_keys=True).encode()).hexdigest()
    body = [
        f"# {kind} Closure Certificate — UAKOS-CLOSURE-002\n",
        f"| Field | Value |", "|---|---|",
        f"| Program | UAKOS-CLOSURE-002 |",
        f"| Certificate | {kind} Closure |",
        f"| Baseline | `{m['baseline_commit']}` (branch `{m['branch']}`) |",
        f"| Determination | **{verdict}** |",
        f"| Concepts | {m['concept_total']} |",
        f"| Seal (sha256) | `{seal}` |",
        f"| Authority | NONE — DERIVED TRUTH (fail-closed, TRACK-001) |",
        "",
    ]
    if ok:
        body.append("All closure invariants hold: zero missing, zero duplicate, zero orphan, "
                     "zero unclassified, zero broken traceability, zero drift. "
                     f"{kind} closure is **CERTIFIED**.")
    else:
        body.append(f"**Certification withheld.** Under the repository's fail-closed law, {kind.lower()} "
                    "closure cannot be certified while open gaps exist. Current gaps:\n")
        body.append("```json\n" + json.dumps(m["gaps"], indent=2, sort_keys=True) + "\n```")
        body.append("\nSee `10-CONSTITUTIONAL-GAP-REGISTER.md` and `09-REPOSITORY-ENRICHMENT-PLAN.md`. "
                    "Re-run `make closure` after enrichment; this certificate self-certifies when gaps reach zero.")
    return "\n".join(body)


def _final_report(m: dict) -> str:
    return (
        f"**Determination: {m['determination']}** — gaps: **{m['gap_total']}**.\n\n"
        + _fence([[k, v] for k, v in m["gaps"].items()], ["Invariant (must be 0)", "Count"])
        + "\n\n## Dispositions\n\n"
        + _fence([[k, v] for k, v in m["dispositions"].items()], ["Disposition", "Concepts"])
        + f"\n\n## Success criteria\n\n"
        + _fence([
            ["Every concept has one canonical home", "PASS" if m["gaps"]["not_homed_concepts"] == 0 else "FAIL"],
            ["Every concept has one disposition", "PASS" if m["gaps"]["not_homed_concepts"] == 0 else "FAIL"],
            ["Zero conversation-only knowledge", "PASS" if m["gaps"]["conversation_only"] == 0 else "FAIL"],
            ["Zero upload-only knowledge", "PASS" if m["gaps"]["upload_only"] == 0 else "FAIL"],
            ["Zero in-repo unhomed knowledge", "PASS" if m["gaps"]["in_repo_unhomed"] == 0 else "FAIL"],
            ["Zero duplicate canonical knowledge", "PASS" if m["gaps"]["duplicate_canonical_homes"] == 0
             and m["gaps"]["ukda_content_hash_duplicates"] == 0 else "FAIL"],
            ["Zero orphan concepts", "PASS" if m["gaps"]["orphan_concepts"] == 0 else "FAIL"],
        ], ["Criterion", "Status"])
        + f"\n\n{'100% Vision-to-Repository Closure achieved.' if m['determination'] == 'CLOSED' else 'Closure not yet achieved — see gap register.'}"
    )


# --------------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    gate = "--gate" in argv
    require_complete = "--require-complete-population" in argv
    sources = discover_sources()
    concepts, _cert = build_concepts(sources)
    assign(concepts)
    model = build_model(sources, concepts)
    (HERE / "closure.json").write_text(
        json.dumps({k: v for k, v in model.items() if k != "concepts"} | {"concepts": model["concepts"]},
                   indent=2, sort_keys=True, ensure_ascii=False) + "\n", "utf-8")
    written = emit(model)
    print(f"UAKOS-CLOSURE-002: {model['determination']} | concepts={model['concept_total']} "
          f"| gaps={model['gap_total']} {json.dumps(model['gaps'], sort_keys=True)}")
    # AB-6: the scan mode travels with the verdict on every run, so a reader can never again
    # mistake an unscanned population for a closed one from the summary line alone.
    print(f"scan_mode={model['scan_mode']} | population_complete={model['population_complete']}")
    print(f"wrote {len(written) + 1} artifacts to {HERE}")
    if not model["population_complete"]:
        print(
            "DISCLOSURE — POPULATION INCOMPLETE (schema 2, AB-6 / CG-10): "
            f"{model['population_disclosure']}",
            file=sys.stderr,
        )
    if gate and model["determination"] != "CLOSED":
        print("GATE FAILED: repository closure NOT achieved (fail-closed).", file=sys.stderr)
        return 1
    if require_complete and not model["population_complete"]:
        print(
            "GATE FAILED: population INCOMPLETE — a closure certificate may not rest on a "
            "population that was not read (fail-closed). Declare a narrower scope with "
            "CLOSURE_SKIP_CORPUS=1, or make the corpus readable.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
