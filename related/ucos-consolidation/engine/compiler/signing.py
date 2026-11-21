"""TASK-000026 — Signing Stage (EPIC-003, IMP-007 §12).

Applies a cryptographic signature and generates an SBOM for a package. Signing is
gated before publishing (IMP-007 §12/§15) and is deterministic: the signature is
an HMAC-SHA256 over the package's canonical signing payload, so identical inputs
and key yield an identical signature (reproducibility, IMP-007 §5).

Secrets by reference only (SEC-04 / SEC-05 / ID-04; Mandatory constraints):
    * the signing key is supplied either as an explicit ``bytes`` key (used for
      deterministic tests) or, in production, as a Foundation :class:`SecretRef`
      (e.g. ``env://UCOS_SIGNING_KEY``) that is **resolved at sign time and never
      stored, embedded, or logged**;
    * the signed package records only a **non-secret key label** (the reference
      name, never the value).

The generated SBOM enumerates every artifact with its hash plus the provenance
chain and pinned toolchain, and embeds no secrets.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any

from engine.compiler.errors import SigningError
from engine.compiler.packaging import (
    COMPILER_TOOLCHAIN,
    TOOLCHAIN_VERSION,
    Package,
)
from engine.foundation.config.config import SecretRef
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("compiler.sign")

SIGNATURE_ALGORITHM = "HMAC-SHA256"
SBOM_FORMAT = "ucos-sbom/1.0.0"


@dataclass(frozen=True, slots=True)
class SignedPackage:
    """A package with an attached signature and SBOM (no secrets embedded)."""

    package: Package
    algorithm: str
    signature: str
    signing_payload_hash: str
    key_ref: str
    sbom: dict[str, Any]

    @property
    def blueprint_id(self) -> str:
        return self.package.blueprint_id


def _signing_payload(package: Package) -> bytes:
    """Return the deterministic bytes the signature is computed over."""
    payload = {
        "blueprint_id": package.blueprint_id,
        "name": package.name,
        "version": package.version,
        "package_hash": package.package_hash,
        "algorithm": SIGNATURE_ALGORITHM,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _build_sbom(package: Package) -> dict[str, Any]:
    return {
        "sbom_format": SBOM_FORMAT,
        "package": {
            "blueprint_id": package.blueprint_id,
            "name": package.name,
            "version": package.version,
            "sha256": package.package_hash,
        },
        "toolchain": {
            "compiler": COMPILER_TOOLCHAIN,
            "compiler_version": TOOLCHAIN_VERSION,
        },
        "provenance": package.manifest.get("provenance", {}),
        "components": [
            {
                "type": "compiled-artifact",
                "path": a.path,
                "kind": a.kind.value,
                "sha256": a.content_hash,
            }
            for a in package.artifacts
        ],
    }


class Signer:
    """Signs packages with HMAC-SHA256 using a key held by reference only."""

    __slots__ = ("_key", "_key_ref")

    def __init__(
        self,
        *,
        key: bytes | None = None,
        key_ref: SecretRef | str | None = None,
    ) -> None:
        if key is None and key_ref is None:
            raise SigningError("a signing key or key reference is required")
        if key is not None and not isinstance(key, bytes | bytearray):
            raise SigningError("explicit signing key must be bytes")
        self._key: bytes | None = bytes(key) if key is not None else None
        if key_ref is None:
            self._key_ref: SecretRef | None = None
        else:
            self._key_ref = key_ref if isinstance(key_ref, SecretRef) else SecretRef(key_ref)

    def _resolve_key(self) -> bytes:
        if self._key is not None:
            return self._key
        assert self._key_ref is not None  # noqa: S101 — guaranteed by __init__
        resolved = self._key_ref.resolve()
        if not resolved:
            raise SigningError("resolved signing key is empty")
        return resolved.encode("utf-8")

    @property
    def key_ref_label(self) -> str:
        """A non-secret label naming the signing key (never its value)."""
        if self._key_ref is not None:
            return f"{self._key_ref.scheme}://{self._key_ref.locator}"
        return "inline:explicit-key"

    def sign(self, package: Package) -> SignedPackage:
        """Sign ``package`` and attach its SBOM; the key is never embedded."""
        with trace("compiler.sign", blueprint=package.blueprint_id):
            payload = _signing_payload(package)
            key = self._resolve_key()
            signature = hmac.new(key, payload, hashlib.sha256).hexdigest()
            payload_hash = hashlib.sha256(payload).hexdigest()
            sbom = _build_sbom(package)
        _logger.info(
            "compiler.blueprint.signed",
            blueprint=package.blueprint_id,
            algorithm=SIGNATURE_ALGORITHM,
            key_ref=self.key_ref_label,
        )
        return SignedPackage(
            package=package,
            algorithm=SIGNATURE_ALGORITHM,
            signature=signature,
            signing_payload_hash=payload_hash,
            key_ref=self.key_ref_label,
            sbom=sbom,
        )

    def verify(self, signed: SignedPackage) -> bool:
        """Verify a signed package against the current key (signature gate)."""
        expected = hmac.new(
            self._resolve_key(), _signing_payload(signed.package), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signed.signature)


__all__ = [
    "SIGNATURE_ALGORITHM",
    "SBOM_FORMAT",
    "SignedPackage",
    "Signer",
]
