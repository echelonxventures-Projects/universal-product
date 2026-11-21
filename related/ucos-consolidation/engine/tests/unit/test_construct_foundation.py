"""UCON-000001 — the Universal Construct Foundation, measured.

The capability's claim is that any presented construct can be represented, governed, traced,
researched and disposed without constitutional redesign. These tests hold the properties that
make that claim trustworthy rather than decorative, and — this is the part that matters — each
one constructs the failure it is guarding against, so no property is asserted without ever
having been produced.

The properties, in the order they are tested:

    the declaration refuses every incoherence it is supposed to refuse
    identity is total: no natural key produces a refusal instead of an identifier
    the registry has no refusal path, and its arithmetic makes a silent drop impossible
    disposition is a total function whose catch-all forecloses nothing
    reality status and admission cannot be derived from each other
    unknowns, contradictions, research and discovery objects are governed objects
    recursive discovery converges
    nine kinds of self-extension travel one mechanism, and none of them narrows anything
    the closure inventory is a two-directional ratchet
    the gate is fail-closed, three-valued, deterministic, clock-free and writes nothing

The constraint under test throughout: a refusal must never be indistinguishable from a drop.
"""

from __future__ import annotations

import ast
import copy
import dataclasses
import json
import os
import re
import runpy
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from engine.ceu import catalog
from engine.ceu.catalog import SEED_POPULATIONS
from engine.construct import (
    audit,
    contract,
    evidence,
    extension,
    reality,
    views,
)
from engine.construct import (
    cli as construct_cli,
)
from engine.construct import (
    gate as construct_gate,
)
from engine.construct.contract import (
    HOLDS,
    LAW_CHECKS,
    REFUSED,
    ContractError,
    Probe,
    _package_fingerprint,
    available_checks,
    load_contract,
    measure,
    rendered,
)
from engine.construct.declaration import (
    DIGEST_EXCLUSIONS,
    Clause,
    Declaration,
    DeclarationError,
    load_declaration,
    parse,
    repo_root,
)
from engine.construct.disposition import (
    Context,
    DispositionError,
    available_operators,
    dispose,
    evaluate_clause,
    select_rule,
    trace,
)
from engine.construct.extension import ExtensionError
from engine.construct.model import (
    Construct,
    ConstructError,
    DispositionRecord,
    Evidence,
    Presentation,
    RealityAssessment,
    construct_id,
)
from engine.construct.reality import RealityError
from engine.construct.registry import GENESIS, ConstructRegistry, JournalEntry, RegistryError
from engine.construct.views import ViewError
from engine.uckp.canonical import content_hash

REPO = repo_root()


# --- fixtures ------------------------------------------------------------------------------


@pytest.fixture(scope="module", name="declaration")
def _declaration() -> Declaration:
    return load_declaration()


@pytest.fixture(scope="module", name="probe")
def _probe(declaration: Declaration) -> Probe:
    return Probe(declaration=declaration, repo=REPO)


@pytest.fixture(scope="module", name="report")
def _report() -> dict:
    """The full law measurement, taken once: it scans several hundred modules."""
    return measure()


@pytest.fixture(scope="module", name="inventory")
def _inventory(probe: Probe) -> dict:
    return probe.inventory()


@pytest.fixture(name="registry")
def _registry(declaration: Declaration) -> ConstructRegistry:
    return ConstructRegistry(declaration)


# --- the declaration -----------------------------------------------------------------------


def test_the_live_declaration_is_coherent_against_every_implemented_registry(
    declaration: Declaration,
) -> None:
    """All five bindings are checked, so the live path is never the unmeasured one."""
    problems = declaration.validate(
        available_checks(),
        available_operators(),
        views.available_selectors(),
        extension.available_admissions(),
        audit.available_forms(),
    )
    assert problems == [], "the declaration is incoherent:\n  " + "\n  ".join(problems)


def test_the_declaration_declares_at_least_the_required_minimum(declaration: Declaration) -> None:
    """The eight dispositions and eight reality states the requirement names are all present."""
    required_dispositions = {
        "ADMIT",
        "TRANSFORM",
        "RESEARCH",
        "QUARANTINE",
        "DEFER",
        "ESCALATE",
        "UNDECIDABLE",
        "REJECT",
    }
    required_states = {
        "VERIFIED",
        "OBSERVED",
        "REPRODUCED",
        "THEORETICAL",
        "HYPOTHETICAL",
        "CONTRADICTED",
        "UNKNOWN",
        "UNDECIDABLE",
    }
    assert required_dispositions <= set(declaration.disposition_ids)
    assert required_states <= set(declaration.reality_ids)


@pytest.mark.parametrize(
    ("accessor", "argument"),
    [
        ("disposition", "NO-SUCH-DISPOSITION"),
        ("reality", "NO-SUCH-STATE"),
        ("kind", "no-such-kind"),
        ("facet", "no-such-facet"),
        ("law", "NO-SUCH-LAW"),
        ("extension_point", "NO-SUCH-POINT"),
    ],
)
def test_no_declaration_accessor_defaults(
    declaration: Declaration, accessor: str, argument: str
) -> None:
    """A fallback here would be an undeclared vocabulary member admitted at a call site."""
    with pytest.raises(DeclarationError):
        getattr(declaration, accessor)(argument)


def test_an_absent_declaration_is_a_fault_not_a_verdict(tmp_path) -> None:
    with pytest.raises(DeclarationError, match="absent"):
        load_declaration(str(tmp_path / "nothing.json"))


def test_an_unparseable_declaration_is_a_fault(tmp_path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    with pytest.raises(DeclarationError, match="cannot be read"):
        load_declaration(str(broken))


@pytest.mark.parametrize("section", ["principle", "dispositions", "reality_states", "laws"])
def test_a_declaration_missing_a_section_is_refused(section: str) -> None:
    document = json.loads(
        (open(os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json"))).read()
    )
    document.pop(section)
    with pytest.raises(DeclarationError):
        parse(document)


def test_a_law_naming_an_unimplemented_check_is_refused(declaration: Declaration) -> None:
    forged = replace(
        declaration, laws=(*declaration.laws, replace(declaration.laws[0], check="not_a_check"))
    )
    problems = forged.validate(available_checks(), available_operators())
    assert any("not a check" in p or "not implemented" in p for p in problems)


def test_a_check_no_law_claims_is_refused(declaration: Declaration) -> None:
    """Dead code that looks like enforcement is as bad as enforcement that does not exist."""
    problems = declaration.validate(
        available_checks() | {"an_unclaimed_check"}, available_operators()
    )
    assert any("no law claims it" in problem for problem in problems)


def test_an_operator_no_rule_claims_is_refused(declaration: Declaration) -> None:
    problems = declaration.validate(
        available_checks(), available_operators() | {"an_unclaimed_operator"}
    )
    assert any("no rule claims it" in problem for problem in problems)


def test_a_second_catch_all_makes_the_rule_set_untotal(declaration: Declaration) -> None:
    forged = replace(
        declaration,
        rules=(replace(declaration.rules[0], catch_all=True), *declaration.rules[1:]),
    )
    problems = forged.validate(available_checks(), available_operators())
    assert any("catch-all" in problem for problem in problems)


def test_a_catch_all_that_is_not_last_makes_later_rules_unreachable(
    declaration: Declaration,
) -> None:
    forged = replace(declaration, rules=(declaration.rules[-1], *declaration.rules[:-1]))
    problems = forged.validate(available_checks(), available_operators())
    assert any("not last" in problem for problem in problems)


def test_a_disposition_permitting_an_undeclared_act_is_refused(declaration: Declaration) -> None:
    spec = declaration.disposition("ADMIT")
    forged = replace(
        declaration,
        dispositions=(
            replace(spec, permits=spec.permits | {"transmute"}),
            *declaration.dispositions[1:],
        ),
    )
    problems = forged.validate(available_checks(), available_operators())
    assert any("undeclared act" in problem for problem in problems)


def test_a_reality_state_with_no_binding_and_no_gap_is_refused(declaration: Declaration) -> None:
    """Otherwise the vocabulary drifts into a private copy of somebody else's, one row at a time."""
    spec = declaration.reality("UNKNOWN")
    forged = replace(
        declaration,
        reality_states=(
            replace(spec, ceu_binding=None, binding_gap=None),
            *declaration.reality_states[1:],
        ),
    )
    problems = forged.validate(available_checks(), available_operators())
    assert any("discloses no gap" in problem for problem in problems)


def test_the_declaration_digest_excludes_its_source(declaration: Declaration) -> None:
    """A digest that changed with the reader would not be a digest of the declaration."""
    assert "source" not in declaration.digest_payload()
    moved = replace(declaration, source="/somewhere/else.json")
    assert moved.digest_payload() == declaration.digest_payload()


# --- identity ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "natural_key",
    [
        "plain-key",
        "a natural key with spaces",
        "punctuation!,;:@#$%^&*()",
        "自然键-非拉丁文",
        "ключ",
        "\ttabs\tand\nnewlines\n",
        "a" * 500,
    ],
)
def test_identity_is_total_over_natural_keys(natural_key: str) -> None:
    """A construct that could not be named is one that could not be recorded."""
    identity = construct_id("entity", natural_key)
    assert identity.startswith("UMK-")
    assert construct_id("entity", natural_key) == identity


def test_identity_is_a_function_of_kind_and_key(declaration: Declaration) -> None:
    assert construct_id("entity", "k") != construct_id("concept", "k")
    assert construct_id("entity", "k") != construct_id("entity", "j")


@pytest.mark.parametrize(("kind", "key"), [("", "k"), ("entity", ""), ("  ", "k"), ("entity", " ")])
def test_an_unnamed_construct_is_a_fault(kind: str, key: str) -> None:
    with pytest.raises(ConstructError):
        construct_id(kind, key)


# --- the model -----------------------------------------------------------------------------


def test_a_construct_without_a_disposition_cannot_exist(registry: ConstructRegistry) -> None:
    sample = registry.all()[0]
    with pytest.raises(ConstructError, match="UCON-L-01"):
        Construct(
            presentation=sample.presentation,
            dispositions=(),
            assessments=sample.assessments,
            kind_registered=True,
        )


def test_a_construct_with_two_active_dispositions_cannot_exist(
    registry: ConstructRegistry,
) -> None:
    sample = registry.all()[0]
    with pytest.raises(ConstructError, match="exactly one active disposition"):
        Construct(
            presentation=sample.presentation,
            dispositions=(sample.disposition, replace(sample.disposition, sequence=7)),
            assessments=sample.assessments,
            kind_registered=True,
        )


def test_a_construct_without_a_reality_assessment_cannot_exist(
    registry: ConstructRegistry,
) -> None:
    sample = registry.all()[0]
    with pytest.raises(ConstructError, match="reality assessment"):
        Construct(
            presentation=sample.presentation,
            dispositions=sample.dispositions,
            assessments=(),
            kind_registered=True,
        )


def test_evidence_must_name_its_source() -> None:
    with pytest.raises(ConstructError, match="source"):
        Evidence(source="   ", statement="anonymous")


def test_independent_sources_counts_sources_not_records() -> None:
    """Two records from one source are one observation written down twice."""
    presentation = Presentation(
        kind="entity",
        natural_key="counted",
        evidence=(
            Evidence(source="a", statement="one"),
            Evidence(source="a", statement="two"),
            Evidence(source="b", statement="three"),
            Evidence(source="c", statement="four", independent=False),
        ),
    )
    assert presentation.evidence_count == 4
    assert presentation.independent_sources == 2


@pytest.mark.parametrize("absent", ["identity", "disposition", "rule_id", "inputs_digest"])
def test_a_disposition_record_must_be_traceable(absent: str) -> None:
    fields = {
        "identity": "UMK-X-0",
        "disposition": "ADMIT",
        "rule_id": "R",
        "rationale": "because",
        "sequence": 0,
        "inputs_digest": "d",
    }
    fields[absent] = ""
    with pytest.raises(ConstructError, match=absent):
        DispositionRecord(**fields)


# --- the registry --------------------------------------------------------------------------


def test_the_registry_bootstraps_every_declared_kind_through_the_ordinary_path(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    """No privileged insert: a founding kind and a future kind take the same door."""
    assert len(registry.all()) == len(declaration.kinds)
    assert set(declaration.kind_names) <= registry.registered_kinds
    assert registry.verify()["status"] == "PASS"
    assert registry.undisposed() == ()


HOSTILE = (
    ("a-category-nobody-declared", "future-1", {}, "TRANSFORM"),
    ("unknown", "malformed-unknown-with-no-formulation", {}, "RESEARCH"),
    ("entity", "unattributed", {"provenance": "unattributed"}, "QUARANTINE"),
)


@pytest.mark.parametrize(("kind", "key", "payload", "expected"), HOSTILE)
def test_the_registry_records_what_it_cannot_classify(
    registry: ConstructRegistry, kind: str, key: str, payload: dict, expected: str
) -> None:
    construct = registry.present(Presentation(kind=kind, natural_key=key, payload=payload))
    assert registry.has(construct.identity)
    assert construct.disposition.disposition == expected
    assert construct.disposition.rule_id
    assert construct.disposition.rationale


def test_a_rejected_construct_remains_readable(registry: ConstructRegistry) -> None:
    """A rejection that leaves no record is indistinguishable from a silent drop."""
    construct = registry.present(Presentation(kind="entity", natural_key="to-be-rejected"))
    rejected = registry.redispose(
        construct.identity,
        disposition="REJECT",
        rule_id="TEST",
        rationale="measured: a rejection must leave a record",
    )
    assert registry.has(rejected.identity)
    assert rejected.disposition.disposition == "REJECT"
    assert "reference" in reality.permitted_acts(registry.declaration, rejected)
    assert reality.permits(registry.declaration, rejected, "certify") is False


def test_the_population_never_exceeds_the_presentations(registry: ConstructRegistry) -> None:
    seeded = len(registry.all())
    presentations = tuple(
        Presentation(kind="entity", natural_key=f"counted-{index}") for index in range(25)
    )
    registry.present_all(presentations)
    assert len(registry.all()) == seeded + 25
    assert registry.presented >= len(registry.all())


def test_re_presentation_supersedes_and_keeps_history(registry: ConstructRegistry) -> None:
    presentation = Presentation(kind="entity", natural_key="revisited")
    first = registry.present(presentation)
    second = registry.present(presentation)
    assert first.identity == second.identity
    assert len(second.dispositions) == 2
    assert [record.active for record in second.dispositions] == [False, True]
    assert second.dispositions[0].superseded_by == second.disposition.record_id


def test_registered_kinds_is_derived_from_the_record_not_a_table(
    registry: ConstructRegistry,
) -> None:
    assert "invented-here" not in registry.registered_kinds
    extension.register_kind(
        registry, "invented-here", definition="a kind invented by a test", declared_by="test"
    )
    assert "invented-here" in registry.registered_kinds


def test_the_reflective_root_classifies_itself(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    """The fixed point that lets the very first registration happen at all."""
    assert declaration.reflective_root in registry.registered_kinds
    root = registry.get(construct_id(declaration.reflective_root, declaration.reflective_root))
    assert root.kind == declaration.reflective_root
    assert root.presentation.natural_key == declaration.reflective_root


def test_the_admission_journal_is_hash_chained(registry: ConstructRegistry) -> None:
    registry.present(Presentation(kind="entity", natural_key="journalled"))
    assert registry.chain_is_intact()
    assert registry.journal[0].prev_hash == GENESIS
    for previous, current in zip(registry.journal, registry.journal[1:], strict=False):
        assert current.prev_hash == previous.entry_hash


def test_a_tampered_journal_is_detected(registry: ConstructRegistry) -> None:
    """A retroactive edit must break the chain rather than pass quietly."""
    assert registry.chain_is_intact()
    forged = JournalEntry(
        sequence=0,
        identity="UMK-X-0",
        event="presented",
        disposition="ADMIT",
        reality_status="UNKNOWN",
        content_digest="d",
        prev_hash=GENESIS,
    )
    registry._journal[0] = forged  # noqa: SLF001 - forging the failure is the test
    assert registry.chain_is_intact() is False


def test_redispose_refuses_an_undeclared_successor(registry: ConstructRegistry) -> None:
    construct = registry.present(Presentation(kind="entity", natural_key="successor-check"))
    with pytest.raises(RegistryError, match="not a declared"):
        registry.redispose(
            construct.identity,
            disposition=construct.disposition.disposition,
            rule_id="TEST",
            rationale="a disposition is not its own successor",
        )


def test_an_unknown_identity_is_a_fault_not_a_silent_none(registry: ConstructRegistry) -> None:
    with pytest.raises(RegistryError, match="no construct is registered"):
        registry.get("UMK-NOTHING-000000000000")
    assert registry.has("UMK-NOTHING-000000000000") is False


def test_facet_violations_are_recorded_never_refused(registry: ConstructRegistry) -> None:
    """An unknown presented without its formulation is still an unknown somebody presented."""
    construct = registry.present(Presentation(kind="unknown", natural_key="incomplete"))
    assert registry.has(construct.identity)
    assert construct.facet_violations
    assert any("formulation" in violation for violation in construct.facet_violations)


def test_two_registries_built_by_identical_calls_are_byte_identical(
    declaration: Declaration,
) -> None:
    left, right = ConstructRegistry(declaration), ConstructRegistry(declaration)
    for target in (left, right):
        target.present(Presentation(kind="entity", natural_key="determinism"))
    assert left.rendered() == right.rendered()
    assert left.digest() == right.digest()


def test_adopting_a_narrowed_declaration_is_refused(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    """A construct disposed under a definition that no longer exists cannot be read."""
    with pytest.raises(RegistryError, match="only add"):
        registry.adopt(replace(declaration, dispositions=declaration.dispositions[:-1]))
    with pytest.raises(RegistryError, match="only add"):
        registry.adopt(replace(declaration, laws=declaration.laws[:-1]))
    with pytest.raises(RegistryError, match="different artifact"):
        registry.adopt(replace(declaration, artifact_id="SOMETHING-ELSE"))


# --- disposition ---------------------------------------------------------------------------


RULE_PROBES = (
    ("UCON-DR-01", Presentation(kind="entity", natural_key="p1", escalation_requested=True)),
    ("UCON-DR-02", Presentation(kind="entity", natural_key="p2", declared_undecidable=True)),
    ("UCON-DR-04", Presentation(kind="undeclared-kind", natural_key="p4")),
    ("UCON-DR-05", Presentation(kind="unknown", natural_key="p5")),
    (
        "UCON-DR-06",
        Presentation(
            kind="research-object",
            natural_key="p6",
            payload={"hypothesis": "h", "research_state": "in-progress"},
        ),
    ),
    (
        "UCON-DR-07",
        Presentation(
            kind="entity",
            natural_key="p7",
            dependencies=("UMK-ABSENT-000000000000",),
            reality_status="THEORETICAL",
        ),
    ),
    (
        "UCON-DR-08",
        Presentation(kind="entity", natural_key="p8", payload={"provenance": "unattributed"}),
    ),
    ("UCON-DR-09", Presentation(kind="entity", natural_key="p9", reality_status="HYPOTHETICAL")),
    (
        "UCON-DR-10",
        Presentation(
            kind="entity",
            natural_key="p10",
            reality_status="OBSERVED",
            evidence=(Evidence(source="s", statement="seen"),),
        ),
    ),
    ("UCON-DR-11", Presentation(kind="entity", natural_key="p11", reality_status="THEORETICAL")),
)


@pytest.mark.parametrize(("rule_id", "presentation"), RULE_PROBES, ids=[r for r, _ in RULE_PROBES])
def test_every_declared_rule_fires_for_a_construct_that_matches_it(
    registry: ConstructRegistry, rule_id: str, presentation: Presentation
) -> None:
    """A rule nothing can trigger is a rule that has quietly gone dark."""
    construct = registry.present(presentation)
    assert construct.disposition.rule_id == rule_id


def test_the_contradiction_rule_fires_when_a_contradiction_names_the_construct(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    subject = registry.present(Presentation(kind="entity", natural_key="contradicted-subject"))
    views.register_contradiction(
        registry,
        natural_key="CNTR-test",
        left=subject.identity,
        right="UMK-OTHER-000000000000",
        contradiction_class=declaration.contradiction_classes[0],
        resolution_state="open",
    )
    again = registry.present(subject.presentation)
    assert again.disposition.rule_id == "UCON-DR-03"
    assert again.disposition.disposition == "QUARANTINE"


def test_a_resolved_contradiction_stops_quarantining(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    """Which resolution states contradict is declared, so this behaviour is data-driven."""
    subject = registry.present(Presentation(kind="entity", natural_key="resolved-subject"))
    views.register_contradiction(
        registry,
        natural_key="CNTR-resolved",
        left=subject.identity,
        right="UMK-OTHER-000000000000",
        contradiction_class=declaration.contradiction_classes[0],
        resolution_state="resolved-by-evidence",
    )
    assert subject.identity not in registry.contradicted()


def test_the_trace_names_every_rule_and_marks_the_one_that_decided(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    """A disposition whose reason cannot be reconstructed is one nobody can contest."""
    presentation = Presentation(kind="entity", natural_key="traced", reality_status="THEORETICAL")
    rows = trace(declaration, presentation, context=registry.context(reality_status="THEORETICAL"))
    assert [row["rule_id"] for row in rows] == [rule.rule_id for rule in declaration.rules]
    selected = [row for row in rows if row["selected"]]
    assert len(selected) == 1
    assert selected[0]["rule_id"] == declaration.catch_all.rule_id


def test_a_clause_missing_its_declared_argument_is_a_fault(declaration: Declaration) -> None:
    """A silently false clause is a rule that stopped firing without anybody being told."""
    with pytest.raises(DispositionError, match="requires argument"):
        evaluate_clause(
            Clause(operator="kind_in", arguments={}),
            Presentation(kind="entity", natural_key="x"),
            Context(),
        )


def test_an_unimplemented_operator_is_a_fault_not_a_false_clause() -> None:
    with pytest.raises(DispositionError, match="not implemented"):
        evaluate_clause(
            Clause(operator="no_such_operator", arguments={}),
            Presentation(kind="entity", natural_key="x"),
            Context(),
        )


def test_disposition_is_total_for_any_presentation_in_any_world(
    declaration: Declaration,
) -> None:
    rule = select_rule(
        declaration,
        Presentation(kind="nothing-knows-this", natural_key="alone"),
        Context(),
    )
    assert rule.rule_id
    record = dispose(declaration, Presentation(kind="k", natural_key="v"))
    assert record.disposition in declaration.disposition_ids


# --- reality -------------------------------------------------------------------------------


def test_an_unclaimed_construct_takes_the_declared_initial_state(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    construct = registry.present(Presentation(kind="entity", natural_key="unclaimed"))
    assert construct.reality.status == declaration.initial_reality_state


def test_a_claim_above_its_evidence_floor_is_recorded_not_downgraded(
    registry: ConstructRegistry,
) -> None:
    """Silently rewriting the claim would destroy the only evidence that it was made."""
    construct = registry.present(
        Presentation(kind="entity", natural_key="over-claimed", reality_status="VERIFIED")
    )
    assert construct.reality.status == "VERIFIED"
    assert construct.reality.floor_met is False


def test_an_undeclared_reality_state_is_a_fault(registry: ConstructRegistry) -> None:
    with pytest.raises(RealityError, match="undeclared reality state"):
        registry.present(
            Presentation(kind="entity", natural_key="bad-state", reality_status="MADE-UP")
        )


def test_an_undeclared_transition_is_refused(registry: ConstructRegistry) -> None:
    construct = registry.present(
        Presentation(kind="entity", natural_key="transitions", reality_status="VERIFIED")
    )
    with pytest.raises(RealityError, match="not a declared transition"):
        registry.reassess(construct.identity, "HYPOTHETICAL")


def test_every_reality_state_is_reachable_from_the_initial_state(
    declaration: Declaration,
) -> None:
    reachable = reality.reachable_from(declaration, declaration.initial_reality_state)
    assert set(declaration.reality_ids) <= reachable


def test_permitted_acts_is_the_intersection_of_both_sides(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    construct = registry.present(
        Presentation(
            kind="entity",
            natural_key="intersected",
            reality_status="HYPOTHETICAL",
            evidence=(Evidence(source="s", statement="offered"),),
        )
    )
    admitted = (
        construct
        if construct.disposition.disposition == "ADMIT"
        else registry.redispose(
            construct.identity, disposition="ADMIT", rule_id="TEST", rationale="measured"
        )
    )
    expected = (
        declaration.disposition("ADMIT").permits & declaration.reality("HYPOTHETICAL").permits
    )
    assert reality.permitted_acts(declaration, admitted) == expected
    assert reality.permits(declaration, admitted, "certify") is False
    assert "HYPOTHETICAL" in reality.refusal(declaration, admitted, "certify")


def test_an_undeclared_act_is_refused_rather_than_defaulted(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    construct = registry.all()[0]
    assert reality.permits(declaration, construct, "transmute") is False
    assert "not a declared operational act" in reality.refusal(declaration, construct, "transmute")


# --- the unknown, contradiction, research and discovery registries -------------------------


def test_all_four_projections_read_one_store(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    unknown = views.register_unknown(
        registry,
        natural_key="U-1",
        unknown_class=declaration.unknown_classes[0],
        domain="d",
        formulation="what is not known",
    )
    other = registry.present(Presentation(kind="concept", natural_key="C-1"))
    contradiction = views.register_contradiction(
        registry,
        natural_key="K-1",
        left=unknown.identity,
        right=other.identity,
        contradiction_class=declaration.contradiction_classes[0],
        resolution_state="open",
    )
    research = views.register_research(
        registry, natural_key="R-1", hypothesis="h", research_state="open"
    )
    discovery = views.register_discovery(
        registry,
        natural_key="D-1",
        opportunity="o",
        priority=declaration.priority_scale[0],
        impact=declaration.impact_scale[0],
    )
    assert unknown in views.unknowns(registry)
    assert contradiction in views.contradictions(registry)
    assert contradiction in views.standing_contradictions(registry)
    assert research in views.research_objects(registry)
    assert discovery in views.discovery_objects(registry)
    # One store: every projected construct is in the registry itself.
    for construct in (unknown, contradiction, research, discovery):
        assert registry.get(construct.identity) is construct


@pytest.mark.parametrize(
    ("call", "kwargs", "match"),
    [
        (
            "register_unknown",
            {
                "natural_key": "x",
                "unknown_class": "not-a-class",
                "domain": "d",
                "formulation": "f",
            },
            "not a declared unknown class",
        ),
        (
            "register_contradiction",
            {
                "natural_key": "x",
                "left": "a",
                "right": "b",
                "contradiction_class": "nope",
                "resolution_state": "open",
            },
            "not a declared contradiction class",
        ),
        (
            "register_research",
            {"natural_key": "x", "hypothesis": "h", "research_state": "nope"},
            "not a declared research state",
        ),
        (
            "register_discovery",
            {"natural_key": "x", "opportunity": "o", "priority": "P9", "impact": "local"},
            "not a declared discovery priority",
        ),
    ],
)
def test_an_undeclared_vocabulary_member_is_refused(
    registry: ConstructRegistry, call: str, kwargs: dict, match: str
) -> None:
    with pytest.raises(ViewError, match=match):
        getattr(views, call)(registry, **kwargs)


def test_an_unknown_whose_class_is_itself_unknown_is_representable(
    registry: ConstructRegistry,
) -> None:
    """An open vocabulary is not an unchecked one: the second-order unknown has a declared home."""
    construct = views.register_unknown(
        registry,
        natural_key="second-order",
        unknown_class="unknown-unclassified",
        domain="unknown",
        formulation="we do not know what kind of not-knowing this is",
    )
    assert construct in views.unknowns(registry)


def test_any_construct_is_transformable_into_a_research_object(
    registry: ConstructRegistry,
) -> None:
    subject = registry.present(Presentation(kind="entity", natural_key="ordinary"))
    research = views.promote_to_research(registry, subject.identity)
    assert research in views.research_objects(registry)
    assert subject.identity in research.presentation.lineage.derived_from
    assert views.promote_to_research(registry, subject.identity).identity == research.identity


def test_recursive_discovery_reaches_a_fixed_point(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    views.register_unknown(
        registry,
        natural_key="U-fp",
        unknown_class=declaration.unknown_classes[0],
        domain="d",
        formulation="f",
    )
    registry.present(Presentation(kind="entity", natural_key="E-fp", escalation_requested=True))
    first = views.discover(registry)
    assert first
    settled = registry.digest()
    assert views.discover(registry) == ()
    assert registry.digest() == settled
    assert views.discover(registry) == ()
    for construct in first:
        assert construct.presentation.lineage.derived_from


def test_reading_the_opportunities_mints_nothing(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    """A read that changes the thing it reads is a read nobody can trust twice."""
    views.register_unknown(
        registry,
        natural_key="U-read",
        unknown_class=declaration.unknown_classes[0],
        domain="d",
        formulation="f",
    )
    before = registry.digest()
    assert views.opportunities(registry)
    assert registry.digest() == before


def test_a_facet_carried_by_no_root_kind_cannot_be_projected(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    forged = ConstructRegistry(
        replace(
            declaration,
            kinds=tuple(spec for spec in declaration.kinds if spec.facet != "unknown"),
        )
    )
    with pytest.raises(ViewError, match="root kinds for facet"):
        views.register_unknown(
            forged,
            natural_key="x",
            unknown_class="unknown-mathematics",
            domain="d",
            formulation="f",
        )


# --- self-extension ------------------------------------------------------------------------


def test_every_declared_extension_point_is_exercisable(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    for point in declaration.extension_points:
        construct = extension.exercise(registry, point.point_id)
        assert construct.kind == point.kind
        assert construct.presentation.natural_key.startswith(declaration.probe_key_prefix)
        assert construct.disposition.disposition in registry.declaration.disposition_ids


def test_extending_the_declaration_does_not_mutate_the_original(
    declaration: Declaration,
) -> None:
    """A comment claiming a vocabulary is append-only is not evidence; this is."""
    before = declaration.digest_payload()
    extended = extension.extended_with_disposition(
        declaration,
        "PROBE-DISPOSITION",
        definition="a probe",
        permits=(declaration.operational_acts[0],),
        successors=(declaration.disposition_ids[0],),
    )
    assert declaration.digest_payload() == before
    assert len(extended.dispositions) == len(declaration.dispositions) + 1
    assert all(spec in extended.dispositions for spec in declaration.dispositions)


def test_a_terminal_extension_is_refused(declaration: Declaration) -> None:
    """An extension that could close the door the foundation exists to keep open."""
    with pytest.raises(ExtensionError, match="no successor"):
        extension.extended_with_disposition(
            declaration, "DEAD-END", definition="d", permits=(), successors=()
        )
    with pytest.raises(ExtensionError, match="no successor"):
        extension.extended_with_reality_state(
            declaration,
            "DEAD-END",
            definition="d",
            permits=(),
            successors=(),
            binding_gap={"gap_id": "g"},
        )


def test_an_extension_naming_an_undeclared_act_or_successor_is_refused(
    declaration: Declaration,
) -> None:
    with pytest.raises(ExtensionError, match="undeclared acts"):
        extension.extended_with_disposition(
            declaration,
            "X",
            definition="d",
            permits=("transmute",),
            successors=(declaration.disposition_ids[0],),
        )
    with pytest.raises(ExtensionError, match="undeclared successor"):
        extension.extended_with_disposition(
            declaration, "X", definition="d", permits=(), successors=("NOPE",)
        )


def test_a_reality_state_extension_must_bind_or_disclose(declaration: Declaration) -> None:
    with pytest.raises(ExtensionError, match="UCON-L-14"):
        extension.extended_with_reality_state(
            declaration,
            "UNBOUND",
            definition="d",
            permits=(),
            successors=(declaration.initial_reality_state,),
        )


def test_re_declaring_an_existing_member_is_refused(declaration: Declaration) -> None:
    with pytest.raises(ExtensionError, match="already declared"):
        extension.extended_with_kind(declaration, "entity", definition="d")
    with pytest.raises(ExtensionError, match="already declared"):
        extension.extended_with_disposition(
            declaration, "ADMIT", definition="d", permits=(), successors=("REJECT",)
        )


@pytest.mark.parametrize(
    ("assumptions", "limitations"),
    [((), ("a limit",)), (("an assumption",), ()), (("  ",), ("a limit",))],
)
def test_a_verifier_that_cannot_be_verified_is_refused(
    registry: ConstructRegistry, assumptions: tuple, limitations: tuple
) -> None:
    """A verifier whose assumptions are unstated has to be taken on trust."""
    with pytest.raises(ExtensionError, match="UCON-L-12"):
        extension.register_verifier(
            registry,
            natural_key="V",
            verifies="everything",
            assumptions=assumptions,
            limitations=limitations,
            declared_by="test",
        )


def test_a_verifier_may_verify_a_verifier(registry: ConstructRegistry) -> None:
    inner = extension.register_verifier(
        registry,
        natural_key="V-inner",
        verifies="the rule set",
        assumptions=("the declaration is readable",),
        limitations=("says nothing about whether a rule is correct",),
        declared_by="test",
    )
    outer = extension.register_verifier(
        registry,
        natural_key="V-outer",
        verifies="V-inner",
        assumptions=("V-inner declares its own assumptions",),
        limitations=("cannot decide whether those assumptions hold",),
        declared_by="test",
        lineage_of=inner.identity,
    )
    assert inner.identity in outer.presentation.lineage.derived_from


def test_an_extension_must_use_a_kind_carrying_the_extension_facet(
    registry: ConstructRegistry,
) -> None:
    with pytest.raises(ExtensionError, match="extension facet"):
        extension.register_extension(
            registry,
            kind="entity",
            natural_key="x",
            subject="s",
            point_id="UCON-EP-04",
            declared_by="test",
        )


def test_an_extension_records_the_owner_it_is_referred_to(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    """Registering a location axis here does not make engine/context resolve it."""
    point = declaration.extension_point("UCON-EP-07")
    construct = extension.register_extension(
        registry,
        kind=point.kind,
        natural_key="galaxy",
        subject="galaxy",
        point_id=point.point_id,
        declared_by="test",
    )
    assert construct.presentation.payload["referred_to"] == point.owner
    assert construct.presentation.payload["extension_point"] == point.point_id


# --- the extensibility audit ---------------------------------------------------------------


DETECTOR_SOURCES = (
    ("ENUM_CLASS", "import enum\n\n\nclass Kind(str, enum.Enum):\n    A = 'a'\n    B = 'b'\n"),
    ("FROZEN_MEMBERSHIP_SET", "MEMBERS = frozenset({'a', 'b', 'c'})\n"),
    ("FIXED_VOCABULARY_TUPLE", "VOCABULARY = ('a', 'b', 'c')\n"),
    ("FIXED_DISPATCH_TABLE", "TABLE = {'a': 1, 'b': 2}\n"),
    ("POPULATION_ASSERTION", "def f(x):\n    return len(x) == 7\n"),
)


@pytest.mark.parametrize(("form", "source"), DETECTOR_SOURCES, ids=[f for f, _ in DETECTOR_SOURCES])
def test_every_declared_closure_form_is_detected(
    declaration: Declaration, tmp_path, form: str, source: str
) -> None:
    """A declared form nothing detects is a declaration nobody measures."""
    module = tmp_path / "engine" / "probe.py"
    module.parent.mkdir(parents=True)
    module.write_text(source, encoding="utf-8")
    spec = replace(declaration.audit, roots=("engine",))
    found = audit.scan(replace(declaration, audit=spec), str(tmp_path))
    assert form in {closure.form for closure in found}


def test_an_annotated_assignment_is_measured_too(declaration: Declaration, tmp_path) -> None:
    """The first detector missed AnnAssign, so every annotated dispatch table was invisible."""
    module = tmp_path / "engine" / "annotated.py"
    module.parent.mkdir(parents=True)
    module.write_text("from typing import Any\n\nTABLE: dict[str, Any] = {'a': 1}\n", "utf-8")
    spec = replace(declaration.audit, roots=("engine",))
    found = audit.scan(replace(declaration, audit=spec), str(tmp_path))
    assert "TABLE" in {closure.symbol for closure in found}


def test_the_declared_tier_is_resolved_by_longest_prefix(declaration: Declaration) -> None:
    """So declaring a narrower owner never depends on where in the list it was written."""
    tier, owner = declaration.audit.tier_for("engine/kernel/meta.py")
    assert tier == "R1-CONSTITUTIONAL"
    assert owner
    assert declaration.audit.tier_for("engine/nothing_declared/x.py") == ("", "")


def test_an_unclaimed_module_takes_the_declared_undeclared_tier(inventory: dict) -> None:
    assert inventory["undeclared_tier"] in {row["tier"] for row in inventory["risk_tiers"]}


def test_a_disclosed_closure_takes_the_deliberate_tier(inventory: dict) -> None:
    """R4 is a property of the disclosure, not of the module prefix."""
    disclosed = [c for c in inventory["closures"] if c["disclosed"]]
    assert disclosed
    assert {c["tier"] for c in disclosed} == {"R4-DELIBERATE"}


def test_the_inventory_reports_a_real_population(inventory: dict) -> None:
    counts = inventory["counts"]
    assert counts["total"] > 500, "an inventory this small is not measuring the repository"
    assert counts["modules_with_closures"] > 100
    assert set(counts["by_form"]) == audit.available_forms()
    for form in audit.available_forms():
        assert inventory["limitations"][form]
        assert inventory["migrations"][form]


def test_the_live_inventory_ratchet_holds(inventory: dict) -> None:
    assert audit.validate(inventory) == []
    assert inventory["undisclosed_in_governed_scope"] == []
    assert inventory["stale_disclosures"] == []
    assert inventory["baseline_exceeded"] == {}


def test_the_inventory_is_deterministic(probe: Probe) -> None:
    first = audit.inventory(probe.declaration, probe.repo)
    second = audit.inventory(probe.declaration, probe.repo)
    assert audit.rendered(first) == audit.rendered(second)
    assert audit.digest(first) == audit.digest(second)


def test_an_undisclosed_closure_in_governed_scope_is_a_violation(inventory: dict) -> None:
    forged = json.loads(json.dumps(inventory))
    forged["undisclosed_in_governed_scope"] = [
        {"module": "engine/construct/x.py", "line": 1, "symbol": "S", "form": "ENUM_CLASS"}
    ]
    assert audit.validate(forged)


def test_a_stale_disclosure_is_a_violation(inventory: dict) -> None:
    """The disclosures cannot rot into claims about the past."""
    forged = json.loads(json.dumps(inventory))
    forged["stale_disclosures"] = ["UCON-CL-99"]
    assert any("stale" in problem for problem in audit.validate(forged))


def test_exceeding_the_baseline_is_a_violation(inventory: dict) -> None:
    forged = json.loads(json.dumps(inventory))
    forged["baseline_exceeded"] = {"ENUM_CLASS": {"baseline": 246, "measured": 247}}
    assert any("ratchet" in problem for problem in audit.validate(forged))


def test_an_unparseable_module_is_reported_rather_than_crashing_the_audit(
    declaration: Declaration, tmp_path
) -> None:
    module = tmp_path / "engine" / "broken.py"
    module.parent.mkdir(parents=True)
    module.write_text("def (:::\n", encoding="utf-8")
    spec = replace(declaration.audit, roots=("engine",))
    forged = replace(declaration, audit=spec)
    assert audit.scan(forged, str(tmp_path)) == ()
    assert "engine/broken.py" in audit.unscannable(forged, str(tmp_path))


def test_the_audit_verifies_itself(probe: Probe) -> None:
    result = audit.verify(probe.declaration, probe.repo)
    assert result["deterministic"] is True
    assert result["status"] == "PASS", result["problems"]


# --- the laws -------------------------------------------------------------------------------


def test_every_declared_law_holds_on_the_live_repository(report: dict) -> None:
    """The headline measurement. Every violation is named rather than summarised."""
    refused = [row for row in report["laws"] if row["verdict"] == REFUSED]
    assert refused == [], "\n".join(
        f"{row['law_id']}: " + "; ".join(row["violations"]) for row in refused
    )
    assert report["status"] == "OPEN"
    assert report["counts"]["holds"] == report["counts"]["laws"]


def test_the_report_measures_every_declared_law(report: dict, declaration: Declaration) -> None:
    assert [row["law_id"] for row in report["laws"]] == [law.law_id for law in declaration.laws]
    for row in report["laws"]:
        assert row["verdict"] in {HOLDS, REFUSED}
        assert row["statement"]


def test_laws_and_checks_are_bound_in_both_directions(declaration: Declaration) -> None:
    assert {law.check for law in declaration.laws} == available_checks()
    assert set(LAW_CHECKS) == available_checks()


def test_a_single_law_can_be_measured_alone() -> None:
    report = measure(laws=["UCON-L-10"])
    assert [row["law_id"] for row in report["laws"]] == ["UCON-L-10"]


@pytest.mark.parametrize(
    ("check", "mutate"),
    [
        (
            "catch_all_is_non_destructive",
            lambda d: replace(d, catch_all_disposition="REJECT"),
        ),
        (
            "no_state_is_terminal",
            lambda d: replace(
                d,
                dispositions=(
                    replace(d.dispositions[0], terminal=True),
                    *d.dispositions[1:],
                ),
            ),
        ),
        (
            "disposition_is_total",
            lambda d: replace(d, rules=(d.rules[-1], *d.rules[:-1])),
        ),
        (
            "vocabulary_is_not_duplicated",
            lambda d: replace(
                d,
                reality_states=(
                    replace(
                        d.reality_states[0],
                        ceu_binding={"population": "no-such-population", "member": "x"},
                    ),
                    *d.reality_states[1:],
                ),
            ),
        ),
    ],
)
def test_each_law_refuses_a_declaration_that_violates_it(
    declaration: Declaration, check: str, mutate
) -> None:
    """Holding proves nothing unless the law can be made to refuse."""
    forged = Probe(declaration=mutate(declaration), repo=REPO)
    assert LAW_CHECKS[check](forged), f"{check} accepted a declaration that violates it"


def test_the_independence_law_is_structural_not_conventional(probe: Probe) -> None:
    """Two modules that cannot see each other cannot derive one answer from the other."""
    for module, banned in (
        ("reality.py", "engine.construct.disposition"),
        ("disposition.py", "engine.construct.reality"),
    ):
        tree = ast.parse(probe.source(module))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        assert banned not in imported


def test_the_whole_disposition_by_reality_cross_product_is_representable(
    declaration: Declaration,
) -> None:
    """Admission and truth are independently settable, or one implies the other."""
    realized = set()
    registry = ConstructRegistry(declaration)
    for disposition in declaration.disposition_ids:
        for status in declaration.reality_ids:
            construct = registry.present(
                Presentation(
                    kind="entity",
                    natural_key=f"pair-{disposition}-{status}",
                    evidence=(Evidence(source="t", statement="offered"),),
                )
            )
            if construct.disposition.disposition != disposition:
                construct = registry.redispose(
                    construct.identity,
                    disposition=disposition,
                    rule_id="TEST",
                    rationale="measured",
                )
            if construct.reality.status != status:
                construct = registry.reassess(construct.identity, status)
            realized.add((construct.disposition.disposition, construct.reality.status))
    assert len(realized) == len(declaration.disposition_ids) * len(declaration.reality_ids)


def test_admitting_a_construct_never_licenses_certification(declaration: Declaration) -> None:
    """The single sentence the whole capability exists to make operational."""
    registry = ConstructRegistry(declaration)
    construct = registry.present(
        Presentation(
            kind="entity",
            natural_key="admitted",
            reality_status="HYPOTHETICAL",
            evidence=(Evidence(source="t", statement="offered"),),
        )
    )
    if construct.disposition.disposition != "ADMIT":
        construct = registry.redispose(
            construct.identity, disposition="ADMIT", rule_id="TEST", rationale="measured"
        )
    assert construct.disposition.disposition == "ADMIT"
    assert reality.permits(declaration, construct, "certify") is False


def test_admitting_a_future_category_changes_no_source_byte(probe: Probe) -> None:
    """The strongest available form of the openness claim."""
    before = dict(probe.fingerprint())
    registry = probe.fresh_registry()
    for name in ("a-category-from-the-future", "another-one-nobody-modelled"):
        extension.register_kind(registry, name, definition="declared by a test", declared_by="test")
        instance = registry.present(
            Presentation(
                kind=name,
                natural_key=f"instance-of-{name}",
                evidence=(Evidence(source="t", statement="exists"),),
            )
        )
        assert instance.kind_registered
        assert instance.disposition.disposition != "TRANSFORM"

    assert _package_fingerprint(probe.repo) == before


def test_the_reality_vocabulary_binds_to_the_owner_rather_than_copying_it(
    declaration: Declaration,
) -> None:
    """UCOS-CEU-001 owns the existence and epistemic states; this declaration references them."""

    populations = {str(name): {str(row[0]) for row in rows} for name, rows in SEED_POPULATIONS}
    bound = 0
    for spec in declaration.reality_states:
        if spec.ceu_binding is None:
            gap = spec.binding_gap or {}
            assert gap.get("gap_id") and gap.get("finding") and gap.get("referred_to")
            continue
        population = spec.ceu_binding["population"]
        assert population in populations
        assert spec.ceu_binding["member"] in populations[population]
        bound += 1
    assert bound >= 1, "no reality state binds to the vocabulary owner at all"


# --- the gate and the one-command surface ---------------------------------------------------


def test_the_gate_is_open_on_the_live_repository(capsys) -> None:
    assert construct_gate.main(["--gate", "--quiet"]) == construct_gate.EXIT_OPEN


def test_the_gate_emits_valid_json(capsys) -> None:
    assert construct_gate.main(["--json", "--quiet"]) == construct_gate.EXIT_OPEN
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == "ucos-construct-foundation-report"
    assert payload["status"] == "OPEN"


def test_the_gate_renders_a_summary_naming_every_law(capsys) -> None:
    assert construct_gate.main([]) == construct_gate.EXIT_OPEN
    rendered = capsys.readouterr().err
    for law_id in (f"UCON-L-{index:02d}" for index in range(1, 17)):
        assert law_id in rendered


def test_an_unreadable_declaration_is_a_fault_and_not_a_refusal(capsys, tmp_path) -> None:
    """Exit 2 exists so an unreadable declaration cannot pass as whichever answer suits."""
    code = construct_gate.main(["--gate", "--declaration", str(tmp_path / "absent.json")])
    assert code == construct_gate.EXIT_FAULT
    assert "FAULT" in capsys.readouterr().err


def test_the_gate_can_emit_the_closure_inventory(capsys) -> None:
    assert construct_gate.main(["--inventory", "--quiet"]) == construct_gate.EXIT_OPEN
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == "ucos-construct-closure-inventory"
    assert payload["closed_set"] is False


@pytest.mark.parametrize(
    "argv",
    [
        ["laws"],
        ["laws", "--json"],
        ["audit"],
        ["audit", "--json"],
        ["registry"],
        ["discover"],
        ["dispose", "--kind", "entity", "--key", "k"],
        ["dispose", "--kind", "unknown", "--key", "u", "--escalate"],
        ["permits", "--disposition", "ADMIT", "--reality", "HYPOTHETICAL"],
    ],
)
def test_every_cli_subcommand_succeeds(capsys, argv: list[str]) -> None:
    assert construct_cli.main(argv) == construct_cli.EXIT_OK
    capsys.readouterr()


def test_the_cli_reports_a_fault_rather_than_raising(capsys) -> None:
    code = construct_cli.main(["--declaration", "/nonexistent/x.json", "registry"])
    assert code == construct_cli.EXIT_FAULT
    assert "FAULT" in capsys.readouterr().err


def test_the_cli_explains_why_an_act_is_refused(capsys) -> None:
    construct_cli.main(["permits", "--disposition", "ADMIT", "--reality", "HYPOTHETICAL"])
    payload = json.loads(capsys.readouterr().out)
    assert "certify" not in payload["permitted"]
    assert "HYPOTHETICAL" in payload["refused"]["certify"]


# --- determinism, no clock, writes nothing --------------------------------------------------


def test_the_report_embeds_no_clock_reading(report: dict) -> None:
    """A wall-clock reading would make two identical runs produce different bytes."""
    body = json.dumps(report, sort_keys=True)
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", body)


def test_the_report_embeds_no_absolute_machine_path(report: dict) -> None:
    body = json.dumps(report, sort_keys=True)
    assert REPO not in body
    assert os.path.expanduser("~") not in body


def test_two_measurements_of_one_state_are_byte_identical() -> None:
    assert rendered(measure(laws=["UCON-L-10"])) == rendered(measure(laws=["UCON-L-10"]))


def test_measuring_the_repository_writes_nothing() -> None:
    """OBSERVE MODE, verified against git rather than asserted in a docstring."""

    def status() -> str:
        return subprocess.run(  # noqa: S603
            ["git", "status", "--porcelain"],  # noqa: S607
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        ).stdout

    before = status()
    assert construct_gate.main(["--gate", "--quiet"]) == construct_gate.EXIT_OPEN
    assert status() == before


def test_evidence_is_written_atomically_and_completely(declaration: Declaration, tmp_path) -> None:
    report = measure(laws=["UCON-L-10"])
    inventory = {"schema": "ucos-construct-closure-inventory", "counts": {}}
    written = evidence.write(
        declaration, report, inventory, repository=str(tmp_path), command="test"
    )
    assert len(written) == len(declaration.evidence_records)
    for path in written:
        assert path.exists()
        assert not path.with_suffix(path.suffix + ".tmp").exists()
        assert json.loads(path.read_text(encoding="utf-8"))
    payload = json.loads(written[0].read_text(encoding="utf-8"))
    assert payload["observed_at"]
    assert payload["schema"] == "ucos-construct-evidence"


def test_a_declared_evidence_record_nothing_produces_is_a_fault(
    declaration: Declaration,
) -> None:
    forged = replace(
        declaration,
        evidence_records=(*declaration.evidence_records, {"record": "never-written.json"}),
    )
    with pytest.raises(evidence.EvidenceError, match="nothing produces"):
        evidence.assert_complete(forged, {"report": {}, "inventory": {}})


def test_the_contract_loader_refuses_an_incoherent_declaration(tmp_path) -> None:
    document = json.loads(
        open(os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json")).read()
    )
    document["laws"].append(
        {"law_id": "UCON-L-99", "statement": "s", "check": "not_implemented", "blocking": True}
    )
    path = tmp_path / "forged.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(DeclarationError, match="incoherent"):
        load_contract(str(path))


# --- non-vacuity: every law must be capable of refusing ------------------------------------
#
# A law that holds and cannot be made to fail measures nothing. Each forgery below is a state
# the law is supposed to reject; the assertion is that it does. Where a law measures the
# repository's own bytes rather than the declaration (UCON-L-08, UCON-L-16) the forgery is a
# synthetic repository rather than a mutated declaration.


def _forged(declaration: Declaration, **changes) -> Probe:
    return Probe(declaration=replace(declaration, **changes), repo=REPO)


def test_the_operator_binding_law_refuses_an_unimplemented_operator(
    declaration: Declaration,
) -> None:
    last = declaration.rules[-1]
    forged = _forged(
        declaration,
        rules=(
            *declaration.rules[:-1],
            replace(last, when=(Clause(operator="not_implemented_anywhere", arguments={}),)),
        ),
    )
    problems = LAW_CHECKS["operators_are_two_way_bound"](forged)
    assert any("not implemented" in problem for problem in problems)


def test_the_no_silent_drop_law_refuses_an_unreadable_rejection(
    declaration: Declaration,
) -> None:
    """If REJECT stopped permitting reference, a refusal would become unreadable."""
    specs = tuple(
        replace(spec, permits=frozenset()) if spec.identifier == "REJECT" else spec
        for spec in declaration.dispositions
    )
    problems = LAW_CHECKS["nothing_is_silently_ignored"](_forged(declaration, dispositions=specs))
    assert any("indistinguishable from never having been presented" in p for p in problems)


def test_the_first_class_law_refuses_a_contradiction_that_never_stands(
    declaration: Declaration,
) -> None:
    problems = LAW_CHECKS["unknown_and_contradiction_are_first_class"](
        _forged(declaration, contradicting_states=frozenset())
    )
    assert any("not reported as standing" in problem for problem in problems)


def test_the_discovery_law_refuses_a_vacuous_walk(declaration: Declaration) -> None:
    """Discovery that mints nothing over an unattended unknown is not converging, it is idle."""
    problems = LAW_CHECKS["discovery_reaches_a_fixed_point"](
        _forged(declaration, discovery_sources=())
    )
    assert any("vacuous" in problem for problem in problems)


def test_the_extension_law_refuses_an_unimplemented_admission(declaration: Declaration) -> None:
    point = declaration.extension_points[0]
    problems = LAW_CHECKS["extension_points_are_exercisable"](
        _forged(
            declaration,
            extension_points=(replace(point, admission="not_implemented_anywhere"),),
        )
    )
    assert any("admission" in problem for problem in problems)


def test_the_independence_law_refuses_an_admission_that_confers_certification(
    declaration: Declaration,
) -> None:
    """If HYPOTHETICAL permitted certification, admission would imply truth."""
    states = tuple(
        replace(spec, permits=spec.permits | {"certify"})
        if spec.identifier == "HYPOTHETICAL"
        else spec
        for spec in declaration.reality_states
    )
    problems = LAW_CHECKS["reality_is_independent_of_admission"](
        _forged(declaration, reality_states=states)
    )
    assert any("admission implies truth" in problem for problem in problems)


def test_the_verifier_law_refuses_a_facet_that_does_not_require_its_own_assumptions(
    declaration: Declaration,
) -> None:
    facets = dict(declaration.facets)
    facets["verifier"] = replace(facets["verifier"], required_fields=("verifies",))
    problems = LAW_CHECKS["verification_is_itself_verifiable"](_forged(declaration, facets=facets))
    assert any("does not require" in problem for problem in problems)


def test_the_claim_law_refuses_a_scan_that_looks_for_nothing(declaration: Declaration) -> None:
    scan = {**declaration.claim_scan, "phrases": []}
    problems = LAW_CHECKS["no_completeness_claim_is_declared"](
        _forged(declaration, claim_scan=scan)
    )
    assert any("vacuous" in problem for problem in problems)


def test_the_claim_law_refuses_a_stale_exemption(declaration: Declaration) -> None:
    scan = {
        **declaration.claim_scan,
        "preserved_sites": [
            {"module": "engine/construct/model.py", "phrase": "guaranteed first", "reason": "none"}
        ],
    }
    problems = LAW_CHECKS["no_completeness_claim_is_declared"](
        _forged(declaration, claim_scan=scan)
    )
    assert any("stale" in problem for problem in problems)


def test_the_claim_law_refuses_an_undeclared_occurrence(declaration: Declaration, tmp_path) -> None:
    module = tmp_path / "engine" / "construct" / "boastful.py"
    module.parent.mkdir(parents=True)
    module.write_text('"""This capability offers guaranteed first discovery."""\n', "utf-8")
    probe = Probe(
        declaration=replace(
            declaration, claim_scan={**declaration.claim_scan, "preserved_sites": []}
        ),
        repo=str(tmp_path),
    )
    problems = LAW_CHECKS["no_completeness_claim_is_declared"](probe)
    assert any("guarantee vocabulary" in problem for problem in problems)


def test_the_closure_law_refuses_a_lowered_baseline(declaration: Declaration) -> None:
    """The ratchet may hold or fall; measuring above it is a violation."""
    spec = replace(declaration.audit, baseline={form: 0 for form in audit.available_forms()})
    problems = LAW_CHECKS["closure_inventory_holds"](_forged(declaration, audit=spec))
    assert any("exceeds the declared baseline" in problem for problem in problems)


def test_the_closure_law_refuses_an_undisclosed_closure_in_scope(
    declaration: Declaration,
) -> None:
    spec = replace(declaration.audit, disclosures=())
    problems = LAW_CHECKS["closure_inventory_holds"](_forged(declaration, audit=spec))
    assert any("no disclosure" in problem for problem in problems)


def test_the_openness_law_refuses_a_package_it_cannot_read(
    declaration: Declaration, tmp_path
) -> None:
    with pytest.raises(ContractError, match="absent"):
        LAW_CHECKS["future_kinds_need_no_redesign"](
            Probe(declaration=declaration, repo=str(tmp_path))
        )


def test_the_totality_law_refuses_a_parameterised_catch_all(declaration: Declaration) -> None:
    last = declaration.rules[-1]
    forged = _forged(
        declaration,
        rules=(
            *declaration.rules[:-1],
            replace(last, when=(Clause(operator="kind_in", arguments={"kinds": ["entity"]}),)),
        ),
    )
    problems = LAW_CHECKS["disposition_is_total"](forged)
    assert any("condition rather than a catch-all" in problem for problem in problems)


def test_the_terminal_law_refuses_an_unfalsifiable_verified_state(
    declaration: Declaration,
) -> None:
    """A VERIFIED that cannot fall to something weaker claims a verification is permanent."""
    states = tuple(
        replace(spec, successors=("REPRODUCED",)) if spec.identifier == "VERIFIED" else spec
        for spec in declaration.reality_states
    )
    problems = LAW_CHECKS["no_state_is_terminal"](_forged(declaration, reality_states=states))
    assert any("could never be overturned" in problem for problem in problems)


def test_the_terminal_law_refuses_an_unreachable_state(declaration: Declaration) -> None:
    """A state nothing can reach is one the framework declares and can never occupy."""
    stranded = "VERIFIED"
    states = tuple(
        replace(spec, successors=tuple(s for s in spec.successors if s != stranded))
        for spec in declaration.reality_states
    )
    problems = LAW_CHECKS["no_state_is_terminal"](_forged(declaration, reality_states=states))
    assert any("unreachable" in problem and stranded in problem for problem in problems)


# --- the declaration's remaining refusals ---------------------------------------------------


def test_a_thoroughly_broken_declaration_names_every_defect(declaration: Declaration) -> None:
    """One forgery, many defects: validate must report all of them rather than the first."""
    forged = replace(
        declaration,
        reflective_root="not-a-kind",
        initial_reality_state="NOT-A-STATE",
        seed_reality_state="ALSO-NOT-A-STATE",
        kinds=(
            replace(declaration.kinds[0], facet="no-such-facet"),
            replace(declaration.kinds[1], parent="no-such-parent"),
        ),
        rules=(replace(declaration.rules[-1], disposition="NOT-A-DISPOSITION"),),
        extension_points=(
            replace(
                declaration.extension_points[0],
                kind="not-a-kind",
                exercised_by="UCON-L-99",
                admission="not_an_admission",
            ),
        ),
        discovery_sources=(
            replace(declaration.discovery_sources[0], priority="P99", impact="cosmic"),
        ),
        audit=replace(
            declaration.audit,
            undeclared_tier="NOT-A-TIER",
            deliberate_tier="ALSO-NOT-A-TIER",
            baseline={},
        ),
    )
    problems = " | ".join(
        forged.validate(
            available_checks(),
            available_operators(),
            views.available_selectors(),
            extension.available_admissions(),
            audit.available_forms(),
        )
    )
    for expected in (
        "reflective root",
        "initial_reality_state",
        "seed_reality_state",
        "undeclared facet",
        "absent parent",
        "undeclared disposition",
        "undeclared kind",
        "not a declared law",
        "not implemented",
        "undeclared priority",
        "undeclared impact",
        "undeclared_tier",
        "deliberate_tier",
        "no declared baseline",
    ):
        assert expected in problems, f"validate did not report {expected!r}"


def test_a_disclosure_that_is_not_intentional_must_name_a_gap(declaration: Declaration) -> None:
    spec = replace(
        declaration.audit,
        disclosures=(replace(declaration.audit.disclosures[0], intentional=False, gap=None),),
    )
    problems = replace(declaration, audit=spec).validate(available_checks(), available_operators())
    assert any("undisclosed finite assumption" in problem for problem in problems)


def test_a_disclosure_naming_an_undeclared_form_is_refused(declaration: Declaration) -> None:
    spec = replace(
        declaration.audit,
        disclosures=(replace(declaration.audit.disclosures[0], form="NOT-A-FORM"),),
    )
    problems = replace(declaration, audit=spec).validate(available_checks(), available_operators())
    assert any("undeclared closure form" in problem for problem in problems)


def test_a_detectable_form_the_declaration_omits_is_refused(declaration: Declaration) -> None:
    problems = declaration.validate(
        available_checks(),
        available_operators(),
        available_forms=audit.available_forms() | {"AN_UNDECLARED_FORM"},
    )
    assert any("the declaration omits it" in problem for problem in problems)


def test_a_selector_or_admission_the_declaration_omits_is_refused(
    declaration: Declaration,
) -> None:
    problems = declaration.validate(
        available_checks(),
        available_operators(),
        views.available_selectors() | {"unclaimed_selector"},
        extension.available_admissions() | {"unclaimed_admission"},
    )
    assert any("no discovery source claims it" in problem for problem in problems)
    assert any("no extension point claims it" in problem for problem in problems)


def test_require_valid_raises_and_names_the_problems(declaration: Declaration) -> None:
    with pytest.raises(DeclarationError, match="incoherent"):
        replace(declaration, reflective_root="nope").require_valid(
            available_checks(), available_operators()
        )


def test_repo_root_locates_the_repository() -> None:
    assert os.path.isdir(os.path.join(repo_root(), "00-MASTER", "UCON-000001"))


def test_a_non_object_declaration_is_refused() -> None:
    with pytest.raises(DeclarationError, match="JSON object"):
        parse(["not", "an", "object"])  # type: ignore[arg-type]


def test_a_malformed_section_is_refused() -> None:
    document = json.loads(
        open(os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json")).read()
    )
    document["dispositions"] = "not a list"
    with pytest.raises(DeclarationError, match="non-empty list"):
        parse(document)


def test_a_section_holding_a_non_object_row_is_refused() -> None:
    document = json.loads(
        open(os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json")).read()
    )
    document["dispositions"] = ["ADMIT"]
    with pytest.raises(DeclarationError, match="non-object row"):
        parse(document)


# --- the remaining engine surfaces ----------------------------------------------------------


def test_the_registry_projections_filter_the_one_store(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    construct = registry.present(
        Presentation(
            kind="entity",
            natural_key="projected",
            reality_status="OBSERVED",
            evidence=(Evidence(source="s", statement="seen"),),
        )
    )
    assert construct in registry.of_kind("entity")
    assert construct in registry.with_disposition(construct.disposition.disposition)
    assert construct in registry.with_reality("OBSERVED")
    assert construct in registry.of_facet(registry.facet_of("entity"))
    assert registry.summary()["kinds"]["entity"] >= 1


def test_only_a_presentation_may_be_presented(registry: ConstructRegistry) -> None:
    with pytest.raises(RegistryError, match="only a Presentation"):
        registry.present({"kind": "entity"})  # type: ignore[arg-type]


def test_only_a_declaration_may_be_adopted(registry: ConstructRegistry) -> None:
    with pytest.raises(RegistryError, match="only a Declaration"):
        registry.adopt({"artifact_id": "UCON-000001"})  # type: ignore[arg-type]


def test_a_runtime_kind_may_declare_its_own_facet(registry: ConstructRegistry) -> None:
    """A kind registered at runtime carries the facet its registration declared."""
    extension.register_kind(
        registry,
        "runtime-unknown-like",
        definition="a runtime kind with a declared facet",
        facet="unknown",
        declared_by="test",
    )
    assert registry.facet_of("runtime-unknown-like") == "unknown"
    assert registry.facet_of("a-kind-that-declares-nothing") == "none"


def test_registering_a_kind_may_also_extend_the_declaration(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    before = len(registry.declaration.kinds)
    extension.register_kind(
        registry,
        "declared-too",
        definition="d",
        facet="none",
        declared_by="test",
        extend_declaration=True,
    )
    assert len(registry.declaration.kinds) == before + 1
    assert registry.declaration.kind("declared-too").definition == "d"


def test_extending_with_a_kind_naming_an_undeclared_facet_is_refused(
    declaration: Declaration,
) -> None:
    with pytest.raises(ExtensionError, match="not declared"):
        extension.extended_with_kind(declaration, "x", definition="d", facet="no-such-facet")


def test_exercising_an_unimplemented_admission_is_a_fault(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    forged = ConstructRegistry(
        replace(
            declaration,
            extension_points=(replace(declaration.extension_points[0], admission="nope"),),
        )
    )
    with pytest.raises(ExtensionError, match="not implemented"):
        extension.exercise(forged, declaration.extension_points[0].point_id)


def test_a_presentation_and_its_records_serialise_deterministically(
    registry: ConstructRegistry,
) -> None:
    construct = registry.present(
        Presentation(
            kind="entity",
            natural_key="serialised",
            evidence=(Evidence(source="s", statement="seen"),),
        )
    )
    body = construct.as_dict()
    assert body["identity"] == construct.identity
    assert body["presentation"]["evidence"][0]["source"] == "s"
    assert construct.presentation.content_digest() == construct.presentation.content_digest()
    superseded = construct.reality.superseded("next")
    assert superseded.active is False
    assert superseded.superseded_by == "next"
    assert registry.journal[-1].as_dict()["entry_hash"]


def test_the_discovery_report_counts_by_priority_and_impact(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    views.register_unknown(
        registry,
        natural_key="U-report",
        unknown_class=declaration.unknown_classes[0],
        domain="d",
        formulation="f",
    )
    views.discover(registry)
    report = views.discovery_report(registry)
    assert report["unknowns"] >= 1
    assert report["discovery_objects"] >= 1
    assert sum(report["by_priority"].values()) == report["discovery_objects"]
    assert sum(report["by_impact"].values()) == report["discovery_objects"]


def test_derived_identities_are_computable_without_minting(
    registry: ConstructRegistry, declaration: Declaration
) -> None:
    subject = registry.present(Presentation(kind="entity", natural_key="subject"))
    expected = views.research_identity(registry, subject.identity)
    assert not registry.has(expected)
    assert views.promote_to_research(registry, subject.identity).identity == expected
    assert views.discovery_key(registry, subject.identity).startswith(
        declaration.discovery_key_prefix
    )


# --- the gate's remaining paths and the module entry point ----------------------------------


def test_the_gate_writes_evidence_only_when_asked(capsys, tmp_path) -> None:
    """OBSERVE MODE by default. The evidence home is created only on an explicit request."""
    home = tmp_path / ".ucos" / "construct"
    assert not home.exists()
    declaration_path = os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json")
    code = construct_gate.main(
        [
            "--law",
            "UCON-L-10",
            "--evidence",
            "--declaration",
            declaration_path,
            "--repository",
            str(tmp_path),
            "--quiet",
        ]
    )
    capsys.readouterr()
    assert code == construct_gate.EXIT_OPEN
    assert (home / "construct-foundation-report.json").exists()
    assert (home / "closure-inventory.json").exists()


def test_the_gate_closes_when_a_blocking_law_is_refused(capsys, tmp_path) -> None:
    """Exit 1 is a measured refusal, distinct from exit 2 which is no verdict at all."""
    document = json.loads(
        open(os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json")).read()
    )
    document["disposition_rules"]["catch_all_disposition"] = "REJECT"
    path = tmp_path / "forged.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    code = construct_gate.main(["--gate", "--declaration", str(path), "--law", "UCON-L-03"])
    rendered = capsys.readouterr().err
    assert code == construct_gate.EXIT_CLOSED
    assert "XX" in rendered
    assert "CLOSED" in rendered


def test_the_inventory_gate_closes_on_a_ratchet_violation(capsys, tmp_path) -> None:
    document = json.loads(
        open(os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json")).read()
    )
    document["audit"]["baseline"] = {form: 0 for form in audit.available_forms()}
    path = tmp_path / "forged.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    code = construct_gate.main(["--gate", "--inventory", "--declaration", str(path)])
    out = capsys.readouterr()
    assert code == construct_gate.EXIT_CLOSED
    assert json.loads(out.out)["baseline_exceeded"]
    assert "ratchet" in out.err


def test_the_cli_can_write_the_inventory_to_a_named_path(capsys, tmp_path) -> None:
    target = tmp_path / "inventory.json"
    assert construct_cli.main(["audit", "--out", str(target)]) == construct_cli.EXIT_OK
    capsys.readouterr()
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["schema"] == "ucos-construct-closure-inventory"
    assert payload["counts"]["total"] > 500


def test_the_cli_fails_when_a_law_is_refused(capsys, tmp_path) -> None:
    document = json.loads(
        open(os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json")).read()
    )
    document["disposition_rules"]["catch_all_disposition"] = "REJECT"
    path = tmp_path / "forged.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    code = construct_cli.main(["--declaration", str(path), "laws", "--law", "UCON-L-03"])
    capsys.readouterr()
    assert code == construct_cli.EXIT_FAILED


def test_the_cli_dispose_reports_the_full_trace_and_refusals(capsys) -> None:
    construct_cli.main(
        [
            "dispose",
            "--kind",
            "entity",
            "--key",
            "cli-traced",
            "--payload",
            '{"provenance": "unattributed"}',
            "--evidence",
            "a-source",
            "--reality",
            "HYPOTHETICAL",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["construct"]["disposition"] == "QUARANTINE"
    assert payload["refusals"]["certify"]
    assert len(payload["trace"]) >= 10
    assert sum(1 for row in payload["trace"] if row["selected"]) == 1


def test_the_cli_rejects_a_malformed_payload(capsys) -> None:
    code = construct_cli.main(
        ["dispose", "--kind", "entity", "--key", "k", "--payload", "{not json"]
    )
    capsys.readouterr()
    assert code == construct_cli.EXIT_FAULT


def test_the_module_entry_point_is_reachable() -> None:
    """`python -m engine.construct` must reach the same surface the console script publishes."""
    interpreter = os.path.join(REPO, ".ec1-venv", "bin", "python")
    result = subprocess.run(  # noqa: S603
        [
            interpreter,
            "-m",
            "engine.construct",
            "permits",
            "--disposition",
            "ADMIT",
            "--reality",
            "UNKNOWN",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["disposition"] == "ADMIT"


def test_evidence_requires_a_declared_home(declaration: Declaration, tmp_path) -> None:
    with pytest.raises(evidence.EvidenceError, match="no evidence home"):
        evidence.home(replace(declaration, evidence_home=""), str(tmp_path))


def test_evidence_refuses_a_payload_missing_a_declared_record(declaration: Declaration) -> None:
    with pytest.raises(evidence.EvidenceError, match="carries no"):
        evidence.assert_complete(declaration, {"report": {}})


def test_the_detector_cache_cannot_serve_a_stale_answer(declaration: Declaration, tmp_path) -> None:
    """Memoisation is keyed on content, so a changed byte is a changed key, never a stale hit."""
    module = tmp_path / "engine" / "mutating.py"
    module.parent.mkdir(parents=True)
    spec = replace(declaration.audit, roots=("engine",))
    forged = replace(declaration, audit=spec)

    module.write_text("VOCABULARY = ('a', 'b')\n", encoding="utf-8")
    first = audit.scan(forged, str(tmp_path))
    assert [(c.symbol, c.members) for c in first] == [("VOCABULARY", 2)]

    module.write_text("VOCABULARY = ('a', 'b', 'c', 'd')\n", encoding="utf-8")
    second = audit.scan(forged, str(tmp_path))
    assert [(c.symbol, c.members) for c in second] == [("VOCABULARY", 4)]


# --- certification identity completeness -----------------------------------------------------
#
# THE OTHER HALF OF A PROPERTY THIS FILE ONLY EVER ASSERTED ONE HALF OF.
#
# `test_the_declaration_digest_excludes_its_source` and
# `test_extending_the_declaration_does_not_mutate_the_original` both assert that the digest is
# STABLE. Stability alone cannot detect the defect class that was actually present here:
# `digest_payload` listed eleven keys by hand and collapsed ten of them to bare identifier
# lists, so everything the specs SAID sat outside the certification identity. Measured, not
# supposed — flipping `blocking` on UCON-L-01, the flag `contract.py` reads to choose OPEN or
# CLOSED, left `declaration_digest` byte-identical at 192c63af…, and so did rewriting a rule's
# assigned disposition and zeroing an evidence floor. One digest certified two declarations that
# reached opposite verdicts.
#
# The payload is now derived from `dataclasses.fields`, so inclusion is the default and a field
# added to `Declaration` is inside the identity on the day it is written. These tests hold both
# halves and hold the exclusion list in both directions.


def _identity(document: dict) -> str:
    return content_hash(parse(document, source="test").digest_payload())


SEMANTIC_MUTATIONS: dict[str, object] = {
    "flip a law's blocking flag": lambda d: d["laws"][0].__setitem__(
        "blocking", not d["laws"][0]["blocking"]
    ),
    "rewrite a law's statement": lambda d: d["laws"][0].__setitem__("statement", "something else"),
    "rebind a law to another check": lambda d: d["laws"][0].__setitem__("check", "other_check"),
    "zero an evidence floor": lambda d: d["reality_states"][0].__setitem__("evidence_floor", 0),
    "zero an independent-sources floor": lambda d: d["reality_states"][0].__setitem__(
        "independent_sources_floor", 0
    ),
    "make a disposition terminal": lambda d: d["dispositions"][0].__setitem__("terminal", True),
    "drop a disposition": lambda d: d["dispositions"].pop(),
    "redefine a seed construct kind": lambda d: d["construct_kinds"]["seed"][-1].__setitem__(
        "definition", "this kind now means something else"
    ),
    "drop a seed construct kind": lambda d: d["construct_kinds"]["seed"].pop(),
    "change the declared authority": lambda d: d.__setitem__("authority", "SOMETHING ELSE"),
    "change the declared version": lambda d: d.__setitem__("version", "9.9.9"),
}


@pytest.mark.parametrize("name", sorted(SEMANTIC_MUTATIONS))
def test_every_semantic_mutation_moves_the_certification_identity(name: str) -> None:
    """A value that can alter a verdict must be inside the identity that certifies it."""
    document = json.loads(
        (Path(repo_root()) / "00-MASTER" / "UCON-000001" / "ucon-declaration.json").read_text(
            encoding="utf-8"
        )
    )
    baseline = _identity(copy.deepcopy(document))
    mutated = copy.deepcopy(document)
    SEMANTIC_MUTATIONS[name](mutated)
    assert _identity(mutated) != baseline, (
        f"{name!r} changed the declaration's meaning and left the certification identity at "
        f"{baseline[:16]}…. The same digest now certifies two different declarations."
    )


def test_the_identity_covers_every_parsed_field_except_the_declared_exclusions(
    declaration: Declaration,
) -> None:
    """Inclusion is the default; an omission must be a declared, reasoned exclusion."""
    payload = declaration.digest_payload()
    parsed = {field.name for field in dataclasses.fields(declaration)}
    missing = parsed - set(payload)
    assert missing <= set(DIGEST_EXCLUSIONS), (
        "fields silently absent from the certification identity: "
        f"{sorted(missing - set(DIGEST_EXCLUSIONS))}"
    )
    for name, reason in DIGEST_EXCLUSIONS.items():
        assert reason.strip(), f"exclusion {name!r} states no reason"


def test_a_stale_exclusion_is_refused(declaration: Declaration) -> None:
    """The other direction. An exclusion matching no field may silently widen later."""
    assert set(DIGEST_EXCLUSIONS) <= {
        field.name for field in dataclasses.fields(declaration)
    }, "an exclusion names a field this declaration no longer has"


def test_an_in_memory_extension_moves_the_identity(declaration: Declaration) -> None:
    """Extension is a semantic change too, and the identity taken over the SOURCE DOCUMENT
    would not have shown it — which is why the payload is taken over the parsed structure."""
    extended = extension.extended_with_disposition(
        declaration,
        "PROBE-IDENTITY-DISPOSITION",
        definition="a probe",
        permits=(declaration.operational_acts[0],),
        successors=(declaration.disposition_ids[0],),
    )
    assert content_hash(extended.digest_payload()) != content_hash(declaration.digest_payload())


# --- law mutation resistance -----------------------------------------------------------------
#
# MEASURED, NOT ASSUMED. Every law check in `LAW_CHECKS` was replaced, one at a time, with
# `return []` — the `return True` of a law engine — and this suite was re-run against the
# mutant in an isolated worktree. Fourteen of sixteen mutants were killed. TWO SURVIVED:
# `every_construct_is_disposed` (UCON-L-01, the foundational law) and
# `measurement_is_deterministic` (UCON-L-16). Both could be neutered completely while every
# gate reported OPEN and this suite stayed green — which is the exact condition UEC-L-05 names,
# "a detector nobody has shown can fail", sitting on the two laws the capability rests on.
#
# A gate cannot catch this on its own: a law that reports no violations is indistinguishable,
# from inside the gate, from a law that holds. The suite is the only possible detector, so the
# two tests below forge the state each law exists to refuse and require the law to say so —
# and the third test refuses any FUTURE law that arrives without one.


def test_l01_refuses_a_construct_that_carries_no_active_disposition(
    probe: Probe, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant `every_construct_is_disposed -> []` dies here.

    The law builds its own registry, so the forgery is applied to that registry: a construct
    reported as undisposed must be reported as a violation. If the law is neutered the list is
    empty and this fails, which is the whole point.
    """
    monkeypatch.setattr(
        ConstructRegistry,
        "undisposed",
        lambda self: ("forged/undisposed-construct",),
    )
    violations = LAW_CHECKS["every_construct_is_disposed"](probe)
    assert violations, "UCON-L-01 accepted a construct carrying no active disposition"
    assert any("forged/undisposed-construct" in item for item in violations)


def test_l16_refuses_a_measurement_that_does_not_reproduce(
    probe: Probe, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant `measurement_is_deterministic -> []` dies here.

    Two inventories of one repository state are made to differ. A law that reports nothing about
    that is a law that would not notice the day the inventory started reading a clock.
    """
    real = audit.inventory
    calls = {"n": 0}

    def drifting_inventory(*args, **kwargs):
        calls["n"] += 1
        result = dict(real(*args, **kwargs))
        result["counts"] = {**result["counts"], "total": result["counts"]["total"] + calls["n"]}
        return result

    monkeypatch.setattr(audit, "inventory", drifting_inventory)
    violations = LAW_CHECKS["measurement_is_deterministic"](probe)
    assert violations, "UCON-L-16 accepted two measurements of one state that differ"
    assert any("differ" in item for item in violations)


def test_every_law_check_is_named_by_this_suite() -> None:
    """The class-level guard. A law arriving without a forged-violation test fails HERE.

    The two survivors above were not found by reading the code; they were found by mutating
    every law in turn and re-running this suite in a worktree. That experiment is expensive and
    nobody will run it on every commit, so the cheap invariant it implies is enforced instead:
    a law check that this file never names cannot possibly have a test that exercises it, and a
    law nobody exercises is one nobody has shown can fail.

    Naming is necessary, not sufficient — this cannot prove the test is a good one. It is the
    strongest property available in-process, and it closes the door the two survivors came
    through.
    """
    source = Path(__file__).read_text(encoding="utf-8")
    unnamed = sorted(name for name in LAW_CHECKS if name not in source)
    assert not unnamed, (
        "law checks this suite never names, so nothing shows they can fail: " f"{unnamed}"
    )


# --- the refusal branches of the sixteen laws -------------------------------------------------
#
# Every law here holds on the live declaration, so only its HOLDS path had ever run and its
# refusal path was measured by nothing. Each test below drives one violation and asserts the
# message that violation produces — not that some problem was reported, which would pass on
# the wrong one. The doctored registry delegates everything it does not override to a real
# ConstructRegistry, so a law reaching any other behaviour reaches the genuine one.


class _DoctoredRegistry:
    def __init__(self, real, **overrides):
        object.__setattr__(self, "_real", real)
        object.__setattr__(self, "_overrides", overrides)

    def __getattr__(self, name):
        overrides = object.__getattribute__(self, "_overrides")
        if name in overrides:
            return overrides[name]
        return getattr(object.__getattribute__(self, "_real"), name)


class _ProbeWithRegistry(Probe):
    def __init__(self, declaration, registry):
        super().__init__(declaration=declaration, repo=REPO)
        object.__setattr__(self, "_doctored", registry)

    def fresh_registry(self):
        return object.__getattribute__(self, "_doctored")


def _registry_probe(declaration, base=None, **overrides):
    """A probe whose registry is `base` with named behaviours replaced.

    `base` is threaded through on purpose: a test that builds its own ConstructRegistry for the
    overrides and lets this helper build another ends up with two registries — one that records
    the presentations and one the law reads from — and the law then fails on a construct that
    was presented to the wrong instance.
    """
    real = base if base is not None else ConstructRegistry(declaration)
    return _ProbeWithRegistry(declaration, _DoctoredRegistry(real, **overrides))


class _Stand_in:
    """A construct-shaped object the model would refuse to build.

    `Construct.__post_init__` rejects no-disposition and two-active-disposition forms, which is
    exactly what the law's own non-vacuity check proves. Those refusals mean the model cannot
    produce the states the law's OTHER branches guard against, so reaching them needs an object
    that answers the same questions without passing through that validation. Everything the law
    reads is supplied; nothing else is.
    """

    def __init__(self, identity, dispositions, disposition, presentation=None, assessments=()):
        self.identity = identity
        self.dispositions = dispositions
        self.disposition = disposition
        self.presentation = presentation
        self.assessments = assessments


@dataclasses.dataclass(frozen=True)
class _Stand_in_disposition:
    """A disposition-shaped value the model would refuse to build.

    `DispositionRecord.__post_init__` requires a non-empty rule_id, so no real record can reach
    the law's `if not construct.disposition.rule_id` guard. That guard is defence in depth
    against a construct arriving from somewhere the model did not build, and the law itself
    proves the model refuses the forged forms. Exercising the guard therefore needs a value the
    model never made — which is precisely the situation the guard exists for.
    """

    disposition: str
    rule_id: str
    active: bool = True
    sequence: int = 0


def test_a_construct_with_the_wrong_number_of_active_dispositions_is_refused(declaration):
    real = ConstructRegistry(declaration)
    real.present_all(contract._hostile_presentations(declaration))
    everything = real.all()
    sample = everything[0]
    stand_in = _Stand_in(
        sample.identity,
        (),
        sample.disposition,
        presentation=sample.presentation,
        assessments=sample.assessments,
    )
    probe = _registry_probe(declaration, all=lambda: [stand_in])
    problems = contract.every_construct_is_disposed(probe)
    assert any("carries 0 active dispositions" in p for p in problems), problems


def test_a_construct_carrying_an_undeclared_disposition_is_refused(declaration):
    real = ConstructRegistry(declaration)
    real.present_all(contract._hostile_presentations(declaration))
    everything = real.all()
    sample = everything[0]
    forged = dataclasses.replace(
        sample,
        dispositions=(
            dataclasses.replace(sample.disposition, disposition="not-a-declared-disposition"),
        ),
    )
    probe = _registry_probe(declaration, all=lambda: [forged, *everything[1:]])
    problems = contract.every_construct_is_disposed(probe)
    assert any("undeclared disposition" in p for p in problems), problems


def test_a_disposition_naming_no_rule_is_refused(declaration):
    real = ConstructRegistry(declaration)
    real.present_all(contract._hostile_presentations(declaration))
    sample = real.all()[0]
    ruleless = _Stand_in_disposition(sample.disposition.disposition, rule_id="")
    stand_in = _Stand_in(
        sample.identity,
        (ruleless,),
        ruleless,
        presentation=sample.presentation,
        assessments=sample.assessments,
    )
    probe = _registry_probe(declaration, all=lambda: [stand_in])
    problems = contract.every_construct_is_disposed(probe)
    assert any("naming no rule" in p for p in problems), problems


# --- UCON-L-02: the totality refusals ------------------------------------------------------


def test_two_catch_all_rules_are_refused(declaration):
    doubled = (*declaration.rules, dataclasses.replace(declaration.rules[-1], rule_id="second"))
    problems = contract.disposition_is_total(
        Probe(declaration=dataclasses.replace(declaration, rules=doubled), repo=REPO)
    )
    assert any("catch-all rules are declared" in p for p in problems), problems
    # The law returns immediately: with the catch-all ambiguous, nothing after it can be read.
    assert len(problems) == 1, problems


def test_a_construct_selecting_the_wrong_rule_is_refused(declaration):
    real = ConstructRegistry(declaration)

    def wrong_rule(presentation):
        admitted = real.present(presentation)
        return dataclasses.replace(
            admitted,
            dispositions=(
                dataclasses.replace(
                    admitted.disposition, rule_id="a-rule-that-is-not-the-catch-all"
                ),
            ),
        )

    probe = _registry_probe(declaration, present=wrong_rule)
    problems = contract.disposition_is_total(probe)
    assert any("rather than the catch-all" in p for p in problems), problems


def test_a_catch_all_assigning_the_wrong_disposition_is_refused(declaration):
    real = ConstructRegistry(declaration)
    catch_all = [rule for rule in declaration.rules if rule.catch_all][0]
    other = [d for d in declaration.disposition_ids if d != catch_all.disposition][0]

    def wrong_disposition(presentation):
        admitted = real.present(presentation)
        return dataclasses.replace(
            admitted,
            dispositions=(dataclasses.replace(admitted.disposition, disposition=other),),
        )

    probe = _registry_probe(declaration, present=wrong_disposition)
    problems = contract.disposition_is_total(probe)
    assert any("the catch-all assigned" in p for p in problems), problems


def test_a_selection_engine_that_is_not_total_is_refused(declaration, monkeypatch):
    # Totality means every presentation, in any world, reaches a rule. An engine that raises
    # for an unknown kind has a hole in it, and the law performs the check rather than arguing.
    def refuse(*args, **kwargs):
        raise ConstructError("no rule matched")

    monkeypatch.setattr(contract, "select_rule", refuse)
    problems = contract.disposition_is_total(Probe(declaration=declaration, repo=REPO))
    assert any("disposition is not total" in p for p in problems), problems


# --- UCON-L-05: the nothing-ignored refusals -------------------------------------------------


def test_presenting_more_than_are_returned_is_refused(declaration):
    real = ConstructRegistry(declaration)
    probe = _registry_probe(declaration, base=real, present_all=lambda h: real.present_all(h)[:1])
    problems = contract.nothing_is_silently_ignored(probe)
    assert any("were returned" in p for p in problems), problems


def test_a_presented_construct_absent_from_the_registry_is_refused(declaration):
    real = ConstructRegistry(declaration)
    probe = _registry_probe(declaration, base=real, has=lambda identity: False)
    problems = contract.nothing_is_silently_ignored(probe)
    assert any("is not in the registry" in p for p in problems), problems


def test_a_population_smaller_than_the_presentations_is_refused(declaration):
    real = ConstructRegistry(declaration)
    seeded = list(real.all())
    probe = _registry_probe(declaration, base=real, all=lambda: seeded)
    problems = contract.nothing_is_silently_ignored(probe)
    assert any("distinct" in p and "identities were presented" in p for p in problems), problems


def test_a_broken_admission_journal_chain_is_refused(declaration):
    real = ConstructRegistry(declaration)
    probe = _registry_probe(declaration, base=real, chain_is_intact=lambda: False)
    problems = contract.nothing_is_silently_ignored(probe)
    assert any("admission journal chain is broken" in p for p in problems), problems


def test_a_rejected_construct_leaving_no_record_is_refused(declaration):
    real = ConstructRegistry(declaration)
    seen = {"redisposed": None}

    def redispose(identity, **kwargs):
        seen["redisposed"] = real.redispose(identity, **kwargs)
        return seen["redisposed"]

    def has(identity):
        # A rejection that erases the record is indistinguishable from never having been
        # presented, which is the whole condition this law exists to refuse.
        if seen["redisposed"] is not None and identity == seen["redisposed"].identity:
            return False
        return real.has(identity)

    probe = _registry_probe(declaration, base=real, redispose=redispose, has=has)
    problems = contract.nothing_is_silently_ignored(probe)
    assert any("rejected construct left no record" in p for p in problems), problems


# --- UCON-L-06: the first-class refusals ----------------------------------------------------


def test_a_registered_unknown_absent_from_its_registry_is_refused(declaration, monkeypatch):
    monkeypatch.setattr(views, "unknowns", lambda registry: ())
    problems = contract.unknown_and_contradiction_are_first_class(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("unknown is absent from the unknown registry" in p for p in problems), problems


def test_a_registered_contradiction_absent_from_its_registry_is_refused(declaration, monkeypatch):
    monkeypatch.setattr(views, "contradictions", lambda registry: ())
    problems = contract.unknown_and_contradiction_are_first_class(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("contradiction is absent from the contradiction registry" in p for p in problems)


def test_a_promoted_research_object_absent_from_its_registry_is_refused(declaration, monkeypatch):
    monkeypatch.setattr(views, "research_objects", lambda registry: ())
    problems = contract.unknown_and_contradiction_are_first_class(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("research object is absent from the research registry" in p for p in problems)


def test_promotion_that_is_not_idempotent_is_refused(declaration, monkeypatch):
    """Promotion must be a function of the construct, not of how often it was asked for.

    The law promotes the same construct twice and compares identities. A promotion that minted
    a new object each time would grow the research registry on every measurement — the registry
    would fill up with discoveries nobody made.
    """
    real = views.promote_to_research
    calls = {"n": 0}

    class _Elsewhere:
        def __init__(self, identity):
            self.identity = identity

    def multiplying(registry, identity):
        calls["n"] += 1
        promoted = real(registry, identity)
        if calls["n"] == 2:
            return _Elsewhere(promoted.identity + "-a-second-object")
        return promoted

    monkeypatch.setattr(views, "promote_to_research", multiplying)
    problems = contract.unknown_and_contradiction_are_first_class(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("promotion to research is not idempotent" in p for p in problems), problems


def test_a_registered_discovery_absent_from_its_registry_is_refused(declaration, monkeypatch):
    monkeypatch.setattr(views, "discovery_objects", lambda registry: ())
    problems = contract.unknown_and_contradiction_are_first_class(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("discovery object is absent from the discovery registry" in p for p in problems)


# --- UCON-L-09: the extension-point refusals -------------------------------------------------


def test_an_extension_admitting_an_undeclared_disposition_is_refused(declaration, monkeypatch):
    real = extension.exercise

    def wrong_disposition(registry, point_id):
        admitted = real(registry, point_id)
        return dataclasses.replace(
            admitted,
            dispositions=(
                dataclasses.replace(admitted.disposition, disposition="not-declared-anywhere"),
            ),
        )

    monkeypatch.setattr(extension, "exercise", wrong_disposition)
    problems = contract.extension_points_are_exercisable(Probe(declaration=declaration, repo=REPO))
    assert any("carries no declared disposition" in p for p in problems), problems


def test_an_exercise_key_without_the_probe_prefix_is_refused(declaration, monkeypatch):
    # Without the declared prefix a probe is indistinguishable from a governed registration,
    # and exercising an extension point would quietly add real constructs.
    real = extension.exercise

    def unprefixed(registry, point_id):
        admitted = real(registry, point_id)
        return dataclasses.replace(
            admitted,
            presentation=dataclasses.replace(
                admitted.presentation, natural_key="looks-like-a-real-registration"
            ),
        )

    monkeypatch.setattr(extension, "exercise", unprefixed)
    problems = contract.extension_points_are_exercisable(Probe(declaration=declaration, repo=REPO))
    assert any("does not carry the declared probe prefix" in p for p in problems), problems


def test_an_extension_admitting_the_wrong_kind_is_refused(declaration, monkeypatch):
    real = extension.exercise

    def wrong_kind(registry, point_id):
        admitted = real(registry, point_id)
        return dataclasses.replace(
            admitted,
            presentation=dataclasses.replace(admitted.presentation, kind="a-different-kind"),
        )

    monkeypatch.setattr(extension, "exercise", wrong_kind)
    problems = contract.extension_points_are_exercisable(Probe(declaration=declaration, repo=REPO))
    assert any("but admitted" in p for p in problems), problems


def test_a_declared_admission_that_fails_is_reported(declaration, monkeypatch):
    def refuse(registry, point_id):
        raise ConstructError("the declared admission refused for the test")

    monkeypatch.setattr(extension, "exercise", refuse)
    problems = contract.extension_points_are_exercisable(Probe(declaration=declaration, repo=REPO))
    assert any("the declared admission failed" in p for p in problems), problems


# --- UCON-L-07: the fixed-point refusals ------------------------------------------------------


def test_discovery_that_does_not_converge_is_refused(declaration, monkeypatch):
    real = views.discover
    calls = {"n": 0}

    def never_settles(registry):
        calls["n"] += 1
        found = real(registry)
        # Every pass mints something: the walk never reaches a state it stops adding to.
        return found if found else [registry.all()[0]]

    monkeypatch.setattr(views, "discover", never_settles)
    problems = contract.discovery_reaches_a_fixed_point(Probe(declaration=declaration, repo=REPO))
    assert any("does not converge" in p for p in problems), problems


def test_a_second_discovery_pass_that_changes_the_registry_is_refused(declaration, monkeypatch):
    digests = {"n": 0}

    def drifting_digest(self):
        digests["n"] += 1
        return f"digest-{digests['n']}"

    monkeypatch.setattr(ConstructRegistry, "digest", drifting_digest)
    problems = contract.discovery_reaches_a_fixed_point(Probe(declaration=declaration, repo=REPO))
    assert any("there is no fixed point" in p for p in problems), problems


def test_a_discovery_object_naming_no_subject_is_refused(declaration, monkeypatch):
    real = views.discover
    calls = {"n": 0}

    def unlineaged(registry):
        calls["n"] += 1
        found = real(registry)
        if calls["n"] != 1:
            return found
        return [
            dataclasses.replace(
                item,
                presentation=dataclasses.replace(
                    item.presentation,
                    lineage=dataclasses.replace(item.presentation.lineage, derived_from=()),
                ),
            )
            for item in found
        ]

    monkeypatch.setattr(views, "discover", unlineaged)
    problems = contract.discovery_reaches_a_fixed_point(Probe(declaration=declaration, repo=REPO))
    assert any("naming no subject" in p for p in problems), problems


# --- UCON-L-08: the future-kind refusals ------------------------------------------------------


def test_a_registered_kind_not_reported_as_registered_is_refused(declaration, monkeypatch):
    monkeypatch.setattr(
        type(ConstructRegistry(declaration)), "registered_kinds", property(lambda self: ())
    )
    problems = contract.future_kinds_need_no_redesign(Probe(declaration=declaration, repo=REPO))
    assert any("is not reported as a registered kind" in p for p in problems), problems


def test_an_instance_not_reporting_its_kind_as_registered_is_refused(declaration, monkeypatch):
    real = ConstructRegistry.present

    def unregistered(self, presentation):
        return dataclasses.replace(real(self, presentation), kind_registered=False)

    monkeypatch.setattr(ConstructRegistry, "present", unregistered)
    problems = contract.future_kinds_need_no_redesign(Probe(declaration=declaration, repo=REPO))
    assert any("does not report its kind as registered" in p for p in problems), problems


# --- UCON-L-12: the verifier refusals ---------------------------------------------------------


def test_a_verifier_carrying_no_assumptions_is_refused(declaration, monkeypatch):
    real = extension.register_verifier

    def stripped(registry, **kwargs):
        registered = real(registry, **kwargs)
        payload = {**registered.presentation.payload, "assumptions": ()}
        return dataclasses.replace(
            registered,
            presentation=dataclasses.replace(registered.presentation, payload=payload),
        )

    monkeypatch.setattr(extension, "register_verifier", stripped)
    problems = contract.verification_is_itself_verifiable(Probe(declaration=declaration, repo=REPO))
    assert any("verifier carries no assumptions" in p for p in problems), problems


def test_a_verifier_that_cannot_name_what_it_verifies_is_refused(declaration, monkeypatch):
    # Verification has to be recursive: a verifier that cannot name the verifier it verifies
    # makes the chain unexpressible, and nothing can check the checkers.
    real = extension.register_verifier

    def lineageless(registry, **kwargs):
        registered = real(registry, **kwargs)
        lineage = dataclasses.replace(registered.presentation.lineage, derived_from=())
        return dataclasses.replace(
            registered,
            presentation=dataclasses.replace(registered.presentation, lineage=lineage),
        )

    monkeypatch.setattr(extension, "register_verifier", lineageless)
    problems = contract.verification_is_itself_verifiable(Probe(declaration=declaration, repo=REPO))
    assert any("lineage is not expressible" in p for p in problems), problems


def test_a_verifier_declaring_no_assumptions_must_be_refused(declaration, monkeypatch):
    # The law asserts a REFUSAL: a verifier with no assumptions or no limitations claims to
    # have measured something under no conditions and with no bounds. The violation is a
    # register_verifier that accepts one.
    real = extension.register_verifier

    def permissive(registry, **kwargs):
        if not kwargs.get("assumptions") or not any(
            str(item).strip() for item in kwargs.get("assumptions", ())
        ):
            kwargs["assumptions"] = ("filled in by a permissive registrar",)
        if not kwargs.get("limitations"):
            kwargs["limitations"] = ("filled in by a permissive registrar",)
        return real(registry, **kwargs)

    monkeypatch.setattr(extension, "register_verifier", permissive)
    problems = contract.verification_is_itself_verifiable(Probe(declaration=declaration, repo=REPO))
    assert any("was admitted" in p for p in problems), problems


# --- UCON-L-11: admission and reality are independent -------------------------------------


def test_a_module_importing_across_the_admission_reality_boundary_is_refused(
    declaration, monkeypatch
):
    # If reality.py can import the disposition engine, one axis can be derived from the other
    # and the independence the law asserts is structurally impossible.
    monkeypatch.setattr(Probe, "source", lambda self, name: "import engine.construct.disposition\n")
    problems = contract.reality_is_independent_of_admission(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("can be derived from" in p for p in problems), problems


def test_an_unrepresentable_disposition_reality_pair_is_reported(declaration, monkeypatch):
    real = ConstructRegistry.reassess

    def refuse_only_the_pairs(self, identity, status, **kwargs):
        # Narrow on purpose: the law reassesses again further down, OUTSIDE any try, so a
        # blanket refusal escapes the law instead of being reported by it.
        if self.get(identity).presentation.natural_key.startswith("pair-"):
            raise ConstructError("reassessment refused for the test")
        return real(self, identity, status, **kwargs)

    monkeypatch.setattr(ConstructRegistry, "reassess", refuse_only_the_pairs)
    problems = contract.reality_is_independent_of_admission(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("is not representable" in p for p in problems), problems


def test_admission_that_confers_truth_is_refused(declaration, monkeypatch):
    # "Admission does not imply truth" is the whole conjunction: an ADMITted construct in a
    # hypothetical reality state must not be certifiable.
    monkeypatch.setattr(reality, "permits", lambda decl, construct, act: True)
    problems = contract.reality_is_independent_of_admission(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("admission implies truth" in p for p in problems), problems


def test_an_admitted_construct_that_cannot_be_referenced_is_refused(declaration, monkeypatch):
    monkeypatch.setattr(reality, "permits", lambda decl, construct, act: False)
    problems = contract.reality_is_independent_of_admission(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("cannot be referenced" in p for p in problems), problems


def test_reassessing_evidence_that_changes_the_disposition_is_refused(declaration, monkeypatch):
    # Reality must not drive admission. A reassessment that moves the disposition has made the
    # two axes one.
    real = ConstructRegistry.reassess
    other = [d for d in declaration.disposition_ids if d != "ADMIT"][0]

    def drifting(self, identity, status, **kwargs):
        reassessed = real(self, identity, status, **kwargs)
        if status != "VERIFIED":
            return reassessed
        return dataclasses.replace(
            reassessed,
            dispositions=(dataclasses.replace(reassessed.disposition, disposition=other),),
        )

    monkeypatch.setattr(ConstructRegistry, "reassess", drifting)
    problems = contract.reality_is_independent_of_admission(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("reality drives admission" in p for p in problems), problems


# --- UCON-L-03: the catch-all must not be destructive -----------------------------------------


def test_a_terminal_catch_all_disposition_is_refused(declaration):
    catch_all = [rule for rule in declaration.rules if rule.catch_all][0]
    dispositions = tuple(
        dataclasses.replace(spec, terminal=True)
        if spec.identifier == catch_all.disposition
        else spec
        for spec in declaration.dispositions
    )
    problems = contract.catch_all_is_non_destructive(
        Probe(declaration=dataclasses.replace(declaration, dispositions=dispositions), repo=REPO)
    )
    assert any("is terminal" in p for p in problems), problems


def test_a_catch_all_that_forecloses_other_dispositions_is_refused(declaration):
    catch_all = [rule for rule in declaration.rules if rule.catch_all][0]
    dispositions = tuple(
        dataclasses.replace(spec, successors=())
        if spec.identifier == catch_all.disposition
        else spec
        for spec in declaration.dispositions
    )
    problems = contract.catch_all_is_non_destructive(
        Probe(declaration=dataclasses.replace(declaration, dispositions=dispositions), repo=REPO)
    )
    assert any("forecloses them" in p for p in problems), problems


# --- UCON-L-04: operators are two-way bound ---------------------------------------------------


def test_an_operator_claimed_but_not_implemented_is_refused(declaration):
    claimed = frozenset({*declaration.claimed_operators, "an_operator_nobody_wrote"})
    problems = contract.operators_are_two_way_bound(
        Probe(declaration=dataclasses.replace(declaration, claimed_operators=claimed), repo=REPO)
    )
    assert any("differs between the declaration" in p for p in problems), problems


def test_validate_accepting_an_unimplemented_operator_is_refused(declaration, monkeypatch):
    # The law asserts a REFUSAL by validate(), so the violation is a validate() that tolerates
    # a rule naming an operator nobody implemented. validate() returns the problems it found,
    # so "tolerated" is an EMPTY result — the first version of this test returned True and the
    # law read that as validation having objected.
    monkeypatch.setattr(
        type(declaration), "validate", lambda self, checks, implemented, selectors: ()
    )
    problems = contract.operators_are_two_way_bound(Probe(declaration=declaration, repo=REPO))
    assert any("was accepted by validate()" in p for p in problems), problems


# --- UCON-L-10: no state is terminal ----------------------------------------------------------


def test_a_disposition_naming_no_successor_is_refused(declaration):
    closed = (
        dataclasses.replace(declaration.dispositions[0], successors=()),
        *declaration.dispositions[1:],
    )
    problems = contract.no_state_is_terminal(
        Probe(declaration=dataclasses.replace(declaration, dispositions=closed), repo=REPO)
    )
    assert any("names no successor" in p for p in problems), problems


def test_a_reality_state_naming_no_successor_is_refused(declaration):
    closed = (
        dataclasses.replace(declaration.reality_states[0], successors=()),
        *declaration.reality_states[1:],
    )
    problems = contract.no_state_is_terminal(
        Probe(declaration=dataclasses.replace(declaration, reality_states=closed), repo=REPO)
    )
    assert any("could ever be revised" in p for p in problems), problems


# --- UCON-L-16: measurement is deterministic --------------------------------------------------


def test_two_registries_rendering_differently_are_refused(declaration, monkeypatch):
    calls = {"n": 0}

    def drifting(self):
        calls["n"] += 1
        return f"rendered-{calls['n']}"

    monkeypatch.setattr(ConstructRegistry, "rendered", drifting)
    problems = contract.measurement_is_deterministic(Probe(declaration=declaration, repo=REPO))
    assert any("render differently" in p for p in problems), problems


def test_two_registries_with_different_digests_are_refused(declaration, monkeypatch):
    calls = {"n": 0}

    def drifting(self):
        calls["n"] += 1
        return f"digest-{calls['n']}"

    monkeypatch.setattr(ConstructRegistry, "digest", drifting)
    problems = contract.measurement_is_deterministic(Probe(declaration=declaration, repo=REPO))
    assert any("different digests" in p for p in problems), problems


def test_an_inventory_embedding_a_clock_or_a_path_is_refused(declaration, monkeypatch):
    # A measurement carrying a timestamp or a machine path is unrepeatable elsewhere: two
    # identical repositories would disagree because they were measured on different machines.
    monkeypatch.setattr(audit, "rendered", lambda inventory: "measured at T00:00:00")
    problems = contract.measurement_is_deterministic(Probe(declaration=declaration, repo=REPO))
    assert any("makes the measurement unrepeatable elsewhere" in p for p in problems), problems


# --- UCON-L-14: vocabulary is bound, never copied ---------------------------------------------


def test_a_reality_state_binding_to_no_ceu_row_and_disclosing_no_gap_is_refused(declaration):
    unbound = (
        dataclasses.replace(declaration.reality_states[0], ceu_binding=None, binding_gap={}),
        *declaration.reality_states[1:],
    )
    problems = contract.vocabulary_is_not_duplicated(
        Probe(declaration=dataclasses.replace(declaration, reality_states=unbound), repo=REPO)
    )
    assert any("discloses no gap_id" in p for p in problems), problems


def test_a_reality_state_binding_to_an_undeclared_ceu_population_is_refused(declaration):
    rebound = (
        dataclasses.replace(
            declaration.reality_states[0],
            ceu_binding={"population": "a-population-CEU-never-declared", "member": "x"},
        ),
        *declaration.reality_states[1:],
    )
    problems = contract.vocabulary_is_not_duplicated(
        Probe(declaration=dataclasses.replace(declaration, reality_states=rebound), repo=REPO)
    )
    assert any("does not declare" in p for p in problems), problems


def test_a_reality_state_binding_to_a_member_ceu_does_not_carry_is_refused(declaration):
    binding = dict(declaration.reality_states[0].ceu_binding or {})
    binding["member"] = "a-member-CEU-never-carried"
    rebound = (
        dataclasses.replace(declaration.reality_states[0], ceu_binding=binding),
        *declaration.reality_states[1:],
    )
    problems = contract.vocabulary_is_not_duplicated(
        Probe(declaration=dataclasses.replace(declaration, reality_states=rebound), repo=REPO)
    )
    assert any("does not carry" in p for p in problems), problems


def test_the_report_digest_is_a_function_of_the_report(declaration):
    # `digest` is the identity the whole report is recorded under: two identical reports must
    # digest identically and a changed one must not.
    report = {"laws": [{"law_id": "UCON-L-01", "holds": True}]}
    assert contract.digest(report) == contract.digest(dict(report))
    assert contract.digest(report) != contract.digest({"laws": []})


def test_an_extension_that_drops_a_declared_kind_is_refused(declaration):
    # Extension must be additive. A registry whose declaration comes back missing something it
    # started with has narrowed the world under the guise of extending it.
    real = ConstructRegistry(declaration)
    thinner = dataclasses.replace(declaration, kinds=declaration.kinds[1:])

    class _Narrowing:
        declaration = thinner

        def __getattr__(self, name):
            return getattr(real, name)

    probe = _ProbeWithRegistry(declaration, _Narrowing())
    problems = contract.extension_points_are_exercisable(probe)
    assert any("was altered or dropped by an extension" in p for p in problems), problems


def test_an_extension_that_drops_a_declared_disposition_is_refused(declaration):
    real = ConstructRegistry(declaration)
    thinner = dataclasses.replace(declaration, dispositions=declaration.dispositions[1:])

    class _Narrowing:
        declaration = thinner

        def __getattr__(self, name):
            return getattr(real, name)

    probe = _ProbeWithRegistry(declaration, _Narrowing())
    problems = contract.extension_points_are_exercisable(probe)
    assert any("disposition" in p and "was altered or dropped" in p for p in problems), problems


def test_an_extension_that_drops_a_declared_reality_state_is_refused(declaration):
    real = ConstructRegistry(declaration)
    thinner = dataclasses.replace(declaration, reality_states=declaration.reality_states[1:])

    class _Narrowing:
        declaration = thinner

        def __getattr__(self, name):
            return getattr(real, name)

    probe = _ProbeWithRegistry(declaration, _Narrowing())
    problems = contract.extension_points_are_exercisable(probe)
    assert any("reality state" in p and "was altered or dropped" in p for p in problems), problems


def test_adopting_a_narrowed_declaration_must_be_refused(declaration, monkeypatch):
    # The law asserts a REFUSAL: adopt() must reject a declaration that dropped a disposition.
    # The violation is an adopt() that accepts one.
    monkeypatch.setattr(ConstructRegistry, "adopt", lambda self, declaration: None)
    problems = contract.extension_points_are_exercisable(Probe(declaration=declaration, repo=REPO))
    assert any("dropped a disposition was adopted" in p for p in problems), problems


# --- the measurement workspace itself ---------------------------------------------------------


def test_the_fingerprint_is_computed_once_and_reused(declaration):
    # The Probe caches two expensive derivations so sixteen laws do not recompute them sixteen
    # times. A cache that recomputed would still be correct and would make the measurement cost
    # sixteen times what it costs, so the second call reading the cache is the property.
    probe = Probe(declaration=declaration, repo=REPO)
    first = probe.fingerprint()
    assert first is probe.fingerprint()


def test_a_module_that_cannot_be_read_is_a_fault_and_not_a_verdict(declaration):
    # ContractError is deliberately not a refusal: a law that cannot read its own subject has
    # measured nothing, and reporting "HOLDS" or "REFUSED" from that position would be a claim
    # about bytes nobody looked at.
    probe = Probe(declaration=declaration, repo=REPO)
    with pytest.raises(contract.ContractError, match="cannot read"):
        probe.source("a-module-this-package-has-never-had.py")


# --- UCON-L-01: every construct carries exactly one active disposition ------------------------


def test_a_model_that_accepts_a_forged_disposition_set_is_refused(declaration, monkeypatch):
    # The law's non-vacuity check asserts that the MODEL refuses the forged forms. The violation
    # it guards against is a model that accepts them — at which point every other branch of the
    # law is measuring a shape the model would let through.
    class _Permissive:
        def __init__(self, presentation, dispositions, assessments, kind_registered):
            self.presentation = presentation
            self.dispositions = dispositions
            self.assessments = assessments
            self.kind_registered = kind_registered

    monkeypatch.setattr(contract, "Construct", _Permissive)
    problems = contract.every_construct_is_disposed(Probe(declaration=declaration, repo=REPO))
    assert any("no disposition at all" in p for p in problems), problems
    assert any("two active dispositions" in p for p in problems), problems


# --- UCON-L-05: nothing is silently ignored ---------------------------------------------------


def test_a_registry_holding_more_constructs_than_it_counted_presentations_is_refused(declaration):
    # The arithmetic is the point: a registry cannot hold more constructs than were presented to
    # it without having invented one, and the check is what makes "the population equals the
    # presentations" a measurement rather than a restatement of the same number twice.
    probe = _registry_probe(declaration, presented=0)
    problems = contract.nothing_is_silently_ignored(probe)
    assert any("arithmetically impossible" in p for p in problems), problems


# --- UCON-L-06: unknowns, contradictions, research and discovery are first class ---------------


def test_a_research_object_that_names_no_origin_is_refused(declaration, monkeypatch):
    # Promotion without lineage produces an object whose subject cannot be recovered: the
    # research exists and nothing says what it is research INTO.
    real = views.promote_to_research

    def forgetful(registry, identity):
        promoted = real(registry, identity)
        lineage = dataclasses.replace(promoted.presentation.lineage, derived_from=())
        presentation = dataclasses.replace(promoted.presentation, lineage=lineage)
        return _Stand_in(
            promoted.identity,
            promoted.dispositions,
            promoted.disposition,
            presentation=presentation,
            assessments=promoted.assessments,
        )

    monkeypatch.setattr(views, "promote_to_research", forgetful)
    problems = contract.unknown_and_contradiction_are_first_class(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("does not name the construct it derives from" in p for p in problems), problems


def test_an_ordinary_construct_that_cannot_be_promoted_is_refused(declaration, monkeypatch):
    # Promotion must work on ANY construct. A promotion that only succeeds for the kinds the
    # foundation anticipated is a closed set wearing an open interface.
    real = views.promote_to_research

    def barren(registry, identity):
        promoted = real(registry, identity)
        return _Stand_in(
            "",
            promoted.dispositions,
            promoted.disposition,
            presentation=promoted.presentation,
            assessments=promoted.assessments,
        )

    monkeypatch.setattr(views, "promote_to_research", barren)
    problems = contract.unknown_and_contradiction_are_first_class(
        Probe(declaration=declaration, repo=REPO)
    )
    assert any("could not be promoted to a research object" in p for p in problems), problems


def test_a_governed_object_carrying_an_undeclared_disposition_is_refused(declaration):
    # The registry disposes these objects from the real declaration; the law reads the declared
    # set from the probe. Narrowing the probe's view is how the branch that would fire on a
    # disposition nobody declared can be shown to fire at all.
    probe = _ProbeWithRegistry(_NarrowedDispositions(declaration), ConstructRegistry(declaration))
    problems = contract.unknown_and_contradiction_are_first_class(probe)
    assert any("carries an undeclared disposition" in p for p in problems), problems


# --- UCON-L-08: a future category is admissible by registration alone -------------------------


def test_a_package_whose_source_changed_under_registration_is_refused(declaration, monkeypatch):
    # The openness claim is only worth the fingerprint that backs it. If registering eleven
    # categories nobody declared rewrote a byte of this package, admission would require a code
    # change and the model would be closed however the docstring reads.
    prints = iter(({"model.py": "before"}, {"model.py": "after"}))

    monkeypatch.setattr(contract, "_package_fingerprint", lambda repo: next(prints))
    problems = contract.future_kinds_need_no_redesign(Probe(declaration=declaration, repo=REPO))
    assert any("changed while admitting categories" in p for p in problems), problems


# --- UCON-L-11: admission and reality are independent -----------------------------------------


def test_a_construct_presented_as_something_other_than_admitted_is_redisposed(declaration):
    # The conjunction the law measures needs an ADMITted construct in a hypothetical state. The
    # rules currently admit it outright, so the redisposition branch is what makes the law
    # survive a future rule that disposes this presentation some other way.
    real = ConstructRegistry(declaration)

    def present(presentation):
        got = real.present(presentation)
        if presentation.natural_key != "admitted-but-hypothetical":
            return got
        return real.redispose(
            got.identity,
            disposition="TRANSFORM",
            rule_id="doctored",
            rationale="a rule that does not admit this presentation outright",
        )

    probe = _registry_probe(declaration, base=real, present=present)
    assert contract.reality_is_independent_of_admission(probe) == []


# --- UCON-L-12: verification is itself verifiable ---------------------------------------------


def test_a_well_formed_verifier_reporting_facet_violations_is_refused(declaration, monkeypatch):
    # The verifier facet declares required fields. A registration that supplies every one of
    # them and still comes back with violations means the facet machinery disagrees with itself,
    # and every later verifier is being validated by a rule nobody can satisfy.
    real = extension.register_verifier

    def violating(registry, **kwargs):
        got = real(registry, **kwargs)
        if kwargs.get("natural_key") != "UCON-L-12-verifier":
            return got
        return dataclasses.replace(got, facet_violations=("a violation nobody can remove",))

    monkeypatch.setattr(extension, "register_verifier", violating)
    problems = contract.verification_is_itself_verifiable(Probe(declaration=declaration, repo=REPO))
    assert any("reports facet violations" in p for p in problems), problems


# --- UCON-L-13: no completeness claim is declared ---------------------------------------------


def test_the_claim_scan_reads_only_the_declared_extensions(declaration, tmp_path):
    # A scan that read every file would report the guarantee vocabulary out of a fixture, a
    # changelog or a test, and the ratchet would be unusable. The `continue` is what confines
    # the measurement to source.
    root = tmp_path / "capability"
    root.mkdir()
    (root / "clean.py").write_text("x = 1\n", encoding="utf-8")
    (root / "notes.txt").write_text("this file declares infinite truth\n", encoding="utf-8")
    scan = dict(declaration.claim_scan, roots=["capability"], preserved_sites=[])
    probe = Probe(declaration=dataclasses.replace(declaration, claim_scan=scan), repo=str(tmp_path))
    assert contract.no_completeness_claim_is_declared(probe) == []


def test_a_preserved_site_admits_its_occurrence_and_an_undeclared_one_does_not(
    declaration, tmp_path
):
    # Both directions of the ratchet in one measurement: the declared site is admitted in
    # silence, the undeclared one is named. A scan that reported both, or neither, would make
    # the exemption list decorative.
    root = tmp_path / "capability"
    root.mkdir()
    (root / "admitted.py").write_text('PHRASE = "infinite truth"\n', encoding="utf-8")
    (root / "undeclared.py").write_text('OTHER = "infinite truth"\n', encoding="utf-8")
    scan = dict(
        declaration.claim_scan,
        roots=["capability"],
        phrases=["infinite truth"],
        preserved_sites=[
            {"module": os.path.join("capability", "admitted.py"), "phrase": "infinite truth"}
        ],
    )
    probe = Probe(declaration=dataclasses.replace(declaration, claim_scan=scan), repo=str(tmp_path))
    problems = contract.no_completeness_claim_is_declared(probe)
    assert [p for p in problems if "undeclared.py" in p], problems
    assert not [p for p in problems if "admitted.py" in p], problems


# --- UCON-L-14: vocabulary is bound, never copied ---------------------------------------------


def test_a_reality_vocabulary_that_contains_a_whole_ceu_population_is_refused(
    declaration, monkeypatch
):
    # Binding to somebody else's vocabulary and copying it whole are indistinguishable from the
    # outside until the owner changes one row. Holding the whole population is the copy.

    ours = tuple((identifier.lower(), "") for identifier in declaration.reality_ids[:2])
    monkeypatch.setattr(catalog, "SEED_POPULATIONS", (("a-copied-population", ours),))
    problems = contract.vocabulary_is_not_duplicated(Probe(declaration=declaration, repo=REPO))
    assert any("is a copy rather than a binding" in p for p in problems), problems


class _NarrowedDispositions:
    """The declaration with its disposition vocabulary emptied, and nothing else changed.

    A registry built from the real declaration disposes constructs from the real rules. Reading
    the declared set through this proxy is what lets a law's "an undeclared disposition arrived"
    branch fire without forging a construct the model would have refused.
    """

    disposition_ids: tuple[str, ...] = ()

    def __init__(self, real):
        object.__setattr__(self, "_real", real)

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "_real"), name)


# --- the declaration's accessors and the rest of validate() -----------------------------------


def test_every_declared_law_is_reachable_by_its_identifier(declaration: Declaration) -> None:
    # The accessors refuse an undeclared name, which is tested above. The other half — that a
    # declared name resolves — is what makes the refusal a boundary rather than a wall.
    for law in declaration.laws:
        assert declaration.law(law.law_id) is law


def test_a_disposition_naming_an_undeclared_successor_is_refused(declaration: Declaration) -> None:
    # A successor nobody declared makes the lifecycle a graph with an edge leaving the world.
    spec = declaration.disposition("ADMIT")
    forged = replace(
        declaration,
        dispositions=(
            replace(spec, successors=(*spec.successors, "A-DISPOSITION-NOBODY-DECLARED")),
            *declaration.dispositions[1:],
        ),
    )
    problems = forged.validate(available_checks(), available_operators())
    assert any("undeclared successor" in problem for problem in problems), problems


def test_a_reality_state_permitting_an_undeclared_act_is_refused(declaration: Declaration) -> None:
    # The same defect as the disposition case and a separate branch, because the two vocabularies
    # are independent: an act declared for one is not thereby declared for the other.
    spec = declaration.reality("VERIFIED")
    forged = replace(
        declaration,
        reality_states=(
            replace(spec, permits=spec.permits | {"transmute"}),
            *declaration.reality_states[1:],
        ),
    )
    problems = forged.validate(available_checks(), available_operators())
    assert any("reality state" in p and "undeclared act" in p for p in problems), problems


def test_registration_naming_an_undeclared_disposition_is_refused(declaration: Declaration) -> None:
    forged = replace(
        declaration,
        registration_dispositions=declaration.registration_dispositions | {"NOT-A-DISPOSITION"},
    )
    problems = forged.validate(available_checks(), available_operators())
    assert any("registration_dispositions names undeclared" in p for p in problems), problems


def test_registration_naming_no_disposition_at_all_is_refused(declaration: Declaration) -> None:
    # An empty set is the failure that looks like success: every check over it passes vacuously
    # and no registration could ever take effect.
    forged = replace(declaration, registration_dispositions=frozenset())
    problems = forged.validate(available_checks(), available_operators())
    assert any("no registration could ever take effect" in p for p in problems), problems


def test_an_admission_the_declaration_claims_and_nothing_implements_is_refused(
    declaration: Declaration,
) -> None:
    forged = replace(
        declaration, claimed_admissions=declaration.claimed_admissions | {"not_an_admission"}
    )
    problems = forged.validate(
        available_checks(),
        available_operators(),
        available_admissions=extension.available_admissions(),
    )
    assert any("claimed by the declaration but not implemented" in p for p in problems), problems


def test_a_discovery_source_naming_an_unimplemented_selector_is_refused(
    declaration: Declaration,
) -> None:
    source = declaration.discovery_sources[0]
    forged = replace(
        declaration,
        discovery_sources=(
            replace(source, selector="not_a_selector"),
            *declaration.discovery_sources[1:],
        ),
    )
    problems = forged.validate(
        available_checks(),
        available_operators(),
        available_selectors=views.available_selectors(),
    )
    assert any("which is not implemented" in p for p in problems), problems


def test_a_selector_the_declaration_claims_and_nothing_implements_is_refused(
    declaration: Declaration,
) -> None:
    forged = replace(
        declaration, claimed_selectors=declaration.claimed_selectors | {"not_a_selector"}
    )
    problems = forged.validate(
        available_checks(),
        available_operators(),
        available_selectors=views.available_selectors(),
    )
    assert any("selector" in p and "not implemented" in p for p in problems), problems


def test_a_closure_form_no_detector_implements_is_refused(declaration: Declaration) -> None:
    spec = declaration.audit
    forged = replace(
        declaration,
        audit=replace(spec, forms=(*spec.forms, replace(spec.forms[0], form="not-a-form"))),
    )
    problems = forged.validate(
        available_checks(),
        available_operators(),
        available_forms=frozenset(audit.available_forms()),
    )
    assert any("no detector implements it" in p for p in problems), problems


def test_a_facets_section_that_is_not_an_object_is_refused() -> None:
    document = json.loads(
        open(
            os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json"),
            encoding="utf-8",
        ).read()
    )
    document["facets"] = ["a list where an object belongs"]
    with pytest.raises(DeclarationError, match="must be an object"):
        parse(document)


def test_a_row_missing_a_required_key_is_a_fault_and_names_the_key() -> None:
    # Not a DeclarationError raised by a guard — a KeyError from the rehydration itself, caught
    # and re-raised as a fault. Without the catch the declaration reader would surface a raw
    # KeyError to a caller that has no way to tell a malformed document from a bug.
    document = json.loads(
        open(
            os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json"),
            encoding="utf-8",
        ).read()
    )
    document["laws"][0].pop("statement")
    with pytest.raises(DeclarationError, match="malformed"):
        parse(document)


# --- the closure audit's detectors and its unreadable files ------------------------------------


def test_a_bare_set_literal_is_a_frozen_membership_set(declaration: Declaration, tmp_path) -> None:
    # `frozenset({...})` was detected and `{...}` was not, so the cheapest spelling of a closed
    # membership set was the one the audit could not see.
    module = tmp_path / "engine" / "bare.py"
    module.parent.mkdir(parents=True)
    module.write_text("MEMBERS = {'a', 'b', 'c'}\n", encoding="utf-8")
    spec = replace(declaration.audit, roots=("engine",))
    found = audit.scan(replace(declaration, audit=spec), str(tmp_path))
    assert "FROZEN_MEMBERSHIP_SET" in {closure.form for closure in found}
    assert "MEMBERS" in {closure.symbol for closure in found}


def test_a_comparison_against_a_boolean_is_not_a_population_assertion(
    declaration: Declaration, tmp_path
) -> None:
    # `True` is an int in Python, so `len(x) == True` reaches the population detector as a
    # comparison against 1. It asserts nothing about a population and must not be counted, or
    # the closure census would inflate with every truthiness test in the repository.
    module = tmp_path / "engine" / "boolean.py"
    module.parent.mkdir(parents=True)
    module.write_text("def f(x):\n    return len(x) == True\n", encoding="utf-8")
    spec = replace(declaration.audit, roots=("engine",))
    found = audit.scan(replace(declaration, audit=spec), str(tmp_path))
    assert "POPULATION_ASSERTION" not in {closure.form for closure in found}


def test_a_file_that_cannot_be_opened_is_reported_and_does_not_crash_the_audit(
    declaration: Declaration, tmp_path
) -> None:
    # Unparseable is already measured. Unreadable is a different failure and a different branch:
    # the file never becomes source at all, so there is nothing for the parser to refuse.
    module = tmp_path / "engine" / "unreadable.py"
    module.parent.mkdir(parents=True)
    module.write_text("TABLE = {'a': 1}\n", encoding="utf-8")
    module.chmod(0o000)
    spec = replace(declaration.audit, roots=("engine",))
    forged = replace(declaration, audit=spec)
    assert audit.scan(forged, str(tmp_path)) == ()
    assert "engine/unreadable.py" in audit.unscannable(forged, str(tmp_path))


def test_scanning_for_a_form_no_detector_implements_is_a_fault(
    declaration: Declaration, tmp_path
) -> None:
    # A declared form with no detector would otherwise scan to zero findings, and zero findings
    # is what a form that does not occur looks like. The two must not be spelled the same way.
    module = tmp_path / "engine" / "probe.py"
    module.parent.mkdir(parents=True)
    module.write_text("TABLE = {'a': 1}\n", encoding="utf-8")
    spec = declaration.audit
    forged = replace(
        declaration,
        audit=replace(
            spec, roots=("engine",), forms=(replace(spec.forms[0], form="NO-SUCH-FORM"),)
        ),
    )
    with pytest.raises(audit.AuditError, match="no detector implements it"):
        audit.scan(forged, str(tmp_path))


# --- the model's own refusals ------------------------------------------------------------------


def test_a_disposition_sequence_below_zero_is_refused() -> None:
    # The sequence is the ordinal a supersession chain is read in. A negative one would order
    # a record before the genesis of the construct it belongs to.
    with pytest.raises(ConstructError, match="non-negative ordinal"):
        DispositionRecord(
            identity="UMK-ENTITY-0000",
            disposition="ADMIT",
            rule_id="R",
            rationale="measured",
            sequence=-1,
            inputs_digest="d",
        )


def _assessment(**overrides) -> RealityAssessment:
    """A well-formed assessment with one field replaced, for the model's own guards."""
    fields = {
        "identity": "UMK-ENTITY-0000",
        "status": "HYPOTHETICAL",
        "evidence_count": 0,
        "independent_sources": 0,
        "assessed_from": (),
        "sequence": 0,
        "floor_met": True,
    }
    fields.update(overrides)
    return RealityAssessment(**fields)


def test_a_reality_assessment_without_a_status_is_refused() -> None:
    with pytest.raises(ConstructError, match="requires status"):
        _assessment(status="")


def test_an_assessment_naming_no_source_and_one_named_as_a_string_agree() -> None:
    # `assessed_from` is normalised rather than validated: None is no sources and a bare string
    # is one source. A caller that passed a string and got its characters back would have
    # produced an assessment naming len(s) sources, none of which exist.
    assert _assessment(assessed_from=None).assessed_from == ()
    assert _assessment(assessed_from="one-source").assessed_from == ("one-source",)


def test_a_construct_with_two_active_reality_assessments_is_refused(declaration) -> None:
    # The disposition side of this invariant is measured by UCON-L-01. The reality side is a
    # separate record type with a separate active flag, and nothing had ever produced two.
    registry = ConstructRegistry(declaration)
    sample = registry.present(Presentation(kind="entity", natural_key="two-assessments"))
    with pytest.raises(ConstructError, match="exactly one active reality assessment"):
        Construct(
            presentation=sample.presentation,
            dispositions=sample.dispositions,
            assessments=(sample.reality, replace(sample.reality, sequence=99)),
            kind_registered=True,
        )


# --- the registry's remaining branches ---------------------------------------------------------


def test_a_registry_can_be_built_without_bootstrapping(declaration: Declaration) -> None:
    # The bootstrap seeds the reflective constructs the foundation describes itself with. A
    # registry that skips it is how the seeding itself can be measured rather than assumed, and
    # an empty population is the only starting point from which "nothing was dropped" means
    # anything.
    registry = ConstructRegistry(declaration, bootstrap=False)
    assert registry.all() == ()
    assert registry.summary()["chain_head"] == GENESIS


def test_a_registered_kind_declaring_an_unknown_facet_carries_none(declaration: Declaration):
    # A kind registered at runtime names its facet in its payload. A payload naming a facet the
    # declaration does not carry must fall back to the uninterpreted facet rather than to the
    # named one, or registration would be a way to invent a facet the declaration never saw.
    registry = ConstructRegistry(declaration)
    registry.present(
        Presentation(
            kind=declaration.reflective_root,
            natural_key="a-kind-with-a-facet-nobody-declared",
            payload={"facet": "not-a-declared-facet"},
        )
    )
    assert registry.facet_of("a-kind-with-a-facet-nobody-declared") == "none"


def test_a_contradiction_naming_no_side_contradicts_nothing(declaration: Declaration) -> None:
    # The contradicted set is built from the sides a contradiction names. A contradiction whose
    # payload carries no side must contribute no identity — an empty string in that set would
    # quarantine a construct whose identity is "".
    registry = ConstructRegistry(declaration)
    registry.present(
        Presentation(
            kind=views._kind_for_facet(registry, views.FACET_CONTRADICTION),
            natural_key="a-contradiction-naming-nobody",
            payload={"resolution_state": sorted(declaration.contradicting_states)[0]},
        )
    )
    assert "" not in registry.contradicted()


def test_an_edited_journal_body_breaks_the_chain(declaration: Declaration) -> None:
    # A relinked chain and an edited body are different tampering. The link check alone would
    # pass on a journal whose entries still point at each other while one of them says something
    # else than it did when its hash was taken.
    registry = ConstructRegistry(declaration)
    assert registry.chain_is_intact()
    # Edited in place rather than rebuilt: JournalEntry recomputes its own hash on construction,
    # so a replaced entry is a consistent record of a different act. Tampering is the body
    # changing AFTER the hash was taken, and that is the only thing this check can see.
    object.__setattr__(registry._journal[0], "identity", "UMK-ENTITY-somebody-else")
    assert not registry.chain_is_intact()


def test_the_summary_reports_the_facet_violations_it_finds(declaration: Declaration) -> None:
    # The summary is what the gate and the evidence record read. A construct whose payload omits
    # a field its facet requires must appear there by identity, or a facet violation is visible
    # only to whoever happened to hold the construct.
    registry = ConstructRegistry(declaration)
    registry.present(Presentation(kind="unknown", natural_key="malformed-unknown", payload={}))
    assert registry.summary()["facet_violations"]


# --- the CLI and the gate ----------------------------------------------------------------------


def test_the_cli_emits_the_same_bytes_whether_or_not_json_is_asked_for(capsys) -> None:
    # Every command of this CLI emits JSON. The flag selects nothing, and pinning that is the
    # point: a command whose output SHAPE changed with a flag would be two commands sharing a
    # name, and the caller parsing it would have to know which one it got.
    construct_cli._emit({"b": 2, "a": 1}, as_json=True)
    asked = capsys.readouterr().out
    construct_cli._emit({"b": 2, "a": 1}, as_json=False)
    assert capsys.readouterr().out == asked


def test_the_audit_command_names_the_ratchet_violations_it_found(capsys, tmp_path) -> None:
    document = json.loads(
        open(
            os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json"),
            encoding="utf-8",
        ).read()
    )
    document["audit"]["baseline"] = {form: 0 for form in audit.available_forms()}
    path = tmp_path / "forged.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    code = construct_cli.main(["--declaration", str(path), "audit"])
    out = capsys.readouterr().out
    assert code == construct_cli.EXIT_FAILED
    assert "RATCHET VIOLATIONS:" in out


def test_the_rendered_report_truncates_a_law_with_more_violations_than_it_prints(report) -> None:
    # Six violations are shown and the rest are counted. A render that printed all of them would
    # bury the verdict under one law's findings; one that printed six and said nothing about the
    # remainder would report a smaller refusal than the one that was measured.
    forged = copy.deepcopy(report)
    forged["laws"][0]["verdict"] = REFUSED
    forged["laws"][0]["violations"] = [f"violation {index}" for index in range(9)]
    rendered = construct_gate._render(forged)
    assert "... +3 more" in rendered


def test_the_gate_names_the_evidence_it_wrote_unless_asked_to_be_quiet(capsys, tmp_path) -> None:
    # --quiet is measured. The default is not, and the default is what an operator runs: an
    # evidence write nobody is told about is indistinguishable from no write at all.
    declaration_path = os.path.join(REPO, "00-MASTER", "UCON-000001", "ucon-declaration.json")
    code = construct_gate.main(
        [
            "--law",
            "UCON-L-10",
            "--evidence",
            "--declaration",
            declaration_path,
            "--repository",
            str(tmp_path),
        ]
    )
    assert code == construct_gate.EXIT_OPEN
    assert "UCON: wrote" in capsys.readouterr().err


# --- the views' remaining refusals -------------------------------------------------------------


def test_a_contradiction_in_an_undeclared_resolution_state_is_refused(declaration) -> None:
    registry = ConstructRegistry(declaration)
    with pytest.raises(ViewError, match="not a declared resolution state"):
        views.register_contradiction(
            registry,
            natural_key="UCON-views-bad-state",
            left="UMK-ENTITY-a",
            right="UMK-ENTITY-b",
            contradiction_class=declaration.contradiction_classes[0],
            resolution_state="A-RESOLUTION-STATE-NOBODY-DECLARED",
        )


def test_a_discovery_object_with_an_undeclared_impact_is_refused(declaration) -> None:
    registry = ConstructRegistry(declaration)
    with pytest.raises(ViewError, match="not a declared discovery impact"):
        views.register_discovery(
            registry,
            natural_key="UCON-views-bad-impact",
            opportunity="an opportunity nobody can weigh",
            priority=declaration.priority_scale[0],
            impact="AN-IMPACT-NOBODY-DECLARED",
        )


def test_a_discovery_source_naming_an_unimplemented_selector_is_a_fault(declaration) -> None:
    # Declared-but-unimplemented is refused at load time by validate(). This is the same defect
    # reached at discovery time, and it must be a fault rather than a source that selects
    # nothing — a selector that silently matches no construct is a discovery source switched off.
    source = declaration.discovery_sources[0]
    forged = replace(
        declaration,
        discovery_sources=(replace(source, selector="not_a_selector"),),
    )
    registry = ConstructRegistry(forged)
    with pytest.raises(ViewError, match="declared but not implemented"):
        views.opportunities(registry)


# --- extension refuses what would narrow or unbind the vocabulary ------------------------------


def test_extending_with_an_already_declared_reality_state_is_refused(declaration) -> None:
    with pytest.raises(ExtensionError, match="already declared"):
        extension.extended_with_reality_state(
            declaration,
            "VERIFIED",
            definition="a second definition of a state that exists",
            permits=(),
            successors=("UNKNOWN",),
        )


def test_extending_with_a_reality_state_permitting_an_undeclared_act_is_refused(declaration):
    with pytest.raises(ExtensionError, match="permits undeclared acts"):
        extension.extended_with_reality_state(
            declaration,
            "A-NEW-STATE",
            definition="a state permitting an act nobody declared",
            permits=("transmute",),
            successors=("UNKNOWN",),
        )


def test_extending_with_a_reality_state_naming_an_undeclared_successor_is_refused(declaration):
    with pytest.raises(ExtensionError, match="undeclared successor"):
        extension.extended_with_reality_state(
            declaration,
            "A-NEW-STATE",
            definition="a state whose exit leaves the declared world",
            permits=(),
            successors=("A-STATE-NOBODY-DECLARED",),
        )


# --- evidence and disposition ------------------------------------------------------------------


def test_a_record_this_module_produces_and_the_declaration_omits_is_refused(declaration) -> None:
    # The two-way binding again, on the evidence side. A record produced but not declared is a
    # file appearing in the evidence home that no reader is looking for.
    forged = replace(declaration, evidence_records=declaration.evidence_records[:-1])
    with pytest.raises(evidence.EvidenceError, match="the declaration does not name"):
        evidence.assert_complete(forged, {})


def test_a_rule_set_with_no_catch_all_is_a_fault_rather_than_a_default(declaration) -> None:
    # The fallback is written as a fault deliberately: it is unreachable while validate() holds,
    # and a defensive `return declaration.catch_all` here would keep disposing constructs from a
    # rule set that had quietly stopped being total.
    registry = ConstructRegistry(declaration)
    with pytest.raises(DispositionError, match="not total"):
        select_rule(
            replace(declaration, rules=()),
            Presentation(kind="entity", natural_key="nothing-decides-this"),
            registry.context(),
        )


def test_the_entry_point_module_is_executed_under_measurement() -> None:
    """runpy imports `engine.construct.__main__` so its two import-time lines are measured.

    Executing the source in a fresh namespace never registers the module with the
    collector, so coverage reported the entry point unimported. `run_module` runs it the
    way `python -m` does — under a name other than `__main__`, so the dispatch guard stays
    closed and only the module's own two statements execute.
    """

    import engine.construct.__main__ as construct_main

    result = runpy.run_module("engine.construct", run_name="_construct_probe")
    assert result["main"] is construct_cli.main
    assert construct_main.main is construct_cli.main
