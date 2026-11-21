"""EC2-TASK-000113 — Generation Request Provenance (EC2-EPIC-007).

The **traceability continuation** record that carries the GOV-002 §6 **link-4** trace
edge through the Generation Request node. EC2-EPIC-006 discharged the
``05-GENERATION → 06-IMPLEMENTATION`` break by making each cataloged blueprint carry
provenance-by-reference from its generation origin. EC2-EPIC-007 **extends that chain
one node forward**, so a request materializes the full, machine-checkable edge:

    Generation Artifact  ──►  Blueprint  ──►  Request  ──►  Implementation Artifact
       (05-GENERATION)        (EPIC-006)     (EPIC-007)        (downstream)

A :class:`RequestProvenance` records, **by reference only** (no ``05-GENERATION``
content is imported or mutated, DP-03), the trace fields for the request node:

    request_ref · blueprint_ref · family · generation_reference ·
    generation_artifact_id · blueprint_provenance_ref · implementation_target ·
    dependency_chain · content_hash · provenance_metadata · audit_metadata

No synthetic and no inferred linkage: every field is an explicit, evidence-backed
citation supplied by the caller. The :class:`ProvenanceLedger` is an append-only,
deterministic record surface keyed by request id (idempotent by provenance id),
mirroring the certified :class:`~platform.blueprints.provenance.ProvenanceLedger`
discipline exactly. It stores records only; referential integrity (every provenance
references a registered request) is a health probe.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import content_hash as _content_hash
from platform.generation.errors import RequestProvenanceError
from typing import Any


def _require_ref(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RequestProvenanceError(f"provenance {what} must be a non-empty string")
    return value


def _tuple_of_str(values: Iterable[str] | None, what: str) -> tuple[str, ...]:
    items = tuple(values or ())
    for item in items:
        if not isinstance(item, str) or not item.strip():
            raise RequestProvenanceError(f"provenance {what} entries must be non-empty strings")
    return items


def _str_map(values: Mapping[str, str] | None, what: str) -> dict[str, str]:
    mapping = dict(values or {})
    for key, val in mapping.items():
        if not isinstance(key, str) or not key:
            raise RequestProvenanceError(f"provenance {what} keys must be non-empty strings")
        if not isinstance(val, str):
            raise RequestProvenanceError(f"provenance {what} values must be strings")
    return mapping


@dataclass(frozen=True, slots=True)
class RequestProvenance:
    """An immutable, content-addressed request provenance-by-reference record (link-4 edge).

    Binds a request (``request_ref``) to its blueprint (``blueprint_ref`` +
    ``blueprint_provenance_ref``), its ``05-GENERATION`` origin, and its downstream
    ``implementation_target``, carrying the evidence-backed continuation of the link-4
    trace chain. ``provenance_id`` is content-addressed (deterministic).
    """

    request_ref: str
    blueprint_ref: str
    family: BlueprintFamily
    generation_reference: str
    generation_artifact_id: str
    blueprint_provenance_ref: str
    implementation_target: str
    dependency_chain: tuple[str, ...]
    content_hash: str
    provenance_metadata: Mapping[str, str]
    audit_metadata: Mapping[str, str]
    provenance_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        request_ref: str,
        blueprint_ref: str,
        family: BlueprintFamily,
        generation_reference: str,
        generation_artifact_id: str,
        blueprint_provenance_ref: str,
        implementation_target: str,
        content_hash: str,
        dependency_chain: Iterable[str] | None = None,
        provenance_metadata: Mapping[str, str] | None = None,
        audit_metadata: Mapping[str, str] | None = None,
    ) -> RequestProvenance:
        """Build a fully-cited request provenance record (fail-closed; no synthetic linkage)."""
        req = _require_ref(request_ref, "request_ref")
        bp = _require_ref(blueprint_ref, "blueprint_ref")
        if not isinstance(family, BlueprintFamily):
            raise RequestProvenanceError("provenance family must be a BlueprintFamily")
        gen_ref = _require_ref(generation_reference, "generation_reference")
        gen_artifact = _require_ref(generation_artifact_id, "generation_artifact_id")
        bp_prov = _require_ref(blueprint_provenance_ref, "blueprint_provenance_ref")
        impl_target = _require_ref(implementation_target, "implementation_target")
        digest = _require_ref(content_hash, "content_hash")
        dep_chain = _tuple_of_str(dependency_chain, "dependency_chain")
        prov_meta = _str_map(provenance_metadata, "provenance_metadata")
        audit_meta = _str_map(audit_metadata, "audit_metadata")
        core = {
            "request_ref": req,
            "blueprint_ref": bp,
            "family": family.value,
            "generation_reference": gen_ref,
            "generation_artifact_id": gen_artifact,
            "blueprint_provenance_ref": bp_prov,
            "implementation_target": impl_target,
            "dependency_chain": list(dep_chain),
            "content_hash": digest,
            "provenance_metadata": {k: prov_meta[k] for k in sorted(prov_meta)},
            "audit_metadata": {k: audit_meta[k] for k in sorted(audit_meta)},
        }
        return cls(
            request_ref=req,
            blueprint_ref=bp,
            family=family,
            generation_reference=gen_ref,
            generation_artifact_id=gen_artifact,
            blueprint_provenance_ref=bp_prov,
            implementation_target=impl_target,
            dependency_chain=dep_chain,
            content_hash=digest,
            provenance_metadata=prov_meta,
            audit_metadata=audit_meta,
            provenance_id=f"UCOS-GPRV-{_content_hash(core)[:16]}",
        )

    @property
    def is_traceable(self) -> bool:
        """True iff the full backward (generation+blueprint) and forward edges are present.

        The machine-checkable predicate that the ``Generation → Blueprint → Request →
        Implementation`` edge is materially present through this node (link-4 PRESENT).
        """
        return bool(
            self.generation_reference
            and self.generation_artifact_id
            and self.blueprint_ref
            and self.blueprint_provenance_ref
            and self.implementation_target
        )

    def trace_edge(self) -> dict[str, Any]:
        """The explicit Generation → Blueprint → Request → Implementation trace edge (link-4)."""
        return {
            "provenance_id": self.provenance_id,
            "link": "GOV-002-link-4",
            "generation": {
                "reference": self.generation_reference,
                "artifact_id": self.generation_artifact_id,
                "family": self.family.value,
            },
            "blueprint": {
                "blueprint_ref": self.blueprint_ref,
                "provenance_ref": self.blueprint_provenance_ref,
            },
            "request": {"request_ref": self.request_ref, "content_hash": self.content_hash},
            "implementation": {
                "target": self.implementation_target,
                "dependency_chain": list(self.dependency_chain),
            },
            "traceable": self.is_traceable,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "provenance_id": self.provenance_id,
            "request_ref": self.request_ref,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "generation_reference": self.generation_reference,
            "generation_artifact_id": self.generation_artifact_id,
            "blueprint_provenance_ref": self.blueprint_provenance_ref,
            "implementation_target": self.implementation_target,
            "dependency_chain": list(self.dependency_chain),
            "content_hash": self.content_hash,
            "provenance_metadata": {
                k: self.provenance_metadata[k] for k in sorted(self.provenance_metadata)
            },
            "audit_metadata": {k: self.audit_metadata[k] for k in sorted(self.audit_metadata)},
        }

    def fingerprint(self) -> str:
        return _content_hash(self.to_dict())


class ProvenanceLedger:
    """A deterministic, append-only ledger of request provenance records (by reference)."""

    __slots__ = ("_by_request", "_index")

    def __init__(self) -> None:
        self._by_request: dict[str, RequestProvenance] = {}
        self._index: dict[str, str] = {}  # provenance_id -> request_ref

    def record(self, provenance: RequestProvenance) -> RequestProvenance:
        """Record provenance for a request (idempotent by id; fail-closed on conflict)."""
        if not isinstance(provenance, RequestProvenance):
            raise RequestProvenanceError("only a RequestProvenance may be recorded")
        if not provenance.is_traceable:
            raise RequestProvenanceError(
                "provenance is not traceable (missing generation/blueprint/implementation edge)",
                request_ref=provenance.request_ref,
            )
        existing = self._by_request.get(provenance.request_ref)
        if existing is not None:
            if existing.provenance_id == provenance.provenance_id:
                return existing
            raise RequestProvenanceError(
                "request already has distinct provenance recorded",
                request_ref=provenance.request_ref,
            )
        self._by_request[provenance.request_ref] = provenance
        self._index[provenance.provenance_id] = provenance.request_ref
        return provenance

    def __contains__(self, request_ref: str) -> bool:
        return request_ref in self._by_request

    def __len__(self) -> int:
        return len(self._by_request)

    def has(self, request_ref: str) -> bool:
        """True iff provenance is recorded for ``request_ref``."""
        return request_ref in self._by_request

    def get(self, request_ref: str) -> RequestProvenance:
        """Resolve the provenance of a request (fail-closed on absent)."""
        provenance = self._by_request.get(request_ref)
        if provenance is None:
            raise RequestProvenanceError(
                "no provenance recorded for request", request_ref=request_ref
            )
        return provenance

    @property
    def request_refs(self) -> tuple[str, ...]:
        """Every request id with recorded provenance, in stable (sorted) order."""
        return tuple(sorted(self._by_request))

    def all(self) -> tuple[RequestProvenance, ...]:
        """Every recorded provenance in stable (request id) order."""
        return tuple(self._by_request[ref] for ref in self.request_refs)

    def trace(self, request_ref: str) -> dict[str, Any]:
        """Return the link-4 trace edge for a request (fail-closed on absent)."""
        return self.get(request_ref).trace_edge()

    def to_dict(self) -> dict[str, Any]:
        return {
            "provenance_count": len(self._by_request),
            "provenance": [self._by_request[ref].to_dict() for ref in self.request_refs],
        }

    def fingerprint(self) -> str:
        return _content_hash(self.to_dict())


__all__ = ["RequestProvenance", "ProvenanceLedger"]
