"""ZG-P-02 — Coverage certification API (Universe→Code Coverage Instrument).

The certification-facing surface that ZG-D-05 / final Extended-Invariant certification
reads to determine whether **G4** may be declared CLOSED. It produces a single immutable,
content-addressed :class:`CoverageCertification` from a
:class:`~platform.coverage.engine.CoverageEngine`, exposing exactly the mandated fields:

    coverage_status · coverage_percentage · coverage_gaps · coverage_orphans ·
    coverage_violations · coverage_fingerprint · coverage_determinism_status ·
    coverage_certification_status

Certification is fail-closed: it is ``CERTIFIED`` only when the recompute is
deterministic, there are **no structural violations** (no orphan code, no orphan
universe, no duplicate coverage, no fingerprint divergence), and — under the strict
certification policy — no coverage gaps remain. Otherwise it is ``NOT-CERTIFIED`` with
machine-readable reasons.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.coverage.contracts import CoverageNodeKind
from platform.coverage.engine import CoverageEngine
from platform.coverage.errors import CoverageCertificationError
from platform.coverage.graph import CoverageGraph
from platform.foundation.contracts import content_hash
from typing import Any

#: Certification verdicts.
CERTIFIED = "CERTIFIED"
NOT_CERTIFIED = "NOT-CERTIFIED"

#: Determinism verdicts.
DETERMINISTIC = "deterministic"
NON_DETERMINISTIC = "non-deterministic"


@dataclass(frozen=True, slots=True)
class CoverageCertification:
    """An immutable, content-addressed coverage certification record (G4 evidence)."""

    coverage_status: str
    coverage_percentage: float
    coverage_gaps: tuple[str, ...]
    coverage_orphans: tuple[str, ...]
    coverage_violations: tuple[str, ...]
    coverage_fingerprint: str
    coverage_determinism_status: str
    coverage_certification_status: str
    reasons: tuple[str, ...]
    certification_id: str = ""

    @classmethod
    def _build(
        cls,
        *,
        coverage_status: str,
        coverage_percentage: float,
        coverage_gaps: tuple[str, ...],
        coverage_orphans: tuple[str, ...],
        coverage_violations: tuple[str, ...],
        coverage_fingerprint: str,
        coverage_determinism_status: str,
        coverage_certification_status: str,
        reasons: tuple[str, ...],
    ) -> CoverageCertification:
        core = {
            "coverage_status": coverage_status,
            "coverage_percentage": coverage_percentage,
            "coverage_gaps": list(coverage_gaps),
            "coverage_orphans": list(coverage_orphans),
            "coverage_violations": list(coverage_violations),
            "coverage_fingerprint": coverage_fingerprint,
            "coverage_determinism_status": coverage_determinism_status,
            "coverage_certification_status": coverage_certification_status,
            "reasons": list(reasons),
        }
        return cls(
            coverage_status=coverage_status,
            coverage_percentage=coverage_percentage,
            coverage_gaps=coverage_gaps,
            coverage_orphans=coverage_orphans,
            coverage_violations=coverage_violations,
            coverage_fingerprint=coverage_fingerprint,
            coverage_determinism_status=coverage_determinism_status,
            coverage_certification_status=coverage_certification_status,
            reasons=reasons,
            certification_id=f"UCOS-COVC-{content_hash(core)[:16]}",
        )

    @property
    def certified(self) -> bool:
        return self.coverage_certification_status == CERTIFIED

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "coverage_status": self.coverage_status,
            "coverage_percentage": self.coverage_percentage,
            "coverage_gaps": list(self.coverage_gaps),
            "coverage_orphans": list(self.coverage_orphans),
            "coverage_violations": list(self.coverage_violations),
            "coverage_fingerprint": self.coverage_fingerprint,
            "coverage_determinism_status": self.coverage_determinism_status,
            "coverage_certification_status": self.coverage_certification_status,
            "reasons": list(self.reasons),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def assess(engine: CoverageEngine, *, strict: bool = True) -> CoverageCertification:
    """Produce the fail-closed coverage certification for ``engine`` (G4 assertion).

    ``strict`` (the certification default) requires zero coverage gaps in addition to
    zero structural violations. A non-strict assessment certifies structural integrity
    + determinism only (gaps allowed, e.g. for an in-progress delivery baseline).
    """
    if not isinstance(engine, CoverageEngine):
        raise CoverageCertificationError("assess requires a CoverageEngine")

    # Deterministic double-recompute (independent graph instances).
    graph_a = CoverageGraph(engine._source.collect())  # noqa: SLF001 - engine-owned source
    graph_b = CoverageGraph(engine._source.collect())  # noqa: SLF001
    fingerprint = graph_a.fingerprint()
    determinism = DETERMINISTIC if fingerprint == graph_b.fingerprint() else NON_DETERMINISTIC

    # Ensure the registry reflects the current evidence, then verify integrity.
    engine.compute()
    verification = engine.verify()

    gaps = tuple(
        f"{n.kind.value}:{n.ref}:{graph_a.status_of(n.node_id).value}" for n in graph_a.gaps()
    )
    orphans = tuple(f"{n.kind.value}:{n.ref}" for n in graph_a.orphans())
    violations = tuple(verification.violations)

    reasons: list[str] = []
    if determinism != DETERMINISTIC:
        reasons.append("recompute-non-deterministic")
    if violations:
        reasons.append(f"structural-violations:{len(violations)}")
    if strict and gaps:
        reasons.append(f"coverage-gaps:{len(gaps)}")

    certification_status = CERTIFIED if not reasons else NOT_CERTIFIED
    coverage_status = "COMPLETE" if not gaps and not orphans else "PARTIAL"

    return CoverageCertification._build(
        coverage_status=coverage_status,
        coverage_percentage=graph_a.coverage_percentage(CoverageNodeKind.UNIVERSE),
        coverage_gaps=gaps,
        coverage_orphans=orphans,
        coverage_violations=violations,
        coverage_fingerprint=fingerprint,
        coverage_determinism_status=determinism,
        coverage_certification_status=certification_status,
        reasons=tuple(reasons),
    )


__all__ = [
    "CERTIFIED",
    "NOT_CERTIFIED",
    "DETERMINISTIC",
    "NON_DETERMINISTIC",
    "CoverageCertification",
    "assess",
]
