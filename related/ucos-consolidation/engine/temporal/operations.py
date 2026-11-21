"""CMG-000002 §4 — the five required temporal operations.

The contract requires: obtain a current coordinate, compare, convert, validate
ordering, and preserve context. Four are implemented here. The fifth — "get current
coordinate" — is deliberately **not** implemented as a clock read: a caller who has a
reading supplies it, because a function here that read the system time would make
every coordinate it produced unreplayable, and CMG-000002's own ordering laws are
built on replay.

The single most important behaviour in this module is that :func:`compare` can return
``Ordering.INCOMPARABLE``. Law 7 makes cross-system comparison undefined unless a
conversion is declared, so an honest answer is sometimes "no answer". A comparator
that always returns a boolean has assumed one timeline, which is the assumption the
contract exists to remove.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from engine.temporal.coordinate import (
    Ordering,
    ReferenceSystem,
    TemporalCoordinate,
    TemporalError,
)


@dataclass(frozen=True, slots=True)
class ConversionRule:
    """A declared conversion between two reference systems.

    ``function`` is named as data so the conversion history records *which* rule ran,
    not merely that something converted. ``authority`` is required: an unattributed
    conversion cannot satisfy Law 3.
    """

    source: ReferenceSystem
    target: ReferenceSystem
    function_name: str
    authority: str
    convert: Callable[[str], str]

    @property
    def key(self) -> tuple[str, str]:
        return (self.source.key, self.target.key)


class TemporalRegistry:
    """The declared reference systems and the conversions between them.

    Systems are registered, never inferred. A conversion that is not registered does
    not exist, so :func:`compare` across systems fails closed into ``INCOMPARABLE``
    rather than improvising a common frame. Registration is append-only in effect:
    re-registering an identical rule is idempotent, and re-registering a *different*
    rule for the same pair is refused, because two answers to one conversion is the
    ambiguity Law 3 forbids.
    """

    __slots__ = ("_rules", "_systems")

    def __init__(self) -> None:
        self._systems: dict[str, ReferenceSystem] = {}
        self._rules: dict[tuple[str, str], ConversionRule] = {}

    def register_system(self, system: ReferenceSystem) -> None:
        """Declare a reference system.

        Raises:
            TemporalError: the key is already bound to a different system.
        """
        existing = self._systems.get(system.key)
        if existing is not None and existing != system:
            raise TemporalError("reference system already declared differently", subject=system.key)
        self._systems[system.key] = system

    def register_conversion(self, rule: ConversionRule) -> None:
        """Declare a conversion between two registered systems.

        Raises:
            TemporalError: either endpoint is undeclared, or the pair already has a
                different rule.
        """
        for endpoint in (rule.source, rule.target):
            if endpoint.key not in self._systems:
                raise TemporalError(
                    "conversion endpoint is not a declared reference system",
                    subject=endpoint.key,
                )
        existing = self._rules.get(rule.key)
        if existing is not None and existing.function_name != rule.function_name:
            raise TemporalError(
                "conversion already declared by a different function",
                subject=f"{rule.key[0]} -> {rule.key[1]}",
            )
        self._rules[rule.key] = rule

    def systems(self) -> tuple[ReferenceSystem, ...]:
        """Every declared system, in key order."""
        return tuple(self._systems[k] for k in sorted(self._systems))

    def rule_for(self, source: ReferenceSystem, target: ReferenceSystem) -> ConversionRule | None:
        """The declared rule from ``source`` to ``target``, or None."""
        return self._rules.get((source.key, target.key))

    def convertible(self, source: ReferenceSystem, target: ReferenceSystem) -> bool:
        """Whether a declared conversion exists."""
        return self.rule_for(source, target) is not None

    def to_dict(self) -> dict[str, object]:
        """A serialisable view, for a register or a report."""
        return {
            "systems": [s.to_dict() for s in self.systems()],
            "conversions": [
                {
                    "source_system": src,
                    "target_system": tgt,
                    "conversion_function": rule.function_name,
                    "conversion_authority": rule.authority,
                }
                for (src, tgt), rule in sorted(self._rules.items())
            ],
        }


def convert(
    coordinate: TemporalCoordinate,
    target: ReferenceSystem,
    registry: TemporalRegistry,
) -> TemporalCoordinate:
    """Express ``coordinate`` in ``target``, preserving conversion provenance.

    Converting to the system a coordinate is already in is the identity and records no
    step — a no-op conversion in the history would be noise, not provenance.

    Raises:
        TemporalError: no conversion from the coordinate's system to ``target`` is
            declared. Law 3 requires a named function and authority, and inventing one
            is the failure this refusal prevents.
    """
    if coordinate.reference_system.same_system(target):
        return coordinate
    rule = registry.rule_for(coordinate.reference_system, target)
    if rule is None:
        raise TemporalError(
            "no declared conversion between reference systems",
            subject=f"{coordinate.system_key} -> {target.key}",
        )
    return coordinate.with_conversion(
        target=target,
        primary=rule.convert(coordinate.primary),
        function=rule.function_name,
        authority=rule.authority,
    )


def compare(
    left: TemporalCoordinate,
    right: TemporalCoordinate,
    registry: TemporalRegistry | None = None,
) -> Ordering:
    """Order two coordinates, or report that they cannot be ordered.

    Same system: ordered by the system's own comparison. Different systems: ordered
    only if ``registry`` declares a conversion, otherwise ``INCOMPARABLE`` per Law 7.

    A system whose ``total_order`` is False yields ``INCOMPARABLE`` for non-equal
    values even within the system — that is what a partial order means, and a vector
    clock with concurrent events is the case that matters.
    """
    if left.reference_system.same_system(right.reference_system):
        return _compare_within_system(left, right)

    if registry is None:
        return Ordering.INCOMPARABLE
    if registry.convertible(left.reference_system, right.reference_system):
        return _compare_within_system(convert(left, right.reference_system, registry), right)
    if registry.convertible(right.reference_system, left.reference_system):
        return _compare_within_system(left, convert(right, left.reference_system, registry))
    return Ordering.INCOMPARABLE


def _compare_within_system(left: TemporalCoordinate, right: TemporalCoordinate) -> Ordering:
    """Compare two coordinates known to share a reference system."""
    if left.primary == right.primary:
        return Ordering.SIMULTANEOUS
    if not left.reference_system.total_order:
        # A partial order distinguishes only equality; anything else is concurrent.
        return Ordering.INCOMPARABLE
    return Ordering.BEFORE if _key(left.primary) < _key(right.primary) else Ordering.AFTER


def _key(primary: str) -> tuple[int, object]:
    """Order numerically when the value is numeric, lexically otherwise.

    A logical counter must order 2 < 10, which string comparison gets wrong. The
    two-element key keeps numeric and non-numeric values from being compared against
    each other by accident.
    """
    try:
        return (0, int(primary))
    except ValueError:
        pass
    try:
        return (0, float(primary))
    except ValueError:
        return (1, primary)


def validate_ordering(
    coordinates: Iterable[TemporalCoordinate],
    registry: TemporalRegistry | None = None,
) -> tuple[str, ...]:
    """Return the reasons a sequence is not in non-decreasing temporal order.

    Empty result means the sequence is validly ordered. An ``INCOMPARABLE`` adjacent
    pair is reported as a violation rather than skipped: a sequence that claims to be
    ordered while containing an unorderable pair is making a claim it cannot support.
    """
    items = tuple(coordinates)
    problems: list[str] = []
    for index, (earlier, later) in enumerate(zip(items, items[1:], strict=False)):
        verdict = compare(earlier, later, registry)
        if verdict is Ordering.AFTER:
            problems.append(
                f"position {index} is after position {index + 1}: "
                f"{earlier.primary} > {later.primary} in {earlier.system_key}"
            )
        elif verdict is Ordering.INCOMPARABLE:
            problems.append(
                f"positions {index} and {index + 1} are incomparable: "
                f"{earlier.system_key} vs {later.system_key} (no declared conversion)"
            )
    return tuple(problems)


def preserve_context(
    coordinate: TemporalCoordinate, context: Mapping[str, str]
) -> dict[str, object]:
    """Bind a coordinate to the context it was asserted in (CMG-000002 Law 5).

    Returns a plain mapping rather than a new type: the temporal context is consumed
    by ``engine/context/`` (UCXI-000001), which owns context, and returning a
    context object here would be a rival to it.
    """
    return {
        "temporal_coordinate": coordinate.to_dict(),
        "context": dict(sorted(context.items())),
        "$context_owner": "engine/context/ (UCXI-000001) — this is a binding, not a context model",
    }
