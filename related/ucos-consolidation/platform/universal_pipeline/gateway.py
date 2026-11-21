"""UAPF-000001 — the Universal Integration Gateway (the single admission point for work).

Nothing executes in UAPF without a gateway admission. That is the property this module
exists to make structural rather than aspirational: the runtime will not execute a unit
without a :class:`GatewayTransaction` whose authorization it can *recompute*, so bypassing
the gateway is not a rule someone might forget — it is impossible, because a caller cannot
manufacture a valid authorization without performing the same checks the gateway performs.

What a submission must satisfy
------------------------------
Four conditions, checked in a fixed order so a refusal always names the *first* thing
wrong rather than an arbitrary one:

    1. the pipeline version is **registered** (an unregistered pipeline does not exist);
    2. the principal holds every permission the pipeline's security declaration requires;
    3. governance **approves** the submission, when a governance engine is attached;
    4. the unit id is well-formed and the inputs are a mapping.

A refusal is an **error, not a value** (see the module docstring of
:mod:`platform.universal_pipeline.errors`): the refusal is recorded on the bus first — so
the attempt is auditable — and then raised, so no caller can proceed past it by ignoring a
return value. Consequently a :class:`GatewayTransaction` that exists is always an admitted
one, which is why the runtime can treat its mere presence as meaningful.

Idempotence
-----------
A transaction is derived purely from what it admits, so re-submitting the same work yields
an *equal* transaction rather than a second one (AIF-L13 idempotent retry). There is no
counter, no clock and no nonce, which is also what makes the authorization recomputable.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.errors import PipelineGatewayError
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.governance import PipelineGovernance
from platform.universal_pipeline.identity import Identity, mint
from platform.universal_pipeline.registry import PipelineRegistry, PipelineRegistryEntry
from typing import Any


@dataclass(frozen=True, slots=True)
class GatewayTransaction:
    """An admitted submission and the authorization that lets it execute — exactly once.

    ``authorization`` is a content hash over the transaction's own core, so it can be
    recomputed by the runtime and cannot be forged without reproducing the core; and since
    the core names the pipeline, the version, the unit and the inputs, an authorization is
    valid for *that* work and no other. Swapping in different inputs invalidates it.
    """

    pipeline_id: str
    version: str
    unit_id: str
    inputs_hash: str
    authorization: str
    permissions: tuple[str, ...] = ()
    detail: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for label, value in (
            ("pipeline id", self.pipeline_id),
            ("version", self.version),
            ("unit id", self.unit_id),
            ("inputs hash", self.inputs_hash),
            ("authorization", self.authorization),
        ):
            if not isinstance(value, str) or not value:
                raise PipelineGatewayError(f"gateway transaction {label} is required")
        if not isinstance(self.permissions, tuple):
            raise PipelineGatewayError(
                "gateway transaction permissions must be a tuple", unit_id=self.unit_id
            )
        if not isinstance(self.detail, Mapping):
            raise PipelineGatewayError(
                "gateway transaction detail must be a mapping", unit_id=self.unit_id
            )

    @property
    def identity(self) -> Identity:
        """The canonical identity of this transaction."""
        return mint("transaction", self.pipeline_id, self.version, self.unit_id, self.inputs_hash)

    @property
    def transaction_id(self) -> str:
        """The rendered transaction identity."""
        return self.identity.value

    def core(self) -> dict[str, Any]:
        """The authorized core: exactly what this authorization is valid for."""
        return {
            "pipeline_id": self.pipeline_id,
            "version": self.version,
            "unit_id": self.unit_id,
            "inputs_hash": self.inputs_hash,
            "permissions": sorted(self.permissions),
        }

    def expected_authorization(self) -> str:
        """The authorization this transaction's core actually derives."""
        return authorization_for(self.core())

    def verify(self) -> bool:
        """True iff the carried authorization matches the transaction's own core."""
        return self.authorization == self.expected_authorization()

    def require_authorized(self) -> None:
        """Fail closed unless :meth:`verify` holds.

        Raises:
            PipelineGatewayError: if the authorization does not match the core — i.e. the
                transaction was constructed by hand or its core was altered after
                admission. This is the check that makes bypassing the gateway impossible.
        """
        if not self.verify():
            raise PipelineGatewayError(
                "gateway authorization does not match the transaction (bypass attempt)",
                unit_id=self.unit_id,
                pipeline_id=self.pipeline_id,
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "pipeline_id": self.pipeline_id,
            "version": self.version,
            "unit_id": self.unit_id,
            "inputs_hash": self.inputs_hash,
            "authorization": self.authorization,
            "permissions": sorted(self.permissions),
            "detail": dict(self.detail),
        }


def authorization_for(core: Mapping[str, Any]) -> str:
    """The single authorization-derivation rule: a content hash over the admitted core.

    Kept as a module function rather than a method so the gateway (which mints) and the
    transaction (which verifies) provably use the same rule — there is only one.
    """
    return content_hash({"uapf.authorization": dict(core)})


def inputs_hash_for(inputs: Mapping[str, Any] | None) -> str:
    """The content hash binding a submission's inputs into its authorization.

    Raises:
        PipelineGatewayError: if ``inputs`` is not a mapping.
    """
    if inputs is not None and not isinstance(inputs, Mapping):
        raise PipelineGatewayError("submission inputs must be a mapping")
    return content_hash(dict(inputs or {}))


class UniversalPipelineGateway:
    """The one door into execution. Every unit of work enters through :meth:`submit`.

    Composes the registry (does this pipeline exist?), the security declaration (may this
    principal run it?) and governance (do the obligations permit it?). It executes nothing
    itself: admission and execution are separate acts, so the thing that decides is not the
    thing that runs.
    """

    __slots__ = ("_registry", "_governance", "_bus", "_admitted")

    def __init__(
        self,
        registry: PipelineRegistry,
        *,
        governance: PipelineGovernance | None = None,
        bus: PipelineEventBus | None = None,
    ) -> None:
        if not isinstance(registry, PipelineRegistry):
            raise PipelineGatewayError("gateway requires a PipelineRegistry")
        if governance is not None and not isinstance(governance, PipelineGovernance):
            raise PipelineGatewayError("governance must be a PipelineGovernance")
        if bus is not None and not isinstance(bus, PipelineEventBus):
            raise PipelineGatewayError("bus must be a PipelineEventBus")
        self._registry = registry
        self._governance = governance
        self._bus = bus
        self._admitted: dict[str, GatewayTransaction] = {}

    @property
    def admitted(self) -> tuple[GatewayTransaction, ...]:
        """Every admitted transaction, ordered by unit id (deterministic)."""
        return tuple(self._admitted[unit_id] for unit_id in sorted(self._admitted))

    def __len__(self) -> int:
        return len(self._admitted)

    def submit(
        self,
        pipeline_id: str,
        unit_id: str,
        *,
        version: str | None = None,
        inputs: Mapping[str, Any] | None = None,
        permissions: Iterable[str] = (),
        evidence: Mapping[str, Any] | None = None,
    ) -> GatewayTransaction:
        """Admit one unit of work against ``pipeline_id`` and authorize its execution.

        ``evidence`` discharges governance obligations; ``inputs`` are the values the
        stages will receive. They are separate because evidence is *about* the submission
        while inputs are *for* it, and binding governance to the stage inputs would let a
        pipeline discharge its own obligations by declaring a default.

        Raises:
            PipelineGatewayError: if the unit id is malformed, the pipeline version is not
                registered, or the principal lacks a required permission.
            PipelineGovernanceError: if governance refuses the submission.
        """
        if not isinstance(unit_id, str) or not unit_id:
            raise PipelineGatewayError("submission unit id is required", pipeline_id=pipeline_id)
        resolved_permissions = tuple(sorted(set(permissions)))
        entry = self._require_registered(pipeline_id, version, unit_id)
        self._require_permissions(entry, unit_id, resolved_permissions)
        self._require_governance(entry, unit_id, evidence)
        core = {
            "pipeline_id": entry.pipeline_id,
            "version": entry.version,
            "unit_id": unit_id,
            "inputs_hash": inputs_hash_for(inputs),
            "permissions": list(resolved_permissions),
        }
        transaction = GatewayTransaction(
            pipeline_id=entry.pipeline_id,
            version=entry.version,
            unit_id=unit_id,
            inputs_hash=core["inputs_hash"],
            authorization=authorization_for(core),
            permissions=resolved_permissions,
            detail={
                "pipeline_type": entry.pipeline_type,
                "plan_fingerprint": entry.plan.fingerprint(),
                "stage_count": len(entry.definition.stages),
            },
        )
        self._admitted[unit_id] = transaction
        if self._bus is not None:
            self._bus.emit(
                "uapf.gateway.admitted", transaction.transaction_id, payload=transaction.to_dict()
            )
        return transaction

    def transaction(self, unit_id: str) -> GatewayTransaction:
        """The admitted transaction for ``unit_id``.

        Raises:
            PipelineGatewayError: if the unit was never admitted — which is exactly the
                bypass case, so it fails closed.
        """
        transaction = self._admitted.get(unit_id)
        if transaction is None:
            raise PipelineGatewayError(
                "unit was never admitted through the gateway", unit_id=unit_id
            )
        return transaction

    def is_admitted(self, unit_id: str) -> bool:
        """True iff ``unit_id`` holds an admitted transaction."""
        return unit_id in self._admitted

    # -- refusal paths ----------------------------------------------------------------

    def _refuse(self, reason: str, unit_id: str, **context: Any) -> None:
        """Record the refusal, then raise it. Recorded first so the attempt is auditable."""
        if self._bus is not None:
            self._bus.emit(
                "uapf.gateway.refused",
                unit_id,
                payload={
                    "reason": reason,
                    "unit_id": unit_id,
                    **{k: str(v) for k, v in context.items()},
                },
            )
        raise PipelineGatewayError(reason, unit_id=unit_id, **context)

    def _require_registered(
        self, pipeline_id: str, version: str | None, unit_id: str
    ) -> PipelineRegistryEntry:
        try:
            return self._registry.get(pipeline_id, version)
        except Exception as exc:
            self._refuse(
                "submission names an unregistered pipeline",
                unit_id,
                pipeline_id=pipeline_id,
                version=version or "latest",
            )
            raise AssertionError from exc  # pragma: no cover — _refuse always raises.

    def _require_permissions(
        self, entry: PipelineRegistryEntry, unit_id: str, permissions: tuple[str, ...]
    ) -> None:
        required = set(entry.definition.security.required_permissions)
        missing = sorted(required - set(permissions))
        if missing:
            self._refuse(
                "principal lacks a permission the pipeline requires",
                unit_id,
                pipeline_id=entry.pipeline_id,
                missing=missing,
            )

    def _require_governance(
        self,
        entry: PipelineRegistryEntry,
        unit_id: str,
        evidence: Mapping[str, Any] | None,
    ) -> None:
        if self._governance is None:
            return
        verdict = self._governance.evaluate(unit_id, definition=entry.definition, evidence=evidence)
        if not verdict.approved and self._bus is not None:
            self._bus.emit(
                "uapf.gateway.refused",
                unit_id,
                payload={
                    "reason": "governance refused the submission",
                    "unit_id": unit_id,
                    "undischarged": list(verdict.undischarged),
                },
            )
        self._governance.require_approved(verdict)

    # -- evidence ---------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable render of every admission (evidence)."""
        return {
            "admitted_count": len(self._admitted),
            "admitted": [transaction.to_dict() for transaction in self.admitted],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of every admission."""
        return content_hash(self.to_dict())


__all__ = [
    "GatewayTransaction",
    "UniversalPipelineGateway",
    "authorization_for",
    "inputs_hash_for",
]
