"""UCOS Ω∞ Temporal — the universal temporal coordinate.

AUTHORITY = NONE (DERIVED TRUTH).

WHAT REPLACES ``timestamp: str``::

    TemporalCoordinate(
        frame     = <where the observation was made>,
        scale     = <what the components count>,
        ordering  = <how positions on this scale compare>,
        position  = (<opaque components>,),
        clock     = <which clock produced it>,
        labels    = {<calendar>: <rendering>},   # PRESENTATION ONLY
    )

FIVE STATED FACTS WHERE THERE WAS ONE STRING. The string carried the position and nothing else, so
the frame was Earth, the scale was SI seconds, the ordering was total and the clock was whatever the
machine had — none recorded, therefore none questionable, therefore none replaceable.

TWO ASSUMPTIONS THIS FILE'S FIRST DRAFT STILL CONTAINED, and both were found by taking Rule 8
seriously rather than by review:

    json.dumps / hashlib.sha256   Representation and Identity hardcoded as requirements. Now every
                                  byte-producing method takes ``encoding: Encoding`` WITH NO
                                  DEFAULT, so there is nothing to fall back to.
    position: tuple[int, ...]     measurement assumed numeric. Components are now opaque, and
                                  determinism is the codec's declared obligation rather than a
                                  property of the integer type. A symbol, a grade or a lattice
                                  element is a position.

``labels`` IS PRESENTATION AND NEVER IDENTITY, declared ``compare=False``. Two coordinates agreeing
on frame, scale, ordering, position and clock are EQUAL even if one carries a civil rendering and
the other a Darian one. This is what makes calendar registration additive: registering a calendar
enriches what a record DISPLAYS and cannot alter what it IS. Were labels compared, adding a calendar
provider would rewrite every digest in an append-only register, and "extension without code
modification" would be true of the code and false of the data.

THE TWO KINDS OF ORDER, HELD APART DELIBERATELY.

    canonical order   ``canonical_key()``. A SERIALISATION order, whose only job is to make a
    document
                      byte-identical across runs. NOT A CLAIM ABOUT TIME.
    temporal order    ``compare(...)``, which returns one of the registered relations and may answer
                      CONCURRENT or INCOMPARABLE.

Two vector-clock coordinates that are CONCURRENT still sort deterministically, and that is not a
contradiction: one question is which line this goes on in a file, the other is which event happened
first. Conflating them is how a sorted log became a causal history.

COMPARISON REFUSES BEFORE IT GUESSES. Scale mismatch, ordering mismatch and unrelated frames each
produce INCOMPARABLE with a cited rule and a stated reason. None raises, because a population of
incomparable pairs is a governance finding and an exception can describe only the first.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from engine.omega_governance.reference.domain import Value
from engine.omega_governance.reference.encoding import Encoding
from engine.omega_governance.temporal.frames import (
    FrameRegistry,
    ReferenceFrame,
    ScaleRegistry,
    TimeScale,
)
from engine.omega_governance.temporal.ordering import (
    INCOMPARABLE,
    Ordering,
    OrderingRegistry,
    Position,
)

SCHEMA = "ucos-omega-temporal-coordinate"
VERSION = "1.0.0"

#: The reference-domain name a coordinate belongs to. A STRING, resolved through a
#: ``DomainRegistry`` by whoever validates it — this module holds no domain object, so Time carries
#: no privilege here either.
DOMAIN = "TIME"


class CoordinateError(RuntimeError):
    """A coordinate was malformed, or a stored coordinate could not be rehydrated.

    RAISED, NEVER DEFAULTED — and "these two cannot be compared" is out of scope. That is a return
    value.
    """


@dataclass(frozen=True)
class TemporalCoordinate:
    """A position in time, stated completely enough to be questioned.

    NO FIELD HAS A DEFAULT, and the absence is itself a deliverable. A default frame privileges a
    place, a default scale privileges a unit, a default ordering privileges total order. Clock
    providers spare callers the tedium — ``LogicalClock().read()`` fills all five — so requiring
    them costs nothing at a call site and closes four assumptions.

    NO ``order=True``. A ``<`` operator on this type would imply a total order over time itself,
    which is the assumption the subpackage exists to remove. Deterministic serialisation uses
    ``canonical_key()`` explicitly, so a reader can see that an ordering decision was made and what
    it was for.
    """

    frame: ReferenceFrame
    scale: TimeScale
    ordering: Ordering
    position: Position
    clock: str
    labels: Mapping[str, str] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        if not self.position:
            raise CoordinateError(
                "a coordinate with an empty position locates nothing; a clock that cannot produce "
                "at least one component is not a clock"
            )
        if not self.clock.strip():
            raise CoordinateError(
                "a coordinate must name the clock that produced it; a position whose clock is "
                "unknown cannot safely be compared with one from a different clock"
            )
        object.__setattr__(self, "position", tuple(self.position))
        object.__setattr__(self, "labels", dict(sorted(self.labels.items())))

    # ------------------------------------------------------------------ derived, non-mutating

    def with_label(self, calendar: str, rendering: str) -> TemporalCoordinate:
        """A copy carrying one more calendar rendering. IDENTITY UNCHANGED, by construction."""
        if not calendar.strip():
            raise CoordinateError("a label must name the calendar that produced it")
        return TemporalCoordinate(
            self.frame,
            self.scale,
            self.ordering,
            self.position,
            self.clock,
            {**self.labels, calendar: rendering},
        )

    def canonical_key(self) -> tuple[object, ...]:
        """The SERIALISATION order. NOT a temporal claim — see the module docstring.

        Components are rendered as strings because they are opaque: a heterogeneous population would
        make a tuple comparison raise, and a serialisation order that can fail is not a
        serialisation order. The temporal question is ``compare``, which can answer CONCURRENT, as
        no key can.
        """
        return (
            self.frame.name,
            self.scale.name,
            self.ordering.name,
            tuple(str(component) for component in self.position),
            self.clock,
        )

    # ------------------------------------------------------------------------------- reporting

    def as_record(self) -> dict[str, object]:
        """The storage-neutral form: names, and the opaque components as the codec receives them.

        Ω∞ RULE 7 LIVES IN THIS RETURN TYPE. No path object, no file handle, no OS type — so the
        same record is writable to a filesystem, an object store, a relational column, a document
        database, a graph or a ledger without the domain model knowing which. ``from_record`` and
        the registries are what rehydrate it.
        """
        record: dict[str, object] = {
            "frame": self.frame.name,
            "scale": self.scale.name,
            "ordering": self.ordering.name,
            "position": list(self.position),
            "clock": self.clock,
        }
        if self.labels:
            record["labels"] = dict(self.labels)
        return record

    def as_value(self) -> Value:
        """This coordinate as a universal ``Value`` in the TIME domain.

        HOW TIME JOINS THE ARCHITECTURE WITHOUT LEADING IT. A coordinate is a ``Value`` like a
        temperature or a storage locator, validated by the same ``DomainRegistry``, encoded by the
        same codec, and transformable by the same declared transformations. Nothing consuming values
        needs to know that this one came from a clock.
        """
        return Value(
            DOMAIN,
            self.position,
            {
                "frame": self.frame.name,
                "scale": self.scale.name,
                "ordering": self.ordering.name,
                "clock": self.clock,
            },
        )

    def canonical(self, encoding: Encoding) -> bytes:
        """The deterministic bytes UNDER A NAMED ENCODING. Required argument, no default."""
        return encoding.encode(self.as_record())

    def identity(self, encoding: Encoding) -> str:
        """The fingerprint of the IDENTIFYING fields only — labels excluded, as equality excludes
        them.

        ``encoding`` is required for the same reason ``Value.fingerprint`` requires it: a
        fingerprint whose codec is implicit cannot be re-verified, because two codecs give one value
        two byte strings and only one of them yields the stored fingerprint.
        """
        return encoding.fingerprint({k: v for k, v in self.as_record().items() if k != "labels"})

    def __str__(self) -> str:
        rendered = "·".join(str(component) for component in self.position)
        return f"{self.frame.name}/{self.scale.name}@{rendered}"


def from_record(
    record: Mapping[str, object],
    *,
    frames: FrameRegistry,
    scales: ScaleRegistry,
    orderings: OrderingRegistry,
) -> TemporalCoordinate:
    """Rehydrate a stored coordinate THROUGH THE REGISTRIES, so an unknown name refuses.

    A record naming frame ``MARS`` must produce the declared MARS frame with its declared relations
    — not a fresh frame sharing a name and comparable with nothing. Reconstructing would make every
    stored record its own private vocabulary, and comparability across a register would quietly
    vanish.
    """
    try:
        frame_name = str(record["frame"])
        scale_name = str(record["scale"])
        ordering_name = str(record["ordering"])
        raw_position = record["position"]
        clock = str(record["clock"])
    except KeyError as exc:
        raise CoordinateError(
            f"a stored coordinate is missing the required field {exc.args[0]!r}; a partial "
            f"coordinate "
            "would be rehydrated with an assumed frame, scale or ordering, which is the assumption "
            "this type exists to make impossible"
        ) from exc
    if not isinstance(raw_position, list | tuple):
        raise CoordinateError(
            f"a stored coordinate holds position {raw_position!r}, which is not a sequence"
        )
    raw_labels = record.get("labels") or {}
    if not isinstance(raw_labels, Mapping):
        raise CoordinateError("a stored coordinate holds labels that are not a mapping")
    return TemporalCoordinate(
        frame=frames.resolve(frame_name),
        scale=scales.resolve(scale_name),
        ordering=orderings.ordering(ordering_name),
        position=tuple(raw_position),
        clock=clock,
        labels={str(k): str(v) for k, v in raw_labels.items()},
    )


# ------------------------------------------------------------------------------------ comparison


@dataclass(frozen=True, order=True)
class Comparison:
    """The outcome of asking how two coordinates stand, and WHY.

    ``reason`` is populated for every outcome and not only for refusals. "These two are CONCURRENT"
    is unactionable; "CONCURRENT under CAUSAL, neither vector dominates" tells a reader what would
    have to change for an order to exist.
    """

    relation: str
    rule: str
    reason: str
    left: str = ""
    right: str = ""
    decided: bool = True
    ordered: bool = False

    def as_record(self) -> dict[str, object]:
        return {
            "relation": self.relation,
            "rule": self.rule,
            "reason": self.reason,
            "left": self.left,
            "right": self.right,
            "decided": self.decided,
            "ordered": self.ordered,
        }


RULE_SAME_FRAME = "Ω²-C-01"
RULE_RELATED_FRAME = "Ω²-C-02"
RULE_FRAME_UNRELATED = "Ω²-C-03"
RULE_SCALE_MISMATCH = "Ω²-C-04"
RULE_ORDERING_MISMATCH = "Ω²-C-05"


def _refusal(
    rule: str, reason: str, left: TemporalCoordinate, right: TemporalCoordinate
) -> Comparison:
    return Comparison(INCOMPARABLE.name, rule, reason, str(left), str(right), decided=False)


def compare(
    left: TemporalCoordinate,
    right: TemporalCoordinate,
    *,
    frames: FrameRegistry,
    orderings: OrderingRegistry,
) -> Comparison:
    """How two coordinates stand. THREE REFUSAL PATHS BEFORE ANY COMPARISON OF COMPONENTS.

    The order of the checks is the architecture, because each guards the next:

      1. SCALE     sols and seconds are different units. Comparing their components would be a type
                   error dressed as a result, and no frame relation can rescue it.
      2. ORDERING  two coordinates citing different disciplines share no notion of precedence, so
                   there is nothing for a strategy to compute.
      3. FRAME     positions from unrelated frames are INCOMPARABLE. This is the check that makes
      the
                   single-planet assumption impossible to hold by accident.
      4. STRATEGY  only now do components meet components, and the strategy may still answer
                   CONCURRENT.
    """
    if left.scale != right.scale:
        return _refusal(
            RULE_SCALE_MISMATCH,
            f"{left.scale.name} counts {left.scale.unit or 'unnamed units'} and {right.scale.name} "
            f"counts {right.scale.unit or 'unnamed units'}; comparability is declared here and "
            f"never "
            "computed, so two scales are two questions",
            left,
            right,
        )
    if left.ordering != right.ordering:
        return _refusal(
            RULE_ORDERING_MISMATCH,
            f"the coordinates cite {left.ordering.name} and {right.ordering.name}; without a "
            f"shared "
            "discipline there is no agreed meaning of precedence to compute",
            left,
            right,
        )
    relation = frames.comparable(left.frame, right.frame)
    if relation is None:
        return _refusal(
            RULE_FRAME_UNRELATED,
            f"no relation is declared between frames {left.frame.name} and {right.frame.name}, so "
            f"no "
            "observer is known to be able to order these two events; declaring the relation is how "
            "a deployment states that it can",
            left,
            right,
        )
    strategy = orderings.resolve(left.ordering.name)
    outcome = orderings.relations.resolve(strategy.compare(left.position, right.position))
    rule = RULE_SAME_FRAME if left.frame == right.frame else RULE_RELATED_FRAME
    return Comparison(
        outcome.name,
        rule,
        f"{outcome.name} under {left.ordering.name} in frame {left.frame.name}"
        + (
            f" related to {right.frame.name} by {relation.rule}"
            if left.frame != right.frame
            else ""
        )
        + f"; positions {left.position} and {right.position}",
        str(left),
        str(right),
        decided=outcome.decided,
        ordered=outcome.ordered,
    )


def canonical_sequence(coordinates: Iterable[TemporalCoordinate]) -> tuple[TemporalCoordinate, ...]:
    """Coordinates in SERIALISATION order. Deterministic, and not a history.

    Named ``canonical_sequence`` rather than ``chronological`` on purpose: it will happily order two
    concurrent events, which is legitimate for writing a file and illegitimate for drawing a
    conclusion.
    """
    return tuple(sorted(coordinates, key=lambda c: c.canonical_key()))


def assert_deterministic(
    coordinate: TemporalCoordinate,
    *,
    encoding: Encoding,
    frames: FrameRegistry,
    scales: ScaleRegistry,
    orderings: OrderingRegistry,
) -> None:
    """Refuse a coordinate that does not survive a storage round trip unchanged, UNDER THIS
    ENCODING.

    Three properties: encoding twice yields identical bytes, rehydrating yields an equal coordinate,
    and the rehydrated coordinate's fingerprint matches. A type failing any of them would make every
    hash-chained register built on it unverifiable after a write and a read — and the ``encoding``
    argument is what makes the guarantee about a NAMED representation rather than about JSON.
    """
    first = coordinate.canonical(encoding)
    if first != coordinate.canonical(encoding):
        raise CoordinateError(  # pragma: no cover - a REPRODUCIBLE codec cannot reach this
            f"{encoding.codec.identifier()} produced different bytes for one coordinate on two "
            f"calls"
        )
    restored = from_record(
        coordinate.as_record(), frames=frames, scales=scales, orderings=orderings
    )
    if restored != coordinate:
        raise CoordinateError(
            f"the coordinate {coordinate} did not survive a storage round trip; a register whose "
            "records change on read cannot be audited"
        )
    if restored.identity(encoding) != coordinate.identity(encoding):
        raise CoordinateError(  # pragma: no cover - equality above implies this
            f"the coordinate {coordinate} rehydrated to an equal value with a different fingerprint"
        )


__all__ = [
    "DOMAIN",
    "RULE_FRAME_UNRELATED",
    "RULE_ORDERING_MISMATCH",
    "RULE_RELATED_FRAME",
    "RULE_SAME_FRAME",
    "RULE_SCALE_MISMATCH",
    "SCHEMA",
    "VERSION",
    "Comparison",
    "CoordinateError",
    "TemporalCoordinate",
    "assert_deterministic",
    "canonical_sequence",
    "compare",
    "from_record",
]
