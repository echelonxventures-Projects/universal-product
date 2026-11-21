"""UAPF-000001 — the declaration surface: pipeline types, declarations and derived plans.

This module is the reason UAPF can host an unbounded number of pipelines without ever
being edited: a pipeline is **declared as data** and everything about its behaviour is
**derived** from that declaration. Nothing here holds a workflow, a sequence of steps or
a list of known pipelines. Admitting one more pipeline, stage, pipeline type, gate,
policy, capability or plugin is a data entry.

Declared vs derived
-------------------
:class:`PipelineDefinition` is the *declaration* — what the author states. It carries no
order. :class:`PipelinePlan` is the *derivation* — the order that follows from the
stages' declared ``requires`` edges, computed by
:func:`engine.foundation.composition.derive_order`, the repository's single ordering
authority. UAPF therefore has no ordering mechanism of its own to drift from that one
(``DEC-MCOS-14`` recorded exactly that defect), and a stage's position is a consequence
of what it requires rather than of where it was written.

Why the type registry refuses to be an enumeration
--------------------------------------------------
:data:`SEED_PIPELINE_TYPES` transcribes the twenty-one pipeline categories the mission
names, but they are *registered through the public* :func:`register_pipeline_type` like
any other, and no function in this package branches on a specific type. A pipeline type
is a label the registry admits, so "future pipeline types" needs no future code — which
is what makes the framework generic rather than a fixed set of pipelines with a generic
name.

Determinism: every type is immutable, hashable, serializable and pure over its inputs.
Validation is fail-closed at construction, so a malformed declaration cannot exist as an
object — an unregistered type, a duplicate stage id, a dangling ``requires`` edge or a
declared cycle raises rather than degrading.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import ContractRef, Version, content_hash
from platform.universal_pipeline.errors import (
    PipelineDefinitionError,
    PipelinePlanError,
    PipelineTypeError,
)
from platform.universal_pipeline.identity import Identity, mint
from platform.universal_pipeline.vocabulary import Vocabulary
from typing import Any

from engine.foundation.composition import derive_order, get_strategy, unresolved_keys

#: The default ordering strategy for a pipeline plan. ``parallel-waves`` rather than
#: ``dependency-order`` because ``05-BATCH-GENERATION-RULES.md`` §4 derives dependency
#: safety from *intra-wave independence*: a wave is exactly the set whose declared
#: requirements are already satisfied, so wave membership is what makes a batch safe to
#: run concurrently. A caller wanting a strict sequence names ``dependency-order``; both
#: come from the one shared strategy registry, so neither is privileged.
DEFAULT_PIPELINE_STRATEGY = "parallel-waves"

#: The two directions a pipeline may relate to a capability.
CAPABILITY_DIRECTIONS: tuple[str, ...] = ("provides", "requires")

#: The pipeline types seeded at import — the twenty-one categories the mission names.
#: A *declaration*: each is admitted through the public :func:`register_pipeline_type`,
#: so this tuple is a starting point and never a closed world.
SEED_PIPELINE_TYPES: tuple[tuple[str, str], ...] = (
    ("analytics", "measurement and analysis of repository and runtime signals"),
    ("architecture", "architectural evolution, decision and conformance work"),
    ("certification", "certification of validated work against declared criteria"),
    ("compliance", "compliance evaluation against declared obligations"),
    ("deployment", "deployment of assembled artefacts to a target"),
    ("design", "design of declared capabilities prior to build"),
    ("documentation", "authoring and synchronizing canonical documentation"),
    ("evolution", "admission of newly discovered concepts into canonical truth"),
    ("governance", "constitutional governance, policy and authority work"),
    ("implementation", "realization of an approved implementation unit in code"),
    ("knowledge", "canonical knowledge discovery, homing and expansion"),
    ("learning", "learning from recorded outcomes to improve later decisions"),
    ("monitoring", "continuous observation of declared health signals"),
    ("optimization", "improvement of an existing capability without behaviour change"),
    ("planning", "sequencing and readiness assessment of declared work"),
    ("research", "investigation producing new candidate knowledge"),
    ("runtime", "runtime assembly, orchestration and operation"),
    ("security", "security evaluation, hardening and control verification"),
    ("testing", "test authoring and execution over declared surfaces"),
    ("validation", "validation of an implementation against declared rules"),
    ("verification", "independent verification that validation actually holds"),
)

#: The pipeline-type vocabulary. Module-level: a type registered by any consumer is
#: available to every consumer, so there is exactly one pipeline-type namespace. It is the
#: same :class:`~platform.universal_pipeline.vocabulary.Vocabulary` primitive that governs
#: object kinds, event categories, stage handlers and readiness predicates — one
#: open-registration mechanism, not five.
_PIPELINE_TYPES = Vocabulary("pipeline-type", error=PipelineTypeError)


def register_pipeline_type(pipeline_type: str, description: str = "") -> None:
    """Register one pipeline type (unbounded extension by declaration).

    Raises:
        PipelineTypeError: if ``pipeline_type`` is not a lower-case dotted/hyphenated token
            or is already registered. Re-registration is refused rather than ignored: a
            type carries governance meaning, and silently rebinding one would let two
            categories of work share a label.
    """
    _PIPELINE_TYPES.register(pipeline_type, description=description)


def pipeline_types() -> tuple[str, ...]:
    """Every registered pipeline type, sorted (deterministic)."""
    return _PIPELINE_TYPES.terms()


def pipeline_type_description(pipeline_type: str) -> str:
    """The declared description of ``pipeline_type`` (fail-closed if unregistered)."""
    return _PIPELINE_TYPES.require(pipeline_type).description


def require_pipeline_type(pipeline_type: str) -> None:
    """Fail closed unless ``pipeline_type`` is registered.

    Raises:
        PipelineTypeError: naming the unknown type and how many are registered.
    """
    _PIPELINE_TYPES.require(pipeline_type)


def _require_identifier(value: Any, label: str, **context: Any) -> str:
    """Return ``value`` when it is a non-empty string; otherwise fail closed."""
    if not isinstance(value, str) or not value:
        raise PipelineDefinitionError(f"{label} is required", **context)
    return value


def _require_unique(ids: tuple[str, ...], label: str, **context: Any) -> None:
    """Fail closed when ``ids`` contains a duplicate, naming the duplicates."""
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in ids:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        raise PipelineDefinitionError(
            f"duplicate {label}", duplicates=sorted(duplicates), **context
        )


@dataclass(frozen=True, slots=True)
class PipelineGateSpec:
    """A declared gate: an obligation that must be discharged for a stage to pass.

    ``obligation`` names the evidence key the gate requires — the gate is *data*, so a
    stage handler discharges it by producing that key rather than by knowing the gate
    exists. ``blocking`` distinguishes a gate that fails a stage from one that only
    records a finding, which is how an advisory measurement is expressed without a
    second mechanism.
    """

    gate_id: str
    obligation: str
    blocking: bool = True
    description: str = ""

    def __post_init__(self) -> None:
        _require_identifier(self.gate_id, "gate id")
        _require_identifier(self.obligation, "gate obligation", gate_id=self.gate_id)
        if not isinstance(self.blocking, bool):
            raise PipelineDefinitionError("gate blocking must be a bool", gate_id=self.gate_id)

    @property
    def identity(self) -> Identity:
        return mint("gate", self.gate_id, self.obligation)

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "obligation": self.obligation,
            "blocking": self.blocking,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PipelineGateSpec:
        if not isinstance(data, Mapping):
            raise PipelineDefinitionError("gate declaration must be a mapping")
        return cls(
            gate_id=str(data.get("gate_id", "")),
            obligation=str(data.get("obligation", "")),
            blocking=bool(data.get("blocking", True)),
            description=str(data.get("description", "")),
        )


@dataclass(frozen=True, slots=True)
class PipelinePolicy:
    """A declared governance policy: an obligation binding a pipeline or named stages.

    ``applies_to`` empty means the whole pipeline. A policy states an obligation and
    where it binds; it does not state how to check it — the Policy Engine
    (:mod:`platform.universal_pipeline.governance`) evaluates declared obligations
    uniformly, so a new policy needs no new evaluation code.
    """

    policy_id: str
    obligation: str
    applies_to: tuple[str, ...] = ()
    blocking: bool = True
    description: str = ""

    def __post_init__(self) -> None:
        _require_identifier(self.policy_id, "policy id")
        _require_identifier(self.obligation, "policy obligation", policy_id=self.policy_id)
        if not isinstance(self.applies_to, tuple):
            raise PipelineDefinitionError(
                "policy applies_to must be a tuple", policy_id=self.policy_id
            )
        for target in self.applies_to:
            _require_identifier(target, "policy target", policy_id=self.policy_id)

    @property
    def identity(self) -> Identity:
        return mint("policy", self.policy_id, self.obligation)

    def binds(self, stage_id: str) -> bool:
        """True iff this policy binds ``stage_id`` (an empty scope binds everything)."""
        return not self.applies_to or stage_id in self.applies_to

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "obligation": self.obligation,
            "applies_to": list(self.applies_to),
            "blocking": self.blocking,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PipelinePolicy:
        if not isinstance(data, Mapping):
            raise PipelineDefinitionError("policy declaration must be a mapping")
        return cls(
            policy_id=str(data.get("policy_id", "")),
            obligation=str(data.get("obligation", "")),
            applies_to=tuple(str(t) for t in data.get("applies_to", ())),
            blocking=bool(data.get("blocking", True)),
            description=str(data.get("description", "")),
        )


@dataclass(frozen=True, slots=True)
class PipelineCapability:
    """A capability a pipeline declares it ``provides`` or ``requires``.

    The capability graph is derived from these declarations, so a pipeline's place in it
    is a consequence of what it states rather than of a separate catalogue that must be
    kept in step. The contract is a :class:`~platform.foundation.contracts.ContractRef`
    — the repository's existing contract-reference discipline (AR-03 / PL-05), reused
    rather than restated.
    """

    capability_id: str
    contract: ContractRef
    direction: str = "provides"
    description: str = ""

    def __post_init__(self) -> None:
        _require_identifier(self.capability_id, "capability id")
        if not isinstance(self.contract, ContractRef):
            raise PipelineDefinitionError(
                "capability contract must be a ContractRef",
                capability_id=self.capability_id,
            )
        if self.direction not in CAPABILITY_DIRECTIONS:
            raise PipelineDefinitionError(
                "capability direction must be 'provides' or 'requires'",
                capability_id=self.capability_id,
                direction=self.direction,
            )

    @property
    def identity(self) -> Identity:
        return mint("capability", self.capability_id, self.direction, self.contract.name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "contract": self.contract.to_dict(),
            "direction": self.direction,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PipelineCapability:
        if not isinstance(data, Mapping):
            raise PipelineDefinitionError("capability declaration must be a mapping")
        contract = data.get("contract", {})
        if not isinstance(contract, Mapping):
            raise PipelineDefinitionError("capability contract must be a mapping")
        return cls(
            capability_id=str(data.get("capability_id", "")),
            contract=ContractRef(
                name=str(contract.get("name", "")),
                version=str(contract.get("version", "1.0.0")),
            ),
            direction=str(data.get("direction", "provides")),
            description=str(data.get("description", "")),
        )


@dataclass(frozen=True, slots=True)
class PipelinePlugin:
    """A declared extension-point binding: at ``extension_point``, run ``handler``.

    Plugins are how a pipeline is extended without editing it — the binding is data, and
    the handler is resolved from the open stage-handler registry, so a plugin adds
    behaviour without adding a mechanism.
    """

    plugin_id: str
    extension_point: str
    handler: str
    description: str = ""

    def __post_init__(self) -> None:
        _require_identifier(self.plugin_id, "plugin id")
        _require_identifier(
            self.extension_point, "plugin extension point", plugin_id=self.plugin_id
        )
        _require_identifier(self.handler, "plugin handler", plugin_id=self.plugin_id)

    @property
    def identity(self) -> Identity:
        return mint("plugin", self.plugin_id, self.extension_point, self.handler)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "extension_point": self.extension_point,
            "handler": self.handler,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PipelinePlugin:
        if not isinstance(data, Mapping):
            raise PipelineDefinitionError("plugin declaration must be a mapping")
        return cls(
            plugin_id=str(data.get("plugin_id", "")),
            extension_point=str(data.get("extension_point", "")),
            handler=str(data.get("handler", "")),
            description=str(data.get("description", "")),
        )


@dataclass(frozen=True, slots=True)
class PipelineSecuritySpec:
    """The permissions a pipeline requires and the classification of what it touches.

    Declared, not enforced here: the gateway refuses a submission whose principal does
    not hold every required permission, so the single enforcement point stays the
    gateway and this type stays a declaration.
    """

    required_permissions: tuple[str, ...] = ()
    classification: str = "internal"

    def __post_init__(self) -> None:
        if not isinstance(self.required_permissions, tuple):
            raise PipelineDefinitionError("required_permissions must be a tuple")
        for permission in self.required_permissions:
            _require_identifier(permission, "required permission")
        _require_identifier(self.classification, "security classification")

    def to_dict(self) -> dict[str, Any]:
        return {
            "required_permissions": list(self.required_permissions),
            "classification": self.classification,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PipelineSecuritySpec:
        if not isinstance(data, Mapping):
            raise PipelineDefinitionError("security declaration must be a mapping")
        return cls(
            required_permissions=tuple(str(p) for p in data.get("required_permissions", ())),
            classification=str(data.get("classification", "internal")),
        )


@dataclass(frozen=True, slots=True)
class PipelineGovernanceSpec:
    """The governance posture a pipeline declares.

    ``authority`` defaults to ``NONE (DERIVED TRUTH)`` because a pipeline *executes*
    canonical authority and never holds it — the same disclosure every derived programme
    in this repository carries. ``evidence_required`` makes the evidence obligation
    explicit rather than assumed.
    """

    authority: str = "NONE (DERIVED TRUTH)"
    obligations: tuple[str, ...] = ()
    evidence_required: bool = True

    def __post_init__(self) -> None:
        _require_identifier(self.authority, "governance authority")
        if not isinstance(self.obligations, tuple):
            raise PipelineDefinitionError("governance obligations must be a tuple")
        for obligation in self.obligations:
            _require_identifier(obligation, "governance obligation")

    def to_dict(self) -> dict[str, Any]:
        return {
            "authority": self.authority,
            "obligations": list(self.obligations),
            "evidence_required": self.evidence_required,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PipelineGovernanceSpec:
        if not isinstance(data, Mapping):
            raise PipelineDefinitionError("governance declaration must be a mapping")
        return cls(
            authority=str(data.get("authority", "NONE (DERIVED TRUTH)")),
            obligations=tuple(str(o) for o in data.get("obligations", ())),
            evidence_required=bool(data.get("evidence_required", True)),
        )


@dataclass(frozen=True, slots=True)
class StageDefinition:
    """One declared stage: a handler, what it requires, and the gates it must discharge.

    A stage declares ``requires`` — the stage ids that must precede it — and *nothing*
    about its own position. Position is derived (:class:`PipelinePlan`), so reordering a
    pipeline means editing declarations, never editing an order.
    """

    stage_id: str
    handler: str
    requires: tuple[str, ...] = ()
    gates: tuple[PipelineGateSpec, ...] = ()
    policies: tuple[str, ...] = ()
    optional: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        _require_identifier(self.stage_id, "stage id")
        _require_identifier(self.handler, "stage handler", stage_id=self.stage_id)
        if not isinstance(self.requires, tuple):
            raise PipelineDefinitionError("stage requires must be a tuple", stage_id=self.stage_id)
        for required in self.requires:
            _require_identifier(required, "stage requirement", stage_id=self.stage_id)
        if self.stage_id in self.requires:
            raise PipelineDefinitionError("stage cannot require itself", stage_id=self.stage_id)
        _require_unique(self.requires, "stage requirement", stage_id=self.stage_id)
        if not isinstance(self.gates, tuple):
            raise PipelineDefinitionError("stage gates must be a tuple", stage_id=self.stage_id)
        _require_unique(tuple(g.gate_id for g in self.gates), "gate id", stage_id=self.stage_id)
        if not isinstance(self.policies, tuple):
            raise PipelineDefinitionError("stage policies must be a tuple", stage_id=self.stage_id)

    @property
    def identity(self) -> Identity:
        return mint("stage", self.stage_id, self.handler)

    @property
    def blocking_gates(self) -> tuple[PipelineGateSpec, ...]:
        """The gates whose failure fails the stage, in declaration order."""
        return tuple(gate for gate in self.gates if gate.blocking)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "handler": self.handler,
            "requires": list(self.requires),
            "gates": [gate.to_dict() for gate in self.gates],
            "policies": list(self.policies),
            "optional": self.optional,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> StageDefinition:
        if not isinstance(data, Mapping):
            raise PipelineDefinitionError("stage declaration must be a mapping")
        return cls(
            stage_id=str(data.get("stage_id", "")),
            handler=str(data.get("handler", "")),
            requires=tuple(str(r) for r in data.get("requires", ())),
            gates=tuple(PipelineGateSpec.from_dict(g) for g in data.get("gates", ())),
            policies=tuple(str(p) for p in data.get("policies", ())),
            optional=bool(data.get("optional", False)),
            description=str(data.get("description", "")),
        )


@dataclass(frozen=True, slots=True)
class PipelineDefinition:
    """A complete, immutable pipeline declaration — the unit the registry admits.

    Validation is total and fail-closed at construction: an unregistered pipeline type,
    a malformed semantic version, an empty stage set, a duplicate stage id, a dangling
    ``requires`` edge, or a duplicate policy/plugin/capability id all raise. A malformed
    declaration therefore cannot exist as an object, which is why no consumer downstream
    re-checks it.
    """

    pipeline_id: str
    pipeline_type: str
    version: str
    stages: tuple[StageDefinition, ...]
    capabilities: tuple[PipelineCapability, ...] = ()
    policies: tuple[PipelinePolicy, ...] = ()
    plugins: tuple[PipelinePlugin, ...] = ()
    governance: PipelineGovernanceSpec = field(default_factory=PipelineGovernanceSpec)
    security: PipelineSecuritySpec = field(default_factory=PipelineSecuritySpec)
    strategy: str = DEFAULT_PIPELINE_STRATEGY
    description: str = ""

    def __post_init__(self) -> None:
        _require_identifier(self.pipeline_id, "pipeline id")
        require_pipeline_type(self.pipeline_type)
        try:
            Version.parse(self.version)
        except Exception as exc:  # noqa: BLE001 — re-raised as the UAPF domain error
            raise PipelineDefinitionError(
                "pipeline version must be a semantic version",
                pipeline_id=self.pipeline_id,
                version=self.version,
            ) from exc
        if not isinstance(self.stages, tuple) or not self.stages:
            raise PipelineDefinitionError(
                "a pipeline must declare at least one stage", pipeline_id=self.pipeline_id
            )
        stage_ids = tuple(stage.stage_id for stage in self.stages)
        _require_unique(stage_ids, "stage id", pipeline_id=self.pipeline_id)
        declared = set(stage_ids)
        for stage in self.stages:
            missing = sorted(set(stage.requires) - declared)
            if missing:
                raise PipelineDefinitionError(
                    "stage requires an undeclared stage (closure honesty)",
                    pipeline_id=self.pipeline_id,
                    stage_id=stage.stage_id,
                    missing=missing,
                )
        _require_unique(
            tuple(p.policy_id for p in self.policies), "policy id", pipeline_id=self.pipeline_id
        )
        _require_unique(
            tuple(p.plugin_id for p in self.plugins), "plugin id", pipeline_id=self.pipeline_id
        )
        _require_unique(
            tuple(f"{c.direction}:{c.capability_id}" for c in self.capabilities),
            "capability declaration",
            pipeline_id=self.pipeline_id,
        )
        policy_ids = {p.policy_id for p in self.policies}
        for stage in self.stages:
            unknown = sorted(set(stage.policies) - policy_ids)
            if unknown:
                raise PipelineDefinitionError(
                    "stage binds an undeclared policy (closure honesty)",
                    pipeline_id=self.pipeline_id,
                    stage_id=stage.stage_id,
                    unknown=unknown,
                )
        _require_identifier(self.strategy, "pipeline strategy", pipeline_id=self.pipeline_id)

    # -- derived views ----------------------------------------------------------------

    @property
    def identity(self) -> Identity:
        """The canonical identity of this pipeline *version* (id + version)."""
        return mint("pipeline", self.pipeline_id, self.version)

    @property
    def stage_ids(self) -> tuple[str, ...]:
        """The declared stage ids in declaration order."""
        return tuple(stage.stage_id for stage in self.stages)

    def stage(self, stage_id: str) -> StageDefinition:
        """The declared stage ``stage_id``.

        Raises:
            PipelineDefinitionError: if no such stage is declared (fail-closed).
        """
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        raise PipelineDefinitionError(
            "no such stage in pipeline", pipeline_id=self.pipeline_id, stage_id=stage_id
        )

    def graph(self) -> dict[str, tuple[str, ...]]:
        """The resolved requirement graph: stage id -> the stage ids it requires.

        The exact shape :func:`engine.foundation.composition.derive_order` consumes, so
        the pipeline is ordered by the repository's ordering authority without an
        adapter in between.
        """
        return {stage.stage_id: tuple(sorted(stage.requires)) for stage in self.stages}

    def policies_for(self, stage_id: str) -> tuple[PipelinePolicy, ...]:
        """Every declared policy binding ``stage_id``, in declaration order."""
        return tuple(policy for policy in self.policies if policy.binds(stage_id))

    def capabilities_by(self, direction: str) -> tuple[PipelineCapability, ...]:
        """The declared capabilities in ``direction`` (``provides`` / ``requires``)."""
        if direction not in CAPABILITY_DIRECTIONS:
            raise PipelineDefinitionError("unknown capability direction", direction=direction)
        return tuple(c for c in self.capabilities if c.direction == direction)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_type": self.pipeline_type,
            "version": self.version,
            "identity": self.identity.value,
            "stages": [stage.to_dict() for stage in self.stages],
            "capabilities": [c.to_dict() for c in self.capabilities],
            "policies": [p.to_dict() for p in self.policies],
            "plugins": [p.to_dict() for p in self.plugins],
            "governance": self.governance.to_dict(),
            "security": self.security.to_dict(),
            "strategy": self.strategy,
            "description": self.description,
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of the whole declaration."""
        return content_hash(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PipelineDefinition:
        """Rebuild a declaration from its serialized form (the discovery path).

        Raises:
            PipelineDefinitionError: if ``data`` is not a mapping or any nested
                declaration is malformed.
            PipelineTypeError: if the declared pipeline type is unregistered.
        """
        if not isinstance(data, Mapping):
            raise PipelineDefinitionError("pipeline declaration must be a mapping")
        governance = data.get("governance")
        security = data.get("security")
        return cls(
            pipeline_id=str(data.get("pipeline_id", "")),
            pipeline_type=str(data.get("pipeline_type", "")),
            version=str(data.get("version", "1.0.0")),
            stages=tuple(StageDefinition.from_dict(s) for s in data.get("stages", ())),
            capabilities=tuple(
                PipelineCapability.from_dict(c) for c in data.get("capabilities", ())
            ),
            policies=tuple(PipelinePolicy.from_dict(p) for p in data.get("policies", ())),
            plugins=tuple(PipelinePlugin.from_dict(p) for p in data.get("plugins", ())),
            governance=(
                PipelineGovernanceSpec.from_dict(governance)
                if governance is not None
                else PipelineGovernanceSpec()
            ),
            security=(
                PipelineSecuritySpec.from_dict(security)
                if security is not None
                else PipelineSecuritySpec()
            ),
            strategy=str(data.get("strategy", DEFAULT_PIPELINE_STRATEGY)),
            description=str(data.get("description", "")),
        )


@dataclass(frozen=True, slots=True)
class PipelinePlan:
    """The derived execution plan of one pipeline version: ``(wave, stage_id)`` pairs.

    A plan is *computed*, never authored. It exists as a distinct type because the
    derivation must be recorded: a plan carries its ``strategy`` and its own
    fingerprint, so the order actually executed is evidence rather than an assumption.
    """

    pipeline_id: str
    version: str
    strategy: str
    waves: tuple[tuple[int, str], ...]

    def __post_init__(self) -> None:
        # A plan validates its own fields with its own error rather than borrowing the
        # declaration helper: a malformed *plan* is a derivation fault, and reporting it as a
        # declaration fault would send a caller to look at the wrong object.
        if not isinstance(self.pipeline_id, str) or not self.pipeline_id:
            raise PipelinePlanError("plan pipeline id is required")
        if not isinstance(self.version, str) or not self.version:
            raise PipelinePlanError("plan version is required", pipeline_id=self.pipeline_id)
        if not isinstance(self.strategy, str) or not self.strategy:
            raise PipelinePlanError("plan strategy is required", pipeline_id=self.pipeline_id)
        if not isinstance(self.waves, tuple) or not self.waves:
            raise PipelinePlanError(
                "a plan must place at least one stage", pipeline_id=self.pipeline_id
            )

    @classmethod
    def derive(cls, definition: PipelineDefinition, *, strategy: str | None = None) -> PipelinePlan:
        """Derive the plan of ``definition`` using the named ordering strategy.

        Delegates to :func:`engine.foundation.composition.derive_order` — the single
        ordering authority — and reports a declared cycle through
        :func:`~engine.foundation.composition.unresolved_keys`, so the error names the
        stages that could not be placed rather than only that ordering failed.

        Raises:
            PipelinePlanError: if the strategy is unregistered, or the declared stage
                graph contains a cycle.
        """
        if not isinstance(definition, PipelineDefinition):
            raise PipelinePlanError("a plan is derived from a PipelineDefinition")
        resolved = strategy or definition.strategy
        try:
            get_strategy(resolved)
        except KeyError as exc:
            raise PipelinePlanError(
                "unregistered ordering strategy (extension is by registration)",
                pipeline_id=definition.pipeline_id,
                strategy=resolved,
            ) from exc
        graph = definition.graph()
        ordering = derive_order(graph, strategy=resolved)
        unresolved = unresolved_keys(graph, ordering)
        if unresolved:
            raise PipelinePlanError(
                "declared stage graph contains a cycle",
                pipeline_id=definition.pipeline_id,
                unresolved=unresolved,
            )
        return cls(
            pipeline_id=definition.pipeline_id,
            version=definition.version,
            strategy=resolved,
            waves=tuple((int(wave), key) for wave, key in ordering),
        )

    @property
    def identity(self) -> Identity:
        return mint("plan", self.pipeline_id, self.version, self.strategy)

    @property
    def stage_ids(self) -> tuple[str, ...]:
        """The planned stage ids in execution order."""
        return tuple(stage_id for _wave, stage_id in self.waves)

    @property
    def wave_indices(self) -> tuple[int, ...]:
        """The distinct wave indices in ascending order."""
        return tuple(sorted({wave for wave, _stage_id in self.waves}))

    @property
    def wave_count(self) -> int:
        return len(self.wave_indices)

    @property
    def max_parallelism(self) -> int:
        """The widest wave — the most stages the declarations permit to run at once."""
        return max(len(self.stages_in_wave(wave)) for wave in self.wave_indices)

    def stages_in_wave(self, wave: int) -> tuple[str, ...]:
        """The stage ids placed in ``wave``, sorted (deterministic)."""
        return tuple(sorted(stage_id for index, stage_id in self.waves if index == wave))

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "version": self.version,
            "strategy": self.strategy,
            "identity": self.identity.value,
            "wave_count": self.wave_count,
            "max_parallelism": self.max_parallelism,
            "waves": [{"wave": wave, "stage_id": stage_id} for wave, stage_id in self.waves],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of the derived plan."""
        return content_hash(self.to_dict())


for _pipeline_type, _type_description in SEED_PIPELINE_TYPES:
    register_pipeline_type(_pipeline_type, _type_description)
del _pipeline_type, _type_description


__all__ = [
    "CAPABILITY_DIRECTIONS",
    "DEFAULT_PIPELINE_STRATEGY",
    "SEED_PIPELINE_TYPES",
    "PipelineCapability",
    "PipelineDefinition",
    "PipelineGateSpec",
    "PipelineGovernanceSpec",
    "PipelinePlan",
    "PipelinePlugin",
    "PipelinePolicy",
    "PipelineSecuritySpec",
    "StageDefinition",
    "pipeline_type_description",
    "pipeline_types",
    "register_pipeline_type",
    "require_pipeline_type",
]
