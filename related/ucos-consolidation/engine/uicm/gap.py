"""UCOS-UICM-000001 — the closure gap register.

A gap here is not a complaint; it is the *receipt* for a non-closed cell. The declaration
requires that every cell in a state whose ``requires_gap`` is true has a registered gap,
and :mod:`engine.uicm.validation` refuses the run when one does not. That inversion is
what makes "no hidden gaps" a measurable property: the register is derived from the matrix
by total function, so a gap cannot be omitted without the cardinality check failing
(UICM-INV-10).

Gap identity is derived from the obligation it discharges, so the same repository measured
twice produces the same gap identifiers. A counter would make gap identity depend on
iteration order and the register would never replay.

Classification is declared, never inferred by keyword. Four classes live in
``uicm.json``, and the mapping from a measured cell to a class is a function of the cell's
*state* and its *dimension*, both of which are declared:

    ABSENT-OBLIGATION       nothing located asks the question of this capability
    REGISTRY-DRIFT          a located register is stale against the tracked boundary
    UNSATISFIED-REQUIREMENT the question was asked, measured, and not met
    UNMEASURABLE            a required input was absent, so no verdict is reachable

The distinction between the first and the third is the one that matters most when reading
the register. An ABSENT-OBLIGATION gap is not a capability failing a test; it is a test
that was never written. Reporting both as the same kind of failure would misdirect every
remediation decision made from this register.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.uicm.model import (
    Capability,
    ClosureCell,
    ClosureDeclaration,
    ClosureError,
    ClosureState,
    digest,
)
from engine.uicm.obligation import ObligationRegister

#: The gap register document format.
GAP_REGISTER_FORMAT = "ucos-uicm-gap-register/1.0.0"

#: The gap identifier prefix.
GAP_PREFIX = "UICM-GAP"

#: Declared class names, referenced by :func:`classify`. The strings name rows that must
#: exist in the declaration's ``gap_classification``; :func:`build_register` verifies the
#: reference rather than assuming it, so a renamed class fails closed instead of silently
#: producing an unclassified register.
CLASS_ABSENT_OBLIGATION = "ABSENT-OBLIGATION"
CLASS_REGISTRY_DRIFT = "REGISTRY-DRIFT"
CLASS_UNSATISFIED = "UNSATISFIED-REQUIREMENT"
CLASS_UNMEASURABLE = "UNMEASURABLE"

#: Dimensions whose OPEN state means "a located register is stale" rather than "the
#: requirement is unmet". Read from the declaration by owner reference: a dimension whose
#: owner is an identity or registration register is one whose failure is drift in that
#: register, not a defect in the capability.
_DRIFT_OWNER_REFERENCES = ("SRC-ARTIFACT-IDENTITY", "SRC-REGISTRATION")

#: Evidence markers a probe emits when nothing located asks the dimension question.
_ABSENCE_MARKER = "no located instrument"


class GapError(ClosureError):
    """Raised when the gap register cannot be derived or is incomplete."""


@dataclass(frozen=True, slots=True)
class Gap:
    """One registered closure gap, keyed to the obligation it discharges.

    The last three fields are the **resolution projection**: the instrument that closes a
    gap of this dimension, the owner of that instrument, and the located gate that validates
    the change. All three are derived — the instrument from the declared binding, the owner
    by applying the identity authority's own TOTAL ownership function to it, the gate from
    the same declared row. None is a claim this register is entitled to make on its own, and
    none can express progress: there is no status, no assignee and no timestamp here,
    because a closure is only ever a measurement and this register is only ever its receipt.
    """

    gap_id: str
    obligation_id: str
    capability_id: str
    capability_name: str
    canonical_owner: str
    dimension_id: str
    dimension_name: str
    state: ClosureState
    gap_class: str
    finding: str
    requirement: str
    discharging_owner: str
    resolution_target: str
    resolution_owner: str
    validating_gate: str
    evidence: tuple[str, ...]
    blocking: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "obligation_id": self.obligation_id,
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "canonical_owner": self.canonical_owner,
            "dimension_id": self.dimension_id,
            "dimension_name": self.dimension_name,
            "state": self.state.value,
            "gap_class": self.gap_class,
            "finding": self.finding,
            "requirement": self.requirement,
            "discharging_owner": self.discharging_owner,
            "resolution_target": self.resolution_target,
            "resolution_owner": self.resolution_owner,
            "validating_gate": self.validating_gate,
            "evidence": list(self.evidence),
            "blocking": self.blocking,
        }

    def digest(self) -> str:
        return digest(self.to_dict())


def gap_id(obligation_id: str) -> str:
    """Derive the gap identifier from the obligation it discharges (injective, no counter)."""
    return obligation_id.replace("UICM-OBL", GAP_PREFIX, 1)


def classify(cell: ClosureCell, declaration: ClosureDeclaration) -> str:
    """Assign one declared gap class to a non-closed cell.

    Precedence is deliberate. Unmeasurability outranks everything, because a verdict that
    could not be reached must never be reported as a requirement that was merely unmet.
    Absence of an obligation outranks non-satisfaction, because a question nobody asks is
    not a capability that failed.
    """
    if cell.state is ClosureState.BLOCKED:
        return CLASS_UNMEASURABLE
    if _ABSENCE_MARKER in cell.finding:
        return CLASS_ABSENT_OBLIGATION
    dimension = declaration.dimension(cell.dimension_id)
    if dimension.owner_reference in _DRIFT_OWNER_REFERENCES:
        return CLASS_REGISTRY_DRIFT
    return CLASS_UNSATISFIED


class GapRegister:
    """The registered gaps for one measurement run."""

    __slots__ = ("_by_key", "_gaps")

    def __init__(self, gaps: Sequence[Gap]) -> None:
        self._gaps = tuple(gaps)
        self._by_key = {f"{g.capability_name}:{g.dimension_id}": g for g in self._gaps}
        if len(self._by_key) != len(self._gaps):
            raise GapError("gap register carries a duplicate coordinate")

    @property
    def gaps(self) -> tuple[Gap, ...]:
        return self._gaps

    def __len__(self) -> int:
        return len(self._gaps)

    def __contains__(self, key: object) -> bool:
        return key in self._by_key

    def keys(self) -> frozenset[str]:
        """Every matrix coordinate carrying a registered gap."""
        return frozenset(self._by_key)

    def for_capability(self, capability_name: str) -> tuple[Gap, ...]:
        return tuple(g for g in self._gaps if g.capability_name == capability_name)

    def for_dimension(self, dimension_id: str) -> tuple[Gap, ...]:
        return tuple(g for g in self._gaps if g.dimension_id == dimension_id)

    def by_class(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for gap in self._gaps:
            counts[gap.gap_class] = counts.get(gap.gap_class, 0) + 1
        return dict(sorted(counts.items()))

    def by_dimension(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for gap in self._gaps:
            counts[gap.dimension_id] = counts.get(gap.dimension_id, 0) + 1
        return dict(sorted(counts.items()))

    def by_capability(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for gap in self._gaps:
            counts[gap.capability_name] = counts.get(gap.capability_name, 0) + 1
        return dict(sorted(counts.items()))

    @property
    def blocking_total(self) -> int:
        return sum(1 for gap in self._gaps if gap.blocking)

    def to_document(self) -> dict[str, Any]:
        return {
            "format": GAP_REGISTER_FORMAT,
            "authority": "NONE - DERIVED TRUTH",
            "gap_total": len(self._gaps),
            "blocking_total": self.blocking_total,
            "by_class": self.by_class(),
            "by_dimension": self.by_dimension(),
            "by_capability": self.by_capability(),
            "gaps": [gap.to_dict() for gap in self._gaps],
        }

    def digest(self) -> str:
        return digest(self.to_document())


def ownership_function(declaration: ClosureDeclaration, repo: Path) -> Callable[[str], str]:
    """The located TOTAL ownership function, loaded from the home the declaration names.

    UICM derives no ownership. The identity authority already owns the question "who owns
    this path?", publishes the rule set as declared data and binds the function that applies
    it, so this reads that function and calls it. Re-expressing those rules here would put a
    second interpretation of one law in the repository, and the two would drift — the same
    reason the state vocabulary is compared against the declaration rather than restated.

    Loaded by declared path rather than imported by name because the authority's home is a
    programme's operational memory and not an importable package. An absent home, an
    unloadable module or an unbound symbol is a refusal: an ownership answer this engine
    invented would be indistinguishable in the register from one the authority gave.
    """
    record = declaration.ownership_authority
    home = repo / str(record["home"])
    symbol = str(record["symbol"])
    spec = importlib.util.spec_from_file_location(f"uicm.ownership.{home.stem}", home)
    if spec is None or spec.loader is None:
        raise GapError("the declared ownership authority cannot be loaded", home=str(home))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - the located owner's module, reported not masked
        raise GapError(
            "the declared ownership authority did not load",
            home=str(home),
            reason=f"{type(exc).__name__}: {exc}",
        ) from exc
    function = getattr(module, symbol, None)
    if not callable(function):
        raise GapError(
            "the declared ownership authority does not bind its declared symbol",
            home=str(home),
            symbol=symbol,
        )
    return function


def build_register(
    cells: Sequence[ClosureCell],
    declaration: ClosureDeclaration,
    obligations: ObligationRegister,
    capabilities: Sequence[Capability],
    repo: Path,
) -> GapRegister:
    """Derive the gap register from the matrix by total function.

    Every cell whose state requires a gap gets exactly one, and the class names used are
    verified against the declaration so a renamed class fails closed rather than
    producing an unclassified register.

    ``capabilities`` supplies the location a capability-local resolution target resolves
    against, and ``repo`` locates the ownership authority. Both are inputs rather than
    module state, so the register stays a function of the declaration and the tree.
    """
    declared_classes = set(declaration.gap_classes)
    used = {
        CLASS_ABSENT_OBLIGATION,
        CLASS_REGISTRY_DRIFT,
        CLASS_UNSATISFIED,
        CLASS_UNMEASURABLE,
    }
    undeclared = sorted(used - declared_classes)
    if undeclared:
        raise GapError("gap classifier references undeclared gap class(es)", undeclared=undeclared)

    placeholder = declaration.location_placeholder
    locations = {capability.name: capability.location for capability in capabilities}
    derive_owner = ownership_function(declaration, repo)

    gaps: list[Gap] = []
    for cell in cells:
        if not cell.state.requires_gap:
            continue
        obligation = _obligation_for(cell, obligations)
        dimension = declaration.dimension(cell.dimension_id)
        binding = declaration.resolution_binding(cell.dimension_id)
        if cell.capability_name not in locations:
            raise GapError(
                "a gap names a capability the population does not carry",
                cell=cell.key,
            )
        target = binding.resolve(placeholder, locations[cell.capability_name])
        gaps.append(
            Gap(
                gap_id=gap_id(obligation.obligation_id),
                obligation_id=obligation.obligation_id,
                capability_id=cell.capability_id,
                capability_name=cell.capability_name,
                canonical_owner=obligation.canonical_owner,
                dimension_id=cell.dimension_id,
                dimension_name=dimension.name,
                state=cell.state,
                gap_class=classify(cell, declaration),
                finding=cell.finding,
                requirement=dimension.requirement,
                discharging_owner=obligation.discharging_owner,
                resolution_target=target,
                resolution_owner=str(derive_owner(target)),
                validating_gate=binding.gate,
                evidence=cell.evidence,
                blocking=dimension.blocking,
            )
        )
    return GapRegister(gaps)


def _obligation_for(cell: ClosureCell, obligations: ObligationRegister) -> Any:
    """Find the registered obligation governing ``cell``, or fail closed.

    A gap with no obligation would be a finding nobody owed, which is exactly the
    unowned-defect condition the obligation register exists to make impossible.
    """
    for obligation in obligations.obligations():
        if obligation.key == cell.key:
            return obligation
    raise GapError("no registered obligation governs this cell", cell=cell.key)


def classification_reference(declaration: ClosureDeclaration) -> Mapping[str, str]:
    """The declared class -> meaning mapping, for rendering the register header."""
    return declaration.gap_classes


__all__ = [
    "CLASS_ABSENT_OBLIGATION",
    "CLASS_REGISTRY_DRIFT",
    "CLASS_UNMEASURABLE",
    "CLASS_UNSATISFIED",
    "GAP_PREFIX",
    "GAP_REGISTER_FORMAT",
    "Gap",
    "GapError",
    "GapRegister",
    "build_register",
    "classification_reference",
    "classify",
    "gap_id",
    "ownership_function",
]
