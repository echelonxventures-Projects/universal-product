"""UCOS Ω∞ Phase 1, Deliverable 1 — the DiscoveryProvider contract, registry and resolution.

AUTHORITY = NONE (DERIVED TRUTH).

THE ASSUMPTION THIS REMOVES, quoted from the code it removes it from::

    # engine/universal_discovery/discovery.py
    subprocess.run(["git", "ls-files", "-z", "--cached", "--exclude-standard", "*.py"], ...)

That line is the entire discovery mechanism of UCOS. It is correct, it is deliberate, and it is a
hard architectural limit: there is no seam at which a different enumeration could be substituted,
so "UCOS governs a git repository of Python" is not a configuration of the system, it IS the
system. Phase 1 introduces the seam.

THE CONTRACT IS FOUR QUESTIONS, and the fourth is the one that makes the other three safe.

  identifier()    a stable name, so evidence can say which provider produced a population
  enumerate()     the artifacts, as universal Artifacts rather than paths
  metadata()      facts about this provider instance — where it is bound, what it is reading
  capabilities()  what it can and cannot do, SELF-DECLARED

WITHOUT ``capabilities()`` THE ABSTRACTION WOULD BE A LIE. A caller holding an interface it cannot
interrogate must assume, and assumption is what Phase 1 exists to delete. With it, "this
measurement requires tracked content" becomes a refusal naming the provider instead of a silent
difference in behaviour between a developer's machine and a clean checkout.

WHAT A PROVIDER IS NOT. It is not a classifier — types come from Deliverable 4, and a provider that
typed its own artifacts would be a second classification path disagreeing with the first. It is not
an authority derivation. It is not a knowledge space. A provider answers exactly one question:
"what is here?"

RESOLUTION IS BY CAPABILITY, NEVER BY NAME. ``resolve_capable(TRACKED_CONTENT)`` is the call a
measurement makes; ``resolve("git")`` exists for evidence and tests. Selecting a provider by name
would re-introduce the assumption one layer up — the code would once again say "git" — which is
precisely the smuggling Rule Ω-1 forbids.
"""

from __future__ import annotations

import fnmatch
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from engine.omega_infinite.artifact import Artifact
from engine.omega_infinite.capability import Capability, CapabilitySet


class ProviderError(RuntimeError):
    """A provider could not enumerate, or no provider satisfied a requirement.

    RAISED, NEVER DEFAULTED — the same discipline as ``OmegaError``. A resolution that returned
    ``None`` when nothing matched would let a caller measure an empty population and report a
    pass, and an empty population satisfies every invariant in the system.
    """


@dataclass(frozen=True)
class Selector:
    """Which artifacts an enumeration wants, expressed without assuming a storage model.

    ``patterns`` are matched against the LOCATOR with ``fnmatch``, which is a string operation and
    not a filesystem one — so the same selector works against object keys and graph node names.

    ``EMPTY MEANS EVERYTHING``, deliberately. The Ω-1 query hard-codes ``'*.py'``; the default here
    is "no filter", so a provider's honest answer to "what is here?" is the whole population and
    narrowing it is an explicit act by the caller.
    """

    patterns: tuple[str, ...] = ()
    limit: int | None = None

    def matches(self, locator: str) -> bool:
        if not self.patterns:
            return True
        return any(fnmatch.fnmatch(locator, pattern) for pattern in self.patterns)

    def apply(self, artifacts: Sequence[Artifact]) -> tuple[Artifact, ...]:
        kept = tuple(a for a in artifacts if self.matches(a.location.locator))
        if self.limit is None:
            return kept
        return kept[: self.limit]

    def as_record(self) -> dict[str, object]:
        return {"patterns": list(self.patterns), "limit": self.limit}


#: A selector for nothing at all, used by capability probes that must not pay for an enumeration.
NOTHING = Selector(patterns=("",))


@dataclass(frozen=True)
class ProviderMetadata:
    """Facts about one provider INSTANCE — not about its class.

    ``binding`` is where this instance is pointed; ``mechanism`` is how it reads; ``details`` is
    open, because a provider knows things about itself that no abstraction can anticipate. The
    ``revision`` field is empty unless the provider declares ``VERSIONED_CONTENT``, so a record
    cannot claim reproducibility the provider never offered.
    """

    identifier: str
    binding: str
    mechanism: str
    revision: str = ""
    details: dict[str, str] = field(default_factory=dict)

    def as_record(self) -> dict[str, object]:
        return {
            "identifier": self.identifier,
            "binding": self.binding,
            "mechanism": self.mechanism,
            "revision": self.revision,
            "details": dict(sorted(self.details.items())),
        }


@runtime_checkable
class DiscoveryProvider(Protocol):
    """The Ω∞ discovery contract. Four methods, and no assumption about what is behind them."""

    def identifier(self) -> str:
        """A stable, unique name for this provider."""

    def enumerate(self, selector: Selector | None = None) -> tuple[Artifact, ...]:
        """Every artifact this provider can see, narrowed by ``selector``."""

    def metadata(self) -> ProviderMetadata:
        """Facts about this provider instance."""

    def capabilities(self) -> CapabilitySet:
        """What this provider declares it can do. Never inferred by the caller."""


class BaseProvider:
    """Shared plumbing for the concrete providers. NOT part of the contract.

    A provider may implement ``DiscoveryProvider`` without inheriting from this — the contract is a
    Protocol precisely so that a third-party provider needs no dependency on this class. What lives
    here is only the machinery every provider would otherwise duplicate: capability requirement,
    deterministic ordering, and the enumerate/collect split.
    """

    #: Providers are resolved highest-priority-first, so a repository bound to both a version
    #: control system and a filesystem prefers the one carrying stronger guarantees.
    priority: int = 0

    def identifier(self) -> str:  # pragma: no cover - every subclass overrides
        raise NotImplementedError

    def capabilities(self) -> CapabilitySet:  # pragma: no cover - every subclass overrides
        raise NotImplementedError

    def metadata(self) -> ProviderMetadata:  # pragma: no cover - every subclass overrides
        raise NotImplementedError

    def collect(self, selector: Selector) -> Iterable[Artifact]:  # pragma: no cover - overridden
        """The provider-specific enumeration. Called by ``enumerate``, never by a consumer."""
        raise NotImplementedError

    def enumerate(self, selector: Selector | None = None) -> tuple[Artifact, ...]:
        """Sorted, deduplicated, selector-narrowed. ONE ordering rule for every provider.

        Determinism is enforced here rather than trusted to each provider: ``git ls-files`` returns
        sorted output and ``os.walk`` does not, and a population whose order depends on the
        provider would make two evidence documents differ for no governed reason.
        """
        chosen = selector or Selector()
        collected = {a.identifier: a for a in self.collect(chosen)}
        ordered = tuple(collected[key] for key in sorted(collected))
        return chosen.apply(ordered)

    #: How a capability's name becomes the method that delivers it. One rule, so a new capability
    #: is a declaration plus a method and never a change to this class.
    SUPPLY_PREFIX = "supply_"

    def supply(
        self, capability: Capability, selector: Selector | None = None, **arguments: object
    ) -> object:
        """Deliver what ``capability`` promises, or refuse.

        WHY THIS EXISTS. Measured before it did: the git provider declared five capabilities and
        the protocol offered ONE data method, ``enumerate``. Four of the five — VERSIONED_CONTENT,
        CONTENT_HASHING, AUTHORITY_METADATA, LOCAL_STORAGE — could not be obtained through any
        call, so `AUTHORITY_METADATA`, which the provider's own docstring says it "exposes on
        request", had no request to make. Callers that needed those facts went to the tool
        directly, and were then counted as bypassing an abstraction that did not cover them.

        A DECLARATION NOW COSTS SOMETHING. `verify_capabilities` refuses a provider declaring a
        capability it cannot supply, so declaring one is a promise the class must keep rather than
        a line in a report. That is the property `ENVELOPE_ONLY` was defined to catch, applied
        here before the axis is registered rather than after.
        """
        self.require(capability)
        method = getattr(self, self.SUPPLY_PREFIX + capability.name.lower(), None)
        if method is None:
            raise ProviderError(
                f"provider {self.identifier()!r} declares {capability.name} and supplies no "
                f"{self.SUPPLY_PREFIX}{capability.name.lower()}"
            )
        # KEYWORD ARGUMENTS PASS THROUGH, because not every question is a pattern. A change set
        # is asked between two recorded points and a revision's metadata is asked of one revision;
        # forcing either through a Selector would make the selector mean different things to
        # different capabilities, which is how a contract stops being one contract.
        return method(selector or Selector(), **arguments)

    def verify_capabilities(self) -> tuple[str, ...]:
        """Every declared capability this provider cannot deliver. Empty is the contract.

        TRACKED_CONTENT is satisfied by ``collect``/``enumerate`` rather than a supply method,
        because enumeration IS the protocol's one required question and predates this dispatch.
        """
        missing = []
        for cap in sorted(self.capabilities(), key=lambda c: c.name):
            if cap.name == "TRACKED_CONTENT":
                continue
            if getattr(self, self.SUPPLY_PREFIX + cap.name.lower(), None) is None:
                missing.append(cap.name)
        return tuple(missing)

    def require(self, *capabilities: Capability) -> None:
        """Refuse an operation this provider never claimed to support."""
        self.capabilities().require(*capabilities, subject=f"provider {self.identifier()!r}")

    def report(self) -> dict[str, object]:
        """Provider self-description, for the evidence document."""
        return {
            "identifier": self.identifier(),
            "priority": self.priority,
            "metadata": self.metadata().as_record(),
            **self.capabilities().as_record(),
        }


# ------------------------------------------------------------------------------------ registry


@dataclass(frozen=True)
class Resolution:
    """Which provider was chosen, and WHY. Returned by capability resolution.

    The rejected list is carried on purpose: "no provider supports REMOTE_STORAGE" is a much less
    useful sentence than "filesystem and git were considered and neither declares it".
    """

    provider: DiscoveryProvider
    required: tuple[Capability, ...]
    rejected: tuple[tuple[str, tuple[str, ...]], ...] = ()

    def as_record(self) -> dict[str, object]:
        return {
            "chosen": self.provider.identifier(),
            "required": [c.name for c in self.required],
            "rejected": [{"provider": name, "missing": list(gap)} for name, gap in self.rejected],
        }


class ProviderRegistry:
    """The set of available providers, resolvable by name and by declared capability.

    OPEN AND UNBOUNDED. Nothing here enumerates provider kinds, so a provider for a storage system
    nobody has written yet is registered rather than integrated. That is the Deliverable 1 success
    criterion: git and the filesystem enter through the same door as everything that follows.
    """

    def __init__(self, providers: Iterable[DiscoveryProvider] = ()) -> None:
        self._by_identifier: dict[str, DiscoveryProvider] = {}
        for provider in providers:
            self.register(provider)

    def register(self, provider: DiscoveryProvider) -> DiscoveryProvider:
        """Add a provider. A DUPLICATE IDENTIFIER RAISES rather than replacing silently.

        Silent replacement would make the population depend on registration order, and registration
        order depends on import order — which is exactly the class of defect that cannot be
        reproduced from a diff.
        """
        name = provider.identifier()
        if not name.strip():
            raise ProviderError("a provider must declare a non-empty identifier to be registered")
        if name in self._by_identifier:
            raise ProviderError(
                f"a provider identified as {name!r} is already registered; replacing it silently "
                "would make the discovered population depend on import order"
            )
        self._by_identifier[name] = provider
        return provider

    def resolve(self, identifier: str) -> DiscoveryProvider:
        """By name. FOR EVIDENCE AND TESTS — a measurement resolves by capability instead."""
        try:
            return self._by_identifier[identifier]
        except KeyError:
            raise ProviderError(
                f"no provider is registered as {identifier!r}; registered: "
                f"{', '.join(self.identifiers()) or '<none>'}"
            ) from None

    def identifiers(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_identifier))

    def providers(self) -> tuple[DiscoveryProvider, ...]:
        """Highest priority first, then by identifier so the order is total and reproducible."""
        return tuple(
            sorted(
                self._by_identifier.values(),
                key=lambda p: (-_priority_of(p), p.identifier()),
            )
        )

    def supporting(self, *required: Capability) -> tuple[DiscoveryProvider, ...]:
        """Every provider declaring all of ``required``, in resolution order."""
        return tuple(p for p in self.providers() if not p.capabilities().missing(*required))

    def resolve_capable(self, *required: Capability) -> Resolution:
        """THE RESOLUTION A MEASUREMENT USES. By capability, so no call site names a provider.

        Raises when nothing matches, and the refusal names every provider considered and what each
        was missing — so a failure is actionable without reading this file.
        """
        rejected: list[tuple[str, tuple[str, ...]]] = []
        for provider in self.providers():
            gap = provider.capabilities().missing(*required)
            if not gap:
                return Resolution(provider, required, tuple(rejected))
            rejected.append((provider.identifier(), tuple(c.name for c in gap)))
        raise ProviderError(
            "no registered provider declares "
            f"{', '.join(c.name for c in required) or '<no capability>'}; considered "
            + (
                "; ".join(f"{name} (missing {', '.join(gap)})" for name, gap in rejected)
                or "<no providers registered>"
            )
        )

    def capability_matrix(self) -> dict[str, list[str]]:
        """``provider -> declared capabilities``. Deliverable 1's capability reporting."""
        return {p.identifier(): list(p.capabilities().names()) for p in self.providers()}

    def report(self) -> dict[str, object]:
        """The registry, as evidence. Every provider self-describes; nothing here describes them."""
        return {
            "providers": [_report_of(p) for p in self.providers()],
            "capability_matrix": self.capability_matrix(),
        }

    def __len__(self) -> int:
        return len(self._by_identifier)

    def __contains__(self, identifier: object) -> bool:
        return isinstance(identifier, str) and identifier in self._by_identifier


def _priority_of(provider: DiscoveryProvider) -> int:
    """A provider declaring no priority sorts at zero. Duck-typed, so the Protocol stays thin."""
    return int(getattr(provider, "priority", 0))


def _report_of(provider: DiscoveryProvider) -> dict[str, object]:
    """Prefer a provider's own report; fall back to the contract's four questions.

    A third-party provider implementing only the Protocol still appears in evidence, which is the
    test of whether ``BaseProvider`` is genuinely optional.
    """
    own = getattr(provider, "report", None)
    if callable(own):
        return dict(own())
    return {
        "identifier": provider.identifier(),
        "priority": _priority_of(provider),
        "metadata": provider.metadata().as_record(),
        **provider.capabilities().as_record(),
    }
