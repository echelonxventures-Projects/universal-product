"""UCON-000001 Part 05 — the construct registry. It has no refusal path, and that is the point.

Read the public surface and notice what is missing: there is no ``reject()``, no ``refuse()``
and no code path in :meth:`ConstructRegistry.present` that returns without recording. A
construct whose classifying kind is unregistered is recorded. A construct that contradicts
another is recorded. A construct that is undecidable, unattributed, malformed against its
facet, or of a category this repository has never heard of is recorded. The disposition decides
what the construct may *do*; it never decides whether the construct *exists in the record*.

That inversion is the whole design. Before it, an unknown kind raised
``MetaTypeUnknownError`` and the construct left no trace — so "we refused it" and "we never
saw it" were the same observable state, and nothing downstream could tell a governed refusal
from a silent drop. Now the two are different: a refusal is a REJECT record naming the rule
and rationale that produced it, and a drop is impossible, because
:attr:`ConstructRegistry.presented` counts presentations and law UCON-L-05 compares that count
to the population. A registry that could lose a construct would fail its own arithmetic.

Openness is derived, never tabulated. :attr:`registered_kinds` is computed by scanning the
constructs of the reflective kind — it consults no list — exactly as
``engine/kernel/registry.py::metatype_exists`` does. The seed kinds in the declaration are not
a privileged table either: :meth:`bootstrap` presents each one through the same
:meth:`present` an unknown category would travel, with the declaration as its evidence. There
is therefore no code path that admits a founding kind and no code path that admits any other,
which is what makes "a future category is one registration" mechanically true rather than
documented.

History is appended to and never rewritten. A re-disposition supersedes the previous record
and keeps it; a re-assessment does the same. The journal is hash-chained from a genesis of
sixty-four zeros, so a retroactive edit or a reordering breaks :meth:`chain_is_intact` rather
than passing quietly. No clock is read anywhere: ordering is a sequence the registry assigns,
because a wall-clock ordering would make two identical runs produce different bytes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from engine.construct import disposition as disposition_engine
from engine.construct import reality as reality_engine
from engine.construct.declaration import Declaration, load_declaration
from engine.construct.model import (
    Construct,
    ConstructError,
    DispositionRecord,
    Evidence,
    Lineage,
    Presentation,
)
from engine.uckp.canonical import canonical_json, content_hash

#: The head of an empty chain. Sixty-four zeros, so a genesis entry is distinguishable from a
#: missing one rather than both rendering as an absent field.
GENESIS = "0" * 64

#: The facet names the registry derives behaviour from. Structural: these are the facets whose
#: payloads this module reads in order to compute the disposition context, and they are read
#: from the declaration's facet table, never invented here.
_CONTRADICTION_FACET = "contradiction"
_RESEARCH_FACET = "research"


class RegistryError(ConstructError):
    """A registry operation the model forbids — an unknown identity, a broken chain."""


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """One hash-chained record of a governed act. Tamper-evident, clock-free."""

    sequence: int
    identity: str
    event: str
    disposition: str
    reality_status: str
    content_digest: str
    prev_hash: str
    entry_hash: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "entry_hash", content_hash(self.body()))

    def body(self) -> dict[str, Any]:
        """The hashed body. ``prev_hash`` is inside it, which is what chains the journal."""
        return {
            "content_digest": self.content_digest,
            "disposition": self.disposition,
            "event": self.event,
            "identity": self.identity,
            "prev_hash": self.prev_hash,
            "reality_status": self.reality_status,
            "sequence": self.sequence,
        }

    def as_dict(self) -> dict[str, Any]:
        return {**self.body(), "entry_hash": self.entry_hash}


class ConstructRegistry:
    """The one home for presented constructs. Append-only, derived-open, and total.

    Not frozen: it is an engine, and the values it holds are the frozen ones. Every read
    accessor returns a sorted, immutable projection, so two registries built by the same calls
    render identical bytes.
    """

    def __init__(self, declaration: Declaration | None = None, *, bootstrap: bool = True) -> None:
        self._declaration = declaration if declaration is not None else load_declaration()
        self._constructs: dict[str, Construct] = {}
        self._journal: list[JournalEntry] = []
        self._presented = 0
        if bootstrap:
            self.bootstrap()

    # --- declaration and openness ----------------------------------------------------------

    @property
    def declaration(self) -> Declaration:
        return self._declaration

    @property
    def presented(self) -> int:
        """How many presentations were made. Compared to the population by law UCON-L-05."""
        return self._presented

    @property
    def registered_kinds(self) -> frozenset[str]:
        """The kinds that have been registered, derived from the record and nothing else.

        The reflective root is always a member: it classifies itself, which is the fixed point
        that lets the very first registration happen at all. Every other kind is here because a
        construct of the reflective kind was presented AND its disposition is one the declaration
        says makes a registration effective — a set that is declared rather than written here,
        because a disposition name in this module would be exactly the undeclared policy the
        capability exists to inventory.
        """
        root = self._declaration.reflective_root
        effective = self._declaration.registration_dispositions
        registered = {root}
        for construct in self._constructs.values():
            if construct.kind == root and construct.disposition.disposition in effective:
                registered.add(construct.presentation.natural_key)
        return frozenset(registered)

    def facet_of(self, kind: str) -> str:
        """The facet a kind carries — from the declaration, else from its registration.

        A runtime-registered kind declares its own facet in the payload of the construct that
        registered it. A kind that declares none carries the uninterpreted facet, which is the
        conservative answer: the foundation reads no field it was not told about.
        """
        for spec in self._declaration.kinds:
            if spec.kind == kind:
                return spec.facet
        root = self._declaration.reflective_root
        for construct in self._constructs.values():
            if construct.kind == root and construct.presentation.natural_key == kind:
                declared = construct.presentation.payload.get("facet")
                if isinstance(declared, str) and declared in self._declaration.facets:
                    return declared
        return "none"

    # --- the disposition context ------------------------------------------------------------

    def contradicted(self) -> frozenset[str]:
        """Identities named by a contradiction whose resolution state is still contradicting.

        Which resolution states contradict is DECLARED (``contradicting`` on each state), not
        decided here. A membership test in this module would have been an undeclared policy
        sitting exactly where nobody would look for it.
        """
        named: set[str] = set()
        for construct in self._constructs.values():
            if self.facet_of(construct.kind) != _CONTRADICTION_FACET:
                continue
            state = str(construct.presentation.payload.get("resolution_state") or "")
            if state not in self._declaration.contradicting_states:
                continue
            for side in ("left", "right"):
                value = construct.presentation.payload.get(side)
                if isinstance(value, str) and value:
                    named.add(value)
        return frozenset(named)

    def research_states(self) -> Mapping[str, str]:
        """Every research construct's declared research state, by identity."""
        return {
            construct.identity: str(construct.presentation.payload.get("research_state") or "")
            for construct in self._constructs.values()
            if self.facet_of(construct.kind) == _RESEARCH_FACET
        }

    def context(self, *, reality_status: str = "") -> disposition_engine.Context:
        """The read-only view the disposition engine is given. Rebuilt per presentation.

        Rebuilt rather than cached because a contradiction registered a moment ago must affect
        the next presentation. A cached context is how a governance decision comes to be made
        against a world that no longer exists.
        """
        return disposition_engine.Context(
            registered_kinds=self.registered_kinds,
            registered_identities=frozenset(self._constructs),
            contradicted=self.contradicted(),
            research_states=self.research_states(),
            reality_status=reality_status,
        )

    # --- presentation -------------------------------------------------------------------------

    def facet_violations(self, presentation: Presentation) -> tuple[str, ...]:
        """Required facet fields the payload did not supply. A record, never a refusal.

        An unknown presented without its formulation is still an unknown somebody presented.
        Refusing it would destroy the only evidence that the attempt was made, so the violation
        travels with the construct instead and makes whatever disposition it receives
        actionable.
        """
        facet = self._declaration.facet(self.facet_of(presentation.kind))
        return tuple(
            f"{facet.name}.{name} is required and absent"
            for name in facet.required_fields
            if name not in presentation.payload
        )

    def present(self, presentation: Presentation) -> Construct:
        """Record ``presentation``, assess it, dispose it, and return the construct.

        There is no branch here that declines. Re-presenting an identity that is already held
        supersedes its disposition and assessment and keeps both histories, so presentation is
        idempotent in identity and cumulative in history.
        """
        if not isinstance(presentation, Presentation):
            raise RegistryError("only a Presentation may be presented")
        self._presented += 1
        identity = presentation.identity
        existing = self._constructs.get(identity)
        base = len(existing.dispositions) if existing else 0
        assessment = reality_engine.assess(self._declaration, presentation, sequence=base)
        record = disposition_engine.dispose(
            self._declaration,
            presentation,
            context=self.context(reality_status=assessment.status),
            sequence=base,
        )
        if existing is None:
            construct = Construct(
                presentation=presentation,
                dispositions=(record,),
                assessments=(assessment,),
                kind_registered=presentation.kind in self.registered_kinds,
                facet_violations=self.facet_violations(presentation),
            )
            event = "presented"
        else:
            construct = Construct(
                presentation=presentation,
                dispositions=(
                    *(item.superseded(record.record_id) for item in existing.dispositions),
                    record,
                ),
                assessments=(
                    *(item.superseded(assessment.record_id) for item in existing.assessments),
                    assessment,
                ),
                kind_registered=presentation.kind in self.registered_kinds,
                facet_violations=self.facet_violations(presentation),
            )
            event = "re-presented"
        self._constructs[identity] = construct
        self._append(construct, event)
        return construct

    def present_all(self, presentations: Iterable[Presentation]) -> tuple[Construct, ...]:
        """Present many, in order. Returns one construct per presentation, none dropped."""
        return tuple(self.present(presentation) for presentation in presentations)

    # --- governed change ---------------------------------------------------------------------

    def redispose(
        self, identity: str, *, disposition: str, rule_id: str, rationale: str
    ) -> Construct:
        """Supersede the active disposition. The declared successor graph is enforced.

        A disposition the current one does not name as a successor is refused, which is what
        makes the disposition lifecycle a lifecycle. The previous record is retained and marked
        superseded, so the history of how a construct came to be where it is stays readable.
        """
        construct = self.get(identity)
        current = construct.disposition
        spec = self._declaration.disposition(current.disposition)
        if disposition not in spec.successors:
            raise RegistryError(
                f"{identity}: {current.disposition} -> {disposition} is not a declared "
                f"successor; declared successors are {', '.join(spec.successors) or 'none'}"
            )
        self._declaration.disposition(disposition)
        record = DispositionRecord(
            identity=identity,
            disposition=disposition,
            rule_id=rule_id,
            rationale=rationale,
            sequence=len(construct.dispositions),
            inputs_digest=construct.presentation.content_digest(),
        )
        updated = Construct(
            presentation=construct.presentation,
            dispositions=(
                *(item.superseded(record.record_id) for item in construct.dispositions),
                record,
            ),
            assessments=construct.assessments,
            kind_registered=construct.kind_registered,
            facet_violations=construct.facet_violations,
        )
        self._constructs[identity] = updated
        self._append(updated, "redisposed")
        return updated

    def reassess(
        self,
        identity: str,
        to_status: str,
        *,
        evidence: Iterable[Evidence] | None = None,
    ) -> Construct:
        """Supersede the active reality assessment along a declared transition.

        Note what this method cannot do: it takes no disposition argument and touches no
        disposition record. Evidence changes what the evidence supports; it does not
        re-admit anything. Re-admission is :meth:`redispose`, and the two acts stay separate
        because collapsing them is exactly how "verified" comes to mean "allowed".
        """
        construct = self.get(identity)
        offered = tuple(evidence or ())
        updated_assessment = reality_engine.transition(
            self._declaration,
            construct.reality,
            to_status,
            sequence=len(construct.assessments),
            evidence_count=(construct.reality.evidence_count + len(offered) if offered else None),
            independent_sources=(
                construct.reality.independent_sources
                + len({item.source for item in offered if item.independent})
                if offered
                else None
            ),
            assessed_from=(
                (*construct.reality.assessed_from, *(item.evidence_id for item in offered))
                if offered
                else None
            ),
        )
        updated = Construct(
            presentation=construct.presentation,
            dispositions=construct.dispositions,
            assessments=(
                *(item.superseded(updated_assessment.record_id) for item in construct.assessments),
                updated_assessment,
            ),
            kind_registered=construct.kind_registered,
            facet_violations=construct.facet_violations,
        )
        self._constructs[identity] = updated
        self._append(updated, "reassessed")
        return updated

    # --- governed extension of the declaration itself --------------------------------------

    def adopt(self, declaration: Declaration) -> Declaration:
        """Swap in an extended declaration, refusing any narrowing of what was already declared.

        This is the one way the vocabularies grow at runtime, and the refusal is what makes the
        growth trustworthy. An extension must be *additive*: every kind, disposition and reality
        state previously declared must still be present and byte-identical afterwards. A
        declaration that dropped a member, or redefined one, would retroactively change the
        meaning of records already in the registry — a construct disposed under a definition
        that no longer exists is a construct whose disposition can no longer be read.

        Returns the adopted declaration so callers can chain, and raises rather than silently
        keeping the old one: an extension that appeared to succeed and did not is worse than one
        that failed loudly.
        """
        if not isinstance(declaration, Declaration):
            raise RegistryError("only a Declaration may be adopted")
        current = self._declaration
        if declaration.artifact_id != current.artifact_id:
            raise RegistryError(
                f"cannot adopt a declaration from a different artifact "
                f"({declaration.artifact_id!r} != {current.artifact_id!r})"
            )
        narrowings: list[str] = []
        for spec in current.kinds:
            if spec not in declaration.kinds:
                narrowings.append(f"kind {spec.kind!r} was declared and is absent or altered")
        for spec in current.dispositions:
            if spec not in declaration.dispositions:
                narrowings.append(
                    f"disposition {spec.identifier!r} was declared and is absent or altered"
                )
        for spec in current.reality_states:
            if spec not in declaration.reality_states:
                narrowings.append(
                    f"reality state {spec.identifier!r} was declared and is absent or altered"
                )
        for law in current.laws:
            if law not in declaration.laws:
                narrowings.append(f"law {law.law_id!r} was declared and is absent or altered")
        if narrowings:
            raise RegistryError("an extension may only add:\n  " + "\n  ".join(sorted(narrowings)))
        self._declaration = declaration
        return declaration

    # --- reads ---------------------------------------------------------------------------------

    def has(self, identity: str) -> bool:
        return identity in self._constructs

    def get(self, identity: str) -> Construct:
        """The construct, or raise. Absence is a fault to the caller, never a silent None."""
        construct = self._constructs.get(identity)
        if construct is None:
            raise RegistryError(f"no construct is registered under {identity!r}")
        return construct

    def all(self) -> tuple[Construct, ...]:
        """Every construct, ordered by identity so the projection is byte-stable."""
        return tuple(self._constructs[key] for key in sorted(self._constructs))

    def of_kind(self, kind: str) -> tuple[Construct, ...]:
        return tuple(c for c in self.all() if c.kind == kind)

    def of_facet(self, facet: str) -> tuple[Construct, ...]:
        return tuple(c for c in self.all() if self.facet_of(c.kind) == facet)

    def with_disposition(self, disposition: str) -> tuple[Construct, ...]:
        return tuple(c for c in self.all() if c.disposition.disposition == disposition)

    def with_reality(self, status: str) -> tuple[Construct, ...]:
        return tuple(c for c in self.all() if c.reality.status == status)

    @property
    def journal(self) -> tuple[JournalEntry, ...]:
        return tuple(self._journal)

    def undisposed(self) -> tuple[str, ...]:
        """Identities carrying no active disposition. Structurally always empty.

        It is measured anyway, because the value of UCON-L-01 is that it is *computed* rather
        than argued from the constructor. A model invariant that nothing ever checks is a model
        invariant that survives its own refactor.
        """
        return tuple(
            identity
            for identity, construct in sorted(self._constructs.items())
            if len([r for r in construct.dispositions if r.active]) != 1
        )

    # --- integrity ------------------------------------------------------------------------------

    def _append(self, construct: Construct, event: str) -> None:
        prev = self._journal[-1].entry_hash if self._journal else GENESIS
        self._journal.append(
            JournalEntry(
                sequence=len(self._journal),
                identity=construct.identity,
                event=event,
                disposition=construct.disposition.disposition,
                reality_status=construct.reality.status,
                content_digest=construct.presentation.content_digest(),
                prev_hash=prev,
            )
        )

    def chain_is_intact(self) -> bool:
        """True iff every entry links to its predecessor and no body was edited."""
        expected = GENESIS
        for index, entry in enumerate(self._journal):
            if entry.sequence != index or entry.prev_hash != expected:
                return False
            if entry.entry_hash != content_hash(entry.body()):
                return False
            expected = entry.entry_hash
        return True

    def verify(self) -> dict[str, Any]:
        """The registry's own measurement: nothing dropped, everything disposed, chain intact."""
        undisposed = self.undisposed()
        return {
            "chain_intact": self.chain_is_intact(),
            "constructs": len(self._constructs),
            "journal_entries": len(self._journal),
            "presented": self._presented,
            "undisposed": list(undisposed),
            "status": (
                "PASS"
                if self.chain_is_intact()
                and not undisposed
                and self._presented >= len(self._constructs)
                else "FAIL"
            ),
        }

    def summary(self) -> dict[str, Any]:
        """A deterministic account of the population, for evidence and for the gate."""
        dispositions = {name: 0 for name in self._declaration.disposition_ids}
        realities = {name: 0 for name in self._declaration.reality_ids}
        kinds: dict[str, int] = {}
        violations: dict[str, list[str]] = {}
        for construct in self.all():
            dispositions[construct.disposition.disposition] = (
                dispositions.get(construct.disposition.disposition, 0) + 1
            )
            realities[construct.reality.status] = realities.get(construct.reality.status, 0) + 1
            kinds[construct.kind] = kinds.get(construct.kind, 0) + 1
            if construct.facet_violations:
                violations[construct.identity] = list(construct.facet_violations)
        return {
            "chain_head": self._journal[-1].entry_hash if self._journal else GENESIS,
            "constructs": len(self._constructs),
            "dispositions": dict(sorted(dispositions.items())),
            "facet_violations": dict(sorted(violations.items())),
            "kinds": dict(sorted(kinds.items())),
            "presented": self._presented,
            "reality_states": dict(sorted(realities.items())),
            "registered_kinds": sorted(self.registered_kinds),
        }

    def digest(self) -> str:
        """A content address over the whole population. Two equal registries hash equally."""
        return content_hash([construct.as_dict() for construct in self.all()])

    def rendered(self) -> str:
        return canonical_json([construct.as_dict() for construct in self.all()])

    # --- bootstrap ---------------------------------------------------------------------------

    def bootstrap(self) -> tuple[Construct, ...]:
        """Register the declared seed kinds through the ordinary presentation path.

        The reflective root goes first because it classifies itself; every other seed kind then
        travels the same :meth:`present` an unknown category would. There is deliberately no
        privileged insert here — if there were, "a founding kind" and "a future kind" would take
        different paths and the openness proof in law UCON-L-08 would be measuring the wrong one.
        """
        root = self._declaration.reflective_root
        ordered = sorted(self._declaration.kinds, key=lambda spec: (spec.kind != root, spec.kind))
        admitted: list[Construct] = []
        for spec in ordered:
            admitted.append(
                self.present(
                    Presentation(
                        kind=root,
                        natural_key=spec.kind,
                        title=spec.title,
                        payload={
                            "definition": spec.definition,
                            "facet": spec.facet,
                            **({"parent": spec.parent} if spec.parent else {}),
                        },
                        evidence=(
                            Evidence(
                                source=self._declaration.artifact_id,
                                statement=f"declared construct kind {spec.kind!r}",
                            ),
                        ),
                        reality_status=self._declaration.seed_reality_state,
                        lineage=Lineage(presented_by=self._declaration.artifact_id),
                    )
                )
            )
        return tuple(admitted)


__all__ = [
    "GENESIS",
    "ConstructRegistry",
    "JournalEntry",
    "RegistryError",
]
