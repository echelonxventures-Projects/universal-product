"""Provider Registry tests (Terminal-04).

The registry is the registration authority, so the interesting tests are the
refusals: duplicate registration, version regression, non-additive evolution, kind
mutation, and dependency cycles.
"""

from __future__ import annotations

from platform.tests.universal_provider_helpers import (
    MEMO_RESOURCE_KIND,
    memo_capabilities,
    memo_descriptor,
)
from platform.universal_provider.errors import ProviderRegistryError
from platform.universal_provider.registry import ProviderRegistry
from platform.universal_provider.sdk import (
    declare_capability,
    declare_dependency,
    declare_provider,
)

import pytest


def _descriptor(provider_id: str, version: str = "1.0.0", **kwargs: object):
    return memo_descriptor(provider_id=provider_id, version=version, **kwargs)  # type: ignore[arg-type]


def test_registration_is_content_addressed_and_sequenced() -> None:
    registry = ProviderRegistry()
    record = registry.register(memo_descriptor())
    assert record.sequence == 1
    assert record.provider_id == "fixture.memo"
    assert record.kind == "memo"
    assert record.qualified_id == "fixture.memo@1.0.0"
    assert record.descriptor_hash == memo_descriptor().content_hash()
    assert record.to_dict()["registration_id"] == record.registration_id
    assert len(registry) == 1
    assert "fixture.memo" in registry
    assert "absent.provider" not in registry
    assert 42 not in registry
    assert "not a slug" not in registry


def test_registration_is_append_only() -> None:
    registry = ProviderRegistry()
    registry.register(memo_descriptor())
    with pytest.raises(ProviderRegistryError) as exc:
        registry.register(memo_descriptor())
    assert "PC-13" in exc.value.message
    assert exc.value.detail["qualified_id"] == "fixture.memo@1.0.0"


def test_only_a_descriptor_may_be_registered() -> None:
    with pytest.raises(ProviderRegistryError):
        ProviderRegistry().register({"provider_id": "a.b"})  # type: ignore[arg-type]


def test_resolution_returns_the_highest_satisfying_version() -> None:
    registry = ProviderRegistry()
    registry.register(_descriptor("fixture.memo", "1.0.0"))
    registry.register(_descriptor("fixture.memo", "1.4.0"))
    registry.register(_descriptor("fixture.memo", "2.0.0"))
    assert registry.resolve("fixture.memo").version == "2.0.0"
    assert registry.resolve("fixture.memo", "1.0.0").version == "2.0.0"
    assert registry.versions("fixture.memo") == ("1.0.0", "1.4.0", "2.0.0")
    assert registry.get("fixture.memo", "1.4.0").version == "1.4.0"


def test_resolution_fails_closed() -> None:
    registry = ProviderRegistry()
    registry.register(memo_descriptor())
    with pytest.raises(ProviderRegistryError):
        registry.resolve("absent.provider")
    with pytest.raises(ProviderRegistryError) as exc:
        registry.resolve("fixture.memo", "9.0.0")
    assert exc.value.detail["registered"] == ("1.0.0",)
    with pytest.raises(ProviderRegistryError):
        registry.get("fixture.memo", "9.9.9")


def test_a_version_older_than_the_major_line_head_is_refused() -> None:
    registry = ProviderRegistry()
    registry.register(_descriptor("fixture.memo", "1.4.0"))
    with pytest.raises(ProviderRegistryError) as exc:
        registry.register(_descriptor("fixture.memo", "1.2.0"))
    assert exc.value.detail["registered_head"] == "1.4.0"


def test_evolution_within_a_major_line_must_be_additive() -> None:
    registry = ProviderRegistry()
    registry.register(_descriptor("fixture.memo", "1.0.0"))
    extended = _descriptor(
        "fixture.memo",
        "1.1.0",
        capabilities=(
            *memo_capabilities(),
            declare_capability(
                "memo.extra", "query", resource_kind=MEMO_RESOURCE_KIND, selector_keys=("x",)
            ),
        ),
    )
    assert registry.register(extended).version == "1.1.0"
    narrowed = _descriptor("fixture.memo", "1.2.0", capabilities=memo_capabilities()[:1])
    with pytest.raises(ProviderRegistryError) as exc:
        registry.register(narrowed)
    assert "memo.attestation" in exc.value.detail["removed"]


def test_a_new_major_version_may_narrow_freely() -> None:
    registry = ProviderRegistry()
    registry.register(_descriptor("fixture.memo", "1.0.0"))
    assert (
        registry.register(
            _descriptor("fixture.memo", "2.0.0", capabilities=memo_capabilities()[:1])
        ).version
        == "2.0.0"
    )


def test_kind_may_not_change_within_a_major_line() -> None:
    registry = ProviderRegistry()
    registry.register(_descriptor("fixture.memo", "1.0.0"))
    with pytest.raises(ProviderRegistryError) as exc:
        registry.register(_descriptor("fixture.memo", "1.1.0", kind="other"))
    assert exc.value.detail["offered_kind"] == "other"


def test_enumeration_is_deterministic_and_kind_filtering_is_data_driven() -> None:
    registry = ProviderRegistry()
    registry.register(_descriptor("z.provider", "1.0.0", kind="zeta"))
    registry.register(_descriptor("a.provider", "1.0.0", kind="alpha"))
    registry.register(_descriptor("a.provider", "1.1.0", kind="alpha"))
    assert [r.qualified_id for r in registry.registrations()] == [
        "a.provider@1.0.0",
        "a.provider@1.1.0",
        "z.provider@1.0.0",
    ]
    assert registry.kinds() == ("alpha", "zeta")
    assert registry.provider_ids() == ("a.provider", "z.provider")
    assert [r.qualified_id for r in registry.registrations(kind="alpha")] == [
        "a.provider@1.0.0",
        "a.provider@1.1.0",
    ]
    assert [r.qualified_id for r in registry.heads()] == [
        "a.provider@1.1.0",
        "z.provider@1.0.0",
    ]


def test_resolution_order_is_dependency_first() -> None:
    registry = ProviderRegistry()
    registry.register(_descriptor("base.provider"))
    registry.register(
        _descriptor("mid.provider", dependencies=(declare_dependency("base.provider"),))
    )
    registry.register(
        _descriptor("top.provider", dependencies=(declare_dependency("mid.provider"),))
    )
    order = [record.provider_id for record in registry.resolution_order("top.provider")]
    assert order == ["base.provider", "mid.provider", "top.provider"]
    assert [r.provider_id for r in registry.resolution_order("base.provider")] == ["base.provider"]


def test_resolution_order_refuses_a_cycle() -> None:
    registry = ProviderRegistry()
    registry.register(_descriptor("a.one", dependencies=(declare_dependency("a.two"),)))
    registry.register(_descriptor("a.two", dependencies=(declare_dependency("a.one"),)))
    with pytest.raises(ProviderRegistryError) as exc:
        registry.resolution_order("a.one")
    assert "PC-12" in exc.value.message
    assert exc.value.detail["cycle"][0] == "a.one"


def test_a_missing_required_dependency_is_fatal_but_an_optional_one_is_not() -> None:
    registry = ProviderRegistry()
    registry.register(
        _descriptor("needs.required", dependencies=(declare_dependency("gone.away"),))
    )
    with pytest.raises(ProviderRegistryError):
        registry.resolution_order("needs.required")
    registry.register(
        _descriptor(
            "needs.optional", dependencies=(declare_dependency("gone.away", optional=True),)
        )
    )
    assert [r.provider_id for r in registry.resolution_order("needs.optional")] == [
        "needs.optional"
    ]


def test_a_diamond_dependency_is_visited_once() -> None:
    registry = ProviderRegistry()
    registry.register(_descriptor("d.base"))
    registry.register(_descriptor("d.left", dependencies=(declare_dependency("d.base"),)))
    registry.register(_descriptor("d.right", dependencies=(declare_dependency("d.base"),)))
    registry.register(
        _descriptor(
            "d.top",
            dependencies=(declare_dependency("d.left"), declare_dependency("d.right")),
        )
    )
    order = [record.provider_id for record in registry.resolution_order("d.top")]
    assert order.count("d.base") == 1
    assert order.index("d.base") < order.index("d.top")


def test_registry_projection_is_reproducible() -> None:
    first = ProviderRegistry.from_descriptors([memo_descriptor()])
    second = ProviderRegistry.from_descriptors([memo_descriptor()])
    assert first.registry_hash() == second.registry_hash()
    assert first.to_dict()["count"] == 1


def test_registry_builds_from_plain_payloads() -> None:
    registry = ProviderRegistry.from_payloads([memo_descriptor().to_dict()])
    assert registry.resolve("fixture.memo").version == "1.0.0"


def test_register_all_preserves_order() -> None:
    registry = ProviderRegistry()
    records = registry.register_all([_descriptor("first.provider"), _descriptor("second.provider")])
    assert [record.sequence for record in records] == [1, 2]


def test_a_provider_declaring_no_capabilities_is_still_registrable() -> None:
    """Registration validates registrability, not conformance — that is validation's job."""
    registry = ProviderRegistry()
    bare = declare_provider("bare.provider", "memo", "1.0.0")
    assert registry.register(bare).qualified_id == "bare.provider@1.0.0"


def test_heads_keeps_the_highest_version_whichever_order_the_records_arrive_in() -> None:
    """THE HEAD IS THE HIGHEST VERSION, NOT THE LAST ONE SEEN.

    ``heads`` walks the record map and keeps the greater version per provider id, so both
    arms of that comparison have to run: the first record for an id (nothing to compare
    with) and a later one that is LOWER than what is already held. Registering ascending
    only ever takes the first arm, which is why the "keep what I have" arm was dead — and it
    is the one that stops a stale version from becoming the head by being registered second.
    """
    registry = ProviderRegistry()
    registry.register(memo_descriptor(version="2.0.0"))
    registry.register(memo_descriptor(version="1.0.0"))
    registry.register(memo_descriptor(version="1.5.0"))

    heads = registry.heads()
    assert len(heads) == 1
    assert heads[0].version == "2.0.0"
