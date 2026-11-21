"""WP-07 — Crypto Agility (PRJ-C2 / ACT-C2).

Algorithm-tagged **multihash** digests, an algorithm registry, crypto version
negotiation, a digest abstraction, witnessed crypto rollover, and forward
compatibility with future algorithms. It realizes **AIF-L22** ("algorithm-tagged
multihash digest sets; witnessed rollover; deprecation only post-rollover; identity
is opaque and survives algorithm breakage") and gap-resolution **A/G5**.

Composition:
    * digests are computed over the **Canonical Content Form** (WP-06,
      :func:`~platform.foundation.canonical.canonical_bytes`), so agility never
      changes *what* is hashed, only *how*;
    * a :class:`Multihash` is **self-describing** (``algorithm:value``): it can
      *represent* a digest for an algorithm this runtime cannot compute (future
      compatibility), and only *verification* requires the algorithm locally — so an
      opaque durable identity (WP-04) is unaffected by any single algorithm's
      breakage (AIF-L22);
    * a :class:`DigestSet` carries several multihashes over the *same* canonical
      bytes; **rollover** widens the set append-only, and an algorithm may be
      **deprecated only after** a successor is active (never leaving zero active).

Deterministic and stdlib-only (TP-04): all hashing uses :mod:`hashlib`; no wall-clock
and no I/O; nothing is written to the certified corpus (DP-03).
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from platform.foundation.canonical import (
    CCF_DEFAULT_PROFILE,
    CanonicalProfile,
    canonical_bytes,
)
from platform.foundation.errors import AlgorithmNegotiationError, CryptoAgilityError
from typing import Any

from engine.foundation.obs.logging import get_logger

_logger = get_logger("foundation.crypto_agility")

#: The self-describing export format tag (semantic version — widens append-only).
CRYPTO_REGISTRY_FORMAT = "ucos-crypto-agility-registry/1.0.0"

#: The multihash tag separator (``algorithm:hexvalue``).
MULTIHASH_SEPARATOR = ":"


def _hash_bytes(algorithm: str, data: bytes) -> str:
    """Hash ``data`` with a hashlib ``algorithm``; fail closed if unavailable."""
    try:
        digest = hashlib.new(algorithm)
    except (ValueError, TypeError) as exc:
        raise CryptoAgilityError(
            "hash algorithm is not available in this runtime", algorithm=algorithm
        ) from exc
    digest.update(data)
    return digest.hexdigest()


class AlgorithmStatus(str, Enum):
    """The lifecycle of a registered algorithm (append-only, AIF-L17)."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"  # only after a successor is active (post-rollover)


@dataclass(frozen=True, slots=True)
class HashAlgorithm:
    """An immutable descriptor of a hash algorithm (multihash-tagged).

    ``strength`` is a deterministic preference rank (higher wins negotiation).
    ``digest_size`` is resolved from the runtime's ``hashlib`` so a bogus algorithm
    is rejected at registration (fails closed).
    """

    name: str
    strength: int
    digest_size: int

    @classmethod
    def create(cls, name: str, strength: int) -> HashAlgorithm:
        if not isinstance(name, str) or not name:
            raise CryptoAgilityError("algorithm name is required")
        if not isinstance(strength, int) or strength <= 0:
            raise CryptoAgilityError("algorithm strength must be a positive int", name=name)
        try:
            size = hashlib.new(name).digest_size
        except (ValueError, TypeError) as exc:
            raise CryptoAgilityError("unknown hash algorithm", algorithm=name) from exc
        return cls(name=name, strength=strength, digest_size=size)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "strength": self.strength, "digest_size": self.digest_size}


#: The pinned default algorithm set (weakest→strongest by ``strength``). Widens
#: append-only via rollover; sha256 is the pinned CCF default (WP-06).
DEFAULT_ALGORITHMS: tuple[tuple[str, int], ...] = (
    ("sha256", 10),
    ("sha3_256", 20),
    ("sha512", 30),
)


@dataclass(frozen=True, slots=True)
class Multihash:
    """A self-describing, algorithm-tagged digest (``algorithm:hexvalue``).

    Representable even for an algorithm this runtime cannot compute (future
    compatibility); verification requires the algorithm locally.
    """

    algorithm: str
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.algorithm, str) or not self.algorithm:
            raise CryptoAgilityError("multihash algorithm is required")
        if MULTIHASH_SEPARATOR in self.algorithm:
            raise CryptoAgilityError("algorithm must not contain the separator")
        if not isinstance(self.value, str) or not self.value:
            raise CryptoAgilityError("multihash value is required")

    @property
    def tag(self) -> str:
        """The self-describing ``algorithm:value`` render."""
        return f"{self.algorithm}{MULTIHASH_SEPARATOR}{self.value}"

    @classmethod
    def parse(cls, tag: str) -> Multihash:
        """Parse a ``algorithm:value`` tag (fails closed on a malformed tag)."""
        if not isinstance(tag, str) or MULTIHASH_SEPARATOR not in tag:
            raise CryptoAgilityError("malformed multihash tag", tag=tag)
        algorithm, _, value = tag.partition(MULTIHASH_SEPARATOR)
        return cls(algorithm=algorithm, value=value)

    def verify_bytes(self, data: bytes) -> bool:
        """True iff ``data`` hashes to this multihash (requires the algorithm)."""
        return _hash_bytes(self.algorithm, data) == self.value

    def to_dict(self) -> dict[str, Any]:
        return {"algorithm": self.algorithm, "value": self.value}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Multihash:
        if not isinstance(data, Mapping):
            raise CryptoAgilityError("multihash record must be a mapping")
        try:
            return cls(algorithm=data["algorithm"], value=data["value"])
        except (KeyError, TypeError) as exc:
            raise CryptoAgilityError("multihash record is missing required fields") from exc


def compute_multihash(
    content: Any, algorithm: str, *, profile: CanonicalProfile | None = None
) -> Multihash:
    """Compute a multihash of ``content`` over its CCF (WP-06) with ``algorithm``."""
    data = canonical_bytes(content, profile)
    return Multihash(algorithm=algorithm, value=_hash_bytes(algorithm, data))


@dataclass(frozen=True, slots=True)
class RolloverRecord:
    """A witnessed crypto-rollover event: a new algorithm becomes active (AIF-L22)."""

    algorithm: str
    strength: int
    witness: str

    def to_dict(self) -> dict[str, Any]:
        return {"algorithm": self.algorithm, "strength": self.strength, "witness": self.witness}


class AlgorithmRegistry:
    """An append-only registry of hash algorithms with agile lifecycle (AIF-L22)."""

    __slots__ = ("_algorithms", "_status", "_order", "_rollovers")

    def __init__(self, *, seed_defaults: bool = True) -> None:
        self._algorithms: dict[str, HashAlgorithm] = {}
        self._status: dict[str, AlgorithmStatus] = {}
        self._order: list[str] = []
        self._rollovers: list[RolloverRecord] = []
        if seed_defaults:
            for name, strength in DEFAULT_ALGORITHMS:
                self.register(HashAlgorithm.create(name, strength))

    def register(self, algorithm: HashAlgorithm) -> HashAlgorithm:
        """Register an algorithm as ACTIVE; an existing name is not overwritten."""
        if not isinstance(algorithm, HashAlgorithm):
            raise CryptoAgilityError("register expects a HashAlgorithm")
        existing = self._algorithms.get(algorithm.name)
        if existing is not None:
            if existing != algorithm:
                raise CryptoAgilityError(
                    "algorithm already registered with different parameters",
                    algorithm=algorithm.name,
                )
            return existing
        self._algorithms[algorithm.name] = algorithm
        self._status[algorithm.name] = AlgorithmStatus.ACTIVE
        self._order.append(algorithm.name)
        return algorithm

    def __contains__(self, name: str) -> bool:
        return name in self._algorithms

    def __len__(self) -> int:
        return len(self._order)

    def get(self, name: str) -> HashAlgorithm:
        algorithm = self._algorithms.get(name)
        if algorithm is None:
            raise CryptoAgilityError("no such algorithm", algorithm=name)
        return algorithm

    def status(self, name: str) -> AlgorithmStatus:
        self.get(name)
        return self._status[name]

    @property
    def rollovers(self) -> tuple[RolloverRecord, ...]:
        return tuple(self._rollovers)

    def active_algorithms(self) -> tuple[HashAlgorithm, ...]:
        """Active algorithms, strongest first (deterministic tie-break by name)."""
        active = [
            self._algorithms[n] for n in self._order if self._status[n] is AlgorithmStatus.ACTIVE
        ]
        return tuple(sorted(active, key=lambda a: (-a.strength, a.name)))

    def preferred(self) -> HashAlgorithm:
        """The strongest active algorithm (fails closed if none active)."""
        active = self.active_algorithms()
        if not active:
            raise AlgorithmNegotiationError("no active hash algorithm")
        return active[0]

    def negotiate(self, peer_supported: Iterable[str]) -> HashAlgorithm:
        """Return the strongest active algorithm also supported by a peer.

        Deterministic (preference by strength, tie-break by name); fails closed if
        there is no common active algorithm (AIF-L22 crypto version negotiation).
        """
        peer = set(peer_supported)
        for algorithm in self.active_algorithms():
            if algorithm.name in peer:
                return algorithm
        raise AlgorithmNegotiationError(
            "no common active hash algorithm with peer", peer=sorted(peer)
        )

    def rollover(self, name: str, strength: int, *, witness: str) -> RolloverRecord:
        """Introduce a new active algorithm under a witnessed rollover (AIF-L22)."""
        if not isinstance(witness, str) or not witness.strip():
            raise CryptoAgilityError("rollover must name a witness", algorithm=name)
        if name in self._algorithms:
            raise CryptoAgilityError("algorithm already registered", algorithm=name)
        self.register(HashAlgorithm.create(name, strength))
        record = RolloverRecord(algorithm=name, strength=strength, witness=witness)
        self._rollovers.append(record)
        _logger.info("foundation.crypto_agility.rollover", algorithm=name, witness=witness)
        return record

    def deprecate(self, name: str) -> None:
        """Deprecate an algorithm — only permitted post-rollover (≥1 active remains).

        Deprecation only after rollover (AIF-L22): at least one *other* algorithm
        must remain active, so the digest set never loses all verifiable algorithms.
        """
        self.get(name)
        if self._status[name] is AlgorithmStatus.DEPRECATED:
            return
        others_active = any(
            n != name and self._status[n] is AlgorithmStatus.ACTIVE for n in self._order
        )
        if not others_active:
            raise AlgorithmNegotiationError(
                "cannot deprecate the only active algorithm (rollover first)",
                algorithm=name,
            )
        self._status[name] = AlgorithmStatus.DEPRECATED
        _logger.info("foundation.crypto_agility.deprecated", algorithm=name)

    def export(self) -> dict[str, Any]:
        return {
            "registry_format": CRYPTO_REGISTRY_FORMAT,
            "algorithms": [
                {**self._algorithms[n].to_dict(), "status": self._status[n].value}
                for n in self._order
            ],
            "rollovers": [r.to_dict() for r in self._rollovers],
        }


@dataclass(frozen=True, slots=True)
class DigestSet:
    """An algorithm-agile set of multihashes over the *same* canonical bytes (AIF-L22).

    Rollover widens the set append-only; verification passes iff every carried
    multihash (whose algorithm is available locally) recomputes — so the identity
    survives any single algorithm's breakage as long as one strong algorithm holds.
    """

    profile_id: str
    digests: tuple[Multihash, ...]

    @classmethod
    def compute(
        cls,
        content: Any,
        algorithms: Iterable[str],
        *,
        profile: CanonicalProfile | None = None,
    ) -> DigestSet:
        """Compute a digest set over the CCF of ``content`` for each algorithm."""
        names = list(dict.fromkeys(algorithms))
        if not names:
            raise CryptoAgilityError("a digest set requires at least one algorithm")
        data = canonical_bytes(content, profile)
        digests = tuple(
            sorted(
                (Multihash(n, _hash_bytes(n, data)) for n in names),
                key=lambda m: m.algorithm,
            )
        )
        prof_id = profile.profile_id if profile is not None else CCF_DEFAULT_PROFILE
        return cls(profile_id=prof_id, digests=digests)

    @property
    def algorithms(self) -> tuple[str, ...]:
        return tuple(m.algorithm for m in self.digests)

    def by_algorithm(self, name: str) -> Multihash:
        for multihash in self.digests:
            if multihash.algorithm == name:
                return multihash
        raise CryptoAgilityError("no digest for algorithm", algorithm=name)

    def verify(self, content: Any, *, profile: CanonicalProfile | None = None) -> bool:
        """True iff every carried multihash recomputes over the content's CCF."""
        data = canonical_bytes(content, profile)
        return all(m.verify_bytes(data) for m in self.digests)

    def verify_with(
        self, content: Any, algorithm: str, *, profile: CanonicalProfile | None = None
    ) -> bool:
        """Verify a single algorithm's multihash (agile per-algorithm verification)."""
        data = canonical_bytes(content, profile)
        return self.by_algorithm(algorithm).verify_bytes(data)

    def rolled_over(
        self, content: Any, algorithm: str, *, profile: CanonicalProfile | None = None
    ) -> DigestSet:
        """Return a widened set with ``algorithm`` added (append-only rollover)."""
        if algorithm in self.algorithms:
            raise CryptoAgilityError("algorithm already in digest set", algorithm=algorithm)
        data = canonical_bytes(content, profile)
        widened = (*self.digests, Multihash(algorithm, _hash_bytes(algorithm, data)))
        return DigestSet(
            profile_id=self.profile_id,
            digests=tuple(sorted(widened, key=lambda m: m.algorithm)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "digests": [m.to_dict() for m in self.digests],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> DigestSet:
        if not isinstance(data, Mapping):
            raise CryptoAgilityError("digest-set record must be a mapping")
        try:
            digests = tuple(Multihash.from_dict(d) for d in data["digests"])
            profile_id = data["profile_id"]
        except (KeyError, TypeError) as exc:
            raise CryptoAgilityError("digest-set record is missing required fields") from exc
        if not digests:
            raise CryptoAgilityError("a digest set requires at least one algorithm")
        return cls(profile_id=profile_id, digests=digests)


def default_algorithm_registry() -> AlgorithmRegistry:
    """Return a registry seeded with the pinned default algorithm set."""
    return AlgorithmRegistry()


__all__ = [
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
]
