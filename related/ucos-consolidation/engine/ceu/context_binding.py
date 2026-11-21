"""CEU Context Binding (P4-F-009 remainder, WP-UCDA-028).

`engine/knowledge/ukip/confidence.py` (`ADR-0016`) proved the integration shape for
one context kind (`KNOWLEDGE`) and one entity substrate (UKDA's knowledge objects).
This module applies the identical shape to a second entity substrate — CEU's
`ExistenceUnit`, the one record type every construct in the existence substrate
already is — and a second context kind, `IDENTITY`, plus a third, `GOVERNANCE`,
demonstrating that one subject can carry more than one bound context kind at once
without a second registry, a second taxonomy, or a hardcoded category list.

No new context authority is created here. `engine.context.registry.ContextRegistry`
remains the sole registration authority (`UCXI-000001`); this module only projects
data CEU already owns (`ExistenceUnit`'s own fields, `ExistenceRegistry.supersede()`'s
recorded authority) into the shapes `engine.context.ontology` already declares for
`IDENTITY` and `GOVERNANCE` — exactly as `confidence.py` projected UKIP's own
`canonical_source`/`provenance` into `KNOWLEDGE`'s shape, inventing nothing new.
"""

from __future__ import annotations

from engine.ceu.existence import ExistenceRegistry, ExistenceUnit
from engine.context.model import ContextDeclaration, ContextRecord, ContextValue
from engine.context.registry import ACTION_REGISTER, ContextRegistry
from engine.context.taxonomy import ContextAuthority, ContextKind
from engine.registry.universal.identity import RegistryKind, deterministic_id

#: The namespace every CEU-sourced context binding is registered under.
EXISTENCE_CONTEXT_NAMESPACE = "existence"


def _natural_key(unit: ExistenceUnit) -> str:
    """The identity a context binding for `unit` is registered under.

    Keyed by `(form, key)`, not `universal_id` — a unit's constitutional identity is
    permanent once minted (CEU-001's own discipline), so this is stable across a
    unit's own supersession/resurrection cycle, exactly the population `context_binding
    for a subject` is meant to describe over that subject's whole existence, not one
    momentary state of it.
    """
    return f"{unit.form}:{unit.key}"


def _context_id(kind: ContextKind, unit: ExistenceUnit) -> str:
    """The deterministic context id a binding of `kind` for `unit` would carry."""
    namespace = f"{EXISTENCE_CONTEXT_NAMESPACE}.{kind.value}"
    return deterministic_id(RegistryKind.CONTEXT, namespace, _natural_key(unit))


# --------------------------------------------------------------------- IDENTITY ---


def identity_declaration(
    unit: ExistenceUnit,
    *,
    authority: ContextAuthority = ContextAuthority.OPERATIONAL,
    note: str = "",
) -> ContextDeclaration:
    """Build the IDENTITY context declaration for `unit`.

    `subject`/`identifier`/`authority` are projected from fields `unit` already
    carries (`title`, the EPIC/REG-AUTO-001-minted `universal_id`, and the identity
    kind that authority minted it under) — nothing here is asserted new.
    """
    values = [
        ContextValue(
            dimension="subject", value=unit.title, authority=authority, source=unit.universal_id
        ),
        ContextValue(
            dimension="identifier",
            value=unit.universal_id,
            authority=authority,
            source=unit.identity_kind or unit.form,
        ),
        ContextValue(
            dimension="authority",
            value=unit.identity_kind or "EPIC/REG-AUTO-001",
            authority=authority,
            source=unit.universal_id,
        ),
    ]
    if note:
        values.append(
            ContextValue(
                dimension="note", value=note, authority=authority, source=unit.universal_id
            )
        )
    return ContextDeclaration(
        kind=ContextKind.IDENTITY,
        namespace=f"{EXISTENCE_CONTEXT_NAMESPACE}.{ContextKind.IDENTITY.value}",
        natural_key=_natural_key(unit),
        values=tuple(values),
        authority=authority,
        boundary=unit.namespace or "universal",
        description=f"identity context for {unit.form}:{unit.key}",
    )


def bind_identity(
    context_registry: ContextRegistry,
    unit: ExistenceUnit,
    *,
    authority: ContextAuthority = ContextAuthority.OPERATIONAL,
    note: str = "",
) -> ContextRecord:
    """Register (or idempotently re-affirm) `unit`'s IDENTITY context."""
    return context_registry.register(identity_declaration(unit, authority=authority, note=note))


def identity_of(context_registry: ContextRegistry, unit: ExistenceUnit) -> str | None:
    """The bound `identifier` dimension for `unit`, or `None` if never bound."""
    found = context_registry.find(_context_id(ContextKind.IDENTITY, unit))
    if found is None:
        return None
    value = found.dimension("identifier")
    return None if value is None else value.value


# -------------------------------------------------------------------- GOVERNANCE --


#: The namespace GOVERNANCE bindings for CEU units are registered under.
GOVERNANCE_NAMESPACE = f"{EXISTENCE_CONTEXT_NAMESPACE}.{ContextKind.GOVERNANCE.value}"


def governance_natural_key(registry: ExistenceRegistry, unit: ExistenceUnit) -> str:
    """The natural key `unit`'s GOVERNANCE binding carries at its *current* state.

    Suffixed by how many supersession events `unit` has recorded, exactly as
    `confidence.py`'s `@{version}` suffix versions a knowledge confidence context —
    `ContextRegistry.supersede` requires a successor's identity to differ from its
    predecessor's, so each new `supersede()` on `unit` must earn a new natural key
    before its governance context can be re-asserted, not silently overwritten.
    """
    history = registry.supersession_history(unit.universal_id)
    return f"{_natural_key(unit)}@{len(history)}"


def governance_context_id(registry: ExistenceRegistry, unit: ExistenceUnit) -> str:
    """The deterministic context id `unit`'s *current* GOVERNANCE binding would carry."""
    return deterministic_id(
        RegistryKind.CONTEXT, GOVERNANCE_NAMESPACE, governance_natural_key(registry, unit)
    )


def governance_declaration(
    registry: ExistenceRegistry,
    unit: ExistenceUnit,
    *,
    authority: ContextAuthority = ContextAuthority.OPERATIONAL,
    note: str = "",
) -> ContextDeclaration:
    """Build the GOVERNANCE context declaration for `unit`'s current state.

    Projects `ExistenceRegistry.supersede()`'s own recorded `authority`/`note`
    (`existence.py`'s `_supersessions` history, `ADR-0023`) into GOVERNANCE's shape
    — "who governs this unit's admissibility, and under what stated policy" is
    exactly what a supersession record already answers; this only makes that
    answer queryable through UCXI rather than only through CEU's own journal.

    A unit never superseded has no history to project, so it governs under
    CEU-001 itself, the substrate's own root authority — not a subject-specific
    assertion, but a true and citable default. A resurrection is projected as a
    distinct state from the supersession it reverses (governance moves to whoever
    resurrected it), not collapsed into the same assertion — two states asserting
    identical substance under different identities would themselves violate
    UCXI's own Context Once rule (CXL-06).
    """
    history = registry.supersession_history(unit.universal_id)
    latest = history[-1] if history else None
    if latest is None:
        governing_authority = "CEU-001"
        policy = "supersession-admissibility:unsuperseded"
        decision_rights = "CEU-001 (root, unsuperseded)"
    elif latest["active"]:
        governing_authority = latest["authority"]
        policy = "supersession-admissibility:active-supersession"
        decision_rights = f"active supersession by {latest['authority']}"
    else:
        resurrected_by = latest.get("resurrected_by", "")
        governing_authority = resurrected_by or latest["authority"]
        policy = "supersession-admissibility:resurrected"
        decision_rights = (
            f"resurrected by {resurrected_by} (prior supersession by {latest['authority']})"
            if resurrected_by
            else f"superseded by {latest['authority']} (inactive)"
        )
    values = [
        ContextValue(
            dimension="authority",
            value=governing_authority,
            authority=authority,
            source=unit.universal_id,
        ),
        ContextValue(
            dimension="policy", value=policy, authority=authority, source=unit.universal_id
        ),
        ContextValue(
            dimension="decision_rights",
            value=decision_rights,
            authority=authority,
            source=unit.universal_id,
        ),
    ]
    if note:
        values.append(
            ContextValue(
                dimension="note", value=note, authority=authority, source=unit.universal_id
            )
        )
    return ContextDeclaration(
        kind=ContextKind.GOVERNANCE,
        namespace=GOVERNANCE_NAMESPACE,
        natural_key=governance_natural_key(registry, unit),
        values=tuple(values),
        authority=authority,
        boundary=unit.namespace or "universal",
        description=f"governance context for {unit.form}:{unit.key}",
    )


def bind_governance(
    context_registry: ContextRegistry,
    existence_registry: ExistenceRegistry,
    unit: ExistenceUnit,
    *,
    authority: ContextAuthority = ContextAuthority.OPERATIONAL,
    note: str = "",
) -> ContextRecord:
    """Register (or idempotently re-affirm) `unit`'s current GOVERNANCE context.

    Raises :class:`~engine.context.errors.DuplicateContextError` if a *different*
    governance projection was already asserted for this exact supersession-count —
    that should not happen (the projection is a pure function of `unit`'s recorded
    history), so a collision here means the history changed between two reads of it,
    not a legitimate correction; a correction belongs to :func:`resupersede_governance`.
    """
    declaration = governance_declaration(existence_registry, unit, authority=authority, note=note)
    return context_registry.register(declaration)


def resupersede_governance(
    context_registry: ContextRegistry,
    existence_registry: ExistenceRegistry,
    predecessor_context_id: str,
    unit: ExistenceUnit,
    *,
    authority: ContextAuthority = ContextAuthority.OPERATIONAL,
    note: str = "",
) -> ContextRecord:
    """Correct `unit`'s GOVERNANCE binding, retaining the predecessor (append-only).

    Call this after a new `ExistenceRegistry.supersede()` on `unit`: the bumped
    supersession count gives the new declaration a natural key distinct from
    `predecessor_context_id`'s, which `ContextRegistry.supersede` requires of a
    successor — the same discipline `confidence.py`'s `resupersede_confidence`
    documents for a bumped knowledge version.
    """
    declaration = governance_declaration(existence_registry, unit, authority=authority, note=note)
    return context_registry.supersede(predecessor_context_id, declaration)


def governance_of(
    context_registry: ContextRegistry, existence_registry: ExistenceRegistry, unit: ExistenceUnit
) -> ContextRecord | None:
    """The active GOVERNANCE record bound to `unit`'s current state, or `None`."""
    return context_registry.find(governance_context_id(existence_registry, unit))


def governance_history(
    context_registry: ContextRegistry, unit: ExistenceUnit
) -> tuple[ContextRecord, ...]:
    """Every GOVERNANCE context ever bound for `unit`, oldest first.

    Ordered by the registry's own append-only audit sequence, never a clock — the
    same historical-reconstruction discipline `engine.knowledge.ukip.confidence.
    confidence_history()` already established for the `KNOWLEDGE` kind. Matched by
    natural-key prefix (`{form}:{key}@`) since each supersession state carries its
    own suffixed natural key.
    """
    prefix = f"{_natural_key(unit)}@"
    matches = {
        record.context_id: record
        for record in context_registry.by_kind(ContextKind.GOVERNANCE)
        if record.namespace == GOVERNANCE_NAMESPACE and record.natural_key.startswith(prefix)
    }
    order = {
        entry.subject: entry.sequence
        for entry in context_registry.audit()
        if entry.action == ACTION_REGISTER and entry.subject in matches
    }
    return tuple(matches[cid] for cid in sorted(matches, key=lambda cid: order.get(cid, 0)))


__all__ = [
    "EXISTENCE_CONTEXT_NAMESPACE",
    "GOVERNANCE_NAMESPACE",
    "identity_declaration",
    "bind_identity",
    "identity_of",
    "governance_natural_key",
    "governance_context_id",
    "governance_declaration",
    "bind_governance",
    "resupersede_governance",
    "governance_of",
    "governance_history",
]
