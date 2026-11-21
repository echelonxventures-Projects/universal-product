"""UAPF-000001 — the Universal Registry Engine (the one admission point for pipelines).

A pipeline exists, for UAPF, exactly when it is registered here. Nothing consults a
directory listing, a module attribute or a hard-coded list, so "discover the pipelines"
is always the same act — read the registry — and a pipeline that is not registered simply
does not run. That is what makes the framework registry-driven rather than
convention-driven.

What the registry stores, and what it refuses to store
------------------------------------------------------
An entry binds a *declaration* to its *derived plan* and to an admission ordinal. It
stores no order, no status and no supersession flag, because all three are derivable and
a stored copy of a derivable fact is a copy that can go stale:

    * the plan is derived at admission and re-derivable from the declaration, so
      :meth:`PipelineRegistry.require_intact` can prove the stored plan is still the plan
      the declaration implies;
    * supersession is derived by semantic-version comparison
      (:meth:`PipelineRegistry.latest`), so a version chain cannot disagree with itself;
    * the capability graph and the inter-pipeline dependency edges are derived from the
      declared capabilities (:meth:`capability_graph`, :meth:`pipeline_dependencies`), so
      the capability catalogue is a *view* of the registry and never a second catalogue
      to reconcile.

Uniqueness is enforced on ``(pipeline_id, version)``: re-registering an existing version
is refused rather than ignored, so an entry can never be silently rebound. Versions may
arrive in any order — a catalogue is data and its order is not meaningful — and ``latest``
is still the greatest version, not the last one read.

Determinism: entries are returned in sorted order everywhere, so listings, graphs and
fingerprints are byte-identical across runs. Registration optionally records an event on
a :class:`~platform.universal_pipeline.events.PipelineEventBus`; the registry itself
performs no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import Version, content_hash
from platform.universal_pipeline.contracts import PipelineDefinition, PipelinePlan
from platform.universal_pipeline.errors import PipelineRegistryError
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.identity import Identity, mint
from typing import Any


@dataclass(frozen=True, slots=True)
class PipelineRegistryEntry:
    """One admitted pipeline version: its declaration, its derived plan, its ordinal.

    ``ordinal`` is the admission position — a deterministic total order over a partial
    truth (registration order), useful for audit and never used for precedence. Precedence
    is by semantic version, which is a property of the declaration rather than of when it
    happened to be read.
    """

    definition: PipelineDefinition
    plan: PipelinePlan
    ordinal: int

    def __post_init__(self) -> None:
        if not isinstance(self.definition, PipelineDefinition):
            raise PipelineRegistryError("registry entry requires a PipelineDefinition")
        if not isinstance(self.plan, PipelinePlan):
            raise PipelineRegistryError(
                "registry entry requires a PipelinePlan",
                pipeline_id=self.definition.pipeline_id,
            )
        if self.ordinal < 0:
            raise PipelineRegistryError(
                "registry entry ordinal must be non-negative",
                pipeline_id=self.definition.pipeline_id,
            )
        if self.plan.pipeline_id != self.definition.pipeline_id:
            raise PipelineRegistryError(
                "registry entry plan belongs to a different pipeline",
                pipeline_id=self.definition.pipeline_id,
                plan_pipeline_id=self.plan.pipeline_id,
            )
        if self.plan.version != self.definition.version:
            raise PipelineRegistryError(
                "registry entry plan belongs to a different version",
                pipeline_id=self.definition.pipeline_id,
                version=self.definition.version,
                plan_version=self.plan.version,
            )

    @property
    def pipeline_id(self) -> str:
        return self.definition.pipeline_id

    @property
    def version(self) -> str:
        return self.definition.version

    @property
    def pipeline_type(self) -> str:
        return self.definition.pipeline_type

    @property
    def identity(self) -> Identity:
        """The canonical identity of the registered pipeline version."""
        return self.definition.identity

    @property
    def key(self) -> tuple[str, str]:
        """The registry key: ``(pipeline_id, version)``."""
        return (self.pipeline_id, self.version)

    def semantic_version(self) -> Version:
        """The parsed semantic version (precedence within a pipeline id)."""
        return Version.parse(self.version)

    def replan(self) -> PipelinePlan:
        """Re-derive the plan from the declaration (the integrity check's other half)."""
        return PipelinePlan.derive(self.definition)

    def to_dict(self) -> dict[str, Any]:
        return {
            "identity": self.identity.value,
            "pipeline_id": self.pipeline_id,
            "pipeline_type": self.pipeline_type,
            "version": self.version,
            "ordinal": self.ordinal,
            "definition_fingerprint": self.definition.fingerprint(),
            "plan_fingerprint": self.plan.fingerprint(),
            "stage_count": len(self.definition.stages),
            "wave_count": self.plan.wave_count,
            "max_parallelism": self.plan.max_parallelism,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class PipelineRegistry:
    """The single registration authority for pipeline declarations.

    Holds admitted entries keyed by ``(pipeline_id, version)`` and derives every other
    view from them. Unbounded: it knows nothing about any particular pipeline, pipeline
    type or stage, so the thousandth registration costs exactly what the first did.
    """

    __slots__ = ("_entries", "_bus")

    def __init__(self, *, bus: PipelineEventBus | None = None) -> None:
        if bus is not None and not isinstance(bus, PipelineEventBus):
            raise PipelineRegistryError("bus must be a PipelineEventBus")
        self._entries: dict[tuple[str, str], PipelineRegistryEntry] = {}
        self._bus = bus

    # -- registration -----------------------------------------------------------------

    def register(self, definition: PipelineDefinition) -> PipelineRegistryEntry:
        """Admit ``definition``, derive its plan, and return the resulting entry.

        The plan is derived *here* rather than accepted from the caller, so no entry can
        carry an order that its declaration does not imply.

        Raises:
            PipelineRegistryError: if ``definition`` is not a
                :class:`~platform.universal_pipeline.contracts.PipelineDefinition`, or
                ``(pipeline_id, version)`` is already registered.
            PipelinePlanError: if the declared stage graph cannot be ordered.
        """
        if not isinstance(definition, PipelineDefinition):
            raise PipelineRegistryError("only a PipelineDefinition can be registered")
        key = (definition.pipeline_id, definition.version)
        if key in self._entries:
            raise PipelineRegistryError(
                "pipeline version already registered",
                pipeline_id=definition.pipeline_id,
                version=definition.version,
            )
        previous_latest = self._latest_or_none(definition.pipeline_id)
        entry = PipelineRegistryEntry(
            definition=definition,
            plan=PipelinePlan.derive(definition),
            ordinal=len(self._entries),
        )
        self._entries[key] = entry
        if self._bus is not None:
            self._bus.emit(
                "uapf.pipeline.registered",
                entry.identity.value,
                payload={
                    "pipeline_id": entry.pipeline_id,
                    "pipeline_type": entry.pipeline_type,
                    "version": entry.version,
                    "ordinal": entry.ordinal,
                    "definition_fingerprint": definition.fingerprint(),
                },
            )
            # Each declared capability is recorded as its own event. The capability graph is
            # DERIVED from these declarations, so recording the declarations is what makes the
            # derived graph auditable: the graph can always be reconstructed from history.
            for capability in definition.capabilities:
                self._bus.emit(
                    "uapf.capability.declared",
                    capability.identity.value,
                    payload={
                        "pipeline_id": entry.pipeline_id,
                        "version": entry.version,
                        "capability_id": capability.capability_id,
                        "direction": capability.direction,
                        "contract": capability.contract.to_dict(),
                    },
                )
            if previous_latest is not None and self.latest(definition.pipeline_id).key == key:
                self._bus.emit(
                    "uapf.pipeline.superseded",
                    previous_latest.identity.value,
                    payload={
                        "pipeline_id": previous_latest.pipeline_id,
                        "superseded_version": previous_latest.version,
                        "superseding_version": entry.version,
                    },
                )
        return entry

    # -- lookup -----------------------------------------------------------------------

    def __contains__(self, key: tuple[str, str]) -> bool:
        return key in self._entries

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> tuple[PipelineRegistryEntry, ...]:
        """Every entry, ordered by ``(pipeline_id, semantic version)`` (deterministic)."""
        return tuple(
            sorted(self._entries.values(), key=lambda e: (e.pipeline_id, e.semantic_version()))
        )

    @property
    def pipeline_ids(self) -> tuple[str, ...]:
        """Every registered pipeline id, sorted."""
        return tuple(sorted({key[0] for key in self._entries}))

    @property
    def pipeline_types_registered(self) -> tuple[str, ...]:
        """The distinct pipeline types actually present in the registry, sorted."""
        return tuple(sorted({entry.pipeline_type for entry in self._entries.values()}))

    def versions(self, pipeline_id: str) -> tuple[str, ...]:
        """Every registered version of ``pipeline_id``, in semantic-version order.

        Raises:
            PipelineRegistryError: if no version of ``pipeline_id`` is registered.
        """
        found = [entry for entry in self._entries.values() if entry.pipeline_id == pipeline_id]
        if not found:
            raise PipelineRegistryError("no such pipeline registered", pipeline_id=pipeline_id)
        return tuple(entry.version for entry in sorted(found, key=lambda e: e.semantic_version()))

    def get(self, pipeline_id: str, version: str | None = None) -> PipelineRegistryEntry:
        """The entry for ``pipeline_id`` at ``version`` (the latest version when omitted).

        Raises:
            PipelineRegistryError: if the pipeline, or that version of it, is not
                registered (fail-closed — never a silent ``None``).
        """
        if version is None:
            return self.latest(pipeline_id)
        entry = self._entries.get((pipeline_id, version))
        if entry is None:
            raise PipelineRegistryError(
                "no such pipeline version registered",
                pipeline_id=pipeline_id,
                version=version,
            )
        return entry

    def latest(self, pipeline_id: str) -> PipelineRegistryEntry:
        """The greatest registered version of ``pipeline_id``.

        Derived by semantic-version comparison, so it is the latest *version* and not
        merely the most recently registered one.

        Raises:
            PipelineRegistryError: if no version of ``pipeline_id`` is registered.
        """
        entry = self._latest_or_none(pipeline_id)
        if entry is None:
            raise PipelineRegistryError("no such pipeline registered", pipeline_id=pipeline_id)
        return entry

    def by_type(self, pipeline_type: str) -> tuple[PipelineRegistryEntry, ...]:
        """Every entry of ``pipeline_type``, in registry order.

        Empty is a legitimate answer: a registered type with no pipeline declared against
        it yet is exactly the open-world case, so this does not fail closed.
        """
        return tuple(entry for entry in self.entries if entry.pipeline_type == pipeline_type)

    def is_superseded(self, pipeline_id: str, version: str) -> bool:
        """True iff a greater version of ``pipeline_id`` is registered."""
        entry = self.get(pipeline_id, version)
        return entry.key != self.latest(pipeline_id).key

    # -- derived graphs ---------------------------------------------------------------

    def capability_graph(self) -> dict[str, dict[str, list[str]]]:
        """capability id -> the latest pipeline ids providing and requiring it.

        The capability catalogue, derived from declarations. Only latest versions
        contribute, because a superseded version's declarations describe history rather
        than the capability surface currently in force.
        """
        graph: dict[str, dict[str, list[str]]] = {}
        for pipeline_id in self.pipeline_ids:
            entry = self.latest(pipeline_id)
            for capability in entry.definition.capabilities:
                bucket = graph.setdefault(
                    capability.capability_id, {"provided_by": [], "required_by": []}
                )
                side = "provided_by" if capability.direction == "provides" else "required_by"
                if pipeline_id not in bucket[side]:
                    bucket[side].append(pipeline_id)
        return {
            capability_id: {
                "provided_by": sorted(sides["provided_by"]),
                "required_by": sorted(sides["required_by"]),
            }
            for capability_id, sides in sorted(graph.items())
        }

    def pipeline_dependencies(self) -> dict[str, tuple[str, ...]]:
        """pipeline id -> the pipeline ids providing the capabilities it requires.

        The inter-pipeline dependency graph, derived from the capability declarations
        rather than declared twice. A self-edge is dropped: a pipeline that both provides
        and requires a capability satisfies itself, and a self-dependency would be a
        spurious cycle.
        """
        graph = self.capability_graph()
        edges: dict[str, set[str]] = {pid: set() for pid in self.pipeline_ids}
        for sides in graph.values():
            for consumer in sides["required_by"]:
                for provider in sides["provided_by"]:
                    if provider != consumer:
                        edges[consumer].add(provider)
        return {pid: tuple(sorted(providers)) for pid, providers in sorted(edges.items())}

    def unsatisfied_capabilities(self) -> tuple[tuple[str, str], ...]:
        """``(pipeline id, capability id)`` for every requirement nothing provides.

        A dead-capability / broken-closure finding, reported rather than left implicit.
        """
        graph = self.capability_graph()
        return tuple(
            sorted(
                (consumer, capability_id)
                for capability_id, sides in graph.items()
                if not sides["provided_by"]
                for consumer in sides["required_by"]
            )
        )

    def unconsumed_capabilities(self) -> tuple[tuple[str, str], ...]:
        """``(pipeline id, capability id)`` for every provision nothing requires.

        Not an error — a capability may be provided for an external consumer — but a
        dead-capability *finding*, so it is measured rather than assumed away.
        """
        graph = self.capability_graph()
        return tuple(
            sorted(
                (provider, capability_id)
                for capability_id, sides in graph.items()
                if not sides["required_by"]
                for provider in sides["provided_by"]
            )
        )

    # -- integrity --------------------------------------------------------------------

    def verify(self) -> bool:
        """True iff every entry's stored plan is still the plan its declaration derives."""
        return all(entry.plan == entry.replan() for entry in self._entries.values())

    def require_intact(self) -> None:
        """Fail closed unless every stored plan matches its re-derivation.

        Raises:
            PipelineRegistryError: naming the first entry whose stored plan no longer
                follows from its declaration — i.e. an entry was constructed by hand
                rather than admitted through :meth:`register`.
        """
        for entry in self.entries:
            if entry.plan != entry.replan():
                raise PipelineRegistryError(
                    "registered plan does not match its declaration",
                    pipeline_id=entry.pipeline_id,
                    version=entry.version,
                )

    # -- internals / evidence ---------------------------------------------------------

    def _latest_or_none(self, pipeline_id: str) -> PipelineRegistryEntry | None:
        found = [entry for entry in self._entries.values() if entry.pipeline_id == pipeline_id]
        if not found:
            return None
        return max(found, key=lambda e: e.semantic_version())

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable render of the registry (evidence)."""
        return {
            "entry_count": len(self._entries),
            "pipeline_count": len(self.pipeline_ids),
            "pipeline_types_registered": list(self.pipeline_types_registered),
            "entries": [entry.to_dict() for entry in self.entries],
            "capability_graph": self.capability_graph(),
            "pipeline_dependencies": {
                pid: list(providers) for pid, providers in self.pipeline_dependencies().items()
            },
            "unsatisfied_capabilities": [list(pair) for pair in self.unsatisfied_capabilities()],
            "unconsumed_capabilities": [list(pair) for pair in self.unconsumed_capabilities()],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of the whole registry."""
        return content_hash(self.to_dict())

    @property
    def identity(self) -> Identity:
        """The content-addressed identity of the registry's current contents."""
        return mint("catalog", "pipeline-registry", self.fingerprint())


__all__ = ["PipelineRegistry", "PipelineRegistryEntry"]
