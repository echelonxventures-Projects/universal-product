"""UCOS-UOF-001 — governance reduction: proposals a governing authority could ratify.

The distinction this module exists to hold is the one between a *recommendation* and a
*determination*. A determination reads declared evidence and states what is true; a
recommendation states what an authority could decide, and is never evidence for anything. The
type carries no ``constitutive`` field precisely so a proposal cannot be mistaken for one, and
``propose`` refuses outright for a subject that already has a declared owner — the first step
by which a recommendation could quietly displace a determination.

The second subject is the workload measurement. Its point is that *remediable* work is
reported separately from *irreducible* work, so a subject whose only artifact was never
registered is not billed as constitutional ambiguity: it needs registration, not a governing
authority. ``governance_minimum`` is the residue after both, and is the number the whole
framework is trying to drive down honestly rather than by reclassification.
"""

from __future__ import annotations

from platform.universal_ownership.contracts import (
    REASON_NO_EVIDENCE,
    EvidenceKind,
    OwnershipDeclaration,
    OwnershipDetermination,
    OwnershipEvidence,
    OwnershipRecord,
    OwnershipStanding,
)
from platform.universal_ownership.errors import OwnershipRecommendationError
from platform.universal_ownership.recommendation import (
    BASIS_ELIGIBLE_LOCATOR,
    BASIS_PEER_PRECEDENT,
    DEFAULT_PRECEDENCE,
    CallableRecommendationProvider,
    EligibleLocatorRecommendationProvider,
    GovernanceReductionEngine,
    GovernanceWorkload,
    OwnershipRecommendation,
    OwnershipRecommendationProvider,
    PeerPrecedentRecommendationProvider,
    RecommendationProviderDescriptor,
    RecommendationProviderRegistry,
    build_governance_reduction,
    default_recommendation_providers,
)
from platform.universal_truth import Subject, default_truth_policy
from platform.universal_truth.eligibility import CanonicalHomePolicy

import pytest


def subject(subject_id: str, *locators: str, **attributes) -> Subject:
    return Subject.create(subject_id, locators=locators, attributes=attributes)


def record(
    subject_id: str,
    standing: OwnershipStanding = OwnershipStanding.UNRESOLVED,
    **kwargs,
) -> OwnershipRecord:
    """An open record. An absence of ownership must always name its reason."""
    kwargs.setdefault("reasons", (REASON_NO_EVIDENCE,))
    return OwnershipRecord.create(subject_id, standing, **kwargs)


def recommendation(
    subject_id: str = "S-1",
    proposed_owner: str = "OWNER-A",
    *,
    basis: str = BASIS_ELIGIBLE_LOCATOR,
    provider_id: str = "recommendation.test",
    **kwargs,
) -> OwnershipRecommendation:
    return OwnershipRecommendation.create(
        subject_id, proposed_owner, basis, provider_id=provider_id, **kwargs
    )


def descriptor(
    provider_id: str = "recommendation.test", **kwargs
) -> RecommendationProviderDescriptor:
    kwargs.setdefault("basis", BASIS_ELIGIBLE_LOCATOR)
    return RecommendationProviderDescriptor(provider_id=provider_id, **kwargs)


def callable_provider(*produced, provider_id: str = "recommendation.test", **kwargs):
    return CallableRecommendationProvider(
        descriptor(provider_id, **kwargs), lambda subject, record: produced
    )


@pytest.fixture(scope="module")
def policy():
    return default_truth_policy()


@pytest.fixture(scope="module")
def eligible_locator(policy) -> str:
    """A locator the declared Truth policy admits as a canonical home."""
    home = CanonicalHomePolicy(policy)
    for candidate in ("platform/universal_ownership/contracts.py", "engine/knowledge/model.py"):
        if home.admits(candidate):
            return candidate
    pytest.skip("the declared Truth policy admits neither probe locator")


# ---------------------------------------------------------------------------
# RecommendationProviderDescriptor
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("provider_id", ("", "   ", 7, None))
def test_a_provider_must_identify_itself(provider_id):
    with pytest.raises(OwnershipRecommendationError) as exc:
        RecommendationProviderDescriptor(provider_id=provider_id, basis=BASIS_ELIGIBLE_LOCATOR)
    assert "provider_id" in str(exc.value)


@pytest.mark.parametrize("basis", ("", "  ", 3, None))
def test_a_provider_must_declare_the_basis_it_proposes_on(basis):
    """A proposal with no stated basis is an opinion, and no authority can review one."""
    with pytest.raises(OwnershipRecommendationError) as exc:
        RecommendationProviderDescriptor(provider_id="recommendation.x", basis=basis)
    assert "basis" in str(exc.value)


@pytest.mark.parametrize("precedence", ("600", 1.5, True, None))
def test_provider_precedence_must_be_a_whole_number(precedence):
    """A bool is rejected too: True would silently order as 1 and outrank nothing meaningfully."""
    with pytest.raises(OwnershipRecommendationError) as exc:
        RecommendationProviderDescriptor(
            provider_id="recommendation.x", basis=BASIS_ELIGIBLE_LOCATOR, precedence=precedence
        )
    assert "precedence" in str(exc.value)


def test_providers_order_by_declared_precedence_then_identity():
    strong = descriptor("recommendation.b", precedence=900)
    weak = descriptor("recommendation.a", precedence=100)
    assert sorted((weak, strong), key=lambda item: item.order_key)[0] is strong


def test_a_descriptor_projects_what_it_declares():
    assert descriptor("recommendation.x", precedence=42, description="why").to_dict() == {
        "provider_id": "recommendation.x",
        "basis": BASIS_ELIGIBLE_LOCATOR,
        "precedence": 42,
        "description": "why",
    }


# ---------------------------------------------------------------------------
# OwnershipRecommendation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("missing", ("subject_id", "proposed_owner", "basis", "provider_id"))
def test_a_recommendation_requires_every_field_that_makes_it_reviewable(missing):
    fields = {
        "subject_id": "S-1",
        "proposed_owner": "OWNER-A",
        "basis": BASIS_ELIGIBLE_LOCATOR,
        "provider_id": "recommendation.test",
    }
    fields[missing] = "   "
    with pytest.raises(OwnershipRecommendationError) as exc:
        OwnershipRecommendation.create(
            fields["subject_id"],
            fields["proposed_owner"],
            fields["basis"],
            provider_id=fields["provider_id"],
        )
    assert missing in str(exc.value)


def test_a_recommendation_is_content_addressed_over_what_it_proposes():
    first = recommendation(locator="a/b.py")
    same = recommendation(locator="a/b.py")
    other = recommendation(locator="c/d.py")
    assert first.recommendation_id == same.recommendation_id != other.recommendation_id
    assert first.recommendation_id.startswith("UCOS-UOFR-")


def test_recommendation_fields_are_stripped():
    built = OwnershipRecommendation.create(
        "  S-1  ",
        " OWNER-A ",
        f" {BASIS_ELIGIBLE_LOCATOR} ",
        provider_id=" recommendation.test ",
        authority=" AUTH ",
        locator=" a/b.py ",
    )
    assert built.subject_id == "S-1"
    assert built.proposed_owner == "OWNER-A"
    assert built.provider_id == "recommendation.test"
    assert built.authority == "AUTH"
    assert built.locator == "a/b.py"


def test_a_recommendation_never_reads_as_binding():
    """There is no field by which a proposal could be mistaken for evidence."""
    payload = recommendation(detail="because").to_dict()
    assert payload["binding"] is False
    assert "constitutive" not in payload
    assert not hasattr(OwnershipRecommendation, "constitutive")


def test_proposals_order_strongest_first_then_locator_then_identity():
    strong = recommendation(locator="z.py", precedence=900)
    weak = recommendation(locator="a.py", precedence=100)
    assert sorted((weak, strong), key=lambda item: item.order_key)[0] is strong


def test_the_declaration_entry_is_the_shape_the_governed_catalogue_expects():
    """Ratification should be a reviewed paste of a governed decision, not a translation."""
    entry = recommendation(
        proposed_owner="OWNER-A", locator="a/b.py", detail="found here"
    ).as_declaration_entry()
    assert entry == {
        "owner": "OWNER-A",
        "authority": "OWNER-A",
        "locator": "a/b.py",
        "detail": f"{BASIS_ELIGIBLE_LOCATOR}: found here",
    }


def test_the_declaration_entry_falls_back_to_the_basis_alone_without_a_detail():
    entry = recommendation(authority="AUTH-B").as_declaration_entry()
    assert entry["authority"] == "AUTH-B"
    assert entry["detail"] == BASIS_ELIGIBLE_LOCATOR


def test_a_recommendation_fingerprints_over_its_projection():
    assert recommendation().fingerprint() == recommendation().fingerprint()
    assert recommendation().fingerprint() != recommendation(proposed_owner="OTHER").fingerprint()


# ---------------------------------------------------------------------------
# the provider protocol
# ---------------------------------------------------------------------------


def test_proposing_requires_a_subject_and_a_record():
    provider = callable_provider()
    with pytest.raises(OwnershipRecommendationError):
        provider.propose("S-1", record("S-1"))
    with pytest.raises(OwnershipRecommendationError):
        provider.propose(subject("S-1"), {"subject_id": "S-1"})


def test_nothing_is_proposed_for_a_subject_that_already_has_a_declared_owner():
    """The first step toward a recommendation displacing a determination, refused here."""
    provider = callable_provider(recommendation())
    assert provider.propose(subject("S-1"), declared_record("S-1", "OWNER-A")) == ()


def test_a_provider_that_raises_is_contained_as_a_typed_refusal():
    def _explodes(subject, record):
        raise RuntimeError("provider exploded")

    provider = CallableRecommendationProvider(descriptor(), _explodes)
    with pytest.raises(OwnershipRecommendationError) as exc:
        provider.propose(subject("S-1"), record("S-1"))
    message = str(exc.value)
    assert "provider failed" in message
    assert "provider exploded" in message


def test_a_typed_refusal_from_a_provider_passes_through_unwrapped():
    original = OwnershipRecommendationError("already typed")

    def _refuses(subject, record):
        raise original

    provider = CallableRecommendationProvider(descriptor(), _refuses)
    with pytest.raises(OwnershipRecommendationError) as exc:
        provider.propose(subject("S-1"), record("S-1"))
    assert exc.value is original


def test_a_provider_producing_something_that_is_not_a_recommendation_is_refused():
    provider = callable_provider({"subject_id": "S-1"})
    with pytest.raises(OwnershipRecommendationError) as exc:
        provider.propose(subject("S-1"), record("S-1"))
    assert "non-recommendation value" in str(exc.value)


def test_a_proposal_attributed_to_another_provider_is_refused():
    """Provenance that does not match its provider would make the basis untraceable."""
    provider = callable_provider(recommendation(provider_id="recommendation.somebody-else"))
    with pytest.raises(OwnershipRecommendationError) as exc:
        provider.propose(subject("S-1"), record("S-1"))
    assert "provenance does not match" in str(exc.value)


def test_a_proposal_about_a_different_subject_is_refused():
    provider = callable_provider(recommendation(subject_id="S-OTHER"))
    with pytest.raises(OwnershipRecommendationError) as exc:
        provider.propose(subject("S-1"), record("S-1"))
    assert "subject does not match" in str(exc.value)


def test_proposals_are_deduplicated_and_returned_in_deterministic_order():
    weak = recommendation(locator="z.py", precedence=100)
    strong = recommendation(locator="a.py", precedence=900)
    provider = callable_provider(weak, strong, weak)
    assert provider.propose(subject("S-1"), record("S-1")) == (strong, weak)


def test_a_callable_provider_requires_a_descriptor_and_a_callable():
    with pytest.raises(OwnershipRecommendationError):
        CallableRecommendationProvider({"provider_id": "x"}, lambda s, r: ())
    with pytest.raises(OwnershipRecommendationError) as exc:
        CallableRecommendationProvider(descriptor(), "not callable")
    assert "requires a callable" in str(exc.value)


def test_the_provider_base_declares_the_extension_point_abstractly():
    assert OwnershipRecommendationProvider.__abstractmethods__ == frozenset(
        {"descriptor", "recommend"}
    )


# ---------------------------------------------------------------------------
# EligibleLocatorRecommendationProvider
# ---------------------------------------------------------------------------


def test_the_eligible_locator_provider_accepts_a_policy_or_a_composed_home(policy):
    from_policy = EligibleLocatorRecommendationProvider(policy)
    from_home = EligibleLocatorRecommendationProvider(CanonicalHomePolicy(policy))
    assert isinstance(from_policy.home, CanonicalHomePolicy)
    assert from_home.home.policy is policy
    assert from_policy.descriptor().basis == BASIS_ELIGIBLE_LOCATOR


def test_the_eligible_locator_provider_refuses_anything_that_is_not_a_policy():
    with pytest.raises(OwnershipRecommendationError) as exc:
        EligibleLocatorRecommendationProvider({"zones": []})
    assert "TruthPolicy or CanonicalHomePolicy" in str(exc.value)


def test_a_subject_in_a_declared_home_zone_gets_the_zone_authority_proposed(
    policy, eligible_locator
):
    provider = EligibleLocatorRecommendationProvider(policy)
    proposals = provider.propose(subject("S-1", eligible_locator), record("S-1"))
    assert len(proposals) == 1
    proposal = proposals[0]
    assert proposal.basis == BASIS_ELIGIBLE_LOCATOR
    assert proposal.locator == eligible_locator
    assert proposal.proposed_owner
    assert "could own it once an authority says so" in proposal.detail
    # The proposal is strengthened by the zone's own declared precedence.
    assert proposal.precedence > provider.descriptor().precedence


def test_a_subject_in_no_declared_home_zone_gets_no_proposal(policy):
    """Proposing a locator the eligibility rules would refuse would waste a governance act."""
    provider = EligibleLocatorRecommendationProvider(policy)
    assert provider.propose(subject("S-1", "no/such/zone/file.txt"), record("S-1")) == ()


def test_a_subject_with_no_locator_at_all_gets_no_proposal(policy):
    provider = EligibleLocatorRecommendationProvider(policy)
    assert provider.propose(subject("S-1"), record("S-1")) == ()


def test_the_single_strongest_eligible_locator_wins(policy):
    """One proposal, deterministically chosen — not one per eligible locator."""
    home = CanonicalHomePolicy(policy)
    weaker, stronger = "platform/universal_ownership/contracts.py", "adr/some-decision.md"
    if not (home.admits(weaker) and home.admits(stronger)):
        pytest.skip("the declared Truth policy admits neither probe locator")
    assert home.policy.classify(stronger).precedence > home.policy.classify(weaker).precedence

    provider = EligibleLocatorRecommendationProvider(policy)
    proposals = provider.propose(
        subject("S-1", "zzz/not/a/zone.txt", weaker, stronger), record("S-1")
    )
    assert len(proposals) == 1
    assert proposals[0].locator == stronger


def test_locators_of_equal_precedence_break_the_tie_deterministically(policy):
    """Equal zones must not let locator enumeration order decide who is proposed."""
    home = CanonicalHomePolicy(policy)
    first, second = "engine/knowledge/model.py", "platform/universal_ownership/contracts.py"
    if not (home.admits(first) and home.admits(second)):
        pytest.skip("the declared Truth policy admits neither probe locator")
    assert home.policy.classify(first).precedence == home.policy.classify(second).precedence

    provider = EligibleLocatorRecommendationProvider(policy)
    forward = provider.propose(subject("S-1", first, second), record("S-1"))
    backward = provider.propose(subject("S-1", second, first), record("S-1"))
    assert forward == backward
    assert forward[0].locator == min(first, second)


# ---------------------------------------------------------------------------
# PeerPrecedentRecommendationProvider
# ---------------------------------------------------------------------------


def test_the_peer_precedent_provider_requires_a_mapping_and_an_attribute():
    with pytest.raises(OwnershipRecommendationError) as exc:
        PeerPrecedentRecommendationProvider([("a", "b")], attribute="family")
    assert "requires a mapping" in str(exc.value)
    with pytest.raises(OwnershipRecommendationError) as exc:
        PeerPrecedentRecommendationProvider({}, attribute="  ")
    assert "attribute it groups by" in str(exc.value)


def test_a_subject_sharing_an_attribute_value_with_declared_peers_inherits_the_precedent():
    provider = PeerPrecedentRecommendationProvider({"ENGINE": "OWNER-A"}, attribute="family")
    proposals = provider.propose(subject("S-1", family="ENGINE"), record("S-1"))
    assert len(proposals) == 1
    assert proposals[0].proposed_owner == "OWNER-A"
    assert proposals[0].basis == BASIS_PEER_PRECEDENT
    assert "family=ENGINE" in proposals[0].detail
    assert provider.attribute == "family"
    assert provider.count == 1


def test_a_subject_whose_attribute_carries_no_precedent_gets_no_proposal():
    provider = PeerPrecedentRecommendationProvider({"ENGINE": "OWNER-A"}, attribute="family")
    assert provider.propose(subject("S-1", family="PLATFORM"), record("S-1")) == ()


def test_a_subject_that_does_not_declare_the_attribute_gets_no_proposal():
    provider = PeerPrecedentRecommendationProvider({"ENGINE": "OWNER-A"}, attribute="family")
    assert provider.propose(subject("S-1"), record("S-1")) == ()


def test_precedent_is_derived_from_declared_ownership_alone():
    """A recommendation never becomes the basis of another recommendation."""
    subjects = [
        subject("S-1", family="ENGINE"),
        subject("S-2", family="ENGINE"),
        subject("S-3", family="ENGINE"),
    ]
    determination = OwnershipDetermination.create(
        [
            declared_record("S-1", "OWNER-A"),
            declared_record("S-2", "OWNER-A"),
            record("S-3"),  # open: contributes nothing to the precedent
        ]
    )
    provider = PeerPrecedentRecommendationProvider.from_determination(
        determination, subjects, attribute="family"
    )
    assert provider.count == 1
    assert provider.propose(subjects[2], record("S-3"))[0].proposed_owner == "OWNER-A"


def test_precedent_requires_the_declared_determination_it_is_read_from():
    with pytest.raises(OwnershipRecommendationError) as exc:
        PeerPrecedentRecommendationProvider.from_determination(
            {"records": []}, [], attribute="family"
        )
    assert "OwnershipDetermination" in str(exc.value)


def test_a_contested_majority_yields_no_precedent():
    """A tie is not a precedent, and inventing one here is the inference the framework refuses."""
    subjects = [subject("S-1", family="ENGINE"), subject("S-2", family="ENGINE")]
    determination = OwnershipDetermination.create(
        [declared_record("S-1", "OWNER-A"), declared_record("S-2", "OWNER-B")]
    )
    provider = PeerPrecedentRecommendationProvider.from_determination(
        determination, subjects, attribute="family"
    )
    assert provider.count == 0


def test_a_thin_majority_yields_no_precedent():
    subjects = [subject("S-1", family="ENGINE")]
    determination = OwnershipDetermination.create([declared_record("S-1", "OWNER-A")])
    provider = PeerPrecedentRecommendationProvider.from_determination(
        determination, subjects, attribute="family", minimum_peers=2
    )
    assert provider.count == 0


def test_a_subject_missing_the_attribute_or_an_owner_contributes_no_precedent():
    subjects = [
        subject("S-1", family="ENGINE"),
        subject("S-2"),  # declares no family
        subject("S-3", family="ENGINE"),
        subject("S-4", family="ENGINE"),
    ]
    determination = OwnershipDetermination.create(
        [
            declared_record("S-1", "OWNER-A"),
            declared_record("S-2", "OWNER-B"),
            declared_record("S-3", "OWNER-A"),
            record("S-4"),  # open, so no owner to tally
        ]
    )
    provider = PeerPrecedentRecommendationProvider.from_determination(
        determination, subjects, attribute="family"
    )
    assert provider.count == 1
    assert provider.propose(subjects[3], record("S-4"))[0].proposed_owner == "OWNER-A"


# ---------------------------------------------------------------------------
# RecommendationProviderRegistry
# ---------------------------------------------------------------------------


def test_only_a_recommendation_provider_may_be_registered():
    with pytest.raises(OwnershipRecommendationError) as exc:
        RecommendationProviderRegistry().add(lambda s, r: ())
    assert "only OwnershipRecommendationProvider" in str(exc.value)


def test_registering_the_same_provider_object_twice_is_idempotent():
    provider = callable_provider()
    registry = RecommendationProviderRegistry([provider])
    assert registry.add(provider) is provider
    assert registry.count == 1


def test_a_second_provider_claiming_a_registered_identity_is_refused():
    registry = RecommendationProviderRegistry([callable_provider(provider_id="recommendation.x")])
    with pytest.raises(OwnershipRecommendationError) as exc:
        registry.add(callable_provider(provider_id="recommendation.x"))
    assert "identity already registered" in str(exc.value)


def test_providers_resolve_in_declared_precedence_order_never_insertion_order():
    weak = callable_provider(provider_id="recommendation.weak", precedence=100)
    strong = callable_provider(provider_id="recommendation.strong", precedence=900)
    registry = RecommendationProviderRegistry()
    returned = registry.extend([weak, strong])
    assert returned == (strong, weak)
    assert [item.provider_id for item in registry.descriptors()] == [
        "recommendation.strong",
        "recommendation.weak",
    ]


def test_get_reports_an_unregistered_provider_as_absent():
    assert RecommendationProviderRegistry().get("recommendation.nobody") is None


def test_require_returns_a_registered_provider():
    provider = callable_provider(provider_id="recommendation.x")
    assert RecommendationProviderRegistry([provider]).require("recommendation.x") is provider


def test_require_refuses_an_unregistered_provider():
    with pytest.raises(OwnershipRecommendationError) as exc:
        RecommendationProviderRegistry().require("recommendation.nobody")
    assert "unknown recommendation provider" in str(exc.value)


def test_the_registry_gathers_every_provider_proposal_deterministically():
    weak = callable_provider(
        recommendation(provider_id="recommendation.weak", precedence=100, locator="z.py"),
        provider_id="recommendation.weak",
        precedence=100,
    )
    strong = callable_provider(
        recommendation(provider_id="recommendation.strong", precedence=900, locator="a.py"),
        provider_id="recommendation.strong",
        precedence=900,
    )
    registry = RecommendationProviderRegistry([weak, strong])
    proposals = registry.propose(subject("S-1"), record("S-1"))
    assert [item.provider_id for item in proposals] == [
        "recommendation.strong",
        "recommendation.weak",
    ]


def test_the_registry_projection_and_fingerprint_are_deterministic():
    forward = RecommendationProviderRegistry(
        [
            callable_provider(provider_id="recommendation.a"),
            callable_provider(provider_id="recommendation.b"),
        ]
    )
    backward = RecommendationProviderRegistry(
        [
            callable_provider(provider_id="recommendation.b"),
            callable_provider(provider_id="recommendation.a"),
        ]
    )
    assert forward.to_dict() == backward.to_dict()
    assert forward.to_dict()["provider_count"] == 2
    assert forward.fingerprint() == backward.fingerprint()


# ---------------------------------------------------------------------------
# GovernanceWorkload
# ---------------------------------------------------------------------------


def declared_record(subject_id: str, owner: str) -> OwnershipRecord:
    """A record standing DECLARED — the only standing the precedent is allowed to read."""
    evidence = OwnershipEvidence.create(
        subject_id,
        owner,
        EvidenceKind.DECLARED_ASSIGNMENT,
        locator=f"catalog/{subject_id}.json",
        provider_id="test.declared",
        authority=owner,
    )
    declaration = OwnershipDeclaration.create(
        subject_id,
        owner,
        authority=owner,
        kind=EvidenceKind.DECLARED_ASSIGNMENT,
        locator=evidence.locator,
        evidence_ids=(evidence.evidence_id,),
    )
    return OwnershipRecord.create(subject_id, OwnershipStanding.DECLARED, declaration=declaration)


def test_a_workload_requires_the_determination_it_measures():
    with pytest.raises(OwnershipRecommendationError) as exc:
        GovernanceWorkload.create({"records": []}, [])
    assert "OwnershipDetermination" in str(exc.value)


def test_an_open_subject_with_a_proposal_is_ratifiable():
    determination = OwnershipDetermination.create([record("S-1")])
    workload = GovernanceWorkload.create(determination, [recommendation("S-1")])
    assert workload.ratifiable == ("S-1",)
    assert workload.irreducible == ()
    assert workload.reduction == 100.0
    assert workload.open_total == 1


def test_an_open_subject_with_no_proposal_and_no_deficit_is_irreducible():
    """The theoretical minimum an authority must decide from first principles."""
    determination = OwnershipDetermination.create([record("S-1")])
    workload = GovernanceWorkload.create(determination, [])
    assert workload.irreducible == ("S-1",)
    assert workload.governance_minimum == ("S-1",)
    assert workload.reduction == 0.0
    assert workload.determinable == 0.0


def test_a_mechanical_omission_is_remediable_and_never_billed_as_ambiguity():
    """A subject whose artifact was simply unregistered needs registration, not a decision."""
    determination = OwnershipDetermination.create(
        [record("S-1", refusals=(("a/b.py", "SUBJECT-NOT-REGISTERED", "test.provider"),))]
    )
    workload = GovernanceWorkload.create(determination, [])
    assert workload.remediable == ("S-1",)
    assert workload.irreducible == ("S-1",)
    assert workload.governance_minimum == ()  # the residue, correctly, is empty
    assert workload.determinable == 100.0
    assert workload.by_deficit() == {"SUBJECT-NOT-REGISTERED": 1}


def test_a_determination_that_left_nothing_open_is_fully_reduced():
    determination = OwnershipDetermination.create([declared_record("S-1", "OWNER-A")])
    workload = GovernanceWorkload.create(determination, [])
    assert workload.open_total == 0
    assert workload.reduction == 100.0
    assert workload.determinable == 100.0
    assert workload.declared == 1


def test_deficits_are_tallied_most_frequent_first():
    determination = OwnershipDetermination.create(
        [
            record("S-1", refusals=(("a.py", "DEFICIT-COMMON", "p"),)),
            record("S-2", refusals=(("b.py", "DEFICIT-COMMON", "p"),)),
            record("S-3", refusals=(("c.py", "DEFICIT-RARE", "p"),)),
        ]
    )
    workload = GovernanceWorkload.create(determination, [])
    assert list(workload.by_deficit()) == ["DEFICIT-COMMON", "DEFICIT-RARE"]
    assert workload.by_deficit()["DEFICIT-COMMON"] == 2


def test_every_proposal_for_a_subject_is_retrievable_strongest_first():
    determination = OwnershipDetermination.create([record("S-1"), record("S-2")])
    weak = recommendation("S-1", locator="z.py", precedence=100)
    strong = recommendation("S-1", locator="a.py", precedence=900)
    other = recommendation("S-2")
    workload = GovernanceWorkload.create(determination, [weak, strong, other])
    assert workload.for_subject("S-1") == (strong, weak)
    assert workload.for_subject("S-NOBODY") == ()


def test_the_strongest_proposal_per_subject_is_the_one_that_would_be_ratified():
    determination = OwnershipDetermination.create([record("S-1")])
    weak = recommendation("S-1", proposed_owner="OWNER-WEAK", locator="z.py", precedence=100)
    strong = recommendation("S-1", proposed_owner="OWNER-STRONG", locator="a.py", precedence=900)
    workload = GovernanceWorkload.create(determination, [weak, strong])
    assert workload.strongest() == {"S-1": strong}
    assert workload.by_proposed_owner() == {"OWNER-STRONG": 1}


def test_proposals_are_tallied_by_the_basis_that_produced_them():
    determination = OwnershipDetermination.create([record("S-1"), record("S-2")])
    workload = GovernanceWorkload.create(
        determination,
        [
            recommendation("S-1", basis=BASIS_ELIGIBLE_LOCATOR),
            recommendation("S-2", basis=BASIS_PEER_PRECEDENT),
        ],
    )
    tally = workload.by_basis()
    assert tally[BASIS_ELIGIBLE_LOCATOR] == 1
    assert tally[BASIS_PEER_PRECEDENT] == 1


def test_a_basis_outside_the_declared_vocabulary_is_still_tallied():
    """An unknown basis is counted, never dropped: a silent zero would hide a whole provider."""
    determination = OwnershipDetermination.create([record("S-1")])
    workload = GovernanceWorkload.create(
        determination, [recommendation("S-1", basis="recommendation.future-basis")]
    )
    assert workload.by_basis()["recommendation.future-basis"] == 1


def test_owners_are_tallied_by_how_much_they_would_take_descending():
    determination = OwnershipDetermination.create([record("S-1"), record("S-2"), record("S-3")])
    workload = GovernanceWorkload.create(
        determination,
        [
            recommendation("S-1", proposed_owner="OWNER-A"),
            recommendation("S-2", proposed_owner="OWNER-A"),
            recommendation("S-3", proposed_owner="OWNER-B"),
        ],
    )
    assert list(workload.by_proposed_owner()) == ["OWNER-A", "OWNER-B"]


def test_the_draft_catalogue_is_emitted_as_a_draft_and_never_as_evidence():
    determination = OwnershipDetermination.create([record("S-1"), record("S-2")])
    workload = GovernanceWorkload.create(determination, [recommendation("S-1")])
    document = workload.as_declaration_document(authority="GOVERNING-BODY")
    assert document["ratified"] is False
    assert "NOT BINDING" in document["$comment"]
    assert document["authority"] == "GOVERNING-BODY"
    assert set(document["assignments"]) == {"S-1"}
    assert document["irreducible"] == ["S-2"]
    assert document["governance_minimum"] == ["S-2"]


def test_the_counts_reconcile_with_the_populations_they_describe():
    determination = OwnershipDetermination.create(
        [
            declared_record("S-0", "OWNER-A"),
            record("S-1"),
            record("S-2", refusals=(("b.py", "DEFICIT", "p"),)),
        ]
    )
    workload = GovernanceWorkload.create(determination, [recommendation("S-1")])
    counts = workload.counts()
    assert counts["subjects"] == 3
    assert counts["declared"] == 1
    assert counts["open"] == 2
    assert counts["ratifiable"] + counts["irreducible"] == counts["open"]
    assert counts["governance_minimum"] <= counts["irreducible"]
    assert counts["recommendations"] == 1


def test_the_full_projection_carries_the_proposals_the_summary_drops():
    determination = OwnershipDetermination.create([record("S-1")])
    workload = GovernanceWorkload.create(determination, [recommendation("S-1")])
    full = workload.to_dict()
    compact = workload.summary()
    assert full["recommendations"]
    assert "recommendations" not in compact
    assert full["workload_id"] == compact["workload_id"]
    assert full["counts"] == compact["counts"]
    assert full["deficits"] == []


def test_a_workload_fingerprints_over_the_facts_it_asserts():
    determination = OwnershipDetermination.create([record("S-1")])
    first = GovernanceWorkload.create(determination, [recommendation("S-1")])
    second = GovernanceWorkload.create(determination, [recommendation("S-1")])
    assert first.fingerprint() == second.fingerprint()
    assert first.workload_id == second.workload_id
    assert first.workload_id.startswith("UCOS-UOFW-")


# ---------------------------------------------------------------------------
# GovernanceReductionEngine
# ---------------------------------------------------------------------------


def test_the_engine_requires_a_provider_registry():
    with pytest.raises(OwnershipRecommendationError) as exc:
        GovernanceReductionEngine([callable_provider()])
    assert "RecommendationProviderRegistry" in str(exc.value)


def test_the_engine_proposes_only_for_the_residue_the_determination_left_open():
    registry = RecommendationProviderRegistry([callable_provider(recommendation("S-1"))])
    engine = GovernanceReductionEngine(registry)
    determination = OwnershipDetermination.create(
        [declared_record("S-0", "OWNER-A"), record("S-1")]
    )
    workload = engine.reduce(determination, [subject("S-0"), subject("S-1")])
    assert workload.ratifiable == ("S-1",)
    assert {item.subject_id for item in workload.recommendations} == {"S-1"}
    assert engine.providers is registry


def test_a_subject_absent_from_the_population_yields_no_proposal_rather_than_a_guess():
    """The workload can never be understated by a missing input."""
    registry = RecommendationProviderRegistry([callable_provider(recommendation("S-1"))])
    determination = OwnershipDetermination.create([record("S-1")])
    workload = GovernanceReductionEngine(registry).reduce(determination, [])
    assert workload.ratifiable == ()
    assert workload.irreducible == ("S-1",)


def test_the_engine_composition_projects_and_fingerprints_deterministically():
    registry = RecommendationProviderRegistry([callable_provider()])
    engine = GovernanceReductionEngine(registry)
    assert engine.to_dict() == {"providers": registry.to_dict()}
    assert engine.fingerprint() == GovernanceReductionEngine(registry).fingerprint()


# ---------------------------------------------------------------------------
# the shipped composition
# ---------------------------------------------------------------------------


def test_the_shipped_provider_set_always_carries_the_eligible_locator_proposer(policy):
    providers = default_recommendation_providers(policy)
    assert len(providers) == 1
    assert isinstance(providers[0], EligibleLocatorRecommendationProvider)


def test_peer_precedent_joins_the_shipped_set_only_when_it_is_derivable(policy):
    determination = OwnershipDetermination.create(
        [declared_record("S-1", "OWNER-A"), declared_record("S-2", "OWNER-A")]
    )
    subjects = [subject("S-1", family="ENGINE"), subject("S-2", family="ENGINE")]
    with_attribute = default_recommendation_providers(
        policy, determination=determination, subjects=subjects, attribute="family"
    )
    without_attribute = default_recommendation_providers(
        policy, determination=determination, subjects=subjects
    )
    assert len(with_attribute) == 2
    assert isinstance(with_attribute[1], PeerPrecedentRecommendationProvider)
    assert len(without_attribute) == 1


def test_the_default_composition_reduces_a_real_determination(policy, eligible_locator):
    engine = build_governance_reduction(policy)
    determination = OwnershipDetermination.create([record("S-1")])
    workload = engine.reduce(determination, [subject("S-1", eligible_locator)])
    assert workload.ratifiable == ("S-1",)
    assert workload.strongest()["S-1"].basis == BASIS_ELIGIBLE_LOCATOR
    assert workload.reduction == 100.0


def test_the_default_composition_carries_the_peer_precedent_when_asked(policy):
    determination = OwnershipDetermination.create(
        [
            declared_record("S-1", "OWNER-A"),
            declared_record("S-2", "OWNER-A"),
            record("S-3"),
        ]
    )
    subjects = [
        subject("S-1", family="ENGINE"),
        subject("S-2", family="ENGINE"),
        subject("S-3", family="ENGINE"),
    ]
    engine = build_governance_reduction(
        policy, determination=determination, subjects=subjects, attribute="family"
    )
    workload = engine.reduce(determination, subjects)
    assert workload.ratifiable == ("S-3",)
    assert workload.strongest()["S-3"].basis == BASIS_PEER_PRECEDENT


def test_the_declared_basis_vocabulary_is_what_the_shipped_providers_use():
    assert DEFAULT_PRECEDENCE > 0
    assert BASIS_ELIGIBLE_LOCATOR != BASIS_PEER_PRECEDENT
