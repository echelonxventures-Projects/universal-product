"""UCOS Ω∞ Universal Reference Architecture — the capability registry (Deliverable 3).

AUTHORITY = NONE (DERIVED TRUTH).

WHY A CAPABILITY REGISTRY IS THE FIRST FILE. Ω∞ Rule 3 requires a previously unknown reference
domain to be introduced by registration alone. A registration that carried no statement of what the
new thing CAN DO would force every consumer to guess, and a consumer that guesses is a consumer with
a hardcoded assumption — the assumption has simply moved from the producer to the reader.

    domains.declare(martian_chronology)     ← registered. But can it order? can it encode?
                                              can it transform? Nothing says. So callers assume.

THIS IS THE DEFECT Ω∞ RULE 3 IS USUALLY VIOLATED BY. Moving ``datetime.now()`` behind
``ClockProvider.now()`` relocates the assumption unless the provider also declares what it does not
offer. A clock that cannot order concurrent events, a codec that cannot encode a symbol, a storage
provider that cannot enumerate — each must be able to SAY SO, or a caller will discover it by
producing a wrong answer.

CAPABILITIES ARE OPEN AND UNQUANTIFIED. ``WELL_KNOWN`` below is a convenience for readers and a
canonicalisation aid for the registry. Nothing in this package iterates it, branches on it,
validates against it or requires membership in it. A capability a caller invents at runtime works
identically, which is the property that makes the list permanently safe to be incomplete — and it
permanently is.

CLOSED TO REDEFINITION, OPEN TO EXTENSION. One name with two meanings is worse than two names,
because a requirement for ``ORDERED`` would be satisfied by a provider that meant something else and
the requirement would silently stop being a requirement.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass


class CapabilityError(RuntimeError):
    """A capability was required and not declared, or declared inconsistently.

    RAISED, NEVER DEFAULTED. Returning ``False`` for "does this provider support X" when the
    provider never said either way converts "unknown" into "no", and a caller then proceeds on a
    fact nobody established.
    """


@dataclass(frozen=True, order=True)
class Capability:
    """One self-declared property of a provider or a domain.

    ``order=True`` so capability sets sort deterministically. Every document this architecture emits
    is compared byte-for-byte, and an unordered set would break that for a reason having nothing to
    do with governance.
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
# domains this package ships need in order to describe themselves. A domain for a concept nobody has
# named declares its own.

ORDERABLE = Capability(
    "ORDERABLE",
    "Values in this domain can be compared, though not necessarily totally: the comparison may "
    "answer that two values are concurrent or that the question is unanswerable.",
)
TOTALLY_ORDERABLE = Capability(
    "TOTALLY_ORDERABLE",
    "Every pair of values in this domain is comparable and exactly one of precedes, follows or "
    "coincides holds. A STRONGER claim than ORDERABLE and rarely true outside a single observer.",
)
ENCODABLE = Capability(
    "ENCODABLE",
    "Values in this domain can be reduced to bytes by a registered codec, so they survive storage "
    "in a system this architecture does not own.",
)
IDENTIFIABLE = Capability(
    "IDENTIFIABLE",
    "Values in this domain have a stable digest under a registered identity provider, so two "
    "records can be compared without comparing their contents.",
)
TRANSFORMABLE = Capability(
    "TRANSFORMABLE",
    "At least one declared transformation maps values of this domain into another domain. Says "
    "nothing about whether the transformation is lossless or invertible.",
)
QUANTITATIVE = Capability(
    "QUANTITATIVE",
    "Values carry magnitude, so differences and ratios are meaningful. ITS ABSENCE IS THE POINT: a "
    "domain of symbols, grades or lattice elements is measurable without being numeric, and a "
    "measurement architecture that required this capability would exclude every such system.",
)
ENUMERABLE = Capability(
    "ENUMERABLE",
    "The population of values or artifacts can be listed. A storage or discovery property, and one "
    "an append-only ledger or an infinite space may honestly lack.",
)
ADDRESSABLE = Capability(
    "ADDRESSABLE",
    "An individual value or artifact can be fetched by a locator without enumerating the whole "
    "population.",
)
MUTABLE = Capability(
    "MUTABLE",
    "Stored values can be overwritten. Declared so an append-only register can REFUSE a storage "
    "provider that offers it, rather than discovering the overwrite in an audit.",
)
APPEND_ONLY = Capability(
    "APPEND_ONLY",
    "Stored values can be added and never altered or removed. The property a governance register "
    "requires of its storage, stated by the storage rather than hoped for by the register.",
)
REPRODUCIBLE = Capability(
    "REPRODUCIBLE",
    "Two reads of the same subject under unchanged inputs produce identical values, so evidence "
    "built on this provider can be compared byte-for-byte across runs and machines.",
)
FRAME_RELATIVE = Capability(
    "FRAME_RELATIVE",
    "Values are meaningful only relative to a declared reference frame, so two values from "
    "different frames are not comparable without a declared relation between the frames.",
)
AUTHORITY_BEARING = Capability(
    "AUTHORITY_BEARING",
    "The provider carries ownership information of its own, which an authority resolution may "
    "consult instead of inferring ownership from structure.",
)

#: Registered eagerly so canonical spellings exist before any provider is constructed. A convenience
#: for readers and for the registry's conflict check; NOT a constraint on providers.
WELL_KNOWN: tuple[Capability, ...] = (
    ADDRESSABLE,
    APPEND_ONLY,
    AUTHORITY_BEARING,
    ENCODABLE,
    ENUMERABLE,
    FRAME_RELATIVE,
    IDENTIFIABLE,
    MUTABLE,
    ORDERABLE,
    QUANTITATIVE,
    REPRODUCIBLE,
    TOTALLY_ORDERABLE,
    TRANSFORMABLE,
)


class CapabilityRegistry:
    """Canonical name -> ``Capability``. Open for extension, closed to redefinition."""

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
                "with two meanings makes every requirement on it unenforceable; choose a different "
                "name"
            )
        return existing

    def declare_name(self, name: str, description: str) -> Capability:
        """Declare from primitives, for a provider assembling its own vocabulary at runtime."""
        return self.declare(Capability(name, description))

    def resolve(self, name: str) -> Capability:
        """The registered capability for a name. An UNKNOWN name raises rather than inventing
        one.
        """
        try:
            return self._by_name[name]
        except KeyError:
            raise CapabilityError(
                f"{name!r} is not a declared capability; declare it before requiring it, so that a "
                "misspelling cannot become a requirement no provider can fail"
            ) from None

    def known(self) -> tuple[Capability, ...]:
        return tuple(sorted(self._by_name.values()))

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


@dataclass(frozen=True)
class CapabilitySet:
    """What one provider or domain declares about itself. Immutable, ordered and answerable.

    THE INTERROGATION SURFACE. ``supports`` answers, ``require`` refuses, ``missing`` explains. A
    consumer needing append-only storage calls ``require(APPEND_ONLY)`` and receives a refusal
    naming the provider — which is the sentence a hardcoded storage layer could never produce,
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
                "requires it, and a capability that was not declared must never be assumed"
            )

    def refuse(self, *forbidden: Capability, subject: str = "this provider") -> None:
        """Refuse if any named capability IS declared. The inverse, and it is genuinely needed.

        An append-only register must reject storage that declares ``MUTABLE``. Without this method a
        caller would express that as ``not supports(MUTABLE)``, which passes for a provider that
        never declared either way — turning "unknown" into "safe".
        """
        present = tuple(sorted(c for c in forbidden if c in self.capabilities))
        if present:
            raise CapabilityError(
                f"{subject} declares {', '.join(c.name for c in present)}, which this operation "
                "forbids; the declaration is what makes the refusal possible before the damage"
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


def default_registry() -> CapabilityRegistry:
    """A registry seeded with the well-known set. Callers build their own rather than sharing one.

    NO PROCESS-WIDE SINGLETON. A shared capability registry would let one deployment's runtime
    declaration alter another's vocabulary, and the open-world verification suite must be able to
    declare capabilities that do not leak into the evidence run.
    """
    return CapabilityRegistry()


__all__ = [
    "ADDRESSABLE",
    "APPEND_ONLY",
    "AUTHORITY_BEARING",
    "ENCODABLE",
    "ENUMERABLE",
    "FRAME_RELATIVE",
    "IDENTIFIABLE",
    "MUTABLE",
    "ORDERABLE",
    "QUANTITATIVE",
    "REPRODUCIBLE",
    "TOTALLY_ORDERABLE",
    "TRANSFORMABLE",
    "WELL_KNOWN",
    "Capability",
    "CapabilityError",
    "CapabilityRegistry",
    "CapabilitySet",
    "default_registry",
]
