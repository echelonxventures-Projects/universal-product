"""UCOS EC-2 Platform Foundation (EC2-EPIC-001) — the reusable platform substrate.

The first implementation epic of the EC-2 Platform Realization Program. It
establishes the foundational framework every subsequent EC-2 epic builds on, as an
**additive** layer over the certified EC-1 engine — it consumes EC-1 only through
published contracts, never modifies it, never writes to the certified corpus
(DP-03), and preserves determinism end to end.

Deliverables (EC2-TASK-000055…000062):
    * **contracts** (TASK-000055) — versioned platform contract surface + canonical
      hashing, reusing EC-1 ``Version``/``Contract``/``ContractRegistry``.
    * **config** (TASK-000056) — typed, immutable platform configuration wrapping the
      EC-1 loader (secrets by reference only).
    * **identity** (TASK-000057) — the platform identity model: roles, permissions,
      immutable content-addressed principals.
    * **services** (TASK-000058) — the deterministic platform service registry.
    * **dependencies** (TASK-000059) — the deterministic, acyclic dependency model.
    * **events** (TASK-000060) — the immutable event model + append-only event bus.
    * **capabilities** (TASK-000061) — the platform + EC-1 engine capability model
      (the encoded EC-1 ↔ EC-2 boundary).
    * **bootstrap** (TASK-000062) — deterministic composition into a ``PlatformContext``.

This epic is **foundation only**: no UI, portal, workspace, dashboard, or runtime
operation is implemented here.
"""

from __future__ import annotations

from platform.foundation.admission import (
    ADMISSION_LEDGER_FORMAT,
    AdmissionAuthority,
    AdmissionBinder,
    AdmissionRecord,
    AuthorityMigration,
    AuthorityStatus,
)
from platform.foundation.bootstrap import (
    BOOTSTRAP_EVENT,
    PlatformContext,
    bootstrap_platform,
)
from platform.foundation.canonical import (
    CCF_DEFAULT_PROFILE,
    CCF_DIGEST_ALGORITHM,
    DEFAULT_PROFILE,
    CanonicalDigest,
    CanonicalProfile,
    ProfileRegistry,
    canonical_bytes,
    canonical_string,
    content_digest,
    normalize_text,
)
from platform.foundation.capabilities import (
    Capability,
    CapabilityCatalog,
    CapabilityKind,
    default_capability_catalog,
    default_engine_capabilities,
    default_platform_capabilities,
)
from platform.foundation.config import (
    Environment,
    PlatformConfig,
    SecretRef,
    load_platform_config,
)
from platform.foundation.contracts import (
    ENGINE_CONTRACTS,
    PLATFORM_CONTRACT_VERSION,
    PLATFORM_NAME,
    PLATFORM_PROGRAM_ID,
    Contract,
    ContractRef,
    ContractRegistry,
    Version,
    canonical_json,
    content_hash,
    platform_contract,
    platform_contract_registry,
)
from platform.foundation.crypto_agility import (
    CRYPTO_REGISTRY_FORMAT,
    DEFAULT_ALGORITHMS,
    MULTIHASH_SEPARATOR,
    AlgorithmRegistry,
    AlgorithmStatus,
    DigestSet,
    HashAlgorithm,
    Multihash,
    RolloverRecord,
    compute_multihash,
    default_algorithm_registry,
)
from platform.foundation.dag_ledger import (
    DAG_LEDGER_FORMAT,
    EVENT_ID_PREFIX,
    GENESIS_HASH,
    DagEvent,
    EventDag,
)
from platform.foundation.dependencies import DependencyGraph, DependencyNode
from platform.foundation.derivation import (
    DERIVATION_LEDGER_FORMAT,
    DerivationContract,
    DerivationEngine,
    DerivationInput,
    DerivationResult,
    InputKind,
)
from platform.foundation.durable_identity import (
    DURABLE_IDENTITY_PROFILE,
    IDENTITY_REGISTRY_FORMAT,
    P2_OPAQUE_HEX_LEN,
    P2_URN_PREFIX,
    AdmissionKey,
    DurableIdentity,
    IdentityMint,
    IdentityRegistry,
    MintState,
    build_identity_registry,
)
from platform.foundation.errors import (
    AdmissionError,
    AlgorithmNegotiationError,
    AuthorityBindingError,
    BootstrapError,
    CanonicalFormError,
    CapabilityError,
    CryptoAgilityError,
    DagLedgerError,
    DagLedgerIntegrityError,
    DependencyError,
    DerivationError,
    DerivationPurityError,
    DuplicateAdmissionError,
    DurableIdentityError,
    EventError,
    IdentityCollisionError,
    IdentityMintError,
    PlatformConfigError,
    PlatformContractError,
    PlatformError,
    PlatformIdentityError,
    ServiceRegistrationError,
    ServiceResolutionError,
    SignatureError,
    TrustChainError,
    TrustError,
)
from platform.foundation.events import EventBus, EventHandler, PlatformEvent
from platform.foundation.identity import (
    READ_ONLY_ROLES,
    SCOPED_ROLES,
    Permission,
    Principal,
    Role,
    all_roles,
)
from platform.foundation.services import (
    ServiceDescriptor,
    ServiceProvider,
    ServiceRegistry,
)
from platform.foundation.trust import (
    TRUST_SIGNATURE_ALGORITHM,
    TRUST_STORE_FORMAT,
    Delegation,
    KeyStatus,
    NotaryRecord,
    Revocation,
    Signature,
    TrustEngine,
    TrustKey,
    bootstrap_trust,
)

__all__ = [
    # contracts (TASK-000055)
    "PLATFORM_CONTRACT_VERSION",
    "PLATFORM_NAME",
    "PLATFORM_PROGRAM_ID",
    "Version",
    "Contract",
    "ContractRegistry",
    "ContractRef",
    "platform_contract",
    "platform_contract_registry",
    "canonical_json",
    "content_hash",
    "ENGINE_CONTRACTS",
    # config (TASK-000056)
    "Environment",
    "SecretRef",
    "PlatformConfig",
    "load_platform_config",
    # identity (TASK-000057)
    "Role",
    "Permission",
    "Principal",
    "SCOPED_ROLES",
    "READ_ONLY_ROLES",
    "all_roles",
    # services (TASK-000058)
    "ServiceProvider",
    "ServiceDescriptor",
    "ServiceRegistry",
    # dependencies (TASK-000059)
    "DependencyNode",
    "DependencyGraph",
    # events (TASK-000060)
    "EventHandler",
    "PlatformEvent",
    "EventBus",
    # DAG event ledger (WP-03 / PRJ-C2 · ACT-C2)
    "GENESIS_HASH",
    "DAG_LEDGER_FORMAT",
    "EVENT_ID_PREFIX",
    "DagEvent",
    "EventDag",
    # P2 durable identity minting (WP-04 / PRJ-C2 · ACT-C2)
    "DURABLE_IDENTITY_PROFILE",
    "P2_OPAQUE_HEX_LEN",
    "P2_URN_PREFIX",
    "IDENTITY_REGISTRY_FORMAT",
    "AdmissionKey",
    "DurableIdentity",
    "MintState",
    "IdentityMint",
    "IdentityRegistry",
    "build_identity_registry",
    # genesis trust, keys & signing (WP-05 / PRJ-C2 · ACT-C2)
    "TRUST_SIGNATURE_ALGORITHM",
    "TRUST_STORE_FORMAT",
    "KeyStatus",
    "TrustKey",
    "Signature",
    "Delegation",
    "NotaryRecord",
    "Revocation",
    "TrustEngine",
    "bootstrap_trust",
    # canonical content form (WP-06 / PRJ-C2 · ACT-C2)
    "CCF_DEFAULT_PROFILE",
    "CCF_DIGEST_ALGORITHM",
    "DEFAULT_PROFILE",
    "CanonicalProfile",
    "ProfileRegistry",
    "CanonicalDigest",
    "normalize_text",
    "canonical_string",
    "canonical_bytes",
    "content_digest",
    # crypto agility (WP-07 / PRJ-C2 · ACT-C2)
    "CRYPTO_REGISTRY_FORMAT",
    "MULTIHASH_SEPARATOR",
    "DEFAULT_ALGORITHMS",
    "AlgorithmStatus",
    "HashAlgorithm",
    "Multihash",
    "RolloverRecord",
    "AlgorithmRegistry",
    "DigestSet",
    "compute_multihash",
    "default_algorithm_registry",
    # admission key binder (WP-08 / PRJ-C2 · ACT-C2)
    "ADMISSION_LEDGER_FORMAT",
    "AuthorityStatus",
    "AdmissionAuthority",
    "AdmissionRecord",
    "AuthorityMigration",
    "AdmissionBinder",
    # derivation purity (WP-09 / PRJ-C2 · ACT-C2)
    "DERIVATION_LEDGER_FORMAT",
    "InputKind",
    "DerivationInput",
    "DerivationContract",
    "DerivationResult",
    "DerivationEngine",
    # capabilities (TASK-000061)
    "CapabilityKind",
    "Capability",
    "CapabilityCatalog",
    "default_engine_capabilities",
    "default_platform_capabilities",
    "default_capability_catalog",
    # bootstrap (TASK-000062)
    "BOOTSTRAP_EVENT",
    "PlatformContext",
    "bootstrap_platform",
    # errors (TASK-000055)
    "PlatformError",
    "PlatformContractError",
    "PlatformConfigError",
    "PlatformIdentityError",
    "ServiceRegistrationError",
    "ServiceResolutionError",
    "DependencyError",
    "EventError",
    "DagLedgerError",
    "DagLedgerIntegrityError",
    "DurableIdentityError",
    "IdentityMintError",
    "IdentityCollisionError",
    "TrustError",
    "SignatureError",
    "TrustChainError",
    "CanonicalFormError",
    "CryptoAgilityError",
    "AlgorithmNegotiationError",
    "AdmissionError",
    "AuthorityBindingError",
    "DuplicateAdmissionError",
    "DerivationError",
    "DerivationPurityError",
    "CapabilityError",
    "BootstrapError",
]
