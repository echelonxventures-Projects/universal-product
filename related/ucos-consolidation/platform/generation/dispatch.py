"""EC2-TASK-000112 — Generation Request Dispatch (EC2-EPIC-007).

The **execution dispatch boundary** — the authoritative, governed handoff point
between the platform and the certified EC-1 Execution Runtime (Program §2.1 #8, PC-07,
§4.3). Generation Requests are the single seam through which generation activity
crosses from the platform into execution:

    User Interface  ──►  Generation Request  ──►  Execution Runtime
                              (this boundary)

A :class:`DispatchRecord` is an immutable, content-addressed record of a request being
handed off, bound **by reference** to the certified EC-1 execution contracts —
``engine.factory.generate``, ``engine.compiler.compile``, ``engine.runtime.assemble``,
and ``engine.determinism.reproduce`` (published as ``ENGINE_CONTRACTS`` in
``platform/foundation/contracts.py``). The boundary **records** the handoff and its
parameters read-only; it invokes no ``engine.*`` module and computes no generation
itself (P10 — the actual execution is EC2-EPIC-012 Runtime Operations, consumed by
reference). This mirrors the certified :mod:`platform.blueprints.classification`
read-only-façade precedent exactly.

The :class:`DispatchLedger` is an append-only, deterministic record surface keyed by
request id (idempotent by dispatch id, fail-closed on a conflicting handoff), so the
dispatch history is reproducible and auditable. Because a request can only reach the
Execution Runtime through a recorded dispatch, "no runtime bypass path" (§7) is a
machine-checkable invariant (the dispatch-integrity health check).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import ENGINE_CONTRACTS, ContractRef
from platform.foundation.contracts import content_hash as _content_hash
from platform.generation.errors import RequestDispatchError
from typing import Any

#: The EC-1 factory contract the dispatch boundary hands off to (read-only, ENG-CAP-06).
FACTORY_CONTRACT = "engine.factory.generate"

#: The EC-1 compiler contract bound at dispatch (read-only, ENG-CAP-02).
COMPILER_CONTRACT = "engine.compiler.compile"

#: The EC-1 runtime-assembly contract bound at dispatch (read-only, ENG-CAP-04).
RUNTIME_CONTRACT = "engine.runtime.assemble"

#: The EC-1 determinism/reproducibility contract bound at dispatch (read-only, ENG-CAP-03).
DETERMINISM_CONTRACT = "engine.determinism.reproduce"

#: The certified EC-1 contract references the dispatch boundary binds to (by reference).
DISPATCH_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ref
    for ref in ENGINE_CONTRACTS
    if ref.name in {FACTORY_CONTRACT, COMPILER_CONTRACT, RUNTIME_CONTRACT, DETERMINISM_CONTRACT}
)

#: The default execution target the dispatch boundary hands off to.
DEFAULT_EXECUTION_TARGET = RUNTIME_CONTRACT

_ALLOWED_TARGETS: frozenset[str] = frozenset(ref.name for ref in DISPATCH_CONTRACTS)


def _str_map(values: Mapping[str, str] | None, what: str) -> dict[str, str]:
    mapping = dict(values or {})
    for key, val in mapping.items():
        if not isinstance(key, str) or not key:
            raise RequestDispatchError(f"dispatch {what} keys must be non-empty strings")
        if not isinstance(val, str):
            raise RequestDispatchError(f"dispatch {what} values must be strings")
    return mapping


@dataclass(frozen=True, slots=True)
class DispatchRecord:
    """An immutable, content-addressed record of a request→execution-runtime handoff.

    Binds a request (``request_ref``) and its referenced blueprint (``blueprint_ref``)
    to the certified EC-1 execution ``engine_contracts`` (by reference) and the chosen
    ``execution_target``, carrying the ``parameters`` and ``content_hash`` handed off.
    ``dispatch_id`` is content-addressed (deterministic).
    """

    dispatch_id: str
    request_ref: str
    blueprint_ref: str
    family: BlueprintFamily
    execution_target: str
    engine_contracts: tuple[str, ...]
    content_hash: str
    parameters: Mapping[str, str]
    tick: int

    @classmethod
    def create(
        cls,
        *,
        request_ref: str,
        blueprint_ref: str,
        family: BlueprintFamily,
        content_hash: str,
        tick: int,
        execution_target: str = DEFAULT_EXECUTION_TARGET,
        parameters: Mapping[str, str] | None = None,
    ) -> DispatchRecord:
        """Build a dispatch record bound to the EC-1 execution contracts (fail-closed)."""
        if not isinstance(request_ref, str) or not request_ref:
            raise RequestDispatchError("dispatch requires a request_ref")
        if not isinstance(blueprint_ref, str) or not blueprint_ref:
            raise RequestDispatchError("dispatch requires a blueprint_ref", request_ref=request_ref)
        if not isinstance(family, BlueprintFamily):
            raise RequestDispatchError("dispatch family must be a BlueprintFamily")
        if not isinstance(content_hash, str) or not content_hash:
            raise RequestDispatchError("dispatch requires a content_hash", request_ref=request_ref)
        if not isinstance(tick, int) or isinstance(tick, bool):
            raise RequestDispatchError("dispatch tick must be an int", request_ref=request_ref)
        if execution_target not in _ALLOWED_TARGETS:
            raise RequestDispatchError(
                "dispatch execution_target must be a certified EC-1 execution contract",
                request_ref=request_ref,
                execution_target=execution_target,
            )
        params = _str_map(parameters, "parameters")
        engine_contracts = tuple(ref.name for ref in DISPATCH_CONTRACTS)
        core = {
            "request_ref": request_ref,
            "blueprint_ref": blueprint_ref,
            "family": family.value,
            "execution_target": execution_target,
            "engine_contracts": list(engine_contracts),
            "content_hash": content_hash,
            "parameters": {k: params[k] for k in sorted(params)},
            "tick": tick,
        }
        return cls(
            dispatch_id=f"UCOS-GDSP-{_content_hash(core)[:16]}",
            request_ref=request_ref,
            blueprint_ref=blueprint_ref,
            family=family,
            execution_target=execution_target,
            engine_contracts=engine_contracts,
            content_hash=content_hash,
            parameters=params,
            tick=tick,
        )

    def handoff_edge(self) -> dict[str, Any]:
        """The explicit UI→Request→Execution-Runtime handoff edge (audit evidence)."""
        return {
            "dispatch_id": self.dispatch_id,
            "boundary": "generation-request-dispatch",
            "request": {"request_ref": self.request_ref, "content_hash": self.content_hash},
            "blueprint": {"blueprint_ref": self.blueprint_ref, "family": self.family.value},
            "execution": {
                "target": self.execution_target,
                "engine_contracts": list(self.engine_contracts),
            },
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "dispatch_id": self.dispatch_id,
            "request_ref": self.request_ref,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "execution_target": self.execution_target,
            "engine_contracts": list(self.engine_contracts),
            "content_hash": self.content_hash,
            "parameters": {k: self.parameters[k] for k in sorted(self.parameters)},
            "tick": self.tick,
        }

    def fingerprint(self) -> str:
        return _content_hash(self.to_dict())


class DispatchLedger:
    """A deterministic, append-only ledger of request→runtime dispatch records (by reference)."""

    __slots__ = ("_by_request", "_index")

    def __init__(self) -> None:
        self._by_request: dict[str, DispatchRecord] = {}
        self._index: dict[str, str] = {}  # dispatch_id -> request_ref

    def record(self, dispatch: DispatchRecord) -> DispatchRecord:
        """Record a dispatch handoff (idempotent by id; fail-closed on conflict).

        Re-recording the identical dispatch returns the stored entry. Recording a
        *different* dispatch for a request that already has one is refused (a request is
        handed off exactly once; append-only).
        """
        if not isinstance(dispatch, DispatchRecord):
            raise RequestDispatchError("only a DispatchRecord may be recorded")
        existing = self._by_request.get(dispatch.request_ref)
        if existing is not None:
            if existing.dispatch_id == dispatch.dispatch_id:
                return existing
            raise RequestDispatchError(
                "request already has a distinct dispatch recorded",
                request_ref=dispatch.request_ref,
            )
        self._by_request[dispatch.request_ref] = dispatch
        self._index[dispatch.dispatch_id] = dispatch.request_ref
        return dispatch

    def __contains__(self, request_ref: str) -> bool:
        return request_ref in self._by_request

    def __len__(self) -> int:
        return len(self._by_request)

    def has(self, request_ref: str) -> bool:
        """True iff a dispatch is recorded for ``request_ref``."""
        return request_ref in self._by_request

    def get(self, request_ref: str) -> DispatchRecord:
        """Resolve the dispatch of a request (fail-closed on absent)."""
        dispatch = self._by_request.get(request_ref)
        if dispatch is None:
            raise RequestDispatchError("no dispatch recorded for request", request_ref=request_ref)
        return dispatch

    def by_dispatch_id(self, dispatch_id: str) -> DispatchRecord:
        """Resolve a dispatch by its id (fail-closed on absent)."""
        request_ref = self._index.get(dispatch_id)
        if request_ref is None:
            raise RequestDispatchError("no such dispatch", dispatch_id=dispatch_id)
        return self._by_request[request_ref]

    @property
    def request_refs(self) -> tuple[str, ...]:
        """Every request id with a recorded dispatch, in stable (sorted) order."""
        return tuple(sorted(self._by_request))

    def all(self) -> tuple[DispatchRecord, ...]:
        """Every recorded dispatch in stable (request id) order."""
        return tuple(self._by_request[ref] for ref in self.request_refs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dispatch_count": len(self._by_request),
            "dispatches": [self._by_request[ref].to_dict() for ref in self.request_refs],
        }

    def fingerprint(self) -> str:
        return _content_hash(self.to_dict())


def all_dispatch_contracts() -> tuple[str, ...]:
    """The certified EC-1 execution contract names the dispatch boundary binds to."""
    return tuple(ref.name for ref in DISPATCH_CONTRACTS)


__all__ = [
    "FACTORY_CONTRACT",
    "COMPILER_CONTRACT",
    "RUNTIME_CONTRACT",
    "DETERMINISM_CONTRACT",
    "DISPATCH_CONTRACTS",
    "DEFAULT_EXECUTION_TARGET",
    "DispatchRecord",
    "DispatchLedger",
    "all_dispatch_contracts",
]
