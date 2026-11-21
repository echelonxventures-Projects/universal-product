"""UCI-000001 Part 11 — the classifier that decides what an uncovered line COSTS.

WHY THIS MODULE WAS AT 0%, AND WHY THAT IS THE WORST PLACE FOR A GAP. Classification decides what
the repository owes for an uncovered line: ``executable`` obliges a test, ``dead_code`` a deletion,
``impossible`` and ``defensive`` a proof. A classifier is therefore a machine for RETIRING coverage
debt, and a careless one retires it without any test being written. An unexercised debt-retirement
machine is the one component whose silent failure looks exactly like progress.

THE TWO CONSTRUCTIONS THAT KEEP IT HONEST, both asserted here:

  * ``executable`` is the DEFAULT, so silence costs work rather than saving it. A classifier whose
    default were ``defensive`` would clear the backlog by saying nothing.
  * every non-default classification names the RULE that produced it, so the justification is a
    matched pattern a reader can check rather than a judgement they must accept.

RULE ORDER IS MEANING. First match wins, so a ``raise NotImplementedError`` under ``TYPE_CHECKING``
is impossible-to-execute BEFORE it is defensive. The ordering tests below are not style checks —
they pin the semantics of the table.
"""

from __future__ import annotations

from engine.certification_integrity.classify import (
    GENERATED_MARKER,
    RULES,
    Plan,
    classify_line,
)
from engine.certification_integrity.model import (
    CLASS_DEFENSIVE,
    CLASS_EXECUTABLE,
    CLASS_GENERATED,
    CLASS_IMPOSSIBLE,
    CLASS_UNREACHABLE,
    REMEDY,
    UncoveredLine,
)


def _line(**overrides: object) -> UncoveredLine:
    fields: dict[str, object] = {
        "path": "engine/thing.py",
        "line": 12,
        "owner": "engine.thing",
        "source": "    return value",
        "classification": CLASS_EXECUTABLE,
        "justification": "owes a test",
    }
    fields.update(overrides)
    return UncoveredLine(**fields)  # type: ignore[arg-type]


# --------------------------------------------------------------- the default costs work


def test_an_unrecognised_line_is_executable_and_owes_a_test() -> None:
    """THE LOAD-BEARING DEFAULT. If this were anything cheaper, every line no rule understood
    would retire itself, and the backlog would fall fastest for the code nobody can classify."""
    classification, rule, justification = classify_line("    return value", "a.py", "")
    assert classification == CLASS_EXECUTABLE
    assert rule == "UCI-K-00"
    assert "owes a test" in justification


def test_every_classification_names_a_rule_a_reader_can_look_up() -> None:
    samples = (
        "    if TYPE_CHECKING:",
        "if __name__ == '__main__':",
        "    sys.exit(1)",
        "    raise NotImplementedError",
        "    except OSError:",
        "    something()  # pragma: no cover",
        "    return value",
    )
    for source in samples:
        classification, rule, justification = classify_line(source, "a.py", "")
        assert rule.startswith("UCI-K-"), source
        assert justification.strip(), source
        assert classification


# ------------------------------------------------------------------------ each rule fires


def test_a_typing_only_block_is_impossible_to_execute() -> None:
    for source in ("    if TYPE_CHECKING:", "from typing import Any", "import typing"):
        classification, rule, _ = classify_line(source, "a.py", "")
        assert (classification, rule) == (CLASS_IMPOSSIBLE, "UCI-K-01"), source


def test_a_module_entry_guard_is_impossible_because_tests_import() -> None:
    classification, rule, _ = classify_line('if __name__ == "__main__":', "a.py", "")
    assert (classification, rule) == (CLASS_IMPOSSIBLE, "UCI-K-02")


def test_a_statement_after_an_unconditional_transfer_is_unreachable() -> None:
    for source in ("    raise SystemExit(2)", "    sys.exit(1)"):
        classification, rule, _ = classify_line(source, "a.py", "")
        assert (classification, rule) == (CLASS_UNREACHABLE, "UCI-K-03"), source


def test_an_abstract_or_re_raise_guard_is_defensive() -> None:
    for source in ("    raise NotImplementedError", "    raise AssertionError('unreachable')"):
        classification, rule, _ = classify_line(source, "a.py", "")
        assert (classification, rule) == (CLASS_DEFENSIVE, "UCI-K-04"), source


def test_an_environmental_exception_handler_is_defensive() -> None:
    for source in (
        "    except OSError:",
        "    except MemoryError:",
        "    except KeyboardInterrupt:",
        "    except SystemExit:",
    ):
        classification, rule, _ = classify_line(source, "a.py", "")
        assert (classification, rule) == (CLASS_DEFENSIVE, "UCI-K-05"), source


def test_an_author_marked_branch_is_defensive() -> None:
    classification, rule, _ = classify_line("    fallback()  # pragma: no cover", "a.py", "")
    assert (classification, rule) == (CLASS_DEFENSIVE, "UCI-K-06")


def test_a_generated_file_is_classified_from_its_HEAD_not_its_line() -> None:
    """The remedy for generated output is to govern the GENERATOR: a test over generated bytes
    tests the generator's last run. The marker is therefore read from the file head, and it wins
    over every line rule."""
    classification, rule, justification = classify_line(
        "    return value", "a.py", "# AUTO-GENERATED — do not edit"
    )
    assert (classification, rule) == (CLASS_GENERATED, "UCI-K-07")
    assert "generator" in justification


def test_the_generated_marker_beats_a_line_rule_that_would_otherwise_match() -> None:
    """Ordering across the two mechanisms, not just within the table."""
    classification, _, _ = classify_line("    raise NotImplementedError", "a.py", "@generated")
    assert classification == CLASS_GENERATED


# ------------------------------------------------------------------------- rule ordering


def test_first_match_wins_so_the_table_order_is_the_semantics() -> None:
    """A ``raise NotImplementedError`` is defensive (UCI-K-04). Under a typing guard the
    LINE is still the raise, so the ordering claim is checked where it is actually
    observable: the impossible rules are declared before the defensive ones."""
    order = [rule for _cls, rule, _desc, _pat in RULES]
    assert order == ["UCI-K-01", "UCI-K-02", "UCI-K-03", "UCI-K-04", "UCI-K-05", "UCI-K-06"]
    impossible = [i for i, (c, *_r) in enumerate(RULES) if c == CLASS_IMPOSSIBLE]
    defensive = [i for i, (c, *_r) in enumerate(RULES) if c == CLASS_DEFENSIVE]
    assert max(impossible) < min(defensive)


def test_every_rule_id_is_unique() -> None:
    ids = [rule for _c, rule, _d, _p in RULES]
    assert len(set(ids)) == len(ids)


def test_every_rule_carries_a_description_that_states_the_property() -> None:
    for _classification, rule, description, _pattern in RULES:
        assert description.strip(), rule


def test_dead_code_is_never_assigned_by_pattern() -> None:
    """Deliberately not automated: deciding code is dead requires knowing nothing calls it,
    including from outside this repository, and a classifier that guessed would propose deletions
    on the strength of a regex."""
    assert all(classification != "dead_code" for classification, *_rest in RULES)


def test_the_generated_marker_is_case_insensitive_and_accepts_the_common_spellings() -> None:
    for head in (
        "DO NOT EDIT",
        "do not edit",
        "auto-generated",
        "autogenerated",
        "Generated by x",
        "@generated",
    ):
        assert GENERATED_MARKER.search(head), head
    assert not GENERATED_MARKER.search("a perfectly ordinary docstring")


# -------------------------------------------------------------------------------- the plan


def test_a_plan_counts_by_class_and_by_owner() -> None:
    plan = Plan(
        lines=(
            _line(path="a.py", classification=CLASS_EXECUTABLE),
            _line(path="a.py", classification=CLASS_EXECUTABLE),
            _line(path="b.py", classification=CLASS_DEFENSIVE),
        ),
        unmeasured_in_scope=(),
    )
    assert plan.by_class() == {CLASS_EXECUTABLE: 2, CLASS_DEFENSIVE: 1}
    assert plan.by_owner() == [("a.py", 2), ("b.py", 1)]
    assert plan.by_owner(limit=1) == [("a.py", 2)]


def test_a_plan_isolates_the_lines_that_actually_owe_a_test() -> None:
    plan = Plan(
        lines=(
            _line(path="a.py", classification=CLASS_EXECUTABLE),
            _line(path="b.py", classification=CLASS_IMPOSSIBLE),
            _line(path="c.py", classification=CLASS_GENERATED),
        ),
        unmeasured_in_scope=(),
    )
    assert [line.path for line in plan.executable()] == ["a.py"]


def test_an_undescribed_file_is_not_an_uncovered_line() -> None:
    """Conflating the two would report a RENDERING defect as a coverage gap and send it to the
    wrong remedy — and its true covered fraction is unknown, never assumed to be zero."""
    plan = Plan(lines=(), unmeasured_in_scope=("d.py",), undescribed_statements=40)
    assert plan.lines == ()
    assert plan.unmeasured_in_scope == ("d.py",)
    assert plan.undescribed_statements == 40
    assert plan.by_class() == {}
    assert plan.executable() == ()


def test_undescribed_statements_defaults_to_zero() -> None:
    assert Plan(lines=(), unmeasured_in_scope=()).undescribed_statements == 0


def test_every_classification_has_a_declared_remedy() -> None:
    """A class with no remedy is a finding nobody can act on."""
    for classification in (
        CLASS_EXECUTABLE,
        CLASS_DEFENSIVE,
        CLASS_IMPOSSIBLE,
        CLASS_UNREACHABLE,
        CLASS_GENERATED,
    ):
        assert classification in REMEDY
        assert REMEDY[classification].strip()
