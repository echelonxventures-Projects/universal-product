"""Provider SDK tests (Terminal-04).

The SDK's claim is that constitutional conformance is not optional for a provider
author. These tests attack that claim from the author's side: they try to return an
unattributed resource, a foreign resource, a wrong-kind resource, to be served an
undeclared capability, and to have a substrate fault escape.
"""

from __future__ import annotations

from collections.abc import Iterable
from platform.tests.universal_provider_helpers import (
    MEMO_RESOURCE_KIND,
    DegradedProvider,
    FaultyProvider,
    MemoProvider,
    memo_capabilities,
    memo_descriptor,
)
from platform.universal_provider.constitution import ProviderOperation
from platform.universal_provider.contracts import (
    ProviderCapability,
    ProviderQuery,
    ProviderResource,
    ProviderState,
)
from platform.universal_provider.discovery import RegistrySource
from platform.universal_provider.errors import (
    ProviderCapabilityError,
    ProviderContractError,
    ProviderExecutionError,
)
from platform.universal_provider.registry import ProviderRegistry
from platform.universal_provider.sdk import (
    BaseProvider,
    declare_capability,
    declare_dependency,
    declare_provider,
)

import pytest


class BadlyAttributedProvider(MemoProvider):
    """Returns a resource attributed to a different provider."""

    def resolve_query(
        self, capability: ProviderCapability, request: ProviderQuery
    ) -> Iterable[ProviderResource]:
        yield ProviderResource(
            resource_id="stolen",
            kind=MEMO_RESOURCE_KIND,
            provider_id="someone.else",
            payload={},
            provenance={"source_of_record": "elsewhere"},
        )


class WrongKindProvider(MemoProvider):
    """Returns a resource whose kind contradicts the declared capability."""

    def resolve_query(
        self, capability: ProviderCapability, request: ProviderQuery
    ) -> Iterable[ProviderResource]:
        yield self.resource("odd", "some.other.kind", {})


class NonResourceProvider(MemoProvider):
    """Returns something that is not a resource at all."""

    def resolve_query(
        self, capability: ProviderCapability, request: ProviderQuery
    ) -> Iterable[ProviderResource]:
        yield "not a resource"  # type: ignore[misc]


def test_declare_helpers_build_conformant_declarations() -> None:
    capability = declare_capability("c", "query", selector_keys=("a",))
    assert capability.operation is ProviderOperation.QUERY
    dependency = declare_dependency("c.d", min_version="1.2.3", optional=True)
    assert dependency.optional is True
    descriptor = declare_provider(
        "a.b", "memo", "1.0.0", capabilities=(capability,), dependencies=(dependency,)
    )
    assert descriptor.qualified_id == "a.b@1.0.0"


def test_provider_construction_requires_every_substrate_operation() -> None:
    query_only = declare_provider(
        "a.b", "memo", "1.0.0", capabilities=(declare_capability("c", "query"),)
    )
    with pytest.raises(ProviderCapabilityError) as exc:
        MemoProvider(query_only)
    assert set(exc.value.detail["undeclared_operations"]) == {"fetch", "verify"}


def test_provider_construction_requires_a_descriptor() -> None:
    with pytest.raises(ProviderContractError):
        MemoProvider("not a descriptor")  # type: ignore[arg-type]


def test_describe_and_capabilities_are_intrinsic() -> None:
    provider = MemoProvider(memo_descriptor())
    assert provider.describe().qualified_id == "fixture.memo@1.0.0"
    assert [c.name for c in provider.capabilities()] == [c.name for c in memo_capabilities()]
    assert provider.config == {}


def test_query_orders_deterministically_despite_an_unordered_substrate() -> None:
    provider = MemoProvider(memo_descriptor())
    response = provider.query(ProviderQuery(capability="memo.notes"))
    assert response.resource_ids() == ("note-a", "note-b", "note-c")
    assert response.diagnostics == {"matched": 3, "returned": 3, "offset": 0}
    assert response.truncated is False


def test_query_is_reproducible() -> None:
    provider = MemoProvider(memo_descriptor())
    request = ProviderQuery(capability="memo.notes")
    assert provider.query(request).response_hash == provider.query(request).response_hash


def test_query_paginates_with_a_stable_cursor() -> None:
    provider = MemoProvider(memo_descriptor())
    first = provider.query(ProviderQuery(capability="memo.notes", limit=2))
    assert first.resource_ids() == ("note-a", "note-b")
    assert first.truncated is True
    assert first.next_cursor == "2"
    second = provider.query(
        ProviderQuery(capability="memo.notes", limit=2, cursor=first.next_cursor)
    )
    assert second.resource_ids() == ("note-c",)
    assert second.truncated is False
    assert second.next_cursor == ""


def test_query_honours_the_declared_selector() -> None:
    provider = MemoProvider(memo_descriptor())
    tagged = provider.query(ProviderQuery(capability="memo.notes", selector={"tag": "red"}))
    assert tagged.resource_ids() == ("note-a", "note-c")
    prefixed = provider.query(
        ProviderQuery(capability="memo.notes", selector={"id_prefix": "note-b"})
    )
    assert prefixed.resource_ids() == ("note-b",)


def test_query_refuses_an_undeclared_capability_and_an_undeclared_selector_key() -> None:
    provider = MemoProvider(memo_descriptor())
    with pytest.raises(ProviderCapabilityError):
        provider.query(ProviderQuery(capability="memo.absent"))
    with pytest.raises(ProviderCapabilityError) as exc:
        provider.query(ProviderQuery(capability="memo.notes", selector={"colour": "red"}))
    assert exc.value.detail["undeclared"] == ["colour"]


def test_query_refuses_a_capability_bound_to_another_operation() -> None:
    provider = MemoProvider(memo_descriptor())
    with pytest.raises(ProviderCapabilityError) as exc:
        provider.query(ProviderQuery(capability="memo.note"))
    assert exc.value.detail["operation"] == "fetch"


def test_query_refuses_a_missing_required_selector_key() -> None:
    descriptor = memo_descriptor(
        capabilities=(
            declare_capability(
                "memo.notes",
                "query",
                resource_kind=MEMO_RESOURCE_KIND,
                selector_keys=("tag",),
                required_selector_keys=("tag",),
            ),
            *memo_capabilities()[1:],
        )
    )
    provider = MemoProvider(descriptor)
    with pytest.raises(ProviderCapabilityError) as exc:
        provider.query(ProviderQuery(capability="memo.notes"))
    assert exc.value.detail["missing"] == ["tag"]


def test_query_requires_a_provider_query_and_a_valid_cursor() -> None:
    provider = MemoProvider(memo_descriptor())
    with pytest.raises(ProviderContractError):
        provider.query("memo.notes")  # type: ignore[arg-type]
    with pytest.raises(ProviderContractError):
        provider.query(ProviderQuery(capability="memo.notes", cursor="abc"))
    with pytest.raises(ProviderContractError):
        provider.query(ProviderQuery(capability="memo.notes", cursor="-1"))


def test_fetch_resolves_one_resource_and_fails_closed_when_absent() -> None:
    provider = MemoProvider(memo_descriptor())
    assert provider.fetch("note-a").payload["title"] == "alpha"
    with pytest.raises(ProviderExecutionError) as exc:
        provider.fetch("note-absent")
    assert "PC-07" in exc.value.message
    with pytest.raises(ProviderContractError):
        provider.fetch("  ")


def test_verify_derives_an_attestation_and_reports_the_unresolvable_honestly() -> None:
    provider = MemoProvider(memo_descriptor())
    attestation = provider.verify("note-a")
    assert attestation.verified is True
    assert attestation.provenance_chain == (
        "in-memory fixture substrate",
        "fixture.memo@1.0.0",
    )
    absent = provider.verify("note-absent")
    assert absent.verified is False
    assert absent.reasons == ("unresolvable: UPA-EXECUTION",)
    with pytest.raises(ProviderContractError):
        provider.verify("")


def test_verify_refuses_to_attest_an_empty_provenance_chain() -> None:
    class ChainlessProvider(MemoProvider):
        def provenance_chain(self, resource: ProviderResource) -> tuple[str, ...]:
            return ()

    attestation = ChainlessProvider(memo_descriptor()).verify("note-a")
    assert attestation.verified is False
    assert "PC-06" in attestation.reasons[0]


def test_health_reports_serving_degraded_and_unavailable() -> None:
    assert MemoProvider(memo_descriptor()).health().state is ProviderState.SERVING
    degraded = DegradedProvider(memo_descriptor()).health()
    assert degraded.state is ProviderState.DEGRADED
    assert degraded.reasons == ("check failed: index_fresh",)
    empty = MemoProvider(memo_descriptor(), {"notes": {}}).health()
    assert empty.state is ProviderState.UNAVAILABLE


def test_health_isolates_a_raising_probe_instead_of_propagating_it() -> None:
    health = FaultyProvider(memo_descriptor()).health()
    assert health.state is ProviderState.UNAVAILABLE
    assert health.checks == {"probe": False}
    assert health.reasons == ("probe raised RuntimeError",)


def test_a_substrate_fault_becomes_a_typed_framework_error() -> None:
    provider = FaultyProvider(memo_descriptor())
    with pytest.raises(ProviderExecutionError) as exc:
        provider.query(ProviderQuery(capability="memo.notes"))
    assert exc.value.detail["operation"] == "query"
    assert "RuntimeError" in exc.value.detail["cause"]


def test_a_provider_may_not_return_a_foreign_wrong_kind_or_non_resource_value() -> None:
    descriptor = memo_descriptor()
    request = ProviderQuery(capability="memo.notes")
    with pytest.raises(ProviderContractError) as foreign:
        BadlyAttributedProvider(descriptor).query(request)
    assert foreign.value.detail["attributed_to"] == "someone.else"
    with pytest.raises(ProviderContractError) as wrong_kind:
        WrongKindProvider(descriptor).query(request)
    assert wrong_kind.value.detail["declared_kind"] == MEMO_RESOURCE_KIND
    with pytest.raises(ProviderContractError):
        NonResourceProvider(descriptor).query(request)


def test_resource_helper_injects_attribution_and_the_declared_source_of_record() -> None:
    provider = MemoProvider(memo_descriptor())
    resource = provider.resource("x", MEMO_RESOURCE_KIND, {"a": 1})
    assert resource.provider_id == "fixture.memo"
    assert resource.provenance["source_of_record"] == "in-memory fixture substrate"
    override = provider.resource(
        "y", MEMO_RESOURCE_KIND, {}, provenance={"source_of_record": "explicit"}
    )
    assert override.provenance["source_of_record"] == "explicit"


def test_a_non_deterministic_capability_is_not_reordered() -> None:
    descriptor = memo_descriptor(
        capabilities=(
            declare_capability(
                "memo.notes",
                "query",
                resource_kind=MEMO_RESOURCE_KIND,
                selector_keys=("tag", "id_prefix"),
                deterministic=False,
            ),
            *memo_capabilities()[1:],
        )
    )
    response = MemoProvider(descriptor).query(ProviderQuery(capability="memo.notes"))
    assert response.resource_ids() == ("note-c", "note-b", "note-a")


def test_base_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseProvider(memo_descriptor())  # type: ignore[abstract]


def test_a_provider_declaring_no_health_checks_is_serving() -> None:
    """AN EMPTY PROBE IS A PASS, NOT AN ABSENCE.

    ``probe`` is the SDK's extension point for substrate health, and a provider with nothing
    to check must report serviceable rather than unknown — otherwise every provider would
    have to implement a probe to be usable, which would make the default the one thing that
    cannot ship. The memo fixture overrides it, which is why the default had never run.
    """
    descriptor = memo_descriptor()

    class _NoProbe(BaseProvider):
        def resolve_query(self, capability, request):
            return ()

        def resolve_resource(self, resource_id: str):
            return None

    provider = _NoProbe(descriptor)
    assert provider.probe() == {}
    assert provider.health().serving is True


def test_a_framework_error_from_inside_a_provider_is_re_raised_unchanged() -> None:
    """FAULT ISOLATION CONVERTS THE UNTYPED, AND PASSES THE TYPED THROUGH.

    A provider that already refused in the framework's own vocabulary has said exactly what
    went wrong; wrapping it again would bury a precise code inside a generic execution error
    and the caller would have to unwrap two layers to find out that the resource simply does
    not exist. Only the untyped arm had been driven.
    """

    descriptor = memo_descriptor()

    class _Typed(BaseProvider):
        def resolve_query(self, capability, request):
            return ()

        def resolve_resource(self, resource_id: str):
            raise ProviderCapabilityError("no such note", {"resource_id": resource_id})

    with pytest.raises(ProviderCapabilityError) as excinfo:
        _Typed(descriptor).fetch("note-a")
    assert not isinstance(excinfo.value, ProviderExecutionError)
    assert excinfo.value.detail["resource_id"] == "note-a"


def test_a_registry_source_reports_the_name_every_discovery_is_recorded_under() -> None:
    """The source name is what a discovery record is attributed to, so a discovery whose
    source could not be named would be a provider that appeared from nowhere. The declaration
    source's name had a caller; the registry source's did not."""

    registry = ProviderRegistry.from_descriptors([memo_descriptor()])

    assert RegistrySource(registry).name == "registry"
    assert RegistrySource(registry, name="upstream").name == "upstream"
    assert all(d.source == "upstream" for d in RegistrySource(registry, "upstream").discover())
