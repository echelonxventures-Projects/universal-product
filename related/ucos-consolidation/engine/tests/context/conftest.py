"""Shared fixtures for the Universal Context Intelligence tests (UCXI-000001).

Every fixture builds its context set in memory from the declared catalog or from
purpose-built declarations; nothing reads or writes the certified corpus (DP-03).
"""

from __future__ import annotations

from typing import Any

import pytest

from engine.context.catalog import bootstrap_registry
from engine.context.composition import compose
from engine.context.model import ContextDeclaration, values_from_mapping
from engine.context.ontology import DimensionSpec
from engine.context.registry import ContextRegistry
from engine.context.taxonomy import ContextAuthority, ContextKind, ContextTaxon


@pytest.fixture
def empty_registry() -> ContextRegistry:
    """A registry with the universal taxonomy/ontology and no registered context."""
    return ContextRegistry()


@pytest.fixture
def universal_registry() -> ContextRegistry:
    """A registry bootstrapped with the fifteen universal contexts."""
    return bootstrap_registry()


@pytest.fixture
def composed(universal_registry: ContextRegistry) -> Any:
    """The bounded composition over the fifteen universal contexts."""
    return compose(universal_registry)


def declaration(
    *,
    kind: ContextKind | str = ContextKind.TEMPORAL,
    namespace: str = "ucos.test",
    natural_key: str = "subject",
    values: dict[str, Any] | None = None,
    authority: ContextAuthority = ContextAuthority.OPERATIONAL,
    boundary: str = "test-frame",
    parent: str | None = None,
    source: str = "engine/tests/context/conftest.py",
) -> ContextDeclaration:
    """Build a conformant declaration, defaulting to a valid temporal context."""
    kind_value = kind.value if isinstance(kind, ContextKind) else kind
    payload = (
        values
        if values is not None
        else {
            "reference_frame": "test clock",
            "ordering": "sequence",
            "resolution": "one step",
        }
    )
    return ContextDeclaration(
        kind=kind_value,
        namespace=namespace,
        natural_key=natural_key,
        values=values_from_mapping(payload, authority=authority, source=source),
        authority=authority,
        boundary=boundary,
        parent=parent,
    )


def spatial_values() -> dict[str, Any]:
    return {
        "reference_frame": "test grid",
        "extent": "one cell",
        "locality": "adjacent",
    }


def future_taxon(taxon_id: str = "CTX-QUANTUM", kind: str = "quantum") -> ContextTaxon:
    """A future (non-universal) taxon used to prove the taxonomy is open."""
    return ContextTaxon(
        taxon_id=taxon_id,
        kind=kind,
        title="Quantum Context",
        parent="CTX-ROOT",
        description="A context type this release has never seen.",
    )


def future_dimensions() -> tuple[DimensionSpec, ...]:
    return (
        DimensionSpec(
            name="basis", value_type="string", required=True, description="Measurement basis."
        ),
        DimensionSpec(
            name="entangled", value_type="boolean", required=False, description="Entangled?"
        ),
    )
