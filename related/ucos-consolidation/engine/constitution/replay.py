"""UCOS-ARE-000001 — the Autonomous Replay Engine (Requirement 006).

After a mutation, six things must happen before anything may be certified: recompute,
revalidate, reverify, recertify, reregister, replay. They must happen *repeatedly*, until
two consecutive rounds are byte-identical — the deterministic fixed point.

The reason it is a loop rather than a sequence is that recomputation can move the thing it
recomputes. Revalidating a population can surface a subject whose recertification changes
a digest that the next revalidation reads. A single pass would certify a state that its
own rules had already invalidated. Iterating to a fixed point is what makes the certified
state *stable under its own rules*, which is the only sense in which certification means
anything.

Divergence is a defect, not a retry
-----------------------------------
Every act in this package is pure over its inputs, so a correct system converges at round
two: round one computes, round two reproduces. A run that does not converge within its
bound has a non-deterministic act somewhere in it — something read a clock, an environment
variable, a set iteration order or a filesystem — and
:func:`require_fixed_point` refuses rather than looping harder, naming the round digests
so the divergent act can be found.

Bounded on purpose
------------------
``max_rounds`` is small by default. An unbounded loop would turn a determinism defect into
a hang, and a hang is the one failure mode that produces no evidence at all.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.constitution import authority as authority_graph
from engine.constitution import dependency as dependency_graph
from engine.constitution import legality as legality_engine
from engine.constitution import planner as execution_planner
from engine.constitution.errors import ReplayDivergence
from engine.constitution.metadata import Population
from engine.uckp.canonical import content_hash

#: The identity of the replay engine this module realises.
REPLAY_ENGINE_ID = "UCOS-ARE-000001"

#: Versioned so acts can be *added* without any prior replay record changing meaning.
REPLAY_VERSION = "1.0.0"

#: The default convergence bound. Two rounds prove a fixed point; more than a handful
#: proves a determinism defect, so the bound is small enough to fail fast and large
#: enough that a legitimately layered recomputation is never cut short.
DEFAULT_MAX_ROUNDS = 8


@dataclass(frozen=True, slots=True)
class Act:
    """One recomputation act, and the function that computes its digest over a state."""

    name: str
    statement: str
    compute: Callable[[Population], str]

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "statement": self.statement}


def _recompute(population: Population) -> str:
    """Rebuild the constitutional graph from the declarations."""
    return dependency_graph.build(population).digest()


def _revalidate(population: Population) -> str:
    """Re-prove every legality obligation over every subject."""
    graph = dependency_graph.build(population)
    return legality_engine.assess(population, graph).digest()


def _reverify(population: Population) -> str:
    """Re-measure the authority graph for circularity and self-attestation."""
    graph = dependency_graph.build(population)
    return authority_graph.analyse(population, graph).digest()


def _recertify(population: Population) -> str:
    """Re-derive the execution plan — the certified artefact of a constitutional state."""
    return execution_planner.plan(population).digest()


def _reregister(population: Population) -> str:
    """Re-take the identity of the registered population itself."""
    return population.digest()


#: The recomputation acts, in the order Requirement 006 names them (DATA — extend by
#: appending). No function below branches on an act name, so a seventh act is one entry.
REPLAY_ACTS: tuple[Act, ...] = (
    Act("recompute", "the constitutional graph is rebuilt from the declarations", _recompute),
    Act("revalidate", "every legality obligation is re-proven", _revalidate),
    Act("reverify", "the authority graph is re-measured", _reverify),
    Act("recertify", "the execution plan is re-derived", _recertify),
    Act("reregister", "the registered population is re-identified", _reregister),
)


@dataclass(frozen=True, slots=True)
class Round:
    """One complete recomputation pass and the digest it produced."""

    index: int
    act_digests: Mapping[str, str]
    digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "act_digests": {k: self.act_digests[k] for k in sorted(self.act_digests)},
            "digest": self.digest,
        }


@dataclass(frozen=True, slots=True)
class ReplayRecord:
    """The record of a convergence attempt: every round, and whether it settled."""

    engine_id: str
    rounds: tuple[Round, ...]
    fixed_point: bool
    max_rounds: int

    @property
    def converged_at(self) -> int:
        """The round index at which two consecutive rounds matched, or ``-1``."""
        return self.rounds[-1].index if self.fixed_point and self.rounds else -1

    @property
    def final_digest(self) -> str:
        """The digest of the settled state — empty when it never settled."""
        return self.rounds[-1].digest if self.fixed_point and self.rounds else ""

    @property
    def status(self) -> str:
        return "FIXED-POINT" if self.fixed_point else "DIVERGENT"

    def divergent_acts(self) -> tuple[str, ...]:
        """The acts whose digest differed between the last two rounds, ordered.

        This is what a caller wants when convergence fails: not "it diverged" but *which
        act* is not a function of its input.
        """
        if len(self.rounds) < 2:
            return ()
        previous, current = self.rounds[-2], self.rounds[-1]
        return tuple(
            sorted(
                name
                for name in current.act_digests
                if previous.act_digests.get(name) != current.act_digests[name]
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-replay",
            "version": REPLAY_VERSION,
            "engine_id": self.engine_id,
            "status": self.status,
            "fixed_point": self.fixed_point,
            "converged_at": self.converged_at,
            "final_digest": self.final_digest,
            "round_count": len(self.rounds),
            "max_rounds": self.max_rounds,
            "divergent_acts": list(self.divergent_acts()),
            "acts": [a.to_dict() for a in REPLAY_ACTS],
            "rounds": [r.to_dict() for r in self.rounds],
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def _round(population: Population, index: int, acts: Sequence[Act]) -> Round:
    """Run every act once over ``population`` and digest the whole pass.

    An act that raises does not abort the round: its digest becomes the digest of the
    failure, which is stable if the failure is deterministic. A run that fails the same
    way twice is still a fixed point — an unstable *failure*, by contrast, is a
    determinism defect and must be reported as divergence rather than hidden behind a
    traceback from round one.
    """
    digests: dict[str, str] = {}
    for act in acts:
        try:
            digests[act.name] = act.compute(population)
        except Exception as exc:  # noqa: BLE001 - a stable failure is still a fixed point
            digests[act.name] = content_hash(
                {"act": act.name, "error": type(exc).__name__, "message": str(exc)}
            )
    return Round(
        index=index,
        act_digests=digests,
        digest=content_hash({"acts": {k: digests[k] for k in sorted(digests)}}),
    )


def converge(
    population: Population,
    *,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    acts: Sequence[Act] = REPLAY_ACTS,
) -> ReplayRecord:
    """Recompute, revalidate, reverify, recertify, reregister and replay to a fixed point.

    Returns the record whether or not it converged; :func:`require_fixed_point` is the
    fail-closed form. Reporting divergence is itself evidence, so this never raises on a
    divergent run.
    """
    if max_rounds < 2:
        raise ReplayDivergence(
            "a fixed point cannot be observed in fewer than two rounds",
            engine_id=REPLAY_ENGINE_ID,
            max_rounds=max_rounds,
        )
    rounds: list[Round] = []
    for index in range(1, max_rounds + 1):
        current = _round(population, index, acts)
        rounds.append(current)
        if len(rounds) >= 2 and rounds[-2].digest == current.digest:
            return ReplayRecord(
                engine_id=REPLAY_ENGINE_ID,
                rounds=tuple(rounds),
                fixed_point=True,
                max_rounds=max_rounds,
            )
    return ReplayRecord(
        engine_id=REPLAY_ENGINE_ID,
        rounds=tuple(rounds),
        fixed_point=False,
        max_rounds=max_rounds,
    )


def require_fixed_point(
    population: Population,
    *,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    acts: Sequence[Act] = REPLAY_ACTS,
) -> ReplayRecord:
    """Converge and refuse unless a deterministic fixed point was reached.

    The gate that stands between a mutation and a certificate. Nothing in this package
    certifies a state that has not been through it.

    Raises:
        ReplayDivergence: the state did not settle within ``max_rounds``; the divergent
            acts and every round digest are named.
    """
    record = converge(population, max_rounds=max_rounds, acts=acts)
    if not record.fixed_point:
        raise ReplayDivergence(
            "replay did not reach a deterministic fixed point; certification is void",
            engine_id=REPLAY_ENGINE_ID,
            clause="CEL-06",
            max_rounds=max_rounds,
            divergent_acts=list(record.divergent_acts()),
            round_digests=[r.digest for r in record.rounds],
        )
    return record


def to_document() -> dict[str, Any]:
    """The replay model as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-replay-model",
        "version": REPLAY_VERSION,
        "engine_id": REPLAY_ENGINE_ID,
        "acts": [a.to_dict() for a in REPLAY_ACTS],
        "default_max_rounds": DEFAULT_MAX_ROUNDS,
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "DEFAULT_MAX_ROUNDS",
    "REPLAY_ACTS",
    "REPLAY_ENGINE_ID",
    "REPLAY_VERSION",
    "Act",
    "ReplayRecord",
    "Round",
    "converge",
    "digest",
    "require_fixed_point",
    "to_document",
]
