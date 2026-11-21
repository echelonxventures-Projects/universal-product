"""EC2-TASK-000101 — Blueprint Versioning (EC2-EPIC-006).

The authoritative **content-addressed immutability + append-only lineage** versioning
model (Program P5/P18; Foundation ``content_hash``; the same discipline the certified
EC-1 Certification Ledger and ``platform/security/classification.py::ClassificationLedger``
apply). EPIC-006 reuses it, inventing no new versioning semantics (Determination §9):

    * **Version model** — each blueprint version is an immutable, content-addressed
      record; the version identity is a pure function of ``{blueprint_id, revision,
      content_hash, metadata}`` (identical content ⇒ identical version id).
    * **Revision model** — a new revision is a new immutable version bound to the same
      blueprint lineage root; prior revisions are never mutated.
    * **Immutability model** — no in-place edit; every change appends a new version.
    * **Lineage model** — each version references its parent version (append-only chain
      from the lineage root), yielding a verifiable, reproducible history.
    * **Supersession model** — a later version MAY supersede an earlier one (marking it
      superseded by reference) without deleting or mutating it; superseded versions
      remain discoverable for audit/provenance.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.blueprints.errors import BlueprintVersionError
from platform.blueprints.metadata import EMPTY_METADATA, BlueprintMetadata
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class BlueprintVersion:
    """An immutable, content-addressed blueprint version bound to a lineage root.

    ``version_id`` is content-addressed from ``{blueprint_id, revision, content_hash,
    metadata}``. ``parent_version_id`` references the prior revision (``None`` for the
    lineage root). ``superseded_by`` names a later version that supersedes this one
    (set immutably via :meth:`superseded`), or ``None`` while current.
    """

    version_id: str
    blueprint_id: str
    revision: int
    content_hash: str
    parent_version_id: str | None
    superseded_by: str | None
    metadata: BlueprintMetadata

    @classmethod
    def create(
        cls,
        *,
        blueprint_id: str,
        revision: int,
        content_hash: str,
        parent_version_id: str | None = None,
        metadata: BlueprintMetadata | None = None,
    ) -> BlueprintVersion:
        """Build an immutable, content-addressed version (deterministic)."""
        if not isinstance(blueprint_id, str) or not blueprint_id:
            raise BlueprintVersionError("version requires a blueprint_id")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            raise BlueprintVersionError(
                "version revision must be a positive integer", blueprint_id=blueprint_id
            )
        if not isinstance(content_hash, str) or not content_hash:
            raise BlueprintVersionError(
                "version requires a non-empty content_hash", blueprint_id=blueprint_id
            )
        if parent_version_id is not None and (
            not isinstance(parent_version_id, str) or not parent_version_id
        ):
            raise BlueprintVersionError(
                "parent_version_id must be a non-empty string when provided",
                blueprint_id=blueprint_id,
            )
        if revision == 1 and parent_version_id is not None:
            raise BlueprintVersionError(
                "the lineage root (revision 1) must have no parent", blueprint_id=blueprint_id
            )
        if revision > 1 and parent_version_id is None:
            raise BlueprintVersionError(
                "a non-root revision must reference a parent version",
                blueprint_id=blueprint_id,
            )
        md = metadata if metadata is not None else EMPTY_METADATA
        if not isinstance(md, BlueprintMetadata):
            raise BlueprintVersionError("version metadata must be a BlueprintMetadata")
        core = {
            "blueprint_id": blueprint_id,
            "revision": revision,
            "content_hash": content_hash,
            "parent_version_id": parent_version_id,
            "metadata": md.to_dict(),
        }
        return cls(
            version_id=f"UCOS-BVER-{content_hash_of(core)}",
            blueprint_id=blueprint_id,
            revision=revision,
            content_hash=content_hash,
            parent_version_id=parent_version_id,
            superseded_by=None,
            metadata=md,
        )

    def superseded(self, superseded_by: str) -> BlueprintVersion:
        """Return an immutable copy marked superseded by ``superseded_by`` (never mutates)."""
        if not isinstance(superseded_by, str) or not superseded_by:
            raise BlueprintVersionError(
                "superseded_by must be a non-empty version id", version_id=self.version_id
            )
        if superseded_by == self.version_id:
            raise BlueprintVersionError(
                "a version cannot supersede itself", version_id=self.version_id
            )
        return BlueprintVersion(
            version_id=self.version_id,
            blueprint_id=self.blueprint_id,
            revision=self.revision,
            content_hash=self.content_hash,
            parent_version_id=self.parent_version_id,
            superseded_by=superseded_by,
            metadata=self.metadata,
        )

    @property
    def is_root(self) -> bool:
        return self.parent_version_id is None

    @property
    def is_current(self) -> bool:
        """True iff this version has not been superseded."""
        return self.superseded_by is None

    def to_dict(self) -> dict[str, Any]:
        return {
            "version_id": self.version_id,
            "blueprint_id": self.blueprint_id,
            "revision": self.revision,
            "content_hash": self.content_hash,
            "parent_version_id": self.parent_version_id,
            "superseded_by": self.superseded_by,
            "metadata": self.metadata.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash_of(self.to_dict())


def content_hash_of(payload: Any) -> str:
    """Return the 16-hex content-addressed suffix used for version ids (deterministic)."""
    return content_hash(payload)[:16]


class VersionLineage:
    """A deterministic, append-only lineage of immutable blueprint versions.

    Holds the ordered revision chain for a single blueprint: revision 1 is the root,
    each subsequent revision references its parent, and supersession is recorded by
    marking the prior current version superseded (immutably) when a newer one is added.
    """

    __slots__ = ("_blueprint_id", "_versions")

    def __init__(self, blueprint_id: str) -> None:
        if not isinstance(blueprint_id, str) or not blueprint_id:
            raise BlueprintVersionError("a lineage requires a blueprint_id")
        self._blueprint_id = blueprint_id
        self._versions: list[BlueprintVersion] = []

    @property
    def blueprint_id(self) -> str:
        return self._blueprint_id

    def __len__(self) -> int:
        return len(self._versions)

    @property
    def revisions(self) -> tuple[BlueprintVersion, ...]:
        """Every version in revision order (append-only)."""
        return tuple(self._versions)

    def head(self) -> BlueprintVersion:
        """The current (non-superseded) head version (fail-closed on empty)."""
        if not self._versions:
            raise BlueprintVersionError("lineage has no versions", blueprint_id=self._blueprint_id)
        return self._versions[-1]

    def append(
        self, content_hash: str, *, metadata: BlueprintMetadata | None = None
    ) -> BlueprintVersion:
        """Append a new immutable revision, superseding the prior head (append-only).

        Revision 1 is the lineage root; each later revision references the prior head
        as its parent and marks that prior head superseded (without mutating history).
        """
        revision = len(self._versions) + 1
        parent = self._versions[-1] if self._versions else None
        version = BlueprintVersion.create(
            blueprint_id=self._blueprint_id,
            revision=revision,
            content_hash=content_hash,
            parent_version_id=parent.version_id if parent is not None else None,
            metadata=metadata,
        )
        if parent is not None:
            self._versions[-1] = parent.superseded(version.version_id)
        self._versions.append(version)
        return version

    def get(self, version_id: str) -> BlueprintVersion:
        """Resolve a version by id (fail-closed on absent)."""
        for version in self._versions:
            if version.version_id == version_id:
                return version
        raise BlueprintVersionError(
            "no such version", blueprint_id=self._blueprint_id, version_id=version_id
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint_id": self._blueprint_id,
            "revision_count": len(self._versions),
            "versions": [v.to_dict() for v in self._versions],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["BlueprintVersion", "VersionLineage", "content_hash_of"]
