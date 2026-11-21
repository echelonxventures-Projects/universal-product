"""UCOS-CTRL-000001 — Universal Version Engine (Wave 4).

A version string tells you nothing you can act on. ``"1.2.0"`` cannot say what it
came from, whether it may be promoted, what rolling it back would restore, or
whether the thing it labels still hashes to what it labelled. This engine makes
version an executable capability instead of an annotation.

Seven dimensions are versioned independently — semantic, constitutional,
artifact, capability, implementation, governance and certification — because they
move at different rates: a certification can be reissued without the
implementation changing, and an implementation can change without the
constitution moving. Collapsing them into one string is what makes "what version
is this?" unanswerable in a repository this size.

Every version is an immutable, content-addressed :class:`VersionRecord` with a
parent, so a lineage is a chain rather than a list. That is what makes the six
required operations real:

    lineage      the chain of records for one subject in one dimension
    ancestry     the walk from any record back to its lineage root
    comparison   semantic ordering, total over parseable versions
    promotion    an append that raises the version and inherits the parent
    rollback     an append that *restores* an earlier content without deleting
                 the history that produced it
    replay       recomputing every content address in a lineage and failing
                 closed the moment one of them no longer verifies

Nothing here consults the clock, so a lineage replayed on another machine
reproduces byte-identical identities.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from platform.universal_control_plane.errors import ObjectNotFoundError, VersionError
from platform.universal_control_plane.ontology import (
    VERSION_ARTIFACT,
    VERSION_CAPABILITY,
    VERSION_CERTIFICATION,
    VERSION_CONSTITUTIONAL,
    VERSION_GOVERNANCE,
    VERSION_IMPLEMENTATION,
    VERSION_KINDS,
    VERSION_SEMANTIC,
    VersionRecord,
    payload_digest,
)
from typing import Any

#: Promotion levels a caller may request.
LEVEL_MAJOR = "major"
LEVEL_MINOR = "minor"
LEVEL_PATCH = "patch"
PROMOTION_LEVELS: tuple[str, ...] = (LEVEL_MAJOR, LEVEL_MINOR, LEVEL_PATCH)

_VERSION_PATTERN = re.compile(
    r"^\s*v?(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?"
    r"(?:[-+](?P<pre>[0-9A-Za-z.\-+]+))?\s*$"
)


@dataclass(frozen=True, slots=True)
class SemanticVersion:
    """A parsed, totally ordered version.

    A pre-release sorts *before* the release it precedes (``1.0.0-rc1`` <
    ``1.0.0``), which is the only ordering under which promoting out of a
    pre-release is an increase rather than a decrease.
    """

    major: int
    minor: int = 0
    patch: int = 0
    pre: str = ""

    @classmethod
    def parse(cls, value: str) -> SemanticVersion:
        """Parse *value*; raises :class:`VersionError` when it is not a version."""
        match = _VERSION_PATTERN.match(value or "")
        if match is None:
            raise VersionError(f"not a parseable version: {value!r}")
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor") or 0),
            patch=int(match.group("patch") or 0),
            pre=match.group("pre") or "",
        )

    @classmethod
    def try_parse(cls, value: str) -> SemanticVersion | None:
        """Parse *value*, or return ``None`` when it is not a version."""
        try:
            return cls.parse(value)
        except VersionError:
            return None

    @property
    def sort_key(self) -> tuple[int, int, int, int, str]:
        # A present pre-release ranks 0 (earlier); its absence ranks 1 (later).
        return (self.major, self.minor, self.patch, 0 if self.pre else 1, self.pre)

    def __lt__(self, other: SemanticVersion) -> bool:
        return self.sort_key < other.sort_key

    def __le__(self, other: SemanticVersion) -> bool:
        return self.sort_key <= other.sort_key

    def bump(self, level: str = LEVEL_PATCH) -> SemanticVersion:
        """The next version at *level*. Dropping a pre-release is itself a bump."""
        if level not in PROMOTION_LEVELS:
            raise VersionError(f"unknown promotion level: {level!r}")
        if level == LEVEL_MAJOR:
            return SemanticVersion(self.major + 1, 0, 0)
        if level == LEVEL_MINOR:
            return SemanticVersion(self.major, self.minor + 1, 0)
        if self.pre:
            # Promoting a pre-release releases it rather than advancing past it.
            return SemanticVersion(self.major, self.minor, self.patch)
        return SemanticVersion(self.major, self.minor, self.patch + 1)

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"{base}-{self.pre}" if self.pre else base

    def to_dict(self) -> dict[str, Any]:
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "pre": self.pre,
            "version": str(self),
        }


def compare_versions(left: str, right: str) -> int:
    """Return -1/0/1 comparing two version strings.

    Unparseable versions fall back to a stable lexical comparison rather than
    raising: the repository carries constitutional versions that are not semantic,
    and refusing to order them would make the whole lineage unsortable.
    """
    a = SemanticVersion.try_parse(left)
    b = SemanticVersion.try_parse(right)
    if a is not None and b is not None:
        if a.sort_key == b.sort_key:
            return 0
        return -1 if a < b else 1
    if a is not None:
        return 1  # a parseable version outranks an opaque token
    if b is not None:
        return -1
    return (left > right) - (left < right)


@dataclass
class VersionEngine:
    """Append-only, content-addressed versioning across all seven dimensions."""

    _lineages: dict[tuple[str, str], list[VersionRecord]] = field(default_factory=dict)
    _by_version_id: dict[str, VersionRecord] = field(default_factory=dict)

    # -- registration ----------------------------------------------------

    def register(
        self,
        subject_id: str,
        *,
        kind: str = VERSION_SEMANTIC,
        version: str,
        content_digest: str = "",
        rationale: str = "",
        tick: int = 0,
    ) -> VersionRecord:
        """Append a version to a subject's lineage in one dimension.

        Re-registering the identical version *and* content is idempotent: the
        existing record is returned rather than a duplicate revision appended, so
        a repeated discovery pass does not inflate every lineage.
        """
        if not subject_id.strip():
            raise VersionError("a version requires a non-empty subject_id")
        if kind not in VERSION_KINDS:
            raise VersionError(f"unknown version kind: {kind!r} (expected one of {VERSION_KINDS})")
        if not version.strip():
            raise VersionError(f"a {kind} version of {subject_id!r} must be non-empty")

        chain = self._lineages.setdefault((subject_id, kind), [])
        if chain:
            head = chain[-1]
            if head.version == version and head.content_digest == content_digest:
                return head
        record = VersionRecord(
            subject_id=subject_id,
            kind=kind,
            version=version,
            revision=len(chain) + 1,
            content_digest=content_digest,
            parent_version_id=chain[-1].version_id if chain else "",
            rationale=rationale,
            tick=tick,
        )
        if chain:
            self._supersede(chain, len(chain) - 1, record.version_id)
        chain.append(record)
        self._by_version_id[record.version_id] = record
        return record

    def _supersede(self, chain: list[VersionRecord], index: int, successor_id: str) -> None:
        """Mark ``chain[index]`` superseded, preserving its identity.

        ``superseded_by`` is deliberately outside the content address: a record's
        identity must not change when something later points at it, or every
        ancestor link in the lineage would break on the next append.
        """
        old = chain[index]
        updated = VersionRecord(
            subject_id=old.subject_id,
            kind=old.kind,
            version=old.version,
            revision=old.revision,
            content_digest=old.content_digest,
            parent_version_id=old.parent_version_id,
            superseded_by=successor_id,
            rationale=old.rationale,
            attributes=old.attributes,
            tick=old.tick,
        )
        chain[index] = updated
        self._by_version_id[updated.version_id] = updated

    # -- retrieval -------------------------------------------------------

    def current(self, subject_id: str, *, kind: str = VERSION_SEMANTIC) -> VersionRecord:
        """The head of a subject's lineage in one dimension."""
        chain = self._lineages.get((subject_id, kind))
        if not chain:
            raise ObjectNotFoundError(f"no {kind} version registered for: {subject_id}")
        return chain[-1]

    def current_version(self, subject_id: str, *, kind: str = VERSION_SEMANTIC) -> str:
        """The head version string, or the empty string when the lineage is absent."""
        chain = self._lineages.get((subject_id, kind))
        return chain[-1].version if chain else ""

    def get(self, version_id: str) -> VersionRecord:
        if version_id not in self._by_version_id:
            raise ObjectNotFoundError(f"version record not found: {version_id}")
        return self._by_version_id[version_id]

    def lineage(
        self, subject_id: str, *, kind: str = VERSION_SEMANTIC
    ) -> tuple[VersionRecord, ...]:
        """Every revision for a subject in one dimension, oldest first."""
        return tuple(self._lineages.get((subject_id, kind), ()))

    def ancestry(self, version_id: str) -> tuple[VersionRecord, ...]:
        """Walk from *version_id* back to its lineage root, newest first."""
        record = self.get(version_id)
        chain = [record]
        seen = {version_id}
        while record.parent_version_id:
            if record.parent_version_id in seen:
                raise VersionError(f"version ancestry loops at {record.parent_version_id!r}")
            seen.add(record.parent_version_id)
            record = self.get(record.parent_version_id)
            chain.append(record)
        return tuple(chain)

    def subjects(self, *, kind: str | None = None) -> tuple[str, ...]:
        return tuple(sorted({s for (s, k) in self._lineages if kind is None or k == kind}))

    def kinds_for(self, subject_id: str) -> tuple[str, ...]:
        return tuple(sorted(k for (s, k) in self._lineages if s == subject_id))

    def count(self) -> int:
        return sum(len(chain) for chain in self._lineages.values())

    # -- comparison ------------------------------------------------------

    def compare(self, subject_id: str, other_id: str, *, kind: str = VERSION_SEMANTIC) -> int:
        """Compare two subjects' current versions in one dimension."""
        return compare_versions(
            self.current(subject_id, kind=kind).version,
            self.current(other_id, kind=kind).version,
        )

    def is_ahead_of(self, subject_id: str, other_id: str, *, kind: str = VERSION_SEMANTIC) -> bool:
        return self.compare(subject_id, other_id, kind=kind) > 0

    # -- promotion and rollback ------------------------------------------

    def promote(
        self,
        subject_id: str,
        *,
        kind: str = VERSION_SEMANTIC,
        level: str = LEVEL_PATCH,
        content_digest: str = "",
        rationale: str = "",
        tick: int = 0,
    ) -> VersionRecord:
        """Append the next version at *level*, inheriting the current head as parent."""
        head = self.current(subject_id, kind=kind)
        parsed = SemanticVersion.try_parse(head.version)
        if parsed is None:
            raise VersionError(
                f"cannot promote an unparseable {kind} version: {head.version!r} "
                f"(subject {subject_id!r})"
            )
        return self.register(
            subject_id,
            kind=kind,
            version=str(parsed.bump(level)),
            content_digest=content_digest or head.content_digest,
            rationale=rationale or f"promoted {level} from {head.version}",
            tick=tick,
        )

    def rollback(
        self,
        subject_id: str,
        *,
        kind: str = VERSION_SEMANTIC,
        to_revision: int,
        rationale: str = "",
        tick: int = 0,
    ) -> VersionRecord:
        """Restore an earlier revision by *appending* it forward.

        Nothing is deleted. Rolling back to revision 2 appends a new head whose
        version and content are revision 2's, so the history that produced the
        rollback survives it — which is what makes the rollback itself replayable.
        """
        chain = self.lineage(subject_id, kind=kind)
        if not chain:
            raise ObjectNotFoundError(f"no {kind} version registered for: {subject_id}")
        target = next((r for r in chain if r.revision == to_revision), None)
        if target is None:
            raise VersionError(
                f"revision {to_revision} is not in the {kind} lineage of {subject_id!r} "
                f"(available: 1..{len(chain)})"
            )
        if target.revision == chain[-1].revision:
            raise VersionError(
                f"revision {to_revision} is already the head of {subject_id!r}; "
                "nothing to roll back"
            )
        head = chain[-1]
        # Force an append even though version+digest match the target: a rollback
        # is a distinct event and the idempotence shortcut must not swallow it.
        mutable = self._lineages[(subject_id, kind)]
        record = VersionRecord(
            subject_id=subject_id,
            kind=kind,
            version=target.version,
            revision=len(mutable) + 1,
            content_digest=target.content_digest,
            parent_version_id=head.version_id,
            rationale=rationale or f"rolled back from {head.version} to revision {to_revision}",
            attributes={"rollback_of": head.version_id, "restored_revision": to_revision},
            tick=tick,
        )
        self._supersede(mutable, len(mutable) - 1, record.version_id)
        mutable.append(record)
        self._by_version_id[record.version_id] = record
        return record

    # -- replay ----------------------------------------------------------

    def replay(self, subject_id: str, *, kind: str = VERSION_SEMANTIC) -> tuple[VersionRecord, ...]:
        """Recompute a lineage and fail closed the moment a link no longer verifies.

        Checks three invariants a lineage cannot survive losing: revisions are
        contiguous from 1, each record's parent is the record before it, and every
        content address still recomputes to the identity it was stored under.
        """
        chain = self.lineage(subject_id, kind=kind)
        if not chain:
            raise ObjectNotFoundError(f"no {kind} version registered for: {subject_id}")
        previous: VersionRecord | None = None
        for index, record in enumerate(chain):
            expected_revision = index + 1
            if record.revision != expected_revision:
                raise VersionError(
                    f"{kind} lineage of {subject_id!r} breaks at position {expected_revision}: "
                    f"recorded revision {record.revision}"
                )
            expected_parent = previous.version_id if previous is not None else ""
            if record.parent_version_id != expected_parent:
                raise VersionError(
                    f"{kind} lineage of {subject_id!r} breaks at revision {record.revision}: "
                    f"parent {record.parent_version_id!r} != {expected_parent!r}"
                )
            if self._by_version_id.get(record.version_id) is None:
                raise VersionError(
                    f"{kind} lineage of {subject_id!r} references an unindexed version "
                    f"at revision {record.revision}"
                )
            previous = record
        return chain

    def verify(self, subject_id: str, *, kind: str = VERSION_SEMANTIC) -> bool:
        """True iff the lineage replays; raises :class:`VersionError` when it does not."""
        self.replay(subject_id, kind=kind)
        return True

    def replay_digest(self) -> str:
        """A content digest over every lineage — equal iff the whole history is equal."""
        return payload_digest(
            [
                {
                    "subject": subject,
                    "kind": kind,
                    "records": [r.to_dict() for r in self._lineages[(subject, kind)]],
                }
                for (subject, kind) in sorted(self._lineages)
            ]
        )

    # -- bulk ingestion --------------------------------------------------

    def ingest_change_ledger(
        self, ledger: Mapping[str, Any], *, kind: str = VERSION_ARTIFACT, tick: int = 0
    ) -> int:
        """Load the repository's recorded version history into a versioned dimension.

        The change ledger already holds every artifact's version history with its
        content baseline. Re-deriving that would be a second authority over the
        same knowledge; this reads it and returns how many records were appended.
        """
        records = ledger.get("version_records")
        if not isinstance(records, Mapping):
            raise VersionError("change ledger has no 'version_records' mapping")
        appended = 0
        for subject_id in sorted(records):
            entry = records[subject_id]
            if not isinstance(entry, Mapping):
                continue
            history = entry.get("history")
            if not isinstance(history, list):
                continue
            for item in history:
                if not isinstance(item, Mapping):
                    continue
                version = str(item.get("version", "") or "")
                if not version:
                    continue
                before = self.count()
                self.register(
                    subject_id,
                    kind=kind,
                    version=version,
                    content_digest=str(item.get("content_hash", "") or ""),
                    rationale="ingested from the repository change ledger",
                    tick=tick,
                )
                appended += self.count() - before
        return appended

    def ingest(
        self,
        pairs: Iterable[tuple[str, str]],
        *,
        kind: str,
        digests: Mapping[str, str] | None = None,
        tick: int = 0,
    ) -> tuple[VersionRecord, ...]:
        """Register one dimension for many subjects from ``(subject_id, version)`` pairs."""
        lookup = digests or {}
        return tuple(
            self.register(
                subject_id,
                kind=kind,
                version=version,
                content_digest=lookup.get(subject_id, ""),
                tick=tick,
            )
            for subject_id, version in sorted(pairs)
            if version
        )

    # -- projection ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        by_kind: dict[str, int] = {}
        for _subject, kind in self._lineages:
            by_kind[kind] = by_kind.get(kind, 0) + 1
        return {
            "engine": "VersionEngine",
            "kinds": list(VERSION_KINDS),
            "counts": {
                "records": self.count(),
                "lineages": len(self._lineages),
                "subjects": len(self.subjects()),
                "by_kind": dict(sorted(by_kind.items())),
            },
            "replay_digest": self.replay_digest(),
        }


__all__ = [
    "LEVEL_MAJOR",
    "LEVEL_MINOR",
    "LEVEL_PATCH",
    "PROMOTION_LEVELS",
    "VERSION_ARTIFACT",
    "VERSION_CAPABILITY",
    "VERSION_CERTIFICATION",
    "VERSION_CONSTITUTIONAL",
    "VERSION_GOVERNANCE",
    "VERSION_IMPLEMENTATION",
    "VERSION_KINDS",
    "VERSION_SEMANTIC",
    "SemanticVersion",
    "VersionEngine",
    "compare_versions",
]
