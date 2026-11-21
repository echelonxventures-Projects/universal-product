"""TASK-000026/000029 — Signing Stage tests (deterministic signature + SBOM)."""

from __future__ import annotations

import pytest

from engine.compiler.data_compiler import DataBlueprintCompiler
from engine.compiler.errors import SigningError
from engine.compiler.packaging import Packager
from engine.compiler.parser import parse_document
from engine.compiler.signing import SIGNATURE_ALGORITHM, Signer
from engine.foundation.config.config import SecretRef


def _package(data_blueprint):
    ir = parse_document(data_blueprint)
    compiled = DataBlueprintCompiler().compile(ir)
    return Packager().package(compiled, name=ir.name, version=ir.version)


def test_sign_is_deterministic_and_verifies(data_blueprint):
    package = _package(data_blueprint)
    signer = Signer(key=b"unit-test-key")
    a = signer.sign(package)
    b = signer.sign(package)
    assert a.signature == b.signature
    assert a.algorithm == SIGNATURE_ALGORITHM
    assert a.blueprint_id == "BP-DATA-0001"
    assert signer.verify(a)


def test_sbom_enumerates_artifacts(data_blueprint):
    signed = Signer(key=b"k").sign(_package(data_blueprint))
    sbom = signed.sbom
    assert sbom["package"]["blueprint_id"] == "BP-DATA-0001"
    assert len(sbom["components"]) == 3
    assert sbom["provenance"]["chain"][0] == "BP-DATA-0001"


def test_verify_fails_for_different_key(data_blueprint):
    package = _package(data_blueprint)
    signed = Signer(key=b"key-one").sign(package)
    assert not Signer(key=b"key-two").verify(signed)


def test_key_ref_label_never_leaks_secret_value(data_blueprint, monkeypatch):
    monkeypatch.setenv("UCOS_TEST_SIGNING_KEY", "s3cr3t-value")
    signer = Signer(key_ref="env://UCOS_TEST_SIGNING_KEY")
    signed = signer.sign(_package(data_blueprint))
    assert signed.key_ref == "env://UCOS_TEST_SIGNING_KEY"
    assert "s3cr3t-value" not in str(signed.key_ref)
    assert signer.verify(signed)


def test_secret_ref_instance_accepted(data_blueprint, monkeypatch):
    monkeypatch.setenv("UCOS_TEST_SIGNING_KEY", "abc")
    signer = Signer(key_ref=SecretRef("env://UCOS_TEST_SIGNING_KEY"))
    assert signer.verify(signer.sign(_package(data_blueprint)))


def test_signer_requires_a_key():
    with pytest.raises(SigningError):
        Signer()


def test_signer_rejects_non_bytes_key():
    with pytest.raises(SigningError):
        Signer(key="not-bytes")  # type: ignore[arg-type]


def test_signer_rejects_empty_resolved_key(data_blueprint, monkeypatch):
    monkeypatch.setenv("UCOS_EMPTY_KEY", "")
    signer = Signer(key_ref="env://UCOS_EMPTY_KEY")
    with pytest.raises(SigningError):
        signer.sign(_package(data_blueprint))
