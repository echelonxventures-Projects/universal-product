"""UCOS-RTAG-000001 — the Repository Truth Assimilation Gate (Requirement 008).

Before anything may be created, five things must happen: discover, assimilate, search,
reuse analysis, gap analysis. Creation is permitted only where all four canonical
searches come back empty — no canonical capability, no canonical owner, no canonical
artifact, no canonical knowledge.

The failure this prevents is not wasted effort. It is a **second truth**: two subjects
that both produce ``pricing.quote`` are not redundant, they are a repository that answers
one question two ways and cannot say which answer is canonical. Every downstream
guarantee in this package — one owner, one certifier, one derived order — assumes that
question has one answer, so this gate is what the rest of the system stands on.

What "already exists" means
---------------------------
Four searches, run against the declarations and nothing else (DATA in :data:`SEARCHES`,
so a fifth is one appended entry):

    * **artifact** — a subject with this key is already declared;
    * **capability** — some subject already declares one of the proposed outputs;
    * **owner** — the proposed owner already owns a subject covering this ground;
    * **knowledge** — the proposed inputs are already consumed under this owner.

A hit is not advice. :func:`require_creatable` refuses, and names the incumbent, so the
caller's next move is to extend the canonical subject rather than to file beside it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.constitution.errors import DuplicateTruth
from engine.constitution.metadata import ConstitutionalMetadata, Population
from engine.uckp.canonical import content_hash

#: The identity of the assimilation gate this module realises.
GATE_ID = "UCOS-RTAG-000001"

#: Versioned so searches can be *added* without any prior verdict changing meaning.
ASSIMILATION_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class Proposal:
    """What a caller intends to create, before it has the right to.

    Deliberately not a :class:`~engine.constitution.metadata.ConstitutionalMetadata`: a
    proposal is not yet an artifact, and giving it the artifact type would let an
    unassimilated proposal be passed to anything that takes a declaration.
    """

    subject: str
    owner: str = ""
    outputs: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    intent: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "owner": self.owner,
            "outputs": list(self.outputs),
            "inputs": list(self.inputs),
            "intent": self.intent,
        }


@dataclass(frozen=True, slots=True)
class Incumbent:
    """An existing canonical subject that already covers part of a proposal."""

    search: str
    subject: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"search": self.search, "subject": self.subject, "detail": self.detail}


#: A search: given the proposal and the population, name whatever already covers it.
SearchFunction = Callable[[Proposal, Population], "tuple[Incumbent, ...]"]


@dataclass(frozen=True, slots=True)
class Search:
    """One canonical search that must come back empty before creation is permitted."""

    name: str
    statement: str
    run: SearchFunction

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "statement": self.statement}


def _search_artifact(proposal: Proposal, population: Population) -> tuple[Incumbent, ...]:
    if proposal.subject in population:
        return (
            Incumbent(
                "artifact",
                proposal.subject,
                "a subject with this key is already declared; extend it rather than "
                "declaring a second one",
            ),
        )
    return ()


def _search_capability(proposal: Proposal, population: Population) -> tuple[Incumbent, ...]:
    found: list[Incumbent] = []
    wanted = set(proposal.outputs)
    if not wanted:
        return ()
    for record in population:
        if record.subject == proposal.subject:
            continue
        overlap = sorted(wanted & set(record.entries("outputs")))
        if overlap:
            found.append(
                Incumbent(
                    "capability",
                    record.subject,
                    f"already produces {', '.join(overlap)}; a capability has one canonical owner",
                )
            )
    return tuple(found)


def _search_owner(proposal: Proposal, population: Population) -> tuple[Incumbent, ...]:
    if not proposal.owner:
        return ()
    found: list[Incumbent] = []
    for record in population:
        if record.subject == proposal.subject:
            continue
        if record.canonical_owner != proposal.owner:
            continue
        # Same owner *and* overlapping ground is a duplicate; same owner alone is not —
        # a nucleus is expected to own many capabilities, and refusing that would make
        # the gate prohibit growth rather than duplication.
        if set(proposal.outputs) & set(record.entries("outputs")):
            found.append(
                Incumbent(
                    "owner",
                    record.subject,
                    f"owner {proposal.owner!r} already covers this ground here",
                )
            )
    return tuple(found)


def _search_knowledge(proposal: Proposal, population: Population) -> tuple[Incumbent, ...]:
    if not proposal.inputs or not proposal.owner:
        return ()
    wanted = set(proposal.inputs)
    found: list[Incumbent] = []
    for record in population:
        if record.subject == proposal.subject:
            continue
        if record.canonical_owner != proposal.owner:
            continue
        overlap = sorted(wanted & set(record.entries("inputs")))
        if overlap and set(proposal.outputs) & set(record.entries("outputs")):
            found.append(
                Incumbent(
                    "knowledge",
                    record.subject,
                    f"already assimilates {', '.join(overlap)} under the same owner "
                    "toward the same outputs",
                )
            )
    return tuple(found)


#: The canonical searches (DATA — extend by appending, never edit).
SEARCHES: tuple[Search, ...] = (
    Search("artifact", "no canonical artifact with this key exists", _search_artifact),
    Search("capability", "no canonical capability produces these outputs", _search_capability),
    Search("owner", "no canonical owner already covers this ground", _search_owner),
    Search(
        "knowledge",
        "no canonical knowledge already assimilates these inputs",
        _search_knowledge,
    ),
)


@dataclass(frozen=True, slots=True)
class AssimilationVerdict:
    """Whether a proposal may be created, and what already exists if it may not."""

    gate_id: str
    proposal: Proposal
    incumbents: tuple[Incumbent, ...]
    searched: tuple[str, ...] = ()
    scope: Mapping[str, Any] = field(default_factory=dict)

    @property
    def creatable(self) -> bool:
        """True iff every canonical search came back empty."""
        return not self.incumbents

    @property
    def status(self) -> str:
        return "CREATE" if self.creatable else "REUSE"

    @property
    def reuse_targets(self) -> tuple[str, ...]:
        """The existing subjects the caller should extend instead, ordered."""
        return tuple(sorted({incumbent.subject for incumbent in self.incumbents}))

    def gap(self) -> tuple[str, ...]:
        """The searches that found nothing — the genuine gap this proposal would fill."""
        covered = {incumbent.search for incumbent in self.incumbents}
        return tuple(name for name in self.searched if name not in covered)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-assimilation-verdict",
            "version": ASSIMILATION_VERSION,
            "gate_id": self.gate_id,
            "status": self.status,
            "creatable": self.creatable,
            "proposal": self.proposal.to_dict(),
            "searched": list(self.searched),
            "gap": list(self.gap()),
            "reuse_targets": list(self.reuse_targets),
            "incumbents": [i.to_dict() for i in self.incumbents],
            "scope": {k: self.scope[k] for k in sorted(self.scope)},
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def assimilate(
    proposal: Proposal,
    population: Population,
    *,
    searches: Sequence[Search] = SEARCHES,
) -> AssimilationVerdict:
    """Run every canonical search over ``proposal`` and return the verdict.

    Reports; does not refuse. A caller doing gap analysis wants the whole picture,
    including which searches came back empty — :func:`require_creatable` is the gate.
    """
    incumbents: list[Incumbent] = []
    for search in searches:
        incumbents.extend(search.run(proposal, population))
    incumbents.sort(key=lambda i: (i.search, i.subject))
    return AssimilationVerdict(
        gate_id=GATE_ID,
        proposal=proposal,
        incumbents=tuple(incumbents),
        searched=tuple(search.name for search in searches),
        scope={"subjects": len(population)},
    )


def require_creatable(
    proposal: Proposal,
    population: Population,
    *,
    searches: Sequence[Search] = SEARCHES,
) -> AssimilationVerdict:
    """Return the verdict if creation is permitted, else refuse — the fail-closed gate.

    Raises:
        DuplicateTruth: a canonical artifact, capability, owner or knowledge already
            covers the proposal; the incumbents to extend instead are named.
    """
    verdict = assimilate(proposal, population, searches=searches)
    if not verdict.creatable:
        raise DuplicateTruth(
            "creation refused: canonical truth already covers this proposal",
            gate_id=GATE_ID,
            clause="CEL-08",
            subject=proposal.subject,
            reuse_targets=list(verdict.reuse_targets),
            incumbents=[i.to_dict() for i in verdict.incumbents],
        )
    return verdict


def proposal_for(record: ConstitutionalMetadata) -> Proposal:
    """Read a proposal out of a completed declaration.

    Lets the gateway run the assimilation gate over an incoming declaration without the
    caller restating what it already declared — the same values, read once.
    """
    return Proposal(
        subject=record.subject,
        owner=record.canonical_owner,
        outputs=record.entries("outputs"),
        inputs=record.entries("inputs"),
        intent=f"declared by {record.universal_id or 'an unidentified subject'}",
    )


def duplicate_capabilities(population: Population) -> dict[str, tuple[str, ...]]:
    """Every output declared by more than one subject — CEL-INV-10, measured.

    The population-wide form of the capability search: the gate refuses duplicates at
    admission, and this finds any that entered by another path.
    """
    producers: dict[str, list[str]] = {}
    for record in population:
        for output in record.entries("outputs"):
            producers.setdefault(output, []).append(record.subject)
    return {
        output: tuple(sorted(subjects))
        for output, subjects in sorted(producers.items())
        if len(subjects) > 1
    }


def to_document() -> dict[str, Any]:
    """The search set as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-assimilation-gate",
        "version": ASSIMILATION_VERSION,
        "gate_id": GATE_ID,
        "searches": [s.to_dict() for s in SEARCHES],
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "ASSIMILATION_VERSION",
    "GATE_ID",
    "SEARCHES",
    "AssimilationVerdict",
    "Incumbent",
    "Proposal",
    "Search",
    "SearchFunction",
    "assimilate",
    "digest",
    "duplicate_capabilities",
    "proposal_for",
    "require_creatable",
    "to_document",
]
