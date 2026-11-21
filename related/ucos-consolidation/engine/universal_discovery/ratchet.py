"""UCOS-OMEGA-001 Part 6 (Ω-4) — ratchets that evolve, replacing ceilings that were snapshots.

WHAT A STATIC CEILING ACTUALLY ASSERTS.

    MAX_OUTSIDE_SCOPE = 65
    ungoverned_executables = 27
    unmeasured_governance_engines = 39
    engines_without_tests = 25
    single_plane_engines = 14

Five numbers that were measurements on the afternoon somebody took them. Two of them were 607 and
570 a week earlier. Every one is a claim about a population size, and a claim about a population
size is false the moment the population grows for a legitimate reason — so a repository that
doubles has to rewrite its own ceilings, and the rewrite is indistinguishable from a retreat. The
declaration files even record the history in their rationale strings, which is the tell: a
threshold that needs a changelog is not a threshold, it is a diary.

WORSE, IN BOTH DIRECTIONS. This repository's ceilings are two-sided — a measurement BELOW the
ceiling also fails, forcing the number down as the work lands. That is a good instinct
implemented as a chore: every improvement requires a commit to a JSON file to tell the gate that
improving was allowed.

Ω-4 REPLACES THE NUMBER WITH A DIRECTION.

The gate no longer asks "is this under 65". It asks "is this worse than the best this repository
has ever achieved", and the best-ever value is a measurement the gate itself records. Improving
needs no edit. Regressing needs a written justification naming the metric. Scaling needs nothing
at all, because a DENSITY ratchet is a ratio and a ratio does not care how large the repository
became.

  MONOTONIC   may fall or hold, never rise. For populations that should only ever shrink.
  CONVERGENT  monotonic, AND a hold long enough to look like acceptance is reported as STALLED.
              This is the kind that refuses to let an exemption class become a convention.
  DENSITY     a ratio. Scale-free, so growth cannot breach it and cannot flatter it either.
  ENTROPY     complexity per executable unit. Bounds how tangled the average artifact may get,
              independent of how many artifacts there are.

WHY ``best`` IS SEALED RATHER THAN AUTHORED. The state file holds the best value ever OBSERVED,
written by ``--seal`` from a measurement, never typed. A human editing it upward is exactly the
retreat the two-sided ceiling was trying to prevent, and it is visible as a diff that raises a
number no measurement produced — which ``assert_sealed_from_measurement`` refuses.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence

from engine.universal_discovery.model import (
    CONVERGENT,
    DENSITY,
    ENTROPY,
    HELD,
    IMPROVED,
    JUSTIFIED,
    MONOTONIC,
    RATCHET_KINDS,
    REGRESSED,
    SEEDED,
    STALLED,
    Observation,
    OmegaError,
)

SCHEMA = "ucos-omega-ratchet"
VERSION = "1.0.0"

#: How many consecutive sealed observations at an unchanged non-zero value a CONVERGENT metric may
#: record before the hold is reported as STALLED. Not a threshold on the METRIC — a threshold on
#: how long "no progress" may go unremarked, which is the only kind of number an infinite system
#: can hold, because it does not scale with the repository.
STALL_OBSERVATIONS = 5


class Ratchet:
    """The best-ever value per metric, and the justifications that permit a regression.

    HOLDS NO METRIC DEFINITION. The metrics are supplied by the measurement; this class knows only
    how to compare, so a phase that adds a metric needs no edit here and a metric that is retired
    leaves no orphan rule behind. That is the same construction as the rest of Ω: the mechanism
    quantifies over what it is given, never over a list of what there is.
    """

    def __init__(self, document: Mapping[str, object] | None = None) -> None:
        document = document or {}
        self.best: dict[str, float] = {
            str(k): float(v) for k, v in (document.get("best") or {}).items()
        }
        self.kinds: dict[str, str] = {
            str(k): str(v) for k, v in (document.get("kinds") or {}).items()
        }
        self.holds: dict[str, int] = {
            str(k): int(v) for k, v in (document.get("holds") or {}).items()
        }
        self.justifications: dict[str, str] = {
            str(entry["metric"]): str(entry["reason"])
            for entry in (document.get("justifications") or [])
        }
        #: Declared structural floors: ``metric -> (value, reason)``. A CONVERGENT metric whose
        #: target of zero is genuinely unreachable declares WHY here, and the declaration is
        #: refused the moment it stops being true.
        self.floors: dict[str, tuple[float, str]] = {
            str(entry["metric"]): (float(entry["value"]), str(entry["reason"]))
            for entry in (document.get("floors") or [])
        }
        #: Re-seed records: ``metric -> reason``. When a measurement DEFECT is fixed, the metric's
        #: old bound is a number about a different question and has to be dropped, or the gate
        #: refuses forever against an answer nobody can reach. That is legitimate and it is also
        #: the most abusable operation in this file, so it leaves a permanent record: dropping a
        #: bound without writing here loses the audit trail, and ``assert_corrections_recorded``
        #: is what notices.
        self.corrections: dict[str, str] = {
            str(entry["metric"]): str(entry["reason"])
            for entry in (document.get("corrections") or [])
        }
        for metric, reason in self.justifications.items():
            if not reason.strip():
                raise OmegaError(
                    f"the regression justification for {metric!r} states no reason; an unexplained "
                    "regression is the ceiling rewrite this mechanism exists to replace"
                )
        for metric, (_value, reason) in self.floors.items():
            if not reason.strip():
                raise OmegaError(
                    f"the declared floor for {metric!r} states no reason; a floor without an "
                    "argument is a ceiling wearing a different name"
                )
        for metric, reason in self.corrections.items():
            if not reason.strip():
                raise OmegaError(
                    f"the re-seed record for {metric!r} states no reason; a bound dropped without "
                    "a written correction is indistinguishable from a bound dropped to pass"
                )

    # ------------------------------------------------------------------------------ comparison

    def observe(
        self,
        metric: str,
        kind: str,
        value: float,
        subject: str,
        *,
        ratio: tuple[int, int] | None = None,
    ) -> Observation:
        """Compare one measurement against its own best-ever value.

        A metric seen for the first time is SEEDED, never REGRESSED. Seeding is not a free pass:
        the seeded value becomes the bound every future run is held to, so the first observation
        is the last one that costs nothing.
        """
        if kind not in RATCHET_KINDS:
            raise OmegaError(
                f"{metric!r} declares ratchet kind {kind!r}, which is not one of Ω-4's"
            )
        declared = self.kinds.get(metric)
        if declared is not None and declared != kind:
            raise OmegaError(
                f"{metric!r} was sealed as {declared} and is now measured as {kind}; a metric that "
                "changes kind is a different metric and must be named differently"
            )
        best = self.best.get(metric)
        if best is None:
            return Observation(metric, kind, value, None, SEEDED, subject, ratio=ratio)

        if value < best:
            return Observation(metric, kind, value, best, IMPROVED, subject, ratio=ratio)

        if value > best:
            reason = self.justifications.get(metric, "")
            verdict = JUSTIFIED if reason else REGRESSED
            return Observation(metric, kind, value, best, verdict, subject, reason, ratio)

        stalled = (
            kind == CONVERGENT and value > 0 and self.holds.get(metric, 0) + 1 >= STALL_OBSERVATIONS
        )
        if not stalled:
            return Observation(metric, kind, value, best, HELD, subject, ratio=ratio)
        # A CONVERGENT metric can legitimately bottom out above zero, and forcing a fix that does
        # not exist would be worse than the ceiling this replaces — it would make the gate demand a
        # lie. So a stall is accepted when a DECLARED FLOOR argues that this value is the floor.
        #
        # A FLOOR IS NOT A JUSTIFICATION, and keeping them separate is the point. A justification
        # excuses a value ABOVE the best; if the same entry served both purposes, one written
        # sentence about an unreachable zero would also excuse unlimited growth forever. A floor
        # excuses only the STALL, and never a regression: at 33 a declared floor of 33 is accepted,
        # at 34 the same declaration refuses.
        floor = self.floors.get(metric)
        if floor is not None and value <= floor[0]:
            return Observation(metric, kind, value, best, JUSTIFIED, subject, floor[1], ratio)
        return Observation(metric, kind, value, best, STALLED, subject, ratio=ratio)

    # ----------------------------------------------------------------------------------- seal

    def sealed(self, observations: Sequence[Observation]) -> dict[str, object]:
        """The next state file: best-ever values, updated only DOWNWARD, plus the hold counters.

        A JUSTIFIED regression does NOT move ``best``. That is deliberate and it is the difference
        between a justification and a new ceiling: the justification lets one run pass, and the
        repository is still held to the value it once achieved. Ratifying a regression therefore
        requires the metric to actually improve again, not a note explaining that it will not.
        """
        best = dict(self.best)
        kinds = dict(self.kinds)
        holds = dict(self.holds)
        for observation in observations:
            kinds[observation.metric] = observation.kind
            previous = best.get(observation.metric)
            if previous is None or observation.value < previous:
                best[observation.metric] = observation.value
                holds[observation.metric] = 0
            elif observation.value == previous:
                holds[observation.metric] = holds.get(observation.metric, 0) + 1
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "authority": "NONE — DERIVED TRUTH. Every value here is a measurement, never a choice.",
            "producer": "engine/universal_discovery/ratchet.py",
            "how_to_read": (
                "best[m] is the lowest value of metric m this repository has ever recorded. A run "
                "measuring more than best[m] is REFUSED unless justifications names m with a "
                "reason. A justification permits one run and never moves best[m], so a regression "
                "cannot become the new normal by being explained. holds[m] counts consecutive "
                "runs at an unchanged value; a CONVERGENT metric held at a non-zero value for "
                f"{STALL_OBSERVATIONS} runs is reported STALLED, because an exemption class that "
                "stops shrinking has become a convention. floors[m] argues that a particular "
                "value IS m's floor and so accepts the stall — it does NOT excuse a regression, "
                "and it is refused as stale the moment m is measured below it."
            ),
            "best": {k: best[k] for k in sorted(best)},
            "kinds": {k: kinds[k] for k in sorted(kinds)},
            "holds": {k: holds[k] for k in sorted(holds)},
            "justifications": [
                {"metric": m, "reason": self.justifications[m]} for m in sorted(self.justifications)
            ],
            "floors": [
                {"metric": m, "value": self.floors[m][0], "reason": self.floors[m][1]}
                for m in sorted(self.floors)
            ],
            # Carried forward, always. A re-seed is the one operation here that can make a
            # refusal disappear, so its record must survive every subsequent seal — otherwise the
            # next seal launders it and the diff that would have shown it is gone.
            "corrections": [
                {"metric": m, "reason": self.corrections[m]} for m in sorted(self.corrections)
            ],
        }


def load(path: str) -> Ratchet:
    """Read the sealed state. A MISSING file seeds; a CORRUPT file is a fault.

    The distinction matters. "Not measured yet" is a real state with a safe answer. "Measured and
    unreadable" is a state in which every comparison would silently pass, so it raises.
    """
    if not os.path.exists(path):
        return Ratchet({})
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError) as exc:
        raise OmegaError(
            f"the Ω ratchet state at {path} is unreadable, and an unreadable ratchet permits "
            f"every regression: {exc}"
        ) from exc
    if document.get("schema") != SCHEMA:
        raise OmegaError(
            f"{path} declares schema {document.get('schema')!r}, not {SCHEMA!r}; refusing to "
            "compare against a document that may not be a ratchet"
        )
    return Ratchet(document)


def write(path: str, document: Mapping[str, object]) -> None:
    """Seal the state deterministically. Sorted keys, trailing newline, no wall clock."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    encoded = json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(encoded)


def refusals(observations: Sequence[Observation]) -> tuple[Observation, ...]:
    return tuple(o for o in observations if o.refused)


def assert_floors_live(state: Ratchet, observations: Sequence[Observation]) -> None:
    """A declared floor that stops being true is a REFUSAL, not a leftover.

    The same two-direction discipline the coverage-exemption register already uses, and for the same
    reason: an argument that has been overtaken by the work must cost something, or the register
    rots into a blanket permission. If a metric is measured BELOW its declared floor, the floor was
    wrong and the declaration has to say so.
    """
    measured = {o.metric: o.value for o in observations}
    stale = sorted(
        f"{metric} (declared floor {value}, measured {measured[metric]})"
        for metric, (value, _reason) in state.floors.items()
        if metric in measured and measured[metric] < value
    )
    if stale:
        raise OmegaError(
            "these declared floors are above the value actually measured, so the argument that "
            "they are floors has been overtaken and must be withdrawn or lowered: "
            + ", ".join(stale)
        )
    unbound = sorted(metric for metric in state.floors if metric not in measured)
    if unbound:
        raise OmegaError(
            "these declared floors name no measured metric, so they argue about nothing: "
            + ", ".join(unbound)
        )


def assert_sealed_from_measurement(
    document: Mapping[str, object], observations: Sequence[Observation]
) -> None:
    """Refuse a state file whose ``best`` is looser than the measurement that produced it.

    THE ATTACK THIS CLOSES, stated plainly: raise ``best`` by hand and every regression becomes
    compliant, silently and forever, in a diff that looks like maintenance. So the seal is checked
    against the run: no ``best`` may exceed the value just measured, because a lower value was
    once achieved and a measurement cannot retroactively un-achieve it.
    """
    best = {str(k): float(v) for k, v in (document.get("best") or {}).items()}
    measured = {o.metric: o.value for o in observations}
    inflated = sorted(
        metric for metric, bound in best.items() if metric in measured and bound > measured[metric]
    )
    if inflated:
        raise OmegaError(
            "these sealed bounds are looser than the measurement that sealed them, so the state "
            "file was edited rather than measured: " + ", ".join(inflated)
        )


def ratio(numerator: int, denominator: int) -> float:
    """A DENSITY/ENTROPY value. An empty denominator is a fault, never a comfortable zero."""
    if denominator <= 0:
        raise OmegaError(
            "a density ratchet was measured over an empty denominator, which would report "
            "perfection for an empty repository"
        )
    return round(numerator / denominator, 6)


#: Kinds whose value is a ratio rather than a count, kept here so reporting can format them
#: without a second table that could disagree with this one.
RATIO_KINDS: frozenset[str] = frozenset({DENSITY, ENTROPY})

__all__ = [
    "CONVERGENT",
    "DENSITY",
    "ENTROPY",
    "MONOTONIC",
    "RATIO_KINDS",
    "SCHEMA",
    "STALL_OBSERVATIONS",
    "Ratchet",
    "assert_floors_live",
    "assert_sealed_from_measurement",
    "load",
    "ratio",
    "refusals",
    "write",
]
