"""TASK-000027/000029 — Publishing Stage tests (frozen-corpus gate + record)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.compiler.data_compiler import DataBlueprintCompiler
from engine.compiler.errors import PublishingError
from engine.compiler.packaging import Packager
from engine.compiler.parser import parse_document
from engine.compiler.publishing import (
    MANIFEST_FILE,
    RECORD_FILE,
    SBOM_FILE,
    SIGNATURE_FILE,
    Publisher,
)
from engine.compiler.signing import SignedPackage, Signer


def _signed(data_blueprint) -> tuple[SignedPackage, Signer]:
    ir = parse_document(data_blueprint)
    compiled = DataBlueprintCompiler().compile(ir)
    package = Packager().package(compiled, name=ir.name, version=ir.version)
    signer = Signer(key=b"publish-test-key")
    return signer.sign(package), signer


def test_publish_writes_all_files_and_record(tmp_path, data_blueprint):
    signed, signer = _signed(data_blueprint)
    publisher = Publisher(tmp_path)
    assert publisher.output_dir == Path(tmp_path)
    published = publisher.publish(signed, verify_with=signer)

    assert published.artifact_id.startswith("UCOS-CMP-BP-DATA-0001-")
    assert published.record["authority"] == "ENGINEERING-EXECUTION-ONLY"
    assert published.record["provenance"]["chain"][0] == "BP-DATA-0001"
    assert published.record["signature"]["algorithm"] == "HMAC-SHA256"

    target = Path(published.output_dir)
    for filename in (MANIFEST_FILE, SBOM_FILE, SIGNATURE_FILE, RECORD_FILE):
        assert (target / filename).is_file()
    assert (target / "artifacts" / "schema" / "customer.sql").is_file()
    assert (target / "artifacts" / "persistence" / "customer_repository.py").is_file()
    # record round-trips as JSON
    record_on_disk = json.loads((target / RECORD_FILE).read_text())
    assert record_on_disk["blueprint_id"] == "BP-DATA-0001"


def test_publish_refuses_unverified_signature(tmp_path, data_blueprint):
    signed, _ = _signed(data_blueprint)
    other_signer = Signer(key=b"a-different-key")
    with pytest.raises(PublishingError) as exc:
        Publisher(tmp_path).publish(signed, verify_with=other_signer)
    assert "verification failed" in exc.value.message


def test_publish_refuses_frozen_corpus_output(monkeypatch, tmp_path, data_blueprint):
    signed, signer = _signed(data_blueprint)
    # Run from a temp cwd and target 00-BOOK — the frozen-path guard must block it.
    monkeypatch.chdir(tmp_path)
    publisher = Publisher("00-BOOK/output")
    with pytest.raises(PublishingError) as exc:
        publisher.publish(signed, verify_with=signer)
    assert "read-only certified corpus" in exc.value.message


def test_published_record_is_deterministic(tmp_path, data_blueprint):
    signed, signer = _signed(data_blueprint)
    first = Publisher(tmp_path / "a").publish(signed, verify_with=signer)
    second = Publisher(tmp_path / "b").publish(signed, verify_with=signer)
    assert first.artifact_id == second.artifact_id
    assert first.record == second.record
