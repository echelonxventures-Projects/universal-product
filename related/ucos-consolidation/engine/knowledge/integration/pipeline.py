"""UKI — the Constitutional Execution Path (EPIC-UKDA-002, final deliverable).

Binds every integration engine into the single, fail-closed constitutional sequence
every future capability must follow:

    Discover -> Analyze -> Reuse -> Extend -> Compose -> Create (only if necessary)
    -> Validate -> Certify -> Register -> Evolve

For one :class:`~engine.knowledge.integration.contracts.ArtifactIntent` the pipeline:

    * **Discover**  — mandatory deterministic discovery of existing knowledge (D2);
    * **Analyze**   — canonical ownership (D3) + duplicate prevention (D6), fail-closed;
    * **Reuse**     — reuse/extend/compose/create determination (D5);
    * **Extend/Compose/Create** — materialize the resulting object by the *least*
      creative route the reuse determination permits (creation is the last resort);
    * **Validate**  — UKDA validation of the resulting base (D-UKDA Part 10);
    * **Certify**   — UKDA certification of the resulting object (Part 11);
    * **Register**  — duplication-free registration plan (D9);
    * **Evolve**    — the end-to-end traceability chain (D7) + governance grounding (D8).

Every engine is reused verbatim; the pipeline adds only sequencing and fail-closed
gating. It is deterministic: identical bases and intents yield identical decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.knowledge.certification import KnowledgeCertifier
from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.integration.composition import AutonomousComposer
from engine.knowledge.integration.contracts import (
    ArtifactIntent,
    DiscoveryPhase,
    Disposition,
    Operation,
    SequenceStage,
)
from engine.knowledge.integration.dependency import DependencyIntegration
from engine.knowledge.integration.discovery import DiscoveryProtocol
from engine.knowledge.integration.duplication import DuplicatePreventionEngine
from engine.knowledge.integration.errors import IntegrationError
from engine.knowledge.integration.governance import GOVERNANCE_KINDS, GovernanceIntegration
from engine.knowledge.integration.ownership import OwnershipProtocol
from engine.knowledge.integration.registration import RegistrationIntegration
from engine.knowledge.integration.reuse import ReuseEngine
from engine.knowledge.integration.traceability import TraceabilityEngine
from engine.knowledge.model import Lifecycle
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.validation import validate_base


class Outcome(str, Enum):
    """The terminal outcome of a constitutional pipeline run."""

    CREATED = "created"
    MODIFIED = "modified"
    EXTENDED = "extended"
    COMPOSED = "composed"
    REUSED = "reused"
    BLOCKED = "blocked"


class StageStatus(str, Enum):
    DONE = "done"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class StageRecord:
    """The immutable record of one execution-path stage."""

    stage: SequenceStage
    status: StageStatus
    detail: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"stage": self.stage.value, "status": self.status.value, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class ConstitutionalDecision:
    """The deterministic outcome of the constitutional execution path for one intent."""

    intent_id: str
    outcome: Outcome
    disposition: Disposition
    stages: tuple[StageRecord, ...]
    artifact: dict[str, Any] | None = None
    reasons: tuple[str, ...] = ()

    @property
    def accepted(self) -> bool:
        return self.outcome is not Outcome.BLOCKED

    def stage(self, stage: SequenceStage) -> StageRecord | None:
        for record in self.stages:
            if record.stage is stage:
                return record
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "outcome": self.outcome.value,
            "accepted": self.accepted,
            "disposition": self.disposition.value,
            "reasons": list(self.reasons),
            "artifact": self.artifact,
            "stages": [s.to_dict() for s in self.stages],
        }


class ConstitutionalPipeline:
    """Runs the fail-closed constitutional execution path over an intent (final deliverable)."""

    __slots__ = (
        "_base",
        "_discovery",
        "_ownership",
        "_duplication",
        "_reuse",
        "_dependency",
        "_composer",
        "_certifier",
    )

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base
        self._discovery = DiscoveryProtocol(base)
        self._ownership = OwnershipProtocol()
        self._duplication = DuplicatePreventionEngine(base)
        self._reuse = ReuseEngine(base)
        self._dependency = DependencyIntegration(base)
        self._composer = AutonomousComposer(base)
        self._certifier = KnowledgeCertifier()

    @property
    def base(self) -> KnowledgeBase:
        return self._base

    def _lifecycle_for(self, intent: ArtifactIntent) -> Lifecycle:
        existing = self._base.get_object(intent.intent_id)
        if existing is not None:
            return existing.lifecycle
        return Lifecycle.DRAFT

    def _trial(self, obj: CanonicalKnowledgeObject) -> KnowledgeBase:
        if self._base.has_object(obj.cko_id):
            return self._base.replace_object(obj)
        return self._base.with_object(obj)

    def execute(self, intent: ArtifactIntent) -> ConstitutionalDecision:
        """Run the full constitutional sequence for ``intent`` (deterministic, fail-closed)."""
        stages: list[StageRecord] = []

        # 1. DISCOVER — mandatory (UKI-LAW-002).
        discovery = self._discovery.discover(intent, phase=DiscoveryPhase.CREATION)
        stages.append(StageRecord(SequenceStage.DISCOVER, StageStatus.DONE, discovery.to_dict()))

        # 2. ANALYZE — ownership (UKI-LAW-005) + duplicate prevention (UKI-LAW-004).
        ownership = self._ownership.assess(intent, self._base)
        duplication = self._duplication.screen(intent)
        analyze_detail = {
            "ownership": ownership.to_dict(),
            "duplication": duplication.to_dict(),
            "dependency": self._dependency.view_intent(intent).to_dict(),
        }
        # A pure, same-owner semantic duplicate on a CREATE is not blocked here: the
        # constitutional response is to REUSE the existing canonical artifact
        # (UKI-LAW-003), which itself prevents the duplicate and preserves Single
        # Canonical Truth (UKI-LAW-004). Every other duplication mode — overlapping
        # ownership, conflicting capability, parallel implementation, redundant
        # universe, divergent identity — and any duplicate under a MODIFY (where the
        # identity already exists distinctly) remains fail-closed.
        reuse_exempt = intent.operation is Operation.CREATE
        blocking_duplication = tuple(
            kind
            for kind in duplication.kinds()
            if not (reuse_exempt and kind == "semantic-duplicate")
        )
        if not ownership.satisfied or blocking_duplication:
            stages.append(StageRecord(SequenceStage.ANALYZE, StageStatus.BLOCKED, analyze_detail))
            reasons = tuple((*ownership.issues, *blocking_duplication))
            return ConstitutionalDecision(
                intent_id=intent.intent_id,
                outcome=Outcome.BLOCKED,
                disposition=Disposition.CREATE,
                stages=tuple(stages),
                reasons=reasons or ("analysis rejected the intent",),
            )
        stages.append(StageRecord(SequenceStage.ANALYZE, StageStatus.DONE, analyze_detail))

        # 3. REUSE — determination (UKI-LAW-003).
        reuse = self._reuse.assess(intent)
        stages.append(StageRecord(SequenceStage.REUSE, StageStatus.DONE, reuse.to_dict()))

        # 4. EXTEND / COMPOSE / CREATE — the least-creative permitted route.
        resulting, outcome, extend_status, compose_status, create_status = self._materialize(
            intent, reuse.disposition
        )
        stages.append(
            StageRecord(
                SequenceStage.EXTEND,
                extend_status,
                {"targets": list(reuse.targets)} if extend_status is StageStatus.DONE else {},
            )
        )
        stages.append(
            StageRecord(
                SequenceStage.COMPOSE,
                compose_status,
                {"components": list(reuse.targets)} if compose_status is StageStatus.DONE else {},
            )
        )
        stages.append(
            StageRecord(
                SequenceStage.CREATE,
                create_status,
                {"authored": resulting.cko_id} if create_status is StageStatus.DONE else {},
            )
        )

        trial = self._trial(resulting) if outcome is not Outcome.REUSED else self._base

        # 5. VALIDATE — fail-closed (UKDA Part 10).
        validation = validate_base(trial)
        if not validation.accepted:
            stages.append(
                StageRecord(SequenceStage.VALIDATE, StageStatus.BLOCKED, validation.to_dict())
            )
            return ConstitutionalDecision(
                intent_id=intent.intent_id,
                outcome=Outcome.BLOCKED,
                disposition=reuse.disposition,
                stages=tuple(stages),
                artifact=resulting.to_dict(),
                reasons=("resulting base failed knowledge validation",),
            )
        stages.append(StageRecord(SequenceStage.VALIDATE, StageStatus.DONE, validation.to_dict()))

        # 6. CERTIFY — completeness attestation (UKDA Part 11).
        certification = self._certifier.certify_object(resulting, trial)
        stages.append(StageRecord(SequenceStage.CERTIFY, StageStatus.DONE, certification.to_dict()))

        # 7. REGISTER — duplication-free (UKI-LAW-008).
        registration = RegistrationIntegration(self._base).plan_object(resulting)
        stages.append(StageRecord(SequenceStage.REGISTER, StageStatus.DONE, registration.to_dict()))

        # 8. EVOLVE — end-to-end traceability (UKI-LAW-006) + governance grounding (UKI-LAW-007).
        trace = TraceabilityEngine(trial).trace(resulting.cko_id)
        evolve_detail: dict[str, Any] = {"traceability": trace.to_dict()}
        if resulting.kind in GOVERNANCE_KINDS:
            evolve_detail["governance"] = (
                GovernanceIntegration(trial).bind_object(resulting.cko_id).to_dict()
            )
        stages.append(StageRecord(SequenceStage.EVOLVE, StageStatus.DONE, evolve_detail))

        reasons = (
            ("modify evolves the existing canonical artifact in place; creation avoided",)
            if outcome is Outcome.MODIFIED
            else reuse.reasons
        )
        return ConstitutionalDecision(
            intent_id=intent.intent_id,
            outcome=outcome,
            disposition=reuse.disposition,
            stages=tuple(stages),
            artifact=resulting.to_dict(),
            reasons=reasons,
        )

    def _materialize(
        self, intent: ArtifactIntent, disposition: Disposition
    ) -> tuple[CanonicalKnowledgeObject, Outcome, StageStatus, StageStatus, StageStatus]:
        """Produce the resulting object by the least-creative route the reuse permits.

        MODIFY is operation-aware and takes precedence over the create-avoidance
        dispositions: the artifact already exists and is owned by the caller (the
        Ownership Protocol has asserted this), so it is *evolved in place* — the
        create-family routes (reuse/extend/compose/create) never apply to a modify.
        """
        lifecycle = self._lifecycle_for(intent)

        if intent.operation is Operation.MODIFY:
            obj = intent.to_cko(lifecycle=lifecycle)
            return (
                obj,
                Outcome.MODIFIED,
                StageStatus.SKIPPED,
                StageStatus.SKIPPED,
                StageStatus.SKIPPED,
            )

        if disposition is Disposition.REUSE:
            target = self._reuse.assess(intent).targets[0]
            existing = self._base.require_object(target)
            return (
                existing,
                Outcome.REUSED,
                StageStatus.SKIPPED,
                StageStatus.SKIPPED,
                StageStatus.SKIPPED,
            )

        if disposition is Disposition.EXTEND:
            target = self._reuse.assess(intent).targets[0]
            parent = intent.parent or target
            obj = CanonicalKnowledgeObject.create(
                cko_id=intent.intent_id,
                kind=intent.kind,
                title=intent.title,
                statement=intent.statement,
                rationale=intent.rationale,
                universe=intent.universe,
                authority=intent.authority,
                owner=intent.owner,
                lifecycle=lifecycle,
                version=intent.version,
                parent=parent,
                dependencies=intent.dependencies,
                consumers=intent.consumers,
                knowledge_links=tuple(sorted(set((*intent.knowledge_links, target)))),
                decision_links=intent.decision_links,
                tags=intent.tags,
            )
            return obj, Outcome.EXTENDED, StageStatus.DONE, StageStatus.SKIPPED, StageStatus.DONE

        if disposition is Disposition.COMPOSE:
            result = self._composer.compose(intent)
            if result.sufficient and result.composed is not None:
                obj = CanonicalKnowledgeObject.from_dict(result.composed)
                return (
                    obj,
                    Outcome.COMPOSED,
                    StageStatus.SKIPPED,
                    StageStatus.DONE,
                    StageStatus.DONE,
                )
            # Composition proved insufficient at materialization — fall back to create.
            return (
                intent.to_cko(lifecycle=lifecycle),
                Outcome.CREATED,
                StageStatus.SKIPPED,
                StageStatus.SKIPPED,
                StageStatus.DONE,
            )

        # CREATE — the last resort.
        return (
            intent.to_cko(lifecycle=lifecycle),
            Outcome.CREATED,
            StageStatus.SKIPPED,
            StageStatus.SKIPPED,
            StageStatus.DONE,
        )

    def require(self, intent: ArtifactIntent) -> ConstitutionalDecision:
        """Execute the path or raise if the intent is constitutionally blocked (fail-closed)."""
        decision = self.execute(intent)
        if not decision.accepted:
            raise IntegrationError(
                "constitutional execution path blocked the intent",
                intent_id=intent.intent_id,
                reasons=list(decision.reasons),
            )
        return decision

    def assimilate(self, repository: Any, *, default_owner: str | None = None) -> Any:
        """Accept a live repository and produce a fully assimilated RepositorySubject.

        The repository may be a filesystem path (``str``/``Path`` — probed live into a
        deterministic snapshot) or an already-captured ``RepositorySnapshot``. Every
        discovered unit is routed through :meth:`execute`, so discovery, ownership,
        dependency, and reuse determination are performed by the existing engines —
        this method adds only repository probing and assimilation, never a second
        execution controller (EPIC-UKDA-004).
        """
        from engine.knowledge.integration.repository import (
            RepositoryAssimilator,
            RepositoryProbe,
            RepositorySnapshot,
        )

        snapshot = (
            repository
            if isinstance(repository, RepositorySnapshot)
            else RepositoryProbe().capture(repository)
        )
        kwargs = {"default_owner": default_owner} if default_owner is not None else {}
        return RepositoryAssimilator(self, **kwargs).assimilate(snapshot)


__all__ = [
    "Outcome",
    "StageStatus",
    "StageRecord",
    "ConstitutionalDecision",
    "ConstitutionalPipeline",
]
