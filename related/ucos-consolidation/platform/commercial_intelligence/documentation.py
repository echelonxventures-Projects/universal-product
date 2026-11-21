"""UCOS-EPIC-014 — Business Documentation (Terminal T5).

A commercial offer that is not documented is not an offer: it is an unbounded promise.
Business Documentation models the **document set** a commercial package must carry, and
asserts its completeness mechanically — the required kinds are declared, every document is
content-addressed, and a missing or unaddressed document is a blocking absence rather than
a stylistic remark.

Each :class:`BusinessDocument` carries the SHA-256 of the content it describes rather than
the content itself, so the set is a stable, auditable manifest: two document sets are the
same set iff their manifests hash identically. The digest is *verified in shape* (64 hex
characters) so an unaddressed document can never masquerade as an addressed one.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from platform.commercial_intelligence.errors import DocumentationError
from platform.foundation.contracts import content_hash
from typing import Any

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class DocumentKind(str, Enum):
    """The closed business-document vocabulary, in canonical order."""

    OVERVIEW = "overview"
    PRICING_SHEET = "pricing_sheet"
    LICENCE_TERMS = "licence_terms"
    SUPPORT_POLICY = "support_policy"
    SECURITY_STATEMENT = "security_statement"
    ROADMAP = "roadmap"
    INVESTMENT_CASE = "investment_case"
    CUSTOMER_REFERENCE = "customer_reference"

    @classmethod
    def parse(cls, value: Any) -> DocumentKind:
        try:
            return cls(value)
        except ValueError as exc:
            raise DocumentationError(
                "unknown business document kind",
                kind=value,
                supported=[k.value for k in cls],
            ) from exc

    @property
    def order(self) -> int:
        return _KIND_ORDER[self]


_KIND_ORDER: dict[DocumentKind, int] = {kind: i for i, kind in enumerate(DocumentKind)}

#: The document kinds a commercial package must carry before it may be offered. The
#: remaining kinds are legitimate but optional, and their absence is never blocking.
REQUIRED_DOCUMENT_KINDS: tuple[DocumentKind, ...] = (
    DocumentKind.OVERVIEW,
    DocumentKind.PRICING_SHEET,
    DocumentKind.LICENCE_TERMS,
    DocumentKind.SUPPORT_POLICY,
    DocumentKind.SECURITY_STATEMENT,
)


@dataclass(frozen=True, slots=True)
class BusinessDocument:
    """An immutable, content-addressed business document manifest entry."""

    document_id: str
    kind: DocumentKind
    title: str
    version: str
    content_sha256: str

    def __post_init__(self) -> None:
        if not self.document_id:
            raise DocumentationError("a business document requires a non-empty document_id")
        if not self.title:
            raise DocumentationError(
                "a business document requires a title", document_id=self.document_id
            )
        if not self.version:
            raise DocumentationError(
                "a business document requires a version", document_id=self.document_id
            )
        if not _SHA256_PATTERN.match(self.content_sha256 or ""):
            raise DocumentationError(
                "a business document requires the lower-case hex SHA-256 of its content — "
                "an unaddressed document cannot be audited",
                document_id=self.document_id,
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> BusinessDocument:
        if not isinstance(raw, Mapping):
            raise DocumentationError("a business document must be a mapping")
        return cls(
            document_id=str(raw.get("document_id") or ""),
            kind=DocumentKind.parse(raw.get("kind")),
            title=str(raw.get("title") or ""),
            version=str(raw.get("version") or ""),
            content_sha256=str(raw.get("content_sha256") or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "kind": self.kind.value,
            "title": self.title,
            "version": self.version,
            "content_sha256": self.content_sha256,
        }


@dataclass(frozen=True, slots=True)
class DocumentationCompleteness:
    """The deterministic completeness projection of one documentation set."""

    required: tuple[str, ...]
    present: tuple[str, ...]
    missing: tuple[str, ...]
    optional_present: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.missing

    def to_dict(self) -> dict[str, Any]:
        return {
            "required": list(self.required),
            "present": list(self.present),
            "missing": list(self.missing),
            "optional_present": list(self.optional_present),
            "complete": self.complete,
        }


@dataclass(frozen=True, slots=True)
class DocumentationSet:
    """An immutable, deterministically ordered documentation set for one commercial subject."""

    subject_id: str
    documents: tuple[BusinessDocument, ...] = ()
    required_kinds: tuple[DocumentKind, ...] = REQUIRED_DOCUMENT_KINDS

    def __post_init__(self) -> None:
        if not self.subject_id:
            raise DocumentationError("a documentation set requires the subject it documents")
        seen_ids: set[str] = set()
        seen_kinds: set[DocumentKind] = set()
        for document in self.documents:
            if document.document_id in seen_ids:
                raise DocumentationError(
                    "duplicate document_id in the documentation set",
                    document_id=document.document_id,
                )
            if document.kind in seen_kinds:
                raise DocumentationError(
                    "duplicate document kind in the documentation set — exactly one document "
                    "per kind keeps the manifest unambiguous",
                    kind=document.kind.value,
                    subject_id=self.subject_id,
                )
            seen_ids.add(document.document_id)
            seen_kinds.add(document.kind)

    @classmethod
    def from_mapping(cls, raw: Any) -> DocumentationSet:
        """Assimilate ``{subject_id, documents, required_kinds}`` into a documentation set."""
        if not isinstance(raw, Mapping):
            raise DocumentationError("a documentation set must be a mapping")
        documents_raw = raw.get("documents", ())
        if isinstance(documents_raw, str | bytes) or not isinstance(documents_raw, Sequence):
            raise DocumentationError(
                "documentation set documents must be a sequence",
                subject_id=raw.get("subject_id"),
            )
        documents = tuple(
            sorted(
                (BusinessDocument.from_mapping(item) for item in documents_raw),
                key=lambda document: (document.kind.order, document.document_id),
            )
        )
        required_raw = raw.get("required_kinds")
        if required_raw is None:
            required = REQUIRED_DOCUMENT_KINDS
        else:
            if isinstance(required_raw, str) or not isinstance(required_raw, Sequence):
                raise DocumentationError(
                    "documentation required_kinds must be a sequence",
                    subject_id=raw.get("subject_id"),
                )
            required = tuple(
                sorted({DocumentKind.parse(item) for item in required_raw}, key=lambda k: k.order)
            )
        return cls(
            subject_id=str(raw.get("subject_id") or ""),
            documents=documents,
            required_kinds=required,
        )

    def kinds(self) -> tuple[DocumentKind, ...]:
        return tuple(sorted({d.kind for d in self.documents}, key=lambda kind: kind.order))

    def get(self, kind: DocumentKind) -> BusinessDocument | None:
        for document in self.documents:
            if document.kind is kind:
                return document
        return None

    def completeness(self) -> DocumentationCompleteness:
        """The deterministic completeness verdict against the declared required kinds."""
        present = set(self.kinds())
        required = set(self.required_kinds)
        return DocumentationCompleteness(
            required=tuple(sorted((k.value for k in required), key=str)),
            present=tuple(sorted((k.value for k in present & required), key=str)),
            missing=tuple(sorted((k.value for k in required - present), key=str)),
            optional_present=tuple(sorted((k.value for k in present - required), key=str)),
        )

    def manifest(self) -> dict[str, Any]:
        """The stable, auditable manifest of the set (the basis of its identity)."""
        return {
            "subject_id": self.subject_id,
            "documents": [document.to_dict() for document in self.documents],
            "required_kinds": [kind.value for kind in self.required_kinds],
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.manifest(),
            "total": len(self.documents),
            "completeness": self.completeness().to_dict(),
            "manifest_sha256": self.digest(),
        }

    def digest(self) -> str:
        return content_hash(self.manifest())


__all__ = [
    "DocumentKind",
    "REQUIRED_DOCUMENT_KINDS",
    "BusinessDocument",
    "DocumentationCompleteness",
    "DocumentationSet",
]
