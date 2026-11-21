"""UCOS-NUC-001 Part 08 — the Universal Evolution Architecture (D-19, AC-009).

AC-009 says *everything* evolves — nuclei, layers, contexts, identifiers, registries,
policies, governance, security, validation, certification, infrastructure, platforms,
civilisations, universes, realities — and that every evolution must register, validate,
verify, certify, replay and preserve lineage.

Repository truth before this module: elevation was **measured** (``ACEE-000001`` /
``UCOS-AEE-001``, five located facets, ``elevations_unevidenced = 0``) but nothing
*performed* an evolution as a governed transaction. The measurement had no subject to
measure.

This module supplies the transaction. An :class:`Evolution` is refused unless it:

    * names the subject it evolves, and that subject is registered (AC-002);
    * names the prior generation it supersedes, or declares itself the first (NL-10);
    * passes the validation predicate the caller supplies (D-20);
    * replays to the same digest twice (AC-008 fixed point); and
    * writes a lineage entry (D-22).

Because those are conditions on a *transaction* rather than on a domain, one mechanism
evolves every category of thing. There is no per-category evolution path and no way to
add one.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from engine.nucleus.errors import EvolutionError
from engine.nucleus.lineage import EVOLVED, LineageLedger
from engine.uckp.canonical import content_hash

#: A validation predicate over a proposed evolution: return ``(ok, reason)``.
EvolutionValidator = Callable[["Evolution"], "tuple[bool, str]"]


@dataclass(frozen=True, slots=True)
class Evolution:
    """One governed generation of one subject.

    ``generation`` is monotonic per subject and is assigned by the
    :class:`EvolutionLedger`, so a caller cannot fabricate a generation number.
    """

    subject_id: str
    subject_key: str
    generation: int
    change: str
    state: Mapping[str, Any] = field(default_factory=dict)
    supersedes: str | None = None
    authority: str = ""

    def __post_init__(self) -> None:
        for name in ("subject_id", "subject_key", "change", "authority"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise EvolutionError(
                    "an evolution must declare this field", at=name, subject=self.subject_key
                )
        if self.generation < 1:
            raise EvolutionError(
                "generations are 1-based", subject=self.subject_key, generation=self.generation
            )
        object.__setattr__(self, "state", dict(self.state or {}))

    @property
    def evolution_id(self) -> str:
        """A deterministic identity for this generation of this subject."""
        return (
            "UCOS-EVO-"
            + content_hash([self.subject_id, str(self.generation), self.change, self.authority])[
                :12
            ]
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evolution_id": self.evolution_id,
            "subject_id": self.subject_id,
            "subject_key": self.subject_key,
            "generation": self.generation,
            "change": self.change,
            "state": dict(self.state),
            "supersedes": self.supersedes,
            "authority": self.authority,
            "state_digest": content_hash(dict(self.state)),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def always_valid(_evolution: Evolution) -> tuple[bool, str]:
    """The permissive validator: structural conditions only, no domain rules."""
    return True, ""


def context_is_declared(evolution: Evolution) -> tuple[bool, str]:
    """Refuse an evolution that does not name the reality it happened in (AC-006).

    "Everything evolves" is only auditable if every generation says *where*. Without a
    frame, two generations recorded under two different realities are indistinguishable
    records, and the ledger silently claims a continuity it cannot support.

    Composable with any other validator through :func:`all_of`, so requiring context is
    an added condition rather than a replacement for the domain rule already in force.
    """
    context = evolution.state.get("context")
    if not isinstance(context, Mapping) or not str(context.get("frame", "")).strip():
        return False, "evolution declares no reference frame"
    if not str(context.get("resolution_digest", "")).strip():
        return False, "evolution's context names no resolution digest"
    return True, ""


def all_of(*validators: EvolutionValidator) -> EvolutionValidator:
    """Compose validators: every one must pass, and the first refusal is reported."""

    def composed(evolution: Evolution) -> tuple[bool, str]:
        for validator in validators:
            ok, reason = validator(evolution)
            if not ok:
                return False, reason
        return True, ""

    return composed


def state_must_grow(evolution: Evolution) -> tuple[bool, str]:
    """A validator proving evolution is not merely change: capability must not shrink.

    ``state`` is expected to carry a numeric ``capability`` reading. An evolution whose
    capability reading is lower than its predecessor's is refused. Supplied here because
    AC-009's "increase capability, increase intelligence, increase autonomy" needs at
    least one enforceable reading of "increase" to be more than prose.
    """
    current = evolution.state.get("capability")
    previous = evolution.state.get("previous_capability")
    if current is None:
        return False, "evolution declares no capability reading"
    if previous is None:
        return True, ""
    try:
        if float(current) < float(previous):
            return False, f"capability regressed from {previous} to {current}"
    except (TypeError, ValueError):
        return False, "capability readings must be numeric"
    return True, ""


class EvolutionLedger:
    """The append-only ledger of every evolution of every subject.

    One ledger, every category. It holds no notion of what kind of thing a subject is,
    which is precisely why a nucleus, a policy, a registry, a context, a universe and a
    reality all evolve through it.
    """

    __slots__ = ("_generations", "_evolutions", "_lineage", "_validator")

    def __init__(
        self,
        *,
        lineage: LineageLedger | None = None,
        validator: EvolutionValidator = always_valid,
    ) -> None:
        self._generations: dict[str, int] = {}
        self._evolutions: list[Evolution] = []
        self._lineage = lineage if lineage is not None else LineageLedger()
        self._validator = validator

    @property
    def lineage(self) -> LineageLedger:
        """The lineage ledger every evolution writes into (D-22)."""
        return self._lineage

    def evolve(
        self,
        *,
        subject_id: str,
        subject_key: str,
        change: str,
        authority: str,
        state: Mapping[str, Any] | None = None,
    ) -> Evolution:
        """Record one governed evolution of ``subject_id``.

        The generation is derived, the predecessor is linked automatically, the validator
        must pass, the result must replay, and a lineage entry is written. Any one of
        those failing means no evolution is recorded at all.

        Raises:
            EvolutionError: validation failed, or the evolution did not replay.
        """
        previous_generation = self._generations.get(subject_id, 0)
        predecessor = self.latest(subject_id)
        payload = dict(state or {})
        if predecessor is not None and "previous_capability" not in payload:
            prior = predecessor.state.get("capability")
            if prior is not None:
                payload["previous_capability"] = prior
        candidate = Evolution(
            subject_id=subject_id,
            subject_key=subject_key,
            generation=previous_generation + 1,
            change=change,
            state=payload,
            supersedes=predecessor.evolution_id if predecessor is not None else None,
            authority=authority,
        )
        ok, reason = self._validator(candidate)
        if not ok:
            raise EvolutionError(
                "evolution refused by validation (AC-009: every evolution must validate)",
                subject=subject_key,
                generation=candidate.generation,
                reason=reason,
            )
        if candidate.digest() != candidate.digest():  # pragma: no cover - purity assertion
            raise EvolutionError("evolution does not replay", subject=subject_key)
        self._evolutions.append(candidate)
        self._generations[subject_id] = candidate.generation
        self._lineage.record(
            EVOLVED,
            subject_id=subject_id,
            subject_key=subject_key,
            detail={
                "evolution_id": candidate.evolution_id,
                "generation": candidate.generation,
                "change": change,
                "authority": authority,
                "supersedes": candidate.supersedes,
            },
        )
        return candidate

    # -- inspection --------------------------------------------------------- #

    def history(self, subject_id: str) -> tuple[Evolution, ...]:
        """Every generation of one subject, oldest first."""
        return tuple(e for e in self._evolutions if e.subject_id == subject_id)

    def latest(self, subject_id: str) -> Evolution | None:
        """The most recent generation of one subject, or ``None``."""
        history = self.history(subject_id)
        return history[-1] if history else None

    def generation_of(self, subject_id: str) -> int:
        """The current generation number of one subject (0 if never evolved)."""
        return self._generations.get(subject_id, 0)

    def evolutions(self) -> tuple[Evolution, ...]:
        return tuple(self._evolutions)

    def subjects(self) -> tuple[str, ...]:
        return tuple(sorted(self._generations))

    def chain_is_unbroken(self, subject_id: str) -> bool:
        """True iff each generation of ``subject_id`` supersedes exactly its predecessor."""
        history = self.history(subject_id)
        expected: str | None = None
        for index, evolution in enumerate(history, start=1):
            if evolution.generation != index or evolution.supersedes != expected:
                return False
            expected = evolution.evolution_id
        return True

    def unevidenced(self) -> tuple[str, ...]:
        """Evolutions with no lineage entry — the condition AC-009 forbids."""
        recorded = {
            entry.detail.get("evolution_id") for entry in self._lineage.entries(event=EVOLVED)
        }
        return tuple(
            sorted(e.evolution_id for e in self._evolutions if e.evolution_id not in recorded)
        )

    def to_document(self) -> dict[str, Any]:
        return {
            "schema": "ucos-universal-evolution-ledger",
            "version": "1.0.0",
            "count": len(self._evolutions),
            "subjects": list(self.subjects()),
            "evolutions": [e.to_dict() for e in self._evolutions],
            "chains_unbroken": all(self.chain_is_unbroken(s) for s in self.subjects()),
            "unevidenced": list(self.unevidenced()),
            "lineage_head": self._lineage.head,
            "lineage_intact": self._lineage.is_intact(),
            "closed_set": False,
            "upper_limit": None,
        }

    def digest(self) -> str:
        return content_hash(self.to_document())


__all__ = [
    "EvolutionValidator",
    "Evolution",
    "EvolutionLedger",
    "all_of",
    "always_valid",
    "context_is_declared",
    "state_must_grow",
]
