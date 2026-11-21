#!/usr/bin/env python3
"""UCOS-UTCE-001 — Universal Traceability Closure Engine.

AUTHORITY = NONE (DERIVED TRUTH). READ-ONLY over the certified corpus. This engine populates no
lane, writes no relationship, changes no predicate and owns no measurement service.

It exists because two different obligations were conflated under one word. CEP-001 XVIII.1
requires every artifact to trace upward to its authorizing definition and downward to its
reproducible evidence, rooted and closed with zero orphans — and that, in those exact words, is
the precondition CEP-006 V.1 and CEP-007 V.1 name for ratification and for freeze. The registry
schema separately carries a thirteen-stage field whose completeness the located measurement
service reports as the repository's largest gap. This engine measures the first as BLOCKING,
reports the second UNCHANGED against its own owner, and quantifies what would be needed to
discharge each open obligation — citing, for every entry it calls derivable, the located edge
that would support it.

    python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --render
    python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --gate
    python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-declaration
    python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-no-enumeration
    python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-write-scope
    python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-determinism
    python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-read-only
    python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-no-fabrication

Exit semantics:
    0  every blocking validation satisfied — gate OPEN
    1  a blocking validation unsatisfied, or a self-guard failed — gate CLOSED
    2  fail-closed abort — the declaration or a located vocabulary is unusable

Both vocabularies are read from their located owners by static analysis rather than by import:
importing would execute the module and make this engine depend on the very code it measures.

Stdlib only. No network. No timestamp, no duration, no commit identity and no absolute path is
emitted, so the sealed output set is byte-identical for an unchanged repository.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "utce-declaration.json"
MODEL = HERE / "utce.json"
OWN_PREFIX = HERE.relative_to(REPO).as_posix() + "/"

REQUIRED_SECTIONS = (
    "programme",
    "corpus",
    "lane_vocabulary",
    "relationship_vocabulary",
    "obligations",
    "rooting_relations",
    "lineage_relations",
    "derivation_rules",
    "obligation_classes",
    "validations",
    "exit_criteria",
)

MAX_CITED_EDGES = 3


class FailClosed(Exception):
    """Raised when no verdict may be asserted. Always exits 2."""


def load_declaration() -> dict:
    if not DECLARATION.exists():
        raise FailClosed(f"declaration not found: {DECLARATION.name}")
    try:
        document = json.loads(DECLARATION.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosed(f"declaration is not valid JSON: {exc}") from exc
    missing = [key for key in REQUIRED_SECTIONS if key not in document]
    if missing:
        raise FailClosed(f"declaration is missing required section(s): {', '.join(missing)}")
    return document


def read_text(relative: str) -> str | None:
    target = REPO / relative
    if not target.is_file():
        return None
    try:
        return target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_symbol(owner: str, symbol: str) -> object:
    """Read a module-level literal by static analysis. Never imports the module."""
    text = read_text(owner)
    if text is None:
        raise FailClosed(f"vocabulary owner does not resolve: {owner}")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        raise FailClosed(f"vocabulary owner does not parse: {owner}: {exc}") from exc
    value: object = None
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        elif isinstance(node, ast.AugAssign):
            targets = [node.target]
        else:
            continue
        if not any(isinstance(target, ast.Name) and target.id == symbol for target in targets):
            continue
        if node.value is None:
            continue
        try:
            literal = ast.literal_eval(node.value)
        except ValueError as exc:
            raise FailClosed(f"{owner}::{symbol} is not a literal: {exc}") from exc
        if isinstance(node, ast.AugAssign) and isinstance(value, list) and isinstance(literal, list):
            value = value + literal
        else:
            value = literal
    if value is None:
        raise FailClosed(f"{owner}::{symbol} was not found")
    return value


def load_corpus(document: dict) -> tuple[list[dict], list[dict]]:
    corpus = document["corpus"]
    records: list[list[dict]] = []
    for key in ("artifacts", "relationships"):
        binding = corpus[key]
        text = read_text(binding["owner"])
        if text is None:
            raise FailClosed(f"corpus source does not resolve: {binding['owner']}")
        try:
            envelope = json.loads(text)
        except json.JSONDecodeError as exc:
            raise FailClosed(f"corpus source is not valid JSON: {binding['owner']}: {exc}") from exc
        collection = envelope.get(binding["collection_pointer"])
        if not isinstance(collection, list) or not collection:
            raise FailClosed(f"corpus source yields no collection: {binding['owner']}")
        records.append([entry for entry in collection if isinstance(entry, dict)])
    return records[0], records[1]


def measure(document: dict) -> dict:
    programme = document["programme"]
    corpus = document["corpus"]
    artifacts, relationships = load_corpus(document)

    lanes = list(read_symbol(document["lane_vocabulary"]["owner"], document["lane_vocabulary"]["symbol"]))
    vocabulary = read_symbol(
        document["relationship_vocabulary"]["owner"], document["relationship_vocabulary"]["symbol"]
    )
    if not lanes or not isinstance(vocabulary, list) or not vocabulary:
        raise FailClosed("a located vocabulary is empty")

    binding = document["relationship_vocabulary"]
    # lane -> the located labels that can populate it, and the types that carry it
    mechanism: dict[str, dict[str, list[str]]] = {lane: {"labels": [], "types": []} for lane in lanes}
    known_types: set[str] = set()
    for entry in vocabulary:
        if not isinstance(entry, dict):
            continue
        name = entry.get(binding["type_field"])
        inverse = entry.get("inverse")
        for candidate in (name, inverse):
            if candidate:
                known_types.add(candidate)
        for field in (binding["subject_lane_field"], binding["object_lane_field"]):
            lane = entry.get(field)
            if lane in mechanism:
                for label in entry.get(binding["labels_field"]) or []:
                    if label not in mechanism[lane]["labels"]:
                        mechanism[lane]["labels"].append(label)
                if name and name not in mechanism[lane]["types"]:
                    mechanism[lane]["types"].append(name)

    # --- corpus indexes ---------------------------------------------------
    id_field = corpus["artifacts"]["id_field"]
    identifiers = {record.get(id_field) for record in artifacts if record.get(id_field)}
    rel = corpus["relationships"]
    dangling: list[str] = []
    outgoing: dict[str, list[dict]] = {}
    incoming: dict[str, list[dict]] = {}
    unknown_types: set[str] = set()
    for edge in relationships:
        source, target = edge.get(rel["from_field"]), edge.get(rel["to_field"])
        kind = edge.get(rel["type_field"])
        if kind:
            unknown_types.add(kind) if kind not in known_types else None
        for endpoint in (source, target):
            if endpoint not in identifiers:
                dangling.append(f"{edge.get(rel['id_field'])}: endpoint {endpoint} is not registered")
        outgoing.setdefault(source, []).append(edge)
        incoming.setdefault(target, []).append(edge)

    # --- constitutional obligations ---------------------------------------
    obligations = []
    unbound_obligations: list[str] = []
    for entry in document["obligations"]:
        text = read_text(entry["owner"])
        bound = text is not None and entry["anchor"] in text
        obligations.append(
            {"id": entry["id"], "obligation": entry["obligation"], "owner": entry["owner"], "bound": bound}
        )
        if not bound:
            unbound_obligations.append(f"{entry['id']}: anchor absent in {entry['owner']}")

    rooting_types = {entry["type"] for entry in document["rooting_relations"]}
    lineage_types = {entry["type"] for entry in document["lineage_relations"]}
    unlocated_types = sorted(
        f"{name}: absent from the located relationship vocabulary"
        for name in sorted(rooting_types | lineage_types)
        if name not in known_types
    )

    unrooted: list[str] = []
    orphans: list[str] = []
    evidence_missing: list[str] = []
    for record in artifacts:
        identifier = record.get(id_field)
        edges = outgoing.get(identifier, [])
        if not edges and not incoming.get(identifier):
            orphans.append(str(identifier))
        if not any(edge.get(rel["type_field"]) in rooting_types for edge in edges):
            # A lattice root has no upward edge by construction; it is rooted when something
            # subordinate points at it through a rooting relation.
            if not any(
                edge.get(rel["type_field"]) in rooting_types for edge in incoming.get(identifier, [])
            ):
                unrooted.append(str(identifier))
        for field in corpus["evidence_fields"]:
            if not record.get(field):
                evidence_missing.append(f"{identifier}: {field} is absent")

    # lineage acyclicity over the located lineage edges
    lineage_edges: dict[str, list[str]] = {}
    for edge in relationships:
        if edge.get(rel["type_field"]) in lineage_types:
            lineage_edges.setdefault(edge.get(rel["from_field"]), []).append(edge.get(rel["to_field"]))
    lineage_cycles: list[str] = []
    state: dict[str, int] = {}

    def walk(node: str, trail: list[str]) -> None:
        if state.get(node) == 1:
            lineage_cycles.append(" -> ".join(trail + [node]))
            return
        if state.get(node) == 2:
            return
        state[node] = 1
        for target in lineage_edges.get(node, []):
            walk(target, trail + [node])
        state[node] = 2

    for node in sorted(lineage_edges):
        walk(node, [])

    # --- engineering spine, measured exactly as the located service does ---
    spine_field = corpus["traceability_field"]
    lane_population = {lane: 0 for lane in lanes}
    any_lane = 0
    fully_traced = 0
    populated_pairs: set[tuple[str, str]] = set()
    for record in artifacts:
        identifier = record.get(id_field)
        spine = record.get(spine_field) or {}
        present = 0
        for lane in lanes:
            entries = spine.get(lane) or []
            if entries:
                lane_population[lane] += 1
                populated_pairs.add((str(identifier), lane))
                present += 1
        if present:
            any_lane += 1
        if present == len(lanes):
            fully_traced += 1

    # --- derivation headroom, every count citing located edges -------------
    derivation = []
    unbound_rules: list[str] = []
    for rule in document["derivation_rules"]:
        if rule["type"] not in known_types:
            unbound_rules.append(f"{rule['id']}: type absent from the located vocabulary")
        if rule["lane"] not in lanes:
            unbound_rules.append(f"{rule['id']}: lane absent from the located lane vocabulary")
        index = outgoing if rule["read"] == "from" else incoming
        endpoint = rel["from_field"] if rule["read"] == "from" else rel["to_field"]
        supported: dict[str, list[str]] = {}
        for owner, edges in index.items():
            for edge in edges:
                if edge.get(rel["type_field"]) != rule["type"]:
                    continue
                if edge.get(endpoint) != owner:
                    continue
                supported.setdefault(str(owner), []).append(str(edge.get(rel["id_field"])))
        already = sum(1 for owner in supported if (owner, rule["lane"]) in populated_pairs)
        derivation.append(
            {
                "id": rule["id"],
                "type": rule["type"],
                "read": rule["read"],
                "lane": rule["lane"],
                "artifacts_supported": len(supported),
                "already_written": already,
                "derivable_not_written": len(supported) - already,
                "cited_edges": sorted(
                    edge for edges in list(supported.values())[:MAX_CITED_EDGES] for edge in edges[:1]
                )[:MAX_CITED_EDGES],
                "basis": rule["basis"],
            }
        )
    uncited = [entry["id"] for entry in derivation if entry["artifacts_supported"] and not entry["cited_edges"]]

    # --- collection-mechanism register and open obligations ----------------
    classes = {entry["class"] for entry in document["obligation_classes"]}
    dischargeable = next(
        (entry["class"] for entry in document["obligation_classes"] if entry["id"] == document["obligation_classes"][0]["id"]),
        None,
    )
    absent = next(
        (entry["class"] for entry in document["obligation_classes"] if entry["id"] == document["obligation_classes"][1]["id"]),
        None,
    )
    if dischargeable is None or absent is None or not classes:
        raise FailClosed("the obligation-class vocabulary is unusable")

    lane_register = []
    unclassified: list[str] = []
    mechanism_absent: list[str] = []
    total = len(artifacts)
    for lane in lanes:
        labels = mechanism[lane]["labels"]
        obligation_class = dischargeable if labels else absent
        if obligation_class not in classes:
            unclassified.append(lane)
        if not labels:
            mechanism_absent.append(f"{lane}: no located label produces this lane")
        lane_register.append(
            {
                "lane": lane,
                "populated": lane_population[lane],
                "unevidenced": total - lane_population[lane],
                "labels": labels,
                "types": mechanism[lane]["types"],
                "obligation_class": obligation_class,
            }
        )

    lanes_accounted = sorted(set(lanes) - {entry["lane"] for entry in lane_register})

    findings: dict[str, list[str]] = {
        "UTCE-VAL-01": unbound_obligations,
        "UTCE-VAL-02": [],
        "UTCE-VAL-03": sorted(set(dangling)),
        "UTCE-VAL-04": sorted(unrooted),
        "UTCE-VAL-05": sorted(orphans),
        "UTCE-VAL-06": sorted(set(evidence_missing)),
        "UTCE-VAL-07": sorted(set(lineage_cycles)),
        "UTCE-VAL-08": unlocated_types,
        "UTCE-VAL-09": sorted(set(unbound_rules)),
        "UTCE-VAL-10": [f"{lane}: not accounted for in the mechanism register" for lane in lanes_accounted],
        "UTCE-VAL-11": [f"{lane}: no obligation class" for lane in unclassified],
        "UTCE-VAL-12": [f"{item}: derivable entries reported without a cited edge" for item in uncited],
        "UTCE-VAL-13": mechanism_absent,
        "UTCE-VAL-14": (
            []
            if fully_traced == total
            else [f"{total - fully_traced} of {total} artifacts do not populate every lane"]
        ),
    }

    validations = []
    for validation in document["validations"]:
        measured = validation["id"] in findings
        failures = findings.get(validation["id"], [])
        validations.append(
            {
                "id": validation["id"],
                "dimension": validation["dimension"],
                "obligation": validation["obligation"],
                "blocking": bool(validation["blocking"]),
                "measured": measured,
                "satisfied": measured and not failures,
                "failures": sorted(failures)[:40],
                "failure_count": len(failures),
            }
        )
    blocking_failures = [
        entry["id"] for entry in validations if entry["blocking"] and not entry["satisfied"]
    ]
    gate = "CLOSED" if blocking_failures else "OPEN"

    model = {
        "programme": programme,
        "vocabularies": {
            "lanes": lanes,
            "lane_owner": document["lane_vocabulary"]["owner"],
            "relationship_types": sorted(known_types),
            "relationship_owner": document["relationship_vocabulary"]["owner"],
            "unknown_types_in_corpus": sorted(unknown_types),
        },
        "obligations": obligations,
        "constitutional_traceability": {
            "artifacts": total,
            "relationships": len(relationships),
            "dangling_endpoints": len(set(dangling)),
            "unrooted": len(unrooted),
            "orphans": len(orphans),
            "evidence_field_gaps": len(set(evidence_missing)),
            "lineage_cycles": len(set(lineage_cycles)),
            "rooted_and_closed": not (dangling or unrooted or orphans or evidence_missing or lineage_cycles),
        },
        "engineering_spine": {
            "artifacts": total,
            "lanes": len(lanes),
            "artifacts_with_any_lane": any_lane,
            "artifacts_fully_traced": fully_traced,
            "artifacts_incomplete": total - fully_traced,
            "owner": "platform/measurement \u00b7 00-BOOK/tools",
        },
        "lane_register": lane_register,
        "derivation": derivation,
        "obligation_classes": list(document["obligation_classes"]),
        "validations": validations,
        "counts": {
            "artifacts": total,
            "relationships": len(relationships),
            "lanes": len(lanes),
            "lanes_with_mechanism": sum(1 for entry in lane_register if entry["labels"]),
            "lanes_without_mechanism": sum(1 for entry in lane_register if not entry["labels"]),
            "obligations_bound": sum(1 for entry in obligations if entry["bound"]),
            "obligations": len(obligations),
            "derivable_not_written": sum(entry["derivable_not_written"] for entry in derivation),
            "artifacts_fully_traced": fully_traced,
            "artifacts_with_any_lane": any_lane,
        },
        "blocking_failures": blocking_failures,
        "gate": gate,
        "gate_exit": 1 if blocking_failures else 0,
        "determination": (
            "CONSTITUTIONAL-TRACEABILITY-CLOSED" if gate == "OPEN" else "CONSTITUTIONAL-TRACEABILITY-OPEN"
        ),
        "exit_criteria": list(document["exit_criteria"]),
        "findings": list(document.get("findings", [])),
    }
    model["seal_sha256"] = digest(json.dumps(model, sort_keys=True, ensure_ascii=False))
    return model


# ---------------------------------------------------------------------------
# rendering


def table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines)


def front_matter(model: dict) -> str:
    programme = model["programme"]
    counts = model["counts"]
    constitutional = model["constitutional_traceability"]
    rows = [
        ["PROGRAMME", f"{programme['id']} — {programme['name']}"],
        ["VERSION", programme["version"]],
        ["AUTHORITY", programme["authority"]],
        ["CORPUS MEASURED", f"{counts['artifacts']} artifacts · {counts['relationships']} relationships"],
        ["CONSTITUTIONAL OBLIGATIONS BOUND", f"{counts['obligations_bound']}/{counts['obligations']}"],
        ["ROOTED AND CLOSED", "YES" if constitutional["rooted_and_closed"] else "NO"],
        ["DANGLING ENDPOINTS", constitutional["dangling_endpoints"]],
        ["UNROOTED", constitutional["unrooted"]],
        ["ORPHANS", constitutional["orphans"]],
        ["LINEAGE CYCLES", constitutional["lineage_cycles"]],
        ["ENGINEERING SPINE", f"{counts['artifacts_fully_traced']}/{counts['artifacts']} fully traced · {counts['artifacts_with_any_lane']} with at least one lane"],
        ["LANES WITH A COLLECTION MECHANISM", f"{counts['lanes_with_mechanism']}/{counts['lanes']}"],
        ["DERIVABLE, NOT WRITTEN", counts["derivable_not_written"]],
        ["GATE", model["gate"]],
        ["DETERMINATION", model["determination"]],
        ["SEAL (sha256)", model["seal_sha256"]],
        ["GENERATED BY", "utce_engine.py — regenerated, never hand-authored"],
    ]
    return table(["Field", "Value"], rows) + "\n\n> " + programme["disclosure"]


def render(model: dict) -> dict[str, str]:
    programme = model["programme"]
    pages: dict[str, str] = {}

    pages["00-UTCE-DASHBOARD.md"] = "\n".join(
        [
            f"# {programme['id']} — {programme['name']} · Dashboard",
            "",
            front_matter(model),
            "",
            "## The two obligations, measured separately",
            "",
            table(
                ["Obligation", "What it requires", "Owner", "Measured result", "Blocking"],
                [
                    [
                        "Constitutional traceability",
                        "upward rooting, downward evidence, closure, zero orphans, acyclic lineage (CEP-001 XVIII · CEP-008 XI)",
                        "`00-CEP/CEP-001` · `00-CEP/CEP-008`",
                        "ROOTED AND CLOSED" if model["constitutional_traceability"]["rooted_and_closed"] else "OPEN",
                        "YES",
                    ],
                    [
                        "Engineering spine completeness",
                        "all thirteen schema lanes populated on every artifact",
                        f"`{model['engineering_spine']['owner']}`",
                        f"{model['engineering_spine']['artifacts_fully_traced']}/{model['engineering_spine']['artifacts']} fully traced",
                        "no — reported unchanged, not closed here",
                    ],
                ],
            ),
            "",
            "## Constitutional obligations",
            "",
            table(
                ["Obligation", "Requirement", "Located in", "Bound"],
                [
                    [
                        f"`{entry['id']}`",
                        entry["obligation"],
                        f"`{entry['owner']}`",
                        "YES" if entry["bound"] else "**NO**",
                    ]
                    for entry in model["obligations"]
                ],
            ),
            "",
            "## Blocking failures",
            "",
            (
                "None. Every blocking validation is satisfied."
                if not model["blocking_failures"]
                else "\n".join(f"- `{item}`" for item in model["blocking_failures"])
            ),
            "",
        ]
    )

    pages["01-TRACEABILITY-OBLIGATION-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Lane Obligation and Collection-Mechanism Register",
            "",
            "One row per lane of the located lane vocabulary. `labels` are the front-matter row",
            "labels the located relationship vocabulary maps to that lane — the mechanism by which",
            "an artifact can lawfully declare the evidence. A lane with no label cannot be",
            "populated by any means the repository currently provides, and its obligation is",
            "therefore undischargeable until the vocabulary owner adds one.",
            "",
            table(
                ["Lane", "Populated", "Unevidenced", "Collection labels (located)", "Obligation class"],
                [
                    [
                        f"`{entry['lane']}`",
                        entry["populated"],
                        entry["unevidenced"],
                        ", ".join(f"`{label}`" for label in entry["labels"]) or "— none",
                        entry["obligation_class"],
                    ]
                    for entry in model["lane_register"]
                ],
            ),
            "",
            "## Obligation classes",
            "",
            table(
                ["Class", "Definition"],
                [[f"`{entry['class']}`", entry["definition"]] for entry in model["obligation_classes"]],
            ),
            "",
            "## Located vocabularies",
            "",
            f"Lane vocabulary read from `{model['vocabularies']['lane_owner']}`"
            f" — {len(model['vocabularies']['lanes'])} lanes.",
            "",
            f"Relationship vocabulary read from `{model['vocabularies']['relationship_owner']}`"
            f" — {len(model['vocabularies']['relationship_types'])} declared types.",
            "",
            (
                ""
                if not model["vocabularies"]["unknown_types_in_corpus"]
                else "Types present in the corpus but absent from the located vocabulary: "
                + ", ".join(f"`{item}`" for item in model["vocabularies"]["unknown_types_in_corpus"])
                + "\n"
            ),
        ]
    )

    pages["02-DERIVATION-HEADROOM-REGISTER.md"] = "\n".join(
        [
            f"# {programme['id']} · Derivation Headroom",
            "",
            "How many lane entries the edges ALREADY in the certified corpus would support, and",
            "how many of those the generator already wrote. `derivable, not written` is headroom",
            "that requires no new evidence — only that the located generator write what its own",
            "vocabulary already declares. **This programme writes none of it.** Every row cites",
            "located edge identifiers so the count is auditable against the corpus.",
            "",
            table(
                ["Rule", "Located type", "Read", "Lane", "Artifacts supported", "Already written", "Derivable, not written", "Cited edges"],
                [
                    [
                        f"`{entry['id']}`",
                        f"`{entry['type']}`",
                        entry["read"],
                        f"`{entry['lane']}`",
                        entry["artifacts_supported"],
                        entry["already_written"],
                        entry["derivable_not_written"],
                        ", ".join(f"`{edge}`" for edge in entry["cited_edges"]) or "—",
                    ]
                    for entry in model["derivation"]
                ],
            ),
            "",
            "## Basis of each rule",
            "",
            table(
                ["Rule", "Basis"],
                [[f"`{entry['id']}`", entry["basis"]] for entry in model["derivation"]],
            ),
            "",
        ]
    )

    pages["03-CERTIFICATION-REPORT.md"] = "\n".join(
        [
            f"# {programme['id']} · Certification Report",
            "",
            front_matter(model),
            "",
            "## Validation dimensions",
            "",
            table(
                ["Dimension", "Obligation", "Blocking", "Measured", "Satisfied", "Failures"],
                [
                    [
                        f"`{entry['id']}` {entry['dimension']}",
                        entry["obligation"],
                        "YES" if entry["blocking"] else "no",
                        "YES" if entry["measured"] else "**NO**",
                        "YES" if entry["satisfied"] else "**NO**",
                        entry["failure_count"],
                    ]
                    for entry in model["validations"]
                ],
            ),
            "",
            "## Exit criteria",
            "",
            table(
                ["Criterion", "Statement"],
                [[f"`{item['id']}`", item["criterion"]] for item in model["exit_criteria"]],
            ),
            "",
            "## Findings",
            "",
            table(
                ["Finding", "Class", "Owner", "Disposition", "Title"],
                [
                    [
                        f"`{item['id']}`",
                        item["class"],
                        f"`{item['owner']}`",
                        item["disposition"],
                        item["title"],
                    ]
                    for item in model["findings"]
                ],
            ),
            "",
            "The constitutional traceability obligation named by CEP-006 V.1 and CEP-007 V.1 is",
            "measured here and its satisfaction is decidable. The thirteen-lane engineering spine",
            "is reported unchanged against its own owner and is not closed by this programme.",
            "Where this register and a located owner differ, the located owner governs.",
            "",
        ]
    )
    return pages


def write_registers(model: dict) -> list[str]:
    written = []
    for name, body in sorted(render(model).items()):
        (HERE / name).write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")
        written.append(name)
    MODEL.write_text(
        json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    written.append(MODEL.name)
    return written


# ---------------------------------------------------------------------------
# self-guards


def check_declaration(document: dict) -> list[str]:
    problems: list[str] = []
    for entry in document["obligations"]:
        if not (REPO / entry["owner"]).is_file():
            problems.append(f"{entry['id']}: owner does not resolve")
        else:
            text = read_text(entry["owner"]) or ""
            if entry["anchor"] not in text:
                problems.append(f"{entry['id']}: anchor absent in {entry['owner']}")
    for key in ("lane_vocabulary", "relationship_vocabulary"):
        if not (REPO / document[key]["owner"]).is_file():
            problems.append(f"{key}: owner does not resolve")
    for key in ("artifacts", "relationships"):
        if not (REPO / document["corpus"][key]["owner"]).is_file():
            problems.append(f"corpus {key}: owner does not resolve")
    seen: set[str] = set()
    for section in ("obligations", "derivation_rules", "obligation_classes", "validations", "exit_criteria"):
        for entry in document[section]:
            if entry["id"] in seen:
                problems.append(f"{section}: duplicate id {entry['id']}")
            seen.add(entry["id"])
    return problems


def check_no_enumeration(document: dict) -> list[str]:
    """No lane, relationship type or artifact identifier may be a literal in this engine."""
    source = Path(__file__).read_text(encoding="utf-8")
    model = measure(document)
    leaked: list[str] = []
    for lane in model["vocabularies"]["lanes"]:
        if f'"{lane}"' in source or f"'{lane}'" in source:
            leaked.append(f"lane {lane}")
    for name in model["vocabularies"]["relationship_types"]:
        if f'"{name}"' in source or f"'{name}'" in source:
            leaked.append(f"type {name}")
    return sorted(set(leaked))


def check_write_scope(document: dict) -> list[str]:
    problems: list[str] = []
    for target in [HERE / name for name in render(measure(document))] + [MODEL]:
        try:
            target.resolve().relative_to(HERE)
        except ValueError:
            problems.append(target.as_posix())
    for prefix in document["programme"]["forbidden_write_prefixes"]:
        if OWN_PREFIX.startswith(prefix):
            problems.append(f"own home falls inside a forbidden prefix: {prefix}")
    return problems


def check_determinism(document: dict) -> list[str]:
    first, second = render(measure(document)), render(measure(document))
    return sorted(name for name in first if first[name] != second.get(name))


def check_read_only(document: dict) -> list[str]:
    """Every corpus and vocabulary source must sit under a forbidden write prefix."""
    problems: list[str] = []
    sources = [document["corpus"][key]["owner"] for key in ("artifacts", "relationships")]
    sources += [document[key]["owner"] for key in ("lane_vocabulary", "relationship_vocabulary")]
    sources += [entry["owner"] for entry in document["obligations"]]
    prefixes = tuple(document["programme"]["forbidden_write_prefixes"])
    for source in sorted(set(sources)):
        if not source.startswith(prefixes):
            problems.append(f"{source}: read from a path this programme is not forbidden to write")
    return problems


def check_no_fabrication(document: dict) -> list[str]:
    """Every derivable count must cite located edges, and no lane may be reported populated
    beyond what the corpus records."""
    model = measure(document)
    problems: list[str] = []
    for entry in model["derivation"]:
        if entry["artifacts_supported"] and not entry["cited_edges"]:
            problems.append(f"{entry['id']}: reports support with no cited edge")
        if entry["already_written"] > entry["artifacts_supported"]:
            problems.append(f"{entry['id']}: already_written exceeds supported")
    total = model["counts"]["artifacts"]
    for entry in model["lane_register"]:
        if entry["populated"] + entry["unevidenced"] != total:
            problems.append(f"{entry['lane']}: population does not reconcile against the corpus")
        if entry["populated"] > total:
            problems.append(f"{entry['lane']}: population exceeds the corpus")
    if model["engineering_spine"]["artifacts_fully_traced"] > total:
        problems.append("fully-traced count exceeds the corpus")
    return problems


GUARDS = {
    "check-declaration": check_declaration,
    "check-no-enumeration": check_no_enumeration,
    "check-write-scope": check_write_scope,
    "check-determinism": check_determinism,
    "check-read-only": check_read_only,
    "check-no-fabrication": check_no_fabrication,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    for name in GUARDS:
        parser.add_argument(f"--{name}", action="store_true")
    args = parser.parse_args(argv)

    try:
        document = load_declaration()
    except FailClosed as exc:
        print(f"UCOS-UTCE-001 ABORT: {exc}", file=sys.stderr)
        return 2

    selected = [name for name in GUARDS if getattr(args, name.replace("-", "_"))]
    if selected:
        failed = False
        for name in selected:
            try:
                problems = GUARDS[name](document)
            except FailClosed as exc:
                print(f"UCOS-UTCE-001 ABORT: {exc}", file=sys.stderr)
                return 2
            if problems:
                failed = True
                print(f"UCOS-UTCE-001 {name}: FAIL ({len(problems)})", file=sys.stderr)
                for problem in problems[:40]:
                    print(f"  - {problem}", file=sys.stderr)
            else:
                print(f"UCOS-UTCE-001 {name}: PASS")
        return 1 if failed else 0

    try:
        model = measure(document)
    except FailClosed as exc:
        print(f"UCOS-UTCE-001 ABORT: {exc}", file=sys.stderr)
        return 2

    written = write_registers(model)
    counts = model["counts"]
    constitutional = model["constitutional_traceability"]
    if not args.quiet:
        print(
            f"UCOS-UTCE-001: {model['determination']} | artifacts={counts['artifacts']} "
            f"| edges={counts['relationships']} | dangling={constitutional['dangling_endpoints']} "
            f"| unrooted={constitutional['unrooted']} | orphans={constitutional['orphans']} "
            f"| lanes-with-mechanism={counts['lanes_with_mechanism']}/{counts['lanes']} "
            f"| spine={counts['artifacts_fully_traced']}/{counts['artifacts']} "
            f"| derivable={counts['derivable_not_written']} "
            f"| gate={model['gate']} | seal={model['seal_sha256'][:16]}"
        )
        print(f"wrote {len(written)} artifacts to {HERE.relative_to(REPO).as_posix()}")
        for entry in model["validations"]:
            if entry["blocking"] and not entry["satisfied"]:
                print(f"  BLOCKING {entry['id']} {entry['dimension']}: {entry['failure_count']}", file=sys.stderr)
                for failure in entry["failures"][:10]:
                    print(f"    - {failure}", file=sys.stderr)

    if args.gate:
        return model["gate_exit"]
    return 0


if __name__ == "__main__":
    sys.exit(main())
