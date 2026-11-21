"""UKDA Part 07/08 — Developer/Agent Handbooks + Auto Documentation Engine.

Every handbook and reference document is **generated** from the canonical
knowledge base — never authored by hand — so documentation can never drift from
the single authoritative source (the Knowledge Once Principle). Generation is
deterministic (stable ordering, no wall-clock), so regenerating an unchanged base
produces byte-identical output and a CI drift gate is trivially possible.

    * :class:`DocumentationEngine` — renders a fixed set of Markdown handbooks
      and reports (developer, architecture, decision, governance, knowledge index,
      API/contract, runtime, traceability, dependency, and the knowledge-graph
      visualization) from a :class:`~engine.knowledge.store.KnowledgeBase` and can
      materialise them to a directory.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord
from engine.knowledge.intelligence import KnowledgeIntelligence
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle, RelationType
from engine.knowledge.store import KnowledgeBase

#: The canonical handbook filenames the engine generates (Part 07).
DEVELOPER_HANDBOOK = "DEVELOPER-HANDBOOK.md"
ARCHITECTURE_HANDBOOK = "ARCHITECTURE-HANDBOOK.md"
DECISION_HANDBOOK = "DECISION-HANDBOOK.md"
GOVERNANCE_HANDBOOK = "GOVERNANCE-HANDBOOK.md"
KNOWLEDGE_INDEX = "KNOWLEDGE-INDEX.md"
#: Additional generated references (Part 07/08) — API/runtime handbooks, the
#: traceability and dependency reports, and the knowledge-graph visualization.
API_HANDBOOK = "API-HANDBOOK.md"
RUNTIME_HANDBOOK = "RUNTIME-HANDBOOK.md"
TRACEABILITY_REPORT = "TRACEABILITY-REPORT.md"
DEPENDENCY_REPORT = "DEPENDENCY-REPORT.md"
KNOWLEDGE_GRAPH = "KNOWLEDGE-GRAPH.md"

#: Lifecycle stages that describe live, runtime authority (what governs the
#: running system right now). Kept local to documentation so the runtime handbook
#: is a pure projection and never re-defines lifecycle semantics.
_RUNTIME_STAGES = (Lifecycle.IMPLEMENTED, Lifecycle.OPERATIONAL)
#: Inbound edge types that mean "this object is part of the consumed contract
#: surface" — someone depends on or consumes it.
_CONTRACT_INBOUND = (RelationType.DEPENDS_ON, RelationType.CONSUMES)

_GENERATED_BANNER = (
    "<!-- GENERATED FROM CANONICAL KNOWLEDGE — DO NOT EDIT BY HAND.\n"
    "     Author knowledge once in the canonical store; regenerate with\n"
    "     `python -m engine.knowledge.cli docs`. (UKDA Part 07/08) -->"
)


def _bullets(items: Iterable[str]) -> list[str]:
    out = [f"- {item}" for item in items]
    return out or ["- _none_"]


def _cell(items: Iterable[str]) -> str:
    """Render an iterable of ids as a single Markdown table cell (deterministic)."""
    values = list(items)
    return ", ".join(values) if values else "—"


def _inline(items: Iterable[str]) -> str:
    """Render an iterable inline, using an italic placeholder when empty."""
    values = list(items)
    return ", ".join(values) if values else "_none_"


def _safe_id(node: str) -> str:
    """Sanitise a canonical id into a Mermaid-safe node identifier."""
    return "".join(ch if ch.isalnum() else "_" for ch in node)


class DocumentationEngine:
    """Deterministically renders handbooks from the canonical knowledge base."""

    __slots__ = ("_base",)

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base

    # -- individual handbooks --------------------------------------------------

    def knowledge_index(self) -> str:
        lines = [_GENERATED_BANNER, "", "# UCOS Ω∞ — Canonical Knowledge Index", ""]
        lines.append(f"Total canonical objects: {len(self._base.objects())}")
        lines.append(f"Total decisions: {len(self._base.decisions())}")
        lines.append("")
        lines.append("| CKO ID | Kind | Authority | Lifecycle | Title |")
        lines.append("| --- | --- | --- | --- | --- |")
        for obj in self._base.objects():
            lines.append(
                f"| {obj.cko_id} | {obj.kind.value} | {obj.authority.value} "
                f"| {obj.lifecycle.value} | {obj.title} |"
            )
        lines.append("")
        return "\n".join(lines) + "\n"

    def architecture_handbook(self) -> str:
        lines = [_GENERATED_BANNER, "", "# UCOS Ω∞ — Architecture Handbook", ""]
        lines.append(
            "This handbook is generated from the canonical knowledge base. It reflects "
            "the ratified architecture; there is nothing to rediscover."
        )
        for kind in (
            KnowledgeKind.PRINCIPLE,
            KnowledgeKind.STANDARD,
            KnowledgeKind.PATTERN,
            KnowledgeKind.CONVENTION,
        ):
            objs = self._base.by_kind(kind)
            if not objs:
                continue
            lines.append("")
            lines.append(f"## {kind.value.title()}s")
            for obj in objs:
                lines.append("")
                lines.append(f"### {obj.cko_id} — {obj.title}")
                lines.append("")
                lines.append(obj.statement)
                if obj.rationale:
                    lines.append("")
                    lines.append(f"**Rationale.** {obj.rationale}")
        lines.append("")
        return "\n".join(lines) + "\n"

    def decision_handbook(self) -> str:
        lines = [_GENERATED_BANNER, "", "# UCOS Ω∞ — Decision Handbook (ADR)", ""]
        lines.append(
            "Every architectural decision is recorded once, with permanent rationale. "
            "No ratified decision requires rediscovery."
        )
        for dec in self._base.decisions():
            lines.extend(self._render_decision(dec))
        if not self._base.decisions():
            lines.append("")
            lines.append("_No decisions recorded yet._")
        lines.append("")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _render_decision(dec: DecisionRecord) -> list[str]:
        lines = ["", f"## {dec.decision_id} — {dec.title}", ""]
        lines.append(f"- **Status:** {dec.lifecycle.value}")
        lines.append(f"- **Authority:** {dec.authority.value}")
        lines.append(f"- **Owner:** {dec.owner}")
        lines.append(f"- **Review authority:** {dec.review_authority}")
        lines.append("")
        lines.append(f"**Problem.** {dec.problem_statement}")
        lines.append("")
        lines.append(f"**Context.** {dec.context}")
        lines.append("")
        lines.append(f"**Objective.** {dec.objective}")
        lines.append("")
        lines.append("**Alternatives considered.**")
        lines.extend(_bullets(dec.alternatives))
        if dec.rejected_options:
            lines.append("")
            lines.append("**Rejected options.**")
            lines.extend(_bullets(f"{r.option} — {r.reason}" for r in dec.rejected_options))
        lines.append("")
        lines.append(f"**Chosen architecture.** {dec.chosen_architecture}")
        lines.append("")
        lines.append(f"**Rationale.** {dec.rationale}")
        if dec.consequences:
            lines.append("")
            lines.append("**Consequences.**")
            lines.extend(_bullets(dec.consequences))
        if dec.risks:
            lines.append("")
            lines.append("**Risks.**")
            lines.extend(_bullets(dec.risks))
        if dec.mitigations:
            lines.append("")
            lines.append("**Mitigations.**")
            lines.extend(_bullets(dec.mitigations))
        lines.append("")
        lines.append(f"**Supersession rules.** {dec.supersession_rules}")
        return lines

    def governance_handbook(self) -> str:
        lines = [_GENERATED_BANNER, "", "# UCOS Ω∞ — Governance Handbook", ""]
        for kind in (KnowledgeKind.RULE, KnowledgeKind.POLICY, KnowledgeKind.CONSTRAINT):
            objs = self._base.by_kind(kind)
            if not objs:
                continue
            lines.append("")
            lines.append(f"## {kind.value.title()}s")
            for obj in objs:
                lines.append(
                    f"- **{obj.cko_id}** ({obj.authority.value}): {obj.title} — {obj.statement}"
                )
        exceptions = self._base.by_kind(KnowledgeKind.EXCEPTION)
        if exceptions:
            lines.append("")
            lines.append("## Documented exceptions")
            for obj in exceptions:
                lines.append(f"- **{obj.cko_id}**: {obj.title} — {obj.statement}")
        lines.append("")
        return "\n".join(lines) + "\n"

    def developer_handbook(self) -> str:
        lines = [_GENERATED_BANNER, "", "# UCOS Ω∞ — Developer Handbook", ""]
        lines.append(
            "A newly onboarded developer or AI agent needs no verbal explanation: "
            "this handbook, generated from canonical knowledge, states the why, what, "
            "and how of the repository architecture."
        )
        constitutional = self._base.by_authority(KnowledgeAuthority.CONSTITUTIONAL)
        lines.append("")
        lines.append("## Constitutional knowledge (read first)")
        for obj in constitutional:
            lines.append(f"- **{obj.cko_id}** — {obj.title}: {obj.statement}")
        if not constitutional:
            lines.append("- _none ratified yet_")
        lines.append("")
        lines.append("## Standards & conventions")
        standards = (
            *self._base.by_kind(KnowledgeKind.STANDARD),
            *self._base.by_kind(KnowledgeKind.CONVENTION),
        )
        for obj in standards:
            lines.append(f"- **{obj.cko_id}** — {obj.title}")
        lines.append("")
        lines.append("## Anti-patterns to avoid")
        anti = self._base.by_kind(KnowledgeKind.ANTI_PATTERN)
        for obj in anti:
            lines.append(f"- **{obj.cko_id}** — {obj.title}: {obj.statement}")
        if not anti:
            lines.append("- _none recorded_")
        lines.append("")
        lines.append("## Where to look next")
        lines.append(f"- Architecture: `{ARCHITECTURE_HANDBOOK}`")
        lines.append(f"- Decisions: `{DECISION_HANDBOOK}`")
        lines.append(f"- Governance: `{GOVERNANCE_HANDBOOK}`")
        lines.append(f"- Full index: `{KNOWLEDGE_INDEX}`")
        lines.append("")
        return "\n".join(lines) + "\n"

    # -- API & runtime handbooks -----------------------------------------------

    def api_handbook(self) -> str:
        """The contract/interface surface, projected from canonical knowledge.

        The "API" of the architecture is not hand-listed: it is exactly the
        standards, conventions, and patterns that define how modules interact,
        plus every canonical object that others depend on or consume (the
        published contract surface, discovered from the knowledge graph).
        """
        graph = self._base.graph()
        lines = [_GENERATED_BANNER, "", "# UCOS Ω∞ — API & Contract Handbook", ""]
        lines.append(
            "The contract surface is generated from canonical knowledge: it is the "
            "set of standards, conventions, and patterns that govern inter-module "
            "interaction, together with every object that is consumed or depended on "
            "elsewhere. Nothing here is authored twice."
        )
        for kind, heading in (
            (KnowledgeKind.STANDARD, "Contract standards"),
            (KnowledgeKind.CONVENTION, "Interface conventions"),
            (KnowledgeKind.PATTERN, "Interaction patterns"),
        ):
            objs = self._base.by_kind(kind)
            if not objs:
                continue
            lines.append("")
            lines.append(f"## {heading}")
            for obj in objs:
                lines.append("")
                lines.append(f"### {obj.cko_id} — {obj.title}")
                lines.append(f"- **Authority:** {obj.authority.value}")
                lines.append(f"- **Version:** {obj.version}")
                lines.append("")
                lines.append(obj.statement)

        lines.append("")
        lines.append("## Published contract surface")
        lines.append("")
        lines.append(
            "Objects that other canonical knowledge depends on or consumes. Each is a "
            "load-bearing contract; changing it has the listed consumers."
        )
        surface_found = False
        for obj in self._base.objects():
            consumers: dict[str, None] = {}
            for rel in _CONTRACT_INBOUND:
                for src in graph.predecessors(obj.cko_id, type=rel):
                    consumers.setdefault(src, None)
            if not consumers:
                continue
            surface_found = True
            lines.append("")
            lines.append(f"### {obj.cko_id} — {obj.title}")
            lines.append(f"- **Kind:** {obj.kind.value}")
            lines.append("- **Consumed by:**")
            lines.extend(f"  - {cid}" for cid in sorted(consumers))
        if not surface_found:
            lines.append("")
            lines.append("_No consumed contracts recorded yet._")
        lines.append("")
        return "\n".join(lines) + "\n"

    def runtime_handbook(self) -> str:
        """What governs the running system, projected from operational knowledge.

        The runtime handbook is the projection of every canonical object that is
        currently a live authority (implemented/operational) plus the rules,
        policies, and constraints that are enforced at runtime.
        """
        lines = [_GENERATED_BANNER, "", "# UCOS Ω∞ — Runtime Handbook", ""]
        lines.append(
            "This handbook is generated from the canonical knowledge that is live at "
            "runtime. It states what authority the running system operates under; "
            "there is nothing to rediscover."
        )

        live = [obj for stage in _RUNTIME_STAGES for obj in self._base.by_lifecycle(stage)]
        live.sort(key=lambda o: o.cko_id)
        lines.append("")
        lines.append("## Operational authorities")
        if live:
            by_universe: dict[str, list[CanonicalKnowledgeObject]] = {}
            for obj in live:
                by_universe.setdefault(obj.universe, []).append(obj)
            for universe in sorted(by_universe):
                lines.append("")
                lines.append(f"### Universe: {universe}")
                for obj in by_universe[universe]:
                    lines.append(
                        f"- **{obj.cko_id}** ({obj.lifecycle.value}, {obj.kind.value}): "
                        f"{obj.title} — {obj.statement}"
                    )
        else:
            lines.append("")
            lines.append("_No operational authorities recorded yet._")

        for kind, heading in (
            (KnowledgeKind.RULE, "Enforced runtime rules"),
            (KnowledgeKind.POLICY, "Runtime policies"),
            (KnowledgeKind.CONSTRAINT, "Runtime constraints"),
        ):
            objs = self._base.by_kind(kind)
            if not objs:
                continue
            lines.append("")
            lines.append(f"## {heading}")
            for obj in objs:
                lines.append(f"- **{obj.cko_id}** ({obj.authority.value}): {obj.statement}")

        guarantees = [
            obj
            for obj in self._base.by_authority(KnowledgeAuthority.CONSTITUTIONAL)
            if obj.is_active
        ]
        lines.append("")
        lines.append("## Constitutional guarantees (always in force)")
        if guarantees:
            for obj in guarantees:
                lines.append(f"- **{obj.cko_id}** — {obj.title}: {obj.statement}")
        else:
            lines.append("- _none ratified yet_")
        lines.append("")
        return "\n".join(lines) + "\n"

    # -- traceability & dependency reports -------------------------------------

    def traceability_report(self) -> str:
        """A full traceability matrix linking every object to its single source.

        Proves the Knowledge Once Principle operationally: every object traces to
        the decisions, knowledge, and dependencies it derives from, and every
        decision traces to the objects that govern and reference it.
        """
        graph = self._base.graph()
        lines = [_GENERATED_BANNER, "", "# UCOS Ω∞ — Traceability Report", ""]
        lines.append(
            "Generated from canonical links. Every canonical object traces to the "
            "decisions, knowledge, and dependencies it derives from — a single, "
            "auditable source of truth."
        )
        lines.append("")
        lines.append("## Object traceability")
        lines.append("")
        header = "| CKO ID | Kind | Decisions | Depends on | Knowledge links | Depended on by |"
        lines.append(header)
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for obj in self._base.objects():
            depended_by = sorted(
                {
                    src
                    for rel in _CONTRACT_INBOUND
                    for src in graph.predecessors(obj.cko_id, type=rel)
                }
            )
            lines.append(
                f"| {obj.cko_id} | {obj.kind.value} | {_cell(obj.decision_links)} "
                f"| {_cell(obj.dependencies)} | {_cell(obj.knowledge_links)} "
                f"| {_cell(depended_by)} |"
            )
        lines.append("")
        lines.append("## Decision traceability")
        lines.append("")
        if self._base.decisions():
            lines.append("| Decision ID | Governing objects | Referenced by |")
            lines.append("| --- | --- | --- |")
            for dec in self._base.decisions():
                referenced_by = sorted(
                    obj.cko_id
                    for obj in self._base.objects()
                    if dec.decision_id in obj.decision_links
                )
                lines.append(
                    f"| {dec.decision_id} | {_cell(dec.dependencies)} | {_cell(referenced_by)} |"
                )
        else:
            lines.append("_No decisions recorded yet._")
        lines.append("")
        return "\n".join(lines) + "\n"

    def dependency_report(self) -> str:
        """Graph analytics: direct/transitive dependencies, impact, and health."""
        intel = KnowledgeIntelligence(self._base)
        graph = intel.graph
        lines = [_GENERATED_BANNER, "", "# UCOS Ω∞ — Dependency Report", ""]
        lines.append(
            "Generated from the Universal Knowledge Graph. Shows what each object "
            "relies on, what relies on it, and the blast radius of a change."
        )
        lines.append("")
        lines.append("## Per-object dependencies & impact")
        lines.append("")
        lines.append("| Node | Depends on | Depended on by | Transitive impact | Degree |")
        lines.append("| --- | --- | --- | --- | --- |")
        node_ids = sorted(set(self._base.object_ids()) | set(graph.nodes()))
        for node in node_ids:
            lines.append(
                f"| {node} | {_cell(graph.dependencies_of(node))} "
                f"| {_cell(graph.dependents_of(node))} "
                f"| {_cell(graph.impact_of(node))} | {graph.degree(node)} |"
            )

        lines.append("")
        lines.append("## Relationship inventory")
        lines.append("")
        lines.append("| Relationship type | Edges |")
        lines.append("| --- | --- |")
        for rel in graph.types():
            lines.append(f"| {rel.value} | {len(graph.edges_of_type(rel))} |")

        lines.append("")
        lines.append("## Graph health")
        orphans = intel.find_orphans()
        broken = intel.find_broken_references()
        conflicts = intel.find_conflicts()
        duplicates = intel.find_duplicates()
        lines.append("")
        lines.append(f"- **Orphans:** {_inline(orphans)}")
        lines.append(
            "- **Broken references:** "
            + (", ".join(f"{s} → {t}" for s, t in broken) if broken else "_none_")
        )
        lines.append(
            "- **Conflicts:** "
            + (
                ", ".join(f"{c.left} ⇄ {c.right} ({c.reason})" for c in conflicts)
                if conflicts
                else "_none_"
            )
        )
        lines.append(
            "- **Duplicate knowledge:** "
            + (", ".join(" / ".join(d.cko_ids) for d in duplicates) if duplicates else "_none_")
        )
        lines.append("")
        return "\n".join(lines) + "\n"

    # -- knowledge visualization -----------------------------------------------

    def knowledge_graph(self) -> str:
        """A deterministic Mermaid rendering of the Universal Knowledge Graph."""
        graph = self._base.graph()
        lines = [_GENERATED_BANNER, "", "# UCOS Ω∞ — Knowledge Graph Visualization", ""]
        lines.append(
            "A rendering of the canonical knowledge graph, generated from the link "
            "topology of the objects themselves. Nodes are canonical objects and "
            "decisions; edges are typed, first-class relationships."
        )
        lines.append("")
        lines.append("```mermaid")
        lines.append("graph LR")
        for node in graph.nodes():
            label = self._node_label(node)
            lines.append(f'  {_safe_id(node)}["{label}"]')
        for edge in sorted(graph.all(), key=lambda e: e.key()):
            lines.append(
                f"  {_safe_id(edge.source)} -->|{edge.type.value}| {_safe_id(edge.target)}"
            )
        lines.append("```")
        lines.append("")
        lines.append("## Node legend")
        lines.append("")
        lines.append("| Node | Title |")
        lines.append("| --- | --- |")
        for node in graph.nodes():
            lines.append(f"| {node} | {self._node_label(node)} |")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _node_label(self, node: str) -> str:
        """Human-readable title for a graph node (object, decision, or bare id)."""
        obj = self._base.get_object(node)
        if obj is not None:
            return obj.title
        dec = self._base.get_decision(node)
        if dec is not None:
            return dec.title
        return node

    # -- aggregate + materialise -----------------------------------------------

    def render_all(self) -> dict[str, str]:
        """Return every handbook keyed by filename (deterministic)."""
        return {
            ARCHITECTURE_HANDBOOK: self.architecture_handbook(),
            API_HANDBOOK: self.api_handbook(),
            DECISION_HANDBOOK: self.decision_handbook(),
            DEPENDENCY_REPORT: self.dependency_report(),
            DEVELOPER_HANDBOOK: self.developer_handbook(),
            GOVERNANCE_HANDBOOK: self.governance_handbook(),
            KNOWLEDGE_GRAPH: self.knowledge_graph(),
            KNOWLEDGE_INDEX: self.knowledge_index(),
            RUNTIME_HANDBOOK: self.runtime_handbook(),
            TRACEABILITY_REPORT: self.traceability_report(),
        }

    def write_all(self, out_dir: str | Path) -> tuple[Path, ...]:
        """Write every handbook to ``out_dir`` and return the written paths."""
        target = Path(out_dir)
        target.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for filename, content in sorted(self.render_all().items()):
            path = target / filename
            path.write_text(content, encoding="utf-8")
            written.append(path)
        return tuple(written)


__all__ = [
    "DEVELOPER_HANDBOOK",
    "ARCHITECTURE_HANDBOOK",
    "DECISION_HANDBOOK",
    "GOVERNANCE_HANDBOOK",
    "KNOWLEDGE_INDEX",
    "API_HANDBOOK",
    "RUNTIME_HANDBOOK",
    "TRACEABILITY_REPORT",
    "DEPENDENCY_REPORT",
    "KNOWLEDGE_GRAPH",
    "DocumentationEngine",
]
