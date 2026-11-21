"""The Meta-Civilization Operating System — the platform that generates platforms.

:class:`MetaCivilizationPlatform` binds the three components of this layer over **one**
Universal Meta-Kernel:

    * the :class:`~engine.civilization.dimensions.DimensionRegistry` — the open dimension
      space every generated system is contextualized within;
    * the :class:`~engine.civilization.composition.CompositionPlanner` — execution derived
      from declarations rather than a pipeline; and
    * the :class:`~engine.civilization.generation.ConstitutionalGenerator` — the stratum
      chain by which a constitutional operating system is generated.

One kernel, not three: the kernel is the single admission authority, the single identity
authority, the single governance authority and the single audit journal. This facade
therefore adds no registry, no identity scheme and no second source of truth. It is the
Universal Engineering Platform surface — a *realization layer*, exactly as the Universal
Provider Framework is, and it holds **no authority of its own**: every determination it
reports is derived from kernel state.

Authority: NONE. The kernel governs; this layer composes.
"""

from __future__ import annotations

from engine.civilization.composition import CompositionPlan, CompositionPlanner
from engine.civilization.dimensions import DimensionRegistry
from engine.civilization.generation import ConstitutionalGenerator, GenerationResult
from engine.kernel.identity import content_digest
from engine.kernel.kernel import MetaKernel


class MetaCivilizationPlatform:
    """The Meta-Civilization Operating System: dimensions, composition and generation."""

    __slots__ = ("_kernel", "_dimensions", "_composition", "_generation")

    version = "1.0.0"

    #: This layer holds no constitutional authority. It derives everything from the kernel.
    authority = "NONE"

    def __init__(self, *, kernel: MetaKernel | None = None) -> None:
        self._kernel = kernel if kernel is not None else MetaKernel()
        # Construction order is irrelevant to the resulting kernel state: the shared facet
        # vocabulary is seeded by one idempotent, order-independent function.
        self._dimensions = DimensionRegistry(kernel=self._kernel)
        self._composition = CompositionPlanner(kernel=self._kernel)
        self._generation = ConstitutionalGenerator(kernel=self._kernel)

    # -- component access ------------------------------------------------------

    @property
    def kernel(self) -> MetaKernel:
        """The single Universal Meta-Kernel this platform derives from."""
        return self._kernel

    @property
    def dimensions(self) -> DimensionRegistry:
        """The open dimension space."""
        return self._dimensions

    @property
    def composition(self) -> CompositionPlanner:
        """The declarative composition planner."""
        return self._composition

    @property
    def generation(self) -> ConstitutionalGenerator:
        """The constitutional generator."""
        return self._generation

    # -- the one operation that spans all three --------------------------------

    def realize(
        self,
        blueprint: str,
        *,
        strategy: str | None = None,
    ) -> tuple[GenerationResult, CompositionPlan]:
        """Generate a constitutional operating system and derive its composition plan.

        The blueprint's declared dimensions become the composition context and its declared
        capabilities become the composition targets, so the generated system and the plan
        that realizes it come from the same declaration. A blueprint declaring no capability
        has nothing to compose and is refused rather than given an invented plan — generate
        it through :meth:`ConstitutionalGenerator.generate` if that is what is wanted.
        """
        declared = self._generation.blueprint(blueprint)
        result = self._generation.generate(blueprint)
        self._generation.verify_derivation(result)
        capabilities = tuple(declared.attributes.get("capabilities", ()))
        context = tuple(declared.attributes.get("dimensions", ()))
        policies = tuple(
            policy
            for key in capabilities
            for policy in self._composition.capability(key).attributes.get("policies", ())
        )
        plan = self._composition.plan(
            capabilities,
            context=context,
            policies=policies,
            strategy=strategy if strategy is not None else "dependency-order",
        )
        return result, plan

    # -- validation + certification + description ------------------------------

    def validate(self) -> bool:
        """Validate every component and the kernel audit chain beneath them."""
        return (
            self._dimensions.validate()
            and self._composition.validate()
            and self._generation.validate()
            and self._kernel.validate()
        )

    def snapshot_hash(self) -> str:
        """A deterministic hash over the whole platform state."""
        return content_digest(
            {
                "kernel": self._kernel.registry.snapshot(),
                "dimensions": self._dimensions.describe(),
                "composition": self._composition.describe(),
                "generation": self._generation.describe(),
            }
        )

    def certify(self) -> dict[str, object]:
        """Emit a deterministic self-certification of the platform."""
        valid = self.validate()
        return {
            "subject": "MetaCivilizationOperatingSystem",
            "version": self.version,
            "authority": self.authority,
            "determination": "CERTIFIED" if valid else "REJECTED",
            "kernel_determination": self._kernel.certify()["determination"],
            "audit_head": self._kernel.registry.audit_head,
            "dimensions": len(self._dimensions.dimensions()),
            "capabilities": len(self._composition.capabilities()),
            "operating_systems": len(self._generation.operating_systems()),
            "strata": len(self._generation.strata()),
            "snapshot_hash": self.snapshot_hash(),
        }

    def describe(self) -> dict[str, object]:
        """A deterministic, machine-readable description of the platform."""
        return {
            "platform": "UCOS Meta-Civilization Operating System",
            "version": self.version,
            "authority": self.authority,
            "derives_from": {
                "kernel": self._kernel.describe()["kernel"],
                "kernel_version": self._kernel.version,
                "kernel_root": self._generation.kernel_root(),
            },
            "dimensions": self._dimensions.describe(),
            "composition": self._composition.describe(),
            "generation": self._generation.describe(),
            "open_world": True,
            "upper_limit": None,
        }

    def trace(self, identity: str) -> dict[str, object]:
        """The traceable lineage of anything this platform has registered."""
        return self._kernel.trace(identity)


__all__ = ["MetaCivilizationPlatform"]
