"""Provider Composition tests (Terminal-04).

The claim under test is closure: a composite of providers satisfies the very same
constitutional interface, so it can be validated by the same gates, nested inside
another composite, and consumed by code that cannot tell the difference.
"""

from __future__ import annotations

from platform.tests.universal_provider_helpers import (
    MEMO_RESOURCE_KIND,
    FaultyProvider,
    MemoProvider,
    memo_capabilities,
    memo_descriptor,
)
from platform.universal_provider.composition import (
    CompositeProvider,
    CompositionStrategy,
    compose_providers,
)
from platform.universal_provider.constitution import ProviderOperation
from platform.universal_provider.contracts import (
    ProviderIdentity,
    ProviderQuery,
    ProviderResource,
    ProviderState,
    provider_operations,
)
from platform.universal_provider.errors import (
    ProviderCapabilityError,
    ProviderCompositionError,
    ProviderExecutionError,
)
from platform.universal_provider.lifecycle import ProviderLifecycle, ProviderPhase
from platform.universal_provider.registry import ProviderRegistry
from platform.universal_provider.sdk import declare_capability
from platform.universal_provider.validation import (
    ProviderValidator,
    ValidationStatus,
    ValidationSubject,
)

import pytest

LEFT_NOTES = {"left-1": {"tag": "red"}, "shared": {"tag": "red"}}
RIGHT_NOTES = {"right-1": {"tag": "blue"}, "shared": {"tag": "blue"}}


def _left() -> MemoProvider:
    return MemoProvider(memo_descriptor(provider_id="fixture.left"), {"notes": LEFT_NOTES})


def _right() -> MemoProvider:
    return MemoProvider(memo_descriptor(provider_id="fixture.right"), {"notes": RIGHT_NOTES})


def _composite(strategy: CompositionStrategy = CompositionStrategy.FEDERATED) -> CompositeProvider:
    return compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [_left(), _right()],
        strategy=strategy,
        authority="TEST",
        description="a composition of two memo providers",
    )


# ---------------------------------------------------------------------------- closure


def test_a_composite_satisfies_the_constitutional_interface() -> None:
    composite = _composite()
    assert provider_operations(composite) == provider_operations(_left())
    assert len(provider_operations(composite)) == 6


def test_a_composite_synthesizes_its_own_descriptor() -> None:
    composite = _composite()
    descriptor = composite.describe()
    assert descriptor.qualified_id == "fixture.fabric@1.0.0"
    assert descriptor.kind == "fabric"
    assert descriptor.metadata["composition_strategy"] == "federated"
    assert descriptor.metadata["composition_members"] == [
        "fixture.left@1.0.0",
        "fixture.right@1.0.0",
    ]
    assert [d.provider_id for d in descriptor.dependencies] == [
        "fixture.left",
        "fixture.right",
    ]
    assert descriptor.source_of_record == "in-memory fixture substrate"


def test_a_composite_passes_the_same_gates_as_a_single_provider() -> None:
    composite = _composite()
    descriptor = composite.describe()
    registry = ProviderRegistry()
    registry.register(memo_descriptor(provider_id="fixture.left"))
    registry.register(memo_descriptor(provider_id="fixture.right"))
    registry.register(descriptor)
    lifecycle = ProviderLifecycle()
    lifecycle.declare(descriptor.qualified_id)
    lifecycle.transition(descriptor.qualified_id, ProviderPhase.REGISTERED)
    report = ProviderValidator().validate(
        ValidationSubject(
            descriptor=descriptor, instance=composite, registry=registry, lifecycle=lifecycle
        )
    )
    assert report.status in {ValidationStatus.PASSED, ValidationStatus.INCOMPLETE}
    assert report.failures() == ()


def test_composition_nests_to_arbitrary_depth() -> None:
    inner = _composite()
    outer = compose_providers("fixture.meta", "fabric", "1.0.0", [inner], authority="TEST")
    response = outer.query(ProviderQuery(capability="memo.notes"))
    assert len(response) == 3
    assert outer.describe().metadata["composition_members"] == ["fixture.fabric@1.0.0"]


# --------------------------------------------------------------------------- strategy


def test_federated_returns_the_union_attributed_to_each_member() -> None:
    response = _composite().query(ProviderQuery(capability="memo.notes"))
    assert response.resource_ids() == ("left-1", "shared", "right-1", "shared")
    assert [r.provider_id for r in response.resources] == [
        "fixture.left",
        "fixture.left",
        "fixture.right",
        "fixture.right",
    ]
    assert response.diagnostics["strategy"] == "federated"
    assert response.diagnostics["contributions"] == {"fixture.left": 2, "fixture.right": 2}
    assert response.provider_id == "fixture.fabric"


def test_layered_deduplicates_by_resource_id_with_the_first_member_winning() -> None:
    response = _composite(CompositionStrategy.LAYERED).query(ProviderQuery(capability="memo.notes"))
    assert response.resource_ids() == ("left-1", "shared", "right-1")
    shared = next(r for r in response.resources if r.resource_id == "shared")
    assert shared.provider_id == "fixture.left"


def test_fallback_stops_at_the_first_member_that_returns_anything() -> None:
    response = _composite(CompositionStrategy.FALLBACK).query(
        ProviderQuery(capability="memo.notes")
    )
    assert response.diagnostics["contributions"] == {"fixture.left": 2}
    assert set(response.resource_ids()) == {"left-1", "shared"}


def test_fallback_moves_on_when_the_first_member_is_empty() -> None:
    empty = MemoProvider(memo_descriptor(provider_id="fixture.empty"), {"notes": {}})
    composite = compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [empty, _right()],
        strategy=CompositionStrategy.FALLBACK,
        authority="TEST",
    )
    response = composite.query(ProviderQuery(capability="memo.notes"))
    assert response.diagnostics["contributions"] == {"fixture.empty": 0, "fixture.right": 2}


def test_a_strategy_may_be_supplied_as_a_string() -> None:
    composite = compose_providers(
        "fixture.fabric", "fabric", "1.0.0", [_left()], strategy="layered", authority="TEST"
    )
    assert composite.strategy is CompositionStrategy.LAYERED


def test_the_composite_paginates_the_merged_result() -> None:
    response = _composite().query(ProviderQuery(capability="memo.notes", limit=2))
    assert len(response) == 2
    assert response.truncated is True
    assert response.next_cursor == "2"


# ------------------------------------------------------------------------ resilience


def test_a_failing_member_degrades_scope_rather_than_the_composition() -> None:
    faulty = FaultyProvider(memo_descriptor(provider_id="fixture.faulty"))
    composite = compose_providers(
        "fixture.fabric", "fabric", "1.0.0", [faulty, _right()], authority="TEST"
    )
    response = composite.query(ProviderQuery(capability="memo.notes"))
    assert set(response.resource_ids()) == {"right-1", "shared"}
    assert response.diagnostics["degraded"] == {"fixture.faulty": "UPA-EXECUTION"}


def test_an_untyped_member_fault_is_isolated() -> None:
    class RawProvider(MemoProvider):
        def query(self, request: ProviderQuery):  # type: ignore[override]
            raise RuntimeError("raw")

        def fetch(self, resource_id: str) -> ProviderResource:
            raise RuntimeError("raw")

    composite = compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [RawProvider(memo_descriptor(provider_id="fixture.raw")), _right()],
        authority="TEST",
    )
    response = composite.query(ProviderQuery(capability="memo.notes"))
    assert response.diagnostics["degraded"] == {"fixture.raw": "untyped:RuntimeError"}
    assert len(response) == 2


def test_a_member_returning_a_non_response_is_recorded_as_degraded() -> None:
    class WrongReturn(MemoProvider):
        def query(self, request: ProviderQuery):  # type: ignore[override]
            return "not a response"

    composite = compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [WrongReturn(memo_descriptor(provider_id="fixture.wrong")), _right()],
        authority="TEST",
    )
    response = composite.query(ProviderQuery(capability="memo.notes"))
    assert response.diagnostics["degraded"] == {"fixture.wrong": "non-response"}


def test_health_aggregates_serving_degraded_and_unavailable() -> None:
    assert _composite().health().state is ProviderState.SERVING
    partial = compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [_left(), FaultyProvider(memo_descriptor(provider_id="fixture.faulty"))],
        authority="TEST",
    )
    degraded = partial.health()
    assert degraded.state is ProviderState.DEGRADED
    assert degraded.checks == {"fixture.left": True, "fixture.faulty": False}
    all_bad = compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [FaultyProvider(memo_descriptor(provider_id="fixture.faulty"))],
        authority="TEST",
    )
    assert all_bad.health().state is ProviderState.UNAVAILABLE


def test_health_isolates_a_member_whose_health_raises() -> None:
    class ExplodingHealth(MemoProvider):
        def health(self):  # type: ignore[override]
            raise RuntimeError("no health")

    composite = compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [ExplodingHealth(memo_descriptor(provider_id="fixture.boom")), _right()],
        authority="TEST",
    )
    health = composite.health()
    assert health.state is ProviderState.DEGRADED
    assert any("health raised RuntimeError" in reason for reason in health.reasons)


# ------------------------------------------------------------------- fetch and verify


def test_fetch_returns_the_first_member_resolution_and_otherwise_fails_closed() -> None:
    composite = _composite()
    assert composite.fetch("right-1").provider_id == "fixture.right"
    assert composite.fetch("shared").provider_id == "fixture.left"
    with pytest.raises(ProviderExecutionError) as exc:
        composite.fetch("absent")
    assert set(exc.value.detail["attempts"]) == {"fixture.left", "fixture.right"}


def test_verify_delegates_to_the_owning_member_and_appends_the_conveyor() -> None:
    attestation = _composite().verify("right-1")
    assert attestation.verified is True
    assert attestation.provider_id == "fixture.fabric"
    assert attestation.provenance_chain[-1] == "fixture.fabric@1.0.0"
    assert "fixture.right@1.0.0" in attestation.provenance_chain


def test_verify_reports_an_unresolvable_resource_honestly() -> None:
    attestation = _composite().verify("absent")
    assert attestation.verified is False
    assert attestation.resource_hash == ""
    assert attestation.reasons == ("no composition member could resolve the resource",)


def test_verify_surfaces_a_member_s_unverified_attestation_unchanged() -> None:
    class ChainlessProvider(MemoProvider):
        def provenance_chain(self, resource: ProviderResource) -> tuple[str, ...]:
            return ()

    composite = compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [
            ChainlessProvider(
                memo_descriptor(provider_id="fixture.chainless"), {"notes": LEFT_NOTES}
            )
        ],
        authority="TEST",
    )
    attestation = composite.verify("left-1")
    assert attestation.verified is False
    assert attestation.provider_id == "fixture.chainless"


# --------------------------------------------------------------------- capability merge


def test_same_named_capabilities_merge_additively() -> None:
    wide = memo_descriptor(
        provider_id="fixture.wide",
        capabilities=(
            declare_capability(
                "memo.notes",
                "query",
                resource_kind=MEMO_RESOURCE_KIND,
                selector_keys=("tag", "extra"),
                required_selector_keys=("tag",),
                effects=("net:read",),
            ),
            *memo_capabilities()[1:],
        ),
    )
    composite = compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [_left(), MemoProvider(wide, {"notes": RIGHT_NOTES})],
        authority="TEST",
    )
    merged = composite.describe().capability("memo.notes")
    assert merged.selector_keys == ("extra", "id_prefix", "tag")
    assert merged.required_selector_keys == ()
    assert merged.effects == ("mem:read", "net:read")
    assert merged.operation is ProviderOperation.QUERY


def test_determinism_conjoins_across_members() -> None:
    loose = memo_descriptor(
        provider_id="fixture.loose",
        capabilities=(
            declare_capability(
                "memo.notes",
                "query",
                resource_kind=MEMO_RESOURCE_KIND,
                selector_keys=("tag",),
                deterministic=False,
            ),
            *memo_capabilities()[1:],
        ),
    )
    composite = compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [_left(), MemoProvider(loose, {"notes": RIGHT_NOTES})],
        authority="TEST",
    )
    assert composite.describe().capability("memo.notes").deterministic is False


def test_incompatible_capability_declarations_are_refused() -> None:
    clashing_operation = memo_descriptor(
        provider_id="fixture.clash",
        capabilities=(
            declare_capability("memo.notes", "fetch", resource_kind=MEMO_RESOURCE_KIND),
            declare_capability(
                "memo.note", "query", resource_kind=MEMO_RESOURCE_KIND, selector_keys=("x",)
            ),
            *memo_capabilities()[2:],
        ),
    )
    with pytest.raises(ProviderCompositionError) as exc:
        compose_providers(
            "fixture.fabric",
            "fabric",
            "1.0.0",
            [_left(), MemoProvider(clashing_operation, {"notes": {}})],
            authority="TEST",
        )
    assert "different operations" in exc.value.message

    clashing_kind = memo_descriptor(
        provider_id="fixture.kindclash",
        capabilities=(
            declare_capability(
                "memo.notes", "query", resource_kind="other.kind", selector_keys=("tag",)
            ),
            *memo_capabilities()[1:],
        ),
    )
    with pytest.raises(ProviderCompositionError) as kind_exc:
        compose_providers(
            "fixture.fabric",
            "fabric",
            "1.0.0",
            [_left(), MemoProvider(clashing_kind, {"notes": {}})],
            authority="TEST",
        )
    assert "incompatible resource kinds" in kind_exc.value.message


# ------------------------------------------------------------------------ invariants


def test_a_composite_requires_a_proper_identity_and_at_least_one_member() -> None:
    with pytest.raises(ProviderCompositionError):
        CompositeProvider(identity="nope", members=[_left()])  # type: ignore[arg-type]
    with pytest.raises(ProviderCompositionError) as exc:
        CompositeProvider(
            identity=ProviderIdentity(provider_id="a.b", kind="fabric", version="1.0.0"),
            members=[],
        )
    assert "PC-07" in exc.value.message


def test_a_member_must_satisfy_the_constitutional_interface() -> None:
    class NotAProvider:
        def describe(self) -> None: ...

    with pytest.raises(ProviderCompositionError) as exc:
        compose_providers("fixture.fabric", "fabric", "1.0.0", [NotAProvider()], authority="TEST")
    assert "PC-01" in exc.value.message
    assert "query" in exc.value.detail["missing_operations"]


def test_a_composite_may_not_contain_itself_directly_or_transitively() -> None:
    with pytest.raises(ProviderCompositionError) as direct:
        compose_providers("fixture.left", "fabric", "1.0.0", [_left()], authority="TEST")
    assert "PC-12" in direct.value.message
    inner = _composite()
    with pytest.raises(ProviderCompositionError):
        compose_providers("fixture.left", "fabric", "1.0.0", [inner], authority="TEST")


def test_a_composite_may_not_include_the_same_provider_twice() -> None:
    with pytest.raises(ProviderCompositionError) as exc:
        compose_providers("fixture.fabric", "fabric", "1.0.0", [_left(), _left()], authority="TEST")
    assert exc.value.detail["duplicates"] == ["fixture.left"]


def test_an_undeclared_capability_is_refused_by_the_composite() -> None:
    composite = _composite()
    with pytest.raises(ProviderCapabilityError):
        composite.query(ProviderQuery(capability="memo.absent"))
    with pytest.raises(ProviderCapabilityError) as exc:
        composite.query(ProviderQuery(capability="memo.note"))
    assert exc.value.code == "UPA-CAPABILITY"
    with pytest.raises(ProviderCompositionError):
        composite.query("memo.notes")  # type: ignore[arg-type]


def test_an_undeclared_selector_key_is_refused_by_the_composite_itself() -> None:
    """PC-07: the composite admits against its merged surface before fanning out.

    A member's refusal is absorbed by fan-out fault isolation (PC-09), so if the
    composite did not admit the selector itself an undeclared key would degrade to an
    empty response instead of being refused.
    """
    composite = _composite()
    with pytest.raises(ProviderCapabilityError) as exc:
        composite.query(ProviderQuery(capability="memo.notes", selector={"undeclared.key": True}))
    assert exc.value.code == "UPA-CAPABILITY"
    assert exc.value.detail["undeclared"] == ["undeclared.key"]
    assert exc.value.detail["declared"] == ["id_prefix", "tag"]


def test_a_selector_key_every_member_requires_stays_required_on_the_composite() -> None:
    """The merged surface intersects required keys, and the composite enforces them."""
    strict = memo_descriptor(
        provider_id="fixture.strict",
        capabilities=(
            declare_capability(
                "memo.notes",
                "query",
                resource_kind=MEMO_RESOURCE_KIND,
                selector_keys=("tag",),
                required_selector_keys=("tag",),
                effects=("mem:read",),
            ),
            *memo_capabilities()[1:],
        ),
    )
    composite = compose_providers(
        "fixture.fabric",
        "fabric",
        "1.0.0",
        [MemoProvider(strict, {"notes": LEFT_NOTES})],
        authority="TEST",
    )
    assert composite.describe().capability("memo.notes").required_selector_keys == ("tag",)
    with pytest.raises(ProviderCapabilityError) as exc:
        composite.query(ProviderQuery(capability="memo.notes"))
    assert exc.value.detail["missing"] == ["tag"]
    served = composite.query(ProviderQuery(capability="memo.notes", selector={"tag": "red"}))
    assert len(served) == 2


def test_a_capability_no_member_provides_is_refused() -> None:
    """A merged surface always has a participant, so this probes the guard directly."""
    composite = _composite()
    composite._member_descriptors = (  # noqa: SLF001 - simulate a member losing a capability
        memo_descriptor(provider_id="fixture.left", capabilities=memo_capabilities()[1:]),
        memo_descriptor(provider_id="fixture.right", capabilities=memo_capabilities()[1:]),
    )
    with pytest.raises(ProviderCapabilityError) as exc:
        composite.query(ProviderQuery(capability="memo.notes"))
    assert "PC-07" in exc.value.message


def test_the_composition_hash_pins_members_and_strategy() -> None:
    first = _composite()
    assert first.composition_hash() == _composite().composition_hash()
    assert first.composition_hash() != _composite(CompositionStrategy.LAYERED).composition_hash()
    payload = first.to_dict()
    assert payload["strategy"] == "federated"
    assert payload["members"] == ["fixture.left@1.0.0", "fixture.right@1.0.0"]
    assert payload["capabilities"] == ["memo.notes", "memo.note", "memo.attestation"]
    assert len(first.members) == 2
    assert [c.name for c in first.capabilities()] == payload["capabilities"]


def test_a_member_raising_an_untyped_fault_is_isolated_and_attributed() -> None:
    """PC-09 FAULT ISOLATION IS ABOUT THE UNTYPED CASE.

    A member raising a framework error is already handled: the composite records its code
    and tries the next member. A member raising something else — a library's own exception,
    an AttributeError from a half-built substrate — must not escape the composite, or one
    misbehaving member takes down every consumer of the composition. It is recorded under
    its TYPE NAME, so the fail-closed refusal still says which member did what.

    Both loops isolate: ``fetch``, which attributes each attempt, and ``verify``, which
    probes members and moves on. A real member cannot reach either arm, because the SDK's
    own ``_isolate`` converts untyped faults before they leave the provider — so this is the
    second defence for a member that is not an SDK provider at all.
    """

    class _Untyped:
        def __init__(self, descriptor) -> None:
            self._descriptor = descriptor

        def describe(self):
            return self._descriptor

        def capabilities(self):
            return self._descriptor.capabilities

        def health(self):
            return MemoProvider(self._descriptor).health()

        def query(self, request):
            raise ZeroDivisionError("the substrate is half-built")

        def fetch(self, resource_id):
            raise ZeroDivisionError("the substrate is half-built")

        def verify(self, resource_id):
            raise ZeroDivisionError("the substrate is half-built")

    composite = compose_providers(
        "fixture.faulty-fabric",
        "fabric",
        "1.0.0",
        [_Untyped(memo_descriptor(provider_id="fixture.untyped")), _left()],
        strategy=CompositionStrategy.FALLBACK,
        authority="TEST",
        description="a composition holding one misbehaving member",
    )

    resolved = composite.fetch("left-1")
    assert resolved.resource_id == "left-1"

    attestation = composite.verify("left-1")
    assert attestation.verified

    with pytest.raises(ProviderExecutionError) as excinfo:
        composite.fetch("note-does-not-exist")
    attempts = excinfo.value.detail["attempts"]
    assert any(str(v).startswith("untyped:ZeroDivisionError") for v in attempts.values())
