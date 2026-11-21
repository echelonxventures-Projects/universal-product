"""UCOS Ω∞ Phase 2, Deliverables Ω-2.1, Ω-2.4 and Ω-2.5 — governance states as first-class entities.

AUTHORITY = NONE (DERIVED TRUTH). A vocabulary and a graph. Classifies nothing by itself and
certifies nothing ever.

THE DEFECT THIS CLOSES, in one line of an existing model::

    disposition: str    # Ω-5: exactly one of MEASURED EXEMPTED GENERATED ARCHIVED TRANSIENT

ONE FIELD, FIVE VALUES, AND THEREFORE ONE QUESTION. That field carries custody ("generated",
"archived"), scope ("exempted") and measurement ("measured") at once, so the answers compete for the
slot. An artifact genuinely both GENERATED and MEASURED must surrender one fact to be recordable,
and the surrendered fact becomes a governance state nothing can see. That is a SILENT GOVERNANCE
STATE.

The same collapse is why MEASURED came to mean GOVERNED. They are not synonyms — measurement is an
observation, governance is a claim of ownership under a rule — but one slot cannot hold both, so
whichever was written last won.

SIX AXES, EACH TOTAL, NONE PRIVILEGED.

    CUSTODY         UNKNOWN · DISCOVERED · GENERATED · TRANSIENT · ARCHIVED
    ATTRIBUTION     UNATTRIBUTED · ATTRIBUTED
    GOVERNANCE      UNGOVERNED · GOVERNED · EXEMPTED
    MEASUREMENT     UNMEASURED · MEASURED · UNMEASURABLE
    CERTIFICATION   UNCERTIFIED · CERTIFIED · CONDITIONALLY_CERTIFIED · REJECTED · UNVERIFIABLE
    CONSISTENCY     CONSISTENT · CONTRADICTED

A ``GovernanceStatus`` carries one position per axis. That is the whole of "eliminate all silent
governance states": no vector omits an axis, so no concern is unanswered. "We have not measured
this" is ``UNMEASURED`` — a value, countable and ratchetable — rather than a field nobody set.

THE CLOSED LIST THIS FILE'S FIRST DRAFT STILL CONTAINED. ``AXES`` was a module tuple quantified over
inside ``GovernanceStatus.__post_init__``, so registering a seventh axis at runtime would have made
every new status refuse construction, and Ω∞ Rule 3 would have failed on the model's own type. The
responsibility is now split, and the split is the fix:

    the TYPE enforces a LOCAL invariant     no axis holds two positions. Always checkable, no
    registry
    the REGISTRY enforces the GLOBAL one    ``assert_total`` reports every status silent about any
                                            REGISTERED axis, so widening the model makes existing
                                            records incomplete AND COUNTABLE rather than silently
                                            grandfathered

WHY THAT ORDERING IS RIGHT. A seventh axis is new knowledge, and new knowledge should not
retroactively invalidate a record's construction — it should produce a finding naming every record
that predates it. Refusing construction would force a migration; reporting a population invites one.

DELIVERABLE Ω-2.4 IS DISCHARGED BY THE SHAPE OF THE GRAPH, not by a validator.

    UNKNOWN never certifies       ``UNCERTIFIED → CERTIFIED`` is blocked_by UNKNOWN
    UNKNOWN never auto-exempts    ``UNGOVERNED → EXEMPTED`` is blocked_by UNKNOWN and needs a reason
    UNKNOWN never vanishes by relabelling
                                  UNKNOWN's ONLY outgoing edge is to DISCOVERED, which requires an
                                  observation. There is no edge to GENERATED, TRANSIENT or ARCHIVED.

AND NOTHING RETURNS TO UNKNOWN — it has no inbound edge — which makes the invariant provable by
exhaustive search rather than by argument. ``invariants.unknown_never_certifies`` enumerates all 900
vectors.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from engine.omega_governance.temporal.clocks import ClockProvider
from engine.omega_governance.temporal.coordinate import TemporalCoordinate


class StateError(RuntimeError):
    """A state, axis or transition was invalid, or a transition was refused.

    RAISED, NEVER DEFAULTED. Returning the unchanged status on a refused transition would produce a
    record claiming the artifact is still where it was, with no trace of the attempt — the silent
    governance state this package exists to eliminate, reintroduced by the error handling.
    """


# ----------------------------------------------------------------------------------------- axes


@dataclass(frozen=True, order=True)
class Axis:
    """One independent governance concern.

    ``order=True`` so a status vector sorts deterministically. Every document Phase 2 emits is
    compared byte-for-byte, and an unordered vector would break that for a reason unrelated to
    governance.
    """

    name: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise StateError("an axis with no name cannot hold a position or be reported")

    def __str__(self) -> str:
        return self.name


CUSTODY = Axis(
    "CUSTODY",
    "What the system knows this artifact to BE: whether it has been observed at all, and if so "
    "whether its bytes are authored, machine-produced, non-persistent or frozen.",
)
ATTRIBUTION = Axis(
    "ATTRIBUTION",
    "Whether authority resolution terminated above the universal fallback. Separate from "
    "GOVERNANCE "
    "because an owner of last resort is an owner in name and not in fact.",
)
GOVERNANCE = Axis(
    "GOVERNANCE",
    "Whether a governing rule claims this artifact, and whether that rule places it inside or "
    "outside a measurement scope. An exemption is a GOVERNANCE act, not a measurement outcome.",
)
MEASUREMENT = Axis(
    "MEASUREMENT",
    "Whether an observation of this artifact exists. Independent of GOVERNANCE, because conflating "
    "the two is the defect Deliverable Ω-2.5 names.",
)
CERTIFICATION = Axis(
    "CERTIFICATION",
    "The disposition a certification decision reached. Independent of MEASUREMENT, because "
    "certification consumes measurement and is not a synonym for it.",
)
CONSISTENCY = Axis(
    "CONSISTENCY",
    "Whether an open contradiction names this artifact. Its own axis because a contradiction is "
    "ABOUT the other five and must not overwrite the facts it contradicts.",
)

#: The axes this module ships. A CONVENIENCE TUPLE, seeded into a registry and nothing more. Nothing
#: quantifies over it: ``GovernanceStatus`` checks a local invariant, and completeness is measured
#: against whatever axes a ``StateRegistry`` actually holds.
INITIAL_AXES: tuple[Axis, ...] = (
    ATTRIBUTION,
    CERTIFICATION,
    CONSISTENCY,
    CUSTODY,
    GOVERNANCE,
    MEASUREMENT,
)


# ---------------------------------------------------------------------------------------- states


@dataclass(frozen=True, order=True)
class GovernanceState:
    """One position on one axis. A first-class entity, as the directive requires.

    ``initial`` marks the position a never-touched artifact occupies. Exactly one per axis, checked
    by ``StateRegistry.initial``: two would mean the starting vector is a choice, and a starting
    vector that is a choice is not a baseline.
    """

    name: str
    axis: Axis
    description: str = ""
    initial: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise StateError("a governance state with no name cannot be recorded or counted")

    def __str__(self) -> str:
        return self.name


# --------------------------------------------------------------------------------- CUSTODY
UNKNOWN = GovernanceState(
    "UNKNOWN",
    CUSTODY,
    "No provider has reported this artifact and no classifier has typed it. A NAMED POPULATION, "
    "never an absence: an artifact nobody can name is a governance hole no measurement can see.",
    initial=True,
)
DISCOVERED = GovernanceState(
    "DISCOVERED",
    CUSTODY,
    "A provider enumerated it. The ONLY exit from UNKNOWN, which is what stops the unknown "
    "population from draining through relabelling.",
)
GENERATED = GovernanceState(
    "GENERATED",
    CUSTODY,
    "Machine-produced from a source held elsewhere. Says nothing about governance: a generated "
    "artifact still has an owner, namely whoever owns the generator.",
)
TRANSIENT = GovernanceState(
    "TRANSIENT",
    CUSTODY,
    "Does not persist. The only custody claim that is self-justifying, and therefore the only one "
    "this graph requires a written reason for.",
)
ARCHIVED = GovernanceState(
    "ARCHIVED",
    CUSTODY,
    "Frozen; the bytes are immutable by a guard elsewhere. Orthogonal to CERTIFICATION, which is "
    "what makes 'certified but archived' recordable.",
)

# ----------------------------------------------------------------------------- ATTRIBUTION
UNATTRIBUTED = GovernanceState(
    "UNATTRIBUTED",
    ATTRIBUTION,
    "Authority resolution reached the universal fallback. An authority chain EXISTS — Ω-2.2 "
    "guarantees it — but nothing above the fallback claimed the artifact.",
    initial=True,
)
ATTRIBUTED = GovernanceState(
    "ATTRIBUTED",
    ATTRIBUTION,
    "Authority resolution terminated at a tier above the universal fallback, so a named authority "
    "answers for this artifact.",
)

# ------------------------------------------------------------------------------ GOVERNANCE
UNGOVERNED = GovernanceState(
    "UNGOVERNED",
    GOVERNANCE,
    "No governing rule claims this artifact. The default, and a finding rather than a resting "
    "place.",
    initial=True,
)
GOVERNED = GovernanceState(
    "GOVERNED",
    GOVERNANCE,
    "A governing rule claims this artifact and places it inside a measurement scope. NOT a synonym "
    "for MEASURED: the claim is that it ought to be measured, not that it has been.",
)
EXEMPTED = GovernanceState(
    "EXEMPTED",
    GOVERNANCE,
    "A governing rule claims this artifact and places it OUTSIDE a measurement scope, with a "
    "written argument. Governed, and deliberately unmeasured — which a single slot cannot say.",
)

# ----------------------------------------------------------------------------- MEASUREMENT
UNMEASURED = GovernanceState(
    "UNMEASURED",
    MEASUREMENT,
    "No observation exists yet. Distinct from UNMEASURABLE, exactly as UCI's ``coverage_percent = "
    "None`` is distinct from ``0.0``.",
    initial=True,
)
MEASURED = GovernanceState(
    "MEASURED",
    MEASUREMENT,
    "An observation exists. Carries NO governance claim and NO certification consequence; that "
    "separation is Deliverable Ω-2.5.",
)
UNMEASURABLE = GovernanceState(
    "UNMEASURABLE",
    MEASUREMENT,
    "An observation cannot be obtained, and the reason is written down. Refused from UNKNOWN, "
    "because 'we cannot measure what we have not found' is a discovery failure wearing a "
    "measurement excuse.",
)

# --------------------------------------------------------------------------- CERTIFICATION
UNCERTIFIED = GovernanceState(
    "UNCERTIFIED",
    CERTIFICATION,
    "No certification decision has been reached. A state, so 'nobody decided' is countable rather "
    "than indistinguishable from 'decided against'.",
    initial=True,
)
CERTIFIED = GovernanceState(
    "CERTIFIED",
    CERTIFICATION,
    "Every certification input was satisfied. Reachable only from a vector that is DISCOVERED, "
    "ATTRIBUTED, governed and CONSISTENT — the obligations are edges, not advice.",
)
CONDITIONALLY_CERTIFIED = GovernanceState(
    "CONDITIONALLY_CERTIFIED",
    CERTIFICATION,
    "Every required input was satisfied and at least one conditional input was not, with the "
    "shortfall named. A real disposition, so a partial pass need not be rounded to a full one.",
)
REJECTED = GovernanceState(
    "REJECTED",
    CERTIFICATION,
    "A required certification input was definitively unsatisfied. A DECISION, which is why it is "
    "reachable from UNKNOWN while CERTIFIED is not.",
)
UNVERIFIABLE = GovernanceState(
    "UNVERIFIABLE",
    CERTIFICATION,
    "No decision could be reached, because an input could not be evaluated. Never collapsed into "
    "REJECTED: 'we cannot tell' and 'we can tell, and no' are different facts.",
)

# ----------------------------------------------------------------------------- CONSISTENCY
CONSISTENT = GovernanceState(
    "CONSISTENT",
    CONSISTENCY,
    "No open contradiction names this artifact. The initial position, and the only one from which "
    "certification may proceed.",
    initial=True,
)
CONTRADICTED = GovernanceState(
    "CONTRADICTED",
    CONSISTENCY,
    "At least one open contradiction names this artifact. Blocks certification structurally, so a "
    "contradiction cannot be certified past by anyone who did not read the register.",
)

#: The states this module ships. NOT AN EXHAUSTIVE LIST of what may exist — a caller governing a
#: concern nobody has named declares its own axis and positions. Nothing quantifies over this tuple.
INITIAL_STATES: tuple[GovernanceState, ...] = (
    ARCHIVED,
    ATTRIBUTED,
    CERTIFIED,
    CONDITIONALLY_CERTIFIED,
    CONSISTENT,
    CONTRADICTED,
    DISCOVERED,
    EXEMPTED,
    GENERATED,
    GOVERNED,
    MEASURED,
    REJECTED,
    TRANSIENT,
    UNATTRIBUTED,
    UNCERTIFIED,
    UNGOVERNED,
    UNKNOWN,
    UNMEASURABLE,
    UNMEASURED,
    UNVERIFIABLE,
)

#: The thirteen states the Phase 2 directive names as its minimum set. Held here so "every required
#: state is a declared first-class entity" is checked by execution, and so an edit renaming one is
#: refused by a test rather than by a reviewer.
REQUIRED_STATE_NAMES: tuple[str, ...] = (
    "ARCHIVED",
    "CERTIFIED",
    "CONTRADICTED",
    "DISCOVERED",
    "EXEMPTED",
    "GENERATED",
    "GOVERNED",
    "MEASURED",
    "REJECTED",
    "TRANSIENT",
    "UNATTRIBUTED",
    "UNKNOWN",
    "UNVERIFIABLE",
)


class StateRegistry:
    """The canonical name -> state mapping, and the axis set derived from it.

    THE AXIS SET IS DERIVED, NOT DECLARED SEPARATELY. A registry's axes are exactly the axes its
    states occupy, so registering a state on a new axis registers the axis — one act, not two that
    can fall out of step. A deployment adding a seventh concern calls ``declare_name`` twice and has
    a seven-axis model with no edit here.
    """

    def __init__(self, seed: Iterable[GovernanceState] = INITIAL_STATES) -> None:
        self._by_name: dict[str, GovernanceState] = {}
        for state in seed:
            self.declare(state)

    def declare(self, state: GovernanceState) -> GovernanceState:
        """Register a state, or return the identical existing one. A CONFLICT raises."""
        existing = self._by_name.get(state.name)
        if existing is None:
            self._by_name[state.name] = state
            return state
        if existing.axis != state.axis:
            raise StateError(
                f"{state.name!r} is already declared on axis {existing.axis.name}, and one name on "
                f"two axes makes a status vector ambiguous about which concern it answered; "
                f"choose a "
                f"different name for the {state.axis.name} position"
            )
        if existing.description != state.description or existing.initial != state.initial:
            raise StateError(
                f"{state.name!r} is already declared with a different meaning, and one name with "
                f"two "
                "meanings makes every rule about it unenforceable; choose a different name"
            )
        return existing

    def declare_name(
        self, name: str, axis: Axis, description: str, *, initial: bool = False
    ) -> GovernanceState:
        """Declare from primitives. Ω∞ RULE 3: a new concern needs no edit to this file."""
        return self.declare(GovernanceState(name, axis, description, initial))

    def resolve(self, name: str) -> GovernanceState:
        """The registered state for a name. An UNKNOWN name raises rather than inventing a state."""
        try:
            return self._by_name[name]
        except KeyError:
            raise StateError(
                f"{name!r} is not a declared governance state; declare it before recording it, so "
                f"a "
                "misspelling cannot become a state no rule can refuse"
            ) from None

    def axes(self) -> tuple[Axis, ...]:
        """Every axis some declared state occupies. DERIVED, so it cannot disagree."""
        return tuple(sorted({state.axis for state in self._by_name.values()}))

    def on_axis(self, axis: Axis) -> tuple[GovernanceState, ...]:
        return tuple(sorted(s for s in self._by_name.values() if s.axis == axis))

    def initial(self, axis: Axis) -> GovernanceState:
        """The starting position on an axis. Exactly one, and neither zero nor two.

        ZERO means a never-touched artifact has no recordable position, which is the silent state
        this package removes. TWO means the baseline is a preference.
        """
        candidates = [s for s in self.on_axis(axis) if s.initial]
        if len(candidates) != 1:
            raise StateError(
                f"axis {axis.name} declares {len(candidates)} initial positions and must declare "
                "exactly one; without a unique baseline an untouched artifact has no state, and "
                "with two the baseline is a choice rather than a measurement"
            )
        return candidates[0]

    def known(self) -> tuple[GovernanceState, ...]:
        return tuple(sorted(self._by_name.values()))

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


def default_states(extra: Iterable[GovernanceState] = ()) -> StateRegistry:
    """A registry holding the twenty shipped states, plus whatever the caller declares.

    NO PROCESS-WIDE SINGLETON. The open-world suite registers a seventh axis, and a shared registry
    would leak that into the evidence run — making the evidence document depend on which tests ran.
    """
    registry = StateRegistry()
    for state in extra:
        registry.declare(state)
    return registry


# ----------------------------------------------------------------------------------- transitions


@dataclass(frozen=True, order=True)
class Transition:
    """One declared edge, its rule id, and the two guards that make the table a mechanism.

    ``justification`` states why the edge EXISTS; ``requires_reason`` asks the caller why it is
    being TAKEN. Keeping them apart is the difference between a documented graph and an audited one.
    """

    source: GovernanceState
    target: GovernanceState
    rule: str
    justification: str = ""
    #: Refused without a written argument. Set on every edge whose effect is to REDUCE an obligation
    #: — exempting, declaring unmeasurable, withdrawing authority, revoking certification. An
    #: unargued reduction of obligation is indistinguishable from one made to pass.
    requires_reason: bool = False
    #: States which, held ELSEWHERE in the vector, forbid this edge. How a cross-axis law becomes
    #: structural rather than a validator somebody remembers to run.
    blocked_by: tuple[GovernanceState, ...] = ()

    def __post_init__(self) -> None:
        if self.source.axis != self.target.axis:
            raise StateError(
                f"{self.rule} moves {self.source.name} on {self.source.axis.name} to "
                f"{self.target.name} on {self.target.axis.name}; a transition crossing axes would "
                "silently discard the position it left behind, which is the collapse the axes "
                "exist to prevent"
            )
        if self.source == self.target:
            raise StateError(
                f"{self.rule} declares a self-edge on {self.source.name}; a no-op transition would "
                "write an audit record describing no change"
            )
        if not self.rule.strip():
            raise StateError("a transition with no rule id cannot be cited by an audit record")
        object.__setattr__(self, "blocked_by", tuple(sorted(set(self.blocked_by))))

    @property
    def axis(self) -> Axis:
        return self.source.axis

    def as_record(self) -> dict[str, object]:
        return {
            "rule": self.rule,
            "axis": self.axis.name,
            "source": self.source.name,
            "target": self.target.name,
            "justification": self.justification,
            "requires_reason": self.requires_reason,
            "blocked_by": [s.name for s in self.blocked_by],
        }


#: The declared transition graph. ORDER IS NOT SIGNIFICANT — an edge set has no precedence — but
#: ABSENCE IS. Every pair not listed is a refused transition, and four specific absences carry
#: Deliverable Ω-2.4:
#:
#:   UNKNOWN -> GENERATED   absent, so an unknown artifact cannot be relabelled as machine output
#:   UNKNOWN -> TRANSIENT   absent, so it cannot be relabelled as not persisting
#:   UNKNOWN -> ARCHIVED    absent, so it cannot be relabelled as frozen
#:   * -> UNKNOWN           absent entirely, so the unknown population only ever drains
INITIAL_TRANSITIONS: tuple[Transition, ...] = (
    # ------------------------------------------------------------------------------- CUSTODY
    Transition(
        UNKNOWN,
        DISCOVERED,
        "Ω²-S-01",
        "A provider enumerated the artifact. The ONLY exit from UNKNOWN, and it requires an "
        "observation rather than a decision — which is what 'UNKNOWN must never disappear through "
        "relabelling' means when written as a graph.",
    ),
    Transition(
        DISCOVERED,
        GENERATED,
        "Ω²-S-02",
        "A generation marker was found, or the producing generator was identified.",
    ),
    Transition(
        DISCOVERED,
        TRANSIENT,
        "Ω²-S-03",
        "The artifact was declared not to persist. Transience is the one custody claim no "
        "measurement "
        "can confirm, so it is the one that must be argued.",
        requires_reason=True,
    ),
    Transition(
        DISCOVERED,
        ARCHIVED,
        "Ω²-S-04",
        "The artifact fell under an immutability guard, so its bytes are owned by history.",
    ),
    Transition(
        GENERATED,
        ARCHIVED,
        "Ω²-S-05",
        "Generated output was frozen. Both facts remain true because ARCHIVED replaces only the "
        "CUSTODY position.",
    ),
    Transition(
        GENERATED,
        DISCOVERED,
        "Ω²-S-06",
        "The generation marker is gone, so the bytes are authored now. This reduces the "
        "obligation on "
        "whoever owns the generator, so it is argued.",
        requires_reason=True,
    ),
    Transition(
        TRANSIENT,
        DISCOVERED,
        "Ω²-S-07",
        "A declared transient persisted, so the claim was wrong. Needs no argument: this edge "
        "INCREASES obligation, and an increase never has to be excused.",
    ),
    Transition(
        ARCHIVED,
        DISCOVERED,
        "Ω²-S-08",
        "An immutability guard was lifted. Thawing frozen bytes is a decision about history.",
        requires_reason=True,
    ),
    # --------------------------------------------------------------------------- ATTRIBUTION
    Transition(
        UNATTRIBUTED,
        ATTRIBUTED,
        "Ω²-S-09",
        "Authority resolution terminated above the universal fallback. Blocked from UNKNOWN "
        "because "
        "an owner for an artifact nobody has observed is an owner of nothing.",
        blocked_by=(UNKNOWN,),
    ),
    Transition(
        ATTRIBUTED,
        UNATTRIBUTED,
        "Ω²-S-10",
        "A named authority stopped answering and resolution fell to the fallback. Losing an owner "
        "is "
        "the reduction of obligation this graph most needs argued.",
        requires_reason=True,
    ),
    # ---------------------------------------------------------------------------- GOVERNANCE
    Transition(
        UNGOVERNED,
        GOVERNED,
        "Ω²-S-11",
        "A governing rule claimed the artifact. Blocked while UNATTRIBUTED, because governance by "
        "the "
        "authority of last resort is ownership in name only — the population Ω-1's "
        "``authority_of_last_resort`` ratchet holds at zero.",
        blocked_by=(UNKNOWN, UNATTRIBUTED),
    ),
    Transition(
        UNGOVERNED,
        EXEMPTED,
        "Ω²-S-12",
        "A governing rule placed the artifact outside a measurement scope. DELIVERABLE Ω-2.4: "
        "blocked "
        "while UNKNOWN, so an unknown artifact can never become exempted, and argued, so an "
        "exemption "
        "can never be silent.",
        requires_reason=True,
        blocked_by=(UNKNOWN,),
    ),
    Transition(
        GOVERNED,
        EXEMPTED,
        "Ω²-S-13",
        "A governed artifact was placed outside the scope it was inside.",
        requires_reason=True,
    ),
    Transition(
        EXEMPTED,
        GOVERNED,
        "Ω²-S-14",
        "An exemption was withdrawn and the artifact re-entered the measurement scope. An "
        "increase in "
        "obligation, so no argument is demanded.",
        blocked_by=(UNATTRIBUTED,),
    ),
    Transition(
        GOVERNED,
        UNGOVERNED,
        "Ω²-S-15",
        "The governing rule stopped claiming the artifact. The largest single reduction of "
        "obligation "
        "available on this axis.",
        requires_reason=True,
    ),
    Transition(
        EXEMPTED,
        UNGOVERNED,
        "Ω²-S-16",
        "The rule that declared the exemption stopped claiming the artifact at all, so the "
        "exemption's argument no longer has an owner.",
        requires_reason=True,
    ),
    # --------------------------------------------------------------------------- MEASUREMENT
    Transition(
        UNMEASURED,
        MEASURED,
        "Ω²-S-17",
        "An observation was obtained. This edge deliberately carries NO governance guard: "
        "measuring "
        "an ungoverned artifact is legitimate and common, and refusing it here would re-fuse the "
        "two "
        "axes Deliverable Ω-2.5 separates.",
        blocked_by=(UNKNOWN,),
    ),
    Transition(
        UNMEASURED,
        UNMEASURABLE,
        "Ω²-S-18",
        "An observation cannot be obtained, and the obstacle is named. Blocked while UNKNOWN, "
        "because "
        "'unmeasurable' asserted over an unobserved artifact is a discovery failure relabelled as "
        "a "
        "measurement property — the third relabelling escape Ω-2.4 forbids.",
        requires_reason=True,
        blocked_by=(UNKNOWN,),
    ),
    Transition(
        MEASURED,
        UNMEASURED,
        "Ω²-S-19",
        "A previously held observation was invalidated or withdrawn.",
        requires_reason=True,
    ),
    Transition(
        MEASURED,
        UNMEASURABLE,
        "Ω²-S-20",
        "An artifact that was once measured can no longer be, and the obstacle is named.",
        requires_reason=True,
    ),
    Transition(
        UNMEASURABLE,
        MEASURED,
        "Ω²-S-21",
        "The obstacle was removed and an observation was obtained after all. The edge that makes "
        "UNMEASURABLE a finding rather than a terminus.",
    ),
    # ------------------------------------------------------------------------- CERTIFICATION
    Transition(
        UNCERTIFIED,
        CERTIFIED,
        "Ω²-S-22",
        "Every certification input was satisfied. DELIVERABLE Ω-2.4's first requirement lives in "
        "this "
        "edge's guard: UNKNOWN never certifies, and neither does UNATTRIBUTED, UNGOVERNED or "
        "CONTRADICTED. Four obligations, expressed structurally.",
        blocked_by=(UNKNOWN, UNATTRIBUTED, UNGOVERNED, CONTRADICTED),
    ),
    Transition(
        UNCERTIFIED,
        CONDITIONALLY_CERTIFIED,
        "Ω²-S-23",
        "Every required input was satisfied and a conditional one was not. UNGOVERNED is NOT a "
        "blocker here and UNKNOWN is: a conditional pass may carry a governance shortfall as its "
        "named condition, but never an artifact nobody has observed.",
        requires_reason=True,
        blocked_by=(UNKNOWN, UNATTRIBUTED, CONTRADICTED),
    ),
    Transition(
        UNCERTIFIED,
        REJECTED,
        "Ω²-S-24",
        "A required input was definitively unsatisfied. REACHABLE FROM UNKNOWN, deliberately: "
        "rejecting what nobody could find is one of the four dispositions Ω-2.4 requires an "
        "UNKNOWN "
        "to be able to reach.",
        requires_reason=True,
    ),
    Transition(
        UNCERTIFIED,
        UNVERIFIABLE,
        "Ω²-S-25",
        "An input could not be evaluated, so no decision was reachable. Also available from "
        "UNKNOWN, "
        "and distinct from REJECTED because 'we cannot tell' is not 'no'.",
        requires_reason=True,
    ),
    Transition(
        CONDITIONALLY_CERTIFIED,
        CERTIFIED,
        "Ω²-S-26",
        "The named condition was discharged. Carries the same four guards as Ω²-S-22, so a "
        "conditional "
        "pass cannot be used as a side door into full certification.",
        blocked_by=(UNKNOWN, UNATTRIBUTED, UNGOVERNED, CONTRADICTED),
    ),
    Transition(
        CONDITIONALLY_CERTIFIED,
        REJECTED,
        "Ω²-S-27",
        "The named condition was not discharged and a required input failed.",
        requires_reason=True,
    ),
    Transition(
        CONDITIONALLY_CERTIFIED,
        UNVERIFIABLE,
        "Ω²-S-28",
        "An input that was evaluable at decision time no longer is.",
        requires_reason=True,
    ),
    Transition(
        CERTIFIED,
        CONDITIONALLY_CERTIFIED,
        "Ω²-S-29",
        "A conditional input regressed after certification, so the disposition is downgraded "
        "rather "
        "than quietly retained.",
        requires_reason=True,
    ),
    Transition(
        CERTIFIED,
        REJECTED,
        "Ω²-S-30",
        "Certification was revoked because a required input failed after the decision. The edge "
        "that "
        "makes CERTIFIED non-terminal, so a stale certificate is refusable.",
        requires_reason=True,
    ),
    Transition(
        CERTIFIED,
        UNVERIFIABLE,
        "Ω²-S-31",
        "The evidence a certification rested on became unevaluable, so the decision no longer "
        "stands "
        "and no replacement is reachable.",
        requires_reason=True,
    ),
    Transition(
        REJECTED,
        UNCERTIFIED,
        "Ω²-S-32",
        "The decision was re-opened for fresh evaluation. Routing re-entry through UNCERTIFIED "
        "rather "
        "than straight to CERTIFIED means a rejection can only be reversed by a NEW decision, "
        "which "
        "is a new record, which is a new audit entry.",
        requires_reason=True,
    ),
    Transition(
        UNVERIFIABLE,
        UNCERTIFIED,
        "Ω²-S-33",
        "The obstacle to evaluation was removed, so a decision is reachable again.",
    ),
    Transition(
        UNVERIFIABLE,
        REJECTED,
        "Ω²-S-34",
        "Evaluation became possible and the answer was no.",
        requires_reason=True,
    ),
    # --------------------------------------------------------------------------- CONSISTENCY
    Transition(
        CONSISTENT,
        CONTRADICTED,
        "Ω²-S-35",
        "An open contradiction names this artifact. The reason carries the contradiction "
        "identifier, "
        "so the vector points back into the register rather than merely flagging.",
        requires_reason=True,
    ),
    Transition(
        CONTRADICTED,
        CONSISTENT,
        "Ω²-S-36",
        "Every contradiction naming this artifact left the open resolution states. Argued, because "
        "clearing a contradiction is the most consequential reduction of obligation in the graph "
        "— it "
        "unblocks certification.",
        requires_reason=True,
    ),
)


class TransitionGraph:
    """The declared edges, indexed for lookup. A duplicate edge RAISES rather than overwriting.

    WHY A DUPLICATE IS A FAULT. Two edges between one pair would differ in guard or rule id, and
    which applied would depend on table order — so the same attempted transition would be permitted
    or refused according to where somebody appended a line. A rule whose outcome depends on file
    order is not a rule.
    """

    def __init__(self, transitions: Iterable[Transition] = INITIAL_TRANSITIONS) -> None:
        self._by_edge: dict[tuple[str, str], Transition] = {}
        self._by_rule: dict[str, Transition] = {}
        for transition in transitions:
            self.register(transition)

    def register(self, transition: Transition) -> Transition:
        edge = (transition.source.name, transition.target.name)
        existing = self._by_edge.get(edge)
        if existing is not None:
            raise StateError(
                f"the edge {edge[0]} -> {edge[1]} is already declared as {existing.rule}, and a "
                f"second declaration as {transition.rule} would make the applicable guard depend "
                f"on "
                "table order"
            )
        clashing = self._by_rule.get(transition.rule)
        if clashing is not None:
            raise StateError(
                f"rule id {transition.rule!r} already names {clashing.source.name} -> "
                f"{clashing.target.name}; one id for two edges makes an audit record ambiguous "
                f"about "
                "which transition it describes"
            )
        self._by_edge[edge] = transition
        self._by_rule[transition.rule] = transition
        return transition

    def edge(self, source: GovernanceState, target: GovernanceState) -> Transition | None:
        """The declared transition, or ``None``. ABSENCE IS THE REFUSAL, and it is the default."""
        return self._by_edge.get((source.name, target.name))

    def outgoing(self, source: GovernanceState) -> tuple[Transition, ...]:
        return tuple(sorted(t for t in self._by_edge.values() if t.source == source))

    def incoming(self, target: GovernanceState) -> tuple[Transition, ...]:
        return tuple(sorted(t for t in self._by_edge.values() if t.target == target))

    def on_axis(self, axis: Axis) -> tuple[Transition, ...]:
        return tuple(sorted(t for t in self._by_edge.values() if t.axis == axis))

    def rule(self, identifier: str) -> Transition:
        try:
            return self._by_rule[identifier]
        except KeyError:
            raise StateError(
                f"{identifier!r} is not a declared transition rule; an audit record citing it "
                f"would "
                "name a transition this graph cannot perform"
            ) from None

    def known(self) -> tuple[Transition, ...]:
        return tuple(sorted(self._by_edge.values()))

    def __len__(self) -> int:
        return len(self._by_edge)


def default_graph(transitions: Iterable[Transition] = ()) -> TransitionGraph:
    """A graph holding the thirty-six shipped edges, plus whatever the caller registers."""
    graph = TransitionGraph()
    for transition in transitions:
        graph.register(transition)
    return graph


# --------------------------------------------------------------------------------------- status


@dataclass(frozen=True, order=True)
class GovernanceStatus:
    """One position per axis. The construction that eliminates silent governance states.

    ``__post_init__`` ENFORCES ONLY THE LOCAL INVARIANT — no axis holds two positions — and says
    nothing about which axes must be present. That division is deliberate: completeness is relative
    to a REGISTERED axis set, and a type that quantified over a module tuple would refuse
    construction the moment a deployment registered a seventh concern, failing Ω∞ Rule 3 inside the
    model's own constructor. ``assert_total`` measures completeness against the registry, so
    widening the model produces a countable population of incomplete records instead of a migration.
    """

    states: tuple[GovernanceState, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "states", tuple(sorted(self.states)))
        seen: dict[str, GovernanceState] = {}
        for state in self.states:
            duplicate = seen.get(state.axis.name)
            if duplicate is not None:
                raise StateError(
                    f"a status names both {duplicate.name} and {state.name} on axis "
                    f"{state.axis.name}; two positions on one axis is not a richer record, it is "
                    f"an "
                    "unresolved disagreement recorded as a fact"
                )
            seen[state.axis.name] = state

    def axes(self) -> tuple[Axis, ...]:
        return tuple(sorted({state.axis for state in self.states}))

    def position(self, axis: Axis) -> GovernanceState:
        """This status's position on one axis. RAISES if silent about it, rather than returning
        None.

        A ``None`` would let a caller treat "no position recorded" as a benign default, which is the
        silent state this package removes. The refusal names the axis, so the fix is obvious.
        """
        for state in self.states:
            if state.axis == axis:
                return state
        raise StateError(
            f"this status holds no position on axis {axis.name}; it predates the axis's "
            f"registration, "
            "and assert_total is what reports the whole population in that condition"
        )

    def holds(self, state: GovernanceState) -> bool:
        return state in self.states

    def names(self) -> tuple[str, ...]:
        return tuple(state.name for state in self.states)

    def vector(self) -> tuple[tuple[str, str], ...]:
        """``(axis, state)`` pairs, sorted. The canonical identity of a governance position."""
        return tuple((state.axis.name, state.name) for state in self.states)

    def as_record(self) -> dict[str, object]:
        return {state.axis.name: state.name for state in self.states}

    def __contains__(self, state: object) -> bool:
        return isinstance(state, GovernanceState) and state in self.states

    def __iter__(self) -> Iterator[GovernanceState]:
        return iter(self.states)

    def __len__(self) -> int:
        return len(self.states)


def initial_status(registry: StateRegistry) -> GovernanceStatus:
    """The vector a never-touched artifact occupies, over the axes the REGISTRY actually holds.

    ``registry`` is required and has no default, so the baseline is always relative to a named
    vocabulary. A default would make "the initial status" a global fact, and the whole point of an
    open-world model is that the vocabulary is a deployment's choice.
    """
    return GovernanceStatus(tuple(registry.initial(axis) for axis in registry.axes()))


@dataclass(frozen=True, order=True)
class StateChange:
    """The audit record of one applied transition. What makes a transition AUDITABLE.

    ``coordinate`` IS A ``TemporalCoordinate``, NOT A STRING. A string timestamp asserts an unstated
    frame, an unstated scale and a total order over every change ever recorded; the coordinate
    states all three and admits that two changes recorded by different observers may be CONCURRENT.

    It is OPTIONAL, and the option is not laziness: a deployment that has registered no clock has no
    honest coordinate to record, and inventing one would be worse than admitting its absence.
    ``rule`` and ``reason`` carry the audit weight regardless.
    """

    subject: str
    axis: str
    source: str
    target: str
    rule: str
    reason: str = ""
    coordinate: TemporalCoordinate | None = None

    def as_record(self) -> dict[str, object]:
        record: dict[str, object] = {
            "subject": self.subject,
            "axis": self.axis,
            "source": self.source,
            "target": self.target,
            "rule": self.rule,
            "reason": self.reason,
        }
        if self.coordinate is not None:
            record["coordinate"] = self.coordinate.as_record()
        return record


def check(
    status: GovernanceStatus,
    target: GovernanceState,
    *,
    reason: str = "",
    graph: TransitionGraph,
) -> tuple[Transition | None, str]:
    """Machine-check one transition WITHOUT applying it. Returns the edge, or ``None`` and why.

    Separated from ``advance`` because a gate must report every refusal in a population rather than
    stop at the first, and a reporter that had to catch exceptions could not tell a refused
    transition from a broken one.
    """
    try:
        source = status.position(target.axis)
    except StateError as exc:
        return None, str(exc)
    if source == target:
        return None, (
            f"already at {target.name} on axis {target.axis.name}; a no-op transition would write "
            f"an "
            "audit record describing no change"
        )
    transition = graph.edge(source, target)
    if transition is None:
        return None, (
            f"no declared transition from {source.name} to {target.name} on axis "
            f"{target.axis.name}; "
            "the edge's absence IS the refusal, and adding one is a deliberate widening of what "
            "this graph permits"
        )
    blocking = [state.name for state in transition.blocked_by if status.holds(state)]
    if blocking:
        return None, (
            f"{transition.rule} is blocked while this artifact holds {', '.join(blocking)}; the "
            f"guard "
            "is a cross-axis law and not advice"
        )
    if transition.requires_reason and not reason.strip():
        return None, (
            f"{transition.rule} reduces an obligation and states no reason; an unargued reduction "
            f"of "
            "obligation is indistinguishable from one made to pass"
        )
    return transition, ""


def advance(
    status: GovernanceStatus,
    target: GovernanceState,
    *,
    subject: str,
    reason: str = "",
    graph: TransitionGraph,
    clock: ClockProvider | None = None,
) -> tuple[GovernanceStatus, StateChange]:
    """Apply one transition, returning the new status AND its audit record.

    THE RECORD IS RETURNED, NOT OPTIONAL. A signature returning only the new status would let a
    caller move an artifact and record nothing, so "no silent governance states" would hold for the
    vector while failing for the history. The two are produced together so they cannot diverge.
    """
    if not subject.strip():
        raise StateError(
            "a state change must name its subject; an audit record about an unnamed artifact "
            "cannot be joined to the artifact it describes"
        )
    transition, refusal = check(status, target, reason=reason, graph=graph)
    if transition is None:
        raise StateError(f"{subject}: {refusal}")
    replaced = tuple(s for s in status.states if s.axis != target.axis)
    moved = GovernanceStatus((*replaced, target))
    change = StateChange(
        subject=subject,
        axis=transition.axis.name,
        source=transition.source.name,
        target=transition.target.name,
        rule=transition.rule,
        reason=reason,
        coordinate=clock.read() if clock is not None else None,
    )
    return moved, change


# -------------------------------------------------------------------------------------- reporting


def assert_total(statuses: Iterable[tuple[str, GovernanceStatus]], registry: StateRegistry) -> None:
    """Refuse a population in which any artifact is silent about any REGISTERED axis.

    THE GLOBAL INVARIANT, held where the population is held. This is what catches an axis added
    AFTER a population was built — without it, widening the model would silently grandfather every
    existing record into the new silence, which is how a governance concern becomes unmeasurable on
    the day it is introduced.
    """
    axes = registry.axes()
    incomplete: list[str] = []
    for subject, status in statuses:
        positioned = {state.axis.name for state in status.states}
        absent = sorted(axis.name for axis in axes if axis.name not in positioned)
        if absent:
            incomplete.append(f"{subject} ({', '.join(absent)})")
    if incomplete:
        raise StateError(
            "these artifacts hold no position on at least one registered axis, so their governance "
            "record is silent about a concern the model requires them to answer: "
            + ", ".join(sorted(incomplete)[:20])
        )


def census(
    statuses: Iterable[GovernanceStatus], registry: StateRegistry
) -> dict[str, dict[str, int]]:
    """Population count per axis per state. EVERY declared position appears, including the zeroes.

    THE ZEROES ARE THE POINT. A census omitting empty states would make "no artifact is UNKNOWN" and
    "UNKNOWN is not a state this report knows about" look identical, and the second is how a
    population becomes invisible.
    """
    counts: dict[str, dict[str, int]] = {
        axis.name: {state.name: 0 for state in registry.on_axis(axis)} for axis in registry.axes()
    }
    for status in statuses:
        for state in status.states:
            bucket = counts.setdefault(state.axis.name, {})
            bucket[state.name] = bucket.get(state.name, 0) + 1
    return counts


def population_of(
    statuses: Iterable[tuple[str, GovernanceStatus]], state: GovernanceState
) -> tuple[str, ...]:
    """Every subject holding one state. The form in which a population can be driven to zero."""
    return tuple(sorted(subject for subject, status in statuses if status.holds(state)))


# ------------------------------------------------------------------- Ω-2.5, governed vs measured

#: The five combinations Deliverable Ω-2.5 requires, each named as the pair of positions a
#: single-slot disposition cannot hold at once. Held as DATA so "the model supports all
#: combinations" is discharged by execution in ``separation_report`` rather than by a paragraph
#: asserting it.
SEPARATIONS: tuple[tuple[str, GovernanceState, GovernanceState], ...] = (
    ("governed but not measured", GOVERNED, UNMEASURED),
    ("measured but uncertified", MEASURED, UNCERTIFIED),
    ("certified but archived", CERTIFIED, ARCHIVED),
    ("generated but governed", GENERATED, GOVERNED),
    ("transient but attributed", TRANSIENT, ATTRIBUTED),
)


def separation_report(
    statuses: Iterable[tuple[str, GovernanceStatus]] = (),
) -> tuple[dict[str, object], ...]:
    """For each required combination: is it EXPRESSIBLE, and how many artifacts hold it.

    EXPRESSIBLE AND POPULATED ARE DIFFERENT CLAIMS, and both are reported. Expressibility is a
    property of the model — the two states sit on different axes, so a vector can hold both — and it
    is what Ω-2.5 requires. Population is a property of this repository today, and reporting it
    separately stops an empty population from looking like a model that cannot express the case.
    """
    held = tuple(statuses)
    report: list[dict[str, object]] = []
    for description, first, second in SEPARATIONS:
        subjects = tuple(
            sorted(s for s, status in held if status.holds(first) and status.holds(second))
        )
        report.append(
            {
                "combination": description,
                "states": [first.name, second.name],
                "axes": [first.axis.name, second.axis.name],
                "expressible": first.axis != second.axis,
                "population": len(subjects),
                "examples": list(subjects[:3]),
            }
        )
    return tuple(report)


def vocabulary_report(registry: StateRegistry, graph: TransitionGraph) -> dict[str, object]:
    """The declared vocabulary, as a document. Read-only; asserts nothing about any artifact."""
    return {
        "axes": {axis.name: axis.description for axis in registry.axes()},
        "states": {
            axis.name: [
                {"state": s.name, "initial": s.initial, "description": s.description}
                for s in registry.on_axis(axis)
            ]
            for axis in registry.axes()
        },
        "transitions": [t.as_record() for t in graph.known()],
        "required_states_present": sorted(n for n in REQUIRED_STATE_NAMES if n in registry),
        "required_states_absent": sorted(n for n in REQUIRED_STATE_NAMES if n not in registry),
        "openness": (
            "States and axes are registry values, not enum members, and the axis set is DERIVED "
            "from the declared states rather than held as a separate table. Registering a seventh "
            "governance concern is two declare_name calls and no edit. GovernanceStatus enforces "
            "only that no axis holds two positions; completeness is measured against this registry "
            "by assert_total, so a widened model yields a countable population rather than a "
            "migration."
        ),
    }


__all__ = [
    "ARCHIVED",
    "ATTRIBUTED",
    "ATTRIBUTION",
    "CERTIFICATION",
    "CERTIFIED",
    "CONDITIONALLY_CERTIFIED",
    "CONSISTENCY",
    "CONSISTENT",
    "CONTRADICTED",
    "CUSTODY",
    "DISCOVERED",
    "EXEMPTED",
    "GENERATED",
    "GOVERNANCE",
    "GOVERNED",
    "INITIAL_AXES",
    "INITIAL_STATES",
    "INITIAL_TRANSITIONS",
    "MEASURED",
    "MEASUREMENT",
    "REJECTED",
    "REQUIRED_STATE_NAMES",
    "SEPARATIONS",
    "TRANSIENT",
    "UNATTRIBUTED",
    "UNCERTIFIED",
    "UNGOVERNED",
    "UNKNOWN",
    "UNMEASURABLE",
    "UNMEASURED",
    "UNVERIFIABLE",
    "Axis",
    "GovernanceState",
    "GovernanceStatus",
    "StateChange",
    "StateError",
    "StateRegistry",
    "Transition",
    "TransitionGraph",
    "advance",
    "assert_total",
    "census",
    "check",
    "default_graph",
    "default_states",
    "initial_status",
    "population_of",
    "separation_report",
    "vocabulary_report",
]
