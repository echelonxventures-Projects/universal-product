"""Idempotent, order-independent seeding of the civilization facet vocabulary.

The three components of this layer — the dimension registry, the composition planner and the
constitutional generator — are each independently usable over a bare kernel, and each needs
part of the same facet vocabulary. If each seeded only what it happened to need, the
namespace a facet landed in would depend on which component was constructed first, and two
platforms holding the same registrations could disagree on their snapshot hash.

So seeding is a single function, seeding the whole vocabulary into one namespace,
idempotently. Constructing the components in any order yields byte-identical kernel state.
"""

from __future__ import annotations

from engine.civilization.metatypes import CIVILIZATION_FACETS, CIVILIZATION_META_NS
from engine.kernel.kernel import MetaKernel


def seed_facets(kernel: MetaKernel) -> None:
    """Register the civilization facet vocabulary as kernel meta-types (DATA).

    Idempotent: a facet already known to the kernel is left exactly as it is.
    """
    known = set(kernel.registry.metatype_keys())
    for natural_key, description in CIVILIZATION_FACETS:
        if natural_key not in known:
            kernel.register_metatype(
                natural_key,
                name=natural_key,
                description=description,
                namespace=CIVILIZATION_META_NS,
            )


__all__ = ["seed_facets"]
