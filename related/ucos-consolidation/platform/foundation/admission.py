"""WP-08 — Admission Key Binder (PRJ-C2 / ACT-C2).

Binds a path-independent **admission key** to a durable P2 identity under an
**admission authority** that owns a namespace and totally orders its own admissions.
It realizes:

    * **AIF-L06 Path-Independent Admission Key** — identity is keyed by
      ``(AuthorityID, local-key)``, decoupled from any path/name (rename stability);
    * **AIF-L07 Authority-Namespaced Uniqueness** — uniqueness by construction; a name
      or key never binds two identities (duplicate detection);
    * **AIF-L09 Authority = Serialization Domain** — one authority totally orders its
      own admissions; under partition it **blocks minting** or **delegates a
      sub-namespace**;
    * **AIF-L14 Atomic Admission** — an artifact exists only when its admission is
      **sealed** *and* its derived projection **re-verifies** (all-or-nothing; a
      failed projection aborts the mint, leaving no orphan identity).

Composition:
    * durable identities are minted through the WP-04
      :class:`~platform.foundation.durable_identity.IdentityRegistry` (prepare/commit/
      abort atomicity is reused directly);
    * authority migration is **witnessed** by the WP-05
      :class:`~platform.foundation.trust.TrustEngine` (a signed successor link),
      keeping already-minted identities immutable while re-homing namespace
      administration to the successor (A/G-AUTH continuity).

Deterministic and stdlib-only; nothing is written to the certified corpus (DP-03).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from platform.foundation.durable_identity import (
    AdmissionKey,
    DurableIdentity,
    IdentityRegistry,
)
from platform.foundation.errors import (
    AdmissionError,
    AuthorityBindingError,
    DuplicateAdmissionError,
)
from platform.foundation.trust import TrustEngine
from typing import Any

from engine.foundation.obs.logging import get_logger

_logger = get_logger("foundation.admission")

#: The self-describing export format tag (semantic version — widens append-only).
ADMISSION_LEDGER_FORMAT = "ucos-admission-ledger/1.0.0"

#: A pure projection verifier: given the minted identity, re-verify the derived
#: projection (and certification). Returning ``False`` aborts the admission (AIF-L14).
ProjectionVerifier = Callable[[DurableIdentity], bool]


class AuthorityStatus(str, Enum):
    """The lifecycle of an admission authority (AIF-L09 serialization domain)."""

    ACTIVE = "active"
    PARTITIONED = "partitioned"  # blocks minting until resumed (AIF-L09)
    MIGRATED = "migrated"  # administration handed to a signed successor


@dataclass(frozen=True, slots=True)
class AdmissionAuthority:
    """An authority that owns a namespace and serializes its own admissions."""

    authority_id: str
    status: AuthorityStatus = AuthorityStatus.ACTIVE
    successor_id: str | None = None
    parent_id: str | None = None  # set for a delegated sub-namespace (AIF-L09)

    def to_dict(self) -> dict[str, Any]:
        return {
            "authority_id": self.authority_id,
            "status": self.status.value,
            "successor_id": self.successor_id,
            "parent_id": self.parent_id,
        }


@dataclass(frozen=True, slots=True)
class AdmissionRecord:
    """A sealed admission: a logical name bound to a durable identity (AIF-L14)."""

    logical_name: str
    authority_id: str
    local_key: str
    urn: str
    opaque: str

    @property
    def admission_key(self) -> AdmissionKey:
        return AdmissionKey(authority_id=self.authority_id, local_key=self.local_key)

    def to_dict(self) -> dict[str, Any]:
        return {
            "logical_name": self.logical_name,
            "authority_id": self.authority_id,
            "local_key": self.local_key,
            "urn": self.urn,
            "opaque": self.opaque,
        }


@dataclass(frozen=True, slots=True)
class AuthorityMigration:
    """A witnessed authority-migration event (AIF-L09 / A/G-AUTH)."""

    old_authority_id: str
    new_authority_id: str
    witness_key_id: str

    @staticmethod
    def statement(old_authority_id: str, new_authority_id: str) -> dict[str, Any]:
        return {
            "kind": "authority-migration",
            "old": old_authority_id,
            "new": new_authority_id,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "old_authority_id": self.old_authority_id,
            "new_authority_id": self.new_authority_id,
            "witness_key_id": self.witness_key_id,
        }


class AdmissionBinder:
    """Binds admission keys to durable identities under namespaced authorities (WP-08).

    Append-only and deterministic. An authority owns its namespace exclusively; an
    admission atomically mints (or reuses) the durable identity and binds a logical
    name to it, with duplicate detection on both name and key and rename stability.
    """

    __slots__ = ("_identities", "_trust", "_authorities", "_by_name", "_by_key", "_order")

    def __init__(
        self,
        identity_registry: IdentityRegistry | None = None,
        *,
        trust: TrustEngine | None = None,
    ) -> None:
        self._identities = (
            identity_registry if identity_registry is not None else IdentityRegistry()
        )
        self._trust = trust
        self._authorities: dict[str, AdmissionAuthority] = {}
        # logical_name -> AdmissionRecord
        self._by_name: dict[str, AdmissionRecord] = {}
        # admission-key render -> logical_name (path-independent reverse index)
        self._by_key: dict[str, str] = {}
        self._order: list[str] = []

    # -- introspection ------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._order)

    def __contains__(self, logical_name: str) -> bool:
        return logical_name in self._by_name

    @property
    def identities(self) -> IdentityRegistry:
        return self._identities

    @property
    def authorities(self) -> tuple[AdmissionAuthority, ...]:
        return tuple(self._authorities[a] for a in sorted(self._authorities))

    @property
    def records(self) -> tuple[AdmissionRecord, ...]:
        return tuple(self._by_name[n] for n in self._order)

    # -- namespace ownership (AIF-L07) --------------------------------------------

    def register_authority(self, authority_id: str) -> AdmissionAuthority:
        """Register an authority that exclusively owns its namespace (unique id)."""
        if not isinstance(authority_id, str) or not authority_id.strip():
            raise AuthorityBindingError("authority id is required")
        if authority_id in self._authorities:
            raise AuthorityBindingError("authority already registered", authority_id=authority_id)
        authority = AdmissionAuthority(authority_id=authority_id)
        self._authorities[authority_id] = authority
        _logger.info("foundation.admission.authority_registered", authority_id=authority_id)
        return authority

    def authority(self, authority_id: str) -> AdmissionAuthority:
        authority = self._authorities.get(authority_id)
        if authority is None:
            raise AuthorityBindingError("no such authority", authority_id=authority_id)
        return authority

    def _require_mintable(self, authority_id: str) -> AdmissionAuthority:
        authority = self.authority(authority_id)
        if authority.status is AuthorityStatus.PARTITIONED:
            raise AuthorityBindingError(
                "authority is partitioned; minting is blocked (AIF-L09)",
                authority_id=authority_id,
            )
        if authority.status is AuthorityStatus.MIGRATED:
            raise AuthorityBindingError(
                "authority is migrated; mint under its successor",
                authority_id=authority_id,
                successor_id=authority.successor_id,
            )
        return authority

    # -- atomic admission (AIF-L14) -----------------------------------------------

    def admit(
        self,
        authority_id: str,
        local_key: str,
        logical_name: str,
        *,
        verify_projection: ProjectionVerifier | None = None,
    ) -> AdmissionRecord:
        """Atomically admit an artifact: mint its identity and bind a logical name.

        All-or-nothing (AIF-L14): the identity is prepared, the derived projection is
        re-verified (``verify_projection``), and only then is the mint committed and
        the name bound. If projection verification fails (returns ``False`` or
        raises) the mint is aborted, leaving no orphan identity. Idempotent for an
        identical ``(authority, local_key, logical_name)`` triple.
        """
        if not isinstance(logical_name, str) or not logical_name.strip():
            raise AdmissionError("logical name is required")
        self._require_mintable(authority_id)
        key = AdmissionKey(authority_id=authority_id, local_key=local_key)
        ref = key.render

        # Idempotent re-admission of the exact same triple.
        existing_name = self._by_key.get(ref)
        if existing_name is not None:
            if existing_name == logical_name:
                return self._by_name[existing_name]
            raise DuplicateAdmissionError(
                "admission key already bound to a different logical name",
                admission_key=ref,
                bound_name=existing_name,
            )
        if logical_name in self._by_name:
            raise DuplicateAdmissionError(
                "logical name already admitted", logical_name=logical_name
            )

        mint = self._identities.prepare(authority_id, local_key)
        try:
            if verify_projection is not None and not verify_projection(mint.identity):
                raise AdmissionError(
                    "derived projection failed to re-verify (admission aborted)",
                    logical_name=logical_name,
                )
        except BaseException:
            # Atomicity: any failure discards the provisional mint (no orphan).
            self._identities.abort(mint)
            raise
        identity = self._identities.commit(mint)
        record = AdmissionRecord(
            logical_name=logical_name,
            authority_id=identity.authority_id,
            local_key=identity.local_key,
            urn=identity.urn,
            opaque=identity.opaque,
        )
        self._by_name[logical_name] = record
        self._by_key[ref] = logical_name
        self._order.append(logical_name)
        _logger.info(
            "foundation.admission.admitted",
            logical_name=logical_name,
            authority_id=authority_id,
            urn=identity.urn,
        )
        return record

    # -- rename stability (AIF-L06) -----------------------------------------------

    def rename(self, logical_name: str, new_logical_name: str) -> AdmissionRecord:
        """Rebind a logical name; the admission key and identity are **unchanged**.

        Realizes path independence (AIF-L06): renaming an artifact never re-mints or
        changes its durable identity — only the name→identity binding moves.
        """
        if not isinstance(new_logical_name, str) or not new_logical_name.strip():
            raise AdmissionError("new logical name is required")
        record = self.resolve(logical_name)
        if new_logical_name == logical_name:
            return record
        if new_logical_name in self._by_name:
            raise DuplicateAdmissionError(
                "target logical name already admitted", logical_name=new_logical_name
            )
        renamed = AdmissionRecord(
            logical_name=new_logical_name,
            authority_id=record.authority_id,
            local_key=record.local_key,
            urn=record.urn,
            opaque=record.opaque,
        )
        del self._by_name[logical_name]
        self._by_name[new_logical_name] = renamed
        self._by_key[record.admission_key.render] = new_logical_name
        self._order[self._order.index(logical_name)] = new_logical_name
        _logger.info("foundation.admission.renamed", old=logical_name, new=new_logical_name)
        return renamed

    # -- resolution (fails closed — AIF-L16) --------------------------------------

    def resolve(self, logical_name: str) -> AdmissionRecord:
        record = self._by_name.get(logical_name)
        if record is None:
            raise AdmissionError("no admission for logical name", logical_name=logical_name)
        return record

    def resolve_by_key(self, authority_id: str, local_key: str) -> AdmissionRecord:
        ref = AdmissionKey(authority_id=authority_id, local_key=local_key).render
        name = self._by_key.get(ref)
        if name is None:
            raise AdmissionError("no admission for admission key", admission_key=ref)
        return self._by_name[name]

    def is_admitted(self, authority_id: str, local_key: str) -> bool:
        ref = AdmissionKey(authority_id=authority_id, local_key=local_key).render
        return ref in self._by_key

    # -- partition + sub-namespace delegation (AIF-L09) ---------------------------

    def partition(self, authority_id: str) -> AdmissionAuthority:
        """Mark an authority partitioned — new minting is blocked (AIF-L09)."""
        authority = self.authority(authority_id)
        if authority.status is AuthorityStatus.MIGRATED:
            raise AuthorityBindingError(
                "cannot partition a migrated authority", authority_id=authority_id
            )
        updated = AdmissionAuthority(
            authority_id=authority_id,
            status=AuthorityStatus.PARTITIONED,
            successor_id=authority.successor_id,
            parent_id=authority.parent_id,
        )
        self._authorities[authority_id] = updated
        return updated

    def resume(self, authority_id: str) -> AdmissionAuthority:
        """Clear a partition, restoring the authority to ACTIVE."""
        authority = self.authority(authority_id)
        if authority.status is not AuthorityStatus.PARTITIONED:
            raise AuthorityBindingError("authority is not partitioned", authority_id=authority_id)
        restored = AdmissionAuthority(authority_id=authority_id, parent_id=authority.parent_id)
        self._authorities[authority_id] = restored
        return restored

    def delegate_subnamespace(
        self, parent_authority_id: str, child_authority_id: str
    ) -> AdmissionAuthority:
        """Delegate a sub-namespace to a child authority (AIF-L09 partition relief)."""
        self.authority(parent_authority_id)
        if child_authority_id in self._authorities:
            raise AuthorityBindingError(
                "child authority already registered", authority_id=child_authority_id
            )
        child = AdmissionAuthority(authority_id=child_authority_id, parent_id=parent_authority_id)
        self._authorities[child_authority_id] = child
        _logger.info(
            "foundation.admission.subnamespace_delegated",
            parent=parent_authority_id,
            child=child_authority_id,
        )
        return child

    # -- witnessed authority migration (AIF-L09 / A/G-AUTH) -----------------------

    def migrate_authority(
        self, old_authority_id: str, new_authority_id: str, *, witness_key_id: str
    ) -> AuthorityMigration:
        """Migrate namespace administration to a successor under a signed witness.

        Requires a :class:`TrustEngine` (WP-05): the migration statement is signed by
        a trusted witness key. Already-minted identities are **immutable** and remain
        valid (their P2 keeps its original authority); the old authority is marked
        MIGRATED (its minting is blocked) and points at its successor. New admissions
        go under the successor authority.
        """
        if self._trust is None:
            raise AuthorityBindingError("authority migration requires a TrustEngine")
        old = self.authority(old_authority_id)
        if old.status is AuthorityStatus.MIGRATED:
            raise AuthorityBindingError("authority already migrated", authority_id=old_authority_id)
        self.authority(new_authority_id)  # successor must be registered
        self._trust.require_trusted(witness_key_id)
        statement = AuthorityMigration.statement(old_authority_id, new_authority_id)
        signature = self._trust.sign(witness_key_id, statement)
        if not self._trust.verify(signature, statement):  # pragma: no cover - deterministic
            raise AuthorityBindingError("migration signature failed to verify")
        migrated = AdmissionAuthority(
            authority_id=old_authority_id,
            status=AuthorityStatus.MIGRATED,
            successor_id=new_authority_id,
            parent_id=old.parent_id,
        )
        self._authorities[old_authority_id] = migrated
        _logger.info(
            "foundation.admission.authority_migrated",
            old=old_authority_id,
            new=new_authority_id,
            witness=witness_key_id,
        )
        return AuthorityMigration(old_authority_id, new_authority_id, witness_key_id)

    # -- export -------------------------------------------------------------------

    def export(self) -> dict[str, Any]:
        """Serialize the admission ledger to a deterministic, self-describing dict."""
        return {
            "ledger_format": ADMISSION_LEDGER_FORMAT,
            "authorities": [a.to_dict() for a in self.authorities],
            "records": [self._by_name[n].to_dict() for n in self._order],
        }

    to_dict = export


__all__ = [
    "ADMISSION_LEDGER_FORMAT",
    "ProjectionVerifier",
    "AuthorityStatus",
    "AdmissionAuthority",
    "AdmissionRecord",
    "AuthorityMigration",
    "AdmissionBinder",
]
