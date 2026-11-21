"""Bounded partitions and federated visibility over a dependency relation.

Two guarantees, stated once for every layer that needs them:

    * **Boundedness** — every member belongs to exactly one partition. A member bound
      to nothing is refused rather than defaulted.
    * **Isolation** — a dependency crossing a partition boundary is refused unless an
      explicit federation authorises it. Partitions do not leak into each other by
      accident.

WHY THIS IS HERE AND NOT IN A LAYER THAT USES IT. Both rules were implemented in
``engine.runtime.context`` because the runtime needed them first, and
``engine.context.composition`` — whose own declaration (UCXI-000001 CXL-03/CXL-04) makes
them ITS guarantees — imported them upward. That single edge closed the cycle
``engine.runtime -> engine.knowledge -> engine.context -> engine.runtime`` that
UCOS-RIB-001 GATE-10 refuses.

The first correction moved them into ``engine.context.composition``, which broke the
cycle but put a general primitive inside one of its consumers: a third layer wanting
partitions would then have to depend on the context layer, reproducing the same
inversion one step over. The reason it landed there was not architectural — a new module
here mints a universal identity and needs an allocation permit, and that constraint chose
the home. Recording it plainly, because an authorization cost dressed as a design
argument is the failure this repository names in adr/0041.

``engine.compiler`` is the shared substrate: it depends on neither layer, and
``engine/runtime/graph.py`` already reuses :mod:`engine.compiler.cycles` "verbatim
(Mandatory Rule 4 — no duplicate dependency/cycle logic)". The precedent for a general
graph primitive living here was already set; this follows it.

The rules are stated over a node set and a ``dependencies_of`` callable rather than over
any graph class, so no caller's graph type is assumed and this module binds to no layer.
Pure, stdlib-only, deterministic: members and partitions are visited in sorted order, so
identical inputs yield identical frames.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from engine.compiler.errors import DependencyError


class UnboundedMemberError(DependencyError):
    """A member is bound to no partition (boundedness refused)."""


class IsolationError(DependencyError):
    """A crossing is unauthorised, or a federation is malformed (isolation refused)."""


@dataclass(frozen=True, slots=True)
class Partition:
    """One bounded partition: its id and the members bound to it."""

    context_id: str
    members: tuple[str, ...]

    def contains(self, universe_id: str) -> bool:
        """True iff ``universe_id`` is bound to this partition."""
        return universe_id in self.members

    def to_dict(self) -> dict[str, object]:
        return {"context_id": self.context_id, "members": list(self.members)}


@dataclass(frozen=True, slots=True)
class Federation:
    """An explicit cross-partition authorisation. Without one, a crossing is refused."""

    source: str
    target: str

    def to_dict(self) -> dict[str, str]:
        return {"source": self.source, "target": self.target}


@dataclass(frozen=True, slots=True)
class Frame:
    """What one member may reference: same-partition peers plus federated targets."""

    universe_id: str
    context_id: str
    visible: tuple[str, ...]
    federated: tuple[str, ...]

    def can_reference(self, other: str) -> bool:
        """True iff ``other`` is visible from this frame."""
        return other in self.visible

    def to_dict(self) -> dict[str, object]:
        return {
            "universe_id": self.universe_id,
            "context_id": self.context_id,
            "visible": list(self.visible),
            "federated": list(self.federated),
        }


def resolve_partitions(bindings: Mapping[str, str]) -> tuple[Partition, ...]:
    """Group members into their partitions. A member bound to nothing is refused."""
    groups: dict[str, list[str]] = {}
    for member in sorted(bindings):
        partition = bindings[member]
        if not isinstance(partition, str) or not partition:
            raise UnboundedMemberError(
                "member is not bound to a partition (unbounded composition)", member=member
            )
        groups.setdefault(partition, []).append(member)
    return tuple(
        Partition(context_id=cid, members=tuple(sorted(members)))
        for cid, members in sorted(groups.items())
    )


def authorised_crossings(
    bindings: Mapping[str, str], federations: Iterable[Federation]
) -> dict[str, frozenset[str]]:
    """Validate federations and index them by source.

    Refuses a dangling endpoint, a self-federation, a same-partition pair (which is not a
    crossing at all) and a duplicate reference.
    """
    seen: set[tuple[str, str]] = set()
    targets: dict[str, set[str]] = {}
    for federation in federations:
        source, target = federation.source, federation.target
        if source not in bindings:
            raise IsolationError("federation source is not a member", source=source)
        if target not in bindings:
            raise IsolationError("federation target is not a member", target=target)
        if source == target:
            raise IsolationError("a member cannot federate with itself", member=source)
        if bindings[source] == bindings[target]:
            raise IsolationError(
                "federation endpoints share a partition", source=source, target=target
            )
        if (source, target) in seen:
            raise IsolationError(
                "duplicate federation reference (collision)", source=source, target=target
            )
        seen.add((source, target))
        targets.setdefault(source, set()).add(target)
    return {source: frozenset(t) for source, t in targets.items()}


def resolve_frames(
    bindings: Mapping[str, str],
    nodes: Iterable[str],
    dependencies_of: Callable[[str], Iterable[str]],
    federations: Iterable[Federation] = (),
) -> tuple[Frame, ...]:
    """Resolve each member's frame and refuse any unauthorised crossing."""
    ordered = tuple(nodes)
    for node in ordered:
        if node not in bindings:
            raise UnboundedMemberError("member has no partition binding", member=node)
    authorised = authorised_crossings(bindings, federations)
    by_partition: dict[str, list[str]] = {}
    for node in ordered:
        by_partition.setdefault(bindings[node], []).append(node)

    frames: list[Frame] = []
    for member in ordered:
        partition = bindings[member]
        for dependency in dependencies_of(member):
            if bindings[dependency] != partition and dependency not in authorised.get(
                member, frozenset()
            ):
                raise IsolationError(
                    "cross-partition dependency without a federation",
                    member=member,
                    dependency=dependency,
                )
        peers = set(by_partition.get(partition, ())) - {member}
        federated = authorised.get(member, frozenset())
        frames.append(
            Frame(
                universe_id=member,
                context_id=partition,
                visible=tuple(sorted(peers | set(federated))),
                federated=tuple(sorted(federated)),
            )
        )
    return tuple(frames)


__all__ = [
    "Federation",
    "Frame",
    "IsolationError",
    "Partition",
    "UnboundedMemberError",
    "authorised_crossings",
    "resolve_frames",
    "resolve_partitions",
]
