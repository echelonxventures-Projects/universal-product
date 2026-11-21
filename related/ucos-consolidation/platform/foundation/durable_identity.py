"""WP-04 — P2 Durable Identity Minting (PRJ-C2 / ACT-C2).

The authoritative minting layer for **P2 durable identities** — the opaque,
minted-once, immutable, authority-namespaced identity every artifact carries. It
realizes:

    * **AIF-L02 Opaque Durable Identity (P2)** — one minted-once, immutable, opaque,
      authority-namespaced identity per artifact; never content/order/path-derived;
      never reused;
    * **AIF-L06 Path-Independent Admission Key** — identity is keyed by
      ``(AuthorityID, local-key)``, decoupled from any path;
    * **AIF-L07 Authority-Namespaced Uniqueness** — global uniqueness *by
      construction* from the namespaced admission key, with no global coordination;
    * **AIF-L13 Prepare/Commit/Abort Atomicity** — a mint is provisional until it is
      sealed; abort discards it leaving no orphan identity; commit seals atomically;
      retry is idempotent;
    * **AIF-L16 Deterministic Identity Decision** — allocation is a pure function of
      the admission key and every lookup fails closed on ambiguity.

Design (IMP-007 §5 determinism; AX-01/AX-02 bifurcation of truth):
    * A :class:`DurableIdentity` is **Recorded Truth**: immutable, opaque, and keyed
      by its authority-namespaced admission key. Its opaque 128-bit value is a
      deterministic function **of the admission key alone** — never of the artifact's
      content, its admission order, or its path — so the same admission key always
      mints the same identity (idempotent retry) while distinct admission keys are
      globally unique by construction.
    * :class:`IdentityRegistry` is append-only: it exposes no update or delete. A
      mint is ``prepare``-d (provisional), then ``commit``-ted (sealed) or
      ``abort``-ed (discarded, no orphan). Retiring an identity is forward-only and
      its admission key is **never** re-minted (AIF-L17).

Like the DAG ledger it composes with, the registry holds only in-memory state and
**never writes to the certified corpus** (DP-03); persistence, if any, is the
caller's concern via :meth:`IdentityRegistry.export` / :meth:`IdentityRegistry.from_dict`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.foundation.errors import (
    DurableIdentityError,
    IdentityCollisionError,
    IdentityMintError,
)
from typing import Any

from engine.foundation.obs.context import correlation_id
from engine.foundation.obs.logging import get_logger

_logger = get_logger("foundation.durable_identity")

#: The versioned durable-identity profile tag (pinned parameter; widens append-only,
#: AIF-L24). Bump the minor/patch to widen; never rewrite an existing profile.
DURABLE_IDENTITY_PROFILE = "ucos-p2-durable/1.0.0"

#: The opaque P2 value width in hex characters (128 bits — A/G1 ``opaque-128``).
P2_OPAQUE_HEX_LEN = 32

#: The self-describing URN scheme for a rendered P2 identity (opaque, not parsable
#: back into content — it only *addresses* the identity within its authority).
P2_URN_PREFIX = "urn:ucos:p2:"


def _require_token(value: Any, label: str) -> str:
    """Return ``value`` as a validated non-empty identifier token (fails closed)."""
    if not isinstance(value, str) or not value.strip():
        raise DurableIdentityError(f"{label} is required")
    if "/" in value:
        # '/' is reserved as the admission-key render separator, so neither the
        # authority id nor the local key may contain it (keeps rendering lossless).
        raise DurableIdentityError(f"{label} must not contain '/'", value=value)
    return value


@dataclass(frozen=True, slots=True)
class AdmissionKey:
    """The path-independent admission key ``(AuthorityID, local-key)`` (AIF-L06).

    Two artifacts share an identity iff they share an admission key; the key is
    decoupled from any filesystem path or content, so renaming or moving an artifact
    never changes its identity. Uniqueness is authority-namespaced: an authority is
    responsible for the uniqueness of its own local keys, and cross-authority keys
    can never collide (AIF-L07).
    """

    authority_id: str
    local_key: str

    def __post_init__(self) -> None:
        _require_token(self.authority_id, "authority id")
        _require_token(self.local_key, "local key")

    @property
    def render(self) -> str:
        """The stable ``authority/local-key`` textual render of the key."""
        return f"{self.authority_id}/{self.local_key}"

    def to_dict(self) -> dict[str, str]:
        return {"authority_id": self.authority_id, "local_key": self.local_key}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> AdmissionKey:
        if not isinstance(data, Mapping):
            raise DurableIdentityError("admission key record must be a mapping")
        try:
            return cls(authority_id=data["authority_id"], local_key=data["local_key"])
        except (KeyError, TypeError) as exc:
            raise DurableIdentityError("admission key record is missing required fields") from exc


@dataclass(frozen=True, slots=True)
class DurableIdentity:
    """An immutable, opaque, authority-namespaced P2 identity (AIF-L02).

    ``opaque`` is a 128-bit hex value derived deterministically **from the admission
    key alone** — never from the artifact's content, admission order, or path — so it
    is opaque (it reveals nothing about the artifact) yet stable (idempotent retry).
    ``urn`` is the rendered, self-describing address; ``adopted`` marks an identity
    imported with a pre-existing opaque during a one-time genesis grandfather
    (A/G7), whose opaque is frozen rather than recomputed.
    """

    authority_id: str
    local_key: str
    opaque: str
    urn: str = ""
    profile: str = DURABLE_IDENTITY_PROFILE
    adopted: bool = False

    @staticmethod
    def compute_opaque(authority_id: str, local_key: str) -> str:
        """The deterministic opaque 128-bit value for an admission key.

        A truncation of the digest of the *admission key* (authority + local key) —
        never of content/order/path — so distinct keys are unique by construction and
        an identical key always yields an identical opaque (AIF-L02 / AIF-L07).
        """
        digest = content_hash({"authority_id": authority_id, "local_key": local_key, "plane": "P2"})
        return digest[:P2_OPAQUE_HEX_LEN]

    @classmethod
    def mint(cls, authority_id: str, local_key: str) -> DurableIdentity:
        """Deterministically allocate the durable identity for an admission key."""
        key = AdmissionKey(authority_id=authority_id, local_key=local_key)
        opaque = cls.compute_opaque(key.authority_id, key.local_key)
        return cls(
            authority_id=key.authority_id,
            local_key=key.local_key,
            opaque=opaque,
            urn=f"{P2_URN_PREFIX}{key.authority_id}:{opaque}",
            profile=DURABLE_IDENTITY_PROFILE,
            adopted=False,
        )

    @classmethod
    def adopt(cls, authority_id: str, local_key: str, opaque: str) -> DurableIdentity:
        """Import an identity with a pre-existing, frozen ``opaque`` (A/G7 genesis).

        Used once to grandfather an existing corpus: the historical opaque is
        preserved verbatim (Recorded Truth is never recomputed, AX-02) rather than
        re-derived. The admission key is still validated and namespaced.
        """
        key = AdmissionKey(authority_id=authority_id, local_key=local_key)
        if not isinstance(opaque, str) or len(opaque) != P2_OPAQUE_HEX_LEN:
            raise DurableIdentityError(
                "adopted opaque must be a fixed-width hex value",
                width=P2_OPAQUE_HEX_LEN,
            )
        if any(c not in "0123456789abcdef" for c in opaque):
            raise DurableIdentityError("adopted opaque must be lowercase hex", opaque=opaque)
        return cls(
            authority_id=key.authority_id,
            local_key=key.local_key,
            opaque=opaque,
            urn=f"{P2_URN_PREFIX}{key.authority_id}:{opaque}",
            profile=DURABLE_IDENTITY_PROFILE,
            adopted=True,
        )

    @property
    def admission_key(self) -> AdmissionKey:
        return AdmissionKey(authority_id=self.authority_id, local_key=self.local_key)

    def verify(self) -> bool:
        """Return True iff a *natively minted* identity's opaque still recomputes.

        An adopted identity carries a frozen historical opaque that is preserved, not
        recomputed (AX-02), so it is trivially considered intact.
        """
        if self.adopted:
            return True
        return self.compute_opaque(self.authority_id, self.local_key) == self.opaque

    def to_dict(self) -> dict[str, Any]:
        return {
            "authority_id": self.authority_id,
            "local_key": self.local_key,
            "opaque": self.opaque,
            "urn": self.urn,
            "profile": self.profile,
            "adopted": self.adopted,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> DurableIdentity:
        """Reconstruct an identity from its :meth:`to_dict` form (used by import)."""
        if not isinstance(data, Mapping):
            raise DurableIdentityError("identity record must be a mapping")
        try:
            authority_id = data["authority_id"]
            local_key = data["local_key"]
            opaque = data["opaque"]
        except (KeyError, TypeError) as exc:
            raise DurableIdentityError("identity record is missing required fields") from exc
        if data.get("adopted"):
            return cls.adopt(authority_id, local_key, opaque)
        identity = cls.mint(authority_id, local_key)
        if identity.opaque != opaque:
            raise IdentityCollisionError(
                "imported opaque does not match its admission key (tamper detected)",
                expected=opaque,
                actual=identity.opaque,
            )
        return identity


class MintState(str, Enum):
    """The lifecycle of a provisional mint (AIF-L13 prepare/commit/abort)."""

    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"


@dataclass(frozen=True, slots=True)
class IdentityMint:
    """A mint transaction: a durable identity plus its atomicity state (AIF-L13)."""

    identity: DurableIdentity
    state: MintState

    @property
    def admission_key(self) -> AdmissionKey:
        return self.identity.admission_key

    def to_dict(self) -> dict[str, Any]:
        return {"identity": self.identity.to_dict(), "state": self.state.value}


#: The self-describing export format tag (semantic version — widens append-only).
IDENTITY_REGISTRY_FORMAT = "ucos-p2-identity-registry/1.0.0"


class IdentityRegistry:
    """An append-only, deterministic registry of P2 durable identities (WP-04).

    Enforces the constitutional guarantees at mint time: an admission key binds to at
    most one identity (collision prevention, AIF-L07), a sealed identity is immutable
    and idempotent to re-mint (AIF-L13), and a retired admission key is never
    re-minted (never reused, AIF-L02/L17). Provisional mints are held pending until
    committed or aborted, so an aborted mint leaves no orphan identity.
    """

    __slots__ = ("_committed", "_by_opaque", "_pending", "_retired", "_order")

    def __init__(self) -> None:
        # admission-key render -> sealed DurableIdentity (Recorded Truth).
        self._committed: dict[str, DurableIdentity] = {}
        # opaque -> admission-key render (reverse index for O(1) resolution).
        self._by_opaque: dict[str, str] = {}
        # admission-key render -> provisional IdentityMint (not yet sealed).
        self._pending: dict[str, DurableIdentity] = {}
        # admission-key renders that have been retired (never re-minted).
        self._retired: set[str] = set()
        # admission-key renders in commit (admission) order.
        self._order: list[str] = []

    # -- introspection ------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._order)

    def __contains__(self, ref: str) -> bool:
        return ref in self._committed or ref in self._by_opaque

    @property
    def identities(self) -> tuple[DurableIdentity, ...]:
        """An immutable snapshot of the sealed identities in admission order."""
        return tuple(self._committed[r] for r in self._order)

    @property
    def pending(self) -> tuple[IdentityMint, ...]:
        """The provisional (prepared, unsealed) mints, in a deterministic order."""
        return tuple(
            IdentityMint(self._pending[r], MintState.PREPARED) for r in sorted(self._pending)
        )

    @property
    def retired(self) -> tuple[str, ...]:
        """The retired admission-key renders (never re-minted), sorted."""
        return tuple(sorted(self._retired))

    # -- prepare / commit / abort (AIF-L13 atomicity) -----------------------------

    def prepare(self, authority_id: str, local_key: str) -> IdentityMint:
        """Provisionally mint an identity for an admission key (not yet sealed).

        Fails closed if the admission key is already sealed, already pending, or has
        been retired — a mint decision is never ambiguous (AIF-L16).
        """
        identity = DurableIdentity.mint(authority_id, local_key)
        ref = identity.admission_key.render
        if ref in self._retired:
            raise IdentityMintError(
                "admission key is retired and can never be re-minted", admission_key=ref
            )
        if ref in self._committed:
            raise IdentityCollisionError("admission key is already sealed", admission_key=ref)
        if ref in self._pending:
            raise IdentityMintError("admission key already has a pending mint", admission_key=ref)
        self._guard_opaque(identity)
        self._pending[ref] = identity
        _logger.info(
            "foundation.durable_identity.prepared",
            admission_key=ref,
            urn=identity.urn,
            correlation_id=correlation_id(),
        )
        return IdentityMint(identity, MintState.PREPARED)

    def commit(self, mint: IdentityMint) -> DurableIdentity:
        """Atomically seal a provisional mint into Recorded Truth (idempotent).

        Committing a mint whose identity is already sealed (identical opaque) is an
        idempotent retry (AIF-L13) and returns the sealed identity.
        """
        if not isinstance(mint, IdentityMint):
            raise IdentityMintError("commit expects an IdentityMint")
        identity = mint.identity
        ref = identity.admission_key.render
        existing = self._committed.get(ref)
        if existing is not None:
            if existing.opaque != identity.opaque:
                raise IdentityCollisionError(
                    "admission key already sealed to a different opaque",
                    admission_key=ref,
                )
            # Idempotent retry: already sealed to the same identity.
            self._pending.pop(ref, None)
            return existing
        if ref not in self._pending:
            raise IdentityMintError(
                "no pending mint for admission key (prepare first)", admission_key=ref
            )
        if self._pending[ref].opaque != identity.opaque:
            # The pending provisional and the committed mint disagree ⇒ fail closed.
            raise IdentityCollisionError(
                "committed mint disagrees with the prepared mint", admission_key=ref
            )
        self._guard_opaque(identity)
        del self._pending[ref]
        self._committed[ref] = identity
        self._by_opaque[identity.opaque] = ref
        self._order.append(ref)
        _logger.info(
            "foundation.durable_identity.committed",
            admission_key=ref,
            urn=identity.urn,
            index=len(self._order) - 1,
        )
        return identity

    def abort(self, mint: IdentityMint) -> None:
        """Discard a provisional mint, leaving no orphan identity (AIF-L13)."""
        if not isinstance(mint, IdentityMint):
            raise IdentityMintError("abort expects an IdentityMint")
        ref = mint.admission_key.render
        if ref in self._committed:
            raise IdentityMintError(
                "cannot abort an already-sealed identity (forward-only)", admission_key=ref
            )
        # Aborting an unknown/never-prepared mint is a harmless no-op (idempotent).
        self._pending.pop(ref, None)
        _logger.info("foundation.durable_identity.aborted", admission_key=ref)

    def mint(self, authority_id: str, local_key: str) -> DurableIdentity:
        """Prepare **and** commit in one atomic step; idempotent for a sealed key.

        The common path: re-minting an already-sealed admission key returns the
        existing identity unchanged (idempotent retry, AIF-L13) rather than failing.
        """
        candidate = DurableIdentity.mint(authority_id, local_key)
        ref = candidate.admission_key.render
        if ref in self._retired:
            raise IdentityMintError(
                "admission key is retired and can never be re-minted", admission_key=ref
            )
        existing = self._committed.get(ref)
        if existing is not None:
            return existing
        return self.commit(self.prepare(authority_id, local_key))

    # -- lookup (fails closed — AIF-L16) ------------------------------------------

    def lookup(self, authority_id: str, local_key: str) -> DurableIdentity:
        """Resolve a sealed identity by its admission key (fails closed)."""
        ref = AdmissionKey(authority_id=authority_id, local_key=local_key).render
        identity = self._committed.get(ref)
        if identity is None:
            raise DurableIdentityError("no sealed identity for admission key", admission_key=ref)
        return identity

    def resolve(self, ref: str) -> DurableIdentity:
        """Resolve a sealed identity by opaque value or full URN (fails closed)."""
        opaque = ref[len(P2_URN_PREFIX) :].split(":")[-1] if ref.startswith(P2_URN_PREFIX) else ref
        key_ref = self._by_opaque.get(opaque)
        if key_ref is None:
            raise DurableIdentityError("no sealed identity for reference", ref=ref)
        return self._committed[key_ref]

    def durable_reference(self, authority_id: str, local_key: str) -> str:
        """Return the stable, path-independent URN for a sealed admission key."""
        return self.lookup(authority_id, local_key).urn

    # -- forward-only retirement (AIF-L17) ----------------------------------------

    def retire(self, authority_id: str, local_key: str) -> None:
        """Retire a sealed identity; its admission key is never re-minted."""
        ref = AdmissionKey(authority_id=authority_id, local_key=local_key).render
        if ref not in self._committed:
            raise DurableIdentityError("cannot retire an unsealed identity", admission_key=ref)
        self._retired.add(ref)
        _logger.info("foundation.durable_identity.retired", admission_key=ref)

    # -- migration compatibility (A/G7 genesis grandfather) -----------------------

    def adopt(self, authority_id: str, local_key: str, opaque: str) -> DurableIdentity:
        """Seal an identity with a pre-existing, frozen opaque (one-time genesis).

        Preserves an existing corpus's historical opaque verbatim rather than
        recomputing it (AX-02). Uniqueness is still enforced: the admission key must
        be unsealed/unretired and the opaque must not already be bound.
        """
        identity = DurableIdentity.adopt(authority_id, local_key, opaque)
        ref = identity.admission_key.render
        if ref in self._retired:
            raise IdentityMintError(
                "admission key is retired and can never be re-minted", admission_key=ref
            )
        existing = self._committed.get(ref)
        if existing is not None:
            if existing.opaque != identity.opaque:
                raise IdentityCollisionError(
                    "admission key already sealed to a different opaque",
                    admission_key=ref,
                )
            return existing
        self._guard_opaque(identity)
        self._pending.pop(ref, None)
        self._committed[ref] = identity
        self._by_opaque[identity.opaque] = ref
        self._order.append(ref)
        _logger.info("foundation.durable_identity.adopted", admission_key=ref, urn=identity.urn)
        return identity

    # -- integrity ----------------------------------------------------------------

    def verify(self) -> bool:
        """Return True iff every sealed identity is intact and uniquely indexed."""
        if len(self._by_opaque) != len(self._committed):
            return False
        for ref, identity in self._committed.items():
            if identity.admission_key.render != ref:
                return False
            if not identity.verify():
                return False
            if self._by_opaque.get(identity.opaque) != ref:
                return False
        return True

    def require_intact(self) -> None:
        """Raise :class:`IdentityCollisionError` if the registry is not intact."""
        if not self.verify():
            raise IdentityCollisionError(
                "identity registry integrity check failed", count=len(self._order)
            )

    def fingerprint(self) -> str:
        """A deterministic content hash of the sealed registry (replay/equality)."""
        return content_hash(self.export())

    def _guard_opaque(self, identity: DurableIdentity) -> None:
        """Reject an opaque already bound to a *different* admission key."""
        ref = identity.admission_key.render
        bound = self._by_opaque.get(identity.opaque)
        if bound is not None and bound != ref:
            raise IdentityCollisionError(
                "opaque value already bound to a different admission key",
                opaque=identity.opaque,
                bound_to=bound,
            )
        pending_ref = next(
            (
                r
                for r, ident in self._pending.items()
                if ident.opaque == identity.opaque and r != ref
            ),
            None,
        )
        if pending_ref is not None:
            raise IdentityCollisionError(
                "opaque value already pending for a different admission key",
                opaque=identity.opaque,
                bound_to=pending_ref,
            )

    # -- export / import ----------------------------------------------------------

    def export(self) -> dict[str, Any]:
        """Serialize the sealed registry to a deterministic, self-describing dict.

        Only sealed identities are exported — provisional (unsealed) mints are not
        Recorded Truth and never persist.
        """
        return {
            "registry_format": IDENTITY_REGISTRY_FORMAT,
            "count": len(self._order),
            "retired": sorted(self._retired),
            "identities": [self._committed[r].to_dict() for r in self._order],
        }

    #: Alias kept parallel with the DAG ledger's ``to_dict`` surface.
    to_dict = export

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> IdentityRegistry:
        """Reconstruct (import) a registry from its :meth:`export` form, verifying it."""
        if not isinstance(data, Mapping):
            raise DurableIdentityError("registry export must be a mapping")
        identities = data.get("identities")
        if not isinstance(identities, list):
            raise DurableIdentityError("registry export has no 'identities' list")
        registry = cls()
        for record in identities:
            identity = DurableIdentity.from_dict(record)
            if identity.adopted:
                registry.adopt(identity.authority_id, identity.local_key, identity.opaque)
            else:
                registry.mint(identity.authority_id, identity.local_key)
        for ref in data.get("retired") or ():
            if not isinstance(ref, str) or ref not in registry._committed:
                raise DurableIdentityError(
                    "retired admission key is not a sealed identity", admission_key=ref
                )
            registry._retired.add(ref)
        registry.require_intact()
        return registry


def build_identity_registry(
    seed: Iterable[tuple[str, str]] | None = None,
) -> IdentityRegistry:
    """Build an :class:`IdentityRegistry`, optionally minting a seed of keys.

    ``seed`` is an iterable of ``(authority_id, local_key)`` pairs minted in order.
    Deterministic: the same seed always yields the same registry fingerprint.
    """
    registry = IdentityRegistry()
    for authority_id, local_key in seed or ():
        registry.mint(authority_id, local_key)
    return registry


__all__ = [
    "DURABLE_IDENTITY_PROFILE",
    "P2_OPAQUE_HEX_LEN",
    "P2_URN_PREFIX",
    "IDENTITY_REGISTRY_FORMAT",
    "AdmissionKey",
    "DurableIdentity",
    "MintState",
    "IdentityMint",
    "IdentityRegistry",
    "build_identity_registry",
]
