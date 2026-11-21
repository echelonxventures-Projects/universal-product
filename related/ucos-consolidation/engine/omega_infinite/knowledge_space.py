"""UCOS Ω∞ Phase 1, Deliverable 5 — KnowledgeSpace. A repository root is now one kind of space.

AUTHORITY = NONE (DERIVED TRUTH).

THE ASSUMPTION THIS REMOVES. Every entry point in UCOS-OMEGA-001 takes ``root: str = "."`` and
means by it "the directory that is a git repository whose Python I will govern"::

    def build(root: str = ".") -> OmegaSurface
    def evaluate(root: str = ".") -> Verdict
    def derived_scope(root: str) -> ...

One string, carrying three unstated commitments at once: it is a filesystem path, it is a
repository, and it is the whole world. A bucket is not a path. A registry has no root. A federation
has several. So the signature itself is the limit — not any decision inside these functions.

WHAT A KNOWLEDGE SPACE IS. The bounded world a measurement is made over, plus the providers that
can enumerate it, plus what those providers declare they can do. It answers "what is in scope, and
by what mechanism do we know", which is exactly the pair ``root: str`` conflated into one word.

THE SIX KINDS THE DIRECTIVE NAMES, AND HOW EACH ARRIVES.

  REPOSITORY   implemented. Version-controlled content; prefers a TRACKED_CONTENT provider.
  FILESYSTEM   implemented. Direct storage; no version control anywhere in the path.
  BUCKET       a provider declaring REMOTE_STORAGE, registered into a space of this kind.
  REGISTRY     a provider whose locators are names in a catalogue rather than paths.
  FEDERATION   a space holding SEVERAL providers. The seam is already open — ``BaseKnowledgeSpace``
               takes a registry, not a provider, and ``discover`` merges across all of them,
               deduplicating on ``Artifact.identifier``. Federation therefore needs a subclass that
               registers more providers, not a redesign of this file.
  GRAPH        a provider whose artifacts carry ``relationships``, which the universal Artifact
               already models for exactly this reason.

Only two are implemented, because Phase 1's goal is to remove the structural limit rather than to
support every platform. The test of success is that the four unimplemented kinds require
REGISTRATION and not RESTRUCTURING — which is why they are named here with the mechanism each
would use, rather than left as a gesture at future work.

WHY ``discover`` RETURNS PROVENANCE AND NOT JUST ARTIFACTS. The repository already computed four
independent populations that no code ever compared, and 619 artifacts sat in exactly one of them.
A population that does not carry the space, the providers and the selector that produced it cannot
be compared with another population — so ``SpacePopulation`` carries all three.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from engine.omega_infinite.artifact import Artifact
from engine.omega_infinite.capability import TRACKED_CONTENT, Capability, CapabilitySet
from engine.omega_infinite.provider import (
    DiscoveryProvider,
    ProviderError,
    ProviderRegistry,
    Selector,
)


class KnowledgeSpaceError(RuntimeError):
    """A knowledge space could not be constructed or could not be discovered over."""


@dataclass(frozen=True, order=True)
class SpaceKind:
    """What sort of world a space is. A VALUE, so a seventh kind is data and not a code change."""

    name: str
    description: str = ""

    def __str__(self) -> str:
        return self.name


REPOSITORY = SpaceKind(
    "REPOSITORY",
    "Version-controlled content with an eligibility boundary: an index decides what is in scope.",
)
FILESYSTEM = SpaceKind(
    "FILESYSTEM",
    "Content read directly from storage, with no version control and therefore no boundary "
    "beyond what is readable.",
)
BUCKET = SpaceKind("BUCKET", "Object storage behind a network boundary.")
REGISTRY = SpaceKind("REGISTRY", "A catalogue whose locators are names rather than paths.")
FEDERATION = SpaceKind("FEDERATION", "Several spaces measured as one, deduplicated by identifier.")
GRAPH = SpaceKind(
    "GRAPH", "A relationship-primary space where edges, not containers, define scope."
)

#: Named so the vocabulary is legible. NOTHING QUANTIFIES OVER THIS TUPLE — no dispatch, no
#: validation, no branch. A space kind absent from it works identically, which is the property that
#: makes the list safe to be incomplete.
KINDS: tuple[SpaceKind, ...] = (BUCKET, FEDERATION, FILESYSTEM, GRAPH, REGISTRY, REPOSITORY)


@dataclass(frozen=True)
class SpacePopulation:
    """A discovered population, plus everything needed to compare it with another one.

    ``capabilities`` is the UNION of the contributing providers' declarations, which is the honest
    aggregate: a federated population that came partly from an untracked source cannot claim
    ``TRACKED_CONTENT``, and ``guarantees`` computes that intersection instead when a caller needs
    the weakest common guarantee.
    """

    space: str
    kind: SpaceKind
    artifacts: tuple[Artifact, ...]
    providers: tuple[str, ...]
    selector: Selector
    capabilities: CapabilitySet = field(default_factory=CapabilitySet)

    def locators(self) -> tuple[str, ...]:
        return tuple(a.location.locator for a in self.artifacts)

    def identifiers(self) -> tuple[str, ...]:
        return tuple(a.identifier for a in self.artifacts)

    def by_type(self) -> dict[str, int]:
        counted: dict[str, int] = {}
        for artifact in self.artifacts:
            key = artifact.artifact_type.name
            counted[key] = counted.get(key, 0) + 1
        return dict(sorted(counted.items()))

    def as_record(self) -> dict[str, object]:
        return {
            "space": self.space,
            "kind": self.kind.name,
            "providers": list(self.providers),
            "selector": self.selector.as_record(),
            "capabilities": list(self.capabilities.names()),
            "artifacts": len(self.artifacts),
            "by_type": self.by_type(),
        }

    def __len__(self) -> int:
        return len(self.artifacts)


@runtime_checkable
class KnowledgeSpace(Protocol):
    """The bounded world a measurement is made over."""

    def identifier(self) -> str:
        """A stable name for this space."""

    def kind(self) -> SpaceKind:
        """Which sort of world this is."""

    def registry(self) -> ProviderRegistry:
        """The providers that can enumerate this space."""

    def discover(self, selector: Selector | None = None) -> SpacePopulation:
        """The population, with the provenance needed to compare it against another."""


class BaseKnowledgeSpace:
    """Shared behaviour. TAKES A REGISTRY, NOT A PROVIDER — which is the federation seam.

    A space with one provider and a space with nine differ only in what was registered. That is why
    ``FEDERATION`` needs no new machinery: ``discover`` already merges, deduplicates on
    ``Artifact.identifier`` and reports every contributing provider.
    """

    space_kind: SpaceKind = FILESYSTEM

    def __init__(self, identifier: str, registry: ProviderRegistry) -> None:
        if not identifier.strip():
            raise KnowledgeSpaceError("a knowledge space must have a non-empty identifier")
        if not len(registry):
            raise KnowledgeSpaceError(
                f"knowledge space {identifier!r} has no registered provider, so discovering over "
                "it would report an empty population as a clean one"
            )
        self._identifier = identifier
        self._registry = registry

    def identifier(self) -> str:
        return self._identifier

    def kind(self) -> SpaceKind:
        return self.space_kind

    def registry(self) -> ProviderRegistry:
        return self._registry

    def capabilities(self) -> CapabilitySet:
        """The UNION across providers: what this space can do by some mechanism."""
        total = CapabilitySet()
        for provider in self._registry.providers():
            total = total.union(provider.capabilities())
        return total

    def guarantees(self) -> CapabilitySet:
        """The INTERSECTION: what holds for EVERY artifact regardless of which provider found it.

        The distinction is load-bearing for federation. A space that unions git and the filesystem
        can offer ``CONTENT_HASHING`` for everything but ``TRACKED_CONTENT`` for only part of the
        population — so a measurement whose correctness depends on the eligibility boundary must
        consult this, not ``capabilities()``.
        """
        providers = self._registry.providers()
        if not providers:  # pragma: no cover - the constructor refuses an empty registry
            return CapabilitySet()
        shared = providers[0].capabilities().capabilities
        for provider in providers[1:]:
            shared = shared & provider.capabilities().capabilities
        return CapabilitySet(shared)

    def require(self, *capabilities: Capability) -> None:
        """Refuse unless EVERY provider in this space offers the capability."""
        self.guarantees().require(*capabilities, subject=f"knowledge space {self._identifier!r}")

    def discover(self, selector: Selector | None = None) -> SpacePopulation:
        """Merge every provider's enumeration, deduplicated and sorted by identifier."""
        chosen = selector or Selector()
        merged: dict[str, Artifact] = {}
        contributing: list[str] = []
        for provider in self._registry.providers():
            found = provider.enumerate(chosen)
            contributing.append(provider.identifier())
            for artifact in found:
                merged.setdefault(artifact.identifier, artifact)
        return SpacePopulation(
            space=self._identifier,
            kind=self.kind(),
            artifacts=tuple(merged[key] for key in sorted(merged)),
            providers=tuple(contributing),
            selector=chosen,
            capabilities=self.capabilities(),
        )

    def describe(self) -> dict[str, object]:
        return {
            "identifier": self._identifier,
            "kind": self.kind().name,
            "kind_description": self.kind().description,
            "capabilities_union": list(self.capabilities().names()),
            "capabilities_guaranteed": list(self.guarantees().names()),
            **self._registry.report(),
        }


class RepositoryKnowledgeSpace(BaseKnowledgeSpace):
    """A version-controlled space. What ``root: str`` used to mean, now said explicitly.

    REQUIRES ``TRACKED_CONTENT`` FROM EVERY PROVIDER, asserted in the constructor. That assertion is
    the eligibility boundary expressed as a capability instead of as an unstated consequence of
    calling ``git ls-files``: constructing this space over a provider that enumerates the working
    copy is refused, loudly, at the point of construction rather than silently at verdict time.
    """

    space_kind = REPOSITORY

    def __init__(self, identifier: str, registry: ProviderRegistry) -> None:
        super().__init__(identifier, registry)
        self.require(TRACKED_CONTENT)


class FilesystemKnowledgeSpace(BaseKnowledgeSpace):
    """A storage-only space. No version control is consulted, required or assumed.

    Declares NO guarantee it does not have. A measurement needing the eligibility boundary will be
    refused here — correctly, and with a message naming this space — which is the difference between
    an abstraction and a pretence.
    """

    space_kind = FILESYSTEM


# ----------------------------------------------------------------------------------- resolution


def repository_space(root: str, identifier: str = "") -> RepositoryKnowledgeSpace:
    """A repository space over ``root``. Refuses when no version control provider can serve it."""
    from engine.omega_infinite import git_provider

    if not git_provider.available(root):
        raise KnowledgeSpaceError(
            f"{root!r} is not served by a version control provider, so it cannot be a REPOSITORY "
            "knowledge space; a FILESYSTEM space is the honest description of it"
        )
    registry = ProviderRegistry((git_provider.GitDiscoveryProvider(root),))
    return RepositoryKnowledgeSpace(identifier or root, registry)


def filesystem_space(root: str, identifier: str = "") -> FilesystemKnowledgeSpace:
    """A filesystem space over ``root``. Works where no version control exists at all."""
    from engine.omega_infinite import filesystem_provider

    if not filesystem_provider.available(root):
        raise KnowledgeSpaceError(f"{root!r} is not readable storage, so it is no knowledge space")
    registry = ProviderRegistry((filesystem_provider.FilesystemDiscoveryProvider(root),))
    return FilesystemKnowledgeSpace(identifier or root, registry)


def resolve_space(root: str, identifier: str = "") -> KnowledgeSpace:
    """The strongest space ``root`` can honestly support. THE Ω∞ REPLACEMENT FOR ``root: str``.

    Probes rather than assumes, and the ORDER is by strength of guarantee: a version-controlled
    space carries an eligibility boundary a filesystem space cannot, so it is preferred when
    available. A directory that has never been a repository still resolves — to a FILESYSTEM space,
    with ``TRACKED_CONTENT`` undeclared — which is the Deliverable 2 success criterion reached
    through Deliverable 5.
    """
    from engine.omega_infinite import git_provider

    if git_provider.available(root):
        return repository_space(root, identifier)
    return filesystem_space(root, identifier)


def space_of(
    identifier: str,
    kind: SpaceKind,
    providers: Iterable[DiscoveryProvider],
) -> BaseKnowledgeSpace:
    """Build a space of ANY kind from ANY providers. The registration path for kinds 3-6.

    THIS FUNCTION IS THE PROOF OF UNLIMITED EXPANSION. A bucket space is
    ``space_of("s3://evidence", BUCKET, [S3Provider(...)])`` — no subclass, no edit to this module,
    no new branch anywhere in the package. If supporting object storage required changing this
    file, the abstraction would not have removed the limit; it would have moved it.
    """
    registry = ProviderRegistry(providers)
    if not len(registry):
        raise KnowledgeSpaceError(f"space {identifier!r} was given no provider to enumerate it")

    space = BaseKnowledgeSpace(identifier, registry)
    object.__setattr__(space, "space_kind", kind)
    return space


def strongest_provider(space: KnowledgeSpace, *required: Capability) -> DiscoveryProvider:
    """The highest-priority provider in ``space`` declaring ``required``. Resolution, not naming."""
    try:
        return space.registry().resolve_capable(*required).provider
    except ProviderError as exc:
        raise KnowledgeSpaceError(
            f"knowledge space {space.identifier()!r} has no provider for the required "
            f"capabilities: {exc}"
        ) from exc
