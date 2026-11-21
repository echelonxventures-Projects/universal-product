"""The Research Registry — the append-only home of every assimilated research record.

One registry governs the whole assimilated population: sources, claims, findings,
contribution areas, standards records and research units. Registration applies the
kernel ledger invariants — deterministic identity, single registration, Knowledge-Once
content equality, tamper-evident hash chain — so the registry can *prove* that no
research record is duplicated and that its contents were not tampered with after
assimilation.

Registration order is the deterministic sort order of the corpus, so the journal
chain (and therefore its head hash) is itself reproducible.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from intelligence.kernel.errors import IdentityDivergenceError
from intelligence.kernel.ids import ArtifactClass
from intelligence.kernel.ledger import LedgerEntry, LedgerRegistry
from intelligence.research import AUTHORITY, PROGRAMME
from intelligence.research.model import ResearchCorpus

#: The registry envelope schema id.
SCHEMA = "ucos-research-registry"
VERSION = "1.0.0"

#: Registration order: sources first (everything cites them), then the records that
#: reference them, then the units that aggregate those records.
_REGISTRATION_ORDER = (
    ArtifactClass.RESEARCH_SOURCE,
    ArtifactClass.RESEARCH_CLAIM,
    ArtifactClass.RESEARCH_FINDING,
    ArtifactClass.RESEARCH_CONTRIBUTION,
    ArtifactClass.STANDARD_ANALYSIS,
    ArtifactClass.RESEARCH_UNIT,
)


class ResearchRegistry:
    """A deterministic, append-only registry over an assimilated research corpus."""

    def __init__(self, corpus: ResearchCorpus) -> None:
        self.corpus = corpus
        self._ledger = LedgerRegistry(
            registry_id=f"{PROGRAMME}-RESEARCH-REGISTRY", schema=SCHEMA, version=VERSION
        )
        self._by_ref: dict[str, str] = {}
        self._by_locator: dict[str, str] = {}
        self._register_all()

    # -- construction ----------------------------------------------------------

    def _register_all(self) -> None:
        for artifact_class in _REGISTRATION_ORDER:
            for record, refs in self._population(artifact_class):
                entry = self._ledger.register(artifact_class, record.natural_key, record.to_dict())
                if entry.record_id != record.record_id:
                    raise IdentityDivergenceError(
                        "registered identity diverges from the assimilated identity — "
                        "the natural key used at assimilation and at registration differ",
                        artifact_class=artifact_class.value,
                        natural_key=record.natural_key,
                        assimilated_id=record.record_id,
                        registered_id=entry.record_id,
                    )
                for ref in refs:
                    if ":" in ref:
                        self._by_ref.setdefault(ref, entry.record_id)
                    else:
                        self._by_locator.setdefault(ref, entry.record_id)

    def _population(self, artifact_class: ArtifactClass) -> Iterable[tuple[Any, tuple[str, ...]]]:
        corpus = self.corpus
        if artifact_class is ArtifactClass.RESEARCH_SOURCE:
            return [(s, (s.locator,)) for s in corpus.sources]
        if artifact_class is ArtifactClass.RESEARCH_CLAIM:
            return [(c, (c.claim_ref, c.subject_ref)) for c in corpus.claims]
        if artifact_class is ArtifactClass.RESEARCH_FINDING:
            return [(f, (f.metric_ref,)) for f in corpus.findings]
        if artifact_class is ArtifactClass.RESEARCH_CONTRIBUTION:
            return [(c, c.exemplar_refs) for c in corpus.contributions]
        if artifact_class is ArtifactClass.STANDARD_ANALYSIS:
            return [(s, (s.standard_ref,)) for s in corpus.standards]
        if artifact_class is ArtifactClass.RESEARCH_UNIT:
            return [(u, ()) for u in corpus.units]
        return []

    # -- access ----------------------------------------------------------------

    @property
    def ledger(self) -> LedgerRegistry:
        return self._ledger

    def count(self) -> int:
        return self._ledger.count()

    def get(self, record_id: str) -> LedgerEntry | None:
        return self._ledger.get(record_id)

    def record_id_for_ref(self, ref: str) -> str | None:
        """The registered record that owns a content reference (citation resolution)."""
        return self._by_ref.get(ref)

    def citable_refs(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_ref))

    def record_id_for_locator(self, locator: str) -> str | None:
        """The registered research source that owns a substrate locator."""
        return self._by_locator.get(locator)

    def source_locators(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_locator))

    def unit_ids(self) -> tuple[str, ...]:
        return self._ledger.ids_by_class(ArtifactClass.RESEARCH_UNIT)

    def verify(self) -> dict[str, Any]:
        return self._ledger.verify()

    # -- serialization ---------------------------------------------------------

    def document(self) -> dict[str, Any]:
        snapshot = self._ledger.snapshot()
        snapshot.update(
            {
                "programme": PROGRAMME,
                "authority": AUTHORITY,
                "corpus_counts": self.corpus.counts(),
                "citable_reference_count": len(self._by_ref),
            }
        )
        return snapshot


__all__ = ["SCHEMA", "VERSION", "ResearchRegistry"]
