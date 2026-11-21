"""UCOS-CTRL-000001 — Universal Registries.

Four append-only, content-addressed registries:
    CapabilityRegistry   — registered capabilities by universe
    OwnershipRegistry    — capability → owner bindings
    DependencyRegistry   — directed dependency edges
    AgentRegistry        — registered execution agents

All registries are fail-closed on duplicate registration and produce
deterministic evidence via their ``to_dict()`` surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from platform.universal_control_plane.errors import (
    DuplicateObjectError,
    ObjectNotFoundError,
    RegistrationError,
)
from platform.universal_control_plane.ontology import (
    AgentRecord,
    Capability,
    DependencyRecord,
    OwnershipRecord,
)
from typing import Any

# ---------------------------------------------------------------------------
# Capability Registry
# ---------------------------------------------------------------------------


@dataclass
class CapabilityRegistry:
    """Append-only registry of capabilities, indexed by capability_id."""

    _capabilities: dict[str, Capability] = field(default_factory=dict)

    def register(self, cap: Capability) -> Capability:
        if cap.capability_id in self._capabilities:
            raise DuplicateObjectError(f"capability already registered: {cap.capability_id}")
        if not cap.capability_id.strip():
            raise RegistrationError("capability_id must be non-empty")
        if not cap.universe_id.strip():
            raise RegistrationError("universe_id must be non-empty")
        self._capabilities[cap.capability_id] = cap
        return cap

    def get(self, capability_id: str) -> Capability:
        if capability_id not in self._capabilities:
            raise ObjectNotFoundError(f"capability not found: {capability_id}")
        return self._capabilities[capability_id]

    def by_universe(self, universe_id: str) -> list[Capability]:
        return [c for c in self._capabilities.values() if c.universe_id == universe_id]

    def all(self) -> list[Capability]:
        return list(self._capabilities.values())

    def count(self) -> int:
        return len(self._capabilities)

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry": "CapabilityRegistry",
            "count": self.count(),
            "capabilities": [c.to_dict() for c in self.all()],
        }


# ---------------------------------------------------------------------------
# Ownership Registry
# ---------------------------------------------------------------------------


@dataclass
class OwnershipRegistry:
    """Append-only ownership registry. One owner per capability."""

    _records: dict[str, OwnershipRecord] = field(default_factory=dict)
    # capability_id → ownership_id for fast lookup
    _by_capability: dict[str, str] = field(default_factory=dict)

    def register(self, record: OwnershipRecord) -> OwnershipRecord:
        if record.ownership_id in self._records:
            raise DuplicateObjectError(f"ownership record already exists: {record.ownership_id}")
        if record.capability_id in self._by_capability:
            raise RegistrationError(
                f"capability {record.capability_id!r} already has a registered owner"
            )
        self._records[record.ownership_id] = record
        self._by_capability[record.capability_id] = record.ownership_id
        return record

    def get(self, ownership_id: str) -> OwnershipRecord:
        if ownership_id not in self._records:
            raise ObjectNotFoundError(f"ownership record not found: {ownership_id}")
        return self._records[ownership_id]

    def owner_of(self, capability_id: str) -> OwnershipRecord | None:
        oid = self._by_capability.get(capability_id)
        return self._records[oid] if oid else None

    def by_owner(self, owner_id: str) -> list[OwnershipRecord]:
        return [r for r in self._records.values() if r.owner_id == owner_id]

    def all(self) -> list[OwnershipRecord]:
        return list(self._records.values())

    def count(self) -> int:
        return len(self._records)

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry": "OwnershipRegistry",
            "count": self.count(),
            "records": [r.to_dict() for r in self.all()],
        }


# ---------------------------------------------------------------------------
# Dependency Registry
# ---------------------------------------------------------------------------


@dataclass
class DependencyRegistry:
    """Append-only directed dependency graph."""

    _records: dict[str, DependencyRecord] = field(default_factory=dict)

    def register(self, record: DependencyRecord) -> DependencyRecord:
        if record.dependency_id in self._records:
            raise DuplicateObjectError(f"dependency record already exists: {record.dependency_id}")
        if record.from_id == record.to_id:
            raise RegistrationError("dependency cannot point to itself")
        self._records[record.dependency_id] = record
        return record

    def get(self, dependency_id: str) -> DependencyRecord:
        if dependency_id not in self._records:
            raise ObjectNotFoundError(f"dependency record not found: {dependency_id}")
        return self._records[dependency_id]

    def dependencies_of(self, from_id: str) -> list[DependencyRecord]:
        """Return all dependencies *from_id* declares (things it needs)."""
        return [r for r in self._records.values() if r.from_id == from_id]

    def dependents_of(self, to_id: str) -> list[DependencyRecord]:
        """Return all records whose target is *to_id* (things that need it)."""
        return [r for r in self._records.values() if r.to_id == to_id]

    def has_cycle(self) -> bool:
        """Detect a cycle in the dependency graph using DFS."""
        adj: dict[str, list[str]] = {}
        for r in self._records.values():
            adj.setdefault(r.from_id, []).append(r.to_id)

        visited: set[str] = set()
        in_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            in_stack.add(node)
            for neighbour in adj.get(node, []):
                if neighbour not in visited:
                    if dfs(neighbour):
                        return True
                elif neighbour in in_stack:
                    return True
            in_stack.discard(node)
            return False

        return any(dfs(n) for n in adj if n not in visited)

    def topological_order(self) -> list[str]:
        """Return nodes in topological order (leaves first). Raises on cycle."""
        if self.has_cycle():
            from platform.universal_control_plane.errors import SchedulerError

            raise SchedulerError("dependency graph contains a cycle; topological order impossible")
        adj: dict[str, list[str]] = {}
        in_degree: dict[str, int] = {}
        all_nodes: set[str] = set()
        for r in self._records.values():
            adj.setdefault(r.from_id, []).append(r.to_id)
            all_nodes.update((r.from_id, r.to_id))
        for n in all_nodes:
            in_degree[n] = 0
        for r in self._records.values():
            in_degree[r.to_id] = in_degree.get(r.to_id, 0) + 1

        queue = sorted(n for n, d in in_degree.items() if d == 0)
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for nb in sorted(adj.get(node, [])):
                in_degree[nb] -= 1
                if in_degree[nb] == 0:
                    queue.append(nb)
        # Edges read "from REQUIRES to", so Kahn's seeds on dependents and emits
        # them before the dependencies they require. Reverse it so a node's
        # dependencies precede it — the same contract as
        # engine.compiler.cycles.topological_order, and the order the Scheduler's
        # wave numbering in this package already assumes.
        return list(reversed(order))

    def all(self) -> list[DependencyRecord]:
        return list(self._records.values())

    def count(self) -> int:
        return len(self._records)

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry": "DependencyRegistry",
            "count": self.count(),
            "has_cycle": self.has_cycle(),
            "records": [r.to_dict() for r in self.all()],
        }


# ---------------------------------------------------------------------------
# Agent Registry
# ---------------------------------------------------------------------------


@dataclass
class AgentRegistry:
    """Append-only registry of execution agents."""

    _agents: dict[str, AgentRecord] = field(default_factory=dict)

    def register(self, agent: AgentRecord) -> AgentRecord:
        if agent.agent_id in self._agents:
            raise DuplicateObjectError(f"agent already registered: {agent.agent_id}")
        if not agent.agent_id.strip():
            raise RegistrationError("agent_id must be non-empty")
        self._agents[agent.agent_id] = agent
        return agent

    def get(self, agent_id: str) -> AgentRecord:
        if agent_id not in self._agents:
            raise ObjectNotFoundError(f"agent not found: {agent_id}")
        return self._agents[agent_id]

    def by_capability(self, capability: str) -> list[AgentRecord]:
        return [a for a in self._agents.values() if capability in a.capabilities]

    def active(self) -> list[AgentRecord]:
        from platform.universal_control_plane.ontology import LIFECYCLE_ACTIVE

        return [a for a in self._agents.values() if a.state == LIFECYCLE_ACTIVE]

    def all(self) -> list[AgentRecord]:
        return list(self._agents.values())

    def count(self) -> int:
        return len(self._agents)

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry": "AgentRegistry",
            "count": self.count(),
            "agents": [a.to_dict() for a in self.all()],
        }
