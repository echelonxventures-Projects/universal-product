"""UAPF-000001 — the open stage-handler registry and the stage execution contract.

A stage declares the *name* of a handler; this registry resolves that name to a callable.
That indirection is the whole reason a pipeline declaration can be pure data: the
declaration never holds behaviour, and behaviour is never coupled to a particular
pipeline. Registering a handler admits new behaviour into the framework without editing
the framework, and a stage that names an unregistered handler fails closed rather than
being skipped.

The handler contract
--------------------
A handler is ``(StageContext) -> StageOutcome``. It receives the *declaration* of the
stage it is running — not just its id — so it can discharge the stage's declared gates
without knowing which pipeline invoked it. It must be **pure**: same context, same
outcome, no wall-clock, no RNG, no I/O, no ambient state. That is what makes a whole
pipeline run reproducible, and it is checked in the only way purity can be checked from
outside — the runtime records the outcome, and an identical run must produce an identical
fingerprint.

The built-in handlers
---------------------
Two are registered here, and both are *general* rather than domain-specific:

    * ``uapf.record`` — records its inputs and passes. The honest handler for a stage
      whose work is to be accounted for rather than computed (an assimilation, a
      registration, a synchronization).
    * ``uapf.gate`` — passes exactly when every declared *blocking* gate obligation
      appears in the inputs, and otherwise fails naming the undischarged obligations. It
      reads the gates from the declaration, so it discharges gates it has never heard of;
      adding a gate needs no handler change.

Neither knows any pipeline, stage or gate by name, so the framework ships working
behaviour without shipping a fixed pipeline.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.contracts import StageDefinition
from platform.universal_pipeline.errors import PipelineHandlerError
from platform.universal_pipeline.identity import Identity, mint
from platform.universal_pipeline.vocabulary import Vocabulary
from typing import Any

#: The three outcome statuses a stage may report. ``SKIP`` is distinct from ``PASS``
#: because an optional stage that did not run must not be evidence that it succeeded.
STAGE_OUTCOME_STATUSES: tuple[str, ...] = ("FAIL", "PASS", "SKIP")

#: The one status that lets a plan continue past a stage.
CONTINUE_STATUS = "PASS"

#: The built-in handler that records and passes.
RECORD_HANDLER = "uapf.record"

#: The built-in handler that discharges a stage's declared blocking gates.
GATE_HANDLER = "uapf.gate"


@dataclass(frozen=True, slots=True)
class StageContext:
    """Everything a stage handler is given — and nothing more.

    Deliberately closed: a handler receives the declaration, the identity of the unit, the
    inputs and the attempt number. It gets no bus, no registry, no queue and no clock, so
    a handler *cannot* reach around the framework to mutate state or observe ambient
    conditions. Purity is therefore structural rather than a rule handlers are asked to
    follow.
    """

    pipeline_id: str
    version: str
    unit_id: str
    stage: StageDefinition
    inputs: Mapping[str, Any] = field(default_factory=dict)
    attempt: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.pipeline_id, str) or not self.pipeline_id:
            raise PipelineHandlerError("stage context pipeline id is required")
        if not isinstance(self.unit_id, str) or not self.unit_id:
            raise PipelineHandlerError(
                "stage context unit id is required", pipeline_id=self.pipeline_id
            )
        if not isinstance(self.stage, StageDefinition):
            raise PipelineHandlerError(
                "stage context requires a StageDefinition", unit_id=self.unit_id
            )
        if not isinstance(self.inputs, Mapping):
            raise PipelineHandlerError(
                "stage context inputs must be a mapping", unit_id=self.unit_id
            )
        if self.attempt < 0:
            raise PipelineHandlerError(
                "stage context attempt must be non-negative", unit_id=self.unit_id
            )

    @property
    def stage_id(self) -> str:
        return self.stage.stage_id

    @property
    def handler(self) -> str:
        return self.stage.handler

    def input(self, key: str, default: Any = None) -> Any:
        """The value declared at ``key``, or ``default`` when absent."""
        return self.inputs.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "version": self.version,
            "unit_id": self.unit_id,
            "stage": self.stage.to_dict(),
            "input_keys": sorted(self.inputs),
            "attempt": self.attempt,
        }


@dataclass(frozen=True, slots=True)
class StageOutcome:
    """The immutable result of running one stage.

    ``outputs`` feed the next stage's inputs, so a pipeline threads state forward through
    recorded values rather than through shared mutable context — which is why a re-run
    from the same declaration reproduces the same values. ``findings`` carry the reasons a
    stage did not pass; a ``FAIL`` with no finding is refused, because an unexplained
    failure is not actionable.
    """

    stage_id: str
    status: str
    findings: tuple[str, ...] = ()
    outputs: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.stage_id, str) or not self.stage_id:
            raise PipelineHandlerError("stage outcome stage id is required")
        if self.status not in STAGE_OUTCOME_STATUSES:
            raise PipelineHandlerError(
                "unknown stage outcome status",
                stage_id=self.stage_id,
                status=self.status,
                declared=list(STAGE_OUTCOME_STATUSES),
            )
        if not isinstance(self.findings, tuple):
            raise PipelineHandlerError(
                "stage outcome findings must be a tuple", stage_id=self.stage_id
            )
        for finding in self.findings:
            if not isinstance(finding, str) or not finding:
                raise PipelineHandlerError(
                    "stage outcome findings must be non-empty strings", stage_id=self.stage_id
                )
        if not isinstance(self.outputs, Mapping):
            raise PipelineHandlerError(
                "stage outcome outputs must be a mapping", stage_id=self.stage_id
            )
        if self.status == "FAIL" and not self.findings:
            raise PipelineHandlerError(
                "a failing stage must state at least one finding", stage_id=self.stage_id
            )

    @property
    def passed(self) -> bool:
        """True iff this outcome lets the plan continue."""
        return self.status == CONTINUE_STATUS

    @property
    def identity(self) -> Identity:
        return mint("handler", self.stage_id, self.status, self.evidence_hash())

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "status": self.status,
            "findings": list(self.findings),
            "outputs": dict(self.outputs),
        }

    def evidence_hash(self) -> str:
        """A deterministic content hash of the outcome (the stage's evidence)."""
        return content_hash(self.to_dict())


#: A stage handler: pure, total over its context, and free of side effects.
StageHandler = Callable[[StageContext], StageOutcome]

#: The stage-handler vocabulary: the handler *name* is the governed term and the callable
#: is carried as that term's ``handler`` attribute. Module-level so a handler registered by
#: any consumer is resolvable by every pipeline — one behaviour namespace, and the same
#: :class:`~platform.universal_pipeline.vocabulary.Vocabulary` primitive that governs
#: object kinds, pipeline types, event categories and readiness predicates.
_STAGE_HANDLERS = Vocabulary("stage-handler", error=PipelineHandlerError)


def register_stage_handler(name: str, handler: StageHandler, description: str = "") -> None:
    """Register a stage handler under ``name`` (unbounded extension by registration).

    Raises:
        PipelineHandlerError: if ``name`` is not a lower-case dotted/hyphenated token,
            ``handler`` is not callable, or ``name`` is already registered. Re-registration
            is refused rather than silently replacing: a handler name appears in
            declarations, and rebinding one would change the meaning of every pipeline that
            names it.
    """
    if not callable(handler):
        raise PipelineHandlerError("stage handler must be callable", name=name)
    _STAGE_HANDLERS.register(name, description=description, attributes={"handler": handler})


def stage_handler_names() -> tuple[str, ...]:
    """Every registered stage handler name, sorted (deterministic)."""
    return _STAGE_HANDLERS.terms()


def require_stage_handler(name: str) -> None:
    """Fail closed unless ``name`` resolves to a registered handler.

    Raises:
        PipelineHandlerError: naming the unresolved handler and how many are registered.
    """
    _STAGE_HANDLERS.require(name)


def get_stage_handler(name: str) -> StageHandler:
    """The registered handler ``name`` (fail-closed if unregistered)."""
    resolved: StageHandler = _STAGE_HANDLERS.require(name).attribute("handler")
    return resolved


def run_stage(context: StageContext) -> StageOutcome:
    """Resolve the handler ``context`` names and run it, validating what it returns.

    The single invocation path. It validates the *outcome* as well as the handler, because
    a handler is third-party code and a malformed outcome would otherwise be recorded as
    truth. A handler that raises is not caught here: the runtime owns failure routing, so
    swallowing the exception would hide the reason a unit failed.

    Raises:
        PipelineHandlerError: if the handler is unregistered, or returned something other
            than a :class:`StageOutcome`, or returned an outcome for a different stage.
    """
    if not isinstance(context, StageContext):
        raise PipelineHandlerError("a stage is run from a StageContext")
    handler = get_stage_handler(context.handler)
    outcome = handler(context)
    if not isinstance(outcome, StageOutcome):
        raise PipelineHandlerError(
            "stage handler did not return a StageOutcome",
            name=context.handler,
            stage_id=context.stage_id,
        )
    if outcome.stage_id != context.stage_id:
        raise PipelineHandlerError(
            "stage handler returned an outcome for a different stage",
            name=context.handler,
            stage_id=context.stage_id,
            returned=outcome.stage_id,
        )
    return outcome


def _record_handler(context: StageContext) -> StageOutcome:
    """``uapf.record`` — account for the stage's declaration and inputs, and pass.

    Outputs the declared input keys and the stage's declaration fingerprint rather than
    the input *values*: the values may be large or reference sensitive material, and what
    a recording stage must prove is that it saw them (SEC-04 — context by reference).
    """
    return StageOutcome(
        stage_id=context.stage_id,
        status=CONTINUE_STATUS,
        outputs={
            "recorded_stage": context.stage_id,
            "recorded_handler": context.handler,
            "recorded_input_keys": sorted(context.inputs),
            "declaration_fingerprint": content_hash(context.stage.to_dict()),
        },
    )


def _gate_handler(context: StageContext) -> StageOutcome:
    """``uapf.gate`` — pass iff every declared blocking gate obligation is discharged.

    An obligation is discharged when its name appears as an input key with a truthy
    value. Advisory (non-blocking) gates are reported as findings without failing the
    stage, so a measurement can be recorded without halting work.
    """
    undischarged = [
        gate.obligation
        for gate in context.stage.blocking_gates
        if not context.inputs.get(gate.obligation)
    ]
    advisory = [
        f"advisory gate not discharged: {gate.obligation}"
        for gate in context.stage.gates
        if not gate.blocking and not context.inputs.get(gate.obligation)
    ]
    if undischarged:
        return StageOutcome(
            stage_id=context.stage_id,
            status="FAIL",
            findings=tuple(
                [f"undischarged blocking obligation: {name}" for name in sorted(undischarged)]
                + advisory
            ),
            outputs={"undischarged": sorted(undischarged)},
        )
    return StageOutcome(
        stage_id=context.stage_id,
        status=CONTINUE_STATUS,
        findings=tuple(advisory),
        outputs={
            "discharged": sorted(gate.obligation for gate in context.stage.blocking_gates),
            "gate_count": len(context.stage.gates),
        },
    )


register_stage_handler(
    RECORD_HANDLER, _record_handler, "account for a stage declaration and its inputs, and pass"
)
register_stage_handler(
    GATE_HANDLER, _gate_handler, "pass iff every declared blocking gate obligation is discharged"
)


__all__ = [
    "GATE_HANDLER",
    "CONTINUE_STATUS",
    "RECORD_HANDLER",
    "STAGE_OUTCOME_STATUSES",
    "StageContext",
    "StageHandler",
    "StageOutcome",
    "get_stage_handler",
    "register_stage_handler",
    "require_stage_handler",
    "run_stage",
    "stage_handler_names",
]
