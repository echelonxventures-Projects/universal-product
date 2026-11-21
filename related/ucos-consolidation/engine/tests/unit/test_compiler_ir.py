"""TASK-000017/000029 — IR model, type system, errors, and gap-report tests."""

from __future__ import annotations

import pytest

from engine.compiler.errors import CompilationError, CompilerError, ParseError
from engine.compiler.gap import GapReport, Stage
from engine.compiler.ir import (
    IR_VERSION,
    Attribute,
    BlueprintFamily,
    BlueprintIR,
    Certification,
    CertificationStatus,
    DataRelationship,
    Entity,
    Index,
    Provenance,
    RelationshipKind,
)
from engine.compiler.types import DataType, python_type, sql_type
from engine.foundation.obs.errors import FoundationError

# -- type system --------------------------------------------------------------


def test_datatype_coerce_and_bindings():
    assert DataType.coerce("uuid", context="x") is DataType.UUID
    assert sql_type(DataType.STRING, max_length=64) == "VARCHAR(64)"
    assert sql_type(DataType.STRING) == "VARCHAR"
    # length ignored for non-length-bearing types
    assert sql_type(DataType.INTEGER, max_length=10) == "INTEGER"
    assert python_type(DataType.TIMESTAMP) == "datetime.datetime"


def test_datatype_coerce_rejects_unknown():
    with pytest.raises(CompilationError) as exc:
        DataType.coerce("not-a-type", context="attr")
    assert exc.value.context["at"] == "attr"


# -- enums --------------------------------------------------------------------


def test_family_and_status_coercion():
    assert BlueprintFamily.coerce("BP-DATA", context="x") is BlueprintFamily.DATA
    assert CertificationStatus.coerce("CERTIFIED", context="x") is CertificationStatus.CERTIFIED
    assert RelationshipKind.coerce("one_to_many", context="x") is RelationshipKind.ONE_TO_MANY
    for bad, enum in (
        ("BP-NOPE", BlueprintFamily),
        ("MAYBE", CertificationStatus),
        ("sideways", RelationshipKind),
    ):
        with pytest.raises(ParseError):
            enum.coerce(bad, context="x")


# -- provenance ---------------------------------------------------------------


def _provenance() -> Provenance:
    return Provenance(
        canonical_source="UCOS-DAT-000007",
        reference_architecture="UCOS-REF-000003",
        runtime_catalog="UCOS-CAT-000003",
        architecture_constitution="UCOS-DAT-000002",
        ontology_root="UCOS-DAT-000004",
        generation_framework="UCOS-GEN-000003",
    )


def test_provenance_references_ordered():
    prov = _provenance()
    assert prov.references()[0] == "UCOS-DAT-000007"
    assert len(prov.references()) == 6


def test_provenance_rejects_blank_reference():
    with pytest.raises(ParseError):
        Provenance(
            canonical_source="",
            reference_architecture="r",
            runtime_catalog="c",
            architecture_constitution="a",
            ontology_root="o",
            generation_framework="g",
        )


# -- attributes / entity ------------------------------------------------------


def test_attribute_invariants():
    attr = Attribute(name="id", data_type=DataType.UUID, nullable=False, primary_key=True)
    assert attr.primary_key
    with pytest.raises(ParseError):
        Attribute(name="", data_type=DataType.UUID)
    with pytest.raises(ParseError):
        Attribute(name="x", data_type="uuid")  # type: ignore[arg-type]
    with pytest.raises(ParseError):
        Attribute(name="x", data_type=DataType.STRING, max_length=0)
    with pytest.raises(ParseError):
        Attribute(name="x", data_type=DataType.UUID, primary_key=True, nullable=True)


def test_index_and_relationship_invariants():
    Index(name="ix", columns=("a",))
    with pytest.raises(ParseError):
        Index(name="ix", columns=())
    DataRelationship(name="r", target="BP-DATA-0002", kind=RelationshipKind.ONE_TO_MANY)
    with pytest.raises(ParseError):
        DataRelationship(name="r", target="", kind=RelationshipKind.ONE_TO_MANY)
    with pytest.raises(ParseError):
        DataRelationship(name="r", target="t", kind="one_to_many")  # type: ignore[arg-type]


def test_entity_invariants_and_primary_key():
    entity = Entity(
        name="Customer",
        table="customer",
        attributes=(
            Attribute(name="id", data_type=DataType.UUID, nullable=False, primary_key=True),
            Attribute(name="email", data_type=DataType.STRING),
        ),
        indexes=(Index(name="ix", columns=("email",)),),
    )
    assert entity.primary_key[0].name == "id"

    with pytest.raises(ParseError):  # no attributes
        Entity(name="E", table="e", attributes=())
    with pytest.raises(ParseError):  # duplicate attribute
        Entity(
            name="E",
            table="e",
            attributes=(
                Attribute(name="a", data_type=DataType.INTEGER),
                Attribute(name="a", data_type=DataType.INTEGER),
            ),
        )
    with pytest.raises(ParseError):  # index on unknown column
        Entity(
            name="E",
            table="e",
            attributes=(Attribute(name="a", data_type=DataType.INTEGER),),
            indexes=(Index(name="ix", columns=("nope",)),),
        )


# -- blueprint IR -------------------------------------------------------------


def _entity() -> Entity:
    return Entity(
        name="Customer",
        table="customer",
        attributes=(
            Attribute(name="id", data_type=DataType.UUID, nullable=False, primary_key=True),
        ),
    )


def test_blueprint_ir_create_and_defaults():
    ir = BlueprintIR.create(
        blueprint_id="BP-DATA-0001",
        family=BlueprintFamily.DATA,
        name="Customer",
        version="1.0.0",
        certification=Certification(status=CertificationStatus.CERTIFIED),
        provenance=_provenance(),
        entity=_entity(),
        dependencies=["BP-DATA-0002"],
    )
    assert ir.ir_version == IR_VERSION
    assert ir.dependencies == ("BP-DATA-0002",)
    assert ir.certification.is_certified


def test_blueprint_ir_family_prefix_enforced():
    with pytest.raises(ParseError):
        BlueprintIR.create(
            blueprint_id="BP-EVENT-1",
            family=BlueprintFamily.DATA,
            name="X",
            version="1.0.0",
            certification=Certification(status=CertificationStatus.CERTIFIED),
            provenance=_provenance(),
            entity=_entity(),
        )


def test_blueprint_ir_rejects_self_and_duplicate_dependency():
    with pytest.raises(ParseError):
        BlueprintIR.create(
            blueprint_id="BP-DATA-0001",
            family=BlueprintFamily.DATA,
            name="X",
            version="1.0.0",
            certification=Certification(status=CertificationStatus.CERTIFIED),
            provenance=_provenance(),
            entity=_entity(),
            dependencies=["BP-DATA-0001"],
        )
    with pytest.raises(ParseError):
        BlueprintIR.create(
            blueprint_id="BP-DATA-0001",
            family=BlueprintFamily.DATA,
            name="X",
            version="1.0.0",
            certification=Certification(status=CertificationStatus.CERTIFIED),
            provenance=_provenance(),
            entity=_entity(),
            dependencies=["BP-DATA-0002", "BP-DATA-0002"],
        )


def test_blueprint_ir_type_guards():
    kwargs = dict(
        blueprint_id="BP-DATA-0001",
        family=BlueprintFamily.DATA,
        name="X",
        version="1.0.0",
        certification=Certification(status=CertificationStatus.CERTIFIED),
        provenance=_provenance(),
        entity=_entity(),
    )
    with pytest.raises(ParseError):
        BlueprintIR.create(**{**kwargs, "family": "BP-DATA"})  # type: ignore[arg-type]
    with pytest.raises(ParseError):
        BlueprintIR.create(**{**kwargs, "certification": object()})  # type: ignore[arg-type]
    with pytest.raises(ParseError):
        BlueprintIR.create(**{**kwargs, "provenance": object()})  # type: ignore[arg-type]
    with pytest.raises(ParseError):
        BlueprintIR.create(**{**kwargs, "entity": object()})  # type: ignore[arg-type]


# -- errors / gap report ------------------------------------------------------


def test_error_hierarchy_rooted_in_foundation():
    assert issubclass(CompilerError, FoundationError)
    err = ParseError("bad", at="x")
    assert err.code == "CMP-PARSE-001"
    assert err.to_dict()["context"] == {"at": "x"}


def test_gap_report_from_error_and_serialisation():
    err = ParseError("boom", detail="d")
    report = GapReport.from_error(Stage.PARSE, err, blueprint_id="BP-DATA-0001")
    payload = report.to_dict()
    assert payload["gap_report"] is True
    assert payload["stage"] == "parse"
    assert payload["code"] == "CMP-PARSE-001"
    assert payload["blueprint_id"] == "BP-DATA-0001"
    assert payload["context"] == {"detail": "d"}


def test_gap_report_without_context_or_blueprint():
    report = GapReport(stage=Stage.SIGN, code="CMP-SIGN-001", message="m")
    payload = report.to_dict()
    assert "context" not in payload
    assert "blueprint_id" not in payload
