"""URI-000001 — the Architecture Generator.

Realizes the *structure* implied by canonical knowledge. Nothing here is designed; it is
all read out of the canonical store:

* **Layers** are the authority tiers actually present (constitutional → architectural →
  engineering → advisory). Authority precedence *is* the layering rule, so a lower layer
  may never be depended upon by a higher one — that becomes a checkable boundary rule.
* **Components** are the canonical objects themselves, carrying their kind, owner,
  lifecycle, version, and declared topology.
* **Edges** are the Universal Knowledge Graph edges internal to the target.
* **Boundary rules** are derived: every edge whose target sits in a *less* authoritative
  layer than its source is an inversion, and is reported rather than smoothed over.

Emits a machine-readable descriptor and the human-readable rendering of the same facts
(one source, two projections — never two sources).
"""

from __future__ import annotations

from typing import Any

from intelligence.realization.contracts import (
    ArtifactFamily,
    GeneratedArtifact,
    MediaKind,
)
from intelligence.realization.generators.base import GenerationContext, Generator
from intelligence.realization.knowledge import authority_rank

ARCHITECTURE_FORMAT = "ucos-uri-architecture/1.0.0"


class ArchitectureGenerator(Generator):
    """Derives the architecture descriptor for one realization target."""

    family = ArtifactFamily.ARCHITECTURE
    name = "uri.architecture"
    version = "1.0.0"

    def generate(self, context: GenerationContext) -> tuple[GeneratedArtifact, ...]:
        descriptor = self._descriptor(context)
        slug = context.target.path_slug
        return (
            self.json_artifact(
                context,
                relative_path=f"architecture/{slug}-architecture.json",
                payload=descriptor,
            ),
            self.text_artifact(
                context,
                relative_path=f"architecture/{slug}-architecture.md",
                media=MediaKind.MARKDOWN,
                lines=self._markdown(context, descriptor),
            ),
        )

    # -- derivation -----------------------------------------------------------

    def _components(self, context: GenerationContext) -> list[dict[str, Any]]:
        members = set(context.unit.bound_ckos)
        components = []
        for obj in context.objects:
            components.append(
                {
                    "component_id": obj.cko_id,
                    "name": obj.title,
                    "kind": obj.kind.value,
                    "layer": obj.authority.value,
                    "layer_rank": obj.authority.rank,
                    "owner": obj.owner,
                    "lifecycle": obj.lifecycle.value,
                    "active": obj.is_active,
                    "version": obj.version,
                    "statement": obj.statement,
                    "depends_on": sorted(obj.dependencies),
                    "consumers": sorted(obj.consumers),
                    "internal_links": sorted(ref for ref in obj.all_links() if ref in members),
                    "external_links": sorted(ref for ref in obj.all_links() if ref not in members),
                    "content_sha256": obj.content_sha256,
                }
            )
        return components

    def _layers(self, context: GenerationContext) -> list[dict[str, Any]]:
        layers = []
        for authority in context.target.authorities:
            members = sorted(
                obj.cko_id for obj in context.objects if obj.authority.value == authority
            )
            layers.append(
                {
                    "layer": authority,
                    "rank": authority_rank(authority),
                    "component_count": len(members),
                    "components": members,
                }
            )
        return sorted(layers, key=lambda entry: entry["rank"])

    def _boundary_rules(self, context: GenerationContext) -> list[dict[str, Any]]:
        """Authority precedence rendered as checkable dependency-direction rules."""
        ranks = {obj.cko_id: obj.authority.rank for obj in context.objects}
        inversions = []
        for source, relation, target in context.target.edges:
            if source not in ranks or target not in ranks:
                continue
            if ranks[target] > ranks[source]:
                inversions.append(
                    {
                        "from": source,
                        "relation": relation,
                        "to": target,
                        "finding": "authority-inversion",
                        "detail": (
                            "a more authoritative component points at a less " "authoritative one"
                        ),
                    }
                )
        return sorted(inversions, key=lambda entry: (entry["from"], entry["relation"], entry["to"]))

    def _descriptor(self, context: GenerationContext) -> dict[str, Any]:
        target = context.target
        components = self._components(context)
        layers = self._layers(context)
        inversions = self._boundary_rules(context)
        payload = context.envelope(
            artifact_id=f"UCOS-URI-ARCH-{target.path_slug.upper()}",
            title=f"{target.universe} — Realized Architecture",
            document_format=ARCHITECTURE_FORMAT,
        )
        payload.update(
            {
                "universe": target.universe,
                "target_id": target.target_id,
                "target_seal": target.seal,
                "layers": layers,
                "layering_rule": (
                    "Authority precedence is the layering rule: constitutional > "
                    "architectural > engineering > advisory. A dependency may not point "
                    "from a more authoritative layer into a less authoritative one."
                ),
                "components": components,
                "component_count": len(components),
                "edges": [
                    {"from": src, "relation": rel, "to": dst} for src, rel, dst in target.edges
                ],
                "edge_count": len(target.edges),
                "boundary_findings": inversions,
                "boundary_clean": not inversions,
                "invariants": [inv.to_dict() for inv in target.invariants],
                "patterns": list(target.patterns),
                "conventions": list(target.conventions),
                "anti_patterns": list(target.anti_patterns),
                "decisions": [
                    {
                        "decision_id": dec.decision_id,
                        "title": dec.title,
                        "chosen_architecture": dec.chosen_architecture,
                        "content_sha256": dec.content_sha256,
                    }
                    for dec in context.decisions
                ],
                "owners": list(target.owners),
                "kinds": list(target.kinds),
                "lifecycles": list(target.lifecycles),
            }
        )
        return payload

    # -- rendering ------------------------------------------------------------

    def _markdown(self, context: GenerationContext, descriptor: dict[str, Any]) -> list[str]:
        target = context.target
        lines = self.provenance_comment(context, "<!--")
        lines = [f"{line} -->" for line in lines]
        lines += [
            "",
            f"# {target.universe} — Realized Architecture",
            "",
            f"- Target: `{target.target_id}`",
            f"- Components: {descriptor['component_count']}",
            f"- Edges: {descriptor['edge_count']}",
            f"- Knowledge seal: `{context.intake.knowledge_seal}`",
            "",
            "## Layers (authority precedence)",
            "",
            "| Rank | Layer | Components |",
            "|-----:|-------|-----------:|",
        ]
        for layer in descriptor["layers"]:
            lines.append(f"| {layer['rank']} | {layer['layer']} | {layer['component_count']} |")
        lines += [
            "",
            f"> {descriptor['layering_rule']}",
            "",
            "## Components",
            "",
            "| Component | Kind | Layer | Lifecycle | Owner |",
            "|-----------|------|-------|-----------|-------|",
        ]
        for comp in descriptor["components"]:
            lines.append(
                f"| `{comp['component_id']}` | {comp['kind']} | {comp['layer']} "
                f"| {comp['lifecycle']} | {comp['owner']} |"
            )
        lines += ["", "## Internal edges", ""]
        if descriptor["edges"]:
            lines += ["| From | Relation | To |", "|------|----------|----|"]
            for edge in descriptor["edges"]:
                lines.append(f"| `{edge['from']}` | {edge['relation']} | `{edge['to']}` |")
        else:
            lines.append("_No edges internal to this universe._")
        lines += ["", "## Boundary findings", ""]
        if descriptor["boundary_findings"]:
            for finding in descriptor["boundary_findings"]:
                lines.append(
                    f"- **{finding['finding']}**: `{finding['from']}` "
                    f"-{finding['relation']}-> `{finding['to']}` — {finding['detail']}"
                )
        else:
            lines.append("None — no authority inversion detected.")
        lines += ["", "## Invariants", ""]
        for inv in descriptor["invariants"]:
            lines.append(f"- `{inv['cko_id']}` ({inv['kind']}) — {inv['statement']}")
        lines.append("")
        return lines


__all__ = ["ARCHITECTURE_FORMAT", "ArchitectureGenerator"]
