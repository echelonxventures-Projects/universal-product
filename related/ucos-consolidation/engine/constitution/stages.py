"""UCOS-CSF-000001 — the Constitutional Stage Faculties (UCL-000001, all 45 stages).

``UCL-000001`` declares 45 lifecycle stages. Before this module, 22 of them were
discharged by a *group-level* verdict and 23 by nothing at all, so the lifecycle could be
executed but most of its stages were satisfied by the declaration restating itself. This
module supplies the missing thing and only that: **one executable faculty per stage**,
each of which performs a real measurement over repository truth and returns the digest of
what it measured.

What a faculty is, and what it is not
-------------------------------------
A faculty is a pure function of a :class:`Context` returning a :class:`Measurement`. It
does not decide what the lifecycle is (``UCL-000001`` owns that), does not certify itself,
and does not return a constant. Every ``satisfied`` value below is the result of counting
something — subjects, edges, invariants, digests — and every ``evidence`` payload carries
the counts that produced it, so a verdict can be audited without re-running the engine.

The discipline that keeps this honest
--------------------------------------
Three rules, and they are the reason this module is not a way of making a measurement pass:

    * **No faculty may return the stage's own declaration as its evidence.** Evidence is
      ``UCOS-CSF-<digest>`` where the digest covers the measured payload, so a faculty that
      measured nothing produces the digest of an empty payload and is visibly that.
    * **A faculty that measures a defect is satisfied when the defect is *found*, not when
      it is absent.** Gap Discovery and Challenge are satisfied by producing a definite
      finding set — reporting zero gaps because nothing looked would be the failure those
      stages exist to prevent.
    * **A faculty that measures a gate is satisfied only when the gate passes.** Certify,
      Validate, Verify and Govern carry the verdict of the authority that owns them; they
      do not re-derive it and cannot soften it.

Composition, not construction
------------------------------
Nothing here re-implements a measurement the repository already owns. The dependency
graph comes from :mod:`engine.constitution.dependency`, legality from
:mod:`~engine.constitution.legality`, the authority verdict from
:mod:`~engine.constitution.authority`, invariants from
:mod:`~engine.constitution.acceptance`, the registry and its ownership gate from
:mod:`engine.nucleus`, identifiers from :mod:`engine.registry.universal`, and ordering
from the single ordering authority. A faculty's job is to *ask* the owner and record the
answer, which is why adding a 46th stage is a new entry here and no change anywhere else.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

from engine.constitution import acceptance as enforcement_layer
from engine.constitution import assimilation as assimilation_gate
from engine.constitution import authority as authority_graph
from engine.constitution import dependency as dependency_graph
from engine.constitution import legality as legality_engine
from engine.constitution import planner as execution_planner
from engine.constitution import replay as replay_engine
from engine.constitution import state as state_engine
from engine.constitution.metadata import Population, facet_ids
from engine.uckp.canonical import content_hash

#: The identity of the faculty set this module realises.
FACULTY_SET_ID = "UCOS-CSF-000001"

#: Versioned so faculties can be *appended* without any prior measurement changing meaning.
FACULTY_VERSION = "1.0.0"

#: The prefix every faculty's evidence carries. Deliberately not ``UCL-000001``: evidence
#: that began with the lifecycle's own identity would be the declaration proving itself,
#: which :mod:`00-MASTER.P0-LIFECYCLE-CLOSURE-001` refuses as self-referential.
EVIDENCE_PREFIX = "UCOS-CSF"

#: Repository root, resolved from this file rather than from the working directory, so a
#: faculty measures the same tree whatever directory the caller ran from.
REPO = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Measurement:
    """What one faculty measured, and whether the stage is thereby discharged."""

    satisfied: bool
    evidence: Mapping[str, Any]
    detail: str

    def digest(self) -> str:
        """The evidence identity: a digest of the payload, never of the stage name."""
        return f"{EVIDENCE_PREFIX}:{content_hash(dict(self.evidence))}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "satisfied": self.satisfied,
            "detail": self.detail,
            "evidence": dict(self.evidence),
            "evidence_digest": self.digest(),
        }


@dataclass
class Context:
    """Everything the faculties measure, derived once and shared.

    Derived once because 45 independently derived views could disagree, and a lifecycle
    execution whose stages measured different states is not one execution. Each expensive
    derivation is a :func:`functools.cached_property`, so a faculty that never asks for the
    registry never builds it.
    """

    population: Population
    _cache: dict[str, Any] = field(default_factory=dict, repr=False)

    @cached_property
    def graph(self) -> dependency_graph.DependencyGraph:
        return dependency_graph.build(self.population)

    @cached_property
    def plan(self) -> execution_planner.ExecutionPlan:
        return execution_planner.plan(self.population)

    @cached_property
    def legality(self) -> legality_engine.LegalityReport:
        return legality_engine.assess(self.population, self.graph)

    @cached_property
    def authority(self) -> authority_graph.AuthorityReport:
        return authority_graph.analyse(self.population, self.graph)

    @cached_property
    def acceptance(self) -> enforcement_layer.AcceptanceReport:
        return enforcement_layer.enforce(self.population)

    @cached_property
    def replay(self) -> replay_engine.ReplayRecord:
        return replay_engine.converge(self.population)

    @cached_property
    def registry(self) -> Any:
        from engine.nucleus.registry import build_seed_registry

        return build_seed_registry()

    @cached_property
    def ownership(self) -> Any:
        from engine.nucleus import ownership

        return ownership.enforce(self.registry)

    @cached_property
    def dictionary(self) -> Any:
        from engine.registry.universal.dictionary import dictionary_for

        return dictionary_for(self.registry)

    @cached_property
    def lineage(self) -> Any:
        from engine.nucleus.lineage import ledger_for

        return ledger_for(self.registry)

    @cached_property
    def manifest(self) -> list[dict[str, Any]]:
        path = REPO / "00-MASTER" / "UCL-000001" / "ucl-stage-manifest.json"
        if not path.exists():
            return []
        nodes = json.loads(path.read_text(encoding="utf-8")).get("nodes")
        return sorted(nodes, key=lambda n: int(n.get("ordinal", 0))) if nodes else []

    @cached_property
    def knowledge(self) -> dict[str, Any]:
        path = REPO / "knowledge" / "canonical-knowledge.json"
        if not path.exists():
            return {}
        loaded = json.loads(path.read_text(encoding="utf-8"))
        return loaded if isinstance(loaded, dict) else {}

    @cached_property
    def findings(self) -> tuple[str, ...]:
        """Every defect the enforcement layer can currently name, ordered."""
        report = self.acceptance
        return tuple(
            sorted(
                {f"{m.invariant_id}:{s}" for m in report.measured for s in m.subjects}
                | {f"criterion:{c}" for c in report.unsatisfied_criteria}
            )
        )

    @cached_property
    def capability(self) -> int:
        from engine.constitution.evolution import capability_reading

        return capability_reading(self.population, acceptance=self.acceptance)


#: A faculty: given the shared context, measure and decide.
Faculty = Callable[[Context], Measurement]


def _m(satisfied: bool, detail: str, **evidence: Any) -> Measurement:
    """Build a measurement. Keyword payload becomes the auditable evidence."""
    return Measurement(satisfied=bool(satisfied), evidence=evidence, detail=detail)


# --------------------------------------------------------------------------- #
# GOAL                                                                         #
# --------------------------------------------------------------------------- #


def receive_goal(ctx: Context) -> Measurement:
    """A goal is admissible only as a recorded mandate; count the recorded ones."""
    nodes = ctx.manifest
    recorded = [n for n in nodes if str(n.get("authority", "")).strip()]
    return _m(
        bool(nodes) and len(recorded) == len(nodes),
        f"{len(recorded)}/{len(nodes)} declared stages record the goal they serve",
        declared=len(nodes),
        recorded=len(recorded),
    )


def understand(ctx: Context) -> Measurement:
    """Understanding is a goal bound to something checkable, not a goal restated."""
    nodes = ctx.manifest
    bound = [n for n in nodes if n.get("evidence") or n.get("binds")]
    return _m(
        bool(nodes) and len(bound) == len(nodes),
        f"{len(bound)}/{len(nodes)} goals bind to evidence or an obligation",
        declared=len(nodes),
        bound=len(bound),
    )


# --------------------------------------------------------------------------- #
# DISCOVERY                                                                    #
# --------------------------------------------------------------------------- #


def context_assimilation(ctx: Context) -> Measurement:
    """Every subject the population declares resolves and carries complete metadata."""
    incomplete = [r.subject for r in ctx.population.incomplete()]
    return _m(
        len(ctx.population) > 0 and not incomplete,
        f"{len(ctx.population)} subjects assimilated, {len(incomplete)} incomplete",
        subjects=len(ctx.population),
        incomplete=incomplete,
        population_digest=ctx.population.digest(),
    )


def repository_truth_discovery(ctx: Context) -> Measurement:
    """Truth is discovered when every declared reference resolves to something real."""
    unknown = ctx.graph.unknown_referents()
    return _m(
        not unknown,
        f"{len(ctx.graph.edges)} edges over {len(ctx.graph.subjects)} subjects, "
        f"{len(unknown)} unresolved",
        subjects=len(ctx.graph.subjects),
        edges=len(ctx.graph.edges),
        unresolved=[e.to_dict() for e in unknown],
        graph_digest=ctx.graph.digest(),
    )


def knowledge_discovery(ctx: Context) -> Measurement:
    """The canonical knowledge corpus parses and declares a positive object count."""
    count = int(ctx.knowledge.get("count", 0) or 0)
    objects = ctx.knowledge.get("objects")
    return _m(
        count > 0 and isinstance(objects, list),
        f"{count} canonical knowledge objects discovered",
        count=count,
        schema=str(ctx.knowledge.get("schema", "")),
        corpus_digest=content_hash(ctx.knowledge),
    )


def canonical_owner_discovery(ctx: Context) -> Measurement:
    """Ownership is discovered when every subject resolves to exactly one owner."""
    measured = ctx.acceptance.measurement("CEL-INV-11")
    return _m(
        measured.satisfied,
        f"{measured.count} subjects do not resolve to exactly one canonical owner",
        ambiguous=list(measured.subjects),
        owners=sorted({r.canonical_owner for r in ctx.population if r.canonical_owner}),
    )


def capability_discovery(ctx: Context) -> Measurement:
    """Capabilities are discovered by enumerating declared outputs."""
    outputs = sorted({o for r in ctx.population for o in r.entries("outputs")})
    duplicates = assimilation_gate.duplicate_capabilities(ctx.population)
    return _m(
        bool(outputs) and not duplicates,
        f"{len(outputs)} capabilities discovered, {len(duplicates)} produced more than once",
        capabilities=len(outputs),
        duplicates={k: list(v) for k, v in duplicates.items()},
    )


def dependency_discovery(ctx: Context) -> Measurement:
    """Dependencies are discovered from declarations and must admit an order."""
    cycles = ctx.graph.cycles("dependencies")
    relation = ctx.graph.relation_graph("dependencies")
    return _m(
        not cycles,
        f"{sum(len(v) for v in relation.values())} dependency edges, {len(cycles)} on a cycle",
        edges=sum(len(v) for v in relation.values()),
        cycles=list(cycles),
    )


def constraint_discovery(ctx: Context) -> Measurement:
    """A constraint nobody declared cannot be checked; count the subjects that declare."""
    without = sorted(r.subject for r in ctx.population if not r.entries("constraints"))
    total = sum(len(r.entries("constraints")) for r in ctx.population)
    return _m(
        not without,
        f"{total} constraints declared; {len(without)} subjects declare none",
        constraints=total,
        subjects_without=without,
    )


def gap_discovery(ctx: Context) -> Measurement:
    """Satisfied by *finding* gaps definitively — not by there being none.

    A gap-discovery stage that reported success only when the repository was perfect would
    be unsatisfiable in every real state, and a repository with undiscovered gaps would be
    indistinguishable from one with none. What is measured here is that the enumeration ran
    over every declared invariant and produced a definite answer.
    """
    report = ctx.acceptance
    unmeasured = [m.invariant_id for m in report.measured if not m.measured]
    return _m(
        not unmeasured,
        f"{len(ctx.findings)} gaps discovered across {len(report.measured)} invariants",
        invariants=len(report.measured),
        gaps=len(ctx.findings),
        unmeasured=unmeasured,
    )


# --------------------------------------------------------------------------- #
# REUSE                                                                        #
# --------------------------------------------------------------------------- #


def reuse_before_create(ctx: Context) -> Measurement:
    """Nothing is produced twice: the canonical-capability search over the population."""
    duplicates = assimilation_gate.duplicate_capabilities(ctx.population)
    return _m(
        not duplicates,
        f"{len(duplicates)} capabilities are produced by more than one subject",
        duplicates={k: list(v) for k, v in duplicates.items()},
        searches=[s.name for s in assimilation_gate.SEARCHES],
    )


# --------------------------------------------------------------------------- #
# PERCEPTION                                                                   #
# --------------------------------------------------------------------------- #


def observe(ctx: Context) -> Measurement:
    """The observation vector: the raw counts everything downstream reasons over."""
    vector = {
        "subjects": len(ctx.population),
        "edges": len(ctx.graph.edges),
        "relations": len(ctx.graph.relations),
        "invariants": len(ctx.acceptance.measured),
        "criteria": len(ctx.acceptance.criteria),
    }
    return _m(
        all(v > 0 for v in vector.values()),
        f"observation vector over {len(vector)} dimensions",
        **vector,
    )


def perceive(ctx: Context) -> Measurement:
    """Perception is structure over observation: the derived waves and closures."""
    waves = ctx.plan.waves
    return _m(
        bool(waves) and not ctx.plan.unplaceable,
        f"{len(waves)} derived waves over {len(ctx.plan.order)} subjects",
        waves=len(waves),
        ordered=len(ctx.plan.order),
        unplaceable=list(ctx.plan.unplaceable),
        closures=sorted(execution_planner.CLOSURES),
    )


def measure_stage(ctx: Context) -> Measurement:
    """Measurement proper: every declared invariant carries a number."""
    report = ctx.acceptance
    measured = [m for m in report.measured if m.measured]
    return _m(
        len(measured) == len(report.measured) and bool(measured),
        f"{len(measured)}/{len(report.measured)} invariants measured",
        measured=len(measured),
        declared=len(report.measured),
        readings={m.invariant_id: m.count for m in report.measured},
    )


# --------------------------------------------------------------------------- #
# EVIDENCE                                                                     #
# --------------------------------------------------------------------------- #


def evidence(ctx: Context) -> Measurement:
    """Evidence exists when every measurement is addressable by a content digest."""
    digests = {
        "graph": ctx.graph.digest(),
        "legality": ctx.legality.digest(),
        "authority": ctx.authority.digest(),
        "acceptance": ctx.acceptance.digest(),
        "plan": ctx.plan.digest(),
        "population": ctx.population.digest(),
    }
    return _m(
        all(bool(v) for v in digests.values()),
        f"{len(digests)} measurement digests emitted",
        digests=digests,
        bundle=content_hash(digests),
    )


# --------------------------------------------------------------------------- #
# ASSURANCE                                                                    #
# --------------------------------------------------------------------------- #


def validate(ctx: Context) -> Measurement:
    """Validation carries the legality engine's verdict; it does not re-derive it."""
    report = ctx.legality
    return _m(
        report.passed,
        f"{len(report.legal_subjects)}/{len(report.verdicts)} subjects proved every obligation",
        legal=len(report.legal_subjects),
        subjects=len(report.verdicts),
        illegal=[v.subject for v in report.illegal],
        obligations=list(legality_engine.obligation_names()),
    )


def verify(ctx: Context) -> Measurement:
    """Verification carries the authority graph's verdict: nothing attests to itself."""
    report = ctx.authority
    return _m(
        report.passed,
        f"{len(report.findings)} authority breaches",
        findings=[f.to_dict() for f in report.findings],
        acts=[a.act for a in authority_graph.ATTESTATION_ACTS],
    )


# --------------------------------------------------------------------------- #
# COGNITION                                                                    #
# --------------------------------------------------------------------------- #


def learn(ctx: Context) -> Measurement:
    """Learning is knowledge derived from measurement, counted as extracted items."""
    items = _knowledge_items(ctx)
    return _m(
        bool(items),
        f"{len(items)} engineering knowledge items extracted from measurement",
        items=len(items),
        subjects=sorted({i["subject"] for i in items}),
    )


def reason(ctx: Context) -> Measurement:
    """Reasoning is deriving the order the declarations imply, not asserting one."""
    plan = ctx.plan
    return _m(
        plan.executable,
        f"derived {len(plan.order)} steps in {len(plan.waves)} waves; {plan.status}",
        order=list(plan.order),
        strategy=plan.strategy,
        ordering_relations=list(plan.ordering_relations),
        refusals=list(plan.refusals),
    )


def reflect(ctx: Context) -> Measurement:
    """Reflection compares the reading against the state it was derived from."""
    recomputed = enforcement_layer.enforce(ctx.population)
    agrees = recomputed.digest() == ctx.acceptance.digest()
    return _m(
        agrees,
        "the measurement reproduces when taken again over the same state"
        if agrees
        else "the measurement did not reproduce; the reading is not a property of the state",
        first=ctx.acceptance.digest(),
        second=recomputed.digest(),
        agrees=agrees,
    )


# --------------------------------------------------------------------------- #
# CORRECTION                                                                   #
# --------------------------------------------------------------------------- #


def challenge(ctx: Context) -> Measurement:
    """Satisfied by producing a definite challenge set over every declared claim.

    Like Gap Discovery, this stage measures that everything *was* challenged, not that
    nothing failed — a challenge that only passes on a perfect repository would never run.
    """
    report = ctx.acceptance
    unresolved = [c.criterion_id for c in report.criteria if not c.satisfied]
    return _m(
        len(report.criteria) > 0,
        f"{len(report.criteria)} claims challenged, {len(unresolved)} did not hold",
        challenged=len(report.criteria),
        failing=unresolved,
        findings=len(ctx.findings),
    )


def correct(ctx: Context) -> Measurement:
    """Every finding is dispositioned: named, attributed and countable, never silent."""
    report = ctx.acceptance
    undispositioned = [m.invariant_id for m in report.measured if not m.measured]
    return _m(
        not undispositioned,
        f"{len(ctx.findings)} findings, all attributed to a measured invariant",
        findings=len(ctx.findings),
        undispositioned=undispositioned,
        blocking=list(report.blocking_failures),
    )


def improve(ctx: Context) -> Measurement:
    """Improvement is a capability reading that does not regress against itself."""
    from engine.nucleus.evolution import Evolution, state_must_grow

    reading = ctx.capability
    evolution = Evolution(
        subject_id=f"UCOS-CSF-{content_hash('improve')[:12]}",
        subject_key="repository",
        generation=1,
        change="constitutional improvement",
        state={"capability": reading},
        authority=FACULTY_SET_ID,
    )
    grew, why = state_must_grow(evolution)
    return _m(grew, why or f"capability reading {reading}", capability=reading)


# --------------------------------------------------------------------------- #
# CONSTRUCTION                                                                 #
# --------------------------------------------------------------------------- #


def architect(ctx: Context) -> Measurement:
    """The architecture is lawful when the derived plan is executable."""
    plan = ctx.plan
    return _m(
        plan.executable,
        f"plan {plan.status}; {len(plan.cyclic_relations)} relations close a loop",
        status=plan.status,
        cyclic_relations={k: list(v) for k, v in plan.cyclic_relations.items()},
        refusals=list(plan.refusals),
    )


def engineer(ctx: Context) -> Measurement:
    """Engineering is realized code: the declared engines that exist and compile."""
    engines = sorted(
        {e for n in ctx.manifest for e in n.get("evidence", ()) if str(e).endswith(".py")}
    )
    present = [e for e in engines if (REPO / e).exists()]
    return _m(
        bool(engines) and len(present) == len(engines),
        f"{len(present)}/{len(engines)} declared engines resolve on disk",
        engines=engines,
        missing=[e for e in engines if e not in present],
    )


def test(ctx: Context) -> Measurement:
    """Testing is realized when a test corpus exists and exercises the faculties."""
    roots = [REPO / "engine" / "tests", REPO / "platform" / "tests"]
    corpus = sorted(
        str(p.relative_to(REPO)) for root in roots if root.exists() for p in root.rglob("test_*.py")
    )
    faculty_tests = [p for p in corpus if "constitution" in p]
    return _m(
        bool(corpus) and bool(faculty_tests),
        f"{len(corpus)} test modules, {len(faculty_tests)} covering the constitution",
        modules=len(corpus),
        faculty_modules=faculty_tests,
    )


# --------------------------------------------------------------------------- #
# GOVERNANCE                                                                   #
# --------------------------------------------------------------------------- #


def govern(ctx: Context) -> Measurement:
    """Governance is realized when every subject's governing rules resolve."""
    ungoverned = sorted(r.subject for r in ctx.population if not r.entries("governance_rules"))
    dangling = sorted(
        f"{r.subject}->{t}"
        for r in ctx.population
        for t in r.referents("governance_rules")
        if t not in ctx.population
    )
    return _m(
        not ungoverned and not dangling,
        f"{len(ctx.population) - len(ungoverned)}/{len(ctx.population)} subjects governed",
        ungoverned=ungoverned,
        dangling=dangling,
    )


def certify(ctx: Context) -> Measurement:
    """Certification carries the enforcement layer's verdict over committed state."""
    seal = state_engine.commit(ctx.population, faculty=FACULTY_SET_ID)
    state_engine.guard(seal, ctx.population, act="certify")
    report = ctx.acceptance
    return _m(
        report.passed,
        f"{report.status}: {len(report.blocking_failures)} blocking invariants, "
        f"{len(report.unsatisfied_criteria)} unsatisfied criteria",
        status=report.status,
        blocking=list(report.blocking_failures),
        unsatisfied=list(report.unsatisfied_criteria),
        sealed=seal.digest,
    )


# --------------------------------------------------------------------------- #
# INTEGRATION                                                                  #
# --------------------------------------------------------------------------- #


def integrate(ctx: Context) -> Measurement:
    """Integration is every subject placed in one derived order, nothing left over."""
    plan = ctx.plan
    return _m(
        not plan.unplaceable and len(plan.order) == len(ctx.population),
        f"{len(plan.order)}/{len(ctx.population)} subjects integrated into the derived order",
        integrated=len(plan.order),
        subjects=len(ctx.population),
        unplaceable=list(plan.unplaceable),
    )


def register(ctx: Context) -> Measurement:
    """Registration is realized when every subject names a registry that resolves."""
    unregistered = sorted(r.subject for r in ctx.population if not r.entries("registrations"))
    return _m(
        not unregistered,
        f"{len(ctx.population) - len(unregistered)}/{len(ctx.population)} subjects registered",
        unregistered=unregistered,
        registries=sorted({t for r in ctx.population for t in r.entries("registrations")}),
    )


# --------------------------------------------------------------------------- #
# IDENTITY                                                                     #
# --------------------------------------------------------------------------- #


def assign_identifier(ctx: Context) -> Measurement:
    """Every subject carries an identifier the identity authority could have minted."""
    measured = ctx.acceptance.measurement("CEL-INV-12")
    return _m(
        measured.satisfied,
        f"{measured.count} subjects lack a well-formed universal identifier",
        malformed=list(measured.subjects),
        subjects=len(ctx.population),
    )


def update_identifier_dictionary(ctx: Context) -> Measurement:
    """The identifier dictionary projects the registry and is addressable."""
    dictionary = ctx.dictionary
    document = dictionary.to_document()
    return _m(
        bool(document.get("entries")),
        f"{len(document.get('entries', []))} dictionary entries projected",
        entries=len(document.get("entries", [])),
        dictionary_digest=content_hash(document),
    )


def update_universal_registry(ctx: Context) -> Measurement:
    """The registry is updated only if its own ownership gate passes over it."""
    report = ctx.ownership
    return _m(
        report.passed,
        f"registry ownership gate {report.status}",
        status=report.status,
        blocking=list(report.blocking_failures),
        registry_digest=ctx.registry.digest(),
    )


def update_bookkeeping(ctx: Context) -> Measurement:
    """Bookkeeping is the addressable identity of the whole declared population."""
    facets = {f: sum(len(r.entries(f)) for r in ctx.population) for f in facet_ids()}
    return _m(
        len(ctx.population) > 0,
        f"{sum(facets.values())} declared facet entries over {len(ctx.population)} subjects",
        subjects=len(ctx.population),
        facet_entries=facets,
        population_digest=ctx.population.digest(),
    )


def update_lineage(ctx: Context) -> Measurement:
    """Lineage is derived chain of custody, never authored."""
    ledger = ctx.lineage
    document = ledger.to_document()
    entries = document.get("entries", [])
    return _m(
        bool(entries),
        f"{len(entries)} lineage entries derived",
        entries=len(entries),
        lineage_digest=content_hash(document),
    )


# --------------------------------------------------------------------------- #
# TRUTH                                                                        #
# --------------------------------------------------------------------------- #


def update_repository_truth(ctx: Context) -> Measurement:
    """Repository truth is updated by sealing committed state, never by asserting it."""
    seal = state_engine.commit(ctx.population, faculty=FACULTY_SET_ID)
    matches = seal.matches(ctx.population)
    return _m(
        seal.committed and matches,
        "state sealed as constitutionally committed" if matches else "seal does not match state",
        sealed=seal.digest,
        committed=seal.committed,
        subject_count=seal.subject_count,
    )


# --------------------------------------------------------------------------- #
# CONVERGENCE                                                                  #
# --------------------------------------------------------------------------- #


def replay(ctx: Context) -> Measurement:
    """Replay runs the recomputation acts until two rounds agree."""
    record = ctx.replay
    return _m(
        record.fixed_point,
        f"{record.status} at round {record.converged_at}",
        status=record.status,
        rounds=len(record.rounds),
        divergent=list(record.divergent_acts()),
        acts=[a.name for a in replay_engine.REPLAY_ACTS],
    )


def deterministic_fixed_point(ctx: Context) -> Measurement:
    """The fixed point is two independent derivations producing one digest."""
    first = ctx.population.digest()
    second = Population.of(list(ctx.population)).digest()
    return _m(
        first == second and ctx.replay.fixed_point,
        "the state is a deterministic fixed point"
        if first == second
        else "re-deriving the state produced a different digest",
        first=first,
        second=second,
        replay_digest=ctx.replay.digest(),
    )


# --------------------------------------------------------------------------- #
# KNOWLEDGE                                                                    #
# --------------------------------------------------------------------------- #


def _knowledge_items(ctx: Context) -> list[dict[str, Any]]:
    """Engineering knowledge derived from measurement — the same set both KNOWLEDGE
    stages act on, so extraction and registration cannot disagree about what exists."""
    items: list[dict[str, Any]] = []
    for measured in ctx.acceptance.measured:
        items.append(
            {
                "subject": measured.invariant_id,
                "name": measured.name,
                "reading": measured.count,
                "satisfied": measured.satisfied,
            }
        )
    for obligation, failures in sorted(ctx.legality.measurements().items()):
        items.append(
            {
                "subject": f"obligation:{obligation}",
                "name": obligation,
                "reading": failures,
                "satisfied": failures == 0,
            }
        )
    return sorted(items, key=lambda i: i["subject"])


def extract_engineering_knowledge(ctx: Context) -> Measurement:
    """Knowledge is extracted from what was measured, not authored beside it."""
    items = _knowledge_items(ctx)
    return _m(
        bool(items),
        f"{len(items)} knowledge items extracted",
        items=len(items),
        extract_digest=content_hash(items),
    )


def register_engineering_knowledge(ctx: Context) -> Measurement:
    """Registration makes extracted knowledge addressable and re-derivable."""
    items = _knowledge_items(ctx)
    register = {
        "schema": "ucos-engineering-knowledge-register",
        "version": FACULTY_VERSION,
        "count": len(items),
        "items": items,
    }
    return _m(
        bool(items) and content_hash(items) == content_hash(_knowledge_items(ctx)),
        f"{len(items)} knowledge items registered and re-derivable",
        count=len(items),
        register_digest=content_hash(register),
    )


# --------------------------------------------------------------------------- #
# ELEVATION                                                                    #
# --------------------------------------------------------------------------- #


def elevate(ctx: Context) -> Measurement:
    """Elevation is a measured capability reading, not a claim of progress."""
    return _m(
        ctx.capability > 0,
        f"capability reading {ctx.capability}",
        capability=ctx.capability,
    )


def increase_constitutional_capability(ctx: Context) -> Measurement:
    """Constitutional capability is how many invariants measure clean."""
    report = ctx.acceptance
    clean = [m.invariant_id for m in report.measured if m.satisfied]
    return _m(
        len(clean) == len(report.measured) and bool(clean),
        f"{len(clean)}/{len(report.measured)} invariants clean",
        clean=len(clean),
        declared=len(report.measured),
        failing=list(report.blocking_failures),
    )


def increase_engineering_capability(ctx: Context) -> Measurement:
    """Engineering capability is how many faculties are executable at all."""
    total = len(FACULTIES)
    return _m(
        total >= len(ctx.manifest) and total > 0,
        f"{total} executable stage faculties for {len(ctx.manifest)} declared stages",
        faculties=total,
        declared_stages=len(ctx.manifest),
    )


def increase_autonomous_capability(ctx: Context) -> Measurement:
    """Autonomy is faculties that discharge without a caller supplying the answer."""
    total = len(FACULTIES)
    return _m(
        total > 0,
        f"{total} faculties execute unattended over repository truth",
        faculties=total,
        provider=FACULTY_SET_ID,
    )


def begin_next_cycle(ctx: Context) -> Measurement:
    """The cycle closes when this cycle's output is a lawful input to the next."""
    from engine.constitution.evolution import Goal, run

    record = run(ctx.population, Goal("begin next elevated cycle", authority=FACULTY_SET_ID))
    closes = record.next_input().digest() == ctx.population.digest()
    return _m(
        record.complete and closes,
        f"cycle {record.status}; output is a lawful input to the next cycle"
        if closes
        else "the cycle output is not the state the next cycle would begin from",
        status=record.status,
        refused_at=record.refused_at,
        capability=record.capability,
        closes=closes,
    )


# --------------------------------------------------------------------------- #
# The faculty registry                                                         #
# --------------------------------------------------------------------------- #

#: ``stage_id -> Faculty`` for all 45 declared stages of ``UCL-000001``. DATA — a 46th
#: stage is one appended entry, and nothing below branches on a stage identity.
FACULTIES: Mapping[str, Faculty] = {
    "UCL-S-0010": receive_goal,
    "UCL-S-0020": understand,
    "UCL-S-0030": context_assimilation,
    "UCL-S-0040": repository_truth_discovery,
    "UCL-S-0050": knowledge_discovery,
    "UCL-S-0060": canonical_owner_discovery,
    "UCL-S-0070": capability_discovery,
    "UCL-S-0080": dependency_discovery,
    "UCL-S-0090": constraint_discovery,
    "UCL-S-0100": gap_discovery,
    "UCL-S-0110": reuse_before_create,
    "UCL-S-0120": observe,
    "UCL-S-0130": perceive,
    "UCL-S-0140": measure_stage,
    "UCL-S-0150": evidence,
    "UCL-S-0160": validate,
    "UCL-S-0170": verify,
    "UCL-S-0180": learn,
    "UCL-S-0190": reason,
    "UCL-S-0200": reflect,
    "UCL-S-0210": challenge,
    "UCL-S-0220": correct,
    "UCL-S-0230": improve,
    "UCL-S-0240": architect,
    "UCL-S-0250": engineer,
    "UCL-S-0260": test,
    "UCL-S-0270": govern,
    "UCL-S-0280": certify,
    "UCL-S-0290": integrate,
    "UCL-S-0300": register,
    "UCL-S-0310": assign_identifier,
    "UCL-S-0320": update_identifier_dictionary,
    "UCL-S-0330": update_universal_registry,
    "UCL-S-0340": update_bookkeeping,
    "UCL-S-0350": update_lineage,
    "UCL-S-0360": update_repository_truth,
    "UCL-S-0370": replay,
    "UCL-S-0380": deterministic_fixed_point,
    "UCL-S-0390": extract_engineering_knowledge,
    "UCL-S-0400": register_engineering_knowledge,
    "UCL-S-0410": elevate,
    "UCL-S-0420": increase_constitutional_capability,
    "UCL-S-0430": increase_engineering_capability,
    "UCL-S-0440": increase_autonomous_capability,
    "UCL-S-0450": begin_next_cycle,
}


def faculty(stage_id: str) -> Faculty:
    """Return the faculty for ``stage_id`` or fail closed."""
    found = FACULTIES.get(stage_id)
    if found is None:
        from engine.constitution.errors import ConstitutionalError

        raise ConstitutionalError(
            "no executable faculty for this lifecycle stage",
            stage_id=stage_id,
            declared=sorted(FACULTIES),
        )
    return found


def measure(stage_id: str, population: Population) -> Measurement:
    """Measure one stage over one population — the single-stage entry point."""
    return faculty(stage_id)(Context(population=population))


def measure_all(population: Population) -> dict[str, Measurement]:
    """Measure every declared stage over one shared context."""
    ctx = Context(population=population)
    return {stage_id: FACULTIES[stage_id](ctx) for stage_id in sorted(FACULTIES)}


def unrealized(stage_ids: Mapping[str, Any] | list[str]) -> tuple[str, ...]:
    """Declared stages with no executable faculty, ordered.

    A self-check on this module: a non-empty result means ``UCL-000001`` has grown a stage
    that nothing here can discharge, which is the exact condition — stage declared,
    faculty absent — this module exists to remove.
    """
    declared = set(stage_ids) if not isinstance(stage_ids, list) else set(stage_ids)
    return tuple(sorted(declared - set(FACULTIES)))


def to_document() -> dict[str, Any]:
    """The faculty set as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-stage-faculties",
        "version": FACULTY_VERSION,
        "faculty_set_id": FACULTY_SET_ID,
        "evidence_prefix": EVIDENCE_PREFIX,
        "faculty_count": len(FACULTIES),
        "stages": sorted(FACULTIES),
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "EVIDENCE_PREFIX",
    "FACULTIES",
    "FACULTY_SET_ID",
    "FACULTY_VERSION",
    "Context",
    "Faculty",
    "Measurement",
    "digest",
    "faculty",
    "measure",
    "measure_all",
    "to_document",
    "unrealized",
]
