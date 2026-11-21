"""CMG-000002 as executable law — the Universal Temporal Existence Contract.

CMG-000002 declared a temporal coordinate model in 1020 lines of prose and nothing
imported it. The contract's central claim is that **Universal Time is not a clock**:
it is a reference framework that lets multiple representations coexist, convert and
stay consistent. A document that says so while every timestamp in the repository is
Earth UTC is a claim, not a contract. This package is the contract.

What it refuses, quoting CMG-000002 §3.1's own ``DOES NOT MANDATE`` list: UTC,
ISO 8601, Unix epoch, GPS time, TAI, the Gregorian calendar, the 24-hour clock, Earth
time zones and leap seconds. None of those tokens appears in any control-flow branch
here. A Mars sol coordinate, a Lamport counter, a vector clock and a block height are
all first-class, and none is privileged.

Three consequences that shape the API:

* **No clock.** Nothing in this package reads the system time. ``now()`` does not
  exist. A caller who has a trustworthy reading supplies it with the reference system
  it came from; a caller who does not says so. This is what keeps a temporal
  coordinate replayable across processes and eras — the same discipline
  ``engine/uckp/values.py`` applies with its ``TIMELESS`` sentinel.
* **Comparison is partial, not total.** CMG-000002 Law 7 makes coordinates in
  different reference systems *incomparable* unless a conversion is declared.
  :func:`compare` therefore returns ``None`` rather than guessing, and
  :class:`Ordering` has an ``INCOMPARABLE`` member. A temporal API that always
  returns an answer is one that has assumed a single timeline.
* **Conversion carries provenance.** Law 3 requires conversion history to be
  preserved, so :func:`convert` appends to the coordinate rather than replacing its
  value, and a converted coordinate remembers every system it passed through.

Authority: NONE — DERIVED TRUTH. This package implements a located contract
(CMG-000002); it legislates nothing of its own and mints no identity.
"""

from __future__ import annotations

from engine.temporal.coordinate import (
    Ordering,
    Precision,
    Provenance,
    ReferenceSystem,
    SystemType,
    TemporalCoordinate,
    ValidityPeriod,
)
from engine.temporal.facets import FACET_NAMES, TemporalFacet, TemporalRecord
from engine.temporal.operations import (
    ConversionRule,
    TemporalError,
    TemporalRegistry,
    compare,
    convert,
    validate_ordering,
)

#: The published contract of this package.
TEMPORAL_CONTRACT: dict[str, object] = {
    "contract": "CMG-000002 Universal Temporal Existence Contract",
    "implements": "temporal coordinate model, ordering, conversion, validity, facets",
    "authority": "NONE — DERIVED TRUTH",
    "clock_free": True,
    "mandated_representation": None,
    "$mandated_representation_rationale": (
        "CMG-000002 §3.1 forbids mandating UTC, ISO 8601, Unix epoch, GPS, TAI, "
        "Gregorian, the 24-hour clock, Earth time zones or leap seconds. None is "
        "privileged here; a representation is data supplied by the caller."
    ),
    "laws_honoured": (
        "L3 conversion provenance preservation",
        "L4 representation independence",
        "L6 ordering within reference system",
        "L7 incomparability across systems",
        "L8 evidence binding immutability",
    ),
}

__all__ = [
    "FACET_NAMES",
    "TEMPORAL_CONTRACT",
    "ConversionRule",
    "Ordering",
    "Precision",
    "Provenance",
    "ReferenceSystem",
    "SystemType",
    "TemporalCoordinate",
    "TemporalError",
    "TemporalFacet",
    "TemporalRecord",
    "TemporalRegistry",
    "ValidityPeriod",
    "compare",
    "convert",
    "validate_ordering",
]
