"""UPA-000012 — Provider Framework evidence (Terminal-04).

Turns a framework run into a **content-addressed, byte-reproducible evidence bundle**.
Two runs over an identical substrate produce identical files and an identical
``bundle_hash``, because every artifact is canonical JSON and the framework holds no
wall-clock.

    * :class:`ProviderEvidenceBundle` — the immutable bundle projection.
    * :func:`build_evidence` — assemble a bundle from a framework run.
    * :func:`write_evidence` — materialize the bundle as files plus a manifest.
    * :func:`verify_evidence` — re-hash a materialized bundle and compare.

The manifest lists each artifact with its own content hash, so a bundle is
self-verifying: tampering with any artifact is detectable without access to the
framework that produced it.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from platform.universal_provider.constitution import provider_constitution
from platform.universal_provider.contracts import canonical_json, content_hash
from platform.universal_provider.discovery import DiscoveryResult
from platform.universal_provider.errors import ProviderEvidenceError
from platform.universal_provider.framework import OnboardingResult, ProviderFramework
from typing import Any

#: Semantic version of the evidence bundle format.
PROVIDER_EVIDENCE_VERSION = "1.0.0"

#: The manifest filename written into every bundle directory.
MANIFEST_FILENAME = "MANIFEST.json"


@dataclass(frozen=True, slots=True)
class ProviderEvidenceBundle:
    """The immutable, content-addressed evidence projection of a framework run."""

    constitution: dict[str, Any]
    framework_state: dict[str, Any]
    registry: dict[str, Any]
    lifecycle: dict[str, Any]
    certification: dict[str, Any]
    discovery: dict[str, Any]
    onboarding: dict[str, Any]

    def artifacts(self) -> dict[str, dict[str, Any]]:
        """Return the bundle's artifacts keyed by filename."""
        return {
            "constitution.json": self.constitution,
            "framework-state.json": self.framework_state,
            "registry.json": self.registry,
            "lifecycle.json": self.lifecycle,
            "certification.json": self.certification,
            "discovery.json": self.discovery,
            "onboarding.json": self.onboarding,
        }

    def manifest(self) -> dict[str, Any]:
        """Return the self-verifying manifest over every artifact."""
        artifacts = self.artifacts()
        return {
            "evidence_version": PROVIDER_EVIDENCE_VERSION,
            "artifacts": {
                filename: content_hash(payload) for filename, payload in sorted(artifacts.items())
            },
            "bundle_hash": self.bundle_hash(),
        }

    def bundle_hash(self) -> str:
        """Return the content hash over every artifact in the bundle."""
        return content_hash(
            {
                filename: content_hash(payload)
                for filename, payload in sorted(self.artifacts().items())
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {"manifest": self.manifest(), "artifacts": self.artifacts()}


def build_evidence(
    framework: ProviderFramework,
    *,
    discovery: DiscoveryResult | None = None,
    onboarding: Sequence[OnboardingResult] = (),
) -> ProviderEvidenceBundle:
    """Assemble the evidence bundle for a completed framework run."""
    if not isinstance(framework, ProviderFramework):
        raise ProviderEvidenceError(
            "evidence requires a ProviderFramework", {"received": type(framework).__name__}
        )
    results = tuple(onboarding)
    return ProviderEvidenceBundle(
        constitution=provider_constitution().to_dict(),
        framework_state=framework.state(),
        registry=framework.registry.to_dict(),
        lifecycle=framework.lifecycle.to_dict(),
        certification=framework.certifier.ledger.to_dict(),
        discovery=discovery.to_dict() if discovery is not None else {"discovered": [], "count": 0},
        onboarding={
            "count": len(results),
            "active": sorted(item.qualified_id for item in results if item.active),
            "results": [item.to_dict() for item in results],
        },
    )


def write_evidence(bundle: ProviderEvidenceBundle, directory: Path | str) -> tuple[Path, ...]:
    """Write every artifact plus the manifest into ``directory``, sorted.

    Returns the written paths. Each file is canonical JSON with a trailing newline, so
    the bytes are stable across platforms and reruns.
    """
    if not isinstance(bundle, ProviderEvidenceBundle):
        raise ProviderEvidenceError(
            "write_evidence requires a ProviderEvidenceBundle",
            {"received": type(bundle).__name__},
        )
    target = Path(directory)
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ProviderEvidenceError(
            "evidence directory could not be created",
            {"directory": str(target), "reason": str(exc)},
        ) from exc
    written: list[Path] = []
    payloads = {**bundle.artifacts(), MANIFEST_FILENAME: bundle.manifest()}
    for filename in sorted(payloads):
        path = target / filename
        try:
            path.write_text(canonical_json(payloads[filename]) + "\n", encoding="utf-8")
        except OSError as exc:
            raise ProviderEvidenceError(
                "evidence artifact could not be written",
                {"path": str(path), "reason": str(exc)},
            ) from exc
        written.append(path)
    return tuple(written)


def verify_evidence(directory: Path | str) -> bool:
    """Whether a materialized bundle still matches its own manifest."""
    target = Path(directory)
    manifest_path = target / MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise ProviderEvidenceError("evidence bundle has no manifest", {"directory": str(target)})
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderEvidenceError(
            "evidence manifest is unreadable", {"path": str(manifest_path), "reason": str(exc)}
        ) from exc
    declared = manifest.get("artifacts")
    if not isinstance(declared, dict):
        raise ProviderEvidenceError(
            "evidence manifest declares no artifacts", {"path": str(manifest_path)}
        )
    for filename, expected_hash in sorted(declared.items()):
        path = target / str(filename)
        if not path.is_file():
            return False
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        if content_hash(payload) != expected_hash:
            return False
    recomputed = content_hash({str(k): str(v) for k, v in sorted(declared.items())})
    return recomputed == manifest.get("bundle_hash")


__all__ = [
    "MANIFEST_FILENAME",
    "PROVIDER_EVIDENCE_VERSION",
    "ProviderEvidenceBundle",
    "build_evidence",
    "verify_evidence",
    "write_evidence",
]
