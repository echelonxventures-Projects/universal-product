"""The composer — where a reference-only specification becomes readable content.

This is the single place in the system where canonical text is materialised. It
resolves every :class:`~intelligence.publication.model.ContentRef` through the
Canonical Knowledge Resolver and attaches, to each fragment, the id, locator,
authority and content hash of the canonical record it came from. Nothing is
paraphrased, reordered within a fragment, or edited.

A reference that fails to resolve is recorded in
:attr:`~intelligence.publication.model.ComposedDocument.unresolved` — never silently
dropped and never replaced with substitute text.
"""

from __future__ import annotations

from typing import Any

from intelligence.kernel.errors import UnresolvedReferenceError
from intelligence.kernel.knowledge import CanonicalKnowledgeResolver, ResolvedContent, parse_ref
from intelligence.publication.formats import FormatRegistry
from intelligence.publication.model import (
    Citation,
    ComposedBlock,
    ComposedDocument,
    PublicationSpec,
)
from intelligence.publication.renderers import render
from intelligence.research.registry import ResearchRegistry


class PublicationComposer:
    """Composes and renders publications from reference-only specifications."""

    def __init__(
        self,
        resolver: CanonicalKnowledgeResolver,
        formats: FormatRegistry | None = None,
        research_registry: ResearchRegistry | None = None,
    ) -> None:
        self.resolver = resolver
        self.formats = formats or FormatRegistry()
        self.research_registry = research_registry

    # -- composition -----------------------------------------------------------

    def compose(self, spec: PublicationSpec) -> ComposedDocument:
        descriptor = self.formats.get(spec.format_id)
        unresolved: list[dict[str, str]] = []
        title = self._title(spec, unresolved)
        blocks: list[ComposedBlock] = []
        for section in spec.sections:
            section_type = self.formats.section(section.section_key)
            resolved: list[ResolvedContent] = []
            for ref in section.ref_strings:
                try:
                    resolved.append(self.resolver.resolve(ref))
                except UnresolvedReferenceError as exc:
                    unresolved.append(
                        {"ref": ref, "section": section.section_key, "reason": exc.message}
                    )
            blocks.append(
                ComposedBlock(
                    section_key=section.section_key,
                    heading=section_type.label,
                    ordinal=section.ordinal,
                    structural=section.structural,
                    resolved=tuple(resolved),
                )
            )
        citations = self._citations(spec, blocks, unresolved)
        return ComposedDocument(
            publication_id=spec.publication_id,
            format_id=descriptor.format_id,
            genre=descriptor.genre,
            format_label=descriptor.label,
            area_label=spec.area_label,
            title=title,
            title_ref=spec.title_ref,
            blocks=tuple(blocks),
            citations=citations,
            renderer=descriptor.renderer,
            extension=descriptor.extension,
            citation_style=descriptor.citation_style,
            unresolved=tuple(unresolved),
        )

    def _title(self, spec: PublicationSpec, unresolved: list[dict[str, str]]) -> str:
        if not spec.title_ref:
            unresolved.append(
                {
                    "ref": "",
                    "section": "title-block",
                    "reason": "the scope contains no resolvable title subject",
                }
            )
            return spec.area_label
        try:
            return self.resolver.resolve(spec.title_ref).text
        except UnresolvedReferenceError as exc:
            unresolved.append(
                {"ref": spec.title_ref, "section": "title-block", "reason": exc.message}
            )
            return spec.area_label

    def _citations(
        self,
        spec: PublicationSpec,
        blocks: list[ComposedBlock],
        unresolved: list[dict[str, str]],
    ) -> tuple[Citation, ...]:
        """One citation per distinct reference actually rendered in the document."""
        seen: dict[str, ResolvedContent] = {}
        for block in blocks:
            for resolved in block.resolved:
                seen.setdefault(resolved.ref, resolved)
        for ref in spec.citation_refs:
            if ref in seen:
                continue
            try:
                seen.setdefault(ref, self.resolver.resolve(ref))
            except UnresolvedReferenceError as exc:
                unresolved.append({"ref": ref, "section": "references", "reason": exc.message})
        citations: list[Citation] = []
        for index, ref in enumerate(sorted(seen), start=1):
            resolved = seen[ref]
            space, target, _ = parse_ref(ref)
            citations.append(
                Citation(
                    citation_key=f"C{index:03d}",
                    ref=ref,
                    target=target,
                    space=space,
                    source_locator=resolved.source_locator,
                    source_authority=resolved.source_authority,
                    source_content_sha256=resolved.source_content_sha256,
                    research_record_id=(
                        self.research_registry.record_id_for_ref(ref)
                        if self.research_registry
                        else None
                    ),
                )
            )
        return tuple(citations)

    # -- rendering -------------------------------------------------------------

    def render(self, spec: PublicationSpec) -> tuple[ComposedDocument, str]:
        document = self.compose(spec)
        return document, render(document, self.formats.get(spec.format_id))

    def render_document(self, document: ComposedDocument) -> str:
        return render(document, self.formats.get(document.format_id))

    def filename(self, spec: PublicationSpec, area_key: str) -> str:
        return self.formats.get(spec.format_id).filename(area_key)

    # -- determinism -----------------------------------------------------------

    def verify_determinism(self, spec: PublicationSpec) -> dict[str, Any]:
        """Compose and render twice; prove the bytes are identical."""
        _, first = self.render(spec)
        _, second = self.render(spec)
        return {
            "publication_id": spec.publication_id,
            "format_id": spec.format_id,
            "deterministic": first == second,
            "rendered_bytes": len(first),
        }


__all__ = ["PublicationComposer"]
