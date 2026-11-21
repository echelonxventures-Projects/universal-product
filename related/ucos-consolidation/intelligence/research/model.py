"""The research value types — reference-bearing, prose-free, content-addressed.

Every type in this module is frozen, slotted, deterministic and **carries no
canonical prose**. A claim knows *where* its statement lives (``claim_ref``); it
does not know what the statement says. That is the mechanical guarantee behind
"no duplicated content": there is no field in which a copy could be stored.

The one text a research record may own is a *structural label* — a heading, an
area name, a class name — which is generated from the taxonomy below and can
never collide with canonical prose (validated: RV-10).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from intelligence.kernel.canonical import slug
from intelligence.kernel.ids import ArtifactClass, artifact_id

# ---------------------------------------------------------------------------
# taxonomy (declarative — adding a mapping requires no engine change)
# ---------------------------------------------------------------------------

#: Canonical knowledge kind → research claim class. The research vocabulary is
#: distinct from the knowledge vocabulary on purpose: a *principle* is canonical
#: knowledge, a *foundational-claim* is its research-grade projection.
CLAIM_CLASS_BY_KIND: dict[str, str] = {
    "principle": "foundational-claim",
    "rule": "normative-claim",
    "standard": "specification-claim",
    "pattern": "method-claim",
    "anti-pattern": "negative-result",
    "convention": "practice-claim",
    "decision": "determination",
    "constraint": "constraint-claim",
    "definition": "definitional-claim",
    "invariant": "invariant-claim",
    "policy": "policy-claim",
    "procedure": "procedural-claim",
    "requirement": "requirement-claim",
    "specification": "specification-claim",
}

#: Fallback class for any knowledge kind not yet mapped (never invented, always
#: explicit so a new kind is visible in the output rather than silently absorbed).
DEFAULT_CLAIM_CLASS = "knowledge-claim"

#: Knowledge kinds that constitute a *standard* for Standards Analysis purposes.
STANDARDS_KINDS: frozenset[str] = frozenset({"standard", "rule", "convention", "specification"})

#: Novelty classification (derived from the canonical link topology only).
NOVELTY_PRIOR_ART_LINKED = "PRIOR-ART-LINKED"
NOVELTY_STANDALONE = "STANDALONE"
NOVELTY_SUPERSEDING = "SUPERSEDING"

#: Conformance verdicts for Standards Analysis. INDETERMINATE is a first-class
#: outcome: an undeclared enforcement point is reported, never assumed compliant.
CONFORMANCE_CONFORMANT = "CONFORMANT"
CONFORMANCE_INDETERMINATE = "INDETERMINATE"
CONFORMANCE_NON_CONFORMANT = "NON-CONFORMANT"


def claim_class_for(kind: str) -> str:
    return CLAIM_CLASS_BY_KIND.get(kind, DEFAULT_CLAIM_CLASS)


def ref_target(ref: str) -> str:
    """The target segment of a content reference (``cko:UCKO-X#statement`` → ``UCKO-X``)."""
    _, _, remainder = ref.partition(":")
    target, _, _ = remainder.partition("#")
    return target.strip()


# ---------------------------------------------------------------------------
# value types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ResearchSource:
    """A declared substrate surface, assimilated as a citable research source."""

    source_id: str
    substrate_key: str
    locator: str
    media: str
    authority: str
    role: str
    available: bool
    record_count: int
    content_sha256: str

    @classmethod
    def from_surface(cls, surface: Any) -> ResearchSource:
        return cls(
            source_id=artifact_id(ArtifactClass.RESEARCH_SOURCE, slug(surface.key)),
            substrate_key=surface.key,
            locator=surface.locator,
            media=surface.media,
            authority=surface.authority,
            role=surface.role,
            available=surface.available,
            record_count=surface.record_count,
            content_sha256=surface.content_sha256,
        )

    @property
    def natural_key(self) -> str:
        """The key from which :attr:`source_id` was derived (registry-stable)."""
        return slug(self.substrate_key)

    @property
    def record_id(self) -> str:
        return self.source_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "substrate_key": self.substrate_key,
            "locator": self.locator,
            "media": self.media,
            "authority": self.authority,
            "role": self.role,
            "available": self.available,
            "record_count": self.record_count,
            "content_sha256": self.content_sha256,
        }


@dataclass(frozen=True, slots=True)
class ResearchClaim:
    """A research claim: a reference to canonical knowledge plus derived classification.

    Contains no statement text. ``claim_ref`` is where the statement lives.
    """

    claim_id: str
    claim_class: str
    subject_ref: str
    claim_ref: str
    rationale_ref: str | None
    universe: str
    authority: str
    owner: str
    lifecycle: str
    version: str
    novelty_class: str
    support_refs: tuple[str, ...]
    source_id: str
    source_locator: str
    source_content_sha256: str

    @property
    def natural_key(self) -> str:
        """The canonical subject id from which :attr:`claim_id` was derived."""
        return slug(ref_target(self.claim_ref))

    @property
    def record_id(self) -> str:
        return self.claim_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim_class": self.claim_class,
            "subject_ref": self.subject_ref,
            "claim_ref": self.claim_ref,
            "rationale_ref": self.rationale_ref,
            "universe": self.universe,
            "authority": self.authority,
            "owner": self.owner,
            "lifecycle": self.lifecycle,
            "version": self.version,
            "novelty_class": self.novelty_class,
            "support_refs": list(self.support_refs),
            "source_id": self.source_id,
            "source_locator": self.source_locator,
            "source_content_sha256": self.source_content_sha256,
        }

    def refs(self) -> tuple[str, ...]:
        out = [self.subject_ref, self.claim_ref, *self.support_refs]
        if self.rationale_ref:
            out.append(self.rationale_ref)
        return tuple(dict.fromkeys(out))


@dataclass(frozen=True, slots=True)
class ResearchFinding:
    """A derived, quantitative or verdict-bearing measurement over Repository Truth."""

    finding_id: str
    metric_key: str
    metric_ref: str
    value: str
    unit: str
    finding_class: str
    basis_locator: str
    basis_authority: str
    basis_content_sha256: str

    @property
    def natural_key(self) -> str:
        return slug(self.metric_key)

    @property
    def record_id(self) -> str:
        return self.finding_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "metric_key": self.metric_key,
            "metric_ref": self.metric_ref,
            "value": self.value,
            "unit": self.unit,
            "finding_class": self.finding_class,
            "basis_locator": self.basis_locator,
            "basis_authority": self.basis_authority,
            "basis_content_sha256": self.basis_content_sha256,
        }

    def refs(self) -> tuple[str, ...]:
        return (self.metric_ref,)


@dataclass(frozen=True, slots=True)
class ResearchContribution:
    """A contribution area: one identifier family of the repository concept closure."""

    contribution_id: str
    area: str
    concept_count: int
    disposition_histogram: Mapping[str, int]
    certified: int
    deferred: int
    homed: int
    orphan: int
    exemplar_refs: tuple[str, ...]
    basis_locator: str
    basis_content_sha256: str

    @property
    def natural_key(self) -> str:
        return slug(self.area)

    @property
    def record_id(self) -> str:
        return self.contribution_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "contribution_id": self.contribution_id,
            "area": self.area,
            "concept_count": self.concept_count,
            "disposition_histogram": dict(sorted(self.disposition_histogram.items())),
            "certified": self.certified,
            "deferred": self.deferred,
            "homed": self.homed,
            "orphan": self.orphan,
            "exemplar_refs": list(self.exemplar_refs),
            "basis_locator": self.basis_locator,
            "basis_content_sha256": self.basis_content_sha256,
        }

    def refs(self) -> tuple[str, ...]:
        return self.exemplar_refs


@dataclass(frozen=True, slots=True)
class StandardsRecord:
    """A standards-bearing canonical object, analysed for declared enforcement."""

    standard_id: str
    standard_ref: str
    subject_ref: str
    standard_class: str
    knowledge_kind: str
    universe: str
    authority: str
    owner: str
    lifecycle: str
    obligation_refs: tuple[str, ...]
    enforcement_refs: tuple[str, ...]
    resolved_enforcement_refs: tuple[str, ...]
    unresolved_enforcement_refs: tuple[str, ...]
    conformance: str
    external_families: tuple[str, ...]
    source_content_sha256: str

    @property
    def natural_key(self) -> str:
        return slug(ref_target(self.standard_ref))

    @property
    def record_id(self) -> str:
        return self.standard_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "standard_id": self.standard_id,
            "standard_ref": self.standard_ref,
            "subject_ref": self.subject_ref,
            "standard_class": self.standard_class,
            "knowledge_kind": self.knowledge_kind,
            "universe": self.universe,
            "authority": self.authority,
            "owner": self.owner,
            "lifecycle": self.lifecycle,
            "obligation_refs": list(self.obligation_refs),
            "enforcement_refs": list(self.enforcement_refs),
            "resolved_enforcement_refs": list(self.resolved_enforcement_refs),
            "unresolved_enforcement_refs": list(self.unresolved_enforcement_refs),
            "conformance": self.conformance,
            "external_families": list(self.external_families),
            "source_content_sha256": self.source_content_sha256,
        }

    def refs(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys((self.subject_ref, self.standard_ref, *self.obligation_refs)))


@dataclass(frozen=True, slots=True)
class ResearchUnit:
    """A research area: the assimilated unit the Research Registry governs."""

    unit_id: str
    natural_key: str
    area_label: str
    research_class: str
    claim_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    contribution_ids: tuple[str, ...]
    standard_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    novelty_histogram: Mapping[str, int]

    @property
    def record_id(self) -> str:
        return self.unit_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "natural_key": self.natural_key,
            "area_label": self.area_label,
            "research_class": self.research_class,
            "claim_ids": list(self.claim_ids),
            "finding_ids": list(self.finding_ids),
            "contribution_ids": list(self.contribution_ids),
            "standard_ids": list(self.standard_ids),
            "source_ids": list(self.source_ids),
            "novelty_histogram": dict(sorted(self.novelty_histogram.items())),
            "record_total": (
                len(self.claim_ids)
                + len(self.finding_ids)
                + len(self.contribution_ids)
                + len(self.standard_ids)
            ),
        }


@dataclass(frozen=True, slots=True)
class ResearchCorpus:
    """The complete assimilated research corpus — the single publication input."""

    sources: tuple[ResearchSource, ...] = ()
    claims: tuple[ResearchClaim, ...] = ()
    findings: tuple[ResearchFinding, ...] = ()
    contributions: tuple[ResearchContribution, ...] = ()
    standards: tuple[StandardsRecord, ...] = ()
    units: tuple[ResearchUnit, ...] = ()
    substrate_inventory: tuple[Mapping[str, Any], ...] = ()
    knowledge_fingerprint: Mapping[str, Any] = field(default_factory=dict)

    # -- indexes ---------------------------------------------------------------

    def claim(self, claim_id: str) -> ResearchClaim | None:
        return next((c for c in self.claims if c.claim_id == claim_id), None)

    def claims_by_class(self, *classes: str) -> tuple[ResearchClaim, ...]:
        wanted = set(classes)
        return tuple(c for c in self.claims if c.claim_class in wanted)

    def claims_by_universe(self, universe: str) -> tuple[ResearchClaim, ...]:
        return tuple(c for c in self.claims if c.universe == universe)

    def findings_by_class(self, *classes: str) -> tuple[ResearchFinding, ...]:
        wanted = set(classes)
        return tuple(f for f in self.findings if f.finding_class in wanted)

    def unit(self, natural_key: str) -> ResearchUnit | None:
        return next((u for u in self.units if u.natural_key == natural_key), None)

    def all_refs(self) -> tuple[str, ...]:
        refs: list[str] = []
        for group in (self.claims, self.findings, self.contributions, self.standards):
            for record in group:
                refs.extend(record.refs())
        return tuple(dict.fromkeys(refs))

    def record_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                [s.source_id for s in self.sources]
                + [c.claim_id for c in self.claims]
                + [f.finding_id for f in self.findings]
                + [c.contribution_id for c in self.contributions]
                + [s.standard_id for s in self.standards]
                + [u.unit_id for u in self.units]
            )
        )

    def counts(self) -> dict[str, int]:
        return {
            "sources": len(self.sources),
            "claims": len(self.claims),
            "findings": len(self.findings),
            "contributions": len(self.contributions),
            "standards": len(self.standards),
            "units": len(self.units),
            "references": len(self.all_refs()),
            "records": len(self.record_ids()),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": self.counts(),
            "sources": [s.to_dict() for s in self.sources],
            "claims": [c.to_dict() for c in self.claims],
            "findings": [f.to_dict() for f in self.findings],
            "contributions": [c.to_dict() for c in self.contributions],
            "standards": [s.to_dict() for s in self.standards],
            "units": [u.to_dict() for u in self.units],
            "substrate_inventory": [dict(s) for s in self.substrate_inventory],
            "knowledge_fingerprint": dict(self.knowledge_fingerprint),
        }


def sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted(dict.fromkeys(v for v in values if v)))


__all__ = [
    "CLAIM_CLASS_BY_KIND",
    "CONFORMANCE_CONFORMANT",
    "CONFORMANCE_INDETERMINATE",
    "CONFORMANCE_NON_CONFORMANT",
    "DEFAULT_CLAIM_CLASS",
    "NOVELTY_PRIOR_ART_LINKED",
    "NOVELTY_STANDALONE",
    "NOVELTY_SUPERSEDING",
    "STANDARDS_KINDS",
    "ResearchClaim",
    "ResearchContribution",
    "ResearchCorpus",
    "ResearchFinding",
    "ResearchSource",
    "ResearchUnit",
    "StandardsRecord",
    "claim_class_for",
    "ref_target",
    "sorted_unique",
]
