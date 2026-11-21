"""UCOS-CTRL-000001 — Runtime Discovery and the Completion Gate (Wave 6).

Before this module the control plane's only universe was ``_demo_universe()``:
three invented backlog items, two invented milestones and an agent called Alpha.
It demonstrated the engines and described nothing. Everything the CLI printed was
a literal somebody typed.

:class:`ControlPlane` replaces that with derivation. Nothing below is authored —
every object is a projection of something the repository already records:

    vision      the declared manifest's statement
    goals       the programmes the registry substrate records
    objectives  the artifact categories each programme actually contains
    milestones  the registry volumes, sequenced by their own serial
    backlog     the blocking governance violations — the repository's real
                outstanding work, priced by severity rather than by opinion
    agents      the owners the registry declares

The backlog derivation is the one worth stating plainly: work is not invented to
fill a plan, it is what governance found wrong. When the repository has no
blocking violations the backlog is empty, and that is the correct answer rather
than a broken one.

This module also carries the completion gate — ten executable measurements, each
of which either passes against live repository state or names what is missing.
"""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from platform.universal_control_plane.certification import (
    CertificationEngine,
    CertificationSubject,
)
from platform.universal_control_plane.consumption import ConsumptionEngine, default_consumers
from platform.universal_control_plane.durable import (
    EVENT_CERTIFIED,
    EVENT_GOVERNED,
    EVENT_REGISTERED,
    EVENT_TRUTH_DISCOVERED,
    DurableJournal,
)
from platform.universal_control_plane.errors import ControlPlaneError
from platform.universal_control_plane.evolution import EvolutionEngine
from platform.universal_control_plane.execution import (
    AssignmentEngine,
    Schedule,
    SchedulerEngine,
)
from platform.universal_control_plane.governance import GovernanceEngine, GovernanceSubject
from platform.universal_control_plane.intelligence import (
    DashboardEngine,
    MetricsEngine,
    ProgressEngine,
)
from platform.universal_control_plane.linkage import LinkageEngine
from platform.universal_control_plane.manifest import ControlPlaneManifest, default_manifest
from platform.universal_control_plane.ontology import (
    DIMENSION_CERTIFICATION,
    DIMENSION_GOVERNANCE,
    LIFECYCLE_ACTIVE,
    LIFECYCLE_DRAFT,
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    VERSION_ARTIFACT,
    VERSION_IMPLEMENTATION,
    AgentRecord,
    BacklogItem,
    Goal,
    Milestone,
    Objective,
    Universe,
    Vision,
)
from platform.universal_control_plane.plan import BacklogEngine, PlanEngine, RoadmapEngine
from platform.universal_control_plane.prompt import PromptEngine
from platform.universal_control_plane.registration import RegistrationEngine
from platform.universal_control_plane.registry import AgentRegistry
from platform.universal_control_plane.state import StateEngine
from platform.universal_control_plane.trace import (
    DecisionEngine,
    DeterminationEngine,
    EvidenceEngine,
    HistoryEngine,
    ReplayEngine,
)
from platform.universal_control_plane.truth import RepositoryTruthEngine
from platform.universal_control_plane.version import VersionEngine
from typing import Any

#: The control-plane objects Wave 8 requires to be registered. Measured against
#: what registration actually discovered, never asserted.
REQUIRED_ENGINES: tuple[str, ...] = (
    "AssignmentEngine",
    "CertificationEngine",
    "DashboardEngine",
    "DecisionEngine",
    "EvidenceEngine",
    "EvolutionEngine",
    "GovernanceEngine",
    "HistoryEngine",
    "MetricsEngine",
    "PlanEngine",
    "ProgressEngine",
    "PromptEngine",
    "ReplayEngine",
    "RepositoryTruthEngine",
    "RoadmapEngine",
    "SchedulerEngine",
    "StateEngine",
    "VersionEngine",
)

#: Names whose presence anywhere in the package would mean demo-only state
#: survived. The gate looks for them rather than trusting that they are gone.
DEMO_MARKERS: tuple[str, ...] = ("_demo_universe", "_demo_data", "_sample_universe")

#: Governance severity → backlog priority. Declared once so the derived backlog's
#: ordering is attributable to the severity that produced it.
_SEVERITY_PRIORITY: Mapping[str, str] = {
    SEVERITY_CRITICAL: PRIORITY_CRITICAL,
    SEVERITY_HIGH: PRIORITY_HIGH,
    SEVERITY_MEDIUM: PRIORITY_MEDIUM,
    SEVERITY_LOW: PRIORITY_LOW,
}

#: Effort units per severity — logical, not temporal (the ontology is clock-free).
_SEVERITY_ESTIMATE: Mapping[str, int] = {
    SEVERITY_CRITICAL: 8,
    SEVERITY_HIGH: 5,
    SEVERITY_MEDIUM: 3,
    SEVERITY_LOW: 1,
}


@dataclass(frozen=True, slots=True)
class GateCriterion:
    """One executable completion measurement."""

    criterion_id: str
    passed: bool
    measured: str
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "passed": self.passed,
            "measured": self.measured,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class CompletionReport:
    """The ten-criterion completion gate, evaluated against live state."""

    universe_id: str
    truth_id: str
    criteria: tuple[GateCriterion, ...]

    @property
    def complete(self) -> bool:
        return bool(self.criteria) and all(c.passed for c in self.criteria)

    @property
    def failures(self) -> tuple[str, ...]:
        return tuple(c.criterion_id for c in self.criteria if not c.passed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report": "CompletionReport",
            "universe_id": self.universe_id,
            "truth_id": self.truth_id,
            "complete": self.complete,
            "passed": sum(1 for c in self.criteria if c.passed),
            "total": len(self.criteria),
            "failures": list(self.failures),
            "criteria": [c.to_dict() for c in self.criteria],
        }


@dataclass
class ControlPlane:
    """The composed Universal Control Plane, derived from repository state."""

    manifest: ControlPlaneManifest
    truth: RepositoryTruthEngine
    tick: int = 0

    state: StateEngine = field(default_factory=StateEngine)
    registration: RegistrationEngine = field(default_factory=RegistrationEngine)
    governance: GovernanceEngine = field(default_factory=GovernanceEngine)
    certification: CertificationEngine = field(default_factory=CertificationEngine)
    version: VersionEngine = field(default_factory=VersionEngine)
    evolution: EvolutionEngine = field(default_factory=EvolutionEngine)
    linkage: LinkageEngine = field(default_factory=LinkageEngine)
    consumption: ConsumptionEngine = field(default_factory=ConsumptionEngine)

    plan: PlanEngine = field(default_factory=PlanEngine)
    roadmap: RoadmapEngine = field(default_factory=RoadmapEngine)
    backlog: BacklogEngine = field(default_factory=BacklogEngine)
    agents: AgentRegistry = field(default_factory=AgentRegistry)
    assignments: AssignmentEngine = field(default_factory=AssignmentEngine)
    scheduler: SchedulerEngine = field(default_factory=SchedulerEngine)

    prompts: PromptEngine = field(default_factory=PromptEngine)
    progress: ProgressEngine = field(default_factory=ProgressEngine)
    metrics: MetricsEngine = field(default_factory=MetricsEngine)
    dashboards: DashboardEngine = field(default_factory=DashboardEngine)

    determinations: DeterminationEngine = field(default_factory=DeterminationEngine)
    decisions: DecisionEngine = field(default_factory=DecisionEngine)
    history: HistoryEngine = field(default_factory=HistoryEngine)
    replays: ReplayEngine = field(default_factory=ReplayEngine)
    evidence: EvidenceEngine = field(default_factory=EvidenceEngine)

    journal: DurableJournal | None = None

    # -- construction ----------------------------------------------------

    @classmethod
    def discover(
        cls,
        *,
        manifest: ControlPlaneManifest | None = None,
        truth: RepositoryTruthEngine | None = None,
        data_dir: Path | str | None = None,
        repository_root: Path | str | None = None,
        journal_root: Path | str | None = None,
        tick: int = 0,
    ) -> ControlPlane:
        """Discover a fully wired control plane from repository state.

        Supplying *truth* skips rediscovery — the seam a replay or a test uses to
        drive the identical composition over a known snapshot.
        """
        resolved = manifest or default_manifest()
        engine = truth or RepositoryTruthEngine.discover(
            manifest=resolved, data_dir=data_dir, repository_root=repository_root
        )
        plane = cls(manifest=resolved, truth=engine, tick=tick)
        plane.governance = GovernanceEngine(
            manifest=resolved,
            state_engine=plane.state,
            determination_engine=plane.determinations,
            evidence_engine=plane.evidence,
            history_engine=plane.history,
        )
        plane.certification = CertificationEngine(
            manifest=resolved, evidence_engine=plane.evidence, history_engine=plane.history
        )
        plane.registration = RegistrationEngine(manifest=resolved)
        plane.linkage = LinkageEngine(manifest=resolved)
        if journal_root is not None:
            plane.journal = DurableJournal.open(journal_root, manifest=resolved)
        plane.compose()
        return plane

    # -- composition -----------------------------------------------------

    def compose(self) -> ControlPlane:
        """Derive every control-plane object from discovered Repository Truth."""
        self.registration.register_all(tick=self.tick)
        self._derive_agents()
        self._derive_plan()
        self._derive_roadmap()
        self._resolve_governance()
        self._assess_certification()
        self._register_versions()
        self._observe_evolution()
        self._derive_backlog()
        self._measure_progress()
        self._close_linkage()
        self.consumption.register_all(default_consumers())
        self._journal_state()
        return self

    # -- universe --------------------------------------------------------

    def universe(self) -> Universe:
        """The control plane's own universe, declared rather than invented."""
        return Universe(
            universe_id=self.manifest.universe_id,
            name=self.manifest.universe_name,
            description=self.manifest.universe_description,
            state=LIFECYCLE_ACTIVE,
            version=self.manifest.version,
            attributes={"manifest_id": self.manifest.manifest_id},
            tick=self.tick,
        )

    # -- derivation ------------------------------------------------------

    def _derive_agents(self) -> None:
        """Agents are the owners the registry declares, not personas."""
        artifacts = self.truth.artifacts(tick=self.tick)
        owners: dict[str, set[str]] = {}
        for artifact in artifacts:
            if artifact.owner:
                owners.setdefault(artifact.owner, set()).update(artifact.classes or ("artifact",))
        for owner_id in sorted(owners):
            self.agents.register(
                AgentRecord(
                    agent_id=owner_id,
                    name=owner_id,
                    kind="CUSTODIAN",
                    capabilities=tuple(sorted(owners[owner_id])),
                    state=LIFECYCLE_ACTIVE,
                    tick=self.tick,
                )
            )
        # The universe itself is the agent of its own engines.
        if self.manifest.universe_id not in owners:
            self.agents.register(
                AgentRecord(
                    agent_id=self.manifest.universe_id,
                    name=self.manifest.universe_name,
                    kind="AUTONOMOUS",
                    capabilities=tuple(r.layer for r in self.registration.registrations()),
                    state=LIFECYCLE_ACTIVE,
                    tick=self.tick,
                )
            )

    def _derive_plan(self) -> None:
        """Vision from the manifest; goals from programmes; objectives from categories."""
        vision_id = f"VIS-{self.manifest.universe_id}"
        self.plan.register_vision(
            Vision(
                vision_id=vision_id,
                universe_id=self.manifest.universe_id,
                statement=self.manifest.vision_statement,
                state=LIFECYCLE_ACTIVE,
                tick=self.tick,
            )
        )
        by_program: dict[str, set[str]] = {}
        for artifact in self.truth.artifacts(tick=self.tick):
            program = artifact.program or "UNPROGRAMMED"
            by_program.setdefault(program, set()).add(artifact.category or "UNCATEGORISED")
        for program in sorted(by_program):
            goal_id = f"GOAL-{program}"
            self.plan.register_goal(
                Goal(
                    goal_id=goal_id,
                    vision_id=vision_id,
                    title=f"Programme {program}",
                    description=f"every artifact the registry attributes to programme {program}",
                    priority=PRIORITY_MEDIUM,
                    state=LIFECYCLE_ACTIVE,
                    tick=self.tick,
                )
            )
            for category in sorted(by_program[program]):
                self.plan.register_objective(
                    Objective(
                        objective_id=f"OBJ-{program}-{category}",
                        goal_id=goal_id,
                        title=f"{program}/{category}",
                        success_criteria=(
                            f"every {category} artifact in programme {program} is governed "
                            "and certified"
                        ),
                        priority=PRIORITY_MEDIUM,
                        state=LIFECYCLE_ACTIVE,
                        tick=self.tick,
                    )
                )

    def _derive_roadmap(self) -> None:
        """Milestones are the registry volumes, sequenced by their own serial."""
        volumes: dict[str, set[str]] = {}
        for artifact in self.truth.artifacts(tick=self.tick):
            if artifact.volume:
                volumes.setdefault(artifact.volume, set()).add(artifact.artifact_id)
        for volume_id in sorted(volumes):
            self.roadmap.register(
                Milestone(
                    milestone_id=volume_id,
                    universe_id=self.manifest.universe_id,
                    title=f"Volume {volume_id}",
                    description=f"{len(volumes[volume_id])} registered artifacts",
                    sequence=_volume_sequence(volume_id),
                    state=LIFECYCLE_ACTIVE,
                    tick=self.tick,
                )
            )

    def _resolve_governance(self) -> None:
        """Govern every discovered artifact and every registered engine alike."""
        subjects = [
            GovernanceSubject.from_artifact(a) for a in self.truth.artifacts(tick=self.tick)
        ]
        for record in self.registration.registrations():
            truth_class, eligible = self.truth.classify(_module_locator(record.module))
            subjects.append(
                GovernanceSubject(
                    subject_id=record.subject_id,
                    kind=record.subject_kind,
                    owner=record.owner_id,
                    registered=True,
                    version=str(record.attributes.get("version", "1.0.0")),
                    canonical_home=eligible,
                    evidence_ids=(record.identity, *record.lineage),
                    lifecycle_state=LIFECYCLE_ACTIVE,
                    facts={"layer": record.layer, "truth_class": truth_class},
                )
            )
        self.governance.resolve_all(subjects, tick=self.tick)

    def _assess_certification(self) -> None:
        versions = {a.artifact_id: a.version for a in self.truth.artifacts(tick=self.tick)}
        versions.update(
            {
                r.subject_id: str(r.attributes.get("version", "1.0.0"))
                for r in self.registration.registrations()
            }
        )
        subjects = [
            CertificationSubject.from_governance(
                record, version=versions.get(record.subject_id, "")
            )
            for record in sorted(
                (*self.governance.governed(), *self.governance.not_governed()),
                key=lambda r: r.subject_id,
            )
        ]
        self.certification.assess_all(subjects, tick=self.tick)

    def _register_versions(self) -> None:
        """Version every artifact and every engine, in their own dimensions."""
        self.version.ingest(
            ((a.artifact_id, a.version) for a in self.truth.artifacts(tick=self.tick)),
            kind=VERSION_ARTIFACT,
            digests={a.artifact_id: a.content_digest for a in self.truth.artifacts(tick=self.tick)},
            tick=self.tick,
        )
        self.version.ingest(
            (
                (r.subject_id, str(r.attributes.get("version", "1.0.0")))
                for r in self.registration.registrations()
            ),
            kind=VERSION_IMPLEMENTATION,
            tick=self.tick,
        )

    def _observe_evolution(self) -> None:
        """Observe the governance and certification dimensions of every subject."""
        self.evolution.observe_snapshot(
            DIMENSION_GOVERNANCE,
            {
                r.subject_id: r.status
                for r in (*self.governance.governed(), *self.governance.not_governed())
            },
            tick=self.tick,
        )
        self.evolution.observe_snapshot(
            DIMENSION_CERTIFICATION,
            {
                s.subject_id: s.status
                for s in (*self.certification.certified(), *self.certification.not_certified())
            },
            tick=self.tick,
        )

    def _derive_backlog(self) -> None:
        """The backlog is what governance found wrong, priced by severity."""
        for violation in self.governance.violations():
            self.backlog.add(
                BacklogItem(
                    item_id=violation.violation_id,
                    universe_id=self.manifest.universe_id,
                    title=f"{violation.rule_id} on {violation.subject_id}",
                    description=violation.message,
                    priority=_SEVERITY_PRIORITY.get(violation.severity, PRIORITY_LOW),
                    milestone_id=_milestone_for(self, violation.subject_id),
                    objective_id="",
                    state=LIFECYCLE_DRAFT,
                    estimate=_SEVERITY_ESTIMATE.get(violation.severity, 1),
                    attributes={"rule_id": violation.rule_id, "severity": violation.severity},
                    tick=self.tick,
                )
            )

    def _measure_progress(self) -> None:
        governed = len(self.governance.governed())
        total = self.governance.count()
        self.progress.measure_counts(
            self.manifest.universe_id, total=total, completed=governed, tick=self.tick
        )
        universe_id = self.manifest.universe_id
        self.metrics.record(
            universe_id, "artifacts.discovered", float(len(self.truth.artifacts())), tick=self.tick
        )
        self.metrics.record(
            universe_id, "engines.registered", float(self.registration.count()), tick=self.tick
        )
        self.metrics.record(
            self.manifest.universe_id, "governance.governed", float(governed), tick=self.tick
        )
        self.metrics.record(
            self.manifest.universe_id,
            "certification.certified",
            float(len(self.certification.certified())),
            tick=self.tick,
        )
        self.metrics.record(
            self.manifest.universe_id, "backlog.items", float(self.backlog.count()), tick=self.tick
        )

    def _close_linkage(self) -> None:
        """Bind every registered engine to all nine constitutional dimensions."""
        universe = self.universe()
        for record in self.registration.registrations():
            subject_id = record.subject_id
            governance = self.governance.state_of(subject_id)
            certification = self.certification.state_of(subject_id)
            versions = self.version.lineage(subject_id, kind=VERSION_IMPLEMENTATION)
            self.linkage.link(
                subject_id,
                {
                    "constitution": universe.identity,
                    "ontology": record.lineage[1] if len(record.lineage) > 1 else "",
                    "registry": record.capability_id,
                    "runtime": record.identity,
                    "governance": governance.identity,
                    "certification": certification.identity,
                    "replay": self.evolution.changes(subject_id)[0].identity
                    if self.evolution.changes(subject_id)
                    else "",
                    "version": versions[-1].version_id if versions else "",
                    "evidence": governance.evidence_ids[0] if governance.evidence_ids else "",
                },
                tick=self.tick,
            )

    def _journal_state(self) -> None:
        """Persist the composed state to the durable journal, when one is open."""
        if self.journal is None:
            return
        self.journal.append(
            self.manifest.universe_id,
            EVENT_TRUTH_DISCOVERED,
            {"truth_id": self.truth.truth(tick=self.tick).truth_id},
            tick=self.tick,
        )
        self.journal.record_all(EVENT_REGISTERED, self.registration.registrations(), tick=self.tick)
        for record in self.registration.registrations():
            self.journal.append_record(
                EVENT_GOVERNED, self.governance.state_of(record.subject_id), tick=self.tick
            )
            self.journal.append_record(
                EVENT_CERTIFIED, self.certification.state_of(record.subject_id), tick=self.tick
            )

    # -- services --------------------------------------------------------

    def schedule(self) -> Schedule:
        """Schedule the derived backlog across the discovered agents."""
        return self.scheduler.schedule(
            self.backlog.ready(),
            self.registration.dependency_registry,
            self.agents,
            tick=self.tick,
        )

    def dashboard(self) -> dict[str, Any]:
        """The unified dashboard snapshot over live, derived state."""
        return self.dashboards.snapshot(
            plan_dict=self.plan.to_dict(),
            roadmap_dict=self.roadmap.to_dict(),
            backlog_dict=self.backlog.to_dict(),
            schedule_dict=self.schedule().to_dict(),
            assignment_dict=self.assignments.to_dict(),
            progress_dict=self.progress.to_dict(),
            metrics_dict=self.metrics.to_dict(),
            registry_dicts=[
                self.registration.capability_registry.to_dict(),
                self.registration.ownership_registry.to_dict(),
                self.registration.dependency_registry.to_dict(),
                self.agents.to_dict(),
            ],
            tick=self.tick,
        )

    def consume(self) -> tuple[Any, ...]:
        """Run every bound consumer and return the measured consumption records."""
        return self.consumption.invoke_all(self, tick=self.tick)

    # -- the completion gate ---------------------------------------------

    def completion(self) -> CompletionReport:
        """Evaluate all ten completion criteria against live state."""
        truth = self.truth.truth(tick=self.tick)
        counts = truth.counts()

        criteria: list[GateCriterion] = [
            GateCriterion(
                "repository-truth-operational",
                counts["artifacts"] > 0 and counts["capabilities"] > 0,
                f"{counts['artifacts']} artifacts, {counts['capabilities']} capabilities, "
                f"{counts['dependencies']} dependencies from "
                f"{sum(1 for s in truth.sources if s.available)} available sources",
            ),
            GateCriterion(
                "governance-operational",
                self.governance.count() > 0,
                f"{self.governance.count()} objects resolved, "
                f"{len(self.governance.governed())} governed, "
                f"{len(self.governance.violations())} violations recorded",
            ),
            GateCriterion(
                "certification-operational",
                self.certification.count() > 0,
                f"{self.certification.count()} assessed, "
                f"{len(self.certification.certified())} certified, "
                f"{len(self.certification.ineligible())} ineligible",
            ),
            GateCriterion(
                "version-operational",
                self.version.count() > 0 and self._versions_replay(),
                f"{self.version.count()} version records across "
                f"{len(self.version.subjects())} subjects; every lineage replays",
            ),
            GateCriterion(
                "evolution-operational",
                self.evolution.count() > 0 and self.evolution.verify(),
                f"{self.evolution.count()} changes over "
                f"{len(self.evolution.dimensions())} dimensions; replay verified",
            ),
            self._runtime_discovery_criterion(),
            self._durable_replay_criterion(),
            self._registration_criterion(),
            GateCriterion(
                "consumption-operational",
                self.consumption.operational(),
                f"{len(self.consumption.consumed_by())}/"
                f"{len(self.consumption.consumers())} domains consumed "
                f"({self.consumption.invocation_count()} invocations)",
                ""
                if self.consumption.operational()
                else "run ControlPlane.consume() before measuring consumption",
            ),
            self._no_demo_state_criterion(),
        ]
        return CompletionReport(
            universe_id=self.manifest.universe_id,
            truth_id=truth.truth_id,
            criteria=tuple(criteria),
        )

    def _versions_replay(self) -> bool:
        for subject in self.version.subjects():
            for kind in self.version.kinds_for(subject):
                self.version.replay(subject, kind=kind)
        return True

    def _runtime_discovery_criterion(self) -> GateCriterion:
        plan = self.plan.to_dict()
        derived = {
            "goals": plan["goals"],
            "objectives": plan["objectives"],
            "milestones": self.roadmap.count(),
            "agents": self.agents.count(),
            "backlog": self.backlog.count(),
        }
        passed = derived["objectives"] > 0 and derived["milestones"] > 0 and derived["agents"] > 0
        return GateCriterion(
            "runtime-discovery-operational",
            passed,
            ", ".join(f"{value} {name}" for name, value in sorted(derived.items())),
            "" if passed else "the plan, roadmap or agent population derived nothing",
        )

    def _durable_replay_criterion(self) -> GateCriterion:
        if self.journal is None:
            return GateCriterion(
                "durable-replay-operational",
                False,
                "no journal open",
                "open the control plane with journal_root= to make replay durable",
            )
        replayed = self.journal.reconstruct()
        expected = len(self.registration.registrations())
        passed = (
            self.journal.verify()
            and len(replayed.registrations) == expected
            and len(replayed.governance) == expected
            and len(replayed.certifications) == expected
        )
        return GateCriterion(
            "durable-replay-operational",
            passed,
            f"{self.journal.count()} chained entries reconstruct "
            f"{replayed.counts()['registrations']} registrations, "
            f"{replayed.counts()['governance']} governance and "
            f"{replayed.counts()['certifications']} certification states",
        )

    def _registration_criterion(self) -> GateCriterion:
        missing = tuple(
            name for name in REQUIRED_ENGINES if not self.registration.is_registered(name)
        )
        return GateCriterion(
            "registration-operational",
            not missing and self.registration.count() >= len(REQUIRED_ENGINES),
            f"{self.registration.count()} engines registered across "
            f"{len(self.registration.layers())} layers; "
            f"{len(REQUIRED_ENGINES) - len(missing)}/{len(REQUIRED_ENGINES)} required present",
            f"missing: {', '.join(missing)}" if missing else "",
        )

    def _no_demo_state_criterion(self) -> GateCriterion:
        found = demo_markers_present()
        return GateCriterion(
            "no-demo-state",
            not found,
            f"{len(DEMO_MARKERS)} demo markers searched across the package",
            f"found: {', '.join(found)}" if found else "",
        )

    # -- projection ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        plan = self.plan.to_dict()
        return {
            "control_plane": self.manifest.universe_id,
            "universe": self.universe().to_dict(),
            "truth": self.truth.to_dict(tick=self.tick),
            "registration": self.registration.to_dict()["counts"],
            "governance": self.governance.to_dict()["counts"],
            "certification": self.certification.to_dict()["counts"],
            "version": self.version.to_dict()["counts"],
            "evolution": self.evolution.to_dict()["counts"],
            "linkage": self.linkage.to_dict()["counts"],
            "consumption": self.consumption.to_dict()["counts"],
            "plan": {
                "goals": plan["goals"],
                "objectives": plan["objectives"],
                "milestones": self.roadmap.count(),
                "backlog": self.backlog.count(),
                "agents": self.agents.count(),
            },
        }


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _volume_sequence(volume_id: str) -> int:
    """The numeric serial embedded in a volume identifier, or 0 when it has none."""
    digits = "".join(ch for ch in volume_id if ch.isdigit())
    return int(digits) if digits else 0


def _module_locator(module: str) -> str:
    """The repository locator of a dotted module path."""
    return module.replace(".", "/")


def _milestone_for(plane: ControlPlane, subject_id: str) -> str:
    """The volume a violation's subject belongs to, when the subject is an artifact."""
    try:
        return plane.truth.artifact(subject_id, tick=plane.tick).volume
    except ControlPlaneError:
        return ""


def demo_markers_present(package: str = "platform.universal_control_plane") -> tuple[str, ...]:
    """Search *package* for any surviving demo-only construct.

    Executable rather than asserted: the gate imports every module and looks for
    the markers by name, so deleting the demo and re-adding it later fails the
    gate rather than passing on a stale claim.
    """
    import pkgutil

    root = importlib.import_module(package)
    found: set[str] = set()
    for info in pkgutil.iter_modules(root.__path__):
        module = importlib.import_module(f"{package}.{info.name}")
        for marker in DEMO_MARKERS:
            attribute = getattr(module, marker, None)
            if attribute is not None and (
                inspect.isfunction(attribute) or inspect.isclass(attribute)
            ):
                found.add(f"{module.__name__}.{marker}")
    return tuple(sorted(found))


__all__ = [
    "DEMO_MARKERS",
    "REQUIRED_ENGINES",
    "CompletionReport",
    "ControlPlane",
    "GateCriterion",
    "demo_markers_present",
]
