"""Tests for engine.knowledge.integration.traceability — Deliverable 7."""

from __future__ import annotations

import pytest

from engine.knowledge.errors import KnowledgeNotFoundError
from engine.knowledge.integration.traceability import TRACE_STAGES, TraceabilityEngine
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase

from .conftest import make_cko


def test_trace_stage_vocabulary():
    assert TRACE_STAGES == (
        "constitution",
        "universe",
        "capability",
        "implementation",
        "validation",
        "certification",
        "evidence",
        "deployment",
        "runtime",
    )


def test_trace_resolves_stages():
    principle = make_cko(
        "P",
        kind=KnowledgeKind.PRINCIPLE,
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        lifecycle=Lifecycle.RATIFIED,
    )
    target = make_cko(
        "X",
        dependencies=("P",),
        lifecycle=Lifecycle.OPERATIONAL,
        validation="V-1",
        certification="C-1",
        evidence=("E-1",),
    )
    engine = TraceabilityEngine(KnowledgeBase([principle, target]))
    chain = engine.trace("X")
    assert chain.stage("constitution").references == ("P",)
    assert chain.stage("universe").present
    assert chain.stage("capability").references == ("X",)
    assert chain.stage("validation").references == ("V-1",)
    assert chain.stage("certification").references == ("C-1",)
    assert chain.stage("evidence").references == ("E-1",)
    assert chain.stage("deployment").references == ("operational",)
    assert chain.stage("runtime").references == ("operational",)
    # implementation is a genuine gap (no implements edges)
    assert "implementation" in chain.gaps
    assert not chain.complete
    assert chain.stage("nonexistent-stage") is None
    assert chain.to_dict()["target"] == "X"


def test_constitutional_object_traces_itself():
    principle = make_cko(
        "ROOT",
        kind=KnowledgeKind.PRINCIPLE,
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        lifecycle=Lifecycle.RATIFIED,
    )
    chain = TraceabilityEngine(KnowledgeBase([principle])).trace("ROOT")
    assert "ROOT" in chain.stage("constitution").references
    # a draft-less ratified object is not deployed/runtime
    assert not chain.stage("deployment").present


def test_trace_unknown_raises():
    with pytest.raises(KnowledgeNotFoundError):
        TraceabilityEngine(KnowledgeBase([])).trace("MISSING")
