"""TASK-000028 — Pipeline Orchestrator (EPIC-003, IMP-007 §3).

Sequences the deterministic compilation pipeline end to end:

    Parse → Validate → Resolve → Compile → Optimize → Package → Sign → Publish

Every stage is deterministic, authorization-gated, traceable, and reproducible. A
**stage failure halts the pipeline and produces a Gap Report** (IMP-007 §3/§17);
no partial artifacts are published. The orchestrator publishes its capability
through the versioned Foundation contract ``compiler.compile`` v1.0.0 (AR-03,
PL-05) and accesses the registry **only** through the Registry Adapter
(Mandatory Rule 3).

The orchestrator composes the stages built in TASK-000019…TASK-000027 and adds no
compilation semantics of its own (no invented behaviour, TP-01).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.compiler.data_compiler import DataBlueprintCompiler
from engine.compiler.errors import CompilerError
from engine.compiler.gap import GapReport, Stage
from engine.compiler.ir import BlueprintIR
from engine.compiler.optimization import Optimizer
from engine.compiler.packaging import Packager
from engine.compiler.parser import ensure_supported, parse
from engine.compiler.publishing import PublishedArtifact, Publisher
from engine.compiler.resolver import DependencyResolver
from engine.compiler.signing import Signer
from engine.compiler.validation import BlueprintValidator
from engine.foundation.contracts.contract import Contract, ContractRegistry, Version
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.registry.adapter import RegistryAdapter

_logger = get_logger("compiler.pipeline")

#: The versioned contract the compiler pipeline satisfies (AR-03, PL-05).
COMPILE_CONTRACT = Contract(
    name="compiler.compile",
    version=Version(1, 0, 0),
    description=(
        "Deterministic BP-DATA compilation pipeline: parse, validate (certified "
        "inputs only), resolve (acyclic), compile, optimize, package, sign, publish."
    ),
)


@dataclass(frozen=True, slots=True)
class CompilationResult:
    """The per-blueprint outcome of a pipeline run."""

    blueprint_id: str
    success: bool
    published: PublishedArtifact | None = None
    gap_report: GapReport | None = None


@dataclass(frozen=True, slots=True)
class BuildResult:
    """The outcome of compiling a whole build set."""

    success: bool
    order: tuple[str, ...]
    results: tuple[CompilationResult, ...]
    gap_report: GapReport | None = None

    def result_for(self, blueprint_id: str) -> CompilationResult | None:
        for result in self.results:
            if result.blueprint_id == blueprint_id:
                return result
        return None


class CompilerPipeline:
    """The Universal Compiler pipeline orchestrator (IMP-007 §3)."""

    __slots__ = (
        "_registry",
        "_signer",
        "_publisher",
        "_validator",
        "_resolver",
        "_compiler",
        "_optimizer",
        "_packager",
    )

    def __init__(
        self,
        registry: RegistryAdapter,
        *,
        signer: Signer,
        output_dir: str | Path,
    ) -> None:
        self._registry = registry
        self._signer = signer
        self._publisher = Publisher(output_dir)
        self._validator = BlueprintValidator(registry)
        self._resolver = DependencyResolver()
        self._compiler = DataBlueprintCompiler()
        self._optimizer = Optimizer()
        self._packager = Packager()

    # -- contract --------------------------------------------------------------

    @property
    def contract(self) -> Contract:
        return COMPILE_CONTRACT

    def register_contract(self, registry: ContractRegistry) -> None:
        """Publish the pipeline's contract into a Foundation contract registry."""
        registry.register(COMPILE_CONTRACT)

    # -- public API ------------------------------------------------------------

    def compile(self, sources: Iterable[Mapping[str, Any] | str | bytes]) -> BuildResult:
        """Run the full pipeline over a build set; halt with a Gap Report on failure."""
        with trace("compiler.pipeline"):
            # Stage 1 — Parse (front-end admission).
            try:
                blueprints = self._parse_all(sources)
            except _StageFailure as failure:
                return self._halt(failure, order=())

            # Stage 2 — Validate (certification + registry conformance).
            try:
                for ir in blueprints:
                    self._validator.validate(ir)
            except CompilerError as exc:
                return self._halt(_StageFailure(Stage.VALIDATE, exc, _blueprint_id(exc)), order=())

            # Stage 3 — Resolve (acyclic dependency graph + compile order).
            try:
                resolved = self._resolver.resolve(blueprints)
            except CompilerError as exc:
                return self._halt(_StageFailure(Stage.RESOLVE, exc, _blueprint_id(exc)), order=())

            # Stages 4–8 — per blueprint in dependency order.
            by_id = {ir.blueprint_id: ir for ir in blueprints}
            results: list[CompilationResult] = []
            for blueprint_id in resolved.order:
                ir = by_id[blueprint_id]
                try:
                    published = self._compile_one(ir)
                except _StageFailure as failure:
                    return self._halt(failure, order=resolved.order, partial=results)
                results.append(
                    CompilationResult(blueprint_id=blueprint_id, success=True, published=published)
                )

        _logger.info("compiler.pipeline.succeeded", blueprints=len(results))
        return BuildResult(success=True, order=resolved.order, results=tuple(results))

    def compile_one(self, source: Mapping[str, Any] | str | bytes) -> CompilationResult:
        """Compile a single self-contained blueprint and return its result."""
        build = self.compile([source])
        if build.results:
            return build.results[0]
        # Failure before any per-blueprint result was produced.
        return CompilationResult(
            blueprint_id=build.gap_report.blueprint_id if build.gap_report else "unknown",
            success=False,
            gap_report=build.gap_report,
        )

    # -- internals -------------------------------------------------------------

    def _parse_all(self, sources: Iterable[Mapping[str, Any] | str | bytes]) -> list[BlueprintIR]:
        blueprints: list[BlueprintIR] = []
        for source in sources:
            try:
                ir = ensure_supported(parse(source))
            except CompilerError as exc:
                raise _StageFailure(Stage.PARSE, exc, _blueprint_id(exc)) from exc
            blueprints.append(ir)
        if not blueprints:
            raise _StageFailure(
                Stage.PARSE,
                _empty_build_error(),
                None,
            )
        return blueprints

    def _compile_one(self, ir: BlueprintIR) -> PublishedArtifact:
        try:
            compiled = self._compiler.compile(ir)
        except CompilerError as exc:
            raise _StageFailure(Stage.COMPILE, exc, ir.blueprint_id) from exc
        try:
            optimized = self._optimizer.optimize(compiled)
        except CompilerError as exc:
            raise _StageFailure(Stage.OPTIMIZE, exc, ir.blueprint_id) from exc
        try:
            package = self._packager.package(optimized, name=ir.name, version=ir.version)
        except CompilerError as exc:
            raise _StageFailure(Stage.PACKAGE, exc, ir.blueprint_id) from exc
        try:
            signed = self._signer.sign(package)
        except CompilerError as exc:
            raise _StageFailure(Stage.SIGN, exc, ir.blueprint_id) from exc
        try:
            return self._publisher.publish(signed, verify_with=self._signer)
        except CompilerError as exc:
            raise _StageFailure(Stage.PUBLISH, exc, ir.blueprint_id) from exc

    def _halt(
        self,
        failure: _StageFailure,
        *,
        order: tuple[str, ...],
        partial: list[CompilationResult] | None = None,
    ) -> BuildResult:
        report = GapReport.from_error(
            failure.stage, failure.error, blueprint_id=failure.blueprint_id
        )
        _logger.error(
            "compiler.pipeline.halted",
            stage=failure.stage.value,
            code=failure.error.code,
            blueprint=failure.blueprint_id,
        )
        results = tuple(partial or ())
        return BuildResult(success=False, order=order, results=results, gap_report=report)


class _StageFailure(Exception):
    """Internal carrier binding a :class:`CompilerError` to the stage that raised it."""

    def __init__(self, stage: Stage, error: CompilerError, blueprint_id: str | None) -> None:
        super().__init__(error.message)
        self.stage = stage
        self.error = error
        self.blueprint_id = blueprint_id


def _blueprint_id(exc: CompilerError) -> str | None:
    value = exc.context.get("blueprint_id")
    return value if isinstance(value, str) else None


def _empty_build_error() -> CompilerError:
    from engine.compiler.errors import ParseError

    return ParseError("no blueprints supplied to the compiler")


__all__ = [
    "COMPILE_CONTRACT",
    "CompilationResult",
    "BuildResult",
    "CompilerPipeline",
]
