"""UCOS-CSF-000001 — every one of the 45 stage faculties, exercised and refused.

Two things must be true of this suite or the faculties are decoration.

**Every faculty must run.** Not "the registry has 45 entries" — each one is invoked over a
real population and its measurement inspected, because a faculty that raises is a stage
that is not discharged, and a registry entry proves nothing about the function behind it.

**Every faculty must be capable of failing.** A measurement that returns ``satisfied`` for
any input is not a measurement, and would make the whole lifecycle closure meaningless. So
the gate-carrying faculties are driven against a *broken* population and asserted to
refuse it. That is the test that distinguishes measurement from decoration, and it is why
this file is longer than a smoke test would be.
"""

from __future__ import annotations

import pytest

from engine.constitution import catalog, evolution, stages
from engine.constitution.errors import ConstitutionalError
from engine.constitution.metadata import Population
from engine.nucleus import lifecycle as ucl
from engine.tests.constitution.conftest import declare, population


@pytest.fixture(scope="module")
def system() -> Population:
    """The constitutional execution system, declared as itself."""
    return catalog.build_population()


@pytest.fixture(scope="module")
def measured(system: Population) -> dict[str, stages.Measurement]:
    """Every faculty measured once over the system population."""
    return stages.measure_all(system)


def test_a_faculty_exists_for_every_declared_stage() -> None:
    """A stage the lifecycle declares and nothing can discharge is the defect this closes."""
    declared = [stage.stage_id for stage in ucl.STAGES]
    assert declared, "the lifecycle declares no stage, so the assertions below are vacuous"
    assert stages.unrealized(declared) == ()
    assert set(stages.FACULTIES) == set(declared)


@pytest.mark.parametrize("stage_id", sorted(stages.FACULTIES))
def test_every_faculty_executes_and_measures(
    stage_id: str, measured: dict[str, stages.Measurement]
) -> None:
    """Each faculty runs, decides, and carries auditable evidence for its decision."""
    measurement = measured[stage_id]
    assert isinstance(measurement, stages.Measurement)
    assert isinstance(measurement.satisfied, bool)
    assert measurement.detail, f"{stage_id} decided without saying what it measured"
    assert measurement.evidence, f"{stage_id} returned no evidence payload"
    assert measurement.digest().startswith(stages.EVIDENCE_PREFIX)


@pytest.mark.parametrize("stage_id", sorted(stages.FACULTIES))
def test_no_faculty_returns_the_stage_declaration_as_its_own_evidence(
    stage_id: str, measured: dict[str, stages.Measurement]
) -> None:
    """Self-referential evidence is the declaration proving itself, and is refused."""
    digest = measured[stage_id].digest()
    assert not digest.startswith(ucl.LIFECYCLE_ID)
    assert stage_id not in digest


def test_the_system_population_discharges_every_stage(
    measured: dict[str, stages.Measurement],
) -> None:
    unsatisfied = sorted(k for k, m in measured.items() if not m.satisfied)
    assert unsatisfied == [], f"unsatisfied faculties: {unsatisfied}"


def test_measurement_is_deterministic(system: Population) -> None:
    """Two independent measurements of one state must produce one set of digests."""
    first = {k: m.digest() for k, m in stages.measure_all(system).items()}
    second = {k: m.digest() for k, m in stages.measure_all(system).items()}
    assert first == second


def test_evidence_digests_distinguish_the_stages(
    measured: dict[str, stages.Measurement],
) -> None:
    """Faculties measuring different things must not collapse to one digest.

    If most stages shared a digest they would be one measurement wearing 45 names, which
    is exactly the group-level discharge this faculty set replaced.
    """
    digests = {m.digest() for m in measured.values()}
    assert len(digests) > len(measured) // 2


# --------------------------------------------------------------------------- refusals


def _broken() -> Population:
    """A population that violates something every gate-carrying faculty measures."""
    return population(
        declare("orphan", dependencies=("ghost",), certifications=("orphan",)),
        declare("twin_a", outputs=("collide",)),
        declare("twin_b", outputs=("collide",), governance_rules=()),
    )


@pytest.mark.parametrize(
    "stage_id",
    [
        "UCL-S-0040",  # Repository Truth Discovery — dangling referent
        "UCL-S-0070",  # Capability Discovery — duplicate output
        "UCL-S-0110",  # Reuse Before Create — duplicate output
        "UCL-S-0160",  # Validate — legality fails
        "UCL-S-0170",  # Verify — self-attestation
        "UCL-S-0190",  # Reason — no executable plan
        "UCL-S-0240",  # Architect — plan refuses
        "UCL-S-0270",  # Govern — a subject declares no governance
        "UCL-S-0280",  # Certify — enforcement gate fails
        "UCL-S-0420",  # Increase Constitutional Capability — invariants unclean
    ],
)
def test_gate_carrying_faculties_refuse_a_broken_population(stage_id: str) -> None:
    """A faculty that cannot fail is not measuring anything."""
    measurement = stages.measure(stage_id, _broken())
    assert not measurement.satisfied, f"{stage_id} passed a population it should refuse"
    assert measurement.detail


def test_defect_finding_faculties_are_satisfied_by_finding_defects() -> None:
    """Gap Discovery and Challenge measure that everything *was* examined.

    They must stay satisfied over a broken population — a gap-finder that fails when it
    finds gaps would be unsatisfiable in every real repository, and one that reports zero
    because nothing looked is the failure they exist to prevent.
    """
    broken = _broken()
    gap = stages.measure("UCL-S-0100", broken)
    challenge = stages.measure("UCL-S-0210", broken)
    assert gap.satisfied and gap.evidence["gaps"] > 0
    assert challenge.satisfied and challenge.evidence["failing"]


def test_an_unknown_stage_fails_closed(system: Population) -> None:
    with pytest.raises(ConstitutionalError) as excinfo:
        stages.measure("UCL-S-9999", system)
    assert excinfo.value.detail["stage_id"] == "UCL-S-9999"


def test_the_context_derives_one_shared_view(system: Population) -> None:
    """45 independently derived views could disagree; one cannot."""
    ctx = stages.Context(population=system)
    assert ctx.graph is ctx.graph
    assert ctx.plan.graph.digest() == ctx.graph.digest()
    assert ctx.acceptance.digest() == ctx.acceptance.digest()


def test_the_faculty_set_is_addressable_and_open() -> None:
    document = stages.to_document()
    assert document["faculty_count"] == len(ucl.STAGES)
    assert document["closed_set"] is False
    assert stages.digest() == stages.digest()


# --------------------------------------------------------------------------- integration


def test_the_lifecycle_executes_every_stage_through_the_faculties(system: Population) -> None:
    """The composition point: UCL-000001 runs, discharged by measurement per stage."""

    execution = ucl.execute(
        "repository",
        stage_function=evolution.lifecycle_stage_function(system),
        context={"frame": "test"},
    )
    assert len(execution.outcomes) == len(ucl.STAGES)
    assert execution.complete
    assert execution.chain_is_intact()
    assert not [o for o in execution.outcomes if o.status is ucl.StageStatus.NOT_APPLICABLE]
    assert all(o.evidence.startswith(stages.EVIDENCE_PREFIX) for o in execution.outcomes)


def test_a_broken_population_fails_stages_rather_than_skipping_them() -> None:
    execution = ucl.execute(
        "repository", stage_function=evolution.lifecycle_stage_function(_broken())
    )
    assert execution.failures
    assert not execution.complete


def test_the_manifest_records_the_faculty_module_as_evidence() -> None:
    """Probe 2 of the closure engine reads the manifest; the record must be true."""
    ctx = stages.Context(population=catalog.build_population())
    nodes = ctx.manifest
    assert len(nodes) == len(ucl.STAGES)
    for node in nodes:
        assert "engine/constitution/stages.py" in node["evidence"], node["id"]


def test_a_repository_missing_the_artifacts_a_faculty_reads_yields_nothing_not_a_crash(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """THE FACULTIES READ REAL ARTIFACTS, and a clone that has not produced them yet is a
    real state — a pristine checkout before the generators have run is exactly that.

    An absent manifest yields no stages and an absent knowledge store yields no knowledge;
    both are empty ANSWERS. Letting the read raise would make every stage in the run
    unevaluable for a reason that has nothing to do with the stage, and the resulting
    lifecycle report would say the constitution could not be measured when what actually
    happened is that one file had not been generated.
    """
    monkeypatch.setattr(stages, "REPO", tmp_path)
    context = stages.Context(population=population(declare("root")))

    assert context.manifest == []
    assert context.knowledge == {}


def test_a_measurement_renders_its_evidence_and_the_digest_of_that_evidence() -> None:
    """The evidence identity is a digest of the PAYLOAD and never of the stage name, so two
    stages measuring the same thing carry the same evidence id and a stage measuring
    something different cannot borrow another's. ``to_dict`` is how a lifecycle record reads
    a measurement, and it had no caller — a projection nothing reads can drift from the
    object it projects without any failure."""
    measurement = stages.Measurement(
        satisfied=True, detail="two subjects declared", evidence={"subjects": 2}
    )
    rendered = measurement.to_dict()

    assert rendered["satisfied"] is True
    assert rendered["detail"] == "two subjects declared"
    assert rendered["evidence"] == {"subjects": 2}
    assert rendered["evidence_digest"] == measurement.digest()
    assert rendered["evidence_digest"].startswith(f"{stages.EVIDENCE_PREFIX}:")

    same_payload = stages.Measurement(
        satisfied=False, detail="a different sentence entirely", evidence={"subjects": 2}
    )
    assert same_payload.digest() == measurement.digest(), "the digest read the detail"

    different = stages.Measurement(satisfied=True, detail="x", evidence={"subjects": 3})
    assert different.digest() != measurement.digest()
