"""EC3-B13-U11 — Band-13 completion construct tests (record invariants + roll-ups)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from infrastructure.band13 import (
    Band13Completion,
    UnitCertificationRef,
    make_band13_completion,
)
from infrastructure.band13_meta import (
    BAND_META_CLASSES,
    EXPECTED_UNITS,
    META_MODEL_UNIT,
    BandState,
)

_FULL_INTEGRATION = {
    "all_concerns_certified": True,
    "leaf_closure_complete": True,
    "graph_downward_only": True,
    "graph_acyclic": True,
    "all_nodes_present": True,
    "ownership_disjoint": True,
    "all_edges_certified": True,
    "uimm_determination_complete": True,
}


def _unit_certs(certified: bool = True) -> tuple[tuple[str, str, bool], ...]:
    return tuple((u, f"{'a' * 64}"[:64], certified) for u in EXPECTED_UNITS)


def _completion(**overrides) -> Band13Completion:
    base = make_band13_completion(
        "ucos.infrastructure.band13.completion",
        "ucos.core.band-completion",
        _unit_certs(),
        meta_model_id="b" * 64,
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )
    return replace(base, **overrides) if overrides else base


# ---------------------------------------------------------------------------
# Factory + identity
# ---------------------------------------------------------------------------


def test_make_band13_completion_inventories_ten_units():
    c = _completion()
    assert len(c.units) == len(EXPECTED_UNITS)
    assert set(c.unit_ids()) == set(EXPECTED_UNITS)
    assert c.meta_model_unit == META_MODEL_UNIT
    assert c.meta_model_certification_id == "a" * 64


def test_identity_and_digest_are_deterministic():
    a, b = _completion(), _completion()
    assert a.band_id == b.band_id
    assert a.structure_digest == b.structure_digest
    assert a.band_id.startswith("UCOS-BAND13-")
    assert len(a.structure_digest) == 64
    assert a.meta_class == "BAND-13"


def test_units_sorted_by_unit_id():
    c = _completion()
    assert list(c.unit_ids()) == sorted(c.unit_ids())


def test_unit_certification_ref_to_dict():
    ref = UnitCertificationRef(
        "EC3-B13-U01", ("InfrastructureCapability",), "Cap", "INFRASTRUCTURE-006", "cid", True
    )
    d = ref.to_dict()
    assert set(d) == {
        "unit",
        "meta_classes",
        "name",
        "concern_doc",
        "certification_id",
        "certified",
    }
    assert d["meta_classes"] == ["InfrastructureCapability"]


def test_make_band13_completion_rejects_undeclared_unit():
    with pytest.raises(KeyError):
        make_band13_completion(
            "n",
            "t",
            (("EC3-B13-U99", "cid", True),),
            meta_model_id="m",
            integration=dict(_FULL_INTEGRATION),
            version="1.0.0",
        )


# ---------------------------------------------------------------------------
# Decidable roll-ups — pass + fail branches
# ---------------------------------------------------------------------------


def test_inventory_complete_true_and_false():
    assert _completion().inventory_complete() is True
    short = _completion(units=_completion().units[:-1])
    assert short.inventory_complete() is False


def test_all_units_certified_true_false_and_empty():
    assert _completion().all_units_certified() is True
    uncert = make_band13_completion(
        "n",
        "t",
        _unit_certs(certified=False),
        meta_model_id="m",
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )
    assert uncert.all_units_certified() is False
    empty = _completion(units=())
    assert empty.all_units_certified() is False


def test_meta_class_coverage_complete_true_and_false():
    c = _completion()
    assert set(c.meta_classes_covered()) == set(BAND_META_CLASSES)
    assert c.meta_class_coverage_complete() is True
    # drop the capability unit → coverage no longer exactly the 17 leaves
    dropped = _completion(units=tuple(u for u in c.units if u.unit != "EC3-B13-U01"))
    assert dropped.meta_class_coverage_complete() is False


def test_meta_class_ownership_disjoint_true_and_false():
    c = _completion()
    assert c.meta_class_ownership_disjoint() is True
    # duplicate a meta-class across two units
    dup_unit = replace(c.units[1], meta_classes=("InfrastructureCapability",))
    overlapped = _completion(units=(c.units[0], dup_unit) + c.units[2:])
    assert overlapped.meta_class_ownership_disjoint() is False


def test_integration_closed_true_and_false_and_empty():
    assert _completion().integration_closed() is True
    broken = dict(_FULL_INTEGRATION)
    broken["graph_acyclic"] = False
    part = make_band13_completion(
        "n",
        "t",
        _unit_certs(),
        meta_model_id="m",
        integration=broken,
        version="1.0.0",
    )
    assert part.integration_closed() is False
    empty = _completion(integration=())
    assert empty.integration_closed() is False


def test_dependency_acyclic_true_repeated_and_missing_capstone():
    assert _completion().dependency_acyclic() is True
    dup = _completion().units
    repeated = _completion(units=dup + (dup[0],))
    assert repeated.dependency_acyclic() is False
    no_capstone = _completion(units=tuple(u for u in dup if u.unit != META_MODEL_UNIT))
    assert no_capstone.dependency_acyclic() is False


def test_reuses_by_reference_true_empty_and_blank_id():
    assert _completion().reuses_by_reference() is True
    empty = _completion(units=())
    assert empty.reuses_by_reference() is False
    units = _completion().units
    blanked = _completion(units=(replace(units[0], certification_id="   "),) + units[1:])
    assert blanked.reuses_by_reference() is False


def test_technology_secret_authority_scans():
    c = _completion()
    assert c.names_technology() is False
    assert c.selects_technology() is False
    assert c.embeds_secret() is False
    assert c.confers_authority() is False
    assert c.is_non_projection() is True
    assert c.is_non_constitutive() is True
    tech = _completion(type_tag="kubernetes-backed-completion")
    assert tech.names_technology() is True
    assert tech.is_non_constitutive() is False
    secret = _completion(name="completion-with-password")
    assert secret.embeds_secret() is True
    assert secret.is_non_constitutive() is False


def test_to_dict_shape():
    d = _completion().to_dict()
    assert d["band_class"] == "BAND-13"
    assert d["unit_count"] == len(EXPECTED_UNITS)
    assert d["inventory_complete"] is True
    assert d["all_units_certified"] is True
    assert d["integration_closed"] is True
    assert d["meta_class_ownership_disjoint"] is True
    assert d["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005", "CCE"]
    assert set(d["integration"]) == set(_FULL_INTEGRATION)


def test_canonical_core_excludes_band_id():
    core = _completion().canonical_core()
    assert "band_id" not in core
    assert core["band_class"] == "BAND-13"
    assert core["state"] == BandState.DEFINED.value
