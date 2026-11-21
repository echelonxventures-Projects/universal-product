"""UCOS-NUC-001 — the lifecycle as infrastructure, the lineage ledger, evolution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.nucleus import lifecycle, lineage
from engine.nucleus.errors import EvolutionError, LifecycleError, NucleusError
from engine.nucleus.evolution import (
    Evolution,
    EvolutionLedger,
    always_valid,
    context_is_declared,
    state_must_grow,
)
from engine.nucleus.lifecycle import Stage, StageStatus
from engine.nucleus.registry import build_seed_registry

REPO_ROOT = Path(__file__).resolve().parents[3]


# -- the lifecycle ----------------------------------------------------------- #


def test_the_declared_lifecycle_is_the_mandated_chain():
    """The chain is asserted as a RELATIONSHIP, never as a position or a population.

    A stage admitted anywhere the manifest permits — before the head, in an ordinal gap
    between two stages, or after the highest ordinal — leaves every assertion below true.
    Nothing here names a last stage: ``UCL-000001`` declares no terminal stage and the
    evolution cycle wraps (ISD-L-05), so a positional ``[-1]`` assertion would encode a
    termination the constitution denies.
    """
    assert lifecycle.STAGES, "the lifecycle declares no stage"
    head, *rest = lifecycle.STAGES
    assert head.depends_on == (), "the chain head depends on nothing"
    previous = head
    for stage in rest:
        assert stage.depends_on == (previous.stage_id,), f"{stage.stage_id} breaks the chain"
        assert stage.ordinal > previous.ordinal, f"{stage.stage_id} does not ascend"
        previous = stage
    # Mandated members, asserted by membership. Membership claims that these stages exist;
    # it claims nothing about which others do, so the set stays open.
    names = {stage.name for stage in lifecycle.STAGES}
    assert {
        "Receive Goal",
        "Reuse Before Create",
        "Deterministic Fixed Point",
        "Assign Universal Constitutional Identifier",
    } <= names


def test_stage_order_is_derived_total_and_acyclic():
    order = lifecycle.stage_order()
    assert len(order) == len(lifecycle.STAGES)
    assert order == [s.stage_id for s in lifecycle.STAGES]


def test_a_cyclic_stage_graph_has_no_order():
    cyclic = (
        Stage("A", "a", 1, "G", depends_on=("B",)),
        Stage("B", "b", 2, "G", depends_on=("A",)),
    )
    with pytest.raises(LifecycleError):
        lifecycle.stage_order(cyclic)


def test_stage_lookup_fails_closed():
    assert lifecycle.stage("UCL-S-0010").name == "Receive Goal"
    with pytest.raises(LifecycleError):
        lifecycle.stage("UCL-S-9999")


def test_the_in_engine_stages_do_not_diverge_from_the_declaration_that_owns_them():
    manifest_path = REPO_ROOT / "00-MASTER" / "UCL-000001" / "ucl-stage-manifest.json"
    if not manifest_path.exists():  # pragma: no cover - declaration present in this tree
        pytest.skip("stage manifest not present")
    manifest = json.loads(manifest_path.read_text("utf-8"))
    assert lifecycle.verify_manifest_alignment(manifest) == ()


def test_manifest_alignment_reports_divergence():
    assert lifecycle.verify_manifest_alignment({}) == ("manifest carries no 'nodes' list",)
    divergences = lifecycle.verify_manifest_alignment(
        {"nodes": [{"id": "UCL-S-0010", "stage": "Wrong", "ordinal": 99, "group": "X"}]}
    )
    assert any("stage" in d for d in divergences)
    assert any("absent from manifest" in d for d in divergences)
    assert lifecycle.verify_manifest_alignment({"nodes": ["nope"]})[0].startswith("manifest node")
    assert any(
        "absent from STAGES" in d
        for d in lifecycle.verify_manifest_alignment({"nodes": [{"id": "UCL-S-0011"}]})
    )


def test_execution_runs_every_stage_and_chains_them():
    execution = lifecycle.execute("UCOS-NUC-000000000001")
    assert execution.complete is True
    assert execution.status == "COMPLETE"
    assert len(execution.outcomes) == len(lifecycle.STAGES)
    assert execution.chain_is_intact() is True
    assert execution.chain_head
    assert execution.failures == ()
    assert execution.to_dict()["declared_stage_count"] == len(lifecycle.STAGES)


def test_execution_replays_to_a_deterministic_fixed_point():
    report = lifecycle.replay("UCOS-NUC-000000000001")
    assert report["fixed_point"] is True
    assert report["chain_intact"] is True
    assert report["first_digest"] == report["second_digest"]


def test_a_failing_stage_is_recorded_not_swallowed():
    def failing(subject: str, stage: Stage):
        if stage.stage_id == "UCL-S-0160":
            return StageStatus.FAILED, "probe", {"why": "deliberate"}
        return StageStatus.SATISFIED, "probe", {}

    execution = lifecycle.execute("subject", stage_function=failing)
    assert execution.complete is False
    assert execution.status == "INCOMPLETE"
    assert [o.stage_id for o in execution.failures] == ["UCL-S-0160"]


def test_not_applicable_is_a_first_class_status():
    def mixed(subject: str, stage: Stage):
        return StageStatus.NOT_APPLICABLE, "probe", {}

    execution = lifecycle.execute("subject", stage_function=mixed)
    assert execution.complete is True
    assert all(o.status is StageStatus.NOT_APPLICABLE for o in execution.outcomes)


def test_an_unknown_status_fails_closed():
    def bogus(subject: str, stage: Stage):
        return "elsewhere", "probe", {}

    with pytest.raises(LifecycleError):
        lifecycle.execute("subject", stage_function=bogus)


def test_an_unnamed_subject_cannot_execute():
    with pytest.raises(LifecycleError):
        lifecycle.execute("   ")


def test_a_tampered_chain_is_detected():
    execution = lifecycle.execute("subject")
    from engine.nucleus.lifecycle import LifecycleExecution, StageOutcome

    outcomes = list(execution.outcomes)
    first = outcomes[0]
    outcomes[0] = StageOutcome(
        stage_id=first.stage_id,
        name="tampered",
        group=first.group,
        status=first.status,
        evidence=first.evidence,
        detail=first.detail,
        prev_hash=first.prev_hash,
        entry_hash=first.entry_hash,
    )
    tampered = LifecycleExecution(
        subject=execution.subject,
        lifecycle_id=execution.lifecycle_id,
        outcomes=tuple(outcomes),
        order=execution.order,
    )
    assert tampered.chain_is_intact() is False


def test_the_lifecycle_applies_to_every_category_of_thing():
    registry = build_seed_registry()
    subjects = [s.universal_id for s in registry.subjects()][:6]
    subjects += [c.universal_id for c in registry.capabilities()][:3]
    for subject in subjects:
        execution = lifecycle.execute(subject)
        assert execution.complete
        assert execution.subject == subject


def test_lifecycle_document_declares_no_ceiling():
    document = lifecycle.to_document()
    assert document["stage_count"] == len(lifecycle.STAGES)
    assert document["closed_set"] is False
    assert document["upper_limit"] is None
    assert lifecycle.digest() == lifecycle.digest()
    assert len(document["groups"]) >= 10


def test_an_appended_stage_needs_no_code_change():
    """Openness performed. The assertions relate the run to what was appended, not to a count."""
    appended = Stage(
        "UCL-S-0460",
        "Federate Across Frames",
        460,
        "ELEVATION",
        depends_on=(lifecycle.STAGES[-1].stage_id,),
    )
    extended = (*lifecycle.STAGES, appended)
    execution = lifecycle.execute("subject", stages=extended)
    assert len(execution.outcomes) == len(extended)
    assert [o.stage_id for o in execution.outcomes] == [s.stage_id for s in extended]
    assert execution.outcomes[-1].name == appended.name


# -- lineage ----------------------------------------------------------------- #


def test_lineage_is_appended_hash_chained_and_intact():
    ledger = lineage.LineageLedger()
    first = ledger.record(lineage.GENESIS, subject_id="ID-1", subject_key="k1")
    second = ledger.record(lineage.REGISTERED, subject_id="ID-1", subject_key="k1")
    assert first.prev_hash == ""
    assert second.prev_hash == first.entry_hash
    assert ledger.head == second.entry_hash
    assert ledger.is_intact() is True
    assert len(ledger) == 2
    assert ledger.lineage_of("ID-1") == (lineage.GENESIS, lineage.REGISTERED)
    assert ledger.subjects() == ("ID-1",)


def test_lineage_refuses_an_unnamed_event_or_subject():
    ledger = lineage.LineageLedger()
    with pytest.raises(NucleusError):
        ledger.record("", subject_id="ID-1", subject_key="k")
    with pytest.raises(NucleusError):
        ledger.record("e", subject_id="", subject_key="k")
    with pytest.raises(NucleusError):
        ledger.record("e", subject_id="ID", subject_key="")


def test_a_rewritten_lineage_is_detected():
    ledger = lineage.LineageLedger()
    ledger.record(lineage.GENESIS, subject_id="ID-1", subject_key="k1")
    entries = list(ledger.entries())
    forged = lineage.LineageEntry(
        sequence=1,
        event="forged",
        subject_id="ID-1",
        subject_key="k1",
        prev_hash="",
        entry_hash=entries[0].entry_hash,
    )
    assert lineage.LineageLedger([forged]).is_intact() is False


def test_registry_lineage_covers_every_subject_and_assignment():
    registry = build_seed_registry()
    ledger = lineage.ledger_for(registry)
    known = [s.universal_id for s in registry.subjects()]
    assert ledger.is_intact()
    assert ledger.unrecorded(known) == ()
    assert ledger.orphans(known + [c.universal_id for c in registry.capabilities()]) == ()
    assert len(ledger) == len(known) * 2 + len(registry.assignments())
    document = ledger.to_document()
    assert document["intact"] is True
    assert ledger.digest() == lineage.ledger_for(build_seed_registry()).digest()


def test_lineage_filters_by_event():
    registry = build_seed_registry()
    ledger = lineage.ledger_for(registry)
    assigned = ledger.entries(event=lineage.OWNERSHIP_ASSIGNED)
    assert len(assigned) == len(registry.assignments())


def test_supersession_is_recorded_as_such():
    from engine.nucleus.model import CapabilityDeclaration, SubjectDeclaration
    from engine.nucleus.registry import NucleusRegistry

    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="payment", title="Payment", concept="payment"))
    fresh.register_subject(SubjectDeclaration(key="billing", title="Billing", concept="billing"))
    fresh.register_capability(
        CapabilityDeclaration(key="invoice", title="Invoice", owner="payment")
    )
    fresh.reassign_capability("invoice", new_owner="billing", authority="TEST")
    ledger = lineage.ledger_for(fresh)
    assert len(ledger.entries(event=lineage.OWNERSHIP_SUPERSEDED)) == 1


# -- evolution --------------------------------------------------------------- #


def test_evolution_is_generational_linked_and_evidenced():
    ledger = EvolutionLedger()
    first = ledger.evolve(
        subject_id="ID-1",
        subject_key="payment",
        change="c1",
        authority="A",
        state={"capability": 1},
    )
    second = ledger.evolve(
        subject_id="ID-1",
        subject_key="payment",
        change="c2",
        authority="A",
        state={"capability": 2},
    )
    assert first.generation == 1 and second.generation == 2
    assert second.supersedes == first.evolution_id
    assert ledger.generation_of("ID-1") == 2
    assert ledger.chain_is_unbroken("ID-1") is True
    assert ledger.unevidenced() == ()
    assert ledger.latest("ID-1") == second
    assert ledger.lineage.is_intact()


def test_capability_regression_is_refused():
    ledger = EvolutionLedger(validator=state_must_grow)
    ledger.evolve(
        subject_id="ID-1", subject_key="k", change="c1", authority="A", state={"capability": 5}
    )
    with pytest.raises(EvolutionError) as exc:
        ledger.evolve(
            subject_id="ID-1", subject_key="k", change="c2", authority="A", state={"capability": 4}
        )
    assert "regressed" in exc.value.detail["reason"]


def test_the_growth_validator_requires_a_reading():
    ledger = EvolutionLedger(validator=state_must_grow)
    with pytest.raises(EvolutionError):
        ledger.evolve(subject_id="ID-1", subject_key="k", change="c", authority="A")
    ok, reason = state_must_grow(
        Evolution(
            subject_id="ID",
            subject_key="k",
            generation=1,
            change="c",
            authority="A",
            state={"capability": "not-a-number", "previous_capability": 1},
        )
    )
    assert ok is False and "numeric" in reason


def test_evolution_requires_its_declarations():
    with pytest.raises(EvolutionError):
        Evolution(subject_id="", subject_key="k", generation=1, change="c", authority="A")
    with pytest.raises(EvolutionError):
        Evolution(subject_id="ID", subject_key="k", generation=0, change="c", authority="A")


def test_permissive_validator_still_records_lineage():
    ledger = EvolutionLedger(validator=always_valid)
    ledger.evolve(subject_id="ID-1", subject_key="k", change="c", authority="A")
    document = ledger.to_document()
    assert document["count"] == 1
    assert document["chains_unbroken"] is True
    assert document["lineage_intact"] is True
    assert document["closed_set"] is False
    assert ledger.digest() == ledger.digest()
    assert ledger.evolutions()[0].to_dict()["generation"] == 1


def test_everything_evolves_through_one_mechanism():
    registry = build_seed_registry()
    ledger = EvolutionLedger(lineage=lineage.ledger_for(registry), validator=state_must_grow)
    population = list(registry.subjects()) + list(registry.capabilities())
    for index, item in enumerate(population, start=1):
        ledger.evolve(
            subject_id=item.universal_id,
            subject_key=item.key,
            change="stage-0",
            authority="UCOS-NUC-LAW-0001",
            state={"capability": index},
        )
    assert len(ledger.evolutions()) == len(population)
    assert ledger.unevidenced() == ()
    assert all(ledger.chain_is_unbroken(s) for s in ledger.subjects())


def test_a_context_missing_its_resolution_digest_is_refused():
    """A FRAME NAME IS NOT A RESOLVED FRAME.

    Two conditions, and only the absent-frame one had a case. A context naming a frame but no
    resolution digest says which reality was intended and not which reality was RESOLVED — so
    two generations recorded under two different resolutions of the same frame would be
    indistinguishable records, which is the continuity the ledger would then be claiming
    without support. The passing arm is measured beside it, because a validator that refuses
    everything proves nothing about what it admits.
    """

    def _evolution(context):
        return Evolution(
            subject_id="ID-1",
            subject_key="k",
            generation=1,
            change="c",
            state={"context": context},
            supersedes=None,
            authority="A",
        )

    assert context_is_declared(_evolution({"frame": "planetary-a1", "resolution_digest": "abc"}))[0]

    unframed = context_is_declared(_evolution({"resolution_digest": "abc"}))
    assert unframed == (False, "evolution declares no reference frame")

    unresolved = context_is_declared(_evolution({"frame": "planetary-a1"}))
    assert unresolved == (False, "evolution's context names no resolution digest")


def test_capability_that_holds_or_grows_is_admitted():
    """MONOTONICITY REFUSES A FALL AND MUST ADMIT A HOLD.

    Only the regression was tested, so the arm that says "this reading is fine" had never
    executed — and a validator whose passing path is unmeasured is one that could be refusing
    everything while the suite only ever asks it to refuse. A reading equal to its predecessor
    is not a regression: capability may hold, and requiring strict growth would refuse every
    evolution that changed something other than capability.
    """
    ledger = EvolutionLedger(validator=state_must_grow)
    first = ledger.evolve(
        subject_id="ID-1", subject_key="k", change="c1", authority="A", state={"capability": 5}
    )
    held = ledger.evolve(
        subject_id="ID-1", subject_key="k", change="c2", authority="A", state={"capability": 5}
    )
    grew = ledger.evolve(
        subject_id="ID-1", subject_key="k", change="c3", authority="A", state={"capability": 6}
    )

    assert (first.generation, held.generation, grew.generation) == (1, 2, 3)
    assert held.state["previous_capability"] == 5
    assert grew.state["previous_capability"] == 5


def test_a_first_evolution_carries_no_previous_reading():
    """THE PREVIOUS READING IS COPIED FORWARD FROM A PREDECESSOR THAT EXISTS.

    Every ledger in this suite is measured after at least one evolution, so the arm for the
    FIRST one — where there is no predecessor to read a prior capability from — had never
    run. Inventing a previous reading there would give generation 1 a predecessor it does not
    have, and the monotonicity check would then be comparing a real reading against a
    fabricated one.
    """
    ledger = EvolutionLedger(validator=state_must_grow)

    first = ledger.evolve(
        subject_id="ID-1", subject_key="k", change="c1", authority="A", state={"capability": 5}
    )

    assert "previous_capability" not in first.state
    assert first.supersedes is None


def test_a_chain_whose_generations_or_links_disagree_is_reported_broken():
    """AN UNBROKEN CHAIN IS THE CLAIM, AND IT HAD ONLY EVER BEEN CONFIRMED.

    The reader answers True on every ledger this suite builds, because ``evolve`` is the only
    way to add to one and it numbers and links each generation itself. The False arm is what
    the reader is FOR: a history assembled another way — rehydrated, or merged from two
    ledgers — can carry a generation out of order or a link to the wrong predecessor, and
    either makes the sequence a list rather than a chain.
    """
    ledger = EvolutionLedger()
    ledger.evolve(subject_id="ID-1", subject_key="k", change="c1", authority="A", state={})
    second = ledger.evolve(subject_id="ID-1", subject_key="k", change="c2", authority="A", state={})
    assert ledger.chain_is_unbroken("ID-1") is True

    object.__setattr__(second, "generation", 7)
    assert ledger.chain_is_unbroken("ID-1") is False


def test_a_lineage_entry_recorded_out_of_sequence_is_not_intact():
    """THE LEDGER'S THREE INVARIANTS, AND THE ORDINAL WAS THE UNTESTED ONE.

    A forged back-link was tested; the sequence was not. An entry whose ordinal disagrees
    with where it sits is a record that was reordered or removed — the digests can still
    reproduce while the ledger no longer says what happened in what order, which is the whole
    thing a lineage ledger is for.
    """
    ledger = lineage.LineageLedger()
    ledger.record(event="declared", subject_id="ID-1", subject_key="k1")
    ledger.record(event="declared", subject_id="ID-2", subject_key="k2")
    assert ledger.is_intact() is True

    object.__setattr__(ledger.entries()[1], "sequence", 9)
    assert ledger.is_intact() is False
