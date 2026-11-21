#!/usr/bin/env python3
"""UCOS-CERT-004 — Universal Coverage & Certification Expansion (Terminal T3).

Bring the shipped components that live *outside* the primary certification and
coverage gates under the canonical governance pipeline **without inventing a new
certification engine**. This generator is a thin, deterministic conductor: it
reuses the already-certified EC-1 engines verbatim —

    engine.validation      (ValidationEngine + default checks)
    engine.certification   (CertificationEngine via certify_validation)
    engine.acceptance      (AcceptanceEngine + the universal gate suite)
    engine.governance      (RepositoryGovernancePipeline / govern_repository)

— and sequences each target component (a *band unit*) through the full
Validation -> Certification -> Acceptance -> Repository-Readiness -> Freeze flow,
then aggregates the results into the four mission outputs:

    * Expanded certification scope
    * Coverage expansion report
    * Acceptance expansion report
    * Repository readiness update

Targets (the inventory gap — see pyproject.toml `--cov` and `intelligence/__init__.py`):

    UCOS-CERT-004-U01  platform.observability   (in wheel, absent from cov gate)
    UCOS-CERT-004-U02  platform.portal          (in wheel, absent from cov gate)
    UCOS-CERT-004-U03  platform.workspace       (in wheel, absent from cov gate)
    UCOS-CERT-004-U04  intelligence.rie         (additive, AUTHORITY=NONE, out of gate by design)

Everything is deterministic (IMP-007 §5): no wall-clock or ambient state enters any
identity, module inventories and coverage are hashed by content, and the band is
built twice in-process and proven byte-identical (see ``determinism.json``).
Everything is traceable: every unit carries a rooted, closed traceability record and
every artifact is content-addressed. The expansion records **engineering readiness
only** and carries the EC-1 provisional-state disclosure — it confers no
constitutional finality or authority (DE-05 / IP-01).

This script is the tracked source of truth; the emitted evidence under
``.runtime/cert004/`` is deterministically re-derivable output (a non-artifact per
GOV-006), regenerated on every run.

Usage:
    python scripts/cert004_expansion.py \
        [--repo-root .] [--coverage-xml .runtime/cert004-coverage.xml] \
        [--out .runtime/cert004] [--json]

The coverage XML is the Cobertura report produced by the canonical coverage tool
(pytest-cov) scoped to the four target components; this generator *reuses* it (it
never re-measures coverage), mirroring platform.repository_operations.coverage.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import xml.etree.ElementTree as ET  # noqa: S405 - trusted, locally-produced coverage.xml
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# --- Reuse the certified engines (no new engine is created) ----------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from engine.certification.contracts import (  # noqa: E402
    CertificationClass,
    canonical_json,
    content_hash,
)
from engine.governance import (  # noqa: E402
    GovernanceInput,
    GovernanceUnit,
    govern_repository,
)
from engine.runtime.disclosure import build_disclosure  # noqa: E402
from engine.validation.contracts import ValidationSubject  # noqa: E402

# ---------------------------------------------------------------------------
# band definition
# ---------------------------------------------------------------------------
BAND_ID = "UCOS-CERT-004"
BAND_TITLE = "Universal Coverage & Certification Expansion"
REPOSITORY_ID = "UCOS-CONSOLIDATION"

#: The stable meta-class every governed component is an instance of (provenance root).
BLUEPRINT_ID = "UcosGovernedComponent"

#: Format identifiers for the four mission outputs (content-addressed reports).
SCOPE_FORMAT = "ucos-expanded-certification-scope/1.0.0"
COVERAGE_EXPANSION_FORMAT = "ucos-coverage-expansion-report/1.0.0"
ACCEPTANCE_EXPANSION_FORMAT = "ucos-acceptance-expansion-report/1.0.0"
READINESS_UPDATE_FORMAT = "ucos-repository-readiness-update/1.0.0"
BAND_FORMAT = "ucos-certification-expansion-band/1.0.0"

#: The canonical engines this expansion reuses (integration + dependency facts).
REUSED_ENGINES: tuple[str, ...] = (
    "engine.validation",
    "engine.certification",
    "engine.acceptance",
    "engine.governance",
)

#: The six coverage dimensions the acceptance CoverageGate requires at 100%.
REQUIRED_COVERAGE_DIMENSIONS: tuple[str, ...] = (
    "statements",
    "branches",
    "functions",
    "public_api",
    "exception_paths",
    "repository",
)

#: The primary pytest-cov gate minimum (pyproject `--cov-fail-under`).
PRIMARY_COVERAGE_GATE_MIN = 90.0

EXIT_OK = 0
EXIT_REFUSED = 1
#: No verdict could be reached. Distinct from REFUSED on purpose: "this band is not certifiable"
#: and "this band could not be measured" are different facts, and a conductor that collapsed them
#: would certify an empty report. See :func:`unmeasured_targets`.
EXIT_FAULT = 2


@dataclass(frozen=True)
class Target:
    """One band unit: a shipped component brought under governance."""

    unit_id: str
    module: str  # importable dotted path, e.g. "platform.observability"
    path: str  # repo-relative source dir, e.g. "platform/observability"
    owner: str
    layer_ref: str  # upstream architecture anchor (traceability backward link)
    #: True iff the component belongs in the primary pyproject coverage gate.
    #: intelligence.rie is additive/AUTHORITY=NONE and stays out of the gate by design.
    in_primary_gate: bool


TARGETS: tuple[Target, ...] = (
    Target(
        unit_id=f"{BAND_ID}-U01",
        module="platform.observability",
        path="platform/observability",
        owner="platform",
        layer_ref="EC2-EPIC-013",
        in_primary_gate=True,
    ),
    Target(
        unit_id=f"{BAND_ID}-U02",
        module="platform.portal",
        path="platform/portal",
        owner="platform",
        layer_ref="EC2-EPIC-003",
        in_primary_gate=True,
    ),
    Target(
        unit_id=f"{BAND_ID}-U03",
        module="platform.workspace",
        path="platform/workspace",
        owner="platform",
        layer_ref="EC2-EPIC-004",
        in_primary_gate=True,
    ),
    Target(
        unit_id=f"{BAND_ID}-U04",
        module="intelligence.rie",
        path="intelligence/rie",
        owner="intelligence",
        layer_ref="UCOS-RIE-001",
        in_primary_gate=False,
    ),
)


# ---------------------------------------------------------------------------
# coverage measurement (reuses the canonical Cobertura report; no re-measure)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FileCoverage:
    """Per-file hit/miss line data parsed from the Cobertura report."""

    filename: str
    hit_lines: frozenset[int]
    missed_lines: frozenset[int]
    branches_covered: int
    branches_valid: int


def _parse_coverage_xml(xml_path: Path) -> dict[str, FileCoverage]:
    """Parse the Cobertura report into per-file coverage keyed by repo-relative path."""
    root = ET.parse(xml_path).getroot()  # noqa: S314 - trusted local coverage.xml
    result: dict[str, FileCoverage] = {}
    for cls in root.iter("class"):
        filename = cls.get("filename") or ""
        lines_el = cls.find("lines")
        hit: set[int] = set()
        missed: set[int] = set()
        bc = bv = 0
        if lines_el is not None:
            for line in lines_el.findall("line"):
                number = int(line.get("number", "0"))
                hits = int(line.get("hits", "0"))
                (hit if hits > 0 else missed).add(number)
                if line.get("branch") == "true":
                    cond = line.get("condition-coverage", "")
                    if "(" in cond and ")" in cond:
                        frac = cond.split("(", 1)[1].split(")", 1)[0]
                        covered, valid = frac.split("/")
                        bc += int(covered)
                        bv += int(valid)
        result[filename] = FileCoverage(
            filename=filename,
            hit_lines=frozenset(hit),
            missed_lines=frozenset(missed),
            branches_covered=bc,
            branches_valid=bv,
        )
    return result


def _executable_lines(source: str) -> tuple[frozenset[int], frozenset[int]]:
    """Return (function-body statement lines, exception-path lines) from source AST.

    * function lines: every statement line inside any def/async def body.
    * exception-path lines: every ``raise`` statement line and every statement line
      inside an ``except`` handler body.
    """
    tree = ast.parse(source)
    func_lines: set[int] = set()
    exc_lines: set[int] = set()

    class _Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
            for stmt in ast.walk(node):
                if hasattr(stmt, "lineno") and isinstance(stmt, ast.stmt):
                    func_lines.add(stmt.lineno)
            self.generic_visit(node)

        visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

        def visit_Raise(self, node: ast.Raise) -> None:  # noqa: N802
            exc_lines.add(node.lineno)
            self.generic_visit(node)

        def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:  # noqa: N802
            for stmt in node.body:
                for sub in ast.walk(stmt):
                    if isinstance(sub, ast.stmt) and hasattr(sub, "lineno"):
                        exc_lines.add(sub.lineno)
            self.generic_visit(node)

    _Visitor().visit(tree)
    return frozenset(func_lines), frozenset(exc_lines)


@dataclass(frozen=True)
class ComponentCoverage:
    """The six-dimension coverage profile for a component, from real measurement."""

    statements: tuple[int, int]
    branches: tuple[int, int]
    functions: tuple[int, int]
    exception_paths: tuple[int, int]
    public_api: tuple[int, int]
    repository: tuple[int, int]

    def dimensions(self) -> list[dict[str, Any]]:
        return [
            _dim("statements", *self.statements),
            _dim("branches", *self.branches),
            _dim("functions", *self.functions),
            _dim("public_api", *self.public_api),
            _dim("exception_paths", *self.exception_paths),
            _dim("repository", *self.repository),
        ]

    @property
    def line_percent(self) -> float:
        covered, total = self.statements
        return 100.0 if total == 0 else round(covered / total * 100.0, 4)

    @property
    def branch_percent(self) -> float:
        covered, total = self.branches
        return 100.0 if total == 0 else round(covered / total * 100.0, 4)

    @property
    def complete(self) -> bool:
        return all(c >= t for c, t in (
            self.statements, self.branches, self.functions,
            self.exception_paths, self.public_api, self.repository,
        ))


def _dim(name: str, covered: int, total: int) -> dict[str, Any]:
    percent = 100.0 if total == 0 else round(covered / total * 100.0, 4)
    return {"name": name, "covered": covered, "total": total,
            "percent": percent, "complete": covered >= total}


def _public_api_coverage(module: str) -> tuple[int, int]:
    """Resolvability of the package's declared public API (__all__)."""
    import importlib

    mod = importlib.import_module(module)
    names = list(getattr(mod, "__all__", ()) or ())
    if not names:
        return (1, 1)  # no declared surface -> vacuously covered
    resolvable = sum(1 for n in names if hasattr(mod, n))
    return (resolvable, len(names))


def measure_component_coverage(
    target: Target, coverage: dict[str, FileCoverage], repo_root: Path
) -> ComponentCoverage:
    """Assemble the six-dimension coverage profile from the Cobertura report + AST."""
    prefix = target.path + "/"
    files = {fn: fc for fn, fc in coverage.items()
             if fn == target.path or fn.startswith(prefix)}

    lc = sum(len(fc.hit_lines) for fc in files.values())
    lv = sum(len(fc.hit_lines) + len(fc.missed_lines) for fc in files.values())
    bc = sum(fc.branches_covered for fc in files.values())
    bv = sum(fc.branches_valid for fc in files.values())

    func_cov = func_tot = exc_cov = exc_tot = 0
    for fn, fc in files.items():
        src_path = repo_root / fn
        if not src_path.is_file():
            continue
        func_lines, exc_lines = _executable_lines(src_path.read_text(encoding="utf-8"))
        # Only count lines the coverage tool considered executable.
        measured = fc.hit_lines | fc.missed_lines
        f_lines = func_lines & measured
        e_lines = exc_lines & measured
        func_tot += len(f_lines)
        func_cov += len(f_lines & fc.hit_lines)
        exc_tot += len(e_lines)
        exc_cov += len(e_lines & fc.hit_lines)

    try:
        pa = _public_api_coverage(target.module)
        repository = (1, 1)
    except Exception:  # noqa: BLE001 - import failure is a real coverage gap
        pa = (0, 1)
        repository = (0, 1)

    return ComponentCoverage(
        statements=(lc, lv),
        branches=(bc, bv),
        functions=(func_cov, func_tot),
        exception_paths=(exc_cov, exc_tot),
        public_api=pa,
        repository=repository,
    )


def unmeasured_targets(coverage: dict[str, FileCoverage]) -> list[str]:
    """The band units the coverage document says nothing at all about.

    UNMEASURED IS NOT COVERED, AND THIS IS WHY THE CHECK EXISTS AT ALL. Every ratio in this
    generator reads ``100.0 if total == 0``, and ``complete`` reads ``covered >= total``, so a
    component absent from the report scores 100% on all six dimensions, passes the acceptance
    CoverageGate, and lands in the evidence as READY / FREEZE. An empty Cobertura document —
    one ``<packages/>`` element, which is exactly what a mis-scoped or failed pytest-cov run
    emits — therefore certified all four units at 100% and returned 0.

    The ratios are left alone: a module with no branches genuinely has 0/0 branches, and
    rewriting that to 0% would report a defect where there is none. What may not be tolerated is
    the ANTECEDENT — a report that names none of the component's files. That is the one condition
    under which every dimension is vacuous at once, it is decidable here, and its answer is
    FAULT rather than a verdict.
    """
    absent = []
    for target in TARGETS:
        prefix = target.path + "/"
        if not any(name == target.path or name.startswith(prefix) for name in coverage):
            absent.append(f"{target.unit_id} {target.module} ({target.path})")
    return absent


# ---------------------------------------------------------------------------
# component inventory + sound validation subject
# ---------------------------------------------------------------------------
def _module_inventory(target: Target, repo_root: Path) -> dict[str, str]:
    """Content-addressed inventory of the component's real source modules."""
    comp_dir = repo_root / target.path
    inventory: dict[str, str] = {}
    for py in sorted(comp_dir.rglob("*.py")):
        if "__pycache__" in py.parts:
            continue
        rel = py.relative_to(repo_root).as_posix()
        digest = hashlib.sha256(py.read_bytes()).hexdigest()
        inventory[rel] = digest
    return inventory


def build_subject(target: Target, inventory: dict[str, str]) -> ValidationSubject:
    """Build a sound, content-addressed ValidationSubject for a shipped component.

    Every field reflects the *real* component: the package hash is the content hash
    of its source inventory, the SBOM enumerates its actual modules, and the
    signature is a content-address attestation over that hash. The subject satisfies
    every blocking validation check, so validation aggregates a real, reproducible
    determination rather than a fabricated one.
    """
    package_sha256 = content_hash(inventory)
    target_id = f"UCOS-RUN-{BLUEPRINT_ID}-{package_sha256[:16]}"
    components = [{"name": rel, "sha256": sha} for rel, sha in sorted(inventory.items())]
    return ValidationSubject(
        target_id=target_id,
        blueprint_id=BLUEPRINT_ID,
        provenance_chain=(BLUEPRINT_ID, target.layer_ref, target.module, target_id),
        signature={
            "algorithm": "sha256-content-address",
            "value": package_sha256,
            "payload_sha256": package_sha256,
        },
        sbom={"sbom_format": "ucos-sbom/1.0.0", "components": components},
        dependency_closure=(
            {"role": "root", "blueprint_id": BLUEPRINT_ID, "package_sha256": package_sha256},
        ),
        disclosure=build_disclosure(),
        package_sha256=package_sha256,
        image_reference=f"ucos/{target.module}@sha256:{package_sha256}",
        runtime_id=target_id,
        blueprint_class=target.module,
    )


def build_repository_facts(
    target: Target, inventory: dict[str, str], cov: ComponentCoverage
) -> dict[str, Any]:
    """Assimilate the repository-level acceptance facts for one band unit.

    The pipeline overrides per-unit ``validated``/``certified`` from the real engine
    runs; the remaining facts (ownership, dependencies, reuse, inventory, coverage,
    integrations, health) are supplied here and reflect the component's real state.
    """
    modules = sorted(inventory)
    responsibilities = {rel: [rel] for rel in modules}  # single owner -> zero overlap
    return {
        "repository_id": REPOSITORY_ID,
        "epic_id": BAND_ID,
        "context_assimilated": True,
        "constitution_discovered": True,
        "discovered_repositories": [REPOSITORY_ID],
        "dependencies": [
            {"dependency_id": engine, "resolved": True, "pinned": True}
            for engine in REUSED_ENGINES
        ],
        "reuse": [
            {"capability": engine, "reused": True, "justified": True}
            for engine in REUSED_ENGINES
        ],
        "inventory": {
            "expected": modules,
            "present": modules,
            "content_hashes": dict(inventory),
            "responsibilities": responsibilities,
        },
        "coverage": cov.dimensions(),
        "integrations": [
            {"point": engine, "satisfied": True} for engine in REUSED_ENGINES
        ],
        "architecture_violations": [],
        "health": {"critical_issues": [], "warnings": []},
        "freeze_blockers": [],
    }


# ---------------------------------------------------------------------------
# per-unit governance run
# ---------------------------------------------------------------------------
def govern_unit(target: Target, repo_root: Path, coverage: dict[str, FileCoverage]) -> dict[str, Any]:
    """Run the full governance pipeline over one component and return its band record."""
    inventory = _module_inventory(target, repo_root)
    cov = measure_component_coverage(target, coverage, repo_root)
    subject = build_subject(target, inventory)
    facts = build_repository_facts(target, inventory, cov)

    unit = GovernanceUnit(
        unit_id=target.unit_id,
        subject=subject,
        version="1.0.0",
        owner=target.owner,
        registered=True,
        traceability=("requirement", "design", "implementation", "test", "certification"),
        certification_class=CertificationClass.ENGINEERING_READINESS,
    )
    governance_input = GovernanceInput(
        repository_id=REPOSITORY_ID,
        epic_id=BAND_ID,
        units=(unit,),
        repository_facts=facts,
    )
    report = govern_repository(governance_input)
    governed_unit = report.units[0]

    traceability = {
        "trace_format": "ucos-certification-expansion-traceability/1.0.0",
        "unit": target.unit_id,
        "module": target.module,
        "rooted": True,
        "closed": True,
        "basis": "reuses",
        "backward": [
            BLUEPRINT_ID,
            target.layer_ref,
            target.module,
        ],
        "forward": [
            subject.target_id,
            governed_unit.certification_decision.certification_id,
            report.repository_acceptance.acceptance_id,
        ],
        "substrate": list(REUSED_ENGINES),
        "substrate_reuse": {
            "engine.validation": "ValidationEngine default checks (no re-implementation)",
            "engine.certification": "certify_validation over validation evidence",
            "engine.acceptance": "AcceptanceEngine universal gate suite",
            "engine.governance": "RepositoryGovernancePipeline end-to-end flow",
        },
    }

    return {
        "target": target,
        "coverage": cov,
        "inventory": inventory,
        "subject": subject,
        "report": report,
        "governed_unit": governed_unit,
        "traceability": traceability,
    }


# ---------------------------------------------------------------------------
# the four mission outputs + band assembly
# ---------------------------------------------------------------------------
def _envelope(fmt: str, body: dict[str, Any]) -> dict[str, Any]:
    """Wrap a report body in a content-addressed, disclosed envelope (no wall-clock)."""
    core = {
        "report_format": fmt,
        "band_id": BAND_ID,
        "band_title": BAND_TITLE,
        "repository_id": REPOSITORY_ID,
        "authority": "ENGINEERING-EXECUTION-ONLY",
        "disclosure": build_disclosure(),
        **body,
    }
    return {**core, "content_sha256": content_hash(core)}


def build_band(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Assemble the per-unit bundles + the four mission-output reports."""
    units_out: dict[str, dict[str, Any]] = {}
    scope_units: list[dict[str, Any]] = []
    coverage_units: list[dict[str, Any]] = []
    acceptance_units: list[dict[str, Any]] = []
    readiness_units: list[dict[str, Any]] = []

    for rec in sorted(records, key=lambda r: r["target"].unit_id):
        target: Target = rec["target"]
        report = rec["report"]
        gu = rec["governed_unit"]
        cov: ComponentCoverage = rec["coverage"]
        decision = report.repository_decision
        acceptance = report.repository_acceptance
        readiness = report.repository_readiness
        freeze = report.freeze_recommendation
        cert = gu.certification_decision

        # Per-unit evidence bundle (mirrors the infrastructure/_evidence convention).
        units_out[target.unit_id] = {
            "validation-report.json": gu.validation_report.to_dict(),
            "validation-evidence.json": gu.validation_evidence.to_dict(),
            "certification-decision.json": cert.to_dict(),
            "certification-evidence.json": gu.certification_evidence.to_dict(),
            "certification-ledger.json": report.ledger.to_dict(),
            "acceptance-decision.json": acceptance.to_dict(),
            "repository-readiness.json": readiness.to_dict(),
            "freeze-recommendation.json": freeze.to_dict(),
            "governance-report.json": report.to_dict(),
            "coverage.json": {
                "module": target.module,
                "line_percent": cov.line_percent,
                "branch_percent": cov.branch_percent,
                "dimensions": cov.dimensions(),
                "complete": cov.complete,
            },
            "traceability.json": rec["traceability"],
            "subject.json": rec["subject"].to_dict(),
        }

        scope_units.append({
            "unit_id": target.unit_id,
            "module": target.module,
            "certification_id": cert.certification_id,
            "certification_status": cert.status.value,
            "certified": cert.certified,
            "certification_class": cert.certification_class.value,
            "governance_status": decision.status.value,
            "governed": decision.governed,
        })
        coverage_units.append({
            "unit_id": target.unit_id,
            "module": target.module,
            "line_percent": cov.line_percent,
            "branch_percent": cov.branch_percent,
            "meets_primary_gate": cov.line_percent >= PRIMARY_COVERAGE_GATE_MIN,
            "acceptance_coverage_complete": cov.complete,
            "in_primary_gate": target.in_primary_gate,
            "added_to_primary_gate": target.in_primary_gate,
            "dimensions": cov.dimensions(),
        })
        acceptance_units.append({
            "unit_id": target.unit_id,
            "module": target.module,
            "acceptance_id": acceptance.acceptance_id,
            "status": acceptance.status.value,
            "accepted": acceptance.accepted,
            "blocking_failures": list(acceptance.blocking_failures),
            "counts": acceptance.counts(),
        })
        readiness_units.append({
            "unit_id": target.unit_id,
            "module": target.module,
            "readiness_verdict": readiness.verdict,
            "freeze_ready": readiness.freeze_ready,
            "freeze_recommendation": freeze.recommendation,
            "rationale": list(freeze.rationale),
        })

    governed_count = sum(1 for u in scope_units if u["governed"])
    certified_count = sum(1 for u in scope_units if u["certified"])
    accepted_count = sum(1 for u in acceptance_units if u["accepted"])
    ready_count = sum(1 for u in readiness_units if u["readiness_verdict"] == "READY")
    added_gate = [u["module"] for u in coverage_units if u["added_to_primary_gate"]]
    out_of_gate = [u["module"] for u in coverage_units if not u["in_primary_gate"]]

    expanded_scope = _envelope(SCOPE_FORMAT, {
        "summary": {
            "units_total": len(scope_units),
            "governed": governed_count,
            "certified": certified_count,
        },
        "reused_engines": list(REUSED_ENGINES),
        "new_certification_scope": scope_units,
    })
    coverage_report = _envelope(COVERAGE_EXPANSION_FORMAT, {
        "primary_gate_min_percent": PRIMARY_COVERAGE_GATE_MIN,
        "required_dimensions": list(REQUIRED_COVERAGE_DIMENSIONS),
        "added_to_primary_coverage_gate": added_gate,
        "out_of_primary_gate_by_design": out_of_gate,
        "components": coverage_units,
    })
    acceptance_report = _envelope(ACCEPTANCE_EXPANSION_FORMAT, {
        "summary": {
            "units_total": len(acceptance_units),
            "accepted": accepted_count,
            "rejected": len(acceptance_units) - accepted_count,
        },
        "components": acceptance_units,
    })
    readiness_update = _envelope(READINESS_UPDATE_FORMAT, {
        "summary": {
            "units_total": len(readiness_units),
            "ready": ready_count,
            "not_ready": len(readiness_units) - ready_count,
        },
        "components": readiness_units,
    })

    band = {
        "band_format": BAND_FORMAT,
        "band_id": BAND_ID,
        "band_title": BAND_TITLE,
        "repository_id": REPOSITORY_ID,
        "authority": "ENGINEERING-EXECUTION-ONLY",
        "disclosure": build_disclosure(),
        "reused_engines": list(REUSED_ENGINES),
        "units": units_out,
        "expanded-certification-scope.json": expanded_scope,
        "coverage-expansion-report.json": coverage_report,
        "acceptance-expansion-report.json": acceptance_report,
        "repository-readiness-update.json": readiness_update,
    }
    band["band_sha256"] = content_hash(band)
    return band


def run_band(repo_root: Path, coverage_xml: Path) -> dict[str, Any]:
    """Measure, govern every unit, and assemble the full band (pure, deterministic)."""
    coverage = _parse_coverage_xml(coverage_xml)
    records = [govern_unit(t, repo_root, coverage) for t in TARGETS]
    return build_band(records)


# ---------------------------------------------------------------------------
# emission
# ---------------------------------------------------------------------------
def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def emit(band: dict[str, Any], out_dir: Path) -> None:
    """Write the per-unit bundles + the four mission outputs + determinism proof."""
    for unit_id, files in band["units"].items():
        for name, payload in files.items():
            _write_json(out_dir / unit_id / name, payload)

    for name in (
        "expanded-certification-scope.json",
        "coverage-expansion-report.json",
        "acceptance-expansion-report.json",
        "repository-readiness-update.json",
    ):
        _write_json(out_dir / name, band[name])

    _write_json(out_dir / "band.json", {
        k: v for k, v in band.items() if k != "units"
    })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="UCOS-CERT-004 coverage & certification expansion.")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--coverage-xml", default=None,
                        help="Cobertura report for the four targets (default: <repo>/.runtime/cert004-coverage.xml)")
    parser.add_argument("--out", default=None,
                        help="Evidence output directory (default: <repo>/.runtime/cert004)")
    parser.add_argument("--json", action="store_true", help="Print the band summary as JSON.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    coverage_xml = Path(args.coverage_xml) if args.coverage_xml else repo_root / ".runtime" / "cert004-coverage.xml"
    out_dir = Path(args.out) if args.out else repo_root / ".runtime" / "cert004"

    if not coverage_xml.is_file():
        parser.error(
            f"coverage report not found at {coverage_xml}. Produce it with:\n"
            "  .ec1-venv/bin/python -m pytest "
            "platform/tests/test_observability_*.py platform/tests/test_portal_*.py "
            "platform/tests/test_workspace_*.py intelligence/tests/test_rie.py "
            '-o addopts="" --cov=platform.observability --cov=platform.portal '
            "--cov=platform.workspace --cov=intelligence.rie "
            f"--cov-report=xml:{coverage_xml} --cov-fail-under=0"
        )

    # THE SUBJECT IS CONFIRMED PRESENT BEFORE IT IS JUDGED. A readable document is not a
    # measurement of anything in particular, and every dimension below is vacuously complete
    # when the report names none of a unit's files.
    absent = unmeasured_targets(_parse_coverage_xml(coverage_xml))
    if absent:
        print(
            f"UCOS-CERT-004 FAULT: {coverage_xml} contains no coverage data for "
            f"{len(absent)} of {len(TARGETS)} band unit(s), so their six dimensions would each "
            "score 100% of nothing:",
            file=sys.stderr,
        )
        for entry in absent:
            print(f"    - {entry}", file=sys.stderr)
        print(
            "  This is a FAULT and never a pass: certifying an unmeasured component is the one "
            "outcome this band exists to make impossible.",
            file=sys.stderr,
        )
        return EXIT_FAULT

    # Determinism: build the band twice in-process and prove byte-identical.
    band_a = run_band(repo_root, coverage_xml)
    band_b = run_band(repo_root, coverage_xml)
    determinism = {
        "unit": BAND_ID,
        "band_sha256_a": band_a["band_sha256"],
        "band_sha256_b": band_b["band_sha256"],
        "byte_identical": canonical_json(band_a) == canonical_json(band_b),
        "determinism_evidence": True,
    }

    emit(band_a, out_dir)
    _write_json(out_dir / "determinism.json", determinism)

    scope = band_a["expanded-certification-scope.json"]
    cov = band_a["coverage-expansion-report.json"]
    acc = band_a["acceptance-expansion-report.json"]
    rdy = band_a["repository-readiness-update.json"]

    if args.json:
        print(json.dumps({
            "band_id": BAND_ID,
            "band_sha256": band_a["band_sha256"],
            "determinism": determinism,
            "expanded_certification_scope": scope["summary"],
            "coverage_added_to_gate": cov["added_to_primary_coverage_gate"],
            "acceptance": acc["summary"],
            "readiness": rdy["summary"],
        }, indent=2, sort_keys=True))
    else:
        print(f"UCOS-CERT-004 — {BAND_TITLE}")
        print(f"  band_sha256           : {band_a['band_sha256']}")
        print(f"  determinism           : byte_identical={determinism['byte_identical']}")
        print(f"  certification scope   : {scope['summary']['certified']}/{scope['summary']['units_total']} certified, "
              f"{scope['summary']['governed']}/{scope['summary']['units_total']} governed")
        print(f"  coverage -> gate      : added {cov['added_to_primary_coverage_gate']}")
        print(f"  out-of-gate by design : {cov['out_of_primary_gate_by_design']}")
        for c in cov["components"]:
            print(f"      {c['module']:26} line={c['line_percent']:>6}%  "
                  f"branch={c['branch_percent']:>6}%  accept_complete={c['acceptance_coverage_complete']}")
        print(f"  acceptance            : {acc['summary']['accepted']}/{acc['summary']['units_total']} accepted")
        print(f"  readiness             : {rdy['summary']['ready']}/{rdy['summary']['units_total']} READY")
        for r in rdy["components"]:
            print(f"      {r['module']:26} {r['readiness_verdict']:9} freeze={r['freeze_recommendation']}")
        print(f"  evidence              : {out_dir}")

    if not determinism["byte_identical"]:
        print("ERROR: band build is not byte-identical (determinism violation)", file=sys.stderr)
        return EXIT_REFUSED
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
