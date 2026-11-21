"""EC2-TASK-000055 — Platform Foundation error taxonomy (EC2-EPIC-001).

The Platform Foundation **reuses** the EC-1 Foundation error discipline
(TASK-000006) additively — it does not fork or modify it. Every platform error is
rooted in :class:`~engine.foundation.obs.errors.FoundationError`, carries a stable,
category-prefixed ``code`` (``EC2-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The Platform Foundation is *additive over EC-1*: it consumes the certified EC-1
engine only through published contracts, never modifies it, and never writes to the
certified corpus (DP-03). A malformed platform contract, configuration, identity,
service registration, dependency graph, event, capability, or bootstrap fails loudly
with a specific error. The base class is named :class:`PlatformError` so it never
shadows EC-1 / compiler / validation / certification error hierarchies.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class PlatformError(FoundationError):
    """Base class for all EC-2 Platform Foundation errors."""

    code = "EC2-000"


class PlatformContractError(PlatformError):
    """A platform contract is malformed or violates versioning discipline (AR-03/PL-05)."""

    code = "EC2-CONTRACT-001"


class PlatformConfigError(PlatformError):
    """Platform configuration is invalid, missing, or malformed."""

    code = "EC2-CONFIG-001"


class PlatformIdentityError(PlatformError):
    """A platform principal, role, or permission set is malformed."""

    code = "EC2-IDENTITY-001"


class ServiceRegistrationError(PlatformError):
    """A platform service could not be registered (duplicate or malformed)."""

    code = "EC2-SERVICE-001"


class ServiceResolutionError(PlatformError):
    """A platform service could not be resolved from the registry."""

    code = "EC2-SERVICE-002"


class DependencyError(PlatformError):
    """A platform dependency is unresolved or the dependency graph has a cycle."""

    code = "EC2-DEPENDENCY-001"


class EventError(PlatformError):
    """A platform event or event-bus operation is malformed."""

    code = "EC2-EVENT-001"


class DagLedgerError(PlatformError):
    """A DAG event-ledger operation is malformed (WP-03).

    Raised for an invalid append/branch/merge (e.g. a parent reference that is not
    already recorded), a malformed export, or an import that cannot be replayed in a
    causally valid (parents-before-children) order. Fails closed (AIF-L16).
    """

    code = "EC2-LEDGER-001"


class DagLedgerIntegrityError(DagLedgerError):
    """The append-only, Merkle-linked event DAG failed its integrity check (WP-03).

    Raised when a recorded event's recomputed Merkle hash no longer matches its
    stored ``event_hash``, when a parent edge is dangling, or when the recorded
    order violates the parents-before-children topology — i.e. Recorded Truth was
    mutated. The DAG is tamper-evident: any edit of history is detected (AIF-L08 /
    AIF-L17, forward-only compensation).
    """

    code = "EC2-LEDGER-002"


class DurableIdentityError(PlatformError):
    """A P2 durable identity operation is malformed (WP-04).

    Raised for an invalid admission key, a malformed durable identity, or a failed
    mint validation. P2 identities are opaque, authority-namespaced, minted-once and
    immutable (AIF-L02); any violation fails closed (AIF-L16).
    """

    code = "EC2-IDENTITY-P2-001"


class IdentityMintError(DurableIdentityError):
    """A durable-identity mint transaction is invalid (WP-04).

    Raised when a prepare/commit/abort step is applied to a mint in an incompatible
    state, an unknown provisional mint is committed/aborted, or a retired admission
    key is re-minted (identities are never reused — AIF-L02 / AIF-L13).
    """

    code = "EC2-IDENTITY-P2-002"


class IdentityCollisionError(DurableIdentityError):
    """A durable-identity collision was detected (WP-04).

    Raised when an admission key or opaque value would bind to more than one
    identity — global uniqueness is guaranteed by construction from the
    authority-namespaced admission key (AIF-L07), so a collision is a fail-closed
    integrity fault.
    """

    code = "EC2-IDENTITY-P2-003"


class TrustError(PlatformError):
    """A genesis-trust, key, or signing operation is malformed (WP-05).

    Base for the trust/keys/signing taxonomy realizing AIF-L10 (genesis + trust) and
    AIF-L11 (signed events, custody, revocation). Fails closed (AIF-L16).
    """

    code = "EC2-TRUST-001"


class SignatureError(TrustError):
    """A signature could not be produced or failed verification (WP-05).

    Raised for a missing/empty key, a malformed signature record, or a signature
    that does not verify against the referenced key. Keys are never embedded in
    artifacts (AIF-L11 / RR-07).
    """

    code = "EC2-TRUST-002"


class TrustChainError(TrustError):
    """A trust chain is broken, untrusted, or references a revoked/unknown key (WP-05).

    Raised when a key cannot be traced by signed delegation to a self-signed genesis
    anchor, when a key on the path is revoked, or when a delegation cycle is
    detected. Successor recognition is by signed delegation or quorum (AIF-L10).
    """

    code = "EC2-TRUST-003"


class CanonicalFormError(PlatformError):
    """Content could not be reduced to its Canonical Content Form (WP-06).

    Raised for an unknown/invalid canonical profile or content that cannot be
    deterministically normalized/serialized. The CCF is the versioned,
    technology-independent normalization over which every P1 content digest computes
    (AIF-L05 · A/G4); a malformed input fails closed (AIF-L16).
    """

    code = "EC2-CCF-001"


class CryptoAgilityError(PlatformError):
    """A multihash / algorithm-registry / rollover operation is malformed (WP-07).

    Base for crypto-agility faults. Digests are algorithm-tagged multihashes and the
    opaque durable identity survives algorithm breakage (AIF-L22 · A/G5); an
    unsupported algorithm or malformed multihash fails closed (AIF-L16).
    """

    code = "EC2-CRYPTO-001"


class AlgorithmNegotiationError(CryptoAgilityError):
    """No acceptable hash algorithm could be negotiated (WP-07).

    Raised when there is no common active algorithm between two parties, or when a
    rollover/deprecation would leave no active algorithm (deprecation is only
    permitted *after* rollover to a successor — AIF-L22).
    """

    code = "EC2-CRYPTO-002"


class AdmissionError(PlatformError):
    """An admission-key binding operation is malformed (WP-08).

    Base for the admission-authority taxonomy realizing AIF-L06 (path-independent
    admission key), AIF-L07 (authority-namespaced uniqueness), AIF-L09 (authority =
    serialization domain), and AIF-L14 (atomic admission). Fails closed (AIF-L16).
    """

    code = "EC2-ADMISSION-001"


class AuthorityBindingError(AdmissionError):
    """An admission authority / namespace-ownership / migration rule was violated (WP-08).

    Raised for an unknown or duplicate authority, minting attempted under a
    partitioned or migrated authority (AIF-L09), or an unwitnessed/invalid authority
    migration.
    """

    code = "EC2-ADMISSION-002"


class DuplicateAdmissionError(AdmissionError):
    """A duplicate admission was detected (WP-08).

    Raised when a logical name is already bound, or when a distinct name would bind
    an already-admitted admission key (the same identity admitted twice) — uniqueness
    is authority-namespaced and path-independent (AIF-L06 / AIF-L07).
    """

    code = "EC2-ADMISSION-003"


class DerivationError(PlatformError):
    """A derivation operation is malformed or its inputs drifted (WP-09).

    Base for the derivation-purity taxonomy realizing AIF-L18 (derived = pure
    f(Source, Recorded Truth, Generator-version); stamped; no hidden state/wall-clock)
    and AIF-L20 (non-mixing of determinisms). Fails closed (AIF-L16).
    """

    code = "EC2-DERIVATION-001"


class DerivationPurityError(DerivationError):
    """A derivation was impure or mixed determinisms (WP-09).

    Raised when a derivation is non-reproducible (its output differs across identical
    re-derivations — hidden state or wall-clock, AIF-L18), or when a *derived* value
    is declared as an identity-determinism source (mixing generated determinism into
    recorded identity, AIF-L20).
    """

    code = "EC2-DERIVATION-002"


class CapabilityError(PlatformError):
    """A platform or engine capability is malformed or references an unknown dependency."""

    code = "EC2-CAPABILITY-001"


class BootstrapError(PlatformError):
    """The platform foundation could not be composed (bootstrap failed, fail-closed)."""

    code = "EC2-BOOTSTRAP-001"


__all__ = [
    "PlatformError",
    "PlatformContractError",
    "PlatformConfigError",
    "PlatformIdentityError",
    "ServiceRegistrationError",
    "ServiceResolutionError",
    "DependencyError",
    "EventError",
    "DagLedgerError",
    "DagLedgerIntegrityError",
    "DurableIdentityError",
    "IdentityMintError",
    "IdentityCollisionError",
    "TrustError",
    "SignatureError",
    "TrustChainError",
    "CanonicalFormError",
    "CryptoAgilityError",
    "AlgorithmNegotiationError",
    "AdmissionError",
    "AuthorityBindingError",
    "DuplicateAdmissionError",
    "DerivationError",
    "DerivationPurityError",
    "CapabilityError",
    "BootstrapError",
]
