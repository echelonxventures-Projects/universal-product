"""Ω∞ authority resolution — seven tiers, and a resolution that cannot terminate with nothing.

THE PROPERTY THAT MATTERS IS TOTALITY, and it is easy to get almost right. A resolver that returns
``None`` for an unclaimed artifact hands every caller the same decision to make separately, and they
will not make it the same way: one treats it as unowned, one as owned by the caller, one crashes.
``AuthorityResolver`` therefore always returns a chain — but a fallback that quietly succeeded would
be worse than a null, because "nobody owns this" would become indistinguishable from "the universal
authority owns this". The fallback is consequently RECORDED as an event and COUNTED as a density, so
an unowned population stays visible and can be driven down.

CONTESTED IS SURFACED, NEVER RESOLVED. Two sources at one tier claiming different authorities is a
real disagreement between two humans, and picking one by sort order would settle a governance
dispute by alphabet.
"""

from __future__ import annotations

import pytest

from engine.omega_governance.authority import (
    ABSTAIN,
    ARTIFACT_AUTHORITY,
    DOMAIN_AUTHORITY,
    INITIAL_TIERS,
    OWNER_AUTHORITY,
    SYSTEM_AUTHORITY,
    UNIVERSAL_FALLBACK,
    UNIVERSAL_FALLBACK_AUTHORITY,
    AuthorityChain,
    AuthorityError,
    AuthorityResolver,
    AuthorityTier,
    MappingSource,
    assert_total,
    contested,
    fallback_count,
    fallback_density,
    tier_census,
    unattributed,
)
from engine.omega_governance.temporal.clocks import LogicalClock


def _resolver(*sources: MappingSource, clock: LogicalClock | None = None) -> AuthorityResolver:
    return (
        AuthorityResolver(sources=sources, clock=clock)
        if clock
        else AuthorityResolver(sources=sources)
    )


# ----------------------------------------------------------------------------------- tiers


def test_the_seven_shipped_tiers_are_ranked_and_exactly_one_is_the_fallback() -> None:
    assert len(INITIAL_TIERS) == 7
    ranks = [tier.rank for tier in INITIAL_TIERS]
    assert ranks == sorted(ranks), "the tiers are not in rank order, so resolution order is unclear"
    assert [tier.fallback for tier in INITIAL_TIERS].count(True) == 1
    assert UNIVERSAL_FALLBACK.fallback


def test_every_tier_carries_its_own_rule_id() -> None:
    """A chain cites the rule that produced it, so a reader can check the claim rather than trust
    the resolver's word for which tier answered."""
    for tier in INITIAL_TIERS:
        assert tier.rule.strip()
    assert len({tier.rule for tier in INITIAL_TIERS}) == len(INITIAL_TIERS)


def test_a_tier_must_be_named_and_carry_a_rule() -> None:
    with pytest.raises(AuthorityError):
        AuthorityTier(rank=1, name="   ", rule="R-1")
    with pytest.raises(AuthorityError):
        AuthorityTier(rank=1, name="A_TIER", rule="   ")


# --------------------------------------------------------------------------------- sources


def test_a_source_claims_what_it_holds_and_abstains_on_everything_else() -> None:
    source = MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-ONE"})
    assert source.claim("a") == "TEAM-ONE"
    assert source.claim("b") == ABSTAIN


def test_a_source_must_be_named() -> None:
    with pytest.raises(AuthorityError):
        MappingSource("   ", OWNER_AUTHORITY, {})


def test_registering_two_sources_under_one_identifier_is_refused() -> None:
    """A silent replacement would let a later registration delete an ownership claim, and the loss
    would look exactly like the claim never having existed."""
    resolver = AuthorityResolver()
    resolver.register(MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-ONE"}))
    with pytest.raises(AuthorityError):
        resolver.register(MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-TWO"}))


def test_sources_are_grouped_by_the_tier_they_declare() -> None:
    resolver = _resolver(
        MappingSource("owners", OWNER_AUTHORITY, {}),
        MappingSource("domains", DOMAIN_AUTHORITY, {}),
    )
    assert [s.identifier() for s in resolver.sources_at(OWNER_AUTHORITY)] == ["owners"]
    assert [s.identifier() for s in resolver.sources_at(DOMAIN_AUTHORITY)] == ["domains"]
    assert resolver.sources_at(SYSTEM_AUTHORITY) == ()


# ------------------------------------------------------------------------------ resolution


def test_a_claim_resolves_to_the_authority_and_names_the_tier_and_rule() -> None:
    chain = _resolver(MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-ONE"})).resolve("a")
    assert chain.authority == "TEAM-ONE"
    assert chain.tier == OWNER_AUTHORITY.name
    assert chain.rule == OWNER_AUTHORITY.rule
    assert not chain.fallback


def test_the_most_specific_tier_wins_over_a_broader_one() -> None:
    """Artifact-level ownership must beat a system-wide default, or a blanket claim would silence
    every specific one and nothing would report the override."""
    chain = _resolver(
        MappingSource("artifacts", ARTIFACT_AUTHORITY, {"a": "ARTIFACT-OWNER"}),
        MappingSource("systems", SYSTEM_AUTHORITY, {"a": "SYSTEM-OWNER"}),
    ).resolve("a")
    assert chain.authority == "ARTIFACT-OWNER"
    assert chain.tier == ARTIFACT_AUTHORITY.name


def test_a_broader_tier_answers_when_the_specific_one_abstains() -> None:
    chain = _resolver(
        MappingSource("artifacts", ARTIFACT_AUTHORITY, {"other": "ARTIFACT-OWNER"}),
        MappingSource("systems", SYSTEM_AUTHORITY, {"a": "SYSTEM-OWNER"}),
    ).resolve("a")
    assert chain.authority == "SYSTEM-OWNER"
    assert chain.tier == SYSTEM_AUTHORITY.name


def test_resolution_is_total_and_never_returns_nothing() -> None:
    """Every configuration, including one with no sources at all."""
    for resolver in (AuthorityResolver(), _resolver(MappingSource("owners", OWNER_AUTHORITY, {}))):
        chain = resolver.resolve("unclaimed")
        assert chain.authority == UNIVERSAL_FALLBACK_AUTHORITY
        assert chain.fallback


def test_reaching_the_fallback_is_recorded_as_an_event_rather_than_passing_quietly() -> None:
    """The difference between "nobody owns this" and "the universal authority owns this". Without
    the event the two readings are the same string and the unowned population is invisible."""
    resolver = _resolver(MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-ONE"}))
    resolver.resolve("a")
    resolver.resolve("b")
    resolver.resolve("c")

    events = resolver.fallback_events()
    assert [event.subject for event in events] == ["b", "c"]
    assert [event.sequence for event in events] == [0, 1]
    assert all(event.authority == UNIVERSAL_FALLBACK_AUTHORITY for event in events)


def test_a_fallback_event_records_which_tiers_were_consulted_and_which_had_sources() -> None:
    """Nobody claimed it and nobody was asked are different failures with different remedies."""
    resolver = _resolver(MappingSource("owners", OWNER_AUTHORITY, {}))
    resolver.resolve("a")
    event = resolver.fallback_events()[0]
    assert OWNER_AUTHORITY.name in event.tiers_with_sources
    assert ARTIFACT_AUTHORITY.name in event.tiers_consulted
    assert ARTIFACT_AUTHORITY.name not in event.tiers_with_sources


def test_a_fallback_event_can_be_stamped_with_a_coordinate_from_an_injected_clock() -> None:
    resolver = AuthorityResolver(sources=(), clock=LogicalClock("authority"))
    resolver.resolve("a")
    event = resolver.fallback_events()[0]
    assert event.coordinate is not None
    assert event.coordinate.clock == "authority"


def test_the_fallback_record_is_append_only() -> None:
    resolver = AuthorityResolver()
    resolver.resolve("a")
    first = resolver.fallback_events()
    resolver.resolve("b")
    assert resolver.fallback_events()[: len(first)] == first


def test_a_chain_explains_itself_in_words_a_reader_can_check_against_its_links() -> None:
    chain = _resolver(MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-ONE"})).resolve("a")
    explanation = chain.explanation()
    assert "TEAM-ONE" in explanation
    assert chain.as_record()["authority"] == "TEAM-ONE"


def test_a_chain_records_every_tier_it_consulted_including_the_ones_that_abstained() -> None:
    """A chain that only showed the winning tier would make an abstention indistinguishable from a
    tier nobody registered a source for."""
    chain = _resolver(MappingSource("systems", SYSTEM_AUTHORITY, {"a": "SYSTEM-OWNER"})).resolve(
        "a"
    )
    consulted = {link.tier for link in chain.links}
    assert ARTIFACT_AUTHORITY.name in consulted
    assert any(link.abstained for link in chain.links)


def test_a_chain_must_name_an_authority() -> None:
    with pytest.raises(AuthorityError):
        AuthorityChain(subject="a", authority="   ", tier="OWNER", rule="R-1")


# ------------------------------------------------------------------------------- contested


def test_two_different_claims_at_one_tier_are_surfaced_and_never_silently_picked() -> None:
    """A real disagreement between two humans. Resolving it by sort order would settle a governance
    dispute by alphabet and leave no trace that there had been one."""
    resolver = _resolver(
        MappingSource("owners-a", OWNER_AUTHORITY, {"a": "TEAM-ONE"}),
        MappingSource("owners-b", OWNER_AUTHORITY, {"a": "TEAM-TWO"}),
    )
    chain = resolver.resolve("a")
    assert chain.contested_tiers
    assert contested([chain]) == (("a", (OWNER_AUTHORITY.name,)),)


def test_two_sources_agreeing_at_one_tier_is_not_contested() -> None:
    resolver = _resolver(
        MappingSource("owners-a", OWNER_AUTHORITY, {"a": "TEAM-ONE"}),
        MappingSource("owners-b", OWNER_AUTHORITY, {"a": "TEAM-ONE"}),
    )
    chain = resolver.resolve("a")
    assert not chain.contested_tiers
    assert contested([chain]) == ()


def test_a_contested_resolution_still_produces_an_authority() -> None:
    """Surfacing a dispute must not make the system unable to answer at all — an artifact two teams
    are arguing about is still an artifact something has to govern today."""
    resolver = _resolver(
        MappingSource("owners-a", OWNER_AUTHORITY, {"a": "TEAM-ONE"}),
        MappingSource("owners-b", OWNER_AUTHORITY, {"a": "TEAM-TWO"}),
    )
    assert resolver.resolve("a").authority.strip()


# ------------------------------------------------------------------------------ population


def test_resolve_all_answers_for_every_subject_it_was_given() -> None:
    resolver = _resolver(MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-ONE"}))
    chains = resolver.resolve_all(["a", "b"])
    assert len(chains) == 2
    assert {chain.subject for chain in chains} == {"a", "b"}


def test_assert_total_passes_over_a_resolved_population() -> None:
    resolver = _resolver(MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-ONE"}))
    assert_total(resolver.resolve_all(["a", "b"]))


def test_assert_total_refuses_a_chain_that_resolved_to_nothing() -> None:
    """Non-vacuity. The totality claim is worth what this check's ability to fail is worth."""
    empty = AuthorityChain.__new__(AuthorityChain)
    object.__setattr__(empty, "subject", "a")
    object.__setattr__(empty, "authority", "")
    object.__setattr__(empty, "tier", "OWNER")
    object.__setattr__(empty, "rule", "R-1")
    object.__setattr__(empty, "links", ())
    object.__setattr__(empty, "fallback", False)
    with pytest.raises(AuthorityError):
        assert_total([empty])


def test_the_unattributed_population_is_named_so_it_can_be_driven_to_zero() -> None:
    resolver = _resolver(MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-ONE"}))
    chains = resolver.resolve_all(["a", "b", "c"])
    assert unattributed(chains) == ("b", "c")
    assert fallback_count(chains) == 2


def test_fallback_density_is_scale_free_so_growth_cannot_flatter_it() -> None:
    """Two of four and two hundred of four hundred are the same governance failure, and a raw count
    would report the second as a hundred times worse while the ratio holds steady."""
    resolver = _resolver(MappingSource("owners", OWNER_AUTHORITY, {"a": "X", "b": "X"}))
    small = resolver.resolve_all(["a", "b", "c", "d"])
    assert fallback_density(small) == 0.5

    wide_source = MappingSource("owners", OWNER_AUTHORITY, {f"a{n}": "X" for n in range(200)})
    wide = _resolver(wide_source).resolve_all(
        [f"a{n}" for n in range(200)] + [f"z{n}" for n in range(200)]
    )
    assert fallback_density(wide) == 0.5


def test_fallback_density_over_an_empty_population_is_a_fault_and_not_a_comfortable_zero() -> None:
    """Ω-4's own argument, applied here: 0.0 over no artifacts would report perfect attribution for
    a measurement that resolved nothing, converting "this population is ungoverned" into "this
    population is fully governed" — the most dangerous defect a density metric can have."""
    with pytest.raises(AuthorityError):
        fallback_density([])


def test_the_tier_census_reports_every_tier_including_the_ones_that_resolved_nothing() -> None:
    resolver = _resolver(MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-ONE"}))
    counted = tier_census(resolver.resolve_all(["a", "b"]))
    assert set(counted) == {tier.name for tier in INITIAL_TIERS}
    assert counted[OWNER_AUTHORITY.name] == 1
    assert counted[DOMAIN_AUTHORITY.name] == 0


def test_the_resolver_report_describes_what_it_holds() -> None:
    resolver = _resolver(MappingSource("owners", OWNER_AUTHORITY, {"a": "TEAM-ONE"}))
    resolver.resolve("unclaimed")
    report = resolver.report()
    assert isinstance(report, dict)
    assert len(resolver) == 1


# ------------------------------------------------ the refusals a well-formed hierarchy never needs


def test_a_tier_ranked_below_one_is_refused() -> None:
    """Ranks start at 1 so 0 stays available as "no tier resolved", which must never be a legal
    outcome — a rank of zero would make the absent answer indistinguishable from the first one."""
    with pytest.raises(AuthorityError, match="ranks start at 1"):
        AuthorityTier(name="ZERO", rank=0, rule="TEST-R-00")


def test_a_tier_renders_as_its_name() -> None:
    """The tier appears inside a chain's own explanation, so it has to read as the name a
    reviewer knows rather than as a dataclass repr."""
    assert str(ARTIFACT_AUTHORITY) == ARTIFACT_AUTHORITY.name


def test_a_chain_must_name_the_subject_it_resolves_and_the_rule_it_cites() -> None:
    """An attribution that names no subject cannot be joined to the artifact it is about, and one
    citing no rule cannot be checked against the hierarchy that produced it."""
    with pytest.raises(AuthorityError, match="must name the subject"):
        AuthorityChain(subject="  ", authority="somebody", tier="ARTIFACT", rule="R")
    with pytest.raises(AuthorityError, match="cites no rule"):
        AuthorityChain(subject="a/path", authority="somebody", tier="ARTIFACT", rule="  ")


def test_a_chain_no_registered_tier_abstained_on_carries_no_abstention_clause() -> None:
    """The explanation is assembled from what happened. A chain with an abstaining tier names it;
    one with none must not carry the sentence with an empty list after it."""
    # With no source registered anywhere, the only consulted tier is the fallback — and it
    # answered rather than abstaining, so there is nothing to list.
    assert "abstaining tiers:" not in _resolver().resolve("a/path").explanation()
    wider = _resolver(
        MappingSource("specific", ARTIFACT_AUTHORITY, {"other/path": "somebody"}),
        MappingSource("broad", DOMAIN_AUTHORITY, {"a/path": "somebody-else"}),
    )
    assert "abstaining tiers:" in wider.resolve("a/path").explanation()


def test_a_contested_chain_names_the_tiers_that_disagreed() -> None:
    """Picking one of two claims by sort order would settle a governance dispute by alphabet, so
    the disagreement travels in the explanation rather than being resolved out of it."""
    resolver = _resolver(
        MappingSource("one", ARTIFACT_AUTHORITY, {"a/path": "somebody"}),
        MappingSource("two", ARTIFACT_AUTHORITY, {"a/path": "somebody-else"}),
    )
    chain = resolver.resolve("a/path")
    assert chain.contested_tiers
    assert "CONTESTED at" in chain.explanation()


def test_a_fallback_event_records_its_coordinate_only_when_a_clock_supplied_one() -> None:
    """A record that always carried the key would make "no clock was injected" indistinguishable
    from "the clock answered nothing", and this package keeps Time unprivileged precisely so a
    deployment with no clock stays expressible."""
    unstamped = _resolver()
    assert unstamped.resolve("unclaimed/path").authority == UNIVERSAL_FALLBACK_AUTHORITY
    assert "coordinate" not in unstamped.fallback_events()[-1].as_record()
    stamped = _resolver(clock=LogicalClock("test"))
    stamped.resolve("unclaimed/path")
    record = stamped.fallback_events()[-1].as_record()
    assert record["coordinate"]
    assert record["subject"] == "unclaimed/path"
    assert record["authority"] == UNIVERSAL_FALLBACK_AUTHORITY


def test_a_resolver_with_no_fallback_authority_or_no_fallback_tier_is_refused() -> None:
    """Both are the same defect at two levels: a hierarchy whose last rung is conditional can
    reach the end with no answer, which is the one path Ω-2.2 forbids."""
    with pytest.raises(AuthorityError, match="terminate with NONE"):
        AuthorityResolver(fallback_authority="   ")
    with pytest.raises(AuthorityError, match="declares no fallback tier"):
        AuthorityResolver(tiers=(ARTIFACT_AUTHORITY,))


def test_a_source_registering_at_the_fallback_tier_is_refused() -> None:
    """The fallback tier is constructed by the resolver and admits no source: a registerable
    fallback is a removable fallback."""
    with pytest.raises(AuthorityError, match="registerable fallback is a removable fallback"):
        _resolver(MappingSource("last", UNIVERSAL_FALLBACK, {"a/path": "somebody"}))


def test_resolving_an_unnamed_subject_is_refused() -> None:
    with pytest.raises(AuthorityError, match="unnamed subject"):
        _resolver().resolve("   ")


def test_a_source_that_identifies_itself_as_nothing_cannot_enter_a_chain() -> None:
    """MappingSource refuses this at construction, so the resolver's own guard has never run. It
    is the one that protects a source arriving from somewhere the constructor did not build — and
    an unidentifiable source is one no chain could cite as the reason for its attribution."""

    class _Anonymous:
        def identifier(self) -> str:
            return "   "

        def tier(self) -> AuthorityTier:
            return ARTIFACT_AUTHORITY

        def claim(self, subject: str) -> str:
            return ABSTAIN

    with pytest.raises(AuthorityError, match="must identify itself"):
        _resolver().register(_Anonymous())
