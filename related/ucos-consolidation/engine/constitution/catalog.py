"""UCOS-CEL-0001 Part 03 — the constitutional execution system, declared as itself.

Every engine in this package is an executable artifact, and CEL-09 does not exempt the
engines that enforce CEL-09. This module is the population in which they declare
themselves: twelve subjects, each carrying the fifteen mandated facets, each owned,
authorised, certified and registered by something that is not itself.

It is a seed, not a second registry
-----------------------------------
The subjects here are *declarations*, in the same sense as
:mod:`engine.nucleus.catalog`'s seed nuclei. They mint no identifiers of their own —
:func:`engine.registry.universal.identity.deterministic_id` does that — and they own no
capability, because ownership terminates externally at the nucleus that owns this domain.

Why the system declaring itself is not self-certification
---------------------------------------------------------
CEL-05 forbids a subject certifying *itself*, not a population containing its own
certifier. The certification relation here is a chain: each engine is certified by the
enforcement layer, the enforcement layer by the law, and the law by the founding
determination — which is external, and so terminates the regress without closing it. Run
``ucos-cel acceptance`` and the gate measures that chain rather than taking this
docstring's word for it.

The honest limit of this
------------------------
This population declares what the engines *are*, and the gate proves the declaration is
constitutionally coherent. It does not prove the Python behaves as declared; that is what
the tests under ``engine/tests/constitution`` are for. A declaration that passed the gate
while the code did the opposite would be a lie the gate cannot catch, so neither substitute
for the other.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from engine.constitution import (
    acceptance as enforcement_layer,
)
from engine.constitution import (
    assimilation as assimilation_gate,
)
from engine.constitution import (
    authority as authority_graph,
)
from engine.constitution import (
    dependency as dependency_graph,
)
from engine.constitution import (
    evolution as evolution_engine,
)
from engine.constitution import (
    gateway as mutation_gateway,
)
from engine.constitution import (
    law,
    metadata,
)
from engine.constitution import (
    legality as legality_engine,
)
from engine.constitution import (
    planner as execution_planner,
)
from engine.constitution import (
    replay as replay_engine,
)
from engine.constitution import (
    state as state_engine,
)
from engine.registry.universal.identity import RegistryKind, deterministic_id
from engine.uckp.canonical import content_hash

#: The namespace every subject in this catalogue is identified under.
NAMESPACE = "constitution"

#: The founding determination. External by construction: it is what the repository is
#: measured *against*, so nothing inside the repository certifies it.
DETERMINATION = "ext:P0-AUTONOMOUS-CONSTITUTIONAL-EXECUTION-001"

#: The nucleus that owns this capability domain. External to this population because
#: nuclei are registered in :mod:`engine.nucleus.registry`, which is their one authority —
#: declaring one here would be a second nucleus truth.
OWNER = "ext:UCOS-NUC-CONSTITUTION"

#: The registry every subject registers in.
REGISTRY = "ext:UCOS-UNIVERSAL-REGISTRY"

#: The subject that certifies the certifier of last resort, and the two rules every
#: subject is validated and verified against. All external: the regress has to end.
_RATIFIER = DETERMINATION
_VALIDATION = "ext:UCOS-CEP-004-CONSTITUTIONAL-VALIDATION-CONSTITUTION"
_VERIFICATION = "ext:UCOS-CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION"
_GOVERNANCE = "ext:UCOS-CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION"
_REPLAY = "ext:UCOS-DETERMINISM-REPRODUCIBILITY"
_EVOLUTION = "ext:UCOS-CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION"
_LINEAGE = "ext:UCOS-UNIVERSAL-LINEAGE"
_TRACEABILITY = "ext:UCOS-CEP-008-CONSTITUTIONAL-EVIDENCE-TRACEABILITY-CONSTITUTION"


@dataclass(frozen=True, slots=True)
class Declaration:
    """One engine of this package, as it declares itself.

    Only the facets that differ between engines are held here. The eight that are the same
    for every engine in a single package — governance, replay, evolution, lineage and
    traceability rules, the registry, the owner — are supplied by :func:`_declare`, because
    repeating them twelve times would invite twelve chances for one to drift.
    """

    subject: str
    engine_id: str
    statement: str
    depends_on: tuple[str, ...]
    certified_by: str
    outputs: tuple[str, ...]
    inputs: tuple[str, ...]
    constraints: tuple[str, ...]


#: The twelve engines (DATA — a thirteenth is one appended entry).
DECLARATIONS: tuple[Declaration, ...] = (
    Declaration(
        subject="constitution.law",
        engine_id=law.LAW_ID,
        statement="the clauses, invariants and acceptance criteria of constitutional execution",
        depends_on=(),
        certified_by=_RATIFIER,
        outputs=("constitutional-execution-law",),
        inputs=(DETERMINATION,),
        constraints=("clauses are data", "extension is by appending, never by editing"),
    ),
    Declaration(
        subject="constitution.metadata",
        engine_id=metadata.MANDATE_ID,
        statement="the fifteen facets an executable artifact must declare",
        depends_on=("constitution.law",),
        certified_by="constitution.acceptance",
        outputs=("constitutional-metadata-mandate", "constitutional-population"),
        inputs=("constitutional-execution-law",),
        constraints=("no facet is optional", "an unknown facet name is refused, never ignored"),
    ),
    Declaration(
        subject="constitution.dependency",
        engine_id=dependency_graph.GRAPH_ID,
        statement="the universal constitutional dependency graph",
        depends_on=("constitution.metadata",),
        certified_by="constitution.acceptance",
        outputs=("constitutional-dependency-graph",),
        inputs=("constitutional-population",),
        constraints=(
            "order is never derived here",
            "an unresolved edge is refused, never projected",
        ),
    ),
    Declaration(
        subject="constitution.authority",
        engine_id=authority_graph.AUTHORITY_GRAPH_ID,
        statement="the constitutional authority graph and its circularity detection",
        depends_on=("constitution.dependency",),
        certified_by="constitution.acceptance",
        outputs=("constitutional-authority-report",),
        inputs=("constitutional-dependency-graph", "constitutional-population"),
        constraints=("no subject attests to itself", "a cycle is refused, never broken"),
    ),
    Declaration(
        subject="constitution.legality",
        engine_id=legality_engine.LEGALITY_ENGINE_ID,
        statement="the nine proofs every execution request must discharge",
        depends_on=("constitution.authority",),
        certified_by="constitution.acceptance",
        outputs=("constitutional-legality-report",),
        inputs=("constitutional-dependency-graph", "constitutional-population"),
        constraints=("there is no partial legality", "an unevaluable proof is an unproven proof"),
    ),
    Declaration(
        subject="constitution.planner",
        engine_id=execution_planner.PLANNER_ID,
        statement="the derived, topologically ordered execution plan",
        depends_on=("constitution.legality",),
        certified_by="constitution.acceptance",
        outputs=("constitutional-execution-plan",),
        inputs=("constitutional-legality-report", "constitutional-authority-report"),
        constraints=(
            "no caller may supply an order",
            "ordering is delegated to the single ordering authority",
        ),
    ),
    Declaration(
        subject="constitution.state",
        engine_id=state_engine.ENGINE_ID,
        statement="the dirty state prevention engine and its seals",
        depends_on=("constitution.metadata",),
        certified_by="constitution.acceptance",
        outputs=("constitutional-state-seal",),
        inputs=("constitutional-population",),
        constraints=("no clock is read", "freshness is digest equality, never wall-clock order"),
    ),
    Declaration(
        subject="constitution.replay",
        engine_id=replay_engine.REPLAY_ENGINE_ID,
        statement="the autonomous replay engine and its fixed point",
        depends_on=("constitution.planner",),
        certified_by="constitution.acceptance",
        outputs=("constitutional-replay-record",),
        inputs=("constitutional-population",),
        constraints=("convergence is bounded", "divergence is a defect, never a retry"),
    ),
    Declaration(
        subject="constitution.assimilation",
        engine_id=assimilation_gate.GATE_ID,
        statement="the repository truth assimilation gate: reuse before create",
        depends_on=("constitution.metadata",),
        certified_by="constitution.acceptance",
        outputs=("constitutional-assimilation-verdict",),
        inputs=("constitutional-population",),
        constraints=("creation requires four empty searches", "a hit refuses, it does not warn"),
    ),
    Declaration(
        subject="constitution.gateway",
        engine_id=mutation_gateway.GATEWAY_ID,
        statement="the constitutional mutation gateway: the only path to a committed state",
        depends_on=(
            "constitution.assimilation",
            "constitution.replay",
            "constitution.state",
        ),
        certified_by="constitution.acceptance",
        outputs=("constitutional-mutation-record", "committed-population"),
        inputs=("constitutional-population", "constitutional-state-seal"),
        constraints=(
            "every stage discharges or the mutation does not apply",
            "it is the only producer of a clean state seal",
        ),
    ),
    Declaration(
        subject="constitution.acceptance",
        engine_id=enforcement_layer.ENFORCEMENT_ID,
        statement="the enforcement layer: every invariant measured, every criterion resolved",
        depends_on=("constitution.planner",),
        certified_by="constitution.law",
        outputs=("constitutional-acceptance-report",),
        inputs=("constitutional-population", "constitutional-execution-law"),
        constraints=(
            "an invariant with no measurement is reported unmeasured and blocking",
            "every criterion resolves through an invariant, never through a judgement",
        ),
    ),
    Declaration(
        subject="constitution.evolution",
        engine_id=evolution_engine.ENGINE_ID,
        statement="the autonomous constitutional evolution cycle",
        depends_on=("constitution.gateway", "constitution.acceptance"),
        certified_by="constitution.acceptance",
        outputs=("constitutional-cycle-record",),
        inputs=("constitutional-population", "constitutional-acceptance-report"),
        constraints=(
            "it composes UCL-000001 rather than copying it",
            "elevation is measured, never asserted",
        ),
    ),
)


def _declare(declaration: Declaration) -> metadata.ConstitutionalMetadata:
    """Turn one engine's declaration into its complete constitutional metadata."""
    return metadata.ConstitutionalMetadata.declare(
        declaration.subject,
        universal_id=deterministic_id(
            RegistryKind.ENGINE, NAMESPACE, declaration.subject.replace(".", "-")
        ),
        canonical_owner=OWNER,
        authorities=(DETERMINATION, *declaration.depends_on),
        dependencies=declaration.depends_on or (DETERMINATION,),
        constraints=declaration.constraints,
        inputs=declaration.inputs,
        outputs=declaration.outputs,
        registrations=(REGISTRY,),
        certifications=(declaration.certified_by,),
        validation_rules=(_VALIDATION,),
        verification_rules=(_VERIFICATION,),
        replay_rules=(_REPLAY,),
        governance_rules=(_GOVERNANCE,),
        evolution_rules=(_EVOLUTION,),
        lineage_rules=(_LINEAGE,),
        traceability_rules=(_TRACEABILITY, DETERMINATION),
    )


def build_population(
    declarations: Sequence[Declaration] = DECLARATIONS,
) -> metadata.Population:
    """The constitutional execution system as a population of declared subjects."""
    return metadata.Population.of(_declare(declaration) for declaration in declarations)


def engine_index() -> dict[str, str]:
    """``subject → engine identifier`` for every declared engine."""
    return {d.subject: d.engine_id for d in DECLARATIONS}


def to_document() -> dict[str, Any]:
    """The catalogue as a deterministic, machine-readable document."""
    population = build_population()
    return {
        "schema": "ucos-constitutional-engine-catalogue",
        "version": metadata.MANDATE_VERSION,
        "namespace": NAMESPACE,
        "determination": DETERMINATION,
        "owner": OWNER,
        "engine_count": len(DECLARATIONS),
        "engines": [
            {
                "subject": d.subject,
                "engine_id": d.engine_id,
                "statement": d.statement,
                "depends_on": list(d.depends_on),
                "certified_by": d.certified_by,
            }
            for d in DECLARATIONS
        ],
        "population_digest": population.digest(),
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "DECLARATIONS",
    "DETERMINATION",
    "NAMESPACE",
    "OWNER",
    "REGISTRY",
    "Declaration",
    "build_population",
    "digest",
    "engine_index",
    "to_document",
]
