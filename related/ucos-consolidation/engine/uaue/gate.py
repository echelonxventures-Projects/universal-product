"""UAUE — the evolution capability gate (UAUE-000001, Epoch 4).

The gate this register's own final position declares (``make uaue-gate``) and, until Epoch 4,
the one thing in the whole declaration that nothing discharged. That was not a cosmetic gap:
the declaration binds one verification dimension to this gate, so while the target did not
exist the dimension was bound to something nobody ran — and the governance dimension correctly
reported the whole register PARTIALLY_IMPLEMENTED for exactly that reason. A gate that only
existed as a string in a declaration was the register's own most honest finding about itself.

Ten obligations are measured, and each one is the negation of a way this capability could look
present while being absent:

1. **The authority rehydrates.** Every later measurement is a function of it, so a declaration
   that cannot be read makes every other answer unattributable rather than merely unknown.
2. **Every declared position resolves.** A position whose owner home has vanished cannot
   discharge its duty, and a loop with a hole in it is not a loop.
3. **Every canonical stage is owned.** The stage set belongs to the constitutional stage
   authority, not to this register; a stage appended there and claimed by nothing would be an
   ungoverned stage of a governed cycle.
4. **No declared dependency is unresolved.** A dependency that does not resolve makes an
   evaluation unable to predict an effect, which is what forbids authorising an execution.
5. **A traversal replays.** Two conducted runs of one candidate must reach one digest. Without
   this, every other verdict here is an anecdote about one execution.
6. **An unknown subject traverses.** The declared probe — an object in no registry, of no
   declared class, owned by nobody — must reach a settled, certified run without a new
   registry, authority, engine or schema. This is the only obligation that measures the claim
   the whole programme is *for*, and it is measured by conducting it, not by asserting it.
7. **Every mandatory invariant is measured.** The declaration carries ten blocking invariants,
   and until this obligation existed the gate evaluated none of them. A blocking invariant that
   nothing evaluates is of unknown compliance, so an unmeasurable measure closes the gate rather
   than passing it.
8. **The declared surface is producible and reproducible.** Every register the declaration names
   has an implemented renderer, and the bytes it renders carry no memory address, wall clock or
   absolute path. A certification measured in memory and discarded is one nobody can read, and a
   register that only replays on the machine that wrote it proves nothing in CI.
9. **The repository's own verification runs this gate.** Every verification entry point the
   declaration names as a gate must invoke this module fail-closed. Three positions name
   ``./verify.sh``, and while the wiring measurement asked only whether that file exists, the gate
   could report every declared gate wired over a pipeline that had never heard of this programme.
   A gate invoked only by hand discharges nothing.
10. **Every declared exit criterion is measured.** The declaration states fifteen exit criteria,
    one per implementation phase, and for three epochs they were loaded, rendered and evaluated by
    nothing — so the programme's own definition of done was prose that read identically whether it
    held or not. Each criterion now names a measure, the engine computes it, and a measure the
    engine cannot compute closes the gate.

The count is not a constant of this module and nothing should treat it as one: an obligation is
added by adding a measurement, and the surface is read off the gate rather than remembered — see
``declared_gate_obligations`` in ``engine/tests/unit/test_uaue_controller.py``, which requires
every obligation this module constructs to appear in the report exactly once under a contiguous
numbering. A hard-coded count fails on the one change that cannot weaken a gate — adding an
obligation — and passes on the one that can: dropping one.

The gate creates nothing. It rehydrates the declaration through its owner, conducts candidates
through the controller, and projects the history through the append-only ledger that owns it.
The projection it writes is derived truth: ``--render`` regenerates it and ``--replay`` proves
the committed bytes are what the declaration produces, so a hand-edited history is a failure
rather than a fact.

Exit status follows the repository convention, and the distinction is the point: ``1`` means an
obligation was measured and refused, ``2`` means no verdict could be reached at all. Collapsing
them would let an unmeasurable gate pass for a satisfied one.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.uaue.controller import EvolutionContext, EvolutionController, EvolutionRun
from engine.uaue.discovery import DiscoveryReport
from engine.uaue.exits import exit_measures
from engine.uaue.model import PRESENT, EvolutionAuthorityError
from engine.uaue.objects import EvolutionCandidate
from engine.uaue.registers import (
    RENDERERS,
    irreproducible_content,
    mandatory_measures,
    register_path,
    rendered_surface,
)
from engine.uaue.registers import replay_drift as register_drift
from engine.uaue.resolution import PROGRAMME_HOME, DeclarationReader, Substrate
from engine.uckp.canonical import canonical_json

#: Returned when an obligation was measured and refused — the gate is CLOSED.
EXIT_CLOSED = 1

#: Returned when no verdict could be reached, so nothing may be asserted either way.
EXIT_FAULT = 2

#: The flag through which this gate is consumed fail-closed. Named once and read twice — by the
#: CLI that offers it and by the integration obligation that requires the repository's own
#: verification path to use it — so the two cannot disagree about what fail-closed means.
FAIL_CLOSED_FLAG = "--gate"

#: How this gate is invoked: ``python -m <this module>``. Derived from the module's own location
#: rather than written down, because the integration obligation compares it against the text of
#: the repository's verification entry point, and a literal here could be renamed out of step
#: with the module it names — which would leave the obligation measuring a string nothing runs.
MODULE_PATH = f"{__package__}.{Path(__file__).stem}"


@dataclass(frozen=True, slots=True)
class Obligation:
    """One gate obligation, measured.

    ``detail`` is required whether the obligation passed or failed. A gate that explains only
    its failures cannot be shown to be non-vacuous, and a gate nobody can show to be
    non-vacuous is a gate that has always been passing for reasons nobody checked.
    """

    identifier: str
    obligation: str
    satisfied: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "obligation": self.obligation,
            "satisfied": self.satisfied,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class GateReport:
    """Every measured obligation, and the projection the run produced."""

    obligations: tuple[Obligation, ...]
    projection: dict[str, Any]
    runs: tuple[EvolutionRun, ...]
    context: EvolutionContext

    @property
    def failures(self) -> tuple[Obligation, ...]:
        return tuple(entry for entry in self.obligations if not entry.satisfied)

    @property
    def open(self) -> bool:
        return not self.failures

    @property
    def summary(self) -> str:
        satisfied = len(self.obligations) - len(self.failures)
        state = "OPEN" if self.open else "CLOSED"
        return f"UAUE gate {state} — {satisfied}/{len(self.obligations)} obligations satisfied"

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate": "uaue-gate",
            "open": self.open,
            "summary": self.summary,
            "obligations": [entry.to_dict() for entry in self.obligations],
            "runs": [
                {
                    "run_id": run.run_id,
                    "candidate_identity": run.candidate_identity,
                    "subject_identity": run.subject_identity,
                    "candidate_class": run.candidate_class,
                    "certified": run.certified,
                    "halted_at": run.halted_at,
                    "refusals": list(run.refusals),
                    "settlement": run.settlement.to_dict() if run.settlement else None,
                    "digest": run.digest(),
                }
                for run in self.runs
            ],
        }


def history_path(context: EvolutionContext, root: Path | None = None) -> Path:
    """Where the history projection is written.

    The filename is read from the declaration and the directory is this programme's own
    operational home, so the gate cannot write outside the home it owns and cannot write a file
    the declaration did not name.
    """
    base = root if root is not None else context.substrate.root
    return base / PROGRAMME_HOME / context.authority.history.file


def load_context(substrate: Substrate | None = None) -> EvolutionContext:
    """The context the gate conducts against: the canonical declaration and a measured tree."""
    return EvolutionContext.resolve(substrate=substrate, reader=DeclarationReader.canonical())


def _unknown_candidate(
    report: DiscoveryReport, context: EvolutionContext
) -> EvolutionCandidate | None:
    """The declared unknown probe, as discovery emitted it, or ``None`` when it was not emitted.

    Selected by matching the declared probe's own subject rather than by a class name written
    here: a class literal in the gate would be the gate knowing what the unknown subject is,
    which is precisely the knowledge the probe exists to prove is unnecessary.

    Absence returns ``None`` rather than raising, because a probe that was not discovered is a
    *measured* failure of the sixth obligation — the gate must close on it and name it, not abort
    with no verdict. Aborting is reserved for a declaration that cannot be read at all.
    """
    subject = context.authority.unknown_probe.subject
    for candidate in report.candidates:
        if candidate.subject_identity == subject:
            return candidate
    return None


def _authority_obligation(context: EvolutionContext) -> Obligation:
    authority = context.authority
    return Obligation(
        identifier="UAUE-GATE-01",
        obligation="the canonical evolution declaration rehydrates into a usable authority",
        satisfied=True,
        detail=(
            f"{authority.programme_id} v{authority.version}: "
            f"{len(authority.classifications)} classifications, "
            f"{len(authority.registers)} registers, {len(authority.phases)} positions, "
            f"{len(authority.lifecycle_states)} stages, "
            f"{len(authority.dependencies)} dependency edges, "
            f"{len(authority.ownership)} owner homes, "
            f"{len(authority.object_kinds)} object kinds, "
            f"{len(authority.required_fields)} mandated fields; "
            f"digest {authority.digest()[:12]}"
        ),
    )


def _positions_obligation(context: EvolutionContext) -> Obligation:
    authority = context.authority
    unresolved: list[str] = []
    for phase in authority.phases:
        if not phase.owners:
            unresolved.append(f"{phase.identifier}: no owner is declared")
            continue
        absent = [owner.home for owner in phase.owners if not owner.resolves]
        if absent:
            unresolved.append(f"{phase.identifier}: {', '.join(absent)}")
        if phase.missing_symbols:
            unresolved.append(f"{phase.identifier}: unbound {', '.join(phase.missing_symbols)}")
        if not phase.gate.wired:
            unresolved.append(f"{phase.identifier}: gate not wired ({phase.gate.detail})")
    return Obligation(
        identifier="UAUE-GATE-02",
        obligation=(
            "every declared position of the loop resolves to an owner that exists, "
            "binds the symbols it is read through, and names a wired gate"
        ),
        satisfied=not unresolved,
        detail=(
            "; ".join(unresolved)
            if unresolved
            else (
                f"all {len(authority.phases)} positions resolve with their symbols "
                "and every declared gate is wired"
            )
        ),
    )


def _stages_obligation(context: EvolutionContext) -> Obligation:
    authority = context.authority
    unowned = [state.name for state in authority.lifecycle_states if not state.claimed_by]
    contested = [state.name for state in authority.lifecycle_states if len(state.claimed_by) > 1]
    problems: list[str] = []
    if unowned:
        problems.append(f"claimed by no position: {unowned}")
    if contested:
        problems.append(f"claimed by more than one position: {contested}")
    return Obligation(
        identifier="UAUE-GATE-03",
        obligation=(
            "every canonical stage of the perpetual cycle is claimed by exactly one position, "
            "so no stage of a governed cycle is ungoverned and none has two authorities"
        ),
        satisfied=not problems,
        detail=(
            "; ".join(problems)
            if problems
            else (
                f"all {len(authority.lifecycle_states)} canonical stages of "
                f"{authority.stage_authority_home} are claimed exactly once"
            )
        ),
    )


def _dependencies_obligation(context: EvolutionContext) -> Obligation:
    authority = context.authority
    positions = {phase.identifier for phase in authority.phases}
    ordinals = {phase.identifier: phase.ordinal for phase in authority.phases}
    unresolved: list[str] = []
    backward: list[str] = []
    for edge in authority.dependencies:
        if edge.kind == "phase":
            if ordinals[edge.depends_on] >= ordinals[edge.phase]:
                backward.append(f"{edge.phase}->{edge.depends_on}")
            continue
        if edge.depends_on in positions:
            continue
        if context.substrate.state(edge.depends_on) != PRESENT:
            unresolved.append(f"{edge.phase}->{edge.depends_on}")
    problems: list[str] = []
    if unresolved:
        problems.append(f"unresolved: {sorted(set(unresolved))}")
    if backward:
        problems.append(f"backward edges: {sorted(set(backward))}")
    return Obligation(
        identifier="UAUE-GATE-04",
        obligation=(
            "every declared dependency resolves in the measured tree and every position "
            "dependency points at an earlier position, so the loop is orderable"
        ),
        satisfied=not problems,
        detail=(
            "; ".join(problems)
            if problems
            else f"all {len(authority.dependencies)} dependency edges resolve and run forward"
        ),
    )


def _replay_obligation(runs: Sequence[EvolutionRun], replays: Sequence[EvolutionRun]) -> Obligation:
    """Two conducted traversals of the same candidates must be indistinguishable."""
    differences: list[str] = []
    if not runs:
        # Non-vacuity. A replay measurement over nothing replays perfectly and proves nothing, so
        # an empty candidate set is a failure of this obligation rather than a trivial pass.
        differences.append("no candidate was conducted, so nothing was replayed")
    if len(runs) != len(replays):
        differences.append(f"{len(runs)} runs against {len(replays)} on replay")
    for first, second in zip(runs, replays, strict=False):
        if first.digest() != second.digest():
            differences.append(f"{first.candidate_identity}: run digest differs")
        if first.run_id != second.run_id:
            differences.append(f"{first.candidate_identity}: run identity differs")
        first_rounds = first.settlement.rounds if first.settlement else -1
        second_rounds = second.settlement.rounds if second.settlement else -1
        if first_rounds != second_rounds:
            differences.append(
                f"{first.candidate_identity}: settled in {first_rounds} rounds, "
                f"then in {second_rounds}"
            )
    rounds = sorted({run.settlement.rounds if run.settlement else 0 for run in runs})
    return Obligation(
        identifier="UAUE-GATE-05",
        obligation=(
            "conducting the same candidates twice produces byte-identical runs, "
            "identical run identities and the same number of settlement rounds"
        ),
        satisfied=not differences,
        detail=(
            "; ".join(differences)
            if differences
            else (
                f"{len(runs)} runs replay byte-identically, "
                f"every one settling within {rounds} rounds"
            )
        ),
    )


def _unknown_obligation(run: EvolutionRun | None, context: EvolutionContext) -> Obligation:
    """The unknown subject must traverse every position and settle, requiring nothing new."""
    probe = context.authority.unknown_probe
    obligation = (
        "the declared unknown subject traverses every position of the loop to a settled, "
        f"certified run, requiring none of: {', '.join(probe.must_not_require)}"
    )
    if run is None:
        return Obligation(
            identifier="UAUE-GATE-06",
            obligation=obligation,
            satisfied=False,
            detail=(
                f"the declared unknown subject {probe.subject} was not discovered, "
                "so the claim that an unknown object can evolve is unmeasured"
            ),
        )
    problems: list[str] = []
    if run.halted:
        problems.append(f"halted at {run.halted_at}: {'; '.join(run.refusals)}")
    if len(run.stage_results) != len(context.authority.phases):
        problems.append(
            f"traversed {len(run.stage_results)} of {len(context.authority.phases)} positions"
        )
    if not run.certified:
        problems.append(f"not certified: {'; '.join(run.refusals)}")
    if run.settlement is None or not run.settlement.converged:
        problems.append("the state did not settle")
    if run.mutation_performed:
        problems.append("a mutation was recorded")
    # Nothing new was required: every object of the traversal resolves under an owner that
    # exists independently of this programme, and no owner home lies inside its own home.
    own = f"{PROGRAMME_HOME}/"
    invented = sorted(
        {
            home
            for home in (entry.home for entry in context.authority.ownership)
            if home.startswith(own)
        }
    )
    if invented:
        problems.append(f"an owner home was created inside this programme: {invented}")
    return Obligation(
        identifier="UAUE-GATE-06",
        obligation=obligation,
        satisfied=not problems,
        detail=(
            "; ".join(problems)
            if problems
            else (
                f"{probe.subject} traversed {len(run.stage_results)} positions and settled in "
                f"{run.settlement.rounds if run.settlement else 0} rounds under "
                f"{len(context.authority.ownership)} pre-existing owner homes"
            )
        ),
    )


def _mandatory_obligation(
    report_runs: Sequence[EvolutionRun],
    context: EvolutionContext,
    measures: Mapping[str, int],
) -> Obligation:
    """Every declared mandatory invariant, measured against its declared expectation.

    The declaration carries ten blocking invariants — zero anonymous evolution objects, zero
    unmanaged changes, zero missing history, evidence, validation, verification or certification,
    zero duplicate authorities, zero lifecycle bypasses, zero uncontrolled mutations — and until
    this obligation existed the gate measured none of them. A blocking invariant that nothing
    evaluates is of unknown compliance and must never be presumed satisfied, so an unmeasurable
    measure closes the gate rather than passing it.
    """
    authority = context.authority
    unmet: list[str] = []
    for entry in authority.mandatory:
        measured = measures.get(entry.measure)
        if measured is None:
            unmet.append(f"{entry.identifier}: measure '{entry.measure}' was not computed")
            continue
        if measured != entry.expect:
            unmet.append(
                f"{entry.identifier} ({entry.invariant}): "
                f"expected {entry.expect}, measured {measured}"
            )
    return Obligation(
        identifier="UAUE-GATE-07",
        obligation=(
            "every declared mandatory invariant is measured and equals its declared "
            "expectation, so no blocking invariant is presumed satisfied without evaluation"
        ),
        satisfied=not unmet,
        detail=(
            "; ".join(unmet)
            if unmet
            else (
                f"all {len(authority.mandatory)} mandatory invariants measured and satisfied "
                f"over {sum(len(run.chain.objects) for run in report_runs)} evolution objects "
                f"in {len(report_runs)} runs"
            )
        ),
    )


def _surface_obligation(context: EvolutionContext, report: GateReport) -> Obligation:
    """Every declared register has an implemented renderer and reproduces elsewhere.

    A declared register with no renderer is the defect this epoch closed: the declaration named
    eighteen registers and fourteen renderers, and nothing produced any of them, so every
    certification proof was measured in memory and discarded. The obligation is measured by
    rendering, not by checking a name against a list — and the rendered bytes are then scanned
    for content that could not reproduce on another process or another machine, because a
    register surface that only replays where it was written proves nothing in CI.
    """
    authority = context.authority
    problems = [
        f"{register.file}: renderer {register.renderer!r} is not implemented"
        for register in authority.registers
        if register.renderer not in RENDERERS
    ]
    if not problems:
        problems.extend(irreproducible_content(report))
    return Obligation(
        identifier="UAUE-GATE-08",
        obligation=(
            "every register the declaration names has an implemented renderer and renders "
            "bytes that reproduce on any process and any machine, so the certification "
            "surface is producible and replayable rather than merely declared"
        ),
        satisfied=not problems,
        detail=(
            "; ".join(problems)
            if problems
            else (
                f"all {len(authority.registers)} declared registers render through "
                f"{len({register.renderer for register in authority.registers})} implemented "
                "renderers, carrying no memory address, wall clock or absolute path"
            )
        ),
    )


def _integration_obligation(context: EvolutionContext) -> Obligation:
    """Every verification entry point this declaration names as a gate must run this gate.

    The defect this closes was the programme's most honest finding about itself. Three positions
    name ``./verify.sh`` as the gate that closes them, and the wiring measurement asked only
    whether that file exists and is executable — which it always did. So the gate reported "every
    declared gate is wired" while nothing in the repository's verification pipeline had ever heard
    of this programme: the capability was fail-closed, deterministic, green, and invoked only by
    hand. A gate that exists and is never run discharges nothing, and a position bound to it is
    ungated in every sense that matters.

    The measurement is textual and deliberately narrow. A *path*-form gate is a pipeline this
    declaration is claiming discharges one of its positions, so it must invoke this module, and it
    must do so through the fail-closed flag — an entry point that ran the gate and ignored its
    exit status would be a report, not a gate. A ``make <target>`` gate is not measured here: those
    belong to other owners, and requiring another owner's target to invoke this programme would be
    this register legislating over homes it does not own.
    """
    substrate = context.substrate
    declared = [substrate.entry_point(phase.gate.command) for phase in context.authority.phases]
    entry_points = sorted({path for path in declared if path is not None})
    gated_positions = sum(1 for path in declared if path is not None)
    problems: list[str] = []
    if not entry_points:
        # Non-vacuity. With no entry point declared, an "every entry point runs this gate" claim
        # is satisfied by an empty set and measures nothing, so it is a refusal instead: the
        # positions that name a pipeline are the ones whose gate this obligation exists to check.
        problems.append(
            "no position names a verification entry point, so nothing measures whether the "
            "repository's own pipeline runs this gate"
        )
    for path in entry_points:
        if not substrate.invokes(path, MODULE_PATH):
            problems.append(f"{path} does not invoke {MODULE_PATH}")
        elif not substrate.invokes(path, FAIL_CLOSED_FLAG):
            problems.append(
                f"{path} invokes {MODULE_PATH} but not through {FAIL_CLOSED_FLAG}, "
                "so a refused obligation would not fail the pipeline"
            )
    return Obligation(
        identifier="UAUE-GATE-09",
        obligation=(
            "every verification entry point this declaration names as a gate invokes this "
            f"gate through {FAIL_CLOSED_FLAG}, so the positions bound to it are closed by "
            "something that measures them rather than by a file that merely exists"
        ),
        satisfied=not problems,
        detail=(
            "; ".join(problems)
            if problems
            else (
                f"{', '.join(entry_points)} invokes {MODULE_PATH} {FAIL_CLOSED_FLAG}, "
                f"gating the {gated_positions} positions that name it"
            )
        ),
    )


def _exit_criteria_obligation(context: EvolutionContext, measures: Mapping[str, int]) -> Obligation:
    """Every declared exit criterion, measured against its declared expectation.

    The declaration states fifteen exit criteria, one per implementation phase, and each names the
    condition under which that phase may be called complete. For three epochs they were loaded,
    rendered into the capability matrix, and evaluated by nothing — so the programme's own
    definition of done was a column of prose that read identically whether it held or not. That is
    the defect the repository refuses by rule: an unmeasured obligation is of unknown compliance
    and may not be presumed satisfied.

    Measured exactly as the mandatory invariants are: the declaration names a measure, the engine
    computes it, and a measure the engine cannot compute closes the gate rather than passing it.
    """
    authority = context.authority
    unmet: list[str] = []
    for entry in authority.exit_criteria:
        measured = measures.get(entry.measure)
        if measured is None:
            unmet.append(f"{entry.identifier}: measure '{entry.measure}' was not computed")
            continue
        if measured != entry.expect:
            unmet.append(
                f"{entry.identifier} ({entry.criterion}): "
                f"expected {entry.expect}, measured {measured}"
            )
    phases = {entry.phase for entry in authority.exit_criteria}
    return Obligation(
        identifier="UAUE-GATE-10",
        obligation=(
            "every declared exit criterion of every implementation phase is measured and equals "
            "its declared expectation, so the programme's own definition of completion is "
            "evaluated rather than asserted"
        ),
        satisfied=not unmet,
        detail=(
            "; ".join(unmet)
            if unmet
            else (
                f"all {len(authority.exit_criteria)} exit criteria across "
                f"{len(phases)} implementation phases measured and satisfied"
            )
        ),
    )


def measure(context: EvolutionContext | None = None) -> GateReport:
    """Measure every gate obligation and produce the history projection.

    Args:
        context: the context to conduct against. Resolved from the canonical declaration and the
            tree this package lives in when omitted.

    Returns:
        A :class:`GateReport`. Deterministic: two calls over one tree return equal reports and
        equal projections, which is the property obligation five measures from the inside.
    """
    context = context if context is not None else load_context()
    controller = EvolutionController(context)

    discovered = controller.discover()
    probe = _unknown_candidate(discovered, context)

    # The probe is conducted first when it exists: it is the subject that proves the loop needs no
    # knowledge of what it carries, so a gate that skipped it would be measuring only the
    # candidates the repository happens to have produced today.
    subjects: list[EvolutionCandidate] = [] if probe is None else [probe]
    subjects.extend(
        candidate
        for candidate in discovered.candidates
        if probe is None or candidate.evolution_id != probe.evolution_id
    )
    runs = controller.run_all(subjects)
    replays = controller.run_all(subjects)
    probe_run = runs[0] if probe is not None and runs else None

    obligations = (
        _authority_obligation(context),
        _positions_obligation(context),
        _stages_obligation(context),
        _dependencies_obligation(context),
        _replay_obligation(runs, replays),
        _unknown_obligation(probe_run, context),
    )
    report = GateReport(
        obligations=obligations,
        projection=controller.project_history(runs),
        runs=tuple(runs),
        context=context,
    )
    # The last three obligations are measured against the completed report because two of them are
    # functions of the runs it carries: the invariants are counted over every conducted object, and
    # the surface obligation is measured by actually rendering every declared register rather than
    # by comparing renderer names to a list. The integration obligation is ordered with them so the
    # report reads outward — the declaration, the loop, the runs, then the repository the whole
    # thing is wired into.
    measures = mandatory_measures(report)
    return GateReport(
        obligations=obligations
        + (
            _mandatory_obligation(report.runs, context, measures),
            _surface_obligation(context, report),
            _integration_obligation(context),
            _exit_criteria_obligation(context, exit_measures(report)),
        ),
        projection=report.projection,
        runs=report.runs,
        context=context,
    )


def render(report: GateReport, destination: Path | None = None) -> Path:
    """Write the history projection to the declared file.

    The write is a projection and never a truth: the bytes are the deterministic product of the
    declaration and the measured tree, and :func:`replay_drift` proves it by regenerating them.
    """
    target = destination if destination is not None else history_path(report.context)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(canonical_json(report.projection) + "\n", encoding="utf-8")
    return target


def render_registers(report: GateReport, root: Path | None = None) -> tuple[Path, ...]:
    """Write every declared register. Returns the written paths in declared order.

    The rendering belongs to :mod:`engine.uaue.registers` and the writing belongs here, because
    this package holds exactly one writing module: the question "what may UAUE mutate, and where"
    has to have one answer, and a renderer that wrote its own file would make the answer a survey
    of eighteen call sites.

    Every register the declaration names is written or nothing is. The whole surface is rendered
    before the first path is touched, so a declaration naming an unimplemented renderer fails
    with no file written rather than after twelve — a surface that wrote sixteen of eighteen and
    reported success would leave two registers carrying the previous run's measurements.
    """
    surface = rendered_surface(report)
    written: list[Path] = []
    for file, body in surface.items():
        target = register_path(report.context, file, root)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        written.append(target)
    return tuple(written)


def render_surface(report: GateReport, root: Path | None = None) -> tuple[Path, ...]:
    """Write the history projection and every declared register.

    The whole declared surface, in one call, because the two halves are projections of one
    measurement: rendering the history without the registers is what left every certification
    proof measured and unreadable, and rendering the registers without the history would leave
    the append-only ledger they summarise behind.
    """
    destination = (
        None if root is None else root / PROGRAMME_HOME / report.context.authority.history.file
    )
    written = [render(report, destination)]
    written.extend(render_registers(report, root))
    return tuple(written)


def replay_drift(report: GateReport, destination: Path | None = None) -> str:
    """Empty when the committed projection and every committed register replay exactly.

    Returns a description of the drift otherwise. Committed files are compared as bytes rather
    than as parsed documents, because a projection that only matches after normalisation is a
    projection whose canonical form nobody is holding to.

    The register surface is included here rather than measured separately so that one command
    answers one question: is what is committed the product of the declaration. A gate that
    proved the history replayed while eighteen registers drifted would be measuring the smaller
    half of its own output.
    """
    target = destination if destination is not None else history_path(report.context)
    problems: list[str] = []
    if not target.is_file():
        problems.append(f"the history projection has not been rendered: {target}")
    else:
        expected = canonical_json(report.projection) + "\n"
        try:
            actual = target.read_text(encoding="utf-8")
        except OSError as error:
            problems.append(f"the committed history projection is unreadable: {error}")
        else:
            if actual != expected:
                problems.append(
                    "the committed history projection is not the product of the declaration "
                    f"({len(actual)} bytes committed, {len(expected)} bytes projected)"
                )
    problems.extend(register_drift(report))
    return "; ".join(problems)


def _print_report(report: GateReport, drift: str, stream: Any) -> None:
    def emit(line: str = "") -> None:
        print(line, file=stream)

    emit("=========================================================")
    emit("UAUE-000001 — Autonomous Universal Evolution Gate")
    emit("=========================================================")
    for entry in report.obligations:
        mark = "PASS" if entry.satisfied else "FAIL"
        emit(f"  [{mark}] {entry.identifier} — {entry.obligation}")
        emit(f"         {entry.detail}")
    certified = sum(1 for run in report.runs if run.certified)
    emit()
    emit(f"  runs conducted:  {len(report.runs)}")
    emit(f"  runs certified:  {certified}")
    ledger = report.projection.get("ledger", {})
    records = ledger.get("records", []) if isinstance(ledger, dict) else []
    emit(f"  history records: {len(records)}")
    if drift:
        emit(f"  replay drift:    {drift}")
    emit()
    emit(f"  {report.summary}")
    emit("=========================================================")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. 0 when the gate is OPEN, 1 when CLOSED, 2 on a fault."""
    parser = argparse.ArgumentParser(
        prog="uaue-gate",
        description=(
            "UAUE-000001 — measure the autonomous universal evolution capability against "
            "repository truth and project the evolution history."
        ),
    )
    parser.add_argument(
        FAIL_CLOSED_FLAG,
        action="store_true",
        dest="gate",
        help="fail-closed: exit non-zero while any obligation is unsatisfied",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="write the declared history projection and every declared register",
    )
    parser.add_argument(
        "--replay",
        action="store_true",
        help="fail-closed: exit non-zero if the committed projection is not a replay",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    parser.add_argument("--quiet", action="store_true", help="suppress the human-readable report")
    args = parser.parse_args(argv)

    try:
        report = measure()
    except EvolutionAuthorityError as error:
        print(f"uaue gate fault: {error}", file=sys.stderr)
        return EXIT_FAULT
    except OSError as error:
        print(f"uaue gate io fault: {error}", file=sys.stderr)
        return EXIT_FAULT

    written: tuple[Path, ...] = ()
    if args.render:
        try:
            written = render_surface(report)
        except OSError as error:
            print(f"uaue gate io fault: {error}", file=sys.stderr)
            return EXIT_FAULT
        except EvolutionAuthorityError as error:
            print(f"uaue gate fault: {error}", file=sys.stderr)
            return EXIT_FAULT

    drift = "" if args.render else replay_drift(report)

    if not args.quiet:
        _print_report(report, drift if args.replay else "", sys.stderr)
        for path in written:
            print(f"  projected: {path}", file=sys.stderr)

    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))

    if args.replay and drift:
        print(f"UAUE-000001 REPLAY DRIFT — {drift}", file=sys.stderr)
        return EXIT_CLOSED
    if args.gate and not report.open:
        for entry in report.failures:
            print(f"UAUE GATE CLOSED — {entry.identifier}: {entry.detail}", file=sys.stderr)
        return EXIT_CLOSED
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "EXIT_CLOSED",
    "EXIT_FAULT",
    "GateReport",
    "Obligation",
    "history_path",
    "load_context",
    "main",
    "measure",
    "render",
    "render_registers",
    "render_surface",
    "replay_drift",
]
