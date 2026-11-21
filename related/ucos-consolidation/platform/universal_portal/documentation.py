"""UCOS-EPIC-008 / Terminal T8 — Documentation Portal (documentation index).

The **documentation** surface: a deterministic, content-addressed documentation index
generated entirely from the published contract surface and the eight application
descriptors — never hand-authored, never drifting from the code. It produces one page per
application (what it is, which capability group authorizes it, which published contracts it
consumes) and one page per published Universal Portal contract (its published description).
The index is a pure function of the vocabulary, so it is byte-identical across processes.

It authorizes nothing itself (the :class:`~platform.universal_portal.service.UniversalPortalService`
gates it on portal-navigation READ); it holds no session state; it starts no server.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_portal.contracts import (
    PortalApplication,
    UniversalPortalSurface,
    all_portal_applications,
    default_universal_portal_contracts,
)
from platform.universal_portal.errors import DocumentationPortalError
from typing import Any


@dataclass(frozen=True, slots=True)
class DocumentationPage:
    """An immutable, content-addressed documentation page."""

    page_id: str
    slug: str
    title: str
    section: str
    body: str
    references: tuple[str, ...]

    @classmethod
    def create(
        cls,
        *,
        slug: str,
        title: str,
        section: str,
        body: str,
        references: tuple[str, ...],
    ) -> DocumentationPage:
        if not slug or not title:
            raise DocumentationPortalError("a documentation page requires a slug and title")
        core = {
            "slug": slug,
            "title": title,
            "section": section,
            "body": body,
            "references": list(references),
        }
        return cls(
            page_id=f"UCOS-T8DOC-{content_hash(core)[:16]}",
            slug=slug,
            title=title,
            section=section,
            body=body,
            references=references,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_id": self.page_id,
            "slug": self.slug,
            "title": self.title,
            "section": self.section,
            "body": self.body,
            "references": list(self.references),
        }


@dataclass(frozen=True, slots=True)
class DocumentationIndex:
    """An immutable, content-addressed documentation index over all pages."""

    pages: tuple[DocumentationPage, ...]
    index_id: str = ""

    @classmethod
    def create(cls, pages: tuple[DocumentationPage, ...]) -> DocumentationIndex:
        core = [p.to_dict() for p in pages]
        return cls(pages=pages, index_id=f"UCOS-T8IDX-{content_hash(core)[:16]}")

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def slugs(self) -> tuple[str, ...]:
        return tuple(p.slug for p in self.pages)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index_id": self.index_id,
            "page_count": self.page_count,
            "pages": [p.to_dict() for p in self.pages],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def _application_body(surface: UniversalPortalSurface) -> str:
    """A deterministic descriptive body for an application page."""
    return (
        f"{surface.title} is a read-only Universal Portal surface in the "
        f"'{surface.section.value}' section. It is authorized by the "
        f"'{surface.group.value}' capability group ({surface.required_permission.value}) "
        f"and consumes {len(surface.consumed_contracts)} published contract(s) by "
        f"reference, never bypassing the underlying platform service."
    )


class DocumentationPortal:
    """A deterministic read model producing the Universal Portal documentation index."""

    __slots__ = ()

    def index(self) -> DocumentationIndex:
        """Build the deterministic documentation index (pure, no authorization)."""
        pages: list[DocumentationPage] = []
        for application in all_portal_applications():
            surface = UniversalPortalSurface.of(application)
            pages.append(
                DocumentationPage.create(
                    slug=application.value,
                    title=surface.title,
                    section=surface.section.value,
                    body=_application_body(surface),
                    references=surface.consumed_contracts,
                )
            )
        for contract in default_universal_portal_contracts():
            pages.append(
                DocumentationPage.create(
                    slug=contract.name,
                    title=contract.name,
                    section="contracts",
                    body=contract.description,
                    references=(f"{contract.name}@{contract.version}",),
                )
            )
        return DocumentationIndex.create(tuple(pages))

    def page(self, slug: str) -> DocumentationPage:
        """Resolve a single documentation page by slug (fail-closed on unknown slug)."""
        if not isinstance(slug, str) or not slug:
            raise DocumentationPortalError("documentation slug is required")
        for page in self.index().pages:
            if page.slug == slug:
                return page
        raise DocumentationPortalError("no such documentation page", slug=slug)

    def page_for(self, application: PortalApplication) -> DocumentationPage:
        """Resolve the documentation page for an application (fail-closed)."""
        if not isinstance(application, PortalApplication):
            raise DocumentationPortalError("application must be a PortalApplication")
        return self.page(application.value)


__all__ = ["DocumentationPage", "DocumentationIndex", "DocumentationPortal"]
