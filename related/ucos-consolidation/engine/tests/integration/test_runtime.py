"""TASK-000037 — Runtime Assembly Validation (EPIC-005, IMP-007 §8).

Proves the EPIC-005 success criterion end to end: a compiled, published BP-DATA
artifact is transformed into a **deployable runtime unit**, a **deployment
descriptor**, and a **rollback descriptor**, with provenance, signature
verification, SBOM verification, and the EC-1 provisional-state disclosure all
preserved through packaging and deployment generation.

The published package consumed here is produced by the real EPIC-003 compiler
pipeline against the certified compiler substrate (see ``conftest``); no fixture
short-circuits the runtime engine.
"""

from __future__ import annotations

import json

import pytest

from engine.runtime import (
    DISCLOSURE_ID,
    PublishedPackage,
    RuntimeUnit,
    assemble,
    dependency_closure_record,
    descriptor,
    disclosure_present,
    rollback,
)
from engine.runtime.deploy import DeploymentDescriptor, RollbackDescriptor
from engine.runtime.errors import SignatureValidationError

# -- SUCCESS CRITERION --------------------------------------------------------


def test_published_artifact_becomes_deployable_runtime_unit(published_package, runtime_signer):
    """A published BP-DATA artifact assembles into a deployable RuntimeUnit."""
    unit = assemble(published_package, verify_with=runtime_signer)

    assert isinstance(unit, RuntimeUnit)
    assert unit.blueprint_id == "BP-DATA-0001"
    assert unit.runtime_id.startswith("UCOS-RUN-BP-DATA-0001-")
    assert unit.artifact_id.startswith("UCOS-CMP-BP-DATA-0001-")
    # digest-pinned, immutable image reference
    assert unit.image_reference == f"ucos-runtime/bp-data-0001@sha256:{unit.package_sha256}"
    # descriptor is complete and self-describing
    assert unit.descriptor["runtime_descriptor_format"] == "ucos-runtime/1.0.0"
    assert unit.descriptor["runtime_id"] == unit.runtime_id
    assert unit.descriptor["components"]  # generated components bound


def test_deployment_and_rollback_descriptors_generated(published_package, runtime_signer):
    """Assembly yields both a deployment descriptor and a reversible rollback path."""
    unit = assemble(published_package, verify_with=runtime_signer)

    deployment = descriptor(unit)
    assert isinstance(deployment, DeploymentDescriptor)
    kinds = [m["kind"] for m in deployment.kubernetes]
    assert kinds == ["ConfigMap", "Deployment", "Service"]
    assert deployment.image == unit.image_reference
    assert deployment.to_dict()["immutable"] is True

    reverse = rollback(unit)
    assert isinstance(reverse, RollbackDescriptor)
    assert reverse.reversible is True
    assert reverse.strategy == "reversible-checkpoint"
    assert reverse.checkpoint["package_sha256"] == unit.package_sha256
    assert "kubectl rollout undo" in reverse.kubernetes_rollback["command"]


def test_provenance_preserved(published_package, runtime_signer):
    """The backward-traceability chain survives assembly and deployment generation."""
    unit = assemble(published_package, verify_with=runtime_signer)
    assert unit.provenance_chain[0] == "BP-DATA-0001"
    assert unit.descriptor["provenance"]["chain"] == list(unit.provenance_chain)

    deployment = descriptor(unit)
    assert deployment.provenance_chain == unit.provenance_chain
    # provenance is stamped onto every generated manifest annotation
    for manifest in deployment.kubernetes:
        assert manifest["metadata"]["annotations"]["ucos.dev/provenance-chain"] == ",".join(
            unit.provenance_chain
        )


def test_signature_verified(published_package, runtime_signer):
    """Assembly verifies the package signature; a wrong key is refused."""
    # correct key → verified
    unit = assemble(published_package, verify_with=runtime_signer)
    assert unit.signature["algorithm"] == "HMAC-SHA256"

    # wrong key → refused
    from engine.compiler.signing import Signer

    with pytest.raises(SignatureValidationError):
        assemble(published_package, verify_with=Signer(key=b"the-wrong-key"))


def test_sbom_verified(published_package, runtime_signer):
    """The SBOM is present and its component count matches the manifest."""
    unit = assemble(published_package, verify_with=runtime_signer)
    package = PublishedPackage.from_published(published_package)
    assert unit.sbom["sbom_format"].startswith("ucos-sbom/")
    assert len(unit.sbom["components"]) == len(package.manifest["artifacts"])
    assert unit.descriptor["sbom"]["component_count"] == len(unit.sbom["components"])


def test_disclosure_present_and_survives(published_package, runtime_signer):
    """The EC-1 provisional-state disclosure is present on the unit and every descriptor."""
    unit = assemble(published_package, verify_with=runtime_signer)
    assert disclosure_present(unit.disclosure)
    assert unit.disclosure["disclosure_id"] == DISCLOSURE_ID
    assert unit.disclosure["asserts_constitutional_finality"] is False
    # survives into the descriptor
    assert unit.descriptor["provisional_state_disclosure"]["disclosure_id"] == DISCLOSURE_ID

    deployment = descriptor(unit)
    assert deployment.disclosure["disclosure_id"] == DISCLOSURE_ID
    for manifest in deployment.kubernetes:
        annotations = manifest["metadata"]["annotations"]
        assert annotations["ucos.dev/provisional-state-disclosure"] == DISCLOSURE_ID

    reverse = rollback(unit)
    assert reverse.disclosure["disclosure_id"] == DISCLOSURE_ID


# -- DEPENDENCY CLOSURE -------------------------------------------------------


def test_dependency_closure_resolved_and_recorded(
    published_package, dependency_published_package, runtime_signer
):
    """A supplied dependency is validated and pinned into the closure record."""
    dependency = PublishedPackage.from_published(dependency_published_package)
    unit = assemble(published_package, verify_with=runtime_signer, dependencies=[dependency])

    ids = {entry.blueprint_id for entry in unit.dependency_closure}
    assert ids == {"BP-DATA-0001", "BP-DATA-0002"}
    roles = {entry.blueprint_id: entry.role for entry in unit.dependency_closure}
    assert roles["BP-DATA-0001"] == "root"
    assert roles["BP-DATA-0002"] == "dependency"

    record = dependency_closure_record(unit)
    assert record["root_package_sha256"] == unit.package_sha256
    assert len(record["members"]) == 2


# -- DETERMINISM --------------------------------------------------------------


def test_assembly_is_deterministic(published_package, runtime_signer):
    """Identical published package + closure ⇒ byte-identical descriptor + runtime_id."""
    a = assemble(published_package, verify_with=runtime_signer)
    b = assemble(published_package, verify_with=runtime_signer)
    assert a.runtime_id == b.runtime_id
    assert json.dumps(a.descriptor, sort_keys=True) == json.dumps(b.descriptor, sort_keys=True)

    da = json.dumps(descriptor(a).to_dict(), sort_keys=True)
    db = json.dumps(descriptor(b).to_dict(), sort_keys=True)
    assert da == db
