"""UCI-000001 Part 1 — vocabulary.

Every name here is a noun the laws in ``contract.py`` quantify over. Nothing in this module
reads the filesystem, imports a sibling or holds a threshold: a vocabulary that could observe
would be able to disagree with the observations that use it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# --------------------------------------------------------------------------- object kinds
# The eight kinds the certification question is asked about. Constants rather than an enum
# because they are serialised into evidence and read by tools outside this package; an enum's
# repr would make the evidence depend on Python.

KIND_MODULE = "module"
KIND_CLASS = "class"
KIND_FUNCTION = "function"
KIND_METHOD = "method"
KIND_ENTRY_POINT = "entry_point"
KIND_CLI = "cli"
KIND_WORKFLOW_STAGE = "workflow_stage"
KIND_GOVERNANCE_ENGINE = "governance_engine"

OBJECT_KINDS = (
    KIND_MODULE,
    KIND_CLASS,
    KIND_FUNCTION,
    KIND_METHOD,
    KIND_ENTRY_POINT,
    KIND_CLI,
    KIND_WORKFLOW_STAGE,
    KIND_GOVERNANCE_ENGINE,
)

# ------------------------------------------------------------------- file classification
# Rule 2 of the mandate: every tracked Python artifact is classified, and the classification
# decides whether absence from the denominator is a defect or a governed exclusion.

FILE_EXECUTABLE = "executable"
FILE_TEST = "test"
FILE_GENERATED = "generated"
FILE_DECLARATION = "constitutional_declaration"
FILE_TOOLING = "tooling"
FILE_MIGRATION = "migration"
FILE_ARCHIVED = "archived"
FILE_EXCLUDED = "intentionally_excluded"

FILE_CLASSES = (
    FILE_EXECUTABLE,
    FILE_TEST,
    FILE_GENERATED,
    FILE_DECLARATION,
    FILE_TOOLING,
    FILE_MIGRATION,
    FILE_ARCHIVED,
    FILE_EXCLUDED,
)

#: Classes that MUST be inside the coverage denominator. The mandate's Rule 2 refuses
#: completion while any executable artifact is outside it, and ``tooling`` is included
#: deliberately: 00-BOOK/tools/ukb.py is the registration enforcement the whole corpus plane
#: depends on, and calling it "tooling" is a description of its directory, not a reason its
#: executed fraction may be unknown.
CLASSES_REQUIRING_MEASUREMENT = frozenset({FILE_EXECUTABLE, FILE_TOOLING})

# ------------------------------------------------------------------------- invocation planes
# PLANE TYPES, not invoking texts. UEC-L-06 counts distinct texts that name an artifact, which
# is the right measurement for "could this be deleted without anything noticing" and the wrong
# one for "is there a single point of failure": thirty-three workflow files are thirty-three
# texts and one CI plane, so an artifact invoked from thirty-three workflows and nothing else
# scores 33 there and 1 here. Both are true. This module needs the stricter one because a
# repository whose only invoker is CI cannot be verified locally, and vice versa.

PLANE_MAKE = "make"
PLANE_VERIFY = "verify"
PLANE_ENV = "env"
PLANE_CI = "ci"
PLANE_PYTHON = "python"
PLANE_TEST = "test"

PLANE_TYPES = (PLANE_MAKE, PLANE_VERIFY, PLANE_ENV, PLANE_CI, PLANE_PYTHON, PLANE_TEST)

#: Planes that can run without CI, and planes that can run without a developer's machine. An
#: artifact whose planes fall entirely on one side has a single point of failure even when it
#: has two plane types, which is why ``surface`` reports the set and not only its size.
LOCAL_PLANES = frozenset({PLANE_MAKE, PLANE_VERIFY, PLANE_ENV})
AUTOMATED_PLANES = frozenset({PLANE_CI})

# ---------------------------------------------------------------- uncovered-line disposition
# The mandate's classification set. ``EXECUTABLE`` is the only class whose remedy is "write a
# test", and it is the DEFAULT: a line is executable until something proves otherwise. The
# asymmetry is deliberate — the cheap classification must be the one that costs work, or
# classification becomes the mechanism by which coverage debt is retired without tests.

CLASS_EXECUTABLE = "executable"
CLASS_DEFENSIVE = "defensive"
CLASS_IMPOSSIBLE = "impossible"
CLASS_UNREACHABLE = "unreachable"
CLASS_DEAD = "dead_code"
CLASS_GENERATED = "generated"
CLASS_EXEMPT = "governance-exempt"

LINE_CLASSES = (
    CLASS_EXECUTABLE,
    CLASS_DEFENSIVE,
    CLASS_IMPOSSIBLE,
    CLASS_UNREACHABLE,
    CLASS_DEAD,
    CLASS_GENERATED,
    CLASS_EXEMPT,
)

#: The remedy each class obliges. A class with no remedy would be a place to put lines.
REMEDY = {
    CLASS_EXECUTABLE: "write tests",
    CLASS_DEAD: "delete",
    CLASS_IMPOSSIBLE: "prove",
    CLASS_GENERATED: "govern",
    CLASS_DEFENSIVE: "prove",
    CLASS_UNREACHABLE: "prove or delete",
    CLASS_EXEMPT: "declare with constitutional authority",
}


class IntegrityError(Exception):
    """A measurement could not be taken, so no verdict may be asserted.

    Distinct from a refusal. ``contract.measure`` turns a refusal into exit 1 and this into
    exit 2, because "the surface is fully governed" and "the surface could not be enumerated"
    are different facts, and a gate that collapsed them would let a broken enumerator certify
    an empty repository.
    """


class DriftError(IntegrityError):
    """Two runs of one measurement over one state disagreed."""


@dataclass(frozen=True)
class ExecutableObject:
    """One executable object and everything the certification question asks about it.

    ``statements``/``covered``/``missing`` are line counts over the object's own line range,
    attributed to the innermost enclosing object so the counts partition rather than nest: a
    method's statements belong to the method, not also to its class and its module.
    """

    name: str
    kind: str
    module: str
    statements: int
    covered: int
    missing: int
    #: ``None`` when the object is outside the coverage denominator. Zero and "unmeasured" are
    #: different facts and a float cannot hold both; every consumer must decide which it means,
    #: which is the point.
    coverage_percent: float | None
    tested: bool
    invoked: bool
    invocation_planes: tuple[str, ...]
    #: False when no coverage measurement covers this object's file at all.
    measured: bool
    missing_lines: tuple[int, ...] = field(default=(), repr=False)

    def as_record(self) -> dict[str, object]:
        """The mandate's record shape, with the derived fields it did not ask for appended."""
        return {
            "name": self.name,
            "statements": self.statements,
            "covered": self.covered,
            "missing": self.missing,
            "coverage_percent": self.coverage_percent,
            "tested": self.tested,
            "invoked": self.invoked,
            "invocation_planes": list(self.invocation_planes),
            "kind": self.kind,
            "module": self.module,
            "measured": self.measured,
        }


@dataclass(frozen=True)
class FileRecord:
    """One tracked Python artifact, classified, with its governing authority."""

    path: str
    classification: str
    statements: int
    covered: int
    missing: int
    measured: bool
    execution_paths: tuple[str, ...]
    invocation_sources: tuple[str, ...]
    governing_authority: str
    exclusion_reason: str | None
    #: Statement count from the AST alone, NEVER intersected with a coverage report. ``statements``
    #: is intersected when one is present, so a law that used it for a size threshold answered
    #: differently depending on whether coverage.xml happened to exist — measured: UCI-L-06 moved
    #: 10 -> 9 on exactly that, with no file changed. A law whose verdict depends on the presence
    #: of an artifact it does not measure is not a law about the repository.
    ast_statements: int = 0

    @property
    def coverage_percent(self) -> float | None:
        if not self.measured:
            return None
        return 100.0 if self.statements == 0 else round(self.covered * 100.0 / self.statements, 4)

    def as_record(self) -> dict[str, object]:
        return {
            "path": self.path,
            "classification": self.classification,
            "measured_statements": self.statements,
            "covered_statements": self.covered,
            "missing_statements": self.missing,
            "coverage_percent": self.coverage_percent,
            "measured": self.measured,
            "execution_paths": list(self.execution_paths),
            "invocation_sources": list(self.invocation_sources),
            "governing_authority": self.governing_authority,
            "exclusion_reason": self.exclusion_reason,
        }


@dataclass(frozen=True)
class Provenance:
    """What a coverage figure is a figure OF.

    A percentage with no provenance is not reproducible even in principle: it does not say which
    tree it measured, which interpreter ran it, or how many tests contributed. Every field here
    is required, and ``dirty`` must be False for a certification run — a measurement of a tree
    that is not the named commit is a measurement of nothing citable.
    """

    commit_sha: str
    dirty: bool
    coverage_percent: float
    statements: int
    covered: int
    missing: int
    branch_percent: float | None
    test_count: int
    duration_seconds: float
    environment_hash: str
    python_version: str
    platform: str
    inventory_digest: str = ""
    coverage_digest: str = ""

    def as_record(self) -> dict[str, object]:
        return {
            "commit_sha": self.commit_sha,
            "dirty": self.dirty,
            "coverage_percent": self.coverage_percent,
            "statements": self.statements,
            "covered": self.covered,
            "missing": self.missing,
            "branch_percent": self.branch_percent,
            "test_count": self.test_count,
            "duration_seconds": self.duration_seconds,
            "environment_hash": self.environment_hash,
            "python_version": self.python_version,
            "platform": self.platform,
            "inventory_digest": self.inventory_digest,
            "coverage_digest": self.coverage_digest,
        }


@dataclass(frozen=True)
class UncoveredLine:
    """One uncovered line and its disposition under the mandate's classification rules."""

    path: str
    line: int
    owner: str
    source: str
    classification: str
    justification: str

    @property
    def remedy(self) -> str:
        return REMEDY[self.classification]

    def as_record(self) -> dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "owner": self.owner,
            "source": self.source,
            "classification": self.classification,
            "justification": self.justification,
            "remedy": self.remedy,
        }


Verdict = Literal["OPEN", "CLOSED", "FAULT"]
