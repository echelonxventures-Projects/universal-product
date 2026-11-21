"""UCOS-CTRL-000001 — Universal Evolution Engine (Wave 5).

The Version Engine records *what* each thing is. This engine records *how it got
there*: the ordered sequence of observations, the delta between consecutive ones,
and — the part a plain change log never answers — whether each delta was an
improvement or a regression.

That judgement cannot be guessed from two strings, so it is declared. A dimension
registers the ranking of its values (``UNGOVERNED`` < ``NOT-GOVERNED`` <
``GOVERNED``), and thereafter every transition in that dimension is classified
against it. Where a dimension has no declared ranking the engine says ``MODIFIED``
and declines to editorialise, which is the honest answer rather than a coin flip.

Five dimensions ship declared — capability, architecture, governance,
certification and version — and a specialised deployment registers more without
touching this module.

Replay is deterministic by construction. The engine keeps the observation log,
not just its conclusions, so :meth:`EvolutionEngine.replay` re-folds the log from
empty and reproduces the identical change sequence; if it ever does not, the
history is corrupt and the engine says so rather than papering over it.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from platform.universal_control_plane.errors import EvolutionError
from platform.universal_control_plane.ontology import (
    CERTIFICATION_CERTIFIED,
    CERTIFICATION_NOT_CERTIFIED,
    CERTIFICATION_UNCERTIFIED,
    CHANGE_CREATED,
    CHANGE_IMPROVED,
    CHANGE_MODIFIED,
    CHANGE_PROMOTED,
    CHANGE_REGRESSED,
    CHANGE_REMOVED,
    CHANGE_UNCHANGED,
    DIMENSION_ARCHITECTURE,
    DIMENSION_CAPABILITY,
    DIMENSION_CERTIFICATION,
    DIMENSION_GOVERNANCE,
    DIMENSION_VERSION,
    GOVERNANCE_GOVERNED,
    GOVERNANCE_NOT_GOVERNED,
    GOVERNANCE_UNGOVERNED,
    LIFECYCLE_ACTIVE,
    LIFECYCLE_ARCHIVED,
    LIFECYCLE_CANCELLED,
    LIFECYCLE_COMPLETE,
    LIFECYCLE_DRAFT,
    LIFECYCLE_PAUSED,
    ChangeRecord,
    payload_digest,
)
from platform.universal_control_plane.version import SemanticVersion, compare_versions
from typing import Any

#: The declared value rankings the control plane ships with. Each is ordered
#: worst-to-best, so a move rightwards is a promotion and leftwards a regression.
DEFAULT_ORDERINGS: Mapping[str, tuple[str, ...]] = {
    DIMENSION_GOVERNANCE: (
        GOVERNANCE_UNGOVERNED,
        GOVERNANCE_NOT_GOVERNED,
        GOVERNANCE_GOVERNED,
    ),
    DIMENSION_CERTIFICATION: (
        CERTIFICATION_UNCERTIFIED,
        CERTIFICATION_NOT_CERTIFIED,
        CERTIFICATION_CERTIFIED,
    ),
    DIMENSION_CAPABILITY: (
        LIFECYCLE_CANCELLED,
        LIFECYCLE_ARCHIVED,
        LIFECYCLE_DRAFT,
        LIFECYCLE_PAUSED,
        LIFECYCLE_ACTIVE,
        LIFECYCLE_COMPLETE,
    ),
}

#: Dimensions the engine understands out of the box. Open — a manifest or caller
#: may observe any dimension name it likes.
DEFAULT_DIMENSIONS: tuple[str, ...] = (
    DIMENSION_CAPABILITY,
    DIMENSION_ARCHITECTURE,
    DIMENSION_GOVERNANCE,
    DIMENSION_CERTIFICATION,
    DIMENSION_VERSION,
)


@dataclass(frozen=True, slots=True)
class Observation:
    """One recorded measurement of one subject in one dimension.

    The observation log — not the derived change list — is the engine's durable
    state, because a conclusion you cannot re-derive is not replayable.
    """

    subject_id: str
    dimension: str
    value: str
    tick: int = 0
    present: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "dimension": self.dimension,
            "value": self.value,
            "tick": self.tick,
            "present": self.present,
        }


@dataclass
class EvolutionEngine:
    """Tracks change, classifies it, and replays the whole history deterministically."""

    _orderings: dict[str, tuple[str, ...]] = field(default_factory=lambda: dict(DEFAULT_ORDERINGS))
    _observations: list[Observation] = field(default_factory=list)
    _changes: list[ChangeRecord] = field(default_factory=list)
    _current: dict[tuple[str, str], str] = field(default_factory=dict)

    # -- declared orderings ----------------------------------------------

    def register_ordering(self, dimension: str, ranks: Sequence[str]) -> None:
        """Declare the worst-to-best ranking of values in *dimension*."""
        if not dimension.strip():
            raise EvolutionError("a dimension ordering requires a non-empty dimension")
        cleaned = tuple(str(r) for r in ranks if str(r).strip())
        if len(cleaned) < 2:
            raise EvolutionError(
                f"ordering for {dimension!r} needs at least two ranked values to order anything"
            )
        if len(set(cleaned)) != len(cleaned):
            raise EvolutionError(f"ordering for {dimension!r} ranks a value twice")
        self._orderings[dimension] = cleaned

    def ordering(self, dimension: str) -> tuple[str, ...]:
        return self._orderings.get(dimension, ())

    # -- classification --------------------------------------------------

    def classify(self, dimension: str, before: str, after: str) -> str:
        """Classify a transition. Never guesses: an unranked dimension is MODIFIED."""
        if before == after:
            return CHANGE_UNCHANGED

        ranks = self._orderings.get(dimension)
        if ranks and before in ranks and after in ranks:
            return CHANGE_PROMOTED if ranks.index(after) > ranks.index(before) else CHANGE_REGRESSED

        if dimension == DIMENSION_VERSION:
            return _by_version(before, after)

        # Numeric before version-shaped, and only outside the version dimension.
        # ``90.5`` parses as both a decimal and a two-component version; read as
        # a version it would report a coverage rise as a *promotion*, which is
        # the wrong word for a measurement. Inside the version dimension the
        # opposite reading is the right one, which is why that case is settled
        # above rather than here.
        numeric = _as_numbers(before, after)
        if numeric is not None:
            low, high = numeric
            return CHANGE_IMPROVED if high > low else CHANGE_REGRESSED

        if (
            SemanticVersion.try_parse(before) is not None
            and SemanticVersion.try_parse(after) is not None
        ):
            return _by_version(before, after)

        return CHANGE_MODIFIED

    # -- observation -----------------------------------------------------

    def observe(
        self, subject_id: str, dimension: str, value: str, *, tick: int = 0
    ) -> ChangeRecord:
        """Record a measurement and emit the change it represents."""
        if not subject_id.strip():
            raise EvolutionError("an observation requires a non-empty subject_id")
        if not dimension.strip():
            raise EvolutionError("an observation requires a non-empty dimension")
        observation = Observation(subject_id, dimension, str(value), tick=tick)
        self._observations.append(observation)
        return self._fold(observation, self._current, self._changes)

    def observe_many(
        self, items: Iterable[tuple[str, str, str]], *, tick: int = 0
    ) -> tuple[ChangeRecord, ...]:
        """Record many ``(subject_id, dimension, value)`` measurements, deterministically."""
        return tuple(
            self.observe(subject_id, dimension, value, tick=tick)
            for subject_id, dimension, value in sorted(items)
        )

    def observe_snapshot(
        self, dimension: str, snapshot: Mapping[str, str], *, tick: int = 0
    ) -> tuple[ChangeRecord, ...]:
        """Observe a whole dimension at once, emitting REMOVED for what vanished."""
        changes = [
            self.observe(subject_id, dimension, snapshot[subject_id], tick=tick)
            for subject_id in sorted(snapshot)
        ]
        vanished = sorted(
            subject
            for (subject, dim) in self._current
            if dim == dimension and subject not in snapshot
        )
        changes.extend(self.retire(subject, dimension, tick=tick) for subject in vanished)
        return tuple(changes)

    def retire(self, subject_id: str, dimension: str, *, tick: int = 0) -> ChangeRecord:
        """Record that a subject left a dimension it previously occupied."""
        if (subject_id, dimension) not in self._current:
            raise EvolutionError(
                f"cannot retire {subject_id!r} from {dimension!r}: it was never observed there"
            )
        observation = Observation(subject_id, dimension, "", tick=tick, present=False)
        self._observations.append(observation)
        return self._fold(observation, self._current, self._changes)

    # -- the fold (the single place a change is derived) -----------------

    def _fold(
        self,
        observation: Observation,
        current: dict[tuple[str, str], str],
        sink: list[ChangeRecord],
    ) -> ChangeRecord:
        """Derive one change from one observation against *current* state.

        Replay works by running this same fold over the same log into a fresh
        pair of accumulators — one implementation, so a replay cannot diverge
        from live recording by construction.
        """
        key = (observation.subject_id, observation.dimension)
        previous = current.get(key)
        sequence = len(sink) + 1

        if not observation.present:
            kind = CHANGE_REMOVED
            before, after = previous or "", ""
            current.pop(key, None)
        elif previous is None:
            kind = CHANGE_CREATED
            before, after = "", observation.value
            current[key] = observation.value
        else:
            kind = self.classify(observation.dimension, previous, observation.value)
            before, after = previous, observation.value
            current[key] = observation.value

        change = ChangeRecord(
            change_id=f"CHG-{sequence:08d}",
            subject_id=observation.subject_id,
            kind=kind,
            dimension=observation.dimension,
            sequence=sequence,
            from_value=before,
            to_value=after,
            delta_digest=payload_digest(
                {
                    "subject": observation.subject_id,
                    "dimension": observation.dimension,
                    "from": before,
                    "to": after,
                }
            ),
            rationale=f"{observation.dimension}: {before or '∅'} → {after or '∅'}",
            tick=observation.tick,
        )
        sink.append(change)
        return change

    # -- queries ---------------------------------------------------------

    def changes(
        self,
        subject_id: str | None = None,
        *,
        dimension: str | None = None,
        kind: str | None = None,
    ) -> tuple[ChangeRecord, ...]:
        return tuple(
            c
            for c in self._changes
            if (subject_id is None or c.subject_id == subject_id)
            and (dimension is None or c.dimension == dimension)
            and (kind is None or c.kind == kind)
        )

    def promotions(self) -> tuple[ChangeRecord, ...]:
        return self.changes(kind=CHANGE_PROMOTED)

    def regressions(self) -> tuple[ChangeRecord, ...]:
        return self.changes(kind=CHANGE_REGRESSED)

    def improvements(self) -> tuple[ChangeRecord, ...]:
        return self.changes(kind=CHANGE_IMPROVED)

    def deltas(self) -> tuple[ChangeRecord, ...]:
        """Every change that actually moved something (UNCHANGED excluded)."""
        return tuple(c for c in self._changes if c.kind != CHANGE_UNCHANGED)

    def current_value(self, subject_id: str, dimension: str) -> str:
        return self._current.get((subject_id, dimension), "")

    def observations(self) -> tuple[Observation, ...]:
        return tuple(self._observations)

    def dimensions(self) -> tuple[str, ...]:
        return tuple(sorted({o.dimension for o in self._observations}))

    def count(self) -> int:
        return len(self._changes)

    def histogram(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for change in self._changes:
            counts[change.kind] = counts.get(change.kind, 0) + 1
        return dict(sorted(counts.items()))

    # -- delta between two snapshots -------------------------------------

    def diff(
        self, dimension: str, before: Mapping[str, str], after: Mapping[str, str]
    ) -> tuple[ChangeRecord, ...]:
        """Classify the delta between two snapshots without recording anything.

        The pure counterpart of :meth:`observe_snapshot`: it answers *what would
        change* without moving the engine's state, which is what a plan needs
        before it commits to anything.
        """
        state: dict[tuple[str, str], str] = {}
        sink: list[ChangeRecord] = []
        for subject_id in sorted(before):
            self._fold(Observation(subject_id, dimension, before[subject_id]), state, sink)
        baseline = len(sink)
        for subject_id in sorted(after):
            self._fold(Observation(subject_id, dimension, after[subject_id]), state, sink)
        for subject_id in sorted(set(before) - set(after)):
            self._fold(Observation(subject_id, dimension, "", present=False), state, sink)
        return tuple(sink[baseline:])

    # -- replay ----------------------------------------------------------

    def replay(self) -> tuple[ChangeRecord, ...]:
        """Re-fold the observation log from empty and return the reconstructed history."""
        state: dict[tuple[str, str], str] = {}
        sink: list[ChangeRecord] = []
        for observation in self._observations:
            self._fold(observation, state, sink)
        return tuple(sink)

    def replay_digest(self) -> str:
        """The digest of the recorded history — comparable across processes."""
        return payload_digest([c.to_dict() for c in self._changes])

    def verify(self) -> bool:
        """True iff replaying the log reproduces the recorded history exactly."""
        replayed = self.replay()
        if payload_digest([c.to_dict() for c in replayed]) != self.replay_digest():
            raise EvolutionError(
                "evolution replay diverged from the recorded history: "
                f"{len(replayed)} replayed vs {len(self._changes)} recorded"
            )
        return True

    # -- bulk ingestion --------------------------------------------------

    def ingest_change_ledger(
        self, ledger: Mapping[str, Any], *, dimension: str = DIMENSION_ARCHITECTURE
    ) -> int:
        """Load the repository's recorded change events as observations.

        The ledger records each event's resulting state (``to``); replaying those
        in recorded order reconstructs the repository's own evolution inside the
        control plane, rather than inventing a parallel history beside it.
        """
        events = ledger.get("change_events")
        if not isinstance(events, list):
            raise EvolutionError("change ledger has no 'change_events' array")
        ordered = sorted(
            (e for e in events if isinstance(e, Mapping)),
            key=lambda e: (int(e.get("snapshot_seq", 0) or 0), str(e.get("change_id", ""))),
        )
        before = self.count()
        for index, event in enumerate(ordered):
            subject = str(event.get("subject", "") or "")
            if not subject:
                continue
            self.observe(subject, dimension, str(event.get("to", "") or ""), tick=index)
        return self.count() - before

    # -- projection ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "EvolutionEngine",
            "dimensions": list(self.dimensions()),
            "orderings": {k: list(v) for k, v in sorted(self._orderings.items())},
            "counts": {
                "observations": len(self._observations),
                "changes": self.count(),
                "deltas": len(self.deltas()),
                "promotions": len(self.promotions()),
                "regressions": len(self.regressions()),
                "improvements": len(self.improvements()),
            },
            "histogram": self.histogram(),
            "replay_digest": self.replay_digest(),
        }


def _as_numbers(before: str, after: str) -> tuple[float, float] | None:
    """Both values as floats, or ``None`` when either is not numeric."""
    try:
        return float(before), float(after)
    except (TypeError, ValueError):
        return None


def _by_version(before: str, after: str) -> str:
    """Classify a transition by version order (total, even over opaque tokens)."""
    comparison = compare_versions(before, after)
    if comparison < 0:
        return CHANGE_PROMOTED
    if comparison > 0:
        return CHANGE_REGRESSED
    return CHANGE_UNCHANGED


__all__ = [
    "DEFAULT_DIMENSIONS",
    "DEFAULT_ORDERINGS",
    "DIMENSION_ARCHITECTURE",
    "DIMENSION_CAPABILITY",
    "DIMENSION_CERTIFICATION",
    "DIMENSION_GOVERNANCE",
    "DIMENSION_VERSION",
    "EvolutionEngine",
    "Observation",
]
