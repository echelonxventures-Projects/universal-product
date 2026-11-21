"""Completion tests — exercise every remaining branch to a genuine 100%.

These drive the defensive paths that ordinary use never reaches: the closure's re-visit
short-circuit, and the two proof loops' failure recording. No line is waived; each path is
driven by a real (if adversarial) input.
"""

from __future__ import annotations

from engine.civilization.compliance import architectural_proof
from engine.civilization.composition import CompositionPlanner
from engine.civilization.dimensions import DimensionRegistry
from engine.civilization.generation import ConstitutionalGenerator


def test_closure_short_circuits_a_requirement_queued_twice():
    # "top" queues both "a" and "b"; "b" queues "a" again before "a" has been expanded, so
    # "a" sits in the pending queue twice and the second visit takes the skip branch.
    planner = CompositionPlanner()
    planner.register_capability("a")
    planner.register_capability("b", requires=("a",))
    planner.register_capability("top", requires=("a", "b"))
    closure = planner.closure(("top",))
    assert set(closure) == {"top", "a", "b"}
    assert closure["a"] == ()
    assert closure["b"] == ("a",)


def test_the_proof_records_a_dimension_failure_as_evidence(monkeypatch):
    def refuse(self, key, **kwargs):
        raise RuntimeError(f"cannot admit {key}")

    monkeypatch.setattr(DimensionRegistry, "register_dimension", refuse)
    proof = architectural_proof()
    assert proof["passed"] is False
    assert proof["categories_proven"] == 0
    assert all(record["ok"] is False for record in proof["category_records"])
    assert all("cannot admit" in record["error"] for record in proof["category_records"])


def test_the_proof_records_an_operating_system_failure_as_evidence(monkeypatch):
    def refuse(self, key, **kwargs):
        raise RuntimeError(f"cannot generate {key}")

    monkeypatch.setattr(ConstitutionalGenerator, "register_operating_system", refuse)
    proof = architectural_proof()
    assert proof["passed"] is False
    assert proof["operating_systems_proven"] == 0
    assert all(record["ok"] is False for record in proof["operating_system_records"])
    # The dimension loop is unaffected, so a failure is isolated rather than global.
    assert proof["categories_proven"] == proof["categories_total"]
