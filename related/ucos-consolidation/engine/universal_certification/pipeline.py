"""UCOS-EPIC-006 — Certification Pipeline (Terminal T6).

The **Certification Pipeline** is the end-to-end orchestration of the Universal
Certification Engine: it runs the canonical stages in order —

    subject → compliance + rules (engine) → certificate → evidence → approval → audit

— gating at each stage and producing a single immutable :class:`CertificationOutcome`.
It is deterministic (IMP-007 §5) and fail-closed (OP-CERT-001): a **NOT-CERTIFIED**
decision is never submitted for approval and can never be approved, and every material
event is recorded on the append-only, hash-chained
:class:`~engine.universal_certification.audit.CertificationAuditLedger`.

The pipeline **records only** — it re-judges nothing (TP-01), mutates no subject, and
never writes to the certified corpus (DP-03). An identical subject processed by an
identical pipeline configuration yields a byte-identical outcome (certificate hash,
evidence hash, approval chain, and audit chain).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.universal_certification.approval import ApprovalWorkflow
from engine.universal_certification.audit import AuditEventType, CertificationAuditLedger
from engine.universal_certification.contracts import (
    Certificate,
    CertificationStatus,
    UniversalCertificationSubject,
)
from engine.universal_certification.engine import (
    CertificationDecision,
    UniversalCertificationEngine,
)
from engine.universal_certification.evidence import (
    CertificationEvidence,
    build_certification_evidence,
)

_logger = get_logger("universal_certification.pipeline")

#: The default submitter identity when the caller supplies none.
DEFAULT_SUBMITTER = "ucos-certification-pipeline"


@dataclass(frozen=True, slots=True)
class CertificationOutcome:
    """The immutable, end-to-end outcome of a certification pipeline run."""

    decision: CertificationDecision
    certificate: Certificate
    evidence: CertificationEvidence
    approval: ApprovalWorkflow
    audit_entries: tuple[dict[str, Any], ...]

    @property
    def certified(self) -> bool:
        return self.decision.certified

    @property
    def approved(self) -> bool:
        return self.approval.approved

    @property
    def certification_id(self) -> str:
        return self.certificate.certification_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "certified": self.certified,
            "approved": self.approved,
            "decision": self.decision.to_dict(),
            "evidence": self.evidence.to_dict(),
            "approval": self.approval.to_dict(),
            "audit_entries": [dict(e) for e in self.audit_entries],
        }


class CertificationPipeline:
    """Orchestrates the universal certification stages onto a shared audit ledger."""

    __slots__ = ("_engine", "_audit")

    def __init__(
        self,
        engine: UniversalCertificationEngine | None = None,
        *,
        audit: CertificationAuditLedger | None = None,
    ) -> None:
        self._engine = engine if engine is not None else UniversalCertificationEngine()
        self._audit = audit if audit is not None else CertificationAuditLedger()

    @property
    def engine(self) -> UniversalCertificationEngine:
        return self._engine

    @property
    def audit(self) -> CertificationAuditLedger:
        return self._audit

    def run(
        self,
        subject: UniversalCertificationSubject,
        *,
        approver: str | None = None,
        rationale: str = "",
        submitter: str = DEFAULT_SUBMITTER,
        auto_submit: bool = True,
    ) -> CertificationOutcome:
        """Certify ``subject`` end to end, gating approval on a certified decision.

        A CERTIFIED decision is submitted for approval (when ``auto_submit``) and, if an
        ``approver`` is supplied, approved. A NOT-CERTIFIED decision is never submitted
        and never approved (fail-closed). Every stage is recorded on the audit ledger.
        """
        with trace("universal_certification.pipeline", target=subject.target_id):
            decision = self._engine.certify(subject)
            certificate = decision.certificate
            cert_sha = certificate.content_sha256

            self._audit.record(
                AuditEventType.CERTIFIED if decision.certified else AuditEventType.NOT_CERTIFIED,
                certification_id=certificate.certification_id,
                certificate_sha256=cert_sha,
                status=decision.status.value,
                blocking_failures=list(decision.blocking_failures),
            )
            self._audit.record(
                AuditEventType.CERTIFICATE_ISSUED,
                certification_id=certificate.certification_id,
                certificate_sha256=cert_sha,
                target_id=decision.target_id,
                version=decision.version,
            )

            evidence = build_certification_evidence(decision)
            self._audit.record(
                AuditEventType.EVIDENCE_RECORDED,
                certification_id=certificate.certification_id,
                certificate_sha256=cert_sha,
                evidence_sha256=evidence.content_sha256(),
            )

            workflow = ApprovalWorkflow(decision)
            if decision.status is CertificationStatus.CERTIFIED and auto_submit:
                workflow.submit(actor=approver or submitter, rationale=rationale)
                self._audit.record(
                    AuditEventType.APPROVAL_SUBMITTED,
                    certification_id=certificate.certification_id,
                    certificate_sha256=cert_sha,
                    submitter=approver or submitter,
                )
                if approver is not None:
                    workflow.approve(actor=approver, rationale=rationale)
                    self._audit.record(
                        AuditEventType.APPROVED,
                        certification_id=certificate.certification_id,
                        certificate_sha256=cert_sha,
                        approver=approver,
                    )

            outcome = CertificationOutcome(
                decision=decision,
                certificate=certificate,
                evidence=evidence,
                approval=workflow,
                audit_entries=tuple(
                    e.to_dict() for e in self._audit.events_for(certificate.certification_id)
                ),
            )
        _logger.info(
            "universal_certification.pipeline.completed",
            certification_id=certificate.certification_id,
            certified=decision.certified,
            approved=workflow.approved,
        )
        return outcome


__all__ = [
    "DEFAULT_SUBMITTER",
    "CertificationOutcome",
    "CertificationPipeline",
]
