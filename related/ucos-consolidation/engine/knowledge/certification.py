"""UKDA Part 11 — Knowledge Certification (EPIC-UKDA).

Certification attests that a canonical object (or the whole base) is *complete*:
every canonical object is self-describing, every decision is reviewable, every
rationale exists, every declared dependency and relationship resolves, every
consumer is identified, and every authority is defined.

Certification is **sound** (it attests only what the base substantiates),
**record-only** (it confers no constitutional authority — ``ENGINEERING-EXECUTION-
ONLY``), and **reproducible**: an identical object yields a byte-identical
:class:`KnowledgeCertificationRecord` and thus a stable ``certification_id``.
It is fail-closed: any blocking criterion failure yields ``NOT_CERTIFIED``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.model import KnowledgeKind, content_hash
from engine.knowledge.store import KnowledgeBase

#: Certification confers no constitutional authority (DE-05 / IP-01).
KNOWLEDGE_CERTIFICATION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"
KNOWLEDGE_CERTIFICATION_STANDARD = "UCOS-UKDA-KNOWLEDGE-CERTIFICATION-STANDARD"
KNOWLEDGE_CERTIFICATION_STANDARD_VERSION = "1.0.0"


class CertStatus(str, Enum):
    """The shared certification vocabulary (UKDA and UKIP mean the same by the same words).

    ``DENIED`` and ``INCOMPLETE`` refine ``NOT_CERTIFIED`` for callers that must
    distinguish *refused outright* (a blocking failure denies regardless of how many
    criteria pass) from *not yet established* (nothing asserts against it). The UKIP
    certifier is declared to reuse this vocabulary rather than redefine it
    (:mod:`engine.knowledge.ukip.certification`), so the members it names live here.
    """

    CERTIFIED = "certified"
    NOT_CERTIFIED = "not-certified"
    DENIED = "denied"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True, slots=True)
class Criterion:
    """The immutable outcome of a single certification criterion."""

    criterion_id: str
    passed: bool
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "passed": self.passed,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class KnowledgeCertificationRecord:
    """An immutable, content-addressed certification record for one object."""

    certification_id: str
    cko_id: str
    version: str
    status: CertStatus
    standard: str
    standard_version: str
    authority: str
    criteria: tuple[Criterion, ...]
    content_sha256: str

    @property
    def certified(self) -> bool:
        return self.status is CertStatus.CERTIFIED

    @staticmethod
    def _core(
        *,
        cko_id: str,
        version: str,
        status: CertStatus,
        standard: str,
        standard_version: str,
        authority: str,
        criteria: tuple[Criterion, ...],
    ) -> dict[str, Any]:
        return {
            "cko_id": cko_id,
            "version": version,
            "status": status.value,
            "standard": standard,
            "standard_version": standard_version,
            "authority": authority,
            "criteria": [c.to_dict() for c in criteria],
        }

    @classmethod
    def create(
        cls,
        *,
        cko_id: str,
        version: str,
        status: CertStatus,
        criteria: tuple[Criterion, ...],
        standard: str = KNOWLEDGE_CERTIFICATION_STANDARD,
        standard_version: str = KNOWLEDGE_CERTIFICATION_STANDARD_VERSION,
        authority: str = KNOWLEDGE_CERTIFICATION_AUTHORITY,
    ) -> KnowledgeCertificationRecord:
        core = cls._core(
            cko_id=cko_id,
            version=version,
            status=status,
            standard=standard,
            standard_version=standard_version,
            authority=authority,
            criteria=criteria,
        )
        digest = content_hash(core)
        return cls(
            certification_id=f"UKDA-CERT-{cko_id}-{digest[:16]}",
            cko_id=cko_id,
            version=version,
            status=status,
            standard=standard,
            standard_version=standard_version,
            authority=authority,
            criteria=criteria,
            content_sha256=digest,
        )

    def recompute_hash(self) -> str:
        return content_hash(
            self._core(
                cko_id=self.cko_id,
                version=self.version,
                status=self.status,
                standard=self.standard,
                standard_version=self.standard_version,
                authority=self.authority,
                criteria=self.criteria,
            )
        )

    def verify_integrity(self) -> bool:
        return self.recompute_hash() == self.content_sha256

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "cko_id": self.cko_id,
            "version": self.version,
            "status": self.status.value,
            "certified": self.certified,
            "standard": self.standard,
            "standard_version": self.standard_version,
            "authority": self.authority,
            "criteria": [c.to_dict() for c in self.criteria],
            "content_sha256": self.content_sha256,
        }


@dataclass(frozen=True, slots=True)
class BaseCertificationReport:
    """The aggregate certification verdict over the whole knowledge base."""

    status: CertStatus
    records: tuple[KnowledgeCertificationRecord, ...]

    @property
    def certified(self) -> bool:
        return self.status is CertStatus.CERTIFIED

    @property
    def not_certified_ids(self) -> tuple[str, ...]:
        return tuple(r.cko_id for r in self.records if not r.certified)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "certified": self.certified,
            "count": len(self.records),
            "not_certified": list(self.not_certified_ids),
            "records": [r.to_dict() for r in self.records],
        }


class KnowledgeCertifier:
    """Runs the deterministic completeness criteria over canonical objects (Part 11)."""

    def certify_object(
        self, obj: CanonicalKnowledgeObject, base: KnowledgeBase
    ) -> KnowledgeCertificationRecord:
        """Evaluate every criterion over ``obj`` and issue a content-addressed record."""
        criteria = self._evaluate(obj, base)
        status = (
            CertStatus.CERTIFIED if all(c.passed for c in criteria) else CertStatus.NOT_CERTIFIED
        )
        return KnowledgeCertificationRecord.create(
            cko_id=obj.cko_id,
            version=obj.version,
            status=status,
            criteria=criteria,
        )

    def certify_base(self, base: KnowledgeBase) -> BaseCertificationReport:
        """Certify every object in the base and aggregate (fail-closed)."""
        records = tuple(self.certify_object(obj, base) for obj in base.objects())
        status = (
            CertStatus.CERTIFIED if all(r.certified for r in records) else CertStatus.NOT_CERTIFIED
        )
        return BaseCertificationReport(status=status, records=records)

    # -- criteria --------------------------------------------------------------

    def _evaluate(
        self, obj: CanonicalKnowledgeObject, base: KnowledgeBase
    ) -> tuple[Criterion, ...]:
        known = set(base.object_ids())
        known_decisions = set(base.decision_ids())

        complete = bool(obj.title and obj.statement and obj.universe and obj.version)
        authority_defined = bool(obj.authority)
        owner_defined = bool(obj.owner) and obj.owner != "UNASSIGNED"
        integrity_ok = obj.verify_integrity()

        # Rationale required for judgemental kinds.
        rationale_ok = bool(obj.rationale) or obj.kind not in (
            KnowledgeKind.DECISION,
            KnowledgeKind.RULE,
            KnowledgeKind.PRINCIPLE,
        )

        # Every declared dependency/link resolves.
        deps_ok = all(ref in known for ref in obj.all_links())
        decisions_ok = all(ref in known_decisions for ref in obj.decision_links)

        # A DECISION object must be documented by a reviewable decision record.
        decision_reviewable = True
        decision_msg = "not a decision object"
        if obj.kind is KnowledgeKind.DECISION:
            linked = [base.get_decision(d) for d in obj.decision_links]
            present = [d for d in linked if d is not None]
            decision_reviewable = bool(present) and all(d.is_reviewable for d in present)
            decision_msg = (
                "linked decision(s) reviewable"
                if decision_reviewable
                else "decision object lacks a reviewable decision record"
            )

        return (
            Criterion("complete", complete, "all required fields present"),
            Criterion("authority-defined", authority_defined, "authority tier present"),
            Criterion("owner-identified", owner_defined, "owner assigned"),
            Criterion("rationale-present", rationale_ok, "rationale present where required"),
            Criterion("dependencies-resolve", deps_ok, "all links resolve to known objects"),
            Criterion("decisions-resolve", decisions_ok, "all decision links resolve"),
            Criterion("integrity-sealed", integrity_ok, "content hash verifies"),
            Criterion("decision-reviewable", decision_reviewable, decision_msg),
        )


def certify_base(base: KnowledgeBase) -> BaseCertificationReport:
    """Convenience: certify a base with the default certifier."""
    return KnowledgeCertifier().certify_base(base)


__all__ = [
    "KNOWLEDGE_CERTIFICATION_AUTHORITY",
    "KNOWLEDGE_CERTIFICATION_STANDARD",
    "KNOWLEDGE_CERTIFICATION_STANDARD_VERSION",
    "CertStatus",
    "Criterion",
    "KnowledgeCertificationRecord",
    "BaseCertificationReport",
    "KnowledgeCertifier",
    "certify_base",
]
