#!/usr/bin/env python3
"""URRC-000001 — Repository Reality & Constitutional Completion engine.

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing, ratifies nothing,
freezes no architecture and owns no concern. It is the executable expression of the
programme charter: it reads a single DATA declaration (``urrc-bindings.json``) that binds
each chartered deliverable either to the canonical owner that already holds it, to a
derivation over declared machine-readable substrate, or to a counted probe of verified
absence — and then computes, never asserts, the reuse, duplication, conflict, gap,
completeness, readiness and automation verdicts.

    python3 00-MASTER/URRC-000001/urrc_engine.py                 # regenerate + report
    python3 00-MASTER/URRC-000001/urrc_engine.py --gate           # fail-closed
    python3 00-MASTER/URRC-000001/urrc_engine.py --check-declaration
    python3 00-MASTER/URRC-000001/urrc_engine.py --check-no-enumeration
    python3 00-MASTER/URRC-000001/urrc_engine.py --check-write-scope
    python3 00-MASTER/URRC-000001/urrc_engine.py --check-determinism
    python3 00-MASTER/URRC-000001/urrc_engine.py --check-substrate
    python3 00-MASTER/URRC-000001/urrc_engine.py --check-no-fabrication
    python3 00-MASTER/URRC-000001/urrc_engine.py --check-reuse-before-create
    python3 00-MASTER/URRC-000001/urrc_engine.py --check-law-namespace

Exit semantics of --gate:
    0  every blocking gate passed
    1  a blocking gate failed
    2  fail-closed abort — the declaration or a required substrate is unusable, so no
       verdict may be asserted

The engine contains no deliverable name, no declared identifier, no binding-mode name and
no substrate path as a literal; the charter is DATA and a self-check proves it. Extending
the programme — a deliverable, matrix, gate, substrate, derivation or mode — is an edit to
the declaration and needs no code change.

Stdlib only. No network. No timestamp is emitted anywhere, so the rendered output set is
byte-identical for an unchanged repository state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "urrc-bindings.json"
EVIDENCE_DIR = HERE / "evidence"
EVIDENCE_INDEX = "urrc-substrate-index.json"
MODEL_FILE = "urrc.json"

# Keys an entry of each declared list-section may carry. A key outside its allowed set is
# a fail-closed violation: it prevents a new obligation, a hidden assumption or an unbound
# claim from being smuggled in through a new field. The section names are engine
# vocabulary; their contents are DATA.
ALLOWED_KEYS: dict[str, set[str]] = {
    "modes": {
        "id",
        "mode",
        "definition",
        "is_reuse",
        "requires_owner",
        "requires_derivation",
        "is_unknown",
    },
    "substrate": {"id", "path", "kind", "required", "pointers", "purpose"},
    "derivations": {"id", "primitive", "purpose", "args"},
    "deliverables": {
        "index",
        "id",
        "name",
        "subject",
        "mode",
        "canonical_owner",
        "derivations",
        "matrix",
        "generator_class",
        "note",
    },
    "matrices": {"id", "name", "subject", "computable"},
    "gates": {"id", "name", "blocking", "matrices", "criterion"},
    "outputs": {"id", "file", "title", "purpose", "matrices", "derivations", "deliverables"},
    "non_derivable": {
        "id",
        "fact",
        "reason",
        "required_evidence_class",
        "probe",
        "owner",
        "bounds",
    },
    "work_packages": {
        "id",
        "title",
        "owner",
        "route",
        "authorization_required",
        "discharges",
        "acceptance",
    },
    "references": {"id", "path", "purpose"},
}

# Programme fields that must name a located artefact. A reuse claim over an unresolvable
# reference is an empty claim.
PROGRAMME_REFERENCE_KEYS = (
    "governing_instrument",
    "evolution_owner",
    "operational_memory_owner",
    "registration_owner",
    "aggregate_gate_owner",
    "resilience_owner",
    "identity_allocation_owner",
    "identifier_family_owner",
)

PROGRAMME_SCALAR_KEYS = (
    "id",
    "name",
    "version",
    "charter_designation",
    "authority",
    "operational_home",
    "gate_name",
    "gate_clause",
    "determination_pass",
    "determination_fail",
    "disclosure",
    "mission",
    "law_namespace_pattern",
    "roster_binding",
)

# Reference strings may carry human suffixes. A reference resolves by exact path, then by
# glob, then by unique prefix within its parent directory.
_SUFFIX_SPLITS = (" (", " \u00a7", " Art ", " \u00b7 ", " \u2014 ")


# --------------------------------------------------------------------------- helpers


def fail_closed(message: str) -> NoReturn:
    print(f"URRC-000001: FAIL-CLOSED ABORT — {message}", file=sys.stderr)
    raise SystemExit(2)


def load_declaration() -> dict:
    if not DECLARATION.is_file():
        fail_closed(f"declaration absent: {DECLARATION}")
    try:
        return json.loads(DECLARATION.read_text("utf-8"))
    except json.JSONDecodeError as exc:
        fail_closed(f"declaration is not valid JSON: {exc}")


def strip_reference(ref: str) -> str:
    text = ref
    for token in _SUFFIX_SPLITS:
        if token in text:
            text = text.split(token, 1)[0]
    return text.strip()


def resolve_reference(ref: str) -> Path | None:
    """Resolve a declaration reference to a located repository path, or None."""
    bare = strip_reference(ref)
    if not bare:
        return None
    candidate = REPO / bare
    if candidate.exists():
        return candidate
    parent = candidate.parent
    if not parent.is_dir():
        return None
    if "*" in candidate.name or "?" in candidate.name:
        matches = sorted(parent.glob(candidate.name))
        return matches[0] if matches else None
    matches = sorted(child for child in parent.iterdir() if child.name.startswith(candidate.name))
    return matches[0] if matches else None


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest(payload: object) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def git(*args: str) -> str:
    try:
        out = subprocess.run(  # noqa: S603 — fixed argv, no shell, no user input
            ["git", *args],  # noqa: S607 — resolved from PATH by design, as CI does
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        return out.stdout.strip()
    except OSError:
        return ""


def is_tracked(path: str) -> bool:
    return bool(git("ls-files", "--", path))


def repository_state() -> dict:
    """The repository state RECORDED in this programme's emitted determinations.

    Repository Fixed-Point Closure (UCOS-RFP-001 RFP-2 / RFP-3) forbids a tracked
    artifact from embedding the identity of the commit that contains it, and from
    recording an observation of the working tree that contains it. This function
    previously emitted both, and both are non-convergent by construction:

      * a commit's identity is a function of the bytes it contains, so an artifact
        naming its own commit demands a commit whose hash lies inside its own tree;
      * writing "CLEAN, 0 entries" makes the tree dirty, so the value recorded is
        never the value that holds once it has been recorded.

    Neither is lost. Version control already owns the containing commit, and tree
    cleanliness is owned by the gate's exit code — restating either here duplicated
    state the repository already held and put this programme's determinations in
    permanent Evidence Drift. The value below is constant, so regeneration at an
    unchanged tracked tree is byte-identical in every environment and at every
    commit.
    """
    return {
        "anchor": "the containing commit — owned by version control, never restated here",
        "basis": (
            "UCOS-RFP-001 RFP-2 (no commit self-reference) and RFP-3 "
            "(no working-tree self-observation)"
        ),
    }


def table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        rows = [["—"] * len(headers)]
    head = "| " + " | ".join(headers) + " |\n"
    rule = "|" + "|".join(["---"] * len(headers)) + "|\n"
    body = "".join("| " + " | ".join(str(cell) for cell in row) + " |\n" for row in rows)
    return head + rule + body


def as_list(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def section(decl: dict, name: str) -> list[dict]:
    return [entry for entry in decl.get(name, []) if isinstance(entry, dict)]


def ids_of(decl: dict, name: str) -> list[str]:
    return [entry["id"] for entry in section(decl, name) if entry.get("id")]


def navigate(payload: object, pointer: str | None) -> object:
    """Walk a dotted pointer into parsed JSON. Returns None when it does not resolve."""
    if pointer in (None, ""):
        return payload
    current = payload
    for part in str(pointer).split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def size_of(value: object) -> int | None:
    if isinstance(value, list | dict | str):
        return len(value)
    if isinstance(value, int | float) and not isinstance(value, bool):
        return int(value)
    return None


def short(text: object, limit: int = 72) -> str:
    body = str(text).replace("|", "/").replace("\n", " ")
    return body if len(body) <= limit else body[: limit - 1] + "\u2026"


# ------------------------------------------------------------------ substrate loading


class Substrate:
    """The declared machine-readable substrate, loaded once and never mutated."""

    def __init__(self, decl: dict) -> None:
        self.records: dict[str, dict] = {}
        self.payloads: dict[str, object] = {}
        for entry in section(decl, "substrate"):
            ident = entry.get("id") or ""
            rel = entry.get("path") or ""
            path = REPO / rel
            record = {
                "id": ident,
                "path": rel,
                "kind": entry.get("kind") or "",
                "purpose": entry.get("purpose") or "",
                "required": bool(entry.get("required")),
                "exists": path.is_file(),
                "tracked": is_tracked(rel) if rel else False,
                "parses": False,
                "pointers": [str(p) for p in as_list(entry.get("pointers"))],
                "pointers_resolved": [],
                "pointers_unresolved": [],
                "records": 0,
                "content_sha256": "",
            }
            if record["exists"]:
                raw = path.read_bytes()
                record["content_sha256"] = hashlib.sha256(raw).hexdigest()
                try:
                    payload = json.loads(raw.decode("utf-8"))
                    record["parses"] = True
                    self.payloads[ident] = payload
                    total = 0
                    for pointer in record["pointers"]:
                        value = navigate(payload, pointer)
                        if value is None:
                            record["pointers_unresolved"].append(pointer)
                            continue
                        record["pointers_resolved"].append(pointer)
                        measured = size_of(value)
                        if measured is not None:
                            total += measured
                    record["records"] = total
                except (json.JSONDecodeError, UnicodeDecodeError):
                    record["parses"] = False
            self.records[ident] = record

    def payload(self, ident: str) -> object | None:
        return self.payloads.get(ident)

    def findings(self) -> list[str]:
        out: list[str] = []
        for record in self.records.values():
            if not record["required"]:
                continue
            if not record["exists"]:
                out.append(f"{record['id']}: required substrate absent: {record['path']}")
                continue
            if not record["tracked"]:
                out.append(
                    f"{record['id']}: required substrate is not in version control, so it is "
                    f"not Repository Truth: {record['path']}"
                )
            if not record["parses"]:
                out.append(f"{record['id']}: required substrate does not parse: {record['path']}")
                continue
            for pointer in record["pointers_unresolved"]:
                out.append(f"{record['id']}: declared pointer does not resolve: {pointer}")
        return out


# ------------------------------------------------------------------------- primitives
#
# Each primitive is a generic computation parameterised entirely by declaration DATA. A
# primitive knows nothing about what the fact it computes means. Every result carries the
# substrate identifiers that evidence it, so a record can never be fabricated.


def _result(
    headline: str,
    rows: list[list[str]],
    count: int | None,
    evidence: list[str],
    unknown: bool = False,
) -> dict:
    return {
        "headline": headline,
        "rows": rows,
        "count": count,
        "evidence": sorted(set(evidence)),
        "unknown": unknown,
    }


def _payload_or_unknown(sub: Substrate, ident: str) -> tuple[object | None, dict | None]:
    payload = sub.payload(ident)
    if payload is None:
        return None, _result("substrate unavailable", [], None, [], unknown=True)
    return payload, None


def p_record_count(sub: Substrate, args: dict) -> dict:
    ident = args.get("substrate")
    payload, miss = _payload_or_unknown(sub, ident)
    if miss:
        return miss
    value = navigate(payload, args.get("pointer"))
    measured = size_of(value)
    if measured is None:
        return _result("pointer does not resolve to a countable value", [], None, [ident], True)
    return _result(f"{measured} records", [["records", str(measured)]], measured, [ident])


def p_declared_vs_actual(sub: Substrate, args: dict) -> dict:
    ident = args.get("substrate")
    payload, miss = _payload_or_unknown(sub, ident)
    if miss:
        return miss
    declared = size_of(navigate(payload, args.get("count_field")))
    actual = size_of(navigate(payload, args.get("pointer")))
    if declared is None or actual is None:
        return _result("declared or actual value does not resolve", [], None, [ident], True)
    delta = actual - declared
    return _result(
        f"declared {declared} · present {actual} · delta {delta}",
        [["declared", str(declared)], ["present", str(actual)], ["delta", str(delta)]],
        abs(delta),
        [ident],
    )


def p_cross_count_delta(sub: Substrate, args: dict) -> dict:
    left_id = args.get("left_substrate")
    right_id = args.get("right_substrate")
    left_payload, miss = _payload_or_unknown(sub, left_id)
    if miss:
        return miss
    right_payload, miss = _payload_or_unknown(sub, right_id)
    if miss:
        return miss
    left = size_of(navigate(left_payload, args.get("left_path")))
    right = size_of(navigate(right_payload, args.get("right_path")))
    if left is None or right is None:
        return _result("one side does not resolve", [], None, [left_id, right_id], True)
    delta = left - right
    return _result(
        f"{left} vs {right} · delta {delta}",
        [
            [f"`{left_id}` {args.get('left_path')}", str(left)],
            [f"`{right_id}` {args.get('right_path')}", str(right)],
            ["delta", str(delta)],
        ],
        abs(delta),
        [left_id, right_id],
    )


def _iter_records(payload: object, pointer: str | None) -> list[dict]:
    value = navigate(payload, pointer)
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [item for item in value.values() if isinstance(item, dict)]
    return []


def p_duplicate_field_values(sub: Substrate, args: dict) -> dict:
    ident = args.get("substrate")
    payload, miss = _payload_or_unknown(sub, ident)
    if miss:
        return miss
    field = args.get("field")
    counts: dict[str, int] = {}
    for record in _iter_records(payload, args.get("pointer")):
        value = record.get(field)
        if value in (None, ""):
            continue
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    duplicates = sorted(
        ((value, n) for value, n in counts.items() if n > 1), key=lambda pair: (-pair[1], pair[0])
    )
    rows = [[f"`{short(value, 60)}`", str(n)] for value, n in duplicates[:20]]
    if len(duplicates) > 20:
        rows.append([f"… {len(duplicates) - 20} further value(s)", ""])
    return _result(
        f"{len(duplicates)} value(s) shared by more than one record "
        f"(over {len(counts)} distinct value(s))",
        rows,
        len(duplicates),
        [ident],
    )


def p_field_histogram(sub: Substrate, args: dict) -> dict:
    ident = args.get("substrate")
    payload, miss = _payload_or_unknown(sub, ident)
    if miss:
        return miss
    field = args.get("field")
    counts: dict[str, int] = {}
    for record in _iter_records(payload, args.get("pointer")):
        key = str(record.get(field))
        counts[key] = counts.get(key, 0) + 1
    ordered = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    rows = [[f"`{short(value, 60)}`", str(n)] for value, n in ordered]
    return _result(f"{len(ordered)} distinct value(s)", rows, len(ordered), [ident])


def p_field_value_not_in_reference(sub: Substrate, args: dict) -> dict:
    ident = args.get("substrate")
    ref_id = args.get("ref_substrate")
    payload, miss = _payload_or_unknown(sub, ident)
    if miss:
        return miss
    ref_payload, miss = _payload_or_unknown(sub, ref_id)
    if miss:
        return miss
    allowed: set[str] = set()
    ref_field = args.get("ref_field")
    for record in _iter_records(ref_payload, args.get("ref_pointer")):
        value = record.get(ref_field)
        if value not in (None, ""):
            allowed.add(str(value))
    field = args.get("field")
    offending: dict[str, int] = {}
    for record in _iter_records(payload, args.get("pointer")):
        value = record.get(field)
        if value in (None, ""):
            continue
        key = str(value)
        if key not in allowed:
            offending[key] = offending.get(key, 0) + 1
    ordered = sorted(offending.items(), key=lambda pair: (-pair[1], pair[0]))
    rows = [[f"`{short(value, 60)}`", str(n)] for value, n in ordered]
    return _result(
        f"{len(ordered)} value(s) absent from the reference set of {len(allowed)}",
        rows,
        len(ordered),
        [ident, ref_id],
    )


def p_filtered_record_count(sub: Substrate, args: dict) -> dict:
    ident = args.get("substrate")
    payload, miss = _payload_or_unknown(sub, ident)
    if miss:
        return miss
    field = args.get("field")
    wanted = {str(value) for value in as_list(args.get("values"))}
    matched = [
        record
        for record in _iter_records(payload, args.get("pointer"))
        if str(record.get(field)) in wanted
    ]
    rows = [
        [f"`{short(record.get('id') or record.get(field), 48)}`", short(record.get("title") or "")]
        for record in matched[:20]
    ]
    return _result(f"{len(matched)} matching record(s)", rows, len(matched), [ident])


def p_key_occupancy(sub: Substrate, args: dict) -> dict:
    ident = args.get("substrate")
    payload, miss = _payload_or_unknown(sub, ident)
    if miss:
        return miss
    container = navigate(payload, args.get("pointer"))
    if not isinstance(container, dict):
        return _result("pointer does not resolve to a keyed container", [], None, [ident], True)
    field = args.get("field")
    rows: list[list[str]] = []
    for key in sorted(container):
        value = container[key]
        if field and isinstance(value, dict):
            rows.append([f"`{key}`", short(value.get(field))])
        else:
            rows.append([f"`{key}`", short(value)])
    return _result(f"{len(rows)} key(s)", rows, len(rows), [ident])


def p_dict_list_lengths(sub: Substrate, args: dict) -> dict:
    ident = args.get("substrate")
    payload, miss = _payload_or_unknown(sub, ident)
    if miss:
        return miss
    container = navigate(payload, args.get("pointer"))
    if not isinstance(container, dict):
        return _result("pointer does not resolve to a keyed container", [], None, [ident], True)
    rows: list[list[str]] = []
    total = 0
    for key in sorted(container):
        measured = size_of(container[key]) or 0
        total += measured
        rows.append([f"`{key}`", str(measured)])
    rows.append(["**total**", f"**{total}**"])
    return _result(f"{len(container)} key(s) · {total} member(s)", rows, total, [ident])


def p_subdict_fill_ratio(sub: Substrate, args: dict) -> dict:
    ident = args.get("substrate")
    payload, miss = _payload_or_unknown(sub, ident)
    if miss:
        return miss
    field = args.get("field")
    records = _iter_records(payload, args.get("pointer"))
    dimension_filled: dict[str, int] = {}
    dimension_total: dict[str, int] = {}
    complete = 0
    empty = 0
    slots = 0
    filled = 0
    for record in records:
        container = record.get(field)
        if not isinstance(container, dict):
            continue
        local_filled = 0
        for key, value in container.items():
            dimension_total[key] = dimension_total.get(key, 0) + 1
            slots += 1
            if size_of(value):
                filled += 1
                local_filled += 1
                dimension_filled[key] = dimension_filled.get(key, 0) + 1
        if container and local_filled == len(container):
            complete += 1
        if local_filled == 0:
            empty += 1
    ratio = (filled * 10000 // slots) / 100 if slots else 0
    traced = len(records) - empty
    traced_share = (traced * 10000 // len(records)) / 100 if records else 0
    rows = [
        ["records measured", str(len(records))],
        ["dimension slots", str(slots)],
        ["slots populated", str(filled)],
        ["populated share (%)", f"{ratio}"],
        ["records fully traced", str(complete)],
        ["records with no trace", str(empty)],
        ["records with at least one trace", str(traced)],
        ["traced-record share (%)", f"{traced_share}"],
    ]
    for key in sorted(dimension_total):
        rows.append(
            [f"dimension `{key}`", f"{dimension_filled.get(key, 0)}/{dimension_total[key]}"]
        )
    return _result(
        f"{filled}/{slots} dimension slots populated ({ratio}%) · "
        f"{traced}/{len(records)} record(s) carry at least one trace ({traced_share}%) · "
        f"{complete} record(s) fully traced · {empty} with none",
        rows,
        slots - filled,
        [ident],
    )


def p_edge_status_join(sub: Substrate, args: dict) -> dict:
    edge_id = args.get("edge_substrate")
    node_id = args.get("node_substrate")
    edge_payload, miss = _payload_or_unknown(sub, edge_id)
    if miss:
        return miss
    node_payload, miss = _payload_or_unknown(sub, node_id)
    if miss:
        return miss
    key_field = args.get("node_key_field")
    status_field = args.get("node_status_field")
    status_by_key: dict[str, str] = {}
    for record in _iter_records(node_payload, args.get("node_pointer")):
        key = record.get(key_field)
        if key in (None, ""):
            continue
        status_by_key[str(key)] = str(record.get(status_field))
    wanted = {str(value) for value in as_list(args.get("status_values"))}
    from_field = args.get("from_field")
    to_field = args.get("to_field")
    offending: list[list[str]] = []
    unresolved_endpoints = 0
    edges = _iter_records(edge_payload, args.get("edge_pointer"))
    for edge in edges:
        source = str(edge.get(from_field))
        target = str(edge.get(to_field))
        source_status = status_by_key.get(source)
        target_status = status_by_key.get(target)
        if source_status is None or target_status is None:
            unresolved_endpoints += 1
            continue
        if target_status in wanted and source_status not in wanted:
            offending.append([f"`{source}`", source_status, f"`{target}`", target_status])
    rows = [
        ["edges examined", str(len(edges))],
        ["endpoints not registered", str(unresolved_endpoints)],
        ["live dependencies on superseded targets", str(len(offending))],
    ]
    rows += [[a, b, c, d] for a, b, c, d in offending[:20]]
    return _result(
        f"{len(offending)} live dependency/dependencies on a superseded target "
        f"(over {len(edges)} edge(s); {unresolved_endpoints} endpoint(s) not registered)",
        rows,
        len(offending),
        [edge_id, node_id],
    )


def p_tracked_glob_census(sub: Substrate, args: dict) -> dict:
    found: list[str] = []
    for pattern in as_list(args.get("globs")):
        for line in git("ls-files", "--", str(pattern)).splitlines():
            candidate = line.strip()
            if candidate:
                found.append(candidate)
    unique = sorted(set(found))
    rows = [[f"`{item}`", "TRACKED"] for item in unique]
    return _result(f"{len(unique)} tracked path(s)", rows, len(unique), [])


def p_text_presence(sub: Substrate, args: dict, computed: dict[str, dict] | None = None) -> dict:
    source = (computed or {}).get(args.get("items_from")) or {}
    items = [row[0].strip("`") for row in source.get("rows", []) if row and row[0].startswith("`")]
    targets: list[Path] = []
    for entry in as_list(args.get("files")):
        path = REPO / str(entry)
        if path.is_dir():
            targets += sorted(child for child in path.rglob("*") if child.is_file())
        elif path.is_file():
            targets.append(path)
    corpus: dict[str, str] = {}
    for path in targets:
        rel = str(path.relative_to(REPO))
        if not is_tracked(rel):
            continue
        try:
            corpus[rel] = path.read_text("utf-8", errors="ignore")
        except OSError:
            continue
    rows: list[list[str]] = []
    bound = 0
    for item in items:
        holders = sorted(rel for rel, text in corpus.items() if item in text)
        if holders:
            bound += 1
        rows.append(
            [
                f"`{item}`",
                str(len(holders)),
                ", ".join(f"`{holder}`" for holder in holders) if holders else "**none**",
            ]
        )
    return _result(
        f"{bound}/{len(items)} located engine(s) bound to at least one entry point, "
        f"workflow or hook (over {len(corpus)} tracked binding file(s))",
        rows,
        len(items) - bound,
        [],
    )


def p_substrate_census(sub: Substrate, args: dict) -> dict:
    rows: list[list[str]] = []
    unusable = 0
    for ident in sorted(sub.records):
        record = sub.records[ident]
        ok = record["exists"] and record["tracked"] and record["parses"]
        if record["required"] and not ok:
            unusable += 1
        rows.append(
            [
                f"`{ident}`",
                f"`{record['path']}`",
                "YES" if record["exists"] else "**NO**",
                "YES" if record["tracked"] else "**NO**",
                "YES" if record["parses"] else "**NO**",
                f"{len(record['pointers_resolved'])}/{len(record['pointers'])}",
                str(record["records"]),
                f"`{record['content_sha256'][:12]}`" if record["content_sha256"] else "—",
            ]
        )
    return _result(
        f"{len(rows)} declared substrate(s) · {unusable} required substrate(s) unusable",
        rows,
        unusable,
        sorted(sub.records),
    )


def p_binding_mode_distribution(sub: Substrate, args: dict, decl: dict | None = None) -> dict:
    counts: dict[str, int] = {}
    for entry in section(decl or {}, "deliverables"):
        key = str(entry.get("mode"))
        counts[key] = counts.get(key, 0) + 1
    ordered = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    rows = [[f"`{mode}`", str(n)] for mode, n in ordered]
    unknown_modes = {
        str(entry.get("mode")) for entry in section(decl or {}, "modes") if entry.get("is_unknown")
    }
    unknown_total = sum(n for mode, n in counts.items() if mode in unknown_modes)
    rows.append(["**bound to verified absence**", f"**{unknown_total}**"])
    return _result(
        f"{len(ordered)} mode(s) in use · {unknown_total} deliverable(s) bound to verified absence",
        rows,
        unknown_total,
        [],
    )


def p_binding_owner_collision(sub: Substrate, args: dict, decl: dict | None = None) -> dict:
    owners: dict[str, list[str]] = {}
    for entry in section(decl or {}, "deliverables"):
        owner = (entry.get("canonical_owner") or "").strip()
        if not owner:
            continue
        owners.setdefault(owner, []).append(str(entry.get("id")))
    collisions = {owner: ids for owner, ids in owners.items() if len(ids) > 1}
    rows = [
        [f"`{owner}`", ", ".join(f"`{ident}`" for ident in sorted(ids))]
        for owner, ids in sorted(collisions.items())
    ]
    return _result(
        f"{len(collisions)} canonical owner(s) claimed by more than one deliverable "
        f"(over {len(owners)} distinct owner(s))",
        rows,
        len(collisions),
        [],
    )


def p_declared_local_runtime(sub: Substrate, args: dict) -> dict:
    """State a DECLARED per-clone fact and cite the live observation by evidence id.

    This primitive replaced `upstream_probe`, which ran `git rev-parse @{u}` and `git remote`
    at render time and wrote the answers into `16-NON-DERIVABLE-REGISTER.md` and `urrc.json`.
    Remote configuration is per-clone: the same commit rendered "an upstream is configured" on
    a developer machine and "no upstream is configured" in a detached worktree, so two tracked
    artifacts carried a fact about the machine that happened to render them.

    The register's PURPOSE survives intact — it exists to disclose what cannot be derived from
    committed history — but a disclosure of local observation cannot itself be a byte-identical
    canonical artifact. The claim is now authored in the declaration and the observation is
    referenced, never read (UAKOS-CLOSURE-008 R-EV-2).
    """
    rows = [
        ["declared claim", str(args.get("claim", ""))],
        ["derivable from committed history", "**no** — per-clone local runtime state"],
        ["observation", f"`{args.get('evidence_id', '')}` (LOCAL_RUNTIME, NON_CANONICAL)"],
    ]
    return _result(str(args.get("finding", "non-derivable: local runtime state")), rows, 1, [])


def p_ignored_path_census(sub: Substrate, args: dict) -> dict:
    """Census of declared evidence zones over TRACKED state only.

    The `present` column was a filesystem observation: it counted which ignored paths happened
    to exist on the rendering machine, so the count fell from 4 to 1 in a fresh worktree and
    moved the artifact's bytes with it. Whether a declared path is TRACKED is repository truth
    at a commit and is all this fact needs — a path excluded from version control cannot supply
    prior seals from committed history whether or not it exists locally.
    """
    rows: list[list[str]] = []
    excluded = 0
    for entry in as_list(args.get("paths")):
        rel = str(entry)
        tracked = is_tracked(rel)
        if not tracked:
            excluded += 1
        rows.append([f"`{rel}`", "YES" if tracked else "**NO**"])
    return _result(
        f"{excluded} declared path(s) excluded from version control",
        rows,
        excluded,
        [],
    )


# The primitive table is engine vocabulary: fixed, closed, and knowing nothing about the
# meaning of any fact it computes. Adding a fact is a declaration edit; adding a *kind* of
# computation is the only change that touches this table.
PRIMITIVES: dict[str, Callable[..., dict]] = {
    "record_count": p_record_count,
    "declared_vs_actual": p_declared_vs_actual,
    "cross_count_delta": p_cross_count_delta,
    "duplicate_field_values": p_duplicate_field_values,
    "field_histogram": p_field_histogram,
    "field_value_not_in_reference": p_field_value_not_in_reference,
    "filtered_record_count": p_filtered_record_count,
    "key_occupancy": p_key_occupancy,
    "dict_list_lengths": p_dict_list_lengths,
    "subdict_fill_ratio": p_subdict_fill_ratio,
    "edge_status_join": p_edge_status_join,
    "tracked_glob_census": p_tracked_glob_census,
    "text_presence": p_text_presence,
    "substrate_census": p_substrate_census,
    "binding_mode_distribution": p_binding_mode_distribution,
    "binding_owner_collision": p_binding_owner_collision,
    "declared_local_runtime": p_declared_local_runtime,
    "ignored_path_census": p_ignored_path_census,
}

# Primitives that need the declaration itself, and primitives that consume the result of
# another derivation. Declared here so the dispatcher stays uniform.
NEEDS_DECLARATION = ("binding_mode_distribution", "binding_owner_collision")
NEEDS_COMPUTED = ("text_presence",)


def compute_derivations(decl: dict, sub: Substrate) -> dict[str, dict]:
    """Evaluate every declared derivation. Dependent derivations run last."""
    entries = section(decl, "derivations")
    ordered = [entry for entry in entries if entry.get("primitive") not in NEEDS_COMPUTED]
    ordered += [entry for entry in entries if entry.get("primitive") in NEEDS_COMPUTED]
    computed: dict[str, dict] = {}
    for entry in ordered:
        ident = str(entry.get("id"))
        name = str(entry.get("primitive"))
        primitive = PRIMITIVES.get(name)
        args = entry.get("args") if isinstance(entry.get("args"), dict) else {}
        if primitive is None:
            result = _result(f"undeclared primitive {name!r}", [], None, [], unknown=True)
        elif name in NEEDS_DECLARATION:
            result = primitive(sub, args, decl)
        elif name in NEEDS_COMPUTED:
            result = primitive(sub, args, computed)
        else:
            result = primitive(sub, args)
        result = dict(result)
        result["id"] = ident
        result["primitive"] = name
        result["purpose"] = entry.get("purpose") or ""
        computed[ident] = result
    return computed


# ------------------------------------------------------------------- self-check logic


def check_declaration(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Structural integrity: identity, vocabulary, closure, range and cross-reference."""
    findings: list[str] = []
    seen: dict[str, str] = {}
    for name, allowed in ALLOWED_KEYS.items():
        entries = decl.get(name)
        if not entries:
            findings.append(f"{name}: section is absent or empty")
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                findings.append(f"{name}: entry is not a record")
                continue
            ident = entry.get("id")
            if not ident:
                findings.append(f"{name}: entry without an id")
                continue
            if ident in seen:
                findings.append(f"duplicate identifier {ident} ({seen[ident]} and {name})")
            seen[ident] = name
            extra = set(entry) - allowed
            if extra:
                findings.append(f"{ident}: key(s) outside the permitted set: {sorted(extra)}")

    programme = decl.get("programme") or {}
    for key in PROGRAMME_SCALAR_KEYS:
        if not programme.get(key):
            findings.append(f"programme: declares no {key}")
    for key in PROGRAMME_REFERENCE_KEYS:
        ref = programme.get(key)
        if not ref or resolve_reference(str(ref)) is None:
            findings.append(f"programme.{key}: reference does not resolve: {ref!r}")
    for ref in as_list(programme.get("governed_by")):
        if resolve_reference(str(ref)) is None:
            findings.append(f"programme.governed_by: reference does not resolve: {ref!r}")
    for prefix in as_list(programme.get("forbidden_write_prefixes")):
        if not (REPO / str(prefix)).exists():
            findings.append(f"programme.forbidden_write_prefixes: prefix does not exist: {prefix}")
    try:
        re.compile(str(programme.get("law_namespace_pattern") or ""))
    except re.error as exc:
        findings.append(f"programme.law_namespace_pattern: not a valid expression: {exc}")

    mode_names = {str(entry.get("mode")) for entry in section(decl, "modes")}
    for entry in section(decl, "modes"):
        for key in ("mode", "definition"):
            if not entry.get(key):
                findings.append(f"{entry.get('id')}: declares no {key}")
        for key in ("is_reuse", "requires_owner", "requires_derivation", "is_unknown"):
            if key not in entry:
                findings.append(f"{entry.get('id')}: declares no {key} flag")

    substrate_ids = set(ids_of(decl, "substrate"))
    for entry in section(decl, "substrate"):
        for key in ("path", "kind", "purpose"):
            if not entry.get(key):
                findings.append(f"{entry.get('id')}: declares no {key}")
        if "required" not in entry:
            findings.append(f"{entry.get('id')}: declares no required flag")
        if not as_list(entry.get("pointers")):
            findings.append(f"{entry.get('id')}: declares no pointers")

    derivation_ids = set(ids_of(decl, "derivations"))
    for entry in section(decl, "derivations"):
        ident = entry.get("id")
        if not entry.get("purpose"):
            findings.append(f"{ident}: declares no purpose")
        name = str(entry.get("primitive"))
        if name not in PRIMITIVES:
            findings.append(f"{ident}: primitive {name!r} is not implemented")
        args = entry.get("args")
        if not isinstance(args, dict):
            findings.append(f"{ident}: declares no args object")
            continue
        for key, value in args.items():
            if key.endswith("substrate") and str(value) not in substrate_ids:
                findings.append(f"{ident}: args.{key} names undeclared substrate {value!r}")
            if key == "items_from" and str(value) not in derivation_ids:
                findings.append(f"{ident}: args.{key} names undeclared derivation {value!r}")

    matrix_ids = set(ids_of(decl, "matrices"))
    for entry in section(decl, "matrices"):
        for key in ("name", "subject"):
            if not entry.get(key):
                findings.append(f"{entry.get('id')}: declares no {key}")
        if "computable" not in entry:
            findings.append(f"{entry.get('id')}: declares no computable flag")

    # deliverables — contiguous charter range, no gap, no repeat; every binding bound
    deliverables = section(decl, "deliverables")
    first = programme.get("deliverable_range_first")
    last = programme.get("deliverable_range_last")
    if not isinstance(first, int) or not isinstance(last, int) or last < first:
        findings.append("programme: declares no usable deliverable index range")
    else:
        expected = list(range(first, last + 1))
        actual = sorted(
            entry.get("index") for entry in deliverables if isinstance(entry.get("index"), int)
        )
        if len(actual) != len(deliverables):
            findings.append("deliverables: an entry declares no integer index")
        if actual != expected:
            missing = sorted(set(expected) - set(actual))
            repeated = sorted({i for i in actual if actual.count(i) > 1})
            findings.append(
                "deliverables: indices are not exactly the charter range "
                f"{first}..{last} — missing {missing}, repeated {repeated}"
            )
    for entry in deliverables:
        ident = entry.get("id")
        for key in ("name", "subject", "generator_class", "note"):
            if not entry.get(key):
                findings.append(f"{ident}: declares no {key}")
        if "canonical_owner" not in entry:
            findings.append(f'{ident}: declares no canonical_owner field (use "" when none)')
        if str(entry.get("mode")) not in mode_names:
            findings.append(f"{ident}: mode {entry.get('mode')!r} is not a declared mode")
        if str(entry.get("matrix")) not in matrix_ids:
            findings.append(f"{ident}: matrix {entry.get('matrix')!r} is not a declared matrix")
        for ref in as_list(entry.get("derivations")):
            if str(ref) not in derivation_ids:
                findings.append(f"{ident}: names undeclared derivation {ref!r}")

    # gates — each binds at least one computable matrix, so a manual gate is impossible
    computable = {
        str(entry.get("id")) for entry in section(decl, "matrices") if entry.get("computable")
    }
    for entry in section(decl, "gates"):
        ident = entry.get("id")
        for key in ("name", "criterion"):
            if not entry.get(key):
                findings.append(f"{ident}: declares no {key}")
        if "blocking" not in entry:
            findings.append(f"{ident}: declares no blocking flag")
        bound = [str(ref) for ref in as_list(entry.get("matrices"))]
        for ref in bound:
            if ref not in matrix_ids:
                findings.append(f"{ident}: names undeclared matrix {ref!r}")
        if not [ref for ref in bound if ref in computable]:
            findings.append(f"{ident}: binds no computable matrix — a manual gate is prohibited")

    outputs = section(decl, "outputs")
    if len(outputs) != RENDERED_OUTPUTS:
        findings.append(
            f"outputs: exactly {RENDERED_OUTPUTS} deliverables are rendered, "
            f"{len(outputs)} declared"
        )
    deliverable_ids = set(ids_of(decl, "deliverables"))
    for entry in outputs:
        for key in ("file", "title", "purpose"):
            if not entry.get(key):
                findings.append(f"{entry.get('id')}: declares no {key}")
        for ref in as_list(entry.get("matrices")):
            if str(ref) not in matrix_ids:
                findings.append(f"{entry.get('id')}: names undeclared matrix {ref!r}")
        for ref in as_list(entry.get("derivations")):
            if str(ref) not in derivation_ids:
                findings.append(f"{entry.get('id')}: names undeclared derivation {ref!r}")
        for ref in as_list(entry.get("deliverables")):
            if str(ref) not in deliverable_ids:
                findings.append(f"{entry.get('id')}: names undeclared deliverable {ref!r}")

    # every matrix is rendered by at least one output, so a declared matrix cannot hide
    rendered_matrices = {str(ref) for entry in outputs for ref in as_list(entry.get("matrices"))}
    for ident in sorted(matrix_ids - rendered_matrices):
        findings.append(f"{ident}: declared matrix is bound to no output")

    for entry in section(decl, "non_derivable"):
        ident = entry.get("id")
        for key in ("fact", "reason", "required_evidence_class", "owner"):
            if not entry.get(key):
                findings.append(f"{ident}: declares no {key}")
        probe = str(entry.get("probe"))
        if probe not in derivation_ids:
            findings.append(f"{ident}: probe {probe!r} is not a declared derivation")
        if entry.get("owner") and resolve_reference(str(entry.get("owner"))) is None:
            findings.append(f"{ident}: owner does not resolve: {entry.get('owner')!r}")
        bounds = as_list(entry.get("bounds"))
        if not bounds:
            findings.append(f"{ident}: names no deliverable that it bounds")
        for ref in bounds:
            if str(ref) not in deliverable_ids:
                findings.append(f"{ident}: bounds undeclared deliverable {ref!r}")

    for entry in section(decl, "work_packages"):
        ident = entry.get("id")
        for key in ("title", "owner", "route", "discharges", "acceptance"):
            if not entry.get(key):
                findings.append(f"{ident}: declares no {key}")
        if "authorization_required" not in entry:
            findings.append(f"{ident}: declares no authorization_required flag")
        if entry.get("owner") and resolve_reference(str(entry.get("owner"))) is None:
            findings.append(f"{ident}: owner does not resolve: {entry.get('owner')!r}")

    for entry in section(decl, "references"):
        ident = entry.get("id")
        if not entry.get("purpose"):
            findings.append(f"{ident}: declares no purpose")
        if resolve_reference(str(entry.get("path"))) is None:
            findings.append(f"{ident}: reference does not resolve: {entry.get('path')!r}")

    return findings


def check_no_enumeration(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Prove the programme is DATA: the engine may name none of its subject matter.

    A declared value counts as named only when it appears as a distinct token in the
    source, so an unrelated English word that merely contains a declared token as a
    substring is not a false positive — while any literal use of the token itself is.
    """
    findings: list[str] = []
    source = Path(__file__).read_text("utf-8")
    literals: list[str] = []
    for name in ALLOWED_KEYS:
        literals += [str(entry.get("id")) for entry in section(decl, name) if entry.get("id")]
    literals += [str(entry.get("name")) for entry in section(decl, "deliverables")]
    literals += [str(entry.get("mode")) for entry in section(decl, "modes")]
    literals += [str(entry.get("path")) for entry in section(decl, "substrate")]
    literals += [
        str(entry.get("canonical_owner"))
        for entry in section(decl, "deliverables")
        if entry.get("canonical_owner")
    ]
    literals.append(str((decl.get("programme") or {}).get("law_namespace_pattern") or ""))
    for literal in sorted({item for item in literals if item and item != "None"}):
        token = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(literal) + r"(?![A-Za-z0-9_])")
        if token.search(source):
            findings.append(
                f"engine source special-cases declared value {literal!r} — extending the "
                "programme would require a code change"
            )
    return findings


def check_write_scope(decl: dict, sub: Substrate | None = None, written: list[Path] | None = None):
    """No write may land outside this programme's own operational memory."""
    findings: list[str] = []
    programme = decl.get("programme") or {}
    for prefix in as_list(programme.get("forbidden_write_prefixes")):
        target = REPO / str(prefix)
        if not target.exists():
            findings.append(f"forbidden-write prefix does not exist: {prefix}")
            continue
        try:
            HERE.relative_to(target.resolve())
        except ValueError:
            pass
        else:
            findings.append(f"programme home lies inside a forbidden write prefix: {prefix}")
    for path in written or []:
        resolved = path.resolve()
        try:
            resolved.relative_to(HERE)
        except ValueError:
            findings.append(f"write outside the programme's operational memory: {resolved}")
    return findings


def check_substrate(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Every required substrate exists, is tracked, parses, and its pointers resolve."""
    substrate = sub if sub is not None else Substrate(decl)
    return substrate.findings()


def check_no_fabrication(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Every derived record carries substrate evidence or an explicit absence marker."""
    substrate = sub if sub is not None else Substrate(decl)
    computed = compute_derivations(decl, substrate)
    probes = {str(entry.get("probe")) for entry in section(decl, "non_derivable")}
    findings: list[str] = []
    for ident in sorted(computed):
        result = computed[ident]
        if result.get("unknown"):
            findings.append(
                f"{ident}: derivation returned no measurable value and is not declared as "
                "verified absence"
            )
            continue
        if result.get("evidence"):
            continue
        if ident in probes:
            continue
        if result.get("count") is None:
            findings.append(f"{ident}: derivation carries neither evidence nor a counted result")
    for entry in section(decl, "deliverables"):
        mode = mode_of(decl, entry)
        if mode.get("is_unknown") and not [
            item for item in section(decl, "non_derivable") if item.get("probe")
        ]:
            findings.append(f"{entry.get('id')}: bound to absence with no counted probe")
    return findings


def check_reuse_before_create(decl: dict, sub: Substrate | None = None) -> list[str]:
    """The zero-duplication invariant, mechanized."""
    findings: list[str] = []
    for entry in section(decl, "deliverables"):
        ident = entry.get("id")
        mode = mode_of(decl, entry)
        owner = (entry.get("canonical_owner") or "").strip()
        resolved = resolve_reference(owner) if owner else None
        if resolved is not None and not mode.get("is_reuse"):
            findings.append(
                f"{ident}: canonical owner resolves ({owner}) but the binding is not a reuse "
                "mode — a create over an existing owner is a finding, not a preference"
            )
        if mode.get("requires_owner") and resolved is None:
            findings.append(
                f"{ident}: the declared mode requires a canonical owner, but {owner!r} does "
                "not resolve"
            )
        if mode.get("requires_derivation") and not as_list(entry.get("derivations")):
            findings.append(f"{ident}: the declared mode requires a derivation, and none is bound")
        if not mode.get("requires_owner") and owner and resolved is None:
            findings.append(f"{ident}: declares an owner that does not resolve: {owner!r}")
    return findings


def check_law_namespace(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Neither the declaration nor any rendered byte may reintroduce the law token."""
    programme = decl.get("programme") or {}
    pattern = str(programme.get("law_namespace_pattern") or "")
    if not pattern:
        return ["programme: declares no law namespace pattern"]
    try:
        expression = re.compile(pattern)
    except re.error as exc:
        return [f"programme.law_namespace_pattern: not a valid expression: {exc}"]
    whitelist = {str(item) for item in as_list(programme.get("law_citation_whitelist"))}

    def offences(label: str, text: str) -> list[str]:
        hits = sorted({hit for hit in expression.findall(text) if hit not in whitelist})
        return [f"{label}: reintroduces the ratified law token {hit!r}" for hit in hits]

    findings = offences("declaration", DECLARATION.read_text("utf-8"))
    substrate = sub if sub is not None else Substrate(decl)
    model = build_model(decl, substrate, repository_state())
    for name, text in sorted(render(decl, model).items()):
        findings += offences(f"rendered output {name}", text)
    return findings


def self_determinism(decl: dict, sub: Substrate | None = None) -> list[str]:
    """Render the output set twice from one model; the bytes must be identical."""
    substrate = sub if sub is not None else Substrate(decl)
    fixed_state = repository_state()
    first = render(decl, build_model(decl, substrate, fixed_state))
    second = render(decl, build_model(decl, substrate, fixed_state))
    if set(first) != set(second):
        return ["rendered output set differs between runs"]
    return [
        f"non-deterministic rendering: {name}"
        for name in sorted(first)
        if first[name] != second[name]
    ]


SELF_CHECKS: dict[str, Callable[[dict, Substrate | None], list[str]]] = {
    "--check-declaration": check_declaration,
    "--check-no-enumeration": check_no_enumeration,
    "--check-write-scope": lambda decl, sub=None: check_write_scope(decl, sub),
    "--check-determinism": self_determinism,
    "--check-substrate": check_substrate,
    "--check-no-fabrication": check_no_fabrication,
    "--check-reuse-before-create": check_reuse_before_create,
    "--check-law-namespace": check_law_namespace,
}


# --------------------------------------------------------------------------- assessment


def mode_of(decl: dict, deliverable: dict) -> dict:
    for entry in section(decl, "modes"):
        if str(entry.get("mode")) == str(deliverable.get("mode")):
            return entry
    return {}


def assess(decl: dict, sub: Substrate, computed: dict[str, dict]) -> dict:
    """Assess every deliverable, matrix and gate from computed state only."""
    unknown_probe = {str(entry.get("probe")): entry for entry in section(decl, "non_derivable")}
    deliverables: list[dict] = []
    for entry in section(decl, "deliverables"):
        mode = mode_of(decl, entry)
        owner = (entry.get("canonical_owner") or "").strip()
        resolved = resolve_reference(owner) if owner else None
        owner_rel = str(resolved.relative_to(REPO)) if resolved is not None else ""
        derivations = [str(ref) for ref in as_list(entry.get("derivations"))]
        unresolved = [ref for ref in derivations if computed.get(ref, {}).get("unknown")]
        reasons: list[str] = []
        if mode.get("requires_owner") and resolved is None:
            reasons.append(f"canonical owner does not resolve: {owner}")
        if resolved is not None and not mode.get("is_reuse"):
            reasons.append("owner resolves but the binding is a create mode")
        if mode.get("requires_derivation") and not derivations:
            reasons.append("the mode requires a derivation and none is bound")
        if unresolved:
            reasons.append("derivation(s) returned no measurable value: " + ", ".join(unresolved))
        if (
            mode.get("is_unknown")
            and not any(ref in unknown_probe for ref in derivations)
            and not unknown_probe
        ):
            reasons.append("bound to absence with no counted probe")
        bound = not reasons
        deliverables.append(
            {
                "index": entry.get("index"),
                "id": entry.get("id"),
                "name": entry.get("name") or "",
                "subject": entry.get("subject") or "",
                "mode": str(entry.get("mode")),
                "is_reuse": bool(mode.get("is_reuse")),
                "is_unknown": bool(mode.get("is_unknown")),
                "canonical_owner": owner,
                "owner_resolved": owner_rel,
                "owner_tracked": is_tracked(owner_rel) if owner_rel else False,
                "matrix": str(entry.get("matrix")),
                "generator_class": entry.get("generator_class") or "",
                "note": entry.get("note") or "",
                "derivations": derivations,
                "bound": bound,
                "reasons": reasons,
            }
        )

    by_matrix: dict[str, list[dict]] = {}
    for record in deliverables:
        by_matrix.setdefault(record["matrix"], []).append(record)

    matrices: list[dict] = []
    for entry in section(decl, "matrices"):
        ident = str(entry.get("id"))
        members = by_matrix.get(ident, [])
        member_derivations: list[str] = []
        for record in members:
            for ref in record["derivations"]:
                if ref not in member_derivations:
                    member_derivations.append(ref)
        unbound = [record["id"] for record in members if not record["bound"]]
        matrices.append(
            {
                "id": ident,
                "name": entry.get("name") or "",
                "subject": entry.get("subject") or "",
                "computable": bool(entry.get("computable")),
                "deliverables": [record["id"] for record in members],
                "derivations": member_derivations,
                "unbound": unbound,
                "verdict": "BOUND" if members and not unbound else "NOT BOUND",
            }
        )
    verdict_by_matrix = {record["id"]: record for record in matrices}

    guards = {
        "declaration": check_declaration(decl, sub),
        "substrate": check_substrate(decl, sub),
        "reuse": check_reuse_before_create(decl, sub),
        "fabrication": check_no_fabrication(decl, sub),
    }

    gates: list[dict] = []
    for entry in section(decl, "gates"):
        ident = str(entry.get("id"))
        bound_matrices = [str(ref) for ref in as_list(entry.get("matrices"))]
        failures: list[str] = []
        for ref in bound_matrices:
            matrix = verdict_by_matrix.get(ref)
            if matrix is None:
                failures.append(f"{ref}: not computed")
            elif matrix["unbound"]:
                failures.append(f"{ref}: unbound deliverable(s) {', '.join(matrix['unbound'])}")
        gates.append(
            {
                "id": ident,
                "name": entry.get("name") or "",
                "blocking": bool(entry.get("blocking")),
                "criterion": entry.get("criterion") or "",
                "matrices": bound_matrices,
                "failures": failures,
                "verdict": "PASS" if not failures else "FAIL",
            }
        )

    return {
        "deliverables": deliverables,
        "matrices": matrices,
        "gates": gates,
        "guards": guards,
    }


RENDERED_OUTPUTS = 18


def build_model(decl: dict, sub: Substrate, repo_state: dict) -> dict:
    computed = compute_derivations(decl, sub)
    a = assess(decl, sub, computed)
    deliverables = a["deliverables"]
    gates = a["gates"]
    guards = a["guards"]

    guard_findings = sorted({item for values in guards.values() for item in values})
    blocking_failed = [gate["id"] for gate in gates if gate["blocking"] and gate["failures"]]
    advisory_failed = [gate["id"] for gate in gates if not gate["blocking"] and gate["failures"]]
    unbound = [record["id"] for record in deliverables if not record["bound"]]

    gate_open = not guard_findings and not blocking_failed and not unbound
    programme = decl["programme"]

    mode_counts: dict[str, int] = {}
    for record in deliverables:
        mode_counts[record["mode"]] = mode_counts.get(record["mode"], 0) + 1

    substrate_records = [sub.records[key] for key in sorted(sub.records)]
    model = {
        "programme": programme,
        "repository": repo_state,
        "substrate": substrate_records,
        "derivations": [computed[key] for key in sorted(computed)],
        "deliverables": deliverables,
        "matrices": a["matrices"],
        "gates": gates,
        "guards": guards,
        "guard_findings": guard_findings,
        "non_derivable": section(decl, "non_derivable"),
        "work_packages": section(decl, "work_packages"),
        "references": section(decl, "references"),
        "modes": section(decl, "modes"),
        "metrics": {
            "deliverable_total": len(deliverables),
            "deliverables_bound": len([r for r in deliverables if r["bound"]]),
            "deliverables_unbound": unbound,
            "mode_distribution": mode_counts,
            "reuse_bindings": len([r for r in deliverables if r["is_reuse"]]),
            "declared_unknown_bindings": len([r for r in deliverables if r["is_unknown"]]),
            "substrate_total": len(substrate_records),
            "substrate_usable": len(
                [r for r in substrate_records if r["exists"] and r["tracked"] and r["parses"]]
            ),
            "derivation_total": len(computed),
            "derivations_measured": len(
                [key for key in computed if not computed[key].get("unknown")]
            ),
            "matrix_total": len(a["matrices"]),
            "matrices_bound": len([m for m in a["matrices"] if not m["unbound"]]),
            "gate_total": len(gates),
            "gates_passed": len([g for g in gates if not g["failures"]]),
            "blocking_failed": blocking_failed,
            "advisory_failed": advisory_failed,
            "non_derivable_total": len(section(decl, "non_derivable")),
            "work_package_total": len(section(decl, "work_packages")),
            "evidence_references": sum(
                len(computed[key].get("evidence") or []) for key in computed
            ),
        },
        "gate": "OPEN" if gate_open else "CLOSED",
        "determination": (
            programme["determination_pass"] if gate_open else programme["determination_fail"]
        ),
        "gate_exit": 0 if gate_open else 1,
    }
    sealed = {
        "deliverables": [
            {"id": r["id"], "bound": r["bound"], "mode": r["mode"]} for r in deliverables
        ],
        "matrices": [{"id": m["id"], "verdict": m["verdict"]} for m in a["matrices"]],
        "gates": [{"id": g["id"], "verdict": g["verdict"]} for g in gates],
        "gate": model["gate"],
        "determination": model["determination"],
        "guard_findings": guard_findings,
    }
    model["seal_sha256"] = digest(sealed)
    return model


# ------------------------------------------------------------------------ rendering


def header(title: str, decl: dict, model: dict, purpose: str) -> str:
    programme = decl["programme"]
    repo = model["repository"]
    m = model["metrics"]
    return (
        f"# {title}\n\n"
        + table(
            ["Field", "Value"],
            [
                ["PROGRAMME", f"`{programme['id']}` — {programme['name']} v{programme['version']}"],
                ["CHARTERED AS", f"`{programme['charter_designation']}`"],
                ["RESUMED BY", f"`{programme.get('resumed_by_directive', '')}`"],
                ["AUTHORITY", f"**{programme['authority']}**"],
                ["GOVERNING INSTRUMENT", f"`{programme['governing_instrument']}`"],
                ["OPERATIONAL HOME", f"`{programme['operational_home']}`"],
                ["REPOSITORY ANCHOR", repo["anchor"]],
                ["FIXED-POINT BASIS", repo["basis"]],
                ["DELIVERABLE BINDING", f"{m['deliverables_bound']}/{m['deliverable_total']}"],
                ["SUBSTRATE USABLE", f"{m['substrate_usable']}/{m['substrate_total']}"],
                ["DETERMINATION", f"**{model['determination']}**"],
                [
                    programme["gate_name"].upper(),
                    f"**{model['gate']}** (`{programme['gate_clause']}`)",
                ],
                ["SEAL (sha256)", f"`{model['seal_sha256']}`"],
                ["GENERATED BY", "`urrc_engine.py` — regenerated, never hand-authored"],
            ],
        )
        + f"\n> {purpose}\n\n"
        + f"> **DISCLOSURE.** {programme['disclosure']}\n\n---\n\n"
    )


FOOTER = (
    "\n---\n\n*This determination is DERIVED TRUTH. It creates no authority, allocates no "
    "identity, ratifies nothing, freezes nothing, and supersedes no governing instrument. It "
    "binds what already exists and duplicates none of it. Where a conflict is reported, the "
    "conflict is recorded with each verdict's scope and left to the authority that owns it. "
    "Where a fact could not be honestly derived, the absence is declared and counted rather "
    "than filled in. Where this document conflicts with a higher frozen or governing "
    "instrument, the higher instrument governs.*\n"
)


def deliverable_rows(records: list[dict]) -> list[list[str]]:
    return [
        [
            str(record["index"]),
            f"`{record['id']}`",
            record["name"],
            f"`{record['mode']}`",
            f"`{record['canonical_owner']}`" if record["canonical_owner"] else "—",
            (
                "OK"
                if record["owner_resolved"]
                else ("n/a" if not record["canonical_owner"] else "**MISSING**")
            ),
            (
                "YES"
                if record["owner_tracked"]
                else ("\u2014" if not record["canonical_owner"] else "**NO**")
            ),
            record["generator_class"],
            "**BOUND**" if record["bound"] else "**NOT BOUND** — " + "; ".join(record["reasons"]),
        ]
        for record in records
    ]


DELIVERABLE_HEADERS = [
    "#",
    "Deliverable",
    "Name",
    "Mode",
    "Canonical owner",
    "Resolves",
    "Tracked",
    "Generator",
    "Binding",
]


def derivation_block(result: dict) -> str:
    body = (
        f"**`{result['id']}`** — {result['purpose']}\n\n"
        f"- **Primitive** — `{result['primitive']}`\n"
        f"- **Result** — {result['headline']}\n"
        f"- **Substrate evidence** — "
        + (
            ", ".join(f"`{item}`" for item in result["evidence"])
            or "none (probe over the repository)"
        )
        + "\n"
        + ("- **Measurable** — **NO — declared unknown**\n" if result.get("unknown") else "")
        + "\n"
    )
    rows = result.get("rows") or []
    if rows:
        width = max(len(row) for row in rows)
        headers = ["Key", "Value", "Detail", "Detail"][:width]
        body += table(headers, [list(row) + [""] * (width - len(row)) for row in rows]) + "\n"
    return body


def bounded_deliverable_ids(model: dict) -> set[str]:
    """Deliverables whose claim is capped by a registered refusal."""
    return {str(ref) for entry in model["non_derivable"] for ref in as_list(entry.get("bounds"))}


def render(decl: dict, model: dict) -> dict[str, str]:
    spec = section(decl, "outputs")
    name = [entry["file"] for entry in spec]
    title = [entry["title"] for entry in spec]
    purpose = [entry["purpose"] for entry in spec]
    m = model["metrics"]
    by_id = {record["id"]: record for record in model["deliverables"]}
    derivation_by_id = {result["id"]: result for result in model["derivations"]}
    matrix_by_id = {record["id"]: record for record in model["matrices"]}
    out: dict[str, str] = {}

    # ---- matrix / binding documents (every output that binds a matrix)
    for index, entry in enumerate(spec):
        bound_matrices = [str(ref) for ref in as_list(entry.get("matrices"))]
        if not bound_matrices:
            continue
        body = header(title[index], decl, model, purpose[index])
        for ref in bound_matrices:
            matrix = matrix_by_id.get(ref)
            if matrix is None:
                continue
            members = [by_id[ident] for ident in matrix["deliverables"] if ident in by_id]
            body += (
                f"## {matrix['name']}\n\n"
                f"{matrix['subject']}\n\n"
                + table(
                    ["Field", "Value"],
                    [
                        ["Matrix", f"`{matrix['id']}`"],
                        ["Deliverables bound", str(len(members))],
                        ["Computable", "YES" if matrix["computable"] else "**NO**"],
                        ["Verdict", f"**{matrix['verdict']}**"],
                        [
                            "Unbound",
                            ", ".join(f"`{i}`" for i in matrix["unbound"]) or "none",
                        ],
                    ],
                )
                + "\n### Deliverables\n\n"
                + table(DELIVERABLE_HEADERS, deliverable_rows(members))
                + "\n"
            )
            for record in members:
                capped = [
                    entry
                    for entry in model["non_derivable"]
                    if record["id"] in [str(ref) for ref in as_list(entry.get("bounds"))]
                ]
                body += (
                    f"#### {record['id']} — {record['name']}\n\n"
                    f"- **Subject** — {record['subject']}\n"
                    f"- **Binding mode** — `{record['mode']}`\n"
                    f"- **Canonical owner** — "
                    + (
                        f"`{record['canonical_owner']}`"
                        if record["canonical_owner"]
                        else "none \u2014 derived"
                    )
                    + "\n"
                    f"- **Note** — {record['note']}\n"
                    + (
                        ""
                        if not capped
                        else "- **Claim capped by verified absence** — "
                        + "; ".join(f"`{entry.get('id')}` {entry.get('fact')}" for entry in capped)
                        + "\n"
                    )
                    + "\n"
                )
                for ref in record["derivations"]:
                    result = derivation_by_id.get(ref)
                    if result is not None:
                        body += derivation_block(result)
        extra = [str(ref) for ref in as_list(entry.get("derivations"))]
        for ref in extra:
            result = derivation_by_id.get(ref)
            if result is not None:
                body += derivation_block(result)
        out[name[index]] = body + FOOTER

    # ---- 01 deliverable binding register
    out[name[1]] = (
        header(title[1], decl, model, purpose[1])
        + "## The chartered deliverables\n\n"
        + table(DELIVERABLE_HEADERS, deliverable_rows(model["deliverables"]))
        + "\n## Binding modes\n\n"
        + table(
            ["Mode", "Definition", "Reuse", "Owner required", "Derivation required", "Absence"],
            [
                [
                    f"`{entry.get('mode')}`",
                    entry.get("definition") or "",
                    "YES" if entry.get("is_reuse") else "no",
                    "YES" if entry.get("requires_owner") else "no",
                    "YES" if entry.get("requires_derivation") else "no",
                    "YES" if entry.get("is_unknown") else "no",
                ]
                for entry in model["modes"]
            ],
        )
        + "\n## Mode distribution\n\n"
        + table(
            ["Mode", "Deliverables"],
            [[f"`{mode}`", str(n)] for mode, n in sorted(m["mode_distribution"].items())],
        )
        + "\n## Bound canonical artefacts (pointers only)\n\n"
        + table(
            ["Reference", "Path", "Resolves", "Purpose"],
            [
                [
                    f"`{entry.get('id')}`",
                    f"`{entry.get('path')}`",
                    (
                        "OK"
                        if resolve_reference(str(entry.get("path"))) is not None
                        else "**MISSING**"
                    ),
                    entry.get("purpose") or "",
                ]
                for entry in model["references"]
            ],
        )
        + FOOTER
    )

    # ---- 00 dashboard
    out[name[0]] = (
        header(f"{decl['programme']['id']} — {title[0]}", decl, model, purpose[0])
        + "## Determination\n\n"
        + table(
            ["Dimension", "Value"],
            [
                ["Deliverables bound", f"{m['deliverables_bound']}/{m['deliverable_total']}"],
                ["Reuse bindings", str(m["reuse_bindings"])],
                ["Bound to verified absence", str(m["declared_unknown_bindings"])],
                ["Substrate usable", f"{m['substrate_usable']}/{m['substrate_total']}"],
                ["Derivations measured", f"{m['derivations_measured']}/{m['derivation_total']}"],
                ["Matrices bound", f"{m['matrices_bound']}/{m['matrix_total']}"],
                ["Gates passed", f"{m['gates_passed']}/{m['gate_total']}"],
                ["Blocking gate failures", ", ".join(m["blocking_failed"]) or "none"],
                ["Advisory gate failures", ", ".join(m["advisory_failed"]) or "none"],
                ["Non-derivable facts declared", str(m["non_derivable_total"])],
                ["Work packages registered", str(m["work_package_total"])],
                ["Substrate evidence references", str(m["evidence_references"])],
                ["Guard findings", str(len(model["guard_findings"]))],
                ["Determination", f"**{model['determination']}**"],
                ["Gate", f"**{model['gate']}**"],
            ],
        )
        + "\n## Binding distribution\n\n"
        + table(
            ["Mode", "Deliverables", "Reuse"],
            [
                [
                    f"`{entry.get('mode')}`",
                    str(m["mode_distribution"].get(str(entry.get("mode")), 0)),
                    "YES" if entry.get("is_reuse") else "no",
                ]
                for entry in model["modes"]
            ],
        )
        + "\n## Matrix verdicts\n\n"
        + table(
            ["Matrix", "Name", "Deliverables", "Verdict"],
            [
                [
                    f"`{record['id']}`",
                    record["name"],
                    str(len(record["deliverables"])),
                    f"**{record['verdict']}**",
                ]
                for record in model["matrices"]
            ],
        )
        + "\n## Gate table\n\n"
        + table(
            ["Gate", "Name", "Blocking", "Criterion", "Verdict"],
            [
                [
                    f"`{gate['id']}`",
                    gate["name"],
                    "YES" if gate["blocking"] else "advisory",
                    gate["criterion"],
                    f"**{gate['verdict']}**"
                    + ("" if not gate["failures"] else " — " + "; ".join(gate["failures"])),
                ]
                for gate in model["gates"]
            ],
        )
        + "\n## Self-guards\n\n"
        + table(
            ["Guard", "Findings", "Verdict"],
            [
                [key, str(len(values)), "PASS" if not values else "**FAIL**"]
                for key, values in sorted(model["guards"].items())
            ],
        )
        + "\n## Verified absence and the owner of each unblocking act\n\n"
        + table(
            ["Fact", "Bounds", "Blocked by", "Owner of the unblocking act"],
            [
                [
                    entry.get("fact") or "",
                    ", ".join(f"`{ref}`" for ref in as_list(entry.get("bounds"))) or "—",
                    entry.get("reason") or "",
                    f"`{entry.get('owner')}`",
                ]
                for entry in model["non_derivable"]
            ],
        )
        + "\n## Substrate\n\n"
        + table(
            ["Substrate", "Path", "Kind", "Tracked", "Parses", "Pointers", "Records"],
            [
                [
                    f"`{record['id']}`",
                    f"`{record['path']}`",
                    record["kind"],
                    "YES" if record["tracked"] else "**NO**",
                    "YES" if record["parses"] else "**NO**",
                    f"{len(record['pointers_resolved'])}/{len(record['pointers'])}",
                    str(record["records"]),
                ]
                for record in model["substrate"]
            ],
        )
        + (
            ""
            if not model["guard_findings"]
            else "\n## Guard findings\n\n"
            + "".join(f"- {finding}\n" for finding in model["guard_findings"])
        )
        + FOOTER
    )

    # ---- 16 non-derivable register
    body = header(title[16], decl, model, purpose[16])
    for entry in model["non_derivable"]:
        probe = derivation_by_id.get(str(entry.get("probe")))
        bounded = [by_id[str(ref)] for ref in as_list(entry.get("bounds")) if str(ref) in by_id]
        body += (
            f"## {entry.get('id')} — {entry.get('fact')}\n\n"
            f"- **Why it cannot be derived** — {entry.get('reason')}\n"
            "- **Evidence class that would be required** \u2014 "
            + f"{entry.get('required_evidence_class')}\n"
            f"- **Owner of the act that would supply it** — `{entry.get('owner')}`\n"
            f"- **Deliverable(s) it bounds** — "
            + (
                ", ".join(f"`{record['id']}` {record['name']}" for record in bounded)
                or "none declared"
            )
            + "\n\n"
            "**Counted probe**\n\n"
        )
        body += derivation_block(probe) if probe else "> Probe not computed.\n\n"
    out[name[16]] = (
        body
        + "## What is refused, and why that is the honest result\n\n"
        + "Each entry above is a fact this programme declines to fabricate. No body is written "
        + "for it, no row is invented, and no verdict is issued in its place. The probe measures "
        + "the absence so that the absence itself is Repository Truth, and the evidence class "
        + "names exactly what would have to exist — and who would have to author it — before the "
        + "fact could be derived at all.\n\n"
        + "Every chartered deliverable is nonetheless bound: no deliverable is wholly "
        + "unobtainable. What the register records is narrower and more precise — a bounded "
        + f"refusal **inside** {len(bounded_deliverable_ids(model))} "
        + "of the chartered deliverables, each naming the deliverable whose claim it caps. A "
        + "deliverable therefore reports what was measured and, where a refusal bounds it, "
        + "stops exactly there.\n"
        + FOOTER
    )

    # ---- 17 programme completion determination
    out[name[17]] = (
        header(title[17], decl, model, purpose[17])
        + "## Scope of this determination\n\n"
        + "This determination is about **this programme only**. It records that the chartered "
        + "deliverables are bound to Repository Truth. It does **not** claim that the repository "
        + "is complete, ratified, certified beyond its declared ceiling, or frozen — those are "
        + "verdicts for the authorities that own them, and one of them is declared vacant.\n\n"
        + "## Completion criteria\n\n"
        + table(
            ["Gate", "Name", "Blocking", "Verdict"],
            [
                [
                    f"`{gate['id']}`",
                    gate["name"],
                    "YES" if gate["blocking"] else "advisory",
                    f"**{gate['verdict']}**"
                    + ("" if not gate["failures"] else " — " + "; ".join(gate["failures"])),
                ]
                for gate in model["gates"]
            ],
        )
        + "\n## Deliverable binding\n\n"
        + table(DELIVERABLE_HEADERS, deliverable_rows(model["deliverables"]))
        + "\n## Work packages registered, not performed\n\n"
        + table(
            ["Work package", "Title", "Owner", "Authorization required", "Acceptance"],
            [
                [
                    f"`{entry.get('id')}`",
                    entry.get("title") or "",
                    f"`{entry.get('owner')}`",
                    "YES" if entry.get("authorization_required") else "no",
                    entry.get("acceptance") or "",
                ]
                for entry in model["work_packages"]
            ],
        )
        + "\n## Continuation package\n\n"
        + table(
            ["Element", "Value"],
            [
                ["Repository state source", f"`{decl['programme']['operational_memory_owner']}`"],
                ["Inherited resilience contract", f"`{decl['programme']['resilience_owner']}`"],
                [
                    "Roster binding",
                    f"`{decl['programme']['roster_binding']}` \u2014 "
                    + f"{decl['programme']['roster_binding_status']}",
                ],
                [
                    "Completed work",
                    f"{m['deliverables_bound']}/{m['deliverable_total']} chartered deliverables "
                    f"bound; {m['derivations_measured']}/{m['derivation_total']} derivations "
                    f"measured over {m['substrate_usable']} usable substrate(s); "
                    f"{m['non_derivable_total']} fact(s) declared non-derivable "
                    "with counted probes",
                ],
                [
                    "Remaining work",
                    f"{m['work_package_total']} registered work package(s), each requiring "
                    "authorization and an owner outside this programme; nothing blocking inside it",
                ],
                [
                    "Open issues",
                    ", ".join(f"`{entry.get('id')}`" for entry in model["non_derivable"]) or "none",
                ],
                [
                    "Architectural decisions",
                    "Reuse-first, zero-duplication, data-driven: no catalogue, registry, roadmap, "
                    "graph, sequence or authority was created; every fact is a pointer, a "
                    "derivation over declared substrate, or a counted absence",
                ],
                ["Determination", f"**{model['determination']}**"],
                ["Gate", f"**{model['gate']}**"],
                ["Seal", f"`{model['seal_sha256']}`"],
            ],
        )
        + FOOTER
    )
    return out


# ----------------------------------------------------------------------------- driver


def write_outputs(decl: dict, model: dict) -> list[Path]:
    written: list[Path] = []
    for filename, text in sorted(render(decl, model).items()):
        target = HERE / filename
        target.write_text(text, encoding="utf-8")
        written.append(target)
    model_path = HERE / MODEL_FILE
    model_path.write_text(canonical_json(model), encoding="utf-8")
    written.append(model_path)
    EVIDENCE_DIR.mkdir(exist_ok=True)
    index_path = EVIDENCE_DIR / EVIDENCE_INDEX
    index_path.write_text(
        canonical_json(
            {
                "substrate": model["substrate"],
                "derivations": [
                    {
                        "id": result["id"],
                        "primitive": result["primitive"],
                        "headline": result["headline"],
                        "count": result["count"],
                        "evidence": result["evidence"],
                        "unknown": result["unknown"],
                    }
                    for result in model["derivations"]
                ],
            }
        ),
        encoding="utf-8",
    )
    written.append(index_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", action="store_true")
    for flag in SELF_CHECKS:
        parser.add_argument(flag, action="store_true", dest=flag.lstrip("-").replace("-", "_"))
    args = parser.parse_args()

    decl = load_declaration()

    for flag, check in SELF_CHECKS.items():
        if getattr(args, flag.lstrip("-").replace("-", "_")):
            substrate = Substrate(decl)
            findings = check(decl, substrate)
            label = flag.lstrip("-")
            if findings:
                print(f"URRC-000001 {label}: FAIL")
                for finding in findings:
                    print(f"  - {finding}")
                return 1
            print(f"URRC-000001 {label}: PASS")
            return 0

    substrate = Substrate(decl)
    fatal = [
        finding
        for finding in substrate.findings()
        if "absent" in finding or "does not parse" in finding
    ]
    if fatal:
        fail_closed("; ".join(fatal))

    model = build_model(decl, substrate, repository_state())
    written = write_outputs(decl, model)
    scope = check_write_scope(decl, substrate, written)
    if scope:
        fail_closed("; ".join(scope))

    m = model["metrics"]
    print(
        f"URRC-000001: {model['determination']} | "
        f"deliverables={m['deliverables_bound']}/{m['deliverable_total']} | "
        f"substrate={m['substrate_usable']}/{m['substrate_total']} | "
        f"derivations={m['derivations_measured']}/{m['derivation_total']} | "
        f"gates={m['gates_passed']}/{m['gate_total']} | "
        f"unknown={m['non_derivable_total']} | "
        f"gate={model['gate']} | seal={model['seal_sha256'][:16]}"
    )
    if not args.gate:
        print(f"wrote {len(written)} artifacts to {HERE}")
        return 0
    if model["guard_findings"]:
        for finding in model["guard_findings"]:
            print(f"  - {finding}", file=sys.stderr)
    for gate in model["gates"]:
        if gate["blocking"] and gate["failures"]:
            print(
                f"  - {gate['id']} {gate['name']}: {'; '.join(gate['failures'])}",
                file=sys.stderr,
            )
    return model["gate_exit"]


if __name__ == "__main__":
    raise SystemExit(main())
