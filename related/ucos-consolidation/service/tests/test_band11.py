"""EC3-B11-U12 — Band-11 completion construct tests (record invariants + roll-ups)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from service.band11 import (
    Band11Completion,
    UnitCertificationRef,
    make_band11_completion,
)
from service.band11_meta import (
    BAND_META_CLASSES,
    EXPECTED_UNITS,
    META_MODEL_UNIT,
    BandState,
)

_FULL_INTEGRATION = {
    "all_members_certified": True,
    "closure_SMI_01": True,
    "relationship_closure_SMI_02": True,
    "totality_SMI_03": True,
    "founding_acyclic_SMI_04": True,
    "reuse_by_reference_SMI_05": True,
    "non_constitutive_SMI_06": True,
    "non_projection_SMI_07": True,
    "map_resolves": True,
}


def _unit_certs(certified: bool = True) -> tuple[tuple[str, str, bool], ...]:
    return tuple((u, f"UCOS-CERT-{u}-{'a' * 16}", certified) for u in EXPECTED_UNITS)


def _completion(**overrides) -> Band11Completion:
    base = make_band11_completion(
        "ucos.service.band11.completion",
        "ucos.core.band-completion",
        _unit_certs(),
        meta_model_id="UCOS-METAMODEL-ucos.service.metamodel.universal-" + "b" * 16,
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )
    return replace(base, **overrides) if overrides else base


# ---------------------------------------------------------------------------
# Factory + identity
# ---------------------------------------------------------------------------


def test_make_band11_completion_inventories_eleven_units():
    c = _completion()
    assert len(c.units) == len(EXPECTED_UNITS)
    assert set(c.unit_ids()) == set(EXPECTED_UNITS)
    assert c.meta_model_unit == META_MODEL_UNIT
    assert c.meta_model_certification_id == f"UCOS-CERT-{META_MODEL_UNIT}-{'a' * 16}"


def test_identity_and_digest_are_deterministic():
    a, b = _completion(), _completion()
    assert a.band_id == b.band_id
    assert a.structure_digest == b.structure_digest
    assert a.band_id.startswith("UCOS-BAND11-")
    assert len(a.structure_digest) == 64
    assert a.meta_class == "BAND-11"


def test_units_sorted_by_unit_id():
    c = _completion()
    assert list(c.unit_ids()) == sorted(c.unit_ids())


def test_unit_certification_ref_to_dict():
    ref = UnitCertificationRef("EC3-B11-U01", "SMC-01", "Service", "SERVICE-001…005", "cid", True)
    d = ref.to_dict()
    assert set(d) == {"unit", "meta_class", "name", "concern_doc", "certification_id", "certified"}


def test_make_band11_completion_rejects_undeclared_unit():
    with pytest.raises(KeyError):
        make_band11_completion(
            "n", "t", (("EC3-B11-U99", "cid", True),), meta_model_id="m",
            integration=dict(_FULL_INTEGRATION), version="1.0.0",
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
    uncert = make_band11_completion(
        "n", "t", _unit_certs(certified=False), meta_model_id="m",
        integration=dict(_FULL_INTEGRATION), version="1.0.0",
    )
    assert uncert.all_units_certified() is False
    empty = _completion(units=())
    assert empty.all_units_certified() is False


def test_meta_class_coverage_complete_true_and_false():
    c = _completion()
    assert set(c.meta_classes_covered()) == set(BAND_META_CLASSES)
    assert c.meta_class_coverage_complete() is True
    # drop the Service unit → coverage no longer exactly SMC-01…10
    dropped = _completion(units=tuple(u for u in c.units if u.meta_class != "SMC-01"))
    assert dropped.meta_class_coverage_complete() is False


def test_integration_closed_true_and_false_and_empty():
    assert _completion().integration_closed() is True
    broken = dict(_FULL_INTEGRATION)
    broken["closure_SMI_01"] = False
    part = make_band11_completion(
        "n", "t", _unit_certs(), meta_model_id="m", integration=broken, version="1.0.0",
    )
    assert part.integration_closed() is False
    empty = _completion(integration=())
    assert empty.integration_closed() is False


def test_dependency_acyclic_true_repeated_and_missing_metamodel():
    assert _completion().dependency_acyclic() is True
    dup = _completion().units
    repeated = _completion(units=dup + (dup[0],))
    assert repeated.dependency_acyclic() is False
    # a completion whose units omit the meta-model capstone is not downward-closed
    no_capstone = _completion(units=tuple(u for u in dup if u.unit != META_MODEL_UNIT))
    assert no_capstone.dependency_acyclic() is False


def test_reuses_by_reference_true_empty_and_blank_id():
    assert _completion().reuses_by_reference() is True
    empty = _completion(units=())
    assert empty.reuses_by_reference() is False
    blank = _completion().units[0]
    blanked = _completion(units=(replace(blank, certification_id="   "),) + _completion().units[1:])
    assert blanked.reuses_by_reference() is False


def test_technology_secret_authority_scans():
    c = _completion()
    assert c.names_technology() is False
    assert c.selects_technology() is False
    assert c.embeds_secret() is False
    assert c.confers_authority() is False
    assert c.is_non_projection() is True
    assert c.is_non_constitutive() is True
    # a record naming a technology in its type_tag is constitutive/tech-bound
    tech = _completion(type_tag="grpc-backed-completion")
    assert tech.names_technology() is True
    assert tech.is_non_constitutive() is False
    secret = _completion(name="completion-with-password")
    assert secret.embeds_secret() is True
    assert secret.is_non_constitutive() is False


def test_to_dict_shape():
    d = _completion().to_dict()
    assert d["band_class"] == "BAND-11"
    assert d["unit_count"] == len(EXPECTED_UNITS)
    assert d["inventory_complete"] is True
    assert d["all_units_certified"] is True
    assert d["integration_closed"] is True
    assert d["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005", "CCE"]
    assert set(d["integration"]) == set(_FULL_INTEGRATION)


def test_canonical_core_excludes_band_id():
    core = _completion().canonical_core()
    assert "band_id" not in core
    assert core["band_class"] == "BAND-11"
    assert core["state"] == BandState.DEFINED.value
