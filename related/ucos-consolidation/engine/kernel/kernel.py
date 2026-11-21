"""The Universal Meta-Kernel facade.

:class:`MetaKernel` composes the open :class:`~engine.kernel.registry.UniversalRegistry`
and :class:`~engine.kernel.governance.Governance`, seeds the reflective root meta-type and
the founding universal meta-types (as DATA — see :mod:`engine.kernel.seed`), and exposes
the universal operations every abstraction inherits. It is the single object a provider
holds; providers register concrete things through it and never subclass the kernel.

The cross-cutting capability contract is expressed generically here — ``register``,
``describe``, ``discover``, ``classify``, ``govern``, ``validate``, ``certify``, ``trace``,
``evolve``, ``compose`` — so the 25 directives hold uniformly for *anything* registered,
present or future.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from engine.foundation.contracts.contract import Version
from engine.kernel.governance import Governance, GovernanceDecision
from engine.kernel.meta import (
    META_TYPE_ROOT,
    MetaObject,
    make_metatype,
    reflective_root,
)
from engine.kernel.registry import UniversalRegistry
from engine.kernel.seed import FOUNDING_METATYPES, FOUNDING_NAMESPACE


class MetaKernel:
    """The immutable engineering substrate: open, governed, self-describing."""

    __slots__ = ("_registry",)

    version = "1.0.0"

    def __init__(self, *, seed: bool = True, governance: Governance | None = None) -> None:
        self._registry = UniversalRegistry(governance=governance)
        if seed:
            self._seed()

    # -- seeding ---------------------------------------------------------------

    def _seed(self) -> None:
        # 1. The reflective root classifies itself — the single fixed point.
        self._registry.register(reflective_root(namespace=FOUNDING_NAMESPACE))
        # 2. The founding universal meta-types, as DATA. Each is a registration, not a
        #    code branch; the kernel treats them exactly as it treats a category it has
        #    never seen (they simply happen to ship in the seed table).
        for natural_key, name, description in FOUNDING_METATYPES:
            self.register_metatype(natural_key, name=name, description=description)

    # -- registry access -------------------------------------------------------

    @property
    def registry(self) -> UniversalRegistry:
        """The underlying open, governed registry."""
        return self._registry

    @property
    def governance(self) -> Governance:
        """The kernel's governance authority."""
        return self._registry.governance

    # -- Universal Classification / registration -------------------------------

    def register_metatype(
        self,
        natural_key: str,
        *,
        name: str = "",
        description: str = "",
        namespace: str = FOUNDING_NAMESPACE,
        attributes: Mapping[str, Any] | None = None,
        provenance: Mapping[str, Any] | None = None,
    ) -> MetaObject:
        """Declare a new concept-category by registering its meta-type.

        This is the whole of "extending the platform to a previously unknown category":
        one governed registration. The kernel is not modified.
        """
        obj = make_metatype(
            natural_key,
            namespace=namespace,
            name=name,
            description=description,
            attributes=attributes,
            provenance=provenance,
        )
        return self._registry.register(obj)

    def register_object(
        self,
        *,
        metatype: str,
        natural_key: str,
        namespace: str,
        name: str = "",
        version: Version | str = "1.0.0",
        attributes: Mapping[str, Any] | None = None,
        relationships: Any = None,
        provenance: Mapping[str, Any] | None = None,
    ) -> MetaObject:
        """Register a concrete instance classified by an (already registered) meta-type."""
        ver = Version.parse(version) if isinstance(version, str) else version
        obj = MetaObject(
            metatype=metatype,
            namespace=namespace,
            natural_key=natural_key,
            name=name,
            version=ver,
            attributes=dict(attributes or {}),
            relationships=tuple(relationships or ()),
            provenance=dict(provenance or {}),
        )
        return self._registry.register(obj)

    def classify(self, identity: str) -> str:
        """Return the meta-type that classifies a registered thing."""
        return self._registry.get(identity).metatype

    # -- Universal Discovery ---------------------------------------------------

    def discover(
        self,
        *,
        metatype: str | None = None,
        namespace: str | None = None,
        attribute: tuple[str, Any] | None = None,
    ) -> tuple[MetaObject, ...]:
        """Find registered things by open predicates. Everything is discoverable."""
        results = self._registry.by_metatype(metatype) if metatype else self._registry.all()
        if namespace is not None:
            results = tuple(o for o in results if o.namespace == namespace)
        if attribute is not None:
            key, value = attribute
            results = tuple(o for o in results if o.attributes.get(key) == value)
        return results

    def metatypes(self) -> tuple[MetaObject, ...]:
        """The open universe of registered concept-categories."""
        return self._registry.metatypes()

    # -- Universal Evolution / Composition -------------------------------------

    def evolve(self, identity: str, version: Version | str, **changes: Any) -> MetaObject:
        """Register a new, superseding version of a registered thing."""
        current = self._registry.get(identity)
        ver = Version.parse(version) if isinstance(version, str) else version
        evolved = current.evolve(ver, **changes)
        return self._registry.register(evolved)

    def compose(self, identity: str, relation: str, target: str) -> MetaObject:
        """Add a governed relationship from one thing to another (new version).

        A relationship changes content, so composition produces a superseding version —
        the lineage of who-related-to-whom-when is itself append-only and auditable.
        """
        current = self._registry.get(identity)
        related = current.with_relationship(relation, target)
        if related is current:
            return current
        bumped = related.evolve(
            Version(current.version.major, current.version.minor, current.version.patch + 1),
            relationships=related.relationships,
        )
        return self._registry.register(bumped)

    # -- Universal Governance / Validation / Certification / Trace -------------

    def govern(self, candidate: MetaObject) -> GovernanceDecision:
        """Return the governance decision for a candidate without admitting it."""
        return self.governance.evaluate(candidate, self._registry)

    def validate(self) -> bool:
        """Validate the whole kernel state (audit chain + invariants)."""
        return self._registry.verify()

    def trace(self, identity: str) -> dict[str, object]:
        """Return the traceable lineage of a registered thing."""
        return self._registry.trace(identity)

    def certify(self) -> dict[str, object]:
        """Emit a deterministic self-certification of kernel integrity."""
        valid = self.validate()
        return {
            "subject": "UniversalMetaKernel",
            "kernel_version": self.version,
            "determination": "CERTIFIED" if valid else "REJECTED",
            "audit_head": self._registry.audit_head,
            "identities": self._registry.count(),
            "metatypes": self._registry.count() and len(self.metatypes()),
            "snapshot_hash": _snapshot_hash(self._registry),
        }

    # -- Universal self-description --------------------------------------------

    def describe(self) -> dict[str, object]:
        """A deterministic, machine-readable description of the kernel itself."""
        return {
            "kernel": "UCOS Universal Meta-Kernel",
            "version": self.version,
            "root_metatype": META_TYPE_ROOT,
            "founding_metatypes": [mt.natural_key for mt in self.metatypes()],
            "governance": self.governance.describe(),
            "identities": self._registry.count(),
            "versions": self._registry.count_versions(),
            "open_world": True,
        }


def _snapshot_hash(registry: UniversalRegistry) -> str:
    from engine.kernel.identity import content_digest

    return content_digest(registry.snapshot())


__all__ = ["MetaKernel"]
