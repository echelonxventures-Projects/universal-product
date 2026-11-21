"""UAUE-000001 Epoch 6 — the declared register surface.

The defect this surface closes is not "a missing document". The declaration named eighteen
registers and fourteen renderers, the gate measured every certification proof, and then discarded
the measurement: a certification that is correct and unreadable is indistinguishable from a
certification nobody performed. So the surface exists — and a surface that produces files is
exactly the kind of capability that can look present while being absent, which is what this suite
measures.

Six properties, each with the mutation that closes it:

1. **The declaration drives the surface.** Every declared register is rendered, in declared order,
   through a renderer the declaration names. No register file name and no register title appears
   anywhere in the renderer module: a hard-coded name would be the declaration kept in two places,
   and the second copy is the one that goes stale.
2. **Nothing here writes.** The renderer returns bodies. The gate performs every write, under a
   write-scope bound measured in ``test_uaue_evolution_engine.py``.
3. **The bytes are deterministic.** Two renders of one report, and two independent measurements of
   one tree, produce identical bytes — the property the replay proof rests on.
4. **The bytes are reproducible elsewhere.** No memory address, no wall clock, no absolute
   repository root. Measured by poisoning a renderer and requiring the guard to fire: the first
   render of this surface shipped a heap address, the diff was one line, and every count in the
   register was correct, which is the shape of defect a spot read does not catch.
5. **A declared renderer that does not exist is a refusal.** Not a skipped register. A surface that
   wrote seventeen files and reported success would leave one register carrying a previous run's
   measurements, and the gate would still be OPEN.
6. **Drift is detected as bytes.** A hand edit to a committed register is a failure, not a fact.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from engine.uaue import gate as gate_module
from engine.uaue.gate import GateReport, measure, render_registers
from engine.uaue.model import EvolutionAuthorityError, Invariant
from engine.uaue.registers import (
    DERIVED_TRUTH,
    RENDERERS,
    _relative,
    _unknown_satisfied,
    irreproducible_content,
    mandatory_measures,
    register_path,
    render_register,
    rendered_surface,
    replay_drift,
    surface_digest,
)
from engine.uaue.resolution import PROGRAMME_HOME, REPO_ROOT

REGISTERS_SOURCE = REPO_ROOT / "engine" / "uaue" / "registers.py"


@pytest.fixture(scope="module")
def report() -> GateReport:
    return measure()


@pytest.fixture(scope="module")
def surface(report: GateReport) -> dict[str, str]:
    return rendered_surface(report)


# --------------------------------------------------------------------------------------
# 1. The declaration drives the surface
# --------------------------------------------------------------------------------------


def test_the_implemented_renderers_are_exactly_the_declared_renderers(report: GateReport) -> None:
    """Both directions. A declared renderer that is absent is an unproducible register; an
    implemented renderer nothing declares is code no declaration governs."""
    declared = {entry.renderer for entry in report.context.authority.registers}
    assert declared == set(RENDERERS), {
        "declared but not implemented": sorted(declared - set(RENDERERS)),
        "implemented but not declared": sorted(set(RENDERERS) - declared),
    }


def test_every_declared_register_renders_in_declared_order(
    report: GateReport, surface: dict[str, str]
) -> None:
    declared = [entry.file for entry in report.context.authority.registers]
    assert list(surface) == declared
    assert len(surface) == len(report.context.authority.registers)
    assert all(body.strip() for body in surface.values())


def test_no_register_file_name_or_title_is_written_into_the_renderer_module(
    report: GateReport,
) -> None:
    """The register set lives in the declaration. A nineteenth register must be a declaration edit.

    Measured against the declaration rather than against a list in this test, so a register added
    tomorrow is checked by this assertion without anyone remembering to extend it.
    """
    source = REGISTERS_SOURCE.read_text("utf-8")
    for entry in report.context.authority.registers:
        assert entry.file not in source, f"registers.py names the register file {entry.file}"
        assert entry.title not in source, f"registers.py names the register title {entry.title}"


def test_every_register_states_the_authority_relation_it_holds(
    report: GateReport, surface: dict[str, str]
) -> None:
    """A register read in isolation must not be mistakable for a source of authority."""
    digest = report.context.authority.digest()[:16]
    for entry in report.context.authority.registers:
        body = surface[entry.file]
        assert body.startswith(f"# {entry.title}\n")
        assert DERIVED_TRUTH in body
        assert digest in body, f"{entry.file} does not carry the declaration digest"
        assert entry.renderer in body
        assert body.endswith("\n")


# --------------------------------------------------------------------------------------
# 2. Nothing here writes — the renderer hands back bodies and reaches no path
# --------------------------------------------------------------------------------------


def test_rendering_the_whole_surface_touches_no_path(
    report: GateReport, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Rendering with the working directory moved elsewhere produces bytes and creates nothing."""
    monkeypatch.chdir(tmp_path)
    bodies = rendered_surface(report)
    assert len(bodies) == len(report.context.authority.registers)
    assert list(tmp_path.iterdir()) == []


def test_register_path_computes_a_destination_without_creating_it(
    report: GateReport, tmp_path: Path
) -> None:
    entry = report.context.authority.registers[0]
    target = register_path(report.context, entry.file, tmp_path)
    assert target == tmp_path / PROGRAMME_HOME / entry.file
    assert not target.exists()
    assert not target.parent.exists()


# --------------------------------------------------------------------------------------
# 3. Determinism
# --------------------------------------------------------------------------------------


def test_the_surface_is_byte_identical_when_rendered_twice(
    report: GateReport, surface: dict[str, str]
) -> None:
    assert rendered_surface(report) == surface
    assert surface_digest(report) == surface_digest(report)


def test_the_surface_is_byte_identical_across_independent_measurements(
    surface: dict[str, str],
) -> None:
    """A second measurement of one tree must render one surface.

    This is the in-process half of the replay proof. The cross-process half is the gate's
    ``--replay``, which compares the committed bytes; both are required, because a surface that
    reproduced only within one interpreter would still drift in CI.
    """
    second = measure()
    assert rendered_surface(second) == surface


# --------------------------------------------------------------------------------------
# 4. Reproducibility elsewhere — and the guard that measures it can fire
# --------------------------------------------------------------------------------------


def test_the_committed_surface_embeds_nothing_irreproducible(report: GateReport) -> None:
    assert irreproducible_content(report) == ()


@pytest.mark.parametrize(
    ("token", "why"),
    [
        ("<engine.uaue.objects.EvolutionObject object at 0x7f2b3c4d5e6f>", "a memory address"),
        ("rendered 2026-08-15T12:34:56Z", "a wall clock"),
    ],
)
def test_the_irreproducibility_guard_fires_on_leaked_content(
    report: GateReport, monkeypatch: pytest.MonkeyPatch, token: str, why: str
) -> None:
    """The guard is measured by leaking, because a guard that has never fired has never run."""
    entry = report.context.authority.registers[0]
    monkeypatch.setitem(RENDERERS, entry.renderer, lambda _report, _register: f"# leak\n{token}\n")
    findings = irreproducible_content(report)
    assert findings, f"the guard did not detect {why}"
    assert any(entry.file in finding for finding in findings), findings


def test_the_irreproducibility_guard_fires_on_the_absolute_repository_root(
    report: GateReport, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An absolute path reproduces only on the machine that wrote it."""
    root = str(report.context.substrate.root)
    entry = report.context.authority.registers[0]
    monkeypatch.setitem(RENDERERS, entry.renderer, lambda _r, _reg: f"# leak\n{root}/engine\n")
    findings = irreproducible_content(report)
    assert any("absolute repository root" in finding for finding in findings), findings


def test_the_surface_obligation_closes_the_gate_when_a_register_leaks(
    report: GateReport, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The finding must reach the gate's verdict, not only the guard's return value."""
    entry = report.context.authority.registers[0]
    monkeypatch.setitem(RENDERERS, entry.renderer, lambda _r, _reg: "# leak\n0x7f2b3c4d5e6f\n")
    closed = gate_module.measure(report.context)
    assert not closed.open
    assert "UAUE-GATE-08" in {failure.identifier for failure in closed.failures}


# --------------------------------------------------------------------------------------
# 5. A declared renderer that does not exist is a refusal, never a skipped register
# --------------------------------------------------------------------------------------


def test_an_unimplemented_renderer_refuses_the_whole_surface(
    report: GateReport, monkeypatch: pytest.MonkeyPatch
) -> None:
    entry = report.context.authority.registers[0]
    monkeypatch.delitem(RENDERERS, entry.renderer)
    with pytest.raises(EvolutionAuthorityError) as refusal:
        render_register(report, entry)
    assert entry.renderer in str(refusal.value) or entry.renderer in repr(refusal.value)
    with pytest.raises(EvolutionAuthorityError):
        rendered_surface(report)


def test_an_unimplemented_renderer_writes_no_file_at_all(
    report: GateReport, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The refusal happens before the first path is touched, so there is no partial surface."""
    entry = report.context.authority.registers[-1]
    monkeypatch.delitem(RENDERERS, entry.renderer)
    with pytest.raises(EvolutionAuthorityError):
        render_registers(report, tmp_path)
    assert list(tmp_path.rglob("*.md")) == []


def test_an_unimplemented_renderer_closes_the_gate(
    report: GateReport, monkeypatch: pytest.MonkeyPatch
) -> None:
    entry = report.context.authority.registers[0]
    monkeypatch.delitem(RENDERERS, entry.renderer)
    obligation = gate_module._surface_obligation(report.context, report)
    assert not obligation.satisfied
    assert entry.file in obligation.detail


# --------------------------------------------------------------------------------------
# 6. Drift is measured as bytes
# --------------------------------------------------------------------------------------


def test_a_rendered_surface_replays_and_a_hand_edit_does_not(
    report: GateReport, tmp_path: Path
) -> None:
    written = render_registers(report, tmp_path)
    assert replay_drift(report, tmp_path) == ()

    edited = written[0]
    edited.write_text(edited.read_text("utf-8") + "a hand edit\n", encoding="utf-8")
    drift = replay_drift(report, tmp_path)
    assert any(edited.name in entry for entry in drift), drift

    edited.write_text(rendered_surface(report)[edited.name], encoding="utf-8")
    assert replay_drift(report, tmp_path) == ()

    written[-1].unlink()
    drift = replay_drift(report, tmp_path)
    assert any("not rendered" in entry for entry in drift), drift


def test_an_unrendered_surface_is_drift_for_every_declared_register(
    report: GateReport, tmp_path: Path
) -> None:
    drift = replay_drift(report, tmp_path)
    assert len(drift) == len(report.context.authority.registers)


def test_the_surface_digest_changes_when_any_register_changes(
    report: GateReport, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = surface_digest(report)
    entry = report.context.authority.registers[0]
    monkeypatch.setitem(RENDERERS, entry.renderer, lambda _r, _reg: "# a different body\n")
    assert surface_digest(report) != before


# --------------------------------------------------------------------------------------
# The mandatory measures the registers publish
# --------------------------------------------------------------------------------------


def test_every_declared_mandatory_measure_is_computed_and_meets_its_expectation(
    report: GateReport,
) -> None:
    measures = mandatory_measures(report)
    for entry in report.context.authority.mandatory:
        assert entry.measure in measures, f"{entry.identifier} names an uncomputed measure"
        assert measures[entry.measure] == entry.expect, (
            f"{entry.identifier} ({entry.invariant}): "
            f"expected {entry.expect}, measured {measures[entry.measure]}"
        )


def test_a_measure_that_cannot_be_computed_is_a_refusal_and_never_a_zero(
    report: GateReport,
) -> None:
    """A missing measure that defaulted to zero would read as a satisfied blocking invariant."""
    unmeasurable = Invariant(
        identifier="AUE-MAN-TEST",
        invariant="an invariant naming a measure nothing computes",
        measure="a_measure_no_renderer_can_compute",
        expect=0,
        blocking=True,
    )
    authority = replace(
        report.context.authority, mandatory=report.context.authority.mandatory + (unmeasurable,)
    )
    poisoned = replace(report, context=replace(report.context, authority=authority))
    with pytest.raises(EvolutionAuthorityError):
        mandatory_measures(poisoned)


def test_the_mandatory_obligation_closes_when_a_measure_cannot_be_computed(
    report: GateReport,
) -> None:
    unmeasurable = Invariant(
        identifier="AUE-MAN-TEST",
        invariant="an invariant naming a measure nothing computes",
        measure="a_measure_no_renderer_can_compute",
        expect=0,
        blocking=True,
    )
    authority = replace(
        report.context.authority, mandatory=report.context.authority.mandatory + (unmeasurable,)
    )
    context = replace(report.context, authority=authority)
    measures = mandatory_measures(report)
    obligation = gate_module._mandatory_obligation(report.runs, context, measures)
    assert not obligation.satisfied
    assert "AUE-MAN-TEST" in obligation.detail


def test_a_rendered_register_that_cannot_be_read_is_drift_and_never_a_match(
    report: GateReport, tmp_path: Path
) -> None:
    """Unreadable is a third answer beside "not rendered" and "different bytes", and it must
    read as drift: a register whose bytes cannot be compared has not been shown to be the
    product of the declaration, and treating it as a match would let an unreadable file certify
    itself."""
    written = render_registers(report, tmp_path)
    written[0].chmod(0o000)
    drift = replay_drift(report, tmp_path)
    assert any("unreadable" in entry for entry in drift), drift


def test_a_path_outside_the_measured_root_is_left_as_it_was_given(tmp_path: Path) -> None:
    """Rendered paths are made repository-relative so a register reproduces on any machine. A
    path that is not under the root has no relative form, and inventing one would put a
    fabricated location into the surface — so it is carried through unchanged."""

    assert _relative(tmp_path / "inside" / "register.md", tmp_path) == "inside/register.md"
    assert _relative("/elsewhere/register.md", tmp_path) == "/elsewhere/register.md"


def test_two_phases_declaring_one_owner_set_are_counted_as_a_duplicate_authority(
    report: GateReport,
) -> None:
    """Two positions answering to exactly the same owners are one authority wearing two names,
    and the measure exists so that collapse is visible rather than inferred from a reading of
    the declaration."""

    authority = report.context.authority
    first, second = authority.phases[0], authority.phases[1]
    collapsed = replace(
        authority,
        phases=tuple(
            replace(entry, owners=first.owners) if entry is second else entry
            for entry in authority.phases
        ),
    )
    doctored = replace(report, context=replace(report.context, authority=collapsed))
    assert mandatory_measures(doctored)["duplicate_authorities"] >= 1


def test_a_ledger_row_of_another_shape_contributes_no_history_identity(
    report: GateReport,
) -> None:
    """The history identities are read out of the projection the run produced. A row this reader
    cannot read must contribute nothing rather than a partial identity, because a partial one
    would count an object as recorded that nothing recorded."""

    baseline = mandatory_measures(report)
    projection = {
        **report.projection,
        "ledger": {
            **report.projection.get("ledger", {}),
            "records": [
                "not a record",
                {"subject": 7},
                *(report.projection.get("ledger", {}).get("records", []) or []),
            ],
        },
    }
    assert mandatory_measures(replace(report, projection=projection)) == baseline
    assert mandatory_measures(replace(report, projection={"ledger": "not a mapping"}))


def test_the_unknown_obligation_is_unsatisfied_when_no_run_carries_the_probe_subject(
    report: GateReport,
) -> None:
    """Selected by the probe's own subject rather than by an obligation identifier, so the
    register is not coupled to the gate's numbering — and with no run carrying that subject the
    obligation is unsatisfied rather than silently absent."""

    assert _unknown_satisfied(report) is True
    assert _unknown_satisfied(replace(report, runs=())) is False


def test_a_run_of_another_subject_does_not_answer_for_the_unknown_obligation(
    report: GateReport,
) -> None:
    """The obligation is about ONE declared subject. A run of some other candidate must not
    answer for it — neither by satisfying it nor by refusing it — or the measure would report
    whatever the last run happened to do."""

    other = replace(report.runs[0], subject_identity="a-subject-the-probe-never-names")
    assert _unknown_satisfied(replace(report, runs=(other,))) is False
