"""EC2-CAP-SEC-001 / SEC-INTEL — Security Intelligence model, ledger, roll-up & service.

The heart of the **Security Intelligence Runtime** (Phase 2): the immutable,
evaluative, **non-enforcing** :class:`SecurityFinding` record, the append-only
:class:`FindingLedger`, the automatic **evidence-derived roll-up**, and the
:class:`SecurityIntelligenceService` composition root that records findings, computes
the security dimension, and produces deterministic evidence.

A :class:`SecurityFinding` is the platform realization of the UKB-ADV-005 security
intelligence entities (Threat Models · Security Controls · Vulnerabilities/Findings ·
Exceptions · Penetration Results · Compliance/Audit Evidence), recorded against the
physical ``finding.schema.json`` vocabulary **by reference**. It *records* and
*correlates*; it grants no access, enforces no policy, and enacts nothing
(ARCH-SECURITY-001 §11/§21; RG-02 / AR-04). The roll-up is **evidence-derived only**
— open ``CRITICAL``/``HIGH`` without a valid Exception ⇒ ``BLOCKED``; exceptions
auto-expire when ``expires <= now``; no security status is entered by hand
(UKB-ADV-005 §4).

Secret defense (UKB-ADV-005 §6; SEC-04 / RR-07): the runtime stores **no** secret
value. Any ingested field containing a detected secret pattern is rejected and a
``SECRET-LEAK`` finding referencing **location only** is recorded instead.

Determinism (IMP-007 §5): all time inputs are caller-supplied **logical ticks**
(integers), never wall-clock; every identity and fingerprint is content-addressed, so
the same findings and the same logical ``now`` yield the same ledger, roll-up, and
:class:`SecurityIntelligenceEvidence`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.security.contracts import (
    BLOCKING_SEVERITIES,
    OPEN_FINDING_STATES,
    FindingKind,
    FindingState,
    RollupState,
    Severity,
    all_finding_kinds,
    all_finding_states,
    all_severities,
)
from platform.security.errors import (
    FindingValidationError,
    SecurityFindingError,
    SecurityRollupError,
)
from typing import Any

#: The governed event emitted for every recorded finding (PC-16).
FINDING_RECORDED_EVENT = "security.intelligence.finding.recorded"

#: The governed event emitted for every evidence-derived roll-up evaluation.
ROLLUP_EVALUATED_EVENT = "security.intelligence.rollup.evaluated"

#: The default backward-traceability source for a finding (the physical schema).
FINDING_SCHEMA_SOURCE_DEFAULT = "00-BOOK/SCHEMAS/finding.schema.json (UKB-ADV-005 §2)"

#: The finding kinds that represent an active security *exposure* subject to roll-up.
#: Controls, exceptions, and compliance/audit evidence are posture records, not
#: exposures, so they never drive the blocking view (UKB-ADV-005 §4).
EXPOSURE_KINDS: frozenset[FindingKind] = frozenset(
    {FindingKind.VULNERABILITY, FindingKind.THREAT, FindingKind.PENTEST}
)

#: The synthetic identifier a recorded secret-leak finding carries (UKB-ADV-005 §6).
SECRET_LEAK_IDENTIFIER = "SECRET-LEAK"  # noqa: S105 — a finding identifier, not a credential

#: Deterministic, non-capturing secret-shape patterns used to reject secret values at
#: ingest. These detect the *shape* of common secrets; no secret value is embedded
#: (they are detectors, not credentials — SEC-04 / RR-07).
_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),  # AWS access key id shape
    re.compile(r"\bASIA[0-9A-Z]{16}\b"),  # AWS temporary access key id shape
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),  # GitHub token shapes
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),  # Slack token shapes
    re.compile(r"\bey[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),  # JWT
    re.compile(r"(?i)\b(?:secret|token|api[_-]?key|passwd|password)\b\s*[:=]\s*\S{6,}"),
)


def scan_for_secret(text: str | None) -> bool:
    """Return ``True`` iff ``text`` matches any known secret shape (value never stored)."""
    if not text:
        return False
    return any(pattern.search(text) for pattern in _SECRET_PATTERNS)


@dataclass(frozen=True, slots=True)
class SecurityFinding:
    """An immutable, evaluative, non-enforcing security-intelligence finding.

    Records a UKB-ADV-005 entity of ``kind`` (Vulnerability / Control / Threat /
    Exception / PenTest / Compliance / Audit evidence) with an evaluative ``state``
    and optional ``severity``. Time-boxed fields (``sla_due`` / ``expires``) are
    caller-supplied **logical ticks** (never wall-clock). ``non_enforcing`` is
    invariantly ``True`` — the record enacts nothing. ``finding_id`` is
    content-addressed (deterministic; ``UCOS-SFND-``).
    """

    kind: FindingKind
    name: str
    state: FindingState = FindingState.OPEN
    severity: Severity | None = None
    identifier: str | None = None
    affects: tuple[str, ...] = ()
    mitigates: tuple[str, ...] = ()
    sla_due: int | None = None
    exception_of: str | None = None
    approver: str | None = None
    expires: int | None = None
    evidence: str | None = None
    source_ref: str = ""
    non_enforcing: bool = True
    finding_id: str = ""

    @classmethod
    def create(
        cls,
        kind: FindingKind,
        name: str,
        *,
        state: FindingState = FindingState.OPEN,
        severity: Severity | None = None,
        identifier: str | None = None,
        affects: tuple[str, ...] | list[str] = (),
        mitigates: tuple[str, ...] | list[str] = (),
        sla_due: int | None = None,
        exception_of: str | None = None,
        approver: str | None = None,
        expires: int | None = None,
        evidence: str | None = None,
        source_ref: str = FINDING_SCHEMA_SOURCE_DEFAULT,
    ) -> SecurityFinding:
        """Build a finding with a deterministic id, fail-closed on any violation."""
        if not isinstance(kind, FindingKind):
            raise SecurityFindingError("finding kind must be a FindingKind")
        if not isinstance(name, str) or not name.strip():
            raise SecurityFindingError("finding requires a non-empty name", kind=kind.value)
        if not isinstance(state, FindingState):
            raise SecurityFindingError("finding state must be a FindingState", kind=kind.value)
        if severity is not None and not isinstance(severity, Severity):
            raise SecurityFindingError(
                "finding severity must be a Severity or None", kind=kind.value
            )
        for tick_name, tick in (("sla_due", sla_due), ("expires", expires)):
            if tick is not None and (not isinstance(tick, int) or isinstance(tick, bool)):
                raise SecurityFindingError(
                    f"{tick_name} must be a logical tick (int) or None", kind=kind.value
                )
        affects_t = tuple(affects)
        mitigates_t = tuple(mitigates)
        # An EXCEPTION is a time-boxed risk acceptance: it must reference the finding
        # it excepts, name an approver, and carry an expiry tick (UKB-ADV-005 §2/§4).
        if kind is FindingKind.EXCEPTION:
            if not (isinstance(exception_of, str) and exception_of.strip()):
                raise SecurityFindingError("an EXCEPTION must reference the finding it excepts")
            if not (isinstance(approver, str) and approver.strip()):
                raise SecurityFindingError("an EXCEPTION must name an approver", name=name)
            if not isinstance(expires, int) or isinstance(expires, bool):
                raise SecurityFindingError("an EXCEPTION must carry an expiry tick", name=name)
        elif exception_of is not None:
            raise SecurityFindingError(
                "only an EXCEPTION may carry exception_of", kind=kind.value, name=name
            )
        core = {
            "kind": kind.value,
            "name": name,
            "state": state.value,
            "severity": severity.value if severity is not None else None,
            "identifier": identifier,
            "affects": list(affects_t),
            "mitigates": list(mitigates_t),
            "sla_due": sla_due,
            "exception_of": exception_of,
            "approver": approver,
            "expires": expires,
            "evidence": evidence,
            "source_ref": source_ref,
            "non_enforcing": True,
        }
        return cls(
            kind=kind,
            name=name,
            state=state,
            severity=severity,
            identifier=identifier,
            affects=affects_t,
            mitigates=mitigates_t,
            sla_due=sla_due,
            exception_of=exception_of,
            approver=approver,
            expires=expires,
            evidence=evidence,
            source_ref=source_ref,
            non_enforcing=True,
            finding_id=f"UCOS-SFND-{content_hash(core)[:16]}",
        )

    @property
    def is_exposure(self) -> bool:
        """True iff this finding represents an active exposure subject to roll-up."""
        return self.kind in EXPOSURE_KINDS

    def is_open(self) -> bool:
        """True iff this finding is still an active exposure (OPEN / IN_PROGRESS)."""
        return self.state in OPEN_FINDING_STATES

    def is_valid_exception(self, now: int) -> bool:
        """True iff this ACCEPTED exception has not expired at logical ``now``."""
        if self.kind is not FindingKind.EXCEPTION:
            return False
        if self.state is not FindingState.ACCEPTED:
            return False
        return self.expires is not None and self.expires > now

    def validate(self) -> dict[str, Any]:
        """Re-affirm meta-validity (typed · identified · non-enforcing · kind-consistent).

        Raises :class:`FindingValidationError` if an invariant is violated (which
        :meth:`create` already prevents; this is a defensive re-check for callers).
        """
        exception_consistent = (self.kind is FindingKind.EXCEPTION) == (
            self.exception_of is not None
        )
        checks = {
            "typed": isinstance(self.kind, FindingKind) and isinstance(self.state, FindingState),
            "identified": self.finding_id.startswith("UCOS-SFND-"),
            "named": bool(self.name and self.name.strip()),
            "non_enforcing": self.non_enforcing is True,
            "exception_reference_consistent": exception_consistent,
            "secret_free": not scan_for_secret(self.evidence),
        }
        if not all(checks.values()):
            failed = sorted(n for n, ok in checks.items() if not ok)
            raise FindingValidationError(
                "finding failed meta-validity",
                finding_id=self.finding_id,
                failed=",".join(failed),
            )
        return {"finding_id": self.finding_id, "meta_valid": True, "checks": checks}

    def trace(self) -> dict[str, Any]:
        """Return the traceability chain (backward source · subject · affected refs)."""
        return {
            "finding_id": self.finding_id,
            "backward": {"kind": self.kind.value, "source_ref": self.source_ref},
            "subject": {"name": self.name, "identifier": self.identifier},
            "affects": list(self.affects),
            "exception_of": self.exception_of,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "kind": self.kind.value,
            "name": self.name,
            "state": self.state.value,
            "severity": self.severity.value if self.severity is not None else None,
            "identifier": self.identifier,
            "affects": list(self.affects),
            "mitigates": list(self.mitigates),
            "sla_due": self.sla_due,
            "exception_of": self.exception_of,
            "approver": self.approver,
            "expires": self.expires,
            "evidence": self.evidence,
            "source_ref": self.source_ref,
            "non_enforcing": self.non_enforcing,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class FindingLedger:
    """SEC-INTEL's deterministic, append-only finding record surface.

    Records :class:`SecurityFinding` entries. Append-only and idempotent by
    ``finding_id`` (re-recording an identical finding returns the existing entry; it
    never mutates or duplicates). It exposes **no** ratify/enact/override operation
    (RG-02 / AR-04) and is **not** the seven-registry SEC-REG system (a later phase).
    """

    __slots__ = ("_entries", "_index")

    def __init__(self) -> None:
        self._entries: list[SecurityFinding] = []
        self._index: dict[str, int] = {}

    def record(self, finding: SecurityFinding) -> SecurityFinding:
        """Append a finding (idempotent by id); returns the stored entry (fail-closed)."""
        if not isinstance(finding, SecurityFinding):
            raise SecurityFindingError("only a SecurityFinding may be recorded")
        finding.validate()
        existing = self._index.get(finding.finding_id)
        if existing is not None:
            return self._entries[existing]
        self._index[finding.finding_id] = len(self._entries)
        self._entries.append(finding)
        return finding

    @property
    def findings(self) -> tuple[SecurityFinding, ...]:
        """An immutable snapshot of the append-only ledger (in record order)."""
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, finding_id: str) -> bool:
        return finding_id in self._index

    def get(self, finding_id: str) -> SecurityFinding:
        """Return a recorded finding by id (raises if absent)."""
        idx = self._index.get(finding_id)
        if idx is None:
            raise SecurityFindingError("no such finding", finding_id=finding_id)
        return self._entries[idx]

    def by_kind(self, kind: FindingKind) -> tuple[SecurityFinding, ...]:
        """Every recorded finding of ``kind`` in record order (queryable)."""
        return tuple(f for f in self._entries if f.kind is kind)

    def by_state(self, state: FindingState) -> tuple[SecurityFinding, ...]:
        """Every recorded finding in ``state`` in record order (queryable)."""
        return tuple(f for f in self._entries if f.state is state)

    def by_severity(self, severity: Severity) -> tuple[SecurityFinding, ...]:
        """Every recorded finding of ``severity`` in record order (queryable)."""
        return tuple(f for f in self._entries if f.severity is severity)

    def affecting(self, subject_ref: str) -> tuple[SecurityFinding, ...]:
        """Every recorded finding that affects ``subject_ref`` in record order."""
        return tuple(f for f in self._entries if subject_ref in f.affects)

    def exceptions(self) -> tuple[SecurityFinding, ...]:
        """Every recorded EXCEPTION finding in record order."""
        return tuple(f for f in self._entries if f.kind is FindingKind.EXCEPTION)

    def fingerprint(self) -> str:
        """A deterministic fingerprint over the ordered ledger."""
        return content_hash([f.to_dict() for f in self._entries])

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_count": len(self._entries),
            "findings": [f.to_dict() for f in self._entries],
        }


@dataclass(frozen=True, slots=True)
class SecurityRollup:
    """The evidence-derived security roll-up over a ledger at a logical ``now``.

    Deterministic and content-addressed (``UCOS-SRUP-``). ``state`` is computed from
    evidence only (UKB-ADV-005 §4); it is never entered by hand.
    """

    state: RollupState
    evaluated_at: int
    open_exposure_count: int
    blocking_count: int
    in_progress_count: int
    valid_exception_count: int
    expired_exception_count: int
    blocked_by: tuple[str, ...]
    rollup_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        state: RollupState,
        evaluated_at: int,
        open_exposure_count: int,
        blocking_count: int,
        in_progress_count: int,
        valid_exception_count: int,
        expired_exception_count: int,
        blocked_by: tuple[str, ...],
    ) -> SecurityRollup:
        core = {
            "state": state.value,
            "evaluated_at": evaluated_at,
            "open_exposure_count": open_exposure_count,
            "blocking_count": blocking_count,
            "in_progress_count": in_progress_count,
            "valid_exception_count": valid_exception_count,
            "expired_exception_count": expired_exception_count,
            "blocked_by": list(blocked_by),
        }
        return cls(
            state=state,
            evaluated_at=evaluated_at,
            open_exposure_count=open_exposure_count,
            blocking_count=blocking_count,
            in_progress_count=in_progress_count,
            valid_exception_count=valid_exception_count,
            expired_exception_count=expired_exception_count,
            blocked_by=blocked_by,
            rollup_id=f"UCOS-SRUP-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rollup_id": self.rollup_id,
            "state": self.state.value,
            "evaluated_at": self.evaluated_at,
            "open_exposure_count": self.open_exposure_count,
            "blocking_count": self.blocking_count,
            "in_progress_count": self.in_progress_count,
            "valid_exception_count": self.valid_exception_count,
            "expired_exception_count": self.expired_exception_count,
            "blocked_by": list(self.blocked_by),
            "enacts": False,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def compute_rollup(findings: tuple[SecurityFinding, ...], now: int) -> SecurityRollup:
    """Compute the evidence-derived security roll-up (pure; deterministic).

    Rule (UKB-ADV-005 §4): an open ``CRITICAL``/``HIGH`` exposure without a valid,
    non-expired Exception forces ``BLOCKED``; any other open exposure yields
    ``IN_PROGRESS``; otherwise ``APPROVED``. Exceptions auto-expire when
    ``expires <= now``. Enacts nothing.
    """
    if not isinstance(now, int) or isinstance(now, bool):
        raise SecurityRollupError("roll-up requires a logical tick (int) now")
    # Index valid (non-expired) exceptions by the finding they except. Only ACCEPTED
    # EXCEPTION findings reach the body; create() guarantees each carries an expiry
    # tick and an exception_of, so validity reduces to expires > now.
    valid_exceptions: set[str | None] = set()
    valid_exception_count = 0
    expired_exception_count = 0
    for f in findings:
        if f.kind is not FindingKind.EXCEPTION or f.state is not FindingState.ACCEPTED:
            continue
        if f.is_valid_exception(now):
            valid_exception_count += 1
            valid_exceptions.add(f.exception_of)
        else:
            expired_exception_count += 1

    open_exposure_count = 0
    blocking_count = 0
    in_progress_count = 0
    blocked_by: list[str] = []
    for f in findings:
        if not f.is_exposure or not f.is_open():
            continue
        open_exposure_count += 1
        excepted = f.finding_id in valid_exceptions
        if f.severity in BLOCKING_SEVERITIES and not excepted:
            blocking_count += 1
            blocked_by.append(f.finding_id)
        else:
            in_progress_count += 1

    if blocking_count > 0:
        state = RollupState.BLOCKED
    elif in_progress_count > 0:
        state = RollupState.IN_PROGRESS
    else:
        state = RollupState.APPROVED

    return SecurityRollup.create(
        state=state,
        evaluated_at=now,
        open_exposure_count=open_exposure_count,
        blocking_count=blocking_count,
        in_progress_count=in_progress_count,
        valid_exception_count=valid_exception_count,
        expired_exception_count=expired_exception_count,
        blocked_by=tuple(sorted(blocked_by)),
    )


@dataclass(frozen=True, slots=True)
class SecurityIntelligenceEvidence:
    """A deterministic, content-addressed report over recorded findings + roll-up.

    Aggregates the ledger fingerprint, per-kind / per-severity / per-state counts, and
    the evidence-derived roll-up at a logical ``now`` into a single reproducible
    evidence object for audit and program-certification roll-up. ``UCOS-SIEV-``.
    """

    ledger_fingerprint: str
    finding_count: int
    rollup: dict[str, Any]
    kind_counts: tuple[tuple[str, int], ...]
    severity_counts: tuple[tuple[str, int], ...]
    state_counts: tuple[tuple[str, int], ...]
    findings: tuple[dict[str, Any], ...]
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        ledger_fingerprint: str,
        rollup: dict[str, Any],
        kind_counts: tuple[tuple[str, int], ...],
        severity_counts: tuple[tuple[str, int], ...],
        state_counts: tuple[tuple[str, int], ...],
        findings: tuple[dict[str, Any], ...],
    ) -> SecurityIntelligenceEvidence:
        core = {
            "ledger_fingerprint": ledger_fingerprint,
            "rollup": rollup,
            "kind_counts": [list(kc) for kc in kind_counts],
            "severity_counts": [list(sc) for sc in severity_counts],
            "state_counts": [list(sc) for sc in state_counts],
            "findings": list(findings),
        }
        return cls(
            ledger_fingerprint=ledger_fingerprint,
            finding_count=len(findings),
            rollup=rollup,
            kind_counts=kind_counts,
            severity_counts=severity_counts,
            state_counts=state_counts,
            findings=findings,
            evidence_id=f"UCOS-SIEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "ledger_fingerprint": self.ledger_fingerprint,
            "finding_count": self.finding_count,
            "rollup": dict(self.rollup),
            "kind_counts": [list(kc) for kc in self.kind_counts],
            "severity_counts": [list(sc) for sc in self.severity_counts],
            "state_counts": [list(sc) for sc in self.state_counts],
            "findings": [dict(f) for f in self.findings],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class SecurityIntelligenceService:
    """The governed SEC-INTEL composition root (record · rollup · trace · validate · report)."""

    __slots__ = ("_ledger", "_events")

    def __init__(
        self,
        *,
        ledger: FindingLedger | None = None,
        events: EventBus | None = None,
    ) -> None:
        if ledger is not None and not isinstance(ledger, FindingLedger):
            raise SecurityFindingError("ledger must be a FindingLedger when provided")
        if events is not None and not isinstance(events, EventBus):
            raise SecurityFindingError("events must be an EventBus when provided")
        self._ledger = ledger if ledger is not None else FindingLedger()
        self._events = events

    @property
    def ledger(self) -> FindingLedger:
        return self._ledger

    # -- record (with secret defense) -------------------------------------------

    def record_finding(
        self,
        kind: FindingKind,
        name: str,
        *,
        state: FindingState = FindingState.OPEN,
        severity: Severity | None = None,
        identifier: str | None = None,
        affects: tuple[str, ...] | list[str] = (),
        mitigates: tuple[str, ...] | list[str] = (),
        sla_due: int | None = None,
        exception_of: str | None = None,
        approver: str | None = None,
        expires: int | None = None,
        evidence: str | None = None,
        source_ref: str = FINDING_SCHEMA_SOURCE_DEFAULT,
        location: str | None = None,
    ) -> SecurityFinding:
        """Record a finding, defending against secret leakage (UKB-ADV-005 §6).

        If any ingested field (name / identifier / evidence) contains a detected
        secret pattern, the original finding is **rejected** (its value is never
        stored) and a ``SECRET-LEAK`` finding referencing **location only** is
        recorded and returned instead. Otherwise the finding is recorded normally.
        A governed ``security.intelligence.finding.recorded`` event is emitted.
        """
        if scan_for_secret(name) or scan_for_secret(identifier) or scan_for_secret(evidence):
            return self._record_secret_leak(affects=tuple(affects), location=location)
        finding = SecurityFinding.create(
            kind,
            name,
            state=state,
            severity=severity,
            identifier=identifier,
            affects=affects,
            mitigates=mitigates,
            sla_due=sla_due,
            exception_of=exception_of,
            approver=approver,
            expires=expires,
            evidence=evidence,
            source_ref=source_ref,
        )
        recorded = self._ledger.record(finding)
        self._emit_finding(recorded, secret_leak=False)
        return recorded

    def record(self, finding: SecurityFinding) -> SecurityFinding:
        """Record a pre-built finding (idempotent; fail-closed on secret content)."""
        if not isinstance(finding, SecurityFinding):
            raise SecurityFindingError("only a SecurityFinding may be recorded")
        recorded = self._ledger.record(finding)
        self._emit_finding(recorded, secret_leak=False)
        return recorded

    def _record_secret_leak(
        self, *, affects: tuple[str, ...], location: str | None
    ) -> SecurityFinding:
        """Record a location-only SECRET-LEAK finding (no secret value stored)."""
        loc = location if (isinstance(location, str) and location.strip()) else "|".join(affects)
        leak = SecurityFinding.create(
            FindingKind.VULNERABILITY,
            "detected secret pattern (value redacted)",
            state=FindingState.OPEN,
            severity=Severity.CRITICAL,
            identifier=SECRET_LEAK_IDENTIFIER,
            affects=affects,
            evidence=f"secret detected at location: {loc or 'unspecified'} (value not stored)",
            source_ref="UKB-ADV-005 §6 (SEC-04 / RR-07)",
        )
        recorded = self._ledger.record(leak)
        self._emit_finding(recorded, secret_leak=True)
        return recorded

    # -- roll-up ----------------------------------------------------------------

    def rollup(self, now: int) -> SecurityRollup:
        """Compute + emit the evidence-derived security roll-up at logical ``now``."""
        result = compute_rollup(self._ledger.findings, now)
        if self._events is not None:
            self._events.publish(
                ROLLUP_EVALUATED_EVENT,
                source="platform.security.intelligence",
                subject="security.dimension",
                payload={"rollup": result.to_dict(), "enacts": False},
            )
        return result

    # -- trace + validate + report ----------------------------------------------

    def trace(self, finding_id: str) -> dict[str, Any]:
        """Return the traceability chain for a recorded finding."""
        return self._ledger.get(finding_id).trace()

    def validate(self, finding_id: str) -> dict[str, Any]:
        """Re-affirm the meta-validity of a recorded finding (fail-closed)."""
        return self._ledger.get(finding_id).validate()

    def validate_all(self) -> dict[str, Any]:
        """Validate every recorded finding; returns an aggregate decidable result."""
        results = [f.validate() for f in self._ledger.findings]
        return {
            "finding_count": len(results),
            "meta_valid": all(r["meta_valid"] for r in results),
            "results": results,
        }

    def report(self, now: int) -> SecurityIntelligenceEvidence:
        """Produce deterministic intelligence evidence over the ledger at ``now``."""
        findings = self._ledger.findings
        kind_counts = tuple(
            (k.value, sum(1 for f in findings if f.kind is k)) for k in all_finding_kinds()
        )
        severity_counts = tuple(
            (s.value, sum(1 for f in findings if f.severity is s)) for s in all_severities()
        )
        state_counts = tuple(
            (s.value, sum(1 for f in findings if f.state is s)) for s in all_finding_states()
        )
        return SecurityIntelligenceEvidence.create(
            ledger_fingerprint=self._ledger.fingerprint(),
            rollup=compute_rollup(findings, now).to_dict(),
            kind_counts=kind_counts,
            severity_counts=severity_counts,
            state_counts=state_counts,
            findings=tuple(f.to_dict() for f in findings),
        )

    def to_dict(self, now: int) -> dict[str, Any]:
        return {"ledger": self._ledger.to_dict(), "evidence": self.report(now).to_dict()}

    # -- internals --------------------------------------------------------------

    def _emit_finding(self, finding: SecurityFinding, *, secret_leak: bool) -> None:
        """Publish a governed ``security.intelligence.finding.recorded`` event (if bound)."""
        if self._events is None:
            return
        self._events.publish(
            FINDING_RECORDED_EVENT,
            source="platform.security.intelligence",
            subject=finding.finding_id,
            payload={"finding": finding.to_dict(), "secret_leak": secret_leak, "enacts": False},
        )


def build_security_intelligence_service(
    *, events: EventBus | None = None
) -> SecurityIntelligenceService:
    """Default composition of the Security Intelligence Runtime (record-only)."""
    return SecurityIntelligenceService(ledger=FindingLedger(), events=events)


__all__ = [
    "FINDING_RECORDED_EVENT",
    "ROLLUP_EVALUATED_EVENT",
    "EXPOSURE_KINDS",
    "SECRET_LEAK_IDENTIFIER",
    "FINDING_SCHEMA_SOURCE_DEFAULT",
    "scan_for_secret",
    "SecurityFinding",
    "FindingLedger",
    "SecurityRollup",
    "compute_rollup",
    "SecurityIntelligenceEvidence",
    "SecurityIntelligenceService",
    "build_security_intelligence_service",
]
