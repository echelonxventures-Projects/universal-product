"""UCOS-CTRL-000001 — Traceability Engines.

Five engines that together constitute the Universal Traceability Layer:

    DeterminationEngine  — records and retrieves determinations
    DecisionEngine       — records decisions with rationale and alternatives
    HistoryEngine        — append-only history log for any subject
    ReplayEngine         — records and verifies replayable executions
    EvidenceEngine       — records and verifies content-addressed evidence
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from platform.universal_control_plane.errors import (
    DuplicateObjectError,
    EvidenceError,
    ObjectNotFoundError,
    ReplayError,
)
from platform.universal_control_plane.ontology import (
    Decision,
    Determination,
    Evidence,
    HistoryEntry,
    ReplayRecord,
)
from typing import Any


def _digest(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Determination Engine
# ---------------------------------------------------------------------------


@dataclass
class DeterminationEngine:
    """Records and retrieves determinations about any subject."""

    _determinations: dict[str, Determination] = field(default_factory=dict)

    def record(self, det: Determination) -> Determination:
        if det.determination_id in self._determinations:
            raise DuplicateObjectError(f"determination already recorded: {det.determination_id}")
        if not det.verdict.strip():
            from platform.universal_control_plane.errors import DeterminationError

            raise DeterminationError("verdict must be a non-empty string")
        self._determinations[det.determination_id] = det
        return det

    def get(self, determination_id: str) -> Determination:
        if determination_id not in self._determinations:
            raise ObjectNotFoundError(f"determination not found: {determination_id}")
        return self._determinations[determination_id]

    def for_subject(self, subject_id: str) -> list[Determination]:
        return [d for d in self._determinations.values() if d.subject_id == subject_id]

    def latest_for_subject(self, subject_id: str) -> Determination | None:
        results = self.for_subject(subject_id)
        return max(results, key=lambda d: d.tick) if results else None

    def by_verdict(self, verdict: str) -> list[Determination]:
        return [d for d in self._determinations.values() if d.verdict == verdict]

    def count(self) -> int:
        return len(self._determinations)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "DeterminationEngine",
            "count": self.count(),
            "determinations": [d.to_dict() for d in self._determinations.values()],
        }


# ---------------------------------------------------------------------------
# Decision Engine
# ---------------------------------------------------------------------------


@dataclass
class DecisionEngine:
    """Records decisions with their rationale and considered alternatives."""

    _decisions: dict[str, Decision] = field(default_factory=dict)

    def record(self, decision: Decision) -> Decision:
        if decision.decision_id in self._decisions:
            raise DuplicateObjectError(f"decision already recorded: {decision.decision_id}")
        if not decision.choice.strip():
            from platform.universal_control_plane.errors import DeterminationError

            raise DeterminationError("choice must be a non-empty string")
        self._decisions[decision.decision_id] = decision
        return decision

    def get(self, decision_id: str) -> Decision:
        if decision_id not in self._decisions:
            raise ObjectNotFoundError(f"decision not found: {decision_id}")
        return self._decisions[decision_id]

    def for_subject(self, subject_id: str) -> list[Decision]:
        return [d for d in self._decisions.values() if d.subject_id == subject_id]

    def for_determination(self, determination_id: str) -> list[Decision]:
        return [d for d in self._decisions.values() if d.determination_id == determination_id]

    def count(self) -> int:
        return len(self._decisions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "DecisionEngine",
            "count": self.count(),
            "decisions": [d.to_dict() for d in self._decisions.values()],
        }


# ---------------------------------------------------------------------------
# History Engine
# ---------------------------------------------------------------------------


@dataclass
class HistoryEngine:
    """Append-only history log for every control-plane subject."""

    _entries: list[HistoryEntry] = field(default_factory=list)

    def append(self, entry: HistoryEntry) -> HistoryEntry:
        self._entries.append(entry)
        return entry

    def for_subject(self, subject_id: str) -> list[HistoryEntry]:
        return [e for e in self._entries if e.subject_id == subject_id]

    def by_event(self, event: str) -> list[HistoryEntry]:
        return [e for e in self._entries if e.event == event]

    def all(self) -> list[HistoryEntry]:
        return list(self._entries)

    def count(self) -> int:
        return len(self._entries)

    def digest(self) -> str:
        """Content digest of the full ordered log — changes on any append."""
        return _digest([e.to_dict() for e in self._entries])

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "HistoryEngine",
            "count": self.count(),
            "digest": self.digest(),
            "entries": [e.to_dict() for e in self._entries],
        }


# ---------------------------------------------------------------------------
# Replay Engine
# ---------------------------------------------------------------------------


@dataclass
class ReplayEngine:
    """Records replayable execution records and verifies determinism."""

    _records: dict[str, ReplayRecord] = field(default_factory=dict)

    def record(self, replay: ReplayRecord) -> ReplayRecord:
        if replay.replay_id in self._records:
            raise DuplicateObjectError(f"replay record already exists: {replay.replay_id}")
        self._records[replay.replay_id] = replay
        return replay

    def get(self, replay_id: str) -> ReplayRecord:
        if replay_id not in self._records:
            raise ObjectNotFoundError(f"replay record not found: {replay_id}")
        return self._records[replay_id]

    def verify(self, replay_id: str, inputs_digest: str, outputs_digest: str) -> bool:
        """Return True iff both digests match the recorded replay."""
        rec = self.get(replay_id)
        if rec.inputs_digest != inputs_digest:
            raise ReplayError(
                f"inputs digest mismatch for replay {replay_id!r}: "
                f"recorded={rec.inputs_digest!r} given={inputs_digest!r}"
            )
        if rec.outputs_digest != outputs_digest:
            raise ReplayError(
                f"outputs digest mismatch for replay {replay_id!r}: "
                f"recorded={rec.outputs_digest!r} given={outputs_digest!r}"
            )
        return True

    def for_subject(self, subject_id: str) -> list[ReplayRecord]:
        return [r for r in self._records.values() if r.subject_id == subject_id]

    def count(self) -> int:
        return len(self._records)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "ReplayEngine",
            "count": self.count(),
            "records": [r.to_dict() for r in self._records.values()],
        }


# ---------------------------------------------------------------------------
# Evidence Engine
# ---------------------------------------------------------------------------


@dataclass
class EvidenceEngine:
    """Records content-addressed evidence and verifies payload integrity."""

    _evidence: dict[str, Evidence] = field(default_factory=dict)

    @staticmethod
    def make_digest(payload: Any) -> str:
        """Compute the canonical payload digest for an evidence payload."""
        return _digest(payload)

    def record(self, evidence: Evidence) -> Evidence:
        if evidence.evidence_id in self._evidence:
            raise DuplicateObjectError(f"evidence record already exists: {evidence.evidence_id}")
        if not evidence.payload_digest.strip():
            raise EvidenceError("payload_digest must be non-empty")
        self._evidence[evidence.evidence_id] = evidence
        return evidence

    def get(self, evidence_id: str) -> Evidence:
        if evidence_id not in self._evidence:
            raise ObjectNotFoundError(f"evidence record not found: {evidence_id}")
        return self._evidence[evidence_id]

    def verify(self, evidence_id: str, payload: Any) -> bool:
        """Recompute the digest from *payload* and compare to the recorded digest."""
        rec = self.get(evidence_id)
        actual = self.make_digest(payload)
        if actual != rec.payload_digest:
            raise EvidenceError(
                f"evidence digest mismatch for {evidence_id!r}: "
                f"recorded={rec.payload_digest!r} computed={actual!r}"
            )
        return True

    def for_subject(self, subject_id: str) -> list[Evidence]:
        return [e for e in self._evidence.values() if e.subject_id == subject_id]

    def by_kind(self, kind: str) -> list[Evidence]:
        return [e for e in self._evidence.values() if e.kind == kind]

    def count(self) -> int:
        return len(self._evidence)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "EvidenceEngine",
            "count": self.count(),
            "evidence": [e.to_dict() for e in self._evidence.values()],
        }
