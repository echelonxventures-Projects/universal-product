"""EC2-CAP-SEC-001 / SEC-ZONE — Zone & Control Posture Runtime (UMB-015 §1–§2).

The **Zone & Control Posture Runtime** (final sub-capability) records the posture of the
UMB-015 five protection zones (UCOS CORE · GOVERNANCE · ENGINEERING · OPERATIONS ·
CONSUMPTION) and seven controls (Access · Visibility · Identity · Synchronization ·
Publication · Knowledge · Audit), and evaluates the zone mutation-direction invariant
(UMB-INV-01: *higher zones may read outward; lower zones never mutate inward*).

Zones and controls are **policy configuration, not compiled ceilings** (UMB-015 §4): a
posture may be recorded against any of the canonical zones/controls **or** against a
free-form future zone/control target, so a new zone/control is incorporable additively
with no foundational redesign. Posture evaluation is **record-only** (determination
§6.1): it authorizes, ratifies, and enacts nothing (RG-02 / AR-04); it stores no secret
value (SEC-04 / RR-07); it writes nothing to the frozen corpus (DP-03). Security state is
DOMAIN-D and is never projected onto another domain (UMB-015 §5).

Determinism (IMP-007 §5): all time inputs are caller-supplied logical ticks; every id and
fingerprint is content-addressed.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.security.contracts import (
    CANON_ZONES,
    CONTROL_MECHANISM,
    ZONE_DEFAULT_POSTURE,
    ZONE_LEVEL,
    ZONE_NAME,
    RollupState,
    SecurityControl,
    SecurityZone,
    all_security_controls,
    all_security_zones,
)
from platform.security.errors import (
    SecurityZoneError,
    ZoneMutationError,
    ZonePostureError,
)
from platform.security.intelligence import scan_for_secret
from typing import Any

#: The governed event emitted for every recorded posture (PC-16).
POSTURE_RECORDED_EVENT = "security.zone.posture.recorded"

#: Posture target kinds (policy-configured; a target may also be a free-form future one).
POSTURE_TARGET_ZONE = "zone"
POSTURE_TARGET_CONTROL = "control"


def zone_may_mutate(source: SecurityZone, target: SecurityZone) -> dict[str, Any]:
    """Decide whether ``source`` may mutate ``target`` (UMB-INV-01; enacts nothing).

    A zone may mutate a target of equal-or-lower privilege only (``source`` level ≤
    ``target`` level). Consequently ZONE-3/ZONE-4 may never mutate the canon zones
    (ZONE-0/1/2). This is a **decidable predicate** recorded for evidence; it grants
    nothing and performs no write (RG-02 / AR-04).
    """
    if not isinstance(source, SecurityZone) or not isinstance(target, SecurityZone):
        raise ZoneMutationError("zone mutation evaluation requires two SecurityZone values")
    may = ZONE_LEVEL[source] <= ZONE_LEVEL[target]
    canon_guarded = target in CANON_ZONES and source not in CANON_ZONES
    if canon_guarded:
        reason = "canon zone (ZONE-0/1/2) is never mutated by ZONE-3/ZONE-4 (UMB-INV-01)"
    elif may:
        reason = "source is at least as privileged as the target (outward mutation permitted)"
    else:
        reason = "lower-privilege zone may not mutate inward toward the core (UMB-INV-01)"
    return {
        "source": source.value,
        "target": target.value,
        "may_mutate": may and not canon_guarded,
        "reason": reason,
        "enacts": False,
    }


@dataclass(frozen=True, slots=True)
class PostureRecord:
    """An immutable, evaluative, non-enacting zone/control posture record.

    Records that a ``target`` (a zone or control, canonical **or** free-form future one)
    bears an evaluative ``posture`` (a ``security``-dimension roll-up state) with a
    ``rationale`` and citing ``evidence_refs``. ``target_kind`` is ``"zone"`` or
    ``"control"``. ``evaluated_at`` is a caller-supplied logical tick. ``non_enacting``
    is invariantly ``True``. ``posture_id`` is content-addressed (``UCOS-SZON-``).
    """

    target_kind: str
    target: str
    posture: RollupState
    rationale: str
    evaluated_at: int
    evidence_refs: tuple[str, ...] = ()
    non_enacting: bool = True
    posture_id: str = ""

    @classmethod
    def create(
        cls,
        target_kind: str,
        target: str,
        posture: RollupState,
        *,
        rationale: str,
        evaluated_at: int,
        evidence_refs: tuple[str, ...] | list[str] = (),
    ) -> PostureRecord:
        """Build a posture record with a deterministic id, fail-closed on any violation."""
        if target_kind not in (POSTURE_TARGET_ZONE, POSTURE_TARGET_CONTROL):
            raise ZonePostureError(
                "target_kind must be 'zone' or 'control'", target_kind=str(target_kind)
            )
        if not isinstance(target, str) or not target.strip():
            raise ZonePostureError("posture requires a non-empty target", target_kind=target_kind)
        if not isinstance(posture, RollupState):
            raise ZonePostureError("posture must be a RollupState", target=target)
        if not isinstance(rationale, str) or not rationale.strip():
            raise ZonePostureError("posture requires a non-empty rationale", target=target)
        if not isinstance(evaluated_at, int) or isinstance(evaluated_at, bool):
            raise ZonePostureError("posture requires a logical tick evaluated_at", target=target)
        refs_t = tuple(evidence_refs)
        for value in (target, rationale, *refs_t):
            if scan_for_secret(value):
                raise ZonePostureError(
                    "posture rejected: a field matched a secret pattern (RR-07)", target=target
                )
        core = {
            "target_kind": target_kind,
            "target": target,
            "posture": posture.value,
            "rationale": rationale,
            "evaluated_at": evaluated_at,
            "evidence_refs": list(refs_t),
            "non_enacting": True,
        }
        return cls(
            target_kind=target_kind,
            target=target,
            posture=posture,
            rationale=rationale,
            evaluated_at=evaluated_at,
            evidence_refs=refs_t,
            non_enacting=True,
            posture_id=f"UCOS-SZON-{content_hash(core)[:16]}",
        )

    @classmethod
    def for_zone(
        cls,
        zone: SecurityZone,
        posture: RollupState,
        *,
        rationale: str,
        evaluated_at: int,
        evidence_refs: tuple[str, ...] | list[str] = (),
    ) -> PostureRecord:
        """Build a posture record for a canonical :class:`SecurityZone`."""
        if not isinstance(zone, SecurityZone):
            raise ZonePostureError("for_zone requires a SecurityZone")
        return cls.create(
            POSTURE_TARGET_ZONE,
            zone.value,
            posture,
            rationale=rationale,
            evaluated_at=evaluated_at,
            evidence_refs=evidence_refs,
        )

    @classmethod
    def for_control(
        cls,
        control: SecurityControl,
        posture: RollupState,
        *,
        rationale: str,
        evaluated_at: int,
        evidence_refs: tuple[str, ...] | list[str] = (),
    ) -> PostureRecord:
        """Build a posture record for a canonical :class:`SecurityControl`."""
        if not isinstance(control, SecurityControl):
            raise ZonePostureError("for_control requires a SecurityControl")
        return cls.create(
            POSTURE_TARGET_CONTROL,
            control.value,
            posture,
            rationale=rationale,
            evaluated_at=evaluated_at,
            evidence_refs=evidence_refs,
        )

    def validate(self) -> dict[str, Any]:
        """Re-affirm meta-validity (typed · identified · non-enacting)."""
        checks = {
            "typed": isinstance(self.posture, RollupState)
            and self.target_kind in (POSTURE_TARGET_ZONE, POSTURE_TARGET_CONTROL),
            "identified": self.posture_id.startswith("UCOS-SZON-"),
            "non_enacting": self.non_enacting is True,
        }
        if not all(checks.values()):
            failed = sorted(n for n, ok in checks.items() if not ok)
            raise ZonePostureError(
                "posture failed meta-validity", posture_id=self.posture_id, failed=",".join(failed)
            )
        return {"posture_id": self.posture_id, "meta_valid": True, "checks": checks}

    def trace(self) -> dict[str, Any]:
        """Return the traceability chain (backward UMB-015 · target · evidence refs)."""
        section = "UMB-015 §1" if self.target_kind == POSTURE_TARGET_ZONE else "UMB-015 §2"
        return {
            "posture_id": self.posture_id,
            "backward": {"target_kind": self.target_kind, "source_ref": section},
            "subject": {"target": self.target, "posture": self.posture.value},
            "evidence_refs": list(self.evidence_refs),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "posture_id": self.posture_id,
            "target_kind": self.target_kind,
            "target": self.target,
            "posture": self.posture.value,
            "rationale": self.rationale,
            "evaluated_at": self.evaluated_at,
            "evidence_refs": list(self.evidence_refs),
            "non_enacting": self.non_enacting,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class PostureLedger:
    """SEC-ZONE's deterministic, append-only posture record surface.

    Idempotent by ``posture_id``; queryable by target kind / target / posture. It
    exposes no ratify/enact/override operation (RG-02 / AR-04).
    """

    __slots__ = ("_entries", "_index")

    def __init__(self) -> None:
        self._entries: list[PostureRecord] = []
        self._index: dict[str, int] = {}

    def record(self, posture: PostureRecord) -> PostureRecord:
        if not isinstance(posture, PostureRecord):
            raise ZonePostureError("only a PostureRecord may be recorded")
        posture.validate()
        existing = self._index.get(posture.posture_id)
        if existing is not None:
            return self._entries[existing]
        self._index[posture.posture_id] = len(self._entries)
        self._entries.append(posture)
        return posture

    @property
    def postures(self) -> tuple[PostureRecord, ...]:
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, posture_id: str) -> bool:
        return posture_id in self._index

    def get(self, posture_id: str) -> PostureRecord:
        idx = self._index.get(posture_id)
        if idx is None:
            raise ZonePostureError("no such posture", posture_id=posture_id)
        return self._entries[idx]

    def by_kind(self, target_kind: str) -> tuple[PostureRecord, ...]:
        return tuple(p for p in self._entries if p.target_kind == target_kind)

    def by_target(self, target: str) -> tuple[PostureRecord, ...]:
        return tuple(p for p in self._entries if p.target == target)

    def by_posture(self, posture: RollupState) -> tuple[PostureRecord, ...]:
        return tuple(p for p in self._entries if p.posture is posture)

    def fingerprint(self) -> str:
        return content_hash([p.to_dict() for p in self._entries])

    def to_dict(self) -> dict[str, Any]:
        return {
            "posture_count": len(self._entries),
            "postures": [p.to_dict() for p in self._entries],
        }


@dataclass(frozen=True, slots=True)
class SecurityZoneEvidence:
    """A deterministic, content-addressed report over recorded postures (``UCOS-SZEV-``)."""

    ledger_fingerprint: str
    posture_count: int
    zones_assessed: int
    controls_assessed: int
    posture_counts: tuple[tuple[str, int], ...]
    postures: tuple[dict[str, Any], ...]
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        ledger_fingerprint: str,
        zones_assessed: int,
        controls_assessed: int,
        posture_counts: tuple[tuple[str, int], ...],
        postures: tuple[dict[str, Any], ...],
    ) -> SecurityZoneEvidence:
        core = {
            "ledger_fingerprint": ledger_fingerprint,
            "zones_assessed": zones_assessed,
            "controls_assessed": controls_assessed,
            "posture_counts": [list(pc) for pc in posture_counts],
            "postures": list(postures),
        }
        return cls(
            ledger_fingerprint=ledger_fingerprint,
            posture_count=len(postures),
            zones_assessed=zones_assessed,
            controls_assessed=controls_assessed,
            posture_counts=posture_counts,
            postures=postures,
            evidence_id=f"UCOS-SZEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "ledger_fingerprint": self.ledger_fingerprint,
            "posture_count": self.posture_count,
            "zones_assessed": self.zones_assessed,
            "controls_assessed": self.controls_assessed,
            "posture_counts": [list(pc) for pc in self.posture_counts],
            "postures": [dict(p) for p in self.postures],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class SecurityZoneService:
    """The governed SEC-ZONE composition root (assess · mutation-eval · trace · report)."""

    __slots__ = ("_ledger", "_events")

    def __init__(
        self,
        *,
        ledger: PostureLedger | None = None,
        events: EventBus | None = None,
    ) -> None:
        if ledger is not None and not isinstance(ledger, PostureLedger):
            raise SecurityZoneError("ledger must be a PostureLedger when provided")
        if events is not None and not isinstance(events, EventBus):
            raise SecurityZoneError("events must be an EventBus when provided")
        self._ledger = ledger if ledger is not None else PostureLedger()
        self._events = events

    @property
    def ledger(self) -> PostureLedger:
        return self._ledger

    # -- policy configuration (UMB-015 §1/§2; policy-configured, not compiled) ---

    def zone_policies(self) -> tuple[dict[str, Any], ...]:
        """The canonical five-zone policy configuration (default; extensible)."""
        return tuple(
            {
                "zone": z.value,
                "name": ZONE_NAME[z],
                "level": ZONE_LEVEL[z],
                "default_posture": ZONE_DEFAULT_POSTURE[z],
            }
            for z in all_security_zones()
        )

    def control_policies(self) -> tuple[dict[str, Any], ...]:
        """The canonical seven-control policy configuration (default; extensible)."""
        return tuple(
            {"control": c.value, "mechanism": CONTROL_MECHANISM[c]} for c in all_security_controls()
        )

    # -- assess (record-only) ---------------------------------------------------

    def assess(
        self,
        target_kind: str,
        target: str,
        posture: RollupState,
        *,
        rationale: str,
        evaluated_at: int,
        evidence_refs: tuple[str, ...] | list[str] = (),
    ) -> PostureRecord:
        """Record a posture against any target (canonical or free-form future one)."""
        record = PostureRecord.create(
            target_kind,
            target,
            posture,
            rationale=rationale,
            evaluated_at=evaluated_at,
            evidence_refs=evidence_refs,
        )
        recorded = self._ledger.record(record)
        self._emit(recorded)
        return recorded

    def assess_zone(
        self,
        zone: SecurityZone,
        posture: RollupState,
        *,
        rationale: str,
        evaluated_at: int,
        evidence_refs: tuple[str, ...] | list[str] = (),
    ) -> PostureRecord:
        """Record a posture for a canonical zone."""
        record = PostureRecord.for_zone(
            zone,
            posture,
            rationale=rationale,
            evaluated_at=evaluated_at,
            evidence_refs=evidence_refs,
        )
        recorded = self._ledger.record(record)
        self._emit(recorded)
        return recorded

    def assess_control(
        self,
        control: SecurityControl,
        posture: RollupState,
        *,
        rationale: str,
        evaluated_at: int,
        evidence_refs: tuple[str, ...] | list[str] = (),
    ) -> PostureRecord:
        """Record a posture for a canonical control."""
        record = PostureRecord.for_control(
            control,
            posture,
            rationale=rationale,
            evaluated_at=evaluated_at,
            evidence_refs=evidence_refs,
        )
        recorded = self._ledger.record(record)
        self._emit(recorded)
        return recorded

    # -- mutation-direction evaluation (decidable; enacts nothing) --------------

    def evaluate_mutation(self, source: SecurityZone, target: SecurityZone) -> dict[str, Any]:
        """Decide whether ``source`` may mutate ``target`` (UMB-INV-01; record-only)."""
        return zone_may_mutate(source, target)

    # -- trace + validate + report ----------------------------------------------

    def trace(self, posture_id: str) -> dict[str, Any]:
        return self._ledger.get(posture_id).trace()

    def validate(self, posture_id: str) -> dict[str, Any]:
        return self._ledger.get(posture_id).validate()

    def validate_all(self) -> dict[str, Any]:
        results = [p.validate() for p in self._ledger.postures]
        return {
            "posture_count": len(results),
            "meta_valid": all(r["meta_valid"] for r in results),
            "results": results,
        }

    def report(self) -> SecurityZoneEvidence:
        """Produce deterministic zone/control posture evidence (record-only)."""
        postures = self._ledger.postures
        canonical_zones = {z.value for z in all_security_zones()}
        canonical_controls = {c.value for c in all_security_controls()}
        zones_assessed = len(
            {
                p.target
                for p in postures
                if p.target_kind == POSTURE_TARGET_ZONE and p.target in canonical_zones
            }
        )
        controls_assessed = len(
            {
                p.target
                for p in postures
                if p.target_kind == POSTURE_TARGET_CONTROL and p.target in canonical_controls
            }
        )
        posture_counts = tuple(
            (state.value, sum(1 for p in postures if p.posture is state)) for state in RollupState
        )
        return SecurityZoneEvidence.create(
            ledger_fingerprint=self._ledger.fingerprint(),
            zones_assessed=zones_assessed,
            controls_assessed=controls_assessed,
            posture_counts=posture_counts,
            postures=tuple(p.to_dict() for p in postures),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone_policies": list(self.zone_policies()),
            "control_policies": list(self.control_policies()),
            "ledger": self._ledger.to_dict(),
            "evidence": self.report().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _emit(self, posture: PostureRecord) -> None:
        if self._events is None:
            return
        self._events.publish(
            POSTURE_RECORDED_EVENT,
            source="platform.security.zones",
            subject=posture.target,
            payload={"posture": posture.to_dict(), "enacts": False},
        )


def build_security_zone_service(*, events: EventBus | None = None) -> SecurityZoneService:
    """Default composition of the Zone & Control Posture Runtime (record-only)."""
    return SecurityZoneService(ledger=PostureLedger(), events=events)


__all__ = [
    "POSTURE_RECORDED_EVENT",
    "POSTURE_TARGET_ZONE",
    "POSTURE_TARGET_CONTROL",
    "zone_may_mutate",
    "PostureRecord",
    "PostureLedger",
    "SecurityZoneEvidence",
    "SecurityZoneService",
    "build_security_zone_service",
]
