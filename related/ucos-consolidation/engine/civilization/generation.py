"""The Constitutional Generation Model — the architecture generates systems.

Generation proceeds through an ordered chain of **strata**. The chain shipped as DATA in
:data:`GENERATION_STRATA` is the ratified one —

    Universal Meta Kernel → Meta-Civilization OS → Constitutional Blueprint →
    Domain Constitutional Operating System → Nucleus → Universe → Capability →
    Component → Configured Solution

— but the chain is not the architecture. A stratum is a registered kernel meta-type ordered
by a declared predecessor, so inserting, refining or extending a stratum is a registration
(:meth:`ConstitutionalGenerator.register_stratum`), never a change to this module. Unlimited
decomposition and unlimited composition are the same freedom read in two directions.

A **constitutional operating system** is likewise a registered kernel meta-type. That is why
no list of operating systems appears anywhere in this layer: a domain operating system is
admitted by registering it, and one nobody has named yet is admitted the same way as one that
already exists. The catalogue is open by construction, not by an enumeration someone
remembered to extend.

Every generated record carries exactly one
:data:`~engine.civilization.metatypes.DERIVES_FROM` edge, and the chain roots at the kernel's
own reflective root meta-type. That is the executable form of *nothing bypasses the Meta
Kernel*: :meth:`ConstitutionalGenerator.verify_derivation` walks the chain and refuses a
result whose authority does not trace back to the kernel.

Generation is idempotent: generating an already-generated blueprint returns the existing
lineage rather than admitting the same knowledge twice.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.civilization.errors import (
    BlueprintUnknownError,
    DerivationError,
    StratumOrderError,
    StratumUnknownError,
)
from engine.civilization.metatypes import (
    BLUEPRINT_NS,
    DERIVES_FROM,
    GENERATION_NS,
    OPERATING_SYSTEM_META_NS,
    OPERATING_SYSTEM_ROLE,
    STRATUM_META_NS,
    STRATUM_ROLE,
)
from engine.civilization.seeding import seed_facets
from engine.kernel.governance import Constraint
from engine.kernel.identity import content_digest
from engine.kernel.kernel import MetaKernel
from engine.kernel.meta import MetaObject

#: The ratified generation chain, as DATA: (key, name, predecessor, description). The
#: predecessor of the first stratum is ``None`` — it is the stratum that derives directly
#: from the Universal Meta-Kernel. Editing this table is one way to change the chain;
#: registering a stratum at runtime is the other, and it requires no edit at all.
GENERATION_STRATA: tuple[tuple[str, str, str | None, str], ...] = (
    (
        "MetaKernelStratum",
        "Universal Meta Kernel",
        None,
        "The highest constitutional authority; everything below derives from it.",
    ),
    (
        "MetaCivilizationStratum",
        "Meta-Civilization Operating System",
        "MetaKernelStratum",
        "The layer that generates constitutional operating systems.",
    ),
    (
        "BlueprintStratum",
        "Constitutional Blueprint",
        "MetaCivilizationStratum",
        "The declaration from which a constitutional operating system is generated.",
    ),
    (
        "OperatingSystemStratum",
        "Domain Constitutional Operating System",
        "BlueprintStratum",
        "A generated, self-governing constitutional operating system for a domain.",
    ),
    (
        "NucleusStratum",
        "Nucleus",
        "OperatingSystemStratum",
        "The complete constitutional universe of exactly one canonical concept.",
    ),
    (
        "UniverseStratum",
        "Universe",
        "NucleusStratum",
        "A governed composition of complete nuclei plus configuration.",
    ),
    (
        "CapabilityStratum",
        "Capability",
        "UniverseStratum",
        "A declared, discoverable, composable unit of realizable behaviour.",
    ),
    (
        "ComponentStratum",
        "Component",
        "CapabilityStratum",
        "A realization of a capability within a universe.",
    ),
    (
        "SolutionStratum",
        "Configured Solution",
        "ComponentStratum",
        "A configuration of components; a delivered system.",
    ),
)


@dataclass(frozen=True)
class GenerationResult:
    """The lineage produced by generating one constitutional blueprint."""

    blueprint: str
    operating_system: str
    strata: tuple[str, ...]
    lineage: tuple[str, ...]
    root: str

    def records(self) -> dict[str, str]:
        """Stratum key -> minted identity, in chain order."""
        return dict(zip(self.strata, self.lineage, strict=True))

    def body(self) -> dict[str, object]:
        """The substantive result body (used for the derivation hash)."""
        return {
            "blueprint": self.blueprint,
            "operating_system": self.operating_system,
            "strata": list(self.strata),
            "lineage": list(self.lineage),
            "root": self.root,
        }

    def derivation_hash(self) -> str:
        """SHA-256 over the result body — a deterministic derivation identity."""
        return content_digest(self.body())

    def to_dict(self) -> dict[str, object]:
        """A deterministic, serialisable rendering of the result."""
        payload = self.body()
        payload["depth"] = len(self.strata)
        payload["derivation_hash"] = self.derivation_hash()
        return payload


class ConstitutionalGenerator:
    """Generates constitutional operating systems from declared blueprints."""

    __slots__ = ("_kernel",)

    def __init__(self, *, kernel: MetaKernel | None = None, seed: bool = True) -> None:
        self._kernel = kernel if kernel is not None else MetaKernel()
        seed_facets(self._kernel)
        self._bind_governance()
        if seed:
            self._seed_strata()

    # -- seeding + governance --------------------------------------------------

    def _seed_strata(self) -> None:
        """Register the ratified generation chain as kernel meta-types (DATA)."""
        for key, name, after, description in GENERATION_STRATA:
            if not self._stratum_registered(key):
                self.register_stratum(key, name=name, after=after, description=description)

    def _bind_governance(self) -> None:
        """Bind the derivation invariant into the kernel's open admission policy."""
        gov = self._kernel.governance
        if "generation-derivation-rooted" not in set(gov.admission.constraint_names()):
            gov.register_constraint(
                Constraint("generation-derivation-rooted", self._check_derivation)
            )

    def _check_derivation(self, candidate: MetaObject, _view: Any) -> tuple[bool, str]:
        """Every generated record declares exactly one derivation edge."""
        if candidate.namespace != GENERATION_NS:
            return True, ""
        edges = candidate.related(DERIVES_FROM)
        if len(edges) == 1:
            return True, ""
        return False, f"generated record declares {len(edges)} derivation edges, expected 1"

    # -- the kernel root -------------------------------------------------------

    @property
    def kernel(self) -> MetaKernel:
        """The kernel this generator admits through — there is no second registry."""
        return self._kernel

    def kernel_root(self) -> str:
        """The identity of the kernel's reflective root meta-type.

        This is the single point every generated lineage roots at, so the claim that nothing
        bypasses the Meta-Kernel is a graph property rather than an assurance.
        """
        for metatype in self._kernel.metatypes():
            if metatype.is_reflective_root:
                return metatype.identity
        raise DerivationError("the kernel has no reflective root, so nothing may derive")

    # -- strata ----------------------------------------------------------------

    def register_stratum(
        self,
        key: str,
        *,
        name: str = "",
        after: str | None = None,
        description: str = "",
    ) -> MetaObject:
        """Admit a generation stratum, ordered after ``after`` (or first when ``None``)."""
        if after is not None and not self._stratum_registered(after):
            raise StratumUnknownError(
                "cannot order a stratum after an unregistered stratum",
                stratum=key,
                after=after,
            )
        return self._kernel.register_metatype(
            key,
            name=name or key,
            description=description or f"Generation stratum {key}.",
            namespace=STRATUM_META_NS,
            attributes={"role": STRATUM_ROLE, "after": after},
        )

    def _stratum_registered(self, key: str) -> bool:
        return any(stratum.natural_key == key for stratum in self._stratum_objects())

    def _stratum_objects(self) -> tuple[MetaObject, ...]:
        return self._kernel.discover(namespace=STRATUM_META_NS)

    def strata(self) -> tuple[str, ...]:
        """Every registered stratum, in declared chain order.

        Raises :class:`StratumOrderError` when the declarations do not form a single chain —
        no order is invented from an ambiguous declaration.
        """
        successors: dict[str | None, list[str]] = {}
        for stratum in self._stratum_objects():
            successors.setdefault(stratum.attributes.get("after"), []).append(stratum.natural_key)
        if not successors:
            return ()
        ordered: list[str] = []
        cursor: str | None = None
        while cursor in successors:
            candidates = successors.pop(cursor)
            if len(candidates) != 1:
                raise StratumOrderError(
                    "stratum order is ambiguous: several strata declare the same predecessor",
                    after=cursor,
                    candidates=sorted(candidates),
                )
            cursor = candidates[0]
            ordered.append(cursor)
        if successors:
            raise StratumOrderError(
                "stratum order is broken: a stratum declares an unreachable predecessor",
                unreachable=sorted(successors),
            )
        return tuple(ordered)

    # -- operating systems (open catalogue) ------------------------------------

    def register_operating_system(
        self,
        key: str,
        *,
        name: str = "",
        description: str = "",
        attributes: Mapping[str, Any] | None = None,
    ) -> MetaObject:
        """Admit a constitutional operating system. The catalogue is never finite."""
        attrs: dict[str, Any] = dict(attributes or {})
        attrs["role"] = OPERATING_SYSTEM_ROLE
        return self._kernel.register_metatype(
            key,
            name=name or key,
            description=description or f"Constitutional operating system {key}.",
            namespace=OPERATING_SYSTEM_META_NS,
            attributes=attrs,
        )

    def operating_systems(self) -> tuple[str, ...]:
        """Every registered constitutional operating system, ordered."""
        found = self._kernel.discover(namespace=OPERATING_SYSTEM_META_NS)
        return tuple(sorted(os_type.natural_key for os_type in found))

    # -- blueprints ------------------------------------------------------------

    def register_blueprint(
        self,
        key: str,
        *,
        operating_system: str,
        name: str = "",
        dimensions: Sequence[str] = (),
        capabilities: Sequence[str] = (),
        attributes: Mapping[str, Any] | None = None,
    ) -> MetaObject:
        """Declare the blueprint from which a constitutional operating system is generated."""
        if operating_system not in self.operating_systems():
            raise BlueprintUnknownError(
                "blueprint names an unregistered constitutional operating system",
                blueprint=key,
                operating_system=operating_system,
            )
        attrs: dict[str, Any] = dict(attributes or {})
        attrs["operating_system"] = operating_system
        attrs["dimensions"] = sorted(dimensions)
        attrs["capabilities"] = sorted(capabilities)
        return self._kernel.register_object(
            metatype="ConstitutionalBlueprint",
            natural_key=key,
            namespace=BLUEPRINT_NS,
            name=name or key,
            attributes=attrs,
        )

    def blueprint(self, key: str) -> MetaObject:
        """The declaration of a registered blueprint."""
        for declared in self.blueprints():
            if declared.natural_key == key:
                return declared
        raise BlueprintUnknownError("blueprint is not registered", blueprint=key)

    def blueprints(self) -> tuple[MetaObject, ...]:
        """Every registered blueprint, ordered by natural key."""
        found = self._kernel.discover(namespace=BLUEPRINT_NS)
        return tuple(sorted(found, key=lambda o: o.natural_key))

    # -- generation ------------------------------------------------------------

    def generate(self, blueprint_key: str) -> GenerationResult:
        """Generate the full stratum lineage for a blueprint, rooted at the kernel."""
        declared = self.blueprint(blueprint_key)
        operating_system = str(declared.attributes["operating_system"])
        strata = self.strata()
        if not strata:
            raise StratumOrderError("no generation stratum is registered, so nothing generates")
        root = self.kernel_root()
        previous = root
        lineage: list[str] = []
        for stratum in strata:
            record = self._stratum_record(blueprint_key, stratum)
            if record is None:
                record = self._kernel.register_object(
                    metatype=stratum,
                    natural_key=f"{blueprint_key}:{stratum}",
                    namespace=GENERATION_NS,
                    name=f"{declared.name} · {stratum}",
                    attributes={
                        "blueprint": blueprint_key,
                        "operating_system": operating_system,
                        "stratum": stratum,
                        "dimensions": list(declared.attributes.get("dimensions", ())),
                        "capabilities": list(declared.attributes.get("capabilities", ())),
                    },
                    relationships=({"relation": DERIVES_FROM, "target": previous},),
                )
            previous = record.identity
            lineage.append(record.identity)
        return GenerationResult(
            blueprint=blueprint_key,
            operating_system=operating_system,
            strata=strata,
            lineage=tuple(lineage),
            root=root,
        )

    def _stratum_record(self, blueprint_key: str, stratum: str) -> MetaObject | None:
        """An already-generated record for this blueprint and stratum, if any."""
        natural_key = f"{blueprint_key}:{stratum}"
        for record in self.generated():
            if record.natural_key == natural_key:
                return record
        return None

    def generated(self, *, blueprint: str | None = None) -> tuple[MetaObject, ...]:
        """Every generated stratum record, optionally filtered by blueprint."""
        found = self._kernel.discover(namespace=GENERATION_NS)
        if blueprint is not None:
            found = tuple(r for r in found if r.attributes.get("blueprint") == blueprint)
        return tuple(sorted(found, key=lambda o: o.natural_key))

    def verify_derivation(self, result: GenerationResult) -> bool:
        """Walk the lineage and prove it roots at the kernel's reflective root.

        Raises :class:`DerivationError` on a broken chain: an unrooted lineage is a
        constitutional violation, not a warning.
        """
        expected = result.root
        for identity in result.lineage:
            record = self._kernel.registry.get(identity)
            edges = record.related(DERIVES_FROM)
            if edges != (expected,):
                raise DerivationError(
                    "generated record does not derive from its declared predecessor",
                    identity=identity,
                    expected=expected,
                    found=list(edges),
                )
            expected = identity
        if result.root != self.kernel_root():
            raise DerivationError(
                "lineage does not root at the kernel reflective root",
                root=result.root,
            )
        return True

    # -- validation + description ----------------------------------------------

    def validate(self) -> bool:
        """True iff every generated record derives from a registered predecessor."""
        known = {record.identity for record in self.generated()} | {self.kernel_root()}
        for record in self.generated():
            edges = record.related(DERIVES_FROM)
            if len(edges) != 1 or edges[0] not in known:
                return False
        return self._kernel.validate()

    def describe(self) -> dict[str, object]:
        """A deterministic, machine-readable description of the generation model."""
        return {
            "subject": "ConstitutionalGenerationModel",
            "strata": list(self.strata()),
            "depth": len(self.strata()),
            "operating_systems": list(self.operating_systems()),
            "blueprints": [b.natural_key for b in self.blueprints()],
            "generated_records": len(self.generated()),
            "kernel_root": self.kernel_root(),
            "finite_catalogue": False,
            "upper_limit": None,
        }


__all__ = ["ConstitutionalGenerator", "GenerationResult", "GENERATION_STRATA"]
