"""Tests for engine.knowledge.integration.registration — Deliverable 9."""

from __future__ import annotations

import pytest

from engine.knowledge.integration.errors import RegistrationConflictError
from engine.knowledge.integration.registration import RegistrationIntegration

from .conftest import make_cko, make_intent


def test_plan_new_object_registers_universe_capability_dependency(base):
    integ = RegistrationIntegration(base)
    obj = make_cko("N", dependencies=("COMP-A",))
    plan = integ.plan_object(obj)
    by_cat = {(e.category, e.identifier): e for e in plan.entries}
    assert by_cat[("universe", "TEST")].status == "already-registered"
    assert by_cat[("capability", "N")].status == "registered"
    dep = by_cat[("dependency", "N-depends-on->COMP-A")]
    assert dep.status == "registered"
    assert dep.is_new
    counts = plan.counts()
    assert counts["registered"] >= 2
    assert plan.to_dict()["target"] == "N"


def test_idempotent_registration_of_existing_object(base):
    integ = RegistrationIntegration(base)
    plan = integ.plan_object(base.require_object("COMP-A"))
    # everything COMP-A introduces is already registered -> no new entries
    assert plan.new_entries == ()
    assert plan.counts()["registered"] == 0


def test_plan_intent(base):
    plan = RegistrationIntegration(base).plan_intent(make_intent("NEW"))
    assert any(e.category == "capability" and e.identifier == "NEW" for e in plan.entries)


def test_require_rejects_divergent_duplicate(base):
    integ = RegistrationIntegration(base)
    # same id, divergent content -> conflict
    with pytest.raises(RegistrationConflictError):
        integ.require(make_intent("COMP-A", statement="totally different substance"))
    # same id, identical substance -> no conflict, returns a plan
    same = make_intent("COMP-A", title="alpha component", statement="the alpha component substance")
    assert integ.require(same) is not None


def test_every_link_an_object_declares_is_a_thing_to_register(base):
    """Decision links and a certification are registrations too, and both were unplanned.

    The plan is what a caller acts on, so a category missing from it is a registration that
    silently never happens — the object lands with a decision link nothing recorded and a
    certification nothing knows about. Their STATUS is derived the same way every other
    category's is: already-registered when the base already holds it, registered otherwise.
    """
    obj = make_cko("N", decision_links=("UDR-KNOWN", "UDR-UNKNOWN"), certification="CERT-1")
    plan = RegistrationIntegration(base).plan_object(obj)
    by_cat = {(e.category, e.identifier): e for e in plan.entries}

    assert by_cat[("decision", "UDR-KNOWN")].status == "registered"
    assert by_cat[("decision", "UDR-UNKNOWN")].status == "registered"
    assert by_cat[("certification", "CERT-1")].status == "registered"
    assert by_cat[("certification", "CERT-1")].payload == {"certification": "CERT-1"}

    bare = RegistrationIntegration(base).plan_object(make_cko("M"))
    assert not any(e.category in {"decision", "certification"} for e in bare.entries)


def test_requiring_an_id_the_base_has_never_seen_plans_without_comparing(base):
    """``require`` compares content only when there IS an existing object to compare with.

    A wholly new id has nothing to diverge from, so the conflict check is skipped and the
    plan is returned — and that is the ordinary path. Every existing test drove the arm
    where the id is already present, which left the common case unexecuted.
    """
    plan = RegistrationIntegration(base).require(make_intent("BRAND-NEW"))
    assert plan.target == "BRAND-NEW"
    assert any(e.category == "capability" and e.identifier == "BRAND-NEW" for e in plan.entries)
