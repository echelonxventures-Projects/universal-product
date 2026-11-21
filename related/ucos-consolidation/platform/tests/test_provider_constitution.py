"""Provider Constitution tests (Terminal-04).

The constitution is the law, so these tests assert the two properties that make it
universal: the operation surface is closed, and the *kind* vocabulary is not.
"""

from __future__ import annotations

from platform.universal_provider.constitution import (
    CONSTITUTIONAL_GATES,
    CONSTITUTIONAL_OPERATIONS,
    INTRINSIC_OPERATIONS,
    PROVIDER_ARTICLES,
    SUBSTRATE_OPERATIONS,
    ProviderArticle,
    ProviderOperation,
    article,
    normalize_kind,
    normalize_provider_id,
    provider_constitution,
    require_operations,
    require_semver,
    version_tuple,
)
from platform.universal_provider.errors import ProviderConstitutionError

import pytest


def test_constitution_has_fourteen_articles_each_with_a_distinct_gate() -> None:
    assert len(PROVIDER_ARTICLES) == 14
    assert len(set(CONSTITUTIONAL_GATES)) == 14
    assert len({a.article_id for a in PROVIDER_ARTICLES}) == 14


def test_operation_surface_is_closed_and_partitioned() -> None:
    assert len(CONSTITUTIONAL_OPERATIONS) == 6
    assert set(CONSTITUTIONAL_OPERATIONS) == set(ProviderOperation)
    assert set(INTRINSIC_OPERATIONS) | set(SUBSTRATE_OPERATIONS) == set(ProviderOperation)
    assert not set(INTRINSIC_OPERATIONS) & set(SUBSTRATE_OPERATIONS)


def test_require_operations_refuses_both_missing_and_extra_operations() -> None:
    assert require_operations(op.value for op in ProviderOperation) == CONSTITUTIONAL_OPERATIONS
    with pytest.raises(ProviderConstitutionError) as missing:
        require_operations(["describe", "query"])
    assert "verify" in missing.value.detail["missing"]
    with pytest.raises(ProviderConstitutionError) as extra:
        require_operations([*(op.value for op in ProviderOperation), "mutate"])
    assert extra.value.detail["extra"] == ["mutate"]


@pytest.mark.parametrize(
    "kind",
    [
        "repository",
        "documentation",
        "patent",
        "marketplace",
        "quantum-substrate",
        "kind.not.yet.imagined",
    ],
)
def test_kind_vocabulary_is_open(kind: str) -> None:
    """Any well-formed slug is a valid kind, including ones invented later (PC-02)."""
    assert normalize_kind(kind) == kind


@pytest.mark.parametrize("kind", ["", "has space", "-leading", "9numeric", "under_score", 42])
def test_kind_form_is_still_enforced(kind: object) -> None:
    with pytest.raises(ProviderConstitutionError):
        normalize_kind(kind)  # type: ignore[arg-type]


def test_kind_and_provider_id_are_normalized() -> None:
    assert normalize_kind("  Repository  ") == "repository"
    assert normalize_provider_id("  UCOS.Repository ") == "ucos.repository"
    with pytest.raises(ProviderConstitutionError):
        normalize_provider_id("not a slug")
    with pytest.raises(ProviderConstitutionError):
        normalize_provider_id(None)  # type: ignore[arg-type]


@pytest.mark.parametrize("version", ["1.0.0", "0.0.1", "10.20.30"])
def test_semver_accepted(version: str) -> None:
    assert require_semver(version) == version


@pytest.mark.parametrize("version", ["1.0", "1.0.0-rc1", "01.0.0", "", None])
def test_semver_refused(version: object) -> None:
    with pytest.raises(ProviderConstitutionError):
        require_semver(version)  # type: ignore[arg-type]


def test_version_tuple_orders_numerically_not_lexically() -> None:
    assert version_tuple("2.0.0") > version_tuple("10.0.0".replace("10", "1"))
    assert sorted(["1.10.0", "1.9.0"], key=version_tuple) == ["1.9.0", "1.10.0"]


def test_article_lookup_fails_closed_on_unknown_id() -> None:
    assert article("PC-01").gate == "PV-01-INTERFACE-COMPLETE"
    with pytest.raises(ProviderConstitutionError) as exc:
        article("PC-99")
    assert "PC-01" in exc.value.detail["known"]


def test_article_requires_every_field() -> None:
    with pytest.raises(ProviderConstitutionError):
        ProviderArticle(article_id="PC-X", title="", mandate="m", gate="g")


def test_constitution_projection_is_content_addressable_and_complete() -> None:
    constitution = provider_constitution()
    payload = constitution.to_dict()
    assert payload["operations"] == [op.value for op in CONSTITUTIONAL_OPERATIONS]
    assert len(payload["articles"]) == 14
    assert constitution.article_ids()[0] == "PC-01"
    assert constitution.gates() == CONSTITUTIONAL_GATES
    assert provider_constitution().to_dict() == payload
