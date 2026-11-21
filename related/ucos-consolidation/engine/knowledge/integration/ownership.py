"""UKI Deliverable 3 — Canonical Ownership Protocol (EPIC-UKDA-002).

Every constitutional artifact must declare **exactly one** of each: owner, canonical
identifier, constitutional authority, and lifecycle (``UKI-LAW-005``). This module
turns that law into an enforced, fail-closed protocol over an
:class:`~engine.knowledge.integration.contracts.ArtifactIntent` and the canonical
:class:`~engine.knowledge.store.KnowledgeBase`.

    * :class:`CanonicalOwnership` — the single, immutable ownership declaration.
    * :class:`OwnershipProtocol` — asserts a declaration is complete, unambiguous,
      and non-conflicting with the existing corpus (an id may not change owner or
      authority under a create; a modify must target the existing id), and surfaces
      *overlapping ownership* — identical knowledge owned by more than one owner.

It reuses the UKDA content model (semantic hashing, ownership fields) verbatim; it
introduces no second ownership store.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.knowledge.integration.contracts import ArtifactIntent, Operation
from engine.knowledge.integration.errors import OwnershipViolationError
from engine.knowledge.model import KnowledgeAuthority, Lifecycle
from engine.knowledge.store import KnowledgeBase

_UNASSIGNED = "UNASSIGNED"


@dataclass(frozen=True, slots=True)
class CanonicalOwnership:
    """The exactly-one ownership declaration of a canonical artifact."""

    canonical_id: str
    owner: str
    authority: KnowledgeAuthority
    lifecycle: Lifecycle

    def to_dict(self) -> dict[str, Any]:
        return {
            "canonical_id": self.canonical_id,
            "owner": self.owner,
            "authority": self.authority.value,
            "lifecycle": self.lifecycle.value,
        }


@dataclass(frozen=True, slots=True)
class OwnershipOverlap:
    """Identical knowledge owned by more than one owner (a UKI-LAW-005 violation)."""

    semantic_sha256: str
    owners: tuple[str, ...]
    cko_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_sha256": self.semantic_sha256,
            "owners": list(self.owners),
            "cko_ids": list(self.cko_ids),
        }


@dataclass(frozen=True, slots=True)
class OwnershipAssessment:
    """The outcome of asserting the ownership protocol over an intent."""

    ownership: CanonicalOwnership
    issues: tuple[str, ...] = ()

    @property
    def satisfied(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "ownership": self.ownership.to_dict(),
            "satisfied": self.satisfied,
            "issues": list(self.issues),
        }


class OwnershipProtocol:
    """Enforces the Canonical Ownership Protocol (Deliverable 3), fail-closed."""

    def declare(
        self, intent: ArtifactIntent, *, lifecycle: Lifecycle | None = None
    ) -> CanonicalOwnership:
        """Project the intent's single ownership declaration (no corpus check)."""
        return CanonicalOwnership(
            canonical_id=intent.intent_id,
            owner=intent.owner,
            authority=intent.authority,
            lifecycle=lifecycle if lifecycle is not None else Lifecycle.DRAFT,
        )

    def assess(self, intent: ArtifactIntent, base: KnowledgeBase) -> OwnershipAssessment:
        """Assess ownership completeness and corpus consistency (non-raising)."""
        issues: list[str] = []
        if not intent.owner or intent.owner == _UNASSIGNED:
            issues.append("owner is unassigned")

        existing = base.get_object(intent.intent_id)
        if intent.operation is Operation.CREATE and existing is not None:
            issues.append(
                f"canonical id '{intent.intent_id}' already owned by "
                f"'{existing.owner}' (create would duplicate identity)"
            )
        if intent.operation is Operation.MODIFY:
            if existing is None:
                issues.append(f"modify targets '{intent.intent_id}' which does not exist")
            else:
                if existing.owner != intent.owner:
                    issues.append(
                        f"ownership takeover: '{intent.intent_id}' is owned by "
                        f"'{existing.owner}', not '{intent.owner}'"
                    )
                if existing.authority is not intent.authority:
                    issues.append(
                        f"authority change on '{intent.intent_id}': "
                        f"{existing.authority.value} -> {intent.authority.value}"
                    )

        lifecycle = existing.lifecycle if existing is not None else Lifecycle.DRAFT
        ownership = CanonicalOwnership(
            canonical_id=intent.intent_id,
            owner=intent.owner,
            authority=intent.authority,
            lifecycle=lifecycle,
        )
        return OwnershipAssessment(ownership=ownership, issues=tuple(issues))

    def require(self, intent: ArtifactIntent, base: KnowledgeBase) -> CanonicalOwnership:
        """Return the ownership declaration or raise on any violation (fail-closed)."""
        assessment = self.assess(intent, base)
        if not assessment.satisfied:
            raise OwnershipViolationError(
                "canonical ownership protocol violated",
                canonical_id=intent.intent_id,
                issues=list(assessment.issues),
            )
        return assessment.ownership

    def find_overlaps(self, base: KnowledgeBase) -> tuple[OwnershipOverlap, ...]:
        """Detect identical active knowledge claimed by more than one owner."""
        by_hash: dict[str, list[tuple[str, str]]] = {}
        for obj in base.objects():
            if not obj.is_active:
                continue
            by_hash.setdefault(obj.semantic_hash(), []).append((obj.owner, obj.cko_id))
        overlaps: list[OwnershipOverlap] = []
        for semantic, members in by_hash.items():
            owners = sorted({owner for owner, _ in members})
            if len(owners) > 1:
                overlaps.append(
                    OwnershipOverlap(
                        semantic_sha256=semantic,
                        owners=tuple(owners),
                        cko_ids=tuple(sorted(cid for _, cid in members)),
                    )
                )
        overlaps.sort(key=lambda o: o.semantic_sha256)
        return tuple(overlaps)


__all__ = [
    "CanonicalOwnership",
    "OwnershipOverlap",
    "OwnershipAssessment",
    "OwnershipProtocol",
]
