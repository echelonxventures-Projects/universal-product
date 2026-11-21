"""UCXI-000001 Parts 07/08 — resolution and composition tests.

Resolution must be *defensible*: precedence explicit, ambiguity refused, provenance
preserved. Composition must be *bounded and isolated*: every member in exactly one
frame, every cross-frame reference federated. Both must be deterministic — the same
inputs seal identically, which is what the certifier's determinism dimension measures.
"""

from __future__ import annotations

import pytest

from engine.compiler.partition import UnboundedMemberError
from engine.context import composition as composition_module
from engine.context.composition import (
    ComposedContext,
    Federation,
    compose,
    compose_universal,
    frames_of,
    merge,
    projection,
)
from engine.context.errors import (
    ContextAmbiguityError,
    ContextCompositionError,
    ContextIsolationError,
    ContextResolutionFailure,
)
from engine.context.model import Observer
from engine.context.registry import ContextRegistry
from engine.context.resolution import (
    ContextRequest,
    candidates,
    resolution_report,
    resolve,
    resolve_kind,
    resolve_many,
    resolve_universal,
    try_resolve,
    values_of,
)
from engine.context.taxonomy import ContextAuthority, ContextKind, ContextLifecycle, ContextRelation
from engine.tests.context.conftest import declaration, spatial_values


def _temporal(**kwargs: object) -> object:
    return declaration(**kwargs)  # type: ignore[arg-type]


# -------------------------------------------------------------------- resolution


def test_resolve_returns_values_with_provenance(universal_registry: ContextRegistry) -> None:
    resolved = resolve_kind(universal_registry, ContextKind.TEMPORAL)
    assert resolved.kind == "temporal"
    assert resolved.get("ordering") == "causal — dependency order and commit ancestry"
    assert resolved.provenance_of("ordering") == "engine/determinism/reproduce.py"
    assert resolved.provenance_of("nope") is None
    assert resolved.get("nope") is None
    assert resolved.content_hash == resolve_kind(universal_registry, "temporal").content_hash
    assert resolved.to_dict()["kind"] == "temporal"


def test_resolution_is_refused_when_nothing_applies(empty_registry: ContextRegistry) -> None:
    with pytest.raises(ContextResolutionFailure):
        resolve_kind(empty_registry, ContextKind.TEMPORAL)
    resolved, reason = try_resolve(empty_registry, ContextRequest(kind="temporal"))
    assert resolved is None and reason


def test_authority_outranks_specificity(empty_registry: ContextRegistry) -> None:
    empty_registry.register(
        declaration(
            namespace="ucos",
            natural_key="broad",
            authority=ContextAuthority.CONSTITUTIONAL,
            source="charter",
            values={
                "reference_frame": "constitutional clock",
                "ordering": "causal",
                "resolution": "commit",
            },
        )
    )
    empty_registry.register(
        declaration(
            namespace="ucos.engine.runtime",
            natural_key="narrow",
            authority=ContextAuthority.OBSERVED,
            source="sensor",
            values={
                "reference_frame": "observed clock",
                "ordering": "sequence",
                "resolution": "step",
            },
        )
    )
    resolved = resolve(
        empty_registry, ContextRequest(kind="temporal", namespace="ucos.engine.runtime")
    )
    assert resolved.get("reference_frame") == "constitutional clock"
    assert resolved.provenance_of("reference_frame") == "charter"


def test_specificity_breaks_an_authority_tie(empty_registry: ContextRegistry) -> None:
    empty_registry.register(
        declaration(
            namespace="ucos",
            natural_key="broad",
            values={"reference_frame": "broad", "ordering": "a", "resolution": "b"},
        )
    )
    empty_registry.register(
        declaration(
            namespace="ucos.engine",
            natural_key="narrow",
            values={"reference_frame": "narrow", "ordering": "a2", "resolution": "b2"},
        )
    )
    resolved = resolve(empty_registry, ContextRequest(kind="temporal", namespace="ucos.engine"))
    assert resolved.get("reference_frame") == "narrow"


def test_equal_authority_and_specificity_with_different_values_is_refused(
    empty_registry: ContextRegistry,
) -> None:
    empty_registry.register(
        declaration(
            namespace="ucos.test",
            natural_key="one",
            values={"reference_frame": "clock-a", "ordering": "a", "resolution": "b"},
        )
    )
    empty_registry.register(
        declaration(
            namespace="ucos.test",
            natural_key="two",
            values={"reference_frame": "clock-b", "ordering": "a", "resolution": "b"},
        )
    )
    with pytest.raises(ContextAmbiguityError):
        resolve(empty_registry, ContextRequest(kind="temporal", namespace="ucos.test"))


def test_equal_authority_with_identical_values_is_not_a_conflict(
    empty_registry: ContextRegistry,
) -> None:
    same = {"reference_frame": "same", "ordering": "a", "resolution": "b"}
    empty_registry.register(
        declaration(namespace="ucos.test", natural_key="one", values=same, boundary="frame-a")
    )
    empty_registry.register(
        declaration(namespace="ucos.test", natural_key="two", values=same, boundary="frame-b")
    )
    resolved = resolve(empty_registry, ContextRequest(kind="temporal", namespace="ucos.test"))
    assert resolved.get("reference_frame") == "same"
    assert len(resolved.considered) == 2


def test_missing_required_dimension_is_refused(empty_registry: ContextRegistry) -> None:
    empty_registry.register(declaration())
    with pytest.raises(ContextResolutionFailure):
        resolve(
            empty_registry,
            ContextRequest(kind="temporal", dimensions=("reference_frame", "absent")),
        )


def test_boundary_and_lifecycle_filters(empty_registry: ContextRegistry) -> None:
    record = empty_registry.register(declaration(boundary="frame-a"))
    assert candidates(empty_registry, ContextRequest(kind="temporal", boundary="frame-a"))
    assert not candidates(empty_registry, ContextRequest(kind="temporal", boundary="frame-b"))

    empty_registry.transition(record.context_id, ContextLifecycle.RESOLVED)
    empty_registry.transition(record.context_id, ContextLifecycle.SUPERSEDED)
    assert not candidates(empty_registry, ContextRequest(kind="temporal"))
    assert candidates(empty_registry, ContextRequest(kind="temporal", include_inactive=True))


def test_member_scoping(universal_registry: ContextRegistry) -> None:
    temporal = universal_registry.by_kind(ContextKind.TEMPORAL)[0]
    assert candidates(
        universal_registry, ContextRequest(kind="temporal", members=(temporal.context_id,))
    )
    assert not candidates(
        universal_registry, ContextRequest(kind="temporal", members=("UCOS-CTX-000000000000",))
    )


def test_resolve_many_and_universal_and_report(universal_registry: ContextRegistry) -> None:
    everything = resolve_many(universal_registry)
    assert len(everything) == 16
    universal = resolve_universal(
        universal_registry, observer=Observer(observer_id="o", vantage="v")
    )
    assert len(universal) == 16
    assert set(values_of(universal)) == set(universal)
    report = resolution_report(universal_registry)
    assert report["all_resolvable"] and report["resolvable"] == 16 == report["total"]


def test_resolution_report_marks_unresolvable_kinds(empty_registry: ContextRegistry) -> None:
    report = resolution_report(empty_registry)
    assert not report["all_resolvable"]
    assert report["resolvable"] == 0
    assert all(row["reason"] for row in report["kinds"])


def test_request_serialisation() -> None:
    request = ContextRequest(
        kind=ContextKind.TEMPORAL,
        namespace="UCOS.Test",
        observer=Observer(observer_id="o", vantage="v"),
    )
    payload = request.to_dict()
    assert payload["kind"] == "temporal"
    assert payload["namespace"] == "ucos.test"
    assert payload["observer"]["observer_id"] == "o"


# ------------------------------------------------------------------- composition


def test_compose_universal_is_bounded_and_complete(universal_registry: ContextRegistry) -> None:
    composed = compose_universal(universal_registry)
    assert isinstance(composed, ComposedContext)
    assert len(composed.members) == 16
    assert len(composed.frames) == 1
    assert composed.is_universally_complete
    assert composed.missing_universal() == ()
    assert len(composed.kinds()) == 16
    assert composed.composition_id.startswith("CTXC-")
    assert composed.value("temporal", "ordering")
    assert composed.value("temporal", "nope") is None
    assert composed.get("nope") is None
    assert composed.frame_of(composed.members[0]) == "ucos-universal"
    assert composed.frame_of("UCOS-CTX-000000000000") is None
    assert composed.summary()["universally_complete"] is True
    assert composed.to_dict()["content_hash"] == composed.content_hash
    assert len(projection(composed)) == 16


def test_composition_is_deterministic(universal_registry: ContextRegistry) -> None:
    first = compose(universal_registry)
    second = compose(universal_registry)
    assert first.composition_id == second.composition_id
    assert first.content_hash == second.content_hash


def test_compose_refuses_empty_and_unknown_members(empty_registry: ContextRegistry) -> None:
    with pytest.raises(ContextCompositionError):
        compose(empty_registry)
    with pytest.raises(ContextCompositionError):
        compose(empty_registry, context_ids=["UCOS-CTX-000000000000"])


def test_require_universal_refuses_an_incomplete_set(empty_registry: ContextRegistry) -> None:
    empty_registry.register(declaration())
    composed = compose(empty_registry)
    assert not composed.is_universally_complete
    assert len(composed.missing_universal()) == 15
    with pytest.raises(ContextCompositionError):
        compose(empty_registry, require_universal=True)


def test_cross_frame_dependency_requires_a_federation(empty_registry: ContextRegistry) -> None:
    here = empty_registry.register(declaration(natural_key="here", boundary="frame-a"))
    there = empty_registry.register(
        declaration(
            kind=ContextKind.SPATIAL,
            natural_key="there",
            boundary="frame-b",
            values=spatial_values(),
        )
    )
    empty_registry.relate(ContextRelation.DEPENDS_ON, here.context_id, there.context_id)
    with pytest.raises(ContextIsolationError):
        compose(empty_registry)

    empty_registry.relate(ContextRelation.FEDERATES, here.context_id, there.context_id)
    composed = compose(empty_registry)
    assert len(composed.frames) == 2
    assert composed.can_reference(here.context_id, there.context_id)
    assert not composed.can_reference(there.context_id, here.context_id)
    assert composed.reference_frame_of(here.context_id) is not None
    assert composed.reference_frame_of("UCOS-CTX-000000000000") is None


def test_dependency_outside_the_composition_is_refused(empty_registry: ContextRegistry) -> None:
    here = empty_registry.register(declaration(natural_key="here"))
    there = empty_registry.register(
        declaration(kind=ContextKind.SPATIAL, natural_key="there", values=spatial_values())
    )
    empty_registry.relate(ContextRelation.DEPENDS_ON, here.context_id, there.context_id)
    with pytest.raises(ContextCompositionError):
        compose(empty_registry, context_ids=[here.context_id])


def test_supplied_federation_is_honoured(empty_registry: ContextRegistry) -> None:
    here = empty_registry.register(declaration(natural_key="here", boundary="frame-a"))
    there = empty_registry.register(
        declaration(
            kind=ContextKind.SPATIAL,
            natural_key="there",
            boundary="frame-b",
            values=spatial_values(),
        )
    )
    empty_registry.relate(ContextRelation.DEPENDS_ON, here.context_id, there.context_id)
    composed = compose(
        empty_registry,
        federations=(Federation(source=here.context_id, target=there.context_id),),
    )
    assert composed.federations


def test_merge_recomposes_from_the_registry(universal_registry: ContextRegistry) -> None:
    records = universal_registry.records()
    left = compose(universal_registry, context_ids=[records[0].context_id])
    right = compose(universal_registry, context_ids=[records[1].context_id])
    merged = merge(left, right, universal_registry)
    assert set(merged.members) == {records[0].context_id, records[1].context_id}


def test_frames_of_refuses_an_unbounded_binding() -> None:
    assert frames_of({"a": "frame"})[0].context_id == "frame"
    with pytest.raises(ContextCompositionError):
        frames_of({"a": ""})


def test_a_member_bound_to_no_frame_is_refused_as_a_composition_error(
    universal_registry: ContextRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """THE COMPILER'S ERROR IS TRANSLATED, NOT PROPAGATED.

    Frame partitioning is `engine.compiler.partition`'s job, and an ``UnboundedMemberError``
    is its vocabulary. Letting it escape would make a caller composing contexts catch an
    error from a module it never called, and the message would name a partition rather than
    the composition that asked for one. Both call sites translate it — partitioning and
    frame resolution — because either can be the first to notice.

    CXL-03 already refuses a registered context with no bounding frame, so a registry that
    reaches this is one whose records were assembled some other way; the translation is what
    keeps that a composition error rather than a compiler one.
    """

    def unbounded(_bindings):
        raise UnboundedMemberError("member has no frame")

    monkeypatch.setattr(composition_module, "resolve_partitions", unbounded)
    with pytest.raises(ContextCompositionError, match="not bound to a frame") as excinfo:
        compose(universal_registry)
    assert "member has no frame" in excinfo.value.context["detail"]


def test_a_frame_resolution_that_finds_an_unbounded_member_is_translated_too(
    universal_registry: ContextRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The second call site. ``resolve_frames`` walks the edges as well as the bindings, so
    it can find a member that partitioning did not — and the caller must see the same error
    from both, or "not bound to a frame" would mean two different exception types depending
    on which walk noticed first."""

    def unbounded(*_args, **_kwargs):
        raise UnboundedMemberError("edge names a member with no frame")

    monkeypatch.setattr(composition_module, "resolve_frames", unbounded)
    with pytest.raises(ContextCompositionError, match="not bound to a frame") as excinfo:
        compose(universal_registry)
    assert "edge names a member with no frame" in excinfo.value.context["detail"]
