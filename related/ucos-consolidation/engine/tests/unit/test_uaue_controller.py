"""UAUE-000001 Epoch 4 — the autonomous evolution controller.

Epoch 3 proved eleven functions correct in isolation. What it could not prove is that anything
carries a candidate through all of them: the traversal lived in a test helper, which meant the
*claim* being made — that this repository can evolve an arbitrary subject without being told what
it is — was demonstrated by the test suite rather than by the platform. A capability whose only
implementation is its own test is not a capability.

The properties measured here, and the failure each one closes:

1. **A candidate reaches a certified evolution.** One admitted candidate traverses all eleven
   declared positions, settles, and satisfies every declared validation dimension, verification
   dimension and certification proof — through the controller, with no test-side wiring.
2. **Runs replay.** Two conducted runs of one candidate produce one run identity and one digest,
   through the same number of settlement rounds. Determinism is claimed about the *path*, not only
   the destination, because a run that reached the same place by a different route would make the
   settlement bound unmeasurable.
3. **The unknown subject needs nothing new.** The declared probe and a subject of a class this
   suite invents both traverse the identical code path, produce the identical run shape, and add
   no registry, authority, engine or schema. An unknown object is admitted through the same door
   as everything else or the door is not universal.
4. **Every refusal is a refusal.** Missing identity, missing subject, missing evidence, an
   unresolved dependency, a failed validation, a failed verification, a failed certification and
   an unauthorised execution each drive the controller to refuse — and each for its own named
   reason, so a gate that always passed could not go unnoticed.
5. **The fixed point is a fixed point.** The settlement converges, converges in the same number of
   rounds every time, terminates at its ceiling rather than spinning, and — the property that
   makes it a settlement at all — one more round after convergence changes nothing.
6. **The conductor carries no knowledge of its subject.** The controller source names no phase,
   register, object kind, criterion, candidate class or domain. Measured against the declaration
   rather than asserted, so a literal added tomorrow fails this test.
"""

from __future__ import annotations

import ast
import io
import json
import re
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

import engine.uaue.controller as module
from engine.uaue import controller as controller_module
from engine.uaue import gate as gate_module
from engine.uaue.authority import load_evolution_authority
from engine.uaue.controller import (
    MAX_SETTLEMENT_ROUNDS,
    EvolutionContext,
    EvolutionController,
    EvolutionRefused,
    EvolutionRun,
    resolve_evolution_state,
)
from engine.uaue.gate import (
    FAIL_CLOSED_FLAG,
    MODULE_PATH,
    history_path,
    main,
    measure,
    replay_drift,
)
from engine.uaue.history import query_history, rehydrate_history
from engine.uaue.model import (
    ABSENT,
    Criterion,
    Dependency,
    EvolutionAuthority,
    EvolutionAuthorityError,
    Phase,
)
from engine.uaue.objects import EvolutionCandidate, as_context, derive_identity
from engine.uaue.resolution import (
    DECLARATION_PATH,
    PROGRAMME_HOME,
    REPO_ROOT,
    DeclarationReader,
    Substrate,
)
from engine.uckp.evolution import CYCLE_LENGTH
from engine.uckp.vocabulary import LIFECYCLE_STAGE, Term, build_vocabulary_registry

CONTROLLER_SOURCE = REPO_ROOT / "engine" / "uaue" / "controller.py"
GATE_SOURCE = REPO_ROOT / "engine" / "uaue" / "gate.py"


def declared_gate_obligations() -> set[str]:
    """Every obligation identifier the gate module can construct, read out of the gate itself.

    A literal count is a snapshot of the day it was written. It fails on the one change that
    cannot make a gate weaker — measuring one more obligation — and passes on the change that
    can: quietly measuring one fewer. So the obligation surface is measured rather than
    remembered. Every ``UAUE-GATE-NN`` identifier the gate constructs must appear in the report
    it produces, which closes both directions at once: an obligation dropped from ``measure`` is
    a failure, and so is an obligation function that exists and is never called.
    """

    found: set[str] = set()
    tree = ast.parse(GATE_SOURCE.read_text("utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if re.fullmatch(r"UAUE-GATE-\d{2}", node.value):
                found.add(node.value)
    assert found, "the gate constructs no obligation identifier, so it measures nothing"
    return found


def assert_obligation_surface(identifiers: Sequence[str]) -> None:
    """The measured obligations are exactly the gate's surface, each once, numbered 1..N.

    The contiguity check is what makes a *removal* visible: dropping the seventh obligation and
    renumbering nothing leaves a hole, and dropping the last one shortens the range. Neither is
    detectable by a count that was itself edited to match.
    """
    declared = declared_gate_obligations()
    assert sorted(identifiers) == sorted(
        declared
    ), f"measured {sorted(identifiers)} against the gate's own surface {sorted(declared)}"
    assert len(identifiers) == len(set(identifiers)), f"measured twice: {identifiers}"
    ordinals = sorted(int(entry.rsplit("-", 1)[1]) for entry in identifiers)
    assert ordinals == list(range(1, len(ordinals) + 1)), f"numbering has a hole: {ordinals}"


# --------------------------------------------------------------------------------------
# Fixtures — one context, one controller, one traversal, shared across the suite.
# --------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def context() -> EvolutionContext:
    return EvolutionContext.resolve()


@pytest.fixture(scope="module")
def controller(context: EvolutionContext) -> EvolutionController:
    return EvolutionController(context)


@pytest.fixture(scope="module")
def authority(context: EvolutionContext) -> EvolutionAuthority:
    return context.authority


@pytest.fixture(scope="module")
def discovered(controller: EvolutionController):
    return controller.discover()


@pytest.fixture(scope="module")
def probe(discovered, authority: EvolutionAuthority) -> EvolutionCandidate:
    """The declared unknown subject, as the declared source emitted it."""
    return next(
        entry
        for entry in discovered.candidates
        if entry.subject_identity == authority.unknown_probe.subject
    )


@pytest.fixture(scope="module")
def probe_run(controller: EvolutionController, probe: EvolutionCandidate) -> EvolutionRun:
    return controller.run(probe)


@pytest.fixture(scope="module")
def declaration() -> dict[str, Any]:
    return json.loads((REPO_ROOT / DECLARATION_PATH).read_text("utf-8"))


def _unknown_object(authority: EvolutionAuthority, probe: EvolutionCandidate) -> EvolutionCandidate:
    """A subject of a class nothing in this repository declares — invented by this test.

    Not the declared probe. The declared probe proves the *declaration* can carry an unknown
    subject; this proves the *controller* can, because its class, subject and reason appear in no
    declaration, no registry and no source. It reuses the declared identity rule rather than
    minting an identifier, which is the one thing an unknown object may not bring with it.
    """
    subject = "unknown://no-such-thing/0.0.1"
    reason = "an object this repository has never seen, carried to prove it need not be known"
    head = authority.phase_by_ordinal(1)
    inputs = {
        "candidate_class": "NOT_A_DECLARED_CLASS",
        "subject_identity": subject,
        "reason": reason,
        "authority": dict(probe.context).get("owner", ""),
        "object_kind": authority.object_kind_of(head.identifier).identifier,
    }
    return EvolutionCandidate(
        evolution_id=derive_identity(authority.identity, {k: str(v) for k, v in inputs.items()}),
        subject_identity=subject,
        candidate_class="NOT_A_DECLARED_CLASS",
        source=probe.source,
        owner=probe.owner,
        reason=reason,
        previous_state="nothing in this repository models this subject",
        target_state="the subject traverses the loop without the loop knowing what it is",
        context=as_context({**dict(probe.context), "subject_class": "NOT_A_DECLARED_CLASS"}),
        evidence=probe.evidence,
        dependencies=probe.dependencies,
        severity="",
    )


# --------------------------------------------------------------------------------------
# 1. Candidate -> complete lifecycle -> certified evolution
# --------------------------------------------------------------------------------------


def test_a_candidate_traverses_every_declared_position(
    probe_run: EvolutionRun, authority: EvolutionAuthority
) -> None:
    assert len(probe_run.stage_results) == len(authority.phases)
    assert [entry.phase for entry in probe_run.stage_results] == [
        phase.identifier for phase in authority.phases
    ]
    assert [entry.ordinal for entry in probe_run.stage_results] == [
        phase.ordinal for phase in authority.phases
    ]


def test_every_position_produced_its_declared_object_kind(
    probe_run: EvolutionRun, authority: EvolutionAuthority
) -> None:
    for entry in probe_run.stage_results:
        assert entry.object_kind == authority.object_kind_of(entry.phase).identifier
        assert entry.lifecycle_state == authority.stage_of(entry.phase)
        assert entry.evolution_id
        assert entry.digest
        assert entry.evidence


def test_the_run_is_certified_and_refuses_nothing(probe_run: EvolutionRun) -> None:
    assert probe_run.refusals == (), probe_run.refusals
    assert not probe_run.halted
    assert probe_run.certified
    assert probe_run.verdict().startswith("CERTIFIED")


def test_every_declared_criterion_is_measured_and_satisfied(
    probe_run: EvolutionRun, authority: EvolutionAuthority
) -> None:
    for verdict, declared in (
        (probe_run.validation, authority.validations),
        (probe_run.verification, authority.verifications),
        (probe_run.certification, authority.certifications),
    ):
        assert verdict is not None
        assert {entry.identifier for entry in verdict.outcomes} == {
            entry.identifier for entry in declared
        }
        assert verdict.passed, verdict.summary


def test_the_run_carries_a_rehydratable_history_projection(probe_run: EvolutionRun) -> None:
    ledger = rehydrate_history(probe_run.history)
    assert len(ledger) == CYCLE_LENGTH
    recorded = {record.subject for record in ledger.records()}
    assert {obj.evolution_id for obj in probe_run.chain.objects} <= recorded


def test_the_run_identity_is_derived_and_the_run_digests(probe_run: EvolutionRun) -> None:
    assert probe_run.run_id
    assert probe_run.digest()
    assert probe_run.to_dict()["digest"] == probe_run.digest()
    assert probe_run.candidate_identity == probe_run.chain.evolution_id


def test_execution_is_authorisation_and_never_a_mutation(probe_run: EvolutionRun) -> None:
    """``execution_authorized`` and ``mutation_performed`` must remain distinguishable."""
    assert probe_run.execution_authorized is True
    assert probe_run.mutation_performed is False
    assert probe_run.chain.execution is not None
    assert probe_run.chain.execution.mutation_performed is False
    assert dict(probe_run.chain.execution.obj.context)["mutation_performed"] == "false"


# --------------------------------------------------------------------------------------
# 2. Deterministic replay
# --------------------------------------------------------------------------------------


def test_two_executions_of_one_candidate_produce_one_digest(
    controller: EvolutionController, probe: EvolutionCandidate
) -> None:
    first = controller.run(probe)
    second = controller.run(probe)
    assert first.run_id == second.run_id
    assert first.digest() == second.digest()
    assert first.chain.digest() == second.chain.digest()
    assert first.history == second.history


def test_replay_takes_the_same_path_not_merely_the_same_destination(
    controller: EvolutionController, probe: EvolutionCandidate
) -> None:
    first = controller.run(probe).settlement
    second = controller.run(probe).settlement
    assert first is not None and second is not None
    assert first.rounds == second.rounds
    assert first.digests == second.digests


def test_two_controllers_over_one_context_are_indistinguishable(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    """No state accumulates in a controller, so a fresh one must reach the same answer."""
    assert (
        EvolutionController(context).run(probe).digest()
        == EvolutionController(context).run(probe).digest()
    )


def test_the_run_identity_does_not_depend_on_where_the_declaration_was_read_from(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    """A context digest that embedded a filesystem path would make replay a claim about a disk."""
    document = context.to_document()
    assert not any(str(REPO_ROOT) in str(value) for value in document.values())
    assert context.digest() == EvolutionContext.resolve().digest()


def test_the_history_projection_is_deterministic_over_many_runs(
    controller: EvolutionController, probe: EvolutionCandidate
) -> None:
    runs = controller.run_all([probe, probe])
    assert controller.project_history(runs) == controller.project_history(runs)
    # Two cycles, so the append-only ledger's cycle-advance rule is exercised rather than assumed.

    assert rehydrate_history(controller.project_history(runs)).cycles() == 2


# --------------------------------------------------------------------------------------
# 3. Unknown object — no new schema, registry, authority or engine
# --------------------------------------------------------------------------------------


def test_an_object_of_no_declared_class_traverses_the_whole_loop(
    controller: EvolutionController, authority: EvolutionAuthority, probe: EvolutionCandidate
) -> None:
    run = controller.run(_unknown_object(authority, probe))
    assert not run.halted, run.refusals
    assert run.certified, run.refusals
    assert len(run.stage_results) == len(authority.phases)


def test_the_unknown_object_produces_the_same_run_shape_as_a_known_one(
    controller: EvolutionController,
    authority: EvolutionAuthority,
    probe: EvolutionCandidate,
    discovered,
) -> None:
    """The loop's shape must not depend on what the subject is."""
    known = next(
        entry for entry in discovered.candidates if entry.candidate_class != probe.candidate_class
    )
    shapes = {
        tuple((entry.ordinal, entry.phase, entry.object_kind) for entry in run.stage_results)
        for run in (
            controller.run(_unknown_object(authority, probe)),
            controller.run(probe),
            controller.run(known),
        )
    }
    assert len(shapes) == 1


def test_the_unknown_object_needed_no_new_owner_registry_or_schema(
    controller: EvolutionController,
    authority: EvolutionAuthority,
    probe: EvolutionCandidate,
) -> None:
    """Every object of the unknown traversal resolves under an owner that predates this register.

    Measured by requiring each object's authority and dependencies to name only homes the
    declaration already binds and positions the declaration already declares. An object that had
    required something new would have had to name it, and nothing new is nameable here.
    """
    run = controller.run(_unknown_object(authority, probe))
    homes = {entry.home for entry in authority.ownership}
    positions = {phase.identifier for phase in authority.phases}
    for obj in run.chain.objects:
        assert obj.authority
        assert set(obj.dependencies) <= homes | positions
        assert obj.lifecycle_state in {state.name for state in authority.lifecycle_states}
    # No owner home lies inside this programme's own home: nothing was created to serve it.
    assert not [home for home in homes if home.startswith("00-MASTER/UAUE-000001/")]


def test_the_stage_vocabulary_admits_a_term_no_stage_declares(
    authority: EvolutionAuthority,
) -> None:
    """The unknown proof requires an open stage vocabulary, and its owner is not this register.

    The declaration binds this obligation to ``extended_with`` on the Layer Zero vocabulary
    registry (AUE-SYM-05). Measured through that owner rather than restated: if the cycle were a
    closed set, an unknown subject could never occupy a stage nobody had legislated, and the whole
    unknown-evolution claim would be false for a reason no amount of controller code could fix.
    """

    term = authority.unknown_probe.unknown_stage_term
    canonical = {state.name for state in authority.lifecycle_states}
    assert term not in canonical

    vocabulary = build_vocabulary_registry().require(LIFECYCLE_STAGE)
    assert not vocabulary.has(term)
    extended = vocabulary.extended_with(Term(term_id=term, definition="a stage no stage declares"))
    assert extended.has(term)
    # Append-only: the vocabulary that was extended is unchanged, so no digest computed under it
    # has been retroactively invalidated.
    assert not vocabulary.has(term)


# --------------------------------------------------------------------------------------
# 4. Failure cases — each refused, each for its own reason
# --------------------------------------------------------------------------------------


def test_a_candidate_with_no_identity_is_refused_at_admission(
    controller: EvolutionController, probe: EvolutionCandidate
) -> None:
    with pytest.raises(EvolutionRefused, match="anonymous candidate"):
        controller.run(replace(probe, evolution_id=""))


def test_a_candidate_naming_no_subject_is_refused_at_admission(
    controller: EvolutionController, probe: EvolutionCandidate
) -> None:
    with pytest.raises(EvolutionRefused, match="no subject"):
        controller.run(replace(probe, subject_identity="   "))


def test_a_candidate_with_no_resolving_evidence_is_refused_at_admission(
    controller: EvolutionController, probe: EvolutionCandidate
) -> None:
    with pytest.raises(EvolutionRefused, match="no resolving evidence"):
        controller.run(replace(probe, evidence=("no/such/path/at/all.json",)))


def test_an_unresolved_dependency_halts_the_traversal_at_the_authorisation_position(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    """A dependency that does not resolve makes the effect unknown, so nothing may be authorised."""

    class DependencyLost(Substrate):
        """The real tree, with one declared owner home of the loop treated as absent."""

        def __init__(self, missing: str) -> None:
            super().__init__(context.substrate.root)
            self._missing = missing

        def state(self, path: str) -> str:
            return ABSENT if path == self._missing else super().state(path)

    lost = context.authority.phase_by_ordinal(4).homes[0]
    broken = replace(context, substrate=DependencyLost(lost))
    run = EvolutionController(broken).run(probe)
    assert run.halted
    assert not run.certified
    assert any(lost in entry for entry in run.refusals), run.refusals
    assert any("did not authorise an execution" in entry for entry in run.refusals)
    # The halting position still appears in the stage results, carrying no object: a traversal that
    # simply stopped listing positions would be indistinguishable from one that never reached them.
    halting = next(entry for entry in run.stage_results if not entry.discharged)
    assert halting.phase == context.authority.phase_by_ordinal(5).identifier
    assert halting.evolution_id == ""
    assert halting.object_kind == ""
    assert halting.digest == ""
    assert run.execution_authorized is False
    assert run.mutation_performed is False


def test_an_owner_that_refuses_halts_the_traversal_and_names_the_refusal(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    """When a delegated owner refuses, the refusal is recorded on the run, never raised past it.

    An exception escaping the traversal would lose both the position that called the owner and the
    obligation the owner refused on, which is the whole content of the finding.
    """

    composed = context.authority.phase_by_ordinal(3)
    ownerless = replace(composed, owners=())
    assert isinstance(ownerless, Phase)
    phases = tuple(
        ownerless if phase.identifier == composed.identifier else phase
        for phase in context.authority.phases
    )
    broken = replace(context, authority=replace(context.authority, phases=phases))
    run = EvolutionController(broken).run(probe)
    assert run.halted
    assert not run.certified
    assert run.halted_at == composed.identifier
    assert any("no located owner" in entry for entry in run.refusals), run.refusals


def test_a_controller_can_be_resolved_from_repository_truth_alone(
    probe: EvolutionCandidate, context: EvolutionContext
) -> None:
    """The entry point every consumer uses: no arguments, everything read from the declaration."""
    controller = EvolutionController.canonical()
    assert controller.context.digest() == context.digest()
    assert controller.authority.programme_id == context.authority.programme_id
    assert controller.run(probe).digest() == EvolutionController(context).run(probe).digest()


def test_an_unpermitted_execution_path_refuses_the_authorisation(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    """A context that grants no permission over the declared path authorises nothing."""
    ungranted = replace(context, execution_permissions=("engine/uaue/controller.py",))
    run = EvolutionController(ungranted).run(probe)
    assert run.halted
    assert not run.certified
    assert any("grants no permission" in entry for entry in run.refusals), run.refusals


def test_an_unwired_execution_gate_refuses_the_authorisation(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    """Authorisation requires the declared gate to be wired; an unwired gate discharges nothing."""

    class GatesGone(Substrate):
        def make_targets(self) -> frozenset[str]:
            return frozenset()

        def gate_state(self, command: str) -> tuple[bool, str]:
            return False, "no gate is wired in this tree"

    substrate = GatesGone(context.substrate.root)
    unwired = replace(
        context,
        substrate=substrate,
        authority=load_evolution_authority(DeclarationReader.canonical(), substrate),
    )
    run = EvolutionController(unwired).run(probe)
    assert not run.certified
    assert run.refusals


def test_a_failed_validation_refuses_the_run(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    """A blocking validation dimension the declaration names must be able to refuse a run.

    Driven by widening the criterion set with a dimension no engine can measure, which the
    validation owner reports unsatisfied rather than skipping — absence of evidence is never
    evidence.
    """

    invented = Criterion(
        identifier="AUE-VAL-XX",
        subject="a dimension no engine measures",
        obligation="must be unmeasurable",
        blocking=True,
    )
    authority = replace(context.authority, validations=(*context.authority.validations, invented))
    broken = replace(
        context,
        authority=authority,
        validation_policy=(*context.validation_policy, invented.identifier),
    )
    run = EvolutionController(broken).run(probe)
    assert not run.certified
    assert any("validation refused" in entry for entry in run.refusals), run.refusals
    assert run.validation is not None and not run.validation.passed


def test_a_failed_verification_refuses_the_run(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    invented = Criterion(
        identifier="AUE-VER-XX",
        subject="a dimension no engine measures",
        obligation="must be unmeasurable",
        blocking=True,
        bound_gate="",
    )
    authority = replace(
        context.authority, verifications=(*context.authority.verifications, invented)
    )
    broken = replace(
        context,
        authority=authority,
        verification_policy=(*context.verification_policy, invented.identifier),
    )
    run = EvolutionController(broken).run(probe)
    assert not run.certified
    assert any("verification refused" in entry for entry in run.refusals), run.refusals


def test_a_failed_certification_refuses_the_run(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    invented = Criterion(
        identifier="AUE-CER-XX",
        subject="a proof no engine measures",
        obligation="must be unmeasurable",
        blocking=True,
    )
    authority = replace(
        context.authority, certifications=(*context.authority.certifications, invented)
    )
    broken = replace(
        context,
        authority=authority,
        certification_policy=(*context.certification_policy, invented.identifier),
    )
    run = EvolutionController(broken).run(probe)
    assert not run.certified
    assert any("certification refused" in entry for entry in run.refusals), run.refusals


def test_a_context_over_a_position_with_no_owner_is_refused(context: EvolutionContext) -> None:
    """No located owner for the execution position means no execution could ever be authorised."""

    executor = context.authority.phase_by_ordinal(5)
    ownerless = Phase(
        identifier=executor.identifier,
        ordinal=executor.ordinal,
        name=executor.name,
        duty=executor.duty,
        canonical_stages=executor.canonical_stages,
        produces=executor.produces,
        owners=(),
        gate=executor.gate,
        declared_evidence=executor.declared_evidence,
        resolving_evidence=executor.resolving_evidence,
        authority=executor.authority,
        reuse=executor.reuse,
        classification=executor.classification,
    )
    phases = tuple(
        ownerless if phase.identifier == executor.identifier else phase
        for phase in context.authority.phases
    )
    with pytest.raises(EvolutionRefused, match="names no owner"):
        EvolutionContext.resolve(
            authority=replace(context.authority, phases=phases),
            substrate=context.substrate,
        )


def test_a_halted_run_is_excluded_from_the_history_projection(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    """A chain that never reached a position has no record for it, and the ledger refuses a gap."""
    ungranted = replace(context, execution_permissions=())
    halted = EvolutionController(ungranted).run(probe)
    assert halted.halted
    assert halted.history == {}
    assert EvolutionController(ungranted).project_history([halted]) == (
        EvolutionController(ungranted).project_history([])
    )


# --------------------------------------------------------------------------------------
# 5. Fixed point settlement
# --------------------------------------------------------------------------------------


def test_the_settlement_converges(probe_run: EvolutionRun) -> None:
    assert probe_run.settlement is not None
    assert probe_run.settlement.converged
    assert probe_run.settlement.rounds >= 2, "convergence cannot be observed in one round"
    assert probe_run.settlement.rounds <= MAX_SETTLEMENT_ROUNDS
    assert probe_run.settlement.digests[-1] == probe_run.settlement.digests[-2]


def test_the_settlement_is_a_true_fixed_point(
    probe_run: EvolutionRun, context: EvolutionContext
) -> None:
    """Settling an already-settled chain changes nothing — the definition of a fixed point."""
    again = resolve_evolution_state(probe_run.chain, context)
    assert again.converged
    assert again.digests[0] == probe_run.settlement.digests[-1]  # type: ignore[union-attr]
    assert again.rounds == 2, "a settled chain must reproduce its own state on the first round"


def test_the_settlement_terminates_at_its_ceiling_instead_of_spinning(
    probe_run: EvolutionRun, context: EvolutionContext
) -> None:
    """A ceiling below the rounds convergence needs must stop, and must say it did not settle."""
    chain = probe_run.chain.with_verdicts(validation=None, verification=None, certification=None)
    bounded = resolve_evolution_state(chain, context, max_rounds=1)
    assert bounded.rounds == 1
    assert not bounded.converged
    assert bounded.chain is not chain


def test_a_ceiling_below_one_round_is_refused(
    probe_run: EvolutionRun, context: EvolutionContext
) -> None:
    with pytest.raises(EvolutionRefused, match="ceiling below one round"):
        resolve_evolution_state(probe_run.chain, context, max_rounds=0)
    with pytest.raises(EvolutionRefused, match="ceiling below one round"):
        EvolutionContext.resolve(substrate=context.substrate, max_settlement_rounds=0)


def test_the_settlement_round_count_is_deterministic(
    context: EvolutionContext, probe_run: EvolutionRun
) -> None:
    chain = probe_run.chain
    rounds = {resolve_evolution_state(chain, context).rounds for _ in range(3)}
    assert len(rounds) == 1


def test_an_unsettled_run_is_never_certified(
    context: EvolutionContext, probe: EvolutionCandidate
) -> None:
    starved = replace(context, max_settlement_rounds=1)
    run = EvolutionController(starved).run(probe)
    assert run.settlement is not None and not run.settlement.converged
    assert not run.certified
    assert any("did not settle" in entry for entry in run.refusals), run.refusals


# --------------------------------------------------------------------------------------
# 6. The conductor holds no knowledge of what it conducts
# --------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def controller_source() -> str:
    return CONTROLLER_SOURCE.read_text("utf-8")


def test_the_controller_names_no_declared_identifier(
    controller_source: str, declaration: dict[str, Any]
) -> None:
    """Every phase, register, object kind, field, criterion and source id must be absent.

    This is the structural form of "no domain-specific logic". The controller resolves each of
    them from the authority, so a literal appearing here would mean a rename could silently stop
    the loop being conducted while every test still passed.
    """
    leaked: list[str] = []
    for block, key in (
        ("phases", "id"),
        ("object_kinds", "id"),
        ("required_fields", "id"),
        ("validations", "id"),
        ("verifications", "id"),
        ("certifications", "id"),
        ("mandatory", "id"),
        ("discovery_sources", "id"),
        ("discovery_duties", "id"),
        ("classifications", "id"),
        ("registers", "file"),
    ):
        for entry in declaration[block]:
            value = entry[key]
            if value in controller_source:
                leaked.append(f"{block}:{value}")
    assert not leaked, f"the controller enumerates declared values: {leaked}"


def test_the_controller_names_no_candidate_class_and_no_subject(
    controller_source: str, declaration: dict[str, Any], discovered
) -> None:
    leaked = [
        entry["candidate_class"]
        for entry in declaration["discovery_sources"]
        if entry["candidate_class"] in controller_source
    ]
    assert not leaked, f"the controller branches on a candidate class: {leaked}"
    assert declaration["unknown_probe"]["subject"] not in controller_source
    # Structured subject identities only. A bare English word that happens to also be a subject
    # ("execution" is one) proves nothing about enumeration when it appears in prose, whereas a
    # path, URI or dotted identity appearing here could only be a hardcoded subject.
    structured = [
        candidate.subject_identity
        for candidate in discovered.candidates
        if any(mark in candidate.subject_identity for mark in ("/", ":", ".", "-"))
    ]
    assert structured, "the measurement would be vacuous with no structured subject to check"
    assert not [subject for subject in structured if subject in controller_source]


def test_the_controller_names_no_gate_and_no_owner_home(
    controller_source: str, authority: EvolutionAuthority
) -> None:
    """Owners and gates are pointers resolved from the declaration, never literals."""
    leaked = [entry.home for entry in authority.ownership if entry.home in controller_source]
    assert not leaked, f"the controller names an owner home: {leaked}"
    gates = {phase.gate.command for phase in authority.phases if phase.gate.command}
    assert not [gate for gate in gates if gate in controller_source]


def test_the_controller_reuses_the_epoch_three_owners_and_reimplements_none(
    controller_source: str,
) -> None:
    """Every measurement is delegated. A controller that measured would be a second opinion."""
    for owner in (
        "discover_evolution_candidates",
        "understand_evolution",
        "create_evolution_plan",
        "simulate_evolution",
        "execute_evolution",
        "observe_evolution",
        "validate_evolution",
        "verify_evolution",
        "certify_evolution",
        "project_history",
    ):
        assert owner in controller_source, f"{owner} is not reused by the controller"
    # The controller must not become a second identity, ledger or certificate issuer.
    for forbidden in ("class EvolutionLedger", "def derive_identity", "def content_hash"):
        assert forbidden not in controller_source


def test_the_controller_names_no_domain_at_all(controller_source: str) -> None:
    """The conductor must know nothing of any domain, model of reality, vendor or toolchain.

    The mission's own list, measured literally. It is a crude test and that is the point: the
    controller's vocabulary is meant to be exactly six things — evolution object, lifecycle
    position, evidence, dependency, validation, certification — and a word from any domain
    appearing here, even in prose, would mean somebody had started to explain a subject instead of
    conducting it.
    """
    forbidden = (
        "commerce",
        "intelligence",
        "product",
        "earth",
        "mars",
        "universe",
        "technology",
        "vendor",
        "language",
        "platform",
    )
    lowered = controller_source.lower()
    leaked = [word for word in forbidden if word in lowered]
    assert not leaked, f"the controller names a domain: {leaked}"


def test_the_controller_holds_no_module_level_mutable_state() -> None:
    """A conductor with memory could not replay, so there must be nothing to remember."""

    mutable = [
        name
        for name, value in vars(module).items()
        if not name.startswith("__") and isinstance(value, list | dict | set) and name.isupper()
    ]
    assert not mutable, f"module-level mutable state: {mutable}"
    assert not hasattr(EvolutionController, "__dict__") or "_cache" not in dir(EvolutionController)
    assert EvolutionController.__slots__ == ("_context",)


def test_the_controller_writes_nothing(
    controller_source: str, controller: EvolutionController, probe: EvolutionCandidate
) -> None:
    """No write path exists at all, so no bypass of the mutation gateway can originate here."""
    for forbidden in ("write_text", "write_bytes", "open(", "mkdir", "unlink", "subprocess"):
        assert forbidden not in controller_source, forbidden
    run = controller.run(probe)
    assert run.mutation_performed is False


# --------------------------------------------------------------------------------------
# The gate, and the projection it renders
# --------------------------------------------------------------------------------------


def test_the_gate_is_open_over_repository_truth() -> None:
    report = measure()
    assert report.open, [entry.to_dict() for entry in report.failures]
    assert_obligation_surface([entry.identifier for entry in report.obligations])
    assert all(entry.detail for entry in report.obligations)
    assert all(entry.obligation for entry in report.obligations)
    assert report.runs
    assert all(run.certified for run in report.runs)


def test_the_gate_can_close(context: EvolutionContext) -> None:
    """A gate that cannot fail measures nothing. Three obligations driven to CLOSED at once."""

    class NothingResolves(Substrate):
        def state(self, path: str) -> str:
            return ABSENT

        def gate_state(self, command: str) -> tuple[bool, str]:
            return False, "nothing is wired in this tree"

    starved = replace(context, substrate=NothingResolves(context.substrate.root))
    report = measure(starved)
    assert not report.open
    assert {entry.identifier for entry in report.failures} >= {
        "UAUE-GATE-04",
        "UAUE-GATE-05",
        "UAUE-GATE-06",
    }


def test_the_position_obligation_can_close(context: EvolutionContext) -> None:
    """A position whose owner home has vanished must close the gate.

    Measured by rehydrating the authority against a tree in which one declared owner home is
    absent, rather than by editing the authority object: the classification of a position is the
    loader's to determine, and a hand-built authority would be measuring this test's opinion.
    """

    lost = context.authority.phase_by_ordinal(3).homes[0]

    class HomeLost(Substrate):
        def state(self, path: str) -> str:
            return ABSENT if path == lost else super().state(path)

    substrate = HomeLost(context.substrate.root)
    broken = replace(
        context,
        substrate=substrate,
        authority=load_evolution_authority(DeclarationReader.canonical(), substrate),
    )
    report = measure(broken)
    assert not report.open
    failed = {entry.identifier: entry.detail for entry in report.failures}
    assert "UAUE-GATE-02" in failed
    assert lost in failed["UAUE-GATE-02"]


def test_the_repository_verification_path_actually_runs_this_gate(
    context: EvolutionContext,
) -> None:
    """The integration claim, measured against the pipeline file rather than assumed.

    Three positions name a verification entry point as their gate. Before this was measured, the
    wiring check asked only whether that file existed and was executable — which it always was —
    so the gate could report every declared gate wired over a pipeline that had never heard of
    this programme.
    """

    entry_points = {
        context.substrate.entry_point(phase.gate.command) for phase in context.authority.phases
    }
    entry_points.discard(None)
    assert entry_points, "no position names a verification entry point"
    for path in entry_points:
        assert context.substrate.invokes(path, MODULE_PATH), f"{path} does not run {MODULE_PATH}"
        assert context.substrate.invokes(path, FAIL_CLOSED_FLAG), f"{path} ignores the exit status"


def test_the_integration_obligation_closes_when_the_pipeline_does_not_run_the_gate(
    context: EvolutionContext,
) -> None:
    """Measured through the whole gate, because the verdict is what a consumer sees."""

    class PipelineIgnoresThisProgramme(Substrate):
        def invokes(self, path: str, token: str) -> bool:
            return False

    unwired = replace(context, substrate=PipelineIgnoresThisProgramme(context.substrate.root))
    report = measure(unwired)
    assert not report.open
    failed = {entry.identifier: entry.detail for entry in report.failures}
    assert "UAUE-GATE-09" in failed
    assert "verify.sh" in failed["UAUE-GATE-09"]


def test_the_integration_obligation_closes_when_the_pipeline_ignores_the_exit_status(
    context: EvolutionContext,
) -> None:
    """Running the gate and discarding its verdict is a report, not a gate."""

    class PipelineRunsItButNotFailClosed(Substrate):
        def invokes(self, path: str, token: str) -> bool:
            return token != gate_module.FAIL_CLOSED_FLAG

    lenient = replace(context, substrate=PipelineRunsItButNotFailClosed(context.substrate.root))
    obligation = gate_module._integration_obligation(lenient)
    assert not obligation.satisfied
    assert gate_module.FAIL_CLOSED_FLAG in obligation.detail


def test_the_integration_obligation_closes_when_no_entry_point_is_declared(
    context: EvolutionContext,
) -> None:
    """An "every entry point runs this gate" claim over an empty set measures nothing."""

    class NoPipelineIsNamed(Substrate):
        def entry_point(self, command: str) -> str | None:
            return None

    detached = replace(context, substrate=NoPipelineIsNamed(context.substrate.root))
    obligation = gate_module._integration_obligation(detached)
    assert not obligation.satisfied
    assert "no position names a verification entry point" in obligation.detail


def test_the_committed_history_projection_is_a_replay(context: EvolutionContext) -> None:
    """The committed file must be exactly what the declaration produces, byte for byte."""

    report = measure(context)
    assert Path(history_path(context)).is_file()
    assert replay_drift(report) == "", replay_drift(report)


def test_the_committed_history_projection_rehydrates_and_is_queryable(
    context: EvolutionContext,
) -> None:
    document = json.loads(Path(history_path(context)).read_text("utf-8"))
    ledger = rehydrate_history(document)
    assert len(ledger) > 0
    assert not ledger.is_terminated(), "the perpetual cycle has no terminal stage"
    assert document["append_only"] is True
    assert document["schema"] == context.authority.history.schema
    for key in document["queryable_by"]:
        query_history(document, key, "")
    first = ledger.records()[0]
    assert query_history(document, "subject", first.subject)


def test_the_history_projection_is_written_only_inside_the_programme_home(
    context: EvolutionContext,
) -> None:
    target = Path(history_path(context)).resolve()
    home = (Path(context.substrate.root) / "00-MASTER" / context.authority.programme_id).resolve()
    assert target.parent == home
    assert target.name == context.authority.history.file


# --------------------------------------------------------------------------------------
# The gate's command surface — exit status is the only thing a gate is consumed through
# --------------------------------------------------------------------------------------


def test_the_gate_command_exits_zero_when_every_obligation_is_satisfied(capsys) -> None:
    assert main([]) == 0
    assert main(["--gate", "--quiet"]) == 0
    report = capsys.readouterr()
    assert "UAUE gate OPEN" in report.err
    assert report.out == "", "a quiet run must print nothing on stdout"


def test_the_gate_command_emits_a_machine_readable_report(capsys) -> None:
    assert main(["--json", "--quiet"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["gate"] == "uaue-gate"
    assert document["open"] is True
    assert_obligation_surface([entry["id"] for entry in document["obligations"]])
    # Serialised obligations carry the whole record, not a verdict alone: a consumer that can read
    # "satisfied" but not what was satisfied cannot show the gate is non-vacuous.
    for entry in document["obligations"]:
        assert set(entry) == {"id", "obligation", "satisfied", "detail"}, entry
        assert entry["obligation"] and entry["detail"], entry
        assert entry["satisfied"] is True, entry
    # The human summary and the machine body must be counting the same obligations. They are
    # produced by different code paths over one report, so a count that drifted between them
    # would make two published numbers disagree about one measurement.
    total = len(document["obligations"])
    assert document["summary"] == f"UAUE gate OPEN — {total}/{total} obligations satisfied"
    assert document["runs"] and all(entry["certified"] for entry in document["runs"])
    assert all(entry["digest"] for entry in document["runs"])


def test_the_gate_command_exits_non_zero_when_an_obligation_is_refused(
    monkeypatch, context: EvolutionContext
) -> None:
    """The only thing a gate is consumed through is its exit status, so it must be measured."""

    refused = gate_module.GateReport(
        obligations=(
            gate_module.Obligation(
                identifier="UAUE-GATE-01",
                obligation="a refused obligation",
                satisfied=False,
                detail="refused for the purpose of measuring the exit status",
            ),
        ),
        projection={},
        runs=(),
        context=context,
    )
    monkeypatch.setattr(gate_module, "measure", lambda *_, **__: refused)
    assert gate_module.main(["--gate", "--quiet"]) == gate_module.EXIT_CLOSED
    assert refused.summary.startswith("UAUE gate CLOSED")


def test_an_unusable_declaration_is_a_fault_and_never_a_verdict(monkeypatch) -> None:
    """ "The gate is closed" and "I could not tell" are different answers, with different codes."""

    def unusable(*_: Any, **__: Any) -> None:
        raise EvolutionAuthorityError("the declaration is unusable")

    monkeypatch.setattr(gate_module, "measure", unusable)
    assert gate_module.main(["--gate"]) == gate_module.EXIT_FAULT

    def unreadable(*_: Any, **__: Any) -> None:
        raise OSError("the tree is unreadable")

    monkeypatch.setattr(gate_module, "measure", unreadable)
    assert gate_module.main(["--gate"]) == gate_module.EXIT_FAULT


def test_the_render_command_writes_the_projection_and_the_replay_command_checks_it(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    """Render, then replay, then mutate one byte and prove the replay refuses it."""

    target = tmp_path / PROGRAMME_HOME / "UAUE-EVOLUTION-HISTORY.json"
    monkeypatch.setattr(gate_module, "history_path", lambda *_, **__: target)

    assert gate_module.main(["--render"]) == 0
    assert target.is_file()
    assert "projected:" in capsys.readouterr().err
    assert gate_module.main(["--replay", "--quiet"]) == 0

    target.write_text(target.read_text("utf-8").replace("append_only", "append_ONLY", 1))
    assert gate_module.main(["--replay", "--quiet"]) == gate_module.EXIT_CLOSED

    target.unlink()
    assert gate_module.main(["--replay", "--quiet"]) == gate_module.EXIT_CLOSED


def test_a_render_into_an_unwritable_destination_is_a_fault(monkeypatch, tmp_path: Path) -> None:
    blocked = tmp_path / "not-a-directory"
    blocked.write_text("", encoding="utf-8")
    monkeypatch.setattr(gate_module, "history_path", lambda *_, **__: blocked / "history.json")
    assert gate_module.main(["--render", "--quiet"]) == gate_module.EXIT_FAULT


def test_the_replay_check_reports_an_unreadable_projection(
    monkeypatch, tmp_path: Path, context: EvolutionContext
) -> None:
    """An unreadable committed projection is a drift finding, never a silent pass."""

    report = measure(context)
    assert replay_drift(report, tmp_path / "absent.json").startswith("the history projection has")
    unreadable = tmp_path / "unreadable.json"
    unreadable.write_text("{}", encoding="utf-8")
    unreadable.chmod(0o000)
    try:
        assert "unreadable" in replay_drift(report, unreadable)
    finally:
        unreadable.chmod(0o600)


# --------------------------------------------------------------------------------------
# the controller's refusals, which a healthy repository never produces


def test_an_evaluation_that_did_not_settle_halts_before_authorisation(
    controller: EvolutionController, probe: EvolutionCandidate, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Authorisation reads the evaluation's verdict rather than re-deriving it, and an execution
    authorised past an unsettled evaluation would perform an act nobody predicted the impact of.
    The reason is carried through by name so an operator can see WHICH of the three conditions
    withheld the authorisation."""

    real = controller_module.simulate_evolution

    def _unsettled(plan, authority, substrate=None):  # noqa: ANN001, ANN202
        return replace(real(plan, authority, substrate), fixed_point=False)

    monkeypatch.setattr(controller_module, "simulate_evolution", _unsettled)
    run = controller.run(probe)
    assert run.refusals
    assert any("did not settle over the candidate state" in reason for reason in run.refusals)


def test_an_execution_claiming_a_mutation_is_refused_twice_over(
    controller: EvolutionController, probe: EvolutionCandidate, monkeypatch: pytest.MonkeyPatch
) -> None:
    """This controller never performs a mutation, so a record claiming one came from somewhere
    it does not control. Refused at the authorisation position AND again when the run is sealed,
    because the two are different readers and neither may rely on the other having looked."""

    real = controller_module.execute_evolution

    def _claiming(simulation, authority, substrate=None):  # noqa: ANN001, ANN202
        return replace(real(simulation, authority, substrate), mutation_performed=True)

    monkeypatch.setattr(controller_module, "execute_evolution", _claiming)
    run = controller.run(probe)
    assert any("never does and never permits" in reason for reason in run.refusals)
    assert any("which this controller never performs" in reason for reason in run.refusals)


def test_a_history_that_cannot_be_projected_is_a_refusal_and_not_a_crash(
    controller: EvolutionController, probe: EvolutionCandidate, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The run is the unit an operator reads. A projection failure that escaped as an exception
    would take the whole run's record with it, including every refusal already collected."""

    def _unprojectable(chain, authority):  # noqa: ANN001, ANN202
        raise EvolutionAuthorityError("the ledger refused the projection")

    monkeypatch.setattr(controller_module, "project_history", _unprojectable)
    run = controller.run(probe)
    assert any("history could not be projected" in reason for reason in run.refusals)
    assert run.history == {}


# --------------------------------------------------------------------------------------
# the gate's obligations, each shown to refuse
#
# Every one of these holds against the real declaration, so none of the refusal arms had run.
# An obligation that silently stopped measuring would report SATISFIED for ever, and the gate
# would be OPEN on the strength of a check that had stopped asking.


def _obligation(context: EvolutionContext, builder: str):
    return getattr(gate_module, builder)(context)


def test_a_position_with_no_owner_or_an_unwired_gate_is_unresolved(
    context: EvolutionContext,
) -> None:
    """A position with no declared owner answers to nobody, and one whose gate is not wired
    refuses at nothing. Both make the position's later claims unattributable."""
    authority = context.authority
    ownerless = replace(
        authority,
        phases=(replace(authority.phases[0], owners=()), *authority.phases[1:]),
    )
    obligation = _obligation(replace(context, authority=ownerless), "_positions_obligation")
    assert not obligation.satisfied
    assert "no owner is declared" in obligation.detail

    unwired_gate = replace(authority.phases[0].gate, wired=False, detail="not in the Makefile")
    unwired = replace(
        authority,
        phases=(replace(authority.phases[0], gate=unwired_gate), *authority.phases[1:]),
    )
    obligation = _obligation(replace(context, authority=unwired), "_positions_obligation")
    assert not obligation.satisfied
    assert "gate not wired" in obligation.detail


def test_a_stage_claimed_by_nobody_or_by_two_positions_closes_the_stage_obligation(
    context: EvolutionContext,
) -> None:
    """Exactly once is the property. Claimed by nobody is a stage of a governed cycle that is
    ungoverned; claimed twice is a stage with two authorities and no tiebreak."""
    authority = context.authority
    for claimed_by, message in (
        ((), "claimed by no position"),
        (("AUE-P-01", "AUE-P-02"), "claimed by more than one position"),
    ):
        doctored = replace(
            authority,
            lifecycle_states=(
                replace(authority.lifecycle_states[0], claimed_by=claimed_by),
                *authority.lifecycle_states[1:],
            ),
        )
        obligation = _obligation(replace(context, authority=doctored), "_stages_obligation")
        assert not obligation.satisfied
        assert message in obligation.detail


def test_a_backward_or_unresolved_dependency_closes_the_dependency_obligation(
    context: EvolutionContext,
) -> None:
    """A phase edge pointing forwards would let a position depend on one that has not run; a
    home edge naming a path nobody wrote is a dependency on nothing.

    The loader derives phase edges from loop order and refuses a phase whose ordinal disagrees
    with its position, so no declaration can produce the first. Handing the obligation an edge
    set the deriver cannot build is what shows the guard still works if a future deriver could.
    """

    authority = context.authority
    forward = Dependency(
        phase=authority.phases[0].identifier,
        depends_on=authority.phases[-1].identifier,
        kind="phase",
    )
    absent = Dependency(
        phase=authority.phases[0].identifier,
        depends_on="engine/absent/nowhere.py",
        kind="home",
    )
    # A home edge naming a POSITION rather than a path is resolved by the position existing, so
    # it is skipped rather than looked for on disk — otherwise every such edge would report as
    # an unresolved file nobody wrote.
    positional = Dependency(
        phase=authority.phases[0].identifier,
        depends_on=authority.phases[1].identifier,
        kind="home",
    )
    doctored = replace(
        authority, dependencies=(*authority.dependencies, forward, absent, positional)
    )
    obligation = _obligation(replace(context, authority=doctored), "_dependencies_obligation")
    assert not obligation.satisfied
    assert "backward edges" in obligation.detail
    assert "unresolved" in obligation.detail


def test_a_replay_that_does_not_reproduce_the_run_closes_the_replay_obligation(
    controller: EvolutionController, probe: EvolutionCandidate
) -> None:
    """Four separate differences, because they mean different things: a different population, a
    different run digest, a different run identity, and a settlement that took a different
    number of rounds. Collapsing them would report "the replay differs" and say nothing an
    operator could act on."""

    first = controller.run(probe)
    drifted = replace(
        first,
        run_id=f"{first.run_id}x",
        settlement=replace(first.settlement, rounds=first.settlement.rounds + 1),
    )
    obligation = gate_module._replay_obligation((first,), (drifted, drifted))
    assert not obligation.satisfied
    assert "1 runs against 2 on replay" in obligation.detail
    assert "run digest differs" in obligation.detail
    assert "run identity differs" in obligation.detail
    assert "rounds" in obligation.detail


def test_a_run_recording_a_mutation_or_inventing_an_owner_home_closes_the_unknown_obligation(
    context: EvolutionContext, probe_run: EvolutionRun
) -> None:
    """Nothing new was required, and "nothing new" is measured two ways: no mutation was
    performed, and no owner home lies inside this programme's own home. The second is what
    would make the register its own authority."""

    mutating = replace(probe_run, mutation_performed=True)
    obligation = gate_module._unknown_obligation(mutating, context)
    assert not obligation.satisfied
    assert "a mutation was recorded" in obligation.detail

    authority = context.authority
    invented = replace(
        authority,
        ownership=(
            replace(authority.ownership[0], home=f"{PROGRAMME_HOME}/invented.py"),
            *authority.ownership[1:],
        ),
    )
    obligation = gate_module._unknown_obligation(probe_run, replace(context, authority=invented))
    assert not obligation.satisfied
    assert "created inside this programme" in obligation.detail


def test_the_report_names_the_replay_drift_it_found(capsys) -> None:
    """The drift line is the one an operator acts on. A report that computed the drift and did
    not print it would leave the committed projection's disagreement discoverable only by
    running the gate again with different flags."""

    context = EvolutionContext.resolve()
    report = gate_module.measure(context)
    stream = io.StringIO()
    gate_module._print_report(report, "the committed projection disagrees", stream)
    assert "replay drift:" in stream.getvalue()


def test_a_render_the_declaration_refuses_is_a_fault_and_never_a_verdict(monkeypatch) -> None:
    """An IO failure and a declaration failure are different faults on the same command, and
    both must exit FAULT rather than reporting a gate verdict about a surface nobody wrote."""

    def _refusing(*_: Any, **__: Any) -> None:
        raise EvolutionAuthorityError("the surface cannot be rendered")

    monkeypatch.setattr(gate_module, "render_surface", _refusing)
    assert gate_module.main(["--render", "--quiet"]) == gate_module.EXIT_FAULT
