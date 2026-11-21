"""UVI-000001 Part 10 — the cost table is a MEASUREMENT, so its derivation is measured.

WHY THIS MODULE WAS AT 0%. It runs on demand (`make verify-cost-model`) and inside no verification
mode, by design: a stale table produces a slower plan, never a wrong one. Nothing being a gate is
exactly why nothing exercised it, and the three properties its own docstring says the derivation
depends on — the hidden-duration residual, the content-hash binding, the non-greedy node match —
are each a way the table can become quietly wrong while every run stays green.

THE REGEX IS THE SHARPEST EDGE HERE. The node part is matched non-greedily to end of line rather
than as ``\\S+``, because a parametrised id may contain a space. A whitespace-free pattern drops
exactly those lines, which under-counts the objects most likely to be parametrised and therefore
most likely to be the ones worth splitting. That is asserted directly below.
"""

from __future__ import annotations

import json

import pytest

from engine.verification_intelligence import cost_model
from engine.verification_intelligence.cost_model import (
    DEFAULT_SPLIT_THRESHOLD,
    DURATION,
    SCHEMA,
    WALL_CLOCK,
    derive,
    main,
)
from engine.verification_intelligence.model import VerificationIntelligenceError
from engine.verification_intelligence.registry import build_test_registry, load_substrates

#: Loading the substrates is the expensive part of this module — it reads the published object
#: registry — and every test needs the same view of it. Loaded ONCE, at module scope, because a
#: per-test load cost 20s for 16 tests and bought nothing: the substrates are read-only here.
_SUBSTRATES = load_substrates(".")
_REGISTRY = build_test_registry(_SUBSTRATES, ".")
COLLECTIBLE: list[str] = sorted(_REGISTRY.paths)
#: Objects whose published record carries a content hash. ``.get(path, {})`` rather than a
#: subscript because the two populations legitimately differ: the collectible set is derived
#: from the tree on every run, while the object registry is a published artifact that lags a
#: newly added test file until it is registered. A subscript turned that ordinary lag into a
#: collection-time KeyError that took the whole module down.
HASHED: list[str] = [
    path for path in COLLECTIBLE if _SUBSTRATES.objects.get(path, {}).get("content_hash")
]


# ------------------------------------------------------------------------------ the regexes


def test_a_parametrised_node_id_containing_a_space_is_still_matched() -> None:
    """The defect a ``\\S+`` node pattern produces: the line is dropped entirely, so the object is
    priced from fewer of its nodes than it has and may fall under the split threshold."""
    line = "12.30s call     platform/tests/test_x.py::test_y[a b]"
    assert DURATION.findall(line) == [("12.30", "platform/tests/test_x.py", "test_y[a b]")]


def test_setup_call_and_teardown_all_count_toward_one_object() -> None:
    """An object's cost is what the suite spends on it, and a fixture that costs ten seconds in
    setup costs ten seconds whichever phase pytest attributes it to."""
    transcript = (
        "1.00s setup    a/test_x.py::test_y\n"
        "2.00s call     a/test_x.py::test_y\n"
        "3.00s teardown a/test_x.py::test_y\n"
    )
    assert len(DURATION.findall(transcript)) == 3


def test_a_line_that_is_not_a_duration_is_not_matched() -> None:
    assert DURATION.findall("== 3 passed in 1.2s ==") == []


def test_the_wall_clock_is_read_from_the_summary_line() -> None:
    assert WALL_CLOCK.findall("11628 passed, 3 skipped in 1588.54s (0:26:28)") == ["1588.54"]


# -------------------------------------------------------------------------------- refusals


def test_a_transcript_with_no_durations_is_refused_rather_than_priced_as_empty() -> None:
    """An empty table is not a cheap suite; it is a transcript from a run that was never asked for
    durations. Returning it would price every object at the unknown default and silently double
    the plan."""
    with pytest.raises(VerificationIntelligenceError) as refusal:
        derive("11628 passed in 1588.54s\n")
    assert "--durations" in str(refusal.value)


# ------------------------------------------------------------------------------ derivation


def _transcript(root: str, paths: list[str]) -> str:
    lines = [f"{2.0 + n}s call     {p}::test_one" for n, p in enumerate(paths)]
    lines.append("100 passed in 900.00s (0:15:00)")
    return "\n".join(lines) + "\n"


def test_the_document_declares_its_schema_and_holds_no_authority(tmp_path) -> None:
    """It is a measurement. A cost table that claimed authority would be a fact about the
    repository rather than a reading of one afternoon's suite."""

    root = "."
    collectible = COLLECTIBLE[:3]
    assert collectible, "the repository publishes no collectible test objects"

    document = derive(_transcript(root, collectible), root=root)
    assert document["schema"] == SCHEMA
    assert document["authority"].startswith("NONE")
    assert document["units"] == "seconds"
    assert document["split_threshold_seconds"] == DEFAULT_SPLIT_THRESHOLD


def test_objects_pytest_never_printed_are_priced_at_the_residual_not_left_unknown() -> None:
    """pytest hides anything under 0.005s. Those objects WERE measured and found negligible, and
    pricing them as unknown would put more fiction into the plan than the suite contains work."""

    root = "."
    collectible = COLLECTIBLE
    assert len(collectible) > 5

    document = derive(_transcript(root, collectible[:2]), root=root)
    assert document["below_resolution_seconds"] > 0.0
    # Every collectible object is priced, not only the ones that produced a line.
    assert set(document["costs"]) == set(collectible)
    for path in collectible[2:]:
        assert document["costs"][path] == document["below_resolution_seconds"]


def test_a_path_the_registry_does_not_collect_is_not_priced() -> None:
    """The table prices the SELECTION's population. A stray path in a transcript is not an object
    the planner can place, and pricing it would put a phantom in the shard packing."""

    root = "."
    collectible = COLLECTIBLE[:2]
    transcript = "5.00s call     not/a/collected/test_ghost.py::test_x\n" + _transcript(
        root, collectible
    )
    document = derive(transcript, root=root)
    assert "not/a/collected/test_ghost.py" not in document["costs"]


def test_an_object_over_the_threshold_is_split_and_records_the_hash_it_was_measured_at() -> None:
    """A node id is only usable while it is current, so the planner splits only while the recorded
    content_hash still matches and a changed file falls back to whole-file placement."""

    root = "."
    hashed = HASHED
    assert hashed, "no collectible object publishes a content hash"
    target = hashed[0]

    transcript = (
        f"40.00s call     {target}::test_a\n"
        f"41.00s call     {target}::test_b\n"
        "100 passed in 900.00s (0:15:00)\n"
    )
    document = derive(transcript, root=root, threshold=60.0)
    assert target in document["split"]
    entry = document["split"][target]
    assert entry["content_hash"] == _SUBSTRATES.objects[target]["content_hash"]
    assert entry["measured_seconds"] == 81.0
    assert set(entry["nodes"]) == {f"{target}::test_a", f"{target}::test_b"}


def test_an_object_under_the_threshold_is_placed_whole() -> None:
    root = "."
    target = COLLECTIBLE[0]
    transcript = f"5.00s call     {target}::test_a\n100 passed in 900.00s\n"
    assert derive(transcript, root=root, threshold=60.0)["split"] == {}


def test_the_threshold_is_a_parameter_so_a_caller_can_measure_a_different_shape() -> None:
    root = "."
    hashed = HASHED
    target = hashed[0]
    transcript = f"5.00s call     {target}::test_a\n100 passed in 900.00s\n"
    assert derive(transcript, root=root, threshold=1.0)["split"] != {}


def test_derivation_is_deterministic_over_one_transcript() -> None:
    """Two derivations of one transcript must be byte-identical, or the table is a second source
    of plan variation on top of the suite's own."""

    root = "."
    transcript = _transcript(root, COLLECTIBLE[:3])
    first = json.dumps(derive(transcript, root=root), sort_keys=True)
    second = json.dumps(derive(transcript, root=root), sort_keys=True)
    assert first == second


def test_the_costs_and_split_tables_are_emitted_in_sorted_order() -> None:
    """Key order is part of the bytes, and the bytes are compared."""

    root = "."
    document = derive(_transcript(root, COLLECTIBLE[:4]), root=root)
    assert list(document["costs"]) == sorted(document["costs"])


# ------------------------------------------------------------------------------------ CLI


def test_the_cli_writes_the_table_where_it_is_told(tmp_path) -> None:
    source = tmp_path / "durations.txt"
    source.write_text(_transcript(".", COLLECTIBLE[:2]), encoding="utf-8")
    out = tmp_path / "cost.json"

    assert main(["--from", str(source), "--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["schema"] == SCHEMA


def test_the_cli_faults_on_an_unreadable_transcript(tmp_path, capsys) -> None:
    assert main(["--from", str(tmp_path / "nothing.txt"), "--out", str(tmp_path / "o.json")]) == 2
    assert "UVI FAULT" in capsys.readouterr().err


def test_the_cli_faults_on_a_transcript_that_carries_no_durations(tmp_path, capsys) -> None:
    source = tmp_path / "durations.txt"
    source.write_text("11628 passed in 1588.54s\n", encoding="utf-8")
    assert main(["--from", str(source), "--out", str(tmp_path / "o.json")]) == 2
    assert "UVI FAULT" in capsys.readouterr().err


def test_an_object_with_no_published_content_hash_is_placed_whole(monkeypatch) -> None:
    """The split entry records the hash it was measured at, so an object with no published hash
    has nothing to record. Splitting it anyway would produce node ids the planner could never
    check for currency, which is the stale-split failure with the detection removed."""

    root = "."
    target = HASHED[0]
    substrates = load_substrates(root)
    substrates.objects[target] = {**substrates.objects[target], "content_hash": ""}
    monkeypatch.setattr(cost_model, "load_substrates", lambda base: substrates)

    transcript = (
        f"40.00s call     {target}::test_a\n"
        f"41.00s call     {target}::test_b\n"
        "100 passed in 900.00s (0:15:00)\n"
    )
    assert derive(transcript, root=root, threshold=60.0)["split"] == {}
