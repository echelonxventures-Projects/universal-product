#!/usr/bin/env python3
"""UCL-000001 — Universal Constitutional Lifecycle.

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates no lifecycle, opens no
registry, mints no identifier, declares no namespace, admits no capability and
certifies nothing. It DISCOVERS the constitutional stage graph the repository has
already legislated, normalizes it into Canonical Knowledge Objects, composes the
declared graph types, measures whether each stage is executable, and executes the
discovered graph as a deterministic traversal.

Everything it enforces is read from ``ucl-declaration.json``. This source file
contains no stage, no stage name, no stage ordering, no capability, no owner path,
no graph type, no relation type and no serialization parser choice: admitting a
stage, a capability, an object kind, a relation, a graph type, a provider, an
adapter, a serialization, an obligation, a property or an expansion axis is an
append-only edit to DATA and requires no change here (PR-07 Zero Enumeration).

Discovery pipeline (metadata in, Canonical Knowledge Objects out):

    Metadata Provider  — WHERE constitutional metadata lives, in which serialization
        ↓
    Metadata Adapter   — HOW those records normalize into CKOs of a declared kind
        ↓
    Canonical Knowledge Objects — kind, identity, owner, authority, provenance, relations
        ↓
    Discovery Engine   — composes graphs, evaluates obligations, orders, executes

The engine never sees a file, a format or a field name below the adapter layer, so
replacing a serialization or a storage technology changes no object kind, no
relation, no graph type, no obligation and no stage.

Implementation independence: only a provider whose discovery class MAY ORIGINATE
contributes objects. Implementation source is read as EVIDENCE only — to confirm a
symbol exists — and ``--check-implementation-independence`` fails closed if any
object or relation is ever traced to an evidence-class provider.

Determinism: the output is a pure function of tracked repository content. Nothing
here reads the wall clock, the commit identity (RFP-2) or the working tree's own
status (RFP-3), so the emitted bytes are stable and the repository remains a fixed
point. Execution resolves and records; it never re-invokes the stages' own engines,
which would create the self-observation topology RFP-3 forbids.

Exit semantics:
  0  gate OPEN / guard PASS
  1  gate CLOSED / guard FAIL
  2  fail-closed abort — the declaration is unusable, so no verdict may be asserted
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DECLARATION = HERE / "ucl-declaration.json"
MODEL = HERE / "ucl.json"
OWN_PREFIX = HERE.relative_to(REPO).as_posix() + "/"

REQUIRED_SECTIONS = (
    "programme",
    "determination",
    "cko_model",
    "serializations",
    "discovery_classes",
    "metadata_providers",
    "metadata_adapters",
    "provider_discovery",
    "reference_normalizations",
    "applicability_classes",
    "relationship_model",
    "semantic_identity",
    "knowledge_extraction",
    "elevation_measures",
    "self_evolution_path",
    "readiness_dimensions",
    "derived_counters",
    "graph_types",
    "lifecycle_authorities",
    "obligation_rules",
    "property_rules",
    "admission_paths",
    "expansion_axes",
    "execution",
    "unboundedness",
    "hygiene",
    "capabilities",
    "record_set",
    "validations",
    "exit_criteria",
    "findings",
    "law_source",
)

PAGES = (
    "00-UNIVERSAL-CONSTITUTIONAL-LIFECYCLE-DASHBOARD.md",
    "01-CONSTITUTIONAL-STAGE-GRAPH-REGISTER.md",
    "02-STAGE-OBLIGATION-BINDING-MATRIX.md",
    "03-STAGE-PROPERTY-CONFORMANCE-REGISTER.md",
    "04-LIFECYCLE-AUTHORITY-CROSSWALK-REGISTER.md",
    "05-CANONICAL-KNOWLEDGE-OBJECT-AND-GRAPH-REGISTER.md",
    "06-METADATA-PROVIDER-AND-ADAPTER-REGISTER.md",
    "07-OPEN-WORLD-EXPANSION-AXIS-REGISTER.md",
    "08-DETERMINISTIC-EXECUTION-AND-REPLAY-REGISTER.md",
    "09-VALIDATION-REPORT.md",
    "10-CERTIFICATION-REPORT.md",
    "11-ADMISSION-AND-DISPOSITION-DETERMINATION.md",
    "12-KNOWLEDGE-EXTRACTION-AND-CAPABILITY-ELEVATION-REGISTER.md",
    "13-SELF-EVOLUTION-AND-OMEGA-E05-READINESS-CERTIFICATION.md",
)

ACTION_CREATE = "CREATE"
ACTION_REUSE = "REUSE"
ACTION_EXTEND = "EXTEND"
STATUS_EXISTING = "EXISTING"
STATUS_PARTIAL = "PARTIAL"
STATUS_MISSING = "MISSING"
CLASS_MAY_ORIGINATE = "may_originate"
ID_SEPARATOR = "::"
SAMPLE = 12


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
    if not relative:
        return None
    target = REPO / relative
    if not target.is_file():
        return None
    try:
        return target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):  # pragma: no cover - defensive
        return None


def exists(relative: str) -> bool:
    return bool(relative) and (REPO / relative).exists()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


# ------------------------------------------------------- serialization reader table


def _read_json(relative: str) -> Any:
    raw = read_text(relative)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FailClosed(f"a provider is not valid for its declared serialization: {relative}: {exc}") from exc


def _read_toml(relative: str) -> Any:
    target = REPO / relative
    if not target.is_file():
        return None
    try:
        with target.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise FailClosed(f"a provider is not valid for its declared serialization: {relative}: {exc}") from exc


def _read_text_document(relative: str) -> Any:
    raw = read_text(relative)
    return None if raw is None else {}


READERS = {
    "json": _read_json,
    "toml": _read_toml,
    "text": _read_text_document,
}


def reader_for(document: dict, serialization_id: str) -> Any:
    """The reader a declared serialization dispatches to, or None if unregistered.

    An unregistered serialization is REPORTED, never fatal: the registry must be
    extendable before it is implemented, or it is not open.
    """
    for entry in document["serializations"]:
        if str(entry["id"]) != str(serialization_id):
            continue
        if not entry.get("registered"):
            return None
        return READERS.get(str(entry["reader"]))
    return None


# --------------------------------------------------------------- pointer resolution


def follow(payload: Any, pointer: str) -> Any:
    """Walk a dotted pointer. An empty pointer resolves to the document root."""
    current = payload
    if not pointer:
        return current
    for step in str(pointer).split("."):
        if isinstance(current, dict) and step in current:
            current = current[step]
        else:
            return None
    return current


def collection(payload: Any) -> list[tuple[str, Any]]:
    """Normalize whatever a pointer yielded into (key, record) pairs.

    A list is keyed by nothing and a mapping is keyed by its own keys, so a keyed
    metadata store needs no adapter change and no engine change.
    """
    if isinstance(payload, list):
        return [("", item) for item in payload]
    if isinstance(payload, dict):
        return [(str(key), value) for key, value in payload.items()]
    return []


# ------------------------------------------------------------- provider discovery


def discover_providers(document: dict) -> list[dict]:
    """Declared providers, plus every provider the located pattern discovers.

    The pattern is declared; the discovered providers are NOT listed anywhere, which
    is what keeps a future stage automatically discoverable and stops this
    declaration from becoming a stage enumeration by the back door.
    """
    providers: list[dict] = []
    for entry in document["metadata_providers"]:
        providers.append(
            {
                "id": str(entry["id"]),
                "name": str(entry["name"]),
                "owner": str(entry["owner"]),
                "serialization": str(entry["serialization"]),
                "discovery_class": str(entry["discovery_class"]),
                "discovered": False,
                "open": None,
                "admission": "",
                "closed_enumeration": None,
                "located": exists(str(entry["owner"])),
            }
        )

    spec = document["provider_discovery"]
    root = REPO / str(spec["root"])
    suffix = str(spec["suffix"])
    fields = spec["openness_fields"]
    found: list[Path] = []
    if root.is_dir():
        found = sorted(path for path in root.iterdir() if path.is_file() and path.name.endswith(suffix))
    for path in found:
        relative = path.relative_to(REPO).as_posix()
        read = reader_for(document, str(spec["serialization"]))
        payload = read(relative) if read else None
        header = follow(payload, str(spec["openness_pointer"])) or {}
        providers.append(
            {
                "id": str(spec["id"]),
                "name": str(header.get("name") or relative),
                "owner": relative,
                "serialization": str(spec["serialization"]),
                "discovery_class": str(spec["discovery_class"]),
                "discovered": True,
                "open": header.get(str(fields["open"])),
                "admission": str(header.get(str(fields["admission"])) or ""),
                "closed_enumeration": header.get(str(fields["closed_enumeration"])),
                "located": True,
            }
        )
    return providers


# ------------------------------------------------------------- adapter normalization


def _strings(value: Any) -> list[str]:
    """Every string a value could be carrying, at any of its shapes."""
    out: list[str] = []
    if value is None:
        return out
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, dict):
        for item in value.values():
            out.extend(_strings(item))
        return out
    if isinstance(value, list):
        for item in value:
            out.extend(_strings(item))
        return out
    return out


def _relation_groups(value: Any) -> list[list[str]]:
    """Group a relation value into CANDIDATE SETS, one set per intended target.

    A relation target may be written as a bare string, a list of strings, or a list of
    records that name the target alongside the adapter it belongs to. A record names
    exactly one target, so all of its strings form ONE candidate set and resolution
    decides which of them is the target. Collecting them as candidates rather than as
    targets is what lets the engine read any metadata schema without knowing which key
    holds the reference — and stops a schema's own field values from being mistaken
    for dangling references.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [[value]] if value else []
    if isinstance(value, dict):
        group = _strings(value)
        return [group] if group else []
    if isinstance(value, list):
        groups: list[list[str]] = []
        for item in value:
            groups.extend(_relation_groups(item))
        return groups
    return []


def normalize(document: dict, providers: list[dict]) -> tuple[list[dict], list[dict]]:
    """Run every adapter over its provider and emit Canonical Knowledge Objects."""
    by_id: dict[str, list[dict]] = {}
    for provider in providers:
        by_id.setdefault(provider["id"], []).append(provider)

    classes = {str(entry["id"]): bool(entry.get(CLASS_MAY_ORIGINATE)) for entry in document["discovery_classes"]}
    ckos: list[dict] = []
    reports: list[dict] = []

    for adapter in document["metadata_adapters"]:
        adapter_id = str(adapter["id"])
        provider_id = str(adapter["provider"])
        pointer = str(adapter.get("pointer") or "")
        field_map = adapter.get("field_map") or {}
        relation_map = adapter.get("relation_map") or {}
        kind = str(adapter["cko_kind"])
        matched = by_id.get(provider_id) or []
        emitted = 0
        resolved = bool(matched)
        for provider in matched:
            read = reader_for(document, provider["serialization"])
            if read is None or not provider["located"]:
                resolved = False
                continue
            payload = read(provider["owner"])
            records = collection(follow(payload, pointer))
            if not records:
                resolved = False
            may_originate = classes.get(provider["discovery_class"], False)
            if not may_originate:
                # An evidence-class provider contributes nothing. Recorded so the
                # separation is measured rather than assumed.
                continue
            for key, record in records:
                if not isinstance(record, dict):
                    record = {"": record}
                identity = str(record.get(str(field_map.get("id") or ""), "") or key or "")
                if not identity:
                    continue
                attributes: dict[str, Any] = {}
                for neutral, native in field_map.items():
                    if neutral == "id" or not native:
                        continue
                    if native in record:
                        attributes[str(neutral)] = record[native]
                relations: list[dict] = []
                for relation, native in relation_map.items():
                    for group in _relation_groups(record.get(str(native))):
                        relations.append({"relation": str(relation), "candidates": group})
                ckos.append(
                    {
                        "cko_id": adapter_id + ID_SEPARATOR + identity,
                        "record_id": identity,
                        "kind": kind,
                        "name": str(record.get(str(field_map.get("name") or ""), "") or identity),
                        "semantic_id": semantic_identity(document, kind, identity),
                        "attributes": attributes,
                        "relations": relations,
                        "provenance": {
                            "provider": provider["id"],
                            "provider_owner": provider["owner"],
                            "adapter": adapter_id,
                            "discovery_class": provider["discovery_class"],
                            "serialization": provider["serialization"],
                        },
                    }
                )
                emitted += 1
        reports.append(
            {
                "id": adapter_id,
                "name": str(adapter["name"]),
                "provider": provider_id,
                "pointer": pointer,
                "kind": kind,
                "providers_matched": len(matched),
                "objects": emitted,
                "resolved": resolved and emitted > 0,
                "note": str(adapter.get("note", "")),
            }
        )
    return ckos, reports


# ------------------------------------------------------------------ relation resolution


def semantic_identity(document: dict, kind: str, record_id: str) -> str:
    """The immutable constitutional identity of an entity.

    Derived ONLY from what the entity IS. Every input the invariants permit to evolve —
    representation, serialization, storage, transport, runtime, implementation and
    location — is excluded by construction, so moving a file, changing a format or
    migrating a store cannot mint a new identity. A digest is used, but only over
    immutable constitutional identity fields: a digest over anything mutable would be a
    fingerprint masquerading as an identity. The inputs are read from the declaration,
    so the derivation is itself governed rather than hard-coded.
    """
    spec = document["semantic_identity"]
    available = {"kind": kind, "record_id": record_id}
    payload = [available.get(str(name), "") for name in spec["inputs"]]
    return digest(canonical(payload))


def relationship_identity(document: dict, relation: str, source: str, target: str) -> str:
    """The constitutional identity of a relationship, from its participants' identities.

    Never from a handle, an adapter, a provider, a serialization or a path: those are
    the mutable implementation characteristics the invariants forbid identity from
    resting on.
    """
    spec = document["relationship_model"]
    available = {
        "relation": relation,
        "source_semantic_id": source,
        "target_semantic_id": target,
    }
    payload = [available.get(str(name), "") for name in spec["identity_inputs"]]
    return digest(canonical(payload))


def relationship_objects(document: dict, edges: list[dict], by_cko: dict[str, dict], registry_identity: dict[str, str]) -> list[dict]:
    """Every relationship, as a first-class Canonical Knowledge Object.

    A relationship is a constitutionally governed entity, so it holds its own object and
    its own constitutional identity, and it is discovered through the same provider and
    adapter pipeline as an entity — it carries the provenance of the metadata that
    declared it. Its participants are recorded as ATTRIBUTES rather than as further
    relations, which keeps the model finite while leaving the relationship governable.

    A target that is a located artifact is resolved to its REGISTERED constitutional
    identity. A target the repository has deliberately not registered carries none, and
    that is reported rather than patched with its path.
    """
    spec = document["relationship_model"]
    if not spec.get("first_class"):
        return []
    kind = str(spec["cko_kind"])
    order = [str(step) for step in spec["target_identity_resolution"]]
    out: list[dict] = []
    for edge in edges:
        origin = by_cko.get(edge["source"]) or {}
        source_identity = str(origin.get("semantic_id") or "")
        target_identity = ""
        for step in order:
            if target_identity:
                break
            if step == "cko":
                for candidate in edge["resolved"]:
                    other = by_cko.get(candidate)
                    if other is not None:
                        target_identity = str(other.get("semantic_id") or "")
                        break
            elif step == "registry":
                target_identity = registry_identity.get(str(edge["target"]), "")
        record_id = "|".join([str(edge["relation"]), source_identity, target_identity])
        identity = relationship_identity(document, str(edge["relation"]), source_identity, target_identity)
        out.append(
            {
                # A HANDLE, not an identity: it disambiguates every declared relationship
                # even where a target carries no registered constitutional identity.
                "cko_id": kind + ID_SEPARATOR + digest(
                    "|".join([str(edge["source"]), str(edge["relation"]), str(edge["target"])])
                )[:32],
                "record_id": record_id,
                "kind": kind,
                "name": str(edge["relation"]),
                "semantic_id": identity,
                "target_identified": bool(target_identity),
                "attributes": {
                    "source": edge["source"],
                    "relation": edge["relation"],
                    "target": edge["target"],
                    "target_class": edge["target_class"],
                },
                "relations": [],
                "provenance": dict(origin.get("provenance") or {}),
            }
        )
    return out


def index_ckos(ckos: list[dict]) -> tuple[dict[str, dict], dict[str, list[str]]]:
    by_cko = {entry["cko_id"]: entry for entry in ckos}
    by_record: dict[str, list[str]] = {}
    for entry in ckos:
        by_record.setdefault(entry["record_id"], []).append(entry["cko_id"])
    return by_cko, by_record


def identity_collisions(ckos: list[dict]) -> list[str]:
    """Entities holding more than one Canonical Knowledge Object.

    Constitutional law: every governed entity possesses EXACTLY ONE CKO, and that
    object is its immutable constitutional identity. An entity is identified by its
    kind and its recorded identity, so two objects sharing both are two identities
    for one entity — a duplication no derived view could later reconcile.
    """
    seen: dict[tuple[str, str], list[str]] = {}
    for entry in ckos:
        seen.setdefault((entry["kind"], entry["record_id"]), []).append(entry["cko_id"])
    return sorted(f"{kind}/{record}" for (kind, record), holders in seen.items() if len(holders) > 1)


def _variants(value: str, rules: list[dict]) -> list[tuple[str, str]]:
    """Every reading a declared normalization rule permits, with the rule that gave it.

    The original reading always comes first, so a reference that resolves as written is
    never reinterpreted. Nothing here knows any instrument, any path or any identifier.
    """
    out: list[tuple[str, str]] = [(value, "")]
    for rule in rules:
        kind = str(rule.get("rule") or "")
        rule_id = str(rule.get("id") or "")
        if kind == "trim-annotation":
            separator = str(rule.get("separator") or "")
            if separator and separator in value:
                out.append((value.split(separator, 1)[0].strip(), rule_id))
        elif kind == "trim-section":
            for separator in rule.get("separators") or []:
                if str(separator) in value:
                    out.append((value.split(str(separator), 1)[0].strip(), rule_id))
        elif kind == "prefix-unique":
            for candidate, _ in list(out):
                target = REPO / candidate
                if target.exists() or not candidate:
                    continue
                parent = target.parent
                if not parent.is_dir():
                    continue
                matches = sorted(
                    item.relative_to(REPO).as_posix()
                    for item in parent.iterdir()
                    if item.name.startswith(target.name)
                )
                if len(matches) == 1:
                    out.append((matches[0], rule_id))
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for candidate, rule_id in out:
        if candidate and candidate not in seen:
            seen.add(candidate)
            unique.append((candidate, rule_id))
    return unique


def resolve_relations(ckos: list[dict], rules: list[dict]) -> list[dict]:
    """Classify every relation as pointing at one CKO, a located artifact, or nothing.

    Each relation carries a CANDIDATE SET naming exactly one intended target. The
    first candidate that resolves to a Canonical Knowledge Object is the target,
    because a relation between governed entities is a relation between their CKOs;
    only if none resolves is a located artifact accepted, under the declared reading
    rules; and only if neither does the relation dangle.
    """
    by_cko, by_record = index_ckos(ckos)
    edges: list[dict] = []
    for entry in ckos:
        for relation in entry["relations"]:
            candidates = [str(c) for c in relation["candidates"]]
            target, kind, resolved, applied = (candidates[0] if candidates else ""), "dangling", [], ""
            for candidate in candidates:
                if candidate in by_cko:
                    target, kind, resolved = candidate, "cko", [candidate]
                    break
                if candidate in by_record:
                    target, kind, resolved = candidate, "cko", list(by_record[candidate])
                    break
            if kind == "dangling":
                for candidate in candidates:
                    for variant, rule_id in _variants(candidate, rules):
                        if exists(variant):
                            target, kind, resolved, applied = variant, "artifact", [variant], rule_id
                            break
                    if kind != "dangling":
                        break
            edges.append(
                {
                    "source": entry["cko_id"],
                    "relation": str(relation["relation"]),
                    "target": target,
                    "candidates": candidates,
                    "target_class": kind,
                    "resolved": resolved,
                    "normalized_by": applied,
                    "ambiguous": len(resolved) > 1,
                }
            )
    return edges


# ------------------------------------------------------------------------ rule engine


def _zone(value: str) -> str:
    """The zone a located path lives in — its parent directory.

    Zone is the granularity at which the repository grants and withholds scope: a
    registry admits a directory, and a check owns a directory. Comparing at file
    granularity would make every unlisted file look out of scope.
    """
    text = str(value).strip()
    return text.rsplit("/", 1)[0] if "/" in text else ""


def _related(entry: dict, edges_by_source: dict[str, list[dict]], relation: str, kind_filter: str, by_cko: dict[str, dict]) -> list[dict]:
    out: list[dict] = []
    for edge in edges_by_source.get(entry["cko_id"], []):
        if edge["relation"] != relation:
            continue
        for target in edge["resolved"]:
            other = by_cko.get(target)
            if other is None:
                continue
            if kind_filter and other["kind"] != kind_filter:
                continue
            out.append(other)
    return out


def _executable_resolves(value: Any) -> bool:
    """Does a declared invocation name a program the repository actually holds?

    The invocation is a token sequence whose interpreter and flags are not paths;
    the program is whichever token resolves, so no argument convention is assumed.
    """
    for token in _strings(value):
        if exists(token):
            return True
    return False


def evaluate(rule: dict, entry: dict, context: dict) -> bool:  # noqa: C901 - one branch per declared mechanic
    kind = str(rule.get("kind") or "")
    edges_by_source = context["edges_by_source"]
    by_cko = context["by_cko"]

    if kind == "all_of":
        return all(evaluate(item, entry, context) for item in rule.get("rules") or [])
    if kind == "any_of":
        return any(evaluate(item, entry, context) for item in rule.get("rules") or [])
    if kind == "attribute_present":
        return bool(str(entry["attributes"].get(str(rule["attribute"]), "") or "").strip())
    if kind == "attribute_resolves":
        return exists(str(entry["attributes"].get(str(rule["attribute"]), "") or ""))
    if kind == "originated_by_class":
        return entry["provenance"]["discovery_class"] == str(rule["class"])
    if kind == "relation_to_kind":
        return bool(_related(entry, edges_by_source, str(rule["relation"]), str(rule.get("kind_filter") or ""), by_cko))
    if kind == "relation_targets_resolve":
        found = [
            edge
            for edge in edges_by_source.get(entry["cko_id"], [])
            if edge["relation"] == str(rule["relation"])
        ]
        return bool(found) and all(edge["target_class"] != "dangling" for edge in found)
    if kind == "related_attribute_resolves":
        for other in _related(entry, edges_by_source, str(rule["relation"]), str(rule.get("kind_filter") or ""), by_cko):
            if _executable_resolves(other["attributes"].get(str(rule["attribute"]))):
                return True
        return False
    if kind == "related_attribute_true":
        for other in _related(entry, edges_by_source, str(rule["relation"]), str(rule.get("kind_filter") or ""), by_cko):
            if bool(other["attributes"].get(str(rule["attribute"]))):
                return True
        return False
    if kind == "transitive_relation_present":
        for other in _related(entry, edges_by_source, str(rule["relation"]), str(rule.get("kind_filter") or ""), by_cko):
            if _related(other, edges_by_source, str(rule["then_relation"]), "", by_cko):
                return True
        return False
    if kind == "transitive_relation_attribute_true":
        attribute = str(rule["attribute"])
        for other in _related(entry, edges_by_source, str(rule["relation"]), str(rule.get("kind_filter") or ""), by_cko):
            for final in _related(other, edges_by_source, str(rule["then_relation"]), "", by_cko):
                if bool(final["attributes"].get(attribute)):
                    return True
        return False
    if kind == "attribute_in_kind":
        value = str(entry["attributes"].get(str(rule["attribute"]), "") or "")
        if not value:
            return False
        return value in context["attribute_space"].get(
            (str(rule["kind_filter"]), str(rule["target_attribute"])), frozenset()
        )
    if kind == "scope_covered":
        # Is the zone this attribute lives in already covered by objects of that kind?
        # This asks whether Repository Truth puts the entity IN SCOPE for an
        # obligation, which is a different question from whether it satisfies it.
        value = str(entry["attributes"].get(str(rule["attribute"]), "") or "")
        if not value:
            return False
        return _zone(value) in context["scope_space"].get(
            (str(rule["kind_filter"]), str(rule["target_attribute"])), frozenset()
        )
    if kind == "edge_participation":
        relation = str(rule.get("relation") or "")
        outgoing = [e for e in edges_by_source.get(entry["cko_id"], []) if not relation or e["relation"] == relation]
        incoming = context["incoming"].get(entry["cko_id"], [])
        incoming = [e for e in incoming if not relation or e["relation"] == relation]
        return bool(outgoing or incoming)
    if kind == "admission_path_open":
        return context["admission_open"]
    if kind == "obligation_satisfied":
        return bool(context["obligation_state"].get(entry["cko_id"], {}).get(str(rule["obligation"])))
    raise FailClosed(f"a declared rule names a mechanic that does not exist: {kind!r}")


# ------------------------------------------------------------------------- ordering


def topological(nodes: list[dict], edges_by_source: dict[str, list[dict]], relation: str) -> tuple[list[str], list[str]]:
    """Order the discovered graph. Cycles are reported, never broken silently."""
    ids = [entry["cko_id"] for entry in nodes]
    present = set(ids)
    ordinal = {
        entry["cko_id"]: _as_int(entry["attributes"].get("ordinal"))
        for entry in nodes
    }
    prerequisites: dict[str, set[str]] = {node: set() for node in ids}
    for node in ids:
        for edge in edges_by_source.get(node, []):
            if edge["relation"] != relation:
                continue
            for target in edge["resolved"]:
                if target in present:
                    prerequisites[node].add(target)

    order: list[str] = []
    remaining = dict(prerequisites)
    while remaining:
        ready = sorted(
            (node for node, need in remaining.items() if not (need - set(order))),
            key=lambda node: (ordinal[node], node),
        )
        if not ready:
            break
        for node in ready:
            order.append(node)
            del remaining[node]
    return order, sorted(remaining)


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


# ------------------------------------------------------------------------- execution


def execute(goal: str, order: list[str], by_cko: dict[str, dict], obligation_state: dict, property_state: dict, graph_digest: str) -> dict:
    """Execute the discovered graph as a deterministic constitutional traversal.

    This resolves and records; it does not re-invoke the stages' own engines. Those
    are already executed by the fixed-point pipeline, and invoking them from here
    would make this engine observe a run of itself.
    """
    steps: list[dict] = []
    for position, cko_id in enumerate(order, start=1):
        entry = by_cko[cko_id]
        obligations = obligation_state.get(cko_id, {})
        properties = property_state.get(cko_id, {})
        steps.append(
            {
                "position": position,
                "cko_id": cko_id,
                "stage": entry["name"],
                "owner": str(entry["attributes"].get("owner", "") or ""),
                "obligations_bound": sum(1 for value in obligations.values() if value),
                "obligations_total": len(obligations),
                "properties_held": sum(1 for value in properties.values() if value),
                "properties_total": len(properties),
                "admitted": bool(obligations) and all(
                    obligations.get(name) for name in ("OBL-OWNER", "OBL-AUTHORITY", "OBL-DECLARATION") if name in obligations
                ),
            }
        )
    goal_digest = digest(goal)
    record = {
        "goal": goal,
        "goal_digest": goal_digest,
        "graph_digest": graph_digest,
        "steps": steps,
        "stages_traversed": len(steps),
    }
    record["run_id"] = digest(canonical({"goal_digest": goal_digest, "graph_digest": graph_digest}))
    return record


# ----------------------------------------------------------------------- measurement


def compare(value: int, comparator: str, expect: int) -> bool:
    if comparator == "==":
        return value == expect
    if comparator == "<=":
        return value <= expect
    if comparator == ">=":
        return value >= expect
    raise FailClosed(f"unknown comparator in the declaration: {comparator!r}")


def symbol_present(relative: str, symbol: str) -> bool:
    """EVIDENCE EXTRACTION ONLY. Confirms a definition exists, originates nothing."""
    source = read_text(relative)
    if source is None:
        return False
    pattern = re.compile(
        rf"^\s*(?:def\s+{re.escape(symbol)}\b"
        rf"|class\s+{re.escape(symbol)}\b"
        rf"|{re.escape(symbol)}\s*[:=])",
        re.MULTILINE,
    )
    return bool(pattern.search(source)) or f'"{symbol}"' in source


def _kind_of(document: dict, adapter_id: str) -> str:
    """The object kind a declared adapter emits."""
    for adapter in document["metadata_adapters"]:
        if str(adapter["id"]) == str(adapter_id):
            return str(adapter["cko_kind"])
    return ""


def _registry_adapter(document: dict) -> str:
    """The declared adapter whose objects carry registered constitutional identity."""
    return str(document["relationship_model"].get("target_identity_adapter") or "")


def _applicability_tokens(document: dict) -> tuple[str, str, str]:
    """The three applicability tokens, read from the declaration by their own semantics.

    Identified by what each class says about participation rather than by its name, so
    renaming a class in the registry cannot silently change which obligations gate.
    """
    always = conditional = never = ""
    for entry in document["applicability_classes"]:
        participates = str(entry.get("participates", "")).lower()
        if participates.startswith("always"):
            always = str(entry["id"])
        elif participates.startswith("never"):
            never = str(entry["id"])
        else:
            conditional = str(entry["id"])
    if not (always and conditional and never):
        raise FailClosed("the applicability registry does not declare all three participation classes")
    return always, conditional, never


def measure(document: dict) -> dict:  # noqa: C901 - one measurement per declared concern
    providers = discover_providers(document)
    ckos, adapter_reports = normalize(document, providers)
    edges = resolve_relations(ckos, document["reference_normalizations"])
    by_cko, _ = index_ckos(ckos)

    edges_by_source: dict[str, list[dict]] = {}
    incoming: dict[str, list[dict]] = {}
    for edge in edges:
        edges_by_source.setdefault(edge["source"], []).append(edge)
        for target in edge["resolved"]:
            incoming.setdefault(target, []).append(edge)

    known_kinds = {str(entry["kind"]) for entry in document["cko_model"]["kinds"]}
    known_relations = {str(entry["relation"]) for entry in document["cko_model"]["relation_types"]}

    attribute_space: dict[tuple[str, str], frozenset[str]] = {}
    scope_space: dict[tuple[str, str], frozenset[str]] = {}
    for rule in document["obligation_rules"]:
        for item in [rule, rule.get("condition") or {}, *(rule.get("rules") or [])]:
            mechanic = str(item.get("kind") or "")
            if mechanic not in ("attribute_in_kind", "scope_covered"):
                continue
            key = (str(item["kind_filter"]), str(item["target_attribute"]))
            values = [
                str(entry["attributes"].get(key[1], "") or "")
                for entry in ckos
                if entry["kind"] == key[0]
            ]
            if mechanic == "attribute_in_kind" and key not in attribute_space:
                attribute_space[key] = frozenset(v for v in values if v)
            if mechanic == "scope_covered" and key not in scope_space:
                scope_space[key] = frozenset(_zone(v) for v in values if v)

    # The stage plane is whatever kind the stage-manifest adapter emits, read from the
    # declaration rather than named here.
    stage_kind = ""
    manifest_adapter = ""
    for adapter in document["metadata_adapters"]:
        if str(adapter["provider"]) == str(document["provider_discovery"]["id"]):
            stage_kind = str(adapter["cko_kind"])
            manifest_adapter = str(adapter["id"])
            break
    if not stage_kind:
        raise FailClosed("no adapter is bound to the discovered provider surface")
    stages = sorted((entry for entry in ckos if entry["kind"] == stage_kind), key=lambda e: (_as_int(e["attributes"].get("ordinal")), e["cko_id"]))

    discovered_providers = [p for p in providers if p["discovered"]]
    admission_open = bool(discovered_providers) and all(
        p["open"] is True and p["closed_enumeration"] is False and p["admission"] for p in discovered_providers
    )

    context = {
        "edges_by_source": edges_by_source,
        "incoming": incoming,
        "by_cko": by_cko,
        "attribute_space": attribute_space,
        "scope_space": scope_space,
        "admission_open": admission_open,
        "obligation_state": {},
    }

    # Applicability is determined BEFORE satisfaction. An obligation the repository
    # does not place the stage in scope for is NOT_APPLICABLE, and is reported rather
    # than counted as unbound: counting it would manufacture a deficiency.
    classes = {str(entry["id"]) for entry in document["applicability_classes"]}
    required_class, conditional_class, inapplicable_class = _applicability_tokens(document)
    obligation_state: dict[str, dict[str, bool]] = {}
    applicability_state: dict[str, dict[str, str]] = {}
    for entry in stages:
        state: dict[str, bool] = {}
        applies: dict[str, str] = {}
        for rule in document["obligation_rules"]:
            name = str(rule["id"])
            declared = str(rule.get("applicability") or required_class)
            if declared not in classes:
                raise FailClosed(f"{name}: declares an unregistered applicability {declared!r}")
            if declared == conditional_class:
                condition = rule.get("condition")
                if not condition:
                    raise FailClosed(f"{name}: declared conditional with no governing condition")
                resolved = declared if evaluate(condition, entry, context) else inapplicable_class
            else:
                resolved = declared
            applies[name] = resolved
            state[name] = evaluate(rule, entry, context)
        obligation_state[entry["cko_id"]] = state
        applicability_state[entry["cko_id"]] = applies
    context["obligation_state"] = obligation_state

    property_state: dict[str, dict[str, bool]] = {}
    for entry in stages:
        state = {}
        for rule in document["property_rules"]:
            state[str(rule["id"])] = evaluate(rule, entry, context)
        property_state[entry["cko_id"]] = state

    dependency_relation = ""
    for gtype in document["graph_types"]["types"]:
        if stage_kind in [str(k) for k in gtype["node_kinds"]] and gtype["edge_relations"]:
            for relation in gtype["edge_relations"]:
                if any(e["relation"] == str(relation) for e in edges if e["source"].startswith(manifest_adapter)):
                    dependency_relation = str(relation)
                    break
        if dependency_relation:
            break
    order, cycles = topological(stages, edges_by_source, dependency_relation)

    graph_digest = digest(
        canonical(
            [
                {"cko_id": e["cko_id"], "kind": e["kind"], "relations": sorted(canonical(r) for r in e["relations"])}
                for e in sorted(ckos, key=lambda item: item["cko_id"])
            ]
        )
    )

    # ---- relationships as first-class objects, and the invariant constitutional identity
    registry_kind = _kind_of(document, _registry_adapter(document))
    registry_identity = {
        str(entry["attributes"].get("owner", "") or ""): str(entry.get("semantic_id") or "")
        for entry in ckos
        if entry["kind"] == registry_kind
    }
    registry_identity.pop("", None)
    relationships = relationship_objects(document, edges, by_cko, registry_identity)
    all_ckos = ckos + relationships
    semantic_seen: dict[str, set[str]] = {}
    for entry in all_ckos:
        # Only DETERMINATE identities can be compared for collision. A relationship whose
        # target carries no registered constitutional identity has an indeterminate
        # identity by construction, and the honest treatment is to report that — not to
        # substitute the target's path, because a path is a location and locations may
        # evolve, so using one would turn a file move into an identity change.
        if entry["kind"] == str(document["relationship_model"]["cko_kind"]) and not entry.get("target_identified"):
            continue
        semantic_seen.setdefault(str(entry.get("semantic_id") or ""), set()).add(entry["cko_id"])
    semantic_clashes = sorted(
        key for key, holders in semantic_seen.items() if key and len(holders) > 1
    )
    without_semantic = [entry["cko_id"] for entry in all_ckos if not str(entry.get("semantic_id") or "")]
    # An identity must not rest on anything the invariants permit to evolve. Proved by
    # re-deriving it with every excluded input perturbed and requiring it to be unchanged.
    excluded = [str(name) for name in document["semantic_identity"]["excluded_inputs"]]
    mutable_leak: list[str] = []
    for entry in ckos:
        if entry["kind"] == registry_kind:
            continue
        perturbed = dict(entry)
        perturbed["provenance"] = {name: name + "-perturbed" for name in entry["provenance"]}
        recomputed = semantic_identity(document, entry["kind"], entry["record_id"])
        if recomputed != str(entry.get("semantic_id") or ""):
            mutable_leak.append(entry["cko_id"])
    for name in excluded:
        if name in document["semantic_identity"]["inputs"]:
            mutable_leak.append(f"declared input is a mutable characteristic: {name}")
    unidentified_targets = [e["cko_id"] for e in relationships if not e["target_identified"]]
    # The DISTINCT artifacts the Universal Registry does not admit, as opposed to the
    # EDGES that reach them. The two are different constitutional quantities and only
    # this one measures the disclosed condition itself.
    #
    # A relationship count conflates "the graph reaches a new corner of the corpus the
    # registry cannot name" with "more edges point at a corner already disclosed". The
    # second grows with legitimate knowledge-base growth for no constitutional reason —
    # 119 capability facts each citing the one generated catalogue they were all derived
    # from move the relationship count by 119 and the disclosed condition by ONE. Only the
    # target measure detects a genuinely new unadmitted corner at +1, and it detects it
    # even when the relationship ratchet still has slack.
    unadmitted_targets = sorted(
        {str(e["attributes"]["target"]) for e in relationships if not e["target_identified"]}
    )

    # ---- self-evolution path: every step owned OUTSIDE this programme
    evolution_steps: list[dict] = []
    for entry in document["self_evolution_path"]:
        owner = str(entry["owner"])
        text = read_text(owner)
        anchor = str(entry.get("anchor") or "")
        evolution_steps.append(
            {
                "id": str(entry["id"]),
                "step": str(entry["step"]),
                "owner": owner,
                "anchor": anchor,
                "located": text is not None,
                "anchor_present": (not anchor) or (bool(text) and anchor in text),
                "external": not owner.startswith(OWN_PREFIX),
            }
        )

    # ---- graph type composition
    graphs: list[dict] = []
    for gtype in document["graph_types"]["types"]:
        node_kinds = [str(k) for k in gtype["node_kinds"]]
        relations = [str(r) for r in gtype["edge_relations"]]
        # Composed from DISCOVERED objects — entity CKOs and relationship CKOs alike —
        # never from the order in which the engine happened to read them.
        nodes = [e for e in all_ckos if e["kind"] in node_kinds]
        selected = [e for e in edges if e["relation"] in relations and e["source"] in {n["cko_id"] for n in nodes}]
        graphs.append(
            {
                "id": str(gtype["id"]),
                "graph": str(gtype["graph"]),
                "node_kinds": node_kinds,
                "edge_relations": relations,
                "nodes": len(nodes),
                "edges": len(selected),
                "kinds_known": all(k in known_kinds for k in node_kinds),
                "relations_known": all(r in known_relations for r in relations),
            }
        )

    # ---- lifecycle authority crosswalk
    authorities: list[dict] = []
    for entry in document["lifecycle_authorities"]:
        owner = str(entry["owner"])
        text = read_text(owner)
        anchor = str(entry["anchor"])
        authorities.append(
            {
                "id": str(entry["id"]),
                "name": str(entry["name"]),
                "owner": owner,
                "anchor": anchor,
                "role": str(entry["role"]),
                "located": text is not None,
                "anchor_present": bool(text) and anchor in text,
                "merge_prohibited": bool(entry.get("merge_prohibited")),
                "claimed_here": owner.startswith(OWN_PREFIX),
            }
        )

    # ---- admission paths (EVIDENCE probes) and expansion axes
    paths: list[dict] = []
    for entry in document["admission_paths"]:
        owner = str(entry["owner"])
        symbol = str(entry["symbol"])
        paths.append(
            {
                "id": str(entry["id"]),
                "owner": owner,
                "symbol": symbol,
                "kind": str(entry["kind"]),
                "discovery_class": str(entry["discovery_class"]),
                "located": exists(owner),
                "symbol_located": symbol_present(owner, symbol),
            }
        )
    path_state = {p["id"]: (p["located"] and p["symbol_located"]) for p in paths}
    axes: list[dict] = []
    for entry in document["expansion_axes"]:
        target = str(entry["admission_path"])
        axes.append(
            {
                "id": str(entry["id"]),
                "axis": str(entry["axis"]),
                "clause": str(entry["clause"]),
                "admission_path": target,
                "blocking": bool(entry.get("blocking")),
                "bound": bool(path_state.get(target)),
            }
        )

    # ---- located terminal-state claims
    terminal_tokens = [str(t).lower() for t in document["unboundedness"]["terminal_tokens"]]
    negations = [str(n).lower() for n in document["unboundedness"]["negation_markers"]]
    surfaces = [str(a["owner"]) for a in document["lifecycle_authorities"]]
    surfaces.append(str(document["unboundedness"]["owner"]))
    terminal_hits: list[str] = []
    for relative in sorted(set(surfaces)):
        for line in (read_text(relative) or "").splitlines():
            low = line.lower()
            for token in terminal_tokens:
                if token in low and not any(marker in low for marker in negations):
                    terminal_hits.append(f"{relative}::{token}")

    # ---- architectural bound tokens: the engine and every discovered provider
    tokens = [str(t) for t in document["hygiene"]["limit_tokens"]]
    bound_hits: list[str] = []
    scanned = [Path(__file__).relative_to(REPO).as_posix()] + [p["owner"] for p in discovered_providers]
    for relative in scanned:
        for line in (read_text(relative) or "").splitlines():
            low = line.lower()
            for token in tokens:
                if token.lower() in low and not any(marker in low for marker in negations):
                    bound_hits.append(f"{relative}::{token}")

    # ---- capabilities
    capabilities: list[dict] = []
    for entry in document["capabilities"]:
        owner = str(entry["owner"])
        artifacts = [str(a) for a in entry["artifacts"]]
        capabilities.append(
            {
                "id": str(entry["id"]),
                "group": str(entry["group"]),
                "capability": str(entry["capability"]),
                "owner": owner,
                "artifacts": artifacts,
                "status": str(entry["status"]),
                "action": str(entry["action"]),
                "evidence": str(entry.get("evidence", "")),
                "owner_located": exists(owner),
                "artifacts_unresolved": [a for a in artifacts if not exists(a)],
            }
        )

    # ---- records and write scope
    records: list[dict] = []
    for entry in document["record_set"]["records"]:
        owner = str(entry["owner"])
        text = read_text(owner)
        anchor = str(entry["anchor"])
        records.append(
            {
                "id": str(entry["id"]),
                "owner": owner,
                "anchor": anchor,
                "law": str(entry["law"]),
                "located": text is not None,
                "anchor_present": (not anchor) or (bool(text) and anchor in text),
            }
        )
    write_set = {OWN_PREFIX + name for name in PAGES}
    write_set.add(MODEL.relative_to(REPO).as_posix())
    record_set = {row["owner"] for row in records}
    forbidden = [str(p) for p in document["programme"]["forbidden_write_prefixes"]]
    immutability = {
        "write_set": sorted(write_set),
        "record_set": sorted(record_set),
        "intersection": sorted(write_set & record_set),
        "outside_home": sorted(p for p in write_set if not p.startswith(OWN_PREFIX)),
        "forbidden_trespass": sorted(p for p in write_set for prefix in forbidden if p.startswith(prefix)),
    }
    immutability["disjoint"] = not (
        immutability["intersection"] or immutability["outside_home"] or immutability["forbidden_trespass"]
    )

    # ---- deterministic execution of the declared canonical goals
    # ---- constitutional law: exactly one CKO per governed entity, and derived
    # artifacts are never Repository Truth. Every register this programme emits is a
    # PROJECTION of the discovered objects; a provider pointing at one would make a
    # derived view into a source, which is the circularity the law forbids.
    collisions = identity_collisions(ckos)
    derived_set = {OWN_PREFIX + name for name in PAGES}
    derived_set.add(MODEL.relative_to(REPO).as_posix())
    derived_as_truth = sorted(
        p["owner"] for p in providers if p["owner"] in derived_set
    )
    declared_own = sorted(
        p["owner"] for p in providers if p["owner"].startswith(OWN_PREFIX)
    )

    runs: list[dict] = []
    for entry in document["execution"]["canonical_goals"]:
        goal = str(entry["goal"])
        first = execute(goal, order, by_cko, obligation_state, property_state, graph_digest)
        second = execute(goal, order, by_cko, obligation_state, property_state, graph_digest)
        runs.append(
            {
                "id": str(entry["id"]),
                "goal": goal,
                "note": str(entry.get("note", "")),
                "run_id": first["run_id"],
                "stages_traversed": first["stages_traversed"],
                "stages_admitted": sum(1 for step in first["steps"] if step["admitted"]),
                "deterministic": canonical(first) == canonical(second),
                "steps": first["steps"],
            }
        )

    obligation_failures = sum(        1
        for cko_id, state in obligation_state.items()
        for name, value in state.items()
        if not value and applicability_state[cko_id][name] != inapplicable_class
    )
    obligation_inapplicable = sum(
        1
        for applies in applicability_state.values()
        for value in applies.values()
        if value == inapplicable_class
    )
    obligation_conditional_active = sum(
        1
        for applies in applicability_state.values()
        for value in applies.values()
        if value == conditional_class
    )
    property_failures = sum(
        1 for state in property_state.values() for value in state.values() if not value
    )

    counters = {
        "stage_nodes_discovered": len(stages),
        "stage_nodes_unowned": sum(1 for e in stages if not exists(str(e["attributes"].get("owner", "") or ""))),
        "stage_nodes_unauthorized": sum(
            1 for e in stages if not exists(str(e["attributes"].get("authority_owner", "") or ""))
        ),
        "graph_cycles": len(cycles),
        "dangling_relations": sum(1 for e in edges if e["target_class"] == "dangling"),
        "capabilities_created": sum(1 for c in capabilities if c["action"] == ACTION_CREATE),
        "capabilities_unowned": sum(1 for c in capabilities if not c["owner_located"]),
        "capability_artifacts_unresolved": sum(len(c["artifacts_unresolved"]) for c in capabilities),
        "evidence_originated_ckos": sum(
            1 for e in ckos if e["provenance"]["discovery_class"] != "constitutional-metadata"
        ),
        "providers_without_reader": sum(
            1 for p in providers if reader_for(document, p["serialization"]) is None
        ),
        "providers_unlocated": sum(1 for p in providers if not p["located"]),
        "adapters_unresolved": sum(1 for a in adapter_reports if not a["resolved"]),
        "expansion_axes_unbound": sum(1 for a in axes if a["blocking"] and not a["bound"]),
        "admission_paths_unresolved": sum(1 for p in paths if not (p["located"] and p["symbol_located"])),
        "limit_tokens_present": len(bound_hits),
        "terminal_state_claims": len(terminal_hits),
        "closed_enumerations_declared": sum(
            1
            for flag in (
                document["cko_model"].get("closed_enumeration"),
                document["graph_types"].get("closed_enumeration"),
                *[p["closed_enumeration"] for p in discovered_providers],
            )
            if flag is not False
        ),
        "reentry_declarations_absent": 0
        if any(
            edge["target_class"] == "cko" and _reentry_like(edge["relation"], document)
            for edge in edges
        )
        else 1,
        "serialization_readers_registered": len(
            {
                str(entry["reader"])
                for entry in document["serializations"]
                if entry.get("registered") and READERS.get(str(entry["reader"]))
            }
        ),
        "serializations_exercised": len({p["serialization"] for p in providers if p["located"]}),
        "capability_nodes_discovered": sum(g["nodes"] for g in graphs if g["id"] == _capability_graph_id(document)),
        "cko_kind_registry_closed": 0 if document["cko_model"].get("open") is True else 1,
        "graph_type_registry_closed": 0 if document["graph_types"].get("open") is True else 1,
        "graph_types_unresolved": sum(1 for g in graphs if not (g["kinds_known"] and g["relations_known"])),
        "graph_types_empty": sum(1 for g in graphs if not g["nodes"]),
        "lifecycle_authorities_unresolved": sum(
            1 for a in authorities if not (a["located"] and a["anchor_present"])
        ),
        "parallel_authority_claims": sum(1 for a in authorities if a["claimed_here"]),
        "record_write_intersections": len(immutability["intersection"]),
        "writes_outside_home": len(immutability["outside_home"]) + len(immutability["forbidden_trespass"]),
        "authority_claims": 0 if str(document["programme"]["authority"]).startswith("NONE") else 1,
        "runs_nondeterministic": sum(1 for r in runs if not r["deterministic"]),
        "providers_not_open": sum(
            1
            for p in discovered_providers
            if not (p["open"] is True and p["closed_enumeration"] is False and p["admission"])
        ),
        "ckos_without_provenance": sum(1 for e in ckos if not e["provenance"]["provider"]),
        "ckos_of_unknown_kind": sum(1 for e in ckos if e["kind"] not in known_kinds),
        "relations_of_unknown_type": sum(1 for e in edges if e["relation"] not in known_relations),
        "stage_obligation_failures": obligation_failures,
        "stage_obligations_not_applicable": obligation_inapplicable,
        "stage_obligations_conditional_active": obligation_conditional_active,
        "stage_property_failures": property_failures,
        "cko_identity_collisions": len(collisions),
        "cko_reference_ambiguities": sum(1 for e in edges if e["ambiguous"]),
        "derived_artifacts_used_as_truth": len(derived_as_truth),
        "relationship_ckos_discovered": len(relationships),
        "ckos_without_semantic_identity": len(without_semantic),
        "semantic_identity_collisions": len(semantic_clashes),
        "self_evolution_steps_unbound": sum(
            1 for s in evolution_steps if not (s["located"] and s["anchor_present"] and s["external"])
        ),
        "goals_executed": len(runs),
        "expansion_axes_bound": sum(1 for a in axes if a["bound"]),
        "semantic_identity_mutable_inputs": len(mutable_leak),
        "relationships_without_target_identity": len(unidentified_targets),
        "unadmitted_target_artifacts": len(unadmitted_targets),
        "knowledge_extractions_unmeasured": 0,
        "elevations_unevidenced": 0,
        "readiness_owners_unresolved": 0,
        "ckos_discovered": len(all_ckos),
        "relations_discovered": len(edges),
    }

    # Declared population counters: the engine names no adapter, it loops over the
    # declaration and counts the objects each named adapter emitted.
    for entry in document["derived_counters"]:
        kind = _kind_of(document, str(entry["adapter"]))
        counters[str(entry["id"])] = sum(1 for e in ckos if e["kind"] == kind)

    unbounded: list[dict] = []
    for dimension in document["unboundedness"]["dimensions"]:
        name = str(dimension["measure"])
        value = counters.get(name)
        if value is None:
            raise FailClosed(f"an unbounded dimension names a measurement that does not exist: {name}")
        unbounded.append(
            {
                "id": str(dimension["id"]),
                "requirement": str(dimension["requirement"]),
                "clause": str(dimension["clause"]),
                "measure": name,
                "comparator": str(dimension["comparator"]),
                "expect": int(dimension["expect"]),
                "value": int(value),
                "satisfied": compare(int(value), str(dimension["comparator"]), int(dimension["expect"])),
                "blocking": bool(dimension["blocking"]),
            }
        )
    counters["unboundedness_violations"] = sum(1 for d in unbounded if d["blocking"] and not d["satisfied"])

    # ---- extracted engineering knowledge: measured from the run, never asserted about it
    extraction = document["knowledge_extraction"]
    extractions: list[dict] = []
    for rule in extraction["rules"]:
        name = str(rule["measure"])
        extractions.append(
            {
                "id": str(rule["id"]),
                "knowledge": str(rule["knowledge"]),
                "measure": name,
                "value": counters.get(name),
                "measured": name in counters,
                "reusable_as": str(rule["reusable_as"]),
                "registration_owner": str(extraction["registration_owner"]),
                "registration_owner_located": exists(str(extraction["registration_owner"])),
            }
        )
    counters["knowledge_extractions_unmeasured"] = sum(
        1 for e in extractions if not (e["measured"] and e["registration_owner_located"])
    )

    # ---- capability elevation: each increase carries five facets, each located
    elevations: list[dict] = []
    facets = ("evidence_owner", "lineage_owner", "replay_owner", "certification_owner", "authority_owner")
    for entry in document["elevation_measures"]:
        name = str(entry["measure"])
        missing = [facet for facet in facets if not exists(str(entry[facet]))]
        elevations.append(
            {
                "id": str(entry["id"]),
                "increase": str(entry["increase"]),
                "statement": str(entry["statement"]),
                "measure": name,
                "value": counters.get(name),
                "measured": name in counters,
                "facets": {facet: str(entry[facet]) for facet in facets},
                "facets_unresolved": missing,
                "evidenced": not missing and name in counters,
            }
        )
    counters["elevations_unevidenced"] = sum(1 for e in elevations if not e["evidenced"])

    # ---- Ω-E05 readiness: every dimension measured against a located owner
    readiness: list[dict] = []
    for entry in document["readiness_dimensions"]:
        name = str(entry["measure"])
        owner = str(entry["owner"])
        value = counters.get(name)
        located = exists(owner)
        met = value is not None and compare(int(value), str(entry["comparator"]), int(entry["expect"]))
        readiness.append(
            {
                "id": str(entry["id"]),
                "dimension": str(entry["dimension"]),
                "owner": owner,
                "owner_located": located,
                "measure": name,
                "comparator": str(entry["comparator"]),
                "expect": int(entry["expect"]),
                "value": value,
                "ready": bool(located and met),
            }
        )
    counters["readiness_owners_unresolved"] = sum(1 for r in readiness if not r["owner_located"])
    counters["readiness_dimensions_unmet"] = sum(1 for r in readiness if not r["ready"])

    slack: list[dict] = []
    for entry in document["validations"]:
        if str(entry.get("comparator")) != "<=":
            continue
        name = str(entry.get("measure"))
        value = counters.get(name)
        if value is not None and int(value) < int(entry["expect"]):
            slack.append({"id": str(entry["id"]), "measure": name, "value": int(value), "bound": int(entry["expect"])})
    counters["bounds_slack"] = len(slack)

    validations: list[dict] = []
    for entry in document["validations"]:
        name = str(entry["measure"])
        value = counters.get(name)
        if value is None:
            raise FailClosed(f"a declared dimension has no measurement: {entry['id']} ({name})")
        validations.append(
            {
                "id": str(entry["id"]),
                "dimension": str(entry["dimension"]),
                "measure": name,
                "comparator": str(entry["comparator"]),
                "expect": int(entry["expect"]),
                "value": int(value),
                "satisfied": compare(int(value), str(entry["comparator"]), int(entry["expect"])),
                "blocking": bool(entry["blocking"]),
                "bound_finding": entry.get("bound_finding"),
            }
        )

    blocking_failures = [v["id"] for v in validations if v["blocking"] and not v["satisfied"]]
    gate = "OPEN" if not blocking_failures else "CLOSED"
    determination = document["determination"]["bound"] if gate == "OPEN" else document["determination"]["open"]

    model = {
        "programme": document["programme"],
        "cko_model": {
            "open": document["cko_model"].get("open"),
            "kinds": sorted(known_kinds),
            "relation_types": sorted(known_relations),
            "admission": str(document["cko_model"].get("admission", "")),
        },
        "serializations": document["serializations"],
        "providers": providers,
        "adapters": adapter_reports,
        "stage_kind": stage_kind,
        "dependency_relation": dependency_relation,
        "stages": [
            {
                "cko_id": e["cko_id"],
                "record_id": e["record_id"],
                "stage": e["name"],
                "ordinal": _as_int(e["attributes"].get("ordinal")),
                "group": str(e["attributes"].get("group", "") or ""),
                "owner": str(e["attributes"].get("owner", "") or ""),
                "authority": str(e["attributes"].get("authority", "") or ""),
                "authority_owner": str(e["attributes"].get("authority_owner", "") or ""),
                "provenance": e["provenance"],
                "obligations": obligation_state[e["cko_id"]],
                "applicability": applicability_state[e["cko_id"]],
                "properties": property_state[e["cko_id"]],
                "relations": [
                    {"relation": edge["relation"], "target": edge["target"], "target_class": edge["target_class"]}
                    for edge in edges_by_source.get(e["cko_id"], [])
                ],
            }
            for e in stages
        ],
        "order": order,
        "cycles": cycles,
        "graphs": graphs,
        "graph_digest": graph_digest,
        "authorities": authorities,
        "admission_paths": paths,
        "expansion_axes": axes,
        "terminal_hits": sorted(set(terminal_hits)),
        "bound_hits": sorted(set(bound_hits)),
        "capabilities": capabilities,
        "records": records,
        "immutability": immutability,
        "identity_collisions": collisions,
        "relationships": relationships,
        "semantic_identity": {
            "inputs": document["semantic_identity"]["inputs"],
            "excluded_inputs": document["semantic_identity"]["excluded_inputs"],
            "collisions": semantic_clashes,
            "without_identity": without_semantic,
            "mutable_inputs": mutable_leak,
            "relationships_without_target_identity": len(unidentified_targets),
            "unadmitted_target_artifacts": unadmitted_targets,
        },
        "extractions": extractions,
        "elevations": elevations,
        "self_evolution": evolution_steps,
        "readiness": readiness,
        "omega_e05_authorized": bool(gate == "OPEN" and all(r["ready"] for r in readiness)),
        "truth_class": {
            "declared_sources_in_own_home": declared_own,
            "derived_artifacts": sorted(derived_set),
            "derived_used_as_truth": derived_as_truth,
        },
        "runs": runs,
        "obligation_rules": document["obligation_rules"],
        "applicability_classes": document["applicability_classes"],
        "applicability_tokens": {
            "required": required_class,
            "conditional": conditional_class,
            "not_applicable": inapplicable_class,
        },
        "property_rules": document["property_rules"],
        "unboundedness": unbounded,
        "counters": counters,
        "bounds_slack": slack,
        "validations": validations,
        "exit_criteria": document["exit_criteria"],
        "findings": document["findings"],
        "blocking_failures": blocking_failures,
        "gate": gate,
        "determination": determination,
    }
    model["seal_sha256"] = digest(canonical({k: v for k, v in model.items() if k != "seal_sha256"}))
    return model


def _reentry_like(relation: str, document: dict) -> bool:
    """Is this declared relation the non-terminality relation?

    Decided by the relation's own declared note rather than by its name, so renaming
    it in the registry does not silently disable the non-terminality measurement.
    """
    for entry in document["cko_model"]["relation_types"]:
        if str(entry["relation"]) != relation:
            continue
        return "non-terminal" in str(entry.get("note", "")).lower()
    return False


def _capability_graph_id(document: dict) -> str:
    """The graph type whose nodes are the discovered capability plane."""
    for gtype in document["graph_types"]["types"]:
        if "capability" in str(gtype["graph"]).lower():
            return str(gtype["id"])
    return ""


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
                    ["GRAPH DIGEST (sha256)", model["graph_digest"]],
                    ["SEAL (sha256)", model["seal_sha256"]],
                    ["GENERATED BY", "ucl_engine.py — regenerated, never hand-authored"],
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
    obligations = [str(r["id"]) for r in model["obligation_rules"]]
    properties = [str(r["id"]) for r in model["property_rules"]]

    # ---- 00 dashboard
    body = [front_matter(model, "Universal Constitutional Lifecycle Dashboard")]
    body.append("## Measured position\n")
    body.append(
        table(
            ["Reading", "Value"],
            [
                ["Canonical Knowledge Objects discovered", str(counters["ckos_discovered"])],
                ["Relations discovered", str(counters["relations_discovered"])],
                ["Constitutional stages discovered", str(counters["stage_nodes_discovered"])],
                ["Stage plane (CKO kind)", code(model["stage_kind"])],
                ["Dependency relation", code(model["dependency_relation"])],
                ["Graph cycles", str(counters["graph_cycles"])],
                ["Dangling relations", str(counters["dangling_relations"])],
                ["Metadata providers", str(len(model["providers"]))],
                ["Metadata adapters resolved", f"{len(model['adapters']) - counters['adapters_unresolved']}/{len(model['adapters'])}"],
                ["Serialization readers registered", str(counters["serialization_readers_registered"])],
                ["Serializations exercised by a located provider", str(counters["serializations_exercised"])],
                ["Graph types composed", f"{len(model['graphs']) - counters['graph_types_empty']}/{len(model['graphs'])}"],
                ["Expansion axes bound", f"{len(model['expansion_axes']) - counters['expansion_axes_unbound']}/{len(model['expansion_axes'])}"],
                ["Obligation bindings held", f"{len(model['stages']) * len(obligations) - counters['stage_obligation_failures']}/{len(model['stages']) * len(obligations)}"],
                ["Property conformances held", f"{len(model['stages']) * len(properties) - counters['stage_property_failures']}/{len(model['stages']) * len(properties)}"],
                ["Canonical goals executed deterministically", f"{len(model['runs']) - counters['runs_nondeterministic']}/{len(model['runs'])}"],
                ["Objects originated from implementation evidence", str(counters["evidence_originated_ckos"])],
                ["Capabilities dispositioned CREATE", str(counters["capabilities_created"])],
                ["Record immutability", yes(model["immutability"]["disjoint"])],
                ["Blocking dimensions satisfied", f"{sum(1 for v in model['validations'] if v['satisfied'])}/{len(model['validations'])}"],
            ],
        )
    )
    body.append("\n## What this programme does NOT do\n")
    body.append(
        "\n".join(
            [
                "- It legislates no lifecycle and creates no stage.",
                "- It enumerates no stage, no capability, no owner, no graph type and no relation type.",
                "- It opens no registry, mints no identifier and declares no namespace.",
                "- It re-invokes no stage engine, so it never observes a run of itself.",
                "- It certifies nothing and resolves nothing authoritatively.",
                "",
                "Where this measurement and a located instrument differ, **the located instrument governs**.",
            ]
        )
    )
    body.append("\n## Registers\n")
    body.append("\n".join(f"- [{name}]({name})" for name in PAGES if name != PAGES[0]))
    pages[PAGES[0]] = "\n".join(body) + "\n"

    # ---- 01 stage graph
    body = [front_matter(model, "Constitutional Stage Graph Register")]
    body.append(
        "The constitutional stage graph, DISCOVERED from declared constitutional metadata and\n"
        "normalized into Canonical Knowledge Objects. No stage is named in the engine or in the\n"
        "declaration: each row below exists because a located metadata provider declares it.\n"
        "Order is derived topologically from the discovered dependency relation, never from a\n"
        "list. A stage admitted between two others takes an ordinal in the gap and no existing\n"
        "ordinal moves.\n"
    )
    body.append(
        table(
            ["#", "Stage", "Group", "Canonical owner", "Constitutional authority owner", "Owner resolves", "Authority resolves"],
            [
                [
                    str(position),
                    stage["stage"],
                    stage["group"],
                    code(stage["owner"]),
                    code(stage["authority_owner"]),
                    yes(bool(stage["owner"]) and exists(stage["owner"])),
                    yes(bool(stage["authority_owner"]) and exists(stage["authority_owner"])),
                ]
                for position, stage in enumerate(_ordered(model), start=1)
            ],
        )
    )
    body.append("\n## Declared constitutional authority per stage\n")
    body.append(
        table(
            ["Stage", "Authority"],
            [[stage["stage"], stage["authority"]] for stage in _ordered(model)],
        )
    )
    body.append("\n## Derived traversal order\n")
    body.append(f"Cycles detected: **{len(model['cycles'])}**. A cycle would make the lifecycle unorderable.\n")
    body.append("\n".join(f"{position}. {model_stage['stage']}" for position, model_stage in enumerate(_ordered(model), start=1)))
    pages[PAGES[1]] = "\n".join(body) + "\n"

    # ---- 02 obligation matrix
    body = [front_matter(model, "Stage Obligation Binding Matrix")]
    tokens = model["applicability_tokens"]
    body.append(
        "Every obligation is a declared RULE evaluated against every discovered stage. An obligation\n"
        "is NOT universally applicable: applicability is determined FIRST, and Repository Truth decides\n"
        "the conditional cases. Only REQUIRED obligations, and CONDITIONAL obligations whose governing\n"
        "condition is satisfied, participate in gate failure. A NOT_APPLICABLE obligation is reported\n"
        "as such and never counted as unbound — counting it would manufacture a deficiency the\n"
        "repository does not have.\n"
    )
    body.append(
        table(
            ["Class", "Participates in gate failure", "Note"],
            [
                [str(entry["id"]), str(entry["participates"]), str(entry.get("note", ""))]
                for entry in model["applicability_classes"]
            ],
        )
    )
    body.append("\n## Obligations\n")
    body.append(
        table(
            ["Obligation", "Applicability", "Mechanic", "In scope", "Bound (in scope)", "Not applicable", "Statement"],
            [
                [
                    str(rule["id"]),
                    str(rule.get("applicability") or tokens["required"]),
                    code(rule.get("kind")),
                    str(_scope_count(model, str(rule["id"]))),
                    f"{_bound_count(model, str(rule['id']))}/{_scope_count(model, str(rule['id']))}",
                    str(_na_count(model, str(rule["id"]))),
                    str(rule.get("note", "")),
                ]
                for rule in model["obligation_rules"]
            ],
        )
    )
    body.append("\n## Per-stage binding\n")
    body.append(
        f"`PASS` bound · `FAIL` in scope and unbound · `n/a` not applicable to this stage.\n"
    )
    body.append(
        table(
            ["Stage", *[o.replace("OBL-", "") for o in obligations], "Bound / in scope"],
            [
                [
                    stage["stage"],
                    *[_cell(stage, name, tokens) for name in obligations],
                    f"{sum(1 for n in obligations if stage['obligations'].get(n) and stage['applicability'].get(n) != tokens['not_applicable'])}"
                    f"/{sum(1 for n in obligations if stage['applicability'].get(n) != tokens['not_applicable'])}",
                ]
                for stage in _ordered(model)
            ],
        )
    )
    pages[PAGES[2]] = "\n".join(body) + "\n"

    # ---- 03 property conformance
    body = [front_matter(model, "Stage Property Conformance Register")]
    body.append(
        "The properties every stage must exhibit, each DERIVED from measured facts rather than\n"
        "asserted. A property that does not hold is a statement about the repository, so it is\n"
        "measured, bounded and referred rather than manufactured.\n"
    )
    body.append(
        table(
            ["Property", "Rule", "Mechanic", "Held"],
            [
                [
                    str(rule.get("property")),
                    str(rule["id"]),
                    code(rule.get("kind")),
                    f"{sum(1 for s in model['stages'] if s['properties'].get(str(rule['id'])))}/{len(model['stages'])}",
                ]
                for rule in model["property_rules"]
            ],
        )
    )
    body.append("\n## Per-stage conformance\n")
    body.append(
        table(
            ["Stage", *[p.replace("PROP-", "") for p in properties], "Held"],
            [
                [
                    stage["stage"],
                    *[tick(bool(stage["properties"].get(name))) for name in properties],
                    f"{sum(1 for v in stage['properties'].values() if v)}/{len(properties)}",
                ]
                for stage in _ordered(model)
            ],
        )
    )
    pages[PAGES[3]] = "\n".join(body) + "\n"

    # ---- 04 authority crosswalk
    body = [front_matter(model, "Lifecycle Authority Crosswalk Register")]
    body.append(
        "Several distinct owned things share the word 'lifecycle'. They are CROSSWALKED here and\n"
        "never merged: a merge would amend every owner at once, which is expansion by\n"
        "reinterpretation. This programme claims none of these roles.\n"
    )
    body.append(
        table(
            ["Authority", "Owner", "Anchor", "Resolves", "Anchor present", "Claimed here", "Role"],
            [
                [
                    entry["id"],
                    code(entry["owner"]),
                    code(entry["anchor"]),
                    yes(entry["located"]),
                    yes(entry["anchor_present"]),
                    yes(entry["claimed_here"]),
                    entry["role"],
                ]
                for entry in model["authorities"]
            ],
        )
    )
    body.append("\n## Located terminal-state claims\n")
    body.append(
        f"Terminal-state claims found across the located lifecycle instruments: **{len(model['terminal_hits'])}**.\n"
        "A phrase asserting closure inside a prohibition of closure is the architecture defending\n"
        "itself, so a hit whose line carries a negation marker is not counted as a claim.\n"
    )
    if model["terminal_hits"]:
        body.append("\n".join(f"- {code(hit)}" for hit in model["terminal_hits"]))
    pages[PAGES[4]] = "\n".join(body) + "\n"

    # ---- 05 CKO + graphs
    body = [front_matter(model, "Canonical Knowledge Object and Graph Register")]
    body.append(
        "Every constitutionally governed entity is normalized to a Canonical Knowledge Object: a\n"
        "kind, an identity, an owner, a provenance and typed relations. Repository Truth is\n"
        "expressed as relationships among those objects, never as an implementation structure.\n"
        "The kind registry and the relation registry are OPEN — a previously unknown entity is\n"
        "admitted by appending a kind, and a previously unknown relationship by appending a type.\n"
    )
    body.append("\n## Canonical Knowledge Object kinds discovered\n")
    counts: dict[str, int] = {}
    for stage in model["stages"]:
        counts[stage["provenance"]["adapter"]] = counts.get(stage["provenance"]["adapter"], 0) + 1
    body.append(
        table(
            ["Kind", "Objects", "Adapter(s)"],
            [
                [
                    code(kind),
                    str(sum(a["objects"] for a in model["adapters"] if a["kind"] == kind)),
                    " · ".join(code(a["id"]) for a in model["adapters"] if a["kind"] == kind),
                ]
                for kind in model["cko_model"]["kinds"]
            ],
        )
    )
    body.append("\n## Relation types declared\n")
    body.append("\n".join(f"- {code(name)}" for name in model["cko_model"]["relation_types"]))
    body.append("\n\n## Graph types composed\n")
    body.append(
        "Graph types are themselves declared and OPEN: the architecture assumes no permanently\n"
        "fixed set. Each is composed by selecting object kinds as nodes and relation types as edges.\n"
    )
    body.append(
        table(
            ["Graph", "Node kinds", "Edge relations", "Nodes", "Edges", "Kinds known", "Relations known"],
            [
                [
                    entry["graph"],
                    " · ".join(code(k) for k in entry["node_kinds"]),
                    " · ".join(code(r) for r in entry["edge_relations"]) or "—",
                    str(entry["nodes"]),
                    str(entry["edges"]),
                    yes(entry["kinds_known"]),
                    yes(entry["relations_known"]),
                ]
                for entry in model["graphs"]
            ],
        )
    )
    body.append(f"\n**Graph digest (sha256):** `{model['graph_digest']}`\n")
    pages[PAGES[5]] = "\n".join(body) + "\n"

    # ---- 06 providers + adapters
    body = [front_matter(model, "Metadata Provider and Adapter Register")]
    body.append(
        "Discovery targets constitutional METADATA, not a file format. A provider says WHERE\n"
        "metadata lives and in which serialization; an adapter says HOW those records normalize\n"
        "into objects. Replacing a serialization or a storage technology means registering a\n"
        "provider and an adapter — it changes no object kind, no relation, no graph type, no\n"
        "obligation and no stage.\n"
    )
    body.append("\n## Serialization registry (open)\n")
    body.append(
        table(
            ["Serialization", "Reader", "Registered", "Reader available", "Note"],
            [
                [
                    entry["name"],
                    code(entry["reader"]),
                    yes(bool(entry.get("registered"))),
                    yes(bool(READERS.get(str(entry["reader"])))),
                    str(entry.get("note", "")),
                ]
                for entry in model["serializations"]
            ],
        )
    )
    body.append(
        "\nAn unregistered serialization is admissible and REPORTED, never fatal: a registry that\n"
        "must be implemented before it can be extended is not open.\n"
    )
    body.append("\n## Metadata providers\n")
    body.append(
        table(
            ["Provider", "Owner", "Serialization", "Discovery class", "Discovered by pattern", "Resolves", "Open"],
            [
                [
                    entry["id"],
                    code(entry["owner"]),
                    code(entry["serialization"]),
                    entry["discovery_class"],
                    yes(entry["discovered"]),
                    yes(entry["located"]),
                    "—" if entry["open"] is None else yes(bool(entry["open"])),
                ]
                for entry in model["providers"]
            ],
        )
    )
    body.append("\n## Metadata adapters\n")
    body.append(
        table(
            ["Adapter", "Provider", "Pointer", "Object kind", "Objects", "Resolves"],
            [
                [
                    entry["id"],
                    code(entry["provider"]),
                    code(entry["pointer"]) or "*(root)*",
                    code(entry["kind"]),
                    str(entry["objects"]),
                    yes(entry["resolved"]),
                ]
                for entry in model["adapters"]
            ],
        )
    )
    pages[PAGES[6]] = "\n".join(body) + "\n"

    # ---- 07 expansion axes
    body = [front_matter(model, "Open-World Expansion Axis Register")]
    body.append(
        "Every axis for which no maximum may exist, each bound to the located instrument that\n"
        "authorizes unboundedness AND to an admission path that must resolve. An axis whose\n"
        "registrar does not resolve is an axis whose openness was asserted and never probed.\n"
    )
    body.append(
        table(
            ["Axis", "Clause", "Admission path", "Registrar", "Bound"],
            [
                [
                    entry["axis"],
                    entry["clause"],
                    code(entry["admission_path"]),
                    code(_path_symbol(model, entry["admission_path"])),
                    tick(entry["bound"]),
                ]
                for entry in model["expansion_axes"]
            ],
        )
    )
    body.append("\n## Admission paths probed\n")
    body.append(
        "These are EVIDENCE probes. They confirm a located extension path exists; they originate\n"
        "no object and no relation.\n"
    )
    body.append(
        table(
            ["Path", "Owner", "Symbol", "Discovery class", "Owner resolves", "Symbol present"],
            [
                [
                    entry["id"],
                    code(entry["owner"]),
                    code(entry["symbol"]),
                    entry["discovery_class"],
                    yes(entry["located"]),
                    yes(entry["symbol_located"]),
                ]
                for entry in model["admission_paths"]
            ],
        )
    )
    body.append("\n## Unbounded dimensions\n")
    body.append(
        table(
            ["Dimension", "Requirement", "Clause", "Measure", "Value", "Expect", "Satisfied"],
            [
                [
                    entry["id"],
                    entry["requirement"],
                    entry["clause"],
                    code(entry["measure"]),
                    str(entry["value"]),
                    f"{entry['comparator']} {entry['expect']}",
                    tick(entry["satisfied"]),
                ]
                for entry in model["unboundedness"]
            ],
        )
    )
    body.append(f"\nArchitectural bound tokens found: **{len(model['bound_hits'])}**.\n")
    pages[PAGES[7]] = "\n".join(body) + "\n"

    # ---- 08 execution + replay
    body = [front_matter(model, "Deterministic Execution and Replay Register")]
    body.append(
        "The lifecycle EXECUTES the discovered graph: a deterministic constitutional traversal in\n"
        "topological order that resolves each stage's relations and obligations and emits a run\n"
        "record. It does NOT re-invoke the stages' own engines — those are already executed by the\n"
        "fixed-point pipeline, and invoking them here would create the self-observation topology\n"
        "that forbids the repository from converging.\n\n"
        "A run is a pure function of the goal text and the discovered graph, so the same goal\n"
        "against the same graph yields the same run identity, byte for byte. Arbitrary goals are\n"
        "executable through the engine's execution entry point; the goals below are declared so\n"
        "that execution itself is committed, replayable and drift-checked.\n"
    )
    body.append(
        table(
            ["Goal", "Run identity (sha256)", "Stages traversed", "Stages admitted", "Deterministic"],
            [
                [
                    entry["id"],
                    entry["run_id"],
                    str(entry["stages_traversed"]),
                    str(entry["stages_admitted"]),
                    tick(entry["deterministic"]),
                ]
                for entry in model["runs"]
            ],
        )
    )
    for entry in model["runs"]:
        body.append(f"\n### {entry['id']}\n")
        body.append(f"> {entry['goal']}\n")
        if entry["note"]:
            body.append(f"{entry['note']}\n")
        body.append(
            table(
                ["#", "Stage", "Obligations bound", "Properties held", "Admitted"],
                [
                    [
                        str(step["position"]),
                        step["stage"],
                        f"{step['obligations_bound']}/{step['obligations_total']}",
                        f"{step['properties_held']}/{step['properties_total']}",
                        tick(step["admitted"]),
                    ]
                    for step in entry["steps"]
                ],
            )
        )
    body.append(
        "\n## Universal applicability\n\n"
        "The traversal names no capability. It is the same traversal for every goal, which is what\n"
        "makes it reusable by every canonical capability without modification — and why no\n"
        "capability requires its own engineering methodology and no capability list exists that\n"
        "could be incomplete.\n"
    )
    pages[PAGES[8]] = "\n".join(body) + "\n"

    # ---- 09 validation
    body = [front_matter(model, "Validation Report")]
    body.append("Every dimension is a measurement over located metadata. A blocking failure closes the gate.\n")
    body.append(
        table(
            ["Dimension", "Statement", "Measure", "Value", "Expect", "Blocking", "Result"],
            [
                [
                    entry["id"],
                    entry["dimension"],
                    code(entry["measure"]),
                    str(entry["value"]),
                    f"{entry['comparator']} {entry['expect']}",
                    yes(entry["blocking"]),
                    tick(entry["satisfied"]),
                ]
                for entry in model["validations"]
            ],
        )
    )
    body.append("\n## Bound tightness\n")
    body.append(
        f"Bounds carrying slack: **{len(model['bounds_slack'])}**. A bound wider than the divergence it\n"
        "describes would let a regression hide inside the slack, so every declared bound must equal\n"
        "its measured value exactly.\n"
    )
    if model["bounds_slack"]:
        body.append(
            table(
                ["Dimension", "Measure", "Measured", "Declared bound"],
                [
                    [entry["id"], code(entry["measure"]), str(entry["value"]), str(entry["bound"])]
                    for entry in model["bounds_slack"]
                ],
            )
        )
    pages[PAGES[9]] = "\n".join(body) + "\n"

    # ---- 10 certification
    body = [front_matter(model, "Certification Report")]
    body.append(f"## Determination — {model['determination']}\n")
    body.append(f"Gate: **{model['gate']}**. Blocking failures: **{len(model['blocking_failures'])}**.\n")
    body.append("\n## Exit criteria\n")
    body.append(
        table(
            ["Criterion", "Statement"],
            [[str(entry["id"]), str(entry["statement"])] for entry in model["exit_criteria"]],
        )
    )
    body.append("\n## Findings\n")
    body.append(
        "A measured divergence is REGISTERED and REFERRED to its owner, never adjudicated here.\n"
    )
    for entry in model["findings"]:
        body.append(f"\n### {entry['id']} — {entry['title']}\n")
        body.append(
            table(
                ["Field", "Value"],
                [
                    ["CLASS", str(entry["class"])],
                    ["DISPOSITION", str(entry["disposition"])],
                    ["BLOCKING", yes(bool(entry["blocking"]))],
                    ["REFERRED TO", code(entry["referred_to"])],
                    ["BOUND MEASURE", code(entry.get("bound_measure") or "")],
                ],
            )
        )
        body.append(f"\n{entry['detail']}\n")
        body.append(f"\n**Why not repaired.** {entry['why_not_repaired']}\n")
    body.append("\n## Immutability of the located records read\n")
    body.append(
        table(
            ["Record", "Owner", "Anchor", "Law", "Resolves", "Anchor present"],
            [
                [
                    entry["id"],
                    code(entry["owner"]),
                    code(entry["anchor"]) or "*(root)*",
                    entry["law"],
                    yes(entry["located"]),
                    yes(entry["anchor_present"]),
                ]
                for entry in model["records"]
            ],
        )
    )
    body.append(
        f"\nwrite set ∩ record set = ∅: **{yes(model['immutability']['disjoint'])}**\n"
    )
    pages[PAGES[10]] = "\n".join(body) + "\n"

    # ---- 11 admission and disposition
    body = [front_matter(model, "Admission and Disposition Determination")]
    body.append(
        "Disposition order is REUSE → EXTEND → CREATE. CREATE is a validation FAILURE wherever a\n"
        "canonical owner resolves: a capability whose owner resolves cannot be created a second\n"
        "time without manufacturing a parallel authority.\n"
    )
    body.append(
        table(
            ["Capability", "Group", "Canonical owner", "Status", "Action", "Owner resolves"],
            [
                [
                    entry["capability"],
                    entry["group"],
                    code(entry["owner"]),
                    entry["status"],
                    entry["action"],
                    yes(entry["owner_located"] and not entry["artifacts_unresolved"]),
                ]
                for entry in model["capabilities"]
            ],
        )
    )
    body.append("\n## Determination per capability\n")
    for entry in model["capabilities"]:
        body.append(f"\n### {entry['id']} — {entry['capability']}\n")
        body.append(f"**{entry['status']} · {entry['action']}** — owner {code(entry['owner'])}\n")
        body.append(f"\n{entry['evidence']}\n")
    body.append("\n## Refusals inherited and made\n")
    body.append(
        "\n".join(
            [
                "- No second lifecycle authority is created; the located owners are crosswalked, never merged.",
                "- No second registry, dictionary, namespace, resolver or identifier family is opened.",
                "- No stage, capability, owner, graph type or relation type is enumerated in code.",
                "- No architectural bound is introduced for implementation convenience.",
                "- No graph element originates from implementation source.",
                f"- Capabilities dispositioned CREATE: **{counters['capabilities_created']}**.",
            ]
        )
    )
    pages[PAGES[11]] = "\n".join(body) + "\n"

    # ---- 12 knowledge extraction + capability elevation
    body = [front_matter(model, "Knowledge Extraction and Capability Elevation Register")]
    body.append(
        "Every completed execution extracts engineering knowledge, and that knowledge becomes\n"
        "Canonical Knowledge Objects so it accumulates constitutionally across future cycles.\n"
        "Extraction is a MEASUREMENT of the run, never an assertion about it. Registration is\n"
        "delegated to the located knowledge home: this programme opens no knowledge store, because\n"
        "Knowledge Once means the canonical home already exists and a second one would fork it.\n"
    )
    body.append(
        table(
            ["Knowledge", "Measure", "Value", "Measured", "Registers with", "Reusable as"],
            [
                [
                    str(entry["knowledge"]),
                    code(entry["measure"]),
                    str(entry["value"]),
                    yes(entry["measured"]),
                    code(entry["registration_owner"]),
                    str(entry["reusable_as"]),
                ]
                for entry in model["extractions"]
            ],
        )
    )
    body.append("\n## Capability elevation\n")
    body.append(
        "Three increases, each MEASURED from the discovered graph rather than asserted, and each\n"
        "carrying evidence, lineage, replay, certification and a governing authority. An increase\n"
        "whose facets do not all resolve is reported as unevidenced rather than claimed.\n"
    )
    body.append(
        table(
            ["Increase", "Measure", "Value", "Evidenced", "What increased"],
            [
                [
                    str(entry["increase"]),
                    code(entry["measure"]),
                    str(entry["value"]),
                    tick(entry["evidenced"]),
                    str(entry["statement"]),
                ]
                for entry in model["elevations"]
            ],
        )
    )
    for entry in model["elevations"]:
        body.append(f"\n### {entry['id']} — {entry['increase']}\n")
        body.append(
            table(
                ["Facet", "Located owner", "Resolves"],
                [
                    [name.replace("_owner", ""), code(owner), yes(exists(owner))]
                    for name, owner in sorted(entry["facets"].items())
                ],
            )
        )
    pages[PAGES[12]] = "\n".join(body) + "\n"

    # ---- 13 self-evolution + Ω-E05 readiness
    body = [front_matter(model, "Self-Evolution and Ω-E05 Readiness Certification")]
    body.append(
        "The substrate may evolve itself, but only along the declared path, and never outside\n"
        "constitutional governance. Each step is owned OUTSIDE this programme, so self-modification\n"
        "cannot route around a step by construction: the step's owner is not this programme.\n"
    )
    body.append(
        table(
            ["Step", "Located owner", "Anchor", "Resolves", "Anchor present", "Owned externally"],
            [
                [
                    str(entry["step"]),
                    code(entry["owner"]),
                    code(entry["anchor"]) or "*(root)*",
                    yes(entry["located"]),
                    yes(entry["anchor_present"]),
                    yes(entry["external"]),
                ]
                for entry in model["self_evolution"]
            ],
        )
    )
    body.append("\n## Constitutional identity model\n")
    body.append(
        "`cko_id` is a local HANDLE and may change. `semantic_id` is the CONSTITUTIONAL IDENTITY and\n"
        "is derived exclusively from immutable constitutional identity fields. A digest is used, but\n"
        "only over those fields — a digest over anything mutable would be a fingerprint masquerading\n"
        "as an identity. Digests are separately used for integrity, replay and deterministic\n"
        "evidence (the graph digest and the run identity), and neither is ever an identity.\n"
    )
    body.append(
        table(
            ["Property", "Value"],
            [
                ["Identity inputs", " · ".join(code(v) for v in model["semantic_identity"]["inputs"])],
                ["Excluded (may evolve)", " · ".join(code(v) for v in model["semantic_identity"]["excluded_inputs"])],
                ["Objects without a constitutional identity", str(len(model["semantic_identity"]["without_identity"]))],
                ["Identity collisions", str(len(model["semantic_identity"]["collisions"]))],
                ["Identities resting on a mutable input", str(len(model["semantic_identity"]["mutable_inputs"]))],
                ["Relationship CKOs", str(model["counters"]["relationship_ckos_discovered"])],
                ["Relationships whose target carries no registered identity", str(model["semantic_identity"]["relationships_without_target_identity"])],
            ],
        )
    )
    body.append("\n## Ω-E05 readiness\n")
    body.append(
        "Ω-E04 certifies whether Ω-E05 may begin. Every dimension is MEASURED against a located\n"
        "owner: readiness is a statement about the repository, so a dimension whose owner does not\n"
        "resolve, or whose measure is unmet, reports NOT READY rather than being waived.\n"
    )
    body.append(
        table(
            ["Dimension", "Located owner", "Measure", "Value", "Expect", "Ready"],
            [
                [
                    str(entry["dimension"]),
                    code(entry["owner"]),
                    code(entry["measure"]),
                    str(entry["value"]),
                    f"{entry['comparator']} {entry['expect']}",
                    tick(entry["ready"]),
                ]
                for entry in model["readiness"]
            ],
        )
    )
    ready = sum(1 for entry in model["readiness"] if entry["ready"])
    body.append(
        f"\n**Readiness: {ready}/{len(model['readiness'])} dimensions.** "
        f"Gate: **{model['gate']}**.\n"
    )
    body.append(
        f"\n## Determination — Ω-E05 "
        f"{'AUTHORIZED' if model['omega_e05_authorized'] else 'NOT AUTHORIZED'}\n"
    )
    body.append(
        "Ω-E05 is authorized only when every readiness dimension is ready AND the gate is OPEN.\n"
        "Authorization confers no ratification, no finality and no authority: it records that the\n"
        "substrate Ω-E05 must bind to is discovered, executable, replayable and convergent.\n"
    )
    pages[PAGES[13]] = "\n".join(body) + "\n"

    return pages


def _ordered(model: dict) -> list[dict]:
    position = {cko_id: index for index, cko_id in enumerate(model["order"])}
    return sorted(model["stages"], key=lambda stage: (position.get(stage["cko_id"], len(position)), stage["cko_id"]))


def _cell(stage: dict, name: str, tokens: dict) -> str:
    if stage["applicability"].get(name) == tokens["not_applicable"]:
        return "n/a"
    return tick(bool(stage["obligations"].get(name)))


def _scope_count(model: dict, name: str) -> int:
    na = model["applicability_tokens"]["not_applicable"]
    return sum(1 for stage in model["stages"] if stage["applicability"].get(name) != na)


def _bound_count(model: dict, name: str) -> int:
    na = model["applicability_tokens"]["not_applicable"]
    return sum(
        1
        for stage in model["stages"]
        if stage["applicability"].get(name) != na and stage["obligations"].get(name)
    )


def _na_count(model: dict, name: str) -> int:
    na = model["applicability_tokens"]["not_applicable"]
    return sum(1 for stage in model["stages"] if stage["applicability"].get(name) == na)


def _path_symbol(model: dict, path_id: str) -> str:
    for entry in model["admission_paths"]:
        if entry["id"] == path_id:
            return entry["symbol"]
    return ""


def write_registers(model: dict) -> list[str]:
    HERE.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, text in render(model).items():
        (HERE / name).write_text(text, encoding="utf-8")
        written.append(name)
    MODEL.write_text(json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(MODEL.name)
    return sorted(written)


# --------------------------------------------------------------------------- guards


def check_declaration(document: dict) -> list[str]:  # noqa: C901 - one integrity rule per section
    problems: list[str] = []
    seen: set[str] = set()
    sections = (
        "serializations",
        "discovery_classes",
        "metadata_providers",
        "metadata_adapters",
        "lifecycle_authorities",
        "obligation_rules",
        "property_rules",
        "admission_paths",
        "expansion_axes",
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
                seen.add(str(identifier))
    for group in (document["cko_model"]["kinds"], document["cko_model"]["relation_types"], document["graph_types"]["types"], document["record_set"]["records"], document["unboundedness"]["dimensions"], document["execution"]["canonical_goals"]):
        for entry in group:
            identifier = str(entry.get("id") or "")
            if identifier in seen:
                problems.append(f"duplicate id across the declaration: {identifier}")
            seen.add(identifier)

    measures = [str(entry["measure"]) for entry in document["validations"]]
    problems += [
        f"validations: duplicate measure {item}"
        for item in sorted({m for m in measures if measures.count(m) > 1})
    ]

    for key in ("law_owner", "architecture_owner"):
        if not (REPO / str(document["programme"][key])).is_file():
            problems.append(f"programme.{key} does not resolve")
    for entry in document["metadata_providers"]:
        if not exists(str(entry["owner"])):
            problems.append(f"{entry['id']}: provider owner does not resolve: {entry['owner']}")
        if not any(str(s["id"]) == str(entry["serialization"]) for s in document["serializations"]):
            problems.append(f"{entry['id']}: names an unknown serialization {entry['serialization']}")
    provider_ids = {str(entry["id"]) for entry in document["metadata_providers"]}
    provider_ids.add(str(document["provider_discovery"]["id"]))
    kinds = {str(entry["kind"]) for entry in document["cko_model"]["kinds"]}
    relations = {str(entry["relation"]) for entry in document["cko_model"]["relation_types"]}
    for entry in document["metadata_adapters"]:
        if str(entry["provider"]) not in provider_ids:
            problems.append(f"{entry['id']}: names an unknown provider {entry['provider']}")
        if str(entry["cko_kind"]) not in kinds:
            problems.append(f"{entry['id']}: emits an unregistered object kind {entry['cko_kind']}")
        for relation in (entry.get("relation_map") or {}):
            if str(relation) not in relations:
                problems.append(f"{entry['id']}: maps an unregistered relation {relation}")
    for entry in document["graph_types"]["types"]:
        for kind in entry["node_kinds"]:
            if str(kind) not in kinds:
                problems.append(f"{entry['id']}: names an unregistered object kind {kind}")
        for relation in entry["edge_relations"]:
            if str(relation) not in relations:
                problems.append(f"{entry['id']}: names an unregistered relation {relation}")
    for entry in document["lifecycle_authorities"]:
        if not exists(str(entry["owner"])):
            problems.append(f"{entry['id']}: authority owner does not resolve: {entry['owner']}")
        if not str(entry.get("anchor", "")).strip():
            problems.append(f"{entry['id']}: no anchor recorded")
    for entry in document["admission_paths"]:
        if not exists(str(entry["owner"])):
            problems.append(f"{entry['id']}: admission path owner does not resolve: {entry['owner']}")
    path_ids = {str(entry["id"]) for entry in document["admission_paths"]}
    for entry in document["expansion_axes"]:
        if str(entry["admission_path"]) not in path_ids:
            problems.append(f"{entry['id']}: names an unknown admission path {entry['admission_path']}")
    for entry in document["capabilities"]:
        if not exists(str(entry["owner"])):
            problems.append(f"{entry['id']}: capability owner does not resolve: {entry['owner']}")
    for entry in document["record_set"]["records"]:
        if not exists(str(entry["owner"])):
            problems.append(f"{entry['id']}: record owner does not resolve: {entry['owner']}")
    if not (REPO / str(document["unboundedness"]["owner"])).is_file():
        problems.append("unboundedness: owner does not resolve")
    if not (REPO / str(document["law_source"]["owner"])).is_file():
        problems.append("law_source: owner does not resolve")

    forbidden = [str(p) for p in document["programme"]["forbidden_write_prefixes"]]
    claimants = {str(document["programme"][k]) for k in ("law_owner", "architecture_owner")}
    claimants |= {str(e["owner"]) for e in document["metadata_providers"]}
    claimants |= {str(e["owner"]) for e in document["lifecycle_authorities"]}
    claimants |= {str(e["owner"]) for e in document["admission_paths"]}
    claimants |= {str(e["owner"]) for e in document["record_set"]["records"]}
    claimants |= {str(document["unboundedness"]["owner"]), str(document["law_source"]["owner"])}
    for claimant in sorted(claimants):
        if claimant.startswith(OWN_PREFIX):
            continue
        if not any(claimant.startswith(prefix) for prefix in forbidden):
            problems.append(f"a claimant is left unprotected by forbidden_write_prefixes: {claimant}")

    findings = {str(f["id"]) for f in document["findings"]}
    for entry in document["validations"]:
        if str(entry.get("comparator")) == "<=":
            bound_finding = entry.get("bound_finding")
            if not bound_finding:
                problems.append(f"{entry['id']}: declares a bound with no disposing finding")
            elif str(bound_finding) not in findings:
                problems.append(f"{entry['id']}: names an unknown finding {bound_finding}")
    if not any(str(c["action"]) == ACTION_EXTEND for c in document["capabilities"]):
        problems.append("no capability is dispositioned EXTEND, so this programme implements no gap")
    for entry in document["capabilities"]:
        if str(entry["status"]) == STATUS_MISSING and str(entry["action"]) != ACTION_CREATE:
            problems.append(f"{entry['id']}: MISSING without CREATE is not a disposition")
        if str(entry["status"]) == STATUS_EXISTING and str(entry["action"]) != ACTION_REUSE:
            problems.append(f"{entry['id']}: EXISTING must be dispositioned REUSE")
        if str(entry["status"]) == STATUS_PARTIAL and str(entry["action"]) != ACTION_EXTEND:
            problems.append(f"{entry['id']}: PARTIAL must be dispositioned EXTEND")
    return problems


def _schema_vocabulary(payload: Any, out: set[str] | None = None) -> set[str]:
    """Every field name the declaration itself uses, at any depth.

    This is the engine's lawful vocabulary: it may name the fields of its own
    declaration without that being an enumeration of the data those fields carry.
    """
    words = set() if out is None else out
    if isinstance(payload, dict):
        for key, value in payload.items():
            words.add(str(key).strip().lower())
            _schema_vocabulary(value, words)
    elif isinstance(payload, list):
        for item in payload:
            _schema_vocabulary(item, words)
    return words


def _executable_literals() -> set[str]:
    """Every string constant this engine could actually branch on.

    Parsed from the syntax tree, so COMMENTS are excluded entirely and DOCSTRINGS are
    removed explicitly. The objective of enumeration detection is to prevent hardcoded
    constitutional behaviour, not to prevent constitutional terminology from appearing
    in prose: a docstring saying this engine registers nothing is documentation, and a
    comment naming a stage would change no behaviour. Only a literal in executable
    position could make the engine treat one discovered value differently from another.
    """
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    docstrings.add(id(body[0].value))
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings
    }


def check_no_enumeration(document: dict) -> list[str]:
    """No discovered value may steer behaviour from inside this engine.

    This is the mechanical proof that the lifecycle is graph-driven rather than
    enumeration-driven: if the engine cannot name what it discovered, it cannot have
    hard-coded it, and admitting a new member cannot require editing it.

    The scan distinguishes EXECUTABLE BEHAVIOUR from documentation. Only string
    constants in executable position are examined — comments and docstrings are
    excluded by construction, because prose that names a stage changes nothing. The
    declaration's own field names are GOVERNED VOCABULARY and are likewise exempt:
    an engine must be able to name the fields of its declaration, and the vocabulary
    is derived from the declaration's keys rather than listed, so the exemption cannot
    be widened by hand. A discovered stage name, owner path, identifier or graph type
    is never a declaration key, so none of them can hide inside it.
    """
    literals = _executable_literals()
    schema_words = _schema_vocabulary(document)
    model = measure(document)
    leaked: list[str] = []

    def literal(value: str) -> bool:
        text = str(value).strip()
        if not text or text.lower() in schema_words:
            return False
        return text in literals

    def embedded(value: str) -> bool:
        text = str(value).strip()
        if not text:
            return False
        return any(text in item for item in literals)

    for stage in model["stages"]:
        if embedded(stage["record_id"]):
            leaked.append(f"stage identifier steers behaviour: {stage['record_id']}")
        if literal(stage["stage"]):
            leaked.append(f"stage name steers behaviour: {stage['stage']}")
        for value in (stage["owner"], stage["authority_owner"]):
            if embedded(value):
                leaked.append(f"stage owner path steers behaviour: {value}")
    for entry in model["graphs"]:
        if literal(entry["graph"]):
            leaked.append(f"graph type steers behaviour: {entry['graph']}")
        if embedded(entry["id"]):
            leaked.append(f"graph type identifier steers behaviour: {entry['id']}")
    for entry in model["capabilities"]:
        if embedded(entry["owner"]):
            leaked.append(f"capability owner steers behaviour: {entry['owner']}")
    for entry in model["providers"]:
        if embedded(entry["owner"]):
            leaked.append(f"provider owner steers behaviour: {entry['owner']}")
    for entry in model["adapters"]:
        if embedded(entry["id"]):
            leaked.append(f"adapter identifier steers behaviour: {entry['id']}")
    for entry in model["admission_paths"]:
        if embedded(entry["owner"]):
            leaked.append(f"admission path steers behaviour: {entry['owner']}")
    for name in model["cko_model"]["kinds"]:
        if literal(name):
            leaked.append(f"object kind steers behaviour: {name}")
    for name in model["cko_model"]["relation_types"]:
        if literal(name):
            leaked.append(f"relation type steers behaviour: {name}")
    for entry in model["expansion_axes"]:
        if literal(entry["axis"]):
            leaked.append(f"expansion axis steers behaviour: {entry['axis']}")
    return sorted(set(leaked))


def check_write_scope(document: dict) -> list[str]:
    problems: list[str] = []
    for name in PAGES:
        try:
            (HERE / name).resolve().relative_to(HERE)
        except ValueError:  # pragma: no cover - defensive
            problems.append(name)
    model = measure(document)
    if set(render(model)) != set(PAGES):
        problems.append("the renderer does not produce exactly the declared page set")
    for prefix in document["programme"]["forbidden_write_prefixes"]:
        if OWN_PREFIX.startswith(str(prefix)):
            problems.append(f"own home falls inside a forbidden prefix: {prefix}")
    problems += [f"writes outside its home: {p}" for p in model["immutability"]["outside_home"]]
    problems += [f"writes inside a forbidden prefix: {p}" for p in model["immutability"]["forbidden_trespass"]]
    return problems


def check_determinism(document: dict) -> list[str]:
    first, second = render(measure(document)), render(measure(document))
    problems = sorted(name for name in first if first[name] != second.get(name))
    if measure(document)["seal_sha256"] != measure(document)["seal_sha256"]:  # pragma: no cover
        problems.append("the seal is not stable across two measurements")
    source = Path(__file__).read_text(encoding="utf-8")
    for forbidden in document["hygiene"]["nondeterministic_inputs"]:
        if str(forbidden) in source:
            problems.append(f"the engine reads a non-deterministic input: {forbidden}")
    model = measure(document)
    problems += [f"{r['id']}: run is not deterministic" for r in model["runs"] if not r["deterministic"]]
    return problems


def check_implementation_independence(document: dict) -> list[str]:
    """No Canonical Knowledge Object or relation may originate from implementation source."""
    model = measure(document)
    problems: list[str] = []
    originating = {
        str(entry["id"])
        for entry in document["discovery_classes"]
        if entry.get(CLASS_MAY_ORIGINATE)
    }
    for stage in model["stages"]:
        if stage["provenance"]["discovery_class"] not in originating:
            problems.append(f"{stage['record_id']}: originated by an evidence-class provider")
    if model["counters"]["evidence_originated_ckos"]:
        problems.append(
            f"{model['counters']['evidence_originated_ckos']} objects originated outside constitutional metadata"
        )
    for entry in document["metadata_adapters"]:
        provider = str(entry["provider"])
        for declared in document["metadata_providers"]:
            if str(declared["id"]) != provider:
                continue
            if str(declared["discovery_class"]) not in originating:
                problems.append(f"{entry['id']}: adapter bound to an evidence-class provider")
    if not model["stages"]:
        problems.append("no stage was discovered, so implementation independence is unmeasured")
    return problems


def check_open_world(document: dict) -> list[str]:
    """No finite bound may be declared, and every open registry must name a live registrar."""
    model = measure(document)
    problems = [f"architectural bound token present: {hit}" for hit in model["bound_hits"]]
    problems += [
        f"{entry['id']}: expansion axis has no resolving admission path"
        for entry in model["expansion_axes"]
        if entry["blocking"] and not entry["bound"]
    ]
    for entry in model["providers"]:
        if entry["discovered"] and not (entry["open"] is True and entry["closed_enumeration"] is False):
            problems.append(f"{entry['owner']}: discovered provider does not declare itself open")
    if document["cko_model"].get("open") is not True or document["cko_model"].get("closed_enumeration") is not False:
        problems.append("the object kind registry is not declared open")
    if document["graph_types"].get("open") is not True or document["graph_types"].get("closed_enumeration") is not False:
        problems.append("the graph type registry is not declared open")
    if model["counters"]["serialization_readers_registered"] < 2:
        problems.append("only one serialization reader is registered, so discovery is format-bound")
    if not any(not entry.get("registered") for entry in document["serializations"]):
        problems.append("no unregistered serialization is admitted, so the registry is closed in practice")
    if model["counters"]["reentry_declarations_absent"]:
        problems.append("no re-entry is declared, so the lifecycle would terminate")
    return problems


def check_no_parallel_authority(document: dict) -> list[str]:
    """The programme that refuses a second lifecycle must not become one."""
    model = measure(document)
    problems: list[str] = []
    if not str(model["programme"]["authority"]).startswith("NONE"):
        problems.append("this measurement claims an authority")
    for entry in model["authorities"]:
        if entry["claimed_here"]:
            problems.append(f"{entry['id']}: a located lifecycle authority is claimed by this programme")
        if not entry["located"]:
            problems.append(f"{entry['id']}: located lifecycle authority does not resolve")
        if not entry["anchor_present"]:
            problems.append(f"{entry['id']}: anchor absent from the authority's own text")
    for entry in model["capabilities"]:
        if entry["action"] == ACTION_CREATE:
            problems.append(f"{entry['id']}: dispositioned CREATE, which would manufacture a parallel authority")
    for finding in model["findings"]:
        if str(finding["disposition"]) not in ("REGISTERED", "GOVERNED"):
            problems.append(f"{finding['id']}: a divergence was decided rather than referred")
    write_set = set(model["immutability"]["write_set"])
    for entry in model["records"]:
        if entry["owner"] in write_set:
            problems.append(f"{entry['id']}: this programme writes a located record")
    return problems


def check_lifecycle_executable(document: dict) -> list[str]:
    """The lifecycle must be a real, orderable, executable graph — not a table of names."""
    model = measure(document)
    problems: list[str] = []
    if not model["stages"]:
        problems.append("no constitutional stage was discovered")
    if not model["order"]:
        problems.append("the discovered graph produced no traversal order")
    if len(model["order"]) != len(model["stages"]):
        problems.append("the traversal does not cover every discovered stage")
    problems += [f"the dependency graph is cyclic at {node}" for node in model["cycles"]]
    if not model["dependency_relation"]:
        problems.append("no dependency relation was discovered, so ordering is not derived")
    problems += [
        f"{entry['id']}: canonical goal did not execute deterministically"
        for entry in model["runs"]
        if not entry["deterministic"]
    ]
    if not model["runs"]:
        problems.append("no canonical goal was executed, so the lifecycle is unproven as executable")
    for entry in model["runs"]:
        if entry["stages_traversed"] != len(model["stages"]):
            problems.append(f"{entry['id']}: traversal skipped a discovered stage")
    for stage in model["stages"]:
        if not exists(stage["owner"]):
            problems.append(f"{stage['record_id']}: canonical owner does not resolve")
        if not exists(stage["authority_owner"]):
            problems.append(f"{stage['record_id']}: constitutional authority owner does not resolve")
    for entry in model["graphs"]:
        if not entry["kinds_known"] or not entry["relations_known"]:
            problems.append(f"{entry['id']}: composes an unregistered kind or relation")
    if model["counters"]["dangling_relations"]:
        problems.append(f"{model['counters']['dangling_relations']} relations resolve to nothing")
    return problems


def check_record_immutability(document: dict) -> list[str]:
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


def check_knowledge_once(document: dict) -> list[str]:
    """Every stage, capability and graph member is discovered, never defined here."""
    problems: list[str] = []
    raw = DECLARATION.read_text(encoding="utf-8")
    model = measure(document)
    # Tested by IDENTIFIER. A stage record without its constitutional identifier is not a
    # stage record, so the identifier is what would constitute a definition here. A stage
    # NAME appearing elsewhere in the declaration is governed vocabulary — the
    # self-evolution path deliberately shares wording with the stages it routes through —
    # and descriptive vocabulary is not a definition.
    for stage in model["stages"]:
        if stage["record_id"] and stage["record_id"] in raw:
            problems.append(f"the declaration defines a discovered stage: {stage['record_id']}")
    if not model["counters"]["stage_nodes_discovered"]:
        problems.append("no stage was discovered from located metadata")
    if not model["counters"]["capability_nodes_discovered"]:
        problems.append("no capability was discovered from located metadata")
    if not model["counters"]["ckos_discovered"]:
        problems.append("no Canonical Knowledge Object was discovered")
    return problems


def check_bounds_tight(document: dict) -> list[str]:
    model = measure(document)
    return [
        f"{entry['id']}: bound {entry['bound']} exceeds the measured divergence {entry['value']} ({entry['measure']})"
        for entry in model["bounds_slack"]
    ]


def check_cko_identity(document: dict) -> list[str]:
    """Constitutional law: exactly one CKO per governed entity, and nothing derived is truth.

    The Canonical Knowledge Object is the immutable constitutional identity of the
    entity. Every register, graph, report, projection, measurement and certificate
    this programme emits is DERIVED from those objects — and none of them may be read
    back as a source, or a derived view would have become Repository Truth.
    """
    model = measure(document)
    problems = [
        f"an entity holds more than one Canonical Knowledge Object: {item}"
        for item in model["identity_collisions"]
    ]
    problems += [
        f"a derived artifact is used as a metadata source: {item}"
        for item in model["truth_class"]["derived_used_as_truth"]
    ]
    for entry in model["providers"]:
        if entry["owner"].startswith(OWN_PREFIX) and not entry["discovered"]:
            problems.append(f"{entry['owner']}: a source inside this home is not a discovered declaration")
    if not model["counters"]["ckos_discovered"]:
        problems.append("no Canonical Knowledge Object was discovered, so identity is unmeasured")
    for stage in model["stages"]:
        if not stage["record_id"]:
            problems.append("a discovered stage carries no constitutional identity")
    return problems


def check_semantic_identity(document: dict) -> list[str]:
    """Constitutional identity must be immutable, singular, and free of mutable inputs.

    A digest is legitimate for integrity, replay, deterministic evidence and
    fingerprinting. It becomes a constitutional identity only when derived exclusively
    from immutable constitutional identity fields — so this guard proves that no input
    the invariants permit to evolve participates in the derivation.
    """
    model = measure(document)
    identity = model["semantic_identity"]
    problems = [f"object carries no constitutional identity: {item}" for item in identity["without_identity"][:20]]
    problems += [f"constitutional identity rests on a mutable input: {item}" for item in identity["mutable_inputs"][:20]]
    problems += [f"two determinate entities share a constitutional identity: {item}" for item in identity["collisions"][:20]]
    declared = [str(name) for name in identity["inputs"]]
    for name in identity["excluded_inputs"]:
        if str(name) in declared:
            problems.append(f"an excluded input is declared as an identity input: {name}")
    if not declared:
        problems.append("no identity input is declared, so identity is underivable")
    # Relationships must be first-class and discovered through the same pipeline.
    if not model["counters"]["relationship_ckos_discovered"]:
        problems.append("no relationship object was discovered, so relationships are not first-class")
    originating = {
        str(entry["id"]) for entry in document["discovery_classes"] if entry.get(CLASS_MAY_ORIGINATE)
    }
    for entry in model["relationships"][:200]:
        if str(entry["provenance"].get("discovery_class") or "") not in originating:
            problems.append(f"relationship not traced to an originating provider: {entry['cko_id']}")
    return problems


GUARDS = {
    "check-declaration": check_declaration,
    "check-no-enumeration": check_no_enumeration,
    "check-write-scope": check_write_scope,
    "check-determinism": check_determinism,
    "check-implementation-independence": check_implementation_independence,
    "check-open-world": check_open_world,
    "check-no-parallel-authority": check_no_parallel_authority,
    "check-lifecycle-executable": check_lifecycle_executable,
    "check-cko-identity": check_cko_identity,
    "check-semantic-identity": check_semantic_identity,
    "check-knowledge-once": check_knowledge_once,
    "check-record-immutability": check_record_immutability,
    "check-bounds-tight": check_bounds_tight,
}


# --------------------------------------------------------------------------- entry point


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    parser.add_argument("--render", action="store_true", help="regenerate the registers")
    parser.add_argument("--gate", action="store_true", help="fail-closed lifecycle gate")
    parser.add_argument("--execute", metavar="GOAL", help="execute the discovered lifecycle for an arbitrary goal")
    parser.add_argument("--quiet", action="store_true")
    for name in GUARDS:
        parser.add_argument(f"--{name}", action="store_true")
    args = parser.parse_args(argv)

    try:
        document = load_declaration()
    except FailClosed as exc:
        print(f"UCL-000001 ABORT: {exc}", file=sys.stderr)
        return 2

    selected = [name for name in GUARDS if getattr(args, name.replace("-", "_"))]
    if selected:
        failed = False
        for name in selected:
            try:
                problems = GUARDS[name](document)
            except FailClosed as exc:
                print(f"UCL-000001 ABORT: {exc}", file=sys.stderr)
                return 2
            if problems:
                failed = True
                print(f"UCL-000001 {name}: FAIL ({len(problems)})", file=sys.stderr)
                for problem in problems[:40]:
                    print(f"  - {problem}", file=sys.stderr)
            else:
                print(f"UCL-000001 {name}: PASS")
        return 1 if failed else 0

    try:
        model = measure(document)
    except FailClosed as exc:
        print(f"UCL-000001 ABORT: {exc}", file=sys.stderr)
        return 2

    if args.execute is not None:
        # The substrate entry point ACEE binds to. Writes nothing.
        by_cko = {stage["cko_id"]: {"name": stage["stage"], "attributes": {"owner": stage["owner"]}} for stage in model["stages"]}
        obligations = {stage["cko_id"]: stage["obligations"] for stage in model["stages"]}
        properties = {stage["cko_id"]: stage["properties"] for stage in model["stages"]}
        record = execute(args.execute, model["order"], by_cko, obligations, properties, model["graph_digest"])
        print(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False))
        return 0

    written = write_registers(model)
    counters = model["counters"]
    if not args.quiet:
        print(
            f"UCL-000001: {model['determination']} "
            f"| ckos={counters['ckos_discovered']} "
            f"| relations={counters['relations_discovered']} "
            f"| stages={counters['stage_nodes_discovered']} "
            f"| order={len(model['order'])} cycles={counters['graph_cycles']} "
            f"| providers={len(model['providers'])}({counters['providers_without_reader']}noreader) "
            f"| adapters={len(model['adapters']) - counters['adapters_unresolved']}/{len(model['adapters'])} "
            f"| graphs={len(model['graphs']) - counters['graph_types_empty']}/{len(model['graphs'])} "
            f"| axes={len(model['expansion_axes']) - counters['expansion_axes_unbound']}/{len(model['expansion_axes'])} "
            f"| obligations={counters['stage_obligation_failures']}unbound "
            f"| properties={counters['stage_property_failures']}unmet "
            f"| runs={len(model['runs']) - counters['runs_nondeterministic']}/{len(model['runs'])}det "
            f"| criteria={sum(1 for v in model['validations'] if v['satisfied'])}/{len(model['validations'])} "
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
