"""UCOS Ω∞ Phase 1 — the Universal Discovery Abstraction Layer.

AUTHORITY = NONE (DERIVED TRUTH). This package legislates nothing, seals nothing and certifies
nothing. It removes four architectural assumptions and replaces them with abstractions.

WHAT WAS ASSUMED, AND WHAT IT IS NOW.

    git ls-files                 →  DiscoveryProvider, resolved by declared capability
    a tracked Python file        →  Artifact, of an extensible ArtifactType
    a local filesystem           →  one provider's storage model, declared not assumed
    a repository root            →  KnowledgeSpace, of an extensible SpaceKind

RULE Ω-1 IN ONE SENTENCE: git, Python, "repository" and "filesystem" are now VALUES inside
registries rather than TERMS inside control flow. Nothing in this package branches on any of them.

PHASE 1 IS ADDITIVE AND REPLACES NOTHING. ``engine/universal_discovery`` is untouched — same entry
points, same population, same dispositions, same ratchets. ``compat.equivalence`` measures that:
configuring this layer the way Ω-1 is configured reproduces Ω-1's population byte-for-byte, in the
same order, and the test suite asserts tuple equality rather than set membership.

READ IN THIS ORDER. ``capability`` (what a provider may be asked), ``artifact`` (what is found),
``classification`` (what it is), ``provider`` (how it is found), ``knowledge_space`` (where), then
``compat`` (proof nothing changed) and ``evidence`` (proof the five criteria hold).

WHAT PHASE 1 DELIBERATELY DOES NOT DO. It does not support object storage, registries, federations
or graphs. It makes each of those a REGISTRATION rather than a redesign — see
``knowledge_space.space_of`` and ``evidence.expansion_probe``, which add a capability, a type, a
space kind and a provider at runtime with no edit to any file here.
"""

from engine.omega_infinite.artifact import (
    CONFIGURATION,
    DATASET,
    DOCUMENT,
    PYTHON,
    UNKNOWN,
    WORKFLOW,
    Artifact,
    ArtifactError,
    ArtifactType,
    Authority,
    Location,
    Relationship,
)
from engine.omega_infinite.capability import (
    AUTHORITY_METADATA,
    CONTENT_HASHING,
    LOCAL_STORAGE,
    REMOTE_STORAGE,
    TRACKED_CONTENT,
    VERSIONED_CONTENT,
    Capability,
    CapabilityError,
    CapabilitySet,
)
from engine.omega_infinite.classification import (
    Classification,
    ClassificationPipeline,
    Classifier,
    TypeVocabulary,
    default_pipeline,
)
from engine.omega_infinite.knowledge_space import (
    FILESYSTEM,
    REPOSITORY,
    FilesystemKnowledgeSpace,
    KnowledgeSpace,
    KnowledgeSpaceError,
    RepositoryKnowledgeSpace,
    SpaceKind,
    SpacePopulation,
    resolve_space,
)
from engine.omega_infinite.provider import (
    DiscoveryProvider,
    ProviderError,
    ProviderMetadata,
    ProviderRegistry,
    Selector,
)

__all__ = [
    "AUTHORITY_METADATA",
    "CONFIGURATION",
    "CONTENT_HASHING",
    "DATASET",
    "DOCUMENT",
    "FILESYSTEM",
    "LOCAL_STORAGE",
    "PYTHON",
    "REMOTE_STORAGE",
    "REPOSITORY",
    "TRACKED_CONTENT",
    "UNKNOWN",
    "VERSIONED_CONTENT",
    "WORKFLOW",
    "Artifact",
    "ArtifactError",
    "ArtifactType",
    "Authority",
    "Capability",
    "CapabilityError",
    "CapabilitySet",
    "Classification",
    "ClassificationPipeline",
    "Classifier",
    "DiscoveryProvider",
    "FilesystemKnowledgeSpace",
    "KnowledgeSpace",
    "KnowledgeSpaceError",
    "Location",
    "ProviderError",
    "ProviderMetadata",
    "ProviderRegistry",
    "Relationship",
    "RepositoryKnowledgeSpace",
    "Selector",
    "SpaceKind",
    "SpacePopulation",
    "TypeVocabulary",
    "default_pipeline",
    "resolve_space",
]
