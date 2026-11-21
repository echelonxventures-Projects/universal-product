"""UCXI-000001 — Universal Context Intelligence error taxonomy.

Every refusal of the context layer is a typed, auditable event. The taxonomy is
rooted in :class:`~engine.foundation.obs.errors.FoundationError` so a context
refusal carries the same stable ``code`` + structured, non-secret ``context``
discipline as every other EC-1 error surface (PL-02, IP-12) and is machine
consumable by the validation, certification and gate layers above it.

The layer is **fail-closed** (CXL-11): an ambiguous, unbounded, unclassified or
unprovenanced context is refused rather than guessed. Each error below names one
such refusal, so a caller can distinguish *"the declaration is malformed"* from
*"the declaration is well formed but the constitution forbids it"*.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class ContextError(FoundationError):
    """Base class for every Universal Context Intelligence error."""

    code = "CTX-000"


class ContextValidationError(ContextError):
    """A context declaration failed structural validation."""

    code = "CTX-VALID-400"


class TaxonomyError(ContextError):
    """A context kind or taxon is unknown, malformed, or illegally extended."""

    code = "CTX-TAX-400"


class OntologyError(ContextError):
    """A context violates the ontology: missing/unknown dimension or bad relation."""

    code = "CTX-ONT-400"


class ConstitutionViolation(ContextError):
    """A context (or context set) breaches a Context Constitution law."""

    code = "CTX-CONST-403"


class ContextRegistrationError(ContextError):
    """A registration was refused by the context registration authority."""

    code = "CTX-REG-400"


class DuplicateContextError(ContextRegistrationError):
    """A different context is already registered under the same identity."""

    code = "CTX-REG-DUP-409"


class ContextOnceViolation(ContextRegistrationError):
    """Identical context content is already registered under another identity.

    The context analogue of *Knowledge Once* (CXL-06): one canonical home per unit
    of context.
    """

    code = "CTX-REG-ONCE-409"


class ContextNotFoundError(ContextRegistrationError):
    """The requested context identity is not registered."""

    code = "CTX-REG-404"


class LifecycleTransitionError(ContextError):
    """An illegal context lifecycle transition was attempted."""

    code = "CTX-LIFE-409"


class ContextResolutionFailure(ContextError):
    """A required context (or required dimension) could not be resolved."""

    code = "CTX-RES-404"


class ContextAmbiguityError(ContextResolutionFailure):
    """Two equally authoritative sources disagree, so resolution is refused."""

    code = "CTX-RES-409"


class ContextCompositionError(ContextError):
    """A context composition is unbounded, incomplete, or internally inconsistent."""

    code = "CTX-COMP-409"


class ContextIsolationError(ContextCompositionError):
    """A cross-boundary context reference has no authorising federation (CXL-04)."""

    code = "CTX-ISO-403"


class ContextGraphError(ContextError):
    """The context graph is malformed (illegal relation, cycle, orphan)."""

    code = "CTX-GRAPH-409"


class ContextRuntimeError(ContextError):
    """A context could not be bound, activated, or released."""

    code = "CTX-RT-409"


class ContextCertificationError(ContextError):
    """Certification could not be computed (or was asked to assert, not compute)."""

    code = "CTX-CERT-500"


class ContextEvidenceError(ContextError):
    """Evidence could not be produced or would land in the frozen corpus (DP-03)."""

    code = "CTX-EVD-500"


__all__ = [
    "ContextError",
    "ContextValidationError",
    "TaxonomyError",
    "OntologyError",
    "ConstitutionViolation",
    "ContextRegistrationError",
    "DuplicateContextError",
    "ContextOnceViolation",
    "ContextNotFoundError",
    "LifecycleTransitionError",
    "ContextResolutionFailure",
    "ContextAmbiguityError",
    "ContextCompositionError",
    "ContextIsolationError",
    "ContextGraphError",
    "ContextRuntimeError",
    "ContextCertificationError",
    "ContextEvidenceError",
]
