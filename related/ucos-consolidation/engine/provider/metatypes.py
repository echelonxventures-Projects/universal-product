"""Provider vocabulary — expressed as DATA, seeded as kernel meta-types.

The framework introduces no new kernel code for provider concepts. Instead it *registers*
a small vocabulary of provider **facet** meta-types into the kernel, and models:

    * a provider **category** as a registered kernel meta-type (open set) tagged with the
      role :data:`CATEGORY_ROLE`; and
    * a concrete **provider** as a registered ``MetaObject`` classified by its category
      meta-type, carrying its facets (contract, capabilities, metadata, health, lifecycle,
      dependencies, policy/context bindings) as open attributes and relationships.

Adding a facet, a category, or a provider is therefore a registration — never a framework
change. Nothing here names a vendor, a technology, or a concrete provider.
"""

from __future__ import annotations

#: Namespace for the provider facet vocabulary meta-types.
PROVIDER_META_NS = "umk.provider.meta"

#: Namespace for registered provider categories (each a kernel meta-type).
PROVIDER_CATEGORY_NS = "umk.provider.category"

#: Namespace for concrete provider instances (each classified by a category meta-type).
PROVIDER_INSTANCE_NS = "umk.provider.instance"

#: The attribute marker that distinguishes a provider-category meta-type from any other
#: meta-type. Categories are open: a new one is a registration, not a code change.
CATEGORY_ROLE = "provider-category"

#: The universal provider facets (mission self-check vocabulary), as DATA. Each becomes a
#: kernel meta-type describing one facet of providerhood. Ordered for legibility only.
PROVIDER_FACETS: tuple[tuple[str, str], ...] = (
    ("ProviderContract", "The named, versioned interface a provider satisfies."),
    ("ProviderCapability", "A capability a provider advertises it can realise."),
    ("ProviderMetadata", "Open descriptive metadata attached to a provider."),
    ("ProviderPolicy", "A governance policy bound to a provider."),
    ("ProviderLifecycle", "The governed lifecycle state progression of a provider."),
    ("ProviderContext", "A context within which a provider is bound to operate."),
    ("ProviderRelationship", "A governed relationship between providers (e.g. depends-on)."),
    ("ProviderInstance", "A concrete registered provider classified by a category."),
    ("ProviderHealth", "The advertised health model and status of a provider."),
    ("ProviderSelection", "A strategy by which one provider is chosen among candidates."),
    ("ProviderCategory", "An open classification under which providers are registered."),
)

#: The attribute keys a provider instance carries. Documented for legibility; the kernel
#: attribute map is open, so a provider may carry additional keys without a framework
#: change.
PROVIDER_ATTRIBUTE_KEYS: tuple[str, ...] = (
    "capabilities",
    "contract",
    "metadata",
    "health",
    "lifecycle",
)


def facet_keys() -> tuple[str, ...]:
    """The natural keys of the provider facet meta-types (deterministically ordered)."""
    return tuple(sorted(key for key, _desc in PROVIDER_FACETS))


__all__ = [
    "PROVIDER_META_NS",
    "PROVIDER_CATEGORY_NS",
    "PROVIDER_INSTANCE_NS",
    "CATEGORY_ROLE",
    "PROVIDER_FACETS",
    "PROVIDER_ATTRIBUTE_KEYS",
    "facet_keys",
]
