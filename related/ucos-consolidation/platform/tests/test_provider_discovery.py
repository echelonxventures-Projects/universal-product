"""Provider Discovery tests (Terminal-04).

Discovery is where "no hardcoded providers" is cashed out: a provider exists because
a manifest says so. These tests onboard a provider the framework has never heard of
using only a JSON file, and then attack every malformed-manifest path.
"""

from __future__ import annotations

import json
from pathlib import Path
from platform.tests.universal_provider_helpers import (
    MEMO_ENTRY_POINT,
    MemoProvider,
    memo_descriptor,
    memo_manifest,
    write_manifest,
)
from platform.universal_provider.discovery import (
    MANIFEST_PROVIDERS_KEY,
    CatalogSource,
    DeclarationSource,
    DiscoveredProvider,
    DiscoveryResult,
    ProviderDiscovery,
    RegistrySource,
    resolve_entry_point,
)
from platform.universal_provider.errors import (
    ProviderCapabilityError,
    ProviderDiscoveryError,
)
from platform.universal_provider.registry import ProviderRegistry

import pytest


def test_a_provider_is_discovered_from_a_json_manifest_alone(tmp_path: Path) -> None:
    write_manifest(tmp_path, "memo.json", memo_manifest())
    result = ProviderDiscovery([CatalogSource(tmp_path)]).discover()
    assert len(result) == 1
    assert result.provider_ids() == ("fixture.memo",)
    assert result.kinds() == ("memo",)
    assert result.discovered[0].origin == "memo.json"
    assert result.discovered[0].resolvable is True


def test_a_manifest_may_declare_several_providers(tmp_path: Path) -> None:
    write_manifest(
        tmp_path,
        "many.json",
        {
            MANIFEST_PROVIDERS_KEY: [
                memo_manifest(),
                {
                    **memo_manifest(),
                    "identity": {**memo_manifest()["identity"], "provider_id": "fixture.other"},
                },
            ]
        },
    )
    result = ProviderDiscovery([CatalogSource(tmp_path)]).discover()
    assert result.provider_ids() == ("fixture.memo", "fixture.other")


def test_a_manifest_may_be_a_bare_list(tmp_path: Path) -> None:
    write_manifest(tmp_path, "list.json", [memo_manifest()])
    assert len(ProviderDiscovery([CatalogSource(tmp_path)]).discover()) == 1


def test_manifests_are_read_in_sorted_filename_order(tmp_path: Path) -> None:
    write_manifest(tmp_path, "b.json", memo_manifest())
    write_manifest(
        tmp_path,
        "a.json",
        {
            **memo_manifest(),
            "identity": {**memo_manifest()["identity"], "provider_id": "fixture.aaa"},
        },
    )
    source = CatalogSource(tmp_path)
    assert [item.origin for item in source.discover()] == ["a.json", "b.json"]
    assert source.directory == tmp_path
    assert source.name == "catalog"


def test_discovery_is_reproducible(tmp_path: Path) -> None:
    write_manifest(tmp_path, "memo.json", memo_manifest())
    first = ProviderDiscovery([CatalogSource(tmp_path)]).discover()
    second = ProviderDiscovery([CatalogSource(tmp_path)]).discover()
    assert first.discovery_hash() == second.discovery_hash()


def test_declared_only_providers_are_separated_from_realizable_ones(tmp_path: Path) -> None:
    write_manifest(tmp_path, "realizable.json", memo_manifest())
    write_manifest(
        tmp_path,
        "declared.json",
        {
            **memo_manifest(),
            "identity": {**memo_manifest()["identity"], "provider_id": "fixture.declared"},
            "entry_point": "",
        },
    )
    result = ProviderDiscovery([CatalogSource(tmp_path)]).discover()
    assert [item.provider_id for item in result.resolvable()] == ["fixture.memo"]
    assert [item.provider_id for item in result.declared_only()] == ["fixture.declared"]
    payload = result.to_dict()
    assert payload["resolvable"] == 1
    assert payload["declared_only"] == 1


def test_an_absent_or_non_directory_catalog_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ProviderDiscoveryError) as absent:
        CatalogSource(tmp_path / "nope").discover()
    assert "PC-07" in absent.value.message
    file_path = tmp_path / "a-file.json"
    file_path.write_text("{}", encoding="utf-8")
    with pytest.raises(ProviderDiscoveryError):
        CatalogSource(file_path).discover()


def test_a_malformed_manifest_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(ProviderDiscoveryError) as exc:
        CatalogSource(tmp_path).discover()
    assert exc.value.detail["manifest"] == "broken.json"


def test_a_manifest_declaring_an_invalid_descriptor_fails_closed(tmp_path: Path) -> None:
    write_manifest(tmp_path, "bad.json", {"identity": {"provider_id": "x.y", "kind": "memo"}})
    with pytest.raises(ProviderDiscoveryError) as exc:
        CatalogSource(tmp_path).discover()
    assert "malformed descriptor" in exc.value.message


@pytest.mark.parametrize(
    "payload",
    [
        {MANIFEST_PROVIDERS_KEY: {"not": "a list"}},
        [1, 2, 3],
        "a bare string",
        7,
    ],
)
def test_manifest_shape_is_enforced(tmp_path: Path, payload: object) -> None:
    (tmp_path / "shape.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ProviderDiscoveryError):
        CatalogSource(tmp_path).discover()


def test_declaration_and_registry_sources() -> None:
    declaration = DeclarationSource([memo_descriptor()])
    assert declaration.name == "declaration"
    assert declaration.discover()[0].origin == "in-process"
    registry = ProviderRegistry.from_descriptors([memo_descriptor()])
    found = RegistrySource(registry).discover()
    assert found[0].source == "registry"
    assert found[0].origin.startswith("registration:")


def test_a_declaration_source_holds_descriptors_only() -> None:
    with pytest.raises(ProviderDiscoveryError):
        DeclarationSource(["not a descriptor"])  # type: ignore[list-item]


def test_source_precedence_is_first_wins_and_divergence_is_reported() -> None:
    original = memo_descriptor()
    divergent = memo_descriptor(source_of_record="a different substrate")
    discovery = ProviderDiscovery(
        [DeclarationSource([original], name="first"), DeclarationSource([divergent], name="second")]
    )
    result = discovery.discover()
    assert len(result) == 1
    assert result.discovered[0].source == "first"
    assert len(result.conflicts) == 1
    assert result.conflicts[0]["accepted_source"] == "first"
    assert result.conflicts[0]["rejected_source"] == "second"


def test_an_identical_redeclaration_is_not_a_conflict() -> None:
    discovery = ProviderDiscovery(
        [
            DeclarationSource([memo_descriptor()], name="first"),
            DeclarationSource([memo_descriptor()], name="second"),
        ]
    )
    result = discovery.discover()
    assert result.conflicts == ()
    assert result.diagnostics["per_source"] == {"first": 1, "second": 1}
    assert result.sources == ("first", "second")


def test_a_source_must_be_named_and_discoverable() -> None:
    discovery = ProviderDiscovery()
    with pytest.raises(ProviderDiscoveryError):
        discovery.add_source(object())  # type: ignore[arg-type]

    class Unnamed:
        name = ""

        def discover(self) -> tuple[DiscoveredProvider, ...]:
            return ()

    with pytest.raises(ProviderDiscoveryError):
        discovery.add_source(Unnamed())  # type: ignore[arg-type]


def test_a_source_yielding_the_wrong_type_fails_closed() -> None:
    class Wrong:
        name = "wrong"

        def discover(self) -> tuple[object, ...]:
            return ("not a discovered provider",)

    with pytest.raises(ProviderDiscoveryError):
        ProviderDiscovery([Wrong()]).discover()  # type: ignore[list-item]


def test_an_empty_discovery_result_is_well_formed() -> None:
    result = DiscoveryResult()
    assert len(result) == 0
    assert result.kinds() == ()
    assert result.descriptors() == ()


def test_entry_point_resolution_yields_a_live_provider() -> None:
    instance = resolve_entry_point(memo_descriptor(), {"notes": {"only": {"tag": "t"}}})
    assert isinstance(instance, MemoProvider)
    assert instance.describe().entry_point == MEMO_ENTRY_POINT
    assert instance.fetch("only").payload == {"tag": "t"}


@pytest.mark.parametrize(
    "entry_point",
    [
        "",
        "no-colon",
        "too:many:colons",
        ":missing_module",
        "platform.tests.universal_provider_helpers:",
        "platform.tests.no_such_module:build_memo",
        "platform.tests.universal_provider_helpers:absent_attribute",
        "platform.tests.universal_provider_helpers:NOT_CALLABLE",
    ],
)
def test_entry_point_resolution_fails_closed(entry_point: str) -> None:
    with pytest.raises(ProviderDiscoveryError):
        resolve_entry_point(memo_descriptor(entry_point=entry_point))


def test_a_raising_entry_point_is_isolated_as_a_typed_error() -> None:
    descriptor = memo_descriptor(
        entry_point="platform.tests.universal_provider_helpers:exploding_factory"
    )
    with pytest.raises(ProviderDiscoveryError) as exc:
        resolve_entry_point(descriptor)
    assert "RuntimeError" in exc.value.detail["cause"]


def test_an_entry_point_raising_a_framework_error_is_surfaced_unchanged() -> None:
    """A typed constitutional refusal keeps its own code rather than being re-wrapped."""
    descriptor = memo_descriptor(
        entry_point="platform.tests.universal_provider_helpers:build_memo",
        capabilities=memo_descriptor().capabilities[:1],
    )
    with pytest.raises(ProviderCapabilityError) as exc:
        resolve_entry_point(descriptor)
    assert exc.value.code == "UPA-CAPABILITY"
    assert set(exc.value.detail["undeclared_operations"]) == {"fetch", "verify"}
