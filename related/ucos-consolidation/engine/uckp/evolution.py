"""UCKP Layer Zero — the Universal Evolution Model (Article 14).

Evolution observes, learns, reasons, simulates, analyses impact and dependencies,
resolves authority, implements, validates, verifies, replays, certifies, transitions
and assimilates — and then begins again. Article 14 adds three constraints that shape
the whole module: it appends, it never rewrites, and it never terminates.

"Never terminates" is easy to write and easy to violate, so it is encoded rather than
promised. :func:`next_stage` wraps from the last stage back to the first, so there is no
stage from which nothing follows, and :meth:`EvolutionLedger.is_terminated` is a method
that always returns ``False`` because there is no state it could return ``True`` from.
An evolution model with a terminal stage would eventually stop, and a constitution that
stops evolving becomes a description of the past.

"Never rewrites" is enforced by :meth:`EvolutionLedger.append`, which admits only the
stage the cycle says comes next. A caller cannot skip validation to reach certification,
because skipping is exactly how an unproven claim acquires a certificate.

"Never terminates" and "never bounded" are different claims, and the second one also has
to be encoded. :data:`EvolutionStage` is a closed enumeration, so on its own it would fix
the cycle at the fifteen stages that happened to be known when it was written, and a
sixteenth would be a code edit. INV-14 requires that *every* vocabulary admit an unknown
future member, so the stage set is also published as a vocabulary
(:func:`evolution_stage_vocabulary`) — the same treatment
:data:`~engine.uckp.vocabulary.FACET_VOCABULARY_INSTANCE` gives the equally closed
:class:`~engine.uckp.facets.Facet`. The enum remains the single home of the seeded cycle
and the vocabulary is derived from it, so the two cannot disagree; what the vocabulary
adds is that the stage set is now *measured* against INV-14 by
:meth:`~engine.uckp.vocabulary.VocabularyRegistry.is_extensible` instead of being the one
constitutional vocabulary nothing probed.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum

from engine.uckp.canonical import content_hash
from engine.uckp.errors import EvolutionError
from engine.uckp.vocabulary import Term, Vocabulary


class EvolutionStage(str, Enum):
    """The fifteen stages of the perpetual constitutional cycle."""

    OBSERVE = "observe"
    LEARN = "learn"
    REASON = "reason"
    SIMULATE = "simulate"
    IMPACT_ANALYSIS = "impact-analysis"
    DEPENDENCY_ANALYSIS = "dependency-analysis"
    AUTHORITY_RESOLUTION = "authority-resolution"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    VERIFICATION = "verification"
    REPLAY = "replay"
    CERTIFICATION = "certification"
    STATE_TRANSITION = "state-transition"
    KNOWLEDGE_ASSIMILATION = "knowledge-assimilation"
    CONTINUATION = "continuation"

    @classmethod
    def coerce(cls, value: object) -> EvolutionStage:
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.value == text:
                return member
        raise EvolutionError("unknown evolution stage", stage=str(value))


#: The cycle, in order. Derived from the enum so the two can never disagree.
EVOLUTION_CYCLE: tuple[EvolutionStage, ...] = tuple(EvolutionStage)

#: How many stages one full cycle contains.
CYCLE_LENGTH = len(EVOLUTION_CYCLE)


def next_stage(stage: EvolutionStage | str) -> EvolutionStage:
    """The stage that follows ``stage``, wrapping forever (Article 14)."""
    current = EvolutionStage.coerce(stage)
    index = EVOLUTION_CYCLE.index(current)
    return EVOLUTION_CYCLE[(index + 1) % CYCLE_LENGTH]


def is_terminal(stage: EvolutionStage | str) -> bool:
    """Always false. No stage of a perpetual cycle is terminal."""
    EvolutionStage.coerce(stage)
    return False


#: The vocabulary id under which the stage set is published.
EVOLUTION_STAGE = "uckp.evolution-stage"

#: The vocabulary id under which subject types are published (Phase 2 extension).
EVOLUTION_SUBJECT_TYPE = "uckp.evolution-subject-type"

#: The vocabulary id under which requirement evolution events are published (Phase 2).
REQUIREMENT_EVOLUTION_EVENT = "uckp.requirement-evolution-event"

#: The document form :meth:`EvolutionLedger.to_document` emits and
#: :meth:`EvolutionLedger.from_document` accepts. Named once, so a projection and its
#: inverse cannot disagree about what they are exchanging, and so a loader can refuse a
#: document that merely happens to carry a ``records`` array.
LEDGER_SCHEMA = "ucos-uckp-evolution-ledger"

#: The version of :data:`LEDGER_SCHEMA`. A loader that cannot name the version it accepts
#: cannot tell a future form from a malformed one.
LEDGER_VERSION = "1.1.0"


def evolution_stage_vocabulary() -> Vocabulary:
    """The stage set as an open vocabulary, derived from :data:`EVOLUTION_CYCLE`.

    Every term is generated from the cycle — its position becomes the rank and
    :func:`next_stage` becomes its successor — so this is a projection of the cycle and
    not a second list of stages to keep in step with the first. Registering it is what
    brings the stage set under INV-14: a registry holding it reports itself closed unless
    the stage set admits a term no stage declares.
    """
    return Vocabulary(
        EVOLUTION_STAGE,
        "the stages of the perpetual constitutional cycle, with their lawful successors",
        tuple(
            Term(
                stage.value,
                f"stage {index} of {CYCLE_LENGTH} in the perpetual constitutional cycle",
                rank=index,
                successors=(next_stage(stage).value,),
            )
            for index, stage in enumerate(EVOLUTION_CYCLE)
        ),
    )


def evolution_subject_type_vocabulary() -> Vocabulary:
    """Subject types tracked by evolution ledger (Phase 2 REQ-23 extension).

    Extensible vocabulary of subject types that can undergo evolution. Seeded with
    known types (PROGRAMME, CAPABILITY, DECISION, REQUIREMENT) but open to future
    types per INV-14 (every vocabulary admits unknown future members).

    This vocabulary enables subject type classification without fixing a closed set,
    satisfying the Phase 2 requirement that evolution support requirements while
    preserving infinite expansion capability.
    """
    return Vocabulary(
        EVOLUTION_SUBJECT_TYPE,
        "types of subjects that undergo constitutional evolution",
        (
            Term("PROGRAMME", "a constitutional programme undergoing evolution", rank=0),
            Term("CAPABILITY", "a capability undergoing evolution", rank=1),
            Term("DECISION", "a constitutional decision undergoing evolution", rank=2),
            Term("REQUIREMENT", "a requirement undergoing evolution", rank=3),
            Term("PRINCIPLE", "a universal principle undergoing evolution", rank=4),
            Term("KNOWLEDGE", "knowledge undergoing evolution", rank=5),
        ),
    )


def requirement_evolution_event_vocabulary() -> Vocabulary:
    """Requirement-specific evolution events (Phase 2 REQ-23 extension).

    Extensible vocabulary of requirement lifecycle events. Seeded with known
    requirement evolution events but open to future events per INV-14.

    These events track requirement lifecycle: creation, modification, refinement,
    merging, supersession, deprecation, reactivation, splitting, and relationship
    changes.
    """
    return Vocabulary(
        REQUIREMENT_EVOLUTION_EVENT,
        "lifecycle events specific to requirement evolution",
        (
            Term("CREATED", "requirement created (initial admission)", rank=0),
            Term("MODIFIED", "requirement content modified", rank=1),
            Term("REFINED", "requirement refined (scope/criteria clarified)", rank=2),
            Term("MERGED", "requirement merged with another requirement", rank=3),
            Term("SUPERSEDED", "requirement superseded by newer requirement", rank=4),
            Term("DEPRECATED", "requirement deprecated (no longer applicable)", rank=5),
            Term("REACTIVATED", "deprecated requirement reactivated", rank=6),
            Term("SPLIT", "requirement split into multiple requirements", rank=7),
            Term("RELATION_CHANGED", "requirement relationships changed", rank=8),
        ),
    )


@dataclass(frozen=True, slots=True)
class EvolutionRecord:
    """One appended step of the perpetual cycle.

    Phase 2 extension: Added optional subject_type and event_type fields to support
    requirement evolution (REQ-23 work item). Backward compatible: existing records
    without these fields remain valid.
    """

    cycle: int
    stage: EvolutionStage
    subject: str
    outcome: str
    digest: str
    findings: tuple[str, ...] = field(default_factory=tuple)
    subject_type: str | None = None
    event_type: str | None = None

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "cycle": self.cycle,
            "stage": self.stage.value,
            "subject": self.subject,
            "outcome": self.outcome,
            "digest": self.digest,
            "findings": list(self.findings),
        }
        if self.subject_type is not None:
            result["subject_type"] = self.subject_type
        if self.event_type is not None:
            result["event_type"] = self.event_type
        return result

    @classmethod
    def from_dict(cls, data: object) -> EvolutionRecord:
        record = data if isinstance(data, dict) else {}
        return cls(
            cycle=int(record.get("cycle", 0)),
            stage=EvolutionStage.coerce(record.get("stage")),
            subject=str(record.get("subject", "")),
            outcome=str(record.get("outcome", "")),
            digest=str(record.get("digest", "")),
            findings=tuple(str(item) for item in record.get("findings") or ()),
            subject_type=str(record["subject_type"]) if "subject_type" in record else None,
            event_type=str(record["event_type"]) if "event_type" in record else None,
        )


class EvolutionLedger:
    """The append-only record of constitutional evolution."""

    __slots__ = ("_records",)

    def __init__(self, records: Iterable[EvolutionRecord] = ()) -> None:
        self._records: list[EvolutionRecord] = []
        for record in records:
            self.append(record)

    def append(self, record: EvolutionRecord) -> EvolutionRecord:
        """Append the next lawful stage. Skipping and rewriting are both refused."""
        if not self._records:
            if record.stage is not EVOLUTION_CYCLE[0] or record.cycle != 0:
                raise EvolutionError(
                    "evolution must begin at the first stage of cycle zero",
                    stage=record.stage.value,
                    cycle=record.cycle,
                )
            self._records.append(record)
            return record
        previous = self._records[-1]
        expected_stage = next_stage(previous.stage)
        wrapped = expected_stage is EVOLUTION_CYCLE[0]
        expected_cycle = previous.cycle + 1 if wrapped else previous.cycle
        if record.stage is not expected_stage:
            raise EvolutionError(
                "evolution stages may not be skipped or reordered",
                expected=expected_stage.value,
                declared=record.stage.value,
            )
        if record.cycle != expected_cycle:
            raise EvolutionError(
                "evolution cycle must advance exactly once per full cycle",
                expected=expected_cycle,
                declared=record.cycle,
            )
        self._records.append(record)
        return record

    def extend(self, records: Iterable[EvolutionRecord]) -> tuple[EvolutionRecord, ...]:
        return tuple(self.append(record) for record in records)

    def records(self) -> tuple[EvolutionRecord, ...]:
        return tuple(self._records)

    def __len__(self) -> int:
        return len(self._records)

    def current_stage(self) -> EvolutionStage | None:
        return self._records[-1].stage if self._records else None

    def expected_stage(self) -> EvolutionStage:
        """The stage the ledger will accept next. Always defined (Article 14)."""
        if not self._records:
            return EVOLUTION_CYCLE[0]
        return next_stage(self._records[-1].stage)

    def cycles(self) -> int:
        return (self._records[-1].cycle + 1) if self._records else 0

    def completed_cycles(self) -> int:
        """Cycles that reached the final stage — the ones with a state transition."""
        return sum(1 for record in self._records if record.stage is EVOLUTION_CYCLE[-1])

    def is_terminated(self) -> bool:
        """Always false. There is no ledger state from which nothing may follow."""
        return False

    def stage_records(self, stage: EvolutionStage | str) -> tuple[EvolutionRecord, ...]:
        resolved = EvolutionStage.coerce(stage)
        return tuple(record for record in self._records if record.stage is resolved)

    def subject_type_records(self, subject_type: str) -> tuple[EvolutionRecord, ...]:
        """Records for a specific subject type (Phase 2 REQ-23 extension).

        Returns records matching the given subject_type. Records without subject_type
        (pre-Phase 2 records) are excluded from results.
        """
        return tuple(record for record in self._records if record.subject_type == subject_type)

    def event_type_records(self, event_type: str) -> tuple[EvolutionRecord, ...]:
        """Records for a specific event type (Phase 2 REQ-23 extension).

        Returns records matching the given event_type. Records without event_type
        (pre-Phase 2 records) are excluded from results.
        """
        return tuple(record for record in self._records if record.event_type == event_type)

    def findings(self) -> tuple[str, ...]:
        return tuple(finding for record in self._records for finding in record.findings)

    def to_document(self) -> dict[str, object]:
        return {
            "schema": LEDGER_SCHEMA,
            "version": LEDGER_VERSION,
            "counts": {
                "records": len(self._records),
                "cycles": self.cycles(),
                "completed_cycles": self.completed_cycles(),
                "findings": len(self.findings()),
            },
            "cycle_definition": [stage.value for stage in EVOLUTION_CYCLE],
            "expected_stage": self.expected_stage().value,
            "terminated": self.is_terminated(),
            "records": [record.to_dict() for record in self._records],
        }

    @classmethod
    def from_document(cls, document: object) -> EvolutionLedger:
        """Rehydrate a ledger from the document :meth:`to_document` produced.

        Article 14 holds that evolution appends, never rewrites and never terminates.
        Until this method existed that claim was only checkable *inside* the process that
        did the appending: the ledger could project itself to canonical JSON and had no
        inverse, so a published evolution history could be read by a human, diffed by CI
        and trusted by a downstream programme without anything ever re-applying the rules
        it was supposed to have been built under. An append-only history that cannot be
        loaded is an append-only history nobody can falsify.

        Loading is therefore a verification rather than a deserialization. Every record is
        replayed through :meth:`append`, so a history with a skipped stage, a reordered
        stage, a renumbered cycle or an injected record is refused here exactly as it
        would have been refused when it was written — and refused with the same error, from
        the same code path, because there is only one code path. The inverse of a
        content-addressed projection has to be as strict as the projection or the digest
        stops meaning anything.

        ``schema`` is checked because a loader that accepts any object carrying a
        ``records`` array will eventually be handed one that was never a ledger.
        ``cycle_definition`` is checked against the live cycle because a document written
        under a different stage set replays into a different history: the stages would be
        accepted one by one and the whole would silently mean something else. That check is
        what keeps the open-world stage set (Article 17) from turning into a quiet
        reinterpretation of an old history.
        """
        if not isinstance(document, dict):
            raise EvolutionError(
                "an evolution ledger document must be a mapping",
                received=type(document).__name__,
            )
        schema = str(document.get("schema", ""))
        if schema != LEDGER_SCHEMA:
            raise EvolutionError(
                "document is not an evolution ledger",
                expected=LEDGER_SCHEMA,
                declared=schema or "<absent>",
            )
        declared_cycle = document.get("cycle_definition")
        if declared_cycle is not None:
            live_cycle = [stage.value for stage in EVOLUTION_CYCLE]
            if [str(stage) for stage in declared_cycle] != live_cycle:
                raise EvolutionError(
                    "document was written under a different evolution cycle",
                    expected=",".join(live_cycle),
                    declared=",".join(str(stage) for stage in declared_cycle),
                )
        records = document.get("records", ())
        if not isinstance(records, list | tuple):
            raise EvolutionError(
                "an evolution ledger document must carry a sequence of records",
                received=type(records).__name__,
            )
        return cls(EvolutionRecord.from_dict(record) for record in records)

    def fingerprint(self) -> str:
        return content_hash([record.to_dict() for record in self._records])


__all__ = [
    "CYCLE_LENGTH",
    "EVOLUTION_CYCLE",
    "EVOLUTION_STAGE",
    "LEDGER_SCHEMA",
    "LEDGER_VERSION",
    "EvolutionLedger",
    "EvolutionRecord",
    "EvolutionStage",
    "evolution_stage_vocabulary",
    "is_terminal",
    "next_stage",
]
