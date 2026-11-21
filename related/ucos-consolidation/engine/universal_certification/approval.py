"""UCOS-EPIC-006 — Approval Workflow (Terminal T6).

The **Approval Workflow** is a governed, deterministic, fail-closed state machine that
gates the *issuance* of a universal certificate behind an explicit, attributed
approval act (MIP Part 15 — certify-before-promote; Part 30 — every determination is
attributed and appealable). It re-judges nothing: it only governs the transition of an
already-computed :class:`~engine.universal_certification.engine.CertificationDecision`
from DRAFT → PENDING → {APPROVED | REJECTED | WITHDRAWN}.

Fail-closed invariant (OP-CERT-001): a **NOT-CERTIFIED** decision can never be
APPROVED — an attempt raises :class:`ApprovalWorkflowError`. Every transition is
recorded as an immutable, **hash-chained** :class:`ApprovalRecord`, so the approval
history is tamper-evident like the audit ledger. Transitions embed no wall-clock or
ambient state — ordering lives in the append-only sequence — so an identical sequence
of actions over an identical decision reproduces an identical chain of record hashes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.universal_certification.contracts import content_hash
from engine.universal_certification.engine import CertificationDecision
from engine.universal_certification.errors import ApprovalWorkflowError

_logger = get_logger("universal_certification.approval")

#: The genesis predecessor hash for the first approval record.
GENESIS_HASH = "0" * 64


class ApprovalState(str, Enum):
    """The lifecycle state of a certificate's approval."""

    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApprovalAction(str, Enum):
    """A governed approval-workflow transition verb."""

    SUBMIT = "submit"
    APPROVE = "approve"
    REJECT = "reject"
    WITHDRAW = "withdraw"


#: The terminal states of the workflow (no further transition is permitted).
_TERMINAL_STATES = frozenset(
    {ApprovalState.APPROVED, ApprovalState.REJECTED, ApprovalState.WITHDRAWN}
)


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    """One immutable, hash-chained approval-workflow transition record."""

    sequence: int
    certification_id: str
    certificate_sha256: str
    action: ApprovalAction
    from_state: ApprovalState
    to_state: ApprovalState
    actor: str
    rationale: str
    prev_hash: str
    record_hash: str

    @staticmethod
    def compute_hash(
        *,
        sequence: int,
        certification_id: str,
        certificate_sha256: str,
        action: ApprovalAction,
        from_state: ApprovalState,
        to_state: ApprovalState,
        actor: str,
        rationale: str,
        prev_hash: str,
    ) -> str:
        """The deterministic record hash binding this transition to its predecessor."""
        return content_hash(
            {
                "sequence": sequence,
                "certification_id": certification_id,
                "certificate_sha256": certificate_sha256,
                "action": action.value,
                "from_state": from_state.value,
                "to_state": to_state.value,
                "actor": actor,
                "rationale": rationale,
                "prev_hash": prev_hash,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "certification_id": self.certification_id,
            "certificate_sha256": self.certificate_sha256,
            "action": self.action.value,
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "actor": self.actor,
            "rationale": self.rationale,
            "prev_hash": self.prev_hash,
            "record_hash": self.record_hash,
        }


class ApprovalWorkflow:
    """A deterministic, fail-closed, hash-chained approval workflow for one decision."""

    __slots__ = ("_decision", "_state", "_records")

    def __init__(self, decision: CertificationDecision) -> None:
        if not isinstance(decision, CertificationDecision):
            raise ApprovalWorkflowError("approval workflow requires a CertificationDecision")
        self._decision = decision
        self._state = ApprovalState.DRAFT
        self._records: list[ApprovalRecord] = []

    @property
    def certification_id(self) -> str:
        return self._decision.certification_id

    @property
    def state(self) -> ApprovalState:
        return self._state

    @property
    def records(self) -> tuple[ApprovalRecord, ...]:
        """An immutable snapshot of the approval history (append-only)."""
        return tuple(self._records)

    @property
    def head_hash(self) -> str:
        return self._records[-1].record_hash if self._records else GENESIS_HASH

    @property
    def approved(self) -> bool:
        return self._state is ApprovalState.APPROVED

    @property
    def is_terminal(self) -> bool:
        return self._state in _TERMINAL_STATES

    # -- transitions -----------------------------------------------------------

    def submit(self, actor: str, rationale: str = "") -> ApprovalRecord:
        """DRAFT → PENDING: submit the decision for approval."""
        if self._state is not ApprovalState.DRAFT:
            raise ApprovalWorkflowError(
                "only a draft approval may be submitted",
                state=self._state.value,
                certification_id=self.certification_id,
            )
        return self._transition(ApprovalAction.SUBMIT, ApprovalState.PENDING, actor, rationale)

    def approve(self, actor: str, rationale: str = "") -> ApprovalRecord:
        """PENDING → APPROVED: approve a CERTIFIED decision (fail-closed)."""
        self._require_pending(ApprovalAction.APPROVE)
        if not self._decision.certified:
            raise ApprovalWorkflowError(
                "a not-certified decision can never be approved (fail-closed)",
                certification_id=self.certification_id,
                status=self._decision.status.value,
                blocking_failures=list(self._decision.blocking_failures),
            )
        return self._transition(ApprovalAction.APPROVE, ApprovalState.APPROVED, actor, rationale)

    def reject(self, actor: str, rationale: str = "") -> ApprovalRecord:
        """PENDING → REJECTED: reject the decision with a recorded rationale."""
        self._require_pending(ApprovalAction.REJECT)
        return self._transition(ApprovalAction.REJECT, ApprovalState.REJECTED, actor, rationale)

    def withdraw(self, actor: str, rationale: str = "") -> ApprovalRecord:
        """PENDING → WITHDRAWN: withdraw a pending approval request."""
        self._require_pending(ApprovalAction.WITHDRAW)
        return self._transition(ApprovalAction.WITHDRAW, ApprovalState.WITHDRAWN, actor, rationale)

    # -- internals -------------------------------------------------------------

    def _require_pending(self, action: ApprovalAction) -> None:
        if self._state is not ApprovalState.PENDING:
            raise ApprovalWorkflowError(
                f"action {action.value!r} requires a pending approval",
                state=self._state.value,
                certification_id=self.certification_id,
            )

    def _transition(
        self,
        action: ApprovalAction,
        to_state: ApprovalState,
        actor: str,
        rationale: str,
    ) -> ApprovalRecord:
        if not isinstance(actor, str) or not actor:
            raise ApprovalWorkflowError("approval actor must be a non-empty string")
        if not isinstance(rationale, str):
            raise ApprovalWorkflowError("approval rationale must be a string")
        sequence = len(self._records)
        from_state = self._state
        prev_hash = self.head_hash
        certificate_sha256 = self._decision.certificate.content_sha256
        record_hash = ApprovalRecord.compute_hash(
            sequence=sequence,
            certification_id=self.certification_id,
            certificate_sha256=certificate_sha256,
            action=action,
            from_state=from_state,
            to_state=to_state,
            actor=actor,
            rationale=rationale,
            prev_hash=prev_hash,
        )
        record = ApprovalRecord(
            sequence=sequence,
            certification_id=self.certification_id,
            certificate_sha256=certificate_sha256,
            action=action,
            from_state=from_state,
            to_state=to_state,
            actor=actor,
            rationale=rationale,
            prev_hash=prev_hash,
            record_hash=record_hash,
        )
        self._records.append(record)
        self._state = to_state
        _logger.info(
            "universal_certification.approval.transition",
            certification_id=self.certification_id,
            action=action.value,
            to_state=to_state.value,
        )
        return record

    def verify(self) -> bool:
        """Return True iff the approval record hash chain is intact (tamper-evident)."""
        prev = GENESIS_HASH
        for index, record in enumerate(self._records):
            if record.sequence != index or record.prev_hash != prev:
                return False
            expected = ApprovalRecord.compute_hash(
                sequence=record.sequence,
                certification_id=record.certification_id,
                certificate_sha256=record.certificate_sha256,
                action=record.action,
                from_state=record.from_state,
                to_state=record.to_state,
                actor=record.actor,
                rationale=record.rationale,
                prev_hash=record.prev_hash,
            )
            if expected != record.record_hash:
                return False
            prev = record.record_hash
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_format": "ucos-universal-approval-workflow/1.0.0",
            "certification_id": self.certification_id,
            "state": self._state.value,
            "approved": self.approved,
            "head_hash": self.head_hash,
            "records": [r.to_dict() for r in self._records],
        }


__all__ = [
    "GENESIS_HASH",
    "ApprovalState",
    "ApprovalAction",
    "ApprovalRecord",
    "ApprovalWorkflow",
]
