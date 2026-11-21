"""UAPF-000001 — the Universal Policy Engine (constitutional governance of execution).

Nothing bypasses governance. A policy is a *declared obligation* and the verdict on it is
*derived*, so this engine adds no authority of its own: it holds no rule text, decides
nothing by opinion, and cannot approve something its declarations do not approve. Its own
authority is ``NONE (DERIVED TRUTH)``, the same disclosure every derived programme in this
repository carries.

Why a verdict is a value
------------------------
:class:`GovernanceVerdict` is an immutable, fingerprinted record rather than a boolean
return. A boolean cannot be audited: it says a submission was approved without saying
which obligations were considered, which were discharged, and which were waived as
advisory. The verdict carries all three, so approval is *evidence* and a later gate can
re-derive it and compare.

Obligations, discharged and undischarged
----------------------------------------
An obligation is discharged when its name appears in the submitted evidence with a truthy
value. That single rule covers every policy, which is why registering a policy needs no
evaluation code: a new obligation is a new key, not a new branch. Blocking policies fail a
submission; advisory ones only record a finding, so a measurement can be taken without
halting work.

Two policy scopes compose
-------------------------
Policies registered on the engine bind *every* subject (repository-wide governance);
policies declared by a pipeline bind that pipeline (local governance). Both are evaluated
by the same rule and the verdict names their origin, so a local declaration can never
weaken a repository-wide obligation — the union is evaluated, never the narrower set.

Forward-only recovery
---------------------
:class:`RecoveryPoint` records a checkpoint; it does not roll anything back. Recorded Truth
is forward-only (AIF-L17), so recovery means resuming from a recorded point, and a
"rollback" is a new forward change. The engine therefore has no undo operation — the
absence is the guarantee.

Determinism: every decision is a sorted lookup over declarations. No wall-clock, no RNG,
no I/O.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.contracts import PipelineDefinition, PipelinePolicy
from platform.universal_pipeline.errors import PipelineGovernanceError
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.identity import Identity, mint
from platform.universal_pipeline.state import require_state
from typing import Any

#: The governance authority of this engine. It executes canonical authority and never
#: holds it, so the value is a disclosure and not a placeholder.
GOVERNANCE_AUTHORITY = "NONE (DERIVED TRUTH)"


@dataclass(frozen=True, slots=True)
class GovernanceVerdict:
    """The auditable outcome of evaluating every binding obligation on one subject."""

    subject: str
    approved: bool
    considered: tuple[str, ...] = ()
    discharged: tuple[str, ...] = ()
    undischarged: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.subject, str) or not self.subject:
            raise PipelineGovernanceError("governance verdict subject is required")
        if not isinstance(self.approved, bool):
            raise PipelineGovernanceError(
                "governance verdict approval must be a bool", subject=self.subject
            )
        for label, values in (
            ("considered", self.considered),
            ("discharged", self.discharged),
            ("undischarged", self.undischarged),
            ("findings", self.findings),
        ):
            if not isinstance(values, tuple):
                raise PipelineGovernanceError(
                    f"governance verdict {label} must be a tuple", subject=self.subject
                )
        if self.approved and self.undischarged:
            raise PipelineGovernanceError(
                "an approved verdict cannot carry an undischarged blocking obligation",
                subject=self.subject,
                undischarged=list(self.undischarged),
            )
        if not self.approved and not self.undischarged and not self.findings:
            raise PipelineGovernanceError(
                "a refusal must state why it refused", subject=self.subject
            )

    @property
    def identity(self) -> Identity:
        return mint("governance-verdict", self.subject, self.fingerprint())

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "authority": GOVERNANCE_AUTHORITY,
            "approved": self.approved,
            "considered": list(self.considered),
            "discharged": list(self.discharged),
            "undischarged": list(self.undischarged),
            "findings": list(self.findings),
        }

    def fingerprint(self) -> str:
        return content_hash(
            {
                "subject": self.subject,
                "approved": self.approved,
                "considered": list(self.considered),
                "discharged": list(self.discharged),
                "undischarged": list(self.undischarged),
                "findings": list(self.findings),
            }
        )


@dataclass(frozen=True, slots=True)
class RecoveryPoint:
    """A recorded, forward-only checkpoint: where a subject was, and what it looked like.

    ``checkpoint`` is content-addressed, so resuming from a recovery point can prove the
    state it resumes from is the state that was recorded. There is no ``restore``: recovery
    is a forward continuation from a recorded point (AIF-L17).
    """

    subject: str
    state: str
    checkpoint: str
    ordinal: int
    detail: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.subject, str) or not self.subject:
            raise PipelineGovernanceError("recovery point subject is required")
        require_state(self.state)
        if not isinstance(self.checkpoint, str) or not self.checkpoint:
            raise PipelineGovernanceError(
                "recovery point checkpoint is required", subject=self.subject
            )
        if self.ordinal < 0:
            raise PipelineGovernanceError(
                "recovery point ordinal must be non-negative", subject=self.subject
            )
        if not isinstance(self.detail, Mapping):
            raise PipelineGovernanceError(
                "recovery point detail must be a mapping", subject=self.subject
            )

    @property
    def identity(self) -> Identity:
        return mint("recovery-point", self.subject, self.state, self.checkpoint)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "state": self.state,
            "checkpoint": self.checkpoint,
            "ordinal": self.ordinal,
            "detail": dict(self.detail),
        }


class PipelineGovernance:
    """The one policy-evaluation and audit authority of a platform instance."""

    __slots__ = ("_policies", "_verdicts", "_recovery", "_bus")

    def __init__(self, *, bus: PipelineEventBus | None = None) -> None:
        if bus is not None and not isinstance(bus, PipelineEventBus):
            raise PipelineGovernanceError("bus must be a PipelineEventBus")
        self._policies: dict[str, PipelinePolicy] = {}
        self._verdicts: list[GovernanceVerdict] = []
        self._recovery: list[RecoveryPoint] = []
        self._bus = bus

    # -- declaration ------------------------------------------------------------------

    def register_policy(self, policy: PipelinePolicy) -> PipelinePolicy:
        """Register a repository-wide policy that binds every subject.

        Raises:
            PipelineGovernanceError: if ``policy`` is not a
                :class:`~platform.universal_pipeline.contracts.PipelinePolicy`, or its id
                is already registered (rebinding a policy id would silently change what a
                past verdict meant).
        """
        if not isinstance(policy, PipelinePolicy):
            raise PipelineGovernanceError("only a PipelinePolicy can be registered")
        if policy.policy_id in self._policies:
            raise PipelineGovernanceError("policy already registered", policy_id=policy.policy_id)
        self._policies[policy.policy_id] = policy
        return policy

    @property
    def policies(self) -> tuple[PipelinePolicy, ...]:
        """Every repository-wide policy, ordered by policy id (deterministic)."""
        return tuple(self._policies[pid] for pid in sorted(self._policies))

    @property
    def verdicts(self) -> tuple[GovernanceVerdict, ...]:
        """Every verdict produced, in evaluation order (the audit trail)."""
        return tuple(self._verdicts)

    @property
    def recovery_points(self) -> tuple[RecoveryPoint, ...]:
        """Every recorded recovery point, in record order."""
        return tuple(self._recovery)

    # -- evaluation -------------------------------------------------------------------

    def binding_policies(
        self,
        *,
        definition: PipelineDefinition | None = None,
        stage_id: str | None = None,
    ) -> tuple[PipelinePolicy, ...]:
        """Every policy binding the subject: repository-wide ∪ pipeline-declared.

        The union, never the narrower set: a pipeline cannot shed a repository-wide
        obligation by declaring its own. A repository-wide policy wins a policy-id
        collision, because the pipeline-declared one would otherwise redefine it.
        """
        binding: dict[str, PipelinePolicy] = {}
        if definition is not None:
            if not isinstance(definition, PipelineDefinition):
                raise PipelineGovernanceError("definition must be a PipelineDefinition")
            declared = (
                definition.policies_for(stage_id) if stage_id is not None else definition.policies
            )
            for policy in declared:
                binding[policy.policy_id] = policy
        for policy in self._policies.values():
            if stage_id is None or policy.binds(stage_id):
                binding[policy.policy_id] = policy
        return tuple(binding[pid] for pid in sorted(binding))

    def evaluate(
        self,
        subject: str,
        *,
        definition: PipelineDefinition | None = None,
        evidence: Mapping[str, Any] | None = None,
        stage_id: str | None = None,
    ) -> GovernanceVerdict:
        """Evaluate every binding obligation on ``subject`` and record the verdict.

        Approval requires every *blocking* obligation to be discharged by ``evidence``;
        advisory obligations produce findings only. A pipeline's declared governance
        obligations (:class:`~platform.universal_pipeline.contracts.PipelineGovernanceSpec`)
        are evaluated alongside its policies, so a governance posture is not a comment.

        Raises:
            PipelineGovernanceError: if ``subject`` is not a non-empty string, or
                ``evidence`` is not a mapping.
        """
        if not isinstance(subject, str) or not subject:
            raise PipelineGovernanceError("governance subject is required")
        if evidence is not None and not isinstance(evidence, Mapping):
            raise PipelineGovernanceError("governance evidence must be a mapping", subject=subject)
        discharged_by = dict(evidence or {})
        policies = self.binding_policies(definition=definition, stage_id=stage_id)
        considered: list[str] = []
        discharged: list[str] = []
        undischarged: list[str] = []
        findings: list[str] = []
        for policy in policies:
            considered.append(policy.obligation)
            if discharged_by.get(policy.obligation):
                discharged.append(policy.obligation)
            elif policy.blocking:
                undischarged.append(policy.obligation)
                findings.append(
                    f"undischarged blocking policy {policy.policy_id}: {policy.obligation}"
                )
            else:
                findings.append(
                    f"undischarged advisory policy {policy.policy_id}: {policy.obligation}"
                )
        if definition is not None:
            for obligation in definition.governance.obligations:
                considered.append(obligation)
                if discharged_by.get(obligation):
                    discharged.append(obligation)
                else:
                    undischarged.append(obligation)
                    findings.append(f"undischarged governance obligation: {obligation}")
        verdict = GovernanceVerdict(
            subject=subject,
            approved=not undischarged,
            considered=tuple(sorted(set(considered))),
            discharged=tuple(sorted(set(discharged))),
            undischarged=tuple(sorted(set(undischarged))),
            findings=tuple(sorted(set(findings))),
        )
        self._verdicts.append(verdict)
        if self._bus is not None:
            self._bus.emit("uapf.policy.evaluated", subject, payload=verdict.to_dict())
        return verdict

    def require_approved(self, verdict: GovernanceVerdict) -> None:
        """Fail closed unless ``verdict`` approved its subject.

        Raises:
            PipelineGovernanceError: naming the undischarged obligations. A refusal is an
                error and never a warning, so no caller can proceed past one by ignoring
                a return value.
        """
        if not isinstance(verdict, GovernanceVerdict):
            raise PipelineGovernanceError("a GovernanceVerdict is required")
        if not verdict.approved:
            raise PipelineGovernanceError(
                "governance refused the subject",
                subject=verdict.subject,
                undischarged=list(verdict.undischarged),
                findings=list(verdict.findings),
            )

    # -- recovery ---------------------------------------------------------------------

    def record_recovery_point(
        self,
        subject: str,
        state: str,
        *,
        detail: Mapping[str, Any] | None = None,
    ) -> RecoveryPoint:
        """Record a forward-only recovery point for ``subject`` at ``state``.

        Raises:
            PipelineGovernanceError: if ``subject`` is not a non-empty string.
            PipelineStateError: if ``state`` is not a declared lifecycle state.
        """
        if not isinstance(subject, str) or not subject:
            raise PipelineGovernanceError("recovery point subject is required")
        resolved = dict(detail or {})
        point = RecoveryPoint(
            subject=subject,
            state=state,
            checkpoint=content_hash({"subject": subject, "state": state, "detail": resolved}),
            ordinal=len(self._recovery),
            detail=resolved,
        )
        self._recovery.append(point)
        if self._bus is not None:
            self._bus.emit("uapf.recovery.recorded", subject, payload=point.to_dict())
        return point

    def latest_recovery_point(self, subject: str) -> RecoveryPoint:
        """The most recently recorded recovery point for ``subject``.

        Raises:
            PipelineGovernanceError: if none was recorded (fail-closed — resuming from a
                point that does not exist is exactly the failure mode to prevent).
        """
        for point in reversed(self._recovery):
            if point.subject == subject:
                return point
        raise PipelineGovernanceError("no recovery point recorded", subject=subject)

    # -- audit / evidence -------------------------------------------------------------

    def audit_trail(self, subject: str | None = None) -> tuple[dict[str, Any], ...]:
        """Every verdict and recovery point, optionally filtered to one ``subject``."""
        entries: list[dict[str, Any]] = [
            {"kind": "verdict", **verdict.to_dict()}
            for verdict in self._verdicts
            if subject is None or verdict.subject == subject
        ]
        entries.extend(
            {"kind": "recovery-point", **point.to_dict()}
            for point in self._recovery
            if subject is None or point.subject == subject
        )
        return tuple(entries)

    def verdicts_for(self, subject: str) -> tuple[GovernanceVerdict, ...]:
        """Every verdict recorded about ``subject``, in evaluation order."""
        return tuple(verdict for verdict in self._verdicts if verdict.subject == subject)

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable render of governance state (evidence)."""
        return {
            "authority": GOVERNANCE_AUTHORITY,
            "policy_count": len(self._policies),
            "policies": [policy.to_dict() for policy in self.policies],
            "verdict_count": len(self._verdicts),
            "approved": sum(1 for verdict in self._verdicts if verdict.approved),
            "refused": sum(1 for verdict in self._verdicts if not verdict.approved),
            "recovery_point_count": len(self._recovery),
            "verdicts": [verdict.to_dict() for verdict in self._verdicts],
            "recovery_points": [point.to_dict() for point in self._recovery],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of governance state."""
        return content_hash(self.to_dict())


def obligations_from(evidence: Iterable[str]) -> dict[str, bool]:
    """Build a discharged-evidence mapping from an iterable of obligation names.

    A convenience for the common case where a caller knows *which* obligations are
    discharged but has no value to attach. Keeps callers from hand-building ``{k: True}``
    dictionaries inconsistently.
    """
    return {str(name): True for name in evidence}


__all__ = [
    "GOVERNANCE_AUTHORITY",
    "GovernanceVerdict",
    "PipelineGovernance",
    "RecoveryPoint",
    "obligations_from",
]
