"""UCOS-NUC-001 — the Nucleus Ownership Authority.

The one place the constitutional rule *capabilities belong to Nuclei; layers and
compositions own nothing* is implemented and enforced. It creates no second nucleus
definition, no second registry, no second identifier scheme, no second lifecycle and no
second hash primitive: identifiers come from :mod:`engine.registry.universal.identity`,
digests from :mod:`engine.uckp.canonical`, terms from :mod:`engine.uckp.vocabulary`, and
ordering from :mod:`engine.foundation.composition.ordering`.

The constitutional correction it encodes
----------------------------------------
Commerce is a **Composition**, not a Nucleus — and so is every named platform, product,
sector vertical and civilisational system. That is not a label applied by convention here:
:func:`engine.nucleus.model.derive_role` derives the role from whether the subject selects
nuclei, and the registry refuses a capability whose owner is anything but a Nucleus. A
composition therefore *cannot* own a capability, and a subject that selects nuclei
*cannot* be registered as a nucleus.

One command::

    ucos-nucleus law
    ucos-nucleus registry
    ucos-nucleus gate
    ucos-nucleus compose --composition commerce
    ucos-nucleus lifecycle --subject <id>
    ucos-nucleus certify
"""

from __future__ import annotations

from engine.nucleus.catalog import (
    SEED_COMPOSITIONS,
    SEED_NUCLEI,
    composition_keys,
    layer_keys,
    nucleus_keys,
    seed_capabilities,
    seed_subjects,
)
from engine.nucleus.certification import (
    Certificate,
    Check,
    ValidationReport,
    Verdict,
    certify,
    validate,
)
from engine.nucleus.context import (
    CONTEXT_BOUND,
    bind_lineage,
    bind_registry,
    context_fingerprint,
    context_measurements,
    context_stage_function,
    dictionary_with_context,
    evolutions_without_context,
    evolve_in_context,
    unbound_subjects,
)
from engine.nucleus.errors import (
    CertificationError,
    CompositionOwnershipViolation,
    EvolutionError,
    LayerOwnershipViolation,
    LifecycleError,
    MisclassificationError,
    NucleusError,
    OwnershipViolation,
    RegistrationError,
    StructuralValidationError,
)
from engine.nucleus.evolution import Evolution, EvolutionLedger, state_must_grow
from engine.nucleus.law import (
    LAW_ID,
    OWNERSHIP_CLAUSES,
    OWNERSHIP_INVARIANTS,
    SUPREMACY_CLAUSE,
    StructuralRole,
)
from engine.nucleus.lifecycle import (
    STAGES,
    LifecycleExecution,
    Stage,
    StageStatus,
    execute,
    replay,
    stage_order,
)
from engine.nucleus.lineage import LineageEntry, LineageLedger, ledger_for
from engine.nucleus.model import (
    CapabilityDeclaration,
    CapabilityRecord,
    OwnershipAssignment,
    SubjectDeclaration,
    SubjectRecord,
    derive_role,
)
from engine.nucleus.ownership import GATE_ID, OwnershipReport, enforce, gate
from engine.nucleus.registry import NucleusRegistry, build_seed_registry

__all__ = [
    # law
    "LAW_ID",
    "SUPREMACY_CLAUSE",
    "OWNERSHIP_CLAUSES",
    "OWNERSHIP_INVARIANTS",
    "StructuralRole",
    # model
    "SubjectDeclaration",
    "SubjectRecord",
    "CapabilityDeclaration",
    "CapabilityRecord",
    "OwnershipAssignment",
    "derive_role",
    # catalogue
    "SEED_NUCLEI",
    "SEED_COMPOSITIONS",
    "seed_subjects",
    "seed_capabilities",
    "nucleus_keys",
    "layer_keys",
    "composition_keys",
    # registry
    "NucleusRegistry",
    "build_seed_registry",
    # gate
    "GATE_ID",
    "OwnershipReport",
    "enforce",
    "gate",
    # lifecycle
    "STAGES",
    "Stage",
    "StageStatus",
    "LifecycleExecution",
    "execute",
    "replay",
    "stage_order",
    # lineage + evolution
    "LineageEntry",
    "LineageLedger",
    "ledger_for",
    "Evolution",
    "EvolutionLedger",
    "state_must_grow",
    # context binding
    "CONTEXT_BOUND",
    "context_fingerprint",
    "context_stage_function",
    "bind_lineage",
    "bind_registry",
    "unbound_subjects",
    "evolve_in_context",
    "evolutions_without_context",
    "dictionary_with_context",
    "context_measurements",
    # validation + certification
    "Check",
    "ValidationReport",
    "Certificate",
    "Verdict",
    "validate",
    "certify",
    # errors
    "NucleusError",
    "StructuralValidationError",
    "RegistrationError",
    "OwnershipViolation",
    "LayerOwnershipViolation",
    "CompositionOwnershipViolation",
    "MisclassificationError",
    "LifecycleError",
    "EvolutionError",
    "CertificationError",
]
