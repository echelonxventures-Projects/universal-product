"""UZX-000001 — the programme's own enforcement, and the cases that license it.

adr/0021 stated a principle, disclosed that nothing enforced it, and kept none for fourteen days.
The Zero-X programme reproduced that structure one level up: twelve residue classes governed by a
plan document with no gate. These tests are what makes the difference between a programme that is
well-tended and one that enforces its own discipline.
"""

from __future__ import annotations

import pytest

import engine.omega_infinite.direct_callers  # noqa: F401 - the caller loads what the register names
import engine.zero_class.entity_derivation  # noqa: F401 - ZX-02's detector, loaded for the same reason

# Imported through the PACKAGE, not the module. Ω-4 counted engine/zero_class/__init__.py as an
# unreachable artifact when this reached past it — code no import, plane or entry point touches —
# which is the same refusal engine/conformance drew when its tests bypassed its own package. A
# package nothing imports is a package nothing proves.
from engine.zero_class import (
    ZeroClassError,
    measure,
    stage_of,
    unenforced,
)
from engine.zero_class.measure import (
    DETECTED,
    RATCHETED,
    UNENFORCED_CEILING,
    _resolve,
    load_register,
)


@pytest.fixture(scope="module")
def results():
    return measure()


def test_the_register_declares_at_least_one_class(results) -> None:
    assert results


def test_no_class_is_governed_without_enforcement(results) -> None:
    """ZX-SELF: the register measures itself by the rule it applies to everything else.

    A register that exempted itself would repeat adr/0021 exactly, one level up — a rule that is
    right, with a measurement that does not reach the instrument stating it.
    """
    assert len(unenforced()) <= UNENFORCED_CEILING, (
        "a class is declared with a detector that cannot be resolved, run, or shown to fail in "
        f"both directions: {unenforced()}"
    )


def test_every_detected_class_proves_both_directions(results) -> None:
    """Stage 2 is not 'a detector exists'. It is 'a detector demonstrably fails correctly'."""
    for result in results:
        if result.stage >= DETECTED:
            assert result.catches, f"{result.class_id} cannot demonstrate it catches a violation"
            assert result.spares, f"{result.class_id} cannot demonstrate it spares a benign case"


def test_every_ratcheted_class_does_not_exceed_its_ceiling(results) -> None:
    for result in results:
        if result.stage >= RATCHETED:
            assert result.measured is not None and result.ceiling is not None
            assert result.measured <= result.ceiling, result.class_id


def test_a_detector_that_cannot_spare_is_refused() -> None:
    """THE FAILING CASE THIS INSTRUMENT RESTS ON.

    Without it, "no class is unenforced" could mean the rule holds or that nothing can fail it.
    A predicate that flags everything catches every violation and is still useless: false
    positives make a floor unreachable, because the last entries resist every migration and the
    only way to close the count is to declare modules that never had a defect. That is not
    hypothetical — the first bypass detector did exactly this, counting a declaration naming a
    tool as an invocation of it.
    """
    entry = {
        "class_id": "ZX-FAKE",
        "name": "a detector that flags everything",
        "definition": "constructed for this test",
        "detector": "engine.zero_class.measure.unenforced",
        "predicate": _flags_everything,
        "must_catch": ["x = 1\n"],
        "must_not_catch": ["y = 2\n"],
        "remedy": "PROPOSED",
    }
    result = stage_of(entry)
    assert result.catches is True
    assert result.spares is False, "a predicate that flags everything must fail the spare case"
    assert result.stage < DETECTED, "it must not reach DETECTED on catching alone"
    assert any("false positive" in reason for reason in result.reasons)


def test_a_class_with_no_detector_stays_declared() -> None:
    result = stage_of({"class_id": "ZX-NONE", "name": "undetected", "definition": "x"})
    assert result.stage < DETECTED
    assert any("no detector" in reason for reason in result.reasons)


def test_a_declared_but_undetected_class_says_why() -> None:
    """A class honestly at stage 1 is a different thing from one nobody thought of."""
    register = load_register()
    pending = register.get("declared_not_detected") or []
    assert pending, "the register claims full coverage; that claim needs evidence"
    for entry in pending:
        assert len(entry.get("why", "")) > 60, entry.get("class_id")


def test_the_register_never_declares_a_stage() -> None:
    """The register names classes and detectors. Stages are computed, never read."""
    register = load_register()
    for entry in register["classes"]:
        assert (
            "stage" not in entry
        ), f"{entry['class_id']} declares a stage it should be measured for"


def test_an_unloaded_detector_is_a_fault_not_a_pass() -> None:
    with pytest.raises(ZeroClassError, match="not loaded|no attribute"):
        stage_of(
            {
                "class_id": "ZX-GHOST",
                "name": "ghost",
                "definition": "x",
                "detector": "no.such.module.detector",
                "predicate": "no.such.module.predicate",
                "must_catch": ["a = 1\n"],
                "must_not_catch": ["b = 2\n"],
            }
        )


def _flags_everything(_path) -> bool:
    """A predicate with no discrimination, for the failing case above."""
    return True


def test_a_result_renders_every_field_it_measured(results) -> None:
    """A MEASUREMENT NOBODY CAN WRITE DOWN IS A MEASUREMENT NOBODY CAN COMPARE.

    Every assertion above reads the result object directly, so the render — the form the gate
    emits and evidence stores — had no caller. It carries the two directions under names that
    say what they PROVE rather than what the field is called, because "catches: false" beside
    "spares: false" is unreadable without knowing which is the worse failure.
    """
    rendered = results[0].to_dict()

    assert set(rendered) == {
        "class_id",
        "name",
        "stage",
        "measured",
        "ceiling",
        "proves_it_catches",
        "proves_it_spares",
        "reasons",
    }
    assert rendered["class_id"] == results[0].class_id
    assert rendered["proves_it_catches"] is results[0].catches
    assert isinstance(rendered["reasons"], list)


def test_cases_declared_with_no_predicate_to_run_them_against_are_reported() -> None:
    """CASES WITHOUT A PREDICATE ARE A REGISTER THAT LOOKS ENFORCED AND IS NOT.

    A class naming no predicate at all is silent — there is nothing to run and nothing to say.
    A class naming CASES but no predicate is the dangerous shape: it reads as a class whose
    detector has been proven in both directions, and nothing was run. Reporting the two apart
    is the difference between "not yet" and "someone thought this was done".
    """
    silent = stage_of({"class_id": "ZX-SILENT", "name": "silent", "definition": "x"})
    assert not any("no predicate is named" in reason for reason in silent.reasons)

    misleading = stage_of(
        {
            "class_id": "ZX-CASES-ONLY",
            "name": "cases with nothing to run them",
            "definition": "x",
            "must_catch": ["x = 1\n"],
            "must_not_catch": ["y = 2\n"],
        }
    )

    assert misleading.stage < DETECTED
    assert any("no predicate is named" in reason for reason in misleading.reasons)


def test_a_detector_that_cannot_catch_is_refused_and_says_which_case_escaped() -> None:
    """THE OTHER DIRECTION, AND THE ONE THE PROGRAMME NAMES AS MERELY USELESS.

    A predicate that flags nothing spares every benign case perfectly and catches no violation
    at all — so it would report a class as spare-proven while enforcing nothing. The finding
    names the INDEX of the case that escaped, because a detector with several must-catch cases
    is usually right about some of them, and "it cannot catch" does not say which.
    """
    result = stage_of(
        {
            "class_id": "ZX-BLIND",
            "name": "a detector that flags nothing",
            "definition": "constructed for this test",
            "detector": "engine.zero_class.measure.unenforced",
            "predicate": lambda _path: False,
            "must_catch": ["x = 1\n", "z = 3\n"],
            "must_not_catch": ["y = 2\n"],
        }
    )

    assert result.catches is False
    assert result.spares is True
    assert result.stage < DETECTED
    assert [r for r in result.reasons if "was not caught" in r] == [
        "must_catch[0] was not caught",
        "must_catch[1] was not caught",
    ]


def test_a_class_that_is_named_and_not_defined_says_so() -> None:
    """A DEFINITION IS WHAT MAKES A CLASS DECLARED AT ALL.

    Stage 1 is "declared", and a class with no definition has not reached it — it is a name in
    a register. The reason is emitted rather than left to be inferred from the stage, because a
    stage of 0 beside a stage of 1 tells a reader nothing about which of the two things is
    missing.
    """
    result = stage_of({"class_id": "ZX-NAMEONLY", "name": "named and not declared"})

    assert result.stage == 0
    assert any("the class is named and not declared" in reason for reason in result.reasons)


def test_a_detector_that_raises_keeps_its_class_declared_and_records_the_fault() -> None:
    """A DETECTOR THAT BLOWS UP IS NOT A DETECTOR THAT FOUND NOTHING.

    The resolvable-but-broken case had no test: the unresolvable one raises a typed error and
    is handled above, while a detector that resolves and then fails is caught deliberately
    broadly, because ANY failure keeps the class at DECLARED. Letting it escape would make one
    broken detector cost the measurement of every other class; treating it as zero findings
    would ratchet a class on the strength of an exception.
    """
    # A DOTTED NAME that resolves and then fails when its result is measured. The detector is
    # named rather than handed over, because a detector is DATA in the register and only the
    # predicate may be a callable — so a broken detector arrives exactly like this one.
    result = stage_of(
        {
            "class_id": "ZX-BROKEN",
            "name": "a detector whose result cannot be measured",
            "definition": "constructed for this test",
            "detector": "engine.zero_class.measure.ZeroClassError",
            "predicate": lambda path: path.name.startswith("catch"),
            "must_catch": ["x = 1\n"],
            "must_not_catch": ["y = 2\n"],
        }
    )

    assert result.measured is None
    assert result.stage < DETECTED
    assert any("detector raised: TypeError" in reason for reason in result.reasons)


def test_a_ceiling_that_cannot_be_resolved_is_reported_and_does_not_ratchet() -> None:
    """A CEILING NAMES A NUMBER, AND A NAME THAT RESOLVES TO SOMETHING ELSE IS NOT ONE.

    Every ceiling in the register resolves to an integer, so the arm answering for one that
    does not had no case. It is the difference between a class that is ratcheted and one that
    only appears to be: without the guard the failure would either escape as a TypeError from
    inside the measurement, or — worse — leave ``ceiling`` unset and let the comparison be
    skipped silently, reporting the class at ATTRIBUTED with no indication that its bound was
    unreadable.
    """
    result = stage_of(
        {
            "class_id": "ZX-NOCEILING",
            "name": "a ceiling that is not a number",
            "definition": "constructed for this test",
            "detector": "engine.zero_class.measure.UNENFORCED_CEILING",
            "predicate": lambda path: path.name.startswith("catch"),
            "must_catch": ["x = 1\n"],
            "must_not_catch": ["y = 2\n"],
            "ceiling": "engine.zero_class.measure.ZeroClassError",
        }
    )

    assert result.ceiling is None
    assert result.stage < RATCHETED
    assert any("ceiling unresolvable" in reason for reason in result.reasons)


def test_a_register_that_is_absent_unparseable_or_empty_is_a_fault(tmp_path) -> None:
    """THE REGISTER IS THE SUBJECT, AND AN UNUSABLE SUBJECT IS A FAULT AND NEVER A VERDICT.

    Three ways for the register to be unusable, none of which had a case because the packaged
    one is always present and well formed. Each must raise rather than return an empty
    measurement, because "no class is unenforced" computed over zero classes is a green tick
    that means nothing was measured — which is precisely the structure this programme exists
    to refuse.
    """
    with pytest.raises(ZeroClassError, match="register is absent"):
        load_register(str(tmp_path / "no-such-register.json"))

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{ truncated", encoding="utf-8")
    with pytest.raises(ZeroClassError, match="not valid JSON"):
        load_register(str(malformed))

    empty = tmp_path / "empty.json"
    empty.write_text('{"classes": []}', encoding="utf-8")
    with pytest.raises(ZeroClassError, match="declares no class"):
        measure(str(empty))


def test_a_name_whose_module_is_loaded_but_whose_attribute_is_not_there_is_a_fault() -> None:
    """ "NOT LOADED" AND "NO SUCH ATTRIBUTE" ARE DIFFERENT FAULTS AND THE MESSAGE SAYS WHICH.

    Resolution walks the dotted name from the longest prefix down, so a name whose module is
    absent stops at "not loaded" — the arm the ghost-detector case reaches. This is the other
    one: the module IS loaded and the attribute inside it is misspelled or gone, which is what
    a register left behind by a rename looks like. Collapsing the two would send a reader
    looking for a missing import when the import is fine and the name has moved.
    """
    with pytest.raises(ZeroClassError, match="no attribute no_such_detector"):
        _resolve("engine.zero_class.measure.no_such_detector")

    with pytest.raises(ZeroClassError, match="not loaded"):
        _resolve("no.such.module.detector")

    # Through the measurement the fault is a REASON rather than an escape, because one
    # unresolvable detector must not cost the measurement of every other class.
    renamed = stage_of(
        {
            "class_id": "ZX-RENAMED",
            "name": "a detector left behind by a rename",
            "definition": "constructed for this test",
            "detector": "engine.zero_class.measure.no_such_detector",
        }
    )
    assert renamed.stage < DETECTED
    assert any("no attribute no_such_detector" in reason for reason in renamed.reasons)
