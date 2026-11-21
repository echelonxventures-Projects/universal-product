"""TASK-000041 — Generation Orchestrator (EPIC-006).

The single execution path of the Factory Layer. What it does for each request is
**declared** as a phase graph in :mod:`engine.factory.phases`; the order in which it
does it is **derived** from those declarations through
:mod:`engine.foundation.composition`, the one ordering authority the repository has.
The declared phases are:

    * ``resolve-blueprint`` — resolves the blueprint document through an injected
      :class:`~engine.determinism.reproduce.BlueprintProvider` (no direct filesystem
      scanning by the orchestrator);
    * ``classify`` — resolves the classification from registry metadata: the registered
      :class:`~engine.registry.models.Artifact` when the blueprint is registered,
      otherwise the blueprint document's declared metadata;
    * ``resolve-factory`` — resolves the factory via the
      :class:`~engine.factory.registry.FactoryRegistry` and binds the
      :class:`~engine.factory.factories.base.ExecutionContext`. This phase declares the
      **seam**: execution is handed to the resolved factory, which hands it straight back
      to :meth:`execute`, so no factory holds pipeline logic;
    * ``compile`` — executes the compiler pipeline (EPIC-003) through the RegistryAdapter,
      which enforces certification and family support;
    * ``assemble``, ``deploy``, ``rollback`` — execute the runtime pipeline (EPIC-005) on
      the published artifact;
    * ``evidence`` — produces a :class:`~engine.factory.contracts.FactoryResult` with a
      deterministic Generation Evidence Record.

``DEC-MCOS-14`` recorded that this file previously carried the order as statement order,
which made it a second ordering mechanism beside the derived plan of
:mod:`engine.civilization.composition`. ``WP-UCDA-018`` required a single composition
path. There is now one: declaring a further phase changes the order this orchestrator
executes and the stages every factory advertises, with no edit to either module.

It bypasses nothing: registry access is via the RegistryAdapter, certification and family
gates are the compiler's own, disclosure is the runtime's own, and no artifacts are
invented — a class the compiler defers yields a faithful **gap** result carrying the
compiler's Gap Report (TP-01). A gap short-circuits the runtime phases by *state*, not by
a branch in the order: each runtime phase is a no-op once the compilation carries a gap,
and ``evidence`` reports faithfully either way.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.compiler.pipeline import CompilationResult, CompilerPipeline
from engine.compiler.signing import Signer
from engine.determinism.reproduce import BlueprintProvider, DirectoryBlueprintProvider
from engine.factory.classifier import BlueprintClassification, resolve_blueprint_class
from engine.factory.contracts import (
    FactoryRequest,
    FactoryResult,
    GenerationStatus,
)
from engine.factory.errors import BlueprintResolutionError, OrchestrationError
from engine.factory.evidence import build_generation_evidence
from engine.factory.factories.base import ExecutionContext, Factory
from engine.factory.phases import generation_phase, generation_span, register_generation_phase
from engine.factory.registry import FactoryRegistry
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.registry.adapter import RegistryAdapter
from engine.runtime import assemble, descriptor, disclosure_present, rollback

_logger = get_logger("factory.orchestrator")


@dataclass(slots=True)
class GenerationState:
    """The accumulator threaded through the derived phase order.

    Each declared phase reads what earlier phases produced and records what it produced.
    Because the order is derived rather than written, the state — not statement position —
    is what carries a phase's output to its successor.
    """

    request: FactoryRequest
    document: Mapping[str, Any] | None = None
    classification: BlueprintClassification | None = None
    factory: Factory | None = None
    context: ExecutionContext | None = None
    compilation: CompilationResult | None = None
    unit: Any = None
    result: FactoryResult | None = None

    @property
    def version(self) -> str:
        """The blueprint version as declared by the resolved document."""
        return str((self.document or {}).get("version", ""))

    @property
    def gapped(self) -> bool:
        """True once compilation has produced no publishable artifact (TP-01)."""
        compilation = self.compilation
        return compilation is None or not compilation.success or compilation.published is None

    def bound(self) -> ExecutionContext:
        """The bound execution context, or a loud failure if no phase produced one."""
        if self.context is None:
            raise OrchestrationError("generation phase ran before the execution context was bound")
        return self.context


class GenerationOrchestrator:
    """Runs the declared generation phases in their derived order for one blueprint."""

    __slots__ = ("_registry", "_factories", "_provider", "_signer", "_output_dir")

    def __init__(
        self,
        *,
        registry: RegistryAdapter,
        factories: FactoryRegistry,
        signer: Signer,
        output_dir: str | Path,
        provider: BlueprintProvider | None = None,
    ) -> None:
        self._registry = registry
        self._factories = factories
        self._signer = signer
        self._output_dir = Path(output_dir)
        self._provider = provider if provider is not None else DirectoryBlueprintProvider()

    @property
    def factories(self) -> FactoryRegistry:
        return self._factories

    # -- public API ------------------------------------------------------------

    def generate(self, request: FactoryRequest) -> FactoryResult:
        """Generate a single blueprint through the uniform factory path."""
        with trace("factory.generate", blueprint=request.blueprint_id):
            state = GenerationState(request=request)
            self._run(state, after_seam=False)
            factory = state.factory
            if factory is None:
                raise OrchestrationError("no declared phase resolved a factory before the seam")
            # Every factory reuses this exact execution path (delegates to execute).
            result = factory.generate(state.bound(), self)
        _logger.info(
            "factory.generated",
            blueprint=request.blueprint_id,
            blueprint_class=state.bound().classification.value,
            factory=factory.descriptor.name,
            status=result.status.value,
        )
        return result

    # -- FactoryExecution (shared execution path) ------------------------------

    def execute(self, context: ExecutionContext) -> FactoryResult:
        """The one and only compile + assemble path (reused by every factory)."""
        state = GenerationState(
            request=context.request,
            document=context.document,
            classification=context.classification,
            context=context,
        )
        self._run(state, after_seam=True)
        if state.result is None:
            raise OrchestrationError("no declared phase produced a generation result")
        return state.result

    # -- derived execution -----------------------------------------------------

    def _run(self, state: GenerationState, *, after_seam: bool) -> None:
        """Apply each declared phase of the derived span, in the order derived for it."""
        for key in generation_span(after_seam=after_seam):
            handler = generation_phase(key).handler
            if handler is None:  # pragma: no cover - registration always supplies one
                raise OrchestrationError("declared generation phase has no handler", phase=key)
            handler(self, state)

    # -- stages ----------------------------------------------------------------

    def _resolve_blueprint(self, blueprint_id: str) -> Mapping[str, Any]:
        try:
            return self._provider.get(blueprint_id)
        except Exception as exc:  # provider-specific resolution failure  # noqa: BLE001
            raise BlueprintResolutionError(
                "could not resolve blueprint input document",
                blueprint_id=blueprint_id,
                detail=str(exc),
            ) from exc

    def _classify(self, blueprint_id: str, document: Mapping[str, Any]) -> BlueprintClassification:
        """Classify from the registered artifact metadata if present, else the doc."""
        artifact = self._registry.artifacts.find(blueprint_id)
        if artifact is not None:
            return resolve_blueprint_class(artifact)
        return resolve_blueprint_class(document)

    def _compile(self, document: Mapping[str, Any]) -> CompilationResult:
        pipeline = CompilerPipeline(
            self._registry, signer=self._signer, output_dir=self._output_dir
        )
        return pipeline.compile_one(document)

    def _generated_result(self, state: GenerationState) -> FactoryResult:
        context = state.bound()
        compilation = state.compilation
        assert compilation is not None  # guaranteed by the gap check  # noqa: S101
        published = compilation.published
        assert published is not None  # guaranteed by the gap check  # noqa: S101
        unit = state.unit
        if unit is None:
            raise OrchestrationError("no declared phase assembled a runtime unit")

        closure = tuple(unit.closure_records())
        evidence = build_generation_evidence(
            blueprint_id=context.request.blueprint_id,
            blueprint_version=state.version,
            classification=context.classification,
            compiler_artifact={
                "artifact_id": published.artifact_id,
                "package_sha256": unit.package_sha256,
            },
            runtime_artifact={
                "runtime_id": unit.runtime_id,
                "image_reference": unit.image_reference,
            },
            dependency_closure=closure,
            disclosure=unit.disclosure,
        )
        return FactoryResult(
            blueprint_id=context.request.blueprint_id,
            blueprint_class=context.classification.value,
            factory_name=context.descriptor.name,
            status=GenerationStatus.GENERATED,
            success=True,
            artifact_id=published.artifact_id,
            runtime_id=unit.runtime_id,
            package_sha256=unit.package_sha256,
            image_reference=unit.image_reference,
            dependency_closure=closure,
            disclosure_present=disclosure_present(unit.disclosure),
            evidence=evidence.to_dict(),
        )

    def _gap_result(self, state: GenerationState) -> FactoryResult:
        """A faithful gap outcome — no artifacts invented (TP-01)."""
        context = state.bound()
        compilation = state.compilation
        gap = (
            compilation.gap_report.to_dict()
            if compilation is not None and compilation.gap_report is not None
            else {"message": "compilation produced no artifact"}
        )
        evidence = build_generation_evidence(
            blueprint_id=context.request.blueprint_id,
            blueprint_version=state.version,
            classification=context.classification,
            compiler_artifact=None,
            runtime_artifact=None,
            dependency_closure=(),
            disclosure=None,
            gap=gap,
        )
        return FactoryResult(
            blueprint_id=context.request.blueprint_id,
            blueprint_class=context.classification.value,
            factory_name=context.descriptor.name,
            status=GenerationStatus.GAP,
            success=False,
            dependency_closure=(),
            disclosure_present=False,
            evidence=evidence.to_dict(),
            gap=gap,
        )


# --------------------------------------------------------------------------- phase handlers
#
# One handler per declared phase. None of them names its successor, and none of them is
# called from a written sequence: `GenerationOrchestrator._run` applies whichever phases the
# derived span contains, in the derived order.


def _phase_resolve_blueprint(orchestrator: GenerationOrchestrator, state: GenerationState) -> None:
    state.document = orchestrator._resolve_blueprint(state.request.blueprint_id)


def _phase_classify(orchestrator: GenerationOrchestrator, state: GenerationState) -> None:
    state.classification = orchestrator._classify(state.request.blueprint_id, state.document or {})


def _phase_resolve_factory(orchestrator: GenerationOrchestrator, state: GenerationState) -> None:
    classification = state.classification
    if classification is None:
        raise OrchestrationError("factory resolution ran before the blueprint was classified")
    factory = orchestrator.factories.resolve_factory(classification)
    state.factory = factory
    state.context = ExecutionContext(
        request=state.request,
        document=state.document or {},
        classification=classification,
        descriptor=factory.descriptor,
    )


def _phase_compile(orchestrator: GenerationOrchestrator, state: GenerationState) -> None:
    state.compilation = orchestrator._compile(state.bound().document)


def _phase_assemble(orchestrator: GenerationOrchestrator, state: GenerationState) -> None:
    if state.gapped:
        return
    compilation = state.compilation
    assert compilation is not None and compilation.published is not None  # noqa: S101
    state.unit = assemble(
        compilation.published,
        verify_with=orchestrator._signer,
        environment=state.bound().request.environment,
    )


def _phase_deploy(_orchestrator: GenerationOrchestrator, state: GenerationState) -> None:
    if state.gapped:
        return
    descriptor(state.unit, environment=state.bound().request.environment)


def _phase_rollback(_orchestrator: GenerationOrchestrator, state: GenerationState) -> None:
    # Deployment and rollback are both exercised: the runtime pipeline is reversible.
    if state.gapped:
        return
    rollback(state.unit)


def _phase_evidence(orchestrator: GenerationOrchestrator, state: GenerationState) -> None:
    state.result = (
        orchestrator._gap_result(state) if state.gapped else orchestrator._generated_result(state)
    )


#: The declared phase graph of the generation runtime. Each phase names only what it
#: requires; the order is derived, and registering one more phase changes it.
register_generation_phase("resolve-blueprint", handler=_phase_resolve_blueprint)
register_generation_phase("classify", handler=_phase_classify, requires=("resolve-blueprint",))
register_generation_phase(
    "resolve-factory", handler=_phase_resolve_factory, requires=("classify",), seam=True
)
register_generation_phase("compile", handler=_phase_compile, requires=("resolve-factory",))
register_generation_phase("assemble", handler=_phase_assemble, requires=("compile",))
register_generation_phase("deploy", handler=_phase_deploy, requires=("assemble",))
register_generation_phase("rollback", handler=_phase_rollback, requires=("deploy",))
register_generation_phase("evidence", handler=_phase_evidence, requires=("rollback",))


__all__ = ["GenerationOrchestrator", "GenerationState"]
