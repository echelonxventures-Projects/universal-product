"""UCOS Ω∞ — Universal Provider Framework (PROGRAM-003, WAVE-2).

The Universal Provider Framework is the constitutional **realization layer** between the
immutable Universal Meta-Kernel (PROGRAM-002) and every future implementation:

    * The kernel defines **existence** — what a thing is (a governed, registered
      ``MetaObject`` classified by an open ``MetaType``).
    * The Provider Framework defines **realization** — how a capability is provided,
      selected, negotiated, composed, versioned, and governed.
    * Concrete providers implement **behaviour** — and are future *registrations*, never
      framework modifications.

Design (why this is the *smallest possible* framework, and why it is not a duplicate):

    * It is built entirely **on** the kernel and modifies neither the kernel nor any other
      package. A provider *category* is a registered kernel meta-type; a concrete provider
      is a registered ``MetaObject`` classified by that category meta-type. There is no
      closed set of provider kinds anywhere — a previously unknown provider category is
      admitted by *registration only* (Universal Provider Law; the kernel's Engineering
      Rule 7).
    * It contains **no** ``enum`` of provider kinds, no ``if kind == ...`` branch, no
      vendor or technology literal, and names no concrete provider.
    * A distinct, higher-layer ``platform/universal_provider`` (EC-2 "Terminal-04") exists;
      this framework does not import or duplicate it. The engine layer cannot depend on the
      platform layer, so the kernel realization layer necessarily lives here, over a
      different substrate (governed kernel meta-objects rather than platform descriptors).

Everything is deterministic and content-addressed (the kernel guarantees it): no
wall-clock, no RNG, no network. An identical catalogue of registrations over an identical
kernel yields an identical framework state.
"""

from __future__ import annotations

from engine.provider.errors import (
    ProviderCategoryUnknownError,
    ProviderContractError,
    ProviderFrameworkError,
    ProviderNegotiationError,
    ProviderResolutionError,
)
from engine.provider.framework import NegotiationResult, ProviderFramework
from engine.provider.metatypes import (
    CATEGORY_ROLE,
    PROVIDER_CATEGORY_NS,
    PROVIDER_FACETS,
    PROVIDER_INSTANCE_NS,
    PROVIDER_META_NS,
)
from engine.provider.selection import SelectionStrategy, highest_version, register_strategy

__all__ = [
    "ProviderFramework",
    "NegotiationResult",
    "ProviderFrameworkError",
    "ProviderCategoryUnknownError",
    "ProviderContractError",
    "ProviderResolutionError",
    "ProviderNegotiationError",
    "SelectionStrategy",
    "highest_version",
    "register_strategy",
    "PROVIDER_META_NS",
    "PROVIDER_CATEGORY_NS",
    "PROVIDER_INSTANCE_NS",
    "CATEGORY_ROLE",
    "PROVIDER_FACETS",
]

__framework_version__ = "1.0.0"
