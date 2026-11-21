"""UAPF-000001 — the Universal Event Engine (Recorded Truth for pipeline activity).

Every act UAPF performs — a registration, an admission, a refusal, a state change, a
stage outcome, a verdict, a tick — is recorded as an event, and the record is the only
account of what happened. There is **no second event substrate**: this module composes
:class:`platform.foundation.dag_ledger.EventDag`, the repository's append-only,
Merkle-linked event DAG, and adds exactly two things to it — an open *category* registry
and UAPF's domain error discipline.

Why the DAG and not the linear bus
----------------------------------
Autonomous work diverges and converges: several pipelines advance concurrently, a batch
splits into units, units rejoin at a certification point. A monotonic sequence cannot
express that without lying about causality, whereas ``branch`` and ``merge`` are
first-class in the DAG (AIF-L08). Recording is also forward-only: there is no update and
no delete, so a correction is a new event and history is tamper-evident (AIF-L17). Both
properties are inherited, not re-implemented.

Categories are declared, not enumerated
---------------------------------------
:func:`register_event_category` opens the vocabulary; :data:`SEED_EVENT_CATEGORIES`
declares the categories UAPF itself emits and registers them through that same public
function. Emitting an unregistered category fails closed, so the event vocabulary is
knowable — and extending it is one data entry, never a change to the bus.

Determinism: the bus holds no wall-clock and no counter of its own. An event's identity
is the Merkle hash of its content and its parents, so an identical sequence of emissions
yields a byte-identical DAG and an identical :meth:`PipelineEventBus.fingerprint` in
every environment. Nothing here is persisted; like the ledger it generalizes, this bus
never writes the certified corpus (DP-03).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from platform.foundation.dag_ledger import DagEvent, EventDag
from platform.foundation.errors import DagLedgerError
from platform.universal_pipeline.errors import PipelineEventError
from platform.universal_pipeline.identity import IDENTITY_PREFIX
from platform.universal_pipeline.vocabulary import Vocabulary
from typing import Any

#: The default event source: the programme that owns this framework. Derived from the
#: identity namespace rather than restated, so the source and the identity prefix cannot
#: drift apart.
EVENT_SOURCE = f"{IDENTITY_PREFIX}-000001"

#: The event categories UAPF itself emits. A *declaration*: each is admitted through the
#: public :func:`register_event_category`, so the vocabulary stays open and a consumer's
#: own category is a peer of these, not a second-class citizen.
SEED_EVENT_CATEGORIES: tuple[tuple[str, str], ...] = (
    ("uapf.capability.declared", "a pipeline declared a provided or required capability"),
    ("uapf.catalog.discovered", "a declaration catalogue was parsed and admitted"),
    ("uapf.dependency.declared", "a dependency edge was declared"),
    ("uapf.escalation.raised", "autonomy halted for a declared human-decision reason"),
    ("uapf.gateway.admitted", "the gateway admitted a submission and authorized execution"),
    ("uapf.gateway.refused", "the gateway refused a submission (fail-closed)"),
    ("uapf.orchestration.tick", "one autonomous orchestration tick completed"),
    ("uapf.pipeline.registered", "a pipeline version entered the registry"),
    ("uapf.pipeline.superseded", "a pipeline version was superseded by a newer version"),
    ("uapf.policy.evaluated", "the policy engine produced a governance verdict"),
    ("uapf.queue.cut", "an execution batch was cut from the ready queue"),
    ("uapf.queue.demoted", "a unit left the ready queue for the blocked set"),
    ("uapf.queue.enqueued", "a unit entered the execution queue"),
    ("uapf.queue.promoted", "a unit was promoted to the ready queue"),
    ("uapf.queue.retired", "a unit left every active queue for a terminal sink"),
    ("uapf.recovery.recorded", "a forward-only recovery point was recorded"),
    ("uapf.stage.completed", "a stage handler returned an outcome"),
    ("uapf.telemetry.recorded", "a metric or span was recorded"),
    ("uapf.unit.certified", "a unit was certified"),
    ("uapf.unit.state-changed", "a unit advanced along the declared lifecycle"),
    ("uapf.unit.validated", "a unit was validated"),
    ("uapf.unit.verified", "a unit was verified"),
)

#: The event-category vocabulary. Module-level so a category registered by any consumer is
#: emittable by every consumer — one vocabulary, not one per bus instance.
_EVENT_CATEGORIES = Vocabulary("event-category", error=PipelineEventError)


def register_event_category(category: str, description: str = "") -> None:
    """Register one event category (unbounded extension by declaration).

    Raises:
        PipelineEventError: if ``category`` is not a lower-case dotted/hyphenated token or
            is already registered. Re-registration is refused: a category is how recorded
            history is queried, and rebinding one would silently change the meaning of
            events already recorded under it.
    """
    _EVENT_CATEGORIES.register(category, description=description)


def event_categories() -> tuple[str, ...]:
    """Every registered event category, sorted (deterministic)."""
    return _EVENT_CATEGORIES.terms()


def event_category_description(category: str) -> str:
    """The declared description of ``category`` (fail-closed if unregistered)."""
    return _EVENT_CATEGORIES.require(category).description


def require_event_category(category: str) -> None:
    """Fail closed unless ``category`` is registered.

    Raises:
        PipelineEventError: naming the unknown category and how many are registered.
    """
    _EVENT_CATEGORIES.require(category)


class PipelineEventBus:
    """The append-only, Merkle-linked event record of one UAPF platform instance.

    A thin, category-guarded façade over :class:`~platform.foundation.dag_ledger.EventDag`.
    It exposes ``emit`` / ``branch`` / ``merge`` because divergence and convergence are
    first-class in autonomous work, and it exposes no update and no delete because
    Recorded Truth is forward-only.
    """

    __slots__ = ("_dag", "_source")

    def __init__(self, *, source: str = EVENT_SOURCE) -> None:
        if not isinstance(source, str) or not source:
            raise PipelineEventError("event source is required")
        self._dag = EventDag()
        self._source = source

    @property
    def source(self) -> str:
        """The source recorded on every event this bus emits."""
        return self._source

    @property
    def events(self) -> tuple[DagEvent, ...]:
        """An immutable snapshot of the recorded DAG in admission order."""
        return self._dag.events

    @property
    def heads(self) -> tuple[str, ...]:
        """The current head hashes — the tips of recorded history."""
        return self._dag.heads

    def __len__(self) -> int:
        return len(self._dag)

    def emit(
        self,
        category: str,
        subject: str,
        *,
        payload: Mapping[str, Any] | None = None,
        parents: Iterable[str] | None = None,
    ) -> DagEvent:
        """Record one event of ``category`` about ``subject``.

        With no explicit ``parents`` the event chains onto the current head, so ordinary
        recording is linear; ``parents`` (or :meth:`merge`) expresses convergence.

        Raises:
            PipelineEventError: if ``category`` is unregistered, ``subject`` is not a
                string, or the underlying ledger refuses the append (a dangling parent,
                or an ambiguous head after a divergence). Every failure is closed.
        """
        require_event_category(category)
        if not isinstance(subject, str):
            raise PipelineEventError("event subject must be a string", category=category)
        try:
            return self._dag.append(
                category, self._source, subject, payload=payload, parents=parents
            )
        except DagLedgerError as exc:
            raise PipelineEventError(
                "event could not be recorded",
                category=category,
                subject=subject,
                reason=exc.message,
            ) from exc

    def branch(
        self,
        parent: str,
        category: str,
        subject: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> DagEvent:
        """Record ``category`` as an explicit divergence from ``parent``.

        Raises:
            PipelineEventError: if the category is unregistered or ``parent`` is not
                recorded (edges never dangle).
        """
        require_event_category(category)
        try:
            return self._dag.branch(parent, category, self._source, subject, payload=payload)
        except DagLedgerError as exc:
            raise PipelineEventError(
                "event branch refused", category=category, parent=parent, reason=exc.message
            ) from exc

    def merge(
        self,
        parents: Iterable[str],
        category: str,
        subject: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> DagEvent:
        """Record ``category`` as an explicit convergence of ``parents``.

        Raises:
            PipelineEventError: if the category is unregistered or any parent is not
                recorded.
        """
        require_event_category(category)
        try:
            return self._dag.merge(list(parents), category, self._source, subject, payload=payload)
        except DagLedgerError as exc:
            raise PipelineEventError(
                "event merge refused", category=category, reason=exc.message
            ) from exc

    def events_of(self, category: str) -> tuple[DagEvent, ...]:
        """Every recorded event of ``category`` in admission order.

        Fail-closed on an unregistered category: querying history for a category that
        cannot be emitted is a caller error, and returning an empty tuple would hide it.
        """
        require_event_category(category)
        return tuple(event for event in self._dag.events if event.event_type == category)

    def events_about(self, subject: str) -> tuple[DagEvent, ...]:
        """Every recorded event about ``subject`` in admission order (the audit trail)."""
        return tuple(event for event in self._dag.events if event.subject == subject)

    def categories_recorded(self) -> tuple[str, ...]:
        """The distinct categories actually present in recorded history, sorted."""
        return tuple(sorted({event.event_type for event in self._dag.events}))

    def verify(self) -> bool:
        """True iff recorded history is intact (Merkle hashes and edges all check)."""
        return self._dag.verify()

    def require_intact(self) -> None:
        """Fail closed unless recorded history is intact.

        Raises:
            PipelineEventError: if any recorded event's hash or edge no longer checks —
                i.e. Recorded Truth was mutated.
        """
        try:
            self._dag.require_intact()
        except DagLedgerError as exc:
            raise PipelineEventError(
                "recorded event history is not intact", reason=exc.message
            ) from exc

    def fingerprint(self) -> str:
        """A deterministic content hash of the whole recorded DAG."""
        return self._dag.fingerprint()

    def export(self) -> dict[str, Any]:
        """Serialize recorded history (persistence, if any, is the caller's concern)."""
        return self._dag.export()

    def to_dict(self) -> dict[str, Any]:
        """A deterministic summary of recorded history (evidence)."""
        return {
            "source": self._source,
            "event_count": len(self._dag),
            "heads": list(self._dag.heads),
            "categories_recorded": list(self.categories_recorded()),
            "fingerprint": self.fingerprint(),
        }


for _category, _category_description in SEED_EVENT_CATEGORIES:
    register_event_category(_category, _category_description)
del _category, _category_description


__all__ = [
    "EVENT_SOURCE",
    "SEED_EVENT_CATEGORIES",
    "PipelineEventBus",
    "event_categories",
    "event_category_description",
    "register_event_category",
    "require_event_category",
]
