"""UKI Deliverable 9 — Universal Registration Integration (EPIC-UKDA-002).

Automatically registers the constitutional entities an artifact introduces — its
**universe, capability, relationships, dependencies, decisions, evidence, and
certification** — **without duplicate registration** (``UKI-LAW-008``). Registration
is computed as an idempotent *plan* over the canonical
:class:`~engine.knowledge.store.KnowledgeBase`: any entity already present is reported
as ``already-registered`` (a no-op), and only genuinely new entities are ``registered``.

    * :class:`RegistrationEntry` — one registrable entity and its status.
    * :class:`RegistrationPlan` — the deterministic set of entries for one artifact.
    * :class:`RegistrationIntegration` — plans registration for an intent/object and
      fails closed on a *divergent duplicate* registration (same id, different content).

This layer plans only; it never writes the frozen corpus (DP-03). It reuses the UKDA
graph edge derivation verbatim, so relationships are never a second source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.graph import derive_edges
from engine.knowledge.integration.contracts import ArtifactIntent
from engine.knowledge.integration.errors import RegistrationConflictError
from engine.knowledge.model import RelationType
from engine.knowledge.store import KnowledgeBase

_REGISTERED = "registered"
_ALREADY = "already-registered"


@dataclass(frozen=True, slots=True)
class RegistrationEntry:
    """A single registrable constitutional entity and its registration status."""

    category: str
    identifier: str
    status: str
    payload: dict[str, Any]

    @property
    def is_new(self) -> bool:
        return self.status == _REGISTERED

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "identifier": self.identifier,
            "status": self.status,
            "payload": dict(self.payload),
        }


@dataclass(frozen=True, slots=True)
class RegistrationPlan:
    """The deterministic, duplication-free registration plan for one artifact."""

    target: str
    entries: tuple[RegistrationEntry, ...]

    @property
    def new_entries(self) -> tuple[RegistrationEntry, ...]:
        return tuple(e for e in self.entries if e.is_new)

    def counts(self) -> dict[str, int]:
        return {
            "total": len(self.entries),
            "registered": len(self.new_entries),
            "already_registered": len(self.entries) - len(self.new_entries),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "counts": self.counts(),
            "entries": [e.to_dict() for e in self.entries],
        }


class RegistrationIntegration:
    """Plans duplication-free registration of constitutional entities (Deliverable 9)."""

    __slots__ = ("_base", "_universes", "_edge_keys", "_certs")

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base
        self._universes = {obj.universe for obj in base.objects()}
        self._edge_keys = {edge.key() for edge in base.graph()}
        self._certs = {obj.certification for obj in base.objects() if obj.certification}

    def _status_object(self, cko_id: str) -> str:
        return _ALREADY if self._base.has_object(cko_id) else _REGISTERED

    def plan_object(self, obj: CanonicalKnowledgeObject) -> RegistrationPlan:
        """Compute the idempotent registration plan for a canonical object."""
        entries: list[RegistrationEntry] = []

        entries.append(
            RegistrationEntry(
                category="universe",
                identifier=obj.universe,
                status=_ALREADY if obj.universe in self._universes else _REGISTERED,
                payload={"universe": obj.universe},
            )
        )
        entries.append(
            RegistrationEntry(
                category="capability",
                identifier=obj.cko_id,
                status=self._status_object(obj.cko_id),
                payload={
                    "kind": obj.kind.value,
                    "authority": obj.authority.value,
                    "owner": obj.owner,
                    "lifecycle": obj.lifecycle.value,
                },
            )
        )
        for edge in derive_edges(obj):
            category = "dependency" if edge.type is RelationType.DEPENDS_ON else "relationship"
            entries.append(
                RegistrationEntry(
                    category=category,
                    identifier=f"{edge.source}-{edge.type.value}->{edge.target}",
                    status=_ALREADY if edge.key() in self._edge_keys else _REGISTERED,
                    payload=edge.to_dict(),
                )
            )
        for ref in obj.decision_links:
            entries.append(
                RegistrationEntry(
                    category="decision",
                    identifier=ref,
                    status=_ALREADY if self._base.has_decision(ref) else _REGISTERED,
                    payload={"decision": ref},
                )
            )
        for ref in obj.evidence:
            entries.append(
                RegistrationEntry(
                    category="evidence",
                    identifier=ref,
                    status=self._status_object(ref),
                    payload={"evidence": ref},
                )
            )
        if obj.certification:
            entries.append(
                RegistrationEntry(
                    category="certification",
                    identifier=obj.certification,
                    status=_ALREADY if obj.certification in self._certs else _REGISTERED,
                    payload={"certification": obj.certification},
                )
            )

        entries.sort(key=lambda e: (e.category, e.identifier))
        return RegistrationPlan(target=obj.cko_id, entries=tuple(entries))

    def plan_intent(self, intent: ArtifactIntent) -> RegistrationPlan:
        """Compute the registration plan for a proposed intent's candidate object."""
        return self.plan_object(intent.to_cko())

    def require(self, intent: ArtifactIntent) -> RegistrationPlan:
        """Plan registration, raising on a divergent duplicate registration (fail-closed)."""
        existing = self._base.get_object(intent.intent_id)
        if existing is not None:
            candidate = intent.to_cko(lifecycle=existing.lifecycle)
            if candidate.semantic_hash() != existing.semantic_hash():
                raise RegistrationConflictError(
                    "registration would duplicate an existing id with divergent content",
                    identifier=intent.intent_id,
                )
        return self.plan_intent(intent)


__all__ = [
    "RegistrationEntry",
    "RegistrationPlan",
    "RegistrationIntegration",
]
