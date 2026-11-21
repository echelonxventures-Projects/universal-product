"""TASK-000027 — Publishing Stage (EPIC-003, IMP-007 §3/§12).

Publishing is the final pipeline stage: it registers the signed artifact with its
**embedded provenance** into an artifact-registry record and materialises the
package to an output directory. Two hard gates apply:

    * **Signature gate** (IMP-007 §12/§15) — publishing verifies the signature
      first; an unverifiable package is refused.
    * **Frozen-corpus gate** (DP-03 / C-01; Mandatory Rules 1 & 3) — the output
      directory is checked with the Foundation frozen-path guard, so the compiler
      **can never write into ``00-BOOK/``, ``00-SOURCE/``, or ``99-FREEZE/``**.

The produced artifact record embeds the complete backward-traceability chain
(Mandatory Rule 6) and a deterministic engineering artifact identity (IMP-007
§10) that confers no authority (IMP-007 §18). The record contains no secrets and
no wall-clock state, so a reproduced build yields an identical record.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.compiler.errors import PublishingError
from engine.compiler.signing import SignedPackage, Signer
from engine.foundation.guards.frozen_paths import assert_no_frozen_write
from engine.foundation.obs.errors import SecurityViolation
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("compiler.publish")

MANIFEST_FILE = "manifest.json"
SBOM_FILE = "sbom.json"
SIGNATURE_FILE = "signature.json"
RECORD_FILE = "artifact-record.json"


@dataclass(frozen=True, slots=True)
class PublishedArtifact:
    """The outcome of publishing: the registry record and materialised files."""

    artifact_id: str
    blueprint_id: str
    record: dict[str, Any]
    output_dir: str
    written_paths: tuple[str, ...]


def _compilation_id(signed: SignedPackage) -> str:
    """A deterministic compilation identity (IMP-007 §10)."""
    digest = hashlib.sha256(
        f"{signed.package.package_hash}:{signed.signature}".encode()
    ).hexdigest()
    return digest[:16]


def _artifact_id(signed: SignedPackage, compilation_id: str) -> str:
    """A deterministic, non-authoritative engineering artifact id (IMP-007 §10)."""
    return f"UCOS-CMP-{signed.package.blueprint_id}-{compilation_id}"


def _artifact_record(signed: SignedPackage) -> dict[str, Any]:
    package = signed.package
    compilation_id = _compilation_id(signed)
    artifact_id = _artifact_id(signed, compilation_id)
    return {
        "artifact_id": artifact_id,
        "compilation_id": compilation_id,
        "blueprint_id": package.blueprint_id,
        "name": package.name,
        "version": package.version,
        "authority": "ENGINEERING-EXECUTION-ONLY",
        "package": {
            "sha256": package.package_hash,
            "format": package.manifest.get("package_format"),
        },
        "signature": {
            "algorithm": signed.algorithm,
            "value": signed.signature,
            "payload_sha256": signed.signing_payload_hash,
            "key_ref": signed.key_ref,
        },
        "provenance": package.manifest.get("provenance", {}),
        "toolchain": package.manifest.get("toolchain", {}),
        "artifacts": [
            {"path": a.path, "kind": a.kind.value, "sha256": a.content_hash}
            for a in package.artifacts
        ],
    }


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


class Publisher:
    """Publishes a signed package to an output directory, gated on verification."""

    __slots__ = ("_output_dir",)

    def __init__(self, output_dir: str | Path) -> None:
        self._output_dir = Path(output_dir)

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    def _guard_frozen(self, target: Path) -> None:
        """Refuse to publish anywhere under the read-only certified corpus."""
        try:
            relative = target.resolve().relative_to(Path.cwd())
            probe = relative.as_posix()
        except ValueError:
            probe = target.as_posix()
        try:
            assert_no_frozen_write([probe])
        except SecurityViolation as exc:
            raise PublishingError(
                "refusing to publish into the read-only certified corpus (DP-03)",
                output_dir=str(target),
                detail=exc.message,
            ) from exc

    def publish(self, signed: SignedPackage, *, verify_with: Signer) -> PublishedArtifact:
        """Verify, gate, materialise, and register a signed package."""
        with trace("compiler.publish", blueprint=signed.package.blueprint_id):
            if not verify_with.verify(signed):
                raise PublishingError(
                    "signature verification failed; publishing is refused",
                    blueprint_id=signed.package.blueprint_id,
                )
            target = self._output_dir / signed.package.blueprint_id
            self._guard_frozen(target)

            record = _artifact_record(signed)
            written = self._materialise(target, signed, record)
        _logger.info(
            "compiler.blueprint.published",
            blueprint=signed.package.blueprint_id,
            artifact_id=record["artifact_id"],
            files=len(written),
        )
        return PublishedArtifact(
            artifact_id=record["artifact_id"],
            blueprint_id=signed.package.blueprint_id,
            record=record,
            output_dir=str(target),
            written_paths=written,
        )

    def _materialise(
        self, target: Path, signed: SignedPackage, record: dict[str, Any]
    ) -> tuple[str, ...]:
        package = signed.package
        written: list[str] = []
        artifacts_root = target / "artifacts"
        for artifact in package.artifacts:
            path = artifacts_root / artifact.path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(artifact.content, encoding="utf-8")
            written.append(path.as_posix())

        target.mkdir(parents=True, exist_ok=True)
        for filename, payload in (
            (MANIFEST_FILE, package.manifest),
            (SBOM_FILE, signed.sbom),
            (SIGNATURE_FILE, self._signature_doc(signed)),
            (RECORD_FILE, record),
        ):
            path = target / filename
            path.write_text(_canonical_json(payload), encoding="utf-8")
            written.append(path.as_posix())
        return tuple(sorted(written))

    @staticmethod
    def _signature_doc(signed: SignedPackage) -> dict[str, Any]:
        return {
            "algorithm": signed.algorithm,
            "signature": signed.signature,
            "payload_sha256": signed.signing_payload_hash,
            "package_sha256": signed.package.package_hash,
            "key_ref": signed.key_ref,
        }


__all__ = [
    "MANIFEST_FILE",
    "SBOM_FILE",
    "SIGNATURE_FILE",
    "RECORD_FILE",
    "PublishedArtifact",
    "Publisher",
]
