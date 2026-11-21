"""Universal Provider Framework errors.

Every framework failure is a subclass of :class:`ProviderFrameworkError`, which is itself
a :class:`~engine.kernel.errors.KernelError` — so the whole provider surface is catchable
either as a provider error or as part of the kernel error surface. Errors carry structured
context rather than only a message, so evidence remains machine-readable.
"""

from __future__ import annotations

from engine.kernel.errors import KernelError


class ProviderFrameworkError(KernelError):
    """Base class for every Universal Provider Framework error."""


class ProviderCategoryUnknownError(ProviderFrameworkError):
    """A provider was registered against a category that is not a registered category.

    This is the constitutional guard that keeps the category space *open by
    registration*: a new provider category is admitted by first registering its
    category meta-type, never by editing the framework.
    """


class ProviderContractError(ProviderFrameworkError):
    """A provider declared a malformed or absent contract."""


class ProviderResolutionError(ProviderFrameworkError):
    """No registered provider satisfies a resolution request."""


class ProviderNegotiationError(ProviderFrameworkError):
    """A provider negotiation could not be completed."""


class ProviderSelectionError(ProviderFrameworkError):
    """A selection strategy was requested that is not registered."""


__all__ = [
    "ProviderFrameworkError",
    "ProviderCategoryUnknownError",
    "ProviderContractError",
    "ProviderResolutionError",
    "ProviderNegotiationError",
    "ProviderSelectionError",
]
