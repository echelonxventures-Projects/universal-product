"""Universal Meta-Civilization layer errors.

Every failure of this layer is a subclass of :class:`CivilizationError`, which is itself a
:class:`~engine.kernel.errors.KernelError` — so the whole surface is catchable either as a
civilization error or as part of the kernel error surface. Errors carry structured context
rather than only a message, so evidence remains machine-readable.
"""

from __future__ import annotations

from engine.kernel.errors import KernelError


class CivilizationError(KernelError):
    """Base class for every Universal Meta-Civilization layer error."""


class DimensionUnknownError(CivilizationError):
    """A dimension was referenced that is not a registered dimension.

    This is the constitutional guard that keeps the dimension space *open by
    registration*: a previously unknown dimension is admitted by registering it, never by
    editing this layer and never by extending a closed enumeration.
    """


class DimensionClosedError(CivilizationError):
    """A dimension declared a closed value set, or a finite bound in either direction.

    The Universal Dimension Model admits no dimension that legislates its own bound: a
    dimension describes an axis, and the axis is unbounded above *and* below. A finite value
    set, a ceiling, and a floor all belong to a *policy over* a dimension, never to the
    dimension itself — including a bound imposed by physical reality, which is a
    configuration bound on a policy rather than a property of the axis.
    """


class CapabilityUnknownError(CivilizationError):
    """Composition referenced a capability that is not registered."""


class CompositionCycleError(CivilizationError):
    """A capability dependency graph contains a cycle, so no order exists."""


class CompositionUnsatisfiedError(CivilizationError):
    """A capability's declared dimension or policy requirements are unsatisfied.

    Composition is context aware and policy aware: a plan is refused rather than silently
    degraded when the requesting context does not bind a dimension a capability requires.
    """


class CompositionStrategyError(CivilizationError):
    """A composition strategy was requested that is not registered."""


class StratumUnknownError(CivilizationError):
    """A generation stratum was referenced that is not registered."""


class StratumOrderError(CivilizationError):
    """A stratum declared a predecessor that cannot be ordered."""


class BlueprintUnknownError(CivilizationError):
    """Generation referenced a constitutional blueprint that is not registered."""


class DerivationError(CivilizationError):
    """A generated artefact does not derive from the Universal Meta-Kernel.

    Nothing below the Meta-Kernel may bypass it: every generated stratum record roots, by
    an unbroken derivation chain, at the kernel's reflective root meta-type.
    """


__all__ = [
    "CivilizationError",
    "DimensionUnknownError",
    "DimensionClosedError",
    "CapabilityUnknownError",
    "CompositionCycleError",
    "CompositionUnsatisfiedError",
    "CompositionStrategyError",
    "StratumUnknownError",
    "StratumOrderError",
    "BlueprintUnknownError",
    "DerivationError",
]
