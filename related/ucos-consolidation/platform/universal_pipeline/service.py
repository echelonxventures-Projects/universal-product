"""UAPF-000001 — the Universal Autonomous Engineering Platform façade.

One object that composes the whole framework, wired correctly, once. Every engine in this
package is usable in isolation — that is why they are separate modules and why each is
independently testable — but a caller assembling twelve engines by hand would be the place
the wiring silently goes wrong: a runtime built without the queue, a gateway built without
governance, two buses instead of one. :class:`UniversalPipelinePlatform` removes that class
of defect by making the correct composition the only composition on offer.

Composed, not re-implemented
----------------------------
The façade owns no behaviour. It creates the engines, hands each the collaborators it needs,
and exposes them as attributes so nothing is hidden behind it: ``platform.registry`` is the
registry, not a wrapper around one. Its own methods are only the two-or-three-step sequences
a caller would otherwise have to remember in the right order — declare, discover, submit,
run, and the synchronization snapshot.

One bus, one truth
------------------
Every engine shares a single :class:`~platform.universal_pipeline.events.PipelineEventBus`,
so the recorded history of a platform instance is *one* causally-linked DAG rather than
several logs that must be interleaved after the fact. That is the property that makes
:meth:`UniversalPipelinePlatform.state` a complete account: every engine's contribution is
already in the same record.

Instance state and namespace state
----------------------------------
Everything a platform *records* — registry, queues, verdicts, records, telemetry, events —
belongs to the instance, so two instances never interfere. The *vocabularies* (object kinds,
pipeline types, event categories, stage handlers, readiness predicates) are deliberately
process-wide, because they are namespaces and a per-instance namespace would let the same
term mean two things. One visible consequence is worth stating plainly: a second platform
built in the same process sees types the first one already admitted, so its discovery report
records zero *new* types. That is the namespace working, not non-determinism — the
determinism guarantee is that identical declarations produce identical fingerprints in a
fresh process, and it is asserted that way in the tests.

Repository synchronization
--------------------------
:meth:`state` renders every dimension the mission requires to be synchronized — repository
truth, identity, registries, dependency graph, capability graph, ontology, taxonomy,
validation, verification, certification, evidence and traceability — from the engines that
own them, in one deterministic mapping. It restates nothing: every value is read from its
canonical owner, so the snapshot cannot disagree with the platform it describes.
:meth:`fingerprint` reduces it to one hash, which is what a determinism gate compares.
"""

from __future__ import annotations

from collections.abc import Mapping
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.assurance import PipelineAssurance
from platform.universal_pipeline.contracts import (
    PipelineDefinition,
    pipeline_types,
    register_pipeline_type,
)
from platform.universal_pipeline.dependencies import DependencyManager
from platform.universal_pipeline.discovery import DiscoveryReport, PipelineDiscovery
from platform.universal_pipeline.errors import PipelinePlatformError
from platform.universal_pipeline.events import PipelineEventBus, event_categories
from platform.universal_pipeline.execution import PipelineRuntime
from platform.universal_pipeline.gateway import GatewayTransaction, UniversalPipelineGateway
from platform.universal_pipeline.governance import PipelineGovernance
from platform.universal_pipeline.handlers import stage_handler_names
from platform.universal_pipeline.identity import Identity, meta_model, mint, object_kinds
from platform.universal_pipeline.observability import PipelineObservability
from platform.universal_pipeline.orchestrator import (
    OrchestrationTick,
    UniversalWorkOrchestrator,
    readiness_predicate_names,
)
from platform.universal_pipeline.queue import PipelineQueueManager, QueueEntry
from platform.universal_pipeline.registry import PipelineRegistry, PipelineRegistryEntry
from platform.universal_pipeline.scheduler import PipelineSchedule, PipelineScheduler
from platform.universal_pipeline.state import DEFAULT_MAX_RETRY, state_machine
from typing import Any


class UniversalPipelinePlatform:
    """The composed Universal Autonomous Engineering Platform for one workspace."""

    __slots__ = (
        "_bus",
        "_registry",
        "_queue",
        "_dependencies",
        "_scheduler",
        "_governance",
        "_assurance",
        "_observability",
        "_gateway",
        "_runtime",
        "_discovery",
        "_orchestrator",
    )

    def __init__(
        self,
        *,
        source: str | None = None,
        max_batch: int | None = None,
        max_retry: int = DEFAULT_MAX_RETRY,
    ) -> None:
        if max_batch is not None and (not isinstance(max_batch, int) or max_batch < 1):
            raise PipelinePlatformError("max_batch must be a positive integer")
        if not isinstance(max_retry, int) or max_retry < 0:
            raise PipelinePlatformError("max_retry must be a non-negative integer")
        self._bus = PipelineEventBus(source=source) if source else PipelineEventBus()
        self._registry = PipelineRegistry(bus=self._bus)
        self._queue = PipelineQueueManager(bus=self._bus, max_retry=max_retry)
        self._dependencies = DependencyManager()
        self._scheduler = PipelineScheduler()
        self._governance = PipelineGovernance(bus=self._bus)
        self._assurance = PipelineAssurance(bus=self._bus)
        self._observability = PipelineObservability(bus=self._bus)
        self._gateway = UniversalPipelineGateway(
            self._registry, governance=self._governance, bus=self._bus
        )
        self._runtime = PipelineRuntime(
            self._registry,
            queue=self._queue,
            bus=self._bus,
            observability=self._observability,
        )
        self._discovery = PipelineDiscovery(self._registry, bus=self._bus)
        self._orchestrator = UniversalWorkOrchestrator(
            self._registry,
            self._queue,
            self._gateway,
            self._runtime,
            self._assurance,
            governance=self._governance,
            observability=self._observability,
            dependencies=self._dependencies,
            bus=self._bus,
            max_batch=max_batch,
            max_retry=max_retry,
        )

    # -- the engines (exposed, not wrapped) -------------------------------------------

    @property
    def bus(self) -> PipelineEventBus:
        return self._bus

    @property
    def registry(self) -> PipelineRegistry:
        return self._registry

    @property
    def queue(self) -> PipelineQueueManager:
        return self._queue

    @property
    def dependencies(self) -> DependencyManager:
        return self._dependencies

    @property
    def scheduler(self) -> PipelineScheduler:
        return self._scheduler

    @property
    def governance(self) -> PipelineGovernance:
        return self._governance

    @property
    def assurance(self) -> PipelineAssurance:
        return self._assurance

    @property
    def observability(self) -> PipelineObservability:
        return self._observability

    @property
    def gateway(self) -> UniversalPipelineGateway:
        return self._gateway

    @property
    def runtime(self) -> PipelineRuntime:
        return self._runtime

    @property
    def discovery(self) -> PipelineDiscovery:
        return self._discovery

    @property
    def orchestrator(self) -> UniversalWorkOrchestrator:
        return self._orchestrator

    @property
    def identity(self) -> Identity:
        """The content-addressed identity of this platform's current state."""
        return mint("platform", "uapf", self.fingerprint())

    # -- declaration ------------------------------------------------------------------

    def register_type(self, pipeline_type: str, description: str = "") -> None:
        """Admit a new pipeline category. Idempotent, so calling it twice is safe."""
        if pipeline_type in pipeline_types():
            return
        register_pipeline_type(pipeline_type, description)

    def register(self, definition: PipelineDefinition) -> PipelineRegistryEntry:
        """Register one pipeline declaration and record its declared capability edges.

        The dependency edges between pipelines are derived from the capability declarations
        and re-declared here after every registration, so the dependency graph always
        reflects the registry rather than a snapshot of it.
        """
        entry = self._registry.register(definition)
        self._sync_pipeline_dependencies()
        return entry

    def discover(self, document: str | Mapping[str, Any]) -> DiscoveryReport:
        """Admit every pipeline a declaration catalogue holds, then resynchronize edges."""
        report = self._discovery.discover(document)
        self._sync_pipeline_dependencies()
        return report

    def admit_unit(
        self,
        unit_id: str,
        pipeline_id: str,
        *,
        version: str | None = None,
        wave: int = 1,
        family: str = "",
        depends_on: tuple[str, ...] = (),
    ) -> QueueEntry:
        """Admit one unit of work into the Execution Queue and declare its dependencies.

        Raises:
            PipelinePlatformError: if the unit already declared dependencies (a unit has
                exactly one declaration).
            PipelineRegistryError: if the pipeline version is not registered — a unit for a
                pipeline that does not exist is refused at admission rather than blocked
                later, because there is nothing that could ever unblock it.
        """
        entry = self._registry.get(pipeline_id, version)
        if unit_id in self._dependencies:
            raise PipelinePlatformError("unit already admitted", unit_id=unit_id)
        self._dependencies.declare(unit_id, depends_on)
        return self._queue.enqueue(
            QueueEntry(
                unit_id=unit_id,
                pipeline_id=entry.pipeline_id,
                version=entry.version,
                wave=wave,
                family=family,
            )
        )

    # -- execution --------------------------------------------------------------------

    def submit(
        self,
        pipeline_id: str,
        unit_id: str,
        *,
        version: str | None = None,
        inputs: Mapping[str, Any] | None = None,
        permissions: tuple[str, ...] = (),
        evidence: Mapping[str, Any] | None = None,
    ) -> GatewayTransaction:
        """Admit work through the gateway (the only door into execution)."""
        return self._gateway.submit(
            pipeline_id,
            unit_id,
            version=version,
            inputs=inputs,
            permissions=permissions,
            evidence=evidence,
        )

    def tick(self, **kwargs: Any) -> OrchestrationTick:
        """Perform one autonomous orchestration tick."""
        return self._orchestrator.tick(**kwargs)

    def run(self, **kwargs: Any) -> tuple[OrchestrationTick, ...]:
        """Run autonomously until no tick makes progress (bounded)."""
        return self._orchestrator.run(**kwargs)

    def schedule(self, **kwargs: Any) -> PipelineSchedule:
        """Derive the dependency-safe schedule of every declared node.

        The relationship graph holds two namespaces — bare ids are execution units, and
        ``pipeline:<id>`` nodes are the inter-pipeline edges the registry derives from the
        capability declarations — so the schedule covers both. They share one graph on
        purpose: they are relationships between the same repository, and two graphs would be
        two answers to "what depends on what". The prefix keeps them distinguishable, and no
        edge ever crosses the two namespaces, so neither can constrain the other by accident.
        """
        return self._scheduler.schedule(self._dependencies, **kwargs)

    # -- integrity --------------------------------------------------------------------

    def require_intact(self) -> None:
        """Fail closed unless every canonical invariant this platform can check holds.

        Four independent checks, each owned by the engine that can actually decide it:
        recorded history is Merkle-intact, every registered plan still follows from its
        declaration, the declared dependency graph is closed and acyclic, and the queue
        invariants hold. They are independent on purpose — no single check is the only thing
        standing between the platform and an inconsistent state.

        The dependency check is skipped when nothing is declared, because an empty graph is
        trivially valid and validating it would report nothing.
        """
        self._bus.require_intact()
        self._registry.require_intact()
        if len(self._dependencies):
            self._dependencies.validate()
        self._queue.require_invariants()

    # -- repository synchronization ---------------------------------------------------

    def state(self) -> dict[str, Any]:
        """Every synchronized dimension, read from its canonical owner (evidence).

        The one snapshot: nothing here is restated, recomputed independently or cached, so it
        is impossible for this mapping to disagree with the platform it describes.
        """
        return {
            "programme": self._bus.source,
            "identity": {
                "meta_model": meta_model(),
                "object_kinds": list(object_kinds()),
            },
            "taxonomy": {
                "pipeline_types": list(pipeline_types()),
                "event_categories": list(event_categories()),
                "stage_handlers": list(stage_handler_names()),
                "readiness_predicates": list(readiness_predicate_names()),
            },
            "ontology": {
                "lifecycle": state_machine(),
                "capability_graph": self._registry.capability_graph(),
            },
            "registries": self._registry.to_dict(),
            "dependency_graph": self._dependencies.to_dict(),
            "queues": self._queue.to_dict(),
            "governance": self._governance.to_dict(),
            "assurance": self._assurance.to_dict(),
            "observability": self._observability.to_dict(),
            "gateway": self._gateway.to_dict(),
            "orchestration": self._orchestrator.to_dict(),
            "evidence": self._bus.to_dict(),
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of every synchronized dimension."""
        return content_hash(self.state())

    def summary(self) -> dict[str, Any]:
        """A small, human-readable status line for a dashboard or a gate.

        Derived from :meth:`state` rather than measured independently, so the short view and
        the full view can never disagree.
        """
        snapshot = self.state()
        return {
            "programme": snapshot["programme"],
            "pipeline_types": len(snapshot["taxonomy"]["pipeline_types"]),
            "pipelines_registered": snapshot["registries"]["entry_count"],
            "units_admitted": snapshot["queues"]["admitted"],
            "ready": len(snapshot["queues"]["ready_queue"]),
            "blocked": len(snapshot["queues"]["blocked_set"]),
            "completed": len(snapshot["queues"]["completed"]),
            "certified": snapshot["assurance"]["certification_count"],
            "ticks": snapshot["orchestration"]["tick_count"],
            "events": snapshot["evidence"]["event_count"],
            "health": snapshot["observability"]["health"]["status"],
            "fingerprint": content_hash(snapshot),
        }

    # -- internals --------------------------------------------------------------------

    def _sync_pipeline_dependencies(self) -> None:
        """Declare the inter-pipeline edges the registry derives, without re-declaring.

        The dependency manager refuses a duplicate declaration by design (a node has exactly
        one declaration), so only *new* pipeline ids are declared here. An existing pipeline
        whose capability declarations changed does so by registering a new *version*, which
        is a new entry rather than a mutation — so there is nothing to update.
        """
        for pipeline_id, providers in self._registry.pipeline_dependencies().items():
            node = f"pipeline:{pipeline_id}"
            if node in self._dependencies:
                continue
            edges = tuple(f"pipeline:{provider}" for provider in providers)
            self._dependencies.declare(node, edges)
            self._bus.emit(
                "uapf.dependency.declared",
                node,
                payload={"node": node, "depends_on": list(edges)},
            )


__all__ = ["UniversalPipelinePlatform"]
