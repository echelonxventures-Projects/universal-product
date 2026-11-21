"""UCOS-EPIC-003 — The eight registry-driven discovery dimensions.

Each discoverer is a **pure function** over the read-only registry views (EPIC-002):
the :class:`~engine.registry.artifacts.ArtifactRepository`, the
:class:`~engine.registry.graph.RelationshipGraph`, the
:class:`~engine.registry.volumes.VolumeRepository`, and the
:class:`~engine.registry.source.RegistrySource`. Every discovered fact is drawn
verbatim from a registry record.

There are **no hard-coded discovery patterns**: no regex over paths or content, no
``glob``/``fnmatch``, no filesystem walking, and no enumerated lists of what to
look for. The registry is the single source of truth (INV-13). The one place a
controlled vocabulary is consulted is lifecycle *classification* for the capability
realisation profile — and that vocabulary is the registry's own
:class:`~engine.registry.models.LifecycleStatus` enum, not an ad-hoc pattern.

Every discoverer returns a :class:`~engine.discovery.contracts.DimensionResult` with
items in stable (sorted) order and a :class:`~engine.discovery.contracts.DimensionCoverage`
that measures how much of the in-scope substrate was resolved. A coverage shortfall
is always a referential gap in the substrate, never a limitation of discovery.
"""

from __future__ import annotations

from engine.discovery.contracts import (
    DimensionCoverage,
    DimensionResult,
    DiscoveredItem,
    DiscoveryKind,
)
from engine.registry.artifacts import ArtifactRepository
from engine.registry.graph import DEPENDS_ON, RelationshipGraph
from engine.registry.models import Artifact, LifecycleStatus
from engine.registry.source import (
    ARTIFACTS_FILE,
    RELATIONSHIPS_FILE,
    VOLUMES_FILE,
    RegistrySource,
)
from engine.registry.volumes import VolumeRepository

#: The registry's own lifecycle statuses that denote a *realised* artifact — a unit
#: of work that exists as more than a plan. Drawn from the registry vocabulary
#: (LifecycleStatus), never an ad-hoc string pattern.
REALIZED_STATUSES: frozenset[LifecycleStatus] = frozenset(
    {
        LifecycleStatus.IMPLEMENTED,
        LifecycleStatus.TESTED,
        LifecycleStatus.CERTIFIED,
        LifecycleStatus.DEPLOYED,
        LifecycleStatus.PRODUCTION,
        LifecycleStatus.ACTIVE,
        LifecycleStatus.COMPLETE,
        LifecycleStatus.FINAL,
        LifecycleStatus.FROZEN,
    }
)


def _slug(text: str) -> str:
    """Return a deterministic, upper-case, dash-delimited slug of ``text``.

    Used only to build stable *item ids* from registry values already chosen by the
    corpus — it is not a discovery pattern (nothing is matched against it).
    """
    out: list[str] = []
    prev_dash = False
    for ch in str(text).strip().upper():
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    return "".join(out).strip("-") or "NONE"


def _is_realized(artifact: Artifact) -> bool:
    return artifact.status in REALIZED_STATUSES


# --------------------------------------------------------------------------- 1. namespace


def discover_namespaces(
    artifacts: ArtifactRepository,
    volumes: VolumeRepository,
) -> DimensionResult:
    """Discover the registry's organising namespaces: volumes, categories, programs.

    A *volume* namespace is the canonical containment axis of the Master Book; a
    *category* and a *program* namespace are the provenance/organising facets every
    artifact declares. Every namespace is grounded in real registry values.

    Coverage scope is the set of distinct namespaces; a namespace is *discovered*
    (resolved) unless it is a volume referenced by an artifact yet absent from the
    volume registry — a dangling namespace, which is a substrate gap.
    """
    items: list[DiscoveredItem] = []
    gaps: list[str] = []

    # Volume namespaces: union of registry volumes and volumes artifacts reference.
    referenced = {a.volume for a in artifacts if a.volume}
    registered = set(volumes.ids())
    for volume_id in sorted(referenced | registered):
        member_count = len(artifacts.by_volume(volume_id))
        exists = volumes.exists(volume_id)
        volume = volumes.find(volume_id)
        if not exists:
            gaps.append(volume_id)
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.NAMESPACE,
                item_id=f"UDNS-VOL-{_slug(volume_id)}",
                name=volume.name if volume else volume_id,
                source=VOLUMES_FILE,
                attributes={
                    "axis": "volume",
                    "volume_id": volume_id,
                    "registered": exists,
                    "member_count": member_count,
                    "category": volume.category if volume else "",
                },
            )
        )

    # Category namespaces (always grounded in artifacts that carry them).
    for category in artifacts.categories():
        members = artifacts.by_category(category)
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.NAMESPACE,
                item_id=f"UDNS-CAT-{_slug(category)}",
                name=category,
                source=ARTIFACTS_FILE,
                attributes={"axis": "category", "member_count": len(members)},
            )
        )

    # Program namespaces (always grounded in artifacts that carry them).
    for program in artifacts.programs():
        members = artifacts.by_program(program)
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.NAMESPACE,
                item_id=f"UDNS-PROG-{_slug(program)}",
                name=program,
                source=ARTIFACTS_FILE,
                attributes={"axis": "program", "member_count": len(members)},
            )
        )

    total = len(referenced | registered) + len(artifacts.categories()) + len(artifacts.programs())
    discovered = total - len(gaps)
    return DimensionResult(
        kind=DiscoveryKind.NAMESPACE,
        items=tuple(items),
        coverage=DimensionCoverage(DiscoveryKind.NAMESPACE, discovered=discovered, total=total),
        gaps=tuple(sorted(gaps)),
    )


# --------------------------------------------------------------------------- 2. document


def discover_documents(artifacts: ArtifactRepository) -> DimensionResult:
    """Discover every registered artifact as an addressable document.

    A document is the artifact projected by its addressable identity — id, name,
    canonical ``path``, ``return_link``, version, and lifecycle status. Coverage
    scope is every artifact; a document is discovered unless it declares no path
    (which the schema forbids, so a shortfall marks a malformed record).
    """
    items: list[DiscoveredItem] = []
    gaps: list[str] = []
    for artifact in artifacts.all():
        has_path = bool(artifact.path)
        if not has_path:
            gaps.append(artifact.universal_id)
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.DOCUMENT,
                item_id=f"UDDOC-{artifact.universal_id}",
                name=artifact.name,
                source=ARTIFACTS_FILE,
                attributes={
                    "universal_id": artifact.universal_id,
                    "native_id": artifact.native_id,
                    "path": artifact.path,
                    "return_link": artifact.return_link,
                    "version": artifact.version,
                    "status": artifact.status.value,
                    "volume": artifact.volume,
                    "category": artifact.category,
                    "page_start": artifact.page_start,
                    "page_end": artifact.page_end,
                },
                references=(artifact.parent,) if artifact.parent else (),
            )
        )
    total = artifacts.count()
    discovered = total - len(gaps)
    return DimensionResult(
        kind=DiscoveryKind.DOCUMENT,
        items=tuple(sorted(items, key=lambda i: i.item_id)),
        coverage=DimensionCoverage(DiscoveryKind.DOCUMENT, discovered=discovered, total=total),
        gaps=tuple(sorted(gaps)),
    )


# --------------------------------------------------------------------------- 3. registry


def discover_registries(
    source: RegistrySource,
    artifacts: ArtifactRepository,
    graph: RelationshipGraph,
    volumes: VolumeRepository,
) -> DimensionResult:
    """Discover the registries themselves — the three canonical data files.

    Each registry (artifacts / relationships / volumes) is discovered with its live
    record count. Coverage scope is the three canonical registries; a registry is
    discovered iff its data file is present in the substrate.
    """
    registries = (
        ("artifacts", ARTIFACTS_FILE, artifacts.count()),
        ("relationships", RELATIONSHIPS_FILE, graph.count()),
        ("volumes", VOLUMES_FILE, volumes.count()),
    )
    items: list[DiscoveredItem] = []
    gaps: list[str] = []
    for name, filename, count in registries:
        present = source.exists(filename)
        if not present:
            gaps.append(filename)
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.REGISTRY,
                item_id=f"UDREG-{_slug(name)}",
                name=name,
                source=filename,
                attributes={"filename": filename, "present": present, "record_count": count},
            )
        )
    total = len(registries)
    discovered = total - len(gaps)
    return DimensionResult(
        kind=DiscoveryKind.REGISTRY,
        items=tuple(items),
        coverage=DimensionCoverage(DiscoveryKind.REGISTRY, discovered=discovered, total=total),
        gaps=tuple(sorted(gaps)),
    )


# --------------------------------------------------------------------------- 4. component


def discover_components(
    artifacts: ArtifactRepository,
    graph: RelationshipGraph,
) -> DimensionResult:
    """Discover every registered artifact as a lifecycle component.

    A component is the artifact projected by its structural role — lifecycle status,
    realisation, owner, parent, and immediate children. Coverage scope is every
    artifact; a component is discovered unless it names a ``parent`` that resolves to
    no artifact (a dangling parent — a substrate gap).
    """
    items: list[DiscoveredItem] = []
    gaps: list[str] = []
    for artifact in artifacts.all():
        parent_resolves = (not artifact.parent) or artifacts.exists(artifact.parent)
        if not parent_resolves:
            gaps.append(artifact.universal_id)
        children = tuple(
            sorted(c.universal_id for c in artifacts.children_of(artifact.universal_id))
        )
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.COMPONENT,
                item_id=f"UDCMP-{artifact.universal_id}",
                name=artifact.name,
                source=ARTIFACTS_FILE,
                attributes={
                    "universal_id": artifact.universal_id,
                    "status": artifact.status.value,
                    "realized": _is_realized(artifact),
                    "owner": artifact.owner,
                    "program": artifact.program,
                    "category": artifact.category,
                    "parent": artifact.parent,
                    "parent_resolves": parent_resolves,
                    "child_count": len(children),
                    "degree": graph.degree(artifact.universal_id),
                },
                references=children,
            )
        )
    total = artifacts.count()
    discovered = total - len(gaps)
    return DimensionResult(
        kind=DiscoveryKind.COMPONENT,
        items=tuple(sorted(items, key=lambda i: i.item_id)),
        coverage=DimensionCoverage(DiscoveryKind.COMPONENT, discovered=discovered, total=total),
        gaps=tuple(sorted(gaps)),
    )


# --------------------------------------------------------------------------- 5. dependency


def discover_dependencies(
    artifacts: ArtifactRepository,
    graph: RelationshipGraph,
) -> DimensionResult:
    """Discover dependency relations from the graph and from declared arrays.

    Two registry sources are unified and de-duplicated by ``(source, target)``:
    first-class ``Depends-On`` edges in the relationship graph, and the
    ``dependencies`` arrays declared on artifact records. Coverage scope is every
    distinct dependency relation; a relation is discovered (resolved) iff its target
    resolves to a known artifact — a dangling target is a substrate gap.
    """
    seen: dict[tuple[str, str], DiscoveredItem] = {}
    gaps: list[str] = []

    def _add(src: str, tgt: str, item_id: str, via: str) -> None:
        pair = (src, tgt)
        if pair in seen:
            # Prefer the graph edge id (added first); record additional provenance.
            existing = seen[pair]
            vias = tuple(sorted(set(existing.attributes.get("via", ())) | {via}))
            seen[pair] = DiscoveredItem(
                kind=existing.kind,
                item_id=existing.item_id,
                name=existing.name,
                source=existing.source,
                attributes={**existing.attributes, "via": vias},
                references=existing.references,
            )
            return
        resolved = artifacts.exists(tgt)
        seen[pair] = DiscoveredItem(
            kind=DiscoveryKind.DEPENDENCY,
            item_id=item_id,
            name=f"{src} -> {tgt}",
            source=RELATIONSHIPS_FILE if via == "graph" else ARTIFACTS_FILE,
            attributes={
                "source_id": src,
                "target_id": tgt,
                "resolved": resolved,
                "source_exists": artifacts.exists(src),
                "via": (via,),
            },
            references=(src, tgt),
        )

    # First-class Depends-On edges.
    for edge in graph.edges_of_type(DEPENDS_ON):
        _add(edge.source, edge.target, f"UDDEP-{edge.edge_id}", "graph")

    # Declared dependency arrays on artifacts (may add relations the graph omits).
    for artifact in artifacts.all():
        for target in artifact.dependencies:
            _add(
                artifact.universal_id,
                target,
                f"UDDEP-DECL-{_slug(artifact.universal_id)}-{_slug(target)}",
                "declared",
            )

    for (_src, tgt), item in seen.items():
        if not item.attributes.get("resolved", False):
            gaps.append(tgt)

    items = tuple(sorted(seen.values(), key=lambda i: (i.references[0], i.references[1])))
    total = len(items)
    discovered = total - sum(1 for i in items if not i.attributes.get("resolved", False))
    return DimensionResult(
        kind=DiscoveryKind.DEPENDENCY,
        items=items,
        coverage=DimensionCoverage(DiscoveryKind.DEPENDENCY, discovered=discovered, total=total),
        gaps=tuple(sorted(set(gaps))),
    )


# --------------------------------------------------------------------------- 6. evidence


def discover_evidence(artifacts: ArtifactRepository) -> DimensionResult:
    """Discover the evidence each artifact carries: content hash + traceability.

    An artifact's evidence is its content-addressing (``content_hash``) and its
    requirement-to-operations ``traceability`` chain. Coverage scope is every
    artifact; an artifact's evidence is discovered iff it carries a content hash —
    the minimum evidence that makes a record verifiable. Missing hashes are gaps.
    """
    items: list[DiscoveredItem] = []
    gaps: list[str] = []
    for artifact in artifacts.all():
        has_hash = bool(artifact.content_hash)
        trace_refs = artifact.traceability.references()
        trace_stages = tuple(
            stage for stage in artifact.traceability.stages if artifact.traceability.stage(stage)
        )
        if not has_hash:
            gaps.append(artifact.universal_id)
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.EVIDENCE,
                item_id=f"UDEV-{artifact.universal_id}",
                name=artifact.name,
                source=ARTIFACTS_FILE,
                attributes={
                    "universal_id": artifact.universal_id,
                    "content_hash": artifact.content_hash,
                    "has_content_hash": has_hash,
                    "traceability_stages": list(trace_stages),
                    "traceability_reference_count": len(trace_refs),
                    "traced": bool(trace_refs),
                },
                references=trace_refs,
            )
        )
    total = artifacts.count()
    discovered = total - len(gaps)
    return DimensionResult(
        kind=DiscoveryKind.EVIDENCE,
        items=tuple(sorted(items, key=lambda i: i.item_id)),
        coverage=DimensionCoverage(DiscoveryKind.EVIDENCE, discovered=discovered, total=total),
        gaps=tuple(sorted(gaps)),
    )


# --------------------------------------------------------------------------- 7. ontology


def discover_ontology(
    artifacts: ArtifactRepository,
    graph: RelationshipGraph,
) -> DimensionResult:
    """Discover the knowledge-graph vocabulary: relationship types + taxonomy.

    The ontology is the set of terms the substrate actually uses — relationship edge
    types, artifact categories, and lifecycle statuses. Every term is derived from
    real usage (with its usage count), so coverage is complete by construction: there
    is no term the engine can fail to surface.
    """
    items: list[DiscoveredItem] = []

    for edge_type in graph.types():
        usage = len(graph.edges_of_type(edge_type))
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.ONTOLOGY,
                item_id=f"UDONT-REL-{_slug(edge_type)}",
                name=edge_type,
                source=RELATIONSHIPS_FILE,
                attributes={"term_kind": "relationship_type", "usage": usage},
            )
        )

    for category in artifacts.categories():
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.ONTOLOGY,
                item_id=f"UDONT-CAT-{_slug(category)}",
                name=category,
                source=ARTIFACTS_FILE,
                attributes={"term_kind": "category", "usage": len(artifacts.by_category(category))},
            )
        )

    for status, usage in artifacts.status_counts().items():
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.ONTOLOGY,
                item_id=f"UDONT-STATUS-{_slug(status)}",
                name=status,
                source=ARTIFACTS_FILE,
                attributes={"term_kind": "lifecycle_status", "usage": usage},
            )
        )

    total = len(items)
    return DimensionResult(
        kind=DiscoveryKind.ONTOLOGY,
        items=tuple(items),
        coverage=DimensionCoverage(DiscoveryKind.ONTOLOGY, discovered=total, total=total),
        gaps=(),
    )


# --------------------------------------------------------------------------- 8. capability


def discover_capabilities(
    artifacts: ArtifactRepository,
    volumes: VolumeRepository,
) -> DimensionResult:
    """Discover the capabilities the corpus provides: programs + realisation profile.

    A capability is a *program* — a coherent body of work — grounded in the artifacts
    that carry it. Each capability reports its member count, its realisation profile
    (how many members are in a realised lifecycle status), and the volumes it spans.
    Coverage scope is every program; a capability is discovered (realised) iff at
    least one of its members is in a realised lifecycle status. A program of only
    planned artifacts is an unrealised capability — a gap.
    """
    items: list[DiscoveredItem] = []
    gaps: list[str] = []
    for program in artifacts.programs():
        members = artifacts.by_program(program)
        realized_members = [a for a in members if _is_realized(a)]
        spanned_volumes = tuple(sorted({a.volume for a in members if a.volume}))
        realized = bool(realized_members)
        if not realized:
            gaps.append(program)
        items.append(
            DiscoveredItem(
                kind=DiscoveryKind.CAPABILITY,
                item_id=f"UDCAP-{_slug(program)}",
                name=program,
                source=ARTIFACTS_FILE,
                attributes={
                    "program": program,
                    "member_count": len(members),
                    "realized_count": len(realized_members),
                    "realized": realized,
                    "volume_span": len(spanned_volumes),
                },
                references=spanned_volumes,
            )
        )
    total = len(items)
    discovered = total - len(gaps)
    return DimensionResult(
        kind=DiscoveryKind.CAPABILITY,
        items=tuple(items),
        coverage=DimensionCoverage(DiscoveryKind.CAPABILITY, discovered=discovered, total=total),
        gaps=tuple(sorted(gaps)),
    )


__all__ = [
    "REALIZED_STATUSES",
    "discover_namespaces",
    "discover_documents",
    "discover_registries",
    "discover_components",
    "discover_dependencies",
    "discover_evidence",
    "discover_ontology",
    "discover_capabilities",
]
