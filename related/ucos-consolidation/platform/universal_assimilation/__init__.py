"""UCOS Ω∞ — Universal Source Assimilation Framework (``platform.universal_assimilation``).

**UCOS-USAF-001.** The reusable Foundation capability through which *every* source is
assimilated by one framework: ChatGPT and Claude conversation exports, markdown, DOCX, PDF,
repositories, git history, API responses, database record sets, email — and sources nobody has
invented yet, which are added by **declaration** (an open source-kind registry plus one
adapter) rather than by another bespoke ingestion engine.

The framework is deliberately narrow about what it decides. Adapters normalise bytes into
addressable units; Repository Truth policy classifies the source and its destination;
ownership is determined elsewhere. What the pipeline contributes is the honest terminal
state of every source, from a closed vocabulary:

    ASSIMILATED · NORMALIZED · ADMITTED · DEFERRED · REJECTED

with a named reason whenever a source stopped short. Content is never fabricated: a PDF whose
text cannot be recovered yields no units and an honest ``NO-EXTRACTABLE-CONTENT``, and a source
with no declared canonical destination is reported as such rather than counted as assimilated.

Payload acquisition belongs to the caller — the framework never scans a filesystem, opens a
network connection, or rediscovers a repository as a side effect of assimilating one file.
"""

from __future__ import annotations

from platform.universal_assimilation.adapters import (
    CallableAdapter,
    ConversationExportAdapter,
    DocxAdapter,
    JsonAdapter,
    PdfAdapter,
    RecordSetAdapter,
    SourceAdapter,
    SourceAdapterDescriptor,
    SourceAdapterRegistry,
    TextAdapter,
    default_adapter_registry,
    default_source_adapters,
)
from platform.universal_assimilation.bootstrap import (
    ASSIMILATION_SERVICE_NAME,
    assimilation_service_descriptor,
    bootstrap_assimilation,
    register_assimilation,
)
from platform.universal_assimilation.contracts import (
    ASSIMILATION_CONTRACT_VERSION,
    ASSIMILATION_CONTRACTS,
    ASSIMILATION_REASONS,
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
    KIND_SPREADSHEET_CSV,
    KIND_STRUCTURED_JSON,
    KIND_UNKNOWN,
    REASON_DESTINATION_NOT_HOME,
    REASON_NO_ADAPTER,
    REASON_NO_DECLARED_DESTINATION,
    REASON_NO_EXTRACTABLE_CONTENT,
    REASON_TRANSIENT_SOURCE,
    REASON_UNCLASSIFIED_SOURCE,
    USAF_ID,
    AssimilationRecord,
    AssimilationReport,
    AssimilationState,
    AssimilationUnit,
    SourceKindDeclaration,
    SourceKindRegistry,
    SourceRef,
    assimilation_contract_names,
    default_source_kind_registry,
    default_source_kinds,
    normalize_text,
    payload_digest,
)
from platform.universal_assimilation.errors import (
    AdapterConflictError,
    AssimilationContractError,
    AssimilationError,
    AssimilationPipelineError,
    SourceAdapterError,
    SourceKindError,
)
from platform.universal_assimilation.pipeline import (
    AssimilationOutcome,
    AssimilationPipeline,
    SourceInput,
)

__all__ = [
    "USAF_ID",
    "ASSIMILATION_CONTRACT_VERSION",
    "ASSIMILATION_CONTRACTS",
    "assimilation_contract_names",
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
    "SourceInput",
    "AssimilationOutcome",
    "AssimilationPipeline",
    "ASSIMILATION_SERVICE_NAME",
    "bootstrap_assimilation",
    "assimilation_service_descriptor",
    "register_assimilation",
    "AssimilationError",
    "AssimilationContractError",
    "SourceKindError",
    "SourceAdapterError",
    "AdapterConflictError",
    "AssimilationPipelineError",
]
