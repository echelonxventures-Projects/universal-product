"""EC3-B10-U04 — Schema validation tests (EC-1 PASS + V1…V5 + UDL-10 + VC)."""

from __future__ import annotations

from dataclasses import replace

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.schema import entity_schema_for
from data.schema_traceability import build_schema_traceability
from data.schema_validation import (
    SchemaValidationSubject,
    schema_checks,
    validate_schema,
)
from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine

ENTITY_NAME = "ucos.demo.entity"
SCHEMA_NAME = "ucos.demo.schema"


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _schema(**overrides):
    entity = overrides.pop("entity", _entity())
    return entity_schema_for(
        entity,
        name=overrides.pop("name", SCHEMA_NAME),
        type_tag=overrides.pop("type_tag", "ucos.core.schema"),
        **overrides,
    )


def _trace(schema):
    return build_schema_traceability(schema, unit="EC3-B10-U04", forward=(schema.schema_id,))


def test_validation_passes_and_is_accepted():
    s = _schema()
    result = validate_schema(s, _trace(s))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    s = _schema()
    result = validate_schema(s, _trace(s))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(schema_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_v1_v5_all_hold():
    s = _schema()
    result = validate_schema(s, _trace(s))
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["meta-class-single"]  # V1 (DMC-05)
    assert passed["meta-relationships-closed"]  # V2
    assert passed["meta-constraints"]  # V3 (DSA-K1/K3)
    assert passed["founding-acyclic"]  # V4
    assert passed["lifecycle-valid"]  # V5


def test_schema_explicitness_udl10_checks_present_and_pass():
    s = _schema()
    result = validate_schema(s, _trace(s))
    passed = {f.check_id: f.passed for f in result.report.findings}
    for cid in (
        "schema-typed",  # DSA-03 / UDL-03
        "schema-named",  # DSA-01
        "schema-identified",  # UDL-04/05
        "schema-explicit-structure",  # UDL-10 / DSA-01
        "schema-elements-typed",  # DSA-03 / DSA-C3
        "schema-conformance-decidable",  # DSA-02 / DSA-C2
        "schema-describes-subject",  # DMR-04 / DSA-09
        "schema-composition-acyclic",  # DSA-05 / DSA-C1
        "schema-versioned",  # DSA-06
        "schema-classified",  # DXH-05
        "data-value-fidelity",  # UDL-06 (transitive)
        "foundation-reuse-integrity",  # UDL-02 / VC-5
        "storage-independence",  # UDL-11 / DSA-07
        "non-constitutive",  # UDL-15 / DSA-09
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_shared_check_ids_present_for_cce_gate_reuse():
    # These ids are consumed by the reused DMC-01 CCE ten-gate suite.
    s = _schema()
    result = validate_schema(s, _trace(s))
    ids = {f.check_id for f in result.report.findings}
    for cid in (
        "meta-class-single",
        "meta-relationships-closed",
        "foundation-reuse-integrity",
        "data-value-fidelity",
        "founding-acyclic",
        "provisional-state-disclosure",
        "traceability-rooted",
    ):
        assert cid in ids, cid


def test_subject_projection_is_deterministic():
    s = _schema()
    s1 = SchemaValidationSubject.from_schema(s, _trace(s))
    s2 = SchemaValidationSubject.from_schema(s, _trace(s))
    assert s1 == s2  # determinism at the subject boundary


def test_untraced_schema_fails_traceability_gate():
    s = _schema()
    subject = SchemaValidationSubject.from_schema(s, _trace(s))
    subject = replace(subject, provenance_chain=())  # orphaned lineage
    report = ValidationEngine(schema_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


def test_secret_bearing_schema_fails_non_constitutive_gate():
    s = _schema(name="api_key")
    result = validate_schema(s, _trace(s))
    assert result.accepted is False
    assert "non-constitutive" in {f.check_id for f in result.report.blocking_failures}


def test_untyped_element_subject_fails_elements_typed_gate():
    s = _schema()
    subject = SchemaValidationSubject.from_schema(s, _trace(s))
    subject = replace(subject, elements_typed=False, element_type_tags=("",))
    report = ValidationEngine(schema_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "schema-elements-typed" in {f.check_id for f in report.blocking_failures}


def test_non_decidable_conformance_subject_fails_gate():
    s = _schema()
    subject = SchemaValidationSubject.from_schema(s, _trace(s))
    subject = replace(subject, conformance_decidable=False)
    report = ValidationEngine(schema_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "schema-conformance-decidable" in {f.check_id for f in report.blocking_failures}


def test_self_composing_schema_fails_acyclic_gate():
    s = _schema()
    subject = SchemaValidationSubject.from_schema(s, _trace(s))
    subject = replace(subject, member_schema_refs=(subject.target_id,))
    report = ValidationEngine(schema_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "schema-composition-acyclic" in {f.check_id for f in report.blocking_failures}


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    _s = _schema()
    assert_every_check_can_refuse(
        SchemaValidationSubject.from_schema(_s, _trace(_s)), schema_checks()
    )
