"""EPIC-DOC-002 — Universal Constitutional Knowledge Portal.

Transforms the fixed set of flat handbooks emitted by the
:class:`~engine.knowledge.docs.DocumentationEngine` (UKDA Part 07/08) into a single,
navigable **constitutional knowledge portal**: a cross-linked family of generated
pages, each a pure projection of the canonical knowledge base and its derived
analytics. Nothing on any page is authored here — every portal is derived from the
Universal Knowledge & Decision Architecture (UKDA, EPIC-UKDA) and the Universal
Constitutional Knowledge Integration engines (UKI, EPIC-UKDA-002), reused verbatim:

    * Architecture, Governance, Traceability, Dependency, Execution, Visualization —
      projected through the :class:`~engine.knowledge.docs.DocumentationEngine`.
    * Capability, Universe, EPIC, Implementation, Repository — projected from the
      canonical objects/decisions and the Universal Knowledge Graph.
    * Validation — the fail-closed :func:`~engine.knowledge.validation.validate_base`
      suite (Part 10); Certification — :func:`~engine.knowledge.certification.certify_base`
      (Part 11); Coverage — the :class:`~engine.knowledge.intelligence.CoverageReport`.
    * Search — a deterministic, offline inverted index over the exact tokens the
      institutional-memory search matches.

Every artifact references its constitutional origin (the transitive constitutional
providers resolved by the UKI
:class:`~engine.knowledge.integration.traceability.TraceabilityEngine`),
every page links to every other (a generated navigation bar), and generation is
deterministic (stable ordering, no wall-clock) so an unchanged base regenerates
byte-identically and a CI drift gate is trivial. The Knowledge Once Principle is
preserved: the portal is a second *view*, never a second *source* — zero duplicate
documentation.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from engine.knowledge.certification import (
    KNOWLEDGE_CERTIFICATION_AUTHORITY,
    certify_base,
)
from engine.knowledge.docs import DocumentationEngine
from engine.knowledge.integration.constitution import integration_constitution
from engine.knowledge.integration.dependency import DependencyIntegration
from engine.knowledge.integration.governance import GOVERNANCE_KINDS, GovernanceIntegration
from engine.knowledge.integration.ownership import OwnershipProtocol
from engine.knowledge.integration.traceability import TraceabilityEngine
from engine.knowledge.intelligence import KnowledgeIntelligence
from engine.knowledge.model import KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.validation import validate_base

#: The single navigable entry point of the portal.
PORTAL_INDEX = "INDEX.md"

#: The fifteen generated portal filenames (EPIC-DOC-002).
ARCHITECTURE_PORTAL = "ARCHITECTURE-PORTAL.md"
CAPABILITY_PORTAL = "CAPABILITY-PORTAL.md"
UNIVERSE_PORTAL = "UNIVERSE-PORTAL.md"
EPIC_PORTAL = "EPIC-PORTAL.md"
IMPLEMENTATION_PORTAL = "IMPLEMENTATION-PORTAL.md"
VALIDATION_PORTAL = "VALIDATION-PORTAL.md"
CERTIFICATION_PORTAL = "CERTIFICATION-PORTAL.md"
TRACEABILITY_PORTAL = "TRACEABILITY-PORTAL.md"
REPOSITORY_PORTAL = "REPOSITORY-PORTAL.md"
DEPENDENCY_PORTAL = "DEPENDENCY-PORTAL.md"
EXECUTION_PORTAL = "EXECUTION-PORTAL.md"
COVERAGE_PORTAL = "COVERAGE-PORTAL.md"
GOVERNANCE_PORTAL = "GOVERNANCE-PORTAL.md"
SEARCH_PORTAL = "SEARCH-PORTAL.md"
VISUALIZATION_PORTAL = "VISUALIZATION-PORTAL.md"

#: The ordered portal registry — the single source of truth for the index table and
#: the navigation bar (both are derived from it, never hand-listed twice).
PORTALS: tuple[tuple[str, str, str], ...] = (
    (
        ARCHITECTURE_PORTAL,
        "Architecture",
        "Ratified principles, standards, patterns, and conventions.",
    ),
    (
        CAPABILITY_PORTAL,
        "Capability",
        "Adopted capabilities (canonical DECISION objects) and their origin.",
    ),
    (UNIVERSE_PORTAL, "Universe", "Every canonical object grouped by its universe."),
    (
        EPIC_PORTAL,
        "EPIC",
        "Program-level decision records and the knowledge that realises them.",
    ),
    (
        IMPLEMENTATION_PORTAL,
        "Implementation",
        "Live knowledge (implemented/operational) with evidence.",
    ),
    (VALIDATION_PORTAL, "Validation", "The fail-closed knowledge validation suite (Part 10)."),
    (
        CERTIFICATION_PORTAL,
        "Certification",
        "The completeness certification of every object (Part 11).",
    ),
    (
        TRACEABILITY_PORTAL,
        "Traceability",
        "Object/decision matrix + the constitutional chain per artifact.",
    ),
    (
        REPOSITORY_PORTAL,
        "Repository",
        "A repository-wide map: owners, universes, kinds, ownership integrity.",
    ),
    (
        DEPENDENCY_PORTAL,
        "Dependency",
        "Dependencies, dependents, and transitive impact from the graph.",
    ),
    (
        EXECUTION_PORTAL,
        "Execution",
        "What governs the running system + the constitutional execution path.",
    ),
    (COVERAGE_PORTAL, "Coverage", "Coverage/consistency of the canonical base and its gaps."),
    (
        GOVERNANCE_PORTAL,
        "Governance",
        "Rules, policies, constraints + governance grounding (UKI-LAW-007).",
    ),
    (
        SEARCH_PORTAL,
        "Search",
        "A deterministic, offline inverted search index over every object.",
    ),
    (
        VISUALIZATION_PORTAL,
        "Visualization",
        "A deterministic Mermaid rendering of the knowledge graph.",
    ),
)

#: Title lookup by filename (includes the portal home).
_TITLE_BY_FILE: dict[str, str] = {PORTAL_INDEX: "Constitutional Knowledge Portal"}
_TITLE_BY_FILE.update({filename: f"{title} Portal" for filename, title, _ in PORTALS})

_BANNER = (
    "<!-- GENERATED CONSTITUTIONAL KNOWLEDGE PORTAL — DO NOT EDIT BY HAND.\n"
    "     100% derived from the canonical knowledge base; author knowledge once and\n"
    "     regenerate with `python -m engine.knowledge.cli portal`. (EPIC-DOC-002) -->"
)


def _cell(items: Iterable[str]) -> str:
    """Render an iterable of ids as one Markdown table cell (em dash when empty)."""
    values = list(items)
    return ", ".join(values) if values else "—"


def _bullets(items: Iterable[str]) -> list[str]:
    out = [f"- {item}" for item in items]
    return out or ["- _none_"]


class KnowledgePortal:
    """Deterministically renders the navigable constitutional knowledge portal.

    The portal is a *presentation* layer: it reuses the UKDA generators and the UKI
    integration engines verbatim and adds only cross-linked navigation and the
    per-artifact constitutional origin. It never re-derives knowledge semantics.
    """

    __slots__ = ("_base", "_docs", "_intel", "_trace", "_deps")

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base
        self._docs = DocumentationEngine(base)
        self._intel = KnowledgeIntelligence(base)
        self._trace = TraceabilityEngine(base)
        self._deps = DependencyIntegration(base)

    # -- chrome (navigation + page assembly) -----------------------------------

    def _nav(self, current: str) -> str:
        """A generated navigation bar linking every portal; the current page is bold."""
        parts: list[str] = []
        home = "**Home**" if current == PORTAL_INDEX else f"[Home]({PORTAL_INDEX})"
        parts.append(home)
        for filename, title, _ in PORTALS:
            if filename == current:
                parts.append(f"**{title}**")
            else:
                parts.append(f"[{title}]({filename})")
        return "**Portals:** " + " · ".join(parts)

    def _page(self, filename: str, derivation: str, body: list[str]) -> str:
        """Assemble a portal page: banner, nav, title, derivation note, body, nav."""
        title = _TITLE_BY_FILE[filename]
        lines = [
            _BANNER,
            "",
            self._nav(filename),
            "",
            f"# UCOS Ω∞ — {title}",
            "",
            f"> {derivation}",
            "",
        ]
        lines.extend(body)
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(self._nav(filename))
        lines.append("")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _doc_body(document: str) -> list[str]:
        """Strip a DocumentationEngine render's banner + H1, returning the body lines.

        Reusing the canonical handbook body (rather than re-implementing it) is what
        keeps the portal a second view and never a second source (zero duplication).
        """
        lines = document.split("\n")
        for index, line in enumerate(lines):
            if line.startswith("# "):
                body = lines[index + 1 :]
                while body and body[0] == "":
                    body.pop(0)
                while body and body[-1] == "":
                    body.pop()
                return body
        return lines

    def _origin(self, cko_id: str) -> tuple[str, ...]:
        """The transitive constitutional providers of an object (its origin).

        Delegates to the UKI traceability engine's ``constitution`` stage so the
        portal's notion of "constitutional origin" is identical to the one the
        constitutional execution path enforces.
        """
        chain = self._trace.trace(cko_id)
        stage = chain.stage("constitution")
        return stage.references if stage is not None else ()

    # -- portal home -----------------------------------------------------------

    def index(self) -> str:
        base = self._base
        body = [
            "The single navigable entry point to the constitutional knowledge portal. "
            f"Every page below is generated from the canonical knowledge base "
            f"(**{len(base.objects())}** objects, **{len(base.decisions())}** decisions); "
            "nothing is handwritten, everything is linked, and regeneration is "
            "byte-identical.",
            "",
            "## Portals",
            "",
            "| # | Portal | What it projects |",
            "| --- | --- | --- |",
        ]
        for position, (filename, title, purpose) in enumerate(PORTALS, start=1):
            body.append(f"| {position} | [{title}]({filename}) | {purpose} |")
        body.append("")
        body.append("## Canonical state")
        body.append("")
        body.append(f"- **Objects:** {len(base.objects())}")
        body.append(f"- **Decisions:** {len(base.decisions())}")
        active = len(base.active_objects())
        body.append(f"- **Active (ratified/implemented/operational):** {active}")
        universes = sorted({obj.universe for obj in base.objects()})
        body.append(f"- **Universes:** {_cell(universes)}")
        return self._page(
            PORTAL_INDEX,
            "Everything derived. Everything linked. Everything deterministic.",
            body,
        )

    # -- projected-from-handbook portals ---------------------------------------

    def architecture(self) -> str:
        return self._page(
            ARCHITECTURE_PORTAL,
            "Projected from canonical knowledge (UKDA Part 07): the ratified architecture.",
            self._doc_body(self._docs.architecture_handbook()),
        )

    def governance(self) -> str:
        body = self._doc_body(self._docs.governance_handbook())
        body.append("")
        body.append("## Governance grounding (UKI-LAW-007)")
        body.append("")
        body.append(
            "Every governance-kind object must reference canonical knowledge and a "
            "constitutional law. Grounding is resolved from the object's own links."
        )
        body.append("")
        governance = [obj for obj in self._base.objects() if obj.kind in GOVERNANCE_KINDS]
        if governance:
            binder = GovernanceIntegration(self._base)
            body.append("| Object | Grounded | Knowledge | Laws | Evidence |")
            body.append("| --- | --- | --- | --- | --- |")
            for obj in governance:
                ref = binder.bind_object(obj.cko_id)
                body.append(
                    f"| {obj.cko_id} | {'yes' if ref.grounded else 'no'} "
                    f"| {_cell(ref.knowledge)} | {_cell(ref.laws)} | {_cell(ref.evidence)} |"
                )
        else:
            body.append("_No governance objects recorded yet._")
        return self._page(
            GOVERNANCE_PORTAL,
            "Projected from canonical knowledge (UKDA Part 07) + governance grounding (UKI D8).",
            body,
        )

    def dependency(self) -> str:
        return self._page(
            DEPENDENCY_PORTAL,
            "Projected from the Universal Knowledge Graph (UKDA Part 05/08).",
            self._doc_body(self._docs.dependency_report()),
        )

    def visualization(self) -> str:
        return self._page(
            VISUALIZATION_PORTAL,
            "A deterministic Mermaid projection of the knowledge graph (UKDA Part 08).",
            self._doc_body(self._docs.knowledge_graph()),
        )

    def traceability(self) -> str:
        body = self._doc_body(self._docs.traceability_report())
        body.append("")
        body.append("## Constitutional chains")
        body.append("")
        body.append(
            "The end-to-end chain per artifact (UKI-LAW-006): Constitution → Universe → "
            "Capability → Implementation → Validation → Certification → Evidence → "
            "Deployment → Runtime. Every artifact references its constitutional origin."
        )
        body.append("")
        objects = self._base.objects()
        if objects:
            body.append("| CKO ID | Complete | Constitutional origin | Gaps |")
            body.append("| --- | --- | --- | --- |")
            for obj in objects:
                chain = self._trace.trace(obj.cko_id)
                body.append(
                    f"| {obj.cko_id} | {'yes' if chain.complete else 'no'} "
                    f"| {_cell(self._origin(obj.cko_id))} | {_cell(chain.gaps)} |"
                )
        else:
            body.append("_No canonical objects recorded yet._")
        return self._page(
            TRACEABILITY_PORTAL,
            "Projected from canonical links (UKDA Part 08) + constitutional chains (UKI D7).",
            body,
        )

    def execution(self) -> str:
        body = self._doc_body(self._docs.runtime_handbook())
        body.append("")
        body.append("## Constitutional execution path")
        body.append("")
        body.append(
            "The ordered, fail-closed sequence every future capability follows before "
            "an artifact is created (UKI, EPIC-UKDA-002), with the laws bound to each stage."
        )
        constitution = integration_constitution()
        for stage in constitution.sequence:
            body.append("")
            body.append(f"### {stage.value.title()}")
            laws = constitution.laws_for_stage(stage)
            body.extend(_bullets(f"**{law.law_id}** — {law.title}" for law in laws))
        return self._page(
            EXECUTION_PORTAL,
            "Projected from operational knowledge (UKDA Part 07) + the execution path (UKI D1).",
            body,
        )

    # -- projected-from-base portals -------------------------------------------

    def capability(self) -> str:
        body = [
            "Each capability is a canonical **DECISION** object — an adopted, ratified "
            "capability of the system. Every capability traces to its permanent decision "
            "record and to the constitutional knowledge it derives from.",
        ]
        capabilities = self._base.by_kind(KnowledgeKind.DECISION)
        if not capabilities:
            body.append("")
            body.append("_No capabilities recorded yet._")
            return self._page(CAPABILITY_PORTAL, self._capability_note(), body)
        for obj in capabilities:
            view = self._deps.view(obj.cko_id)
            body.append("")
            body.append(f"## {obj.cko_id} — {obj.title}")
            body.append("")
            body.append(f"- **Authority:** {obj.authority.value}")
            body.append(f"- **Lifecycle:** {obj.lifecycle.value}")
            body.append(f"- **Universe:** {obj.universe}")
            body.append(f"- **Decision record(s):** {_cell(obj.decision_links)}")
            body.append(f"- **Constitutional origin:** {_cell(self._origin(obj.cko_id))}")
            body.append(f"- **Consumed by:** {_cell(view.consumers or view.dependents)}")
            body.append("")
            body.append(obj.statement)
        return self._page(CAPABILITY_PORTAL, self._capability_note(), body)

    @staticmethod
    def _capability_note() -> str:
        return "Projected from canonical DECISION objects (UKDA Part 02) + origin (UKI D7)."

    def universe(self) -> str:
        body = [
            "Every canonical object grouped by the universe it belongs to. Universes are "
            "read directly from each object's canonical ``universe`` field.",
        ]
        objects = self._base.objects()
        universes = sorted({obj.universe for obj in objects})
        if not universes:
            body.append("")
            body.append("_No universes recorded yet._")
            return self._page(UNIVERSE_PORTAL, self._universe_note(), body)
        for universe in universes:
            members = self._base.by_universe(universe)
            body.append("")
            body.append(f"## Universe: {universe} ({len(members)})")
            body.append("")
            body.append("| CKO ID | Kind | Authority | Lifecycle | Title |")
            body.append("| --- | --- | --- | --- | --- |")
            for obj in members:
                body.append(
                    f"| {obj.cko_id} | {obj.kind.value} | {obj.authority.value} "
                    f"| {obj.lifecycle.value} | {obj.title} |"
                )
        return self._page(UNIVERSE_PORTAL, self._universe_note(), body)

    @staticmethod
    def _universe_note() -> str:
        return "Projected from the canonical ``universe`` field of every object (UKDA Part 02)."

    def epic(self) -> str:
        body = [
            "Each EPIC is a program-level **decision record**. Member knowledge is every "
            "canonical object that references the decision through its ``decision_links``.",
        ]
        decisions = self._base.decisions()
        if not decisions:
            body.append("")
            body.append("_No decision records recorded yet._")
            return self._page(EPIC_PORTAL, self._epic_note(), body)
        for dec in decisions:
            members = sorted(
                obj.cko_id for obj in self._base.objects() if dec.decision_id in obj.decision_links
            )
            body.append("")
            body.append(f"## {dec.decision_id} — {dec.title}")
            body.append("")
            body.append(f"- **Objective:** {dec.objective}")
            body.append(f"- **Chosen architecture:** {dec.chosen_architecture}")
            body.append(f"- **Grounded in:** {_cell(dec.dependencies)}")
            body.append(f"- **Member knowledge:** {_cell(members)}")
        unattributed = sorted(obj.cko_id for obj in self._base.objects() if not obj.decision_links)
        body.append("")
        body.append("## Unattributed knowledge")
        body.append("")
        body.append(
            "Canonical objects not yet linked to any decision record "
            f"(informational): {_cell(unattributed)}"
        )
        return self._page(EPIC_PORTAL, self._epic_note(), body)

    @staticmethod
    def _epic_note() -> str:
        return "Projected from decision records and object ``decision_links`` (UKDA Part 03)."

    def implementation(self) -> str:
        body = [
            "Every canonical object that is live in the system — lifecycle "
            "``implemented`` or ``operational`` — with what it depends on, its recorded "
            "evidence, and its constitutional origin.",
        ]
        live = [
            obj
            for obj in self._base.objects()
            if obj.lifecycle in (Lifecycle.IMPLEMENTED, Lifecycle.OPERATIONAL)
        ]
        if not live:
            body.append("")
            body.append("_No implemented or operational knowledge recorded yet._")
            return self._page(IMPLEMENTATION_PORTAL, self._implementation_note(), body)
        body.append("")
        body.append("| CKO ID | Kind | Lifecycle | Depends on | Evidence | Constitutional origin |")
        body.append("| --- | --- | --- | --- | --- | --- |")
        for obj in live:
            body.append(
                f"| {obj.cko_id} | {obj.kind.value} | {obj.lifecycle.value} "
                f"| {_cell(obj.dependencies)} | {_cell(obj.evidence)} "
                f"| {_cell(self._origin(obj.cko_id))} |"
            )
        return self._page(IMPLEMENTATION_PORTAL, self._implementation_note(), body)

    @staticmethod
    def _implementation_note() -> str:
        return "Projected from object lifecycle + evidence links (UKDA Part 02/12)."

    def repository(self) -> str:
        base = self._base
        coverage = self._intel.coverage()
        body = [
            "A repository-wide map of the canonical corpus: who owns what, which "
            "universes exist, and the distribution of kinds, authorities, and lifecycles.",
            "",
            "## Ownership",
            "",
            "| Owner | Objects | CKO IDs |",
            "| --- | --- | --- |",
        ]
        by_owner: dict[str, list[str]] = {}
        for obj in base.objects():
            by_owner.setdefault(obj.owner, []).append(obj.cko_id)
        for owner in sorted(by_owner):
            ids = sorted(by_owner[owner])
            body.append(f"| {owner} | {len(ids)} | {_cell(ids)} |")
        if not by_owner:
            body.append("| _none_ | 0 | — |")

        body.append("")
        body.append("## Distribution")
        body.append("")
        for heading, mapping in (
            ("By kind", coverage.by_kind),
            ("By authority", coverage.by_authority),
            ("By lifecycle", coverage.by_lifecycle),
        ):
            body.append(f"### {heading}")
            body.append("")
            body.append("| Bucket | Count |")
            body.append("| --- | --- |")
            for key, count in mapping.items():
                body.append(f"| {key} | {count} |")
            if not mapping:
                body.append("| _none_ | 0 |")
            body.append("")

        body.append("## Ownership integrity")
        body.append("")
        overlaps = OwnershipProtocol().find_overlaps(base)
        if overlaps:
            body.append("| Owners | Objects |")
            body.append("| --- | --- |")
            for overlap in overlaps:
                body.append(f"| {_cell(overlap.owners)} | {_cell(overlap.cko_ids)} |")
        else:
            body.append(
                "No overlapping ownership: no identical knowledge is claimed by more "
                "than one owner (UKI-LAW-005 holds)."
            )
        return self._page(
            REPOSITORY_PORTAL,
            "Projected from the whole canonical corpus + ownership protocol (UKI D3).",
            body,
        )

    # -- gate portals (validation / certification / coverage) ------------------

    def validation(self) -> str:
        report = validate_base(self._base)
        counts = report.counts()
        body = [
            f"- **Verdict:** {report.verdict.value} "
            f"({'accepted' if report.accepted else 'rejected'})",
            f"- **Checks:** {counts['total']} · passed {counts['passed']} · "
            f"failed {counts['failed']} · blocking failures {counts['blocking_failed']}",
            "",
            "| Check | Severity | Status | Message | Offenders |",
            "| --- | --- | --- | --- | --- |",
        ]
        for finding in report.findings:
            body.append(
                f"| {finding.check_id} | {finding.severity.value} | {finding.status.value} "
                f"| {finding.message} | {_cell(finding.offenders)} |"
            )
        return self._page(
            VALIDATION_PORTAL,
            "The fail-closed knowledge validation suite, run live (UKDA Part 10).",
            body,
        )

    def certification(self) -> str:
        report = certify_base(self._base)
        body = [
            f"- **Status:** {report.status.value} "
            f"({'certified' if report.certified else 'not certified'})",
            f"- **Objects certified:** {len(report.records)}",
            f"- **Not certified:** {_cell(report.not_certified_ids)}",
            f"- **Authority:** {KNOWLEDGE_CERTIFICATION_AUTHORITY} "
            "(certification confers no constitutional authority).",
            "",
            "| CKO ID | Status | Failed criteria |",
            "| --- | --- | --- |",
        ]
        for record in report.records:
            failed = tuple(c.criterion_id for c in record.criteria if not c.passed)
            body.append(f"| {record.cko_id} | {record.status.value} | {_cell(failed)} |")
        if not report.records:
            body.append("| _none_ | — | — |")
        return self._page(
            CERTIFICATION_PORTAL,
            "The completeness certification of every object, run live (UKDA Part 11).",
            body,
        )

    def coverage(self) -> str:
        report = self._intel.coverage()
        body = [
            f"- **Total objects:** {report.total_objects}",
            f"- **Total decisions:** {report.total_decisions}",
            "",
            "## Distribution",
            "",
            "| Dimension | Buckets |",
            "| --- | --- |",
            f"| Kind | {_cell(f'{k}: {v}' for k, v in report.by_kind.items())} |",
            f"| Authority | {_cell(f'{k}: {v}' for k, v in report.by_authority.items())} |",
            f"| Lifecycle | {_cell(f'{k}: {v}' for k, v in report.by_lifecycle.items())} |",
            "",
            "## Gaps",
            "",
            f"- **Objects missing rationale:** {_cell(report.objects_missing_rationale)}",
            f"- **Objects missing owner:** {_cell(report.objects_missing_owner)}",
            f"- **Orphans:** {_cell(report.orphans)}",
            f"- **Undocumented decisions:** {_cell(report.undocumented_decisions)}",
        ]
        return self._page(
            COVERAGE_PORTAL,
            "Projected from the coverage/consistency snapshot (UKDA Part 09).",
            body,
        )

    # -- search portal ---------------------------------------------------------

    def search(self) -> str:
        objects = self._base.objects()
        body = [
            "A deterministic, offline search index over every canonical object. The "
            "per-object terms and the inverted term index below use the exact "
            "tokenisation the institutional-memory search matches, so this page can be "
            "searched (ctrl-F) or consumed as an index without any runtime engine.",
        ]
        inverted: dict[str, list[str]] = {}
        body.append("")
        body.append("## Object terms")
        body.append("")
        if objects:
            body.append("| CKO ID | Title | Terms |")
            body.append("| --- | --- | --- |")
            for obj in objects:
                terms = self._intel.document_terms(obj)
                for term in terms:
                    inverted.setdefault(term, []).append(obj.cko_id)
                body.append(f"| {obj.cko_id} | {obj.title} | {_cell(terms)} |")
        else:
            body.append("_No canonical objects to index yet._")

        body.append("")
        body.append("## Inverted index")
        body.append("")
        if inverted:
            body.append("| Term | Objects |")
            body.append("| --- | --- |")
            for term in sorted(inverted):
                body.append(f"| {term} | {_cell(sorted(set(inverted[term])))} |")
        else:
            body.append("_Index is empty._")
        return self._page(
            SEARCH_PORTAL,
            "A deterministic inverted index over the exact search tokens (UKDA Part 09).",
            body,
        )

    # -- aggregate + materialise -----------------------------------------------

    def render_all(self) -> dict[str, str]:
        """Return every portal page keyed by filename (deterministic)."""
        return {
            PORTAL_INDEX: self.index(),
            ARCHITECTURE_PORTAL: self.architecture(),
            CAPABILITY_PORTAL: self.capability(),
            UNIVERSE_PORTAL: self.universe(),
            EPIC_PORTAL: self.epic(),
            IMPLEMENTATION_PORTAL: self.implementation(),
            VALIDATION_PORTAL: self.validation(),
            CERTIFICATION_PORTAL: self.certification(),
            TRACEABILITY_PORTAL: self.traceability(),
            REPOSITORY_PORTAL: self.repository(),
            DEPENDENCY_PORTAL: self.dependency(),
            EXECUTION_PORTAL: self.execution(),
            COVERAGE_PORTAL: self.coverage(),
            GOVERNANCE_PORTAL: self.governance(),
            SEARCH_PORTAL: self.search(),
            VISUALIZATION_PORTAL: self.visualization(),
        }

    def write_all(self, out_dir: str | Path) -> tuple[Path, ...]:
        """Write every portal page to ``out_dir`` and return the written paths."""
        target = Path(out_dir)
        target.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for filename, content in sorted(self.render_all().items()):
            path = target / filename
            path.write_text(content, encoding="utf-8")
            written.append(path)
        return tuple(written)


__all__ = [
    "PORTAL_INDEX",
    "ARCHITECTURE_PORTAL",
    "CAPABILITY_PORTAL",
    "UNIVERSE_PORTAL",
    "EPIC_PORTAL",
    "IMPLEMENTATION_PORTAL",
    "VALIDATION_PORTAL",
    "CERTIFICATION_PORTAL",
    "TRACEABILITY_PORTAL",
    "REPOSITORY_PORTAL",
    "DEPENDENCY_PORTAL",
    "EXECUTION_PORTAL",
    "COVERAGE_PORTAL",
    "GOVERNANCE_PORTAL",
    "SEARCH_PORTAL",
    "VISUALIZATION_PORTAL",
    "PORTALS",
    "KnowledgePortal",
]
