"""UCOS Ω∞ Phase 1, Deliverable 6 — capabilities, declared by the provider and never assumed.

AUTHORITY = NONE (DERIVED TRUTH). This module legislates nothing. It records what a provider says
about itself and refuses to let a caller guess.

THE DEFECT THIS CLOSES. ``engine/universal_discovery/discovery.py`` does not ask whether version
control is available; it runs ``git ls-files`` and raises when that fails. The assumption is
invisible because it is unconditional — there is no place in the code where "is this population
tracked?" is a question, so there is no place where a different answer could be given. A caller
therefore cannot know what it is standing on:

    tracked_python(root)     ← requires git. Nothing says so. Nothing can ask.

An assumption that cannot be interrogated cannot be replaced. Phase 1 makes it interrogable.

WHY CAPABILITIES ARE OPEN AND NOT AN ENUM. An ``Enum`` is a list, and Rule Ω-1 exists because a
list of what exists agrees with itself forever. A provider for a storage system nobody has written
yet will declare a capability nobody has named yet, and that must require no edit here — so
``Capability`` is a value class, the well-known set below is a CONVENIENCE rather than a
constraint, and ``CapabilityRegistry`` admits new names at runtime.

WHY THE WELL-KNOWN SET STILL EXISTS. Two providers that spell the same property differently cannot
be compared, and a capability vocabulary in which every provider invents its own terms is not a
vocabulary. The registry therefore CANONICALISES: a name is registered once with a description,
and a second registration under a conflicting description is refused rather than silently merged.

WHAT A CAPABILITY IS NOT. It is not a permission and not a promise of quality. ``CONTENT_HASHING``
says the provider can produce a content hash, not that the hash is any particular algorithm. A
consumer that needs a specific algorithm asks the provider's ``metadata()``, which is where facts
about a concrete provider belong.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass


class CapabilityError(RuntimeError):
    """A capability was required and not declared, or declared inconsistently.

    RAISED, NEVER DEFAULTED. Returning ``False`` for "does this provider support X" when the
    provider never said either way is the same defect as an empty population passing every
    invariant: it converts "unknown" into "no" and lets a caller proceed on a fact nobody
    established.
    """


@dataclass(frozen=True, order=True)
class Capability:
    """One self-declared provider property: a canonical name and what it means.

    ``order=True`` so capability sets sort deterministically. Every document this package emits is
    compared byte-for-byte by the Phase 1 determinism test, and an unordered set would make that
    test flap for a reason that has nothing to do with discovery.
    """

    name: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise CapabilityError("a capability with no name cannot be declared or required")

    def __str__(self) -> str:
        return self.name


# --------------------------------------------------------------------------- the well-known set
# NOT AN EXHAUSTIVE LIST, and the distinction is the deliverable. These are the properties the
# repository's own two providers need in order to describe themselves; a third provider adds its
# own by calling ``CapabilityRegistry.declare``. Nothing in this package quantifies over the tuple
# below, so nothing breaks when it is incomplete — which it permanently is.

TRACKED_CONTENT = Capability(
    "TRACKED_CONTENT",
    "The provider enumerates only content an index admits, so untracked local debris cannot "
    "change a verdict. This is the property engine/universal_discovery relies on and never states.",
)
VERSIONED_CONTENT = Capability(
    "VERSIONED_CONTENT",
    "The provider can name a revision of the content, so an enumeration is reproducible against "
    "a point in history rather than only against 'now'.",
)
LOCAL_STORAGE = Capability(
    "LOCAL_STORAGE",
    "Artifact bytes are readable from the machine running the measurement with no network call.",
)
REMOTE_STORAGE = Capability(
    "REMOTE_STORAGE",
    "Artifact bytes live behind a network boundary, so enumeration cost and failure modes are "
    "not those of a filesystem and a caller must not assume they are.",
)
CONTENT_HASHING = Capability(
    "CONTENT_HASHING",
    "The provider can produce a stable content digest for an artifact without the caller reading "
    "the bytes itself.",
)
WORKING_TREE_STATE = Capability(
    "WORKING_TREE_STATE",
    "The provider can report what the local working copy holds that the tracked population does "
    "not — additions not yet indexed, and modifications not yet recorded. A DIFFERENT QUESTION "
    "from TRACKED_CONTENT rather than a wider filter on it: a verdict that must not depend on "
    "local debris asks the first, and a tool reporting what an operator has yet to commit asks "
    "the second. Conflating them is what made four callers reach past the provider for an answer "
    "it never offered.",
)
REVISION_IDENTITY = Capability(
    "REVISION_IDENTITY",
    "The provider can say how this working copy names itself and where it stands: the line of "
    "development it is on, the abbreviated form of its current revision, whether it is a working "
    "copy at all, the upstream it tracks, whether a named reference resolves, and where two "
    "references diverged. Distinct from VERSIONED_CONTENT, which names ONE revision so an "
    "enumeration is reproducible — this answers POSITION, which is what a tool reporting on the "
    "work in progress needs and what an impact selector needs to find a comparison point.",
)
CHANGE_SET = Capability(
    "CHANGE_SET",
    "The provider can name the artifacts that DIFFER between two recorded points, or between a "
    "recorded point and the working copy. A different question from TRACKED_CONTENT, which names "
    "what exists, and from WORKING_TREE_STATE, which names what is uncommitted: this one is about "
    "the delta itself, and an impact selector asks it on every run.",
)
REVISION_HISTORY = Capability(
    "REVISION_HISTORY",
    "The provider can enumerate the recorded revisions and the named lines of development that "
    "reach them. What VERSIONED_CONTENT names as one revision, this walks as a sequence.",
)
REVISION_METADATA = Capability(
    "REVISION_METADATA",
    "The provider can report the facts a recorded revision carries — when it was made, what it "
    "was called — without the caller parsing the tool's output format itself.",
)
AUTHORITY_METADATA = Capability(
    "AUTHORITY_METADATA",
    "The provider carries ownership information of its own — a committer, an owner field, an ACL "
    "— which an authority derivation may consult instead of inferring ownership from structure.",
)

#: Registered eagerly so the canonical spellings exist before any provider is constructed. A
#: convenience for readers and for the registry's conflict check; NOT a constraint on providers.
WELL_KNOWN: tuple[Capability, ...] = (
    AUTHORITY_METADATA,
    CONTENT_HASHING,
    LOCAL_STORAGE,
    REMOTE_STORAGE,
    TRACKED_CONTENT,
    VERSIONED_CONTENT,
)


class CapabilityRegistry:
    """The canonical name -> ``Capability`` mapping. Open for extension, closed to redefinition.

    OPEN, because Phase 1's whole purpose is that a storage system nobody has named yet needs no
    edit to this file. CLOSED TO REDEFINITION, because two different meanings under one name is
    worse than two names: a consumer requiring ``CONTENT_HASHING`` would be satisfied by a provider
    that meant something else by it, and the requirement would silently stop being a requirement.
    """

    def __init__(self, seed: Iterable[Capability] = WELL_KNOWN) -> None:
        self._by_name: dict[str, Capability] = {}
        for capability in seed:
            self.declare(capability)

    def declare(self, capability: Capability) -> Capability:
        """Register a capability, or return the identical existing one. A CONFLICT raises."""
        existing = self._by_name.get(capability.name)
        if existing is None:
            self._by_name[capability.name] = capability
            return capability
        if existing.description != capability.description:
            raise CapabilityError(
                f"{capability.name!r} is already declared with a different meaning, and one name "
                "with two meanings makes every requirement on it unenforceable; choose a "
                "different name"
            )
        return existing

    def declare_name(self, name: str, description: str) -> Capability:
        """Declare from primitives, for a provider assembling its own vocabulary at runtime."""
        return self.declare(Capability(name, description))

    def resolve(self, name: str) -> Capability:
        """The registered capability for a name. An UNKNOWN name raises rather than inventing one.

        This is the anti-typo boundary. ``require("CONTENT_HASHNG")`` must fail loudly; if it
        resolved to a fresh capability nothing declares, the requirement would pass vacuously.
        """
        try:
            return self._by_name[name]
        except KeyError:
            raise CapabilityError(
                f"{name!r} is not a declared capability; declare it before requiring it, so that "
                "a misspelling cannot become a requirement no provider can fail"
            ) from None

    def known(self) -> tuple[Capability, ...]:
        return tuple(sorted(self._by_name.values()))

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


#: The process-wide registry. A single canonical vocabulary, so two providers constructed in
#: different modules are comparable. Tests build their own instance rather than mutating this.
REGISTRY = CapabilityRegistry()


@dataclass(frozen=True)
class CapabilitySet:
    """What one provider declares about itself. Immutable, ordered, and answerable.

    THE INTERROGATION SURFACE. ``supports`` answers, ``require`` refuses, ``missing`` explains.
    A consumer that needs tracked content calls ``require(TRACKED_CONTENT)`` and gets a refusal
    naming the provider — which is the sentence ``discovery.tracked_python`` could never produce,
    because it had nothing to name.
    """

    capabilities: frozenset[Capability] = frozenset()

    @classmethod
    def of(cls, *capabilities: Capability) -> CapabilitySet:
        return cls(frozenset(capabilities))

    def supports(self, capability: Capability) -> bool:
        return capability in self.capabilities

    def supports_name(self, name: str) -> bool:
        return any(c.name == name for c in self.capabilities)

    def missing(self, *required: Capability) -> tuple[Capability, ...]:
        return tuple(sorted(c for c in required if c not in self.capabilities))

    def require(self, *required: Capability, subject: str = "this provider") -> None:
        """Refuse unless every named capability is declared. The Ω∞ 'no assumptions' enforcement."""
        absent = self.missing(*required)
        if absent:
            raise CapabilityError(
                f"{subject} does not declare {', '.join(c.name for c in absent)}; the operation "
                "requires it and a capability that was not declared must never be assumed"
            )

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(c.name for c in self.capabilities))

    def union(self, other: CapabilitySet) -> CapabilitySet:
        return CapabilitySet(self.capabilities | other.capabilities)

    def as_record(self) -> dict[str, object]:
        return {
            "capabilities": list(self.names()),
            "declared": {c.name: c.description for c in sorted(self.capabilities)},
        }

    def __iter__(self) -> Iterator[Capability]:
        return iter(sorted(self.capabilities))

    def __len__(self) -> int:
        return len(self.capabilities)
