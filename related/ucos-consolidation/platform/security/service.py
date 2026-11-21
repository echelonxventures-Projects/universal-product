"""EC2-CAP-SEC-001 / SEC-CLASS — Security Classification Service (Phase 1).

The composition root of the **Security Classification Runtime**. It exposes the five
SEC-CLASS responsibilities — **classify · record · trace · validate · report** — over
an append-only :class:`~platform.security.classification.ClassificationLedger`, and it
resolves a classification's declared enforcement obligation to the **existing**,
certified L7 :class:`~platform.identity.service.AuthorizationService` seam **by
reference only**.

Boundary (mission-critical): this service **never** authorizes, ratifies, enacts,
governs, overrides, or escalates authority (RG-02 / AR-04; determination §4.3). When
an :class:`AuthorizationService` is bound, it is used **solely** to confirm that a
referenced :class:`~platform.identity.contracts.CapabilityGroup` is a real row of the
§3.2 matrix the seam governs — a *reference resolution*, not an access decision. No
call to ``authorize`` is ever made.

Every classification recording is a governed action: when an
:class:`~platform.foundation.events.EventBus` is bound, a deterministic
``security.classification.recorded`` event is published so the L8 Observability Layer
can audit it (PC-16; determination §9). The service is deterministic: the same calls
yield the same ledger and the same :class:`SecurityClassificationEvidence` fingerprint.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.identity.contracts import CapabilityGroup, all_capability_groups
from platform.identity.service import AuthorizationService
from platform.security.classification import ClassificationLedger, SecurityClassification
from platform.security.contracts import (
    ClassificationKind,
    EnforcementReference,
    SubjectLayer,
    all_classification_kinds,
)
from platform.security.errors import (
    EnforcementReferenceError,
    SecurityClassificationError,
)
from typing import Any

#: The governed event emitted for every recorded classification (PC-16).
CLASSIFICATION_RECORDED_EVENT = "security.classification.recorded"

#: The canonical set of L7 capability groups (a frozen snapshot for reference resolution).
_KNOWN_GROUPS: frozenset[CapabilityGroup] = frozenset(all_capability_groups())


@dataclass(frozen=True, slots=True)
class SecurityClassificationEvidence:
    """A deterministic, content-addressed report over recorded classifications.

    Aggregates the ledger fingerprint, counts, and a per-kind breakdown into a single
    reproducible evidence object suitable for audit and program certification roll-up
    (determination §11). Content-addressed ``evidence_id`` (``UCOS-SCEV-``).
    """

    ledger_fingerprint: str
    classification_count: int
    l7_bound_count: int
    kind_counts: tuple[tuple[str, int], ...]
    classifications: tuple[dict[str, Any], ...]
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        ledger_fingerprint: str,
        classifications: tuple[dict[str, Any], ...],
        kind_counts: tuple[tuple[str, int], ...],
        l7_bound_count: int,
    ) -> SecurityClassificationEvidence:
        core = {
            "ledger_fingerprint": ledger_fingerprint,
            "classifications": list(classifications),
            "kind_counts": [list(kc) for kc in kind_counts],
            "l7_bound_count": l7_bound_count,
        }
        return cls(
            ledger_fingerprint=ledger_fingerprint,
            classification_count=len(classifications),
            l7_bound_count=l7_bound_count,
            kind_counts=kind_counts,
            classifications=classifications,
            evidence_id=f"UCOS-SCEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "ledger_fingerprint": self.ledger_fingerprint,
            "classification_count": self.classification_count,
            "l7_bound_count": self.l7_bound_count,
            "kind_counts": [list(kc) for kc in self.kind_counts],
            "classifications": [dict(c) for c in self.classifications],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class SecurityClassificationService:
    """The governed SEC-CLASS composition root (classify · record · trace · validate · report)."""

    __slots__ = ("_ledger", "_authorization", "_events")

    def __init__(
        self,
        *,
        ledger: ClassificationLedger | None = None,
        authorization: AuthorizationService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if ledger is not None and not isinstance(ledger, ClassificationLedger):
            raise SecurityClassificationError("ledger must be a ClassificationLedger when provided")
        if authorization is not None and not isinstance(authorization, AuthorizationService):
            raise SecurityClassificationError(
                "authorization must be an AuthorizationService when provided"
            )
        if events is not None and not isinstance(events, EventBus):
            raise SecurityClassificationError("events must be an EventBus when provided")
        self._ledger = ledger if ledger is not None else ClassificationLedger()
        self._authorization = authorization
        self._events = events

    # -- component access -------------------------------------------------------

    @property
    def ledger(self) -> ClassificationLedger:
        return self._ledger

    @property
    def authorization_bound(self) -> bool:
        """True iff the certified L7 seam is available for reference resolution."""
        return self._authorization is not None

    # -- enforcement-reference resolution (by reference; never authorizes) ------

    def resolve_enforcement_reference(self, reference: EnforcementReference) -> dict[str, Any]:
        """Confirm a reference resolves to a real L7 seam row (no access decision).

        Verifies the referenced :class:`CapabilityGroup` is a real row of the §3.2
        matrix the certified :class:`AuthorizationService` governs. This is a
        *reference resolution*: it makes **no** authorization decision and grants
        nothing (RG-02 / AR-04). Raises if the reference does not resolve.
        """
        if not isinstance(reference, EnforcementReference):
            raise EnforcementReferenceError("an EnforcementReference is required")
        if reference.group not in _KNOWN_GROUPS:
            raise EnforcementReferenceError(
                "enforcement reference does not resolve to a known L7 capability group",
                group=reference.group.value,
            )
        return {
            "reference_id": reference.reference_id,
            "group": reference.group.value,
            "permission": reference.permission.value,
            "resolved": True,
            "seam": "platform.identity.AuthorizationService",
            "seam_bound": self._authorization is not None,
            "enacts": False,
        }

    # -- classify + record ------------------------------------------------------

    def classify(
        self,
        kind: ClassificationKind,
        layer: SubjectLayer,
        subject_ref: str,
        label: str,
        *,
        enforcement_ref: EnforcementReference | None = None,
        constitution_ref: str | None = None,
    ) -> SecurityClassification:
        """Classify a construct, resolve any L7 reference, record it, and emit a governed event.

        Builds an evaluative, non-enforcing :class:`SecurityClassification`; if it is
        L7-bound, resolves its :class:`EnforcementReference` against the certified seam
        (reference-only); appends it to the append-only ledger (idempotent by id); and
        publishes a ``security.classification.recorded`` governed event when an event
        bus is bound. Enacts nothing.
        """
        classification = SecurityClassification.create(
            kind,
            layer,
            subject_ref,
            label,
            enforcement_ref=enforcement_ref,
            constitution_ref=constitution_ref,
        )
        resolution: dict[str, Any] | None = None
        if classification.enforcement_ref is not None:
            resolution = self.resolve_enforcement_reference(classification.enforcement_ref)
        recorded = self._ledger.record(classification)
        self._emit(recorded, resolution)
        return recorded

    def record(self, classification: SecurityClassification) -> SecurityClassification:
        """Record a pre-built classification (idempotent); resolves any L7 reference first."""
        if not isinstance(classification, SecurityClassification):
            raise SecurityClassificationError("only a SecurityClassification may be recorded")
        resolution: dict[str, Any] | None = None
        if classification.enforcement_ref is not None:
            resolution = self.resolve_enforcement_reference(classification.enforcement_ref)
        recorded = self._ledger.record(classification)
        self._emit(recorded, resolution)
        return recorded

    # -- trace + validate + report ----------------------------------------------

    def trace(self, classification_id: str) -> dict[str, Any]:
        """Return the full traceability chain for a recorded classification (§14)."""
        return self._ledger.get(classification_id).trace()

    def validate(self, classification_id: str) -> dict[str, Any]:
        """Re-affirm the meta-validity of a recorded classification (fail-closed)."""
        return self._ledger.get(classification_id).validate()

    def validate_all(self) -> dict[str, Any]:
        """Validate every recorded classification; returns an aggregate decidable result."""
        results = [c.validate() for c in self._ledger.classifications]
        return {
            "classification_count": len(results),
            "meta_valid": all(r["meta_valid"] for r in results),
            "results": results,
        }

    def report(self) -> SecurityClassificationEvidence:
        """Produce the deterministic classification evidence over the ledger (record-only)."""
        classifications = self._ledger.classifications
        kind_counts = tuple(
            (kind.value, sum(1 for c in classifications if c.kind is kind))
            for kind in all_classification_kinds()
        )
        l7_bound_count = sum(1 for c in classifications if c.is_l7_bound)
        return SecurityClassificationEvidence.create(
            ledger_fingerprint=self._ledger.fingerprint(),
            classifications=tuple(c.to_dict() for c in classifications),
            kind_counts=kind_counts,
            l7_bound_count=l7_bound_count,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ledger": self._ledger.to_dict(),
            "authorization_bound": self._authorization is not None,
            "evidence": self.report().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _emit(
        self, classification: SecurityClassification, resolution: dict[str, Any] | None
    ) -> None:
        """Publish a governed ``security.classification.recorded`` event (if bound)."""
        if self._events is None:
            return
        payload: dict[str, Any] = {
            "classification": classification.to_dict(),
            "enforcement_resolution": resolution,
            "enacts": False,
        }
        self._events.publish(
            CLASSIFICATION_RECORDED_EVENT,
            source="platform.security.classification",
            subject=classification.subject_ref,
            payload=payload,
        )


def build_security_classification_service(
    *,
    authorization: AuthorizationService | None = None,
    events: EventBus | None = None,
) -> SecurityClassificationService:
    """Default composition of the Security Classification Runtime (record-only)."""
    return SecurityClassificationService(
        ledger=ClassificationLedger(),
        authorization=authorization,
        events=events,
    )


__all__ = [
    "CLASSIFICATION_RECORDED_EVENT",
    "SecurityClassificationEvidence",
    "SecurityClassificationService",
    "build_security_classification_service",
]
