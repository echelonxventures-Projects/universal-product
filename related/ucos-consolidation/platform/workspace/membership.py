"""EC2-TASK-000083 — Workspace Membership (EC2-EPIC-004).

The deterministic, append-only registry binding principals to workspaces with a
workspace-local :class:`~platform.workspace.contracts.MemberRole`. Membership is a
collaboration fact — *who belongs to this workspace and in what role* — and never a
substitute for platform authorization (which the Identity Layer resolves). The
registry is fail-closed (duplicate add, or removal/lookup of an absent member, raise)
and records every change as an ordered, append-only :class:`MembershipEvent` (no
wall-clock; a caller-supplied logical ``tick``) so membership history is reproducible
and auditable (OP-C3).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.workspace.contracts import MemberRole, WorkspaceMember
from platform.workspace.errors import MembershipError
from typing import Any


@dataclass(frozen=True, slots=True)
class MembershipEvent:
    """An immutable, ordered record of a membership change (append-only)."""

    sequence: int
    workspace_id: str
    principal_id: str
    role: MemberRole
    action: str
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "workspace_id": self.workspace_id,
            "principal_id": self.principal_id,
            "role": self.role.value,
            "action": self.action,
            "tick": self.tick,
        }


class MembershipRegistry:
    """A deterministic, append-only registry of workspace memberships."""

    __slots__ = ("_by_workspace", "_log")

    def __init__(self) -> None:
        # workspace_id -> {principal_id -> WorkspaceMember}
        self._by_workspace: dict[str, dict[str, WorkspaceMember]] = {}
        self._log: list[MembershipEvent] = []

    def add(
        self,
        workspace_id: str,
        principal_id: str,
        subject: str,
        role: MemberRole,
        *,
        tick: int,
    ) -> WorkspaceMember:
        """Add a principal to a workspace (fail-closed on duplicate)."""
        member = WorkspaceMember.create(workspace_id, principal_id, subject, role)
        members = self._by_workspace.setdefault(workspace_id, {})
        if principal_id in members:
            raise MembershipError(
                "principal is already a member",
                workspace_id=workspace_id,
                principal_id=principal_id,
            )
        members[principal_id] = member
        self._record(workspace_id, principal_id, role, "added", tick)
        return member

    def remove(self, workspace_id: str, principal_id: str, *, tick: int) -> WorkspaceMember:
        """Remove a principal from a workspace (fail-closed on absent member)."""
        members = self._by_workspace.get(workspace_id, {})
        member = members.get(principal_id)
        if member is None:
            raise MembershipError(
                "principal is not a member",
                workspace_id=workspace_id,
                principal_id=principal_id,
            )
        del members[principal_id]
        self._record(workspace_id, principal_id, member.role, "removed", tick)
        return member

    def member(self, workspace_id: str, principal_id: str) -> WorkspaceMember | None:
        """Return the principal's membership in a workspace, or ``None``."""
        return self._by_workspace.get(workspace_id, {}).get(principal_id)

    def is_member(self, workspace_id: str, principal_id: str) -> bool:
        """True iff the principal is currently a member of the workspace."""
        return principal_id in self._by_workspace.get(workspace_id, {})

    def members_of(self, workspace_id: str) -> tuple[WorkspaceMember, ...]:
        """Every current member of a workspace, in stable (principal-id) order."""
        members = self._by_workspace.get(workspace_id, {})
        return tuple(members[pid] for pid in sorted(members))

    def workspaces_of(self, principal_id: str) -> tuple[str, ...]:
        """Every workspace id the principal is currently a member of (stable order)."""
        return tuple(
            wid for wid in sorted(self._by_workspace) if principal_id in self._by_workspace[wid]
        )

    @property
    def workspace_ids(self) -> tuple[str, ...]:
        """Every workspace id that currently has at least one member (stable order)."""
        return tuple(wid for wid in sorted(self._by_workspace) if self._by_workspace[wid])

    @property
    def events(self) -> tuple[MembershipEvent, ...]:
        """An immutable snapshot of the append-only membership event log (in order)."""
        return tuple(self._log)

    def __len__(self) -> int:
        """The total number of current memberships across all workspaces."""
        return sum(len(members) for members in self._by_workspace.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "membership_count": len(self),
            "memberships": [
                self._by_workspace[wid][pid].to_dict()
                for wid in sorted(self._by_workspace)
                for pid in sorted(self._by_workspace[wid])
            ],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())

    def _record(
        self, workspace_id: str, principal_id: str, role: MemberRole, action: str, tick: int
    ) -> None:
        self._log.append(
            MembershipEvent(
                sequence=len(self._log),
                workspace_id=workspace_id,
                principal_id=principal_id,
                role=role,
                action=action,
                tick=tick,
            )
        )


__all__ = ["MembershipEvent", "MembershipRegistry"]
