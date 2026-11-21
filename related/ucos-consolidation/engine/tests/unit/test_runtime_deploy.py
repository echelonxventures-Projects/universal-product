"""TASK-000035/000037 — Deployment descriptor + rollback unit tests."""

from __future__ import annotations

import dataclasses

import pytest

from engine.runtime.assembly import PublishedPackage, assemble
from engine.runtime.deploy import (
    ROLLBACK_STRATEGY,
    dependency_closure_record,
    descriptor,
    rollback,
)
from engine.runtime.errors import DeploymentError, DisclosureError


def _unit(published_package, runtime_signer, **kwargs):
    return assemble(published_package, verify_with=runtime_signer, **kwargs)


# -- deployment descriptor ----------------------------------------------------


def test_descriptor_generates_three_manifests(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    deployment = descriptor(unit)
    assert [m["kind"] for m in deployment.kubernetes] == [
        "ConfigMap",
        "Deployment",
        "Service",
    ]
    dep_manifest = deployment.kubernetes[1]
    assert dep_manifest["spec"]["template"]["spec"]["containers"][0]["image"] == (
        unit.image_reference
    )
    assert dep_manifest["metadata"]["namespace"] == "runtime"


def test_descriptor_honours_environment_override(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    deployment = descriptor(unit, environment="production")
    assert deployment.environment == "production"
    assert deployment.kubernetes[0]["metadata"]["namespace"] == "production"


def test_descriptor_binds_secret_env_by_reference(published_package, runtime_signer):
    unit = _unit(
        published_package,
        runtime_signer,
        config_secrets={"UCOS_DB_PASSWORD": "env://UCOS_DB_PASSWORD"},
    )
    deployment = descriptor(unit)
    container = deployment.kubernetes[1]["spec"]["template"]["spec"]["containers"][0]
    env = container["env"]
    assert env[0]["name"] == "UCOS_DB_PASSWORD"
    # value is referenced via secretKeyRef, never inline
    assert env[0]["valueFrom"]["secretKeyRef"]["key"] == "UCOS_DB_PASSWORD"
    assert "value" not in env[0]


def test_descriptor_no_secret_env_when_none(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    container = descriptor(unit).kubernetes[1]["spec"]["template"]["spec"]["containers"][0]
    assert container["env"] == []


def test_descriptor_requires_disclosure(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    stripped = dataclasses.replace(unit, disclosure=None)
    with pytest.raises(DisclosureError):
        descriptor(stripped)


def test_descriptor_refuses_empty_closure(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    broken = dataclasses.replace(unit, dependency_closure=())
    with pytest.raises(DeploymentError):
        descriptor(broken)


def test_descriptor_refuses_unpinned_package(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    broken = dataclasses.replace(unit, package_sha256="")
    with pytest.raises(DeploymentError):
        descriptor(broken)


# -- rollback -----------------------------------------------------------------


def test_rollback_is_reversible_and_checkpointed(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    reverse = rollback(unit)
    assert reverse.reversible is True
    assert reverse.strategy == ROLLBACK_STRATEGY
    assert reverse.reverts_to is None
    assert reverse.checkpoint["image"] == unit.image_reference
    assert reverse.kubernetes_rollback["restore_image"] == unit.image_reference
    assert "kubectl rollout undo" in reverse.kubernetes_rollback["command"]


def test_rollback_reverts_to_previous_when_supplied(
    published_package, dependency_published_package, runtime_signer
):
    current = _unit(published_package, runtime_signer)
    previous = assemble(dependency_published_package, verify_with=runtime_signer)
    reverse = rollback(current, previous=previous)
    assert reverse.reverts_to is not None
    assert reverse.reverts_to["image"] == previous.image_reference
    assert reverse.kubernetes_rollback["restore_image"] == previous.image_reference
    assert "--to-revision-image" in reverse.kubernetes_rollback["command"]


def test_rollback_requires_disclosure(published_package, runtime_signer):
    unit = dataclasses.replace(_unit(published_package, runtime_signer), disclosure=None)
    with pytest.raises(DisclosureError):
        rollback(unit)


# -- closure record + serialisation -------------------------------------------


def test_dependency_closure_record(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    record = dependency_closure_record(unit)
    assert record["dependency_closure_format"] == "ucos-closure/1.0.0"
    assert record["root_package_sha256"] == unit.package_sha256
    assert record["members"][0]["role"] == "root"


def test_descriptors_serialise_to_dict(published_package, runtime_signer):
    unit = _unit(published_package, runtime_signer)
    deployment = descriptor(unit).to_dict()
    reverse = rollback(unit).to_dict()
    assert deployment["deployment_descriptor_format"] == "ucos-deployment/1.0.0"
    assert reverse["rollback_descriptor_format"] == "ucos-rollback/1.0.0"
    assert deployment["provisional_state_disclosure"]["gate"] == "EC-1"
    assert reverse["provisional_state_disclosure"]["gate"] == "EC-1"


def test_from_published_matches_load(published_package):
    a = PublishedPackage.from_published(published_package)
    b = PublishedPackage.load(published_package.output_dir)
    assert a.package_sha256 == b.package_sha256
