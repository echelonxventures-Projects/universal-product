"""The UCOS adapter — UCOS's own truth, expressed in the substrate's terms.

WHAT AN ADAPTER OWES AND WHAT IT MUST NOT DO. It answers "what exists here" and "who
answers for it" in UCOS's vocabulary, and translates. It does not teach the substrate about
UCOS: no rule, no threshold and no judgement crosses this boundary, only facts.

TWO SOURCES, DELIBERATELY. The filesystem says what EXISTS; `00-BOOK/DATA/artifacts.json`
says what UCOS CLAIMS to govern. Reading only the register would make the adapter agree with
UCOS by construction and find nothing — which is exactly how a register goes stale unnoticed.
The disagreement between the two is the finding.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator

from uakp.adapters.filesystem import FilesystemAdapter
from uakp.core.artifact import Artifact
from uakp.core.authority import Authority

DECLARATION = os.path.join("00-MASTER", "UCOS-SUB-001", "sub-declaration.json")
REGISTER = os.path.join("00-BOOK", "DATA", "artifacts.json")
EXCLUSIONS = os.path.join("00-BOOK", "DATA", "exclusion-register.json")
ID_LEDGER = os.path.join("00-BOOK", "DATA", "id-ledger.json")
ENFORCEMENT = os.path.join("00-MASTER", "UEC-000001", "uec-declaration.json")


def ungoverned_directories(root: str) -> frozenset[str]:
    """Directories that hold no governed truth: caches, virtualenvs, version-control internals.

    Not a whitelist of what may exist — a list of what is reconstructible from what does.

    IT WAS A FROZEN LITERAL AND THAT WAS A CLOSED ENUMERATION. Eight names in the module
    source meant the set could only change by editing code, which UCKP-ART-17 refuses: a
    future category is admitted by registration, never by amendment. ISD-L-01 and UCON-L-15
    both counted it, and both were right. It reads from `discovery.ungoverned_directories` in
    UCOS-SUB-001's own declaration instead, so admitting a name is a data change.

    AN EMPTY OR ABSENT LIST RAISES RATHER THAN DEFAULTING. A default would silently walk
    `.git` and `.ec1-venv` and report thousands of artifacts nothing governs — a measurement
    that lies in the direction of alarm. The gate turns anything raised here into FAULT
    (exit 2, no verdict), which is the honest outcome when the declaration cannot be read.
    """
    with open(os.path.join(root, DECLARATION), encoding="utf-8") as handle:
        names = json.load(handle)["discovery"]["ungoverned_directories"]
    if not isinstance(names, list) or not all(isinstance(name, str) and name for name in names):
        raise ValueError(f"{DECLARATION}: discovery.ungoverned_directories is not a list of names")
    if not names:
        raise ValueError(f"{DECLARATION}: discovery.ungoverned_directories is empty")
    return frozenset(names)


def artifacts(root: str) -> Iterator[Artifact]:
    """Everything the environment contains, whatever language or format it is in."""
    skip = ungoverned_directories(root)
    yield from FilesystemAdapter(root, skip_directories=skip).discover()


def authorities(root: str) -> Iterator[Authority]:
    """What UCOS's own register claims to govern, as one authority.

    One authority rather than many because the register does not attribute its entries to
    distinct owners; claiming otherwise here would be the adapter inventing structure its
    source does not have, which is worse than reporting the structure that exists.
    """
    path = os.path.join(root, REGISTER)
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError):
        return
    entries = (
        document
        if isinstance(document, list)
        else (document.get("artifacts") or document.get("entries") or [])
    )
    claimed = {
        entry.get("path") or entry.get("canonical_path") or entry.get("identity")
        for entry in entries
        if isinstance(entry, dict)
    }
    claimed.discard(None)
    yield Authority(identity="UCOS-ARTIFACT-REGISTER", governs=frozenset(claimed))

    # EXCLUSION IS GOVERNANCE, NOT ITS ABSENCE, AND OMITTING IT WOULD MAKE THIS GATE LIE.
    # UCOS's exclusion register declares each excluded path with a class and a written
    # reason, so an excluded path is governed BY that register. Reporting those as owned by
    # nobody would drown the real finding in five thousand entries UCOS has already
    # answered for — and a finding nobody can read is not a finding.
    present = frozenset(a.identity for a in artifacts(root))
    yield from _exclusion_authority(root)
    yield from _identity_authority(root, present)
    yield from _enforcement_authority(root, present)


def _identity_authority(root: str, existing: frozenset[str]) -> Iterator[Authority]:
    """UGA's identity ledger — the broadest thing UCOS actually governs.

    `artifacts.json` is the CORPUS register: 1,658 entries, permit-gated, and deliberately
    narrow. The identity ledger is the object map, and an object with a Universal ID is
    governed whether or not the corpus admits it. Reading only the corpus register reported
    5,470 ungoverned artifacts, most of which UGA had in fact minted identities for — a
    finding that was true of the register and false of the repository.
    """
    path = os.path.join(root, ID_LEDGER)
    try:
        with open(path, encoding="utf-8") as handle:
            ledger = json.load(handle)
    except (OSError, ValueError):
        return
    # AN APPEND-ONLY LEDGER RECORDS IDENTITY, IT DOES NOT CLAIM PRESENCE. UCKP-ART-05 makes
    # an identity permanent: when a path is retired the ledger keeps its entry forever, which
    # is what append-only MEANS for a deletion. Mapping every historical entry to a present
    # claim reported thirteen "claims over things that do not exist" — all thirteen genuinely
    # absent, and none of them a defect. `ledger_authority.py` was deliberately moved with its
    # old identity retired, and the ledger recording that is the system working.
    #
    # So the ledger governs what it has minted AND that is still here. The retired remainder
    # is history, and history is not a claim.
    present = set(existing)
    claimed: set[str] = set()
    for section in ("by_path", "by_object"):
        entries = ledger.get(section)
        if isinstance(entries, dict):
            claimed |= set(entries) & present
    if claimed:
        yield Authority(identity="UCOS-IDENTITY-LEDGER", governs=frozenset(claimed))


def _enforcement_authority(root: str, existing: frozenset[str]) -> Iterator[Authority]:
    """UEC-000001's enforcement register — the gates, and who answers for each of them.

    THIS WAS MISSING AND THE MEASUREMENT WAS WRONG IN THE DIRECTION OF ALARM. UEC-000001
    binds every enforcement artifact in the repository to a rule and to a named owner, which
    is a claim of governance in the plainest sense the word has. Omitting it reported five
    artifacts as owned by nobody while an instrument of this repository named all five — and
    two of them, `uctx-gate.yml` and `ufi-gate.yml`, had nothing to do with this programme,
    so the error predated it and was found by it.

    The same failure mode has now been found three times in this adapter: read one register
    and you measure that register rather than the repository. The corpus register alone
    reported 5,470; adding exclusions and the identity ledger cut that to hundreds.

    IDENTITIES THAT ARE NOT PATHS ARE NOT CLAIMS OVER PATHS. Fifty-eight of the register's
    entries name Make targets and twenty-five name verify.sh stages: real governed things
    that are not files. Filtering to what exists on disk keeps this authority from claiming
    to govern a path merely because a target shares its name, which is exactly the invented
    structure the module docstring forbids.
    """
    path = os.path.join(root, ENFORCEMENT)
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError):
        return
    entries = document.get("governed_enforcement")
    if not isinstance(entries, list):
        return
    claimed = {
        entry["identity"]
        for entry in entries
        if isinstance(entry, dict)
        and isinstance(entry.get("identity"), str)
        and entry["identity"] in existing
    }
    if claimed:
        yield Authority(identity="UCOS-ENFORCEMENT-REGISTER", governs=frozenset(claimed))


def _pattern(rule: str) -> re.Pattern[str] | None:
    """Compile one gitignore rule into a regex over repository-relative paths.

    A rule that cannot be interpreted compiles to ``None`` and therefore matches NOTHING.
    Over-matching here would silently absolve paths the register never claimed, which is the
    direction that hides a finding.

    THE SEGMENT GRAMMAR IS THE POINT, and it is git's, not fnmatch's. ``**`` spans directory
    separators and a single ``*`` does not, so ``00-MASTER/**/evidence/`` claims
    ``00-MASTER/UAKOS-CLOSURE-008/evidence/verify.log`` while ``00-MASTER/*/evidence/`` would
    not claim it two levels down. ``fnmatch`` cannot express that distinction at all: it
    translates every ``*`` to ``.*``, so it says yes to both or, once a trailing slash sent the
    rule down a literal-prefix branch, to neither.

    MEASURED, this repository, 2026-09-02: the literal-prefix branch and ``fnmatch`` between
    them reported 221 artifacts as governed by nobody while the exclusion register named every
    one of them — 213 under ``00-MASTER/**/evidence/``, 6 under ``*.egg-info/`` and 2 under
    ``**/.claude/...``. Three ordinary gitignore forms, each declared, each ignored by git, and
    each unreadable to the consumer that had to apply it. Debt that does not exist is not the
    safe direction to be wrong in: it buries the debt that does under a number nobody trusts.
    """
    rule = rule.strip()
    if not rule or rule.startswith("#"):
        return None
    # A RULE WHOSE SCOPE IS NOT IN THE DATA MATCHES NOTHING. The register holds an entry
    # whose rule is bare `*`, and whose own rationale says: "The rule is scoped to the cache
    # directory that contains it, never to the repository root, and is admitted only in that
    # scope." That scope lives in PROSE and not in any field, so no consumer can apply it
    # correctly. Applied at root it absolved all 7,351 artifacts and this gate reported zero
    # contradictions — a total false green produced by reading a register faithfully.
    #
    # Refusing it here is the conservative direction, and the only honest one: an
    # unscopeable universal pattern is un-interpretable, and this function's contract is that
    # what it cannot interpret it does not absolve.
    if rule.strip("*/") == "":
        return None
    directory_only = rule.endswith("/")
    # A LEADING SLASH IS AN ANCHOR AND CARRIES MEANING. `/knowledge/` says so in its own
    # rationale — "Anchored with a leading slash so only the repo-root store is excluded;
    # engine/knowledge/ stays tracked" — and dropping it absolved 93 artifacts under
    # `00-MASTER/UAKOS-CLOSURE-008/evidence-vendored/output/knowledge/`, which the register
    # never claimed and git does not ignore.
    rooted = rule.startswith("/")
    body = rule.strip("/")
    # A rule with no interior separator floats: git matches it at any depth, which is what
    # `*.egg-info/` intends — an egg-info directory wherever the build puts one.
    floating = not rooted and "/" not in body
    segments = body.split("/")
    parts: list[str] = []
    separator_due = False
    for index, segment in enumerate(segments):
        if segment == "**":
            # `a/**/b` matches `a/b` and `a/x/y/b`, so the wildcard stands for zero or more
            # WHOLE segments and the separator that introduced it is mandatory, not folded in.
            # `(?:.*/)?` here would have let `00-MASTER/**/evidence/` claim
            # `00-MASTERvendored/evidence/`, which is over-matching on the segment boundary.
            if separator_due:
                parts.append("/")
            parts.append("(?:[^/]+/)*" if index < len(segments) - 1 else ".*")
            separator_due = False
            continue
        if separator_due:
            parts.append("/")
        parts.append(_segment(segment))
        separator_due = True
    prefix = "(?:.*/)?" if floating else ""
    tail = "/.*" if directory_only else "(?:/.*)?"
    try:
        return re.compile(f"^{prefix}{''.join(parts)}{tail}$")
    except re.error:  # pragma: no cover — every rule in the register compiles
        return None


def _segment(segment: str) -> str:
    """One path segment of a gitignore rule as a regex that never crosses a separator.

    Bracket expressions pass through as character classes because git supports them and this
    register uses one: ``00-MASTER/UAKOS-CLOSURE-002/[0-9][0-9]-*.md`` claims 43 generated
    registers, and escaping the brackets literally left every one of them unaccounted for.
    """
    out: list[str] = []
    index = 0
    while index < len(segment):
        char = segment[index]
        if char == "*":
            out.append("[^/]*")
        elif char == "?":
            out.append("[^/]")
        elif char == "[":
            close = segment.find("]", index + 2)
            if close == -1:  # an unterminated class is not a class; take it literally
                out.append(re.escape(char))
            else:
                body = segment[index + 1 : close]
                out.append("[" + ("^" + body[1:] if body[0] in "!^" else body) + "]")
                index = close + 1
                continue
        else:
            out.append(re.escape(char))
        index += 1
    return "".join(out)


def _matches(relative: str, rule: str) -> bool:
    """Whether one gitignore-shaped register rule claims one repository-relative path."""
    pattern = _pattern(rule)
    return pattern is not None and pattern.match(relative) is not None


def _carve_outs(root: str) -> tuple[str, ...]:
    """The repository's own `!pattern` lines — the paths its ignore rules explicitly EXEMPT.

    The register declares what an exclusion MEANS; it carries no negations, because a carve-out
    is the absence of an exclusion and has no class to declare. `.gitignore` carries them, and
    twenty-four of them matter: `00-MASTER/UAKOS-CLOSURE-002/[0-9][0-9]-*.md` names a family of
    generated registers, and twenty-four authored files inside that family are un-ignored by
    name. Applying the family rule without the carve-outs let the exclusion register absolve
    twenty-four tracked, authored artifacts.

    THE DIRECTION OF THIS DEPENDENCY IS THE WHOLE ARGUMENT. UCOS-CL-001 closed a defect where a
    one-line ignore rule bought a convergence certification, and its correction was that
    `.gitignore` may never be an INPUT to the gate that polices excluded state. Reading only the
    negations keeps that: a rule read here can only ever REMOVE an absolution, never grant one.
    Adding an ignore rule still absolves nothing until the register declares a class for it;
    adding a carve-out withdraws a claim the register was making by accident.
    """
    try:
        with open(os.path.join(root, ".gitignore"), encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return ()
    return tuple(line[1:].strip() for line in lines if line.startswith("!") and line[1:].strip())


def _exclusion_authority(root: str) -> Iterator[Authority]:
    path = os.path.join(root, EXCLUSIONS)
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError):
        return
    rules_declared = [
        entry["rule"]
        for entry in document.get("entries", [])
        if isinstance(entry, dict) and entry.get("rule")
    ]
    if not rules_declared:
        return
    exempt = _carve_outs(root)
    excluded = {
        artifact.identity
        for artifact in artifacts(root)
        if any(_matches(artifact.identity, rule) for rule in rules_declared)
        and not any(_matches(artifact.identity, rule) for rule in exempt)
    }
    yield Authority(identity="UCOS-EXCLUSION-REGISTER", governs=frozenset(excluded))


__all__ = [
    "DECLARATION",
    "ENFORCEMENT",
    "EXCLUSIONS",
    "ID_LEDGER",
    "REGISTER",
    "artifacts",
    "authorities",
    "ungoverned_directories",
]
