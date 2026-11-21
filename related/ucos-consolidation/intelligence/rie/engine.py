"""RepositoryIntelligenceEngine — the additive producer of repository intelligence.

Reads evidence → derives the Repository Intelligence Model → renders every
machine-readable output (the RIB among them). Holds no authority; every output
carries ``authority = "NONE (derived truth)"`` and cites its evidence state.
"""

from __future__ import annotations

import json
from typing import Any

from . import __version__
from .analysis import (
    aeos_readiness,
    digital_twin_snapshot,
    execution_frontier,
    progress,
    repository_health,
)
from .canonical import canonical_json, sealed
from .census import full_census
from .config import FileSink, OutputSink, RepoConfig
from .discovery import discover
from .drift import detect
from .evidence import EvidenceReader
from .knowledge import KNOWN_SPINE_GAPS

_AUTHORITY = "NONE (derived truth)"
_SNAPSHOT_FILE = "UCOS-RIE-MODEL.json"


def _envelope(reader: EvidenceReader, artifact_id: str, title: str) -> dict[str, Any]:
    """Common, deterministic header. No wall-clock — identity is the evidence state."""
    return {
        "artifact_id": artifact_id,
        "title": title,
        "producer": f"UCOS-RIE-001 Repository Intelligence Engine v{__version__}",
        "authority": _AUTHORITY,
        "classification": "ADDITIVE INTELLIGENCE (machine-readable) — derived, non-authoritative",
        "generation": reader.generation_state(),
        "evidence_state": reader.state_fingerprint(),
        "evidence_timestamp": reader.control_tower().get("generated_at"),
    }


def _dependency_graph(reader: EvidenceReader) -> dict[str, Any]:
    """Program→program dependency edges derived from artifacts.json + acyclicity fact."""
    arts = reader.artifacts().get("artifacts", [])
    prog_of: dict[str, str] = {}
    for a in arts:
        prog = a.get("program")
        for key in (a.get("universal_id"), a.get("native_id")):
            if key:
                prog_of[key] = prog
    edges: dict[tuple[str, str], int] = {}
    for a in arts:
        src = a.get("program")
        for dep in a.get("dependencies", []) or []:
            dst = prog_of.get(dep)
            if dst and src and dst != src:
                edges[(src, dst)] = edges.get((src, dst), 0) + 1
    cert = reader.certification()
    kg = cert.get("domains", {}).get("knowledge_graph", {})
    return {
        "program_edges": [{"from": s, "to": d, "count": n} for (s, d), n in sorted(edges.items())],
        "program_edge_count": len(edges),
        "total_corpus_edges": reader.control_tower().get("portfolio", {}).get("total_edges"),
        "depends_on_acyclic": kg.get("pass") if kg else None,
        "layered_architecture_bottom_up": [
            "LAW Ω∞-000",
            "MIP v2 (28 universes · 25 directives) + ARCH-001..004",
            "UCGF + GOV-001..006",
            "Domain constitutions (02-MASTER) + bands 03-13",
            "CIOA spec → CCE spec",
            "EC-1 engine/",
            "EC-2 platform/ (composes EC-1)",
            "UKB/UKBX + control-tower/twin/artifacts",
            "MCS (00-MASTER)",
            "[FUTURE] AEOS execution spine",
            "[FUTURE] adapters + universal CLI",
        ],
    }


def build_model(reader: EvidenceReader) -> dict[str, Any]:
    """Derive the full, deterministic Repository Intelligence Model (no drift, no wall-clock)."""
    census = full_census(reader)
    # UCOS-CL-005: the canonical model no longer reads coverage. coverage.xml is
    # TEST_EXECUTION_STATE — gitignored, absent from every pristine clone — so any value
    # derived from it made these tracked, content-hashed outputs irreproducible across
    # clones. Coverage remains available through EvidenceReader.coverage() for the
    # NON-canonical surfaces that legitimately report it (portal, knowledge store,
    # research corpus), all of which emit to ignored or untracked paths.
    caps = [c.as_dict() for c in discover(reader)]
    health = repository_health(reader, census)
    prog = progress(reader, census)
    frontier = execution_frontier(reader)
    twin = digital_twin_snapshot(reader, health, prog)
    aeos = aeos_readiness(reader, caps)
    depgraph = _dependency_graph(reader)
    model = _envelope(reader, "UCOS-RIE-MODEL", "Repository Intelligence Model")
    model.update(
        {
            "capabilities": caps,
            "capability_count": len(caps),
            "health": health,
            "progress": prog,
            "execution_frontier": frontier,
            "dependency_graph": depgraph,
            "digital_twin": twin,
            "aeos_readiness": aeos,
        }
    )
    return model


class RepositoryIntelligenceEngine:
    def __init__(self, config: RepoConfig | None = None) -> None:
        self.config = config or RepoConfig.create()
        self.reader = EvidenceReader(self.config)

    # -- core ------------------------------------------------------------
    def model(self) -> dict[str, Any]:
        return build_model(self.reader)

    def _prior_model(self) -> dict[str, Any] | None:
        path = self.config.output_dir / _SNAPSHOT_FILE
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    # -- outputs ---------------------------------------------------------
    def outputs(self, prior: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
        """Render every machine-readable output as {filename: sealed_payload}."""
        model = self.model()
        r = self.reader
        drift = detect(model, prior if prior is not None else self._prior_model())

        snapshot = _envelope(r, "UCOS-RIE-SNAPSHOT", "Repository Intelligence Snapshot")
        snapshot.update(
            {
                "capability_count": model["capability_count"],
                "overall_health": model["health"]["overall"],
                "dimension_index_reconciled_pct": model["progress"][
                    "dimension_index_reconciled_pct"
                ],
                "next_executable_capability": model["execution_frontier"].get(
                    "next_executable_capability"
                ),
                "aeos_verdict": model["aeos_readiness"]["verdict"],
                "drift": drift,
            }
        )

        cap_catalog = _envelope(r, "UCOS-RIE-CAPABILITY-CATALOG", "Capability Intelligence Catalog")
        cap_catalog.update(
            {"capabilities": model["capabilities"], "count": model["capability_count"]}
        )

        depgraph = _envelope(r, "UCOS-RIE-DEPENDENCY-GRAPH", "Dependency Intelligence Graph")
        depgraph.update(model["dependency_graph"])

        prog_out = _envelope(r, "UCOS-RIE-PROGRESS", "Progress Intelligence Report")
        prog_out.update(model["progress"])

        health_out = _envelope(r, "UCOS-RIE-HEALTH", "Repository Health Report")
        health_out.update(model["health"])

        twin_out = _envelope(r, "UCOS-RIE-DIGITAL-TWIN", "Repository Digital Twin Snapshot")
        twin_out.update(model["digital_twin"])

        frontier_out = _envelope(r, "UCOS-RIE-EXECUTION-FRONTIER", "Execution Frontier Report")
        frontier_out.update(model["execution_frontier"])

        aeos_out = _envelope(r, "UCOS-RIE-AEOS-READINESS", "AEOS Readiness Report")
        aeos_out.update(model["aeos_readiness"])

        rib = self._render_rib(model)

        payloads = {
            _SNAPSHOT_FILE: model,
            "UCOS-RIE-SNAPSHOT.json": snapshot,
            "UCOS-RIE-CAPABILITY-CATALOG.json": cap_catalog,
            "UCOS-RIE-DEPENDENCY-GRAPH.json": depgraph,
            "UCOS-RIE-PROGRESS.json": prog_out,
            "UCOS-RIE-HEALTH.json": health_out,
            "UCOS-RIE-DIGITAL-TWIN.json": twin_out,
            "UCOS-RIE-EXECUTION-FRONTIER.json": frontier_out,
            "UCOS-RIE-AEOS-READINESS.json": aeos_out,
            "UCOS-IMP-BASELINE-001.rib.json": rib,
        }
        return {name: sealed(payload) for name, payload in payloads.items()}

    def _render_rib(self, model: dict[str, Any]) -> dict[str, Any]:
        """Regenerate the Repository Implementation Baseline as an RIE output."""
        rib = _envelope(
            self.reader,
            "UCOS-IMP-BASELINE-001",
            "Repository Implementation Baseline (generated by RIE)",
        )
        rib.update(
            {
                "note": "This baseline is now a GENERATED OUTPUT of UCOS-RIE-001. It replaces the "
                "hand-authored baseline as the machine-readable source and is regenerated "
                "deterministically from evidence on every repository change.",
                "capability_inventory": model["capabilities"],
                "repository_health": model["health"],
                "progress": model["progress"],
                "dependency_graph": model["dependency_graph"],
                "execution_frontier": model["execution_frontier"],
                "digital_twin_snapshot": model["digital_twin"],
                "aeos_readiness": model["aeos_readiness"],
                "known_spine_gaps": KNOWN_SPINE_GAPS,
            }
        )
        return rib

    def write(self, sink: OutputSink | None = None) -> list[str]:
        target = sink or FileSink(self.config.output_dir)
        written = []
        for name, payload in self.outputs().items():
            written.append(target.emit(name, canonical_json(payload)))
        return sorted(written)

    # -- determinism proof ----------------------------------------------
    def verify_determinism(self) -> dict[str, Any]:
        """Prove identical repository state ⇒ identical outputs (byte-level)."""
        a = self.outputs(prior=None)
        b = self.outputs(prior=None)
        mismatches = [name for name in a if canonical_json(a[name]) != canonical_json(b[name])]
        return {
            "deterministic": not mismatches,
            "outputs_checked": sorted(a),
            "mismatches": mismatches,
            "model_content_hash": sealed(self.model())["content_hash"],
        }
