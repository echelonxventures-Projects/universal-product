"""UCON-000001 Part 07 — self-extension. Nine subjects, one mechanism.

An ontology that can declare an ontology, a governance that can govern governance, a
verification that can verify verification, a location framework that can grow an axis, a
temporal framework that can grow a reference system, an identity framework that can grow a
namespace — these are six separate requirements, and the tempting implementation is six
subsystems. This module is the argument against that. All nine declared extension points take
the same path: **register a construct**. An ontology is a construct of kind ``ontology``; a
governance rule is a construct of kind ``governance-rule``; a verifier is a construct of kind
``verifier``; a location axis, a temporal system and an identity namespace are constructs of
their kinds. There is therefore one extension mechanism to verify rather than nine, and law
UCON-L-09 verifies it by walking the declared points and performing every admission in memory.

Two of the nine extend the foundation's own vocabularies, which needs the extra care:
registering a disposition or a reality state must extend the *declaration*, not just the
registry. That is done by :func:`extended_with_disposition` and
:func:`extended_with_reality_state`, which are **non-mutating** — they return a new
:class:`~engine.construct.declaration.Declaration` via ``dataclasses.replace`` and leave the
original untouched — and adopted through :meth:`ConstructRegistry.adopt`, which refuses any
narrowing. A comment claiming a vocabulary is append-only is not evidence; a non-mutating
extension that is then checked for narrowing is.

What this module does NOT do is take ownership of what it extends. Registering a construct of
kind ``location-axis`` does not make ``engine/context/location.py`` resolve a new axis, and
registering a ``temporal-system`` does not teach ``engine/temporal`` a new conversion. Those
owners are named in the declaration for each point, and the construct registered here is the
*governed representation* of an extension referred to its owner — the disposition, the lineage,
the evidence and the trace. Claiming otherwise would be this capability quietly becoming a
second authority over six frameworks it does not own, which is precisely the failure the
declaration's ``$not_a_second_authority`` note refuses.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import replace
from typing import Any

from engine.construct.declaration import (
    Declaration,
    DispositionSpec,
    ExtensionPoint,
    KindSpec,
    RealitySpec,
)
from engine.construct.model import Construct, ConstructError, Evidence, Lineage, Presentation
from engine.construct.registry import ConstructRegistry


class ExtensionError(ConstructError):
    """An extension the declaration or the model refuses."""


# --- non-mutating declaration extension --------------------------------------------------------


def extended_with_kind(
    declaration: Declaration,
    kind: str,
    *,
    definition: str,
    facet: str = "none",
    parent: str | None = None,
    title: str = "",
) -> Declaration:
    """A new declaration carrying one more kind. The original is untouched.

    Note that registering a kind does not *require* this: :attr:`ConstructRegistry.registered_kinds`
    derives openness from the record, so a runtime kind works without ever touching the
    declaration. This function exists for the case where the new kind must also carry a facet the
    declaration can validate payloads against.
    """
    if any(spec.kind == kind for spec in declaration.kinds):
        raise ExtensionError(f"kind {kind!r} is already declared")
    if facet not in declaration.facets:
        raise ExtensionError(f"facet {facet!r} is not declared")
    return replace(
        declaration,
        kinds=(
            *declaration.kinds,
            KindSpec(
                kind=kind,
                title=title or kind,
                facet=facet,
                parent=parent,
                definition=definition,
            ),
        ),
    )


def extended_with_disposition(
    declaration: Declaration,
    identifier: str,
    *,
    definition: str,
    permits: Iterable[str],
    successors: Iterable[str],
    title: str = "",
) -> Declaration:
    """A new declaration carrying one more disposition. Never terminal, and never mutating.

    ``terminal`` is not a parameter. A registered disposition is non-terminal by construction,
    because law UCON-L-10 requires that nothing be permanently closed and an extension that could
    introduce a terminal disposition would let a caller close the door the foundation exists to
    keep open.
    """
    if any(spec.identifier == identifier for spec in declaration.dispositions):
        raise ExtensionError(f"disposition {identifier!r} is already declared")
    acts = set(declaration.operational_acts)
    requested = {str(act) for act in permits}
    undeclared = requested - acts
    if undeclared:
        raise ExtensionError(
            f"disposition {identifier!r} permits undeclared acts: {', '.join(sorted(undeclared))}"
        )
    onward = tuple(str(item) for item in successors)
    if not onward:
        raise ExtensionError(
            f"disposition {identifier!r} names no successor, which would make it terminal "
            "and permanently close every construct that reached it (UCON-L-10)"
        )
    known = set(declaration.disposition_ids)
    for successor in onward:
        if successor not in known:
            raise ExtensionError(
                f"disposition {identifier!r} names undeclared successor {successor!r}"
            )
    return replace(
        declaration,
        dispositions=(
            *declaration.dispositions,
            DispositionSpec(
                identifier=identifier,
                title=title or identifier,
                definition=definition,
                terminal=False,
                permits=frozenset(requested),
                successors=onward,
            ),
        ),
    )


def extended_with_reality_state(
    declaration: Declaration,
    identifier: str,
    *,
    definition: str,
    permits: Iterable[str],
    successors: Iterable[str],
    evidence_floor: int = 0,
    independent_sources_floor: int = 0,
    ceu_binding: Mapping[str, str] | None = None,
    binding_gap: Mapping[str, Any] | None = None,
    title: str = "",
) -> Declaration:
    """A new declaration carrying one more reality state. Non-terminal, non-mutating, bound.

    A state that binds to no UCOS-CEU-001 row must disclose why, exactly as the declared states
    do. That is what stops the reality vocabulary from drifting into a private copy of somebody
    else's existence vocabulary one runtime registration at a time.
    """
    if any(spec.identifier == identifier for spec in declaration.reality_states):
        raise ExtensionError(f"reality state {identifier!r} is already declared")
    acts = set(declaration.operational_acts)
    requested = {str(act) for act in permits}
    undeclared = requested - acts
    if undeclared:
        raise ExtensionError(
            f"reality state {identifier!r} permits undeclared acts: "
            f"{', '.join(sorted(undeclared))}"
        )
    onward = tuple(str(item) for item in successors)
    if not onward:
        raise ExtensionError(
            f"reality state {identifier!r} names no successor, which would make it a state "
            "nothing can leave — including by falsification (UCON-L-10)"
        )
    known = set(declaration.reality_ids)
    for successor in onward:
        if successor not in known:
            raise ExtensionError(
                f"reality state {identifier!r} names undeclared successor {successor!r}"
            )
    if ceu_binding is None and not binding_gap:
        raise ExtensionError(
            f"reality state {identifier!r} binds to no CEU row and discloses no gap; one or "
            "the other is required (UCON-L-14)"
        )
    return replace(
        declaration,
        reality_states=(
            *declaration.reality_states,
            RealitySpec(
                identifier=identifier,
                title=title or identifier,
                definition=definition,
                evidence_floor=evidence_floor,
                independent_sources_floor=independent_sources_floor,
                permits=frozenset(requested),
                successors=onward,
                ceu_binding=(dict(ceu_binding) if ceu_binding else None),
                binding_gap=(dict(binding_gap) if binding_gap else None),
            ),
        ),
    )


# --- the public registrations --------------------------------------------------------------------


def register_kind(
    registry: ConstructRegistry,
    kind: str,
    *,
    definition: str,
    facet: str = "none",
    parent: str | None = None,
    declared_by: str,
    extend_declaration: bool = False,
) -> Construct:
    """Register a construct kind. This is the whole of "the model handles a future category".

    No schema changes, no enum grows, and no file in ``engine/construct/`` is touched. The kind
    becomes registered because a construct of the reflective kind was presented and admitted for
    it, and :attr:`ConstructRegistry.registered_kinds` derives openness from that record rather
    than from any table. Law UCON-L-08 fingerprints this package's source before and after
    admitting categories nobody has ever declared, and refuses if a byte moved.
    """
    if extend_declaration:
        registry.adopt(
            extended_with_kind(
                registry.declaration, kind, definition=definition, facet=facet, parent=parent
            )
        )
    return registry.present(
        Presentation(
            kind=registry.declaration.reflective_root,
            natural_key=kind,
            title=kind,
            payload={
                "definition": definition,
                "facet": facet,
                **({"parent": parent} if parent else {}),
            },
            evidence=(Evidence(source=declared_by, statement=f"declares kind {kind!r}"),),
            reality_status=registry.declaration.seed_reality_state,
            lineage=Lineage(presented_by=declared_by),
        )
    )


def register_disposition(
    registry: ConstructRegistry,
    identifier: str,
    *,
    definition: str,
    permits: Iterable[str],
    successors: Iterable[str],
    declared_by: str,
) -> Construct:
    """Register a disposition, extending the declaration additively and recording the act."""
    registry.adopt(
        extended_with_disposition(
            registry.declaration,
            identifier,
            definition=definition,
            permits=permits,
            successors=successors,
        )
    )
    return _register_extension_construct(
        registry,
        kind=_kind_carrying(registry, "disposition"),
        natural_key=identifier,
        subject=identifier,
        point_id="UCON-EP-02",
        payload={"definition": definition, "permits": sorted(str(a) for a in permits)},
        declared_by=declared_by,
    )


def register_reality_state(
    registry: ConstructRegistry,
    identifier: str,
    *,
    definition: str,
    permits: Iterable[str],
    successors: Iterable[str],
    evidence_floor: int = 0,
    independent_sources_floor: int = 0,
    ceu_binding: Mapping[str, str] | None = None,
    binding_gap: Mapping[str, Any] | None = None,
    declared_by: str,
) -> Construct:
    """Register a reality state, extending the declaration additively and recording the act."""
    registry.adopt(
        extended_with_reality_state(
            registry.declaration,
            identifier,
            definition=definition,
            permits=permits,
            successors=successors,
            evidence_floor=evidence_floor,
            independent_sources_floor=independent_sources_floor,
            ceu_binding=ceu_binding,
            binding_gap=binding_gap,
        )
    )
    return _register_extension_construct(
        registry,
        kind=_kind_carrying(registry, "reality-state"),
        natural_key=identifier,
        subject=identifier,
        point_id="UCON-EP-03",
        payload={"definition": definition, "evidence_floor": evidence_floor},
        declared_by=declared_by,
    )


def register_extension(
    registry: ConstructRegistry,
    *,
    kind: str,
    natural_key: str,
    subject: str,
    point_id: str,
    payload: Mapping[str, Any] | None = None,
    declared_by: str,
    derived_from: Iterable[str] = (),
) -> Construct:
    """Register an extension of a framework this capability does not own.

    The construct is the governed *representation* of the extension — disposed, traced, and
    referred to the owner the declaration names for that point. It does not make the owner
    behave differently, and the docstring says so because a reader who assumed otherwise would
    believe a location axis registered here becomes resolvable in ``engine/context``.
    """
    point = registry.declaration.extension_point(point_id)
    if registry.facet_of(kind) != "extension":
        raise ExtensionError(
            f"kind {kind!r} does not carry the extension facet, so it cannot represent an "
            "extension of another framework"
        )
    return _register_extension_construct(
        registry,
        kind=kind,
        natural_key=natural_key,
        subject=subject,
        point_id=point.point_id,
        payload=payload,
        declared_by=declared_by,
        derived_from=derived_from,
    )


def register_verifier(
    registry: ConstructRegistry,
    *,
    natural_key: str,
    verifies: str,
    assumptions: Iterable[str],
    limitations: Iterable[str],
    declared_by: str,
    lineage_of: str = "",
    evidence: Iterable[Evidence] = (),
    reality_status: str = "",
) -> Construct:
    """Register a verifier. Assumptions and limitations are required, and that is the point.

    A verifier that declares neither is a verifier nothing can verify: there is no way to ask
    whether its assumptions hold or whether the question at hand is inside its limits, so its
    verdict has to be taken on trust. Law UCON-L-12 measures the refusal, and it is a refusal
    rather than a facet violation because admitting an unverifiable verifier would let it start
    certifying things immediately.
    """
    stated = tuple(str(item) for item in assumptions if str(item).strip())
    limits = tuple(str(item) for item in limitations if str(item).strip())
    if not stated:
        raise ExtensionError(
            f"verifier {natural_key!r} declares no assumptions; a verifier whose assumptions "
            "are unstated cannot itself be verified (UCON-L-12)"
        )
    if not limits:
        raise ExtensionError(
            f"verifier {natural_key!r} declares no limitations; a verifier that claims none is "
            "claiming to decide everything (UCON-L-12)"
        )
    return registry.present(
        Presentation(
            kind=_kind_carrying(registry, "verifier"),
            natural_key=natural_key,
            title=f"verifier of {verifies}",
            payload={
                "assumptions": list(stated),
                "limitations": list(limits),
                "verifies": verifies,
                **({"lineage_of": lineage_of} if lineage_of else {}),
            },
            evidence=tuple(evidence),
            reality_status=reality_status,
            lineage=Lineage(
                derived_from=((lineage_of,) if lineage_of else ()), presented_by=declared_by
            ),
        )
    )


def _kind_carrying(registry: ConstructRegistry, kind: str) -> str:
    """Confirm the kind is declared, and return it. A typo becomes a fault, not an empty view."""
    return registry.declaration.kind(kind).kind


def _register_extension_construct(
    registry: ConstructRegistry,
    *,
    kind: str,
    natural_key: str,
    subject: str,
    point_id: str,
    payload: Mapping[str, Any] | None,
    declared_by: str,
    derived_from: Iterable[str] = (),
) -> Construct:
    point = registry.declaration.extension_point(point_id)
    return registry.present(
        Presentation(
            kind=kind,
            natural_key=natural_key,
            title=f"{point.subject}: {subject}",
            payload={
                **dict(payload or {}),
                "extension_point": point.point_id,
                "referred_to": point.owner,
                "subject": subject,
            },
            evidence=(
                Evidence(
                    source=declared_by,
                    statement=f"extends {point.subject} under {point.point_id}",
                ),
            ),
            reality_status=registry.declaration.seed_reality_state,
            lineage=Lineage(derived_from=tuple(derived_from), presented_by=declared_by),
        )
    )


# --- the declared admissions, exercised generically -----------------------------------------------
#
# One probe adapter per declared admission name, so law UCON-L-09 can walk the declared points
# and perform every admission without knowing what any of them is. Each probe derives its key
# from the declared probe prefix and the point id, which makes it identifiable by inspection and
# unable to collide with a governed registration.


def _probe_key(registry: ConstructRegistry, point: ExtensionPoint) -> str:
    return f"{registry.declaration.probe_key_prefix}-{point.point_id}"


def _admit_kind(registry: ConstructRegistry, point: ExtensionPoint) -> Construct:
    return register_kind(
        registry,
        _probe_key(registry, point),
        definition=f"in-memory exercise of {point.point_id}",
        declared_by=point.exercised_by,
    )


def _admit_disposition(registry: ConstructRegistry, point: ExtensionPoint) -> Construct:
    return register_disposition(
        registry,
        _probe_key(registry, point),
        definition=f"in-memory exercise of {point.point_id}",
        permits=(registry.declaration.operational_acts[0],),
        successors=(registry.declaration.disposition_ids[0],),
        declared_by=point.exercised_by,
    )


def _admit_reality_state(registry: ConstructRegistry, point: ExtensionPoint) -> Construct:
    return register_reality_state(
        registry,
        _probe_key(registry, point),
        definition=f"in-memory exercise of {point.point_id}",
        permits=(registry.declaration.operational_acts[0],),
        successors=(registry.declaration.initial_reality_state,),
        binding_gap={
            "gap_id": f"{point.point_id}-PROBE",
            "finding": "a probe state binds to no CEU row by construction",
        },
        declared_by=point.exercised_by,
    )


def _admit_extension(registry: ConstructRegistry, point: ExtensionPoint) -> Construct:
    return register_extension(
        registry,
        kind=point.kind,
        natural_key=_probe_key(registry, point),
        subject=f"exercise of {point.subject}",
        point_id=point.point_id,
        declared_by=point.exercised_by,
    )


def _admit_verifier(registry: ConstructRegistry, point: ExtensionPoint) -> Construct:
    return register_verifier(
        registry,
        natural_key=_probe_key(registry, point),
        verifies=point.subject,
        assumptions=(f"the declaration of {point.point_id} is readable",),
        limitations=("decides nothing outside the exercise it performs",),
        declared_by=point.exercised_by,
    )


#: The implemented admissions, keyed by the name an extension point declares. Two-way bound to
#: the declared points at load: nothing here may go unclaimed, and no point may name an absent one.
ADMISSIONS: Mapping[str, Callable[[ConstructRegistry, ExtensionPoint], Construct]] = {
    "register_disposition": _admit_disposition,
    "register_extension": _admit_extension,
    "register_kind": _admit_kind,
    "register_reality_state": _admit_reality_state,
    "register_verifier": _admit_verifier,
}


def available_admissions() -> frozenset[str]:
    """The admission names this module implements — the set the declaration is bound against."""
    return frozenset(ADMISSIONS)


def exercise(registry: ConstructRegistry, point_id: str) -> Construct:
    """Perform the declared admission for one extension point, in memory.

    The whole of law UCON-L-09's mechanism. A point whose admission cannot be performed is a
    declared extensibility claim that is not true, and this is where that becomes measurable
    instead of documented.
    """
    point = registry.declaration.extension_point(point_id)
    admission = ADMISSIONS.get(point.admission)
    if admission is None:
        raise ExtensionError(
            f"{point.point_id}: admission {point.admission!r} is declared but not implemented"
        )
    return admission(registry, point)


__all__ = [
    "ADMISSIONS",
    "ExtensionError",
    "available_admissions",
    "exercise",
    "extended_with_disposition",
    "extended_with_kind",
    "extended_with_reality_state",
    "register_disposition",
    "register_extension",
    "register_kind",
    "register_reality_state",
    "register_verifier",
]
