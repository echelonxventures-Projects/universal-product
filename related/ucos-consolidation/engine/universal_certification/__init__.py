"""UCOS-EPIC-006 — Universal Certification Engine (Terminal T6).

The **Universal Certification Engine** is an additive, record-only certifier that
consumes three normalized inputs — **Validation**, **Measurement**, and **Repository
Truth** — and aggregates them into:

    * a **Compliance Report** (the Compliance Engine, fail-closed conformance frames),
    * a fail-closed **Certification Decision** (CERTIFIED / NOT-CERTIFIED) over a suite
      of open **Certification Rules**,
    * an **immutable, content-addressed Certificate**,
    * a **Certification Evidence** record referencing every consumed evidence,
    * a governed, hash-chained **Approval Workflow** (certify-before-promote), and
    * an append-only, hash-chained **Certification Audit Ledger**.

The **Certification Pipeline** orchestrates these stages end to end into a single
:class:`CertificationOutcome`.

The engine is *universal* — it depends on no single producer: any source that can
supply a :class:`ValidationInput`, a :class:`MeasurementInput`, and a
:class:`RepositoryTruthInput` can be certified. It is *sound* (it aggregates upstream
verdicts, inventing none — TP-01), *deterministic* (IMP-007 §5 — identical inputs
yield a byte-identical certificate, evidence, approval chain, and audit chain),
*fail-closed* (OP-CERT-001 — a not-certified decision can never be approved), *record
-only* (never writes to the certified corpus — DP-03), and *non-constitutive*
(``ENGINEERING-EXECUTION-ONLY``; it carries the EC-1 provisional-state disclosure and
asserts no constitutional finality — DE-05 / IP-01).
"""

from __future__ import annotations

from engine.universal_certification.approval import (
    GENESIS_HASH as APPROVAL_GENESIS_HASH,
)
from engine.universal_certification.approval import (
    ApprovalAction,
    ApprovalRecord,
    ApprovalState,
    ApprovalWorkflow,
)
from engine.universal_certification.audit import (
    GENESIS_HASH as AUDIT_GENESIS_HASH,
)
from engine.universal_certification.audit import (
    AuditEntry,
    AuditEventType,
    CertificationAuditLedger,
)
from engine.universal_certification.compliance import (
    COMPLIANCE_REPORT_FORMAT,
    ComplianceEngine,
    ComplianceFrame,
    ComplianceReport,
    DisclosureConformanceFrame,
    MeasurementConformanceFrame,
    RepositoryTruthConformanceFrame,
    ValidationConformanceFrame,
    ValidationEvidenceFrame,
    default_frames,
)
from engine.universal_certification.contracts import (
    DISCLOSURE_CHECK_ID,
    UCERT_AUTHORITY,
    UCERT_CONTRACT_VERSION,
    UCERT_STANDARD,
    UCERT_STANDARD_VERSION,
    Certificate,
    CertificationClass,
    CertificationStatus,
    ComplianceFinding,
    ComplianceStatus,
    Measurement,
    MeasurementComparator,
    MeasurementInput,
    RepositoryTruthInput,
    RuleFinding,
    RuleSeverity,
    RuleStatus,
    UniversalCertificationSubject,
    ValidationInput,
    canonical_json,
    content_hash,
)
from engine.universal_certification.engine import (
    CertificationDecision,
    UniversalCertificationEngine,
)
from engine.universal_certification.errors import (
    ApprovalWorkflowError,
    AuditIntegrityError,
    CertificateIntegrityError,
    CertificationInputError,
    CertificationPipelineError,
    CertificationRuleError,
    CertificationSubjectError,
    ComplianceEvaluationError,
    UniversalCertificationError,
)
from engine.universal_certification.evidence import (
    EVIDENCE_FORMAT,
    CertificationEvidence,
    build_certification_evidence,
)
from engine.universal_certification.pipeline import (
    DEFAULT_SUBMITTER,
    CertificationOutcome,
    CertificationPipeline,
)
from engine.universal_certification.rules import (
    CertificationRule,
    ComplianceConformantRule,
    DisclosurePresentRule,
    MeasurementCompleteRule,
    MeasurementsPresentRule,
    MeasurementsSatisfiedRule,
    RepositoryTruthConsistentRule,
    ValidationAcceptedRule,
    ValidationCompleteRule,
    ValidationEvidencePresentRule,
    VersionPinnedRule,
    default_rules,
)

__all__ = [
    # contracts
    "UCERT_CONTRACT_VERSION",
    "UCERT_STANDARD",
    "UCERT_STANDARD_VERSION",
    "UCERT_AUTHORITY",
    "DISCLOSURE_CHECK_ID",
    "canonical_json",
    "content_hash",
    "RuleSeverity",
    "RuleStatus",
    "CertificationStatus",
    "CertificationClass",
    "ComplianceStatus",
    "MeasurementComparator",
    "Measurement",
    "ValidationInput",
    "MeasurementInput",
    "RepositoryTruthInput",
    "UniversalCertificationSubject",
    "RuleFinding",
    "ComplianceFinding",
    "Certificate",
    # compliance engine
    "COMPLIANCE_REPORT_FORMAT",
    "ComplianceFrame",
    "ValidationConformanceFrame",
    "ValidationEvidenceFrame",
    "MeasurementConformanceFrame",
    "RepositoryTruthConformanceFrame",
    "DisclosureConformanceFrame",
    "default_frames",
    "ComplianceReport",
    "ComplianceEngine",
    # rules
    "CertificationRule",
    "ComplianceConformantRule",
    "ValidationAcceptedRule",
    "ValidationEvidencePresentRule",
    "MeasurementsPresentRule",
    "MeasurementsSatisfiedRule",
    "RepositoryTruthConsistentRule",
    "DisclosurePresentRule",
    "VersionPinnedRule",
    "MeasurementCompleteRule",
    "ValidationCompleteRule",
    "default_rules",
    # decision engine
    "CertificationDecision",
    "UniversalCertificationEngine",
    # evidence
    "EVIDENCE_FORMAT",
    "CertificationEvidence",
    "build_certification_evidence",
    # approval workflow
    "APPROVAL_GENESIS_HASH",
    "ApprovalState",
    "ApprovalAction",
    "ApprovalRecord",
    "ApprovalWorkflow",
    # audit
    "AUDIT_GENESIS_HASH",
    "AuditEventType",
    "AuditEntry",
    "CertificationAuditLedger",
    # pipeline
    "DEFAULT_SUBMITTER",
    "CertificationOutcome",
    "CertificationPipeline",
    # errors
    "UniversalCertificationError",
    "CertificationInputError",
    "CertificationSubjectError",
    "ComplianceEvaluationError",
    "CertificationRuleError",
    "CertificateIntegrityError",
    "ApprovalWorkflowError",
    "AuditIntegrityError",
    "CertificationPipelineError",
]
