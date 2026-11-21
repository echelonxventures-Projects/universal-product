"""UAC-000001 — the harness measured, and the reason it is measured rather than trusted.

Ω-4 counted `engine/conformance` as an unreachable artifact the moment it landed: code no
import, plane or entry point reaches. That was correct and is the point of the metric — an
instrument nothing invokes proves nothing, however well it is written. These tests are what
reach it, and `make conformance` is the operator's path to the same measurement.
"""

from __future__ import annotations

import pathlib

import pytest

import engine.uckp.execution  # noqa: F401 - the caller loads what the register names
import engine.uckp.persistence  # noqa: F401
from engine.conformance import (
    PROVEN,
    SINGLE,
    ConformanceError,
    measure,
    measure_axis,
)
from engine.conformance.measure import (
    DECLARED_ABSENT,
    ENVELOPE_ONLY,
    REGISTER_PATH,
    load_register,
)


def _axis(results, name):
    return next(r for r in results if r.axis == name)


@pytest.fixture(scope="module")
def results():
    return measure(REGISTER_PATH)


def test_the_register_declares_at_least_one_axis(results) -> None:
    assert results, "a register declaring no axis is a fault, not an empty measurement"


def test_persistence_is_proven_because_its_contract_can_refuse_a_placeholder(results) -> None:
    """The axis that licenses the harness: it passes for a reason that can fail.

    PersistenceAdapter demands write() then read() and compares universe digests, so a
    mechanism that records nothing cannot return it. A pass here is evidence; that is what
    makes this axis the right one to validate the instrument against.
    """
    axis = _axis(results, "persistence")
    assert axis.disposition == PROVEN
    assert len(axis.distinct) >= 2
    assert axis.discriminating is True
    assert axis.shared_bodies == ()


def test_execution_is_single_and_no_longer_envelope_only(results) -> None:
    """The verdict this suite was written to make sayable, and then the fix that moved it.

    WRITTEN AS ENVELOPE_ONLY, AND THAT WAS CORRECT AT THE TIME. engine/uckp/execution.py declared
    ten technologies and verify_execution_interchangeable passed over all of them, because no
    adapter overrode `execute` — every call reached the same resolve_operation that produced the
    expected digest, so the check compared Python's answer to Python's answer once per adapter
    name and could not refuse anything.

    THE CONTRACT NOW DISCRIMINATES, so the axis moved. `computes()` defaults to False, claiming
    computation is an act rather than an inheritance, and a claimant returning a different digest
    is named in failures. One adapter claims it. Nine are transcription targets, reported as such
    rather than counted as agreement, and deliberately not deleted: UCKP-ART-17 admits an unknown
    future category by registration, and those declarations are that mechanism working.

    SINGLE IS NOT PROVEN, AND THE TEST SAYS SO. One implementation is an assumption — adr/0039's
    own bar — and this asserts the axis has not quietly been credited with more than it earned.
    """
    axis = _axis(results, "execution")
    assert axis.disposition == SINGLE, "the axis is not PROVEN; one implementation is an assumption"
    assert axis.discriminating is True, "the contract must be able to refuse a false claimant"
    assert len(axis.distinct) == 1


def test_a_second_implementation_is_now_provable_rather_than_assertable(results) -> None:
    """Why the move from ENVELOPE_ONLY to SINGLE is progress and not a relabelling.

    Under ENVELOPE_ONLY no number of implementations could be distinguished, so a Rust engine
    would have passed the interchangeability check by transcribing and computing nothing. The
    axis now carries a discriminator, which is exactly the bar a second implementation must clear
    to move it to PROVEN — by evidence rather than by declaration.
    """
    axis = _axis(results, "execution")
    assert axis.discriminating, "without a discriminator, a second implementation proves nothing"
    assert axis.disposition != PROVEN, "two claimants are required, and there is one"


def test_an_unloaded_contract_is_unmeasurable_and_never_silently_skipped() -> None:
    """The harness imports nothing, so an unloaded contract must say so rather than vanish."""
    with pytest.raises(ConformanceError, match="not loaded|cannot be measured"):
        measure_axis({"axis": "absent", "contract": "no.such.module.Contract"})


def test_the_harness_names_no_technology() -> None:
    """The instrument that measures hardcoding may not hardcode what it measures.

    A technology named in the harness would make one axis privileged and the register
    advisory. Axis modules appear only under __main__, which decides nothing.
    """

    source = pathlib.Path("engine/conformance/measure.py").read_text(encoding="utf-8")
    body = source.split('if __name__ == "__main__":')[0]
    for token in ("python", "rust", "golang", "sqlite", "postgres", "kubernetes", "git"):
        assert token not in body.lower(), f"the harness names a technology: {token}"


def test_every_result_renders_the_measurement_behind_its_disposition(results) -> None:
    """A DISPOSITION WITHOUT ITS WORKING IS A LABEL, and the render is where the working goes.

    Every assertion above reads the result object, so the form `make conformance` emits and
    evidence stores had no caller. It carries the implementations, the DISTINCT ones and the
    ones sharing a sibling's body as three separate lists, because the difference between them
    is the whole judgement: an implementation inheriting another's body is one implementation
    wearing two names, and counting it would make an interchangeability test unfailable.
    """
    rendered = _axis(results, "persistence").to_dict()

    assert set(rendered) == {
        "axis",
        "contract",
        "implementations",
        "distinct_implementations",
        "shared_bodies",
        "discriminating_contract",
        "disposition",
        "reason",
    }
    assert rendered["axis"] == "persistence"
    assert rendered["disposition"] == PROVEN
    assert rendered["reason"]


def test_a_reference_whose_module_is_loaded_but_whose_name_is_gone_is_a_fault() -> None:
    """ "NOT LOADED" AND "DECLARES NO SUCH NAME" ARE DIFFERENT FAULTS.

    The unloaded case was tested. This is the other: the module IS loaded and the contract name
    inside it has moved or been misspelled — what a register left behind by a rename looks like.
    The message names the PREFIX that was found, so a reader is sent to the module that exists
    rather than to a missing import that does not.
    """
    with pytest.raises(ConformanceError, match="declares no NoSuchContract"):
        measure_axis({"axis": "renamed", "contract": "engine.uckp.persistence.NoSuchContract"})


def test_a_contract_reference_naming_something_that_is_not_a_class_is_a_fault() -> None:
    """AN AXIS IS A CONTRACT, AND A CONTRACT IS A CLASS.

    Both declared axes name real classes, so the check had no case — and it is what stops the
    implementation search from being run against a function or a constant, where the subclass
    walk would raise from inside the measurement instead of naming the register entry that is
    wrong. A fault here is the register's, not the code's, and the message says which axis.
    """
    with pytest.raises(ConformanceError, match="not-a-class: .* is not a class"):
        measure_axis({"axis": "not-a-class", "contract": "engine.uckp.persistence.__name__"})


def test_an_axis_declared_absent_is_reported_as_declared_and_not_measured() -> None:
    """A DECLARED ABSENCE IS AN ANSWER AND MUST NOT BE COUNTED AS A MEASUREMENT.

    Neither declared axis is absent, so this disposition had never been produced. It is how an
    axis whose contract does not exist yet stays in the register with a written reason instead
    of being deleted — and the reason is carried through, because an absence with no reason is
    indistinguishable from an oversight.
    """
    result = measure_axis(
        {
            "axis": "future",
            "contract": "engine.uckp.persistence.PersistenceAdapter",
            "declared_absent": True,
            "$absence_reason": "no second mechanism has been written for this axis yet",
        }
    )

    assert result.disposition == DECLARED_ABSENT
    assert result.reason == "no second mechanism has been written for this axis yet"

    unexplained = measure_axis(
        {
            "axis": "future",
            "contract": "engine.uckp.persistence.PersistenceAdapter",
            "declared_absent": True,
        }
    )
    assert unexplained.reason == "declared absent"


def test_a_contract_that_demands_no_answer_is_envelope_only_however_many_implement_it() -> None:
    """THE VERDICT THIS HARNESS EXISTS TO MAKE SAYABLE, and it had no case left.

    Both registered axes now carry a discriminator, so ENVELOPE_ONLY — the disposition the
    execution axis USED to hold, and the whole reason the instrument was written — became
    unreachable through the register. Without a discriminator no number of implementations can
    be distinguished by any case written against the contract, so a second engine would pass an
    interchangeability check by transcribing and computing nothing. The count is irrelevant
    here on purpose: the judgement is about the CONTRACT, not about how many classes subclass
    it.
    """
    result = measure_axis(
        {
            "axis": "envelope",
            "contract": "engine.uckp.persistence.PersistenceAdapter",
            "abstract_methods": ["write", "read"],
        }
    )

    assert result.disposition == ENVELOPE_ONLY
    assert result.discriminating is False
    assert "no number of implementations can be distinguished" in result.reason
    assert len(result.distinct) >= 2, "and it is ENVELOPE_ONLY despite them"


def test_a_contract_no_implementation_defines_itself_is_envelope_only() -> None:
    """DISTINCTNESS IS ABOUT WHO DEFINES THE BODY, NOT WHO CARRIES THE NAME.

    The zero-distinct arm had never run: every implementation of both declared contracts
    defines its own methods. It is reached by naming a method NO class in any implementation's
    MRO supplies — which is what a register entry looks like after a contract's method is
    renamed and the entry is not. Every implementation is then credited with defining nothing,
    the axis is an envelope again however long the list is, and the lookup that answers "who
    defines this" returns the empty string rather than guessing at the first base.
    """
    result = measure_axis(
        {
            "axis": "renamed-method",
            "contract": "engine.uckp.persistence.PersistenceAdapter",
            "abstract_methods": ["a_method_no_implementation_supplies"],
            "discriminator": "engine.uckp.persistence.PersistenceAdapter.read",
        }
    )

    assert result.distinct == ()
    assert result.shared_bodies
    assert result.disposition == ENVELOPE_ONLY
    assert result.reason == "no implementation defines the contract itself"


def test_a_register_that_is_absent_unparseable_or_empty_is_a_fault(tmp_path) -> None:
    """THE REGISTER IS THE SUBJECT, AND AN UNUSABLE SUBJECT IS A FAULT AND NEVER A VERDICT.

    Three ways to be unusable, none of which had a case because the packaged register is always
    present and well formed. Returning an empty measurement instead would report "no axis fails"
    over zero axes — a green tick meaning nothing was measured, which is the exact structure
    this harness was written to refuse.
    """
    with pytest.raises(ConformanceError, match="register is absent"):
        load_register(str(tmp_path / "no-such-register.json"))

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{ truncated", encoding="utf-8")
    with pytest.raises(ConformanceError, match="not valid JSON"):
        load_register(str(malformed))

    empty = tmp_path / "empty.json"
    empty.write_text('{"axes": []}', encoding="utf-8")
    with pytest.raises(ConformanceError, match="declares no axis"):
        measure(str(empty))
