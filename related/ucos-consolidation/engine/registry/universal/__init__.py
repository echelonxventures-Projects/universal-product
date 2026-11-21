"""UCOS-EPIC-001 — Universal Registry Platform (write-side registration authority).

The single registration authority for every artifact in UCOS Ω∞. Where the
EPIC-002 :mod:`engine.registry` adapter provides *read-only* access over the
certified ``00-BOOK`` corpus, this package provides the governed **write** path:
the authority through which an artifact becomes Repository Truth.

Constitutional requirements enforced (AB-001 architecture consumed, not redesigned;
EG-001 conformance):

    * Repository Truth only — records are append-only; nothing is overwritten.
    * Knowledge Once — one canonical home per unit of knowledge (content dedup).
    * No duplicate registrations — a ``(universal_id, version)`` is unique.
    * Deterministic IDs — identity is a pure function of ``(kind, namespace,
      natural_key)``.
    * Version aware — monotonic version chains; supersede-not-overwrite (PL-05).
    * Audit trail — a tamper-evident, hash-chained journal of every act.

Composition: the **Registry Core** plus twelve typed registries — Namespace,
Capability, Document, Engine, Component, API, Service, Application,
Infrastructure, Dependency, Evidence, Certification — behind one versioned
``registry.platform`` contract. Stdlib-only (TP-04/TP-05); never writes to the
frozen corpus (DP-03).
"""

from __future__ import annotations

from engine.registry.universal.audit import (
    GENESIS_HASH,
    AuditJournal,
    SequenceClock,
    utc_clock,
)
from engine.registry.universal.core import DEFAULT_ACTOR, RegistryCore, version_ref
from engine.registry.universal.errors import (
    AuditIntegrityError,
    DependencyError,
    DuplicateRegistrationError,
    KnowledgeOnceViolation,
    NamespaceError,
    RegistrationError,
    RegistrationNotFoundError,
    RegistrationValidationError,
    VersionConflictError,
)
from engine.registry.universal.identity import (
    ID_PREFIX,
    RegistryKind,
    canonical_json,
    content_digest,
    deterministic_id,
    identity_tuple,
    normalize_namespace,
    normalize_natural_key,
    parse_kind,
)
from engine.registry.universal.records import (
    AuditAct,
    AuditEntry,
    Registration,
    RegistrationRequest,
    RegistrationState,
)
from engine.registry.universal.registries import (
    REGISTRY_PLATFORM_CONTRACT,
    ApiRegistry,
    ApplicationRegistry,
    CapabilityRegistry,
    CertificationRegistry,
    ComponentRegistry,
    DependencyRegistry,
    DocumentRegistry,
    EngineRegistry,
    EvidenceRegistry,
    InfrastructureRegistry,
    NamespaceRegistry,
    ServiceRegistry,
    TypedRegistry,
    UniversalRegistryPlatform,
)

__all__ = [
    # facade + core
    "UniversalRegistryPlatform",
    "RegistryCore",
    "REGISTRY_PLATFORM_CONTRACT",
    "DEFAULT_ACTOR",
    "version_ref",
    # identity
    "RegistryKind",
    "ID_PREFIX",
    "canonical_json",
    "content_digest",
    "deterministic_id",
    "identity_tuple",
    "normalize_namespace",
    "normalize_natural_key",
    "parse_kind",
    # records
    "RegistrationRequest",
    "Registration",
    "RegistrationState",
    "AuditEntry",
    "AuditAct",
    # audit
    "AuditJournal",
    "GENESIS_HASH",
    "SequenceClock",
    "utc_clock",
    # typed registries
    "TypedRegistry",
    "NamespaceRegistry",
    "CapabilityRegistry",
    "DocumentRegistry",
    "EngineRegistry",
    "ComponentRegistry",
    "ApiRegistry",
    "ServiceRegistry",
    "ApplicationRegistry",
    "InfrastructureRegistry",
    "DependencyRegistry",
    "EvidenceRegistry",
    "CertificationRegistry",
    # errors
    "RegistrationError",
    "RegistrationValidationError",
    "NamespaceError",
    "DuplicateRegistrationError",
    "KnowledgeOnceViolation",
    "VersionConflictError",
    "RegistrationNotFoundError",
    "DependencyError",
    "AuditIntegrityError",
]
