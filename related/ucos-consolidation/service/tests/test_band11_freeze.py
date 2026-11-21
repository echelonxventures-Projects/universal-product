"""EC3-B11-U13 — Band-11 freeze construct tests (record invariants + roll-ups)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from service.band11_freeze import (
    Band11Freeze,
    FrozenUnitRef,
    make_band11_freeze,
)
from service.band11_freeze_meta import (
    BAND_COMPLETION_UNIT,
    EXPECTED_FROZEN_UNITS,
    FREEZE_EFFECTS,
    FREEZE_META_CLASSES,
    FREEZE_META_MODEL_UNIT,
    FreezeState,
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

_BAND_CERT = "UCOS-CERT-BAND-11-" + "a" * 16


def _unit_certs(certified: bool = True) -> tuple[tuple[str, str, bool], ...]:
    return tuple((u, f"UCOS-CERT-{u}-{'a' * 16}", certified) for u in EXPECTED_FROZEN_UNITS)


def _freeze(**overrides) -> Band11Freeze:
    base = make_band11_freeze(
        "ucos.service.band11.freeze",
        "ucos.core.band-freeze",
        _unit_certs(),
        band_completion_id="UCOS-BAND11-ucos.service.band11.completion-" + "b" * 16,
        band_completion_certification_id=_BAND_CERT,
        meta_model_id="UCOS-METAMODEL-ucos.service.metamodel.universal-" + "c" * 16,
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )
    return replace(base, **overrides) if overrides else base


# ---------------------------------------------------------------------------
# Factory + identity
# ---------------------------------------------------------------------------


def test_make_freeze_inventories_twelve_units():
    f = _freeze()
    assert len(f.units) == len(EXPECTED_FROZEN_UNITS)
    assert set(f.unit_ids()) == set(EXPECTED_FROZEN_UNITS)
    assert f.band_completion_unit == BAND_COMPLETION_UNIT
    assert f.meta_model_unit == FREEZE_META_MODEL_UNIT
    assert f.meta_model_certification_id == f"UCOS-CERT-{FREEZE_META_MODEL_UNIT}-{'a' * 16}"


def test_identity_and_baseline_digest_are_deterministic():
    a, b = _freeze(), _freeze()
    assert a.freeze_id == b.freeze_id
    assert a.baseline_digest == b.baseline_digest
    assert a.structure_digest == a.baseline_digest
    assert a.freeze_id.startswith("UCOS-FREEZE-BAND11-")
    assert len(a.baseline_digest) == 64
    assert a.meta_class == "BAND-11-FREEZE"


def test_units_sorted_by_unit_id():
    f = _freeze()
    assert list(f.unit_ids()) == sorted(f.unit_ids())


def test_frozen_unit_ref_to_dict():
    ref = FrozenUnitRef("EC3-B11-U01", "SMC-01", "Service", "SERVICE-001…005", "cid", True, True)
    d = ref.to_dict()
    assert set(d) == {
        "unit", "meta_class", "name", "concern_doc", "certification_id", "certified", "frozen",
    }
    assert d["frozen"] is True


def test_make_freeze_rejects_undeclared_unit():
    with pytest.raises(KeyError):
        make_band11_freeze(
            "n", "t", (("EC3-B11-U99", "cid", True),),
            band_completion_id="x", band_completion_certification_id=_BAND_CERT,
            meta_model_id="m", integration=dict(_FULL_INTEGRATION), version="1.0.0",
        )


def test_effects_default_to_full_set_and_can_be_overridden():
    assert set(_freeze().effects) == set(FREEZE_EFFECTS)
    partial = make_band11_freeze(
        "n", "t", _unit_certs(),
        band_completion_id="x", band_completion_certification_id=_BAND_CERT,
        meta_model_id="m", integration=dict(_FULL_INTEGRATION),
        effects=("FE-1", "FE-2"), version="1.0.0",
    )
    assert set(partial.effects) == {"FE-1", "FE-2"}
    assert partial.effects_declared() is False


def test_meta_model_cert_empty_when_u11_absent():
    # a freeze built without the U11 unit has no meta-model certification id
    certs = tuple((u, f"UCOS-CERT-{u}-{'a' * 16}", True) for u in EXPECTED_FROZEN_UNITS
                  if u != FREEZE_META_MODEL_UNIT)
    f = make_band11_freeze(
        "n", "t", certs,
        band_completion_id="x", band_completion_certification_id=_BAND_CERT,
        meta_model_id="m", integration=dict(_FULL_INTEGRATION), version="1.0.0",
    )
    assert f.meta_model_certification_id == ""


# ---------------------------------------------------------------------------
# Decidable roll-ups — pass + fail branches
# ---------------------------------------------------------------------------


def test_inventory_complete_true_and_false():
    assert _freeze().inventory_complete() is True
    short = _freeze(units=_freeze().units[:-1])
    assert short.inventory_complete() is False


def test_all_units_certified_true_false_and_empty():
    assert _freeze().all_units_certified() is True
    uncert = make_band11_freeze(
        "n", "t", _unit_certs(certified=False),
        band_completion_id="x", band_completion_certification_id=_BAND_CERT,
        meta_model_id="m", integration=dict(_FULL_INTEGRATION), version="1.0.0",
    )
    assert uncert.all_units_certified() is False
    assert _freeze(units=()).all_units_certified() is False


def test_all_units_frozen_true_false_and_empty():
    assert _freeze().all_units_frozen() is True
    thawed = _freeze().units[0]
    mixed = _freeze(units=(replace(thawed, frozen=False),) + _freeze().units[1:])
    assert mixed.all_units_frozen() is False
    assert _freeze(units=()).all_units_frozen() is False


def test_meta_class_coverage_complete_true_and_false():
    f = _freeze()
    assert set(f.meta_classes_covered()) == set(FREEZE_META_CLASSES)
    assert f.meta_class_coverage_complete() is True
    dropped = _freeze(units=tuple(u for u in f.units if u.meta_class != "SMC-01"))
    assert dropped.meta_class_coverage_complete() is False


def test_band_completion_referenced_true_and_fail_branches():
    assert _freeze().band_completion_referenced() is True
    assert _freeze(band_completion_unit="EC3-B11-U99").band_completion_referenced() is False
    assert _freeze(band_completion_id="   ").band_completion_referenced() is False
    assert _freeze(band_completion_certification_id="UCOS-CERT-SMC-01-x").band_completion_referenced() is False


def test_integration_closed_true_false_and_empty():
    assert _freeze().integration_closed() is True
    broken = dict(_FULL_INTEGRATION)
    broken["closure_SMI_01"] = False
    part = make_band11_freeze(
        "n", "t", _unit_certs(),
        band_completion_id="x", band_completion_certification_id=_BAND_CERT,
        meta_model_id="m", integration=broken, version="1.0.0",
    )
    assert part.integration_closed() is False
    assert _freeze(integration=()).integration_closed() is False


def test_dependency_acyclic_true_repeated_and_missing_capstones():
    assert _freeze().dependency_acyclic() is True
    units = _freeze().units
    repeated = _freeze(units=units + (units[0],))
    assert repeated.dependency_acyclic() is False
    no_metamodel = _freeze(units=tuple(u for u in units if u.unit != FREEZE_META_MODEL_UNIT))
    assert no_metamodel.dependency_acyclic() is False
    no_band = _freeze(units=tuple(u for u in units if u.unit != BAND_COMPLETION_UNIT))
    assert no_band.dependency_acyclic() is False


def test_reuses_by_reference_true_empty_and_blank_id():
    assert _freeze().reuses_by_reference() is True
    assert _freeze(units=()).reuses_by_reference() is False
    blank = _freeze().units[0]
    blanked = _freeze(units=(replace(blank, certification_id="   "),) + _freeze().units[1:])
    assert blanked.reuses_by_reference() is False


def test_effects_declared_true_and_false():
    assert _freeze().effects_declared() is True
    assert _freeze(effects=("FE-1",)).effects_declared() is False


def test_immutable_baseline_true():
    assert _freeze().is_immutable_baseline() is True


def test_technology_secret_authority_scans():
    f = _freeze()
    assert f.names_technology() is False
    assert f.selects_technology() is False
    assert f.embeds_secret() is False
    assert f.confers_authority() is False
    assert f.is_non_projection() is True
    assert f.is_non_constitutive() is True
    tech = _freeze(type_tag="grpc-backed-freeze")
    assert tech.names_technology() is True
    assert tech.is_non_constitutive() is False
    secret = _freeze(name="freeze-with-password")
    assert secret.embeds_secret() is True
    assert secret.is_non_constitutive() is False


def test_to_dict_shape():
    d = _freeze().to_dict()
    assert d["freeze_class"] == "BAND-11-FREEZE"
    assert d["unit_count"] == len(EXPECTED_FROZEN_UNITS)
    assert d["inventory_complete"] is True
    assert d["all_units_certified"] is True
    assert d["all_units_frozen"] is True
    assert d["band_completion_referenced"] is True
    assert d["integration_closed"] is True
    assert d["immutable_baseline"] is True
    assert d["effects_declared"] is True
    assert d["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005", "CCE"]
    assert set(d["integration"]) == set(_FULL_INTEGRATION)
    assert d["baseline_digest"] == d["structure_digest"]


def test_canonical_core_excludes_freeze_id():
    core = _freeze().canonical_core()
    assert "freeze_id" not in core
    assert core["freeze_class"] == "BAND-11-FREEZE"
    assert core["state"] == FreezeState.DEFINED.value
