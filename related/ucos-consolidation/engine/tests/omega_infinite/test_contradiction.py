"""Stage 3 — the Universal Contradiction Engine.

THE PROPERTY UNDER TEST IS THAT NOTHING STAYS SILENT. A contradiction engine is trivially
easy to write so that it passes everything: examine no subject, declare no rule, report
"clean". Most of what follows therefore asserts on the engine's ACCOUNTING — how many
subjects were examined, which rules claimed a subject, which subjects nothing looked at —
rather than only on the contradictions it found. A finding count of zero is evidence of
nothing until the denominator is known.

The second property is that no test here mentions a programming language. Subjects are
Rust, Go, Terraform, SQL, Markdown and Zig on purpose: if any assertion below could only
hold for Python, the abstraction is not real.
"""

from __future__ import annotations

import pytest

from engine.omega_infinite.artifact import Artifact, Authority, Location
from engine.omega_infinite.contradiction import (
    UNKNOWN_VALUE,
    AuthorityOpposition,
    Claim,
    Contradiction,
    ContradictionError,
    ContradictionRegistry,
    ContradictionReport,
    MetadataOpposition,
    detect,
    from_metadata,
    seed_registry,
)


def _subject(identifier: str, **facts: str) -> Artifact:
    return from_metadata(identifier, facts)


# ------------------------------------------------------------------------------------- claims


def test_a_claim_must_name_the_dimension_it_speaks_about() -> None:
    with pytest.raises(ContradictionError, match="dimension"):
        Claim("   ", "true", "coverage")


def test_a_claim_must_name_its_source_because_an_unattributed_finding_cannot_be_routed() -> None:
    with pytest.raises(ContradictionError, match="names no source"):
        Claim("measured", "true", "  ")


def test_an_unknown_value_is_not_a_known_claim() -> None:
    """The engine must distinguish "asked, no answer" from "answered false"."""
    assert not Claim("verified", UNKNOWN_VALUE, "plane").known
    assert Claim("verified", "false", "plane").known


def test_a_contradiction_must_name_its_rule_and_subject() -> None:
    left, right = Claim("a", "1", "s"), Claim("b", "2", "t")
    with pytest.raises(ContradictionError, match="name the rule"):
        Contradiction(rule="  ", subject="x", left=left, right=right)
    with pytest.raises(ContradictionError, match="no subject"):
        Contradiction(rule="R", subject="  ", left=left, right=right)


def test_a_contradiction_reads_as_the_two_instruments_that_disagree() -> None:
    found = Contradiction(
        rule="OMEGA-C-01",
        subject="main.rs",
        left=Claim("measured", "true", "coverage"),
        right=Claim("in_scope", "false", "scope derivation"),
        detail="measured but outside scope",
    )
    rendered = str(found)
    assert "coverage says measured=true" in rendered
    assert "scope derivation says in_scope=false" in rendered
    assert found.as_record()["subject"] == "main.rs"


# -------------------------------------------------------------------------------------- rules


def test_a_rule_must_carry_an_identifier_and_a_question() -> None:
    for bad in ("", "   "):
        with pytest.raises(ContradictionError, match="identifier"):
            MetadataOpposition(bad, "q", "a", "1", "b", "2")
        with pytest.raises(ContradictionError, match="identifier"):
            AuthorityOpposition(bad, "q", "a", "1")
    with pytest.raises(ContradictionError, match="asks no question"):
        MetadataOpposition("R", "  ", "a", "1", "b", "2")
    with pytest.raises(ContradictionError, match="asks no question"):
        AuthorityOpposition("R", "  ", "a", "1")


def test_a_metadata_rule_examines_only_the_subjects_its_precondition_selects() -> None:
    rule = MetadataOpposition("R", "q", "measured", "true", "in_scope", "true")
    assert rule.examines(_subject("a.go", measured="true"))
    assert not rule.examines(_subject("b.go", measured="false"))
    assert not rule.examines(_subject("c.go"))


def test_a_metadata_rule_finds_the_opposition_it_declares() -> None:
    rule = MetadataOpposition("R", "q", "measured", "true", "in_scope", "true")
    (found,) = rule.contradictions(_subject("a.rs", measured="true", in_scope="false"))
    assert found.rule == "R"
    assert found.subject == "a.rs"
    assert rule.contradictions(_subject("b.rs", measured="true", in_scope="true")) == ()


def test_a_missing_expectation_is_a_contradiction_not_a_pass() -> None:
    """Absence must not read as agreement — that is how a gate becomes a no-op."""
    rule = MetadataOpposition("R", "q", "certified", "true", "verified", "true")
    (found,) = rule.contradictions(_subject("a.sql", certified="true"))
    assert found.right.value == UNKNOWN_VALUE


def test_a_rule_that_examines_nothing_returns_nothing() -> None:
    rule = MetadataOpposition("R", "q", "measured", "true", "in_scope", "true")
    assert rule.contradictions(_subject("a.zig", colour="blue")) == ()


def test_a_forbidding_rule_inverts_the_expectation() -> None:
    """`archived but executed` needs no second rule class, only an inverted expectation."""
    rule = MetadataOpposition(
        "R", "q", "governance_state", "archived", "executed", "true", forbid=True
    )
    (found,) = rule.contradictions(_subject("old.tf", governance_state="archived", executed="true"))
    assert found.right.value == "true"
    assert rule.contradictions(_subject("cold.tf", governance_state="archived")) == ()


def test_an_authority_rule_refuses_an_unresolved_owner_and_accepts_a_resolved_one() -> None:
    rule = AuthorityOpposition("R", "q", "governance_state", "governed")
    unowned = _subject("a.md", governance_state="governed")
    (found,) = rule.contradictions(unowned)
    assert found.right.value == "UNRESOLVED"

    owned = from_metadata(
        "b.md", {"governance_state": "governed"}, owner="UCOS-DOC", owner_rule="Ω"
    )
    assert rule.contradictions(owned) == ()
    assert rule.contradictions(_subject("c.md")) == ()


def test_from_metadata_attaches_an_owner_only_when_one_is_given() -> None:
    assert not from_metadata("a", {}).authority.resolved
    assert from_metadata("b", {}, owner="OWNER").authority.resolved


# ----------------------------------------------------------------------------------- registry


def test_the_registry_admits_a_rule_and_resolves_it_by_identifier() -> None:
    rule = MetadataOpposition("R-1", "q", "a", "1", "b", "2")
    registry = ContradictionRegistry()
    assert registry.declare(rule) is rule
    assert registry.resolve("R-1") is rule
    assert len(registry) == 1


def test_redeclaring_one_identifier_with_a_different_rule_is_a_competing_authority() -> None:
    registry = ContradictionRegistry([MetadataOpposition("R-1", "q", "a", "1", "b", "2")])
    with pytest.raises(ContradictionError, match="already declared"):
        registry.declare(MetadataOpposition("R-1", "other", "c", "1", "d", "2"))


def test_redeclaring_the_identical_rule_object_is_idempotent() -> None:
    rule = MetadataOpposition("R-1", "q", "a", "1", "b", "2")
    registry = ContradictionRegistry([rule])
    registry.declare(rule)
    assert len(registry) == 1


def test_asking_for_an_undeclared_rule_is_refused() -> None:
    with pytest.raises(ContradictionError, match="no rule named"):
        ContradictionRegistry().resolve("R-404")


def test_something_that_is_not_a_rule_is_refused() -> None:
    with pytest.raises(ContradictionError, match="not a contradiction rule"):
        ContradictionRegistry().declare(object())  # type: ignore[arg-type]


def test_known_rules_come_back_in_identifier_order_so_a_run_is_deterministic() -> None:
    registry = ContradictionRegistry(
        [
            MetadataOpposition("R-2", "q", "a", "1", "b", "2"),
            MetadataOpposition("R-1", "q", "a", "1", "b", "2"),
        ]
    )
    assert [rule.identifier for rule in registry.known] == ["R-1", "R-2"]


# ------------------------------------------------------------------------------------ detect


def test_an_engine_with_no_rules_refuses_rather_than_reporting_everything_consistent() -> None:
    """THE vacuous-pass guard. Zero rules must never render as a clean repository."""
    with pytest.raises(ContradictionError, match="no contradiction rule is declared"):
        detect([_subject("a.go")], ContradictionRegistry())


def test_detect_needs_a_registry() -> None:
    with pytest.raises(ContradictionError, match="needs a ContradictionRegistry"):
        detect([], object())  # type: ignore[arg-type]


def test_a_subject_no_rule_examined_is_reported_rather_than_assumed_consistent() -> None:
    report = detect([_subject("opaque.zig", colour="blue")], seed_registry())
    assert report.clean
    assert report.unexamined == ("opaque.zig",)
    assert report.blocks_certification, "unknown must not certify"


def test_a_rule_that_claimed_no_subject_is_reported_as_idle() -> None:
    """A rule that never applies is dead weight, and dead weight that looks like coverage."""
    registry = ContradictionRegistry(
        [
            MetadataOpposition("R-USED", "q", "measured", "true", "in_scope", "true"),
            MetadataOpposition("R-IDLE", "q", "nothing_has_this", "x", "b", "2"),
        ]
    )
    report = detect([_subject("a.rs", measured="true", in_scope="true")], registry)
    assert report.idle_rules == ("R-IDLE",)
    assert report.clean


def test_an_idle_rule_alone_does_not_block_certification() -> None:
    """Idleness is a finding about the rule set, not about any subject's truth."""
    registry = ContradictionRegistry(
        [
            MetadataOpposition("R-USED", "q", "measured", "true", "in_scope", "true"),
            MetadataOpposition("R-IDLE", "q", "absent", "x", "b", "2"),
        ]
    )
    report = detect([_subject("a.rs", measured="true", in_scope="true")], registry)
    assert report.idle_rules and not report.blocks_certification


def test_the_engine_examines_subjects_of_every_type_identically() -> None:
    subjects = [
        _subject("core.rs", measured="true", in_scope="false"),
        _subject("main.go", certified="true"),
        _subject("infra.tf", governance_state="archived", executed="true"),
        _subject("schema.sql", governance_state="governed"),
    ]
    report = detect(subjects, seed_registry())
    assert report.subjects_examined == 4
    assert report.unexamined == ()
    assert {found.subject for found in report.contradictions} == {
        "core.rs",
        "main.go",
        "infra.tf",
        "schema.sql",
    }


def test_findings_are_sorted_so_two_runs_produce_identical_bytes() -> None:
    subjects = [
        _subject("z.go", measured="true", in_scope="false"),
        _subject("a.go", measured="true", in_scope="false"),
    ]
    first = detect(subjects, seed_registry())
    second = detect(list(reversed(subjects)), seed_registry())
    assert first.as_record() == second.as_record()
    assert [c.subject for c in first.contradictions] == ["a.go", "z.go"]


def test_the_report_counts_findings_by_rule() -> None:
    subjects = [
        _subject("a.go", measured="true", in_scope="false"),
        _subject("b.go", measured="true", in_scope="false"),
        _subject("c.go", governance_state="archived", executed="true"),
    ]
    assert detect(subjects, seed_registry()).by_rule() == {"OMEGA-C-01": 2, "OMEGA-C-06": 1}


def test_a_fully_consistent_population_is_clean_and_certifiable() -> None:
    consistent = from_metadata(
        "good.rs",
        {
            "measured": "true",
            "in_scope": "true",
            "certified": "true",
            "verified": "true",
            "reproducible": "true",
            "reachable": "true",
            "tested": "true",
            "governance_state": "governed",
            "discoverable": "true",
        },
        owner="UCOS-ENGINE",
        owner_rule="Ω-A-02",
    )
    report = detect([consistent], seed_registry())
    assert report.clean and not report.blocks_certification
    assert report.unexamined == ()


def test_an_empty_population_examines_nothing_and_every_rule_is_idle() -> None:
    report = detect([], seed_registry())
    assert report.subjects_total == 0
    assert len(report.idle_rules) == 10
    assert not report.blocks_certification


# ------------------------------------------------------------------------------------ report


def test_the_record_carries_the_denominator_not_only_the_findings() -> None:
    report = detect([_subject("a.rs", measured="true", in_scope="false")], seed_registry())
    record = report.as_record()
    assert record["subjects_total"] == 1
    assert record["subjects_examined"] == 1
    assert record["blocks_certification"] is True
    assert len(record["rules_applied"]) == 10
    assert record["contradictions"][0]["rule"] == "OMEGA-C-01"


def test_an_empty_report_is_clean_and_certifiable() -> None:
    assert ContradictionReport().clean
    assert not ContradictionReport().blocks_certification


# -------------------------------------------------------------------------------- seed rules


def test_the_seed_declares_the_ten_oppositions_the_directive_names() -> None:
    identifiers = [rule.identifier for rule in seed_registry().known]
    assert identifiers == [f"OMEGA-C-{n:02d}" for n in range(1, 11)]


def test_every_seed_rule_states_the_question_it_answers() -> None:
    assert all(rule.question.strip() for rule in seed_registry().known)


def test_the_seed_is_a_floor_and_a_caller_may_add_to_it_without_editing_the_module() -> None:
    extra = MetadataOpposition(
        "DOMAIN-C-01",
        "does a mars asset declare a jurisdiction?",
        "domain",
        "mars",
        "jurisdiction",
        "declared",
    )
    registry = seed_registry([extra])
    assert len(registry) == 11
    assert registry.resolve("DOMAIN-C-01") is extra


def test_a_future_domain_rule_finds_contradictions_with_no_change_to_the_engine() -> None:
    """Stage 10's requirement, in miniature: a new domain costs a declaration, not an edit."""
    registry = seed_registry(
        [
            MetadataOpposition(
                "INTERSTELLAR-C-01",
                "does every relativistic artifact declare a reference frame?",
                "propagation",
                "relativistic",
                "reference_frame",
                "declared",
            )
        ]
    )
    probe = _subject("andromeda/probe.wasm", propagation="relativistic")
    (found,) = [c for c in detect([probe], registry).contradictions]
    assert found.rule == "INTERSTELLAR-C-01"


def test_an_artifact_built_by_hand_reaches_the_engine_the_same_way() -> None:
    """The engine's door is Artifact — not a provider, a path or a language."""
    built = Artifact(
        identifier="oort://survey.parquet",
        location=Location(provider="object-store", locator="oort://survey.parquet"),
        metadata={"governance_state": "governed"},
        authority=Authority(owner="", rule=""),
    )
    (found,) = detect([built], seed_registry()).contradictions
    assert found.rule == "OMEGA-C-09"
    assert found.subject == "oort://survey.parquet"
