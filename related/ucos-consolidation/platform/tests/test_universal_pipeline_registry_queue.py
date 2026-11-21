"""UAPF-000001 — tests for the registry engine, the derived queues and the batch former.

The registry claim under test: it stores a declaration and its derived plan and *nothing
derivable* — so supersession, the capability graph and the inter-pipeline dependency edges are
computed, and :meth:`require_intact` can prove a stored plan still follows from its declaration.

The queue claim: membership and order are derived, never chosen. There is no operation that can
reorder a queue or enqueue by hand, and every membership change passes the lifecycle guard — so
``04`` §5's invariants hold by construction. Batching is tested against ``05`` §2 rule by rule.
"""

from __future__ import annotations

import dataclasses
from platform.foundation.contracts import ContractRef
from platform.universal_pipeline.contracts import (
    PipelineCapability,
    PipelineDefinition,
    PipelinePlan,
    StageDefinition,
)
from platform.universal_pipeline.errors import (
    PipelineQueueError,
    PipelineRegistryError,
    PipelineStateError,
)
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.queue import PipelineQueueManager, QueueEntry
from platform.universal_pipeline.registry import PipelineRegistry, PipelineRegistryEntry

import pytest


def _definition(
    pipeline_id: str = "test.pipeline",
    version: str = "1.0.0",
    *,
    pipeline_type: str = "evolution",
    capabilities: tuple[PipelineCapability, ...] = (),
) -> PipelineDefinition:
    return PipelineDefinition(
        pipeline_id=pipeline_id,
        pipeline_type=pipeline_type,
        version=version,
        stages=(StageDefinition(stage_id="only", handler="uapf.record"),),
        capabilities=capabilities,
    )


def _entry(unit_id: str, *, wave: int = 1, family: str = "") -> QueueEntry:
    return QueueEntry(
        unit_id=unit_id, pipeline_id="test.pipeline", version="1.0.0", wave=wave, family=family
    )


def _queue(**kwargs: object) -> PipelineQueueManager:
    return PipelineQueueManager(**kwargs)  # type: ignore[arg-type]


# ------------------------------------------------------------------------------ registry


def test_registration_derives_the_plan_rather_than_accepting_one() -> None:
    registry = PipelineRegistry()
    entry = registry.register(_definition())
    assert entry.plan == PipelinePlan.derive(entry.definition)
    assert entry.pipeline_id == "test.pipeline"
    assert entry.pipeline_type == "evolution"
    assert entry.version == "1.0.0"
    assert entry.ordinal == 0
    assert entry.key == ("test.pipeline", "1.0.0")
    assert entry.identity == entry.definition.identity
    assert entry.replan() == entry.plan
    assert entry.to_dict()["stage_count"] == 1
    assert entry.fingerprint() == registry.get("test.pipeline").fingerprint()
    assert ("test.pipeline", "1.0.0") in registry
    assert len(registry) == 1


def test_a_version_is_registered_once() -> None:
    registry = PipelineRegistry()
    registry.register(_definition())
    with pytest.raises(PipelineRegistryError, match="already registered"):
        registry.register(_definition())
    with pytest.raises(PipelineRegistryError, match="only a PipelineDefinition"):
        registry.register("not a definition")  # type: ignore[arg-type]


def test_latest_is_the_greatest_version_not_the_most_recently_registered() -> None:
    registry = PipelineRegistry()
    registry.register(_definition(version="1.2.0"))
    registry.register(_definition(version="1.10.0"))
    # Registered last, but lower — precedence is by semantic version, not arrival.
    registry.register(_definition(version="1.3.0"))
    assert registry.versions("test.pipeline") == ("1.2.0", "1.3.0", "1.10.0")
    assert registry.latest("test.pipeline").version == "1.10.0"
    assert registry.get("test.pipeline").version == "1.10.0"
    assert registry.get("test.pipeline", "1.2.0").version == "1.2.0"
    assert registry.is_superseded("test.pipeline", "1.3.0")
    assert not registry.is_superseded("test.pipeline", "1.10.0")


def test_registry_lookups_fail_closed_rather_than_returning_none() -> None:
    registry = PipelineRegistry()
    with pytest.raises(PipelineRegistryError, match="no such pipeline registered"):
        registry.latest("absent")
    with pytest.raises(PipelineRegistryError, match="no such pipeline registered"):
        registry.versions("absent")
    registry.register(_definition())
    with pytest.raises(PipelineRegistryError, match="no such pipeline version"):
        registry.get("test.pipeline", "9.9.9")


def test_registry_orders_every_listing_deterministically() -> None:
    registry = PipelineRegistry()
    registry.register(_definition("b.pipeline", "2.0.0", pipeline_type="implementation"))
    registry.register(_definition("a.pipeline", "1.0.0"))
    registry.register(_definition("a.pipeline", "1.1.0"))
    assert [(e.pipeline_id, e.version) for e in registry.entries] == [
        ("a.pipeline", "1.0.0"),
        ("a.pipeline", "1.1.0"),
        ("b.pipeline", "2.0.0"),
    ]
    assert registry.pipeline_ids == ("a.pipeline", "b.pipeline")
    assert registry.pipeline_types_registered == ("evolution", "implementation")
    assert [e.pipeline_id for e in registry.by_type("implementation")] == ["b.pipeline"]
    # A registered type with no pipeline is the open-world case, not a failure.
    assert registry.by_type("research") == ()


def test_capability_and_dependency_graphs_are_derived_from_declarations() -> None:
    registry = PipelineRegistry()
    registry.register(
        _definition(
            "provider",
            capabilities=(PipelineCapability("cap.x", ContractRef("c.x"), "provides"),),
        )
    )
    registry.register(
        _definition(
            "consumer",
            pipeline_type="implementation",
            capabilities=(
                PipelineCapability("cap.x", ContractRef("c.x"), "requires"),
                PipelineCapability("cap.missing", ContractRef("c.m"), "requires"),
            ),
        )
    )
    graph = registry.capability_graph()
    assert graph["cap.x"] == {"provided_by": ["provider"], "required_by": ["consumer"]}
    assert graph["cap.missing"] == {"provided_by": [], "required_by": ["consumer"]}
    assert registry.pipeline_dependencies() == {"consumer": ("provider",), "provider": ()}
    assert registry.unsatisfied_capabilities() == (("consumer", "cap.missing"),)
    assert registry.unconsumed_capabilities() == ()


def test_only_the_latest_version_contributes_to_the_capability_surface() -> None:
    registry = PipelineRegistry()
    registry.register(
        _definition(
            "p",
            "1.0.0",
            capabilities=(PipelineCapability("cap.old", ContractRef("c"), "provides"),),
        )
    )
    registry.register(
        _definition(
            "p",
            "2.0.0",
            capabilities=(PipelineCapability("cap.new", ContractRef("c"), "provides"),),
        )
    )
    assert set(registry.capability_graph()) == {"cap.new"}
    assert registry.unconsumed_capabilities() == (("p", "cap.new"),)


def test_a_self_satisfying_pipeline_does_not_depend_on_itself() -> None:
    registry = PipelineRegistry()
    registry.register(
        _definition(
            "p",
            capabilities=(
                PipelineCapability("cap", ContractRef("c"), "provides"),
                PipelineCapability("cap", ContractRef("c"), "requires"),
            ),
        )
    )
    assert registry.pipeline_dependencies() == {"p": ()}


def test_registry_integrity_detects_a_plan_that_no_longer_follows() -> None:
    registry = PipelineRegistry()
    registry.register(_definition())
    assert registry.verify()
    registry.require_intact()
    # An entry cannot be built with a mismatched plan at all.
    other = PipelinePlan.derive(_definition("other.pipeline"))
    with pytest.raises(PipelineRegistryError, match="different pipeline"):
        PipelineRegistryEntry(definition=_definition(), plan=other, ordinal=0)
    mismatched_version = PipelinePlan.derive(_definition(version="2.0.0"))
    with pytest.raises(PipelineRegistryError, match="different version"):
        PipelineRegistryEntry(definition=_definition(), plan=mismatched_version, ordinal=0)


def test_registry_entry_validates_its_own_shape() -> None:
    definition = _definition()
    plan = PipelinePlan.derive(definition)
    with pytest.raises(PipelineRegistryError, match="requires a PipelineDefinition"):
        PipelineRegistryEntry(definition="x", plan=plan, ordinal=0)  # type: ignore[arg-type]
    with pytest.raises(PipelineRegistryError, match="requires a PipelinePlan"):
        PipelineRegistryEntry(definition=definition, plan="x", ordinal=0)  # type: ignore[arg-type]
    with pytest.raises(PipelineRegistryError, match="ordinal must be non-negative"):
        PipelineRegistryEntry(definition=definition, plan=plan, ordinal=-1)


def test_registry_records_registration_supersession_and_capabilities_on_the_bus() -> None:
    bus = PipelineEventBus()
    registry = PipelineRegistry(bus=bus)
    registry.register(
        _definition(capabilities=(PipelineCapability("cap", ContractRef("c"), "provides"),))
    )
    assert len(bus.events_of("uapf.pipeline.registered")) == 1
    assert len(bus.events_of("uapf.capability.declared")) == 1
    assert bus.events_of("uapf.pipeline.superseded") == ()
    registry.register(_definition(version="2.0.0"))
    superseded = bus.events_of("uapf.pipeline.superseded")
    assert len(superseded) == 1
    assert superseded[0].payload["superseding_version"] == "2.0.0"
    # Registering an older version supersedes nothing.
    registry.register(_definition(version="1.5.0"))
    assert len(bus.events_of("uapf.pipeline.superseded")) == 1
    with pytest.raises(PipelineRegistryError, match="must be a PipelineEventBus"):
        PipelineRegistry(bus="not a bus")  # type: ignore[arg-type]


def test_registry_evidence_is_deterministic() -> None:
    def build() -> PipelineRegistry:
        registry = PipelineRegistry()
        registry.register(_definition("b.pipeline"))
        registry.register(_definition("a.pipeline"))
        return registry

    left, right = build(), build()
    assert left.fingerprint() == right.fingerprint()
    assert left.identity.kind == "catalog"
    assert left.to_dict()["entry_count"] == 2


# --------------------------------------------------------------------------------- queue


def test_a_unit_joins_the_execution_queue_in_the_initial_state() -> None:
    queue = _queue()
    entry = queue.enqueue(_entry("u1"))
    assert entry.state == "SPECIFIED"
    assert [e.unit_id for e in queue.execution_queue] == ["u1"]
    assert queue.ready_queue == ()
    assert "u1" in queue
    assert len(queue) == 1
    assert queue.entry("u1") == entry
    assert entry.identity.kind == "queue-entry"
    assert entry.position == (1, "", "u1")
    assert entry.fingerprint() == queue.entry("u1").fingerprint()


def test_admission_is_single_and_must_be_in_the_initial_state() -> None:
    queue = _queue()
    queue.enqueue(_entry("u1"))
    with pytest.raises(PipelineQueueError, match="already admitted"):
        queue.enqueue(_entry("u1"))
    with pytest.raises(PipelineQueueError, match="only a QueueEntry"):
        queue.enqueue("u2")  # type: ignore[arg-type]
    with pytest.raises(PipelineQueueError, match="admitted in the initial state"):
        queue.enqueue(dataclasses.replace(_entry("u2"), state="READY"))
    with pytest.raises(PipelineQueueError, match="no such unit"):
        queue.entry("absent")


def test_queue_order_is_wave_then_family_then_id() -> None:
    queue = _queue()
    for unit_id, wave, family in [
        ("z", 1, "A"),
        ("a", 2, "A"),
        ("m", 1, "B"),
        ("b", 1, "A"),
    ]:
        queue.enqueue(_entry(unit_id, wave=wave, family=family))
    assert [e.unit_id for e in queue.execution_queue] == ["b", "z", "m", "a"]


def test_promotion_demotion_and_re_promotion_preserve_derived_position() -> None:
    queue = _queue()
    queue.enqueue(_entry("u1"))
    queue.enqueue(_entry("u2"))
    queue.promote("u1")
    assert [e.unit_id for e in queue.ready_queue] == ["u1"]
    blocked = queue.demote("u2", "BLOCKED:PREDECESSOR-WAVE")
    assert blocked.state == "BLOCKED"
    assert [(e.unit_id, e.reason) for e in queue.blocked_set] == [
        ("u2", "BLOCKED:PREDECESSOR-WAVE")
    ]
    queue.promote("u2")
    assert [e.unit_id for e in queue.ready_queue] == ["u1", "u2"]
    with pytest.raises(PipelineQueueError, match="block reason is required"):
        queue.demote("u1", "")


def test_a_sentinel_is_excluded_and_never_batched() -> None:
    queue = _queue()
    queue.enqueue(_entry("real"))
    queue.enqueue(_entry("sentinel"))
    excluded = queue.exclude("sentinel", "NOT REQUIRED")
    assert excluded.excluded
    assert [e.unit_id for e in queue.excluded_set] == ["sentinel"]
    assert [e.unit_id for e in queue.execution_queue] == ["real"]
    queue.promote("real")
    assert [e.unit_id for e in queue.cut()] == ["real"]
    queue.require_invariants()
    with pytest.raises(PipelineQueueError, match="never promoted"):
        queue.promote("sentinel")
    with pytest.raises(PipelineQueueError, match="exclusion reason is required"):
        queue.exclude("real", "")


def test_work_in_flight_cannot_be_excluded() -> None:
    queue = _queue()
    queue.enqueue(_entry("u1"))
    queue.promote("u1")
    queue.cut()
    with pytest.raises(PipelineQueueError, match="not-yet-executing"):
        queue.exclude("u1", "too late")


def test_a_batch_is_drawn_from_one_wave_only_and_capped() -> None:
    queue = _queue()
    for index in range(3):
        queue.enqueue(_entry(f"w1-{index}", wave=1))
    queue.enqueue(_entry("w2-0", wave=2))
    for entry in list(queue.execution_queue):
        queue.promote(entry.unit_id)
    first = queue.cut(max_batch=2)
    assert [e.unit_id for e in first] == ["w1-0", "w1-1"]
    assert all(e.state == "EXECUTING" for e in first)
    queue.require_invariants()
    # The wave is derived (the lowest present), never chosen: wave 1 must drain first.
    second = queue.cut()
    assert [e.unit_id for e in second] == ["w1-2"]
    for unit_id in ("w1-0", "w1-1", "w1-2"):
        queue.advance(unit_id, "IMPLEMENTED")
    assert [e.unit_id for e in queue.cut()] == ["w2-0"]


def test_cutting_an_empty_ready_queue_is_a_normal_steady_state() -> None:
    queue = _queue()
    assert queue.cut() == ()
    with pytest.raises(PipelineQueueError, match="max_batch must be a positive integer"):
        queue.cut(max_batch=0)


def test_a_unit_reaches_the_completed_sink_through_the_lifecycle() -> None:
    queue = _queue()
    queue.enqueue(_entry("u1"))
    queue.promote("u1")
    queue.cut()
    for state in ("IMPLEMENTED", "VALIDATED", "CERTIFIED"):
        queue.advance("u1", state)
    assert [e.unit_id for e in queue.completed] == ["u1"]
    assert queue.execution_queue == ()
    queue.retire("u1", to_state="ARCHIVED")
    assert [e.unit_id for e in queue.completed] == ["u1"]


def test_an_illegal_transition_cannot_enter_a_queue() -> None:
    queue = _queue()
    queue.enqueue(_entry("u1"))
    with pytest.raises(PipelineStateError, match="illegal"):
        queue.advance("u1", "CERTIFIED")
    with pytest.raises(PipelineStateError, match="illegal"):
        queue.fail("u1", "not executing yet")
    with pytest.raises(PipelineQueueError, match="terminal state"):
        queue.retire("u1", to_state="READY")


def test_failure_retry_and_exhaustion_are_bounded() -> None:
    queue = _queue(max_retry=2)
    queue.enqueue(_entry("u1"))
    queue.promote("u1")
    queue.cut()
    queue.fail("u1", "boom")
    assert [(e.unit_id, e.reason) for e in queue.failed] == [("u1", "boom")]
    assert queue.retry("u1").attempts == 1
    queue.cut()
    queue.fail("u1", "boom again")
    assert queue.retry("u1").attempts == 2
    queue.cut()
    queue.fail("u1", "boom once more")
    # Budget exhausted: an error, so the caller must escalate rather than drop the unit.
    with pytest.raises(PipelineStateError, match="retry budget exhausted"):
        queue.retry("u1")
    queue.retire("u1", to_state="ARCHIVED")


def test_a_failure_must_state_its_reason() -> None:
    queue = _queue()
    queue.enqueue(_entry("u1"))
    queue.promote("u1")
    queue.cut()
    with pytest.raises(PipelineQueueError, match="failure reason is required"):
        queue.fail("u1", "")


def test_queue_records_every_membership_change_on_the_bus() -> None:
    bus = PipelineEventBus()
    queue = _queue(bus=bus)
    queue.enqueue(_entry("u1"))
    queue.promote("u1")
    queue.cut()
    queue.advance("u1", "IMPLEMENTED")
    assert len(bus.events_of("uapf.queue.enqueued")) == 1
    assert len(bus.events_of("uapf.queue.promoted")) == 1
    assert len(bus.events_of("uapf.queue.cut")) == 1
    assert len(bus.events_of("uapf.unit.state-changed")) == 1
    assert bus.events_of("uapf.queue.cut")[0].payload["wave"] == 1


def test_queue_construction_is_validated() -> None:
    with pytest.raises(PipelineQueueError, match="must be a PipelineEventBus"):
        _queue(bus="x")
    with pytest.raises(PipelineQueueError, match="max_retry must be non-negative"):
        _queue(max_retry=-1)


@pytest.mark.parametrize(
    ("overrides", "match"),
    [
        ({"unit_id": ""}, "unit id is required"),
        ({"pipeline_id": ""}, "pipeline id is required"),
        ({"version": ""}, "version is required"),
        ({"wave": 0}, "wave must be an integer"),
        ({"wave": True}, "wave must be an integer"),
        ({"family": 1}, "family must be a string"),
        ({"attempts": -1}, "attempts must be non-negative"),
    ],
)
def test_queue_entry_validates_its_own_shape(overrides: dict[str, object], match: str) -> None:
    fields: dict[str, object] = {
        "unit_id": "u1",
        "pipeline_id": "p",
        "version": "1.0.0",
    }
    fields.update(overrides)
    with pytest.raises(PipelineQueueError, match=match):
        QueueEntry(**fields)  # type: ignore[arg-type]


def test_invariants_detect_a_multi_wave_batch() -> None:
    queue = _queue()
    queue.enqueue(_entry("w1", wave=1))
    queue.enqueue(_entry("w2", wave=2))
    queue.promote("w1")
    queue.promote("w2")
    queue.cut()
    queue.cut()
    # Two cuts have put two waves in flight at once, which B1 forbids.
    with pytest.raises(PipelineQueueError, match="one wave only"):
        queue.require_invariants()


def test_queue_evidence_is_deterministic() -> None:
    def build() -> PipelineQueueManager:
        queue = _queue()
        queue.enqueue(_entry("b"))
        queue.enqueue(_entry("a"))
        queue.promote("a")
        return queue

    left, right = build(), build()
    assert left.fingerprint() == right.fingerprint()
    rendered = left.to_dict()
    assert rendered["admitted"] == 2
    assert rendered["ready_queue"] == ["a"]
    assert [e["unit_id"] for e in rendered["entries"]] == ["a", "b"]


def test_a_capability_graph_lists_each_provider_once(monkeypatch) -> None:
    """THE CAPABILITY GRAPH IS A SET OF PROVIDERS, NOT A COUNT OF DECLARATIONS.

    A pipeline appearing twice on one side of a capability would make the graph report two
    providers for a capability with one owner — exactly the shape an unsatisfied- or
    duplicated-capability check is meant to detect. It cannot happen today:
    ``PipelineDefinition`` refuses a duplicate declaration and ``pipeline_ids`` is a set, so
    each id is visited once. The guard is what keeps that true if either stops being.
    """
    registry = PipelineRegistry()
    registry.register(
        PipelineDefinition(
            pipeline_id="test.provider",
            pipeline_type="implementation",
            version="1.0.0",
            stages=(StageDefinition(stage_id="a", handler="uapf.record"),),
            capabilities=(PipelineCapability("cap.x", ContractRef("c.x"), "provides"),),
        )
    )
    assert registry.capability_graph()["cap.x"]["provided_by"] == ["test.provider"]

    monkeypatch.setattr(
        type(registry),
        "pipeline_ids",
        property(lambda _self: ("test.provider", "test.provider")),
    )
    assert registry.capability_graph()["cap.x"]["provided_by"] == ["test.provider"]


def test_a_registry_entry_whose_plan_no_longer_follows_from_its_declaration_is_refused() -> None:
    """A PLAN IS DERIVED, so a stored one that does not re-derive was written by hand.

    ``register`` computes the plan from the definition, which is why the integrity check has
    never fired: every admitted entry re-plans to what it holds. It is the check for an entry
    constructed directly — and a plan that does not follow from its declaration would execute
    stages the pipeline never declared, in an order nothing derived.
    """
    registry = PipelineRegistry()
    registry.register(
        PipelineDefinition(
            pipeline_id="test.replanned",
            pipeline_type="implementation",
            version="1.0.0",
            stages=(
                StageDefinition(stage_id="a", handler="uapf.record"),
                StageDefinition(stage_id="b", handler="uapf.record", requires=("a",)),
            ),
        )
    )
    registry.require_intact()

    entry = registry.entries[0]
    forged = dataclasses.replace(
        entry, plan=dataclasses.replace(entry.plan, waves=((0, "b"), (1, "a")))
    )
    registry._entries[0] = forged  # noqa: SLF001 - deliberate corruption

    with pytest.raises(PipelineRegistryError, match="does not match its declaration"):
        registry.require_intact()


def test_an_excluded_sentinel_that_is_also_an_active_unit_is_refused() -> None:
    """EXCLUSION AND ACTIVITY ARE MUTUALLY EXCLUSIVE CLAIMS.

    A unit cannot both be excluded from the run and be in a queue the run is working
    through: whichever the orchestrator consulted first would decide, and the other claim
    would be silently ignored. The refusal names the overlapping units so the contradiction
    can be resolved rather than merely detected.
    """
    manager = PipelineQueueManager()
    manager.enqueue(QueueEntry(unit_id="live", pipeline_id="p", version="1.0.0"))
    manager.require_invariants()

    # An entry that is BOTH excluded and still in an active queue: `exclude` moves the
    # unit out, so this state is reached by putting the excluded sentinel back.
    manager.exclude("live", reason="deliberate")
    excluded = manager.entry("live")

    # An entry that is BOTH excluded and active cannot arise through the queue: every
    # active-queue accessor filters on ``excluded is False``, and one unit has one flag.
    # The state is reached with a SECOND record under the same unit id — which is what a
    # rehydrated or hand-assembled queue would hold — so the check is exercised on the
    # contradiction it exists to name.
    manager._entries["live-active"] = dataclasses.replace(  # noqa: SLF001 - deliberate
        excluded, state="READY", excluded=False
    )

    with pytest.raises(PipelineQueueError, match="disjoint from every active queue"):
        manager.require_invariants()
