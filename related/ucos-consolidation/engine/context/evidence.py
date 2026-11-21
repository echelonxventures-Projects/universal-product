"""UCXI-000001 Part 13 — Context Evidence: the auditable artefact of the whole layer.

One deterministic document that lets a reviewer re-derive every claim the layer makes:
the constitution and its assessment, the taxonomy and ontology in force, the registry
state and its journal integrity, the resolvability of every universal kind, the
composition's frames and federations, the graph's shape, the validation report, and the
computed certificate — plus **worked exemplars** (a resolution, an impact query, an
activation trace) proving the layer is operational rather than merely constructible.

The document contains no timestamp and no machine identity, so an unchanged context set
produces byte-identical evidence and drift is visible as a changed seal. Writing reuses
the frozen-path guard (:mod:`engine.foundation.guards.frozen_paths`): evidence may never
land in the certified corpus (DP-03).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.context.catalog import bootstrap_registry, catalog_sources
from engine.context.certification import certify
from engine.context.composition import compose
from engine.context.constitution import CONTEXT_CONSTITUTION
from engine.context.errors import ContextError, ContextEvidenceError
from engine.context.graph import build_context_graph
from engine.context.registry import ContextRegistry
from engine.context.resolution import ContextRequest, resolution_report, try_resolve
from engine.context.runtime import ContextRuntime
from engine.context.validation import validate

#: Evidence document schema version (append-only, semantically versioned).
EVIDENCE_VERSION = "1.0.0"


def _exemplars(registry: ContextRegistry, composed: Any) -> dict[str, Any]:
    """Worked exemplars demonstrating the layer answers real questions."""
    graph = build_context_graph(registry)
    kinds = registry.kinds()
    subject_kind = kinds[0] if kinds else ""
    resolved, reason = (
        try_resolve(registry, ContextRequest(kind=subject_kind)) if subject_kind else (None, "")
    )

    widest = ""
    widest_radius = -1
    for context_id in graph.contexts():
        radius = graph.blast_radius(context_id)
        if radius > widest_radius:
            widest, widest_radius = context_id, radius

    activation: dict[str, Any] = {"activated": False}
    if composed is not None:
        runtime = ContextRuntime()
        with runtime.activate(composed) as active:
            activation = {
                "activated": True,
                "activation": active.to_dict(),
                "trace": runtime.trace(),
                "sample_read": {
                    "kind": subject_kind,
                    "dimension": (
                        resolved.values[0].dimension if resolved and resolved.values else ""
                    ),
                    "value": (
                        runtime.value(subject_kind, resolved.values[0].dimension)
                        if resolved and resolved.values
                        else None
                    ),
                },
            }
        activation["released"] = runtime.current() is None

    return {
        "resolution": {
            "kind": subject_kind,
            "resolved": resolved.to_dict() if resolved else None,
            "reason": reason,
        },
        "impact": {
            "subject": widest,
            "blast_radius": max(widest_radius, 0),
            "impacted": list(graph.impact_of(widest)) if widest else [],
            "dependencies": list(graph.dependencies_of(widest)) if widest else [],
            "taxon": graph.taxon_of(widest) if widest else None,
        },
        "runtime": activation,
        "resolution_order": list(graph.order_of_resolution()),
    }


def build_evidence(registry: ContextRegistry | None = None) -> dict[str, Any]:
    """Build the deterministic evidence document for a context set.

    With no registry, the universal catalog is bootstrapped, so the default document
    describes the platform's own fifteen universal contexts.
    """
    target = bootstrap_registry() if registry is None else registry
    graph = build_context_graph(target)
    composed = None
    composition_error = ""
    try:
        composed = compose(target)
    except ContextError as exc:
        composition_error = str(exc)

    report = validate(target, graph=graph, composed=composed)
    assessment = CONTEXT_CONSTITUTION.assess(target, graph=graph, composed=composed)
    certificate = certify(target, composed=composed)

    return {
        "evidence_version": EVIDENCE_VERSION,
        "authority": "NONE (DERIVED TRUTH)",
        "programme": "UCXI-000001",
        "capability": "Universal Context Intelligence",
        "constitution": {
            "laws": CONTEXT_CONSTITUTION.to_dict(),
            "assessment": assessment.to_dict(),
        },
        "taxonomy": target.taxonomy.to_dict(),
        "ontology": target.ontology.to_dict(),
        "registry": {
            "summary": target.summary(),
            "seal": target.seal(),
            "audit_intact": not target.verify_audit(),
            "audit_findings": target.verify_audit(),
            "contexts": [record.to_dict() for record in target.records()],
            "relations": [edge.to_dict() for edge in target.relations()],
        },
        "resolution": resolution_report(target),
        "composition": (
            composed.summary() if composed is not None else {"error": composition_error}
        ),
        "graph": graph.summary(),
        "validation": report.to_dict(),
        "certification": certificate.to_dict(),
        "catalog_sources": list(catalog_sources()),
        "exemplars": _exemplars(target, composed),
        "operational": bool(certificate.certified and composed is not None and report.is_valid),
    }


def _assert_writable(path: Path) -> None:
    """Refuse to write evidence into the frozen corpus (DP-03)."""
    from engine.foundation.guards.frozen_paths import find_frozen_writes

    try:
        repo_root = Path(__file__).resolve().parents[2]
        relative = path.resolve().relative_to(repo_root)
    except ValueError:
        return  # outside the repository entirely (e.g. a temporary directory)
    if find_frozen_writes([relative.as_posix()]):
        raise ContextEvidenceError(
            "refusing to write context evidence into the frozen corpus", path=str(path)
        )


def write_evidence(evidence: dict[str, Any], path: str | Path) -> Path:
    """Write the evidence document canonically (sorted keys, trailing newline)."""
    target = Path(path)
    _assert_writable(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(evidence_json(evidence), encoding="utf-8")
    return target


def evidence_index(evidence: dict[str, Any]) -> dict[str, Any]:
    """A compact index over an evidence document (what a gate needs to read)."""
    certification = evidence["certification"]
    return {
        "schema": "ucos-ucxi-context-evidence-index",
        "authority": evidence["authority"],
        "programme": evidence["programme"],
        "verdict": certification["verdict"],
        "certificate_id": certification["certificate_id"],
        "seal_sha256": certification["content_hash"],
        "seals": certification["seals"],
        "dimensions": [
            {
                "dimension_id": dimension["dimension_id"],
                "passed": dimension["passed"],
                "measured": dimension["measured"],
            }
            for dimension in certification["dimensions"]
        ],
        "universal_coverage": evidence["registry"]["summary"]["universal_covered"],
        "universal_kinds": evidence["registry"]["summary"]["universal_kinds"],
        "violations": evidence["validation"]["is_valid"],
        "operational": evidence["operational"],
    }


def evidence_json(evidence: dict[str, Any]) -> str:
    """The canonical JSON rendering of an evidence document."""
    return json.dumps(evidence, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


__all__ = [
    "EVIDENCE_VERSION",
    "build_evidence",
    "write_evidence",
    "evidence_index",
    "evidence_json",
]
