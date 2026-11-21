"""UCOS-UICM-000001 — Universal Implementation Closure Matrix.

**Measurement and certification layer only.** This package answers one question that
nothing in the repository could answer before it: *is capability X closed on dimension Y?*
It owns no registry, mints no identifier, legislates no lifecycle and issues no
certificate.

Three capabilities were located as genuinely absent and are created here. Everything else
UICM needs was already owned, and is consumed rather than rebuilt:

    created
      capability x dimension closure matrix     engine.uicm.matrix
      capability-keyed obligation register      engine.uicm.obligation
      closure state machine                    engine.uicm.model

    consumed (read, never written)
      capability identity     knowledge/canonical-knowledge.json      UCKO-CAP-*
      artifact identity       00-MASTER/UCOS-UGA-001                  UCOS-* universal_id
      implementation mapping  intelligence/UCOS-RIE-CAPABILITY-CATALOG.json

    invoked (verdict belongs to the owner)
      certification           engine.universal_certification          UCOS-EPIC-006
      lifecycle stages        UCIC-001                                bound, never forked
      canonical digest        engine.uckp.canonical                   the single primitive
      disclosure              engine.foundation.contracts.disclosure

Every register here is **append-only and immutable**. A closure state is never edited: a
change of state is a new observation appended with explicit lineage to the observation it
supersedes, and the record it replaced stays exactly as it was, reported thereafter as
``SUPERSEDED``. There is no update path and no delete path anywhere in the package, and
that absence is *measured* over this package's own source (UICM-INV-16) rather than
asserted, because an append-only register whose immutability is only a convention is one
edit away from not being one.

The declaration at ``00-MASTER/UCOS-UICM-000001/uicm.json`` owns every enumeration: the
seven states, the seventeen dimensions, the population rule, the source paths, the gap
classes and the eighteen invariants. No dimension id, capability name or source path is an
executable literal in this package, and UICM-INV-15 measures that too. Admitting a
dimension or a capability is an append-only edit to declared data and requires no change
here.

Imports are lazy so that reading the closure model costs nothing at import time. Note in
particular that ``intelligence`` is never imported: that package depends on ``engine``, so
its catalogue is consumed as JSON, which is what a reference into another owner's register
should be.
"""

from __future__ import annotations

from typing import Any

__version__ = "1.0.0"

#: The programme this package realizes.
PROGRAMME_ID = "UCOS-UICM-000001"

#: Public name -> owning module, resolved on first access.
_EXPORTS: dict[str, str] = {
    # closure state machine and object model
    "Capability": "engine.uicm.model",
    "ClosureCell": "engine.uicm.model",
    "ClosureDeclaration": "engine.uicm.model",
    "ClosureDeclarationError": "engine.uicm.model",
    "ClosureError": "engine.uicm.model",
    "ClosureState": "engine.uicm.model",
    "ClosureStateError": "engine.uicm.model",
    "DimensionDeclaration": "engine.uicm.model",
    "StateDeclaration": "engine.uicm.model",
    # the matrix and population assembly
    "CanonicalOwners": "engine.uicm.matrix",
    "ClosureMatrix": "engine.uicm.matrix",
    "PopulationError": "engine.uicm.matrix",
    "discover_population": "engine.uicm.matrix",
    # the capability-keyed obligation register
    "ClosureObligation": "engine.uicm.obligation",
    "ObligationRegister": "engine.uicm.obligation",
    "ObligationError": "engine.uicm.obligation",
    # the observation registry
    "Observation": "engine.uicm.observation",
    "ObservationRegistry": "engine.uicm.observation",
    "ObservationError": "engine.uicm.observation",
    # measurement
    "ProbeResult": "engine.uicm.measurement",
    "RepositoryFacts": "engine.uicm.measurement",
    "measure": "engine.uicm.measurement",
    "probe_names": "engine.uicm.measurement",
    # the gap register
    "Gap": "engine.uicm.gap",
    "GapRegister": "engine.uicm.gap",
    "GapError": "engine.uicm.gap",
    # the validation engine
    "ClosureValidation": "engine.uicm.validation",
    "InvariantResult": "engine.uicm.validation",
    "validate": "engine.uicm.validation",
    # the certification projection
    "ClosureCertification": "engine.uicm.certification",
    "project_certification": "engine.uicm.certification",
    # the lifecycle controller
    "CLOSURE_CONTRACT": "engine.uicm.controller",
    "ClosureRun": "engine.uicm.controller",
    "UicmController": "engine.uicm.controller",
}


def __getattr__(name: str) -> Any:
    """Resolve a public name to its owning module on first access."""
    module_path = _EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    return getattr(import_module(module_path), name)


def __dir__() -> list[str]:
    return sorted([*_EXPORTS, "PROGRAMME_ID", "__version__"])


__all__ = ["PROGRAMME_ID", *sorted(_EXPORTS)]
