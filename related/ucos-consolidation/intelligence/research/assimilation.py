"""Research Assimilation — Repository Truth becomes a citable research corpus.

Assimilation is a *projection*, not an import. Nothing is fetched, invented, or
paraphrased. Six substrate surfaces are projected into research-grade records:

    canonical-knowledge   → claims (foundational / normative / method / negative)
    canonical-decisions   → determinations (with alternatives + rejected options)
    concept-closure       → contribution areas (one per identifier family)
    control-tower/graph   → findings (corpus scale)
    corpus-certification  → findings (certification verdict)
    coverage.xml          → findings (empirical validation), via the RIE evidence reader

Every produced record stores references only. A surface that is unavailable
produces *no* record — the gap is reported by :meth:`ResearchAssimilationEngine.gaps`
and makes dependent verdicts INDETERMINATE rather than optimistic.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord
from intelligence.kernel.canonical import sha256_file, slug
from intelligence.kernel.ids import ArtifactClass, artifact_id
from intelligence.kernel.knowledge import CanonicalKnowledgeResolver, make_ref
from intelligence.kernel.substrate import SubstrateReader
from intelligence.research.model import (
    NOVELTY_PRIOR_ART_LINKED,
    NOVELTY_STANDALONE,
    NOVELTY_SUPERSEDING,
    ResearchClaim,
    ResearchContribution,
    ResearchCorpus,
    ResearchFinding,
    ResearchSource,
    ResearchUnit,
    claim_class_for,
    sorted_unique,
)
from intelligence.research.standards import analyse_all

#: The reserved research area for decision records. Decision records carry no
#: ``universe`` field, so the research projection assigns this structural label
#: rather than inferring (and thereby inventing) a universe for them.
DETERMINATION_AREA = "DETERMINATION"

#: The reserved research area holding measurements and contribution areas — facts
#: about the repository rather than claims made by it.
MEASUREMENT_AREA = "REPOSITORY-MEASUREMENT"

#: Research class of a unit, derived from what the unit contains.
RESEARCH_CLASS_THEORETICAL = "theoretical"
RESEARCH_CLASS_DETERMINATION = "determination"
RESEARCH_CLASS_EMPIRICAL = "empirical"

#: Coverage findings, projected from ``coverage.xml`` through the RIE evidence
#: reader (the registered owner of coverage parsing — never re-implemented here).
COVERAGE_FINDINGS: tuple[dict[str, str], ...] = (
    {"key": "coverage.line_pct", "attribute": "line_pct", "unit": "percent of lines covered"},
    {
        "key": "coverage.branch_pct",
        "attribute": "branch_pct",
        "unit": "percent of branches covered",
    },
    {"key": "coverage.lines_covered", "attribute": "lines_covered", "unit": "covered lines"},
    {"key": "coverage.lines_valid", "attribute": "lines_valid", "unit": "measured lines"},
)

#: Concept-closure boolean flags counted per contribution area.
_CONCEPT_FLAGS = ("certified", "deferred", "homed", "orphan")


def _finding_class(value: str) -> str:
    stripped = value.strip()
    try:
        float(stripped)
    except ValueError:
        return "qualitative-verdict"
    return "quantitative"


def _novelty(obj: CanonicalKnowledgeObject) -> str:
    if obj.supersedes:
        return NOVELTY_SUPERSEDING
    if obj.knowledge_links or obj.parent or obj.dependencies:
        return NOVELTY_PRIOR_ART_LINKED
    return NOVELTY_STANDALONE


class ResearchAssimilationEngine:
    """Projects declared Repository Truth into a :class:`ResearchCorpus`."""

    def __init__(self, substrate: SubstrateReader, resolver: CanonicalKnowledgeResolver) -> None:
        self.substrate = substrate
        self.resolver = resolver

    # -- sources ---------------------------------------------------------------

    def sources(self) -> tuple[ResearchSource, ...]:
        surfaces = [self.substrate.surface(k) for k in self.substrate.keys()]
        sources = [ResearchSource.from_surface(s) for s in surfaces]
        coverage = self._coverage()
        if coverage is not None and coverage.available:
            path = self.substrate.config.coverage_xml
            sources.append(
                ResearchSource(
                    source_id=artifact_id(ArtifactClass.RESEARCH_SOURCE, slug("coverage-report")),
                    substrate_key="coverage-report",
                    locator=self.substrate.config.rel(path),
                    media="xml",
                    authority="GENERATED",
                    role="The pytest+coverage gate output — empirical validation evidence.",
                    available=True,
                    record_count=coverage.lines_valid,
                    content_sha256=sha256_file(path),
                )
            )
        return tuple(sorted(sources, key=lambda s: s.substrate_key))

    def _source_index(self) -> dict[str, str]:
        return {s.locator: s.source_id for s in self.sources()}

    def _coverage(self) -> Any:
        """Coverage, read through its registered owner (compose, never duplicate)."""
        return self.resolver.coverage()

    # -- claims ----------------------------------------------------------------

    def claims(self) -> tuple[ResearchClaim, ...]:
        index = self._source_index()
        knowledge_locator = self.substrate.declaration("canonical-knowledge")["locator"]
        decision_locator = self.substrate.declaration("canonical-decisions")["locator"]
        claims = [
            self._claim_from_object(obj, index.get(knowledge_locator, ""), knowledge_locator)
            for obj in self.resolver.objects()
        ]
        claims.extend(
            self._claim_from_decision(dec, index.get(decision_locator, ""), decision_locator)
            for dec in self.resolver.decisions()
        )
        return tuple(sorted(claims, key=lambda c: (c.universe, c.claim_class, c.claim_ref)))

    def _claim_from_object(
        self, obj: CanonicalKnowledgeObject, source_id: str, locator: str
    ) -> ResearchClaim:
        support = sorted_unique(
            [
                make_ref("cko", ref, "statement")
                for ref in (*obj.knowledge_links, *obj.dependencies, *obj.supersedes)
                if self.resolver.base.has_object(ref)
            ]
        )
        return ResearchClaim(
            claim_id=artifact_id(ArtifactClass.RESEARCH_CLAIM, slug(obj.cko_id)),
            claim_class=claim_class_for(obj.kind.value),
            subject_ref=make_ref("cko", obj.cko_id, "title"),
            claim_ref=make_ref("cko", obj.cko_id, "statement"),
            rationale_ref=(
                make_ref("cko", obj.cko_id, "rationale") if obj.rationale.strip() else None
            ),
            universe=obj.universe,
            authority=obj.authority.value,
            owner=obj.owner,
            lifecycle=obj.lifecycle.value,
            version=obj.version,
            novelty_class=_novelty(obj),
            support_refs=support,
            source_id=source_id,
            source_locator=locator,
            source_content_sha256=obj.content_sha256,
        )

    def _claim_from_decision(
        self, dec: DecisionRecord, source_id: str, locator: str
    ) -> ResearchClaim:
        support = sorted_unique(
            [
                make_ref("decision", dec.decision_id, field)
                for field in ("alternatives", "evaluation_criteria", "tradeoffs", "consequences")
                if self.resolver.exists(make_ref("decision", dec.decision_id, field))
            ]
        )
        return ResearchClaim(
            claim_id=artifact_id(ArtifactClass.RESEARCH_CLAIM, slug(dec.decision_id)),
            claim_class=claim_class_for("decision"),
            subject_ref=make_ref("decision", dec.decision_id, "title"),
            claim_ref=make_ref("decision", dec.decision_id, "chosen_architecture"),
            rationale_ref=make_ref("decision", dec.decision_id, "rationale"),
            universe=DETERMINATION_AREA,
            authority=dec.authority.value,
            owner=dec.owner,
            lifecycle=dec.lifecycle.value,
            version=dec.version,
            novelty_class=(NOVELTY_SUPERSEDING if dec.supersedes else NOVELTY_PRIOR_ART_LINKED),
            support_refs=support,
            source_id=source_id,
            source_locator=locator,
            source_content_sha256=dec.content_sha256,
        )

    # -- findings --------------------------------------------------------------

    def findings(self) -> tuple[ResearchFinding, ...]:
        findings = [self._finding_from_metric(key) for key in self.resolver.available_metrics()]
        findings.extend(self._coverage_findings())
        return tuple(sorted(findings, key=lambda f: f.metric_key))

    def _finding_from_metric(self, key: str) -> ResearchFinding:
        ref = f"metric:{key}"
        resolved = self.resolver.resolve(ref)
        return ResearchFinding(
            finding_id=artifact_id(ArtifactClass.RESEARCH_FINDING, slug(key)),
            metric_key=key,
            metric_ref=ref,
            value=resolved.text,
            unit=self.resolver.metric_unit(key),
            finding_class=_finding_class(resolved.text),
            basis_locator=resolved.source_locator,
            basis_authority=resolved.source_authority,
            basis_content_sha256=resolved.source_content_sha256,
        )

    def _coverage_findings(self) -> list[ResearchFinding]:
        coverage = self._coverage()
        if coverage is None or not coverage.available:
            return []
        path = self.substrate.config.coverage_xml
        locator = self.substrate.config.rel(path)
        digest = sha256_file(path)
        out: list[ResearchFinding] = []
        for declaration in COVERAGE_FINDINGS:
            value = str(getattr(coverage, declaration["attribute"]))
            out.append(
                ResearchFinding(
                    finding_id=artifact_id(
                        ArtifactClass.RESEARCH_FINDING, slug(declaration["key"])
                    ),
                    metric_key=declaration["key"],
                    metric_ref=f"coverage:{declaration['attribute']}",
                    value=value,
                    unit=declaration["unit"],
                    finding_class=_finding_class(value),
                    basis_locator=locator,
                    basis_authority="GENERATED",
                    basis_content_sha256=digest,
                )
            )
        return out

    # -- contributions ---------------------------------------------------------

    def contributions(self) -> tuple[ResearchContribution, ...]:
        surface = self.substrate.surface("concept-closure")
        if not surface.available:
            return ()
        by_family: dict[str, list[Mapping[str, Any]]] = {}
        for row in self.substrate.records("concept-closure"):
            family = str(row.get("family") or "UNCLASSIFIED")
            by_family.setdefault(family, []).append(row)
        out: list[ResearchContribution] = []
        for family in sorted(by_family):
            rows = by_family[family]
            dispositions: dict[str, int] = {}
            flags = dict.fromkeys(_CONCEPT_FLAGS, 0)
            for row in rows:
                disposition = str(row.get("disposition") or "UNDISPOSITIONED")
                dispositions[disposition] = dispositions.get(disposition, 0) + 1
                for flag in _CONCEPT_FLAGS:
                    if bool(row.get(flag)):
                        flags[flag] += 1
            exemplars = tuple(
                make_ref("concept", str(row.get("id")), "disposition")
                for row in sorted(rows, key=lambda r: str(r.get("id")))[:3]
                if row.get("id")
            )
            out.append(
                ResearchContribution(
                    contribution_id=artifact_id(ArtifactClass.RESEARCH_CONTRIBUTION, slug(family)),
                    area=family,
                    concept_count=len(rows),
                    disposition_histogram=dispositions,
                    certified=flags["certified"],
                    deferred=flags["deferred"],
                    homed=flags["homed"],
                    orphan=flags["orphan"],
                    exemplar_refs=exemplars,
                    basis_locator=surface.locator,
                    basis_content_sha256=surface.content_sha256,
                )
            )
        return tuple(out)

    # -- units -----------------------------------------------------------------

    def units(
        self,
        claims: tuple[ResearchClaim, ...],
        findings: tuple[ResearchFinding, ...],
        contributions: tuple[ResearchContribution, ...],
        standards: tuple[Any, ...],
    ) -> tuple[ResearchUnit, ...]:
        index = self._source_index()
        by_area: dict[str, list[ResearchClaim]] = {}
        for claim in claims:
            by_area.setdefault(claim.universe, []).append(claim)
        units: list[ResearchUnit] = []
        for area in sorted(by_area):
            area_claims = by_area[area]
            area_standards = [s for s in standards if s.universe == area]
            novelty: dict[str, int] = {}
            for claim in area_claims:
                novelty[claim.novelty_class] = novelty.get(claim.novelty_class, 0) + 1
            units.append(
                ResearchUnit(
                    unit_id=artifact_id(ArtifactClass.RESEARCH_UNIT, slug(area)),
                    natural_key=slug(area),
                    area_label=area,
                    research_class=(
                        RESEARCH_CLASS_DETERMINATION
                        if area == DETERMINATION_AREA
                        else RESEARCH_CLASS_THEORETICAL
                    ),
                    claim_ids=tuple(c.claim_id for c in area_claims),
                    finding_ids=(),
                    contribution_ids=(),
                    standard_ids=tuple(s.standard_id for s in area_standards),
                    source_ids=sorted_unique([c.source_id for c in area_claims]),
                    novelty_histogram=novelty,
                )
            )
        measurement_sources = sorted_unique(
            [index.get(f.basis_locator, "") for f in findings]
            + [index.get(c.basis_locator, "") for c in contributions]
        )
        units.append(
            ResearchUnit(
                unit_id=artifact_id(ArtifactClass.RESEARCH_UNIT, slug(MEASUREMENT_AREA)),
                natural_key=slug(MEASUREMENT_AREA),
                area_label=MEASUREMENT_AREA,
                research_class=RESEARCH_CLASS_EMPIRICAL,
                claim_ids=(),
                finding_ids=tuple(f.finding_id for f in findings),
                contribution_ids=tuple(c.contribution_id for c in contributions),
                standard_ids=(),
                source_ids=measurement_sources,
                novelty_histogram={},
            )
        )
        return tuple(units)

    # -- corpus ----------------------------------------------------------------

    def assimilate(self) -> ResearchCorpus:
        """Produce the complete, deterministic research corpus."""
        sources = self.sources()
        claims = self.claims()
        findings = self.findings()
        contributions = self.contributions()
        standards = analyse_all(self.resolver)
        units = self.units(claims, findings, contributions, standards)
        return ResearchCorpus(
            sources=sources,
            claims=claims,
            findings=findings,
            contributions=contributions,
            standards=standards,
            units=units,
            substrate_inventory=tuple(self.substrate.inventory()),
            knowledge_fingerprint=self.resolver.fingerprint(),
        )

    # -- honest absence --------------------------------------------------------

    def gaps(self) -> list[dict[str, Any]]:
        """Declared surfaces that are absent — reported, never substituted."""
        gaps = [
            {
                "substrate_key": key,
                "locator": self.substrate.surface(key).locator,
                "required": self.substrate.declaration(key)["required"],
                "consequence": "records derived from this surface are not produced",
            }
            for key in self.substrate.keys()
            if not self.substrate.available(key)
        ]
        coverage = self._coverage()
        if coverage is None or not coverage.available:
            gaps.append(
                {
                    "substrate_key": "coverage-report",
                    "locator": self.substrate.config.rel(self.substrate.config.coverage_xml),
                    "required": False,
                    "consequence": "empirical validation findings are not produced "
                    "(run the coverage gate to materialise them)",
                }
            )
        return gaps


__all__ = [
    "COVERAGE_FINDINGS",
    "DETERMINATION_AREA",
    "MEASUREMENT_AREA",
    "RESEARCH_CLASS_DETERMINATION",
    "RESEARCH_CLASS_EMPIRICAL",
    "RESEARCH_CLASS_THEORETICAL",
    "ResearchAssimilationEngine",
]
