"""UCOS-CMM-000001 — the Constitutional Metadata Mandate (Requirement 009).

CEL-09 states the rule; this module is the only place it is *representable*. An artifact
does not become governable because a document says it should be — it becomes governable
when it has declared the fifteen things a governor needs in order to govern it, and when
something refuses to run it until it has.

Why the facets are data
-----------------------
:data:`MANDATED_FACETS` is a tuple. Every other module in this package reads facets
through :func:`facet` and :meth:`ConstitutionalMetadata.entries` and none of them names a
specific facet in a conditional, so a sixteenth constitutional obligation is one appended
entry here — the graph, the legality engine, the planner, the gateway and the acceptance
gate all pick it up without an edit. That is the same open-by-registration discipline the
vocabulary, ordering and identifier authorities already use.

Referents
---------
Facets marked :attr:`Facet.graph_bearing` carry *subject references*. This is what makes
one uniform mechanism serve every relation the directive names: the dependency graph, the
authority graph, the certification graph and the ownership graph are the same derivation
applied to different facets, so there is no second graph builder to drift from the first.
An entry that does not resolve to a registered subject is not silently a free-text note —
:mod:`engine.constitution.dependency` reports it as an unknown referent (CEL-INV-02).

Why external references exist
-----------------------------
Two rules collide if every reference must resolve inside the population. CEL-09 makes the
certification facet mandatory, so every subject names a certifier; CEL-05 makes the
certification relation acyclic, so no chain of certifiers may close. In a finite
population those two cannot both hold: an acyclic relation must have a last node, and a
last node has nobody to name. The same regress applies to authority, governance and
registration.

Real constitutions terminate the regress the same way this module does — at an authority
that is *named but external*: a founding determination, a standards body, a law that
nobody certifies because it is what certification is measured against. An entry prefixed
:data:`EXTERNAL_PREFIX` is such a reference. It is recorded, it is evidence, and it
satisfies the facet — but it is not an edge, so it can neither dangle nor close a cycle.

The prefix is deliberately explicit rather than inferred from "this key isn't in the
population". Inferring it would make every typo'd subject key a silent external authority,
which is precisely the bypass this package exists to close.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.constitution.errors import ConstitutionalError, MetadataIncomplete
from engine.registry.universal.identity import is_well_formed
from engine.uckp.canonical import content_hash

#: The identity of the metadata mandate this module realises.
MANDATE_ID = "UCOS-CMM-000001"

#: Versioned so facets can be *appended* without any prior declaration changing meaning.
MANDATE_VERSION = "1.0.0"

#: The marker that makes a facet entry an *external* authority rather than a subject
#: reference: the terminator of the authority regress. See the module docstring.
EXTERNAL_PREFIX = "ext:"


def is_external(entry: str) -> bool:
    """True iff ``entry`` names an authority outside the population."""
    return entry.startswith(EXTERNAL_PREFIX)


@dataclass(frozen=True, slots=True)
class Facet:
    """One mandated metadata facet: what an artifact must declare, and what it means."""

    facet_id: str
    statement: str
    #: ``"one"`` — exactly one entry; ``"many"`` — one or more entries.
    cardinality: str = "many"
    #: True iff entries are references to other subjects, and so form a relation.
    graph_bearing: bool = False
    #: False iff absence is reported but does not by itself refuse execution.
    blocking: bool = True

    @property
    def singular(self) -> bool:
        return self.cardinality == "one"

    def to_dict(self) -> dict[str, Any]:
        return {
            "facet_id": self.facet_id,
            "statement": self.statement,
            "cardinality": self.cardinality,
            "graph_bearing": self.graph_bearing,
            "blocking": self.blocking,
        }


#: The fifteen mandated facets (DATA — extend by appending, never edit).
MANDATED_FACETS: tuple[Facet, ...] = (
    Facet(
        "canonical_owner",
        "The single nucleus that owns this artifact. Exactly one, never zero, never two.",
        cardinality="one",
        graph_bearing=True,
    ),
    Facet(
        "authorities",
        "The subjects whose authority this artifact acts under.",
        graph_bearing=True,
    ),
    Facet(
        "dependencies",
        "The subjects that must be complete before this artifact may execute.",
        graph_bearing=True,
    ),
    Facet(
        "constraints",
        "The conditions this artifact must hold within, expressed so they can be checked.",
    ),
    Facet(
        "inputs",
        "What this artifact consumes.",
    ),
    Facet(
        "outputs",
        "What this artifact produces. Two artifacts declaring the same output are a "
        "duplicate capability (CEL-INV-10).",
    ),
    Facet(
        "registrations",
        "The registries this artifact is registered in.",
        graph_bearing=True,
    ),
    Facet(
        "certifications",
        "The subjects that certify this artifact. A subject may not appear in its own.",
        graph_bearing=True,
    ),
    Facet(
        "validation_rules",
        "The rules that decide whether this artifact is well-formed.",
        graph_bearing=True,
    ),
    Facet(
        "verification_rules",
        "The rules that decide whether this artifact does what it declares.",
        graph_bearing=True,
    ),
    Facet(
        "replay_rules",
        "The rules under which this artifact's execution must reproduce byte-identically.",
    ),
    Facet(
        "governance_rules",
        "The rules under which this artifact is governed, and by which it is ratified.",
        graph_bearing=True,
    ),
    Facet(
        "evolution_rules",
        "The rules under which this artifact may change, and what must not regress.",
    ),
    Facet(
        "lineage_rules",
        "The rules recording where this artifact came from and what it supersedes.",
    ),
    Facet(
        "traceability_rules",
        "The rules linking this artifact to the determination that required it.",
    ),
)

#: ``facet_id → Facet`` for lookup.
_BY_ID: Mapping[str, Facet] = {f.facet_id: f for f in MANDATED_FACETS}


def facet(facet_id: str) -> Facet:
    """Return the mandated facet or fail closed."""
    found = _BY_ID.get(facet_id)
    if found is None:
        raise ConstitutionalError(
            "no such mandated metadata facet",
            facet_id=facet_id,
            allowed=[f.facet_id for f in MANDATED_FACETS],
        )
    return found


def facet_ids() -> tuple[str, ...]:
    """Every mandated facet id, in declaration order."""
    return tuple(f.facet_id for f in MANDATED_FACETS)


def graph_bearing_facets() -> tuple[str, ...]:
    """The facets whose entries are subject references, and so form relations."""
    return tuple(f.facet_id for f in MANDATED_FACETS if f.graph_bearing)


def _normalize(entries: Any, *, facet_id: str) -> tuple[str, ...]:
    """Coerce a facet's declared value to an ordered, de-duplicated tuple of tokens."""
    if entries is None:
        return ()
    if isinstance(entries, str):
        candidates: Sequence[Any] = (entries,)
    elif isinstance(entries, Iterable):
        candidates = tuple(entries)
    else:
        raise ConstitutionalError(
            "a metadata facet must be a string or an iterable of strings",
            facet_id=facet_id,
            value=repr(entries),
        )
    seen: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, str):
            raise ConstitutionalError(
                "a metadata facet entry must be a string",
                facet_id=facet_id,
                value=repr(candidate),
            )
        token = candidate.strip()
        if token and token not in seen:
            seen.append(token)
    return tuple(seen)


@dataclass(frozen=True, slots=True)
class ConstitutionalMetadata:
    """The complete constitutional declaration of one executable artifact.

    Construct through :meth:`declare`, which normalises and validates the facet values.
    The dataclass itself stays a plain, hashable record so it can be carried in evidence
    and re-read from a document without a second parsing path.
    """

    subject: str
    universal_id: str
    facets: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    @classmethod
    def declare(
        cls,
        subject: str,
        *,
        universal_id: str,
        **facet_values: Any,
    ) -> ConstitutionalMetadata:
        """Declare metadata for ``subject``.

        Unknown facet names are refused rather than ignored: a typo'd facet would
        otherwise read as a *silently absent* obligation, which is exactly the failure
        mode CEL-09 exists to remove.
        """
        if not isinstance(subject, str) or not subject.strip():
            raise ConstitutionalError("a metadata declaration must name its subject")
        unknown = sorted(set(facet_values) - set(_BY_ID))
        if unknown:
            raise ConstitutionalError(
                "unknown metadata facet declared",
                subject=subject.strip(),
                unknown=unknown,
                allowed=list(facet_ids()),
            )
        normalized = {
            facet_id: _normalize(facet_values.get(facet_id), facet_id=facet_id)
            for facet_id in facet_ids()
        }
        return cls(
            subject=subject.strip(),
            universal_id=str(universal_id).strip(),
            facets=normalized,
        )

    def entries(self, facet_id: str) -> tuple[str, ...]:
        """The declared entries of one facet — empty when undeclared."""
        facet(facet_id)
        return tuple(self.facets.get(facet_id, ()))

    @property
    def canonical_owner(self) -> str:
        """The single declared owner, or the empty string when none is declared.

        May be an external reference: a root subject is owned by the determination that
        required it, which is a real owner even though it is not a declared subject.
        """
        owners = self.entries("canonical_owner")
        return owners[0] if len(owners) == 1 else ""

    def missing_facets(self) -> tuple[str, ...]:
        """The blocking facets this artifact has not satisfied, ordered."""
        missing: list[str] = []
        for item in MANDATED_FACETS:
            if not item.blocking:
                continue
            declared = self.entries(item.facet_id)
            if not declared or (item.singular and len(declared) != 1):
                missing.append(item.facet_id)
        return tuple(missing)

    @property
    def identity_well_formed(self) -> bool:
        """True iff the universal identifier is one the identity authority could mint."""
        return is_well_formed(self.universal_id)

    @property
    def complete(self) -> bool:
        """True iff every blocking facet is satisfied at its declared cardinality."""
        return not self.missing_facets()

    # CEL-09 grants the four faculties together and withdraws them together: an artifact
    # that cannot be governed cannot meaningfully be certified either, so these are one
    # predicate under four names rather than four independent checks.
    @property
    def executable(self) -> bool:
        return self.complete

    @property
    def governable(self) -> bool:
        return self.complete

    @property
    def certifiable(self) -> bool:
        return self.complete

    @property
    def registerable(self) -> bool:
        return self.complete

    def referents(self, facet_id: str) -> tuple[str, ...]:
        """The *subject* references carried by one graph-bearing facet.

        External references are excluded: they terminate the authority regress and so must
        not become edges, or the graph would demand that the founding determination itself
        be a registered subject with a certifier of its own.

        A facet that carries no references returns empty rather than raising: callers
        sweep every facet uniformly, and a non-graph facet contributing no edges is the
        correct answer, not an error.
        """
        if not facet(facet_id).graph_bearing:
            return ()
        return tuple(entry for entry in self.entries(facet_id) if not is_external(entry))

    def external_references(self, facet_id: str) -> tuple[str, ...]:
        """The external authorities named by one facet — recorded, never resolved."""
        return tuple(entry for entry in self.entries(facet_id) if is_external(entry))

    def terminal_facets(self) -> tuple[str, ...]:
        """The graph-bearing facets this subject terminates externally, ordered.

        Reported rather than hidden: a subject terminating *every* authority facet
        externally has declared itself accountable to nothing inside the repository, which
        is lawful for a root and suspicious anywhere else.
        """
        return tuple(
            facet_id
            for facet_id in graph_bearing_facets()
            if self.external_references(facet_id) and not self.referents(facet_id)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-metadata",
            "version": MANDATE_VERSION,
            "mandate_id": MANDATE_ID,
            "subject": self.subject,
            "universal_id": self.universal_id,
            "complete": self.complete,
            "missing_facets": list(self.missing_facets()),
            "terminal_facets": list(self.terminal_facets()),
            "facets": {facet_id: list(self.entries(facet_id)) for facet_id in facet_ids()},
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def require_complete(metadata: ConstitutionalMetadata) -> ConstitutionalMetadata:
    """Return ``metadata`` if it is complete, else refuse — the fail-closed entry point.

    Raises:
        MetadataIncomplete: a blocking facet is absent, so the artifact is not executable,
            not governable, not certifiable and not registerable.
    """
    missing = metadata.missing_facets()
    if missing:
        raise MetadataIncomplete(
            "artifact is not executable: mandated metadata is incomplete",
            mandate_id=MANDATE_ID,
            subject=metadata.subject,
            missing_facets=list(missing),
        )
    return metadata


@dataclass(frozen=True, slots=True)
class Population:
    """A set of declared artifacts — the unit of repository truth this package reasons over.

    Every engine in this package takes a population and returns a report about it. The
    population is immutable: the only way to obtain a different one is
    :mod:`engine.constitution.gateway`, which is how CEL-04's "direct mutation shall be
    impossible" is a property of the type system rather than a request in a document.
    """

    records: Mapping[str, ConstitutionalMetadata] = field(default_factory=dict)

    @classmethod
    def of(cls, records: Iterable[ConstitutionalMetadata]) -> Population:
        """Build a population, refusing two declarations of the same subject.

        A duplicate subject is refused rather than last-one-wins: two declarations of one
        subject are two truths about it, and CEL-08 admits only one.
        """
        indexed: dict[str, ConstitutionalMetadata] = {}
        for record in records:
            if record.subject in indexed:
                raise ConstitutionalError(
                    "duplicate subject declaration",
                    subject=record.subject,
                )
            indexed[record.subject] = record
        return cls(records=dict(sorted(indexed.items())))

    def __iter__(self) -> Iterator[ConstitutionalMetadata]:
        for key in sorted(self.records):
            yield self.records[key]

    def __len__(self) -> int:
        return len(self.records)

    def __contains__(self, subject: object) -> bool:
        return subject in self.records

    def subjects(self) -> tuple[str, ...]:
        """Every declared subject key, ordered."""
        return tuple(sorted(self.records))

    def get(self, subject: str) -> ConstitutionalMetadata:
        """Return the declaration for ``subject`` or fail closed."""
        found = self.records.get(subject)
        if found is None:
            raise ConstitutionalError("no such declared subject", subject=subject)
        return found

    def with_records(self, records: Iterable[ConstitutionalMetadata]) -> Population:
        """Return a *new* population with ``records`` added or replaced.

        Deliberately not a mutator. The gateway calls this after a mutation has completed
        every stage of its pipeline; nothing else has cause to.
        """
        merged = dict(self.records)
        for record in records:
            merged[record.subject] = record
        return Population(records=dict(sorted(merged.items())))

    def incomplete(self) -> tuple[ConstitutionalMetadata, ...]:
        """Every declaration missing a blocking facet, ordered by subject."""
        return tuple(record for record in self if not record.complete)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-population",
            "version": MANDATE_VERSION,
            "subject_count": len(self.records),
            "subjects": list(self.subjects()),
            "records": [record.to_dict() for record in self],
        }

    def digest(self) -> str:
        """The content digest of the whole population — the state identity DPE seals."""
        return content_hash(self.to_dict())


def to_document() -> dict[str, Any]:
    """The mandate itself as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-metadata-mandate",
        "version": MANDATE_VERSION,
        "mandate_id": MANDATE_ID,
        "facet_count": len(MANDATED_FACETS),
        "facets": [f.to_dict() for f in MANDATED_FACETS],
        "graph_bearing": list(graph_bearing_facets()),
        "external_prefix": EXTERNAL_PREFIX,
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "EXTERNAL_PREFIX",
    "MANDATED_FACETS",
    "MANDATE_ID",
    "MANDATE_VERSION",
    "ConstitutionalMetadata",
    "Facet",
    "Population",
    "digest",
    "facet",
    "facet_ids",
    "graph_bearing_facets",
    "is_external",
    "require_complete",
    "to_document",
]
