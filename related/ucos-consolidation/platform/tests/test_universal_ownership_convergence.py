"""Tests for the converged canonical-ownership determination and governance reduction.

Two ownership determinations once existed over one population and reported different numbers.
These tests hold the converged determination to the standard that made the convergence
defensible in the first place:

    * it must reproduce the retired determination's measurement, not merely replace it;
    * it must still **refuse to infer**, so the negative cases are load bearing — a change
      that made an unresolved subject resolve would be a regression even though it improves
      the numbers (``CEP-002`` 14.2);
    * a recommendation must never become ownership, at any grain, under any provider.
"""

from __future__ import annotations

import json
from platform.universal_foundation.bootstrap import (
    bootstrap_project_ownership,
    bootstrap_universal_foundation,
    canonical_home_policy,
    registered_locators,
)
from platform.universal_ownership.contracts import (
    OwnershipDetermination,
    OwnershipGranularity,
    OwnershipRecord,
    OwnershipStanding,
)
from platform.universal_ownership.determination import OwnershipDeterminationEngine
from platform.universal_ownership.errors import (
    OwnershipContractError,
    OwnershipEvidenceError,
    OwnershipRecommendationError,
)
from platform.universal_ownership.evidence import (
    DeclaredIdentityProvider,
    EvidenceProviderRegistry,
    RoleLocatorProvider,
    read_declared_identities,
)
from platform.universal_ownership.recommendation import (
    BASIS_ELIGIBLE_LOCATOR,
    BASIS_PEER_PRECEDENT,
    EligibleLocatorRecommendationProvider,
    GovernanceReductionEngine,
    GovernanceWorkload,
    OwnershipRecommendation,
    PeerPrecedentRecommendationProvider,
    RecommendationProviderRegistry,
    build_governance_reduction,
)
from platform.universal_truth.contracts import Subject
from platform.universal_truth.eligibility import (
    REASON_DERIVED_RESIDUE,
    REASON_FORM_NOT_ADMITTED,
    REASON_NOT_REGISTERED,
    REASON_ZONE_INELIGIBLE,
    CanonicalHomePolicy,
    EligibilityLedger,
    load_eligibility_ledger,
    open_ledger,
)
from platform.universal_truth.errors import RepositoryTruthError, TruthEligibilityError
from platform.universal_truth.policy import default_truth_policy

import pytest

CONSTITUTION = "02-MASTER/THING-001-CONSTITUTION.md"
REALIZATION = "06-IMPLEMENTATION/THING-001-IMPLEMENTATION.md"
PEER = "02-MASTER/THING-001-OTHER-AUTHORITY.md"
EVIDENCE = "02-MASTER/x_evidence/THING-001.md"
PROJECTION = "00-BOOK/DATA/artifacts.json"

#: The measurement the retired engine-side resolver produced over this repository. The
#: converged determination must reproduce it exactly; that reproduction is what made retiring
#: the second implementation a convergence rather than a replacement. The pin advances with
#: the measured population: Ω-A12 registered the Foundation's specialisation catalogue as a
#: concept (541 → 542), and the one new concept stands unresolved (390 → 391), so each count
#: moves by exactly its measured amount while declared and contested hold still.
#:
#: CLOSURE-SYNC-001 advances it again for the same reason. UAKOS-CLOSURE-002 now measures 549
#: concepts: the seven UCKO-{ALIAS,EXPLICIT,NOBODY,PEER,TARGET,WRONG,X}-0001 identities carried
#: by engine/tests/knowledge/ukip/test_registry.py — a file tracked since W0-2 and unmodified
#: since — became visible to the concept scan when the upstream model was re-rendered. All
#: seven stand unresolved, so total moves 542 → 549 and unresolved 391 → 398 by exactly the
#: measured population delta, while declared (151) and contested (0) hold still. Those two
#: are the convergence claim: the retired resolver's answer is still reproduced exactly.
#:
#: CLOSURE-HOME-001 advances `declared` for the first time, and the reason it may is that the
#: RESOLVER did not change — the evidence did. This pin compares two implementations of one
#: rule; both read `population_document: 00-MASTER/UAKOS-CLOSURE-002/closure.json`, and the
#: retired resolver, given the input below, would answer identically. What changed is upstream:
#: UAKOS-CLOSURE-002 previously recognised a definitional home ONLY when a file's basename
#: carried the concept id. That fits one of this repository's two id conventions. The other
#: defines a whole family inside one document and declares the range in a heading —
#: `## SECTION 3 — META-RELATIONSHIPS (AMR-01…14)`. Those concepts were homed by evidence zone
#: and never declared, so the determination reported them unowned while their definition sat
#: under a header naming their exact range. Authoring `AMR-01-*.md` to satisfy the old rule
#: would have been a second authoring of existing knowledge, which UCKP-ART-03 voids.
#:
#: 90 concepts hold such a declaration and exactly one document making it, so declared moves
#: 151 → 241 and unresolved 398 → 308 by exactly that amount. The movement is CONSERVED —
#: every concept that moved went from unresolved to declared, and total (549) and contested (0)
#: hold still — which is what distinguishes an evidence delta from a resolver regression. A
#: heading counts only when it declares scope: an id leading its own heading, or falling inside
#: a declared range. An id merely appearing in a heading is a mention, and `## EC3-B10 DATA
#: REALIZATION PACKAGE (ARCH-DATA-001)` is a heading about work on a concept, not a claim to
#: define it — reading those as declarations wrongly moved 51 further concepts, and two such
#: packages then both claimed ARCH-DATA-001. A declaration must also be DELIVERED: SERVICE-005
#: declares `## SECTION 3 — META-RELATIONSHIPS (SMR-01…13)` and carries the thirteen defining
#: rows, while SERVICE-014 cites the same range under `### 15.2 Relationship consistency — all
#: within SOR-01…13 / SMR-01…13` and carries none. Without requiring delivery the two compete
#: and neither can be the home, which is why SMR-01…13 stood unowned beside their definitions.
#: Projections are excluded on the same principle:
#: a document naming another as its `Source:` is a generated view, and UCKP-ART-11 is explicit
#: that generated output never owns truth.
#:
#: CLOSURE-HOME-002 advances it once more, and for the same reason as CLOSURE-HOME-001: the
#: resolver is untouched and the evidence moved. 02-MASTER/EC-3-BAND-REALIZATION-UNIT-REGISTER.md
#: was installed under permit P-UCOS-CORPUS-008 as the definitional home of 47 EC-3 band
#: realization units — concepts that were certified, evidenced under */_evidence/, and owned by
#: no document, because Band 13's charter puts its unit table under "Recommended default WBS ...
#: Recommended, not binding" and a recommendation does not define. declared moves 241 -> 288 and
#: unresolved 308 -> 261 by exactly 47, total (549) and contested (0) hold, and the movement is
#: CONSERVED — every concept that moved went from unresolved to declared, which is what
#: separates an evidence delta from a resolver regression.
#:
#: CLOSURE-HOME-003 advances it a third time, and the reason is unchanged: the resolver is
#: untouched and the evidence moved again. Two registers were installed and one was completed
#: from a second source — 85 compiler components transcribed from PHASE-003 of the Universal
#: Platform document, 21 constitutional laws from PART XVI of Missing 2.docx plus LAW Ω∞-000
#: from the Universal Reality Compiler Constitution. declared moves 288 -> 394 and unresolved
#: 261 -> 155 by exactly 106, total (549) and contested (0) hold, and the movement is CONSERVED:
#: every concept that moved went from unresolved to declared. None of those 106 was authored.
#: Each was transcribed from a source document that already stated it, which is what keeps this
#: an evidence delta rather than a resolver regression.
#: CLOSURE-HOME-004 closes the population, and it does so on the two instruments the
#: framework itself provides — never on a resolver change. (a) The governed assignment
#: catalogue, empty before this, carries the 113 proposals the deterministic recommender
#: emitted over workloads UCOS-UOFW-06e957829500e7e1 and UCOS-UOFW-8cb3b0082e9e8d2a, each
#: entry transcribed from its strongest recommendation (owner, authority, locator, basis)
#: under operator authorization in session; declared moves 394 -> 507, and the movement is
#: CONSERVED because no proposal was edited and no owner was invented. (b)
#: 02-MASTER/UCOS-PROGRAM-FAMILY-CONCEPT-REGISTER.md installs the definitional home the
#: origin register could not be — 41 subjects move 507 -> 548, every row carried verbatim
#: from 00-MASTER/UAKOS-PHASE-001A-R1/01-AUTHORITATIVE-ORIGIN-REGISTER.md and cited there.
#: The last, UCOS-RECON-C1, resolves by a governed assignment whose locator is the eligible
#: register: its operational-memory origin names ITSELF
#: UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION and is the record of the exclusion the concept
#: legislates, not a rival definition. declared 394 -> 549, unresolved 155 -> 0, total (549)
#: and contested (0) hold, and the governance minimum measured 0 at every step.
RETIRED_MEASUREMENT = {"total": 550, "declared": 550, "contested": 0, "unresolved": 0}


def _home(*registered: str, **kwargs) -> CanonicalHomePolicy:
    """A canonical-home policy over the declared zones plus an eligibility ledger."""
    ledger = EligibilityLedger.create(
        ledger_id="test.eligibility",
        registered=registered or None,
        admitted_suffixes=kwargs.pop("admitted_suffixes", (".md",)),
        excluded_segments=kwargs.pop("excluded_segments", ("_evidence/",)),
        **kwargs,
    )
    return CanonicalHomePolicy(default_truth_policy(), ledger)


# --------------------------------------------------------------------------------------
# eligibility — the declared rules a zone class is not enough to satisfy
# --------------------------------------------------------------------------------------


def test_an_unregistered_artifact_is_not_eligible():
    home = _home(CONSTITUTION)
    assert home.admits(CONSTITUTION)
    assert home.verdict("02-MASTER/UNREGISTERED.md").reason == REASON_NOT_REGISTERED


def test_a_non_markdown_projection_is_not_eligible():
    home = _home(CONSTITUTION, PROJECTION)
    assert home.verdict(PROJECTION).reason == REASON_FORM_NOT_ADMITTED


def test_derived_residue_inside_an_eligible_zone_is_not_eligible():
    """Evidence sitting inside a canonical tree does not become canonical by adjacency."""
    home = _home(CONSTITUTION, EVIDENCE)
    assert home.verdict(EVIDENCE).reason == REASON_DERIVED_RESIDUE


def test_an_ineligible_zone_is_refused_before_any_ledger_rule_is_consulted():
    home = _home("00-MASTER/PROGRAMME/THING-001.md")
    assert home.verdict("00-MASTER/PROGRAMME/THING-001.md").reason == REASON_ZONE_INELIGIBLE


def test_an_undeclared_dimension_admits_everything():
    """Silence in a declaration means 'no such requirement', never a guessed requirement."""
    home = CanonicalHomePolicy(default_truth_policy(), open_ledger())
    assert home.admits(CONSTITUTION)
    assert home.admits(PROJECTION)
    assert not open_ledger().enforces_anything


def test_requiring_registration_without_a_ledger_fails_closed_at_decision_time():
    ledger = EligibilityLedger.create(
        ledger_id="test.deferred", require_registration=True, admitted_suffixes=(".md",)
    )
    assert ledger.require_registration
    with pytest.raises(TruthEligibilityError):
        ledger.verdict(CONSTITUTION)


def test_the_eligibility_ledger_summarises_rather_than_copies_the_registration_set():
    """A registration ledger is owned elsewhere; copying it in would restate that knowledge."""
    ledger = EligibilityLedger.create(registered=(CONSTITUTION, PEER))
    payload = ledger.to_dict()
    assert payload["registration_count"] == 2
    assert CONSTITUTION not in json.dumps(payload)


def test_by_reason_groups_a_population_for_triage():
    home = _home(CONSTITUTION, EVIDENCE, PROJECTION)
    grouped = home.by_reason((CONSTITUTION, EVIDENCE, PROJECTION, "00-MASTER/X/THING.md"))
    assert set(grouped) >= {REASON_DERIVED_RESIDUE, REASON_FORM_NOT_ADMITTED}


# --------------------------------------------------------------------------------------
# ownership grain — the constitutional position a project declares
# --------------------------------------------------------------------------------------


def _determine(home, subject, granularity):
    providers = EvidenceProviderRegistry(
        (RoleLocatorProvider("definitional-home", home, granularity=granularity),)
    )
    return OwnershipDeterminationEngine(providers, policy=home).determine_subject(subject)


def test_at_locator_grain_two_artifacts_in_one_zone_are_an_unsettled_contest():
    """Knowledge Once is a statement about locations, so this must not be absorbed."""
    home = _home(CONSTITUTION, PEER)
    subject = Subject.create("THING-001", roles={"definitional-home": (CONSTITUTION, PEER)})
    record = _determine(home, subject, OwnershipGranularity.LOCATOR)
    assert record.standing is OwnershipStanding.CONTESTED
    assert dict(record.claims) == {CONSTITUTION: 1, PEER: 1}


def test_at_authority_grain_two_artifacts_in_one_zone_are_one_owner():
    """The other defensible position: the authority owns it whichever document carries it."""
    home = _home(CONSTITUTION, PEER)
    subject = Subject.create("THING-001", roles={"definitional-home": (CONSTITUTION, PEER)})
    record = _determine(home, subject, OwnershipGranularity.AUTHORITY)
    assert record.standing is OwnershipStanding.DECLARED
    assert record.owner == "Constitutional Authority (02-MASTER)"


def test_a_contest_across_zones_is_settled_by_declared_precedence_not_a_special_case():
    """The retired resolver settled this with a hardcoded realization rule; precedence does it."""
    home = _home(CONSTITUTION, REALIZATION)
    subject = Subject.create("THING-001", roles={"definitional-home": (CONSTITUTION, REALIZATION)})
    record = _determine(home, subject, OwnershipGranularity.LOCATOR)
    assert record.standing is OwnershipStanding.DECLARED
    assert record.owner == CONSTITUTION
    assert dict(record.claims) == {CONSTITUTION: 1, REALIZATION: 1}


def test_an_unknown_granularity_fails_closed():
    with pytest.raises(OwnershipContractError):
        RoleLocatorProvider("definitional-home", _home(CONSTITUTION), granularity="sort-of")


# --------------------------------------------------------------------------------------
# role locators — reusing a measurement the project already owns
# --------------------------------------------------------------------------------------


def test_a_role_provider_adopts_the_declared_role_and_derives_nothing():
    """The provider holds no rule about what makes a locator definitional. That is the point."""
    home = _home(CONSTITUTION)
    tagged = Subject.create("THING-001", roles={"definitional-home": (CONSTITUTION,)})
    untagged = Subject.create("THING-001", locators=(CONSTITUTION,))
    provider = RoleLocatorProvider("definitional-home", home)
    assert provider.collect(tagged)
    assert not provider.collect(untagged)


def test_a_role_locator_in_an_ineligible_zone_establishes_nothing():
    home = _home(CONSTITUTION, EVIDENCE)
    subject = Subject.create("THING-001", roles={"definitional-home": (EVIDENCE,)})
    assert not RoleLocatorProvider("definitional-home", home).collect(subject)


def test_a_role_never_introduces_a_locator_the_subject_does_not_carry():
    subject = Subject.create("THING-001", roles={"definitional-home": (CONSTITUTION,)})
    assert CONSTITUTION in subject.locators
    assert subject.role("definitional-home") == (CONSTITUTION,)
    assert subject.role("undeclared") == ()


def test_a_role_provider_requires_a_declared_role_name():
    with pytest.raises(OwnershipEvidenceError):
        RoleLocatorProvider("   ", _home(CONSTITUTION))


def test_reading_declared_identities_never_scans_and_absence_is_not_an_assertion(tmp_path):
    target = tmp_path / CONSTITUTION
    target.parent.mkdir(parents=True)
    target.write_text("| ARTIFACT ID | THING-001 |\n", encoding="utf-8")
    found = read_declared_identities((CONSTITUTION, "02-MASTER/ABSENT.md"), root=tmp_path)
    assert found == {CONSTITUTION: "THING-001"}


def test_a_suffixed_declaration_does_not_claim_the_bare_subject(tmp_path):
    target = tmp_path / "02-MASTER/THING-001-GIG.md"
    target.parent.mkdir(parents=True)
    target.write_text("| ARTIFACT ID | THING-001-GIG |\n", encoding="utf-8")
    found = read_declared_identities(("02-MASTER/THING-001-GIG.md",), root=tmp_path)
    home = _home("02-MASTER/THING-001-GIG.md")
    provider = DeclaredIdentityProvider(found, home, granularity=OwnershipGranularity.LOCATOR)
    assert not provider.collect(Subject.create("THING-001"))


# --------------------------------------------------------------------------------------
# the live repository — the convergence claim itself
# --------------------------------------------------------------------------------------


def test_the_converged_determination_reproduces_the_retired_measurement():
    """The substance of the convergence: one model, and the same answer the other one gave.

    Asserted as containment, not equality: the four *standing* counts are what the retired
    engine measured and must be reproduced exactly, while an additively introduced diagnostic
    count is not a change to that answer (UFC-08).
    """
    foundation = bootstrap_universal_foundation()
    subjects = foundation.project_population()
    determination = foundation.determine_ownership(subjects)
    assert determination.counts().items() >= RETIRED_MEASUREMENT.items()


def _stripped_governed_assignments(tmp_path):
    """The live Foundation with its ownership EVIDENCE emptied — never its resolver.

    At CLOSURE-HOME-004 the repository's open population is fully declared, so the residue
    the anti-inference guards watch can no longer be observed by looking at the repository
    alone — and a guard that depends on repository residue is a guard repository evidence can
    silently disarm. These tests therefore manufacture the residue instead: the same 549
    subjects and the same declared policy, read through (a) an assignment catalogue stripped
    of its governed decisions and (b) a projection of the population document with the
    `def_homes`/`exact_homes` declaration evidence removed — the evidence state this
    repository was in before CLOSURE-HOME-001…005. Nothing about the resolver changes. Every
    subject that returns to UNRESOLVED must carry a named reason, and ownership that stands
    after the stripping must stand on evidence the stripping did not touch.
    """
    with open(
        "platform/universal_foundation/catalog/ucos-consolidation.json", encoding="utf-8"
    ) as handle:
        spec = json.load(handle)
    with open(
        "platform/universal_ownership/catalog/ucos-ownership-declarations.json", encoding="utf-8"
    ) as handle:
        catalogue = json.load(handle)
    catalogue["assignments"] = {}
    stripped_catalogue = tmp_path / "ucos-ownership-declarations.stripped.json"
    stripped_catalogue.write_text(json.dumps(catalogue), encoding="utf-8")
    with open("00-MASTER/UAKOS-CLOSURE-002/closure.json", encoding="utf-8") as handle:
        population = json.load(handle)
    for concept in population["concepts"]:
        concept["def_homes"] = []
        concept["exact_homes"] = []
    stripped_population = tmp_path / "closure.stripped.json"
    stripped_population.write_text(json.dumps(population), encoding="utf-8")
    spec["ownership_declarations"] = str(stripped_catalogue)
    spec["population_document"] = str(stripped_population)
    stripped_spec = tmp_path / "ucos-consolidation.stripped.json"
    stripped_spec.write_text(json.dumps(spec), encoding="utf-8")
    return bootstrap_universal_foundation(str(stripped_spec))


def test_the_converged_determination_still_refuses_to_infer(tmp_path):
    """Every live declaration is evidenced; with the evidence gone, the residue reopens."""
    foundation = bootstrap_universal_foundation()
    subjects = foundation.project_population()
    determination = foundation.determine_ownership(subjects)
    assert all(
        record.declaration is not None and record.declaration.locator
        for record in determination.declared
    )
    assert determination.closed, "closure is the claim now; it must be explicit, not incidental"

    stripped = _stripped_governed_assignments(tmp_path)
    stripped_subjects = stripped.project_population()
    residue = stripped.determine_ownership(stripped_subjects)
    assert residue.unresolved, "emptying the evidence inferred ownership from nothing"
    assert all(record.reasons for record in residue.unresolved)


def test_the_governance_workload_separates_ratifiable_from_irreducible(tmp_path):
    foundation = _stripped_governed_assignments(tmp_path)
    subjects = foundation.project_population()
    determination = foundation.determine_ownership(subjects)
    workload = build_governance_reduction(
        foundation.ownership.home,
        determination=determination,
        subjects=subjects,
        attribute=foundation.specialization.peer_attribute,
    ).reduce(determination, subjects)
    counts = workload.counts()
    assert counts["open"] == len(determination.unresolved) + len(determination.contested)
    assert counts["ratifiable"] + counts["irreducible"] == counts["open"]
    assert 0 < counts["ratifiable"]
    assert 0.0 < workload.reduction <= 100.0
    assert set(workload.by_basis()) == {BASIS_ELIGIBLE_LOCATOR, BASIS_PEER_PRECEDENT}


def test_the_project_registration_ledger_is_projected_not_restated():
    foundation = bootstrap_universal_foundation()
    ledger = registered_locators(foundation.specialization)
    assert ledger and len(ledger) > 100
    home = canonical_home_policy(foundation.specialization, foundation.truth)
    assert home.ledger.require_registration
    assert home.ledger.registration_count == len(ledger)


def test_the_converged_determination_is_replay_identical():
    foundation = bootstrap_universal_foundation()
    subjects = foundation.project_population()
    first = foundation.determine_ownership(subjects).to_dict()
    second = foundation.determine_ownership(subjects).to_dict()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_the_composed_ownership_engine_is_content_addressed():
    foundation = bootstrap_universal_foundation()
    assert foundation.ownership.fingerprint() == foundation.ownership.fingerprint()


def test_composing_ownership_from_the_declaration_needs_no_repository_knowledge():
    foundation = bootstrap_universal_foundation()
    engine = bootstrap_project_ownership(
        foundation.specialization, foundation.truth, foundation.project_population()
    )
    provider_ids = {item.provider_id for item in engine.providers.descriptors()}
    assert "ownership.declared-identity" in provider_ids
    assert any(item.startswith("ownership.role.") for item in provider_ids)


# --------------------------------------------------------------------------------------
# governance reduction — a recommendation is never ownership
# --------------------------------------------------------------------------------------


def test_a_recommendation_is_never_offered_for_a_declared_subject():
    """The one rule that keeps a proposal from displacing a determination."""

    home = _home(CONSTITUTION)
    provider = EligibleLocatorRecommendationProvider(home)
    subject = Subject.create("THING-001", locators=(CONSTITUTION,))
    declared = _determine(
        home,
        Subject.create("THING-001", roles={"definitional-home": (CONSTITUTION,)}),
        OwnershipGranularity.LOCATOR,
    )
    assert declared.declared
    assert provider.propose(subject, declared) == ()
    open_record = OwnershipRecord.create(
        "THING-001", OwnershipStanding.UNRESOLVED, reasons=("NO-OWNERSHIP-EVIDENCE",)
    )
    assert provider.propose(subject, open_record)


def test_a_recommendation_carries_no_field_by_which_it_could_pass_for_evidence():
    recommendation = OwnershipRecommendation.create(
        "THING-001", "Some Authority", BASIS_ELIGIBLE_LOCATOR, provider_id="p"
    )
    payload = recommendation.to_dict()
    assert payload["binding"] is False
    assert "constitutive" not in payload
    assert not hasattr(recommendation, "constitutive")


def test_a_recommendation_proposes_only_a_locator_an_authority_could_actually_ratify():
    """Proposing an ineligible home would waste the one act only governance may perform."""

    home = _home(CONSTITUTION)
    provider = EligibleLocatorRecommendationProvider(home)
    subject = Subject.create("THING-001", locators=("02-MASTER/UNREGISTERED.md",))
    record = OwnershipRecord.create(
        "THING-001", OwnershipStanding.UNRESOLVED, reasons=("NO-OWNERSHIP-EVIDENCE",)
    )
    assert provider.propose(subject, record) == ()


def test_a_thin_or_contested_peer_precedent_yields_no_precedent():
    """Inventing a precedent from a tie is exactly the inference the framework refuses."""
    foundation = bootstrap_universal_foundation()
    subjects = foundation.project_population()
    determination = foundation.determine_ownership(subjects)
    provider = PeerPrecedentRecommendationProvider.from_determination(
        determination, subjects, attribute="family", minimum_peers=1000
    )
    assert provider.count == 0
    assert provider.attribute == "family"


def test_the_governance_workload_separates_ratifiable_from_irreducible_live():
    """The live state after CLOSURE-HOME-004: nothing is open, so nothing is proposable.

    The separation itself is guarded against manufactured evidence above; this is the
    repository-state half of the claim, and it holds only while ownership remains declared
    by evidence rather than inferred.
    """
    foundation = bootstrap_universal_foundation()
    subjects = foundation.project_population()
    determination = foundation.determine_ownership(subjects)
    workload = build_governance_reduction(
        foundation.ownership.home,
        determination=determination,
        subjects=subjects,
        attribute=foundation.specialization.peer_attribute,
    ).reduce(determination, subjects)
    counts = workload.counts()
    assert counts["open"] == len(determination.unresolved) + len(determination.contested) == 0
    assert counts["ratifiable"] == counts["irreducible"] == 0
    assert workload.reduction == 100.0, "nothing is open, so nothing reduces — the engine says so"


def test_the_irreducible_residue_is_exactly_what_no_provider_can_propose_for():
    foundation = bootstrap_universal_foundation()
    subjects = foundation.project_population()
    determination = foundation.determine_ownership(subjects)
    workload = build_governance_reduction(
        foundation.ownership.home, determination=determination, subjects=subjects
    ).reduce(determination, subjects)
    proposed = {item.subject_id for item in workload.recommendations}
    assert not (set(workload.irreducible) & proposed)
    assert set(workload.ratifiable) <= proposed


def test_the_draft_document_is_explicitly_not_binding(tmp_path):
    foundation = _stripped_governed_assignments(tmp_path)
    subjects = foundation.project_population()
    determination = foundation.determine_ownership(subjects)
    workload = build_governance_reduction(
        foundation.ownership.home, determination=determination, subjects=subjects
    ).reduce(determination, subjects)
    document = workload.as_declaration_document(authority="Test Authority")
    assert document["ratified"] is False
    assert "NOT BINDING" in document["$comment"]
    assert document["assignments"]


def test_the_workload_is_replay_identical():
    foundation = bootstrap_universal_foundation()
    subjects = foundation.project_population()
    determination = foundation.determine_ownership(subjects)
    engine = build_governance_reduction(
        foundation.ownership.home, determination=determination, subjects=subjects
    )
    first = engine.reduce(determination, subjects).to_dict()
    second = engine.reduce(determination, subjects).to_dict()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_a_recommendation_provider_registry_is_deterministic_and_fail_closed():
    home = _home(CONSTITUTION)
    registry = RecommendationProviderRegistry((EligibleLocatorRecommendationProvider(home),))
    assert registry.count == 1
    with pytest.raises(OwnershipRecommendationError):
        registry.add(EligibleLocatorRecommendationProvider(home))  # same identity, different object
    with pytest.raises(OwnershipRecommendationError):
        registry.require("recommendation.nope")
    with pytest.raises(OwnershipRecommendationError):
        GovernanceReductionEngine(object())  # type: ignore[arg-type]


def test_a_recommendation_requires_every_declared_field():
    with pytest.raises(OwnershipRecommendationError):
        OwnershipRecommendation.create("", "owner", BASIS_ELIGIBLE_LOCATOR, provider_id="p")
    with pytest.raises(OwnershipRecommendationError):
        OwnershipRecommendation.create("S-1", "  ", BASIS_ELIGIBLE_LOCATOR, provider_id="p")


# --------------------------------------------------------------------------------------
# the eligibility surface — every declared dimension, and every refusal
# --------------------------------------------------------------------------------------


def test_an_eligibility_document_round_trips_and_rejects_a_malformed_field():
    ledger = EligibilityLedger.from_document(
        {
            "ledger_id": "test.document",
            "require_registration": False,
            "admitted_suffixes": [".md"],
            "excluded_segments": ["_evidence/"],
            "description": "declared",
        }
    )
    assert ledger.ledger_id == "test.document"
    assert ledger.admitted_suffixes == (".md",)
    assert ledger.excluded_segments == ("_evidence/",)
    assert ledger.description == "declared"
    assert ledger.fingerprint() == ledger.fingerprint()
    with pytest.raises(TruthEligibilityError):
        EligibilityLedger.from_document({"admitted_suffixes": ".md"})
    with pytest.raises(TruthEligibilityError):
        EligibilityLedger.from_document({"excluded_segments": "nope"})
    with pytest.raises(TruthEligibilityError):
        EligibilityLedger.from_document(["not", "a", "mapping"])


def test_an_eligibility_ledger_is_loaded_from_a_declared_document(tmp_path):
    document = tmp_path / "eligibility.json"
    document.write_text(
        json.dumps({"ledger_id": "loaded", "admitted_suffixes": [".md"]}), encoding="utf-8"
    )

    ledger = load_eligibility_ledger(document, registered=(CONSTITUTION,))
    assert ledger.ledger_id == "loaded"
    assert ledger.require_registration is True
    assert ledger.admits(CONSTITUTION)
    with pytest.raises(TruthEligibilityError):
        load_eligibility_ledger(tmp_path / "absent.json")


def test_an_empty_locator_is_refused_rather_than_defaulted():
    ledger = EligibilityLedger.create(admitted_suffixes=(".md",))
    with pytest.raises(TruthEligibilityError):
        ledger.verdict("   ")
    # The composed policy classifies first, and an empty locator cannot be classified either,
    # so the refusal surfaces as a policy error rather than an eligibility one. Both refuse.

    with pytest.raises(RepositoryTruthError):
        _home(CONSTITUTION).verdict("")


def test_filter_and_verdicts_normalise_and_deduplicate():
    ledger = EligibilityLedger.create(admitted_suffixes=(".md",))
    admitted = ledger.filter(("./" + CONSTITUTION, CONSTITUTION, PROJECTION, ""))
    assert admitted == (CONSTITUTION,)
    assert len(ledger.verdicts((CONSTITUTION, "./" + CONSTITUTION, PROJECTION))) == 2


def test_the_canonical_home_policy_reports_the_zone_authority_only_when_it_admits():
    home = _home(CONSTITUTION)
    assert home.authority(CONSTITUTION) == "Constitutional Authority (02-MASTER)"
    assert home.authority("02-MASTER/UNREGISTERED.md") == ""
    assert home.fingerprint() == home.fingerprint()
    assert home.to_dict()["eligibility"]["ledger_id"] == "test.eligibility"


def test_the_canonical_home_policy_refuses_a_malformed_composition():
    with pytest.raises(TruthEligibilityError):
        CanonicalHomePolicy(object())  # type: ignore[arg-type]
    with pytest.raises(TruthEligibilityError):
        CanonicalHomePolicy(default_truth_policy(), object())  # type: ignore[arg-type]


def test_a_ledger_declaring_nothing_reports_that_it_enforces_nothing():
    ledger = EligibilityLedger.create(ledger_id="")
    assert ledger.ledger_id == "truth.eligibility.default"
    assert not ledger.enforces_anything
    assert ledger.registration_count == 0
    assert ledger.verdict(PROJECTION).eligible


def test_an_excluded_segment_matches_a_whole_path_segment_as_well_as_a_fragment():
    ledger = EligibilityLedger.create(excluded_segments=("CHECKPOINTS",))
    assert not ledger.admits("02-MASTER/CHECKPOINTS/THING-001.md")
    assert ledger.admits(CONSTITUTION)


# --------------------------------------------------------------------------------------
# Ω-A12 — the diagnosed residue. Governance minimisation is only honest once the residue
# distinguishes work that needs an authority from work that needs an act.
# --------------------------------------------------------------------------------------


def _workload():
    foundation = bootstrap_universal_foundation()
    subjects = foundation.project_population()
    determination = foundation.determine_ownership(subjects)
    workload = build_governance_reduction(
        foundation.ownership.home,
        determination=determination,
        subjects=subjects,
        attribute=foundation.specialization.peer_attribute,
    ).reduce(determination, subjects)
    return determination, workload


def test_every_unresolved_subject_names_a_reason_or_a_located_deficit():
    """An open subject that can say nothing about itself is the failure being removed."""
    determination, _ = _workload()
    for record in determination.unresolved:
        assert record.reasons
        if record.refusals:
            assert all(
                locator and reason and provider for locator, reason, provider in record.refusals
            )


def test_the_diagnosed_deficits_come_only_from_the_declared_eligibility_vocabulary():
    """No engine may invent a deficit code; the declarations publish the closed set."""
    from platform.universal_truth.eligibility import ELIGIBILITY_REASONS, REASON_ELIGIBLE

    determination, workload = _workload()
    admissible = set(ELIGIBILITY_REASONS) - {REASON_ELIGIBLE}
    assert set(determination.by_refusal()) <= admissible
    assert set(workload.by_deficit()) <= admissible


def test_the_workload_separates_remediable_work_from_work_only_an_authority_can_do():
    determination, workload = _workload()
    counts = workload.counts()
    assert counts["remediable"] == len(determination.remediable)
    assert set(workload.remediable) <= set(workload.ratifiable) | set(workload.irreducible)
    assert set(workload.governance_minimum) == set(workload.irreducible) - set(workload.remediable)
    assert counts["governance_minimum"] == len(workload.governance_minimum)
    assert workload.determinable >= workload.reduction


def test_the_diagnosis_is_replay_identical():
    first = _workload()[1].to_dict()
    second = _workload()[1].to_dict()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_the_draft_document_publishes_the_remediable_and_irreducible_split():
    _, workload = _workload()
    document = workload.as_declaration_document(authority="A")
    assert document["ratified"] is False
    assert document["remediable"] == list(workload.remediable)
    assert document["governance_minimum"] == list(workload.governance_minimum)


def test_a_closed_population_reports_a_complete_determination():
    """The identity case: nothing open means nothing to propose and nothing to remedy."""

    foundation = bootstrap_universal_foundation()
    subjects = foundation.project_population()
    determination = foundation.determine_ownership(subjects)
    declared_only = OwnershipDetermination.create(determination.declared)
    workload = GovernanceWorkload.create(declared_only, ())
    assert workload.open_total == 0
    assert workload.reduction == 100.0
    assert workload.determinable == 100.0
    assert workload.governance_minimum == ()
    assert workload.by_deficit() == {}
