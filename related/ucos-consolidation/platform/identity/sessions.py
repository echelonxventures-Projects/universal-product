"""EC2-TASK-000068 — Session Model (EC2-EPIC-002).

The immutable session vocabulary plus a deterministic, append-only session registry.
A :class:`Session` binds an authenticated principal to a bounded lifetime; the
:class:`SessionRegistry` establishes, validates, and revokes sessions for the
authorization service (PC-01).

Design (IMP-007 §5 determinism; SEC-04 secrets by reference; fail-closed):
    * **No wall-clock.** A session's lifetime is expressed in a caller-supplied
      **logical clock** (monotonic integer ``tick``s). ``expires_at = issued_at + ttl``.
      Validity is a pure function of a supplied ``now`` tick, so the whole model is
      reproducible and never reads the system clock.
    * **Content-addressed identity.** ``session_id`` is a content hash of the session
      core (principal, tenant, issued_at, expires_at, credential reference), so an
      identical establishment is idempotent and reproducible.
    * **Secrets by reference only.** A session may carry a ``credential_ref`` (an
      opaque reference to externally-held credential material) — **never** a secret
      value (SEC-04).
    * **Append-only & fail-closed.** Establishment and revocation are recorded in an
      append-only event log; :meth:`SessionRegistry.validate` raises on any
      absent / expired / revoked session (never silently allows).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Principal
from platform.identity.errors import SessionError
from typing import Any


class SessionStatus(str, Enum):
    """The effective status of a session at a given logical time."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(frozen=True, slots=True)
class Session:
    """An immutable, content-addressed authenticated session (no wall-clock).

    ``lifecycle`` is the stored lifecycle state (``ACTIVE`` or ``REVOKED``); the
    *effective* status additionally accounts for expiry against a supplied ``now``.
    """

    principal_id: str
    subject: str
    issued_at: int
    expires_at: int
    tenant: str | None = None
    credential_ref: str | None = None
    lifecycle: SessionStatus = SessionStatus.ACTIVE
    session_id: str = ""

    @classmethod
    def establish(
        cls,
        principal: Principal,
        *,
        issued_at: int,
        ttl: int,
        credential_ref: str | None = None,
    ) -> Session:
        """Build an ACTIVE session with a deterministic, content-addressed id."""
        if not isinstance(principal, Principal):
            raise SessionError("a valid Principal is required to establish a session")
        if not isinstance(issued_at, int) or isinstance(issued_at, bool) or issued_at < 0:
            raise SessionError(
                "issued_at must be a non-negative logical tick",
                principal_id=principal.principal_id,
            )
        if not isinstance(ttl, int) or isinstance(ttl, bool) or ttl <= 0:
            raise SessionError(
                "ttl must be a positive number of logical ticks",
                principal_id=principal.principal_id,
            )
        if credential_ref is not None and (
            not isinstance(credential_ref, str) or not credential_ref
        ):
            raise SessionError(
                "credential_ref must be a non-empty reference string (SEC-04)",
                principal_id=principal.principal_id,
            )
        expires_at = issued_at + ttl
        core = {
            "principal_id": principal.principal_id,
            "subject": principal.subject,
            "tenant": principal.tenant,
            "issued_at": issued_at,
            "expires_at": expires_at,
            "credential_ref": credential_ref,
        }
        return cls(
            principal_id=principal.principal_id,
            subject=principal.subject,
            issued_at=issued_at,
            expires_at=expires_at,
            tenant=principal.tenant,
            credential_ref=credential_ref,
            lifecycle=SessionStatus.ACTIVE,
            session_id=f"UCOS-SESS-{content_hash(core)[:16]}",
        )

    def effective_status(self, now: int) -> SessionStatus:
        """The effective status at logical time ``now`` (revocation wins over expiry)."""
        if self.lifecycle is SessionStatus.REVOKED:
            return SessionStatus.REVOKED
        if now >= self.expires_at:
            return SessionStatus.EXPIRED
        return SessionStatus.ACTIVE

    def is_valid(self, now: int) -> bool:
        """True iff the session is ACTIVE (not expired, not revoked) at ``now``."""
        return self.effective_status(now) is SessionStatus.ACTIVE

    def revoked(self) -> Session:
        """Return a REVOKED copy of this session (immutable transition)."""
        return Session(
            principal_id=self.principal_id,
            subject=self.subject,
            issued_at=self.issued_at,
            expires_at=self.expires_at,
            tenant=self.tenant,
            credential_ref=self.credential_ref,
            lifecycle=SessionStatus.REVOKED,
            session_id=self.session_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "principal_id": self.principal_id,
            "subject": self.subject,
            "tenant": self.tenant,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "credential_ref": self.credential_ref,
            "lifecycle": self.lifecycle.value,
        }


@dataclass(frozen=True, slots=True)
class SessionEvent:
    """An append-only record of a session lifecycle transition (deterministic)."""

    sequence: int
    session_id: str
    status: SessionStatus
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "session_id": self.session_id,
            "status": self.status.value,
            "tick": self.tick,
        }


class SessionRegistry:
    """A deterministic, append-only registry of authenticated sessions (PC-01)."""

    __slots__ = ("_by_id", "_log")

    def __init__(self) -> None:
        self._by_id: dict[str, Session] = {}
        self._log: list[SessionEvent] = []

    def establish(
        self,
        principal: Principal,
        *,
        issued_at: int,
        ttl: int,
        credential_ref: str | None = None,
    ) -> Session:
        """Establish (or idempotently return) a session for ``principal``."""
        session = Session.establish(
            principal, issued_at=issued_at, ttl=ttl, credential_ref=credential_ref
        )
        existing = self._by_id.get(session.session_id)
        if existing is not None:
            return existing
        self._by_id[session.session_id] = session
        self._record(session.session_id, SessionStatus.ACTIVE, issued_at)
        return session

    def get(self, session_id: str) -> Session:
        """Resolve a session by id (raises if absent)."""
        session = self._by_id.get(session_id)
        if session is None:
            raise SessionError("no such session", session_id=session_id)
        return session

    def validate(self, session_id: str, now: int) -> Session:
        """Return the session iff it is ACTIVE at ``now`` (fail-closed)."""
        if not isinstance(now, int) or isinstance(now, bool) or now < 0:
            raise SessionError("now must be a non-negative logical tick", session_id=session_id)
        session = self.get(session_id)
        status = session.effective_status(now)
        if status is not SessionStatus.ACTIVE:
            raise SessionError("session is not active", session_id=session_id, status=status.value)
        return session

    def revoke(self, session_id: str, *, tick: int) -> Session:
        """Revoke a session (idempotent); records the transition (append-only)."""
        session = self.get(session_id)
        if session.lifecycle is SessionStatus.REVOKED:
            return session
        revoked = session.revoked()
        self._by_id[session_id] = revoked
        self._record(session_id, SessionStatus.REVOKED, tick)
        return revoked

    def __contains__(self, session_id: str) -> bool:
        return session_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

    @property
    def ids(self) -> tuple[str, ...]:
        """Every session id in deterministic order."""
        return tuple(sorted(self._by_id))

    def sessions(self) -> tuple[Session, ...]:
        """Every session in deterministic (id) order."""
        return tuple(self._by_id[sid] for sid in self.ids)

    def for_principal(self, principal_id: str) -> tuple[Session, ...]:
        """Every session for ``principal_id`` in deterministic order."""
        return tuple(s for s in self.sessions() if s.principal_id == principal_id)

    def active_sessions(self, now: int) -> tuple[Session, ...]:
        """Every session ACTIVE at ``now`` in deterministic order."""
        return tuple(s for s in self.sessions() if s.is_valid(now))

    @property
    def events(self) -> tuple[SessionEvent, ...]:
        """An immutable snapshot of the append-only session event log."""
        return tuple(self._log)

    def _record(self, session_id: str, status: SessionStatus, tick: int) -> None:
        self._log.append(
            SessionEvent(sequence=len(self._log), session_id=session_id, status=status, tick=tick)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_count": len(self._by_id),
            "sessions": [s.to_dict() for s in self.sessions()],
            "events": [e.to_dict() for e in self._log],
        }


__all__ = ["SessionStatus", "Session", "SessionEvent", "SessionRegistry"]
