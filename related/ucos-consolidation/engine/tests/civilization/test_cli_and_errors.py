"""The ``ucos-mcos`` command surface, the error surface, and the shared seeding."""

from __future__ import annotations

import json

import pytest

from engine.civilization import __layer_version__
from engine.civilization.cli import main
from engine.civilization.errors import CivilizationError, DimensionUnknownError
from engine.civilization.metatypes import (
    CIVILIZATION_FACETS,
    DIMENSION_FACETS,
    dimension_facet_keys,
    facet_keys,
)
from engine.civilization.seeding import seed_facets
from engine.kernel.errors import KernelError
from engine.kernel.kernel import MetaKernel


def test_describe_emits_canonical_json(capsys):
    assert main(["describe"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["platform"] == "UCOS Meta-Civilization Operating System"
    assert payload["authority"] == "NONE"


def test_prove_exits_zero_when_compliant(capsys):
    assert main(["prove"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "CONSTITUTIONALLY-COMPLIANT"


def test_the_gate_alias_and_the_default_both_prove(capsys):
    assert main(["--gate"]) == 0
    first = json.loads(capsys.readouterr().out)
    assert main([]) == 0
    second = json.loads(capsys.readouterr().out)
    assert first["report_hash"] == second["report_hash"]


def test_prove_exits_non_zero_when_a_gate_fails(monkeypatch, capsys):
    monkeypatch.setattr(
        "engine.civilization.cli.constitutional_report",
        lambda: {"passed": False, "verdict": "NON-COMPLIANT"},
    )
    assert main(["prove"]) == 1
    assert "NON-COMPLIANT" in capsys.readouterr().out


def test_certify_emits_a_determination(capsys):
    assert main(["certify"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["determination"] == "CERTIFIED"
    assert payload["subject"] == "MetaCivilizationOperatingSystem"


def test_evidence_writes_the_full_set(tmp_path, capsys):
    target = tmp_path / "evidence"
    assert main(["evidence", str(target)]) == 0
    written = json.loads(capsys.readouterr().out)["written"]
    assert len(written) == 6
    for name in written:
        text = (target / name).read_text(encoding="utf-8")
        assert text.endswith("\n")
        json.loads(text)


def test_the_error_surface_is_catchable_as_a_kernel_error():
    assert issubclass(CivilizationError, KernelError)
    with pytest.raises(KernelError):
        raise DimensionUnknownError("x", dimension="d")


def test_errors_carry_structured_context():
    error = DimensionUnknownError("not registered", dimension="Axis")
    assert error.to_dict()["context"] == {"dimension": "Axis"}


def test_seeding_is_idempotent_and_order_independent():
    first = MetaKernel()
    seed_facets(first)
    count = len(first.metatypes())
    seed_facets(first)
    assert len(first.metatypes()) == count
    second = MetaKernel()
    seed_facets(second)
    assert first.certify()["snapshot_hash"] == second.certify()["snapshot_hash"]


def test_the_vocabulary_is_deterministically_ordered():
    assert facet_keys() == tuple(sorted(facet_keys()))
    assert dimension_facet_keys() == tuple(sorted(dimension_facet_keys()))
    assert len(facet_keys()) == len(CIVILIZATION_FACETS)
    assert len(dimension_facet_keys()) == len(DIMENSION_FACETS)


def test_the_layer_declares_a_version():
    assert __layer_version__ == "1.0.0"
