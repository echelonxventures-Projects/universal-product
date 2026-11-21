"""UCOS-UOF-001 — Ownership Determination Framework.

The engine that applies the Ownership Declaration Contract to collected evidence. It has
exactly three possible outcomes per subject — DECLARED, CONTESTED, UNRESOLVED — and no
fourth path that quietly assigns an owner to make a number look better.

Determination order (total, deterministic, declared):

    1. **Registration** — where a registration authority is declared, an unregistered
       subject is UNRESOLVED (``SUBJECT-NOT-REGISTERED``); OWN-REQ-004.
    2. **Zone eligibility** — evidence located outside a declared canonical-home zone is
       inadmissible; a subject with only such evidence is UNRESOLVED
       (``EVIDENCE-NOT-IN-CANONICAL-HOME-ZONE``); OWN-REQ-003.
    3. **Constitutive evidence** — corroboration alone yields UNRESOLVED
       (``NO-CONSTITUTIVE-OWNERSHIP-DECLARATION``); no evidence at all yields
       ``NO-OWNERSHIP-EVIDENCE``; OWN-REQ-001.
    4. **Single claim** — one surviving owner is DECLARED; OWN-REQ-002.
    5. **Contest** — several owners are settled *only* by declared precedence; an unsettled
       contest is CONTESTED (``CONTEST-NOT-SETTLED-BY-DECLARED-PRECEDENCE``); OWN-REQ-005.

Every record additionally carries the **refusals** its providers diagnosed: the candidate
locators that existed and the declared eligibility deficit that refused each one. A refusal is
never evidence and never an owner — it is the difference between "no artifact was ever written
for this subject" and "the artifact exists but a declared rule refused it", which is the
difference between work only an authority can do and work a project can simply do.
"""

from __future__ import annotations

from collections.abc import Iterable
from platform.foundation.contracts import content_hash
from platform.universal_ownership.contracts import (
    REASON_CONTEST_UNSETTLED,
    REASON_INELIGIBLE_ZONE,
    REASON_NO_CONSTITUTIVE_DECLARATION,
    REASON_NO_EVIDENCE,
    REASON_SUBJECT_NOT_REGISTERED,
    RULE_CONTEST_SETTLED,
    RULE_SOLE_DECLARATION,
    OwnershipDeclaration,
    OwnershipDeclarationContract,
    OwnershipDetermination,
    OwnershipEvidence,
    OwnershipRecord,
    OwnershipStanding,
    default_ownership_contract,
)
from platform.universal_ownership.errors import (
    OwnershipDeterminationError,
    OwnershipFabricationError,
)
from platform.universal_ownership.evidence import EvidenceProviderRegistry
from platform.universal_truth.contracts import Subject
from platform.universal_truth.eligibility import CanonicalHomePolicy
from platform.universal_truth.policy import TruthPolicy
from typing import Any

#: The refuser identity recorded when the *determination itself* — rather than any provider —
#: asked whether a subject's locators could hold ownership. The question belongs to the
#: canonical-home policy, so the refusal is attributed to it and never to a provider that never
#: recognised a candidate in the first place.
CANONICAL_HOME_REFUSER = "ownership.canonical-home"


def _claim_strength(evidence: Iterable[OwnershipEvidence]) -> tuple[int, int]:
    """The strength of one owner's claim: best precedence, then constitutive count."""
    items = tuple(evidence)
    best = max((item.precedence for item in items), default=0)
    constitutive = sum(1 for item in items if item.constitutive)
    return (best, constitutive)


class OwnershipDeterminationEngine:
    """Determines canonical ownership from constitutional evidence — and nothing else."""

    __slots__ = ("_providers", "_home", "_contract", "_registered")

    def __init__(
        self,
        providers: EvidenceProviderRegistry,
        *,
        policy: TruthPolicy | CanonicalHomePolicy | None = None,
        contract: OwnershipDeclarationContract | None = None,
        registered: Iterable[str] | None = None,
    ) -> None:
        if not isinstance(providers, EvidenceProviderRegistry):
            raise OwnershipDeterminationError("determination requires an EvidenceProviderRegistry")
        if policy is None:
            self._home: CanonicalHomePolicy | None = None
        elif isinstance(policy, CanonicalHomePolicy):
            self._home = policy
        elif isinstance(policy, TruthPolicy):
            self._home = CanonicalHomePolicy(policy)
        else:
            raise OwnershipDeterminationError(
                "policy must be a TruthPolicy or CanonicalHomePolicy when supplied"
            )
        self._providers = providers
        self._contract = contract or default_ownership_contract()
        self._registered = (
            frozenset(str(item) for item in registered) if registered is not None else None
        )

    @property
    def providers(self) -> EvidenceProviderRegistry:
        """The pluggable evidence providers this engine consults."""
        return self._providers

    @property
    def contract(self) -> OwnershipDeclarationContract:
        """The Ownership Declaration Contract this engine enforces."""
        return self._contract

    @property
    def policy(self) -> TruthPolicy | None:
        """The Repository Truth policy deciding canonical-home eligibility, if declared."""
        return self._home.policy if self._home is not None else None

    @property
    def home(self) -> CanonicalHomePolicy | None:
        """The composed canonical-home policy (zone class plus declared eligibility)."""
        return self._home

    @property
    def registration_ledger(self) -> frozenset[str] | None:
        """The registration ledger this engine enforces, or ``None`` when registration is open.

        Exposed so a composition can be rebuilt without silently dropping the requirement —
        a declared obligation that disappears through a wrapper is the same failure as one
        that was never declared.
        """
        return self._registered

    def _admissible(
        self, evidence: tuple[OwnershipEvidence, ...]
    ) -> tuple[tuple[OwnershipEvidence, ...], tuple[tuple[str, str, str], ...]]:
        """Filter evidence to declared canonical-home zones (OWN-REQ-003).

        Returns the admitted evidence and, for each item refused, the ``(locator, deficit,
        provider)`` triple naming *why* — so an exclusion is diagnosed rather than merely
        counted.
        """
        if self._home is None:
            return evidence, ()
        admitted: list[OwnershipEvidence] = []
        refused: list[tuple[str, str, str]] = []
        for item in evidence:
            if not item.locator:
                admitted.append(item)
                continue
            verdict = self._home.verdict(item.locator)
            if verdict.eligible:
                admitted.append(item)
            else:
                refused.append((verdict.locator, verdict.reason, item.provider_id))
        return tuple(admitted), tuple(sorted(set(refused)))

    def determine_subject(self, subject: Subject) -> OwnershipRecord:
        """Determine ownership for exactly one subject, honestly."""
        if not isinstance(subject, Subject):
            raise OwnershipDeterminationError("determination requires a Subject")
        evidence = self._providers.collect(subject)
        all_ids = tuple(item.evidence_id for item in evidence)
        diagnosed = tuple(
            (item.locator, item.reason, item.provider_id)
            for item in self._providers.refusals(subject)
        )

        if self._registered is not None and subject.subject_id not in self._registered:
            return OwnershipRecord.create(
                subject.subject_id,
                OwnershipStanding.UNRESOLVED,
                reasons=(REASON_SUBJECT_NOT_REGISTERED,),
                unmet=("OWN-REQ-004",),
                evidence_ids=all_ids,
                refusals=diagnosed,
            )

        admitted, excluded = self._admissible(evidence)
        refusals = tuple(sorted(set(diagnosed) | set(excluded)))
        constitutive = tuple(item for item in admitted if item.constitutive)

        if not constitutive:
            if not evidence:
                if self._home is not None and subject.locators:
                    verdicts = self._home.verdicts(subject.locators)
                    if not any(verdict.eligible for verdict in verdicts):
                        # Only locators no provider already diagnosed are attributed to the
                        # policy, so each refused locator carries exactly one refusal and it
                        # names the most specific refuser (UFC-16: one subject, one measurement).
                        diagnosed_locators = {locator for locator, _, _ in refusals}
                        return OwnershipRecord.create(
                            subject.subject_id,
                            OwnershipStanding.UNRESOLVED,
                            reasons=(REASON_INELIGIBLE_ZONE,),
                            unmet=("OWN-REQ-003",),
                            refusals=(
                                *refusals,
                                *(
                                    (verdict.locator, verdict.reason, CANONICAL_HOME_REFUSER)
                                    for verdict in verdicts
                                    if verdict.locator not in diagnosed_locators
                                ),
                            ),
                        )
                reason, unmet = REASON_NO_EVIDENCE, ("OWN-REQ-001",)
            elif excluded and not admitted:
                reason, unmet = REASON_INELIGIBLE_ZONE, ("OWN-REQ-003",)
            else:
                reason, unmet = REASON_NO_CONSTITUTIVE_DECLARATION, ("OWN-REQ-001",)
            return OwnershipRecord.create(
                subject.subject_id,
                OwnershipStanding.UNRESOLVED,
                reasons=(reason,),
                unmet=unmet,
                evidence_ids=all_ids,
                refusals=refusals,
            )

        by_owner: dict[str, list[OwnershipEvidence]] = {}
        for item in constitutive:
            by_owner.setdefault(item.owner, []).append(item)
        claims = {owner: len(items) for owner, items in by_owner.items()}

        if len(by_owner) == 1:
            owner = next(iter(by_owner))
            rule = RULE_SOLE_DECLARATION
        else:
            strengths = {owner: _claim_strength(items) for owner, items in by_owner.items()}
            best = max(strengths.values())
            leaders = sorted(owner for owner, value in strengths.items() if value == best)
            if len(leaders) != 1:
                return OwnershipRecord.create(
                    subject.subject_id,
                    OwnershipStanding.CONTESTED,
                    reasons=(REASON_CONTEST_UNSETTLED,),
                    unmet=("OWN-REQ-002", "OWN-REQ-005"),
                    claims=claims,
                    evidence_ids=all_ids,
                    refusals=refusals,
                )
            owner = leaders[0]
            rule = RULE_CONTEST_SETTLED

        winning = sorted(by_owner[owner], key=lambda item: item.order_key)
        authority = next((item.authority for item in winning if item.authority), owner)
        declaration = OwnershipDeclaration.create(
            subject.subject_id,
            owner,
            authority=authority,
            kind=winning[0].kind,
            locator=winning[0].locator,
            rule=rule,
            evidence_ids=[item.evidence_id for item in winning],
            satisfied=self._contract.mandatory_ids(),
        )
        return OwnershipRecord.create(
            subject.subject_id,
            OwnershipStanding.DECLARED,
            declaration=declaration,
            claims=claims,
            evidence_ids=all_ids,
            refusals=refusals,
        )

    def determine(self, subjects: Iterable[Subject]) -> OwnershipDetermination:
        """Determine ownership across a whole subject population."""
        records = [self.determine_subject(subject) for subject in subjects]
        return OwnershipDetermination.create(records, contract_id=self._contract.contract_id)

    def require_owner(self, subject: Subject) -> str:
        """The declared owner of ``subject``; refuses to invent one (fail-closed)."""
        record = self.determine_subject(subject)
        if not record.declared:
            raise OwnershipFabricationError(
                "ownership is not declared and SHALL NOT be inferred",
                subject=subject.subject_id,
                standing=record.standing.value,
                reasons=",".join(record.reasons),
            )
        return record.owner

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this engine's composition (UFC-11)."""
        return {
            "contract": self._contract.to_dict(),
            "providers": self._providers.to_dict(),
            "canonical_home": self._home.to_dict() if self._home is not None else None,
            "registration_required": self._registered is not None,
            "registered_count": len(self._registered) if self._registered is not None else 0,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this engine's composition."""
        return content_hash(self.to_dict())


__all__ = ["CANONICAL_HOME_REFUSER", "OwnershipDeterminationEngine"]
