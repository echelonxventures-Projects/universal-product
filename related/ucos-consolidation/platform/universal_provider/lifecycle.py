"""UPA-000007 — Provider Lifecycle (Terminal-04).

Provider state changes only here, only along a declared transition, and only with an
appended, hash-chained ledger entry (PC-10). There is no other way to move a provider,
which is what makes "no provider serves a consumer before certification" (PC-11) a
structural property rather than a convention: :data:`ProviderPhase.ACTIVE` is
reachable only from ``CERTIFIED`` or ``SUSPENDED``, and ``CERTIFIED`` only from
``VALIDATED``.

    * :class:`ProviderPhase` — the nine lifecycle phases.
    * :data:`LIFECYCLE_TRANSITIONS` — the complete legal transition map.
    * :class:`LifecycleEntry` — one immutable, hash-chained transition record.
    * :class:`ProviderLifecycle` — the lifecycle authority and its ledger.

The ledger is append-only and tamper-evident: each entry hashes its own content
together with the previous entry's hash, so any retroactive edit to provider history
breaks the chain and :meth:`ProviderLifecycle.verify` returns ``False``. The lifecycle
holds no wall-clock — ordering is by monotonic sequence — so a lifecycle replayed from
identical transitions produces an identical chain.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from platform.universal_provider.contracts import canonical_json, content_hash
from platform.universal_provider.errors import ProviderLifecycleError
from typing import Any

#: Semantic version of the Provider Lifecycle contract surface.
PROVIDER_LIFECYCLE_VERSION = "1.0.0"

#: The genesis link of the lifecycle hash chain.
GENESIS_HASH = "0" * 64


class ProviderPhase(str, Enum):
    """The lifecycle phases a provider passes through.

    * ``DECLARED``   — a descriptor exists; nothing has been accepted yet.
    * ``REGISTERED`` — accepted by the registration authority; discoverable.
    * ``VALIDATED``  — every constitutional gate has been executed and passed.
    * ``CERTIFIED``  — a certificate has been issued over that validation.
    * ``ACTIVE``     — permitted to serve consumers. Requires certification.
    * ``SUSPENDED``  — temporarily withdrawn from service; reinstatable.
    * ``DEPRECATED`` — superseded; still serving, no longer recommended.
    * ``RETIRED``    — permanently withdrawn. Terminal.
    * ``REJECTED``   — refused admission. Terminal.
    """

    DECLARED = "declared"
    REGISTERED = "registered"
    VALIDATED = "validated"
    CERTIFIED = "certified"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    REJECTED = "rejected"


#: The complete legal transition map. Anything absent from this map is refused
#: (PC-07): the lifecycle has no permissive default.
LIFECYCLE_TRANSITIONS: Mapping[ProviderPhase, frozenset[ProviderPhase]] = {
    ProviderPhase.DECLARED: frozenset({ProviderPhase.REGISTERED, ProviderPhase.REJECTED}),
    ProviderPhase.REGISTERED: frozenset(
        {ProviderPhase.VALIDATED, ProviderPhase.REJECTED, ProviderPhase.RETIRED}
    ),
    ProviderPhase.VALIDATED: frozenset(
        {ProviderPhase.CERTIFIED, ProviderPhase.REJECTED, ProviderPhase.RETIRED}
    ),
    ProviderPhase.CERTIFIED: frozenset(
        {
            ProviderPhase.ACTIVE,
            ProviderPhase.SUSPENDED,
            ProviderPhase.DEPRECATED,
            ProviderPhase.RETIRED,
        }
    ),
    ProviderPhase.ACTIVE: frozenset(
        {ProviderPhase.SUSPENDED, ProviderPhase.DEPRECATED, ProviderPhase.RETIRED}
    ),
    ProviderPhase.SUSPENDED: frozenset(
        {ProviderPhase.ACTIVE, ProviderPhase.DEPRECATED, ProviderPhase.RETIRED}
    ),
    ProviderPhase.DEPRECATED: frozenset({ProviderPhase.SUSPENDED, ProviderPhase.RETIRED}),
    ProviderPhase.RETIRED: frozenset(),
    ProviderPhase.REJECTED: frozenset(),
}

#: Phases from which a provider may serve a consumer.
SERVING_PHASES: frozenset[ProviderPhase] = frozenset(
    {ProviderPhase.ACTIVE, ProviderPhase.DEPRECATED}
)

#: Terminal phases — no transition leaves them.
TERMINAL_PHASES: frozenset[ProviderPhase] = frozenset(
    {ProviderPhase.RETIRED, ProviderPhase.REJECTED}
)


def coerce_phase(phase: ProviderPhase | str) -> ProviderPhase:
    """Return ``phase`` as a :class:`ProviderPhase`, failing closed (PC-07)."""
    if isinstance(phase, ProviderPhase):
        return phase
    try:
        return ProviderPhase(str(phase).strip().lower())
    except ValueError as exc:
        raise ProviderLifecycleError(
            "unknown lifecycle phase",
            {"phase": repr(phase), "known": [p.value for p in ProviderPhase]},
        ) from exc


@dataclass(frozen=True, slots=True)
class LifecycleEntry:
    """One immutable, hash-chained lifecycle transition record (PC-10)."""

    sequence: int
    qualified_id: str
    from_phase: ProviderPhase
    to_phase: ProviderPhase
    reason: str
    evidence_ref: str
    previous_hash: str
    entry_hash: str

    def payload(self) -> dict[str, Any]:
        """Return the content the entry hash is computed over."""
        return {
            "sequence": self.sequence,
            "qualified_id": self.qualified_id,
            "from_phase": self.from_phase.value,
            "to_phase": self.to_phase.value,
            "reason": self.reason,
            "evidence_ref": self.evidence_ref,
            "previous_hash": self.previous_hash,
        }

    def recompute_hash(self) -> str:
        """Recompute this entry's hash from its own content plus the chain link."""
        return content_hash(self.payload())

    def to_dict(self) -> dict[str, Any]:
        return {**self.payload(), "entry_hash": self.entry_hash}


class ProviderLifecycle:
    """The lifecycle authority: the only path to provider state (PC-10).

    Keyed by version-pinned ``provider_id@version``, so lifecycle state can never
    leak across versions of the same provider — activating 2.0.0 does not activate
    1.4.0, and retiring 1.4.0 does not retire 2.0.0.
    """

    def __init__(self) -> None:
        self._phases: dict[str, ProviderPhase] = {}
        self._entries: list[LifecycleEntry] = []

    # ------------------------------------------------------------------- admission

    def declare(self, qualified_id: str) -> ProviderPhase:
        """Enter ``qualified_id`` into the lifecycle at :attr:`ProviderPhase.DECLARED`.

        Idempotent for an already-tracked provider: re-declaring does not reset
        state, because resetting state would be an ungoverned mutation (PC-10).
        """
        key = self._require_key(qualified_id)
        if key not in self._phases:
            self._phases[key] = ProviderPhase.DECLARED
        return self._phases[key]

    def tracks(self, qualified_id: str) -> bool:
        return self._require_key(qualified_id) in self._phases

    def phase(self, qualified_id: str) -> ProviderPhase:
        """Return the current phase, failing closed for an untracked provider."""
        key = self._require_key(qualified_id)
        current = self._phases.get(key)
        if current is None:
            raise ProviderLifecycleError(
                "provider is not tracked by the lifecycle authority",
                {"qualified_id": key},
            )
        return current

    # ------------------------------------------------------------------ transitions

    def can_transition(self, qualified_id: str, to_phase: ProviderPhase | str) -> bool:
        """Whether the transition is legal, without attempting it."""
        target = coerce_phase(to_phase)
        try:
            current = self.phase(qualified_id)
        except ProviderLifecycleError:
            return False
        return target in LIFECYCLE_TRANSITIONS[current]

    def transition(
        self,
        qualified_id: str,
        to_phase: ProviderPhase | str,
        *,
        reason: str = "",
        evidence_ref: str = "",
    ) -> LifecycleEntry:
        """Move a provider along a **declared** transition and append to the ledger.

        Refuses an untracked provider, a terminal-phase departure, and any transition
        absent from :data:`LIFECYCLE_TRANSITIONS`. The refusal is the enforcement
        point for PC-11: there is no edge into ``ACTIVE`` that does not pass through
        ``CERTIFIED``.
        """
        key = self._require_key(qualified_id)
        current = self.phase(key)
        target = coerce_phase(to_phase)
        allowed = LIFECYCLE_TRANSITIONS[current]
        if target not in allowed:
            raise ProviderLifecycleError(
                "illegal lifecycle transition (PC-10)",
                {
                    "qualified_id": key,
                    "from_phase": current.value,
                    "to_phase": target.value,
                    "allowed": sorted(phase.value for phase in allowed),
                    "terminal": current in TERMINAL_PHASES,
                },
            )
        previous_hash = self.head_hash
        sequence = len(self._entries) + 1
        payload = {
            "sequence": sequence,
            "qualified_id": key,
            "from_phase": current.value,
            "to_phase": target.value,
            "reason": reason,
            "evidence_ref": evidence_ref,
            "previous_hash": previous_hash,
        }
        entry = LifecycleEntry(
            sequence=sequence,
            qualified_id=key,
            from_phase=current,
            to_phase=target,
            reason=reason,
            evidence_ref=evidence_ref,
            previous_hash=previous_hash,
            entry_hash=content_hash(payload),
        )
        self._entries.append(entry)
        self._phases[key] = target
        return entry

    # ---------------------------------------------------------------------- queries

    def may_serve(self, qualified_id: str) -> bool:
        """Whether this provider is permitted to serve a consumer (PC-11)."""
        try:
            return self.phase(qualified_id) in SERVING_PHASES
        except ProviderLifecycleError:
            return False

    def require_serving(self, qualified_id: str) -> ProviderPhase:
        """Return the phase if the provider may serve, else refuse (PC-11 / PC-07)."""
        current = self.phase(qualified_id)
        if current not in SERVING_PHASES:
            raise ProviderLifecycleError(
                "provider may not serve consumers in its current phase (PC-11)",
                {
                    "qualified_id": self._require_key(qualified_id),
                    "phase": current.value,
                    "serving_phases": sorted(phase.value for phase in SERVING_PHASES),
                },
            )
        return current

    def in_phase(self, phase: ProviderPhase | str) -> tuple[str, ...]:
        """Return the tracked providers currently in ``phase``, id-ordered."""
        target = coerce_phase(phase)
        return tuple(sorted(key for key, value in self._phases.items() if value is target))

    def serving(self) -> tuple[str, ...]:
        """Return every provider currently permitted to serve, id-ordered."""
        return tuple(sorted(key for key, value in self._phases.items() if value in SERVING_PHASES))

    def history(self, qualified_id: str) -> tuple[LifecycleEntry, ...]:
        """Return the transition history for one provider, in sequence order."""
        key = self._require_key(qualified_id)
        return tuple(entry for entry in self._entries if entry.qualified_id == key)

    def phases(self) -> dict[str, str]:
        """Return the deterministic snapshot of every tracked provider's phase."""
        return {key: self._phases[key].value for key in sorted(self._phases)}

    # ----------------------------------------------------------------------- ledger

    @property
    def entries(self) -> tuple[LifecycleEntry, ...]:
        return tuple(self._entries)

    @property
    def head_hash(self) -> str:
        """Return the hash of the most recent entry, or the genesis link."""
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    def __len__(self) -> int:
        return len(self._entries)

    def verify(self) -> bool:
        """Whether the transition chain is intact and correctly linked."""
        previous = GENESIS_HASH
        for index, entry in enumerate(self._entries, start=1):
            if entry.sequence != index or entry.previous_hash != previous:
                return False
            if entry.recompute_hash() != entry.entry_hash:
                return False
            previous = entry.entry_hash
        return True

    def require_intact(self) -> None:
        """Raise unless the ledger chain verifies (PC-10)."""
        if not self.verify():
            raise ProviderLifecycleError(
                "provider lifecycle ledger integrity check failed",
                {"entries": len(self._entries), "head_hash": self.head_hash},
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "lifecycle_version": PROVIDER_LIFECYCLE_VERSION,
            "phases": self.phases(),
            "head_hash": self.head_hash,
            "entries": [entry.to_dict() for entry in self._entries],
        }

    def ledger_hash(self) -> str:
        return content_hash(self.to_dict())

    def canonical(self) -> str:
        """Return the canonical JSON encoding of the whole lifecycle."""
        return canonical_json(self.to_dict())

    @staticmethod
    def _require_key(qualified_id: str) -> str:
        if not isinstance(qualified_id, str) or not qualified_id.strip():
            raise ProviderLifecycleError(
                "a lifecycle key must be a non-empty 'provider_id@version' string",
                {"qualified_id": repr(qualified_id)},
            )
        key = qualified_id.strip()
        if "@" not in key:
            raise ProviderLifecycleError(
                "lifecycle state is version-pinned; expected 'provider_id@version'",
                {"qualified_id": key},
            )
        return key


__all__ = [
    "GENESIS_HASH",
    "LIFECYCLE_TRANSITIONS",
    "PROVIDER_LIFECYCLE_VERSION",
    "SERVING_PHASES",
    "TERMINAL_PHASES",
    "LifecycleEntry",
    "ProviderLifecycle",
    "ProviderPhase",
    "coerce_phase",
]
