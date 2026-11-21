"""UCOS-EPIC-014 — Approval Intelligence (Terminal T5).

When Policy Governance returns ``requires_approval``, the action is not permitted until an
**approval chain** is satisfied. Approval Intelligence evaluates that chain
deterministically and fail-closed:

    * a stage is satisfied only by ``quorum`` *distinct* approvers holding the stage's
      role — a duplicate approver never counts twice;
    * an approver may not approve their own request (declared ``requested_by``), so
      self-approval is structurally impossible;
    * any rejection at any stage is terminal: the chain is refused, not merely pending;
    * a decision naming an unknown stage, or an approver whose role does not match the
      stage, is recorded as an irregularity and never counted toward quorum.

Ordering is by stage index, so an outcome is reproducible regardless of the order the
decisions were recorded in.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from platform.commercial_intelligence.errors import ApprovalError
from platform.foundation.contracts import content_hash
from typing import Any


class ApprovalDecision(str, Enum):
    """The closed approval-decision vocabulary."""

    APPROVED = "approved"
    REJECTED = "rejected"

    @classmethod
    def parse(cls, value: Any) -> ApprovalDecision:
        try:
            return cls(value)
        except ValueError as exc:
            raise ApprovalError(
                "unknown approval decision",
                decision=value,
                supported=[d.value for d in cls],
            ) from exc


@dataclass(frozen=True, slots=True)
class ApprovalStage:
    """An immutable approval stage: a role and the number of distinct approvers required."""

    stage_id: str
    role: str
    quorum: int = 1

    def __post_init__(self) -> None:
        if not self.stage_id:
            raise ApprovalError("an approval stage requires a non-empty stage_id")
        if not self.role:
            raise ApprovalError(
                "an approval stage requires the accountable role", stage_id=self.stage_id
            )
        if isinstance(self.quorum, bool) or not isinstance(self.quorum, int) or self.quorum < 1:
            raise ApprovalError(
                "an approval stage requires an integer quorum of at least one",
                stage_id=self.stage_id,
                quorum=repr(self.quorum),
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> ApprovalStage:
        if not isinstance(raw, Mapping):
            raise ApprovalError("an approval stage must be a mapping")
        return cls(
            stage_id=str(raw.get("stage_id") or ""),
            role=str(raw.get("role") or ""),
            quorum=raw.get("quorum", 1),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"stage_id": self.stage_id, "role": self.role, "quorum": self.quorum}


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    """An immutable record of one approver's decision at one stage."""

    record_id: str
    stage_id: str
    approver_id: str
    role: str
    decision: ApprovalDecision

    def __post_init__(self) -> None:
        if not self.record_id:
            raise ApprovalError("an approval record requires a non-empty record_id")
        for field_name, value in (
            ("stage_id", self.stage_id),
            ("approver_id", self.approver_id),
            ("role", self.role),
        ):
            if not value:
                raise ApprovalError(
                    f"an approval record requires a {field_name}", record_id=self.record_id
                )

    @classmethod
    def from_mapping(cls, raw: Any) -> ApprovalRecord:
        if not isinstance(raw, Mapping):
            raise ApprovalError("an approval record must be a mapping")
        return cls(
            record_id=str(raw.get("record_id") or ""),
            stage_id=str(raw.get("stage_id") or ""),
            approver_id=str(raw.get("approver_id") or ""),
            role=str(raw.get("role") or ""),
            decision=ApprovalDecision.parse(raw.get("decision")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "stage_id": self.stage_id,
            "approver_id": self.approver_id,
            "role": self.role,
            "decision": self.decision.value,
        }


@dataclass(frozen=True, slots=True)
class StageOutcome:
    """The deterministic outcome of one approval stage."""

    stage_id: str
    role: str
    quorum: int
    approvals: int
    rejected: bool
    satisfied: bool
    approvers: tuple[str, ...]
    irregularities: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "role": self.role,
            "quorum": self.quorum,
            "approvals": self.approvals,
            "rejected": self.rejected,
            "satisfied": self.satisfied,
            "approvers": list(self.approvers),
            "irregularities": list(self.irregularities),
        }


@dataclass(frozen=True, slots=True)
class ApprovalOutcome:
    """The immutable, content-addressed outcome of a whole approval chain."""

    chain_id: str
    satisfied: bool
    rejected: bool
    stages: tuple[StageOutcome, ...]
    pending_stages: tuple[str, ...]
    irregularities: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "satisfied": self.satisfied,
            "rejected": self.rejected,
            "stages": [stage.to_dict() for stage in self.stages],
            "pending_stages": list(self.pending_stages),
            "irregularities": list(self.irregularities),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ApprovalChain:
    """An immutable, ordered approval chain for one commercial request."""

    chain_id: str
    requested_by: str
    stages: tuple[ApprovalStage, ...]

    def __post_init__(self) -> None:
        if not self.chain_id:
            raise ApprovalError("an approval chain requires a non-empty chain_id")
        if not self.requested_by:
            raise ApprovalError(
                "an approval chain requires the requesting principal, so self-approval "
                "can be refused",
                chain_id=self.chain_id,
            )
        if not self.stages:
            raise ApprovalError(
                "an approval chain requires at least one stage", chain_id=self.chain_id
            )
        seen: set[str] = set()
        for stage in self.stages:
            if stage.stage_id in seen:
                raise ApprovalError(
                    "duplicate stage_id in the approval chain",
                    chain_id=self.chain_id,
                    stage_id=stage.stage_id,
                )
            seen.add(stage.stage_id)

    @classmethod
    def from_mapping(cls, raw: Any) -> ApprovalChain:
        """Assimilate ``{chain_id, requested_by, stages}`` into an approval chain."""
        if not isinstance(raw, Mapping):
            raise ApprovalError("an approval chain must be a mapping")
        stages_raw = raw.get("stages", ())
        if isinstance(stages_raw, str | bytes) or not isinstance(stages_raw, Sequence):
            raise ApprovalError(
                "approval chain stages must be a sequence", chain_id=raw.get("chain_id")
            )
        return cls(
            chain_id=str(raw.get("chain_id") or ""),
            requested_by=str(raw.get("requested_by") or ""),
            stages=tuple(ApprovalStage.from_mapping(item) for item in stages_raw),
        )

    def stage(self, stage_id: str) -> ApprovalStage | None:
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def evaluate(self, records: Sequence[ApprovalRecord]) -> ApprovalOutcome:
        """Evaluate ``records`` against this chain — fail-closed, order-independent."""
        known = {stage.stage_id for stage in self.stages}
        irregularities: list[str] = []
        by_stage: dict[str, list[ApprovalRecord]] = {stage_id: [] for stage_id in known}
        for record in records:
            if record.stage_id not in known:
                irregularities.append(
                    f"{record.record_id}: names stage {record.stage_id} which is not in the chain"
                )
                continue
            by_stage[record.stage_id].append(record)

        outcomes: list[StageOutcome] = []
        for stage in self.stages:
            stage_irregularities: list[str] = []
            approvers: set[str] = set()
            rejected = False
            for record in sorted(by_stage[stage.stage_id], key=lambda r: r.record_id):
                if record.role != stage.role:
                    stage_irregularities.append(
                        f"{record.record_id}: role {record.role} does not hold stage role "
                        f"{stage.role}"
                    )
                    continue
                if record.approver_id == self.requested_by:
                    stage_irregularities.append(
                        f"{record.record_id}: self-approval by the requesting principal "
                        f"{self.requested_by} is refused"
                    )
                    continue
                if record.decision is ApprovalDecision.REJECTED:
                    rejected = True
                    continue
                approvers.add(record.approver_id)
            satisfied = not rejected and len(approvers) >= stage.quorum
            outcomes.append(
                StageOutcome(
                    stage_id=stage.stage_id,
                    role=stage.role,
                    quorum=stage.quorum,
                    approvals=len(approvers),
                    rejected=rejected,
                    satisfied=satisfied,
                    approvers=tuple(sorted(approvers)),
                    irregularities=tuple(stage_irregularities),
                )
            )
            irregularities.extend(stage_irregularities)

        return ApprovalOutcome(
            chain_id=self.chain_id,
            satisfied=all(stage.satisfied for stage in outcomes),
            rejected=any(stage.rejected for stage in outcomes),
            stages=tuple(outcomes),
            pending_stages=tuple(
                stage.stage_id for stage in outcomes if not stage.satisfied and not stage.rejected
            ),
            irregularities=tuple(irregularities),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "requested_by": self.requested_by,
            "stages": [stage.to_dict() for stage in self.stages],
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def parse_records(raw: Any) -> tuple[ApprovalRecord, ...]:
    """Assimilate a sequence of approval-record mappings, in canonical record-id order."""
    if isinstance(raw, str | bytes) or not isinstance(raw, Sequence):
        raise ApprovalError("approval records must be a sequence")
    return tuple(
        sorted(
            (ApprovalRecord.from_mapping(item) for item in raw),
            key=lambda record: record.record_id,
        )
    )


__all__ = [
    "ApprovalDecision",
    "ApprovalStage",
    "ApprovalRecord",
    "StageOutcome",
    "ApprovalOutcome",
    "ApprovalChain",
    "parse_records",
]
