"""Publication value types — a specification that *cannot* hold canonical prose.

The zero-duplication guarantee is enforced by the shape of the data, not by review:

  * :class:`ContentRef` holds a reference string and a role. No text.
  * :class:`SectionSpec` holds a section key and refs. No text.
  * :class:`PublicationSpec` holds ids, keys and refs. No text.

Text exists only in :class:`ComposedBlock` / :class:`ComposedDocument`, which are
produced at render time by the composer and where every fragment carries the id,
locator and content hash of the canonical record it was resolved from.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from intelligence.kernel.canonical import slug
from intelligence.kernel.ids import ArtifactClass, artifact_id
from intelligence.kernel.knowledge import ResolvedContent

#: Roles a reference may play inside a section (ordering is deterministic by role).
ROLE_PRIMARY = "primary"
ROLE_SUPPORT = "support"
ROLE_EVIDENCE = "evidence"
_ROLE_ORDER = {ROLE_PRIMARY: 0, ROLE_SUPPORT: 1, ROLE_EVIDENCE: 2}


@dataclass(frozen=True, slots=True)
class ContentRef:
    """A pointer to canonical content. Carries no text, by construction."""

    ref: str
    role: str = ROLE_PRIMARY

    @property
    def sort_key(self) -> tuple[int, str]:
        return (_ROLE_ORDER.get(self.role, 99), self.ref)

    def to_dict(self) -> dict[str, str]:
        return {"ref": self.ref, "role": self.role}


@dataclass(frozen=True, slots=True)
class SectionSpec:
    """One ordered section of a publication: a key, an ordinal, and references."""

    section_key: str
    ordinal: int
    refs: tuple[ContentRef, ...] = ()
    structural: bool = False

    @property
    def ref_strings(self) -> tuple[str, ...]:
        return tuple(r.ref for r in self.refs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_key": self.section_key,
            "ordinal": self.ordinal,
            "structural": self.structural,
            "ref_count": len(self.refs),
            "refs": [r.to_dict() for r in self.refs],
        }


@dataclass(frozen=True, slots=True)
class PublicationSpec:
    """The complete, prose-free specification of one publication."""

    publication_id: str
    natural_key: str
    format_id: str
    genre: str
    area_label: str
    unit_id: str
    title_ref: str
    subject_refs: tuple[str, ...]
    sections: tuple[SectionSpec, ...]
    citation_refs: tuple[str, ...]
    research_record_ids: tuple[str, ...]

    @classmethod
    def create(cls, *, format_id: str, area_label: str, **fields: Any) -> PublicationSpec:
        natural_key = slug(f"{format_id}-{area_label}")
        return cls(
            publication_id=artifact_id(ArtifactClass.PUBLICATION, natural_key),
            natural_key=natural_key,
            format_id=format_id,
            area_label=area_label,
            **fields,
        )

    @property
    def record_id(self) -> str:
        return self.publication_id

    def section(self, section_key: str) -> SectionSpec | None:
        return next((s for s in self.sections if s.section_key == section_key), None)

    def section_keys(self) -> tuple[str, ...]:
        return tuple(s.section_key for s in self.sections)

    def content_sections(self) -> tuple[SectionSpec, ...]:
        return tuple(s for s in self.sections if not s.structural)

    def all_refs(self) -> tuple[str, ...]:
        refs: list[str] = [self.title_ref, *self.subject_refs]
        for section in self.sections:
            refs.extend(section.ref_strings)
        refs.extend(self.citation_refs)
        return tuple(dict.fromkeys(refs))

    def to_dict(self) -> dict[str, Any]:
        return {
            "publication_id": self.publication_id,
            "natural_key": self.natural_key,
            "format_id": self.format_id,
            "genre": self.genre,
            "area_label": self.area_label,
            "unit_id": self.unit_id,
            "title_ref": self.title_ref,
            "subject_refs": list(self.subject_refs),
            "sections": [s.to_dict() for s in self.sections],
            "citation_refs": list(self.citation_refs),
            "research_record_ids": list(self.research_record_ids),
            "section_count": len(self.sections),
            "reference_count": len(self.all_refs()),
        }


@dataclass(frozen=True, slots=True)
class ComposedBlock:
    """A rendered section: heading (structural) + resolved canonical content."""

    section_key: str
    heading: str
    ordinal: int
    structural: bool
    resolved: tuple[ResolvedContent, ...]

    @property
    def is_empty(self) -> bool:
        return not self.resolved

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_key": self.section_key,
            "heading": self.heading,
            "ordinal": self.ordinal,
            "structural": self.structural,
            "block_count": len(self.resolved),
            "blocks": [r.to_dict() for r in self.resolved],
        }


@dataclass(frozen=True, slots=True)
class Citation:
    """A citation: a canonical reference plus the research record that registered it."""

    citation_key: str
    ref: str
    target: str
    space: str
    source_locator: str
    source_authority: str
    source_content_sha256: str
    research_record_id: str | None

    @property
    def natural_key(self) -> str:
        return slug(self.ref)

    def to_dict(self) -> dict[str, Any]:
        return {
            "citation_key": self.citation_key,
            "ref": self.ref,
            "target": self.target,
            "space": self.space,
            "source_locator": self.source_locator,
            "source_authority": self.source_authority,
            "source_content_sha256": self.source_content_sha256,
            "research_record_id": self.research_record_id,
        }


@dataclass(frozen=True, slots=True)
class ComposedDocument:
    """A fully composed publication: resolved content with complete provenance."""

    publication_id: str
    format_id: str
    genre: str
    format_label: str
    area_label: str
    title: str
    title_ref: str
    blocks: tuple[ComposedBlock, ...]
    citations: tuple[Citation, ...]
    renderer: str
    extension: str
    citation_style: str
    unresolved: tuple[Mapping[str, str], ...] = ()

    def content_blocks(self) -> tuple[ComposedBlock, ...]:
        return tuple(b for b in self.blocks if not b.structural)

    def resolved_total(self) -> int:
        return sum(len(b.resolved) for b in self.blocks)

    def provenance_index(self) -> list[dict[str, str]]:
        seen: dict[str, dict[str, str]] = {}
        for block in self.blocks:
            for resolved in block.resolved:
                seen.setdefault(resolved.ref, resolved.provenance())
        return [seen[k] for k in sorted(seen)]

    def counts(self) -> dict[str, int]:
        return {
            "sections": len(self.blocks),
            "content_sections": len(self.content_blocks()),
            "resolved_blocks": self.resolved_total(),
            "citations": len(self.citations),
            "distinct_sources": len(self.provenance_index()),
            "unresolved": len(self.unresolved),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "publication_id": self.publication_id,
            "format_id": self.format_id,
            "genre": self.genre,
            "format_label": self.format_label,
            "area_label": self.area_label,
            "title": self.title,
            "title_ref": self.title_ref,
            "renderer": self.renderer,
            "extension": self.extension,
            "citation_style": self.citation_style,
            "counts": self.counts(),
            "sections": [b.to_dict() for b in self.blocks],
            "citations": [c.to_dict() for c in self.citations],
            "provenance_index": self.provenance_index(),
            "unresolved": [dict(u) for u in self.unresolved],
        }


@dataclass(frozen=True, slots=True)
class PublicationSet:
    """The generated population: specs, composed documents and rendered bodies."""

    specs: tuple[PublicationSpec, ...] = ()
    documents: tuple[ComposedDocument, ...] = ()
    rendered: Mapping[str, str] = field(default_factory=dict)

    def document(self, format_id: str) -> ComposedDocument | None:
        return next((d for d in self.documents if d.format_id == format_id), None)

    def spec(self, format_id: str) -> PublicationSpec | None:
        return next((s for s in self.specs if s.format_id == format_id), None)

    def format_ids(self) -> tuple[str, ...]:
        return tuple(s.format_id for s in self.specs)

    def counts(self) -> dict[str, int]:
        return {
            "publications": len(self.specs),
            "documents": len(self.documents),
            "rendered_files": len(self.rendered),
            "resolved_blocks": sum(d.resolved_total() for d in self.documents),
            "citations": len({c.ref for d in self.documents for c in d.citations}),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": self.counts(),
            "publications": [s.to_dict() for s in self.specs],
            "documents": [d.to_dict() for d in self.documents],
            "rendered_files": sorted(self.rendered),
        }


def ordered_refs(refs: Sequence[ContentRef]) -> tuple[ContentRef, ...]:
    """Deterministic reference ordering: role first, then reference string."""
    return tuple(sorted(dict.fromkeys(refs), key=lambda r: r.sort_key))


__all__ = [
    "ROLE_EVIDENCE",
    "ROLE_PRIMARY",
    "ROLE_SUPPORT",
    "Citation",
    "ComposedBlock",
    "ComposedDocument",
    "ContentRef",
    "PublicationSet",
    "PublicationSpec",
    "SectionSpec",
    "ordered_refs",
]
