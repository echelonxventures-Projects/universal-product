"""UCOS-UICM-000001 — the append-only closure observation registry.

A closure state is never edited. This module is what makes that structural rather than
aspirational: a state *change* is a new :class:`Observation` appended to the registry,
carrying explicit lineage to the observation it supersedes, and the record it replaced is
left exactly as it was. So the registry is a history, not a current-value store, and the
question "what did this coordinate read before, and what replaced it?" has an answer that
no later run can erase.

Three properties are enforced here rather than described.

**No mutating operation exists.** The registry exposes ``record``, ``record_transition``
and read accessors. There is no update, no delete, no overwrite and no setter, and
:class:`Observation` is a frozen dataclass so a record cannot be altered after
construction. UICM-INV-16 measures the absence of a mutating operation over this package's
own source, because an append-only register whose immutability is only a convention is
one edit away from not being append-only.

**Lineage is explicit.** Each observation names ``supersedes`` — the identifier of the
prior observation for the same coordinate — and links ``previous_hash`` across the whole
registry. The first reading of a coordinate supersedes nothing and says so with an empty
reference rather than a null nobody checks.

**Supersession is derived, not stamped.** An observation cannot carry "I was superseded",
because writing that would be the in-place mutation the design forbids. Instead the
registry derives it: for a coordinate, the last appended observation is current and every
earlier one is :attr:`~engine.uicm.model.ClosureState.SUPERSEDED`. The state a record
carries is the state that was *measured*; the state the registry *reports* for a historical
record is SUPERSEDED. Keeping those two distinct is what allows history to stay truthful
while the current reading stays unambiguous.

Observation identity is derived from the coordinate and the revision depth. It is not
minted: the capability half comes from the capability register and the dimension half from
the declaration, and the revision is the lineage depth of the coordinate rather than a
global counter, so identity does not depend on the order unrelated coordinates were
measured in.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.uicm.model import (
    Capability,
    ClosureCell,
    ClosureError,
    ClosureState,
    DimensionDeclaration,
    digest,
)

#: The observation registry document format.
OBSERVATION_REGISTRY_FORMAT = "ucos-uicm-observation-registry/1.0.0"

#: The genesis link of the observation chain.
GENESIS_HASH = "0" * 64

#: The observation identifier prefix.
OBSERVATION_PREFIX = "UICM-OBS"

#: The empty lineage reference — the first reading of a coordinate supersedes nothing.
NO_PREDECESSOR = ""


class ObservationError(ClosureError):
    """Raised when an observation is malformed or the registry's chain is broken."""


def observation_id(capability: Capability, dimension: DimensionDeclaration, revision: int) -> str:
    """Derive an observation identifier from owned identity plus lineage depth.

    Injective within a coordinate by ``revision`` and across coordinates by the capability
    identity and dimension ordinal, both of which are owned elsewhere. No global counter,
    so measuring the same tree twice yields the same identifiers.
    """
    if revision < 1:
        raise ObservationError("observation revision is 1-based")
    return f"{OBSERVATION_PREFIX}-{capability.short_id}-" f"{dimension.ordinal:02d}-r{revision:02d}"


@dataclass(frozen=True, slots=True)
class Observation:
    """One immutable reading of one coordinate at one point in the lineage.

    ``state`` is what was measured. Whether this reading is still current is not stored
    here — it is derived by the registry, because storing it would require editing a
    record that a later observation replaced.
    """

    observation_id: str
    sequence: int
    revision: int
    capability_id: str
    capability_name: str
    dimension_id: str
    state: ClosureState
    finding: str
    evidence: tuple[str, ...]
    supersedes: str
    previous_hash: str
    entry_hash: str

    @classmethod
    def link(
        cls,
        *,
        observation_id: str,
        sequence: int,
        revision: int,
        capability: Capability,
        dimension: DimensionDeclaration,
        state: ClosureState,
        finding: str,
        evidence: Sequence[str],
        supersedes: str,
        previous_hash: str,
    ) -> Observation:
        """Construct a chained observation. The link seals every field above it."""
        body = {
            "observation_id": observation_id,
            "sequence": sequence,
            "revision": revision,
            "capability_id": capability.capability_id,
            "capability_name": capability.name,
            "dimension_id": dimension.id,
            "state": state.value,
            "finding": finding,
            "evidence": list(evidence),
            "supersedes": supersedes,
            "previous_hash": previous_hash,
        }
        return cls(
            observation_id=observation_id,
            sequence=sequence,
            revision=revision,
            capability_id=capability.capability_id,
            capability_name=capability.name,
            dimension_id=dimension.id,
            state=state,
            finding=finding,
            evidence=tuple(evidence),
            supersedes=supersedes,
            previous_hash=previous_hash,
            entry_hash=digest(body),
        )

    @property
    def key(self) -> str:
        """The matrix coordinate this observation reads."""
        return f"{self.capability_name}:{self.dimension_id}"

    @property
    def evidence_digest(self) -> str:
        if not self.evidence:
            return ""
        return digest({"cell": self.key, "evidence": list(self.evidence)})

    def body(self) -> dict[str, Any]:
        """The hashed subset, so a reader can recompute the link independently."""
        return {
            "observation_id": self.observation_id,
            "sequence": self.sequence,
            "revision": self.revision,
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "dimension_id": self.dimension_id,
            "state": self.state.value,
            "finding": self.finding,
            "evidence": list(self.evidence),
            "supersedes": self.supersedes,
            "previous_hash": self.previous_hash,
        }

    def expected_hash(self) -> str:
        return digest(self.body())

    def to_dict(self, *, current: bool) -> dict[str, Any]:
        """Serialize, reporting the derived effective state alongside the measured one."""
        record = self.body()
        record["entry_hash"] = self.entry_hash
        record["current"] = current
        record["effective_state"] = self.state.value if current else ClosureState.SUPERSEDED.value
        return record


class ObservationRegistry:
    """An append-only, hash-chained registry of closure observations.

    The public surface is deliberately three verbs wide — append, read, verify. Adding a
    fourth that changed a record would break the property the whole programme rests on,
    so the absence is measured (UICM-INV-16) rather than left to review.
    """

    __slots__ = ("_by_coordinate", "_by_id", "_observations")

    def __init__(self) -> None:
        self._observations: list[Observation] = []
        self._by_id: dict[str, Observation] = {}
        self._by_coordinate: dict[str, list[str]] = {}

    # -- append -------------------------------------------------------------------

    def record(
        self,
        *,
        capability: Capability,
        dimension: DimensionDeclaration,
        state: ClosureState,
        finding: str,
        evidence: Sequence[str] = (),
    ) -> Observation:
        """Append one observation, superseding this coordinate's previous reading.

        The transition into ``state`` is checked against the declared algebra: appending a
        reading that could not legally follow the current one is refused, so the registry
        cannot contain a history that the state machine says is impossible.
        """
        key = f"{capability.name}:{dimension.id}"
        lineage = self._by_coordinate.setdefault(key, [])
        predecessor = self._by_id[lineage[-1]] if lineage else None
        if predecessor is not None:
            predecessor.state.require_transition_to(state)
        revision = len(lineage) + 1
        identifier = observation_id(capability, dimension, revision)
        if identifier in self._by_id:
            raise ObservationError(
                "observation identifier already recorded", observation_id=identifier
            )
        observation = Observation.link(
            observation_id=identifier,
            sequence=len(self._observations) + 1,
            revision=revision,
            capability=capability,
            dimension=dimension,
            state=state,
            finding=finding,
            evidence=evidence,
            supersedes=predecessor.observation_id if predecessor else NO_PREDECESSOR,
            previous_hash=self.head_hash,
        )
        self._observations.append(observation)
        self._by_id[identifier] = observation
        lineage.append(identifier)
        return observation

    def record_transition(
        self,
        *,
        capability: Capability,
        dimension: DimensionDeclaration,
        states: Sequence[ClosureState],
        finding: str,
        evidence: Sequence[str] = (),
    ) -> tuple[Observation, ...]:
        """Append one observation per state in a transition path.

        Every state a coordinate passes through becomes its own record with its own
        lineage link, so the path is reconstructable rather than collapsed into an
        endpoint. Only the final observation carries the evidence, because the
        intermediate states are procedural — a coordinate being *measured* is not itself a
        finding about the repository.
        """
        if not states:
            raise ObservationError("a transition path needs at least one state")
        appended: list[Observation] = []
        last = len(states) - 1
        for position, state in enumerate(states):
            appended.append(
                self.record(
                    capability=capability,
                    dimension=dimension,
                    state=state,
                    finding=finding if position == last else state.value,
                    evidence=evidence if position == last else (),
                )
            )
        return tuple(appended)

    # -- read ---------------------------------------------------------------------

    @property
    def head_hash(self) -> str:
        return self._observations[-1].entry_hash if self._observations else GENESIS_HASH

    @property
    def observations(self) -> tuple[Observation, ...]:
        return tuple(self._observations)

    def __len__(self) -> int:
        return len(self._observations)

    def __iter__(self) -> Iterator[Observation]:
        return iter(tuple(self._observations))

    def __contains__(self, identifier: object) -> bool:
        return identifier in self._by_id

    def get(self, identifier: str) -> Observation:
        observation = self._by_id.get(identifier)
        if observation is None:
            raise ObservationError("no such observation", observation_id=identifier)
        return observation

    def coordinates(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_coordinate))

    def lineage(self, key: str) -> tuple[Observation, ...]:
        """Every observation of one coordinate, oldest first."""
        return tuple(self._by_id[i] for i in self._by_coordinate.get(key, ()))

    def current(self, key: str) -> Observation:
        """The coordinate's live reading, or fail closed if it was never observed."""
        lineage = self._by_coordinate.get(key)
        if not lineage:
            raise ObservationError("coordinate has no observation", coordinate=key)
        return self._by_id[lineage[-1]]

    def current_observations(self) -> tuple[Observation, ...]:
        """One live reading per coordinate, in coordinate order."""
        return tuple(self.current(key) for key in self.coordinates())

    def superseded_observations(self) -> tuple[Observation, ...]:
        """Every historical reading — the records a later observation replaced."""
        live = {o.observation_id for o in self.current_observations()}
        return tuple(o for o in self._observations if o.observation_id not in live)

    def is_current(self, observation: Observation) -> bool:
        return self.current(observation.key).observation_id == observation.observation_id

    def effective_state(self, observation: Observation) -> ClosureState:
        """The state to report: what was measured, or SUPERSEDED if history replaced it."""
        return observation.state if self.is_current(observation) else ClosureState.SUPERSEDED

    def state_counts(self) -> dict[str, int]:
        """Effective-state counts across every observation, historical ones included."""
        counts = {state.value: 0 for state in ClosureState}
        for observation in self._observations:
            counts[self.effective_state(observation).value] += 1
        return counts

    def cells(self) -> tuple[ClosureCell, ...]:
        """Project the live readings into matrix cells.

        The matrix is a *view* over the current observations. It holds no state of its own,
        so the matrix and the history can never disagree about what was measured.
        """
        projected: list[ClosureCell] = []
        for observation in self.current_observations():
            lineage = self.lineage(observation.key)
            projected.append(
                ClosureCell(
                    capability_id=observation.capability_id,
                    capability_name=observation.capability_name,
                    dimension_id=observation.dimension_id,
                    state=observation.state,
                    finding=observation.finding,
                    evidence=observation.evidence,
                    transition=tuple(step.state.value for step in lineage),
                    observation_id=observation.observation_id,
                    observation_lineage=tuple(step.observation_id for step in lineage),
                )
            )
        return tuple(projected)

    # -- verify -------------------------------------------------------------------

    def verify(self) -> bool:
        """True iff every link recomputes, the sequence is dense, and lineage is sound."""
        previous = GENESIS_HASH
        seen_per_coordinate: dict[str, str] = {}
        for position, observation in enumerate(self._observations, start=1):
            if observation.sequence != position:
                return False
            if observation.previous_hash != previous:
                return False
            if observation.entry_hash != observation.expected_hash():
                return False
            expected_predecessor = seen_per_coordinate.get(observation.key, NO_PREDECESSOR)
            if observation.supersedes != expected_predecessor:
                return False
            seen_per_coordinate[observation.key] = observation.observation_id
            previous = observation.entry_hash
        return True

    def require_intact(self) -> None:
        if not self.verify():
            raise ObservationError("observation registry chain is not intact")

    def lineage_report(self) -> dict[str, Any]:
        """How deep the history runs, and how much of it is historical."""
        historical = self.superseded_observations()
        return {
            "observation_total": len(self._observations),
            "coordinate_total": len(self._by_coordinate),
            "current_total": len(self.current_observations()),
            "superseded_total": len(historical),
            "max_revision": max((len(v) for v in self._by_coordinate.values()), default=0),
            "chain_intact": self.verify(),
            "head_hash": self.head_hash,
        }

    def to_document(self) -> dict[str, Any]:
        live = {o.observation_id for o in self.current_observations()}
        return {
            "format": OBSERVATION_REGISTRY_FORMAT,
            "authority": "NONE - DERIVED TRUTH",
            "mutability": "APPEND-ONLY IMMUTABLE",
            "lineage": self.lineage_report(),
            "effective_state_counts": self.state_counts(),
            "observations": [
                observation.to_dict(current=observation.observation_id in live)
                for observation in self._observations
            ],
        }

    def digest(self) -> str:
        return digest(self.to_document())


def build_registry(
    capabilities: Sequence[Capability],
    dimensions: Sequence[DimensionDeclaration],
    findings: Mapping[str, tuple[ClosureState, str, tuple[str, ...]]],
) -> ObservationRegistry:
    """Record the full transition path for every coordinate.

    ``findings`` maps a coordinate to the measured outcome. Each coordinate is recorded as
    DISCOVERED (the obligation existed), then MEASURED (a probe ran), then the measured
    state — three observations, so the lineage shows that nothing jumped straight to a
    verdict without being measured first.
    """
    registry = ObservationRegistry()
    for capability in capabilities:
        for dimension in dimensions:
            key = f"{capability.name}:{dimension.id}"
            if key not in findings:
                raise ObservationError("coordinate was not measured", coordinate=key)
            state, finding, evidence = findings[key]
            registry.record_transition(
                capability=capability,
                dimension=dimension,
                states=(ClosureState.DISCOVERED, ClosureState.MEASURED, state),
                finding=finding,
                evidence=evidence,
            )
    registry.require_intact()
    return registry


__all__ = [
    "GENESIS_HASH",
    "NO_PREDECESSOR",
    "OBSERVATION_PREFIX",
    "OBSERVATION_REGISTRY_FORMAT",
    "Observation",
    "ObservationError",
    "ObservationRegistry",
    "build_registry",
    "observation_id",
]
