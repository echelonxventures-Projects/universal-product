"""Publication Validation — fourteen fail-closed obligations over the generated set.

PV-01  every publication names a registered format
PV-02  every required section of every format is satisfied with resolved content
PV-03  every reference in every publication resolves — nothing is unresolved
PV-04  ZERO DUPLICATION: no publication specification carries canonical prose
PV-05  every rendered block carries complete provenance (locator + content hash)
PV-06  every citation traces to a registered research record
PV-07  no publication repeats a reference across two of its own sections
PV-08  composition and rendering are deterministic (byte-identical on repeat)
PV-09  every format's renderer is registered
PV-10  no empty section is rendered — an unfillable optional section is omitted
PV-11  every rendered document carries the generated-artifact banner
PV-12  the publication registry chain recomputes and Knowledge-Once holds
PV-13  citation records are shared, not duplicated, across publications
PV-14  the format space is open — a format registered at runtime generates and
       validates with no code change (executed as a live probe, not asserted)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from intelligence.kernel.canonical import canonical_json, slug
from intelligence.kernel.knowledge import CanonicalKnowledgeResolver, parse_ref
from intelligence.kernel.validation import Check, ValidationReport, report
from intelligence.publication import GENERATED_BANNER, PROGRAMME
from intelligence.publication.composer import PublicationComposer
from intelligence.publication.formats import FormatRegistry
from intelligence.publication.model import PublicationSet
from intelligence.publication.registry import PublicationRegistry
from intelligence.publication.renderers import renderer_ids
from intelligence.research.registry import ResearchRegistry

#: Exact heading markup a renderer emits, per renderer id. Used by PV-10 so the
#: emptiness check is structural (exact markup on its own line) rather than a fragile
#: substring scan that could match canonical prose containing the same word.
_HEADING_MARKUP: dict[str, tuple[str, ...]] = {
    "markdown": ("## {heading}",),
    "latex": (r"\section*{{{heading}}}",),
    "html": ("<section><h2>{heading}</h2><ul>", "<section><h2>{heading}</h2>"),
    "plaintext": ("{upper}",),
}


def _heading_markers(renderer: str, heading: str) -> tuple[str, ...]:
    templates = _HEADING_MARKUP.get(renderer, ("{heading}",))
    return tuple(t.format(heading=heading, upper=heading.upper()) for t in templates)


class PublicationValidationEngine:
    """Validates a generated publication set against the fourteen obligations."""

    def __init__(
        self,
        publications: PublicationSet,
        formats: FormatRegistry,
        resolver: CanonicalKnowledgeResolver,
        registry: PublicationRegistry,
        composer: PublicationComposer,
        research_registry: ResearchRegistry | None = None,
        *,
        openness_probe: Callable[[], dict[str, Any]] | None = None,
    ) -> None:
        self.publications = publications
        self.formats = formats
        self.resolver = resolver
        self.registry = registry
        self.composer = composer
        self.research_registry = research_registry
        self._openness_probe = openness_probe

    # -- obligations -----------------------------------------------------------

    def _pv01(self) -> Check:
        unknown = [
            s.format_id for s in self.publications.specs if not self.formats.has(s.format_id)
        ]
        return Check(
            "PV-01",
            "Formats registered",
            "Every publication must name a format present in the open format registry.",
            not unknown,
            detail={"publications": len(self.publications.specs), "unknown_formats": unknown},
        )

    def _pv02(self) -> Check:
        unsatisfied: list[dict[str, Any]] = []
        for document in self.publications.documents:
            descriptor = self.formats.get(document.format_id)
            empty = [
                block.section_key
                for block in document.blocks
                if block.section_key in descriptor.required
                and not block.structural
                and block.is_empty
            ]
            if empty:
                unsatisfied.append({"format_id": document.format_id, "empty_required": empty})
        return Check(
            "PV-02",
            "Required sections satisfied",
            "Every section a format declares required must resolve at least one "
            "canonical reference; an unfillable required section is a failed publication.",
            not unsatisfied,
            detail={"documents": len(self.publications.documents), "unsatisfied": unsatisfied},
        )

    def _pv03(self) -> Check:
        unresolved = [
            {"format_id": d.format_id, "items": [dict(u) for u in d.unresolved]}
            for d in self.publications.documents
            if d.unresolved
        ]
        return Check(
            "PV-03",
            "References resolve",
            "Every reference in every publication must resolve; an unresolved reference "
            "is never dropped, substituted, or paraphrased.",
            not unresolved,
            detail={"documents_with_unresolved": unresolved},
        )

    def _pv04(self) -> Check:
        violations: list[dict[str, Any]] = []
        for spec in self.publications.specs:
            serialized = canonical_json(spec.to_dict())
            owners = self.resolver.copied_prose(serialized)
            if owners:
                violations.append({"format_id": spec.format_id, "copied_from": owners})
        return Check(
            "PV-04",
            "Zero canonical-prose duplication",
            "A publication specification must contain no canonical prose — only ids, "
            "keys and references (UCKO-PRIN-0001; the anti-pattern UCKO-ANTI-0001).",
            not violations,
            detail={
                "specifications_scanned": len(self.publications.specs),
                "prose_shingles_indexed": len(self.resolver.prose_index()),
                "violations": violations,
            },
        )

    def _pv05(self) -> Check:
        missing: list[dict[str, str]] = []
        total = 0
        for document in self.publications.documents:
            for block in document.blocks:
                for resolved in block.resolved:
                    total += 1
                    if not (resolved.source_locator and resolved.source_content_sha256):
                        missing.append({"format_id": document.format_id, "ref": resolved.ref})
        return Check(
            "PV-05",
            "Rendered blocks attributed",
            "Every rendered fragment must carry the locator and content hash of the "
            "canonical record it was resolved from.",
            not missing,
            detail={"blocks_checked": total, "without_provenance": missing},
        )

    def _pv06(self) -> Check:
        if self.research_registry is None:
            return Check(
                "PV-06",
                "Citations traceable to research records",
                "Every citation must trace to a registered research record.",
                None,
                detail={"reason": "no research registry supplied"},
            )
        known_targets = {parse_ref(r)[1] for r in self.research_registry.citable_refs()}
        untraceable: list[dict[str, str]] = []
        checked = 0
        for document in self.publications.documents:
            for citation in document.citations:
                checked += 1
                direct = self.research_registry.record_id_for_ref(citation.ref)
                if direct or citation.target in known_targets:
                    continue
                untraceable.append({"format_id": document.format_id, "ref": citation.ref})
        return Check(
            "PV-06",
            "Citations traceable to research records",
            "Every citation must trace to a registered research record, directly or "
            "through the canonical subject that record governs.",
            not untraceable,
            detail={"citations_checked": checked, "untraceable": untraceable},
        )

    def _pv07(self) -> Check:
        repeats: list[dict[str, Any]] = []
        for spec in self.publications.specs:
            seen: dict[str, str] = {}
            duplicated: list[dict[str, str]] = []
            for section in spec.sections:
                for ref in section.ref_strings:
                    if ref in seen:
                        duplicated.append(
                            {"ref": ref, "first": seen[ref], "again": section.section_key}
                        )
                    else:
                        seen[ref] = section.section_key
            if duplicated:
                repeats.append({"format_id": spec.format_id, "duplicated": duplicated})
        return Check(
            "PV-07",
            "No intra-document repetition",
            "A publication must not place the same canonical reference in two of its "
            "own sections — content is stated once and cross-referenced.",
            not repeats,
            detail={"documents_with_repeats": repeats},
        )

    def _pv08(self) -> Check:
        nondeterministic = [
            result
            for result in (self.composer.verify_determinism(s) for s in self.publications.specs)
            if not result["deterministic"]
        ]
        return Check(
            "PV-08",
            "Composition deterministic",
            "Composing and rendering the same specification twice must produce "
            "byte-identical output.",
            not nondeterministic,
            detail={
                "specifications_checked": len(self.publications.specs),
                "nondeterministic": nondeterministic,
            },
        )

    def _pv09(self) -> Check:
        available = set(renderer_ids())
        missing = sorted(
            {f.renderer for f in self.formats.formats() if f.renderer not in available}
        )
        return Check(
            "PV-09",
            "Renderers registered",
            "Every format must declare a renderer that is registered.",
            not missing,
            detail={"renderers_available": sorted(available), "missing": missing},
        )

    def _pv10(self) -> Check:
        rendered_empty: list[dict[str, str]] = []
        for document in self.publications.documents:
            body = self.publications.rendered.get(self._filename(document))
            if body is None or document.renderer == "json":
                # A JSON rendering is a structural serialization: it records every
                # declared section with its block_count, which is the correct machine
                # representation of an unfilled optional section.
                continue
            lines = set(body.splitlines())
            for block in document.blocks:
                if block.structural or not block.is_empty or not block.heading:
                    continue
                if any(
                    marker in lines for marker in _heading_markers(document.renderer, block.heading)
                ):
                    rendered_empty.append(
                        {"format_id": document.format_id, "section": block.section_key}
                    )
        return Check(
            "PV-10",
            "No empty section rendered",
            "A section that resolves no content must be omitted from the rendered "
            "document, not emitted as an empty heading (JSON renderings are structural "
            "and record the empty section explicitly instead).",
            not rendered_empty,
            detail={"rendered_empty_sections": rendered_empty},
        )

    def _pv11(self) -> Check:
        missing = [
            name
            for name, body in sorted(self.publications.rendered.items())
            if GENERATED_BANNER not in body
        ]
        return Check(
            "PV-11",
            "Generated banner present",
            "Every rendered document must declare that it was generated from canonical "
            "knowledge, so it can never be mistaken for an authored authority.",
            not missing,
            detail={"rendered": len(self.publications.rendered), "without_banner": missing},
        )

    def _pv12(self) -> Check:
        integrity = self.registry.verify()
        return Check(
            "PV-12",
            "Publication registry intact",
            "The append-only publication journal must recompute and Knowledge-Once "
            "must hold across formats, publications, sections and citations.",
            bool(integrity["intact"]),
            detail={
                "records": integrity["records"],
                "broken_links": integrity["broken_links"],
                "content_collisions": integrity["content_collisions"],
                "head": integrity["head"],
            },
        )

    def _pv13(self) -> Check:
        shared = self.registry.shared_citation_report()
        return Check(
            "PV-13",
            "Citations shared, not duplicated",
            "A canonical reference cited by N publications must produce exactly one "
            "citation record — the registry-level proof of non-duplication.",
            shared["duplicate_citation_records"] == 0
            and shared["registered_citation_records"] == shared["distinct_references"],
            detail=shared,
        )

    def _pv14(self) -> Check:
        if self._openness_probe is None:
            return Check(
                "PV-14",
                "Format space open",
                "A format registered at runtime must generate and validate with no "
                "code change (unlimited publication formats).",
                None,
                detail={"reason": "no openness probe supplied"},
            )
        result = self._openness_probe()
        return Check(
            "PV-14",
            "Format space open",
            "A format registered at runtime must generate and validate with no code "
            "change — proven by generating a probe format declared as data only.",
            bool(result.get("generated")) and bool(result.get("rendered")),
            detail=result,
        )

    # -- helpers ---------------------------------------------------------------

    def _filename(self, document: Any) -> str:
        descriptor = self.formats.get(document.format_id)
        return descriptor.filename(slug(document.area_label))

    # -- report ---------------------------------------------------------------

    def checks(self) -> tuple[Check, ...]:
        return (
            self._pv01(),
            self._pv02(),
            self._pv03(),
            self._pv04(),
            self._pv05(),
            self._pv06(),
            self._pv07(),
            self._pv08(),
            self._pv09(),
            self._pv10(),
            self._pv11(),
            self._pv12(),
            self._pv13(),
            self._pv14(),
        )

    def validate(self) -> ValidationReport:
        return report("generated publication set", PROGRAMME, self.checks())


__all__ = ["PublicationValidationEngine"]
