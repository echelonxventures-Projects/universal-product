"""An append-only, content-addressed, Knowledge-Once, hash-chained registry ledger.

The Universal Registry Platform (``engine.registry.universal``) is the single
registration authority for the twelve *platform* artifact kinds and stays that.
Research and publication artifacts are **derived truth** produced by additive
intelligence; registering them in the platform would create a second, competing
population inside a certified authority. The ledger therefore applies the same
invariants — deterministic identity, append-only registration, Knowledge-Once
content equality, duplicate rejection, and a tamper-evident hash chain — to the
derived population, and publishes its own deterministic JSON envelope.

Invariants (all fail-closed):
  1. identity is a pure function of ``(class, namespace, natural_key)``
  2. an identity is registered exactly once (append-only, never overwritten)
  3. identical content under two identities is a Knowledge-Once violation
  4. every registration is journalled into a SHA-256 chain that recomputes
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from intelligence.kernel.canonical import canonical_json, sha256_text
from intelligence.kernel.errors import (
    DuplicateRecordError,
    KnowledgeOnceViolation,
    LedgerIntegrityError,
)
from intelligence.kernel.ids import ArtifactClass, artifact_id, content_digest

#: The first link of every journal chain.
GENESIS_HASH = "0" * 64

#: The single journalled act — the ledger is append-only, so there is no other.
ACT_REGISTER = "REGISTER"


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    """One registered derived artifact."""

    record_id: str
    artifact_class: str
    namespace: str
    natural_key: str
    content_digest: str
    payload: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "artifact_class": self.artifact_class,
            "namespace": self.namespace,
            "natural_key": self.natural_key,
            "content_digest": self.content_digest,
            "payload": dict(self.payload),
        }


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """One tamper-evident link of the registration chain."""

    sequence: int
    act: str
    record_id: str
    content_digest: str
    previous_hash: str
    entry_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "act": self.act,
            "record_id": self.record_id,
            "content_digest": self.content_digest,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }


def _link_hash(previous: str, act: str, record_id: str, digest: str, sequence: int) -> str:
    return sha256_text(canonical_json([previous, act, record_id, digest, sequence]))


@dataclass
class LedgerRegistry:
    """A deterministic, append-only registry of derived intelligence artifacts."""

    registry_id: str
    schema: str
    version: str = "1.0.0"
    _entries: dict[str, LedgerEntry] = field(default_factory=dict, repr=False)
    _by_content: dict[str, str] = field(default_factory=dict, repr=False)
    _journal: list[JournalEntry] = field(default_factory=list, repr=False)

    # -- registration ----------------------------------------------------------

    def register(
        self,
        artifact_class: ArtifactClass | str,
        natural_key: str,
        payload: Mapping[str, Any],
        *,
        namespace: str | None = None,
    ) -> LedgerEntry:
        """Register one artifact, enforcing every ledger invariant (fail-closed)."""
        klass = ArtifactClass.coerce(artifact_class)
        ns = namespace or klass.default_namespace
        record_id = artifact_id(klass, natural_key, namespace=ns)
        if record_id in self._entries:
            raise DuplicateRecordError(
                "identity already registered in an append-only ledger",
                registry=self.registry_id,
                record_id=record_id,
                natural_key=natural_key,
                artifact_class=klass.value,
            )
        digest = content_digest(payload)
        owner = self._by_content.get(digest)
        if owner is not None:
            raise KnowledgeOnceViolation(
                "identical content registered under a second identity",
                registry=self.registry_id,
                record_id=record_id,
                existing_record_id=owner,
                content_digest=digest,
            )
        entry = LedgerEntry(
            record_id=record_id,
            artifact_class=klass.value,
            namespace=ns,
            natural_key=natural_key,
            content_digest=digest,
            payload=dict(payload),
        )
        self._entries[record_id] = entry
        self._by_content[digest] = record_id
        previous = self._journal[-1].entry_hash if self._journal else GENESIS_HASH
        sequence = len(self._journal) + 1
        self._journal.append(
            JournalEntry(
                sequence=sequence,
                act=ACT_REGISTER,
                record_id=record_id,
                content_digest=digest,
                previous_hash=previous,
                entry_hash=_link_hash(previous, ACT_REGISTER, record_id, digest, sequence),
            )
        )
        return entry

    # -- lookup ----------------------------------------------------------------

    def get(self, record_id: str) -> LedgerEntry | None:
        return self._entries.get(record_id)

    def exists(self, record_id: str) -> bool:
        return record_id in self._entries

    def id_for(
        self,
        artifact_class: ArtifactClass | str,
        natural_key: str,
        *,
        namespace: str | None = None,
    ) -> str:
        klass = ArtifactClass.coerce(artifact_class)
        return artifact_id(klass, natural_key, namespace=namespace or klass.default_namespace)

    def all(self) -> tuple[LedgerEntry, ...]:
        return tuple(self._entries[k] for k in sorted(self._entries))

    def by_class(self, artifact_class: ArtifactClass | str) -> tuple[LedgerEntry, ...]:
        value = ArtifactClass.coerce(artifact_class).value
        return tuple(e for e in self.all() if e.artifact_class == value)

    def ids_by_class(self, artifact_class: ArtifactClass | str) -> tuple[str, ...]:
        return tuple(e.record_id for e in self.by_class(artifact_class))

    def count(self) -> int:
        return len(self._entries)

    def class_histogram(self) -> dict[str, int]:
        histogram: dict[str, int] = {}
        for entry in self.all():
            histogram[entry.artifact_class] = histogram.get(entry.artifact_class, 0) + 1
        return dict(sorted(histogram.items()))

    def journal(self) -> tuple[JournalEntry, ...]:
        return tuple(self._journal)

    def head(self) -> str:
        return self._journal[-1].entry_hash if self._journal else GENESIS_HASH

    # -- integrity -------------------------------------------------------------

    def verify(self) -> dict[str, Any]:
        """Recompute the chain and the content index. Never raises; reports."""
        broken: list[int] = []
        previous = GENESIS_HASH
        for entry in self._journal:
            expected = _link_hash(
                previous, entry.act, entry.record_id, entry.content_digest, entry.sequence
            )
            if entry.previous_hash != previous or entry.entry_hash != expected:
                broken.append(entry.sequence)
            previous = entry.entry_hash
        digests: dict[str, list[str]] = {}
        for record in self.all():
            digests.setdefault(record.content_digest, []).append(record.record_id)
        collisions = {d: ids for d, ids in sorted(digests.items()) if len(ids) > 1}
        return {
            "registry_id": self.registry_id,
            "records": self.count(),
            "journal_length": len(self._journal),
            "chain_intact": not broken,
            "broken_links": broken,
            "knowledge_once_holds": not collisions,
            "content_collisions": collisions,
            "head": self.head(),
            "intact": not broken and not collisions,
        }

    def require_integrity(self) -> None:
        report = self.verify()
        if not report["intact"]:
            raise LedgerIntegrityError(
                "ledger integrity check failed",
                **{
                    "registry": self.registry_id,
                    "broken_links": report["broken_links"],
                    "content_collisions": sorted(report["content_collisions"]),
                },
            )

    # -- serialization ---------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        return {
            "registry_id": self.registry_id,
            "schema": self.schema,
            "version": self.version,
            "count": self.count(),
            "class_histogram": self.class_histogram(),
            "records": [e.to_dict() for e in self.all()],
            "journal": [j.to_dict() for j in self.journal()],
            "journal_head": self.head(),
            "integrity": self.verify(),
        }


__all__ = [
    "ACT_REGISTER",
    "GENESIS_HASH",
    "JournalEntry",
    "LedgerEntry",
    "LedgerRegistry",
]
