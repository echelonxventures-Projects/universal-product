"""The Universal Dimension Model — an open, governed registry of dimensions.

A **dimension** is an axis along which any thing may be contextualized: a language, a
currency, a country, a calendar, a jurisdiction, a cloud, a region, a tenant, an
organization, a reality, an existence model, or an axis nobody has named yet. This module
contains no list of dimensions, and no closed enumeration of dimension kinds, because a
dimension is admitted by **registration**:

    registry.register_dimension("SomeAxisNobodyHasNamedYet")

Each registration mints two governed kernel objects — the dimension's own **meta-type** (so
the dimension can classify things) and its **declaration** (so the dimension's facets,
contexts and policies are themselves registered knowledge). Both go through the kernel's
single admission authority; this module holds no registry of its own.

Two constitutional invariants are bound into kernel governance here, so they are enforced at
admission rather than asserted in prose:

    * **every dimension satisfies every mandatory facet** — a declaration that omits one is
      refused (:data:`~engine.civilization.metatypes.DIMENSION_FACETS`); and
    * **no dimension legislates its own bound** — a declaration carrying a closed value
      set, a ceiling, or a floor is refused
      (:data:`~engine.civilization.metatypes.FORBIDDEN_DIMENSION_KEYS`).

Unlimited specialization and generalization are the same relation read in two directions
(:data:`~engine.civilization.metatypes.SPECIALIZES`); unlimited composition is
:data:`~engine.civilization.metatypes.COMPOSES`. Neither has a depth or arity limit.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from engine.civilization.errors import DimensionClosedError, DimensionUnknownError
from engine.civilization.metatypes import (
    COMPOSES,
    DIMENSION_FACETS,
    DIMENSION_META_NS,
    DIMENSION_NS,
    DIMENSION_ROLE,
    FORBIDDEN_DIMENSION_KEYS,
    SPECIALIZES,
    dimension_facet_keys,
)
from engine.civilization.seeding import seed_facets
from engine.kernel.governance import Constraint
from engine.kernel.kernel import MetaKernel
from engine.kernel.meta import MetaObject


class DimensionRegistry:
    """The open dimension space, realized entirely over the Universal Meta-Kernel."""

    __slots__ = ("_kernel",)

    def __init__(self, *, kernel: MetaKernel | None = None) -> None:
        self._kernel = kernel if kernel is not None else MetaKernel()
        seed_facets(self._kernel)
        self._bind_governance()

    # -- seeding + governance --------------------------------------------------

    def _bind_governance(self) -> None:
        """Bind the dimension invariants into the kernel's open admission policy.

        The kernel is not edited: these are registrations through the governance extension
        point. Each constraint is scoped to dimension declarations, so it is a no-op for
        every other kind of meta-object.
        """
        gov = self._kernel.governance
        existing = set(gov.admission.constraint_names())
        for name, check in (
            ("dimension-facets-complete", self._check_facets_complete),
            ("dimension-declares-no-ceiling", self._check_no_bound),
        ):
            if name not in existing:
                gov.register_constraint(Constraint(name, check))

    def _check_facets_complete(self, candidate: MetaObject, _view: Any) -> tuple[bool, str]:
        """A dimension declaration satisfies every mandatory facet."""
        if candidate.namespace != DIMENSION_NS:
            return True, ""
        declared = candidate.attributes.get("facets")
        have = set(declared) if isinstance(declared, list | tuple) else set()
        missing = sorted(set(dimension_facet_keys()) - have)
        if not missing:
            return True, ""
        return False, f"dimension omits mandatory facet(s): {missing}"

    def _check_no_bound(self, candidate: MetaObject, _view: Any) -> tuple[bool, str]:
        """A dimension may not legislate a closed value set, or a bound in either direction."""
        if candidate.namespace != DIMENSION_NS:
            return True, ""
        offending = sorted(set(FORBIDDEN_DIMENSION_KEYS) & set(candidate.attributes))
        if not offending:
            return True, ""
        return False, f"dimension declares a bound: {offending}"

    # -- registration ----------------------------------------------------------

    def register_dimension(
        self,
        key: str,
        *,
        name: str = "",
        description: str = "",
        contexts: Sequence[str] = (),
        policies: Sequence[str] = (),
        specializes: str | None = None,
        attributes: Mapping[str, Any] | None = None,
    ) -> MetaObject:
        """Admit a dimension: its meta-type, then its governed declaration.

        ``specializes`` names an already-registered dimension, making this one a
        specialization of it — the mechanism for unlimited specialization (and, read in
        reverse, unlimited generalization). There is no depth limit.

        Raises :class:`DimensionUnknownError` when ``specializes`` names an unregistered
        dimension, and :class:`DimensionClosedError` when the declaration would legislate a
        ceiling.
        """
        if specializes is not None and not self.is_registered(specializes):
            raise DimensionUnknownError(
                "cannot specialize an unregistered dimension",
                dimension=key,
                specializes=specializes,
            )
        attrs: dict[str, Any] = dict(attributes or {})
        offending = sorted(set(FORBIDDEN_DIMENSION_KEYS) & set(attrs))
        if offending:
            raise DimensionClosedError(
                "a dimension may not declare a closed value set or a finite bound",
                dimension=key,
                offending=offending,
            )
        if key not in set(self._kernel.registry.metatype_keys()):
            self._kernel.register_metatype(
                key,
                name=key,
                description=description or f"Dimension {key}.",
                namespace=DIMENSION_META_NS,
                attributes={"role": DIMENSION_ROLE},
            )
        attrs["facets"] = list(dimension_facet_keys())
        attrs["contexts"] = sorted(contexts)
        attrs["policies"] = sorted(policies)
        relationships = (
            ({"relation": SPECIALIZES, "target": self.declaration(specializes).identity},)
            if specializes is not None
            else ()
        )
        return self._kernel.register_object(
            metatype=key,
            natural_key=key,
            namespace=DIMENSION_NS,
            name=name or key,
            attributes=attrs,
            relationships=relationships,
        )

    def compose(self, key: str, *, into: str) -> MetaObject:
        """Record that dimension ``into`` is composed from dimension ``key``.

        Composition is unbounded in arity: a composite dimension may compose any number of
        other dimensions, each recorded as a further governed version.
        """
        source = self.declaration(key)
        return self._kernel.compose(self.declaration(into).identity, COMPOSES, source.identity)

    # -- lookup + discovery ----------------------------------------------------

    @property
    def kernel(self) -> MetaKernel:
        """The kernel this registry admits through — there is no second registry."""
        return self._kernel

    def is_registered(self, key: str) -> bool:
        """True iff ``key`` is a registered dimension (not merely a known meta-type)."""
        return any(d.natural_key == key for d in self.dimensions())

    def declaration(self, key: str) -> MetaObject:
        """The governed declaration of a registered dimension."""
        for declared in self.dimensions():
            if declared.natural_key == key:
                return declared
        raise DimensionUnknownError("dimension is not registered", dimension=key)

    def dimensions(self) -> tuple[MetaObject, ...]:
        """Every registered dimension declaration, ordered by natural key."""
        found = self._kernel.discover(namespace=DIMENSION_NS)
        return tuple(sorted(found, key=lambda o: o.natural_key))

    def dimension_keys(self) -> tuple[str, ...]:
        """The natural keys of every registered dimension, ordered."""
        return tuple(d.natural_key for d in self.dimensions())

    def discover(
        self,
        *,
        context: str | None = None,
        policy: str | None = None,
        specializes: str | None = None,
    ) -> tuple[MetaObject, ...]:
        """Find dimensions by open predicates. Every dimension is discoverable."""
        results = self.dimensions()
        if context is not None:
            results = tuple(d for d in results if context in d.attributes.get("contexts", ()))
        if policy is not None:
            results = tuple(d for d in results if policy in d.attributes.get("policies", ()))
        if specializes is not None:
            parent = self.declaration(specializes).identity
            results = tuple(d for d in results if parent in d.related(SPECIALIZES))
        return results

    def trace(self, key: str) -> dict[str, object]:
        """The traceable lineage of a registered dimension."""
        return self._kernel.trace(self.declaration(key).identity)

    # -- validation + description ----------------------------------------------

    def validate(self) -> bool:
        """Validate every registered dimension against the mandatory facet set."""
        mandatory = set(dimension_facet_keys())
        for declared in self.dimensions():
            declared_facets = declared.attributes.get("facets")
            have = set(declared_facets) if isinstance(declared_facets, list | tuple) else set()
            if mandatory - have:
                return False
        return self._kernel.validate()

    def describe(self) -> dict[str, object]:
        """A deterministic, machine-readable description of the dimension space."""
        return {
            "subject": "UniversalDimensionModel",
            "dimensions": list(self.dimension_keys()),
            "count": len(self.dimensions()),
            "mandatory_facets": list(dimension_facet_keys()),
            "forbidden_declarations": list(FORBIDDEN_DIMENSION_KEYS),
            "facet_definitions": {key: desc for key, desc in DIMENSION_FACETS},
            "closed_set": False,
            "upper_limit": None,
        }


__all__ = ["DimensionRegistry"]
