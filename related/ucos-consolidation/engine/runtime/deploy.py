"""TASK-000035 — Deployment Descriptor + Rollback (EPIC-005, IMP-007 §8; IP-08).

Generates the deployable, **reversible** deployment definition for a
:class:`~engine.runtime.assembly.RuntimeUnit`:

    * :func:`descriptor` — a :class:`DeploymentDescriptor` bundling deterministic
      **Kubernetes manifests** (ConfigMap, Deployment, Service), a deployment
      descriptor, and the pinned **dependency closure record**. Images are pinned
      **by digest** (immutable deployment); secrets are referenced via
      ``secretKeyRef`` (never inline, SEC-04); provenance and the EC-1
      provisional-state disclosure are stamped onto every manifest.
    * :func:`rollback` — a :class:`RollbackDescriptor` describing a **reversible,
      checkpoint-based** rollback (IP-08): the current pinned state is captured as
      a restorable checkpoint and, when a prior unit is supplied, the exact pinned
      state to revert to is recorded, together with the closure to restore.

The factory generates deployment *definitions* only — it does not deploy to or
mutate any live environment (§8; consumed downstream by IMP-008). Every output is
deterministic (no timestamps, sorted collections) and carries the disclosure, so a
deployment can never imply constitutional finality (DE-05). Stdlib-only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.assembly import RuntimeUnit, k8s_name
from engine.runtime.disclosure import require_disclosure
from engine.runtime.errors import DeploymentError

_logger = get_logger("runtime.deploy")

#: The rollback strategy: reversible and checkpoint-based (IP-08).
ROLLBACK_STRATEGY = "reversible-checkpoint"

_DEFAULT_PORT = 8080


# --------------------------------------------------------------------------- #
# Value types                                                                  #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class DeploymentDescriptor:
    """A complete, deterministic deployment definition for a runtime unit (§8)."""

    runtime_id: str
    blueprint_id: str
    artifact_id: str
    environment: str
    image: str
    kubernetes: tuple[dict[str, Any], ...]
    dependency_closure: tuple[dict[str, str], ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "deployment_descriptor_format": "ucos-deployment/1.0.0",
            "runtime_id": self.runtime_id,
            "blueprint_id": self.blueprint_id,
            "artifact_id": self.artifact_id,
            "environment": self.environment,
            "image": self.image,
            "immutable": True,
            "kubernetes": list(self.kubernetes),
            "dependency_closure": list(self.dependency_closure),
            "provenance_chain": list(self.provenance_chain),
            "provisional_state_disclosure": self.disclosure,
        }


@dataclass(frozen=True, slots=True)
class RollbackDescriptor:
    """A reversible, checkpoint-based rollback definition (IP-08)."""

    runtime_id: str
    blueprint_id: str
    artifact_id: str
    environment: str
    strategy: str
    reversible: bool
    checkpoint: dict[str, Any]
    reverts_to: dict[str, Any] | None
    kubernetes_rollback: dict[str, Any]
    dependency_closure: tuple[dict[str, str], ...]
    disclosure: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "rollback_descriptor_format": "ucos-rollback/1.0.0",
            "runtime_id": self.runtime_id,
            "blueprint_id": self.blueprint_id,
            "artifact_id": self.artifact_id,
            "environment": self.environment,
            "strategy": self.strategy,
            "reversible": self.reversible,
            "checkpoint": self.checkpoint,
            "reverts_to": self.reverts_to,
            "kubernetes_rollback": self.kubernetes_rollback,
            "dependency_closure": list(self.dependency_closure),
            "provisional_state_disclosure": self.disclosure,
        }


# --------------------------------------------------------------------------- #
# Public API                                                                   #
# --------------------------------------------------------------------------- #


def descriptor(unit: RuntimeUnit, *, environment: str | None = None) -> DeploymentDescriptor:
    """Generate the :class:`DeploymentDescriptor` for ``unit`` (§8).

    Raises:
        DisclosureError: if ``unit`` carries no EC-1 provisional-state disclosure
            (a deployment must never be generated without it while gates are open).
    """
    disclosure = require_disclosure(unit.disclosure)
    _ensure_deployable(unit)
    env = environment or unit.environment
    with trace("runtime.deploy.descriptor", runtime=unit.runtime_id):
        manifests = _kubernetes_manifests(unit, env, disclosure)
        deployment = DeploymentDescriptor(
            runtime_id=unit.runtime_id,
            blueprint_id=unit.blueprint_id,
            artifact_id=unit.artifact_id,
            environment=env,
            image=unit.image_reference,
            kubernetes=manifests,
            dependency_closure=tuple(unit.closure_records()),
            provenance_chain=unit.provenance_chain,
            disclosure=disclosure,
        )
    _logger.info(
        "runtime.deploy.descriptor.generated",
        runtime=unit.runtime_id,
        manifests=len(manifests),
        environment=env,
    )
    return deployment


def rollback(
    unit: RuntimeUnit,
    *,
    previous: RuntimeUnit | None = None,
    environment: str | None = None,
) -> RollbackDescriptor:
    """Generate a reversible, checkpoint-based :class:`RollbackDescriptor` (IP-08).

    The checkpoint captures ``unit``'s pinned, digest-addressed state so the
    deployment can be restored to a known-good point. When ``previous`` is given,
    the exact prior pinned state to revert to is recorded as ``reverts_to``.
    """
    disclosure = require_disclosure(unit.disclosure)
    env = environment or unit.environment
    name = k8s_name(unit.blueprint_id)
    with trace("runtime.deploy.rollback", runtime=unit.runtime_id):
        checkpoint = _checkpoint(unit)
        reverts_to = _checkpoint(previous) if previous is not None else None
        kubernetes_rollback = {
            "kind": "RolloutUndo",
            "target": f"deployment/{name}",
            "command": (
                f"kubectl rollout undo deployment/{name} --namespace {env}"
                if reverts_to is None
                else (
                    f"kubectl rollout undo deployment/{name} "
                    f"--to-revision-image {reverts_to['image']} --namespace {env}"
                )
            ),
            "restore_image": (reverts_to or checkpoint)["image"],
        }
        descriptor_out = RollbackDescriptor(
            runtime_id=unit.runtime_id,
            blueprint_id=unit.blueprint_id,
            artifact_id=unit.artifact_id,
            environment=env,
            strategy=ROLLBACK_STRATEGY,
            reversible=True,
            checkpoint=checkpoint,
            reverts_to=reverts_to,
            kubernetes_rollback=kubernetes_rollback,
            dependency_closure=tuple(unit.closure_records()),
            disclosure=disclosure,
        )
    _logger.info(
        "runtime.deploy.rollback.generated",
        runtime=unit.runtime_id,
        reversible=True,
        has_previous=previous is not None,
    )
    return descriptor_out


def dependency_closure_record(unit: RuntimeUnit) -> dict[str, Any]:
    """Return the standalone pinned dependency-closure record for ``unit`` (§8)."""
    return {
        "dependency_closure_format": "ucos-closure/1.0.0",
        "runtime_id": unit.runtime_id,
        "blueprint_id": unit.blueprint_id,
        "root_package_sha256": unit.package_sha256,
        "members": unit.closure_records(),
    }


# --------------------------------------------------------------------------- #
# Kubernetes manifest generation (deterministic)                              #
# --------------------------------------------------------------------------- #


def _checkpoint(unit: RuntimeUnit) -> dict[str, Any]:
    return {
        "runtime_id": unit.runtime_id,
        "artifact_id": unit.artifact_id,
        "package_sha256": unit.package_sha256,
        "image": unit.image_reference,
        "dependency_closure": unit.closure_records(),
    }


def _labels(unit: RuntimeUnit) -> dict[str, str]:
    return {
        "app.kubernetes.io/name": k8s_name(unit.blueprint_id),
        "app.kubernetes.io/version": unit.version,
        "app.kubernetes.io/managed-by": "ucos-runtime-assembly",
        "ucos.dev/blueprint-id": unit.blueprint_id,
        "ucos.dev/artifact-id": unit.artifact_id,
        "ucos.dev/runtime-id": unit.runtime_id,
    }


def _annotations(unit: RuntimeUnit, disclosure: dict[str, Any]) -> dict[str, str]:
    return {
        "ucos.dev/package-sha256": unit.package_sha256,
        "ucos.dev/provenance-chain": ",".join(unit.provenance_chain),
        "ucos.dev/generation-framework": str(
            unit.descriptor.get("provenance", {}).get("generation_framework", "")
        ),
        "ucos.dev/authority": "ENGINEERING-EXECUTION-ONLY",
        "ucos.dev/provisional-state-disclosure": disclosure["disclosure_id"],
        "ucos.dev/provisional-state-statement": disclosure["statement"],
    }


def _kubernetes_manifests(
    unit: RuntimeUnit, environment: str, disclosure: dict[str, Any]
) -> tuple[dict[str, Any], ...]:
    """Emit ConfigMap + Deployment + Service, deterministically ordered (§8)."""
    name = k8s_name(unit.blueprint_id)
    labels = _labels(unit)
    annotations = _annotations(unit, disclosure)
    resources = unit.resources

    config_map = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": f"{name}-config",
            "namespace": environment,
            "labels": labels,
            "annotations": annotations,
        },
        "data": {
            "blueprint_id": unit.blueprint_id,
            "artifact_id": unit.artifact_id,
            "runtime_id": unit.runtime_id,
            "environment": environment,
            "provenance_chain": ",".join(unit.provenance_chain),
        },
    }

    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": name,
            "namespace": environment,
            "labels": labels,
            "annotations": annotations,
        },
        "spec": {
            "replicas": resources["replicas"],
            "selector": {"matchLabels": {"app.kubernetes.io/name": name}},
            "template": {
                "metadata": {"labels": labels, "annotations": annotations},
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": unit.image_reference,
                            "imagePullPolicy": "IfNotPresent",
                            "ports": [{"containerPort": _DEFAULT_PORT}],
                            "envFrom": [{"configMapRef": {"name": f"{name}-config"}}],
                            "env": _secret_env(unit, name),
                            "resources": {
                                "requests": {
                                    "cpu": resources["cpu_request"],
                                    "memory": resources["memory_request"],
                                },
                                "limits": {
                                    "cpu": resources["cpu_limit"],
                                    "memory": resources["memory_limit"],
                                },
                            },
                        }
                    ]
                },
            },
        },
    }

    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": name,
            "namespace": environment,
            "labels": labels,
            "annotations": annotations,
        },
        "spec": {
            "selector": {"app.kubernetes.io/name": name},
            "ports": [{"port": _DEFAULT_PORT, "targetPort": _DEFAULT_PORT}],
            "type": "ClusterIP",
        },
    }

    return (config_map, deployment, service)


def _secret_env(unit: RuntimeUnit, name: str) -> list[dict[str, Any]]:
    """Bind configuration secrets via ``secretKeyRef`` — never inline (SEC-04)."""
    if not unit.secrets:
        return []
    return [
        {
            "name": binding.name,
            "valueFrom": {"secretKeyRef": {"name": f"{name}-secrets", "key": binding.name}},
        }
        for binding in unit.secrets
    ]


def _ensure_deployable(unit: RuntimeUnit) -> None:
    """Refuse to generate a deployment for an unpinned or empty runtime unit (§8)."""
    if not unit.package_sha256:
        raise DeploymentError("runtime unit has no pinned package hash", runtime_id=unit.runtime_id)
    if not unit.dependency_closure:
        raise DeploymentError(
            "runtime unit has an empty dependency closure", runtime_id=unit.runtime_id
        )


__all__ = [
    "ROLLBACK_STRATEGY",
    "DeploymentDescriptor",
    "RollbackDescriptor",
    "descriptor",
    "rollback",
    "dependency_closure_record",
]
