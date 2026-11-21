"""Shared fixtures for the constitutional execution system's tests.

:func:`declare` exists so a test that cares about *one* facet does not have to restate the
other fourteen. Every facet defaults to something lawful, so a test reads as the single
deviation it is testing — ``declare("x", certifications=("x",))`` is visibly a
self-certification test and nothing else.
"""

from __future__ import annotations

from typing import Any

import pytest

from engine.constitution import catalog, metadata
from engine.registry.universal.identity import RegistryKind, deterministic_id

#: A lawful default for every graph-bearing facet: external, so it terminates rather than
#: dangling, and so a test that does not name a relation contributes no edges to it.
LAWFUL_DEFAULTS: dict[str, Any] = {
    "canonical_owner": ("ext:UCOS-NUC-TEST",),
    "authorities": ("ext:UCOS-DETERMINATION-TEST",),
    "dependencies": ("ext:UCOS-DETERMINATION-TEST",),
    "constraints": ("deterministic",),
    "inputs": ("test-input",),
    "outputs": ("test-output",),
    "registrations": ("ext:UCOS-REGISTRY-TEST",),
    "certifications": ("ext:UCOS-CERTIFIER-TEST",),
    "validation_rules": ("ext:UCOS-VALIDATION-TEST",),
    "verification_rules": ("ext:UCOS-VERIFICATION-TEST",),
    "replay_rules": ("ext:UCOS-REPLAY-TEST",),
    "governance_rules": ("ext:UCOS-GOVERNANCE-TEST",),
    "evolution_rules": ("ext:UCOS-EVOLUTION-TEST",),
    "lineage_rules": ("ext:UCOS-LINEAGE-TEST",),
    "traceability_rules": ("ext:UCOS-TRACE-TEST",),
}


def declare(subject: str, **overrides: Any) -> metadata.ConstitutionalMetadata:
    """A complete, lawful declaration for ``subject``, with ``overrides`` applied.

    ``outputs`` defaults to a value derived from the subject so two declarations never
    collide as duplicate capabilities by accident — a test that wants that collision asks
    for it explicitly.
    """
    facets = dict(LAWFUL_DEFAULTS)
    facets["outputs"] = (f"{subject}-output",)
    facets.update(overrides)
    return metadata.ConstitutionalMetadata.declare(
        subject,
        universal_id=deterministic_id(
            RegistryKind.ENGINE, "test", subject.replace(".", "-").replace("_", "-")
        ),
        **facets,
    )


def population(*records: metadata.ConstitutionalMetadata) -> metadata.Population:
    """A population of the given declarations."""
    return metadata.Population.of(records)


@pytest.fixture
def lawful() -> metadata.Population:
    """A three-subject population that satisfies every clause of the law."""
    return population(
        declare("root"),
        declare("middle", dependencies=("root",), certifications=("root",)),
        declare("leaf", dependencies=("middle",), certifications=("root",)),
    )


@pytest.fixture
def system() -> metadata.Population:
    """The constitutional execution system, declared as itself."""
    return catalog.build_population()
