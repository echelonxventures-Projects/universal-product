"""UCOS-UICM-000001 — the certification projection.

UICM is not a certification authority and this module is careful to be unable to become
one. It contains no rule, no criterion, no verdict logic and no certificate type. What it
does is *project* the closure measurement into the three inputs
:mod:`engine.universal_certification` already consumes, hand them to that engine, and
report the decision it returns unchanged.

    closure measurement  ->  ValidationInput        (did the closure claims validate?)
                         ->  MeasurementInput       (decidable closure metrics)
                         ->  RepositoryTruthInput   (population homed? gaps closed?)
                                     |
                                     v
                     UniversalCertificationEngine (UCOS-EPIC-006)
                                     |
                                     v
                          Certificate + evidence

Three consequences of being a projection rather than an authority, each of which is a
property of the code and not a promise:

**A NOT-CERTIFIED decision is reported as-is.** There is no branch here that upgrades,
retries or reinterprets a refusal. If the located engine refuses, this module's output
says so, which is the expected outcome while the population carries open gaps.

**The measurements are computed, never asserted.** ``Measurement.evaluate`` derives
``satisfied`` from the value, comparator and threshold, so this module cannot hand the
certifier a metric that claims a satisfaction it did not measure.

**Repository-truth consistency is the certifier's own conjunction.**
``RepositoryTruthInput.consistent`` requires closed, fully homed and zero open gaps. This
module supplies the counts and does not compute the verdict, so it cannot report closure
the certifier would not have granted.

The validation projection carries the provisional-state disclosure check because the
located engine requires it (``DisclosurePresentRule``), and the disclosure itself comes
from its own owner, ``engine.foundation.contracts.disclosure`` — UICM neither writes nor
paraphrases it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.foundation.contracts.disclosure import build_disclosure, disclosure_present
from engine.uicm.gap import GapRegister
from engine.uicm.matrix import ClosureMatrix
from engine.uicm.model import ClosureDeclaration, digest
from engine.uicm.observation import ObservationRegistry
from engine.uicm.validation import ClosureValidation
from engine.universal_certification.contracts import (
    DISCLOSURE_CHECK_ID,
    CertificationClass,
    Measurement,
    MeasurementComparator,
    MeasurementInput,
    RepositoryTruthInput,
    RuleSeverity,
    ValidationInput,
)
from engine.universal_certification.engine import (
    CertificationDecision,
    UniversalCertificationEngine,
)
from engine.universal_certification.evidence import build_certification_evidence

#: The projection document format. Deliberately not a certificate format: this module
#: emits a projection and a reference to somebody else's decision.
CERTIFICATION_PROJECTION_FORMAT = "ucos-uicm-certification-projection/1.0.0"

#: The metric identifiers this projection submits. Each is decidable and each threshold is
#: the zero-tolerance the programme declares.
METRIC_HIDDEN_GAPS = "uicm.hidden_gaps"
METRIC_DUPLICATE_OWNERSHIP = "uicm.duplicate_ownership"
METRIC_INVENTED_CAPABILITY = "uicm.invented_capability"
METRIC_ORPHAN_ARTIFACT = "uicm.orphan_artifact"
METRIC_UNEVIDENCED_CLOSURE = "uicm.unevidenced_closure"
METRIC_MUTABLE_REGISTRY_OPERATION = "uicm.mutable_registry_operation"
METRIC_MATRIX_TOTALITY = "uicm.matrix_totality"
METRIC_BLOCKING_INVARIANTS = "uicm.blocking_invariant_violations"
METRIC_OBSERVATION_CHAIN = "uicm.observation_chain_intact"
METRIC_CLOSED_CELLS = "uicm.closed_cell_ratio"


@dataclass(frozen=True, slots=True)
class ClosureCertification:
    """The located owner's decision plus the projection that produced it.

    ``status`` and ``certified`` are read straight off the decision. This class exposes no
    method that could alter either.
    """

    decision: CertificationDecision
    validation_input: ValidationInput
    measurement_input: MeasurementInput
    repository_truth: RepositoryTruthInput
    evidence: Any

    @property
    def certified(self) -> bool:
        """The located owner's verdict, unmodified."""
        return self.decision.certified

    @property
    def status(self) -> str:
        return self.decision.status.value

    @property
    def certification_id(self) -> str:
        return self.decision.certification_id

    @property
    def blocking_failures(self) -> tuple[str, ...]:
        return self.decision.blocking_failures

    def to_document(self) -> dict[str, Any]:
        return {
            "format": CERTIFICATION_PROJECTION_FORMAT,
            "authority": "NONE - DERIVED TRUTH",
            "certification_owner": "engine/universal_certification (UCOS-EPIC-006)",
            "uicm_role": "PROJECTION - supplies inputs, reports the owner's decision unchanged",
            "status": self.status,
            "certified": self.certified,
            "certification_id": self.certification_id,
            "blocking_failures": list(self.blocking_failures),
            "counts": self.decision.counts(),
            "consumed_inputs": {
                "validation": self.validation_input.to_dict(),
                "measurement": self.measurement_input.to_dict(),
                "repository_truth": self.repository_truth.to_dict(),
            },
            "rule_findings": [f.to_dict() for f in self.decision.findings],
            "compliance": self.decision.compliance.to_dict(),
            "certificate": self.decision.certificate.to_dict(),
            "evidence_sha256": self.evidence.content_sha256(),
        }

    def digest(self) -> str:
        return digest(self.to_document())


def _validation_projection(
    *,
    declaration: ClosureDeclaration,
    matrix: ClosureMatrix,
    validation: ClosureValidation,
) -> ValidationInput:
    """Project the closure-invariant report into the certifier's validation input.

    ``checks_run`` is the declared invariant set plus the disclosure check the located
    engine requires. The disclosure verdict is measured by its own owner rather than
    assumed: a missing disclosure lands in ``blocking_failures`` and the certifier refuses.
    """
    disclosure = build_disclosure()
    checks = [result.invariant_id for result in validation.results]
    failures = list(validation.blocking_failures)
    checks.append(DISCLOSURE_CHECK_ID)
    if not disclosure_present(disclosure):
        failures.append(DISCLOSURE_CHECK_ID)
    return ValidationInput(
        target_id=declaration.programme_id,
        blueprint_id=f"{declaration.programme_id}-CLOSURE-MATRIX",
        verdict="pass" if validation.accepted else "fail",
        accepted=validation.accepted,
        checks_run=tuple(checks),
        blocking_failures=tuple(failures),
        counts=validation.counts(),
        evidence_present=True,
        evidence_sha256=digest(
            {
                "validation": validation.to_document(),
                "matrix": matrix.digest(),
            }
        ),
    )


def _measurement_projection(
    *,
    matrix: ClosureMatrix,
    gaps: GapRegister,
    validation: ClosureValidation,
    observations: ObservationRegistry,
) -> MeasurementInput:
    """Project the closure measurement into decidable metrics with computed verdicts."""
    hidden = len(matrix.non_pass_cells()) - len(gaps)
    duplicate_ownership = len(
        validation.result("UICM-INV-06").evidence.get("duplicate_capability_rows", {})
    )
    invented = len(validation.result("UICM-INV-08").evidence.get("invented", []))
    orphans = int(validation.result("UICM-INV-09").evidence.get("orphan_total", 0))
    unevidenced = int(validation.result("UICM-INV-04").evidence.get("offender_total", 0))
    mutable_ops = int(validation.result("UICM-INV-16").evidence.get("mutating_operation_total", 0))
    totality = validation.result("UICM-INV-11")
    closed_cells = sum(1 for cell in matrix.cells if cell.is_pass)
    metrics = (
        Measurement.evaluate(
            metric_id=METRIC_HIDDEN_GAPS,
            value=abs(hidden),
            threshold=0,
            comparator=MeasurementComparator.EQ,
            severity=RuleSeverity.BLOCKING,
            unit="cells",
        ),
        Measurement.evaluate(
            metric_id=METRIC_DUPLICATE_OWNERSHIP,
            value=duplicate_ownership,
            threshold=0,
            comparator=MeasurementComparator.EQ,
            severity=RuleSeverity.BLOCKING,
            unit="capabilities",
        ),
        Measurement.evaluate(
            metric_id=METRIC_INVENTED_CAPABILITY,
            value=invented,
            threshold=0,
            comparator=MeasurementComparator.EQ,
            severity=RuleSeverity.BLOCKING,
            unit="capabilities",
        ),
        Measurement.evaluate(
            metric_id=METRIC_ORPHAN_ARTIFACT,
            value=orphans,
            threshold=0,
            comparator=MeasurementComparator.EQ,
            severity=RuleSeverity.BLOCKING,
            unit="artifacts",
        ),
        Measurement.evaluate(
            metric_id=METRIC_UNEVIDENCED_CLOSURE,
            value=unevidenced,
            threshold=0,
            comparator=MeasurementComparator.EQ,
            severity=RuleSeverity.BLOCKING,
            unit="cells",
        ),
        Measurement.evaluate(
            metric_id=METRIC_MUTABLE_REGISTRY_OPERATION,
            value=mutable_ops,
            threshold=0,
            comparator=MeasurementComparator.EQ,
            severity=RuleSeverity.BLOCKING,
            unit="operations",
        ),
        Measurement.evaluate(
            metric_id=METRIC_MATRIX_TOTALITY,
            value=int(totality.evidence.get("cells", 0)),
            threshold=int(totality.evidence.get("expected", 0)),
            comparator=MeasurementComparator.EQ,
            severity=RuleSeverity.BLOCKING,
            unit="cells",
        ),
        Measurement.evaluate(
            metric_id=METRIC_OBSERVATION_CHAIN,
            value=1 if observations.verify() else 0,
            threshold=1,
            comparator=MeasurementComparator.EQ,
            severity=RuleSeverity.BLOCKING,
            unit="boolean",
        ),
        Measurement.evaluate(
            metric_id=METRIC_BLOCKING_INVARIANTS,
            value=len(validation.blocking_failures),
            threshold=0,
            comparator=MeasurementComparator.EQ,
            severity=RuleSeverity.BLOCKING,
            unit="invariants",
        ),
        # The one metric that is *expected* to fall short while the population carries
        # open gaps. It is submitted as BLOCKING deliberately: a closure certificate that
        # ignored unclosed cells would certify the opposite of what it measured.
        Measurement.evaluate(
            metric_id=METRIC_CLOSED_CELLS,
            value=closed_cells,
            threshold=matrix.cell_count,
            comparator=MeasurementComparator.EQ,
            severity=RuleSeverity.BLOCKING,
            unit="cells",
        ),
    )
    return MeasurementInput.create(metrics, source="engine.uicm.measurement")


def _repository_truth_projection(
    *, matrix: ClosureMatrix, gaps: GapRegister
) -> RepositoryTruthInput:
    """Project the closure population into the certifier's repository-truth input.

    The population is the concept set: every capability is "homed" because every one
    resolves to a canonical owner. Gaps are the closure gaps by dimension, so
    ``consistent`` — which the certifier computes, not this module — is false exactly while
    a closure gap stands.
    """
    homed = sum(
        1
        for capability in matrix.capabilities
        if capability.canonical_owner and capability.capability_id
    )
    return RepositoryTruthInput.create(
        snapshot_id=f"{matrix.declaration_digest[:16]}-closure-population",
        content_sha256=matrix.digest(),
        total_concepts=len(matrix.capabilities),
        homed_concepts=homed,
        gaps=gaps.by_dimension(),
        closed=len(gaps) == 0,
    )


def project_certification(
    *,
    declaration: ClosureDeclaration,
    matrix: ClosureMatrix,
    gaps: GapRegister,
    validation: ClosureValidation,
    observations: ObservationRegistry,
    engine: UniversalCertificationEngine | None = None,
) -> ClosureCertification:
    """Submit the closure measurement to the located certifier and report its decision.

    No argument of this function can influence the verdict except by changing what was
    measured, and the returned decision is the located engine's own object.
    """
    certifier = engine or UniversalCertificationEngine()
    validation_input = _validation_projection(
        declaration=declaration, matrix=matrix, validation=validation
    )
    measurement_input = _measurement_projection(
        matrix=matrix, gaps=gaps, validation=validation, observations=observations
    )
    repository_truth = _repository_truth_projection(matrix=matrix, gaps=gaps)
    decision = certifier.certify_inputs(
        validation=validation_input,
        measurement=measurement_input,
        repository_truth=repository_truth,
        version=declaration.programme_version,
        certification_class=CertificationClass.UNIVERSAL_READINESS,
    )
    return ClosureCertification(
        decision=decision,
        validation_input=validation_input,
        measurement_input=measurement_input,
        repository_truth=repository_truth,
        evidence=build_certification_evidence(decision),
    )


__all__ = [
    "CERTIFICATION_PROJECTION_FORMAT",
    "METRIC_BLOCKING_INVARIANTS",
    "METRIC_CLOSED_CELLS",
    "METRIC_DUPLICATE_OWNERSHIP",
    "METRIC_HIDDEN_GAPS",
    "METRIC_INVENTED_CAPABILITY",
    "METRIC_MATRIX_TOTALITY",
    "METRIC_MUTABLE_REGISTRY_OPERATION",
    "METRIC_OBSERVATION_CHAIN",
    "METRIC_ORPHAN_ARTIFACT",
    "METRIC_UNEVIDENCED_CLOSURE",
    "ClosureCertification",
    "project_certification",
]
