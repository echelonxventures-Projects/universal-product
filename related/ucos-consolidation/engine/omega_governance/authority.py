"""UCOS Ω∞ Phase 2, Deliverable Ω-2.2 — authority resolution that cannot terminate with NONE.

AUTHORITY = NONE (DERIVED TRUTH). This module resolves authority over artifacts and holds none
itself. Saying so is not a formality: a resolver that claimed authority would be a source in its own
chain.

THE DEFECT THIS CLOSES, and it is a single legal value::

    authority: str    # Ω-2: the authority that owns it. "" only when disposition is TRANSIENT

ONE ARTIFACT CLASS MAY HAVE NO OWNER. Defensible inside Ω-1 — a file declared not to persist cannot
acquire a durable owner — but it makes ``authority`` a field a reader must test before using, and
every such field eventually gets used untested. Worse, it makes "every artifact has an authority
chain" FALSE in the current system, so no invariant can assert it, so nothing measures the
population where it fails.

Phase 2 closes the hole rather than widening the exception: a transient artifact resolves to the
universal fallback like anything else nothing claims, and "nothing claimed it" becomes a MEASURED
EVENT instead of an empty string.

SEVEN TIERS, IN RESOLUTION ORDER.

    Ω²-A-01  ARTIFACT     the artifact declares its own authority
    Ω²-A-02  OWNER        a named owner claims it directly
    Ω²-A-03  DOMAIN       the capability domain it belongs to claims it
    Ω²-A-04  SYSTEM       the system that operates it claims it
    Ω²-A-05  PROGRAM      the governance programme it was produced under claims it
    Ω²-A-06  FEDERATION   a federation the programme participates in claims it
    Ω²-A-07  FALLBACK     unconditional. UNIVERSAL, and therefore never NONE.

ORDER IS LOAD-BEARING, on the same argument Ω-1 records: a self-declaration must beat an inherited
one, or an artifact could be moved into a directory and thereby reassigned to an owner who never
accepted it. Narrow claims resolve first because a narrow claim is about THIS artifact and a broad
one is about a set the artifact happens to be in.

THE CLOSED LIST THIS FILE'S FIRST DRAFT CONTAINED. Rule ids lived in ``RULES: dict[int, str]``,
keyed 1 to 7. An eighth tier — a caller's inter-organisational arbitration rung — would have raised
``KeyError`` inside ``resolve``, which is Ω∞ Rule 3 failing in the least visible possible place. THE
RULE ID NOW LIVES ON THE TIER, so declaring a tier declares its rule, one act instead of two that
can fall out of step, and there is no table to be missing a key.

WHY THE FALLBACK IS NOT A SOURCE. Tiers 1 to 6 are populated by injected ``AuthoritySource`` objects
— nothing here knows what a domain or a federation looks like, which is what lets a bucket, a
registry or a graph supply its own. The fallback is constructed by the resolver itself, from a
constant, with no registration step. There is therefore no configuration in which it is absent, and
``resolve`` over a resolver with ZERO SOURCES still returns an authority. That is the whole of
"resolution must never terminate with NONE" — an unremovable branch, not a validation somebody runs
afterwards.

REACHING THE FALLBACK IS NOT AN ERROR. IT IS AN EVENT. Record it, measure it, ratchet it:
``resolve`` flags the chain, the resolver accumulates a ``FallbackEvent`` per occurrence,
``fallback_density`` makes it scale-free, and ``adapters.ratchet_observations`` submits it as a
CONVERGENT Ω-4 metric — the same treatment Ω-1 gives its own ``authority_of_last_resort``, held at
zero.

A CONTESTED TIER IS SURFACED, NEVER SILENTLY BROKEN. Two sources at one tier claiming different
authorities is a real condition, and picking the alphabetically-first without saying so would make
ownership depend on a source's name. Resolution proceeds deterministically AND marks the link
``contested``, which is what ``contradiction.AuthorityContradictionDetector`` reads. Ω-1's
equivalent rule — unanimity among importers, otherwise fall through — loses the information; this
keeps it.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from engine.omega_governance.temporal.clocks import ClockProvider
from engine.omega_governance.temporal.coordinate import TemporalCoordinate


class AuthorityError(RuntimeError):
    """An authority tier, source or chain was invalid.

    RAISED, NEVER DEFAULTED — with a narrow remit. "Nothing claimed the artifact" is NOT an error
    and never raises. It is the fallback, and turning it into an exception would make the unclaimed
    population invisible in exactly the way an empty string already does.
    """


# ---------------------------------------------------------------------------------------- tiers


@dataclass(frozen=True, order=True)
class AuthorityTier:
    """One rung of the resolution hierarchy, carrying its own rule id.

    ``rank`` is FIRST so tiers sort by precedence rather than by name: resolution order is a
    property of the data, and an eighth tier takes its place by declaring a rank instead of by being
    appended to a list in the right position.

    ``rule`` LIVES HERE rather than in a rank-keyed table. The first draft kept it in
    ``dict[int, str]``, which meant a tier at rank 8 raised ``KeyError`` during resolution — Ω∞ Rule
    3 violated by a lookup nobody would think to challenge.
    """

    rank: int
    name: str
    rule: str
    description: str = ""
    #: True for the unconditional tier only. A PREDICATE rather than a name comparison, so a caller
    #: supplying its own fallback constant need not match a spelling.
    fallback: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise AuthorityError("an authority tier with no name cannot appear in a chain")
        if not self.rule.strip():
            raise AuthorityError(
                f"tier {self.name!r} declares no rule id; an attribution citing it could not be "
                "checked against the hierarchy that produced it"
            )
        if self.rank < 1:
            raise AuthorityError(
                f"tier {self.name!r} declares rank {self.rank}; ranks start at 1 so that 0 remains "
                "available as 'no tier resolved', which must never be a legal outcome"
            )

    def __str__(self) -> str:
        return self.name


ARTIFACT_AUTHORITY = AuthorityTier(
    1,
    "ARTIFACT",
    "Ω²-A-01",
    "The artifact declares its own authority. Resolves first because a self-declaration is the "
    "only "
    "claim that cannot be created by moving the artifact somewhere else.",
)
OWNER_AUTHORITY = AuthorityTier(
    2,
    "OWNER",
    "Ω²-A-02",
    "A named owner claims this specific artifact. A claim about the artifact, not about a set it "
    "belongs to.",
)
DOMAIN_AUTHORITY = AuthorityTier(
    3,
    "DOMAIN",
    "Ω²-A-03",
    "The capability domain the artifact belongs to claims it. The first inherited tier, and the "
    "narrowest of them.",
)
SYSTEM_AUTHORITY = AuthorityTier(
    4,
    "SYSTEM",
    "Ω²-A-04",
    "The system that operates the artifact claims it. Broader than a domain: a system composes "
    "domains "
    "and answers for their interaction.",
)
PROGRAM_AUTHORITY = AuthorityTier(
    5,
    "PROGRAM",
    "Ω²-A-05",
    "The governance programme the artifact was produced under claims it. The tier Ω-1's "
    "ANCESTRY-HOME "
    "rule corresponds to.",
)
FEDERATION_AUTHORITY = AuthorityTier(
    6,
    "FEDERATION",
    "Ω²-A-06",
    "A federation the programme participates in claims it. The last tier at which a NAMED body "
    "answers "
    "for the artifact.",
)
UNIVERSAL_FALLBACK = AuthorityTier(
    7,
    "UNIVERSAL_FALLBACK",
    "Ω²-A-07",
    "Unconditional. Reached when every tier above abstains. NOT a failure and NOT an error: a "
    "measured "
    "event, recorded per occurrence and ratcheted as a convergent population.",
    fallback=True,
)

#: The hierarchy this module ships, in resolution order. ``AuthorityResolver`` quantifies over the
#: sequence it is GIVEN, not over this tuple — a caller adding a tier passes its own. Totality is
#: guaranteed by a fallback tier being present, which the resolver checks, and not by this tuple
#: being exhaustive of every authority shape anyone might name.
INITIAL_TIERS: tuple[AuthorityTier, ...] = (
    ARTIFACT_AUTHORITY,
    OWNER_AUTHORITY,
    DOMAIN_AUTHORITY,
    SYSTEM_AUTHORITY,
    PROGRAM_AUTHORITY,
    FEDERATION_AUTHORITY,
    UNIVERSAL_FALLBACK,
)

#: The authority every unclaimed artifact resolves to. A CONSTANT, not a source, and not
#: configurable away: the resolver builds the terminal link from this value with no registration
#: step, so no deployment can produce a resolver that returns nothing.
UNIVERSAL_FALLBACK_AUTHORITY = "UCOS-UNIVERSAL-AUTHORITY"

#: The sentinel a source returns to abstain. Empty means "I make no claim", which is DIFFERENT from
#: a source that claims the fallback: the first falls through, the second is a named claim that
#: happens to name the universal body.
ABSTAIN = ""


# --------------------------------------------------------------------------------------- sources


@runtime_checkable
class AuthoritySource(Protocol):
    """The claim contract. Three methods, and no assumption about where a claim comes from."""

    def identifier(self) -> str:
        """A stable, unique name, cited in the chain it contributes to."""

    def tier(self) -> AuthorityTier:
        """The tier at which this source's claims are considered."""

    def claim(self, subject: str) -> str:
        """The authority asserted over ``subject``, or ``ABSTAIN`` for no claim."""


@dataclass(frozen=True)
class MappingSource:
    """A source backed by an explicit mapping. The simplest honest source.

    PRESENT FOR ADAPTERS AND EVIDENCE, not as the expected shape. A real domain source consults a
    declaration; a real federation source consults a remote registry. This class exists so a caller
    can lift an already-computed attribution — Ω-1's seven-rule chain, for instance — into a tier
    without writing a class.
    """

    source_identifier: str
    source_tier: AuthorityTier
    claims: dict[str, str]

    def __post_init__(self) -> None:
        if not self.source_identifier.strip():
            raise AuthorityError(
                "an authority source with no identifier cannot be cited in a chain"
            )
        object.__setattr__(self, "claims", dict(sorted(self.claims.items())))

    def identifier(self) -> str:
        return self.source_identifier

    def tier(self) -> AuthorityTier:
        return self.source_tier

    def claim(self, subject: str) -> str:
        return self.claims.get(subject, ABSTAIN).strip()


# ---------------------------------------------------------------------------------------- chains


@dataclass(frozen=True, order=True)
class AuthorityLink:
    """What one tier said when consulted. The unit the CHAIN is made of.

    EVERY CONSULTED TIER PRODUCES A LINK, including the ones that abstained. A chain holding only
    the winning tier answers "who owns this" and not "who was asked", and the second question is
    what makes an attribution arguable: an artifact attributed at PROGRAM tier because DOMAIN
    abstained is a different governance fact from one for which no domain source exists.
    """

    rank: int
    tier: str
    sources: tuple[str, ...] = ()
    claims: tuple[str, ...] = ()
    selected: str = ABSTAIN

    def __post_init__(self) -> None:
        object.__setattr__(self, "sources", tuple(sorted(self.sources)))
        object.__setattr__(self, "claims", tuple(sorted(set(self.claims))))

    @property
    def abstained(self) -> bool:
        return not self.claims

    @property
    def contested(self) -> bool:
        """Two or more DIFFERENT claims at one tier. Surfaced, and never silently resolved.

        Resolution still picks deterministically, because a resolver that raised here would let one
        disputed artifact stop the measurement of every other. The flag is how the disagreement
        survives into the contradiction register instead of being absorbed by the sort order.
        """
        return len(self.claims) > 1

    def as_record(self) -> dict[str, object]:
        return {
            "rank": self.rank,
            "tier": self.tier,
            "sources": list(self.sources),
            "claims": list(self.claims),
            "selected": self.selected,
            "abstained": self.abstained,
            "contested": self.contested,
        }


@dataclass(frozen=True, order=True)
class AuthorityChain:
    """The resolved authority for one subject, and the full record of how it was reached.

    ``authority`` IS NEVER EMPTY. ``__post_init__`` refuses an empty value rather than trusting the
    resolver, because this type is also constructed by adapters lifting legacy records, and Ω-1
    legitimately holds ``authority = ""`` for transients. A lift that dropped the value would
    reintroduce the hole this deliverable closes, in the one code path nobody tests as hard.
    """

    subject: str
    authority: str
    tier: str
    rule: str
    links: tuple[AuthorityLink, ...] = ()
    fallback: bool = False

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise AuthorityError("an authority chain must name the subject it resolves")
        if not self.authority.strip():
            raise AuthorityError(
                f"the chain for {self.subject!r} resolves to no authority; Ω-2.2 admits no such "
                "outcome, and an empty authority is the state that makes 'every artifact has an "
                "owner' unassertable"
            )
        if not self.rule.strip():
            raise AuthorityError(
                f"the chain for {self.subject!r} cites no rule, so the attribution cannot be "
                f"checked "
                "against the hierarchy that produced it"
            )
        object.__setattr__(self, "links", tuple(sorted(self.links)))

    @property
    def contested_tiers(self) -> tuple[str, ...]:
        return tuple(link.tier for link in self.links if link.contested)

    def explanation(self) -> str:
        """Why this authority, in words a reader can check against the links.

        PROSE GENERATED FROM THE LINKS, so the sentence and the machine-readable record cannot
        disagree.
        """
        consulted = [link for link in self.links if link.sources]
        abstained = [link.tier for link in consulted if link.abstained]
        head = (
            f"{self.subject} resolves to {self.authority} at tier {self.tier} by {self.rule}"
            if not self.fallback
            else (
                f"{self.subject} reached the universal fallback {self.authority} by {self.rule}, "
                "because every tier above it abstained"
            )
        )
        parts = [head, f"{len(consulted)} of {len(self.links)} tiers had a registered source"]
        if abstained:
            parts.append("abstaining tiers: " + ", ".join(abstained))
        if self.contested_tiers:
            parts.append(
                "CONTESTED at "
                + ", ".join(self.contested_tiers)
                + " — two sources at one tier claimed different authorities, and the disagreement "
                "is a "
                "contradiction finding rather than a resolution detail"
            )
        return "; ".join(parts) + "."

    def as_record(self) -> dict[str, object]:
        return {
            "subject": self.subject,
            "authority": self.authority,
            "tier": self.tier,
            "rule": self.rule,
            "fallback": self.fallback,
            "contested_tiers": list(self.contested_tiers),
            "explanation": self.explanation(),
            "links": [link.as_record() for link in self.links],
        }


@dataclass(frozen=True, order=True)
class FallbackEvent:
    """One recorded arrival at the universal fallback. The directive's "record the event".

    RECORDED PER OCCURRENCE, not aggregated. A count says how many artifacts nothing claims; the
    events say WHICH, and which tiers were even available to claim them — the difference between "47
    artifacts are unattributed" and "47 artifacts are unattributed and no DOMAIN source is
    registered", where only the second names the fix.

    ``coordinate`` is a ``TemporalCoordinate`` and is OPTIONAL, for the reason ``StateChange``
    gives: a deployment with no registered clock has no honest coordinate, and inventing one is
    worse than admitting its absence.
    """

    sequence: int
    subject: str
    tiers_consulted: tuple[str, ...]
    tiers_with_sources: tuple[str, ...]
    authority: str
    coordinate: TemporalCoordinate | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "tiers_consulted", tuple(self.tiers_consulted))
        object.__setattr__(self, "tiers_with_sources", tuple(self.tiers_with_sources))

    def as_record(self) -> dict[str, object]:
        record: dict[str, object] = {
            "sequence": self.sequence,
            "subject": self.subject,
            "authority": self.authority,
            "tiers_consulted": list(self.tiers_consulted),
            "tiers_with_sources": list(self.tiers_with_sources),
            "reason": (
                "every tier above the universal fallback abstained; "
                f"{len(self.tiers_with_sources)} of {len(self.tiers_consulted)} tiers had a "
                f"registered "
                "source to abstain with"
            ),
        }
        if self.coordinate is not None:
            record["coordinate"] = self.coordinate.as_record()
        return record


# -------------------------------------------------------------------------------------- resolver


class AuthorityResolver:
    """Walks the tiers and returns a chain. NEVER returns nothing, in any configuration.

    THE PROPERTY THIS BUYS, as the experiment that demonstrates it:
    ``AuthorityResolver([]).resolve("anything")`` returns a chain whose authority is the universal
    fallback. Zero sources, no configuration, no declaration file — and still an attribution.
    Deliverable Ω-2.2 is not a policy this class enforces; it is a shape it cannot be built without.
    """

    def __init__(
        self,
        sources: Iterable[AuthoritySource] = (),
        *,
        tiers: Sequence[AuthorityTier] = INITIAL_TIERS,
        fallback_authority: str = UNIVERSAL_FALLBACK_AUTHORITY,
        clock: ClockProvider | None = None,
    ) -> None:
        if not fallback_authority.strip():
            raise AuthorityError(
                "the fallback authority is empty, which would let resolution terminate with NONE "
                "through the one path Ω-2.2 forbids"
            )
        self._tiers = tuple(sorted(tiers))
        if not any(tier.fallback for tier in self._tiers):
            raise AuthorityError(
                "the tier hierarchy declares no fallback tier, so resolution could reach the end "
                "of the hierarchy with no answer; a hierarchy without an unconditional last rung "
                "is the defect this deliverable closes"
            )
        self._fallback_authority = fallback_authority
        self._clock = clock
        self._sources: list[AuthoritySource] = []
        self._fallback_events: list[FallbackEvent] = []
        for source in sources:
            self.register(source)

    def register(self, source: AuthoritySource) -> AuthoritySource:
        """Add a source. A duplicate identifier RAISES rather than replacing silently.

        Replacing silently would make an attribution depend on import order — the resolved owner of
        an artifact must not change because two modules were imported the other way round.
        """
        identifier = source.identifier()
        if not identifier.strip():
            raise AuthorityError("an authority source must identify itself to appear in a chain")
        if any(s.identifier() == identifier for s in self._sources):
            raise AuthorityError(
                f"an authority source identified {identifier!r} is already registered; replacing "
                f"it "
                "silently would make attribution depend on registration order"
            )
        if source.tier().fallback:
            raise AuthorityError(
                f"{identifier!r} registers at the fallback tier, which is constructed by the "
                f"resolver "
                "and admits no source; a registerable fallback is a removable fallback"
            )
        self._sources.append(source)
        return source

    def sources_at(self, tier: AuthorityTier) -> tuple[AuthoritySource, ...]:
        return tuple(
            sorted((s for s in self._sources if s.tier() == tier), key=lambda s: s.identifier())
        )

    def resolve(self, subject: str) -> AuthorityChain:
        """The authority chain for one subject. TOTAL: every call returns an authority."""
        if not subject.strip():
            raise AuthorityError(
                "authority was requested for an unnamed subject; an attribution that names nothing "
                "cannot be joined to the artifact it is about"
            )
        links: list[AuthorityLink] = []
        resolved: tuple[str, AuthorityTier] | None = None
        for tier in self._tiers:
            if tier.fallback:
                continue
            at_tier = self.sources_at(tier)
            claims = tuple(c for c in (s.claim(subject) for s in at_tier) if c)
            selected = sorted(set(claims))[0] if claims else ABSTAIN
            links.append(
                AuthorityLink(
                    rank=tier.rank,
                    tier=tier.name,
                    sources=tuple(s.identifier() for s in at_tier),
                    claims=claims,
                    selected=selected,
                )
            )
            if selected and resolved is None:
                resolved = (selected, tier)

        fallback_tier = next(tier for tier in self._tiers if tier.fallback)
        if resolved is None:
            links.append(
                AuthorityLink(
                    rank=fallback_tier.rank,
                    tier=fallback_tier.name,
                    sources=("resolver",),
                    claims=(self._fallback_authority,),
                    selected=self._fallback_authority,
                )
            )
            self._fallback_events.append(
                FallbackEvent(
                    sequence=len(self._fallback_events),
                    subject=subject,
                    tiers_consulted=tuple(t.name for t in self._tiers),
                    tiers_with_sources=tuple(
                        link.tier
                        for link in links
                        if link.sources and link.tier != fallback_tier.name
                    ),
                    authority=self._fallback_authority,
                    coordinate=self._clock.read() if self._clock is not None else None,
                )
            )
            return AuthorityChain(
                subject=subject,
                authority=self._fallback_authority,
                tier=fallback_tier.name,
                rule=fallback_tier.rule,
                links=tuple(links),
                fallback=True,
            )

        authority, tier = resolved
        links.append(
            AuthorityLink(
                rank=fallback_tier.rank,
                tier=fallback_tier.name,
                sources=("resolver",),
                claims=(),
                selected=ABSTAIN,
            )
        )
        return AuthorityChain(
            subject=subject,
            authority=authority,
            tier=tier.name,
            rule=tier.rule,
            links=tuple(links),
            fallback=False,
        )

    def resolve_all(self, subjects: Iterable[str]) -> tuple[AuthorityChain, ...]:
        return tuple(self.resolve(subject) for subject in sorted(set(subjects)))

    def fallback_events(self) -> tuple[FallbackEvent, ...]:
        """Every recorded arrival at the fallback. APPEND-ONLY by construction.

        No method removes an event and none is offered. A resolver that could forget a fallback
        arrival would make the metric it feeds unfalsifiable.
        """
        return tuple(self._fallback_events)

    def report(self) -> dict[str, object]:
        return {
            "tiers": [
                {
                    "rank": tier.rank,
                    "tier": tier.name,
                    "rule": tier.rule,
                    "fallback": tier.fallback,
                    "sources": [s.identifier() for s in self.sources_at(tier)],
                    "description": tier.description,
                }
                for tier in self._tiers
            ],
            "fallback_authority": self._fallback_authority,
            "registered_sources": len(self._sources),
            "fallback_events": len(self._fallback_events),
            "guarantee": (
                "resolve() returns an authority for every subject in every configuration, "
                "including a resolver with zero registered sources, because the terminal link is "
                "constructed from a constant rather than resolved from a source. Rule ids live on "
                "the tiers, so an eighth tier needs no entry in any table."
            ),
        }

    def __len__(self) -> int:
        return len(self._sources)


# ------------------------------------------------------------------------------------- reporting


def assert_total(chains: Iterable[AuthorityChain]) -> None:
    """Refuse a population in which any chain resolves to nothing.

    ``AuthorityChain.__post_init__`` already makes an empty authority unconstructable, so this can
    only fire for a chain built by a future path that bypasses the constructor. It exists where the
    POPULATION is held, on the same argument Ω-1 gives for keeping ``assert_total`` next to a total
    resolver.
    """
    orphans = sorted(
        chain.subject for chain in chains if not chain.authority.strip() or not chain.tier.strip()
    )
    if orphans:
        raise AuthorityError(
            "these subjects hold an authority chain that terminates with nothing, which Ω-2.2 "
            "admits "
            "no path to: " + ", ".join(orphans[:20])
        )


def fallback_count(chains: Iterable[AuthorityChain]) -> int:
    return sum(1 for chain in chains if chain.fallback)


def fallback_density(chains: Iterable[AuthorityChain]) -> float:
    """Fallback arrivals per resolved subject. SCALE-FREE, so growth cannot breach or flatter it.

    An empty population is a FAULT rather than a comfortable zero, on Ω-4's own argument: a density
    of 0.0 over no artifacts reports perfect attribution for a measurement that resolved nothing.
    """
    held = tuple(chains)
    if not held:
        raise AuthorityError(
            "fallback density was requested over an empty population, which would report perfect "
            "attribution for a measurement that resolved nothing"
        )
    return round(fallback_count(held) / len(held), 6)


def tier_census(
    chains: Iterable[AuthorityChain], tiers: Sequence[AuthorityTier] = INITIAL_TIERS
) -> dict[str, int]:
    """Resolution count per tier. EVERY tier appears, including the ones that resolved nothing."""
    counts = {tier.name: 0 for tier in tiers}
    for chain in chains:
        counts[chain.tier] = counts.get(chain.tier, 0) + 1
    return counts


def unattributed(chains: Iterable[AuthorityChain]) -> tuple[str, ...]:
    """Every subject that reached the fallback. The population Ω-2.2 requires to be measurable."""
    return tuple(sorted(chain.subject for chain in chains if chain.fallback))


def contested(chains: Iterable[AuthorityChain]) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Every subject with a contested tier, and which tiers. Input to the contradiction engine."""
    return tuple(
        sorted((chain.subject, chain.contested_tiers) for chain in chains if chain.contested_tiers)
    )


__all__ = [
    "ABSTAIN",
    "ARTIFACT_AUTHORITY",
    "DOMAIN_AUTHORITY",
    "FEDERATION_AUTHORITY",
    "INITIAL_TIERS",
    "OWNER_AUTHORITY",
    "PROGRAM_AUTHORITY",
    "SYSTEM_AUTHORITY",
    "UNIVERSAL_FALLBACK",
    "UNIVERSAL_FALLBACK_AUTHORITY",
    "AuthorityChain",
    "AuthorityError",
    "AuthorityLink",
    "AuthorityResolver",
    "AuthoritySource",
    "AuthorityTier",
    "FallbackEvent",
    "MappingSource",
    "assert_total",
    "contested",
    "fallback_count",
    "fallback_density",
    "tier_census",
    "unattributed",
]
