"""UCOS-CL-001 — repository contamination measured over the filesystem, not over git's
exclusion rules.

The defect this closes
----------------------
UCOS-RIB-001 measured repository cleanliness as a count of ``git status --porcelain``
lines. That command applies the ignore authority, so ``.gitignore`` was an *input* to the
gate whose job is to police excluded state. At commit ``be46a300`` two lines
(``* [2-9]`` / ``* [2-9].*``) removed 41 physically-present files from the gate's
observation surface. Nothing left the disk. But the metric fell to zero, which flipped
RIB ``GATE-12`` and ``GATE-04``, opened ``rib.json:gate``, satisfied AEE
``OBS-BLUEPRINT-GATE`` and cleared ``CONV-02``. A one-line ignore rule could buy a
convergence certification.

The correction
--------------
Cleanliness is measured over the ignored-INCLUSIVE filesystem, and every ignored path
must resolve to a class declared in the tracked exclusion register
(``00-BOOK/DATA/exclusion-register.json``). An ignored path that no register entry claims
is ``ignored_unclassified`` and fails closed.

The property that was missing, and is now structural: **adding an ignore rule no longer
removes an observation, it adds a classification obligation.** The contamination count is
not a function of anything the author of a mutation can shrink unilaterally — shrinking it
requires declaring a class in a tracked, reviewable artifact.

Why here
--------
``platform.repository_intelligence`` is the repository's existing repository-state
capability (``substrate``, ``discovery``, ``evidence``, ``validation``). UCOS-RIB-001 is a
programme that *consumes* repository intelligence; it is not the owner of the measurement.
Putting the classifier here keeps one implementation with many consumers rather than a
second one hard-coded inside a programme engine.
"""

from __future__ import annotations

import fnmatch
import json
import subprocess
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

#: The register that declares what an exclusion *means*. Tracked, authored, never generated.
EXCLUSION_REGISTER = "00-BOOK/DATA/exclusion-register.json"

#: Classes the register may assign. A rule carrying anything else is not a declaration.
DECLARED_CLASSES: frozenset[str] = frozenset(
    {
        "GENERATED_DETERMINISTIC",
        "GENERATED_ENVIRONMENTAL",
        "TEST_EXECUTION_ARTIFACT",
        "CACHE",
        "TOOL_OPERATIONAL",
        "TEMPORARY",
        "EXPLICITLY_AUTHORIZED_EXTERNAL",
    }
)


@dataclass(frozen=True)
class ExcludedPath:
    """One ignored filesystem entry and the register entry that accounts for it."""

    path: str
    rule: str
    classification: str | None

    @property
    def classified(self) -> bool:
        return self.classification in DECLARED_CLASSES


@dataclass(frozen=True)
class ContaminationReport:
    """The measured contamination state of a repository working tree.

    Every count here is a function of the FILESYSTEM plus the tracked register. None of
    them can be reduced by editing ``.gitignore`` alone.
    """

    dirty_entries: tuple[str, ...] = ()
    untracked_entries: tuple[str, ...] = ()
    excluded: tuple[ExcludedPath, ...] = ()
    shadowed_tracked: tuple[str, ...] = ()
    register_errors: tuple[str, ...] = field(default=())

    @property
    def ignored_unclassified(self) -> int:
        """Ignored paths that no register entry claims. THE fail-closed metric."""
        return sum(1 for e in self.excluded if not e.classified)

    @property
    def unclassified_paths(self) -> tuple[str, ...]:
        return tuple(e.path for e in self.excluded if not e.classified)

    @property
    def contamination_entries(self) -> int:
        """Everything the repository cannot account for.

        Uncommitted work, untracked files, ignored-but-undeclared paths, and any tracked
        path shadowed by an ignore rule. Deliberately NOT the same number as
        ``dirty_entries``: that one answers "is the index clean", this one answers "is the
        repository accounted for".
        """
        return (
            len(self.dirty_entries)
            + len(self.untracked_entries)
            + self.ignored_unclassified
            + len(self.shadowed_tracked)
        )

    @property
    def clean(self) -> bool:
        return self.contamination_entries == 0 and not self.register_errors

    @property
    def excluded_entries(self) -> int:
        """How many ignored paths exist on THIS filesystem.

        UCOS-RC-001 — diagnostic only, and deliberately NOT serialized. This counts
        ``__pycache__`` directories, ``.ec1-venv``, tool caches: artifacts of the machine
        rather than of the repository. It was serialized once, and the Phase-9 forensic at
        HEAD 382b65e8 found it to be the single differing field in rib.json between the
        source repository (232) and a pristine clone (69) — the entire cause of
        registry_variance. A caller wanting it for a report reads it here; nothing that
        reaches a canonical artifact may.
        """
        return len(self.excluded)

    def as_dict(self) -> dict[str, object]:
        """The CANONICAL serialization. Every value is invariant across environments.

        What is included is a governance verdict — is anything unclassified, shadowed,
        dirty, or untracked — and each of those is zero in any correctly-governed clone of
        the same commit. What is excluded is any measure of how much ignored material this
        particular machine happens to hold, because a canonical artifact whose bytes move
        with the local cache population cannot be reproduced from its own commit.
        """
        return {
            "dirty_entries": len(self.dirty_entries),
            "untracked_entries": len(self.untracked_entries),
            # `excluded_entries` is deliberately absent — see the property above.
            "ignored_unclassified": self.ignored_unclassified,
            "shadowed_tracked": len(self.shadowed_tracked),
            "contamination_entries": self.contamination_entries,
            "register_errors": list(self.register_errors),
            "clean": self.clean,
            # Paths, not just counts, for the unaccounted-for cases: a reader must be able
            # to act on a failure without re-deriving it. The counts alone are what let the
            # earlier defect stay invisible. These are empty whenever governance holds, so
            # they carry no environmental content in a passing repository — and when they
            # are non-empty the repository is already failing closed and must be read.
            "unclassified_paths": list(self.unclassified_paths)[:50],
            "shadowed_tracked_paths": list(self.shadowed_tracked)[:50],
        }


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607 - fixed argv, no shell
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        # A failing git command and a git command returning nothing are different states.
        # Conflating them is exactly how a corrupt ref made `git log --all` look like an
        # empty history (UCOS-CL-004), so this raises rather than returning "".
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout


def load_register(repo: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    """Read the exclusion register into ``rule -> class``, plus any structural errors."""
    path = repo / EXCLUSION_REGISTER
    if not path.exists():
        return {}, (f"exclusion register missing: {EXCLUSION_REGISTER}",)
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, (f"exclusion register is not valid JSON: {exc}",)

    mapping: dict[str, str] = {}
    errors: list[str] = []
    for entry in doc.get("entries", []):
        rule, klass = entry.get("rule"), entry.get("class")
        if not rule:
            errors.append("register entry with no rule")
            continue
        if klass not in DECLARED_CLASSES:
            errors.append(f"rule {rule!r} carries undeclared class {klass!r}")
            continue
        if rule in mapping:
            errors.append(f"rule {rule!r} declared twice")
            continue
        mapping[rule] = klass
    return mapping, tuple(errors)


def _rule_of(line: str) -> str:
    """Extract the pattern from a ``git check-ignore -v`` source field.

    The field is ``<source>:<line>:<pattern>``. The pattern may itself contain ``:``, so
    the split is bounded to the first two separators rather than taking the last field.
    """
    parts = line.split(":", 2)
    return parts[2] if len(parts) == 3 else line


def _check_ignore(repo: Path, paths: Sequence[str], *, no_index: bool) -> dict[str, str]:
    """Map each of *paths* to the ignore rule that matches it, if any."""
    if not paths:
        return {}
    args = ["check-ignore", "-v", "--stdin"]
    if no_index:
        args.insert(1, "--no-index")
    proc = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607 - fixed argv, no shell
        cwd=repo,
        input="\n".join(paths),
        capture_output=True,
        text=True,
        check=False,
    )
    # check-ignore exits 1 when nothing matched, which is a legitimate result, not an error.
    if proc.returncode not in (0, 1):
        raise RuntimeError(f"git check-ignore failed ({proc.returncode}): {proc.stderr.strip()}")
    out: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) < 2:
            continue
        source, path = fields[0], fields[-1]
        rule = _rule_of(source)
        # A negation rule (`!pattern`) means the path is explicitly NOT excluded.
        if rule.startswith("!"):
            continue
        out[path] = rule
    return out


def _classify(rule: str, register: Mapping[str, str]) -> str | None:
    """Resolve a rule to its declared class, exactly first then by pattern."""
    if rule in register:
        return register[rule]
    # A nested tool-authored `.gitignore` may hold a bare `*`; the register declares that
    # form once rather than once per cache directory.
    for declared, klass in register.items():
        if fnmatch.fnmatch(rule, declared) or fnmatch.fnmatch(declared, rule):
            return klass
    return None


def measure(repo: Path, *, generated: Iterable[str] = ()) -> ContaminationReport:
    """Measure contamination over the ignored-inclusive filesystem.

    ``generated`` names paths a producer legitimately rewrites on every run — a programme's
    own regenerated outputs. They are subtracted from the dirty set for the same reason
    UCOS-RIB-001 already subtracts them: an artifact that dirties itself by being produced
    would make its own gate un-satisfiable.
    """
    repo = Path(repo)
    register, register_errors = load_register(repo)
    exempt = set(generated)

    porcelain = _git(
        repo, "status", "--porcelain", "--ignored=matching", "--untracked-files=all", "-z"
    )
    dirty: list[str] = []
    untracked: list[str] = []
    ignored: list[str] = []
    for record in porcelain.split("\0"):
        if len(record) < 4:
            continue
        code, path = record[:2], record[3:]
        if path in exempt:
            continue
        if code == "!!":
            ignored.append(path)
        elif code == "??":
            untracked.append(path)
        else:
            dirty.append(path)

    rules = _check_ignore(repo, ignored, no_index=False)
    excluded = tuple(
        ExcludedPath(
            path=p,
            rule=rules.get(p, "<unmatched>"),
            classification=_classify(rules.get(p, "<unmatched>"), register),
        )
        for p in sorted(ignored)
    )

    # A tracked path matched by an ignore rule survives only because git skips ignore rules
    # for indexed files. The moment it leaves the index it vanishes from governance, so it
    # is contamination-in-waiting and is counted now rather than discovered later.
    tracked = [p for p in _git(repo, "ls-files", "-z").split("\0") if p]
    shadowed = tuple(sorted(_check_ignore(repo, tracked, no_index=True)))

    return ContaminationReport(
        dirty_entries=tuple(sorted(dirty)),
        untracked_entries=tuple(sorted(untracked)),
        excluded=excluded,
        shadowed_tracked=shadowed,
        register_errors=register_errors,
    )
