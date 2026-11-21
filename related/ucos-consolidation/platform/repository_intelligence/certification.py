"""UCOS-EPIC-014 — Repository Certification (Terminal T5).

Issues the immutable, self-verifying **Repository Intelligence Certificate**: the sealed
statement that, at a known repository content digest, all eight discovery dimensions ran,
validation adjudicated them, and the repository either is or is not internally consistent.

Determination is fail-closed and mechanical — it is a function of the validation verdict
alone, never a judgement:

    * ``CERTIFIED-INTELLIGENT`` with ``gate OPEN``  — validation passed.
    * ``NOT-CERTIFIED`` with ``gate CLOSED`` — validation failed; the certificate still
      issues, carrying the exact blocking rules, because a suppressed certificate would
      hide the failure it exists to report.

The certificate confers **no constitutional authority** (DE-05 / IP-01): it records derived
engineering truth about the repository. Repository evidence remains the only authority.

Sealing reuses the repository's established idiom: a SHA-256 over the canonical JSON of the
verdict-bearing core only — never volatile detail, never a wall-clock — so re-running against
unchanged content reproduces the identical seal, and :meth:`RepositoryCertificate.verify_integrity`
detects any mutation.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.repository_intelligence.contracts import (
    CERTIFICATE_FORMAT,
    CERTIFICATION_STANDARD,
    CERTIFICATION_STANDARD_VERSION,
    DERIVED_TRUTH,
    REPOSITORY_INTELLIGENCE_AUTHORITY,
    REPOSITORY_INTELLIGENCE_PROGRAMME,
    Determination,
    RepositoryIntelligenceReport,
    Verdict,
)
from platform.repository_intelligence.errors import RepositoryCertificationError
from platform.repository_intelligence.validation import RepositoryValidationReport
from typing import Any

from engine.runtime.disclosure import build_disclosure

#: The gate states a certificate can report.
GATE_OPEN = "OPEN"
GATE_CLOSED = "CLOSED"


@dataclass(frozen=True, slots=True)
class RepositoryCertificate:
    """An immutable, content-addressed, self-verifying Repository Intelligence Certificate."""

    certificate_id: str
    programme: str
    repository_id: str
    determination: Determination
    gate: str
    substrate_digest: str
    report_sha256: str
    validation_sha256: str
    graph_digest: str
    dimension_verdicts: Mapping[str, str]
    metrics: Mapping[str, int]
    blocking_rules: tuple[str, ...]
    advisory_rules: tuple[str, ...]
    standard: str
    standard_version: str
    authority: str
    derived_from: str
    disclosure: Mapping[str, Any]
    seal_sha256: str

    @staticmethod
    def _core(
        *,
        repository_id: str,
        determination: Determination,
        gate: str,
        substrate_digest: str,
        report_sha256: str,
        validation_sha256: str,
        graph_digest: str,
        dimension_verdicts: Mapping[str, str],
        metrics: Mapping[str, int],
        blocking_rules: tuple[str, ...],
        advisory_rules: tuple[str, ...],
        disclosure: Mapping[str, Any],
    ) -> dict[str, Any]:
        """The canonical, hashable, verdict-bearing core (excludes id and seal)."""
        return {
            "programme": REPOSITORY_INTELLIGENCE_PROGRAMME,
            "repository_id": repository_id,
            "determination": determination.value,
            "gate": gate,
            "substrate_digest": substrate_digest,
            "report_sha256": report_sha256,
            "validation_sha256": validation_sha256,
            "graph_digest": graph_digest,
            "dimension_verdicts": dict(sorted(dimension_verdicts.items())),
            "metrics": dict(sorted(metrics.items())),
            "blocking_rules": list(blocking_rules),
            "advisory_rules": list(advisory_rules),
            "standard": CERTIFICATION_STANDARD,
            "standard_version": CERTIFICATION_STANDARD_VERSION,
            "authority": REPOSITORY_INTELLIGENCE_AUTHORITY,
            "derived_from": DERIVED_TRUTH,
            "disclosure": dict(disclosure),
        }

    @classmethod
    def issue(
        cls,
        report: RepositoryIntelligenceReport,
        validation: RepositoryValidationReport,
    ) -> RepositoryCertificate:
        """Issue the certificate for a report and its validation.

        Raises:
            RepositoryCertificationError: if the validation does not belong to the report —
                certifying a report against someone else's validation would seal a lie.
        """
        if validation.report_sha256 != report.report_sha256:
            raise RepositoryCertificationError(
                "validation report does not correspond to the intelligence report",
                report_sha256=report.report_sha256,
                validated_sha256=validation.report_sha256,
            )
        determination = (
            Determination.CERTIFIED_INTELLIGENT
            if validation.verdict is Verdict.PASS
            else Determination.NOT_CERTIFIED
        )
        gate = GATE_OPEN if determination is Determination.CERTIFIED_INTELLIGENT else GATE_CLOSED
        counts = report.counts()
        validation_counts = validation.counts()
        metrics = {
            "units": counts["units"],
            "capabilities": counts["capabilities"],
            "graph_nodes": counts["graph_nodes"],
            "graph_edges": counts["graph_edges"],
            "dimensions": counts["dimensions"],
            "checks": counts["checks"],
            "blocking_failed": counts["blocking_failed"],
            "advisory_failed": counts["advisory_failed"],
            "recommendations": counts["recommendations"],
            "unowned": counts["unowned"],
            "unproven_reuse": counts["unproven_reuse"],
            "rules": validation_counts["rules"],
            "rules_passed": validation_counts["passed"],
            "composed_acceptance_gates": validation_counts["composed_acceptance_gates"],
            "intelligence_rules": validation_counts["intelligence_rules"],
        }
        disclosure = build_disclosure()
        core = cls._core(
            repository_id=report.repository_id,
            determination=determination,
            gate=gate,
            substrate_digest=report.substrate_digest,
            report_sha256=report.report_sha256,
            validation_sha256=validation.validation_sha256,
            graph_digest=report.graph.digest(),
            dimension_verdicts=report.dimension_verdicts(),
            metrics=metrics,
            blocking_rules=validation.blocking_failures(),
            advisory_rules=validation.advisory_failures(),
            disclosure=disclosure,
        )
        seal = content_hash(core)
        return cls(
            certificate_id=f"{REPOSITORY_INTELLIGENCE_PROGRAMME}-{seal[:16]}",
            programme=REPOSITORY_INTELLIGENCE_PROGRAMME,
            repository_id=report.repository_id,
            determination=determination,
            gate=gate,
            substrate_digest=report.substrate_digest,
            report_sha256=report.report_sha256,
            validation_sha256=validation.validation_sha256,
            graph_digest=report.graph.digest(),
            dimension_verdicts=dict(report.dimension_verdicts()),
            metrics=metrics,
            blocking_rules=validation.blocking_failures(),
            advisory_rules=validation.advisory_failures(),
            standard=CERTIFICATION_STANDARD,
            standard_version=CERTIFICATION_STANDARD_VERSION,
            authority=REPOSITORY_INTELLIGENCE_AUTHORITY,
            derived_from=DERIVED_TRUTH,
            disclosure=disclosure,
            seal_sha256=seal,
        )

    # -- integrity --------------------------------------------------------
    @property
    def certified(self) -> bool:
        return self.determination is Determination.CERTIFIED_INTELLIGENT

    @property
    def gate_open(self) -> bool:
        return self.gate == GATE_OPEN

    def recompute_seal(self) -> str:
        """Recompute the seal from the current field values."""
        return content_hash(
            self._core(
                repository_id=self.repository_id,
                determination=self.determination,
                gate=self.gate,
                substrate_digest=self.substrate_digest,
                report_sha256=self.report_sha256,
                validation_sha256=self.validation_sha256,
                graph_digest=self.graph_digest,
                dimension_verdicts=self.dimension_verdicts,
                metrics=self.metrics,
                blocking_rules=self.blocking_rules,
                advisory_rules=self.advisory_rules,
                disclosure=self.disclosure,
            )
        )

    def verify_integrity(self) -> bool:
        """True iff the stored seal matches a recomputation (no mutation occurred)."""
        return self.recompute_seal() == self.seal_sha256

    def require_integrity(self) -> None:
        """Raise if the certificate was mutated after issue."""
        if not self.verify_integrity():
            raise RepositoryCertificationError(
                "repository intelligence certificate integrity check failed",
                certificate_id=self.certificate_id,
                expected=self.seal_sha256,
                actual=self.recompute_seal(),
            )

    # -- projections ------------------------------------------------------
    def hook_line(self) -> str:
        """The single-line session-start summary, matching the repository's hook idiom."""
        return (
            f"{self.programme}: {self.determination.value}"
            f" | capabilities={self.metrics['capabilities']}"
            f" | nodes={self.metrics['graph_nodes']}"
            f" | edges={self.metrics['graph_edges']}"
            f" | dimensions={self.metrics['dimensions']}/8"
            f" | rules={self.metrics['rules_passed']}/{self.metrics['rules']} PASS"
            f" | blocking={len(self.blocking_rules) or 'none'}"
            f" | gate={self.gate}"
            f" | seal={self.seal_sha256[:16]}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "certificate_format": CERTIFICATE_FORMAT,
            "certificate_id": self.certificate_id,
            "programme": self.programme,
            "repository_id": self.repository_id,
            "determination": self.determination.value,
            "certified": self.certified,
            "gate": self.gate,
            "substrate_digest": self.substrate_digest,
            "intelligence_report_sha256": self.report_sha256,
            "validation_sha256": self.validation_sha256,
            "graph_digest": self.graph_digest,
            "dimension_verdicts": dict(sorted(self.dimension_verdicts.items())),
            "metrics": dict(sorted(self.metrics.items())),
            "blocking_rules": list(self.blocking_rules),
            "advisory_rules": list(self.advisory_rules),
            "standard": self.standard,
            "standard_version": self.standard_version,
            "authority": self.authority,
            "derived_from": self.derived_from,
            "disclosure": dict(self.disclosure),
            "seal_sha256": self.seal_sha256,
        }


def certify(
    report: RepositoryIntelligenceReport, validation: RepositoryValidationReport
) -> RepositoryCertificate:
    """Convenience: issue the certificate for a report and its validation."""
    return RepositoryCertificate.issue(report, validation)


__all__ = ["GATE_OPEN", "GATE_CLOSED", "RepositoryCertificate", "certify"]
