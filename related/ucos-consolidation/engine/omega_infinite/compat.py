"""UCOS Ω∞ Phase 1, Deliverable 7 — backwards compatibility, discharged by equivalence.

AUTHORITY = NONE (DERIVED TRUTH).

PHASE 1 ADDS A LAYER AND REPLACES NOTHING. ``engine/universal_discovery`` is untouched: same
entry points, same population, same dispositions, same ratchets, same sealed evidence. This module
is where that claim stops being a promise and becomes a measurement.

THE PROOF OBLIGATION, STATED PRECISELY. If the abstraction is a genuine generalisation of Ω-1, then
configuring it the way Ω-1 is configured must produce Ω-1's answer EXACTLY — not approximately, not
modulo ordering, not "the same set of interesting files". Byte-for-byte the same tuple::

    discovery.tracked_python(root)
        ==
    repository_space(root).discover(Selector(patterns=("*.py",))).locators()

A generalisation that changed the answer would not be a generalisation, it would be a second
population — and this repository already paid for four independent populations that no code
compared, with 619 artifacts sitting in exactly one of them. ``equivalence()`` below computes the
difference in both directions and ``identical`` is the assertion the test suite makes.

WHERE THE HARD-CODED ASSUMPTION WENT. It did not disappear; it moved to a place where it can be
named, inspected and overridden. ``PYTHON_ONLY`` is the ``'*.py'`` from ``discovery.tracked_python``
expressed as data. It is one line, it is a value, and passing a different one changes the population
without changing any code. That is the whole of Phase 1 in a single comparison:

    before   the filter is a string literal inside the only enumeration mechanism there is
    after    the filter is an argument, the mechanism is one provider among others, and both are
             reported in the evidence document

THE ADAPTER IS THE OTHER HALF. ``as_universal`` lifts an Ω-1 artifact into the universal model, and
what it demonstrates is Deliverable 3's success criterion: PYTHON becomes a TYPE, and the four
Python-specific measurements Ω-1 carries as FIELDS — statements, callables, imports, module —
become ``metadata`` on an artifact whose shape knows nothing about Python. The Ω-1 verdicts survive
the lift as metadata too, so no governance fact is lost in translation.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.omega_infinite.artifact import PYTHON, Artifact, Authority, Location
from engine.omega_infinite.classification import RULE_SUFFIX
from engine.omega_infinite.knowledge_space import repository_space
from engine.omega_infinite.provider import Selector

#: Ω-1's hard-coded query, as DATA. This single value is the assumption Phase 1 relocated: it was
#: ``"*.py"`` spliced into an argv list with no seam around it, and it is now an argument with a
#: name, a docstring and a test.
PYTHON_ONLY = Selector(patterns=("*.py",))

#: The provider identifier Ω-1 implicitly used. Named so the equivalence report can state which
#: mechanism produced the population it compared against.
LEGACY_PROVIDER = "git"


def tracked_python_via_abstraction(root: str) -> tuple[str, ...]:
    """Ω-1's population, computed entirely through the Phase 1 abstractions.

    Reads as a sentence about spaces and selectors rather than about git and Python, and returns the
    identical tuple. No call site here names a subprocess, a suffix filter or a repository layout.
    """
    space = repository_space(root)
    return space.discover(PYTHON_ONLY).locators()


@dataclass(frozen=True)
class Equivalence:
    """The two-directional comparison. ``identical`` is the whole of Deliverable 7.

    BOTH DIRECTIONS ARE CARRIED, because a one-directional check is satisfied by a subset. "Every
    file Ω-1 found is in my population" is true of a population containing every file in the
    universe, and would hide exactly the over-collection defect a widened default enumeration is
    most likely to introduce.
    """

    legacy: tuple[str, ...]
    abstracted: tuple[str, ...]

    @property
    def only_in_legacy(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.legacy) - set(self.abstracted)))

    @property
    def only_in_abstraction(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.abstracted) - set(self.legacy)))

    @property
    def identical(self) -> bool:
        """Tuple equality, so ORDER is part of the claim and not only membership."""
        return self.legacy == self.abstracted

    def as_record(self) -> dict[str, object]:
        return {
            "legacy_mechanism": "engine.universal_discovery.discovery.tracked_python",
            "abstracted_mechanism": (
                f"knowledge_space.repository_space -> provider {LEGACY_PROVIDER!r} -> "
                f"Selector(patterns={list(PYTHON_ONLY.patterns)})"
            ),
            "legacy_count": len(self.legacy),
            "abstracted_count": len(self.abstracted),
            "identical": self.identical,
            "only_in_legacy": list(self.only_in_legacy),
            "only_in_abstraction": list(self.only_in_abstraction),
        }

    def summary(self) -> str:
        if self.identical:
            return (
                f"IDENTICAL — {len(self.legacy)} artifacts, same order, same membership. The "
                "abstraction reproduces Ω-1 exactly."
            )
        return (
            f"DIVERGED — legacy {len(self.legacy)}, abstracted {len(self.abstracted)}; "
            f"only-in-legacy {len(self.only_in_legacy)}, "
            f"only-in-abstraction {len(self.only_in_abstraction)}"
        )


def equivalence(root: str) -> Equivalence:
    """Measure the two mechanisms against each other over one tree.

    The legacy import is LOCAL rather than module-level, and deliberately so: this package must not
    make ``engine.universal_discovery`` an import-time dependency of the abstraction layer. Phase 1
    is additive, and an abstraction that could not load without the thing it abstracts would have
    inverted the dependency it exists to remove.
    """
    from engine.universal_discovery import discovery

    return Equivalence(discovery.tracked_python(root), tracked_python_via_abstraction(root))


def as_universal(legacy: object) -> Artifact:
    """Lift an ``engine.universal_discovery.model.Artifact`` into the universal model.

    DUCK-TYPED ON PURPOSE. Importing the legacy dataclass for an isinstance check would create the
    dependency the local import above avoids, and the fields read here are exactly the ones the Ω-1
    record documents.

    WHAT THE LIFT DEMONSTRATES. Every Python-specific field becomes metadata; the type becomes a
    value; the Ω-1 governance verdicts ride along unchanged. Nothing is discarded, and nothing
    Python-specific enters the universal shape.
    """
    path = str(getattr(legacy, "path", ""))
    if not path:
        raise ValueError("a legacy artifact with no path cannot be lifted")
    return Artifact(
        identifier=f"{LEGACY_PROVIDER}:{path}",
        location=Location(LEGACY_PROVIDER, path),
        artifact_type=PYTHON,
        classification_rule=RULE_SUFFIX,
        authority=Authority(
            owner=str(getattr(legacy, "authority", "")) or "UNRESOLVED",
            rule=str(getattr(legacy, "authority_rule", "")),
        ),
        metadata=_legacy_metadata(legacy),
    )


def _legacy_metadata(legacy: object) -> dict[str, str]:
    """Ω-1's Python measurements and dispositions, as open metadata rather than fixed fields."""
    return {
        "omega_disposition": str(getattr(legacy, "disposition", "")),
        "omega_disposition_rule": str(getattr(legacy, "disposition_rule", "")),
        "omega_reachable": str(bool(getattr(legacy, "reachable", False))).lower(),
        "omega_root": str(getattr(legacy, "root", "")),
        "python_callables": str(int(getattr(legacy, "callables", 0))),
        "python_imports": str(int(getattr(legacy, "imports", 0))),
        "python_module": str(getattr(legacy, "module", "")),
        "python_statements": str(int(getattr(legacy, "statements", 0))),
    }
