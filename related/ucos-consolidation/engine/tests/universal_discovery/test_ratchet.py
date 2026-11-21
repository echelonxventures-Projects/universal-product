"""Ω-4 — a ratchet is a DIRECTION. Improving costs nothing; regressing costs a written reason."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.universal_discovery import ratchet
from engine.universal_discovery.model import (
    CONVERGENT,
    DENSITY,
    ENTROPY,
    HELD,
    IMPROVED,
    JUSTIFIED,
    MONOTONIC,
    REGRESSED,
    SEEDED,
    STALLED,
    OmegaError,
)


def _state(**best: float) -> ratchet.Ratchet:
    return ratchet.Ratchet(
        {
            "best": best,
            "kinds": {metric: MONOTONIC for metric in best},
            "holds": {},
            "justifications": [],
        }
    )


# ---------------------------------------------------------------------------------- comparison


def test_a_first_observation_is_seeded_and_becomes_the_bound() -> None:
    """Seeding is not a free pass: the first observation is the last one that costs nothing."""
    observation = ratchet.Ratchet({}).observe("m", MONOTONIC, 42.0, "subject")
    assert observation.verdict == SEEDED
    assert observation.best is None
    assert not observation.refused


def test_an_improvement_needs_no_edit_anywhere() -> None:
    """THE DEFECT THIS REPLACES, stated as a test.

    The previous two-sided ceiling REFUSED a measurement below the ceiling, so repaying debt closed
    the gate until somebody committed the new number. It fired that way on the commit that
    introduced Ω: the denominator improved from 65 to 64 and the gate refused the improvement.
    """
    observation = _state(m=65.0).observe("m", MONOTONIC, 64.0, "subject")
    assert observation.verdict == IMPROVED
    assert not observation.refused


def test_holding_at_the_best_is_accepted() -> None:
    assert _state(m=64.0).observe("m", MONOTONIC, 64.0, "subject").verdict == HELD


def test_a_regression_with_no_reason_is_refused() -> None:
    observation = _state(m=64.0).observe("m", MONOTONIC, 65.0, "subject")
    assert observation.verdict == REGRESSED
    assert observation.refused


def test_a_regression_with_a_written_reason_is_permitted_once() -> None:
    state = ratchet.Ratchet(
        {
            "best": {"m": 64.0},
            "kinds": {"m": MONOTONIC},
            "justifications": [
                {"metric": "m", "reason": "a layer was admitted, so the surface grew"}
            ],
        }
    )
    observation = state.observe("m", MONOTONIC, 70.0, "subject")
    assert observation.verdict == JUSTIFIED
    assert not observation.refused
    assert "layer was admitted" in observation.justification


def test_a_justification_never_moves_the_bound() -> None:
    """The difference between a justification and a new ceiling.

    Ratifying a regression requires the metric to actually improve again, not a note explaining
    that it will not.
    """
    state = ratchet.Ratchet(
        {
            "best": {"m": 64.0},
            "kinds": {"m": MONOTONIC},
            "justifications": [{"metric": "m", "reason": "argued"}],
        }
    )
    sealed = state.sealed([state.observe("m", MONOTONIC, 70.0, "subject")])
    assert sealed["best"]["m"] == 64.0, "a justified regression became the new normal"


def test_an_unexplained_justification_is_refused_at_load() -> None:
    with pytest.raises(OmegaError, match="states no reason"):
        ratchet.Ratchet({"justifications": [{"metric": "m", "reason": "   "}]})


def test_an_unknown_ratchet_kind_is_refused() -> None:
    with pytest.raises(OmegaError, match="not one of"):
        ratchet.Ratchet({}).observe("m", "WHATEVER", 1.0, "subject")


def test_a_metric_that_changes_kind_is_a_different_metric() -> None:
    state = ratchet.Ratchet({"best": {"m": 1.0}, "kinds": {"m": MONOTONIC}})
    with pytest.raises(OmegaError, match="changes kind"):
        state.observe("m", CONVERGENT, 1.0, "subject")


# ------------------------------------------------------------------------------------ convergence


def test_a_convergent_metric_held_too_long_at_a_non_zero_value_is_stalled() -> None:
    """What stops an exemption class from quietly becoming a settled convention."""
    state = ratchet.Ratchet(
        {
            "best": {"m": 5.0},
            "kinds": {"m": CONVERGENT},
            "holds": {"m": ratchet.STALL_OBSERVATIONS - 1},
        }
    )
    observation = state.observe("m", CONVERGENT, 5.0, "subject")
    assert observation.verdict == STALLED
    assert observation.refused


def test_a_convergent_metric_at_zero_never_stalls() -> None:
    """Zero is the target, so holding there is success rather than stagnation."""
    state = ratchet.Ratchet({"best": {"m": 0.0}, "kinds": {"m": CONVERGENT}, "holds": {"m": 99}})
    assert state.observe("m", CONVERGENT, 0.0, "subject").verdict == HELD


def test_a_monotonic_metric_never_stalls() -> None:
    """Zero is NOT the target for a disclosure ratchet; demanding convergence demands a lie."""
    state = ratchet.Ratchet({"best": {"m": 10.0}, "kinds": {"m": MONOTONIC}, "holds": {"m": 99}})
    assert state.observe("m", MONOTONIC, 10.0, "subject").verdict == HELD


def test_a_stall_is_accepted_by_a_declared_floor_and_not_by_a_justification() -> None:
    """A CONVERGENT metric may legitimately bottom out above zero, and the two mechanisms differ.

    THE FLAW THIS SEPARATION FIXES. When one ``justifications`` entry served both purposes, a single
    written sentence about an unreachable zero also excused unlimited growth on that metric forever
    — the mechanism meant to argue about a floor silently became a permanent regression permit. A
    floor now excuses only the STALL.
    """
    base = {
        "best": {"m": 2.0},
        "kinds": {"m": CONVERGENT},
        "holds": {"m": ratchet.STALL_OBSERVATIONS},
    }
    unargued = ratchet.Ratchet(dict(base))
    assert unargued.observe("m", CONVERGENT, 2.0, "s").verdict == STALLED

    floored = ratchet.Ratchet(
        {**base, "floors": [{"metric": "m", "value": 2, "reason": "both are root initialisers"}]}
    )
    accepted = floored.observe("m", CONVERGENT, 2.0, "s")
    assert accepted.verdict == JUSTIFIED
    assert not accepted.refused
    assert "root initialisers" in accepted.justification


def test_a_floor_never_excuses_a_regression() -> None:
    """At the floor it is accepted; one above the best the SAME declaration refuses."""
    floored = ratchet.Ratchet(
        {
            "best": {"m": 33.0},
            "kinds": {"m": CONVERGENT},
            "holds": {"m": ratchet.STALL_OBSERVATIONS},
            "floors": [{"metric": "m", "value": 33, "reason": "declared open finding"}],
        }
    )
    assert floored.observe("m", CONVERGENT, 33.0, "s").verdict == JUSTIFIED
    regressed = floored.observe("m", CONVERGENT, 34.0, "s")
    assert regressed.verdict == REGRESSED
    assert regressed.refused


def test_a_floor_with_no_reason_is_refused() -> None:
    with pytest.raises(OmegaError, match="ceiling wearing a different name"):
        ratchet.Ratchet({"floors": [{"metric": "m", "value": 1, "reason": " "}]})


def test_a_floor_overtaken_by_the_work_is_refused_as_stale() -> None:
    """The two-direction discipline the coverage-exemption register uses, for the same reason."""
    state = ratchet.Ratchet(
        {
            "best": {"m": 5.0},
            "kinds": {"m": CONVERGENT},
            "floors": [{"metric": "m", "value": 5, "reason": "argued"}],
        }
    )
    with pytest.raises(OmegaError, match="overtaken"):
        ratchet.assert_floors_live(state, [state.observe("m", CONVERGENT, 3.0, "s")])


def test_a_floor_naming_no_measured_metric_is_refused() -> None:
    state = ratchet.Ratchet({"floors": [{"metric": "gone", "value": 1, "reason": "argued"}]})
    with pytest.raises(OmegaError, match="argue about nothing"):
        ratchet.assert_floors_live(state, [])


def test_a_live_floor_passes_the_same_check() -> None:
    state = ratchet.Ratchet(
        {
            "best": {"m": 5.0},
            "kinds": {"m": CONVERGENT},
            "floors": [{"metric": "m", "value": 5, "reason": "argued"}],
        }
    )
    ratchet.assert_floors_live(state, [state.observe("m", CONVERGENT, 5.0, "s")])


def test_floors_survive_a_seal_and_a_round_trip(tmp_path: Path) -> None:
    state = ratchet.Ratchet(
        {
            "best": {"m": 5.0},
            "kinds": {"m": CONVERGENT},
            "floors": [{"metric": "m", "value": 5, "reason": "argued"}],
        }
    )
    path = tmp_path / "state.json"
    ratchet.write(str(path), state.sealed([state.observe("m", CONVERGENT, 5.0, "s")]))
    assert ratchet.load(str(path)).floors == {"m": (5.0, "argued")}


def test_a_re_seed_record_survives_every_subsequent_seal(tmp_path: Path) -> None:
    """THE LAUNDERING THIS CLOSES, and it was measured rather than imagined.

    Dropping a metric's bound is legitimate when a measurement DEFECT is fixed: the old number
    answers a different question, and leaving it in place would make the gate refuse forever
    against a value nobody can reach. It is also the one operation here that can make a refusal
    disappear. The first version of ``sealed()`` did not carry ``corrections`` forward, so the very
    next seal erased the record — the drop stayed, the explanation did not, and the diff that would
    have shown it was gone.
    """
    state = ratchet.Ratchet(
        {
            "best": {"m": 5.0},
            "kinds": {"m": CONVERGENT},
            "corrections": [{"metric": "m", "reason": "the basename match was wrong"}],
        }
    )
    path = tmp_path / "state.json"
    ratchet.write(str(path), state.sealed([state.observe("m", CONVERGENT, 5.0, "s")]))
    first = ratchet.load(str(path))
    assert first.corrections == {"m": "the basename match was wrong"}

    # And through a second, unrelated seal.
    ratchet.write(str(path), first.sealed([first.observe("m", CONVERGENT, 4.0, "s")]))
    assert ratchet.load(str(path)).corrections == {"m": "the basename match was wrong"}


def test_a_re_seed_with_no_written_correction_is_refused() -> None:
    with pytest.raises(OmegaError, match="indistinguishable from a bound dropped to pass"):
        ratchet.Ratchet({"corrections": [{"metric": "m", "reason": "  "}]})


def test_an_improvement_resets_the_hold_counter() -> None:
    state = ratchet.Ratchet({"best": {"m": 5.0}, "kinds": {"m": CONVERGENT}, "holds": {"m": 4}})
    sealed = state.sealed([state.observe("m", CONVERGENT, 4.0, "subject")])
    assert sealed["holds"]["m"] == 0


def test_holding_increments_the_hold_counter() -> None:
    state = ratchet.Ratchet({"best": {"m": 5.0}, "kinds": {"m": CONVERGENT}, "holds": {"m": 1}})
    sealed = state.sealed([state.observe("m", CONVERGENT, 5.0, "subject")])
    assert sealed["holds"]["m"] == 2


# ------------------------------------------------------------------------------------- sealing


def test_sealing_only_ever_moves_a_bound_downward() -> None:
    state = _state(m=10.0)
    sealed = state.sealed([state.observe("m", MONOTONIC, 3.0, "subject")])
    assert sealed["best"]["m"] == 3.0


def test_a_sealed_document_is_self_describing_and_deterministic(tmp_path: Path) -> None:
    state = ratchet.Ratchet({})
    document = state.sealed([state.observe("m", MONOTONIC, 1.0, "subject")])
    assert document["schema"] == ratchet.SCHEMA
    assert "how_to_read" in document
    path = tmp_path / "nested" / "omega-ratchet.json"
    ratchet.write(str(path), document)
    first = path.read_text(encoding="utf-8")
    ratchet.write(str(path), document)
    assert path.read_text(encoding="utf-8") == first
    assert first.endswith("\n")
    assert json.loads(first)["best"]["m"] == 1.0


def test_a_hand_inflated_bound_is_refused() -> None:
    """THE ATTACK: raise ``best`` by hand and every regression becomes compliant, forever."""
    state = ratchet.Ratchet({})
    observations = [state.observe("m", MONOTONIC, 5.0, "subject")]
    document = state.sealed(observations)
    document["best"]["m"] = 500.0  # type: ignore[index]
    with pytest.raises(OmegaError, match="edited rather than measured"):
        ratchet.assert_sealed_from_measurement(document, observations)


def test_a_correctly_sealed_document_passes_the_same_check() -> None:
    state = ratchet.Ratchet({})
    observations = [state.observe("m", MONOTONIC, 5.0, "subject")]
    ratchet.assert_sealed_from_measurement(state.sealed(observations), observations)


# --------------------------------------------------------------------------------------- loading


def test_a_missing_state_file_seeds_rather_than_faulting(tmp_path: Path) -> None:
    """ "Not measured yet" is a real state with a safe answer."""
    assert ratchet.load(str(tmp_path / "absent.json")).best == {}


def test_a_corrupt_state_file_is_a_fault(tmp_path: Path) -> None:
    """ "Measured and unreadable" is a state in which every comparison would silently pass."""
    path = tmp_path / "omega-ratchet.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(OmegaError, match="permits every regression"):
        ratchet.load(str(path))


def test_a_state_file_of_the_wrong_schema_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "omega-ratchet.json"
    path.write_text(json.dumps({"schema": "something-else", "best": {}}), encoding="utf-8")
    with pytest.raises(OmegaError, match="refusing to compare"):
        ratchet.load(str(path))


def test_a_round_trip_preserves_every_bound(tmp_path: Path) -> None:
    path = tmp_path / "omega-ratchet.json"
    state = ratchet.Ratchet({})
    observations = [
        state.observe("a", MONOTONIC, 1.0, "s"),
        state.observe("b", CONVERGENT, 2.0, "s"),
    ]
    ratchet.write(str(path), state.sealed(observations))
    reloaded = ratchet.load(str(path))
    assert reloaded.best == {"a": 1.0, "b": 2.0}
    assert reloaded.kinds == {"a": MONOTONIC, "b": CONVERGENT}


# ---------------------------------------------------------------------------------------- ratios


def test_a_density_ratio_is_scale_free() -> None:
    """The property that makes growth unable to breach a bound — or to flatter one."""
    assert ratchet.ratio(1, 10) == ratchet.ratio(1000, 10000)


def test_a_ratio_over_an_empty_denominator_is_a_fault() -> None:
    """It would report perfection for an empty repository."""
    with pytest.raises(OmegaError, match="empty denominator"):
        ratchet.ratio(0, 0)


def test_the_ratio_kinds_are_named_in_one_place() -> None:
    assert ratchet.RATIO_KINDS == frozenset({DENSITY, ENTROPY})


def test_refusals_selects_exactly_the_blocking_verdicts() -> None:
    state = _state(m=1.0, n=1.0)
    observations = [
        state.observe("m", MONOTONIC, 2.0, "s"),
        state.observe("n", MONOTONIC, 1.0, "s"),
    ]
    assert [o.metric for o in ratchet.refusals(observations)] == ["m"]


def test_an_observation_renders_its_ratio_when_it_has_one() -> None:
    state = ratchet.Ratchet({})
    observation = state.observe("d", DENSITY, 0.1, "s", ratio=(1, 10))
    record = observation.as_record()
    assert record["ratio"] == {"numerator": 1, "denominator": 10}
    assert "justification" not in record
