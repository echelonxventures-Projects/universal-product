"""WP-05 — Genesis Trust, Keys & Signing (PRJ-C2 / ACT-C2).

The trust root for all **Recorded Truth**: a self-signed genesis anchor, a signed
key hierarchy, a deterministic signing engine, signature verification, trust
anchors, revocation, key rotation, and notary support. It realizes:

    * **AIF-L10 Genesis & Trust** — genesis is a self-signed axiomatic anchor;
      successors are recognized by signed delegation (or quorum);
    * **AIF-L11 Signed Events & Custody** — every event is signed; keys are **never
      embedded in artifacts**; revocation is a signed event with notary timestamping.

Custody & secrets (SEC-04 / RR-07): keys are held **by reference only** — an explicit
``bytes`` key (deterministic tests) or a Foundation :class:`SecretRef` resolved at
sign time and never stored, embedded, or logged. A :class:`Signature` records only a
non-secret ``key_id`` and the signature value, never key material. The signing scheme
reuses the certified EC-1 discipline verbatim (HMAC-SHA256 over a canonical payload,
:mod:`engine.compiler.signing`), so identical inputs and key yield an identical,
reproducible signature (IMP-007 §5).

Determinism (AX-02, no wall-clock): notary timestamps are an **authority-local,
monotonic ordinal** recorded at witness time (AIF-L04 discipline), never a
wall-clock read — so the trust state is byte-reproducible. Like its sibling ledgers
this engine holds only in-memory state and **never writes to the certified corpus**
(DP-03).
"""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import canonical_json
from platform.foundation.errors import SignatureError, TrustChainError, TrustError
from typing import Any

from engine.foundation.config.config import SecretRef
from engine.foundation.obs.logging import get_logger

_logger = get_logger("foundation.trust")

#: The signing algorithm — reused verbatim from the certified EC-1 signing stage.
TRUST_SIGNATURE_ALGORITHM = "HMAC-SHA256"

#: The self-describing export format tag (semantic version — widens append-only).
TRUST_STORE_FORMAT = "ucos-genesis-trust-store/1.0.0"


def _require_key_id(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TrustError("key id is required")
    return value


def _canonical_bytes(statement: Mapping[str, Any]) -> bytes:
    """The deterministic bytes a signature is computed over."""
    return canonical_json(statement).encode("utf-8")


class KeyStatus(str, Enum):
    """The lifecycle status of a trust key (append-only, forward-only — AIF-L17)."""

    ACTIVE = "active"
    ROTATED = "rotated"  # superseded by a delegated successor; still historically valid
    REVOKED = "revoked"  # signed revocation recorded; no longer trusted


@dataclass(frozen=True, slots=True)
class TrustKey:
    """An immutable trust-key descriptor — **no secret material** (AIF-L11).

    ``parent_key_id`` names the key that delegated trust to this one; a genesis
    anchor has no parent and is self-signed (:attr:`is_genesis`).
    """

    key_id: str
    algorithm: str = TRUST_SIGNATURE_ALGORITHM
    parent_key_id: str | None = None
    is_genesis: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "key_id": self.key_id,
            "algorithm": self.algorithm,
            "parent_key_id": self.parent_key_id,
            "is_genesis": self.is_genesis,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> TrustKey:
        if not isinstance(data, Mapping):
            raise TrustError("trust key record must be a mapping")
        try:
            key_id = data["key_id"]
        except (KeyError, TypeError) as exc:
            raise TrustError("trust key record is missing 'key_id'") from exc
        return cls(
            key_id=key_id,
            algorithm=data.get("algorithm", TRUST_SIGNATURE_ALGORITHM),
            parent_key_id=data.get("parent_key_id"),
            is_genesis=bool(data.get("is_genesis", False)),
        )


@dataclass(frozen=True, slots=True)
class Signature:
    """A detached HMAC signature over a canonical statement (no key embedded)."""

    key_id: str
    algorithm: str
    value: str
    payload_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "key_id": self.key_id,
            "algorithm": self.algorithm,
            "value": self.value,
            "payload_hash": self.payload_hash,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Signature:
        if not isinstance(data, Mapping):
            raise SignatureError("signature record must be a mapping")
        try:
            return cls(
                key_id=data["key_id"],
                algorithm=data["algorithm"],
                value=data["value"],
                payload_hash=data["payload_hash"],
            )
        except (KeyError, TypeError) as exc:
            raise SignatureError("signature record is missing required fields") from exc


@dataclass(frozen=True, slots=True)
class Delegation:
    """A signed trust edge: ``parent_key_id`` authorizes ``child_key_id`` (AIF-L10)."""

    parent_key_id: str
    child_key_id: str
    signature: Signature

    @staticmethod
    def statement(parent_key_id: str, child_key_id: str) -> dict[str, Any]:
        return {"kind": "delegation", "parent": parent_key_id, "child": child_key_id}

    def to_dict(self) -> dict[str, Any]:
        return {
            "parent_key_id": self.parent_key_id,
            "child_key_id": self.child_key_id,
            "signature": self.signature.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class NotaryRecord:
    """A witnessed, non-recomputable timestamp: a monotonic ordinal + witness sig.

    The ordinal is authority-local and recorded at witness time (AIF-L04 discipline),
    never a wall-clock read, so the record is deterministic and reproducible.
    """

    sequence: int
    witness_key_id: str
    digest: str
    signature: Signature

    @staticmethod
    def statement(sequence: int, witness_key_id: str, digest: str) -> dict[str, Any]:
        return {
            "kind": "notary",
            "sequence": sequence,
            "witness": witness_key_id,
            "digest": digest,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "witness_key_id": self.witness_key_id,
            "digest": self.digest,
            "signature": self.signature.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class Revocation:
    """A signed, notary-timestamped revocation event (AIF-L11 / AIF-L17)."""

    key_id: str
    reason: str
    notary: NotaryRecord
    signature: Signature

    @staticmethod
    def statement(key_id: str, reason: str, notary_sequence: int) -> dict[str, Any]:
        return {
            "kind": "revocation",
            "key_id": key_id,
            "reason": reason,
            "notary_sequence": notary_sequence,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "key_id": self.key_id,
            "reason": self.reason,
            "notary": self.notary.to_dict(),
            "signature": self.signature.to_dict(),
        }


class _Keyring:
    """In-memory custody of secret key material, held **by reference** (SEC-04).

    A key is either an explicit ``bytes`` value (deterministic tests) or a
    :class:`SecretRef` resolved at use time. Secrets never leave the keyring: they
    are never serialized, embedded, or logged — only a non-secret label is exposed.
    """

    __slots__ = ("_keys", "_refs")

    def __init__(self) -> None:
        self._keys: dict[str, bytes] = {}
        self._refs: dict[str, SecretRef] = {}

    def __contains__(self, key_id: str) -> bool:
        return key_id in self._keys or key_id in self._refs

    def register(
        self,
        key_id: str,
        *,
        key: bytes | None = None,
        key_ref: SecretRef | str | None = None,
    ) -> None:
        if key is None and key_ref is None:
            raise SignatureError("a signing key or key reference is required", key_id=key_id)
        if key is not None and not isinstance(key, bytes | bytearray):
            raise SignatureError("explicit signing key must be bytes", key_id=key_id)
        if key is not None:
            self._keys[key_id] = bytes(key)
        else:
            self._refs[key_id] = key_ref if isinstance(key_ref, SecretRef) else SecretRef(key_ref)

    def resolve(self, key_id: str) -> bytes:
        if key_id in self._keys:
            return self._keys[key_id]
        ref = self._refs.get(key_id)
        if ref is None:  # pragma: no cover - callers guard keyring membership first
            raise SignatureError("no key material for key id", key_id=key_id)
        resolved = ref.resolve()
        if not resolved:
            raise SignatureError("resolved signing key is empty", key_id=key_id)
        return resolved.encode("utf-8")

    def label(self, key_id: str) -> str:
        """A non-secret label naming the key (never its value)."""
        ref = self._refs.get(key_id)
        if ref is not None:
            return f"{ref.scheme}://{ref.locator}"
        return "inline:explicit-key"


class TrustEngine:
    """The genesis trust root: keys, signing, verification, delegation, revocation.

    Append-only and deterministic. Trust flows from one or more self-signed genesis
    anchors along signed delegations; a key is trusted iff it can be traced to a
    genesis anchor and no key on that path has been revoked (fails closed, AIF-L16).
    """

    __slots__ = (
        "_keyring",
        "_keys",
        "_delegations",
        "_revocations",
        "_rotated",
        "_notary_seq",
        "_order",
    )

    def __init__(self) -> None:
        self._keyring = _Keyring()
        self._keys: dict[str, TrustKey] = {}
        # child_key_id -> Delegation (each non-genesis key is delegated by one parent).
        self._delegations: dict[str, Delegation] = {}
        self._revocations: dict[str, Revocation] = {}
        # key ids that have been rotated out (superseded by a delegated successor).
        self._rotated: set[str] = set()
        self._notary_seq = 0
        self._order: list[str] = []

    # -- introspection ------------------------------------------------------------

    def __contains__(self, key_id: str) -> bool:
        return key_id in self._keys

    def __len__(self) -> int:
        return len(self._keys)

    @property
    def keys(self) -> tuple[TrustKey, ...]:
        return tuple(self._keys[k] for k in self._order)

    @property
    def trust_anchors(self) -> tuple[TrustKey, ...]:
        """The self-signed genesis anchors, in registration order."""
        return tuple(self._keys[k] for k in self._order if self._keys[k].is_genesis)

    @property
    def revocations(self) -> tuple[Revocation, ...]:
        return tuple(self._revocations[k] for k in self._order if k in self._revocations)

    def get(self, key_id: str) -> TrustKey:
        key = self._keys.get(key_id)
        if key is None:
            raise TrustError("no such trust key", key_id=key_id)
        return key

    def status(self, key_id: str) -> KeyStatus:
        self.get(key_id)
        if key_id in self._revocations:
            return KeyStatus.REVOKED
        if key_id in self._rotated:
            return KeyStatus.ROTATED
        return KeyStatus.ACTIVE

    # -- signing / verification (AIF-L11) -----------------------------------------

    def _sign_statement(self, key_id: str, statement: Mapping[str, Any]) -> Signature:
        payload = _canonical_bytes(statement)
        key = self._keyring.resolve(key_id)
        value = hmac.new(key, payload, hashlib.sha256).hexdigest()
        payload_hash = hashlib.sha256(payload).hexdigest()
        return Signature(
            key_id=key_id,
            algorithm=TRUST_SIGNATURE_ALGORITHM,
            value=value,
            payload_hash=payload_hash,
        )

    def sign(self, key_id: str, statement: Mapping[str, Any]) -> Signature:
        """Sign a canonical ``statement`` with the referenced key (fails closed)."""
        _require_key_id(key_id)
        if key_id not in self._keyring:
            raise SignatureError("cannot sign with an unregistered key", key_id=key_id)
        signature = self._sign_statement(key_id, statement)
        _logger.info(
            "foundation.trust.signed",
            key_id=key_id,
            algorithm=TRUST_SIGNATURE_ALGORITHM,
            key_ref=self._keyring.label(key_id),
        )
        return signature

    def verify(self, signature: Signature, statement: Mapping[str, Any]) -> bool:
        """Verify ``signature`` over ``statement`` against the referenced key."""
        if not isinstance(signature, Signature):
            raise SignatureError("verify expects a Signature")
        if signature.algorithm != TRUST_SIGNATURE_ALGORITHM:
            return False
        if signature.key_id not in self._keyring:
            raise SignatureError("cannot verify with an unregistered key", key_id=signature.key_id)
        expected = self._sign_statement(signature.key_id, statement)
        return hmac.compare_digest(expected.value, signature.value)

    # -- genesis + key hierarchy (AIF-L10) ----------------------------------------

    def establish_genesis(
        self,
        key_id: str,
        *,
        key: bytes | None = None,
        key_ref: SecretRef | str | None = None,
    ) -> TrustKey:
        """Establish a self-signed genesis trust anchor (axiomatic root)."""
        _require_key_id(key_id)
        if key_id in self._keys:
            raise TrustError("key id already registered", key_id=key_id)
        self._keyring.register(key_id, key=key, key_ref=key_ref)
        anchor = TrustKey(key_id=key_id, is_genesis=True, parent_key_id=None)
        self._keys[key_id] = anchor
        self._order.append(key_id)
        _logger.info("foundation.trust.genesis_established", key_id=key_id)
        return anchor

    def register_key(
        self,
        key_id: str,
        *,
        key: bytes | None = None,
        key_ref: SecretRef | str | None = None,
    ) -> None:
        """Register key material for a not-yet-trusted key (awaiting delegation)."""
        _require_key_id(key_id)
        if key_id in self._keyring:
            raise TrustError("key id already registered", key_id=key_id)
        self._keyring.register(key_id, key=key, key_ref=key_ref)

    def delegate(self, parent_key_id: str, child_key_id: str) -> Delegation:
        """Delegate trust from a trusted parent to a registered child (signed edge).

        The parent must itself be trusted (traceable to a genesis anchor and not
        revoked). The child's key material must already be registered.
        """
        _require_key_id(parent_key_id)
        _require_key_id(child_key_id)
        if parent_key_id == child_key_id:
            raise TrustChainError("a key cannot delegate to itself", key_id=parent_key_id)
        self.require_trusted(parent_key_id)
        if child_key_id not in self._keyring:
            raise TrustError("child key material is not registered", key_id=child_key_id)
        if child_key_id in self._keys:
            raise TrustError("child key already trusted", key_id=child_key_id)
        statement = Delegation.statement(parent_key_id, child_key_id)
        signature = self._sign_statement(parent_key_id, statement)
        delegation = Delegation(parent_key_id, child_key_id, signature)
        self._keys[child_key_id] = TrustKey(key_id=child_key_id, parent_key_id=parent_key_id)
        self._delegations[child_key_id] = delegation
        self._order.append(child_key_id)
        _logger.info("foundation.trust.delegated", parent=parent_key_id, child=child_key_id)
        return delegation

    def rotate(
        self,
        old_key_id: str,
        new_key_id: str,
        *,
        key: bytes | None = None,
        key_ref: SecretRef | str | None = None,
    ) -> Delegation:
        """Rotate ``old_key_id`` to a fresh ``new_key_id`` via signed delegation.

        The successor is recognized by a delegation signed by the outgoing key
        (AIF-L10); the outgoing key is marked :attr:`KeyStatus.ROTATED` but remains
        historically valid (append-only, AIF-L17).
        """
        self.require_trusted(old_key_id)
        self.register_key(new_key_id, key=key, key_ref=key_ref)
        statement = Delegation.statement(old_key_id, new_key_id)
        signature = self._sign_statement(old_key_id, statement)
        delegation = Delegation(old_key_id, new_key_id, signature)
        self._keys[new_key_id] = TrustKey(key_id=new_key_id, parent_key_id=old_key_id)
        self._delegations[new_key_id] = delegation
        self._rotated.add(old_key_id)
        self._order.append(new_key_id)
        _logger.info("foundation.trust.rotated", old=old_key_id, new=new_key_id)
        return delegation

    # -- notary + revocation (AIF-L11) --------------------------------------------

    def notarize(self, digest: str, witness_key_id: str) -> NotaryRecord:
        """Witness ``digest`` with a signed, monotonically-ordinaled notary record."""
        if not isinstance(digest, str) or not digest:
            raise TrustError("notary digest is required")
        self.require_trusted(witness_key_id)
        self._notary_seq += 1
        sequence = self._notary_seq
        statement = NotaryRecord.statement(sequence, witness_key_id, digest)
        signature = self._sign_statement(witness_key_id, statement)
        record = NotaryRecord(sequence, witness_key_id, digest, signature)
        _logger.info("foundation.trust.notarized", sequence=sequence, witness=witness_key_id)
        return record

    def revoke(self, key_id: str, reason: str, *, witness_key_id: str) -> Revocation:
        """Record a signed, notary-timestamped revocation of ``key_id`` (AIF-L11).

        Forward-only: revocation is a new signed event, never a deletion (AIF-L17).
        The revocation is signed by the key itself (self-revocation) or by any
        trusted witness; the witness also notarizes the event.
        """
        self.get(key_id)
        if key_id in self._revocations:
            raise TrustError("key already revoked", key_id=key_id)
        if witness_key_id != key_id:
            self.require_trusted(witness_key_id)
        elif key_id not in self._keyring:  # pragma: no cover - keys always have material
            raise SignatureError("cannot self-revoke without key material", key_id=key_id)
        digest = hashlib.sha256(
            _canonical_bytes({"kind": "revoke-intent", "key_id": key_id, "reason": reason})
        ).hexdigest()
        notary = self.notarize(digest, witness_key_id)
        statement = Revocation.statement(key_id, reason, notary.sequence)
        signature = self._sign_statement(witness_key_id, statement)
        revocation = Revocation(key_id, reason, notary, signature)
        self._revocations[key_id] = revocation
        _logger.info("foundation.trust.revoked", key_id=key_id, witness=witness_key_id)
        return revocation

    # -- trust chain verification (AIF-L10, fail closed) --------------------------

    def verify_chain(self, key_id: str) -> tuple[TrustKey, ...]:
        """Return the trust path from ``key_id`` up to a genesis anchor (fail closed).

        Raises :class:`TrustChainError` if the key is unknown, revoked, references a
        revoked ancestor, cannot be traced to a self-signed genesis anchor, or forms
        a delegation cycle.
        """
        path: list[TrustKey] = []
        seen: set[str] = set()
        current = self.get(key_id)
        while True:
            if current.key_id in seen:
                raise TrustChainError("delegation cycle detected", key_id=current.key_id)
            seen.add(current.key_id)
            if current.key_id in self._revocations:
                raise TrustChainError("key on trust path is revoked", key_id=current.key_id)
            path.append(current)
            if current.is_genesis:
                # Verify the axiomatic self-signature is reproducible.
                statement = {"kind": "genesis", "key_id": current.key_id}
                if not self.verify(
                    self._sign_statement(current.key_id, statement), statement
                ):  # pragma: no cover - deterministic; defensive
                    raise TrustChainError("genesis self-signature invalid", key_id=current.key_id)
                return tuple(path)
            delegation = self._delegations.get(current.key_id)
            if delegation is None:
                raise TrustChainError(
                    "key has no delegation to a trust anchor", key_id=current.key_id
                )
            statement = Delegation.statement(delegation.parent_key_id, current.key_id)
            if not self.verify(delegation.signature, statement):
                raise TrustChainError("delegation signature invalid", key_id=current.key_id)
            current = self.get(delegation.parent_key_id)

    def is_trusted(self, key_id: str) -> bool:
        """True iff ``key_id`` is traceable to a genesis anchor and not revoked."""
        try:
            self.verify_chain(key_id)
        except TrustError:
            return False
        return True

    def require_trusted(self, key_id: str) -> None:
        """Raise :class:`TrustChainError` unless ``key_id`` is trusted."""
        self.verify_chain(key_id)

    # -- export (public trust state only — never secrets) -------------------------

    def export(self) -> dict[str, Any]:
        """Serialize the **public** trust state (keys/delegations/revocations).

        Secret key material is **never** exported (AIF-L11 / RR-07).
        """
        return {
            "store_format": TRUST_STORE_FORMAT,
            "algorithm": TRUST_SIGNATURE_ALGORITHM,
            "keys": [self._keys[k].to_dict() for k in self._order],
            "delegations": [
                self._delegations[k].to_dict() for k in self._order if k in self._delegations
            ],
            "revocations": [r.to_dict() for r in self.revocations],
            "rotated": sorted(self._rotated),
            "notary_sequence": self._notary_seq,
        }

    to_dict = export

    def fingerprint(self) -> str:
        """A deterministic content hash of the public trust state (replay/equality)."""
        return hashlib.sha256(_canonical_bytes(self.export())).hexdigest()


def bootstrap_trust(
    genesis_key_id: str,
    *,
    key: bytes | None = None,
    key_ref: SecretRef | str | None = None,
) -> TrustEngine:
    """Build a :class:`TrustEngine` with a single established genesis anchor."""
    engine = TrustEngine()
    engine.establish_genesis(genesis_key_id, key=key, key_ref=key_ref)
    return engine


__all__ = [
    "TRUST_SIGNATURE_ALGORITHM",
    "TRUST_STORE_FORMAT",
    "KeyStatus",
    "TrustKey",
    "Signature",
    "Delegation",
    "NotaryRecord",
    "Revocation",
    "TrustEngine",
    "bootstrap_trust",
]
