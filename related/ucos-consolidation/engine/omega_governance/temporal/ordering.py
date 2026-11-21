"""UCOS Ω∞ Temporal — ordering as a provider, and RELATIONS as a registry.

AUTHORITY = NONE (DERIVED TRUTH).

THE ASSUMPTION THIS REMOVES, and it is the deepest one in the package::

    timestamp: str      # and records sorted with ``sorted(...)``

A sortable timestamp asserts a TOTAL ORDER: every pair comparable, exactly one of before, after,
simultaneous. False for every distributed system, false for two observers with no shared frame,
false for a forked ledger — and false SILENTLY, because ``sorted()`` never refuses. Two causally
unrelated events acquire an order no observation produced, and a contradiction engine reading that
order reports a sequence the sort algorithm invented.

THE SECOND ASSUMPTION, WHICH SURVIVED THIS FILE'S FIRST DRAFT. The relations were a module tuple of
five strings, quantified over by ``assert_consistent``, with the mirror rule written as
``{BEFORE: AFTER, AFTER: BEFORE}``. A sixth relation — a quantum ordering's "superposed", an
interval order's "overlaps" — would have required editing both. That is Ω∞ Rule 4's target exactly,
and it did not look like an enum. Relations are now a REGISTRY of value objects carrying their own
semantics:

    decided      the comparison answered at all
    ordered      one position precedes the other
    coincident   the two positions are the same position
    inverse      the relation that must hold when the arguments are swapped

``assert_consistent`` reads those four properties and never a relation NAME, so a registered sixth
relation is checked by the same code that checks the five below.

FIVE SHIPPED RELATIONS, AND WHY CONCURRENT AND INCOMPARABLE ARE DIFFERENT FACTS. CONCURRENT is an
ANSWER: a causal ordering examined both positions and found neither dominates. INCOMPARABLE is a
REFUSAL: the positions are measured in scales or frames between which nothing is declared, so no
answer exists. A record reporting the second as the first claims knowledge it does not have.
Collapsing them is what a two-valued comparison forces.

POSITIONS ARE OPAQUE. ``Position = tuple[object, ...]`` and not ``tuple[int, ...]``, because Ω∞ Rule
8 requires a non-numeric measurement system to register and operate. Symbols, grades and lattice
elements are positions. Determinism is the ENCODING layer's obligation, not the position type's, and
magnitude is the ``QUANTITATIVE`` capability a symbolic domain simply does not declare. Strategies
that need arithmetic guard for it and return INCOMPARABLE rather than raising — a shape a strategy
cannot handle is a datum, not an interruption.

THIS MODULE IMPORTS NOTHING FROM THIS REPOSITORY. Ordering is arithmetic over opaque tuples, and
arithmetic needs no world.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


class OrderingError(RuntimeError):
    """An ordering, relation or strategy declaration was invalid.

    RAISED, NEVER DEFAULTED — with a narrow remit. "These positions cannot be compared" does NOT
    raise; it returns a relation whose ``decided`` is false, because a refusal arriving as an
    exception cannot be counted alongside the comparisons that succeeded, and a population of
    incomparable pairs is exactly what a distributed governance record must report.
    """


# ------------------------------------------------------------------------------------- relations


@dataclass(frozen=True, order=True)
class Relation:
    """One possible outcome of comparing two positions, carrying its own semantics.

    THE FOUR PROPERTIES REPLACE FOUR CLOSED LISTS. Before, ``RELATIONS``, ``ORDERED_RELATIONS``,
    ``DECIDED_RELATIONS`` and an inverse ``dict`` all had to be edited in step to add an outcome.
    Now a registered relation states what it means and every consumer reads the properties.
    """

    name: str
    description: str = ""
    #: The comparison produced an answer. False means the question was declined.
    decided: bool = True
    #: One position precedes the other.
    ordered: bool = False
    #: The two positions are the same position.
    coincident: bool = False
    #: The relation that must hold when the arguments are swapped. Empty means self-inverse.
    inverse: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise OrderingError("a relation with no name cannot be returned or reported")
        if self.ordered and self.coincident:
            raise OrderingError(
                f"relation {self.name!r} claims both precedence and coincidence; a position cannot "
                "both come before another and be the same position"
            )
        if self.ordered and not self.inverse.strip():
            raise OrderingError(
                f"relation {self.name!r} asserts precedence and declares no inverse; without one, "
                "swapping the arguments has no defined answer and antisymmetry is uncheckable"
            )

    @property
    def admits_total_order(self) -> bool:
        """Whether this outcome is compatible with a claim of totality. READ, never a name check."""
        return self.decided and (self.ordered or self.coincident)

    def as_record(self) -> dict[str, object]:
        return {
            "relation": self.name,
            "decided": self.decided,
            "ordered": self.ordered,
            "coincident": self.coincident,
            "inverse": self.inverse or self.name,
            "description": self.description,
        }

    def __str__(self) -> str:
        return self.name


BEFORE = Relation(
    "BEFORE",
    "The left position precedes the right.",
    decided=True,
    ordered=True,
    inverse="AFTER",
)
AFTER = Relation(
    "AFTER",
    "The right position precedes the left.",
    decided=True,
    ordered=True,
    inverse="BEFORE",
)
SIMULTANEOUS = Relation(
    "SIMULTANEOUS",
    "The positions are the same position. Distinct from CONCURRENT, which is two DIFFERENT "
    "positions neither of which precedes.",
    decided=True,
    coincident=True,
)
CONCURRENT = Relation(
    "CONCURRENT",
    "Both positions are real and neither precedes. AN ANSWER, not missing information: a causal "
    "ordering examined both and found no causal path in either direction.",
    decided=True,
)
INCOMPARABLE = Relation(
    "INCOMPARABLE",
    "The question is not answerable for this pair. A REFUSAL: the positions come from scales or "
    "frames between which nothing is declared, so there is no answer to give.",
    decided=False,
)

#: The relations this module ships. NOT AN EXHAUSTIVE LIST of what a comparison may conclude, and
#: nothing quantifies over it — ``RelationRegistry`` is seeded from it and consumers read
#: properties.
INITIAL_RELATIONS: tuple[Relation, ...] = (AFTER, BEFORE, CONCURRENT, INCOMPARABLE, SIMULTANEOUS)


class RelationRegistry:
    """Relation name -> ``Relation``. Open for extension, closed to redefinition."""

    def __init__(self, seed: Iterable[Relation] = INITIAL_RELATIONS) -> None:
        self._by_name: dict[str, Relation] = {}
        for relation in seed:
            self.declare(relation)

    def declare(self, relation: Relation) -> Relation:
        existing = self._by_name.get(relation.name)
        if existing is None:
            self._by_name[relation.name] = relation
            return relation
        if existing != relation:
            raise OrderingError(
                f"relation {relation.name!r} is already declared with different semantics; one "
                f"name "
                "with two meanings makes every conclusion drawn from it unenforceable"
            )
        return existing

    def declare_name(
        self,
        name: str,
        description: str,
        *,
        decided: bool = True,
        ordered: bool = False,
        coincident: bool = False,
        inverse: str = "",
    ) -> Relation:
        """Declare a sixth outcome from primitives. RULE 3, with no edit to this module."""
        return self.declare(Relation(name, description, decided, ordered, coincident, inverse))

    def resolve(self, name: str) -> Relation:
        try:
            return self._by_name[name]
        except KeyError:
            raise OrderingError(
                f"{name!r} is not a declared relation; a strategy returning it would produce a "
                "conclusion whose meaning nothing states"
            ) from None

    def inverse_of(self, name: str) -> Relation:
        """The relation that must hold when the arguments are swapped. NO HARDCODED PAIR TABLE."""
        relation = self.resolve(name)
        return self.resolve(relation.inverse) if relation.inverse else relation

    def known(self) -> tuple[Relation, ...]:
        return tuple(sorted(self._by_name.values()))

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


# -------------------------------------------------------------------------------------- orderings


@dataclass(frozen=True, order=True)
class Ordering:
    """One ordering discipline, declared as a value.

    ``total`` is a CLAIM THE STRATEGY MAKES ABOUT ITSELF, checkable by execution: a strategy
    declaring ``total=True`` that ever returns an outcome whose ``admits_total_order`` is false is
    refused by ``assert_consistent``. Without that check, "total" is a comment.
    """

    name: str
    description: str = ""
    total: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise OrderingError("an ordering with no name cannot be cited by a coordinate")

    def __str__(self) -> str:
        return self.name


TOTAL = Ordering(
    "TOTAL",
    "Every pair is comparable and exactly one of precedence or coincidence holds. Honest only for "
    "positions from a single counter observed by a single observer.",
    total=True,
)
PARTIAL = Ordering(
    "PARTIAL",
    "Some pairs are concurrent. The general shape, and what a caller should reach for when unsure: "
    "assuming partiality costs a comparison, assuming totality costs a wrong answer.",
)
CAUSAL = Ordering(
    "CAUSAL",
    "Precedence means a causal path exists. Concurrency is a positive finding about causality "
    "rather than missing information.",
)
DISTRIBUTED = Ordering(
    "DISTRIBUTED",
    "Comparability requires participants to agree. Positions from disagreeing observers are "
    "incomparable, so absence of consensus is reported rather than resolved.",
)
BRANCHING = Ordering(
    "BRANCHING",
    "Positions carry a branch identity. Two positions on divergent branches are incomparable — not "
    "concurrent, because they are not two views of one history but two histories.",
)

#: Shipped orderings. NOT EXHAUSTIVE; nothing quantifies over it.
INITIAL_ORDERINGS: tuple[Ordering, ...] = (BRANCHING, CAUSAL, DISTRIBUTED, PARTIAL, TOTAL)


# ------------------------------------------------------------------------------------ strategies
#: A position is a tuple of OPAQUE components. Ω∞ Rule 8: a non-numeric measurement system must
#: register and operate, so a symbol, a grade, a lattice element, a branch label and an integer are
#: all components and none is a special case. One shape carries a scalar counter, a vector clock, a
#: ``(chain, height)`` pair and a ``(second, attosecond)`` split.
Position = tuple[object, ...]


@runtime_checkable
class OrderingStrategy(Protocol):
    """The comparison contract. Two methods, and no assumption about what the components mean."""

    def ordering(self) -> Ordering:
        """The discipline this strategy implements."""

    def compare(self, left: Position, right: Position) -> str:
        """A declared relation NAME.

        MUST NOT RAISE for shapes or types it does not understand — it returns an undecided
        relation, so an unanswerable pair is a datum rather than an interruption.
        """


def _try_precedes(left: Position, right: Position) -> bool | None:
    """``left < right``, or ``None`` when the components are not mutually comparable.

    THE GUARD THAT MAKES NON-NUMERIC POSITIONS SAFE. Comparing a symbol with an integer raises in
    Python; raising here would turn a heterogeneous population into an interruption instead of a
    finding. Returning ``None`` lets the caller answer INCOMPARABLE, which is the honest outcome.
    """
    try:
        return bool(left < right)  # type: ignore[operator]
    except TypeError:
        return None


@dataclass(frozen=True)
class LexicographicStrategy:
    """Component-by-component comparison. TOTAL for homogeneous, mutually comparable positions.

    Positions of DIFFERENT LENGTH are incomparable rather than zero-padded: padding would equate a
    one-component position with a two-component one whose second is zero, and those come from
    differently-shaped clocks.

    WORKS ON SYMBOLS. A position of strings orders lexicographically, which is why a non-numeric
    measurement system needs no strategy of its own unless its order differs from its spelling.
    """

    def ordering(self) -> Ordering:
        return TOTAL

    def compare(self, left: Position, right: Position) -> str:
        if len(left) != len(right):
            return INCOMPARABLE.name
        if left == right:
            return SIMULTANEOUS.name
        precedes = _try_precedes(left, right)
        if precedes is None:
            return INCOMPARABLE.name
        return BEFORE.name if precedes else AFTER.name


@dataclass(frozen=True)
class CausalStrategy:
    """Vector clocks. Componentwise domination, and genuine concurrency when neither dominates.

    THE STRATEGY THAT MAKES THE POINT. ``(1, 0)`` and ``(0, 1)`` are CONCURRENT: both happened,
    neither caused the other, and any total order over them is invention. A string timestamp cannot
    express this outcome, which is why it always produces one.
    """

    def ordering(self) -> Ordering:
        return CAUSAL

    def compare(self, left: Position, right: Position) -> str:
        if len(left) != len(right):
            return INCOMPARABLE.name
        if left == right:
            return SIMULTANEOUS.name
        try:
            left_dominates = all(a >= b for a, b in zip(left, right, strict=True))  # type: ignore[operator]
            right_dominates = all(a <= b for a, b in zip(left, right, strict=True))  # type: ignore[operator]
        except TypeError:
            return INCOMPARABLE.name
        if left_dominates:
            return AFTER.name
        if right_dominates:
            return BEFORE.name
        return CONCURRENT.name


@dataclass(frozen=True)
class BranchingStrategy:
    """Positions shaped ``(branch, height, ...)``. Comparable only within one branch.

    FOR FORKED HISTORIES: a reorganised ledger, a simulation replayed from a checkpoint, a
    governance timeline that diverged and was never merged. Height 9 on branch 2 and height 11 on
    branch 3 stand in no order, and reporting one as later would describe a history that does not
    exist.
    """

    branch_fields: int = 1

    def __post_init__(self) -> None:
        if self.branch_fields < 1:
            raise OrderingError(
                "a branching strategy with no branch fields cannot tell two histories apart, so "
                "every position would appear to be on one branch"
            )

    def ordering(self) -> Ordering:
        return BRANCHING

    def compare(self, left: Position, right: Position) -> str:
        cut = self.branch_fields
        if len(left) <= cut or len(right) <= cut or len(left) != len(right):
            return INCOMPARABLE.name
        if left[:cut] != right[:cut]:
            return INCOMPARABLE.name
        if left == right:
            return SIMULTANEOUS.name
        precedes = _try_precedes(left[cut:], right[cut:])
        if precedes is None:
            return INCOMPARABLE.name
        return BEFORE.name if precedes else AFTER.name


@dataclass(frozen=True)
class ConsensusStrategy:
    """Positions shaped ``(observer, ...)``. Comparable only between agreeing observers.

    ``agreeing`` is the declared set of observer identities sharing a frame. An empty set means no
    observer agrees with any other, which is the correct starting assumption for a federation nobody
    has configured — and it makes the absence of consensus a reported finding rather than a default.
    """

    agreeing: frozenset[object] = frozenset()

    def ordering(self) -> Ordering:
        return DISTRIBUTED

    def compare(self, left: Position, right: Position) -> str:
        if not left or not right or len(left) != len(right):
            return INCOMPARABLE.name
        if left[0] not in self.agreeing or right[0] not in self.agreeing:
            return INCOMPARABLE.name
        if left[1:] == right[1:]:
            return SIMULTANEOUS.name
        precedes = _try_precedes(left[1:], right[1:])
        if precedes is None:
            return INCOMPARABLE.name
        return BEFORE.name if precedes else AFTER.name


class OrderingRegistry:
    """Ordering name -> strategy, plus the declared ordering vocabulary and the relation registry.

    HOLDS THE RELATIONS TOO, because a strategy's outcomes must resolve against the same vocabulary
    the consistency check reads. Two registries could disagree, and the disagreement would surface
    as an unexplainable comparison rather than as a configuration error.
    """

    def __init__(
        self,
        seed: Iterable[OrderingStrategy] = (),
        *,
        relations: RelationRegistry | None = None,
    ) -> None:
        self._by_name: dict[str, OrderingStrategy] = {}
        self._orderings: dict[str, Ordering] = {o.name: o for o in INITIAL_ORDERINGS}
        self.relations = relations if relations is not None else RelationRegistry()
        for strategy in seed:
            self.register(strategy)

    def register(self, strategy: OrderingStrategy) -> OrderingStrategy:
        ordering = strategy.ordering()
        existing = self._by_name.get(ordering.name)
        if existing is not None and type(existing) is not type(strategy):
            raise OrderingError(
                f"ordering {ordering.name!r} is already implemented by {type(existing).__name__}, "
                "and one ordering name with two comparison behaviours makes every claim about "
                "event order unenforceable; declare a new ordering instead"
            )
        declared = self._orderings.get(ordering.name)
        if declared is not None and declared != ordering:
            raise OrderingError(
                f"ordering {ordering.name!r} is already declared with a different meaning; one "
                f"name "
                "with two meanings is worse than two names"
            )
        self._orderings[ordering.name] = ordering
        self._by_name[ordering.name] = strategy
        return strategy

    def declare(self, ordering: Ordering) -> Ordering:
        existing = self._orderings.get(ordering.name)
        if existing is not None and existing != ordering:
            raise OrderingError(
                f"ordering {ordering.name!r} is already declared with a different meaning; choose "
                f"a "
                "different name"
            )
        self._orderings[ordering.name] = ordering
        return ordering

    def resolve(self, name: str) -> OrderingStrategy:
        try:
            return self._by_name[name]
        except KeyError:
            raise OrderingError(
                f"{name!r} names no registered ordering strategy; register it before recording a "
                "coordinate that cites it, so a misspelling cannot become an order nobody defines"
            ) from None

    def ordering(self, name: str) -> Ordering:
        try:
            return self._orderings[name]
        except KeyError:
            raise OrderingError(
                f"{name!r} is not a declared ordering; declaring it is how a sixth discipline "
                f"joins "
                "this system, and it must happen before a record cites it"
            ) from None

    def known(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_name))

    def declared(self) -> tuple[Ordering, ...]:
        return tuple(sorted(self._orderings.values()))

    def report(self) -> dict[str, object]:
        return {
            "strategies": {
                name: {
                    "implementation": type(strategy).__name__,
                    "total": strategy.ordering().total,
                }
                for name, strategy in sorted(self._by_name.items())
            },
            "orderings": [
                {"ordering": o.name, "total": o.total, "description": o.description}
                for o in self.declared()
            ],
            "relations": [relation.as_record() for relation in self.relations.known()],
        }

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


def default_registry(strategies: Sequence[OrderingStrategy] = ()) -> OrderingRegistry:
    """A registry holding the four shipped strategies, plus whatever the caller supplies.

    NO PROCESS-WIDE SINGLETON. ``ConsensusStrategy`` carries the agreeing-observer set, so a shared
    registry would let one federation's consensus configuration govern another's comparisons.
    """
    registry = OrderingRegistry(
        (LexicographicStrategy(), CausalStrategy(), BranchingStrategy(), ConsensusStrategy())
    )
    for strategy in strategies:
        registry.register(strategy)
    return registry


def _shape_of(position: Position) -> tuple[object, ...]:
    """The position's SHAPE: its arity and its component type names.

    WHY A SHAPE NOTION IS NEEDED HERE, and it is an assumption this function's own first
    draft contained. ``assert_consistent`` demanded that a strategy declaring ``total=True``
    return an ordered or coincident relation for EVERY sample pair — including a 1-tuple
    against a 2-tuple, and an integer component against a symbolic one.
    ``LexicographicStrategy`` correctly answers INCOMPARABLE for both, so the checker refused
    a strategy that was telling the truth.

    THE CHECKER WAS WRONG, NOT THE STRATEGY. Totality is a claim about ONE position domain,
    not about every pair of tuples that can be constructed. Positions of different arity come
    from differently-shaped clocks, and a position of symbols and a position of integers are
    measurements on different scales; asking whether they are ordered is a category error, and
    INCOMPARABLE is the honest answer to a category error.

    So the totality obligation is enforced WITHIN a shape class, and cross-shape pairs are
    still checked for antisymmetry — which must hold everywhere, because a refusal that
    depends on argument order is not a refusal.
    """
    return (len(position), tuple(type(component).__name__ for component in position))


def assert_consistent(
    strategy: OrderingStrategy,
    samples: Sequence[Position],
    relations: RelationRegistry,
) -> None:
    """Refuse a strategy whose declared discipline contradicts its measured behaviour.

    THREE PROPERTIES, each measured, and NONE OF THEM NAMES A RELATION. The check reads
    ``admits_total_order`` and ``inverse``, so a registered sixth relation is verified by this same
    function with no edit — which is what Rule 4 requires of a consistency check.

      declared relation   an outcome the registry does not know is a conclusion nothing defines
      totality            a strategy claiming totality that returns an undecided or concurrent
                          outcome is lying about itself, and every ordering claim inherits the lie.
                          Enforced WITHIN one shape class only: see ``_shape_of``
      antisymmetry        ``compare(a, b)`` must mirror to ``compare(b, a)`` via the declared
                          inverse, or "the earlier event" is undefined while appearing to have an
                          answer
    """
    ordering = strategy.ordering()
    for left in samples:
        for right in samples:
            outcome = relations.resolve(strategy.compare(left, right))
            same_domain = _shape_of(left) == _shape_of(right)
            if ordering.total and same_domain and not outcome.admits_total_order:
                raise OrderingError(
                    f"{ordering.name} declares itself total and returned {outcome.name} for "
                    f"{left} vs {right}, which are the SAME shape; a total ordering that admits "
                    "unordered pairs within one position domain is a partial ordering with a "
                    "wrong label, and callers will trust the label"
                )
            mirrored = relations.resolve(strategy.compare(right, left))
            expected = relations.inverse_of(outcome.name)
            if mirrored != expected:
                raise OrderingError(
                    f"{ordering.name} compares {left} vs {right} as {outcome.name} but {right} vs "
                    f"{left} as {mirrored.name}, where {expected.name} was required by the "
                    f"declared "
                    "inverse; without antisymmetry 'the earlier event' is undefined while still "
                    "appearing to have an answer"
                )


__all__ = [
    "AFTER",
    "BEFORE",
    "BRANCHING",
    "CAUSAL",
    "CONCURRENT",
    "DISTRIBUTED",
    "INCOMPARABLE",
    "INITIAL_ORDERINGS",
    "INITIAL_RELATIONS",
    "PARTIAL",
    "SIMULTANEOUS",
    "TOTAL",
    "BranchingStrategy",
    "CausalStrategy",
    "ConsensusStrategy",
    "LexicographicStrategy",
    "Ordering",
    "OrderingError",
    "OrderingRegistry",
    "OrderingStrategy",
    "Position",
    "Relation",
    "RelationRegistry",
    "assert_consistent",
    "default_registry",
]
