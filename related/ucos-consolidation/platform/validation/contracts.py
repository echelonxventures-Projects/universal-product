"""EC2-TASK-000145 — Validation Console Contracts (EC2-EPIC-010).

The versioned contract surface for the UCOS Platform **Validation Console Runtime**
(L3 Application of the Program architecture, §4) plus the immutable **core vocabulary**
and the **read-only view value types** every validation-console service speaks. It
reuses the certified EC-1 contract machinery through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and binds console authorization to
the single §3.2 :class:`~platform.identity.contracts.CapabilityGroup`
``validation-explorer`` (PC-09, matrix index 10) that **already physically exists** in
the certified Identity Layer. EC2-EPIC-010 introduces **no new capability group, no new
authority, and no new authorization logic**.

It also **reuses — rather than reinventing** — the certified EC-1 Validation Layer
vocabulary: the recorded :class:`~engine.validation.contracts.Verdict`,
:class:`~engine.validation.contracts.Severity`, and
:class:`~engine.validation.contracts.CheckStatus` are the frozen engine members
(re-exported, never redefined), and every surfaced datum is a faithful projection of an
:class:`~engine.validation.contracts.ValidationReport`,
:class:`~engine.validation.evidence.ValidationEvidence`, and
:class:`~engine.validation.gates.AcceptanceDecision` produced by the certified engine.
The console **records** these read-only; it computes no verdict of its own (TP-01).

Vocabulary:
    * :class:`ValidationAction` — the governed (read-only) console verbs, each mapped to
      the coarse RBAC :class:`~platform.foundation.identity.Permission` it requires (all
      :data:`Permission.READ`).
    * :class:`FindingView` / :class:`ValidationSummary` / :class:`ValidationDecisionView`
      / :class:`ValidationEvidenceReference` / :class:`ValidationTrace` — immutable,
      serializable read projections of the certified engine outputs.
    * :class:`ValidationRecord` — an immutable, content-addressed console record binding
      a certified :class:`ValidationReport` + evidence + decision + subject to an
      optional generation request / workspace / project **by reference**, scoped to a
      tenant, carrying the surfacing owner and a logical tick.
    * :data:`VALIDATION_CONSOLE_CONTRACTS` — the published console service contracts
      consumers (EPIC-011 certification console, later presentation) bind to by
      reference (PL-05, versioned).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.validation.errors import ValidationContractError
from platform.validation.metadata import EMPTY_VALIDATION_METADATA, ValidationRecordMetadata
from typing import Any

from engine.validation.contracts import (
    CheckStatus,
    Severity,
    ValidationFinding,
    ValidationReport,
    ValidationSubject,
    Verdict,
)
from engine.validation.evidence import ValidationEvidence
from engine.validation.gates import AcceptanceDecision

#: The semantic version of the Validation Console Runtime contract surface (AR-03/PL-05).
VALIDATION_CONSOLE_CONTRACT_VERSION = "1.0.0"

#: The §3.2 capability group authorizing every console action (reused; no new group).
VALIDATION_CONSOLE_GROUP = CapabilityGroup.VALIDATION_EXPLORER

#: The certified EC-1 validation contract this console consumes by reference (L4).
ENGINE_VALIDATION_CONTRACT = "engine.validation.validate"

#: Re-exports of the frozen EC-1 validation vocabulary (recorded, never redefined).
ConsoleVerdict = Verdict
ConsoleSeverity = Severity
ConsoleCheckStatus = CheckStatus


class ValidationAction(str, Enum):
    """The governed (read-only) validation-console verbs.

    Every action requires only :data:`Permission.READ` on the ``validation-explorer``
    group — the console exposes no create/execute/administer authority and no mutation
    path to any validation datum (P7 alignment).
    """

    SURFACE = "surface"
    INSPECT = "inspect"
    VIEW_EVIDENCE = "view-evidence"
    VIEW_DECISION = "view-decision"
    SUMMARIZE = "summarize"
    DISCOVER = "discover"
    SEARCH = "search"
    TRACK = "track"
    TRACE = "trace"


#: The verb→permission map (Determination §7/§13). Every console verb is READ-only.
_ACTION_PERMISSIONS: dict[ValidationAction, Permission] = {
    action: Permission.READ for action in ValidationAction
}


def permission_for(action: ValidationAction) -> Permission:
    """Return the RBAC permission required by a console action (fail-closed)."""
    if not isinstance(action, ValidationAction):
        raise ValidationContractError("action must be a ValidationAction")
    return _ACTION_PERMISSIONS[action]


def all_validation_actions() -> tuple[ValidationAction, ...]:
    """Return every validation-console action in stable declaration order."""
    return tuple(ValidationAction)


# --------------------------------------------------------------------------- #
# Read-only view projections of the certified engine outputs.                 #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class FindingView:
    """An immutable read projection of a single certified :class:`ValidationFinding`."""

    check_id: str
    severity: str
    status: str
    passed: bool
    blocking_failure: bool
    message: str

    @classmethod
    def from_finding(cls, finding: ValidationFinding) -> FindingView:
        if not isinstance(finding, ValidationFinding):
            raise ValidationContractError("FindingView requires a ValidationFinding")
        return cls(
            check_id=finding.check_id,
            severity=finding.severity.value,
            status=finding.status.value,
            passed=finding.passed,
            blocking_failure=finding.is_blocking_failure,
            message=finding.message,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "severity": self.severity,
            "status": self.status,
            "passed": self.passed,
            "blocking_failure": self.blocking_failure,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class ValidationSummary:
    """An immutable summary projection of a certified :class:`ValidationReport`."""

    target_id: str
    blueprint_id: str
    verdict: str
    accepted: bool
    total: int
    passed: int
    failed: int
    blocking_failed: int
    advisory_failed: int

    @classmethod
    def from_report(cls, report: ValidationReport) -> ValidationSummary:
        if not isinstance(report, ValidationReport):
            raise ValidationContractError("ValidationSummary requires a ValidationReport")
        counts = report.counts()
        return cls(
            target_id=report.target_id,
            blueprint_id=report.blueprint_id,
            verdict=report.verdict.value,
            accepted=report.accepted,
            total=counts["total"],
            passed=counts["passed"],
            failed=counts["failed"],
            blocking_failed=counts["blocking_failed"],
            advisory_failed=counts["advisory_failed"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "verdict": self.verdict,
            "accepted": self.accepted,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "blocking_failed": self.blocking_failed,
            "advisory_failed": self.advisory_failed,
        }


@dataclass(frozen=True, slots=True)
class ValidationDecisionView:
    """An immutable read projection of a certified :class:`AcceptanceDecision`."""

    target_id: str
    blueprint_id: str
    accepted: bool
    verdict: str
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]

    @classmethod
    def from_decision(cls, decision: AcceptanceDecision) -> ValidationDecisionView:
        if not isinstance(decision, AcceptanceDecision):
            raise ValidationContractError("ValidationDecisionView requires an AcceptanceDecision")
        return cls(
            target_id=decision.target_id,
            blueprint_id=decision.blueprint_id,
            accepted=decision.accepted,
            verdict=decision.verdict,
            blocking_failures=tuple(decision.blocking_failures),
            advisory_failures=tuple(decision.advisory_failures),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "accepted": self.accepted,
            "verdict": self.verdict,
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
        }


@dataclass(frozen=True, slots=True)
class ValidationEvidenceReference:
    """An immutable, content-addressed reference to a certified :class:`ValidationEvidence`.

    Surfaces the evidence *by reference* — its format, verdict, checks run, blocking
    failures, and a fingerprint of the full evidence record — without mutating or
    re-deriving it (P6). The ``evidence_fingerprint`` is the content hash of the
    certified evidence document, so a rendered reference is verifiable against the engine
    output byte-for-byte.
    """

    target_id: str
    blueprint_id: str
    evidence_format: str
    verdict: str
    accepted: bool
    checks_run: tuple[str, ...]
    blocking_failures: tuple[str, ...]
    evidence_fingerprint: str

    @classmethod
    def from_evidence(cls, evidence: ValidationEvidence) -> ValidationEvidenceReference:
        if not isinstance(evidence, ValidationEvidence):
            raise ValidationContractError(
                "ValidationEvidenceReference requires a ValidationEvidence"
            )
        return cls(
            target_id=evidence.target_id,
            blueprint_id=evidence.blueprint_id,
            evidence_format=evidence.to_dict()["evidence_format"],
            verdict=evidence.verdict,
            accepted=evidence.accepted,
            checks_run=tuple(evidence.checks_run),
            blocking_failures=tuple(evidence.blocking_failures),
            evidence_fingerprint=content_hash(evidence.to_dict()),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "evidence_format": self.evidence_format,
            "verdict": self.verdict,
            "accepted": self.accepted,
            "checks_run": list(self.checks_run),
            "blocking_failures": list(self.blocking_failures),
            "evidence_fingerprint": self.evidence_fingerprint,
        }


@dataclass(frozen=True, slots=True)
class ValidationTrace:
    """An immutable, content-addressed validation trace edge (Request → Target → Validation).

    Continues the platform link chain through the validation node by reference: it binds
    the validated ``target_id`` and its ``blueprint_id`` (and the engine
    ``provenance_chain`` rooted at the blueprint) to the optional originating generation
    ``request_ref``, carrying the certified verdict/acceptance. It records no synthetic
    linkage — every field is an explicit citation drawn from the certified report/subject.
    """

    target_id: str
    blueprint_id: str
    verdict: str
    accepted: bool
    provenance_chain: tuple[str, ...]
    request_ref: str | None
    trace_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        target_id: str,
        blueprint_id: str,
        verdict: str,
        accepted: bool,
        provenance_chain: tuple[str, ...],
        request_ref: str | None = None,
    ) -> ValidationTrace:
        core = {
            "target_id": target_id,
            "blueprint_id": blueprint_id,
            "verdict": verdict,
            "accepted": accepted,
            "provenance_chain": list(provenance_chain),
            "request_ref": request_ref,
        }
        return cls(
            target_id=target_id,
            blueprint_id=blueprint_id,
            verdict=verdict,
            accepted=accepted,
            provenance_chain=provenance_chain,
            request_ref=request_ref,
            trace_id=f"UCOS-VTRC-{content_hash(core)[:16]}",
        )

    @property
    def is_traceable(self) -> bool:
        """True iff the backward edge (target rooted at its blueprint) is present."""
        return bool(
            self.target_id
            and self.blueprint_id
            and self.provenance_chain
            and self.provenance_chain[0] == self.blueprint_id
        )

    def edge(self) -> dict[str, Any]:
        """The explicit Request → Target → Validation trace edge (audit evidence)."""
        return {
            "trace_id": self.trace_id,
            "link": "validation-trace",
            "request": {"request_ref": self.request_ref},
            "target": {
                "target_id": self.target_id,
                "blueprint_id": self.blueprint_id,
                "provenance_chain": list(self.provenance_chain),
            },
            "validation": {"verdict": self.verdict, "accepted": self.accepted},
            "traceable": self.is_traceable,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "verdict": self.verdict,
            "accepted": self.accepted,
            "provenance_chain": list(self.provenance_chain),
            "request_ref": self.request_ref,
            "traceable": self.is_traceable,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- #
# The console record aggregate.                                               #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ValidationRecord:
    """An immutable, content-addressed validation console record (a surfaced snapshot).

    Binds a certified :class:`ValidationReport` + :class:`ValidationEvidence` +
    :class:`AcceptanceDecision` (all produced read-only by the certified engine over the
    stored :class:`ValidationSubject`) to an optional originating generation
    ``request_ref``, workspace/project (by reference), and a ``tenant`` isolation
    boundary, recording the surfacing ``owner_subject``. The ``record_id`` is
    content-addressed from the target, the report fingerprint, and the binding — so
    surfacing is idempotent and reproducible for an identical validation regardless of
    when it is surfaced (temporal ordering lives in the append-only inspection log and
    the governed event stream).
    """

    record_id: str
    target_id: str
    blueprint_id: str
    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision
    subject: ValidationSubject
    request_ref: str | None
    workspace_id: str | None
    project_id: str | None
    tenant: str | None
    owner_subject: str
    metadata: ValidationRecordMetadata

    @classmethod
    def create(
        cls,
        *,
        report: ValidationReport,
        evidence: ValidationEvidence,
        decision: AcceptanceDecision,
        subject: ValidationSubject,
        owner_subject: str,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: ValidationRecordMetadata | None = None,
    ) -> ValidationRecord:
        """Build a content-addressed console record (fail-closed; no re-derivation)."""
        if not isinstance(report, ValidationReport):
            raise ValidationContractError("record requires a ValidationReport")
        if not isinstance(evidence, ValidationEvidence):
            raise ValidationContractError("record requires a ValidationEvidence")
        if not isinstance(decision, AcceptanceDecision):
            raise ValidationContractError("record requires an AcceptanceDecision")
        if not isinstance(subject, ValidationSubject):
            raise ValidationContractError("record requires a ValidationSubject")
        if not isinstance(owner_subject, str) or not owner_subject:
            raise ValidationContractError("record owner_subject is required")
        if report.target_id != subject.target_id:
            raise ValidationContractError(
                "record report/subject target mismatch",
                report_target=report.target_id,
                subject_target=subject.target_id,
            )
        for name, value in (
            ("request_ref", request_ref),
            ("workspace_id", workspace_id),
            ("project_id", project_id),
        ):
            if value is not None and (not isinstance(value, str) or not value):
                raise ValidationContractError(
                    f"record {name} must be a non-empty string when provided"
                )
        md = metadata if metadata is not None else EMPTY_VALIDATION_METADATA
        if not isinstance(md, ValidationRecordMetadata):
            raise ValidationContractError("record metadata must be a ValidationRecordMetadata")
        identity = {
            "target_id": report.target_id,
            "report_fingerprint": content_hash(report.to_dict()),
            "request_ref": request_ref,
            "workspace_id": workspace_id,
            "project_id": project_id,
            "tenant": tenant,
            "owner_subject": owner_subject,
        }
        return cls(
            record_id=f"UCOS-VREP-{content_hash(identity)[:16]}",
            target_id=report.target_id,
            blueprint_id=report.blueprint_id,
            report=report,
            evidence=evidence,
            decision=decision,
            subject=subject,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            owner_subject=owner_subject,
            metadata=md,
        )

    @property
    def accepted(self) -> bool:
        """True iff the certified report accepted the target."""
        return self.report.accepted

    def report_fingerprint(self) -> str:
        """The content hash of the certified report (fidelity anchor)."""
        return content_hash(self.report.to_dict())

    def summary(self) -> ValidationSummary:
        return ValidationSummary.from_report(self.report)

    def decision_view(self) -> ValidationDecisionView:
        return ValidationDecisionView.from_decision(self.decision)

    def evidence_reference(self) -> ValidationEvidenceReference:
        return ValidationEvidenceReference.from_evidence(self.evidence)

    def finding_views(self) -> tuple[FindingView, ...]:
        return tuple(FindingView.from_finding(f) for f in self.report.findings)

    def trace(self) -> ValidationTrace:
        return ValidationTrace.create(
            target_id=self.target_id,
            blueprint_id=self.blueprint_id,
            verdict=self.report.verdict.value,
            accepted=self.report.accepted,
            provenance_chain=tuple(self.subject.provenance_chain),
            request_ref=self.request_ref,
        )

    def with_metadata(self, metadata: ValidationRecordMetadata) -> ValidationRecord:
        """Return an immutable copy carrying ``metadata`` (the id is preserved)."""
        if not isinstance(metadata, ValidationRecordMetadata):
            raise ValidationContractError("record metadata must be a ValidationRecordMetadata")
        return ValidationRecord(
            record_id=self.record_id,
            target_id=self.target_id,
            blueprint_id=self.blueprint_id,
            report=self.report,
            evidence=self.evidence,
            decision=self.decision,
            subject=self.subject,
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
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "report": self.report.to_dict(),
            "evidence": self.evidence.to_dict(),
            "decision": self.decision.to_dict(),
            "subject": self.subject.to_dict(),
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
# The published validation-console contract surface (L3).                     #
# --------------------------------------------------------------------------- #

#: The console service contract identities the Validation Console Runtime publishes.
#: Each maps to an EC2-EPIC-010 deliverable; consumers bind to these by reference (PL-05).
_VALIDATION_CONSOLE_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("validation.registry.records", "Record registry — surface/register/resolve/discover."),
    ("validation.facade.surface", "Facade — read-only engine.validation reproduction (P6)."),
    ("validation.evidence.view", "Evidence — faithful evidence reference (by reference)."),
    ("validation.decision.view", "Decision — faithful acceptance-decision view."),
    ("validation.status.derive", "Status — deterministic derived validation posture."),
    ("validation.search.query", "Validation search — authorization + isolation scoped."),
    ("validation.trace.navigate", "Trace — Request→Target→Validation link continuation."),
    ("validation.runtime.service", "Console runtime — the L3 access + context decision point."),
)

#: Immutable references to the published validation-console contracts (name + version).
VALIDATION_CONSOLE_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, VALIDATION_CONSOLE_CONTRACT_VERSION)
    for name, _ in _VALIDATION_CONSOLE_CONTRACT_NAMES
)


def validation_console_contract(name: str, description: str = "") -> Contract:
    """Build a versioned console :class:`Contract` at the console contract version."""
    if not isinstance(name, str) or not name:
        raise ValidationContractError("validation console contract name is required")
    try:
        return platform_contract(name, VALIDATION_CONSOLE_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise ValidationContractError(str(exc), name=name) from exc


def default_validation_console_contracts() -> tuple[Contract, ...]:
    """The published console contracts as concrete :class:`Contract` objects."""
    return tuple(
        validation_console_contract(name, description)
        for name, description in _VALIDATION_CONSOLE_CONTRACT_NAMES
    )


__all__ = [
    "VALIDATION_CONSOLE_CONTRACT_VERSION",
    "VALIDATION_CONSOLE_GROUP",
    "ENGINE_VALIDATION_CONTRACT",
    "Verdict",
    "Severity",
    "CheckStatus",
    "ConsoleVerdict",
    "ConsoleSeverity",
    "ConsoleCheckStatus",
    "ValidationAction",
    "permission_for",
    "all_validation_actions",
    "FindingView",
    "ValidationSummary",
    "ValidationDecisionView",
    "ValidationEvidenceReference",
    "ValidationTrace",
    "ValidationRecord",
    "VALIDATION_CONSOLE_CONTRACTS",
    "validation_console_contract",
    "default_validation_console_contracts",
]
