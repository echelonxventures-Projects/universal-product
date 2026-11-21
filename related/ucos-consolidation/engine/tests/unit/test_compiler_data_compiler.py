"""TASK-000023/000029 — Data Blueprint Compiler tests."""

from __future__ import annotations

import json
import py_compile

import pytest

from engine.compiler.data_compiler import (
    ArtifactKind,
    DataBlueprintCompiler,
    provenance_chain,
    snake_case,
)
from engine.compiler.errors import CompilationError
from engine.compiler.parser import parse_document


def _compile(data_blueprint):
    return DataBlueprintCompiler().compile(parse_document(data_blueprint))


def test_snake_case():
    assert snake_case("CustomerOrder") == "customer_order"
    assert snake_case("HTTPServer") == "http_server"
    assert snake_case("already_snake") == "already_snake"


def test_compile_emits_three_artifacts(data_blueprint):
    compiled = _compile(data_blueprint)
    kinds = {a.kind for a in compiled.artifacts}
    assert kinds == {ArtifactKind.SQL_SCHEMA, ArtifactKind.SOURCE, ArtifactKind.CONFIG}
    assert compiled.blueprint_id == "BP-DATA-0001"


def test_sql_schema_content(data_blueprint):
    sql = _compile(data_blueprint).artifact(ArtifactKind.SQL_SCHEMA).content
    assert "CREATE TABLE customer (" in sql
    assert "id UUID NOT NULL" in sql
    assert "email VARCHAR(320) NOT NULL UNIQUE" in sql
    assert "PRIMARY KEY (id)" in sql
    assert "CREATE UNIQUE INDEX ix_customer_email ON customer (email);" in sql
    # provenance embedded (Mandatory Rule 6)
    assert "-- provenance: BP-DATA-0001 <- UCOS-DAT-000007" in sql


def test_source_is_valid_python(tmp_path, data_blueprint):
    source = _compile(data_blueprint).artifact(ArtifactKind.SOURCE).content
    assert "class Customer:" in source
    assert "class CustomerRepository(Protocol):" in source
    assert "def get(self, id: uuid.UUID) -> Customer | None:" in source
    path = tmp_path / "generated.py"
    path.write_text(source, encoding="utf-8")
    py_compile.compile(str(path), doraise=True)  # raises on syntax error


def test_config_is_valid_json_with_provenance(data_blueprint):
    config = _compile(data_blueprint).artifact(ArtifactKind.CONFIG).content
    decoded = json.loads(config)
    assert decoded["table"] == "customer"
    assert decoded["primary_key"] == "id"
    assert decoded["provenance"]["chain"][0] == "BP-DATA-0001"
    assert decoded["provenance"]["generation_framework"] == "UCOS-GEN-000003"
    assert decoded["relationships"][0]["target"] == "BP-DATA-0002"


def test_compile_is_deterministic(data_blueprint):
    first = _compile(data_blueprint)
    second = _compile(data_blueprint)
    assert [a.content_hash for a in first.artifacts] == [a.content_hash for a in second.artifacts]


def test_default_and_bigint_columns(data_blueprint):
    data_blueprint["entity"]["attributes"].append(
        {"name": "score", "data_type": "bigint", "nullable": True, "default": "0"}
    )
    sql = _compile(data_blueprint).artifact(ArtifactKind.SQL_SCHEMA).content
    assert "score BIGINT DEFAULT 0" in sql


def test_provenance_chain_order(data_blueprint):
    chain = provenance_chain(parse_document(data_blueprint))
    assert chain == (
        "BP-DATA-0001",
        "UCOS-DAT-000007",
        "UCOS-REF-000003",
        "UCOS-CAT-000003",
        "UCOS-DAT-000002",
        "UCOS-DAT-000004",
    )


def test_artifact_lookup_missing_kind_raises(data_blueprint):
    compiled = _compile(data_blueprint)
    stripped = compiled.__class__(
        blueprint_id=compiled.blueprint_id,
        provenance_chain=compiled.provenance_chain,
        generation_framework=compiled.generation_framework,
        artifacts=(),
    )
    with pytest.raises(CompilationError):
        stripped.artifact(ArtifactKind.SQL_SCHEMA)
