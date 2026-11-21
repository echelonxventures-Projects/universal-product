#!/usr/bin/env python3
"""IMR-003A-R1 — CIOS Architecture Verification Harness.

Verifies the CIOS declaration against the numeric and structural contract fixed by
CIOS-01 (Article II, III, IV, V, VII.3, X.1). Every assertion this mission makes in
prose is checked here, so that RAC-8 ("every binding assertion is checked by
executable code ... not asserted in prose") is satisfied.

SCOPE AND AUTHORITY BOUNDARY
  This harness validates CIOS's OWN DECLARATION ONLY. It is a self-check under
  IMR-003A AC-4 and CIOS-15 §4 (surface S-C). It is NOT a CEP-004 validation, binds
  no corpus artifact, creates no registry or gate, confers no status, and discharges
  no located gate or finding (VR-10 .. VR-14).

  It is written independently of the located graph validator because UCCEP-F-003
  records that the located validator fails open on a reported cycle (CIOS-06 §4.3).
  A pass here does NOT discharge UCCEP-F-003.

USAGE
  python3 00-MASTER/IMR-003A-R1/r1_verify.py [--json]

EXIT CODES
  0  all checks PASS
  1  one or more checks FAIL
  2  harness could not run (bindings file missing or unparseable)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import deque
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths. Resolved relative to this file so the harness is location-independent.
# ---------------------------------------------------------------------------

R1_DIR = Path(__file__).resolve().parent
MISSION_DIR = R1_DIR.parent / "IMR-003A"
REPO_ROOT = R1_DIR.parent.parent
BINDINGS = MISSION_DIR / "cios-bindings.json"

BASELINE = "b26c5bb66c37717fe4eb96552bad4b9d8b74d890"

# Digests of the two RECOVERED artifacts, captured by IMR-003A-R1 Phase 1.
# RAC-1 requires these be byte-identical before and after the recovery mission.
RECOVERED_DIGESTS = {
    "00-CIOS-MISSION-REGISTRATION-RECORD.md":
        "37d194fd51ed82546d586f1604e1652ce60cc0c5e4f5dce79d7bfd72d6e4f6e7",
    "01-CIOS-CONSTITUTION.md":
        "a0c0dcc00b169c0358aecce36e958c8fa7cb906127c688aaa14798ca9162ea2b",
}

# The 23 declared outputs of IMR-003A OUTPUT 0.3 (1 registration record + 20 numbered
# outputs + cios-bindings.json + README.md index).
DECLARED_OUTPUTS = [
    "00-CIOS-MISSION-REGISTRATION-RECORD.md",
    "01-CIOS-CONSTITUTION.md",
    "02-CIOS-OPERATING-MODEL.md",
    "03-CIOS-ENGINE-ARCHITECTURE.md",
    "04-CIOS-ENGINE-RESPONSIBILITIES.md",
    "05-CIOS-ENGINE-INTERFACES.md",
    "06-CIOS-ENGINE-DEPENDENCIES.md",
    "07-CIOS-LIFECYCLE-MODEL.md",
    "08-CIOS-IDENTITY-MODEL.md",
    "09-CIOS-QUEUE-MODEL.md",
    "10-CIOS-SCHEDULING-MODEL.md",
    "11-CIOS-IMPLEMENTATION-PROTECTION-MODEL.md",
    "12-CIOS-CONTINUOUS-EVOLUTION-MODEL.md",
    "13-CIOS-REPOSITORY-INTEGRATION-MODEL.md",
    "14-CIOS-GOVERNANCE-INTEGRATION-MODEL.md",
    "15-CIOS-VALIDATION-INTEGRATION-MODEL.md",
    "16-CIOS-CERTIFICATION-INTEGRATION-MODEL.md",
    "17-CIOS-TRACEABILITY-MODEL.md",
    "18-CIOS-REPOSITORY-IMPACT-ASSESSMENT.md",
    "19-CIOS-GAP-ANALYSIS.md",
    "20-CIOS-CONSTITUTIONAL-VERIFICATION.md",
    "cios-bindings.json",
    "README.md",
]

# CIOS-01 Article X.1 numeric contract, plus the derived cardinalities.
CARDINALITY_CONTRACT = {
    "planes": 4,
    "partitions": 4,
    "laws": 24,
    "invariants": 12,
    "engines": 24,
    "ports": 48,
    "stages": 24,
    "identity_fields": 22,
    "queues": 4,
    "key_elements": 8,
    "override_authorities": 2,
    "interruption_classes": 10,
    "self_checks": 4,
    "cios_gates": 7,
    "gaps": 14,
    "derives_edges": 25,
}

LOCATED_GATES = [f"G-{n:02d}" for n in range(1, 15)]

# Tokens CIOS-L-22 forbids CIOS from enumerating. Matched case-insensitively as
# whole words. Deliberately excludes words that appear only as prohibitions.
PROHIBITED_ENUMERATIONS = [
    "postgres", "postgresql", "mysql", "mongodb", "sqlite", "redis", "kafka",
    "aws", "azure", "gcp", "kubernetes", "docker", "terraform",
    "python", "javascript", "typescript", "golang", "rust", "java",
    "grpc", "graphql", "protobuf", "yaml", "xml", "rest api",
]


class Report:
    """Accumulates PASS/FAIL results."""

    def __init__(self) -> None:
        self.results: list[dict] = []

    def check(self, cid: str, name: str, ok: bool, detail: str = "") -> bool:
        self.results.append(
            {"id": cid, "check": name, "verdict": "PASS" if ok else "FAIL", "detail": detail}
        )
        return ok

    @property
    def failed(self) -> list[dict]:
        return [r for r in self.results if r["verdict"] == "FAIL"]

    @property
    def passed(self) -> list[dict]:
        return [r for r in self.results if r["verdict"] == "PASS"]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_non_destruction(rep: Report) -> None:
    """RAC-1 — the two recovered artifacts are byte-identical."""
    for name, expected in RECOVERED_DIGESTS.items():
        path = MISSION_DIR / name
        if not path.exists():
            rep.check("V-01", f"non-destruction: {name}", False, "FILE MISSING")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        rep.check(
            "V-01",
            f"non-destruction: {name}",
            actual == expected,
            f"expected {expected[:16]}… got {actual[:16]}…",
        )


def check_register_completeness(rep: Report) -> None:
    """RAC-3 — every declared output of OUTPUT 0.3 exists in its declared slot."""
    missing = [n for n in DECLARED_OUTPUTS if not (MISSION_DIR / n).exists()]
    rep.check(
        "V-02",
        "register completeness (23 declared outputs present)",
        not missing,
        f"missing: {missing}" if missing else f"{len(DECLARED_OUTPUTS)}/{len(DECLARED_OUTPUTS)} present",
    )


def check_structural_integrity(rep: Report) -> None:
    """No truncation, no placeholder; every markdown ARTIFACT carries its terminal marker.

    README.md is exempt from the terminal-marker rule: IMR-003A OUTPUT 0.3 declares it as
    the "Mission index", not as a mission output artifact, so it bears no artifact terminus.
    It is still checked for placeholders.
    """
    marker_exempt = {"README.md"}
    bad_marker, bad_placeholder = [], []
    placeholder = re.compile(r"\b(TODO|TBD|FIXME|PLACEHOLDER)\b")
    for name in DECLARED_OUTPUTS:
        path = MISSION_DIR / name
        if not path.exists() or path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        if name not in marker_exempt and "END OF ARTIFACT" not in text[-2000:]:
            bad_marker.append(name)
        # Strip inline code spans, where these tokens legitimately appear as
        # the subject of a prohibition ("no `TODO`").
        stripped = re.sub(r"`[^`]*`", "", text)
        if placeholder.search(stripped):
            bad_placeholder.append(name)
    rep.check("V-03", "terminal marker present in every artifact (README exempt as index)",
              not bad_marker,
              f"missing marker: {bad_marker}" if bad_marker else "all 21 artifacts marked")
    rep.check("V-04", "no placeholder tokens outside code spans", not bad_placeholder,
              f"placeholders in: {bad_placeholder}" if bad_placeholder else "none")


def check_cardinality(rep: Report, b: dict) -> None:
    """CIOS-01 Art X.1 numeric contract, checked against declared collections."""
    declared = b.get("cardinality", {})
    for key, expected in CARDINALITY_CONTRACT.items():
        got = declared.get(key, {}).get("count")
        rep.check("V-05", f"cardinality declared: {key} = {expected}", got == expected,
                  f"declared {got}")

    actual = {
        "planes": len(b.get("planes", [])),
        "partitions": len(b.get("partitions", [])),
        "laws": len(b.get("laws", [])),
        "invariants": len(b.get("invariants", [])),
        "engines": len(b.get("engines", [])),
        "stages": len(b.get("stages", [])),
        "identity_fields": len(b.get("identity_fields", [])),
        "queues": len(b.get("queues", [])),
        "key_elements": len(b.get("priority_key_vector", [])),
        "override_authorities": len(b.get("override_authorities", [])),
        "interruption_classes": len(b.get("interruption_classes", [])),
        "self_checks": len(b.get("self_checks", [])),
        "cios_gates": len(b.get("cios_gates", [])),
        "gaps": len(b.get("gaps", [])),
        "derives_edges": len(b.get("derives_edges", [])),
    }
    for key, count in actual.items():
        expected = CARDINALITY_CONTRACT[key]
        rep.check("V-06", f"cardinality actual: {key} = {expected}", count == expected,
                  f"found {count}")

    # Ports are derived: 2 per engine.
    engines = b.get("engines", [])
    ports = {e.get("port_in") for e in engines} | {e.get("port_out") for e in engines}
    ports.discard(None)
    rep.check("V-07", "ports actual = 48 (2 per engine, no collision)", len(ports) == 48,
              f"found {len(ports)} distinct ports")


def check_identifier_sequences(rep: Report, b: dict) -> None:
    """Families are contiguous and complete — no gap, no duplicate."""
    specs = [
        ("engines", "id", "CIOS-E-{:02d}", 1, 24),
        ("laws", "id", "CIOS-L-{:02d}", 1, 24),
        ("invariants", "id", "CIOS-INV-{:02d}", 1, 12),
        ("stages", "id", "CIOS-S-{:02d}", 1, 24),
        ("identity_fields", "id", "CIOS-ID-{:02d}", 1, 22),
        ("interruption_classes", "id", "CIOS-IC-{:02d}", 1, 10),
        ("cios_gates", "id", "CIOS-G-{:02d}", 1, 7),
        ("gaps", "id", "CIOS-GAP-{:02d}", 1, 14),
    ]
    for key, field, pattern, lo, hi in specs:
        got = [item.get(field) for item in b.get(key, [])]
        expected = [pattern.format(i) for i in range(lo, hi + 1)]
        rep.check("V-08", f"{key} identifiers contiguous {pattern.format(lo)}..{pattern.format(hi)}",
                  got == expected,
                  f"mismatch at {[g for g, e in zip(got, expected) if g != e][:3]}"
                  if got != expected else "contiguous")


def check_port_convention(rep: Report, b: dict) -> None:
    """CIOS-05: engine nn holds inbound CIOS-P-(2n-1) and outbound CIOS-P-(2n)."""
    bad = []
    for e in b.get("engines", []):
        n = int(e["id"].split("-")[-1])
        if e.get("port_in") != f"CIOS-P-{2 * n - 1:02d}" or e.get("port_out") != f"CIOS-P-{2 * n:02d}":
            bad.append(e["id"])
    rep.check("V-09", "port convention: E-nn -> P-(2n-1) in, P-(2n) out", not bad,
              f"violations: {bad}" if bad else "all 24 conform")


def check_law_enforcers(rep: Report, b: dict) -> None:
    """CIOS-01 Art II: a law naming no located enforcer is itself a finding."""
    bad = [law["id"] for law in b.get("laws", []) if not law.get("located_enforcer")]
    rep.check("V-10", "every law names a located enforcer", not bad,
              f"laws without enforcer: {bad}" if bad else "24/24 name one")


def check_engine_binding_classes(rep: Report, b: dict) -> None:
    """Every engine is BOUND, COMPOSING (with an Art VII.3 citation), or ABSENT."""
    engines = b.get("engines", [])
    valid = {"BOUND", "COMPOSING", "ABSENT"}
    bad_class = [e["id"] for e in engines if e.get("class") not in valid]
    rep.check("V-11", "every engine has a valid binding class", not bad_class,
              f"invalid: {bad_class}" if bad_class else "all valid")

    composing_no_cite = [
        e["id"] for e in engines if e.get("class") == "COMPOSING" and not e.get("vii3_row")
    ]
    rep.check("V-12", "no COMPOSING engine lacks an Art VII.3 citation", not composing_no_cite,
              f"uncited: {composing_no_cite}" if composing_no_cite else "all cited")

    no_owner = [
        e["id"] for e in engines
        if e.get("class") in {"BOUND", "COMPOSING"} and not e.get("located_owner")
    ]
    rep.check("V-13", "every bound/composing engine names a located owner", not no_owner,
              f"ownerless: {no_owner}" if no_owner else "all owned")

    absent = [e["id"] for e in engines if e.get("class") == "ABSENT"]
    rep.check("V-14", "engines recorded ABSENT = 0", not absent,
              f"absent: {absent}" if absent else "0")

    # Every Art VII.3 row is accounted for: claimed by an engine or explicitly discharged.
    rows = b.get("vii3_contributions", [])
    rep.check("V-15", "Art VII.3 has exactly 9 contribution rows", len(rows) == 9,
              f"found {len(rows)}")
    unaccounted = [
        r["row"] for r in rows if not r.get("claimed_by") and not r.get("discharged_by")
    ]
    rep.check("V-16", "every Art VII.3 row is claimed or explicitly discharged", not unaccounted,
              f"unaccounted: {unaccounted}" if unaccounted else "all 9 accounted")

    # Cross-check: every vii3_row cited by an engine is a real row.
    real = {r["row"] for r in rows}
    bogus = sorted({e["vii3_row"] for e in engines if e.get("vii3_row")} - real)
    rep.check("V-17", "no engine cites a non-existent Art VII.3 row", not bogus,
              f"bogus: {bogus}" if bogus else "all citations valid")


def check_plane_assignment(rep: Report, b: dict) -> None:
    """Every engine belongs to exactly one declared plane; plane counts reconcile."""
    plane_ids = {p["id"] for p in b.get("planes", [])}
    engines = b.get("engines", [])
    bad = [e["id"] for e in engines if e.get("plane") not in plane_ids]
    rep.check("V-18", "every engine is assigned to a declared plane", not bad,
              f"bad assignment: {bad}" if bad else "all 24 assigned")

    for p in b.get("planes", []):
        declared = p.get("engines")
        actual = sum(1 for e in engines if e.get("plane") == p["id"])
        rep.check("V-19", f"plane engine count reconciles: {p['id']} = {declared}",
                  declared == actual, f"declared {declared}, found {actual}")


def check_single_writer(rep: Report, b: dict) -> None:
    """CIOS-INV-02 / CIOS-02 §4.3 — every mutable target has at most one writer."""
    writers = b.get("write_scope_writers", {})
    multi = {t: w for t, w in writers.items() if len(w) > 1}
    rep.check("V-20", "single-writer property holds for every target", not multi,
              f"multi-writer: {multi}" if multi else "all targets have <=1 writer")

    rep.check("V-21", "PLAN[n] (active epoch) has zero writers",
              writers.get("PLAN[n]") == [], f"got {writers.get('PLAN[n]')}")
    rep.check("V-22", "located corpus artifacts have zero writers",
              writers.get("located_corpus_artifacts") == [],
              f"got {writers.get('located_corpus_artifacts')}")

    obs = next((p for p in b.get("planes", []) if p["id"] == "CIOS-PL-D"), {})
    scope = set(obs.get("write_scope", []))
    forbidden = scope - {"findings_channel", "own_operational_memory"}
    rep.check("V-23", "observation plane writes nothing but findings", not forbidden,
              f"unexpected scope: {sorted(forbidden)}" if forbidden else "findings only")


def check_acyclicity(rep: Report, b: dict) -> tuple[bool, dict]:
    """CIOS-INV-05 — Kahn topological sort over the DERIVES edge set."""
    engines = [e["id"] for e in b.get("engines", [])]
    edges = [tuple(e) for e in b.get("derives_edges", [])]

    unknown = sorted({n for edge in edges for n in edge} - set(engines))
    rep.check("V-24", "every edge endpoint is a declared engine", not unknown,
              f"unknown nodes: {unknown}" if unknown else "all endpoints valid")

    self_loops = [e for e in edges if e[0] == e[1]]
    rep.check("V-25", "no self-loops", not self_loops, f"{self_loops}" if self_loops else "0")

    dupes = sorted({e for e in edges if edges.count(e) > 1})
    rep.check("V-26", "no duplicate edges", not dupes, f"{dupes}" if dupes else "0")

    indeg = {n: 0 for n in engines}
    adj: dict[str, list[str]] = {n: [] for n in engines}
    for src, dst in edges:
        if src in adj and dst in indeg:
            adj[src].append(dst)
            indeg[dst] += 1

    queue = deque(sorted(n for n, d in indeg.items() if d == 0))
    order, layer_of = [], {}
    working = dict(indeg)
    while queue:
        node = queue.popleft()
        order.append(node)
        layer_of[node] = max(
            (layer_of[s] + 1 for s, ds in adj.items() if node in ds and s in layer_of),
            default=0,
        )
        for nxt in sorted(adj[node]):
            working[nxt] -= 1
            if working[nxt] == 0:
                queue.append(nxt)

    residual = sorted(set(engines) - set(order))
    acyclic = not residual
    rep.check("V-27", "DERIVES graph is acyclic (Kahn: no residual nodes)", acyclic,
              f"residual (in a cycle): {residual}" if residual else
              f"topologically sorted all {len(order)} nodes")

    # Every edge must run strictly low->high layer.
    violations = [
        f"{s}->{d}" for s, d in edges
        if s in layer_of and d in layer_of and layer_of[s] >= layer_of[d]
    ]
    rep.check("V-28", "every DERIVES edge runs strictly lower->higher layer", not violations,
              f"violations: {violations}" if violations else "all 25 monotone")

    sources = sorted(n for n, d in indeg.items() if d == 0)
    sinks = sorted(n for n in engines if not adj[n])
    props = b.get("graph_properties", {})
    dscope = props.get("derives_scoped", {})
    cscope = props.get("combined_scoped", {})

    rep.check("V-29", "DERIVES-scoped source nodes match declaration",
              sources == sorted(dscope.get("source_nodes", [])),
              f"computed {sources}, declared {dscope.get('source_nodes')}")
    rep.check("V-30", "DERIVES-scoped sink nodes match declaration",
              sinks == sorted(dscope.get("sink_nodes", [])),
              f"computed {sinks}, declared {dscope.get('sink_nodes')}")

    isolated = sorted(n for n in engines if indeg[n] == 0 and not adj[n])
    rep.check("V-30b", "DERIVES-scoped isolated nodes match declaration",
              isolated == sorted(dscope.get("isolated_nodes", [])),
              f"computed {isolated}, declared {dscope.get('isolated_nodes')}")

    layers = max(layer_of.values()) + 1 if layer_of else 0
    rep.check("V-31", "DERIVES-scoped topological layer count matches declaration",
              layers == dscope.get("topological_layers"),
              f"computed {layers}, declared {dscope.get('topological_layers')}")

    # Combined scope: DERIVES + OBSERVES. Every non-observer feeds every observer.
    observers = list(b.get("observes_sinks", []))
    c_adj = {n: list(adj[n]) for n in engines}
    c_indeg = dict(indeg)
    for n in engines:
        if n in observers:
            continue
        for obs in observers:
            c_adj[n].append(obs)
            c_indeg[obs] += 1
    c_sources = sorted(n for n, d in c_indeg.items() if d == 0)
    c_sinks = sorted(n for n in engines if not c_adj[n])
    rep.check("V-31b", "combined-scoped source nodes match declaration",
              c_sources == sorted(cscope.get("source_nodes", [])),
              f"computed {c_sources}, declared {cscope.get('source_nodes')}")
    rep.check("V-31c", "combined-scoped sink nodes match declaration",
              c_sinks == sorted(cscope.get("sink_nodes", [])),
              f"computed {c_sinks}, declared {cscope.get('sink_nodes')}")
    rep.check("V-31d", "combined-scoped observes edge count matches declaration",
              sum(1 for n in engines if n not in observers) * len(observers)
              == props.get("observes_edges"),
              f"computed {sum(1 for n in engines if n not in observers) * len(observers)}, "
              f"declared {props.get('observes_edges')}")

    # Observation engines must be sinks: out-degree 0 (CIOS-06 §4.2).
    non_sink_obs = [n for n in observers if c_adj.get(n)]
    rep.check("V-32", "observation engines have out-degree 0 in both scopes", not non_sink_obs,
              f"non-sinks: {non_sink_obs}" if non_sink_obs else "all sinks")

    return acyclic, {"order": order, "layers": layers, "sources": sources, "sinks": sinks}


def check_stage_bindings(rep: Report, b: dict) -> None:
    """CIOS-07 — stages bind to real engines; every located gate is bound; none bypassed."""
    engine_ids = {e["id"] for e in b.get("engines", [])}
    stages = b.get("stages", [])

    bad_engine = [s["id"] for s in stages if s.get("engine") not in engine_ids]
    rep.check("V-33", "every stage names a declared engine", not bad_engine,
              f"bad: {bad_engine}" if bad_engine else "all 24 valid")

    no_verdict = [s["id"] for s in stages if not s.get("on_failure")]
    rep.check("V-34", "every stage declares fail-closed behaviour", not no_verdict,
              f"missing: {no_verdict}" if no_verdict else "24/24 declared")

    ungated = [
        s["id"] for s in stages
        if not s.get("located_gate") and not s.get("self_check") and s["id"] != "CIOS-S-01"
    ]
    rep.check("V-35", "every stage except S-01 is gated or self-checked", not ungated,
              f"ungated: {ungated}" if ungated else "all gated")

    coverage = b.get("located_gate_coverage", {})
    unbound = [g for g in LOCATED_GATES if not coverage.get(g)]
    rep.check("V-36", "all 14 located gates are bound", not unbound,
              f"unbound: {unbound}" if unbound else "14/14 bound")

    # Gate coverage must reference real stages or the located execution interval.
    stage_ids = {s["id"] for s in stages}
    bogus = sorted({
        t for targets in coverage.values() for t in targets
        if t not in stage_ids and t != "located_execution_interval"
    })
    rep.check("V-37", "gate coverage references only real stages", not bogus,
              f"bogus targets: {bogus}" if bogus else "all valid")

    interval = b.get("located_execution_interval", {})
    rep.check("V-38", "zero CIOS stages inside the located execution interval",
              interval.get("cios_stages_declared_inside") == 0,
              f"declared {interval.get('cios_stages_declared_inside')}")

    partitions = {p["id"] for p in b.get("partitions", [])}
    bad_part = [s["id"] for s in stages if s.get("partition") not in partitions]
    rep.check("V-39", "every stage maps to a declared partition", not bad_part,
              f"bad: {bad_part}" if bad_part else "all valid")


def check_identity_model(rep: Report, b: dict) -> None:
    """CIOS-08 — AIF-L01 bifurcation; CIOS mints nothing outside its three fields."""
    fields = b.get("identity_fields", [])
    valid = {"RECORDED-immutable", "RECORDED-append-sequence", "RECORDED-bind-once", "DERIVED"}
    bad = [f["id"] for f in fields if f.get("class") not in valid]
    rep.check("V-40", "every identity field has a valid RECORDED/DERIVED class", not bad,
              f"invalid: {bad}" if bad else "all valid")

    derived = [f["id"] for f in fields if f.get("class") == "DERIVED"]
    rep.check("V-41", "exactly one DERIVED field (AIF-L01 bifurcation)", len(derived) == 1,
              f"derived: {derived}")

    recorded_and_derived = [
        f["id"] for f in fields
        if f.get("class") == "DERIVED" and f.get("recorded_as_truth") is True
    ]
    rep.check("V-42", "no field is both RECORDED and DERIVED", not recorded_and_derived,
              f"violations: {recorded_and_derived}" if recorded_and_derived else "0")

    cios_minted = sorted(f["id"] for f in fields if f.get("minted_by_cios") is True)
    rep.check("V-43", "CIOS produces exactly ID-18, ID-19, ID-20",
              cios_minted == ["CIOS-ID-18", "CIOS-ID-19", "CIOS-ID-20"], f"got {cios_minted}")

    no_authority = [f["id"] for f in fields if not f.get("authority")]
    rep.check("V-44", "every identity field names a minting/resolving authority", not no_authority,
              f"missing: {no_authority}" if no_authority else "22/22 named")

    stage_ids = {s["id"] for s in b.get("stages", [])}
    bad_stage = [f["id"] for f in fields if f.get("resolved_at") not in stage_ids]
    rep.check("V-45", "every identity field resolves at a declared stage", not bad_stage,
              f"bad: {bad_stage}" if bad_stage else "all valid")


def check_key_vector(rep: Report, b: dict) -> None:
    """CIOS-10 — located-order preservation and totality."""
    vec = b.get("priority_key_vector", [])
    ranks = [k.get("rank") for k in vec]
    rep.check("V-46", "key vector ranks are 1..8 contiguous", ranks == list(range(1, 9)),
              f"got {ranks}")

    leading = [k.get("element") for k in vec[:3]]
    rep.check("V-47", "ranks 1-3 preserve the located order (wave, family, located id)",
              leading == ["wave", "family", "located id"], f"got {leading}")
    rep.check("V-48", "ranks 1-3 are locked", all(k.get("locked") for k in vec[:3]),
              "locked" if all(k.get("locked") for k in vec[:3]) else "NOT locked")

    terminator = vec[-1] if vec else {}
    rep.check("V-49", "rank 8 terminator is the witnessed admission ordinal",
              terminator.get("element") == "witnessed admission ordinal"
              and terminator.get("locked") is True,
              f"got {terminator.get('element')}, locked={terminator.get('locked')}")

    # Totality depends on the ordinal being the declared ordering authority.
    ordinal = next(
        (f for f in b.get("identity_fields", []) if f.get("is_ordering_authority")), None
    )
    rep.check("V-50", "ordering authority is CIOS-ID-06 (not a timestamp)",
              ordinal is not None and ordinal["id"] == "CIOS-ID-06",
              f"got {ordinal['id'] if ordinal else None}")


def check_wave_preservation(rep: Report, b: dict) -> None:
    """CIOS-10 §3 — the located wave partition is preserved exactly."""
    w = b.get("wave_successor_function", {})
    rep.check("V-51", "located wave partition not altered",
              w.get("altered_located_partition") is False,
              f"altered={w.get('altered_located_partition')}")
    rep.check("V-52", "located wave counts preserved (20/15/32/11/12)",
              w.get("located_counts") == {"W1": 20, "W2": 15, "W3": 32, "W4": 11, "W5": 12},
              f"got {w.get('located_counts')}")
    rep.check("V-53", "located effective implementable total = 77",
              (w.get("located_effective_implementable") or {}).get("total") == 77,
              f"got {(w.get('located_effective_implementable') or {}).get('total')}")
    rep.check("V-54", "no terminal wave (CIOS-L-01 perpetual operation)",
              w.get("terminal_wave") is None, f"got {w.get('terminal_wave')}")


def check_unboundedness(rep: Report, b: dict) -> None:
    """CIOS-L-24 — no queue declares a capacity bound."""
    bounded = [q["id"] for q in b.get("queues", []) if q.get("bounded") is not False]
    rep.check("V-55", "no queue declares a capacity bound", not bounded,
              f"bounded: {bounded}" if bounded else "all unbounded")

    props = b.get("graph_properties", {})
    rep.check("V-56", "zero back-edges into CIOS-PL-A (basis of CIOS-L-04)",
              props.get("back_edges_into_PL_A") == 0,
              f"got {props.get('back_edges_into_PL_A')}")


def check_override_model(rep: Report, b: dict) -> None:
    """CIOS-L-21 — exactly two located override authorities; neither created by CIOS."""
    auths = b.get("override_authorities", [])
    rep.check("V-57", "exactly two override authorities", len(auths) == 2, f"found {len(auths)}")

    self_created = [a["id"] for a in auths if a.get("created_by_cios") is not False]
    rep.check("V-58", "no override authority is created by CIOS", not self_created,
              f"self-created: {self_created}" if self_created else "both located")

    no_evidence = [a["id"] for a in auths if not a.get("evidence_required")]
    rep.check("V-59", "every override authority requires evidence", not no_evidence,
              f"missing: {no_evidence}" if no_evidence else "both require evidence")

    q = b.get("quiesce_protocol", {})
    rep.check("V-60", "quiesce drains rather than interrupts (QP-4)",
              q.get("drains_rather_than_interrupts") is True, f"got {q.get('drains_rather_than_interrupts')}")
    rep.check("V-61", "quiesce is not invocable for routine operation",
              q.get("invocable_for_routine_operation") is False,
              f"got {q.get('invocable_for_routine_operation')}")

    rejects = [c["id"] for c in b.get("interruption_classes", []) if c.get("verdict") != "REJECT"]
    rep.check("V-62", "all interruption classes reject by default", not rejects,
              f"non-rejecting: {rejects}" if rejects else "10/10 reject")


def check_authority_neutrality(rep: Report, b: dict) -> None:
    """CIOS-INV-12 and the compliance posture — CIOS owns nothing it must not."""
    c = b.get("compliance", {})
    zero_required = [
        "engines_absent", "engines_claiming_own_authority", "engines_minting_identity",
        "engines_dispatching", "engines_acting_as_gate",
        "composing_engines_without_vii3_citation", "duplicate_responsibilities",
        "unresolved_overlaps", "laws_without_located_enforcer", "located_gates_bypassed",
        "cios_concerns_owned", "cios_registries_created", "parallel_identifier_systems_created",
        "gates_discharged_by_cios", "findings_discharged_by_cios", "prohibited_enumerations",
    ]
    for key in zero_required:
        rep.check("V-63", f"compliance: {key} = 0", c.get(key) == 0, f"declared {c.get(key)}")

    rep.check("V-64", "compliance: 14 located gates bound", c.get("located_gates_bound") == 14,
              f"declared {c.get('located_gates_bound')}")
    rep.check("V-65", "CIOS identifiers are not corpus identifiers",
              c.get("cios_identifier_families_are_corpus_identifiers") is False,
              f"declared {c.get('cios_identifier_families_are_corpus_identifiers')}")

    p = b.get("programme", {})
    rep.check("V-66", "supremacy is not conferred", p.get("supremacy_conferred") is False,
              f"declared {p.get('supremacy_conferred')}")
    rep.check("V-67", "supremacy deferred behind CIOS-G-01 and CIOS-G-02",
              sorted(p.get("supremacy_deferred_behind", [])) == ["CIOS-G-01", "CIOS-G-02"],
              f"declared {p.get('supremacy_deferred_behind')}")
    rep.check("V-68", "corpus identity consumed = false",
              p.get("corpus_identity_consumed") is False,
              f"declared {p.get('corpus_identity_consumed')}")


def check_freeze_legality(rep: Report, b: dict) -> None:
    """RAC-7 / GD-10-C1 — no freeze is declared, implied or recorded."""
    f = b.get("freeze_status", {})
    for key in ("cep007_freeze_declared", "freeze_baseline_declared",
                "freeze_authorization_declared", "freeze_eligible",
                "is_constitutional_freeze"):
        rep.check("V-69", f"freeze legality: {key} = false", f.get(key) is False,
                  f"declared {f.get(key)}")

    rep.check("V-70", "freeze ineligibility limbs recorded (>=3)",
              len(f.get("freeze_ineligibility_limbs", [])) >= 3,
              f"{len(f.get('freeze_ineligibility_limbs', []))} limbs")

    sealed = next((p for p in b.get("partitions", []) if p["id"] == "CIOS-PT-01"), {})
    rep.check("V-71", "CIOS-PT-01 declared NOT a CEP-007 freeze state",
              sealed.get("is_cep007_freeze_state") is False,
              f"declared {sealed.get('is_cep007_freeze_state')}")

    wc = b.get("write_confinement", {})
    rep.check("V-72", "freeze registry entries added = 0",
              wc.get("freeze_registry_entries_added") == 0,
              f"declared {wc.get('freeze_registry_entries_added')}")


def check_write_confinement(rep: Report, b: dict) -> None:
    """AC-9 — zero corpus mutation, zero registration drift."""
    wc = b.get("write_confinement", {})
    for key in ("corpus_artifacts_modified", "registries_written", "registries_created",
                "registry_entries_added", "corpus_identifiers_consumed",
                "id_ledger_entries_created", "registration_drift_introduced",
                "frozen_surfaces_accessed", "closure_json_writes"):
        rep.check("V-73", f"write confinement: {key} = 0", wc.get(key) == 0,
                  f"declared {wc.get(key)}")

    zones = wc.get("writable_zones", [])
    rep.check("V-74", "writable zones are the two mission homes only",
              zones == ["00-MASTER/IMR-003A/", "00-MASTER/IMR-003A-R1/"], f"declared {zones}")
    rep.check("V-75", "mission home is registration-excluded",
              wc.get("registration_excluded") is True, f"declared {wc.get('registration_excluded')}")


def check_gaps_and_gates(rep: Report, b: dict) -> None:
    """CIOS-01 Art X.1 limb 8 — every gap and gate names an owner."""
    gaps = b.get("gaps", [])
    no_owner = [g["id"] for g in gaps if not g.get("owner")]
    rep.check("V-76", "every gap names an owner", not no_owner,
              f"ownerless: {no_owner}" if no_owner else f"{len(gaps)}/{len(gaps)} named")

    no_unblock = [g["id"] for g in gaps if not g.get("unblocking_condition")]
    rep.check("V-77", "every gap names an unblocking condition", not no_unblock,
              f"missing: {no_unblock}" if no_unblock else "all named")

    gates = b.get("cios_gates", [])
    bad_gate = [g["id"] for g in gates
                if not g.get("owner") or not g.get("unblocking_condition")]
    rep.check("V-78", "every CIOS gate names an owner and unblocking condition", not bad_gate,
              f"incomplete: {bad_gate}" if bad_gate else f"{len(gates)}/{len(gates)} complete")

    discharged = [g["id"] for g in gates if g.get("status") != "OPEN"]
    rep.check("V-79", "no CIOS gate is claimed discharged", not discharged,
              f"claimed discharged: {discharged}" if discharged else "all 7 OPEN")

    findings = b.get("inherited_findings", [])
    rep.check("V-80", "nine inherited findings recorded as bounds", len(findings) == 9,
              f"found {len(findings)}")


def check_located_references(rep: Report, b: dict) -> None:
    """CIOS-INV-11 — every located path CIOS cites resolves at the baseline."""
    dangling = []
    for binding in b.get("located_bindings", []):
        path = binding.get("path")
        if path and not (REPO_ROOT / path).exists():
            dangling.append(path)
    rep.check("V-81", "every located binding path resolves", not dangling,
              f"dangling: {dangling}" if dangling else
              f"{len(b.get('located_bindings', []))}/{len(b.get('located_bindings', []))} resolve")

    copied = [x.get("path") for x in b.get("located_bindings", []) if x.get("copied") is not False]
    rep.check("V-82", "no located binding is copied or restated", not copied,
              f"copied: {copied}" if copied else "pointers only")


def check_repository_truth(rep: Report, b: dict) -> None:
    """Repository Truth is read, not written, and its values are unchanged."""
    rt = b.get("repository_truth", {})
    closure = REPO_ROOT / rt.get("source", "")
    if not closure.exists():
        rep.check("V-83", "Repository Truth source resolves", False, f"missing {rt.get('source')}")
        return
    rep.check("V-83", "Repository Truth source resolves", True, str(rt.get("source")))

    data = json.loads(closure.read_text(encoding="utf-8"))
    rep.check("V-84", "closure determination = CLOSED",
              data.get("determination") == rt.get("determination") == "CLOSED",
              f"actual {data.get('determination')}")
    rep.check("V-85", "closure concept_total = 434",
              data.get("concept_total") == rt.get("concept_total") == 434,
              f"actual {data.get('concept_total')}")
    rep.check("V-86", "closure gap_total = 0",
              data.get("gap_total") == rt.get("gap_total") == 0,
              f"actual {data.get('gap_total')}")
    gaps = data.get("gaps", {})
    rep.check("V-87", "all seven closure gap classes are zero",
              bool(gaps) and all(v == 0 for v in gaps.values()),
              f"actual {gaps}")
    rep.check("V-88", "CIOS does not write or regenerate Repository Truth",
              rt.get("written_by_cios") is False and rt.get("regenerated_by_cios") is False,
              f"written={rt.get('written_by_cios')} regenerated={rt.get('regenerated_by_cios')}")


def check_zero_enumeration(rep: Report, b: dict) -> None:
    """CIOS-L-22 — the CIOS corpus enumerates no technology, vendor, platform or format."""
    hits: dict[str, list[str]] = {}
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(t) for t in PROHIBITED_ENUMERATIONS) + r")\b",
        re.IGNORECASE,
    )
    for name in DECLARED_OUTPUTS:
        path = MISSION_DIR / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        found = sorted({m.group(0).lower() for m in pattern.finditer(text)})
        if found:
            hits[name] = found
    rep.check("V-89", "zero prohibited enumerations in the CIOS corpus", not hits,
              f"hits: {hits}" if hits else f"scanned {len(DECLARED_OUTPUTS)} artifacts, 0 hits")


def check_baseline(rep: Report, b: dict) -> None:
    """The declared baseline matches the recovery baseline; no re-baselining occurred."""
    p = b.get("programme", {})
    rep.check("V-90", "declared baseline matches the IMR-003A baseline",
              p.get("baseline_commit") == BASELINE, f"declared {p.get('baseline_commit')}")
    rep.check("V-91", "standing is PROVISIONAL", p.get("standing") == "PROVISIONAL",
              f"declared {p.get('standing')}")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="IMR-003A-R1 CIOS architecture verification")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args()

    if not BINDINGS.exists():
        print(f"HARNESS ERROR: bindings not found at {BINDINGS}", file=sys.stderr)
        return 2
    try:
        bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"HARNESS ERROR: cios-bindings.json is not valid JSON: {exc}", file=sys.stderr)
        return 2

    rep = Report()

    check_non_destruction(rep)
    check_register_completeness(rep)
    check_structural_integrity(rep)
    check_cardinality(rep, bindings)
    check_identifier_sequences(rep, bindings)
    check_port_convention(rep, bindings)
    check_law_enforcers(rep, bindings)
    check_engine_binding_classes(rep, bindings)
    check_plane_assignment(rep, bindings)
    check_single_writer(rep, bindings)
    check_acyclicity(rep, bindings)
    check_stage_bindings(rep, bindings)
    check_identity_model(rep, bindings)
    check_key_vector(rep, bindings)
    check_wave_preservation(rep, bindings)
    check_unboundedness(rep, bindings)
    check_override_model(rep, bindings)
    check_authority_neutrality(rep, bindings)
    check_freeze_legality(rep, bindings)
    check_write_confinement(rep, bindings)
    check_gaps_and_gates(rep, bindings)
    check_located_references(rep, bindings)
    check_repository_truth(rep, bindings)
    check_zero_enumeration(rep, bindings)
    check_baseline(rep, bindings)

    ok = not rep.failed

    if args.json:
        print(json.dumps({
            "mission": "IMR-003A-R1",
            "subject": "CIOS architecture verification",
            "baseline": BASELINE,
            "scope": "CIOS's own declaration only (AC-4 self-check; not a CEP-004 validation)",
            "total": len(rep.results),
            "passed": len(rep.passed),
            "failed": len(rep.failed),
            "verdict": "PASS" if ok else "FAIL",
            "results": rep.results,
        }, indent=2))
    else:
        print("=" * 78)
        print("IMR-003A-R1 — CIOS ARCHITECTURE VERIFICATION")
        print(f"baseline {BASELINE[:7]} | scope: CIOS's own declaration (AC-4 self-check)")
        print("=" * 78)
        for r in rep.results:
            mark = "PASS" if r["verdict"] == "PASS" else "FAIL"
            print(f"[{mark}] {r['id']:<6} {r['check']}")
            if r["verdict"] == "FAIL" and r["detail"]:
                print(f"         -> {r['detail']}")
        print("-" * 78)
        print(f"TOTAL {len(rep.results)}  PASS {len(rep.passed)}  FAIL {len(rep.failed)}")
        print(f"VERDICT: {'PASS' if ok else 'FAIL'}")
        print("-" * 78)
        print("This harness validates CIOS's own declaration. It is NOT a CEP-004")
        print("validation, confers no status, and discharges no located gate or")
        print("finding. UCCEP-F-003 remains open; CIOS-INV-05 is proven here for")
        print("CIOS's graph only, not machine-enforced corpus-wide.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
