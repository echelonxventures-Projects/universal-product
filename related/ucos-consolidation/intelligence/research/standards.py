"""Standards Analysis — declared standards, their obligations, and real enforcement.

A standard is only a standard if something enforces it. This module derives, for
every standards-bearing canonical object:

  * its **obligations** — the canonical objects it links, depends on, or is consumed by
  * its **enforcement points** — the ``evidence`` / ``certification`` / ``validation``
    references the canonical record declares
  * whether each enforcement point actually **resolves** against Repository Truth
    (a canonical id that exists, or a repository path that exists)
  * a conformance verdict of CONFORMANT / INDETERMINATE / NON-CONFORMANT

The verdict is fail-closed and never optimistic: a standard that declares no
enforcement point is INDETERMINATE (the absence is reported, not excused), and a
standard whose enforcement reference does not resolve is NON-CONFORMANT.

The external standards families below are an explicitly **CURATED** cross-reference
overlay — a reading aid for publication, carrying no authority and asserting no
external certification. They are kept separate from every DERIVED fact so the two
can never be confused (the discipline ``intelligence.rie.knowledge`` established).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject
from intelligence.kernel.canonical import slug
from intelligence.kernel.ids import ArtifactClass, artifact_id
from intelligence.kernel.knowledge import CanonicalKnowledgeResolver, make_ref
from intelligence.research.model import (
    CONFORMANCE_CONFORMANT,
    CONFORMANCE_INDETERMINATE,
    CONFORMANCE_NON_CONFORMANT,
    STANDARDS_KINDS,
    ResearchCorpus,
    StandardsRecord,
    claim_class_for,
    sorted_unique,
)

#: CLASSIFICATION = CURATED. Declarative, non-authoritative cross-reference from a
#: repository standard class to the external standards families a reader may find
#: comparable. This asserts NO conformance and NO certification; it exists so a
#: generated publication can situate a repository standard in the wider landscape.
#: Adding a row is a data edit and changes no derived fact.
EXTERNAL_STANDARD_FAMILIES: dict[str, tuple[str, ...]] = {
    "specification-claim": (
        "ISO/IEC/IEEE 42010 — architecture description",
        "ISO/IEC 25010 — systems and software quality models",
    ),
    "normative-claim": (
        "IETF RFC 2119 — requirement-level keywords",
        "ISO/IEC/IEEE 29148 — requirements engineering",
    ),
    "practice-claim": (
        "ISO/IEC/IEEE 12207 — software life cycle processes",
        "ISO/IEC 5055 — code quality measures",
    ),
    "method-claim": ("ISO/IEC/IEEE 42020 — architecture processes",),
    "foundational-claim": ("ISO/IEC/IEEE 42010 — architecture principles and rationale",),
    "invariant-claim": ("ISO/IEC 25010 — reliability and maintainability characteristics",),
    "negative-result": ("ISO/IEC 25010 — maintainability (analysability, modifiability)",),
    "determination": ("ISO/IEC/IEEE 42010 — architecture decisions and rationale",),
}

#: CLASSIFICATION = CURATED. Content-addressing / determinism cross-reference used
#: when a standard's subject matter is integrity or reproducibility.
INTEGRITY_STANDARD_FAMILIES: tuple[str, ...] = (
    "NIST FIPS 180-4 — SHA-2 family of secure hash algorithms",
    "IETF RFC 8785 — JSON canonicalization scheme",
)

#: Tags/kinds whose subject matter triggers the integrity cross-reference.
_INTEGRITY_MARKERS = ("hash", "content-address", "determinis", "integrity", "seal", "canonical")


def _integrity_flavoured(obj: CanonicalKnowledgeObject) -> bool:
    """True when a standard's *identity metadata* (never its prose) is integrity-flavoured.

    Only the title and tags are inspected — both structural metadata — so this
    classification never requires reading, storing, or copying canonical prose.
    """
    haystack = " ".join((obj.title, *obj.tags)).lower()
    return any(marker in haystack for marker in _INTEGRITY_MARKERS)


def external_families(obj: CanonicalKnowledgeObject, standard_class: str) -> tuple[str, ...]:
    families = list(EXTERNAL_STANDARD_FAMILIES.get(standard_class, ()))
    if _integrity_flavoured(obj):
        families.extend(INTEGRITY_STANDARD_FAMILIES)
    return sorted_unique(families)


def is_standards_bearing(obj: CanonicalKnowledgeObject) -> bool:
    return obj.kind.value in STANDARDS_KINDS


def _resolves(reference: str, resolver: CanonicalKnowledgeResolver) -> bool:
    """A reference resolves if it is a known canonical id or an existing repo path."""
    if resolver.base.has_object(reference) or resolver.base.has_decision(reference):
        return True
    if reference in resolver.concepts():
        return True
    candidate = resolver.substrate.config.repo_root / reference
    return candidate.exists()


def analyse_standard(
    obj: CanonicalKnowledgeObject, resolver: CanonicalKnowledgeResolver
) -> StandardsRecord:
    """Derive the standards record for one standards-bearing canonical object."""
    standard_class = claim_class_for(obj.kind.value)
    obligations = sorted_unique(
        [make_ref("cko", ref, "statement") for ref in obj.knowledge_links if ref]
        + [make_ref("cko", ref, "statement") for ref in obj.dependencies if ref]
    )
    declared = sorted_unique(
        [
            *obj.evidence,
            *((obj.certification,) if obj.certification else ()),
            *((obj.validation,) if obj.validation else ()),
        ]
    )
    resolved = tuple(r for r in declared if _resolves(r, resolver))
    unresolved = tuple(r for r in declared if r not in resolved)
    if not declared:
        conformance = CONFORMANCE_INDETERMINATE
    elif unresolved:
        conformance = CONFORMANCE_NON_CONFORMANT
    else:
        conformance = CONFORMANCE_CONFORMANT
    return StandardsRecord(
        standard_id=artifact_id(ArtifactClass.STANDARD_ANALYSIS, slug(obj.cko_id)),
        standard_ref=make_ref("cko", obj.cko_id, "statement"),
        subject_ref=make_ref("cko", obj.cko_id, "title"),
        standard_class=standard_class,
        knowledge_kind=obj.kind.value,
        universe=obj.universe,
        authority=obj.authority.value,
        owner=obj.owner,
        lifecycle=obj.lifecycle.value,
        obligation_refs=obligations,
        enforcement_refs=declared,
        resolved_enforcement_refs=resolved,
        unresolved_enforcement_refs=unresolved,
        conformance=conformance,
        external_families=external_families(obj, standard_class),
        source_content_sha256=obj.content_sha256,
    )


def analyse_all(resolver: CanonicalKnowledgeResolver) -> tuple[StandardsRecord, ...]:
    return tuple(
        analyse_standard(obj, resolver) for obj in resolver.objects() if is_standards_bearing(obj)
    )


class StandardsAnalysisEngine:
    """Produces the Standards Analysis view over an assimilated research corpus."""

    def __init__(self, corpus: ResearchCorpus, resolver: CanonicalKnowledgeResolver) -> None:
        self.corpus = corpus
        self.resolver = resolver

    def conformance_histogram(self) -> dict[str, int]:
        histogram = {
            CONFORMANCE_CONFORMANT: 0,
            CONFORMANCE_INDETERMINATE: 0,
            CONFORMANCE_NON_CONFORMANT: 0,
        }
        for record in self.corpus.standards:
            histogram[record.conformance] = histogram.get(record.conformance, 0) + 1
        return dict(sorted(histogram.items()))

    def class_histogram(self) -> dict[str, int]:
        histogram: dict[str, int] = {}
        for record in self.corpus.standards:
            histogram[record.standard_class] = histogram.get(record.standard_class, 0) + 1
        return dict(sorted(histogram.items()))

    def universe_histogram(self) -> dict[str, int]:
        histogram: dict[str, int] = {}
        for record in self.corpus.standards:
            histogram[record.universe] = histogram.get(record.universe, 0) + 1
        return dict(sorted(histogram.items()))

    def programme_instruments(self) -> dict[str, Any]:
        """Standards-programme instruments LOCATED in the repository (never listed by hand)."""
        registries = self.resolver.substrate.directory_names("science-registries")
        constitution = self.resolver.substrate.directory_names("science-constitution")
        return {
            "science_registry_instruments": list(registries),
            "science_registry_count": len(registries),
            "science_constitution_instruments": list(constitution),
            "locator": self.resolver.substrate.declaration("science-registries")["locator"],
            "available": self.resolver.substrate.available("science-registries"),
        }

    def unresolved_enforcement(self) -> list[dict[str, Any]]:
        return [
            {
                "standard_id": r.standard_id,
                "standard_ref": r.standard_ref,
                "unresolved": list(r.unresolved_enforcement_refs),
            }
            for r in self.corpus.standards
            if r.unresolved_enforcement_refs
        ]

    def external_cross_reference(self) -> dict[str, list[str]]:
        table: dict[str, set[str]] = {}
        for record in self.corpus.standards:
            table.setdefault(record.standard_class, set()).update(record.external_families)
        return {k: sorted(v) for k, v in sorted(table.items())}

    def model(self) -> dict[str, Any]:
        conformance = self.conformance_histogram()
        analysed = len(self.corpus.standards)
        return {
            "standards_analysed": analysed,
            "conformance_histogram": conformance,
            "conformant_pct": (
                round(100.0 * conformance[CONFORMANCE_CONFORMANT] / analysed, 2)
                if analysed
                else 0.0
            ),
            "standard_class_histogram": self.class_histogram(),
            "universe_histogram": self.universe_histogram(),
            "obligation_total": sum(len(r.obligation_refs) for r in self.corpus.standards),
            "enforcement_total": sum(len(r.enforcement_refs) for r in self.corpus.standards),
            "unresolved_enforcement": self.unresolved_enforcement(),
            "programme_instruments": self.programme_instruments(),
            "external_cross_reference": {
                "classification": "CURATED — non-authoritative reading aid; asserts no "
                "conformance to, or certification by, any external body",
                "table": self.external_cross_reference(),
            },
            "standards": [r.to_dict() for r in self.corpus.standards],
        }


def curated_overlay() -> Mapping[str, Any]:
    """The curated overlay, published verbatim so its provenance is auditable."""
    return {
        "classification": "CURATED",
        "authority": "NONE — reading aid only",
        "external_standard_families": {
            k: list(v) for k, v in sorted(EXTERNAL_STANDARD_FAMILIES.items())
        },
        "integrity_standard_families": list(INTEGRITY_STANDARD_FAMILIES),
    }


__all__ = [
    "EXTERNAL_STANDARD_FAMILIES",
    "INTEGRITY_STANDARD_FAMILIES",
    "StandardsAnalysisEngine",
    "analyse_all",
    "analyse_standard",
    "curated_overlay",
    "external_families",
    "is_standards_bearing",
]
