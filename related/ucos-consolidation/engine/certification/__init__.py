"""EC-1 Certification Layer (EPIC-008) — deterministic, immutable certification.

Public API surface for the Certification Layer: an additive, record-only certifier
that consumes the Validation Reports and Validation Evidence produced by the
Validation Layer (EPIC-007) and aggregates their verdicts into:

    * a **Certification Decision** (fail-closed CERTIFIED / NOT-CERTIFIED),
    * an **immutable, content-addressed Certification Record**,
    * a **Certification Evidence** record (closing the Validation → Certification
      evidence chain),
    * an append-only, hash-chained **Certification Ledger Entry**, and
    * an EC-1 **Program Closure Report** (the A1…A10 acceptance framework).

The layer is additive and constitutional: it invents no verdict (TP-01 — it only
aggregates validation), mutates no subject, accesses the registry only through the
already-validated upstream artifacts (never a direct corpus/registry write, DP-03),
and is fully deterministic (IMP-007 §5) — an identical Validation Report +
Validation Evidence yields a byte-identical decision, record, evidence, ledger
entry, and closure report. Certification records **engineering readiness only** and
carries the EC-1 provisional-state disclosure — it confers no constitutional
finality or authority (DE-05 / IP-01).

Tasks: TASK-000050 (architecture + contracts + record + criteria), TASK-000051
(decision engine), TASK-000052 (evidence), TASK-000053 (ledger), TASK-000054
(program closure report).
"""

from __future__ import annotations

from engine.certification.closure import (
    CERTIFICATION_ACCEPTANCE_ID,
    EC1_EPICS,
    PROGRAM_NAME,
    AcceptanceEntry,
    ProgramClosureReport,
    build_program_closure,
    certification_framework_status,
)
from engine.certification.contracts import (
    CERTIFICATION_AUTHORITY,
    CERTIFICATION_CONTRACT_VERSION,
    CERTIFICATION_STANDARD,
    CERTIFICATION_STANDARD_VERSION,
    CertificationClass,
    CertificationFinding,
    CertificationRecord,
    CertificationRequest,
    CertificationStatus,
    CertificationSubject,
    CriterionSeverity,
    CriterionStatus,
    canonical_json,
    content_hash,
)
from engine.certification.criteria import (
    CertificationCriterion,
    DisclosureValidatedCriterion,
    ValidationAcceptedCriterion,
    ValidationCompleteCriterion,
    ValidationEvidencePresentCriterion,
    VersionPinnedCriterion,
    default_criteria,
)
from engine.certification.engine import (
    CertificationDecision,
    CertificationEngine,
    certify_validation,
)
from engine.certification.errors import (
    CertificationIntegrityError,
    CertificationLayerError,
    CertificationSubjectError,
    LedgerIntegrityError,
    ProgramClosureError,
)
from engine.certification.evidence import (
    EVIDENCE_FORMAT,
    CertificationEvidence,
    build_certification_evidence,
)
from engine.certification.integrity import (
    INTEGRITY_EVIDENCE_FORMAT,
    INTEGRITY_REPORT_FORMAT,
    CertificationRegister,
    ConstitutionalIntegrityError,
    DuplicateCertificationError,
    IntegrityEvidence,
    IntegrityFinding,
    IntegrityReport,
    build_integrity_evidence,
    enforce_integrity,
    verify_certification_integrity,
)
from engine.certification.ledger import (
    GENESIS_HASH,
    CertificationLedger,
    CertificationLedgerEntry,
)

__all__ = [
    # contracts
    "CERTIFICATION_CONTRACT_VERSION",
    "CERTIFICATION_STANDARD",
    "CERTIFICATION_STANDARD_VERSION",
    "CERTIFICATION_AUTHORITY",
    "canonical_json",
    "content_hash",
    "CriterionSeverity",
    "CriterionStatus",
    "CertificationStatus",
    "CertificationClass",
    "CertificationRequest",
    "CertificationFinding",
    "CertificationSubject",
    "CertificationRecord",
    # criteria
    "CertificationCriterion",
    "ValidationAcceptedCriterion",
    "ValidationEvidencePresentCriterion",
    "DisclosureValidatedCriterion",
    "VersionPinnedCriterion",
    "ValidationCompleteCriterion",
    "default_criteria",
    # decision engine
    "CertificationDecision",
    "CertificationEngine",
    "certify_validation",
    # evidence
    "CertificationEvidence",
    "build_certification_evidence",
    "EVIDENCE_FORMAT",
    # constitutional integrity (EPIC-008 strengthening)
    "INTEGRITY_REPORT_FORMAT",
    "INTEGRITY_EVIDENCE_FORMAT",
    "CertificationRegister",
    "verify_certification_integrity",
    "enforce_integrity",
    "IntegrityFinding",
    "IntegrityReport",
    "IntegrityEvidence",
    "build_integrity_evidence",
    "DuplicateCertificationError",
    "ConstitutionalIntegrityError",
    # ledger
    "CertificationLedger",
    "CertificationLedgerEntry",
    "GENESIS_HASH",
    # closure
    "ProgramClosureReport",
    "AcceptanceEntry",
    "build_program_closure",
    "certification_framework_status",
    "PROGRAM_NAME",
    "EC1_EPICS",
    "CERTIFICATION_ACCEPTANCE_ID",
    # errors
    "CertificationLayerError",
    "CertificationSubjectError",
    "CertificationIntegrityError",
    "LedgerIntegrityError",
    "ProgramClosureError",
]
