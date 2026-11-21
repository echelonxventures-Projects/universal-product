"""Mandate conformance — the Absolute Universal Constitutional Model (interrogative).

163 mandates over 11 sections. The document is a set of questions every constitutional
object must be able to answer -- WHY, WHAT, WHO, WHERE, WHEN, HOW, WHICH, CAN -- followed by
the CONSTITUTION facets that answer them, the FLOW that produces them and the OUTPUTS.

That shape makes Article 6 the natural respondent: a facet IS "a question every
constitutional object must be able to answer about itself", and the facet enum already
declares the question each one answers. Where a mandated facet has no facet, the suite says
so rather than reaching for the nearest module that shares a word.
"""

from __future__ import annotations

from engine.tests.conformance.mandate_corpus import (
    assert_absence_rule_can_find_something,
    assert_homes_exist,
    assert_named_by_nothing,
    assert_partitions,
    section,
    tracked,
)
from engine.uckp.facets import REQUIRED_FACETS, Facet

# --- QM-CONST — the twenty-five constitutional facets ---------------------------

#: Mandated facet -> the universal facet that answers it.
CONSTITUTION_FACET = {
    "QM-CONST/CO-01": Facet.IDENTITY,  # Identity
    "QM-CONST/CO-02": Facet.SEMANTIC_IDENTITY,  # Meaning
    "QM-CONST/CO-04": Facet.CONTEXT,  # Context
    "QM-CONST/CO-05": Facet.RELATIONSHIPS,  # Relationships
    "QM-CONST/CO-06": Facet.CONSTRAINTS,  # Constraints
    "QM-CONST/CO-07": Facet.POLICIES,  # Rules -- "What rules govern its use?"
    "QM-CONST/CO-11": Facet.LIFECYCLE,  # States
    "QM-CONST/CO-12": Facet.TEMPORAL_HISTORY,  # Events
    "QM-CONST/CO-14": Facet.EVIDENCE,  # Evidence
    "QM-CONST/CO-15": Facet.KNOWLEDGE_CONTEXT,  # Knowledge
    "QM-CONST/CO-18": Facet.GOVERNANCE_CONTEXT,  # Governance
    "QM-CONST/CO-19": Facet.SECURITY_CONTEXT,  # Security
    "QM-CONST/CO-23": Facet.RUNTIME_BINDINGS,  # Runtime
    "QM-CONST/CO-24": Facet.EVOLUTION_HISTORY,  # Evolution
    "QM-CONST/CO-25": Facet.PROJECTION_BINDINGS,  # Projection
}

#: Answered by an instrument rather than by a facet. These are things the substrate HAS, not
#: questions an object answers about itself, and forcing them into the facet enum would be a
#: constitutional amendment -- every object in the universe suddenly owing a new answer.
CONSTITUTION_INSTRUMENT = {
    "QM-CONST/CO-08": "engine/uckp/law.py",  # Laws
    "QM-CONST/CO-09": "engine/uckp/capabilities.py",  # Capabilities
    "QM-CONST/CO-13": "platform/universal_measurement",  # Measurements
    "QM-CONST/CO-17": "engine/uckp/intelligence.py",  # Intelligence
    "QM-CONST/CO-22": "platform/commercial_intelligence",  # Commercialization
}

#: Neither a facet nor an instrument. Five of the twenty-five, and the list is worth reading
#: as a set: Purpose, Behaviors, Information, Privacy and Economics. The substrate can say
#: what a thing IS and who governs it, and cannot say what it is FOR, how it ACTS, or what
#: it costs.
CONSTITUTION_ABSENT = {
    "QM-CONST/CO-03": "purpose",
    "QM-CONST/CO-10": "behavior",
    "QM-CONST/CO-16": "information",
    "QM-CONST/CO-20": "privacy",
    "QM-CONST/CO-21": "economics",
}


def test_every_constitutional_facet_is_a_facet_an_instrument_or_absent() -> None:
    mandates = section("QM-CONST")
    assert len(mandates) == 25, f"the model names 25 facets, corpus has {len(mandates)}"
    assert_partitions(
        "QM-CONST",
        mandates,
        CONSTITUTION_FACET,
        CONSTITUTION_INSTRUMENT,
        CONSTITUTION_ABSENT,
    )


def test_each_mapped_facet_is_required_and_declares_the_question_it_answers() -> None:
    for mandate, facet in CONSTITUTION_FACET.items():
        assert facet in REQUIRED_FACETS, f"{mandate}: {facet} is not a required facet"
        assert facet.question.endswith("?"), (
            f"{mandate}: facet {facet.value!r} declares no question, so it cannot be the "
            "answer to an interrogative mandate"
        )


def test_the_facet_mapping_is_injective() -> None:
    """NON-VACUITY. Two mandated facets answered by one facet means one is unanswered."""
    facets = list(CONSTITUTION_FACET.values())
    duplicated = sorted({f.value for f in facets if facets.count(f) > 1})
    assert not duplicated, f"facets claimed by more than one mandate: {duplicated}"


def test_every_instrument_home_is_tracked() -> None:
    assert_homes_exist("QM-CONST", CONSTITUTION_INSTRUMENT)


def test_the_absent_five_are_neither_a_facet_nor_a_module() -> None:
    """NON-VACUITY, in both directions: no facet carries the name, and no tracked module is
    named for it. Either alone would let a real answer read as missing."""
    facet_names = {facet.value.replace("-", "") for facet in Facet}
    for mandate, concept in CONSTITUTION_ABSENT.items():
        assert (
            concept.replace(" ", "") not in facet_names
        ), f"{mandate}: {concept!r} is declared absent but a facet is named for it"
    assert_named_by_nothing("QM-CONST", CONSTITUTION_ABSENT)


def test_the_naming_rule_this_suite_relies_on_can_find_something() -> None:
    assert_absence_rule_can_find_something("uckp capabilities")


# --- QM-FLOW — the twenty-eight stages of the constitutional flow ----------------
#
# The interrogative model ends in a FLOW: Potential through Evolution Registration and back
# to Repository Truth, then infinity. UCL-000001 declares this repository's own lifecycle as
# forty-five stages, so the question is whether the flow the document draws is the lifecycle
# the repository runs.
#
# Seventeen stages the two agree on by name. Ten more are performed by an instrument the
# lifecycle does not name as a stage -- which is a difference in where the boundary of
# "lifecycle" falls, not a missing capability, and calling them absent would be wrong. One
# is genuinely nothing: Potential, the state before anything exists, which a lifecycle of
# governed objects has no stage for by construction.
#
# The stage names are read from `ucl.json` rather than restated here, so a lifecycle that
# renamed a stage breaks this binding instead of silently passing.

#: Flow stage -> the UCL-000001 lifecycle stage that performs it, by that stage's own name.
FLOW_LIFECYCLE_STAGE = {
    "QM-FLOW/FL-02": "Observe",  # Observation
    "QM-FLOW/FL-03": "Knowledge Discovery",  # Discovery
    "QM-FLOW/FL-04": "Perceive",  # Recognition
    "QM-FLOW/FL-06": "Assign Universal Constitutional Identifier",  # Identity Resolution
    "QM-FLOW/FL-07": "Context Assimilation",  # Context Resolution
    "QM-FLOW/FL-09": "Constraint Discovery",  # Constraint Resolution
    "QM-FLOW/FL-11": "Update Repository Truth",  # Repository Truth
    "QM-FLOW/FL-17": "Validate",  # Validation
    "QM-FLOW/FL-18": "Verify",  # Verification
    "QM-FLOW/FL-19": "Certify",  # Certification
    "QM-FLOW/FL-20": "Register",  # Registration
    "QM-FLOW/FL-21": "Integrate",  # Deployment
    "QM-FLOW/FL-24": "Measure",  # Measurement
    "QM-FLOW/FL-25": "Learn",  # Learning
    "QM-FLOW/FL-26": "Extract Engineering Knowledge",  # Knowledge Extraction
    "QM-FLOW/FL-27": "Elevate",  # Capability Elevation
    "QM-FLOW/FL-28": "Register Engineering Knowledge",  # Evolution Registration
}

#: Flow stage -> an instrument that performs it outside the declared lifecycle.
FLOW_INSTRUMENT = {
    "QM-FLOW/FL-05": "engine/knowledge/ukip/classification.py",  # Classification
    "QM-FLOW/FL-08": "engine/uckp/resolution.py",  # Relationship Resolution
    "QM-FLOW/FL-10": "engine/uckp/assimilation.py",  # Knowledge Assimilation
    "QM-FLOW/FL-12": "intelligence/realization/planning.py",  # Planning
    "QM-FLOW/FL-13": "engine/knowledge/integration/composition.py",  # Composition
    "QM-FLOW/FL-14": "engine/foundation/config",  # Configuration
    "QM-FLOW/FL-15": "intelligence/realization/generators",  # Generation
    "QM-FLOW/FL-16": "intelligence/realization/implementation.py",  # Implementation
    "QM-FLOW/FL-22": "engine/runtime",  # Runtime
    "QM-FLOW/FL-23": "platform/observability",  # Monitoring
}

#: Performed by nothing, and correctly so.
FLOW_ABSENT = {"QM-FLOW/FL-01": "Potential"}


def _ucl_stage_names() -> set[str]:
    """The stage names UCL-000001 declares, read from its own generated state."""
    import json

    from engine.tests.conformance.mandate_corpus import repo_root

    ucl = json.loads(
        (repo_root() / "00-MASTER" / "UCL-000001" / "ucl.json").read_text(encoding="utf-8")
    )
    return {str(stage.get("stage") or "") for stage in ucl["stages"]}


def test_every_flow_stage_is_a_lifecycle_stage_an_instrument_or_absent() -> None:
    mandates = section("QM-FLOW")
    assert len(mandates) == 28, f"the flow draws 28 stages, corpus has {len(mandates)}"
    assert_partitions(
        "QM-FLOW",
        mandates,
        FLOW_LIFECYCLE_STAGE,
        FLOW_INSTRUMENT,
        FLOW_ABSENT,
    )


def test_every_lifecycle_backed_stage_names_a_stage_ucl_declares() -> None:
    declared = _ucl_stage_names()
    assert len(declared) >= 40, f"UCL declares only {len(declared)} stages; the join is suspect"
    for mandate, stage in FLOW_LIFECYCLE_STAGE.items():
        assert stage in declared, (
            f"{mandate}: UCL-000001 declares no stage named {stage!r}; the lifecycle renamed "
            "it or never had it, and either way this join is stale"
        )
    claimed = list(FLOW_LIFECYCLE_STAGE.values())
    duplicated = sorted({s for s in claimed if claimed.count(s) > 1})
    assert not duplicated, f"one lifecycle stage claimed by two flow stages: {duplicated}"


def test_every_instrument_backed_stage_is_tracked_and_is_not_a_lifecycle_stage() -> None:
    """The tier boundary. A stage UCL declares belongs in the lifecycle tier, and putting it
    here would understate how strongly the repository holds it."""
    assert_homes_exist("QM-FLOW", FLOW_INSTRUMENT)
    declared = {name.lower() for name in _ucl_stage_names()}
    mandates = section("QM-FLOW")
    for mandate in FLOW_INSTRUMENT:
        assert mandates[mandate].lower() not in declared, (
            f"{mandate}: {mandates[mandate]!r} IS a declared lifecycle stage and is "
            "understated as a loose instrument"
        )


def test_potential_is_absent_because_a_lifecycle_of_objects_cannot_have_a_stage_for_it() -> None:
    """NON-VACUITY for the one absent stage, and the reason is structural rather than a gap.

    `Potential` is the state before anything exists. UCL governs objects, and an object in
    the potential state is one that has not been minted -- Article 2 says nothing exists
    constitutionally until it has become a knowledge object. A stage for it would be a stage
    with no subject.
    """
    declared = {name.lower() for name in _ucl_stage_names()}
    assert "potential" not in declared
    assert not [
        path
        for path in tracked()
        if path.endswith(".py") and "potential" in path.rsplit("/", 1)[-1].lower()
    ], "a potential module now exists; FL-01 is no longer absent by construction"


def test_the_flow_and_the_lifecycle_agree_more_than_they_differ() -> None:
    """The finding. Seventeen of twenty-eight stages match by name across two documents
    written independently, which is what makes the ten differences legible as boundary
    disagreements rather than as holes."""
    assert len(FLOW_LIFECYCLE_STAGE) == 17
    assert len(FLOW_INSTRUMENT) == 10
    assert len(FLOW_LIFECYCLE_STAGE) > len(FLOW_INSTRUMENT) + len(FLOW_ABSENT)


# --- QM-WHY / WHO / WHERE / WHEN — thirty-four questions against thirty-three facets ---
#
# The interrogative model asks questions. Article 6 declares facets, and a facet IS a
# question -- `Facet.question` returns the one it answers, in the law's own words. So these
# sections have a respondent that needs no interpretation: for each mandated question, which
# facet answers it?
#
# The four sections below hold thirty-four questions. Twenty-two have a facet. Twelve do
# not, and they are not scattered: every unanswered question is about the FUTURE, about a
# BENEFICIARY, or about PURPOSE. The facet model describes what a thing is, what has
# happened to it and what holds of it now. It has no facet for what will happen, for whom it
# is for, or for why it should exist at all -- and the WHY section is unanswered entire.

#: Question -> the facet that answers it. One facet may answer two questions when the two
#: are the same question asked twice; those are named in the test below rather than hidden.
QUESTION_FACET = {
    # WHO
    "QM-WHO/WO-01": Facet.PROVENANCE,  # Who created
    "QM-WHO/WO-02": Facet.OWNERSHIP,  # Who owns
    "QM-WHO/WO-03": Facet.GOVERNANCE_CONTEXT,  # Who governs
    "QM-WHO/WO-04": Facet.OBSERVER_CONTEXT,  # Who observes
    "QM-WHO/WO-05": Facet.GOVERNANCE_CONTEXT,  # Who decides -- the governing body decides
    "QM-WHO/WO-06": Facet.RUNTIME_BINDINGS,  # Who executes
    "QM-WHO/WO-07": Facet.CERTIFICATION,  # Who certifies
    "QM-WHO/WO-08": Facet.AUDIT,  # Who evolves -- who did what to it, provably
    # WHERE
    "QM-WHERE/WR-01": Facet.EXISTENCE_CONTEXT,  # Where does it exist
    "QM-WHERE/WR-02": Facet.CONTEXT,  # Where is it valid
    "QM-WHERE/WR-03": Facet.RUNTIME_BINDINGS,  # Where is it executed
    "QM-WHERE/WR-04": Facet.OBSERVER_CONTEXT,  # Where is it observed
    "QM-WHERE/WR-05": Facet.PERSISTENCE_BINDINGS,  # Where is it stored
    "QM-WHERE/WR-06": Facet.RUNTIME_BINDINGS,  # Where is it deployed
    "QM-WHERE/WR-07": Facet.GOVERNANCE_CONTEXT,  # Where is it governed
    "QM-WHERE/WR-10": Facet.PROJECTION_BINDINGS,  # Where can it project
    # WHEN
    "QM-WHEN/WN-01": Facet.TEMPORAL_HISTORY,  # When was it created
    "QM-WHEN/WN-02": Facet.CONTEXT,  # When is it valid
    "QM-WHEN/WN-04": Facet.TEMPORAL_HISTORY,  # When does it change
    "QM-WHEN/WN-06": Facet.EVOLUTION_HISTORY,  # When does it evolve
    "QM-WHEN/WN-07": Facet.CERTIFICATION,  # When is it certified
    "QM-WHEN/WN-08": Facet.AUDIT,  # When is it observed
    "QM-WHEN/WN-09": Facet.REPLAY,  # When is it replayed
}

#: Questions about the FUTURE. Every facet is a record of something that has already
#: happened or a condition that already holds, so none of these has an answer.
QUESTION_ABOUT_FUTURE = {
    "QM-WHERE/WR-08": "Where can it evolve",
    "QM-WHERE/WR-09": "Where can it replicate",
    "QM-WHEN/WN-03": "When does it execute",
    "QM-WHEN/WN-05": "When does it expire",
    "QM-WHEN/WN-10": "When is the next evolution",
}

#: Questions about a BENEFICIARY. The object model names who acts on a thing and never who
#: it is for.
QUESTION_ABOUT_BENEFICIARY = {
    "QM-WHO/WO-09": "Who consumes",
    "QM-WHO/WO-10": "Who benefits",
}

#: The WHY section, unanswered entire. This is the Purpose gap that QM-CONST, MI-000 and
#: ARCH-UCMM each record separately, arriving here as four questions nothing can answer.
QUESTION_ABOUT_PURPOSE = {
    "QM-WHY/WY-01": "Why does anything exist",
    "QM-WHY/WY-02": "Why should it exist",
    "QM-WHY/WY-03": "Why should it evolve",
    "QM-WHY/WY-04": "Why should it continue",
}


def test_every_interrogative_question_is_answered_or_declared_unanswerable() -> None:
    mandates: dict[str, str] = {}
    for name in ("QM-WHY", "QM-WHO", "QM-WHERE", "QM-WHEN"):
        mandates.update(section(name))
    assert len(mandates) == 34, f"the four sections ask 34 questions, corpus has {len(mandates)}"
    assert_partitions(
        "QM-WHY/WHO/WHERE/WHEN",
        mandates,
        QUESTION_FACET,
        QUESTION_ABOUT_FUTURE,
        QUESTION_ABOUT_BENEFICIARY,
        QUESTION_ABOUT_PURPOSE,
    )


def test_every_answering_facet_is_required_and_declares_its_own_question() -> None:
    for mandate, facet in QUESTION_FACET.items():
        assert facet in REQUIRED_FACETS, f"{mandate}: {facet} is not a required facet"
        assert facet.question.endswith("?"), f"{mandate}: {facet.value!r} declares no question"


def test_the_facets_answering_two_questions_answer_the_same_question_twice() -> None:
    """NON-VACUITY for the four shared facets. A facet answering two DIFFERENT questions
    would mean one of them is unanswered and the mapping is hiding it, so the pairs are
    named here and each pair has to be two phrasings of one question."""
    shared: dict[Facet, list[str]] = {}
    for mandate, facet in QUESTION_FACET.items():
        shared.setdefault(facet, []).append(mandate)
    doubled = {facet: sorted(ms) for facet, ms in shared.items() if len(ms) > 1}
    assert {f.value for f in doubled} == {
        "audit",
        "certification",
        "context",
        "governance-context",
        "observer-context",
        "runtime-bindings",
        "temporal-history",
    }, f"the set of doubled facets changed: {sorted(f.value for f in doubled)}"

    # Each pair is one question asked from two directions: WHO governs and WHERE it is
    # governed are the governing body; WHO certifies and WHEN it was certified are one
    # attestation. A facet answering two genuinely different questions would mean one of
    # them is unanswered, so any change to this set has to be re-read, not re-baselined.
    assert doubled[Facet.GOVERNANCE_CONTEXT] == [
        "QM-WHERE/WR-07",
        "QM-WHO/WO-03",
        "QM-WHO/WO-05",
    ]


def test_no_facet_answers_a_question_about_the_future() -> None:
    """NON-VACUITY, and the finding. Every facet question is in the past or present tense --
    what happened, what holds, what was certified. If one ever asks what WILL happen, these
    five questions have an answer and this tier is wrong.

    `Facet.REPLAY` asks "How CAN it be reproduced exactly?" and the first draft of this test
    read that as future tense. It is not: reproducing is a capability that holds now, over a
    record of what already happened. A test for future tense has to look for future tense.
    """
    future_words = ("will ", "next ", "expire", "future")
    offending = [
        facet.value
        for facet in Facet
        if any(word in facet.question.lower() for word in future_words)
    ]
    assert not offending, (
        f"these facets now ask about the future: {offending}; the questions tiered as "
        "unanswerable may now have answers"
    )


def test_no_facet_asks_why_or_for_whom() -> None:
    """NON-VACUITY for the other two tiers, and the sharpest statement of the Purpose gap:
    of thirty-three questions the law declares, not one begins with Why."""
    questions = [facet.question.lower() for facet in Facet]
    assert not [
        q for q in questions if q.startswith("why")
    ], "a facet now asks Why; the WHY section is no longer unanswered entire"
    assert not [
        q for q in questions if "for whom" in q or "benefit" in q
    ], "a facet now asks who a thing is for; the beneficiary questions have an answer"


def test_the_purpose_gap_is_the_same_one_three_other_sections_record() -> None:
    """Four questions here, one constitutional facet in QM-CONST, one kernel element in
    MI-000, and one meta-model universal in ARCH-UCMM. One hole, four sightings."""
    from engine.tests.conformance.test_mandates_index import KERNEL_INTENT_ABSENT

    assert "purpose" in set(CONSTITUTION_ABSENT.values())
    assert "purpose" in set(KERNEL_INTENT_ABSENT.values())
    assert len(QUESTION_ABOUT_PURPOSE) == 4


# --- QM-WHAT / WHICH / CAN / HOW — forty-six questions ---------------------------
#
# The remaining four interrogative sections. Unlike WHO, WHERE and WHEN, most of these are
# not questions an object answers ABOUT ITSELF -- "Can generate" and "What cannot exist" are
# questions about the SUBSTRATE -- so the respondent is an instrument rather than a facet,
# and the split is kept because the two are different kinds of answer.
#
# Two of the HOW questions are answered by a facet VERBATIM: Article 6 asks "How is it found
# without anyone listing it?" and "How is it bound to everything else?", which are HW-01 and
# HW-03 word for word. The two documents were written apart and arrive at the same sentence.
#
# Three questions have no answer, and they repeat the shape found in WHO/WHERE/WHEN: What
# SHOULD exist and what WILL exist are normative and future, and How is it IMPROVED has no
# instrument because Self Optimizing does not exist.

QUESTION_FACET_2 = {
    "QM-WHICH/WH-03": Facet.CONTEXT,  # Which context
    "QM-WHICH/WH-06": Facet.DEPENDENCIES,  # Which dependency
    "QM-WHICH/WH-07": Facet.CONSTRAINTS,  # Which constraint
    "QM-WHICH/WH-08": Facet.POLICIES,  # Which rule
    "QM-WHICH/WH-09": Facet.POLICIES,  # Which policy -- the same facet, the same question
    "QM-WHICH/WH-10": Facet.EVOLUTION_HISTORY,  # Which evolution
    "QM-HOW/HW-01": Facet.DISCOVERY,  # How is it discovered -- the facet's own words
    "QM-HOW/HW-02": Facet.SEMANTIC_IDENTITY,  # How is it understood
    "QM-HOW/HW-03": Facet.RELATIONSHIPS,  # How is it related -- the facet's own words
    "QM-HOW/HW-08": Facet.VALIDATION,  # How is it validated
    "QM-HOW/HW-09": Facet.VERIFICATION,  # How is it verified
    "QM-HOW/HW-10": Facet.CERTIFICATION,  # How is it certified
    "QM-HOW/HW-11": Facet.RUNTIME_BINDINGS,  # How is it deployed
    "QM-HOW/HW-15": Facet.EVOLUTION_HISTORY,  # How is it evolved
}

QUESTION_INSTRUMENT = {
    # WHAT -- questions about the universe of things, answered by registers and refusals
    "QM-WHAT/WT-01": "00-MASTER/UCOS-UGA-001/00-EXISTENCE-INVENTORY.json",  # What exists
    "QM-WHAT/WT-02": "engine/kernel/kernel.py",  # What can exist -- open by registration
    "QM-WHAT/WT-03": "engine/kernel/compliance.py",  # What cannot exist -- PROHIBITED_TOKENS
    "QM-WHAT/WT-04": "00-BOOK/DATA/allocation-permits.json",  # What may exist
    "QM-WHAT/WT-05": "engine/uckp/facets.py",  # What must exist -- REQUIRED_FACETS
    "QM-WHAT/WT-08": "engine/registry/universal/records.py",  # What no longer exists
    "QM-WHAT/WT-09": "engine/kernel/compliance.py",  # What is unknown -- UNKNOWN_CATEGORIES
    # WHICH
    "QM-WHICH/WH-01": "engine/uckp/evolution.py",  # Which version -- the state chain
    "QM-WHICH/WH-02": "engine/provider/selection.py",  # Which variant
    "QM-WHICH/WH-04": "engine/foundation/config",  # Which configuration
    "QM-WHICH/WH-05": "engine/uckp/capabilities.py",  # Which capability
    # CAN
    "QM-CAN/CN-01": "engine/universal_discovery",  # Can discover
    "QM-CAN/CN-02": "engine/constitution/assimilation.py",  # Can reuse
    "QM-CAN/CN-03": "platform/foundation/derivation.py",  # Can derive
    "QM-CAN/CN-04": "engine/foundation/config",  # Can configure
    "QM-CAN/CN-05": "engine/knowledge/integration/composition.py",  # Can compose
    "QM-CAN/CN-06": "intelligence/realization/generators",  # Can generate
    "QM-CAN/CN-07": "intelligence/realization/implementation.py",  # Can implement
    "QM-CAN/CN-08": "engine/validation",  # Can validate
    "QM-CAN/CN-09": "engine/uaue/verification.py",  # Can verify
    "QM-CAN/CN-10": "engine/certification",  # Can certify
    "QM-CAN/CN-11": "platform/commercial_intelligence",  # Can commercialize
    "QM-CAN/CN-12": "engine/constitution/evolution.py",  # Can evolve
    # HOW
    "QM-HOW/HW-04": "engine/foundation/config",  # How is it configured
    "QM-HOW/HW-05": "engine/knowledge/integration/composition.py",  # How is it composed
    "QM-HOW/HW-06": "intelligence/realization/generators",  # How is it generated
    "QM-HOW/HW-07": "intelligence/realization/implementation.py",  # How is it implemented
    "QM-HOW/HW-12": "engine/runtime",  # How is it operated
    "QM-HOW/HW-13": "platform/observability",  # How is it monitored
}

QUESTION_UNANSWERED_2 = {
    "QM-WHAT/WT-06": "What should exist",
    "QM-WHAT/WT-07": "What will exist",
    "QM-HOW/HW-14": "How is it improved",
}


def test_every_remaining_interrogative_is_answered_or_unanswered() -> None:
    mandates: dict[str, str] = {}
    for name in ("QM-WHAT", "QM-WHICH", "QM-CAN", "QM-HOW"):
        mandates.update(section(name))
    assert len(mandates) == 46, f"the four sections ask 46 questions, corpus has {len(mandates)}"
    assert_partitions(
        "QM-WHAT/WHICH/CAN/HOW",
        mandates,
        QUESTION_FACET_2,
        QUESTION_INSTRUMENT,
        QUESTION_UNANSWERED_2,
    )


def test_every_answering_instrument_is_tracked() -> None:
    assert_homes_exist("QM-WHAT/WHICH/CAN/HOW", QUESTION_INSTRUMENT)


def test_the_two_how_questions_the_law_asks_verbatim_really_are_verbatim() -> None:
    """NON-VACUITY, and the most direct evidence that these two documents describe one
    system: the mandate and the facet are the same sentence."""
    mandates = section("QM-HOW")
    assert Facet.DISCOVERY.question == "How is it found without anyone listing it?"
    assert Facet.RELATIONSHIPS.question == "How is it bound to everything else?"
    assert mandates["QM-HOW/HW-01"] == "How is it discovered"
    assert mandates["QM-HOW/HW-03"] == "How is it related"


def test_what_is_unknown_is_answered_and_is_no_longer_a_gap() -> None:
    """`What is unknown` is one of the concepts CAEM-001 dispositions CREATE, on the grounds
    that a zero-length head noun could not be searched. The kernel answers it directly:
    UNKNOWN_CATEGORIES is the declared list of categories the substrate does not know, and
    the architectural proof represents every one of them."""
    from engine.kernel.compliance import UNKNOWN_CATEGORIES, architectural_proof

    assert len(UNKNOWN_CATEGORIES) >= 11
    proof = architectural_proof()
    proven = {record["category"] for record in proof["records"] if record["ok"]}
    declared = {key for key, _instance, _attributes in UNKNOWN_CATEGORIES}
    assert declared <= proven, f"unknown categories nothing represents: {sorted(declared - proven)}"
    assert proof["kernel_unchanged"] is True


def test_the_three_unanswered_questions_are_normative_future_or_improvement() -> None:
    """NON-VACUITY. Two ask what SHOULD or WILL be, which no register of what IS can answer.
    The third has no instrument because Self Optimizing does not exist -- so if that lands,
    this question is answered and the tier is wrong."""
    from engine.tests.conformance.test_mandates_prd import SELF_NEAR_MISS

    assert (
        "PRD-SELF/SELF-11" in SELF_NEAR_MISS
    ), "Self Optimizing now exists; QM-HOW/HW-14 has an instrument and must be re-tiered"
    assert set(QUESTION_UNANSWERED_2) == {
        "QM-WHAT/WT-06",
        "QM-WHAT/WT-07",
        "QM-HOW/HW-14",
    }


# --- QM-OUT — the outputs, and the nine still unaccounted ------------------------
#
# The interrogative model closes with thirty OUTPUTS. Twenty-one are bound through the
# sections that own them; the nine below are the rest, and they divide into four kinds.
#
# ROBOTS IS ON THE CREATE LIST AND SHOULD NOT BE. `Robotics` is one of the twenty-seven
# target domains MI-017 lists, and MI-017 already settles what a market is owed: admission,
# never construction. A robot built as an output of this substrate is the fixed industry
# LYR-NEG/LN-05 forbids, and MI-015/PJ-25 already records Robotics as a projection with no
# producer for the same reason.

#: Output -> the instrument that produces it.
OUTPUT_INSTRUMENT = {
    "QM-OUT/OU-08": "engine/context/ontology.py",  # Ontologies
    "QM-OUT/OU-09": "engine/context/taxonomy.py",  # Taxonomies
    "QM-OUT/OU-11": "00-BOOK/DATA",  # Data
}

#: Output -> the section that owns the set. Models are the twenty MI-003 declares; counting
#: them again here would be a second authoring of one inventory.
OUTPUT_VIA_SECTION = {"QM-OUT/OU-05": "MI-003"}  # Models

#: Market-shaped outputs. Admitted as registered data, never built -- the MI-017 rule.
OUTPUT_MARKET_SHAPED = {
    "QM-OUT/OU-24": "Organizations",
    "QM-OUT/OU-26": "Robots",
}

#: Not outputs at all: the document's own words for the totality and the openness of the
#: list. `Everything` heads the column, and the last two entries say the column can grow.
OUTPUT_TOTALITY_AND_OPENNESS = {
    "QM-OUT/OU-01": "Everything",
    "QM-OUT/OU-29": "Future Systems",
    "QM-OUT/OU-30": "Unknown Future Projections",
}


def test_the_nine_remaining_outputs_are_accounted_four_ways() -> None:
    mandates = section("QM-OUT")
    assert len(mandates) == 30, f"the model lists 30 outputs, corpus has {len(mandates)}"
    covered = {
        **OUTPUT_INSTRUMENT,
        **OUTPUT_VIA_SECTION,
        **OUTPUT_MARKET_SHAPED,
        **OUTPUT_TOTALITY_AND_OPENNESS,
    }
    assert len(covered) == 9
    foreign = sorted(set(covered) - set(mandates))
    assert not foreign, f"tiered identifiers that are not QM-OUT mandates: {foreign}"
    assert_homes_exist("QM-OUT", OUTPUT_INSTRUMENT)


def test_models_are_the_twenty_the_master_index_declares() -> None:
    """The join. Re-listing the models here would be a second authoring of one inventory."""
    from engine.tests.conformance.test_mandates_index import (
        UNIVERSAL_MODEL,
        UNIVERSAL_MODEL_ABSENT,
    )

    assert OUTPUT_VIA_SECTION["QM-OUT/OU-05"] == "MI-003"
    assert (
        len(UNIVERSAL_MODEL) + len(UNIVERSAL_MODEL_ABSENT) == 20
    ), "MI-003 no longer accounts for twenty models; the output row rests on that section"


def test_robots_and_organizations_are_admitted_not_built() -> None:
    """The correction this binding makes, and the reason it is not new construction.

    `Robots` is dispositioned CREATE. `Robotics` is an MI-017 target domain, and
    `organization` shares the axis `company` -- a prohibited token. Both admit as registered
    metatypes with the kernel unchanged, which is what a market is owed.
    """
    from engine.kernel.compliance import PROHIBITED_TOKENS, kernel_source_fingerprint
    from engine.kernel.kernel import MetaKernel

    domains = {label.lower() for label in section("MI-017").values()}
    assert (
        "robotics" in domains
    ), "Robotics is no longer a target domain; the Robots output may be construction after all"
    assert "company" in PROHIBITED_TOKENS, (
        "`company` is no longer refused, so Organizations could be seeded as a concrete "
        "market and this row must be re-decided"
    )

    kernel = MetaKernel()
    before = kernel_source_fingerprint()
    for label in OUTPUT_MARKET_SHAPED.values():
        kernel.register_metatype(f"Output-{label}", name=label, description=f"output: {label}")
    assert kernel_source_fingerprint() == before, (
        "admitting the market-shaped outputs changed the kernel's source, so they were built "
        "rather than registered -- the fixed-industry failure LN-05 forbids"
    )
    registered = {obj.natural_key for obj in kernel.metatypes()}
    assert {"Output-Robots", "Output-Organizations"} <= registered


def test_everything_and_the_future_entries_are_not_outputs() -> None:
    """NON-VACUITY for the last tier. `Everything` heads the column and the last two entries
    say the column can grow; treating any of the three as a deliverable would report three
    products where the document states a totality and an openness."""
    mandates = section("QM-OUT")
    labels = list(mandates.values())
    assert (
        labels[0] == "Everything"
    ), f"the outputs no longer open with the totality word: {labels[0]!r}"
    assert (
        labels[-1] == "Unknown Future Projections"
    ), f"the outputs no longer close with the openness claim: {labels[-1]!r}"
    for mandate in OUTPUT_TOTALITY_AND_OPENNESS:
        assert mandate not in OUTPUT_INSTRUMENT
        assert mandate not in OUTPUT_MARKET_SHAPED
