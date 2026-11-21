"""UKI Deliverable 8 — Knowledge Governance Integration (EPIC-UKDA-002).

Binds governance to canonical knowledge: every governance decision must reference
(``UKI-LAW-007``) canonical **knowledge**, the constitutional **laws** it is
subordinate to, prior **decisions**, and supporting **evidence**. This module
resolves those references from the artifact's own canonical links and fails closed on
an ungrounded governance decision.

    * :class:`GovernanceReference` — the four resolved reference sets for one decision.
    * :class:`GovernanceIntegration` — grounds a governance-kind canonical object
      (decision/policy/rule) or a recorded
      :class:`~engine.knowledge.cko.DecisionRecord`, reusing the UKDA store/graph
      verbatim (no second decision ledger).

"Grounded" is fail-closed on the non-negotiable references (canonical knowledge and a
constitutional law); missing prior decisions or evidence are reported as advisory.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord
from engine.knowledge.integration.errors import GovernanceGroundingError
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind
from engine.knowledge.store import KnowledgeBase

#: The canonical kinds that constitute a governance decision.
GOVERNANCE_KINDS: frozenset[KnowledgeKind] = frozenset(
    {KnowledgeKind.DECISION, KnowledgeKind.POLICY, KnowledgeKind.RULE}
)


@dataclass(frozen=True, slots=True)
class GovernanceReference:
    """The canonical references a governance decision is grounded in (Deliverable 8)."""

    decision: str
    knowledge: tuple[str, ...]
    laws: tuple[str, ...]
    decisions: tuple[str, ...]
    evidence: tuple[str, ...]
    issues: tuple[str, ...] = ()

    @property
    def grounded(self) -> bool:
        """True iff the non-negotiable grounding (knowledge + constitutional law) holds."""
        return bool(self.knowledge) and bool(self.laws) and not self._blocking_issues()

    def _blocking_issues(self) -> tuple[str, ...]:
        blocking = []
        if not self.knowledge:
            blocking.append("references no canonical knowledge")
        if not self.laws:
            blocking.append("references no constitutional law")
        return tuple(blocking)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "grounded": self.grounded,
            "knowledge": list(self.knowledge),
            "laws": list(self.laws),
            "decisions": list(self.decisions),
            "evidence": list(self.evidence),
            "issues": list(self.issues),
        }


class GovernanceIntegration:
    """Grounds governance decisions in canonical knowledge, fail-closed (Deliverable 8)."""

    __slots__ = ("_base",)

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base

    def _resolve(
        self,
        decision_id: str,
        *,
        candidate_knowledge: tuple[str, ...],
        candidate_decisions: tuple[str, ...],
        candidate_evidence: tuple[str, ...],
    ) -> GovernanceReference:
        knowledge: list[str] = []
        laws: list[str] = []
        evidence: list[str] = list(candidate_evidence)
        for ref in candidate_knowledge:
            obj = self._base.get_object(ref)
            if obj is None:
                continue
            knowledge.append(ref)
            if obj.authority is KnowledgeAuthority.CONSTITUTIONAL:
                laws.append(ref)
            if obj.kind is KnowledgeKind.EVIDENCE:
                evidence.append(ref)
        decisions = [d for d in candidate_decisions if self._base.has_decision(d)]

        issues: list[str] = []
        if not knowledge:
            issues.append("references no canonical knowledge")
        if not laws:
            issues.append("references no constitutional law")
        if not decisions:
            issues.append("references no prior decision (advisory)")
        if not evidence:
            issues.append("references no evidence (advisory)")

        return GovernanceReference(
            decision=decision_id,
            knowledge=tuple(sorted(set(knowledge))),
            laws=tuple(sorted(set(laws))),
            decisions=tuple(sorted(set(decisions))),
            evidence=tuple(sorted(set(evidence))),
            issues=tuple(issues),
        )

    def bind_object(self, cko_id: str) -> GovernanceReference:
        """Resolve the grounding of a governance-kind canonical object."""
        obj: CanonicalKnowledgeObject = self._base.require_object(cko_id)
        return self._resolve(
            cko_id,
            candidate_knowledge=tuple((*obj.dependencies, *obj.knowledge_links, obj.parent))
            if obj.parent
            else tuple((*obj.dependencies, *obj.knowledge_links)),
            candidate_decisions=obj.decision_links,
            candidate_evidence=obj.evidence,
        )

    def bind_decision(self, decision_id: str) -> GovernanceReference:
        """Resolve the grounding of a recorded decision record."""
        dec: DecisionRecord = self._base.require_decision(decision_id)
        prior = (dec.supersedes,) if dec.supersedes else ()
        return self._resolve(
            decision_id,
            candidate_knowledge=dec.dependencies,
            candidate_decisions=prior,
            candidate_evidence=(),
        )

    def require_grounded(self, cko_id: str) -> GovernanceReference:
        """Ground a governance object or raise (fail-closed on ungrounded governance)."""
        reference = self.bind_object(cko_id)
        if not reference.grounded:
            raise GovernanceGroundingError(
                "governance decision is not grounded in canonical knowledge",
                decision=cko_id,
                issues=list(reference._blocking_issues()),
            )
        return reference


__all__ = ["GOVERNANCE_KINDS", "GovernanceReference", "GovernanceIntegration"]
