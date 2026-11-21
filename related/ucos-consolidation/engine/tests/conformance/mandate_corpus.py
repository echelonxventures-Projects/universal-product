"""The reader every mandate-conformance suite shares, and the two checks each one owes.

WHY THIS IS ONE MODULE AND NOT SIX COPIES. Six suites read the same corpus and make the
same two structural claims about their own tiering. Copied, those claims drift: the fourth
copy forgets disjointness, the fifth widens its absence search, and a suite that has quietly
stopped checking looks exactly like one that passes. UCKP-ART-03 calls a second authoring of
the same knowledge void, and this is the smallest thing that keeps it singular.

WHAT A SUITE OWES, AND WHY BOTH HALVES.

  * TOTALITY — every mandate in the section lands in exactly one tier. Without it a
    mandate can be dropped from the suite and read as passing, because nothing looks for it.
  * NON-VACUITY — the tier meaning "nothing carries this" is searched for, not asserted.
    Without it the absent tier is where anything inconvenient goes, and absence is the one
    claim that costs nothing to make and everything to be wrong about.

WHAT THIS MODULE REFUSES TO DO. It never reads `07-MANDATE-DISPOSITION.json`. That file is
this repository measuring itself, and a conformance suite that checked the measurement
instead of the thing measured would agree with it by construction. Every suite reads the
TRANSCRIPTION -- the documents' own wording -- and asserts against the instruments.
"""

from __future__ import annotations

import json
import subprocess
from functools import lru_cache
from pathlib import Path

#: The transcription. Never the disposition — see the module docstring.
CORPUS_PATH = ("00-MASTER", "CAEM-001", "06-MANDATE-CORPUS.json")


def repo_root() -> Path:
    """The repository root, derived from this file's own location."""
    return Path(__file__).resolve().parents[3]


@lru_cache(maxsize=1)
def corpus() -> dict:
    return json.loads((repo_root().joinpath(*CORPUS_PATH)).read_text(encoding="utf-8"))


def section(name: str) -> dict[str, str]:
    """``{atom_id: label}`` for one section, in transcription order.

    The section is checked to EXIST. A typo would otherwise return an empty mapping and
    every assertion a suite makes over it would pass without examining anything.
    """
    atoms = {a["atom_id"]: a["label"] for a in corpus()["atoms"] if a["section"] == name}
    assert atoms, f"{name} is not a section this corpus carries"
    return atoms


@lru_cache(maxsize=1)
def tracked() -> tuple[str, ...]:
    """Every version-controlled path. The filesystem is not Repository Truth: an untracked
    worktree copy or editor scratch file is not evidence that anything exists."""
    listing = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", "-C", str(repo_root()), "ls-files"],  # noqa: S607 - git from PATH by design
        capture_output=True,
        text=True,
        check=True,
    )
    return tuple(line for line in listing.stdout.splitlines() if line)


def assert_partitions(name: str, mandates: dict[str, str], *tiers: dict) -> None:
    """TOTALITY: the tiers cover the section exactly, and no mandate sits in two of them."""
    accounted: set[str] = set()
    for tier in tiers:
        accounted |= set(tier)

    missing = sorted(set(mandates) - accounted)
    assert not missing, f"{name}: mandates in no tier: {missing}"

    foreign = sorted(accounted - set(mandates))
    assert not foreign, f"{name}: tiered identifiers that are not {name} mandates: {foreign}"

    total = sum(len(tier) for tier in tiers)
    assert total == len(accounted) == len(mandates), (
        f"{name}: {total} tier entries over {len(accounted)} distinct mandates — one is "
        "claimed in two tiers, so it is being reported both present and absent"
    )


def assert_homes_exist(name: str, homes: dict[str, str]) -> None:
    """A home that does not exist is a guess. Checked against the TRACKED set."""
    known = set(tracked())
    for mandate, home in homes.items():
        assert home in known or any(
            path.startswith(home.rstrip("/") + "/") for path in known
        ), f"{name}/{mandate}: declared home {home!r} is not a tracked path"


def _path_tokens(path: str) -> set[str]:
    """The words a path is made of, singularised.

    Raw substring matching is wrong here and was wrong in practice: `mission` occurs inside
    `admission.py` and `permissions.py`, so a search for the kernel's Mission found two
    modules that have nothing to do with it. A path is a sequence of WORDS and the question
    is whether one of them is the concept, so the path is split into words and compared word
    to word.
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


def assert_named_by_nothing(name: str, absent: dict[str, str], *, suffix: str = ".py") -> None:
    """NON-VACUITY for an absent tier.

    Naming means the PATH carries every word of the concept as a WORD, not as a substring
    and not merely its last word: matching `Realization Package` to
    `commercial_intelligence/packages.py` on `package` alone is the occurrence-is-ownership
    error these suites exist to avoid, and matching `Mission` to `admission.py` is the same
    error one level down. Searching file CONTENT instead would match every document that
    merely discusses the concept and make absence unprovable in the other direction.
    """
    for mandate, concept in absent.items():
        words = {w.rstrip("s") for w in concept.replace("-", " ").lower().split()}
        found = [
            path
            for path in tracked()
            if path.endswith(suffix) and "/tests/" not in path and words <= _path_tokens(path)
        ]
        assert not found, (
            f"{name}/{mandate}: {concept!r} is declared absent but a path is named for it: "
            f"{found}"
        )


def assert_absence_rule_can_find_something(concept: str, *, suffix: str = ".py") -> None:
    """The absence rule must be capable of a positive verdict, or it passes every absence
    claim by construction. Each suite runs it against a concept it has located."""
    words = {w.rstrip("s") for w in concept.replace("-", " ").lower().split()}
    hits = [path for path in tracked() if path.endswith(suffix) and words <= _path_tokens(path)]
    assert hits, (
        f"the path-naming rule finds nothing for {concept!r}, which is located; the rule "
        "matches nothing at all and every absence claim resting on it is vacuous"
    )
