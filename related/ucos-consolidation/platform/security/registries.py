"""EC2-CAP-SEC-001 / SEC-REG — Security Registry Runtime (the seven §17 registries).

The **Security Registry Runtime** (Phase 3) realizes the seven constitutional security
registries (ARCH-SECURITY-001 §17): **Security · Identity · Threat · Risk · Evidence ·
Certification · Trust**. Each is an **append-only, record-only, attributed, queryable**
store: every mutation is timestamped (a caller-supplied logical tick) and attributed
(a principal reference), and the store is queryable (RG-05). No registry **ever**
ratifies or enacts — there is structurally no ratify/enact/grant/revoke/override method
(RG-02 / AR-04; determination §8). **No eighth registry is introduced.**

A :class:`RegistryEntry` is an immutable, content-addressed (`UCOS-SREG-`) attributed
record. It stores *references* to platform constructs (e.g. a SEC-INTEL ``UCOS-SFND-``
finding, a SEC-CLASS ``UCOS-SCLS-`` classification, a trust anchor, a control id) — it
never duplicates their content and never writes to the frozen corpus (DP-03). It stores
**no** secret value (SEC-04 / RR-07).

Determinism (IMP-007 §5): entry ids and fingerprints are content-addressed; the same
records recorded in the same order at the same logical ticks yield the same registry
set and the same :class:`SecurityRegistryEvidence`.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.security.contracts import (
    REGISTRY_SOURCE,
    RegistryKind,
    all_registry_kinds,
)
from platform.security.errors import (
    RegistryValidationError,
    SecurityRegistryError,
)
from platform.security.intelligence import scan_for_secret
from typing import Any

#: The governed event emitted for every recorded registry entry (PC-16; RG-05).
REGISTRY_RECORDED_EVENT = "security.registry.recorded"


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    """An immutable, attributed, timestamped, non-enacting registry record (RG-05).

    Records that a ``subject_ref`` bears a ``record_type`` in a given ``registry``,
    optionally referencing other platform ids (``refs``) and carrying evaluative
    ``attributes`` (a sorted key/value mapping). ``recorded_by`` is a principal
    reference (attribution, by reference — no identity is created) and ``recorded_at``
    is a caller-supplied logical tick. ``non_enacting`` is invariantly ``True``.
    ``entry_id`` is content-addressed (``UCOS-SREG-``; deterministic).
    """

    registry: RegistryKind
    record_type: str
    subject_ref: str
    recorded_by: str
    recorded_at: int
    refs: tuple[str, ...] = ()
    attributes: tuple[tuple[str, str], ...] = ()
    non_enacting: bool = True
    entry_id: str = ""

    @classmethod
    def create(
        cls,
        registry: RegistryKind,
        record_type: str,
        subject_ref: str,
        *,
        recorded_by: str,
        recorded_at: int,
        refs: tuple[str, ...] | list[str] = (),
        attributes: dict[str, str] | None = None,
    ) -> RegistryEntry:
        """Build a registry entry with a deterministic id, fail-closed on any violation."""
        if not isinstance(registry, RegistryKind):
            raise SecurityRegistryError("registry must be a RegistryKind")
        if not isinstance(record_type, str) or not record_type.strip():
            raise SecurityRegistryError(
                "registry entry requires a non-empty record_type", registry=registry.value
            )
        if not isinstance(subject_ref, str) or not subject_ref.strip():
            raise SecurityRegistryError(
                "registry entry requires a non-empty subject_ref", registry=registry.value
            )
        # RG-05: every mutation is attributed and timestamped.
        if not isinstance(recorded_by, str) or not recorded_by.strip():
            raise SecurityRegistryError(
                "registry entry must be attributed (recorded_by principal reference)",
                registry=registry.value,
            )
        if not isinstance(recorded_at, int) or isinstance(recorded_at, bool):
            raise SecurityRegistryError(
                "registry entry must be timestamped with a logical tick (int)",
                registry=registry.value,
            )
        refs_t = tuple(refs)
        attrs = attributes or {}
        # Secret defense (SEC-04 / RR-07): no secret value may enter a registry.
        for value in (subject_ref, record_type, *refs_t, *attrs.keys(), *attrs.values()):
            if scan_for_secret(value):
                raise SecurityRegistryError(
                    "registry entry rejected: a field matched a secret pattern (RR-07)",
                    registry=registry.value,
                )
        attributes_t = tuple(sorted((str(k), str(v)) for k, v in attrs.items()))
        core = {
            "registry": registry.value,
            "record_type": record_type,
            "subject_ref": subject_ref,
            "recorded_by": recorded_by,
            "recorded_at": recorded_at,
            "refs": list(refs_t),
            "attributes": [list(a) for a in attributes_t],
            "non_enacting": True,
        }
        return cls(
            registry=registry,
            record_type=record_type,
            subject_ref=subject_ref,
            recorded_by=recorded_by,
            recorded_at=recorded_at,
            refs=refs_t,
            attributes=attributes_t,
            non_enacting=True,
            entry_id=f"UCOS-SREG-{content_hash(core)[:16]}",
        )

    def validate(self) -> dict[str, Any]:
        """Re-affirm meta-validity (typed · identified · attributed · timestamped · non-enacting).

        Raises :class:`RegistryValidationError` if any RG-05 invariant is violated.
        """
        timestamped = isinstance(self.recorded_at, int) and not isinstance(self.recorded_at, bool)
        checks = {
            "typed": isinstance(self.registry, RegistryKind),
            "identified": self.entry_id.startswith("UCOS-SREG-"),
            "attributed": bool(self.recorded_by and self.recorded_by.strip()),
            "timestamped": timestamped,
            "non_enacting": self.non_enacting is True,
        }
        if not all(checks.values()):
            failed = sorted(n for n, ok in checks.items() if not ok)
            raise RegistryValidationError(
                "registry entry failed meta-validity",
                entry_id=self.entry_id,
                failed=",".join(failed),
            )
        return {"entry_id": self.entry_id, "meta_valid": True, "checks": checks}

    def trace(self) -> dict[str, Any]:
        """Return the traceability chain (backward source · subject · referenced ids)."""
        return {
            "entry_id": self.entry_id,
            "backward": {
                "registry": self.registry.value,
                "source_ref": REGISTRY_SOURCE[self.registry],
            },
            "subject": {"subject_ref": self.subject_ref, "record_type": self.record_type},
            "refs": list(self.refs),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "registry": self.registry.value,
            "record_type": self.record_type,
            "subject_ref": self.subject_ref,
            "recorded_by": self.recorded_by,
            "recorded_at": self.recorded_at,
            "refs": list(self.refs),
            "attributes": [list(a) for a in self.attributes],
            "non_enacting": self.non_enacting,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class AppendOnlyRegistry:
    """A single append-only, record-only, queryable §17 registry (RG-02 / RG-05).

    Idempotent by ``entry_id`` (re-recording an identical entry returns the existing
    one; it never mutates or duplicates). It exposes **only** record + read/query
    operations — there is structurally no ratify/enact/grant/revoke/override/delete
    method (RG-02 / AR-04).
    """

    __slots__ = ("_kind", "_entries", "_index")

    def __init__(self, kind: RegistryKind) -> None:
        if not isinstance(kind, RegistryKind):
            raise SecurityRegistryError("registry kind must be a RegistryKind")
        self._kind = kind
        self._entries: list[RegistryEntry] = []
        self._index: dict[str, int] = {}

    @property
    def kind(self) -> RegistryKind:
        return self._kind

    def record(self, entry: RegistryEntry) -> RegistryEntry:
        """Append an entry (idempotent by id); returns the stored entry (fail-closed)."""
        if not isinstance(entry, RegistryEntry):
            raise SecurityRegistryError("only a RegistryEntry may be recorded")
        if entry.registry is not self._kind:
            raise SecurityRegistryError(
                "entry does not belong to this registry",
                registry=self._kind.value,
                entry_registry=entry.registry.value,
            )
        entry.validate()
        existing = self._index.get(entry.entry_id)
        if existing is not None:
            return self._entries[existing]
        self._index[entry.entry_id] = len(self._entries)
        self._entries.append(entry)
        return entry

    @property
    def entries(self) -> tuple[RegistryEntry, ...]:
        """An immutable snapshot of the append-only registry (in record order)."""
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, entry_id: str) -> bool:
        return entry_id in self._index

    def get(self, entry_id: str) -> RegistryEntry:
        """Return a recorded entry by id (raises if absent)."""
        idx = self._index.get(entry_id)
        if idx is None:
            raise SecurityRegistryError(
                "no such registry entry", registry=self._kind.value, entry_id=entry_id
            )
        return self._entries[idx]

    def by_record_type(self, record_type: str) -> tuple[RegistryEntry, ...]:
        """Every entry of ``record_type`` in record order (queryable)."""
        return tuple(e for e in self._entries if e.record_type == record_type)

    def by_subject(self, subject_ref: str) -> tuple[RegistryEntry, ...]:
        """Every entry recorded against ``subject_ref`` in record order."""
        return tuple(e for e in self._entries if e.subject_ref == subject_ref)

    def referencing(self, ref: str) -> tuple[RegistryEntry, ...]:
        """Every entry that references ``ref`` in record order."""
        return tuple(e for e in self._entries if ref in e.refs)

    def fingerprint(self) -> str:
        """A deterministic fingerprint over the ordered registry."""
        return content_hash([e.to_dict() for e in self._entries])

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry": self._kind.value,
            "entry_count": len(self._entries),
            "entries": [e.to_dict() for e in self._entries],
        }


class SecurityRegistrySet:
    """The seven §17 registries as one composed, append-only, record-only set.

    Holds exactly one :class:`AppendOnlyRegistry` per :class:`RegistryKind`; no eighth
    registry can be created. Exposes record + query only (RG-02).
    """

    __slots__ = ("_registries",)

    def __init__(self) -> None:
        self._registries: dict[RegistryKind, AppendOnlyRegistry] = {
            kind: AppendOnlyRegistry(kind) for kind in all_registry_kinds()
        }

    def registry(self, kind: RegistryKind) -> AppendOnlyRegistry:
        """Return the registry for ``kind`` (fail-closed on a bad kind)."""
        if not isinstance(kind, RegistryKind):
            raise SecurityRegistryError("registry kind must be a RegistryKind")
        return self._registries[kind]

    def record(self, entry: RegistryEntry) -> RegistryEntry:
        """Route an entry to its registry and append it (idempotent)."""
        if not isinstance(entry, RegistryEntry):
            raise SecurityRegistryError("only a RegistryEntry may be recorded")
        return self._registries[entry.registry].record(entry)

    @property
    def kinds(self) -> tuple[RegistryKind, ...]:
        return all_registry_kinds()

    def __len__(self) -> int:
        """Total number of entries across all seven registries."""
        return sum(len(r) for r in self._registries.values())

    def counts(self) -> tuple[tuple[str, int], ...]:
        """Per-registry entry counts in stable registry order (queryable)."""
        return tuple((kind.value, len(self._registries[kind])) for kind in all_registry_kinds())

    def fingerprint(self) -> str:
        """A deterministic fingerprint over all seven registries in stable order."""
        return content_hash([self._registries[kind].to_dict() for kind in all_registry_kinds()])

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_count": len(self._registries),
            "total_entries": len(self),
            "registries": [self._registries[kind].to_dict() for kind in all_registry_kinds()],
        }


@dataclass(frozen=True, slots=True)
class SecurityRegistryEvidence:
    """A deterministic, content-addressed report over all seven registries (``UCOS-SREV-``)."""

    set_fingerprint: str
    total_entries: int
    registry_counts: tuple[tuple[str, int], ...]
    registries: tuple[dict[str, Any], ...]
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        set_fingerprint: str,
        total_entries: int,
        registry_counts: tuple[tuple[str, int], ...],
        registries: tuple[dict[str, Any], ...],
    ) -> SecurityRegistryEvidence:
        core = {
            "set_fingerprint": set_fingerprint,
            "total_entries": total_entries,
            "registry_counts": [list(rc) for rc in registry_counts],
            "registries": list(registries),
        }
        return cls(
            set_fingerprint=set_fingerprint,
            total_entries=total_entries,
            registry_counts=registry_counts,
            registries=registries,
            evidence_id=f"UCOS-SREV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "set_fingerprint": self.set_fingerprint,
            "total_entries": self.total_entries,
            "registry_counts": [list(rc) for rc in self.registry_counts],
            "registries": [dict(r) for r in self.registries],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class SecurityRegistryService:
    """The governed SEC-REG composition root (record · query · trace · validate · report)."""

    __slots__ = ("_registries", "_events")

    def __init__(
        self,
        *,
        registries: SecurityRegistrySet | None = None,
        events: EventBus | None = None,
    ) -> None:
        if registries is not None and not isinstance(registries, SecurityRegistrySet):
            raise SecurityRegistryError("registries must be a SecurityRegistrySet when provided")
        if events is not None and not isinstance(events, EventBus):
            raise SecurityRegistryError("events must be an EventBus when provided")
        self._registries = registries if registries is not None else SecurityRegistrySet()
        self._events = events

    @property
    def registries(self) -> SecurityRegistrySet:
        return self._registries

    # -- record -----------------------------------------------------------------

    def record(
        self,
        registry: RegistryKind,
        record_type: str,
        subject_ref: str,
        *,
        recorded_by: str,
        recorded_at: int,
        refs: tuple[str, ...] | list[str] = (),
        attributes: dict[str, str] | None = None,
    ) -> RegistryEntry:
        """Build + append an attributed registry entry, emitting a governed event."""
        entry = RegistryEntry.create(
            registry,
            record_type,
            subject_ref,
            recorded_by=recorded_by,
            recorded_at=recorded_at,
            refs=refs,
            attributes=attributes,
        )
        recorded = self._registries.record(entry)
        self._emit(recorded)
        return recorded

    def record_entry(self, entry: RegistryEntry) -> RegistryEntry:
        """Append a pre-built entry (idempotent); emits a governed event."""
        if not isinstance(entry, RegistryEntry):
            raise SecurityRegistryError("only a RegistryEntry may be recorded")
        recorded = self._registries.record(entry)
        self._emit(recorded)
        return recorded

    # -- query + trace + validate + report --------------------------------------

    def query(
        self,
        registry: RegistryKind,
        *,
        record_type: str | None = None,
        subject_ref: str | None = None,
        ref: str | None = None,
    ) -> tuple[RegistryEntry, ...]:
        """Query one registry by record type / subject / reference (record-only)."""
        reg = self._registries.registry(registry)
        if record_type is not None:
            return reg.by_record_type(record_type)
        if subject_ref is not None:
            return reg.by_subject(subject_ref)
        if ref is not None:
            return reg.referencing(ref)
        return reg.entries

    def trace(self, registry: RegistryKind, entry_id: str) -> dict[str, Any]:
        """Return the traceability chain for a recorded entry."""
        return self._registries.registry(registry).get(entry_id).trace()

    def validate(self, registry: RegistryKind, entry_id: str) -> dict[str, Any]:
        """Re-affirm the meta-validity of a recorded entry (fail-closed)."""
        return self._registries.registry(registry).get(entry_id).validate()

    def validate_all(self) -> dict[str, Any]:
        """Validate every entry across all seven registries; aggregate decidable result."""
        results = [
            e.validate()
            for kind in self._registries.kinds
            for e in self._registries.registry(kind).entries
        ]
        return {
            "entry_count": len(results),
            "meta_valid": all(r["meta_valid"] for r in results),
            "results": results,
        }

    def report(self) -> SecurityRegistryEvidence:
        """Produce deterministic evidence over all seven registries (record-only)."""
        return SecurityRegistryEvidence.create(
            set_fingerprint=self._registries.fingerprint(),
            total_entries=len(self._registries),
            registry_counts=self._registries.counts(),
            registries=tuple(
                self._registries.registry(kind).to_dict() for kind in self._registries.kinds
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"registries": self._registries.to_dict(), "evidence": self.report().to_dict()}

    # -- internals --------------------------------------------------------------

    def _emit(self, entry: RegistryEntry) -> None:
        """Publish a governed ``security.registry.recorded`` event (if bound)."""
        if self._events is None:
            return
        self._events.publish(
            REGISTRY_RECORDED_EVENT,
            source="platform.security.registries",
            subject=entry.entry_id,
            payload={"entry": entry.to_dict(), "enacts": False},
        )


def build_security_registry_service(*, events: EventBus | None = None) -> SecurityRegistryService:
    """Default composition of the Security Registry Runtime (record-only)."""
    return SecurityRegistryService(registries=SecurityRegistrySet(), events=events)


__all__ = [
    "REGISTRY_RECORDED_EVENT",
    "RegistryEntry",
    "AppendOnlyRegistry",
    "SecurityRegistrySet",
    "SecurityRegistryEvidence",
    "SecurityRegistryService",
    "build_security_registry_service",
]
