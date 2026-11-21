"""UAUE — Universal Autonomous Evolution engine (UAUE-000001).

This package is the machine reader of the canonical evolution declaration at
``00-MASTER/UAUE-000001/uaue-evolution.json`` and nothing else. It legislates no stage,
mints no identity, registers no object and issues no certificate: every one of those has a
located owner elsewhere in the repository, and the declaration binds each phase of the
perpetual evolution cycle to that owner by pointer.

The package deliberately carries **no list of registers, phases, stages or classification
rules**. Registers, phases and classifications are read from the declaration; the stage set
is read from :mod:`engine.uckp.evolution`, the Article 14 authority that owns it. A second
copy of any of those here would be a second authority over one subject, which is the exact
failure this programme exists to measure.

The traversal itself is :mod:`engine.uaue.controller`, which conducts a candidate through every
declared position and settles the interdependence between completeness, validation and
certification to a fixed point. It is exported here because a capability reachable only through a
private module path is a capability nothing can discover.

Layering: this package may import from :mod:`engine` only. It never imports ``platform`` or
``intelligence``, and it never imports a ``00-MASTER`` programme engine — those are
stdlib-only scripts whose import would execute a measurement as a side effect.
"""

from __future__ import annotations

from engine.uaue.authority import load_evolution_authority
from engine.uaue.controller import (
    EvolutionContext,
    EvolutionController,
    EvolutionRefused,
    EvolutionRun,
    EvolutionSettlement,
    StageResult,
    resolve_evolution_state,
)
from engine.uaue.model import (
    Classification,
    Dependency,
    EvolutionAuthority,
    EvolutionAuthorityError,
    Gate,
    LifecycleState,
    ObjectKind,
    Owner,
    Ownership,
    Phase,
    Register,
    RequiredField,
)

__all__ = [
    "Classification",
    "Dependency",
    "EvolutionAuthority",
    "EvolutionAuthorityError",
    "EvolutionContext",
    "EvolutionController",
    "EvolutionRefused",
    "EvolutionRun",
    "EvolutionSettlement",
    "Gate",
    "LifecycleState",
    "ObjectKind",
    "Owner",
    "Ownership",
    "Phase",
    "Register",
    "RequiredField",
    "StageResult",
    "load_evolution_authority",
    "resolve_evolution_state",
]
