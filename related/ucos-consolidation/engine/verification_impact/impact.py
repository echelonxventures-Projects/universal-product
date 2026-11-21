"""Changed object → minimal required verification.

The flow the determination requires, in order:

    changed object → impact discovery → affected objects → affected evidence
                   → affected tests → affected certification → minimal scope

Two design rules make this safe to select verification with rather than merely
informative:

* **Fail wide, never narrow.** Every path this engine cannot classify escalates to
  FULL scope. An impact engine's failure mode must be "verify everything", because the
  alternative is a green run that skipped the affected test. :func:`analyse` returns
  ``escalations`` naming every reason it widened, so a reader can see *why* a run was
  full rather than guessing.
* **Non-code changes escalate.** A change to a declaration, registry, config or
  constitutional document has no import edges, so its blast radius is not computable
  from the dependency graph. Those escalate rather than resolving to an empty set —
  which is exactly the case where a naive engine reports "no tests affected".
* **An escalation states what was measured.** Widening is safe; naming a reason that was
  never measured is not, because the reason is what a reader uses to decide whether the
  coupling is real. Every branch in :func:`analyse` consults the registry before it
  characterises a path.

DECLARED LIMIT — DATA EDGES ARE NOT IN THE SUBSTRATE. The object registry resolves
dependencies through ``uga_engine.py::python_imports``, so no record carries a non-``.py``
dependency: measured at this commit, the count of non-``.py`` dependency edges across all
5 439 entries is zero. A module that reads a governed data file — ``engine/lineage/
projection.py`` naming ``engine/lineage/families.json``, for one — therefore has a real
coupling that the substrate does not record, and this engine escalates rather than
inventing the edge. Deriving data edges here would build the second dependency graph this
package exists not to build (``OBS-INV-13``); closing it belongs to the registry's producer,
not to its reader.
"""

from __future__ import annotations

import enum
import os
from dataclasses import dataclass, field

from engine.verification_impact.graph import ImpactGraph

#: Path prefixes whose change cannot be bounded by import edges. A change here
#: escalates to FULL, because a declaration or registry drives engines that no
#: import graph connects to it.
UNBOUNDED_PREFIXES: tuple[str, ...] = (
    "00-BOOK/DATA/",
    "00-BOOK/SCHEMAS/",
    "00-BOOK/tools/",
    "00-CMG/",
    "00-CEP/",
    "pyproject.toml",
    "verify.sh",
    "Makefile",
    "scripts/",
)

#: The FALLBACK when the registry cannot be consulted. Not a policy and not a language choice —
#: the value the derivation below produces today, kept so a caller holding no graph still gets the
#: current answer rather than an empty one.
FALLBACK_BOUNDED_SUFFIXES: tuple[str, ...] = (".py",)


def bounded_suffixes(graph: ImpactGraph) -> tuple[str, ...]:
    """Which suffixes carry dependency edges, MEASURED from the registry rather than declared.

    THIS WAS A LITERAL, AND THE LITERAL WAS A LANGUAGE ASSUMPTION. `BOUNDED_SUFFIXES = (".py",)`
    said that only Python files have edges an impact analysis can follow. That is true today and
    is not a property of impact analysis: it is a property of the registry's edge derivation,
    which resolves imports through `uga_engine.py::python_imports` and nothing else. Measured at
    this commit, `.py` is the only suffix carrying a dependency edge — 2,106 objects — out of
    2,924 `.md`, 2,290 `.py`, 173 `.json`, 38 `.yml` and 11 `.sh`.

    Deriving it means the day a second language acquires an edge deriver, its files stop
    escalating every change to FULL without anyone editing this module. That is UCKP-ART-15: no
    conclusion rests on a hardcoded assumption, every finding derived from the declared universe.
    A file type whose edges nobody derives is still unbounded, and correctly so — the conclusion
    is unchanged, its BASIS is now measured.
    """
    measured = {
        os.path.splitext(path)[1] for path, record in graph.objects.items() if record.dependencies
    }
    return tuple(sorted(measured)) or FALLBACK_BOUNDED_SUFFIXES


class Scope(str, enum.Enum):
    """How much verification a change requires.

    Ordered by breadth. :meth:`widen` keeps the strongest requirement, so combining
    a bounded change with an unbounded one yields the unbounded answer.
    """

    NONE = "none"
    CHANGED = "changed"
    INTEGRATION = "integration"
    FULL = "full"

    @property
    def rank(self) -> int:
        return {"none": 0, "changed": 1, "integration": 2, "full": 3}[self.value]

    def widen(self, other: Scope) -> Scope:
        """Return the broader of the two scopes."""
        return self if self.rank >= other.rank else other


@dataclass(frozen=True, slots=True)
class ImpactReport:
    """What a change reaches, and the least verification that covers it."""

    changed: tuple[str, ...]
    affected_objects: tuple[str, ...]
    affected_tests: tuple[str, ...]
    affected_evidence: tuple[str, ...]
    affected_certification: tuple[str, ...]
    affected_owners: tuple[str, ...]
    scope: Scope
    escalations: tuple[str, ...]
    unregistered: tuple[str, ...]
    unbounded: tuple[str, ...] = ()

    @property
    def is_full(self) -> bool:
        return self.scope is Scope.FULL

    @property
    def is_computable(self) -> bool:
        """True when every changed path was bounded by a graph rather than escaped it.

        The distinction a consumer needs and ``scope`` alone cannot express. Both
        ``Scope.FULL`` from "this file type has no edges" and ``Scope.INTEGRATION``
        from "the blast radius is wide" widen the plan, but only the first is an
        *inability to compute*: the second is a computed answer that happens to be
        large, and a consumer with more substrates than this engine has may narrow it
        legitimately. Nothing may narrow the first.
        """
        return not self.unbounded

    def to_dict(self) -> dict[str, object]:
        return {
            "changed": list(self.changed),
            "affected_objects": list(self.affected_objects),
            "affected_tests": list(self.affected_tests),
            "affected_evidence": list(self.affected_evidence),
            "affected_certification": list(self.affected_certification),
            "affected_owners": list(self.affected_owners),
            "scope": self.scope.value,
            "escalations": list(self.escalations),
            "unregistered": list(self.unregistered),
            "unbounded": list(self.unbounded),
            "counts": {
                "changed": len(self.changed),
                "affected_objects": len(self.affected_objects),
                "affected_tests": len(self.affected_tests),
                "affected_owners": len(self.affected_owners),
            },
        }


def _is_unbounded(path: str) -> bool:
    return path.startswith(UNBOUNDED_PREFIXES)


def _is_bounded(path: str, suffixes: tuple[str, ...] = FALLBACK_BOUNDED_SUFFIXES) -> bool:
    return path.endswith(suffixes)


def analyse(graph: ImpactGraph, changed: list[str] | tuple[str, ...]) -> ImpactReport:
    """Compute the impact of ``changed`` and the minimal verification it requires."""
    changed_paths = tuple(sorted(set(changed)))
    if not changed_paths:
        return ImpactReport(
            changed=(),
            affected_objects=(),
            affected_tests=(),
            affected_evidence=(),
            affected_certification=(),
            affected_owners=(),
            scope=Scope.NONE,
            escalations=(),
            unregistered=(),
        )

    suffixes = bounded_suffixes(graph)
    escalations: list[str] = []
    scope = Scope.CHANGED
    bounded: set[str] = set()
    unregistered: list[str] = []
    unbounded: list[str] = []

    for path in changed_paths:
        if _is_unbounded(path):
            scope = scope.widen(Scope.FULL)
            unbounded.append(path)
            escalations.append(
                f"{path}: change is not bounded by import edges "
                "(declaration, registry, schema, tooling or contract)"
            )
            continue
        # THE REGISTRY IS CONSULTED BEFORE THE FILE TYPE, AND THE ORDER IS THE POINT.
        # The earlier form asked `_is_bounded` first and, for anything that was not `.py`,
        # reported "no dependency edges exist for this file type" — a claim about the type,
        # asserted before anything was measured. It was false in both directions:
        # `engine/lineage/families.json` is registered as UCOS-ENG-000023 with an explicitly
        # empty `dependencies` list, which is a MEASURED emptiness rather than a type-level
        # absence, and 172 registered `.json` objects show the type carries records at all.
        # Every branch below still widens to FULL, so no run narrows — what changes is that
        # each escalation now states what was actually measured. This is the same defect
        # class the non-ASCII path fix retired: escalation that is right by accident and
        # wrong by mechanism is not tracking real coupling.
        record = graph.record(path)
        if record is None:
            scope = scope.widen(Scope.FULL)
            unbounded.append(path)
            escalations.append(
                f"{path}: not present in the executable object registry, so its "
                "dependents are unknown"
            )
            unregistered.append(path)
            continue
        if not _is_bounded(path, suffixes):
            scope = scope.widen(Scope.FULL)
            unbounded.append(path)
            escalations.append(
                f"{path}: recorded as {record.object_class}, a class the object registry "
                "does not resolve dependency edges for, so its dependents are unknown"
            )
            continue
        bounded.add(path)

    affected = graph.dependents_of(bounded) if bounded else set()
    universe = bounded | affected

    tests = sorted(p for p in universe if (r := graph.record(p)) is not None and r.is_test)
    evidence = sorted(
        {
            r.evidence_class
            for p in universe
            if (r := graph.record(p)) is not None and r.evidence_class
        }
    )
    certification = sorted(
        {
            r.certification_status
            for p in universe
            if (r := graph.record(p)) is not None and r.certification_status
        }
    )
    owners = sorted({r.owner for p in universe if (r := graph.record(p)) is not None and r.owner})

    # A bounded change that reaches no test is not "nothing to verify" — it is code
    # nothing exercises, which is a coverage question, not a licence to skip.
    if bounded and not tests:
        scope = scope.widen(Scope.INTEGRATION)
        escalations.append("bounded change reaches no test object; widening rather than skipping")

    # Breadth is itself a signal: a change reaching many owners is a subsystem change.
    if len(owners) > 3 and scope is Scope.CHANGED:
        scope = scope.widen(Scope.INTEGRATION)
        escalations.append(
            f"change reaches {len(owners)} owners, which is a subsystem-level blast radius"
        )

    return ImpactReport(
        changed=changed_paths,
        affected_objects=tuple(sorted(universe)),
        affected_tests=tuple(tests),
        affected_evidence=tuple(evidence),
        affected_certification=tuple(certification),
        affected_owners=tuple(owners),
        scope=scope,
        escalations=tuple(escalations),
        unregistered=tuple(unregistered),
        unbounded=tuple(sorted(unbounded)),
    )


@dataclass(frozen=True, slots=True)
class VerificationPlan:
    """The concrete pytest selection a mode should run."""

    scope: Scope
    test_paths: tuple[str, ...] = field(default_factory=tuple)
    run_everything: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "scope": self.scope.value,
            "run_everything": self.run_everything,
            "test_paths": list(self.test_paths),
            "reason": self.reason,
        }


def plan(report: ImpactReport) -> VerificationPlan:
    """Turn an impact report into the selection a verification mode should execute."""
    if report.scope is Scope.NONE:
        return VerificationPlan(
            scope=Scope.NONE, run_everything=False, reason="no changes to verify"
        )
    if report.scope in (Scope.FULL, Scope.INTEGRATION):
        return VerificationPlan(
            scope=report.scope,
            run_everything=True,
            reason=(
                report.escalations[0] if report.escalations else "scope requires the whole suite"
            ),
        )
    return VerificationPlan(
        scope=Scope.CHANGED,
        test_paths=report.affected_tests,
        run_everything=False,
        reason=(
            f"{len(report.affected_tests)} test object(s) reachable from "
            f"{len(report.changed)} changed file(s)"
        ),
    )
