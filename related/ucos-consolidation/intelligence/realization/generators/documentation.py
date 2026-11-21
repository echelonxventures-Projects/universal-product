"""URI-000001 — the Documentation Generator.

Realizes canonical knowledge as prose. This generator is the direct operationalisation of
the Knowledge Once Principle (``UCKO-PRIN-0001``) and its anti-pattern
(``UCKO-ANTI-0001`` Knowledge Duplication): documentation is *never* a copy of a decision
kept in a second place. It is a projection, regenerated from the single canonical source,
and every claim it makes cites the canonical id it came from.

Three documents per target:

* the universe handbook — every canonical object, grouped by authority tier, each entry
  citing its id, kind, owner, lifecycle, version and content hash;
* the decision record digest — problem, alternatives, rejected options *with reasons*, and
  consequences, so a future reader never has to rediscover a decision;
* the realization map — which artifact realizes which canonical object, in which family.

One repository-wide index is also emitted, by the lexicographically first target only, so
the path is claimed exactly once no matter how many targets exist.
"""

from __future__ import annotations

from engine.knowledge.cko import CanonicalKnowledgeObject
from intelligence.realization.contracts import (
    FAMILY_ORDER,
    ArtifactFamily,
    GeneratedArtifact,
    MediaKind,
)
from intelligence.realization.generators.base import GenerationContext, Generator

INDEX_PATH = "docs/index.md"


class DocumentationGenerator(Generator):
    """Projects canonical knowledge into generated, citation-bearing documentation."""

    family = ArtifactFamily.DOCUMENTATION
    name = "uri.documentation"
    version = "1.0.0"

    def generate(self, context: GenerationContext) -> tuple[GeneratedArtifact, ...]:
        slug = context.target.path_slug
        artifacts = [
            self.text_artifact(
                context,
                relative_path=f"docs/{slug}.md",
                media=MediaKind.MARKDOWN,
                lines=self._handbook(context),
            ),
            self.text_artifact(
                context,
                relative_path=f"docs/{slug}-decisions.md",
                media=MediaKind.MARKDOWN,
                lines=self._decisions(context),
            ),
            self.text_artifact(
                context,
                relative_path=f"docs/{slug}-realization-map.md",
                media=MediaKind.MARKDOWN,
                lines=self._realization_map(context),
            ),
        ]
        if self._owns_index(context):
            artifacts.append(
                self.text_artifact(
                    context,
                    relative_path=INDEX_PATH,
                    media=MediaKind.MARKDOWN,
                    lines=self._index(context),
                )
            )
        return tuple(artifacts)

    # -- index ownership ------------------------------------------------------

    @staticmethod
    def _owns_index(context: GenerationContext) -> bool:
        """The first target by id owns the shared index, so the path is claimed once."""
        first = min(target.target_id for target in context.plan.targets)
        return context.target.target_id == first

    # -- rendering ------------------------------------------------------------

    def _header(self, context: GenerationContext, title: str) -> list[str]:
        lines = [f"{line} -->" for line in self.provenance_comment(context, "<!--")]
        lines += ["", f"# {title}", ""]
        return lines

    def _handbook(self, context: GenerationContext) -> list[str]:
        target = context.target
        lines = self._header(
            context, f"{target.universe} — Canonical Knowledge Handbook (generated)"
        )
        lines += [
            "> This handbook is **generated** from the UKDA canonical knowledge store. It",
            "> contains no independent authority and no copied decision text is authored",
            "> here — every statement below is a projection of the canonical object cited",
            "> beside it (`UCKO-PRIN-0001`, `UCKO-ANTI-0001`).",
            "",
            f"- Universe: **{target.universe}**",
            f"- Target: `{target.target_id}`",
            f"- Canonical objects: {len(target.cko_ids)}",
            f"- Normative invariants: {len(target.invariants)}",
            f"- Owners: {', '.join(target.owners)}",
            f"- Knowledge seal: `{context.intake.knowledge_seal}`",
            "",
            "## Contents by authority tier",
            "",
        ]
        for authority in target.authorities:
            members = [obj for obj in context.objects if obj.authority.value == authority]
            lines += [f"### {authority.capitalize()} ({len(members)})", ""]
            for obj in members:
                lines.extend(self._entry(obj))
            lines.append("")
        lines += ["## Normative invariants", ""]
        if target.invariants:
            for inv in target.invariants:
                lines.append(
                    f"- **`{inv.cko_id}`** ({inv.kind}, {inv.authority}) — {inv.statement}"
                )
        else:
            lines.append("_This universe declares no normative invariant._")
        lines += ["", "## Patterns, conventions and anti-patterns", ""]
        for label, ids in (
            ("Patterns", target.patterns),
            ("Conventions", target.conventions),
            ("Anti-patterns", target.anti_patterns),
        ):
            rendered = ", ".join(f"`{cko_id}`" for cko_id in ids) or "_none_"
            lines.append(f"- **{label}**: {rendered}")
        lines.append("")
        return lines

    @staticmethod
    def _entry(obj: CanonicalKnowledgeObject) -> list[str]:
        lines = [
            f"#### `{obj.cko_id}` — {obj.title}",
            "",
            f"- Kind: `{obj.kind.value}` · Authority: `{obj.authority.value}` · "
            f"Lifecycle: `{obj.lifecycle.value}` · Version: `{obj.version}`",
            f"- Owner: `{obj.owner}`",
            f"- Content hash: `{obj.content_sha256}`",
            "",
            f"{obj.statement}",
            "",
        ]
        if obj.rationale:
            lines += [f"**Rationale.** {obj.rationale}", ""]
        links = obj.all_links()
        if links:
            lines += [
                "Links: " + ", ".join(f"`{ref}`" for ref in links),
                "",
            ]
        return lines

    def _decisions(self, context: GenerationContext) -> list[str]:
        target = context.target
        lines = self._header(context, f"{target.universe} — Canonical Decision Digest (generated)")
        lines += [
            "> A decision is recorded once and never rediscovered. Rejected options are",
            "> retained **with their reasons** so a future reader cannot re-litigate a",
            "> settled question without new information.",
            "",
        ]
        if not context.decisions:
            lines += [
                "_No canonical decision record is linked from this universe._",
                "",
                "This is a coverage observation, not a defect: the universe's authority",
                "derives from its canonical objects, which cite no separate decision record.",
                "",
            ]
            return lines
        for dec in context.decisions:
            lines += [
                f"## `{dec.decision_id}` — {dec.title}",
                "",
                f"- Authority: `{dec.authority.value}` · Lifecycle: "
                f"`{dec.lifecycle.value}` · Version: `{dec.version}`",
                f"- Owner: `{dec.owner}` · Review authority: `{dec.review_authority}`",
                f"- Content hash: `{dec.content_sha256}`",
                f"- Reviewable record: `{dec.is_reviewable}`",
                "",
                f"**Problem.** {dec.problem_statement}",
                "",
                f"**Context.** {dec.context}",
                "",
                f"**Objective.** {dec.objective}",
                "",
                f"**Chosen architecture.** {dec.chosen_architecture}",
                "",
                f"**Rationale.** {dec.rationale}",
                "",
            ]
            if dec.alternatives:
                lines += ["**Alternatives considered.**", ""]
                lines += [f"- {alt}" for alt in dec.alternatives]
                lines.append("")
            if dec.rejected_options:
                lines += ["**Rejected options and why.**", ""]
                lines += [f"- _{opt.option}_ — {opt.reason}" for opt in dec.rejected_options]
                lines.append("")
            for label, values in (
                ("Evaluation criteria", dec.evaluation_criteria),
                ("Tradeoffs", dec.tradeoffs),
                ("Consequences", dec.consequences),
                ("Risks", dec.risks),
                ("Mitigations", dec.mitigations),
                ("Certification requirements", dec.certification_requirements),
            ):
                if values:
                    lines += [f"**{label}.**", ""]
                    lines += [f"- {value}" for value in values]
                    lines.append("")
            if dec.supersession_rules:
                lines += [f"**Supersession rules.** {dec.supersession_rules}", ""]
        return lines

    def _realization_map(self, context: GenerationContext) -> list[str]:
        target = context.target
        lines = self._header(context, f"{target.universe} — Realization Map (generated)")
        lines += [
            "> Which artifact realizes this universe, in which family, and from which",
            "> canonical objects. This is the human-readable face of the traceability",
            "> ledger; the machine-readable form is the URI traceability artifact.",
            "",
            "| Family | Artifact |",
            "|--------|----------|",
        ]
        for family in FAMILY_ORDER:
            for path in context.upstream_paths(family):
                lines.append(f"| {family.value} | `{path}` |")
        lines += [
            f"| {ArtifactFamily.DOCUMENTATION.value} | `docs/{target.path_slug}.md` |",
            f"| {ArtifactFamily.DOCUMENTATION.value} | "
            f"`docs/{target.path_slug}-decisions.md` |",
            f"| {ArtifactFamily.DOCUMENTATION.value} | "
            f"`docs/{target.path_slug}-realization-map.md` |",
            "",
            "## Source canonical objects",
            "",
        ]
        for obj in context.objects:
            lines.append(
                f"- `{obj.cko_id}` — {obj.title} ({obj.kind.value}, {obj.authority.value})"
            )
        lines.append("")
        return lines

    def _index(self, context: GenerationContext) -> list[str]:
        lines = self._header(context, "Realized Canonical Knowledge — Index (generated)")
        lines += [
            "> Generated by URI-000001 from the UKDA canonical knowledge store. Every",
            "> document under `docs/` is a projection of canonical knowledge; edit the",
            "> canonical store, never these files.",
            "",
            f"- Knowledge seal: `{context.intake.knowledge_seal}`",
            f"- Realization plan: `{context.composition.plan_id}`",
            f"- Targets: {len(context.plan.targets)}",
            "",
            "## Universes",
            "",
            "| Universe | Target | Objects | Invariants | Handbook |",
            "|----------|--------|--------:|-----------:|----------|",
        ]
        for target in sorted(context.plan.targets, key=lambda t: t.target_id):
            lines.append(
                f"| {target.universe} | `{target.target_id}` | {len(target.cko_ids)} "
                f"| {len(target.invariants)} | `docs/{target.path_slug}.md` |"
            )
        lines += [
            "",
            "## Artifact families",
            "",
            "| Family | Realizes |",
            "|--------|----------|",
            "| architecture | authority layers, components, edges, boundary findings |",
            "| schema | inferred JSON Schema + ANSI SQL projection of the record contract |",
            "| api | read-only OpenAPI surface + framework-neutral route table |",
            "| runtime | runtime descriptor + executable mechanical invariant checks |",
            "| deployment | UCIC-001 gate ladder, deployables, non-destructive rollback |",
            "| test | executable assertions derived from canonical facts |",
            "| documentation | this index, handbooks, decision digests, realization maps |",
            "",
        ]
        return lines


__all__ = ["INDEX_PATH", "DocumentationGenerator"]
