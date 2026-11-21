#!/usr/bin/env python3
"""UIS-001 — Universal Identity System Conformance.

AUTHORITY = NONE (DERIVED TRUTH). This engine mints no identity, allocates no
identifier, declares no namespace, defines no grammar, opens no registry and
legislates no lifecycle. It reads the identity architecture the repository has
already legislated (AIF, ENG-001, UMB-003/004/005/008/009/010, AUTH-INF-001) and
the identity data the repository has already recorded (the append-only identity
ledger and the derived artifact registry), and reports what they say.

Everything it enforces is read from ``uis-declaration.json``. This source file
contains no universal identifier, no category namespace, no ledger path and no
discovered family name: adding a capability, a law, a plane, a mechanism, a
bookkeeping obligation or an unboundedness dimension is an append-only edit to
that DATA file and requires no change here (PR-07 Zero Enumeration).

Determinism (AIF-L18): the output is a pure function of tracked repository
content. Nothing here reads the wall clock, the commit identity (RFP-2) or the
working tree's own status (RFP-3), so the emitted bytes are stable and the
repository can remain a fixed point.

Exit semantics:
  0  gate OPEN / guard PASS
  1  gate CLOSED / guard FAIL
  2  fail-closed abort — the declaration is unusable, so no verdict may be asserted
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "uis-declaration.json"
MODEL = HERE / "uis.json"
OWN_PREFIX = HERE.relative_to(REPO).as_posix() + "/"

REQUIRED_SECTIONS = (
    "programme",
    "determination",
    "identity_planes",
    "identity_mechanisms",
    "realization_obligation",
    "ledger_source",
    "registry_source",
    "grammar_source",
    "classification_authority",
    "namespace_governance",
    "facet_authority",
    "lifecycle",
    "laws",
    "law_source",
    "bookkeeping_obligations",
    "hygiene",
    "unboundedness",
    "capabilities",
    "record_set",
    "validations",
    "exit_criteria",
    "findings",
)

PAGES = (
    "00-IDENTITY-CONFORMANCE-DASHBOARD.md",
    "01-IDENTITY-CAPABILITY-MAPPING-MATRIX.md",
    "02-IDENTITY-LAW-BINDING-REGISTER.md",
    "03-IDENTITY-PLANE-AND-GRAMMAR-REGISTER.md",
    "04-IDENTITY-LEDGER-MEASUREMENT-REGISTER.md",
    "05-UNBOUNDEDNESS-AND-SELF-DESCRIPTION-REGISTER.md",
    "06-VALIDATION-REPORT.md",
    "07-CERTIFICATION-REPORT.md",
    "08-ADMISSION-AND-DISPOSITION-DETERMINATION.md",
)

STATUS_EXISTING = "EXISTING"
STATUS_PARTIAL = "PARTIAL"
STATUS_MISSING = "MISSING"
ACTION_CREATE = "CREATE"
NOT_MEASURABLE = "DECLARED-NOT-MEASURABLE"


class FailClosed(Exception):
    """Raised when no verdict may be asserted."""


# --------------------------------------------------------------------------- inputs


def load_declaration() -> dict:
    if not DECLARATION.is_file():
        raise FailClosed(f"declaration is absent: {DECLARATION.name}")
    try:
        document = json.loads(DECLARATION.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosed(f"declaration is not valid JSON: {exc}") from exc
    missing = [name for name in REQUIRED_SECTIONS if name not in document]
    if missing:
        raise FailClosed(f"declaration is missing required sections: {', '.join(missing)}")
    return document


def read_text(relative: str) -> str | None:
    target = REPO / relative
    if not target.is_file():
        return None
    try:
        return target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):  # pragma: no cover - defensive
        return None


def read_json(relative: str) -> Any:
    raw = read_text(relative)
    if raw is None:
        raise FailClosed(f"a declared source does not resolve: {relative}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FailClosed(f"a declared source is not valid JSON: {relative}: {exc}") from exc


def load_classification(document: dict) -> Any:
    """Import the located classification authority as a module.

    The authority is Python, and its rules are the values this measurement reads.
    Reading them by import rather than by text keeps the reading faithful to what
    the allocator itself sees.
    """
    relative = document["classification_authority"]["owner"]
    target = REPO / relative
    if not target.is_file():
        raise FailClosed(f"the classification authority does not resolve: {relative}")
    parent = str(target.parent)
    inserted = parent not in sys.path
    if inserted:
        sys.path.insert(0, parent)
    try:
        spec = importlib.util.spec_from_file_location(f"_uis_{target.stem}", target)
        if spec is None or spec.loader is None:  # pragma: no cover - defensive
            raise FailClosed(f"the classification authority is not importable: {relative}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except FailClosed:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise FailClosed(f"the classification authority failed to load: {relative}: {exc}") from exc
    finally:
        if inserted and parent in sys.path:
            sys.path.remove(parent)


def symbol_present(relative: str, symbol: str) -> bool:
    """Is ``symbol`` defined in the located module?

    Measured over SOURCE TEXT, never by importing: an engine module may carry
    dependencies this measurement has no business loading, and a definition is a
    textual fact.
    """
    source = read_text(relative)
    if source is None:
        return False
    pattern = re.compile(
        rf"^\s*(?:def\s+{re.escape(symbol)}\b"
        rf"|class\s+{re.escape(symbol)}\b"
        rf"|{re.escape(symbol)}\s*[:=])",
        re.MULTILINE,
    )
    return bool(pattern.search(source))


def collect_field_space(payload: Any) -> tuple[set[str], set[str]]:
    """The field names a located JSON source ITSELF carries, at its two natural depths.

    A bookkeeping obligation names a *field*, and a field is answered either by the
    document as a whole or by each entry the document records. Those are the only two
    depths the located sources use: the recorded plane answers ``history`` once for the
    whole ledger and ``first_seen`` once per recorded path, and the derived plane
    answers every obligation per registered entry.

    Nothing is enumerated here: the key space is READ from whatever the located source
    contains, so adding a field to a source, or an obligation to the declaration, needs
    no change in this module (PR-07 Zero Enumeration).
    """
    document_fields: set[str] = set()
    entry_fields: set[str] = set()
    if isinstance(payload, dict):
        document_fields |= {str(key) for key in payload}
        containers: Any = list(payload.values())
    elif isinstance(payload, list):
        containers = list(payload)
    else:
        return document_fields, entry_fields
    for container in containers:
        entries: Any
        if isinstance(container, dict):
            entries = list(container.values())
        elif isinstance(container, list):
            entries = list(container)
        else:
            continue
        for entry in entries:
            if isinstance(entry, dict):
                entry_fields |= {str(key) for key in entry}
    return document_fields, entry_fields


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def getattr_path(module: Any, symbol: str) -> Any:
    return getattr(module, symbol, None)


# --------------------------------------------------------------------------- identity plane readings


def parse_identity(value: str, pattern: re.Pattern[str]) -> tuple[str | None, int | None, bool]:
    """Split a located identity into its namespace and ordinal segments."""
    ok = bool(pattern.match(value))
    parts = value.split("-")
    if len(parts) < 3:
        return None, None, ok
    namespace = "-".join(parts[1:-1])
    tail = parts[-1]
    ordinal = int(tail) if tail.isdigit() else None
    return namespace, ordinal, ok


def measure_ledger(document: dict, config: Any) -> dict:  # noqa: C901 - one reading per law
    """Read the RECORDED identity plane and the DERIVED registry plane."""
    ledger_decl = document["ledger_source"]
    registry_decl = document["registry_source"]
    grammar_decl = document["grammar_source"]
    classify = document["classification_authority"]

    ledger = read_json(ledger_decl["owner"])
    registry = read_json(registry_decl["owner"])
    schema = read_json(grammar_decl["owner"])

    by_path = ledger.get(ledger_decl["path_map"]) or {}
    history = ledger.get(ledger_decl["history_map"]) or {}
    sequences = ledger.get(ledger_decl["sequence_map"]) or {}
    records = registry.get(registry_decl["collection"]) or []
    if not by_path or not records:
        raise FailClosed("the located identity sources carry no entries, so nothing may be asserted")

    pointer = grammar_decl["pointer"].split(".")
    node: Any = schema
    for step in pointer:
        node = (node or {}).get(step) if isinstance(node, dict) else None
    if not isinstance(node, str):
        raise FailClosed("the declared identity grammar does not resolve in its owner")
    grammar = re.compile(node)

    id_field = ledger_decl["identity_field"]
    cat_field = ledger_decl["category_field"]
    seq_field = ledger_decl["sequence_field"]
    r_id = registry_decl["identity_field"]
    r_path = registry_decl["path_field"]

    excluded = tuple(getattr_path(config, classify["exclusion_symbol"]) or ())

    # ---- recorded plane
    identity_to_paths: dict[str, set[str]] = {}
    for path in sorted(by_path):
        entry = by_path[path] or {}
        identity = str(entry.get(id_field) or "")
        identity_to_paths.setdefault(identity, set()).add(path)

    collisions = sorted(k for k, v in identity_to_paths.items() if len(v) > 1)
    unresolvable = sorted(p for p in by_path if not (REPO / p).is_file())
    nonsource = sorted(p for p in by_path if excluded and p.startswith(excluded))

    # UIL-04/07/19: the recorded namespace segment must equal the recorded category,
    # and the identity must satisfy the grammar its owner declares.
    grammar_failures: list[str] = []
    attribute_coupled: list[str] = []
    ordinals: dict[str, set[int]] = {}
    renumbered: list[str] = []
    for path in sorted(by_path):
        entry = by_path[path] or {}
        identity = str(entry.get(id_field) or "")
        namespace, ordinal, ok = parse_identity(identity, grammar)
        if not ok:
            grammar_failures.append(identity)
        recorded_category = str(entry.get(cat_field) or "")
        if namespace is not None and recorded_category and namespace != recorded_category:
            attribute_coupled.append(identity)
        if namespace is not None and ordinal is not None:
            seen = ordinals.setdefault(namespace, set())
            if ordinal in seen:
                renumbered.append(identity)
            seen.add(ordinal)

    # UIL-13: every recorded history is a contiguous append-only sequence from one.
    history_breaks: list[str] = []
    altered: list[str] = []
    for identity in sorted(history):
        events = history[identity] or []
        steps = [event.get(seq_field) for event in events]
        if steps != list(range(1, len(steps) + 1)):
            history_breaks.append(identity)
        if identity not in identity_to_paths:
            altered.append(identity)

    # ---- derived plane
    absent_identity = [str(rec.get(r_path) or "?") for rec in records if not rec.get(r_id)]
    path_to_ids: dict[str, set[str]] = {}
    for rec in records:
        path = str(rec.get(r_path) or "")
        if path:
            path_to_ids.setdefault(path, set()).add(str(rec.get(r_id) or ""))
    multiple = sorted(p for p, ids in path_to_ids.items() if len(ids) > 1)

    recorded_ids = {str((by_path[p] or {}).get(id_field) or "") for p in by_path}
    registry_ids = {str(rec.get(r_id) or "") for rec in records}
    derived_absent = sorted(i for i in registry_ids if i and i not in recorded_ids)

    # UIL-09 reference integrity
    parent_field = registry_decl["parent_field"]
    dep_field = registry_decl["dependency_field"]
    dangling: list[str] = []
    for rec in records:
        parent = rec.get(parent_field)
        if parent and str(parent) not in registry_ids:
            dangling.append(f"{rec.get(r_id)} -> {parent}")
        for dep in rec.get(dep_field) or []:
            if str(dep) not in registry_ids:
                dangling.append(f"{rec.get(r_id)} -> {dep}")

    # UIL-10 traceability, UIL-14 verifiability
    untraceable: list[str] = []
    unverifiable: list[str] = []
    for rec in records:
        for key in ("owner_field", "program_field", "category_field"):
            if not rec.get(registry_decl[key]):
                untraceable.append(str(rec.get(r_id) or "?"))
                break
        if not rec.get(registry_decl["content_field"]):
            unverifiable.append(str(rec.get(r_id) or "?"))

    # UIL-12 lifecycle
    lifecycle_symbol = document["lifecycle"]["status_symbol"]
    declared_states: set[str] = set()
    for item in getattr_path(config, lifecycle_symbol) or ():
        if isinstance(item, (list, tuple)) and item:
            declared_states.add(str(item[-1]))
        else:
            declared_states.add(str(item))
    used_states = {str(rec.get(registry_decl["status_field"])) for rec in records if rec.get(registry_decl["status_field"])}
    undeclared_states = sorted(used_states - declared_states)

    # UIL-15 / UIL-17 hygiene
    hygiene = document["hygiene"]
    indicators = [str(t).lower() for t in hygiene["secret_indicators"]]
    exempt = {str(f).lower() for f in hygiene["secret_exempt_fields"]}
    secret_hits: list[str] = []
    for rec in records:
        for key in rec:
            low = str(key).lower()
            if low in exempt:
                continue
            if any(token in low for token in indicators):
                secret_hits.append(f"{rec.get(r_id)}::{key}")
    tokens = [str(t).upper() for t in hygiene["authority_tokens"]]
    fields = [str(f) for f in hygiene["authority_fields"]]
    authority_hits: list[str] = []
    for rec in records:
        for field in fields:
            value = str(rec.get(field) or "").upper()
            if any(token in value for token in tokens):
                authority_hits.append(f"{rec.get(r_id)}::{field}")

    # ---- namespace governance
    declared_namespaces: set[str] = set()
    rules = getattr_path(config, classify["rule_symbol"]) or ()
    index = int(classify["rule_category_index"])
    for rule in rules:
        if isinstance(rule, (list, tuple)) and len(rule) > index:
            declared_namespaces.add(str(rule[index]))
    declared_namespaces |= set(getattr_path(config, classify["family_symbol"]) or {})
    volumes = getattr_path(config, classify["volume_symbol"]) or ()
    v_index = int(classify["volume_code_index"])
    for volume in volumes:
        if isinstance(volume, (list, tuple)) and len(volume) > v_index:
            declared_namespaces.add(str(volume[v_index]))
    for key in ("derived_default_symbol", "execution_category_symbol"):
        value = getattr_path(config, classify[key])
        if isinstance(value, str):
            declared_namespaces.add(value)
        elif value:
            declared_namespaces |= {str(item) for item in value}
    execution_default = getattr_path(config, "EXECUTION_DEFAULT_CATEGORY")
    if isinstance(execution_default, str):
        declared_namespaces.add(execution_default)

    live_namespaces = sorted(n for n, count in sequences.items() if isinstance(count, int) and count > 0)
    ungoverned = sorted(set(live_namespaces) - declared_namespaces)

    # UIL-16 / UNB-01: partition ambiguity and formatting capacity
    width = getattr_path(config, classify["derived_width_symbol"])
    width = int(width) if isinstance(width, int) else 0
    buckets: dict[str, set[str]] = {}
    if width > 0:
        for namespace in live_namespaces:
            buckets.setdefault(namespace[:width], set()).add(namespace)
    ambiguous = {k: sorted(v) for k, v in buckets.items() if len(v) > 1}
    ambiguity_excess = sum(len(v) - 1 for v in ambiguous.values())

    ordinal_width = 0
    match = re.search(r"\[0-9\]\{(\d+)\}", node)
    if match:
        ordinal_width = int(match.group(1))
    capacity = 10**ordinal_width if ordinal_width else 0
    fraction = float(document["unboundedness"]["capacity_threshold_fraction"])
    near: list[dict] = []
    peak = {"namespace": None, "used": 0, "fraction": 0.0}
    for namespace in live_namespaces:
        used = int(sequences.get(namespace) or 0)
        share = (used / capacity) if capacity else 1.0
        if share > peak["fraction"]:
            peak = {"namespace": namespace, "used": used, "fraction": share}
        if capacity and share >= fraction:
            near.append({"namespace": namespace, "used": used, "fraction": share})

    return {
        "grammar": node,
        "counts": {
            "recorded_identities": len(by_path),
            "recorded_histories": len(history),
            "registered_identities": len(records),
            "live_namespaces": len(live_namespaces),
            "declared_namespaces": len(declared_namespaces),
            "namespace_capacity": capacity,
            "namespace_width": width,
        },
        "peak_namespace": peak,
        "near_capacity": near,
        "ambiguous_namespaces": ambiguous,
        "ungoverned_namespaces": ungoverned,
        "nonsource_admissions": nonsource,
        "unresolvable": unresolvable,
        "measures": {
            "identities_absent": len(absent_identity),
            "identities_multiple": len(multiple),
            "identity_collisions": len(collisions),
            "identities_altered": len(altered),
            "identities_reused": len(collisions),
            "identities_renumbered": len(renumbered),
            "identities_attribute_coupled": len(attribute_coupled),
            "identities_unresolvable": len(unresolvable),
            "references_unresolvable": len(dangling),
            "identities_untraceable": len(untraceable),
            "lifecycle_states_undeclared": len(undeclared_states),
            "history_not_append_only": len(history_breaks),
            "identities_unverifiable": len(unverifiable),
            "identity_records_with_secret_field": len(secret_hits),
            "namespace_partition_ambiguities": ambiguity_excess,
            "identity_records_claiming_authority": len(authority_hits),
            "identities_failing_declared_grammar": len(grammar_failures),
            "registry_identities_absent_from_ledger": len(derived_absent),
            "nonsource_identity_admissions": len(nonsource),
            "namespaces_ungoverned": len(ungoverned),
            "namespaces_near_capacity": len(near),
        },
        "evidence": {
            "undeclared_states": undeclared_states,
            "dangling": sorted(dangling)[:20],
            "secret_hits": sorted(secret_hits)[:20],
            "authority_hits": sorted(authority_hits)[:20],
        },
    }


# --------------------------------------------------------------------------- architecture readings


def measure_realization(document: dict) -> list[dict]:
    obligation = document["realization_obligation"]
    tokens = [str(t) for t in obligation["tokens"]]
    single = str(obligation["single_authority_token"])
    rows: list[dict] = []
    for relative in obligation["obligated"]:
        text = read_text(relative)
        declared = bool(text) and any(token in text for token in tokens)
        exclusive = bool(text) and single.lower() in text.lower()
        rows.append(
            {
                "artifact": relative,
                "located": text is not None,
                "declares_realization": declared,
                "declares_single_authority": exclusive,
                "met": text is not None and declared,
            }
        )
    return rows


def measure_mechanisms(document: dict) -> list[dict]:
    planes = {str(p["plane"]) for p in document["identity_planes"]}
    rows: list[dict] = []
    for mech in document["identity_mechanisms"]:
        module = str(mech["module"])
        grammar_owner = str(mech["grammar_owner"])
        rows.append(
            {
                "id": mech["id"],
                "name": mech["name"],
                "plane": mech["plane"],
                "owner": mech["owner"],
                "module": module,
                "symbol": mech["symbol"],
                "grammar_owner": grammar_owner,
                "grammar_symbol": mech["grammar_symbol"],
                "keyed_by": mech["keyed_by"],
                "note": mech.get("note", ""),
                "plane_declared": str(mech["plane"]) in planes,
                "owner_located": (REPO / str(mech["owner"])).is_file(),
                "module_located": (REPO / module).is_file(),
                "symbol_located": symbol_present(module, str(mech["symbol"])),
                "grammar_located": symbol_present(grammar_owner, str(mech["grammar_symbol"]))
                or (REPO / grammar_owner).suffix == ".json" and (REPO / grammar_owner).is_file(),
            }
        )
    return rows


def measure_capabilities(document: dict) -> list[dict]:
    rows: list[dict] = []
    for cap in document["capabilities"]:
        owner = str(cap["owner"])
        artifacts = [str(a) for a in cap["artifacts"]]
        unresolved = [a for a in artifacts if not (REPO / a).exists()]
        rows.append(
            {
                "id": cap["id"],
                "group": cap["group"],
                "capability": cap["capability"],
                "owner": owner,
                "artifacts": artifacts,
                "status": cap["status"],
                "action": cap["action"],
                "evidence": cap.get("evidence", ""),
                "owner_located": (REPO / owner).exists(),
                "artifacts_unresolved": unresolved,
            }
        )
    return rows


def measure_bookkeeping(document: dict) -> list[dict]:
    facet_decl = document["facet_authority"]
    facet_source = read_text(str(facet_decl["owner"])) or ""
    facet_values = set(re.findall(r'^\s*[A-Z][A-Z0-9_]*\s*=\s*"([a-z0-9-]+)"', facet_source, re.MULTILINE))
    field_space: dict[str, tuple[set[str], set[str]]] = {}
    rows: list[dict] = []
    for item in document["bookkeeping_obligations"]:
        source_key = str(item["source"])
        source = document.get(source_key) or {}
        owner = str(source.get("owner") or "")
        field = str(item["field"])
        facet = str(item["facet"])
        located = bool(owner) and (REPO / owner).is_file()
        # An obligation that binds only to the file CONTAINING the answer has not been
        # measured: the located source must actually carry the declared field. The
        # resolution scope is recorded so the reading is evidence rather than a verdict.
        if not located:
            resolved, scope = False, "OWNER-ABSENT"
        elif item["plane"] == "artifact":
            if source_key not in field_space:
                field_space[source_key] = collect_field_space(read_json(owner))
            document_fields, entry_fields = field_space[source_key]
            if field in entry_fields:
                resolved, scope = True, "ENTRY"
            elif field in document_fields:
                resolved, scope = True, "DOCUMENT"
            else:
                resolved, scope = False, "FIELD-ABSENT"
        elif field in facet_values:
            # The code plane answers an obligation with a member of the located closed
            # set, so the member itself is the field.
            resolved, scope = True, "MEMBER"
        elif symbol_present(owner, field):
            resolved, scope = True, "SYMBOL"
        else:
            resolved, scope = False, "FIELD-ABSENT"
        rows.append(
            {
                "id": item["id"],
                "obligation": item["obligation"],
                "plane": item["plane"],
                "source": owner,
                "field": field,
                "facet": facet,
                "owner_located": located,
                "field_scope": scope,
                "bound": located and resolved,
                "facet_known": facet in facet_values,
            }
        )
    return rows, sorted(facet_values)


def measure_unboundedness(document: dict, ledger: dict, bookkeeping: list[dict]) -> tuple:
    section = document["unboundedness"]
    probes: list[dict] = []
    for probe in section["extension_probes"]:
        module = str(probe["module"])
        symbol = str(probe["symbol"])
        probes.append(
            {
                "id": probe["id"],
                "module": module,
                "symbol": symbol,
                "kind": probe["kind"],
                "located": (REPO / module).is_file(),
                "symbol_located": symbol_present(module, symbol),
            }
        )
    by_id = {p["id"]: p for p in probes}

    # A phrase asserting closure closes the architecture; the SAME phrase inside a
    # prohibition of closure is the architecture defending itself. Counting the second
    # as the first would convict the expansion constitution of the defect it forbids,
    # so a hit whose line carries a negation marker is not a claim.
    terminal_tokens = [str(t).lower() for t in section["terminal_tokens"]]
    negations = [str(n).lower() for n in section["negation_markers"]]
    terminal_hits: list[str] = []
    surfaces = list(document["realization_obligation"]["obligated"]) + [
        str(document["programme"]["law_owner"]),
        str(section["owner"]),
    ]
    for relative in surfaces:
        text = read_text(relative) or ""
        for line in text.splitlines():
            low = line.lower()
            for token in terminal_tokens:
                if token not in low:
                    continue
                if any(marker in low for marker in negations):
                    continue
                terminal_hits.append(f"{relative}::{token}")

    measures = {
        "namespaces_near_capacity": ledger["measures"]["namespaces_near_capacity"],
        "terminal_state_claims": len(terminal_hits),
        "extension_probes_unresolved": sum(
            0 if (p["located"] and p["symbol_located"]) else 1 for p in probes
        ),
        # Self-description is measured BY RESOLUTION: an identity is self-describing when
        # resolving it answers every declared bookkeeping obligation through a located
        # field and a member of the located closed facet set.
        "self_description_unbound": sum(
            0 if (b["bound"] and b["facet_known"]) else 1 for b in bookkeeping
        ),
    }

    rows: list[dict] = []
    for dim in section["dimensions"]:
        probe = by_id.get(str(dim.get("probe") or ""))
        measure = str(dim["measure"])
        if measure in measures:
            value = measures[measure]
        elif probe is not None:
            value = 0 if (probe["located"] and probe["symbol_located"]) else 1
        else:  # pragma: no cover - defensive
            value = 1
        satisfied = compare(value, str(dim["comparator"]), int(dim["expect"]))
        rows.append(
            {
                "id": dim["id"],
                "requirement": dim["requirement"],
                "clause": dim["clause"],
                "restated_by": dim["restated_by"],
                "restated_anchor": dim["restated_anchor"],
                "measure": measure,
                "comparator": dim["comparator"],
                "expect": dim["expect"],
                "value": value,
                "satisfied": satisfied,
                "blocking": bool(dim["blocking"]),
                "probe": dim.get("probe"),
                "note": dim.get("note", ""),
            }
        )
    return rows, probes, terminal_hits, measures


def measure_records(document: dict) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    for record in document["record_set"]["records"]:
        owner = str(record["owner"])
        text = read_text(owner)
        anchor = str(record["anchor"])
        rows.append(
            {
                "id": record["id"],
                "owner": owner,
                "anchor": anchor,
                "law": record["law"],
                "located": text is not None,
                "anchor_present": bool(text) and anchor in text,
            }
        )
    write_set = {(OWN_PREFIX + name) for name in PAGES}
    write_set.add(MODEL.relative_to(REPO).as_posix())
    record_set = {row["owner"] for row in rows}
    intersection = sorted(write_set & record_set)
    outside = sorted(p for p in write_set if not p.startswith(OWN_PREFIX))
    forbidden = [str(p) for p in document["programme"]["forbidden_write_prefixes"]]
    trespass = sorted(p for p in write_set for prefix in forbidden if p.startswith(prefix))
    immutability = {
        "write_set": sorted(write_set),
        "record_set": sorted(record_set),
        "intersection": intersection,
        "outside_home": outside,
        "forbidden_trespass": trespass,
        "disjoint": not intersection and not outside and not trespass,
    }
    return rows, immutability


def compare(value: int, comparator: str, expect: int) -> bool:
    if comparator == "==":
        return value == expect
    if comparator == "<=":
        return value <= expect
    if comparator == ">=":
        return value >= expect
    raise FailClosed(f"unknown comparator in the declaration: {comparator!r}")


# --------------------------------------------------------------------------- measurement


def measure(document: dict) -> dict:  # noqa: C901 - one measurement per declared concern
    config = load_classification(document)
    ledger = measure_ledger(document, config)
    realization = measure_realization(document)
    mechanisms = measure_mechanisms(document)
    capabilities = measure_capabilities(document)
    bookkeeping, facet_values = measure_bookkeeping(document)
    unbounded, probes, terminal_hits, unbounded_measures = measure_unboundedness(
        document, ledger, bookkeeping
    )
    records, immutability = measure_records(document)

    planes = []
    for plane in document["identity_planes"]:
        realizations = [m for m in mechanisms if m["plane"] == plane["plane"]]
        planes.append(
            {
                "id": plane["id"],
                "plane": plane["plane"],
                "name": plane["name"],
                "law": plane["law"],
                "anchor": plane["anchor"],
                "role": plane["role"],
                "definition": plane["definition"],
                "owner_located": (REPO / str(plane["owner"])).is_file(),
                "mechanisms": [m["id"] for m in realizations],
                "realized": bool(realizations),
            }
        )

    law_source = document["law_source"]
    law_text = read_text(str(law_source["owner"])) or ""
    laws: list[dict] = []
    for law in document["laws"]:
        identifier = str(law["id"])
        bound = identifier in law_text
        if law.get("measurable"):
            measure_name = str(law["measure"])
            value = ledger["measures"].get(measure_name)
            if value is None:
                value = unbounded_measures.get(measure_name)
            if value is None:
                value = derived_measure(measure_name, capabilities, immutability)
            satisfied = compare(int(value), str(law["comparator"]), int(law["expect"]))
            state = "SATISFIED" if satisfied else "VIOLATED"
        else:
            measure_name = None
            value = None
            satisfied = True
            state = NOT_MEASURABLE
        laws.append(
            {
                "id": identifier,
                "law": law["law"],
                "invariant": law["invariant"],
                "measurable": bool(law.get("measurable")),
                "measure": measure_name,
                "comparator": law.get("comparator"),
                "expect": law.get("expect"),
                "bound_finding": law.get("bound_finding"),
                "value": value,
                "satisfied": satisfied,
                "state": state,
                "bound": bound,
                "blocking": bool(law.get("blocking")),
                "reason": law.get("reason", ""),
            }
        )

    counters = {
        "capabilities_unowned": sum(0 if c["owner_located"] else 1 for c in capabilities),
        "capabilities_created": sum(1 for c in capabilities if c["action"] == ACTION_CREATE),
        "capability_artifacts_unresolved": sum(len(c["artifacts_unresolved"]) for c in capabilities),
        "realization_obligations_unmet": sum(0 if r["met"] else 1 for r in realization),
        "mechanisms_unclassified": sum(0 if m["plane_declared"] else 1 for m in mechanisms),
        "mechanisms_unresolved": sum(
            0 if (m["module_located"] and m["symbol_located"] and m["owner_located"] and m["grammar_located"]) else 1
            for m in mechanisms
        ),
        "planes_unrealized": sum(0 if p["realized"] else 1 for p in planes),
        "laws_unbound": sum(0 if law["bound"] else 1 for law in laws),
        "laws_violated": sum(1 for law in laws if law["blocking"] and not law["satisfied"]),
        "bookkeeping_unbound": sum(0 if b["bound"] else 1 for b in bookkeeping),
        # The field half of the binding, isolated from the owner half: an obligation whose
        # containing source is located but whose declared field is not is exactly the
        # defect a source-only reading could not see.
        "bookkeeping_fields_unresolved": sum(
            1 for b in bookkeeping if b["owner_located"] and not b["bound"]
        ),
        "bookkeeping_facets_unknown": sum(0 if b["facet_known"] else 1 for b in bookkeeping),
        "identity_minting_attempts": 0,
        "writes_outside_home": len(immutability["outside_home"]) + len(immutability["forbidden_trespass"]),
        "record_write_intersections": len(immutability["intersection"]),
        "authority_claims": 0 if str(document["programme"]["authority"]).startswith("NONE") else 1,
        "unboundedness_violations": sum(1 for d in unbounded if d["blocking"] and not d["satisfied"]),
    }
    counters.update(ledger["measures"])
    counters.update(unbounded_measures)

    # A bound that exceeds the divergence it describes would let a regression hide
    # inside the slack, so slack is itself measured.
    slack: list[dict] = []
    for entry in list(document["laws"]) + list(document["validations"]):
        if str(entry.get("comparator")) != "<=":
            continue
        name = str(entry.get("measure"))
        value = counters.get(name)
        if value is None:
            continue
        if int(value) < int(entry["expect"]):
            slack.append({"id": entry["id"], "measure": name, "value": int(value), "bound": int(entry["expect"])})
    counters["bounds_slack"] = len(slack)

    validations: list[dict] = []
    for check in document["validations"]:
        name = str(check["measure"])
        value = counters.get(name)
        if value is None:
            raise FailClosed(f"a declared dimension has no measurement: {check['id']} ({name})")
        satisfied = compare(int(value), str(check["comparator"]), int(check["expect"]))
        validations.append(
            {
                "id": check["id"],
                "dimension": check["dimension"],
                "measure": name,
                "comparator": check["comparator"],
                "expect": check["expect"],
                "value": int(value),
                "satisfied": satisfied,
                "blocking": bool(check["blocking"]),
                "bound_finding": check.get("bound_finding"),
            }
        )

    blocking_failures = [v["id"] for v in validations if v["blocking"] and not v["satisfied"]]
    gate = "OPEN" if not blocking_failures else "CLOSED"
    determination = (
        document["determination"]["bound"] if gate == "OPEN" else document["determination"]["open"]
    )

    model = {
        "programme": document["programme"],
        "grammar": ledger["grammar"],
        "counts": ledger["counts"],
        "peak_namespace": ledger["peak_namespace"],
        "near_capacity": ledger["near_capacity"],
        "ambiguous_namespaces": ledger["ambiguous_namespaces"],
        "ungoverned_namespaces": ledger["ungoverned_namespaces"],
        "nonsource_admissions": ledger["nonsource_admissions"],
        "unresolvable": ledger["unresolvable"],
        "evidence": ledger["evidence"],
        "planes": planes,
        "mechanisms": mechanisms,
        "realization": realization,
        "capabilities": capabilities,
        "bookkeeping": bookkeeping,
        "facet_values": facet_values,
        "unboundedness": unbounded,
        "probes": probes,
        "terminal_hits": sorted(terminal_hits),
        "laws": laws,
        "records": records,
        "immutability": immutability,
        "counters": counters,
        "bounds_slack": slack,
        "validations": validations,
        "exit_criteria": document["exit_criteria"],
        "findings": document["findings"],
        "blocking_failures": blocking_failures,
        "gate": gate,
        "determination": determination,
    }
    model["seal_sha256"] = digest(
        json.dumps(
            {k: v for k, v in model.items() if k != "seal_sha256"},
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    return model


def derived_measure(name: str, capabilities: list[dict], immutability: dict) -> int:
    """Measures a law shares with a validation, so neither is computed twice."""
    if name == "capabilities_created":
        return sum(1 for c in capabilities if c["action"] == ACTION_CREATE)
    if name == "record_write_intersections":
        return len(immutability["intersection"])
    raise FailClosed(f"a declared law names a measurement that does not exist: {name}")


# --------------------------------------------------------------------------- rendering


def table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(out)


def yes(value: bool) -> str:
    return "YES" if value else "**NO**"


def tick(value: bool) -> str:
    return "PASS" if value else "**FAIL**"


def code(value: Any) -> str:
    text = str(value)
    return f"`{text}`" if text else ""


def front_matter(model: dict, title: str) -> str:
    programme = model["programme"]
    return "\n".join(
        [
            f"# {programme['id']} · {title}",
            "",
            table(
                ["Field", "Value"],
                [
                    ["PROGRAMME", f"{programme['id']} — {programme['name']}"],
                    ["VERSION", str(programme["version"])],
                    ["AUTHORITY", str(programme["authority"])],
                    ["LAW OWNER", code(programme["law_owner"])],
                    ["ARCHITECTURE OWNER", code(programme["architecture_owner"])],
                    ["GATE", model["gate"]],
                    ["DETERMINATION", model["determination"]],
                    ["SEAL (sha256)", model["seal_sha256"]],
                    ["GENERATED BY", "uis_engine.py — regenerated, never hand-authored"],
                ],
            ),
            "",
            f"> {programme['disclosure']}",
            "",
        ]
    )


def render(model: dict) -> dict[str, str]:  # noqa: C901 - one page per measured concern
    pages: dict[str, str] = {}
    counters = model["counters"]

    # ---- 00 dashboard
    body = [front_matter(model, "Identity Conformance Dashboard")]
    body.append("## Measured position\n")
    body.append(
        table(
            ["Reading", "Value"],
            [
                ["Recorded identities (RECORDED plane)", str(model["counts"]["recorded_identities"])],
                ["Recorded histories", str(model["counts"]["recorded_histories"])],
                ["Registered identities (DERIVED plane)", str(model["counts"]["registered_identities"])],
                ["Live category namespaces", str(model["counts"]["live_namespaces"])],
                ["Namespaces declared by the classification authority", str(model["counts"]["declared_namespaces"])],
                ["Formatting capacity per namespace", str(model["counts"]["namespace_capacity"])],
                ["Identity laws bound", f"{len(model['laws']) - counters['laws_unbound']}/{len(model['laws'])}"],
                ["Identity laws measured", str(sum(1 for law in model["laws"] if law["measurable"]))],
                ["Capabilities mapped", str(len(model["capabilities"]))],
                ["Capabilities dispositioned CREATE", str(counters["capabilities_created"])],
                ["Bookkeeping obligations bound", f"{len(model['bookkeeping']) - counters['bookkeeping_unbound']}/{len(model['bookkeeping'])}"],
                ["Unboundedness directions satisfied", f"{sum(1 for d in model['unboundedness'] if d['satisfied'])}/{len(model['unboundedness'])}"],
                ["Blocking dimensions satisfied", f"{sum(1 for v in model['validations'] if v['satisfied'])}/{len(model['validations'])}"],
                ["Record immutability", yes(model["immutability"]["disjoint"])],
            ],
        )
    )
    body.append("\n## What this measurement does NOT do\n")
    body.append(
        "\n".join(
            [
                "- It mints no identity and allocates no identifier.",
                "- It declares no namespace and defines no grammar.",
                "- It opens no registry and legislates no lifecycle.",
                "- It resolves nothing authoritatively and certifies nothing.",
                "",
                "Where this measurement and a located instrument differ, **the located instrument governs**.",
            ]
        )
    )
    body.append("\n## Registers\n")
    body.append("\n".join(f"- [{name}]({name})" for name in PAGES if name != PAGES[0]))
    pages[PAGES[0]] = "\n".join(body) + "\n"

    # ---- 01 capability mapping matrix
    body = [front_matter(model, "Identity Capability Mapping Matrix")]
    body.append(
        "Every identity capability reached by semantic measurement, mapped to its located canonical\n"
        "owner, its located artifacts, its measured implementation status and its constitutional action.\n"
        "`CREATE` is a validation failure wherever an owner is named: a capability whose owner resolves\n"
        "cannot be created a second time without manufacturing a parallel authority.\n"
    )
    body.append(
        table(
            ["Capability", "Group", "Canonical owner", "Repository artifact(s)", "Status", "Action", "Owner resolves"],
            [
                [
                    row["capability"],
                    row["group"],
                    code(row["owner"]),
                    " · ".join(code(a) for a in row["artifacts"]),
                    row["status"],
                    row["action"],
                    yes(row["owner_located"] and not row["artifacts_unresolved"]),
                ]
                for row in model["capabilities"]
            ],
        )
    )
    counts_by_action: dict[str, int] = {}
    counts_by_status: dict[str, int] = {}
    for row in model["capabilities"]:
        counts_by_action[row["action"]] = counts_by_action.get(row["action"], 0) + 1
        counts_by_status[row["status"]] = counts_by_status.get(row["status"], 0) + 1
    body.append("\n## Disposition summary\n")
    body.append(
        table(
            ["Constitutional action", "Count"],
            [[key, str(counts_by_action[key])] for key in sorted(counts_by_action)],
        )
    )
    body.append("")
    body.append(
        table(
            ["Implementation status", "Count"],
            [[key, str(counts_by_status[key])] for key in sorted(counts_by_status)],
        )
    )
    body.append("\n## Evidence\n")
    body.append(
        table(
            ["Capability", "Evidence"],
            [[row["capability"], row["evidence"]] for row in model["capabilities"] if row["evidence"]],
        )
    )
    pages[PAGES[1]] = "\n".join(body) + "\n"

    # ---- 02 law binding register
    body = [front_matter(model, "Identity Law Binding Register")]
    body.append(
        "The identity laws the located architecture declares as binding invariants, each bound to its\n"
        "owner and, where the located data can decide it, measured. A law reported\n"
        f"`{NOT_MEASURABLE}` is bound but NOT asserted, so the coverage of this measurement is visible\n"
        "rather than assumed.\n"
    )
    body.append(
        table(
            ["Law", "Invariant", "Bound", "Measure", "Expect", "Measured", "State"],
            [
                [
                    law["id"],
                    law["invariant"],
                    yes(law["bound"]),
                    code(law["measure"]) if law["measure"] else "—",
                    f"{law['comparator']} {law['expect']}" if law["measurable"] else "—",
                    str(law["value"]) if law["value"] is not None else "—",
                    law["state"] if law["satisfied"] else f"**{law['state']}**",
                ]
                for law in model["laws"]
            ],
        )
    )
    unmeasured = [law for law in model["laws"] if not law["measurable"]]
    if unmeasured:
        body.append("\n## Declared but not decidable here\n")
        body.append(table(["Law", "Reason"], [[law["id"], law["reason"]] for law in unmeasured]))
    body.append("\n## Single identity authority\n")
    body.append(
        "The law obliges every named architecture to declare that it realizes the single identity\n"
        "authority. That obligation is verified here rather than assumed.\n"
    )
    body.append(
        table(
            ["Obligated architecture", "Located", "Declares realization", "Declares single authority"],
            [
                [code(row["artifact"]), yes(row["located"]), yes(row["declares_realization"]), yes(row["declares_single_authority"])]
                for row in model["realization"]
            ],
        )
    )
    pages[PAGES[2]] = "\n".join(body) + "\n"

    # ---- 03 planes and grammars
    body = [front_matter(model, "Identity Plane and Grammar Register")]
    body.append(
        "The located identity planes and the located mechanisms that realize them. The planes are\n"
        "declared by the law as orthogonal and non-substitutable, so the mechanisms are **crosswalked,\n"
        "never merged**: one scheme per plane, each with its own declared grammar. No scheme is minted\n"
        "here and none is unified.\n"
    )
    body.append(
        table(
            ["Plane", "Name", "Law", "Role", "Definition", "Realized by"],
            [
                [p["plane"], p["name"], p["law"], p["role"], p["definition"], ", ".join(p["mechanisms"]) or "**none**"]
                for p in model["planes"]
            ],
        )
    )
    body.append("\n## Located identity mechanisms (the crosswalk)\n")
    body.append(
        table(
            ["Mechanism", "Plane", "Keyed by", "Module", "Grammar owner", "Resolves"],
            [
                [
                    m["name"],
                    m["plane"],
                    m["keyed_by"],
                    code(m["module"]),
                    code(m["grammar_owner"]),
                    yes(m["module_located"] and m["symbol_located"] and m["grammar_located"]),
                ]
                for m in model["mechanisms"]
            ],
        )
    )
    body.append("\n## Why four schemes is the architecture and not a defect\n")
    body.append(
        "\n".join(
            f"- **{m['plane']} — {m['name']}.** {m['note']}" for m in model["mechanisms"] if m["note"]
        )
    )
    body.append(f"\n## Declared artifact-plane grammar\n\n`{model['grammar']}`\n")
    body.append("## Namespace governance\n")
    body.append(
        table(
            ["Reading", "Value"],
            [
                ["Live category namespaces", str(model["counts"]["live_namespaces"])],
                ["Governed by a declared classification rule", str(model["counts"]["live_namespaces"] - counters["namespaces_ungoverned"])],
                ["Ungoverned (referred to the nomenclature owner)", str(counters["namespaces_ungoverned"])],
                ["Partition ambiguity excess", str(counters["namespace_partition_ambiguities"])],
                ["Derived namespace width now in force", str(model["counts"]["namespace_width"])],
            ],
        )
    )
    if model["ambiguous_namespaces"]:
        body.append("\n### Namespaces that share a truncation window\n")
        body.append(
            table(
                ["Truncated code", "Distinct live namespaces"],
                [[code(k), " · ".join(code(n) for n in v)] for k, v in sorted(model["ambiguous_namespaces"].items())],
            )
        )
    pages[PAGES[3]] = "\n".join(body) + "\n"

    # ---- 04 ledger measurement
    body = [front_matter(model, "Identity Ledger Measurement Register")]
    body.append(
        "The measurement of the located identity data. The ledger is the RECORDED plane and the artifact\n"
        "registry is the DERIVED plane; the root axiom forbids conflating them, so they are read\n"
        "separately and measured against each other.\n"
    )
    body.append(
        table(
            ["Measure", "Value"],
            [[code(k), str(v)] for k, v in sorted(model["counters"].items())],
        )
    )
    body.append("\n## Standing divergences\n")
    body.append(
        "Each is bounded, disclosed and referred to its owner. None is repaired here: erasing or editing\n"
        "a recorded identity is forbidden by the append-only law, so a measurement that 'fixed' one would\n"
        "be committing the defect it reports.\n"
    )
    body.append(
        table(
            ["Finding", "Class", "Disposition", "Bound measure", "Measured", "Referred to"],
            [
                [
                    f["id"],
                    f["class"],
                    f["disposition"],
                    code(f["bound_measure"]) if f.get("bound_measure") else "—",
                    str(counters.get(str(f.get("bound_measure")), "—")),
                    code(f["referred_to"]),
                ]
                for f in model["findings"]
            ],
        )
    )
    for finding in model["findings"]:
        body.append(f"\n### {finding['id']} — {finding['title']}\n")
        body.append(finding["detail"])
        body.append(f"\n*Why it is not repaired here:* {finding['why_not_repaired']}")
    pages[PAGES[4]] = "\n".join(body) + "\n"

    # ---- 05 unboundedness
    body = [front_matter(model, "Unboundedness and Self-Description Register")]
    body.append(
        "Unbounded lawful expansion is legislated by the located expansion constitution and restated by\n"
        "the identity and nomenclature architectures. It was never measured. Each direction below is\n"
        "bound to its clause and probed over located code or located data. Nothing here widens a\n"
        "parameter, admits a namespace or declares a family: a measurement that expanded the\n"
        "architecture in order to prove it expandable would be the parallel authority the meta-governance\n"
        "instrument forbids.\n"
    )
    body.append(
        table(
            ["Direction", "Requirement", "Clause", "Measure", "Expect", "Measured", "State"],
            [
                [
                    d["id"],
                    d["requirement"],
                    d["clause"],
                    code(d["measure"]),
                    f"{d['comparator']} {d['expect']}",
                    str(d["value"]),
                    tick(d["satisfied"]),
                ]
                for d in model["unboundedness"]
            ],
        )
    )
    body.append("\n## Located extension paths\n")
    body.append(
        "A closed set with a declared admission path is extensible; a closed set without one is a\n"
        "ceiling. Each probe proves the path exists — it never adds a member.\n"
    )
    body.append(
        table(
            ["Probe", "Extension path", "Module", "Symbol", "Resolves"],
            [
                [p["id"], p["kind"], code(p["module"]), code(p["symbol"]), yes(p["located"] and p["symbol_located"])]
                for p in model["probes"]
            ],
        )
    )
    peak = model["peak_namespace"]
    body.append("\n## Identity scale headroom\n")
    body.append(
        table(
            ["Reading", "Value"],
            [
                ["Formatting capacity per namespace", str(model["counts"]["namespace_capacity"])],
                ["Busiest live namespace", code(peak["namespace"]) if peak["namespace"] else "—"],
                ["Ordinals allocated in it", str(peak["used"])],
                ["Fraction of capacity in use", f"{peak['fraction'] * 100:.6f}%"],
                ["Namespaces at or beyond the declared fraction", str(counters["namespaces_near_capacity"])],
            ],
        )
    )
    body.append(
        "\nThe width is **formatting, not a ceiling**: the located expansion constitution declares that a\n"
        "width widens append-only if a namespace approaches it, renumbering nothing. This dimension is\n"
        "what makes that trigger observable instead of arriving as an exhaustion.\n"
    )
    body.append("## Constitutional self-description\n")
    body.append(
        "Self-description is measured **by resolution, not by parsing**: the law makes durable identity\n"
        "opaque and the architecture forbids consumers depending on a token's internal structure. The\n"
        "measured property is that resolving any identity answers every declared bookkeeping obligation.\n"
    )
    body.append(
        "An obligation binds only when the located source **carries the declared field**, not\n"
        "merely when the file containing it resolves. `Field resolves in` records where the\n"
        "located source answers it: `DOCUMENT` once for the whole record, `ENTRY` once per\n"
        "recorded entry, `MEMBER` as a member of the located closed facet set, `SYMBOL` as a\n"
        "definition in the located module. `FIELD-ABSENT` is a failure of the binding, not a note.\n"
    )
    body.append(
        table(
            [
                "Obligation",
                "Plane",
                "Answered by",
                "Field",
                "Field resolves in",
                "Facet",
                "Bound",
                "Facet is a declared member",
            ],
            [
                [
                    b["obligation"],
                    b["plane"],
                    code(b["source"]),
                    code(b["field"]),
                    b["field_scope"],
                    code(b["facet"]),
                    yes(b["bound"]),
                    yes(b["facet_known"]),
                ]
                for b in model["bookkeeping"]
            ],
        )
    )
    pages[PAGES[5]] = "\n".join(body) + "\n"

    # ---- 06 validation
    body = [front_matter(model, "Validation Report")]
    body.append(
        table(
            ["Dimension", "Statement", "Measure", "Expect", "Measured", "Blocking", "Result"],
            [
                [
                    v["id"],
                    v["dimension"],
                    code(v["measure"]),
                    f"{v['comparator']} {v['expect']}",
                    str(v["value"]),
                    yes(v["blocking"]),
                    tick(v["satisfied"]),
                ]
                for v in model["validations"]
            ],
        )
    )
    body.append("\n## Bound tightness\n")
    body.append(
        "A bound wider than the divergence it describes would let a regression hide inside the slack, so\n"
        "slack is itself a blocking measurement.\n"
    )
    if model["bounds_slack"]:
        body.append(
            table(
                ["Dimension", "Measure", "Measured", "Declared bound"],
                [[s["id"], code(s["measure"]), str(s["value"]), str(s["bound"])] for s in model["bounds_slack"]],
            )
        )
    else:
        body.append("Every declared bound is tight: no bound exceeds the divergence it describes.")
    body.append("\n## Record immutability\n")
    body.append(
        table(
            ["Reading", "Value"],
            [
                ["Paths this measurement writes", str(len(model["immutability"]["write_set"]))],
                ["Located records it must not write", str(len(model["immutability"]["record_set"]))],
                ["Intersection", str(len(model["immutability"]["intersection"]))],
                ["Writes outside its own home", str(len(model["immutability"]["outside_home"]))],
                ["Writes inside a forbidden prefix", str(len(model["immutability"]["forbidden_trespass"]))],
                ["Disjoint", yes(model["immutability"]["disjoint"])],
            ],
        )
    )
    body.append("")
    body.append(
        table(
            ["Record", "Owner", "Located", "Anchor present", "Law"],
            [[r["id"], code(r["owner"]), yes(r["located"]), yes(r["anchor_present"]), r["law"]] for r in model["records"]],
        )
    )
    pages[PAGES[6]] = "\n".join(body) + "\n"

    # ---- 07 certification
    body = [front_matter(model, "Certification Report")]
    body.append("## Exit criteria\n")
    body.append(
        table(
            ["Criterion", "Statement"],
            [[c["id"], c["statement"]] for c in model["exit_criteria"]],
        )
    )
    body.append("\n## Position\n")
    body.append(
        table(
            ["Attribute", "Value"],
            [
                ["CAPABILITIES MAPPED", f"{len(model['capabilities'])}"],
                ["DISPOSITIONED CREATE", str(counters["capabilities_created"])],
                ["IDENTITY LAWS BOUND", f"{len(model['laws']) - counters['laws_unbound']}/{len(model['laws'])}"],
                ["IDENTITY LAWS MEASURED", str(sum(1 for law in model["laws"] if law["measurable"]))],
                ["IDENTITY PLANES REALIZED", f"{len(model['planes']) - counters['planes_unrealized']}/{len(model['planes'])}"],
                ["MECHANISMS CROSSWALKED", str(len(model["mechanisms"]))],
                ["SINGLE AUTHORITY DECLARED BY", f"{len(model['realization']) - counters['realization_obligations_unmet']}/{len(model['realization'])}"],
                ["BOOKKEEPING OBLIGATIONS BOUND", f"{len(model['bookkeeping']) - counters['bookkeeping_unbound']}/{len(model['bookkeeping'])}"],
                ["UNBOUNDEDNESS DIRECTIONS", f"{sum(1 for d in model['unboundedness'] if d['satisfied'])}/{len(model['unboundedness'])}"],
                ["BLOCKING DIMENSIONS", f"{sum(1 for v in model['validations'] if v['satisfied'])}/{len(model['validations'])}"],
                ["RECORD IMMUTABILITY", f"write ∩ record = {len(model['immutability']['intersection'])} · disjoint {yes(model['immutability']['disjoint'])}"],
                ["STANDING DIVERGENCES", f"{len(model['findings'])} registered, 0 decided"],
                ["GATE", model["gate"]],
                ["DETERMINATION", model["determination"]],
            ],
        )
    )
    body.append("\n## Findings\n")
    body.append(
        table(
            ["Finding", "Class", "Disposition", "Blocking", "Title"],
            [[f["id"], f["class"], f["disposition"], yes(bool(f["blocking"])), f["title"]] for f in model["findings"]],
        )
    )
    body.append(
        "\nThis measurement holds no identity authority, no certification authority and no ratification\n"
        "authority: it reads the identity architecture the repository has already legislated and the\n"
        "identity data it has already recorded, and reports what they say. Where this measurement and a\n"
        "located instrument differ, **the located instrument governs**.\n"
    )
    pages[PAGES[7]] = "\n".join(body) + "\n"

    # ---- 08 admission and disposition
    body = [front_matter(model, "Admission and Disposition")]
    body.append(
        "Exactly one disposition is recorded for every capability reached. A disposition is drawn from the\n"
        "totality rule of the located instrument, never invented here, and `CREATE` is a validation\n"
        "failure: a capability whose owner is named cannot be created a second time without manufacturing\n"
        "the parallel authority that instrument forbids.\n"
    )
    body.append(
        table(
            ["Capability", "Disposition", "Canonical owner", "Owner resolves", "Refusal recorded"],
            [
                [row["capability"], row["action"], code(row["owner"]), yes(row["owner_located"]), yes(row["action"] != ACTION_CREATE)]
                for row in model["capabilities"]
            ],
        )
    )
    body.append("\n## What was refused\n")
    body.append(
        "\n".join(
            [
                "A new identity authority — **REFUSED**: the law declares exactly one, and every obligated architecture declares it realizes that one.",
                "A new identity registry — **REFUSED**: the located registry family already governs registration.",
                "A new identity namespace — **REFUSED**: the located nomenclature architecture admits namespaces append-only from data.",
                "A new identity lifecycle — **REFUSED**: the located identity architecture already binds the lifecycle to its status field.",
                "A new identity resolver — **REFUSED**: the located identity architecture forecloses a new resolver and a new address space explicitly.",
                "A new identifier family — **REFUSED**: one grammar per declared plane already exists; the planes are crosswalked, never merged.",
                "A new bookkeeping mechanism — **REFUSED**: bookkeeping is bound twice already, by the artifact schema and by the closed facet set.",
                "",
                "What was **EXTENDED** is the measurement of what already exists, in the operational-memory lane, holding no authority.",
            ]
        )
    )
    pages[PAGES[8]] = "\n".join(body) + "\n"

    return pages


def write_registers(model: dict) -> list[str]:
    HERE.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, text in render(model).items():
        (HERE / name).write_text(text, encoding="utf-8")
        written.append(name)
    MODEL.write_text(
        json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    written.append(MODEL.name)
    return sorted(written)


# --------------------------------------------------------------------------- guards


def check_declaration(document: dict) -> list[str]:
    problems: list[str] = []
    seen: set[str] = set()
    sections = (
        "identity_planes",
        "identity_mechanisms",
        "laws",
        "bookkeeping_obligations",
        "capabilities",
        "validations",
        "exit_criteria",
        "findings",
    )
    for section in sections:
        for entry in document[section]:
            identifier = entry.get("id")
            if not identifier:
                problems.append(f"{section}: an entry carries no id")
            elif identifier in seen:
                problems.append(f"{section}: duplicate id {identifier}")
            else:
                seen.add(identifier)
    for entry in document["unboundedness"]["dimensions"] + document["unboundedness"]["extension_probes"]:
        identifier = entry.get("id")
        if identifier in seen:
            problems.append(f"unboundedness: duplicate id {identifier}")
        seen.add(identifier)
    for entry in document["record_set"]["records"]:
        if entry.get("id") in seen:
            problems.append(f"record_set: duplicate id {entry.get('id')}")
        seen.add(entry.get("id"))

    measures = [entry["measure"] for entry in document["validations"]]
    problems.extend(
        f"validations: duplicate measure {item}"
        for item in sorted({m for m in measures if measures.count(m) > 1})
    )

    # Every cited owner must resolve, or the reading rests on nothing.
    for section in ("identity_planes", "identity_mechanisms", "capabilities"):
        for entry in document[section]:
            owner = str(entry.get("owner") or "")
            if owner and not (REPO / owner).exists():
                problems.append(f"{entry['id']}: owner does not resolve: {owner}")
    for key in ("law_owner", "architecture_owner"):
        if not (REPO / str(document["programme"][key])).is_file():
            problems.append(f"programme.{key} does not resolve")
    for key in (
        "ledger_source",
        "registry_source",
        "grammar_source",
        "classification_authority",
        "namespace_governance",
        "facet_authority",
        "lifecycle",
        "law_source",
    ):
        owner = str(document[key]["owner"])
        if not (REPO / owner).is_file():
            problems.append(f"{key}: owner does not resolve: {owner}")
    if not (REPO / str(document["unboundedness"]["owner"])).is_file():
        problems.append("unboundedness: owner does not resolve")
    for entry in document["realization_obligation"]["obligated"]:
        if not (REPO / str(entry)).is_file():
            problems.append(f"realization_obligation: does not resolve: {entry}")
    for entry in document["record_set"]["records"]:
        if not (REPO / str(entry["owner"])).is_file():
            problems.append(f"{entry['id']}: record owner does not resolve: {entry['owner']}")
        if not str(entry.get("anchor", "")).strip():
            problems.append(f"{entry['id']}: no anchor recorded")

    # Every claimant this measurement reads must be write-protected from it.
    forbidden = [str(p) for p in document["programme"]["forbidden_write_prefixes"]]
    claimants = {str(document["programme"][k]) for k in ("law_owner", "architecture_owner")}
    claimants |= {str(document[k]["owner"]) for k in ("ledger_source", "registry_source", "grammar_source", "classification_authority", "facet_authority")}
    claimants |= {str(document["unboundedness"]["owner"])}
    claimants |= {str(e["owner"]) for e in document["record_set"]["records"]}
    for claimant in sorted(claimants):
        if not any(claimant.startswith(prefix) for prefix in forbidden):
            problems.append(f"a claimant is left unprotected by forbidden_write_prefixes: {claimant}")

    # A bound must name a finding that disposes of it, or it is an unexplained tolerance.
    findings = {str(f["id"]) for f in document["findings"]}
    for entry in list(document["laws"]) + list(document["validations"]):
        if str(entry.get("comparator")) == "<=":
            bound_finding = entry.get("bound_finding")
            if not bound_finding:
                problems.append(f"{entry['id']}: declares a bound with no disposing finding")
            elif str(bound_finding) not in findings:
                problems.append(f"{entry['id']}: names an unknown finding {bound_finding}")
    for entry in document["laws"]:
        if entry.get("measurable") and not entry.get("measure"):
            problems.append(f"{entry['id']}: declared measurable with no measure")
        if not entry.get("measurable") and not entry.get("reason"):
            problems.append(f"{entry['id']}: declared not measurable with no reason")
    if not any(str(c["action"]) == "EXTEND" for c in document["capabilities"]):
        problems.append("no capability is dispositioned EXTEND, so this programme implements no gap")
    for entry in document["capabilities"]:
        if str(entry["status"]) == STATUS_MISSING and str(entry["action"]) != ACTION_CREATE:
            problems.append(f"{entry['id']}: MISSING without CREATE is not a disposition")
        if str(entry["status"]) == STATUS_EXISTING and str(entry["action"]) != "REUSE":
            problems.append(f"{entry['id']}: EXISTING must be dispositioned REUSE")
        if str(entry["status"]) == STATUS_PARTIAL and str(entry["action"]) != "EXTEND":
            problems.append(f"{entry['id']}: PARTIAL must be dispositioned EXTEND")
    return problems


def check_no_enumeration(document: dict) -> list[str]:
    """No discovered identity, namespace or path may appear as a literal in this source.

    A namespace is tested as a QUOTED STRING or inside an identity token, not as a bare
    word. Several discovered namespaces are truncations that collide with ordinary English
    words, and a prose label containing such a word is not an enumeration — only a string
    literal the engine could branch on would be.
    """
    source = Path(__file__).read_text(encoding="utf-8")
    model = measure(document)
    leaked: list[str] = []
    for namespace in model["ungoverned_namespaces"]:
        token = re.escape(str(namespace))
        if re.search(rf"[\"']{token}[\"']", source) or re.search(rf"-{token}-", source):
            leaked.append(f"namespace {namespace}")
    for path in model["nonsource_admissions"] + model["unresolvable"]:
        if str(path) in source:
            leaked.append(f"path {path}")
    for bucket in model["ambiguous_namespaces"]:
        if re.search(rf"[\"']{re.escape(str(bucket))}[\"']", source):
            leaked.append(f"truncation bucket {bucket}")
    if model["grammar"] in source:
        leaked.append("the declared grammar is hard-coded")
    return sorted(set(leaked))


def check_write_scope(document: dict) -> list[str]:
    problems: list[str] = []
    for name in PAGES:
        try:
            (HERE / name).resolve().relative_to(HERE)
        except ValueError:  # pragma: no cover - defensive
            problems.append(name)
    rendered = set(render(measure(document)))
    if rendered != set(PAGES):
        problems.append("the renderer does not produce exactly the declared page set")
    for prefix in document["programme"]["forbidden_write_prefixes"]:
        if OWN_PREFIX.startswith(str(prefix)):
            problems.append(f"own home falls inside a forbidden prefix: {prefix}")
    model = measure(document)
    problems += [f"writes outside its home: {p}" for p in model["immutability"]["outside_home"]]
    problems += [f"writes inside a forbidden prefix: {p}" for p in model["immutability"]["forbidden_trespass"]]
    return problems


def check_determinism(document: dict) -> list[str]:
    """Byte-identical rendering, and no non-deterministic input in this engine's source.

    The forbidden inputs are read from the declaration rather than written here: an engine
    holding those strings in its own source would match itself while scanning for them.
    """
    first, second = render(measure(document)), render(measure(document))
    problems = sorted(name for name in first if first[name] != second.get(name))
    if measure(document)["seal_sha256"] != measure(document)["seal_sha256"]:  # pragma: no cover
        problems.append("the seal is not stable across two measurements")
    source = Path(__file__).read_text(encoding="utf-8")
    for forbidden in document["hygiene"]["nondeterministic_inputs"]:
        if str(forbidden) in source:
            problems.append(f"the engine reads a non-deterministic input: {forbidden}")
    return problems


def check_knowledge_once(document: dict) -> list[str]:
    """No identity, namespace or divergence may be DEFINED here; all must be discovered."""
    problems: list[str] = []
    raw = DECLARATION.read_text(encoding="utf-8")
    model = measure(document)
    for namespace in model["ungoverned_namespaces"]:
        if re.search(rf"\"{re.escape(str(namespace))}\"", raw):
            problems.append(f"declaration names namespace {namespace}")
    for path in model["nonsource_admissions"] + model["unresolvable"]:
        if str(path) in raw:
            problems.append(f"declaration names path {path}")
    if not model["counts"]["recorded_identities"]:
        problems.append("no identity was discovered from the located ledger")
    if not model["counts"]["registered_identities"]:
        problems.append("no identity was discovered from the located registry")
    if not model["facet_values"]:
        problems.append("no facet was discovered from the located facet authority")
    return problems


def check_record_immutability(document: dict) -> list[str]:
    """MANDATORY. write_set ∩ record_set = ∅, and every located record is protected."""
    model = measure(document)
    immutability = model["immutability"]
    problems = [f"write set intersects the record set: {item}" for item in immutability["intersection"]]
    problems += [f"writes outside its own home: {item}" for item in immutability["outside_home"]]
    problems += [f"writes inside a forbidden prefix: {item}" for item in immutability["forbidden_trespass"]]
    for record in model["records"]:
        if not record["located"]:
            problems.append(f"{record['id']}: protected record is absent")
        if not record["anchor_present"]:
            problems.append(f"{record['id']}: protected record's anchor moved")
    if not immutability["record_set"]:
        problems.append("no record is protected, so immutability is unmeasured")
    return problems


def check_no_identity_minting(document: dict) -> list[str]:
    """MANDATORY for this programme. It must prove it is not a second identity engine."""
    problems: list[str] = []
    model = measure(document)
    write_set = set(model["immutability"]["write_set"])

    # It may not write any located identity source.
    for key in ("ledger_source", "registry_source", "grammar_source", "classification_authority"):
        owner = str(document[key]["owner"])
        if owner in write_set:
            problems.append(f"this measurement writes an identity source: {owner}")

    # Its emitted bytes may not contain an identity that satisfies the located grammar
    # but is absent from the located ledger — that would be a minted identifier.
    grammar = re.compile(model["grammar"].strip("^$"))
    ledger = read_json(str(document["ledger_source"]["owner"]))
    known = {
        str((entry or {}).get(document["ledger_source"]["identity_field"]) or "")
        for entry in (ledger.get(document["ledger_source"]["path_map"]) or {}).values()
    }
    for name, text in render(model).items():
        for candidate in set(grammar.findall(text)) if grammar.groups else set(re.findall(model["grammar"].strip("^$"), text)):
            token = candidate if isinstance(candidate, str) else ""
            if token and token not in known:
                problems.append(f"{name}: emits an identifier absent from the ledger: {token}")

    # It may not declare a namespace of its own.
    if str(document["programme"]["id"]) in known:  # pragma: no cover - defensive
        problems.append("this programme has consumed a corpus identity")
    if not str(document["programme"]["authority"]).startswith("NONE"):
        problems.append("this measurement claims an authority")
    return sorted(set(problems))


def check_bounds_tight(document: dict) -> list[str]:
    """A bound wider than its divergence would let a regression hide in the slack."""
    model = measure(document)
    return [
        f"{entry['id']}: bound {entry['bound']} exceeds the measured divergence {entry['value']} ({entry['measure']})"
        for entry in model["bounds_slack"]
    ]


def check_no_authority(document: dict) -> list[str]:
    """This measurement must never raise the standing of what it measures."""
    model = measure(document)
    problems: list[str] = []
    if not str(model["programme"]["authority"]).startswith("NONE"):
        problems.append("this measurement claims an authority")
    for entry in model["capabilities"]:
        if entry["action"] == ACTION_CREATE:
            problems.append(f"{entry['id']}: dispositioned CREATE, which would manufacture a parallel authority")
    for finding in model["findings"]:
        if str(finding["disposition"]) not in ("REGISTERED", "GOVERNED"):
            problems.append(f"{finding['id']}: a divergence was decided rather than referred")
    if model["terminal_hits"]:
        problems += [f"a located identity instrument declares a terminal state: {hit}" for hit in model["terminal_hits"]]
    return problems


GUARDS = {
    "check-declaration": check_declaration,
    "check-no-enumeration": check_no_enumeration,
    "check-write-scope": check_write_scope,
    "check-determinism": check_determinism,
    "check-knowledge-once": check_knowledge_once,
    "check-record-immutability": check_record_immutability,
    "check-no-identity-minting": check_no_identity_minting,
    "check-bounds-tight": check_bounds_tight,
    "check-no-authority": check_no_authority,
}


# --------------------------------------------------------------------------- entry point


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    parser.add_argument("--render", action="store_true", help="regenerate the registers")
    parser.add_argument("--gate", action="store_true", help="fail-closed identity conformance gate")
    parser.add_argument("--quiet", action="store_true")
    for name in GUARDS:
        parser.add_argument(f"--{name}", action="store_true")
    args = parser.parse_args(argv)

    try:
        document = load_declaration()
    except FailClosed as exc:
        print(f"UIS-001 ABORT: {exc}", file=sys.stderr)
        return 2

    selected = [name for name in GUARDS if getattr(args, name.replace("-", "_"))]
    if selected:
        failed = False
        for name in selected:
            try:
                problems = GUARDS[name](document)
            except FailClosed as exc:
                print(f"UIS-001 ABORT: {exc}", file=sys.stderr)
                return 2
            if problems:
                failed = True
                print(f"UIS-001 {name}: FAIL ({len(problems)})", file=sys.stderr)
                for problem in problems[:40]:
                    print(f"  - {problem}", file=sys.stderr)
            else:
                print(f"UIS-001 {name}: PASS")
        return 1 if failed else 0

    try:
        model = measure(document)
    except FailClosed as exc:
        print(f"UIS-001 ABORT: {exc}", file=sys.stderr)
        return 2

    written = write_registers(model)
    counters = model["counters"]
    if not args.quiet:
        print(
            f"UIS-001: {model['determination']} "
            f"| identities={model['counts']['recorded_identities']}rec/{model['counts']['registered_identities']}reg "
            f"| planes={len(model['planes']) - counters['planes_unrealized']}/{len(model['planes'])} "
            f"| mechanisms={len(model['mechanisms'])} "
            f"| authority={len(model['realization']) - counters['realization_obligations_unmet']}/{len(model['realization'])} "
            f"| laws={len(model['laws']) - counters['laws_unbound']}/{len(model['laws'])}bound"
            f",{sum(1 for law in model['laws'] if law['measurable'])}measured "
            f"| capabilities={len(model['capabilities'])}({counters['capabilities_created']}create) "
            f"| bookkeeping={len(model['bookkeeping']) - counters['bookkeeping_unbound']}/{len(model['bookkeeping'])} "
            f"| unbounded={sum(1 for d in model['unboundedness'] if d['satisfied'])}/{len(model['unboundedness'])} "
            f"| namespaces={model['counts']['live_namespaces']}live/{counters['namespaces_ungoverned']}ungoverned "
            f"| criteria={sum(1 for v in model['validations'] if v['satisfied'])}/{len(model['validations'])} "
            f"| immutable={str(model['immutability']['disjoint']).lower()} "
            f"| gate={model['gate']} | seal={model['seal_sha256'][:16]}"
        )
        print(f"wrote {len(written)} artifacts to {HERE.relative_to(REPO).as_posix()}")
        for entry in model["validations"]:
            if entry["blocking"] and not entry["satisfied"]:
                print(
                    f"  BLOCKING {entry['id']} {entry['dimension']}: "
                    f"{entry['value']} {entry['comparator']} {entry['expect']} failed",
                    file=sys.stderr,
                )

    if args.gate and model["gate"] != "OPEN":
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
