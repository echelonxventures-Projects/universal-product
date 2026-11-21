"""TASK-000034 — Runtime Assembly error taxonomy (EPIC-005).

The Runtime Assembly engine reuses the EC-1 Foundation error discipline
(TASK-000006): every error is rooted in :class:`FoundationError`, carries a
stable, category-prefixed ``code`` and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable.

Runtime assembly binds only registered, certified components (IMP-007 §8/§15):
when provenance cannot be validated, a signature cannot be verified, the SBOM is
absent, the dependency closure is broken, or a secret would be exposed inline, the
engine fails loudly with a specific, evidence-bearing error. The base class is
named :class:`RuntimeAssemblyError` (not ``RuntimeError``) so it never shadows the
Python builtin.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class RuntimeAssemblyError(FoundationError):
    """Base class for all Runtime Assembly errors (EPIC-005)."""

    code = "RT-000"


class ProvenanceValidationError(RuntimeAssemblyError):
    """The provenance chain is absent, malformed, or inconsistent (IMP-007 §1/§8)."""

    code = "RT-PROV-001"


class SignatureValidationError(RuntimeAssemblyError):
    """The package signature could not be verified — assembly is refused (§12/§15)."""

    code = "RT-SIG-001"


class SBOMValidationError(RuntimeAssemblyError):
    """The Software Bill of Materials is absent or malformed (§12)."""

    code = "RT-SBOM-001"


class DependencyClosureError(RuntimeAssemblyError):
    """The pinned dependency closure is broken or ambiguous (§8)."""

    code = "RT-DEP-001"


class SecretExposureError(RuntimeAssemblyError):
    """An inline secret was supplied where a reference is required (SEC-04, §8)."""

    code = "RT-SEC-001"


class DisclosureError(RuntimeAssemblyError):
    """The EC-1 provisional-state disclosure is missing (DE-05, C-05)."""

    code = "RT-DISC-001"


class DeploymentError(RuntimeAssemblyError):
    """A deployment or rollback descriptor could not be generated (§8; IP-08)."""

    code = "RT-DEPLOY-001"


# --------------------------------------------------------------------------- #
# EPIC-006 — Universal Runtime Composition error taxonomy                      #
# --------------------------------------------------------------------------- #
#
# The Universal Runtime Composition Engine (EPIC-006, realising RUNTIME-013 §D8/D9)
# composes **already-assembled** runtime units ("Universes") into a deterministic,
# bounded, acyclic composition. It is a composition *structure* only — never an
# engine, scheduler, or executor (RUNTIME-013 ORL-15/ORL-23). Its errors share the
# Foundation error discipline (coded, structured, non-secret) but form a distinct
# root from :class:`RuntimeAssemblyError`, because composition is a separate runtime
# capability from assembly (no duplicate capability ownership).


class RuntimeCompositionError(FoundationError):
    """Base class for all Universal Runtime Composition errors (EPIC-006)."""

    code = "RT-COMP-000"


class RuntimeGraphError(RuntimeCompositionError):
    """The runtime composition graph is cyclic, open, or malformed (ORL-11/17)."""

    code = "RT-GRAPH-001"


class ContextResolutionError(RuntimeCompositionError):
    """A universe is unbounded or its bounding context is inconsistent (ORL-05/14)."""

    code = "RT-CTX-001"


class ReferenceFrameError(RuntimeCompositionError):
    """A cross-context reference leaks isolation or a federation link is invalid.

    Enforces context isolation and explicit, collision-free federation
    (RUNTIME-013 ORL-12/ORL-13; ENG-005 Federation References).
    """

    code = "RT-REF-001"


class ExecutionPlanError(RuntimeCompositionError):
    """A deterministic execution plan could not be produced (ORL-09/ORL-20)."""

    code = "RT-PLAN-001"


class OrchestrationError(RuntimeCompositionError):
    """A coordinated composition (orchestration) could not be recorded (ORL-01/09)."""

    code = "RT-ORCH-001"


__all__ = [
    "RuntimeAssemblyError",
    "ProvenanceValidationError",
    "SignatureValidationError",
    "SBOMValidationError",
    "DependencyClosureError",
    "SecretExposureError",
    "DisclosureError",
    "DeploymentError",
    # EPIC-006 — composition
    "RuntimeCompositionError",
    "RuntimeGraphError",
    "ContextResolutionError",
    "ReferenceFrameError",
    "ExecutionPlanError",
    "OrchestrationError",
]
