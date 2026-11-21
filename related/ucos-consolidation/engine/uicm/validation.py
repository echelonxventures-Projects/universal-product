"""UCOS-UICM-000001 — validation of closure claims.

The probes in :mod:`engine.uicm.measurement` measure the repository. This module measures
*the measurement*. Those are different jobs, and conflating them is how a closure report
comes to certify itself: if the same code decides both "is this capability closed?" and
"is this closure claim admissible?", then a defect in the first is invisible to the second.

Each invariant is declared in ``uicm.json`` and implemented here as a probe over the run's
own artifacts. Four of them are the properties the first acceptance is required to prove,
and each is a cardinality or set comparison rather than a judgement:

    no hidden gaps          UICM-INV-10  gap count == count of cells not in a pass state
    no duplicate ownership  UICM-INV-06  every capability has exactly one owner row
    no duplicate identity   UICM-INV-07  every identity is read; the engine mints none
    no invented capability  UICM-INV-08  every capability is in both registers and the tree

The remaining invariants enforce the three closure rules the declaration states: an
unevidenced pass is refused (UICM-INV-04), a non-pass cell without a registered gap is
refused (UICM-INV-05), and an undeclared state or transition is refused (UICM-INV-12).

UICM-INV-07 deserves a note on how it can be checked at all. "UICM mints no identity" is a
claim about *code*, not about data, so the probe reads this package's own source and fails
closed if any module here constructs a capability or artifact identifier rather than
reading one. A prose assurance that nothing is minted is precisely the kind of claim that
quietly stops being true, which is the same reasoning ``engine.uckp.validation`` applies
to the canonical hashing primitive.
"""

from __future__ import annotations

import ast
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.uicm.gap import GapRegister
from engine.uicm.matrix import CanonicalOwners, ClosureMatrix
from engine.uicm.measurement import probe_names
from engine.uicm.model import (
    ClosureDeclaration,
    ClosureError,
    ClosureState,
    digest,
)
from engine.uicm.obligation import ObligationRegister
from engine.uicm.observation import ObservationRegistry

#: The validation report format.
VALIDATION_REPORT_FORMAT = "ucos-uicm-closure-validation/1.0.0"

SATISFIED = "SATISFIED"
VIOLATED = "VIOLATED"

#: Identifier-minting call shapes this package must never contain. Identity comes from the
#: canonical owners; a call to a minting helper here would be a second identity authority.
_FORBIDDEN_MINTS = ("deterministic_id", "mint", "uuid4", "uuid5", "identity_tuple")

#: Dunder hooks that would let a caller reassign or delete a sealed field. These are
#: structural rather than vocabulary, so they are named here; the *vocabulary* of forbidden
#: register verbs is read from the declaration (``registry_model.operations_forbidden``).
_FORBIDDEN_HOOKS = ("__setattr__", "__delattr__", "__setitem__", "__delitem__")

#: Modules of this package exempt from the minting probe because they *derive* record ids
#: from identity already owned elsewhere rather than minting subject identity. The
#: exemption is by module, is enumerated here in one place, and is itself measured: the
#: probe fails closed if an exempt module is absent, so the list cannot silently rot.
_DERIVED_ID_MODULES = ("obligation.py", "gap.py")


class ValidationError(ClosureError):
    """Raised only when validation itself cannot run (never for a failed invariant)."""


@dataclass(frozen=True, slots=True)
class InvariantResult:
    """One invariant's verdict, with the measurement that produced it."""

    invariant_id: str
    name: str
    verdict: str
    detail: str
    blocking: bool
    evidence: Mapping[str, Any]

    @property
    def satisfied(self) -> bool:
        return self.verdict == SATISFIED

    @property
    def blocks(self) -> bool:
        return self.blocking and not self.satisfied

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "name": self.name,
            "verdict": self.verdict,
            "detail": self.detail,
            "blocking": self.blocking,
            "evidence": dict(self.evidence),
        }


@dataclass(frozen=True, slots=True)
class ClosureValidation:
    """The validation report over one closure run."""

    results: tuple[InvariantResult, ...]

    @property
    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(r.invariant_id for r in self.results if r.blocks)

    @property
    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(r.invariant_id for r in self.results if not r.satisfied and not r.blocking)

    @property
    def accepted(self) -> bool:
        """True iff no blocking invariant is violated."""
        return not self.blocking_failures

    def result(self, invariant_id: str) -> InvariantResult:
        for candidate in self.results:
            if candidate.invariant_id == invariant_id:
                return candidate
        raise ValidationError(f"no such invariant: {invariant_id}")

    def counts(self) -> dict[str, int]:
        satisfied = sum(1 for r in self.results if r.satisfied)
        return {
            "total": len(self.results),
            "satisfied": satisfied,
            "violated": len(self.results) - satisfied,
            "blocking_violated": len(self.blocking_failures),
        }

    def to_document(self) -> dict[str, Any]:
        return {
            "format": VALIDATION_REPORT_FORMAT,
            "authority": "NONE - DERIVED TRUTH",
            "accepted": self.accepted,
            "counts": self.counts(),
            "blocking_failures": list(self.blocking_failures),
            "results": [r.to_dict() for r in self.results],
        }

    def digest(self) -> str:
        return digest(self.to_document())


def _result(
    declared: Mapping[str, Any],
    *,
    satisfied: bool,
    detail: str,
    evidence: Mapping[str, Any],
) -> InvariantResult:
    return InvariantResult(
        invariant_id=str(declared["id"]),
        name=str(declared["name"]),
        verdict=SATISFIED if satisfied else VIOLATED,
        detail=detail,
        blocking=bool(declared["blocking"]),
        evidence=dict(evidence),
    )


def validate(
    *,
    declaration: ClosureDeclaration,
    matrix: ClosureMatrix,
    obligations: ObligationRegister,
    gaps: GapRegister,
    owners: CanonicalOwners,
    observations: ObservationRegistry,
    package_root: Path,
    replay_digest: str | None = None,
) -> ClosureValidation:
    """Evaluate every declared invariant over the run's own artifacts.

    ``replay_digest`` is a second independent measurement's matrix digest. When it is
    absent, UICM-INV-13 is VIOLATED rather than skipped: determinism that nobody
    re-measured is not determinism that holds.
    """
    declared = {str(record["id"]): record for record in declaration.invariants}
    missing = sorted(set(declared) - set(_IMPLEMENTED))
    unimplemented = sorted(set(_IMPLEMENTED) - set(declared))
    if missing or unimplemented:
        raise ValidationError(
            "declared invariants and implemented probes are not in bijection: "
            f"undeclared={unimplemented} unimplemented={missing}"
        )
    context = _Context(
        declaration=declaration,
        matrix=matrix,
        obligations=obligations,
        gaps=gaps,
        owners=owners,
        package_root=Path(package_root),
        replay_digest=replay_digest,
        observations=observations,
    )
    return ClosureValidation(
        results=tuple(
            _IMPLEMENTED[invariant_id](declared[invariant_id], context)
            for invariant_id in sorted(declared)
        )
    )


@dataclass(frozen=True, slots=True)
class _Context:
    declaration: ClosureDeclaration
    matrix: ClosureMatrix
    obligations: ObligationRegister
    gaps: GapRegister
    owners: CanonicalOwners
    package_root: Path
    replay_digest: str | None
    observations: ObservationRegistry


def _inv_state_vocabulary(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    declared_states = set(ctx.declaration.state_ids)
    implemented = {state.value for state in ClosureState}
    ok = declared_states == implemented
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"{len(implemented)} states agree between declaration and state machine"
            if ok
            else "declaration and state machine disagree"
        ),
        evidence={
            "declared": sorted(declared_states),
            "implemented": sorted(implemented),
        },
    )


def _inv_probe_bijection(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    declared_probes = set(ctx.declaration.probe_names)
    implemented = set(probe_names())
    ok = declared_probes == implemented
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"{len(implemented)} probes in bijection with {len(declared_probes)} dimensions"
            if ok
            else "probes and dimensions are not in bijection"
        ),
        evidence={
            "undeclared_probes": sorted(implemented - declared_probes),
            "unimplemented_probes": sorted(declared_probes - implemented),
        },
    )


def _inv_obligation_totality(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    cell_keys = {cell.key for cell in ctx.matrix.cells}
    obligation_keys = ctx.obligations.keys()
    ok = cell_keys == obligation_keys and len(ctx.obligations) == len(ctx.matrix.cells)
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"{len(ctx.obligations)} obligations govern {len(ctx.matrix.cells)} cells"
            if ok
            else "obligation register is not total over the matrix"
        ),
        evidence={
            "cells": len(cell_keys),
            "obligations": len(ctx.obligations),
            "ungoverned_cells": sorted(cell_keys - obligation_keys)[:10],
            "chain_intact": ctx.obligations.verify(),
        },
    )


def _inv_no_unevidenced_closure(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    offenders = [
        cell.key
        for cell in ctx.matrix.cells
        if cell.state.requires_evidence and not cell.evidence_digest
    ]
    return _result(
        declared,
        satisfied=not offenders,
        detail=(
            "every cell requiring evidence carries an evidence digest"
            if not offenders
            else f"{len(offenders)} cell(s) claim a state they carry no evidence for"
        ),
        evidence={"offenders": offenders[:10], "offender_total": len(offenders)},
    )


def _inv_no_unregistered_gap(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    required = {cell.key for cell in ctx.matrix.cells if cell.state.requires_gap}
    registered = ctx.gaps.keys()
    missing = sorted(required - registered)
    extra = sorted(registered - required)
    ok = not missing and not extra
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"{len(registered)} gaps registered for {len(required)} non-pass cell(s)"
            if ok
            else "the gap register does not match the non-pass cells"
        ),
        evidence={
            "unregistered": missing[:10],
            "unmatched": extra[:10],
            "required": len(required),
            "registered": len(registered),
        },
    )


def _inv_no_duplicate_ownership(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    duplicates = {
        name: count
        for name, count in ctx.owners.capability_identity_duplicates.items()
        if count > 1
    }
    multi_impl = {
        location: len(rows) for location, rows in ctx.owners.implementation.items() if len(rows) > 1
    }
    owners_per_capability = {
        capability.name: capability.canonical_owner for capability in ctx.matrix.capabilities
    }
    ok = (
        not duplicates
        and not multi_impl
        and len(owners_per_capability) == len(ctx.matrix.capabilities)
    )
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"{len(ctx.matrix.capabilities)} capabilities carry exactly one owner each"
            if ok
            else "duplicate ownership detected"
        ),
        evidence={
            "duplicate_capability_rows": dict(sorted(duplicates.items())),
            "duplicate_implementation_rows": dict(sorted(multi_impl.items())),
        },
    )


def _inv_no_duplicate_identity(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    """Measured over this package's own source: no module here mints subject identity."""
    offenders: list[str] = []
    inspected: list[str] = []
    modules = sorted(p for p in ctx.package_root.glob("*.py"))
    for module in modules:
        inspected.append(module.name)
        if module.name in _DERIVED_ID_MODULES:
            continue
        try:
            tree = ast.parse(module.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:  # a module that will not parse is a defect
            raise ValidationError(f"uicm module does not parse: {module}") from exc
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            target = node.func
            name = (
                target.attr
                if isinstance(target, ast.Attribute)
                else target.id
                if isinstance(target, ast.Name)
                else ""
            )
            if name in _FORBIDDEN_MINTS:
                offenders.append(f"{module.name}:{node.lineno}:{name}")
    absent_exemptions = sorted(name for name in _DERIVED_ID_MODULES if name not in set(inspected))
    # Capability identities must all be traceable to the capability register.
    unread = [
        capability.name
        for capability in ctx.matrix.capabilities
        if capability.capability_id
        != str(ctx.owners.capability_identity[capability.name]["cko_id"])
    ]
    ok = not offenders and not absent_exemptions and not unread
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"{len(inspected)} module(s) mint no subject identity; "
            f"{len(ctx.matrix.capabilities)} identities read from the capability register"
            if ok
            else "identity is being minted or is not traceable to the register"
        ),
        evidence={
            "minting_calls": offenders[:10],
            "absent_exemptions": absent_exemptions,
            "untraceable_identities": unread[:10],
            "modules_inspected": len(inspected),
        },
    )


def _inv_no_invented_capability(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    tracked = set(ctx.owners.tracked)
    invented: list[str] = []
    for capability in ctx.matrix.capabilities:
        in_register = capability.name in ctx.owners.capability_identity
        in_catalogue = capability.location in ctx.owners.implementation
        on_boundary = all(path in tracked for path in capability.artifacts)
        if not (in_register and in_catalogue and on_boundary):
            invented.append(capability.name)
    return _result(
        declared,
        satisfied=not invented,
        detail=(
            f"all {len(ctx.matrix.capabilities)} capabilities exist in both registers "
            "and on the tracked boundary"
            if not invented
            else f"{len(invented)} capability(ies) are not carried by the canonical owners"
        ),
        evidence={"invented": invented[:10], "population": len(ctx.matrix.capabilities)},
    )


def _inv_no_orphan_artifact(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    population = ctx.declaration.population
    extension = str(population["artifact_extension"])
    excluded = ctx.declaration.excluded_namespaces
    roots = ctx.declaration.capability_roots
    owned = {path for capability in ctx.matrix.capabilities for path in capability.artifacts}
    orphans = [
        path
        for path in ctx.owners.tracked
        if path.endswith(extension)
        and path.startswith(tuple(f"{root}/" for root in roots))
        and path not in owned
        and not any(path.startswith(f"{root}/{ns}/") for root in roots for ns in excluded)
    ]
    return _result(
        declared,
        satisfied=not orphans,
        detail=(
            f"every tracked artifact under {', '.join(roots)} resolves to one capability"
            if not orphans
            else f"{len(orphans)} tracked artifact(s) belong to no capability"
        ),
        evidence={"orphans": orphans[:10], "orphan_total": len(orphans), "owned": len(owned)},
    )


def _inv_no_hidden_gap(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    non_pass = len(ctx.matrix.non_pass_cells())
    registered = len(ctx.gaps)
    ok = non_pass == registered
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"{registered} registered gap(s) for {non_pass} non-pass cell(s) — no gap hidden"
            if ok
            else f"{non_pass} non-pass cell(s) but {registered} registered gap(s)"
        ),
        evidence={
            "non_pass_cells": non_pass,
            "registered_gaps": registered,
            "by_class": ctx.gaps.by_class(),
        },
    )


def _inv_matrix_totality(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    expected = len(ctx.matrix.capabilities) * len(ctx.matrix.dimension_ids)
    ok = len(ctx.matrix.cells) == expected
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"{len(ctx.matrix.capabilities)} x {len(ctx.matrix.dimension_ids)} = {expected} cells"
            if ok
            else "matrix is not total"
        ),
        evidence={
            "capabilities": len(ctx.matrix.capabilities),
            "dimensions": len(ctx.matrix.dimension_ids),
            "cells": len(ctx.matrix.cells),
            "expected": expected,
        },
    )


def _inv_state_legality(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    legal = set(ctx.declaration.state_ids)
    illegal_states = [c.key for c in ctx.matrix.cells if c.state.value not in legal]
    illegal_transitions: list[str] = []
    for cell in ctx.matrix.cells:
        steps = [ClosureState.coerce(s) for s in cell.transition]
        for origin, target in zip(steps, steps[1:], strict=False):
            if not origin.may_transition_to(target):
                illegal_transitions.append(f"{cell.key}:{origin.value}->{target.value}")
    ok = not illegal_states and not illegal_transitions
    return _result(
        declared,
        satisfied=ok,
        detail=(
            "every cell state and transition is declared"
            if ok
            else "an undeclared state or transition was recorded"
        ),
        evidence={
            "illegal_states": illegal_states[:10],
            "illegal_transitions": illegal_transitions[:10],
        },
    )


def _inv_measurement_determinism(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    if ctx.replay_digest is None:
        return _result(
            declared,
            satisfied=False,
            detail="determinism was not re-measured, so it is not established",
            evidence={"replay_digest": None},
        )
    ok = ctx.replay_digest == ctx.matrix.digest()
    return _result(
        declared,
        satisfied=ok,
        detail=(
            "an independent second measurement produced an identical matrix digest"
            if ok
            else "a second measurement of the same tree produced a different digest"
        ),
        evidence={
            "first": ctx.matrix.digest(),
            "second": ctx.replay_digest,
        },
    )


def _inv_no_parallel_authority(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    programme = ctx.declaration.document["programme"]
    token = programme.get("namespace_token")
    home = str(programme["operational_home"])
    engine_home = str(programme["engine_home"])
    ok = token is None
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"no meta-constitutional namespace token claimed; writes confined to {home}"
            if ok
            else "a namespace token is claimed, which a SUBSTANTIVE programme may not do"
        ),
        evidence={
            "namespace_token": token,
            "operational_home": home,
            "engine_home": engine_home,
            "authority": str(programme["authority"]),
        },
    )


def _inv_no_enumeration(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    """No dimension vocabulary and no capability name is enumerated in the engine.

    The failure mode this guards is precise, so the measurement is precise. Two shapes are
    refused:

    * a **collection literal** carrying two or more dimension ids — that is the dimension
      vocabulary written down a second time, which is what makes a declaration stop being
      the single source;
    * a **comparison** against a dimension-id literal — that is a per-dimension branch,
      which is how a hard-coded exception enters.

    A capability name is refused anywhere at all, in any shape: the population is derived
    from the canonical owners, so no capability should ever be nameable in this package.

    What is deliberately *not* refused is a serialization key that happens to equal a
    dimension id. ``{"evidence": [...]}`` in a ``to_dict`` is a field name, not a reference
    to the Evidence Closure dimension, and a probe that conflated the two would be
    measuring Python's string identity rather than the property that matters — it would
    also push the engine towards worse names to satisfy a check.
    """
    dimensions = set(ctx.declaration.dimension_ids)
    capabilities = {capability.name for capability in ctx.matrix.capabilities}
    offenders: list[str] = []
    for module in sorted(ctx.package_root.glob("*.py")):
        try:
            tree = ast.parse(module.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:
            raise ValidationError(f"uicm module does not parse: {module}") from exc
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in capabilities:
                    offenders.append(f"{module.name}:{node.lineno}:capability:{node.value}")
                continue
            if isinstance(node, ast.List | ast.Tuple | ast.Set):
                literals = [
                    element.value
                    for element in node.elts
                    if isinstance(element, ast.Constant) and isinstance(element.value, str)
                ]
                enumerated = sorted(set(literals) & dimensions)
                if len(enumerated) >= 2:
                    offenders.append(
                        f"{module.name}:{node.lineno}:dimension-vocabulary:{','.join(enumerated)}"
                    )
            elif isinstance(node, ast.Compare):
                operands = [node.left, *node.comparators]
                for operand in operands:
                    if (
                        isinstance(operand, ast.Constant)
                        and isinstance(operand.value, str)
                        and operand.value in dimensions
                    ):
                        offenders.append(
                            f"{module.name}:{node.lineno}:dimension-branch:{operand.value}"
                        )
    return _result(
        declared,
        satisfied=not offenders,
        detail=(
            f"no dimension vocabulary is enumerated and no capability name appears "
            f"across {len(dimensions)} dimensions and {len(capabilities)} capabilities"
            if not offenders
            else f"{len(offenders)} enumerated reference(s) found in the engine"
        ),
        evidence={
            "offenders": offenders[:10],
            "offender_total": len(offenders),
            "dimensions_checked": len(dimensions),
            "capabilities_checked": len(capabilities),
        },
    )


def _inv_append_only_registers(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    """No mutating operation exists in the engine, and every record type is immutable.

    Three measurements over this package's own source, and the forbidden vocabulary is read
    from the declaration rather than written here, so tightening it is a declaration edit.

    First: no class exposes a public operation whose name is a declared forbidden verb, and
    none defines a hook that would let a caller reassign or delete a sealed field. Note
    what this deliberately does *not* flag — a local ``dict.setdefault`` while building an
    index is not a register mutation, and a probe that confused the two would be measuring
    Python rather than the property that matters.

    Second: every dataclass declared here is frozen. A mutable record would let a caller
    edit a sealed observation in place and the hash chain would not notice, because a chain
    seals what was hashed at construction rather than what the object currently holds.

    Third: no statement deletes stored state.
    """
    forbidden = tuple(
        str(verb) for verb in ctx.declaration.section("registry_model")["operations_forbidden"]
    )
    mutating: list[str] = []
    mutable_records: list[str] = []
    deletions: list[str] = []
    for module in sorted(ctx.package_root.glob("*.py")):
        try:
            tree = ast.parse(module.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:
            raise ValidationError(f"uicm module does not parse: {module}") from exc
        for node in ast.walk(tree):
            if isinstance(node, ast.Delete):
                for target in node.targets:
                    if isinstance(target, ast.Attribute | ast.Subscript):
                        deletions.append(f"{module.name}:{node.lineno}")
            if not isinstance(node, ast.ClassDef):
                continue
            for member in node.body:
                if not isinstance(member, ast.FunctionDef | ast.AsyncFunctionDef):
                    continue
                if member.name in _FORBIDDEN_HOOKS:
                    mutating.append(f"{module.name}:{member.lineno}:{node.name}.{member.name}")
                elif not member.name.startswith("_") and member.name in forbidden:
                    mutating.append(f"{module.name}:{member.lineno}:{node.name}.{member.name}")
            if _is_dataclass(node) and not _is_frozen_dataclass(node):
                mutable_records.append(f"{module.name}:{node.lineno}:{node.name}")
    ok = not mutating and not mutable_records and not deletions
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"no public operation matches the {len(forbidden)} forbidden verb(s); "
            "every declared record type is frozen; nothing deletes stored state"
            if ok
            else "a mutating operation, mutable record type or deletion was found"
        ),
        evidence={
            "mutating_operations": mutating[:10],
            "mutating_operation_total": len(mutating) + len(deletions),
            "mutable_record_types": mutable_records[:10],
            "deletions": deletions[:10],
            "forbidden_operations": list(forbidden),
            "permitted_operations": list(
                ctx.declaration.section("registry_model")["operations_permitted"]
            ),
        },
    )


def _is_dataclass(node: ast.ClassDef) -> bool:
    for decorator in node.decorator_list:
        base = decorator.func if isinstance(decorator, ast.Call) else decorator
        name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", "")
        if name == "dataclass":
            return True
    return False


def _is_frozen_dataclass(node: ast.ClassDef) -> bool:
    for decorator in node.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        for keyword in decorator.keywords:
            if (
                keyword.arg == "frozen"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is True
            ):
                return True
    return False


def _inv_observation_lineage(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    """Every observation after a coordinate's first names its predecessor; the chain holds."""
    broken_lineage: list[str] = []
    multiple_current: list[str] = []
    for key in ctx.observations.coordinates():
        lineage = ctx.observations.lineage(key)
        for position, observation in enumerate(lineage):
            expected = "" if position == 0 else lineage[position - 1].observation_id
            if observation.supersedes != expected:
                broken_lineage.append(f"{key}:{observation.observation_id}")
        current = [o for o in lineage if ctx.observations.is_current(o)]
        if len(current) != 1:
            multiple_current.append(f"{key}:{len(current)}")
    chain = ctx.observations.verify()
    ok = not broken_lineage and not multiple_current and chain
    report = ctx.observations.lineage_report()
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"{report['observation_total']} observations over "
            f"{report['coordinate_total']} coordinates; chain intact; "
            "exactly one current reading per coordinate"
            if ok
            else "observation lineage is broken"
        ),
        evidence={
            "broken_lineage": broken_lineage[:10],
            "coordinates_without_single_current": multiple_current[:10],
            "chain_intact": chain,
            "lineage": dict(report),
        },
    )


def _inv_supersession_terminality(declared: Mapping[str, Any], ctx: _Context) -> InvariantResult:
    """SUPERSEDED is terminal, every historical reading is SUPERSEDED, no current one is."""
    terminal = ClosureState.SUPERSEDED.is_terminal
    historical = ctx.observations.superseded_observations()
    misreported = [
        observation.observation_id
        for observation in historical
        if ctx.observations.effective_state(observation) is not ClosureState.SUPERSEDED
    ]
    current_superseded = [
        observation.observation_id
        for observation in ctx.observations.current_observations()
        if ctx.observations.effective_state(observation) is ClosureState.SUPERSEDED
    ]
    ok = terminal and not misreported and not current_superseded
    return _result(
        declared,
        satisfied=ok,
        detail=(
            f"SUPERSEDED is terminal; {len(historical)} historical reading(s) reported as "
            "SUPERSEDED; no current reading is"
            if ok
            else "supersession semantics are violated"
        ),
        evidence={
            "superseded_is_terminal": terminal,
            "historical_total": len(historical),
            "misreported_historical": misreported[:10],
            "current_reported_superseded": current_superseded[:10],
        },
    )


_IMPLEMENTED: Mapping[str, Any] = {
    "UICM-INV-01": _inv_state_vocabulary,
    "UICM-INV-02": _inv_probe_bijection,
    "UICM-INV-03": _inv_obligation_totality,
    "UICM-INV-04": _inv_no_unevidenced_closure,
    "UICM-INV-05": _inv_no_unregistered_gap,
    "UICM-INV-06": _inv_no_duplicate_ownership,
    "UICM-INV-07": _inv_no_duplicate_identity,
    "UICM-INV-08": _inv_no_invented_capability,
    "UICM-INV-09": _inv_no_orphan_artifact,
    "UICM-INV-10": _inv_no_hidden_gap,
    "UICM-INV-11": _inv_matrix_totality,
    "UICM-INV-12": _inv_state_legality,
    "UICM-INV-13": _inv_measurement_determinism,
    "UICM-INV-14": _inv_no_parallel_authority,
    "UICM-INV-15": _inv_no_enumeration,
    "UICM-INV-16": _inv_append_only_registers,
    "UICM-INV-17": _inv_observation_lineage,
    "UICM-INV-18": _inv_supersession_terminality,
}


def implemented_invariants() -> tuple[str, ...]:
    return tuple(sorted(_IMPLEMENTED))


def sequence_digest(results: Sequence[InvariantResult]) -> str:
    return digest([r.to_dict() for r in results])


__all__ = [
    "SATISFIED",
    "VALIDATION_REPORT_FORMAT",
    "VIOLATED",
    "ClosureValidation",
    "InvariantResult",
    "ValidationError",
    "implemented_invariants",
    "sequence_digest",
    "validate",
]
