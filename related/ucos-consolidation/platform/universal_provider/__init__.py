"""UCOS Ω∞ — Universal Provider Architecture (UPA · Terminal-04).

The **Universal Provider Architecture** is the substrate through which *any* external
or internal capability source enters UCOS. It exists to make one guarantee structural
rather than aspirational:

    Every provider — Repository, Documentation, Architecture, Research, Journal,
    Patent, Standards, Government, Security, AI, Runtime, Marketplace, Customer,
    Financial, and every provider not yet imagined — implements **one constitutional
    interface**, and no provider is named anywhere in this framework.

There is no provider-specific architecture here. There is no enumeration of provider
kinds, no ``if kind == ...``, no per-provider module, and no import of any provider.
A provider enters through **data**: a descriptor (authored in code or as a JSON
manifest) that names its own identity, capabilities, and entry point. Onboarding is
therefore registration plus declaration — never a framework change. That is the whole
point, and gate ``PV-02-KIND-OPEN`` proves it mechanically by scanning this package's
own source for the provider under validation.

Eight deliverables, one per module:

    1. **constitution** — the Provider Constitution: fourteen articles, six
       constitutional operations, an open kind vocabulary, and one executable gate per
       article. The law providers are held to.
    2. **contracts** — the value types crossing the one provider boundary:
       :class:`~platform.universal_provider.contracts.ProviderDescriptor`,
       ``ProviderQuery``/``ProviderResponse``, ``ProviderResource`` (provenance
       mandatory), ``ProviderHealth``, ``ProviderAttestation``, and the
       :class:`~platform.universal_provider.contracts.Provider` protocol itself.
    3. **sdk** — :class:`~platform.universal_provider.sdk.BaseProvider`: constitutional
       conformance by default. An author supplies substrate access through three
       hooks; the SDK supplies capability admission, determinism, provenance,
       pagination, and fault isolation, and does not let the author opt out.
    4. **registry** — the append-only, content-addressed registration authority, with
       semver resolution, additive-evolution enforcement, and acyclic dependency
       ordering.
    5. **discovery** — manifest-driven, registry-driven, and in-process discovery, plus
       :func:`~platform.universal_provider.discovery.resolve_entry_point`: the single
       bridge from a declaration to a live provider.
    6. **lifecycle** — the nine-phase state machine and its hash-chained transition
       ledger. The only path to provider state, with no edge into ``ACTIVE`` that
       bypasses ``CERTIFIED``.
    7. **validation** — fourteen executable gates, one per article, with three
       outcomes. ``INDETERMINATE`` is first-class: a declared-but-unbuilt provider is
       reported as *incomplete*, never as passing and never as failing.
    8. **certification** — tiered, sound, content-addressed certificates over
       validation evidence, in an append-only hash-chained ledger. Only
       ``CERTIFIED-UNIVERSAL`` authorizes service.

Plus **composition** (a composite of providers is itself a provider, so composition is
closed and unboundedly nestable), **framework** (the façade running
discover → admit → realize → validate → certify → activate), **evidence**
(byte-reproducible, self-verifying bundles), and **cli** (``ucos-provider``).

Everything is deterministic and content-addressed: no wall-clock, no ambient state,
canonical JSON throughout. An identical catalog over an identical substrate yields an
identical framework state hash.
"""

from __future__ import annotations

from platform.universal_provider.certification import (
    CertificationLedger,
    CertificationTier,
    ProviderCertificate,
    ProviderCertifier,
)
from platform.universal_provider.composition import (
    CompositeProvider,
    CompositionStrategy,
    compose_providers,
)
from platform.universal_provider.constitution import (
    CONSTITUTIONAL_OPERATIONS,
    INTRINSIC_OPERATIONS,
    PROVIDER_ARTICLES,
    PROVIDER_CONSTITUTION_VERSION,
    PROVIDER_INTERFACE,
    PROVIDER_INTERFACE_VERSION,
    SUBSTRATE_OPERATIONS,
    ProviderArticle,
    ProviderConstitution,
    ProviderOperation,
    provider_constitution,
)
from platform.universal_provider.contracts import (
    PROVIDER_CONTRACT_VERSION,
    Provider,
    ProviderAttestation,
    ProviderCapability,
    ProviderDependency,
    ProviderDescriptor,
    ProviderHealth,
    ProviderIdentity,
    ProviderQuery,
    ProviderResource,
    ProviderResponse,
    ProviderState,
    canonical_json,
    content_hash,
)
from platform.universal_provider.discovery import (
    CatalogSource,
    DeclarationSource,
    DiscoveredProvider,
    DiscoveryResult,
    ProviderDiscovery,
    RegistrySource,
    resolve_entry_point,
)
from platform.universal_provider.errors import (
    ProviderCapabilityError,
    ProviderCertificationError,
    ProviderCompositionError,
    ProviderConstitutionError,
    ProviderContractError,
    ProviderDiscoveryError,
    ProviderExecutionError,
    ProviderFrameworkError,
    ProviderLifecycleError,
    ProviderRegistryError,
    ProviderValidationError,
)
from platform.universal_provider.evidence import (
    ProviderEvidenceBundle,
    build_evidence,
    verify_evidence,
    write_evidence,
)
from platform.universal_provider.framework import (
    PROVIDER_FRAMEWORK_VERSION,
    OnboardingResult,
    ProviderFramework,
)
from platform.universal_provider.lifecycle import (
    LIFECYCLE_TRANSITIONS,
    LifecycleEntry,
    ProviderLifecycle,
    ProviderPhase,
)
from platform.universal_provider.registry import (
    ProviderRegistration,
    ProviderRegistry,
)
from platform.universal_provider.sdk import (
    PROVIDER_SDK_VERSION,
    BaseProvider,
    declare_capability,
    declare_dependency,
    declare_provider,
)
from platform.universal_provider.validation import (
    GateResult,
    GateStatus,
    ProviderGate,
    ProviderValidator,
    ValidationReport,
    ValidationStatus,
    ValidationSubject,
    default_gates,
)

#: Semantic version of the Universal Provider Architecture as a whole.
UNIVERSAL_PROVIDER_VERSION = "1.0.0"

__all__ = [
    "CONSTITUTIONAL_OPERATIONS",
    "INTRINSIC_OPERATIONS",
    "LIFECYCLE_TRANSITIONS",
    "PROVIDER_ARTICLES",
    "PROVIDER_CONSTITUTION_VERSION",
    "PROVIDER_CONTRACT_VERSION",
    "PROVIDER_FRAMEWORK_VERSION",
    "PROVIDER_INTERFACE",
    "PROVIDER_INTERFACE_VERSION",
    "PROVIDER_SDK_VERSION",
    "SUBSTRATE_OPERATIONS",
    "UNIVERSAL_PROVIDER_VERSION",
    "BaseProvider",
    "CatalogSource",
    "CertificationLedger",
    "CertificationTier",
    "CompositeProvider",
    "CompositionStrategy",
    "DeclarationSource",
    "DiscoveredProvider",
    "DiscoveryResult",
    "GateResult",
    "GateStatus",
    "LifecycleEntry",
    "OnboardingResult",
    "Provider",
    "ProviderArticle",
    "ProviderAttestation",
    "ProviderCapability",
    "ProviderCapabilityError",
    "ProviderCertificate",
    "ProviderCertificationError",
    "ProviderCertifier",
    "ProviderCompositionError",
    "ProviderConstitution",
    "ProviderConstitutionError",
    "ProviderContractError",
    "ProviderDependency",
    "ProviderDescriptor",
    "ProviderDiscovery",
    "ProviderDiscoveryError",
    "ProviderEvidenceBundle",
    "ProviderExecutionError",
    "ProviderFramework",
    "ProviderFrameworkError",
    "ProviderGate",
    "ProviderHealth",
    "ProviderIdentity",
    "ProviderLifecycle",
    "ProviderLifecycleError",
    "ProviderOperation",
    "ProviderPhase",
    "ProviderQuery",
    "ProviderRegistration",
    "ProviderRegistryError",
    "ProviderRegistry",
    "ProviderResource",
    "ProviderResponse",
    "ProviderState",
    "ProviderValidationError",
    "ProviderValidator",
    "RegistrySource",
    "ValidationReport",
    "ValidationStatus",
    "ValidationSubject",
    "build_evidence",
    "canonical_json",
    "compose_providers",
    "content_hash",
    "declare_capability",
    "declare_dependency",
    "declare_provider",
    "default_gates",
    "provider_constitution",
    "resolve_entry_point",
    "verify_evidence",
    "write_evidence",
]
