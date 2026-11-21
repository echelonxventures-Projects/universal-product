"""ZG-P-02 — Coverage vocabulary & contracts (Universe→Code Coverage Instrument).

The immutable, deterministic vocabulary the coverage instrument speaks, plus the
versioned published contract surface (AR-03/PL-05, reusing the certified Foundation
contract machinery). The instrument models the authoritative coverage spine

    Universe → Phase → Program → Implementation → Epic → Module → Code Asset → Runtime Asset

as a directed graph of typed :class:`CoverageNode` connected by adjacency-checked
:class:`CoverageEdge` values, each carrying a :class:`CoverageStatus`. Every identity is
content-addressed (deterministic, reproducible; IMP-007 §5) and holds no wall-clock —
the optional ``tick`` on an edge is a **caller-supplied logical tick** that is excluded
from every identity and fingerprint, so recompute is byte-identical across processes.

Nothing here is hardcoded to a specific universe or program: the vocabulary defines the
*shape* of coverage; the concrete nodes/edges are supplied by an evidence source
(:mod:`platform.coverage.evidence`).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.coverage.errors import CoverageContractError
from platform.foundation.contracts import ContractRef, content_hash
from typing import Any

#: The semantic version of the coverage instrument contract surface (AR-03/PL-05).
COVERAGE_CONTRACT_VERSION = "1.0.0"


class CoverageNodeKind(str, Enum):
    """The eight authoritative coverage tiers (the Universe→Code spine)."""

    UNIVERSE = "universe"
    PHASE = "phase"
    PROGRAM = "program"
    IMPLEMENTATION = "implementation"
    EPIC = "epic"
    MODULE = "module"
    CODE_ASSET = "code_asset"
    RUNTIME_ASSET = "runtime_asset"


#: The ordered coverage spine. Adjacent kinds (i, i+1) are the only legal edge kinds.
COVERAGE_SPINE: tuple[CoverageNodeKind, ...] = (
    CoverageNodeKind.UNIVERSE,
    CoverageNodeKind.PHASE,
    CoverageNodeKind.PROGRAM,
    CoverageNodeKind.IMPLEMENTATION,
    CoverageNodeKind.EPIC,
    CoverageNodeKind.MODULE,
    CoverageNodeKind.CODE_ASSET,
    CoverageNodeKind.RUNTIME_ASSET,
)

#: Index of each kind in the spine, for O(1) adjacency checks.
_SPINE_INDEX: dict[CoverageNodeKind, int] = {k: i for i, k in enumerate(COVERAGE_SPINE)}

#: The terminal tier that carries realization evidence (coverage bottoms out here).
TERMINAL_KIND = CoverageNodeKind.RUNTIME_ASSET

#: The root tier (universes have no legal parent in the spine).
ROOT_KIND = CoverageNodeKind.UNIVERSE


def is_adjacent(source: CoverageNodeKind, target: CoverageNodeKind) -> bool:
    """True iff ``target`` directly follows ``source`` in the coverage spine."""
    return _SPINE_INDEX.get(target, -1) - _SPINE_INDEX.get(source, -2) == 1


def edge_kind_label(source: CoverageNodeKind, target: CoverageNodeKind) -> str:
    """A stable label for the edge kind between two adjacent node kinds."""
    return f"{source.value}->{target.value}"


class CoverageStatus(str, Enum):
    """The fail-closed coverage verdict for a node or an aggregate.

    ``COVERED`` — a downstream path terminates in runtime evidence and no child is a gap.
    ``PARTIAL`` — some downstream children are covered, some are gaps.
    ``UNCOVERED`` — no downstream runtime evidence (a coverage gap; well-formed).
    ``ORPHANED`` — a structural defect: the node has no valid lineage to a universe.
    """

    COVERED = "covered"
    PARTIAL = "partial"
    UNCOVERED = "uncovered"
    ORPHANED = "orphaned"


@dataclass(frozen=True, slots=True)
class CoverageNode:
    """An immutable, content-addressed node in the coverage graph.

    ``ref`` is the *authoritative identifier* of the entity (e.g. ``UNI-005``,
    ``IMP-005``, ``platform/identity``, ``EC2-EPIC-002``, ``platform/identity/service.py``,
    a symbol name, or ``runtime:platform/identity``). ``authority`` cites the repository
    artifact the node was derived from. The identity ``node_id`` is a pure function of
    ``(kind, ref)`` — never of authority/metadata — so the same entity always hashes to
    the same id regardless of which evidence pass discovered it.
    """

    kind: CoverageNodeKind
    ref: str
    label: str = ""
    authority: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)
    node_id: str = ""

    @classmethod
    def create(
        cls,
        kind: CoverageNodeKind,
        ref: str,
        *,
        label: str = "",
        authority: str = "",
        metadata: Mapping[str, str] | None = None,
    ) -> CoverageNode:
        if not isinstance(kind, CoverageNodeKind):
            raise CoverageContractError("coverage node kind must be a CoverageNodeKind")
        if not isinstance(ref, str) or not ref.strip():
            raise CoverageContractError("coverage node ref must be a non-empty string")
        meta = dict(metadata or {})
        for key, val in meta.items():
            if not isinstance(key, str) or not key or not isinstance(val, str):
                raise CoverageContractError(
                    "coverage node metadata must be a str->str map", ref=ref
                )
        core = {"kind": kind.value, "ref": ref}
        return cls(
            kind=kind,
            ref=ref,
            label=label or ref,
            authority=authority,
            metadata=meta,
            node_id=f"UCOS-COVN-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "kind": self.kind.value,
            "ref": self.ref,
            "label": self.label,
            "authority": self.authority,
            "metadata": {k: self.metadata[k] for k in sorted(self.metadata)},
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class CoverageEdge:
    """An immutable, content-addressed, adjacency-checked coverage edge.

    Connects a ``source`` entity to a ``target`` entity one tier down the spine, citing
    the ``authority`` (source artifact) and ``evidence`` (the specific citation) that
    establish the link. ``tick`` is a caller-supplied **logical** timestamp: it is
    recorded for traceability but excluded from ``edge_id`` and every fingerprint, so
    recompute is deterministic (no wall-clock; IMP-007 §5).
    """

    source_kind: CoverageNodeKind
    source_ref: str
    target_kind: CoverageNodeKind
    target_ref: str
    authority: str
    evidence: str
    tick: int = 0
    edge_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        source_kind: CoverageNodeKind,
        source_ref: str,
        target_kind: CoverageNodeKind,
        target_ref: str,
        authority: str,
        evidence: str,
        tick: int = 0,
    ) -> CoverageEdge:
        if not isinstance(source_kind, CoverageNodeKind) or not isinstance(
            target_kind, CoverageNodeKind
        ):
            raise CoverageContractError("coverage edge kinds must be CoverageNodeKind")
        if not is_adjacent(source_kind, target_kind):
            raise CoverageContractError(
                "coverage edge violates spine adjacency",
                source_kind=source_kind.value,
                target_kind=target_kind.value,
            )
        for name, value in (("source_ref", source_ref), ("target_ref", target_ref)):
            if not isinstance(value, str) or not value.strip():
                raise CoverageContractError(f"coverage edge {name} must be a non-empty string")
        if not isinstance(authority, str) or not authority.strip():
            raise CoverageContractError("coverage edge authority (citation) is mandatory")
        if not isinstance(evidence, str) or not evidence.strip():
            raise CoverageContractError("coverage edge evidence (citation) is mandatory")
        if not isinstance(tick, int) or isinstance(tick, bool) or tick < 0:
            raise CoverageContractError("coverage edge tick must be a non-negative int")
        core = {
            "source_kind": source_kind.value,
            "source_ref": source_ref,
            "target_kind": target_kind.value,
            "target_ref": target_ref,
            "authority": authority,
            "evidence": evidence,
        }
        return cls(
            source_kind=source_kind,
            source_ref=source_ref,
            target_kind=target_kind,
            target_ref=target_ref,
            authority=authority,
            evidence=evidence,
            tick=tick,
            edge_id=f"UCOS-COVE-{content_hash(core)[:16]}",
        )

    @property
    def kind_label(self) -> str:
        """The stable edge-kind label (e.g. ``universe->phase``)."""
        return edge_kind_label(self.source_kind, self.target_kind)

    def source_node_id(self) -> str:
        """The content-addressed node id of the source endpoint."""
        core = {"kind": self.source_kind.value, "ref": self.source_ref}
        return f"UCOS-COVN-{content_hash(core)[:16]}"

    def target_node_id(self) -> str:
        """The content-addressed node id of the target endpoint."""
        core = {"kind": self.target_kind.value, "ref": self.target_ref}
        return f"UCOS-COVN-{content_hash(core)[:16]}"

    def trace(self) -> dict[str, Any]:
        """The deterministic, machine-reconstructable lineage record for this edge."""
        return {
            "edge_id": self.edge_id,
            "kind": self.kind_label,
            "source": {"kind": self.source_kind.value, "ref": self.source_ref},
            "target": {"kind": self.target_kind.value, "ref": self.target_ref},
            "authority": self.authority,
            "evidence": self.evidence,
            "fingerprint": self.fingerprint(),
            "timestamp": self.tick,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "kind": self.kind_label,
            "source_kind": self.source_kind.value,
            "source_ref": self.source_ref,
            "target_kind": self.target_kind.value,
            "target_ref": self.target_ref,
            "authority": self.authority,
            "evidence": self.evidence,
        }

    def fingerprint(self) -> str:
        """Content fingerprint (excludes the logical ``tick`` — determinism-safe)."""
        return content_hash(self.to_dict())


#: The published coverage contract surface (consumed by certification/TRACK-001 by ref).
_COVERAGE_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("coverage.graph.reconstruct", "Deterministic Universe→Code coverage graph."),
    ("coverage.registry.record", "Append-only content-addressed coverage registry."),
    ("coverage.engine.compute", "Coverage compute/verify/reconcile/fingerprint/report."),
    ("coverage.health.probe", "Coverage integrity + completeness health checks."),
    ("coverage.certification.assess", "Certification-facing coverage assertions (G4)."),
)

#: Immutable references to the five published coverage contracts (name + version).
COVERAGE_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, COVERAGE_CONTRACT_VERSION) for name, _ in _COVERAGE_CONTRACT_NAMES
)

#: The authoritative governance instruments this coverage recompute integrates with
#: (by reference only — it reads them, replaces none). Cited in every report/evidence.
GOVERNANCE_AUTHORITIES: tuple[str, ...] = (
    "GOV-002",  # Constitution→Implementation traceability (link model)
    "GOV-005",  # Repository governance reconciliation (zero-gap invariant)
    "GOV-006",  # Repository governance correction (category→volume)
    "TRACK-001",  # Evidence→status, append-only, fail-closed
    "STATUS-001",  # Evidence→status discipline
    "MIP-ZG-001",  # Master coverage & reconciliation determination (authorizing basis)
)


def coverage_contract_names() -> tuple[str, ...]:
    """Return the published coverage contract names in stable order."""
    return tuple(name for name, _ in _COVERAGE_CONTRACT_NAMES)


__all__ = [
    "COVERAGE_CONTRACT_VERSION",
    "CoverageNodeKind",
    "COVERAGE_SPINE",
    "TERMINAL_KIND",
    "ROOT_KIND",
    "is_adjacent",
    "edge_kind_label",
    "CoverageStatus",
    "CoverageNode",
    "CoverageEdge",
    "COVERAGE_CONTRACTS",
    "GOVERNANCE_AUTHORITIES",
    "coverage_contract_names",
]
