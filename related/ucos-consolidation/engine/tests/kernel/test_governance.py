"""Tests for Universal Governance (open policies + universal constraints)."""

from __future__ import annotations

import pytest

from engine.kernel.governance import Constraint, Governance, Policy
from engine.kernel.meta import make_metatype
from engine.kernel.registry import UniversalRegistry


def _always_ok(_candidate, _view):
    return True, ""


def _always_fail(_candidate, _view):
    return False, "denied by test constraint"


def test_default_admission_policy_has_universal_constraints():
    gov = Governance()
    names = gov.admission.constraint_names()
    assert "identity-present" in names
    assert "metatype-registered" in names
    assert "relationships-acyclic" in names
    assert "content-unique" in names


def test_register_constraint_extends_admission():
    gov = Governance()
    gov.register_constraint(Constraint("extra", _always_ok))
    assert "extra" in gov.admission.constraint_names()


def test_register_policy_and_lookup():
    gov = Governance()
    gov.register_policy(Policy("custom", [Constraint("c", _always_ok)]))
    assert "custom" in gov.policy_names()
    assert gov.policy("custom").constraint_names() == ["c"]


def test_register_duplicate_policy_rejected():
    gov = Governance()
    with pytest.raises(ValueError):
        gov.register_policy(Policy("admission"))


def test_decision_reports_reasons():
    gov = Governance()
    gov.register_constraint(Constraint("fails", _always_fail))
    registry = UniversalRegistry(governance=gov)
    candidate = make_metatype("Anything")
    decision = gov.evaluate(candidate, registry)
    assert decision.allowed is False
    assert "denied by test constraint" in decision.reasons
    d = decision.to_dict()
    assert d["allowed"] is False
    assert any(o["constraint"] == "fails" for o in d["outcomes"])


def test_describe_is_deterministic():
    assert Governance().describe() == Governance().describe()
