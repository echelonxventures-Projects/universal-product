"""TASK-000033/000034 — Determinism integration & CI-gate behaviour tests.

Proves the EPIC-004 success criterion end to end against the real, certified
``00-BOOK`` registry: the same blueprint, same compiler, and same environment
definition produce the same output every time. Also exercises the CI-gate
contract implemented by ``engine.determinism.reproduce.main`` — pass on identity,
fail on divergence, with preserved evidence.
"""

from __future__ import annotations

import json

import pytest

from engine.determinism import reproduce
from engine.determinism.hermetic import hermetic_env
from engine.determinism.reproduce import double_build, main
from engine.registry.adapter import RegistryAdapter
from engine.registry.source import default_data_dir


@pytest.fixture
def real_registry() -> RegistryAdapter:
    if not default_data_dir().is_dir():
        pytest.skip("00-BOOK/DATA registry substrate not present")
    return RegistryAdapter.open()


# -- SUCCESS CRITERION --------------------------------------------------------


def test_bp_data_0001_is_byte_identical_across_independent_executions(real_registry):
    """double_build("BP-DATA-0001") == byte_identical with zero differences."""
    result = double_build("BP-DATA-0001", registry=real_registry)

    assert result.byte_identical is True
    assert result.divergences == ()
    assert result.artifact_id_a == result.artifact_id_b
    # zero differences across every required category
    assert result.category_identical == {
        "generated_source": True,
        "manifests": True,
        "sbom": True,
        "signatures": True,
        "publication_payloads": True,
    }


def test_environment_definition_is_stable(real_registry):
    # same environment definition across independent constructions
    assert hermetic_env().fingerprint() == hermetic_env().fingerprint()
    a = double_build("BP-DATA-0001", registry=real_registry)
    b = double_build("BP-DATA-0001", registry=real_registry)
    assert a.environment_fingerprint == b.environment_fingerprint
    assert a.artifact_id_a == b.artifact_id_a  # reproducible across separate runs


# -- CI GATE BEHAVIOUR --------------------------------------------------------


def test_ci_gate_passes_and_publishes_evidence(tmp_path):
    exit_code = main(["BP-DATA-0001", "--evidence-dir", str(tmp_path / "ev")])
    assert exit_code == 0
    evidence = tmp_path / "ev" / "determinism-evidence.json"
    report = tmp_path / "ev" / "BP-DATA-0001-reproducibility_report.json"
    assert evidence.is_file()
    assert report.is_file()
    payload = json.loads(evidence.read_text())
    assert payload["byte_identical"] is True
    assert payload["results"][0]["blueprint_id"] == "BP-DATA-0001"


def test_ci_gate_fails_on_divergence(tmp_path, monkeypatch):
    # Simulate a non-deterministic result; the gate must exit non-zero (fail).
    from engine.determinism.reproduce import FileDiff, ReproducibilityResult

    diverging = ReproducibilityResult(
        blueprint_id="BP-DATA-0001",
        byte_identical=False,
        environment_fingerprint="deadbeef",
        artifact_id_a="UCOS-CMP-BP-DATA-0001-a",
        artifact_id_b="UCOS-CMP-BP-DATA-0001-b",
        category_identical={
            "generated_source": False,
            "manifests": True,
            "sbom": True,
            "signatures": True,
            "publication_payloads": True,
        },
        diffs=(
            FileDiff(
                path="artifacts/schema/customer.sql",
                category="generated_source",
                status="differs",
                sha256_a="aa",
                sha256_b="bb",
            ),
        ),
    )
    monkeypatch.setattr(reproduce, "double_build", lambda *a, **k: diverging)
    exit_code = main(["BP-DATA-0001", "--evidence-dir", str(tmp_path / "ev")])
    assert exit_code == 1
    # divergence evidence is preserved (reproducibility_report.json)
    report = json.loads((tmp_path / "ev" / "BP-DATA-0001-reproducibility_report.json").read_text())
    assert report["byte_identical"] is False
    assert report["divergence_count"] == 1


def test_ci_gate_uses_key_ref_when_env_present(tmp_path, monkeypatch):
    monkeypatch.setenv("UCOS_DETERMINISM_KEY", "ci-signing-key")
    exit_code = main(["BP-DATA-0001", "--evidence-dir", str(tmp_path / "ev")])
    assert exit_code == 0


def test_ci_gate_defaults_to_bp_data_0001(tmp_path, monkeypatch):
    captured: list[str] = []

    def _fake(bp_id, **kwargs):
        captured.append(bp_id)
        return reproduce.ReproducibilityResult(
            blueprint_id=bp_id,
            byte_identical=True,
            environment_fingerprint="fp",
            artifact_id_a="a",
            artifact_id_b="a",
            category_identical=dict.fromkeys(reproduce.CATEGORIES, True),
            diffs=(),
        )

    monkeypatch.setattr(reproduce, "double_build", _fake)
    exit_code = main(["--evidence-dir", str(tmp_path / "ev")])
    assert exit_code == 0
    assert captured == ["BP-DATA-0001"]
