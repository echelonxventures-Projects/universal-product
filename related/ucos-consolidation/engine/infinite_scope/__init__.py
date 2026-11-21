"""UISD-000001 — Universal Infinite Scope and Direction, as executable law.

AUTHORITY = NONE (DERIVED TRUTH). This package legislates nothing. It is not superior to
CMG-000001 (law owner), UCIC-001 (lifecycle owner) or CEP-009 (evolution authority): it
declares no lifecycle stage, opens no registry, consumes no counter and issues no
identifier. Its subject is a *property* of instruments, never an instrument.

The property: scope, direction, relationship and evolution capacity are unbounded for
every UCOS object — and for this principle itself. That was already certified in prose by
``03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md`` (16 axes) and
``04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md`` (23 axes), but the latter states its own
limit in §4 — no exhaustive proof of absence was performed, and residual risk is confined
to the realization layers. This package computes the property over exactly that
undischarged space, on every ``./verify.sh`` run.

What it does NOT assert, because the assertion would be false and would get the gate
disabled: that no enumeration is closed anywhere. ``engine/uckp/facets.py`` closes 33
facets deliberately, so that every vocabulary inside them can stay open — closure of the
question set is what keeps the answer sets infinite. The prohibited condition is
**undisclosed** closure: an enumeration closed in code or data while nothing states what
closes it or how a member is admitted.

Eleven laws, all held as DATA in ``00-MASTER/UISD-000001/uisd-declaration.json``. This package
contains no law text, no enumeration member, no path and no phrase.

OBSERVE MODE — READ ONLY. Stdlib only; no wall clock, no network, no subprocess; writes
nothing anywhere, including gitignored paths.
"""

from engine.infinite_scope.contract import (
    ADMISSION_FORMS,
    DECLARATION_PATH,
    LAW_CHECKS,
    assess,
    candidate_files,
    load_contract,
    load_declaration,
    repo_root,
    scan_occurrences,
)
from engine.infinite_scope.model import (
    AdmissionExercise,
    BaselineSurface,
    CapabilityEnumeration,
    ClosedEnumeration,
    DeclaredPin,
    ExerciseConsumer,
    ExpansionAxis,
    FreezeScan,
    InfiniteScopeContract,
    InfiniteScopeError,
    Law,
    PreservedSite,
)

__all__ = [
    "ADMISSION_FORMS",
    "DECLARATION_PATH",
    "LAW_CHECKS",
    "AdmissionExercise",
    "BaselineSurface",
    "CapabilityEnumeration",
    "ClosedEnumeration",
    "DeclaredPin",
    "ExerciseConsumer",
    "ExpansionAxis",
    "FreezeScan",
    "InfiniteScopeContract",
    "InfiniteScopeError",
    "Law",
    "PreservedSite",
    "assess",
    "candidate_files",
    "load_contract",
    "load_declaration",
    "repo_root",
    "scan_occurrences",
]
