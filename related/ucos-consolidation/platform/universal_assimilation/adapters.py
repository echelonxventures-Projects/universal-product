"""UCOS-USAF-001 — Source adapters: one framework, every source.

An adapter's only job is to turn *bytes of a declared kind* into normalised
:class:`~platform.universal_assimilation.contracts.AssimilationUnit` values. It decides
nothing about Truth, ownership, or destination — which is precisely why one pipeline can
serve conversation exports, DOCX, PDF, repositories, git history, APIs, databases, email and
whatever arrives next.

Shipped adapters:

    * :class:`TextAdapter` — markdown and plain text (markdown splits on ATX headings).
    * :class:`JsonAdapter` — structured JSON documents.
    * :class:`ConversationExportAdapter` — assistant conversation exports, recognised by
      **payload structure, never by filename**: ChatGPT ``mapping``/``message`` graphs,
      Claude ``chat_messages``, and the generic ``messages`` form.
    * :class:`DocxAdapter` — Office Open XML, paragraph by paragraph.
    * :class:`PdfAdapter` — PDF text operators from Flate-decoded content streams; a PDF whose
      text cannot be honestly extracted yields **no** units rather than invented content.
    * :class:`RecordSetAdapter` — the declared-schema adapter through which repositories, git
      history, API responses, database rows and email are assimilated without any adapter
      needing network or driver access: a connector supplies records, the schema is declared.
    * :class:`CallableAdapter` — the seam for a source nobody has thought of yet.

Adapters never read the filesystem or the network themselves: payload acquisition is the
caller's business, so the framework never rediscovers a repository as a side effect of
assimilating one file.
"""

from __future__ import annotations

import io
import json
import re
import zipfile
import zlib
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_assimilation.contracts import (
    KIND_API_RESPONSE,
    KIND_CHAT_TRANSCRIPT,
    KIND_CONVERSATION_EXPORT,
    KIND_DATABASE_RECORD,
    KIND_DOCUMENT_DOCX,
    KIND_DOCUMENT_PDF,
    KIND_EMAIL_MESSAGE,
    KIND_GIT_HISTORY,
    KIND_MARKDOWN,
    KIND_PLAIN_TEXT,
    KIND_REPOSITORY,
    KIND_STRUCTURED_JSON,
    AssimilationUnit,
    SourceRef,
    normalize_text,
)
from platform.universal_assimilation.errors import (
    AdapterConflictError,
    SourceAdapterError,
)
from typing import Any

#: The default adapter precedence. Higher wins when several adapters accept a source.
DEFAULT_PRECEDENCE = 100

#: The maximum payload an adapter will decode, so a pathological source cannot stall a run.
MAX_PAYLOAD_BYTES = 64 * 1024 * 1024

_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_XML_TAG = re.compile(r"<[^>]+>")
_DOCX_PARAGRAPH = re.compile(r"<w:p(?:\s[^>]*)?/>|<w:p(?:\s[^>]*)?>.*?</w:p>", re.DOTALL)
_PDF_STREAM = re.compile(rb"stream\r?\n(.*?)endstream", re.DOTALL)
_PDF_TEXT = re.compile(rb"\((?:\\.|[^\\()])*\)")


def _decode(payload: bytes) -> str:
    """Decode a payload as text, tolerantly but deterministically."""
    if not isinstance(payload, bytes | bytearray):
        raise SourceAdapterError("payload must be bytes")
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise SourceAdapterError("payload exceeds the decodable limit", byte_size=len(payload))
    return bytes(payload).decode("utf-8", errors="replace")


def _load_json(payload: bytes) -> Any:
    """Parse a JSON payload (fail-closed)."""
    try:
        return json.loads(_decode(payload))
    except json.JSONDecodeError as exc:
        raise SourceAdapterError("payload is not valid JSON", detail=str(exc)) from exc


@dataclass(frozen=True, slots=True)
class SourceAdapterDescriptor:
    """How an adapter identifies itself and which declared kinds it can normalise."""

    adapter_id: str
    kinds: tuple[str, ...]
    precedence: int = DEFAULT_PRECEDENCE
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.adapter_id, str) or not self.adapter_id.strip():
            raise SourceAdapterError("adapter_id must be a non-empty string")
        if not self.kinds:
            raise SourceAdapterError("adapter declares no source kinds", adapter_id=self.adapter_id)
        if not isinstance(self.precedence, int) or isinstance(self.precedence, bool):
            raise SourceAdapterError(
                "adapter precedence must be an int", adapter_id=self.adapter_id
            )

    @property
    def order_key(self) -> tuple[int, str]:
        """Deterministic adapter order: highest precedence first, then identity."""
        return (-self.precedence, self.adapter_id)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this descriptor."""
        return {
            "adapter_id": self.adapter_id,
            "kinds": list(self.kinds),
            "precedence": self.precedence,
            "description": self.description,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this descriptor."""
        return content_hash(self.to_dict())


class SourceAdapter(ABC):
    """The one extension point through which every source becomes normalised units."""

    @abstractmethod
    def descriptor(self) -> SourceAdapterDescriptor:
        """Describe this adapter's identity, declared kinds and precedence."""
        raise NotImplementedError  # pragma: no cover - abstract

    @abstractmethod
    def extract(self, source: SourceRef, payload: bytes) -> Iterable[AssimilationUnit]:
        """Normalise ``payload`` into addressable units for ``source``."""
        raise NotImplementedError  # pragma: no cover - abstract

    def supports(self, source: SourceRef) -> bool:
        """Whether this adapter declares the kind of ``source``."""
        return source.kind in self.descriptor().kinds

    def units(self, source: SourceRef, payload: bytes) -> tuple[AssimilationUnit, ...]:
        """Protocol enforcement: contain faults, verify provenance, order deterministically."""
        if not isinstance(source, SourceRef):
            raise SourceAdapterError("normalisation requires a SourceRef")
        descriptor = self.descriptor()
        if not self.supports(source):
            raise SourceAdapterError(
                "adapter does not declare this source kind",
                adapter_id=descriptor.adapter_id,
                kind=source.kind,
            )
        try:
            produced = tuple(self.extract(source, payload))
        except SourceAdapterError:
            raise
        except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
            raise SourceAdapterError(
                "source adapter failed",
                adapter_id=descriptor.adapter_id,
                locator=source.locator,
                detail=str(exc),
            ) from exc
        for unit in produced:
            if not isinstance(unit, AssimilationUnit):
                raise SourceAdapterError(
                    "adapter produced a non-unit value", adapter_id=descriptor.adapter_id
                )
            if unit.source_id != source.source_id:
                raise SourceAdapterError(
                    "unit provenance does not match its source",
                    adapter_id=descriptor.adapter_id,
                    locator=source.locator,
                )
        unique = {unit.unit_id: unit for unit in produced}
        return tuple(sorted(unique.values(), key=lambda unit: (unit.sequence, unit.key)))


class TextAdapter(SourceAdapter):
    """Markdown and plain text. Markdown splits on ATX headings; text yields one unit."""

    __slots__ = ("_descriptor",)

    def __init__(
        self,
        *,
        adapter_id: str = "assimilation.text",
        kinds: Sequence[str] = (KIND_MARKDOWN, KIND_PLAIN_TEXT),
        precedence: int = DEFAULT_PRECEDENCE,
    ) -> None:
        self._descriptor = SourceAdapterDescriptor(
            adapter_id=adapter_id,
            kinds=tuple(kinds),
            precedence=precedence,
            description="Markdown (heading-addressed) and plain-text documents.",
        )

    def descriptor(self) -> SourceAdapterDescriptor:
        """Describe this adapter."""
        return self._descriptor

    def extract(self, source: SourceRef, payload: bytes) -> Iterable[AssimilationUnit]:
        """Split markdown on headings; emit plain text as a single unit."""
        text = _decode(payload)
        if source.kind != KIND_MARKDOWN:
            body = normalize_text(text)
            if not body:
                return ()
            return (
                AssimilationUnit.create(
                    source.source_id, source.locator, body, title=source.locator
                ),
            )
        units: list[AssimilationUnit] = []
        heading = ""
        buffer: list[str] = []
        sequence = 0

        def flush() -> None:
            nonlocal sequence, buffer
            body = normalize_text(" ".join(buffer))
            if body:
                units.append(
                    AssimilationUnit.create(
                        source.source_id,
                        f"{source.locator}#{heading or 'preamble'}",
                        body,
                        title=heading,
                        sequence=sequence,
                    )
                )
                sequence += 1
            buffer = []

        for line in text.splitlines():
            match = _HEADING.match(line)
            if match:
                flush()
                heading = match.group(2)
                continue
            buffer.append(line)
        flush()
        return tuple(units)


class JsonAdapter(SourceAdapter):
    """Structured JSON: one unit per top-level member, addressed by its key or index."""

    __slots__ = ("_descriptor",)

    def __init__(
        self,
        *,
        adapter_id: str = "assimilation.json",
        kinds: Sequence[str] = (KIND_STRUCTURED_JSON,),
        precedence: int = DEFAULT_PRECEDENCE,
    ) -> None:
        self._descriptor = SourceAdapterDescriptor(
            adapter_id=adapter_id,
            kinds=tuple(kinds),
            precedence=precedence,
            description="Structured JSON documents addressed by top-level member.",
        )

    def descriptor(self) -> SourceAdapterDescriptor:
        """Describe this adapter."""
        return self._descriptor

    def extract(self, source: SourceRef, payload: bytes) -> Iterable[AssimilationUnit]:
        """Emit one unit per top-level member of the document."""
        document = _load_json(payload)
        members: list[tuple[str, Any]]
        if isinstance(document, Mapping):
            members = [(str(key), document[key]) for key in sorted(document)]
        elif isinstance(document, Sequence) and not isinstance(document, str | bytes):
            members = [(str(index), value) for index, value in enumerate(document)]
        else:
            members = [("value", document)]
        units: list[AssimilationUnit] = []
        for sequence, (key, value) in enumerate(members):
            body = normalize_text(json.dumps(value, sort_keys=True, ensure_ascii=False))
            if not body:
                continue
            units.append(
                AssimilationUnit.create(
                    source.source_id,
                    f"{source.locator}#{key}",
                    body,
                    title=key,
                    sequence=sequence,
                )
            )
        return tuple(units)


class ConversationExportAdapter(SourceAdapter):
    """Assistant conversation exports, recognised by payload structure, never by filename.

    Handles the ChatGPT ``mapping`` node graph, the Claude ``chat_messages`` form, and the
    generic ``messages`` form — one unit per message, with role and conversation recorded as
    attributes so provenance survives normalisation.
    """

    __slots__ = ("_descriptor",)

    def __init__(
        self,
        *,
        adapter_id: str = "assimilation.conversation-export",
        kinds: Sequence[str] = (KIND_CONVERSATION_EXPORT, KIND_CHAT_TRANSCRIPT),
        precedence: int = 500,
    ) -> None:
        self._descriptor = SourceAdapterDescriptor(
            adapter_id=adapter_id,
            kinds=tuple(kinds),
            precedence=precedence,
            description="Assistant conversation exports (ChatGPT, Claude, generic).",
        )

    def descriptor(self) -> SourceAdapterDescriptor:
        """Describe this adapter."""
        return self._descriptor

    @staticmethod
    def _content_text(content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, Mapping):
            if "parts" in content:
                return " ".join(
                    ConversationExportAdapter._content_text(part)
                    for part in content.get("parts") or ()
                )
            for key in ("text", "value", "content", "body"):
                if key in content:
                    return ConversationExportAdapter._content_text(content[key])
            return ""
        if isinstance(content, Sequence) and not isinstance(content, str | bytes):
            return " ".join(ConversationExportAdapter._content_text(item) for item in content)
        return str(content)

    @classmethod
    def _messages(cls, conversation: Mapping[str, Any]) -> list[tuple[str, str, str]]:
        """``(key, role, text)`` triples for one conversation, in a stable order."""
        found: list[tuple[str, str, str]] = []
        mapping = conversation.get("mapping")
        if isinstance(mapping, Mapping):
            for node_id in sorted(mapping):
                node = mapping[node_id]
                if not isinstance(node, Mapping):
                    continue
                message = node.get("message")
                if not isinstance(message, Mapping):
                    continue
                author = message.get("author")
                role = (
                    str(author.get("role", ""))
                    if isinstance(author, Mapping)
                    else str(message.get("role", ""))
                )
                found.append((str(node_id), role, cls._content_text(message.get("content"))))
            return found
        for key in ("chat_messages", "messages", "conversation"):
            block = conversation.get(key)
            if isinstance(block, Sequence) and not isinstance(block, str | bytes):
                for index, message in enumerate(block):
                    if not isinstance(message, Mapping):
                        continue
                    role = str(
                        message.get("role") or message.get("sender") or message.get("author") or ""
                    )
                    text = cls._content_text(
                        message.get("content") if "content" in message else message.get("text")
                    )
                    found.append((f"{key}.{index:06d}", role, text))
                return found
        return found

    @staticmethod
    def _conversations(document: Any) -> list[tuple[str, Mapping[str, Any]]]:
        if isinstance(document, Mapping):
            for key in ("conversations", "chats", "threads"):
                block = document.get(key)
                if isinstance(block, Sequence) and not isinstance(block, str | bytes):
                    return [
                        (str(item.get("id") or item.get("uuid") or index), item)
                        for index, item in enumerate(block)
                        if isinstance(item, Mapping)
                    ]
            return [(str(document.get("id") or document.get("uuid") or "conversation"), document)]
        if isinstance(document, Sequence) and not isinstance(document, str | bytes):
            return [
                (str(item.get("id") or item.get("uuid") or index), item)
                for index, item in enumerate(document)
                if isinstance(item, Mapping)
            ]
        return []

    def extract(self, source: SourceRef, payload: bytes) -> Iterable[AssimilationUnit]:
        """Emit one unit per message across every conversation in the export."""
        document = _load_json(payload)
        units: list[AssimilationUnit] = []
        sequence = 0
        for conversation_id, conversation in self._conversations(document):
            title = str(conversation.get("title", "") or "")
            for key, role, text in self._messages(conversation):
                body = normalize_text(text)
                if not body:
                    continue
                units.append(
                    AssimilationUnit.create(
                        source.source_id,
                        f"{source.locator}#{conversation_id}/{key}",
                        body,
                        title=title,
                        sequence=sequence,
                        attributes={"conversation": str(conversation_id), "role": role},
                    )
                )
                sequence += 1
        return tuple(units)


class DocxAdapter(SourceAdapter):
    """Office Open XML documents: one unit per non-empty paragraph."""

    __slots__ = ("_descriptor", "_member")

    def __init__(
        self,
        *,
        adapter_id: str = "assimilation.docx",
        kinds: Sequence[str] = (KIND_DOCUMENT_DOCX,),
        precedence: int = DEFAULT_PRECEDENCE,
        member: str = "word/document.xml",
    ) -> None:
        self._member = member
        self._descriptor = SourceAdapterDescriptor(
            adapter_id=adapter_id,
            kinds=tuple(kinds),
            precedence=precedence,
            description="Office Open XML word documents, paragraph addressed.",
        )

    def descriptor(self) -> SourceAdapterDescriptor:
        """Describe this adapter."""
        return self._descriptor

    def extract(self, source: SourceRef, payload: bytes) -> Iterable[AssimilationUnit]:
        """Emit one unit per paragraph of the document body."""
        try:
            with zipfile.ZipFile(io.BytesIO(bytes(payload))) as archive:
                xml = archive.read(self._member).decode("utf-8", errors="replace")
        except (KeyError, OSError, zipfile.BadZipFile) as exc:
            raise SourceAdapterError(
                "docx payload could not be opened",
                adapter_id=self._descriptor.adapter_id,
                locator=source.locator,
                detail=str(exc),
            ) from exc
        units: list[AssimilationUnit] = []
        sequence = 0
        for match in _DOCX_PARAGRAPH.finditer(xml):
            body = normalize_text(_XML_TAG.sub(" ", match.group(0)))
            if not body:
                continue
            units.append(
                AssimilationUnit.create(
                    source.source_id,
                    f"{source.locator}#p{sequence:06d}",
                    body,
                    sequence=sequence,
                )
            )
            sequence += 1
        return tuple(units)


class PdfAdapter(SourceAdapter):
    """PDF documents: text operators from Flate-decoded content streams.

    A PDF whose text cannot be honestly recovered (scanned images, unsupported filters)
    yields **zero** units. The pipeline then records ``NO-EXTRACTABLE-CONTENT`` — an honest
    deferral is always preferable to fabricated content.
    """

    __slots__ = ("_descriptor",)

    def __init__(
        self,
        *,
        adapter_id: str = "assimilation.pdf",
        kinds: Sequence[str] = (KIND_DOCUMENT_PDF,),
        precedence: int = DEFAULT_PRECEDENCE,
    ) -> None:
        self._descriptor = SourceAdapterDescriptor(
            adapter_id=adapter_id,
            kinds=tuple(kinds),
            precedence=precedence,
            description="PDF documents, content-stream text operators.",
        )

    def descriptor(self) -> SourceAdapterDescriptor:
        """Describe this adapter."""
        return self._descriptor

    @staticmethod
    def _stream_text(raw: bytes) -> str:
        try:
            data = zlib.decompress(raw)
        except zlib.error:
            data = raw
        pieces: list[str] = []
        for match in _PDF_TEXT.finditer(data):
            literal = match.group(0)[1:-1]
            literal = literal.replace(b"\\(", b"(").replace(b"\\)", b")")
            literal = literal.replace(b"\\\\", b"\\")
            pieces.append(literal.decode("utf-8", errors="replace"))
        return " ".join(pieces)

    def extract(self, source: SourceRef, payload: bytes) -> Iterable[AssimilationUnit]:
        """Emit one unit per content stream that yielded recoverable text."""
        data = bytes(payload)
        if len(data) > MAX_PAYLOAD_BYTES:
            raise SourceAdapterError("pdf payload exceeds the decodable limit", byte_size=len(data))
        units: list[AssimilationUnit] = []
        sequence = 0
        for match in _PDF_STREAM.finditer(data):
            body = normalize_text(self._stream_text(match.group(1)))
            if not body:
                continue
            units.append(
                AssimilationUnit.create(
                    source.source_id,
                    f"{source.locator}#s{sequence:06d}",
                    body,
                    sequence=sequence,
                    attributes={"extraction": "content-stream"},
                )
            )
            sequence += 1
        return tuple(units)


class RecordSetAdapter(SourceAdapter):
    """The declared-schema adapter for record-shaped sources.

    Repositories, git histories, API responses, database result sets and email all arrive as
    *records*. A connector supplies the records as JSON; this adapter declares which field
    is the identity and which fields carry the text. That is how the framework assimilates
    those sources without any adapter needing filesystem, network or driver access — and how
    a future record-shaped source is supported by declaration alone.
    """

    __slots__ = ("_descriptor", "_collection", "_identity_field", "_text_fields")

    def __init__(
        self,
        *,
        adapter_id: str = "assimilation.record-set",
        kinds: Sequence[str] = (
            KIND_REPOSITORY,
            KIND_GIT_HISTORY,
            KIND_API_RESPONSE,
            KIND_DATABASE_RECORD,
            KIND_EMAIL_MESSAGE,
        ),
        precedence: int = DEFAULT_PRECEDENCE,
        collection: str = "records",
        identity_field: str = "id",
        text_fields: Sequence[str] = ("text", "body", "content", "message", "summary"),
    ) -> None:
        self._collection = collection
        self._identity_field = identity_field
        self._text_fields = tuple(text_fields)
        self._descriptor = SourceAdapterDescriptor(
            adapter_id=adapter_id,
            kinds=tuple(kinds),
            precedence=precedence,
            description="Record-shaped sources normalised by declared schema.",
        )

    def descriptor(self) -> SourceAdapterDescriptor:
        """Describe this adapter."""
        return self._descriptor

    def extract(self, source: SourceRef, payload: bytes) -> Iterable[AssimilationUnit]:
        """Emit one unit per record, addressed by its declared identity field."""
        document = _load_json(payload)
        if isinstance(document, Mapping):
            records = document.get(self._collection, ())
        else:
            records = document
        if not isinstance(records, Sequence) or isinstance(records, str | bytes):
            raise SourceAdapterError(
                "record-set payload declares no record sequence",
                adapter_id=self._descriptor.adapter_id,
                collection=self._collection,
            )
        units: list[AssimilationUnit] = []
        for sequence, record in enumerate(records):
            if not isinstance(record, Mapping):
                continue
            identity = str(record.get(self._identity_field, sequence))
            texts = [
                str(record[field])
                for field in self._text_fields
                if field in record and record[field] is not None
            ]
            body = normalize_text(" ".join(texts))
            if not body:
                continue
            units.append(
                AssimilationUnit.create(
                    source.source_id,
                    f"{source.locator}#{identity}",
                    body,
                    title=str(record.get("title", "")),
                    sequence=sequence,
                    attributes={"record_identity": identity},
                )
            )
        return tuple(units)


class CallableAdapter(SourceAdapter):
    """Wraps any callable as a source adapter — the seam for future sources."""

    __slots__ = ("_descriptor", "_extractor")

    def __init__(
        self,
        descriptor: SourceAdapterDescriptor,
        extractor: Callable[[SourceRef, bytes], Iterable[AssimilationUnit]],
    ) -> None:
        if not isinstance(descriptor, SourceAdapterDescriptor):
            raise SourceAdapterError("callable adapter requires a descriptor")
        if not callable(extractor):
            raise SourceAdapterError(
                "callable adapter requires a callable", adapter_id=descriptor.adapter_id
            )
        self._descriptor = descriptor
        self._extractor = extractor

    def descriptor(self) -> SourceAdapterDescriptor:
        """Describe this adapter."""
        return self._descriptor

    def extract(self, source: SourceRef, payload: bytes) -> Iterable[AssimilationUnit]:
        """Delegate to the wrapped extractor."""
        return self._extractor(source, payload)


class SourceAdapterRegistry:
    """A deterministic, fail-closed registry of source adapters."""

    __slots__ = ("_adapters",)

    def __init__(self, adapters: Iterable[SourceAdapter] = ()) -> None:
        self._adapters: dict[str, SourceAdapter] = {}
        self.extend(adapters)

    def add(self, adapter: SourceAdapter) -> SourceAdapter:
        """Register ``adapter``; idempotent by object, fail-closed on identity collision."""
        if not isinstance(adapter, SourceAdapter):
            raise SourceAdapterError("registry accepts only SourceAdapter values")
        descriptor = adapter.descriptor()
        existing = self._adapters.get(descriptor.adapter_id)
        if existing is not None:
            if existing is adapter:
                return existing
            raise AdapterConflictError(
                "adapter identity already registered", adapter_id=descriptor.adapter_id
            )
        self._adapters[descriptor.adapter_id] = adapter
        return adapter

    def extend(self, adapters: Iterable[SourceAdapter]) -> tuple[SourceAdapter, ...]:
        """Register every adapter in ``adapters``, returning them in resolution order."""
        for adapter in adapters:
            self.add(adapter)
        return self.ordered()

    def get(self, adapter_id: str) -> SourceAdapter | None:
        """The registered adapter ``adapter_id``, or ``None``."""
        return self._adapters.get(adapter_id)

    def require(self, adapter_id: str) -> SourceAdapter:
        """The registered adapter ``adapter_id`` (fail-closed)."""
        adapter = self.get(adapter_id)
        if adapter is None:
            raise SourceAdapterError("unknown source adapter", adapter_id=adapter_id)
        return adapter

    @property
    def count(self) -> int:
        """How many adapters are registered."""
        return len(self._adapters)

    def ordered(self) -> tuple[SourceAdapter, ...]:
        """Every adapter in declared precedence order — never insertion order."""
        return tuple(sorted(self._adapters.values(), key=lambda item: item.descriptor().order_key))

    def descriptors(self) -> tuple[SourceAdapterDescriptor, ...]:
        """Every adapter descriptor in resolution order."""
        return tuple(adapter.descriptor() for adapter in self.ordered())

    def kinds(self) -> tuple[str, ...]:
        """Every source kind some registered adapter can normalise."""
        found: set[str] = set()
        for descriptor in self.descriptors():
            found.update(descriptor.kinds)
        return tuple(sorted(found))

    def for_source(self, source: SourceRef) -> SourceAdapter | None:
        """The highest-precedence adapter that declares the kind of ``source``."""
        for adapter in self.ordered():
            if adapter.supports(source):
                return adapter
        return None

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this registry."""
        return {
            "adapter_count": self.count,
            "kinds": list(self.kinds()),
            "adapters": [descriptor.to_dict() for descriptor in self.descriptors()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this registry."""
        return content_hash(self.to_dict())


def default_source_adapters() -> tuple[SourceAdapter, ...]:
    """The adapters the framework ships with — extend the registry, never fork it."""
    return (
        TextAdapter(),
        JsonAdapter(),
        ConversationExportAdapter(),
        DocxAdapter(),
        PdfAdapter(),
        RecordSetAdapter(),
    )


def default_adapter_registry() -> SourceAdapterRegistry:
    """A registry seeded with the shipped adapters."""
    return SourceAdapterRegistry(default_source_adapters())


__all__ = [
    "DEFAULT_PRECEDENCE",
    "MAX_PAYLOAD_BYTES",
    "SourceAdapterDescriptor",
    "SourceAdapter",
    "TextAdapter",
    "JsonAdapter",
    "ConversationExportAdapter",
    "DocxAdapter",
    "PdfAdapter",
    "RecordSetAdapter",
    "CallableAdapter",
    "SourceAdapterRegistry",
    "default_source_adapters",
    "default_adapter_registry",
]
