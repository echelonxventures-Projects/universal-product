"""EC2-TASK-000085 — Workspace Isolation (EC2-EPIC-004).

The deterministic tenant/workspace **isolation guard** that enforces acceptance
criterion **P3** (cross-tenant/workspace isolation holds in 100% of isolation tests).
It complements — and never replaces — the Identity Layer's tenant-scope invariant:
the identity policy already denies *scoped* principals (Partner/Integrator) that cross
a tenant boundary, and this guard extends the same rule to **every** tenant-bound
principal at the workspace-object level, giving a single, explicit
``tenant-isolation-violation`` reason.

The rule is pure and fail-closed:

    * a **global** workspace (``tenant is None``) is visible to all principals;
    * an **unscoped** principal (``tenant is None``, e.g. a platform administrator) is
      not confined to a tenant;
    * otherwise access is allowed **only** when the principal's tenant equals the
      workspace's tenant — a mismatch is denied.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.identity import Principal
from platform.workspace.contracts import Workspace
from platform.workspace.errors import WorkspaceIsolationError
from typing import Any


def tenants_isolated(principal_tenant: str | None, workspace_tenant: str | None) -> bool:
    """True iff a principal in ``principal_tenant`` is isolated from ``workspace_tenant``.

    Isolation holds (access denied) only when both tenants are set and differ.
    """
    return (
        workspace_tenant is not None
        and principal_tenant is not None
        and principal_tenant != workspace_tenant
    )


@dataclass(frozen=True, slots=True)
class IsolationDecision:
    """An immutable tenant/workspace isolation decision (fail-closed)."""

    allowed: bool
    reason: str
    principal_tenant: str | None
    workspace_tenant: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "principal_tenant": self.principal_tenant,
            "workspace_tenant": self.workspace_tenant,
        }


class IsolationGuard:
    """The deterministic tenant/workspace isolation decision point (P3)."""

    __slots__ = ()

    def evaluate(self, principal: Principal, workspace: Workspace) -> IsolationDecision:
        """Evaluate isolation for ``principal`` accessing ``workspace`` (fail-closed)."""
        if not isinstance(principal, Principal):
            raise WorkspaceIsolationError("a valid Principal is required")
        if not isinstance(workspace, Workspace):
            raise WorkspaceIsolationError("a valid Workspace is required")
        if workspace.tenant is None:
            return self._decision(True, "global-workspace", principal, workspace)
        if principal.tenant is None:
            return self._decision(True, "unscoped-principal", principal, workspace)
        if principal.tenant == workspace.tenant:
            return self._decision(True, "tenant-match", principal, workspace)
        return self._decision(False, "tenant-isolation-violation", principal, workspace)

    def permits(self, principal: Principal, workspace: Workspace) -> bool:
        """True iff isolation permits ``principal`` to access ``workspace``."""
        return self.evaluate(principal, workspace).allowed

    @staticmethod
    def _decision(
        allowed: bool, reason: str, principal: Principal, workspace: Workspace
    ) -> IsolationDecision:
        return IsolationDecision(
            allowed=allowed,
            reason=reason,
            principal_tenant=principal.tenant,
            workspace_tenant=workspace.tenant,
        )


__all__ = ["tenants_isolated", "IsolationDecision", "IsolationGuard"]
