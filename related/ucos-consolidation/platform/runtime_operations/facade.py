"""EC2-TASK-000165 — Runtime Operations EC-1 Façade (EC2-EPIC-012).

The **L4 execution façade** — the single component that invokes the certified EC-1
Runtime Assembly engine (Program §4.2: "L4 Execution … the only component that invokes
EC-1 … calls EC-1's published APIs … ``engine.runtime``"). It consumes ``engine.runtime``
**by reference**: it binds the published, versioned
:data:`~platform.runtime_operations.contracts.ENGINE_RUNTIME_ASSEMBLE_CONTRACT`
(``engine.runtime.assemble`` v1) and
:data:`~platform.runtime_operations.contracts.ENGINE_RUNTIME_DEPLOY_CONTRACT`
(``engine.runtime.deploy`` v1, both present in
:data:`~platform.foundation.contracts.ENGINE_CONTRACTS`) and invokes the certified,
deterministic :func:`engine.runtime.deploy.descriptor` /
:func:`engine.runtime.deploy.rollback` factories **read-only** over an already-assembled
:class:`~engine.runtime.assembly.RuntimeUnit` to obtain the authoritative
:class:`~engine.runtime.deploy.DeploymentDescriptor` and
:class:`~engine.runtime.deploy.RollbackDescriptor`.

Because those factories are **pure, deterministic functions** of the runtime unit
(IMP-007 §5), this reproduction is byte-for-byte identical to the engine's own output —
the mechanism by which the runtime guarantees fidelity (P6). The façade **implements no
deployment logic** and **redefines no descriptor format, rollback strategy, disclosure, or
reversibility rule** (TP-01); it holds no engine of its own and delegates entirely. The
actual runtime execution remains inside EC-1 / the downstream runtime platform (IMP-008);
this façade generates deployable *definitions* only. It mutates nothing, writes nothing to
the corpus (DP-03), and performs no I/O.
"""

from __future__ import annotations

from platform.foundation.contracts import ENGINE_CONTRACTS, ContractRef, content_hash
from platform.runtime_operations.contracts import (
    ENGINE_RUNTIME_ASSEMBLE_CONTRACT,
    ENGINE_RUNTIME_DEPLOY_CONTRACT,
    RuntimeUnitReference,
)
from platform.runtime_operations.errors import RuntimeDescriptorError, RuntimeFidelityError

from engine.runtime.assembly import RuntimeUnit
from engine.runtime.deploy import (
    DeploymentDescriptor,
    RollbackDescriptor,
)
from engine.runtime.deploy import (
    descriptor as engine_deployment_descriptor,
)
from engine.runtime.deploy import (
    rollback as engine_rollback_descriptor,
)
from engine.runtime.errors import DeploymentError, DisclosureError

#: The certified EC-1 runtime contract references the façade binds to (by reference).
RUNTIME_ENGINE_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ref
    for ref in ENGINE_CONTRACTS
    if ref.name in {ENGINE_RUNTIME_ASSEMBLE_CONTRACT, ENGINE_RUNTIME_DEPLOY_CONTRACT}
)


class RuntimeFacade:
    """The read-only EC-1 runtime façade (consumes ``engine.runtime`` by reference).

    Stateless: it holds no engine and no runtime state, delegating every descriptor
    generation to the certified, deterministic EC-1 factories. It never assembles a unit
    (assembly is upstream EC-1 work consumed by reference) and implements no deployment.
    """

    __slots__ = ()

    @property
    def engine_contracts(self) -> tuple[ContractRef, ...]:
        """The certified EC-1 runtime contract references (by reference)."""
        return RUNTIME_ENGINE_CONTRACTS

    @property
    def assemble_contract(self) -> str:
        """The certified EC-1 assembly contract name this façade binds to."""
        return ENGINE_RUNTIME_ASSEMBLE_CONTRACT

    @property
    def deploy_contract(self) -> str:
        """The certified EC-1 deploy contract name this façade binds to."""
        return ENGINE_RUNTIME_DEPLOY_CONTRACT

    def unit_reference(self, unit: RuntimeUnit) -> RuntimeUnitReference:
        """Project a read-only reference to an assembled runtime unit (P6)."""
        if not isinstance(unit, RuntimeUnit):
            raise RuntimeDescriptorError("unit_reference requires a RuntimeUnit")
        return RuntimeUnitReference.from_unit(unit)

    def deployment_descriptor(
        self, unit: RuntimeUnit, *, environment: str | None = None
    ) -> DeploymentDescriptor:
        """Reproduce the certified :class:`DeploymentDescriptor` for ``unit`` (read-only).

        Delegates to :func:`engine.runtime.deploy.descriptor`; it implements no deployment.
        Raises :class:`RuntimeDescriptorError` if the certified engine refuses the unit
        (missing disclosure, unpinned package, or empty dependency closure).
        """
        if not isinstance(unit, RuntimeUnit):
            raise RuntimeDescriptorError("deployment_descriptor requires a RuntimeUnit")
        try:
            return engine_deployment_descriptor(unit, environment=environment)
        except (DeploymentError, DisclosureError) as exc:
            raise RuntimeDescriptorError(
                "certified engine refused deployment descriptor generation",
                runtime_id=unit.runtime_id,
                detail=str(exc),
            ) from exc

    def rollback_descriptor(
        self,
        unit: RuntimeUnit,
        *,
        previous: RuntimeUnit | None = None,
        environment: str | None = None,
    ) -> RollbackDescriptor:
        """Reproduce the certified reversible :class:`RollbackDescriptor` for ``unit`` (IP-08).

        Delegates to :func:`engine.runtime.deploy.rollback`; it implements no rollback.
        When ``previous`` is supplied, the exact prior pinned state to revert to is
        recorded by the certified engine.
        """
        if not isinstance(unit, RuntimeUnit):
            raise RuntimeDescriptorError("rollback_descriptor requires a RuntimeUnit")
        if previous is not None and not isinstance(previous, RuntimeUnit):
            raise RuntimeDescriptorError("rollback previous must be a RuntimeUnit when provided")
        try:
            return engine_rollback_descriptor(unit, previous=previous, environment=environment)
        except (DeploymentError, DisclosureError) as exc:
            raise RuntimeDescriptorError(
                "certified engine refused rollback descriptor generation",
                runtime_id=unit.runtime_id,
                detail=str(exc),
            ) from exc

    def verify_deployment_fidelity(
        self,
        descriptor: DeploymentDescriptor,
        unit: RuntimeUnit,
        *,
        environment: str | None = None,
    ) -> bool:
        """True iff re-generating the deployment descriptor reproduces ``descriptor`` (P6)."""
        if not isinstance(descriptor, DeploymentDescriptor):
            raise RuntimeFidelityError("verify_deployment_fidelity requires a DeploymentDescriptor")
        reproduced = self.deployment_descriptor(unit, environment=environment)
        return content_hash(reproduced.to_dict()) == content_hash(descriptor.to_dict())

    def verify_rollback_fidelity(
        self,
        descriptor: RollbackDescriptor,
        unit: RuntimeUnit,
        *,
        previous: RuntimeUnit | None = None,
        environment: str | None = None,
    ) -> bool:
        """True iff re-generating the rollback descriptor reproduces ``descriptor`` (P6)."""
        if not isinstance(descriptor, RollbackDescriptor):
            raise RuntimeFidelityError("verify_rollback_fidelity requires a RollbackDescriptor")
        reproduced = self.rollback_descriptor(unit, previous=previous, environment=environment)
        return content_hash(reproduced.to_dict()) == content_hash(descriptor.to_dict())


__all__ = ["RUNTIME_ENGINE_CONTRACTS", "RuntimeFacade"]
