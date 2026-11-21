"""TASK-000034 — Runtime Assembly Engine (EPIC-005, IMP-007 §8).

Transforms a **published compiler package** (TASK-000027 output) into a
deployable, self-describing :class:`RuntimeUnit` for the IMP-008 Runtime Platform.
Assembly is the composition step defined by IMP-007 §8 — *dependency assembly ·
configuration assembly · resource assembly · runtime assembly* — and it binds
**only registered, certified components** (§15). It produces a certified,
deployable assembly and **no live production system** (§8).

The engine applies four hard gates before it emits anything:

    * **Provenance gate** (§1) — the backward-traceability chain must be present
      and byte-consistent across the manifest, the artifact record, and the SBOM.
    * **Signature gate** (§12/§15) — the package signature is verified with a
      caller-supplied :class:`~engine.compiler.signing.Signer`; an unverifiable
      package is refused (the same gate the Publisher applies).
    * **SBOM gate** (§12) — a well-formed SBOM enumerating every component must be
      present.
    * **Secrets-by-reference gate** (SEC-04) — configuration binds secrets **only**
      by reference (``env://…``); an inline secret value is refused.

The generated **runtime descriptor is deterministic** (IMP-007 §5): it embeds no
timestamps or ambient state and sorts every collection, so an identical published
package and dependency closure yield a byte-identical descriptor and a stable
``runtime_id``. Assembly reuses the Foundation, Compiler packaging/signing, and
disclosure APIs verbatim (Mandatory Rule 4) and every generated unit carries the
EC-1 provisional-state disclosure (TASK-000036).
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from engine.compiler.packaging import Package, _hash_manifest
from engine.compiler.publishing import (
    MANIFEST_FILE,
    RECORD_FILE,
    SBOM_FILE,
    SIGNATURE_FILE,
    PublishedArtifact,
)
from engine.compiler.signing import SignedPackage, Signer
from engine.foundation.config.config import SecretRef
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.disclosure import inject_provisional_state
from engine.runtime.errors import (
    DependencyClosureError,
    ProvenanceValidationError,
    RuntimeAssemblyError,
    SBOMValidationError,
    SecretExposureError,
    SignatureValidationError,
)

_logger = get_logger("runtime.assembly")

#: The runtime descriptor format the engine emits.
RUNTIME_DESCRIPTOR_FORMAT = "ucos-runtime/1.0.0"

#: Keys whose values are treated as secrets and therefore forbidden inline (SEC-04).
_SECRET_KEY_PATTERN = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|apikey|credential|"
    r"private[_-]?key|access[_-]?key)",
    re.IGNORECASE,
)

#: Deterministic default resource envelope bound by resource assembly (§8). The
#: blueprint declares no resources, so a fixed, minimal envelope is bound.
DEFAULT_RESOURCES: dict[str, Any] = {
    "replicas": 1,
    "cpu_request": "100m",
    "cpu_limit": "500m",
    "memory_request": "128Mi",
    "memory_limit": "256Mi",
}


# --------------------------------------------------------------------------- #
# Value types                                                                  #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class SecretBinding:
    """A configuration secret bound **by reference only** (SEC-04)."""

    name: str
    ref: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "ref": self.ref}


@dataclass(frozen=True, slots=True)
class ClosureEntry:
    """One pinned member of the resolved dependency closure (§8)."""

    blueprint_id: str
    artifact_id: str
    package_sha256: str
    role: str  # "root" | "dependency"

    def to_dict(self) -> dict[str, str]:
        return {
            "blueprint_id": self.blueprint_id,
            "artifact_id": self.artifact_id,
            "package_sha256": self.package_sha256,
            "role": self.role,
        }


@dataclass(frozen=True, slots=True)
class PublishedPackage:
    """A read view over a materialised **published compiler package**.

    Constructed either from a published output directory (:meth:`load`) or from an
    in-memory :class:`~engine.compiler.publishing.PublishedArtifact`
    (:meth:`from_published`). The ``package_sha256`` is recomputed from the
    manifest and cross-checked against the record and signature, so a tampered
    package is rejected at load time (integrity, §12).
    """

    blueprint_id: str
    artifact_id: str
    name: str
    version: str
    root: str
    manifest: dict[str, Any]
    sbom: dict[str, Any]
    signature: dict[str, Any]
    record: dict[str, Any]
    package_sha256: str
    artifact_files: tuple[str, ...]

    @classmethod
    def load(cls, directory: str | Path) -> PublishedPackage:
        """Load a published package from a materialised output directory."""
        root = Path(directory)
        manifest = _read_json(root / MANIFEST_FILE)
        sbom = _read_json(root / SBOM_FILE)
        signature = _read_json(root / SIGNATURE_FILE)
        record = _read_json(root / RECORD_FILE)

        blueprint_id = str(manifest.get("blueprint_id", ""))
        if not blueprint_id:
            raise RuntimeAssemblyError(
                "published package manifest has no blueprint_id", root=str(root)
            )

        package_sha256 = _hash_manifest(manifest)
        _cross_check_hash(package_sha256, record, signature, root)

        artifacts_root = root / "artifacts"
        artifact_files = (
            tuple(
                sorted(
                    p.relative_to(artifacts_root).as_posix()
                    for p in artifacts_root.rglob("*")
                    if p.is_file()
                )
            )
            if artifacts_root.is_dir()
            else ()
        )

        return cls(
            blueprint_id=blueprint_id,
            artifact_id=str(record.get("artifact_id", "")),
            name=str(manifest.get("name", "")),
            version=str(manifest.get("version", "")),
            root=str(root),
            manifest=manifest,
            sbom=sbom,
            signature=signature,
            record=record,
            package_sha256=package_sha256,
            artifact_files=artifact_files,
        )

    @classmethod
    def from_published(cls, published: PublishedArtifact) -> PublishedPackage:
        """Build a :class:`PublishedPackage` from a :class:`PublishedArtifact`."""
        return cls.load(published.output_dir)


@dataclass(frozen=True, slots=True)
class RuntimeUnit:
    """A deployable runtime unit assembled from a certified published package (§8).

    Self-describing and deterministic: it carries the verified provenance chain,
    the signature summary, the SBOM, the resolved pinned dependency closure, the
    deterministic runtime descriptor, and the EC-1 provisional-state disclosure.
    """

    runtime_id: str
    blueprint_id: str
    artifact_id: str
    name: str
    version: str
    package_sha256: str
    provenance_chain: tuple[str, ...]
    signature: dict[str, Any]
    sbom: dict[str, Any]
    dependency_closure: tuple[ClosureEntry, ...]
    secrets: tuple[SecretBinding, ...]
    resources: dict[str, Any]
    descriptor: dict[str, Any]
    environment: str
    disclosure: dict[str, Any] | None = field(default=None)

    @property
    def image_reference(self) -> str:
        """A digest-pinned, immutable container image reference (§8)."""
        return f"ucos-runtime/{k8s_name(self.blueprint_id)}@sha256:{self.package_sha256}"

    def closure_records(self) -> list[dict[str, str]]:
        return [entry.to_dict() for entry in self.dependency_closure]

    def to_dict(self) -> dict[str, Any]:
        """A complete, auditable, JSON-serialisable view of the runtime unit."""
        return {
            "runtime_id": self.runtime_id,
            "blueprint_id": self.blueprint_id,
            "artifact_id": self.artifact_id,
            "name": self.name,
            "version": self.version,
            "package_sha256": self.package_sha256,
            "image_reference": self.image_reference,
            "provenance_chain": list(self.provenance_chain),
            "signature": dict(self.signature),
            "sbom": {
                "format": self.sbom.get("sbom_format"),
                "component_count": len(self.sbom.get("components", [])),
            },
            "dependency_closure": self.closure_records(),
            "secrets": [s.to_dict() for s in self.secrets],
            "resources": dict(self.resources),
            "environment": self.environment,
            "descriptor": self.descriptor,
            "provisional_state_disclosure": self.disclosure,
        }


# --------------------------------------------------------------------------- #
# Public API                                                                   #
# --------------------------------------------------------------------------- #


def k8s_name(blueprint_id: str) -> str:
    """Return a deterministic, RFC-1123-safe name derived from a blueprint id."""
    lowered = blueprint_id.strip().lower()
    safe = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return safe or "runtime"


def assemble(
    package: PublishedPackage | PublishedArtifact,
    *,
    verify_with: Signer,
    dependencies: Iterable[PublishedPackage] = (),
    environment: str = "runtime",
    config_secrets: Mapping[str, SecretRef | str] | None = None,
) -> RuntimeUnit:
    """Assemble a published compiler ``package`` into a deployable :class:`RuntimeUnit`.

    Args:
        package: a published compiler package, either a :class:`PublishedPackage`
            or an in-memory :class:`PublishedArtifact` (materialised on disk).
        verify_with: the :class:`~engine.compiler.signing.Signer` used to verify
            the package signature (and every dependency's signature). Its key is
            held by reference only (SEC-04).
        dependencies: the resolved set of published packages this unit depends on.
            They form the pinned dependency closure together with ``package``.
        environment: the target environment label bound into configuration.
        config_secrets: environment-specific secrets, supplied **by reference
            only** (``env://…`` or :class:`SecretRef`). Inline values are refused.

    Raises:
        ProvenanceValidationError, SignatureValidationError, SBOMValidationError,
        DependencyClosureError, SecretExposureError: on any gate failure.
    """
    if isinstance(package, PublishedArtifact):
        package = PublishedPackage.from_published(package)

    with trace("runtime.assemble", blueprint=package.blueprint_id):
        provenance_chain = _validate_provenance(package)
        _verify_signature(package, verify_with)
        _validate_sbom(package)

        closure = _resolve_closure(package, dependencies, verify_with)
        secrets = _bind_secrets(config_secrets)
        descriptor = _build_descriptor(
            package,
            provenance_chain=provenance_chain,
            closure=closure,
            secrets=secrets,
            environment=environment,
        )
        _assert_no_inline_secrets(descriptor)

        runtime_id = _runtime_id(package, closure)
        descriptor["runtime_id"] = runtime_id

        unit = RuntimeUnit(
            runtime_id=runtime_id,
            blueprint_id=package.blueprint_id,
            artifact_id=package.artifact_id,
            name=package.name,
            version=package.version,
            package_sha256=package.package_sha256,
            provenance_chain=provenance_chain,
            signature=_signature_summary(package),
            sbom=package.sbom,
            dependency_closure=closure,
            secrets=secrets,
            resources=dict(DEFAULT_RESOURCES),
            descriptor=descriptor,
            environment=environment,
        )
        # Every generated runtime carries the EC-1 provisional-state disclosure.
        unit = inject_provisional_state(unit)

    _logger.info(
        "runtime.assembled",
        blueprint=package.blueprint_id,
        runtime_id=runtime_id,
        closure=len(closure),
    )
    return unit


# --------------------------------------------------------------------------- #
# Validation gates                                                             #
# --------------------------------------------------------------------------- #


def _validate_provenance(package: PublishedPackage) -> tuple[str, ...]:
    """Validate the backward-traceability chain across manifest/record/sbom (§1)."""
    chain = _extract_chain(package.manifest, "manifest", package.blueprint_id)
    record_chain = _extract_chain(package.record, "artifact record", package.blueprint_id)
    sbom_chain = _extract_chain(package.sbom, "sbom", package.blueprint_id)

    if not (chain == record_chain == sbom_chain):
        raise ProvenanceValidationError(
            "provenance chain is inconsistent across manifest, record, and SBOM",
            blueprint_id=package.blueprint_id,
        )
    if chain[0] != package.blueprint_id:
        raise ProvenanceValidationError(
            "provenance chain does not originate at the blueprint",
            blueprint_id=package.blueprint_id,
            head=chain[0],
        )
    return chain


def _extract_chain(payload: Mapping[str, Any], source: str, blueprint_id: str) -> tuple[str, ...]:
    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise ProvenanceValidationError(
            "provenance block is missing", blueprint_id=blueprint_id, source=source
        )
    chain = provenance.get("chain")
    if not isinstance(chain, list) or not chain:
        raise ProvenanceValidationError(
            "provenance chain is missing or empty",
            blueprint_id=blueprint_id,
            source=source,
        )
    if not all(isinstance(link, str) and link for link in chain):
        raise ProvenanceValidationError(
            "provenance chain contains an empty or non-string link",
            blueprint_id=blueprint_id,
            source=source,
        )
    return tuple(chain)


def _verify_signature(package: PublishedPackage, signer: Signer) -> None:
    """Verify the package signature (self-consistency + cryptographic, §12/§15)."""
    signature = package.signature
    algorithm = signature.get("algorithm")
    value = signature.get("signature")
    payload_hash = signature.get("payload_sha256")
    if not (algorithm and value and payload_hash):
        raise SignatureValidationError(
            "published package signature is incomplete",
            blueprint_id=package.blueprint_id,
        )
    if signature.get("package_sha256") != package.package_sha256:
        raise SignatureValidationError(
            "signature package hash does not match the manifest",
            blueprint_id=package.blueprint_id,
        )
    if not signer.verify(_reconstruct_signed(package)):
        raise SignatureValidationError(
            "package signature verification failed; assembly is refused",
            blueprint_id=package.blueprint_id,
        )


def _reconstruct_signed(package: PublishedPackage) -> SignedPackage:
    """Reconstruct a :class:`SignedPackage` for verification (reuse of §12 verify)."""
    signature = package.signature
    reconstructed = Package(
        blueprint_id=package.blueprint_id,
        name=package.name,
        version=package.version,
        artifacts=(),
        manifest=package.manifest,
        package_hash=package.package_sha256,
    )
    return SignedPackage(
        package=reconstructed,
        algorithm=str(signature["algorithm"]),
        signature=str(signature["signature"]),
        signing_payload_hash=str(signature["payload_sha256"]),
        key_ref=str(signature.get("key_ref", "")),
        sbom=package.sbom,
    )


def _validate_sbom(package: PublishedPackage) -> None:
    """Validate SBOM presence and structure (§12)."""
    sbom = package.sbom
    if not isinstance(sbom, dict) or not sbom.get("sbom_format"):
        raise SBOMValidationError(
            "SBOM is absent or has no format", blueprint_id=package.blueprint_id
        )
    components = sbom.get("components")
    if not isinstance(components, list) or not components:
        raise SBOMValidationError(
            "SBOM enumerates no components", blueprint_id=package.blueprint_id
        )
    manifest_artifacts = package.manifest.get("artifacts", [])
    if len(components) != len(manifest_artifacts):
        raise SBOMValidationError(
            "SBOM component count does not match the manifest",
            blueprint_id=package.blueprint_id,
            sbom=len(components),
            manifest=len(manifest_artifacts),
        )


# --------------------------------------------------------------------------- #
# Dependency closure & configuration                                          #
# --------------------------------------------------------------------------- #


def _resolve_closure(
    package: PublishedPackage,
    dependencies: Iterable[PublishedPackage],
    signer: Signer,
) -> tuple[ClosureEntry, ...]:
    """Resolve the pinned dependency closure (root + validated dependencies, §8)."""
    entries: list[ClosureEntry] = [
        ClosureEntry(
            blueprint_id=package.blueprint_id,
            artifact_id=package.artifact_id,
            package_sha256=package.package_sha256,
            role="root",
        )
    ]
    seen = {package.blueprint_id}
    for dependency in dependencies:
        if dependency.blueprint_id in seen:
            raise DependencyClosureError(
                "duplicate blueprint id in dependency closure",
                blueprint_id=dependency.blueprint_id,
            )
        seen.add(dependency.blueprint_id)
        # Dependencies are bound only when certified & verifiable (§15).
        _validate_provenance(dependency)
        _verify_signature(dependency, signer)
        _validate_sbom(dependency)
        entries.append(
            ClosureEntry(
                blueprint_id=dependency.blueprint_id,
                artifact_id=dependency.artifact_id,
                package_sha256=dependency.package_sha256,
                role="dependency",
            )
        )
    return tuple(sorted(entries, key=lambda e: (e.role != "root", e.blueprint_id)))


def _bind_secrets(
    config_secrets: Mapping[str, SecretRef | str] | None,
) -> tuple[SecretBinding, ...]:
    """Bind configuration secrets **by reference only** (SEC-04)."""
    if not config_secrets:
        return ()
    bindings: list[SecretBinding] = []
    for name, ref in config_secrets.items():
        if isinstance(ref, SecretRef):
            reference = f"{ref.scheme}://{ref.locator}"
        elif isinstance(ref, str) and SecretRef.is_reference(ref):
            reference = ref
        else:
            raise SecretExposureError(
                "configuration secret must be supplied by reference (e.g. env://VAR)",
                name=name,
            )
        bindings.append(SecretBinding(name=name, ref=reference))
    return tuple(sorted(bindings, key=lambda b: b.name))


def _assert_no_inline_secrets(descriptor: Mapping[str, Any]) -> None:
    """Refuse any secret-like key whose value is not a reference (SEC-04)."""
    for key, value in _walk(descriptor):
        if _SECRET_KEY_PATTERN.search(key) and isinstance(value, str):
            if not SecretRef.is_reference(value):
                raise SecretExposureError(
                    "inline secret value detected in runtime descriptor", key=key
                )


def _walk(node: Any, key: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(node, Mapping):
        for child_key, child in node.items():
            yield from _walk(child, str(child_key))
    elif isinstance(node, list | tuple):
        for child in node:
            yield from _walk(child, key)
    else:
        yield key, node


# --------------------------------------------------------------------------- #
# Descriptor generation                                                        #
# --------------------------------------------------------------------------- #


def _build_descriptor(
    package: PublishedPackage,
    *,
    provenance_chain: tuple[str, ...],
    closure: tuple[ClosureEntry, ...],
    secrets: tuple[SecretBinding, ...],
    environment: str,
) -> dict[str, Any]:
    """Build the deterministic runtime descriptor (no timestamps, sorted, §5)."""
    manifest = package.manifest
    components = sorted(
        (
            {"path": a["path"], "kind": a["kind"], "sha256": a["sha256"]}
            for a in manifest.get("artifacts", [])
        ),
        key=lambda c: c["path"],
    )
    return {
        "runtime_descriptor_format": RUNTIME_DESCRIPTOR_FORMAT,
        "blueprint_id": package.blueprint_id,
        "artifact_id": package.artifact_id,
        "name": package.name,
        "version": package.version,
        "authority": "ENGINEERING-EXECUTION-ONLY",
        "package": {
            "sha256": package.package_sha256,
            "format": manifest.get("package_format"),
        },
        "toolchain": manifest.get("toolchain", {}),
        "provenance": {
            "chain": list(provenance_chain),
            "generation_framework": manifest.get("provenance", {}).get("generation_framework"),
        },
        "components": components,
        "configuration": {
            "environment": environment,
            "secrets_by_reference": [s.to_dict() for s in secrets],
        },
        "resources": dict(DEFAULT_RESOURCES),
        "sbom": {
            "format": package.sbom.get("sbom_format"),
            "component_count": len(package.sbom.get("components", [])),
        },
        "signature": _signature_summary(package),
        "dependency_closure": [entry.to_dict() for entry in closure],
    }


def _signature_summary(package: PublishedPackage) -> dict[str, Any]:
    signature = package.signature
    return {
        "algorithm": signature.get("algorithm"),
        "value": signature.get("signature"),
        "payload_sha256": signature.get("payload_sha256"),
        "key_ref": signature.get("key_ref"),
    }


def _runtime_id(package: PublishedPackage, closure: tuple[ClosureEntry, ...]) -> str:
    """A deterministic, non-authoritative runtime identity (IMP-007 §5/§10)."""
    closure_fingerprint = ";".join(f"{e.blueprint_id}:{e.package_sha256}" for e in closure)
    digest = hashlib.sha256(
        f"{package.artifact_id}:{package.package_sha256}:{closure_fingerprint}".encode()
    ).hexdigest()
    return f"UCOS-RUN-{package.blueprint_id}-{digest[:16]}"


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeAssemblyError("published package is missing a required file", path=str(path))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeAssemblyError(
            "published package file is not valid JSON", path=str(path), detail=str(exc)
        ) from exc
    if not isinstance(data, dict):
        raise RuntimeAssemblyError("published package file is not a JSON object", path=str(path))
    return data


def _cross_check_hash(
    package_sha256: str,
    record: Mapping[str, Any],
    signature: Mapping[str, Any],
    root: Path,
) -> None:
    record_hash = record.get("package", {}).get("sha256")
    signature_hash = signature.get("package_sha256")
    if record_hash != package_sha256 or signature_hash != package_sha256:
        raise RuntimeAssemblyError(
            "published package hash is inconsistent (possible tampering)",
            root=str(root),
            manifest_hash=package_sha256,
            record_hash=record_hash,
            signature_hash=signature_hash,
        )


__all__ = [
    "RUNTIME_DESCRIPTOR_FORMAT",
    "DEFAULT_RESOURCES",
    "SecretBinding",
    "ClosureEntry",
    "PublishedPackage",
    "RuntimeUnit",
    "assemble",
    "k8s_name",
]
