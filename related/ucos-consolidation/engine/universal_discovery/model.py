"""UCOS-OMEGA-001 Part 1 — the vocabulary, and why each term is a measurement.

AUTHORITY = NONE (DERIVED TRUTH). This package legislates nothing. It measures.

WHAT THIS PACKAGE REPLACES, STATED AS THE DEFECT THAT PRODUCED IT.

Every governance control in this repository quantified over a list somebody wrote down. The
lists were correct on the day they were written and silently wrong afterwards. The measured
instances, all of them found by reading the lists rather than by any control firing:

    SOURCE_TREES = ("engine", "platform")     ← five other roots existed
    engine.recursive_knowledge                ← a namespace package no predicate saw
    intelligence, service, data,              ← 35,333 statements, 4,121 passing tests,
      application, infrastructure               collected by nothing
    certification_integrity                   ← declared, never imported

Seven omissions, one root cause: **enumerated governance**. A list of what exists agrees with
itself forever. It cannot report its own incompleteness, because incompleteness is precisely
the thing it has no term for.

THE Ω INVERSION. Governance stops comparing reality against a curated list and starts deriving
its scope FROM reality. The population is ``git ls-files '*.py'``; every scope, authority,
denominator and threshold is a function of that population. A new top-level tree is governed on
the commit that introduces it, with no edit anywhere — which is the only form in which the claim
"unbounded scope" is checkable rather than aspirational.

THE FIVE DISPOSITIONS ARE TOTAL AND MUTUALLY EXCLUSIVE.

Every tracked Python artifact receives exactly one, and the last rule is unconditional, so
"unknown" and "orphan" are structurally unreachable rather than merely unobserved. That
totality is the whole product: a file cannot fall out of governance by being unusual.

  MEASURED   — inside a measurement that runs. Coverage measures it, or the suite executes it.
  EXEMPTED   — outside measurement for a DERIVED and STATED reason, ratcheted convergently.
  GENERATED  — a producer owns its bytes; measuring it would measure the producer twice.
  ARCHIVED   — under a tree a declaration freezes. Writing to it is already refused.
  TRANSIENT  — declared transient by its owner. The ONLY disposition a human may assert, and
               the only one under which ``authority = NONE`` is admissible.

WHY ``EXEMPTED`` IS NOT AN ESCAPE HATCH. An exemption must name the RULE that produced it, the
rule must be a measured property rather than a path, and the population of each rule is a
convergent ratchet — it may fall and hold, never rise. An exemption class that stops shrinking
is visible as a stalled ratchet instead of invisible as a settled convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --------------------------------------------------------------------------- dispositions
#: Ω-5. Exactly one per tracked Python artifact. No sixth value, and no absence.
MEASURED = "MEASURED"
EXEMPTED = "EXEMPTED"
GENERATED = "GENERATED"
ARCHIVED = "ARCHIVED"
TRANSIENT = "TRANSIENT"

DISPOSITIONS: tuple[str, ...] = (MEASURED, EXEMPTED, GENERATED, ARCHIVED, TRANSIENT)

#: The dispositions under which a missing authority is a FINDING rather than a fact. Ω-2 admits
#: ``authority = NONE`` for exactly one disposition, and TRANSIENT is the one, because transience
#: is the only claim that is self-justifying: an artifact declared not to persist cannot acquire
#: a durable owner.
AUTHORITY_REQUIRED: frozenset[str] = frozenset({MEASURED, EXEMPTED, GENERATED, ARCHIVED})

#: The dispositions that participate in the executable-surface denominator. GENERATED and
#: ARCHIVED are excluded because their bytes are owned elsewhere; TRANSIENT because it does not
#: persist. Everything else counts, which is what makes the ratio unable to be flattered by
#: reclassification alone — the reclassification has to be justified by a measured property.
SURFACE_DISPOSITIONS: frozenset[str] = frozenset({MEASURED, EXEMPTED})

# ------------------------------------------------------------------------------ ratchet kinds
#: Ω-4. A ratchet is a DIRECTION, never a ceiling. The four kinds are the four honest shapes a
#: "this must not get worse" claim can take; a fifth shape would be a number somebody chose.
MONOTONIC = "MONOTONIC"  # may fall or hold. Never rise.
CONVERGENT = "CONVERGENT"  # may fall or hold, and a long hold is reported as STALLED.
DENSITY = "DENSITY"  # a ratio. May improve or hold. Scale-free by construction.
ENTROPY = "ENTROPY"  # complexity per executable unit. May improve or hold.

RATCHET_KINDS: tuple[str, ...] = (MONOTONIC, CONVERGENT, DENSITY, ENTROPY)

#: Ratchets whose better direction is DOWN. ``DENSITY`` and ``ENTROPY`` are also down-better
#: here; a metric whose better direction is up is expressed as its complement so that one
#: comparison serves every kind and no per-metric sign convention can be got wrong.
LOWER_IS_BETTER: frozenset[str] = frozenset(RATCHET_KINDS)

#: Verdicts a ratchet observation can carry.
IMPROVED = "IMPROVED"
HELD = "HELD"
STALLED = "STALLED"
REGRESSED = "REGRESSED"
JUSTIFIED = "JUSTIFIED"
SEEDED = "SEEDED"


class OmegaError(RuntimeError):
    """A discovery, authority or ratchet measurement could not be made.

    RAISED, NEVER DEFAULTED. Every place this is raised is a place where returning a benign
    value would make a "no violations" claim true by emptiness — an empty repository satisfies
    every invariant in this package, so an empty answer must be a fault rather than a pass.
    """


@dataclass(frozen=True)
class Artifact:
    """One tracked Python file, and every Ω verdict about it.

    Constructed once per run and never mutated: the disposition, the authority and the
    reachability verdict are all functions of the same population, so a reader can check that
    they were computed over one world rather than three.
    """

    path: str
    #: Ω-1: the discovered top-level root. Derived, never declared.
    root: str
    #: Ω-1: the dotted module name, when the path is importable as one; else "".
    module: str
    #: Ω-5: exactly one of DISPOSITIONS.
    disposition: str
    #: Ω-5: the rule id that produced the disposition. Never a judgement.
    disposition_rule: str
    #: Ω-5: the measured property the rule observed, in words a reader can check.
    disposition_reason: str
    #: Ω-2: the authority that owns this artifact. "" only when disposition is TRANSIENT.
    authority: str
    #: Ω-2: the derivation step that produced the authority.
    authority_rule: str
    #: Ω-3: whether the execution graph reaches this artifact from any entry point.
    reachable: bool
    #: Ω-3: the planes that reach it, grouped by TYPE so one plane cannot be counted twice.
    reached_by: tuple[str, ...]
    #: Structural size, from the AST alone. Never intersected with a coverage report, so this
    #: field cannot change because an artifact the run does not measure happened to exist.
    statements: int
    #: Callable entry points inside the file. A file with no callable has no way to be entered.
    callables: int
    #: Import fan-out. The ENTROPY ratchet's numerator.
    imports: int

    def as_record(self) -> dict[str, object]:
        return {
            "path": self.path,
            "root": self.root,
            "module": self.module,
            "disposition": self.disposition,
            "disposition_rule": self.disposition_rule,
            "disposition_reason": self.disposition_reason,
            "authority": self.authority,
            "authority_rule": self.authority_rule,
            "reachable": self.reachable,
            "reached_by": list(self.reached_by),
            "statements": self.statements,
            "callables": self.callables,
            "imports": self.imports,
        }


@dataclass(frozen=True)
class Observation:
    """One ratchet metric, measured now and compared against its own best-ever value."""

    metric: str
    kind: str
    value: float
    best: float | None
    verdict: str
    #: What the metric counts, so a reader need not read the code to check the claim.
    subject: str
    #: Present only when verdict is JUSTIFIED. The declared reason a regression stands.
    justification: str = ""
    #: Present only for DENSITY/ENTROPY: the numerator and denominator that produced ``value``.
    ratio: tuple[int, int] | None = None

    @property
    def refused(self) -> bool:
        return self.verdict in (REGRESSED, STALLED)

    def as_record(self) -> dict[str, object]:
        record: dict[str, object] = {
            "metric": self.metric,
            "kind": self.kind,
            "value": self.value,
            "best": self.best,
            "verdict": self.verdict,
            "subject": self.subject,
        }
        if self.justification:
            record["justification"] = self.justification
        if self.ratio is not None:
            record["ratio"] = {"numerator": self.ratio[0], "denominator": self.ratio[1]}
        return record


@dataclass(frozen=True)
class Population:
    """The discovered world. Ω-1's output and every other phase's only input.

    NO CONSTRUCTOR ARGUMENT IS A LIST SOMEBODY WROTE. Every field is derived from
    ``git ls-files``, from the AST of what that returns, or from a declaration whose own
    contents are discovered. That is the property the gate asserts about this class.
    """

    #: Every tracked ``.py`` path, POSIX, repo-relative, sorted.
    paths: tuple[str, ...]
    #: Every discovered top-level root that carries tracked Python.
    roots: tuple[str, ...]
    #: Roots whose name is a Python identifier, so a coverage source can name them.
    importable_roots: tuple[str, ...]
    #: Discovered test roots: directories a test-module property identifies, not a listing.
    test_roots: tuple[str, ...]
    #: The derived coverage denominator, as dotted package names.
    measurable_packages: tuple[str, ...]
    #: Declared exemptions, package -> reason. The one human-authored input, and the reason it
    #: is admissible is that Ω-5 requires an exemption to be arguable rather than silent.
    declared_exemptions: dict[str, str] = field(default_factory=dict)
    #: Declared transient paths, path -> reason. The only route to ``authority = NONE``.
    declared_transient: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.paths:
            raise OmegaError(
                "the discovered Python population is empty, and every Ω invariant is "
                "vacuously true over an empty world — refusing to report a pass"
            )
        if not self.roots:
            raise OmegaError("tracked Python exists but no root was derived from it")
