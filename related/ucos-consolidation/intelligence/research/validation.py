"""Research Validation — thirteen fail-closed obligations over the assimilated corpus.

The validator proves the properties the mission requires, mechanically:

  RV-01  every required substrate surface is available
  RV-02  every content reference in the corpus resolves against canonical knowledge
  RV-03  every claim carries resolvable provenance (source, locator, content hash)
  RV-04  every finding is bound to available evidence — no invented measurement
  RV-05  Knowledge-Once holds across the research population (no duplicate content)
  RV-06  the registry hash chain recomputes (tamper-evident)
  RV-07  contribution areas reconcile exactly with the concept-closure total
  RV-08  no standard declares an enforcement point that fails to resolve
  RV-09  ZERO DUPLICATION: no research record carries canonical prose
  RV-10  assimilation is deterministic (identical state ⇒ byte-identical corpus)
  RV-11  claim identity is unique — one claim per canonical subject
  RV-12  every research unit's members are registered records
  RV-13  no orphan record — every record belongs to a research unit
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from intelligence.kernel.canonical import canonical_json
from intelligence.kernel.errors import UnresolvedReferenceError
from intelligence.kernel.knowledge import CanonicalKnowledgeResolver
from intelligence.kernel.validation import Check, ValidationReport, report
from intelligence.research import PROGRAMME
from intelligence.research.model import (
    CONFORMANCE_NON_CONFORMANT,
    ResearchCorpus,
)
from intelligence.research.registry import ResearchRegistry

#: Structural (generated) text fields that the zero-duplication check inspects.
#: Every other field is an id, a ref, a count, or a hash and cannot hold prose.
_TEXT_FIELDS = ("area", "area_label", "role", "unit", "value", "research_class", "standard_class")


class ResearchValidationEngine:
    """Validates an assimilated research corpus against the thirteen obligations."""

    def __init__(
        self,
        corpus: ResearchCorpus,
        resolver: CanonicalKnowledgeResolver,
        registry: ResearchRegistry,
        *,
        reassimilate: Callable[[], ResearchCorpus] | None = None,
    ) -> None:
        self.corpus = corpus
        self.resolver = resolver
        self.registry = registry
        self._reassimilate = reassimilate

    # -- individual obligations ------------------------------------------------

    def _rv01(self) -> Check:
        missing = self.resolver.substrate.missing_required()
        return Check(
            "RV-01",
            "Required substrate available",
            "Every substrate surface declared required must be present and readable.",
            not missing,
            detail={"missing_required": missing, "declared": list(self.resolver.substrate.keys())},
        )

    def _rv02(self) -> Check:
        unresolved: list[dict[str, str]] = []
        refs = self.corpus.all_refs()
        for ref in refs:
            try:
                self.resolver.resolve(ref)
            except UnresolvedReferenceError as exc:
                unresolved.append({"ref": ref, "reason": exc.message})
        return Check(
            "RV-02",
            "References resolve",
            "Every content reference must resolve against canonical knowledge or a "
            "declared substrate surface — a non-resolving reference is fabrication.",
            not unresolved,
            detail={"references_checked": len(refs), "unresolved": unresolved},
        )

    def _rv03(self) -> Check:
        missing = [
            c.claim_id
            for c in self.corpus.claims
            if not (c.source_id and c.source_locator and c.source_content_sha256)
        ]
        return Check(
            "RV-03",
            "Claim provenance complete",
            "Every claim must name its source record, source locator and source content hash.",
            not missing,
            detail={"claims": len(self.corpus.claims), "without_provenance": missing},
        )

    def _rv04(self) -> Check:
        unbound = [
            f.finding_id
            for f in self.corpus.findings
            if not f.basis_content_sha256 or f.basis_content_sha256 == "absent"
        ]
        return Check(
            "RV-04",
            "Findings evidence-bound",
            "Every finding must carry the content hash of the evidence it was read from.",
            not unbound,
            detail={"findings": len(self.corpus.findings), "unbound": unbound},
        )

    def _rv05(self) -> Check:
        integrity = self.registry.verify()
        return Check(
            "RV-05",
            "Knowledge-Once holds",
            "No two research records may carry identical content under distinct identities.",
            bool(integrity["knowledge_once_holds"]),
            detail={"content_collisions": integrity["content_collisions"]},
        )

    def _rv06(self) -> Check:
        integrity = self.registry.verify()
        return Check(
            "RV-06",
            "Registry chain intact",
            "The append-only registration journal must recompute link-for-link.",
            bool(integrity["chain_intact"]),
            detail={
                "journal_length": integrity["journal_length"],
                "broken_links": integrity["broken_links"],
                "head": integrity["head"],
            },
        )

    def _rv07(self) -> Check:
        declared = self.resolver.substrate.payload("concept-closure").get("concept_total")
        summed = sum(c.concept_count for c in self.corpus.contributions)
        if declared is None:
            return Check(
                "RV-07",
                "Contribution areas reconcile",
                "Contribution area counts must sum to the declared concept total.",
                None,
                detail={"reason": "concept-closure does not declare concept_total"},
            )
        return Check(
            "RV-07",
            "Contribution areas reconcile",
            "Contribution area counts must sum to the declared concept total.",
            int(declared) == summed,
            detail={
                "declared_total": declared,
                "summed": summed,
                "areas": len(self.corpus.contributions),
            },
        )

    def _rv08(self) -> Check:
        offenders = [
            {"standard_id": s.standard_id, "unresolved": list(s.unresolved_enforcement_refs)}
            for s in self.corpus.standards
            if s.conformance == CONFORMANCE_NON_CONFORMANT
        ]
        return Check(
            "RV-08",
            "Standards enforcement resolves",
            "A standard that declares an enforcement point must have it resolve; an "
            "undeclared enforcement point is reported INDETERMINATE, never assumed.",
            not offenders,
            detail={"standards": len(self.corpus.standards), "non_conformant": offenders},
        )

    def _rv09(self) -> Check:
        violations: list[dict[str, Any]] = []
        for group_name, records in (
            ("sources", self.corpus.sources),
            ("claims", self.corpus.claims),
            ("findings", self.corpus.findings),
            ("contributions", self.corpus.contributions),
            ("standards", self.corpus.standards),
            ("units", self.corpus.units),
        ):
            for record in records:
                payload = record.to_dict()
                for field_name in _TEXT_FIELDS:
                    text = payload.get(field_name)
                    if not isinstance(text, str) or not text:
                        continue
                    owners = self.resolver.copied_prose(text)
                    if owners:
                        violations.append(
                            {"group": group_name, "field": field_name, "copied_from": owners}
                        )
        return Check(
            "RV-09",
            "Zero canonical-prose duplication",
            "No research record may carry canonical prose; canonical content is "
            "referenced and materialised only at render time (UCKO-PRIN-0001).",
            not violations,
            detail={
                "violations": violations,
                "prose_shingles_indexed": len(self.resolver.prose_index()),
            },
        )

    def _rv10(self) -> Check:
        if self._reassimilate is None:
            return Check(
                "RV-10",
                "Assimilation deterministic",
                "Identical repository state must produce a byte-identical corpus.",
                None,
                detail={"reason": "no re-assimilation callable supplied"},
            )
        again = self._reassimilate()
        first = canonical_json(self.corpus.to_dict())
        second = canonical_json(again.to_dict())
        return Check(
            "RV-10",
            "Assimilation deterministic",
            "Identical repository state must produce a byte-identical corpus.",
            first == second,
            detail={"corpus_bytes": len(first), "identical": first == second},
        )

    def _rv11(self) -> Check:
        seen: dict[str, int] = {}
        for claim in self.corpus.claims:
            seen[claim.claim_ref] = seen.get(claim.claim_ref, 0) + 1
        duplicates = {ref: n for ref, n in sorted(seen.items()) if n > 1}
        return Check(
            "RV-11",
            "Claim identity unique",
            "Exactly one research claim may exist per canonical subject reference.",
            not duplicates,
            detail={"claims": len(self.corpus.claims), "duplicated_refs": duplicates},
        )

    def _rv12(self) -> Check:
        known = {e.record_id for e in self.registry.ledger.all()}
        dangling: list[dict[str, Any]] = []
        for unit in self.corpus.units:
            members = (
                *unit.claim_ids,
                *unit.finding_ids,
                *unit.contribution_ids,
                *unit.standard_ids,
                *unit.source_ids,
            )
            missing = [m for m in members if m not in known]
            if missing:
                dangling.append({"unit_id": unit.unit_id, "missing": missing})
        return Check(
            "RV-12",
            "Unit membership registered",
            "Every member id named by a research unit must be a registered record.",
            not dangling,
            detail={"units": len(self.corpus.units), "dangling": dangling},
        )

    def _rv13(self) -> Check:
        member_ids: set[str] = set()
        for unit in self.corpus.units:
            member_ids.update(unit.claim_ids)
            member_ids.update(unit.finding_ids)
            member_ids.update(unit.contribution_ids)
            member_ids.update(unit.standard_ids)
        orphans = [c.claim_id for c in self.corpus.claims if c.claim_id not in member_ids]
        orphans += [f.finding_id for f in self.corpus.findings if f.finding_id not in member_ids]
        orphans += [
            c.contribution_id
            for c in self.corpus.contributions
            if c.contribution_id not in member_ids
        ]
        orphans += [s.standard_id for s in self.corpus.standards if s.standard_id not in member_ids]
        return Check(
            "RV-13",
            "No orphan research record",
            "Every claim, finding, contribution and standard must belong to a research unit.",
            not orphans,
            detail={"orphans": sorted(orphans)},
        )

    # -- report ----------------------------------------------------------------

    def checks(self) -> tuple[Check, ...]:
        return (
            self._rv01(),
            self._rv02(),
            self._rv03(),
            self._rv04(),
            self._rv05(),
            self._rv06(),
            self._rv07(),
            self._rv08(),
            self._rv09(),
            self._rv10(),
            self._rv11(),
            self._rv12(),
            self._rv13(),
        )

    def validate(self) -> ValidationReport:
        return report("assimilated research corpus", PROGRAMME, self.checks())


__all__ = ["ResearchValidationEngine"]
