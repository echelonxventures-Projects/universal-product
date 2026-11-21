"""UCOS-OBSERVATION-UNIVERSE-001 OBS-INV-11 — observation influence, measured differentially.

The defect this pins, measured before the fix
---------------------------------------------
``UCOS-RIB-001`` strips eight declared working-tree measures and recomputes
``gates[].verdict``, ``gate``, ``gate_exit``, ``determination`` and ``compliance`` from
what remains. It never recomputed the AGGREGATES over those verdicts, and they are
computed far upstream at ``rib_engine.py:1939-1945`` from the *runtime* gates, before the
strip runs. The committed artifact therefore stated ``gate: OPEN``, ``gates[]`` all PASS
and ``gates_passed: 10`` in the same file, and five values plus the seal moved with the
working tree:

    metrics.gates_passed · metrics.blocking_failed · metrics.compliance_findings
    metrics.validations_failed · repository.contamination.clean · seal_sha256

Phase 8 held at ``zero_drift_rounds=0`` with ``registry_variance=5`` and
``ordering_variance=5`` while RIB was *perfectly deterministic* — rounds 1 through 5
produced byte-identical digests. The artifact was stable; it was stably wrong, because
the committed bytes were generated over a dirty tree.

Why this test is differential and not lexical
---------------------------------------------
The three guards that existed before — OBS-INV-02 (declared keys), OBS-INV-07 (signature
sweep) and RIB's own ``_WORKING_TREE_MEASURES`` — are the same kind of instrument: a
vocabulary of leak NAMES. None of the six leaking values is spelled like a leak.
``gates_passed`` is a perfectly innocent name for a contaminated number, so every
name-based guard passed while the leak sat in the artifact.

:func:`test_canonical_projection_is_invariant_under_working_tree_state` therefore varies
the observation and compares the output, which is name-free and total over whatever the
producer emits — including the values nobody has thought of yet.

:func:`test_a_non_observation_failure_still_closes_the_gate` is the other half, and is
the one that would catch a "fix" that simply stopped reporting. Nothing may be weakened:
an unclassified ignored path or any other unmet validation must still close the gate.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REGISTER = REPO / "00-BOOK" / "DATA" / "observation-universe.json"
RIB_DIR = REPO / "00-MASTER" / "UCOS-RIB-001"


@pytest.fixture(scope="module")
def register() -> dict:
    return json.loads(REGISTER.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rib_engine():
    sys.path.insert(0, str(RIB_DIR))
    try:
        import rib_engine as module
    finally:
        sys.path.pop(0)
    return module


def _runtime_model(
    *, dirty: int = 0, unclassified: int = 0, other_failure: int = 0, engine=None
) -> dict:
    """A RIB runtime model in which the named conditions are the only variables.

    ``engine`` seals the model exactly as ``build_model`` does — over the RUNTIME
    verdicts. The seal is the outermost derived value and was the last one leaking, so a
    model without one would let the differential pass while the real artifact drifted.
    """
    validations = [
        {
            "id": "VAL-01",
            "metric": "units_outside_architecture",
            "measured": other_failure,
            "expect": 0,
            "verdict": "PASS" if not other_failure else "FAIL",
            "name": "Architecture",
            "criterion": "every implementation unit lies inside a declared layer",
        },
        {
            "id": "VAL-02",
            "metric": "dirty_entries_outside_generated",
            "measured": dirty,
            "expect": 0,
            "verdict": "PASS" if not dirty else "FAIL",
            "name": "Clean tree",
            "criterion": "the working tree is clean at the computed HEAD",
        },
    ]
    validations_failed = sum(1 for v in validations if v["verdict"] != "PASS")
    gate12_failures = ([f"dirty_entries_outside_generated={dirty}"] if dirty else []) + (
        [f"ignored_unclassified={unclassified}"] if unclassified else []
    )
    gate04_failures = [f"validations_failed={validations_failed}"] if validations_failed else []
    gates = [
        {
            "id": "GATE-04",
            "name": "Repository Validation",
            "blocking": True,
            "metrics": ["validations_failed"],
            # Mirrors rib-blueprint.json. GATE-04's working-tree dependence is TRANSITIVE —
            # it gates on validations_failed, which aggregates the validations remaining once
            # the working-tree ones are set aside — so no metrics intersection can find it.
            # The engine used to carry this as a literal `gid == "GATE-04"` in three places,
            # which check-no-enumeration refuses: extending the blueprint must never require
            # a code change. The fact is declared now, so the fixture declares it too.
            "working_tree_transitive": True,
            "failures": gate04_failures,
            "verdict": "PASS" if not gate04_failures else "FAIL",
            "criterion": "every validation obligation met",
        },
        {
            "id": "GATE-12",
            "name": "Repository Clean",
            "blocking": True,
            "metrics": ["dirty_entries_outside_generated", "ignored_unclassified"],
            "failures": gate12_failures,
            "verdict": "PASS" if not gate12_failures else "FAIL",
            "criterion": "the working tree carries no uncommitted entry outside this zone",
        },
    ]
    compliance = [{"id": "CMP-01", "gate": "GATE-12", "finding": "tree dirty"}] if dirty else []
    model = {
        "units": [{"unique_id": "U-1", "unit_key": "k", "disposition": "REUSE"}],
        "verifications": [{"id": "VER-01", "verdict": "PASS"}],
        "gates": gates,
        "validations": validations,
        "compliance": compliance,
        "metrics": {
            "gate_total": len(gates),
            "gates_passed": len([g for g in gates if not g["failures"]]),
            "blocking_failed": [g["id"] for g in gates if g["blocking"] and g["failures"]],
            "validations_failed": validations_failed,
            "compliance_findings": len(compliance),
            "dirty_entries_outside_generated": dirty,
        },
        "repository": {
            "dirty_entries": dirty,
            "tracked_files": 5762,
            "contamination": {
                "available": True,
                "clean": not dirty,
                "contamination_entries": dirty,
            },
        },
        "gate": "OPEN" if not (dirty or unclassified or other_failure) else "CLOSED",
        "determination": "BLUEPRINT CERTIFIED — REPOSITORY MAY PROCEED",
    }
    if engine is not None:
        model["seal_sha256"] = engine.digest(engine.seal_payload(model))
    return model


def _flatten(node, path: str = ""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _flatten(value, f"{path}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _flatten(value, f"{path}[{index}]")
    else:
        yield path, node


# --- the boundary itself ------------------------------------------------------------


def test_the_register_declares_the_derived_observation_rule(register) -> None:
    rule = register["derived_observation_rule"]
    assert "directly or through derived values" in rule["statement"]
    assert rule["test"]["kind"] == "DIFFERENTIAL"
    assert "OBS-INV-11" in rule["measured_by"]


def test_every_declared_observation_source_can_actually_be_detected(register) -> None:
    """A source with no detect pattern cannot be varied, so it cannot be measured."""
    for name, spec in register["observation_sources"].items():
        assert spec.get("detect"), f"{name} declares no detect pattern"
        assert spec.get("canonical_admissibility"), name


# --- OBS-INV-11, the differential ---------------------------------------------------


def test_canonical_projection_is_invariant_under_working_tree_state(rib_engine) -> None:
    """THE invariant. Hold the commit fixed; vary only the observation.

    Against the previous implementation this found six leaking canonical values.
    """
    clean = rib_engine.canonical_model(copy.deepcopy(_runtime_model(dirty=0, engine=rib_engine)))
    dirty = rib_engine.canonical_model(copy.deepcopy(_runtime_model(dirty=72, engine=rib_engine)))

    left, right = dict(_flatten(clean)), dict(_flatten(dirty))
    leaking = sorted(k for k in set(left) | set(right) if left.get(k) != right.get(k))
    assert leaking == [], "canonical values that move with the working tree:\n  " + "\n  ".join(
        f"{k}: clean={left.get(k)!r} dirty={right.get(k)!r}" for k in leaking
    )


@pytest.mark.parametrize("dirty", [1, 16, 72, 5000])
def test_the_projection_is_invariant_at_every_magnitude(rib_engine, dirty) -> None:
    """A count is a lower-resolution copy; so is a boolean. Neither may survive."""
    baseline = rib_engine.canonical_model(copy.deepcopy(_runtime_model(dirty=0, engine=rib_engine)))
    observed = rib_engine.canonical_model(
        copy.deepcopy(_runtime_model(dirty=dirty, engine=rib_engine))
    )
    assert observed == baseline


# --- nothing weakened ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("condition", "expected"),
    [
        ({}, "OPEN"),
        ({"dirty": 72}, "OPEN"),
        ({"unclassified": 3}, "CLOSED"),
        ({"other_failure": 1}, "CLOSED"),
        ({"dirty": 72, "unclassified": 3}, "CLOSED"),
    ],
)
def test_a_non_observation_failure_still_closes_the_gate(rib_engine, condition, expected) -> None:
    """The half that catches a "fix" that merely stopped reporting.

    A dirty tree is an observation and must not close the CANONICAL gate — it is not a
    fact about the commit. An unclassified ignored path is a fact about the commit and
    must still close it, even when measured by the same gate on the same run.
    """
    projected = rib_engine.canonical_model(
        copy.deepcopy(_runtime_model(**condition, engine=rib_engine))
    )
    assert projected["gate"] == expected
    assert projected["gate_exit"] == (0 if expected == "OPEN" else 1)


def test_the_runtime_verdict_is_preserved_for_the_process_exit(rib_engine) -> None:
    """RIB must still refuse a dirty tree at runtime — only the ARTIFACT is cleansed."""
    model = _runtime_model(dirty=72, engine=rib_engine)
    rib_engine.canonical_model(copy.deepcopy(model))
    assert model["metrics"]["blocking_failed"] == ["GATE-04", "GATE-12"]
    assert model["repository"]["contamination"]["clean"] is False


def test_the_observation_is_referenced_not_deleted(rib_engine) -> None:
    """Evidence is relocated, never destroyed: the slot keeps a resolvable identity."""
    projected = rib_engine.canonical_model(
        copy.deepcopy(_runtime_model(dirty=72, engine=rib_engine))
    )
    reference = projected["working_tree_verdict_observation"]
    assert reference
    contamination = projected["repository"]["contamination"]
    assert contamination["clean"] == reference, "the boolean must carry the identity"
