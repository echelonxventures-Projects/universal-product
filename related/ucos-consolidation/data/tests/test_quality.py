"""EC3-B10-U08 — Quality construct tests (DMC-09 + DQA-01…10 + UDL-14/03/04)."""

from __future__ import annotations

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.quality import (
    MeasuredConstructRef,
    MeasurementEntry,
    QualityError,
    QualityObject,
    make_measurements,
    make_quality,
    policy_ref_for,
)
from data.quality_meta import (
    QUALITY_META_CLASS,
    QUALITY_RELATIONSHIPS,
    QualityKind,
    QualityState,
    QualityVerdict,
)

ENTITY_NAME = "ucos.demo.entity"
QUALITY_NAME = "ucos.demo.quality"
POLICY_REF = policy_ref_for("quality.udl")
SCHEMA_REF = "UCOS-SCHEMA-REF:ucos.demo.schema"


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _measurements(dim="completeness"):
    return make_measurements(((dim, True, 100),))


def _quality(**overrides):
    entity = overrides.pop("entity", None) or _entity()
    kind = overrides.pop("kind", QualityKind.COMPLETENESS_MEASURE)
    kwargs = dict(kind=kind, measurements=overrides.pop("measurements", _measurements()))
    # schema-relative kinds require a schema reference unless the test overrides it
    if kind in (QualityKind.COMPLETENESS_MEASURE, QualityKind.CONSISTENCY_MEASURE):
        kwargs["schema_ref"] = overrides.pop("schema_ref", SCHEMA_REF)
    kwargs.update(overrides)
    policy_ref = kwargs.pop("policy_ref", POLICY_REF)
    name = kwargs.pop("name", QUALITY_NAME)
    type_tag = kwargs.pop("type_tag", "ucos.core.quality")
    return make_quality(name, type_tag, entity, policy_ref, **kwargs)


def test_quality_is_typed_named_identified_and_classified():
    q = _quality()
    assert q.meta_class == QUALITY_META_CLASS  # V1 (DMC-09)
    assert q.name == QUALITY_NAME  # named
    assert q.type_tag == "ucos.core.quality"  # UDL-03 typed
    assert q.quality_id.startswith("UCOS-QUALITY-")  # UDL-04 identified (ENG-001)
    assert q.kind is QualityKind.COMPLETENESS_MEASURE  # DXH-09 classified
    assert q.is_classified() is True


def test_quality_measures_entity_by_reference_not_owning():
    entity = _entity()
    q = _quality(entity=entity)
    assert q.measured_construct_id() == entity.entity_id  # DMR-08 measures
    assert q.measures_construct(entity.entity_id) is True
    assert q.absorbs_measured() is False  # DQA-C3 / DMX-02 — referenced, not owned
    ref_dict = q.measured_ref.to_dict()
    assert ref_dict["owned"] is False
    assert ref_dict["binding"] == "DMR-08:measures"


def test_measured_construct_ref_requires_certified_entity():
    with pytest.raises(QualityError):  # DMR-08
        MeasuredConstructRef.from_entity(object())


def test_quality_is_evaluative_and_non_remediating():
    q = _quality()
    assert q.is_evaluative() is True  # DQA-01 / DQA-K2
    assert q.remediates() is False  # DQA-03 / DQA-K2 — enacts nothing
    assert q.enforces() is False  # DQA-03 / UDL-14
    assert q.grants_access() is False  # DQA-09 / DQA-K5
    assert q.confers_authority() is False  # DQA-09 / DQA-K5
    assert q.is_recorded() is True  # DQA-04 / DQA-K4


def test_quality_is_dimensioned_single_facet():
    q = _quality()
    assert q.is_dimensioned() is True  # DQA-02
    assert q.measured_dimension() == "completeness"  # DXC-02 single facet
    assert q.measured_dimensions() == ("completeness",)


def test_quality_binds_policy_by_reference():
    q = _quality()
    assert q.binds_policy_by_reference() is True  # DMR-11 / DQA-06 / DQA-K3
    assert q.policy_ref.startswith("UCOS-POLICY-REF:")


def test_quality_records_measurement_verdicts():
    q = _quality()
    assert q.records_measurement() is True  # DQA-C1
    assert q.measured_dimensions() == ("completeness",)
    assert q.passes() is True
    assert q.gap_report() == ()  # no deficiency recorded


def test_quality_gap_report_records_deficiencies_without_remediating():
    q = _quality(measurements=make_measurements((("completeness", False, 40),)))
    assert q.gap_report() == ("completeness",)  # DQA-C4 — routed to a Gap Report, not fixed
    assert q.passes() is False
    assert q.remediates() is False  # still remediates nothing


def test_completeness_measure_is_schema_relative():
    q = _quality(kind=QualityKind.COMPLETENESS_MEASURE)
    assert q.is_schema_relative() is True  # DQA-05 / DQA-C2
    assert q.schema_ref.startswith("UCOS-SCHEMA-REF:")


def test_consistency_measure_requires_schema_reference():
    with pytest.raises(QualityError):  # DQA-05 / DQA-C2
        _quality(
            kind=QualityKind.CONSISTENCY_MEASURE,
            measurements=_measurements("consistency"),
            schema_ref="",
        )


def test_accuracy_measure_needs_no_schema_reference():
    q = _quality(kind=QualityKind.ACCURACY_MEASURE, measurements=_measurements("accuracy"))
    assert q.is_schema_relative() is True  # trivially — not a schema-relative kind
    assert q.schema_ref == ""


def test_integrity_measure_needs_no_schema_reference():
    q = _quality(kind=QualityKind.INTEGRITY_MEASURE, measurements=_measurements("integrity"))
    assert q.measured_dimension() == "integrity"
    assert q.schema_ref == ""


def test_non_schema_relative_measure_rejects_malformed_present_schema_ref():
    # DQA-05 — for a non-schema-relative kind, a present schema_ref must still be a
    # declared-schema reference; a malformed non-empty value is rejected fail-closed.
    with pytest.raises(QualityError):
        _quality(
            kind=QualityKind.ACCURACY_MEASURE,
            measurements=_measurements("accuracy"),
            schema_ref="not-a-schema-ref",
        )


def test_non_schema_relative_measure_accepts_valid_present_schema_ref():
    # DQA-05 — a well-formed declared-schema reference is accepted (and remains trivially
    # schema-relative) for a non-schema-relative kind without being required.
    q = _quality(
        kind=QualityKind.ACCURACY_MEASURE,
        measurements=_measurements("accuracy"),
        schema_ref=SCHEMA_REF,
    )
    assert q.schema_ref == SCHEMA_REF
    assert q.is_schema_relative() is True


def test_quality_identity_is_deterministic_and_structure_derived():
    a = _quality()
    b = _quality()
    c = _quality(name="different.quality")
    assert a.quality_id == b.quality_id  # same structure → same ENG-001 identity
    assert a.quality_id != c.quality_id  # different name → different identity


def test_quality_is_immutable_objecthood():
    q = _quality()
    with pytest.raises((AttributeError, TypeError)):
        q.name = "other"  # frozen object (ENG-002 objecthood)


def test_unnamed_quality_is_rejected_fail_closed():
    with pytest.raises(QualityError):
        _quality(name="")


def test_untyped_quality_is_rejected_fail_closed():
    with pytest.raises(QualityError):
        _quality(type_tag="")  # DQA-K1 / UDL-03


def test_quality_without_measurements_is_rejected_fail_closed():
    with pytest.raises(QualityError):  # DQA-C1 — ≥1 measurement required
        _quality(measurements=())


def test_measurement_dimension_must_match_kind_facet():
    with pytest.raises(QualityError):  # DXC-02 / DQA-02 — single facet
        _quality(
            kind=QualityKind.COMPLETENESS_MEASURE,
            measurements=make_measurements((("accuracy", True, 100),)),
        )


def test_measurement_entry_requires_valid_dimension_verdict_and_score():
    with pytest.raises(QualityError):  # DQA-02 — unknown dimension
        MeasurementEntry(dimension="freshness", satisfied=True)
    with pytest.raises(QualityError):  # DQA-C1 — decidable verdict
        MeasurementEntry(dimension="accuracy", satisfied="yes")
    with pytest.raises(QualityError):  # DQA-C3 — integer metric
        MeasurementEntry(dimension="accuracy", satisfied=True, score="high")
    with pytest.raises(QualityError):  # DQA-C3 — bounded [0,100]
        MeasurementEntry(dimension="accuracy", satisfied=True, score=101)
    with pytest.raises(QualityError):  # DQA-C3 — bool is not a metric
        MeasurementEntry(dimension="accuracy", satisfied=True, score=True)


def test_quality_naming_a_profiling_technology_is_rejected_fail_closed():
    # UDL-14 / DQA-07 / DQA-K5 — evaluative record only; names no profiling/DQ/benchmark tech.
    with pytest.raises(QualityError):
        _quality(name="great expectations")
    with pytest.raises(QualityError):
        _quality(type_tag="deequ.profiler")
    with pytest.raises(QualityError):
        _quality(schema_ref="UCOS-SCHEMA-REF:quality benchmark")


def test_relationships_are_within_dmr_closure():
    q = _quality()
    assert set(q.meta_relationships()) <= set(QUALITY_RELATIONSHIPS)  # V2
    assert q.meta_relationships() == ("DMR-08", "DMR-10", "DMR-11")


def test_verdict_is_a_decidable_quality_judgment():
    q = _quality(verdict=QualityVerdict.FAIL)
    assert q.verdict is QualityVerdict.FAIL  # DQA-C1 / DOV-08
    payload = q.to_dict()
    assert payload["verdict"] == "fail"


def test_supersession_lineage_is_recorded():
    q = _quality(version="2.0.0", supersedes="UCOS-QUALITY-old-0000000000000000")
    assert q.version == "2.0.0"  # DQA-08
    assert q.supersedes == "UCOS-QUALITY-old-0000000000000000"  # DQA-C5 append-only
    with pytest.raises(QualityError):
        _quality(version="")


def test_founding_graph_is_acyclic():
    q = _quality()
    assert q.is_founding_acyclic() is True  # V4 / DMK-03


def test_invalid_policy_ref_is_rejected():
    with pytest.raises(QualityError):  # DMR-11 / DQA-K3 — must bind a RUNTIME policy reference
        _quality(policy_ref="not-a-policy-ref")


def test_subject_without_certified_construct_id_is_rejected():
    bad_ref = MeasuredConstructRef(
        construct_id="NOT-A-CONSTRUCT",
        structure_digest="a" * 64,
        name="x",
        type_tag="t",
        meta_class="DMC-02",
    )
    with pytest.raises(QualityError):  # DMR-08
        make_quality(
            "q",
            "ucos.core.quality",
            bad_ref,
            POLICY_REF,
            measurements=_measurements(),
            schema_ref=SCHEMA_REF,
        )


def test_subject_without_structural_digest_is_rejected():
    bad_ref = MeasuredConstructRef(
        construct_id="UCOS-ENTITY-x-0000000000000000",
        structure_digest="short",  # not a 64-hex digest
        name="x",
        type_tag="t",
        meta_class="DMC-02",
    )
    with pytest.raises(QualityError):  # UDL-06
        make_quality(
            "q",
            "ucos.core.quality",
            bad_ref,
            POLICY_REF,
            measurements=_measurements(),
            schema_ref=SCHEMA_REF,
        )


def test_non_measured_ref_is_rejected():
    with pytest.raises(QualityError):  # DMR-08
        QualityObject(
            name="q",
            type_tag="ucos.core.quality",
            kind=QualityKind.COMPLETENESS_MEASURE,
            measured_ref="not-a-ref",
            policy_ref=POLICY_REF,
            measurements=_measurements(),
            schema_ref=SCHEMA_REF,
        )


def test_non_quality_kind_is_rejected():
    with pytest.raises(QualityError):  # DXH-09 / DMR-09
        _quality(kind="Completeness-Measure")  # str, not QualityKind


def test_non_measurement_tuple_is_rejected():
    # Constructed directly (bypassing make_quality's tuple() coercion) to exercise the guard.
    ref = MeasuredConstructRef.from_entity(_entity())
    with pytest.raises(QualityError):  # DQA-C1
        QualityObject(
            name="q",
            type_tag="ucos.core.quality",
            kind=QualityKind.COMPLETENESS_MEASURE,
            measured_ref=ref,
            policy_ref=POLICY_REF,
            measurements=[MeasurementEntry("completeness", True)],  # list, not tuple
            schema_ref=SCHEMA_REF,
        )


def test_non_measurement_entry_member_is_rejected():
    with pytest.raises(QualityError):  # DQA-C1
        _quality(measurements=("not-an-entry",))


def test_non_verdict_is_rejected():
    with pytest.raises(QualityError):  # DQA-C1
        _quality(verdict="pass")  # str, not QualityVerdict


def test_non_string_schema_ref_is_rejected():
    with pytest.raises(QualityError):  # DQA-05
        _quality(schema_ref=123)


def test_non_state_state_is_rejected():
    with pytest.raises(QualityError):  # UDL-12
        _quality(state="DEFINED")  # str, not QualityState


def test_non_string_supersedes_is_rejected():
    with pytest.raises(QualityError):  # DQA-C5
        _quality(supersedes=123)


def test_non_constitutive_and_no_secret():
    q = _quality()
    assert q.confers_authority() is False  # UDL-15 / DQA-09 / C7
    assert q.redefines_el1() is False  # UDL-02 / DMI-05
    assert q.selects_technology() is False  # UDL-14 / DQA-K5 (evaluative record)
    assert q.embeds_secret() is False


def test_secret_bearing_quality_is_detected():
    leaky = _quality(name="password")
    assert leaky.embeds_secret() is True  # UDL-15 / RR-07


def test_quality_to_dict_records_substrate_reuse():
    q = _quality()
    payload = q.to_dict()
    assert payload["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005"]
    assert payload["meta_class"] == "DMC-09"
    assert payload["absorbs_measured"] is False
    assert payload["evaluative"] is True
    assert payload["remediates"] is False
    assert payload["enforces"] is False
    assert payload["grants_access"] is False
    assert payload["recorded"] is True
    assert payload["names_technology"] is False
    assert payload["binds_policy_by_reference"] is True
    assert payload["schema_relative"] is True


def test_quality_type_is_the_realized_construct():
    assert isinstance(_quality(), QualityObject)


def test_progression_is_forward_only():
    q = _quality(state=QualityState.DEFINED)
    active = q.transition(QualityState.ACTIVE)
    assert active.state is QualityState.ACTIVE  # UDL-12 forward-only
    with pytest.raises(QualityError):
        active.transition(QualityState.DEFINED)  # backward rejected


def test_transition_to_non_state_is_rejected():
    q = _quality()
    with pytest.raises(QualityError):  # UDL-12
        q.transition("ACTIVE")  # str, not QualityState


def test_make_measurements_builds_entries():
    entries = make_measurements((("accuracy", True, 90), ("accuracy", False, 10)))
    assert len(entries) == 2
    assert all(isinstance(e, MeasurementEntry) for e in entries)
    assert entries[1].dimension == "accuracy"
    assert entries[1].satisfied is False
    assert entries[1].score == 10


def test_policy_ref_for_builds_prefixed_reference():
    ref = policy_ref_for("quality.udl")
    assert ref == "UCOS-POLICY-REF:quality.udl"


def test_quality_selects_no_technology():
    q = _quality()
    assert q.names_technology() is False  # UDL-14 / DQA-07 / DQA-K5
    assert q.selects_technology() is False
