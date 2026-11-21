"""UCPA-000001 Part 02 — the measurements.

``ucpa-declaration.json`` names a check, :data:`LAW_CHECKS` implements it, and
:meth:`AlignmentContract.validate` refuses any disagreement in either direction.

Every check reads a file the repository already owns, at a path the declaration names.
None is satisfied by a constant in this module: there is no primitive name, no facet
name, no ``ONT-*`` id and no repository path anywhere below. That is the whole point —
a gate whose answer is baked into its own source measures nothing.

The facet side of ``UCPA-L-03`` is **imported** from :mod:`engine.uckp.facets` rather
than restated, so the mapping cannot silently drift from the model it maps. If a
thirty-fourth facet is ever admitted, this gate closes until the reduction covers it,
which is the correct behaviour: a new universal question every object must answer is a
constitutional amendment, and it must not pass unnoticed.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any

from engine.root_ontology.model import (
    ROLE_AUTHORITY,
    ROLE_SUPERSEDED,
    AlignmentContract,
    AlignmentError,
    Primitive,
)

_DECLARATION = os.path.join("00-MASTER", "UCPA-000001", "ucpa-declaration.json")


def repo_root() -> str:
    """Return the repository root, derived from this file's location."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_declaration(path: str | None = None) -> dict[str, Any]:
    """Read and parse the declaration, or fail closed."""
    target = path or os.path.join(repo_root(), _DECLARATION)
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError as error:
        raise AlignmentError("the declaration is absent", subject=target) from error
    except json.JSONDecodeError as error:
        raise AlignmentError(
            f"the declaration is not valid JSON ({error})", subject=target
        ) from error
    if not isinstance(document, dict):
        raise AlignmentError("the declaration is not an object", subject=target)
    return document


def load_contract(path: str | None = None) -> AlignmentContract:
    """Rehydrate the contract and refuse one that could not be measured."""
    contract = AlignmentContract.of(load_declaration(path))
    problems = contract.validate(frozenset(LAW_CHECKS))
    if problems:
        raise AlignmentError(
            "the declaration and the implemented checks disagree: " + "; ".join(problems)
        )
    return contract


def _read_text(repo: str, relpath: str) -> str | None:
    """Return the text at ``relpath``, or None when it cannot be read."""
    try:
        with open(os.path.join(repo, relpath), encoding="utf-8") as handle:
            return handle.read()
    except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError, PermissionError):
        return None


def _read_json(repo: str, relpath: str) -> Any:
    """Return the parsed JSON at ``relpath``, or None when it cannot be read."""
    text = _read_text(repo, relpath)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def check_primitives_are_declared_by_the_register(
    contract: AlignmentContract, repo: str
) -> tuple[str, ...]:
    """UCPA-L-01 — every bound primitive is an element the canonical register carries.

    Both the identifier and the element name must appear. Matching on the id alone would
    accept a register that had renamed the element out from under the binding; matching
    on the name alone would accept one that had renumbered it.
    """
    register = _read_text(repo, contract.source.canonical_owner)
    if register is None:
        return (f"the canonical owner cannot be read: {contract.source.canonical_owner}",)
    violations: list[str] = []
    for primitive in contract.primitives:
        if primitive.identifier not in register:
            violations.append(
                f"{primitive.identifier}: absent from the canonical owner "
                f"{contract.source.canonical_owner}"
            )
        elif primitive.element not in register:
            violations.append(
                f"{primitive.identifier}: the canonical owner carries the id but not the "
                f"element name {primitive.element!r}"
            )
    return tuple(violations)


def check_standing_matches_the_ratification_record(
    contract: AlignmentContract, repo: str
) -> tuple[str, ...]:
    """UCPA-L-02 — standing is read from the ratification record, not asserted here."""
    record = _read_text(repo, contract.source.ratification_record)
    if record is None:
        return (f"the ratification record cannot be read: {contract.source.ratification_record}",)
    rows = [line for line in record.splitlines() if line.strip()]
    violations: list[str] = []
    for ratified in contract.ratified_standing:
        matching = [line for line in rows if ratified.supersession_id in line]
        if not matching:
            violations.append(
                f"{ratified.supersession_id}: no row in "
                f"{contract.source.ratification_record} names this supersession"
            )
            continue
        if not any(ratified.evidence_phrase in line for line in matching):
            violations.append(
                f"{ratified.supersession_id}/{ratified.element}: the record does not carry "
                f"the declared evidence phrase {ratified.evidence_phrase!r}"
            )
            continue
        bound = next((p for p in contract.primitives if p.element == ratified.element), None)
        if bound is None:
            violations.append(
                f"{ratified.supersession_id}: the record ratifies {ratified.element}, which "
                f"no primitive binds"
            )
        elif bound.standing != ratified.requires_standing:
            violations.append(
                f"{bound.identifier}: bound as {bound.standing} but "
                f"{ratified.supersession_id} ratifies it as {ratified.requires_standing}"
            )
    return tuple(violations)


def check_facet_reduction_covers_the_facet_model(
    contract: AlignmentContract, repo: str
) -> tuple[str, ...]:
    """UCPA-L-03 — total and single-valued over the live, imported facet enumeration."""
    del repo
    try:
        from engine.uckp.facets import Facet
    except ImportError as error:  # pragma: no cover - the import is a hard dependency
        return (f"the facet model cannot be imported: {error}",)

    live = {facet.value for facet in Facet}
    bound = {primitive.identifier for primitive in contract.primitives}
    violations: list[str] = []
    seen: set[str] = set()
    for reduction in contract.reductions:
        if reduction.facet in seen:
            violations.append(f"{reduction.facet}: reduced more than once")
        seen.add(reduction.facet)
        if reduction.facet not in live:
            violations.append(f"{reduction.facet}: not a facet the facet model declares")
        if reduction.primitive not in bound:
            violations.append(
                f"{reduction.facet}: reduces to {reduction.primitive}, which no primitive binds"
            )
    for uncovered in sorted(live - seen):
        violations.append(f"{uncovered}: the facet model declares it and no reduction covers it")
    return tuple(violations)


def check_no_reduction_targets_the_axiom(contract: AlignmentContract, repo: str) -> tuple[str, ...]:
    """UCPA-L-04 — nothing anchors to the axiom, because the axiom is not a node."""
    del repo
    violations: list[str] = []
    for reduction in contract.reductions:
        primitive = contract.primitive(reduction.primitive)
        if primitive is not None and primitive.is_axiom:
            violations.append(
                f"{reduction.facet}: reduces to {primitive.identifier} "
                f"({primitive.element}), which is the axiom and is not an addressable node"
            )
    return tuple(violations)


def check_projections_resolve_and_supersessions_are_real(
    contract: AlignmentContract, repo: str
) -> tuple[str, ...]:
    """UCPA-L-05 — a classification naming a file nobody can open governs nothing."""
    violations: list[str] = []
    for projection in contract.projections:
        if _read_text(repo, projection.path) is None:
            violations.append(
                f"{projection.identifier}: names a file that cannot be read: {projection.path}"
            )
            continue
        if projection.role != ROLE_SUPERSEDED:
            continue
        if not projection.superseded_by:
            violations.append(
                f"{projection.identifier}: classified {ROLE_SUPERSEDED} and names no "
                f"superseding instrument"
            )
            continue
        superseding = _read_text(repo, projection.superseded_by)
        if superseding is None:
            violations.append(
                f"{projection.identifier}: names superseding instrument "
                f"{projection.superseded_by}, which cannot be read"
            )
        elif projection.path not in superseding:
            violations.append(
                f"{projection.identifier}: {projection.superseded_by} does not name the "
                f"artifact it is said to supersede"
            )
    return tuple(violations)


def _owners_named_by(document: Any, binding_id: str) -> set[str]:
    """Return every ``canonical_owner`` recorded against ``binding_id`` in ``document``."""
    found: set[str] = set()
    if isinstance(document, dict):
        if document.get("id") == binding_id:
            owner = document.get("canonical_owner")
            if isinstance(owner, str):
                found.add(owner)
        for value in document.values():
            found |= _owners_named_by(value, binding_id)
    elif isinstance(document, list):
        for item in document:
            found |= _owners_named_by(item, binding_id)
    return found


def check_authority_is_single_and_matches_the_owner_binding(
    contract: AlignmentContract, repo: str
) -> tuple[str, ...]:
    """UCPA-L-06 — one authority, and it is the one the binding register already names."""
    holders = [p for p in contract.projections if p.role == ROLE_AUTHORITY]
    if len(holders) != 1:
        return (
            f"exactly one projection must hold role {ROLE_AUTHORITY}; "
            f"{len(holders)} do: {sorted(p.identifier for p in holders)}",
        )
    violations: list[str] = []
    holder = holders[0]
    if holder.path != contract.source.canonical_owner:
        violations.append(
            f"{holder.identifier}: holds {ROLE_AUTHORITY} at {holder.path}, but the declared "
            f"canonical owner is {contract.source.canonical_owner}"
        )
    binding = _read_json(repo, contract.source.owner_binding)
    if binding is None:
        return (*violations, f"the owner binding cannot be read: {contract.source.owner_binding}")
    owners = _owners_named_by(binding, contract.source.owner_binding_id)
    if not owners:
        violations.append(
            f"{contract.source.owner_binding} declares no canonical owner under "
            f"{contract.source.owner_binding_id}"
        )
    elif contract.source.canonical_owner not in owners:
        violations.append(
            f"{contract.source.owner_binding_id} names {sorted(owners)} as canonical owner, "
            f"not {contract.source.canonical_owner}"
        )
    return tuple(violations)


def check_the_primitive_set_admits_a_future_member(
    contract: AlignmentContract, repo: str
) -> tuple[str, ...]:
    """UCPA-L-07 — openness measured, not claimed.

    A synthetic primitive is admitted into a copy of the binding. The copy must remain
    usable and every pre-existing primitive must be unchanged afterwards: admission is an
    append, and an append that reclassifies a sibling is not an append.
    """
    del repo
    probe = Primitive(
        identifier=contract.openness.probe_id,
        element=contract.openness.probe_element,
        standing=contract.openness.probe_standing,
        layer_order=len(contract.primitives) + 1,
        ratified_by=contract.artifact_id,
        basis="synthetic probe admitted by UCPA-L-07; never persisted",
    )
    try:
        extended = contract.extended_with(probe)
    except AlignmentError as error:
        return (f"the primitive set refused a future member, so it is closed: {error}",)
    violations: list[str] = []
    if extended.primitive(probe.identifier) is None:
        violations.append("the admitted probe is absent from the extended binding")
    for original in contract.primitives:
        carried = extended.primitive(original.identifier)
        if carried != original:
            violations.append(
                f"{original.identifier}: admission altered an existing primitive, so it is "
                f"not an append"
            )
    if contract.primitive(probe.identifier) is not None:
        violations.append("the probe leaked into the declared binding")
    return tuple(violations)


def check_the_programme_reduces_to_a_declared_primitive(
    contract: AlignmentContract, repo: str
) -> tuple[str, ...]:
    """UCPA-L-08 — the programme is subject to the law it enforces."""
    del repo
    violations: list[str] = []
    target = contract.primitive(contract.self_application.reduces_to)
    if target is None:
        violations.append(
            f"self_application reduces to {contract.self_application.reduces_to}, which no "
            f"primitive binds"
        )
    elif target.is_axiom:
        violations.append(
            f"self_application reduces to the axiom {target.identifier}, which is not an "
            f"addressable node"
        )
    if contract.self_application.measured_by not in {law.law_id for law in contract.laws}:
        violations.append(
            f"self_application names {contract.self_application.measured_by} as its measure, "
            f"which is not a declared law"
        )
    return tuple(violations)


#: Every check the declaration may name. The model refuses a law naming a check absent
#: from this mapping, and a check here that no law claims.
LAW_CHECKS: dict[str, Callable[[AlignmentContract, str], tuple[str, ...]]] = {
    "primitives_are_declared_by_the_register": check_primitives_are_declared_by_the_register,
    "standing_matches_the_ratification_record": check_standing_matches_the_ratification_record,
    "facet_reduction_covers_the_facet_model": check_facet_reduction_covers_the_facet_model,
    "no_reduction_targets_the_axiom": check_no_reduction_targets_the_axiom,
    "projections_resolve_and_supersessions_are_real": (
        check_projections_resolve_and_supersessions_are_real
    ),
    "authority_is_single_and_matches_the_owner_binding": (
        check_authority_is_single_and_matches_the_owner_binding
    ),
    "the_primitive_set_admits_a_future_member": check_the_primitive_set_admits_a_future_member,
    "the_programme_reduces_to_a_declared_primitive": (
        check_the_programme_reduces_to_a_declared_primitive
    ),
}


def assess(contract: AlignmentContract, repo: str) -> list[tuple[str, str, tuple[str, ...]]]:
    """Measure every law, returning ``(law_id, title, violations)`` in declaration order."""
    return [(law.law_id, law.title, LAW_CHECKS[law.check](contract, repo)) for law in contract.laws]


__all__ = ["LAW_CHECKS", "assess", "load_contract", "load_declaration", "repo_root"]
