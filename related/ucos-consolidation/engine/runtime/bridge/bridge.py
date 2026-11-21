"""EPIC-RTE-003 — Runtime Integration & Repository Execution Bridge.

The single, canonical **Runtime Bridge** that connects the repository lifecycle to
runtime execution. It **implements only integration** (the EPIC-RTE-003 mission):
it reuses the existing engines verbatim and duplicates none of their logic —

    * **Runtime Composition** (EPIC-006) — :func:`~engine.runtime.composition.compose`;
    * **Runtime Execution Platform** (EPIC-RTE-002) —
      :class:`~engine.runtime.execution.platform.ExecutionPlatform` (composition,
      execution state, checkpoint, continuation, recovery, replay, authorization,
      monitoring — all reused, none reimplemented);
    * **Validation** (EPIC-007) — :func:`~engine.validation.executor.validate_runtime_unit`;
    * **Certification** (EPIC-008) — :func:`~engine.certification.engine.certify_validation`;
    * **Repository Acceptance** (EPIC-VAL-002) —
      :func:`~engine.acceptance.engine.accept_repository`;
    * **Knowledge** (EPIC-UKDA) — the canonical
      :class:`~engine.knowledge.store.KnowledgeBase` + content-addressed
      :class:`~engine.knowledge.cko.CanonicalKnowledgeObject`.

The bridge realises the six integration objectives as pure, deterministic functions
(each a thin adapter over a reused engine), and unifies them behind the
:class:`RuntimeBridge` facade:

    1. RepositorySubject → Runtime Composition   (:func:`compose_repository`)
    2. Runtime Composition → Runtime Execution   (:func:`execute_composition`)
    3. Runtime Execution → Validation            (:func:`validate_execution`)
    4. Runtime Execution → Certification         (:func:`certify_execution`)
    5. Runtime Execution → Acceptance            (:func:`accept_execution`)
    6. Execution Evidence → Knowledge            (:func:`record_execution_evidence`)

Everything is deterministic (IMP-007 §5): every stage is a pure function of its
inputs with no wall-clock or ambient state, so identical inputs yield a
byte-identical :class:`~engine.runtime.bridge.contracts.RepositoryExecutionRecord`.
Everything is **replayable** and **resumable**: the bridge exposes the reused
platform's replay/checkpoint/continue/recover capabilities over the recorded run
(no execution path is skipped, and no runtime logic is duplicated to provide them).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.acceptance.engine import (
    AcceptanceDecision,
    accept_repository,
    enforce_acceptance,
)
from engine.acceptance.evidence import AcceptanceEvidence, build_acceptance_evidence
from engine.certification.contracts import CertificationClass
from engine.certification.engine import certify_validation
from engine.certification.evidence import build_certification_evidence
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    content_hash,
)
from engine.knowledge.store import KnowledgeBase
from engine.runtime.assembly import RuntimeUnit
from engine.runtime.bridge.contracts import RepositoryExecutionRecord, UnitAssurance
from engine.runtime.bridge.errors import BridgeInputError
from engine.runtime.composition import RuntimeComposition, Universe, compose
from engine.runtime.execution.platform import ExecutionPlatform, ExecutionResult
from engine.runtime.planner import DEFAULT_COORDINATION
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import validate_runtime_unit

if TYPE_CHECKING:  # pragma: no cover - typing only
    from engine.acceptance.contracts import RepositorySubject as _RepositorySubjectT
    from engine.acceptance.gates import AcceptanceGate
    from engine.runtime.execution.checkpoint import Checkpoint
    from engine.runtime.execution.coordinator import ExecutionRun
    from engine.runtime.execution.replay_validation import ReplayValidation
    from engine.validation.contracts import ValidationReport

_logger = get_logger("runtime.bridge")

#: The default owner recorded on the knowledge evidence object the bridge authors.
DEFAULT_KNOWLEDGE_OWNER = "UCOS-RUNTIME-BRIDGE"

#: The default universe the knowledge evidence object is filed under.
DEFAULT_KNOWLEDGE_UNIVERSE = "runtime"


@dataclass(frozen=True, slots=True)
class ValidatedUnit:
    """The intermediate projection between the validation and certification bridges.

    Carries one composed universe's assembled unit, its modelled execution status,
    and the reused Validation Report + Evidence — the exact inputs the Certification
    engine consumes. It re-derives nothing.
    """

    universe_id: str
    unit: RuntimeUnit
    execution_status: str
    report: ValidationReport
    evidence: ValidationEvidence


# --------------------------------------------------------------------------- #
# Bridge 1 — RepositorySubject → Runtime Composition                           #
# --------------------------------------------------------------------------- #


def compose_repository(
    subject: _RepositorySubjectT | Mapping[str, Any],
    universes: Iterable[Universe | RuntimeUnit],
    *,
    coordination: str = DEFAULT_COORDINATION,
) -> RuntimeComposition:
    """Bridge an assimilated repository into a deterministic Runtime Composition.

    The repository ``subject`` (an assimilated
    :class:`~engine.acceptance.contracts.RepositorySubject`, or a raw facts mapping
    normalised through the acceptance engine's own assimilation) anchors the
    lifecycle; its already-assembled runtime ``universes`` are composed by the
    reused :func:`~engine.runtime.composition.compose` engine. Bare
    :class:`~engine.runtime.assembly.RuntimeUnit` members are bound into Universes
    verbatim via :meth:`Universe.of`.

    Raises:
        BridgeInputError: if no universes are supplied or a member is neither a
            Universe nor a RuntimeUnit.
        RepositorySubjectError: if ``subject`` cannot be assimilated (reused).
        RuntimeCompositionError, RuntimeGraphError, …: on any composition failure
            (reused verbatim — the bridge adds no composition logic).
    """
    normalised = _subject(subject)
    members = _materialise_universes(universes)
    with trace(
        "runtime.bridge.compose",
        repository=normalised.repository_id,
        universes=len(members),
        coordination=coordination,
    ):
        composition = compose(members, coordination=coordination)
    _logger.info(
        "runtime.bridge.composed",
        repository=normalised.repository_id,
        composition_id=composition.composition_id,
        universes=len(members),
    )
    return composition


# --------------------------------------------------------------------------- #
# Bridge 2 — Runtime Composition → Runtime Execution                           #
# --------------------------------------------------------------------------- #


def execute_composition(
    composition: RuntimeComposition,
    *,
    outcomes: Mapping[str, str] | None = None,
    execution_subject: str = "engineering",
    platform: ExecutionPlatform | None = None,
) -> ExecutionResult:
    """Bridge a composition into the reused Runtime Execution Platform.

    Delegates end to end to :meth:`ExecutionPlatform.run`, which produces a
    deterministic, resumable, observable :class:`ExecutionResult` (the run plus
    monitor/metrics/health/diagnostics/snapshot). The bridge executes nothing
    itself — it reuses the platform verbatim.
    """
    engine = platform if platform is not None else ExecutionPlatform()
    result = engine.run(composition, outcomes=outcomes, subject=execution_subject)
    _logger.info(
        "runtime.bridge.executed",
        composition_id=composition.composition_id,
        run_id=result.run_id,
        status=result.status,
    )
    return result


# --------------------------------------------------------------------------- #
# Bridge 3 — Runtime Execution → Validation                                    #
# --------------------------------------------------------------------------- #


def validate_execution(execution: ExecutionResult) -> tuple[ValidatedUnit, ...]:
    """Bridge an executed composition into Validation, one composed unit at a time.

    Every composed universe's assembled runtime unit is validated by the reused
    :func:`~engine.validation.executor.validate_runtime_unit` engine (no execution
    path is skipped), and its modelled execution status is carried alongside so the
    downstream record ties assurance to the run. Returns one
    :class:`ValidatedUnit` per composed universe, in the composition's stable order.
    """
    run = execution.run
    composition = run.composition
    validated: list[ValidatedUnit] = []
    with trace("runtime.bridge.validate", run_id=run.run_id):
        for universe in composition.universes:
            report = validate_runtime_unit(universe.unit)
            validated.append(
                ValidatedUnit(
                    universe_id=universe.universe_id,
                    unit=universe.unit,
                    execution_status=run.state_of(universe.universe_id).status,
                    report=report,
                    evidence=build_validation_evidence(report),
                )
            )
    _logger.info(
        "runtime.bridge.validated",
        run_id=run.run_id,
        units=len(validated),
        blocking=sum(1 for v in validated if not v.report.accepted),
    )
    return tuple(validated)


# --------------------------------------------------------------------------- #
# Bridge 4 — Runtime Execution → Certification                                 #
# --------------------------------------------------------------------------- #


def certify_execution(
    validated: Iterable[ValidatedUnit],
    *,
    certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS,
) -> tuple[UnitAssurance, ...]:
    """Bridge validated units into Certification, producing per-unit assurances.

    Each unit's reused Validation Report + Evidence is certified by the reused
    :func:`~engine.certification.engine.certify_validation` engine, closing the
    evidence chain validation → certification. Returns one :class:`UnitAssurance`
    per validated unit (the modelled execution status, the validation record, and
    the certification record bound together).
    """
    assurances: list[UnitAssurance] = []
    for item in validated:
        decision = certify_validation(
            item.report,
            item.evidence,
            version=item.unit.version,
            certification_class=certification_class,
        )
        assurances.append(
            UnitAssurance(
                universe_id=item.universe_id,
                runtime_id=item.unit.runtime_id,
                blueprint_id=item.unit.blueprint_id,
                execution_status=item.execution_status,
                validation=item.report,
                validation_evidence=item.evidence,
                certification=decision,
                certification_evidence=build_certification_evidence(decision),
            )
        )
    _logger.info(
        "runtime.bridge.certified",
        units=len(assurances),
        not_certified=sum(1 for a in assurances if not a.certified),
    )
    return tuple(assurances)


# --------------------------------------------------------------------------- #
# Bridge 5 — Runtime Execution → Acceptance                                    #
# --------------------------------------------------------------------------- #


def accept_execution(
    subject: _RepositorySubjectT | Mapping[str, Any],
    execution: ExecutionResult,
    *,
    strict: bool = False,
    gates: Iterable[AcceptanceGate] | None = None,
) -> tuple[AcceptanceDecision, AcceptanceEvidence]:
    """Bridge an executed repository into the reused Repository Acceptance gate.

    Runs the reused :func:`~engine.acceptance.engine.accept_repository` suite over
    the assimilated ``subject`` and builds the reproducible Acceptance Evidence. In
    ``strict`` mode a rejected repository raises (fail-closed, reused verbatim). The
    ``execution`` result is threaded so the acceptance determination is tied to the
    modelled run in the bridge record.

    Raises:
        AcceptanceRejectedError: if ``strict`` and the repository is rejected (reused).
    """
    decision = accept_repository(subject, gates=gates)
    enforce_acceptance(decision, strict=strict)
    evidence = build_acceptance_evidence(decision)
    _logger.info(
        "runtime.bridge.accepted",
        repository=decision.repository_id,
        run_id=execution.run_id,
        acceptance_id=decision.acceptance_id,
        accepted=decision.accepted,
    )
    return decision, evidence


# --------------------------------------------------------------------------- #
# Bridge 6 — Execution Evidence → Knowledge                                    #
# --------------------------------------------------------------------------- #


def record_execution_evidence(
    *,
    subject: _RepositorySubjectT | Mapping[str, Any],
    execution: ExecutionResult,
    assurances: Iterable[UnitAssurance],
    acceptance: AcceptanceDecision,
    acceptance_evidence: AcceptanceEvidence,
    base: KnowledgeBase | None = None,
    owner: str = DEFAULT_KNOWLEDGE_OWNER,
    universe: str = DEFAULT_KNOWLEDGE_UNIVERSE,
) -> tuple[KnowledgeBase, CanonicalKnowledgeObject]:
    """Bridge the execution's evidence chain into the canonical Knowledge Base.

    Every reproducible evidence reference produced by the lifecycle — the modelled
    execution result, each unit's validation and certification evidence, and the
    repository acceptance evidence — is collected and recorded, verbatim, into the
    ``evidence`` topology of a single content-addressed
    :class:`~engine.knowledge.cko.CanonicalKnowledgeObject` (kind ``evidence``). The
    object is added to ``base`` (a fresh empty base by default) through the reused
    :meth:`KnowledgeBase.with_object` authoring path; a same-identity re-recording
    replaces the prior object idempotently. Returns the new, immutable base and the
    authored evidence object.
    """
    normalised = _subject(subject)
    materialised = tuple(assurances)
    refs = _collect_evidence_refs(execution, materialised, acceptance, acceptance_evidence)
    digest = content_hash(
        {
            "repository_id": normalised.repository_id,
            "epic_id": normalised.epic_id,
            "run_id": execution.run_id,
            "acceptance_id": acceptance.acceptance_id,
            "evidence": list(refs),
        }
    )
    cko = CanonicalKnowledgeObject.create(
        cko_id=f"UCOS-EVIDENCE-{digest[:16]}",
        kind=KnowledgeKind.EVIDENCE,
        title=(f"Runtime execution evidence — {normalised.repository_id} ({normalised.epic_id})"),
        statement=(
            f"Deterministic runtime-bridge evidence for repository "
            f"{normalised.repository_id} under {normalised.epic_id}: execution run "
            f"{execution.run_id} status {execution.status}; acceptance "
            f"{acceptance.acceptance_id} "
            f"{'accepted' if acceptance.accepted else 'rejected'}; "
            f"{len(materialised)} composed unit(s) validated and certified."
        ),
        universe=universe,
        authority=KnowledgeAuthority.ENGINEERING,
        owner=owner,
        lifecycle=Lifecycle.DRAFT,
        version="1.0.0",
        evidence=refs,
        tags=(
            "runtime-bridge",
            f"status:{execution.status}",
            f"acceptance:{'accepted' if acceptance.accepted else 'rejected'}",
        ),
    )
    target = base if base is not None else KnowledgeBase()
    new_base = (
        target.replace_object(cko) if target.has_object(cko.cko_id) else target.with_object(cko)
    )
    _logger.info(
        "runtime.bridge.recorded",
        repository=normalised.repository_id,
        cko_id=cko.cko_id,
        evidence_refs=len(refs),
    )
    return new_base, cko


# --------------------------------------------------------------------------- #
# The canonical facade                                                         #
# --------------------------------------------------------------------------- #


class RuntimeBridge:
    """The single canonical Runtime Bridge connecting repository lifecycle to execution.

    A thin, deterministic coordinator: every stage delegates to the module-level
    bridge function that adapts a reused engine, and :meth:`run` threads all six
    stages into one immutable
    :class:`~engine.runtime.bridge.contracts.RepositoryExecutionRecord`. The facade
    also surfaces the reused Execution Platform's replay/checkpoint/continue/recover
    capabilities over a produced record, so a bridged execution is **replayable** and
    **resumable** without any duplicate runtime logic.
    """

    __slots__ = ("_platform",)

    def __init__(self, platform: ExecutionPlatform | None = None) -> None:
        self._platform = platform if platform is not None else ExecutionPlatform()

    @property
    def platform(self) -> ExecutionPlatform:
        return self._platform

    # -- individual stages -----------------------------------------------------

    def compose(
        self,
        subject: _RepositorySubjectT | Mapping[str, Any],
        universes: Iterable[Universe | RuntimeUnit],
        *,
        coordination: str = DEFAULT_COORDINATION,
    ) -> RuntimeComposition:
        return compose_repository(subject, universes, coordination=coordination)

    def execute(
        self,
        composition: RuntimeComposition,
        *,
        outcomes: Mapping[str, str] | None = None,
        execution_subject: str = "engineering",
    ) -> ExecutionResult:
        return execute_composition(
            composition,
            outcomes=outcomes,
            execution_subject=execution_subject,
            platform=self._platform,
        )

    def validate(self, execution: ExecutionResult) -> tuple[ValidatedUnit, ...]:
        return validate_execution(execution)

    def certify(
        self,
        validated: Iterable[ValidatedUnit],
        *,
        certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS,
    ) -> tuple[UnitAssurance, ...]:
        return certify_execution(validated, certification_class=certification_class)

    def accept(
        self,
        subject: _RepositorySubjectT | Mapping[str, Any],
        execution: ExecutionResult,
        *,
        strict: bool = False,
        gates: Iterable[AcceptanceGate] | None = None,
    ) -> tuple[AcceptanceDecision, AcceptanceEvidence]:
        return accept_execution(subject, execution, strict=strict, gates=gates)

    def record(
        self,
        *,
        subject: _RepositorySubjectT | Mapping[str, Any],
        execution: ExecutionResult,
        assurances: Iterable[UnitAssurance],
        acceptance: AcceptanceDecision,
        acceptance_evidence: AcceptanceEvidence,
        base: KnowledgeBase | None = None,
        owner: str = DEFAULT_KNOWLEDGE_OWNER,
        universe: str = DEFAULT_KNOWLEDGE_UNIVERSE,
    ) -> tuple[KnowledgeBase, CanonicalKnowledgeObject]:
        return record_execution_evidence(
            subject=subject,
            execution=execution,
            assurances=assurances,
            acceptance=acceptance,
            acceptance_evidence=acceptance_evidence,
            base=base,
            owner=owner,
            universe=universe,
        )

    # -- end-to-end ------------------------------------------------------------

    def run(
        self,
        subject: _RepositorySubjectT | Mapping[str, Any],
        universes: Iterable[Universe | RuntimeUnit],
        *,
        coordination: str = DEFAULT_COORDINATION,
        outcomes: Mapping[str, str] | None = None,
        execution_subject: str = "engineering",
        certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS,
        strict: bool = False,
        gates: Iterable[AcceptanceGate] | None = None,
        base: KnowledgeBase | None = None,
        knowledge_owner: str = DEFAULT_KNOWLEDGE_OWNER,
        knowledge_universe: str = DEFAULT_KNOWLEDGE_UNIVERSE,
    ) -> RepositoryExecutionRecord:
        """Thread a repository through all six bridges into one canonical record.

        Deterministic (ORL-20): identical inputs yield a byte-identical
        :class:`RepositoryExecutionRecord`. Fail-closed acceptance is honoured when
        ``strict`` is set (reused verbatim).
        """
        normalised = _subject(subject)
        with trace(
            "runtime.bridge.run",
            repository=normalised.repository_id,
            epic=normalised.epic_id,
        ):
            composition = self.compose(normalised, universes, coordination=coordination)
            execution = self.execute(
                composition, outcomes=outcomes, execution_subject=execution_subject
            )
            validated = self.validate(execution)
            assurances = self.certify(validated, certification_class=certification_class)
            acceptance, acceptance_evidence = self.accept(
                normalised, execution, strict=strict, gates=gates
            )
            _, knowledge_object = self.record(
                subject=normalised,
                execution=execution,
                assurances=assurances,
                acceptance=acceptance,
                acceptance_evidence=acceptance_evidence,
                base=base,
                owner=knowledge_owner,
                universe=knowledge_universe,
            )
            record = RepositoryExecutionRecord.create(
                repository_id=normalised.repository_id,
                epic_id=normalised.epic_id,
                composition=composition,
                execution=execution,
                assurances=assurances,
                acceptance=acceptance,
                acceptance_evidence=acceptance_evidence,
                knowledge_object=knowledge_object,
                disclosure=composition.disclosure,
            )
        _logger.info(
            "runtime.bridge.run.complete",
            repository=normalised.repository_id,
            bridge_id=record.bridge_id,
            run_id=record.run_id,
            status=record.status,
            accepted=record.accepted,
            certified=record.certified,
        )
        return record

    def into_knowledge(
        self, record: RepositoryExecutionRecord, *, base: KnowledgeBase | None = None
    ) -> KnowledgeBase:
        """Add ``record``'s authored evidence object to ``base`` (reused authoring path)."""
        target = base if base is not None else KnowledgeBase()
        obj = record.knowledge_object
        if target.has_object(obj.cko_id):
            return target.replace_object(obj)
        return target.with_object(obj)

    # -- replay / resume (reused platform capabilities over a record) ----------

    def replay(self, record: RepositoryExecutionRecord) -> ExecutionRun:
        """Deterministically replay the record's execution (reused platform.replay)."""
        return self._platform.replay(record.composition, record.execution.run)

    def verify_replay(self, record: RepositoryExecutionRecord) -> ReplayValidation:
        """Validate that a replay reproduces the record's run byte-for-byte (reused)."""
        return self._platform.validate_replay(record.composition, record.execution.run)

    def require_replay(self, record: RepositoryExecutionRecord) -> ReplayValidation:
        """Assert a byte-identical replay or raise (reused platform.require_replay)."""
        return self._platform.require_replay(record.composition, record.execution.run)

    def checkpoint(
        self, record: RepositoryExecutionRecord, *, through_stage: int | None = None
    ) -> Checkpoint:
        """Checkpoint the record's execution for resumption (reused platform)."""
        return self._platform.checkpoint(record.execution.run, through_stage=through_stage)

    def resume(
        self,
        record: RepositoryExecutionRecord,
        checkpoint: Checkpoint,
        *,
        outcomes: Mapping[str, str] | None = None,
        execution_subject: str = "engineering",
    ) -> ExecutionRun:
        """Resume the record's execution from a checkpoint (reused platform)."""
        return self._platform.continue_from(
            record.composition, checkpoint, outcomes=outcomes, subject=execution_subject
        )

    def recover(self, record: RepositoryExecutionRecord) -> Checkpoint:
        """Establish a consistent recovery checkpoint for the run (reused platform)."""
        return self._platform.recover(record.execution.run)


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _subject(
    subject: _RepositorySubjectT | Mapping[str, Any],
) -> _RepositorySubjectT:
    """Normalise a subject or raw facts mapping into a RepositorySubject (reused)."""
    from engine.acceptance.contracts import RepositorySubject

    if isinstance(subject, RepositorySubject):
        return subject
    return RepositorySubject.from_mapping(subject)


def _materialise_universes(
    universes: Iterable[Universe | RuntimeUnit],
) -> list[Universe]:
    """Bind bare RuntimeUnits into Universes; validate the composition set."""
    members: list[Universe] = []
    for item in universes:
        if isinstance(item, Universe):
            members.append(item)
        elif isinstance(item, RuntimeUnit):
            members.append(Universe.of(item))
        else:
            raise BridgeInputError(
                "composition member must be a Universe or a RuntimeUnit",
                got=type(item).__name__,
            )
    if not members:
        raise BridgeInputError("a repository composition requires at least one runtime universe")
    return members


def _collect_evidence_refs(
    execution: ExecutionResult,
    assurances: tuple[UnitAssurance, ...],
    acceptance: AcceptanceDecision,
    acceptance_evidence: AcceptanceEvidence,
) -> tuple[str, ...]:
    """Collect every reproducible evidence reference of the lifecycle (sorted, unique)."""
    refs: set[str] = {
        f"execution:{execution.run_id}:{content_hash(execution.to_dict())}",
        f"acceptance:{acceptance.acceptance_id}:{acceptance_evidence.content_sha256()}",
    }
    for assurance in assurances:
        refs.update(assurance.evidence_refs())
    return tuple(sorted(refs))


__all__ = [
    "DEFAULT_KNOWLEDGE_OWNER",
    "DEFAULT_KNOWLEDGE_UNIVERSE",
    "ValidatedUnit",
    "compose_repository",
    "execute_composition",
    "validate_execution",
    "certify_execution",
    "accept_execution",
    "record_execution_evidence",
    "RuntimeBridge",
]
