"""The CCE ten gates, shown REFUSING — across every Band-13 certification module at once.

WHY THIS FILE EXISTS, AND WHY IT IS ONE FILE. Eleven infrastructure units each publish a
``cce_gates()`` suite of ten blocking criteria, and every existing suite certifies a
construct that satisfies all ten. So the ``_passed`` arm of every gate was measured and the
``_failed`` arm of none of them was: ten gates observed only agreeing with their subject,
in eleven modules, is eleven copies of a control nobody has ever seen fire.

The argument is identical in all eleven, so it is authored ONCE (UCKP-ART-03) and the
modules are DISCOVERED rather than listed (UCKP-ART-08): a twelfth certification module
added to ``infrastructure/`` is held to this the moment it exists, with no edit here.

WHAT A REFUSING SUBJECT IS. ``CertificationSubject`` is a pure projection of a validation
outcome, so a refusal is produced by handing the gates a projection of a validation that
FAILED — never by reaching into a gate. Two are needed, because ``_checks_ok``
distinguishes a check that did not run from one that ran and failed, and a suite that only
ever produced one of those would leave the other arm unexecuted.
"""

from __future__ import annotations

import pkgutil
import sys
from typing import Any

import pytest

import infrastructure
from engine.certification.contracts import (
    CertificationClass,
    CertificationSubject,
    CriterionStatus,
)
from infrastructure import (  # noqa: F401 — imported so the walk below can resolve each one from sys.modules
    band13_certification,
    capability_certification,
    compute_certification,
    environment_certification,
    governance_certification,
    integration_certification,
    network_certification,
    resilience_certification,
    security_certification,
    storage_certification,
    topology_certification,
)


def _certification_modules() -> list[Any]:
    """Every ``infrastructure.*_certification`` module that publishes a CCE gate suite."""
    found = []
    for info in sorted(pkgutil.iter_modules(infrastructure.__path__), key=lambda i: i.name):
        if not info.name.endswith("_certification"):
            continue
        # RESOLVED THROUGH ``sys.modules``, NOT ``importlib.import_module``. A dynamic import
        # whose argument is computed is a site Ω-3 can measure no edge through, and Ω-4 holds
        # `unresolved_dynamic_sites` MONOTONIC — so importing the walk's own output would buy
        # this derivation at the cost of a permanently unmeasurable edge. Every module is
        # reached by the STATIC import above, so the lookup cannot miss; a module the header
        # does not name fails HERE, by name, which is the finding rather than a silent skip.
        module = sys.modules.get(f"infrastructure.{info.name}")
        assert module is not None, (
            f"infrastructure.{info.name} exists but no static import reaches it, so this walk "
            f"would silently skip it; name it in this module's header"
        )
        if hasattr(module, "cce_gates"):
            found.append(module)
    return found


MODULES = _certification_modules()
MODULE_IDS = [m.__name__.rsplit(".", 1)[-1] for m in MODULES]


def _subject(**overrides: Any) -> CertificationSubject:
    fields: dict[str, Any] = {
        "target_id": "TARGET",
        "blueprint_id": "BLUEPRINT",
        "version": "1.0.0",
        "certification_class": CertificationClass.ENGINEERING_READINESS,
        "validation_verdict": "fail",
        "validation_accepted": False,
        "checks_run": (),
        "blocking_failures": ("a-check-that-ran-and-refused",),
        "counts": {"failed": 3},
        "evidence_present": False,
        "evidence_sha256": "",
    }
    fields.update(overrides)
    return CertificationSubject(**fields)


def test_the_discovery_found_every_band_13_certification_module():
    """A discovery that found nothing would make every test below vacuously green."""
    assert len(MODULES) >= 11
    assert all(len(module.cce_gates()) == 10 for module in MODULES)


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_every_gate_refuses_a_validation_that_did_not_run_its_checks(module):
    """The ``:not-run`` arm. A gate whose required checks were never executed may not
    report the construct as certified — an unmeasured check is not a passed one."""
    findings = [gate.evaluate(_subject()) for gate in module.cce_gates()]
    assert [f.status for f in findings] == [CriterionStatus.FAIL] * 10
    assert all(f.criterion_id == f"CC-{n}" for n, f in enumerate(findings, start=1))
    problems = [p for f in findings for p in f.details.get("problems", [])]
    assert problems and all(p.endswith(":not-run") for p in problems)


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_every_gate_refuses_a_check_that_ran_and_failed(module):
    """The ``:failed`` arm, which is a different fact from ``:not-run`` and is reported as
    one: a check that executed and refused is evidence, and losing that distinction would
    make a broken construct indistinguishable from an unmeasured one."""
    required = sorted({cid for gate in module.cce_gates() for cid in gate.required_checks})
    assert required, "no gate in this module declares a required check"
    subject = _subject(checks_run=tuple(required), blocking_failures=tuple(required))
    findings = [gate.evaluate(subject) for gate in module.cce_gates()]
    assert all(f.status is CriterionStatus.FAIL for f in findings)
    problems = [p for f in findings for p in f.details.get("problems", [])]
    assert problems and all(p.endswith(":failed") for p in problems)


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_the_validation_gate_reports_the_verdict_it_refused_on(module):
    gate = next(g for g in module.cce_gates() if g.criterion_id == "CC-4")
    finding = gate.evaluate(_subject(validation_accepted=True, validation_verdict="warn"))
    assert finding.status is CriterionStatus.FAIL
    assert finding.details["verdict"] == "warn"


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_the_evidence_gate_refuses_a_digest_that_is_absent(module):
    gate = next(g for g in module.cce_gates() if g.criterion_id == "CC-6")
    assert gate.evaluate(_subject(evidence_present=True, evidence_sha256="")).status is (
        CriterionStatus.FAIL
    )
    assert gate.evaluate(_subject(evidence_present=False, evidence_sha256="a" * 64)).status is (
        CriterionStatus.FAIL
    )


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_the_readiness_gate_names_the_blockers_that_closed_it(module):
    gate = next(g for g in module.cce_gates() if g.criterion_id == "CC-8")
    finding = gate.evaluate(_subject(blocking_failures=("check-a", "check-b")))
    assert finding.status is CriterionStatus.FAIL
    assert finding.details["blockers"] == ["check-a", "check-b"]


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_the_gap_gate_refuses_while_any_gap_remains(module):
    gate = next(g for g in module.cce_gates() if g.criterion_id == "CC-9")
    finding = gate.evaluate(_subject(counts={"failed": 2}))
    assert finding.status is CriterionStatus.FAIL
    assert finding.details["failed"] == 2
    assert gate.evaluate(_subject(counts={"failed": 0})).status is CriterionStatus.PASS


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_the_completeness_gate_reports_which_prerequisite_was_open(module):
    gate = next(g for g in module.cce_gates() if g.criterion_id == "CC-10")
    finding = gate.evaluate(
        _subject(validation_accepted=True, evidence_present=True, counts={"failed": 1})
    )
    assert finding.status is CriterionStatus.FAIL
    assert finding.details == {"accepted": True, "evidence": True, "failed": 1}


_WITH_PRIVATE_COMPLIANCE = [m for m in MODULES if hasattr(m, "_decide_compliance")]


@pytest.mark.parametrize(
    "module",
    _WITH_PRIVATE_COMPLIANCE,
    ids=[m.__name__.rsplit(".", 1)[-1] for m in _WITH_PRIVATE_COMPLIANCE],
)
def test_every_compliance_condition_fails_when_no_check_ran(module):
    """C1…C7 are decided from the same findings, so an unmeasured validation must leave
    every condition unsatisfied rather than defaulting any of them to pass."""
    decided = module._decide_compliance(_subject())
    assert [row["id"] for row in decided] == [f"C{n}" for n in range(1, 8)]
    assert all(row["status"] == "fail" for row in decided)
