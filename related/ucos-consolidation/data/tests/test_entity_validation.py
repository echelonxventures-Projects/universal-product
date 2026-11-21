"""EC3-B10-U03 — Entity validation tests (EC-1 PASS + V1…V5 + UDL-07 + VC)."""

from __future__ import annotations

from dataclasses import replace

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.entity_meta import EntityState
from data.entity_traceability import build_entity_traceability
from data.entity_validation import (
    EntityValidationSubject,
    entity_checks,
    validate_entity,
)
from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine

ENTITY_NAME = "ucos.demo.entity"


def _borne_attr(name="ucos.demo.attr", bearing=None):
    return make_attribute(
        name,
        "ucos.core.string",
        make_datum("ucos.core.string", f"value-of-{name}"),
        bearing if bearing is not None else entity_ref_for(ENTITY_NAME),
    )


def _entity(**overrides):
    name = overrides.get("name", ENTITY_NAME)
    attributes = overrides.pop("attributes", (_borne_attr(bearing=entity_ref_for(name)),))
    kwargs = dict(name=ENTITY_NAME, type_tag="ucos.core.entity")
    kwargs.update(overrides)
    return make_entity(
        kwargs.pop("name"),
        kwargs.pop("type_tag"),
        attributes,
        **kwargs,
    )


def _trace(entity):
    return build_entity_traceability(entity, unit="EC3-B10-U03", forward=(entity.entity_id,))


def test_validation_passes_and_is_accepted():
    e = _entity()
    result = validate_entity(e, _trace(e))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    e = _entity()
    result = validate_entity(e, _trace(e))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(entity_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_v1_v5_all_hold():
    e = _entity()
    result = validate_entity(e, _trace(e))
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["meta-class-single"]  # V1 (DMC-02)
    assert passed["meta-relationships-closed"]  # V2
    assert passed["meta-constraints"]  # V3 (DEA-K1/K2)
    assert passed["founding-acyclic"]  # V4
    assert passed["lifecycle-valid"]  # V5


def test_entity_boundedness_udl07_checks_present_and_pass():
    e = _entity()
    result = validate_entity(e, _trace(e))
    passed = {f.check_id: f.passed for f in result.report.findings}
    for cid in (
        "entity-typed",  # DEA-01 / UDL-03
        "entity-named",  # DEA-02
        "entity-identified",  # UDL-04/05
        "entity-bears-attributes",  # DMR-01 / DEA-04
        "entity-boundedness",  # UDL-07 / DEA-03
        "entity-boundary-ownership",  # DEA-C2
        "entity-attributes-typed",  # DEA-04 / DEA-K2 / UDL-08
        "entity-classified",  # DXH-02
        "entity-schema-before-active",  # DEA-06 / DEA-K3
        "data-value-fidelity",  # UDL-06 (transitive)
        "foundation-reuse-integrity",  # UDL-02 / VC-5
        "storage-independence",  # UDL-11
        "non-constitutive",  # UDL-15
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_shared_check_ids_present_for_cce_gate_reuse():
    # These ids are consumed by the reused DMC-01 CCE ten-gate suite.
    e = _entity()
    result = validate_entity(e, _trace(e))
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
    e = _entity()
    s1 = EntityValidationSubject.from_entity(e, _trace(e))
    s2 = EntityValidationSubject.from_entity(e, _trace(e))
    assert s1 == s2  # determinism at the subject boundary


def test_untraced_entity_fails_traceability_gate():
    e = _entity()
    subject = EntityValidationSubject.from_entity(e, _trace(e))
    subject = replace(subject, provenance_chain=())  # orphaned lineage
    report = ValidationEngine(entity_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


def test_secret_bearing_entity_fails_non_constitutive_gate():
    e = _entity(name="api_key")
    result = validate_entity(e, _trace(e))
    assert result.accepted is False
    assert "non-constitutive" in {f.check_id for f in result.report.blocking_failures}


def test_active_entity_without_schema_fails_schema_before_active():
    # DEA-K3 — an entity cannot be validly ACTIVE without a described-by schema.
    e = _entity(state=EntityState.ACTIVE)
    result = validate_entity(e, _trace(e))
    assert result.accepted is False
    assert "entity-schema-before-active" in {f.check_id for f in result.report.blocking_failures}


def test_active_entity_with_schema_reference_validates():
    e = _entity(state=EntityState.ACTIVE, schema_ref="UCOS-SCHEMA-REF:ucos.demo.schema")
    result = validate_entity(e, _trace(e))
    assert result.accepted is True
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["entity-schema-before-active"]  # DEA-06 / DEA-K3


def test_boundary_ownership_gate_on_subject_mutation():
    e = _entity()
    subject = EntityValidationSubject.from_entity(e, _trace(e))
    subject = replace(subject, attribute_bearing_refs=("UCOS-ENTITY-REF:foreign",))
    report = ValidationEngine(entity_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "entity-boundary-ownership" in {f.check_id for f in report.blocking_failures}


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    e = _entity()
    subject = EntityValidationSubject.from_entity(e, _trace(e))
    assert_every_check_can_refuse(subject, entity_checks())
