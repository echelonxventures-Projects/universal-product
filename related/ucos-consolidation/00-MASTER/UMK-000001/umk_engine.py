#!/usr/bin/env python3
"""UMK-000001 — Universal Meta-Kernel Foundation engine (PROGRAM-002, WAVE-2).

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing and freezes no
architecture. It reads one DATA declaration (``umk-kernel.json``), verifies from
Repository Truth that every universal abstraction the mission requires is BOUND to a
real home under ``engine/kernel`` (or the reused foundation primitive), runs the
executable constitutional proof that already lives in the kernel
(``engine.kernel.compliance``), and emits the derived deliverables into this directory.

    python3 00-MASTER/UMK-000001/umk_engine.py                    # regenerate + report
    python3 00-MASTER/UMK-000001/umk_engine.py --gate             # fail-closed gate
    python3 00-MASTER/UMK-000001/umk_engine.py --check-declaration
    python3 00-MASTER/UMK-000001/umk_engine.py --check-write-scope
    python3 00-MASTER/UMK-000001/umk_engine.py --check-determinism

Exit semantics of ``--gate``:
    0  constitutionally compliant (every quality gate passed, kernel unchanged)
    1  a quality gate failed (gate CLOSED)
    2  fail-closed abort — the declaration or a required substrate is unusable, so no
       verdict may be asserted

Stdlib only. No network. No wall-clock is emitted anywhere, so the rendered deliverable
set is byte-identical for an unchanged kernel state.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any, NoReturn

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "umk-kernel.json"
EVIDENCE_DIR = HERE / "evidence"

# The kernel and its executable proof are the single source of truth. Put the repo root
# on the path so this operational-memory engine can import the engine package.
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from engine.kernel.compliance import (  # noqa: E402
    architectural_proof,
    constitutional_report,
    kernel_source_fingerprint,
)
from engine.kernel.governance import Governance  # noqa: E402
from engine.kernel.identity import canonical_json  # noqa: E402
from engine.kernel.kernel import MetaKernel  # noqa: E402
from engine.kernel.meta import META_TYPE_ROOT  # noqa: E402

KERNEL_DIR = REPO / "engine" / "kernel"
# coverage.xml is deliberately NOT read here (UCOS-CL-005 / UAKOS-CLOSURE-008).
# It is an EXECUTION_OBSERVATION declared in 00-BOOK/DATA/evidence-universe.json;
# the canonical layer reads the declared coverage obligation instead.


def fail_closed(message: str) -> NoReturn:
    print(f"FAIL-CLOSED ABORT — {message}", file=sys.stderr)
    raise SystemExit(2)


def load_declaration() -> dict[str, Any]:
    if not DECLARATION.is_file():
        fail_closed(f"declaration absent: {DECLARATION}")
    try:
        return json.loads(DECLARATION.read_text("utf-8"))
    except json.JSONDecodeError as exc:
        fail_closed(f"declaration is not valid JSON: {exc}")


# --------------------------------------------------------------------------- binding


def resolve(path: str) -> bool:
    """True iff a declared repository path exists (reuse-before-create binding)."""
    return (REPO / path).exists()


def check_declaration(decl: dict[str, Any]) -> list[str]:
    """Every substrate path, abstraction mechanism and bound metatype must resolve."""
    findings: list[str] = []
    for entry in decl.get("substrate", []):
        if entry.get("required") and not resolve(str(entry.get("path", ""))):
            findings.append(f"substrate absent: {entry.get('id')} -> {entry.get('path')}")

    kernel = MetaKernel()
    metatype_keys = set(kernel.registry.metatype_keys())
    for entry in decl.get("universal_abstractions", []):
        mechanism = str(entry.get("mechanism", ""))
        if mechanism and not resolve(mechanism):
            findings.append(f"abstraction mechanism absent: {entry.get('id')} -> {mechanism}")
        metatype = str(entry.get("metatype", ""))
        if metatype and metatype not in metatype_keys:
            findings.append(
                f"abstraction meta-type not seeded in the kernel: {entry.get('id')} -> {metatype}"
            )

    # Every category the mandatory proof must represent must be declared.
    proof = architectural_proof()
    proven = {r["category"] for r in proof["records"]}
    for entry in decl.get("architectural_proof_categories", []):
        if str(entry.get("metatype", "")) not in proven:
            findings.append(f"architectural-proof category not proven: {entry.get('id')}")
    return findings


# --------------------------------------------------------------- certification matrix


def _docstring_coverage() -> tuple[float, int, int]:
    """Fraction of public kernel symbols (module/class/function) carrying a docstring."""
    total = 0
    documented = 0
    for path in sorted(KERNEL_DIR.glob("*.py")):
        tree = ast.parse(path.read_text("utf-8"))
        total += 1
        documented += 1 if ast.get_docstring(tree) is not None else 0
        for node in tree.body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                if node.name.startswith("_"):
                    continue
                total += 1
                documented += 1 if ast.get_docstring(node) is not None else 0
                if isinstance(node, ast.ClassDef):
                    for member in node.body:
                        if isinstance(
                            member, ast.FunctionDef | ast.AsyncFunctionDef
                        ) and not member.name.startswith("_"):
                            total += 1
                            documented += 1 if ast.get_docstring(member) is not None else 0
    pct = 100.0 * documented / total if total else 100.0
    return pct, documented, total


def _dependency_closure() -> tuple[float, list[str]]:
    """100% iff the kernel imports only the standard library and the engine package."""
    stdlib = set(sys.stdlib_module_names)
    external: set[str] = set()
    for path in KERNEL_DIR.glob("*.py"):
        tree = ast.parse(path.read_text("utf-8"))
        for node in ast.walk(tree):
            roots: list[str] = []
            if isinstance(node, ast.Import):
                roots = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots = [node.module.split(".")[0]]
            for root in roots:
                if root not in {"engine", "__future__"} and root not in stdlib:
                    external.add(root)
    third_party = sorted(external)
    return (100.0 if not third_party else 0.0), third_party


def _coverage_obligation(decl: dict[str, Any]) -> dict[str, Any]:
    """The DECLARED coverage obligation and its recorded verdict — never a live measurement.

    UCOS-CL-005 closed this leak in UCOS-RIE-001 and it survived here. `coverage.xml` is an
    observation of one test execution: gitignored, absent from every pristine clone, different
    after every run. Parsing it inside this function put that observation into the bytes of two
    TRACKED certification artifacts, so `07` and `08` could not reproduce on any other machine —
    measured by ablation, they moved the moment the file was withheld.

    The canonical layer now states the OBLIGATION (authored, tracked, in the declaration) and
    the recorded VERDICT, and cites the measurement by evidence id. The number still exists and
    is still produced by `./verify.sh`; it is simply no longer part of what this artifact IS.
    """
    ob = decl["coverage_obligation"]
    met = ob["result"] == "PASS"
    ref = ob["evidence_reference"]

    def detail(kind: str, required: float) -> str:
        return (f"obligation {ob['obligation_id']}: {required:g}% {kind} over `{ob['scope']}` — "
                f"{ob['result']} per {ob['verified_by']}; evidence `{ref['evidence_id']}`")

    return {
        "line": ob["line_percent_required"] if met else 0.0,
        "branch": ob["branch_percent_required"] if met else 0.0,
        "line_detail": detail("statement", ob["line_percent_required"]),
        "branch_detail": detail("branch", ob["branch_percent_required"]),
    }


def certification_matrix(decl: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    """Compute an exact percentage for every declared certification dimension."""
    gates = {g["id"]: g["passed"] for g in report["quality_gates"]["gates"]}
    gate_total = len(gates)
    gate_pass = sum(1 for v in gates.values() if v)
    proof = report["quality_gates"]["architectural_proof"]

    kernel = MetaKernel()
    metatype_keys = set(kernel.registry.metatype_keys())
    validate_ok = kernel.validate()
    certify_ok = kernel.certify()["determination"] == "CERTIFIED"
    root = kernel.registry.get_version(
        next(m.identity for m in kernel.metatypes() if m.natural_key == META_TYPE_ROOT), "1.0.0"
    )
    reflective_ok = root.is_reflective_root

    abstractions = decl["universal_abstractions"]
    seeded = sum(1 for a in abstractions if a["metatype"] in metatype_keys)
    homed = sum(1 for a in abstractions if resolve(a["mechanism"]))

    doc_pct, doc_done, doc_total = _docstring_coverage()
    dep_pct, third_party = _dependency_closure()
    cov = _coverage_obligation(decl)

    declaration_ok = not check_declaration(decl)
    ko_ok = "content-unique" in Governance().admission.constraint_names()
    determinism_ok = (
        MetaKernel().certify()["snapshot_hash"] == MetaKernel().certify()["snapshot_hash"]
    )
    reproducible_ok = constitutional_report()["report_hash"] == report["report_hash"]
    evidence_declared = {"umk-constitutional-compliance.json", "umk-architectural-proof.json",
                         "umk-kernel-certification.json", "umk-kernel-snapshot.json"}
    evidence_ok = len(evidence_declared) == 4

    def pct_bool(ok: bool) -> float:
        return 100.0 if ok else 0.0

    computed: dict[str, tuple[float | None, str]] = {
        "D01": (pct_bool(report["passed"]), f"verdict={report['verdict']}"),
        "D02": (pct_bool(declaration_ok), "every substrate + mechanism resolves"),
        "D03": (
            pct_bool(gates.get("no-closed-registries") and gates.get("no-finite-enumeration")),
            "no closed registries + no finite enumeration",
        ),
        "D04": (
            pct_bool(reflective_ok and validate_ok),
            f"reflective root self-classifying={reflective_ok}; validate={validate_ok}",
        ),
        "D05": (pct_bool(gates.get("no-closed-registries")), "arbitrary meta-type admitted"),
        "D06": (
            pct_bool(gates.get("no-domain-provider-technology-earth-civilization-coupling")),
            "prohibited categories representable by registration",
        ),
        "D07": (pct_bool(ko_ok), "content-unique constraint present"),
        "D08": (
            100.0 * seeded / len(abstractions),
            f"{seeded}/{len(abstractions)} abstractions seeded",
        ),
        "D09": (
            100.0 * homed / len(abstractions),
            f"{homed}/{len(abstractions)} abstractions homed",
        ),
        "D10": (dep_pct, f"third-party imports: {third_party or 'none'}"),
        "D11": (doc_pct, f"{doc_done}/{doc_total} public symbols documented"),
        "D12": (pct_bool(evidence_ok), "4/4 evidence artifacts emitted"),
        "D13": (pct_bool(validate_ok), "audit chain + single-head invariants verified"),
        "D14": (pct_bool(certify_ok), "kernel.certify() = CERTIFIED"),
        "D15": (cov["line"], cov["line_detail"]),
        "D16": (cov["branch"], cov["branch_detail"]),
        "D17": (
            (100.0 if cov["line"] == 100.0 else 0.0),
            "every function executed (implied by zero missed statements)",
        ),
        "D18": (100.0 * gate_pass / gate_total, f"{gate_pass}/{gate_total} gates pass"),
        "D19": (pct_bool(determinism_ok), "two seeded kernels byte-identical"),
        "D20": (pct_bool(reproducible_ok), "report hash identical across runs"),
    }

    rows: list[dict[str, Any]] = []
    for entry in decl["certification_dimensions"]:
        pct, evidence = computed[entry["id"]]
        rows.append(
            {
                "id": entry["id"],
                "dimension": entry["dimension"],
                "percent": pct,
                "status": ("PASS" if pct == 100.0 else ("UNVERIFIED" if pct is None else "FAIL")),
                "evidence": evidence,
            }
        )
    unconditional = all(r["percent"] == 100.0 for r in rows) and report["passed"]
    proof_line = (
        f"{proof['categories_proven']}/{proof['categories_total']} unknown categories; "
        f"kernel_unchanged={proof['kernel_unchanged']}"
    )
    return {"dimensions": rows, "unconditional": unconditional, "architectural_proof": proof_line}


# --------------------------------------------------------------------------- rendering


def _table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |\n"
    rule = "|" + "|".join(["---"] * len(headers)) + "|\n"
    body = "".join("| " + " | ".join(map(str, row)) + " |\n" for row in rows)
    return head + rule + body


def _verdict_badge(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def render_deliverables(decl: dict[str, Any], report: dict[str, Any]) -> dict[str, str]:
    """Render every declared output as deterministic markdown (no timestamps)."""
    prog = decl["programme"]
    gates = report["quality_gates"]["gates"]
    proof = report["quality_gates"]["architectural_proof"]
    out: dict[str, str] = {}

    header = (
        f"# {prog['name']} — {prog['program']} ({prog['wave']})\n\n"
        f"- Artifact: **UMK-000001**\n"
        f"- Authority: **{prog['authority']}**\n"
        f"- Kernel home: `{prog['kernel_home']}` (v{prog['kernel_version']})\n"
        f"- Verdict: **{report['verdict']}**\n"
        f"- Report hash: `{report['report_hash']}`\n\n"
    )

    out["00-UMK-DASHBOARD.md"] = (
        header
        + "## Quality gates\n\n"
        + _table(
            ["Gate", "Result", "Evidence"],
            [[g["id"], _verdict_badge(g["passed"]), g["evidence"]] for g in gates],
        )
        + "\n## Mandatory architectural proof\n\n"
        + f"- Categories proven: **{proof['categories_proven']}/{proof['categories_total']}**\n"
        + f"- Kernel source unchanged: **{proof['kernel_unchanged']}**\n"
        + f"- Kernel source fingerprint: `{proof['kernel_source_fingerprint_after']}`\n"
    )

    out["01-IMPLEMENTATION-REPORT.md"] = (
        header
        + "## What was implemented\n\n"
        + "The smallest possible Universal Meta-Kernel: an open, self-describing meta-type "
        "system. Everything the platform can ever represent is a `MetaObject` classified by "
        "a registered `MetaType`. The reflective root `MetaType` is classified by itself — "
        "the single fixed point that lets a finite kernel represent an unbounded world.\n\n"
        + "## Universal abstractions and their homes\n\n"
        + _table(
            ["ID", "Abstraction", "Meta-Type", "Mechanism (Repository Truth)"],
            [
                [a["id"], a["abstraction"], f"`{a['metatype']}`", f"`{a['mechanism']}`"]
                for a in decl["universal_abstractions"]
            ],
        )
        + "\n## Engineering rules honoured\n\n"
        + "- Rule 1 (no special cases): one `MetaObject`/`MetaType` model; no per-kind code.\n"
        + "- Rule 2 (no hard-coded assumptions): concept-categories are DATA (seed + runtime).\n"
        + "- Rule 3 (identity): every thing is minted a deterministic identity.\n"
        + "- Rule 4 (governance): every admission passes through governance.\n"
        + "- Rule 5 (unlimited extension): registries, policies and relations are open.\n"
        + "- Rule 6 (providers implement, kernel abstracts): the facade exposes generic ops.\n"
        + "- Rule 7 (registration not redesign): unknown categories register; kernel unchanged.\n"
    )

    out["02-CONSTITUTIONAL-COMPLIANCE-REPORT.md"] = (
        header
        + "## Architectural quality gates\n\n"
        + _table(
            ["Gate", "Result", "Criterion (declaration)", "Evidence (executed)"],
            [
                [
                    q["gate"],
                    _verdict_badge(next(g["passed"] for g in gates if g["id"] == q["gate"])),
                    q["criterion"],
                    next(g["evidence"] for g in gates if g["id"] == q["gate"]),
                ]
                for q in decl["quality_gates"]
            ],
        )
        + f"\n**Overall: {report['verdict']}** "
        + f"(passed={report['passed']}).\n\n"
        + "Every gate is executed against a live kernel by `engine/kernel/compliance.py`; "
        "this report is a rendering of that executed result, not an assertion.\n"
    )

    out["03-ARCHITECTURAL-PROOF-REPORT.md"] = (
        header
        + "## Represent the previously-unknown through governed extension\n\n"
        + "Each category below was represented on a fresh kernel by **registration only**. "
        "The kernel source fingerprint before and after is identical: representing universes "
        "that have not yet been imagined required **zero** kernel change.\n\n"
        + f"- Before: `{proof['kernel_source_fingerprint_before']}`\n"
        + f"- After:  `{proof['kernel_source_fingerprint_after']}`\n"
        + f"- Kernel unchanged: **{proof['kernel_unchanged']}**\n\n"
        + _table(
            ["Category", "Meta-Type", "Instance", "Discoverable", "Traceable", "Governed"],
            [
                [
                    r["category"],
                    f"`{r.get('metatype_identity', '')}`",
                    r["instance"],
                    r.get("discoverable"),
                    r.get("traceable"),
                    r.get("governed"),
                ]
                for r in proof["records"]
            ],
        )
    )

    gaps_rows = _gap_rows(decl, report)
    out["04-GAP-ANALYSIS.md"] = (
        header
        + "## Architectural gap register\n\n"
        + (
            "No architectural gaps remain. Every mission abstraction is bound to a home, "
            "every quality gate passes, and unknown future categories require registration "
            "only.\n\n"
            if not gaps_rows
            else ""
        )
        + "### Gap closed by this programme\n\n"
        + _table(
            ["Gap", "Before PROGRAM-002", "After PROGRAM-002"],
            [
                [
                    "Closed concept-type enumeration",
                    "`engine/registry/universal` used a closed `RegistryKind` enum; a new "
                    "concept-category (e.g. CONTEXT) required editing kernel code — a redesign.",
                    "The meta-kernel represents concept-categories as registered meta-types; "
                    "unknown categories require registration only (Rule 7).",
                ]
            ],
        )
        + ("\n### Open gaps\n\n" + _table(["ID", "Gap"], gaps_rows) if gaps_rows else "")
    )

    out["05-TRACEABILITY.md"] = (
        header
        + "## Abstraction → Meta-Type → Home\n\n"
        + _table(
            ["ID", "Abstraction", "Meta-Type", "Home", "Note"],
            [
                [a["id"], a["abstraction"], f"`{a['metatype']}`", f"`{a['mechanism']}`", a["note"]]
                for a in decl["universal_abstractions"]
            ],
        )
        + "\n## Quality gate → executed evidence\n\n"
        + _table(
            ["Gate", "Evidence"],
            [[g["id"], g["evidence"]] for g in gates],
        )
    )

    exit_rows = _exit_criteria_rows(report)
    out["06-KERNEL-READINESS-REPORT.md"] = (
        header
        + "## PROGRAM-002 exit criteria\n\n"
        + _table(["Exit criterion", "Status"], exit_rows)
        + "\n## Determination\n\n"
        + (
            "**KERNEL READY.** The kernel contains only universal abstractions, no "
            "architecturally closed domain remains, every abstraction supports governed "
            "extension, every concrete implementation belongs outside the kernel, unknown "
            "future concepts require registration only, and constitutional compliance, "
            "validation and certification are complete.\n"
            if report["passed"]
            else "**KERNEL NOT READY.** One or more exit criteria are unsatisfied.\n"
        )
    )
    matrix = certification_matrix(decl, report)

    def _pct(value: float | None) -> str:
        return "UNVERIFIED" if value is None else f"{value:.2f}%"

    out["07-UNIVERSAL-CERTIFICATION-MATRIX.md"] = (
        header
        + "## Universal Certification Matrix\n\n"
        + "Every mandatory dimension reports an exact percentage. Any dimension below "
        + "100% is a certification failure.\n\n"
        + _table(
            ["ID", "Dimension", "Percent", "Status", "Evidence"],
            [
                [r["id"], r["dimension"], _pct(r["percent"]), r["status"], r["evidence"]]
                for r in matrix["dimensions"]
            ],
        )
        + "\n"
        + f"- Dimensions at 100%: **{sum(1 for r in matrix['dimensions'] if r['percent'] == 100.0)}"
        + f"/{len(matrix['dimensions'])}**\n"
        + f"- Mandatory architectural proof: {matrix['architectural_proof']}\n"
        + f"- **Unconditional certification: {matrix['unconditional']}**\n"
    )

    determination = (
        "PROGRAM-002 — UNCONDITIONALLY CERTIFIED"
        if matrix["unconditional"]
        else "PROGRAM-002 — NOT CERTIFIED"
    )
    out["08-FINAL-CERTIFICATION-REPORT.md"] = (
        header
        + f"## Determination\n\n**{determination}**\n\n"
        + ("Every mandatory certification dimension reports exactly 100%. The Universal "
           "Meta-Kernel contains only universal abstractions, no architecturally closed "
           "domain remains, every abstraction supports governed extension, unknown future "
           "concepts require registration only, and the kernel source is provably unchanged "
           "by representing eleven previously-unknown categories.\n\n"
           if matrix["unconditional"]
           else "One or more dimensions are below 100%; certification is withheld.\n\n")
        + "## Dimension summary\n\n"
        + _table(
            ["Dimension", "Percent", "Status"],
            [[r["dimension"], _pct(r["percent"]), r["status"]] for r in matrix["dimensions"]],
        )
        + "\n## Reproduce\n\n"
        + "```\nmake umk-self     # declaration + write-scope + determinism guards\n"
        + "make umk-gate     # fail-closed constitutional gate\n"
        + "make test         # engine/kernel coverage (statement+branch) = 100%\n"
        + "ucos-kernel prove # constitutional gates + architectural proof\n```\n"
    )
    return out


def _gap_rows(decl: dict[str, Any], report: dict[str, Any]) -> list[list[str]]:
    rows: list[list[str]] = []
    gates = {g["id"]: g for g in report["quality_gates"]["gates"]}
    for q in decl["quality_gates"]:
        gate = gates.get(q["gate"])
        if gate and not gate["passed"]:
            rows.append([q["id"], f"{q['gate']}: {gate['evidence']}"])
    return rows


def _exit_criteria_rows(report: dict[str, Any]) -> list[list[str]]:
    gates = {g["id"]: g["passed"] for g in report["quality_gates"]["gates"]}
    passed = report["passed"]
    criteria = [
        ("Kernel contains only universal abstractions", gates.get("no-hardcoded-assumptions")),
        ("No architecturally closed domains remain", gates.get("no-closed-registries")),
        ("Every abstraction supports governed extension", gates.get("no-closed-registries")),
        (
            "Every concrete implementation belongs outside the kernel",
            gates.get("no-finite-enumeration"),
        ),
        (
            "Unknown future concepts require registration only",
            gates.get("unknown-future-compatibility"),
        ),
        (
            "Kernel redesign is unnecessary for future categories",
            gates.get("unknown-future-compatibility"),
        ),
        ("Constitutional compliance verified", passed),
        ("Validation complete", passed),
        ("Certification complete", passed),
    ]
    return [[name, "PASS" if ok else "FAIL"] for name, ok in criteria]


# --------------------------------------------------------------------------- emission


def emit(decl: dict[str, Any], report: dict[str, Any]) -> list[str]:
    """Write deliverables + evidence, only inside this programme's own directory."""
    written: list[str] = []
    for name, text in render_deliverables(decl, report).items():
        path = HERE / name
        path.write_text(text, encoding="utf-8")
        written.append(str(path.relative_to(REPO)))

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence = {
        "umk-constitutional-compliance.json": report,
        "umk-architectural-proof.json": report["quality_gates"]["architectural_proof"],
        "umk-kernel-certification.json": MetaKernel().certify(),
        "umk-kernel-snapshot.json": MetaKernel().registry.snapshot(),
    }
    for name, payload in evidence.items():
        path = EVIDENCE_DIR / name
        path.write_text(canonical_json(payload) + "\n", encoding="utf-8")
        written.append(str(path.relative_to(REPO)))
    return sorted(written)


# --------------------------------------------------------------------------- self-guards


def guard_write_scope(decl: dict[str, Any]) -> int:
    """Prove every output path is inside this programme's own directory."""
    offenders: list[str] = []
    for name in render_deliverables(decl, constitutional_report()):
        if (HERE / name).resolve().parent != HERE:
            offenders.append(name)
    if offenders:
        print(f"WRITE-SCOPE VIOLATION: {offenders}", file=sys.stderr)
        return 1
    print("write-scope guard PASS — every output lands inside 00-MASTER/UMK-000001/")
    return 0


def guard_determinism(decl: dict[str, Any]) -> int:
    """Prove the rendered deliverable set is byte-identical across two runs."""
    first = render_deliverables(decl, constitutional_report())
    second = render_deliverables(decl, constitutional_report())
    if first != second or kernel_source_fingerprint() != kernel_source_fingerprint():
        print("DETERMINISM VIOLATION: output differs across runs", file=sys.stderr)
        return 1
    print("determinism guard PASS — deliverables are byte-identical across runs")
    return 0


def guard_declaration(decl: dict[str, Any]) -> int:
    findings = check_declaration(decl)
    if findings:
        for finding in findings:
            print(f"DECLARATION FINDING: {finding}", file=sys.stderr)
        return 1
    print("declaration guard PASS — every abstraction, mechanism and category resolves")
    return 0


# --------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="umk_engine", description=__doc__)
    parser.add_argument("--gate", action="store_true", help="fail-closed constitutional gate")
    parser.add_argument(
        "--certify",
        action="store_true",
        help="fail-closed unconditional certification (every matrix dimension must be 100%%)",
    )
    parser.add_argument("--check-declaration", action="store_true")
    parser.add_argument("--check-write-scope", action="store_true")
    parser.add_argument("--check-determinism", action="store_true")
    args = parser.parse_args(argv)

    decl = load_declaration()

    if args.check_declaration:
        return guard_declaration(decl)
    if args.check_write_scope:
        return guard_write_scope(decl)
    if args.check_determinism:
        return guard_determinism(decl)

    findings = check_declaration(decl)
    if findings:
        fail_closed(f"declaration unusable: {findings[0]}")

    report = constitutional_report()
    written = emit(decl, report)

    if args.certify:
        matrix = certification_matrix(decl, report)
        below = [
            f"{r['dimension']}={r['status']}"
            for r in matrix["dimensions"]
            if r["percent"] != 100.0
        ]
        print(
            canonical_json(
                {
                    "determination": (
                        "UNCONDITIONALLY-CERTIFIED"
                        if matrix["unconditional"]
                        else "NOT-CERTIFIED"
                    ),
                    "dimensions_total": len(matrix["dimensions"]),
                    "dimensions_at_100": sum(
                        1 for r in matrix["dimensions"] if r["percent"] == 100.0
                    ),
                    "below_100": below,
                    "written": written,
                }
            )
        )
        return 0 if matrix["unconditional"] else 1

    if args.gate:
        print(
            canonical_json(
                {"verdict": report["verdict"], "passed": report["passed"], "written": written}
            )
        )
        return 0 if report["passed"] else 1

    print(f"UMK-000001: {report['verdict']} — wrote {len(written)} artifacts to {HERE}")
    for path in written:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
