"""UCOS-USAF-001 — Assimilation vocabulary & contracts.

The vocabulary in which *every* source is described, whatever it is made of. The source
taxonomy is deliberately an **open registry** rather than a closed enum: a future source —
one nobody has thought of yet — is declared, not code-changed into an enumeration.

The state machine is closed and total, because an honest system must always be able to say
where a source stopped:

    DISCOVERED → ADMITTED → NORMALIZED → ASSIMILATED
                       ↘ DEFERRED (named reason)
                       ↘ REJECTED (named reason)

A source is **never** silently dropped and never counted as assimilated because a metric
would look better. Identities live in a disjoint ``UCOS-USA*`` namespace, hold no
wall-clock, and are content-addressed (IMP-007 §5).
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import ContractRef, content_hash
from platform.universal_assimilation.errors import (
    AssimilationContractError,
    SourceKindError,
)
from platform.universal_truth.contracts import TruthClass, normalize_locator
from typing import Any

#: The canonical identity of the Universal Source Assimilation Framework instance.
USAF_ID = "UCOS-USAF-001"

#: The semantic version of the assimilation contract surface (AR-03/PL-05).
ASSIMILATION_CONTRACT_VERSION = "1.0.0"

#: Declared source kinds shipped with the framework. The registry is open: declare more.
KIND_CONVERSATION_EXPORT = "conversation-export"
KIND_CHAT_TRANSCRIPT = "chat-transcript"
KIND_MARKDOWN = "markdown"
KIND_PLAIN_TEXT = "plain-text"
KIND_STRUCTURED_JSON = "structured-json"
KIND_DOCUMENT_DOCX = "document-docx"
KIND_DOCUMENT_PDF = "document-pdf"
KIND_SPREADSHEET_CSV = "spreadsheet-csv"
KIND_REPOSITORY = "repository"
KIND_GIT_HISTORY = "git-history"
KIND_API_RESPONSE = "api-response"
KIND_DATABASE_RECORD = "database-record"
KIND_EMAIL_MESSAGE = "email-message"
KIND_UNKNOWN = "unknown"


def normalize_text(text: str) -> str:
    """Collapse whitespace so semantically identical content hashes identically."""
    if not isinstance(text, str):
        raise AssimilationContractError("text must be a string")
    return " ".join(text.split())


def payload_digest(payload: bytes) -> str:
    """The content digest of a raw source payload (deterministic, reproducible)."""
    if not isinstance(payload, bytes | bytearray):
        raise AssimilationContractError("source payload must be bytes")
    return hashlib.sha256(bytes(payload)).hexdigest()


@dataclass(frozen=True, slots=True)
class SourceKindDeclaration:
    """A declared kind of source. Declaring one is how the framework meets a new source."""

    kind_id: str
    description: str = ""
    binary: bool = False
    structured: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.kind_id, str) or not self.kind_id.strip():
            raise SourceKindError("kind_id must be a non-empty string")

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this declaration."""
        return {
            "kind_id": self.kind_id,
            "description": self.description,
            "binary": self.binary,
            "structured": self.structured,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this declaration."""
        return content_hash(self.to_dict())


class SourceKindRegistry:
    """An open, deterministic, fail-closed registry of declared source kinds."""

    __slots__ = ("_kinds",)

    def __init__(self, declarations: Iterable[SourceKindDeclaration] = ()) -> None:
        self._kinds: dict[str, SourceKindDeclaration] = {}
        for declaration in declarations:
            self.declare(declaration)

    def declare(self, declaration: SourceKindDeclaration) -> SourceKindDeclaration:
        """Declare a source kind; idempotent by body, fail-closed on redefinition."""
        if not isinstance(declaration, SourceKindDeclaration):
            raise SourceKindError("registry accepts only SourceKindDeclaration values")
        existing = self._kinds.get(declaration.kind_id)
        if existing is not None:
            if existing.fingerprint() != declaration.fingerprint():
                raise SourceKindError(
                    "source kind already declared with a different body",
                    kind_id=declaration.kind_id,
                )
            return existing
        self._kinds[declaration.kind_id] = declaration
        return declaration

    def declare_kind(
        self,
        kind_id: str,
        *,
        description: str = "",
        binary: bool = False,
        structured: bool = False,
    ) -> SourceKindDeclaration:
        """Declare a source kind from its parts (the ergonomic extension point)."""
        return self.declare(
            SourceKindDeclaration(
                kind_id=kind_id, description=description, binary=binary, structured=structured
            )
        )

    def get(self, kind_id: str) -> SourceKindDeclaration | None:
        """The declared kind ``kind_id``, or ``None``."""
        return self._kinds.get(kind_id)

    def require(self, kind_id: str) -> SourceKindDeclaration:
        """The declared kind ``kind_id`` (fail-closed — an undeclared kind is a fault)."""
        declaration = self.get(kind_id)
        if declaration is None:
            raise SourceKindError("undeclared source kind", kind_id=kind_id)
        return declaration

    def __contains__(self, kind_id: object) -> bool:
        return isinstance(kind_id, str) and kind_id in self._kinds

    @property
    def count(self) -> int:
        """How many kinds are declared."""
        return len(self._kinds)

    def ids(self) -> tuple[str, ...]:
        """Every declared kind identity, sorted."""
        return tuple(sorted(self._kinds))

    def declarations(self) -> tuple[SourceKindDeclaration, ...]:
        """Every declaration, ordered by identity."""
        return tuple(self._kinds[kind_id] for kind_id in self.ids())

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this registry."""
        return {
            "kind_count": self.count,
            "kinds": [declaration.to_dict() for declaration in self.declarations()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this registry."""
        return content_hash(self.to_dict())


def default_source_kinds() -> tuple[SourceKindDeclaration, ...]:
    """The source kinds the framework ships knowing about — not the kinds it can learn."""
    return (
        SourceKindDeclaration(
            KIND_CONVERSATION_EXPORT,
            "An assistant conversation export (ChatGPT, Claude, or equivalent).",
            structured=True,
        ),
        SourceKindDeclaration(KIND_CHAT_TRANSCRIPT, "A linear chat transcript.", structured=True),
        SourceKindDeclaration(KIND_MARKDOWN, "A markdown document."),
        SourceKindDeclaration(KIND_PLAIN_TEXT, "A plain-text document."),
        SourceKindDeclaration(KIND_STRUCTURED_JSON, "A structured JSON document.", structured=True),
        SourceKindDeclaration(KIND_DOCUMENT_DOCX, "An Office Open XML word document.", binary=True),
        SourceKindDeclaration(KIND_DOCUMENT_PDF, "A PDF document.", binary=True),
        SourceKindDeclaration(
            KIND_SPREADSHEET_CSV, "A delimiter-separated table.", structured=True
        ),
        SourceKindDeclaration(KIND_REPOSITORY, "A repository working tree.", structured=True),
        SourceKindDeclaration(KIND_GIT_HISTORY, "A version-control history.", structured=True),
        SourceKindDeclaration(KIND_API_RESPONSE, "An API response payload.", structured=True),
        SourceKindDeclaration(KIND_DATABASE_RECORD, "A database record set.", structured=True),
        SourceKindDeclaration(KIND_EMAIL_MESSAGE, "An email message.", structured=True),
        SourceKindDeclaration(KIND_UNKNOWN, "A source whose kind has not been declared."),
    )


def default_source_kind_registry() -> SourceKindRegistry:
    """A registry seeded with the shipped declarations, open to further declaration."""
    return SourceKindRegistry(default_source_kinds())


@dataclass(frozen=True, slots=True)
class SourceRef:
    """An immutable, content-addressed reference to one admitted source."""

    kind: str
    locator: str
    content_sha256: str = ""
    byte_size: int = 0
    revision: str = ""
    source_id: str = ""

    @classmethod
    def create(
        cls,
        kind: str,
        locator: str,
        *,
        content_sha256: str = "",
        byte_size: int = 0,
        revision: str = "",
    ) -> SourceRef:
        """Build a validated source reference with a content-addressed identity."""
        if not isinstance(kind, str) or not kind.strip():
            raise AssimilationContractError("source requires a kind")
        normalized = normalize_locator(locator)
        if not normalized:
            raise AssimilationContractError("source requires a locator", kind=kind)
        core = {
            "kind": kind.strip(),
            "locator": normalized,
            "content_sha256": content_sha256,
        }
        return cls(
            kind=kind.strip(),
            locator=normalized,
            content_sha256=content_sha256,
            byte_size=int(byte_size),
            revision=revision,
            source_id=f"UCOS-USAS-{content_hash(core)[:16]}",
        )

    @classmethod
    def from_payload(
        cls, kind: str, locator: str, payload: bytes, *, revision: str = ""
    ) -> SourceRef:
        """Build a source reference by digesting its raw payload."""
        return cls.create(
            kind,
            locator,
            content_sha256=payload_digest(payload),
            byte_size=len(payload),
            revision=revision,
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this source reference."""
        return {
            "source_id": self.source_id,
            "kind": self.kind,
            "locator": self.locator,
            "content_sha256": self.content_sha256,
            "byte_size": self.byte_size,
            "revision": self.revision,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this source reference."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class AssimilationUnit:
    """One normalised, addressable piece of content extracted from a source."""

    source_id: str
    key: str
    text: str
    title: str = ""
    sequence: int = 0
    attributes: tuple[tuple[str, str], ...] = ()
    unit_id: str = ""

    @classmethod
    def create(
        cls,
        source_id: str,
        key: str,
        text: str,
        *,
        title: str = "",
        sequence: int = 0,
        attributes: Mapping[str, str] | None = None,
    ) -> AssimilationUnit:
        """Build a validated, whitespace-normalised unit with a content-addressed identity."""
        if not isinstance(source_id, str) or not source_id.strip():
            raise AssimilationContractError("unit requires a source_id")
        if not isinstance(key, str) or not key.strip():
            raise AssimilationContractError("unit requires a key", source_id=source_id)
        normalized = normalize_text(text)
        if not normalized:
            raise AssimilationContractError(
                "unit requires non-empty content", source_id=source_id, key=key
            )
        attrs = tuple(sorted((str(k), str(v)) for k, v in dict(attributes or {}).items()))
        core = {"source_id": source_id, "key": key.strip(), "text": normalized}
        return cls(
            source_id=source_id,
            key=key.strip(),
            text=normalized,
            title=title.strip(),
            sequence=int(sequence),
            attributes=attrs,
            unit_id=f"UCOS-USAU-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this unit."""
        return {
            "unit_id": self.unit_id,
            "source_id": self.source_id,
            "key": self.key,
            "title": self.title,
            "sequence": self.sequence,
            "text_length": len(self.text),
            "text_digest": content_hash({"text": self.text}),
            "attributes": {key: value for key, value in self.attributes},
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this unit."""
        return content_hash(self.to_dict())


class AssimilationState(str, Enum):
    """The closed, total state machine of assimilation."""

    DISCOVERED = "discovered"
    ADMITTED = "admitted"
    NORMALIZED = "normalized"
    ASSIMILATED = "assimilated"
    DEFERRED = "deferred"
    REJECTED = "rejected"

    @property
    def terminal(self) -> bool:
        """Whether no further transition is possible from this state."""
        return self in (
            AssimilationState.ASSIMILATED,
            AssimilationState.DEFERRED,
            AssimilationState.REJECTED,
        )


#: Why a source stopped short of assimilation (a closed vocabulary — never blank).
REASON_NO_ADAPTER = "NO-ADAPTER-FOR-SOURCE-KIND"
REASON_NO_EXTRACTABLE_CONTENT = "NO-EXTRACTABLE-CONTENT"
REASON_TRANSIENT_SOURCE = "TRANSIENT-SOURCE-NOT-TRUTH"
REASON_NO_DECLARED_DESTINATION = "NO-DECLARED-CANONICAL-DESTINATION"
REASON_DESTINATION_NOT_HOME = "DESTINATION-NOT-CANONICAL-HOME"
REASON_UNCLASSIFIED_SOURCE = "SOURCE-NOT-CLASSIFIED-BY-TRUTH-POLICY"

#: Every reason the framework can give. An unnamed absence is a defect, not an option.
ASSIMILATION_REASONS: tuple[str, ...] = (
    REASON_NO_ADAPTER,
    REASON_NO_EXTRACTABLE_CONTENT,
    REASON_TRANSIENT_SOURCE,
    REASON_NO_DECLARED_DESTINATION,
    REASON_DESTINATION_NOT_HOME,
    REASON_UNCLASSIFIED_SOURCE,
)


@dataclass(frozen=True, slots=True)
class AssimilationRecord:
    """The terminal determination for exactly one source."""

    source: SourceRef
    state: AssimilationState
    adapter_id: str = ""
    unit_count: int = 0
    truth_class: TruthClass = TruthClass.UNCLASSIFIED
    destination: str = ""
    owner: str = ""
    reasons: tuple[str, ...] = ()
    unit_ids: tuple[str, ...] = ()
    record_id: str = ""

    @classmethod
    def create(
        cls,
        source: SourceRef,
        state: AssimilationState,
        *,
        adapter_id: str = "",
        truth_class: TruthClass | str = TruthClass.UNCLASSIFIED,
        destination: str = "",
        owner: str = "",
        reasons: Iterable[str] = (),
        units: Iterable[AssimilationUnit] = (),
    ) -> AssimilationRecord:
        """Build a validated record; a non-assimilated source must name its reason."""
        if not isinstance(source, SourceRef):
            raise AssimilationContractError("record requires a SourceRef")
        if not isinstance(state, AssimilationState):
            raise AssimilationContractError("record requires an AssimilationState")
        named = tuple(sorted({str(item) for item in reasons if str(item).strip()}))
        if state is not AssimilationState.ASSIMILATED and not named:
            raise AssimilationContractError(
                "a source that is not assimilated must name its reason",
                source_id=source.source_id,
                state=state.value,
            )
        if state is AssimilationState.ASSIMILATED and not destination:
            raise AssimilationContractError(
                "an assimilated source must name its canonical destination",
                source_id=source.source_id,
            )
        unit_ids = tuple(sorted({unit.unit_id for unit in units}))
        resolved = TruthClass.coerce(truth_class, context=source.locator)
        core = {
            "source_id": source.source_id,
            "state": state.value,
            "destination": normalize_locator(destination) if destination else "",
            "reasons": list(named),
        }
        return cls(
            source=source,
            state=state,
            adapter_id=adapter_id,
            unit_count=len(unit_ids),
            truth_class=resolved,
            destination=normalize_locator(destination) if destination else "",
            owner=owner,
            reasons=named,
            unit_ids=unit_ids,
            record_id=f"UCOS-USAR-{content_hash(core)[:16]}",
        )

    @property
    def assimilated(self) -> bool:
        """Whether this source reached a declared canonical destination."""
        return self.state is AssimilationState.ASSIMILATED

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this record."""
        return {
            "record_id": self.record_id,
            "source": self.source.to_dict(),
            "state": self.state.value,
            "adapter_id": self.adapter_id,
            "unit_count": self.unit_count,
            "truth_class": self.truth_class.value,
            "destination": self.destination,
            "owner": self.owner,
            "reasons": list(self.reasons),
            "unit_ids": list(self.unit_ids),
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this record."""
        return content_hash(self.to_dict())


def _percent(part: int, whole: int) -> float:
    """A deterministic percentage; ``0.0`` when the population is empty."""
    if whole <= 0:
        return 0.0
    return round((part / whole) * 100, 4)


@dataclass(frozen=True, slots=True)
class AssimilationReport:
    """The immutable determination of assimilation over a whole source population."""

    records: tuple[AssimilationRecord, ...]
    report_id: str = ""

    @classmethod
    def create(cls, records: Iterable[AssimilationRecord]) -> AssimilationReport:
        """Build a deterministic report, ordered by source identity."""
        ordered = tuple(sorted(records, key=lambda item: (item.source.locator, item.record_id)))
        core = {"records": [record.record_id for record in ordered]}
        return cls(records=ordered, report_id=f"UCOS-USAP-{content_hash(core)[:16]}")

    @property
    def total(self) -> int:
        """The size of the source population."""
        return len(self.records)

    def of_state(self, state: AssimilationState) -> tuple[AssimilationRecord, ...]:
        """Every record in ``state``."""
        return tuple(record for record in self.records if record.state is state)

    @property
    def assimilated(self) -> tuple[AssimilationRecord, ...]:
        """Every source that reached a declared canonical destination."""
        return self.of_state(AssimilationState.ASSIMILATED)

    def outstanding(self) -> tuple[AssimilationRecord, ...]:
        """Every source that has not been assimilated and was not rejected."""
        return tuple(
            record
            for record in self.records
            if record.state not in (AssimilationState.ASSIMILATED, AssimilationState.REJECTED)
        )

    def of_reason(self, reason: str) -> tuple[AssimilationRecord, ...]:
        """Every record carrying ``reason``."""
        return tuple(record for record in self.records if reason in record.reasons)

    @property
    def closed(self) -> bool:
        """Whether every admissible source has been assimilated."""
        return self.total > 0 and not self.outstanding()

    @property
    def coverage(self) -> float:
        """The percentage of the population that has been assimilated."""
        return _percent(len(self.assimilated), self.total)

    def counts_by_state(self) -> dict[str, int]:
        """Population counts by state (every state present, zeros included)."""
        tally = {state.value: 0 for state in AssimilationState}
        for record in self.records:
            tally[record.state.value] += 1
        return dict(sorted(tally.items()))

    def counts_by_kind(self) -> dict[str, int]:
        """Population counts by declared source kind."""
        tally: dict[str, int] = {}
        for record in self.records:
            tally[record.source.kind] = tally.get(record.source.kind, 0) + 1
        return dict(sorted(tally.items()))

    def counts_by_truth_class(self) -> dict[str, int]:
        """Population counts by the truth class of the source locator."""
        tally: dict[str, int] = {}
        for record in self.records:
            key = record.truth_class.value
            tally[key] = tally.get(key, 0) + 1
        return dict(sorted(tally.items()))

    def by_reason(self) -> dict[str, int]:
        """How many sources carry each named reason."""
        tally: dict[str, int] = {}
        for record in self.records:
            for reason in record.reasons:
                tally[reason] = tally.get(reason, 0) + 1
        return dict(sorted(tally.items()))

    @property
    def unit_total(self) -> int:
        """How many normalised units the population yielded."""
        return sum(record.unit_count for record in self.records)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this report."""
        return {
            "report_id": self.report_id,
            "total": self.total,
            "unit_total": self.unit_total,
            "coverage_percentage": self.coverage,
            "closed": self.closed,
            "counts_by_state": self.counts_by_state(),
            "counts_by_kind": self.counts_by_kind(),
            "counts_by_truth_class": self.counts_by_truth_class(),
            "by_reason": self.by_reason(),
            "outstanding": [record.source.locator for record in self.outstanding()],
            "records": [record.to_dict() for record in self.records],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this report."""
        return content_hash(self.to_dict())


_ASSIMILATION_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("assimilation.kinds.declare", "Declare a source kind into the open taxonomy."),
    ("assimilation.adapter.normalize", "Normalise any source into addressable units."),
    ("assimilation.pipeline.assimilate", "Assimilate a source population through one framework."),
    ("assimilation.report.project", "Project the deterministic assimilation determination."),
)

#: The versioned published contract surface of the Source Assimilation Framework.
ASSIMILATION_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, ASSIMILATION_CONTRACT_VERSION) for name, _ in _ASSIMILATION_CONTRACT_NAMES
)


def assimilation_contract_names() -> tuple[str, ...]:
    """The published assimilation contract names, in declaration order."""
    return tuple(name for name, _ in _ASSIMILATION_CONTRACT_NAMES)


__all__ = [
    "USAF_ID",
    "ASSIMILATION_CONTRACT_VERSION",
    "KIND_CONVERSATION_EXPORT",
    "KIND_CHAT_TRANSCRIPT",
    "KIND_MARKDOWN",
    "KIND_PLAIN_TEXT",
    "KIND_STRUCTURED_JSON",
    "KIND_DOCUMENT_DOCX",
    "KIND_DOCUMENT_PDF",
    "KIND_SPREADSHEET_CSV",
    "KIND_REPOSITORY",
    "KIND_GIT_HISTORY",
    "KIND_API_RESPONSE",
    "KIND_DATABASE_RECORD",
    "KIND_EMAIL_MESSAGE",
    "KIND_UNKNOWN",
    "normalize_text",
    "payload_digest",
    "SourceKindDeclaration",
    "SourceKindRegistry",
    "default_source_kinds",
    "default_source_kind_registry",
    "SourceRef",
    "AssimilationUnit",
    "AssimilationState",
    "ASSIMILATION_REASONS",
    "REASON_NO_ADAPTER",
    "REASON_NO_EXTRACTABLE_CONTENT",
    "REASON_TRANSIENT_SOURCE",
    "REASON_NO_DECLARED_DESTINATION",
    "REASON_DESTINATION_NOT_HOME",
    "REASON_UNCLASSIFIED_SOURCE",
    "AssimilationRecord",
    "AssimilationReport",
    "ASSIMILATION_CONTRACTS",
    "assimilation_contract_names",
]
