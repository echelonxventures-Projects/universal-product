"""UCXI-000001 Part 02 — Context Taxonomy: the classification of all context.

The taxonomy answers exactly one question: *what kind of context is this, and where
does it sit in the classification of all context?* It carries no dimensions, no
values and no structure — those belong to the Ontology (Part 03) — so the two never
duplicate each other.

Two things are provided:

    * :class:`ContextKind` — the sixteen **universal** context kinds (existence,
      reality, observer, temporal, spatial, identity, governance, security,
      knowledge, computational, environmental, economic, regulatory, linguistic,
      cultural, measurement). These are the kinds the platform treats as
      constitutionally present in every situation.
    * :class:`ContextTaxonomy` — an immutable classification **tree** seeded with
      those sixteen universal taxa under a single root, and **open by construction**
      (CXL-02): a *future* context type is admitted through
      :meth:`ContextTaxonomy.extend`, which is a DATA edit, not a code edit. No
      control flow in this layer branches on a specific kind, so a seventeenth,
      hundredth or thousandth context type needs no change here.

Extension is bounded, not permissive: a future taxon must name a parent that already
exists, must not collide with an existing taxon or kind, may not shadow or re-declare
a universal taxon, and may not introduce a cycle. Unknown kinds fail loudly through
:meth:`ContextKind.coerce` rather than silently defaulting (CXL-11 fail-closed).

Standard library only (TP-04/TP-05); the module holds no runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.context.errors import LifecycleTransitionError, TaxonomyError

#: The identifier of the single root of the classification of all context.
ROOT_TAXON = "CTX-ROOT"


class ContextKind(str, Enum):
    """The sixteen universal context kinds (Part 02 §1).

    Universal means *always present*: every situation a system reasons about has an
    existence, reality, observer, temporal, spatial, identity, governance, security,
    knowledge, computational, environmental, economic, regulatory, linguistic,
    cultural and measurement context, even when a given dimension is unknown.
    Absence is expressed as an explicit unknown value, never as a missing kind.

    ``MEASUREMENT`` is the sixteenth, admitted by ADR-0005. Every assertion is made
    in some system of measurement, and a system that leaves that implicit has an
    assumed one — usually SI, usually Earth-human. Naming it as a universal kind
    makes the assumption declarable and therefore replaceable: SI, imperial and any
    future or non-human system are peer entities, none privileged. The kind
    *describes* the frame in force; it grants no authority (CXL-10), and no
    measurement engine exists behind it.

    That the list moved from fifteen to sixteen is itself the evidence the taxonomy
    is open: the seed is data, no control flow in this layer branches on a kind, and
    a seventeenth needs no more than another row.
    """

    EXISTENCE = "existence"
    REALITY = "reality"
    OBSERVER = "observer"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    IDENTITY = "identity"
    GOVERNANCE = "governance"
    SECURITY = "security"
    KNOWLEDGE = "knowledge"
    COMPUTATIONAL = "computational"
    ENVIRONMENTAL = "environmental"
    ECONOMIC = "economic"
    REGULATORY = "regulatory"
    LINGUISTIC = "linguistic"
    CULTURAL = "cultural"
    MEASUREMENT = "measurement"

    @classmethod
    def coerce(cls, value: Any, *, at: str = "context") -> ContextKind:
        """Return the universal kind for ``value`` or raise :class:`TaxonomyError`."""
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value))
        except ValueError as exc:
            raise TaxonomyError(
                "unknown universal context kind",
                value=value,
                at=at,
                allowed=[k.value for k in cls],
            ) from exc

    @classmethod
    def values(cls) -> tuple[str, ...]:
        """Every universal kind value, in declaration order."""
        return tuple(kind.value for kind in cls)


#: Convenience tuple of the sixteen universal kinds in declaration order.
UNIVERSAL_KINDS: tuple[ContextKind, ...] = tuple(ContextKind)


class ContextAuthority(str, Enum):
    """The authority a context assertion carries (Part 02 §2, ordered).

    Precedence is *explicit and total* so composition never resolves a conflict by
    arbitrary order (CXL-07). Two assertions of equal authority that disagree are
    refused, not silently merged.
    """

    CONSTITUTIONAL = "constitutional"
    ARCHITECTURAL = "architectural"
    OPERATIONAL = "operational"
    OBSERVED = "observed"
    INFERRED = "inferred"

    @property
    def rank(self) -> int:
        """Numeric precedence; lower is more authoritative (constitutional = 0)."""
        return _AUTHORITY_ORDER[self]

    def outranks(self, other: ContextAuthority) -> bool:
        """True iff ``self`` is strictly more authoritative than ``other``."""
        return self.rank < other.rank

    @classmethod
    def coerce(cls, value: Any, *, at: str = "context") -> ContextAuthority:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value))
        except ValueError as exc:
            raise TaxonomyError(
                "unknown context authority",
                value=value,
                at=at,
                allowed=[a.value for a in cls],
            ) from exc


_AUTHORITY_ORDER: dict[ContextAuthority, int] = {
    ContextAuthority.CONSTITUTIONAL: 0,
    ContextAuthority.ARCHITECTURAL: 1,
    ContextAuthority.OPERATIONAL: 2,
    ContextAuthority.OBSERVED: 3,
    ContextAuthority.INFERRED: 4,
}


class ContextLifecycle(str, Enum):
    """The lifecycle of a context instance (Part 02 §3) with an enforced graph.

    A context is *declared*, then *registered* (given a canonical identity), then
    *resolved* (its values determined with provenance), then *composed* into a
    bounded frame, then *active* in a runtime, then *released*. Retirement happens
    by supersession or archival — never by mutation in place.
    """

    DECLARED = "declared"
    REGISTERED = "registered"
    RESOLVED = "resolved"
    COMPOSED = "composed"
    ACTIVE = "active"
    RELEASED = "released"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"

    @classmethod
    def coerce(cls, value: Any, *, at: str = "context") -> ContextLifecycle:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value))
        except ValueError as exc:
            raise TaxonomyError(
                "unknown context lifecycle stage",
                value=value,
                at=at,
                allowed=[s.value for s in cls],
            ) from exc

    def can_transition_to(self, target: ContextLifecycle) -> bool:
        """True iff moving from ``self`` to ``target`` is a legal transition."""
        return target in _LIFECYCLE_TRANSITIONS.get(self, frozenset())

    def require_transition(self, target: ContextLifecycle, *, at: str = "context") -> None:
        """Raise :class:`LifecycleTransitionError` if the transition is illegal."""
        if not self.can_transition_to(target):
            raise LifecycleTransitionError(
                "illegal context lifecycle transition",
                at=at,
                current=self.value,
                target=target.value,
                allowed=sorted(t.value for t in _LIFECYCLE_TRANSITIONS.get(self, ())),
            )

    @property
    def is_active(self) -> bool:
        """True iff a context in this stage may participate in resolution."""
        return self in _ACTIVE_STAGES

    @property
    def is_terminal(self) -> bool:
        """True iff no further transition is possible from this stage."""
        return not _LIFECYCLE_TRANSITIONS.get(self)


_LIFECYCLE_TRANSITIONS: dict[ContextLifecycle, frozenset[ContextLifecycle]] = {
    ContextLifecycle.DECLARED: frozenset({ContextLifecycle.REGISTERED, ContextLifecycle.ARCHIVED}),
    ContextLifecycle.REGISTERED: frozenset(
        {ContextLifecycle.RESOLVED, ContextLifecycle.SUPERSEDED, ContextLifecycle.ARCHIVED}
    ),
    ContextLifecycle.RESOLVED: frozenset(
        {ContextLifecycle.COMPOSED, ContextLifecycle.SUPERSEDED, ContextLifecycle.ARCHIVED}
    ),
    ContextLifecycle.COMPOSED: frozenset(
        {ContextLifecycle.ACTIVE, ContextLifecycle.SUPERSEDED, ContextLifecycle.ARCHIVED}
    ),
    ContextLifecycle.ACTIVE: frozenset({ContextLifecycle.RELEASED, ContextLifecycle.SUPERSEDED}),
    ContextLifecycle.RELEASED: frozenset(
        {ContextLifecycle.ACTIVE, ContextLifecycle.SUPERSEDED, ContextLifecycle.ARCHIVED}
    ),
    ContextLifecycle.SUPERSEDED: frozenset({ContextLifecycle.ARCHIVED}),
    ContextLifecycle.ARCHIVED: frozenset(),
}

_ACTIVE_STAGES: frozenset[ContextLifecycle] = frozenset(
    {
        ContextLifecycle.REGISTERED,
        ContextLifecycle.RESOLVED,
        ContextLifecycle.COMPOSED,
        ContextLifecycle.ACTIVE,
    }
)


class ContextRelation(str, Enum):
    """The canonical relationship types of the context graph (Part 02 §4)."""

    CONTAINS = "contains"
    REFINES = "refines"
    DERIVES_FROM = "derives-from"
    DEPENDS_ON = "depends-on"
    CONSTRAINS = "constrains"
    OBSERVES = "observes"
    FEDERATES = "federates"
    SUPERSEDES = "supersedes"
    CLASSIFIED_AS = "classified-as"
    EQUIVALENT_TO = "equivalent-to"
    CONFLICTS_WITH = "conflicts-with"

    @classmethod
    def coerce(cls, value: Any, *, at: str = "relation") -> ContextRelation:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value))
        except ValueError as exc:
            raise TaxonomyError(
                "unknown context relation",
                value=value,
                at=at,
                allowed=[r.value for r in cls],
            ) from exc

    @property
    def is_symmetric(self) -> bool:
        """True iff the relation reads identically in both directions."""
        return self in _SYMMETRIC_RELATIONS

    @property
    def is_hierarchical(self) -> bool:
        """True iff the relation must remain acyclic (a hierarchy, not a web)."""
        return self in _HIERARCHICAL_RELATIONS


_SYMMETRIC_RELATIONS: frozenset[ContextRelation] = frozenset(
    {ContextRelation.EQUIVALENT_TO, ContextRelation.CONFLICTS_WITH}
)

_HIERARCHICAL_RELATIONS: frozenset[ContextRelation] = frozenset(
    {
        ContextRelation.CONTAINS,
        ContextRelation.REFINES,
        ContextRelation.DERIVES_FROM,
        ContextRelation.DEPENDS_ON,
        ContextRelation.SUPERSEDES,
        ContextRelation.CLASSIFIED_AS,
    }
)


# --------------------------------------------------------------------------- #
# The classification tree                                                      #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ContextTaxon:
    """One node of the classification of all context.

    ``kind`` is an open string: a universal taxon carries a :class:`ContextKind`
    value, while a future taxon may declare a kind this release has never seen.
    ``universal`` marks the sixteen constitutionally present taxa, which may never
    be redefined or removed.
    """

    taxon_id: str
    kind: str
    title: str
    parent: str | None = None
    universal: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        for field_name in ("taxon_id", "kind", "title"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise TaxonomyError(
                    "taxon field must be a non-empty string",
                    field=field_name,
                    taxon=self.taxon_id,
                )
        if self.parent is not None and (not isinstance(self.parent, str) or not self.parent):
            raise TaxonomyError(
                "taxon parent must be a non-empty string or None", taxon=self.taxon_id
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "taxon_id": self.taxon_id,
            "kind": self.kind,
            "title": self.title,
            "parent": self.parent,
            "universal": self.universal,
            "description": self.description,
        }


def _universal_taxa() -> tuple[ContextTaxon, ...]:
    """Build the seed tree: the root plus one taxon per universal kind (DATA)."""
    root = ContextTaxon(
        taxon_id=ROOT_TAXON,
        kind="context",
        title="Universal Context",
        parent=None,
        universal=True,
        description="The root of the classification of all context. Every context is a "
        "descendant of this taxon; nothing is unclassified.",
    )
    titles = {
        ContextKind.EXISTENCE: (
            "Existence Context",
            "Whether, in what mode, and on what substrate the subject exists at all.",
        ),
        ContextKind.REALITY: (
            "Reality Context",
            "Whether the subject is actual, modelled, simulated, planned or hypothetical.",
        ),
        ContextKind.OBSERVER: (
            "Observer Context",
            "Who or what observes, from what vantage, with what epistemic access.",
        ),
        ContextKind.TEMPORAL: (
            "Temporal Context",
            "The time frame, ordering and resolution within which the subject holds.",
        ),
        ContextKind.SPATIAL: (
            "Spatial Context",
            "The spatial or topological frame, extent and locality of the subject.",
        ),
        ContextKind.IDENTITY: (
            "Identity Context",
            "Which subject this is, under whose naming authority, with what identifier.",
        ),
        ContextKind.GOVERNANCE: (
            "Governance Context",
            "The authority, policy and decision rights that govern the subject.",
        ),
        ContextKind.SECURITY: (
            "Security Context",
            "Classification, trust boundary and controls applying to the subject.",
        ),
        ContextKind.KNOWLEDGE: (
            "Knowledge Context",
            "The source, provenance and confidence of what is known about the subject.",
        ),
        ContextKind.COMPUTATIONAL: (
            "Computational Context",
            "The execution substrate, resources and computational model in force.",
        ),
        ContextKind.ENVIRONMENTAL: (
            "Environmental Context",
            "The surrounding medium, conditions and physical constraints.",
        ),
        ContextKind.ECONOMIC: (
            "Economic Context",
            "Cost model, value and scarcity conditions bearing on the subject.",
        ),
        ContextKind.REGULATORY: (
            "Regulatory Context",
            "Jurisdiction, obligations and compliance state imposed externally.",
        ),
        ContextKind.LINGUISTIC: (
            "Linguistic Context",
            "Language, register, terminology and encoding in which meaning is carried.",
        ),
        ContextKind.CULTURAL: (
            "Cultural Context",
            "Locale, norms and conventions shaping interpretation and acceptability.",
        ),
        ContextKind.MEASUREMENT: (
            "Measurement Context",
            "The system, units and scale in which a quantity is expressed. No system "
            "is privileged: SI, imperial and any future or non-human system are peers.",
        ),
    }
    taxa = [root]
    for kind in UNIVERSAL_KINDS:
        title, description = titles[kind]
        taxa.append(
            ContextTaxon(
                taxon_id=f"CTX-{kind.value.upper()}",
                kind=kind.value,
                title=title,
                parent=ROOT_TAXON,
                universal=True,
                description=description,
            )
        )
    return tuple(taxa)


#: The seed taxonomy: the root plus the sixteen universal taxa (DATA, not code).
UNIVERSAL_TAXA: tuple[ContextTaxon, ...] = _universal_taxa()


class ContextTaxonomy:
    """An immutable, open classification tree over context kinds.

    The default instance is the universal seed; :meth:`extend` returns a *new*
    taxonomy admitting a future taxon (and, with it, a future context kind). The
    instance is never mutated, so a taxonomy handed to a validator or certifier
    cannot change underneath it.
    """

    __slots__ = ("_taxa", "_children", "_by_kind")

    def __init__(self, taxa: tuple[ContextTaxon, ...] = UNIVERSAL_TAXA) -> None:
        by_id: dict[str, ContextTaxon] = {}
        by_kind: dict[str, str] = {}
        for taxon in taxa:
            if taxon.taxon_id in by_id:
                raise TaxonomyError("duplicate taxon identifier", taxon=taxon.taxon_id)
            if taxon.kind in by_kind and taxon.taxon_id != by_kind[taxon.kind]:
                raise TaxonomyError(
                    "two taxa claim the same context kind",
                    kind=taxon.kind,
                    taxon=taxon.taxon_id,
                    existing=by_kind[taxon.kind],
                )
            by_id[taxon.taxon_id] = taxon
            by_kind[taxon.kind] = taxon.taxon_id

        roots = [t for t in taxa if t.parent is None]
        if len(roots) != 1:
            raise TaxonomyError(
                "the classification of all context has exactly one root",
                roots=sorted(t.taxon_id for t in roots),
            )

        children: dict[str, list[str]] = {tid: [] for tid in by_id}
        for taxon in taxa:
            if taxon.parent is None:
                continue
            if taxon.parent not in by_id:
                raise TaxonomyError(
                    "taxon parent is not a declared taxon (open classification)",
                    taxon=taxon.taxon_id,
                    parent=taxon.parent,
                )
            children[taxon.parent].append(taxon.taxon_id)

        self._taxa: dict[str, ContextTaxon] = dict(sorted(by_id.items()))
        self._children: dict[str, tuple[str, ...]] = {
            tid: tuple(sorted(kids)) for tid, kids in children.items()
        }
        self._by_kind: dict[str, str] = dict(sorted(by_kind.items()))

        # Reachability (no cycle, no detached branch): every taxon reaches the root.
        root_id = roots[0].taxon_id
        for taxon_id in self._taxa:
            self._assert_reaches(taxon_id, root_id)

    # -- construction ------------------------------------------------------- #

    def _assert_reaches(self, taxon_id: str, root_id: str) -> None:
        seen: set[str] = set()
        cursor: str | None = taxon_id
        while cursor is not None:
            if cursor in seen:
                raise TaxonomyError(
                    "cycle in the classification tree",
                    taxon=taxon_id,
                    cycle=sorted(seen),
                )
            seen.add(cursor)
            if cursor == root_id:
                return
            cursor = self._taxa[cursor].parent
        raise TaxonomyError("taxon does not reach the root", taxon=taxon_id)

    def extend(self, taxon: ContextTaxon) -> ContextTaxonomy:
        """Admit a **future context type** and return the extended taxonomy.

        Extension is bounded (CXL-02): the taxon must be new, must name an existing
        parent, may not claim a kind already claimed, and may not be marked
        ``universal`` — universality is constitutional and cannot be granted by
        extension.

        Raises:
            TaxonomyError: the extension is not admissible.
        """
        if taxon.taxon_id in self._taxa:
            raise TaxonomyError("taxon is already classified", taxon=taxon.taxon_id)
        if taxon.universal:
            raise TaxonomyError(
                "universality is constitutional and cannot be granted by extension",
                taxon=taxon.taxon_id,
            )
        if taxon.parent is None:
            raise TaxonomyError(
                "a future taxon must name an existing parent (one root only)",
                taxon=taxon.taxon_id,
            )
        if taxon.parent not in self._taxa:
            raise TaxonomyError(
                "future taxon parent is not classified",
                taxon=taxon.taxon_id,
                parent=taxon.parent,
            )
        if taxon.kind in self._by_kind:
            raise TaxonomyError(
                "context kind is already claimed by another taxon",
                kind=taxon.kind,
                taxon=taxon.taxon_id,
                existing=self._by_kind[taxon.kind],
            )
        return ContextTaxonomy(tuple(self._taxa.values()) + (taxon,))

    # -- lookups ------------------------------------------------------------ #

    def __len__(self) -> int:
        return len(self._taxa)

    def taxon_ids(self) -> tuple[str, ...]:
        """Every taxon identifier, ordered."""
        return tuple(self._taxa)

    def taxa(self) -> tuple[ContextTaxon, ...]:
        """Every taxon, ordered by identifier."""
        return tuple(self._taxa.values())

    def has(self, taxon_id: str) -> bool:
        return taxon_id in self._taxa

    def taxon(self, taxon_id: str) -> ContextTaxon:
        """Return the taxon or raise :class:`TaxonomyError`."""
        try:
            return self._taxa[taxon_id]
        except KeyError as exc:
            raise TaxonomyError("taxon is not classified", taxon=taxon_id) from exc

    def taxon_for_kind(self, kind: str) -> ContextTaxon:
        """Return the taxon that classifies ``kind`` or raise."""
        kind_value = kind.value if isinstance(kind, ContextKind) else str(kind)
        taxon_id = self._by_kind.get(kind_value)
        if taxon_id is None:
            raise TaxonomyError("context kind is not classified", kind=kind_value)
        return self._taxa[taxon_id]

    def kinds(self) -> tuple[str, ...]:
        """Every classified context kind, ordered (universal plus future)."""
        return tuple(k for k in self._by_kind if k != "context")

    def universal_kinds(self) -> tuple[str, ...]:
        """The classified kinds that are constitutionally universal, ordered."""
        return tuple(
            sorted(t.kind for t in self._taxa.values() if t.universal and t.parent is not None)
        )

    def future_kinds(self) -> tuple[str, ...]:
        """The classified kinds admitted by extension, ordered."""
        return tuple(sorted(t.kind for t in self._taxa.values() if not t.universal))

    def is_universal(self, kind: str) -> bool:
        """True iff ``kind`` is one of the constitutionally universal kinds."""
        kind_value = kind.value if isinstance(kind, ContextKind) else str(kind)
        taxon_id = self._by_kind.get(kind_value)
        return taxon_id is not None and self._taxa[taxon_id].universal

    # -- navigation --------------------------------------------------------- #

    def children(self, taxon_id: str) -> tuple[str, ...]:
        """Direct children of ``taxon_id``, ordered."""
        self.taxon(taxon_id)
        return self._children.get(taxon_id, ())

    def ancestors(self, taxon_id: str) -> tuple[str, ...]:
        """Ancestors of ``taxon_id`` from parent up to the root."""
        chain: list[str] = []
        cursor = self.taxon(taxon_id).parent
        while cursor is not None:
            chain.append(cursor)
            cursor = self._taxa[cursor].parent
        return tuple(chain)

    def descendants(self, taxon_id: str) -> tuple[str, ...]:
        """All descendants of ``taxon_id``, ordered (deterministic BFS)."""
        self.taxon(taxon_id)
        out: list[str] = []
        frontier = list(self._children.get(taxon_id, ()))
        while frontier:
            current = frontier.pop(0)
            out.append(current)
            frontier.extend(self._children.get(current, ()))
        return tuple(sorted(out))

    def depth(self, taxon_id: str) -> int:
        """Distance from ``taxon_id`` to the root (root itself is 0)."""
        return len(self.ancestors(taxon_id))

    # -- serialisation ------------------------------------------------------ #

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": next(t.taxon_id for t in self._taxa.values() if t.parent is None),
            "taxa": [t.to_dict() for t in self._taxa.values()],
            "universal_kinds": list(self.universal_kinds()),
            "future_kinds": list(self.future_kinds()),
        }


#: The default, universal taxonomy instance (sixteen universal taxa under one root).
UNIVERSAL_TAXONOMY = ContextTaxonomy()


__all__ = [
    "ROOT_TAXON",
    "ContextKind",
    "ContextAuthority",
    "ContextLifecycle",
    "ContextRelation",
    "ContextTaxon",
    "ContextTaxonomy",
    "UNIVERSAL_KINDS",
    "UNIVERSAL_TAXA",
    "UNIVERSAL_TAXONOMY",
]
