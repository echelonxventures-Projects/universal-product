"""EC3-B10-U02 — Attribute validation tests (EC-1 PASS + V1…V5 + UDL-08 + VC)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from data.attribute import make_attribute
from data.attribute_meta import ATTRIBUTE_META_CLASS, AttributeKind, AttributeState
from data.attribute_traceability import build_attribute_traceability
from data.attribute_validation import (
    AttributeValidationSubject,
    attribute_checks,
    validate_attribute,
)
from data.datum import make_datum
from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine


def _value_datum():
    return make_datum("ucos.core.string", "hello")


def _attr(**overrides):
    kwargs = dict(
        name="ucos.demo.attr",
        type_tag="ucos.core.string",
        value=_value_datum(),
        bearing_entity_ref="UCOS-ENTITY-REF:demo",
    )
    kwargs.update(overrides)
    return make_attribute(
        kwargs.pop("name"),
        kwargs.pop("type_tag"),
        kwargs.pop("value"),
        kwargs.pop("bearing_entity_ref"),
        **kwargs,
    )


def _trace(attr):
    return build_attribute_traceability(attr, unit="EC3-B10-U02", forward=(attr.attribute_id,))


def test_validation_passes_and_is_accepted():
    a = _attr()
    result = validate_attribute(a, _trace(a))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    a = _attr()
    result = validate_attribute(a, _trace(a))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(attribute_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_v1_v5_all_hold():
    a = _attr()
    result = validate_attribute(a, _trace(a))
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["meta-class-single"]  # V1 (DMC-03)
    assert passed["meta-relationships-closed"]  # V2
    assert passed["meta-constraints"]  # V3 (DAA-K1/K2)
    assert passed["founding-acyclic"]  # V4
    assert passed["lifecycle-valid"]  # V5


def test_attribute_typedness_udl08_checks_present_and_pass():
    a = _attr()
    result = validate_attribute(a, _trace(a))
    passed = {f.check_id: f.passed for f in result.report.findings}
    for cid in (
        "attr-typed",  # DAA-01 / UDL-08
        "attr-named",  # DAA-04 / UDL-08
        "attr-single-bearing",  # DMR-01 / DAA-02
        "attr-values-datum",  # DMR-02 / DAA-03
        "attr-nullability-declared",  # DAA-05
        "attr-classified",  # DXH-03
        "data-value-fidelity",  # UDL-06
        "foundation-reuse-integrity",  # UDL-02 / VC-5
        "storage-independence",  # UDL-11
        "non-constitutive",  # UDL-15
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_shared_check_ids_present_for_cce_gate_reuse():
    # These ids are consumed by the reused DMC-01 CCE ten-gate suite.
    a = _attr()
    result = validate_attribute(a, _trace(a))
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
    a = _attr()
    s1 = AttributeValidationSubject.from_attribute(a, _trace(a))
    s2 = AttributeValidationSubject.from_attribute(a, _trace(a))
    assert s1 == s2  # determinism at the subject boundary


def test_untraced_attribute_fails_traceability_gate():
    a = _attr()
    trace = _trace(a)
    subject = AttributeValidationSubject.from_attribute(a, trace)
    subject = replace(subject, provenance_chain=())  # orphaned lineage

    report = ValidationEngine(attribute_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


def test_secret_bearing_attribute_fails_non_constitutive_gate():
    a = _attr(name="api_key")
    result = validate_attribute(a, _trace(a))
    assert result.accepted is False
    assert "non-constitutive" in {f.check_id for f in result.report.blocking_failures}


def test_relational_attribute_validates_by_reference():
    a = _attr(kind=AttributeKind.RELATIONAL, references_entity="UCOS-ENTITY-REF:other")
    result = validate_attribute(a, _trace(a))
    assert result.accepted is True
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["attr-relational-by-reference"]  # DAA-07 / DAA-C4


def test_derived_attribute_with_provenance_validates():
    a = _attr(kind=AttributeKind.DERIVED, derived_from=("UCOS-ATTR-x-0",))
    result = validate_attribute(a, _trace(a))
    assert result.accepted is True
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["attr-derivation-provenance"]  # DAA-06 / DAA-C3


def test_active_attribute_still_validates():
    a = _attr(state=AttributeState.ACTIVE)
    assert validate_attribute(a, _trace(a)).accepted


# --- Refusal witnesses ------------------------------------------------------------
# Every check above was only ever observed PASSING. A check whose failure arm is never
# executed is an unproven refusal: it would satisfy the suite just as well by returning
# `self._passed()` unconditionally. Each row below forges the one condition the named
# check exists to catch, and asserts that check is among the blocking failures — `among`
# and not `equals`, because one malformed field legitimately offends several checks
# (an empty type_tag fails attr-typed AND the DAA-K1 half of meta-constraints).

REFUSALS = [
    ({"type_tag": "   "}, "attr-typed"),
    ({"name": " "}, "attr-named"),
    ({"target_id": "ATTR-1"}, "attr-identified"),
    ({"value_digest": "cafe"}, "data-value-fidelity"),  # wrong length
    ({"value_digest": "z" * 64}, "data-value-fidelity"),  # right length, not hex
    ({"value_datum_id": "UCOS-THING-1"}, "attr-values-datum"),
    ({"absorbs_value": True}, "attr-values-datum"),  # DMX-02: absorbed, not referenced
    ({"bearing_entity_ref": ""}, "attr-single-bearing"),
    ({"nullability_declared": False}, "attr-nullability-declared"),
    ({"kind": "ucos.attribute.kind.invented"}, "attr-classified"),
    ({"kind": AttributeKind.RELATIONAL.value}, "attr-relational-by-reference"),  # no target
    ({"references_entity": "UCOS-ENTITY-REF:x"}, "attr-relational-by-reference"),  # not relational
    ({"kind": AttributeKind.DERIVED.value}, "attr-derivation-provenance"),  # no provenance
    ({"derived_from": ("UCOS-ATTR-x-0",)}, "attr-derivation-provenance"),  # not derived
    ({"meta_class": "DMC-99"}, "meta-class-single"),
    ({"relationships": ("DMR-99-invented",)}, "meta-relationships-closed"),
    ({"name": "", "type_tag": ""}, "meta-constraints"),
    ({"founding_acyclic": False}, "founding-acyclic"),
    ({"lifecycle_state": "molten"}, "lifecycle-valid"),
    ({"redefines_el1": True}, "foundation-reuse-integrity"),
    ({"substrate_refs": ()}, "foundation-reuse-integrity"),
    ({"storage_selected": True}, "storage-independence"),
    ({"selects_technology": True}, "storage-independence"),
    ({"image_reference": "postgres:16"}, "storage-independence"),
    ({"confers_authority": True}, "non-constitutive"),
    ({"embeds_secret": True}, "non-constitutive"),
    ({"disclosure": {}}, "provisional-state-disclosure"),
    ({"provenance_chain": ()}, "traceability-rooted"),
    ({"provenance_chain": ("something-else", "10-DATA@1")}, "traceability-rooted"),  # unrooted
    ({"provenance_chain": (ATTRIBUTE_META_CLASS,)}, "traceability-rooted"),  # never reaches 10-DATA
]


@pytest.mark.parametrize(
    ("mutation", "check_id"), REFUSALS, ids=[f"{cid}-{i}" for i, (_, cid) in enumerate(REFUSALS)]
)
def test_each_check_refuses_the_condition_it_polices(mutation, check_id):
    a = _attr()
    subject = replace(AttributeValidationSubject.from_attribute(a, _trace(a)), **mutation)
    report = ValidationEngine(attribute_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert check_id in {f.check_id for f in report.blocking_failures}


def test_a_relational_attribute_with_a_target_and_a_derived_one_with_provenance_pass():
    """The satisfied arms of the two conditional checks, so the table above proves refusal
    and not merely that the branch is hostile to every input."""
    a = _attr()
    base = AttributeValidationSubject.from_attribute(a, _trace(a))
    relational = replace(
        base, kind=AttributeKind.RELATIONAL.value, references_entity="UCOS-ENTITY-REF:other"
    )
    derived = replace(base, kind=AttributeKind.DERIVED.value, derived_from=("UCOS-ATTR-x-0",))
    for subject in (relational, derived):
        assert ValidationEngine(attribute_checks()).validate(subject).verdict is Verdict.PASS


# --- Every check, not only the ones the table above remembered --------------------------
#
# The REFUSALS table proves the checks it names. It cannot prove the ones it forgot, and it
# cannot notice a check ADDED after it was written: a new arm inherits the table's silence and
# the suite stays green over a refusal nobody ever saw refuse. So the same argument is made a
# second way, deriving both sides — the checks from `attribute_checks()` and the corruptions
# from the subject's own declared fields — with the driver authored once in `engine/tests`
# (UCKP-ART-03) and shared with every other check suite in the repository.
#
# The table stays. It is the READABLE half: each row says which condition a named check exists
# to catch, which is a claim about intent that a derived sweep cannot make. This test is the
# COMPLETE half, and completeness is what the table cannot promise.


def test_every_attribute_check_refuses_something():
    a = _attr()
    subject = AttributeValidationSubject.from_attribute(a, _trace(a))
    assert_every_check_can_refuse(subject, attribute_checks())
