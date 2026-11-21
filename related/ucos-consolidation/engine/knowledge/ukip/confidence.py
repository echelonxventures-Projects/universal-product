"""UKIP Part 13 — Knowledge Confidence (P4-F-003).

Confidence is not a new field on the canonical knowledge object and not a new
store. UCXI-000001 (Universal Context) already declares a ``KNOWLEDGE`` context
kind whose three required dimensions are ``source``, ``provenance`` and
``confidence`` (:mod:`engine.context.ontology`), and a real, working, append-only
:class:`~engine.context.registry.ContextRegistry` to register it in — with zero
call sites anywhere in the repository before this module. This is the integration:
it projects a UKIP :class:`~engine.knowledge.ukip.registry.RegisteredKnowledge`'s
own source and provenance into that shape, so the only new fact a caller asserts
is the confidence value itself.

Confidence is deliberately kept **out** of :class:`~engine.knowledge.cko.
CanonicalKnowledgeObject`'s content-addressed core: embedding it there would change
every existing CKO's ``content_sha256`` and would duplicate a representation UCXI
already owns. A knowledge confidence context is instead a referenceable,
independently supersedable expression — exactly as UKIP's own
:class:`~engine.knowledge.ukip.certification.KnowledgeCertificate` is computed and
offered to a caller rather than embedded in the objects it certifies.

Binding to ``(knowledge_id, version)`` rather than ``knowledge_id`` alone means a
new version of the knowledge gets its own confidence context by construction, and
correcting confidence for the *same* version is a deliberate, explicit act
(:func:`resupersede_confidence`) rather than a silent overwrite — the registry's
own Context Once rule (CXL-06) refuses a silent one for us.

Persistence of the ``ContextRegistry`` itself is a distinct, pre-existing gap,
already disclosed at ``engine/lineage/memory-layers.json`` (the "context" layer
note, companion to P4-F-009): no owner persists it to disk today. This module does
not invent one — the registry passed in is the caller's, in memory, exactly as
:mod:`engine.knowledge.ukip.certification` computes over a caller-supplied registry
without persisting its own result either.
"""

from __future__ import annotations

from engine.context.model import ContextDeclaration, ContextRecord, ContextValue
from engine.context.registry import ACTION_REGISTER, ContextRegistry
from engine.context.taxonomy import ContextAuthority, ContextKind
from engine.knowledge.ukip.registry import RegisteredKnowledge
from engine.registry.universal.identity import RegistryKind, deterministic_id

#: The namespace every knowledge confidence context is registered under.
CONFIDENCE_NAMESPACE = "knowledge"

#: The confidence dimension's name, as declared by UCXI-000001's KNOWLEDGE ontology.
CONFIDENCE_DIMENSION = "confidence"


def _source_dimension(record: RegisteredKnowledge) -> str:
    ref = record.canonical_source
    return f"{ref.provider_id}:{ref.locator}"


def confidence_natural_key(record: RegisteredKnowledge) -> str:
    """The per-version identity a confidence context for ``record`` is registered under."""
    return f"{record.knowledge_id}@{record.version}"


def confidence_context_id(record: RegisteredKnowledge) -> str:
    """The deterministic context id a confidence binding for ``record`` would carry."""
    return deterministic_id(
        RegistryKind.CONTEXT, CONFIDENCE_NAMESPACE, confidence_natural_key(record)
    )


def confidence_declaration(
    record: RegisteredKnowledge,
    *,
    confidence: str,
    authority: ContextAuthority = ContextAuthority.INFERRED,
    note: str = "",
) -> ContextDeclaration:
    """Build the KNOWLEDGE context declaration for ``record``'s confidence.

    ``source`` and ``provenance`` are projected from the record's own existing
    :attr:`RegisteredKnowledge.canonical_source` and
    :attr:`RegisteredKnowledge.provenance` — not invented.
    """
    values = [
        ContextValue(
            dimension="source",
            value=_source_dimension(record),
            authority=authority,
            source=record.canonical_source.locator,
        ),
        ContextValue(
            dimension="provenance",
            value=record.provenance.seal,
            authority=authority,
            source=record.knowledge_id,
        ),
        ContextValue(
            dimension=CONFIDENCE_DIMENSION,
            value=confidence,
            authority=authority,
            source=record.knowledge_id,
        ),
    ]
    if note:
        values.append(
            ContextValue(
                dimension="note", value=note, authority=authority, source=record.knowledge_id
            )
        )
    return ContextDeclaration(
        kind=ContextKind.KNOWLEDGE,
        namespace=CONFIDENCE_NAMESPACE,
        natural_key=confidence_natural_key(record),
        values=tuple(values),
        authority=authority,
        boundary=record.universe or "universal",
        description=f"confidence for {record.knowledge_id} @ {record.version}",
    )


def bind_confidence(
    context_registry: ContextRegistry,
    record: RegisteredKnowledge,
    *,
    confidence: str,
    authority: ContextAuthority = ContextAuthority.INFERRED,
    note: str = "",
) -> ContextRecord:
    """Register (or idempotently re-affirm) ``record``'s confidence context.

    Raises :class:`~engine.context.errors.DuplicateContextError` if a *different*
    confidence was already asserted for this exact ``(knowledge_id, version)`` — a
    correction belongs to :func:`resupersede_confidence`, not a silent overwrite.
    """
    declaration = confidence_declaration(
        record, confidence=confidence, authority=authority, note=note
    )
    return context_registry.register(declaration)


def resupersede_confidence(
    context_registry: ContextRegistry,
    predecessor_context_id: str,
    record: RegisteredKnowledge,
    *,
    confidence: str,
    authority: ContextAuthority = ContextAuthority.INFERRED,
    note: str = "",
) -> ContextRecord:
    """Correct a previously-registered confidence, retaining the predecessor (append-only).

    ``record`` must carry a natural key distinct from the predecessor's, so build it
    with a bumped :attr:`RegisteredKnowledge.version` (the normal case — a
    reassessment usually accompanies a knowledge revision) — ``ContextRegistry.
    supersede`` requires the successor's identity to differ from the predecessor's.
    """
    declaration = confidence_declaration(
        record, confidence=confidence, authority=authority, note=note
    )
    return context_registry.supersede(predecessor_context_id, declaration)


def confidence_of(context_registry: ContextRegistry, record: RegisteredKnowledge) -> str | None:
    """The active confidence value bound to ``record``'s current version, or ``None``."""
    found = context_registry.find(confidence_context_id(record))
    if found is None:
        return None
    value = found.dimension(CONFIDENCE_DIMENSION)
    return None if value is None else value.value


def confidence_history(
    context_registry: ContextRegistry, knowledge_id: str
) -> tuple[ContextRecord, ...]:
    """Every confidence context ever registered for a knowledge subject, oldest first.

    Ordered by the registry's own append-only audit sequence (never a clock), so a
    replay of the same registrations always reproduces the same order — this is
    the historical-reconstruction and resurrection surface: a superseded context
    stays queryable here alongside whatever superseded it.
    """
    prefix = f"{knowledge_id}@"
    matches = {
        record.context_id: record
        for record in context_registry.by_kind(ContextKind.KNOWLEDGE)
        if record.namespace == CONFIDENCE_NAMESPACE and record.natural_key.startswith(prefix)
    }
    order = {
        entry.subject: entry.sequence
        for entry in context_registry.audit()
        if entry.action == ACTION_REGISTER and entry.subject in matches
    }
    return tuple(matches[cid] for cid in sorted(matches, key=lambda cid: order.get(cid, 0)))


__all__ = [
    "CONFIDENCE_NAMESPACE",
    "CONFIDENCE_DIMENSION",
    "confidence_natural_key",
    "confidence_context_id",
    "confidence_declaration",
    "bind_confidence",
    "resupersede_confidence",
    "confidence_of",
    "confidence_history",
]
