"""TASK-000039 — Runtime Context + Reference Frame unit tests (EPIC-006).

Exercises context resolution (boundedness, ORL-14) and reference-frame resolution:
same-context visibility, cross-context isolation (ORL-13), and explicit,
collision-free federation (ORL-12).
"""

from __future__ import annotations

import pytest

from engine.runtime.context import (
    DEFAULT_CONTEXT,
    Federation,
    ReferenceFrame,
    RuntimeContext,
    resolve_contexts,
    resolve_reference_frames,
)
from engine.runtime.errors import ContextResolutionError, ReferenceFrameError
from engine.runtime.graph import RuntimeGraph


@pytest.fixture
def chain() -> RuntimeGraph:
    """b depends on a."""
    return RuntimeGraph.of({"a": (), "b": ("a",)})


# -- value types --------------------------------------------------------------


def test_runtime_context_contains_and_dict():
    context = RuntimeContext(context_id="ctx", members=("a", "b"))
    assert context.contains("a")
    assert not context.contains("z")
    assert context.to_dict() == {"context_id": "ctx", "members": ["a", "b"]}


def test_federation_dict():
    assert Federation("a", "b").to_dict() == {"source": "a", "target": "b"}


def test_reference_frame_can_reference_and_dict():
    frame = ReferenceFrame("a", "ctx", ("b",), ("b",))
    assert frame.can_reference("b")
    assert not frame.can_reference("c")
    assert frame.to_dict()["federated"] == ["b"]


# -- context resolution -------------------------------------------------------


def test_resolve_contexts_groups_members():
    contexts = resolve_contexts({"a": "c1", "b": "c1", "c": "c2"})
    assert [c.context_id for c in contexts] == ["c1", "c2"]
    assert contexts[0].members == ("a", "b")
    assert contexts[1].members == ("c",)


@pytest.mark.parametrize("bad", ["", None, 123])
def test_resolve_contexts_refuses_unbounded(bad):
    with pytest.raises(ContextResolutionError):
        resolve_contexts({"a": bad})


# -- reference-frame resolution -----------------------------------------------


def test_same_context_visibility(chain):
    bindings = {"a": DEFAULT_CONTEXT, "b": DEFAULT_CONTEXT}
    frames = {f.universe_id: f for f in resolve_reference_frames(bindings, chain)}
    assert frames["a"].visible == ("b",)
    assert frames["b"].visible == ("a",)
    assert frames["a"].federated == ()


def test_cross_context_dependency_needs_federation(chain):
    bindings = {"a": "c1", "b": "c2"}
    with pytest.raises(ReferenceFrameError) as exc:
        resolve_reference_frames(bindings, chain)
    assert "isolation leak" in exc.value.message


def test_cross_context_dependency_allowed_with_federation(chain):
    bindings = {"a": "c1", "b": "c2"}
    frames = {
        f.universe_id: f for f in resolve_reference_frames(bindings, chain, [Federation("b", "a")])
    }
    assert frames["b"].federated == ("a",)
    assert frames["b"].visible == ("a",)
    assert frames["a"].visible == ()  # a is alone in c1 and federates nothing


def test_graph_node_without_binding_rejected(chain):
    with pytest.raises(ContextResolutionError):
        resolve_reference_frames({"a": "c1"}, chain)  # b unbound


# -- federation validation ----------------------------------------------------


def test_federation_dangling_source(chain):
    bindings = {"a": "c1", "b": "c2"}
    with pytest.raises(ReferenceFrameError) as exc:
        resolve_reference_frames(bindings, chain, [Federation("ghost", "a")])
    assert "source" in exc.value.message


def test_federation_dangling_target(chain):
    bindings = {"a": "c1", "b": "c2"}
    with pytest.raises(ReferenceFrameError) as exc:
        resolve_reference_frames(bindings, chain, [Federation("b", "ghost")])
    assert "target" in exc.value.message


def test_federation_self_refused(chain):
    bindings = {"a": "c1", "b": "c2"}
    with pytest.raises(ReferenceFrameError) as exc:
        resolve_reference_frames(bindings, chain, [Federation("b", "b")])
    assert "itself" in exc.value.message


def test_federation_same_context_refused(chain):
    bindings = {"a": DEFAULT_CONTEXT, "b": DEFAULT_CONTEXT}
    with pytest.raises(ReferenceFrameError) as exc:
        resolve_reference_frames(bindings, chain, [Federation("b", "a")])
    assert "cross-context" in exc.value.message


def test_federation_duplicate_refused(chain):
    bindings = {"a": "c1", "b": "c2"}
    dup = [Federation("b", "a"), Federation("b", "a")]
    with pytest.raises(ReferenceFrameError) as exc:
        resolve_reference_frames(bindings, chain, dup)
    assert "collision" in exc.value.message
