"""EC-1 Runtime Assembly (EPIC-005) — IMP-007 §8 deployable runtime units.

Public API surface for the Runtime Assembly engine: it transforms a **published
compiler package** (EPIC-003, TASK-000027) into a deployable, reversible
:class:`RuntimeUnit` for the IMP-008 Runtime Platform, and generates the
deployment and rollback definitions that carry it.

The engine is additive engineering code built on the EC-1 Foundation (EPIC-001),
the Registry Adapter (EPIC-002), the Universal Compiler (EPIC-003), and the
Determinism Framework (EPIC-004), all reused verbatim (Mandatory Rule 4). It binds
only registered, certified components (§15), validates provenance/signature/SBOM
before emitting anything (§1/§12), references secrets only (SEC-04), generates
deterministic descriptors (§5), produces reversible checkpoint-based rollback
(IP-08), and stamps every unit with the EC-1 provisional-state disclosure
(DE-05 / C-05). It produces deployable *definitions* only — never a live system.

Tasks: TASK-000034 (assembly engine), TASK-000035 (deployment + rollback),
TASK-000036 (provisional-state disclosure), TASK-000037 (assembly validation).

EPIC-006 (Universal Runtime Composition Engine) extends this package additively:
it **composes existing, already-assembled** :class:`RuntimeUnit` "Universes" into a
deterministic, bounded, acyclic :class:`RuntimeComposition` /
:class:`RuntimeOrchestration` (RUNTIME-013). It reuses the assembly output, the
compiler's cycle/topological primitives, the Foundation observability, and the
EC-1 disclosure verbatim, and adds **no** duplicate assembly, dependency, or
execution logic. Tasks: TASK-000038 (composition graph + dependency resolution),
TASK-000039 (context + reference-frame resolution), TASK-000040 (execution
planner), TASK-000041 (composition engine + dynamic composition), TASK-000042
(runtime orchestration).

EPIC-RTE-002 (Universal Runtime Execution Platform) extends this package further,
additively, in the :mod:`engine.runtime.execution` subpackage: it models execution
as a deterministic, resumable, observable state machine over an existing
:class:`RuntimeComposition` and its recorded :class:`ExecutionPlan`. It reuses the
composition, plan, graph, context, federation, disclosure, and Foundation
observability capabilities **verbatim** and adds **no** duplicate runtime logic; it
executes nothing and holds engineering-execution authority only. See
:mod:`engine.runtime.execution` for its public API (scheduler, coordinator,
lifecycle, monitoring, recovery, continuation, checkpointing, replay, rollback,
isolation, federation, authorization, auditing, metrics, health, diagnostics,
state, snapshot, persistence, and replay validation).
"""

from __future__ import annotations

from engine.runtime.assembly import (
    DEFAULT_RESOURCES,
    RUNTIME_DESCRIPTOR_FORMAT,
    ClosureEntry,
    PublishedPackage,
    RuntimeUnit,
    SecretBinding,
    assemble,
    k8s_name,
)
from engine.runtime.composition import (
    RUNTIME_COMPOSITION_FORMAT,
    RuntimeComposer,
    RuntimeComposition,
    Universe,
    compose,
)
from engine.runtime.context import (
    DEFAULT_CONTEXT,
    Federation,
    ReferenceFrame,
    RuntimeContext,
    resolve_contexts,
    resolve_reference_frames,
)
from engine.runtime.deploy import (
    ROLLBACK_STRATEGY,
    DeploymentDescriptor,
    RollbackDescriptor,
    dependency_closure_record,
    descriptor,
    rollback,
)
from engine.runtime.disclosure import (
    DISCLOSURE_GATE,
    DISCLOSURE_ID,
    DISCLOSURE_STANDARD,
    DISCLOSURE_STATEMENT,
    build_disclosure,
    disclosure_present,
    inject_provisional_state,
    require_disclosure,
)
from engine.runtime.errors import (
    ContextResolutionError,
    DependencyClosureError,
    DeploymentError,
    DisclosureError,
    ExecutionPlanError,
    OrchestrationError,
    ProvenanceValidationError,
    ReferenceFrameError,
    RuntimeAssemblyError,
    RuntimeCompositionError,
    RuntimeGraphError,
    SBOMValidationError,
    SecretExposureError,
    SignatureValidationError,
)
from engine.runtime.graph import DEPENDS_ON, RuntimeGraph
from engine.runtime.orchestration import (
    ORCHESTRATION_FORMAT,
    RuntimeOrchestration,
    orchestrate,
    orchestration_of,
)
from engine.runtime.planner import (
    COORDINATION_CLASSES,
    DEFAULT_COORDINATION,
    EXECUTION_PLAN_FORMAT,
    ExecutionPlan,
    PlanStep,
    plan_execution,
)

__all__ = [
    # assembly
    "assemble",
    "RuntimeUnit",
    "PublishedPackage",
    "ClosureEntry",
    "SecretBinding",
    "RUNTIME_DESCRIPTOR_FORMAT",
    "DEFAULT_RESOURCES",
    "k8s_name",
    # deployment + rollback
    "descriptor",
    "rollback",
    "dependency_closure_record",
    "DeploymentDescriptor",
    "RollbackDescriptor",
    "ROLLBACK_STRATEGY",
    # disclosure
    "inject_provisional_state",
    "build_disclosure",
    "disclosure_present",
    "require_disclosure",
    "DISCLOSURE_ID",
    "DISCLOSURE_STANDARD",
    "DISCLOSURE_GATE",
    "DISCLOSURE_STATEMENT",
    # errors
    "RuntimeAssemblyError",
    "ProvenanceValidationError",
    "SignatureValidationError",
    "SBOMValidationError",
    "DependencyClosureError",
    "SecretExposureError",
    "DisclosureError",
    "DeploymentError",
    # ---- EPIC-006 — Universal Runtime Composition Engine ----
    # graph
    "RuntimeGraph",
    "DEPENDS_ON",
    # context + reference frames
    "RuntimeContext",
    "Federation",
    "ReferenceFrame",
    "resolve_contexts",
    "resolve_reference_frames",
    "DEFAULT_CONTEXT",
    # execution planner
    "ExecutionPlan",
    "PlanStep",
    "plan_execution",
    "COORDINATION_CLASSES",
    "DEFAULT_COORDINATION",
    "EXECUTION_PLAN_FORMAT",
    # composition + dynamic composition
    "Universe",
    "RuntimeComposition",
    "compose",
    "RuntimeComposer",
    "RUNTIME_COMPOSITION_FORMAT",
    # orchestration
    "RuntimeOrchestration",
    "orchestrate",
    "orchestration_of",
    "ORCHESTRATION_FORMAT",
    # composition errors
    "RuntimeCompositionError",
    "RuntimeGraphError",
    "ContextResolutionError",
    "ReferenceFrameError",
    "ExecutionPlanError",
    "OrchestrationError",
]
