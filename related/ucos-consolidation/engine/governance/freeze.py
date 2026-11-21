"""EPIC-VAL-003 — Architecture Freeze recommendation (Terminal T3).

The **Freeze Recommendation** is the pipeline's terminal artifact: a deterministic,
content-addressed attestation of whether the repository's architecture may be
frozen (99-FREEZE). It is derived purely from the unified repository decision and
the repository readiness report — the pipeline recommends **FREEZE iff** the
repository is fail-closed GOVERNED *and* freeze-ready (every blocking gate, including
the 100% coverage and freeze-readiness gates, passed). Any other state yields
**DO-NOT-FREEZE** with an explicit, attributable rationale.

The recommendation is *advisory of engineering readiness only*: it asserts
``ENGINEERING-EXECUTION-ONLY`` authority and carries the EC-1 provisional-state
disclosure — it recommends an engineering freeze, never a constitutional
ratification (DE-05 / IP-01). It embeds no wall-clock or ambient state, so the same
decision + readiness yield a byte-identical recommendation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.governance.contracts import (
    GOVERNANCE_AUTHORITY,
    RepositoryDecision,
    content_hash,
)
from engine.runtime.disclosure import build_disclosure

if TYPE_CHECKING:  # pragma: no cover - typing only
    from engine.acceptance.readiness import RepositoryReadiness

#: The freeze-recommendation report format identifier.
FREEZE_FORMAT = "ucos-freeze-recommendation/1.0.0"

FREEZE = "FREEZE"
DO_NOT_FREEZE = "DO-NOT-FREEZE"


@dataclass(frozen=True, slots=True)
class FreezeRecommendation:
    """A deterministic, content-addressed architecture-freeze recommendation."""

    repository_id: str
    epic_id: str
    recommendation: str
    freeze_ready: bool
    governed: bool
    rationale: tuple[str, ...]
    decision_ref: str
    readiness_ref: str
    acceptance_id: str
    authority: str
    disclosure: dict[str, Any]
    recommendation_sha256: str

    @property
    def freeze(self) -> bool:
        return self.recommendation == FREEZE

    def _core(self) -> dict[str, Any]:
        return {
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "recommendation": self.recommendation,
            "freeze_ready": self.freeze_ready,
            "governed": self.governed,
            "rationale": list(self.rationale),
            "decision_ref": self.decision_ref,
            "readiness_ref": self.readiness_ref,
            "acceptance_id": self.acceptance_id,
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "freeze_format": FREEZE_FORMAT,
            **self._core(),
            "recommendation_sha256": self.recommendation_sha256,
        }


def build_freeze_recommendation(
    decision: RepositoryDecision, readiness: RepositoryReadiness
) -> FreezeRecommendation:
    """Assemble the freeze recommendation from the decision + readiness report.

    Recommends FREEZE iff the repository is GOVERNED **and** freeze-ready; otherwise
    DO-NOT-FREEZE with a deterministic, attributable rationale (the unified decision's
    blocking reasons, else the readiness blocking gates, else a generic marker).
    """
    freeze_ready = readiness.ready
    governed = decision.governed
    should_freeze = governed and freeze_ready

    if should_freeze:
        rationale: tuple[str, ...] = ()
    elif decision.blocking_reasons:
        rationale = decision.blocking_reasons
    elif readiness.blocking_failures:
        rationale = tuple(f"acceptance:{g}" for g in readiness.blocking_failures)
    else:
        rationale = ("repository-not-governed",)

    recommendation = FREEZE if should_freeze else DO_NOT_FREEZE
    disclosure = build_disclosure()
    core = {
        "repository_id": decision.repository_id,
        "epic_id": decision.epic_id,
        "recommendation": recommendation,
        "freeze_ready": freeze_ready,
        "governed": governed,
        "rationale": list(rationale),
        "decision_ref": decision.decision_sha256,
        "readiness_ref": readiness.readiness_sha256,
        "acceptance_id": readiness.acceptance_id,
        "authority": GOVERNANCE_AUTHORITY,
        "disclosure": dict(disclosure),
    }
    return FreezeRecommendation(
        repository_id=decision.repository_id,
        epic_id=decision.epic_id,
        recommendation=recommendation,
        freeze_ready=freeze_ready,
        governed=governed,
        rationale=rationale,
        decision_ref=decision.decision_sha256,
        readiness_ref=readiness.readiness_sha256,
        acceptance_id=readiness.acceptance_id,
        authority=GOVERNANCE_AUTHORITY,
        disclosure=disclosure,
        recommendation_sha256=content_hash(core),
    )


__all__ = [
    "FREEZE_FORMAT",
    "FREEZE",
    "DO_NOT_FREEZE",
    "FreezeRecommendation",
    "build_freeze_recommendation",
]
