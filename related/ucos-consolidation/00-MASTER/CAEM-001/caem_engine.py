#!/usr/bin/env python3
"""CAEM-001 — mandate disposition engine.

MISSION
    Take every mandate the six governing documents state, locate what already OWNS it,
    and disposition it. Five outcomes; only one of them is new construction.

AUTHORITY
    NONE — DERIVED TRUTH. This engine ratifies nothing, certifies nothing, occupies no
    tier and writes ONLY inside 00-MASTER/CAEM-001/.

WHY IT EXISTS
    CAEM-001 §1 performed this act for THIRTEEN concepts, by hand, and said why it had
    to be by hand: `21-CONCEPT-NORMALIZATION-REGISTER.md` and `23-SEMANTIC-EQUIVALENCE-
    MATRIX.md` state that no semantic matching is performed "because doing so would
    fabricate equivalence; equivalence is decided only by canonical-ID identity."

    Six documents mandate 1,449. Thirteen by hand does not scale to 1,449, and semantic
    matching is forbidden. This engine takes the only remaining road: it measures what
    can be measured — does a name occur, in what kind of file, and does anything NAME
    this concept — and then refuses to convert that measurement into an equivalence
    claim. Every disposition it derives is marked PROVISIONAL. Promotion to CONFIRMED
    is a human act recorded in the disposition file, never something this engine does.

    THE ERROR THIS ENGINE IS SHAPED AROUND. The first disposition pass used "zero grep
    hits" as the test for a genuine gap and returned 376 of them. CAEM-001's founding
    measurement is the refutation: the token `Fabric` occurs in ZERO of 4,981 tracked
    files, yet six of the eight Fabrics have canonical homes under other names. Acting
    on 376 would have authored hundreds of rival authorities — void under UCKP-ART-03,
    and the precise failure this instrument exists to prevent. Re-asking each zero-hit
    label against its HEAD NOUN's owner collapsed 376 to 19.

USAGE
    python3 00-MASTER/CAEM-001/caem_engine.py --measure   # slow: ~5k greps, writes 07
    python3 00-MASTER/CAEM-001/caem_engine.py --render    # fast: 07 -> 08
    python3 00-MASTER/CAEM-001/caem_engine.py --gate      # fail-closed checks
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PROGRAM = "CAEM-001"
AUTHORITY = "NONE (DERIVED TRUTH)"

# This engine is invoked as a script (verify.sh stage 6m, `make caem-gate`), so sys.path[0] is
# its own directory and `engine` does not resolve. The repository root must lead the path before
# the classifier below is importable -- the same insertion mcos_engine and lifecycle_closure_engine
# perform. Guarded, so an already-imported caller (the test that loads this by path) is unaffected.
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Structured data is recognised by the classifier, never by the filename. ZX-02 refuses a new
# `path.endswith(...)` decision: the type is derived through the four ordered rules with the
# suffix consulted last, so renaming an artifact cannot change what it is.
from engine.omega_infinite.artifact import DATASET, Artifact, Location  # noqa: E402
from engine.omega_infinite.classification import default_pipeline  # noqa: E402

CORPUS = HERE / "06-MANDATE-CORPUS.json"
DISPOSITION = HERE / "07-MANDATE-DISPOSITION.json"
REGISTER = HERE / "08-MANDATE-DISPOSITION-REGISTER.md"

# Registers whose NAME-SHAPED strings say what this repository owns. A concept named
# here has an owner; the same word inside a report is a mention, and the difference is
# the whole point of the exercise.
ANCHOR_SOURCES = (
    "00-BOOK/DATA/constitutional-authority-alignment.json",
    "00-BOOK/DATA/context-authority.json",
    "00-BOOK/DATA/id-ledger.json",
    "00-BOOK/DATA/evidence-universe.json",
    "00-BOOK/DATA/observation-universe.json",
    "00-BOOK/DATA/mutation-governance-boundary.json",
    "00-BOOK/DATA/generated-artifact-registry.json",
    "00-MASTER/UAKOS-CLOSURE-009/requirements.json",
)

WS = re.compile(r"[\s\-_./]+")


def norm(s: str) -> str:
    return WS.sub(" ", s.strip().lower()).strip()


# --- the classification rule ------------------------------------------------------------
# Negative-form claims assert an ABSENCE. Finding the token proves nothing and NOT finding
# it proves nothing either, so corpus search is the wrong instrument and saying so beats
# reporting ABSENT. The exceptions are disclosed rather than silent: a rule with hidden
# exceptions is a rule nobody can re-derive.
NEG = (" no ", " zero ", " without ", " never ", " not ", " nothing ", " independent of ")
NEG_EXCEPT = {
    "zero trust": "names a security architecture, not the absence of one",
    "not applicable": "a certification verdict value in the ARCH certification set",
    "what no longer exists": "a question about retirement, answerable by a retirement instrument",
}
GENERIC_HITS = 200


def is_assertion(label: str) -> bool:
    n = norm(label)
    if n in NEG_EXCEPT:
        return False
    return any(m in f" {n} " for m in NEG)


def _path_words(path: str) -> set[str]:
    """The words a path is made of, singularised.

    A concept is OWNED by a path only when the path carries every word of the concept as a
    WORD, not as a substring. `vr` occurs inside `srv`, `over`, and `vrm`, so a substring
    test reports seven owners for a concept nothing owns; `web` occurs inside `webhook` and
    `network`. The same rule the conformance suites use in `assert_named_by_nothing` —
    splitting the path into words and comparing word to word — because it is the only form
    under which an absence claim can be falsified in either direction.
    """
    word = ""
    words: set[str] = set()
    for char in path.lower():
        if char.isalnum():
            word += char
        elif word:
            words.add(word.rstrip("s"))
            word = ""
    if word:
        words.add(word.rstrip("s"))
    return words


def named_for(label: str, files: list[str]) -> list[str]:
    """The code files whose PATH names the concept, word for word.

    This is the ownership test `classify` rests IMPLEMENTED on. Counting files that merely
    CONTAIN the token inflates implementation: substring collisions and incidental mentions
    read as owners. Measured against the conformance suites, that inflation moved 30
    concepts the suites prove ABSENT — web, voice, vr, billing, taxation and 25 others —
    into IMPLEMENTED, and the register then reported them as paid while the executable
    evidence said nothing carried them.
    """
    words = {w.rstrip("s") for w in norm(label).replace("-", " ").split()}
    if not words:
        return []
    return [f for f in files if f.endswith(CODE_EXT) and words <= _path_words(f)]


def classify(
    label: str, hits: int, kinds: dict, anchored: bool, owned: list[str] | None = None
) -> str:
    """Seven outcomes, each a different KIND of knowledge or ignorance.

    ANCHORED is the one that carries the weight. A bare word like `Governance` occurs in
    2,616 files, hundreds of them code and tests, so a code-and-test rule fires on word
    frequency alone and says nothing about whether the REQUIREMENT is met. What can be
    established is whether the repository NAMES an owner for the concept — true, checkable,
    and honestly weaker than "implemented", so it gets its own status instead of being
    folded into one.

    IMPLEMENTED requires the stronger test passed in as `owned`: a code file whose PATH
    names the concept word-for-word. `kinds` counts files containing the token, and
    containing is not owning — `vr` is inside `srv`, so a containment test pays thirty
    concepts the conformance suites prove unowned. A concept with hits, tests and no
    named owner is SPECIFIED with test coverage, not IMPLEMENTED.
    """
    if is_assertion(label):
        return "ASSERTION"
    if hits == 0:
        return "ABSENT"
    if len(norm(label).split()) == 1 and hits > GENERIC_HITS:
        return "ANCHORED" if anchored else "UNDECIDABLE"
    if owned and kinds["code"] and (kinds["test"] or kinds["gate"]):
        return "IMPLEMENTED"
    if kinds["code"]:
        return "PARTIAL"
    return "SPECIFIED"


# --- measurement ------------------------------------------------------------------------
CODE_EXT = (".py", ".sh", ".ts", ".tsx", ".js", ".mjs", ".go", ".rs", ".sql")
GATE_FILES = ("Makefile", "verify.sh", "repo-ops.sh", "bootstrap.sh")


def variants(label: str) -> set[str]:
    words = norm(label).split()
    out = {label.strip(), " ".join(words), "-".join(words), "_".join(words), "".join(words)}
    if len(words) > 1:
        out.add(words[0] + "".join(w.capitalize() for w in words[1:]))
    return {v for v in out if v}


#: This programme's own home, excluded from every sweep it performs.
#:
#: WITHOUT THIS THE REGISTER IS SELF-FULFILLING. `06-MANDATE-CORPUS.json` transcribes all
#: 1,449 labels verbatim, so the moment it is committed every mandate matches at least one
#: tracked file -- its own corpus -- and every ABSENT silently becomes SPECIFIED on the
#: strength of the measurement's own input. The same class of defect was found and fixed
#: one programme over: a derived register counted as evidence of the concept it mentions.
SELF = "00-MASTER/CAEM-001/"


_PCRE_CHECKED = False


def _require_pcre() -> None:
    """Fail closed if this git cannot do PCRE, rather than measuring everything as absent."""
    global _PCRE_CHECKED  # noqa: PLW0603 - one-shot capability probe
    if _PCRE_CHECKED:
        return
    probe = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", "grep", "-P", "-l", "-e", r"\bgit\b", "--", "README.md"],  # noqa: S607
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if probe.returncode not in (0, 1):
        raise RuntimeError(
            "git grep -P is unavailable, so single-word mandates cannot be matched as "
            "stems. Refusing to measure: without PCRE every one of them would read ABSENT. "
            f"git said: {probe.stderr.strip()[:200]}"
        )
    _PCRE_CHECKED = True


def git_grep(token: str, whole_word: bool = False) -> list[str]:
    """Tracked files containing `token`, optionally only as a whole word.

    WHY THE FLAG EXISTS. Substring matching is safe for a phrase and catastrophic for a
    short word. Measured on this repository: `AR` matched 6,993 files and `AI` 5,069,
    because both occur inside *are*, *architecture*, *available* and *chain*; `ERP`
    matched 1,353 because Python is full of *interpreter*; `Board` matched 434 through
    *dashboard*; `Architect` matched 2,564 through *architecture*. Whole-word counts are
    226, 323, 31, 27 and 99 -- so between 94% and 98% of those hits were noise, and the
    200-file "too generic to decide" threshold was being applied to that noise.

    MORPHOLOGY IS KEPT. A bare whole-word match would swing the error the other way:
    `Recognize` would stop matching *recognized* (166 files down to 23) and `License`
    would stop matching *licensing* (49 down to 19). So a single word is matched as a
    STEM with an optional inflection -- boundary, word, optional s/es/d/ed/ing, boundary.
    Measured: ERP 1,353 -> 31, AR 6,993 -> 226, Board 434 -> 27, while License recovers
    to 40 and Recognize to 143. Noise removed, inflections retained.

    Phrases keep substring matching, which is already specific enough to be safe and
    stays tolerant of plurals without a pattern.
    """
    if whole_word:
        _require_pcre()
        pattern = rf"\b{re.escape(token)}(s|es|d|ed|ing)?\b"
        argv = ["git", "grep", "-P", "-i", "-l"]
    else:
        pattern = token
        argv = ["git", "grep", "-F", "-i", "-l"]
    result = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [*argv, "--", pattern],  # noqa: S607 - git from PATH by design
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        return []
    return [f for f in result.stdout.splitlines() if f and not f.startswith(SELF)]


def file_kind(path: str) -> str:
    low = path.lower()
    base = low.rsplit("/", 1)[-1]
    if "/tests/" in f"/{low}" or low.startswith("tests/") or base.startswith("test_"):
        return "test"
    if path.startswith(".github/workflows/") or path in GATE_FILES:
        return "gate"
    if low.endswith(CODE_EXT):
        return "code"
    if low.endswith((".json", ".yml", ".yaml", ".toml")):
        return "decl"
    return "doc"


def authority_rank(path: str) -> int:
    """How much AUTHORITY a hit carries. Lower binds harder."""
    if path.endswith("-declaration.json") or path.endswith("/law.py"):
        return 0
    if path.startswith("00-BOOK/DATA/") and path.endswith(".json"):
        return 1
    if path.startswith("00-MASTER/") and path.endswith(".json"):
        return 2
    if path.startswith(("engine/", "platform/", "intelligence/")) and path.endswith(".py"):
        return 6 if "/tests/" in path else 3
    if path.startswith(".github/workflows/"):
        return 4
    return 7


# Words carrying no ownership question of their own.
STOP = frozenset(
    "universal the a an of to for and or is it any every new future unknown before under "
    "once can what who where when how which why shall must may".split()
)

#: Keys whose VALUES name a thing rather than describe it.
NAMING_KEYS = (
    '"artifact_id"',
    '"title"',
    '"authority"',
    '"capability"',
    '"name"',
    '"id"',
    '"domain"',
    '"question"',
    '"subject"',
    '"owner"',
    '"program"',
    '"mission"',
)


#: Above this, a file is scored on its PATH alone. The big DATA registers mention every
#: concept in the repository, so reading them decides nothing and costs everything.
_MAX_SCORED_BYTES = 4_000_000


@lru_cache(maxsize=64)
def _file_text(path: str) -> str | None:
    """Lower-cased contents, cached. Scoring probes the same declarations repeatedly."""
    full = REPO / path
    try:
        if full.stat().st_size > _MAX_SCORED_BYTES:
            return None
        return full.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return None


#: The one classifier instance. Built once, reused for every scored file.
_CLASSIFIER = default_pipeline()


@lru_cache(maxsize=512)
def _is_structured_data(path: str) -> bool:
    """Whether `path` is serialised structured data, asked of the classifier and not the name.

    The scored population is every tracked file that names a mandate, so this decides between a
    key lookup and a prose scan. Asking the classifier keeps that decision out of the caller and
    makes it follow the same four ordered rules every other consumer uses, with the suffix last.
    The file text is the classifier's content evidence and is already cached by ``_file_text``;
    where it is absent the suffix alone still answers, which is the case the caller returns before.
    """
    artifact = Artifact(identifier=path, location=Location(provider="filesystem", locator=path))
    return _CLASSIFIER.classify(artifact, _file_text(path)).artifact_type == DATASET


def owner_score(path: str, label: str) -> int:
    """How strongly does `path` OWN `label`, as opposed to merely mentioning it?

    WHY THIS REPLACED RANK-ORDER. The first attribution sorted hits by file KIND and broke
    ties on path order, so the owner of a concept was in practice whichever declaration
    sorted earliest and happened to contain the word. Measured on the result: 356 of 460
    EXTEND rows took their owner from the head-noun route, and ONE file --
    ACEE-000001/acee-declaration.json -- was named owner of "Monitoring Constitution",
    "Resolve Rules", "When does it change" and "Canonical Authority Discovery" alike.
    `id-ledger.json` owned "Context Model" for the same reason: it mentions everything, so
    it wins any contest decided by mentioning.

    Ownership is a different question from occurrence. A file whose own PATH carries the
    concept is where the concept lives; a file naming it in an identity field is declaring
    it; everything else is prose, and prose scores zero.
    """
    slug = norm(path.replace("/", " ").replace(".", " "))
    words = [w for w in norm(label).split() if w not in STOP and len(w) > 2]
    if not words:
        return 0

    score = 0
    if all(f" {w} " in f" {slug} " for w in words):
        score += 4
    elif f" {words[-1]} " in f" {slug} ":
        score += 3

    lowered = _file_text(path)
    if lowered is None:
        return score
    target = norm(label)

    if _is_structured_data(path):
        if f'"{target}"' in lowered:
            score += 2
        else:
            for key in NAMING_KEYS:
                start = lowered.find(key)
                while start != -1:
                    if target in lowered[start : start + 200]:
                        return score + 2
                    start = lowered.find(key, start + 1)
    else:
        for line in lowered.splitlines():
            stripped = line.strip().lower()
            if stripped.startswith(("#", "def ", "class ", '"""', "- **", "| **")) and (
                target in stripped
            ):
                score += 1
                break
    return score


def build_anchor_index() -> tuple[set, dict]:
    raw: list[str] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                raw.append(key)
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str):
            raw.append(node)

    for rel in ANCHOR_SOURCES:
        path = REPO / rel
        if path.is_file():
            walk(json.loads(path.read_text(encoding="utf-8")))
    tracked = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", "ls-files"],  # noqa: S607 - git from PATH by design
        cwd=REPO,
        capture_output=True,
        text=True,
    ).stdout.split()
    for rel in tracked:
        if rel.startswith(SELF):
            continue
        raw.append(rel)
        raw.extend(rel.replace(".", "/").split("/"))

    anchors: set[str] = set()
    by_word: dict[str, set[str]] = defaultdict(set)
    for value in raw:
        text = norm(value)
        words = text.split()
        # NAME-SHAPED only: a forty-word sentence containing "identity" is a mention,
        # and a mention is exactly what is being refused here.
        if not (1 <= len(words) <= 6) or len(text) > 60:
            continue
        anchors.add(text)
        by_word[words[0]].add(text)
        by_word[words[-1]].add(text)
    return anchors, by_word


def anchored(label: str, anchors: set, by_word: dict) -> bool:
    text = norm(label)
    words = text.split()
    if text in anchors:
        return True
    for candidate in by_word.get(words[0], set()) | by_word.get(words[-1], set()):
        if len(candidate.split()) > 4:
            continue
        if (
            candidate.startswith(f"{text} ")
            or candidate.endswith(f" {text}")
            or f" {text} " in candidate
        ):
            return True
    return False


# --- disposition ------------------------------------------------------------------------


def owners_of_concept(label: str, files: list[str], probe: int = 30) -> list[str]:
    """The hit files that NAME the concept, best first -- never merely mention it.

    Only the top `probe` candidates by authority rank are scored, because scoring reads the
    file and a generic concept can hit thousands. Owners live among the declarations and
    modules, which is exactly what authority rank brings to the front, so the cap costs
    nothing an owner would have occupied.

    Returns [] when nothing NAMES the concept. That empty result is a finding, not a
    failure: it says the concept occurs in this repository without anything claiming it.
    """
    ranked = sorted(files, key=lambda f: (authority_rank(f), f))[:probe]
    scored = [(owner_score(f, label), -authority_rank(f), f) for f in ranked]
    return [f for score, _rank, f in sorted(scored, reverse=True) if score > 0][:4]


def measure(workers: int = 12) -> dict:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    anchors, by_word = build_anchor_index()

    section_kinds = corpus.get("section_kinds", {})
    by_label: dict[str, list[dict]] = defaultdict(list)
    for atom in corpus["atoms"]:
        by_label[norm(atom["label"])].append(atom)
    keys = sorted(by_label)
    print(f"measuring {len(corpus['atoms'])} atoms over {len(keys)} concepts", file=sys.stderr)

    def sweep(key: str) -> tuple[str, list[str]]:
        label = by_label[key][0]["label"]
        single = len(norm(label).split()) == 1
        found: set[str] = set()
        for token in variants(label):
            found.update(git_grep(token, whole_word=single))
        return key, sorted(found, key=lambda f: (authority_rank(f), f))

    concepts: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for done, (key, files) in enumerate(pool.map(sweep, keys), start=1):
            label = by_label[key][0]["label"]
            kinds = Counter(file_kind(f) for f in files)
            kinds = {k: kinds.get(k, 0) for k in ("code", "test", "gate", "decl", "doc")}
            anc = anchored(label, anchors, by_word)
            owned = named_for(label, files)
            concepts[key] = {
                "label": label,
                "status": classify(label, len(files), kinds, anc, owned),
                "mandates": [a["atom_id"] for a in by_label[key]],
                "hits": len(files),
                "anchored": anc,
                "section_kind": next(
                    (
                        section_kinds[a["section"]]
                        for a in by_label[key]
                        if a["section"] in section_kinds
                    ),
                    "CONSTRUCT",
                ),
                "kinds": kinds,
                "owned_code_files": owned,
                "owner_files": owners_of_concept(label, files),
                "code_files": [f for f in files if authority_rank(f) == 3][:4],
                "gate_files": [f for f in files if authority_rank(f) == 4][:2],
                "mention_only": [f for f in files if authority_rank(f) <= 2][:3],
            }
            if done % 200 == 0:
                print(f"  ... {done}/{len(keys)}", file=sys.stderr, flush=True)

    _dispose(concepts, workers)
    totals = Counter(c["status"] for c in concepts.values())
    dispositions = Counter(c.get("disposition", "") for c in concepts.values())
    return {
        "artifact_id": "CAEM-001-07",
        "title": "CAEM-001 · OUTPUT 07 — MANDATE DISPOSITION",
        "authority": AUTHORITY,
        "constitutional_superior": "UCKP-LAW-0001 via CAEM-001",
        "$every_disposition_here_is_provisional": "Derived by measurement, not by the "
        "manual mapping act CAEM-001 §1 performed. "
        "Semantic equivalence is forbidden to this engine, so no row below is an "
        "equivalence claim; each names a CANDIDATE owner a person must confirm or "
        "reject. Promotion to CONFIRMED is recorded per-row and is never automatic.",
        "corpus": "00-MASTER/CAEM-001/06-MANDATE-CORPUS.json",
        "atom_count": len(corpus["atoms"]),
        "concept_count": len(concepts),
        "status_totals": dict(sorted(totals.items())),
        "disposition_totals": dict(sorted(dispositions.items())),
        "concepts": dict(sorted(concepts.items())),
    }


def _dispose(concepts: dict, workers: int) -> None:
    """CAEM-001's rule: a gap exists only where NO owner exists AND extend/reference
    would distort the owner's single responsibility."""
    for concept in concepts.values():
        status = concept["status"]
        kind = concept.get("section_kind", "CONSTRUCT")
        # A stakeholder is an audience and a target domain is a market. Neither is built,
        # and asking "is it in the code" of either is a category error: `Developers`
        # reading IMPLEMENTED because the word occurs in source says nothing at all, and
        # `Agriculture` reading CREATE would instruct the repository to hard-code an
        # industry that PROHIBITED_TOKENS exists to refuse.
        if kind == "STAKEHOLDER":
            concept["disposition"] = "AUDIENCE"
            concept["determination"] = "PROVISIONAL"
            concept["reason"] = (
                "a stakeholder the substrate serves, not a construct it contains; "
                "nothing is owed by the repository"
            )
            continue
        if kind == "DOMAIN":
            concept["disposition"] = "REGISTER"
            concept["determination"] = "PROVISIONAL"
            concept["reason"] = (
                "a market the substrate is composed into, admitted as registered data "
                "rather than built as code (MIP LAW P43-001); implementing it would be "
                "the fixed industry LYR-NEG/LN-05 forbids"
            )
            continue
        if status == "IMPLEMENTED":
            concept["disposition"] = "IMPLEMENTED"
        elif status == "ASSERTION":
            concept["disposition"] = "ASSERT"
        elif concept["hits"] == 0:
            concept["disposition"] = "CREATE"
        elif status == "UNDECIDABLE":
            concept["disposition"] = "ADJUDICATE"
        elif status == "PARTIAL":
            # Code nothing asserts is an owner missing a facet -- the test or the gate --
            # which is EXTEND by definition, never a gap.
            concept["disposition"] = "EXTEND"
        elif concept["owner_files"]:
            concept["disposition"] = "REFERENCE"
        elif concept["code_files"] or concept["gate_files"]:
            concept["disposition"] = "EXTEND"
        else:
            concept["disposition"] = "CREATE"
        concept["determination"] = "PROVISIONAL"

    # THE CAEM-001 CORRECTION. Re-ask every provisional CREATE as a narrower question:
    # is the HEAD NOUN owned? "Analytics Graph" absent does not mean GRAPH is absent.
    provisional = [k for k, c in concepts.items() if c["disposition"] == "CREATE"]
    leaked = [k for k in provisional if concepts[k].get("section_kind") != "CONSTRUCT"]
    if leaked:
        raise RuntimeError(f"a stakeholder or domain reached the CREATE re-ask: {leaked[:3]}")
    print(f"re-asking {len(provisional)} provisional CREATEs", file=sys.stderr)

    def head_owner(key: str) -> tuple[str, list[str], list[str]]:
        words = [w for w in norm(concepts[key]["label"]).split() if w not in STOP and len(w) > 2]
        if not words:
            return key, [], []
        hits = git_grep(words[-1], whole_word=True)
        return key, words, owners_of_concept(words[-1], hits)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for key, words, owners in pool.map(head_owner, provisional):
            concept = concepts[key]
            concept["head_noun"] = words[-1] if words else ""
            concept["head_noun_owner"] = owners
            if owners:
                concept["disposition"] = "EXTEND"
                concept["reason"] = (
                    f"head noun {concept['head_noun']!r} is named by {owners[0]}; the "
                    "concept has an owner, this variant of it does not. CANDIDATE — a "
                    "person must confirm the owner genuinely holds it."
                )
            else:
                concept["reason"] = (
                    f"no owner located for {concept['head_noun'] or key!r} either, so "
                    "nothing in the repository holds this under any spelling tried"
                )


# --- binding ------------------------------------------------------------------------------
def bind(data: dict) -> dict:
    """Which mandates does something OUTSIDE this programme now name?

    A disposition says what is owed. This says what has been PAID, and the two must be
    separate measurements or the register cannot tell a discharged obligation from an
    outstanding one -- repaid debt left unclaimed, which this repository refuses in both
    directions.

    One pass, not 1,449 greps: every identifier-shaped token in the tree is extracted at
    once and intersected with the corpus. The programme's own home is excluded for the
    same reason the sweep excludes it -- `06-MANDATE-CORPUS.json` names all 1,449, so
    without the exclusion every mandate reads as bound by its own transcription.
    """
    result = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [  # noqa: S607 - git from PATH by design
            "git",
            "grep",
            "-l",
            "-E",
            "[A-Z][A-Z0-9]+(-[A-Z0-9]+)*/[A-Z]+[0-9]*-[0-9]+",
            "--",
            f":(exclude){SELF}",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    candidates = [f for f in result.stdout.splitlines() if f]
    declared = {m for c in data["concepts"].values() for m in c["mandates"]}

    # A test may bind one mandate by id, or a whole SECTION by reading the corpus for it --
    # `_corpus_section("MI-017")` covers all 27 target domains by construction and names no
    # individual identifier. Crediting only exact ids would leave those 27 reading unbound
    # while a test proves them, which is the same repaid-debt-unclaimed error in miniature.
    sections = {m.split("/")[0] for m in declared}
    named_in: dict[str, list[str]] = defaultdict(list)
    for rel in candidates:
        try:
            text = (REPO / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for mandate in declared:
            if mandate in text:
                named_in[mandate].append(rel)
        for section in sections:
            if f'"{section}"' in text:
                for mandate in declared:
                    if mandate.startswith(f"{section}/"):
                        named_in[mandate].append(rel)

    bound_total = 0
    for concept in data["concepts"].values():
        files = sorted({f for m in concept["mandates"] for f in named_in.get(m, ())})
        # Only a TEST or a GATE discharges anything. A mandate named in a document is
        # cited, not answered, and counting citations would make the register congratulate
        # itself for prose.
        proving = [f for f in files if file_kind(f) in ("test", "gate")]
        concept["named_by"] = files[:6]
        concept["proved_by"] = proving[:6]
        concept["bound"] = bool(proving)
        bound_total += bool(proving)
    data["bound_total"] = bound_total
    return data


# --- projection -------------------------------------------------------------------------
DISPOSITION_MEANING = {
    "IMPLEMENTED": "Located in code and named by a test or a gate. Nothing owed.",
    "REFERENCE": "An owner already carries this. Cite it and build nothing — building "
    "anyway is a second authoring, void under UCKP-ART-03.",
    "EXTEND": "An owner exists but does not yet carry this facet. Widen the owner.",
    "ASSERT": "The claim is about an ABSENCE. It needs a conformance test, not a name.",
    "ADJUDICATE": "A generic word in 200+ files with no owner located. Search cannot "
    "decide it and this engine will not pretend otherwise.",
    "REGISTER": "A market the substrate is composed into. Admitted as registered data, "
    "never built as code -- MIP LAW P43-001, and `industry` is a token the kernel refuses "
    "to seed. Proving admission IS the implementation.",
    "AUDIENCE": "A stakeholder the substrate serves. Not a construct; nothing is owed.",
    "CREATE": "Nothing in the repository owns this under any spelling tried. A genuine "
    "gap, and the only disposition that is new construction.",
}
ORDER = (
    "IMPLEMENTED",
    "REFERENCE",
    "EXTEND",
    "ASSERT",
    "REGISTER",
    "AUDIENCE",
    "ADJUDICATE",
    "CREATE",
)


def render(data: dict) -> str:
    concepts = data["concepts"]
    lines: list[str] = []
    add = lines.append

    add("# CAEM-001 · OUTPUT 08 — MANDATE DISPOSITION REGISTER")
    add("")
    add(
        f"> **AUTHORITY = NONE — DERIVED TRUTH.** Generated by `caem_engine.py` from "
        f"`06-MANDATE-CORPUS.json`. {data['atom_count']} mandates over "
        f"{data['concept_count']} distinct concepts."
    )
    add("")
    add(
        "**Every disposition below is PROVISIONAL.** This engine may not decide semantic "
        "equivalence — `21-CONCEPT-NORMALIZATION-REGISTER.md` forbids it, because doing so "
        '*"would fabricate equivalence; equivalence is decided only by canonical-ID '
        'identity."* So each row names a **candidate** owner that a person confirms or '
        "rejects. §1 of this instrument shows what a CONFIRMED row looks like: thirteen "
        "concepts, mapped by hand, each with a located home and a stated treatment."
    )
    add("")
    add("## §1 — DISPOSITION TOTALS")
    add("")
    add("| Disposition | Concepts | Mandates | Meaning |")
    add("|---|---:|---:|---|")
    atoms_by = Counter()
    for concept in concepts.values():
        atoms_by[concept["disposition"]] += len(concept["mandates"])
    for name in ORDER:
        count = sum(1 for c in concepts.values() if c["disposition"] == name)
        if count:
            add(f"| **{name}** | {count} | {atoms_by[name]} | {DISPOSITION_MEANING[name]} |")
    add("")

    bound = sum(1 for c in concepts.values() if c.get("bound"))
    if bound:
        add(
            f"**Discharged so far: {bound} of {len(concepts)} concepts** are named by a test "
            "or a gate outside this programme. A disposition records what is OWED; this "
            "records what has been PAID, and they are separate measurements on purpose -- "
            "a register that cannot tell a discharged obligation from an outstanding one "
            "leaves repaid debt unclaimed."
        )
        add("")
        for name in ORDER:
            total = sum(1 for c in concepts.values() if c["disposition"] == name)
            done = sum(1 for c in concepts.values() if c["disposition"] == name and c.get("bound"))
            if total and done:
                add(f"- **{name}** — {done} of {total} bound")
        add("")

    add("## §2 — THE CORRECTION THIS REGISTER IS SHAPED AROUND")
    add("")
    # Derived from THIS run, never narrated from a previous one: a register quoting a
    # number it did not itself measure is exactly the drift it exists to refuse.
    reasked = [c for c in concepts.values() if "head_noun" in c]
    rescued = [c for c in reasked if c.get("head_noun_owner")]
    add(
        f"The first pass used *zero grep hits* as the test for a genuine gap and returned "
        f"**{len(reasked)}**. CAEM-001's founding measurement refutes that directly: the "
        "token `Fabric` occurs in **zero** of 4,981 tracked files, yet six of the eight "
        "Fabrics have canonical homes under other names. A zero-hit **label** is not "
        "evidence of a missing **concept**."
    )
    add("")
    add(
        f"Re-asking each zero-hit label against its **head noun's** owner — *is `graph` "
        f"owned, even though `Analytics Graph` is not?* — moved **{len(rescued)}** concepts "
        f"from CREATE to EXTEND and left **{len(reasked) - len(rescued)}**. Acting on the "
        "first number would have authored hundreds of rival authorities, which is the exact "
        "failure this instrument exists to prevent."
    )
    add("")

    create = sorted(
        (c for c in concepts.values() if c["disposition"] == "CREATE"), key=lambda c: c["label"]
    )
    add("## §3 — CREATE · nothing owns these under any spelling")
    add("")
    add("| Mandated concept | Mandated by | Head noun searched |")
    add("|---|---|---|")
    for concept in create:
        add(
            f"| {concept['label']} | `{concept['mandates'][0]}` | "
            f"`{concept.get('head_noun', '')}` |"
        )
    add("")

    adjudicate = sorted(
        (c for c in concepts.values() if c["disposition"] == "ADJUDICATE"), key=lambda c: c["label"]
    )
    add("## §4 — ADJUDICATE · search cannot decide these")
    add("")
    add("| Concept | Tracked files matching | Mandated by |")
    add("|---|---:|---|")
    for concept in adjudicate:
        add(f"| {concept['label']} | {concept['hits']} | `{concept['mandates'][0]}` |")
    add("")
    add(
        "Several are the instrument failing honestly rather than the repository failing: "
        "a two-letter token like `AI` or `AR` matches inside longer words, and a two-letter "
        "token is not a searchable requirement."
    )
    add("")

    add("## §5 — EVERY CONCEPT")
    add("")
    add("| Concept | Status | Disposition | Determination | Candidate owner | Mandates |")
    add("|---|---|---|---|---|---:|")
    for key in sorted(concepts):
        concept = concepts[key]
        owner = (
            concept["owner_files"]
            or concept["code_files"]
            or concept.get("head_noun_owner")
            or [""]
        )[0]
        add(
            f"| {concept['label']} | {concept['status']} | {concept['disposition']} | "
            f"{concept['determination']} | `{owner}` | {len(concept['mandates'])} |"
        )
    add("")
    return "\n".join(lines) + "\n"


def gate(data: dict, *, quiet: bool = False) -> int:
    """Fail closed. Each check refuses a way this register could quietly become false.

    ``quiet`` suppresses only the passing banner. Failures always print, so a green run
    stays quiet in the certification log while a refusing one still names itself — the
    same contract every other gate engine in this repository honours with the same flag.
    """
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    concepts = data["concepts"]
    failures: list[str] = []

    declared = {a["atom_id"] for a in corpus["atoms"]}
    carried = {m for c in concepts.values() for m in c["mandates"]}
    missing = declared - carried
    if missing:
        failures.append(
            f"CAEM-INV-01 EVERY_MANDATE_DISPOSITIONED: {len(missing)} "
            f"undispositioned, e.g. {sorted(missing)[:3]}"
        )

    orphan = carried - declared
    if orphan:
        failures.append(
            f"CAEM-INV-02 NO_MANDATE_INVENTED: {len(orphan)} dispositioned "
            f"mandates are not in the corpus, e.g. {sorted(orphan)[:3]}"
        )

    undecided = [k for k, c in concepts.items() if c["disposition"] not in ORDER]
    if undecided:
        failures.append(
            f"CAEM-INV-03 EVERY_DISPOSITION_DECLARED: {len(undecided)} carry "
            f"an undeclared disposition"
        )

    # A CONFIRMED row must name a file that exists: a confirmed determination pointing at
    # a path nobody kept is worse than a provisional one, because it reads as settled.
    for key, concept in concepts.items():
        if concept["determination"] != "CONFIRMED":
            continue
        owner = (concept["owner_files"] or concept["code_files"] or [""])[0]
        if not owner or not (REPO / owner).exists():
            failures.append(
                f"CAEM-INV-04 CONFIRMED_OWNER_EXISTS: {key!r} is CONFIRMED but "
                f"its owner {owner!r} is not a file"
            )

    for line in failures:
        print(f"  [FAIL] {line}")
    if failures:
        print(f"GATE FAILED — {len(failures)} blocking finding(s).")
        return 1
    if quiet:
        return 0
    print(f"  [PASS] CAEM-INV-01 EVERY_MANDATE_DISPOSITIONED  (measured={len(declared)})")
    print(f"  [PASS] CAEM-INV-02 NO_MANDATE_INVENTED          (measured={len(carried)})")
    print(f"  [PASS] CAEM-INV-03 EVERY_DISPOSITION_DECLARED   (measured={len(concepts)})")
    print("  [PASS] CAEM-INV-04 CONFIRMED_OWNER_EXISTS")
    print("GATE PASSED — every mandate carries a disposition.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=f"{PROGRAM} mandate disposition engine")
    parser.add_argument(
        "--measure",
        action="store_true",
        help="re-run the full sweep (~5k greps) and rewrite output 07",
    )
    parser.add_argument(
        "--bind",
        action="store_true",
        help="cheap: re-measure which mandates a test or gate now names, and rewrite 07",
    )
    parser.add_argument("--render", action="store_true", help="render output 08 from 07")
    parser.add_argument("--gate", action="store_true", help="fail-closed invariant checks")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress the passing banner; a refusing gate still prints",
    )
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    if args.measure:
        data = bind(measure(args.workers))
        DISPOSITION.write_text(
            json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"wrote {DISPOSITION.relative_to(REPO)}")
        for name, count in sorted(data["disposition_totals"].items()):
            print(f"  {name:12} {count}")

    if not DISPOSITION.is_file():
        print(f"{DISPOSITION.relative_to(REPO)} absent — run --measure first", file=sys.stderr)
        return 2
    data = json.loads(DISPOSITION.read_text(encoding="utf-8"))

    if args.bind:
        data = bind(data)
        DISPOSITION.write_text(
            json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(
            f"bound: {data['bound_total']} of {len(data['concepts'])} concepts "
            "are named by a test or a gate"
        )

    if args.render or args.measure or args.bind:
        REGISTER.write_text(render(data), encoding="utf-8")
        print(f"wrote {REGISTER.relative_to(REPO)}")

    if args.gate:
        return gate(data, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
