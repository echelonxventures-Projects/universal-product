"""EC3-B10-U05 — Storage validation tests (EC-1 PASS + V1…V5 + UDL-11 + VC)."""

from __future__ import annotations

from dataclasses import replace

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.schema import entity_schema_for
from data.storage import make_storage, runtime_ref_for
from data.storage_meta import DurabilityLevel, StorageKind
from data.storage_traceability import build_storage_traceability
from data.storage_validation import (
    StorageValidationSubject,
    storage_checks,
    validate_storage,
)
from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine

ENTITY_NAME = "ucos.demo.entity"
STORAGE_NAME = "ucos.demo.storage"
RUNTIME_REF = runtime_ref_for("state.persist")


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _schema(entity):
    return entity_schema_for(entity, name="ucos.demo.schema", type_tag="ucos.core.schema")


def _storage(**overrides):
    entity = overrides.pop("entity", None) or _entity()
    schema = overrides.pop("schema", None) or _schema(entity)
    kwargs = dict(
        kind=overrides.pop("kind", StorageKind.LOCAL),
        durability=overrides.pop("durability", DurabilityLevel.DURABLE),
    )
    kwargs.update(overrides)
    loci = kwargs.pop("loci", ("locus.primary",))
    runtime = kwargs.pop("runtime_ref", RUNTIME_REF)
    name = kwargs.pop("name", STORAGE_NAME)
    return make_storage(
        name,
        kwargs.pop("type_tag", "ucos.core.storage"),
        loci,
        ((entity, schema),),
        runtime,
        **kwargs,
    )


def _trace(storage):
    return build_storage_traceability(storage, unit="EC3-B10-U05", forward=(storage.storage_id,))


def test_validation_passes_and_is_accepted():
    s = _storage()
    result = validate_storage(s, _trace(s))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    s = _storage()
    result = validate_storage(s, _trace(s))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(storage_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_v1_v5_all_hold():
    s = _storage()
    result = validate_storage(s, _trace(s))
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["meta-class-single"]  # V1 (DMC-06)
    assert passed["meta-relationships-closed"]  # V2
    assert passed["meta-constraints"]  # V3 (DTA-K1/K3)
    assert passed["founding-acyclic"]  # V4
    assert passed["lifecycle-valid"]  # V5


def test_storage_independence_udl11_checks_present_and_pass():
    s = _storage()
    result = validate_storage(s, _trace(s))
    passed = {f.check_id: f.passed for f in result.report.findings}
    for cid in (
        "storage-typed",  # DTA-01 / UDL-03
        "storage-named",  # DTA-03
        "storage-identified",  # UDL-04/05
        "storage-placement-explicit",  # DTA-03 / DTA-C1
        "storage-durability-declared",  # DTA-04 / DTA-C2
        "storage-persists-entities",  # DMR-05 / DTA-09
        "storage-schema-aligned",  # DTA-07 / DTA-K3
        "storage-persistence-by-reference",  # DMR-11 / DTA-02 / DTA-K2
        "storage-topology-consistent",  # DXH-06 / DTA-C3
        "storage-independence",  # UDL-11 / DTA-01 / DTA-K5
        "storage-versioned",  # DTA-08 / UDL-12
        "storage-classified",  # DXH-06
        "data-value-fidelity",  # UDL-06 (transitive)
        "foundation-reuse-integrity",  # UDL-02 / VC-5
        "non-constitutive",  # UDL-15 / DTA-09
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_shared_check_ids_present_for_cce_gate_reuse():
    # These ids are consumed by the reused DMC-01 CCE ten-gate suite.
    s = _storage()
    result = validate_storage(s, _trace(s))
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
    s = _storage()
    s1 = StorageValidationSubject.from_storage(s, _trace(s))
    s2 = StorageValidationSubject.from_storage(s, _trace(s))
    assert s1 == s2  # determinism at the subject boundary


def test_strict_acceptance_returns_decision_for_valid_topology():
    s = _storage()
    result = validate_storage(s, _trace(s), strict=True)
    assert result.accepted is True
    assert result.decision.accepted is True


def test_untraced_storage_fails_traceability_gate():
    s = _storage()
    subject = StorageValidationSubject.from_storage(s, _trace(s))
    subject = replace(subject, provenance_chain=())  # orphaned lineage
    report = ValidationEngine(storage_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


def test_secret_bearing_storage_fails_non_constitutive_gate():
    s = _storage(name="api_key")
    result = validate_storage(s, _trace(s))
    assert result.accepted is False
    assert "non-constitutive" in {f.check_id for f in result.report.blocking_failures}


def test_technology_naming_subject_fails_independence_gate():
    s = _storage()
    subject = StorageValidationSubject.from_storage(s, _trace(s))
    subject = replace(subject, names_technology=True)
    report = ValidationEngine(storage_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "storage-independence" in {f.check_id for f in report.blocking_failures}


def test_non_schema_aligned_subject_fails_gate():
    s = _storage()
    subject = StorageValidationSubject.from_storage(s, _trace(s))
    subject = replace(subject, schema_aligned=False, schema_refs=("not-a-schema",))
    report = ValidationEngine(storage_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "storage-schema-aligned" in {f.check_id for f in report.blocking_failures}


def test_self_referencing_founding_subject_fails_acyclic_gate():
    s = _storage()
    subject = StorageValidationSubject.from_storage(s, _trace(s))
    subject = replace(subject, founding_acyclic=False)
    report = ValidationEngine(storage_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "founding-acyclic" in {f.check_id for f in report.blocking_failures}


def test_placement_not_decidable_subject_fails_gate():
    s = _storage()
    subject = StorageValidationSubject.from_storage(s, _trace(s))
    subject = replace(subject, placement_explicit=False)
    report = ValidationEngine(storage_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "storage-placement-explicit" in {f.check_id for f in report.blocking_failures}


def test_non_runtime_binding_subject_fails_persistence_gate():
    s = _storage()
    subject = StorageValidationSubject.from_storage(s, _trace(s))
    subject = replace(subject, binds_runtime_by_reference=False)
    report = ValidationEngine(storage_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "storage-persistence-by-reference" in {f.check_id for f in report.blocking_failures}


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    _s = _storage()
    assert_every_check_can_refuse(
        StorageValidationSubject.from_storage(_s, _trace(_s)), storage_checks()
    )
