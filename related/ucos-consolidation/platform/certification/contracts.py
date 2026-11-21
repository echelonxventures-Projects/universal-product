"""EC2-TASK-000153 — Certification Console Contracts (EC2-EPIC-011).

The versioned contract surface for the UCOS Platform **Certification Console & Ledger
Runtime** (L3 Application of the Program architecture, §4) plus the immutable **core
vocabulary**, the **descriptive record metadata**, and the **read-only view value types**
every certification-console service speaks. It reuses the certified EC-1 contract
machinery through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and binds console authorization to
the single §3.2 :class:`~platform.identity.contracts.CapabilityGroup`
``certification-ledger`` (PC-10, matrix index 11) that **already physically exists** in
the certified Identity Layer. EC2-EPIC-011 introduces **no new capability group, no new
authority, and no new authorization logic**.

It also **reuses — rather than reinventing** — the certified EC-1 Certification Layer
vocabulary: the recorded :class:`~engine.certification.contracts.CertificationStatus`,
:class:`~engine.certification.contracts.CertificationClass`,
:class:`~engine.certification.contracts.CriterionSeverity`, and
:class:`~engine.certification.contracts.CriterionStatus` are the frozen engine members
(re-exported, never redefined), and every surfaced datum is a faithful projection of a
:class:`~engine.certification.engine.CertificationDecision`,
:class:`~engine.certification.contracts.CertificationRecord`, and
:class:`~engine.certification.evidence.CertificationEvidence` produced by the certified
engine. The console **records** these read-only; it computes no verdict of its own
(TP-01).

Vocabulary:
    * :class:`CertificationAction` — the governed (read-only) console verbs, each mapped
      to the coarse RBAC :class:`~platform.foundation.identity.Permission` it requires
      (all :data:`Permission.READ`).
    * :class:`CertificationRecordMetadata` — immutable descriptive metadata for a record.
    * :class:`CriterionFindingView` / :class:`CertificationSummary` /
      :class:`CertificationEvidenceReference` / :class:`CertificationTrace` — immutable,
      serializable read projections of the certified engine outputs.
    * :class:`CertificationConsoleRecord` — an immutable, content-addressed console record
      binding a certified :class:`CertificationDecision` + record + evidence to the
      originating validation output (by reference), scoped to a tenant, carrying the
      surfacing owner.
    * :data:`CERTIFICATION_CONSOLE_CONTRACTS` — the published console service contracts.

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.certification.errors import CertificationContractError
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from typing import Any

from engine.certification.contracts import (
    CertificationClass,
    CertificationFinding,
    CertificationRecord,
    CertificationStatus,
    CriterionSeverity,
    CriterionStatus,
)
from engine.certification.engine import CertificationDecision
from engine.certification.evidence import CertificationEvidence
from engine.validation.contracts import ValidationReport
from engine.validation.evidence import ValidationEvidence

#: The semantic version of the Certification Console Runtime contract surface (AR-03/PL-05).
CERTIFICATION_CONSOLE_CONTRACT_VERSION = "1.0.0"

#: The §3.2 capability group authorizing every console action (reused; no new group).
CERTIFICATION_CONSOLE_GROUP = CapabilityGroup.CERTIFICATION_LEDGER

#: The certified EC-1 certification contract this console consumes by reference (L4).
ENGINE_CERTIFICATION_CONTRACT = "engine.certification.certify"

#: Re-exports of the frozen EC-1 certification vocabulary (recorded, never redefined).
ConsoleCertificationStatus = CertificationStatus
ConsoleCertificationClass = CertificationClass
ConsoleCriterionSeverity = CriterionSeverity
ConsoleCriterionStatus = CriterionStatus


class CertificationAction(str, Enum):
    """The governed (read-only) certification-console verbs.

    Every action requires only :data:`Permission.READ` on the ``certification-ledger``
    group — the console exposes no create/execute/administer authority and no mutation
    path to any certification datum or ledger entry (P7 alignment).
    """

    SURFACE = "surface"
    INSPECT = "inspect"
    VIEW_EVIDENCE = "view-evidence"
    VIEW_LEDGER = "view-ledger"
    SUMMARIZE = "summarize"
    DISCOVER = "discover"
    SEARCH = "search"
    TRACK = "track"
    TRACE = "trace"
    VIEW_LINEAGE = "view-lineage"
    VALIDATE_GOVERNANCE = "validate-governance"
    EVALUATE_READINESS = "evaluate-readiness"


#: The verb→permission map (Determination §7/§13). Every console verb is READ-only.
_ACTION_PERMISSIONS: dict[CertificationAction, Permission] = {
    action: Permission.READ for action in CertificationAction
}


def permission_for(action: CertificationAction) -> Permission:
    """Return the RBAC permission required by a console action (fail-closed)."""
    if not isinstance(action, CertificationAction):
        raise CertificationContractError("action must be a CertificationAction")
    return _ACTION_PERMISSIONS[action]


def all_certification_actions() -> tuple[CertificationAction, ...]:
    """Return every certification-console action in stable declaration order."""
    return tuple(CertificationAction)


# --------------------------------------------------------------------------- #
# Descriptive record metadata (value data only; carries no authority).        #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class CertificationRecordMetadata:
    """Immutable, content-addressed descriptive metadata for a certification record."""

    description: str = ""
    labels: frozenset[str] = field(default_factory=frozenset)
    annotations: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        description: str = "",
        labels: Iterable[str] | None = None,
        annotations: Mapping[str, str] | None = None,
    ) -> CertificationRecordMetadata:
        """Build normalized, validated metadata (deterministic)."""
        if not isinstance(description, str):
            raise CertificationContractError("certification record description must be a string")
        label_set = frozenset(_require_str(label, "label") for label in (labels or ()))
        annots = {
            _require_str(k, "annotation key"): _require_str(v, "annotation value")
            for k, v in dict(annotations or {}).items()
        }
        return cls(description=description, labels=label_set, annotations=annots)

    def has_label(self, label: str) -> bool:
        return label in self.labels

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "labels": sorted(self.labels),
            "annotations": {k: self.annotations[k] for k in sorted(self.annotations)},
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def _require_str(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value:
        raise CertificationContractError(f"certification record {what} must be a non-empty string")
    return value


#: The canonical empty metadata (shared default; immutable).
EMPTY_CERTIFICATION_METADATA = CertificationRecordMetadata()


# --------------------------------------------------------------------------- #
# Read-only view projections of the certified engine outputs.                 #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class CriterionFindingView:
    """An immutable read projection of a single certified :class:`CertificationFinding`."""

    criterion_id: str
    severity: str
    status: str
    passed: bool
    blocking_failure: bool
    message: str

    @classmethod
    def from_finding(cls, finding: CertificationFinding) -> CriterionFindingView:
        if not isinstance(finding, CertificationFinding):
            raise CertificationContractError("CriterionFindingView requires a CertificationFinding")
        return cls(
            criterion_id=finding.criterion_id,
            severity=finding.severity.value,
            status=finding.status.value,
            passed=finding.passed,
            blocking_failure=finding.is_blocking_failure,
            message=finding.message,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "severity": self.severity,
            "status": self.status,
            "passed": self.passed,
            "blocking_failure": self.blocking_failure,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class CertificationSummary:
    """An immutable summary projection of a certified :class:`CertificationDecision`."""

    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    status: str
    certified: bool
    certification_class: str
    total: int
    passed: int
    failed: int
    blocking_failed: int
    advisory_failed: int

    @classmethod
    def from_decision(cls, decision: CertificationDecision) -> CertificationSummary:
        if not isinstance(decision, CertificationDecision):
            raise CertificationContractError(
                "CertificationSummary requires a CertificationDecision"
            )
        counts = decision.counts()
        return cls(
            certification_id=decision.certification_id,
            target_id=decision.target_id,
            blueprint_id=decision.blueprint_id,
            version=decision.version,
            status=decision.status.value,
            certified=decision.certified,
            certification_class=decision.certification_class.value,
            total=counts["total"],
            passed=counts["passed"],
            failed=counts["failed"],
            blocking_failed=counts["blocking_failed"],
            advisory_failed=counts["advisory_failed"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "status": self.status,
            "certified": self.certified,
            "certification_class": self.certification_class,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "blocking_failed": self.blocking_failed,
            "advisory_failed": self.advisory_failed,
        }


@dataclass(frozen=True, slots=True)
class CertificationEvidenceReference:
    """An immutable, content-addressed reference to a certified :class:`CertificationEvidence`.

    Surfaces the evidence *by reference* — its format, status, criteria evaluated,
    blocking failures, the reference to the reproducible upstream validation evidence,
    the immutable record's content hash, and a fingerprint of the full evidence record —
    without mutating or re-deriving it (P6). The ``evidence_fingerprint`` is the content
    hash of the certified evidence document, so a rendered reference is verifiable against
    the engine output byte-for-byte.
    """

    certification_id: str
    target_id: str
    blueprint_id: str
    evidence_format: str
    status: str
    certified: bool
    criteria_evaluated: tuple[str, ...]
    blocking_failures: tuple[str, ...]
    validation_evidence_ref: str
    record_sha256: str
    evidence_fingerprint: str

    @classmethod
    def from_evidence(cls, evidence: CertificationEvidence) -> CertificationEvidenceReference:
        if not isinstance(evidence, CertificationEvidence):
            raise CertificationContractError(
                "CertificationEvidenceReference requires a CertificationEvidence"
            )
        payload = evidence.to_dict()
        return cls(
            certification_id=evidence.certification_id,
            target_id=evidence.target_id,
            blueprint_id=evidence.blueprint_id,
            evidence_format=payload["evidence_format"],
            status=evidence.status,
            certified=evidence.certified,
            criteria_evaluated=tuple(evidence.criteria_evaluated),
            blocking_failures=tuple(evidence.blocking_failures),
            validation_evidence_ref=evidence.validation_evidence_ref,
            record_sha256=evidence.record_sha256,
            evidence_fingerprint=content_hash(payload),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "evidence_format": self.evidence_format,
            "status": self.status,
            "certified": self.certified,
            "criteria_evaluated": list(self.criteria_evaluated),
            "blocking_failures": list(self.blocking_failures),
            "validation_evidence_ref": self.validation_evidence_ref,
            "record_sha256": self.record_sha256,
            "evidence_fingerprint": self.evidence_fingerprint,
        }


@dataclass(frozen=True, slots=True)
class CertificationTrace:
    """An immutable, content-addressed certification trace edge (Validation→Target→Certification).

    Continues the platform link chain through the certification node by reference: it
    binds the certified ``target_id`` and its ``blueprint_id`` (and ``version``) to the
    upstream validation verdict/acceptance it aggregates and the optional originating
    generation ``request_ref``, carrying the certified certification status. It records no
    synthetic linkage — every field is an explicit citation drawn from the certified
    decision/record.
    """

    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    status: str
    certified: bool
    validation_verdict: str
    validation_accepted: bool
    validation_evidence_ref: str
    request_ref: str | None
    trace_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        certification_id: str,
        target_id: str,
        blueprint_id: str,
        version: str,
        status: str,
        certified: bool,
        validation_verdict: str,
        validation_accepted: bool,
        validation_evidence_ref: str,
        request_ref: str | None = None,
    ) -> CertificationTrace:
        core = {
            "certification_id": certification_id,
            "target_id": target_id,
            "blueprint_id": blueprint_id,
            "version": version,
            "status": status,
            "certified": certified,
            "validation_verdict": validation_verdict,
            "validation_accepted": validation_accepted,
            "validation_evidence_ref": validation_evidence_ref,
            "request_ref": request_ref,
        }
        return cls(
            certification_id=certification_id,
            target_id=target_id,
            blueprint_id=blueprint_id,
            version=version,
            status=status,
            certified=certified,
            validation_verdict=validation_verdict,
            validation_accepted=validation_accepted,
            validation_evidence_ref=validation_evidence_ref,
            request_ref=request_ref,
            trace_id=f"UCOS-CTRC-{content_hash(core)[:16]}",
        )

    @property
    def is_traceable(self) -> bool:
        """True iff the backward edge (certification rooted at a validated target) is present."""
        return bool(
            self.certification_id
            and self.target_id
            and self.blueprint_id
            and self.validation_evidence_ref
        )

    def edge(self) -> dict[str, Any]:
        """The explicit Validation → Target → Certification trace edge (audit evidence)."""
        return {
            "trace_id": self.trace_id,
            "link": "certification-trace",
            "request": {"request_ref": self.request_ref},
            "validation": {
                "verdict": self.validation_verdict,
                "accepted": self.validation_accepted,
                "evidence_ref": self.validation_evidence_ref,
            },
            "target": {
                "target_id": self.target_id,
                "blueprint_id": self.blueprint_id,
                "version": self.version,
            },
            "certification": {
                "certification_id": self.certification_id,
                "status": self.status,
                "certified": self.certified,
            },
            "traceable": self.is_traceable,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "status": self.status,
            "certified": self.certified,
            "validation_verdict": self.validation_verdict,
            "validation_accepted": self.validation_accepted,
            "validation_evidence_ref": self.validation_evidence_ref,
            "request_ref": self.request_ref,
            "traceable": self.is_traceable,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- #
# The console record aggregate.                                               #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class CertificationConsoleRecord:
    """An immutable, content-addressed certification console record (a surfaced snapshot).

    Binds a certified :class:`CertificationDecision` + :class:`CertificationRecord` +
    :class:`CertificationEvidence` (all produced read-only by the certified engine over
    the upstream :class:`ValidationReport` + :class:`ValidationEvidence`) to an optional
    originating generation ``request_ref``, workspace/project (by reference), and a
    ``tenant`` isolation boundary, recording the surfacing ``owner_subject``. The
    ``record_id`` is content-addressed from the engine ``certification_id`` and the
    binding — so surfacing is idempotent and reproducible for an identical certification
    regardless of when it is surfaced (temporal ordering lives in the append-only ledger,
    the inspection log, and the governed event stream).
    """

    record_id: str
    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    report: ValidationReport
    validation_evidence: ValidationEvidence
    decision: CertificationDecision
    record: CertificationRecord
    certification_evidence: CertificationEvidence
    request_ref: str | None
    workspace_id: str | None
    project_id: str | None
    tenant: str | None
    owner_subject: str
    metadata: CertificationRecordMetadata

    @classmethod
    def create(
        cls,
        *,
        report: ValidationReport,
        validation_evidence: ValidationEvidence,
        decision: CertificationDecision,
        certification_evidence: CertificationEvidence,
        owner_subject: str,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: CertificationRecordMetadata | None = None,
    ) -> CertificationConsoleRecord:
        """Build a content-addressed console record (fail-closed; no re-derivation)."""
        if not isinstance(report, ValidationReport):
            raise CertificationContractError("record requires a ValidationReport")
        if not isinstance(validation_evidence, ValidationEvidence):
            raise CertificationContractError("record requires a ValidationEvidence")
        if not isinstance(decision, CertificationDecision):
            raise CertificationContractError("record requires a CertificationDecision")
        if not isinstance(certification_evidence, CertificationEvidence):
            raise CertificationContractError("record requires a CertificationEvidence")
        if not isinstance(owner_subject, str) or not owner_subject:
            raise CertificationContractError("record owner_subject is required")
        if decision.target_id != report.target_id:
            raise CertificationContractError(
                "record decision/report target mismatch",
                decision_target=decision.target_id,
                report_target=report.target_id,
            )
        for name, value in (
            ("request_ref", request_ref),
            ("workspace_id", workspace_id),
            ("project_id", project_id),
        ):
            if value is not None and (not isinstance(value, str) or not value):
                raise CertificationContractError(
                    f"record {name} must be a non-empty string when provided"
                )
        md = metadata if metadata is not None else EMPTY_CERTIFICATION_METADATA
        if not isinstance(md, CertificationRecordMetadata):
            raise CertificationContractError(
                "record metadata must be a CertificationRecordMetadata"
            )
        identity = {
            "certification_id": decision.certification_id,
            "request_ref": request_ref,
            "workspace_id": workspace_id,
            "project_id": project_id,
            "tenant": tenant,
            "owner_subject": owner_subject,
        }
        return cls(
            record_id=f"UCOS-CREC-{content_hash(identity)[:16]}",
            certification_id=decision.certification_id,
            target_id=decision.target_id,
            blueprint_id=decision.blueprint_id,
            version=decision.version,
            report=report,
            validation_evidence=validation_evidence,
            decision=decision,
            record=decision.record,
            certification_evidence=certification_evidence,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            owner_subject=owner_subject,
            metadata=md,
        )

    @property
    def certified(self) -> bool:
        """True iff the certified decision certified the target."""
        return self.record.certified

    def record_fingerprint(self) -> str:
        """The content hash of the certified certification record (fidelity anchor)."""
        return self.record.content_sha256

    def summary(self) -> CertificationSummary:
        return CertificationSummary.from_decision(self.decision)

    def evidence_reference(self) -> CertificationEvidenceReference:
        return CertificationEvidenceReference.from_evidence(self.certification_evidence)

    def criterion_views(self) -> tuple[CriterionFindingView, ...]:
        return tuple(CriterionFindingView.from_finding(f) for f in self.decision.findings)

    def trace(self) -> CertificationTrace:
        return CertificationTrace.create(
            certification_id=self.certification_id,
            target_id=self.target_id,
            blueprint_id=self.blueprint_id,
            version=self.version,
            status=self.record.status.value,
            certified=self.certified,
            validation_verdict=self.report.verdict.value,
            validation_accepted=self.report.accepted,
            validation_evidence_ref=self.record.evidence_ref,
            request_ref=self.request_ref,
        )

    def with_metadata(self, metadata: CertificationRecordMetadata) -> CertificationConsoleRecord:
        """Return an immutable copy carrying ``metadata`` (the id is preserved)."""
        if not isinstance(metadata, CertificationRecordMetadata):
            raise CertificationContractError(
                "record metadata must be a CertificationRecordMetadata"
            )
        return CertificationConsoleRecord(
            record_id=self.record_id,
            certification_id=self.certification_id,
            target_id=self.target_id,
            blueprint_id=self.blueprint_id,
            version=self.version,
            report=self.report,
            validation_evidence=self.validation_evidence,
            decision=self.decision,
            record=self.record,
            certification_evidence=self.certification_evidence,
            request_ref=self.request_ref,
            workspace_id=self.workspace_id,
            project_id=self.project_id,
            tenant=self.tenant,
            owner_subject=self.owner_subject,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "report": self.report.to_dict(),
            "validation_evidence": self.validation_evidence.to_dict(),
            "decision": self.decision.to_dict(),
            "record": self.record.to_dict(),
            "certification_evidence": self.certification_evidence.to_dict(),
            "request_ref": self.request_ref,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "tenant": self.tenant,
            "owner_subject": self.owner_subject,
            "metadata": self.metadata.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- #
# The published certification-console contract surface (L3).                  #
# --------------------------------------------------------------------------- #

#: The console service contract identities the Certification Console Runtime publishes.
#: Each maps to an EC2-EPIC-011 deliverable; consumers bind to these by reference (PL-05).
_CERTIFICATION_CONSOLE_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("certification.registry.records", "Record registry — surface/register/resolve/discover."),
    ("certification.facade.surface", "Facade — read-only engine.certification reproduction (P6)."),
    ("certification.evidence.view", "Evidence — faithful evidence reference (by reference)."),
    ("certification.ledger.navigate", "Ledger — append-only hash-chained ledger navigation."),
    ("certification.lineage.inspect", "Lineage — parent-child / ancestry inspection."),
    ("certification.status.derive", "Status — deterministic derived certification posture."),
    ("certification.readiness.evaluate", "Readiness — deterministic completeness evaluation."),
    ("certification.governance.validate", "Governance — compliance evaluation + violations."),
    ("certification.search.query", "Certification search — authorization + isolation scoped."),
    ("certification.trace.navigate", "Trace — Validation→Target→Certification continuation."),
    ("certification.runtime.service", "Console runtime — the L3 access + context decision point."),
)

#: Immutable references to the published certification-console contracts (name + version).
CERTIFICATION_CONSOLE_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, CERTIFICATION_CONSOLE_CONTRACT_VERSION)
    for name, _ in _CERTIFICATION_CONSOLE_CONTRACT_NAMES
)


def certification_console_contract(name: str, description: str = "") -> Contract:
    """Build a versioned console :class:`Contract` at the console contract version."""
    if not isinstance(name, str) or not name:
        raise CertificationContractError("certification console contract name is required")
    try:
        return platform_contract(name, CERTIFICATION_CONSOLE_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise CertificationContractError(str(exc), name=name) from exc


def default_certification_console_contracts() -> tuple[Contract, ...]:
    """The published console contracts as concrete :class:`Contract` objects."""
    return tuple(
        certification_console_contract(name, description)
        for name, description in _CERTIFICATION_CONSOLE_CONTRACT_NAMES
    )


__all__ = [
    "CERTIFICATION_CONSOLE_CONTRACT_VERSION",
    "CERTIFICATION_CONSOLE_GROUP",
    "ENGINE_CERTIFICATION_CONTRACT",
    "CertificationStatus",
    "CertificationClass",
    "CriterionSeverity",
    "CriterionStatus",
    "ConsoleCertificationStatus",
    "ConsoleCertificationClass",
    "ConsoleCriterionSeverity",
    "ConsoleCriterionStatus",
    "CertificationAction",
    "permission_for",
    "all_certification_actions",
    "CertificationRecordMetadata",
    "EMPTY_CERTIFICATION_METADATA",
    "CriterionFindingView",
    "CertificationSummary",
    "CertificationEvidenceReference",
    "CertificationTrace",
    "CertificationConsoleRecord",
    "CERTIFICATION_CONSOLE_CONTRACTS",
    "certification_console_contract",
    "default_certification_console_contracts",
]
