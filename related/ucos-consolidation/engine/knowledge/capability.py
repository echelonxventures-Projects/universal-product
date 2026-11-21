"""UKDA Part 04/09 — Repository Self-Awareness (capability knowledge).

Projects the repository's **discovered, implemented capabilities** into the canonical
knowledge layer, so that "does this already exist?" is answerable from canonical
knowledge alone rather than from a human's memory of the source tree.

Why this module exists
----------------------
The Knowledge Reuse Engine (:mod:`engine.knowledge.integration.reuse`) decides
``reuse > extend > compose > create`` by searching the canonical base. Before this
module existed, the base held only the eleven founding seed objects: none of the
repository's *implemented capabilities* were canonical knowledge. The engine was
therefore structurally blind to the repository's own implementation and answered
``CREATE`` for every capability that already existed — the precise failure the
Knowledge Once Principle (``UCKO-PRIN-0001``) exists to prevent. Repository Truth
could not see itself.

Discovery is **not** re-implemented here
----------------------------------------
:func:`intelligence.rie.discovery.discover` is the registered owner of capability
discovery (it derives the capability universe from the ``git ls-files`` eligibility
boundary). This module consumes the catalogue that engine already emits —
``intelligence/UCOS-RIE-CAPABILITY-CATALOG.json`` — as **data**, exactly as
:meth:`engine.knowledge.ukip.providers.MappingProvider.from_json_file` consumes a
provider payload. Reading the catalogue as data rather than importing the engine
keeps the layering intact: ``intelligence`` depends on ``engine``, never the
reverse, so ``engine`` may not import ``intelligence``.

Knowledge Once
--------------
:func:`assimilate_capabilities` authors a capability object only where Repository
Truth proves one is missing, and rewrites one only where the discovered substance
has drifted from the recorded substance. An unchanged capability is left byte-identical,
so re-running the projection is a no-op and the store never churns.

Determinism
-----------
Identifiers are derived from the capability's canonical location, never minted from a
counter or a clock, so the same repository always yields the same identifiers. No
wall-clock value is recorded (IMP-007 §5). Standard library only (TP-04/TP-05).
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.errors import KnowledgeSourceError, KnowledgeValidationError
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle, content_hash
from engine.knowledge.store import KnowledgeBase

#: The universe every capability object is authored into. A dedicated universe keeps
#: capability facts addressable as a set without polluting the constitutional universes.
CAPABILITY_UNIVERSE = "CAPABILITY"

#: Prefix of every derived capability identifier.
CAPABILITY_ID_PREFIX = "UCKO-CAP"

#: Hex characters of the location digest carried by a derived identifier. Matches the
#: 12-character discipline of :mod:`engine.registry.universal.identity` and
#: :mod:`engine.knowledge.ukip.contracts`.
CAPABILITY_ID_DIGEST_LEN = 12

#: Tag marking an object as a capability fact (the machine-checkable membership test).
CAPABILITY_TAG = "capability"

#: Tag marking a capability the repository forbids replacing (reuse is mandatory).
REPLACEMENT_PROHIBITED_TAG = "replacement-prohibited"

#: Tag marking a capability whose purpose is to *verify* other capabilities. Such a
#: package is a legitimate capability and is catalogued as one, but it is never a
#: sensible answer to "what should I reuse to build this?" — you do not implement
#: provenance by reusing the provenance tests. Its symbol surface is also the densest
#: in the repository (hundreds of ``test_<subject>`` names), so leaving it eligible
#: makes it outrank every real owner on every subject.
VERIFICATION_TAG = "verification"

#: Repository-relative location of the catalogue this module projects.
DEFAULT_CATALOG_PATH = "intelligence/UCOS-RIE-CAPABILITY-CATALOG.json"

#: The founding principle every capability fact is authored in service of. Linking to it
#: states the actual relationship — a capability is recorded so that knowledge about it is
#: authored once — and keeps capability facts connected rather than orphaned in the graph.
KNOWLEDGE_ONCE_PRINCIPLE = "UCKO-PRIN-0001"

#: Catalogue keys required of every record (fail-closed schema).
_REQUIRED_KEYS = (
    "unique_id",
    "canonical_name",
    "canonical_location",
    "category",
    "authority",
    "reuse",
    "replacement_prohibited",
    "implementation_status",
)

#: Discovered implementation status → canonical lifecycle.
#:
#: ``CERTIFIED`` and ``IMPLEMENTED`` map to *active* lifecycles because the capability
#: demonstrably exists, which is what makes it a legitimate reuse target. ``PLANNED``
#: and ``INDETERMINATE`` map to inactive lifecycles so an unbuilt capability can never
#: be offered as one to reuse.
_STATUS_LIFECYCLE: Mapping[str, Lifecycle] = {
    "CERTIFIED": Lifecycle.OPERATIONAL,
    "IMPLEMENTED": Lifecycle.IMPLEMENTED,
    "PLANNED": Lifecycle.APPROVED,
    "INDETERMINATE": Lifecycle.DRAFT,
}

#: Lifecycle for a status the catalogue reports but this module does not recognise.
#: Fail-closed: an unknown status is *not* treated as implemented.
_UNKNOWN_STATUS_LIFECYCLE = Lifecycle.DRAFT


def _slug_tokens(text: str) -> tuple[str, ...]:
    """Split an identifier-ish string into lower-case searchable tokens."""
    cleaned = "".join(ch if ch.isalnum() else " " for ch in text)
    return tuple(part.lower() for part in cleaned.split() if part)


def capability_id(canonical_location: str) -> str:
    """The deterministic identifier of the capability at ``canonical_location``.

    Derived from the location, so the identity of a capability is a function of where
    it lives rather than of the order in which capabilities were discovered.
    """
    if not canonical_location or not canonical_location.strip():
        raise KnowledgeValidationError("capability location must be a non-empty string")
    digest = content_hash({"canonical_location": canonical_location})
    return f"{CAPABILITY_ID_PREFIX}-{digest[:CAPABILITY_ID_DIGEST_LEN].upper()}"


def is_capability(obj: CanonicalKnowledgeObject) -> bool:
    """True iff ``obj`` is a capability fact authored by this module."""
    return obj.universe == CAPABILITY_UNIVERSE and CAPABILITY_TAG in obj.tags


def replacement_prohibited(obj: CanonicalKnowledgeObject) -> bool:
    """True iff the repository forbids replacing the capability ``obj`` records."""
    return REPLACEMENT_PROHIBITED_TAG in obj.tags


def is_verification(obj: CanonicalKnowledgeObject) -> bool:
    """True iff ``obj`` records a capability whose purpose is to verify others."""
    return VERIFICATION_TAG in obj.tags


def is_reuse_candidate(obj: CanonicalKnowledgeObject) -> bool:
    """True iff ``obj`` is an implemented capability worth offering for reuse."""
    return is_capability(obj) and obj.is_active and not is_verification(obj)


@dataclass(frozen=True, slots=True)
class CapabilityRecord:
    """One discovered capability, as declared by the discovery catalogue."""

    unique_id: str
    canonical_name: str
    canonical_location: str
    category: str
    authority: str
    reuse: str
    replacement_prohibited: bool
    implementation_status: str
    description: str = ""
    evidence_present: bool = True
    summary: str = ""
    symbols: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> CapabilityRecord:
        """Parse one catalogue record, failing loudly on a malformed entry."""
        if not isinstance(record, Mapping):
            raise KnowledgeValidationError("capability record must be an object")
        missing = [key for key in _REQUIRED_KEYS if key not in record]
        if missing:
            raise KnowledgeValidationError(
                "capability record is missing required keys",
                missing=missing,
                at=str(record.get("canonical_location", "<unknown>")),
            )
        location = str(record["canonical_location"]).strip()
        if not location:
            raise KnowledgeValidationError("capability record has an empty canonical_location")
        return cls(
            unique_id=str(record["unique_id"]),
            canonical_name=str(record["canonical_name"]),
            canonical_location=location,
            category=str(record["category"]),
            authority=str(record["authority"]),
            reuse=str(record["reuse"]),
            replacement_prohibited=bool(record["replacement_prohibited"]),
            implementation_status=str(record["implementation_status"]),
            description=str(record.get("description") or ""),
            evidence_present=bool(record.get("evidence_present", True)),
            summary=str(record.get("summary") or ""),
            symbols=tuple(str(name) for name in (record.get("symbols") or ())),
        )

    # -- projection ------------------------------------------------------------

    @property
    def is_verification(self) -> bool:
        """True iff this capability's purpose is to verify other capabilities."""
        parts = self.canonical_location.split("/")
        return "tests" in parts or parts[-1].startswith("test")

    @property
    def cko_id(self) -> str:
        """The deterministic canonical identifier of this capability."""
        return capability_id(self.canonical_location)

    @property
    def lifecycle(self) -> Lifecycle:
        """The canonical lifecycle implied by the discovered implementation status."""
        return _STATUS_LIFECYCLE.get(self.implementation_status, _UNKNOWN_STATUS_LIFECYCLE)

    @property
    def is_implemented(self) -> bool:
        """True iff the capability demonstrably exists and may be reused."""
        return self.lifecycle.is_active

    @property
    def owner(self) -> str:
        """The accountable authority, derived from the capability's category."""
        stem = "-".join(part.upper() for part in _slug_tokens(self.category)) or "UNASSIGNED"
        return f"UCOS-{stem}-AUTHORITY"

    def tags(self) -> tuple[str, ...]:
        """Searchable tags, stably ordered.

        The capability's own name and location are tokenised into tags so that ranked
        search can match an intent phrased in the repository's vocabulary
        (``"knowledge import"``) against the capability that implements it, without
        the caller having to know the capability's identifier.
        """
        collected = {
            CAPABILITY_TAG,
            self.category,
            self.implementation_status.lower(),
            *_slug_tokens(self.canonical_name),
            *_slug_tokens(self.canonical_location),
        }
        if self.replacement_prohibited:
            collected.add(REPLACEMENT_PROHIBITED_TAG)
        if self.is_verification:
            collected.add(VERIFICATION_TAG)
        return tuple(sorted(tag for tag in collected if tag))

    def statement(self) -> str:
        """The canonical statement of fact about this capability.

        Carries both halves of the capability's identity: its own described purpose
        (prose) and its public symbol surface (structure). Reuse determination is a
        question about purpose, and a statement that records only a module path can be
        enumerated but not *matched* against an intent phrased in domain language.
        """
        described = (self.summary or self.description).strip()
        detail = f" Its own description of itself: {described}" if described else ""
        surface = (
            f" Its public surface comprises: {', '.join(self.symbols)}." if self.symbols else ""
        )
        return (
            f"The capability '{self.canonical_name}' is implemented in this repository at "
            f"'{self.canonical_location}' and is its single canonical owner. "
            f"Discovered implementation status is {self.implementation_status}; "
            f"declared authority is {self.authority}; declared reuse posture is "
            f"{self.reuse}.{detail}{surface}"
        )

    def rationale(self) -> str:
        """Why this capability object exists (required by the rationale-present gate)."""
        posture = (
            "Replacement is prohibited: this capability must be reused, extended or "
            "composed with, never re-created."
            if self.replacement_prohibited
            else "Replacement is not prohibited, but reuse and extension precede creation."
        )
        return (
            "Recorded so Repository Truth can answer 'does this capability already exist?' "
            "without human assistance, making the Knowledge Once Principle enforceable "
            f"against the repository's own implementation. {posture} "
            f"Discovered from the version-controlled capability catalogue as {self.unique_id}."
        )

    def to_object(self, *, version: str = "1.0.0") -> CanonicalKnowledgeObject:
        """Project this record as a sealed canonical knowledge object."""
        return CanonicalKnowledgeObject.create(
            cko_id=self.cko_id,
            kind=KnowledgeKind.FACT,
            title=f"Capability: {self.canonical_name}",
            statement=self.statement(),
            rationale=self.rationale(),
            universe=CAPABILITY_UNIVERSE,
            authority=KnowledgeAuthority.ENGINEERING,
            owner=self.owner,
            lifecycle=self.lifecycle,
            version=version,
            tags=self.tags(),
            knowledge_links=(KNOWLEDGE_ONCE_PRINCIPLE,),
            documentation_links=(self.canonical_location,),
            evidence=(DEFAULT_CATALOG_PATH,) if self.evidence_present else (),
        )


def load_catalog(path: str | Path) -> tuple[CapabilityRecord, ...]:
    """Load discovered capabilities from a capability catalogue document.

    The catalogue is the output of the registered discovery owner; this function only
    parses it. A malformed or absent catalogue is an error, never an empty result —
    silently returning nothing would make the reuse engine blind again.
    """
    resolved = Path(path)
    if not resolved.is_file():
        raise KnowledgeSourceError("capability catalogue not found", path=str(resolved))
    try:
        document = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KnowledgeSourceError(
            "capability catalogue is not valid JSON", path=str(resolved), detail=str(exc)
        ) from exc
    if not isinstance(document, Mapping):
        raise KnowledgeSourceError("capability catalogue root must be an object")
    records = document.get("capabilities")
    if not isinstance(records, list):
        raise KnowledgeSourceError(
            "capability catalogue is missing its capabilities array", path=str(resolved)
        )
    parsed = [CapabilityRecord.from_dict(record) for record in records]
    by_location: dict[str, CapabilityRecord] = {}
    for record in parsed:
        if record.canonical_location in by_location:
            raise KnowledgeValidationError(
                "capability catalogued more than once",
                canonical_location=record.canonical_location,
            )
        by_location[record.canonical_location] = record
    return tuple(by_location[key] for key in sorted(by_location))


def capability_objects(
    records: Iterable[CapabilityRecord], *, version: str = "1.0.0"
) -> tuple[CanonicalKnowledgeObject, ...]:
    """Project capability records into sealed canonical objects, in stable id order."""
    projected = [record.to_object(version=version) for record in records]
    return tuple(sorted(projected, key=lambda obj: obj.cko_id))


@dataclass(frozen=True, slots=True)
class CapabilityAssimilation:
    """The outcome of projecting discovered capabilities into the canonical base."""

    base: KnowledgeBase
    created: tuple[str, ...]
    updated: tuple[str, ...]
    unchanged: tuple[str, ...]
    retired: tuple[str, ...]

    @property
    def changed(self) -> bool:
        """True iff the canonical base differs from the one supplied."""
        return bool(self.created or self.updated or self.retired)

    def counts(self) -> dict[str, int]:
        return {
            "created": len(self.created),
            "updated": len(self.updated),
            "unchanged": len(self.unchanged),
            "retired": len(self.retired),
            "capabilities": len(self.created) + len(self.updated) + len(self.unchanged),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": self.counts(),
            "created": list(self.created),
            "updated": list(self.updated),
            "unchanged": list(self.unchanged),
            "retired": list(self.retired),
        }


def assimilate_capabilities(
    base: KnowledgeBase,
    records: Sequence[CapabilityRecord],
    *,
    version: str = "1.0.0",
) -> CapabilityAssimilation:
    """Merge discovered capabilities into ``base`` under the Knowledge Once Principle.

    A capability object is authored only where Repository Truth proves one is missing,
    and rewritten only where the discovered substance has drifted from the recorded
    substance (compared by the object's own content digest, so the comparison is the
    same one the store enforces). Unchanged objects are carried through untouched, which
    is what makes re-running the projection a no-op.

    Capability objects whose capability is no longer discoverable are reported as
    ``retired`` and dropped, so a deleted capability cannot linger as a false reuse
    target. Non-capability knowledge is never touched.
    """
    projected = {obj.cko_id: obj for obj in capability_objects(records, version=version)}
    existing_capabilities = {obj.cko_id: obj for obj in base.objects() if is_capability(obj)}
    preserved = [obj for obj in base.objects() if not is_capability(obj)]

    created: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []
    merged: list[CanonicalKnowledgeObject] = []

    for cko_id in sorted(projected):
        candidate = projected[cko_id]
        current = existing_capabilities.get(cko_id)
        if current is None:
            created.append(cko_id)
            merged.append(candidate)
        elif current.content_sha256 != candidate.content_sha256:
            updated.append(cko_id)
            merged.append(candidate)
        else:
            unchanged.append(cko_id)
            merged.append(current)

    retired = tuple(sorted(set(existing_capabilities) - set(projected)))

    return CapabilityAssimilation(
        base=KnowledgeBase((*preserved, *merged), base.decisions()),
        created=tuple(created),
        updated=tuple(updated),
        unchanged=tuple(unchanged),
        retired=retired,
    )


def coverage(records: Sequence[CapabilityRecord], base: KnowledgeBase) -> dict[str, Any]:
    """Capability coverage of the canonical base: what is discovered vs recorded.

    ``uncovered`` is the set that makes the reuse engine blind — a capability the
    repository implements but canonical knowledge does not record.
    """
    discovered = {record.canonical_location: record for record in records}
    recorded = {obj.cko_id for obj in base.objects() if is_capability(obj)}
    covered = sorted(loc for loc, rec in discovered.items() if rec.cko_id in recorded)
    uncovered = sorted(loc for loc, rec in discovered.items() if rec.cko_id not in recorded)
    reusable = sorted(
        loc for loc, rec in discovered.items() if rec.cko_id in recorded and rec.is_implemented
    )
    total = len(discovered)
    return {
        "discovered": total,
        "recorded": len(covered),
        "uncovered": len(uncovered),
        "reusable": len(reusable),
        "coverage_pct": round(100.0 * len(covered) / total, 2) if total else 0.0,
        "uncovered_locations": uncovered,
    }


__all__ = [
    "CAPABILITY_UNIVERSE",
    "CAPABILITY_ID_PREFIX",
    "CAPABILITY_ID_DIGEST_LEN",
    "CAPABILITY_TAG",
    "REPLACEMENT_PROHIBITED_TAG",
    "DEFAULT_CATALOG_PATH",
    "CapabilityRecord",
    "CapabilityAssimilation",
    "capability_id",
    "is_capability",
    "replacement_prohibited",
    "load_catalog",
    "capability_objects",
    "assimilate_capabilities",
    "coverage",
]
