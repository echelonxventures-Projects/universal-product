#!/usr/bin/env python3
"""ACEE-000001 — Autonomous Constitutional Engineering Engine.

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates no lifecycle, opens no
registry, mints no identifier, declares no namespace, admits no capability,
authorizes no engineering and certifies nothing. It DISCOVERS the engineering plane
the repository has already legislated — the lifecycle phases every engineering goal
traverses, the executable capabilities that discharge them, the quality capabilities
that validate and verify them, the gates that certify them and the dispositions that
govern them — normalizes all of it into Canonical Knowledge Objects, and derives, for
any engineering goal, the complete engineering plan bound to located owners.

It is not a second lifecycle. UCIC-001 owns the single deterministic lifecycle every
capability follows and UCL-000001 made that lifecycle executable; this engine binds a
GOAL to it. It is not a second loop: UCOS-AEE-001 owns the closed repository-directed
loop, and this engine invokes no engine and re-runs no owner. It is not a second
registry, dictionary, identifier scheme or knowledge store.

Everything it enforces is read from ``acee-declaration.json``. This source file
contains no phase, no phase name, no capability, no goal, no owner path, no gate, no
disposition, no object kind, no relation type and no graph type: admitting any of them
is an append-only edit to DATA and requires no change here (PR-07 Zero Enumeration).

Discovery pipeline (metadata in, Canonical Knowledge Objects out):

    Metadata Provider  — WHERE engineering metadata lives, in which serialization
        ↓
    Metadata Adapter   — HOW those records normalize into CKOs of a declared kind
        ↓
    Canonical Knowledge Objects — kind, identity, owner, authority, provenance, relations
        ↓
    Engineering Engine — composes graphs, measures obligations and properties,
                         determines disposition, orders, plans

The engine never sees a file, a format or a field name below the adapter layer, so
replacing a serialization or a storage technology changes no object kind, no relation,
no graph type, no obligation, no property, no phase and no capability.

Three planes are measured, each identified by what the declaration says it is MEASURED
BY rather than by its name:

    the goal plane       — measured by OBLIGATIONS: does an engineering goal carry a
                           located subject, a canonical owner, a constitutional
                           authority, a disposition derived from Repository Truth, and
                           a plan with no unbound step and no manual decision?
    the invariant plane  — measured by PROPERTIES: is each constitutional completion
                           invariant owned, anchored, machine-readable, measured and
                           satisfied by a located owner — so that it is REUSED rather
                           than reimplemented?
    the lifecycle plane  — measured by TRAVERSAL: the stage graph a plan walks. This
                           plane is CONSUMED, never re-derived. UCIC-001 owns the single
                           deterministic lifecycle and UCL-000001 already made it
                           discoverable and ordered; this engine reads that graph and
                           binds a goal to it. Re-deriving a lifecycle here would be the
                           parallel lifecycle the constitution forbids.

Disposition is DERIVED, never asserted: the ordered disposition rules resolve each
subject to one of the located disposition values the repository already legislates, and
CREATE is reachable only where Repository Truth proves no canonical owner exists.

Implementation independence: only a provider whose discovery class MAY ORIGINATE
contributes objects. Implementation source is read as EVIDENCE only — to confirm a
symbol exists — and ``--check-implementation-independence`` fails closed if any object
or relation is ever traced to an evidence-class provider.

No privileged path: this engine holds no branch keyed on its own identity, its own home
or its own programme, and it appears in the goal plane as a subject like any other.
``--check-no-privileged-logic`` fails closed if it ever exempts itself.

Determinism: the output is a pure function of tracked repository content. Nothing here
reads the wall clock, the commit identity (RFP-2) or the working tree's own status
(RFP-3), so the emitted bytes are stable and the repository remains a fixed point.
Planning resolves and records; it never invokes a capability, because invoking the
capabilities it measures would make this engine observe a run of itself — the
self-observation topology RFP-3 forbids. Actuation is discharged by the located owners
of the execution surfaces this engine measures, and by no one else.

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
DECLARATION = HERE / "acee-declaration.json"
MODEL = HERE / "acee.json"
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
    "planes",
    "relationship_model",
    "semantic_identity",
    "knowledge_extraction",
    "elevation_measures",
    "reduction_measures",
    "self_evolution_path",
    "exit_dimensions",
    "derived_counters",
    "graph_types",
    "engineering_authorities",
    "obligation_rules",
    "property_rules",
    "disposition_rules",
    "goal_contract",
    "admission_paths",
    "expansion_axes",
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
    "00-AUTONOMOUS-CONSTITUTIONAL-ENGINEERING-DASHBOARD.md",
    "01-ENGINEERING-GOAL-REGISTER.md",
    "02-GOAL-OBLIGATION-BINDING-MATRIX.md",
    "03-CONSTITUTIONAL-COMPLETION-INVARIANT-REGISTER.md",
    "04-AUTONOMOUS-DISPOSITION-DETERMINATION-REGISTER.md",
    "05-CANONICAL-KNOWLEDGE-OBJECT-AND-GRAPH-REGISTER.md",
    "06-METADATA-PROVIDER-AND-ADAPTER-REGISTER.md",
    "07-OPEN-WORLD-EXPANSION-AXIS-REGISTER.md",
    "08-GOAL-DRIVEN-ENGINEERING-PLAN-REGISTER.md",
    "09-ENGINEERING-AUTHORITY-CROSSWALK-REGISTER.md",
    "10-FUTURE-ENGINEERING-REDUCTION-REGISTER.md",
    "11-KNOWLEDGE-EXTRACTION-AND-CAPABILITY-ELEVATION-REGISTER.md",
    "12-VALIDATION-REPORT.md",
    "13-CERTIFICATION-REPORT.md",
    "14-SELF-ENGINEERING-AND-NON-PRIVILEGE-REGISTER.md",
    "15-OMEGA-E05-EXIT-CERTIFICATION.md",
)

ACTION_CREATE = "CREATE"
ACTION_REUSE = "REUSE"
ACTION_EXTEND = "EXTEND"
STATUS_EXISTING = "EXISTING"
STATUS_PARTIAL = "PARTIAL"
STATUS_MISSING = "MISSING"
CLASS_MAY_ORIGINATE = "may_originate"
MEASURED_BY_OBLIGATIONS = "obligations"
MEASURED_BY_PROPERTIES = "properties"
MEASURED_BY_TRAVERSAL = "traversal"
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

_SELECTOR = re.compile(r"^([^\[\]]*)\[([^\[\]=]+)=([^\[\]]*)\]$")


def follow(payload: Any, pointer: str) -> Any:
    """Walk a dotted pointer. An empty pointer resolves to the document root.

    A step may carry a declared SELECTOR — ``name[field=value]`` — which picks the one
    member of a sequence whose field holds that value. Selection is a property of the
    pointer, not of the engine: which collection is selected, by which field, at which
    value, is entirely declared. Without it a metadata owner that keys its collections
    by a field rather than by a key would be unreadable, and the only alternative would
    be to teach this engine that owner's shape — which is exactly the hard-coding the
    zero-enumeration invariant forbids.
    """
    current = payload
    if not pointer:
        return current
    for step in str(pointer).split("."):
        match = _SELECTOR.match(step)
        if match is not None:
            name, field, value = match.group(1), match.group(2), match.group(3)
            if name:
                current = current[name] if isinstance(current, dict) and name in current else None
            if not isinstance(current, list):
                return None
            chosen = None
            for item in current:
                if isinstance(item, dict) and str(item.get(field, "")) == value:
                    chosen = item
                    break
            current = chosen
            if current is None:
                return None
            continue
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
    """Declared providers, plus every provider a located pattern discovers.

    The patterns are declared; the discovered providers are NOT listed anywhere, which
    is what keeps a future engineering goal and a future completion invariant
    automatically discoverable and stops this declaration from becoming an enumeration
    of either by the back door.

    ``provider_discovery`` is a LIST of surfaces because the repository has more than one
    open surface to offer. Reading it as a list rather than as a single spec is what lets
    a further surface be admitted by appending a spec, with no change here.
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

    for spec in document["provider_discovery"]:
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


def discovered_surface_ids(document: dict) -> set[str]:
    """The provider ids that exist only because a pattern found them."""
    return {str(spec["id"]) for spec in document["provider_discovery"]}


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
    holds the reference — and stops a schema's own field values from being mistaken for
    dangling references.
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
        # A collection whose owner declares no ordinal still carries an ORDER: the order
        # the owner wrote it in, which for a declared pipeline IS the evidential order.
        # The base separates one owner's order from another's; it is declared, never
        # inferred, and it confers no priority and no authority.
        ordinal_base = adapter.get("ordinal_base")
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
            for index, (key, record) in enumerate(records):
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
                if ordinal_base is not None and "ordinal" not in attributes:
                    attributes["ordinal"] = _as_int(ordinal_base) + index
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


# ------------------------------------------------------------------------- identity


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


def relationship_objects(
    document: dict, edges: list[dict], by_cko: dict[str, dict], registry_identity: dict[str, str]
) -> list[dict]:
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
                "cko_id": kind
                + ID_SEPARATOR
                + digest("|".join([str(edge["source"]), str(edge["relation"]), str(edge["target"])]))[:32],
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

    Constitutional law: every governed entity possesses EXACTLY ONE CKO, and that object
    is its immutable constitutional identity. An entity is identified by its kind and
    its recorded identity, so two objects sharing both are two identities for one entity
    — a duplication no derived view could later reconcile.
    """
    seen: dict[tuple[str, str], list[str]] = {}
    for entry in ckos:
        seen.setdefault((entry["kind"], entry["record_id"]), []).append(entry["cko_id"])
    return sorted(f"{kind}/{record}" for (kind, record), holders in seen.items() if len(holders) > 1)


# --------------------------------------------------------------- relation resolution


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

    Each relation carries a CANDIDATE SET naming exactly one intended target. The first
    candidate that resolves to a Canonical Knowledge Object is the target, because a
    relation between governed entities is a relation between their CKOs; only if none
    resolves is a located artifact accepted, under the declared reading rules; and only
    if neither does the relation dangle.
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


def _related(
    entry: dict,
    context: dict,
    relation: str,
    kind_filter: str,
    direction: str,
) -> list[dict]:
    """Every object reachable from this one over a declared relation.

    DIRECTION is declared, because the repository's located owners each declare the same
    governed relation from their own side: a lifecycle owner names the capability that
    discharges its stage, while a capability owner names the stages it discharges. Both
    are the same relation; insisting on one direction would make one of the two owners
    unreadable and would force this engine to know which owner wrote which.
    """
    by_cko = context["by_cko"]
    out: list[dict] = []
    seen: set[str] = set()
    edges: list[tuple[dict, str]] = []
    if direction in ("outgoing", "either"):
        for edge in context["edges_by_source"].get(entry["cko_id"], []):
            edges.append((edge, "target"))
    if direction in ("incoming", "either"):
        for edge in context["incoming"].get(entry["cko_id"], []):
            edges.append((edge, "source"))
    for edge, side in edges:
        if relation and edge["relation"] != relation:
            continue
        candidates = edge["resolved"] if side == "target" else [edge["source"]]
        for candidate in candidates:
            other = by_cko.get(candidate)
            if other is None or other["cko_id"] in seen:
                continue
            if kind_filter and other["kind"] != kind_filter:
                continue
            seen.add(other["cko_id"])
            out.append(other)
    return out


def _executable_resolves(value: Any) -> bool:
    """Does a declared invocation name a program the repository actually holds?

    The invocation is a token sequence whose interpreter and flags are not paths; the
    program is whichever token resolves, so no argument convention is assumed.
    """
    for token in _strings(value):
        if exists(token):
            return True
    return False


def evaluate(rule: dict, entry: dict, context: dict) -> bool:  # noqa: C901 - one branch per declared mechanic
    kind = str(rule.get("kind") or "")

    if kind == "all_of":
        return all(evaluate(item, entry, context) for item in rule.get("rules") or [])
    if kind == "any_of":
        return any(evaluate(item, entry, context) for item in rule.get("rules") or [])
    if kind == "not_of":
        return not evaluate(rule["rule"], entry, context)
    if kind == "attribute_present":
        return bool(str(entry["attributes"].get(str(rule["attribute"]), "") or "").strip())
    if kind == "attribute_resolves":
        return exists(str(entry["attributes"].get(str(rule["attribute"]), "") or ""))
    if kind == "attribute_executable":
        return _executable_resolves(entry["attributes"].get(str(rule["attribute"])))
    if kind == "attribute_true":
        return bool(entry["attributes"].get(str(rule["attribute"])))
    if kind == "derived_true":
        return bool(context["derived"].get(entry["cko_id"], {}).get(str(rule["fact"])))
    if kind == "originated_by_class":
        return entry["provenance"]["discovery_class"] == str(rule["class"])
    if kind == "relation_to_kind":
        return bool(
            _related(
                entry,
                context,
                str(rule["relation"]),
                str(rule.get("kind_filter") or ""),
                str(rule.get("direction") or "outgoing"),
            )
        )
    if kind == "relation_targets_resolve":
        found = [
            edge
            for edge in context["edges_by_source"].get(entry["cko_id"], [])
            if edge["relation"] == str(rule["relation"])
        ]
        return bool(found) and all(edge["target_class"] != "dangling" for edge in found)
    if kind == "related_satisfies":
        # The general composition mechanic: evaluate a sub-rule on every object reached
        # over a declared relation. Every multi-hop obligation is expressed with this
        # rather than with a dedicated mechanic per shape, so a new obligation shape is
        # a declaration edit and never an engine edit.
        for other in _related(
            entry,
            context,
            str(rule.get("relation") or ""),
            str(rule.get("kind_filter") or ""),
            str(rule.get("direction") or "outgoing"),
        ):
            if evaluate(rule["rule"], other, context):
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
        # This asks whether Repository Truth puts the entity IN SCOPE for an obligation,
        # which is a different question from whether it satisfies it.
        value = str(entry["attributes"].get(str(rule["attribute"]), "") or "")
        if not value:
            return False
        return _zone(value) in context["scope_space"].get(
            (str(rule["kind_filter"]), str(rule["target_attribute"])), frozenset()
        )
    if kind == "edge_participation":
        relation = str(rule.get("relation") or "")
        outgoing = [
            e for e in context["edges_by_source"].get(entry["cko_id"], []) if not relation or e["relation"] == relation
        ]
        incoming = [
            e for e in context["incoming"].get(entry["cko_id"], []) if not relation or e["relation"] == relation
        ]
        return bool(outgoing or incoming)
    if kind == "admission_path_open":
        return context["admission_open"]
    if kind == "obligation_satisfied":
        return bool(context["obligation_state"].get(entry["cko_id"], {}).get(str(rule["obligation"])))
    raise FailClosed(f"a declared rule names a mechanic that does not exist: {kind!r}")


# ------------------------------------------------------------------------- ordering


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def topological(nodes: list[dict], edges_by_source: dict[str, list[dict]], relation: str) -> tuple[list[str], list[str]]:
    """Order the consumed graph. Cycles are reported, never broken silently."""
    ids = [entry["cko_id"] for entry in nodes]
    present = set(ids)
    ordinal = {entry["cko_id"]: _as_int(entry["attributes"].get("ordinal")) for entry in nodes}
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


# -------------------------------------------------------------------------- planning


def plan(goal: str, subject: str, order: list[str], by_cko: dict[str, dict], stage_graph_digest: str) -> dict:
    """Derive the complete engineering plan for a goal over the consumed lifecycle.

    This resolves and records. It invokes no capability and re-runs no owner: the
    located owners of the execution surfaces are already executed by the fixed-point
    pipeline, and invoking them here would make this engine observe a run of itself.

    Every step is measured for whether it is discharged by an ALREADY LOCATED owner. A
    step that is not is a step that would require new engineering infrastructure, and the
    count of those is the whole reduction claim: if it is zero for every goal, then the
    marginal engineering infrastructure an additional goal requires is nothing.
    """
    steps: list[dict] = []
    for position, cko_id in enumerate(order, start=1):
        entry = by_cko[cko_id]
        owner = str(entry["attributes"].get("owner", "") or "")
        authority_owner = str(entry["attributes"].get("authority_owner", "") or "")
        owner_located = exists(owner)
        authority_located = exists(authority_owner)
        reused = owner_located and not owner.startswith(OWN_PREFIX)
        steps.append(
            {
                "position": position,
                "stage_id": entry["record_id"],
                "stage": entry["name"],
                "group": str(entry["attributes"].get("group", "") or ""),
                "owner": owner,
                "owner_located": owner_located,
                "authority_owner": authority_owner,
                "authority_located": authority_located,
                "bound": bool(owner_located and authority_located),
                "reused": reused,
                "new_infrastructure_required": not owner_located,
            }
        )
    goal_digest = digest(goal)
    record = {
        "goal": goal,
        "goal_digest": goal_digest,
        "subject": subject,
        "subject_located": exists(subject),
        "stage_graph_digest": stage_graph_digest,
        "steps": steps,
        "steps_total": len(steps),
        "steps_bound": sum(1 for step in steps if step["bound"]),
        "steps_unbound": sum(1 for step in steps if not step["bound"]),
        "steps_reused": sum(1 for step in steps if step["reused"]),
        "steps_requiring_new_infrastructure": sum(1 for step in steps if step["new_infrastructure_required"]),
    }
    record["plan_id"] = digest(canonical({"goal_digest": goal_digest, "stage_graph_digest": stage_graph_digest}))
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


def anchor_present(relative: str, anchor: str) -> bool:
    """Is the declared anchor actually present inside its owner?

    An owner that does not contain the anchor cited against it does not evidence the
    obligation, and reporting it as owned would be an assumption. An empty anchor means
    the whole document is the anchor, which is only true when the document resolves.
    """
    if not anchor:
        return exists(relative)
    raw = read_text(relative)
    if raw is None:
        return False
    return anchor in raw


def _plane_kinds(document: dict) -> tuple[str, str, str]:
    """The three measured planes, identified by what each says it is MEASURED BY.

    Identified by the measurement each plane carries rather than by its name, so
    renaming a plane in the declaration cannot silently change which objects are held to
    which obligations.
    """
    obligations = properties = traversal = ""
    for entry in document["planes"]:
        measured = str(entry.get("measured_by", "")).lower()
        if measured == MEASURED_BY_OBLIGATIONS:
            obligations = str(entry["kind"])
        elif measured == MEASURED_BY_PROPERTIES:
            properties = str(entry["kind"])
        elif measured == MEASURED_BY_TRAVERSAL:
            traversal = str(entry["kind"])
    if not (obligations and properties and traversal):
        raise FailClosed("the plane registry does not declare all three measured planes")
    return obligations, properties, traversal


def _plane_id(document: dict, measured_by: str) -> str:
    """The declared identifier of the plane carrying a given measurement."""
    for entry in document["planes"]:
        if str(entry.get("measured_by", "")).lower() == measured_by:
            return str(entry["id"])
    raise FailClosed(f"no plane declares the measurement {measured_by!r}")


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


def _reentry_like(relation: str, document: dict) -> bool:
    """Is this declared relation the non-terminality relation?

    Decided by the relation's own declared note rather than by its name, so renaming it
    in the registry does not silently disable the non-terminality measurement.
    """
    for entry in document["cko_model"]["relation_types"]:
        if str(entry["relation"]) != relation:
            continue
        return "non-terminal" in str(entry.get("note", "")).lower()
    return False


def _registry_adapter(document: dict) -> str:
    """The declared adapter whose objects carry registered constitutional identity."""
    return str(document["relationship_model"].get("target_identity_adapter") or "")


def _measure_value(source: str, pointer: str) -> tuple[bool, int]:
    """Read a declared counter out of a located artifact.

    The artifact is read through the registered reader table, so a measure may live in
    any serialization the repository has taught the engine to read. A pointer that does
    not resolve reports NOT LOCATED rather than zero: a missing measure is an unmeasured
    obligation, and zero would read as a satisfied one.
    """
    if not exists(source):
        return False, 0
    payload = _read_json(source) if source.endswith(".json") else None
    if payload is None:
        return False, 0
    found = follow(payload, pointer)
    if isinstance(found, bool):
        return True, int(found)
    if isinstance(found, (int, float)):
        return True, int(found)
    if isinstance(found, (list, dict)):
        return True, len(found)
    return False, 0


def dispose(document: dict, plane: str, facts: dict) -> tuple[str, str, str]:
    """Resolve a subject to exactly one located disposition, from measured facts only.

    Ordered rules, first match wins, and the final rule for each plane must be total so
    that no subject can escape disposition. CREATE is reachable only through a rule whose
    facts say no canonical owner was located — which is the constitutional test, not a
    preference.
    """
    for rule in document["disposition_rules"]:
        if str(rule.get("plane") or "") != plane:
            continue
        when = rule.get("when") or {}
        if all(bool(facts.get(str(name))) == bool(value) for name, value in when.items()):
            return str(rule["disposition"]), str(rule["id"]), str(rule.get("rationale") or "")
    raise FailClosed(f"no disposition rule matched a subject on plane {plane!r}: dispositions must be total")



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

    goal_kind, invariant_kind, stage_kind = _plane_kinds(document)
    always, conditional, never = _applicability_tokens(document)
    surfaces = discovered_surface_ids(document)

    # The registered constitutional identity of a located artifact, from the declared
    # registry adapter. A derived view never supplies identity; the registry does.
    registry_adapter = _registry_adapter(document)
    registry_identity: dict[str, str] = {}
    for entry in ckos:
        if entry["provenance"]["adapter"] != registry_adapter:
            continue
        located = str(entry["attributes"].get("path", "") or "")
        if located:
            registry_identity[located] = entry["semantic_id"]

    relationships = relationship_objects(document, edges, by_cko, registry_identity)

    # Value spaces, so an obligation may ask whether a value or a zone is covered by the
    # objects of another kind without naming any of them.
    attribute_space: dict[tuple[str, str], set[str]] = {}
    scope_space: dict[tuple[str, str], set[str]] = {}
    for entry in ckos:
        for attribute, value in entry["attributes"].items():
            for text in _strings(value):
                attribute_space.setdefault((entry["kind"], attribute), set()).add(text)
                scope_space.setdefault((entry["kind"], attribute), set()).add(_zone(text))

    # Admission paths are EVIDENCE probes: they confirm a registrar exists, and originate
    # nothing. An axis with no resolving registrar is an axis with a hidden bound.
    admission_paths = []
    for entry in document["admission_paths"]:
        owner = str(entry["owner"])
        symbol = str(entry["symbol"])
        admission_paths.append(
            {
                "id": str(entry["id"]),
                "owner": owner,
                "symbol": symbol,
                "kind": str(entry.get("kind", "")),
                "discovery_class": str(entry.get("discovery_class", "")),
                "located": exists(owner),
                "resolves": symbol_present(owner, symbol),
            }
        )
    admission_by_id = {entry["id"]: entry for entry in admission_paths}
    admission_open = all(entry["resolves"] for entry in admission_paths)

    # ---- the lifecycle plane is CONSUMED, never re-derived
    stages = [entry for entry in ckos if entry["kind"] == stage_kind]
    stage_relations = {
        edge["relation"]
        for edge in edges
        if (by_cko.get(edge["source"]) or {}).get("kind") == stage_kind
    }
    graph_relations: set[str] = set()
    for gtype in document["graph_types"]["types"]:
        if stage_kind in [str(k) for k in gtype["node_kinds"]]:
            graph_relations |= {str(r) for r in gtype["edge_relations"]}
    dependency_candidates = sorted(
        relation
        for relation in stage_relations & graph_relations
        if not _reentry_like(relation, document)
    )
    dependency_relation = dependency_candidates[0] if dependency_candidates else ""
    order, cycles = topological(stages, edges_by_source, dependency_relation)
    stage_graph_digest = digest(
        canonical(
            [
                {
                    "stage": entry["record_id"],
                    "owner": str(entry["attributes"].get("owner", "") or ""),
                    "position": order.index(entry["cko_id"]) if entry["cko_id"] in order else -1,
                }
                for entry in sorted(stages, key=lambda item: item["cko_id"])
            ]
        )
    )
    reentry_declarations = sum(
        1 for edge in edges if _reentry_like(edge["relation"], document) and edge["target_class"] != "dangling"
    )

    # ---- derived facts: structural pass
    readable_extensions: set[str] = set()
    for entry in document["serializations"]:
        if entry.get("registered"):
            readable_extensions |= {str(ext) for ext in entry.get("extensions") or []}

    derived: dict[str, dict[str, Any]] = {}
    goals = [entry for entry in ckos if entry["kind"] == goal_kind]
    invariants = [entry for entry in ckos if entry["kind"] == invariant_kind]

    plans: dict[str, dict] = {}
    plan_stability: dict[str, bool] = {}
    for entry in goals:
        subject = str(entry["attributes"].get("subject", "") or "")
        first = plan(entry["name"], subject, order, by_cko, stage_graph_digest)
        second = plan(entry["name"], subject, order, by_cko, stage_graph_digest)
        plan_stability[entry["cko_id"]] = canonical(first) == canonical(second)
        plans[entry["cko_id"]] = first
        owner = str(entry["attributes"].get("owner", "") or "")
        derived[entry["cko_id"]] = {
            "subject_present": bool(subject),
            "subject_located": exists(subject),
            "owner_located": exists(owner),
            "authority_located": exists(str(entry["attributes"].get("authority_owner", "") or "")),
            "plan_complete": bool(first["steps_total"]) and first["steps_unbound"] == 0,
            "plan_deterministic": plan_stability[entry["cko_id"]],
            "requires_new_infrastructure": first["steps_requiring_new_infrastructure"] > 0,
            "subject_is_self": subject.startswith(OWN_PREFIX),
            "fully_reused": bool(first["steps_total"]) and first["steps_reused"] == first["steps_total"],
        }

    for entry in invariants:
        owner = str(entry["attributes"].get("owner", "") or "")
        anchor = str(entry["attributes"].get("anchor", "") or "")
        source = str(entry["attributes"].get("measure_source", "") or "")
        pointer = str(entry["attributes"].get("measure", "") or "")
        comparator = str(entry["attributes"].get("comparator", "") or "")
        expect = _as_int(entry["attributes"].get("expect"))
        located, value = _measure_value(source, pointer) if (source and pointer) else (False, 0)
        derived[entry["cko_id"]] = {
            "owner_located": exists(owner),
            "anchor_present": anchor_present(owner, anchor),
            "machine_readable": any(owner.endswith(ext) for ext in readable_extensions),
            "measure_declared": bool(source and pointer and comparator),
            "measure_located": located,
            "measure_met": bool(located and comparator and compare(value, comparator, expect)),
            "outside_own_home": bool(owner) and not owner.startswith(OWN_PREFIX),
            "measure_value": value,
        }

    context = {
        "edges_by_source": edges_by_source,
        "incoming": incoming,
        "by_cko": by_cko,
        "attribute_space": {key: frozenset(value) for key, value in attribute_space.items()},
        "scope_space": {key: frozenset(value) for key, value in scope_space.items()},
        "admission_open": admission_open,
        "obligation_state": {},
        "derived": derived,
    }

    # ---- obligations over the goal plane
    obligation_state: dict[str, dict[str, bool]] = {}
    obligation_applicability: dict[str, dict[str, str]] = {}
    context["obligation_state"] = obligation_state
    for entry in goals:
        obligation_state[entry["cko_id"]] = {}
        obligation_applicability[entry["cko_id"]] = {}
        for rule in document["obligation_rules"]:
            applicability = str(rule["applicability"])
            if applicability not in (always, conditional, never):
                raise FailClosed(f"an obligation declares an unregistered applicability: {applicability!r}")
            resolved = applicability
            if applicability == conditional:
                condition = rule.get("condition")
                if condition is None:
                    raise FailClosed(f"a conditional obligation declares no condition: {rule['id']}")
                resolved = always if evaluate(condition, entry, context) else never
            obligation_applicability[entry["cko_id"]][str(rule["id"])] = resolved
            if resolved == never:
                obligation_state[entry["cko_id"]][str(rule["id"])] = True
                continue
            obligation_state[entry["cko_id"]][str(rule["id"])] = evaluate(rule, entry, context)

    # ---- properties over the invariant plane
    property_state: dict[str, dict[str, bool]] = {}
    for entry in invariants:
        property_state[entry["cko_id"]] = {
            str(rule["id"]): evaluate(rule, entry, context) for rule in document["property_rules"]
        }

    # ---- disposition: derived from measured facts, never asserted
    disposition_values = {entry["record_id"] for entry in ckos if entry["kind"] == str(document["cko_model"]["disposition_kind"])}
    goal_records: list[dict] = []
    for entry in sorted(goals, key=lambda item: (_as_int(item["attributes"].get("ordinal")), item["cko_id"])):
        facts = dict(derived[entry["cko_id"]])
        applicable = {
            name: value
            for name, value in obligation_state[entry["cko_id"]].items()
            if obligation_applicability[entry["cko_id"]][name] != never
        }
        facts["obligations_unmet"] = not all(applicable.values())
        disposition, rule_id, rationale = dispose(document, _plane_id(document, MEASURED_BY_OBLIGATIONS), facts)
        plan_record = plans[entry["cko_id"]]
        goal_records.append(
            {
                "cko_id": entry["cko_id"],
                "record_id": entry["record_id"],
                "goal": entry["name"],
                "intent": str(entry["attributes"].get("intent", "") or ""),
                "subject": plan_record["subject"],
                "subject_located": plan_record["subject_located"],
                "owner": str(entry["attributes"].get("owner", "") or ""),
                "authority": str(entry["attributes"].get("authority", "") or ""),
                "authority_owner": str(entry["attributes"].get("authority_owner", "") or ""),
                "ordinal": _as_int(entry["attributes"].get("ordinal")),
                "obligations": obligation_state[entry["cko_id"]],
                "applicability": obligation_applicability[entry["cko_id"]],
                "disposition": disposition,
                "disposition_rule": rule_id,
                "disposition_rationale": rationale,
                "disposition_located": disposition in disposition_values,
                "plan": plan_record,
                "plan_deterministic": plan_stability[entry["cko_id"]],
                "provenance": entry["provenance"],
                "facts": facts,
            }
        )

    invariant_records: list[dict] = []
    for entry in sorted(invariants, key=lambda item: (_as_int(item["attributes"].get("ordinal")), item["cko_id"])):
        facts = dict(derived[entry["cko_id"]])
        facts["properties_unmet"] = not all(property_state[entry["cko_id"]].values())
        disposition, rule_id, rationale = dispose(document, _plane_id(document, MEASURED_BY_PROPERTIES), facts)
        invariant_records.append(
            {
                "cko_id": entry["cko_id"],
                "record_id": entry["record_id"],
                "invariant": entry["name"],
                "owner": str(entry["attributes"].get("owner", "") or ""),
                "anchor": str(entry["attributes"].get("anchor", "") or ""),
                "measure_source": str(entry["attributes"].get("measure_source", "") or ""),
                "measure": str(entry["attributes"].get("measure", "") or ""),
                "comparator": str(entry["attributes"].get("comparator", "") or ""),
                "expect": _as_int(entry["attributes"].get("expect")),
                "measure_value": facts["measure_value"],
                "ordinal": _as_int(entry["attributes"].get("ordinal")),
                "properties": property_state[entry["cko_id"]],
                "disposition": disposition,
                "disposition_rule": rule_id,
                "disposition_rationale": rationale,
                "disposition_located": disposition in disposition_values,
                "provenance": entry["provenance"],
                "facts": facts,
            }
        )

    stage_records: list[dict] = []
    position = {cko_id: index + 1 for index, cko_id in enumerate(order)}
    # A lifecycle capability is EXPLICITLY MEASURED when a completion invariant cites the
    # located lifecycle owner at that stage's own name as its anchor. Comparing two
    # DISCOVERED values — an invariant's anchor against a stage's name — is what lets
    # coverage be derived without either being named here.
    lifecycle_owner = str(document["programme"]["lifecycle_owner"])
    measured_anchors = {
        str(record["anchor"]) for record in invariant_records if str(record["owner"]) == lifecycle_owner
    }
    stage_plane = _plane_id(document, MEASURED_BY_TRAVERSAL)
    for entry in sorted(stages, key=lambda item: (position.get(item["cko_id"], 0), item["cko_id"])):
        owner = str(entry["attributes"].get("owner", "") or "")
        authority_owner = str(entry["attributes"].get("authority_owner", "") or "")
        facts = {
            "owner_located": exists(owner),
            "authority_located": exists(authority_owner),
            "invariant_measured": entry["name"] in measured_anchors,
            "traversed": bool(position.get(entry["cko_id"], 0)),
        }
        disposition, rule_id, rationale = dispose(document, stage_plane, facts)
        stage_records.append(
            {
                "cko_id": entry["cko_id"],
                "record_id": entry["record_id"],
                "stage": entry["name"],
                "group": str(entry["attributes"].get("group", "") or ""),
                "owner": owner,
                "owner_located": facts["owner_located"],
                "authority_owner": authority_owner,
                "position": position.get(entry["cko_id"], 0),
                "consumed_from": entry["provenance"]["provider_owner"],
                "facts": facts,
                "disposition": disposition,
                "disposition_rule": rule_id,
                "disposition_rationale": rationale,
                "disposition_located": disposition in disposition_values,
            }
        )

    # ---- graphs composed from entity and relationship objects
    graphs = []
    for gtype in document["graph_types"]["types"]:
        node_kinds = {str(k) for k in gtype["node_kinds"]}
        relation_types = {str(r) for r in gtype["edge_relations"]}
        nodes = [entry["cko_id"] for entry in ckos if entry["kind"] in node_kinds]
        node_set = set(nodes)
        composed = [
            edge
            for edge in edges
            if edge["relation"] in relation_types
            and edge["source"] in node_set
            and any(target in node_set for target in edge["resolved"])
        ]
        graphs.append(
            {
                "id": str(gtype["id"]),
                "graph": str(gtype["graph"]),
                "node_kinds": sorted(node_kinds),
                "edge_relations": sorted(relation_types),
                "nodes": len(nodes),
                "edges": len(composed),
                "composed": bool(nodes),
            }
        )

    # ---- expansion axes
    expansion_axes = []
    for entry in document["expansion_axes"]:
        path = admission_by_id.get(str(entry["admission_path"]))
        expansion_axes.append(
            {
                "id": str(entry["id"]),
                "axis": str(entry["axis"]),
                "clause": str(entry.get("clause", "")),
                "admission_path": str(entry["admission_path"]),
                "registrar": str(path["owner"]) if path else "",
                "blocking": bool(entry.get("blocking", True)),
                "bound": bool(path and path["resolves"]),
            }
        )

    # ---- engineering authorities: crosswalked, never merged
    authorities = []
    for entry in document["engineering_authorities"]:
        owner = str(entry["owner"])
        anchor = str(entry.get("anchor", ""))
        authorities.append(
            {
                "id": str(entry["id"]),
                "name": str(entry["name"]),
                "owner": owner,
                "anchor": anchor,
                "role": str(entry.get("role", "")),
                "merge_prohibited": bool(entry.get("merge_prohibited", True)),
                "located": exists(owner),
                "anchor_present": anchor_present(owner, anchor),
                "claimed_here": owner.startswith(OWN_PREFIX),
            }
        )

    # ---- reduction: the marginal engineering an additional goal requires
    reduction = []
    for entry in document["reduction_measures"]:
        measure_name = str(entry["measure"])
        value = 0
        if measure_name == "goal_steps_requiring_new_infrastructure":
            value = sum(record["plan"]["steps_requiring_new_infrastructure"] for record in goal_records)
        elif measure_name == "goal_plan_steps_unbound":
            value = sum(record["plan"]["steps_unbound"] for record in goal_records)
        elif measure_name == "goals_not_fully_reused":
            value = sum(1 for record in goal_records if not record["facts"]["fully_reused"])
        elif measure_name == "invariants_dispositioned_create":
            value = sum(1 for record in invariant_records if record["disposition_rule"].endswith(ACTION_CREATE))
        elif measure_name == "invariants_without_located_owner":
            value = sum(1 for record in invariant_records if not record["facts"]["owner_located"])
        elif measure_name == "capabilities_created":
            value = sum(1 for entry_ in document["capabilities"] if str(entry_["action"]) == ACTION_CREATE)
        else:
            raise FailClosed(f"a reduction measure names a counter that does not exist: {measure_name!r}")
        reduction.append(
            {
                "id": str(entry["id"]),
                "reduction": str(entry["reduction"]),
                "measure": measure_name,
                "comparator": str(entry["comparator"]),
                "expect": _as_int(entry["expect"]),
                "value": value,
                "owner": str(entry["owner"]),
                "located": exists(str(entry["owner"])),
                "achieved": compare(value, str(entry["comparator"]), _as_int(entry["expect"])),
                "statement": str(entry.get("statement", "")),
            }
        )

    # ---- knowledge extraction and capability elevation
    extraction_counters = {
        "goals_discovered": len(goal_records),
        "invariants_discovered": len(invariant_records),
        "stages_consumed": len(stage_records),
        "ckos_discovered": len(ckos),
        "relationship_ckos_discovered": len(relationships),
        "plans_derived": len(plans),
        "dispositions_discovered": len(disposition_values),
        "authorities_crosswalked": len(authorities),
    }
    extractions = []
    for rule in document["knowledge_extraction"]["rules"]:
        measure_name = str(rule["measure"])
        if measure_name not in extraction_counters:
            raise FailClosed(f"a knowledge extraction rule names a counter that does not exist: {measure_name!r}")
        extractions.append(
            {
                "id": str(rule["id"]),
                "knowledge": str(rule["knowledge"]),
                "measure": measure_name,
                "value": extraction_counters[measure_name],
                "reusable_as": str(rule["reusable_as"]),
                "measured": extraction_counters[measure_name] > 0,
            }
        )

    elevations = []
    for entry in document["elevation_measures"]:
        measure_name = str(entry["measure"])
        if measure_name not in extraction_counters:
            raise FailClosed(f"an elevation measure names a counter that does not exist: {measure_name!r}")
        facets = {
            facet: str(entry.get(facet, ""))
            for facet in ("evidence_owner", "lineage_owner", "replay_owner", "certification_owner", "authority_owner")
        }
        elevations.append(
            {
                "id": str(entry["id"]),
                "increase": str(entry["increase"]),
                "measure": measure_name,
                "value": extraction_counters[measure_name],
                "statement": str(entry.get("statement", "")),
                "facets": facets,
                "evidenced": bool(extraction_counters[measure_name]) and all(exists(path) for path in facets.values()),
            }
        )

    self_evolution = []
    for entry in document["self_evolution_path"]:
        owner = str(entry["owner"])
        anchor = str(entry.get("anchor", ""))
        self_evolution.append(
            {
                "id": str(entry["id"]),
                "step": str(entry["step"]),
                "owner": owner,
                "anchor": anchor,
                "located": exists(owner),
                "anchor_present": anchor_present(owner, anchor),
                "owned_externally": not owner.startswith(OWN_PREFIX),
            }
        )

    # ---- semantic identity
    identity_inputs = [str(name) for name in document["semantic_identity"]["inputs"]]
    excluded_inputs = [str(name) for name in document["semantic_identity"]["excluded_inputs"]]
    all_objects = ckos + relationships
    without_identity = sorted(entry["cko_id"] for entry in all_objects if not entry.get("semantic_id"))
    mutable_inputs = sorted(name for name in identity_inputs if name in excluded_inputs)
    determinate = [entry for entry in relationships if entry.get("target_identified")]
    semantic_seen: dict[str, list[str]] = {}
    for entry in ckos + determinate:
        semantic_seen.setdefault(entry["semantic_id"], []).append(entry["cko_id"])
    semantic_collisions = sorted(key for key, holders in semantic_seen.items() if len(holders) > 1)

    # ---- write scope and record immutability
    write_set = sorted(OWN_PREFIX + name for name in PAGES) + [OWN_PREFIX + MODEL.name]
    record_set = [
        {
            "id": str(entry["id"]),
            "owner": str(entry["owner"]),
            "anchor": str(entry.get("anchor", "")),
            "law": str(entry.get("law", "")),
            "located": exists(str(entry["owner"])),
            "anchor_present": anchor_present(str(entry["owner"]), str(entry.get("anchor", ""))),
        }
        for entry in document["record_set"]["records"]
    ]
    protected = {entry["owner"] for entry in record_set}
    forbidden = [str(prefix) for prefix in document["programme"]["forbidden_write_prefixes"]]
    immutability = {
        "write_set": write_set,
        "intersections": sorted(protected & set(write_set)),
        "outside_home": sorted(path for path in write_set if not path.startswith(OWN_PREFIX)),
        "forbidden_trespass": sorted(
            path for path in write_set for prefix in forbidden if path.startswith(prefix)
        ),
    }
    immutability["disjoint"] = not immutability["intersections"]

    # ---- unboundedness and hygiene
    unbounded_owner = str(document["unboundedness"]["owner"])
    unbounded_text = read_text(unbounded_owner) or ""
    terminal_hits = sorted(
        {
            str(token)
            for token in document["unboundedness"]["terminal_tokens"]
            if str(token) in unbounded_text
            and not any(str(marker) in unbounded_text for marker in document["unboundedness"]["negation_markers"])
        }
    )
    own_source = Path(__file__).read_text(encoding="utf-8")
    manifest_text = "".join(
        sorted(read_text(provider["owner"]) or "" for provider in providers if provider["discovered"])
    )
    declaration_text = DECLARATION.read_text(encoding="utf-8")
    bound_hits = sorted(
        {
            str(token)
            for token in document["hygiene"]["limit_tokens"]
            if str(token) in own_source or str(token) in manifest_text
        }
    )

    graph_digest = digest(
        canonical(
            [
                {
                    "cko_id": entry["cko_id"],
                    "kind": entry["kind"],
                    "relations": sorted(canonical(relation) for relation in entry["relations"]),
                }
                for entry in sorted(ckos, key=lambda item: item["cko_id"])
            ]
        )
    )

    counters = {
        "ckos_discovered": len(ckos),
        "relations_discovered": len(edges),
        "relationship_ckos_discovered": len(relationships),
        "relationships_without_target_identity": sum(1 for entry in relationships if not entry["target_identified"]),
        "goals_discovered": len(goal_records),
        "goals_without_located_subject": sum(1 for record in goal_records if not record["subject_located"]),
        "goal_plans_derived": len(plans),
        "goal_plans_nondeterministic": sum(1 for record in goal_records if not record["plan_deterministic"]),
        "goal_plan_steps_unbound": sum(record["plan"]["steps_unbound"] for record in goal_records),
        "goal_steps_requiring_new_infrastructure": sum(
            record["plan"]["steps_requiring_new_infrastructure"] for record in goal_records
        ),
        "goal_obligation_failures": sum(
            1
            for record in goal_records
            for name, value in record["obligations"].items()
            if not value and record["applicability"][name] != never
        ),
        "goals_dispositioned_create": sum(
            1 for record in goal_records if record["disposition_rule"].endswith(ACTION_CREATE)
        ),
        "goals_without_located_disposition": sum(1 for record in goal_records if not record["disposition_located"]),
        "goals_self_subject": sum(1 for record in goal_records if record["facts"]["subject_is_self"]),
        "goals_not_fully_reused": sum(1 for record in goal_records if not record["facts"]["fully_reused"]),
        "invariants_discovered": len(invariant_records),
        "invariants_without_located_owner": sum(
            1 for record in invariant_records if not record["facts"]["owner_located"]
        ),
        "invariants_without_anchor": sum(1 for record in invariant_records if not record["facts"]["anchor_present"]),
        "invariants_unmeasured": sum(1 for record in invariant_records if not record["facts"]["measure_located"]),
        "invariants_unsatisfied": sum(1 for record in invariant_records if not record["facts"]["measure_met"]),
        "invariants_dispositioned_create": sum(
            1 for record in invariant_records if record["disposition_rule"].endswith(ACTION_CREATE)
        ),
        "invariant_property_failures": sum(
            1 for record in invariant_records for value in record["properties"].values() if not value
        ),
        "invariants_owned_here": sum(1 for record in invariant_records if not record["facts"]["outside_own_home"]),
        "stages_consumed": len(stage_records),
        "stages_unowned": sum(1 for record in stage_records if not record["owner_located"]),
        "stages_unauthorized": sum(1 for record in stage_records if not record["facts"]["authority_located"]),
        "stages_not_traversed": sum(1 for record in stage_records if not record["facts"]["traversed"]),
        "stages_invariant_measured": sum(1 for record in stage_records if record["facts"]["invariant_measured"]),
        "stages_dispositioned_create": sum(
            1 for record in stage_records if record["disposition_rule"].endswith(ACTION_CREATE)
        ),
        "stages_undispositioned": sum(1 for record in stage_records if not record["disposition"]),
        "stages_without_located_disposition": sum(1 for record in stage_records if not record["disposition_located"]),
        # The coverage identity: every consumed capability falls in exactly one disposition
        # bucket, so the total must balance. A non-zero reading here means a capability
        # escaped disposition, which no totality rule should permit.
        "stage_coverage_imbalance": abs(
            len(stage_records)
            - len({record["cko_id"] for record in stage_records if record["disposition"]})
        ),
        "stages_originated_here": sum(1 for record in stage_records if record["consumed_from"].startswith(OWN_PREFIX)),
        "graph_cycles": len(cycles),
        "dangling_relations": sum(1 for edge in edges if edge["target_class"] == "dangling"),
        "reentry_declarations_absent": 0 if reentry_declarations else 1,
        "providers_unlocated": sum(1 for provider in providers if not provider["located"]),
        "providers_without_reader": sum(
            1 for provider in providers if reader_for(document, provider["serialization"]) is None
        ),
        "providers_not_open": sum(
            1 for provider in providers if provider["discovered"] and not provider["open"]
        ),
        "adapters_unresolved": sum(1 for report in adapter_reports if not report["resolved"]),
        "serialization_readers_registered": sum(1 for entry in document["serializations"] if entry.get("registered")),
        "serializations_unregistered": sum(1 for entry in document["serializations"] if not entry.get("registered")),
        "serializations_exercised": len(
            {provider["serialization"] for provider in providers if provider["located"]}
        ),
        "graph_types_empty": sum(1 for entry in graphs if not entry["composed"]),
        "expansion_axes_unbound": sum(1 for entry in expansion_axes if not entry["bound"]),
        "admission_paths_unresolved": sum(1 for entry in admission_paths if not entry["resolves"]),
        "authorities_unresolved": sum(1 for entry in authorities if not entry["located"] or not entry["anchor_present"]),
        "parallel_authority_claims": sum(1 for entry in authorities if entry["claimed_here"]),
        "authority_claims": 0 if str(document["programme"]["authority"]).startswith("NONE") else 1,
        "self_evolution_steps_unbound": sum(
            1 for entry in self_evolution if not entry["located"] or not entry["anchor_present"]
        ),
        "self_evolution_steps_owned_here": sum(1 for entry in self_evolution if not entry["owned_externally"]),
        "reductions_unachieved": sum(1 for entry in reduction if not entry["achieved"]),
        "reduction_owners_unresolved": sum(1 for entry in reduction if not entry["located"]),
        "extractions_unmeasured": sum(1 for entry in extractions if not entry["measured"]),
        "elevations_unevidenced": sum(1 for entry in elevations if not entry["evidenced"]),
        "capabilities_created": sum(1 for entry in document["capabilities"] if str(entry["action"]) == ACTION_CREATE),
        "capabilities_unowned": sum(1 for entry in document["capabilities"] if not exists(str(entry["owner"]))),
        "evidence_originated_ckos": sum(
            1
            for entry in ckos
            if not next(
                (
                    bool(cls.get(CLASS_MAY_ORIGINATE))
                    for cls in document["discovery_classes"]
                    if str(cls["id"]) == entry["provenance"]["discovery_class"]
                ),
                False,
            )
        ),
        "derived_artifacts_used_as_truth": sum(
            1 for provider in providers if provider["owner"].startswith(OWN_PREFIX) and not provider["discovered"]
        ),
        "cko_identity_collisions": len(identity_collisions(ckos)),
        "ckos_without_semantic_identity": len(without_identity),
        "semantic_identity_collisions": len(semantic_collisions),
        "identities_on_mutable_input": len(mutable_inputs),
        "ckos_of_unknown_kind": sum(
            1 for entry in ckos if entry["kind"] not in {str(k["kind"]) for k in document["cko_model"]["kinds"]}
        ),
        "closed_enumerations_declared": sum(
            1
            for flag in (
                document["cko_model"].get("closed_enumeration"),
                document["graph_types"].get("closed_enumeration"),
            )
            if flag
        ),
        "record_write_intersections": len(immutability["intersections"]),
        "terminal_state_claims": len(terminal_hits),
        "limit_tokens_present": len(bound_hits),
        "declaration_names_a_goal": sum(1 for record in goal_records if record["record_id"] in declaration_text),
        "declaration_names_an_invariant": sum(
            1 for record in invariant_records if record["record_id"] in declaration_text
        ),
        "discovered_surfaces": len(surfaces),
        # A privileged path would have to be written down: a branch that recognises this
        # programme's own home would need that home as an executable literal. The home is
        # derived from __file__ instead, so a non-zero count here is a real privilege.
        "privileged_branches": len(
            sorted(
                literal
                for literal in _executable_literals()
                if str(document["programme"]["operational_home"]) in literal
            )
        ),
    }
    for entry in document["derived_counters"]:
        name = str(entry["id"])
        adapter_id = str(entry["adapter"])
        counters[name] = sum(1 for cko in ckos if cko["provenance"]["adapter"] == adapter_id)

    # Bound slack is itself measurable, so it is derived BEFORE the dimensions are
    # recorded: a declared bound that exceeds its measured value is slack a future
    # regression could hide in, and that must be a dimension like any other.
    counters["bounds_slack"] = 0
    for entry in document["validations"]:
        measure_name = str(entry["measure"])
        if measure_name not in counters:
            raise FailClosed(f"a validation names a measure that does not exist: {measure_name!r}")
        if str(entry["comparator"]) == "<=" and counters[measure_name] < _as_int(entry["expect"]):
            counters["bounds_slack"] += 1

    validations = []
    bounds_slack: list[str] = []
    for entry in document["validations"]:
        measure_name = str(entry["measure"])
        if measure_name not in counters:
            raise FailClosed(f"a validation names a measure that does not exist: {measure_name!r}")
        value = counters[measure_name]
        comparator = str(entry["comparator"])
        expect = _as_int(entry["expect"])
        satisfied = compare(value, comparator, expect)
        if comparator == "<=" and value < expect:
            bounds_slack.append(f"{entry['id']}: bound {expect} exceeds the measured {value}")
        validations.append(
            {
                "id": str(entry["id"]),
                "dimension": str(entry["dimension"]),
                "measure": measure_name,
                "comparator": comparator,
                "expect": expect,
                "value": value,
                "blocking": bool(entry.get("blocking", True)),
                "satisfied": satisfied,
                "bound_finding": str(entry.get("bound_finding", "")),
            }
        )

    blocking_failures = [entry["id"] for entry in validations if entry["blocking"] and not entry["satisfied"]]
    gate = "OPEN" if not blocking_failures else "CLOSED"

    exit_dimensions = []
    for entry in document["exit_dimensions"]:
        measure_name = str(entry["measure"])
        if measure_name not in counters:
            raise FailClosed(f"an exit dimension names a measure that does not exist: {measure_name!r}")
        owner = str(entry["owner"])
        value = counters[measure_name]
        exit_dimensions.append(
            {
                "id": str(entry["id"]),
                "dimension": str(entry["dimension"]),
                "owner": owner,
                "located": exists(owner),
                "measure": measure_name,
                "comparator": str(entry["comparator"]),
                "expect": _as_int(entry["expect"]),
                "value": value,
                "ready": bool(exists(owner) and compare(value, str(entry["comparator"]), _as_int(entry["expect"]))),
            }
        )

    model = {
        "programme": document["programme"],
        "gate": gate,
        "determination": document["determination"]["bound" if gate == "OPEN" else "open"],
        "blocking_failures": blocking_failures,
        "providers": providers,
        "adapters": adapter_reports,
        "cko_model": {
            "kinds": [str(entry["kind"]) for entry in document["cko_model"]["kinds"]],
            "relation_types": [str(entry["relation"]) for entry in document["cko_model"]["relation_types"]],
            "open": bool(document["cko_model"].get("open")),
            "admission": str(document["cko_model"].get("admission", "")),
        },
        "planes": document["planes"],
        "not_applicable_token": never,
        "serializations": document["serializations"],
        "knowledge_extraction": document["knowledge_extraction"],
        "goals": goal_records,
        "invariants": invariant_records,
        "stages": stage_records,
        "order": order,
        "cycles": cycles,
        "dependency_relation": dependency_relation,
        "goal_kind": goal_kind,
        "invariant_kind": invariant_kind,
        "stage_kind": stage_kind,
        "stage_graph_digest": stage_graph_digest,
        "relationships": relationships,
        "graphs": graphs,
        "expansion_axes": expansion_axes,
        "admission_paths": admission_paths,
        "authorities": authorities,
        "reduction": reduction,
        "extractions": extractions,
        "elevations": elevations,
        "self_evolution": self_evolution,
        "obligation_rules": document["obligation_rules"],
        "property_rules": document["property_rules"],
        "disposition_rules": document["disposition_rules"],
        "goal_contract": document["goal_contract"],
        "semantic_identity": {
            "inputs": identity_inputs,
            "excluded_inputs": excluded_inputs,
            "without_identity": without_identity,
            "mutable_inputs": mutable_inputs,
            "collisions": semantic_collisions,
        },
        "immutability": immutability,
        "record_set": record_set,
        "terminal_hits": terminal_hits,
        "bound_hits": bound_hits,
        "counters": counters,
        "validations": validations,
        "bounds_slack": sorted(bounds_slack),
        "exit_dimensions": exit_dimensions,
        "exit_criteria": document["exit_criteria"],
        "findings": document["findings"],
        "capabilities": document["capabilities"],
        "law_source": document["law_source"],
        "graph_digest": graph_digest,
    }
    model["omega_e05_complete"] = bool(gate == "OPEN" and all(entry["ready"] for entry in exit_dimensions))
    model["seal_sha256"] = digest(canonical({k: v for k, v in model.items() if k != "seal_sha256"}))
    return model



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
                    ["LIFECYCLE OWNER", code(programme["lifecycle_owner"])],
                    ["GATE", model["gate"]],
                    ["DETERMINATION", model["determination"]],
                    ["STAGE GRAPH DIGEST (sha256)", model["stage_graph_digest"]],
                    ["GRAPH DIGEST (sha256)", model["graph_digest"]],
                    ["SEAL (sha256)", model["seal_sha256"]],
                    ["GENERATED BY", "acee_engine.py — regenerated, never hand-authored"],
                ],
            ),
            "",
            f"> {programme['disclosure']}",
            "",
        ]
    )


def _obligation_cell(record: dict, name: str, never: str) -> str:
    if record["applicability"].get(name) == never:
        return "n/a"
    return tick(bool(record["obligations"].get(name)))


def render(model: dict) -> dict[str, str]:  # noqa: C901 - one page per measured concern
    pages: dict[str, str] = {}
    counters = model["counters"]
    obligations = [str(rule["id"]) for rule in model["obligation_rules"]]
    properties = [str(rule["id"]) for rule in model["property_rules"]]
    never = model["not_applicable_token"]
    serializations = {"serializations": model["serializations"]}

    # ---- 00 dashboard
    body = [front_matter(model, "Autonomous Constitutional Engineering Dashboard")]
    body.append("## Measured position\n")
    body.append(
        table(
            ["Reading", "Value"],
            [
                ["Engineering goals discovered", str(counters["goals_discovered"])],
                ["Constitutional completion invariants discovered", str(counters["invariants_discovered"])],
                ["Lifecycle stages consumed (never re-derived)", str(counters["stages_consumed"])],
                ["Lifecycle owner", code(model["programme"]["lifecycle_owner"])],
                ["Canonical Knowledge Objects discovered", str(counters["ckos_discovered"])],
                ["Relationships discovered (first-class objects)", str(counters["relationship_ckos_discovered"])],
                ["Goal plans derived", str(counters["goal_plans_derived"])],
                ["Plan steps unbound", str(counters["goal_plan_steps_unbound"])],
                ["Plan steps requiring NEW engineering infrastructure", str(counters["goal_steps_requiring_new_infrastructure"])],
                ["Goals dispositioned CREATE", str(counters["goals_dispositioned_create"])],
                ["Invariants dispositioned CREATE", str(counters["invariants_dispositioned_create"])],
                ["Invariants without a located owner", str(counters["invariants_without_located_owner"])],
                ["Invariants unsatisfied", str(counters["invariants_unsatisfied"])],
                ["Goals whose subject is this engine (no privileged path)", str(counters["goals_self_subject"])],
                ["Metadata providers", str(len(model["providers"]))],
                ["Open discovered surfaces", str(counters["discovered_surfaces"])],
                ["Metadata adapters resolved", f"{len(model['adapters']) - counters['adapters_unresolved']}/{len(model['adapters'])}"],
                ["Graph types composed", f"{len(model['graphs']) - counters['graph_types_empty']}/{len(model['graphs'])}"],
                ["Expansion axes bound", f"{len(model['expansion_axes']) - counters['expansion_axes_unbound']}/{len(model['expansion_axes'])}"],
                ["Graph cycles · dangling relations", f"{counters['graph_cycles']} · {counters['dangling_relations']}"],
                ["Parallel authority claims", str(counters["parallel_authority_claims"])],
                ["Objects originated from implementation evidence", str(counters["evidence_originated_ckos"])],
                ["Capabilities dispositioned CREATE", str(counters["capabilities_created"])],
                ["Reduction measures achieved", f"{len(model['reduction']) - counters['reductions_unachieved']}/{len(model['reduction'])}"],
                ["Record immutability (write set ∩ record set = ∅)", yes(model["immutability"]["disjoint"])],
                ["Blocking dimensions satisfied", f"{sum(1 for v in model['validations'] if v['satisfied'])}/{len(model['validations'])}"],
                ["Ω-E05 exit dimensions ready", f"{sum(1 for d in model['exit_dimensions'] if d['ready'])}/{len(model['exit_dimensions'])}"],
            ],
        )
    )
    body.append("\n## What this programme does NOT do\n")
    body.append(
        "\n".join(
            [
                "- It legislates no lifecycle and derives no second lifecycle: the stage graph is CONSUMED from its located owner.",
                "- It drives no second loop, invokes no engine and re-runs no owner.",
                "- It opens no registry, mints no identifier and declares no namespace.",
                "- It enumerates no goal, no invariant, no stage, no owner, no disposition, no graph type and no relation type.",
                "- It holds no privileged path: it appears in the goal plane as a subject like any other.",
                "- It certifies nothing and resolves nothing authoritatively.",
            ]
        )
    )
    body.append("")
    pages[PAGES[0]] = "\n".join(body) + "\n"

    # ---- 01 engineering goal register
    body = [front_matter(model, "Engineering Goal Register")]
    body.append(
        "Goals are DISCOVERED from a located manifest pattern, never listed in the declaration. "
        "Appending a goal admits it; the engine and the declaration are unchanged.\n"
    )
    body.append(
        table(
            ["#", "Goal", "Subject", "Subject located", "Canonical owner", "Owner located", "Authority owner", "Disposition"],
            [
                [
                    str(record["ordinal"]),
                    record["goal"],
                    code(record["subject"]),
                    yes(record["subject_located"]),
                    code(record["owner"]),
                    yes(exists(record["owner"])),
                    code(record["authority_owner"]),
                    record["disposition"],
                ]
                for record in model["goals"]
            ],
        )
    )
    body.append("\n## Why each goal was recorded\n")
    body.append(
        table(
            ["Goal", "Intent"],
            [[record["record_id"], record["intent"]] for record in model["goals"]],
        )
    )
    body.append("\n## Discovered surfaces\n")
    body.append(
        table(
            ["Provider", "Located owner", "Open", "Closed enumeration", "Admission"],
            [
                [
                    provider["id"],
                    code(provider["owner"]),
                    yes(bool(provider["open"])),
                    yes(bool(provider["closed_enumeration"])),
                    provider["admission"],
                ]
                for provider in model["providers"]
                if provider["discovered"]
            ],
        )
    )
    body.append("")
    pages[PAGES[1]] = "\n".join(body) + "\n"

    # ---- 02 goal obligation binding matrix
    body = [front_matter(model, "Goal Obligation Binding Matrix")]
    body.append(
        "Applicability is determined FIRST, from Repository Truth. An obligation that does not arise "
        "is reported NOT APPLICABLE rather than counted as unbound: counting it would manufacture a "
        "deficiency the repository does not have.\n"
    )
    body.append(
        table(
            ["Obligation", "Requirement", "Applicability", "Bound (in scope)", "Not applicable"],
            [
                [
                    str(rule["id"]),
                    str(rule["obligation"]),
                    str(rule["applicability"]),
                    str(
                        sum(
                            1
                            for record in model["goals"]
                            if record["applicability"][str(rule["id"])] != never
                            and record["obligations"][str(rule["id"])]
                        )
                    )
                    + "/"
                    + str(
                        sum(
                            1
                            for record in model["goals"]
                            if record["applicability"][str(rule["id"])] != never
                        )
                    ),
                    str(
                        sum(
                            1
                            for record in model["goals"]
                            if record["applicability"][str(rule["id"])] == never
                        )
                    ),
                ]
                for rule in model["obligation_rules"]
            ],
        )
    )
    body.append("\n## Per-goal binding\n")
    body.append(
        table(
            ["Goal"] + [name.replace("OBL-", "") for name in obligations],
            [
                [record["record_id"]] + [_obligation_cell(record, name, never) for name in obligations]
                for record in model["goals"]
            ],
        )
    )
    body.append("")
    pages[PAGES[2]] = "\n".join(body) + "\n"

    # ---- 03 constitutional completion invariant register
    body = [front_matter(model, "Constitutional Completion Invariant Register")]
    body.append(
        "Every invariant is MEASURED against a located owner. An invariant whose owner does not "
        "resolve, whose cited anchor is absent, or whose measure is unmet reports so, and its "
        "disposition follows from that measurement rather than from an assertion. This is the "
        "mechanical form of MEASURE → DISCOVER → PROVE → IMPLEMENT ONLY IF MISSING.\n"
    )
    body.append(
        table(
            ["#", "Invariant", "Located owner", "Anchor present", "Machine readable", "Measure", "Value", "Expect", "Met", "Disposition"],
            [
                [
                    str(record["ordinal"]),
                    record["invariant"],
                    code(record["owner"]),
                    yes(record["facts"]["anchor_present"]),
                    yes(record["facts"]["machine_readable"]),
                    code(record["measure"]),
                    str(record["measure_value"]),
                    f"{record['comparator']} {record['expect']}",
                    yes(record["facts"]["measure_met"]),
                    record["disposition"],
                ]
                for record in model["invariants"]
            ],
        )
    )
    body.append("\n## Property conformance\n")
    body.append(
        table(
            ["Property", "Requirement", "Held"],
            [
                [
                    str(rule["id"]),
                    str(rule["property"]),
                    f"{sum(1 for record in model['invariants'] if record['properties'][str(rule['id'])])}/{len(model['invariants'])}",
                ]
                for rule in model["property_rules"]
            ],
        )
    )
    body.append("")
    body.append(
        table(
            ["Invariant"] + [name.replace("PROP-", "") for name in properties],
            [
                [record["record_id"]] + [tick(bool(record["properties"][name])) for name in properties]
                for record in model["invariants"]
            ],
        )
    )
    body.append("")
    pages[PAGES[3]] = "\n".join(body) + "\n"

    # ---- 04 autonomous disposition determination
    body = [front_matter(model, "Autonomous Disposition Determination Register")]
    body.append(
        "Disposition is DERIVED from measured facts by ordered rules, and every value resolves to a "
        "disposition the repository already legislates. CREATE is reachable only through a rule whose "
        "facts say no canonical owner was located.\n"
    )
    body.append(
        table(
            ["Rule", "Plane", "When", "Disposition", "Rationale"],
            [
                [
                    str(rule["id"]),
                    str(rule["plane"]),
                    code(canonical(rule.get("when") or {})),
                    str(rule["disposition"]),
                    str(rule.get("rationale", "")),
                ]
                for rule in model["disposition_rules"]
            ],
        )
    )
    body.append("\n## Goal dispositions\n")
    body.append(
        table(
            ["Goal", "Subject", "Disposition", "By rule", "Located value", "Why"],
            [
                [
                    record["record_id"],
                    code(record["subject"]),
                    record["disposition"],
                    record["disposition_rule"],
                    yes(record["disposition_located"]),
                    record["disposition_rationale"],
                ]
                for record in model["goals"]
            ],
        )
    )
    body.append("\n## Invariant dispositions\n")
    body.append(
        table(
            ["Invariant", "Disposition", "By rule", "Located value", "Why"],
            [
                [
                    record["record_id"],
                    record["disposition"],
                    record["disposition_rule"],
                    yes(record["disposition_located"]),
                    record["disposition_rationale"],
                ]
                for record in model["invariants"]
            ],
        )
    )
    body.append("")
    pages[PAGES[4]] = "\n".join(body) + "\n"

    # ---- 05 canonical knowledge object and graph register
    body = [front_matter(model, "Canonical Knowledge Object and Graph Register")]
    body.append(
        table(
            ["Reading", "Value"],
            [
                ["Object kinds registered", str(len(model["cko_model"]["kinds"]))],
                ["Relation types registered", str(len(model["cko_model"]["relation_types"]))],
                ["Objects discovered", str(counters["ckos_discovered"])],
                ["Relationship objects discovered", str(counters["relationship_ckos_discovered"])],
                ["Relationships whose target carries no registered identity", str(counters["relationships_without_target_identity"])],
                ["Identity collisions", str(counters["cko_identity_collisions"])],
                ["Objects of an unregistered kind", str(counters["ckos_of_unknown_kind"])],
                ["Registry open", yes(model["cko_model"]["open"])],
            ],
        )
    )
    body.append(f"\n**Admission.** {model['cko_model']['admission']}\n")
    body.append("## Composed graphs\n")
    body.append(
        table(
            ["Graph", "Concern", "Node kinds", "Edge relations", "Nodes", "Edges", "Composed"],
            [
                [
                    entry["id"],
                    entry["graph"],
                    ", ".join(code(k) for k in entry["node_kinds"]),
                    ", ".join(code(r) for r in entry["edge_relations"]),
                    str(entry["nodes"]),
                    str(entry["edges"]),
                    yes(entry["composed"]),
                ]
                for entry in model["graphs"]
            ],
        )
    )
    body.append("\n## Constitutional identity model\n")
    body.append(
        table(
            ["Property", "Value"],
            [
                ["Identity inputs", ", ".join(code(name) for name in model["semantic_identity"]["inputs"])],
                ["Excluded (may evolve)", ", ".join(code(name) for name in model["semantic_identity"]["excluded_inputs"])],
                ["Objects without a constitutional identity", str(counters["ckos_without_semantic_identity"])],
                ["Identity collisions", str(counters["semantic_identity_collisions"])],
                ["Identities resting on a mutable input", str(counters["identities_on_mutable_input"])],
            ],
        )
    )
    body.append("")
    pages[PAGES[5]] = "\n".join(body) + "\n"

    # ---- 06 provider and adapter register
    body = [front_matter(model, "Metadata Provider and Adapter Register")]
    body.append(
        "A provider declares WHERE engineering metadata lives and in WHICH serialization. An adapter "
        "declares HOW those records normalize into objects of a declared kind. The engine below the "
        "adapter layer sees no file, no format and no field name.\n"
    )
    body.append(
        table(
            ["Provider", "Located owner", "Serialization", "Discovery class", "Discovered", "Located", "Reader"],
            [
                [
                    provider["id"],
                    code(provider["owner"]),
                    code(provider["serialization"]),
                    code(provider["discovery_class"]),
                    yes(provider["discovered"]),
                    yes(provider["located"]),
                    yes(reader_for(serializations, provider["serialization"]) is not None),
                ]
                for provider in model["providers"]
            ],
        )
    )
    body.append("\n## Adapters\n")
    body.append(
        table(
            ["Adapter", "Provider", "Pointer", "Object kind", "Providers matched", "Objects", "Resolved"],
            [
                [
                    report["id"],
                    report["provider"],
                    code(report["pointer"]),
                    code(report["kind"]),
                    str(report["providers_matched"]),
                    str(report["objects"]),
                    yes(report["resolved"]),
                ]
                for report in model["adapters"]
            ],
        )
    )
    body.append("\n## Serializations\n")
    body.append(
        table(
            ["Serialization", "Reader", "Registered", "Note"],
            [
                [str(entry["id"]), code(entry.get("reader", "")), yes(bool(entry.get("registered"))), str(entry.get("note", ""))]
                for entry in model["serializations"]
            ],
        )
    )
    body.append(
        "\nAn unregistered serialization is REPORTED rather than fatal: a registry that must be "
        "implemented before it can be extended is not open.\n"
    )
    pages[PAGES[6]] = "\n".join(body) + "\n"

    # ---- 07 expansion axes
    body = [front_matter(model, "Open-World Expansion Axis Register")]
    body.append(
        "Every axis along which this programme could be bounded resolves to a located registrar. An "
        "axis whose registrar does not resolve is an axis with a hidden bound, and the gate closes.\n"
    )
    body.append(
        table(
            ["Axis", "Expansion axis", "Clause", "Admission path", "Registrar", "Blocking", "Bound"],
            [
                [
                    entry["id"],
                    entry["axis"],
                    entry["clause"],
                    entry["admission_path"],
                    code(entry["registrar"]),
                    yes(entry["blocking"]),
                    yes(entry["bound"]),
                ]
                for entry in model["expansion_axes"]
            ],
        )
    )
    body.append("\n## Admission paths (evidence probes)\n")
    body.append(
        table(
            ["Path", "Located owner", "Symbol", "Located", "Resolves"],
            [
                [entry["id"], code(entry["owner"]), code(entry["symbol"]), yes(entry["located"]), yes(entry["resolves"])]
                for entry in model["admission_paths"]
            ],
        )
    )
    body.append(
        table(
            ["Reading", "Value"],
            [
                ["Architectural bound tokens present", str(counters["limit_tokens_present"])],
                ["Terminal-state claims", str(counters["terminal_state_claims"])],
                ["Closed enumerations declared", str(counters["closed_enumerations_declared"])],
                ["Re-entry declared (lifecycle non-terminal)", yes(not counters["reentry_declarations_absent"])],
            ],
        )
    )
    body.append("")
    pages[PAGES[7]] = "\n".join(body) + "\n"

    # ---- 08 goal-driven engineering plan register
    body = [front_matter(model, "Goal-Driven Engineering Plan Register")]
    contract = model["goal_contract"]
    body.append(
        table(
            ["Plan contract", "Value"],
            [
                ["Plan identity inputs", ", ".join(code(name) for name in contract["plan_id_inputs"])],
                ["Writes", code(canonical(contract["writes"]))],
                ["Side effects", str(contract["side_effects"])],
                ["Invokes a capability", yes(bool(contract["invokes_capabilities"]))],
                ["Lifecycle re-derived", yes(bool(contract["rederives_lifecycle"]))],
            ],
        )
    )
    body.append(
        "\nThe plan is a pure function of the goal text and the consumed stage graph, so the same goal "
        "at the same repository state yields the same plan identity, byte for byte.\n"
    )
    body.append(
        table(
            ["Goal", "Plan identity (sha256)", "Steps", "Bound", "Unbound", "Reused", "Requiring new infrastructure", "Deterministic"],
            [
                [
                    record["record_id"],
                    record["plan"]["plan_id"],
                    str(record["plan"]["steps_total"]),
                    str(record["plan"]["steps_bound"]),
                    str(record["plan"]["steps_unbound"]),
                    str(record["plan"]["steps_reused"]),
                    str(record["plan"]["steps_requiring_new_infrastructure"]),
                    yes(record["plan_deterministic"]),
                ]
                for record in model["goals"]
            ],
        )
    )
    body.append("\n## The consumed lifecycle every goal traverses\n")
    body.append(
        f"Consumed from `{model['programme']['lifecycle_owner']}` — {counters['stages_consumed']} stages, "
        f"ordered by the discovered `{model['dependency_relation']}` relation, "
        f"{counters['graph_cycles']} cycles. This engine derives no stage and re-derives no order.\n"
    )
    body.append(
        "Each capability carries a disposition DERIVED from Repository Truth. **PASS** where a "
        "completion invariant already measures it against the located lifecycle owner at this "
        "capability's own name; **REUSE** where its located canonical owner discharges the "
        "obligation under a located authority; **EXTEND** where an owner exists but the "
        "obligation is not yet discharged; **CREATE** only where no canonical owner exists at "
        "all. The rule that fired is named, so no classification is manual.\n"
    )
    buckets: dict[str, int] = {}
    for record in model["stages"]:
        buckets[record["disposition_rule"]] = buckets.get(record["disposition_rule"], 0) + 1
    body.append(
        table(
            ["Disposition rule", "Capabilities", "Meaning"],
            [
                [
                    rule_id,
                    str(count),
                    next(
                        (
                            str(rule.get("rationale", "")).split("—", 1)[0].strip()
                            for rule in model["disposition_rules"]
                            if str(rule["id"]) == rule_id
                        ),
                        "",
                    ),
                ]
                for rule_id, count in sorted(buckets.items())
            ],
        )
    )
    body.append(
        f"\n**Coverage identity.** required = {counters['stages_consumed']} · dispositioned = "
        f"{counters['stages_consumed'] - counters['stages_undispositioned']} · undispositioned = "
        f"{counters['stages_undispositioned']} · imbalance = {counters['stage_coverage_imbalance']}. "
        f"Missing = 0, unowned = {counters['stages_unowned']}, unauthorized = "
        f"{counters['stages_unauthorized']}, requiring creation = "
        f"{counters['stages_dispositioned_create']}, explicitly invariant-measured = "
        f"{counters['stages_invariant_measured']}.\n"
    )
    body.append(
        table(
            ["#", "Capability", "Group", "Located owner", "Owner", "Authority", "Traversed", "Invariant", "Disposition", "By rule"],
            [
                [
                    str(record["position"]),
                    record["stage"],
                    record["group"],
                    code(record["owner"]),
                    yes(record["owner_located"]),
                    yes(record["facts"]["authority_located"]),
                    yes(record["facts"]["traversed"]),
                    yes(record["facts"]["invariant_measured"]),
                    record["disposition"],
                    record["disposition_rule"],
                ]
                for record in model["stages"]
            ],
        )
    )
    for record in model["goals"]:
        body.append(f"\n### {record['record_id']} — {record['goal']}\n")
        body.append(f"Subject: `{record['subject']}` · disposition **{record['disposition']}** · plan `{record['plan']['plan_id']}`\n")
        body.append(
            table(
                ["#", "Stage", "Located owner", "Bound", "Reused", "New infrastructure required"],
                [
                    [
                        str(step["position"]),
                        step["stage"],
                        code(step["owner"]),
                        yes(step["bound"]),
                        yes(step["reused"]),
                        yes(step["new_infrastructure_required"]),
                    ]
                    for step in record["plan"]["steps"]
                ],
            )
        )
    body.append("")
    pages[PAGES[8]] = "\n".join(body) + "\n"

    # ---- 09 engineering authority crosswalk
    body = [front_matter(model, "Engineering Authority Crosswalk Register")]
    body.append(
        "Several located instruments govern engineering. They are CROSSWALKED and never merged: a "
        "merge would amend every owner at once, which is expansion by reinterpretation. This programme "
        "claims none of these roles, and the gate closes if it ever does.\n"
    )
    body.append(
        table(
            ["Authority", "Concern", "Located owner", "Anchor", "Role", "Located", "Anchor present", "Merge prohibited", "Claimed here"],
            [
                [
                    entry["id"],
                    entry["name"],
                    code(entry["owner"]),
                    code(entry["anchor"]),
                    entry["role"],
                    yes(entry["located"]),
                    yes(entry["anchor_present"]),
                    yes(entry["merge_prohibited"]),
                    yes(entry["claimed_here"]),
                ]
                for entry in model["authorities"]
            ],
        )
    )
    body.append("\n## Self-evolution path — every step owned OUTSIDE this programme\n")
    body.append(
        table(
            ["Step", "Constitutional step", "Located owner", "Anchor", "Resolves", "Anchor present", "Owned externally"],
            [
                [
                    entry["id"],
                    entry["step"],
                    code(entry["owner"]),
                    code(entry["anchor"]),
                    yes(entry["located"]),
                    yes(entry["anchor_present"]),
                    yes(entry["owned_externally"]),
                ]
                for entry in model["self_evolution"]
            ],
        )
    )
    body.append("")
    pages[PAGES[9]] = "\n".join(body) + "\n"

    # ---- 10 future engineering reduction
    body = [front_matter(model, "Future Engineering Reduction Register")]
    body.append(
        "The reduction claim is stated as a measurement, not as a promise. Each measure asks what an "
        "ADDITIONAL engineering goal would cost: if every step of every plan is discharged by an "
        "already-located owner, then the marginal engineering infrastructure a further goal requires "
        "is nothing, and future engineering is reduced to domain work plus governed evolution.\n"
    )
    body.append(
        table(
            ["Measure", "Reduction", "Located owner", "Measure", "Value", "Expect", "Achieved"],
            [
                [
                    entry["id"],
                    entry["reduction"],
                    code(entry["owner"]),
                    code(entry["measure"]),
                    str(entry["value"]),
                    f"{entry['comparator']} {entry['expect']}",
                    yes(entry["achieved"]),
                ]
                for entry in model["reduction"]
            ],
        )
    )
    body.append("\n## What each measure means\n")
    body.append(
        table(
            ["Measure", "Statement"],
            [[entry["id"], entry["statement"]] for entry in model["reduction"]],
        )
    )
    body.append("")
    pages[PAGES[10]] = "\n".join(body) + "\n"

    # ---- 11 knowledge extraction and capability elevation
    body = [front_matter(model, "Knowledge Extraction and Capability Elevation Register")]
    body.append(
        f"Registration owner: `{model['knowledge_extraction']['registration_owner']}` · "
        f"decision owner: `{model['knowledge_extraction']['decision_owner']}` · "
        f"architecture owner: `{model['knowledge_extraction']['architecture_owner']}`\n"
    )
    body.append(
        "Knowledge Once: extracted knowledge is registered in its located home and is never read back "
        "from a derived artifact of this programme. No register this programme writes is Repository "
        "Truth.\n"
    )
    body.append(
        table(
            ["Extraction", "Knowledge", "Measure", "Value", "Reusable as", "Measured"],
            [
                [
                    entry["id"],
                    entry["knowledge"],
                    code(entry["measure"]),
                    str(entry["value"]),
                    entry["reusable_as"],
                    yes(entry["measured"]),
                ]
                for entry in model["extractions"]
            ],
        )
    )
    body.append("\n## Capability elevation — each increase carries all five facets\n")
    body.append(
        table(
            ["Elevation", "Increase", "Measure", "Value", "Evidence", "Lineage", "Replay", "Certification", "Authority", "Evidenced"],
            [
                [
                    entry["id"],
                    entry["increase"],
                    code(entry["measure"]),
                    str(entry["value"]),
                    yes(exists(entry["facets"]["evidence_owner"])),
                    yes(exists(entry["facets"]["lineage_owner"])),
                    yes(exists(entry["facets"]["replay_owner"])),
                    yes(exists(entry["facets"]["certification_owner"])),
                    yes(exists(entry["facets"]["authority_owner"])),
                    yes(entry["evidenced"]),
                ]
                for entry in model["elevations"]
            ],
        )
    )
    body.append("")
    body.append(
        table(
            ["Elevation", "Statement"],
            [[entry["id"], entry["statement"]] for entry in model["elevations"]],
        )
    )
    body.append("")
    pages[PAGES[11]] = "\n".join(body) + "\n"

    # ---- 12 validation report
    body = [front_matter(model, "Validation Report")]
    body.append(
        table(
            ["Dimension", "Requirement", "Measure", "Value", "Expect", "Blocking", "Satisfied", "Bound finding"],
            [
                [
                    entry["id"],
                    entry["dimension"],
                    code(entry["measure"]),
                    str(entry["value"]),
                    f"{entry['comparator']} {entry['expect']}",
                    yes(entry["blocking"]),
                    tick(entry["satisfied"]),
                    entry["bound_finding"],
                ]
                for entry in model["validations"]
            ],
        )
    )
    satisfied = sum(1 for entry in model["validations"] if entry["satisfied"])
    body.append(f"\n**{satisfied}/{len(model['validations'])} dimensions satisfied.** Gate: **{model['gate']}**.\n")
    body.append(
        "Every declared bound is held at exactly its measured value, so no bound carries slack and "
        "any regression closes the gate.\n"
    )
    pages[PAGES[12]] = "\n".join(body) + "\n"

    # ---- 13 certification report
    body = [front_matter(model, "Certification Report")]
    body.append(f"**DETERMINATION — {model['determination']}**\n")
    body.append(
        "> This report confers nothing. It records a measurement. It grants no ratification, no "
        "finality and no authority, and it does not raise the standing of anything it measures.\n"
    )
    body.append("## Exit criteria\n")
    body.append(
        table(
            ["Criterion", "Statement"],
            [[str(entry["id"]), str(entry["statement"])] for entry in model["exit_criteria"]],
        )
    )
    body.append("\n## Measured disclosures — referred, not decided\n")
    for entry in model["findings"]:
        body.append(f"### {entry['id']} — {entry['title']}\n")
        body.append(
            table(
                ["Field", "Value"],
                [
                    ["CLASS", str(entry["class"])],
                    ["DISPOSITION", str(entry["disposition"])],
                    ["BLOCKING", yes(bool(entry.get("blocking")))],
                    ["REFERRED TO", code(entry.get("referred_to", ""))],
                    ["BOUND MEASURE", code(entry.get("bound_measure", ""))],
                ],
            )
        )
        body.append(f"\n{entry['detail']}\n")
        body.append(f"**Why not repaired.** {entry['why_not_repaired']}\n")
    body.append("## Protected records — read, never written\n")
    body.append(
        table(
            ["Record", "Located owner", "Anchor", "Located", "Anchor present", "Law"],
            [
                [
                    entry["id"],
                    code(entry["owner"]),
                    code(entry["anchor"]),
                    yes(entry["located"]),
                    yes(entry["anchor_present"]),
                    entry["law"],
                ]
                for entry in model["record_set"]
            ],
        )
    )
    body.append(f"\nwrite set ∩ located record set = ∅: **{yes(model['immutability']['disjoint'])}**\n")
    body.append("## Capability disposition\n")
    body.append(
        table(
            ["Capability", "Concern", "Located owner", "Status", "Action", "Owner located"],
            [
                [
                    str(entry["id"]),
                    str(entry["capability"]),
                    code(entry["owner"]),
                    str(entry["status"]),
                    str(entry["action"]),
                    yes(exists(str(entry["owner"]))),
                ]
                for entry in model["capabilities"]
            ],
        )
    )
    body.append(
        f"\nCapabilities dispositioned CREATE: **{counters['capabilities_created']}**. "
        "CREATE is lawful only where Repository Truth proves no canonical owner exists.\n"
    )
    pages[PAGES[13]] = "\n".join(body) + "\n"

    # ---- 14 self-engineering and non-privilege
    body = [front_matter(model, "Self-Engineering and Non-Privilege Register")]
    body.append(
        "This programme is engineerable through the same constitutional lifecycle as any other "
        "subject, and holds no privileged path. The proof is structural, not documentary: it appears "
        "in the goal plane as a subject, its plan is derived by the same traversal, and the engine "
        "contains no branch keyed on its own identity.\n"
    )
    self_goals = [record for record in model["goals"] if record["facts"]["subject_is_self"]]
    body.append(
        table(
            ["Reading", "Value"],
            [
                ["Goals whose subject is this engine", str(len(self_goals))],
                ["Those goals' plans complete", yes(all(record["facts"]["plan_complete"] for record in self_goals))],
                ["Those goals' plans deterministic", yes(all(record["plan_deterministic"] for record in self_goals))],
                ["Privileged branches on own identity", str(counters["privileged_branches"])],
                ["Stages originated by this programme", str(counters["stages_originated_here"])],
                ["Invariants owned by this programme", str(counters["invariants_owned_here"])],
                ["Self-evolution steps owned here", str(counters["self_evolution_steps_owned_here"])],
                ["Derived artifacts used as a metadata source", str(counters["derived_artifacts_used_as_truth"])],
            ],
        )
    )
    body.append("\n## The self-referential goals and their derived plans\n")
    body.append(
        table(
            ["Goal", "Subject", "Disposition", "Steps", "Unbound", "Plan identity"],
            [
                [
                    record["record_id"],
                    code(record["subject"]),
                    record["disposition"],
                    str(record["plan"]["steps_total"]),
                    str(record["plan"]["steps_unbound"]),
                    record["plan"]["plan_id"],
                ]
                for record in self_goals
            ],
        )
    )
    body.append(
        "\nA subject that is this engine is measured by the same obligations, disposed by the same "
        "rules and planned over the same lifecycle as a subject that is any other engine. No branch "
        "distinguishes them, which is what makes the absence of a privileged path mechanical.\n"
    )
    pages[PAGES[14]] = "\n".join(body) + "\n"

    # ---- 15 Ω-E05 exit certification
    body = [front_matter(model, "Ω-E05 Exit Certification")]
    body.append(
        "Ω-E05 closes only when every exit dimension is ready AND the gate is OPEN. Every dimension is "
        "MEASURED against a located owner: a dimension whose owner does not resolve, or whose measure "
        "is unmet, reports NOT READY rather than being waived.\n"
    )
    body.append(
        table(
            ["Dimension", "Requirement", "Located owner", "Measure", "Value", "Expect", "Ready"],
            [
                [
                    entry["id"],
                    entry["dimension"],
                    code(entry["owner"]),
                    code(entry["measure"]),
                    str(entry["value"]),
                    f"{entry['comparator']} {entry['expect']}",
                    tick(entry["ready"]),
                ]
                for entry in model["exit_dimensions"]
            ],
        )
    )
    ready = sum(1 for entry in model["exit_dimensions"] if entry["ready"])
    body.append(f"\n**Exit readiness: {ready}/{len(model['exit_dimensions'])} dimensions.** Gate: **{model['gate']}**.\n")
    body.append("## Determination\n")
    body.append(
        f"**Ω-E05 {'COMPLETE' if model['omega_e05_complete'] else 'NOT COMPLETE'}.** "
        "Completion records that a constitutionally valid engineering goal is transformed into a "
        "certified, replayable, converged plan bound entirely to located owners, with no new "
        "engineering infrastructure and no manual engineering decision. It confers no ratification, "
        "no finality and no authority: certification closes scope, never evolution.\n"
    )
    pages[PAGES[15]] = "\n".join(body) + "\n"

    return pages


def write_registers(model: dict) -> list[str]:
    HERE.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, text in render(model).items():
        (HERE / name).write_text(text, encoding="utf-8")
        written.append(name)
    MODEL.write_text(json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(MODEL.name)
    return sorted(written)



# ------------------------------------------------------------------------- self-guards


def _schema_vocabulary(payload: Any, out: set[str] | None = None) -> set[str]:
    """Every key the declaration uses, at any depth.

    These are GOVERNED VOCABULARY: an engine must be able to name the fields of its own
    declaration. The vocabulary is DERIVED from the declaration's keys rather than listed,
    so the exemption cannot be widened by hand.
    """
    words: set[str] = set() if out is None else out
    if isinstance(payload, dict):
        for key, value in payload.items():
            words.add(str(key).lower())
            _schema_vocabulary(value, words)
    elif isinstance(payload, list):
        for item in payload:
            _schema_vocabulary(item, words)
    return words


def _executable_literals() -> set[str]:
    """Every string constant in EXECUTABLE position in this source file.

    Comments never reach the AST, and docstrings are excluded explicitly, because prose
    that names a discovered value steers nothing.
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


# The syntactic positions in which a string literal can STEER A BRANCH. A literal that
# reaches none of them cannot select an owner, a stage, a capability or a code path: it can
# only be printed. The distinction is what separates EXECUTABLE GOVERNANCE, which may never
# be hardcoded, from PRESENTATION, which is a rendered heading and governs nothing.
_STEERING_PREDICATES = frozenset({"startswith", "endswith", "get", "count", "find", "index", "split"})


def _governing_literals() -> set[str]:
    """The string literals in this engine that could steer behaviour.

    A literal is governing when it is an operand of a comparison or membership test, a key
    of a mapping (which can dispatch), a subscript selector, or an argument to a string
    predicate. Everything else — a heading, a column label, a rendered row — is
    PRESENTATION: it flows into output and can never select a capability, an owner or a
    stage. Classifying by POSITION rather than by appearance is what lets this guard forbid
    hardcoded constitutional behaviour without forbidding the words themselves.
    """
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    parents: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node

    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    docstrings.add(id(body[0].value))

    governing: set[str] = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if id(node) in docstrings:
            continue
        current: ast.AST = node
        while True:
            parent = parents.get(id(current))
            if parent is None:
                break
            if isinstance(parent, ast.Compare):
                governing.add(node.value)
                break
            if isinstance(parent, ast.Dict) and any(key is current for key in parent.keys):
                governing.add(node.value)
                break
            if isinstance(parent, ast.Subscript) and parent.slice is current:
                governing.add(node.value)
                break
            if isinstance(parent, ast.Call):
                func = parent.func
                if isinstance(func, ast.Attribute) and func.attr in _STEERING_PREDICATES:
                    governing.add(node.value)
                break
            # A literal inside a container or a boolean operator inherits the position of
            # that container, so `x in ("a", "b")` and `{"a", "b"}` are both reached.
            if isinstance(parent, (ast.Tuple, ast.List, ast.Set, ast.BoolOp, ast.UnaryOp, ast.IfExp)):
                current = parent
                continue
            break
    return governing


def check_declaration(document: dict) -> list[str]:  # noqa: C901 - one integrity rule per section
    """Referential integrity of the declaration itself."""
    problems: list[str] = []
    seen: dict[str, str] = {}
    listed = (
        "serializations",
        "discovery_classes",
        "metadata_providers",
        "metadata_adapters",
        "reference_normalizations",
        "applicability_classes",
        "planes",
        "engineering_authorities",
        "obligation_rules",
        "property_rules",
        "disposition_rules",
        "admission_paths",
        "expansion_axes",
        "reduction_measures",
        "elevation_measures",
        "self_evolution_path",
        "exit_dimensions",
        "derived_counters",
        "capabilities",
        "validations",
        "exit_criteria",
        "findings",
    )
    for section in listed:
        for entry in document[section]:
            ident = str(entry["id"])
            if ident in seen:
                problems.append(f"identifier is not unique: {ident} in {section} and {seen[ident]}")
            seen[ident] = section
    for section, key in (
        ("cko_model", "kinds"),
        ("cko_model", "relation_types"),
        ("record_set", "records"),
    ):
        for entry in document[section][key]:
            ident = str(entry.get("id") or entry.get("kind") or entry.get("relation"))
            if ident in seen:
                problems.append(f"identifier is not unique: {ident} in {section}.{key} and {seen[ident]}")
            seen[ident] = f"{section}.{key}"
    for entry in document["graph_types"]["types"]:
        ident = str(entry["id"])
        if ident in seen:
            problems.append(f"identifier is not unique: {ident}")
        seen[ident] = "graph_types"

    measures = [str(entry["measure"]) for entry in document["validations"]]
    problems += [f"a validation measure is declared twice: {m}" for m in sorted({m for m in measures if measures.count(m) > 1})]

    programme = document["programme"]
    if not str(programme["authority"]).startswith("NONE"):
        problems.append("the programme claims an authority")
    for field in ("law_owner", "architecture_owner", "lifecycle_owner"):
        if not exists(str(programme[field])):
            problems.append(f"a programme owner does not resolve: {field}={programme[field]}")

    kinds = {str(entry["kind"]) for entry in document["cko_model"]["kinds"]}
    relations = {str(entry["relation"]) for entry in document["cko_model"]["relation_types"]}
    serializations = {str(entry["id"]) for entry in document["serializations"]}
    classes = {str(entry["id"]) for entry in document["discovery_classes"]}
    provider_ids = {str(entry["id"]) for entry in document["metadata_providers"]} | discovered_surface_ids(document)

    for entry in document["metadata_providers"]:
        if not exists(str(entry["owner"])):
            problems.append(f"a provider owner does not resolve: {entry['id']} → {entry['owner']}")
        if str(entry["serialization"]) not in serializations:
            problems.append(f"a provider names an unregistered serialization: {entry['id']}")
        if str(entry["discovery_class"]) not in classes:
            problems.append(f"a provider names an unregistered discovery class: {entry['id']}")
    for spec in document["provider_discovery"]:
        if not (REPO / str(spec["root"])).is_dir():
            problems.append(f"a discovery surface root does not resolve: {spec['id']}")
        if str(spec["serialization"]) not in serializations:
            problems.append(f"a discovery surface names an unregistered serialization: {spec['id']}")
    for entry in document["metadata_adapters"]:
        if str(entry["provider"]) not in provider_ids:
            problems.append(f"an adapter names an unknown provider: {entry['id']}")
        if str(entry["cko_kind"]) not in kinds:
            problems.append(f"an adapter emits an unregistered kind: {entry['id']}")
        for relation in (entry.get("relation_map") or {}):
            if str(relation) not in relations:
                problems.append(f"an adapter maps an unregistered relation: {entry['id']} → {relation}")
    for entry in document["graph_types"]["types"]:
        for kind in entry["node_kinds"]:
            if str(kind) not in kinds:
                problems.append(f"a graph type composes an unregistered kind: {entry['id']} → {kind}")
        for relation in entry["edge_relations"]:
            if str(relation) not in relations:
                problems.append(f"a graph type composes an unregistered relation: {entry['id']} → {relation}")
    for entry in document["planes"]:
        if str(entry["kind"]) not in kinds:
            problems.append(f"a plane names an unregistered kind: {entry['id']}")
    if str(document["cko_model"]["disposition_kind"]) not in kinds:
        problems.append("the disposition kind is not a registered object kind")

    for section in ("engineering_authorities", "self_evolution_path", "record_set"):
        entries = document[section]["records"] if section == "record_set" else document[section]
        for entry in entries:
            owner = str(entry["owner"])
            if not exists(owner):
                problems.append(f"a cited owner does not resolve: {entry['id']} → {owner}")
            elif not anchor_present(owner, str(entry.get("anchor", ""))):
                problems.append(f"a cited anchor is absent from its owner: {entry['id']}")
    for entry in document["admission_paths"] + document["capabilities"] + document["reduction_measures"]:
        if not exists(str(entry["owner"])):
            problems.append(f"a cited owner does not resolve: {entry['id']} → {entry['owner']}")
    for entry in document["exit_dimensions"]:
        if not exists(str(entry["owner"])):
            problems.append(f"an exit dimension owner does not resolve: {entry['id']} → {entry['owner']}")
    for entry in document["elevation_measures"]:
        for facet in ("evidence_owner", "lineage_owner", "replay_owner", "certification_owner", "authority_owner"):
            if not exists(str(entry.get(facet, ""))):
                problems.append(f"an elevation facet owner does not resolve: {entry['id']}.{facet}")

    admission_ids = {str(entry["id"]) for entry in document["admission_paths"]}
    for entry in document["expansion_axes"]:
        if str(entry["admission_path"]) not in admission_ids:
            problems.append(f"an expansion axis names an unknown admission path: {entry['id']}")

    # Every claimant this programme cites must be protected from its own writes.
    prefixes = [str(prefix) for prefix in programme["forbidden_write_prefixes"]]
    claimants = {str(entry["owner"]) for entry in document["engineering_authorities"]}
    claimants |= {str(entry["owner"]) for entry in document["record_set"]["records"]}
    for owner in sorted(claimants):
        if owner.startswith(OWN_PREFIX):
            continue
        if not any(owner.startswith(prefix) for prefix in prefixes):
            problems.append(f"a claimant is left unprotected by the forbidden write prefixes: {owner}")

    findings = {str(entry["id"]) for entry in document["findings"]}
    for entry in document["validations"]:
        if str(entry["comparator"]) == "<=" and str(entry.get("bound_finding", "")) not in findings:
            problems.append(f"a bounded validation names no governing finding: {entry['id']}")

    actions = {str(entry["action"]) for entry in document["capabilities"]}
    if ACTION_EXTEND not in actions:
        problems.append("no capability is dispositioned EXTEND, so nothing is being extended")
    for entry in document["capabilities"]:
        status, action = str(entry["status"]), str(entry["action"])
        coherent = {STATUS_MISSING: ACTION_CREATE, STATUS_EXISTING: ACTION_REUSE, STATUS_PARTIAL: ACTION_EXTEND}
        if coherent.get(status) != action:
            problems.append(f"a capability's status and action disagree: {entry['id']} {status}/{action}")

    # Dispositions must be total on every measured plane, or a subject could escape one.
    for plane in document["planes"]:
        rules = [r for r in document["disposition_rules"] if str(r.get("plane")) == str(plane["id"])]
        if not rules:
            problems.append(f"a measured plane has no disposition rule: {plane['id']}")
        elif rules[-1].get("when"):
            problems.append(f"a plane's final disposition rule is not total: {plane['id']}")
    return problems


def check_no_enumeration(document: dict) -> list[str]:
    """No discovered value may STEER BEHAVIOUR from inside this engine.

    This is the mechanical proof that the engineering plane is graph-driven rather than
    enumeration-driven: if the engine cannot branch on what it discovered, it cannot have
    hard-coded it, and admitting a new goal, invariant or stage cannot require editing it.

    Findings are classified by POSITION, not by appearance, in three categories:

      EXECUTABLE GOVERNANCE — a literal that can steer a branch: an operand of a
        comparison or membership test, a mapping key, a subscript selector, or an argument
        to a string predicate. These may NEVER carry a discovered value, and are the only
        findings this guard reports.
      DECLARATION — vocabulary originating from Repository Truth. It belongs in the
        declaration and the manifests, and is exempt here: the declaration's own keys are
        governed vocabulary, derived from its keys rather than listed, so the exemption
        cannot be widened by hand.
      PRESENTATION — a heading, a column label, a rendered row. It flows into output and
        can select no owner, no stage and no capability, so a discovered value appearing
        there is not an enumeration and is deliberately NOT reported.
    """
    literals = _governing_literals()
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

    for record in model["goals"]:
        if embedded(record["record_id"]):
            leaked.append(f"goal identifier steers behaviour: {record['record_id']}")
        if literal(record["goal"]):
            leaked.append(f"goal text steers behaviour: {record['goal']}")
        for value in (record["subject"], record["owner"], record["authority_owner"]):
            if embedded(value):
                leaked.append(f"goal owner path steers behaviour: {value}")
    for record in model["invariants"]:
        if embedded(record["record_id"]):
            leaked.append(f"invariant identifier steers behaviour: {record['record_id']}")
        if literal(record["invariant"]):
            leaked.append(f"invariant name steers behaviour: {record['invariant']}")
        if embedded(record["owner"]):
            leaked.append(f"invariant owner steers behaviour: {record['owner']}")
    for record in model["stages"]:
        if embedded(record["record_id"]):
            leaked.append(f"stage identifier steers behaviour: {record['record_id']}")
        if literal(record["stage"]):
            leaked.append(f"stage name steers behaviour: {record['stage']}")
        if embedded(record["owner"]):
            leaked.append(f"stage owner path steers behaviour: {record['owner']}")
    for entry in model["graphs"]:
        if literal(entry["graph"]):
            leaked.append(f"graph type steers behaviour: {entry['graph']}")
        if embedded(entry["id"]):
            leaked.append(f"graph type identifier steers behaviour: {entry['id']}")
    for entry in model["providers"]:
        if embedded(entry["owner"]):
            leaked.append(f"provider owner steers behaviour: {entry['owner']}")
    for entry in model["adapters"]:
        if embedded(entry["id"]):
            leaked.append(f"adapter identifier steers behaviour: {entry['id']}")
    for entry in model["admission_paths"]:
        if embedded(entry["owner"]):
            leaked.append(f"admission path steers behaviour: {entry['owner']}")
    for entry in model["capabilities"]:
        if embedded(str(entry["owner"])):
            leaked.append(f"capability owner steers behaviour: {entry['owner']}")
    for name in model["cko_model"]["kinds"]:
        if literal(name):
            leaked.append(f"object kind steers behaviour: {name}")
    for name in model["cko_model"]["relation_types"]:
        if literal(name):
            leaked.append(f"relation type steers behaviour: {name}")
    for entry in model["expansion_axes"]:
        if literal(entry["axis"]):
            leaked.append(f"expansion axis steers behaviour: {entry['axis']}")
    for record in model["goals"] + model["invariants"]:
        if literal(record["disposition"]):
            leaked.append(f"disposition value steers behaviour: {record['disposition']}")
    return sorted(set(leaked))


def check_no_privileged_logic(document: dict) -> list[str]:
    """This engine may hold no privileged path over itself.

    Two proofs. First, structural: no executable literal names this programme's own home,
    so no branch can recognise it — the home is derived from ``__file__``. Second,
    behavioural: this engine appears in the goal plane as a subject, is measured by the
    same obligations, disposed by the same rules and planned over the same lifecycle as
    every other subject, and its plan is complete and deterministic.
    """
    model = measure(document)
    problems: list[str] = []
    if model["counters"]["privileged_branches"]:
        problems.append(
            f"{model['counters']['privileged_branches']} executable literals name this programme's own home"
        )
    self_goals = [record for record in model["goals"] if record["facts"]["subject_is_self"]]
    if not self_goals:
        problems.append("no engineering goal takes this engine as its subject, so self-engineering is unproven")
    for record in self_goals:
        if not record["subject_located"]:
            problems.append(f"{record['record_id']}: the self subject does not resolve")
        if not record["facts"]["plan_complete"]:
            problems.append(f"{record['record_id']}: the self plan has an unbound step")
        if not record["plan_deterministic"]:
            problems.append(f"{record['record_id']}: the self plan is not deterministic")
        if not record["disposition_located"]:
            problems.append(f"{record['record_id']}: the self disposition is not a located value")
    # The lifecycle a self goal traverses must be the SAME consumed lifecycle.
    if model["counters"]["stages_originated_here"]:
        problems.append("a lifecycle stage was originated by this programme rather than consumed")
    return problems


def check_reuse_before_create(document: dict) -> list[str]:
    """Nothing may be created where Repository Truth locates a canonical owner."""
    model = measure(document)
    problems: list[str] = []
    for entry in document["capabilities"]:
        if str(entry["action"]) != ACTION_CREATE:
            continue
        problems.append(f"a capability is dispositioned CREATE: {entry['id']}")
    for record in model["invariants"]:
        if record["facts"]["owner_located"] and record["disposition_rule"].endswith(ACTION_CREATE):
            problems.append(f"{record['record_id']}: CREATE was reached although an owner is located")
    for record in model["goals"]:
        if record["facts"]["subject_located"] and record["disposition_rule"].endswith(ACTION_CREATE):
            problems.append(f"{record['record_id']}: CREATE was reached although the subject is located")
    # Every bound owner must be somebody else's: an owner inside this home would be this
    # programme re-implementing what it claims to reuse.
    for record in model["stages"]:
        if record["owner"].startswith(OWN_PREFIX):
            problems.append(f"{record['record_id']}: a consumed stage is owned by this programme")
        if record["facts"]["owner_located"] and record["disposition_rule"].endswith(ACTION_CREATE):
            problems.append(f"{record['record_id']}: CREATE was reached although the capability has a located owner")
    for record in model["invariants"]:
        if not record["facts"]["outside_own_home"]:
            problems.append(f"{record['record_id']}: the invariant owner is this programme")
    return problems


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
    source = Path(__file__).read_text(encoding="utf-8")
    for forbidden in document["hygiene"]["nondeterministic_inputs"]:
        if str(forbidden) in source:
            problems.append(f"the engine reads a non-deterministic input: {forbidden}")
    model = measure(document)
    problems += [
        f"{record['record_id']}: plan is not deterministic" for record in model["goals"] if not record["plan_deterministic"]
    ]
    if measure(document)["seal_sha256"] != measure(document)["seal_sha256"]:  # pragma: no cover
        problems.append("the seal is not stable across two measurements")
    return problems


def check_implementation_independence(document: dict) -> list[str]:
    """No Canonical Knowledge Object or relation may originate from implementation source."""
    model = measure(document)
    problems: list[str] = []
    originating = {str(entry["id"]) for entry in document["discovery_classes"] if entry.get(CLASS_MAY_ORIGINATE)}
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
    if model["counters"]["derived_artifacts_used_as_truth"]:
        problems.append("a derived artifact of this programme is declared as a metadata source")
    if not model["goals"]:
        problems.append("no engineering goal was discovered, so independence is unmeasured")
    if not model["invariants"]:
        problems.append("no completion invariant was discovered, so independence is unmeasured")
    if not model["stages"]:
        problems.append("no lifecycle stage was consumed, so independence is unmeasured")
    return problems


def check_open_world(document: dict) -> list[str]:
    """No finite bound may be declared, and every open registry must name a live registrar."""
    model = measure(document)
    counters = model["counters"]
    problems = [f"architectural bound token present: {hit}" for hit in model["bound_hits"]]
    problems += [
        f"{entry['id']}: expansion axis has no resolving admission path"
        for entry in model["expansion_axes"]
        if entry["blocking"] and not entry["bound"]
    ]
    for provider in model["providers"]:
        if not provider["discovered"]:
            continue
        if not provider["open"]:
            problems.append(f"{provider['owner']}: a discovered surface does not declare itself open")
        if provider["closed_enumeration"]:
            problems.append(f"{provider['owner']}: a discovered surface declares a closed enumeration")
    if counters["closed_enumerations_declared"]:
        problems.append("a registry is declared closed")
    if counters["serialization_readers_registered"] < 2:
        problems.append("fewer than two serialization readers are registered, so serialization is not open")
    if not counters["serializations_unregistered"]:
        problems.append("no unregistered serialization is admitted, so the registry is closed in practice")
    if counters["serializations_exercised"] < 2:
        problems.append("fewer than two serializations are exercised by a located provider")
    if counters["discovered_surfaces"] < 2:
        problems.append("fewer than two open discovered surfaces exist")
    if counters["reentry_declarations_absent"]:
        problems.append("no re-entry is declared, so the lifecycle would terminate")
    if counters["terminal_state_claims"]:
        problems.append("a terminal state is claimed")
    return problems


def check_no_parallel_authority(document: dict) -> list[str]:
    """This programme may hold no authority and may claim no located role."""
    model = measure(document)
    problems: list[str] = []
    if not str(document["programme"]["authority"]).startswith("NONE"):
        problems.append("the programme claims an authority")
    for entry in model["authorities"]:
        if entry["claimed_here"]:
            problems.append(f"{entry['id']}: a located engineering authority is claimed by this programme")
        if not entry["located"]:
            problems.append(f"{entry['id']}: a located engineering authority does not resolve")
        if not entry["anchor_present"]:
            problems.append(f"{entry['id']}: the cited anchor is absent from its owner")
        if not entry["merge_prohibited"]:
            problems.append(f"{entry['id']}: an authority is not marked unmergeable")
    if model["counters"]["capabilities_created"]:
        problems.append("a capability is dispositioned CREATE")
    for entry in model["findings"]:
        if str(entry["disposition"]) not in ("REGISTERED", "GOVERNED"):
            problems.append(f"{entry['id']}: a divergence is decided rather than referred")
    for entry in model["self_evolution"]:
        if not entry["owned_externally"]:
            problems.append(f"{entry['id']}: a self-evolution step is owned by this programme")
    problems += [f"a protected record is in the write set: {p}" for p in model["immutability"]["intersections"]]
    # The lifecycle must be consumed from a single located owner, never authored here.
    if model["programme"]["lifecycle_owner"].startswith(OWN_PREFIX):
        problems.append("the lifecycle owner is this programme, which would be a parallel lifecycle")
    return problems


def check_goal_plane_executable(document: dict) -> list[str]:
    """Every discovered goal must reach a complete, bound, deterministic plan."""
    model = measure(document)
    counters = model["counters"]
    problems: list[str] = []
    if not model["goals"]:
        problems.append("no engineering goal was discovered")
    if not model["stages"]:
        problems.append("no lifecycle stage was consumed, so no plan can be derived")
    if not model["order"]:
        problems.append("the consumed lifecycle yields no order")
    if len(model["order"]) != len(model["stages"]):
        problems.append("the consumed lifecycle is not fully ordered")
    if model["cycles"]:
        problems.append(f"the consumed lifecycle contains cycles: {', '.join(model['cycles'][:SAMPLE])}")
    if not model["dependency_relation"]:
        problems.append("no dependency relation was discovered, so ordering rests on nothing")
    if counters["goal_plan_steps_unbound"]:
        problems.append(f"{counters['goal_plan_steps_unbound']} plan steps bind no located owner")
    if counters["goal_steps_requiring_new_infrastructure"]:
        problems.append(
            f"{counters['goal_steps_requiring_new_infrastructure']} plan steps would require new engineering infrastructure"
        )
    if counters["goal_plans_nondeterministic"]:
        problems.append("a goal plan is not deterministic")
    if counters["goals_without_located_subject"]:
        problems.append(f"{counters['goals_without_located_subject']} goals name an unlocated subject")
    if counters["goals_without_located_disposition"]:
        problems.append("a goal disposition is not a value the repository legislates")
    if counters["dangling_relations"]:
        problems.append(f"{counters['dangling_relations']} relations dangle")
    if counters["stages_unowned"]:
        problems.append(f"{counters['stages_unowned']} consumed stages name no located owner")
    if counters["stages_undispositioned"]:
        problems.append(f"{counters['stages_undispositioned']} consumed capabilities escaped disposition")
    if counters["stage_coverage_imbalance"]:
        problems.append("the lifecycle coverage identity does not balance")
    if counters["stages_dispositioned_create"]:
        problems.append(f"{counters['stages_dispositioned_create']} consumed capabilities require CREATE")
    if counters["stages_without_located_disposition"]:
        problems.append("a capability disposition is not a value the repository legislates")
    return problems


def check_invariant_coverage(document: dict) -> list[str]:
    """Every completion invariant must be owned, anchored and measured against Repository Truth."""
    model = measure(document)
    counters = model["counters"]
    problems: list[str] = []
    if not model["invariants"]:
        problems.append("no completion invariant was discovered")
    for record in model["invariants"]:
        if not record["facts"]["owner_located"]:
            problems.append(f"{record['record_id']}: no located owner")
        elif not record["facts"]["anchor_present"]:
            problems.append(f"{record['record_id']}: the cited anchor is absent from its owner")
        if not record["facts"]["measure_declared"]:
            problems.append(f"{record['record_id']}: no measure is declared, so the invariant is unmeasurable")
        elif not record["facts"]["measure_located"]:
            problems.append(f"{record['record_id']}: the declared measure does not resolve")
    if counters["invariants_dispositioned_create"]:
        problems.append(f"{counters['invariants_dispositioned_create']} invariants require CREATE")
    return problems


def check_cko_identity(document: dict) -> list[str]:
    model = measure(document)
    problems = [f"an entity holds more than one object: {item}" for item in identity_collisions(model_ckos(model))[:SAMPLE]]
    if model["counters"]["cko_identity_collisions"]:
        problems.append(f"{model['counters']['cko_identity_collisions']} identity collisions")
    if model["counters"]["ckos_of_unknown_kind"]:
        problems.append("an object carries an unregistered kind")
    for provider in model["providers"]:
        if provider["owner"].startswith(OWN_PREFIX) and not provider["discovered"]:
            problems.append(f"a derived artifact is declared as a provider: {provider['owner']}")
    if not model["counters"]["ckos_discovered"]:
        problems.append("no object was discovered, so identity is unmeasured")
    for record in model["goals"] + model["invariants"]:
        if not record["record_id"]:
            problems.append("a discovered subject carries no constitutional identity")
    return problems


def model_ckos(model: dict) -> list[dict]:
    """The measured objects, as identity-bearing records.

    The model persists the measured planes rather than every object, so identity is
    re-checked over what the model actually carries.
    """
    return [
        {"cko_id": record["cko_id"], "kind": kind, "record_id": record["record_id"]}
        for kind, plane in (
            (model["goal_kind"], model["goals"]),
            (model["invariant_kind"], model["invariants"]),
            (model["stage_kind"], model["stages"]),
        )
        for record in plane
    ]


def check_semantic_identity(document: dict) -> list[str]:
    """Constitutional identity must be immutable, singular, and free of mutable inputs."""
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
    if not model["counters"]["relationship_ckos_discovered"]:
        problems.append("no relationship object was discovered, so relationships are not first-class")
    originating = {str(entry["id"]) for entry in document["discovery_classes"] if entry.get(CLASS_MAY_ORIGINATE)}
    for entry in model["relationships"][:200]:
        if str(entry["provenance"].get("discovery_class") or "") not in originating:
            problems.append(f"relationship not traced to an originating provider: {entry['cko_id']}")
    return problems


def check_knowledge_once(document: dict) -> list[str]:
    """Nothing discovered may be restated in the declaration."""
    model = measure(document)
    problems: list[str] = []
    if model["counters"]["declaration_names_a_goal"]:
        problems.append("the declaration restates a discovered goal identifier")
    if model["counters"]["declaration_names_an_invariant"]:
        problems.append("the declaration restates a discovered invariant identifier")
    declaration_text = DECLARATION.read_text(encoding="utf-8")
    for record in model["stages"]:
        if record["record_id"] in declaration_text:
            problems.append(f"the declaration restates a consumed stage: {record['record_id']}")
    if not model["counters"]["goals_discovered"]:
        problems.append("no goal was discovered")
    if not model["counters"]["invariants_discovered"]:
        problems.append("no invariant was discovered")
    if not model["counters"]["stages_consumed"]:
        problems.append("no stage was consumed")
    return problems


def check_record_immutability(document: dict) -> list[str]:
    model = measure(document)
    problems = [f"a protected record is in the write set: {p}" for p in model["immutability"]["intersections"]]
    problems += [f"writes outside its home: {p}" for p in model["immutability"]["outside_home"]]
    problems += [f"writes inside a forbidden prefix: {p}" for p in model["immutability"]["forbidden_trespass"]]
    for entry in model["record_set"]:
        if not entry["located"]:
            problems.append(f"a protected record does not resolve: {entry['id']}")
        elif not entry["anchor_present"]:
            problems.append(f"a protected record's anchor is absent: {entry['id']}")
    if not model["record_set"]:
        problems.append("no protected record is declared, so immutability is unmeasured")
    return problems


def check_reduction_measured(document: dict) -> list[str]:
    """Future engineering reduction must be measured, not asserted."""
    model = measure(document)
    problems: list[str] = []
    if not model["reduction"]:
        problems.append("no reduction measure is declared")
    for entry in model["reduction"]:
        if not entry["located"]:
            problems.append(f"{entry['id']}: the reduction owner does not resolve")
        if not entry["achieved"]:
            problems.append(
                f"{entry['id']}: {entry['measure']} = {entry['value']}, expected {entry['comparator']} {entry['expect']}"
            )
    for entry in model["extractions"]:
        if not entry["measured"]:
            problems.append(f"{entry['id']}: extracted knowledge is unmeasured")
    for entry in model["elevations"]:
        if not entry["evidenced"]:
            problems.append(f"{entry['id']}: an elevation carries no evidence, lineage, replay, certification or authority")
    return problems


def check_bounds_tight(document: dict) -> list[str]:
    """A disclosed divergence may not be inflated to hide a future regression."""
    return list(measure(document)["bounds_slack"])


GUARDS = {
    "check-declaration": check_declaration,
    "check-no-enumeration": check_no_enumeration,
    "check-no-privileged-logic": check_no_privileged_logic,
    "check-reuse-before-create": check_reuse_before_create,
    "check-write-scope": check_write_scope,
    "check-determinism": check_determinism,
    "check-implementation-independence": check_implementation_independence,
    "check-open-world": check_open_world,
    "check-no-parallel-authority": check_no_parallel_authority,
    "check-goal-plane-executable": check_goal_plane_executable,
    "check-invariant-coverage": check_invariant_coverage,
    "check-cko-identity": check_cko_identity,
    "check-semantic-identity": check_semantic_identity,
    "check-knowledge-once": check_knowledge_once,
    "check-record-immutability": check_record_immutability,
    "check-reduction-measured": check_reduction_measured,
    "check-bounds-tight": check_bounds_tight,
}


# --------------------------------------------------------------------------- entry point


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=True, description=__doc__.splitlines()[0])
    parser.add_argument("--render", action="store_true", help="regenerate the registers")
    parser.add_argument("--gate", action="store_true", help="fail-closed autonomous engineering gate")
    parser.add_argument(
        "--engineer",
        metavar="GOAL",
        help="derive the complete engineering plan for an arbitrary goal (writes nothing)",
    )
    parser.add_argument(
        "--subject",
        metavar="PATH",
        default="",
        help="the located subject an arbitrary goal is about",
    )
    parser.add_argument("--quiet", action="store_true")
    for name in GUARDS:
        parser.add_argument(f"--{name}", action="store_true")
    args = parser.parse_args(argv)

    try:
        document = load_declaration()
    except FailClosed as exc:
        print(f"ACEE-000001 ABORT: {exc}", file=sys.stderr)
        return 2

    selected = [name for name in GUARDS if getattr(args, name.replace("-", "_"))]
    if selected:
        failed = False
        for name in selected:
            try:
                problems = GUARDS[name](document)
            except FailClosed as exc:
                print(f"ACEE-000001 ABORT: {exc}", file=sys.stderr)
                return 2
            if problems:
                failed = True
                print(f"ACEE-000001 {name}: FAIL ({len(problems)})", file=sys.stderr)
                for problem in problems[:40]:
                    print(f"  - {problem}", file=sys.stderr)
            else:
                print(f"ACEE-000001 {name}: PASS")
        return 1 if failed else 0

    try:
        model = measure(document)
    except FailClosed as exc:
        print(f"ACEE-000001 ABORT: {exc}", file=sys.stderr)
        return 2

    if args.engineer is not None:
        # Goal-directed autonomous engineering for a goal nobody declared. Writes nothing,
        # invokes nothing, and is a pure function of the goal text and the consumed graph.
        by_cko = {
            record["cko_id"]: {
                "record_id": record["record_id"],
                "name": record["stage"],
                "attributes": {
                    "owner": record["owner"],
                    "authority_owner": record["authority_owner"],
                    "group": record["group"],
                },
            }
            for record in model["stages"]
        }
        derived = plan(args.engineer, args.subject, model["order"], by_cko, model["stage_graph_digest"])
        facts = {
            "subject_present": bool(args.subject),
            "subject_located": exists(args.subject),
            "owner_located": exists(args.subject),
            "authority_located": exists(args.subject),
            "plan_complete": bool(derived["steps_total"]) and derived["steps_unbound"] == 0,
            "plan_deterministic": True,
            "requires_new_infrastructure": derived["steps_requiring_new_infrastructure"] > 0,
            "subject_is_self": args.subject.startswith(OWN_PREFIX),
            "fully_reused": bool(derived["steps_total"]) and derived["steps_reused"] == derived["steps_total"],
            "obligations_unmet": False,
        }
        disposition, rule_id, rationale = dispose(document, _plane_id(document, MEASURED_BY_OBLIGATIONS), facts)
        derived["disposition"] = disposition
        derived["disposition_rule"] = rule_id
        derived["disposition_rationale"] = rationale
        print(json.dumps(derived, indent=2, sort_keys=True, ensure_ascii=False))
        return 0

    written = write_registers(model)
    counters = model["counters"]
    if not args.quiet:
        print(
            f"ACEE-000001: {model['determination']} "
            f"| goals={counters['goals_discovered']} "
            f"| invariants={counters['invariants_discovered']}({counters['invariants_unsatisfied']}unsat) "
            f"| stages={counters['stages_consumed']}consumed "
            f"| ckos={counters['ckos_discovered']} relations={counters['relations_discovered']} "
            f"| plans={counters['goal_plans_derived']} unbound={counters['goal_plan_steps_unbound']} "
            f"| newinfra={counters['goal_steps_requiring_new_infrastructure']} "
            f"| create={counters['invariants_dispositioned_create']}inv/{counters['capabilities_created']}cap "
            f"| privileged={counters['privileged_branches']} "
            f"| axes={len(model['expansion_axes']) - counters['expansion_axes_unbound']}/{len(model['expansion_axes'])} "
            f"| reduction={len(model['reduction']) - counters['reductions_unachieved']}/{len(model['reduction'])} "
            f"| criteria={sum(1 for v in model['validations'] if v['satisfied'])}/{len(model['validations'])} "
            f"| exit={sum(1 for d in model['exit_dimensions'] if d['ready'])}/{len(model['exit_dimensions'])} "
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
