"""UCOS-UOF-001 — Deterministic ownership recommendation (governance minimisation).

Ownership SHALL be assigned by governed determination and SHALL NEVER be implied. That law
stands, and this module does not weaken it by one degree: **a recommendation is not
ownership**. Nothing here enters an :class:`~platform.universal_ownership.contracts.
OwnershipDetermination`, changes a standing, or is admissible as evidence.

What it does is remove the *investigation* from governance. For every subject the
determination honestly left UNRESOLVED, a recommendation provider computes — deterministically,
from the same declared policy the determination used — the assignment a governing authority
would most plausibly ratify, together with the located basis for it. Governance then performs
the one act only governance may perform: it ratifies, amends or rejects a concrete proposal,
instead of rediscovering the repository for each subject.

The reduction this achieves is measured, not asserted:

    * **ratifiable** — an UNRESOLVED subject carrying at least one recommendation. The
      governance act is a decision over a stated proposal.
    * **irreducible** — an UNRESOLVED subject no provider can propose anything for. This is
      the theoretical minimum governance workload, and the honest number to report.

Adding a recommendation source is a registered provider (UFC-03); nothing in this module or in
the determination engine changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_ownership.contracts import (
    OwnershipDetermination,
    OwnershipRecord,
)
from platform.universal_ownership.errors import OwnershipRecommendationError
from platform.universal_truth.contracts import Subject
from platform.universal_truth.eligibility import CanonicalHomePolicy
from platform.universal_truth.policy import TruthPolicy
from typing import Any

#: The default recommendation precedence. Higher is preferred when several providers propose.
DEFAULT_PRECEDENCE = 100

#: Basis codes. Each names *why* a proposal is plausible, so a reviewer can check the reasoning
#: rather than trust a score.
BASIS_ELIGIBLE_LOCATOR = "SUBJECT-LOCATOR-IN-DECLARED-HOME-ZONE"
BASIS_PEER_PRECEDENT = "PEER-SUBJECTS-OF-THE-SAME-ATTRIBUTE-ARE-OWNED-BY-THIS-AUTHORITY"

#: The declared basis codes, in precedence order (strongest first).
RECOMMENDATION_BASES: tuple[str, ...] = (
    BASIS_ELIGIBLE_LOCATOR,
    BASIS_PEER_PRECEDENT,
)


@dataclass(frozen=True, slots=True)
class RecommendationProviderDescriptor:
    """How a recommendation provider identifies itself and how strongly it speaks."""

    provider_id: str
    basis: str
    precedence: int = DEFAULT_PRECEDENCE
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str) or not self.provider_id.strip():
            raise OwnershipRecommendationError("provider_id must be a non-empty string")
        if not isinstance(self.basis, str) or not self.basis.strip():
            raise OwnershipRecommendationError(
                "a recommendation provider must declare its basis", provider_id=self.provider_id
            )
        if not isinstance(self.precedence, int) or isinstance(self.precedence, bool):
            raise OwnershipRecommendationError(
                "provider precedence must be an int", provider_id=self.provider_id
            )

    @property
    def order_key(self) -> tuple[int, str]:
        """Deterministic provider order: highest precedence first, then identity."""
        return (-self.precedence, self.provider_id)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this descriptor."""
        return {
            "provider_id": self.provider_id,
            "basis": self.basis,
            "precedence": self.precedence,
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class OwnershipRecommendation:
    """A proposal for a governing authority to ratify. Never an assignment.

    ``constitutive`` is deliberately absent from this type: there is no field by which a
    recommendation could be mistaken for evidence.
    """

    subject_id: str
    proposed_owner: str
    basis: str
    provider_id: str
    authority: str = ""
    locator: str = ""
    precedence: int = DEFAULT_PRECEDENCE
    detail: str = ""
    recommendation_id: str = ""

    @classmethod
    def create(
        cls,
        subject_id: str,
        proposed_owner: str,
        basis: str,
        *,
        provider_id: str,
        authority: str = "",
        locator: str = "",
        precedence: int = DEFAULT_PRECEDENCE,
        detail: str = "",
    ) -> OwnershipRecommendation:
        """Build a validated, content-addressed recommendation."""
        for name, value in (
            ("subject_id", subject_id),
            ("proposed_owner", proposed_owner),
            ("basis", basis),
            ("provider_id", provider_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise OwnershipRecommendationError(
                    f"recommendation requires {name}", subject=str(subject_id)
                )
        core = {
            "subject_id": subject_id.strip(),
            "proposed_owner": proposed_owner.strip(),
            "basis": basis.strip(),
            "provider_id": provider_id.strip(),
            "locator": locator.strip(),
        }
        return cls(
            subject_id=subject_id.strip(),
            proposed_owner=proposed_owner.strip(),
            basis=basis.strip(),
            provider_id=provider_id.strip(),
            authority=authority.strip(),
            locator=locator.strip(),
            precedence=precedence,
            detail=detail,
            recommendation_id=f"UCOS-UOFR-{content_hash(core)[:16]}",
        )

    @property
    def order_key(self) -> tuple[int, str, str]:
        """Deterministic order: strongest proposal first, then locator, then identity."""
        return (-self.precedence, self.locator, self.recommendation_id)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this recommendation."""
        return {
            "recommendation_id": self.recommendation_id,
            "subject_id": self.subject_id,
            "proposed_owner": self.proposed_owner,
            "basis": self.basis,
            "provider_id": self.provider_id,
            "authority": self.authority,
            "locator": self.locator,
            "precedence": self.precedence,
            "detail": self.detail,
            "binding": False,
        }

    def as_declaration_entry(self) -> dict[str, Any]:
        """The governed-catalogue entry this proposal would become **if ratified**.

        Emitting the exact shape the ownership declaration catalogue expects is the whole
        point: ratification becomes a reviewed paste of a governed decision, not a
        translation exercise. It becomes binding only when an authority commits it.
        """
        return {
            "owner": self.proposed_owner,
            "authority": self.authority or self.proposed_owner,
            "locator": self.locator,
            "detail": f"{self.basis}: {self.detail}" if self.detail else self.basis,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this recommendation."""
        return content_hash(self.to_dict())


class OwnershipRecommendationProvider(ABC):
    """The extension point for every source of ownership *recommendation* (UFC-03)."""

    @abstractmethod
    def descriptor(self) -> RecommendationProviderDescriptor:
        """Describe this provider's identity, basis and declared precedence."""
        raise NotImplementedError  # pragma: no cover - abstract

    @abstractmethod
    def recommend(
        self, subject: Subject, record: OwnershipRecord
    ) -> Iterable[OwnershipRecommendation]:
        """Propose the assignments a governing authority could ratify for ``subject``."""
        raise NotImplementedError  # pragma: no cover - abstract

    def propose(
        self, subject: Subject, record: OwnershipRecord
    ) -> tuple[OwnershipRecommendation, ...]:
        """Protocol enforcement: refuse to propose for a settled subject, contain faults.

        A DECLARED subject already has an owner; proposing for it would be the first step
        toward a recommendation quietly displacing a determination. That is refused here.
        """
        if not isinstance(subject, Subject):
            raise OwnershipRecommendationError("recommendation requires a Subject")
        if not isinstance(record, OwnershipRecord):
            raise OwnershipRecommendationError("recommendation requires an OwnershipRecord")
        descriptor = self.descriptor()
        if record.declared:
            return ()
        try:
            produced = tuple(self.recommend(subject, record))
        except OwnershipRecommendationError:
            raise
        except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
            raise OwnershipRecommendationError(
                "recommendation provider failed",
                provider_id=descriptor.provider_id,
                subject=subject.subject_id,
                detail=str(exc),
            ) from exc
        for item in produced:
            if not isinstance(item, OwnershipRecommendation):
                raise OwnershipRecommendationError(
                    "provider produced a non-recommendation value",
                    provider_id=descriptor.provider_id,
                )
            if item.provider_id != descriptor.provider_id:
                raise OwnershipRecommendationError(
                    "recommendation provenance does not match its provider",
                    provider_id=descriptor.provider_id,
                    recommendation_provider=item.provider_id,
                )
            if item.subject_id != subject.subject_id:
                raise OwnershipRecommendationError(
                    "recommendation subject does not match the requested subject",
                    provider_id=descriptor.provider_id,
                    subject=subject.subject_id,
                )
        unique = {item.recommendation_id: item for item in produced}
        return tuple(sorted(unique.values(), key=lambda item: item.order_key))


class EligibleLocatorRecommendationProvider(OwnershipRecommendationProvider):
    """Proposes the authority of the subject's highest-precedence eligible locator.

    The subject is mentioned somewhere the Truth policy already declares able to hold
    canonical ownership, but no artifact there *declared* the ownership. The proposal is
    therefore: let the authority of that zone own it. The determination would not make that
    leap, and correctly so — but a governing authority can, in one reviewed act.
    """

    __slots__ = ("_descriptor", "_home")

    def __init__(
        self,
        policy: TruthPolicy | CanonicalHomePolicy,
        *,
        provider_id: str = "recommendation.eligible-locator",
        precedence: int = 600,
        description: str = "Authority of the highest-precedence eligible locator of the subject.",
    ) -> None:
        if isinstance(policy, CanonicalHomePolicy):
            self._home = policy
        elif isinstance(policy, TruthPolicy):
            self._home = CanonicalHomePolicy(policy)
        else:
            raise OwnershipRecommendationError(
                "eligible-locator provider requires a TruthPolicy or CanonicalHomePolicy",
                provider_id=provider_id,
            )
        self._descriptor = RecommendationProviderDescriptor(
            provider_id=provider_id,
            basis=BASIS_ELIGIBLE_LOCATOR,
            precedence=precedence,
            description=description,
        )

    @property
    def home(self) -> CanonicalHomePolicy:
        """The composed canonical-home policy this provider proposes within.

        Proposing a locator the project's own eligibility rules would refuse would waste a
        governance act, so the provider proposes only what an authority could actually ratify.
        """
        return self._home

    def descriptor(self) -> RecommendationProviderDescriptor:
        """Describe this provider."""
        return self._descriptor

    def recommend(
        self, subject: Subject, record: OwnershipRecord
    ) -> Iterable[OwnershipRecommendation]:
        """The single strongest eligible-zone proposal, or nothing."""
        del record
        best: tuple[int, str, str, str] | None = None
        for locator in subject.locators:
            if not self._home.admits(locator):
                continue
            classification = self._home.policy.classify(locator)
            owner = classification.authority or classification.zone_id
            candidate = (classification.precedence, locator, owner, classification.zone_id)
            if (
                best is None
                or candidate[0] > best[0]
                or (candidate[0] == best[0] and candidate[1] < best[1])
            ):
                best = candidate
        if best is None:
            return ()
        precedence, locator, owner, zone_id = best
        return (
            OwnershipRecommendation.create(
                subject.subject_id,
                owner,
                BASIS_ELIGIBLE_LOCATOR,
                provider_id=self._descriptor.provider_id,
                authority=owner,
                locator=locator,
                precedence=self._descriptor.precedence + precedence,
                detail=(
                    f"the subject is located in declared home zone {zone_id}, whose authority "
                    f"could own it once an authority says so"
                ),
            ),
        )


class PeerPrecedentRecommendationProvider(OwnershipRecommendationProvider):
    """Proposes the owner that already owns the majority of the subject's declared peers.

    Peers are subjects sharing a declared attribute value — a family, a class, a band. Where
    an authority already owns most of a family, proposing it for the family's remainder is a
    precedent a governing authority can confirm in one act instead of many. The precedent is
    computed once over the *determination*, so it is derived from declared ownership only:
    a recommendation never becomes the basis of another recommendation.
    """

    __slots__ = ("_descriptor", "_attribute", "_precedent")

    def __init__(
        self,
        precedent: Mapping[str, str],
        *,
        attribute: str,
        provider_id: str = "recommendation.peer-precedent",
        precedence: int = 300,
        description: str = "Owner of the majority of already-declared peers of the same attribute.",
    ) -> None:
        if not isinstance(precedent, Mapping):
            raise OwnershipRecommendationError(
                "peer-precedent provider requires a mapping", provider_id=provider_id
            )
        if not isinstance(attribute, str) or not attribute.strip():
            raise OwnershipRecommendationError(
                "peer-precedent provider requires the attribute it groups by",
                provider_id=provider_id,
            )
        self._attribute = attribute.strip()
        self._precedent = {str(key): str(value) for key, value in precedent.items()}
        self._descriptor = RecommendationProviderDescriptor(
            provider_id=provider_id,
            basis=BASIS_PEER_PRECEDENT,
            precedence=precedence,
            description=description,
        )

    @classmethod
    def from_determination(
        cls,
        determination: OwnershipDetermination,
        subjects: Iterable[Subject],
        *,
        attribute: str,
        minimum_peers: int = 2,
        **kwargs: Any,
    ) -> PeerPrecedentRecommendationProvider:
        """Derive the precedent from declared ownership alone (fail-closed on a tie).

        An attribute value whose declared peers disagree on their owner, or that has fewer
        than ``minimum_peers`` declared peers, yields **no** precedent: a thin or contested
        majority is not a precedent, and inventing one here would be the inference the whole
        framework refuses.
        """
        if not isinstance(determination, OwnershipDetermination):
            raise OwnershipRecommendationError("precedent requires an OwnershipDetermination")
        owners = determination.index()
        tally: dict[str, dict[str, int]] = {}
        for subject in subjects:
            value = subject.attribute(attribute)
            owner = owners.get(subject.subject_id)
            if not value or not owner:
                continue
            tally.setdefault(value, {})
            tally[value][owner] = tally[value].get(owner, 0) + 1
        precedent: dict[str, str] = {}
        for value, counts in tally.items():
            if sum(counts.values()) < max(1, int(minimum_peers)):
                continue
            ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
            if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
                continue
            precedent[value] = ranked[0][0]
        return cls(precedent, attribute=attribute, **kwargs)

    @property
    def attribute(self) -> str:
        """The declared attribute this provider groups peers by."""
        return self._attribute

    @property
    def count(self) -> int:
        """How many attribute values carry a usable precedent."""
        return len(self._precedent)

    def descriptor(self) -> RecommendationProviderDescriptor:
        """Describe this provider."""
        return self._descriptor

    def recommend(
        self, subject: Subject, record: OwnershipRecord
    ) -> Iterable[OwnershipRecommendation]:
        """The peer-precedent proposal for ``subject``, or nothing."""
        del record
        value = subject.attribute(self._attribute)
        owner = self._precedent.get(value) if value else None
        if not owner:
            return ()
        return (
            OwnershipRecommendation.create(
                subject.subject_id,
                owner,
                BASIS_PEER_PRECEDENT,
                provider_id=self._descriptor.provider_id,
                authority=owner,
                precedence=self._descriptor.precedence,
                detail=(
                    f"every declared peer with {self._attribute}={value} is owned by this authority"
                ),
            ),
        )


class CallableRecommendationProvider(OwnershipRecommendationProvider):
    """Wraps any callable as a recommendation provider — the seam for a future proposer."""

    __slots__ = ("_descriptor", "_supplier")

    def __init__(
        self,
        descriptor: RecommendationProviderDescriptor,
        supplier: Callable[[Subject, OwnershipRecord], Iterable[OwnershipRecommendation]],
    ) -> None:
        if not isinstance(descriptor, RecommendationProviderDescriptor):
            raise OwnershipRecommendationError("callable provider requires a descriptor")
        if not callable(supplier):
            raise OwnershipRecommendationError(
                "callable provider requires a callable", provider_id=descriptor.provider_id
            )
        self._descriptor = descriptor
        self._supplier = supplier

    def descriptor(self) -> RecommendationProviderDescriptor:
        """Describe this provider."""
        return self._descriptor

    def recommend(
        self, subject: Subject, record: OwnershipRecord
    ) -> Iterable[OwnershipRecommendation]:
        """Delegate to the wrapped supplier."""
        return self._supplier(subject, record)


class RecommendationProviderRegistry:
    """A deterministic, fail-closed registry of ownership recommendation providers."""

    __slots__ = ("_providers",)

    def __init__(self, providers: Iterable[OwnershipRecommendationProvider] = ()) -> None:
        self._providers: dict[str, OwnershipRecommendationProvider] = {}
        for provider in providers:
            self.add(provider)

    def add(self, provider: OwnershipRecommendationProvider) -> OwnershipRecommendationProvider:
        """Register ``provider``; idempotent by object, fail-closed on identity collision."""
        if not isinstance(provider, OwnershipRecommendationProvider):
            raise OwnershipRecommendationError(
                "registry accepts only OwnershipRecommendationProvider values"
            )
        descriptor = provider.descriptor()
        existing = self._providers.get(descriptor.provider_id)
        if existing is not None:
            if existing is provider:
                return existing
            raise OwnershipRecommendationError(
                "provider identity already registered", provider_id=descriptor.provider_id
            )
        self._providers[descriptor.provider_id] = provider
        return provider

    def extend(
        self, providers: Iterable[OwnershipRecommendationProvider]
    ) -> tuple[OwnershipRecommendationProvider, ...]:
        """Register every provider in ``providers``, returning them in resolution order."""
        for provider in providers:
            self.add(provider)
        return self.ordered()

    def get(self, provider_id: str) -> OwnershipRecommendationProvider | None:
        """The registered provider ``provider_id``, or ``None``."""
        return self._providers.get(provider_id)

    def require(self, provider_id: str) -> OwnershipRecommendationProvider:
        """The registered provider ``provider_id`` (fail-closed)."""
        provider = self.get(provider_id)
        if provider is None:
            raise OwnershipRecommendationError(
                "unknown recommendation provider", provider_id=str(provider_id)
            )
        return provider

    @property
    def count(self) -> int:
        """How many providers are registered."""
        return len(self._providers)

    def ordered(self) -> tuple[OwnershipRecommendationProvider, ...]:
        """Every provider in declared precedence order — never insertion order."""
        return tuple(sorted(self._providers.values(), key=lambda item: item.descriptor().order_key))

    def descriptors(self) -> tuple[RecommendationProviderDescriptor, ...]:
        """Every provider descriptor in resolution order."""
        return tuple(provider.descriptor() for provider in self.ordered())

    def propose(
        self, subject: Subject, record: OwnershipRecord
    ) -> tuple[OwnershipRecommendation, ...]:
        """Every proposal for ``subject``, deterministically ordered."""
        found: dict[str, OwnershipRecommendation] = {}
        for provider in self.ordered():
            for item in provider.propose(subject, record):
                found[item.recommendation_id] = item
        return tuple(sorted(found.values(), key=lambda item: item.order_key))

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this registry."""
        return {
            "provider_count": self.count,
            "providers": [descriptor.to_dict() for descriptor in self.descriptors()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this registry."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class GovernanceWorkload:
    """The measured governance workload after every deterministic capability has run.

    This is the instrument that makes "governance decides only irreducible ambiguity"
    checkable. The open population is measured three ways, and the three are *orthogonal*
    because they answer different questions:

    * ``ratifiable`` — a provider can state the assignment an authority would ratify, with its
      located basis. Work reduced to a decision over a stated proposal.
    * ``remediable`` — the determination diagnosed a **named, located deficit**: a candidate
      home exists and a declared eligibility rule refused it. Work that needs an *act* (register
      the artifact, move it out of derived residue, give it the declared form), not a decision.
    * ``irreducible`` — neither. No proposal, no diagnosed deficit. This is the theoretical
      minimum an authority must decide from first principles, and ``governance_minimum``
      measures it.

    Reporting ``remediable`` separately is what stops a mechanical omission from being billed as
    constitutional ambiguity. A subject whose only artifact is simply unregistered does not need
    a governing authority; it needs registration.
    """

    subject_total: int
    declared: int
    contested: int
    recommendations: tuple[OwnershipRecommendation, ...]
    ratifiable: tuple[str, ...]
    irreducible: tuple[str, ...]
    remediable: tuple[str, ...] = ()
    deficits: tuple[tuple[str, str], ...] = ()
    workload_id: str = ""

    @classmethod
    def create(
        cls,
        determination: OwnershipDetermination,
        recommendations: Iterable[OwnershipRecommendation],
    ) -> GovernanceWorkload:
        """Build a content-addressed workload measurement over a determination."""
        if not isinstance(determination, OwnershipDetermination):
            raise OwnershipRecommendationError("workload requires an OwnershipDetermination")
        ordered = tuple(sorted(recommendations, key=lambda item: (item.subject_id, item.order_key)))
        proposed = {item.subject_id for item in ordered}
        open_records = tuple(record for record in determination.records if not record.declared)
        open_subjects = {record.subject_id for record in open_records}
        ratifiable = tuple(sorted(open_subjects & proposed))
        irreducible = tuple(sorted(open_subjects - proposed))
        remediable = tuple(sorted(record.subject_id for record in open_records if record.refusals))
        deficits = tuple(
            sorted(
                {
                    (record.subject_id, reason)
                    for record in open_records
                    for reason in record.refusal_reasons
                }
            )
        )
        core = {
            "determination": determination.determination_id,
            "recommendations": [item.recommendation_id for item in ordered],
        }
        return cls(
            subject_total=determination.total,
            declared=len(determination.declared),
            contested=len(determination.contested),
            recommendations=ordered,
            ratifiable=ratifiable,
            irreducible=irreducible,
            remediable=remediable,
            deficits=deficits,
            workload_id=f"UCOS-UOFW-{content_hash(core)[:16]}",
        )

    @property
    def open_total(self) -> int:
        """How many subjects the determination left open (unresolved or contested)."""
        return len(self.ratifiable) + len(self.irreducible)

    @property
    def reduction(self) -> float:
        """The share of the open population reduced to a ratifiable proposal."""
        if self.open_total == 0:
            return 100.0
        return round(len(self.ratifiable) / self.open_total * 100, 4)

    @property
    def governance_minimum(self) -> tuple[str, ...]:
        """The open subjects that are neither ratifiable nor remediable.

        Nothing deterministic can propose an owner for these and nothing names a deficit to
        remedy, so this — and only this — is work a governing authority must originate.
        """
        remediable = set(self.remediable)
        return tuple(item for item in self.irreducible if item not in remediable)

    @property
    def determinable(self) -> float:
        """The share of the open population a deterministic act or proposal can discharge."""
        if self.open_total == 0:
            return 100.0
        reachable = len(set(self.ratifiable) | set(self.remediable))
        return round(reachable / self.open_total * 100, 4)

    def by_deficit(self) -> dict[str, int]:
        """How many open subjects each named, located deficit accounts for."""
        tally: dict[str, int] = {}
        for _, reason in self.deficits:
            tally[reason] = tally.get(reason, 0) + 1
        return dict(sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])))

    def for_subject(self, subject_id: str) -> tuple[OwnershipRecommendation, ...]:
        """Every proposal for ``subject_id``, strongest first."""
        return tuple(
            sorted(
                (item for item in self.recommendations if item.subject_id == subject_id),
                key=lambda item: item.order_key,
            )
        )

    def strongest(self) -> dict[str, OwnershipRecommendation]:
        """The single strongest proposal per ratifiable subject."""
        best: dict[str, OwnershipRecommendation] = {}
        for item in self.recommendations:
            current = best.get(item.subject_id)
            if current is None or item.order_key < current.order_key:
                best[item.subject_id] = item
        return dict(sorted(best.items()))

    def by_basis(self) -> dict[str, int]:
        """How many proposals each declared basis produced."""
        tally = dict.fromkeys(RECOMMENDATION_BASES, 0)
        for item in self.recommendations:
            tally[item.basis] = tally.get(item.basis, 0) + 1
        return dict(sorted(tally.items()))

    def by_proposed_owner(self) -> dict[str, int]:
        """How many ratifiable subjects each proposed owner would take, descending."""
        tally: dict[str, int] = {}
        for item in self.strongest().values():
            tally[item.proposed_owner] = tally.get(item.proposed_owner, 0) + 1
        return dict(sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])))

    def as_declaration_document(self, *, authority: str = "") -> dict[str, Any]:
        """The governed catalogue this workload would become **if wholly ratified**.

        Deliberately emitted as a *separate* document with ``ratified: false``: it is a draft
        for review, never a drop-in replacement for the governed catalogue, and no engine
        reads it as evidence.
        """
        return {
            "$comment": (
                "DRAFT PROPOSAL — NOT BINDING. Deterministically derived from declared "
                "Repository Truth for review by a governing authority. No engine reads this "
                "document as evidence. Ratification means an authority reviews each entry and "
                "commits the accepted ones into the governed ownership declaration catalogue."
            ),
            "ratified": False,
            "authority": authority,
            "workload_id": self.workload_id,
            "reduction_percentage": self.reduction,
            "remediable": list(self.remediable),
            "irreducible": list(self.irreducible),
            "governance_minimum": list(self.governance_minimum),
            "assignments": {
                subject_id: item.as_declaration_entry()
                for subject_id, item in self.strongest().items()
            },
        }

    def counts(self) -> dict[str, int]:
        """Headline counts of the governance workload."""
        return {
            "subjects": self.subject_total,
            "declared": self.declared,
            "contested": self.contested,
            "open": self.open_total,
            "ratifiable": len(self.ratifiable),
            "remediable": len(self.remediable),
            "irreducible": len(self.irreducible),
            "governance_minimum": len(self.governance_minimum),
            "recommendations": len(self.recommendations),
        }

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this workload."""
        return {
            "workload_id": self.workload_id,
            "counts": self.counts(),
            "reduction_percentage": self.reduction,
            "determinable_percentage": self.determinable,
            "by_basis": self.by_basis(),
            "by_deficit": self.by_deficit(),
            "by_proposed_owner": self.by_proposed_owner(),
            "remediable": list(self.remediable),
            "irreducible": list(self.irreducible),
            "governance_minimum": list(self.governance_minimum),
            "deficits": [
                {"subject_id": subject_id, "reason": reason} for subject_id, reason in self.deficits
            ],
            "recommendations": [item.to_dict() for item in self.recommendations],
        }

    def summary(self) -> dict[str, Any]:
        """A compact projection without the per-proposal detail."""
        return {
            "workload_id": self.workload_id,
            "counts": self.counts(),
            "reduction_percentage": self.reduction,
            "determinable_percentage": self.determinable,
            "by_basis": self.by_basis(),
            "by_deficit": self.by_deficit(),
            "by_proposed_owner": self.by_proposed_owner(),
            "governance_minimum": list(self.governance_minimum),
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this workload."""
        return content_hash(self.to_dict())


class GovernanceReductionEngine:
    """Runs every registered recommendation provider over the open residue of a determination."""

    __slots__ = ("_providers",)

    def __init__(self, providers: RecommendationProviderRegistry) -> None:
        if not isinstance(providers, RecommendationProviderRegistry):
            raise OwnershipRecommendationError(
                "governance reduction requires a RecommendationProviderRegistry"
            )
        self._providers = providers

    @property
    def providers(self) -> RecommendationProviderRegistry:
        """The registered recommendation providers."""
        return self._providers

    def reduce(
        self, determination: OwnershipDetermination, subjects: Iterable[Subject]
    ) -> GovernanceWorkload:
        """Measure the governance workload remaining over ``determination``.

        Only subjects the determination left open are proposed for, and a subject present in
        the determination but absent from ``subjects`` yields no proposal rather than a
        guess — so the workload can never be understated by a missing input.
        """
        index = {subject.subject_id: subject for subject in subjects}
        proposals: list[OwnershipRecommendation] = []
        for record in determination.records:
            if record.declared:
                continue
            subject = index.get(record.subject_id)
            if subject is None:
                continue
            proposals.extend(self._providers.propose(subject, record))
        return GovernanceWorkload.create(determination, proposals)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this engine's composition."""
        return {"providers": self._providers.to_dict()}

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this engine's composition."""
        return content_hash(self.to_dict())


def default_recommendation_providers(
    policy: TruthPolicy | CanonicalHomePolicy,
    *,
    determination: OwnershipDetermination | None = None,
    subjects: Iterable[Subject] = (),
    attribute: str = "",
) -> tuple[OwnershipRecommendationProvider, ...]:
    """The shipped provider set: eligible locator always, peer precedent when derivable."""
    providers: list[OwnershipRecommendationProvider] = [
        EligibleLocatorRecommendationProvider(policy)
    ]
    if determination is not None and attribute:
        providers.append(
            PeerPrecedentRecommendationProvider.from_determination(
                determination, subjects, attribute=attribute
            )
        )
    return tuple(providers)


def build_governance_reduction(
    policy: TruthPolicy | CanonicalHomePolicy,
    *,
    determination: OwnershipDetermination | None = None,
    subjects: Iterable[Subject] = (),
    attribute: str = "",
) -> GovernanceReductionEngine:
    """The default composition of the governance reduction engine."""
    population = tuple(subjects)
    return GovernanceReductionEngine(
        RecommendationProviderRegistry(
            default_recommendation_providers(
                policy,
                determination=determination,
                subjects=population,
                attribute=attribute,
            )
        )
    )


__all__ = [
    "BASIS_ELIGIBLE_LOCATOR",
    "BASIS_PEER_PRECEDENT",
    "DEFAULT_PRECEDENCE",
    "RECOMMENDATION_BASES",
    "CallableRecommendationProvider",
    "EligibleLocatorRecommendationProvider",
    "GovernanceReductionEngine",
    "GovernanceWorkload",
    "OwnershipRecommendation",
    "OwnershipRecommendationProvider",
    "PeerPrecedentRecommendationProvider",
    "RecommendationProviderDescriptor",
    "RecommendationProviderRegistry",
    "build_governance_reduction",
    "default_recommendation_providers",
]
