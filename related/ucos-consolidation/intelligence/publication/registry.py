"""The Publication Registry — every format, publication, section and citation, once.

The registry is the append-only, tamper-evident record of what was published, in
which format, from which canonical references. It applies the kernel ledger
invariants to four artifact classes:

    PUBLICATION_FORMAT   one record per registered format descriptor
    PUBLICATION          one record per generated publication (format × scope)
    PUBLICATION_SECTION  one record per section of each publication
    CITATION             one record per DISTINCT canonical reference cited anywhere

Because a citation is registered exactly once across the whole publication set, the
registry doubles as the proof that publications *share* canonical references rather
than each carrying a private copy: N publications citing the same principle produce
one citation record, not N.
"""

from __future__ import annotations

from typing import Any

from intelligence.kernel.errors import IdentityDivergenceError
from intelligence.kernel.ids import ArtifactClass
from intelligence.kernel.ledger import LedgerEntry, LedgerRegistry
from intelligence.publication import AUTHORITY, PROGRAMME
from intelligence.publication.formats import FormatRegistry
from intelligence.publication.model import PublicationSet
from intelligence.research.registry import ResearchRegistry

#: The registry envelope schema id.
SCHEMA = "ucos-publication-registry"
VERSION = "1.0.0"


class PublicationRegistry:
    """A deterministic, append-only registry over a generated publication set."""

    def __init__(
        self,
        publications: PublicationSet,
        formats: FormatRegistry,
        research_registry: ResearchRegistry | None = None,
    ) -> None:
        self.publications = publications
        self.formats = formats
        self.research_registry = research_registry
        self._ledger = LedgerRegistry(
            registry_id=f"{PROGRAMME}-PUBLICATION-REGISTRY", schema=SCHEMA, version=VERSION
        )
        self._citation_ids: dict[str, str] = {}
        self._register_all()

    # -- construction ----------------------------------------------------------

    def _register_all(self) -> None:
        for descriptor in self.formats.formats():
            entry = self._ledger.register(
                ArtifactClass.PUBLICATION_FORMAT, descriptor.natural_key, descriptor.to_dict()
            )
            self._require_identity(entry, descriptor.record_id, "format")
        for spec in self.publications.specs:
            entry = self._ledger.register(
                ArtifactClass.PUBLICATION, spec.natural_key, spec.to_dict()
            )
            self._require_identity(entry, spec.record_id, "publication")
            for section in spec.sections:
                payload = section.to_dict()
                payload["publication_id"] = spec.publication_id
                payload["format_id"] = spec.format_id
                self._ledger.register(
                    ArtifactClass.PUBLICATION_SECTION,
                    f"{spec.natural_key}--{section.section_key}",
                    payload,
                )
        for document in self.publications.documents:
            for citation in document.citations:
                if citation.ref in self._citation_ids:
                    continue
                payload = citation.to_dict()
                payload.pop("citation_key", None)  # per-document ordinal, not identity
                entry = self._ledger.register(ArtifactClass.CITATION, citation.natural_key, payload)
                self._citation_ids[citation.ref] = entry.record_id

    @staticmethod
    def _require_identity(entry: LedgerEntry, expected: str, kind: str) -> None:
        if entry.record_id != expected:
            raise IdentityDivergenceError(
                "registered identity diverges from the generated identity",
                kind=kind,
                generated_id=expected,
                registered_id=entry.record_id,
            )

    # -- access ----------------------------------------------------------------

    @property
    def ledger(self) -> LedgerRegistry:
        return self._ledger

    def count(self) -> int:
        return self._ledger.count()

    def citation_record_id(self, ref: str) -> str | None:
        return self._citation_ids.get(ref)

    def citation_refs(self) -> tuple[str, ...]:
        return tuple(sorted(self._citation_ids))

    def publication_ids(self) -> tuple[str, ...]:
        return self._ledger.ids_by_class(ArtifactClass.PUBLICATION)

    def format_ids(self) -> tuple[str, ...]:
        return self._ledger.ids_by_class(ArtifactClass.PUBLICATION_FORMAT)

    def verify(self) -> dict[str, Any]:
        return self._ledger.verify()

    def shared_citation_report(self) -> dict[str, Any]:
        """How often each canonical reference is reused across publications.

        Reuse > 1 is the desired state: it means several publications point at one
        canonical record instead of each duplicating it.
        """
        usage: dict[str, int] = {}
        for document in self.publications.documents:
            for citation in document.citations:
                usage[citation.ref] = usage.get(citation.ref, 0) + 1
        total_uses = sum(usage.values())
        return {
            "distinct_references": len(usage),
            "total_citation_uses": total_uses,
            "reuse_factor": round(total_uses / len(usage), 3) if usage else 0.0,
            "registered_citation_records": len(self._citation_ids),
            "duplicate_citation_records": max(0, len(self._citation_ids) - len(usage)),
            "most_reused": [
                {"ref": ref, "uses": uses}
                for ref, uses in sorted(usage.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
            ],
        }

    # -- serialization ---------------------------------------------------------

    def document(self) -> dict[str, Any]:
        snapshot = self._ledger.snapshot()
        snapshot.update(
            {
                "programme": PROGRAMME,
                "authority": AUTHORITY,
                "publication_counts": self.publications.counts(),
                "format_count": len(self.formats.format_ids()),
                "shared_citations": self.shared_citation_report(),
                "research_registry_head": (
                    self.research_registry.ledger.head() if self.research_registry else None
                ),
            }
        )
        return snapshot


__all__ = ["SCHEMA", "VERSION", "PublicationRegistry"]
