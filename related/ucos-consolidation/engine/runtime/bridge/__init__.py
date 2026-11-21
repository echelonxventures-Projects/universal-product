"""EPIC-RTE-003 — Runtime Integration & Repository Execution Bridge.

Public API surface for the single, canonical **Runtime Bridge** that connects the
repository lifecycle to runtime execution. It extends the EPIC-RTE-002 Universal
Runtime Execution Platform and the EPIC-006 Universal Runtime Composition Engine
**additively**, in this :mod:`engine.runtime.bridge` subpackage, and **implements
only integration** (the EPIC-RTE-003 mission): it reuses the Composition, Execution
Platform (execution state, checkpoint, continuation, recovery, replay,
authorization, monitoring), Validation, Certification, Acceptance, and Knowledge
engines verbatim and adds **no** duplicate runtime logic.

It realises the six integration objectives, each a pure, deterministic function
over a reused engine, unified behind the :class:`RuntimeBridge` facade:

    RepositorySubject → Composition → Execution → Validation → Certification →
    Acceptance, and Execution Evidence → Knowledge.

Everything is deterministic, replayable, and resumable: identical inputs yield a
byte-identical :class:`RepositoryExecutionRecord`, and the facade surfaces the
reused platform's replay/checkpoint/continue/recover capabilities over a produced
record. No execution path is skipped.
"""

from __future__ import annotations

from engine.runtime.bridge.bridge import (
    DEFAULT_KNOWLEDGE_OWNER,
    DEFAULT_KNOWLEDGE_UNIVERSE,
    RuntimeBridge,
    ValidatedUnit,
    accept_execution,
    certify_execution,
    compose_repository,
    execute_composition,
    record_execution_evidence,
    validate_execution,
)
from engine.runtime.bridge.contracts import (
    BRIDGE_AUTHORITY,
    BRIDGE_RECORD_FORMAT,
    RepositoryExecutionRecord,
    UnitAssurance,
)
from engine.runtime.bridge.errors import (
    BridgeInputError,
    RuntimeBridgeError,
)

__all__ = [
    # facade
    "RuntimeBridge",
    # six integration bridges
    "compose_repository",
    "execute_composition",
    "validate_execution",
    "certify_execution",
    "accept_execution",
    "record_execution_evidence",
    # value types
    "ValidatedUnit",
    "UnitAssurance",
    "RepositoryExecutionRecord",
    "BRIDGE_RECORD_FORMAT",
    "BRIDGE_AUTHORITY",
    # defaults
    "DEFAULT_KNOWLEDGE_OWNER",
    "DEFAULT_KNOWLEDGE_UNIVERSE",
    # errors
    "RuntimeBridgeError",
    "BridgeInputError",
]
