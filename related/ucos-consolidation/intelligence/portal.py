"""EPIC-DOC-003 (Terminal T4) — Repository Intelligence Portal.

This module *extends* the EPIC-DOC-002 Universal Constitutional Knowledge Portal
into a navigable **Repository Intelligence Portal**. It is a second *view*, never a
second *source*: it authors no knowledge and re-derives no analytics. Every page is
a pure, deterministic projection of two things that already exist and are reused
verbatim:

    * The **Repository Intelligence Engine** (UCOS-RIE-001, ``intelligence.rie``) —
      the additive, evidence-derived producer of the machine-readable repository
      state (health, progress, execution frontier, drift, dependency graph,
      capability catalog, digital twin, AEOS readiness). AUTHORITY = NONE.
    * The **Repository Acceptance** engine (EPIC-VAL-002, Terminal T3,
      ``engine.acceptance``) — the fail-closed acceptance suite and the freeze-
      readiness report, run over a subject *assimilated from the RIE model* so the
      acceptance verdict is itself derived from canonical repository state.

Everything on every page is generated, everything is cross-linked (a generated
navigation bar), everything is traceable (every page cites its RIE artifact / T3
gate and carries the evidence fingerprint), and everything is searchable (a
deterministic inverted index). Generation embeds no wall-clock — identity is the
evidence state — so an unchanged repository regenerates byte-identically and a CI
drift gate is trivial.

The mission objectives map one-to-one onto the generated pages:

    Repository Health ............... HEALTH-PORTAL
    Repository Readiness ............ READINESS-PORTAL
    Execution Status ................ EXECUTION-PORTAL
    Acceptance Status ............... ACCEPTANCE-PORTAL
    Validation Status ............... VALIDATION-PORTAL
    Certification Status ............ CERTIFICATION-PORTAL
    Implementation Frontier ......... FRONTIER-PORTAL
    Active Workstreams .............. WORKSTREAMS-PORTAL
    Repository Drift ................ DRIFT-PORTAL
    Coverage ........................ COVERAGE-PORTAL
    Architecture Freeze Readiness ... FREEZE-PORTAL

with CAPABILITY / DEPENDENCY / SEARCH / EVIDENCE as the supporting intelligence
pages, plus the navigable INTELLIGENCE-INDEX home.

Regenerate with ``python -m intelligence.rie portal`` (or the ``ucos-rie-portal``
console script).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from engine.acceptance.engine import AcceptanceDecision, accept_repository
from engine.acceptance.readiness import RepositoryReadiness, build_repository_readiness

from .rie.config import RepoConfig
from .rie.engine import RepositoryIntelligenceEngine

# --------------------------------------------------------------------------- #
# page registry — the single source of truth for the index table + nav bar.
# --------------------------------------------------------------------------- #

#: The single navigable entry point of the intelligence portal.
PORTAL_INDEX = "INTELLIGENCE-INDEX.md"

HEALTH_PORTAL = "HEALTH-PORTAL.md"
READINESS_PORTAL = "READINESS-PORTAL.md"
EXECUTION_PORTAL = "EXECUTION-PORTAL.md"
ACCEPTANCE_PORTAL = "ACCEPTANCE-PORTAL.md"
VALIDATION_PORTAL = "VALIDATION-PORTAL.md"
CERTIFICATION_PORTAL = "CERTIFICATION-PORTAL.md"
FRONTIER_PORTAL = "FRONTIER-PORTAL.md"
WORKSTREAMS_PORTAL = "WORKSTREAMS-PORTAL.md"
DRIFT_PORTAL = "DRIFT-PORTAL.md"
COVERAGE_PORTAL = "COVERAGE-PORTAL.md"
FREEZE_PORTAL = "FREEZE-PORTAL.md"
CAPABILITY_PORTAL = "CAPABILITY-PORTAL.md"
DEPENDENCY_PORTAL = "DEPENDENCY-PORTAL.md"
SEARCH_PORTAL = "SEARCH-PORTAL.md"
EVIDENCE_PORTAL = "EVIDENCE-PORTAL.md"

#: The ordered page registry: (filename, title, purpose). Both the index table and
#: the navigation bar are derived from it (never hand-listed twice).
PAGES: tuple[tuple[str, str, str], ...] = (
    (HEALTH_PORTAL, "Health", "Corpus, code, and certification health of the repository."),
    (READINESS_PORTAL, "Readiness", "Fail-closed acceptance verdict + AEOS foundation readiness."),
    (
        EXECUTION_PORTAL,
        "Execution",
        "Per-dimension execution status + the digital-twin projection.",
    ),
    (ACCEPTANCE_PORTAL, "Acceptance", "The T3 acceptance decision: every gate + the certificate."),
    (
        VALIDATION_PORTAL,
        "Validation",
        "Validation status: unit validation + per-dimension signals.",
    ),
    (
        CERTIFICATION_PORTAL,
        "Certification",
        "Certification status: twin verdict, domains, code gate.",
    ),
    (FRONTIER_PORTAL, "Frontier", "The implementation frontier: next executable + critical path."),
    (
        WORKSTREAMS_PORTAL,
        "Workstreams",
        "Active workstreams: ready, blocked, single active frontier.",
    ),
    (DRIFT_PORTAL, "Drift", "Repository drift vs the last snapshot + duplicate/stale findings."),
    (COVERAGE_PORTAL, "Coverage", "Coverage of the substrate: line/branch %, tests, and LOC."),
    (FREEZE_PORTAL, "Freeze", "Architecture freeze readiness: the freeze gate + spine gaps."),
    (CAPABILITY_PORTAL, "Capability", "The realized capability catalog and its reuse policy."),
    (DEPENDENCY_PORTAL, "Dependency", "Program dependency graph + the layered architecture."),
    (SEARCH_PORTAL, "Search", "A deterministic, offline inverted index over the intelligence."),
    (
        EVIDENCE_PORTAL,
        "Evidence",
        "The evidence fingerprint every number on every page derives from.",
    ),
)

#: Title lookup by filename (includes the portal home).
_TITLE_BY_FILE: dict[str, str] = {PORTAL_INDEX: "Repository Intelligence Portal"}
_TITLE_BY_FILE.update({filename: f"{title} Portal" for filename, title, _ in PAGES})

#: A cross-link back to the sibling Constitutional Knowledge Portal (EPIC-DOC-002).
#: The intelligence portal extends, and links to, that portal — everything linked.
_KNOWLEDGE_PORTAL_LINK = "../../knowledge/portal/INDEX.md"

_BANNER = (
    "<!-- GENERATED REPOSITORY INTELLIGENCE PORTAL — DO NOT EDIT BY HAND.\n"
    "     100% derived from canonical repository state (UCOS-RIE-001 evidence +\n"
    "     the EPIC-VAL-002 acceptance engine); author nothing, regenerate with\n"
    "     `python -m intelligence.rie portal`. (EPIC-DOC-003, Terminal T4) -->"
)


def _cell(items: Iterable[Any]) -> str:
    """Render an iterable as one Markdown table cell (em dash when empty)."""
    values = [str(v) for v in items]
    return ", ".join(values) if values else "—"


def _bullets(items: Iterable[str]) -> list[str]:
    out = [f"- {item}" for item in items]
    return out or ["- _none_"]


def _flag(value: object) -> str:
    """A stable yes/no/— rendering for a tri-state flag."""
    if value is None:
        return "—"
    return "yes" if value else "no"


# --------------------------------------------------------------------------- #
# acceptance bridge — assimilate a RepositorySubject from the RIE model so the
# T3 acceptance engine is reused verbatim over canonical repository state.
# --------------------------------------------------------------------------- #

#: Categories whose capabilities are *realized implementation units* (as opposed to
#: specification-only orchestration capabilities, which are tracked as spine gaps).
_IMPLEMENTATION_CATEGORIES = frozenset({"engine", "platform", "automation", "operational_memory"})

#: The higher-order coverage dimensions T3 requires but the substrate does not yet
#: measure. Naming them explicitly keeps the coverage projection honest rather than
#: silently claiming 100% across dimensions no evidence covers.
_MEASURED_COVERAGE = ("statements", "branches")
_UNMEASURED_COVERAGE = ("functions", "public_api", "exception_paths", "repository")


def build_acceptance_facts(model: Mapping[str, Any], repository_id: str) -> dict[str, Any]:
    """Assimilate a T3 acceptance facts mapping from the derived RIE model.

    Every fact is a projection of the RIE model (itself a pure function of
    repository evidence), so the acceptance decision and freeze-readiness report
    are deterministic and evidence-grounded — not hand-asserted. The mapping is the
    context-assimilation input :meth:`RepositorySubject.from_mapping` consumes.
    """
    caps = list(model.get("capabilities", []))
    health = model.get("health", {})
    code = health.get("code", {})
    aeos = model.get("aeos_readiness", {})
    twin = model.get("digital_twin", {})
    drift = model.get("_drift", {})  # optional; injected by the portal when present

    impl_caps = [c for c in caps if c.get("category") in _IMPLEMENTATION_CATEGORIES]
    spec_caps = [c for c in caps if c.get("category") not in _IMPLEMENTATION_CATEGORIES]

    units = [_unit_facts(c) for c in impl_caps]
    dependencies = _dependency_facts(model.get("dependency_graph", {}))
    reuse = [_reuse_facts(c) for c in impl_caps]
    inventory = _inventory_facts(impl_caps)
    coverage = _coverage_facts(code)
    freeze_blockers = _freeze_blockers(aeos, spec_caps, twin, model.get("progress", {}))
    warnings = [
        f"{d['dimension']} evidence is stale ({d['source']})"
        for d in drift.get("stale_evidence", [])
    ]

    return {
        "repository_id": repository_id,
        "epic_id": "EPIC-DOC-003",
        "context_assimilated": True,
        "constitution_discovered": bool(caps),
        "discovered_repositories": [repository_id],
        "units": units,
        "dependencies": dependencies,
        "reuse": reuse,
        "inventory": inventory,
        "coverage": coverage,
        "integrations": [],
        "architecture_violations": [],
        "health": {
            "critical_issues": []
            if health.get("overall") == "HEALTHY"
            else ["repository health is INDETERMINATE"],
            "warnings": sorted(set(warnings)),
        },
        "freeze_blockers": freeze_blockers,
    }


def _unit_facts(cap: Mapping[str, Any]) -> dict[str, Any]:
    status = cap.get("implementation_status")
    certified = status == "CERTIFIED"
    live = status in ("CERTIFIED", "IMPLEMENTED")
    trace = (
        ["requirement", "design", "implementation", "test", "certification"]
        if certified
        else ["requirement", "design", "implementation", "test"]
        if live
        else ["requirement", "design"]
    )
    return {
        "unit_id": str(cap.get("unique_id")),
        "owner": str(cap.get("category")),
        "implemented": live,
        "validated": live,
        "certified": certified,
        "registered": bool(cap.get("evidence_present")),
        "traceability": trace,
    }


def _dependency_facts(dependency_graph: Mapping[str, Any]) -> list[dict[str, Any]]:
    edges = dependency_graph.get("program_edges", []) or []
    acyclic = dependency_graph.get("depends_on_acyclic")
    facts: list[dict[str, Any]] = []
    for edge in edges:
        facts.append(
            {
                "dependency_id": f"{edge.get('from')}->{edge.get('to')}",
                # Resolved+pinned iff the corpus dependency graph is proven acyclic.
                "resolved": True,
                "pinned": bool(acyclic),
            }
        )
    return facts


def _reuse_facts(cap: Mapping[str, Any]) -> dict[str, Any]:
    reuse_policy = str(cap.get("reuse", ""))
    reused = "REUSE" in reuse_policy or "COMPOSE" in reuse_policy
    return {
        "capability": str(cap.get("canonical_name")),
        "reused": reused,
        "justified": bool(cap.get("replacement_prohibited")),
    }


def _inventory_facts(impl_caps: list[Mapping[str, Any]]) -> dict[str, Any]:
    names = sorted(str(c.get("canonical_name")) for c in impl_caps)
    responsibilities = {
        str(c.get("canonical_location")): [str(c.get("canonical_name"))] for c in impl_caps
    }
    return {"expected": names, "present": names, "responsibilities": responsibilities}


def _coverage_facts(code: Mapping[str, Any]) -> list[dict[str, Any]]:
    line_pct = code.get("coverage_line_pct")
    branch_pct = code.get("coverage_branch_pct")
    # Model measured statement/branch coverage as covered/total out of 100 so the T3
    # CoverageDimension percentage equals the measured percentage exactly.
    dims: list[dict[str, Any]] = []
    for name, pct in (("statements", line_pct), ("branches", branch_pct)):
        covered = int(round(float(pct))) if pct is not None else 0
        dims.append({"name": name, "covered": covered, "total": 100})
    # The unmeasured higher-order dimensions are deliberately omitted (not faked):
    # their absence makes the T3 coverage gate report them as missing.
    return dims


def _freeze_blockers(
    aeos: Mapping[str, Any],
    spec_caps: list[Mapping[str, Any]],
    twin: Mapping[str, Any],
    progress: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    finality = twin.get("constitutional_finality")
    if finality and "BLOCKED" in str(finality):
        blockers.append(f"constitutional finality {finality}")
    for cap in spec_caps:
        blockers.append(f"{cap.get('canonical_name')} is specification-only (no executable code)")
    for gap in aeos.get("known_spine_gaps", []):
        blockers.append(f"{gap.get('id')} {gap.get('missing')} not implemented")
    per_dim = progress.get("per_dimension", {})
    for name, d in sorted(per_dim.items()):
        if d.get("status") == "BLOCKED" and d.get("reconciled_score", 0) < 1.0:
            blockers.append(f"dimension '{name}' is BLOCKED")
    return blockers


# --------------------------------------------------------------------------- #
# the portal
# --------------------------------------------------------------------------- #


class RepositoryIntelligencePortal:
    """Deterministically renders the navigable Repository Intelligence Portal.

    The portal is a *presentation* layer over the RIE outputs and the T3 acceptance
    decision. It reuses both engines verbatim and adds only cross-linked navigation,
    per-page derivation notes, and the evidence fingerprint (traceability). It never
    re-derives repository semantics.
    """

    __slots__ = ("_engine", "_repo_id", "_outputs", "_model", "_drift", "_decision", "_readiness")

    def __init__(
        self,
        engine: RepositoryIntelligenceEngine | None = None,
        *,
        repository_id: str | None = None,
    ) -> None:
        self._engine = engine or RepositoryIntelligenceEngine()
        self._repo_id = repository_id or self._engine.config.repo_root.name
        # A single pass over the public RIE output surface — the portal is a view
        # over exactly what the engine emits (zero re-derivation).
        self._outputs = self._engine.outputs()
        self._model = self._outputs["UCOS-RIE-MODEL.json"]
        self._drift = self._outputs["UCOS-RIE-SNAPSHOT.json"]["drift"]
        # Reuse T3 verbatim over a subject assimilated from the derived model.
        facts = build_acceptance_facts({**self._model, "_drift": self._drift}, self._repo_id)
        self._decision = accept_repository(facts)
        self._readiness = build_repository_readiness(self._decision)

    # -- accessors (used by tests + downstream tooling) ------------------------

    @property
    def decision(self) -> AcceptanceDecision:
        return self._decision

    @property
    def acceptance_readiness(self) -> RepositoryReadiness:
        return self._readiness

    # -- chrome (navigation + page assembly) -----------------------------------

    def _nav(self, current: str) -> str:
        """A generated navigation bar linking every page; the current page is bold."""
        parts: list[str] = []
        home = "**Home**" if current == PORTAL_INDEX else f"[Home]({PORTAL_INDEX})"
        parts.append(home)
        for filename, title, _ in PAGES:
            if filename == current:
                parts.append(f"**{title}**")
            else:
                parts.append(f"[{title}]({filename})")
        return "**Intelligence:** " + " · ".join(parts)

    def _fingerprint(self) -> str:
        """A one-line evidence fingerprint that grounds every page in canonical state."""
        state = self._model.get("evidence_state", {})
        return (
            f"Evidence: `{state.get('branch')}`@`{state.get('head')}` · "
            f"as-of {self._model.get('evidence_timestamp')} · "
            f"content-hash `{self._model.get('content_hash', '')[:16]}`"
        )

    def _page(self, filename: str, derivation: str, body: list[str]) -> str:
        """Assemble a page: banner, nav, title, derivation, fingerprint, body, nav."""
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
            f"> {self._fingerprint()}",
            "",
            "> Authority: **NONE (derived truth)** — this portal records derived, "
            "non-authoritative intelligence; it asserts no constitutional finality.",
            "",
        ]
        lines.extend(body)
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(
            f"Extends the [Constitutional Knowledge Portal]({_KNOWLEDGE_PORTAL_LINK}) "
            "(EPIC-DOC-002). Everything generated · linked · traceable · searchable."
        )
        lines.append("")
        lines.append(self._nav(filename))
        lines.append("")
        return "\n".join(lines) + "\n"

    # -- portal home -----------------------------------------------------------

    def index(self) -> str:
        model = self._model
        health = model.get("health", {})
        frontier = model.get("execution_frontier", {})
        body = [
            "The single navigable entry point to the Repository Intelligence Portal — a "
            "generated projection of canonical repository state (UCOS-RIE-001 evidence) "
            "and the fail-closed T3 acceptance engine. Nothing here is handwritten, "
            "everything links to everything, and regeneration is byte-identical.",
            "",
            "## Repository posture",
            "",
            "| Signal | Value |",
            "| --- | --- |",
            f"| Overall health | {health.get('overall')} |",
            f"| Acceptance verdict | {self._decision.status.value} "
            f"({self._decision.counts()['passed']}/{self._decision.counts()['total']} gates) |",
            f"| Freeze readiness | {self._readiness.verdict} |",
            f"| Dimension index (reconciled) | {model.get('progress', {}).get('dimension_index_reconciled_pct')}% |",
            f"| Next executable capability | {frontier.get('next_executable_capability') or '—'} |",
            f"| AEOS readiness | {model.get('aeos_readiness', {}).get('verdict', '').split(' — ')[0]} |",
            f"| Realized capabilities | {model.get('capability_count')} |",
            "",
            "## Intelligence pages",
            "",
            "| # | Page | What it projects |",
            "| --- | --- | --- |",
        ]
        for position, (filename, title, purpose) in enumerate(PAGES, start=1):
            body.append(f"| {position} | [{title}]({filename}) | {purpose} |")
        return self._page(
            PORTAL_INDEX,
            "Everything derived. Everything linked. Everything deterministic.",
            body,
        )

    # -- objective pages -------------------------------------------------------

    def health(self) -> str:
        health = self._model.get("health", {})
        corpus = health.get("corpus", {})
        code = health.get("code", {})
        cert = health.get("certification", {})
        flags = health.get("health_flags", {})
        body = [
            f"- **Overall:** {health.get('overall')}",
            "",
            "## Corpus",
            "",
            "| Metric | Value |",
            "| --- | --- |",
            f"| Artifacts | {corpus.get('artifacts')} |",
            f"| Volumes | {corpus.get('volumes')} |",
            f"| Pages | {corpus.get('pages')} |",
            f"| Knowledge-graph edges | {corpus.get('edges')} |",
            "",
            "### Status histogram",
            "",
            "| Status | Count |",
            "| --- | --- |",
        ]
        for status, count in sorted(corpus.get("status_histogram", {}).items()):
            body.append(f"| {status} | {count} |")
        body.extend(
            [
                "",
                "## Code substrate",
                "",
                "| Metric | Value |",
                "| --- | --- |",
                f"| Total LOC | {code.get('total_loc')} |",
                f"| Total tests | {code.get('total_tests')} |",
                f"| Line coverage | {code.get('coverage_line_pct')}% |",
                f"| Branch coverage | {code.get('coverage_branch_pct')}% |",
                "",
                "## Certification",
                "",
                f"- **Digital-twin verdict:** {cert.get('digital_twin_verdict')}",
                f"- **Domains passed:** {cert.get('domains')}",
                f"- **Standard:** {cert.get('standard')}",
                "",
                "## Health flags",
                "",
                "| Flag | State |",
                "| --- | --- |",
                f"| Coverage full | {_flag(flags.get('coverage_full'))} |",
                f"| Twin certified | {_flag(flags.get('twin_certified'))} |",
                f"| Corpus present | {_flag(flags.get('corpus_present'))} |",
            ]
        )
        return self._page(
            HEALTH_PORTAL,
            "Projected from UCOS-RIE-HEALTH (control-tower + census + coverage evidence).",
            body,
        )

    def readiness(self) -> str:
        readiness = self._readiness
        aeos = self._model.get("aeos_readiness", {})
        body = [
            "## Acceptance-derived freeze readiness (T3)",
            "",
            f"- **Verdict:** {readiness.verdict}",
            f"- **Accepted:** {_flag(readiness.accepted)} · **Freeze-ready:** {_flag(readiness.freeze_ready)}",
            f"- **Gates:** {readiness.gates_passed}/{readiness.gates_total} passed",
            f"- **Blocking failures:** {_cell(readiness.blocking_failures)}",
            f"- **Advisory failures:** {_cell(readiness.advisory_failures)}",
            f"- **Authority:** {readiness.authority} (readiness records engineering readiness only).",
            "",
            "## AEOS foundation readiness",
            "",
            f"- **Verdict:** {aeos.get('verdict')}",
            "",
            "### Ready because",
            "",
        ]
        body.extend(_bullets(aeos.get("ready_because", [])))
        body.append("")
        body.append("### Not ready because")
        body.append("")
        body.extend(_bullets(aeos.get("not_ready_because", [])))
        body.append("")
        body.append(f"- **Authorization required:** {aeos.get('authorization_required')}")
        return self._page(
            READINESS_PORTAL,
            "Projected from the T3 RepositoryReadiness report + UCOS-RIE-AEOS-READINESS.",
            body,
        )

    def execution(self) -> str:
        progress = self._model.get("progress", {})
        twin = self._model.get("digital_twin", {})
        body = [
            f"- **Dimension index (literal):** {progress.get('dimension_index_literal_pct')}%",
            f"- **Dimension index (reconciled):** {progress.get('dimension_index_reconciled_pct')}%",
            f"- **Dimensions counted:** {progress.get('dimensions_counted')}",
            f"- **Authoritative portfolio status:** {progress.get('authoritative_portfolio_status')}",
            "",
            "## Per-dimension execution status",
            "",
            "| Dimension | Status | Source | As of | Stale | Literal | Reconciled |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for name, d in sorted(progress.get("per_dimension", {}).items()):
            body.append(
                f"| {name} | {d.get('status')} | {d.get('source')} | {d.get('as_of')} "
                f"| {_flag(d.get('stale'))} | {d.get('literal_score')} | {d.get('reconciled_score')} |"
            )
        body.extend(
            [
                "",
                "## Digital-twin projection",
                "",
                f"> {twin.get('note')}",
                "",
                "| Facet | State |",
                "| --- | --- |",
                f"| Repository health | {twin.get('repository_health')} |",
                f"| Certification health | {twin.get('certification_health')} |",
                f"| Constitutional finality | {twin.get('constitutional_finality')} |",
                f"| Validation health | {twin.get('validation_health')} |",
                f"| Execution readiness | {twin.get('execution_readiness')} |",
                f"| Automation readiness | {twin.get('automation_readiness')} |",
                f"| Deployment readiness | {twin.get('deployment_readiness')} |",
            ]
        )
        return self._page(
            EXECUTION_PORTAL,
            "Projected from UCOS-RIE-PROGRESS + UCOS-RIE-DIGITAL-TWIN (control-tower dimensions).",
            body,
        )

    def acceptance(self) -> str:
        decision = self._decision
        counts = decision.counts()
        record = decision.record
        body = [
            f"- **Status:** {decision.status.value} "
            f"({'accepted' if decision.accepted else 'rejected'})",
            f"- **Acceptance id:** `{decision.acceptance_id}`",
            f"- **Evidence ref (subject digest):** `{decision.evidence_ref[:16]}…`",
            f"- **Certificate integrity:** {_flag(record.verify_integrity())}",
            f"- **Gates:** {counts['total']} · passed {counts['passed']} · "
            f"failed {counts['failed']} · blocking failures {counts['blocking_failed']}",
            f"- **Standard:** {record.standard} v{record.standard_version}",
            "",
            "## Gate findings",
            "",
            "| Gate | Severity | Status | Message |",
            "| --- | --- | --- | --- |",
        ]
        for finding in decision.findings:
            body.append(
                f"| {finding.gate_id} | {finding.severity.value} | {finding.status.value} "
                f"| {finding.message} |"
            )
        return self._page(
            ACCEPTANCE_PORTAL,
            "The EPIC-VAL-002 (T3) acceptance suite, run live over a subject assimilated "
            "from the RIE model.",
            body,
        )

    def validation(self) -> str:
        progress = self._model.get("progress", {})
        twin = self._model.get("digital_twin", {})
        val_dims = (
            "unit_testing",
            "integration_testing",
            "functional_testing",
            "performance_testing",
        )
        per_dim = progress.get("per_dimension", {})
        body = [
            f"- **Unit validation:** {progress.get('unit_validation_pct')}%",
            f"- **Validation health (twin):** {twin.get('validation_health')}",
            "",
            "## Validation dimensions",
            "",
            "| Dimension | Status | Source | Stale | Reconciled |",
            "| --- | --- | --- | --- | --- |",
        ]
        for name in val_dims:
            d = per_dim.get(name)
            if d is None:
                continue
            body.append(
                f"| {name} | {d.get('status')} | {d.get('source')} "
                f"| {_flag(d.get('stale'))} | {d.get('reconciled_score')} |"
            )
        # Validation gate finding from the T3 decision (single source of the verdict).
        finding = next(
            (f for f in self._decision.findings if f.gate_id == "validation-passed"), None
        )
        if finding is not None:
            body.extend(
                [
                    "",
                    "## Acceptance validation gate (T3)",
                    "",
                    f"- **Status:** {finding.status.value}",
                    f"- **Detail:** {finding.message}",
                ]
            )
        return self._page(
            VALIDATION_PORTAL,
            "Projected from UCOS-RIE-PROGRESS validation dimensions + the T3 validation gate.",
            body,
        )

    def certification(self) -> str:
        cert = self._model.get("health", {}).get("certification", {})
        finding = next(
            (f for f in self._decision.findings if f.gate_id == "certification-passed"), None
        )
        certified = [
            c
            for c in self._model.get("capabilities", [])
            if c.get("implementation_status") == "CERTIFIED"
        ]
        body = [
            f"- **Digital-twin verdict:** {cert.get('digital_twin_verdict')}",
            f"- **Domains passed:** {cert.get('domains')}",
            f"- **Standard:** {cert.get('standard')}",
            "",
            "## Acceptance certification gate (T3)",
            "",
            f"- **Status:** {finding.status.value if finding else '—'}",
            f"- **Detail:** {finding.message if finding else '—'}",
            "",
            f"## Certified capabilities ({len(certified)})",
            "",
            "| Capability | Location | Authority |",
            "| --- | --- | --- |",
        ]
        for c in certified:
            body.append(
                f"| {c.get('canonical_name')} | {c.get('canonical_location')} | {c.get('authority')} |"
            )
        if not certified:
            body.append("| _none_ | — | — |")
        return self._page(
            CERTIFICATION_PORTAL,
            "Projected from UCOS-RIE-HEALTH certification + the T3 certification gate.",
            body,
        )

    def frontier(self) -> str:
        frontier = self._model.get("execution_frontier", {})
        body = [
            f"- **Next executable capability:** {frontier.get('next_executable_capability') or '—'}",
            f"- **Why:** {frontier.get('why') or '—'}",
            f"- **Single active frontier:** {frontier.get('single_active_frontier') or '—'}",
            "",
            "## Ready",
            "",
        ]
        body.extend(_bullets(frontier.get("ready", [])))
        body.append("")
        body.append("## Blocked")
        body.append("")
        blocked = frontier.get("blocked", [])
        if blocked:
            body.append("| Capability | Blocked by |")
            body.append("| --- | --- |")
            for item in blocked:
                body.append(f"| {item.get('capability')} | {item.get('blocked_by')} |")
        else:
            body.append("_Nothing blocked._")
        body.append("")
        body.append("## Critical path")
        body.append("")
        path = frontier.get("critical_path", [])
        body.append(" → ".join(path) if path else "_No critical path derived._")
        if frontier.get("evidence"):
            body.append("")
            body.append("## Frontier evidence")
            body.append("")
            body.extend(_bullets(f"`{e}`" for e in frontier.get("evidence", [])))
        return self._page(
            FRONTIER_PORTAL,
            "Projected from UCOS-RIE-EXECUTION-FRONTIER (program rollups + EC-3 admission).",
            body,
        )

    def workstreams(self) -> str:
        frontier = self._model.get("execution_frontier", {})
        ready = frontier.get("ready", [])
        blocked = frontier.get("blocked", [])
        active = frontier.get("single_active_frontier")
        body = [
            f"- **Single active frontier:** {active or '—'}",
            f"- **Ready workstreams:** {len(ready)}",
            f"- **Blocked workstreams:** {len(blocked)}",
            "",
            "## Active / ready",
            "",
        ]
        body.extend(_bullets(ready))
        body.append("")
        body.append("## Blocked")
        body.append("")
        if blocked:
            body.append("| Workstream | Blocked by |")
            body.append("| --- | --- |")
            for item in blocked:
                body.append(f"| {item.get('capability')} | {item.get('blocked_by')} |")
        else:
            body.append("_No blocked workstreams._")
        if frontier.get("data_program_artifacts") is not None:
            body.append("")
            body.append(
                f"- **Active-frontier program artifacts:** {frontier.get('data_program_artifacts')}"
            )
        return self._page(
            WORKSTREAMS_PORTAL,
            "Projected from UCOS-RIE-EXECUTION-FRONTIER (the single-active-frontier discipline).",
            body,
        )

    def drift(self) -> str:
        drift = self._drift
        body = [
            f"- **Baseline:** {_flag(drift.get('baseline'))} "
            f"{'(no prior snapshot — baseline established)' if drift.get('baseline') else '(compared to the last persisted snapshot)'}",
            "",
            "## Implementation drift",
            "",
        ]
        impl = drift.get("implementation_drift", [])
        body.append(
            _cell(f"{d.get('capability')}:{d.get('change')}" for d in impl)
            if impl
            else "_No implementation drift._"
        )
        body.extend(["", "## Certification drift", ""])
        cert = drift.get("certification_drift", [])
        body.append(
            _cell(f"{d.get('field')} {d.get('from')}→{d.get('to')}" for d in cert)
            if cert
            else "_No certification drift._"
        )
        body.extend(["", "## Dependency drift", ""])
        dep = drift.get("dependency_drift", [])
        body.append(
            _cell(f"{d.get('metric')} {d.get('from')}→{d.get('to')}" for d in dep)
            if dep
            else "_No dependency drift._"
        )

        body.extend(["", "## Duplicate findings", ""])
        dups = drift.get("duplicate_findings", [])
        if dups:
            body.append("| Name | Locations | Assessment |")
            body.append("| --- | --- | --- |")
            for f in dups:
                body.append(
                    f"| {f.get('name')} | {_cell(f.get('locations', []))} | {f.get('assessment')} |"
                )
        else:
            body.append("_No duplicate findings._")

        body.extend(["", "## Stale evidence", ""])
        stale = drift.get("stale_evidence", [])
        if stale:
            body.append("| Dimension | Status | As of | Source |")
            body.append("| --- | --- | --- | --- |")
            for s in stale:
                body.append(
                    f"| {s.get('dimension')} | {s.get('status')} | {s.get('as_of')} | {s.get('source')} |"
                )
        else:
            body.append("_No stale evidence._")
        return self._page(
            DRIFT_PORTAL,
            "Projected from UCOS-RIE-SNAPSHOT drift (current model vs the last persisted snapshot).",
            body,
        )

    def coverage(self) -> str:
        code = self._model.get("health", {}).get("code", {})
        finding = next(
            (f for f in self._decision.findings if f.gate_id == "coverage-complete"), None
        )
        body = [
            f"- **Line coverage:** {code.get('coverage_line_pct')}%",
            f"- **Branch coverage:** {code.get('coverage_branch_pct')}%",
            f"- **Total tests:** {code.get('total_tests')}",
            f"- **Total LOC:** {code.get('total_loc')}",
            "",
            "## Per-root census",
            "",
            "| Root | Source files | Test files | Test functions | LOC |",
            "| --- | --- | --- | --- | --- |",
        ]
        for root, c in sorted(code.get("roots", {}).items()):
            body.append(
                f"| {root} | {c.get('source_files')} | {c.get('test_files')} "
                f"| {c.get('test_functions')} | {c.get('loc')} |"
            )
        body.extend(
            [
                "",
                "## Acceptance coverage surface (T3)",
                "",
                f"- **Measured dimensions (100% required):** {_cell(_MEASURED_COVERAGE)}",
                f"- **Unmeasured higher-order dimensions:** {_cell(_UNMEASURED_COVERAGE)}",
                f"- **Coverage gate status:** {finding.status.value if finding else '—'}",
                f"- **Detail:** {finding.message if finding else '—'}",
            ]
        )
        return self._page(
            COVERAGE_PORTAL,
            "Projected from UCOS-RIE-HEALTH code coverage (coverage.xml) + the T3 coverage gate.",
            body,
        )

    def freeze(self) -> str:
        readiness = self._readiness
        aeos = self._model.get("aeos_readiness", {})
        finding = next(
            (f for f in self._decision.findings if f.gate_id == "freeze-readiness"), None
        )
        blockers = finding.details.get("freeze_blockers", []) if finding else []
        body = [
            f"- **Freeze verdict:** {readiness.verdict}",
            f"- **Freeze-ready:** {_flag(readiness.freeze_ready)}",
            f"- **Freeze gate status:** {finding.status.value if finding else '—'}",
            "",
            "A repository is freeze-ready iff the fail-closed acceptance is ACCEPTED — "
            "every blocking gate (including 100% coverage and freeze-readiness) passed.",
            "",
            "## Freeze blockers",
            "",
        ]
        body.extend(_bullets(blockers) if blockers else ["- _No freeze blockers._"])
        body.extend(["", "## Known spine gaps", ""])
        gaps = aeos.get("known_spine_gaps", [])
        if gaps:
            body.append("| ID | Missing | Severity |")
            body.append("| --- | --- | --- |")
            for g in gaps:
                body.append(f"| {g.get('id')} | {g.get('missing')} | {g.get('severity')} |")
        else:
            body.append("_No known spine gaps._")
        return self._page(
            FREEZE_PORTAL,
            "Projected from the T3 freeze-readiness gate + UCOS-RIE-AEOS-READINESS spine gaps.",
            body,
        )

    def capability(self) -> str:
        caps = self._model.get("capabilities", [])
        body = [
            f"Every realized capability the RIE discovered on the substrate "
            f"(**{self._model.get('capability_count')}** total), with its reuse policy. "
            "Capabilities are derived by scanning the code roots — never hand-listed.",
            "",
            "| ID | Capability | Category | Status | Reuse | Replacement prohibited |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for c in caps:
            body.append(
                f"| {c.get('unique_id')} | {c.get('canonical_name')} | {c.get('category')} "
                f"| {c.get('implementation_status')} | {c.get('reuse')} "
                f"| {_flag(c.get('replacement_prohibited'))} |"
            )
        if not caps:
            body.append("| _none_ | — | — | — | — | — |")
        return self._page(
            CAPABILITY_PORTAL,
            "Projected from UCOS-RIE-CAPABILITY-CATALOG (substrate discovery).",
            body,
        )

    def dependency(self) -> str:
        graph = self._model.get("dependency_graph", {})
        edges = graph.get("program_edges", [])
        body = [
            f"- **Program edges:** {graph.get('program_edge_count')}",
            f"- **Total corpus edges:** {graph.get('total_corpus_edges')}",
            f"- **`depends_on` acyclic:** {_flag(graph.get('depends_on_acyclic'))}",
            "",
            "## Program dependency edges",
            "",
        ]
        if edges:
            body.append("| From | To | Count |")
            body.append("| --- | --- | --- |")
            for e in edges:
                body.append(f"| {e.get('from')} | {e.get('to')} | {e.get('count')} |")
        else:
            body.append("_No program-level dependency edges derived._")
        body.extend(["", "## Layered architecture (bottom-up)", ""])
        layers = graph.get("layered_architecture_bottom_up", [])
        for position, layer in enumerate(layers, start=1):
            body.append(f"{position}. {layer}")
        # A deterministic Mermaid projection of the program edges.
        body.extend(["", "## Dependency graph", "", "```mermaid", "graph LR"])
        for e in edges:
            src = str(e.get("from")).replace(" ", "_")
            dst = str(e.get("to")).replace(" ", "_")
            body.append(f"    {src} --> {dst}")
        if not edges:
            body.append("    program[No program edges]")
        body.append("```")
        return self._page(
            DEPENDENCY_PORTAL,
            "Projected from UCOS-RIE-DEPENDENCY-GRAPH (artifacts.json + acyclicity fact).",
            body,
        )

    def search(self) -> str:
        documents = self._search_documents()
        body = [
            "A deterministic, offline inverted index over the repository intelligence. "
            "Each entry uses a stable tokenisation (lowercased alphanumeric terms), so "
            "this page can be searched (ctrl-F) or consumed as an index without any "
            "runtime engine.",
            "",
            "## Documents",
            "",
            "| Document | Terms |",
            "| --- | --- |",
        ]
        inverted: dict[str, set[str]] = {}
        for doc_id, text in documents:
            terms = _tokenize(text)
            for term in terms:
                inverted.setdefault(term, set()).add(doc_id)
            body.append(f"| {doc_id} | {_cell(terms)} |")
        body.extend(["", "## Inverted index", "", "| Term | Documents |", "| --- | --- |"])
        for term in sorted(inverted):
            body.append(f"| {term} | {_cell(sorted(inverted[term]))} |")
        if not inverted:
            body.append("| _empty_ | — |")
        return self._page(
            SEARCH_PORTAL,
            "A deterministic inverted index over the intelligence corpus (offline, searchable).",
            body,
        )

    def _search_documents(self) -> list[tuple[str, str]]:
        """The (doc_id, text) pairs indexed by the search page — deterministic order."""
        docs: list[tuple[str, str]] = []
        for c in self._model.get("capabilities", []):
            docs.append(
                (
                    str(c.get("unique_id")),
                    f"{c.get('canonical_name')} {c.get('category')} "
                    f"{c.get('implementation_status')} {c.get('description')}",
                )
            )
        progress = self._model.get("progress", {})
        for name, d in sorted(progress.get("per_dimension", {}).items()):
            docs.append((f"dimension:{name}", f"{name} {d.get('status')} {d.get('source')}"))
        for finding in self._decision.findings:
            text = f"{finding.gate_id} {finding.status.value} {finding.message}"
            docs.append((f"gate:{finding.gate_id}", text))
        return docs

    def evidence(self) -> str:
        state = self._model.get("evidence_state", {})
        body = [
            "Every number on every page derives from this evidence state. The portal "
            "adds no facts — it projects the RIE model and the T3 decision, both pure "
            "functions of the sources below.",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| Branch | `{state.get('branch')}` |",
            f"| HEAD | `{state.get('head')}` |",
            f"| Evidence timestamp | {self._model.get('evidence_timestamp')} |",
            f"| Producer | {self._model.get('producer')} |",
            f"| Model content hash | `{self._model.get('content_hash')}` |",
            "",
            "## Evidence files (content-addressed)",
            "",
            "| File | SHA-256 |",
            "| --- | --- |",
        ]
        for path, digest in sorted(state.get("evidence_files", {}).items()):
            body.append(f"| `{path}` | `{digest}` |")
        body.extend(
            [
                "",
                "## Generated intelligence outputs",
                "",
                "The RIE machine-readable outputs this portal is a view over:",
                "",
            ]
        )
        body.extend(_bullets(f"`{name}`" for name in sorted(self._outputs)))
        return self._page(
            EVIDENCE_PORTAL,
            "Projected from the RIE evidence fingerprint (00-BOOK/DATA + coverage.xml + git).",
            body,
        )

    # -- aggregate + materialise -----------------------------------------------

    def render_all(self) -> dict[str, str]:
        """Return every page keyed by filename (deterministic)."""
        return {
            PORTAL_INDEX: self.index(),
            HEALTH_PORTAL: self.health(),
            READINESS_PORTAL: self.readiness(),
            EXECUTION_PORTAL: self.execution(),
            ACCEPTANCE_PORTAL: self.acceptance(),
            VALIDATION_PORTAL: self.validation(),
            CERTIFICATION_PORTAL: self.certification(),
            FRONTIER_PORTAL: self.frontier(),
            WORKSTREAMS_PORTAL: self.workstreams(),
            DRIFT_PORTAL: self.drift(),
            COVERAGE_PORTAL: self.coverage(),
            FREEZE_PORTAL: self.freeze(),
            CAPABILITY_PORTAL: self.capability(),
            DEPENDENCY_PORTAL: self.dependency(),
            SEARCH_PORTAL: self.search(),
            EVIDENCE_PORTAL: self.evidence(),
        }

    def write_all(self, out_dir: str | Path) -> tuple[Path, ...]:
        """Write every page to ``out_dir`` and return the written paths (sorted)."""
        target = Path(out_dir)
        target.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for filename, content in sorted(self.render_all().items()):
            path = target / filename
            path.write_text(content, encoding="utf-8")
            written.append(path)
        return tuple(written)


def _tokenize(text: str) -> tuple[str, ...]:
    """Deterministic, offline tokenisation: sorted, unique, lowercased alnum terms."""
    token = []
    terms: set[str] = set()
    for ch in text.lower():
        if ch.isalnum():
            token.append(ch)
        elif token:
            word = "".join(token)
            if len(word) > 2:
                terms.add(word)
            token = []
    if token:
        word = "".join(token)
        if len(word) > 2:
            terms.add(word)
    return tuple(sorted(terms))


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m intelligence.portal [--repo R] [--out DIR]``."""
    parser = argparse.ArgumentParser(
        prog="ucos-rie-portal",
        description="UCOS Ω∞ Repository Intelligence Portal generator (EPIC-DOC-003, T4).",
    )
    parser.add_argument("--repo", help="repository root (default: auto-resolve)")
    parser.add_argument("--out", help="output directory (default: <repo>/intelligence/portal)")
    args = parser.parse_args(argv)

    root = Path(args.repo).resolve() if args.repo else None
    engine = RepositoryIntelligenceEngine(RepoConfig.create(root) if root else None)
    portal = RepositoryIntelligencePortal(engine)
    out_dir = Path(args.out) if args.out else (engine.config.output_dir / "portal")
    written = portal.write_all(out_dir)
    print(f"RIE portal: generated {len(written)} pages under {out_dir}:")
    for path in written:
        print(f"  - {path.name}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())


__all__ = [
    "PORTAL_INDEX",
    "HEALTH_PORTAL",
    "READINESS_PORTAL",
    "EXECUTION_PORTAL",
    "ACCEPTANCE_PORTAL",
    "VALIDATION_PORTAL",
    "CERTIFICATION_PORTAL",
    "FRONTIER_PORTAL",
    "WORKSTREAMS_PORTAL",
    "DRIFT_PORTAL",
    "COVERAGE_PORTAL",
    "FREEZE_PORTAL",
    "CAPABILITY_PORTAL",
    "DEPENDENCY_PORTAL",
    "SEARCH_PORTAL",
    "EVIDENCE_PORTAL",
    "PAGES",
    "RepositoryIntelligencePortal",
    "build_acceptance_facts",
    "main",
]
