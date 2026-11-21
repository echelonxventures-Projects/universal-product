"""EC2-TASK-000103/000104 — Blueprint Provenance (EC2-EPIC-006).

The **trace-closure record** that discharges the standing governance obligation
GOV-002 §6 **link-4** — the ``05-GENERATION → 06-IMPLEMENTATION`` (Generation
Framework → Implementation Program) traceability BREAK (GOV-004 BLK-AUTH-GOV-01 /
BLK-AUTH-TRC-01; EXEC-001 RSK-01; MEDIUM). Each cataloged blueprint carries
**provenance-by-reference** from its ``05-GENERATION`` blueprint origin down to its
EC-2 implementation consumption, making each catalog record a materialized, machine-
checkable ``Generation Artifact → Blueprint → Request → Implementation Artifact``
trace edge (Determination §5.3/§5.5).

A :class:`BlueprintProvenance` records, **by reference only** (no ``05-GENERATION``
content is imported or mutated, DP-03), the required trace fields:

    generation_reference · generation_artifact_id · generation_source ·
    generation_lineage · implementation_target · implementation_lineage ·
    dependency_chain · content_hash · provenance_metadata · audit_metadata

No synthetic linkage and no inferred linkage: every field is an explicit,
evidence-backed citation supplied at catalog time. The :class:`ProvenanceLedger` is an
append-only, deterministic record surface keyed by blueprint id (idempotent by
provenance id), mirroring the certified
:class:`~platform.security.classification.ClassificationLedger` discipline. It stores
records only; referential integrity (every provenance references a registered
blueprint) is a health probe.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.blueprints.contracts import BlueprintFamily
from platform.blueprints.errors import BlueprintProvenanceError
from platform.foundation.contracts import content_hash as _content_hash
from typing import Any


def _require_ref(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BlueprintProvenanceError(f"provenance {what} must be a non-empty string")
    return value


def _tuple_of_str(values: Iterable[str] | None, what: str) -> tuple[str, ...]:
    items = tuple(values or ())
    for item in items:
        if not isinstance(item, str) or not item.strip():
            raise BlueprintProvenanceError(f"provenance {what} entries must be non-empty strings")
    return items


def _str_map(values: Mapping[str, str] | None, what: str) -> dict[str, str]:
    mapping = dict(values or {})
    for key, val in mapping.items():
        if not isinstance(key, str) or not key:
            raise BlueprintProvenanceError(f"provenance {what} keys must be non-empty strings")
        if not isinstance(val, str):
            raise BlueprintProvenanceError(f"provenance {what} values must be strings")
    return mapping


@dataclass(frozen=True, slots=True)
class BlueprintProvenance:
    """An immutable, content-addressed provenance-by-reference record (link-4 edge).

    Binds a blueprint (``blueprint_ref``) to its ``05-GENERATION`` origin and its
    downstream implementation target, carrying the full evidence-backed trace chain.
    ``provenance_id`` is content-addressed (deterministic).
    """

    blueprint_ref: str
    family: BlueprintFamily
    generation_reference: str
    generation_artifact_id: str
    generation_source: str
    generation_lineage: tuple[str, ...]
    implementation_target: str
    implementation_lineage: tuple[str, ...]
    dependency_chain: tuple[str, ...]
    content_hash: str
    provenance_metadata: Mapping[str, str]
    audit_metadata: Mapping[str, str]
    provenance_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        blueprint_ref: str,
        family: BlueprintFamily,
        generation_reference: str,
        generation_artifact_id: str,
        generation_source: str,
        implementation_target: str,
        content_hash: str,
        generation_lineage: Iterable[str] | None = None,
        implementation_lineage: Iterable[str] | None = None,
        dependency_chain: Iterable[str] | None = None,
        provenance_metadata: Mapping[str, str] | None = None,
        audit_metadata: Mapping[str, str] | None = None,
    ) -> BlueprintProvenance:
        """Build a fully-cited provenance record (fail-closed; no synthetic linkage)."""
        ref = _require_ref(blueprint_ref, "blueprint_ref")
        if not isinstance(family, BlueprintFamily):
            raise BlueprintProvenanceError("provenance family must be a BlueprintFamily")
        gen_ref = _require_ref(generation_reference, "generation_reference")
        gen_artifact = _require_ref(generation_artifact_id, "generation_artifact_id")
        gen_source = _require_ref(generation_source, "generation_source")
        impl_target = _require_ref(implementation_target, "implementation_target")
        digest = _require_ref(content_hash, "content_hash")
        gen_lineage = _tuple_of_str(generation_lineage, "generation_lineage")
        impl_lineage = _tuple_of_str(implementation_lineage, "implementation_lineage")
        dep_chain = _tuple_of_str(dependency_chain, "dependency_chain")
        prov_meta = _str_map(provenance_metadata, "provenance_metadata")
        audit_meta = _str_map(audit_metadata, "audit_metadata")
        core = {
            "blueprint_ref": ref,
            "family": family.value,
            "generation_reference": gen_ref,
            "generation_artifact_id": gen_artifact,
            "generation_source": gen_source,
            "generation_lineage": list(gen_lineage),
            "implementation_target": impl_target,
            "implementation_lineage": list(impl_lineage),
            "dependency_chain": list(dep_chain),
            "content_hash": digest,
            "provenance_metadata": {k: prov_meta[k] for k in sorted(prov_meta)},
            "audit_metadata": {k: audit_meta[k] for k in sorted(audit_meta)},
        }
        return cls(
            blueprint_ref=ref,
            family=family,
            generation_reference=gen_ref,
            generation_artifact_id=gen_artifact,
            generation_source=gen_source,
            generation_lineage=gen_lineage,
            implementation_target=impl_target,
            implementation_lineage=impl_lineage,
            dependency_chain=dep_chain,
            content_hash=digest,
            provenance_metadata=prov_meta,
            audit_metadata=audit_meta,
            provenance_id=f"UCOS-BPRV-{_content_hash(core)[:16]}",
        )

    @property
    def is_traceable(self) -> bool:
        """True iff both the generation origin and implementation target are present.

        This is the machine-checkable predicate that the ``05-GENERATION →
        06-IMPLEMENTATION`` edge is materially present (link-4 PRESENT, not BREAK).
        """
        return bool(
            self.generation_reference and self.generation_artifact_id and self.implementation_target
        )

    def trace_edge(self) -> dict[str, Any]:
        """The explicit Generation → Blueprint → Implementation trace edge (link-4).

        Backward: the ``05-GENERATION`` framework + BP-* artifact origin. Subject: the
        cataloged blueprint. Forward: the EC-2 implementation target + dependency
        chain. This is the evidence a traceability determination reads to reclassify
        link-4 from BREAK to PRESENT (§5.4/§5.5).
        """
        return {
            "provenance_id": self.provenance_id,
            "link": "GOV-002-link-4",
            "generation": {
                "reference": self.generation_reference,
                "artifact_id": self.generation_artifact_id,
                "source": self.generation_source,
                "family": self.family.value,
                "lineage": list(self.generation_lineage),
            },
            "blueprint": {"blueprint_ref": self.blueprint_ref, "content_hash": self.content_hash},
            "implementation": {
                "target": self.implementation_target,
                "lineage": list(self.implementation_lineage),
                "dependency_chain": list(self.dependency_chain),
            },
            "traceable": self.is_traceable,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "provenance_id": self.provenance_id,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "generation_reference": self.generation_reference,
            "generation_artifact_id": self.generation_artifact_id,
            "generation_source": self.generation_source,
            "generation_lineage": list(self.generation_lineage),
            "implementation_target": self.implementation_target,
            "implementation_lineage": list(self.implementation_lineage),
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
    """A deterministic, append-only ledger of blueprint provenance records (by reference)."""

    __slots__ = ("_by_blueprint", "_index")

    def __init__(self) -> None:
        self._by_blueprint: dict[str, BlueprintProvenance] = {}
        self._index: dict[str, str] = {}  # provenance_id -> blueprint_ref

    def record(self, provenance: BlueprintProvenance) -> BlueprintProvenance:
        """Record provenance for a blueprint (idempotent by id; fail-closed on conflict).

        Re-recording the identical provenance returns the stored entry. Recording a
        *different* provenance for a blueprint that already has one is refused
        (immutable trace edge; append-only).
        """
        if not isinstance(provenance, BlueprintProvenance):
            raise BlueprintProvenanceError("only a BlueprintProvenance may be recorded")
        if not provenance.is_traceable:
            raise BlueprintProvenanceError(
                "provenance is not traceable (missing generation/implementation edge)",
                blueprint_ref=provenance.blueprint_ref,
            )
        existing = self._by_blueprint.get(provenance.blueprint_ref)
        if existing is not None:
            if existing.provenance_id == provenance.provenance_id:
                return existing
            raise BlueprintProvenanceError(
                "blueprint already has distinct provenance recorded",
                blueprint_ref=provenance.blueprint_ref,
            )
        self._by_blueprint[provenance.blueprint_ref] = provenance
        self._index[provenance.provenance_id] = provenance.blueprint_ref
        return provenance

    def __contains__(self, blueprint_ref: str) -> bool:
        return blueprint_ref in self._by_blueprint

    def __len__(self) -> int:
        return len(self._by_blueprint)

    def has(self, blueprint_ref: str) -> bool:
        """True iff provenance is recorded for ``blueprint_ref``."""
        return blueprint_ref in self._by_blueprint

    def get(self, blueprint_ref: str) -> BlueprintProvenance:
        """Resolve the provenance of a blueprint (fail-closed on absent)."""
        provenance = self._by_blueprint.get(blueprint_ref)
        if provenance is None:
            raise BlueprintProvenanceError(
                "no provenance recorded for blueprint", blueprint_ref=blueprint_ref
            )
        return provenance

    @property
    def blueprint_refs(self) -> tuple[str, ...]:
        """Every blueprint id with recorded provenance, in stable (sorted) order."""
        return tuple(sorted(self._by_blueprint))

    def all(self) -> tuple[BlueprintProvenance, ...]:
        """Every recorded provenance in stable (blueprint id) order."""
        return tuple(self._by_blueprint[ref] for ref in self.blueprint_refs)

    def trace(self, blueprint_ref: str) -> dict[str, Any]:
        """Return the link-4 trace edge for a blueprint (fail-closed on absent)."""
        return self.get(blueprint_ref).trace_edge()

    def to_dict(self) -> dict[str, Any]:
        return {
            "provenance_count": len(self._by_blueprint),
            "provenance": [self._by_blueprint[ref].to_dict() for ref in self.blueprint_refs],
        }

    def fingerprint(self) -> str:
        return _content_hash(self.to_dict())


__all__ = ["BlueprintProvenance", "ProvenanceLedger"]
