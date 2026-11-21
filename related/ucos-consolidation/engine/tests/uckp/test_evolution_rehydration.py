"""Rehydration of the Article 14 evolution ledger — the inverse of its own projection.

Repository truth before this suite: the ledger could project itself to a canonical
document and had no loader. A published evolution history was therefore unfalsifiable
between processes — the append-only rules were applied once, at write time, and nothing
re-applied them at read time. These tests pin the property that fixes that: loading is a
verification, and a tampered history is refused on load with the same error the same code
path would have raised on write.

This suite is the evidence bound by ``00-MASTER/UAUE-000001`` finding ``AUE-SELF-01``.
"""

from __future__ import annotations

import pytest

from engine.uckp.canonical import canonical_json
from engine.uckp.errors import EvolutionError
from engine.uckp.evolution import (
    CYCLE_LENGTH,
    EVOLUTION_CYCLE,
    LEDGER_SCHEMA,
    LEDGER_VERSION,
    EvolutionLedger,
    EvolutionRecord,
    EvolutionStage,
)


def _cycle(subject: str = "uaue.subject", cycles: int = 1) -> EvolutionLedger:
    """A ledger carrying ``cycles`` complete lawful cycles."""
    ledger = EvolutionLedger()
    for cycle in range(cycles):
        for stage in EVOLUTION_CYCLE:
            ledger.append(
                EvolutionRecord(
                    cycle=cycle,
                    stage=stage,
                    subject=subject,
                    outcome="satisfied",
                    digest=f"{subject}:{cycle}:{stage.value}",
                    findings=() if stage is not EVOLUTION_CYCLE[0] else ("opened",),
                )
            )
    return ledger


def test_schema_and_version_are_named_once() -> None:
    """The projection announces the form the loader accepts, from one constant."""
    document = EvolutionLedger().to_document()
    assert document["schema"] == LEDGER_SCHEMA
    assert document["version"] == LEDGER_VERSION


def test_round_trip_is_a_fixed_point() -> None:
    """Projecting, loading and re-projecting yields byte-identical canonical bytes."""
    original = _cycle(cycles=2)
    reloaded = EvolutionLedger.from_document(original.to_document())

    assert len(reloaded) == len(original) == CYCLE_LENGTH * 2
    assert reloaded.fingerprint() == original.fingerprint()
    assert canonical_json(reloaded.to_document()) == canonical_json(original.to_document())
    assert reloaded.records() == original.records()


def test_rehydration_preserves_cycle_position_and_findings() -> None:
    """The loaded ledger continues the cycle exactly where the document left it."""
    original = _cycle(cycles=1)
    reloaded = EvolutionLedger.from_document(original.to_document())

    assert reloaded.expected_stage() is original.expected_stage()
    assert reloaded.current_stage() is EVOLUTION_CYCLE[-1]
    assert reloaded.cycles() == 1
    assert reloaded.completed_cycles() == 1
    assert reloaded.findings() == original.findings()
    assert reloaded.is_terminated() is False


def test_an_empty_ledger_round_trips_to_the_opening_stage() -> None:
    reloaded = EvolutionLedger.from_document(EvolutionLedger().to_document())

    assert len(reloaded) == 0
    assert reloaded.expected_stage() is EVOLUTION_CYCLE[0]
    assert reloaded.current_stage() is None


def test_a_loaded_ledger_still_appends() -> None:
    """Rehydration produces a live ledger, not a frozen report of one."""
    reloaded = EvolutionLedger.from_document(_cycle(cycles=1).to_document())
    appended = reloaded.append(
        EvolutionRecord(
            cycle=1,
            stage=EVOLUTION_CYCLE[0],
            subject="uaue.subject",
            outcome="satisfied",
            digest="continued",
        )
    )

    assert appended.cycle == 1
    assert reloaded.cycles() == 2


def test_a_reordered_history_is_refused_on_load() -> None:
    """Tampering that skips a stage is refused by the same rule that refused it on write."""
    document = _cycle(cycles=1).to_document()
    records = list(document["records"])  # type: ignore[arg-type]
    records[1], records[2] = records[2], records[1]
    document["records"] = records

    with pytest.raises(EvolutionError, match="may not be skipped or reordered"):
        EvolutionLedger.from_document(document)


def test_a_truncated_history_that_no_longer_opens_the_cycle_is_refused() -> None:
    """A history whose first record is not the opening stage never began lawfully."""
    document = _cycle(cycles=1).to_document()
    document["records"] = list(document["records"])[3:]  # type: ignore[arg-type]

    with pytest.raises(EvolutionError, match="must begin at the first stage"):
        EvolutionLedger.from_document(document)


def test_a_renumbered_cycle_is_refused() -> None:
    document = _cycle(cycles=2).to_document()
    records = list(document["records"])  # type: ignore[arg-type]
    records[CYCLE_LENGTH]["cycle"] = 7
    document["records"] = records

    with pytest.raises(EvolutionError, match="cycle must advance exactly once"):
        EvolutionLedger.from_document(document)


def test_a_document_of_another_schema_is_refused() -> None:
    """A loader that accepts anything carrying a records array is not a loader."""
    with pytest.raises(EvolutionError, match="not an evolution ledger"):
        EvolutionLedger.from_document({"schema": "ucos-something-else", "records": []})


def test_a_document_with_no_schema_is_refused() -> None:
    with pytest.raises(EvolutionError, match="not an evolution ledger"):
        EvolutionLedger.from_document({"records": []})


def test_a_non_mapping_document_is_refused() -> None:
    with pytest.raises(EvolutionError, match="must be a mapping"):
        EvolutionLedger.from_document([{"stage": "observe"}])


def test_records_must_be_a_sequence() -> None:
    with pytest.raises(EvolutionError, match="sequence of records"):
        EvolutionLedger.from_document({"schema": LEDGER_SCHEMA, "records": {"stage": "observe"}})


def test_a_document_written_under_a_different_cycle_is_refused() -> None:
    """An old history under a superseded stage set means something else — say so."""
    document = _cycle(cycles=1).to_document()
    document["cycle_definition"] = ["observe", "learn"]

    with pytest.raises(EvolutionError, match="different evolution cycle"):
        EvolutionLedger.from_document(document)


def test_a_document_without_a_cycle_definition_is_accepted() -> None:
    """The cycle definition is a cross-check, not a required field of the exchange."""
    document = _cycle(cycles=1).to_document()
    del document["cycle_definition"]

    reloaded = EvolutionLedger.from_document(document)

    assert len(reloaded) == CYCLE_LENGTH


def test_an_unknown_stage_in_a_document_is_refused_by_the_stage_authority() -> None:
    """Rehydration coerces through the stage enum, so an invented stage cannot enter."""
    document = _cycle(cycles=1).to_document()
    records = list(document["records"])  # type: ignore[arg-type]
    records[0]["stage"] = "not-a-stage"
    document["records"] = records

    with pytest.raises(EvolutionError, match="unknown evolution stage"):
        EvolutionLedger.from_document(document)


def test_tuple_records_are_accepted() -> None:
    """A document read from a source that yields tuples is still a ledger document."""
    document = _cycle(cycles=1).to_document()
    document["records"] = tuple(document["records"])  # type: ignore[arg-type]

    assert len(EvolutionLedger.from_document(document)) == CYCLE_LENGTH


def test_records_default_to_empty_when_absent() -> None:
    ledger = EvolutionLedger.from_document({"schema": LEDGER_SCHEMA})

    assert len(ledger) == 0
    assert ledger.expected_stage() is EvolutionStage.OBSERVE
