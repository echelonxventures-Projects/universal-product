"""UAPF-000001 — the Universal Autonomous Pipeline Framework (UAPF).

The constitutional execution foundation for every autonomous activity in UCOS Ω∞. UAPF
hosts an **unbounded** number of autonomous pipelines: a pipeline is *declared as
metadata* and its behaviour is *derived* from that declaration, so admitting one more
pipeline, stage, pipeline type, event category, object kind, stage handler, policy, gate
or plugin is a data entry and never a change to this package.

Reuse posture (Reuse First / No Parallel Authority)
---------------------------------------------------
UAPF creates no ordering mechanism, no second event substrate, no second dependency
algorithm and no second lifecycle discipline. It composes the canonical authorities the
repository already owns:

===========================  ==================================================
Concern                      Canonical authority reused
===========================  ==================================================
Stage / pipeline ordering    :mod:`engine.foundation.composition` (``derive_order``)
Dependency graph + topology  :class:`platform.foundation.dependencies.DependencyGraph`
Event substrate              :class:`platform.foundation.dag_ledger.EventDag`
Canonical hashing            :func:`platform.foundation.contracts.content_hash`
Contract references          :class:`platform.foundation.contracts.ContractRef`
Error discipline             :class:`platform.foundation.errors.PlatformError`
Execution-unit lifecycle     ``06-IMPLEMENTATION-STATE-MACHINE.md`` (Repository Truth)
Queue topology + operations  ``04-EXECUTION-QUEUE-MODEL.md`` (Repository Truth)
===========================  ==================================================

Determinism
-----------
Every module here is pure over its inputs: no wall-clock, no RNG, no network, no ambient
state, no filesystem. Identical declarations therefore yield byte-identical plans,
schedules, queues, transactions, records and fingerprints in every environment. UAPF
governs and records; like the certified runtime plane it invokes no live compute and
never writes the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.universal_pipeline.assurance import (
    CertificationRecord,
    PipelineAssurance,
    ValidationRecord,
    VerificationRecord,
)
from platform.universal_pipeline.contracts import (
    PipelineCapability,
    PipelineDefinition,
    PipelineGateSpec,
    PipelineGovernanceSpec,
    PipelinePlan,
    PipelinePlugin,
    PipelinePolicy,
    PipelineSecuritySpec,
    StageDefinition,
    pipeline_types,
    register_pipeline_type,
    require_pipeline_type,
)
from platform.universal_pipeline.dependencies import DependencyClosure, DependencyManager
from platform.universal_pipeline.discovery import DiscoveryReport, PipelineDiscovery, load_catalog
from platform.universal_pipeline.errors import UniversalPipelineError
from platform.universal_pipeline.events import (
    PipelineEventBus,
    event_categories,
    register_event_category,
)
from platform.universal_pipeline.execution import (
    ExecutionUnit,
    ExecutionUnitRecord,
    PipelineRuntime,
)
from platform.universal_pipeline.gateway import GatewayTransaction, UniversalPipelineGateway
from platform.universal_pipeline.governance import (
    GovernanceVerdict,
    PipelineGovernance,
    RecoveryPoint,
)
from platform.universal_pipeline.handlers import (
    StageContext,
    StageOutcome,
    register_stage_handler,
    stage_handler_names,
)
from platform.universal_pipeline.identity import Identity, mint, object_kinds, register_object_kind
from platform.universal_pipeline.observability import PipelineObservability, PipelineTelemetry
from platform.universal_pipeline.orchestrator import OrchestrationTick, UniversalWorkOrchestrator
from platform.universal_pipeline.queue import PipelineQueueManager, QueueEntry
from platform.universal_pipeline.registry import PipelineRegistry, PipelineRegistryEntry
from platform.universal_pipeline.scheduler import PipelineSchedule, PipelineScheduler
from platform.universal_pipeline.service import UniversalPipelinePlatform
from platform.universal_pipeline.state import EXECUTION_UNIT_STATES, require_unit_transition

#: The semantic version of the UAPF contract surface (AR-03 / PL-05).
UAPF_VERSION = "1.0.0"

#: The programme identity that owns this framework (derived truth; asserts no authority).
UAPF_PROGRAMME = "UAPF-000001"

__all__ = [
    "UAPF_PROGRAMME",
    "UAPF_VERSION",
    "EXECUTION_UNIT_STATES",
    "CertificationRecord",
    "DependencyClosure",
    "DependencyManager",
    "DiscoveryReport",
    "ExecutionUnit",
    "ExecutionUnitRecord",
    "GatewayTransaction",
    "GovernanceVerdict",
    "Identity",
    "OrchestrationTick",
    "PipelineAssurance",
    "PipelineCapability",
    "PipelineDefinition",
    "PipelineDiscovery",
    "PipelineEventBus",
    "PipelineGateSpec",
    "PipelineGovernance",
    "PipelineGovernanceSpec",
    "PipelineObservability",
    "PipelinePlan",
    "PipelinePlugin",
    "PipelinePolicy",
    "PipelineQueueManager",
    "PipelineRegistry",
    "PipelineRegistryEntry",
    "PipelineRuntime",
    "PipelineSchedule",
    "PipelineScheduler",
    "PipelineSecuritySpec",
    "PipelineTelemetry",
    "QueueEntry",
    "RecoveryPoint",
    "StageContext",
    "StageDefinition",
    "StageOutcome",
    "UniversalPipelineError",
    "UniversalPipelineGateway",
    "UniversalPipelinePlatform",
    "UniversalWorkOrchestrator",
    "ValidationRecord",
    "VerificationRecord",
    "event_categories",
    "load_catalog",
    "mint",
    "object_kinds",
    "pipeline_types",
    "register_event_category",
    "register_object_kind",
    "register_pipeline_type",
    "register_stage_handler",
    "require_pipeline_type",
    "require_unit_transition",
    "stage_handler_names",
]
