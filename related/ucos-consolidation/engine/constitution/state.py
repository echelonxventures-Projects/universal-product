"""UCOS-DPE-000001 — the Dirty State Prevention Engine (Requirement 007).

A measurement is a claim about a state. If the state was moving while the claim was made,
the claim describes something that never existed — and a certificate over it certifies
nothing. Requirement 007 prohibits five acts against dirty state: verification,
certification, registration, measurement and governance.

The mechanism is a **seal**. :class:`StateSeal` binds a digest of the population to the
moment it was committed; every guarded act names the seal it read. Two things follow, and
they are the whole point:

    * a seal taken while a mutation is open is *born* dirty and no guarded act accepts it,
      so intermediate state cannot be certified even by a caller who wants to;
    * a seal whose digest no longer matches the population it was taken from is **stale**,
      which catches the subtler failure of measuring a state, mutating it, and then
      certifying against the measurement.

Determinism, not time
---------------------
A seal carries no timestamp. Freshness is decided by *digest equality with the state being
acted on*, never by wall-clock ordering — which is why a sealed act replays identically in
CI, on a laptop and at a commit taken a year later. There is no clock in this module.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from typing import Any

from engine.constitution.errors import DirtyStateViolation
from engine.constitution.metadata import Population
from engine.uckp.canonical import content_hash

#: The identity of the dirty state prevention engine this module realises.
ENGINE_ID = "UCOS-DPE-000001"

#: Versioned so guarded acts can be *added* without prior seals changing meaning.
STATE_VERSION = "1.0.0"

#: The acts that may be performed only against committed state (DATA — append to extend).
GUARDED_ACTS: tuple[str, ...] = (
    "verify",
    "certify",
    "register",
    "measure",
    "govern",
)


@dataclass(frozen=True, slots=True)
class StateSeal:
    """The identity of a constitutionally committed state.

    ``committed`` is False for exactly as long as a mutation is open over the state. A
    seal is not a lock — it does not prevent the mutation — it is the evidence a later
    act needs in order to prove it did not read through one.
    """

    engine_id: str
    digest: str
    subject_count: int
    committed: bool = True
    provenance: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def of(cls, population: Population, *, committed: bool = True, **provenance: Any) -> StateSeal:
        """Seal ``population`` at its current content digest."""
        return cls(
            engine_id=ENGINE_ID,
            digest=population.digest(),
            subject_count=len(population),
            committed=committed,
            provenance={k: provenance[k] for k in sorted(provenance)},
        )

    @property
    def dirty(self) -> bool:
        """True iff this seal was taken over a state with a mutation open."""
        return not self.committed

    def matches(self, population: Population) -> bool:
        """True iff ``population`` is still exactly the state this seal was taken over."""
        return self.digest == population.digest()

    def opened(self) -> StateSeal:
        """The same seal, marked dirty — what a mutation gateway holds while it works."""
        return replace(self, committed=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-state-seal",
            "version": STATE_VERSION,
            "engine_id": self.engine_id,
            "digest": self.digest,
            "subject_count": self.subject_count,
            "committed": self.committed,
            "provenance": dict(self.provenance),
        }

    def seal_digest(self) -> str:
        return content_hash(self.to_dict())


def guard(
    seal: StateSeal,
    population: Population,
    *,
    act: str,
    acts: Sequence[str] = GUARDED_ACTS,
) -> StateSeal:
    """Admit ``act`` against ``population`` under ``seal``, or refuse it.

    Every guarded act in this package passes through here, so the five prohibitions of
    Requirement 007 are one function rather than five remembered rules.

    An act this module does not guard is admitted rather than refused: the guarded set is
    open by declaration, and refusing unknown acts would make :data:`GUARDED_ACTS` a
    closed vocabulary of everything a caller is allowed to do — a far larger claim than
    "these five acts require committed state".

    Raises:
        DirtyStateViolation: the seal is dirty (a mutation was open), or stale (the state
            has moved since it was taken).
    """
    if act not in acts:
        return seal
    if seal.dirty:
        raise DirtyStateViolation(
            f"{act} refused: the state was not constitutionally committed when sealed",
            engine_id=ENGINE_ID,
            act=act,
            clause="CEL-07",
            seal=seal.to_dict(),
        )
    if not seal.matches(population):
        raise DirtyStateViolation(
            f"{act} refused: the state has moved since it was sealed",
            engine_id=ENGINE_ID,
            act=act,
            clause="CEL-07",
            sealed_digest=seal.digest,
            current_digest=population.digest(),
        )
    return seal


def require_committed(seal: StateSeal, population: Population, *, act: str) -> StateSeal:
    """Guard ``act`` unconditionally, whether or not it is in the declared guarded set.

    For a caller that knows its act reads state and wants the prohibition applied without
    first registering the act's name.
    """
    return guard(seal, population, act=act, acts=(act,))


@contextmanager
def mutating(population: Population) -> Iterator[StateSeal]:
    """Hold an open mutation over ``population``: everything sealed inside is dirty.

    Used by :mod:`engine.constitution.gateway` to make CEL-07 structural — code inside
    the block *cannot* obtain a clean seal, so it cannot certify, register, verify,
    measure or govern the half-built state, however it is written.
    """
    yield StateSeal.of(population, committed=False, reason="mutation-open")


def commit(population: Population, **provenance: Any) -> StateSeal:
    """Seal ``population`` as constitutionally committed state.

    The only way to obtain a clean seal. Called at the end of the gateway pipeline, after
    replay has reached a fixed point — never during.
    """
    return StateSeal.of(population, committed=True, **provenance)


def to_document() -> dict[str, Any]:
    """The prohibition set as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-dirty-state-prevention",
        "version": STATE_VERSION,
        "engine_id": ENGINE_ID,
        "guarded_acts": list(GUARDED_ACTS),
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "ENGINE_ID",
    "GUARDED_ACTS",
    "STATE_VERSION",
    "StateSeal",
    "commit",
    "digest",
    "guard",
    "mutating",
    "require_committed",
    "to_document",
]
