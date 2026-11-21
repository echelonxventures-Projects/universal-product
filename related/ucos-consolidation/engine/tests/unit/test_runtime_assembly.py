"""TASK-000034/000037 — Runtime Assembly Engine unit tests (gates + determinism)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.compiler.publishing import (
    MANIFEST_FILE,
    RECORD_FILE,
    SBOM_FILE,
)
from engine.compiler.signing import Signer
from engine.foundation.config.config import SecretRef
from engine.runtime.assembly import (
    DEFAULT_RESOURCES,
    PublishedPackage,
    assemble,
    k8s_name,
)
from engine.runtime.errors import (
    DependencyClosureError,
    ProvenanceValidationError,
    RuntimeAssemblyError,
    SBOMValidationError,
    SecretExposureError,
    SignatureValidationError,
)


def _load(published) -> PublishedPackage:
    return PublishedPackage.from_published(published)


def _rewrite(root: Path, filename: str, mutate) -> None:
    path = root / filename
    data = json.loads(path.read_text())
    mutate(data)
    path.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")


# -- PublishedPackage loading -------------------------------------------------


def test_load_computes_and_cross_checks_hash(published_package):
    package = PublishedPackage.load(published_package.output_dir)
    assert package.blueprint_id == "BP-DATA-0001"
    assert package.package_sha256 == package.record["package"]["sha256"]
    assert package.artifact_files  # generated artifacts discovered


def test_load_rejects_tampered_manifest(published_package):
    root = Path(published_package.output_dir)
    _rewrite(root, MANIFEST_FILE, lambda d: d.update({"name": "Tampered"}))
    with pytest.raises(RuntimeAssemblyError) as exc:
        PublishedPackage.load(root)
    assert "inconsistent" in exc.value.message


def test_load_rejects_missing_file(published_package):
    root = Path(published_package.output_dir)
    (root / SBOM_FILE).unlink()
    with pytest.raises(RuntimeAssemblyError) as exc:
        PublishedPackage.load(root)
    assert "missing a required file" in exc.value.message


def test_load_rejects_non_object_json(published_package, tmp_path):
    root = Path(published_package.output_dir)
    (root / MANIFEST_FILE).write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(RuntimeAssemblyError):
        PublishedPackage.load(root)


def test_load_rejects_invalid_json(published_package):
    root = Path(published_package.output_dir)
    (root / RECORD_FILE).write_text("{not json", encoding="utf-8")
    with pytest.raises(RuntimeAssemblyError) as exc:
        PublishedPackage.load(root)
    assert "not valid JSON" in exc.value.message


def test_load_rejects_manifest_without_blueprint_id(published_package):
    root = Path(published_package.output_dir)
    _rewrite(root, MANIFEST_FILE, lambda d: d.pop("blueprint_id"))
    with pytest.raises(RuntimeAssemblyError):
        PublishedPackage.load(root)


# -- provenance gate ----------------------------------------------------------


def test_provenance_missing_block_rejected(published_package, runtime_signer):
    root = Path(published_package.output_dir)
    _rewrite(root, SBOM_FILE, lambda d: d.update({"provenance": {}}))
    with pytest.raises(ProvenanceValidationError):
        assemble(PublishedPackage.load(root), verify_with=runtime_signer)


def test_provenance_non_mapping_block_rejected(published_package, runtime_signer):
    package = _load(published_package)
    package.manifest["provenance"] = "not-a-mapping"
    with pytest.raises(ProvenanceValidationError) as exc:
        assemble(package, verify_with=runtime_signer)
    assert "block is missing" in exc.value.message


def test_provenance_inconsistent_rejected(published_package, runtime_signer):
    package = _load(published_package)
    # mutate one copy of the chain so manifest/record/sbom disagree
    package.sbom["provenance"]["chain"] = ["BP-DATA-0001", "TAMPERED"]
    with pytest.raises(ProvenanceValidationError) as exc:
        assemble(package, verify_with=runtime_signer)
    assert "inconsistent" in exc.value.message


def test_provenance_empty_chain_rejected(published_package, runtime_signer):
    package = _load(published_package)
    for payload in (package.manifest, package.record, package.sbom):
        payload["provenance"]["chain"] = []
    with pytest.raises(ProvenanceValidationError):
        assemble(package, verify_with=runtime_signer)


def test_provenance_non_string_link_rejected(published_package, runtime_signer):
    package = _load(published_package)
    for payload in (package.manifest, package.record, package.sbom):
        payload["provenance"]["chain"] = ["BP-DATA-0001", ""]
    with pytest.raises(ProvenanceValidationError):
        assemble(package, verify_with=runtime_signer)


def test_provenance_wrong_head_rejected(published_package, runtime_signer):
    package = _load(published_package)
    for payload in (package.manifest, package.record, package.sbom):
        payload["provenance"]["chain"] = ["NOT-THE-BLUEPRINT", "x"]
    with pytest.raises(ProvenanceValidationError) as exc:
        assemble(package, verify_with=runtime_signer)
    assert "originate" in exc.value.message


# -- signature gate -----------------------------------------------------------


def test_signature_wrong_key_rejected(published_package):
    with pytest.raises(SignatureValidationError):
        assemble(published_package, verify_with=Signer(key=b"nope"))


def test_signature_incomplete_rejected(published_package, runtime_signer):
    package = _load(published_package)
    package.signature.pop("payload_sha256")
    with pytest.raises(SignatureValidationError) as exc:
        assemble(package, verify_with=runtime_signer)
    assert "incomplete" in exc.value.message


def test_signature_hash_mismatch_rejected(published_package, runtime_signer):
    package = _load(published_package)
    package.signature["package_sha256"] = "0" * 64
    with pytest.raises(SignatureValidationError) as exc:
        assemble(package, verify_with=runtime_signer)
    assert "does not match" in exc.value.message


# -- SBOM gate ----------------------------------------------------------------


def test_sbom_absent_rejected(published_package, runtime_signer):
    package = _load(published_package)
    package.sbom.pop("sbom_format")
    with pytest.raises(SBOMValidationError):
        assemble(package, verify_with=runtime_signer)


def test_sbom_no_components_rejected(published_package, runtime_signer):
    package = _load(published_package)
    package.sbom["components"] = []
    with pytest.raises(SBOMValidationError):
        assemble(package, verify_with=runtime_signer)


def test_sbom_count_mismatch_rejected(published_package, runtime_signer):
    package = _load(published_package)
    package.sbom["components"] = package.sbom["components"][:-1]
    with pytest.raises(SBOMValidationError) as exc:
        assemble(package, verify_with=runtime_signer)
    assert "does not match the manifest" in exc.value.message


# -- secrets-by-reference gate ------------------------------------------------


def test_secrets_bound_by_reference(published_package, runtime_signer):
    unit = assemble(
        published_package,
        verify_with=runtime_signer,
        config_secrets={"UCOS_DB_PASSWORD": "env://UCOS_DB_PASSWORD"},
    )
    assert unit.secrets[0].name == "UCOS_DB_PASSWORD"
    assert unit.secrets[0].ref == "env://UCOS_DB_PASSWORD"
    bound = unit.descriptor["configuration"]["secrets_by_reference"]
    assert bound == [{"name": "UCOS_DB_PASSWORD", "ref": "env://UCOS_DB_PASSWORD"}]


def test_secrets_accept_secretref_instance(published_package, runtime_signer):
    unit = assemble(
        published_package,
        verify_with=runtime_signer,
        config_secrets={"TOKEN": SecretRef("env://UCOS_TOKEN")},
    )
    assert unit.secrets[0].ref == "env://UCOS_TOKEN"


def test_inline_secret_value_refused(published_package, runtime_signer):
    with pytest.raises(SecretExposureError):
        assemble(
            published_package,
            verify_with=runtime_signer,
            config_secrets={"password": "hunter2-inline"},
        )


def test_descriptor_secret_scan_guard():
    """The defensive descriptor scan refuses an inline secret-like value (SEC-04)."""
    from engine.runtime.assembly import _assert_no_inline_secrets

    _assert_no_inline_secrets({"configuration": {"api_key": "env://UCOS_API_KEY"}})
    with pytest.raises(SecretExposureError):
        _assert_no_inline_secrets({"configuration": {"api_key": "inline-value"}})


# -- dependency closure -------------------------------------------------------


def test_duplicate_dependency_rejected(published_package, runtime_signer):
    dep = _load(published_package)  # same blueprint id as the root
    with pytest.raises(DependencyClosureError):
        assemble(published_package, verify_with=runtime_signer, dependencies=[dep])


def test_closure_root_only_by_default(published_package, runtime_signer):
    unit = assemble(published_package, verify_with=runtime_signer)
    assert [e.role for e in unit.dependency_closure] == ["root"]


# -- helpers & descriptor -----------------------------------------------------


def test_k8s_name_normalizes():
    assert k8s_name("BP-DATA-0001") == "bp-data-0001"
    assert k8s_name("!!!") == "runtime"


def test_default_resources_bound(published_package, runtime_signer):
    unit = assemble(published_package, verify_with=runtime_signer)
    assert unit.resources == DEFAULT_RESOURCES
    assert unit.descriptor["resources"]["replicas"] == 1


def test_to_dict_is_serialisable(published_package, runtime_signer):
    unit = assemble(published_package, verify_with=runtime_signer)
    blob = json.dumps(unit.to_dict(), sort_keys=True)
    assert "UCOS-RUN-BP-DATA-0001-" in blob
