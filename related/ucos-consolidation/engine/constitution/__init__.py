"""UCOS-CEL-0001 — the Autonomous Constitutional Execution System.

The repository already *contained* constitutional rules. This package is what makes it
**enforce** them: the difference between a rule a person follows and a rule that has no
path around it.

Twelve engines, each realising one requirement of
``P0-AUTONOMOUS-CONSTITUTIONAL-EXECUTION-001``:

===========================  ==========================  ==============================
Requirement                  Identity                    Module
===========================  ==========================  ==============================
001 Dependency graph         ``UCOS-CDG-000001``         :mod:`~engine.constitution.dependency`
002 Execution planner        ``UCOS-CEP-EXEC-000001``    :mod:`~engine.constitution.planner`
003 Legality engine          ``UCOS-CLE-000001``         :mod:`~engine.constitution.legality`
004 Mutation gateway         ``UCOS-CMG-EXEC-000001``    :mod:`~engine.constitution.gateway`
005 Authority graph          ``UCOS-CAG-000001``         :mod:`~engine.constitution.authority`
006 Replay engine            ``UCOS-ARE-000001``         :mod:`~engine.constitution.replay`
007 Dirty state prevention   ``UCOS-DPE-000001``         :mod:`~engine.constitution.state`
008 Assimilation gate        ``UCOS-RTAG-000001``        :mod:`~engine.constitution.assimilation`
009 Metadata mandate         ``UCOS-CMM-000001``         :mod:`~engine.constitution.metadata`
010 Enforcement layer        ``UCOS-CEL-ENFORCE-0001``   :mod:`~engine.constitution.acceptance`
011 Evolution engine         ``UCOS-UACE-000001``        :mod:`~engine.constitution.evolution`
===========================  ==========================  ==============================

What it creates, and what it deliberately does not
--------------------------------------------------
It creates no second ordering mechanism (:mod:`engine.foundation.composition.ordering`
remains the one), no second identifier scheme
(:mod:`engine.registry.universal.identity`), no second hash primitive
(:mod:`engine.uckp.canonical`), no second ownership law (:mod:`engine.nucleus.law`) and no
second lifecycle — ``UCL-000001`` in :mod:`engine.nucleus.lifecycle` keeps its 45 stages,
and :func:`engine.constitution.evolution.lifecycle_stage_function` supplies the machinery
to discharge them through the extension point that module already declares.

One command::

    ucos-cel law
    ucos-cel graph
    ucos-cel authority
    ucos-cel legality
    ucos-cel plan
    ucos-cel replay
    ucos-cel cycle
    ucos-cel acceptance
"""

from __future__ import annotations

from engine.constitution.acceptance import (
    ENFORCEMENT_ID,
    AcceptanceReport,
    CriterionOutcome,
    Measured,
    View,
)
from engine.constitution.acceptance import enforce as enforce_acceptance
from engine.constitution.acceptance import gate as acceptance_gate
from engine.constitution.assimilation import (
    GATE_ID as ASSIMILATION_GATE_ID,
)
from engine.constitution.assimilation import (
    AssimilationVerdict,
    Incumbent,
    Proposal,
    Search,
    assimilate,
    duplicate_capabilities,
    proposal_for,
    require_creatable,
)
from engine.constitution.authority import (
    ATTESTATION_ACTS,
    AUTHORITY_GRAPH_ID,
    Act,
    AuthorityFinding,
    AuthorityReport,
    analyse,
    authority_closure,
)
from engine.constitution.authority import gate as authority_gate
from engine.constitution.catalog import build_population, engine_index
from engine.constitution.dependency import (
    GRAPH_ID,
    DependencyGraph,
    Edge,
    discover,
)
from engine.constitution.errors import (
    AcceptanceFailure,
    CircularAuthority,
    ConstitutionalError,
    DirtyStateViolation,
    DuplicateTruth,
    GraphError,
    IllegalExecution,
    ManualSequencing,
    MetadataIncomplete,
    MutationRefused,
    ReplayDivergence,
    SelfAttestation,
)
from engine.constitution.evolution import (
    ENGINE_ID as EVOLUTION_ENGINE_ID,
)
from engine.constitution.evolution import (
    PHASES,
    CycleRecord,
    Goal,
    Phase,
    capability_reading,
    converge_cycles,
    lifecycle_stage_function,
    phase_order,
    require_elevation,
)
from engine.constitution.evolution import run as run_cycle
from engine.constitution.gateway import (
    GATEWAY_ID,
    PIPELINE,
    Mutation,
    MutationRecord,
    apply,
    pipeline_order,
    propose,
)
from engine.constitution.law import (
    ACCEPTANCE_CRITERIA,
    EXECUTION_CLAUSES,
    EXECUTION_INVARIANTS,
    LAW_ID,
    SUPREMACY_CLAUSE,
    AcceptanceCriterion,
    Clause,
    Invariant,
)
from engine.constitution.legality import (
    LEGALITY_ENGINE_ID,
    PROOFS,
    LegalityReport,
    LegalityVerdict,
    Obligation,
    Proof,
    assess,
    prove,
    require_legal,
)
from engine.constitution.metadata import (
    EXTERNAL_PREFIX,
    MANDATE_ID,
    MANDATED_FACETS,
    ConstitutionalMetadata,
    Facet,
    Population,
    facet_ids,
    graph_bearing_facets,
    is_external,
    require_complete,
)
from engine.constitution.planner import (
    CLOSURES,
    ORDERING_RELATIONS,
    PLANNER_ID,
    ExecutionPlan,
    ExecutionStep,
    plan,
    require_executable,
)
from engine.constitution.replay import (
    REPLAY_ACTS,
    REPLAY_ENGINE_ID,
    ReplayRecord,
    Round,
    converge,
    require_fixed_point,
)
from engine.constitution.state import (
    ENGINE_ID as STATE_ENGINE_ID,
)
from engine.constitution.state import (
    GUARDED_ACTS,
    StateSeal,
    commit,
    guard,
    mutating,
    require_committed,
)

__all__ = [
    # law
    "ACCEPTANCE_CRITERIA",
    "EXECUTION_CLAUSES",
    "EXECUTION_INVARIANTS",
    "LAW_ID",
    "SUPREMACY_CLAUSE",
    "AcceptanceCriterion",
    "Clause",
    "Invariant",
    # metadata mandate (Req 009)
    "EXTERNAL_PREFIX",
    "MANDATED_FACETS",
    "MANDATE_ID",
    "ConstitutionalMetadata",
    "Facet",
    "Population",
    "facet_ids",
    "graph_bearing_facets",
    "is_external",
    "require_complete",
    # dependency graph (Req 001)
    "GRAPH_ID",
    "DependencyGraph",
    "Edge",
    "discover",
    # authority graph (Req 005)
    "ATTESTATION_ACTS",
    "AUTHORITY_GRAPH_ID",
    "Act",
    "AuthorityFinding",
    "AuthorityReport",
    "analyse",
    "authority_closure",
    "authority_gate",
    # legality engine (Req 003)
    "LEGALITY_ENGINE_ID",
    "PROOFS",
    "LegalityReport",
    "LegalityVerdict",
    "Obligation",
    "Proof",
    "assess",
    "prove",
    "require_legal",
    # execution planner (Req 002)
    "CLOSURES",
    "ORDERING_RELATIONS",
    "PLANNER_ID",
    "ExecutionPlan",
    "ExecutionStep",
    "plan",
    "require_executable",
    # dirty state prevention (Req 007)
    "GUARDED_ACTS",
    "STATE_ENGINE_ID",
    "StateSeal",
    "commit",
    "guard",
    "mutating",
    "require_committed",
    # replay engine (Req 006)
    "REPLAY_ACTS",
    "REPLAY_ENGINE_ID",
    "ReplayRecord",
    "Round",
    "converge",
    "require_fixed_point",
    # assimilation gate (Req 008)
    "ASSIMILATION_GATE_ID",
    "AssimilationVerdict",
    "Incumbent",
    "Proposal",
    "Search",
    "assimilate",
    "duplicate_capabilities",
    "proposal_for",
    "require_creatable",
    # mutation gateway (Req 004)
    "GATEWAY_ID",
    "PIPELINE",
    "Mutation",
    "MutationRecord",
    "apply",
    "pipeline_order",
    "propose",
    # enforcement layer (Req 010)
    "ENFORCEMENT_ID",
    "AcceptanceReport",
    "CriterionOutcome",
    "Measured",
    "View",
    "acceptance_gate",
    "enforce_acceptance",
    # evolution engine (Req 011)
    "EVOLUTION_ENGINE_ID",
    "PHASES",
    "CycleRecord",
    "Goal",
    "Phase",
    "capability_reading",
    "converge_cycles",
    "lifecycle_stage_function",
    "phase_order",
    "require_elevation",
    "run_cycle",
    # catalogue
    "build_population",
    "engine_index",
    # errors
    "AcceptanceFailure",
    "CircularAuthority",
    "ConstitutionalError",
    "DirtyStateViolation",
    "DuplicateTruth",
    "GraphError",
    "IllegalExecution",
    "ManualSequencing",
    "MetadataIncomplete",
    "MutationRefused",
    "ReplayDivergence",
    "SelfAttestation",
]
